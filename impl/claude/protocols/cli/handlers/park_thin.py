"""
Park Handler: Thin routing shim to world.park.* AGENTESE paths.

All business logic lives in agents/park/ and services/park/.
This file only routes.

AGENTESE Path Mapping:
    kg park                     -> world.park.manifest
    kg park start ...           -> world.park.scenario.start
    kg park status              -> world.park.manifest
    kg park tick ...            -> world.park.scenario.tick
    kg park phase ...           -> world.park.scenario.phase
    kg park complete ...        -> world.park.scenario.complete
    kg park mask list           -> world.park.mask.manifest
    kg park mask show <name>    -> world.park.mask.show
    kg park mask don <name>     -> world.park.mask.don
    kg park mask doff           -> world.park.mask.doff
    kg park mask transform      -> world.park.mask.transform
    kg park force               -> world.park.force.use

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

PARK_SUBCOMMAND_TO_PATH = {
    # Scenario operations
    "status": "world.park.manifest",
    "start": "world.park.scenario.start",
    "tick": "world.park.scenario.tick",
    "phase": "world.park.scenario.phase",
    "complete": "world.park.scenario.complete",
    # Mask operations
    "mask": "world.park.mask.manifest",  # Will be further parsed
    # Force mechanic
    "force": "world.park.force.use",
}

# Mask subcommand routing
MASK_SUBCOMMAND_TO_PATH = {
    "list": "world.park.mask.manifest",
    "show": "world.park.mask.show",
    "don": "world.park.mask.don",
    "doff": "world.park.mask.doff",
    "transform": "world.park.mask.transform",
}

DEFAULT_PATH = "world.park.manifest"


# === Main Entry Point ===


def cmd_park(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Punchdrunk Park: Route to AGENTESE world.park.* paths.

    All business logic is in services/park/ and agents/park/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Handle mask sub-subcommands
    if subcommand == "mask":
        return _handle_mask_command(args, ctx)

    # Route to AGENTESE path
    path = route_to_path(subcommand, PARK_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Parse additional kwargs for specific commands
    kwargs = _parse_park_kwargs(args, subcommand)

    # Project through CLI functor
    return project_command(path, args, ctx, kwargs=kwargs)


def _handle_mask_command(args: list[str], ctx: "InvocationContext | None") -> int:
    """Handle mask sub-subcommands."""
    # Find mask subcommand
    mask_idx = -1
    for i, arg in enumerate(args):
        if arg.lower() == "mask":
            mask_idx = i
            break

    if mask_idx == -1 or mask_idx + 1 >= len(args):
        # No sub-subcommand, default to list
        path = "world.park.mask.manifest"
        return project_command(path, args, ctx)

    mask_subcommand = args[mask_idx + 1].lower()
    path = route_to_path(mask_subcommand, MASK_SUBCOMMAND_TO_PATH, "world.park.mask.manifest")

    # Parse kwargs for mask commands
    kwargs = {}
    if mask_subcommand in ("show", "don") and mask_idx + 2 < len(args):
        kwargs["name"] = args[mask_idx + 2]

    return project_command(path, args, ctx, kwargs=kwargs)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"  # default


def _parse_park_kwargs(args: list[str], subcommand: str) -> dict[str, str | int | bool]:
    """Parse command-specific kwargs."""
    kwargs = {}

    # Parse flags
    for i, arg in enumerate(args):
        if arg.startswith("--timer="):
            kwargs["timer"] = arg.split("=")[1]
        elif arg.startswith("--template="):
            kwargs["template"] = arg.split("=")[1]
        elif arg.startswith("--count="):
            kwargs["count"] = int(arg.split("=")[1])
        elif arg.startswith("--mask="):
            kwargs["mask"] = arg.split("=")[1]
        elif arg == "--accelerated":
            kwargs["accelerated"] = True
        elif arg == "--real-time":
            kwargs["accelerated"] = False

    # Parse positional args for specific commands
    positional = []
    skip_next = False
    for i, arg in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if i == 0 and arg.lower() == subcommand:
            continue
        if arg.startswith("-"):
            # Check if next arg is a flag value
            if "=" not in arg and i + 1 < len(args) and not args[i + 1].startswith("-"):
                skip_next = True
            continue
        positional.append(arg)

    if subcommand == "phase" and positional:
        kwargs["target"] = positional[0]
    elif subcommand == "complete" and positional:
        kwargs["outcome"] = positional[0]

    return kwargs


def _print_help() -> None:
    """Print park command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help

    show_projected_help("world.park", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg park - Punchdrunk Park (Crown Jewel Crisis Practice)

Commands:
  kg park                       Show scenario status
  kg park start                 Start a crisis scenario
  kg park tick                  Advance timers
  kg park mask don <name>       Wear a dialogue mask
  kg park complete              End scenario

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --trace                       Show AGENTESE path
  --timer=TYPE                  Timer: gdpr, sec, hipaa

AGENTESE Paths:
  world.park.manifest           Park status
  world.park.scenario.*         Scenario lifecycle
  world.park.mask.*             Dialogue masks

Examples:
  kg park start --timer=gdpr
  kg park tick --count=5
  kg park mask don trickster
"""
    print(help_text.strip())


__all__ = ["cmd_park"]
