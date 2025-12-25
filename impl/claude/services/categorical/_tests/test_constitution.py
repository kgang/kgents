"""
Tests for Constitutional Reward System.

Verifies that the 7 principles are correctly implemented as reward functions
and that probe-specific rewards integrate properly.
"""

import pytest

from services.categorical.constitution import (
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

    def test_ethical_has_highest_weight(self):
        """ETHICAL should have the highest weight (safety first)."""
        ethical_weight = PRINCIPLE_WEIGHTS[Principle.ETHICAL]
        for principle, weight in PRINCIPLE_WEIGHTS.items():
            if principle != Principle.ETHICAL:
                assert ethical_weight >= weight, f"ETHICAL weight should be highest, but {principle} has {weight}"

    def test_composable_second_highest(self):
        """COMPOSABLE should be second highest (architecture second)."""
        composable_weight = PRINCIPLE_WEIGHTS[Principle.COMPOSABLE]
        ethical_weight = PRINCIPLE_WEIGHTS[Principle.ETHICAL]

        assert composable_weight < ethical_weight
        for principle, weight in PRINCIPLE_WEIGHTS.items():
            if principle not in (Principle.ETHICAL, Principle.COMPOSABLE):
                assert composable_weight >= weight


class TestPrincipleScore:
    """Test PrincipleScore data structure."""

    def test_weighted_score_calculation(self):
        """Weighted score should multiply score by weight."""
        score = PrincipleScore(
            principle=Principle.ETHICAL,
            score=0.8,
            reasoning="Test",
        )
        expected = 0.8 * PRINCIPLE_WEIGHTS[Principle.ETHICAL]
        assert abs(score.weighted_score - expected) < 1e-6

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
    def sample_scores(self):
        """Sample principle scores for testing."""
        return (
            PrincipleScore(Principle.ETHICAL, 1.0, "Perfect ethical score"),
            PrincipleScore(Principle.COMPOSABLE, 0.8, "Good composition"),
            PrincipleScore(Principle.JOY_INDUCING, 0.6, "Some joy"),
        )

    def test_weighted_total_calculation(self, sample_scores):
        """Weighted total should normalize by total weight."""
        eval = ConstitutionalEvaluation(scores=sample_scores)

        # Manual calculation
        total_weighted = sum(s.weighted_score for s in sample_scores)
        total_weight = sum(PRINCIPLE_WEIGHTS[s.principle] for s in sample_scores)
        expected = total_weighted / total_weight

        assert abs(eval.weighted_total - expected) < 1e-6

    def test_by_principle_mapping(self, sample_scores):
        """Should create correct principle -> score mapping."""
        eval = ConstitutionalEvaluation(scores=sample_scores)
        by_principle = eval.by_principle

        assert by_principle[Principle.ETHICAL] == 1.0
        assert by_principle[Principle.COMPOSABLE] == 0.8
        assert by_principle[Principle.JOY_INDUCING] == 0.6

    def test_min_max_scores(self, sample_scores):
        """Should correctly identify min/max scores."""
        eval = ConstitutionalEvaluation(scores=sample_scores)

        assert eval.min_score == 0.6
        assert eval.max_score == 1.0

    def test_satisfies_threshold(self, sample_scores):
        """Should check if all principles meet threshold."""
        eval = ConstitutionalEvaluation(scores=sample_scores)

        assert eval.satisfies_threshold(0.5)  # All >= 0.6
        assert not eval.satisfies_threshold(0.7)  # 0.6 < 0.7

    def test_empty_scores(self):
        """Should handle empty scores gracefully."""
        eval = ConstitutionalEvaluation(scores=())

        assert eval.weighted_total == 0.0
        assert eval.min_score == 0.0
        assert eval.max_score == 0.0
        assert eval.by_principle == {}


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
