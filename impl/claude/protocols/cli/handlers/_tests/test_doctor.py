"""
Tests for doctor command.

Testing strategy:
- Unit tests for CheckStatus enum values
- Unit tests for DoctorReport computed properties
- Integration tests for cmd_doctor command execution
- Mocked check functions for controlled outcomes

Test Tiers:
- tier1: Pure function tests (enum values, dataclass properties)
- tier2: Integration tests (command execution with mocked dependencies)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest

from protocols.cli.handlers.doctor import (
    CheckResult,
    CheckStatus,
    DoctorReport,
    cmd_doctor,
    run_doctor,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Tier 1: CheckStatus Enum Tests
# =============================================================================


@pytest.mark.tier1
@pytest.mark.unit
def test_check_status_enum():
    """Test CheckStatus enum has expected values."""
    assert CheckStatus.PASS.value == "pass"
    assert CheckStatus.WARN.value == "warn"
    assert CheckStatus.FAIL.value == "fail"
    assert CheckStatus.SKIP.value == "skip"

    # Verify all expected statuses exist
    expected_statuses = {"pass", "warn", "fail", "skip"}
    actual_statuses = {status.value for status in CheckStatus}
    assert actual_statuses == expected_statuses


# =============================================================================
# Tier 1: DoctorReport Computed Properties Tests
# =============================================================================


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_empty():
    """Test DoctorReport with no checks."""
    report = DoctorReport()
    assert report.passed == 0
    assert report.warnings == 0
    assert report.failures == 0
    assert report.healthy is True


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_all_passed():
    """Test DoctorReport with all checks passed."""
    report = DoctorReport(
        checks=[
            CheckResult(name="Check 1", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Check 2", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Check 3", status=CheckStatus.PASS, message="OK"),
        ]
    )
    assert report.passed == 3
    assert report.warnings == 0
    assert report.failures == 0
    assert report.healthy is True


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_with_warnings():
    """Test DoctorReport with warnings (still healthy)."""
    report = DoctorReport(
        checks=[
            CheckResult(name="Check 1", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Check 2", status=CheckStatus.WARN, message="Warning"),
            CheckResult(name="Check 3", status=CheckStatus.PASS, message="OK"),
        ]
    )
    assert report.passed == 2
    assert report.warnings == 1
    assert report.failures == 0
    assert report.healthy is True  # Warnings don't affect health


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_with_failures():
    """Test DoctorReport with failures (unhealthy)."""
    report = DoctorReport(
        checks=[
            CheckResult(name="Check 1", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Check 2", status=CheckStatus.FAIL, message="Failed"),
            CheckResult(name="Check 3", status=CheckStatus.WARN, message="Warning"),
        ]
    )
    assert report.passed == 1
    assert report.warnings == 1
    assert report.failures == 1
    assert report.healthy is False


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_with_skipped():
    """Test DoctorReport with skipped checks (not counted as passed/warn/fail)."""
    report = DoctorReport(
        checks=[
            CheckResult(name="Check 1", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Check 2", status=CheckStatus.SKIP, message="Skipped"),
        ]
    )
    assert report.passed == 1
    assert report.warnings == 0
    assert report.failures == 0
    assert report.healthy is True


@pytest.mark.tier1
@pytest.mark.unit
def test_doctor_report_properties():
    """Test DoctorReport computed properties work correctly with mixed statuses."""
    report = DoctorReport(
        checks=[
            CheckResult(name="XDG", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="DB", status=CheckStatus.PASS, message="OK"),
            CheckResult(name="Tables", status=CheckStatus.FAIL, message="Missing"),
            CheckResult(name="Genesis", status=CheckStatus.WARN, message="Partial"),
            CheckResult(name="Instances", status=CheckStatus.SKIP, message="Skipped"),
        ]
    )
    assert report.passed == 2
    assert report.warnings == 1
    assert report.failures == 1
    assert report.healthy is False


# =============================================================================
# Tier 1: CheckResult Tests
# =============================================================================


@pytest.mark.tier1
@pytest.mark.unit
def test_check_result_basic():
    """Test CheckResult basic construction."""
    result = CheckResult(
        name="Test Check",
        status=CheckStatus.PASS,
        message="All good",
    )
    assert result.name == "Test Check"
    assert result.status == CheckStatus.PASS
    assert result.message == "All good"
    assert result.details == {}
    assert result.fix_hint is None


@pytest.mark.tier1
@pytest.mark.unit
def test_check_result_with_details():
    """Test CheckResult with details and fix_hint."""
    result = CheckResult(
        name="Test Check",
        status=CheckStatus.FAIL,
        message="Something wrong",
        details={"path": "/test", "error": "Not found"},
        fix_hint="Run 'kg reset' to fix",
    )
    assert result.details == {"path": "/test", "error": "Not found"}
    assert result.fix_hint == "Run 'kg reset' to fix"


# =============================================================================
# Tier 2: Command Execution Tests
# =============================================================================


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_help_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """Test --help returns 0 and shows help."""
    result = await cmd_doctor(["--help"])
    assert result == 0

    captured = capsys.readouterr()
    assert "kgents doctor" in captured.out
    assert "USAGE" in captured.out
    assert "--fix" in captured.out
    assert "--json" in captured.out
    assert "EXIT CODES" in captured.out


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_help_flag_short(capsys: pytest.CaptureFixture[str]) -> None:
    """Test -h returns 0 and shows help."""
    result = await cmd_doctor(["-h"])
    assert result == 0

    captured = capsys.readouterr()
    assert "kgents doctor" in captured.out


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test --json returns valid JSON with expected structure."""
    # Mock all check functions to return passing results
    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Instance Registry", status=CheckStatus.PASS, message="OK"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        result = await cmd_doctor(["--json"])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # Verify expected structure
    assert "healthy" in output
    assert "passed" in output
    assert "warnings" in output
    assert "failures" in output
    assert "checks" in output

    # Verify values
    assert output["healthy"] is True
    assert output["passed"] == 5
    assert output["warnings"] == 0
    assert output["failures"] == 0
    assert len(output["checks"]) == 5

    # Verify check structure
    for check in output["checks"]:
        assert "name" in check
        assert "status" in check
        assert "message" in check
        assert "details" in check
        assert "fix_hint" in check


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_healthy_report(capsys: pytest.CaptureFixture[str]) -> None:
    """Test all checks passing returns 0."""
    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="All good"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="Exists"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="Present"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="Seeded"),
        CheckResult(name="Instance Registry", status=CheckStatus.PASS, message="Clean"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        result = await cmd_doctor([])

    assert result == 0

    captured = capsys.readouterr()
    assert "HEALTHY" in captured.out


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_unhealthy_report(capsys: pytest.CaptureFixture[str]) -> None:
    """Test failed checks return 1."""
    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(
            name="Global Database",
            status=CheckStatus.FAIL,
            message="Not found",
            fix_hint="Run 'kg reset'",
        ),
        CheckResult(
            name="Database Tables",
            status=CheckStatus.FAIL,
            message="Missing 5 tables",
            fix_hint="Run 'kg reset'",
        ),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.WARN, message="Partial"),
        CheckResult(name="Instance Registry", status=CheckStatus.SKIP, message="Skipped"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        result = await cmd_doctor([])

    assert result == 1

    captured = capsys.readouterr()
    assert "UNHEALTHY" in captured.out
    assert "2 failure" in captured.out


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_fix_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """Test --fix attempts repairs on eligible checks."""
    # Create a warning check that can be fixed
    warn_check = CheckResult(
        name="Instance Registry",
        status=CheckStatus.WARN,
        message="2 stale instances",
        fix_hint="Run 'kg doctor --fix'",
    )

    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        warn_check,
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    async def mock_fix() -> tuple[bool, str]:
        return True, "Stale instances marked as terminated"

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
        patch(
            "protocols.cli.handlers.doctor.fix_stale_instances",
            side_effect=mock_fix,
        ),
    ):
        result = await cmd_doctor(["--fix"])

    assert result == 0

    captured = capsys.readouterr()
    assert "HEALTHY" in captured.out


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_fix_flag_json_output(capsys: pytest.CaptureFixture[str]) -> None:
    """Test --fix with --json outputs JSON after fixes."""
    warn_check = CheckResult(
        name="Instance Registry",
        status=CheckStatus.WARN,
        message="2 stale instances",
        fix_hint="Run 'kg doctor --fix'",
    )

    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        warn_check,
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    async def mock_fix() -> tuple[bool, str]:
        return True, "Stale instances marked as terminated"

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
        patch(
            "protocols.cli.handlers.doctor.fix_stale_instances",
            side_effect=mock_fix,
        ),
    ):
        result = await cmd_doctor(["--fix", "--json"])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["healthy"] is True
    # After fix, the Instance Registry should be PASS
    instance_check = next(c for c in output["checks"] if c["name"] == "Instance Registry")
    assert instance_check["status"] == "pass"
    assert "Fixed:" in instance_check["message"]


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_fix_failure(capsys: pytest.CaptureFixture[str]) -> None:
    """Test --fix when fix function fails."""
    warn_check = CheckResult(
        name="Instance Registry",
        status=CheckStatus.WARN,
        message="2 stale instances",
        fix_hint="Run 'kg doctor --fix'",
    )

    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        warn_check,
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    async def mock_fix() -> tuple[bool, str]:
        return False, "Failed to clean up: database locked"

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
        patch(
            "protocols.cli.handlers.doctor.fix_stale_instances",
            side_effect=mock_fix,
        ),
    ):
        result = await cmd_doctor(["--fix", "--json"])

    # Should still return 0 because warnings don't affect health
    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # Check should still be WARN since fix failed
    instance_check = next(c for c in output["checks"] if c["name"] == "Instance Registry")
    assert instance_check["status"] == "warn"


