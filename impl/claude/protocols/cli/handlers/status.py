"""
Status Handler: Cortex health at a glance.

DevEx V4 Phase 1 - Foundation Layer.
Glass Terminal Integration: Uses GlassClient with 3-layer fallback.

Usage:
    kgents status          # Compact one-liner (combines cortex + ghost)
    kgents status --full   # Full ASCII dashboard
    kgents status --json   # Machine-readable JSON
    kgents status --cortex # Cortex-only (skip ghost health)
    kgents status --ghost  # Show cached status (for debugging)

Example output:
    [CORTEX] OK HEALTHY | instance:a8f3b2 | agents:5 | branch:main dirty:3

Architecture:
    This handler is "hollowed" - it delegates to GlassClient which implements:
    1. Try gRPC call to Cortex daemon (live data)
    2. On gRPC failure, try local CortexServicer (in-process)
    3. On local failure, read from Ghost cache (last-known-good)
    4. On cache miss, provide clear error with recovery guidance
"""

from __future__ import annotations

import asyncio
import json as json_module
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_status(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Display cortex health status.

    This is a "hollowed" handler - it delegates to GlassClient for the
    three-layer fallback strategy (gRPC → local → Ghost cache).

    Glass Terminal Integration:
    - On success: GlassClient writes status to Ghost cache automatically
    - On failure: GlassClient reads from Ghost cache if available
    - Enables offline resilience for debugging

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    - Human output goes to stdout
    - Semantic output goes to FD3 (for agent consumption)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("status", args)
        except ImportError:
            pass

    # Parse args
    full_mode = "--full" in args
    json_mode = "--json" in args
    help_mode = "--help" in args or "-h" in args
    cortex_only = "--cortex" in args
    ghost_mode = "--ghost" in args  # Show cached status only

    if help_mode:
        print(__doc__)
        return 0

    # Ghost mode: show cached status only (for debugging)
    if ghost_mode:
        return _show_glass_cache_status()

    # Run async status retrieval
    return asyncio.run(
        _async_status(
            full_mode=full_mode,
            json_mode=json_mode,
            cortex_only=cortex_only,
            ctx=ctx,
        )
    )


async def _async_status(
    full_mode: bool = False,
    json_mode: bool = False,
    cortex_only: bool = False,
    ctx: "InvocationContext | None" = None,
) -> int:
    """
    Async implementation of status command using GlassClient.

    The GlassClient handles the three-layer fallback:
    1. gRPC to Cortex daemon
    2. Local CortexServicer
    3. Ghost cache

    If ctx is provided, outputs via dual-channel (human + semantic).
    """
    from protocols.cli.glass import GlassResponse, get_glass_client
    from protocols.cli.hollow import find_kgents_root

    project_root = find_kgents_root() or Path.cwd()
    client = get_glass_client()

    try:
        # Create StatusRequest (works with or without protobuf)
        try:
            from protocols.proto.generated import StatusRequest

            request: Any = StatusRequest(verbose=full_mode)
        except ImportError:
            # Fallback: simple object with verbose attribute
            class SimpleRequest:
                def __init__(self, verbose: bool = False):
                    self.verbose = verbose

            request = SimpleRequest(verbose=full_mode)

        # Invoke GetStatus through GlassClient (handles all fallback)
        response: GlassResponse = await client.invoke(
            method="GetStatus",
            request=request,
            ghost_key="status",
            agentese_path="self.cortex.manifest",
        )

        # Extract status data from response
        status_data = _extract_status_data(response.data)

        # Build semantic output (for FD3)
        semantic_output = _build_semantic_output(
            status_data, project_root, cortex_only, response.is_ghost, response.ghost_age
        )

        # Render based on mode
        if json_mode:
            output = _build_json_output_from_data(
                status_data, project_root, cortex_only
            )
            if response.is_ghost:
                output["_ghost"] = {
                    "is_cached": True,
                    "age_seconds": response.ghost_age.total_seconds()
                    if response.ghost_age
                    else None,
                }
            human_output = json_module.dumps(output, indent=2, default=str)
            _emit_output(human_output, semantic_output, ctx)

        elif full_mode:
            _print_full_status(status_data, response.is_ghost, response.ghost_age)
            if not cortex_only:
                _print_ghost_panel(project_root)
            # Full mode doesn't use dual-channel (too complex)
            if ctx is not None:
                ctx.emit_semantic(semantic_output)

        else:
            # Compact mode - use dual-channel output
            compact_line = _render_compact_status(
                status_data, response.is_ghost, response.ghost_age
            )
            if not cortex_only:
                ghost_status = _get_ghost_status_line(project_root)
                if ghost_status:
                    compact_line = _merge_status_lines(compact_line, ghost_status)
            _emit_output(compact_line, semantic_output, ctx)

        return 0

    except ConnectionError as e:
        # GlassClient couldn't connect AND no Ghost cache available
        error_human = f"[STATUS] X OFFLINE | {e}"
        error_semantic = {"health": "offline", "error": str(e)}
        _emit_output(error_human, error_semantic, ctx)
        print("  Run 'kgents infra init' to start the Cortex daemon.")
        return 1

    except Exception as e:
        error_human = f"[STATUS] X ERROR | {e}"
        error_semantic = {"health": "error", "error": str(e)}
        _emit_output(error_human, error_semantic, ctx)
        return 1


def _emit_output(
    human: str,
    semantic: dict[str, Any],
    ctx: "InvocationContext | None",
) -> None:
    """
    Emit output via dual-channel if ctx available, else print.

    This is the key integration point with the Reflector Protocol:
    - Human output goes to stdout (for humans)
    - Semantic output goes to FD3 (for agents consuming our output)
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


def _build_semantic_output(
    status_data: dict[str, Any],
    project_root: Path,
    cortex_only: bool,
    is_ghost: bool,
    ghost_age: Any,
) -> dict[str, Any]:
    """
    Build semantic output for FD3 channel.

    This is the structured data that agents can consume.
    """
    semantic: dict[str, Any] = {
        "health": status_data.get("health", "unknown"),
        "instance_id": status_data.get("instance_id", "unknown"),
        "agents": status_data.get("agents", []),
        "components": status_data.get("components", []),
    }

    if is_ghost:
        semantic["_source"] = "ghost"
        if ghost_age is not None:
            semantic["_age_seconds"] = ghost_age.total_seconds()
    else:
        semantic["_source"] = "live"

    # Add pheromones if present
    pheromones = status_data.get("pheromone_levels", {})
    if pheromones:
        semantic["pheromone_levels"] = pheromones

    # Add ghost context if not cortex-only
    if not cortex_only:
        ghost_context = _get_ghost_context(project_root)
        if ghost_context:
            semantic["ghost_context"] = ghost_context

    return semantic


def _extract_status_data(data: Any) -> dict[str, Any]:
    """
    Extract status data from GlassResponse data.

    Handles both protobuf StatusResponse and dict from Ghost cache.
    """
    if isinstance(data, dict):
        return data

    # Protobuf message - convert to dict
    if hasattr(data, "DESCRIPTOR"):
        try:
            from google.protobuf.json_format import MessageToDict

            return cast(
                dict[str, Any], MessageToDict(data, preserving_proto_field_name=True)
            )
        except ImportError:
            pass

    # Dataclass with to_dict
    if hasattr(data, "to_dict"):
        return cast(dict[str, Any], data.to_dict())

    # Dataclass without to_dict
    if hasattr(data, "__dataclass_fields__"):
        from dataclasses import asdict

        return asdict(data)

    # Unknown type - wrap in dict
    return {"raw": str(data)}


def _render_compact_status(
    status_data: dict[str, Any],
    is_ghost: bool = False,
    ghost_age: Any = None,
) -> str:
    """
    Render compact one-line status.

    Format: [CORTEX] OK HEALTHY | instance:abc123 | agents:5 | components:ok
    """
    prefix = "[GHOST]" if is_ghost else "[CORTEX]"

    health = status_data.get("health", "unknown").upper()
    health_indicator = (
        "OK" if health == "HEALTHY" else "!" if health == "DEGRADED" else "?"
    )

    instance_id = status_data.get("instance_id", "unknown")[:8]

    agents = status_data.get("agents", [])
    agent_count = len(agents) if isinstance(agents, list) else 0

    components = status_data.get("components", [])
    healthy_count = sum(1 for c in components if c.get("healthy", False))
    total_count = len(components)
    comp_status = f"{healthy_count}/{total_count}" if total_count > 0 else "n/a"

    line = f"{prefix} {health_indicator} {health} | instance:{instance_id} | agents:{agent_count} | components:{comp_status}"

    if is_ghost and ghost_age:
        seconds = int(ghost_age.total_seconds())
        if seconds < 60:
            age_str = f"{seconds}s"
        elif seconds < 3600:
            age_str = f"{seconds // 60}m"
        else:
            age_str = f"{seconds // 3600}h"
        line += f" | cached:{age_str} ago"

    return line


def _print_full_status(
    status_data: dict[str, Any],
    is_ghost: bool = False,
    ghost_age: Any = None,
) -> None:
    """Print full ASCII dashboard."""
    prefix = "[GHOST MODE]" if is_ghost else "[CORTEX STATUS]"

    print(f"\n{'=' * 60}")
    print(f"  {prefix}")
    print(f"{'=' * 60}\n")

    # Health
    health = status_data.get("health", "unknown")
    print(f"  Health:      {health.upper()}")
    print(f"  Instance:    {status_data.get('instance_id', 'unknown')}")

    if is_ghost and ghost_age:
        seconds = int(ghost_age.total_seconds())
        print(f"  Cache Age:   {seconds}s (Ghost mode - cached data)")

    # Agents
    agents = status_data.get("agents", [])
    print(f"\n  Agents ({len(agents)}):")
    if agents:
        for agent in agents:
            name = agent.get("name", "unknown")
            genus = agent.get("genus", "?")
            status = agent.get("status", "unknown")
            print(f"    - {name} ({genus}): {status}")
    else:
        print("    (none)")

    # Components
    components = status_data.get("components", [])
    if components:
        print(f"\n  Components ({len(components)}):")
        for comp in components:
            name = comp.get("name", "unknown")
            healthy = comp.get("healthy", False)
            message = comp.get("message", "")
            status_icon = "✓" if healthy else "✗"
            print(
                f"    {status_icon} {name}: {message if message else ('OK' if healthy else 'NOT OK')}"
            )

    # Pheromone levels
    pheromones = status_data.get("pheromone_levels", {})
    if pheromones:
        print("\n  Pheromone Levels:")
        for ptype, level in pheromones.items():
            print(f"    - {ptype}: {level:.2f}")

    # Metabolic pressure
    pressure = status_data.get("metabolic_pressure", 0.0)
    if pressure > 0:
        print(f"\n  Metabolic Pressure: {pressure:.2f}")

    print(f"\n{'=' * 60}\n")


def _get_ghost_status_line(project_root: Path) -> str | None:
    """Read ghost health.status if available."""
    health_path = project_root / ".kgents" / "ghost" / "health.status"
    if health_path.exists():
        try:
            return health_path.read_text().strip()
        except Exception:
            pass
    return None


def _get_ghost_context(project_root: Path) -> dict[str, Any] | None:
    """Read ghost context.json if available."""
    context_path = project_root / ".kgents" / "ghost" / "context.json"
    if context_path.exists():
        try:
            return cast(dict[str, Any], json_module.loads(context_path.read_text()))
        except Exception:
            pass
    return None


def _merge_status_lines(cortex_line: str, ghost_status: str) -> str:
    """
    Merge cortex and ghost status lines into unified format.

    Example:
        cortex: [CORTEX] OK HEALTHY | L:45ms R:12ms | H:45/100 | S:0.3 | Dreams:12
        ghost:  cortex:healthy | branch:main dirty:3 | flinch:0h/5d | infra:running
        merged: [CORTEX] OK HEALTHY | L:45ms | branch:main dirty:3 | flinch:0h/5d
    """
    # Extract meaningful parts from ghost (skip redundant cortex status)
    ghost_parts = ghost_status.split(" | ")
    # Filter out 'cortex:...' since we have better data from dashboard
    meaningful = [p for p in ghost_parts if not p.startswith("cortex:")]

    if not meaningful:
        return cortex_line

    # Append ghost data to cortex line
    return f"{cortex_line} | {' | '.join(meaningful)}"


def _build_json_output_from_data(
    status_data: dict[str, Any],
    project_root: Path,
    cortex_only: bool,
) -> dict[str, Any]:
    """Build comprehensive JSON output from status data dict."""
    output = dict(status_data)

    if not cortex_only:
        ghost_context = _get_ghost_context(project_root)
        if ghost_context:
            output["ghost"] = ghost_context

    return output


def _print_ghost_panel(project_root: Path) -> None:
    """Print ghost panel for full mode."""
    ghost_status = _get_ghost_status_line(project_root)
    ghost_context = _get_ghost_context(project_root)

    if not ghost_status and not ghost_context:
        return

    print()
    print("-- Ghost (Living Filesystem) --")
    if ghost_status:
        print(f"  Status: {ghost_status}")
    if ghost_context:
        print(f"  Last projection: {ghost_context.get('timestamp', 'unknown')}")
        print(f"  Projection count: {ghost_context.get('projection_count', 0)}")
        if "hydrate_current" in ghost_context:
            print(f"  HYDRATE: {ghost_context['hydrate_current']}")


# =============================================================================
# Glass Cache Debugging (--ghost mode)
# =============================================================================


def _show_glass_cache_status() -> int:
    """
    Show Glass cache status for debugging.

    Used by `kgents status --ghost` to inspect the cached state.
    Uses GhostCache from glass.py (the canonical implementation).
    """
    try:
        from datetime import datetime

        from protocols.cli.glass import GHOST_DIR, GhostCache

        cache = GhostCache()

        print("[GLASS CACHE] Status")
        print(f"  Location: {GHOST_DIR}")

        # Check what entries exist
        if not GHOST_DIR.exists():
            print("  Status: Not initialized")
            print()
            print("  No cached data. Run 'kgents status' to populate cache.")
            return 0

        # List cache entries
        entries = []
        for json_file in GHOST_DIR.glob("*.json"):
            if json_file.name == "meta.json":
                continue
            key = json_file.stem
            data, age, timestamp = cache.read(key)
            if data is not None:
                entries.append(
                    {
                        "key": key,
                        "age": age,
                        "timestamp": timestamp,
                    }
                )

        print(f"  Entries: {len(entries)}")
        print()

        if entries:
            print("  Cached data:")
            for entry in entries:
                raw_age = entry["age"]
                entry_age: timedelta | None = (
                    raw_age if isinstance(raw_age, timedelta) else None
                )
                if entry_age is not None:
                    seconds = int(entry_age.total_seconds())
                    if seconds < 60:
                        age_str = f"{seconds}s ago"
                    elif seconds < 3600:
                        age_str = f"{seconds // 60}m ago"
                    else:
                        age_str = f"{seconds // 3600}h ago"
                else:
                    age_str = "unknown age"
                print(f"    - {entry['key']}: {age_str}")
        else:
            print("  No cached data. Run 'kgents status' to populate cache.")

        # Show meta info
        meta = cache.get_meta()
        if meta.get("last_updated"):
            print()
            print(f"  Last updated: {meta['last_updated']}")

        return 0

    except ImportError as e:
        print(f"[ERROR] Glass module not available: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Failed to read Glass cache: {e}")
        return 1
