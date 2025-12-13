"""
Tests for Slider widget - Direct manipulation for continuous values.

Tests verify:
- Value clamping and range handling
- Keyboard navigation (h/l, arrows, 0-9)
- Callback invocation
- Rendering
- Boundary conditions
"""

from __future__ import annotations

import pytest
from agents.i.widgets.slider import (
    SLIDER_CHARS,
    Slider,
    clamp,
    generate_slider_track,
)


class TestClamp:
    """Tests for clamp helper function."""

    def test_value_in_range(self) -> None:
        """Value within range is unchanged."""
        assert clamp(0.5, 0.0, 1.0) == 0.5
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_value_below_min(self) -> None:
        """Value below min is clamped to min."""
        assert clamp(-1.0, 0.0, 1.0) == 0.0
        assert clamp(-100.0, 0.0, 10.0) == 0.0

    def test_value_above_max(self) -> None:
        """Value above max is clamped to max."""
        assert clamp(2.0, 0.0, 1.0) == 1.0
        assert clamp(100.0, 0.0, 10.0) == 10.0

    def test_value_at_min(self) -> None:
        """Value at min is unchanged."""
        assert clamp(0.0, 0.0, 1.0) == 0.0

    def test_value_at_max(self) -> None:
        """Value at max is unchanged."""
        assert clamp(1.0, 0.0, 1.0) == 1.0

    def test_negative_range(self) -> None:
        """Clamp works with negative ranges."""
        assert clamp(-5.0, -10.0, -2.0) == -5.0
        assert clamp(-20.0, -10.0, -2.0) == -10.0
        assert clamp(0.0, -10.0, -2.0) == -2.0


class TestGenerateSliderTrack:
    """Tests for slider track generation."""

    def test_minimum_value(self) -> None:
        """Slider at minimum shows thumb at left."""
        track = generate_slider_track(0.0, 0.0, 1.0, 30, show_value=False)
        # Thumb should be near the left cap
        thumb_idx = track.index(SLIDER_CHARS["thumb"])
        left_cap_idx = track.index(SLIDER_CHARS["left_cap"])
        assert thumb_idx == left_cap_idx + 1

    def test_maximum_value(self) -> None:
        """Slider at maximum shows thumb at right end of track."""
        track = generate_slider_track(1.0, 0.0, 1.0, 30, show_value=False)
        # Thumb should be at the end of the filled track
        thumb_idx = track.index(SLIDER_CHARS["thumb"])
        # Right cap comes after thumb
        right_cap_idx = track.rindex(SLIDER_CHARS["right_cap"])
        # Thumb should be right before the right cap
        assert thumb_idx == right_cap_idx - 1

    def test_middle_value(self) -> None:
        """Slider at middle shows thumb in center."""
        track = generate_slider_track(0.5, 0.0, 1.0, 30, show_value=False)
        # Thumb should be somewhere in the middle
        thumb_idx = track.index(SLIDER_CHARS["thumb"])
        assert 5 < thumb_idx < 25

    def test_with_label(self) -> None:
        """Track with label includes label."""
        track = generate_slider_track(0.5, 0.0, 1.0, 40, label="Temperature")
        assert track.startswith("Temperature:")

    def test_with_value_display(self) -> None:
        """Track shows value when show_value=True."""
        track = generate_slider_track(0.75, 0.0, 1.0, 30, show_value=True)
        assert "0.75" in track

    def test_without_value_display(self) -> None:
        """Track hides value when show_value=False."""
        track = generate_slider_track(0.75, 0.0, 1.0, 30, show_value=False)
        assert "0.75" not in track

    def test_custom_range(self) -> None:
        """Track works with custom value range."""
        # Value of 50 in range 0-100 should be at 50%
        track = generate_slider_track(50.0, 0.0, 100.0, 30, show_value=True)
        assert "50.00" in track

    def test_contains_thumb(self) -> None:
        """Track always contains a thumb."""
        for val in [0.0, 0.25, 0.5, 0.75, 1.0]:
            track = generate_slider_track(val, 0.0, 1.0, 30)
            assert SLIDER_CHARS["thumb"] in track

    def test_filled_track_grows_with_value(self) -> None:
        """Filled portion of track grows with value."""
        track_low = generate_slider_track(0.2, 0.0, 1.0, 30, show_value=False)
        track_high = generate_slider_track(0.8, 0.0, 1.0, 30, show_value=False)

        filled_low = track_low.count(SLIDER_CHARS["track_filled"])
        filled_high = track_high.count(SLIDER_CHARS["track_filled"])

        assert filled_high > filled_low


