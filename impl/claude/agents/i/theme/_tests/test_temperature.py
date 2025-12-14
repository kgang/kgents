"""Tests for the temperature system - subtle state communication.

Philosophy verification:
    - Temperature shifts are subtle (mood, not alert)
    - Same luminance, different hue
    - Breathing is subliminal (4s cycle)
    - State mapping is semantic
"""

import math

import pytest
from agents.i.theme.temperature import (
    STATE_TEMPERATURES,
    BreathingIndicator,
    TemperatureShift,
)


class TestTemperatureShift:
    """Test TemperatureShift color palette."""

    def test_light_mode_colors_defined(self) -> None:
        """All light mode temperature colors should be defined."""
        assert TemperatureShift.NEUTRAL == "#f5f0e6"
        assert TemperatureShift.COOL == "#e6f0f5"
        assert TemperatureShift.WARM == "#f5e6e0"

    def test_dark_mode_colors_defined(self) -> None:
        """All dark mode (earth) temperature colors should be defined."""
        assert TemperatureShift.EARTH_NEUTRAL == "#3d3d3d"
        assert TemperatureShift.EARTH_COOL == "#3a3d40"
        assert TemperatureShift.EARTH_WARM == "#403d3a"

    def test_get_all_light_temps(self) -> None:
        """Should return all light mode temperatures."""
        temps = TemperatureShift.get_all_light_temps()
        assert temps == {
            "neutral": "#f5f0e6",
            "cool": "#e6f0f5",
            "warm": "#f5e6e0",
        }

    def test_get_all_dark_temps(self) -> None:
        """Should return all dark mode temperatures."""
        temps = TemperatureShift.get_all_dark_temps()
        assert temps == {
            "neutral": "#3d3d3d",
            "cool": "#3a3d40",
            "warm": "#403d3a",
        }

    def test_colors_are_hex_format(self) -> None:
        """All colors should be valid hex format."""
        all_colors = [
            TemperatureShift.NEUTRAL,
            TemperatureShift.COOL,
            TemperatureShift.WARM,
            TemperatureShift.EARTH_NEUTRAL,
            TemperatureShift.EARTH_COOL,
            TemperatureShift.EARTH_WARM,
        ]
        for color in all_colors:
            assert color.startswith("#")
            assert len(color) == 7
            # Should be valid hex
            int(color[1:], 16)


class TestStateTemperatures:
    """Test state to temperature mapping."""

    def test_idle_is_cool(self) -> None:
        """Idle state should map to cool temperature."""
        assert STATE_TEMPERATURES["idle"] == TemperatureShift.COOL

    def test_processing_is_warm(self) -> None:
        """Processing state should map to warm temperature."""
        assert STATE_TEMPERATURES["processing"] == TemperatureShift.WARM

    def test_success_is_neutral(self) -> None:
        """Success state should map to neutral temperature."""
        assert STATE_TEMPERATURES["success"] == TemperatureShift.NEUTRAL

    def test_error_is_warm_not_red(self) -> None:
        """Error should be warm (attention needed), not red flash."""
        assert STATE_TEMPERATURES["error"] == TemperatureShift.WARM

    def test_all_common_states_mapped(self) -> None:
        """All common states should have temperature mappings."""
        expected_states = {
            "idle",
            "processing",
            "success",
            "error",
            "loading",
            "active",
        }
        assert set(STATE_TEMPERATURES.keys()) == expected_states

    def test_loading_is_cool(self) -> None:
        """Loading should be cool (patient waiting)."""
        assert STATE_TEMPERATURES["loading"] == TemperatureShift.COOL

    def test_active_is_warm(self) -> None:
        """Active state should be warm (user engaged)."""
        assert STATE_TEMPERATURES["active"] == TemperatureShift.WARM


