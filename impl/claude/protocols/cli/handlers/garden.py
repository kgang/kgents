"""
Garden Command Handler: View and manage the Gardener-Logos garden.

The garden is the unified state model for development sessions:
- Plots are focused regions (crown jewels, plans)
- Seasons affect how much change the garden accepts
- Gestures accumulate in momentum trace

Usage:
    kg garden              Show garden status (ASCII)
    kg garden --json       Show garden status (JSON)
    kg garden season       Show current season
    kg garden health       Show health metrics
    kg garden init         Initialize garden with crown jewel plots

Example:
    kg garden                        # Beautiful ASCII garden view
    kg garden season                 # Current season info
    kg garden health --json          # Health metrics as JSON
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext
    from protocols.gardener_logos import GardenSeason


def _print_help() -> None:
    """Print help for garden command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  (none)            Show garden status (default)")
    print("  season            Show current season info")
    print("  health            Show health metrics")
    print("  init              Initialize garden with default plots")
    print(
        "  transition <to>   Transition to new season (DORMANT|SPROUTING|BLOOMING|HARVEST|COMPOSTING)"
    )
    print()
    print("AUTO-INDUCER (Phase 8):")
    print("  suggest           Check for suggested season transition")
    print("  accept            Accept the current suggestion")
    print("  dismiss           Dismiss the current suggestion (4h cooldown)")
    print()
    print("OPTIONS:")
    print("  --json            Output as JSON")
    print("  --width <n>       ASCII width (default: 72)")
    print("  --help, -h        Show this help")


# =============================================================================
# AGENTESE Thin Routing (Wave 2.5)
# =============================================================================

# Subcommand -> AGENTESE path mapping
GARDEN_SUBCOMMAND_MAP: dict[str, str] = {
    "show": "self.garden.manifest",
    "season": "self.garden.season",
    "health": "self.garden.health",
    "init": "self.garden.init",
    "transition": "self.garden.transition",
    "suggest": "self.garden.suggest",
    "accept": "self.garden.accept",
    "dismiss": "self.garden.dismiss",
}


