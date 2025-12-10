"""
Membrane Protocol CLI handlers.

The Membrane Protocol enables topological perception:
- Observe: Full topological analysis (curvature, void, flow, dampening)
- Sense: Quick shape intuition (<100ms)
- Trace: Follow topic momentum
- Touch: Acknowledge a shape
- Name: Give voice to a void
"""

from __future__ import annotations

from typing import Sequence


def cmd_membrane(args: Sequence[str]) -> int:
    """Handle membrane protocol commands."""
    if not args or args[0] in ("--help", "-h"):
        print("kgents membrane - Membrane Protocol (topological perception)")
        print()
        print("USAGE:")
        print("  kgents membrane <operation> [options]")
        print()
        print("OPERATIONS:")
        print("  observe <path>     Full topological observation")
        print("  sense              Quick shape intuition (<100ms)")
        print("  trace <topic>      Follow topic momentum")
        print("  touch <shape-id>   Acknowledge a shape")
        print("  name <description> Give voice to a void")
        print("  hold <shape-id>    Preserve productive tension")
        print("  release <shape-id> Allow natural resolution")
        print()
        print("EXAMPLES:")
        print("  kgents membrane observe ~/project")
        print("  kgents membrane sense")
        print("  kgents membrane trace 'authentication'")
        return 0

    operation = args[0]
    op_args = list(args[1:])

    handlers = {
        "observe": _cmd_observe,
        "sense": _cmd_sense,
        "trace": _cmd_trace,
        "touch": _cmd_touch,
        "name": _cmd_name,
        "hold": _cmd_hold,
        "release": _cmd_release,
    }

    if operation in handlers:
        return handlers[operation](op_args)
    else:
        print(f"Unknown membrane operation: {operation}")
        print("Run 'kgents membrane --help' for available operations.")
        return 1


# Top-level aliases
def cmd_observe(args: Sequence[str]) -> int:
    """Alias for membrane observe."""
    return _cmd_observe(list(args))


def cmd_sense(args: Sequence[str]) -> int:
    """Alias for membrane sense."""
    return _cmd_sense(list(args))


def cmd_trace(args: Sequence[str]) -> int:
    """Alias for membrane trace."""
    return _cmd_trace(list(args))


def cmd_touch(args: Sequence[str]) -> int:
    """Alias for membrane touch."""
    return _cmd_touch(list(args))


def cmd_name(args: Sequence[str]) -> int:
    """Alias for membrane name."""
    return _cmd_name(list(args))


# Implementation
def _cmd_observe(args: list[str]) -> int:
    """Handle membrane observe."""
    from pathlib import Path

    path = Path(args[0]).expanduser() if args else Path.cwd()
    print(f"Membrane observe: {path}")
    print()
    print("Topological perception not yet implemented in hollow shell.")
    print("This would analyze: curvature, void (ma), flow, dampening.")
    return 0


def _cmd_sense(args: list[str]) -> int:
    """Handle membrane sense (<100ms intuition)."""
    print("Membrane sense: Quick shape intuition")
    print()
    print("Would perceive dominant shapes without full analysis.")
    print("Target: <100ms response time.")
    return 0


def _cmd_trace(args: list[str]) -> int:
    """Handle membrane trace."""
    if not args:
        print("Error: topic required")
        print("Usage: kgents trace <topic>")
        return 1
    topic = args[0]
    print(f"Tracing topic momentum: {topic}")
    print("Not yet implemented in hollow shell.")
    return 0


def _cmd_touch(args: list[str]) -> int:
    """Handle membrane touch."""
    if not args:
        print("Error: shape-id required")
        print("Usage: kgents touch <shape-id>")
        return 1
    shape_id = args[0]
    print(f"Touching shape: {shape_id}")
    print("Not yet implemented in hollow shell.")
    return 0


def _cmd_name(args: list[str]) -> int:
    """Handle membrane name (give voice to void)."""
    if not args:
        print("Error: description required")
        print("Usage: kgents name <description>")
        return 1
    description = " ".join(args)
    print(f"Naming the void: {description}")
    print()
    print("This is the most powerful gesture: naming the unsaid.")
    print("Not yet implemented in hollow shell.")
    return 0


def _cmd_hold(args: list[str]) -> int:
    """Handle membrane hold."""
    if not args:
        print("Error: shape-id required")
        return 1
    print(f"Holding shape: {args[0]}")
    print("Not yet implemented in hollow shell.")
    return 0


def _cmd_release(args: list[str]) -> int:
    """Handle membrane release."""
    if not args:
        print("Error: shape-id required")
        return 1
    print(f"Releasing shape: {args[0]}")
    print("Not yet implemented in hollow shell.")
    return 0
