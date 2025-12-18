"""
Tests for Clock: Central time synchronization.

Wave 5 - Reality Wiring: Clock tests
"""

from __future__ import annotations

import pytest

from agents.i.reactive.wiring.clock import (
    Clock,
    ClockConfig,
    ClockState,
    create_clock,
    get_global_clock,
    reset_global_clock,
)


class TestClockState:
    """Tests for ClockState."""

    def test_clock_state_immutable(self) -> None:
        """ClockState should be immutable (frozen)."""
        state = ClockState(t=100.0, seed=42, frame=5)
        with pytest.raises(AttributeError):
            state.t = 200.0  # type: ignore[misc]

    def test_clock_state_seconds(self) -> None:
        """seconds property should convert ms to seconds."""
        state = ClockState(t=1500.0)
        assert state.seconds == 1.5

    def test_clock_state_entropy_seed_for(self) -> None:
        """entropy_seed_for should be deterministic."""
        state = ClockState(t=100.0, seed=42, frame=10)

        seed1 = state.entropy_seed_for("widget_1")
        seed2 = state.entropy_seed_for("widget_1")
        seed3 = state.entropy_seed_for("widget_2")

        # Same widget = same seed
        assert seed1 == seed2

        # Different widget = different seed
        assert seed1 != seed3

    def test_clock_state_defaults(self) -> None:
        """ClockState should have sensible defaults."""
        state = ClockState()

        assert state.t == 0.0
        assert state.seed == 0
        assert state.frame == 0
        assert state.delta == 0.0
        assert state.running is True
        assert state.rate == 1.0


class TestClockConfig:
    """Tests for ClockConfig."""

    def test_clock_config_defaults(self) -> None:
        """ClockConfig should have sensible defaults."""
        config = ClockConfig()

        assert config.fps == 60
        assert config.initial_seed == 42
        assert config.use_wall_time is True
        assert config.auto_start is True