class TestSliderWidget:
    """Tests for Slider widget class."""

    def test_init_defaults(self) -> None:
        """Widget initializes with defaults."""
        slider = Slider()
        assert slider.value == 0.5
        assert slider.min_val == 0.0
        assert slider.max_val == 1.0
        assert slider.step == 0.1
        assert slider.label == ""
        assert slider.show_value is True

    def test_init_with_values(self) -> None:
        """Widget initializes with custom values."""
        slider = Slider(
            value=0.7,
            min_val=0.0,
            max_val=1.0,
            step=0.05,
            label="Entropy",
            show_value=False,
        )
        assert slider.value == 0.7
        assert slider.min_val == 0.0
        assert slider.max_val == 1.0
        assert slider.step == 0.05
        assert slider.label == "Entropy"
        assert slider.show_value is False

    def test_value_clamped_on_init(self) -> None:
        """Value is clamped to range on init."""
        slider = Slider(value=2.0, min_val=0.0, max_val=1.0)
        assert slider.value == 1.0

        slider2 = Slider(value=-1.0, min_val=0.0, max_val=1.0)
        assert slider2.value == 0.0

    def test_set_value(self) -> None:
        """set_value updates and clamps."""
        slider = Slider()
        slider.set_value(0.8)
        assert slider.value == 0.8

        slider.set_value(2.0)
        assert slider.value == 1.0  # Clamped

    def test_set_range(self) -> None:
        """set_range updates min/max and reclamps value."""
        slider = Slider(value=0.5, min_val=0.0, max_val=1.0)
        slider.set_range(0.0, 0.3)
        assert slider.max_val == 0.3
        assert slider.value == 0.3  # Reclamped


class TestSliderActions:
    """Tests for slider keyboard actions."""

    def test_action_increase(self) -> None:
        """action_increase increases value by step."""
        slider = Slider(value=0.5, step=0.1)
        slider.action_increase()
        assert abs(slider.value - 0.6) < 0.001

    def test_action_decrease(self) -> None:
        """action_decrease decreases value by step."""
        slider = Slider(value=0.5, step=0.1)
        slider.action_decrease()
        assert abs(slider.value - 0.4) < 0.001

    def test_action_increase_clamps_at_max(self) -> None:
        """action_increase stops at max."""
        slider = Slider(value=0.95, step=0.1, max_val=1.0)
        slider.action_increase()
        assert slider.value == 1.0

    def test_action_decrease_clamps_at_min(self) -> None:
        """action_decrease stops at min."""
        slider = Slider(value=0.05, step=0.1, min_val=0.0)
        slider.action_decrease()
        assert slider.value == 0.0

    def test_action_jump_min(self) -> None:
        """action_jump_min sets to minimum."""
        slider = Slider(value=0.7, min_val=0.2)
        slider.action_jump_min()
        assert slider.value == 0.2

    def test_action_jump_max(self) -> None:
        """action_jump_max sets to maximum."""
        slider = Slider(value=0.3, max_val=0.9)
        slider.action_jump_max()
        assert slider.value == 0.9

    def test_numeric_shortcuts(self) -> None:
        """Numeric shortcuts set to percentage of range."""
        slider = Slider(min_val=0.0, max_val=100.0)

        slider.action_set_0()
        assert slider.value == 0.0

        slider.action_set_50()
        assert slider.value == 50.0

        slider.action_set_90()
        assert slider.value == 90.0


