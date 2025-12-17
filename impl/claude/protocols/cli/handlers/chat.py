"""
Chat Handler: Session management CLI interface.

Routes chat commands to appropriate subcommands:
- kg chat sessions     # List saved sessions
- kg chat resume <id>  # Resume a session
- kg chat search <q>   # Search sessions
- kg chat delete <id>  # Delete a session

Note: Interactive chat is accessed via:
- kg soul chat         # Chat with K-gent
- kg town chat <name>  # Chat with citizen
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from protocols.cli.commands.chat import SESSION_COMMANDS, print_help
from protocols.cli.shared import InvocationContext

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext as ReflectorContext


def cmd_chat(args: list[str], ctx: "ReflectorContext | None" = None) -> int:
    """
    Chat session management commands.

    kgents chat - Manage persistent chat sessions.

    Reflector Integration:
    - If ctx is provided, outputs via dual-channel (human + semantic)
    """
    # Get context from hollow.py if not provided
    if ctx is None:
        try:
            from protocols.cli.hollow import get_invocation_context

            ctx = get_invocation_context("chat", args)
        except ImportError:
            pass

    # Parse args
    if "--help" in args or "-h" in args:
        print_help()
        return 0

    # Create unified context
    invocation_ctx = InvocationContext.from_args(args, reflector_ctx=ctx)

    # Get subcommand
    subcommand = None
    remaining_args: list[str] = []

    for arg in args:
        if arg.startswith("-"):
            continue
        if subcommand is None and arg.lower() in SESSION_COMMANDS:
            subcommand = arg.lower()
        else:
            remaining_args.append(arg)

    # If no subcommand, default to sessions
    if subcommand is None:
        subcommand = "sessions"

    # Run async router
    return asyncio.run(_async_route(subcommand, remaining_args, invocation_ctx, args))


async def _async_route(
    subcommand: str,
    remaining_args: list[str],
    ctx: InvocationContext,
    args: list[str],
) -> int:
    """Route to the appropriate subcommand handler."""
    from protocols.cli.shared import OutputFormatter

    # Parse common options
    node_path = None
    limit = 10

    for i, arg in enumerate(args):
        if arg == "--node" and i + 1 < len(args):
            node_path = args[i + 1]
        elif arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass

    try:
        match subcommand:
            case "sessions" | "list":
                from protocols.cli.commands.chat.sessions import execute_sessions

                return await execute_sessions(
                    ctx,
                    node_path=node_path,
                    limit=limit,
                )

            case "resume":
                from protocols.cli.commands.chat.resume import execute_resume

                identifier = remaining_args[0] if remaining_args else None
                return await execute_resume(ctx, identifier)

            case "search":
                from protocols.cli.commands.chat.search import execute_search

                query = " ".join(remaining_args) if remaining_args else None
                return await execute_search(ctx, query, limit=limit)

            case "delete":
                return await _execute_delete(ctx, remaining_args)

            case _:
                output = OutputFormatter(ctx)
                output.emit_error(f"Unknown subcommand: {subcommand}")
                output.emit("")
                output.emit("Valid subcommands: sessions, resume, search, delete")
                return 1

    except ImportError as e:
        print(f"[CHAT] X Required module not available: {e}")
        return 1
    except Exception as e:
        print(f"[CHAT] X Error: {e}")
        return 1


async def _execute_delete(
    ctx: InvocationContext,
    remaining_args: list[str],
) -> int:
    """Execute 'kg chat delete <id>' - delete a session."""
    from protocols.agentese.chat import get_persistence
    from protocols.cli.shared import OutputFormatter

    output = OutputFormatter(ctx)

    if not remaining_args:
        output.emit_error("Please specify a session ID to delete.")
        output.emit("")
        output.emit("Usage: kg chat delete <id>")
        return 1

    session_id = remaining_args[0]

    try:
        persistence = get_persistence()

        # Try to find session by name first
        session = await persistence.load_by_name(session_id)
        if session:
            session_id = session.session_id

        # Delete
        deleted = await persistence.delete_session(session_id)

        if deleted:
            output.emit(f"Deleted session: {session_id}")
            return 0
        else:
            output.emit_error(f"Session not found: {session_id}")
            return 1

    except Exception as e:
        output.emit_error(f"Failed to delete session: {e}")
        return 1


__all__ = ["cmd_chat"]
