"""
Crystal Trail Adapter: Bridge Crystals to Trail Visualization.

Crystals ARE trails through time. This module provides the bridge
between the witness crystallization system and the Trail visualization
infrastructure (TrailGraph.tsx, useForceLayout, etc.).

Key Insight:
    Crystal Level Hierarchy ≈ Trail Steps
    - Crystals at each level become nodes
    - Provenance chains (source_crystals) become edges
    - Level determines y-position anchoring in force layout

Architecture:
    Crystals → CrystalTrailAdapter → TrailGraphNode/Edge → TrailGraph.tsx
                                          ↓
                                    useForceLayout (d3-force)

Philosophy:
    "Composition is primary. The Trail infra generates crystal visualization."

See: spec/protocols/witness-crystallization.md
See: brainstorming/visual-trail-graph-r&d.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .crystal import Crystal, CrystalId, CrystalLevel
from .crystal_store import CrystalStore, get_crystal_store

logger = logging.getLogger("kgents.witness.crystal_trail")


# =============================================================================
# Type Definitions (Mirror trail.ts types)
# =============================================================================


@dataclass
class CrystalGraphNode:
    """
    A node in the crystal hierarchy graph.

    Mirrors TrailGraphNode from api/trail.ts for frontend compatibility.
    """

    id: str
    type: str = "crystal"  # Node type for react-flow
    position: dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "position": self.position,
            "data": self.data,
        }


@dataclass
class CrystalGraphEdge:
    """
    An edge in the crystal hierarchy graph.

    Mirrors TrailGraphEdge from api/trail.ts for frontend compatibility.
    """

    id: str
    source: str
    target: str
    label: str = "compresses"
    type: str = "compression"  # structural | semantic | compression
    animated: bool = False
    style: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "label": self.label,
            "type": self.type,
            "animated": self.animated,
            "style": self.style,
        }


@dataclass
class CrystalGraph:
    """
    A complete crystal hierarchy graph ready for visualization.
    """

    nodes: list[CrystalGraphNode]
    edges: list[CrystalGraphEdge]

    # Metadata
    total_crystals: int = 0
    level_counts: dict[str, int] = field(default_factory=dict)
    time_range: tuple[datetime, datetime] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "total_crystals": self.total_crystals,
            "level_counts": self.level_counts,
            "time_range": [
                self.time_range[0].isoformat(),
                self.time_range[1].isoformat(),
            ]
            if self.time_range
            else None,
        }


# =============================================================================
# Crystal Trail Adapter
# =============================================================================


class CrystalTrailAdapter:
    """
    Adapts crystals to the Trail visualization format.

    The core insight: Crystal hierarchy is isomorphic to Trail structure.

    | Crystal          | Trail              |
    |------------------|--------------------|
    | level            | step_index (y)     |
    | source_crystals  | edges              |
    | topics           | path               |
    | insight          | reasoning          |
    | confidence       | evidence_strength  |

    Layout Strategy:
    - X-axis: Temporal order within level (crystallized_at)
    - Y-axis: Level (SESSION=0 at bottom, EPOCH=3 at top)
    - Edges: Compression relationships (source → target)
    """

    # Level Y-positions (bottom to top, inverted for screen coords)
    LEVEL_Y_POSITIONS = {
        CrystalLevel.SESSION: 450,  # Bottom
        CrystalLevel.DAY: 300,
        CrystalLevel.WEEK: 150,
        CrystalLevel.EPOCH: 50,  # Top
    }

    # Node spacing within level
    NODE_X_SPACING = 180
    NODE_X_START = 100

    def __init__(self, store: CrystalStore | None = None):
        """
        Initialize the adapter.

        Args:
            store: Crystal store (defaults to global singleton)
        """
        self._store = store

    @property
    def store(self) -> CrystalStore:
        """Get the crystal store."""
        if self._store is None:
            self._store = get_crystal_store()
        return self._store

    def to_graph(
        self,
        crystals: list[Crystal] | None = None,
        level_filter: CrystalLevel | None = None,
        limit: int = 50,
    ) -> CrystalGraph:
        """
        Convert crystals to a visualizable graph.

        Args:
            crystals: Specific crystals to include (defaults to store)
            level_filter: Only include crystals at this level
            limit: Maximum crystals per level

        Returns:
            CrystalGraph ready for TrailGraph.tsx
        """
        # Get crystals from store if not provided
        if crystals is None:
            crystals = list(self.store.all())

        # Filter by level if requested
        if level_filter is not None:
            crystals = [c for c in crystals if c.level == level_filter]

        # Group by level for layout
        by_level: dict[CrystalLevel, list[Crystal]] = {
            CrystalLevel.SESSION: [],
            CrystalLevel.DAY: [],
            CrystalLevel.WEEK: [],
            CrystalLevel.EPOCH: [],
        }

        for crystal in crystals:
            by_level[crystal.level].append(crystal)

        # Sort within each level by time (newest first at left)
        for level in by_level:
            by_level[level] = sorted(
                by_level[level],
                key=lambda c: c.crystallized_at,
                reverse=True,
            )[:limit]

        # Build nodes
        nodes: list[CrystalGraphNode] = []
        crystal_id_to_node_id: dict[CrystalId, str] = {}

        for level, level_crystals in by_level.items():
            y = self.LEVEL_Y_POSITIONS[level]

            for i, crystal in enumerate(level_crystals):
                x = self.NODE_X_START + i * self.NODE_X_SPACING

                node_id = f"crystal-{str(crystal.id)[:12]}"
                crystal_id_to_node_id[crystal.id] = node_id

                nodes.append(
                    CrystalGraphNode(
                        id=node_id,
                        type="crystal",
                        position={"x": x, "y": y},
                        data={
                            "crystal_id": str(crystal.id),
                            "level": level.name,
                            "level_value": level.value,
                            "insight": crystal.insight,
                            "significance": crystal.significance,
                            "confidence": crystal.confidence,
                            "source_count": crystal.source_count,
                            "principles": list(crystal.principles),
                            "topics": list(crystal.topics),
                            "crystallized_at": crystal.crystallized_at.isoformat(),
                            # Trail-compatible fields
                            "path": f"crystal.{level.name.lower()}.{str(crystal.id)[:8]}",
                            "holon": level.name,
                            "step_index": level.value,  # Use level as step index
                            "edge_type": "compresses",
                            "reasoning": crystal.significance,
                            "is_current": False,
                        },
                    )
                )

        # Build edges (provenance chains)
        edges: list[CrystalGraphEdge] = []
        edge_count = 0

        for crystal in crystals:
            source_node_id = crystal_id_to_node_id.get(crystal.id)
            if not source_node_id:
                continue

            # Connect to source crystals (higher levels compress lower)
            for source_crystal_id in crystal.source_crystals:
                target_node_id = crystal_id_to_node_id.get(source_crystal_id)
                if target_node_id:
                    edges.append(
                        CrystalGraphEdge(
                            id=f"edge-{edge_count}",
                            source=target_node_id,  # Source → Target (lower to higher)
                            target=source_node_id,
                            label="compresses",
                            type="compression",
                            animated=True,
                            style={"strokeDasharray": "5 5"},
                        )
                    )
                    edge_count += 1

        # Compute metadata
        all_crystals = [c for level_list in by_level.values() for c in level_list]
        level_counts = {level.name: len(crystals_list) for level, crystals_list in by_level.items()}

        # Time range
        time_range = None
        if all_crystals:
            times = [c.crystallized_at for c in all_crystals]
            time_range = (min(times), max(times))

        return CrystalGraph(
            nodes=nodes,
            edges=edges,
            total_crystals=len(all_crystals),
            level_counts=level_counts,
            time_range=time_range,
        )

    def get_crystal_detail(self, crystal_id: CrystalId) -> dict[str, Any] | None:
        """
        Get detailed information about a crystal for the ReasoningPanel.

        Includes source marks/crystals for drill-down.
        """
        crystal = self.store.get(crystal_id)
        if not crystal:
            return None

        return {
            "id": str(crystal.id),
            "level": crystal.level.name,
            "insight": crystal.insight,
            "significance": crystal.significance,
            "principles": list(crystal.principles),
            "topics": list(crystal.topics),
            "confidence": crystal.confidence,
            "source_count": crystal.source_count,
            "source_marks": [str(m) for m in crystal.source_marks],
            "source_crystals": [str(c) for c in crystal.source_crystals],
            "mood": crystal.mood.to_dict(),
            "crystallized_at": crystal.crystallized_at.isoformat(),
            "time_range": [
                crystal.time_range[0].isoformat(),
                crystal.time_range[1].isoformat(),
            ]
            if crystal.time_range
            else None,
        }


# =============================================================================
# Standalone Functions
# =============================================================================


def crystals_to_graph(
    crystals: list[Crystal] | None = None,
    level_filter: CrystalLevel | None = None,
    limit: int = 50,
) -> CrystalGraph:
    """
    Convert crystals to a visualizable graph.

    Convenience function using default adapter.

    Args:
        crystals: Specific crystals to include
        level_filter: Only include crystals at this level
        limit: Maximum crystals per level

    Returns:
        CrystalGraph ready for frontend
    """
    adapter = CrystalTrailAdapter()
    return adapter.to_graph(
        crystals=crystals,
        level_filter=level_filter,
        limit=limit,
    )


def get_hierarchy_graph(
    store: CrystalStore | None = None,
) -> CrystalGraph:
    """
    Get the full crystal hierarchy as a graph.

    Shows all levels with compression relationships.
    """
    adapter = CrystalTrailAdapter(store)
    return adapter.to_graph()


# =============================================================================
# API Response Helpers
# =============================================================================


def format_graph_response(graph: CrystalGraph) -> dict[str, Any]:
    """
    Format graph for AGENTESE API response.

    Compatible with TrailGraphResponse structure.
    """
    return {
        "summary": f"Crystal hierarchy: {graph.total_crystals} crystals across {len(graph.level_counts)} levels",
        "content": "",
        "metadata": {
            "nodes": [n.to_dict() for n in graph.nodes],
            "edges": [e.to_dict() for e in graph.edges],
            "total_crystals": graph.total_crystals,
            "level_counts": graph.level_counts,
            "time_range": [
                graph.time_range[0].isoformat(),
                graph.time_range[1].isoformat(),
            ]
            if graph.time_range
            else None,
            "mode": "crystal",  # Signals crystal mode to frontend
        },
    }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "CrystalGraphNode",
    "CrystalGraphEdge",
    "CrystalGraph",
    # Adapter
    "CrystalTrailAdapter",
    # Functions
    "crystals_to_graph",
    "get_hierarchy_graph",
    "format_graph_response",
]
