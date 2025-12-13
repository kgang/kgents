"""
Active Inference for Memory Management.

The third pillar: Free Energy Minimization.

Memory serves self-evidencing. Agents keep memories that reduce surprise,
compress those that add complexity without accuracy gains, and forget
those that conflict with their world model.

Key Concepts:
- Belief: Agent's probability distribution over concepts
- Free Energy: F = Complexity - Accuracy (minimize this)
- Precision: Inverse variance (confidence in beliefs)
- Self-evidencing: Memory that supports the agent's model of itself

The active inference framework treats memory retention as an optimization
problem: which memories minimize the free energy of the agent's internal
model?

Mathematical Foundation:
  F = KL[Q(s) || P(s|o)] - log P(o)

Where:
  - Q(s): Agent's beliefs about states
  - P(s|o): True posterior given observations
  - P(o): Evidence (model evidence / marginal likelihood)

Minimizing F means:
1. Q approaches the true posterior (accuracy)
2. Avoiding overly complex models (parsimony)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from .crystal import CrystalPattern, MemoryCrystal

T = TypeVar("T")


@dataclass
class Belief:
    """
    Agent's belief distribution over concepts.

    The belief captures what the agent "expects" about the world.
    High precision = confident beliefs (low variance).
    Low precision = uncertain beliefs (high variance).
    """

    distribution: dict[str, float]  # Concept → probability
    precision: float = 1.0  # Inverse variance (confidence)
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        # Normalize if not already
        self._normalize()

    def _normalize(self) -> None:
        """Ensure distribution sums to 1."""
        total = sum(self.distribution.values())
        if total > 0:
            for k in self.distribution:
                self.distribution[k] /= total

    def probability(self, concept: str) -> float:
        """Get probability of a concept (with default)."""
        return self.distribution.get(concept, 0.01)  # Small prior

    def entropy(self) -> float:
        """Shannon entropy of the belief distribution.

        H = -Σ p(x) log p(x)

        High entropy = uncertain, spread beliefs.
        Low entropy = certain, peaked beliefs.
        """
        h = 0.0
        for p in self.distribution.values():
            if p > 0:
                h -= p * math.log(p + 1e-10)
        return h

    def kl_divergence(self, other: "Belief") -> float:
        """KL divergence from self to other.

        KL(self || other) = Σ self(x) log(self(x) / other(x))

        Measures how different the two beliefs are.
        """
        kl = 0.0
        for concept, p in self.distribution.items():
            q = other.probability(concept)
            if p > 0 and q > 0:
                kl += p * math.log(p / q)
        return kl

    def update(self, concept: str, observation_weight: float = 0.5) -> None:
        """Bayesian-inspired update toward observed concept.

        Args:
            concept: The observed concept
            observation_weight: How much to weight the observation (0 to 1)
        """
        # Increase probability of observed concept
        current = self.probability(concept)

        # Blend prior with observation
        self.distribution[concept] = (
            1 - observation_weight
        ) * current + observation_weight

        # Re-normalize
        self._normalize()
        self.last_updated = datetime.now()

    def copy(self) -> "Belief":
        """Create a copy of this belief."""
        return Belief(
            distribution=self.distribution.copy(),
            precision=self.precision,
            last_updated=self.last_updated,
        )


@dataclass
class FreeEnergyBudget:
    """
    Free energy accounting for memory operations.

    Free Energy F = Complexity - Accuracy

    We want to MINIMIZE free energy:
    - Negative free energy = beneficial memory (accuracy > complexity)
    - Positive free energy = costly memory (complexity > accuracy)
    """

    complexity_cost: float  # Cost of maintaining this memory
    accuracy_gain: float  # Benefit for predictions
    precision_weight: float = 1.0  # How precise/confident

    @property
    def free_energy(self) -> float:
        """
        F = Complexity - Accuracy

        Negative = good (keep), Positive = bad (consider forgetting).
        """
        return self.complexity_cost - self.accuracy_gain

    @property
    def expected_value(self) -> float:
        """Value considering precision (confidence-weighted)."""
        return -self.free_energy * self.precision_weight

    def should_retain(self, threshold: float = 0.0) -> bool:
        """Should this memory be retained?

        Args:
            threshold: Free energy threshold (default 0 = break-even)

        Returns:
            True if memory provides net benefit
        """
        return self.free_energy < threshold

    def retention_priority(self) -> float:
        """Priority score for retention (higher = keep more).

        Returns a score where:
        - High positive = definitely keep
        - Near zero = borderline
        - High negative = definitely forget
        """
        return self.accuracy_gain - self.complexity_cost


@dataclass
class InferenceAction:
    """An action recommended by active inference."""

    concept_id: str
    action: str  # "retain", "demote", "promote", "forget"
    free_energy: float
    reason: str


class ActiveInferenceAgent(Generic[T]):
    """
    Memory management via Free Energy minimization.

    This agent evaluates memories based on their contribution to
    the agent's ability to predict and model the world. Memories
    that reduce prediction error are retained; those that add
    complexity without benefit are gracefully forgotten.

    Key Operations:
    - RETAIN: Keep memories that reduce prediction error
    - PROMOTE: Strengthen memories with high accuracy/complexity ratio
    - DEMOTE: Weaken memories with high complexity/accuracy ratio
    - FORGET: Release memories that conflict with world model

    The agent maintains beliefs and updates them based on observations,
    preferring memories that minimize surprise.

    Example:
        belief = Belief(distribution={"python": 0.5, "javascript": 0.3, "rust": 0.2})
        agent = ActiveInferenceAgent(belief)

        # Evaluate a memory
        budget = await agent.evaluate_memory("python_tips", "Tips for Python...", 0.8)
        if budget.should_retain():
            print("Keep this memory!")

        # Update beliefs based on observation
        await agent.update_belief({"python": 0.9})  # Observed Python heavily
    """

    def __init__(
        self,
        prior: Belief,
        complexity_weight: float = 0.001,  # Cost per character
        recency_weight: float = 0.1,  # Weight for recent memories
    ) -> None:
        """Initialize active inference agent.

        Args:
            prior: Initial belief distribution
            complexity_weight: How much complexity costs per unit
            recency_weight: Bonus for recently accessed memories
        """
        self.belief = prior
        self.complexity_weight = complexity_weight
        self.recency_weight = recency_weight
        self._memory_budgets: dict[str, FreeEnergyBudget] = {}
        self._observation_history: list[tuple[datetime, str]] = []

    @property
    def concepts(self) -> set[str]:
        """Concepts in current belief."""
        return set(self.belief.distribution.keys())

    def get_budget(self, concept_id: str) -> FreeEnergyBudget | None:
        """Get cached budget for a concept."""
        return self._memory_budgets.get(concept_id)

    async def evaluate_memory(
        self,
        concept_id: str,
        content: str,
        relevance: float = 0.5,
        last_accessed: datetime | None = None,
    ) -> FreeEnergyBudget:
        """
        Compute free energy budget for a memory.

        Args:
            concept_id: The concept identifier
            content: The memory content (for complexity)
            relevance: Semantic relevance to current beliefs (0 to 1)
            last_accessed: When memory was last accessed

        Returns:
            FreeEnergyBudget with complexity and accuracy
        """
        # Complexity: function of content size
        # More content = more complexity to maintain
        complexity = len(content) * self.complexity_weight

        # Accuracy: function of relevance and belief probability
        # How much does this memory help predict/model the world?
        prior_prob = self.belief.probability(concept_id)
        accuracy = relevance * prior_prob * self.belief.precision

        # Recency bonus (reduces effective complexity)
        recency_bonus = 0.0
        if last_accessed:
            age = datetime.now() - last_accessed
            # Exponential decay of recency bonus
            hours = age.total_seconds() / 3600
            recency_bonus = self.recency_weight * math.exp(-0.1 * hours)

        # Adjust complexity for recency
        adjusted_complexity = max(0.0, complexity - recency_bonus)

        budget = FreeEnergyBudget(
            complexity_cost=adjusted_complexity,
            accuracy_gain=accuracy,
            precision_weight=self.belief.precision,
        )

        # Cache it
        self._memory_budgets[concept_id] = budget

        return budget

    async def should_retain(self, concept_id: str) -> bool:
        """Should this memory be retained?

        Args:
            concept_id: The concept to check

        Returns:
            True if memory should be retained
        """
        budget = self._memory_budgets.get(concept_id)
        if not budget:
            return True  # Default: retain unknown
        return budget.should_retain(threshold=0.0)

    async def update_belief(self, observation: dict[str, float]) -> None:
        """
        Update beliefs based on observation.

        This is a simplified Bayesian update that moves the
        belief distribution toward observed concepts.

        Args:
            observation: Dict mapping concept to observed intensity
        """
        now = datetime.now()

        for concept, intensity in observation.items():
            # Record observation
            self._observation_history.append((now, concept))

            # Update belief toward observation
            self.belief.update(concept, observation_weight=intensity * 0.3)

    async def compute_surprise(self, concept: str) -> float:
        """
        Compute surprise for observing a concept.

        Surprise = -log P(concept)

        High surprise = unexpected observation.
        Low surprise = expected observation.

        Args:
            concept: The observed concept

        Returns:
            Surprise value (non-negative)
        """
        prob = self.belief.probability(concept)
        return -math.log(prob + 1e-10)

    async def recommend_actions(
        self,
        concepts: list[str],
        contents: dict[str, str],
        relevances: dict[str, float] | None = None,
    ) -> list[InferenceAction]:
        """
        Recommend memory management actions for multiple concepts.

        Args:
            concepts: Concepts to evaluate
            contents: Map from concept_id to content string
            relevances: Optional relevance scores (default 0.5)

        Returns:
            List of InferenceAction recommendations
        """
        relevances = relevances or {}
        actions: list[InferenceAction] = []

        for concept_id in concepts:
            content = contents.get(concept_id, "")
            relevance = relevances.get(concept_id, 0.5)

            budget = await self.evaluate_memory(
                concept_id=concept_id,
                content=content,
                relevance=relevance,
            )

            # Determine action based on free energy
            fe = budget.free_energy

            if fe < -0.5:
                # Very beneficial - promote
                action = InferenceAction(
                    concept_id=concept_id,
                    action="promote",
                    free_energy=fe,
                    reason=f"High value: accuracy {budget.accuracy_gain:.2f} >> complexity {budget.complexity_cost:.2f}",
                )
            elif fe < 0:
                # Beneficial - retain
                action = InferenceAction(
                    concept_id=concept_id,
                    action="retain",
                    free_energy=fe,
                    reason=f"Net positive: accuracy {budget.accuracy_gain:.2f} > complexity {budget.complexity_cost:.2f}",
                )
            elif fe < 0.5:
                # Borderline - demote but keep
                action = InferenceAction(
                    concept_id=concept_id,
                    action="demote",
                    free_energy=fe,
                    reason=f"Borderline: complexity {budget.complexity_cost:.2f} slightly > accuracy {budget.accuracy_gain:.2f}",
                )
            else:
                # Costly - recommend forgetting
                action = InferenceAction(
                    concept_id=concept_id,
                    action="forget",
                    free_energy=fe,
                    reason=f"High cost: complexity {budget.complexity_cost:.2f} >> accuracy {budget.accuracy_gain:.2f}",
                )

            actions.append(action)

        # Sort by priority (highest free energy = forget first)
        actions.sort(key=lambda a: a.free_energy, reverse=True)

        return actions

    def prediction_error(self, observations: dict[str, float]) -> float:
        """
        Compute prediction error between beliefs and observations.

        This is the sum of squared differences between expected
        and observed probabilities.

        Args:
            observations: Observed distribution

        Returns:
            Prediction error (lower is better)
        """
        error = 0.0
        all_concepts = set(self.belief.distribution.keys()) | set(observations.keys())

        for concept in all_concepts:
            expected = self.belief.probability(concept)
            observed = observations.get(concept, 0.0)
            error += (expected - observed) ** 2

        return math.sqrt(error)


class InferenceGuidedCrystal(Generic[T]):
    """
    Crystal wrapper that uses Active Inference for retention decisions.

    Combines the holographic MemoryCrystal with Active Inference
    to intelligently manage which memories to promote/demote.

    Example:
        crystal = MemoryCrystal(dimension=64)
        belief = Belief(distribution={"code": 0.5, "docs": 0.3, "chat": 0.2})
        inference = ActiveInferenceAgent(belief)

        guided = InferenceGuidedCrystal(crystal, inference)

        # Consolidate based on free energy, not just recency
        actions = await guided.consolidate()
        # {'concept_a': 'promoted', 'concept_b': 'demoted', ...}
    """

    def __init__(
        self,
        crystal: "MemoryCrystal[T]",
        inference: ActiveInferenceAgent[T],
    ) -> None:
        """Initialize inference-guided crystal.

        Args:
            crystal: The memory crystal to manage
            inference: The active inference agent
        """
        self.crystal = crystal
        self.inference = inference

    async def evaluate_all(self) -> dict[str, FreeEnergyBudget]:
        """Evaluate all concepts in the crystal.

        Returns:
            Map from concept_id to FreeEnergyBudget
        """
        budgets: dict[str, FreeEnergyBudget] = {}

        for concept_id in self.crystal.concepts:
            pattern = self.crystal.get_pattern(concept_id)
            if pattern is None:
                continue

            content = str(pattern.content) if pattern.content else ""
            relevance = pattern.resolution  # Use resolution as relevance proxy

            budget = await self.inference.evaluate_memory(
                concept_id=concept_id,
                content=content,
                relevance=relevance,
                last_accessed=pattern.last_accessed,
            )
            budgets[concept_id] = budget

        return budgets

    async def consolidate(
        self,
        promote_threshold: float = -0.5,
        demote_threshold: float = 0.5,
    ) -> dict[str, str]:
        """
        Consolidate crystal based on free energy.

        Unlike traditional consolidation (recency/frequency), this
        uses active inference to decide what to keep.

        Args:
            promote_threshold: Free energy below this → promote
            demote_threshold: Free energy above this → demote

        Returns:
            Dict mapping concept_id to action taken
        """
        actions: dict[str, str] = {}
        budgets = await self.evaluate_all()

        for concept_id, budget in budgets.items():
            fe = budget.free_energy

            if fe < promote_threshold:
                # High value - promote
                self.crystal.promote(concept_id, factor=1.2)
                actions[concept_id] = "promoted"

            elif fe > demote_threshold:
                # Low value - demote
                self.crystal.demote(concept_id, factor=0.5)
                actions[concept_id] = "demoted"

            else:
                # Neutral - retain as is
                actions[concept_id] = "retained"

        return actions

    async def smart_compress(self, target_ratio: float = 0.8) -> "MemoryCrystal[T]":
        """
        Compress crystal intelligently using free energy.

        Instead of uniform compression, this prioritizes retaining
        high-value memories at full resolution while compressing
        low-value memories more aggressively.

        Args:
            target_ratio: Target compression ratio

        Returns:
            New crystal with variable compression
        """
        # First, consolidate to adjust resolutions based on value
        await self.consolidate()

        # Then apply uniform compression
        return self.crystal.compress(target_ratio)

    async def observe(self, concept_id: str) -> None:
        """
        Record an observation of a concept.

        Updates both the crystal and inference agent.

        Args:
            concept_id: The observed concept
        """
        # Update inference beliefs
        await self.inference.update_belief({concept_id: 0.8})

        # Access the crystal (updates recency)
        self.crystal.retrieve_content(concept_id)

    def stats(self) -> dict[str, Any]:
        """Get combined statistics."""
        crystal_stats = self.crystal.stats()

        budgets_raw = {
            cid: self.inference.get_budget(cid) for cid in self.crystal.concepts
        }
        budgets: dict[str, FreeEnergyBudget] = {
            k: v for k, v in budgets_raw.items() if v is not None
        }

        if budgets:
            avg_fe = sum(b.free_energy for b in budgets.values()) / len(budgets)
            positive_fe = len([b for b in budgets.values() if b.free_energy > 0])
            negative_fe = len([b for b in budgets.values() if b.free_energy < 0])
        else:
            avg_fe = 0.0
            positive_fe = 0
            negative_fe = 0

        return {
            **crystal_stats,
            "belief_entropy": self.inference.belief.entropy(),
            "belief_precision": self.inference.belief.precision,
            "avg_free_energy": avg_fe,
            "costly_memories": positive_fe,  # Consider forgetting
            "valuable_memories": negative_fe,  # Keep these
        }


# ========== Predictive Memory ==========


class PredictiveMemory(Generic[T]):
    """
    Memory that supports predictive processing.

    Active inference agents predict what they'll encounter next.
    This class provides utilities for memory-based prediction.
    """

    def __init__(
        self,
        crystal: "MemoryCrystal[T]",
        inference: ActiveInferenceAgent[T],
    ) -> None:
        """Initialize predictive memory.

        Args:
            crystal: The memory substrate
            inference: The inference agent
        """
        self.crystal = crystal
        self.inference = inference
        self._prediction_history: list[
            tuple[str, str, bool]
        ] = []  # (predicted, actual, correct)

    async def predict_next(self, context: str) -> list[tuple[str, float]]:
        """
        Predict likely next concepts given context.

        Args:
            context: Current context/cue

        Returns:
            List of (concept_id, probability) sorted by likelihood
        """
        predictions: list[tuple[str, float]] = []

        for concept_id in self.crystal.concepts:
            # Combine belief probability with crystal resolution
            belief_prob = self.inference.belief.probability(concept_id)

            pattern = self.crystal.get_pattern(concept_id)
            resolution = pattern.resolution if pattern else 0.5

            # Joint probability
            joint_prob = belief_prob * resolution

            predictions.append((concept_id, joint_prob))

        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)

        return predictions

    async def learn_from_outcome(
        self,
        predicted: str,
        actual: str,
    ) -> None:
        """
        Learn from prediction outcome.

        Updates beliefs based on whether prediction was correct.

        Args:
            predicted: What we predicted
            actual: What actually happened
        """
        correct = predicted == actual
        self._prediction_history.append((predicted, actual, correct))

        # Update inference based on actual
        await self.inference.update_belief({actual: 0.7})

        if not correct:
            # Reduce confidence in wrong predictions
            self.inference.belief.precision *= 0.95

    def prediction_accuracy(self, window: int = 100) -> float:
        """
        Compute recent prediction accuracy.

        Args:
            window: Number of recent predictions to consider

        Returns:
            Accuracy as fraction (0 to 1)
        """
        recent = self._prediction_history[-window:]
        if not recent:
            return 0.0

        correct = sum(1 for _, _, c in recent if c)
        return correct / len(recent)


# ========== Utility Functions ==========


def create_inference_agent(
    concepts: list[str],
    uniform: bool = True,
    precision: float = 1.0,
) -> ActiveInferenceAgent[Any]:
    """
    Factory function to create an inference agent.

    Args:
        concepts: Initial concept vocabulary
        uniform: If True, use uniform prior
        precision: Initial precision (confidence)

    Returns:
        Configured ActiveInferenceAgent
    """
    if uniform:
        n = len(concepts)
        distribution = {c: 1.0 / n for c in concepts}
    else:
        # Use harmonic prior (favor earlier concepts)
        weights = [1.0 / (i + 1) for i in range(len(concepts))]
        total = sum(weights)
        distribution = {c: w / total for c, w in zip(concepts, weights)}

    belief = Belief(distribution=distribution, precision=precision)
    return ActiveInferenceAgent(belief)


def create_guided_crystal(
    dimension: int = 1024,
    concepts: list[str] | None = None,
    precision: float = 1.0,
) -> InferenceGuidedCrystal[Any]:
    """
    Factory function to create an inference-guided crystal.

    Args:
        dimension: Crystal dimension
        concepts: Initial concept vocabulary
        precision: Initial belief precision

    Returns:
        Configured InferenceGuidedCrystal
    """
    from .crystal import MemoryCrystal

    crystal: MemoryCrystal[Any] = MemoryCrystal(dimension=dimension)

    if concepts:
        inference = create_inference_agent(concepts, precision=precision)
    else:
        inference = create_inference_agent(["default"], precision=precision)

    return InferenceGuidedCrystal(crystal, inference)
