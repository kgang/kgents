# Database & Bootstrap Refinement Plan

> *"The proof IS the decision. The mark IS the witness."*

**Status:** PROPOSED
**Author:** Claude + Kent
**Date:** 2025-01-16
**Principle Alignment:** Composable, Joy-Inducing, Tasteful

---

## Executive Summary

The kgents database and bootstrap infrastructure works but has accumulated rough edges: two separate table creation paths, naming inconsistencies, no unified reset operation, and no comprehensive health verification. This plan proposes four targeted improvements that increase joy without adding bloat.

**The Goal:** `kg reset --genesis` + `kg doctor` = confidence.

---

## Problem Statement

### Current Pain Points

| Issue | Impact | Frequency |
|-------|--------|-----------|
| Two table creation paths can drift | Silent failures, missing tables | Every new model |
| No unified reset command | Multi-step incantation required | Every fresh start |
| No DB health verification | "Is it working?" uncertainty | Debugging sessions |
| Naming inconsistency (cortex vs membrane) | Confusion in docs/help | Onboarding |

### The Incantation Problem

Today, a complete reset requires knowing:

```bash
# Step 1: Wipe
kg wipe global --force

# Step 2: Rebuild instance tables (automatic on next command)
kg brain status  # triggers bootstrap

# Step 3: Rebuild model tables (separate!)
uv run python -c "import asyncio; from models.base import init_db; asyncio.run(init_db())"

# Step 4: Seed genesis (optional, separate API)
curl -X POST http://localhost:8000/api/genesis/clean-slate
```

This is functional but not *joyful*.

---

## Current Architecture

### Storage Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE PROVIDERS                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  services/storage/provider.py          XDG File Storage          │
│    └─ cosmos/, uploads/, vectors/      (K-Blocks, staging)       │
│                                                                  │
│  protocols/cli/instance_db/storage.py  Unified DB Abstraction    │
│    └─ run_migrations()                 (instances, shapes,       │
│                                         dreams, cli_sessions)    │
│                                                                  │
│  models/base.py                        SQLAlchemy Models         │
│    └─ init_db()                        (Brain, Witness, K-Block, │
│                                         Teaching, Crystal, etc.) │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Table Ownership (Current)

| System | Tables | Creation Method |
|--------|--------|-----------------|
| Instance DB | `instances`, `shapes`, `dreams`, `embedding_metadata`, `schema_version`, `cli_sessions`, `cli_session_events`, `cli_session_agents`, `cli_session_artifacts` | `StorageProvider.run_migrations()` |
| SQLAlchemy Models | `brain_crystals`, `brain_teaching_crystals`, `witness_marks`, `witness_walks`, `k_blocks`, `k_block_edges`, `zero_seed_*`, etc. | `models.base.init_db()` |

**The Gap:** These two systems don't know about each other. A fresh database might have instance tables but missing model tables, or vice versa.

---

## Proposed Architecture

### Unified Bootstrap Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  kg reset --genesis                                              │
│    │                                                             │
│    ├─► Phase 1: WIPE                                            │
│    │     └─ Delete ~/.local/share/kgents/                       │
│    │     └─ Delete .kgents/ (if --local or --all)               │
│    │                                                             │
│    ├─► Phase 2: SCAFFOLD                                        │
│    │     └─ Create XDG directories                              │
│    │     └─ Write default config                                │
│    │                                                             │
│    ├─► Phase 3: TABLES                                          │
│    │     └─ StorageProvider.run_migrations() [instance tables]  │
│    │     └─ models.base.init_db() [model tables]                │
│    │     └─ Verify all tables exist                             │
│    │                                                             │
│    ├─► Phase 4: GENESIS (if --genesis)                          │
│    │     └─ Seed 22 Constitutional K-Blocks                     │
│    │     └─ Verify derivation graph                             │
│    │                                                             │
│    └─► Phase 5: VERIFY                                          │
│          └─ Run kg doctor internally                            │
│          └─ Report success/warnings                             │
└─────────────────────────────────────────────────────────────────┘
```

### New Command Surface

```bash
# Reset commands
kg reset                      # Interactive: confirm, wipe global, rebuild
kg reset --force              # No confirmation
kg reset --force --genesis    # Include K-Block seeding
kg reset --force --all        # Wipe local + global
kg reset --dry-run            # Preview only

# Health commands
kg doctor                     # Comprehensive health check
kg doctor --fix               # Auto-fix what's fixable
kg doctor --json              # Machine-readable output
```

---

## Implementation Plan

### Phase 1: Quick Wins (30 minutes)

**Goal:** Fix inconsistencies without adding new code.

#### 1.1 Fix Naming in Wipe Help Text

**File:** `protocols/cli/handlers/wipe.py`

```python
# Current (line 33):
print("  local     Remove project DB (.kgents/cortex.db)")

