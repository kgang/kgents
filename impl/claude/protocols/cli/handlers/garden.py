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


def _print_help() -> None:
    """Print help for garden command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  (none)            Show garden status (default)")
    print("  season            Show current season info")
    print("  health            Show health metrics")
    print("  init              Initialize garden with default plots")
    print("  transition <to>   Transition to new season (DORMANT|SPROUTING|BLOOMING|HARVEST|COMPOSTING)")
    print()
    print("OPTIONS:")
    print("  --json            Output as JSON")
    print("  --width <n>       ASCII width (default: 72)")
    print("  --help, -h        Show this help")


def cmd_garden(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the garden command.

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

    # Run async handler
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
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots
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
    from protocols.gardener_logos import create_garden, GardenSeason

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
            f"",
            f"  {season.emoji} SEASON: {season.name}",
            f"",
            f"  {_season_description(season)}",
            f"",
            f"  Plasticity:        {season.plasticity:.0%} (how much change accepted)",
            f"  Entropy Multiplier: {season.entropy_multiplier:.1f}x (operation cost)",
            f"  Since:             {garden.season_since.strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"  Available seasons:",
            f"    DORMANT    - Resting, low cost, stable",
            f"    SPROUTING  - New ideas, high plasticity",
            f"    BLOOMING   - Ideas crystallizing, visible",
            f"    HARVEST    - Gathering, reflection",
            f"    COMPOSTING - Breaking down old patterns",
            f"",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_health(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle health subcommand - show health metrics."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots

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
        entropy_pct = entropy_remaining / metrics.entropy_budget if metrics.entropy_budget > 0 else 0
        entropy_bar = _progress_bar(entropy_pct, 20)

        lines = [
            f"",
            f"  GARDEN HEALTH",
            f"",
            f"  Overall:  {health_bar} {metrics.health_score:.0%}",
            f"  Entropy:  {entropy_bar} {entropy_pct:.0%} remaining",
            f"",
            f"  DETAILS:",
            f"    Active Plots:    {metrics.active_plots}",
            f"    Recent Gestures: {metrics.recent_gestures}",
            f"    Session Cycles:  {metrics.session_cycles}",
            f"    Total Prompts:   {metrics.total_prompts}",
            f"    Entropy Budget:  {metrics.entropy_budget:.2f}",
            f"    Entropy Spent:   {metrics.entropy_spent:.2f}",
            f"",
        ]
        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_init(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle init subcommand - initialize garden with default plots."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots

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
            f"",
            f"  {garden.season.emoji} GARDEN INITIALIZED",
            f"",
            f"  Name: {garden.name}",
            f"  ID:   {garden.garden_id[:8]}...",
            f"  Season: {garden.season.name}",
            f"",
            f"  PLOTS ({len(garden.plots)}):",
        ]
        for name, plot in garden.plots.items():
            active_marker = " <active>" if name == garden.active_plot else ""
            lines.append(f"    - {plot.display_name} ({plot.path}){active_marker}")
        lines.append(f"")
        lines.append(f"  Run 'kg plot <name>' to view a specific plot.")
        lines.append(f"  Run 'kg tend observe concept.gardener' to begin tending.")
        lines.append(f"")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_transition(
    args: list[str],
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle transition subcommand - transition to new season."""
    from protocols.gardener_logos import create_garden, GardenSeason

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
            f"",
            f"  SEASON TRANSITION",
            f"",
            f"  {old_season.emoji} {old_season.name} -> {new_season.emoji} {new_season.name}",
            f"",
            f"  Reason: {reason}",
            f"  Plasticity: {old_season.plasticity:.0%} -> {new_season.plasticity:.0%}",
            f"",
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
