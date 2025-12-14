"""Temperature system - subtle state communication through color mood.

Philosophy:
    The eye perceives temperature shifts as "mood" not "alert".

    Instead of jarring color changes (red flash for error!), we shift
    the temperature of the ambient light:

    - Cool (blue-tint): calm, waiting, idle
    - Warm (red-tint): active, processing, needs attention
    - Neutral: success, equilibrium

    Same luminance, different hue. The eye reads it as atmosphere,
    not as a demand for attention.

Breathing:
    Screens should "breathe" - subtle rhythmic indication of life
    without distraction. A gentle 4-second cycle that says "I'm here"
    without demanding focus.
"""

import math
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TemperatureShift:
    """Subtle color temperature shifts for state changes.

    Instead of jarring color changes, shift temperature:
    - The eye perceives these as "mood" not "alert"
    - Same luminance, different hue
    - Use for background tints, not foreground elements

    The colors are carefully calibrated to maintain readability
    while communicating state through ambient temperature.
    """

    # Base palette (neutral) - warm white, like paper
    NEUTRAL: ClassVar[str] = "#f5f0e6"

    # Temperature shifts (same luminance, different hue)
    COOL: ClassVar[str] = "#e6f0f5"  # Slightly blue - calm, waiting
    WARM: ClassVar[str] = "#f5e6e0"  # Slightly red - active, processing

    # The earth palette variants (for dark mode / terminals)
    EARTH_NEUTRAL: ClassVar[str] = "#3d3d3d"
    EARTH_COOL: ClassVar[str] = "#3a3d40"
    EARTH_WARM: ClassVar[str] = "#403d3a"

    @classmethod
    def get_all_light_temps(cls) -> dict[str, str]:
        """Get all light mode temperature colors."""
        return {
            "neutral": cls.NEUTRAL,
            "cool": cls.COOL,
            "warm": cls.WARM,
        }

    @classmethod
    def get_all_dark_temps(cls) -> dict[str, str]:
        """Get all dark mode temperature colors."""
        return {
            "neutral": cls.EARTH_NEUTRAL,
            "cool": cls.EARTH_COOL,
            "warm": cls.EARTH_WARM,
        }


# State to temperature mapping
# This is the semantic meaning of each temperature
STATE_TEMPERATURES: dict[str, str] = {
    "idle": TemperatureShift.COOL,  # Waiting, calm
    "processing": TemperatureShift.WARM,  # Active, working
    "success": TemperatureShift.NEUTRAL,  # Complete, balanced
    "error": TemperatureShift.WARM,  # Attention needed (warm, not red flash)
    "loading": TemperatureShift.COOL,  # Patient waiting
    "active": TemperatureShift.WARM,  # User engaged
}


class BreathingIndicator:
    """Subtle life indicator that doesn't demand attention.

    Screens should "breathe" - subtle rhythmic indication of life
    without distraction.

    The breathing cycle:
    - 4 seconds per full cycle (slow enough to be subliminal)
    - Opacity oscillates between 0.3 and 0.6
    - Sine wave for smooth, natural motion
    - No easing (constant velocity feels more organic)

    Usage in Textual CSS:
        BreathingIndicator {
            animation: breathe 4s ease-in-out infinite;
        }

        @keyframes breathe {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.6; }
        }
    """

    # Opacity range - subtle enough to not distract
    MIN_OPACITY: ClassVar[float] = 0.3
    MAX_OPACITY: ClassVar[float] = 0.6

    # Cycle duration - slow enough to be subliminal, fast enough to show life
    CYCLE_SECONDS: ClassVar[float] = 4.0

    # CSS for reference (Textual or web)
    DEFAULT_CSS: ClassVar[str] = """
    BreathingIndicator {
        /* Opacity oscillates 0.3 → 0.6 over 4 seconds */
        animation: breathe 4s ease-in-out infinite;
    }

    @keyframes breathe {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 0.6; }
    }
    """

    @classmethod
    def get_opacity_at_time(cls, elapsed_seconds: float) -> float:
        """Calculate opacity at a given time in the breath cycle.

        Uses a sine wave for smooth, natural breathing motion.
        The cycle starts at minimum opacity (exhale), peaks at half cycle (inhale),
        and returns to minimum at full cycle.

        Args:
            elapsed_seconds: Time elapsed since start (will cycle)

        Returns:
            Opacity value between MIN_OPACITY and MAX_OPACITY
        """
        # Get position in current cycle (0.0 to 1.0)
        cycle_position = (elapsed_seconds % cls.CYCLE_SECONDS) / cls.CYCLE_SECONDS

        # Map 0-1 to 0-2π for full sine cycle
        # Start at -π/2 so sin(-π/2) = -1 (minimum) at t=0
        radians = (cycle_position * 2 * math.pi) - (math.pi / 2)

        # Sine oscillates -1 to 1
        sine_value = math.sin(radians)

        # Map -1 to 1 → MIN_OPACITY to MAX_OPACITY
        opacity_range = cls.MAX_OPACITY - cls.MIN_OPACITY
        opacity = cls.MIN_OPACITY + (sine_value + 1) / 2 * opacity_range

        return opacity

    @classmethod
    def get_css_animation(cls, name: str = "breathe") -> str:
        """Generate CSS animation definition.

        Args:
            name: Animation name to use in CSS

        Returns:
            CSS keyframes definition
        """
        return f"""@keyframes {name} {{
    0%, 100% {{ opacity: {cls.MIN_OPACITY}; }}
    50% {{ opacity: {cls.MAX_OPACITY}; }}
}}"""
