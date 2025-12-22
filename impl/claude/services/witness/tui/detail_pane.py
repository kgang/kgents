"""
CrystalDetailPane: Right pane showing expanded crystal details.

Displays:
- Full insight text
- Significance
- Topics/principles
- Source count and confidence
- Time range and mood

See: plans/witness-dashboard-tui.md
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from .crystal_list import LEVEL_COLORS, LEVEL_NAMES, format_age

if TYPE_CHECKING:
    from ..crystal import Crystal


class CrystalDetailPane(Widget):
    """
    Right pane showing expanded crystal details.

    Displays the full context for the selected crystal:
    - Insight (full text)
    - Significance
    - Topics and principles
    - Metadata (sources, confidence, time)
    """

    # Reactive state
    crystal: reactive[Any | None] = reactive(None)

    def set_crystal(self, crystal: Any | None) -> None:
        """Set the crystal to display."""
        self.crystal = crystal
        self.refresh()

    def render(self) -> Text:
        """Render the crystal details."""
        if self.crystal is None:
            return Text("Select a crystal to view details.", style="dim")

        c = self.crystal
        lines: list[Text] = []

        # Level indicator
        level_val = c.level.value if hasattr(c.level, "value") else c.level
        level_name = LEVEL_NAMES.get(level_val, "?")
        level_color = LEVEL_COLORS.get(level_val, "white")

        header = Text()
        header.append("─" * 30, style="dim")
        lines.append(header)

        # Insight section
        lines.append(Text("Insight:", style="bold cyan"))
        # Wrap insight text
        insight_text = c.insight or "(No insight)"
        for line in self._wrap_text(insight_text, self.size.width - 4):
            lines.append(Text(f"  {line}"))
        lines.append(Text(""))

        # Significance section (if present)
        if c.significance:
            lines.append(Text("Significance:", style="bold green"))
            for line in self._wrap_text(c.significance, self.size.width - 4):
                lines.append(Text(f"  {line}"))
            lines.append(Text(""))

        # Topics (if present)
        if c.topics:
            lines.append(Text("Topics:", style="bold yellow"))
            topics_text = ", ".join(sorted(c.topics))
            lines.append(Text(f"  {topics_text}", style="dim"))
            lines.append(Text(""))

        # Principles (if present)
        if c.principles:
            lines.append(Text("Principles:", style="bold magenta"))
            principles_text = ", ".join(c.principles)
            lines.append(Text(f"  {principles_text}", style="dim"))
            lines.append(Text(""))

        # Metadata section
        lines.append(Text("─" * 30, style="dim"))

        # Level and time
        meta1 = Text()
        meta1.append("Level: ", style="dim")
        meta1.append(level_name, style=level_color)
        meta1.append("  Age: ", style="dim")
        meta1.append(format_age(c.crystallized_at), style="cyan")
        lines.append(meta1)

        # Sources and confidence
        source_type = "marks" if level_val == 0 else "crystals"
        conf_style = "green" if c.confidence >= 0.8 else "yellow" if c.confidence >= 0.5 else "red"
        meta2 = Text()
        meta2.append("Sources: ", style="dim")
        meta2.append(f"{c.source_count} {source_type}", style="cyan")
        meta2.append("  Confidence: ", style="dim")
        meta2.append(f"{c.confidence:.0%}", style=conf_style)
        lines.append(meta2)

        # Token estimate and compression
        meta3 = Text()
        meta3.append("Tokens: ", style="dim")
        meta3.append(f"~{c.token_estimate}", style="dim")
        if c.compression_ratio > 1:
            meta3.append("  Compression: ", style="dim")
            meta3.append(f"{c.compression_ratio:.0f}:1", style="dim")
        lines.append(meta3)

        # Time range (if present)
        if c.time_range:
            start, end = c.time_range
            duration_min = (end - start).total_seconds() / 60
            meta4 = Text()
            meta4.append("Duration: ", style="dim")
            if duration_min < 60:
                meta4.append(f"{duration_min:.0f} min", style="dim")
            else:
                hours = duration_min / 60
                meta4.append(f"{hours:.1f} hours", style="dim")
            lines.append(meta4)

        # Mood dominant quality
        if c.mood:
            dominant = c.mood.dominant_quality
            meta5 = Text()
            meta5.append("Mood: ", style="dim")
            meta5.append(dominant, style="italic dim")
            lines.append(meta5)

        # Join all lines
        result = Text()
        for text_line in lines:
            result.append(text_line)
            result.append("\n")

        return result

    def _wrap_text(self, text: str, max_width: int) -> list[str]:
        """
        Wrap text to fit within max_width.

        Simple word wrapping implementation.
        """
        if not text:
            return []

        words = text.split()
        lines: list[str] = []
        current_line: list[str] = []
        current_length = 0

        for word in words:
            word_len = len(word)
            if current_length + word_len + 1 <= max_width:
                current_line.append(word)
                current_length += word_len + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_len

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def watch_crystal(self, crystal: Any | None) -> None:
        """Refresh when crystal changes."""
        self.refresh()


__all__ = [
    "CrystalDetailPane",
]
