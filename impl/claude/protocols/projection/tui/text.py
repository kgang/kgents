"""
TUI Text Widget: Text display with variants.

Supports plain, code, heading, quote, and markdown variants.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from protocols.projection.schema import WidgetMeta
from protocols.projection.tui.base import TUIWidget
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from textual.widgets import Static


@dataclass(frozen=True)
class TextState:
    """State for text widget."""

    content: str
    variant: Literal["plain", "code", "heading", "quote", "markdown"] = "plain"
    truncate_lines: int = 0
    highlight: str | None = None
    language: str = "python"  # For code variant


class TUITextWidget(TUIWidget[TextState]):
    """
    TUI text display widget.

    Renders text with Rich formatting based on variant.
    """

    DEFAULT_CSS = """
    TUITextWidget {
        height: auto;
        width: 100%;
        margin: 1 0;
    }
    """

    def render_content(self) -> RenderableType:
        """Render text content based on variant."""
        if self.state is None:
            return Text("(empty)")

        content = self.state.content

        # Apply truncation
        if self.state.truncate_lines > 0:
            lines = content.split("\n")
            if len(lines) > self.state.truncate_lines:
                content = "\n".join(lines[: self.state.truncate_lines]) + "\n..."

        match self.state.variant:
            case "code":
                return Syntax(
                    content,
                    self.state.language,
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True,
                )
            case "heading":
                text = Text(content, style="bold cyan")
                text.stylize("underline")
                return text
            case "quote":
                return Panel(
                    Text(content, style="italic dim"),
                    border_style="dim",
                    padding=(0, 1),
                )
            case "markdown":
                return Markdown(content)
            case "plain" | _:
                text = Text(content)
                # Apply highlight if specified
                if self.state.highlight:
                    text.highlight_regex(self.state.highlight, style="bold yellow")
                return text

    def render(self) -> RenderableType:
        """Render the widget."""
        return self.render_content()


class TUITextStatic(Static):
    """
    Simple static text widget for quick text rendering.

    Use this when you don't need full TUIWidget features.
    """

    def __init__(
        self,
        content: str,
        variant: Literal["plain", "code", "heading", "quote", "markdown"] = "plain",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._content = content
        self._variant = variant

    def render(self) -> RenderableType:
        match self._variant:
            case "code":
                return Syntax(self._content, "python", theme="monokai")
            case "heading":
                return Text(self._content, style="bold cyan underline")
            case "quote":
                return Panel(
                    Text(self._content, style="italic dim"),
                    border_style="dim",
                )
            case "markdown":
                return Markdown(self._content)
            case _:
                return Text(self._content)
