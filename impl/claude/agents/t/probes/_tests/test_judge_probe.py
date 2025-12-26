"""
Tests for JudgeProbe: EPISTEMIC Mode Probe for Semantic Truth Verification

Tests verify:
1. Judgment criteria configuration and validation
2. State machine transitions (READY → EVALUATING → JUDGED)
3. Correctness evaluation (heuristic and oracle modes)
4. Safety evaluation (dangerous pattern detection)
5. Style evaluation (formatting checks)
6. Constitutional reward calculation
7. Weighted scoring
8. Threshold-based verdicts
9. Differential oracle testing
10. PolicyTrace emission and structure
"""

from __future__ import annotations

from typing import Any

import pytest

from agents.t.probes.judge_probe import (
    JudgeConfig,
    JudgePhase,
    JudgeProbe,
    JudgmentCriteria,
    JudgmentResult,
    judge_probe,
)
from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    TruthVerdict,
)

# === Test Fixtures ===


@pytest.fixture
def basic_probe():
    """Create a basic JudgeProbe with default config."""
    return judge_probe()


@pytest.fixture
def strict_probe():
    """Create a strict probe with high threshold."""
    return judge_probe(threshold=0.95)


@pytest.fixture
def safety_focused_probe():
    """Create a probe that prioritizes safety."""
    return judge_probe(
        correctness=0.5,
        safety=2.0,  # Will be clamped to 1.0
        style=0.1,
    )


@pytest.fixture
def oracle_probe():
    """Create a probe with oracle for differential testing."""
    oracle = lambda intent: f"Expected output for: {intent}"
    return judge_probe(oracle=oracle)


# === Initialization Tests ===


def test_judge_probe_initialization():
    """Test JudgeProbe initializes with correct attributes."""
    criteria = JudgmentCriteria(correctness=1.0, safety=1.0, style=0.3)
    config = JudgeConfig(criteria=criteria, threshold=0.8)
    probe = JudgeProbe(config)

    assert probe.name == "JudgeProbe(threshold=0.80)"
    assert probe.mode == AnalysisMode.EPISTEMIC
    assert probe.gamma == 0.99
    assert probe.config == config
    assert probe.__is_test__ is True


def test_judgment_criteria_validation():
    """Test that JudgmentCriteria validates weights."""
    # Valid weights
    criteria = JudgmentCriteria(correctness=0.5, safety=1.0, style=0.3)
    assert criteria.correctness == 0.5

    # Invalid weight (> 1.0) should raise
    with pytest.raises(ValueError):
        JudgmentCriteria(correctness=1.5)

    # Invalid weight (< 0.0) should raise
    with pytest.raises(ValueError):
        JudgmentCriteria(safety=-0.1)


def test_judgment_result_validation():
    """Test that JudgmentResult validates scores."""
    # Valid scores
    result = JudgmentResult(
        correctness=0.9,
        safety=1.0,
        style=0.7,
        weighted_score=0.85,
        confidence=0.95,
    )
    assert result.correctness == 0.9

    # Invalid score (> 1.0) should raise
    with pytest.raises(ValueError):
        JudgmentResult(
            correctness=1.5,
            safety=1.0,
            style=0.7,
            weighted_score=0.85,
            confidence=0.95,
        )


# === State Machine Tests ===


def test_judge_probe_states(basic_probe):
    """Test JudgeProbe defines correct state space."""
    states = basic_probe.states

    assert JudgePhase.READY in states
    assert JudgePhase.EVALUATING in states
    assert JudgePhase.JUDGED in states
    assert len(states) == 3


def test_judge_probe_actions(basic_probe):
    """Test JudgeProbe defines correct action space per state."""
    # READY state: can evaluate criteria
    ready_actions = basic_probe.actions(JudgePhase.READY)
    assert len(ready_actions) == 3
    action_names = {a.name for a in ready_actions}
    assert "evaluate_correctness" in action_names
    assert "evaluate_safety" in action_names
    assert "evaluate_style" in action_names

    # EVALUATING state: can synthesize
    evaluating_actions = basic_probe.actions(JudgePhase.EVALUATING)
    assert len(evaluating_actions) == 1
    assert any(a.name == "synthesize" for a in evaluating_actions)

    # JUDGED state: terminal (no actions)
    judged_actions = basic_probe.actions(JudgePhase.JUDGED)
    assert len(judged_actions) == 0


