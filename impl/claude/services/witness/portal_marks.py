"""
Portal Marks: Witness integration for portal expansion events.

Bridges portal navigation (Context Perception) with witness marks,
enabling exploration trails to serve as evidence.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

Portal expansions ARE decisions. They reveal what the agent (or human)
thought was worth exploring. This is evidence that should be captured.

Significance Rules:
    - Depth 0: Root view → No mark (just viewing)
    - Depth 1: First expansion → No mark (exploratory)
    - Depth 2+: Deliberate investigation → YES, mark it
    - Following 'evidence' edge type → Always mark
    - Saving a trail → Always mark

See: plans/portal-fullstack-integration.md Phase 2
See: spec/protocols/context-perception.md

Teaching:
    gotcha: Portal marks are fire-and-forget. Errors are logged but
            never raised to caller. Portal UX should never block on
            witness mark emission.
            (Evidence: test_portal_marks.py::test_errors_dont_propagate)

    gotcha: Depth 1 expansions are NOT marked. This prevents noise from
            exploratory clicks. Only depth 2+ shows deliberate interest.
            (Evidence: test_portal_marks.py::test_depth_1_not_marked)
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from .bus import WitnessTopics, get_synergy_bus
from .mark import (
    Mark,
    MarkId,
    NPhase,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)

if TYPE_CHECKING:
    from protocols.agentese.contexts.self_context import Trail

logger = logging.getLogger(__name__)


# =============================================================================
# Portal Expansion Marks
# =============================================================================


async def mark_portal_expansion(
    file_path: str,
    edge_type: str,
    portal_path: list[str],
    depth: int,
    observer_archetype: str,
) -> str | None:
    """
    Emit a witness mark for a portal expansion.

    Records deliberate exploration (depth >= 2) as evidence that can
    be used for trail reconstruction and commitment support.

    Args:
        file_path: Path to the source file being explored
        edge_type: Type of edge expanded (imports, tests, calls, etc.)
        portal_path: List of path segments (e.g., ["imports", "pathlib"])
        depth: Current depth in portal tree (0 = root, 1 = first level, etc.)
        observer_archetype: Observer archetype (developer, reviewer, etc.)

    Returns:
        mark_id if emitted, None if skipped (depth < 2) or on error.

    Note:
        Fire-and-forget: errors are logged, never raised.
        Portal UX should never block on witness integration.
    """
    # Depth 1 = exploratory, depth 2+ = deliberate
    # Exception: "evidence" edge type always marks
    if depth < 2 and edge_type != "evidence":
        logger.debug(f"Portal expansion at depth {depth} - skipping mark (exploratory)")
        return None

    try:
        mark_id = generate_mark_id()
        portal_path_str = "/".join(portal_path)

        # Create the mark
        mark = Mark(
            id=mark_id,
            origin="context_perception",
            stimulus=Stimulus(
                kind="portal",
                content=f"Expanded [{edge_type}] at {portal_path_str}",
                source="self.portal",
                metadata={
                    "file_path": file_path,
                    "edge_type": edge_type,
                    "portal_path": portal_path,
                    "depth": depth,
                },
            ),
            response=Response(
                kind="exploration",
                content=f"Navigated to depth {depth} via [{edge_type}]",
                success=True,
                metadata={"observer_archetype": observer_archetype},
            ),
            umwelt=UmweltSnapshot(
                observer_id=observer_archetype,
                role="explorer",
                capabilities=frozenset({"navigate", "expand", "collapse"}),
                perceptions=frozenset({"portal_tree", "source_code"}),
            ),
            phase=NPhase.SENSE,  # Exploration is sensing
            tags=("portal", "expansion", edge_type),
            metadata={
                "action": "exploration.portal.expand",
                "file_path": file_path,
                "edge_type": edge_type,
                "portal_path": portal_path,
                "depth": depth,
                "observer_archetype": observer_archetype,
                "evidence_strength": "weak" if depth < 3 else "moderate",
            },
        )

        # Emit to bus (fire-and-forget)
        bus = get_synergy_bus()
        await bus.publish(
            WitnessTopics.TRAIL_CAPTURED,
            {
                "mark_id": str(mark_id),
                "action": "exploration.portal.expand",
                "file_path": file_path,
                "edge_type": edge_type,
                "portal_path": portal_path,
                "depth": depth,
                "observer_archetype": observer_archetype,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.debug(
            f"Portal expansion marked: {mark_id} [{edge_type}] depth={depth} path={portal_path_str}"
        )
        return str(mark_id)

    except Exception as e:
        # Fire-and-forget: log error, return None, never raise
        logger.warning(f"Failed to emit portal expansion mark: {e}")
        return None


# =============================================================================
# Trail Save Marks
# =============================================================================


async def mark_trail_save(
    trail: "Trail",
    name: str | None = None,
) -> str | None:
    """
    Emit a witness mark when a trail is saved.

    Uses the existing trail_bridge.py for full trail → mark conversion,
    then emits to the witness bus.

    Args:
        trail: The Trail being saved
        name: Optional name override for the trail

    Returns:
        mark_id if emitted, None on error.

    Note:
        Fire-and-forget: errors are logged, never raised.
    """
    try:
        from .trail_bridge import emit_trail_as_mark

        # Use existing infrastructure
        trail_mark = await emit_trail_as_mark(trail)

        logger.debug(
            f"Trail save marked: {trail_mark.id} name='{trail.name}' steps={len(trail.steps)}"
        )
        return str(trail_mark.id)

    except Exception as e:
        # Fire-and-forget: log error, return None, never raise
        logger.warning(f"Failed to emit trail save mark: {e}")
        return None


# =============================================================================
# Batch Operations (Future)
# =============================================================================


async def mark_portal_collapse(
    file_path: str,
    portal_path: list[str],
    depth: int,
    observer_archetype: str,
) -> str | None:
    """
    Emit a witness mark for a portal collapse.

    Collapses are less significant than expansions, but still recorded
    at depth 3+ to track deliberate navigation.

    Args:
        file_path: Path to the source file
        portal_path: Path segments being collapsed
        depth: Depth of the collapsed node
        observer_archetype: Observer archetype

    Returns:
        mark_id if emitted, None if skipped or on error.
    """
    # Collapses only marked at depth 3+ (even less signal than expand)
    if depth < 3:
        return None

    try:
        mark_id = generate_mark_id()
        portal_path_str = "/".join(portal_path)

        bus = get_synergy_bus()
        await bus.publish(
            WitnessTopics.TRAIL_CAPTURED,
            {
                "mark_id": str(mark_id),
                "action": "exploration.portal.collapse",
                "file_path": file_path,
                "portal_path": portal_path,
                "depth": depth,
                "observer_archetype": observer_archetype,
                "timestamp": datetime.now().isoformat(),
            },
        )

        logger.debug(f"Portal collapse marked: {mark_id} path={portal_path_str}")
        return str(mark_id)

    except Exception as e:
        logger.warning(f"Failed to emit portal collapse mark: {e}")
        return None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "mark_portal_expansion",
    "mark_portal_collapse",
    "mark_trail_save",
]
