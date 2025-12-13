"""
Fixture Handler: Manage HotData fixtures.

DevEx Infrastructure Layer - AD-004 (Pre-Computed Richness).

Philosophy: LLM-once is cheap. Pre-compute rich data, hotload forever.
Demo kgents ARE kgents.

Usage:
    kg fixture list              # List all registered fixtures with status
    kg fixture list --stale      # List only stale/missing fixtures
    kg fixture refresh <name>    # Refresh a specific fixture
    kg fixture refresh --all     # Refresh all stale fixtures
    kg fixture validate          # Validate fixtures against schemas
    kg fixture info <name>       # Show detailed info for a fixture
    kg fixture --help            # Show this help

Example output:
    [FIXTURES] 12 registered | 10 fresh | 2 stale

    demo_snapshot           FRESH    0.3s ago    fixtures/agent_snapshots/demo.json
    soul_deliberating       STALE    2.1h ago    fixtures/agent_snapshots/soul_deliberating.json
    garden_main            MISSING   -           fixtures/garden_states/main.json
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_fixture(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Manage HotData fixtures.

    Subcommands:
        list      List all registered fixtures
        refresh   Refresh stale fixtures
        validate  Validate fixture schemas
        info      Show detailed fixture info
    """
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("fixture", args)
        except ImportError:
            pass

    # Parse subcommand
    if not args or args[0] in ("--help", "-h"):
        print(__doc__)
        return 0

    subcommand = args[0]
    subargs = args[1:]

    if subcommand == "list":
        return _cmd_list(subargs, ctx)
    elif subcommand == "refresh":
        return _cmd_refresh(subargs, ctx)
    elif subcommand == "validate":
        return _cmd_validate(subargs, ctx)
    elif subcommand == "info":
        return _cmd_info(subargs, ctx)
    else:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kg fixture --help' for usage.")
        return 1


