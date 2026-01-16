"""
Tests for Constitutional Reward system.

Philosophy:
    "Test every principle. Test every edge case. Test composition."

See: spec/protocols/chat-unified.md §4.2
"""

from __future__ import annotations

import pytest

from services.chat.evidence import TurnResult
from services.chat.reward import Principle, PrincipleScore, constitutional_reward

# =============================================================================
# PrincipleScore Tests
# =============================================================================


class TestPrincipleScore:
    """Test PrincipleScore dataclass."""

    def test_default_scores_are_one(self):
        """All principles default to 1.0 (optimistic prior)."""
        score = PrincipleScore()
        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.ethical == 1.0
        assert score.joy_inducing == 1.0
        assert score.composable == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_custom_scores(self):
        """Can set custom scores for each principle."""
        score = PrincipleScore(
            tasteful=0.9,
            curated=0.8,
            ethical=0.7,
            joy_inducing=0.6,
            composable=0.5,
            heterarchical=0.4,
            generative=0.3,
        )
        assert score.tasteful == 0.9
        assert score.curated == 0.8
        assert score.ethical == 0.7
        assert score.joy_inducing == 0.6
        assert score.composable == 0.5
        assert score.heterarchical == 0.4
        assert score.generative == 0.3

    def test_weighted_total_default_weights(self):
        """Weighted total uses default weights."""
        # Default weights: ETHICAL=2.0, COMPOSABLE=1.5, JOY=1.2, others=1.0
        # Sum of weights: 2.0 + 1.5 + 1.2 + 1.0*4 = 8.7
        score = PrincipleScore()  # All 1.0
        total = score.weighted_total()
        assert total == pytest.approx(8.7, abs=0.01)

    def test_weighted_total_custom_weights(self):
        """Weighted total accepts custom weights."""
        score = PrincipleScore(ethical=0.5, composable=0.8)
        custom_weights = {
            Principle.ETHICAL: 3.0,
            Principle.COMPOSABLE: 2.0,
            Principle.JOY_INDUCING: 1.0,
            Principle.TASTEFUL: 1.0,
            Principle.CURATED: 1.0,
            Principle.HETERARCHICAL: 1.0,
            Principle.GENERATIVE: 1.0,
        }
        total = score.weighted_total(custom_weights)
        # (0.5*3.0 + 0.8*2.0 + 1.0*5) = 1.5 + 1.6 + 5.0 = 8.1
        assert total == pytest.approx(8.1, abs=0.01)

    def test_weighted_total_partial_override(self):
        """Can override some weights, others default to 1.0."""
        score = PrincipleScore(ethical=0.5)
        weights = {Principle.ETHICAL: 3.0}
        total = score.weighted_total(weights)
        # (0.5*3.0 + 1.0*6) = 1.5 + 6.0 = 7.5
        assert total == pytest.approx(7.5, abs=0.01)

    def test_to_dict(self):
        """Can serialize to dictionary."""
        score = PrincipleScore(ethical=0.8, composable=0.9)
        result = score.to_dict()
        assert result == {
            "tasteful": 1.0,
            "curated": 1.0,
            "ethical": 0.8,
            "joy_inducing": 1.0,
            "composable": 0.9,
            "heterarchical": 1.0,
            "generative": 1.0,
        }

    def test_from_dict(self):
        """Can deserialize from dictionary."""
        data = {
            "tasteful": 0.9,
            "ethical": 0.8,
            "composable": 0.7,
        }
        score = PrincipleScore.from_dict(data)
        assert score.tasteful == 0.9
        assert score.ethical == 0.8
        assert score.composable == 0.7
        # Missing keys default to 1.0
        assert score.curated == 1.0
        assert score.joy_inducing == 1.0

    def test_roundtrip_serialization(self):
        """to_dict/from_dict roundtrip preserves values."""
        original = PrincipleScore(tasteful=0.1, curated=0.2, ethical=0.3, joy_inducing=0.4)
        roundtrip = PrincipleScore.from_dict(original.to_dict())
        assert roundtrip.tasteful == original.tasteful
        assert roundtrip.curated == original.curated
        assert roundtrip.ethical == original.ethical
        assert roundtrip.joy_inducing == original.joy_inducing