# =============================================================================
# Tier 2: run_doctor Function Tests
# =============================================================================


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_run_doctor_returns_report() -> None:
    """Test run_doctor returns a DoctorReport with all checks."""
    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Instance Registry", status=CheckStatus.PASS, message="OK"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        report = await run_doctor(fix=False)

    assert isinstance(report, DoctorReport)
    assert len(report.checks) == 5
    assert report.healthy is True
    assert report.passed == 5


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_run_doctor_with_fix_modifies_report() -> None:
    """Test run_doctor with fix=True modifies check results."""
    warn_check = CheckResult(
        name="Instance Registry",
        status=CheckStatus.WARN,
        message="2 stale instances",
        fix_hint="Run 'kg doctor --fix'",
    )

    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        warn_check,
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    async def mock_fix() -> tuple[bool, str]:
        return True, "Cleaned up"

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
        patch(
            "protocols.cli.handlers.doctor.fix_stale_instances",
            side_effect=mock_fix,
        ),
    ):
        report = await run_doctor(fix=True)

    assert isinstance(report, DoctorReport)
    assert report.healthy is True

    # Instance Registry should be fixed
    instance_check = next(c for c in report.checks if c.name == "Instance Registry")
    assert instance_check.status == CheckStatus.PASS
    assert "Fixed:" in instance_check.message
    assert instance_check.fix_hint is None


