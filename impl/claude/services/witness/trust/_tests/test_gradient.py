"""
Tests for Amendment E: Trust Polynomial Functor.

This test suite validates:
1. TrustLevel polynomial modes
2. TrustState asymmetric dynamics (3x faster loss)
3. Weekly decay
4. Autonomous execution gate (Tier 4 always requires approval)

From: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment E)
"""

import time

import pytest

from services.witness.trust.gradient import (
    Action,
    ApprovalRequired,
    Autonomous,
    HighImpactOnly,
    MostApproved,
    RoutineApproved,
    TrustLevel,
    TrustState,
    can_execute_autonomously,
    create_trust_state,
    high_risk_action,
    low_risk_action,
    medium_risk_action,
    requires_approval,
    trivial_action,
)


class TestTrustLevel:
    """Tests for TrustLevel enum."""

    def test_level_ordering(self) -> None:
        """Trust levels should be ordered 1-5."""
        assert TrustLevel.LEVEL_1 < TrustLevel.LEVEL_2
        assert TrustLevel.LEVEL_2 < TrustLevel.LEVEL_3
        assert TrustLevel.LEVEL_3 < TrustLevel.LEVEL_4
        assert TrustLevel.LEVEL_4 < TrustLevel.LEVEL_5

    def test_all_levels_have_description(self) -> None:
        """All levels should have descriptions."""
        for level in TrustLevel:
            assert len(level.description) > 0

    def test_auto_approve_tiers(self) -> None:
        """Auto-approve thresholds should match spec."""
        assert TrustLevel.LEVEL_1.auto_approve_up_to_tier == 0
        assert TrustLevel.LEVEL_2.auto_approve_up_to_tier == 1
        assert TrustLevel.LEVEL_3.auto_approve_up_to_tier == 2
        assert TrustLevel.LEVEL_4.auto_approve_up_to_tier == 3
        assert TrustLevel.LEVEL_5.auto_approve_up_to_tier == 3  # Never 4

    def test_level_5_never_auto_approves_tier_4(self) -> None:
        """Level 5 should never auto-approve Tier 4 (irreversible)."""
        # Tier 4 is never auto-approved, even at Level 5
        assert TrustLevel.LEVEL_5.auto_approve_up_to_tier < 4


class TestAction:
    """Tests for Action dataclass."""

    def test_valid_risk_tiers(self) -> None:
        """Should accept risk tiers 1-4."""
        for tier in range(1, 5):
            action = Action(name="test", description="test", risk_tier=tier)
            assert action.risk_tier == tier

    def test_invalid_risk_tier_raises(self) -> None:
        """Should reject invalid risk tiers."""
        with pytest.raises(ValueError):
            Action(name="test", description="test", risk_tier=0)

        with pytest.raises(ValueError):
            Action(name="test", description="test", risk_tier=5)

    def test_action_factories(self) -> None:
        """Action factory functions should create correct tiers."""
        assert trivial_action("test").risk_tier == 1
        assert low_risk_action("test").risk_tier == 2
        assert medium_risk_action("test").risk_tier == 3
        assert high_risk_action("test").risk_tier == 4


class TestTrustState:
    """Tests for TrustState with asymmetric dynamics."""

    def test_initial_state(self) -> None:
        """Initial state should be Level 1, score 0."""
        state = TrustState()

        assert state.level == TrustLevel.LEVEL_1
        assert state.score == 0.0
        assert state.aligned_count == 0
        assert state.misaligned_count == 0

    def test_update_aligned_increases_score(self) -> None:
        """Aligned action should increase score by GAIN_RATE."""
        state = TrustState()

        new_state = state.update_aligned()

        assert new_state.score == TrustState.GAIN_RATE
        assert new_state.aligned_count == 1
        assert new_state.level == TrustLevel.LEVEL_1

    def test_update_misaligned_decreases_score(self) -> None:
        """Misaligned action should decrease score by LOSS_RATE."""
        state = TrustState(score=0.5)

        new_state = state.update_misaligned()

        assert new_state.score == 0.5 - TrustState.LOSS_RATE
        assert new_state.misaligned_count == 1

    def test_asymmetric_dynamics_3x_faster_loss(self) -> None:
        """Loss rate should be 3x gain rate."""
        assert TrustState.LOSS_RATE == 3 * TrustState.GAIN_RATE

    def test_level_up_at_score_1(self) -> None:
        """Should level up when score reaches 1.0."""
        state = TrustState(score=0.99, level=TrustLevel.LEVEL_2)

        new_state = state.update_aligned()

        assert new_state.level == TrustLevel.LEVEL_3
        assert new_state.score == 0.0  # Reset to 0

    def test_level_down_at_score_0(self) -> None:
        """Should level down when score reaches 0.0."""
        state = TrustState(score=0.01, level=TrustLevel.LEVEL_3)

        new_state = state.update_misaligned()

        assert new_state.level == TrustLevel.LEVEL_2
        assert new_state.score == 1.0  # Start at top of lower level

    def test_cannot_level_up_past_5(self) -> None:
        """Cannot level up past Level 5."""
        state = TrustState(score=0.99, level=TrustLevel.LEVEL_5)

        new_state = state.update_aligned()

        assert new_state.level == TrustLevel.LEVEL_5
        assert new_state.score == 1.0  # Capped

    def test_cannot_level_down_past_1(self) -> None:
        """Cannot level down past Level 1."""
        state = TrustState(score=0.01, level=TrustLevel.LEVEL_1)

        new_state = state.update_misaligned()

        assert new_state.level == TrustLevel.LEVEL_1
        assert new_state.score == 0.0  # Floored

    def test_immutability(self) -> None:
        """State updates should return new state, not mutate."""
        original = TrustState()

        aligned_state = original.update_aligned()
        misaligned_state = original.update_misaligned()

        # Original should be unchanged
        assert original.aligned_count == 0
        assert original.misaligned_count == 0
        assert aligned_state.aligned_count == 1
        assert misaligned_state.misaligned_count == 1