class TestBreathingIndicator:
    """Test BreathingIndicator subliminal animation."""

    def test_opacity_constants(self) -> None:
        """Opacity range should be subtle (0.3 to 0.6)."""
        assert BreathingIndicator.MIN_OPACITY == 0.3
        assert BreathingIndicator.MAX_OPACITY == 0.6

    def test_cycle_duration(self) -> None:
        """Cycle should be 4 seconds (slow, subliminal)."""
        assert BreathingIndicator.CYCLE_SECONDS == 4.0

    def test_opacity_at_start(self) -> None:
        """Opacity at t=0 should be minimum (starting exhale)."""
        opacity = BreathingIndicator.get_opacity_at_time(0.0)
        assert abs(opacity - BreathingIndicator.MIN_OPACITY) < 0.01

    def test_opacity_at_half_cycle(self) -> None:
        """Opacity at t=2s (half cycle) should be maximum."""
        opacity = BreathingIndicator.get_opacity_at_time(2.0)
        assert abs(opacity - BreathingIndicator.MAX_OPACITY) < 0.01

    def test_opacity_at_full_cycle(self) -> None:
        """Opacity at t=4s (full cycle) should return to minimum."""
        opacity = BreathingIndicator.get_opacity_at_time(4.0)
        assert abs(opacity - BreathingIndicator.MIN_OPACITY) < 0.01

    def test_opacity_cycles_correctly(self) -> None:
        """Opacity should cycle back after full period."""
        opacity_at_0 = BreathingIndicator.get_opacity_at_time(0.0)
        opacity_at_4 = BreathingIndicator.get_opacity_at_time(4.0)
        opacity_at_8 = BreathingIndicator.get_opacity_at_time(8.0)

        assert abs(opacity_at_0 - opacity_at_4) < 0.01
        assert abs(opacity_at_0 - opacity_at_8) < 0.01

    def test_opacity_in_range(self) -> None:
        """Opacity should always be within MIN to MAX range."""
        test_times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.7, 10.3]
        for t in test_times:
            opacity = BreathingIndicator.get_opacity_at_time(t)
            assert (
                BreathingIndicator.MIN_OPACITY
                <= opacity
                <= BreathingIndicator.MAX_OPACITY
            )

    def test_opacity_is_smooth(self) -> None:
        """Opacity should change smoothly (no jumps)."""
        prev_opacity = BreathingIndicator.get_opacity_at_time(0.0)
        for i in range(1, 40):  # 0.1s steps over 4s
            t = i * 0.1
            opacity = BreathingIndicator.get_opacity_at_time(t)
            # Change should be gradual (< 0.05 per 0.1s)
            assert abs(opacity - prev_opacity) < 0.05
            prev_opacity = opacity

    def test_sine_wave_calculation(self) -> None:
        """Should use sine wave for natural breathing."""
        # At quarter cycle (1s), sine wave is at 0 (mid-opacity)
        opacity_at_1s = BreathingIndicator.get_opacity_at_time(1.0)
        mid_opacity = (
            BreathingIndicator.MIN_OPACITY + BreathingIndicator.MAX_OPACITY
        ) / 2
        # sin(0) = 0, so opacity should be mid-point (0.45)
        assert abs(opacity_at_1s - mid_opacity) < 0.01

        # At three-quarter cycle (3s), sine wave is back at 0 (mid-opacity)
        opacity_at_3s = BreathingIndicator.get_opacity_at_time(3.0)
        # sin(π) = 0, so opacity should be mid-point
        assert abs(opacity_at_3s - mid_opacity) < 0.01

    def test_get_css_animation_default(self) -> None:
        """Should generate CSS animation with default name."""
        css = BreathingIndicator.get_css_animation()
        assert "@keyframes breathe" in css
        assert "opacity: 0.3" in css
        assert "opacity: 0.6" in css
        assert "0%, 100%" in css
        assert "50%" in css

    def test_get_css_animation_custom_name(self) -> None:
        """Should generate CSS animation with custom name."""
        css = BreathingIndicator.get_css_animation(name="pulse")
        assert "@keyframes pulse" in css
        assert "breathe" not in css

    def test_default_css_constant(self) -> None:
        """DEFAULT_CSS should contain complete animation definition."""
        css = BreathingIndicator.DEFAULT_CSS
        assert "BreathingIndicator" in css
        assert "animation:" in css
        assert "4s" in css
        assert "ease-in-out" in css
        assert "infinite" in css
        assert "@keyframes breathe" in css
