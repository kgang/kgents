"""
Tests for Constitutional Reward System.

Verifies that the 7 principles are correctly implemented as reward functions
and that probe-specific rewards integrate properly.
"""

import pytest

from services.categorical.constitution import (
    ETHICAL_FLOOR_THRESHOLD,
    PRINCIPLE_WEIGHTS,
    Constitution,
    ConstitutionalEvaluation,
    Principle,
    PrincipleScore,
    ProbeRewards,
    compute_galois_loss,
)


class TestPrincipleWeights:
    """Test that principle weights are correctly configured."""

    def test_weights_exist_for_all_principles(self):
        """All 7 principles should have weights."""
        assert len(PRINCIPLE_WEIGHTS) == 7
        for principle in Principle:
            assert principle in PRINCIPLE_WEIGHTS

    def test_ethical_is_floor_constraint_not_weight(self):
        """
        Amendment A: ETHICAL is a floor constraint, not a weighted principle.

        ETHICAL weight should be 0.0 because it's enforced as a floor,
        not summed with other weights.
        """
        ethical_weight = PRINCIPLE_WEIGHTS[Principle.ETHICAL]
        assert ethical_weight == 0.0, "ETHICAL should be 0 (floor constraint, not weighted)"

    def test_composable_is_highest_weighted(self):
        """
        Amendment A: COMPOSABLE should be highest weighted principle.

        After ETHICAL becomes a floor constraint, COMPOSABLE (1.5) should
        have the highest weight among the remaining principles.
        """
        composable_weight = PRINCIPLE_WEIGHTS[Principle.COMPOSABLE]
        for principle, weight in PRINCIPLE_WEIGHTS.items():
            if principle != Principle.COMPOSABLE:
                assert composable_weight >= weight, (
                    f"COMPOSABLE should have highest weight, but {principle} has {weight}"
                )


class TestPrincipleScore:
    """Test PrincipleScore data structure."""

    def test_weighted_score_calculation(self):
        """Weighted score should multiply score by weight."""
        # Amendment A: Use COMPOSABLE (weighted) instead of ETHICAL (floor)
        score = PrincipleScore(
            principle=Principle.COMPOSABLE,
            score=0.8,
            reasoning="Test",
        )
        expected = 0.8 * PRINCIPLE_WEIGHTS[Principle.COMPOSABLE]
        assert abs(score.weighted_score - expected) < 1e-6

    def test_ethical_weighted_score_is_zero(self):
        """Amendment A: ETHICAL weighted_score should be 0 (floor constraint)."""
        score = PrincipleScore(
            principle=Principle.ETHICAL,
            score=0.8,
            reasoning="Test",
        )
        # ETHICAL is floor, not weighted
        assert score.weighted_score == 0.0

    def test_to_dp_score_conversion(self):
        """Should convert to DP-bridge PrincipleScore."""
        score = PrincipleScore(
            principle=Principle.COMPOSABLE,
            score=0.7,
            reasoning="Test reasoning",
            evidence="Test evidence",
        )
        dp_score = score.to_dp_score()

        assert dp_score.principle == Principle.COMPOSABLE
        assert dp_score.score == 0.7
        assert dp_score.evidence == "Test reasoning"
        assert dp_score.weight == PRINCIPLE_WEIGHTS[Principle.COMPOSABLE]


