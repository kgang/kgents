"""
Plot Command Handler: Manage garden plots (focused regions).

Plots are named focus regions in the garden, corresponding to:
- Crown jewels (Atelier, Brain, Coalition, etc.)
- Forest Protocol plan files
- Custom focus areas

Usage:
    kg plot                    List all plots
    kg plot <name>             Show specific plot details
    kg plot create <name>      Create new plot
    kg plot focus <name>       Set active plot
    kg plot link <name> <plan> Link plot to Forest plan
    kg plot discover           Discover plots from plans/

Example:
    kg plot                            # List all plots
    kg plot coalition-forge            # Show Coalition Forge details
    kg plot focus atelier              # Set Atelier as active plot
    kg plot create my-feature --path world.feature
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def _print_help() -> None:
    """Print help for plot command."""
    print(__doc__)
    print()
    print("SUBCOMMANDS:")
    print("  (none)               List all plots (default)")
    print("  <name>               Show specific plot details")
    print("  create <name>        Create new plot")
    print("  focus <name>         Set active plot")
    print("  link <name> <plan>   Link plot to Forest plan file")
    print("  discover             Discover plots from plans/")
    print()
    print("OPTIONS:")
    print("  --path <path>        AGENTESE path for new plot")
    print("  --description <text> Description for new plot")
    print("  --crown-jewel <name> Link to crown jewel")
    print("  --rigidity <0-1>     Initial rigidity (default: 0.5)")
    print("  --json               Output as JSON")
    print("  --help, -h           Show this help")


def cmd_plot(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Main entry point for the plot command.

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

            ctx = get_invocation_context("plot", args)
        except ImportError:
            pass

    # Handle --help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    json_mode = "--json" in args

    # Parse named arguments
    path = _extract_arg(args, "--path")
    description = _extract_arg(args, "--description")
    crown_jewel = _extract_arg(args, "--crown-jewel")
    rigidity_str = _extract_arg(args, "--rigidity")

    rigidity = 0.5
    if rigidity_str:
        try:
            rigidity = float(rigidity_str)
            rigidity = max(0.0, min(1.0, rigidity))
        except ValueError:
            pass

    # Get subcommand
    subcommand = None
    subcommand_args: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        if subcommand is None:
            subcommand = arg
        else:
            subcommand_args.append(arg)

    # Default: list plots
    if subcommand is None:
        subcommand = "list"

    # Run async handler
    return asyncio.run(
        _async_plot(
            subcommand=subcommand,
            subcommand_args=subcommand_args,
            path=path,
            description=description,
            crown_jewel=crown_jewel,
            rigidity=rigidity,
            json_mode=json_mode,
            ctx=ctx,
        )
    )


async def _async_plot(
    subcommand: str,
    subcommand_args: list[str],
    path: str | None,
    description: str | None,
    crown_jewel: str | None,
    rigidity: float,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Async implementation of plot command."""
    try:
        # Check for specific subcommands first
        match subcommand:
            case "list":
                return await _handle_list(json_mode, ctx)
            case "create":
                if not subcommand_args:
                    _emit_output(
                        "[PLOT] create requires a name. Usage: kg plot create <name> --path <path>",
                        {"error": "create requires a name"},
                        ctx,
                    )
                    return 1
                return await _handle_create(
                    subcommand_args[0],
                    path,
                    description,
                    crown_jewel,
                    rigidity,
                    json_mode,
                    ctx,
                )
            case "focus":
                if not subcommand_args:
                    _emit_output(
                        "[PLOT] focus requires a name. Usage: kg plot focus <name>",
                        {"error": "focus requires a name"},
                        ctx,
                    )
                    return 1
                return await _handle_focus(subcommand_args[0], json_mode, ctx)
            case "link":
                if len(subcommand_args) < 2:
                    _emit_output(
                        "[PLOT] link requires name and plan. Usage: kg plot link <name> <plan>",
                        {"error": "link requires name and plan"},
                        ctx,
                    )
                    return 1
                return await _handle_link(
                    subcommand_args[0], subcommand_args[1], json_mode, ctx
                )
            case "discover":
                return await _handle_discover(json_mode, ctx)
            case _:
                # Treat as plot name - show details
                return await _handle_show(subcommand, json_mode, ctx)

    except ImportError as e:
        _emit_output(
            f"[PLOT] Module not available: {e}",
            {"error": f"Module not available: {e}"},
            ctx,
        )
        return 1

    except Exception as e:
        _emit_output(
            f"[PLOT] Error: {e}",
            {"error": str(e)},
            ctx,
        )
        return 1


