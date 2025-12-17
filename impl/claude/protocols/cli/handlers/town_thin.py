"""
Town Handler: Thin routing shim to world.town.* AGENTESE paths.

All business logic lives in:
- agents/town/ - Simulation engine (TownFlux, Citizen, etc.)
- services/town/ - Persistence layer
- protocols/agentese/contexts/world_town.py - AGENTESE node

This file only routes CLI commands to AGENTESE paths.

AGENTESE Path Mapping:
    kg town                -> world.town.manifest
    kg town start          -> world.town.start
    kg town start2         -> world.town.start (phase2=true)
    kg town step           -> world.town.step
    kg town observe        -> world.town.observe
    kg town lens <name>    -> world.town.citizen.<name>.manifest
    kg town metrics        -> world.town.metrics
    kg town budget         -> world.town.budget
    kg town witness        -> world.town.witness
    kg town chat <name>    -> world.town.citizen.<name>.chat (interactive)
    kg town demo           -> world.town.demo (special demo mode)

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

TOWN_SUBCOMMAND_TO_PATH = {
    # Core operations
    "status": "world.town.manifest",
    "start": "world.town.start",
    "start2": "world.town.start",  # phase2 flag added in kwargs
    "step": "world.town.step",
    "observe": "world.town.observe",
    "witness": "world.town.witness",
    # Metrics
    "metrics": "world.town.metrics",
    "budget": "world.town.budget",
    # Citizen interaction (chat routes to citizen node)
    "chat": "world.town.citizen",  # Needs citizen name extraction
    "lens": "world.town.citizen",  # Needs citizen name extraction
    # Interactive modes (from old handler)
    "whisper": "world.town.citizen",
    "inhabit": "world.town.citizen",
    "intervene": "world.town.intervene",
    "gather": "world.town.gather",
    # Demo mode (preserves old demo functionality)
    "demo": "world.town.demo",
    # Telegram notifications
    "telegram": "world.town.telegram",
}

DEFAULT_PATH = "world.town.manifest"


# === Main Entry Point ===


def cmd_town(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Agent Town: Route to AGENTESE world.town.* paths.

    All business logic is in agents/town/ and services/town/.
    This handler only routes commands.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Handle citizen-specific commands
    if subcommand in ("chat", "lens", "whisper", "inhabit"):
        return _handle_citizen_command(subcommand, args, ctx)

    # Handle demo (special case - preserves old demo functionality)
    if subcommand == "demo":
        return _handle_demo(args, ctx)

    # Route to AGENTESE path
    path = route_to_path(subcommand, TOWN_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Extract kwargs for specific subcommands
    kwargs = _extract_kwargs(subcommand, args)

    # Project through CLI functor
    return project_command(path, args, ctx, kwargs=kwargs)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"  # default


def _extract_kwargs(subcommand: str, args: list[str]) -> dict[str, Any]:
    """
    Extract kwargs from args based on subcommand.

    Handles:
    - start2: phase2=True
    - seed from positional/flag
    """
    kwargs: dict[str, Any] = {}

    # Handle start2 -> phase2 flag
    if subcommand == "start2":
        kwargs["phase2"] = True

    # Extract seed if provided
    for i, arg in enumerate(args):
        if arg == "--seed" and i + 1 < len(args):
            try:
                kwargs["seed"] = int(args[i + 1])
            except ValueError:
                pass
        elif arg.startswith("--seed="):
            try:
                kwargs["seed"] = int(arg.split("=", 1)[1])
            except ValueError:
                pass
        elif subcommand in ("start", "start2") and arg.isdigit():
            # Positional seed for start command
            kwargs["seed"] = int(arg)

    return kwargs


def _handle_citizen_command(
    subcommand: str,
    args: list[str],
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle citizen-specific commands that need name extraction.

    Commands:
    - kg town chat <name> -> world.town.citizen.<name>.chat
    - kg town lens <name> [lod] -> world.town.citizen.<name>.manifest
    - kg town whisper <name> "msg" -> world.town.citizen.<name>.whisper
    - kg town inhabit <name> -> world.town.citizen.<name>.inhabit
    """
    # Extract citizen name
    citizen_name = None
    extra_args: list[str] = []

    skip_next = False
    found_subcommand = False

    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith("-"):
            if arg == "--citizen" and i + 1 < len(args):
                citizen_name = args[i + 1]
                skip_next = True
            continue
        if not found_subcommand:
            found_subcommand = True
            continue
        if citizen_name is None:
            citizen_name = arg
        else:
            extra_args.append(arg)

    if citizen_name is None:
        print(f"[TOWN] Usage: kg town {subcommand} <citizen_name>")
        print("  Available citizens: elara, finn, maya, oren, quinn, sage, wren")
        return 1

    # Build path based on subcommand
    match subcommand:
        case "chat":
            path = f"world.town.citizen.{citizen_name.lower()}.chat"
        case "lens":
            path = f"world.town.citizen.{citizen_name.lower()}.manifest"
        case "whisper":
            path = f"world.town.citizen.{citizen_name.lower()}.whisper"
        case "inhabit":
            path = f"world.town.citizen.{citizen_name.lower()}.inhabit"
        case _:
            path = f"world.town.citizen.{citizen_name.lower()}.manifest"

    # Extract kwargs
    kwargs: dict[str, Any] = {}
    if subcommand == "lens" and extra_args:
        try:
            kwargs["lod"] = int(extra_args[0])
        except ValueError:
            kwargs["lod"] = 2
    elif subcommand == "whisper" and extra_args:
        kwargs["message"] = " ".join(extra_args).strip('"')

    return project_command(
        path, args, ctx, kwargs=kwargs, entity_name=citizen_name.title()
    )


def _handle_demo(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Handle demo command - preserves old demo functionality.

    The demo is interactive and complex, so we delegate to old handler for now.
    Future: migrate to world.town.demo aspect.
    """
    # Import old handler for demo (temporary bridge)
    from protocols.cli.handlers.town import cmd_town as cmd_town_old

    # Strip 'demo' and pass remaining args
    demo_args = ["demo"] + [a for a in args if a != "demo"]
    return cmd_town_old(demo_args, ctx)


def _print_help() -> None:
    """Print town command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help
    show_projected_help("world.town", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg town - Agent Town (Crown Jewel Simulation)

Commands:
  kg town                      Show town status
  kg town start                Start simulation
  kg town step                 Advance simulation
  kg town observe              MESA view
  kg town chat <name>          Chat with citizen

Options:
  --help, -h                   Show this help message
  --json                       Output as JSON
  --trace                      Show AGENTESE path

AGENTESE Paths:
  world.town.manifest          Town status
  world.town.start             Start simulation
  world.town.citizen.<name>.*  Citizen interaction

Examples:
  kg town start
  kg town chat elara
  kg town observe
"""
    print(help_text.strip())


__all__ = ["cmd_town"]
