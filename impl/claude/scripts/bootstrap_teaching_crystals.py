#!/usr/bin/env python3
"""
Bootstrap Teaching Crystals: One-time crystallization of all teaching moments.

This script crystallizes all ~165 teaching moments from Living Docs into Brain,
implementing the Memory-First Documentation protocol.

Usage:
    uv run python scripts/bootstrap_teaching_crystals.py [--dry-run]

Options:
    --dry-run    Preview without persisting (shows first 10 teaching moments)

Teaching:
    gotcha: Run with --dry-run first to preview without persistence.
            (Evidence: this script)

See: plans/memory-first-docs-execution.md (Phase 2B.1)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.living_docs import TeachingCollector


async def main(dry_run: bool = False) -> int:
    """
    Bootstrap all teaching moments to Brain.

    Args:
        dry_run: If True, preview without persisting

    Returns:
        Exit code (0 = success)
    """
    collector = TeachingCollector()
    teachings = list(collector.collect_all())

    print(f"Found {len(teachings)} teaching moments")
    print()

    if dry_run:
        print("=== DRY RUN MODE ===")
        print()

        # Group by severity for summary
        by_severity = {"critical": 0, "warning": 0, "info": 0}
        for t in teachings:
            by_severity[t.moment.severity] += 1

        print("By Severity:")
        print(f"  Critical: {by_severity['critical']}")
        print(f"  Warning:  {by_severity['warning']}")
        print(f"  Info:     {by_severity['info']}")
        print()

        print("Sample (first 10):")
        print("-" * 60)
        for t in teachings[:10]:
            icon = {"critical": "\U0001f6a8", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}.get(
                t.moment.severity, "\u2022"
            )
            print(f"{icon} [{t.moment.severity}] {t.module}::{t.symbol}")
            print(f"   {t.moment.insight[:70]}...")
            if t.moment.evidence:
                print(f"   Evidence: {t.moment.evidence}")
            print()

        if len(teachings) > 10:
            print(f"... and {len(teachings) - 10} more")

        print()
        print("Run without --dry-run to persist to Brain.")
        return 0

    # Actual crystallization
    print("Crystallizing to Brain...")
    print()

    try:
        # Initialize the bootstrap services
        import os

        os.environ.setdefault(
            "KGENTS_DATABASE_URL",
            "postgresql+asyncpg://kgents:kgents@localhost:5432/kgents",
        )

        from services.bootstrap import bootstrap_services, get_service

        await bootstrap_services()

        # Get brain persistence and crystallize
        brain = await get_service("brain_persistence")

        from services.living_docs.crystallizer import TeachingCrystallizer

        crystallizer = TeachingCrystallizer(brain=brain)
        stats = await crystallizer.crystallize_all()

        print("Crystallization Complete")
        print("=" * 40)
        print(f"Total found:        {stats.total_found}")
        print(f"Newly crystallized: {stats.newly_crystallized}")
        print(f"Already existed:    {stats.already_existed}")
        print(f"With evidence:      {stats.with_evidence}")
        print()
        print("By Severity:")
        print(f"  Critical: {stats.by_severity.get('critical', 0)}")
        print(f"  Warning:  {stats.by_severity.get('warning', 0)}")
        print(f"  Info:     {stats.by_severity.get('info', 0)}")

        if stats.errors:
            print()
            print(f"\u26a0\ufe0f Errors ({len(stats.errors)}):")
            for error in stats.errors[:5]:
                print(f"  - {error}")
            if len(stats.errors) > 5:
                print(f"  ... and {len(stats.errors) - 5} more")
            return 1

        print()
        print("\u2705 Bootstrap complete!")
        return 0

    except Exception as e:
        print(f"\u274c Error during crystallization: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    exit_code = asyncio.run(main(dry_run=dry_run))
    sys.exit(exit_code)
