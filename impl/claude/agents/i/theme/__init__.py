"""I-gent v2.5 Theme - Deep Earth + Pink/Purple."""

from .dashboard import THEME, DashboardTheme
from .earth import EARTH_PALETTE, EarthTheme
from .heartbeat import HeartbeatController, HeartbeatMixin, get_heartbeat_controller
from .temperature import (
    STATE_TEMPERATURES,
    BreathingIndicator,
    TemperatureShift,
)

__all__ = [
    "EARTH_PALETTE",
    "EarthTheme",
    "DashboardTheme",
    "THEME",
    "HeartbeatMixin",
    "HeartbeatController",
    "get_heartbeat_controller",
    "TemperatureShift",
    "BreathingIndicator",
    "STATE_TEMPERATURES",
]
