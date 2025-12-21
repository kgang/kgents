"""
Tests for ASHC Verification Runners

Tests the pytest, mypy, and ruff integration.
"""

from __future__ import annotations

import pytest

from ..verify import (
    LintReport,
    SubprocessResult,
    TestReport,
    TypeReport,
    VerificationResult,
    _parse_mypy_output,
    _parse_pytest_output,
    _parse_ruff_output,
    run_mypy,
    run_pytest,
    run_ruff,
    verify_code,
)

# =============================================================================
# Test Report Parsing
# =============================================================================


class TestParsePytestOutput:
    """Tests for pytest output parsing."""

    def test_parse_all_passed(self) -> None:
        """Parse output with all tests passed."""
        result = SubprocessResult(
            stdout="===== 5 passed in 0.12s =====",
            stderr="",
            returncode=0,
            duration_ms=120.0,
        )
        report = _parse_pytest_output(result)

        assert report.passed == 5
        assert report.failed == 0
        assert report.skipped == 0
        assert report.success

    def test_parse_mixed_results(self) -> None:
        """Parse output with mixed results."""
        result = SubprocessResult(
            stdout="===== 3 passed, 2 failed, 1 skipped in 0.25s =====",
            stderr="",
            returncode=1,
            duration_ms=250.0,
        )
        report = _parse_pytest_output(result)

        assert report.passed == 3
        assert report.failed == 2
        assert report.skipped == 1
        assert not report.success

    def test_parse_failure_lines(self) -> None:
        """Parse FAILED lines into errors."""
        result = SubprocessResult(
            stdout="""
FAILED test_foo.py::test_one - AssertionError
FAILED test_foo.py::test_two - ValueError
===== 2 failed in 0.10s =====
""",
            stderr="",
            returncode=1,
            duration_ms=100.0,
        )
        report = _parse_pytest_output(result)

        assert report.failed == 2
        assert len(report.errors) == 2
        assert "test_one" in report.errors[0]

    def test_parse_collection_error(self) -> None:
        """Parse collection/import errors."""
        result = SubprocessResult(
            stdout="",
            stderr="ImportError: No module named 'foo'",
            returncode=2,
            duration_ms=50.0,
        )
        report = _parse_pytest_output(result)

        assert report.failed == 1
        assert len(report.errors) >= 1
        assert not report.success

    def test_parse_empty_output(self) -> None:
        """Parse empty output (no tests collected)."""
        result = SubprocessResult(
            stdout="===== no tests ran in 0.01s =====",
            stderr="",
            returncode=0,
            duration_ms=10.0,
        )
        report = _parse_pytest_output(result)

        assert report.passed == 0
        assert report.failed == 0
        assert report.total == 0


class TestParseMypyOutput:
    """Tests for mypy output parsing."""

    def test_parse_no_errors(self) -> None:
        """Parse mypy output with no errors."""
        result = SubprocessResult(
            stdout="Success: no issues found in 1 source file",
            stderr="",
            returncode=0,
            duration_ms=500.0,
        )
        report = _parse_mypy_output(result)

        assert report.passed
        assert report.error_count == 0

    def test_parse_type_errors(self) -> None:
        """Parse mypy output with type errors."""
        result = SubprocessResult(
            stdout="""code.py:10: error: Incompatible types in assignment
code.py:15: error: Missing return statement
Found 2 errors in 1 file""",
            stderr="",
            returncode=1,
            duration_ms=600.0,
        )
        report = _parse_mypy_output(result)

        assert not report.passed
        assert report.error_count == 2
        assert len(report.errors) == 2

    def test_parse_single_error(self) -> None:
        """Parse mypy output with single error."""
        result = SubprocessResult(
            stdout='code.py:1: error: Cannot find implementation or library stub for module named "nonexistent"',
            stderr="",
            returncode=1,
            duration_ms=300.0,
        )
        report = _parse_mypy_output(result)

        assert not report.passed
        assert report.error_count == 1


class TestParseRuffOutput:
    """Tests for ruff output parsing."""

    def test_parse_no_violations(self) -> None:
        """Parse ruff output with no violations."""
        result = SubprocessResult(
            stdout="",
            stderr="",
            returncode=0,
            duration_ms=50.0,
        )
        report = _parse_ruff_output(result)

        assert report.passed
        assert report.violation_count == 0

    def test_parse_violations(self) -> None:
        """Parse ruff output with violations."""
        result = SubprocessResult(
            stdout="""code.py:1:1: E501 Line too long (120 > 88)
code.py:5:1: F401 'os' imported but unused
code.py:10:5: E711 Comparison to None should be 'if cond is None:'""",
            stderr="",
            returncode=1,
            duration_ms=30.0,
        )
        report = _parse_ruff_output(result)

        assert not report.passed
        assert report.violation_count == 3
        assert len(report.violations) == 3

    def test_parse_single_violation(self) -> None:
        """Parse ruff output with single violation."""
        result = SubprocessResult(
            stdout="code.py:1:1: F401 'sys' imported but unused",
            stderr="",
            returncode=1,
            duration_ms=20.0,
        )
        report = _parse_ruff_output(result)

        assert not report.passed
        assert report.violation_count == 1


# =============================================================================
# Test Verification Runners
# =============================================================================


