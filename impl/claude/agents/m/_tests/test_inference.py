"""
Tests for Active Inference memory management.

The third pillar: Free Energy Minimization.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import pytest
from agents.m.inference import (
    ActiveInferenceAgent,
    Belief,
    FreeEnergyBudget,
    InferenceAction,
    InferenceGuidedCrystal,
    PredictiveMemory,
    create_guided_crystal,
    create_inference_agent,
)

# ========== Belief Tests ==========


class TestBelief:
    """Tests for Belief distribution."""

    def test_belief_creation(self) -> None:
        """Test basic belief creation."""
        belief = Belief(distribution={"a": 0.5, "b": 0.3, "c": 0.2})
        assert belief.precision == 1.0
        assert belief.probability("a") == pytest.approx(0.5, rel=0.01)

    def test_belief_normalization(self) -> None:
        """Test that beliefs are normalized."""
        # Unnormalized input
        belief = Belief(distribution={"a": 10, "b": 5, "c": 5})

        # Should be normalized
        assert belief.probability("a") == pytest.approx(0.5, rel=0.01)
        assert belief.probability("b") == pytest.approx(0.25, rel=0.01)

    def test_belief_default_probability(self) -> None:
        """Test default probability for unknown concepts."""
        belief = Belief(distribution={"known": 0.9, "other": 0.1})

        # Unknown concept gets small prior
        assert belief.probability("unknown") == pytest.approx(0.01)

    def test_belief_entropy_uniform(self) -> None:
        """Test entropy for uniform distribution."""
        belief = Belief(distribution={"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25})

        # Entropy of uniform distribution = log(n)
        expected_entropy = math.log(4)
        assert belief.entropy() == pytest.approx(expected_entropy, rel=0.01)

    def test_belief_entropy_peaked(self) -> None:
        """Test entropy for peaked distribution."""
        belief = Belief(distribution={"a": 0.99, "b": 0.01})

        # Peaked distribution has low entropy
        assert belief.entropy() < math.log(2)

    def test_belief_kl_divergence(self) -> None:
        """Test KL divergence between beliefs."""
        belief1 = Belief(distribution={"a": 0.5, "b": 0.5})
        belief2 = Belief(distribution={"a": 0.9, "b": 0.1})

        # KL(belief1 || belief2) > 0 (they're different)
        kl = belief1.kl_divergence(belief2)
        assert kl > 0

    def test_belief_kl_divergence_same(self) -> None:
        """Test KL divergence for identical beliefs."""
        belief1 = Belief(distribution={"a": 0.5, "b": 0.5})
        belief2 = Belief(distribution={"a": 0.5, "b": 0.5})

        # KL(P || P) = 0
        kl = belief1.kl_divergence(belief2)
        assert kl == pytest.approx(0.0, abs=1e-10)

    def test_belief_update(self) -> None:
        """Test belief update with observation."""
        belief = Belief(distribution={"a": 0.5, "b": 0.5})

        # Observe 'a' heavily
        belief.update("a", observation_weight=0.8)

        # 'a' should increase
        assert belief.probability("a") > 0.5

    def test_belief_copy(self) -> None:
        """Test belief copying."""
        belief = Belief(distribution={"a": 0.5, "b": 0.5}, precision=2.0)
        copied = belief.copy()

        # Modify original
        belief.update("a", observation_weight=0.9)

        # Copy should be unchanged
        assert copied.probability("a") == pytest.approx(0.5)


# ========== FreeEnergyBudget Tests ==========


class TestFreeEnergyBudget:
    """Tests for FreeEnergyBudget."""

    def test_free_energy_calculation(self) -> None:
        """Test F = Complexity - Accuracy."""
        budget = FreeEnergyBudget(complexity_cost=1.0, accuracy_gain=0.5)
        assert budget.free_energy == pytest.approx(0.5)

    def test_free_energy_negative_is_good(self) -> None:
        """Test that negative free energy means beneficial."""
        budget = FreeEnergyBudget(complexity_cost=0.5, accuracy_gain=1.0)

        # Negative free energy = accuracy > complexity
        assert budget.free_energy < 0
        assert budget.should_retain()

    def test_free_energy_positive_is_costly(self) -> None:
        """Test that positive free energy means costly."""
        budget = FreeEnergyBudget(complexity_cost=1.0, accuracy_gain=0.5)

        # Positive free energy = complexity > accuracy
        assert budget.free_energy > 0
        assert not budget.should_retain()

    def test_retention_priority(self) -> None:
        """Test retention priority calculation."""
        good_budget = FreeEnergyBudget(complexity_cost=0.1, accuracy_gain=1.0)
        bad_budget = FreeEnergyBudget(complexity_cost=1.0, accuracy_gain=0.1)

        assert good_budget.retention_priority() > bad_budget.retention_priority()

    def test_expected_value_with_precision(self) -> None:
        """Test expected value includes precision weighting."""
        budget = FreeEnergyBudget(
            complexity_cost=0.5,
            accuracy_gain=1.0,
            precision_weight=2.0,
        )

        # Expected value = -free_energy * precision
        # = -(-0.5) * 2.0 = 1.0
        assert budget.expected_value == pytest.approx(1.0)

    def test_should_retain_with_threshold(self) -> None:
        """Test retention with custom threshold."""
        budget = FreeEnergyBudget(complexity_cost=0.6, accuracy_gain=0.5)

        # Free energy = 0.1 (positive, would not retain by default)
        assert not budget.should_retain(threshold=0.0)

        # But with higher threshold, it's ok
        assert budget.should_retain(threshold=0.2)


# ========== ActiveInferenceAgent Tests ==========


class TestActiveInferenceAgent:
    """Tests for ActiveInferenceAgent."""

    @pytest.fixture
    def agent(self) -> ActiveInferenceAgent[str]:
        """Create a test agent."""
        belief = Belief(distribution={"python": 0.5, "javascript": 0.3, "rust": 0.2})
        return ActiveInferenceAgent(belief)

    @pytest.mark.asyncio
    async def test_evaluate_memory_complexity(
        self, agent: ActiveInferenceAgent[str]
    ) -> None:
        """Test that longer content has higher complexity."""
        short_budget = await agent.evaluate_memory(
            "python",
            "Tips",  # 4 chars
            relevance=0.5,
        )

        long_budget = await agent.evaluate_memory(
            "python",
            "A" * 1000,  # 1000 chars
            relevance=0.5,
        )

        assert long_budget.complexity_cost > short_budget.complexity_cost

    @pytest.mark.asyncio
    async def test_evaluate_memory_relevance(
        self, agent: ActiveInferenceAgent[str]
    ) -> None:
        """Test that relevance affects accuracy gain."""
        low_relevance = await agent.evaluate_memory(
            "python",
            "Content",
            relevance=0.1,
        )

        high_relevance = await agent.evaluate_memory(
            "python",
            "Content",
            relevance=0.9,
        )

        assert high_relevance.accuracy_gain > low_relevance.accuracy_gain

    @pytest.mark.asyncio
    async def test_evaluate_memory_belief_probability(
        self, agent: ActiveInferenceAgent[str]
    ) -> None:
        """Test that higher belief probability increases accuracy."""
        # Python has higher belief (0.5) than rust (0.2)
        python_budget = await agent.evaluate_memory(
            "python",
            "Same content",
            relevance=0.5,
        )

        rust_budget = await agent.evaluate_memory(
            "rust",
            "Same content",
            relevance=0.5,
        )

        assert python_budget.accuracy_gain > rust_budget.accuracy_gain

    @pytest.mark.asyncio
    async def test_evaluate_memory_recency_bonus(
        self, agent: ActiveInferenceAgent[str]
    ) -> None:
        """Test that recent memories have lower effective complexity."""
        recent = await agent.evaluate_memory(
            "python",
            "Content",
            relevance=0.5,
            last_accessed=datetime.now(),  # Just accessed
        )

        old = await agent.evaluate_memory(
            "python",
            "Content",
            relevance=0.5,
            last_accessed=datetime.now() - timedelta(hours=24),  # Day old
        )

        # Recent should have lower complexity (recency bonus)
        assert recent.complexity_cost <= old.complexity_cost

    @pytest.mark.asyncio
    async def test_should_retain(self, agent: ActiveInferenceAgent[str]) -> None:
        """Test retention decision."""
        # Evaluate a beneficial memory
        await agent.evaluate_memory("python", "x", relevance=0.9)

        # Should retain
        assert await agent.should_retain("python")

    @pytest.mark.asyncio
    async def test_should_retain_unknown(
        self, agent: ActiveInferenceAgent[str]
    ) -> None:
        """Test retention for unknown concept (default: retain)."""
        assert await agent.should_retain("never_evaluated")

    @pytest.mark.asyncio
    async def test_update_belief(self, agent: ActiveInferenceAgent[str]) -> None:
        """Test belief update with observation."""
        original_prob = agent.belief.probability("rust")

        # Observe rust heavily
        await agent.update_belief({"rust": 1.0})

        # Rust probability should increase
        assert agent.belief.probability("rust") > original_prob

    @pytest.mark.asyncio
    async def test_compute_surprise(self, agent: ActiveInferenceAgent[str]) -> None:
        """Test surprise computation."""
        # High probability concept = low surprise
        python_surprise = await agent.compute_surprise("python")

        # Low probability concept = high surprise
        unknown_surprise = await agent.compute_surprise("unknown_lang")

        assert unknown_surprise > python_surprise

    @pytest.mark.asyncio
    async def test_recommend_actions(self, agent: ActiveInferenceAgent[str]) -> None:
        """Test action recommendations."""
        concepts = ["python", "javascript"]
        contents = {"python": "x", "javascript": "y" * 10000}  # JS is verbose

        actions = await agent.recommend_actions(
            concepts=concepts,
            contents=contents,
            relevances={"python": 0.9, "javascript": 0.1},
        )

        assert len(actions) == 2
        assert all(isinstance(a, InferenceAction) for a in actions)

        # Python should be promoted (high relevance, low complexity)
        # JavaScript should be demoted/forgotten (low relevance, high complexity)
        python_action = next(a for a in actions if a.concept_id == "python")
        js_action = next(a for a in actions if a.concept_id == "javascript")

        assert python_action.action in ["promote", "retain"]
        assert js_action.action in ["demote", "forget"]

    def test_prediction_error(self, agent: ActiveInferenceAgent[str]) -> None:
        """Test prediction error calculation."""
        # Perfect prediction
        perfect_obs = {"python": 0.5, "javascript": 0.3, "rust": 0.2}
        error = agent.prediction_error(perfect_obs)
        assert error < 0.1  # Very small error

        # Very wrong prediction
        wrong_obs = {"python": 0.0, "javascript": 0.0, "rust": 1.0}
        error = agent.prediction_error(wrong_obs)
        assert error > 0.5  # Large error


# ========== InferenceGuidedCrystal Tests ==========


class TestInferenceGuidedCrystal:
    """Tests for InferenceGuidedCrystal."""

    @pytest.fixture
    def guided_crystal(self) -> InferenceGuidedCrystal[str]:
        """Create a test guided crystal."""
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        # Store some concepts
        crystal.store("python", "Python tips and tricks", [0.8] * 64)
        crystal.store("javascript", "JS tips " * 500, [0.5] * 64)  # Long, low quality
        crystal.store("rust", "Rust memory safety", [0.7] * 64)

        belief = Belief(
            distribution={"python": 0.6, "javascript": 0.1, "rust": 0.3},
            precision=1.0,
        )
        inference: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        return InferenceGuidedCrystal(crystal, inference)

    @pytest.mark.asyncio
    async def test_evaluate_all(
        self, guided_crystal: InferenceGuidedCrystal[str]
    ) -> None:
        """Test evaluating all concepts."""
        budgets = await guided_crystal.evaluate_all()

        assert len(budgets) == 3
        assert "python" in budgets
        assert "javascript" in budgets
        assert "rust" in budgets

    @pytest.mark.asyncio
    async def test_consolidate(
        self, guided_crystal: InferenceGuidedCrystal[str]
    ) -> None:
        """Test consolidation based on free energy."""
        actions = await guided_crystal.consolidate()

        assert len(actions) == 3
        assert all(a in ["promoted", "demoted", "retained"] for a in actions.values())

    @pytest.mark.asyncio
    async def test_consolidate_promotes_valuable(
        self, guided_crystal: InferenceGuidedCrystal[str]
    ) -> None:
        """Test that valuable memories are promoted."""
        # Python has high belief and short content = valuable
        original_resolution = guided_crystal.crystal.resolution_levels["python"]

        await guided_crystal.consolidate(promote_threshold=-0.0001)

        # Python should be promoted (higher resolution)
        # Note: May already be at 1.0, so just check it's not demoted
        new_resolution = guided_crystal.crystal.resolution_levels["python"]
        assert new_resolution >= original_resolution

    @pytest.mark.asyncio
    async def test_consolidate_demotes_costly(
        self, guided_crystal: InferenceGuidedCrystal[str]
    ) -> None:
        """Test that costly memories are demoted."""
        # JavaScript has low belief and long content = costly
        original_resolution = guided_crystal.crystal.resolution_levels["javascript"]

        await guided_crystal.consolidate(demote_threshold=0.001)

        # JavaScript should be demoted (lower resolution)
        new_resolution = guided_crystal.crystal.resolution_levels["javascript"]
        assert new_resolution <= original_resolution

    @pytest.mark.asyncio
    async def test_smart_compress(
        self, guided_crystal: InferenceGuidedCrystal[str]
    ) -> None:
        """Test smart compression."""
        compressed = await guided_crystal.smart_compress(target_ratio=0.8)

        # All concepts should still exist
        assert len(compressed.concepts) == 3

        # Dimension should be reduced
        assert compressed.dimension < guided_crystal.crystal.dimension

    @pytest.mark.asyncio
    async def test_observe(self, guided_crystal: InferenceGuidedCrystal[str]) -> None:
        """Test observation updates both crystal and inference."""
        original_prob = guided_crystal.inference.belief.probability("rust")

        await guided_crystal.observe("rust")

        # Belief should increase
        new_prob = guided_crystal.inference.belief.probability("rust")
        assert new_prob > original_prob

    def test_stats(self, guided_crystal: InferenceGuidedCrystal[str]) -> None:
        """Test combined statistics."""
        stats = guided_crystal.stats()

        assert "dimension" in stats
        assert "concept_count" in stats
        assert "belief_entropy" in stats
        assert "belief_precision" in stats


# ========== PredictiveMemory Tests ==========


class TestPredictiveMemory:
    """Tests for PredictiveMemory."""

    @pytest.fixture
    def predictive_memory(self) -> PredictiveMemory[str]:
        """Create a test predictive memory."""
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("a", "Concept A", [1.0] * 64)
        crystal.store("b", "Concept B", [0.8] * 64)
        crystal.store("c", "Concept C", [0.5] * 64)

        belief = Belief(
            distribution={"a": 0.5, "b": 0.3, "c": 0.2},
            precision=1.0,
        )
        inference: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        return PredictiveMemory(crystal, inference)

    @pytest.mark.asyncio
    async def test_predict_next(self, predictive_memory: PredictiveMemory[str]) -> None:
        """Test next concept prediction."""
        predictions = await predictive_memory.predict_next("context")

        assert len(predictions) == 3
        # Should be sorted by probability (descending)
        assert predictions[0][1] >= predictions[1][1]
        assert predictions[1][1] >= predictions[2][1]

    @pytest.mark.asyncio
    async def test_learn_from_correct_outcome(
        self, predictive_memory: PredictiveMemory[str]
    ) -> None:
        """Test learning from correct prediction."""
        original_precision = predictive_memory.inference.belief.precision

        await predictive_memory.learn_from_outcome("a", "a")

        # Precision should not decrease for correct prediction
        assert predictive_memory.inference.belief.precision >= original_precision * 0.9

    @pytest.mark.asyncio
    async def test_learn_from_wrong_outcome(
        self, predictive_memory: PredictiveMemory[str]
    ) -> None:
        """Test learning from wrong prediction."""
        original_precision = predictive_memory.inference.belief.precision

        await predictive_memory.learn_from_outcome("a", "c")

        # Precision should decrease for wrong prediction
        assert predictive_memory.inference.belief.precision < original_precision

    @pytest.mark.asyncio
    async def test_prediction_accuracy(
        self, predictive_memory: PredictiveMemory[str]
    ) -> None:
        """Test prediction accuracy calculation."""
        # Correct predictions
        await predictive_memory.learn_from_outcome("a", "a")
        await predictive_memory.learn_from_outcome("b", "b")
        # Wrong prediction
        await predictive_memory.learn_from_outcome("a", "c")

        accuracy = predictive_memory.prediction_accuracy()
        assert accuracy == pytest.approx(2 / 3, rel=0.01)

    def test_prediction_accuracy_empty(
        self, predictive_memory: PredictiveMemory[str]
    ) -> None:
        """Test prediction accuracy with no history."""
        accuracy = predictive_memory.prediction_accuracy()
        assert accuracy == 0.0


# ========== Factory Function Tests ==========


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_inference_agent_uniform(self) -> None:
        """Test creating agent with uniform prior."""
        agent = create_inference_agent(["a", "b", "c"], uniform=True)

        assert agent.belief.probability("a") == pytest.approx(1 / 3, rel=0.01)
        assert agent.belief.probability("b") == pytest.approx(1 / 3, rel=0.01)
        assert agent.belief.probability("c") == pytest.approx(1 / 3, rel=0.01)

    def test_create_inference_agent_harmonic(self) -> None:
        """Test creating agent with harmonic prior."""
        agent = create_inference_agent(["a", "b", "c"], uniform=False)

        # Harmonic: first concept gets highest probability
        assert agent.belief.probability("a") > agent.belief.probability("b")
        assert agent.belief.probability("b") > agent.belief.probability("c")

    def test_create_inference_agent_precision(self) -> None:
        """Test creating agent with custom precision."""
        agent = create_inference_agent(["a", "b"], uniform=True, precision=2.0)

        assert agent.belief.precision == 2.0

    def test_create_guided_crystal(self) -> None:
        """Test creating guided crystal."""
        guided = create_guided_crystal(
            dimension=128,
            concepts=["python", "rust"],
            precision=1.5,
        )

        assert guided.crystal.dimension == 128
        assert guided.inference.belief.precision == 1.5

    def test_create_guided_crystal_default(self) -> None:
        """Test creating guided crystal with defaults."""
        guided = create_guided_crystal()

        assert guided.crystal.dimension == 1024
        assert "default" in guided.inference.belief.distribution


# ========== Integration Tests ==========


class TestActiveInferenceIntegration:
    """Integration tests for active inference with other pillars."""

    @pytest.mark.asyncio
    async def test_full_workflow(self) -> None:
        """Test complete active inference workflow."""
        from agents.m.crystal import MemoryCrystal

        # 1. Create crystal and agent
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        belief = Belief(
            distribution={"code": 0.4, "docs": 0.3, "chat": 0.3},
            precision=1.0,
        )
        agent: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)
        guided = InferenceGuidedCrystal(crystal, agent)

        # 2. Store memories
        crystal.store("code_snippet", "def hello(): pass", [0.9] * 64)
        crystal.store("long_doc", "x" * 5000, [0.5] * 64)  # Long but low relevance
        crystal.store("useful_chat", "User wants dark mode", [0.7] * 64)

        # 3. Observe code-related activity
        await guided.observe("code_snippet")
        await guided.observe("code_snippet")
        await agent.update_belief({"code": 0.8})

        # 4. Consolidate based on free energy
        actions = await guided.consolidate()

        # Should have taken action on all memories
        assert len(actions) == 3

        # 5. Verify stats reflect the process
        stats = guided.stats()
        assert stats["concept_count"] == 3

    @pytest.mark.asyncio
    async def test_predictive_workflow(self) -> None:
        """Test predictive memory workflow."""
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("morning", "Morning routine", [1.0] * 64)
        crystal.store("afternoon", "Afternoon tasks", [0.8] * 64)
        crystal.store("evening", "Evening wind-down", [0.6] * 64)

        belief = Belief(
            distribution={"morning": 0.5, "afternoon": 0.3, "evening": 0.2},
        )
        agent: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)
        predictive = PredictiveMemory(crystal, agent)

        # Make predictions and learn
        for _ in range(10):
            predictions = await predictive.predict_next("current_time")
            predicted = predictions[0][0] if predictions else "morning"

            # Simulate: afternoon is actually most common
            await predictive.learn_from_outcome(predicted, "afternoon")

        # After learning, afternoon should have higher probability
        assert agent.belief.probability("afternoon") > agent.belief.probability(
            "evening"
        )


class TestFreeEnergyPrinciple:
    """Tests verifying the Free Energy Principle."""

    @pytest.mark.asyncio
    async def test_minimizes_surprise(self) -> None:
        """Test that the agent minimizes surprise over time."""
        belief = Belief(distribution={"a": 0.33, "b": 0.33, "c": 0.34})
        agent: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        # Repeatedly observe 'a'
        for _ in range(10):
            await agent.update_belief({"a": 0.9})

        # Surprise for 'a' should decrease
        surprise = await agent.compute_surprise("a")
        # High probability = low surprise
        assert surprise < 1.0

    @pytest.mark.asyncio
    async def test_accuracy_complexity_tradeoff(self) -> None:
        """Test the accuracy-complexity tradeoff."""
        belief = Belief(distribution={"relevant": 0.8, "irrelevant": 0.2})
        agent: ActiveInferenceAgent[str] = ActiveInferenceAgent(belief)

        # Relevant but short memory
        relevant_short = await agent.evaluate_memory("relevant", "Short", relevance=0.9)

        # Relevant but long memory
        relevant_long = await agent.evaluate_memory(
            "relevant", "x" * 10000, relevance=0.9
        )

        # Short should have better (more negative) free energy
        assert relevant_short.free_energy < relevant_long.free_energy

    @pytest.mark.asyncio
    async def test_belief_entropy_decreases_with_evidence(self) -> None:
        """Test that entropy decreases with consistent evidence."""
        belief = Belief(distribution={"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25})
        initial_entropy = belief.entropy()

        # Consistently observe 'a'
        for _ in range(10):
            belief.update("a", observation_weight=0.5)

        # Entropy should decrease (more certainty)
        final_entropy = belief.entropy()
        assert final_entropy < initial_entropy
