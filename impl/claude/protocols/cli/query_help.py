"""
Query Help - Enhanced Output for kg ?pattern Queries.

This module provides Rich-formatted output for AGENTESE path queries.
Instead of raw match lists, it shows:
- Path with description
- Category (world/self/concept/void/time)
- Available aspects if it's a node

Usage:
    kg ?self.*      # List all self.* paths
    kg ?*brain*     # Search for brain-related paths
    kg ?world.*.?   # List world nodes and their aspects
"""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.agentese.query import QueryResult

from .help_projector import NODE_EMOJIS, NODE_TITLES, PATH_TO_COMMAND

# === Context Emojis ===

CONTEXT_EMOJIS = {
    "world": "🌍",
    "self": "🔮",
    "concept": "💡",
    "void": "✨",
    "time": "⏰",
}


# === Query Result Formatting ===


@dataclass
class FormattedMatch:
    """A formatted query match."""

    path: str
    description: str
    category: str
    cli_command: str | None
    emoji: str


def format_query_result(result: "QueryResult | Any") -> str:
    """
    Format a query result for terminal display.

    Args:
        result: QueryResult from logos.query() or similar dict

    Returns:
        Formatted string for display
    """
    # Handle dict-like results
    if isinstance(result, dict):
        matches = result.get("matches", [])
        pattern = result.get("pattern", "?")
    elif hasattr(result, "matches"):
        matches = result.matches
        pattern = getattr(result, "pattern", "?")
    else:
        return str(result)

    if not matches:
        return f"No paths match pattern: {pattern}"

    # Format matches
    formatted = [_format_match(m) for m in matches]

    # Render
    try:
        return _render_rich(pattern, formatted)
    except ImportError:
        return _render_plain(pattern, formatted)


def _format_match(match: Any) -> FormattedMatch:
    """Format a single match."""
    # Handle different match types
    if isinstance(match, str):
        path = match
    elif hasattr(match, "path"):
        path = match.path
    elif isinstance(match, dict):
        path = match.get("path", str(match))
    else:
        path = str(match)

    # Derive context
    parts = path.split(".")
    context = parts[0] if parts else "unknown"

    # Get emoji
    emoji = CONTEXT_EMOJIS.get(context, "•")
    if path in NODE_EMOJIS:
        emoji = NODE_EMOJIS[path]

    # Get description
    description = _get_path_description(path)

    # Get CLI command
    cli_command = PATH_TO_COMMAND.get(path)
    if not cli_command and len(parts) >= 2:
        # Try parent path
        parent = ".".join(parts[:2])
        base_cmd = PATH_TO_COMMAND.get(parent)
        if base_cmd and len(parts) > 2:
            cli_command = f"{base_cmd} {parts[-1]}"

    return FormattedMatch(
        path=path,
        description=description,
        category=context,
        cli_command=cli_command,
        emoji=emoji,
    )


def _get_path_description(path: str) -> str:
    """Get description for a path."""
    # Known descriptions
    DESCRIPTIONS = {
        "self.memory": "Holographic memory operations",
        "self.memory.capture": "Capture content to memory",
        "self.memory.recall": "Semantic search for memories",
        "self.memory.manifest": "Brain status overview",
        "self.soul": "Digital consciousness middleware",
        "self.soul.reflect": "K-gent reflection",
        "self.soul.chat": "Dialogue with K-gent",
        "self.forest": "Project health protocol",
        "self.forest.manifest": "Forest health status",
        "self.forest.garden": "Hypnagogia garden",
        "self.forest.tend": "Garden tending operations",
        "world.town": "Agent simulation",
        "world.town.manifest": "Town status",
        "world.town.inhabit": "Become a citizen",
        "world.town.spawn": "Create a citizen",
        "world.park": "Punchdrunk experience",
        "world.atelier": "Collaborative workshops",
        "void.joy": "Oblique strategies",
        "void.joy.oblique": "Draw a strategy card",
        "void.joy.surprise": "Serendipitous prompt",
        "void.memory.surface": "Random memory surfacing",
    }

    if path in DESCRIPTIONS:
        return DESCRIPTIONS[path]

    # Fallback: humanize the last part
    parts = path.split(".")
    if parts:
        return f"{parts[-1].title()} operation"
    return "Unknown"


def _render_rich(pattern: str, matches: list[FormattedMatch]) -> str:
    """Render with Rich formatting."""
    from rich.console import Console
    from rich.table import Table

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=True, width=100)

    # Header
    console.print()
    console.print(f"[bold cyan]Query:[/] {pattern}")
    console.print(f"[dim]Found {len(matches)} matches[/]")
    console.print()

    # Group by context
    by_context: dict[str, list[FormattedMatch]] = {}
    for m in matches:
        by_context.setdefault(m.category, []).append(m)

    # Render each context
    for context, ctx_matches in sorted(by_context.items()):
        emoji = CONTEXT_EMOJIS.get(context, "•")
        console.print(f"[bold magenta]{emoji} {context}.*[/]")

        for m in ctx_matches:
            path_display = m.path
            if m.cli_command:
                console.print(
                    f"  [cyan]{path_display:35}[/] [green]kg {m.cli_command:20}[/] [dim]{m.description}[/]"
                )
            else:
                console.print(f"  [cyan]{path_display:35}[/] [dim]{m.description}[/]")

        console.print()

    # Footer
    console.print("[dim]Tip: Use 'kg <path>' to invoke directly[/]")

    return buffer.getvalue()


def _render_plain(pattern: str, matches: list[FormattedMatch]) -> str:
    """Render as plain text."""
    lines = [
        f"Query: {pattern}",
        f"Found {len(matches)} matches",
        "",
    ]

    # Group by context
    by_context: dict[str, list[FormattedMatch]] = {}
    for m in matches:
        by_context.setdefault(m.category, []).append(m)

    for context, ctx_matches in sorted(by_context.items()):
        lines.append(f"{context}.*")
        for m in ctx_matches:
            if m.cli_command:
                lines.append(f"  {m.path:35} kg {m.cli_command:20} {m.description}")
            else:
                lines.append(f"  {m.path:35} {m.description}")
        lines.append("")

    lines.append("Tip: Use 'kg <path>' to invoke directly")

    return "\n".join(lines)


# === Show Query Help ===


def show_query_help() -> int:
    """
    Show help for the query system.

    Called when user runs `kg ?` with no pattern.
    """
    help_text = """
Query AGENTESE Paths

Usage:
  kg ?<pattern>         Query paths matching pattern

Pattern Syntax:
  kg ?self.*            All paths under self
  kg ?*.memory*         Paths containing 'memory'
  kg ?world.town.?      Aspects of world.town
  kg ?*                 All registered paths

Examples:
  kg ?self.memory.*     List memory operations
  kg ?world.*           List world entities
  kg ?void.*            List entropy/serendipity paths
  kg ?*capture*         Find capture-related paths

Options:
  --limit N             Limit results (default: 100)
  --json                Output as JSON

The query system helps you discover available AGENTESE paths.
Each path can be invoked directly: kg self.memory.capture "content"
"""
    print(help_text.strip())
    return 0


__all__ = [
    "format_query_result",
    "show_query_help",
    "FormattedMatch",
]
