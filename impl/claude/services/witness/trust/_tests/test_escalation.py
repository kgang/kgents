"""
Tests for Escalation Criteria.

Verifies:
- Level 1 criteria (L0 → L1)
- Level 2 criteria (L1 → L2)
- Level 3 criteria (L2 → L3)
- Edge cases and boundary conditions
- PolicyTrace emission for security-critical decisions
"""

import pytest

from agents.t.truth_functor import PolicyTrace
from services.witness.polynomial import TrustLevel
from services.witness.trust.escalation import (
    EscalationResult,
    Level1Criteria,
    Level2Criteria,
    Level3Criteria,
    ObservationStats,
    OperationStats,
    SuggestionStats,
    check_escalation,
)

# =============================================================================
# Level 1 Criteria Tests (L0 → L1)
# =============================================================================


class TestLevel1Criteria:
    """Tests for L0 → L1 escalation."""

    def test_meets_all_criteria(self) -> None:
        """Escalation when all criteria are met."""
        stats = ObservationStats(
            hours_observing=30.0,  # > 24h
            total_observations=150,  # > 100
            false_positives=1,  # 0.67% < 1%
        )

        result = Level1Criteria().check(stats)

        assert result.is_met
        assert result.from_level == TrustLevel.READ_ONLY
        assert result.to_level == TrustLevel.BOUNDED
        assert result.reason == "Criteria met"

    def test_insufficient_hours(self) -> None:
        """No escalation with insufficient observation hours."""
        stats = ObservationStats(
            hours_observing=12.0,  # < 24h
            total_observations=150,
            false_positives=0,
        )

        result = Level1Criteria().check(stats)

        assert not result.is_met
        assert "more hours" in result.reason

    def test_insufficient_observations(self) -> None:
        """No escalation with insufficient observations."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=50,  # < 100
            false_positives=0,
        )

        result = Level1Criteria().check(stats)

        assert not result.is_met
        assert "more observations" in result.reason

    def test_high_false_positive_rate(self) -> None:
        """No escalation with high false positive rate."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=100,
            false_positives=5,  # 5% > 1%
        )

        result = Level1Criteria().check(stats)

        assert not result.is_met
        assert "False positive rate" in result.reason

    def test_criteria_details(self) -> None:
        """Criteria details are populated."""
        stats = ObservationStats(
            hours_observing=24.0,
            total_observations=100,
            false_positives=0,
        )

        result = Level1Criteria().check(stats)

        assert "hours" in result.criteria_details
        assert "observations" in result.criteria_details
        assert "false_positive_rate" in result.criteria_details


# =============================================================================
# Level 2 Criteria Tests (L1 → L2)
# =============================================================================


class TestLevel2Criteria:
    """Tests for L1 → L2 escalation."""

    def test_meets_all_criteria(self) -> None:
        """Escalation when all criteria are met."""
        stats = OperationStats(
            total_operations=120,  # > 100
            failed_operations=3,  # 2.5% < 5%
            unique_operation_types=5,  # > 3
        )

        result = Level2Criteria().check(stats)

        assert result.is_met
        assert result.from_level == TrustLevel.BOUNDED
        assert result.to_level == TrustLevel.SUGGESTION

    def test_insufficient_operations(self) -> None:
        """No escalation with insufficient operations."""
        stats = OperationStats(
            total_operations=50,  # < 100
            failed_operations=0,
            unique_operation_types=5,
        )

        result = Level2Criteria().check(stats)

        assert not result.is_met
        assert "more operations" in result.reason

    def test_high_failure_rate(self) -> None:
        """No escalation with high failure rate."""
        stats = OperationStats(
            total_operations=100,
            failed_operations=10,  # 10% > 5%
            unique_operation_types=5,
        )

        result = Level2Criteria().check(stats)

        assert not result.is_met
        assert "Failure rate" in result.reason

    def test_insufficient_operation_types(self) -> None:
        """No escalation with insufficient operation diversity."""
        stats = OperationStats(
            total_operations=100,
            failed_operations=0,
            unique_operation_types=2,  # < 3
        )

        result = Level2Criteria().check(stats)

        assert not result.is_met
        assert "more operation types" in result.reason


