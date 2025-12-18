"""
Forge Handler: Thin routing shim to world.forge.* AGENTESE paths.

All business logic lives in services/forge/. This file only routes.

AGENTESE Path Mapping:
    kg forge                      -> world.forge.manifest
    kg forge status               -> world.forge.manifest
    kg forge artisans             -> world.forge.artisans (legacy)
    kg forge commission ...       -> world.forge.commission (legacy)
    kg forge gallery              -> world.forge.gallery_items
    kg forge view <id>            -> world.forge.gallery_view
    kg forge collaborate ...      -> world.forge.collaborate (legacy)
    kg forge workshop create ...  -> world.forge.workshop_create
    kg forge workshop join ...    -> world.forge.workshop_join
    kg forge workshop list        -> world.forge.workshop_list
    kg forge workshop end ...     -> world.forge.workshop_end
    kg forge contribute ...       -> world.forge.contribute
    kg forge contributions        -> world.forge.contributions
    kg forge exhibition create    -> world.forge.exhibition_create
    kg forge exhibition open      -> world.forge.exhibition_open
    kg forge gallery add          -> world.forge.gallery_add
    kg forge gallery view         -> world.forge.gallery_view
    kg forge gallery items        -> world.forge.gallery_items

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

# Main subcommand routing
FORGE_SUBCOMMAND_TO_PATH = {
    # Core operations
    "status": "world.forge.manifest",
    # Workshop management
    "workshop": "world.forge.workshop_list",  # Default for 'kg forge workshop'
    # Contributions
    "contribute": "world.forge.contribute",
    "contributions": "world.forge.contributions",
    # Gallery
    "gallery": "world.forge.gallery_items",
    "view": "world.forge.gallery_view",
    # Exhibition
    "exhibition": "world.forge.exhibition_create",
    # Legacy commands (route to old handler for now)
    "artisans": "world.forge.artisans",
    "commission": "world.forge.commission",
    "collaborate": "world.forge.collaborate",
    "exquisite": "world.forge.exquisite",
    "handoff": "world.forge.handoff",
    "constrain": "world.forge.constrain",
    "inspire": "world.forge.inspire",
    "queue": "world.forge.queue",
    "pending": "world.forge.pending",
    "process": "world.forge.process",
    "search": "world.forge.search",
    "seed": "world.forge.seed",
    "lineage": "world.forge.lineage",
    "festival": "world.forge.festival",
    "tokens": "world.forge.tokens",
}

# Two-word subcommand routing (e.g., "workshop create", "gallery add")
FORGE_TWO_WORD_TO_PATH = {
    # Workshop
    "workshop_create": "world.forge.workshop_create",
    "workshop_join": "world.forge.workshop_join",
    "workshop_list": "world.forge.workshop_list",
    "workshop_end": "world.forge.workshop_end",
    # Gallery
    "gallery_add": "world.forge.gallery_add",
    "gallery_view": "world.forge.gallery_view",
    "gallery_items": "world.forge.gallery_items",
    # Exhibition
    "exhibition_create": "world.forge.exhibition_create",
    "exhibition_open": "world.forge.exhibition_open",
}

DEFAULT_PATH = "world.forge.manifest"


# === Main Entry Point ===


def cmd_forge(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Tiny Forge: Route to AGENTESE world.forge.* paths.

    All business logic is in services/forge/. This handler only routes.
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
        if two_word in FORGE_TWO_WORD_TO_PATH:
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
    if subcommand in FORGE_TWO_WORD_TO_PATH:
        return FORGE_TWO_WORD_TO_PATH[subcommand]

    # Then single word
    if subcommand in FORGE_SUBCOMMAND_TO_PATH:
        return FORGE_SUBCOMMAND_TO_PATH[subcommand]

    return DEFAULT_PATH


def _print_help() -> None:
    """Print forge command help (projected from AGENTESE affordances)."""
    from protocols.cli.handlers._help import show_projected_help

    show_projected_help("world.forge", _print_help_fallback)


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg forge - Tiny Forge (Crown Jewel Creative Workshop)

Commands:
  kg forge                      Show forge status
  kg forge workshop create      Create a workshop
  kg forge workshop join        Add artisan
  kg forge contribute           Submit contribution
  kg forge gallery              View gallery
  kg forge exhibition           View exhibition

Options:
  --help, -h                      Show this help message
  --json                          Output as JSON
  --trace                         Show AGENTESE path

AGENTESE Paths:
  world.forge.manifest          Forge status
  world.forge.workshop_create   Create workshop
  world.forge.contribute        Submit contribution
  world.forge.gallery_view      View exhibition

Examples:
  kg forge workshop create "Poetry Circle"
  kg forge contribute artisan-abc "A haiku"
  kg forge gallery
"""
    print(help_text.strip())


__all__ = ["cmd_forge"]
