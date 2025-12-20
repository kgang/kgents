"""
Turn: The atomic unit of conversation, projectable to any target.

A Turn is a moment of dialogue—a single speaker saying something at a point
in time. The key insight is that the same Turn renders differently for
different targets (CLI, TUI, JSON, marimo), but the underlying data is one.

This is the holographic principle: from one Turn, all views derive.

AGENTESE Integration:
    time.conversation.witness → [Turn, Turn, ...]
    time.conversation.project(target="cli") → formatted string
    time.conversation.project(target="json") → JSON dict

Category Theory: Turn is a product type with projection morphisms.
Each projector (to_cli, to_tui, etc.) is a natural transformation
from Turn to the target rendering category.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Mapping

if TYPE_CHECKING:
    pass

# Optional imports for rich rendering
try:
    from rich.text import Text as RichText
except ImportError:
    RichText = None  # type: ignore[assignment, misc]


@dataclass(frozen=True)
class Turn:
    """
    A moment of dialogue, projectable to any target.

    The Turn is immutable (frozen) because dialogue history is immutable.
    Once spoken, a turn cannot be unsaid—only new turns can be added.

    Attributes:
        speaker: Who is speaking (e.g., "user", "assistant", "kgent", "system")
        content: The message content (text)
        timestamp: Unix timestamp (seconds since epoch)
        meta: Optional metadata (tool calls, citations, etc.)

    Example:
        turn = Turn(
            speaker="kgent",
            content="Hello! How can I help you today?",
            timestamp=1734200000.0,
            meta={"confidence": 0.95}
        )

        # Render to CLI
        print(turn.to_cli())
        # Output: [kgent]: Hello! How can I help you today?

        # Render to JSON
        data = turn.to_json()
        # Output: {"speaker": "kgent", "content": "...", ...}
    """

    speaker: str
    content: str
    timestamp: float
    meta: Mapping[str, Any] = field(default_factory=dict)

    def to_cli(self) -> str:
        """
        Project Turn to CLI format (plain text).

        Format: [speaker]: content

        Returns:
            Plain text string suitable for terminal output
        """
        return f"[{self.speaker}]: {self.content}"

    def to_tui(self) -> Any:
        """
        Project Turn to TUI format (Rich Text).

        Returns styled Rich Text object with:
        - Speaker in bold
        - Content in normal weight
        - Role-based coloring

        Returns:
            rich.text.Text object (or plain string if Rich not available)
        """
        if RichText is None:
            # Fallback if Rich not installed
            return self.to_cli()

        # Color mapping by speaker role
        speaker_colors = {
            "user": "cyan",
            "assistant": "green",
            "kgent": "magenta",
            "system": "yellow",
        }
        color = speaker_colors.get(self.speaker.lower(), "white")

        text = RichText()
        text.append(f"[{self.speaker}]", style=f"bold {color}")
        text.append(": ")
        text.append(self.content)
        return text

    def to_json(self) -> dict[str, Any]:
        """
        Project Turn to JSON-serializable dict.

        Suitable for:
        - API responses
        - Logging
        - Storage
        - Wire format

        Returns:
            Dict with all Turn fields
        """
        return {
            "speaker": self.speaker,
            "content": self.content,
            "timestamp": self.timestamp,
            "meta": dict(self.meta),
        }

    def to_json_str(self) -> str:
        """
        Project Turn to JSON string.

        Convenience method for direct serialization.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_json())

    def to_marimo(self) -> str:
        """
        Project Turn to marimo HTML format.

        Returns HTML string suitable for mo.Html() rendering.
        Uses semantic HTML with inline styles for conversation bubbles.

        Returns:
            HTML string for marimo notebook display
        """
        # Speaker-based styling
        speaker_styles = {
            "user": "background: #e3f2fd; border-left: 3px solid #2196f3;",
            "assistant": "background: #e8f5e9; border-left: 3px solid #4caf50;",
            "kgent": "background: #f3e5f5; border-left: 3px solid #9c27b0;",
            "system": "background: #fff8e1; border-left: 3px solid #ffc107;",
        }
        style = speaker_styles.get(self.speaker.lower(), "background: #f5f5f5;")

        return f"""
        <div style="{style} padding: 8px 12px; margin: 4px 0; border-radius: 4px;">
            <strong style="color: #333;">{self.speaker}</strong>
            <p style="margin: 4px 0 0 0; color: #666;">{self.content}</p>
        </div>
        """

    def to_sse(self) -> str:
        """
        Project Turn to Server-Sent Events format.

        Format follows SSE specification:
            data: {json}

        Returns:
            SSE-formatted string
        """
        return f"data: {self.to_json_str()}\n\n"

    def with_meta(self, **kwargs: Any) -> "Turn":
        """
        Create new Turn with additional metadata.

        Immutable update—returns new Turn, original unchanged.

        Args:
            **kwargs: Key-value pairs to add to meta

        Returns:
            New Turn with merged metadata

        Example:
            turn2 = turn.with_meta(edited=True, reason="typo fix")
        """
        merged_meta = {**self.meta, **kwargs}
        return Turn(
            speaker=self.speaker,
            content=self.content,
            timestamp=self.timestamp,
            meta=merged_meta,
        )

    def summarize(self, max_length: int = 50) -> str:
        """
        Get a shortened summary of the turn.

        Useful for logging, debugging, and compact displays.

        Args:
            max_length: Maximum content length before truncation

        Returns:
            Short string summary
        """
        content_preview = (
            self.content[:max_length] + "..." if len(self.content) > max_length else self.content
        )
        return f"[{self.speaker}]: {content_preview}"


def turns_to_markdown(turns: list[Turn]) -> str:
    """
    Convert a list of Turns to Markdown conversation format.

    Args:
        turns: List of Turn objects

    Returns:
        Markdown-formatted conversation
    """
    lines = []
    for turn in turns:
        lines.append(f"**{turn.speaker}**: {turn.content}")
        lines.append("")  # Blank line between turns
    return "\n".join(lines)


def turns_to_json(turns: list[Turn]) -> list[dict[str, Any]]:
    """
    Convert a list of Turns to JSON-serializable list.

    Args:
        turns: List of Turn objects

    Returns:
        List of dicts
    """
    return [turn.to_json() for turn in turns]
