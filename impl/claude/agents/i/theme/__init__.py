"""I-gent v2.5 Theme - Deep Earth + Pink/Purple + QualiaSpace."""

from .dashboard import THEME, DashboardTheme
from .earth import EARTH_PALETTE, EarthTheme
from .heartbeat import HeartbeatController, HeartbeatMixin, get_heartbeat_controller
from .qualia import (
    CIRCADIAN_MODIFIERS,
    CircadianPhase,
    ColorParams,
    MotionParams,
    QualiaCoords,
    QualiaModifier,
    QualiaSpace,
    ShapeParams,
)
from .temperature import (
    STATE_TEMPERATURES,
    BreathingIndicator,
    TemperatureShift,
)

__all__ = [
    # Earth Theme
    "EARTH_PALETTE",
    "EarthTheme",
    "DashboardTheme",
    "THEME",
    # Heartbeat
    "HeartbeatMixin",
    "HeartbeatController",
    "get_heartbeat_controller",
    # Temperature
    "TemperatureShift",
    "BreathingIndicator",
    "STATE_TEMPERATURES",
    # Qualia Space
    "QualiaCoords",
    "QualiaSpace",
    "QualiaModifier",
    "CircadianPhase",
    "CIRCADIAN_MODIFIERS",
    "ColorParams",
    "MotionParams",
    "ShapeParams",
]
