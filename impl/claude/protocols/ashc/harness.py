"""
ASHC VoidHarness: Isolated LLM Execution Environment

Executes Claude CLI in void directories (no CLAUDE.md) to get
clean LLM calls without kgents context injection.

This enables testing Bayesian stopping with genuinely probabilistic behavior.

> "The proof is not formal—it's empirical. Now we prove it with real LLM calls."

Heritage: Phase 4 of ASHC - building on verify.py subprocess patterns
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# =============================================================================
# Configuration Types
# =============================================================================


@dataclass
class VoidHarnessConfig:
    """Configuration for VoidHarness execution environment."""

    model: str = "claude-sonnet-4-20250514"
    timeout_seconds: float = 120.0
    max_concurrent: int = 3
    max_output_tokens: int = 4096
    void_prefix: str = "/tmp/ashc-void"

    # Output parsing
    require_code_fence: bool = False  # If True, require ```python blocks

    # Budget tracking
    warn_at_tokens: int = 50_000  # Warn when approaching budget
    max_tokens: int = 100_000  # Hard cap on total tokens


@dataclass
class TokenBudget:
    """Track and limit token usage across harness lifetime."""

    max_tokens: int = 100_000
    warn_at_tokens: int = 50_000
    used_tokens: int = 0

    @property
    def remaining(self) -> int:
        """Remaining token budget."""
        return max(0, self.max_tokens - self.used_tokens)

    @property
    def exhausted(self) -> bool:
        """Is budget exhausted?"""
        return self.used_tokens >= self.max_tokens

    @property
    def warning_threshold_reached(self) -> bool:
        """Should we warn about approaching limit?"""
        return self.used_tokens >= self.warn_at_tokens

    def consume(self, tokens: int) -> None:
        """
        Consume tokens from budget.

        Raises RuntimeError if budget would be exceeded.
        """
        if self.used_tokens + tokens > self.max_tokens:
            raise RuntimeError(
                f"Token budget exhausted: {self.used_tokens + tokens}/{self.max_tokens}"
            )
        self.used_tokens += tokens


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class GenerationResult:
    """
    Result from a single LLM generation.

    Captures the generated code, metadata, and any errors.
    """

    code: str
    prompt_used: str
    duration_ms: float
    token_estimate: int  # Rough estimate (~4 chars per token)
    raw_output: str
    success: bool
    error: str | None = None
    void_id: str = ""  # Identifier for the void directory used
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_code(self) -> bool:
        """Did generation produce any code?"""
        return bool(self.code.strip())


@dataclass
class SubprocessResult:
    """Result of a subprocess execution."""

    stdout: str
    stderr: str
    returncode: int
    duration_ms: float


# =============================================================================
# VoidHarness Class
# =============================================================================


class VoidHarness:
    """
    Isolated Claude CLI execution environment.

    Creates void directories with no CLAUDE.md to get clean LLM calls
    without kgents context injection. This is essential for testing
    the Bayesian stopping infrastructure with genuine probabilistic behavior.

    Usage:
        harness = VoidHarness()
        code = await harness.generate("def add(a, b): return a + b")

        # Or with full metadata
        result = await harness.generate_detailed("def add(a, b): ...")
        print(f"Took {result.duration_ms}ms, ~{result.token_estimate} tokens")

        # Wire to EvidenceCompiler
        compiler = EvidenceCompiler(generate_fn=harness.generate)
    """

    def __init__(
        self,
        config: VoidHarnessConfig | None = None,
        budget: TokenBudget | None = None,
    ):
        """
        Initialize the harness.

        Args:
            config: Configuration for CLI execution
            budget: Token budget for tracking/limiting usage
        """
        self._config = config or VoidHarnessConfig()
        self._budget = budget or TokenBudget(
            max_tokens=self._config.max_tokens,
            warn_at_tokens=self._config.warn_at_tokens,
        )
        self._semaphore = asyncio.Semaphore(self._config.max_concurrent)
        self._generation_count = 0

    # =========================================================================
    # Public API
    # =========================================================================

    async def generate(self, spec: str) -> str:
        """
        Generate implementation from spec.

        This is the primary interface for EvidenceCompiler.generate_fn.
        Returns just the code string, raises on failure.

        Args:
            spec: The specification to implement

        Returns:
            Generated Python code

        Raises:
            RuntimeError: If generation fails or budget exhausted
        """
        result = await self.generate_detailed(spec)
        if not result.success:
            raise RuntimeError(f"Generation failed: {result.error}")
        return result.code

    async def generate_detailed(self, spec: str) -> GenerationResult:
        """
        Generate implementation with full metadata.

        Returns GenerationResult with code, timing, tokens, and error info.

        Args:
            spec: The specification to implement

        Returns:
            GenerationResult with all metadata
        """
        # Check budget before acquiring semaphore
        if self._budget.exhausted:
            return GenerationResult(
                code="",
                prompt_used="",
                duration_ms=0,
                token_estimate=0,
                raw_output="",
                success=False,
                error="Token budget exhausted",
            )

        async with self._semaphore:
            self._generation_count += 1
            return await self._execute_in_void(spec)

    async def generate_n(
        self,
        spec: str,
        n: int,
    ) -> list[GenerationResult | BaseException]:
        """
        Generate n variations concurrently.

        Useful for gathering evidence across multiple generations.

        Args:
            spec: The specification to implement
            n: Number of variations to generate

        Returns:
            List of GenerationResults (or exceptions if any failed)
        """
        tasks = [self.generate_detailed(spec) for _ in range(n)]
        return await asyncio.gather(*tasks, return_exceptions=True)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def generation_count(self) -> int:
        """Total number of generations performed."""
        return self._generation_count

    @property
    def tokens_used(self) -> int:
        """Total tokens consumed so far."""
        return self._budget.used_tokens

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining in budget."""
        return self._budget.remaining

    @property
    def budget_exhausted(self) -> bool:
        """Is the token budget exhausted?"""
        return self._budget.exhausted

    # =========================================================================
    # Internal Implementation
    # =========================================================================

    async def _execute_in_void(self, spec: str) -> GenerationResult:
        """Execute Claude CLI in a void directory."""
        start = time.monotonic()
        void_id = str(uuid.uuid4())[:8]
        void_dir = Path(f"{self._config.void_prefix}-{void_id}")

        try:
            # Create void directory (empty, no CLAUDE.md)
            void_dir.mkdir(parents=True, exist_ok=True)

            # Write spec file (Claude can read if needed)
            spec_file = void_dir / "spec.md"
            spec_file.write_text(spec)

            # Build prompt
            prompt = self._build_prompt(spec)

            # Execute Claude CLI
            result = await self._run_claude_cli(void_dir, prompt)

            duration_ms = (time.monotonic() - start) * 1000

            # Parse output to extract code
            code = self._extract_code(result.stdout)

            # Estimate tokens (rough: ~4 chars per token)
            token_estimate = (len(prompt) + len(result.stdout)) // 4

            # Track token usage
            try:
                self._budget.consume(token_estimate)
            except RuntimeError as e:
                return GenerationResult(
                    code=code,
                    prompt_used=prompt,
                    duration_ms=duration_ms,
                    token_estimate=token_estimate,
                    raw_output=result.stdout,
                    success=False,
                    error=str(e),
                    void_id=void_id,
                )

            # Determine success
            success = result.returncode == 0 and bool(code.strip())
            error = None
            if result.returncode != 0:
                error = f"CLI returned {result.returncode}: {result.stderr}"
            elif not code.strip():
                error = "No code extracted from output"

            return GenerationResult(
                code=code,
                prompt_used=prompt,
                duration_ms=duration_ms,
                token_estimate=token_estimate,
                raw_output=result.stdout,
                success=success,
                error=error,
                void_id=void_id,
            )

        except asyncio.TimeoutError:
            duration_ms = (time.monotonic() - start) * 1000
            return GenerationResult(
                code="",
                prompt_used=self._build_prompt(spec),
                duration_ms=duration_ms,
                token_estimate=0,
                raw_output="",
                success=False,
                error=f"Timeout after {self._config.timeout_seconds}s",
                void_id=void_id,
            )

        except Exception as e:
            duration_ms = (time.monotonic() - start) * 1000
            return GenerationResult(
                code="",
                prompt_used=self._build_prompt(spec),
                duration_ms=duration_ms,
                token_estimate=0,
                raw_output="",
                success=False,
                error=f"Unexpected error: {e}",
                void_id=void_id,
            )

        finally:
            # Cleanup void directory
            if void_dir.exists():
                shutil.rmtree(void_dir, ignore_errors=True)

    async def _run_claude_cli(
        self,
        cwd: Path,
        prompt: str,
    ) -> SubprocessResult:
        """
        Run Claude CLI in the void directory.

        Uses -p for print mode (non-interactive).
        Running from void directory prevents CLAUDE.md context injection.
        """
        start = time.monotonic()

        cmd = [
            "claude",
            "-p",  # Print mode (non-interactive)
            "--output-format",
            "text",  # Plain text output
            "--model",
            self._config.model,
            prompt,
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(cwd),  # Run from void directory
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(),
                timeout=self._config.timeout_seconds,
            )

            duration_ms = (time.monotonic() - start) * 1000

            return SubprocessResult(
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                returncode=proc.returncode or 0,
                duration_ms=duration_ms,
            )

        except asyncio.TimeoutError:
            # Kill the process if it times out
            if proc is not None:
                proc.kill()
                await proc.wait()
            raise

    def _build_prompt(self, spec: str) -> str:
        """
        Build the generation prompt.

        The prompt is self-contained since we're in a void directory
        with no CLAUDE.md context.
        """
        return f"""You are a Python code generator. Generate a complete, working implementation for the following specification.

RULES:
1. Output ONLY the Python code - no explanations, no markdown
2. Include proper type hints
3. Include docstrings
4. Make it production-ready and correct
5. Do not include test code unless the spec asks for it

SPECIFICATION:
{spec}

PYTHON CODE:
```python
"""

    def _extract_code(self, output: str) -> str:
        """
        Extract code from Claude's output.

        Tries multiple strategies:
        1. Find ```python fenced block
        2. Find any ``` fenced block
        3. Look for def/class/import statements
        4. Return raw output as fallback
        """
        # Strategy 1: Find ```python block
        python_match = re.search(r"```python\s*(.*?)```", output, re.DOTALL)
        if python_match:
            return python_match.group(1).strip()

        # Strategy 2: Find any ``` block
        any_fence_match = re.search(r"```\s*(.*?)```", output, re.DOTALL)
        if any_fence_match:
            return any_fence_match.group(1).strip()

        # Strategy 3: Find code-like content
        lines = output.strip().split("\n")
        code_lines: list[str] = []
        in_code = False

        for line in lines:
            stripped = line.strip()
            # Start of code
            if stripped.startswith(("def ", "class ", "import ", "from ", "@", "async def ")):
                in_code = True
            # Continue collecting if we're in code
            if in_code:
                code_lines.append(line)

        if code_lines:
            return "\n".join(code_lines).strip()

        # Strategy 4: If require_code_fence is False, return raw output
        if not self._config.require_code_fence:
            return output.strip()

        return ""

    # =========================================================================
    # Class Methods
    # =========================================================================

    @classmethod
    def is_available(cls) -> bool:
        """Check if Claude CLI is available on the system."""
        return shutil.which("claude") is not None


# =============================================================================
# Convenience Functions
# =============================================================================


async def generate_from_spec(
    spec: str,
    config: VoidHarnessConfig | None = None,
) -> str:
    """
    Quick generation from spec.

    Args:
        spec: The specification to implement
        config: Optional harness configuration

    Returns:
        Generated Python code

    Raises:
        RuntimeError: If generation fails
    """
    harness = VoidHarness(config)
    return await harness.generate(spec)


async def generate_n_from_spec(
    spec: str,
    n: int,
    config: VoidHarnessConfig | None = None,
) -> list[GenerationResult | BaseException]:
    """
    Generate n variations from spec.

    Args:
        spec: The specification to implement
        n: Number of variations to generate
        config: Optional harness configuration

    Returns:
        List of GenerationResults
    """
    harness = VoidHarness(config)
    return await harness.generate_n(spec, n)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core classes
    "VoidHarness",
    "VoidHarnessConfig",
    "TokenBudget",
    # Result types
    "GenerationResult",
    "SubprocessResult",
    # Convenience functions
    "generate_from_spec",
    "generate_n_from_spec",
]
