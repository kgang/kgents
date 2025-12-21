"""
ASHC Verification Runners

Subprocess runners for pytest, mypy, and ruff verification.
Uses the same tools we use to verify our own work.

> "If these tools are good enough for us to verify our work,
>  they're good enough for ASHC to verify generated work."
"""

from __future__ import annotations

import asyncio
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# =============================================================================
# Report Types
# =============================================================================


@dataclass(frozen=True)
class TestReport:
    """Results from running pytest on generated code."""

    passed: int
    failed: int
    skipped: int
    errors: tuple[str, ...] = ()
    duration_ms: float = 0.0
    raw_output: str = ""

    @property
    def total(self) -> int:
        """Total number of tests."""
        return self.passed + self.failed + self.skipped

    @property
    def success(self) -> bool:
        """Did all tests pass?"""
        return self.failed == 0 and len(self.errors) == 0


@dataclass(frozen=True)
class TypeReport:
    """Results from running mypy on generated code."""

    passed: bool
    error_count: int
    errors: tuple[str, ...] = ()
    raw_output: str = ""


@dataclass(frozen=True)
class LintReport:
    """Results from running ruff on generated code."""

    passed: bool
    violation_count: int
    violations: tuple[str, ...] = ()
    raw_output: str = ""


# =============================================================================
# Subprocess Helpers
# =============================================================================


@dataclass
class SubprocessResult:
    """Result of a subprocess execution."""

    stdout: str
    stderr: str
    returncode: int
    duration_ms: float


async def run_subprocess(
    cmd: list[str],
    cwd: Path | None = None,
    timeout: float = 60.0,
    env: dict[str, str] | None = None,
) -> SubprocessResult:
    """
    Run a subprocess with timeout and output capture.

    Uses asyncio.create_subprocess_exec for async execution.
    """
    import time

    start = time.monotonic()

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd) if cwd else None,
            env=env,
        )

        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout,
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

        duration_ms = (time.monotonic() - start) * 1000
        return SubprocessResult(
            stdout="",
            stderr=f"Process timed out after {timeout}s",
            returncode=-1,
            duration_ms=duration_ms,
        )


# =============================================================================
# Verification Runners
# =============================================================================


async def run_pytest(
    code: str,
    test_code: str | None = None,
    timeout: float = 60.0,
) -> TestReport:
    """
    Run pytest on generated code.

    Args:
        code: The implementation code to test
        test_code: Optional test code. If not provided, uses code as-is.
        timeout: Maximum time to wait for pytest

    Returns:
        TestReport with pass/fail counts and errors
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Write the implementation
        impl_file = tmppath / "impl.py"
        impl_file.write_text(code)

        # Write the test file
        if test_code:
            test_file = tmppath / "test_impl.py"
            test_file.write_text(test_code)
        else:
            # If no test code, treat code as self-testing
            test_file = tmppath / "test_code.py"
            test_file.write_text(code)

        # Run pytest with verbose output for parsing
        result = await run_subprocess(
            ["python", "-m", "pytest", "-v", "--tb=short", str(tmppath)],
            cwd=tmppath,
            timeout=timeout,
        )

        # Parse pytest output
        return _parse_pytest_output(result)


def _parse_pytest_output(result: SubprocessResult) -> TestReport:
    """Parse pytest output into TestReport."""
    output = result.stdout + result.stderr

    # Pattern: "5 passed, 2 failed, 1 skipped"
    passed = 0
    failed = 0
    skipped = 0

    # Look for summary line
    summary_match = re.search(
        r"(\d+)\s+passed",
        output,
    )
    if summary_match:
        passed = int(summary_match.group(1))

    failed_match = re.search(r"(\d+)\s+failed", output)
    if failed_match:
        failed = int(failed_match.group(1))

    skipped_match = re.search(r"(\d+)\s+skipped", output)
    if skipped_match:
        skipped = int(skipped_match.group(1))

    # Extract error messages from FAILED lines
    errors: list[str] = []
    for line in output.split("\n"):
        if "FAILED" in line or "ERROR" in line:
            errors.append(line.strip())

    # Handle complete failure (syntax error, import error, etc.)
    if result.returncode != 0 and passed == 0 and failed == 0:
        # Check for collection errors
        if "error" in output.lower() or "Error" in output:
            errors.append(f"Collection/import error: returncode={result.returncode}")
            failed = 1

    return TestReport(
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=tuple(errors),
        duration_ms=result.duration_ms,
        raw_output=output,
    )


async def run_mypy(
    code: str,
    timeout: float = 30.0,
) -> TypeReport:
    """
    Run mypy on generated code.

    Args:
        code: The code to type-check
        timeout: Maximum time to wait for mypy

    Returns:
        TypeReport with error count and messages
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Write the code
        code_file = tmppath / "code.py"
        code_file.write_text(code)

        # Run mypy
        result = await run_subprocess(
            ["python", "-m", "mypy", "--no-error-summary", str(code_file)],
            cwd=tmppath,
            timeout=timeout,
        )

        return _parse_mypy_output(result)


