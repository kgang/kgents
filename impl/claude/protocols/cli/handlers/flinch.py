"""
Flinch Handler: Test failure analysis from accumulated algedonic signals.

Trust Loop Integration - Horizon 1.

The FlinchStore captures test failures to .kgents/ghost/test_flinches.jsonl.
This command surfaces that data for analysis.

Usage:
    kgents flinch              # Summarize recent test failures
    kgents flinch --patterns   # Show recurring failure patterns
    kgents flinch --hot        # Files with highest failure rate
    kgents flinch --recent N   # Show N most recent failures
    kgents flinch --since 1h   # Failures since 1 hour ago

Example:
    $ kgents flinch
    [FLINCH] Test Failure Summary
    Total: 820 failures recorded
    Last hour: 0
    Last 24h: 5

    Hot files:
      test_foo.py: 32 failures
      test_bar.py: 18 failures

    $ kgents flinch --patterns
    [FLINCH] Recurring Failure Patterns

    test_graph.py (32 failures)
      Most common: test_setup_fixture (28 times)
      Pattern: Setup phase failures suggest fixture issue

Trust Signal: The system noticed patterns in your test failures.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


def cmd_flinch(args: list[str]) -> int:
    """
    Analyze test failures from FlinchStore.

    Surfaces patterns from accumulated algedonic signals.
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    patterns_mode = "--patterns" in args
    hot_mode = "--hot" in args
    recent_mode = "--recent" in args

    if help_mode:
        print(__doc__)
        return 0

    # Get project root (look for .kgents directory or HYDRATE.md)
    from protocols.cli.hollow import find_kgents_root

    project_root = find_kgents_root()
    if project_root is None:
        # Try to find the repo root by looking for HYDRATE.md
        current = Path.cwd()
        while current != current.parent:
            if (current / "HYDRATE.md").exists() or (current / ".kgents").exists():
                project_root = current
                break
            current = current.parent
        if project_root is None:
            project_root = Path.cwd()

    flinch_path = project_root / ".kgents" / "ghost" / "test_flinches.jsonl"

    if not flinch_path.exists():
        print("[FLINCH] No flinch data found")
        print(f"  Expected: {flinch_path}")
        print()
        print("Run tests with pytest to generate flinch data.")
        return 0

    if patterns_mode:
        return _show_patterns(flinch_path)
    elif hot_mode:
        return _show_hot_files(flinch_path)
    elif recent_mode:
        # Get count from args
        try:
            idx = args.index("--recent")
            count = int(args[idx + 1]) if idx + 1 < len(args) else 10
        except (ValueError, IndexError):
            count = 10
        return _show_recent(flinch_path, count)
    else:
        return _show_summary(flinch_path)


def _show_summary(flinch_path: Path) -> int:
    """Show flinch summary."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    result = asyncio.run(collector.collect())

    if not result.success:
        print(f"[FLINCH] Error: {result.error}")
        return 1

    data = result.data

    print("[FLINCH] Test Failure Summary")
    print("=" * 40)
    print(f"Total failures: {data.get('total', 0)}")
    print(f"Last hour: {data.get('last_hour', 0)}")
    print(f"Last 24h: {data.get('last_24h', 0)}")
    print()

    hot_files = data.get("hot_files", [])
    if hot_files:
        print("Hot files (most failures):")
        for file_path, count in hot_files[:5]:
            print(f"  {file_path}: {count} failures")
        print()

    recurring = data.get("top_recurring", [])
    if recurring:
        print("Recurring failures:")
        for test, count in recurring[:5]:
            # Truncate long test names
            if len(test) > 60:
                test = "..." + test[-57:]
            print(f"  {test}: {count}x")
        print()

    # Trust signal
    last_hour = data.get("last_hour", 0)
    if last_hour > 0:
        print(f"[ALERT] {last_hour} failures in the last hour!")
    elif data.get("total", 0) > 0:
        print("[OK] No recent failures (last hour)")

    return 0


def _show_patterns(flinch_path: Path) -> int:
    """Show recurring failure patterns."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    patterns_data = collector.get_patterns()

    print("[FLINCH] Recurring Failure Patterns")
    print("=" * 40)
    print(f"Total flinches: {patterns_data.get('total_flinches', 0)}")
    print(
        f"Modules with failures: {patterns_data.get('total_modules_with_failures', 0)}"
    )
    print()

    patterns = patterns_data.get("patterns", [])
    if not patterns:
        print("No recurring patterns detected (threshold: 3+ failures)")
        return 0

    print("Patterns (3+ failures):")
    print()

    for p in patterns[:10]:
        module = p["module"]
        total = p["total_failures"]
        most_common = p["most_common_test"]
        most_count = p["most_common_count"]

        print(f"  {module}")
        print(f"    Total failures: {total}")
        print(f"    Most common test: {most_common} ({most_count}x)")

        # Infer pattern type
        if "setup" in most_common.lower() or "fixture" in most_common.lower():
            print("    Pattern: Setup/fixture failures - check test infrastructure")
        elif "timeout" in most_common.lower():
            print("    Pattern: Timeout failures - check async handling")
        elif "stream" in most_common.lower() or "parse" in most_common.lower():
            print("    Pattern: Parsing failures - check input handling")
        print()

    return 0


def _show_hot_files(flinch_path: Path) -> int:
    """Show files with highest failure rate."""
    from infra.ghost.collectors import FlinchCollector

    collector = FlinchCollector(flinch_path=flinch_path)
    hot_files = collector.get_hot_files(limit=20)

    print("[FLINCH] Hot Files (Most Failures)")
    print("=" * 40)

    if not hot_files:
        print("No failure data available")
        return 0

    # Calculate max for bar chart
    max_count = hot_files[0][1] if hot_files else 1

    for file_path, count in hot_files:
        # Visual bar
        bar_width = int((count / max_count) * 30)
        bar = "#" * bar_width

        # Truncate long paths
        if len(file_path) > 50:
            file_path = "..." + file_path[-47:]

        print(f"  {file_path}")
        print(f"    {count:4d} {bar}")

    print()
    print("Suggestion: Focus on the hottest files to reduce failure rate.")

    return 0


def _show_recent(flinch_path: Path, count: int) -> int:
    """Show N most recent failures."""
    print(f"[FLINCH] {count} Most Recent Failures")
    print("=" * 40)

    # Parse JSONL directly for recent entries
    flinches: list[dict[str, Any]] = []
    with open(flinch_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    flinches.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # Sort by timestamp descending
    flinches.sort(key=lambda x: x.get("ts", 0), reverse=True)

    if not flinches:
        print("No failures recorded")
        return 0

    for flinch_entry in flinches[:count]:
        ts = flinch_entry.get("ts", 0)
        test = flinch_entry.get("test", "unknown")
        phase = flinch_entry.get("phase", "call")
        duration = flinch_entry.get("duration", 0)

        # Format timestamp
        if ts:
            dt = datetime.fromtimestamp(ts)
            ts_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            ts_str = "unknown"

        # Truncate long test names
        if len(test) > 70:
            test = "..." + test[-67:]

        print(f"  [{ts_str}] {test}")
        print(f"    Phase: {phase}, Duration: {duration:.3f}s")
        print()

    return 0