# =============================================================================
# Constitutional Reward Tests
# =============================================================================


class TestConstitutionalReward:
    """Test constitutional_reward function."""

    def test_perfect_turn(self):
        """Perfect turn gets all 1.0 scores."""
        result = TurnResult(
            response="This is a thoughtful, helpful response!",
            tools=[],
            tools_passed=True,
        )
        score = constitutional_reward("send_message", result, has_mutations=False)
        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.ethical == 1.0
        assert score.joy_inducing == 1.0
        assert score.composable == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_no_turn_result(self):
        """No turn result defaults to perfect scores."""
        score = constitutional_reward("send_message")
        assert score.ethical == 1.0
        assert score.composable == 1.0
        assert score.joy_inducing == 1.0

    # === ETHICAL Tests ===

    def test_ethical_unacknowledged_mutations(self):
        """Unacknowledged mutations lower ethical score."""
        result = TurnResult(tools_passed=False)
        score = constitutional_reward("send_message", result, has_mutations=True)
        assert score.ethical < 1.0
        assert score.ethical == 0.5  # Spec says lower to 0.5

    def test_ethical_acknowledged_mutations(self):
        """Acknowledged mutations get high but not perfect ethical score."""
        result = TurnResult(tools_passed=True)
        score = constitutional_reward("send_message", result, has_mutations=True)
        assert score.ethical < 1.0
        assert score.ethical == 0.9

    def test_ethical_no_mutations(self):
        """No mutations gets perfect ethical score."""
        result = TurnResult(tools_passed=True)
        score = constitutional_reward("send_message", result, has_mutations=False)
        assert score.ethical == 1.0

    # === COMPOSABLE Tests ===

    def test_composable_few_tools(self):
        """Using few tools (<= 5) gets perfect composable score."""
        result = TurnResult(
            tools=[{"name": f"tool_{i}"} for i in range(5)],
        )
        score = constitutional_reward("send_message", result)
        assert score.composable == 1.0

    def test_composable_many_tools(self):
        """Using many tools (> 5) lowers composable score."""
        result = TurnResult(
            tools=[{"name": f"tool_{i}"} for i in range(10)],
        )
        score = constitutional_reward("send_message", result)
        assert score.composable < 1.0
        # 10 tools = 5 over limit, so 1.0 - 5*0.1 = 0.5
        assert score.composable == 0.5

    def test_composable_extreme_tools(self):
        """Extreme tool usage bottoms out at 0.5."""
        result = TurnResult(
            tools=[{"name": f"tool_{i}"} for i in range(100)],
        )
        score = constitutional_reward("send_message", result)
        assert score.composable >= 0.5  # Never goes below 0.5

    def test_composable_zero_tools(self):
        """Zero tools gets perfect composable score."""
        result = TurnResult(tools=[])
        score = constitutional_reward("send_message", result)
        assert score.composable == 1.0

    # === JOY_INDUCING Tests ===

    def test_joy_long_response(self):
        """Long response (>= 20 chars) gets perfect joy score."""
        result = TurnResult(response="This is a thoughtful response!")
        score = constitutional_reward("send_message", result)
        assert score.joy_inducing == 1.0

    def test_joy_short_response(self):
        """Short response (< 20 chars) gets lower joy score."""
        result = TurnResult(response="OK")  # 2 chars
        score = constitutional_reward("send_message", result)
        assert score.joy_inducing < 1.0
        # 2 chars: 0.5 + (2/20)*0.5 = 0.5 + 0.05 = 0.55
        assert score.joy_inducing == pytest.approx(0.55, abs=0.01)

    def test_joy_empty_response(self):
        """Empty response gets very low joy score."""
        result = TurnResult(response="")
        score = constitutional_reward("send_message", result)
        assert score.joy_inducing == 0.3

    def test_joy_exactly_20_chars(self):
        """Response of exactly 20 chars gets perfect score."""
        result = TurnResult(response="12345678901234567890")  # Exactly 20
        score = constitutional_reward("send_message", result)
        assert score.joy_inducing == 1.0

    # === Combined Tests ===

    def test_multiple_violations(self):
        """Multiple principle violations compound."""
        result = TurnResult(
            response="OK",  # Too short (joy)
            tools=[{"name": f"tool_{i}"} for i in range(10)],  # Too many (composable)
            tools_passed=False,  # Tools failed
        )
        score = constitutional_reward("send_message", result, has_mutations=True)
        # All three should be lowered
        assert score.ethical < 1.0
        assert score.composable < 1.0
        assert score.joy_inducing < 1.0
        # Others should be perfect
        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_weighted_total_with_violations(self):
        """Weighted total reflects principle violations."""
        result = TurnResult(
            response="OK",
            tools=[{"name": f"tool_{i}"} for i in range(10)],
            tools_passed=False,
        )
        score = constitutional_reward("send_message", result, has_mutations=True)
        total = score.weighted_total()

        # Manually compute expected:
        # ethical: 0.5 * 2.0 = 1.0
        # composable: 0.5 * 1.5 = 0.75
        # joy_inducing: ~0.55 * 1.2 = 0.66
        # others: 1.0 * 4 = 4.0
        # Total ≈ 6.41
        assert total < 8.7  # Less than perfect
        assert total == pytest.approx(6.41, abs=0.1)


