"""
WARP Primitive → SceneGraph Converters.

Converts WARP primitives (TraceNode, Walk, Ritual, etc.) into SceneGraph
representations for projection to React, CLI, or future Servo targets.

The Insight (from spec/protocols/warp-primitives.md):
    "The webapp is not the UI. The webapp is the composition boundary."

Design Philosophy:
    - Each WARP primitive has a single canonical converter
    - Converters are pure functions (no side effects)
    - Style is declarative (Living Earth palette hints, not CSS)
    - Composition via SceneGraph >> operator

See:
    - protocols/agentese/projection/scene.py (SceneGraph primitives)
    - services/witness/trace_node.py (TraceNode)
    - services/witness/walk.py (Walk)
    - docs/skills/crown-jewel-patterns.md (Pattern 6: Dual-Channel Output)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Sequence

from .scene import (
    Interaction,
    LayoutDirective,
    LayoutMode,
    NodeStyle,
    SceneEdge,
    SceneGraph,
    SceneNode,
    SceneNodeKind,
)

if TYPE_CHECKING:
    from services.witness.covenant import Covenant
    from services.witness.offering import Offering
    from services.witness.ritual import Ritual
    from services.witness.trace_node import TraceNode
    from services.witness.walk import Walk


# =============================================================================
# Living Earth Palette (from crown-jewels-genesis-moodboard.md)
# =============================================================================


@dataclass(frozen=True)
class LivingEarthPalette:
    """
    The Living Earth color palette.

    From moodboard:
        "Warm, breathing machinery"
        "Watercolor textures, hand-made softness"
        "Data flows like water through vines"

    These are semantic color names that projection targets interpret.
    """

    # Earth tones
    COPPER: str = "copper"  # #b87333 - Atelier, crafting
    SAGE: str = "sage"  # #9caf88 - Park, growth
    SOIL: str = "soil"  # #5c4033 - Domain, grounding
    PAPER: str = "paper"  # #f5f5dc - Background, canvas

    # Living accents
    LIVING_GREEN: str = "living_green"  # #4a7c59 - Gestalt, vitality
    AMBER_GLOW: str = "amber_glow"  # #ffbf00 - Coalition, energy
    TWILIGHT: str = "twilight"  # #5d4e6d - Void, mystery

    # Status colors (semantic, not RGB)
    SUCCESS: str = "success"
    WARNING: str = "warning"
    ERROR: str = "error"


PALETTE = LivingEarthPalette()


# =============================================================================
# Hex Values for CSS (Projection Target: React)
# =============================================================================

PALETTE_HEX: dict[str, str] = {
    "copper": "#b87333",
    "sage": "#9caf88",
    "soil": "#5c4033",
    "paper": "#f5f5dc",
    "living_green": "#4a7c59",
    "amber_glow": "#ffbf00",
    "twilight": "#5d4e6d",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "error": "#f87171",
}


def palette_to_hex(color: str) -> str:
    """Convert palette color name to hex value."""
    return PALETTE_HEX.get(color, color)


# =============================================================================
# TraceNode → SceneGraph
# =============================================================================


def trace_node_to_scene(trace: TraceNode, *, animate: bool = True) -> SceneNode:
    """
    Convert a TraceNode to a SceneNode.

    The TraceNode becomes a TRACE-kind SceneNode with:
    - Stimulus displayed as label
    - Response in content
    - Fade animation on appearance
    - Sage background (trace items live in the garden)

    Args:
        trace: The TraceNode to convert
        animate: Whether to include animation hints

    Returns:
        SceneNode ready for projection
    """
    # Truncate stimulus for label
    stimulus_preview = trace.stimulus.content
    if len(stimulus_preview) > 40:
        stimulus_preview = stimulus_preview[:37] + "..."

    style = NodeStyle(
        background=PALETTE.SAGE,
        paper_grain=True,
        breathing=animate and trace.response.success,  # Only breathe if successful
    )

    return SceneNode(
        kind=SceneNodeKind.TRACE,
        content={
            "trace_id": str(trace.id),
            "origin": trace.origin,
            "stimulus": trace.stimulus.to_dict(),
            "response": trace.response.to_dict(),
            "timestamp": trace.timestamp.isoformat(),
            "phase": trace.phase.value if trace.phase else None,
            "tags": list(trace.tags),
        },
        label=stimulus_preview,
        style=style,
        metadata={
            "trace_id": str(trace.id),
            "origin": trace.origin,
            "success": trace.response.success,
        },
    )


def trace_timeline_to_scene(
    traces: Sequence[TraceNode],
    *,
    title: str = "Trace Timeline",
    show_edges: bool = True,
) -> SceneGraph:
    """
    Convert a sequence of TraceNodes to a timeline SceneGraph.

    Creates a horizontal timeline with:
    - Each trace as a TRACE node
    - Causal edges between sequential traces
    - Timeline layout directive

    Args:
        traces: Sequence of TraceNodes (ordered by time)
        title: Title for the scene
        show_edges: Whether to include causal edges

    Returns:
        SceneGraph with timeline layout
    """
    if not traces:
        return SceneGraph.empty()

    nodes = [trace_node_to_scene(t) for t in traces]
    edges: list[SceneEdge] = []

    if show_edges:
        for i in range(len(nodes) - 1):
            edges.append(
                SceneEdge(
                    source=nodes[i].id,
                    target=nodes[i + 1].id,
                    label="",
                    style="solid",
                    metadata={"relation": "causal"},
                )
            )

    return SceneGraph(
        nodes=tuple(nodes),
        edges=tuple(edges),
        layout=LayoutDirective.horizontal(gap=1.5),
        title=title,
        metadata={"type": "trace_timeline", "count": len(traces)},
    )


# =============================================================================
# Walk → SceneGraph
# =============================================================================


def walk_to_scene(walk: Walk, *, include_traces: bool = False) -> SceneGraph:
    """
    Convert a Walk to a SceneGraph.

    Creates a WALK-kind panel with:
    - Walk metadata (goal, phase, status)
    - Participant list
    - Optional trace timeline

    Args:
        walk: The Walk to convert
        include_traces: Whether to include embedded trace timeline

    Returns:
        SceneGraph representing the Walk
    """
    # Determine style based on status
    from services.witness.walk import WalkStatus

    status_colors = {
        WalkStatus.ACTIVE: PALETTE.LIVING_GREEN,
        WalkStatus.PAUSED: PALETTE.AMBER_GLOW,
        WalkStatus.COMPLETE: PALETTE.SAGE,
        WalkStatus.ABANDONED: PALETTE.TWILIGHT,
    }

    style = NodeStyle(
        background=status_colors.get(walk.status, PALETTE.PAPER),
        breathing=walk.is_active,  # Only breathe if active
    )

    # Build content
    content: dict[str, Any] = {
        "walk_id": str(walk.id),
        "name": walk.name,
        "goal": walk.goal.description if walk.goal else None,
        "phase": walk.phase.value,
        "status": walk.status.name,
        "trace_count": walk.trace_count(),
        "participants": [p.name for p in walk.participants],
        "duration_seconds": walk.duration_seconds,
        "started_at": walk.started_at.isoformat(),
    }

    walk_node = SceneNode(
        kind=SceneNodeKind.WALK,
        content=content,
        label=walk.name or f"Walk: {walk.goal.description[:30]}..." if walk.goal else "Walk",
        style=style,
        interactions=(
            Interaction(
                kind="click",
                action=f"time.walk.{walk.id}.witness",
                requires_trust=0,
            ),
        ),
        metadata={"walk_id": str(walk.id), "status": walk.status.name},
    )

    nodes = [walk_node]

    # Add phase indicator
    phase_node = SceneNode(
        kind=SceneNodeKind.TEXT,
        content=f"Phase: {walk.phase.value}",
        label=walk.phase.value,
        style=NodeStyle(background=PALETTE.COPPER),
    )
    nodes.append(phase_node)

    graph = SceneGraph(
        nodes=tuple(nodes),
        layout=LayoutDirective.vertical(gap=0.5),
        title=walk.name,
        metadata={"type": "walk", "walk_id": str(walk.id)},
    )

    return graph


def walk_dashboard_to_scene(walks: Sequence[Walk], *, title: str = "Walk Dashboard") -> SceneGraph:
    """
    Convert multiple Walks to a dashboard SceneGraph.

    Creates a grid of Walk cards with status indicators.

    Args:
        walks: Sequence of Walks to display
        title: Dashboard title

    Returns:
        SceneGraph with grid layout
    """
    if not walks:
        return SceneGraph(
            nodes=(SceneNode.text("No active walks", label="Empty"),),
            layout=LayoutDirective.vertical(),
            title=title,
        )

    # Create header
    header = SceneNode.panel(title, style=NodeStyle(background=PALETTE.PAPER))

    # Create walk cards (without traces for dashboard view)
    walk_scenes = [walk_to_scene(w, include_traces=False) for w in walks]

    # Compose
    cards_graph = SceneGraph(
        nodes=tuple(node for scene in walk_scenes for node in scene.nodes),
        layout=LayoutDirective.grid(gap=1.0),
        title="Walks",
    )

    return SceneGraph(nodes=(header,)) >> cards_graph


# =============================================================================
# Offering → SceneGraph
# =============================================================================


def offering_to_scene(offering: Offering) -> SceneNode:
    """
    Convert an Offering to a SceneNode.

    Creates an OFFERING badge with:
    - Kind indicator (context, capability, information)
    - Brief description
    - Trust requirement

    Args:
        offering: The Offering to convert

    Returns:
        SceneNode badge
    """
    return SceneNode(
        kind=SceneNodeKind.OFFERING,
        content={
            "offering_id": str(offering.id),
            "kind": offering.kind.value if hasattr(offering.kind, "value") else str(offering.kind),
            "description": offering.description,
            "scope": offering.scope,
        },
        label=offering.description[:30] if len(offering.description) > 30 else offering.description,
        style=NodeStyle(
            background=PALETTE.AMBER_GLOW,
            paper_grain=True,
        ),
        metadata={"offering_id": str(offering.id)},
    )


# =============================================================================
# Covenant → SceneGraph
# =============================================================================


def covenant_to_scene(covenant: Covenant) -> SceneNode:
    """
    Convert a Covenant to a SceneNode.

    Creates a COVENANT indicator showing:
    - Permissions granted
    - Trust level required
    - Expiration if applicable

    Args:
        covenant: The Covenant to convert

    Returns:
        SceneNode indicator
    """
    return SceneNode(
        kind=SceneNodeKind.COVENANT,
        content={
            "covenant_id": str(covenant.id),
            "permissions": list(covenant.permissions),
            "trust_level": covenant.trust_level,
            "expires_at": covenant.expires_at.isoformat() if covenant.expires_at else None,
        },
        label=f"Trust L{covenant.trust_level}",
        style=NodeStyle(
            background=PALETTE.COPPER if covenant.trust_level >= 2 else PALETTE.TWILIGHT,
        ),
        interactions=(
            Interaction(
                kind="hover",
                action="show_permissions",
                requires_trust=0,
                metadata={"permissions": list(covenant.permissions)},
            ),
        ),
        metadata={"covenant_id": str(covenant.id), "trust_level": covenant.trust_level},
    )


# =============================================================================
# Ritual → SceneGraph
# =============================================================================


def ritual_to_scene(ritual: Ritual, *, show_steps: bool = True) -> SceneGraph:
    """
    Convert a Ritual to a SceneGraph.

    Creates a RITUAL visualization with:
    - Ritual header (name, status)
    - Step progression
    - Covenant requirements

    Args:
        ritual: The Ritual to convert
        show_steps: Whether to include step details

    Returns:
        SceneGraph representing the Ritual workflow
    """
    # Determine status style
    status_style = NodeStyle(
        background=PALETTE.LIVING_GREEN if ritual.is_complete else PALETTE.COPPER,
        breathing=not ritual.is_complete,  # Breathe while in progress
    )

    ritual_node = SceneNode(
        kind=SceneNodeKind.RITUAL,
        content={
            "ritual_id": str(ritual.id),
            "name": ritual.name,
            "status": ritual.status.name if hasattr(ritual.status, "name") else str(ritual.status),
            "current_step": ritual.current_step,
            "total_steps": ritual.total_steps,
        },
        label=ritual.name,
        style=status_style,
        metadata={
            "ritual_id": str(ritual.id),
            "progress": ritual.current_step / max(ritual.total_steps, 1),
        },
    )

    nodes = [ritual_node]

    # Add step nodes if requested
    if show_steps and hasattr(ritual, "steps"):
        for i, step in enumerate(ritual.steps):
            is_current = i == ritual.current_step
            is_complete = i < ritual.current_step

            step_style = NodeStyle(
                background=PALETTE.SAGE if is_complete else (PALETTE.AMBER_GLOW if is_current else PALETTE.PAPER),
                breathing=is_current,
            )

            step_node = SceneNode(
                kind=SceneNodeKind.TEXT,
                content={"step": i, "description": str(step)},
                label=f"Step {i + 1}",
                style=step_style,
            )
            nodes.append(step_node)

    return SceneGraph(
        nodes=tuple(nodes),
        layout=LayoutDirective.horizontal(gap=1.0),
        title=ritual.name,
        metadata={"type": "ritual", "ritual_id": str(ritual.id)},
    )


# =============================================================================
# Composite Converters
# =============================================================================


def witness_dashboard_to_scene(
    walks: Sequence[Walk],
    traces: Sequence[TraceNode],
    *,
    title: str = "Witness Dashboard",
) -> SceneGraph:
    """
    Create a comprehensive Witness dashboard SceneGraph.

    Combines:
    - Active walks section
    - Recent trace timeline
    - Summary statistics

    Args:
        walks: Active and recent walks
        traces: Recent traces
        title: Dashboard title

    Returns:
        Composite SceneGraph for the dashboard
    """
    # Header
    header = SceneGraph.panel(
        title,
        SceneNode.text(f"{len(walks)} walks, {len(traces)} traces", label="Stats"),
        layout=LayoutDirective.horizontal(),
    )

    # Walks section
    walks_section = walk_dashboard_to_scene(walks, title="Active Walks")

    # Traces section
    traces_section = trace_timeline_to_scene(list(traces)[-10:], title="Recent Activity")

    # Compose vertically
    return header >> walks_section >> traces_section


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Palette
    "LivingEarthPalette",
    "PALETTE",
    "PALETTE_HEX",
    "palette_to_hex",
    # TraceNode converters
    "trace_node_to_scene",
    "trace_timeline_to_scene",
    # Walk converters
    "walk_to_scene",
    "walk_dashboard_to_scene",
    # Offering/Covenant converters
    "offering_to_scene",
    "covenant_to_scene",
    # Ritual converters
    "ritual_to_scene",
    # Composite
    "witness_dashboard_to_scene",
]
