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
import json
import sys
from datetime import timedelta
from pathlib import Path
from typing import Sequence

from .cli_types import (
    BudgetLevel,
    BudgetStatus,
    CLIContext,
    OutputFormat,
    PersonaMode,
    format_output,
    with_metrics,
)
from .mirror_cli import MirrorCLI, format_mirror_report_rich
from .membrane_cli import MembraneCLI, format_membrane_observe_rich
from .igent_synergy import (
    StatusWhisper,
    get_whisper_for_prompt,
    run_garden_tui,
)
from .companions import (
    CompanionsCLI,
)
from .scientific import (
    ScientificCLI,
)

# Kairos imports
from protocols.mirror.kairos.controller import KairosController
from protocols.mirror.kairos.budget import BudgetLevel as KairosBudgetLevel
from protocols.mirror.kairos.watch import watch_loop
from protocols.mirror.obsidian.tension import detect_tensions


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
        "--no-metrics",
        action="store_true",
        dest="no_metrics",
        help="Hide token/cost metrics from output",
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

    # mirror watch (Kairos Phase 3)
    mirror_watch = mirror_sub.add_parser(
        "watch",
        help="Autonomous observation mode (surfaces tensions at opportune moments)",
    )
    mirror_watch.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to observe (default: current directory)",
    )
    mirror_watch.add_argument(
        "--interval",
        type=int,
        default=10,
        help="Observation interval in minutes (default: 10)",
    )
    mirror_watch.add_argument(
        "--verbose",
        action="store_true",
        help="Show debug logs",
    )

    # mirror timing (Kairos context)
    mirror_timing = mirror_sub.add_parser(
        "timing",
        help="Show current timing context (attention, budget, cognitive load)",
    )
    mirror_timing.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)",
    )
    mirror_timing.add_argument(
        "--show-state",
        action="store_true",
        dest="show_state",
        help="Show full controller state",
    )

    # mirror surface (force surface next)
    mirror_surface = mirror_sub.add_parser(
        "surface",
        help="Force surface next deferred tension (override Kairos)",
    )
    mirror_surface.add_argument(
        "--next",
        action="store_true",
        help="Surface next deferred tension",
    )

    # mirror history (intervention log)
    mirror_history = mirror_sub.add_parser(
        "history",
        help="Show intervention history",
    )
    mirror_history.add_argument(
        "--window",
        default="7d",
        help="Time window (e.g., '7d', '24h', '30m')",
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

    # ---------------------------------------------------------------------
    # Daily Companions (Tier 1 - 0 token)
    # ---------------------------------------------------------------------

    # pulse
    pulse_parser = subparsers.add_parser(
        "pulse",
        help="1-line project health pulse (0 tokens)",
    )
    pulse_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to check (default: current directory)",
    )

    # ground
    ground_parser = subparsers.add_parser(
        "ground",
        help="Parse statement and reflect structure (0 tokens)",
    )
    ground_parser.add_argument(
        "statement",
        help="Statement to ground/parse",
    )

    # breathe
    subparsers.add_parser(
        "breathe",
        help="Contemplative pause with gentle prompt (0 tokens)",
    )

    # entropy
    entropy_parser = subparsers.add_parser(
        "entropy",
        help="Show session entropy/chaos budget (0 tokens)",
    )
    entropy_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)",
    )

    # ---------------------------------------------------------------------
    # Scientific Core (Tier 2 - H-gent dialectics)
    # ---------------------------------------------------------------------

    # falsify
    falsify_parser = subparsers.add_parser(
        "falsify",
        help="Find counterexamples to a hypothesis (0 tokens)",
    )
    falsify_parser.add_argument(
        "hypothesis",
        help="The hypothesis to falsify",
    )
    falsify_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to search for counterexamples (default: current directory)",
    )
    falsify_parser.add_argument(
        "--depth",
        choices=["shallow", "medium", "deep"],
        default="medium",
        help="Search depth (default: medium)",
    )

    # conjecture
    conjecture_parser = subparsers.add_parser(
        "conjecture",
        help="Generate hypotheses from observed patterns (0 tokens)",
    )
    conjecture_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)",
    )
    conjecture_parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Maximum conjectures to generate (default: 5)",
    )

    # rival
    rival_parser = subparsers.add_parser(
        "rival",
        help="Steel-man opposing views for a position (0 tokens)",
    )
    rival_parser.add_argument(
        "position",
        help="The position to find rivals for",
    )

    # sublate
    sublate_parser = subparsers.add_parser(
        "sublate",
        help="Synthesize contradictions dialectically (0 tokens)",
    )
    sublate_parser.add_argument(
        "thesis",
        help="The thesis to synthesize",
    )
    sublate_parser.add_argument(
        "--antithesis",
        help="The antithesis (optional, will be inferred if not provided)",
    )
    sublate_parser.add_argument(
        "--force",
        action="store_true",
        help="Force synthesis even if productive tension",
    )

    # shadow
    shadow_parser = subparsers.add_parser(
        "shadow",
        help="Surface suppressed concerns for a self-image (0 tokens)",
    )
    shadow_parser.add_argument(
        "self_image",
        help="The self-image to analyze (e.g., 'I am helpful and accurate')",
    )

    # ---------------------------------------------------------------------
    # Debug Commands
    # ---------------------------------------------------------------------

    # debug
    debug_parser = subparsers.add_parser(
        "debug",
        help="Debug utilities",
    )
    debug_sub = debug_parser.add_subparsers(dest="debug_command", help="Debug command")

    # debug ctx
    debug_sub.add_parser(
        "ctx",
        help="Dump current CLI context",
    )

    # ---------------------------------------------------------------------
    # Bootstrap Commands (Phase 2)
    # ---------------------------------------------------------------------

    # laws
    laws_parser = subparsers.add_parser(
        "laws",
        help="Display and verify the 7 category laws",
    )
    laws_parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["verify", "witness"],
        help="Subcommand: verify or witness",
    )
    laws_parser.add_argument(
        "operation",
        nargs="?",
        help="Operation to witness (for 'witness' subcommand)",
    )
    laws_parser.add_argument(
        "--agent",
        help="Agent ID to verify (for 'verify' subcommand)",
    )

    # principles
    principles_parser = subparsers.add_parser(
        "principles",
        help="Display and check against the 7 design principles",
    )
    principles_parser.add_argument(
        "subcommand",
        nargs="?",
        choices=["check"],
        help="Subcommand: check",
    )
    principles_parser.add_argument(
        "input",
        nargs="?",
        help="Input to check (text or file path)",
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

    elif args.operation == "watch":
        return await handle_mirror_watch(args, ctx)

    elif args.operation == "timing":
        return await handle_mirror_timing(args, ctx)

    elif args.operation == "surface":
        return await handle_mirror_surface(args, ctx)

    elif args.operation == "history":
        return await handle_mirror_history(args, ctx)

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


async def handle_pulse(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle pulse command."""
    cli = CompanionsCLI()
    path = Path(args.path).expanduser().resolve()
    result = await cli.pulse(path, ctx)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "pulse"))

    return result.exit_code


async def handle_ground(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle ground command."""
    cli = CompanionsCLI()
    result = await cli.ground(args.statement, ctx)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "ground"))

    return result.exit_code


