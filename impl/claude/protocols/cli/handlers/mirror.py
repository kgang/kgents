"""
Mirror Protocol CLI handlers.

The Mirror Protocol is a composition of five agents: P >> W >> H >> O >> J

Operations:
- observe: Full analysis (P >> W >> H >> O)
- reflect: Generate synthesis options for a tension
- status: Show current integrity score
- hold: Mark a tension as productive (preserve it)
- watch: Autonomous observation mode (J-gent Kairos) - future

Token cost: 0 (structural analysis only, no LLM calls)
"""

from __future__ import annotations

from typing import Sequence


def cmd_mirror(args: Sequence[str]) -> int:
    """Handle mirror protocol commands."""
    if not args or args[0] in ("--help", "-h"):
        print("kgents mirror - Mirror Protocol (P >> W >> H >> O >> J)")
        print()
        print("USAGE:")
        print("  kgents mirror <operation> [options]")
        print()
        print("OPERATIONS:")
        print(
            "  observe <path>     Full analysis (extracts principles, observes patterns,"
        )
        print("                     detects tensions, generates report)")
        print("  status [path]      Show current integrity score")
        print("  reflect [index]    Generate synthesis options for tension")
        print("  tensions           List all detected tensions")
        print("  hold <index>       Mark tension as productive")
        print()
        print("EXAMPLES:")
        print("  kgents mirror observe ~/Documents/Vault")
        print("  kgents mirror status")
        print("  kgents mirror reflect 0")
        print("  kgents mirror hold 1")
        return 0

    operation = args[0]
    op_args = list(args[1:])

    handlers = {
        "observe": _cmd_observe,
        "status": _cmd_status,
        "reflect": _cmd_reflect,
        "tensions": _cmd_tensions,
        "hold": _cmd_hold,
        "watch": _cmd_watch,
    }

    if operation in handlers:
        return handlers[operation](op_args)
    else:
        print(f"Unknown mirror operation: {operation}")
        print("Run 'kgents mirror --help' for available operations.")
        return 1


def _cmd_observe(args: list[str]) -> int:
    """Handle mirror observe - full P >> W >> H >> O composition."""
    from pathlib import Path

    from ...mirror.composition import mirror_observe, format_report

    path = Path(args[0]).expanduser() if args else Path.cwd()

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        return 1

    print(f"Observing: {path}")
    print("Running P-gent >> W-gent >> H-gent >> O-gent composition...")
    print()

    try:
        report = mirror_observe(path)
        print(format_report(report))

        if report.all_tensions:
            print()
            print("Run 'kgents mirror reflect 0' to explore synthesis options.")
        return 0
    except Exception as e:
        print(f"Error during observation: {e}")
        return 1


def _cmd_status(args: list[str]) -> int:
    """Handle mirror status."""
    from pathlib import Path

    from ...mirror.composition import mirror_status, format_status

    path = Path(args[0]).expanduser() if args else None

    try:
        status = mirror_status(path)
        print(format_status(status))
        return 0
    except Exception as e:
        print(f"Error getting status: {e}")
        return 1


def _cmd_reflect(args: list[str]) -> int:
    """Handle mirror reflect - generate synthesis options."""
    from ...mirror.composition import mirror_reflect, format_synthesis_options

    tension_index = int(args[0]) if args else 0

    try:
        options = mirror_reflect(tension_index)
        print(format_synthesis_options(options))
        return 0
    except Exception as e:
        print(f"Error generating synthesis: {e}")
        return 1


def _cmd_tensions(args: list[str]) -> int:
    """Handle mirror tensions - list all detected tensions."""
    from ...mirror.composition import _last_report, format_tensions

    if _last_report is None:
        print("No cached analysis. Run 'kgents mirror observe <path>' first.")
        return 1

    print(format_tensions(_last_report.all_tensions))
    return 0


def _cmd_hold(args: list[str]) -> int:
    """Handle mirror hold - mark tension as productive."""
    from ...mirror.composition import mirror_hold
    from ...mirror.types import HoldReason

    if not args:
        print("Error: tension index required")
        print("Usage: kgents mirror hold <index> [reason]")
        return 1

    try:
        tension_index = int(args[0])
        reason_str = args[1] if len(args) > 1 else "productive"

        # Map string to HoldReason
        reason_map = {
            "productive": HoldReason.PRODUCTIVE,
            "premature": HoldReason.PREMATURE,
            "external": HoldReason.EXTERNAL_DEPENDENCY,
            "cost": HoldReason.HIGH_COST,
            "kairos": HoldReason.KAIROS,
        }
        reason = reason_map.get(reason_str.lower(), HoldReason.PRODUCTIVE)

        hold = mirror_hold(tension_index, reason)
        if hold:
            print(f"Tension {tension_index} held as {reason.value}")
            print(f"Reason: {hold.why_held}")
            return 0
        else:
            print(f"Error: Invalid tension index {tension_index}")
            return 1
    except ValueError:
        print(f"Error: Invalid index '{args[0]}' - must be a number")
        return 1


def _cmd_watch(args: list[str]) -> int:
    """Handle mirror watch (Kairos mode) - autonomous observation."""
    print("Mirror watch: Autonomous observation mode")
    print()
    print("This feature uses the J-gent Kairos controller for opportune timing.")
    print("Coming in Phase 2 of the Mirror implementation.")
    print()
    print("For now, use 'kgents mirror observe' for single-pass analysis.")
    return 0
