"""
Sovereign Handler: Thin routing shim to concept.sovereign.* AGENTESE paths.

All business logic lives in services/sovereign/. This file only routes.

AGENTESE Path Mapping:
    kg sovereign                 -> concept.sovereign.manifest
    kg sovereign status          -> concept.sovereign.manifest
    kg sovereign list [prefix]   -> concept.sovereign.list
    kg sovereign query <path>    -> concept.sovereign.query
    kg sovereign ingest <path>   -> concept.sovereign.ingest
    kg sovereign diff <path>     -> concept.sovereign.diff
    kg sovereign bootstrap <dir> -> concept.sovereign.bootstrap
    kg sovereign sync <path>     -> concept.sovereign.sync

See: docs/skills/metaphysical-fullstack.md, spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler
from protocols.cli.projection import project_command, route_to_path

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# === Path Routing ===

SOVEREIGN_SUBCOMMAND_TO_PATH = {
    # Status operations
    "status": "concept.sovereign.manifest",
    "list": "concept.sovereign.list",
    "query": "concept.sovereign.query",
    "diff": "concept.sovereign.diff",
    # Mutation operations
    "ingest": "concept.sovereign.ingest",
    "bootstrap": "concept.sovereign.bootstrap",
    "sync": "concept.sovereign.sync",
}

DEFAULT_PATH = "concept.sovereign.manifest"


# === Main Entry Point ===


@handler("sovereign", is_async=False, tier=1, description="Inbound sovereignty control")
def cmd_sovereign(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Inbound Sovereignty: Route to AGENTESE concept.sovereign.* paths.

    All business logic is in services/sovereign/. This handler only routes.
    """
    # Parse help flag (special case - not routed)
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)
    remaining = args[1:] if len(args) > 1 else []

    # Handle special subcommands that need CLI-side logic
    if subcommand == "bootstrap":
        return _handle_bootstrap(remaining, ctx)
    if subcommand == "ingest":
        return _handle_ingest(remaining, ctx)

    # Route to AGENTESE path
    path = route_to_path(subcommand, SOVEREIGN_SUBCOMMAND_TO_PATH, DEFAULT_PATH)

    # Build kwargs from remaining args
    cmd_kwargs = _parse_kwargs(subcommand, remaining)

    # Project through CLI functor
    return project_command(path, remaining, ctx, kwargs=cmd_kwargs)


def _parse_subcommand(args: list[str]) -> str:
    """Extract the subcommand from args."""
    if not args:
        return ""
    first = args[0]
    if first.startswith("-"):
        return ""
    return first


def _parse_kwargs(subcommand: str, args: list[str]) -> dict[str, str]:
    """Parse subcommand-specific kwargs from args."""
    kwargs = {}

    if subcommand == "list":
        # kg sovereign list [prefix]
        if args and not args[0].startswith("-"):
            kwargs["prefix"] = args[0]

    elif subcommand == "query":
        # kg sovereign query <path>
        # Use "entity_path" to avoid conflict with Logos.invoke's "path" param
        if args and not args[0].startswith("-"):
            kwargs["entity_path"] = args[0]

    elif subcommand == "diff":
        # kg sovereign diff <path>
        if args and not args[0].startswith("-"):
            kwargs["entity_path"] = args[0]

    elif subcommand == "sync":
        # kg sovereign sync <path>
        if args and not args[0].startswith("-"):
            kwargs["entity_path"] = args[0]

    return kwargs


def _handle_bootstrap(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Handle bootstrap command with CLI-side file discovery.

    kg sovereign bootstrap <dir> [--pattern GLOB] [--dry-run]
    """
    # Parse arguments
    root = None
    pattern = "**/*"
    dry_run = False

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--pattern" and i + 1 < len(args):
            pattern = args[i + 1]
            i += 2
        elif arg == "--dry-run":
            dry_run = True
            i += 1
        elif not arg.startswith("-") and root is None:
            root = arg
            i += 1
        else:
            i += 1

    if not root:
        print(
            "Usage: kg sovereign bootstrap <directory> [--pattern GLOB] [--dry-run]",
            file=sys.stderr,
        )
        return 1

    # Verify directory exists
    root_path = Path(root)
    if not root_path.exists():
        print(f"Error: Directory not found: {root}", file=sys.stderr)
        return 1
    if not root_path.is_dir():
        print(f"Error: Not a directory: {root}", file=sys.stderr)
        return 1

    # Route to AGENTESE path
    cmd_kwargs = {
        "root": str(root_path.absolute()),
        "pattern": pattern,
        "dry_run": dry_run,
    }

    return project_command("concept.sovereign.bootstrap", args, ctx, kwargs=cmd_kwargs)


def _handle_ingest(args: list[str], ctx: "InvocationContext | None") -> int:
    """
    Handle ingest command with CLI-side file reading.

    kg sovereign ingest <file> [--source SOURCE]
    """
    # Parse arguments
    file_path = None
    source = "cli"

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--source" and i + 1 < len(args):
            source = args[i + 1]
            i += 2
        elif not arg.startswith("-") and file_path is None:
            file_path = arg
            i += 1
        else:
            i += 1

    if not file_path:
        print("Usage: kg sovereign ingest <file> [--source SOURCE]", file=sys.stderr)
        return 1

    # Read file content
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1

    # Route to AGENTESE path
    # Note: using "claimed_path" to avoid conflict with Logos.invoke's "path" param
    cmd_kwargs = {
        "claimed_path": file_path,
        "content": content,
        "source": source,
    }

    return project_command("concept.sovereign.ingest", args, ctx, kwargs=cmd_kwargs)


def _print_help() -> None:
    """Print help message."""
    help_text = """
Inbound Sovereignty: Possess, don't reference.

Usage:
    kg sovereign                     Show store status
    kg sovereign status              Show store status
    kg sovereign list [PREFIX]       List sovereign entities
    kg sovereign query <PATH>        Query entity with overlay
    kg sovereign ingest <FILE>       Ingest a file
    kg sovereign diff <PATH>         Compare with source file
    kg sovereign bootstrap <DIR>     One-time migration
    kg sovereign sync <PATH>         Sync single file

Examples:
    kg sovereign list spec/                List specs
    kg sovereign query spec/k-block.md     View entity
    kg sovereign ingest README.md          Ingest file
    kg sovereign bootstrap spec/ --dry-run Preview bootstrap

Philosophy:
    "We don't reference. We possess."
    "The file is a lie. There is only the witnessed entity."

See: spec/protocols/inbound-sovereignty.md
"""
    print(help_text.strip())


# === Module Exports ===

__all__ = ["cmd_sovereign"]