async def handle_breathe(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle breathe command."""
    cli = CompanionsCLI()
    result = await cli.breathe(ctx)

    if result.success and result.output:
        print(with_metrics(result.output, result, ctx))
    else:
        print(format_output(result, ctx, "breathe"))

    return result.exit_code


async def handle_entropy(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle entropy command."""
    cli = CompanionsCLI()
    path = Path(args.path).expanduser().resolve()
    result = await cli.entropy(path, ctx)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "entropy"))

    return result.exit_code


# =============================================================================
# Scientific Core Handlers (Phase 2)
# =============================================================================


async def handle_falsify(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle falsify command."""
    cli = ScientificCLI()
    path = Path(args.path).expanduser().resolve()
    result = await cli.falsify(args.hypothesis, path, ctx, depth=args.depth)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "falsify"))

    return result.exit_code


async def handle_conjecture(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle conjecture command."""
    cli = ScientificCLI()
    path = Path(args.path).expanduser().resolve()
    result = await cli.conjecture(path, ctx, limit=args.limit)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "conjecture"))

    return result.exit_code


async def handle_rival(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle rival command."""
    cli = ScientificCLI()
    result = await cli.rival(args.position, ctx)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "rival"))

    return result.exit_code


async def handle_sublate(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle sublate command."""
    cli = ScientificCLI()
    result = await cli.sublate(
        args.thesis,
        getattr(args, "antithesis", None),
        ctx,
        force=getattr(args, "force", False),
    )

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "sublate"))

    return result.exit_code