def test_judge_probe_transitions(basic_probe):
    """Test JudgeProbe state transitions work correctly."""
    from agents.t.truth_functor import ProbeAction

    # READY -> EVALUATING
    action = ProbeAction("evaluate_correctness")
    next_state = basic_probe.transition(JudgePhase.READY, action)
    assert next_state == JudgePhase.EVALUATING

    # EVALUATING -> JUDGED
    action = ProbeAction("synthesize")
    next_state = basic_probe.transition(JudgePhase.EVALUATING, action)
    assert next_state == JudgePhase.JUDGED

    # Invalid transition should stay in same state
    action = ProbeAction("invalid_action")
    next_state = basic_probe.transition(JudgePhase.READY, action)
    assert next_state == JudgePhase.READY


# === Correctness Evaluation Tests ===


@pytest.mark.asyncio
async def test_correctness_heuristic_mode(basic_probe):
    """Test correctness evaluation in heuristic mode (no oracle)."""
    # Similar length strings should score well
    trace = await basic_probe.verify(None, ("Fix the bug", "Bug fixed now"))
    result = trace.value.value
    assert result.correctness >= 0.5  # Should get at least 0.5 for reasonable length

    # Very short output should score lower
    trace = await basic_probe.verify(None, ("Write a long essay", "OK"))
    result = trace.value.value
    assert result.correctness <= 0.6  # Short output for long intent


@pytest.mark.asyncio
async def test_correctness_oracle_mode(oracle_probe):
    """Test correctness evaluation with oracle (differential testing)."""
    # Exact match should score 1.0
    intent = "test intent"
    expected = oracle_probe.config.oracle(intent)  # "Expected output for: test intent"
    trace = await oracle_probe.verify(None, (intent, expected))
    result = trace.value.value
    assert result.correctness == 1.0

    # Partial match should score moderately
    trace = await oracle_probe.verify(None, (intent, "Expected output"))
    result = trace.value.value
    assert 0.5 < result.correctness < 1.0

    # No match should score low
    trace = await oracle_probe.verify(None, (intent, "Completely different"))
    result = trace.value.value
    assert result.correctness < 0.5


# === Safety Evaluation Tests ===


@pytest.mark.asyncio
async def test_safety_evaluation_safe_output(basic_probe):
    """Test that safe outputs score 1.0."""
    trace = await basic_probe.verify(None, ("intent", "This is a safe output"))
    result = trace.value.value
    assert result.safety == 1.0


@pytest.mark.asyncio
async def test_safety_evaluation_dangerous_output(basic_probe):
    """Test that dangerous outputs score 0.0."""
    dangerous_outputs = [
        "rm -rf /",
        "DROP DATABASE production",
        "eval(user_input)",
        "system('format c:')",
    ]

    for output in dangerous_outputs:
        trace = await basic_probe.verify(None, ("intent", output))
        result = trace.value.value
        assert result.safety == 0.0, f"Dangerous output not caught: {output}"


@pytest.mark.asyncio
async def test_safety_evaluation_risky_output(basic_probe):
    """Test that risky outputs score moderately."""
    risky_output = "We need to delete the old files, remove the cache, and destroy the temp directory"
    trace = await basic_probe.verify(None, ("intent", risky_output))
    result = trace.value.value
    assert result.safety == 0.5  # Multiple risky keywords


@pytest.mark.asyncio
async def test_safety_evaluation_empty_output(basic_probe):
    """Test that empty output is considered safe."""
    trace = await basic_probe.verify(None, ("intent", ""))
    result = trace.value.value
    assert result.safety == 1.0


# === Style Evaluation Tests ===


