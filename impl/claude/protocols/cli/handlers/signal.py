"""
Signal Handler: SemanticField emit/sense operations.

DevEx V4 Phase 1 - Foundation Layer.
Glass Terminal Integration: Uses GlassClient with 3-layer fallback.

Agents coordinate via stigmergic pheromones in the semantic field.
This handler provides direct access to the field for debugging and testing.

Usage:
    kgents signal                 # Show current field state
    kgents signal emit <kind>     # Emit a signal of given kind
    kgents signal sense <kind>    # Sense signals of given kind
    kgents signal tick            # Trigger decay tick
    kgents signal --ghost         # Show cached field state

Signal Kinds:
    METAPHOR    - Psi-gent: Functor mappings (slow decay)
    INTENT      - F-gent: Artifact intentions (moderate decay)
    WARNING     - J-gent: Safety alerts (fast decay)
    OPPORTUNITY - B-gent: Economic signals (moderate decay)
    SCARCITY    - B-gent: Resource constraints (faster decay)
    MEMORY      - M-gent: Memory consolidation (slow decay)
    NARRATIVE   - N-gent: Story threads (moderate decay)
    CAPABILITY  - L-gent: Agent capabilities (very slow decay)

Example output:
    [FIELD] Active | Pheromones: 12 | Tick: 45

    By Kind:
      METAPHOR:    3 (strongest: 0.85)
      WARNING:     1 (strongest: 0.92)
      CAPABILITY:  8 (strongest: 1.00)

Architecture:
    This handler is "hollowed" - it delegates to GlassClient which implements:
    1. Try gRPC call to Cortex daemon (Invoke RPC)
    2. On gRPC failure, try local CortexServicer (in-process)
    3. On local failure, read from Ghost cache (last-known-good)
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, cast


def cmd_signal(args: list[str]) -> int:
    """
    Interact with the SemanticField.

    This is a "hollowed" handler - it delegates to GlassClient for the
    three-layer fallback strategy (gRPC → local → Ghost cache).
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    json_mode = "--json" in args
    ghost_mode = "--ghost" in args

    if help_mode:
        print(__doc__)
        return 0

    # Ghost mode: show cached field state
    if ghost_mode:
        return _show_ghost_field_state()

    # Determine subcommand
    subcommand = None
    sub_args = []
    for arg in args:
        if not arg.startswith("-"):
            if subcommand is None:
                subcommand = arg
            else:
                sub_args.append(arg)

    # Run async signal command
    return asyncio.run(
        _async_signal(
            subcommand=subcommand,
            sub_args=sub_args,
            json_mode=json_mode,
        )
    )


async def _async_signal(
    subcommand: str | None = None,
    sub_args: list[str] | None = None,
    json_mode: bool = False,
) -> int:
    """
    Async implementation of signal command using GlassClient.

    Uses Invoke RPC with self.field.* paths for field operations.
    """
    from protocols.cli.glass import get_glass_client

    client = get_glass_client()
    sub_args = sub_args or []

    try:
        if subcommand == "emit":
            return await _emit_signal_via_glass(client, sub_args)
        elif subcommand == "sense":
            return await _sense_signals_via_glass(client, sub_args, json_mode)
        elif subcommand == "tick":
            return await _do_tick_via_glass(client)
        else:
            return await _show_field_status_via_glass(client, json_mode)

    except ConnectionError as e:
        print(f"[FIELD] X OFFLINE | {e}")
        print("  Run 'kgents infra init' to start the Cortex daemon.")
        return 1

    except Exception as e:
        print(f"[FIELD] X ERROR | {e}")
        return 1


