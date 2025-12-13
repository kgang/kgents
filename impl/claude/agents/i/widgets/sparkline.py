"""
Sparkline Widget - Inline sparkline visualization.

Renders time-series data as a single-line bar chart using block characters.
Uses "▁▂▃▄▅▆▇█" for visual density.

Usage:
    sparkline = Sparkline(values=[1, 2, 3, 4, 5], width=20)

The sparkline is reactive - updating values automatically refreshes the display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult


def generate_sparkline(values: list[float], width: int = 20) -> str:
    """
    Generate a sparkline string from values.

    Args:
        values: Time series data (can be any numeric values)
        width: Character width of the sparkline

    Returns:
        Sparkline string using "▁▂▃▄▅▆▇█" characters

    Examples:
        >>> generate_sparkline([1, 2, 3, 4, 5], width=5)
        '▁▂▃▆█'

        >>> generate_sparkline([], width=5)
        '▁▁▁▁▁'

        >>> generate_sparkline([5.0], width=5)
        '▁▁▁▁▁'
    """
    # If no values, return baseline
    if not values:
        return "▁" * width

    # Take last `width` values
    values = values[-width:]

    # Pad if we have fewer values than width
    if len(values) < width:
        padding = "▁" * (width - len(values))
        # Continue with what we have
    else:
        padding = ""

    # Find range
    min_v = min(values)
    max_v = max(values)
    range_v = max_v - min_v if max_v > min_v else 1

    # Map to sparkline characters
    chars = "▁▂▃▄▅▆▇█"
    result = []

    for v in values:
        # Normalize to 0-1
        normalized = (v - min_v) / range_v
        # Map to character index
        idx = int(normalized * (len(chars) - 1))
        idx = max(0, min(len(chars) - 1, idx))
        result.append(chars[idx])

    return padding + "".join(result)


class Sparkline(Widget):
    """
    Sparkline widget - renders time series as inline bar chart.

    Attributes:
        values: List of numeric values to display
        width: Character width of the sparkline
    """

    DEFAULT_CSS = """
    Sparkline {
        width: auto;
        height: 1;
        color: #b3a89a;
    }

    Sparkline.active {
        color: #e6a352;
    }

    Sparkline.idle {
        color: #6a6560;
    }
    """

    values: reactive[list[float]] = reactive(list, init=False)
    width: reactive[int] = reactive(20)

    def __init__(
        self,
        values: list[float] | None = None,
        width: int = 20,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize sparkline widget.

        Args:
            values: Initial values to display
            width: Character width
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.values = values if values is not None else []
        self.width = width

    def render(self) -> "RenderResult":
        """Render the sparkline."""
        return generate_sparkline(self.values, self.width)

    def watch_values(self, new_values: list[float]) -> None:
        """React to value changes."""
        self.refresh()

    def watch_width(self, new_width: int) -> None:
        """React to width changes."""
        self.refresh()

    def add_value(self, value: float) -> None:
        """
        Add a new value to the sparkline.

        The sparkline will automatically trim to width.

        Args:
            value: New value to add
        """
        self.values = self.values + [value]

    def set_values(self, values: list[float]) -> None:
        """
        Replace all values.

        Args:
            values: New value list
        """
        self.values = values


# Export public API
__all__ = ["Sparkline", "generate_sparkline"]
