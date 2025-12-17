"""
Chat Search: Search chat sessions by content.

Provides the kg chat search command for finding sessions.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.shared import InvocationContext


async def execute_search(
    ctx: "InvocationContext",
    query: str | None,
    *,
    limit: int = 10,
) -> int:
    """
    Execute 'kg chat search <query>' - search session content.

    Searches in:
    - Session names
    - Session tags
    - User messages
    - Assistant responses
    - Session summaries

    Args:
        ctx: CLI invocation context
        query: Search query string
        limit: Maximum results

    Returns:
        Exit code (0 for success)
    """
    from protocols.agentese.chat import get_persistence
    from protocols.cli.shared import OutputFormatter

    output = OutputFormatter(ctx)

    if not query:
        output.emit_error("Please provide a search query.")
        output.emit("")
        output.emit("Usage: kg chat search <query>")
        output.emit("")
        output.emit("Examples:")
        output.emit("  kg chat search 'authentication'")
        output.emit("  kg chat search 'how to'")
        return 1

    try:
        persistence = get_persistence()
        sessions = await persistence.search_sessions(query, limit=limit)

        if ctx.json_mode:
            data = {
                "query": query,
                "results": [s.to_dict() for s in sessions],
                "count": len(sessions),
            }
            output.emit(json.dumps(data, indent=2, default=str))
            return 0

        # Human-readable output
        if not sessions:
            output.emit(f"No sessions found matching '{query}'")
            return 0

        output.emit(f"Search Results for '{query}' ({len(sessions)} found)")
        output.emit("=" * 60)
        output.emit("")

        for session in sessions:
            name = session.name or session.session_id[:12]
            node = session.node_path
            turns = session.turn_count

            output.emit(f"{name}")
            output.emit(f"   {node} | {turns} turns")

            # Show matching context
            matching_lines = _find_matching_context(session, query)
            for line in matching_lines[:2]:  # Show at most 2 matches
                output.emit(f"   ... {line}")

            output.emit("")

        output.emit("-" * 60)
        output.emit("Resume a session: kg chat resume <name>")

        return 0

    except Exception as e:
        output.emit_error(f"Search failed: {e}")
        return 1


def _find_matching_context(session: "PersistedSession", query: str) -> list[str]:
    """Find lines containing the query for context display."""
    query_lower = query.lower()
    matches: list[str] = []

    # Check name
    if session.name and query_lower in session.name.lower():
        matches.append(f"[name] {session.name}")

    # Check summary
    if session.summary and query_lower in session.summary.lower():
        excerpt = _excerpt_around(session.summary, query)
        matches.append(f"[summary] {excerpt}")

    # Check turns
    for turn in session.turns:
        user_msg = turn.get("user_message", "")
        if query_lower in user_msg.lower():
            excerpt = _excerpt_around(user_msg, query)
            matches.append(f"[you] {excerpt}")

        assistant_msg = turn.get("assistant_response", "")
        if query_lower in assistant_msg.lower():
            excerpt = _excerpt_around(assistant_msg, query)
            matches.append(f"[ai] {excerpt}")

    return matches


def _excerpt_around(text: str, query: str, context_chars: int = 40) -> str:
    """Extract excerpt around the query match."""
    query_lower = query.lower()
    text_lower = text.lower()

    idx = text_lower.find(query_lower)
    if idx == -1:
        return text[:80] + "..." if len(text) > 80 else text

    # Get context around match
    start = max(0, idx - context_chars)
    end = min(len(text), idx + len(query) + context_chars)

    excerpt = text[start:end]

    # Add ellipsis if truncated
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt = excerpt + "..."

    return excerpt


__all__ = ["execute_search"]