async def _show_field_status_via_glass(client: Any, json_mode: bool) -> int:
    """
    Show current field status via GlassClient.

    Uses Invoke RPC with path: self.field.manifest
    """
    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.field.manifest",
            lens="optics.identity",
        )
    except ImportError:

        class SimpleRequest:
            def __init__(self, path: str, lens: str):
                self.path = path
                self.lens = lens

        request = SimpleRequest(path="self.field.manifest", lens="optics.identity")

    response = await client.invoke(
        method="Invoke",
        request=request,
        ghost_key="signal",
        agentese_path="self.field.manifest",
    )

    field_data = _extract_field_data(response.data)

    if json_mode:
        output = field_data
        if response.is_ghost:
            output["_ghost"] = {
                "is_cached": True,
                "age_seconds": response.ghost_age.total_seconds()
                if response.ghost_age
                else None,
            }
        print(json.dumps(output, indent=2))
        return 0

    # Human-readable output
    _print_field_status(field_data, response.is_ghost, response.ghost_age)
    return 0


async def _emit_signal_via_glass(client: Any, args: list[str]) -> int:
    """
    Emit a signal via GlassClient.

    Uses Invoke RPC with path: self.field.emit
    """
    if not args:
        print("Usage: kgents signal emit <kind>")
        print()
        print("Available kinds:")
        print("  METAPHOR, INTENT, WARNING, OPPORTUNITY,")
        print("  SCARCITY, MEMORY, NARRATIVE, CAPABILITY")
        return 1

    kind_name = args[0].upper()
    message = args[1] if len(args) > 1 else "manual signal"

    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.field.emit",
            lens="optics.identity",
            kwargs={
                "kind": kind_name,
                "message": message,
                "source": "cli",
            },
        )
    except ImportError:

        class SimpleRequest:
            def __init__(self, path: str, lens: str, kwargs: dict[str, Any]):
                self.path = path
                self.lens = lens
                self.kwargs = kwargs

        request = SimpleRequest(
            path="self.field.emit",
            lens="optics.identity",
            kwargs={
                "kind": kind_name,
                "message": message,
                "source": "cli",
            },
        )

    response = await client.invoke(
        method="Invoke",
        request=request,
        agentese_path="self.field.emit",
    )

    result = _extract_invoke_result(response.data)

    if "error" in result:
        print(f"[FIELD] ! ERROR | {result['error']}")
        return 1

    pheromone_id = result.get("pheromone_id", "unknown")
    print(f"[FIELD] Emitted {kind_name}: {pheromone_id}")
    return 0


async def _sense_signals_via_glass(
    client: Any, args: list[str], json_mode: bool
) -> int:
    """
    Sense signals via GlassClient.

    Uses Invoke RPC with path: self.field.sense
    """
    kind_name = args[0].upper() if args else None

    kwargs = {"radius": "10.0"}
    if kind_name:
        kwargs["kind"] = kind_name

    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.field.sense",
            lens="optics.identity",
            kwargs=kwargs,
        )
    except ImportError:

        class SimpleRequest:
            def __init__(self, path: str, lens: str, kwargs: dict[str, Any]):
                self.path = path
                self.lens = lens
                self.kwargs = kwargs

        request = SimpleRequest(
            path="self.field.sense",
            lens="optics.identity",
            kwargs=kwargs,
        )

    response = await client.invoke(
        method="Invoke",
        request=request,
        agentese_path="self.field.sense",
    )

    result = _extract_invoke_result(response.data)
    pheromones = result.get("pheromones", [])

    if json_mode:
        print(json.dumps(pheromones, indent=2))
        return 0

    kind_label = kind_name if kind_name else "ALL"
    print(f"[SENSE] {kind_label}: {len(pheromones)} signals")
    print()

    if not pheromones:
        print("  No signals sensed.")
        return 0

    for p in pheromones[:10]:
        kind = p.get("kind", "unknown")
        emitter = p.get("emitter", "unknown")
        intensity = p.get("intensity", 0.0)
        print(f"  [{kind}] {emitter}: {intensity:.2f}")
        payload = p.get("payload")
        if payload:
            payload_str = str(payload)[:50]
            print(f"    payload: {payload_str}")

    if len(pheromones) > 10:
        print(f"  ... and {len(pheromones) - 10} more")

    return 0


