"""
XYZ Health Bar Widget - Displays telemetry/semantic/economic health.

Renders the three O-gent dimensions as compact colored bars:
- X (Telemetry): Red/green gradient - "Is it running?"
- Y (Semantic): Blue/cyan gradient - "Does it mean what it says?"
- Z (Economic): Yellow/gold gradient - "Is it worth the cost?"
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widget import Widget

if TYPE_CHECKING:
    from textual.app import RenderResult

from ..data.ogent import XYZHealth
from ..theme.earth import EARTH_PALETTE

# Characters for health bar rendering
BAR_FULL = "█"
BAR_EMPTY = "░"
BAR_PARTIAL = "▓▒░"


def render_single_bar(
    value: float, width: int, filled_char: str = BAR_FULL, empty_char: str = BAR_EMPTY
) -> str:
    """Render a single health bar."""
    filled = int(value * width)
    empty = width - filled
    return filled_char * filled + empty_char * empty


class XYZHealthBar(Widget):
    """
    Displays XYZ health as three compact bars.

    Layout:
        X ████░░░░░░
        Y ██████░░░░
        Z █████████░
    """

    DEFAULT_CSS = """
    XYZHealthBar {
        width: auto;
        height: 3;
        padding: 0;
    }

    XYZHealthBar .x-bar {
        color: #e88a8a;  /* Salmon pink - telemetry */
    }

    XYZHealthBar .y-bar {
        color: #8ac4e8;  /* Sky blue - semantic */
    }

    XYZHealthBar .z-bar {
        color: #e6a352;  /* Warm amber - economic */
    }
    """

    # Reactive health values
    x_value: reactive[float] = reactive(1.0)
    y_value: reactive[float] = reactive(1.0)
    z_value: reactive[float] = reactive(1.0)

    def __init__(
        self,
        health: XYZHealth | None = None,
        bar_width: int = 8,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.bar_width = bar_width
        if health:
            self.x_value = health.x_telemetry
            self.y_value = health.y_semantic
            self.z_value = health.z_economic

    def update_health(self, health: XYZHealth) -> None:
        """Update the displayed health values."""
        self.x_value = health.x_telemetry
        self.y_value = health.y_semantic
        self.z_value = health.z_economic

    def watch_x_value(self, new_value: float) -> None:
        """React to X value changes."""
        self.refresh()

    def watch_y_value(self, new_value: float) -> None:
        """React to Y value changes."""
        self.refresh()

    def watch_z_value(self, new_value: float) -> None:
        """React to Z value changes."""
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the health bars."""
        x_bar = render_single_bar(self.x_value, self.bar_width)
        y_bar = render_single_bar(self.y_value, self.bar_width)
        z_bar = render_single_bar(self.z_value, self.bar_width)

        return f"X {x_bar}\nY {y_bar}\nZ {z_bar}"


class CompactHealthBar(Widget):
    """
    Compact single-line XYZ health display.

    Layout: X:87% Y:92% Z:78%
    """

    DEFAULT_CSS = """
    CompactHealthBar {
        width: auto;
        height: 1;
        padding: 0;
        color: #b3a89a;  /* Dusty tan - secondary text */
    }
    """

    x_value: reactive[float] = reactive(1.0)
    y_value: reactive[float] = reactive(1.0)
    z_value: reactive[float] = reactive(1.0)

    def __init__(
        self,
        health: XYZHealth | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        if health:
            self.x_value = health.x_telemetry
            self.y_value = health.y_semantic
            self.z_value = health.z_economic

    def update_health(self, health: XYZHealth) -> None:
        """Update the displayed health values."""
        self.x_value = health.x_telemetry
        self.y_value = health.y_semantic
        self.z_value = health.z_economic

    def watch_x_value(self, new_value: float) -> None:
        """React to X value changes."""
        self.refresh()

    def watch_y_value(self, new_value: float) -> None:
        """React to Y value changes."""
        self.refresh()

    def watch_z_value(self, new_value: float) -> None:
        """React to Z value changes."""
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the compact health display."""
        return (
            f"X:{int(self.x_value * 100):2d}% "
            f"Y:{int(self.y_value * 100):2d}% "
            f"Z:{int(self.z_value * 100):2d}%"
        )


class MiniHealthBar(Widget):
    """
    Minimal inline health bar using block characters.

    Layout: ▓▓▓▒░ (overall health in 5 chars)
    """

    DEFAULT_CSS = """
    MiniHealthBar {
        width: 5;
        height: 1;
        padding: 0;
    }

    MiniHealthBar.healthy {
        color: #7d9c7a;  /* Muted sage */
    }

    MiniHealthBar.warning {
        color: #e6a352;  /* Warm amber */
    }

    MiniHealthBar.critical {
        color: #e88a8a;  /* Salmon pink */
    }
    """

    overall: reactive[float] = reactive(1.0)

    def __init__(
        self,
        health: XYZHealth | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        if health:
            self.overall = health.overall
        self._update_class()

    def update_health(self, health: XYZHealth) -> None:
        """Update the displayed health value."""
        self.overall = health.overall

    def _update_class(self) -> None:
        """Update CSS class based on health level."""
        self.remove_class("healthy", "warning", "critical")
        if self.overall >= 0.6:
            self.add_class("healthy")
        elif self.overall >= 0.3:
            self.add_class("warning")
        else:
            self.add_class("critical")

    def watch_overall(self, new_value: float) -> None:
        """React to health changes."""
        self._update_class()
        self.refresh()

    def render(self) -> "RenderResult":
        """Render the mini health bar."""
        # Use 5 character width with gradient
        chars = "░▒▓█"
        filled = int(self.overall * 5)
        result = ""
        for i in range(5):
            if i < filled:
                result += chars[3]  # Full
            elif i == filled:
                # Partial based on remainder
                remainder = (self.overall * 5) - filled
                char_idx = int(remainder * 3)
                result += chars[char_idx]
            else:
                result += chars[0]  # Empty
        return result