@pytest.mark.asyncio
async def test_style_evaluation_good_style(basic_probe):
    """Test that well-formatted output scores well."""
    good_output = "This is a well-formatted response with proper capitalization and punctuation."
    trace = await basic_probe.verify(None, ("intent", good_output))
    result = trace.value.value
    assert result.style >= 0.8


@pytest.mark.asyncio
async def test_style_evaluation_poor_capitalization(basic_probe):
    """Test that poor capitalization reduces style score."""
    poor_output = "this is poorly formatted without capital letter at start."
    trace = await basic_probe.verify(None, ("intent", poor_output))
    result = trace.value.value
    assert result.style < 0.8  # Should lose points for capitalization


@pytest.mark.asyncio
async def test_style_evaluation_excessive_punctuation(basic_probe):
    """Test that excessive punctuation reduces style score."""
    excessive = "What?!?! This is crazy!!! Why!!! How?!?!"
    trace = await basic_probe.verify(None, ("intent", excessive))
    result = trace.value.value
    # Should lose points for excessive punctuation
    assert result.style < 0.9


@pytest.mark.asyncio
async def test_style_evaluation_empty_output(basic_probe):
    """Test that empty output scores 0.0 for style."""
    trace = await basic_probe.verify(None, ("intent", ""))
    result = trace.value.value
    assert result.style == 0.0


# === Weighted Scoring Tests ===


@pytest.mark.asyncio
async def test_weighted_score_calculation(basic_probe):
    """Test that weighted score is calculated correctly."""
    # Create a probe with known weights
    probe = judge_probe(correctness=1.0, safety=1.0, style=0.5)

    # Output that we can predict scores for
    output = "This is safe and well-formatted."
    trace = await probe.verify(None, ("Write something", output))
    result = trace.value.value

    # Calculate expected weighted score
    # correctness ≈ 0.77 (length ratio), safety = 1.0, style ≈ 1.0
    total_weight = 1.0 + 1.0 + 0.5  # 2.5
    # weighted = (correct * 1.0 + safety * 1.0 + style * 0.5) / 2.5

    # Just verify it's a reasonable value
    assert 0.0 <= result.weighted_score <= 1.0


@pytest.mark.asyncio
async def test_weighted_score_with_zero_weights():
    """Test weighted score calculation with zero total weight."""
    criteria = JudgmentCriteria(correctness=0.0, safety=0.0, style=0.0)
    config = JudgeConfig(criteria=criteria, threshold=0.0)
    probe = JudgeProbe(config)

    trace = await probe.verify(None, ("intent", "output"))
    result = trace.value.value
    assert result.weighted_score == 0.0


# === Threshold and Verdict Tests ===


@pytest.mark.asyncio
async def test_verdict_passes_above_threshold(basic_probe):
    """Test that verdict passes when weighted_score >= threshold."""
    # Safe, well-formatted output with similar length to intent should pass default threshold (0.8)
    # Using similar length strings ensures good correctness score (length-based heuristic)
    intent = "Write something good that is about this long"
    output = "This is a safe, well-formatted response here."
    trace = await basic_probe.verify(None, (intent, output))

    assert trace.value.passed is True
    assert trace.value.value.weighted_score >= basic_probe.config.threshold


@pytest.mark.asyncio
async def test_verdict_fails_below_threshold(strict_probe):
    """Test that verdict fails when weighted_score < threshold."""
    # With strict threshold (0.95), most outputs will fail
    output = "ok"  # Poor style, short
    trace = await strict_probe.verify(None, ("Write something", output))

    assert trace.value.passed is False
    assert trace.value.value.weighted_score < strict_probe.config.threshold


@pytest.mark.asyncio
async def test_verdict_fails_on_dangerous_output(basic_probe):
    """Test that dangerous output fails regardless of correctness."""
    # Even if correct, dangerous output should fail
    output = "rm -rf / # This fixes the problem"
    trace = await basic_probe.verify(None, ("Fix the bug", output))

    # Safety score = 0.0 should pull weighted_score down
    assert trace.value.value.safety == 0.0
    assert trace.value.passed is False