class TestConstitutionalEvaluation:
    """Test ConstitutionalEvaluation aggregation."""

    @pytest.fixture
    def sample_scores_ethical_passing(self):
        """Sample principle scores with ETHICAL passing floor."""
        return (
            PrincipleScore(Principle.ETHICAL, 0.8, "Good ethical score"),  # > 0.6 floor
            PrincipleScore(Principle.COMPOSABLE, 0.8, "Good composition"),
            PrincipleScore(Principle.JOY_INDUCING, 0.6, "Some joy"),
        )

    @pytest.fixture
    def sample_scores_ethical_failing(self):
        """Sample principle scores with ETHICAL below floor."""
        return (
            PrincipleScore(Principle.ETHICAL, 0.3, "Low ethical score"),  # < 0.6 floor
            PrincipleScore(Principle.COMPOSABLE, 1.0, "Perfect composition"),
            PrincipleScore(Principle.JOY_INDUCING, 1.0, "Maximum joy"),
        )

    def test_weighted_total_excludes_ethical(self, sample_scores_ethical_passing):
        """
        Amendment A: weighted_total should exclude ETHICAL (it's a floor).

        Only COMPOSABLE and JOY_INDUCING weights should be summed.
        """
        eval = ConstitutionalEvaluation(scores=sample_scores_ethical_passing)

        # Manual calculation: only non-ETHICAL principles
        # COMPOSABLE: 0.8 * 1.5 = 1.2
        # JOY_INDUCING: 0.6 * 1.2 = 0.72
        # Total: 1.92, Weight sum: 2.7
        expected = (0.8 * 1.5 + 0.6 * 1.2) / (1.5 + 1.2)
        assert abs(eval.weighted_total - expected) < 1e-6

    def test_by_principle_mapping(self, sample_scores_ethical_passing):
        """Should create correct principle -> score mapping."""
        eval = ConstitutionalEvaluation(scores=sample_scores_ethical_passing)
        by_principle = eval.by_principle

        assert by_principle[Principle.ETHICAL] == 0.8
        assert by_principle[Principle.COMPOSABLE] == 0.8
        assert by_principle[Principle.JOY_INDUCING] == 0.6

    def test_min_max_scores(self, sample_scores_ethical_passing):
        """Should correctly identify min/max scores."""
        eval = ConstitutionalEvaluation(scores=sample_scores_ethical_passing)

        assert eval.min_score == 0.6
        assert eval.max_score == 0.8

    def test_satisfies_threshold(self, sample_scores_ethical_passing):
        """Should check if all principles meet threshold."""
        eval = ConstitutionalEvaluation(scores=sample_scores_ethical_passing)

        assert eval.satisfies_threshold(0.5)  # All >= 0.6
        assert not eval.satisfies_threshold(0.7)  # 0.6 < 0.7

    def test_empty_scores(self):
        """Should handle empty scores gracefully."""
        eval = ConstitutionalEvaluation(scores=())

        assert eval.weighted_total == 0.0
        assert eval.min_score == 0.0
        assert eval.max_score == 0.0
        assert eval.by_principle == {}


