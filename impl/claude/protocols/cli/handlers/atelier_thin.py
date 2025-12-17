"""
Atelier Handler: Thin routing shim to world.atelier.* AGENTESE paths.

All business logic lives in services/atelier/. This file only routes.

AGENTESE Path Mapping:
    kg atelier                      -> world.atelier.manifest
    kg atelier status               -> world.atelier.manifest
    kg atelier artisans             -> world.atelier.artisans (legacy)
    kg atelier commission ...       -> world.atelier.commission (legacy)
    kg atelier gallery              -> world.atelier.gallery_items
    kg atelier view <id>            -> world.atelier.gallery_view
    kg atelier collaborate ...      -> world.atelier.collaborate (legacy)
    kg atelier workshop create ...  -> world.atelier.workshop_create
    kg atelier workshop join ...    -> world.atelier.workshop_join
    kg atelier workshop list        -> world.atelier.workshop_list
    kg atelier workshop end ...     -> world.atelier.workshop_end
    kg atelier contribute ...       -> world.atelier.contribute
    kg atelier contributions        -> world.atelier.contributions
    kg atelier exhibition create    -> world.atelier.exhibition_create
    kg atelier exhibition open      -> world.atelier.exhibition_open
    kg atelier gallery add          -> world.atelier.gallery_add
    kg atelier gallery view         -> world.atelier.gallery_view
    kg atelier gallery items        -> world.atelier.gallery_items

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

# Main subcommand routing
ATELIER_SUBCOMMAND_TO_PATH = {
    # Core operations
    "status": "world.atelier.manifest",
    # Workshop management
    "workshop": "world.atelier.workshop_list",  # Default for 'kg atelier workshop'
    # Contributions
    "contribute": "world.atelier.contribute",
    "contributions": "world.atelier.contributions",
    # Gallery
    "gallery": "world.atelier.gallery_items",
    "view": "world.atelier.gallery_view",
    # Exhibition
    "exhibition": "world.atelier.exhibition_create",
    # Legacy commands (route to old handler for now)
    "artisans": "world.atelier.artisans",
    "commission": "world.atelier.commission",
    "collaborate": "world.atelier.collaborate",
    "exquisite": "world.atelier.exquisite",
    "handoff": "world.atelier.handoff",
    "constrain": "world.atelier.constrain",
    "inspire": "world.atelier.inspire",
    "queue": "world.atelier.queue",
    "pending": "world.atelier.pending",
    "process": "world.atelier.process",
    "search": "world.atelier.search",
    "seed": "world.atelier.seed",
    "lineage": "world.atelier.lineage",
    "festival": "world.atelier.festival",
    "tokens": "world.atelier.tokens",
}

# Two-word subcommand routing (e.g., "workshop create", "gallery add")
ATELIER_TWO_WORD_TO_PATH = {
    # Workshop
    "workshop_create": "world.atelier.workshop_create",
    "workshop_join": "world.atelier.workshop_join",
    "workshop_list": "world.atelier.workshop_list",
    "workshop_end": "world.atelier.workshop_end",
    # Gallery
    "gallery_add": "world.atelier.gallery_add",
    "gallery_view": "world.atelier.gallery_view",
    "gallery_items": "world.atelier.gallery_items",
    # Exhibition
    "exhibition_create": "world.atelier.exhibition_create",
    "exhibition_open": "world.atelier.exhibition_open",
}

DEFAULT_PATH = "world.atelier.manifest"


# === Main Entry Point ===


def cmd_atelier(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Tiny Atelier: Route to AGENTESE world.atelier.* paths.

    All business logic is in services/atelier/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand (may be one or two words)
    subcommand, remaining_args = _parse_subcommand(args)

    # Route to AGENTESE path
    path = _resolve_path(subcommand)

    # Project through CLI functor
    return project_command(path, remaining_args, ctx)


def _parse_subcommand(args: list[str]) -> tuple[str, list[str]]:
    """
    Extract subcommand from args, handling two-word commands.

    Returns:
        (subcommand, remaining_args)
    """
    non_flag_args = [a for a in args if not a.startswith("-")]

    if len(non_flag_args) >= 2:
        # Check for two-word command (e.g., "workshop create")
        two_word = f"{non_flag_args[0]}_{non_flag_args[1]}"
        if two_word in ATELIER_TWO_WORD_TO_PATH:
            # Remove first two args, keep the rest
            remaining = args.copy()
            for word in non_flag_args[:2]:
                if word in remaining:
                    remaining.remove(word)
            return two_word, remaining

    if len(non_flag_args) >= 1:
        # Single word command
        subcommand = non_flag_args[0].lower()
        remaining = args.copy()
        if subcommand in remaining:
            remaining.remove(subcommand)
        return subcommand, remaining

    return "status", args  # default


def _resolve_path(subcommand: str) -> str:
    """Resolve subcommand to AGENTESE path."""
    # Check two-word first
    if subcommand in ATELIER_TWO_WORD_TO_PATH:
        return ATELIER_TWO_WORD_TO_PATH[subcommand]

    # Then single word
    if subcommand in ATELIER_SUBCOMMAND_TO_PATH:
        return ATELIER_SUBCOMMAND_TO_PATH[subcommand]

    return DEFAULT_PATH


def _print_help() -> None:
    """Print atelier command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help
    show_projected_help("world.atelier", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg atelier - Tiny Atelier (Crown Jewel Creative Workshop)

Commands:
  kg atelier                      Show atelier status
  kg atelier workshop create      Create a workshop
  kg atelier workshop join        Add artisan
  kg atelier contribute           Submit contribution
  kg atelier gallery              View gallery
  kg atelier exhibition           View exhibition

Options:
  --help, -h                      Show this help message
  --json                          Output as JSON
  --trace                         Show AGENTESE path

AGENTESE Paths:
  world.atelier.manifest          Atelier status
  world.atelier.workshop_create   Create workshop
  world.atelier.contribute        Submit contribution
  world.atelier.gallery_view      View exhibition

Examples:
  kg atelier workshop create "Poetry Circle"
  kg atelier contribute artisan-abc "A haiku"
  kg atelier gallery
"""
    print(help_text.strip())


__all__ = ["cmd_atelier"]
