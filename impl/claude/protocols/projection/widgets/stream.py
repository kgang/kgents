"""
StreamWidget: Streaming text display.

Displays text that arrives incrementally, with optional cursor
and chunk delimiting.

Example:
    widget = StreamWidget(StreamWidgetState(
        chunks=("Hello ", "world", "!"),
        complete=False,
        cursor_visible=True
    ))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget


@dataclass(frozen=True)
class StreamWidgetState:
    """
    Immutable stream widget state.

    Attributes:
        chunks: Received text chunks
        complete: Whether stream is complete
        cursor_visible: Show blinking cursor at end
        chunk_delimiter: Delimiter between chunks
        max_chunks: Maximum chunks to retain
    """

    chunks: tuple[str, ...] = ()
    complete: bool = False
    cursor_visible: bool = True
    chunk_delimiter: str = ""
    max_chunks: int = 1000

    @property
    def content(self) -> str:
        """Get full content as single string."""
        return self.chunk_delimiter.join(self.chunks)

    def push_chunk(self, chunk: str) -> StreamWidgetState:
        """Return new state with added chunk."""
        new_chunks = (*self.chunks, chunk)
        # Trim if over max
        if len(new_chunks) > self.max_chunks:
            new_chunks = new_chunks[-self.max_chunks :]
        return StreamWidgetState(
            chunks=new_chunks,
            complete=self.complete,
            cursor_visible=self.cursor_visible,
            chunk_delimiter=self.chunk_delimiter,
            max_chunks=self.max_chunks,
        )

    def mark_complete(self) -> StreamWidgetState:
        """Return new state marked as complete."""
        return StreamWidgetState(
            chunks=self.chunks,
            complete=True,
            cursor_visible=False,
            chunk_delimiter=self.chunk_delimiter,
            max_chunks=self.max_chunks,
        )


class StreamWidget(KgentsWidget[StreamWidgetState]):
    """
    Streaming text display widget.

    Projections:
        - CLI: Plain text with optional cursor
        - TUI: Rich Text with cursor animation
        - MARIMO: HTML with streaming updates
        - JSON: State dict for API responses
    """

    def __init__(self, state: StreamWidgetState | None = None) -> None:
        self.state = Signal.of(state or StreamWidgetState())

    def project(self, target: RenderTarget) -> Any:
        """Project stream to target surface."""
        match target:
            case RenderTarget.CLI:
                return self._to_cli()
            case RenderTarget.TUI:
                return self._to_tui()
            case RenderTarget.MARIMO:
                return self._to_marimo()
            case RenderTarget.JSON:
                return self._to_json()

    def _to_cli(self) -> str:
        """CLI projection: plain text with cursor."""
        s = self.state.value
        content = s.content

        if s.cursor_visible and not s.complete:
            content += "▌"  # Block cursor

        return content

    def _to_tui(self) -> Any:
        """TUI projection: Rich Text."""
        try:
            from rich.text import Text

            s = self.state.value
            text = Text(s.content)

            if s.cursor_visible and not s.complete:
                text.append("▌", style="blink")

            return text
        except ImportError:
            from rich.text import Text

            return Text(self._to_cli())

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML with streaming class."""
        s = self.state.value
        content = s.content

        # Escape HTML entities
        content = (
            content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )
        # Preserve newlines
        content = content.replace("\n", "<br>")

        cursor_class = (
            "kgents-cursor-visible" if s.cursor_visible and not s.complete else ""
        )
        complete_class = (
            "kgents-stream-complete" if s.complete else "kgents-stream-active"
        )

        cursor_html = ""
        if s.cursor_visible and not s.complete:
            cursor_html = '<span class="kgents-cursor">▌</span>'

        return f"""
        <div class="kgents-stream {complete_class} {cursor_class}">
            <span class="kgents-stream-content">{content}</span>{cursor_html}
        </div>
        <style>
            .kgents-cursor {{
                animation: kgents-blink 1s step-end infinite;
            }}
            @keyframes kgents-blink {{
                50% {{ opacity: 0; }}
            }}
        </style>
        """

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "stream",
            "chunks": list(s.chunks),
            "content": s.content,
            "complete": s.complete,
            "cursorVisible": s.cursor_visible,
            "chunkDelimiter": s.chunk_delimiter,
            "chunkCount": len(s.chunks),
        }


__all__ = ["StreamWidget", "StreamWidgetState"]
