"""
Membrane Protocol CLI handlers.

The Membrane uses the same composition as Mirror but with different vocabulary:
- observe/sense → mirror observe (full vs quick mode)
- trace → follow topic momentum
- touch/hold/release → acknowledge shapes

Per the new spec (spec/protocols/mirror.md), Membrane and Mirror are the same
composition (P >> W >> H >> O >> J) with different metaphors:
- Mirror: dialectical (thesis/antithesis/tension)
- Membrane: topological (curvature/void/flow)

For Phase 1, we implement Membrane by delegating to Mirror.
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
        print("EXAMPLES:")
        print("  kgents membrane observe ~/project")
        print("  kgents membrane sense")
        print("  kgents membrane touch 0")
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


# Implementation - delegates to Mirror composition
def _cmd_observe(args: list[str]) -> int:
    """Handle membrane observe - delegates to mirror observe."""
    from pathlib import Path

    from ...mirror.composition import mirror_observe, format_report

    path = Path(args[0]).expanduser() if args else Path.cwd()

    if not path.exists():
        print(f"Error: Path does not exist: {path}")
        return 1

    print(f"Perceiving shapes: {path}")
    print("Running topological observation (P >> W >> H >> O)...")
    print()

    try:
        report = mirror_observe(path)

        # Translate to membrane vocabulary
        output = _translate_report_to_membrane(report)
        print(output)

        if report.all_tensions:
            print()
            print("Run 'kgents membrane shapes' to see all detected shapes.")
        return 0
    except Exception as e:
        print(f"Error during observation: {e}")
        return 1


def _cmd_sense(args: list[str]) -> int:
    """Handle membrane sense - quick mode observation."""
    from pathlib import Path

    from ...mirror.composition import mirror_observe, format_status, mirror_status

    path = Path(args[0]).expanduser() if args else None

    print("Sensing shape...")
    print()

    try:
        if path:
            # Quick observe
            report = mirror_observe(path, quick=True)
            status = mirror_status(None)  # Use cached
        else:
            status = mirror_status(None)

        # Translate to membrane vocabulary
        print(f"Integrity: {status.integrity_score:.2f} {status.trend_indicator}")
        print(f"Shapes detected: {status.tension_count}")
        print(f"Principles: {status.principle_count}")
        return 0
    except Exception as e:
        print(f"Error sensing: {e}")
        return 1


def _cmd_status(args: list[str]) -> int:
    """Handle membrane status."""
    from ...mirror.composition import mirror_status

    try:
        status = mirror_status(None)
        print("--- Shape Status ---")
        print()
        print(f"Integrity: {status.integrity_score:.2f} {status.trend_indicator}")
        print(f"Shapes: {status.tension_count}")
        print(f"Patterns: {status.pattern_count}")
        return 0
    except Exception as e:
        print(f"Error getting status: {e}")
        return 1


def _cmd_shapes(args: list[str]) -> int:
    """Handle membrane shapes - list detected shapes."""
    from ...mirror.composition import _last_report

    if _last_report is None:
        print("No cached observation. Run 'kgents membrane observe <path>' first.")
        return 1

    if not _last_report.all_tensions:
        print("No shapes detected. Your space shows alignment.")
        return 0

    print("--- Detected Shapes ---")
    print()

    for i, t in enumerate(_last_report.all_tensions[:5]):
        # Translate tension vocabulary to shape vocabulary
        shape_type = {
            "BEHAVIORAL": "curvature",
            "ASPIRATIONAL": "void",
            "OUTDATED": "dampening",
            "CONTEXTUAL": "flow",
            "FUNDAMENTAL": "singularity",
        }.get(t.tension_type.value.upper(), "unknown")

        print(f"[{i}] SHAPE-{i:03d}-{shape_type[:4]}")
        print(f"    {t.thesis.content[:50]}...")
        print(f"    Intensity: {t.divergence:.0%}")
        print()

    return 0


def _cmd_touch(args: list[str]) -> int:
    """Handle membrane touch - acknowledge a shape."""
    from ...mirror.composition import mirror_hold
    from ...mirror.types import HoldReason

    if not args:
        print("Error: shape index required")
        print("Usage: kgents membrane touch <index>")
        return 1

    try:
        index = int(args[0])
        hold = mirror_hold(index, HoldReason.PRODUCTIVE, "Acknowledged via touch")

        if hold:
            print(f"Shape {index} acknowledged.")
            print("The shape persists, but you have named it.")
            return 0
        else:
            print(f"Error: Invalid shape index {index}")
            return 1
    except ValueError:
        print(f"Error: Invalid index '{args[0]}' - must be a number")
        return 1


def _cmd_hold(args: list[str]) -> int:
    """Handle membrane hold - preserve productive tension."""
    from ...mirror.composition import mirror_hold
    from ...mirror.types import HoldReason

    if not args:
        print("Error: shape index required")
        print("Usage: kgents membrane hold <index>")
        return 1

    try:
        index = int(args[0])
        hold = mirror_hold(index, HoldReason.PRODUCTIVE)

        if hold:
            print(f"Shape {index} held as productive.")
            print("This tension will not be resolved prematurely.")
            return 0
        else:
            print(f"Error: Invalid shape index {index}")
            return 1
    except ValueError:
        print(f"Error: Invalid index '{args[0]}' - must be a number")
        return 1


def _translate_report_to_membrane(report) -> str:
    """Translate MirrorReport to membrane vocabulary."""
    from ...mirror.types import TensionType

    lines = [
        "--- Shape Report ---",
        "",
    ]

    if report.all_tensions:
        t = report.all_tensions[0]

        # Translate tension type to shape type
        shape_vocab = {
            TensionType.BEHAVIORAL: ("Curvature", "where tension gathers"),
            TensionType.ASPIRATIONAL: ("Void (Ma)", "what is not being said"),
            TensionType.OUTDATED: ("Dampening", "where expression compresses"),
            TensionType.CONTEXTUAL: ("Flow", "how meaning moves"),
            TensionType.FUNDAMENTAL: ("Singularity", "where resolution collapses"),
        }

        shape_name, shape_desc = shape_vocab.get(
            t.tension_type, ("Unknown", "unclassified shape")
        )

        lines.extend(
            [
                f"Primary Shape: {shape_name}",
                f"Description: {shape_desc}",
                "",
                f"Pattern: {t.thesis.content}",
                f"Observation: {t.antithesis.pattern}",
                "",
                f"Intensity: {t.divergence:.0%}",
                "",
                "Interpretation:",
                t.interpretation or "Examine the gap between stated and actual.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "No significant shapes detected.",
                "Your space shows alignment between stated and actual.",
            ]
        )

    lines.append(f"--- Integrity: {report.integrity_score:.2f} ---")

    return "\n".join(lines)
