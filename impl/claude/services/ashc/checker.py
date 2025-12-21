"""
Proof Checker Bridge: The Gatekeeper.

This module bridges to external proof checkers (Dafny, Lean4, Verus).
The proof checker is the source of truth—LLM hallucinations don't matter
because invalid proofs are mechanically rejected.

Heritage: Kleppmann (§12)
    "LLM hallucinations don't matter for proofs because proof checkers
    reject invalid proofs."

The Three Gatekeepers:
    - **Dafny**: Imperative proofs (loops, arrays, ADTs). Uses Z3. Best
      for verifying algorithms with pre/postconditions.
    - **Lean4**: Mathematical proofs. Dependently typed. Best for
      theorem-heavy domains (category theory, formal math).
    - **Verus**: Rust verification. Linear types match ownership model.
      Best for systems code with memory safety proofs.

Teaching:
    gotcha: Dafny outputs to stderr even on success. Parse exit code,
            not output presence, to determine success.
    gotcha: Always clean up temp files—even on exceptions. Use try/finally.
    gotcha: Set process timeouts to prevent zombie processes.
    gotcha: Z3 timeouts are unreliable. Use resource limits instead of
            time limits for Dafny/Verus. Timeouts may not be respected.
    gotcha: Lean4 requires `lake env lean` for project files, not bare
            `lean`. The bare command won't find project dependencies.
    gotcha: Verus `verus!` blocks inside `impl` sections are silently
            ignored. Always wrap the entire `impl` block.
    gotcha: Platform non-determinism: Same proof may verify on macOS but
            timeout on Linux due to Z3 behavior differences.

AGENTESE:
    concept.ashc.prove → Attempt to discharge obligation (uses checker)
"""

from __future__ import annotations

import asyncio
import os
import re
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .contracts import CheckerResult

# =============================================================================
# Checker Protocol
# =============================================================================


class CheckerUnavailable(Exception):
    """
    Raised when a proof checker is not installed or not accessible.

    This allows graceful degradation—the system can fall back to
    evidence-only mode when checkers aren't available.
    """

    def __init__(self, checker_name: str, message: str):
        self.checker_name = checker_name
        super().__init__(f"{checker_name}: {message}")


class CheckerError(Exception):
    """
    Raised when a proof checker encounters an unexpected error.

    This is distinct from a proof failing to verify—that's a normal
    CheckerResult with success=False.
    """

    def __init__(self, checker_name: str, message: str, output: str = ""):
        self.checker_name = checker_name
        self.output = output
        super().__init__(f"{checker_name}: {message}")


