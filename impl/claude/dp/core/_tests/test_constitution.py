"""
Tests for Constitution: The 7 principles as reward function.

Verifies:
1. Default weights are correctly applied
2. Custom evaluators can be injected
3. Custom weights can be set
4. ValueScore is correctly computed
5. Reward is the weighted sum of principle scores
"""

import pytest

from dp.core.constitution import Constitution
from services.categorical.dp_bridge import Principle


def test_constitution_default_reward():
    """Default reward should be 0.5 (neutral) for all principles."""
    const = Constitution()

    reward = const.reward("state1", "action1", "state2")

    # All principles default to 0.5, so weighted average should be 0.5
    assert abs(reward - 0.5) < 1e-6


def test_constitution_default_weights():
    """Verify default weights match the specification."""
    const = Constitution()

    assert const.principle_weights[Principle.ETHICAL] == 2.0
    assert const.principle_weights[Principle.COMPOSABLE] == 1.5
    assert const.principle_weights[Principle.JOY_INDUCING] == 1.2
    assert const.principle_weights[Principle.TASTEFUL] == 1.0
    assert const.principle_weights[Principle.CURATED] == 1.0
    assert const.principle_weights[Principle.HETERARCHICAL] == 1.0
    assert const.principle_weights[Principle.GENERATIVE] == 1.0


def test_constitution_evaluate_structure():
    """Verify ValueScore structure from evaluate()."""
    const = Constitution()

    value_score = const.evaluate("state1", "action1", "state2")

    # Should have 7 principle scores (one for each principle)
    assert len(value_score.principle_scores) == 7

    # All should have default score of 0.5
    for ps in value_score.principle_scores:
        assert abs(ps.score - 0.5) < 1e-6

    # Should have correct weights
    principle_weights = {ps.principle: ps.weight for ps in value_score.principle_scores}
    assert principle_weights[Principle.ETHICAL] == 2.0
    assert principle_weights[Principle.COMPOSABLE] == 1.5
    assert principle_weights[Principle.JOY_INDUCING] == 1.2


def test_constitution_custom_evaluator():
    """Custom evaluators should override default behavior."""
    const = Constitution()

    # Set a custom evaluator for COMPOSABLE
    const.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 1.0 if a == "compose" else 0.0,
        lambda s, a, ns: f"Action '{a}' is compositional" if a == "compose" else "Not compositional"
    )

    # Test with compositional action
    value_score1 = const.evaluate("state1", "compose", "state2")
    composable_score1 = next(
        ps for ps in value_score1.principle_scores if ps.principle == Principle.COMPOSABLE
    )
    assert abs(composable_score1.score - 1.0) < 1e-6
    assert "compositional" in composable_score1.evidence.lower()

    # Test with non-compositional action
    value_score2 = const.evaluate("state1", "other", "state2")
    composable_score2 = next(
        ps for ps in value_score2.principle_scores if ps.principle == Principle.COMPOSABLE
    )
    assert abs(composable_score2.score - 0.0) < 1e-6
    assert "not compositional" in composable_score2.evidence.lower()


def test_constitution_custom_weight():
    """Custom weights should affect total reward."""
    const = Constitution()

    # Set custom weight for ETHICAL (make it even more important)
    const.set_weight(Principle.ETHICAL, 10.0)

    # Set custom evaluator for ETHICAL
    const.set_evaluator(
        Principle.ETHICAL,
        lambda s, a, ns: 1.0,  # Perfect ethical score
    )

    reward = const.reward("state1", "action1", "state2")

    # With ETHICAL at 10.0 weight and 1.0 score, total should be > 0.5
    assert reward > 0.5


def test_constitution_reward_equals_value_score_total():
    """reward() should equal evaluate().total_score."""
    const = Constitution()

    # Add some custom evaluators
    const.set_evaluator(Principle.COMPOSABLE, lambda s, a, ns: 0.8)
    const.set_evaluator(Principle.JOY_INDUCING, lambda s, a, ns: 0.9)
    const.set_evaluator(Principle.ETHICAL, lambda s, a, ns: 1.0)

    reward = const.reward("state1", "action1", "state2")
    value_score = const.evaluate("state1", "action1", "state2")

    # Should be exactly equal
    assert abs(reward - value_score.total_score) < 1e-9


def test_constitution_score_clamping():
    """Scores outside [0, 1] should be clamped."""
    const = Constitution()

    # Set evaluator that returns out-of-bounds values
    const.set_evaluator(Principle.COMPOSABLE, lambda s, a, ns: 2.0)  # > 1.0
    const.set_evaluator(Principle.ETHICAL, lambda s, a, ns: -1.0)    # < 0.0

    value_score = const.evaluate("state1", "action1", "state2")

    # Find the scores
    composable = next(
        ps for ps in value_score.principle_scores if ps.principle == Principle.COMPOSABLE
    )
    ethical = next(
        ps for ps in value_score.principle_scores if ps.principle == Principle.ETHICAL
    )

    # Should be clamped to [0, 1]
    assert composable.score == 1.0
    assert ethical.score == 0.0


def test_constitution_weighted_sum_formula():
    """Verify the weighted sum formula: R(s,a,s') = Σᵢ wᵢ · Rᵢ(s,a,s')."""
    const = Constitution()

    # Set specific evaluators
    const.set_evaluator(Principle.COMPOSABLE, lambda s, a, ns: 0.8)
    const.set_evaluator(Principle.ETHICAL, lambda s, a, ns: 1.0)
    const.set_evaluator(Principle.JOY_INDUCING, lambda s, a, ns: 0.6)

    value_score = const.evaluate("state1", "action1", "state2")

    # Manual computation of weighted sum
    total_weight = sum(ps.weight for ps in value_score.principle_scores)
    weighted_sum = sum(ps.score * ps.weight for ps in value_score.principle_scores)
    expected_reward = weighted_sum / total_weight

    # Should match value_score.total_score
    assert abs(value_score.total_score - expected_reward) < 1e-9

    # Should match reward()
    reward = const.reward("state1", "action1", "state2")
    assert abs(reward - expected_reward) < 1e-9


def test_constitution_all_principles_evaluated():
    """All 7 principles should be evaluated."""
    const = Constitution()

    value_score = const.evaluate("state1", "action1", "state2")

    # Extract principle set
    evaluated_principles = {ps.principle for ps in value_score.principle_scores}

    # Should have all 7 principles
    assert evaluated_principles == set(Principle)


def test_constitution_state_action_independence():
    """Different states/actions should be independently evaluated."""
    const = Constitution()

    # Set state-dependent evaluator
    const.set_evaluator(
        Principle.COMPOSABLE,
        lambda s, a, ns: 1.0 if s == "good_state" else 0.0
    )

    reward1 = const.reward("good_state", "action", "next_state")
    reward2 = const.reward("bad_state", "action", "next_state")

    # Should be different
    assert abs(reward1 - reward2) > 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
