"""
Chat Sessions: List and manage saved chat sessions.

Provides the kg chat sessions command for browsing persisted sessions.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.shared import InvocationContext


async def execute_sessions(
    ctx: "InvocationContext",
    *,
    node_path: str | None = None,
    limit: int = 10,
) -> int:
    """
    Execute 'kg chat sessions' - list saved chat sessions.

    Args:
        ctx: CLI invocation context
        node_path: Optional filter by AGENTESE path
        limit: Maximum sessions to return

    Returns:
        Exit code (0 for success)
    """
    from protocols.agentese.chat import get_persistence
    from protocols.cli.shared import OutputFormatter

    output = OutputFormatter(ctx)

    try:
        persistence = get_persistence()
        sessions = await persistence.list_sessions(
            node_path=node_path,
            limit=limit,
        )

        # Sort by updated_at descending (most recent first)
        sessions.sort(key=lambda s: s.updated_at, reverse=True)

        if ctx.json_mode:
            # JSON output
            data = {
                "sessions": [s.to_dict() for s in sessions],
                "count": len(sessions),
                "filter": {"node_path": node_path, "limit": limit},
            }
            output.emit(json.dumps(data, indent=2, default=str))
            return 0

        # Human-readable output
        if not sessions:
            output.emit("No saved chat sessions found.")
            if node_path:
                output.emit(f"  Filter: node_path={node_path}")
            output.emit("")
            output.emit("Start a chat with:")
            output.emit("  kg soul chat           # Chat with K-gent")
            output.emit("  kg town chat <citizen> # Chat with citizen")
            return 0

        # Header
        output.emit(f"Saved Chat Sessions ({len(sessions)})")
        output.emit("=" * 60)
        output.emit("")

        for session in sessions:
            # Format session display
            name_display = session.name or session.session_id[:12]
            age = _format_age(session.updated_at)
            turns = session.turn_count
            state_emoji = _state_emoji(session.state)

            # Line 1: Name and state
            output.emit(f"{state_emoji} {name_display}")

            # Line 2: Details
            details = []
            details.append(f"Path: {session.node_path}")
            details.append(f"Turns: {turns}")
            details.append(f"Updated: {age}")

            if session.tags:
                details.append(f"Tags: {', '.join(session.tags)}")

            output.emit(f"   {' | '.join(details)}")

            # Line 3: Preview (first message if available)
            if session.turns:
                first_turn = session.turns[0]
                user_msg = first_turn.get("user_message", "")
                preview = user_msg[:60] + "..." if len(user_msg) > 60 else user_msg
                output.emit(f"   > \"{preview}\"")

            output.emit("")

        # Footer
        output.emit("-" * 60)
        output.emit(f"Resume a session: kg chat resume <name|id>")

        return 0

    except Exception as e:
        output.emit_error(f"Failed to list sessions: {e}")
        return 1


def _format_age(dt: datetime) -> str:
    """Format datetime as relative age (e.g., '2 hours ago')."""
    now = datetime.now()
    delta = now - dt

    seconds = delta.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours}h ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days}d ago"
    else:
        weeks = int(seconds // 604800)
        return f"{weeks}w ago"


def _state_emoji(state: str) -> str:
    """Get emoji for session state."""
    return {
        "waiting": "💬",
        "streaming": "📡",
        "collapsed": "💤",
        "ready": "🟢",
        "dormant": "⚪",
        "draining": "🔄",
    }.get(state, "❓")


__all__ = ["execute_sessions"]