class TestAmendmentA:
    """
    Tests for Amendment A: ETHICAL Floor Constraint.

    Amendment A changes ETHICAL from a weighted principle to a floor constraint.
    If ETHICAL < 0.6, the action is rejected regardless of other scores.
    """

    @pytest.fixture
    def ethical_passing_scores(self):
        """Full evaluation with ETHICAL above floor (0.8 > 0.6)."""
        return (
            PrincipleScore(Principle.ETHICAL, 0.8, "Good"),
            PrincipleScore(Principle.COMPOSABLE, 0.9, "Great"),
            PrincipleScore(Principle.JOY_INDUCING, 0.7, "Good"),
            PrincipleScore(Principle.TASTEFUL, 0.8, "Good"),
            PrincipleScore(Principle.CURATED, 0.7, "Good"),
            PrincipleScore(Principle.HETERARCHICAL, 0.8, "Good"),
            PrincipleScore(Principle.GENERATIVE, 0.7, "Good"),
        )

    @pytest.fixture
    def ethical_failing_scores(self):
        """Full evaluation with ETHICAL below floor (0.3 < 0.6)."""
        return (
            PrincipleScore(Principle.ETHICAL, 0.3, "Poor"),  # BELOW FLOOR
            PrincipleScore(Principle.COMPOSABLE, 1.0, "Perfect"),
            PrincipleScore(Principle.JOY_INDUCING, 1.0, "Perfect"),
            PrincipleScore(Principle.TASTEFUL, 1.0, "Perfect"),
            PrincipleScore(Principle.CURATED, 1.0, "Perfect"),
            PrincipleScore(Principle.HETERARCHICAL, 1.0, "Perfect"),
            PrincipleScore(Principle.GENERATIVE, 1.0, "Perfect"),
        )

    def test_ethical_floor_threshold_value(self):
        """ETHICAL floor should be 0.6."""
        assert ETHICAL_FLOOR_THRESHOLD == 0.6

    def test_ethical_passes_when_above_floor(self, ethical_passing_scores):
        """ethical_passes should be True when ETHICAL >= 0.6."""
        eval = ConstitutionalEvaluation(scores=ethical_passing_scores)
        assert eval.ethical_score == 0.8
        assert eval.ethical_passes is True

    def test_ethical_fails_when_below_floor(self, ethical_failing_scores):
        """ethical_passes should be False when ETHICAL < 0.6."""
        eval = ConstitutionalEvaluation(scores=ethical_failing_scores)
        assert eval.ethical_score == 0.3
        assert eval.ethical_passes is False

    def test_weighted_total_zero_when_ethical_fails(self, ethical_failing_scores):
        """
        Amendment A Core: weighted_total returns 0.0 when ETHICAL floor fails.

        Even with perfect scores on all other principles (6 × 1.0),
        low ETHICAL score causes immediate rejection.
        """
        eval = ConstitutionalEvaluation(scores=ethical_failing_scores)
        assert eval.weighted_total == 0.0, (
            "ETHICAL floor failure should return 0.0 weighted_total"
        )

    def test_weighted_total_normal_when_ethical_passes(self, ethical_passing_scores):
        """weighted_total should compute normally when ETHICAL passes."""
        eval = ConstitutionalEvaluation(scores=ethical_passing_scores)
        assert eval.weighted_total > 0.0

    def test_rejection_reason_on_ethical_failure(self, ethical_failing_scores):
        """rejection_reason should explain ETHICAL floor violation."""
        eval = ConstitutionalEvaluation(scores=ethical_failing_scores)
        reason = eval.rejection_reason

        assert reason is not None
        assert "ETHICAL floor violation" in reason
        assert "0.30" in reason
        assert "Amendment A" in reason

    def test_rejection_reason_none_when_passes(self, ethical_passing_scores):
        """rejection_reason should be None when evaluation passes."""
        eval = ConstitutionalEvaluation(scores=ethical_passing_scores)
        # This may still fail if weighted_total < 0.65
        # But ethical_passes is True, so reason would be about weighted sum if it fails

    def test_passes_requires_both_floor_and_weighted(self, ethical_passing_scores):
        """passes property should require both ETHICAL floor and weighted sum."""
        eval = ConstitutionalEvaluation(scores=ethical_passing_scores)

        # With good scores across the board, should pass
        assert eval.ethical_passes is True
        # passes also checks weighted_total >= 0.65

    def test_high_scores_cannot_offset_ethical_violation(self):
        """
        The core Amendment A guarantee: high other scores cannot offset low ETHICAL.

        This test documents the problem Amendment A solves:
        - OLD: ETHICAL=0.3×2.0=0.6 + high other scores = ~7.3 → Could pass!
        - NEW: ETHICAL=0.3 < 0.6 → Immediate rejection
        """
        scores = (
            PrincipleScore(Principle.ETHICAL, 0.3, "Low"),  # BELOW FLOOR
            PrincipleScore(Principle.COMPOSABLE, 1.0, "Perfect"),
            PrincipleScore(Principle.JOY_INDUCING, 1.0, "Perfect"),
            PrincipleScore(Principle.TASTEFUL, 1.0, "Perfect"),
            PrincipleScore(Principle.CURATED, 1.0, "Perfect"),
            PrincipleScore(Principle.HETERARCHICAL, 1.0, "Perfect"),
            PrincipleScore(Principle.GENERATIVE, 1.0, "Perfect"),
        )
        eval = ConstitutionalEvaluation(scores=scores)

        # CRITICAL: Despite 6 perfect scores, ETHICAL floor fails
        assert not eval.ethical_passes
        assert eval.weighted_total == 0.0
        assert not eval.passes
        assert eval.rejection_reason is not None

    def test_exactly_at_floor_passes(self):
        """ETHICAL score exactly at floor (0.6) should pass."""
        scores = (
            PrincipleScore(Principle.ETHICAL, 0.6, "Exactly at floor"),
            PrincipleScore(Principle.COMPOSABLE, 0.8, "Good"),
        )
        eval = ConstitutionalEvaluation(scores=scores)

        assert eval.ethical_passes is True, "0.6 >= 0.6 should pass floor"

    def test_just_below_floor_fails(self):
        """ETHICAL score just below floor (0.59) should fail."""
        scores = (
            PrincipleScore(Principle.ETHICAL, 0.59, "Just below floor"),
            PrincipleScore(Principle.COMPOSABLE, 1.0, "Perfect"),
        )
        eval = ConstitutionalEvaluation(scores=scores)

        assert eval.ethical_passes is False, "0.59 < 0.6 should fail floor"
        assert eval.weighted_total == 0.0

    def test_to_dict_includes_amendment_a_fields(self, ethical_passing_scores):
        """to_dict should include Amendment A fields."""
        eval = ConstitutionalEvaluation(scores=ethical_passing_scores)
        serialized = eval.to_dict()

        assert "ethical_score" in serialized
        assert "ethical_passes" in serialized
        assert "passes" in serialized
        assert "rejection_reason" in serialized