# Fixed:
print("  local     Remove project DB (.kgents/)")
```

#### 1.2 Update Documentation

**File:** `.claude/commands/init-db.md`

Add note about the two-phase table creation and when each is needed.

---

### Phase 2: Unified Reset Command (2 hours)

**Goal:** One command to rule them all.

#### 2.1 Create Reset Handler

**File:** `protocols/cli/handlers/reset.py`

```python
"""
Reset Command - Wipe and rebuild kgents database.

Combines wipe + table creation + optional genesis into one atomic operation.
This is the canonical way to get a fresh start.

Principle: Joy-Inducing
- One command instead of multi-step incantation
- Clear feedback at each phase
- Safe by default (requires confirmation)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from protocols.cli.handler_meta import handler


def _print_help() -> None:
    """Print help for reset command."""
    print("kgents reset - Reset database to clean state")
    print()
    print("USAGE: kgents reset [options]")
    print()
    print("OPTIONS:")
    print("  --force, -f     Skip confirmation prompt")
    print("  --genesis, -g   Seed constitutional K-Blocks after reset")
    print("  --all, -a       Reset both local and global (default: global only)")
    print("  --dry-run       Show what would happen without doing it")
    print("  --help, -h      Show this help")
    print()
    print("PHASES:")
    print("  1. WIPE      Remove existing database files")
    print("  2. SCAFFOLD  Create directory structure")
    print("  3. TABLES    Create all database tables")
    print("  4. GENESIS   Seed K-Blocks (if --genesis)")
    print("  5. VERIFY    Confirm everything is healthy")
    print()
    print("EXAMPLES:")
    print("  kgents reset                    # Interactive reset")
    print("  kgents reset --force            # Skip confirmation")
    print("  kgents reset --force --genesis  # Full reset with K-Blocks")
    print("  kgents reset --dry-run          # Preview only")


async def _run_reset(
    scope: str,
    genesis: bool,
    dry_run: bool,
) -> bool:
    """
    Execute the reset sequence.

    Returns True on success, False on failure.
    """
    from protocols.cli.handlers.wipe import _collect_targets, _wipe_path
    from protocols.cli.instance_db.storage import StorageProvider, XDGPaths

    # Phase 1: WIPE
    print("\n\033[1m[Phase 1/5] WIPE\033[0m")
    targets = _collect_targets(scope)

    if not targets:
        print("  No existing data to wipe.")
    else:
        for label, path, size in targets:
            if dry_run:
                print(f"  \033[90m[dry-run]\033[0m Would delete {label}: {path} ({size})")
            else:
                _wipe_path(path, label)

    if dry_run:
        print("\n\033[90m[dry-run]\033[0m Stopping here. Remove --dry-run to execute.")
        return True

    # Phase 2: SCAFFOLD
    print("\n\033[1m[Phase 2/5] SCAFFOLD\033[0m")
    paths = XDGPaths.resolve()
    paths.ensure_dirs()
    print(f"  Created: {paths.data}/")
    print(f"  Created: {paths.config}/")
    print(f"  Created: {paths.cache}/")

    # Phase 3: TABLES
    print("\n\033[1m[Phase 3/5] TABLES\033[0m")

    # 3a: Instance tables via StorageProvider
    try:
        storage = await StorageProvider.from_config(None, paths)
        await storage.run_migrations()
        print("  Created instance tables (instances, shapes, dreams, ...)")
    except Exception as e:
        print(f"  \033[31mFailed to create instance tables: {e}\033[0m")
        return False

    # 3b: Model tables via SQLAlchemy
    try:
        from models.base import init_db
        await init_db()
        print("  Created model tables (brain_crystals, witness_marks, k_blocks, ...)")
    except Exception as e:
        print(f"  \033[31mFailed to create model tables: {e}\033[0m")
        return False

    # Phase 4: GENESIS (optional)
    if genesis:
        print("\n\033[1m[Phase 4/5] GENESIS\033[0m")
        try:
            from services.zero_seed.clean_slate_genesis import CleanSlateGenesis
            from services.k_block.zero_seed_storage import PostgresZeroSeedStorage

            # Get storage for genesis
            zero_storage = PostgresZeroSeedStorage()
            genesis_seeder = CleanSlateGenesis()
            result = await genesis_seeder.seed_clean_slate(zero_storage)

            print(f"  Seeded {result.total_created} K-Blocks")
            print(f"  L0 Axioms: {len(result.l0_ids)}")
            print(f"  L1 Kernel: {len(result.l1_ids)}")
            print(f"  L2 Principles: {len(result.l2_ids)}")
            print(f"  L3 Architecture: {len(result.l3_ids)}")
        except Exception as e:
            print(f"  \033[33mGenesis failed (non-fatal): {e}\033[0m")
    else:
        print("\n\033[90m[Phase 4/5] GENESIS - Skipped (use --genesis to enable)\033[0m")

    # Phase 5: VERIFY
    print("\n\033[1m[Phase 5/5] VERIFY\033[0m")
    # TODO: Call kg doctor internally when implemented
    print("  \033[32mReset complete!\033[0m")

    return True


@handler("reset", is_async=True, tier=1, description="Reset database to clean state")
async def cmd_reset(args: list[str]) -> int:
    """Handle reset command: Wipe and rebuild kgents database."""
    # Parse args
    force = False
    genesis = False
    scope = "global"
    dry_run = False

    for arg in args:
        if arg in ("--help", "-h"):
            _print_help()
            return 0
        elif arg in ("--force", "-f"):
            force = True
        elif arg in ("--genesis", "-g"):
            genesis = True
        elif arg in ("--all", "-a"):
            scope = "all"
        elif arg == "--dry-run":
            dry_run = True

    # Confirm unless --force or --dry-run
    if not force and not dry_run:
        print("\033[33mWARNING:\033[0m This will delete all kgents data and rebuild from scratch.")
        print()
        try:
            response = input("Type 'reset' to confirm: ")
            if response.strip().lower() != "reset":
                print("Aborted.")
                return 1
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return 1

    # Run reset
    success = await _run_reset(scope, genesis, dry_run)

    if success:
        print()
        print("\033[32m[kgents]\033[0m Database reset complete.")
        if not genesis:
            print("         Run 'kg reset --genesis' next time to include K-Blocks.")
        return 0
    else:
        print()
        print("\033[31m[kgents]\033[0m Reset failed. Check errors above.")
        return 1
```

#### 2.2 Register Handler

**File:** `protocols/cli/handlers/__init__.py`

Add import for reset handler.

#### 2.3 Add Tests

**File:** `protocols/cli/handlers/_tests/test_reset.py`

Mirror the structure of `test_wipe.py`:
- Test help flag
- Test dry-run mode
- Test force flag
- Test genesis flag
- Test full reset flow with mocked storage

---

### Phase 3: Doctor Command (3 hours)

**Goal:** Answer "is my kgents healthy?" definitively.

#### 3.1 Create Doctor Handler

**File:** `protocols/cli/handlers/doctor.py`

```python
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

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from protocols.cli.handler_meta import handler


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class CheckResult:
    name: str
    status: CheckStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    fix_hint: str | None = None


@dataclass
class DoctorReport:
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.PASS)

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.WARN)

    @property
    def failures(self) -> int:
        return sum(1 for c in self.checks if c.status == CheckStatus.FAIL)

    @property
    def healthy(self) -> bool:
        return self.failures == 0


async def check_global_db_exists() -> CheckResult:
    """Check if global database file exists."""
    from protocols.cli.instance_db.storage import XDGPaths

    paths = XDGPaths.resolve()
    db_path = paths.data / "membrane.db"

    if db_path.exists():
        size = db_path.stat().st_size
        size_str = f"{size / 1024 / 1024:.1f} MB" if size > 1024*1024 else f"{size / 1024:.1f} KB"
        return CheckResult(
            name="Global Database",
            status=CheckStatus.PASS,
            message=f"Exists at {db_path}",
            details={"path": str(db_path), "size": size, "size_str": size_str},
        )
    else:
        return CheckResult(
            name="Global Database",
            status=CheckStatus.FAIL,
            message=f"Not found at {db_path}",
            fix_hint="Run 'kg reset' to create database",
        )


async def check_tables_exist() -> CheckResult:
    """Check if all expected tables exist."""
    try:
        from models.base import get_engine, Base
        from sqlalchemy import inspect

        engine = get_engine()
        async with engine.connect() as conn:
            def get_tables(connection):
                inspector = inspect(connection)
                return set(inspector.get_table_names())

            existing = await conn.run_sync(get_tables)

        # Expected tables from SQLAlchemy models
        expected = set(Base.metadata.tables.keys())

        missing = expected - existing
        extra = existing - expected

        if not missing:
            return CheckResult(
                name="Database Tables",
                status=CheckStatus.PASS,
                message=f"All {len(expected)} tables present",
                details={"expected": len(expected), "existing": len(existing)},
            )
        else:
            return CheckResult(
                name="Database Tables",
                status=CheckStatus.FAIL,
                message=f"Missing {len(missing)} tables: {', '.join(sorted(missing)[:5])}{'...' if len(missing) > 5 else ''}",
                details={"missing": list(missing), "extra": list(extra)},
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
    """Check if genesis K-Blocks are seeded."""
    try:
        from models.base import get_async_session
        from sqlalchemy import text

        async with get_async_session() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM k_blocks WHERE id LIKE 'genesis:%'")
            )
            count = result.scalar() or 0

        if count >= 22:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.PASS,
                message=f"{count}/22 K-Blocks seeded",
                details={"count": count},
            )
        elif count > 0:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.WARN,
                message=f"Partial: {count}/22 K-Blocks",
                details={"count": count},
                fix_hint="Run 'kg reset --genesis' for full seeding",
            )
        else:
            return CheckResult(
                name="Genesis K-Blocks",
                status=CheckStatus.WARN,
                message="Not seeded (optional)",
                fix_hint="Run 'kg reset --genesis' to seed",
            )
    except Exception as e:
        return CheckResult(
            name="Genesis K-Blocks",
            status=CheckStatus.SKIP,
            message=f"Could not check: {e}",
        )


async def check_stale_instances() -> CheckResult:
    """Check for stale instance registrations."""
    try:
        from protocols.cli.instance_db.storage import StorageProvider, XDGPaths
        from datetime import datetime, timedelta

        paths = XDGPaths.resolve()
        storage = await StorageProvider.from_config(None, paths)

        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
        result = await storage.relational.fetch_all(
            "SELECT COUNT(*) as count FROM instances WHERE status = 'active' AND last_heartbeat < :cutoff",
            {"cutoff": cutoff},
        )

        stale_count = result[0]["count"] if result else 0

        if stale_count == 0:
            return CheckResult(
                name="Instance Registry",
                status=CheckStatus.PASS,
                message="No stale instances",
            )
        else:
            return CheckResult(
                name="Instance Registry",
                status=CheckStatus.WARN,
                message=f"{stale_count} stale instance(s)",
                details={"stale_count": stale_count},
                fix_hint="Run 'kg doctor --fix' to clean up",
            )
    except Exception as e:
        return CheckResult(
            name="Instance Registry",
            status=CheckStatus.SKIP,
            message=f"Could not check: {e}",
        )


async def check_xdg_directories() -> CheckResult:
    """Check if XDG directories exist and are writable."""
    from protocols.cli.instance_db.storage import XDGPaths

    paths = XDGPaths.resolve()
    issues = []

    for name, path in [
        ("data", paths.data),
        ("config", paths.config),
        ("cache", paths.cache),
    ]:
        if not path.exists():
            issues.append(f"{name} missing")
        elif not path.is_dir():
            issues.append(f"{name} not a directory")

    if not issues:
        return CheckResult(
            name="XDG Directories",
            status=CheckStatus.PASS,
            message="All directories present",
            details={
                "data": str(paths.data),
                "config": str(paths.config),
                "cache": str(paths.cache),
            },
        )
    else:
        return CheckResult(
            name="XDG Directories",
            status=CheckStatus.FAIL,
            message=f"Issues: {', '.join(issues)}",
            fix_hint="Run 'kg reset' to create directories",
        )


async def run_doctor(fix: bool = False) -> DoctorReport:
    """Run all health checks."""
    report = DoctorReport()

    # Run checks
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

    # TODO: Implement --fix for fixable issues

    return report


def _print_report(report: DoctorReport) -> None:
    """Print doctor report to console."""
    status_icons = {
        CheckStatus.PASS: "\033[32m✓\033[0m",
        CheckStatus.WARN: "\033[33m⚠\033[0m",
        CheckStatus.FAIL: "\033[31m✗\033[0m",
        CheckStatus.SKIP: "\033[90m○\033[0m",
    }

    print("\n\033[1m🔍 kgents Health Check\033[0m\n")

    for check in report.checks:
        icon = status_icons[check.status]
        print(f"  {icon} {check.name}: {check.message}")
        if check.fix_hint and check.status in (CheckStatus.WARN, CheckStatus.FAIL):
            print(f"      \033[90m→ {check.fix_hint}\033[0m")

    print()

    if report.healthy:
        if report.warnings:
            print(f"\033[32m✓ HEALTHY\033[0m ({report.warnings} warning{'s' if report.warnings != 1 else ''})")
        else:
            print("\033[32m✓ HEALTHY\033[0m")
    else:
        print(f"\033[31m✗ UNHEALTHY\033[0m ({report.failures} failure{'s' if report.failures != 1 else ''}, {report.warnings} warning{'s' if report.warnings != 1 else ''})")


def _print_help() -> None:
    """Print help for doctor command."""
    print("kgents doctor - Health check for kgents installation")
    print()
    print("USAGE: kgents doctor [options]")
    print()
    print("OPTIONS:")
    print("  --fix         Auto-fix issues that can be repaired")
    print("  --json        Output as JSON (for scripts)")
    print("  --help, -h    Show this help")
    print()
    print("CHECKS:")
    print("  - XDG directories exist and writable")
    print("  - Global database exists")
    print("  - All expected tables present")
    print("  - Genesis K-Blocks seeded (optional)")
    print("  - No stale instance registrations")


@handler("doctor", is_async=True, tier=1, description="Health check for kgents")
async def cmd_doctor(args: list[str]) -> int:
    """Handle doctor command: Comprehensive health check."""
    import json

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
```

---

### Phase 4: Consolidate Table Creation (1 hour)

**Goal:** Single source of truth for all tables.

#### 4.1 Update Lifecycle Bootstrap

**File:** `protocols/cli/instance_db/lifecycle.py`

In `bootstrap()` method, after running instance migrations:

```python
# Stage 5: Run migrations
try:
    await storage.run_migrations()

    # Also ensure SQLAlchemy model tables exist
    from models.base import init_db
    await init_db()

    if not initial_global_db_exists:
        self._signal_first_run(self._paths)
except Exception as e:
    errors.append(f"Migration failed: {e}")
```

#### 4.2 Document the Relationship

**File:** `docs/skills/unified-storage.md` (update existing)

Add section explaining the two-system relationship and why both are called.

---

## Testing Strategy

### Unit Tests

| Test | File | Coverage |
|------|------|----------|
| Reset dry-run | `test_reset.py` | Phase 1 only |
| Reset force | `test_reset.py` | Full flow, mocked storage |
| Reset genesis | `test_reset.py` | K-Block seeding |
| Doctor pass | `test_doctor.py` | All checks pass |
| Doctor fail | `test_doctor.py` | Missing tables |
| Doctor json | `test_doctor.py` | JSON output format |

### Integration Tests

```bash
# Full reset cycle
kg wipe global --force
kg reset --force --genesis
kg doctor --json | jq '.healthy'  # Should be true
```

### Property Tests

```python
@given(st.booleans(), st.booleans(), st.booleans())
def test_reset_flags_independent(force: bool, genesis: bool, all_scope: bool):
    """Reset flags should be independent and composable."""
    # Test that any combination of flags works
```

---

## Success Criteria

### Quantitative

| Metric | Target |
|--------|--------|
| Reset command time | < 5 seconds (no genesis) |
| Reset with genesis | < 15 seconds |
| Doctor command time | < 2 seconds |
| Test coverage | > 90% for new code |

### Qualitative

- [ ] `kg reset --force --genesis` works on fresh machine
- [ ] `kg doctor` gives clear pass/fail for each check
- [ ] No more "which init do I run?" confusion
- [ ] Help text is accurate and consistent

---

## Migration Path

### For Existing Users

No breaking changes. Existing commands (`kg wipe`, `/init-db` skill) continue to work.

### Deprecation Timeline

| Command | Status | Notes |
|---------|--------|-------|
| `kg wipe` | Keep | Still useful for wipe-only |
| `/init-db` skill | Keep | Still useful for table-only |
| `kg reset` | New | Preferred for fresh start |
| `kg doctor` | New | Preferred for health check |

---

## Open Questions

1. **Should `kg reset` require the API server?** Genesis currently needs HTTP endpoint. Could make it direct.

2. **Should `kg doctor --fix` auto-run `kg reset`?** Or just clean up stale instances?

3. **Add `kg reset --backup` flag?** Auto-backup before wipe?

---

## Timeline

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: Quick Wins | 30 min | None |
| Phase 2: Reset Command | 2 hr | Phase 1 |
| Phase 3: Doctor Command | 3 hr | Phase 2 |
| Phase 4: Consolidate | 1 hr | Phase 2 |

**Total: ~7 hours**

---

## References

- `protocols/cli/handlers/wipe.py` - Existing wipe implementation
- `protocols/cli/instance_db/lifecycle.py` - Bootstrap sequence
- `models/base.py` - SQLAlchemy init_db
- `services/zero_seed/clean_slate_genesis.py` - Genesis seeding
- `.claude/commands/init-db.md` - Current init-db skill

---

*"Tasteful > feature-complete. Joy-inducing > merely functional."*