@runtime_checkable
class ProofChecker(Protocol):
    """
    Protocol for proof checker adapters.

    Each checker must:
    1. Accept proof source as string
    2. Return verification result
    3. Handle timeouts gracefully (no zombie processes)

    Teaching:
        gotcha: Protocol > ABC for interfaces. Enables duck typing without
                inheritance coupling. See meta.md: "Protocol > ABC"
    """

    @property
    def name(self) -> str:
        """Checker identifier (e.g., 'dafny', 'lean4')."""
        ...

    @property
    def is_available(self) -> bool:
        """True if the checker is installed and accessible."""
        ...

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Verify a proof.

        Args:
            proof_source: The proof text (Dafny/Lean4/Verus syntax)
            timeout_ms: Maximum time to wait for verification

        Returns:
            CheckerResult with success/failure and diagnostics.

        Raises:
            CheckerUnavailable: If the checker is not installed
            CheckerError: If an unexpected error occurs during verification
        """
        ...


# =============================================================================
# Dafny Checker Implementation
# =============================================================================


class DafnyChecker:
    """
    Dafny proof checker via subprocess.

    Requires: dotnet tool install --global dafny

    Dafny is chosen as the first checker because:
    - Simple installation (dotnet tool)
    - Imperative-ish syntax (easier for LLMs)
    - Clear error messages
    - Lower learning curve than Lean4

    Error Output Understanding:
        Dafny error format includes:
        - BP5003: Postcondition might not hold
        - BP5001: Precondition might not hold
        - Error cascade: First error is key; subsequent often red herrings

    Resource Management:
        - Dafny bundles Z3 (no separate install)
        - Default verification runs continuously in IDE
        - --resource-limit more reliable than --verification-time-limit
        - Z3 may pursue fruitless reasoning if too many facts in scope

    Teaching:
        gotcha: Dafny outputs to stderr even on success. Parse exit code,
                not output presence, to determine success.
        gotcha: Use asyncio.create_subprocess_exec, not subprocess.run,
                to avoid blocking the event loop.
        gotcha: Always unlink temp files in finally block—exceptions happen.
        gotcha: Noisy error cascades—first error message is the key one.
        gotcha: --verification-time-limit not always respected; prefer
                --resource-limit for reliable bounded verification.

    Example:
        >>> checker = DafnyChecker()
        >>> if checker.is_available:
        ...     result = await checker.check("lemma Trivial() ensures true {}")
        ...     assert result.success
    """

    def __init__(
        self,
        dafny_path: str | None = None,
        *,
        verify_on_init: bool = True,
    ):
        """
        Initialize the Dafny checker.

        Args:
            dafny_path: Path to dafny executable. Defaults to "dafny" (on PATH).
            verify_on_init: If True, verify installation on init (default).
                           Set to False for lazy verification.
        """
        self._dafny_path = dafny_path or "dafny"
        self._available: bool | None = None

        if verify_on_init:
            self._verify_installation()

    @property
    def name(self) -> str:
        """Checker identifier."""
        return "dafny"

    @property
    def is_available(self) -> bool:
        """
        True if Dafny is installed and accessible.

        Caches the result to avoid repeated subprocess calls.
        """
        if self._available is None:
            try:
                self._verify_installation()
            except CheckerUnavailable:
                pass  # _available is set by _verify_installation
        return self._available or False

    def _verify_installation(self) -> None:
        """
        Check that Dafny is installed and accessible.

        Raises:
            CheckerUnavailable: If Dafny is not found or not responding.
        """
        import subprocess

        try:
            result = subprocess.run(
                [self._dafny_path, "--version"],
                capture_output=True,
                timeout=10,  # Version check shouldn't take long
            )
            if result.returncode != 0:
                self._available = False
                raise CheckerUnavailable(
                    "dafny",
                    f"Dafny returned exit code {result.returncode}",
                )
            self._available = True
        except FileNotFoundError:
            self._available = False
            raise CheckerUnavailable(
                "dafny",
                "Dafny not found. Install: dotnet tool install --global dafny",
            )
        except subprocess.TimeoutExpired:
            self._available = False
            raise CheckerUnavailable(
                "dafny",
                "Dafny timed out during version check",
            )

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Run Dafny verification on proof source.

        Args:
            proof_source: Dafny source code to verify
            timeout_ms: Maximum verification time in milliseconds

        Returns:
            CheckerResult with verification outcome

        Raises:
            CheckerUnavailable: If Dafny is not installed
            CheckerError: If an unexpected error occurs
        """
        if not self.is_available:
            raise CheckerUnavailable(
                "dafny",
                "Dafny not available. Install: dotnet tool install --global dafny",
            )

        # Write to temp file (Dafny requires file input)
        temp_path: str | None = None
        try:
            # Create temp file
            fd, temp_path = tempfile.mkstemp(suffix=".dfy", prefix="ashc_proof_")
            os.write(fd, proof_source.encode("utf-8"))
            os.close(fd)

            # Run verification
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                self._dafny_path,
                "verify",
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_ms / 1000,
                )
            except asyncio.TimeoutError:
                # Kill the process to prevent zombies
                proc.kill()
                await proc.wait()  # Reap the zombie
                return CheckerResult(
                    success=False,
                    errors=("Verification timeout",),
                    warnings=(),
                    duration_ms=timeout_ms,
                )

            duration = int((time.monotonic() - start) * 1000)
            success = proc.returncode == 0

            # Parse Dafny output
            output = (stdout + stderr).decode("utf-8", errors="replace")
            errors = self._parse_errors(output)
            warnings = self._parse_warnings(output)

            return CheckerResult(
                success=success,
                errors=tuple(errors),
                warnings=tuple(warnings),
                duration_ms=duration,
            )

        except OSError as e:
            raise CheckerError(
                "dafny",
                f"Failed to create temp file: {e}",
            )

        finally:
            # Always clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Best effort cleanup

    def _parse_errors(self, output: str) -> list[str]:
        """
        Extract error messages from Dafny output.

        Dafny error format varies, but typically includes:
        - "Error:" or "error:" followed by message
        - File path and line number

        We extract the message part for actionable feedback.
        """
        errors: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            # Match various error patterns
            if "error:" in line_lower or "error BP" in line:
                # Clean up the error message
                cleaned = line.strip()
                if cleaned and cleaned not in errors:
                    errors.append(cleaned)
            elif "assertion might not hold" in line_lower:
                errors.append(line.strip())
            elif "postcondition might not hold" in line_lower:
                errors.append(line.strip())
            elif "precondition might not hold" in line_lower:
                errors.append(line.strip())

        return errors

    def _parse_warnings(self, output: str) -> list[str]:
        """Extract warning messages from Dafny output."""
        warnings: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            if "warning:" in line_lower or "warning BP" in line:
                cleaned = line.strip()
                if cleaned and cleaned not in warnings:
                    warnings.append(cleaned)

        return warnings