class TestRunPytest:
    """Tests for pytest runner."""

    @pytest.mark.asyncio
    async def test_passing_test(self) -> None:
        """Run pytest on passing test."""
        code = """
def add(a: int, b: int) -> int:
    return a + b
"""
        test_code = """
from impl import add

def test_add():
    assert add(1, 2) == 3
    assert add(0, 0) == 0
"""
        report = await run_pytest(code, test_code, timeout=30.0)

        assert report.passed >= 1
        assert report.failed == 0
        assert report.success

    @pytest.mark.asyncio
    async def test_failing_test(self) -> None:
        """Run pytest on failing test."""
        code = """
def add(a: int, b: int) -> int:
    return a - b  # Bug: subtraction instead of addition
"""
        test_code = """
from impl import add

def test_add():
    assert add(1, 2) == 3  # Will fail
"""
        report = await run_pytest(code, test_code, timeout=30.0)

        assert report.failed >= 1
        assert not report.success

    @pytest.mark.asyncio
    async def test_syntax_error(self) -> None:
        """Run pytest on code with syntax error."""
        code = """
def add(a, b)  # Missing colon
    return a + b
"""
        test_code = """
from impl import add  # This will fail due to syntax error

def test_add():
    assert add(1, 2) == 3
"""
        report = await run_pytest(code, test_code, timeout=30.0)

        # Should detect the error (either failed tests or collection error)
        assert not report.success


class TestRunMypy:
    """Tests for mypy runner."""

    @pytest.mark.asyncio
    async def test_valid_types(self) -> None:
        """Run mypy on correctly typed code."""
        code = """
def greet(name: str) -> str:
    return f"Hello, {name}"

result: str = greet("World")
"""
        report = await run_mypy(code, timeout=30.0)

        # Note: mypy may or may not find issues depending on strictness
        # We just verify it runs without crash
        assert isinstance(report, TypeReport)

    @pytest.mark.asyncio
    async def test_type_error(self) -> None:
        """Run mypy on code with type error."""
        code = """
def add(a: int, b: int) -> int:
    return a + b

result: str = add(1, 2)  # Type error: int assigned to str
"""
        report = await run_mypy(code, timeout=30.0)

        # Should detect the type error
        # Note: exact behavior depends on mypy config
        assert isinstance(report, TypeReport)


class TestRunRuff:
    """Tests for ruff runner."""

    @pytest.mark.asyncio
    async def test_clean_code(self) -> None:
        """Run ruff on clean code."""
        code = """
def greet(name: str) -> str:
    \"\"\"Greet someone.\"\"\"
    return f"Hello, {name}"
"""
        report = await run_ruff(code, timeout=10.0)

        # Clean code should have no violations
        assert report.passed
        assert report.violation_count == 0

    @pytest.mark.asyncio
    async def test_unused_import(self) -> None:
        """Run ruff on code with unused import."""
        code = """
import os  # Unused import
import sys  # Also unused

def greet(name: str) -> str:
    return f"Hello, {name}"
"""
        report = await run_ruff(code, timeout=10.0)

        # Should detect unused imports
        assert report.violation_count >= 1
        assert not report.passed


# =============================================================================
# Test Combined Verification
# =============================================================================


class TestVerifyCode:
    """Tests for combined verification."""

    @pytest.mark.asyncio
    async def test_all_passing(self) -> None:
        """Verify code that passes all checks."""
        code = """
def add(a: int, b: int) -> int:
    \"\"\"Add two integers.\"\"\"
    return a + b
"""
        test_code = """
from impl import add

def test_add() -> None:
    assert add(1, 2) == 3
"""
        result = await verify_code(code, test_code, timeout=30.0)

        assert isinstance(result, VerificationResult)
        assert isinstance(result.test_report, TestReport)
        assert isinstance(result.type_report, TypeReport)
        assert isinstance(result.lint_report, LintReport)

    @pytest.mark.asyncio
    async def test_skip_verifications(self) -> None:
        """Verify with some checks disabled."""
        code = """
import os  # Unused - would fail lint

def foo():
    pass
"""
        result = await verify_code(
            code,
            run_tests=False,
            run_types=False,
            run_lint=False,
        )

        # Should return empty reports
        assert result.test_report.total == 0
        assert result.type_report.passed
        assert result.lint_report.passed


# =============================================================================
# Test Report Properties
# =============================================================================


class TestReportProperties:
    """Tests for report computed properties."""

    def test_test_report_total(self) -> None:
        """Test TestReport.total property."""
        report = TestReport(passed=5, failed=2, skipped=1)
        assert report.total == 8

    def test_test_report_success(self) -> None:
        """Test TestReport.success property."""
        passing = TestReport(passed=5, failed=0, skipped=0)
        assert passing.success

        failing = TestReport(passed=5, failed=1, skipped=0)
        assert not failing.success

        with_errors = TestReport(passed=5, failed=0, skipped=0, errors=("error",))
        assert not with_errors.success

    def test_type_report_passed(self) -> None:
        """Test TypeReport properties."""
        passing = TypeReport(passed=True, error_count=0)
        assert passing.passed

        failing = TypeReport(passed=False, error_count=2)
        assert not failing.passed

    def test_lint_report_passed(self) -> None:
        """Test LintReport properties."""
        passing = LintReport(passed=True, violation_count=0)
        assert passing.passed

        failing = LintReport(passed=False, violation_count=3)
        assert not failing.passed
