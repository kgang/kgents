"""
Map Handler: M-gent HoloMap ASCII render.

DevEx V4 Phase 1 - Foundation Layer.

From Memory-as-Retrieval to Memory-as-Orientation.

Usage:
    kgents map             # Show current map (ASCII + summary)
    kgents map --ascii     # Just ASCII visualization
    kgents map --summary   # Just text summary
    kgents map --json      # Machine-readable JSON
    kgents map <query>     # Center map on query

Example output:
    HoloMap: Current Context
    ========================================
    Origin: Working on DevEx V4 implementation

    Statistics:
      Landmarks: 12
      Desire Lines: 8
      Voids: 2
      Coverage: 87.3%

    Focal Zone (high detail):
      ✓ CLI Handlers
      ✓ Instance DB
      ⚠ MCP Integration (drifting)
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def cmd_map(args: list[str]) -> int:
    """
    Display M-gent's HoloMap of the semantic space.

    The HoloMap provides orientation rather than retrieval:
    - Landmarks: Dense memory clusters
    - Desire Lines: Commonly traversed paths
    - Voids: Unexplored regions
    """
    # Parse args
    ascii_only = "--ascii" in args
    summary_only = "--summary" in args
    json_mode = "--json" in args
    help_mode = "--help" in args or "-h" in args

    # Extract query if provided
    query = None
    for arg in args:
        if not arg.startswith("--") and not arg.startswith("-"):
            query = arg
            break

    if help_mode:
        print(__doc__)
        return 0

    # Get lifecycle state
    from protocols.cli.hollow import get_lifecycle_state

    state = get_lifecycle_state()

    if state is None:
        print("[MAP] ? DB-LESS | No map without memory")
        print("  Run 'kgents init' to initialize workspace.")
        return 0

    try:
        holo_map = _get_or_create_map(state, query)

        if holo_map is None:
            print("[MAP] ? EMPTY | No memories to map")
            print("  Add memories via 'kgents membrane touch <path>'")
            return 0

        renderer = _get_renderer()

        if json_mode:
            print(_map_to_json(holo_map))
        elif ascii_only:
            print(renderer.render_ascii(holo_map))
        elif summary_only:
            print(renderer.render_summary(holo_map))
        else:
            # Both
            print(renderer.render_ascii(holo_map))
            print()
            print(renderer.render_summary(holo_map))

        return 0

    except ImportError as e:
        print(f"[MAP] ! DEGRADED | Missing component: {e}")
        return 1
    except Exception as e:
        print(f"[MAP] X ERROR | {e}")
        return 1


def _get_or_create_map(state, query: str | None):
    """
    Get or create a HoloMap from lifecycle state.

    If query is provided, center the map on that query.
    """
    from agents.m.cartography import ContextVector, HoloMap, Resolution

    # Check if we have a pathfinder or cartography service
    pathfinder = getattr(state, "pathfinder", None)
    vector_store = getattr(state, "vector_store", None)

    if pathfinder is not None:
        # Use pathfinder to generate map
        if query:
            from agents.m.cartography_integrations import Pathfinder

            # Get embedding for query (would need embedder)
            embedder = getattr(state, "embedder", None)
            if embedder:
                embedding = embedder.embed(query)
                origin = ContextVector(embedding=embedding, label=query)
            else:
                # Dummy embedding
                origin = ContextVector(embedding=[0.0] * 384, label=query)
            return pathfinder.generate_map(origin, Resolution.ADAPTIVE)
        else:
            # Generate map from current context
            origin = ContextVector(embedding=[0.0] * 384, label="Current Context")
            return pathfinder.generate_map(origin, Resolution.ADAPTIVE)

    # Fallback: create minimal empty map
    return HoloMap(
        origin=ContextVector(embedding=[0.0] * 384, label=query or "No memories"),
        landmarks=[],
        desire_lines=[],
        voids=[],
        horizon_radius=1.0,
    )


def _get_renderer():
    """Get the MapRenderer instance."""
    from agents.m.cartography_integrations import MapRenderConfig, MapRenderer

    return MapRenderer(
        config=MapRenderConfig(
            width=60,
            height=20,
            show_health=True,
            show_voids=True,
        )
    )


def _map_to_json(holo_map) -> str:
    """Convert HoloMap to JSON."""
    return json.dumps(
        {
            "origin": {
                "label": holo_map.origin.label,
                "dimension": holo_map.origin.dimension,
            },
            "landmarks": [
                {
                    "id": l.id,
                    "label": l.label,
                    "members": len(l.members),
                    "density": l.density,
                }
                for l in holo_map.landmarks
            ],
            "desire_lines": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                }
                for e in holo_map.desire_lines
            ],
            "voids": [
                {
                    "id": v.id,
                    "is_dangerous": v.is_dangerous,
                }
                for v in holo_map.voids
            ],
            "statistics": {
                "landmark_count": holo_map.landmark_count,
                "edge_count": holo_map.edge_count,
                "void_count": holo_map.void_count,
                "coverage": holo_map.coverage,
            },
        },
        indent=2,
    )
