"""Tests for Spring dynamics."""

import pytest
from agents.i.reactive.animation.spring import (
    Spring,
    SpringConfig,
    SpringState,
    SpringVec2,
    spring,
)
from agents.i.reactive.animation.tween import TransitionStatus


class TestSpringConfig:
    """Tests for SpringConfig."""

    def test_default_config(self) -> None:
        """Default config has reasonable values."""
        config = SpringConfig()
        assert config.stiffness == 170.0
        assert config.damping == 26.0
        assert config.mass == 1.0

    def test_preset_gentle(self) -> None:
        """Gentle preset has low stiffness."""
        config = SpringConfig.gentle()
        assert config.stiffness == 120.0
        assert config.damping == 14.0

    def test_preset_wobbly(self) -> None:
        """Wobbly preset has high stiffness, low damping."""
        config = SpringConfig.wobbly()
        assert config.stiffness == 180.0
        assert config.damping == 12.0

    def test_preset_stiff(self) -> None:
        """Stiff preset has high stiffness."""
        config = SpringConfig.stiff()
        assert config.stiffness == 300.0
        assert config.damping == 20.0

    def test_preset_slow(self) -> None:
        """Slow preset is overdamped."""
        config = SpringConfig.slow()
        assert config.stiffness == 120.0
        assert config.damping == 30.0

    def test_preset_bouncy(self) -> None:
        """Bouncy preset has low damping."""
        config = SpringConfig.bouncy()
        assert config.damping == 8.0


class TestSpringCreation:
    """Tests for Spring creation."""

    def test_create_basic(self) -> None:
        """Create basic spring."""
        s = Spring.create(initial=0.0, target=100.0)
        assert s.value == 0.0
        assert s.target == 100.0
        assert s.state.value.status == TransitionStatus.PENDING

    def test_create_with_config(self) -> None:
        """Create spring with custom config."""
        config = SpringConfig(stiffness=200.0, damping=10.0)
        s = Spring.create(initial=0.0, target=100.0, config=config)
        assert s.config.stiffness == 200.0
        assert s.config.damping == 10.0

    def test_convenience_function(self) -> None:
        """Use convenience spring() function."""
        s = spring(initial=0.0, target=100.0, stiffness=150.0, damping=20.0)
        assert s.config.stiffness == 150.0
        assert s.config.damping == 20.0

    def test_create_at_target(self) -> None:
        """Creating spring already at target marks it at rest."""
        s = Spring.create(initial=100.0, target=100.0)
        assert s.state.value.at_rest is True


class TestSpringLifecycle:
    """Tests for Spring lifecycle."""

    def test_start_transitions_to_running(self) -> None:
        """Start transitions from PENDING to RUNNING."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        assert s.state.value.status == TransitionStatus.RUNNING

    def test_start_at_target_completes(self) -> None:
        """Start at target completes immediately."""
        s = Spring.create(initial=100.0, target=100.0)
        s.start()
        assert s.is_complete

    def test_pause_stops_animation(self) -> None:
        """Pause stops spring animation."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)
        s.pause()
        assert s.state.value.status == TransitionStatus.PAUSED

    def test_resume_continues_animation(self) -> None:
        """Resume continues spring animation."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.pause()
        s.resume()
        assert s.is_running

    def test_reset_returns_to_initial(self) -> None:
        """Reset returns spring to initial state."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)
        s.reset()
        assert s.state.value.status == TransitionStatus.PENDING
        assert s.velocity == 0.0


class TestSpringUpdate:
    """Tests for Spring.update()."""

    def test_update_moves_towards_target(self) -> None:
        """Update moves value towards target."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)  # One frame
        assert s.value > 0.0
        assert s.value < 100.0

    def test_update_gains_velocity(self) -> None:
        """Update increases velocity initially."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)
        assert s.velocity > 0.0

    def test_spring_eventually_settles(self) -> None:
        """Spring eventually settles at target."""
        s = Spring.create(initial=0.0, target=100.0, config=SpringConfig.stiff())
        s.start()

        # Simulate many frames
        for _ in range(100):
            if s.is_complete:
                break
            s.update(16.67)

        assert s.is_complete
        assert abs(s.value - 100.0) < 0.01

    def test_spring_overshoots_with_low_damping(self) -> None:
        """Low damping causes overshoot."""
        s = Spring.create(
            initial=0.0,
            target=100.0,
            config=SpringConfig(stiffness=200.0, damping=5.0),
        )
        s.start()

        max_value = 0.0
        for _ in range(200):
            s.update(16.67)
            max_value = max(max_value, s.value)
            if s.is_complete:
                break

        # Should have overshot past 100
        assert max_value > 100.0

    def test_no_update_when_not_running(self) -> None:
        """Update does nothing when not running."""
        s = Spring.create(initial=0.0, target=100.0)
        initial_value = s.value
        s.update(16.67)  # Not started
        assert s.value == initial_value


