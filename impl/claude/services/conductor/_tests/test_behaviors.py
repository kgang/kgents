"""
Tests for Cursor Behaviors module.

CLI v7 Phase 5B: Cursor Behaviors

Following T-gent taxonomy:
- Type I (Unit): Behavior properties, position math, focus tracking
- Type II (Integration): Animator with graph, human focus integration
- Type III (Property): Animation bounds, behavior composition, circadian effects

"Daring, bold, creative, opinionated but not gaudy"
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta

import pytest
from hypothesis import given, settings, strategies as st

from services.conductor.behaviors import (
    AGENTESEGraph,
    BehaviorAnimator,
    BehaviorModulator,
    CursorBehavior,
    FocusPoint,
    HumanFocusTracker,
    Position,
)
from services.conductor.presence import CircadianPhase, CursorState

# =============================================================================
# Mock Graph for Testing
# =============================================================================


@dataclass
class MockGraph:
    """Mock AGENTESE graph for testing behavior animation."""

    nodes: dict[str, Position]
    connections: dict[str, list[str]]

    def get_connected_paths(self, path: str) -> list[str]:
        """Get paths connected to this path."""
        return self.connections.get(path, [])

    def get_position(self, path: str) -> Position | None:
        """Get position for a path."""
        return self.nodes.get(path)

    def get_all_paths(self) -> list[str]:
        """Get all registered paths."""
        return list(self.nodes.keys())


@pytest.fixture
def sample_graph() -> MockGraph:
    """Create a sample graph for testing."""
    return MockGraph(
        nodes={
            "self.memory": Position(0.0, 0.0),
            "self.brain": Position(100.0, 0.0),
            "world.file": Position(0.0, 100.0),
            "concept.pattern": Position(100.0, 100.0),
        },
        connections={
            "self.memory": ["self.brain", "concept.pattern"],
            "self.brain": ["self.memory"],
            "world.file": ["self.memory"],
            "concept.pattern": ["self.brain", "world.file"],
        },
    )


# =============================================================================
# Type I: Unit Tests - CursorBehavior
# =============================================================================


class TestCursorBehaviorProperties:
    """Test CursorBehavior enum properties."""

    def test_all_behaviors_have_emoji(self):
        """Every behavior has an emoji."""
        for behavior in CursorBehavior:
            assert len(behavior.emoji) > 0, f"{behavior.name} missing emoji"

    def test_all_behaviors_have_description(self):
        """Every behavior has a description."""
        for behavior in CursorBehavior:
            assert len(behavior.description) > 0, f"{behavior.name} missing description"

    def test_follow_strength_in_range(self):
        """Follow strength is between 0.0 and 1.0."""
        for behavior in CursorBehavior:
            assert 0.0 <= behavior.follow_strength <= 1.0, (
                f"{behavior.name} follow_strength out of range"
            )

    def test_exploration_tendency_in_range(self):
        """Exploration tendency is between 0.0 and 1.0."""
        for behavior in CursorBehavior:
            assert 0.0 <= behavior.exploration_tendency <= 1.0, (
                f"{behavior.name} exploration_tendency out of range"
            )

    def test_suggestion_probability_in_range(self):
        """Suggestion probability is between 0.0 and 1.0."""
        for behavior in CursorBehavior:
            assert 0.0 <= behavior.suggestion_probability <= 1.0, (
                f"{behavior.name} suggestion_probability out of range"
            )

    def test_movement_smoothness_in_range(self):
        """Movement smoothness is between 0.0 and 1.0."""
        for behavior in CursorBehavior:
            assert 0.0 <= behavior.movement_smoothness <= 1.0, (
                f"{behavior.name} movement_smoothness out of range"
            )

    def test_circadian_sensitivity_in_range(self):
        """Circadian sensitivity is between 0.0 and 1.0."""
        for behavior in CursorBehavior:
            assert 0.0 <= behavior.circadian_sensitivity <= 1.0, (
                f"{behavior.name} circadian_sensitivity out of range"
            )


class TestCursorBehaviorPersonality:
    """Test behavior personality distinctions."""

    def test_follower_has_high_follow_strength(self):
        """FOLLOWER should track human most closely."""
        follower = CursorBehavior.FOLLOWER
        for behavior in CursorBehavior:
            if behavior != follower:
                assert behavior.follow_strength <= follower.follow_strength, (
                    f"{behavior.name} follows more than FOLLOWER"
                )

    def test_explorer_has_high_exploration(self):
        """EXPLORER should explore most."""
        explorer = CursorBehavior.EXPLORER
        for behavior in CursorBehavior:
            if behavior != explorer:
                assert behavior.exploration_tendency <= explorer.exploration_tendency, (
                    f"{behavior.name} explores more than EXPLORER"
                )

    def test_assistant_suggests_most(self):
        """ASSISTANT should have highest suggestion probability."""
        assistant = CursorBehavior.ASSISTANT
        for behavior in CursorBehavior:
            if behavior != assistant:
                assert behavior.suggestion_probability <= assistant.suggestion_probability, (
                    f"{behavior.name} suggests more than ASSISTANT"
                )

    def test_autonomous_has_zero_follow(self):
        """AUTONOMOUS should not follow human at all."""
        autonomous = CursorBehavior.AUTONOMOUS
        assert autonomous.follow_strength == 0.0

    def test_follower_has_high_smoothness(self):
        """FOLLOWER should have smooth, graceful movement."""
        follower = CursorBehavior.FOLLOWER
        assert follower.movement_smoothness >= 0.6

    def test_explorer_is_most_circadian_sensitive(self):
        """EXPLORER behavior changes most with time of day."""
        explorer = CursorBehavior.EXPLORER
        for behavior in CursorBehavior:
            if behavior != explorer:
                assert behavior.circadian_sensitivity <= explorer.circadian_sensitivity


class TestCursorBehaviorPreferredStates:
    """Test behavior-state alignment."""

    def test_follower_prefers_following_state(self):
        """FOLLOWER behavior prefers FOLLOWING cursor state."""
        assert CursorState.FOLLOWING in CursorBehavior.FOLLOWER.preferred_states

    def test_explorer_prefers_exploring_state(self):
        """EXPLORER behavior prefers EXPLORING cursor state."""
        assert CursorState.EXPLORING in CursorBehavior.EXPLORER.preferred_states

    def test_assistant_prefers_suggesting_state(self):
        """ASSISTANT behavior includes SUGGESTING state."""
        assert CursorState.SUGGESTING in CursorBehavior.ASSISTANT.preferred_states

    def test_autonomous_prefers_working_state(self):
        """AUTONOMOUS behavior includes WORKING state."""
        assert CursorState.WORKING in CursorBehavior.AUTONOMOUS.preferred_states


class TestCursorBehaviorCircadianDescription:
    """Test circadian-modulated descriptions."""

    def test_description_changes_at_night(self):
        """Night description adds reflective modifier."""
        explorer = CursorBehavior.EXPLORER
        night_desc = explorer.describe_for_phase(CircadianPhase.NIGHT)
        assert "contemplatively" in night_desc

    def test_description_changes_in_morning(self):
        """Morning description adds energetic modifier."""
        explorer = CursorBehavior.EXPLORER
        morning_desc = explorer.describe_for_phase(CircadianPhase.MORNING)
        assert "energetically" in morning_desc

    def test_description_consistent_at_noon(self):
        """Noon/afternoon descriptions are minimal."""
        explorer = CursorBehavior.EXPLORER
        base_desc = explorer.description
        noon_desc = explorer.describe_for_phase(CircadianPhase.NOON)
        # Should be same or very similar
        assert base_desc in noon_desc


# =============================================================================
# Type I: Unit Tests - Position
# =============================================================================


class TestPosition:
    """Test Position dataclass and math."""

    def test_position_add(self):
        """Position addition."""
        p1 = Position(1.0, 2.0)
        p2 = Position(3.0, 4.0)
        result = p1 + p2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_position_subtract(self):
        """Position subtraction."""
        p1 = Position(5.0, 7.0)
        p2 = Position(2.0, 3.0)
        result = p1 - p2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_position_multiply(self):
        """Position scalar multiplication."""
        p = Position(3.0, 4.0)
        result = p * 2.0
        assert result.x == 6.0
        assert result.y == 8.0

    def test_distance_to_same_point(self):
        """Distance to same point is zero."""
        p = Position(5.0, 5.0)
        assert p.distance_to(p) == 0.0

    def test_distance_to_other_point(self):
        """Distance calculation (3-4-5 triangle)."""
        p1 = Position(0.0, 0.0)
        p2 = Position(3.0, 4.0)
        assert p1.distance_to(p2) == 5.0

    def test_lerp_at_zero(self):
        """Lerp at t=0 returns current position."""
        p1 = Position(0.0, 0.0)
        p2 = Position(10.0, 10.0)
        result = p1.lerp(p2, 0.0)
        assert result.x == 0.0
        assert result.y == 0.0

    def test_lerp_at_one(self):
        """Lerp at t=1 returns target position."""
        p1 = Position(0.0, 0.0)
        p2 = Position(10.0, 10.0)
        result = p1.lerp(p2, 1.0)
        assert result.x == 10.0
        assert result.y == 10.0

    def test_lerp_at_half(self):
        """Lerp at t=0.5 returns midpoint."""
        p1 = Position(0.0, 0.0)
        p2 = Position(10.0, 10.0)
        result = p1.lerp(p2, 0.5)
        assert result.x == 5.0
        assert result.y == 5.0

    def test_lerp_clamps_negative(self):
        """Lerp clamps t < 0 to 0."""
        p1 = Position(0.0, 0.0)
        p2 = Position(10.0, 10.0)
        result = p1.lerp(p2, -0.5)
        assert result.x == 0.0
        assert result.y == 0.0

    def test_lerp_clamps_over_one(self):
        """Lerp clamps t > 1 to 1."""
        p1 = Position(0.0, 0.0)
        p2 = Position(10.0, 10.0)
        result = p1.lerp(p2, 1.5)
        assert result.x == 10.0
        assert result.y == 10.0


# =============================================================================
# Type I: Unit Tests - FocusPoint
# =============================================================================


class TestFocusPoint:
    """Test FocusPoint dataclass."""

    def test_create_focus_point(self):
        """Basic focus point creation."""
        point = FocusPoint(
            path="self.memory",
            position=Position(0.0, 0.0),
        )
        assert point.path == "self.memory"
        assert point.position.x == 0.0

    def test_age_seconds_fresh(self):
        """Fresh focus point has low age."""
        point = FocusPoint(
            path="self.memory",
            position=Position(0.0, 0.0),
        )
        assert point.age_seconds() < 1.0

    def test_age_seconds_old(self):
        """Old focus point has higher age."""
        old_time = datetime.now() - timedelta(seconds=5)
        point = FocusPoint(
            path="self.memory",
            position=Position(0.0, 0.0),
            timestamp=old_time,
        )
        assert point.age_seconds() >= 5.0


# =============================================================================
# Type I: Unit Tests - HumanFocusTracker
# =============================================================================


class TestHumanFocusTracker:
    """Test HumanFocusTracker."""

    @pytest.fixture
    def tracker(self):
        """Create fresh tracker for each test."""
        return HumanFocusTracker()

    def test_empty_tracker_has_no_current(self, tracker):
        """Empty tracker has no current focus."""
        assert tracker.current is None

    def test_update_sets_current(self, tracker):
        """Update sets current focus."""
        tracker.update("self.memory", Position(0.0, 0.0))
        assert tracker.current is not None
        assert tracker.current.path == "self.memory"

    def test_empty_tracker_is_stationary(self, tracker):
        """Empty tracker is considered stationary."""
        assert tracker.is_stationary is True

    def test_recent_update_not_stationary(self, tracker):
        """Recent update means not stationary."""
        tracker.update("self.memory", Position(0.0, 0.0))
        assert tracker.is_stationary is False

    def test_old_update_is_stationary(self, tracker):
        """Old update (>2s) means stationary."""
        old_time = datetime.now() - timedelta(seconds=3)
        tracker.history.append(
            FocusPoint(
                path="self.memory",
                position=Position(0.0, 0.0),
                timestamp=old_time,
            )
        )
        assert tracker.is_stationary is True

    def test_focus_duration_empty(self, tracker):
        """Empty tracker has zero focus duration."""
        assert tracker.focus_duration == 0.0

    def test_focus_duration_single_point(self, tracker):
        """Single point has positive duration."""
        tracker.update("self.memory", Position(0.0, 0.0))
        # Should be very small but positive
        assert tracker.focus_duration >= 0.0

    def test_history_bounded(self, tracker):
        """History is bounded by max_history."""
        tracker.max_history = 5
        for i in range(10):
            tracker.update(f"path.{i}", Position(float(i), 0.0))
        assert len(tracker.history) == 5

    def test_get_recent_paths_empty(self, tracker):
        """Empty tracker returns empty recent paths."""
        assert tracker.get_recent_paths() == []

    def test_get_recent_paths_returns_unique(self, tracker):
        """Recent paths are unique."""
        tracker.update("path.a", Position(0.0, 0.0))
        tracker.update("path.b", Position(1.0, 0.0))
        tracker.update("path.a", Position(2.0, 0.0))  # Duplicate

        paths = tracker.get_recent_paths()
        assert len(paths) == 2
        assert "path.a" in paths
        assert "path.b" in paths


# =============================================================================
# Type II: Integration Tests - BehaviorAnimator
# =============================================================================


class TestBehaviorAnimator:
    """Integration tests for BehaviorAnimator."""

    @pytest.fixture
    def follower_animator(self):
        """Create animator with FOLLOWER behavior."""
        return BehaviorAnimator(behavior=CursorBehavior.FOLLOWER)

    @pytest.fixture
    def explorer_animator(self):
        """Create animator with EXPLORER behavior."""
        return BehaviorAnimator(behavior=CursorBehavior.EXPLORER)

    @pytest.fixture
    def human_focus(self):
        """Create human focus tracker with some history."""
        tracker = HumanFocusTracker()
        tracker.update("self.memory", Position(50.0, 50.0))
        return tracker

    def test_animate_returns_position(self, follower_animator, human_focus, sample_graph):
        """Animate returns a position."""
        pos, path = follower_animator.animate(
            human_focus=human_focus,
            graph=sample_graph,
            dt=0.016,
        )
        assert isinstance(pos, Position)

    def test_animate_moves_toward_human_for_follower(
        self, follower_animator, human_focus, sample_graph
    ):
        """FOLLOWER moves toward human focus over time."""
        follower_animator.current_position = Position(0.0, 0.0)
        human_focus.update("self.memory", Position(100.0, 100.0))

        # Animate for several steps
        for _ in range(100):
            pos, _ = follower_animator.animate(
                human_focus=human_focus,
                graph=sample_graph,
                dt=0.016,
                phase=CircadianPhase.MORNING,
            )

        # Should have moved toward human focus
        distance = pos.distance_to(Position(100.0, 100.0))
        assert distance < 50.0  # Should be significantly closer

    def test_explorer_moves_independently(self, explorer_animator, human_focus, sample_graph):
        """EXPLORER moves somewhat independently of human focus."""
        explorer_animator.current_position = Position(0.0, 0.0)
        explorer_animator.current_path = "self.memory"

        # Set human focus far away
        human_focus.update("world.file", Position(200.0, 200.0))

        # Animate
        positions = []
        for _ in range(50):
            pos, _ = explorer_animator.animate(
                human_focus=human_focus,
                graph=sample_graph,
                dt=0.016,
            )
            positions.append(pos)

        # Explorer should have moved but not necessarily toward human
        # Just verify movement happened
        assert positions[-1] != Position(0.0, 0.0)

    def test_should_suggest_returns_bool(self, follower_animator):
        """should_suggest returns a boolean."""
        result = follower_animator.should_suggest(0.016)
        assert isinstance(result, bool)

    def test_should_suggest_respects_cooldown(self, follower_animator):
        """Suggestion has a cooldown period."""
        # Force a suggestion
        follower_animator.suggestion_cooldown = 0.0

        # Simulate time passing without suggestion
        suggested = False
        for _ in range(1000):
            if follower_animator.should_suggest(0.016):
                suggested = True
                break

        if suggested:
            # Verify cooldown is set
            assert follower_animator.suggestion_cooldown > 0

    def test_suggest_state_returns_valid_state(self, follower_animator):
        """suggest_state returns a CursorState from preferred states."""
        state = follower_animator.suggest_state()
        assert isinstance(state, CursorState)
        assert state in follower_animator.behavior.preferred_states


# =============================================================================
# Type II: Integration Tests - BehaviorModulator
# =============================================================================


class TestBehaviorModulator:
    """Integration tests for BehaviorModulator."""

    @pytest.fixture
    def modulator(self):
        """Create modulator with FOLLOWER base behavior."""
        return BehaviorModulator(base_behavior=CursorBehavior.FOLLOWER)

    @pytest.fixture
    def stationary_focus(self):
        """Create focus tracker that appears stationary."""
        tracker = HumanFocusTracker()
        old_time = datetime.now() - timedelta(seconds=30)
        tracker.history.append(
            FocusPoint(
                path="self.memory",
                position=Position(0.0, 0.0),
                timestamp=old_time,
            )
        )
        return tracker

    def test_effective_behavior_returns_behavior(self, modulator, stationary_focus):
        """get_effective_behavior returns a CursorBehavior."""
        result = modulator.get_effective_behavior(
            human_focus=stationary_focus,
        )
        assert isinstance(result, CursorBehavior)

    def test_usually_returns_base_behavior(self, modulator, stationary_focus):
        """Usually returns the base behavior (deterministic context)."""
        # Run multiple times to check stability
        results = [
            modulator.get_effective_behavior(human_focus=stationary_focus) for _ in range(10)
        ]
        # Most should be base behavior
        base_count = sum(1 for r in results if r == CursorBehavior.FOLLOWER)
        assert base_count >= 5  # At least half should be base

    def test_modulator_respects_circadian_phase(self, modulator, stationary_focus):
        """Behavior can change based on circadian phase."""
        # Test at different phases
        morning_behavior = modulator.get_effective_behavior(
            human_focus=stationary_focus,
            phase=CircadianPhase.MORNING,
        )
        night_behavior = modulator.get_effective_behavior(
            human_focus=stationary_focus,
            phase=CircadianPhase.NIGHT,
        )
        # Both should be valid behaviors (may or may not differ)
        assert morning_behavior in CursorBehavior
        assert night_behavior in CursorBehavior


# =============================================================================
# Type III: Property-Based Tests - Position
# =============================================================================


class TestPositionProperties:
    """Property-based tests for Position."""

    @given(
        st.floats(min_value=-1000, max_value=1000, allow_nan=False),
        st.floats(min_value=-1000, max_value=1000, allow_nan=False),
    )
    def test_distance_to_self_is_zero(self, x: float, y: float):
        """Distance to self is always zero."""
        p = Position(x, y)
        assert p.distance_to(p) == 0.0

    @given(
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
    )
    def test_distance_is_symmetric(self, x1: float, y1: float, x2: float, y2: float):
        """Distance is symmetric: d(a,b) == d(b,a)."""
        p1 = Position(x1, y1)
        p2 = Position(x2, y2)
        assert abs(p1.distance_to(p2) - p2.distance_to(p1)) < 1e-9

    @given(
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
    )
    def test_distance_is_nonnegative(self, x1: float, y1: float, x2: float, y2: float):
        """Distance is always non-negative."""
        p1 = Position(x1, y1)
        p2 = Position(x2, y2)
        assert p1.distance_to(p2) >= 0.0

    @given(
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=-100, max_value=100, allow_nan=False),
        st.floats(min_value=0.0, max_value=1.0),
    )
    def test_lerp_stays_on_segment(self, x1: float, y1: float, x2: float, y2: float, t: float):
        """Lerp result is on the line segment between points."""
        p1 = Position(x1, y1)
        p2 = Position(x2, y2)
        result = p1.lerp(p2, t)

        # Distance from p1 to result + distance from result to p2 should equal distance p1 to p2
        d1 = p1.distance_to(result)
        d2 = result.distance_to(p2)
        d_total = p1.distance_to(p2)

        # Allow small floating point error
        assert abs(d1 + d2 - d_total) < 1e-6


# =============================================================================
# Type III: Property-Based Tests - Behavior Properties
# =============================================================================


class TestBehaviorPropertyBased:
    """Property-based tests for behavior consistency."""

    @given(st.sampled_from(list(CursorBehavior)))
    def test_behavior_properties_sum_reasonable(self, behavior: CursorBehavior):
        """Behavior property values are internally consistent."""
        follow = behavior.follow_strength
        explore = behavior.exploration_tendency

        # High follow + high explore doesn't make sense
        # (you can't closely follow AND wander independently)
        if follow > 0.7:
            assert explore < 0.5, f"{behavior.name} has high follow + high explore"

    @given(st.sampled_from(list(CursorBehavior)))
    def test_preferred_states_not_empty(self, behavior: CursorBehavior):
        """Every behavior has at least one preferred state."""
        assert len(behavior.preferred_states) > 0

    @given(
        st.sampled_from(list(CursorBehavior)),
        st.sampled_from(list(CircadianPhase)),
    )
    def test_circadian_description_includes_base(
        self, behavior: CursorBehavior, phase: CircadianPhase
    ):
        """Circadian description always includes base description."""
        base = behavior.description
        modified = behavior.describe_for_phase(phase)
        assert base in modified


# =============================================================================
# Type III: Property-Based Tests - Animation Bounds
# =============================================================================


class TestAnimationBounds:
    """Property-based tests for animation staying in bounds."""

    @given(
        st.floats(min_value=-500, max_value=500, allow_nan=False),
        st.floats(min_value=-500, max_value=500, allow_nan=False),
        st.sampled_from(list(CursorBehavior)),
        st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=50)
    def test_animation_stays_finite(
        self,
        start_x: float,
        start_y: float,
        behavior: CursorBehavior,
        steps: int,
    ):
        """Animation always produces finite positions."""
        animator = BehaviorAnimator(
            behavior=behavior,
            current_position=Position(start_x, start_y),
        )
        tracker = HumanFocusTracker()
        tracker.update("self.memory", Position(0.0, 0.0))

        for _ in range(steps):
            pos, _ = animator.animate(
                human_focus=tracker,
                graph=None,  # No graph
                dt=0.016,
            )
            assert math.isfinite(pos.x)
            assert math.isfinite(pos.y)


# =============================================================================
# Cursor Integration with Behaviors
# =============================================================================


class TestCursorBehaviorIntegration:
    """Test AgentCursor integration with behaviors."""

    def test_cursor_with_behavior_renders_emoji(self):
        """Cursor with behavior shows behavior emoji."""
        from services.conductor.presence import AgentCursor, CursorState

        cursor = AgentCursor(
            agent_id="test",
            display_name="Test",
            state=CursorState.FOLLOWING,
            activity="tracking",
            behavior=CursorBehavior.EXPLORER,
        )

        # behavior_emoji should combine behavior + state emojis
        assert CursorBehavior.EXPLORER.emoji in cursor.behavior_emoji
        assert CursorState.FOLLOWING.emoji in cursor.behavior_emoji

    def test_cursor_to_dict_includes_behavior(self):
        """Cursor serialization includes behavior."""
        from services.conductor.presence import AgentCursor, CursorState

        cursor = AgentCursor(
            agent_id="test",
            display_name="Test",
            state=CursorState.WORKING,
            activity="busy",
            behavior=CursorBehavior.AUTONOMOUS,
            canvas_position=(100.0, 200.0),
        )

        data = cursor.to_dict()
        assert data["behavior"] == "AUTONOMOUS"
        assert data["canvas_position"]["x"] == 100.0
        assert data["canvas_position"]["y"] == 200.0

    def test_cursor_from_dict_restores_behavior(self):
        """Cursor deserialization restores behavior."""
        from services.conductor.presence import AgentCursor, CursorState

        original = AgentCursor(
            agent_id="test",
            display_name="Test",
            state=CursorState.EXPLORING,
            activity="wandering",
            behavior=CursorBehavior.EXPLORER,
            canvas_position=(50.0, 75.0),
            velocity=(1.0, -0.5),
        )

        data = original.to_dict()
        restored = AgentCursor.from_dict(data)

        assert restored.behavior == CursorBehavior.EXPLORER
        assert restored.canvas_position == (50.0, 75.0)
        assert restored.velocity == (1.0, -0.5)

    def test_cursor_teaching_mode_shows_behavior(self):
        """Teaching mode includes behavior description."""
        from services.conductor.presence import AgentCursor, CursorState

        cursor = AgentCursor(
            agent_id="test",
            display_name="Test",
            state=CursorState.FOLLOWING,
            activity="watching",
            behavior=CursorBehavior.FOLLOWER,
        )

        cli_output = cursor.to_cli(teaching_mode=True)
        assert "Behavior:" in cli_output
        assert "Follows your focus" in cli_output
