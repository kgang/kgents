"""
Signal Handler: SemanticField emit/sense operations.

DevEx V4 Phase 1 - Foundation Layer.

Agents coordinate via stigmergic pheromones in the semantic field.
This handler provides direct access to the field for debugging and testing.

Usage:
    kgents signal                 # Show current field state
    kgents signal emit <kind>     # Emit a signal of given kind
    kgents signal sense <kind>    # Sense signals of given kind
    kgents signal tick            # Trigger decay tick

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
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


def cmd_signal(args: list[str]) -> int:
    """
    Interact with the SemanticField.

    Provides direct access to the stigmergic coordination layer.
    """
    # Parse args
    help_mode = "--help" in args or "-h" in args
    json_mode = "--json" in args

    if help_mode:
        print(__doc__)
        return 0

    # Determine subcommand
    subcommand = None
    sub_args = []
    for arg in args:
        if not arg.startswith("-"):
            if subcommand is None:
                subcommand = arg
            else:
                sub_args.append(arg)

    # Get or create field
    from protocols.cli.hollow import get_lifecycle_state

    state = get_lifecycle_state()
    field = _get_or_create_field(state)

    if subcommand == "emit":
        return _emit_signal(field, sub_args)
    elif subcommand == "sense":
        return _sense_signals(field, sub_args, json_mode)
    elif subcommand == "tick":
        return _do_tick(field)
    else:
        return _show_field_status(field, json_mode)


def _get_or_create_field(state):
    """Get or create SemanticField."""
    if state is not None and hasattr(state, "semantic_field"):
        return state.semantic_field

    from agents.i.semantic_field import create_semantic_field

    return create_semantic_field()


def _show_field_status(field, json_mode: bool) -> int:
    """Show current field status."""
    from agents.i.semantic_field import SemanticPheromoneKind

    # Gather stats
    active = [p for p in field._pheromones.values() if p.is_active]
    by_kind: dict[str, list] = {}
    for p in active:
        kind_name = p.kind.name
        if kind_name not in by_kind:
            by_kind[kind_name] = []
        by_kind[kind_name].append(p)

    if json_mode:
        print(
            json.dumps(
                {
                    "tick": field._current_tick,
                    "active_count": len(active),
                    "by_kind": {
                        k: {
                            "count": len(v),
                            "strongest": max(p.intensity for p in v) if v else 0,
                        }
                        for k, v in by_kind.items()
                    },
                    "pheromones": [
                        {
                            "id": p.id,
                            "kind": p.kind.name,
                            "emitter": p.emitter,
                            "intensity": p.intensity,
                        }
                        for p in active[:20]  # Limit output
                    ],
                },
                indent=2,
            )
        )
        return 0

    # Human-readable output
    print(f"[FIELD] Active | Pheromones: {len(active)} | Tick: {field._current_tick}")
    print()

    if not active:
        print("  No active pheromones in field.")
        print("  Use 'kgents signal emit <kind>' to emit a signal.")
        return 0

    print("By Kind:")
    for kind in SemanticPheromoneKind:
        pheromones = by_kind.get(kind.name, [])
        if pheromones:
            strongest = max(p.intensity for p in pheromones)
            print(f"  {kind.name:12} {len(pheromones):3} (strongest: {strongest:.2f})")

    # Show recent signals
    print()
    print("Recent Signals:")
    recent = sorted(active, key=lambda p: p.created_at, reverse=True)[:5]
    for p in recent:
        print(f"  [{p.kind.name}] {p.emitter}: intensity={p.intensity:.2f}")

    return 0


def _emit_signal(field, args: list[str]) -> int:
    """Emit a signal to the field."""
    from agents.i.semantic_field import FieldCoordinate, SemanticPheromoneKind

    if not args:
        print("Usage: kgents signal emit <kind>")
        print()
        print("Available kinds:")
        for kind in SemanticPheromoneKind:
            print(f"  {kind.name}")
        return 1

    kind_name = args[0].upper()

    try:
        kind = SemanticPheromoneKind[kind_name]
    except KeyError:
        print(f"Unknown signal kind: {kind_name}")
        print()
        print("Available kinds:")
        for k in SemanticPheromoneKind:
            print(f"  {k.name}")
        return 1

    # Emit with default position (origin)
    position = FieldCoordinate(embedding=[0.0] * 384, label="CLI")

    # Payload based on kind
    payload = {
        "source": "cli",
        "message": args[1] if len(args) > 1 else "manual signal",
    }

    pheromone_id = field.emit(
        emitter="cli",
        kind=kind,
        payload=payload,
        position=position,
        intensity=1.0,
    )

    print(f"[FIELD] Emitted {kind.name}: {pheromone_id}")
    return 0


def _sense_signals(field, args: list[str], json_mode: bool) -> int:
    """Sense signals in the field."""
    from agents.i.semantic_field import FieldCoordinate, SemanticPheromoneKind

    # Parse kind filter
    kind = None
    if args:
        kind_name = args[0].upper()
        try:
            kind = SemanticPheromoneKind[kind_name]
        except KeyError:
            print(f"Unknown signal kind: {kind_name}")
            return 1

    # Sense from origin
    position = FieldCoordinate(embedding=[0.0] * 384, label="CLI")
    pheromones = field.sense(position, radius=10.0, kind=kind)

    if json_mode:
        print(
            json.dumps(
                [
                    {
                        "id": p.id,
                        "kind": p.kind.name,
                        "emitter": p.emitter,
                        "intensity": p.intensity,
                        "payload": str(p.payload),
                    }
                    for p in pheromones
                ],
                indent=2,
            )
        )
        return 0

    kind_label = kind.name if kind else "ALL"
    print(f"[SENSE] {kind_label}: {len(pheromones)} signals")
    print()

    if not pheromones:
        print("  No signals sensed.")
        return 0

    for p in pheromones[:10]:
        print(f"  [{p.kind.name}] {p.emitter}: {p.intensity:.2f}")
        if p.payload:
            payload_str = str(p.payload)[:50]
            print(f"    payload: {payload_str}")

    if len(pheromones) > 10:
        print(f"  ... and {len(pheromones) - 10} more")

    return 0


def _do_tick(field) -> int:
    """Trigger a decay tick."""
    before = len([p for p in field._pheromones.values() if p.is_active])
    field.tick()
    after = len([p for p in field._pheromones.values() if p.is_active])

    print(f"[FIELD] Tick {field._current_tick} | {before} -> {after} active pheromones")
    return 0