# =============================================================================
# Level 3 Criteria Tests (L2 → L3)
# =============================================================================


class TestLevel3Criteria:
    """Tests for L2 → L3 escalation."""

    def test_meets_all_criteria(self) -> None:
        """Escalation when all criteria are met."""
        stats = SuggestionStats(
            total_suggestions=60,  # > 50
            confirmed_suggestions=55,  # 91.7% > 90%
            unique_suggestion_types=7,  # > 5
            days_at_level2=10,  # > 7
        )

        result = Level3Criteria().check(stats)

        assert result.is_met
        assert result.from_level == TrustLevel.SUGGESTION
        assert result.to_level == TrustLevel.AUTONOMOUS

    def test_insufficient_suggestions(self) -> None:
        """No escalation with insufficient suggestions."""
        stats = SuggestionStats(
            total_suggestions=30,  # < 50
            confirmed_suggestions=28,
            unique_suggestion_types=7,
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)

        assert not result.is_met
        assert "more suggestions" in result.reason

    def test_low_acceptance_rate(self) -> None:
        """No escalation with low acceptance rate."""
        stats = SuggestionStats(
            total_suggestions=50,
            confirmed_suggestions=40,  # 80% < 90%
            unique_suggestion_types=7,
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)

        assert not result.is_met
        assert "Acceptance rate" in result.reason

    def test_insufficient_suggestion_types(self) -> None:
        """No escalation with insufficient suggestion diversity."""
        stats = SuggestionStats(
            total_suggestions=50,
            confirmed_suggestions=48,
            unique_suggestion_types=3,  # < 5
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)

        assert not result.is_met
        assert "more suggestion types" in result.reason

    def test_insufficient_time_at_level2(self) -> None:
        """No escalation without minimum time at L2."""
        stats = SuggestionStats(
            total_suggestions=50,
            confirmed_suggestions=48,
            unique_suggestion_types=7,
            days_at_level2=3,  # < 7
        )

        result = Level3Criteria().check(stats)

        assert not result.is_met
        assert "more days at Level 2" in result.reason


# =============================================================================
# check_escalation Tests
# =============================================================================


class TestCheckEscalation:
    """Tests for check_escalation convenience function."""

    def test_l0_to_l1_with_correct_stats(self) -> None:
        """Check L0 → L1 with ObservationStats."""
        stats = ObservationStats(hours_observing=30, total_observations=150, false_positives=0)
        result = check_escalation(TrustLevel.READ_ONLY, stats)

        assert result is not None
        assert result.is_met

    def test_l0_to_l1_with_wrong_stats(self) -> None:
        """Check L0 → L1 with wrong stats type returns None."""
        stats = OperationStats(total_operations=100, failed_operations=0, unique_operation_types=5)
        result = check_escalation(TrustLevel.READ_ONLY, stats)

        assert result is None

    def test_l1_to_l2_with_correct_stats(self) -> None:
        """Check L1 → L2 with OperationStats."""
        stats = OperationStats(total_operations=120, failed_operations=0, unique_operation_types=5)
        result = check_escalation(TrustLevel.BOUNDED, stats)

        assert result is not None
        assert result.is_met

    def test_l2_to_l3_with_correct_stats(self) -> None:
        """Check L2 → L3 with SuggestionStats."""
        stats = SuggestionStats(
            total_suggestions=60,
            confirmed_suggestions=55,
            unique_suggestion_types=7,
            days_at_level2=10,
        )
        result = check_escalation(TrustLevel.SUGGESTION, stats)

        assert result is not None
        assert result.is_met

    def test_l3_cannot_escalate(self) -> None:
        """L3 cannot escalate further."""
        stats = SuggestionStats(
            total_suggestions=100,
            confirmed_suggestions=100,
            unique_suggestion_types=10,
            days_at_level2=30,
        )
        result = check_escalation(TrustLevel.AUTONOMOUS, stats)

        assert result is None


