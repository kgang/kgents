"""
Timeline Widget - Horizontal timeline with activity bars.

Groups events by day and shows activity level as sparkline-style bars.
Navigate with cursor to inspect different time periods.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


class Timeline(Widget):
    """
    Horizontal timeline with activity bars.

    Shows temporal activity grouped by day, allowing navigation
    through agent history with cursor controls.
    """

    DEFAULT_CSS = """
    Timeline {
        width: 100%;
        height: 3;
        padding: 0 1;
        color: #d4a574;
    }

    Timeline .cursor {
        color: #f5d08a;
        text-style: bold;
    }
    """

    # Reactive properties
    events: reactive[list[tuple[datetime, float]]] = reactive([])
    cursor_index: reactive[int] = reactive(0)
    num_days: reactive[int] = reactive(7)  # Number of days to show

    def __init__(
        self,
        events: list[tuple[datetime, float]] | None = None,
        cursor_index: int = 0,
        num_days: int = 7,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.events = events or []
        self.cursor_index = cursor_index
        self.num_days = num_days

    def render(self) -> "RenderResult":
        """Render the timeline."""
        if not self.events:
            return "No timeline data"

        # Group events by day
        by_day = self._group_by_day()

        # Get the last N days
        days = list(by_day.keys())[-self.num_days :]

        if not days:
            return "No timeline data"

        # Build output
        header = self._build_header(days)
        bars = self._build_bars(by_day, days)
        cursor = self._build_cursor(len(days))

        return f"{header}\n{bars}\n{cursor}"

    def _group_by_day(self) -> dict[str, list[float]]:
        """Group events by day."""
        by_day: dict[str, list[float]] = {}
        for ts, val in self.events:
            day = ts.strftime("%b %d")
            by_day.setdefault(day, []).append(val)
        return by_day

    def _build_header(self, days: list[str]) -> str:
        """Build the header row with day labels."""
        # Each day gets 8 characters + separator
        parts = []
        for day in days:
            # Center the day label in 8 characters
            centered = day.center(8)
            parts.append(centered)
        return " │ ".join(parts)

    def _build_bars(self, by_day: dict[str, list[float]], days: list[str]) -> str:
        """Build the activity bars row."""
        parts = []
        for day in days:
            values = by_day.get(day, [])
            bar = self._day_bar(values)
            parts.append(bar)
        return " │ ".join(parts)

    def _build_cursor(self, num_days: int) -> str:
        """Build the cursor row."""
        # Each day is 8 chars + 3 for separator (except last)
        # Position cursor under the selected day
        if self.cursor_index >= num_days:
            self.cursor_index = num_days - 1

        # Calculate cursor position
        # Each column is 8 chars wide + " │ " (3 chars) between
        cursor_pos = self.cursor_index * 11 + 4  # Center of first column at 4

        # Build cursor line
        spaces = " " * cursor_pos
        return f"{spaces}▲"

    def _day_bar(self, values: list[float]) -> str:
        """
        Generate bar for one day.

        Args:
            values: Activity values for the day (0.0 to 1.0)

        Returns:
            8-character bar using block characters
        """
        if not values:
            return "▁" * 8

        # Calculate average activity for the day
        avg = sum(values) / len(values)

        # Map to block characters
        chars = "▁▂▃▄▅▆▇█"
        idx = int(avg * (len(chars) - 1))
        idx = max(0, min(len(chars) - 1, idx))

        return chars[idx] * 8

    def watch_events(self, new_events: list[tuple[datetime, float]]) -> None:
        """React to event changes."""
        self.refresh()

    def watch_cursor_index(self, new_index: int) -> None:
        """React to cursor changes."""
        self.refresh()

    def watch_num_days(self, new_days: int) -> None:
        """React to num_days changes."""
        self.refresh()

    def move_cursor_left(self) -> None:
        """Move cursor to the left (earlier day)."""
        if self.cursor_index > 0:
            self.cursor_index -= 1

    def move_cursor_right(self) -> None:
        """Move cursor to the right (later day)."""
        # Calculate max cursor position based on available days
        by_day = self._group_by_day()
        days = list(by_day.keys())[-self.num_days :]
        max_index = len(days) - 1

        if self.cursor_index < max_index:
            self.cursor_index += 1

    def add_event(self, timestamp: datetime, value: float) -> None:
        """
        Add an event to the timeline.

        Args:
            timestamp: When the event occurred
            value: Activity level (0.0 to 1.0)
        """
        self.events = self.events + [(timestamp, value)]