def cmd_garden(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the garden command.

    Wave 2.5: Routes to self.garden.* AGENTESE paths via thin routing.

    Args:
        args: Command-line arguments (after the command name)
        ctx: Optional InvocationContext for dual-channel output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("garden", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Parse width
    width = 72
    for i, arg in enumerate(args):
        if arg == "--width" and i + 1 < len(args):
            try:
                width = int(args[i + 1])
            except ValueError:
                pass

    # Get subcommand
    subcommand = None
    subcommand_args: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        if arg.isdigit():
            continue  # Skip width value
        if subcommand is None:
            subcommand = arg
        else:
            subcommand_args.append(arg)

    # Default subcommand
    if subcommand is None:
        subcommand = "show"

    # Try thin routing to AGENTESE path (Wave 2.5)
    if subcommand in GARDEN_SUBCOMMAND_MAP and json_mode:
        from protocols.cli.projection import project_command

        path = GARDEN_SUBCOMMAND_MAP[subcommand]
        kwargs: dict[str, Any] = {"json_output": True}

        # Handle transition target
        if subcommand == "transition" and subcommand_args:
            kwargs["target"] = subcommand_args[0]
            if len(subcommand_args) > 1:
                kwargs["reason"] = " ".join(subcommand_args[1:])

        try:
            return project_command(path=path, args=list(args), ctx=ctx, kwargs=kwargs)
        except Exception:
            pass  # Fall through to legacy handlers

    # Run async handler (legacy Rich output)
    return asyncio.run(
        _async_garden(
            subcommand=subcommand,
            subcommand_args=subcommand_args,
            json_mode=json_mode,
            width=width,
            ctx=ctx,
        )
    )


async def _async_garden(
    subcommand: str,
    subcommand_args: list[str],
    json_mode: bool,
    width: int,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of garden command."""
    try:
        match subcommand:
            case "show":
                return await _handle_show(json_mode, width, ctx)
            case "season":
                return await _handle_season(json_mode, ctx)
            case "health":
                return await _handle_health(json_mode, ctx)
            case "init":
                return await _handle_init(json_mode, ctx)
            case "transition":
                return await _handle_transition(subcommand_args, json_mode, ctx)
            case "suggest":
                return await _handle_suggest(json_mode, ctx)
            case "accept":
                return await _handle_accept(json_mode, ctx)
            case "dismiss":
                return await _handle_dismiss(json_mode, ctx)
            case _:
                _emit_output(
                    f"[GARDEN] Unknown subcommand: {subcommand}",
                    {"error": f"Unknown subcommand: {subcommand}"},
                    ctx,
                )
                return 1

    except ImportError as e:
        _emit_output(
            f"[GARDEN] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[GARDEN] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _handle_show(
    json_mode: bool,
    width: int,
    ctx: "InvocationContext | None",
) -> int:
    """Handle default show action - display garden."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.projections.ascii import project_garden_to_ascii
    from protocols.gardener_logos.projections.json import project_garden_to_json

    # Get or create garden (in future, load from persistence)
    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    if json_mode:
        import json

        result = project_garden_to_json(garden)
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        ascii_output = project_garden_to_ascii(garden, width=width)
        _emit_output(ascii_output, {"garden": garden.to_dict()}, ctx)

    return 0


async def _handle_season(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle season subcommand - show current season info."""
    from protocols.gardener_logos import GardenSeason, create_garden

    # Get or create garden
    garden = create_garden(name="kgents")

    season = garden.season
    result = {
        "name": season.name,
        "emoji": season.emoji,
        "plasticity": season.plasticity,
        "entropy_multiplier": season.entropy_multiplier,
        "since": garden.season_since.isoformat(),
        "description": _season_description(season),
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            "",
            f"  {season.emoji} SEASON: {season.name}",
            "",
            f"  {_season_description(season)}",
            "",
            f"  Plasticity:        {season.plasticity:.0%} (how much change accepted)",
            f"  Entropy Multiplier: {season.entropy_multiplier:.1f}x (operation cost)",
            f"  Since:             {garden.season_since.strftime('%Y-%m-%d %H:%M')}",
            "",
            "  Available seasons:",
            "    DORMANT    - Resting, low cost, stable",
            "    SPROUTING  - New ideas, high plasticity",
            "    BLOOMING   - Ideas crystallizing, visible",
            "    HARVEST    - Gathering, reflection",
            "    COMPOSTING - Breaking down old patterns",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_health(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle health subcommand - show health metrics."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden

    # Get or create garden
    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()
    garden.metrics.active_plots = len([p for p in garden.plots.values() if p.is_active])

    metrics = garden.metrics
    result = {
        "health_score": metrics.health_score,
        "total_prompts": metrics.total_prompts,
        "active_plots": metrics.active_plots,
        "recent_gestures": metrics.recent_gestures,
        "session_cycles": metrics.session_cycles,
        "entropy_spent": metrics.entropy_spent,
        "entropy_budget": metrics.entropy_budget,
        "entropy_remaining": metrics.entropy_budget - metrics.entropy_spent,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        health_bar = _progress_bar(metrics.health_score, 20)
        entropy_remaining = max(0, metrics.entropy_budget - metrics.entropy_spent)
        entropy_pct = (
            entropy_remaining / metrics.entropy_budget if metrics.entropy_budget > 0 else 0
        )
        entropy_bar = _progress_bar(entropy_pct, 20)

        lines = [
            "",
            "  GARDEN HEALTH",
            "",
            f"  Overall:  {health_bar} {metrics.health_score:.0%}",
            f"  Entropy:  {entropy_bar} {entropy_pct:.0%} remaining",
            "",
            "  DETAILS:",
            f"    Active Plots:    {metrics.active_plots}",
            f"    Recent Gestures: {metrics.recent_gestures}",
            f"    Session Cycles:  {metrics.session_cycles}",
            f"    Total Prompts:   {metrics.total_prompts}",
            f"    Entropy Budget:  {metrics.entropy_budget:.2f}",
            f"    Entropy Spent:   {metrics.entropy_spent:.2f}",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_init(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle init subcommand - initialize garden with default plots."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    result = {
        "status": "initialized",
        "garden_id": garden.garden_id,
        "name": garden.name,
        "season": garden.season.name,
        "plots": list(garden.plots.keys()),
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            "",
            f"  {garden.season.emoji} GARDEN INITIALIZED",
            "",
            f"  Name: {garden.name}",
            f"  ID:   {garden.garden_id[:8]}...",
            f"  Season: {garden.season.name}",
            "",
            f"  PLOTS ({len(garden.plots)}):",
        ]
        for name, plot in garden.plots.items():
            active_marker = " <active>" if name == garden.active_plot else ""
            lines.append(f"    - {plot.display_name} ({plot.path}){active_marker}")
        lines.append("")
        lines.append("  Run 'kg plot <name>' to view a specific plot.")
        lines.append("  Run 'kg tend observe concept.gardener' to begin tending.")
        lines.append("")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_transition(
    args: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle transition subcommand - transition to new season."""
    from protocols.gardener_logos import GardenSeason, create_garden

    if not args:
        _emit_output(
            "[GARDEN] transition requires a target season: DORMANT|SPROUTING|BLOOMING|HARVEST|COMPOSTING",
            {"error": "Missing target season"},
            ctx,
        )
        return 1

    target = args[0].upper()
    reason = " ".join(args[1:]) if len(args) > 1 else "Manual transition"

    try:
        new_season = GardenSeason[target]
    except KeyError:
        valid = "|".join(s.name for s in GardenSeason)
        _emit_output(
            f"[GARDEN] Invalid season: {target}. Valid: {valid}",
            {"error": f"Invalid season: {target}", "valid": valid},
            ctx,
        )
        return 1

    garden = create_garden(name="kgents")
    old_season = garden.season
    garden.transition_season(new_season, reason)

    result = {
        "status": "transitioned",
        "from": old_season.name,
        "to": new_season.name,
        "reason": reason,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            "",
            "  SEASON TRANSITION",
            "",
            f"  {old_season.emoji} {old_season.name} -> {new_season.emoji} {new_season.name}",
            "",
            f"  Reason: {reason}",
            f"  Plasticity: {old_season.plasticity:.0%} -> {new_season.plasticity:.0%}",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


# =============================================================================
# Auto-Inducer Handlers (Phase 8)
# =============================================================================


async def _handle_suggest(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle suggest subcommand - check for season transition suggestion."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.seasons import (
        TransitionSignals,
        suggest_season_transition,
    )

    # Get or create garden with plots for realistic signals
    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()
    garden.metrics.active_plots = len([p for p in garden.plots.values() if p.is_active])

    # Gather signals and evaluate
    signals = TransitionSignals.gather(garden)
    suggestion = suggest_season_transition(garden)

    if suggestion is None:
        result: dict[str, Any] = {
            "status": "no_suggestion",
            "current_season": garden.season.name,
            "signals": signals.to_dict(),
            "message": "Garden is content in its current season.",
        }

        if json_mode:
            import json

            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            lines = [
                "",
                f"  {garden.season.emoji} AUTO-INDUCER: No Suggestion",
                "",
                f"  Current Season: {garden.season.name}",
                "  The garden is content. No transition suggested.",
                "",
                "  CURRENT SIGNALS:",
                f"    Gesture frequency: {signals.gesture_frequency:.2f}/hour",
                f"    Gesture diversity: {signals.gesture_diversity} verbs",
                f"    Time in season:    {signals.time_in_season_hours:.1f} hours",
                f"    Entropy usage:     {signals.entropy_spent_ratio:.0%}",
                f"    Session active:    {'Yes' if signals.session_active else 'No'}",
                "",
            ]
            _emit_output("\n".join(lines), result, ctx)
        return 0

    # We have a suggestion
    result = {
        "status": "suggestion",
        "from_season": suggestion.from_season.name,
        "to_season": suggestion.to_season.name,
        "confidence": suggestion.confidence,
        "reason": suggestion.reason,
        "signals": suggestion.signals.to_dict(),
        "should_suggest": suggestion.should_suggest,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        confidence_bar = _progress_bar(suggestion.confidence, 10)
        lines = [
            "",
            f"  {suggestion.from_season.emoji} AUTO-INDUCER: Transition Suggested!",
            "",
            f"  {suggestion.from_season.emoji} {suggestion.from_season.name} -> {suggestion.to_season.emoji} {suggestion.to_season.name}",
            "",
            f"  Confidence: {confidence_bar} {suggestion.confidence:.0%}",
            f"  Reason:     {suggestion.reason}",
            "",
            "  SIGNALS:",
            f"    Gesture frequency: {signals.gesture_frequency:.2f}/hour",
            f"    Gesture diversity: {signals.gesture_diversity} verbs",
            f"    Time in season:    {signals.time_in_season_hours:.1f} hours",
            f"    Entropy usage:     {signals.entropy_spent_ratio:.0%}",
            "",
            "  ACTIONS:",
            "    kg garden accept   - Accept this transition",
            "    kg garden dismiss  - Dismiss (won't suggest for 4h)",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_accept(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle accept subcommand - accept current transition suggestion."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.seasons import (
        clear_dismissals,
        suggest_season_transition,
    )

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Check if there's a suggestion to accept
    suggestion = suggest_season_transition(garden)

    if suggestion is None or not suggestion.should_suggest:
        result = {
            "status": "no_suggestion",
            "message": "No pending transition suggestion to accept.",
        }
        if json_mode:
            import json

            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            _emit_output(
                "\n  No pending transition suggestion to accept.\n  Run 'kg garden suggest' to check status.\n",
                result,
                ctx,
            )
        return 1

    # Accept the transition
    old_season = suggestion.from_season
    new_season = suggestion.to_season
    garden.transition_season(new_season, f"Accepted auto-inducer suggestion: {suggestion.reason}")

    # Clear dismissals since we're accepting
    clear_dismissals(garden.garden_id)

    result = {
        "status": "accepted",
        "from_season": old_season.name,
        "to_season": new_season.name,
        "reason": suggestion.reason,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            "",
            f"  {new_season.emoji} TRANSITION ACCEPTED",
            "",
            f"  {old_season.emoji} {old_season.name} -> {new_season.emoji} {new_season.name}",
            "",
            f"  Plasticity: {old_season.plasticity:.0%} -> {new_season.plasticity:.0%}",
            f"  Reason: {suggestion.reason}",
            "",
            f"  The garden has transitioned to {new_season.name}.",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_dismiss(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle dismiss subcommand - dismiss current transition suggestion."""
    from protocols.gardener_logos import create_crown_jewel_plots, create_garden
    from protocols.gardener_logos.seasons import (
        dismiss_transition,
        suggest_season_transition,
    )

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Check if there's a suggestion to dismiss
    suggestion = suggest_season_transition(garden)

    if suggestion is None or not suggestion.should_suggest:
        result: dict[str, Any] = {
            "status": "no_suggestion",
            "message": "No pending transition suggestion to dismiss.",
        }
        if json_mode:
            import json

            _emit_output(json.dumps(result, indent=2), result, ctx)
        else:
            _emit_output(
                "\n  No pending transition suggestion to dismiss.\n  Run 'kg garden suggest' to check status.\n",
                result,
                ctx,
            )
        return 1

    # Dismiss the transition
    dismiss_transition(garden.garden_id, suggestion.from_season, suggestion.to_season)

    result = {
        "status": "dismissed",
        "from_season": suggestion.from_season.name,
        "to_season": suggestion.to_season.name,
        "cooldown_hours": 4,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            "",
            "  TRANSITION DISMISSED",
            "",
            f"  {suggestion.from_season.emoji} {suggestion.from_season.name} -> {suggestion.to_season.emoji} {suggestion.to_season.name}",
            "",
            "  This suggestion won't be shown again for 4 hours.",
            f"  The garden remains in {suggestion.from_season.name}.",
            "",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


def _season_description(season: "GardenSeason") -> str:
    """Get human-readable description for a season."""
    from protocols.gardener_logos import GardenSeason

    descriptions = {
        GardenSeason.DORMANT: "Garden is resting. Operations are cheap but prompts resist change.",
        GardenSeason.SPROUTING: "New ideas emerging. High plasticity, perfect for new additions.",
        GardenSeason.BLOOMING: "Ideas crystallizing. Lower plasticity, high visibility.",
        GardenSeason.HARVEST: "Time to gather and consolidate. Reflection-oriented.",
        GardenSeason.COMPOSTING: "Breaking down old patterns. High entropy tolerance.",
    }
    return descriptions.get(season, "Unknown season")


def _progress_bar(value: float, length: int = 10) -> str:
    """Create a progress bar string."""
    filled = int(value * length)
    return "[" + "=" * filled + "-" * (length - filled) + "]"


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


__all__ = ["cmd_garden"]