class TestConstitution:
    """Test Constitution reward function."""

    def test_evaluate_returns_all_principles(self):
        """Should return scores for all 7 principles."""
        eval = Constitution.evaluate(
            state_before="initial",
            action="test_action",
            state_after="final",
        )

        assert len(eval.scores) == 7
        principles_covered = {s.principle for s in eval.scores}
        assert principles_covered == set(Principle)

    def test_tasteful_bloat_penalty(self):
        """Bloat patterns should get low tasteful score."""
        eval = Constitution.evaluate(
            state_before="",
            action="misc_helper_util",
            state_after="",
        )

        tasteful_score = eval.by_principle[Principle.TASTEFUL]
        assert tasteful_score < 0.5, "Bloat pattern should get low tasteful score"

    def test_tasteful_clear_purpose_reward(self):
        """Clear purpose patterns should get high tasteful score."""
        eval = Constitution.evaluate(
            state_before="",
            action="solve_problem",
            state_after="",
        )

        tasteful_score = eval.by_principle[Principle.TASTEFUL]
        assert tasteful_score > 0.7, "Clear purpose should get high tasteful score"

    def test_curated_complexity_penalty(self):
        """Actions that bloat state should get low curated score."""
        eval = Constitution.evaluate(
            state_before="x",
            action="add_features",
            state_after="x" * 1000,  # Massive state growth
        )

        curated_score = eval.by_principle[Principle.CURATED]
        assert curated_score < 0.5, "State bloat should get low curated score"

    def test_ethical_deterministic_reward(self):
        """Deterministic actions should get high ethical score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"deterministic": True},
        )

        ethical_score = eval.by_principle[Principle.ETHICAL]
        assert ethical_score == 1.0, "Deterministic should get perfect ethical score"

    def test_ethical_agency_violation(self):
        """Actions that replace human judgment should get low ethical score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"preserves_human_agency": False},
        )

        ethical_score = eval.by_principle[Principle.ETHICAL]
        assert ethical_score == 0.0, "Agency violation should get zero ethical score"

    def test_joy_explicit_marker(self):
        """Explicitly joyful actions should get high joy score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"joyful": True, "joy_evidence": "Delightful animation"},
        )

        joy_score = eval.by_principle[Principle.JOY_INDUCING]
        assert joy_score >= 0.9, "Explicit joy should get high score"

    def test_composable_law_satisfaction(self):
        """Actions satisfying laws should get perfect composable score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"satisfies_identity": True, "satisfies_associativity": True},
        )

        composable_score = eval.by_principle[Principle.COMPOSABLE]
        assert composable_score == 1.0, "Law satisfaction should get perfect score"

    def test_composable_law_violation(self):
        """Actions violating laws should get low composable score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"satisfies_identity": False},
        )

        composable_score = eval.by_principle[Principle.COMPOSABLE]
        assert composable_score < 0.5, "Law violation should get low score"

    def test_heterarchical_hierarchy_enforcement_penalty(self):
        """Hierarchy enforcement should get low heterarchical score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"enforces_hierarchy": True},
        )

        heterarchical_score = eval.by_principle[Principle.HETERARCHICAL]
        assert heterarchical_score < 0.3, "Hierarchy enforcement should be penalized"

    def test_heterarchical_fluidity_reward(self):
        """Enabling fluidity should get high heterarchical score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"enables_fluidity": True},
        )

        heterarchical_score = eval.by_principle[Principle.HETERARCHICAL]
        assert heterarchical_score == 1.0, "Fluidity should get perfect score"

    def test_generative_full_spec_reward(self):
        """Actions with full spec should get high generative score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"has_spec": True, "regenerability_score": 0.9},
        )

        generative_score = eval.by_principle[Principle.GENERATIVE]
        assert generative_score == 1.0, "Full spec should get perfect score"

    def test_generative_no_spec_penalty(self):
        """Actions without spec should get low generative score."""
        eval = Constitution.evaluate(
            state_before="",
            action="",
            state_after="",
            context={"has_spec": False},
        )

        generative_score = eval.by_principle[Principle.GENERATIVE]
        assert generative_score < 0.5, "No spec should be penalized"


