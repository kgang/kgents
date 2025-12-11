"""
Map Handler: M-gent HoloMap ASCII render.

DevEx V4 Phase 1 - Foundation Layer.
Glass Terminal Integration: Uses GlassClient with 3-layer fallback.

From Memory-as-Retrieval to Memory-as-Orientation.

Usage:
    kgents map             # Show current map (ASCII + summary)
    kgents map --ascii     # Just ASCII visualization
    kgents map --summary   # Just text summary
    kgents map --json      # Machine-readable JSON
    kgents map --ghost     # Show cached map state
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

Architecture:
    This handler is "hollowed" - it delegates to GlassClient which implements:
    1. Try gRPC call to Cortex daemon (GetMap RPC)
    2. On gRPC failure, try local CortexServicer (in-process)
    3. On local failure, read from Ghost cache (last-known-good)
"""

from __future__ import annotations

import asyncio
import json
from typing import Any


def cmd_map(args: list[str]) -> int:
    """
    Display M-gent's HoloMap of the semantic space.

    This is a "hollowed" handler - it delegates to GlassClient for the
    three-layer fallback strategy (gRPC → local → Ghost cache).
    """
    # Parse args
    ascii_only = "--ascii" in args
    summary_only = "--summary" in args
    json_mode = "--json" in args
    ghost_mode = "--ghost" in args
    help_mode = "--help" in args or "-h" in args

    # Extract query/focus if provided
    query = None
    for arg in args:
        if not arg.startswith("--") and not arg.startswith("-"):
            query = arg
            break

    if help_mode:
        print(__doc__)
        return 0

    # Ghost mode: show cached map state
    if ghost_mode:
        return _show_ghost_map_state()

    # Run async map command
    return asyncio.run(
        _async_map(
            query=query,
            ascii_only=ascii_only,
            summary_only=summary_only,
            json_mode=json_mode,
        )
    )


async def _async_map(
    query: str | None = None,
    ascii_only: bool = False,
    summary_only: bool = False,
    json_mode: bool = False,
) -> int:
    """
    Async implementation of map command using GlassClient.

    Uses GetMap RPC to get the HoloMap from Cortex.
    """
    from protocols.cli.glass import GlassResponse, get_glass_client

    client = get_glass_client()

    try:
        # Create MapRequest
        try:
            from protocols.proto.generated import MapRequest

            request = MapRequest(
                focus=query or "",
                resolution="medium",
                format="ascii" if ascii_only else "full",
                include_desire_lines=True,
                include_voids=True,
                include_attractors=True,
            )
        except ImportError:
            # Fallback: simple object
            class SimpleRequest:
                def __init__(
                    self,
                    focus: str,
                    resolution: str,
                    format: str,
                    include_desire_lines: bool,
                    include_voids: bool,
                    include_attractors: bool,
                ):
                    self.focus = focus
                    self.resolution = resolution
                    self.format = format
                    self.include_desire_lines = include_desire_lines
                    self.include_voids = include_voids
                    self.include_attractors = include_attractors

            request = SimpleRequest(
                focus=query or "",
                resolution="medium",
                format="ascii" if ascii_only else "full",
                include_desire_lines=True,
                include_voids=True,
                include_attractors=True,
            )

        # Invoke GetMap through GlassClient
        response: GlassResponse = await client.invoke(
            method="GetMap",
            request=request,
            ghost_key="map",
            agentese_path="world.project.manifest",
        )

        # Extract map data from response
        map_data = _extract_map_data(response.data)

        if json_mode:
            output = _map_data_to_json(map_data)
            if response.is_ghost:
                output_dict = json.loads(output)
                output_dict["_ghost"] = {
                    "is_cached": True,
                    "age_seconds": response.ghost_age.total_seconds()
                    if response.ghost_age
                    else None,
                }
                print(json.dumps(output_dict, indent=2))
            else:
                print(output)

        elif ascii_only:
            _print_ascii_map(map_data, response.is_ghost)

        elif summary_only:
            _print_map_summary(map_data, response.is_ghost, response.ghost_age)

        else:
            # Both ASCII and summary
            _print_ascii_map(map_data, response.is_ghost)
            print()
            _print_map_summary(map_data, response.is_ghost, response.ghost_age)

        return 0

    except ConnectionError as e:
        print(f"[MAP] X OFFLINE | {e}")
        print("  Run 'kgents infra init' to start the Cortex daemon.")
        return 1

    except Exception as e:
        print(f"[MAP] X ERROR | {e}")
        return 1