# =============================================================================
# Mock Checker for Testing
# =============================================================================


class MockChecker:
    """
    Mock proof checker for testing without external dependencies.

    This allows testing the proof search pipeline without requiring
    Dafny/Lean4 to be installed.

    Teaching:
        gotcha: Use DI pattern (inject checker) rather than mocking.
                This mock checker IS the test double.
    """

    def __init__(
        self,
        *,
        default_success: bool = True,
        latency_ms: int = 100,
    ):
        """
        Initialize mock checker.

        Args:
            default_success: Default verification result
            latency_ms: Simulated verification latency
        """
        self._default_success = default_success
        self._latency_ms = latency_ms
        self._call_count = 0
        self._last_proof: str = ""

        # Patterns that always succeed/fail (for testing specific cases)
        self._success_patterns: list[re.Pattern[str]] = []
        self._failure_patterns: list[re.Pattern[str]] = []

    @property
    def name(self) -> str:
        """Checker identifier."""
        return "mock"

    @property
    def is_available(self) -> bool:
        """Mock is always available."""
        return True

    @property
    def call_count(self) -> int:
        """Number of check() calls made."""
        return self._call_count

    @property
    def last_proof(self) -> str:
        """The last proof source that was checked."""
        return self._last_proof

    def always_succeed_on(self, pattern: str) -> "MockChecker":
        """Add pattern that always succeeds."""
        self._success_patterns.append(re.compile(pattern, re.IGNORECASE))
        return self

    def always_fail_on(self, pattern: str) -> "MockChecker":
        """Add pattern that always fails."""
        self._failure_patterns.append(re.compile(pattern, re.IGNORECASE))
        return self

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Mock verification that returns configurable results.

        Checks patterns first, then falls back to default.
        """
        self._call_count += 1
        self._last_proof = proof_source

        # Simulate latency
        await asyncio.sleep(self._latency_ms / 1000)

        # Check failure patterns first
        for pattern in self._failure_patterns:
            if pattern.search(proof_source):
                return CheckerResult(
                    success=False,
                    errors=("Mock: proof matches failure pattern",),
                    duration_ms=self._latency_ms,
                )

        # Check success patterns
        for pattern in self._success_patterns:
            if pattern.search(proof_source):
                return CheckerResult(
                    success=True,
                    errors=(),
                    duration_ms=self._latency_ms,
                )

        # Fall back to default
        if self._default_success:
            return CheckerResult(
                success=True,
                errors=(),
                duration_ms=self._latency_ms,
            )
        else:
            return CheckerResult(
                success=False,
                errors=("Mock: default failure",),
                duration_ms=self._latency_ms,
            )


# =============================================================================
# Checker Registry (Future: Multiple Checker Support)
# =============================================================================


@dataclass
class CheckerRegistry:
    """
    Registry of available proof checkers.

    Allows the proof search to try multiple checkers or select
    the best checker for a given obligation.

    Teaching:
        gotcha: Lazy initialization—don't instantiate checkers until needed.
                This avoids startup cost when checkers aren't used.
    """

    _checkers: dict[str, type[ProofChecker]] = field(default_factory=dict)
    _instances: dict[str, ProofChecker] = field(default_factory=dict)

    def register(self, name: str, checker_class: type[ProofChecker]) -> None:
        """Register a checker class."""
        self._checkers[name] = checker_class

    def get(self, name: str) -> ProofChecker:
        """
        Get a checker instance by name.

        Instantiates on first access (lazy).

        Raises:
            KeyError: If checker not registered
        """
        if name not in self._instances:
            if name not in self._checkers:
                raise KeyError(f"Unknown checker: {name}")
            self._instances[name] = self._checkers[name]()
        return self._instances[name]

    def available_checkers(self) -> list[str]:
        """Return names of all available (installed) checkers."""
        available = []
        for name in self._checkers:
            try:
                checker = self.get(name)
                if checker.is_available:
                    available.append(name)
            except (CheckerUnavailable, Exception):
                pass
        return available


# =============================================================================
# Lean4 Checker Implementation
# =============================================================================


class Lean4Checker:
    """
    Lean4 proof checker via subprocess.

    Requires: elan (Lean version manager)
    Install: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

    Lean4 is the future of formal verification:
    - Dependent types enable expressive specifications
    - Tactics language enables interactive proof development
    - Mathlib provides extensive library of proven theorems
    - Active community with momentum

    Installation Notes:
        - AVOID Homebrew's lean formula (lags behind)
        - Use elan for toolchain management (like rustup)
        - Toolchains install to ~/.elan/toolchains/
        - For mathlib, use `lake exe cache get` (20+ min build → seconds)

    Command-Line Understanding:
        - `lake env lean <file>`: Sets up project environment, finds imports
        - `lean <file>`: Bare compiler, may not find project dependencies
        - For standalone files without project: bare `lean` works
        - For project files: ALWAYS use `lake env lean`

    Error Patterns:
        - "error:" followed by message
        - "unsolved goals" for incomplete tactics
        - "type mismatch" for type errors
        - "unknown identifier" for unbound names

    Teaching:
        gotcha: Use 'lake env lean' not just 'lean' to get correct environment.
        gotcha: Proofs containing 'sorry' are incomplete—treat as FAILED.
        gotcha: Lean uses unicode (∀, →, ×); ensure UTF-8 encoding.
        gotcha: Exact toolchain matching required. Project and deps must use
                same Lean version or cache won't work.
        gotcha: Without mathlib cache, builds take 20+ minutes. Always use
                `lake exe cache get` when working with mathlib projects.

    Example:
        >>> checker = Lean4Checker()
        >>> if checker.is_available:
        ...     result = await checker.check("theorem trivial : ∀ x : Nat, x = x := fun _ => rfl")
        ...     assert result.success
    """

    def __init__(
        self,
        binary_path: str | None = None,
        *,
        verify_on_init: bool = True,
    ):
        """
        Initialize the Lean4 checker.

        Args:
            binary_path: Path to lean executable. Defaults to "lean" (on PATH).
            verify_on_init: If True, verify installation on init (default).
                           Set to False for lazy verification.
        """
        self._binary_path = binary_path or "lean"
        self._available: bool | None = None

        if verify_on_init:
            self._verify_installation()

    @property
    def name(self) -> str:
        """Checker identifier."""
        return "lean4"

    @property
    def is_available(self) -> bool:
        """
        True if Lean4 is installed and accessible.

        Caches the result to avoid repeated subprocess calls.
        """
        if self._available is None:
            try:
                self._verify_installation()
            except CheckerUnavailable:
                pass  # _available is set by _verify_installation
        return self._available or False

    def _verify_installation(self) -> None:
        """
        Check that Lean4 is installed and accessible.

        Raises:
            CheckerUnavailable: If Lean4 is not found or not responding.
        """
        import subprocess

        try:
            result = subprocess.run(
                [self._binary_path, "--version"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                self._available = False
                raise CheckerUnavailable(
                    "lean4",
                    f"Lean4 returned exit code {result.returncode}",
                )
            self._available = True
        except FileNotFoundError:
            self._available = False
            raise CheckerUnavailable(
                "lean4",
                "Lean4 not found. Install: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh",
            )
        except subprocess.TimeoutExpired:
            self._available = False
            raise CheckerUnavailable(
                "lean4",
                "Lean4 timed out during version check",
            )

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Run Lean4 verification on proof source.

        Args:
            proof_source: Lean4 source code to verify
            timeout_ms: Maximum verification time in milliseconds

        Returns:
            CheckerResult with verification outcome

        Raises:
            CheckerUnavailable: If Lean4 is not installed
            CheckerError: If an unexpected error occurs
        """
        if not self.is_available:
            raise CheckerUnavailable(
                "lean4",
                "Lean4 not available. Install: curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh",
            )

        # Write to temp file (Lean requires file input)
        temp_path: str | None = None
        try:
            # Create temp file with Lean template
            fd, temp_path = tempfile.mkstemp(suffix=".lean", prefix="ashc_proof_")
            content = f"-- Auto-generated by ASHC\n\n{proof_source}"
            os.write(fd, content.encode("utf-8"))
            os.close(fd)

            # Run verification
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_ms / 1000,
                )
            except asyncio.TimeoutError:
                # Kill the process to prevent zombies
                proc.kill()
                await proc.wait()
                return CheckerResult(
                    success=False,
                    errors=("Verification timeout",),
                    warnings=(),
                    duration_ms=timeout_ms,
                )

            duration = int((time.monotonic() - start) * 1000)
            output = (stdout + stderr).decode("utf-8", errors="replace")

            # Check for sorry (incomplete proof marker)
            has_sorry = "sorry" in proof_source.lower() or "'sorry'" in output.lower()

            # Parse exit code (0 = success, nonzero = failure)
            success = proc.returncode == 0 and not has_sorry

            errors: list[str] = self._parse_errors(output)
            warnings: list[str] = self._parse_warnings(output)

            # Add sorry warning if present
            if has_sorry and "sorry" not in " ".join(errors).lower():
                errors.append("Proof contains 'sorry' (incomplete)")

            return CheckerResult(
                success=success,
                errors=tuple(errors),
                warnings=tuple(warnings),
                duration_ms=duration,
            )

        except OSError as e:
            raise CheckerError(
                "lean4",
                f"Failed to create temp file: {e}",
            )

        finally:
            # Always clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Best effort cleanup

    def _parse_errors(self, output: str) -> list[str]:
        """
        Extract error messages from Lean4 output.

        Lean4 error format typically includes:
        - "error:" followed by message
        - "unsolved goals" for incomplete tactics
        - "type mismatch" for type errors
        """
        errors: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            if "error:" in line_lower:
                cleaned = line.strip()
                if cleaned and cleaned not in errors:
                    errors.append(cleaned)
            elif "unsolved goals" in line_lower:
                errors.append(line.strip())
            elif "type mismatch" in line_lower:
                errors.append(line.strip())
            elif "unknown identifier" in line_lower:
                errors.append(line.strip())

        return errors

    def _parse_warnings(self, output: str) -> list[str]:
        """Extract warning messages from Lean4 output."""
        warnings: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            if "warning:" in line_lower:
                cleaned = line.strip()
                if cleaned and cleaned not in warnings:
                    warnings.append(cleaned)

        return warnings