# =============================================================================
# Stats Property Tests
# =============================================================================


class TestStatsProperties:
    """Tests for stats dataclass properties."""

    def test_observation_stats_false_positive_rate(self) -> None:
        """ObservationStats calculates false positive rate correctly."""
        stats = ObservationStats(hours_observing=24, total_observations=100, false_positives=5)
        assert stats.false_positive_rate == 0.05

    def test_observation_stats_zero_observations(self) -> None:
        """False positive rate is 0 when no observations."""
        stats = ObservationStats(hours_observing=0, total_observations=0, false_positives=0)
        assert stats.false_positive_rate == 0.0

    def test_operation_stats_failure_rate(self) -> None:
        """OperationStats calculates failure rate correctly."""
        stats = OperationStats(total_operations=100, failed_operations=10, unique_operation_types=3)
        assert stats.failure_rate == 0.10

    def test_suggestion_stats_acceptance_rate(self) -> None:
        """SuggestionStats calculates acceptance rate correctly."""
        stats = SuggestionStats(
            total_suggestions=100,
            confirmed_suggestions=85,
            unique_suggestion_types=5,
            days_at_level2=7,
        )
        assert stats.acceptance_rate == 0.85


# =============================================================================
# PolicyTrace Emission Tests (TIER 2)
# =============================================================================