def _extract_map_data(data: Any) -> dict[str, Any]:
    """
    Extract map data from GlassResponse data.

    Handles both protobuf HoloMap and dict from Ghost cache.
    """
    if isinstance(data, dict):
        return data

    # Protobuf message - convert to dict
    if hasattr(data, "DESCRIPTOR"):
        try:
            from google.protobuf.json_format import MessageToDict

            return MessageToDict(data, preserving_proto_field_name=True)
        except ImportError:
            pass

    # Dataclass with to_dict
    if hasattr(data, "to_dict"):
        return data.to_dict()

    # HoloMap object from local servicer
    if hasattr(data, "landmarks"):
        return {
            "landmarks": [
                {
                    "name": getattr(l, "name", getattr(l, "label", "unknown")),
                    "path": getattr(l, "path", ""),
                    "significance": getattr(
                        l, "significance", getattr(l, "density", 0.0)
                    ),
                    "category": getattr(
                        l, "category", getattr(l, "artifact_type", "unknown")
                    ),
                }
                for l in data.landmarks
            ]
            if hasattr(data, "landmarks")
            else [],
            "desire_lines": [
                {
                    "from_path": getattr(d, "from_path", getattr(d, "source", "")),
                    "to_path": getattr(d, "to_path", getattr(d, "target", "")),
                    "strength": getattr(d, "strength", getattr(d, "weight", 0.0)),
                }
                for d in data.desire_lines
            ]
            if hasattr(data, "desire_lines")
            else [],
            "voids": [
                {
                    "path": getattr(v, "path", getattr(v, "id", "")),
                    "description": getattr(v, "description", getattr(v, "label", "")),
                    "mystery_score": getattr(v, "mystery_score", 0.0),
                }
                for v in data.voids
            ]
            if hasattr(data, "voids")
            else [],
            "rendered": getattr(data, "rendered", "[No visualization available]"),
            "metadata": {
                "total_files": getattr(
                    getattr(data, "metadata", None), "total_files", 0
                ),
                "total_landmarks": getattr(
                    getattr(data, "metadata", None), "total_landmarks", 0
                ),
                "resolution": getattr(
                    getattr(data, "metadata", None), "resolution", "medium"
                ),
            }
            if hasattr(data, "metadata")
            else {},
        }

    # Unknown type - return minimal
    return {"raw": str(data)}


def _print_ascii_map(map_data: dict[str, Any], is_ghost: bool = False) -> None:
    """Print ASCII visualization of the map."""
    prefix = "[GHOST]" if is_ghost else "[MAP]"

    # Check for pre-rendered ASCII from protobuf
    rendered = map_data.get("rendered", "")
    if rendered and rendered != "[Map visualization not yet implemented]":
        print(f"{prefix} HoloMap")
        print("=" * 40)
        print(rendered)
        return

    # Generate simple ASCII representation
    landmarks = map_data.get("landmarks", [])
    desire_lines = map_data.get("desire_lines", [])
    voids = map_data.get("voids", [])

    print(f"{prefix} HoloMap")
    print("=" * 40)

    if not landmarks and not voids:
        print("  [Empty map - no landmarks or voids]")
        print("  Run 'kgents ghost' to populate map")
        return

    # Simple text-based representation
    print()
    if landmarks:
        print("  Landmarks:")
        for i, l in enumerate(landmarks[:10]):
            name = l.get("name", "unknown")
            sig = l.get("significance", 0.0)
            cat = l.get("category", "unknown")
            bar = "█" * max(1, int(sig * 10))
            print(f"    [{cat[:4]:4}] {bar} {name}")

    if desire_lines:
        print()
        print("  Desire Lines:")
        for d in desire_lines[:5]:
            from_path = d.get("from_path", "?")
            to_path = d.get("to_path", "?")
            strength = d.get("strength", 0.0)
            print(f"    {from_path} → {to_path} ({strength:.1f})")

    if voids:
        print()
        print("  Voids (unexplored):")
        for v in voids[:3]:
            desc = v.get("description", v.get("path", "unknown"))
            mystery = v.get("mystery_score", 0.0)
            print(f"    ? {desc} (mystery: {mystery:.1f})")