def _cmd_list(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """List all registered fixtures."""
    from shared.hotdata import FIXTURES_DIR, get_hotdata_registry

    stale_only = "--stale" in args
    json_mode = "--json" in args

    registry = get_hotdata_registry()
    all_names = registry.list_all()
    stale_names = registry.list_stale()
    missing_names = registry.list_missing()

    if not all_names:
        print("[FIXTURES] No fixtures registered.")
        print()
        print("Fixtures are auto-registered when demo modules are imported.")
        print("Try running a demo app first: kg dashboard")
        return 0

    # Build status info
    fixtures_info = []
    for name in sorted(all_names):
        status = registry.get_status(name)
        if status.get("error"):
            continue

        info = {
            "name": name,
            "exists": status["exists"],
            "fresh": status["fresh"],
            "age_seconds": status["age_seconds"],
            "path": status["path"],
            "has_generator": status["has_generator"],
        }

        # Determine status label
        if not status["exists"]:
            info["status"] = "MISSING"
        elif status["fresh"]:
            info["status"] = "FRESH"
        else:
            info["status"] = "STALE"

        fixtures_info.append(info)

    # Filter if stale-only
    if stale_only:
        fixtures_info = [f for f in fixtures_info if f["status"] != "FRESH"]

    # JSON output
    if json_mode:
        output = {
            "total": len(all_names),
            "fresh": len(all_names) - len(stale_names) - len(missing_names),
            "stale": len(stale_names),
            "missing": len(missing_names),
            "fixtures": fixtures_info,
        }
        print(json.dumps(output, indent=2, default=str))
        return 0

    # Human output
    fresh_count = len(all_names) - len(stale_names) - len(missing_names)
    print(
        f"[FIXTURES] {len(all_names)} registered | "
        f"{fresh_count} fresh | "
        f"{len(stale_names)} stale | "
        f"{len(missing_names)} missing"
    )
    print()

    if not fixtures_info:
        if stale_only:
            print("  All fixtures are fresh!")
        return 0

    # Column headers
    print(f"{'NAME':<30} {'STATUS':<10} {'AGE':<12} PATH")
    print("-" * 80)

    for info in fixtures_info:
        name = info["name"][:28]
        status = info["status"]
        age = info["age_seconds"]

        # Format age
        if age is None:
            age_str = "-"
        elif age < 60:
            age_str = f"{age:.1f}s ago"
        elif age < 3600:
            age_str = f"{age / 60:.1f}m ago"
        else:
            age_str = f"{age / 3600:.1f}h ago"

        # Relative path
        path = info["path"]
        try:
            rel_path = Path(path).relative_to(FIXTURES_DIR.parent)
        except ValueError:
            rel_path = Path(path)

        # Status color (ANSI)
        if status == "FRESH":
            status_colored = f"\033[32m{status}\033[0m"  # Green
        elif status == "STALE":
            status_colored = f"\033[33m{status}\033[0m"  # Yellow
        else:
            status_colored = f"\033[31m{status}\033[0m"  # Red

        print(f"{name:<30} {status_colored:<19} {age_str:<12} {rel_path}")

    print()
    print("Use 'kg fixture refresh <name>' to refresh a specific fixture.")
    print("Use 'kg fixture refresh --all' to refresh all stale fixtures.")

    return 0


def _cmd_refresh(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Refresh fixtures."""
    from shared.hotdata import get_hotdata_registry

    refresh_all = "--all" in args
    force = "--force" in args
    dry_run = "--dry-run" in args

    registry = get_hotdata_registry()

    # Filter out flags to get fixture names
    names = [a for a in args if not a.startswith("--")]

    if refresh_all:
        names = registry.list_stale()
        if not names:
            print("[FIXTURES] All fixtures are fresh!")
            return 0
        print(f"[FIXTURES] Refreshing {len(names)} stale fixtures...")
    elif not names:
        print("Usage: kg fixture refresh <name> [--force]")
        print("       kg fixture refresh --all [--force]")
        return 1

    # Refresh each fixture
    for name in names:
        hd = registry.get(name)
        if hd is None:
            print(f"  [SKIP] Unknown fixture: {name}")
            continue

        status = registry.get_status(name)
        if not status.get("has_generator"):
            print(f"  [SKIP] No generator for: {name}")
            continue

        if dry_run:
            print(f"  [DRY-RUN] Would refresh: {name}")
            continue

        try:
            print(f"  [REFRESHING] {name}...")
            asyncio.run(registry.refresh(name, force=force))
            print(f"  [OK] {name} refreshed")
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    return 0


def _cmd_validate(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Validate fixture schemas."""
    from shared.hotdata import get_hotdata_registry

    registry = get_hotdata_registry()
    all_names = registry.list_all()

    if not all_names:
        print("[FIXTURES] No fixtures registered.")
        return 0

    print(f"[FIXTURES] Validating {len(all_names)} fixtures...")
    print()

    errors = []
    valid = 0

    for name in sorted(all_names):
        hd = registry.get(name)
        if hd is None:
            continue

        if not hd.exists():
            print(f"  [SKIP] {name}: file missing")
            continue

        try:
            # Try to load and validate
            hd.load()  # Validates JSON structure
            print(f"  [OK] {name}")
            valid += 1
        except json.JSONDecodeError as e:
            print(f"  [ERROR] {name}: Invalid JSON - {e}")
            errors.append((name, f"Invalid JSON: {e}"))
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")
            errors.append((name, str(e)))

    print()
    print(f"[RESULT] {valid} valid, {len(errors)} errors")

    return 1 if errors else 0


def _cmd_info(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Show detailed info for a fixture."""
    from shared.hotdata import FIXTURES_DIR, get_hotdata_registry

    if not args or args[0].startswith("--"):
        print("Usage: kg fixture info <name>")
        return 1

    name = args[0]
    json_mode = "--json" in args

    registry = get_hotdata_registry()
    status = registry.get_status(name)

    if status.get("error"):
        print(f"[ERROR] {status['error']}")
        return 1

    if json_mode:
        print(json.dumps(status, indent=2, default=str))
        return 0

    print(f"[FIXTURE] {name}")
    print()
    print(f"  Path:          {status['path']}")
    print(f"  Exists:        {'Yes' if status['exists'] else 'No'}")
    print(f"  Fresh:         {'Yes' if status['fresh'] else 'No'}")
    print(f"  Has Generator: {'Yes' if status['has_generator'] else 'No'}")

    if status["age_seconds"] is not None:
        age = status["age_seconds"]
        if age < 60:
            age_str = f"{age:.1f} seconds"
        elif age < 3600:
            age_str = f"{age / 60:.1f} minutes"
        else:
            age_str = f"{age / 3600:.1f} hours"
        print(f"  Age:           {age_str}")

    # Show file content summary if exists
    hd = registry.get(name)
    if hd and hd.exists():
        try:
            content = Path(status["path"]).read_text()
            data = json.loads(content)
            print()
            print("  Content Preview:")
            # Show top-level keys
            if isinstance(data, dict):
                for key in list(data.keys())[:5]:
                    value = data[key]
                    if isinstance(value, str):
                        preview = value[:40] + "..." if len(value) > 40 else value
                    elif isinstance(value, (list, dict)):
                        preview = f"{type(value).__name__} ({len(value)} items)"
                    else:
                        preview = str(value)
                    print(f"    {key}: {preview}")
        except Exception:
            pass

    return 0


# Convenience aliases
def cmd_fixture_list(args: Any) -> int:
    """List all fixtures."""
    return _cmd_list(args)


def cmd_fixture_refresh(args: Any) -> int:
    """Refresh all fixtures."""
    return _cmd_refresh(args)


def cmd_fixture_validate(args: Any) -> int:
    """Validate all fixtures."""
    return _cmd_validate(args)
