"""Tests for FrameScheduler."""

import pytest
from agents.i.reactive.animation.frame import (
    FrameScheduler,
    FrameSchedulerConfig,
    FrameSchedulerState,
    create_frame_scheduler,
)
from agents.i.reactive.wiring.clock import Clock, ClockConfig, ClockState


class TestFrameSchedulerConfig:
    """Tests for FrameSchedulerConfig."""

    def test_default_config(self) -> None:
        """Default config uses 60fps."""
        config = FrameSchedulerConfig()
        assert config.fps == 60
        assert config.max_delta_ms == 100.0
        assert config.skip_frames is True
        assert config.max_skip == 3

    def test_frame_duration(self) -> None:
        """Frame duration calculated correctly."""
        config60 = FrameSchedulerConfig(fps=60)
        config30 = FrameSchedulerConfig(fps=30)
        config120 = FrameSchedulerConfig(fps=120)

        assert abs(config60.frame_duration_ms - 16.67) < 0.1
        assert abs(config30.frame_duration_ms - 33.33) < 0.1
        assert abs(config120.frame_duration_ms - 8.33) < 0.1


class TestFrameSchedulerCreation:
    """Tests for FrameScheduler creation."""

    def test_create_default(self) -> None:
        """Create scheduler with defaults."""
        scheduler = FrameScheduler.create()
        assert scheduler.config.fps == 60
        assert scheduler.state.value.running is True

    def test_create_with_config(self) -> None:
        """Create scheduler with custom config."""
        config = FrameSchedulerConfig(fps=30, max_delta_ms=50.0)
        scheduler = FrameScheduler.create(config=config)
        assert scheduler.config.fps == 30
        assert scheduler.config.max_delta_ms == 50.0

    def test_create_convenience(self) -> None:
        """Create scheduler with convenience function."""
        scheduler = create_frame_scheduler(fps=120)
        assert scheduler.config.fps == 120


class TestFrameCallbacks:
    """Tests for frame callback registration."""

    def test_register_callback(self) -> None:
        """Register a callback."""
        scheduler = FrameScheduler.create()
        callback_id = scheduler.request_frame(lambda d, f, t: None)
        assert callback_id > 0
        assert scheduler.callback_count == 1

    def test_register_multiple_callbacks(self) -> None:
        """Register multiple callbacks."""
        scheduler = FrameScheduler.create()
        scheduler.request_frame(lambda d, f, t: None)
        scheduler.request_frame(lambda d, f, t: None)
        scheduler.request_frame(lambda d, f, t: None)
        assert scheduler.callback_count == 3

    def test_cancel_callback(self) -> None:
        """Cancel a registered callback."""
        scheduler = FrameScheduler.create()
        callback_id = scheduler.request_frame(lambda d, f, t: None)
        assert scheduler.callback_count == 1

        result = scheduler.cancel_frame(callback_id)
        assert result is True
        assert scheduler.callback_count == 0

    def test_cancel_nonexistent(self) -> None:
        """Cancel returns False for non-existent callback."""
        scheduler = FrameScheduler.create()
        result = scheduler.cancel_frame(999)
        assert result is False

    def test_unique_callback_ids(self) -> None:
        """Each callback gets a unique ID."""
        scheduler = FrameScheduler.create()
        id1 = scheduler.request_frame(lambda d, f, t: None)
        id2 = scheduler.request_frame(lambda d, f, t: None)
        id3 = scheduler.request_frame(lambda d, f, t: None)
        assert id1 != id2 != id3


