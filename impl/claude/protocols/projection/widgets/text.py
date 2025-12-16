"""
TextWidget: Simple text display with formatting variants.

Supports multiple text variants for semantic rendering:
- body: Regular paragraph text
- heading: Section heading (# in markdown)
- code: Monospace code block
- quote: Block quote (> in markdown)
- label: Small label text

Example:
    widget = TextWidget(TextWidgetState(
        content="Important Message",
        variant="heading"
    ))
    print(widget.to_cli())  # "# Important Message"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

TextVariant = Literal["body", "heading", "code", "quote", "label"]


@dataclass(frozen=True)
class TextWidgetState:
    """
    Immutable text widget state.

    Attributes:
        content: The text content to display
        variant: Semantic variant for styling
        truncate: Max characters before truncation (None = no truncation)
        highlight: Start/end positions to highlight (None = no highlight)
    """

    content: str
    variant: TextVariant = "body"
    truncate: int | None = None
    highlight: tuple[int, int] | None = None

    @property
    def display_content(self) -> str:
        """Get content with truncation applied."""
        if self.truncate is None or len(self.content) <= self.truncate:
            return self.content
        return self.content[: self.truncate - 3] + "..."


class TextWidget(KgentsWidget[TextWidgetState]):
    """
    Text display widget with formatting variants.

    Projections:
        - CLI: Plain text with markdown-style formatting
        - TUI: Rich Text with styling
        - MARIMO: HTML with CSS classes
        - JSON: State dict for API responses
    """

    def __init__(self, state: TextWidgetState | None = None) -> None:
        self.state = Signal.of(state or TextWidgetState(content=""))

    def project(self, target: RenderTarget) -> Any:
        """Project text to target surface."""
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
        """CLI projection: markdown-style formatting."""
        s = self.state.value
        content = s.display_content

        match s.variant:
            case "heading":
                return f"# {content}"
            case "code":
                return f"```\n{content}\n```"
            case "quote":
                lines = content.split("\n")
                return "\n".join(f"> {line}" for line in lines)
            case "label":
                return f"[{content}]"
            case _:  # body
                return content

    def _to_tui(self) -> Any:
        """TUI projection: Rich Text with styling."""
        try:
            from rich.text import Text

            s = self.state.value
            content = s.display_content

            style_map = {
                "body": "",
                "heading": "bold",
                "code": "dim",
                "quote": "italic",
                "label": "dim",
            }
            style = style_map.get(s.variant, "")

            text = Text(content, style=style)

            # Apply highlight if specified
            if s.highlight:
                start, end = s.highlight
                text.stylize("reverse", start, end)

            return text
        except ImportError:
            return self._to_cli()

    def _to_marimo(self) -> str:
        """MARIMO projection: HTML with CSS classes."""
        s = self.state.value
        content = s.display_content

        # Escape HTML entities
        content = (
            content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        class_map = {
            "body": "kgents-text-body",
            "heading": "kgents-text-heading",
            "code": "kgents-text-code",
            "quote": "kgents-text-quote",
            "label": "kgents-text-label",
        }
        css_class = class_map.get(s.variant, "kgents-text-body")

        tag_map = {
            "body": "p",
            "heading": "h2",
            "code": "pre",
            "quote": "blockquote",
            "label": "span",
        }
        tag = tag_map.get(s.variant, "p")

        # Apply highlight if specified
        if s.highlight:
            start, end = s.highlight
            content = (
                content[:start]
                + f'<mark class="kgents-highlight">{content[start:end]}</mark>'
                + content[end:]
            )

        return f'<{tag} class="{css_class}">{content}</{tag}>'

    def _to_json(self) -> dict[str, Any]:
        """JSON projection: state dict for API responses."""
        s = self.state.value
        return {
            "type": "text",
            "content": s.content,
            "displayContent": s.display_content,
            "variant": s.variant,
            "truncate": s.truncate,
            "highlight": list(s.highlight) if s.highlight else None,
        }


__all__ = ["TextWidget", "TextWidgetState", "TextVariant"]