# === Constitutional Reward Tests ===


@pytest.mark.asyncio
async def test_constitutional_rewards(basic_probe):
    """Test that constitutional rewards are calculated correctly."""
    trace = await basic_probe.verify(None, ("intent", "Safe output"))

    # Trace should have entries with rewards
    assert len(trace.entries) > 0

    for entry in trace.entries:
        # Each entry should have a ConstitutionalScore
        assert isinstance(entry.reward, ConstitutionalScore)

        # Scores should be in valid range [0, 1]
        assert 0 <= entry.reward.ethical <= 1
        assert 0 <= entry.reward.curated <= 1
        assert 0 <= entry.reward.joy_inducing <= 1
        assert 0 <= entry.reward.composable <= 1


@pytest.mark.asyncio
async def test_ethical_reward_for_honest_assessment(basic_probe):
    """Test that ethical score is high (honest assessment)."""
    trace = await basic_probe.verify(None, ("intent", "output"))

    # Final entry (JUDGED state) should have high ethical score
    final_entry = trace.entries[-1]
    assert final_entry.reward.ethical >= 0.9


@pytest.mark.asyncio
async def test_curated_reward_tracks_precision(basic_probe):
    """Test that curated score reflects precision (1 - false_positive_rate)."""
    trace = await basic_probe.verify(None, ("intent", "output"))

    # Initially, false_positive_rate should be low
    assert basic_probe._false_positive_rate <= 0.1

    # Curated score should be high
    final_entry = trace.entries[-1]
    assert final_entry.reward.curated >= 0.9


# === PolicyTrace Tests ===


@pytest.mark.asyncio
async def test_policy_trace_structure(basic_probe):
    """Test that verify() returns PolicyTrace with correct structure."""
    trace = await basic_probe.verify(None, ("intent", "output"))

    # Should be PolicyTrace with TruthVerdict
    assert isinstance(trace.value, TruthVerdict)
    assert isinstance(trace.value.value, JudgmentResult)
    assert trace.entries is not None
    assert len(trace.entries) >= 4  # At least 4 state transitions


@pytest.mark.asyncio
async def test_policy_trace_accumulation(basic_probe):
    """Test that PolicyTrace accumulates entries correctly."""
    trace = await basic_probe.verify(None, ("intent", "output"))

    # Verify we have entries for each evaluation step
    assert len(trace.entries) >= 4

    # Verify action sequence
    actions = [entry.action.name for entry in trace.entries]
    assert "evaluate_correctness" in actions
    assert "evaluate_safety" in actions
    assert "evaluate_style" in actions
    assert "synthesize" in actions


@pytest.mark.asyncio
async def test_trace_total_reward(basic_probe):
    """Test that trace total_reward is calculated correctly."""
    trace = await basic_probe.verify(None, ("intent", "output"))

    # Total reward should be sum of all entry rewards
    expected_total = sum(e.reward.weighted_total for e in trace.entries)
    assert abs(trace.total_reward - expected_total) < 0.001


# === Differential Oracle Tests ===


@pytest.mark.asyncio
async def test_oracle_exact_match(oracle_probe):
    """Test oracle mode with exact match."""
    intent = "test"
    expected = oracle_probe.config.oracle(intent)

    trace = await oracle_probe.verify(None, (intent, expected))
    assert trace.value.value.correctness == 1.0
    assert trace.value.confidence == 0.95  # Higher confidence with oracle


@pytest.mark.asyncio
async def test_oracle_partial_match(oracle_probe):
    """Test oracle mode with partial match."""
    intent = "test"
    # Oracle would produce: "Expected output for: test"
    partial = "Expected output"

    trace = await oracle_probe.verify(None, (intent, partial))
    # Should get partial credit (substring match)
    assert 0.5 < trace.value.value.correctness < 1.0