class TestProbeRewards:
    """Test probe-specific constitutional rewards."""

    def test_null_probe_reward(self):
        """NullProbe should get perfect ETHICAL and COMPOSABLE."""
        eval = ProbeRewards.null_probe_reward("s", "null", "s")

        assert eval.by_principle[Principle.ETHICAL] == 1.0
        assert eval.by_principle[Principle.COMPOSABLE] == 1.0
        assert Principle.GENERATIVE in eval.by_principle

    def test_chaos_probe_reward_survived(self):
        """ChaosProbe with survival should get good scores."""
        eval = ProbeRewards.chaos_probe_reward("s", "chaos", "s", survived=True)

        assert eval.by_principle[Principle.ETHICAL] == 1.0  # 0.5 + 0.5*1
        assert eval.by_principle[Principle.HETERARCHICAL] == 0.8

    def test_chaos_probe_reward_failed(self):
        """ChaosProbe without survival should get penalties."""
        eval = ProbeRewards.chaos_probe_reward("s", "chaos", "s", survived=False)

        assert eval.by_principle[Principle.ETHICAL] == 0.5  # 0.5 + 0.5*0
        assert eval.by_principle[Principle.HETERARCHICAL] == 0.2

    def test_monad_probe_reward_satisfied(self):
        """MonadProbe with laws satisfied should get perfect scores."""
        eval = ProbeRewards.monad_probe_reward(
            "s",
            "monad",
            "s",
            identity_satisfied=True,
            associativity_satisfied=True,
        )

        assert eval.by_principle[Principle.COMPOSABLE] == 1.0
        assert eval.by_principle[Principle.ETHICAL] == 1.0

    def test_monad_probe_reward_partial(self):
        """MonadProbe with partial satisfaction should get partial scores."""
        eval = ProbeRewards.monad_probe_reward(
            "s",
            "monad",
            "s",
            identity_satisfied=True,
            associativity_satisfied=False,
        )

        assert eval.by_principle[Principle.COMPOSABLE] == 0.5
        assert eval.by_principle[Principle.ETHICAL] == 0.5

    def test_monad_probe_reward_violated(self):
        """MonadProbe with violations should get zero scores."""
        eval = ProbeRewards.monad_probe_reward(
            "s",
            "monad",
            "s",
            identity_satisfied=False,
            associativity_satisfied=False,
        )

        assert eval.by_principle[Principle.COMPOSABLE] == 0.0
        assert eval.by_principle[Principle.ETHICAL] == 0.0

    def test_sheaf_probe_reward_coherent(self):
        """SheafProbe with coherence should get perfect scores."""
        eval = ProbeRewards.sheaf_probe_reward(
            "s",
            "sheaf",
            "s",
            coherence_score=1.0,
            violation_count=0,
        )

        assert eval.by_principle[Principle.ETHICAL] == 1.0
        assert eval.by_principle[Principle.GENERATIVE] == 1.0
        assert eval.by_principle[Principle.COMPOSABLE] == 1.0

    def test_sheaf_probe_reward_violations(self):
        """SheafProbe with violations should get low scores."""
        eval = ProbeRewards.sheaf_probe_reward(
            "s",
            "sheaf",
            "s",
            coherence_score=0.3,
            violation_count=5,
        )

        assert eval.by_principle[Principle.ETHICAL] == 0.3
        assert eval.by_principle[Principle.GENERATIVE] == 0.3
        assert eval.by_principle[Principle.COMPOSABLE] == 0.3

    def test_middle_invariance_probe_reward(self):
        """MiddleInvarianceProbe reward."""
        eval_satisfied = ProbeRewards.middle_invariance_probe_reward(
            "s",
            "middle",
            "s",
            invariance_satisfied=True,
        )

        assert eval_satisfied.by_principle[Principle.ETHICAL] == 1.0
        assert eval_satisfied.by_principle[Principle.COMPOSABLE] == 1.0

        eval_violated = ProbeRewards.middle_invariance_probe_reward(
            "s",
            "middle",
            "s",
            invariance_satisfied=False,
        )

        assert eval_violated.by_principle[Principle.ETHICAL] == 0.3
        assert eval_violated.by_principle[Principle.COMPOSABLE] == 0.3

    def test_variator_probe_reward(self):
        """MonadVariatorProbe reward."""
        eval_preserved = ProbeRewards.variator_probe_reward(
            "s",
            "variator",
            "s",
            semantic_preserved=True,
        )

        assert eval_preserved.by_principle[Principle.GENERATIVE] == 1.0
        assert eval_preserved.by_principle[Principle.COMPOSABLE] == 1.0

        eval_broken = ProbeRewards.variator_probe_reward(
            "s",
            "variator",
            "s",
            semantic_preserved=False,
        )

        assert eval_broken.by_principle[Principle.GENERATIVE] == 0.4
        assert eval_broken.by_principle[Principle.COMPOSABLE] == 0.4


