"""
Membrane Protocol CLI handlers.

The Membrane Protocol provides topological perception of a codebase or knowledge vault.
It detects "shapes" - patterns of alignment/misalignment between stated principles and
actual behavior.

Note: The underlying Mirror composition (P >> W >> H >> O >> J) has been deprecated.
Membrane functionality is being rebuilt on top of:
- D-gent (state persistence via instance_db)
- L-gent (semantic analysis)
- The new unified cortex architecture

For now, membrane commands provide helpful stubs that explain the transition.
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
        print("  sense [path]       Quick shape intuition (<100ms)")
        print("  status             Show current shape state")
        print("  shapes             List detected shapes (tensions)")
        print("  touch <index>      Acknowledge a shape")
        print("  hold <index>       Preserve productive tension")
        print()
        print("STATUS:")
        print("  The Membrane Protocol is being rebuilt on the new cortex")
        print("  architecture (D-gent + L-gent + instance_db).")
        print()
        print("  For now, use 'kgents check <path>' for codebase analysis.")
        print()
        print("EXAMPLES:")
        print("  kgents membrane observe ~/project")
        print("  kgents membrane sense")
        return 0

    operation = args[0]
    op_args = list(args[1:])

    handlers = {
        "observe": _cmd_observe,
        "sense": _cmd_sense,
        "status": _cmd_status,
        "shapes": _cmd_shapes,
        "touch": _cmd_touch,
        "hold": _cmd_hold,
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
    """Alias for membrane trace (not yet implemented)."""
    print("[membrane] trace: Not yet implemented on new cortex architecture.")
    print("           Use 'kgents check <path>' for codebase analysis.")
    return 1


def cmd_touch(args: Sequence[str]) -> int:
    """Alias for membrane touch."""
    return _cmd_touch(list(args))


def cmd_name(args: Sequence[str]) -> int:
    """Alias for membrane name (not yet implemented)."""
    print("[membrane] name: Not yet implemented on new cortex architecture.")
    return 1


# Implementation stubs
def _cmd_observe(args: list[str]) -> int:
    """Handle membrane observe - topological observation."""
    from pathlib import Path

    path = Path(args[0]).expanduser() if args else Path.cwd()

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        return 1

    print(f"[membrane] observe: {path}")
    print()
    print("The Membrane Protocol is being rebuilt on the new cortex architecture.")
    print("The original Mirror composition (P >> W >> H >> O >> J) has been deprecated")
    print("in favor of:")
    print()
    print("  - D-gent: State persistence via instance_db")
    print("  - L-gent: Semantic analysis and embedding")
    print("  - Unified Cortex: Auto-bootstrapping infrastructure")
    print()
    print("For codebase analysis, use: kgents check <path>")
    print("For principle verification: kgents judge <path>")
    return 0


def _cmd_sense(args: list[str]) -> int:
    """Handle membrane sense - quick shape intuition."""
    print("[membrane] sense: Quick observation")
    print()
    print("Status: Rebuilding on new cortex architecture.")
    print("Use 'kgents check <path>' for codebase analysis.")
    return 0


def _cmd_status(args: list[str]) -> int:
    """Handle membrane status."""
    print("--- Membrane Status ---")
    print()
    print("Protocol: Transitioning to new architecture")
    print("Storage: instance_db (D-gent)")
    print("Analysis: L-gent semantic layer")
    print()
    print("The original Mirror composition has been deprecated.")
    print("Run 'kgents membrane --help' for more information.")
    return 0


def _cmd_shapes(args: list[str]) -> int:
    """Handle membrane shapes - list detected shapes."""
    print("--- Detected Shapes ---")
    print()
    print("No shapes cached. The Membrane Protocol is being rebuilt.")
    print("Run 'kgents membrane observe <path>' to trigger analysis.")
    return 0


def _cmd_touch(args: list[str]) -> int:
    """Handle membrane touch - acknowledge a shape."""
    if not args:
        print("Error: shape index required")
        print("Usage: kgents membrane touch <index>")
        return 1

    print(f"[membrane] touch {args[0]}: Not yet implemented on new architecture.")
    return 1


def _cmd_hold(args: list[str]) -> int:
    """Handle membrane hold - preserve productive tension."""
    if not args:
        print("Error: shape index required")
        print("Usage: kgents membrane hold <index>")
        return 1

    print(f"[membrane] hold {args[0]}: Not yet implemented on new architecture.")
    return 1
