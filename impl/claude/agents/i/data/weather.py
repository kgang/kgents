"""
System Weather Visualization - Entropy and system state as atmospheric conditions.

Weather metaphors provide intuitive understanding of system health:
- Cloud cover: Entropy level (more clouds = more chaos)
- Temperature: Token rate (hotter = faster processing)
- Pressure: Queue depth (high pressure = congested)
- Wind: Event flow direction (shows data movement)
- Conditions: Overall system state

When entropy is high (>0.8), an Oblique Strategy is displayed
as a creative prompt for the user.

Usage:
    engine = WeatherEngine()
    weather = engine.compute_weather(metrics)
    print(weather.condition)  # "Partly Cloudy"
    print(weather.ascii_art)  # Cloud/sun visualization
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class WeatherCondition(Enum):
    """Weather condition classifications."""

    CLEAR = auto()  # Low entropy, healthy system
    FAIR = auto()  # Normal operation
    PARTLY_CLOUDY = auto()  # Some uncertainty
    CLOUDY = auto()  # Elevated entropy
    OVERCAST = auto()  # High uncertainty
    STORMY = auto()  # Critical entropy levels
    FOGGY = auto()  # Low visibility/understanding


class PressureLevel(Enum):
    """System pressure levels."""

    LOW = auto()  # Underutilized
    NORMAL = auto()  # Healthy load
    HIGH = auto()  # Heavy load
    CRITICAL = auto()  # Overloaded


class WindDirection(Enum):
    """Event flow direction."""

    NORTH = "↑"  # Upward (agent → user)
    SOUTH = "↓"  # Downward (user → agent)
    EAST = "→"  # Forward (agent → world)
    WEST = "←"  # Backward (world → agent)
    CALM = "○"  # No significant flow


# Oblique Strategies (subset for high entropy moments)
OBLIQUE_STRATEGIES = [
    "Honor thy error as a hidden intention",
    "Use an old idea",
    "What would your closest friend do?",
    "What mistakes did you make last time?",
    "Consider different fading systems",
    "Remove specifics and convert to ambiguities",
    "Go outside. Shut the door.",
    "Trust in the you of now",
    "Ask people to work against their better judgement",
    "Take away the elements in order of apparent non-importance",
    "Emphasize differences",
    "Don't be afraid of things because they're easy to do",
    "What are you really thinking about just now?",
    "Breathe more deeply",
    "Turn it upside down",
    "Cluster analysis",
    "Give way to your worst impulse",
    "The most important thing is the thing most easily forgotten",
    "State the problem in words as clearly as possible",
    "Only a part, not the whole",
]


@dataclass
class SystemMetrics:
    """System metrics used to compute weather."""

    entropy: float = 0.3  # 0.0 to 1.0
    token_rate: float = 100.0  # tokens per second
    queue_depth: int = 5  # pending items
    active_agents: int = 3
    recent_events: list[dict[str, Any]] = field(default_factory=list)
    error_rate: float = 0.0  # 0.0 to 1.0
    uptime: timedelta = field(default_factory=lambda: timedelta(hours=1))


@dataclass
class Forecast:
    """Weather forecast for future turns."""

    condition: WeatherCondition
    confidence: float  # 0.0 to 1.0
    horizon: str  # "next turn", "3 turns", etc.
    description: str


@dataclass
class Weather:
    """
    Current system weather state.

    Combines all weather metrics into a cohesive picture
    of system health and behavior.
    """

    condition: WeatherCondition
    cloud_cover: float  # 0-100%
    pressure: PressureLevel
    temperature: str  # "Cold", "Cool", "Warm", "Hot"
    wind: WindDirection
    wind_speed: float  # events/second
    forecast: list[Forecast]
    oblique_strategy: str | None = None  # Shown when entropy > 0.8
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def ascii_art(self) -> str:
        """Get ASCII art representation of weather."""
        return WEATHER_ASCII.get(self.condition, WEATHER_ASCII[WeatherCondition.FAIR])

    @property
    def summary(self) -> str:
        """Get one-line summary of weather."""
        condition_name = self.condition.name.replace("_", " ").title()
        return (
            f"{condition_name} │ {self.temperature} │ "
            f"Pressure: {self.pressure.name} │ Wind: {self.wind.value}"
        )

    @property
    def detailed_summary(self) -> str:
        """Get detailed weather summary."""
        lines = [
            f"Condition: {self.condition.name.replace('_', ' ').title()}",
            f"Cloud Cover: {self.cloud_cover:.0f}%",
            f"Temperature: {self.temperature}",
            f"Pressure: {self.pressure.name}",
            f"Wind: {self.wind.value} at {self.wind_speed:.1f} ev/s",
        ]

        if self.forecast:
            lines.append(f"Forecast: {self.forecast[0].description}")

        if self.oblique_strategy:
            lines.append(f'Suggestion: "{self.oblique_strategy}"')

        return "\n".join(lines)


# ASCII art for weather conditions
WEATHER_ASCII = {
    WeatherCondition.CLEAR: """
    \\   /
     .-.
  ― (   ) ―
     `-'
    /   \\
""",
    WeatherCondition.FAIR: """
   \\  /
 _ /\"\".-.
   \\_( ).
   /(_(_)
""",
    WeatherCondition.PARTLY_CLOUDY: """
   \\  /
 _ /\"\"-._
   \\_(   ).
   /(_(____)
""",
    WeatherCondition.CLOUDY: """
     .--.
  .-(    ).
 (___.__)__)
""",
    WeatherCondition.OVERCAST: """
     .--.
  .-(    ).
 (___.__)__)
     .-.
    (   )
""",
    WeatherCondition.STORMY: """
     .--.
  .-(    ).
 (___.__)__)
   ⚡ ⚡ ⚡
""",
    WeatherCondition.FOGGY: """
  _ - _ - _
   _ - _ -
  _ - _ - _
   - _ - _
""",
}


class WeatherEngine:
    """
    Computes weather from system metrics.

    Maps technical metrics to intuitive weather metaphors:
    - Entropy → Cloud cover
    - Queue depth → Pressure
    - Token rate → Temperature
    - Event flow → Wind
    """

    # Entropy thresholds for conditions
    ENTROPY_THRESHOLDS = {
        0.1: WeatherCondition.CLEAR,
        0.3: WeatherCondition.FAIR,
        0.5: WeatherCondition.PARTLY_CLOUDY,
        0.7: WeatherCondition.CLOUDY,
        0.85: WeatherCondition.OVERCAST,
        1.0: WeatherCondition.STORMY,
    }

    # Queue depth thresholds for pressure
    QUEUE_THRESHOLDS = {
        2: PressureLevel.LOW,
        10: PressureLevel.NORMAL,
        25: PressureLevel.HIGH,
        1000: PressureLevel.CRITICAL,
    }

    # Token rate thresholds for temperature
    TEMP_THRESHOLDS = {
        10: "Cold",
        50: "Cool",
        150: "Warm",
        1000000: "Hot",
    }

    def __init__(self) -> None:
        """Initialize the weather engine."""
        self._last_weather: Weather | None = None
        self._history: list[Weather] = []
        self._external_trend: float = 0.0  # Trend from external sources (e.g., pressure history)

    def set_trend(self, trend: float) -> None:
        """Set external trend value from metabolism pressure history.

        Args:
            trend: Positive = worsening (pressure rising), Negative = improving
        """
        self._external_trend = trend

    def compute_weather(self, metrics: SystemMetrics) -> Weather:
        """
        Compute current weather from system metrics.

        Args:
            metrics: Current system metrics

        Returns:
            Weather state
        """
        # Compute cloud cover from entropy
        cloud_cover = metrics.entropy * 100

        # Determine condition from entropy
        condition = self._classify_condition(metrics.entropy)

        # Check for fog (high error rate)
        if metrics.error_rate > 0.3:
            condition = WeatherCondition.FOGGY

        # Compute pressure from queue depth
        pressure = self._classify_pressure(metrics.queue_depth)

        # Compute temperature from token rate
        temperature = self._classify_temperature(metrics.token_rate)

        # Compute wind from recent events
        wind, wind_speed = self._compute_wind(metrics.recent_events)

        # Generate forecast
        forecast = self._predict_forecast(metrics)

        # Get oblique strategy if entropy is high
        oblique_strategy = None
        if metrics.entropy > 0.8:
            oblique_strategy = random.choice(OBLIQUE_STRATEGIES)

        weather = Weather(
            condition=condition,
            cloud_cover=cloud_cover,
            pressure=pressure,
            temperature=temperature,
            wind=wind,
            wind_speed=wind_speed,
            forecast=forecast,
            oblique_strategy=oblique_strategy,
        )

        # Track history
        self._last_weather = weather
        self._history.append(weather)
        if len(self._history) > 100:
            self._history = self._history[-50:]

        return weather

    def _classify_condition(self, entropy: float) -> WeatherCondition:
        """Classify weather condition from entropy."""
        for threshold, condition in sorted(self.ENTROPY_THRESHOLDS.items()):
            if entropy <= threshold:
                return condition
        return WeatherCondition.STORMY

    def _classify_pressure(self, queue_depth: int) -> PressureLevel:
        """Classify pressure from queue depth."""
        for threshold, level in sorted(self.QUEUE_THRESHOLDS.items()):
            if queue_depth <= threshold:
                return level
        return PressureLevel.CRITICAL

    def _classify_temperature(self, token_rate: float) -> str:
        """Classify temperature from token rate."""
        for threshold, temp in sorted(self.TEMP_THRESHOLDS.items()):
            if token_rate <= threshold:
                return temp
        return "Hot"

    def _compute_wind(
        self,
        events: list[dict[str, Any]],
    ) -> tuple[WindDirection, float]:
        """
        Compute wind direction and speed from recent events.

        Analyzes event flow to determine predominant direction.
        """
        if not events:
            return WindDirection.CALM, 0.0

        # Count event directions
        directions = {
            "user_to_agent": 0,
            "agent_to_user": 0,
            "agent_to_world": 0,
            "world_to_agent": 0,
        }

        for event in events[-20:]:  # Last 20 events
            event_type = event.get("type", "")
            if event_type in ("USER_INPUT", "COMMAND"):
                directions["user_to_agent"] += 1
            elif event_type in ("SPEECH", "RESPONSE"):
                directions["agent_to_user"] += 1
            elif event_type in ("ACTION", "TOOL_CALL"):
                directions["agent_to_world"] += 1
            elif event_type in ("TOOL_RESULT", "OBSERVATION"):
                directions["world_to_agent"] += 1

        # Find dominant direction
        max_count = max(directions.values())
        if max_count == 0:
            return WindDirection.CALM, 0.0

        dominant = max(directions, key=lambda k: directions[k])

        direction_map = {
            "user_to_agent": WindDirection.SOUTH,
            "agent_to_user": WindDirection.NORTH,
            "agent_to_world": WindDirection.EAST,
            "world_to_agent": WindDirection.WEST,
        }

        wind_dir = direction_map.get(dominant, WindDirection.CALM)
        wind_speed = len(events) / 10.0  # events per second (approx)

        return wind_dir, wind_speed

    def _predict_forecast(self, metrics: SystemMetrics) -> list[Forecast]:
        """
        Predict weather for upcoming turns.

        Uses trend analysis from both queue depth and external pressure history
        to forecast conditions.
        """
        forecasts = []

        # Use external trend from metabolism pressure history if available
        # Positive trend = pressure rising = weather worsening
        # Negative trend = pressure falling = weather improving
        if self._external_trend > 0.05:
            # Pressure rising rapidly
            forecasts.append(
                Forecast(
                    condition=WeatherCondition.CLOUDY,
                    confidence=0.8,
                    horizon="next 3 turns",
                    description="Pressure rising, expect clouds",
                )
            )
        elif self._external_trend < -0.05:
            # Pressure falling rapidly
            forecasts.append(
                Forecast(
                    condition=WeatherCondition.FAIR,
                    confidence=0.8,
                    horizon="next 3 turns",
                    description="Pressure falling, clearing expected",
                )
            )
        # Queue-based prediction as fallback
        elif metrics.queue_depth > 20:
            # Congestion building
            forecasts.append(
                Forecast(
                    condition=WeatherCondition.CLOUDY,
                    confidence=0.7,
                    horizon="next 3 turns",
                    description="Increasing cloudiness expected",
                )
            )
        elif metrics.entropy < 0.2:
            # Clear conditions likely to continue
            forecasts.append(
                Forecast(
                    condition=WeatherCondition.CLEAR,
                    confidence=0.8,
                    horizon="next 5 turns",
                    description="Clear conditions continuing",
                )
            )
        else:
            # Normal variability
            forecasts.append(
                Forecast(
                    condition=WeatherCondition.PARTLY_CLOUDY,
                    confidence=0.6,
                    horizon="next turn",
                    description="Variable conditions",
                )
            )

        return forecasts

    def get_trend(self) -> str:
        """Get weather trend from history."""
        if len(self._history) < 2:
            return "stable"

        recent = self._history[-5:]
        entropy_trend = sum(1 if w.cloud_cover > 50 else -1 for w in recent)

        if entropy_trend > 2:
            return "worsening"
        elif entropy_trend < -2:
            return "improving"
        return "stable"


def create_demo_weather() -> Weather:
    """Create demo weather for testing."""
    engine = WeatherEngine()
    metrics = SystemMetrics(
        entropy=0.45,
        token_rate=120.0,
        queue_depth=7,
        active_agents=4,
        recent_events=[
            {"type": "ACTION", "time": datetime.now()},
            {"type": "TOOL_RESULT", "time": datetime.now()},
            {"type": "SPEECH", "time": datetime.now()},
        ],
    )
    return engine.compute_weather(metrics)


__all__ = [
    "Weather",
    "WeatherEngine",
    "WeatherCondition",
    "PressureLevel",
    "WindDirection",
    "SystemMetrics",
    "Forecast",
    "OBLIQUE_STRATEGIES",
    "create_demo_weather",
]