class TestWeeklyDecay:
    """Tests for weekly decay without activity."""

    def test_no_decay_within_week(self) -> None:
        """No decay if less than a week inactive."""
        now = time.time()
        state = TrustState(score=0.5, last_activity=now - (6 * 24 * 60 * 60))

        new_state = state.apply_decay(now)

        # No decay
        assert new_state.score == state.score
        assert new_state.level == state.level

    def test_decay_after_one_week(self) -> None:
        """Should decay by DECAY_RATE after one week."""
        now = time.time()
        week_ago = now - (7 * 24 * 60 * 60)
        state = TrustState(score=0.5, last_activity=week_ago)

        new_state = state.apply_decay(now)

        expected_score = 0.5 - TrustState.DECAY_RATE
        assert abs(new_state.score - expected_score) < 0.01

    def test_decay_proportional_to_weeks(self) -> None:
        """Decay should be proportional to weeks inactive."""
        now = time.time()
        two_weeks_ago = now - (14 * 24 * 60 * 60)
        state = TrustState(score=0.5, last_activity=two_weeks_ago)

        new_state = state.apply_decay(now)

        expected_score = 0.5 - (2 * TrustState.DECAY_RATE)
        assert abs(new_state.score - expected_score) < 0.01

    def test_decay_causes_level_down(self) -> None:
        """Decay to 0 should cause level down."""
        now = time.time()
        ten_weeks_ago = now - (10 * 7 * 24 * 60 * 60)
        state = TrustState(
            score=0.5,
            level=TrustLevel.LEVEL_3,
            last_activity=ten_weeks_ago,
        )

        new_state = state.apply_decay(now)

        # Should decay to lower level
        assert new_state.level == TrustLevel.LEVEL_2
        assert new_state.score == 0.5  # Middle of lower level

    def test_decay_does_not_update_last_activity(self) -> None:
        """Decay should not update last_activity timestamp."""
        now = time.time()
        original_activity = now - (7 * 24 * 60 * 60)
        state = TrustState(score=0.5, last_activity=original_activity)

        new_state = state.apply_decay(now)

        assert new_state.last_activity == original_activity


class TestAutonomousExecutionGate:
    """Tests for can_execute_autonomously and requires_approval."""

    def test_tier_4_always_requires_approval(self) -> None:
        """Tier 4 (irreversible) always requires approval."""
        tier_4_action = high_risk_action("delete production")

        for level in TrustLevel:
            state = TrustState(level=level, score=1.0)
            assert not can_execute_autonomously(state, tier_4_action)

            needs_approval, reason = requires_approval(state, tier_4_action)
            assert needs_approval
            assert "Tier 4" in reason or "irreversible" in reason

    def test_level_1_requires_all_approval(self) -> None:
        """Level 1 requires approval for all tiers."""
        state = TrustState(level=TrustLevel.LEVEL_1)

        for tier in range(1, 4):
            action = Action(name="test", description="test", risk_tier=tier)
            assert not can_execute_autonomously(state, action)

    def test_level_2_auto_approves_tier_1(self) -> None:
        """Level 2 auto-approves Tier 1 only."""
        state = TrustState(level=TrustLevel.LEVEL_2)

        assert can_execute_autonomously(state, trivial_action("format"))
        assert not can_execute_autonomously(state, low_risk_action("refactor"))
        assert not can_execute_autonomously(state, medium_risk_action("deploy"))

    def test_level_3_auto_approves_tiers_1_2(self) -> None:
        """Level 3 auto-approves Tiers 1-2."""
        state = TrustState(level=TrustLevel.LEVEL_3)

        assert can_execute_autonomously(state, trivial_action("format"))
        assert can_execute_autonomously(state, low_risk_action("refactor"))
        assert not can_execute_autonomously(state, medium_risk_action("deploy"))

    def test_level_4_auto_approves_tiers_1_3(self) -> None:
        """Level 4 auto-approves Tiers 1-3."""
        state = TrustState(level=TrustLevel.LEVEL_4)

        assert can_execute_autonomously(state, trivial_action("format"))
        assert can_execute_autonomously(state, low_risk_action("refactor"))
        assert can_execute_autonomously(state, medium_risk_action("deploy"))
        assert not can_execute_autonomously(state, high_risk_action("delete"))

    def test_level_5_same_as_level_4(self) -> None:
        """Level 5 has same auto-approve as Level 4 (Tier 4 never auto)."""
        state = TrustState(level=TrustLevel.LEVEL_5)

        assert can_execute_autonomously(state, medium_risk_action("deploy"))
        assert not can_execute_autonomously(state, high_risk_action("delete"))

    def test_requires_approval_provides_reason(self) -> None:
        """requires_approval should provide clear reason."""
        state = TrustState(level=TrustLevel.LEVEL_2)
        action = medium_risk_action("deploy staging")

        needs, reason = requires_approval(state, action)

        assert needs
        assert "Trust level" in reason or "Tier" in reason