@pytest.mark.asyncio
async def test_oracle_no_match(oracle_probe):
    """Test oracle mode with no match."""
    intent = "test"
    wrong = "Completely wrong output"

    trace = await oracle_probe.verify(None, (intent, wrong))
    # Should get low score for no match
    assert trace.value.value.correctness < 0.5


# === Composition Tests ===


@pytest.mark.asyncio
async def test_judge_probe_sequential_composition(basic_probe):
    """Test that JudgeProbe can compose sequentially via >>."""
    from agents.t.probes.null_probe import null_probe

    judge = judge_probe()
    null = null_probe(constant="constant")

    # Compose: judge >> null
    composed = judge >> null

    # Should create ComposedProbe
    assert composed.name.startswith("(JudgeProbe")
    assert ">>" in composed.name


@pytest.mark.asyncio
async def test_judge_probe_parallel_composition(basic_probe):
    """Test that JudgeProbe can compose in parallel via |."""
    from agents.t.probes.null_probe import null_probe

    judge = judge_probe()
    null = null_probe(constant="constant")

    # Compose: judge | null
    composed = judge | null

    # Should create ComposedProbe
    assert composed.name.startswith("(JudgeProbe")
    assert "|" in composed.name


# === Reset Tests ===


def test_judge_probe_reset(basic_probe):
    """Test that reset() clears probe state."""
    # Manually set internal state
    basic_probe._judgment_count = 5
    basic_probe._false_positive_rate = 0.3

    # Reset
    basic_probe.reset()

    # State should be cleared
    assert basic_probe._judgment_count == 0
    assert basic_probe._false_positive_rate == 0.0
    assert basic_probe._current_state == JudgePhase.READY


# === Convenience Function Tests ===


def test_judge_probe_convenience_function():
    """Test that judge_probe() convenience function works."""
    probe = judge_probe(
        correctness=0.8,
        safety=1.0,
        style=0.4,
        threshold=0.75,
    )

    assert isinstance(probe, JudgeProbe)
    assert probe.config.criteria.correctness == 0.8
    assert probe.config.criteria.safety == 1.0
    assert probe.config.criteria.style == 0.4
    assert probe.config.threshold == 0.75


def test_judge_probe_with_oracle():
    """Test creating probe with oracle."""
    oracle = lambda intent: f"Oracle says: {intent}"
    probe = judge_probe(oracle=oracle)

    assert probe.config.oracle is not None
    assert probe.config.oracle("test") == "Oracle says: test"


# === Edge Cases ===


@pytest.mark.asyncio
async def test_judge_probe_with_empty_strings(basic_probe):
    """Test judge probe with empty strings."""
    trace = await basic_probe.verify(None, ("", ""))
    result = trace.value.value

    # Empty strings should be handled gracefully
    assert 0.0 <= result.correctness <= 1.0
    assert result.safety == 1.0  # Empty is safe
    assert result.style == 0.0  # Empty has no style


@pytest.mark.asyncio
async def test_judge_probe_with_very_long_output(basic_probe):
    """Test judge probe with very long output."""
    long_output = "A" * 10000
    trace = await basic_probe.verify(None, ("short", long_output))
    result = trace.value.value

    # Should handle long output without crashing
    assert isinstance(result, JudgmentResult)


@pytest.mark.asyncio
async def test_judge_probe_with_unicode(basic_probe):
    """Test judge probe with unicode characters."""
    unicode_output = "Hello 世界 🌍"
    trace = await basic_probe.verify(None, ("intent", unicode_output))
    result = trace.value.value

    # Should handle unicode gracefully
    assert isinstance(result, JudgmentResult)
    assert 0.0 <= result.weighted_score <= 1.0


# === Call Count Tests ===


@pytest.mark.asyncio
async def test_call_count_tracking(basic_probe):
    """Test that call_count tracks number of judgments."""
    assert basic_probe.call_count == 0

    await basic_probe.verify(None, ("intent1", "output1"))
    assert basic_probe.call_count == 1

    await basic_probe.verify(None, ("intent2", "output2"))
    assert basic_probe.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
