"""Tests for Tween animation primitive."""

import pytest

from agents.i.reactive.animation.easing import Easing, EasingCurve
from agents.i.reactive.animation.tween import (
    Interpolator,
    TransitionStatus,
    Tween,
    TweenConfig,
    TweenState,
    lerp_color_rgb,
    lerp_int,
    lerp_number,
    lerp_tuple,
    tween,
)


class TestInterpolators:
    """Tests for interpolation functions."""

    def test_lerp_number_at_zero(self) -> None:
        """Number lerp at t=0 returns start."""
        assert lerp_number(0.0, 100.0, 0.0) == 0.0

    def test_lerp_number_at_one(self) -> None:
        """Number lerp at t=1 returns end."""
        assert lerp_number(0.0, 100.0, 1.0) == 100.0

    def test_lerp_number_at_half(self) -> None:
        """Number lerp at t=0.5 returns midpoint."""
        assert lerp_number(0.0, 100.0, 0.5) == 50.0

    def test_lerp_int(self) -> None:
        """Integer lerp rounds correctly."""
        assert lerp_int(0, 10, 0.5) == 5
        assert lerp_int(0, 10, 0.33) == 3
        assert lerp_int(0, 10, 0.67) == 7

    def test_lerp_tuple(self) -> None:
        """Tuple lerp interpolates each component."""
        result = lerp_tuple((0.0, 0.0), (100.0, 200.0), 0.5)
        assert result == (50.0, 100.0)

    def test_lerp_color_rgb(self) -> None:
        """RGB color lerp works correctly."""
        black = (0, 0, 0)
        white = (255, 255, 255)
        gray = lerp_color_rgb(black, white, 0.5)
        assert gray == (128, 128, 128)


class TestTweenCreation:
    """Tests for Tween creation."""

    def test_create_basic(self) -> None:
        """Create basic tween."""
        tw = Tween.create(start=0.0, end=100.0)
        assert tw.state.value.start == 0.0
        assert tw.state.value.end == 100.0
        assert tw.state.value.status == TransitionStatus.PENDING

    def test_create_with_config(self) -> None:
        """Create tween with custom config."""
        config = TweenConfig(duration_ms=500.0, easing=Easing.EASE_IN)
        tw = Tween.create(start=0.0, end=100.0, config=config)
        assert tw.config.duration_ms == 500.0

    def test_convenience_function(self) -> None:
        """Use convenience tween() function."""
        tw = tween(start=0.0, end=100.0, duration_ms=200.0)
        assert tw.config.duration_ms == 200.0

    def test_auto_interpolator_float(self) -> None:
        """Auto-detects float interpolator."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=300.0, easing=Easing.LINEAR),
        )
        tw.start()
        tw.update(150.0)  # Half of 300ms
        assert 40.0 <= tw.value <= 60.0

    def test_auto_interpolator_int(self) -> None:
        """Auto-detects int interpolator."""
        tw = Tween.create(start=0, end=100)
        tw.start()
        tw.update(150.0)
        assert isinstance(tw.value, int)

    def test_custom_interpolator(self) -> None:
        """Use custom interpolator."""

        def step_interp(a: str, b: str, t: float) -> str:
            return b if t >= 0.5 else a

        tw = Tween.create(
            start="off",
            end="on",
            interpolator=step_interp,
            config=TweenConfig(duration_ms=300.0, easing=Easing.LINEAR),
        )
        tw.start()
        tw.update(100.0)  # 1/3 of 300ms, eased < 0.5
        assert tw.value == "off"
        tw.update(100.0)  # 2/3 of 300ms, eased > 0.5
        assert tw.value == "on"


class TestTweenLifecycle:
    """Tests for Tween lifecycle (start, pause, resume, etc.)."""

    def test_start_transitions_to_running(self) -> None:
        """Start transitions from PENDING to RUNNING."""
        tw = Tween.create(start=0.0, end=100.0)
        assert tw.state.value.status == TransitionStatus.PENDING

        tw.start()
        assert tw.state.value.status == TransitionStatus.RUNNING  # type: ignore[comparison-overlap]

    def test_pause_transitions_to_paused(self) -> None:
        """Pause transitions from RUNNING to PAUSED."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.start()
        tw.pause()
        assert tw.state.value.status == TransitionStatus.PAUSED

    def test_resume_transitions_to_running(self) -> None:
        """Resume transitions from PAUSED to RUNNING."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.start()
        tw.pause()
        tw.resume()
        assert tw.state.value.status == TransitionStatus.RUNNING

    def test_cancel_stops_animation(self) -> None:
        """Cancel stops animation."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.start()
        tw.update(100.0)
        tw.cancel()
        assert tw.state.value.status == TransitionStatus.CANCELLED

    def test_reset_returns_to_pending(self) -> None:
        """Reset returns to PENDING state."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.start()
        tw.update(150.0)
        tw.reset()
        assert tw.state.value.status == TransitionStatus.PENDING
        assert tw.state.value.progress == 0.0
        assert tw.value == 0.0


class TestTweenUpdate:
    """Tests for Tween.update()."""

    def test_update_increments_progress(self) -> None:
        """Update increments progress."""
        tw = Tween.create(start=0.0, end=100.0, config=TweenConfig(duration_ms=100.0))
        tw.start()
        tw.update(50.0)  # 50% of 100ms
        assert abs(tw.progress - 0.5) < 0.01

    def test_update_interpolates_value(self) -> None:
        """Update interpolates value based on progress and easing."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, easing=Easing.LINEAR),
        )
        tw.start()
        tw.update(50.0)
        assert abs(tw.value - 50.0) < 0.01

    def test_update_completes_at_duration(self) -> None:
        """Animation completes at duration."""
        tw = Tween.create(start=0.0, end=100.0, config=TweenConfig(duration_ms=100.0))
        tw.start()
        tw.update(100.0)
        assert tw.is_complete
        assert tw.value == 100.0

    def test_update_clamps_at_complete(self) -> None:
        """Update doesn't overshoot after complete."""
        tw = Tween.create(start=0.0, end=100.0, config=TweenConfig(duration_ms=100.0))
        tw.start()
        tw.update(200.0)  # Double the duration
        assert tw.value == 100.0
        assert tw.progress == 1.0

    def test_update_no_change_when_not_running(self) -> None:
        """Update does nothing when not running."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.update(100.0)  # Not started
        assert tw.value == 0.0
        assert tw.progress == 0.0


class TestTweenEasing:
    """Tests for Tween easing behavior."""

    def test_ease_in_slow_start(self) -> None:
        """Ease-in starts slow."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, easing=Easing.EASE_IN),
        )
        tw.start()
        tw.update(25.0)  # 25% progress
        # With ease-in, value should be less than linear (25)
        assert tw.value < 25.0

    def test_ease_out_fast_start(self) -> None:
        """Ease-out starts fast."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, easing=Easing.EASE_OUT),
        )
        tw.start()
        tw.update(25.0)  # 25% progress
        # With ease-out, value should be more than linear (25)
        assert tw.value > 25.0

    def test_custom_easing_curve(self) -> None:
        """Use custom EasingCurve."""
        curve = EasingCurve(Easing.EASE_IN, power=3.0)
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, easing=curve),
        )
        tw.start()
        tw.update(50.0)  # 50% progress, cubic ease-in
        # 0.5^3 * 100 = 12.5
        assert abs(tw.value - 12.5) < 0.5


class TestTweenDelay:
    """Tests for Tween delay."""

    def test_delay_waits_before_starting(self) -> None:
        """Animation waits for delay before interpolating."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, delay_ms=50.0),
        )
        tw.start()
        tw.update(25.0)  # Still in delay
        assert tw.value == 0.0

        tw.update(50.0)  # Past delay, 25% into animation
        assert tw.value > 0.0