def _parse_mypy_output(result: SubprocessResult) -> TypeReport:
    """Parse mypy output into TypeReport."""
    output = result.stdout + result.stderr

    # Count error lines (format: "file.py:line: error: message")
    errors: list[str] = []
    for line in output.split("\n"):
        line = line.strip()
        if ": error:" in line:
            errors.append(line)

    return TypeReport(
        passed=len(errors) == 0 and result.returncode == 0,
        error_count=len(errors),
        errors=tuple(errors),
        raw_output=output,
    )


async def run_ruff(
    code: str,
    timeout: float = 10.0,
) -> LintReport:
    """
    Run ruff on generated code.

    Args:
        code: The code to lint
        timeout: Maximum time to wait for ruff

    Returns:
        LintReport with violation count and messages
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Write the code
        code_file = tmppath / "code.py"
        code_file.write_text(code)

        # Run ruff check
        result = await run_subprocess(
            ["python", "-m", "ruff", "check", str(code_file)],
            cwd=tmppath,
            timeout=timeout,
        )

        return _parse_ruff_output(result)


def _parse_ruff_output(result: SubprocessResult) -> LintReport:
    """Parse ruff output into LintReport."""
    output = result.stdout + result.stderr

    # Count violation lines
    violations: list[str] = []
    for line in output.split("\n"):
        line = line.strip()
        # Old ruff format: code.py:1:1: E501 Line too long
        if re.match(r".*:\d+:\d+:\s+\w+", line):
            violations.append(line)
        # New ruff format: F401 [*] `os` imported but unused
        elif re.match(r"^[A-Z]\d{3}\s+", line):
            violations.append(line)

    # Also check for "Found N errors" in output
    found_match = re.search(r"Found\s+(\d+)\s+errors?", output)
    if found_match:
        violation_count = int(found_match.group(1))
    else:
        violation_count = len(violations)

    return LintReport(
        passed=violation_count == 0 and result.returncode == 0,
        violation_count=violation_count,
        violations=tuple(violations),
        raw_output=output,
    )


# =============================================================================
# Combined Verification
# =============================================================================


@dataclass(frozen=True)
class VerificationResult:
    """Combined results from all verification tools."""

    test_report: TestReport
    type_report: TypeReport
    lint_report: LintReport

    @property
    def passed(self) -> bool:
        """Did all verifications pass?"""
        return self.test_report.success and self.type_report.passed and self.lint_report.passed


async def verify_code(
    code: str,
    test_code: str | None = None,
    run_tests: bool = True,
    run_types: bool = True,
    run_lint: bool = True,
    timeout: float = 60.0,
) -> VerificationResult:
    """
    Run all verification tools on generated code.

    Args:
        code: The implementation code
        test_code: Optional test code
        run_tests: Whether to run pytest
        run_types: Whether to run mypy
        run_lint: Whether to run ruff
        timeout: Timeout per tool

    Returns:
        VerificationResult with all reports
    """
    # Run all verifications in parallel
    test_task = run_pytest(code, test_code, timeout) if run_tests else _empty_test_report()
    type_task = run_mypy(code, timeout) if run_types else _empty_type_report()
    lint_task = run_ruff(code, timeout) if run_lint else _empty_lint_report()

    test_report, type_report, lint_report = await asyncio.gather(test_task, type_task, lint_task)

    return VerificationResult(
        test_report=test_report,
        type_report=type_report,
        lint_report=lint_report,
    )


async def _empty_test_report() -> TestReport:
    """Return an empty test report (skipped)."""
    return TestReport(passed=0, failed=0, skipped=0)


async def _empty_type_report() -> TypeReport:
    """Return an empty type report (skipped)."""
    return TypeReport(passed=True, error_count=0)


async def _empty_lint_report() -> LintReport:
    """Return an empty lint report (skipped)."""
    return LintReport(passed=True, violation_count=0)