async def _handle_list(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle list subcommand - list all plots."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    plots_data = []
    for name, plot in garden.plots.items():
        plots_data.append({
            "name": name,
            "display_name": plot.display_name,
            "path": plot.path,
            "crown_jewel": plot.crown_jewel,
            "progress": plot.progress,
            "rigidity": plot.rigidity,
            "is_active": name == garden.active_plot,
            "tags": plot.tags,
        })

    result = {
        "plots": plots_data,
        "count": len(plots_data),
        "active_plot": garden.active_plot,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            f"",
            f"  PLOTS ({len(garden.plots)})",
            f"",
        ]
        for name, plot in garden.plots.items():
            active_marker = " <active>" if name == garden.active_plot else ""
            progress_bar = _progress_bar(plot.progress, 10)
            progress_pct = f"{plot.progress * 100:.0f}%"

            jewel_tag = f" [{plot.crown_jewel}]" if plot.crown_jewel else ""
            lines.append(
                f"  {plot.display_name:<20} {progress_bar} {progress_pct:>4}{jewel_tag}{active_marker}"
            )
            lines.append(f"    Path: {plot.path}")
            if plot.tags:
                lines.append(f"    Tags: {', '.join(plot.tags)}")
            lines.append("")

        lines.append(f"  Use 'kg plot <name>' for details, 'kg plot focus <name>' to activate.")
        lines.append("")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_show(
    name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle show - display specific plot details."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots
    from protocols.gardener_logos.projections.ascii import project_plot_to_ascii

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Normalize name (allow spaces, hyphens)
    normalized = name.lower().replace(" ", "-")

    plot = garden.plots.get(normalized)
    if not plot:
        # Try to find by display name
        for p_name, p in garden.plots.items():
            if p.display_name.lower() == name.lower():
                plot = p
                normalized = p_name
                break

    if not plot:
        available = list(garden.plots.keys())
        _emit_output(
            f"[PLOT] Plot not found: {name}. Available: {', '.join(available)}",
            {"error": f"Plot not found: {name}", "available": available},
            ctx,
        )
        return 1

    result = {
        "name": normalized,
        "display_name": plot.display_name,
        "path": plot.path,
        "description": plot.description,
        "plan_path": plot.plan_path,
        "crown_jewel": plot.crown_jewel,
        "progress": plot.progress,
        "rigidity": plot.rigidity,
        "prompts": plot.prompts,
        "tags": plot.tags,
        "is_active": normalized == garden.active_plot,
        "created_at": plot.created_at.isoformat(),
        "last_tended": plot.last_tended.isoformat(),
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        ascii_output = project_plot_to_ascii(plot, garden)
        _emit_output(ascii_output, result, ctx)

    return 0


async def _handle_create(
    name: str,
    path: str | None,
    description: str | None,
    crown_jewel: str | None,
    rigidity: float,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle create subcommand - create new plot."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots
    from protocols.gardener_logos.plots import create_plot

    if not path:
        # Generate path from name
        path = f"concept.custom.{name.replace('-', '_')}"

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Check if already exists
    normalized = name.lower().replace(" ", "-")
    if normalized in garden.plots:
        _emit_output(
            f"[PLOT] Plot already exists: {normalized}",
            {"error": f"Plot already exists: {normalized}"},
            ctx,
        )
        return 1

    # Create the plot
    plot = create_plot(
        name=normalized,
        path=path,
        description=description or "",
        crown_jewel=crown_jewel,
        rigidity=rigidity,
    )
    garden.plots[normalized] = plot

    result = {
        "status": "created",
        "name": normalized,
        "path": path,
        "description": description or "",
        "crown_jewel": crown_jewel,
        "rigidity": rigidity,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            f"",
            f"  PLOT CREATED: {plot.display_name}",
            f"",
            f"  Name:        {normalized}",
            f"  Path:        {path}",
            f"  Rigidity:    {rigidity:.0%}",
        ]
        if description:
            lines.append(f"  Description: {description}")
        if crown_jewel:
            lines.append(f"  Crown Jewel: {crown_jewel}")
        lines.append(f"")
        lines.append(f"  Use 'kg plot focus {normalized}' to make it active.")
        lines.append(f"")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_focus(
    name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle focus subcommand - set active plot."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Normalize name
    normalized = name.lower().replace(" ", "-")

    # Check if exists
    if normalized not in garden.plots:
        # Try to find by display name
        found = False
        for p_name, p in garden.plots.items():
            if p.display_name.lower() == name.lower():
                normalized = p_name
                found = True
                break

        if not found:
            available = list(garden.plots.keys())
            _emit_output(
                f"[PLOT] Plot not found: {name}. Available: {', '.join(available)}",
                {"error": f"Plot not found: {name}", "available": available},
                ctx,
            )
            return 1

    old_active = garden.active_plot
    garden.active_plot = normalized
    plot = garden.plots[normalized]

    result = {
        "status": "focused",
        "name": normalized,
        "display_name": plot.display_name,
        "previous_active": old_active,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            f"",
            f"  FOCUS: {plot.display_name}",
            f"",
            f"  Path:      {plot.path}",
            f"  Progress:  {_progress_bar(plot.progress, 10)} {plot.progress:.0%}",
        ]
        if old_active:
            lines.append(f"  Previous:  {old_active}")
        lines.append(f"")
        lines.append(f"  Subsequent tending operations will target this plot.")
        lines.append(f"")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_link(
    name: str,
    plan_path: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle link subcommand - link plot to Forest plan."""
    from protocols.gardener_logos import create_garden, create_crown_jewel_plots

    garden = create_garden(name="kgents")
    garden.plots = create_crown_jewel_plots()

    # Normalize name
    normalized = name.lower().replace(" ", "-")

    if normalized not in garden.plots:
        available = list(garden.plots.keys())
        _emit_output(
            f"[PLOT] Plot not found: {name}. Available: {', '.join(available)}",
            {"error": f"Plot not found: {name}", "available": available},
            ctx,
        )
        return 1

    plot = garden.plots[normalized]
    old_plan = plot.plan_path
    plot.plan_path = plan_path

    result = {
        "status": "linked",
        "name": normalized,
        "plan_path": plan_path,
        "previous_plan": old_plan,
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        lines = [
            f"",
            f"  LINKED: {plot.display_name} -> {plan_path}",
            f"",
        ]
        if old_plan:
            lines.append(f"  Previous plan: {old_plan}")
        lines.append(f"")

        _emit_output("\n".join(lines), result, ctx)

    return 0


async def _handle_discover(
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Handle discover subcommand - discover plots from Forest plans."""
    from protocols.gardener_logos.plots import discover_plots_from_forest

    discovered = await discover_plots_from_forest("plans")

    result = {
        "discovered": [
            {
                "name": p.name,
                "path": p.path,
                "plan_path": p.plan_path,
                "tags": p.tags,
            }
            for p in discovered
        ],
        "count": len(discovered),
    }

    if json_mode:
        import json

        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        if not discovered:
            lines = [
                f"",
                f"  No plots discovered from plans/",
                f"",
                f"  Make sure plans/ directory exists and contains .md files.",
                f"",
            ]
        else:
            lines = [
                f"",
                f"  DISCOVERED PLOTS ({len(discovered)})",
                f"",
            ]
            for plot in discovered:
                lines.append(f"  {plot.display_name}")
                lines.append(f"    Path: {plot.path}")
                lines.append(f"    Plan: {plot.plan_path}")
                lines.append("")

            lines.append(f"  Use 'kg plot create <name>' to add plots to your garden.")
            lines.append("")

        _emit_output("\n".join(lines), result, ctx)

    return 0


def _extract_arg(args: list[str], flag: str) -> str | None:
    """Extract value after a flag from args."""
    for i, arg in enumerate(args):
        if arg == flag and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith(f"{flag}="):
            return arg[len(flag) + 1 :]
    return None


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
    """
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)


__all__ = ["cmd_plot"]
