"""
Doctor Command - Comprehensive kgents health check.

Inspects database, storage, genesis, and instance state.
Optionally fixes issues that can be auto-repaired.

Principle: Transparent Infrastructure
- Make the invisible visible
- Clear pass/fail for each check
- Actionable fix suggestions
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class CheckStatus(str, Enum):
    """Status of a health check."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CheckResult:
    """Result of a single health check."""

    name: str
    status: CheckStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    fix_hint: str | None = None


@dataclass
class DoctorReport:
    """Aggregated results of all health checks."""

    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)

    @property
    def warnings(self) -> int:
        """Count of warning checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)

    @property
    def failures(self) -> int:
        """Count of failed checks."""
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)

    @property
    def healthy(self) -> bool:
        """True if no failures (warnings are OK)."""
        return self.failures == 0


# =============================================================================
# Health Check Functions
# =============================================================================


async def check_xdg_directories() -> CheckResult:
    """Check if XDG directories exist and are writable."""
    from protocols.cli.instance_db.storage import XDGPaths

    paths = XDGPaths.resolve()
    issues = []
    writable_issues = []

    for name, path in [
        ("data", paths.data),
        ("config", paths.config),
        ("cache", paths.cache),
    ]:
        if not path.exists():
            issues.append(f"{name} missing")
        elif not path.is_dir():
            issues.append(f"{name} not a directory")
        else:
            # Check writability by testing if we can create a temp file
            test_file = path / ".doctor_test"
            try:
                test_file.touch()
                test_file.unlink()
            except OSError:
                writable_issues.append(f"{name} not writable")

    if not issues and not writable_issues:
        return CheckResult(
            name="XDG Directories",
            status=CheckStatus.PASS,
            message="All directories present and writable",
            details={
                "data": str(paths.data),
                "config": str(paths.config),
                "cache": str(paths.cache),
            },
        )
    elif writable_issues and not issues:
        return CheckResult(
            name="XDG Directories",
            status=CheckStatus.WARN,
            message=f"Permission issues: {', '.join(writable_issues)}",
            details={
                "data": str(paths.data),
                "config": str(paths.config),
                "cache": str(paths.cache),
            },
            fix_hint="Check directory permissions",
        )
    else:
        all_issues = issues + writable_issues
        return CheckResult(
            name="XDG Directories",
            status=CheckStatus.FAIL,
            message=f"Issues: {', '.join(all_issues)}",
            fix_hint="Run 'kg reset' to create directories",
        )


async def check_global_db_exists() -> CheckResult:
    """Check if global database file exists with size info."""
    from protocols.cli.instance_db.storage import XDGPaths

    paths = XDGPaths.resolve()
    db_path = paths.data / "membrane.db"

    # Check for Postgres via environment
    db_url = os.environ.get("KGENTS_DATABASE_URL", "")
    if db_url.startswith("postgresql"):
        # Using Postgres - check if we can connect
        try:
            from models.base import get_engine

            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(__import__("sqlalchemy").text("SELECT 1"))

            return CheckResult(
                name="Global Database",
                status=CheckStatus.PASS,
                message="PostgreSQL connected",
                details={"backend": "postgresql", "url": db_url[:50] + "..."},
            )
        except Exception as e:
            return CheckResult(
                name="Global Database",
                status=CheckStatus.FAIL,
                message=f"PostgreSQL connection failed: {e}",
                details={"backend": "postgresql"},
                fix_hint="Check KGENTS_DATABASE_URL and ensure Postgres is running",
            )

    # SQLite mode - check file exists
    if db_path.exists():
        size = db_path.stat().st_size
        if size > 1024 * 1024:
            size_str = f"{size / 1024 / 1024:.1f} MB"
        elif size > 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size} B"

        return CheckResult(
            name="Global Database",
            status=CheckStatus.PASS,
            message=f"Exists ({size_str})",
            details={
                "path": str(db_path),
                "size": size,
                "size_str": size_str,
                "backend": "sqlite",
            },
        )
    else:
        return CheckResult(
            name="Global Database",
            status=CheckStatus.FAIL,
            message=f"Not found at {db_path}",
            details={"path": str(db_path), "backend": "sqlite"},
            fix_hint="Run 'kg reset' to create database",
        )


async def check_tables_exist() -> CheckResult:
    """Check if all SQLAlchemy tables are present."""
    try:
        from sqlalchemy import inspect, text

        from models.base import Base, get_engine

        engine = get_engine()

        async with engine.connect() as conn:

            def get_tables(connection: Any) -> set[str]:
                inspector = inspect(connection)
                return set(inspector.get_table_names())

            existing = await conn.run_sync(get_tables)

        # Expected tables from SQLAlchemy models
        expected = set(Base.metadata.tables.keys())

        # If no models registered, skip this check
        if not expected:
            return CheckResult(
                name="Database Tables",
                status=CheckStatus.SKIP,
                message="No SQLAlchemy models registered",
            )

        missing = expected - existing
        extra = existing - expected

        if not missing:
            return CheckResult(
                name="Database Tables",
                status=CheckStatus.PASS,
                message=f"All {len(expected)} model tables present",
                details={
                    "expected": len(expected),
                    "existing": len(existing),
                    "extra": len(extra),
                },
            )
        else:
            # Truncate for display
            missing_display = ", ".join(sorted(missing)[:5])
            if len(missing) > 5:
                missing_display += f"... (+{len(missing) - 5} more)"

            return CheckResult(
                name="Database Tables",
                status=CheckStatus.FAIL,
                message=f"Missing {len(missing)} tables: {missing_display}",
                details={"missing": sorted(missing), "extra": sorted(extra)},
                fix_hint="Run 'kg reset' or '/init-db' to create missing tables",
            )
    except Exception as e:
        return CheckResult(
            name="Database Tables",
            status=CheckStatus.FAIL,
            message=f"Could not inspect tables: {e}",
            fix_hint="Check database connection",
        )


async def check_genesis_status() -> CheckResult:
    """Check if genesis K-Blocks are seeded (22 expected)."""
    try:
        from sqlalchemy import text

        from models.base import get_async_session

        async with get_async_session() as session:
            # Check for kblocks table (note: no underscore in table name)
            try:
                result = await session.execute(
                    text("SELECT COUNT(*) FROM kblocks WHERE id LIKE 'genesis:%'")
                )
                count = result.scalar() or 0
            except Exception:
                # Table might not exist
                return CheckResult(
                    name="Genesis K-Blocks",
                    status=CheckStatus.SKIP,
                    message="kblocks table not found",
                    fix_hint="Run 'kg reset' to create tables first",
                )

        expected = 22  # Constitutional K-Blocks

        if count >= expected:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.PASS,
                message=f"{count}/{expected} K-Blocks seeded",
                details={"count": count, "expected": expected},
            )
        elif count > 0:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.WARN,
                message=f"Partial seeding: {count}/{expected} K-Blocks",
                details={"count": count, "expected": expected},
                fix_hint="Run 'kg reset --genesis' for complete seeding",
            )
        else:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.WARN,
                message="Not seeded (optional for basic operation)",
                details={"count": 0, "expected": expected},
                fix_hint="Run 'kg reset --genesis' to seed K-Blocks",
            )
    except Exception as e:
        return CheckResult(
            name="Genesis K-Blocks",
            status=CheckStatus.SKIP,
            message=f"Could not check: {e}",
        )


async def check_stale_instances() -> CheckResult:
    """Check for stale instance registrations (no heartbeat > 5 min)."""
    try:
        from protocols.cli.instance_db.storage import StorageProvider, XDGPaths

        paths = XDGPaths.resolve()
        storage = await StorageProvider.from_config(None, paths)

        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()

        # Check if instances table exists
        try:
            result = await storage.relational.fetch_all(
                "SELECT COUNT(*) as count FROM instances WHERE status = 'active' AND last_heartbeat < :cutoff",
                {"cutoff": cutoff},
            )
            stale_count = result[0]["count"] if result else 0

            # Also get total active count
            total_result = await storage.relational.fetch_all(
                "SELECT COUNT(*) as count FROM instances WHERE status = 'active'",
                {},
            )
            total_active = total_result[0]["count"] if total_result else 0

        except Exception:
            # Table might not exist - that's OK for fresh installs
            return CheckResult(
                name="Instance Registry",
                status=CheckStatus.SKIP,
                message="instances table not found",
                fix_hint="Run 'kg reset' to create tables",
            )

        await storage.close()

        if stale_count == 0:
            if total_active > 0:
                return CheckResult(
                    name="Instance Registry",
                    status=CheckStatus.PASS,
                    message=f"Clean ({total_active} active instance(s))",
                    details={"active": total_active, "stale": 0},
                )
            else:
                return CheckResult(
                    name="Instance Registry",
                    status=CheckStatus.PASS,
                    message="No active instances",
                    details={"active": 0, "stale": 0},
                )
        else:
            return CheckResult(
                name="Instance Registry",
                status=CheckStatus.WARN,
                message=f"{stale_count} stale instance(s) (no heartbeat > 5 min)",
                details={"active": total_active, "stale": stale_count},
                fix_hint="Run 'kg doctor --fix' to clean up stale instances",
            )
    except Exception as e:
        return CheckResult(
            name="Instance Registry",
            status=CheckStatus.SKIP,
            message=f"Could not check: {e}",
        )


# =============================================================================
# Fix Functions (for --fix flag)
# =============================================================================


async def fix_stale_instances() -> tuple[bool, str]:
    """
    Clean up stale instance registrations.

    Returns:
        (success, message) tuple
    """
    try:
        from protocols.cli.instance_db.storage import StorageProvider, XDGPaths

        paths = XDGPaths.resolve()
        storage = await StorageProvider.from_config(None, paths)

        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()

        # Mark stale instances as terminated
        await storage.relational.execute(
            "UPDATE instances SET status = 'terminated' WHERE status = 'active' AND last_heartbeat < :cutoff",
            {"cutoff": cutoff},
        )

        await storage.close()
        return True, "Stale instances marked as terminated"
    except Exception as e:
        return False, f"Failed to clean up: {e}"


# =============================================================================
# Main Doctor Logic
# =============================================================================


async def run_doctor(fix: bool = False) -> DoctorReport:
    """
    Run all health checks.

    Args:
        fix: If True, attempt to auto-fix issues

    Returns:
        DoctorReport with all check results
    """
    report = DoctorReport()

    # Run checks in order
    checks = [
        check_xdg_directories(),
        check_global_db_exists(),
        check_tables_exist(),
        check_genesis_status(),
        check_stale_instances(),
    ]

    for check_coro in checks:
        result = await check_coro
        report.checks.append(result)

    # Apply fixes if requested
    if fix:
        for check in report.checks:
            if check.status == CheckStatus.WARN and check.name == "Instance Registry":
                success, message = await fix_stale_instances()
                if success:
                    check.status = CheckStatus.PASS
                    check.message = f"Fixed: {message}"
                    check.fix_hint = None

    return report


def _print_report(report: DoctorReport) -> None:
    """Print doctor report to console with ANSI colors."""
    status_icons = {
        CheckStatus.PASS: "\033[32m✓\033[0m",  # Green checkmark
        CheckStatus.WARN: "\033[33m⚠\033[0m",  # Yellow warning
        CheckStatus.FAIL: "\033[31m✗\033[0m",  # Red X
        CheckStatus.SKIP: "\033[90m○\033[0m",  # Gray circle
    }

    print("\n\033[1mkgents Health Check\033[0m\n")

    for check in report.checks:
        icon = status_icons[check.status]
        print(f"  {icon} {check.name}: {check.message}")
        if check.fix_hint and check.status in (CheckStatus.WARN, CheckStatus.FAIL):
            print(f"      \033[90m→ {check.fix_hint}\033[0m")

    print()

    # Summary line
    if report.healthy:
        if report.warnings:
            print(
                f"\033[32m✓ HEALTHY\033[0m ({report.warnings} warning{'s' if report.warnings != 1 else ''})"
            )
        else:
            print("\033[32m✓ HEALTHY\033[0m")
    else:
        parts = []
        if report.failures:
            parts.append(f"{report.failures} failure{'s' if report.failures != 1 else ''}")
        if report.warnings:
            parts.append(f"{report.warnings} warning{'s' if report.warnings != 1 else ''}")
        print(f"\033[31m✗ UNHEALTHY\033[0m ({', '.join(parts)})")


def _print_help() -> None:
    """Print help for doctor command."""
    print("kgents doctor - Health check for kgents installation")
    print()
    print("USAGE: kgents doctor [options]")
    print()
    print("OPTIONS:")
    print("  --fix         Auto-fix issues that can be repaired")
    print("  --json        Output as JSON (for scripts/CI)")
    print("  --help, -h    Show this help")
    print()
    print("CHECKS:")
    print("  - XDG directories exist and writable")
    print("  - Global database (membrane.db or Postgres) accessible")
    print("  - All SQLAlchemy model tables present")
    print("  - Genesis K-Blocks seeded (22 expected, optional)")
    print("  - No stale instance registrations (> 5 min without heartbeat)")
    print()
    print("EXIT CODES:")
    print("  0  All checks passed (warnings OK)")
    print("  1  One or more checks failed")
    print()
    print("EXAMPLES:")
    print("  kgents doctor              # Run health check")
    print("  kgents doctor --fix        # Run and auto-fix issues")
    print("  kgents doctor --json       # Machine-readable output")


@handler("doctor", is_async=True, tier=1, description="Health check for kgents")
async def cmd_doctor(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle doctor command: Comprehensive health check."""
    fix = False
    json_output = False

    for arg in args:
        if arg in ("--help", "-h"):
            _print_help()
            return 0
        elif arg == "--fix":
            fix = True
        elif arg == "--json":
            json_output = True

    report = await run_doctor(fix=fix)

    if json_output:
        output = {
            "healthy": report.healthy,
            "passed": report.passed,
            "warnings": report.warnings,
            "failures": report.failures,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status.value,
                    "message": c.message,
                    "details": c.details,
                    "fix_hint": c.fix_hint,
                }
                for c in report.checks
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        _print_report(report)

    return 0 if report.healthy else 1
