"""
CrystalListPane: Navigable list of crystals with level filtering.

Applies ZenPortal patterns:
- Pattern 4: Vim Navigation (j/k as primary)
- Pattern 6: Elastic Width Truncation
- Pattern 7: Status Glyphs (▪ active, ▫ inactive)
- Pattern 14: Human-Friendly Age ("3m", "1h", "2d")
- Pattern 18: SelectablePane Base

See: docs/skills/zenportal-patterns.md
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

if TYPE_CHECKING:
    from ..crystal import Crystal, CrystalLevel


# Level colors (consistent across TUI)
LEVEL_COLORS = {
    0: "blue",  # SESSION
    1: "green",  # DAY
    2: "yellow",  # WEEK
    3: "magenta",  # EPOCH
}

LEVEL_NAMES = {
    0: "SESSION",
    1: "DAY",
    2: "WEEK",
    3: "EPOCH",
}


def format_age(dt: datetime) -> str:
    """
    Format datetime as human-friendly age.

    Pattern 14: "3m", "1h", "2d" format.
    """
    now = datetime.now()

    # Handle timezone-aware datetimes
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)

    age = now - dt

    if age < timedelta(minutes=1):
        return "now"
    elif age < timedelta(hours=1):
        return f"{int(age.seconds / 60)}m"
    elif age < timedelta(days=1):
        return f"{int(age.seconds / 3600)}h"
    elif age < timedelta(days=7):
        return f"{age.days}d"
    else:
        return f"{age.days // 7}w"


class CrystalListPane(Widget, can_focus=True):
    """
    Navigable list of crystals with vim-style navigation.

    Displays crystals with:
    - Status glyph (▪ selected, ▫ unselected)
    - Level indicator [SESSION/DAY/WEEK/EPOCH]
    - Truncated insight
    - Age, source count, and confidence

    Example row:
        ▪ [SESSION] Completed extinction audit
                    3m ago • 12 marks • 95%
    """

    # Reactive state
    selected_index: reactive[int] = reactive(0)
    is_active: reactive[bool] = reactive(False)

    class CrystalSelected(Message):
        """Message sent when a crystal is selected."""

        def __init__(self, crystal: Any) -> None:
            self.crystal = crystal
            super().__init__()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the crystal list pane."""
        super().__init__(**kwargs)
        self._crystals: list[Any] = []

    def set_crystals(self, crystals: list[Any]) -> None:
        """Set the crystals to display."""
        self._crystals = crystals
        self.selected_index = 0 if crystals else 0
        self.refresh()

    @property
    def selected_crystal(self) -> Any | None:
        """Get the currently selected crystal."""
        if 0 <= self.selected_index < len(self._crystals):
            return self._crystals[self.selected_index]
        return None

    def select_next(self) -> None:
        """Select the next crystal."""
        if self._crystals:
            self.selected_index = min(len(self._crystals) - 1, self.selected_index + 1)
            if self.selected_crystal:
                self.post_message(self.CrystalSelected(self.selected_crystal))

    def select_previous(self) -> None:
        """Select the previous crystal."""
        if self._crystals:
            self.selected_index = max(0, self.selected_index - 1)
            if self.selected_crystal:
                self.post_message(self.CrystalSelected(self.selected_crystal))

    def render(self) -> Text:
        """Render the crystal list."""
        if not self._crystals:
            return Text(
                "No crystals found.\n\nUse 'kg witness crystallize' to create one.", style="dim"
            )

        lines: list[Text] = []
        available_width = self.size.width - 4  # Account for padding

        for i, crystal in enumerate(self._crystals[:20]):  # Limit display
            is_selected = i == self.selected_index

            # Status glyph (Pattern 7)
            glyph = "▪" if is_selected else "▫"
            glyph_style = "bold" if is_selected else "dim"

            # Level indicator
            level_val = crystal.level.value if hasattr(crystal.level, "value") else crystal.level
            level_name = LEVEL_NAMES.get(level_val, "?")
            level_color = LEVEL_COLORS.get(level_val, "white")

            # Truncate insight based on available width (Pattern 6)
            insight = crystal.insight
            max_insight_len = max(20, available_width - 15)  # Leave room for level indicator
            if len(insight) > max_insight_len:
                insight = insight[: max_insight_len - 3] + "..."

            # Format age (Pattern 14)
            age = format_age(crystal.crystallized_at)

            # Format source count
            source_count = crystal.source_count
            source_type = "marks" if crystal.level.value == 0 else "crystals"

            # Format confidence
            confidence = crystal.confidence
            conf_style = "green" if confidence >= 0.8 else "yellow" if confidence >= 0.5 else "red"

            # Build the line
            line = Text()
            line.append(glyph, style=glyph_style)
            line.append(" ")
            line.append(f"[{level_name}]", style=level_color)
            line.append(" ")
            line.append(insight, style="bold" if is_selected else "")
            lines.append(line)

            # Second line: metadata
            meta_line = Text()
            meta_line.append("           ", style="dim")  # Indent
            meta_line.append(f"{age} ago", style="dim")
            meta_line.append(" • ", style="dim")
            meta_line.append(f"{source_count} {source_type}", style="cyan")
            meta_line.append(" • ", style="dim")
            meta_line.append(f"{confidence:.0%}", style=conf_style)
            lines.append(meta_line)

            # Add spacing between items
            lines.append(Text(""))

        # Join all lines
        result = Text()
        for line in lines:
            result.append(line)
            result.append("\n")

        return result

    def watch_selected_index(self, index: int) -> None:
        """Refresh when selection changes."""
        self.refresh()


__all__ = [
    "CrystalListPane",
    "format_age",
    "LEVEL_COLORS",
    "LEVEL_NAMES",
]
