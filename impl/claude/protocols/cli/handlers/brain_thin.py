"""
Brain Handler: Thin routing shim to self.memory.* AGENTESE paths.

All business logic lives in services/brain/. This file only routes.

AGENTESE Path Mapping:
    kg brain                -> self.memory.manifest
    kg brain capture ...    -> self.memory.capture
    kg brain search ...     -> self.memory.recall
    kg brain ghost ...      -> self.memory.ghost.surface
    kg brain surface ...    -> void.memory.surface
    kg brain list           -> self.memory.manifest
    kg brain status         -> self.memory.manifest
    kg brain chat           -> self.jewel.brain.flow.chat.query (interactive)
    kg brain import         -> self.memory.import (batch)

See: docs/skills/metaphysical-fullstack.md, spec/protocols/cli.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

BRAIN_SUBCOMMAND_TO_PATH = {
    # Core operations
    "capture": "self.memory.capture",
    "search": "self.memory.recall",
    "ghost": "self.memory.ghost.surface",
    "surface": "void.memory.surface",
    "list": "self.memory.manifest",
    "status": "self.memory.manifest",
    # Chat (interactive via projection)
    "chat": "self.jewel.brain.flow.chat.query",
    # Import (batch operation)
    "import": "self.memory.import",
}

DEFAULT_PATH = "self.memory.manifest"


# === Main Entry Point ===


def cmd_brain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Holographic Brain: Route to AGENTESE self.memory.* paths.

    All business logic is in services/brain/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to AGENTESE path
    path = route_to_path(subcommand, BRAIN_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Project through CLI functor
    return project_command(path, args, ctx)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "status"  # default


def _print_help() -> None:
    """Print brain command help (projected from AGENTESE affordances)."""
    try:
        from protocols.cli.help_projector import create_help_projector
        from protocols.cli.help_renderer import render_help

        projector = create_help_projector()
        help_obj = projector.project("self.memory")
        print(render_help(help_obj))
    except ImportError:
        # Fallback to static help
        _print_help_fallback()


def _print_help_fallback() -> None:
    """Fallback static help if help projection unavailable."""
    help_text = """
kg brain - Holographic Brain (Crown Jewel Memory)

Commands:
  kg brain                      Show brain status
  kg brain capture "content"    Capture content to memory
  kg brain search "query"       Semantic search for similar memories
  kg brain ghost "context"      Surface memories (alias for search)
  kg brain surface              Serendipity: random memory from the void
  kg brain chat                 Interactive chat with holographic memory

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --trace                       Show AGENTESE path being invoked

AGENTESE Paths:
  self.memory.manifest          Brain status
  self.memory.capture           Capture content
  self.memory.recall            Semantic search

Examples:
  kg brain capture "Python is great for data science"
  kg brain search "programming language"
  kg brain chat
"""
    print(help_text.strip())


__all__ = ["cmd_brain"]
