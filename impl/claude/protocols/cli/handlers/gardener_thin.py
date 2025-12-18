"""
Gardener Handler: Thin routing shim to concept.gardener.* AGENTESE paths.

All business logic lives in agents/gardener/ and services/gardener/.
This file only routes.

AGENTESE Path Mapping:
    kg gardener                -> concept.gardener.manifest
    kg gardener start ...      -> concept.gardener.start
    kg gardener advance        -> concept.gardener.advance
    kg gardener cycle          -> concept.gardener.cycle
    kg gardener poly           -> concept.gardener.polynomial
    kg gardener sessions       -> concept.gardener.sessions
    kg gardener intent ...     -> concept.gardener.intent
    kg gardener chat           -> concept.gardener.chat (interactive)
    kg gardener garden         -> self.garden.manifest
    kg gardener plant ...      -> self.garden.plant
    kg gardener harvest        -> self.garden.harvest
    kg gardener water ...      -> self.garden.nurture
    kg gardener harvest-to-brain -> self.garden.harvest_to_brain
    kg gardener surprise       -> void.garden.sip

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

GARDENER_SUBCOMMAND_TO_PATH = {
    # Session operations (concept.gardener.*)
    "status": "concept.gardener.manifest",
    "session": "concept.gardener.manifest",
    "start": "concept.gardener.start",
    "create": "concept.gardener.start",  # alias
    "new": "concept.gardener.start",  # alias
    "advance": "concept.gardener.advance",
    "next": "concept.gardener.advance",  # alias
    "cycle": "concept.gardener.cycle",
    "polynomial": "concept.gardener.polynomial",
    "poly": "concept.gardener.polynomial",  # alias
    "manifest": "concept.gardener.polynomial",  # alias
    "sessions": "concept.gardener.sessions",
    "list": "concept.gardener.sessions",  # alias
    "intent": "concept.gardener.intent",
    "chat": "concept.gardener.chat",
    # Garden operations (self.garden.*)
    "garden": "self.garden.manifest",
    "plant": "self.garden.plant",
    "harvest": "self.garden.harvest",
    "water": "self.garden.nurture",
    "nurture": "self.garden.nurture",  # alias
    "harvest-to-brain": "self.garden.harvest_to_brain",
    "reap": "self.garden.harvest_to_brain",  # alias
    # Void operations (void.garden.*)
    "surprise": "void.garden.sip",
    "serendipity": "void.garden.sip",  # alias
    "void": "void.garden.sip",  # alias
}

DEFAULT_PATH = "concept.gardener.manifest"


# === Main Entry Point ===


def cmd_gardener(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    The Gardener: Route to AGENTESE concept.gardener.*, self.garden.*, void.garden.* paths.

    All business logic is in services/gardener/ and agents/gardener/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to AGENTESE path
    path = route_to_path(subcommand, GARDENER_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Parse additional kwargs for specific commands
    kwargs = _parse_gardener_kwargs(args, subcommand)

    # Project through CLI functor
    return project_command(path, args, ctx, kwargs=kwargs)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"  # default


def _parse_gardener_kwargs(args: list[str], subcommand: str) -> dict[str, str | list[str]]:
    """Parse command-specific kwargs."""
    kwargs = {}

    # Skip subcommand and flags to find positional content
    positional = []
    for i, arg in enumerate(args):
        if i == 0 and arg.lower() == subcommand:
            continue
        if arg.startswith("-"):
            continue
        positional.append(arg)

    content = " ".join(positional).strip() if positional else None

    if subcommand in ("start", "create", "new") and content:
        kwargs["name"] = content
    elif subcommand == "intent" and content:
        kwargs["description"] = content
    elif subcommand == "plant" and content:
        kwargs["content"] = content
    elif subcommand in ("water", "nurture") and positional:
        kwargs["idea_ref"] = positional[0]
        if len(positional) > 1:
            kwargs["evidence"] = " ".join(positional[1:])

    return kwargs


def _print_help() -> None:
    """Print gardener command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help
    show_projected_help("self.forest.gardener", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg gardener - The Gardener (Crown Jewel Development Sessions)

Commands:
  kg gardener                      Show session status
  kg gardener start [NAME]         Start development session
  kg gardener advance              Advance to next phase
  kg gardener plant "idea"         Plant a new idea
  kg gardener harvest              Show ideas ready to harvest
  kg gardener chat                 Interactive chat

Options:
  --help, -h                       Show this help message
  --json                           Output as JSON
  --trace                          Show AGENTESE path

Session Phases:
  SENSE   - Gather context
  ACT     - Execute intent
  REFLECT - Consolidate learnings

AGENTESE Paths:
  concept.gardener.*               Session lifecycle
  self.garden.*                    Idea lifecycle

Examples:
  kg gardener start "Crown Jewels"
  kg gardener advance
  kg gardener plant "Great idea"
"""
    print(help_text.strip())


__all__ = ["cmd_gardener"]