# =============================================================================
# Tier 2: JSON Output Structure Tests
# =============================================================================


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_json_check_structure(capsys: pytest.CaptureFixture[str]) -> None:
    """Test JSON output check structure includes all expected fields."""
    mock_check = CheckResult(
        name="Test Check",
        status=CheckStatus.FAIL,
        message="Test failed",
        details={"key": "value", "count": 42},
        fix_hint="Do something",
    )

    mock_checks = [
        mock_check,
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        await cmd_doctor(["--json"])

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # Find the test check
    test_check = output["checks"][0]

    # Verify all fields present
    assert test_check["name"] == "Test Check"
    assert test_check["status"] == "fail"
    assert test_check["message"] == "Test failed"
    assert test_check["details"] == {"key": "value", "count": 42}
    assert test_check["fix_hint"] == "Do something"


@pytest.mark.tier2
@pytest.mark.asyncio
async def test_doctor_json_null_fix_hint(capsys: pytest.CaptureFixture[str]) -> None:
    """Test JSON output correctly represents null fix_hint."""
    mock_checks = [
        CheckResult(name="XDG Directories", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Global Database", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Database Tables", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Genesis K-Blocks", status=CheckStatus.PASS, message="OK"),
        CheckResult(name="Instance Registry", status=CheckStatus.PASS, message="OK"),
    ]

    async def mock_xdg() -> CheckResult:
        return mock_checks[0]

    async def mock_db() -> CheckResult:
        return mock_checks[1]

    async def mock_tables() -> CheckResult:
        return mock_checks[2]

    async def mock_genesis() -> CheckResult:
        return mock_checks[3]

    async def mock_instances() -> CheckResult:
        return mock_checks[4]

    with (
        patch(
            "protocols.cli.handlers.doctor.check_xdg_directories",
            side_effect=mock_xdg,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_global_db_exists",
            side_effect=mock_db,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_tables_exist",
            side_effect=mock_tables,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_genesis_status",
            side_effect=mock_genesis,
        ),
        patch(
            "protocols.cli.handlers.doctor.check_stale_instances",
            side_effect=mock_instances,
        ),
    ):
        await cmd_doctor(["--json"])

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # All passing checks should have null fix_hint
    for check in output["checks"]:
        assert check["fix_hint"] is None


__all__ = []
