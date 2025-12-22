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
    kg brain extinct ...    -> void.extinct.* (extinction protocol)

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
    # Extinction protocol (Memory-First Docs)
    "extinct": "void.extinct.list",  # Default to list
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

    # Handle extinct subcommand specially (has sub-subcommands)
    if subcommand == "extinct":
        return _handle_extinct(args, ctx)

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


def _handle_extinct(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Handle extinction protocol subcommands.

    kg brain extinct              -> list all extinction events
    kg brain extinct list         -> list all extinction events
    kg brain extinct show <id>    -> show details of an event
    kg brain extinct wisdom <mod> -> get ghost wisdom from module

    AGENTESE mapping:
        list   -> void.extinct.list
        show   -> void.extinct.show
        wisdom -> void.extinct.wisdom
    """
    import asyncio
    import json

    # Parse sub-subcommand (skip "extinct")
    sub_sub = "list"  # default
    event_id = None
    module_prefix = None
    found_extinct = False

    for arg in args:
        if arg.startswith("-"):
            continue
        if not found_extinct:
            if arg.lower() == "extinct":
                found_extinct = True
            continue
        # First non-flag arg after "extinct" is the sub-subcommand
        if sub_sub == "list":  # still looking for sub-subcommand
            if arg.lower() in ("list", "show", "wisdom"):
                sub_sub = arg.lower()
            else:
                # It's an event_id for implicit "show"
                event_id = arg
                sub_sub = "show"
        else:
            # Second arg is event_id or module_prefix
            if sub_sub == "show":
                event_id = arg
            elif sub_sub == "wisdom":
                module_prefix = arg

    async def run_extinct() -> int:
        try:
            import os

            os.environ.setdefault(
                "KGENTS_DATABASE_URL",
                "postgresql+asyncpg://kgents:kgents@localhost:5432/kgents",
            )

            from services.bootstrap import bootstrap_services, get_service

            await bootstrap_services()
            brain = await get_service("brain_persistence")

            as_json = "--json" in args

            if sub_sub == "list":
                events = await brain.get_extinction_events()
                if as_json:
                    print(
                        json.dumps(
                            [
                                {
                                    "id": e.id,
                                    "reason": e.reason,
                                    "commit": e.commit,
                                    "preserved_count": e.preserved_count,
                                    "deleted_paths": e.deleted_paths,
                                }
                                for e in events
                            ],
                            indent=2,
                        )
                    )
                else:
                    if not events:
                        print("No extinction events recorded.")
                        return 0
                    print("Extinction Events")
                    print("=" * 50)
                    for e in events:
                        print(f"\n{e.id}")
                        print(f"  Reason: {e.reason}")
                        print(f"  Commit: {e.commit}")
                        print(f"  Preserved: {e.preserved_count} teaching crystals")
                return 0

            elif sub_sub == "show":
                if not event_id:
                    print("Usage: kg brain extinct show <event_id>")
                    return 1
                event = await brain.get_extinction_event(event_id)
                if not event:
                    # Try prefix match
                    events = await brain.get_extinction_events()
                    for e in events:
                        if e.id.startswith(event_id):
                            event = e
                            break
                if not event:
                    print(f"Extinction event not found: {event_id}")
                    return 1
                if as_json:
                    print(
                        json.dumps(
                            {
                                "id": event.id,
                                "reason": event.reason,
                                "commit": event.commit,
                                "decision_doc": event.decision_doc,
                                "deleted_paths": event.deleted_paths,
                                "successor_map": event.successor_map,
                                "preserved_count": event.preserved_count,
                            },
                            indent=2,
                        )
                    )
                else:
                    print(f"Extinction Event: {event.id}")
                    print("=" * 50)
                    print(f"Reason: {event.reason}")
                    print(f"Commit: {event.commit}")
                    if event.decision_doc:
                        print(f"Decision Doc: {event.decision_doc}")
                    print("\nDeleted Paths:")
                    for p in event.deleted_paths:
                        successor = event.successor_map.get(p.rstrip("/"), "(removed)")
                        print(f"  - {p} -> {successor}")
                    print(f"\nPreserved: {event.preserved_count} teaching crystals")
                return 0

            elif sub_sub == "wisdom":
                ghosts = await brain.get_extinct_wisdom(module_prefix=module_prefix)
                if as_json:
                    print(
                        json.dumps(
                            [
                                {
                                    "insight": g.teaching.insight,
                                    "severity": g.teaching.severity,
                                    "source_module": g.teaching.source_module,
                                    "source_symbol": g.teaching.source_symbol,
                                    "successor": g.successor,
                                }
                                for g in ghosts
                            ],
                            indent=2,
                        )
                    )
                else:
                    if not ghosts:
                        mod_msg = f" for '{module_prefix}'" if module_prefix else ""
                        print(f"No ancestral wisdom found{mod_msg}.")
                        return 0
                    print("Ancestral Wisdom (From Deleted Code)")
                    print("=" * 50)
                    for g in ghosts[:20]:
                        icon = {
                            "critical": "\U0001f6a8",
                            "warning": "\u26a0\ufe0f",
                            "info": "\u2139\ufe0f",
                        }.get(g.teaching.severity, "\u2022")
                        print(f"\n{icon} {g.teaching.source_module}::{g.teaching.source_symbol}")
                        print(f"   {g.teaching.insight}")
                        if g.successor:
                            print(f"   -> Migrated to: {g.successor}")
                    if len(ghosts) > 20:
                        print(f"\n... and {len(ghosts) - 20} more")
                return 0

            else:
                print(f"Unknown extinct subcommand: {sub_sub}")
                return 1

        except Exception as e:
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            return 1

    return asyncio.run(run_extinct())


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

Extinction Protocol (Memory-First Docs):
  kg brain extinct              List extinction events
  kg brain extinct list         List extinction events
  kg brain extinct show <id>    Show extinction event details
  kg brain extinct wisdom       Show ancestral wisdom from deleted code
  kg brain extinct wisdom <mod> Show wisdom from specific deleted module

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --trace                       Show AGENTESE path being invoked

AGENTESE Paths:
  self.memory.manifest          Brain status
  self.memory.capture           Capture content
  self.memory.recall            Semantic search
  void.extinct.list             List extinction events
  void.extinct.wisdom           Ancestral wisdom

Examples:
  kg brain capture "Python is great for data science"
  kg brain search "programming language"
  kg brain extinct wisdom services.town
  kg brain chat
"""
    print(help_text.strip())


__all__ = ["cmd_brain"]