class TestTweenLooping:
    """Tests for Tween looping."""

    def test_no_loop_completes(self) -> None:
        """Default no-loop completes normally."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, loops=0),
        )
        tw.start()
        tw.update(100.0)
        assert tw.is_complete

    def test_loop_once(self) -> None:
        """Loop once repeats animation."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, loops=1),
        )
        tw.start()
        tw.update(100.0)  # First pass
        assert not tw.is_complete

        tw.update(100.0)  # Second pass
        assert tw.is_complete

    def test_yoyo_reverses(self) -> None:
        """Yoyo reverses direction on loop."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, loops=1, yoyo=True, easing=Easing.LINEAR),
        )
        tw.start()
        tw.update(100.0)  # Forward complete
        assert not tw.is_complete

        tw.update(50.0)  # Halfway back
        # Should be around 50 on the way back (with linear: exactly 50)
        assert 40 < tw.value < 60


class TestTweenSeek:
    """Tests for Tween.seek()."""

    def test_seek_to_progress(self) -> None:
        """Seek jumps to specific progress."""
        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0, easing=Easing.LINEAR),
        )
        tw.start()
        tw.seek(0.75)
        assert abs(tw.progress - 0.75) < 0.01
        assert abs(tw.value - 75.0) < 0.5


class TestTweenReverse:
    """Tests for Tween.reverse()."""

    def test_reverse_swaps_start_end(self) -> None:
        """Reverse swaps start and end values."""
        tw = Tween.create(start=0.0, end=100.0)
        tw.reverse()
        assert tw.state.value.start == 100.0
        assert tw.state.value.end == 0.0


class TestTweenCallback:
    """Tests for completion callback."""

    def test_on_complete_called(self) -> None:
        """on_complete callback is called when animation finishes."""
        completed = [False]

        def on_done(t: Tween[float]) -> None:
            completed[0] = True

        tw = Tween.create(
            start=0.0,
            end=100.0,
            config=TweenConfig(duration_ms=100.0),
            on_complete=on_done,
        )
        tw.start()
        tw.update(100.0)

        assert completed[0] is True


class TestTweenProperties:
    """Tests for Tween properties."""

    def test_is_complete_property(self) -> None:
        """is_complete property works."""
        tw = Tween.create(start=0.0, end=100.0, config=TweenConfig(duration_ms=100.0))
        assert tw.is_complete is False
        tw.start()
        tw.update(100.0)
        assert tw.is_complete is True

    def test_is_running_property(self) -> None:
        """is_running property works."""
        tw = Tween.create(start=0.0, end=100.0)
        assert tw.is_running is False
        tw.start()
        assert tw.is_running is True
        tw.pause()
        assert tw.is_running is False

    def test_value_property(self) -> None:
        """value property returns current value."""
        tw = Tween.create(start=0.0, end=100.0)
        assert tw.value == 0.0

    def test_progress_property(self) -> None:
        """progress property returns current progress."""
        tw = Tween.create(start=0.0, end=100.0)
        assert tw.progress == 0.0