# =============================================================================
# Principle Enum Tests
# =============================================================================


class TestPrincipleEnum:
    """Test Principle enumeration."""

    def test_all_seven_principles_exist(self):
        """All 7 Constitutional principles are defined."""
        principles = list(Principle)
        assert len(principles) == 7
        assert Principle.TASTEFUL in principles
        assert Principle.CURATED in principles
        assert Principle.ETHICAL in principles
        assert Principle.JOY_INDUCING in principles
        assert Principle.COMPOSABLE in principles
        assert Principle.HETERARCHICAL in principles
        assert Principle.GENERATIVE in principles

    def test_principle_values(self):
        """Principle enum values are lowercase snake_case."""
        assert Principle.TASTEFUL.value == "tasteful"
        assert Principle.CURATED.value == "curated"
        assert Principle.ETHICAL.value == "ethical"
        assert Principle.JOY_INDUCING.value == "joy_inducing"
        assert Principle.COMPOSABLE.value == "composable"
        assert Principle.HETERARCHICAL.value == "heterarchical"
        assert Principle.GENERATIVE.value == "generative"


# =============================================================================
# Integration Tests
# =============================================================================


class TestRewardIntegration:
    """Integration tests for Constitutional reward."""

    def test_reward_integrates_with_turn_result(self):
        """Constitutional reward works with real TurnResult instances."""
        # Simulate a real chat turn
        turn = TurnResult(
            tools_passed=True,
            tools=[
                {"name": "read_file", "status": "success"},
                {"name": "write_file", "status": "success"},
            ],
            user_corrected=False,
            signals=[],
            response="I've successfully read and updated the file for you!",
            stopping_suggestion=None,
        )

        score = constitutional_reward("send_message", turn, has_mutations=True)

        # Should get high scores (mutations acknowledged)
        assert score.ethical == 0.9  # Mutations but acknowledged
        assert score.composable == 1.0  # Only 2 tools
        assert score.joy_inducing == 1.0  # Good response length
        assert score.tasteful == 1.0
        assert score.curated == 1.0
        assert score.heterarchical == 1.0
        assert score.generative == 1.0

    def test_reward_score_serialization(self):
        """PrincipleScore can be serialized for storage."""
        result = TurnResult(response="Great work!")
        score = constitutional_reward("send_message", result)

        # Serialize
        data = score.to_dict()
        assert isinstance(data, dict)
        assert "ethical" in data
        assert "composable" in data

        # Deserialize
        restored = PrincipleScore.from_dict(data)
        assert restored.ethical == score.ethical
        assert restored.composable == score.composable