# =============================================================================
# Verus Checker Implementation
# =============================================================================


class VerusChecker:
    """
    Verus proof checker (Rust verification) via subprocess.

    Requires: verus binary from https://github.com/verus-lang/verus

    Verus verifies Rust code with ownership-aware reasoning:
    - Linear types match Rust's ownership model
    - Similar to Dafny but for systems code
    - Good for low-level proofs (memory safety, concurrency)

    Installation Notes:
        - Requires Rust toolchain (rustup)
        - Requires specific Z3 version (e.g., 4.12.5)
        - Use ./tools/get-z3.sh to install correct Z3 version
        - macOS: May need to run ./tools/remove-quarantine.sh

    Z3 Version Management:
        - Verus expects specific Z3 versions
        - Version mismatch: "Verus expects z3 version 'X', found 'Y'"
        - Use --no-solver-version-check to bypass (not recommended)

    Code Modes (Critical Understanding):
        - exec: Normal Rust code that compiles and runs
        - spec: Ghost code for specifications only (never compiled)
        - proof: Ghost code for proofs (never compiled)
        - ghost/tracked: Advanced linear type features

    Error Patterns:
        - "error:" or "error[EXXXX]" for compilation errors
        - "verification failed" for proof failures
        - "precondition not satisfied" for requires violations
        - "postcondition not satisfied" for ensures violations

    Teaching:
        gotcha: Verus requires Rust toolchain; may need rustup setup.
        gotcha: All verified code must be inside the verus! macro.
        gotcha: vstd imports must be explicit.
        gotcha: CRITICAL: verus! blocks inside `impl` sections are SILENTLY
                IGNORED. Always wrap the entire impl, not just methods.
        gotcha: Z3 timeouts are unreliable. May diverge regardless of limit.
        gotcha: cargo verus verify --error-format=json is broken (Issue #1572).
                Use direct verus invocation for structured error output.

    Example:
        >>> checker = VerusChecker()
        >>> if checker.is_available:
        ...     result = await checker.check("proof fn trivial() ensures true {}")
        ...     assert result.success
    """

    def __init__(
        self,
        binary_path: str | None = None,
        *,
        verify_on_init: bool = True,
    ):
        """
        Initialize the Verus checker.

        Args:
            binary_path: Path to verus executable. Defaults to "verus" (on PATH).
            verify_on_init: If True, verify installation on init (default).
                           Set to False for lazy verification.
        """
        self._binary_path = binary_path or "verus"
        self._available: bool | None = None

        if verify_on_init:
            self._verify_installation()

    @property
    def name(self) -> str:
        """Checker identifier."""
        return "verus"

    @property
    def is_available(self) -> bool:
        """
        True if Verus is installed and accessible.

        Caches the result to avoid repeated subprocess calls.
        """
        if self._available is None:
            try:
                self._verify_installation()
            except CheckerUnavailable:
                pass  # _available is set by _verify_installation
        return self._available or False

    def _verify_installation(self) -> None:
        """
        Check that Verus is installed and accessible.

        Raises:
            CheckerUnavailable: If Verus is not found or not responding.
        """
        import subprocess

        try:
            result = subprocess.run(
                [self._binary_path, "--version"],
                capture_output=True,
                timeout=10,
            )
            # Verus may return non-zero for --version in some versions
            # Check if we got any output that looks like version info
            output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
            if result.returncode != 0 and "verus" not in output.lower():
                self._available = False
                raise CheckerUnavailable(
                    "verus",
                    f"Verus returned exit code {result.returncode}",
                )
            self._available = True
        except FileNotFoundError:
            self._available = False
            raise CheckerUnavailable(
                "verus",
                "Verus not found. Install from: https://github.com/verus-lang/verus",
            )
        except subprocess.TimeoutExpired:
            self._available = False
            raise CheckerUnavailable(
                "verus",
                "Verus timed out during version check",
            )

    async def check(
        self,
        proof_source: str,
        timeout_ms: int = 30000,
    ) -> CheckerResult:
        """
        Run Verus verification on proof source.

        Args:
            proof_source: Verus/Rust source code to verify
            timeout_ms: Maximum verification time in milliseconds

        Returns:
            CheckerResult with verification outcome

        Raises:
            CheckerUnavailable: If Verus is not installed
            CheckerError: If an unexpected error occurs
        """
        if not self.is_available:
            raise CheckerUnavailable(
                "verus",
                "Verus not available. Install from: https://github.com/verus-lang/verus",
            )

        # Write to temp file (Verus requires file input)
        temp_path: str | None = None
        try:
            # Create temp file with Verus template
            fd, temp_path = tempfile.mkstemp(suffix=".rs", prefix="ashc_proof_")
            # Wrap in verus! macro if not already wrapped
            if "verus!" not in proof_source:
                content = f"""// Auto-generated by ASHC
use vstd::prelude::*;

verus! {{
    {proof_source}
}}
"""
            else:
                content = f"// Auto-generated by ASHC\nuse vstd::prelude::*;\n\n{proof_source}"

            os.write(fd, content.encode("utf-8"))
            os.close(fd)

            # Run verification
            start = time.monotonic()
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_ms / 1000,
                )
            except asyncio.TimeoutError:
                # Kill the process to prevent zombies
                proc.kill()
                await proc.wait()
                return CheckerResult(
                    success=False,
                    errors=("Verification timeout",),
                    warnings=(),
                    duration_ms=timeout_ms,
                )

            duration = int((time.monotonic() - start) * 1000)
            output = (stdout + stderr).decode("utf-8", errors="replace")

            # Parse exit code (0 = success, nonzero = failure)
            success = proc.returncode == 0

            errors = self._parse_errors(output)
            warnings = self._parse_warnings(output)

            return CheckerResult(
                success=success,
                errors=tuple(errors),
                warnings=tuple(warnings),
                duration_ms=duration,
            )

        except OSError as e:
            raise CheckerError(
                "verus",
                f"Failed to create temp file: {e}",
            )

        finally:
            # Always clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass  # Best effort cleanup

    def _parse_errors(self, output: str) -> list[str]:
        """
        Extract error messages from Verus output.

        Verus error format includes:
        - "error:" for compilation errors
        - "verification failed" for proof failures
        - "assertion failed" for runtime assertions
        - "precondition not satisfied" / "postcondition not satisfied"
        """
        errors: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            if "error:" in line_lower or "error[" in line_lower:
                cleaned = line.strip()
                if cleaned and cleaned not in errors:
                    errors.append(cleaned)
            elif "verification failed" in line_lower:
                errors.append(line.strip())
            elif "assertion failed" in line_lower:
                errors.append(line.strip())
            elif "precondition" in line_lower and ("not satisfied" in line_lower or "failed" in line_lower):
                errors.append(line.strip())
            elif "postcondition" in line_lower and ("not satisfied" in line_lower or "failed" in line_lower):
                errors.append(line.strip())

        return errors

    def _parse_warnings(self, output: str) -> list[str]:
        """Extract warning messages from Verus output."""
        warnings: list[str] = []

        for line in output.split("\n"):
            line_lower = line.lower()
            if "warning:" in line_lower or "warning[" in line_lower:
                cleaned = line.strip()
                if cleaned and cleaned not in warnings:
                    warnings.append(cleaned)

        return warnings


# =============================================================================
# Checker Registry
# =============================================================================


# Default registry with all checkers
_default_registry = CheckerRegistry()
_default_registry.register("dafny", DafnyChecker)
_default_registry.register("lean4", Lean4Checker)
_default_registry.register("verus", VerusChecker)
_default_registry.register("mock", MockChecker)


def get_checker(name: str = "dafny") -> ProofChecker:
    """
    Get a proof checker by name.

    Args:
        name: Checker name ("dafny", "mock", etc.)

    Returns:
        ProofChecker instance

    Raises:
        KeyError: If checker not registered
    """
    return _default_registry.get(name)


def available_checkers() -> list[str]:
    """Return names of all available proof checkers."""
    return _default_registry.available_checkers()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Exceptions
    "CheckerUnavailable",
    "CheckerError",
    # Protocol
    "ProofChecker",
    # Implementations
    "DafnyChecker",
    "Lean4Checker",
    "VerusChecker",
    "MockChecker",
    # Registry
    "CheckerRegistry",
    "get_checker",
    "available_checkers",
]
