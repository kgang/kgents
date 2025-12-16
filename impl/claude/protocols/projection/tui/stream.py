"""
TUI Stream Widget: Streaming text display with cursor.

Shows streaming content with blinking cursor and auto-scroll.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from protocols.projection.tui.base import TUIWidget
from rich.console import RenderableType
from rich.text import Text
from textual.widgets import Static


@dataclass(frozen=True)
class StreamState:
    """State for stream widget."""

    chunks: tuple[str, ...] = field(default_factory=tuple)
    complete: bool = False
    cursor_visible: bool = True


class TUIStreamWidget(TUIWidget[StreamState]):
    """
    TUI streaming text widget.

    Renders streaming content with cursor animation.
    """

    DEFAULT_CSS = """
    TUIStreamWidget {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def render_content(self) -> RenderableType:
        """Render stream content."""
        if self.state is None:
            return Text("")

        content = "".join(self.state.chunks)
        text = Text(content)

        # Add cursor if streaming
        if not self.state.complete and self.state.cursor_visible:
            text.append("▋", style="bold blink blue")

        # Add complete marker
        if self.state.complete:
            text.append(" ✓", style="bold green")

        return text

    def render(self) -> RenderableType:
        """Render the widget."""
        return self.render_content()


class TUIStreamingText(Static):
    """
    Simple streaming text for quick rendering.

    Use this when you don't need full TUIWidget features.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._chunks: list[str] = []
        self._complete = False

    def append_chunk(self, chunk: str) -> None:
        """Append a chunk to the stream."""
        self._chunks.append(chunk)
        self.refresh()

    def mark_complete(self) -> None:
        """Mark stream as complete."""
        self._complete = True
        self.refresh()

    def clear(self) -> None:
        """Clear all chunks."""
        self._chunks = []
        self._complete = False
        self.refresh()

    def get_content(self) -> str:
        """Get accumulated content."""
        return "".join(self._chunks)

    def render(self) -> RenderableType:
        text = Text(self.get_content())

        if not self._complete:
            text.append("▋", style="bold blink blue")
        else:
            text.append(" ✓", style="bold green")

        return text
