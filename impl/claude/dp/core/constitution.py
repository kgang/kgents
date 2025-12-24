"""
The 7 Constitutional Principles as reward function.

The Constitution maps the 7 kgents principles to a reward function for DP agents.

R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')

Where:
- R(s, a, s') is the total reward for taking action a from state s to s'
- wᵢ is the weight for principle i
- Rᵢ(s, a, s') is the reward for principle i

Default weights (from Principle.weight in dp_bridge):
1. Tasteful - Aesthetic coherence (1.0)
2. Curated - Intentional selection (1.0)
3. Ethical - Human augmentation (2.0) [highest priority]
4. Joy-Inducing - Delight (1.2)
5. Composable - Morphism respect (1.5)
6. Heterarchical - Flux over hierarchy (1.0)
7. Generative - Compression (1.0)

Custom evaluators can be injected to provide domain-specific principle scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from services.categorical.dp_bridge import Principle, PrincipleScore, ValueScore

# Type variables for state and action types
S = TypeVar("S")
A = TypeVar("A")


@dataclass
class Constitution:
    """
    The 7 principles as the global reward function.

    This class provides both:
    1. A scalar reward function: R(s, a, s') -> float
    2. A detailed evaluation: evaluate(s, a, s') -> ValueScore

    The reward is the weighted sum of per-principle scores.
    Custom evaluators can be injected for domain-specific scoring.

    Example:
        >>> constitution = Constitution()
        >>> # Add custom evaluator for COMPOSABLE principle
        >>> constitution.evaluators[Principle.COMPOSABLE] = lambda s, a, ns: 1.0 if is_compositional(a) else 0.0
        >>> reward = constitution.reward(state, action, next_state)
        >>> value_score = constitution.evaluate(state, action, next_state)
    """

    # Principle weights (default from Principle.weight)
    principle_weights: dict[Principle, float] = field(default_factory=lambda: {
        Principle.ETHICAL: 2.0,      # Safety first
        Principle.COMPOSABLE: 1.5,   # Architectural importance
        Principle.JOY_INDUCING: 1.2, # Kent's aesthetic priority
        Principle.TASTEFUL: 1.0,
        Principle.CURATED: 1.0,
        Principle.HETERARCHICAL: 1.0,
        Principle.GENERATIVE: 1.0,
    })

    # Custom evaluators: (state, action, next_state) -> score in [0, 1]
    # If not provided, defaults to neutral 0.5 score
    evaluators: dict[Principle, Callable[[Any, Any, Any], float]] = field(default_factory=dict)

    # Evidence generators: (state, action, next_state) -> explanation string
    evidence_generators: dict[Principle, Callable[[Any, Any, Any], str]] = field(default_factory=dict)

    def _get_weight(self, principle: Principle) -> float:
        """Get the weight for a principle (with fallback to Principle.weight)."""
        return self.principle_weights.get(principle, principle.weight)

    def _evaluate_principle(
        self,
        principle: Principle,
        state: Any,
        action: Any,
        next_state: Any,
    ) -> tuple[float, str]:
        """
        Evaluate a single principle.

        Returns:
            Tuple of (score, evidence)
        """
        evaluator = self.evaluators.get(principle)
        evidence_gen = self.evidence_generators.get(principle)

        if evaluator is not None:
            # Use custom evaluator
            raw_score = evaluator(state, action, next_state)
            # Clamp to [0, 1]
            score = max(0.0, min(1.0, raw_score))
        else:
            # Default: neutral score if no evaluator
            score = 0.5

        # Generate evidence
        if evidence_gen is not None:
            evidence = evidence_gen(state, action, next_state)
        else:
            evidence = "No custom evaluator configured"

        return score, evidence

    def evaluate(self, state: S, action: A, next_state: S) -> ValueScore:
        """
        Full evaluation with per-principle breakdown.

        Returns a ValueScore with detailed scores for each principle.
        This is useful for understanding WHY a particular action has
        the reward it does.

        Args:
            state: The state before the action
            action: The action taken
            next_state: The state after the action

        Returns:
            ValueScore with all principle scores and evidence
        """
        principle_scores: list[PrincipleScore] = []

        for principle in Principle:
            score, evidence = self._evaluate_principle(
                principle, state, action, next_state
            )
            weight = self._get_weight(principle)

            principle_scores.append(
                PrincipleScore(
                    principle=principle,
                    score=score,
                    evidence=evidence,
                    weight=weight,
                )
            )

        return ValueScore(
            agent_name=f"transition({state}, {action}, {next_state})",
            principle_scores=tuple(principle_scores),
        )

    def reward(self, state: S, action: A, next_state: S) -> float:
        """
        R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')

        Compute the scalar reward as a weighted sum of principle scores.
        This is the reward function used in DP algorithms (Bellman equation).

        Args:
            state: The state before the action
            action: The action taken
            next_state: The state after the action

        Returns:
            Weighted sum of principle scores (range: [0, 1])
        """
        value_score = self.evaluate(state, action, next_state)
        return value_score.total_score

    def set_evaluator(
        self,
        principle: Principle,
        evaluator: Callable[[Any, Any, Any], float],
        evidence_generator: Callable[[Any, Any, Any], str] | None = None,
    ) -> None:
        """
        Set a custom evaluator for a principle.

        This allows domain-specific reward functions while maintaining
        the overall constitutional structure.

        Args:
            principle: The principle to evaluate
            evaluator: Function (state, action, next_state) -> score in [0, 1]
            evidence_generator: Optional function to generate human-readable evidence
        """
        self.evaluators[principle] = evaluator
        if evidence_generator is not None:
            self.evidence_generators[principle] = evidence_generator

    def set_weight(self, principle: Principle, weight: float) -> None:
        """
        Set the weight for a principle.

        Higher weights make the principle more important in the total reward.

        Args:
            principle: The principle to weight
            weight: The weight (typically 0.0 to 2.0)
        """
        self.principle_weights[principle] = weight


__all__ = ["Constitution"]
