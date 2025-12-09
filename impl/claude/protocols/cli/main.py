"""
kgents CLI - The unified command surface.

This is the main entry point for the kgents command-line interface.
Implements the grammar from spec/protocols/cli.md:

    kgents <genus> <operation> [target] [--modifiers] [--constraints]

Examples:
    kgents mirror observe ~/Documents/Vault
    kgents membrane sense
    kgents observe                          # alias for membrane observe
    kgents garden                           # I-gent garden view

The CLI embodies all seven principles at the surface level.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Sequence

from .cli_types import (
    BudgetLevel,
    BudgetStatus,
    CLIContext,
    OutputFormat,
    PersonaMode,
    format_output,
)
from .mirror_cli import MirrorCLI, format_mirror_report_rich
from .membrane_cli import MembraneCLI, format_membrane_observe_rich
from .igent_synergy import (
    StatusWhisper,
    get_whisper_for_prompt,
    run_garden_tui,
)


# =============================================================================
# Argument Parsing
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with full CLI grammar."""

    parser = argparse.ArgumentParser(
        prog="kgents",
        description="kgents - Kent's Agents CLI. Tasteful, curated, ethical, joy-inducing agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kgents mirror observe ~/Documents/Vault   # Observe vault for tensions
  kgents membrane sense                     # Quick shape intuition
  kgents garden                             # Open I-gent garden view
  kgents observe                            # Alias for membrane observe

For more information, see: https://github.com/kgents/kgents
        """,
    )

    # Global flags
    parser.add_argument(
        "--format",
        choices=["code", "value", "json", "jsonl", "rich", "markdown"],
        default="rich",
        help="Output format (default: rich for TTY, json otherwise)",
    )
    parser.add_argument(
        "--budget",
        choices=["minimal", "low", "medium", "high", "unlimited"],
        default="medium",
        help="Entropy budget level (default: medium)",
    )
    parser.add_argument(
        "--persona",
        choices=["warm", "clinical", "playful", "minimal"],
        default="minimal",
        help="Output personality (default: minimal)",
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Show philosophical context for command",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="kgents 0.1.0",
    )

    # Subparsers for genera and protocols
    subparsers = parser.add_subparsers(dest="command", help="Command namespace")

    # ---------------------------------------------------------------------
    # Mirror Protocol
    # ---------------------------------------------------------------------
    mirror_parser = subparsers.add_parser(
        "mirror",
        help="Mirror Protocol - organizational introspection",
    )
    mirror_sub = mirror_parser.add_subparsers(dest="operation", help="Mirror operation")

    # mirror observe
    mirror_observe = mirror_sub.add_parser(
        "observe",
        help="Single-pass analysis of vault/workspace",
    )
    mirror_observe.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to observe (default: current directory)",
    )

    # mirror reflect
    mirror_reflect = mirror_sub.add_parser(
        "reflect",
        help="Generate synthesis options for tension",
    )
    mirror_reflect.add_argument(
        "--tension",
        type=int,
        default=0,
        help="Tension index to reflect on (default: 0)",
    )

    # mirror status
    mirror_sub.add_parser(
        "status",
        help="Show current integrity score",
    )

    # mirror hold
    mirror_hold = mirror_sub.add_parser(
        "hold",
        help="Mark tension as productive",
    )
    mirror_hold.add_argument(
        "tension_index",
        type=int,
        help="Tension index to hold",
    )
    mirror_hold.add_argument(
        "--reason",
        default="Productive tension",
        help="Reason for holding",
    )

    # ---------------------------------------------------------------------
    # Membrane Protocol
    # ---------------------------------------------------------------------
    membrane_parser = subparsers.add_parser(
        "membrane",
        help="Membrane Protocol - topological perception",
    )
    membrane_sub = membrane_parser.add_subparsers(
        dest="operation", help="Membrane operation"
    )

    # membrane observe
    membrane_observe = membrane_sub.add_parser(
        "observe",
        help="Full topological observation",
    )
    membrane_observe.add_argument(
        "path",
        nargs="?",
        help="Path to observe (default: current directory)",
    )

    # membrane sense
    membrane_sub.add_parser(
        "sense",
        help="Quick shape intuition (<100ms)",
    )

    # membrane trace
    membrane_trace = membrane_sub.add_parser(
        "trace",
        help="Follow topic momentum",
    )
    membrane_trace.add_argument(
        "topic",
        help="Topic to trace",
    )

    # membrane touch
    membrane_touch = membrane_sub.add_parser(
        "touch",
        help="Acknowledge a shape",
    )
    membrane_touch.add_argument(
        "shape_id",
        help="Shape ID to touch (e.g., SHAPE-12)",
    )

    # membrane name
    membrane_name = membrane_sub.add_parser(
        "name",
        help="Give voice to a void",
    )
    membrane_name.add_argument(
        "description",
        help="Description of what is not being said",
    )

    # membrane hold
    membrane_hold = membrane_sub.add_parser(
        "hold",
        help="Preserve productive tension",
    )
    membrane_hold.add_argument(
        "shape_id",
        help="Shape ID to hold",
    )
    membrane_hold.add_argument(
        "--reason",
        default="Productive tension",
        help="Reason for holding",
    )

    # membrane release
    membrane_release = membrane_sub.add_parser(
        "release",
        help="Allow natural resolution",
    )
    membrane_release.add_argument(
        "shape_id",
        help="Shape ID to release",
    )

    # ---------------------------------------------------------------------
    # Top-level Aliases (Convenience)
    # ---------------------------------------------------------------------

    # observe (alias for membrane observe)
    observe_parser = subparsers.add_parser(
        "observe",
        help="Alias for 'membrane observe'",
    )
    observe_parser.add_argument(
        "path",
        nargs="?",
        help="Path to observe",
    )

    # sense (alias for membrane sense)
    subparsers.add_parser(
        "sense",
        help="Alias for 'membrane sense'",
    )

    # trace (alias for membrane trace)
    trace_parser = subparsers.add_parser(
        "trace",
        help="Alias for 'membrane trace'",
    )
    trace_parser.add_argument(
        "topic",
        help="Topic to trace",
    )

    # touch (alias for membrane touch)
    touch_parser = subparsers.add_parser(
        "touch",
        help="Alias for 'membrane touch'",
    )
    touch_parser.add_argument(
        "shape_id",
        help="Shape ID to touch",
    )

    # name (alias for membrane name)
    name_parser = subparsers.add_parser(
        "name",
        help="Alias for 'membrane name'",
    )
    name_parser.add_argument(
        "description",
        help="Description of what is not being said",
    )

    # ---------------------------------------------------------------------
    # I-gent Integration
    # ---------------------------------------------------------------------

    # garden
    garden_parser = subparsers.add_parser(
        "garden",
        help="I-gent garden view",
    )
    garden_parser.add_argument(
        "--load",
        help="Load saved session",
    )
    garden_parser.add_argument(
        "--export",
        help="Export to markdown",
    )

    # whisper (for prompt integration)
    whisper_parser = subparsers.add_parser(
        "whisper",
        help="Get status whisper for prompt",
    )
    whisper_parser.add_argument(
        "--whisper-format",
        choices=["prompt", "raw"],
        default="prompt",
        dest="whisper_format",
        help="Whisper format",
    )

    return parser


# =============================================================================
# Command Handlers
# =============================================================================


async def handle_mirror(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle mirror commands."""
    cli = MirrorCLI()

    if args.explain:
        print(_get_mirror_explanation(args.operation))
        return 0

    if args.operation == "observe":
        path = Path(args.path).expanduser().resolve()
        result = await cli.observe(path, ctx)

        if result.success and result.output:
            if ctx.output_format == OutputFormat.RICH:
                print(format_mirror_report_rich(result.output))
            else:
                print(format_output(result, ctx, "mirror.observe"))
        else:
            print(format_output(result, ctx, "mirror.observe"))

        return result.exit_code

    elif args.operation == "reflect":
        result = await cli.reflect(args.tension, ctx)
        print(format_output(result, ctx, "mirror.reflect"))
        return result.exit_code

    elif args.operation == "status":
        result = await cli.status(ctx)
        print(format_output(result, ctx, "mirror.status"))
        return result.exit_code

    elif args.operation == "hold":
        result = await cli.hold(args.tension_index, args.reason, ctx)
        print(format_output(result, ctx, "mirror.hold"))
        return result.exit_code

    else:
        print(f"Unknown mirror operation: {args.operation}")
        return 1


async def handle_membrane(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle membrane commands."""
    cli = MembraneCLI()

    if args.explain:
        print(_get_membrane_explanation(args.operation))
        return 0

    if args.operation == "observe":
        path = Path(args.path).expanduser().resolve() if args.path else None
        result = await cli.observe(path, ctx)

        if result.success and result.output:
            if ctx.output_format == OutputFormat.RICH:
                print(format_membrane_observe_rich(result.output))
            else:
                print(format_output(result, ctx, "membrane.observe"))
        else:
            print(format_output(result, ctx, "membrane.observe"))

        return result.exit_code

    elif args.operation == "sense":
        result = await cli.sense(ctx)
        print(format_output(result, ctx, "membrane.sense"))
        return result.exit_code

    elif args.operation == "trace":
        result = await cli.trace(args.topic, ctx)
        print(format_output(result, ctx, "membrane.trace"))
        return result.exit_code

    elif args.operation == "touch":
        result = await cli.touch(args.shape_id, ctx)
        print(format_output(result, ctx, "membrane.touch"))
        return result.exit_code

    elif args.operation == "name":
        result = await cli.name(args.description, ctx)
        print(format_output(result, ctx, "membrane.name"))
        return result.exit_code

    elif args.operation == "hold":
        result = await cli.hold(args.shape_id, args.reason, ctx)
        print(format_output(result, ctx, "membrane.hold"))
        return result.exit_code

    elif args.operation == "release":
        result = await cli.release(args.shape_id, ctx)
        print(format_output(result, ctx, "membrane.release"))
        return result.exit_code

    else:
        print(f"Unknown membrane operation: {args.operation}")
        return 1


async def handle_garden(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle garden command."""
    await run_garden_tui()
    return 0


def handle_whisper(args: argparse.Namespace) -> int:
    """Handle whisper command for prompt integration."""
    whisper_fmt = getattr(args, "whisper_format", "prompt")
    if whisper_fmt == "prompt":
        print(get_whisper_for_prompt())
    else:
        whisper = StatusWhisper()
        print(whisper.render())
    return 0


# =============================================================================
# Explanations (--explain flag)
# =============================================================================


def _get_mirror_explanation(operation: str | None) -> str:
    """Get philosophical explanation for mirror operation."""
    if operation == "observe":
        return """
MIRROR OBSERVE: The Witness Without Judgment

The Mirror Protocol's first phase is pure observation. We extract
what is stated (Thesis) and observe what is done (Antithesis),
without collapsing into judgment.

This command implements W-gent observation and P-gent extraction,
producing a tension report that surfaces divergence between
stated principles and observed patterns.

The key insight: An organization cannot change what it cannot see.
The Mirror makes the invisible visible—not by surveillance, but
by reflection.

Category Theory:
  observe : Vault → (DeonticGraph × OnticGraph)
  This is a product functor, extracting both stated and actual.

See also:
  kgents mirror reflect  # Phase 2: Generate synthesis options
  kgents mirror hold     # Preserve productive tension
"""
    return "Use --explain with a specific operation for philosophical context."


def _get_membrane_explanation(operation: str | None) -> str:
    """Get philosophical explanation for membrane operation."""
    if operation == "observe":
        return """
MEMBRANE OBSERVE: Topological Perception

The Membrane perceives shape—not logic (true/false) but topology
(curvature, void, flow, dampening).

This command performs full topological analysis:
- Curvature: Where meaning bends under tension
- Void (Ma): The pregnant emptiness, what is not said
- Flow: How meaning moves through time (semantic momentum)
- Dampening: Where emotional expression compresses

The Membrane is not a boundary. It is a zone of becoming—
the liminal space where intention takes shape.

See also:
  kgents membrane sense   # Quick intuition (<100ms)
  kgents membrane trace   # Follow topic momentum
  kgents membrane name    # Give voice to a void
"""
    elif operation == "sense":
        return """
MEMBRANE SENSE: Quick Shape Intuition

Like peripheral vision, 'sense' perceives dominant shapes
without full analysis. Target: <100ms.

Use when you want a quick read before committing to
full observation.
"""
    elif operation == "name":
        return """
MEMBRANE NAME: Giving Voice to the Void

This is the most powerful gesture: naming the unsaid.

In Japanese aesthetics, Ma (間) is the pregnant emptiness.
The void is not absence—it is active negative space that
shapes what surrounds it.

By naming what is not being said, you begin integration.
The void persists, but it now has a name.
"""
    return "Use --explain with a specific operation for philosophical context."


# =============================================================================
# Main Entry Point
# =============================================================================


async def async_main(argv: Sequence[str] | None = None) -> int:
    """Async main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    # Build context
    ctx = CLIContext(
        output_format=OutputFormat(args.format)
        if hasattr(args, "format")
        else OutputFormat.RICH,
        persona=PersonaMode(args.persona)
        if hasattr(args, "persona")
        else PersonaMode.MINIMAL,
        budget=BudgetStatus.from_level(BudgetLevel(args.budget))
        if hasattr(args, "budget")
        else BudgetStatus.from_level(BudgetLevel.MEDIUM),
    )

    # Route to handler
    if args.command == "mirror":
        return await handle_mirror(args, ctx)

    elif args.command == "membrane":
        return await handle_membrane(args, ctx)

    elif args.command == "observe":
        # Alias for membrane observe
        args.operation = "observe"
        return await handle_membrane(args, ctx)

    elif args.command == "sense":
        # Alias for membrane sense
        args.operation = "sense"
        return await handle_membrane(args, ctx)

    elif args.command == "trace":
        # Alias for membrane trace
        args.operation = "trace"
        return await handle_membrane(args, ctx)

    elif args.command == "touch":
        # Alias for membrane touch
        args.operation = "touch"
        return await handle_membrane(args, ctx)

    elif args.command == "name":
        # Alias for membrane name
        args.operation = "name"
        return await handle_membrane(args, ctx)

    elif args.command == "garden":
        return await handle_garden(args, ctx)

    elif args.command == "whisper":
        return handle_whisper(args)

    else:
        print(f"Unknown command: {args.command}")
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Synchronous main entry point."""
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    sys.exit(main())
