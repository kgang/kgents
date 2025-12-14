"""
WeatherWidget - System weather display for dashboards.

Displays system health as weather conditions:
- Cloud cover: Entropy level
- Temperature: Token rate
- Pressure: Queue depth
- Wind: Event flow direction

Compact display suitable for headers and status bars.

Usage:
    weather_widget = WeatherWidget()
    # Updates automatically from system metrics

Principle 4 (Joy-Inducing): Weather metaphors make system state intuitive.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.reactive import reactive
from textual.widgets import Static

from ..data.weather import (
    SystemMetrics,
    Weather,
    WeatherCondition,
    WeatherEngine,
    create_demo_weather,
)

if TYPE_CHECKING:
    pass


class WeatherWidget(Static):
    """
    Compact weather display showing system state.

    Shows a one-line summary of system weather with:
    - Condition icon (sun, clouds, storm)
    - Temperature indicator
    - Pressure level
    - Wind direction

    When entropy is high (>0.8), shows an Oblique Strategy.
    """

    DEFAULT_CSS = """
    WeatherWidget {
        height: 1;
        width: auto;
        min-width: 40;
        padding: 0 1;
        color: #b3a89a;
    }

    WeatherWidget.stormy {
        color: #e88a8a;
    }

    WeatherWidget.clear {
        color: #7bc275;
    }

    WeatherWidget.cloudy {
        color: #8b7ba5;
    }
    """

    # Reactive properties
    entropy: reactive[float] = reactive(0.3)
    token_rate: reactive[float] = reactive(100.0)
    queue_depth: reactive[int] = reactive(5)

    def __init__(
        self,
        weather: Weather | None = None,
        demo_mode: bool = False,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        """
        Initialize the WeatherWidget.

        Args:
            weather: Initial weather state (optional)
            demo_mode: Use demo data
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self._engine = WeatherEngine()

        if demo_mode or weather is None:
            self._weather = create_demo_weather()
        else:
            self._weather = weather

    def render(self) -> str:
        """Render the weather display."""
        w = self._weather

        # Condition icon
        condition_icons = {
            WeatherCondition.CLEAR: "[#7bc275]\\[/]",
            WeatherCondition.FAIR: "[#8ac4e8]\\[/]",
            WeatherCondition.PARTLY_CLOUDY: "[#b3a89a][/]",
            WeatherCondition.CLOUDY: "[#8b7ba5]☁[/]",
            WeatherCondition.OVERCAST: "[#6a6560]☁☁[/]",
            WeatherCondition.STORMY: "[#e88a8a]⛈[/]",
            WeatherCondition.FOGGY: "[#6a6560]▒[/]",
        }
        icon = condition_icons.get(w.condition, "?")

        # Condition name
        condition_name = w.condition.name.replace("_", " ").title()

        # Temperature with color
        temp_colors = {
            "Cold": "#8ac4e8",
            "Cool": "#b3a89a",
            "Warm": "#f5d08a",
            "Hot": "#e88a8a",
        }
        temp_color = temp_colors.get(w.temperature, "#b3a89a")

        # Pressure indicator
        pressure_str = {
            "LOW": "[#8ac4e8]↓[/]",
            "NORMAL": "[#7bc275]→[/]",
            "HIGH": "[#f5d08a]↑[/]",
            "CRITICAL": "[#e88a8a]↑↑[/]",
        }.get(w.pressure.name, "?")

        # Wind direction
        wind_str = f"[dim]{w.wind.value}[/]"

        # Build output
        output = f"{icon} {condition_name} [{temp_color}]{w.temperature}[/] P:{pressure_str} W:{wind_str}"

        # Add oblique strategy if present
        if w.oblique_strategy:
            strategy = (
                w.oblique_strategy[:30] + "..."
                if len(w.oblique_strategy) > 30
                else w.oblique_strategy
            )
            output += f' │ [#8b7ba5]"{strategy}"[/]'

        return output

    def update_metrics(
        self,
        entropy: float | None = None,
        token_rate: float | None = None,
        queue_depth: int | None = None,
    ) -> None:
        """
        Update weather from new metrics.

        Args:
            entropy: New entropy level (0.0-1.0)
            token_rate: New token rate
            queue_depth: New queue depth
        """
        if entropy is not None:
            self.entropy = entropy
        if token_rate is not None:
            self.token_rate = token_rate
        if queue_depth is not None:
            self.queue_depth = queue_depth

        # Recompute weather
        metrics = SystemMetrics(
            entropy=self.entropy,
            token_rate=self.token_rate,
            queue_depth=self.queue_depth,
        )
        self._weather = self._engine.compute_weather(metrics)

        # Update CSS class based on condition
        self.remove_class("clear", "cloudy", "stormy")
        if self._weather.condition in (WeatherCondition.CLEAR, WeatherCondition.FAIR):
            self.add_class("clear")
        elif self._weather.condition in (WeatherCondition.STORMY,):
            self.add_class("stormy")
        elif self._weather.condition in (
            WeatherCondition.CLOUDY,
            WeatherCondition.OVERCAST,
            WeatherCondition.FOGGY,
        ):
            self.add_class("cloudy")

        self.refresh()

    def update_weather(self, weather: Weather) -> None:
        """
        Directly update with a Weather object.

        Args:
            weather: New weather state
        """
        self._weather = weather
        self.refresh()

    @property
    def current_weather(self) -> Weather:
        """Get the current weather state."""
        return self._weather

    @property
    def trend(self) -> str:
        """Get the weather trend."""
        return self._engine.get_trend()


class CompactWeatherWidget(Static):
    """
    Ultra-compact weather display for tight spaces.

    Shows just an icon and key metrics.
    """

    DEFAULT_CSS = """
    CompactWeatherWidget {
        height: 1;
        width: auto;
        min-width: 15;
        padding: 0 1;
        color: #b3a89a;
    }
    """

    def __init__(
        self,
        weather: Weather | None = None,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._weather = weather or create_demo_weather()

    def render(self) -> str:
        """Render compact weather."""
        w = self._weather

        # Super compact icons
        condition_icons = {
            WeatherCondition.CLEAR: "",
            WeatherCondition.FAIR: "⛅",
            WeatherCondition.PARTLY_CLOUDY: "🌤",
            WeatherCondition.CLOUDY: "☁",
            WeatherCondition.OVERCAST: "☁☁",
            WeatherCondition.STORMY: "⛈",
            WeatherCondition.FOGGY: "🌫",
        }
        icon = condition_icons.get(w.condition, "?")

        # Cloud cover percentage
        cloud_str = f"{w.cloud_cover:.0f}%"

        return f"{icon} {cloud_str} {w.wind.value}"

    def update_weather(self, weather: Weather) -> None:
        """Update the weather."""
        self._weather = weather
        self.refresh()


__all__ = [
    "WeatherWidget",
    "CompactWeatherWidget",
]