def _print_map_summary(
    map_data: dict[str, Any],
    is_ghost: bool = False,
    ghost_age: Any = None,
) -> None:
    """Print map summary statistics."""
    prefix = "[GHOST]" if is_ghost else "[MAP]"

    landmarks = map_data.get("landmarks", [])
    desire_lines = map_data.get("desire_lines", [])
    voids = map_data.get("voids", [])
    metadata = map_data.get("metadata", {})

    print(f"{prefix} Summary")
    print("-" * 40)

    if is_ghost and ghost_age:
        seconds = int(ghost_age.total_seconds())
        print(f"  (Cached data from {seconds}s ago)")
        print()

    print(f"  Landmarks:     {len(landmarks)}")
    print(f"  Desire Lines:  {len(desire_lines)}")
    print(f"  Voids:         {len(voids)}")

    if metadata:
        total_files = metadata.get("total_files", 0)
        resolution = metadata.get("resolution", "medium")
        if total_files:
            print(f"  Total Files:   {total_files}")
        print(f"  Resolution:    {resolution}")


def _map_data_to_json(map_data: dict[str, Any]) -> str:
    """Convert map data to JSON string."""
    return json.dumps(
        {
            "landmarks": [
                {
                    "name": l.get("name", "unknown"),
                    "path": l.get("path", ""),
                    "significance": l.get("significance", 0.0),
                    "category": l.get("category", "unknown"),
                }
                for l in map_data.get("landmarks", [])
            ],
            "desire_lines": [
                {
                    "from_path": d.get("from_path", ""),
                    "to_path": d.get("to_path", ""),
                    "strength": d.get("strength", 0.0),
                }
                for d in map_data.get("desire_lines", [])
            ],
            "voids": [
                {
                    "path": v.get("path", ""),
                    "description": v.get("description", ""),
                    "mystery_score": v.get("mystery_score", 0.0),
                }
                for v in map_data.get("voids", [])
            ],
            "statistics": {
                "landmark_count": len(map_data.get("landmarks", [])),
                "desire_line_count": len(map_data.get("desire_lines", [])),
                "void_count": len(map_data.get("voids", [])),
            },
            "metadata": map_data.get("metadata", {}),
        },
        indent=2,
    )


def _show_ghost_map_state() -> int:
    """Show cached map state for debugging."""
    try:
        from protocols.cli.glass import GHOST_DIR, GhostCache

        cache = GhostCache()
        data, age, timestamp = cache.read("map")

        if data is None:
            print("[GHOST] No cached map state available.")
            print("  Run 'kgents map' to populate cache.")
            return 0

        # Format age
        age_str = "unknown"
        if age is not None:
            seconds = int(age.total_seconds())
            if seconds < 60:
                age_str = f"{seconds}s"
            elif seconds < 3600:
                age_str = f"{seconds // 60}m"
            else:
                age_str = f"{seconds // 3600}h"

        print(f"[GHOST] Cached map state from {age_str} ago:")
        print()

        # Display cached data
        map_data = _extract_map_data(data)
        _print_ascii_map(map_data, is_ghost=True)
        print()
        _print_map_summary(map_data, is_ghost=True, ghost_age=age)

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to read Ghost cache: {e}")
        return 1