async def _do_tick_via_glass(client: Any) -> int:
    """
    Trigger a decay tick via GlassClient.

    Uses Invoke RPC with path: self.field.tick
    """
    try:
        from protocols.proto.generated import InvokeRequest

        request: Any = InvokeRequest(
            path="self.field.tick",
            lens="optics.identity",
        )
    except ImportError:

        class SimpleRequest:
            def __init__(self, path: str, lens: str):
                self.path = path
                self.lens = lens

        request = SimpleRequest(path="self.field.tick", lens="optics.identity")

    response = await client.invoke(
        method="Invoke",
        request=request,
        agentese_path="self.field.tick",
    )

    result = _extract_invoke_result(response.data)

    tick = result.get("tick", "?")
    before = result.get("before", "?")
    after = result.get("after", "?")

    print(f"[FIELD] Tick {tick} | {before} -> {after} active pheromones")
    return 0


def _extract_field_data(data: Any) -> dict[str, Any]:
    """Extract field data from GlassResponse data."""
    if isinstance(data, dict):
        if "result" in data:
            return data["result"] if isinstance(data["result"], dict) else data
        return data

    # Handle InvokeResponse
    if hasattr(data, "result_json"):
        try:
            result = json.loads(data.result_json)
            return result if isinstance(result, dict) else {"raw": result}
        except (json.JSONDecodeError, TypeError):
            pass

    # Protobuf message
    if hasattr(data, "DESCRIPTOR"):
        try:
            from google.protobuf.json_format import MessageToDict

            return cast(
                dict[str, Any], MessageToDict(data, preserving_proto_field_name=True)
            )
        except ImportError:
            pass

    return {"raw": str(data)}


def _extract_invoke_result(data: Any) -> dict[str, Any]:
    """Extract result from InvokeResponse."""
    if isinstance(data, dict):
        if "result" in data:
            return data["result"] if isinstance(data["result"], dict) else data
        return data

    if hasattr(data, "result_json"):
        try:
            return cast(dict[str, Any], json.loads(data.result_json))
        except (json.JSONDecodeError, TypeError):
            pass

    return {"error": "Unable to parse result"}


def _print_field_status(
    field_data: dict[str, Any],
    is_ghost: bool = False,
    ghost_age: Any = None,
) -> None:
    """Print human-readable field status."""
    prefix = "[GHOST]" if is_ghost else "[FIELD]"

    tick = field_data.get("tick", 0)
    active_count = field_data.get("active_count", 0)
    by_kind = field_data.get("by_kind", {})

    print(f"{prefix} Active | Pheromones: {active_count} | Tick: {tick}")

    if is_ghost and ghost_age:
        seconds = int(ghost_age.total_seconds())
        print(f"  (Cached data from {seconds}s ago)")

    print()

    if not by_kind:
        print("  No active pheromones in field.")
        print("  Use 'kgents signal emit <kind>' to emit a signal.")
        return

    print("By Kind:")
    for kind_name, stats in by_kind.items():
        count = stats.get("count", 0)
        strongest = stats.get("strongest", 0.0)
        if count > 0:
            print(f"  {kind_name:12} {count:3} (strongest: {strongest:.2f})")

    # Show recent signals if available
    pheromones = field_data.get("pheromones", [])
    if pheromones:
        print()
        print("Recent Signals:")
        for p in pheromones[:5]:
            kind = p.get("kind", "unknown")
            emitter = p.get("emitter", "unknown")
            intensity = p.get("intensity", 0.0)
            print(f"  [{kind}] {emitter}: intensity={intensity:.2f}")


def _show_ghost_field_state() -> int:
    """Show cached field state for debugging."""
    try:
        from protocols.cli.glass import GhostCache

        cache = GhostCache()
        data, age, timestamp = cache.read("signal")

        if data is None:
            print("[GHOST] No cached field state available.")
            print("  Run 'kgents signal' to populate cache.")
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

        print(f"[GHOST] Cached field state from {age_str} ago:")
        print()

        # Display cached data
        field_data = _extract_field_data(data)
        _print_field_status(field_data, is_ghost=True, ghost_age=age)

        return 0

    except Exception as e:
        print(f"[ERROR] Failed to read Ghost cache: {e}")
        return 1