async def handle_shadow(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle shadow command."""
    cli = ScientificCLI()
    result = await cli.shadow(args.self_image, ctx)

    if result.success and result.output:
        print(with_metrics(result.output.render(), result, ctx))
    else:
        print(format_output(result, ctx, "shadow"))

    return result.exit_code


# =============================================================================
# Debug Handlers
# =============================================================================


def handle_debug(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle debug commands."""
    if args.debug_command == "ctx":
        return handle_debug_ctx(args, ctx)
    else:
        print(f"Unknown debug command: {args.debug_command}")
        print("Available: ctx")
        return 1


def handle_debug_ctx(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Dump current CLI context."""
    if ctx.output_format == OutputFormat.JSON:
        print(
            json.dumps(
                {
                    "output_format": ctx.output_format.value,
                    "persona": ctx.persona.value,
                    "show_metrics": ctx.show_metrics,
                    "budget": {
                        "level": ctx.budget.level.value,
                        "tokens_used": ctx.budget.tokens_used,
                        "llm_calls_used": ctx.budget.llm_calls_used,
                    },
                },
                indent=2,
            )
        )
    else:
        print("=== CLI Context ===\n")
        print(f"Output Format: {ctx.output_format.value}")
        print(f"Persona: {ctx.persona.value}")
        print(f"Show Metrics: {ctx.show_metrics}")
        print()
        print("Budget:")
        print(f"  Level: {ctx.budget.level.value}")
        print(f"  Tokens Used: {ctx.budget.tokens_used}")
        print(f"  LLM Calls Used: {ctx.budget.llm_calls_used}")
        print()
        print("(Note: tokens/calls reset each CLI invocation)")

    return 0


# =============================================================================
# Bootstrap Handlers (CLI Phase 2)
# =============================================================================


async def handle_laws(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle laws commands."""
    from .bootstrap.laws import (
        verify_laws,
        witness_composition,
        format_laws_rich,
        format_laws_json,
        format_verification_rich,
        format_witness_rich,
        Verdict,
    )
    import json as json_module

    use_json = ctx.output_format == OutputFormat.JSON

    # No subcommand - display laws
    if not args.subcommand:
        if use_json:
            print(format_laws_json())
        else:
            print(format_laws_rich())
        return 0

    # Verify subcommand
    if args.subcommand == "verify":
        agent_id = args.agent if hasattr(args, "agent") else None
        report = await verify_laws(agent_id)
        if use_json:
            print(
                json_module.dumps(
                    {
                        "agent_id": report.agent_id,
                        "verified_at": report.verified_at.isoformat(),
                        "overall_verdict": report.overall_verdict.value,
                        "passed": report.passed,
                        "failed": report.failed,
                        "skipped": report.skipped,
                        "results": [
                            {
                                "law": r.law.value,
                                "verdict": r.verdict.value,
                                "evidence": r.evidence,
                            }
                            for r in report.results
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(format_verification_rich(report))
        return 0 if report.overall_verdict != Verdict.FAIL else 1

    # Witness subcommand
    if args.subcommand == "witness":
        if not args.operation:
            print("Error: witness requires an operation argument")
            print("Usage: kgents laws witness <operation>")
            print("Example: kgents laws witness 'ParseCode >> ValidateAST'")
            return 1

        report = await witness_composition(args.operation)
        if use_json:
            print(
                json_module.dumps(
                    {
                        "operation": report.operation,
                        "left": report.left,
                        "right": report.right,
                        "result_type": report.result_type,
                        "valid": report.valid,
                        "laws_checked": [law.value for law in report.laws_checked],
                        "witnessed_at": report.witnessed_at.isoformat(),
                        "notes": report.notes,
                    },
                    indent=2,
                )
            )
        else:
            print(format_witness_rich(report))
        return 0 if report.valid else 1

    return 0


async def handle_principles(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle principles commands."""
    from .bootstrap.principles import (
        evaluate_against_principles,
        evaluate_file,
        format_principles_rich,
        format_principles_json,
        format_evaluation_rich,
        Verdict,
    )
    from pathlib import Path
    import json as json_module

    use_json = ctx.output_format == OutputFormat.JSON

    # No subcommand - display principles
    if not args.subcommand:
        if use_json:
            print(format_principles_json())
        else:
            print(format_principles_rich())
        return 0

    # Check subcommand
    if args.subcommand == "check":
        if not args.input:
            print("Error: check requires input text or file path")
            print("Usage: kgents principles check <input>")
            print(
                'Example: kgents principles check "A monolithic agent that does everything"'
            )
            return 1

        # Check if input is a file path
        input_path = Path(args.input)
        if input_path.exists():
            report = await evaluate_file(input_path)
        else:
            # Treat as text input
            report = await evaluate_against_principles(args.input)

        if use_json:
            print(
                json_module.dumps(
                    {
                        "input": report.input_description,
                        "evaluated_at": report.evaluated_at.isoformat(),
                        "overall_verdict": report.overall_verdict.value,
                        "accepted": report.accepted,
                        "rejected": report.rejected,
                        "unclear": report.unclear,
                        "summary": report.summary,
                        "evaluations": [
                            {
                                "principle": e.principle.value,
                                "verdict": e.verdict.value,
                                "reasoning": e.reasoning,
                                "confidence": e.confidence,
                                "suggestions": e.suggestions,
                            }
                            for e in report.evaluations
                        ],
                    },
                    indent=2,
                )
            )
        else:
            print(format_evaluation_rich(report))

        # Return code based on verdict
        if report.overall_verdict == Verdict.ACCEPT:
            return 0
        elif report.overall_verdict == Verdict.REJECT:
            return 1
        else:
            return 0  # Unclear/Revise are not failures

    return 0


# =============================================================================
# Kairos Handlers (Mirror Phase 3)
# =============================================================================


def _parse_time_window(window_str: str) -> timedelta:
    """Parse time window string like '7d', '24h', '30m' into timedelta."""
    unit = window_str[-1]
    value = int(window_str[:-1])

    if unit == "d":
        return timedelta(days=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "m":
        return timedelta(minutes=value)
    elif unit == "s":
        return timedelta(seconds=value)
    else:
        raise ValueError(f"Unknown time unit: {unit}. Use d/h/m/s")


async def handle_mirror_watch(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle mirror watch command (autonomous Kairos mode)."""
    path = Path(args.path).expanduser().resolve()
    interval = timedelta(minutes=args.interval)
    verbose = args.verbose

    # Map CLI budget to Kairos budget
    budget_map = {
        "minimal": KairosBudgetLevel.LOW,
        "low": KairosBudgetLevel.LOW,
        "medium": KairosBudgetLevel.MEDIUM,
        "high": KairosBudgetLevel.HIGH,
        "unlimited": KairosBudgetLevel.UNLIMITED,
    }
    kairos_budget = budget_map.get(ctx.budget.level.value, KairosBudgetLevel.MEDIUM)

    # Tension detector wrapper
    async def tension_detector_wrapper(workspace_path: Path):
        """Wrapper to call detect_tensions."""
        return await detect_tensions(workspace_path)

    # Callbacks for surfacing/deferring
    async def on_surface(tension, evaluation):
        """Called when tension surfaced."""
        if ctx.output_format == OutputFormat.RICH:
            print(f"\n🔔 [Kairos] Tension surfaced: {tension.id}")
            print(f"   Thesis: {tension.thesis[:80]}...")
            print(f"   Benefit: {evaluation.benefit:.2f}")
        else:
            print(
                json.dumps(
                    {
                        "event": "surface",
                        "tension_id": tension.id,
                        "benefit": evaluation.benefit,
                    }
                )
            )

    async def on_defer(tension, reason):
        """Called when tension deferred."""
        if verbose:
            print(f"   Deferred: {tension.id} ({reason})")

    print(f"[Kairos] Starting watch mode on {path}")
    print(f"[Kairos] Budget: {kairos_budget.label}")
    print(f"[Kairos] Interval: {interval}")
    print("[Kairos] Press Ctrl+C to stop\n")

    try:
        await watch_loop(
            workspace_path=path,
            tension_detector=tension_detector_wrapper,
            budget_level=kairos_budget,
            interval=interval,
            on_surface=on_surface,
            on_defer=on_defer,
            verbose=verbose,
        )
    except KeyboardInterrupt:
        print("\n[Kairos] Watch mode stopped")
        return 0

    return 0


async def handle_mirror_timing(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle mirror timing command (show Kairos context)."""
    path = Path(args.path).expanduser().resolve()

    # Create controller to get context
    controller = KairosController(workspace_path=path)

    if args.show_state:
        # Full controller state
        status = controller.get_status()
        if ctx.output_format == OutputFormat.JSON:
            print(json.dumps(status, indent=2))
        else:
            print("=== Kairos Controller State ===\n")
            print(f"State: {status['state']}")
            print(f"Timestamp: {status['timestamp']}\n")

            print("Context:")
            for key, val in status["context"].items():
                print(f"  {key}: {val}")

            print("\nBudget:")
            for key, val in status["budget"].items():
                print(f"  {key}: {val}")

            print(f"\nDeferred Queue: {status['deferred_queue']['count']} tensions")
            for t in status["deferred_queue"]["tensions"]:
                print(f"  - {t['id']}: {t['reason']} (retry={t['retry_count']})")

            print("\nHistory:")
            print(f"  Total interventions: {status['history']['total_interventions']}")
            print(f"  Recent (7d): {status['history']['recent_7d']}")
    else:
        # Just show current context
        context = controller.get_current_context()

        if ctx.output_format == OutputFormat.JSON:
            print(
                json.dumps(
                    {
                        "attention_state": context.attention_state.name,
                        "attention_budget": context.attention_budget,
                        "cognitive_load": context.cognitive_load,
                        "last_activity_age": context.last_activity_age,
                        "active_files": context.active_files_count,
                    },
                    indent=2,
                )
            )
        else:
            print("=== Current Kairos Context ===\n")
            print(f"Attention State: {context.attention_state.name}")
            print(f"Attention Budget: {context.attention_budget:.2f}")
            print(f"Cognitive Load: {context.cognitive_load:.2f}")
            print(f"Last Activity: {context.last_activity_age:.1f}m ago")
            print(f"Active Files: {context.active_files_count}")

    return 0


async def handle_mirror_surface(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle mirror surface command (force surface next)."""
    if not args.next:
        print("Error: --next flag required")
        return 1

    # Get current directory
    path = Path.cwd()
    controller = KairosController(workspace_path=path)

    # Force surface next
    record = controller.force_surface_next()

    if record:
        tension = record.tension
        if ctx.output_format == OutputFormat.RICH:
            print("=== Force-Surfaced Tension ===\n")
            print(f"ID: {tension.id}")
            print(f"Thesis: {tension.thesis}")
            print(f"Antithesis: {tension.antithesis}")
            print("\nEvaluation:")
            print(f"  Benefit: {record.evaluation.benefit}")
            print(f"  Severity: {record.evaluation.severity}")
        else:
            print(
                json.dumps(
                    {
                        "tension_id": tension.id,
                        "thesis": tension.thesis,
                        "antithesis": tension.antithesis,
                        "benefit": record.evaluation.benefit,
                    },
                    indent=2,
                )
            )
        return 0
    else:
        print("No deferred tensions to surface")
        return 1


async def handle_mirror_history(args: argparse.Namespace, ctx: CLIContext) -> int:
    """Handle mirror history command (show intervention log)."""
    window = _parse_time_window(args.window)

    # Get current directory
    path = Path.cwd()
    controller = KairosController(workspace_path=path)

    # Get history
    history = controller.get_intervention_history(window)

    if ctx.output_format == OutputFormat.JSON:
        print(
            json.dumps(
                [
                    {
                        "timestamp": record.timestamp.isoformat(),
                        "tension_id": record.tension.id,
                        "benefit": record.evaluation.benefit,
                        "user_response": record.user_response,
                        "duration_seconds": record.duration_seconds,
                    }
                    for record in history
                ],
                indent=2,
            )
        )
    else:
        print(f"=== Intervention History (last {args.window}) ===\n")
        if not history:
            print("No interventions recorded")
        else:
            for record in history:
                print(f"[{record.timestamp.isoformat()}] {record.tension.id}")
                print(f"  Benefit: {record.evaluation.benefit:.2f}")
                if record.user_response:
                    print(f"  Response: {record.user_response}")
                if record.duration_seconds:
                    print(f"  Duration: {record.duration_seconds:.1f}s")
                print()

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
        show_metrics=not getattr(args, "no_metrics", False),
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

    # Daily Companions (Tier 1)
    elif args.command == "pulse":
        return await handle_pulse(args, ctx)

    elif args.command == "ground":
        return await handle_ground(args, ctx)

    elif args.command == "breathe":
        return await handle_breathe(args, ctx)

    elif args.command == "entropy":
        return await handle_entropy(args, ctx)

    # Scientific Core (Tier 2 - H-gent dialectics)
    elif args.command == "falsify":
        return await handle_falsify(args, ctx)

    elif args.command == "conjecture":
        return await handle_conjecture(args, ctx)

    elif args.command == "rival":
        return await handle_rival(args, ctx)

    elif args.command == "sublate":
        return await handle_sublate(args, ctx)

    elif args.command == "shadow":
        return await handle_shadow(args, ctx)

    elif args.command == "debug":
        return handle_debug(args, ctx)

    elif args.command == "laws":
        return await handle_laws(args, ctx)

    elif args.command == "principles":
        return await handle_principles(args, ctx)

    else:
        print(f"Unknown command: {args.command}")
        return 1


def main(argv: Sequence[str] | None = None) -> int:
    """Synchronous main entry point."""
    return asyncio.run(async_main(argv))


if __name__ == "__main__":
    sys.exit(main())
