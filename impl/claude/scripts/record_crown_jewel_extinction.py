#!/usr/bin/env python3
"""
Record the 2025-12-21 Crown Jewel Cleanup as an ExtinctionEvent.

This is a one-time script to capture the mass deletion that happened
during the AD-009 Metaphysical Fullstack simplification.

Run once:
    uv run python scripts/record_crown_jewel_extinction.py

Teaching:
    gotcha: This script is idempotent—running it twice won't create duplicates.
            It checks for existing event by commit hash before creating.
            (Evidence: this script)

See: plans/memory-first-docs-execution.md (Phase 3.2)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add impl/claude to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# The Crown Jewel Cleanup metadata
# These modules were deleted on 2025-12-21 as part of AD-009
CROWN_JEWEL_CLEANUP = {
    "reason": "Crown Jewel Cleanup - AD-009 Metaphysical Fullstack",
    "commit": "12209627",  # refactor: Remove world.emergence route, node, and frontend
    "decision_doc": "spec/principles/decisions/AD-009-metaphysical-fullstack.md",
    "deleted_paths": [
        "services/town/",
        "services/park/",
        "services/gestalt/",
        "services/forge/",
        "services/chat/",
        "services/archaeology/",
        "services/coalition/",
        "services/muse/",
        "services/gardener/",
    ],
    "successor_map": {
        # Most concepts were removed entirely
        "services/town": None,  # Concept removed
        "services/park": None,  # Concept removed
        "services/gestalt": None,  # Concept removed
        "services/forge": None,  # Concept removed
        "services/coalition": None,  # Concept removed
        "services/muse": None,  # Concept removed
        # Some functionality migrated
        "services/chat": "services.brain.conversation",
        "services/archaeology": "services.living_docs.temporal",
        "services/gardener": "protocols.ashc",
    },
}


async def main() -> int:
    """
    Record the Crown Jewel Cleanup extinction event.

    Returns:
        Exit code (0 = success)
    """
    print("Recording Crown Jewel Cleanup Extinction Event")
    print("=" * 50)
    print()
    print(f"Reason: {CROWN_JEWEL_CLEANUP['reason']}")
    print(f"Commit: {CROWN_JEWEL_CLEANUP['commit']}")
    print(f"Decision Doc: {CROWN_JEWEL_CLEANUP['decision_doc']}")
    print()
    print("Deleted Paths:")
    for path in CROWN_JEWEL_CLEANUP["deleted_paths"]:
        successor = CROWN_JEWEL_CLEANUP["successor_map"].get(path.rstrip("/"), "N/A")
        successor_str = successor if successor else "(concept removed)"
        print(f"  - {path} -> {successor_str}")
    print()

    try:
        # Initialize the bootstrap services
        import os

        # Default for local Docker development - override via KGENTS_DATABASE_URL
        os.environ.setdefault(
            "KGENTS_DATABASE_URL",
            "postgresql+asyncpg://kgents:kgents@localhost:5432/kgents",
        )

        from services.bootstrap import bootstrap_services, get_service

        await bootstrap_services()
        brain = await get_service("brain_persistence")

        # Check if event already exists (by commit prefix)
        existing_events = await brain.get_extinction_events(limit=100)
        for event in existing_events:
            if event.commit.startswith(CROWN_JEWEL_CLEANUP["commit"]):
                print(f"\u26a0\ufe0f  Event already exists: {event.id}")
                print("    (This script is idempotent)")
                return 0

        # Record the extinction
        result = await brain.prepare_extinction(
            reason=CROWN_JEWEL_CLEANUP["reason"],
            commit=CROWN_JEWEL_CLEANUP["commit"],
            deleted_paths=CROWN_JEWEL_CLEANUP["deleted_paths"],
            decision_doc=CROWN_JEWEL_CLEANUP["decision_doc"],
            successor_map=CROWN_JEWEL_CLEANUP["successor_map"],
        )

        print("Extinction Recorded")
        print("-" * 50)
        print(f"Event ID:       {result.event_id}")
        print(f"Affected:       {result.affected_count} teaching crystals")
        print(f"Preserved:      {result.preserved_count} teaching crystals")
        print()
        print("\u2705 Crown Jewel Cleanup recorded as extinction event")
        print()
        print("To view:")
        print(f"  kg brain extinct show {result.event_id}")
        print("  kg void.extinct.wisdom services.town")

        return 0

    except Exception as e:
        print(f"\u274c Error recording extinction: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