class TestPolicyTraceEmission:
    """Tests for PolicyTrace emission in escalation checks."""

    def test_level1_emits_trace(self) -> None:
        """Level 1 escalation emits PolicyTrace."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=150,
            false_positives=1,
        )

        result = Level1Criteria().check(stats)

        # Verify trace exists
        assert result.trace is not None
        assert isinstance(result.trace, PolicyTrace)

        # Verify trace has correct value
        assert result.trace.value == result.is_met

        # Verify trace has entries (3 criteria + 1 verdict = 4)
        assert len(result.trace.entries) == 4

        # Verify trace entries have reasoning
        for entry in result.trace.entries:
            assert entry.reasoning
            assert entry.reward is not None

    def test_level1_trace_reflects_denial(self) -> None:
        """Failed L1 escalation has trace with value=False."""
        stats = ObservationStats(
            hours_observing=10.0,  # Insufficient
            total_observations=50,  # Insufficient
            false_positives=0,
        )

        result = Level1Criteria().check(stats)

        assert not result.is_met
        assert result.trace is not None
        assert result.trace.value is False

    def test_level1_ethical_scores_reflect_security(self) -> None:
        """L1 trace has high ethical scores for met criteria."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=150,
            false_positives=1,
        )

        result = Level1Criteria().check(stats)
        assert result.trace is not None

        # Check that all entries have ethical component
        for entry in result.trace.entries:
            assert entry.reward.ethical > 0.0

        # False positive check should have highest ethical weight
        fpr_entry = result.trace.entries[2]  # Third entry is FPR check
        assert "false positive" in fpr_entry.reasoning.lower()
        # When FPR is met, ethical score should be 1.0 (CRITICAL for trust)
        assert fpr_entry.reward.ethical == 1.0

    def test_level2_emits_trace(self) -> None:
        """Level 2 escalation emits PolicyTrace."""
        stats = OperationStats(
            total_operations=120,
            failed_operations=3,
            unique_operation_types=5,
        )

        result = Level2Criteria().check(stats)

        assert result.trace is not None
        assert isinstance(result.trace, PolicyTrace)
        assert result.trace.value == result.is_met
        # 3 criteria + 1 verdict = 4 entries
        assert len(result.trace.entries) == 4

    def test_level2_failure_rate_ethical_score(self) -> None:
        """L2 failure rate check has CRITICAL ethical weight."""
        stats = OperationStats(
            total_operations=120,
            failed_operations=3,  # 2.5% < 5% (meets)
            unique_operation_types=5,
        )

        result = Level2Criteria().check(stats)
        assert result.trace is not None

        # Find failure rate entry
        fr_entry = result.trace.entries[1]  # Second entry
        assert "failure rate" in fr_entry.reasoning.lower()
        # When FR is met, ethical score should be 1.0 (reliability is CRITICAL)
        assert fr_entry.reward.ethical == 1.0

    def test_level2_composable_scores_reflect_diversity(self) -> None:
        """L2 operation types check affects composability score."""
        stats_diverse = OperationStats(
            total_operations=120,
            failed_operations=0,
            unique_operation_types=5,  # Diverse
        )

        result_diverse = Level2Criteria().check(stats_diverse)
        assert result_diverse.trace is not None

        # Operation types entry (third one)
        types_entry = result_diverse.trace.entries[2]
        assert types_entry.reward.composable == 1.0  # High composability

    def test_level3_emits_trace(self) -> None:
        """Level 3 escalation emits PolicyTrace."""
        stats = SuggestionStats(
            total_suggestions=60,
            confirmed_suggestions=55,
            unique_suggestion_types=7,
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)

        assert result.trace is not None
        assert isinstance(result.trace, PolicyTrace)
        assert result.trace.value == result.is_met
        # 4 criteria + 1 verdict = 5 entries
        assert len(result.trace.entries) == 5

    def test_level3_acceptance_rate_joy_score(self) -> None:
        """L3 acceptance rate check includes joy_inducing score."""
        stats = SuggestionStats(
            total_suggestions=60,
            confirmed_suggestions=55,  # 91.7% > 90%
            unique_suggestion_types=7,
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)
        assert result.trace is not None

        # Find acceptance rate entry (third entry)
        ar_entry = result.trace.entries[2]
        assert "acceptance rate" in ar_entry.reasoning.lower()
        # High acceptance = joy
        assert ar_entry.reward.joy_inducing == 1.0

    def test_level3_suggestion_types_curated_score(self) -> None:
        """L3 suggestion types check includes curated score."""
        stats = SuggestionStats(
            total_suggestions=60,
            confirmed_suggestions=55,
            unique_suggestion_types=7,  # Diverse
            days_at_level2=10,
        )

        result = Level3Criteria().check(stats)
        assert result.trace is not None

        # Find suggestion types entry (fourth entry)
        types_entry = result.trace.entries[3]
        assert "suggestion types" in types_entry.reasoning.lower()
        # Variety shows sophistication
        assert types_entry.reward.curated == 1.0

    def test_trace_total_reward_calculation(self) -> None:
        """PolicyTrace total_reward aggregates constitutional scores."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=150,
            false_positives=1,
        )

        result = Level1Criteria().check(stats)
        assert result.trace is not None

        # Verify total_reward is computed
        total = result.trace.total_reward
        assert total > 0.0

        # Verify it's sum of weighted rewards
        manual_sum = sum(e.reward.weighted_total for e in result.trace.entries)
        assert abs(total - manual_sum) < 0.001

    def test_failed_escalation_trace_lower_reward(self) -> None:
        """Failed escalations have lower total reward than successful ones."""
        stats_pass = ObservationStats(
            hours_observing=30.0,
            total_observations=150,
            false_positives=1,
        )
        stats_fail = ObservationStats(
            hours_observing=10.0,
            total_observations=50,
            false_positives=5,
        )

        result_pass = Level1Criteria().check(stats_pass)
        result_fail = Level1Criteria().check(stats_fail)

        assert result_pass.trace is not None
        assert result_fail.trace is not None

        # Passing should have higher total reward
        assert result_pass.trace.total_reward > result_fail.trace.total_reward

    def test_trace_phases_are_descriptive(self) -> None:
        """Trace entries have descriptive phase names."""
        stats = ObservationStats(
            hours_observing=30.0,
            total_observations=150,
            false_positives=1,
        )

        result = Level1Criteria().check(stats)
        assert result.trace is not None

        # Initial state should indicate L0→L1
        first_entry = result.trace.entries[0]
        assert "L0" in first_entry.state_before.phase or "L1" in first_entry.state_before.phase

        # Final state should indicate verdict
        final_entry = result.trace.entries[-1]
        assert "verdict" in final_entry.state_after.phase.lower()