class TestFrameProcessing:
    """Tests for process_frame."""

    def test_process_frame_basic(self) -> None:
        """Process frame updates state."""
        scheduler = FrameScheduler.create()
        state = scheduler.process_frame(delta_ms=16.67)
        assert state.frame > 0
        assert state.elapsed_ms > 0

    def test_process_frame_with_clock_state(self) -> None:
        """Process frame from ClockState."""
        scheduler = FrameScheduler.create()
        clock_state = ClockState(
            t=100.0,
            seed=42,
            frame=5,
            delta=16.67,
            running=True,
        )
        state = scheduler.process_frame(clock_state=clock_state)
        assert state.frame == 5
        assert state.elapsed_ms == 100.0

    def test_callbacks_invoked(self) -> None:
        """Callbacks are invoked on process_frame."""
        scheduler = FrameScheduler.create()
        results: list[tuple[float, int, float]] = []

        def callback(delta: float, frame: int, t: float) -> None:
            results.append((delta, frame, t))

        scheduler.request_frame(callback)
        scheduler.process_frame(delta_ms=16.67)

        assert len(results) == 1
        assert results[0][0] == 16.67

    def test_multiple_callbacks_invoked(self) -> None:
        """Multiple callbacks all invoked."""
        scheduler = FrameScheduler.create()
        invoked = [False, False, False]

        scheduler.request_frame(lambda d, f, t: invoked.__setitem__(0, True))
        scheduler.request_frame(lambda d, f, t: invoked.__setitem__(1, True))
        scheduler.request_frame(lambda d, f, t: invoked.__setitem__(2, True))

        scheduler.process_frame(delta_ms=16.67)

        assert all(invoked)

    def test_delta_clamped(self) -> None:
        """Large deltas are clamped."""
        scheduler = FrameScheduler.create(
            config=FrameSchedulerConfig(max_delta_ms=50.0)
        )
        received_delta: list[float] = []
        scheduler.request_frame(lambda d, f, t: received_delta.append(d))

        scheduler.process_frame(delta_ms=200.0)

        assert received_delta[0] == 50.0


class TestFrameSchedulerPauseResume:
    """Tests for pause/resume."""

    def test_pause(self) -> None:
        """Pause stops frame processing."""
        scheduler = FrameScheduler.create()
        scheduler.pause()
        assert scheduler.state.value.running is False

    def test_resume(self) -> None:
        """Resume restarts frame processing."""
        scheduler = FrameScheduler.create()
        scheduler.pause()
        scheduler.resume()
        assert scheduler.state.value.running is True

    def test_paused_no_callbacks(self) -> None:
        """Paused scheduler doesn't invoke callbacks."""
        scheduler = FrameScheduler.create()
        invoked = [False]
        scheduler.request_frame(lambda d, f, t: invoked.__setitem__(0, True))

        scheduler.pause()
        scheduler.process_frame(delta_ms=16.67)

        assert invoked[0] is False


class TestFrameSchedulerReset:
    """Tests for reset."""

    def test_reset_clears_state(self) -> None:
        """Reset clears scheduler state."""
        scheduler = FrameScheduler.create()
        scheduler.request_frame(lambda d, f, t: None)
        scheduler.process_frame(delta_ms=100.0)

        scheduler.reset()

        assert scheduler.state.value.frame == 0
        assert scheduler.state.value.elapsed_ms == 0.0
        assert scheduler.callback_count == 0


class TestFrameSchedulerClockIntegration:
    """Tests for Clock integration."""

    def test_connect_to_clock(self) -> None:
        """Scheduler can connect to Clock."""
        clock = Clock.create(ClockConfig(use_wall_time=False, auto_start=True))
        scheduler = FrameScheduler.create(clock=clock)

        results: list[int] = []
        scheduler.request_frame(lambda d, f, t: results.append(f))

        clock.tick(override_delta=16.67)

        assert len(results) == 1

    def test_auto_update_from_clock(self) -> None:
        """Scheduler updates automatically from Clock ticks."""
        clock = Clock.create(ClockConfig(use_wall_time=False, auto_start=True))
        scheduler = FrameScheduler.create(clock=clock)

        frame_count = [0]
        scheduler.request_frame(
            lambda d, f, t: frame_count.__setitem__(0, frame_count[0] + 1)
        )

        # Tick clock multiple times
        for _ in range(5):
            clock.tick(override_delta=16.67)

        assert frame_count[0] == 5


class TestFrameSchedulerDispose:
    """Tests for dispose."""

    def test_dispose_clears_callbacks(self) -> None:
        """Dispose clears all callbacks."""
        scheduler = FrameScheduler.create()
        scheduler.request_frame(lambda d, f, t: None)
        scheduler.request_frame(lambda d, f, t: None)

        scheduler.dispose()

        assert scheduler.callback_count == 0

    def test_dispose_unsubscribes_clock(self) -> None:
        """Dispose unsubscribes from clock."""
        clock = Clock.create(ClockConfig(use_wall_time=False, auto_start=True))
        scheduler = FrameScheduler.create(clock=clock)

        invoked = [False]
        scheduler.request_frame(lambda d, f, t: invoked.__setitem__(0, True))

        scheduler.dispose()
        clock.tick(override_delta=16.67)

        # Callback should not be invoked after dispose
        assert invoked[0] is False