class TestAlignmentRate:
    """Tests for alignment rate calculation."""

    def test_no_actions_returns_1(self) -> None:
        """No actions should return 1.0 alignment rate."""
        state = TrustState()
        assert state.alignment_rate == 1.0

    def test_all_aligned(self) -> None:
        """All aligned actions should return 1.0."""
        state = TrustState(aligned_count=10, misaligned_count=0)
        assert state.alignment_rate == 1.0

    def test_mixed_alignment(self) -> None:
        """Mixed actions should return correct ratio."""
        state = TrustState(aligned_count=7, misaligned_count=3)
        assert abs(state.alignment_rate - 0.7) < 0.01

    def test_all_misaligned(self) -> None:
        """All misaligned actions should return 0.0."""
        state = TrustState(aligned_count=0, misaligned_count=10)
        assert state.alignment_rate == 0.0


class TestActionsToLevelUp:
    """Tests for actions_to_level_up estimation."""

    def test_max_level_returns_negative_1(self) -> None:
        """At max level, should return -1."""
        state = TrustState(level=TrustLevel.LEVEL_5)
        assert state.actions_to_level_up() == -1

    def test_estimate_from_zero(self) -> None:
        """From score 0, should estimate based on GAIN_RATE."""
        state = TrustState(score=0.0, level=TrustLevel.LEVEL_1)
        expected = int(1.0 / TrustState.GAIN_RATE) + 1
        assert state.actions_to_level_up() == expected

    def test_estimate_partway(self) -> None:
        """Partway through should give reduced estimate."""
        state = TrustState(score=0.5, level=TrustLevel.LEVEL_2)
        expected = int(0.5 / TrustState.GAIN_RATE) + 1
        assert state.actions_to_level_up() == expected


class TestInputTypes:
    """Tests for polynomial functor input types."""

    def test_approval_required(self) -> None:
        """ApprovalRequired should hold action and reasoning."""
        action = trivial_action("test")
        input = ApprovalRequired(action=action, reasoning="needs review")

        assert input.action == action
        assert input.reasoning == "needs review"

    def test_routine_approved(self) -> None:
        """RoutineApproved should hold action and routine flag."""
        action = trivial_action("format")
        input = RoutineApproved(action=action, is_routine=True)

        assert input.action == action
        assert input.is_routine

    def test_autonomous(self) -> None:
        """Autonomous should hold action and veto window state."""
        action = low_risk_action("refactor")
        input = Autonomous(action=action, veto_window_open=True)

        assert input.action == action
        assert input.veto_window_open


class TestCreateTrustState:
    """Tests for create_trust_state factory."""

    def test_default_values(self) -> None:
        """Should create with default values."""
        state = create_trust_state()

        assert state.level == TrustLevel.LEVEL_1
        assert state.score == 0.0
        assert state.aligned_count == 0
        assert state.misaligned_count == 0

    def test_custom_values(self) -> None:
        """Should accept custom values."""
        state = create_trust_state(
            level=3,
            score=0.5,
            aligned_count=10,
            misaligned_count=2,
        )

        assert state.level == TrustLevel.LEVEL_3
        assert state.score == 0.5
        assert state.aligned_count == 10
        assert state.misaligned_count == 2


class TestStringRepresentation:
    """Tests for TrustState string representation."""

    def test_str_contains_key_info(self) -> None:
        """String should contain level, score, and counts."""
        state = TrustState(
            level=TrustLevel.LEVEL_3,
            score=0.75,
            aligned_count=15,
            misaligned_count=3,
        )

        s = str(state)

        assert "L3" in s
        assert "0.75" in s
        assert "15" in s
        assert "3" in s