class TestSliderCallbacks:
    """Tests for slider callback functionality."""

    def test_callback_on_change(self) -> None:
        """Callback is called when value changes."""
        called_with: list[float] = []

        def callback(value: float) -> None:
            called_with.append(value)

        slider = Slider(on_change=callback, value=0.5)
        slider.set_value(0.7)

        # Should have been called with new value
        assert 0.7 in called_with

    def test_no_callback_if_none(self) -> None:
        """No error if callback is None."""
        slider = Slider(on_change=None)
        slider.set_value(0.7)  # Should not raise

    def test_set_callback(self) -> None:
        """set_callback updates the callback."""
        called_with: list[float] = []

        slider = Slider(value=0.5)
        slider.set_callback(lambda v: called_with.append(v))
        slider.set_value(0.8)

        assert 0.8 in called_with


class TestSliderNormalization:
    """Tests for normalized value handling."""

    def test_get_normalized_value(self) -> None:
        """get_normalized_value returns 0-1 value."""
        slider = Slider(value=50.0, min_val=0.0, max_val=100.0)
        assert slider.get_normalized_value() == 0.5

        slider2 = Slider(value=-5.0, min_val=-10.0, max_val=0.0)
        assert slider2.get_normalized_value() == 0.5

    def test_set_normalized_value(self) -> None:
        """set_normalized_value sets from 0-1 range."""
        slider = Slider(min_val=0.0, max_val=100.0)
        slider.set_normalized_value(0.5)
        assert slider.value == 50.0

        slider.set_normalized_value(0.0)
        assert slider.value == 0.0

        slider.set_normalized_value(1.0)
        assert slider.value == 100.0

    def test_normalized_clamps(self) -> None:
        """Normalized value is clamped to 0-1."""
        slider = Slider(min_val=0.0, max_val=100.0)
        slider.set_normalized_value(2.0)
        assert slider.value == 100.0

        slider.set_normalized_value(-1.0)
        assert slider.value == 0.0


class TestSliderBoundaryConditions:
    """Tests for boundary conditions and edge cases."""

    def test_zero_range(self) -> None:
        """Handles zero range gracefully (min == max)."""
        slider = Slider(value=5.0, min_val=5.0, max_val=5.0)
        # Should not crash
        assert slider.value == 5.0
        assert slider.get_normalized_value() == 0.5  # Default for zero range

    def test_inverted_range(self) -> None:
        """Handles inverted range (min > max)."""
        # This is pathological but shouldn't crash
        slider = Slider(value=0.5, min_val=1.0, max_val=0.0)
        # Behavior is undefined but should not crash
        assert isinstance(slider.value, float)

    def test_very_small_step(self) -> None:
        """Handles very small step sizes."""
        slider = Slider(value=0.5, step=0.0001)
        slider.action_increase()
        assert abs(slider.value - 0.5001) < 0.0001

    def test_very_large_range(self) -> None:
        """Handles very large value ranges."""
        slider = Slider(value=5e6, min_val=0.0, max_val=1e9)
        assert slider.value == 5e6
        slider.action_increase()  # Should not overflow

    def test_negative_range(self) -> None:
        """Handles negative value ranges."""
        slider = Slider(value=-5.0, min_val=-10.0, max_val=0.0, step=1.0)
        assert slider.value == -5.0

        slider.action_increase()
        assert slider.value == -4.0

        slider.action_jump_min()
        assert slider.value == -10.0


class TestSliderRender:
    """Tests for slider rendering."""

    def test_render_basic(self) -> None:
        """Basic render produces string."""
        slider = Slider(value=0.5)
        slider._size = (40, 1)  # type: ignore
        result = str(slider.render())

        assert SLIDER_CHARS["thumb"] in result
        assert len(result) > 0

    def test_render_with_label(self) -> None:
        """Render with label includes label."""
        slider = Slider(value=0.5, label="Temp")
        slider._size = (40, 1)  # type: ignore
        result = str(slider.render())

        assert "Temp" in result

    def test_render_without_value(self) -> None:
        """Render with show_value=False hides value."""
        slider = Slider(value=0.75, show_value=False)
        slider._size = (40, 1)  # type: ignore
        result = str(slider.render())

        assert "0.75" not in result