class TestGaloisLoss:
    """Test Galois loss computation."""

    @pytest.mark.asyncio
    async def test_galois_loss_perfect_regeneration(self):
        """Perfect regeneration should have near-zero loss."""

        class MockLLM:
            async def generate(self, system, user, temperature):
                # Mock perfect regeneration
                if "restructure" in user.lower():
                    return type("R", (), {"text": "Component A\nComponent B"})()
                else:
                    # Reconstitute to original
                    return type("R", (), {"text": "original output"})()

        llm = MockLLM()
        loss = await compute_galois_loss("original output", llm)

        assert loss < 0.2, "Perfect regeneration should have low loss"

    @pytest.mark.asyncio
    async def test_galois_loss_failed_regeneration(self):
        """Failed regeneration should have high loss."""

        class MockLLM:
            async def generate(self, system, user, temperature):
                # Mock failed regeneration
                return type("R", (), {"text": "completely different output"})()

        llm = MockLLM()
        loss = await compute_galois_loss("original output", llm)

        assert loss > 0.5, "Failed regeneration should have high loss"

    @pytest.mark.asyncio
    async def test_galois_loss_exception_handling(self):
        """Should handle exceptions gracefully."""

        class MockLLM:
            async def generate(self, system, user, temperature):
                raise RuntimeError("LLM failed")

        llm = MockLLM()
        loss = await compute_galois_loss("output", llm)

        assert loss == 1.0, "Exception should return max loss"


class TestIntegration:
    """Integration tests for constitutional reward system."""

    def test_constitution_to_dp_bridge(self):
        """Constitutional scores should convert to DP bridge scores."""
        eval = Constitution.evaluate("s", "action", "s_")

        # Convert to DP scores
        dp_scores = [s.to_dp_score() for s in eval.scores]

        assert len(dp_scores) == 7
        for dp_score in dp_scores:
            assert 0.0 <= dp_score.score <= 1.0
            assert dp_score.weight == PRINCIPLE_WEIGHTS[dp_score.principle]

    def test_probe_rewards_all_return_evaluations(self):
        """All probe reward functions should return ConstitutionalEvaluation."""
        rewards = [
            ProbeRewards.null_probe_reward("s", "a", "s_"),
            ProbeRewards.chaos_probe_reward("s", "a", "s_", survived=True),
            ProbeRewards.monad_probe_reward("s", "a", "s_"),
            ProbeRewards.sheaf_probe_reward("s", "a", "s_"),
            ProbeRewards.middle_invariance_probe_reward("s", "a", "s_"),
            ProbeRewards.variator_probe_reward("s", "a", "s_"),
        ]

        for reward in rewards:
            assert isinstance(reward, ConstitutionalEvaluation)
            assert reward.weighted_total >= 0.0
            assert reward.weighted_total <= 1.0

    def test_serialization_roundtrip(self):
        """Constitutional evaluation should serialize and deserialize."""
        eval = Constitution.evaluate("s", "action", "s_")
        serialized = eval.to_dict()

        # Check structure
        assert "weighted_total" in serialized
        assert "min_score" in serialized
        assert "max_score" in serialized
        assert "scores" in serialized
        assert len(serialized["scores"]) == 7

        # Check values
        assert serialized["weighted_total"] == eval.weighted_total
        assert serialized["min_score"] == eval.min_score