class TestSpringTarget:
    """Tests for set_target() - spring interruptibility."""

    def test_set_target_changes_target(self) -> None:
        """set_target changes the target value."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)

        s.set_target(50.0)
        assert s.target == 50.0

    def test_set_target_preserves_velocity(self) -> None:
        """set_target preserves current velocity."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()
        s.update(16.67)
        velocity_before = s.velocity

        s.set_target(50.0)
        assert s.velocity == velocity_before

    def test_mid_animation_target_change(self) -> None:
        """Changing target mid-animation creates smooth redirect."""
        s = Spring.create(initial=0.0, target=100.0, config=SpringConfig.stiff())
        s.start()

        # Move towards 100
        for _ in range(20):
            s.update(16.67)

        mid_value = s.value
        assert mid_value > 0

        # Change direction
        s.set_target(0.0)

        # Continue animation
        for _ in range(100):
            if s.is_complete:
                break
            s.update(16.67)

        # Should have returned to 0
        assert abs(s.value - 0.0) < 1.0


class TestSpringSetValue:
    """Tests for set_value() - direct value manipulation."""

    def test_set_value_updates_position(self) -> None:
        """set_value directly sets current position."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()

        s.set_value(50.0)
        assert s.value == 50.0

    def test_set_value_with_velocity(self) -> None:
        """set_value can set initial velocity (e.g., from drag)."""
        s = Spring.create(initial=0.0, target=100.0)
        s.start()

        s.set_value(50.0, velocity=200.0)
        assert s.value == 50.0
        assert s.velocity == 200.0


class TestSpringProperties:
    """Tests for Spring properties."""

    def test_is_complete_property(self) -> None:
        """is_complete works correctly."""
        s = Spring.create(initial=100.0, target=100.0)
        s.start()
        assert s.is_complete is True

    def test_is_running_property(self) -> None:
        """is_running works correctly."""
        s = Spring.create(initial=0.0, target=100.0)
        assert s.is_running is False
        s.start()
        assert s.is_running is True

    def test_value_property(self) -> None:
        """value property returns current value."""
        s = Spring.create(initial=42.0, target=100.0)
        assert s.value == 42.0

    def test_velocity_property(self) -> None:
        """velocity property returns current velocity."""
        s = Spring.create(initial=0.0, target=100.0)
        assert s.velocity == 0.0

    def test_target_property(self) -> None:
        """target property returns current target."""
        s = Spring.create(initial=0.0, target=100.0)
        assert s.target == 100.0


class TestSpringCallback:
    """Tests for Spring completion callback."""

    def test_on_complete_called(self) -> None:
        """on_complete called when spring settles."""
        completed = [False]

        def on_done(sp: Spring) -> None:
            completed[0] = True

        s = Spring.create(
            initial=0.0,
            target=100.0,
            config=SpringConfig.stiff(),
            on_complete=on_done,
        )
        s.start()

        for _ in range(100):
            if s.is_complete:
                break
            s.update(16.67)

        assert completed[0] is True


class TestSpringClamping:
    """Tests for Spring clamping behavior."""

    def test_clamp_prevents_overshoot(self) -> None:
        """Clamp config prevents overshoot."""
        s = Spring.create(
            initial=0.0,
            target=100.0,
            config=SpringConfig(stiffness=200.0, damping=5.0, clamp=True),
        )
        s.start()

        for _ in range(100):
            s.update(16.67)
            assert s.value <= 100.0
            assert s.value >= 0.0
            if s.is_complete:
                break


class TestSpringVec2:
    """Tests for 2D spring animation."""

    def test_create_vec2(self) -> None:
        """Create 2D spring."""
        s = SpringVec2.create(initial=(0.0, 0.0), target=(100.0, 50.0))
        assert s.value == (0.0, 0.0)

    def test_start_both(self) -> None:
        """Start starts both springs."""
        s = SpringVec2.create(initial=(0.0, 0.0), target=(100.0, 50.0))
        s.start()
        assert s.x.is_running
        assert s.y.is_running

    def test_update_returns_tuple(self) -> None:
        """Update returns (x, y) tuple."""
        s = SpringVec2.create(
            initial=(0.0, 0.0),
            target=(100.0, 50.0),
            config=SpringConfig.stiff(),
        )
        s.start()
        value = s.update(16.67)
        assert isinstance(value, tuple)
        assert len(value) == 2
        assert value[0] > 0.0  # x moved
        assert value[1] > 0.0  # y moved

    def test_set_target_vec2(self) -> None:
        """set_target updates both springs."""
        s = SpringVec2.create(initial=(0.0, 0.0), target=(100.0, 50.0))
        s.start()
        s.update(16.67)

        s.set_target((50.0, 25.0))
        assert s.x.target == 50.0
        assert s.y.target == 25.0

    def test_is_complete_vec2(self) -> None:
        """is_complete requires both springs to settle."""
        s = SpringVec2.create(
            initial=(0.0, 0.0),
            target=(100.0, 50.0),
            config=SpringConfig.stiff(),
        )
        s.start()

        for _ in range(100):
            s.update(16.67)
            if s.is_complete:
                break

        assert s.is_complete
        assert abs(s.value[0] - 100.0) < 0.1
        assert abs(s.value[1] - 50.0) < 0.1