class TestClock:
    """Tests for Clock."""

    def test_clock_create(self) -> None:
        """Clock.create should initialize correctly."""
        clock = Clock.create()

        assert clock.config is not None
        assert clock.state is not None
        assert clock.state.value.t == 0.0
        assert clock.state.value.frame == 0

    def test_clock_tick_advances_frame(self) -> None:
        """tick() should advance frame counter."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        state1 = clock.tick(override_delta=16.67)
        assert state1.frame == 1

        state2 = clock.tick(override_delta=16.67)
        assert state2.frame == 2

    def test_clock_tick_advances_time(self) -> None:
        """tick() should advance time."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        clock.tick(override_delta=100.0)
        assert clock.state.value.t == 100.0

        clock.tick(override_delta=50.0)
        assert clock.state.value.t == 150.0

    def test_clock_tick_with_rate(self) -> None:
        """tick() should respect playback rate."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        clock.set_rate(2.0)  # Double speed
        clock.tick(override_delta=100.0)

        # 100ms * 2.0 rate = 200ms
        assert clock.state.value.t == 200.0

    def test_clock_tick_to(self) -> None:
        """tick_to() should set time directly."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        clock.tick_to(500.0)
        assert clock.state.value.t == 500.0

        clock.tick_to(1000.0)
        assert clock.state.value.t == 1000.0

    def test_clock_pause_resume(self) -> None:
        """pause() and resume() should control running state."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        assert clock.state.value.running is True

        clock.pause()
        assert clock.state.value.running is False

        # Tick should not advance when paused
        state_before = clock.state.value
        clock.tick(override_delta=100.0)
        assert clock.state.value.t == state_before.t

        clock.resume()
        assert clock.state.value.running is True

        # Tick should advance again
        clock.tick(override_delta=100.0)
        assert clock.state.value.t > state_before.t

    def test_clock_reset(self) -> None:
        """reset() should return to initial state."""
        clock = Clock.create(ClockConfig(use_wall_time=False, initial_seed=123))

        # Advance clock
        clock.tick(override_delta=100.0)
        clock.tick(override_delta=100.0)
        clock.set_rate(2.0)

        assert clock.state.value.t > 0.0
        assert clock.state.value.frame > 0

        # Reset
        clock.reset()

        assert clock.state.value.t == 0.0
        assert clock.state.value.frame == 0
        assert clock.state.value.seed == 123
        assert clock.state.value.rate == 1.0

    def test_clock_set_rate(self) -> None:
        """set_rate() should update playback rate."""
        clock = Clock.create()

        clock.set_rate(0.5)
        assert clock.state.value.rate == 0.5

        clock.set_rate(3.0)
        assert clock.state.value.rate == 3.0

    def test_clock_set_rate_clamped(self) -> None:
        """set_rate() should clamp to reasonable range."""
        clock = Clock.create()

        clock.set_rate(0.01)
        assert clock.state.value.rate == 0.1  # Minimum

        clock.set_rate(100.0)
        assert clock.state.value.rate == 10.0  # Maximum

    def test_clock_set_seed(self) -> None:
        """set_seed() should update entropy seed."""
        clock = Clock.create()

        clock.set_seed(999)
        assert clock.state.value.seed == 999

    def test_clock_subscribe(self) -> None:
        """subscribe() should receive tick updates."""
        clock = Clock.create(ClockConfig(use_wall_time=False))
        received: list[ClockState] = []

        unsub = clock.subscribe(lambda s: received.append(s))

        clock.tick(override_delta=16.67)
        clock.tick(override_delta=16.67)

        assert len(received) == 2
        assert received[0].frame == 1
        assert received[1].frame == 2

        # Unsubscribe
        unsub()
        clock.tick(override_delta=16.67)
        assert len(received) == 2  # No more updates

    def test_clock_snapshot(self) -> None:
        """snapshot() should return immutable state."""
        clock = Clock.create(ClockConfig(use_wall_time=False))

        clock.tick(override_delta=100.0)
        snapshot = clock.snapshot()

        assert snapshot.t == 100.0
        assert snapshot.frame == 1

        # Modify clock
        clock.tick(override_delta=100.0)

        # Snapshot should be unchanged
        assert snapshot.t == 100.0
        assert snapshot.frame == 1


class TestCreateClock:
    """Tests for create_clock factory function."""

    def test_create_clock_defaults(self) -> None:
        """create_clock() should work with defaults."""
        clock = create_clock()

        assert clock.config.fps == 60
        assert clock.config.initial_seed == 42

    def test_create_clock_custom(self) -> None:
        """create_clock() should accept custom parameters."""
        clock = create_clock(fps=30, seed=999, use_wall_time=False, auto_start=False)

        assert clock.config.fps == 30
        assert clock.config.initial_seed == 999
        assert clock.config.use_wall_time is False
        assert clock.config.auto_start is False
        assert clock.state.value.running is False


class TestGlobalClock:
    """Tests for global clock singleton."""

    def test_get_global_clock(self) -> None:
        """get_global_clock() should return singleton."""
        reset_global_clock()

        clock1 = get_global_clock()
        clock2 = get_global_clock()

        assert clock1 is clock2

    def test_reset_global_clock(self) -> None:
        """reset_global_clock() should create new instance."""
        clock1 = get_global_clock()
        clock1.tick(override_delta=100.0)

        clock2 = reset_global_clock()

        assert clock2 is not clock1
        assert clock2.state.value.t == 0.0


class TestClockDeterminism:
    """Tests for deterministic behavior."""

    def test_same_inputs_same_output(self) -> None:
        """Same tick sequence should produce same state."""
        clock1 = Clock.create(ClockConfig(use_wall_time=False, initial_seed=42))
        clock2 = Clock.create(ClockConfig(use_wall_time=False, initial_seed=42))

        # Same tick sequence
        for _ in range(10):
            clock1.tick(override_delta=16.67)
            clock2.tick(override_delta=16.67)

        # Should be identical
        assert clock1.state.value.t == clock2.state.value.t
        assert clock1.state.value.frame == clock2.state.value.frame
        assert clock1.state.value.seed == clock2.state.value.seed

    def test_entropy_seed_deterministic(self) -> None:
        """Widget entropy seeds should be deterministic."""
        clock = Clock.create(ClockConfig(use_wall_time=False, initial_seed=42))

        clock.tick(override_delta=100.0)
        state = clock.state.value

        seed1 = state.entropy_seed_for("widget_a")
        seed2 = state.entropy_seed_for("widget_a")

        assert seed1 == seed2

        # Recreate with same params
        clock2 = Clock.create(ClockConfig(use_wall_time=False, initial_seed=42))
        clock2.tick(override_delta=100.0)

        seed3 = clock2.state.value.entropy_seed_for("widget_a")
        assert seed1 == seed3
