"""
Constitution as Reward Function

The 7 principles provide the reward signal for all agent actions.
This formalizes the kgents Constitution as a mathematical value function:

    R(s, a, s') = Σᵢ wᵢ · Rᵢ(s, a, s')

Where:
- Rᵢ is the reward for principle i
- wᵢ is the weight for principle i
- s, s' are states before/after action
- a is the action taken

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every action in the kgents system is evaluated against the 7 constitutional
    principles. This isn't just documentation—it's the actual reward function
    that drives agent behavior and learning.

The Principles with Weights:
    - ETHICAL: 2.0 (safety first)
    - COMPOSABLE: 1.5 (architecture second)
    - JOY_INDUCING: 1.2 (Kent's aesthetic)
    - TASTEFUL: 1.0
    - CURATED: 1.0
    - HETERARCHICAL: 1.0
    - GENERATIVE: 1.0

Integration:
    - TruthFunctor probes use constitutional rewards
    - DP-Bridge ValueFunction uses principle scores
    - Witness marks record constitutional justifications

See: spec/theory/dp-native-kgents.md
See: CLAUDE.md → Project Philosophy
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, Protocol

from .dp_bridge import Principle, PrincipleScore as DPPrincipleScore

logger = logging.getLogger("kgents.categorical.constitution")

# Re-export Principle from dp_bridge for consistency
__all_principles__ = Principle

# =============================================================================
# Constitutional Principle Weights
# =============================================================================

PRINCIPLE_WEIGHTS = {
    Principle.ETHICAL: 2.0,       # Safety first
    Principle.COMPOSABLE: 1.5,    # Architecture second
    Principle.JOY_INDUCING: 1.2,  # Kent's aesthetic priority
    Principle.TASTEFUL: 1.0,
    Principle.CURATED: 1.0,
    Principle.HETERARCHICAL: 1.0,
    Principle.GENERATIVE: 1.0,
}


# =============================================================================
# Principle Score (Constitutional View)
# =============================================================================


@dataclass(frozen=True)
class PrincipleScore:
    """
    Score for a single principle.

    Contains score, reasoning, and evidence for constitutional evaluation.
    This is the constitutional view of principle scores (vs. the DP view
    in dp_bridge.PrincipleScore).
    """

    principle: Principle
    score: float  # 0.0 - 1.0
    reasoning: str
    evidence: str = ""

    @property
    def weighted_score(self) -> float:
        """Score multiplied by constitutional weight."""
        return self.score * PRINCIPLE_WEIGHTS.get(self.principle, 1.0)

    def to_dp_score(self) -> DPPrincipleScore:
        """Convert to DP-bridge PrincipleScore."""
        return DPPrincipleScore(
            principle=self.principle,
            score=self.score,
            evidence=self.reasoning,
            weight=PRINCIPLE_WEIGHTS.get(self.principle, 1.0),
        )


# =============================================================================
# Constitutional Evaluation
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalEvaluation:
    """
    Full constitutional evaluation of an action.

    Evaluates state transition (s, a, s') against all 7 principles.
    Returns aggregated scores and principle-by-principle breakdown.

    Example:
        >>> eval = Constitution.evaluate(state_before, action, state_after)
        >>> print(f"Total: {eval.weighted_total:.2f}")
        >>> print(f"Ethical: {eval.by_principle[Principle.ETHICAL]:.2f}")
    """

    scores: tuple[PrincipleScore, ...]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def weighted_total(self) -> float:
        """
        Weighted sum of principle scores, normalized to [0, 1].

        Formula: Σᵢ (scoreᵢ × weightᵢ) / Σᵢ weightᵢ
        """
        if not self.scores:
            return 0.0

        total = sum(ps.weighted_score for ps in self.scores)
        weight_sum = sum(PRINCIPLE_WEIGHTS.get(ps.principle, 1.0) for ps in self.scores)

        return total / weight_sum if weight_sum > 0 else 0.0

    @property
    def by_principle(self) -> dict[Principle, float]:
        """Map from principle to raw score."""
        return {ps.principle: ps.score for ps in self.scores}

    @property
    def min_score(self) -> float:
        """Minimum principle score (bottleneck)."""
        if not self.scores:
            return 0.0
        return min(ps.score for ps in self.scores)

    @property
    def max_score(self) -> float:
        """Maximum principle score."""
        if not self.scores:
            return 0.0
        return max(ps.score for ps in self.scores)

    def satisfies_threshold(self, threshold: float = 0.5) -> bool:
        """Check if all principles meet minimum threshold."""
        return all(ps.score >= threshold for ps in self.scores)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "weighted_total": self.weighted_total,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "scores": [
                {
                    "principle": ps.principle.name,
                    "score": ps.score,
                    "weighted": ps.weighted_score,
                    "reasoning": ps.reasoning,
                    "evidence": ps.evidence,
                }
                for ps in self.scores
            ],
            "timestamp": self.timestamp.isoformat(),
        }


# =============================================================================
# Constitution: The Reward Function
# =============================================================================


class Constitution:
    """
    The Constitutional Reward Function.

    Every agent action is evaluated against the 7 principles.
    This is THE reward function for the kgents DP-native architecture.

    Usage:
        >>> eval = Constitution.evaluate(state_before, action, state_after)
        >>> reward = eval.weighted_total

    Philosophy:
        The Constitution isn't aspirational documentation. It's the actual
        mathematical function that scores every action. If an action violates
        ETHICAL, it gets low reward. If it satisfies all principles, high reward.

        This makes constitutional compliance INTRINSIC to the system, not
        enforced from outside.
    """

    @staticmethod
    def evaluate(
        state_before: Any,
        action: Any,
        state_after: Any,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        Evaluate action against all principles.

        Args:
            state_before: State before action
            action: Action taken (can be any type)
            state_after: State after action
            context: Optional context dict with additional info

        Returns:
            ConstitutionalEvaluation with scores for all principles
        """
        context = context or {}
        scores = []

        # Evaluate each principle
        scores.append(Constitution._evaluate_tasteful(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_curated(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_ethical(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_joy(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_composable(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_heterarchical(state_before, action, state_after, context))
        scores.append(Constitution._evaluate_generative(state_before, action, state_after, context))

        return ConstitutionalEvaluation(scores=tuple(scores))

    # =========================================================================
    # Principle Evaluators
    # =========================================================================

    @staticmethod
    def _evaluate_tasteful(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        TASTEFUL: Each agent serves a clear, justified purpose.

        Scoring:
        - 1.0: Action has clear, singular purpose
        - 0.5: Action has purpose but it's muddled
        - 0.0: Action is bloat/feature-creep
        """
        # Default heuristic: actions with clear names are tasteful
        action_str = str(a).lower()

        # Penalty patterns (bloat indicators)
        bloat_patterns = ["misc", "util", "helper", "temp", "test", "debug"]
        if any(pattern in action_str for pattern in bloat_patterns):
            return PrincipleScore(
                principle=Principle.TASTEFUL,
                score=0.3,
                reasoning="Action name suggests unclear purpose (bloat pattern)",
            )

        # Reward patterns (clear purpose)
        clear_patterns = ["solve", "compute", "analyze", "verify", "validate"]
        if any(pattern in action_str for pattern in clear_patterns):
            return PrincipleScore(
                principle=Principle.TASTEFUL,
                score=0.9,
                reasoning="Action has clear, specific purpose",
            )

        # Default: neutral
        return PrincipleScore(
            principle=Principle.TASTEFUL,
            score=0.6,
            reasoning="Action purpose is identifiable but not exceptional",
        )

    @staticmethod
    def _evaluate_curated(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        CURATED: Intentional selection over exhaustive cataloging.

        Scoring:
        - 1.0: Action is deliberate and selective
        - 0.5: Action is acceptable but not curated
        - 0.0: Action is feature creep or "just in case"
        """
        # Check if action is marked as intentional
        is_intentional = ctx.get("intentional", False)
        if is_intentional:
            return PrincipleScore(
                principle=Principle.CURATED,
                score=1.0,
                reasoning="Action explicitly marked as intentional",
                evidence=str(ctx.get("curation_rationale", "")),
            )

        # Heuristic: does the action produce focused output?
        # (Proxy: does state complexity decrease or stay same?)
        complexity_before = len(str(s))
        complexity_after = len(str(s_))

        if complexity_after > complexity_before * 2:
            return PrincipleScore(
                principle=Principle.CURATED,
                score=0.3,
                reasoning="Action significantly increases state complexity (potential bloat)",
            )

        return PrincipleScore(
            principle=Principle.CURATED,
            score=0.7,
            reasoning="Action maintains reasonable state complexity",
        )

    @staticmethod
    def _evaluate_ethical(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        ETHICAL: Agents augment human capability, never replace judgment.

        Scoring:
        - 1.0: Action preserves human agency
        - 0.5: Action is neutral
        - 0.0: Action undermines human judgment
        """
        # Check for explicit ethical markers
        preserves_agency = ctx.get("preserves_human_agency", True)

        if not preserves_agency:
            return PrincipleScore(
                principle=Principle.ETHICAL,
                score=0.0,
                reasoning="Action explicitly marked as replacing human judgment",
                evidence="VIOLATION: Does not preserve human agency",
            )

        # Check if action is deterministic (predictable = ethical)
        is_deterministic = ctx.get("deterministic", True)
        if is_deterministic:
            return PrincipleScore(
                principle=Principle.ETHICAL,
                score=1.0,
                reasoning="Action is deterministic and predictable",
            )

        return PrincipleScore(
            principle=Principle.ETHICAL,
            score=0.8,
            reasoning="Action appears to preserve human agency",
        )

    @staticmethod
    def _evaluate_joy(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        JOY_INDUCING: Delight in interaction.

        Scoring:
        - 1.0: Action is delightful (elegant, surprising in a good way)
        - 0.5: Action is functional but not joyful
        - 0.0: Action is tedious or frustrating
        """
        # Check for explicit joy markers
        is_joyful = ctx.get("joyful", False)
        joy_evidence = ctx.get("joy_evidence", "")

        if is_joyful:
            return PrincipleScore(
                principle=Principle.JOY_INDUCING,
                score=0.9,
                reasoning="Action explicitly designed for delight",
                evidence=joy_evidence,
            )

        # Heuristic: elegant actions are joyful
        # (Proxy: simple action, complex result = elegance)
        action_complexity = len(str(a))
        if action_complexity < 20:  # Simple action
            state_improvement = len(str(s_)) - len(str(s))
            if state_improvement > 0:
                return PrincipleScore(
                    principle=Principle.JOY_INDUCING,
                    score=0.7,
                    reasoning="Simple action, positive result (elegant)",
                )

        return PrincipleScore(
            principle=Principle.JOY_INDUCING,
            score=0.5,
            reasoning="Action is functional but not remarkably delightful",
        )

    @staticmethod
    def _evaluate_composable(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        COMPOSABLE: Agents are morphisms in a category.

        Scoring:
        - 1.0: Action satisfies composition laws
        - 0.5: Action composes but may violate laws
        - 0.0: Action breaks composition
        """
        # Check if action satisfies identity law
        satisfies_identity = ctx.get("satisfies_identity", True)

        # Check if action satisfies associativity
        satisfies_associativity = ctx.get("satisfies_associativity", True)

        if satisfies_identity and satisfies_associativity:
            return PrincipleScore(
                principle=Principle.COMPOSABLE,
                score=1.0,
                reasoning="Action satisfies categorical composition laws",
                evidence="Identity + Associativity verified",
            )

        if not satisfies_identity:
            return PrincipleScore(
                principle=Principle.COMPOSABLE,
                score=0.3,
                reasoning="Action violates identity law",
                evidence="VIOLATION: Does not compose with identity",
            )

        if not satisfies_associativity:
            return PrincipleScore(
                principle=Principle.COMPOSABLE,
                score=0.3,
                reasoning="Action violates associativity",
                evidence="VIOLATION: Grouping affects result",
            )

        return PrincipleScore(
            principle=Principle.COMPOSABLE,
            score=0.8,
            reasoning="Action appears composable (laws not explicitly verified)",
        )

    @staticmethod
    def _evaluate_heterarchical(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        HETERARCHICAL: Agents exist in flux, not fixed hierarchy.

        Scoring:
        - 1.0: Action enables both leading and following
        - 0.5: Action is neutral
        - 0.0: Action enforces rigid hierarchy
        """
        # Check for hierarchy enforcement
        enforces_hierarchy = ctx.get("enforces_hierarchy", False)

        if enforces_hierarchy:
            return PrincipleScore(
                principle=Principle.HETERARCHICAL,
                score=0.2,
                reasoning="Action enforces rigid hierarchy",
                evidence="VIOLATION: Fixed roles, not flux",
            )

        # Check if action enables role fluidity
        enables_fluidity = ctx.get("enables_fluidity", False)

        if enables_fluidity:
            return PrincipleScore(
                principle=Principle.HETERARCHICAL,
                score=1.0,
                reasoning="Action enables agents to shift roles",
                evidence="Supports heterarchical flux",
            )

        return PrincipleScore(
            principle=Principle.HETERARCHICAL,
            score=0.7,
            reasoning="Action does not enforce hierarchy",
        )

    @staticmethod
    def _evaluate_generative(s: Any, a: Any, s_: Any, ctx: dict[str, Any]) -> PrincipleScore:
        """
        GENERATIVE: Spec is compression (can regenerate from spec).

        Scoring:
        - 1.0: Action/result is fully regenerable from spec
        - 0.5: Partial regenerability
        - 0.0: Not regenerable (implementation detail)
        """
        # Check if action has specification
        has_spec = ctx.get("has_spec", False)
        regenerability_score = ctx.get("regenerability_score", 0.5)

        if has_spec and regenerability_score > 0.8:
            return PrincipleScore(
                principle=Principle.GENERATIVE,
                score=1.0,
                reasoning="Action is fully specified and regenerable",
                evidence=f"Regenerability: {regenerability_score:.2f}",
            )

        if not has_spec:
            return PrincipleScore(
                principle=Principle.GENERATIVE,
                score=0.3,
                reasoning="Action lacks specification (implementation detail)",
            )

        return PrincipleScore(
            principle=Principle.GENERATIVE,
            score=regenerability_score,
            reasoning=f"Partial regenerability: {regenerability_score:.2f}",
        )


# =============================================================================
# Probe-Specific Constitutional Rewards
# =============================================================================


class ProbeRewards:
    """
    Constitutional rewards specific to TruthFunctor probe types.

    Each probe type gets its own constitutional evaluation tailored to
    what that probe tests. This bridges categorical law testing to
    constitutional principle evaluation.

    Philosophy:
        Different probes test different aspects of reasoning. The constitutional
        evaluation reflects what each probe measures:

        - NullProbe tests ETHICAL (predictability) + COMPOSABLE (identity law)
        - ChaosProbe tests ETHICAL (robustness) + JOY (handling chaos)
        - MonadProbe tests COMPOSABLE (monad laws)
        - SheafProbe tests ETHICAL (coherence) + GENERATIVE (consistency)
    """

    @staticmethod
    def null_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        NullProbe: Tests identity element (no-op should be harmless).

        Constitutional focus:
        - ETHICAL: 1.0 (fully predictable, no side effects)
        - COMPOSABLE: 1.0 (satisfies identity law by definition)
        - GENERATIVE: 0.5 (minimal but present)
        """
        scores = (
            PrincipleScore(
                Principle.ETHICAL,
                1.0,
                "Null action is fully predictable and safe",
            ),
            PrincipleScore(
                Principle.COMPOSABLE,
                1.0,
                "Satisfies identity law (f >> null = f)",
            ),
            PrincipleScore(
                Principle.GENERATIVE,
                0.5,
                "Minimal specification (null action)",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)

    @staticmethod
    def chaos_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        survived: bool = True,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        ChaosProbe: Tests robustness to random perturbations.

        Constitutional focus:
        - ETHICAL: Penalty if agent breaks under chaos
        - JOY_INDUCING: Mild reward for handling chaos gracefully
        - HETERARCHICAL: Tests adaptability (flux vs. rigid)
        """
        ethical_score = 0.5 + 0.5 * survived  # Full score if survived
        joy_score = 0.3 if survived else 0.1  # Mild joy from grace under pressure

        scores = (
            PrincipleScore(
                Principle.ETHICAL,
                ethical_score,
                "Agent broke under chaos" if not survived else "Agent survived chaos",
                evidence="Robustness test",
            ),
            PrincipleScore(
                Principle.JOY_INDUCING,
                joy_score,
                "Handling chaos is mildly delightful",
            ),
            PrincipleScore(
                Principle.HETERARCHICAL,
                0.8 if survived else 0.2,
                "Adaptation to chaos shows fluidity",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)

    @staticmethod
    def monad_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        identity_satisfied: bool = True,
        associativity_satisfied: bool = True,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        MonadProbe: Tests monad laws (identity, associativity).

        Constitutional focus:
        - COMPOSABLE: Direct test of composition laws
        - ETHICAL: Law satisfaction = predictability
        """
        composable_score = 0.0
        if identity_satisfied and associativity_satisfied:
            composable_score = 1.0
        elif identity_satisfied or associativity_satisfied:
            composable_score = 0.5

        scores = (
            PrincipleScore(
                Principle.COMPOSABLE,
                composable_score,
                f"Identity: {identity_satisfied}, Assoc: {associativity_satisfied}",
                evidence="Monad law verification",
            ),
            PrincipleScore(
                Principle.ETHICAL,
                composable_score,  # Law satisfaction = predictability
                "Law-abiding reasoning is ethical reasoning",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)

    @staticmethod
    def sheaf_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        coherence_score: float = 1.0,
        violation_count: int = 0,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        SheafProbe: Tests coherence (no contradictions).

        Constitutional focus:
        - ETHICAL: Coherence = honesty = ethical
        - GENERATIVE: Consistent claims are regenerable
        - COMPOSABLE: Sheaf gluing = optimal substructure
        """
        scores = (
            PrincipleScore(
                Principle.ETHICAL,
                coherence_score,
                f"Coherence score: {coherence_score:.2f}",
                evidence=f"Violations: {violation_count}",
            ),
            PrincipleScore(
                Principle.GENERATIVE,
                coherence_score,
                "Coherent reasoning is regenerable",
            ),
            PrincipleScore(
                Principle.COMPOSABLE,
                coherence_score,
                "Sheaf coherence = optimal substructure",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)

    @staticmethod
    def middle_invariance_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        invariance_satisfied: bool = True,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        MiddleInvarianceProbe: Tests prompt stability.

        Constitutional focus:
        - ETHICAL: Invariance = predictability
        - COMPOSABLE: Middle-invariance is a composition law
        """
        score = 1.0 if invariance_satisfied else 0.3

        scores = (
            PrincipleScore(
                Principle.ETHICAL,
                score,
                "Middle-invariance = predictable reasoning",
            ),
            PrincipleScore(
                Principle.COMPOSABLE,
                score,
                "Satisfies middle-invariance law",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)

    @staticmethod
    def variator_probe_reward(
        s: Any,
        a: Any,
        s_: Any,
        semantic_preserved: bool = True,
        context: dict[str, Any] | None = None,
    ) -> ConstitutionalEvaluation:
        """
        MonadVariatorProbe: Tests semantic-preserving transformations.

        Constitutional focus:
        - GENERATIVE: Semantic preservation = regenerability
        - COMPOSABLE: Variators are natural transformations
        """
        score = 1.0 if semantic_preserved else 0.4

        scores = (
            PrincipleScore(
                Principle.GENERATIVE,
                score,
                "Semantic preservation enables regeneration",
            ),
            PrincipleScore(
                Principle.COMPOSABLE,
                score,
                "Variator is a natural transformation",
            ),
        )
        return ConstitutionalEvaluation(scores=scores)


# =============================================================================
# Galois Loss Integration
# =============================================================================


async def compute_galois_loss(
    output: str,
    llm: Any,
    temperature: float = 0.0,
) -> float:
    """
    Compute Galois loss for regenerability testing.

    The Galois loss measures how well an output can be restructured into
    modular form and then reconstituted back to the original:

        L(P) = d(P, C(R(P)))

    Where:
    - P = original output
    - R = restructure into modular form
    - C = reconstitute back from modular form
    - d = semantic distance

    Low loss = high regenerability (GENERATIVE principle satisfaction).

    Args:
        output: The output to test
        llm: LLM client with generate() method
        temperature: Generation temperature

    Returns:
        Loss value in [0, 1] where 0 = perfect regeneration
    """
    try:
        # Step 1: Restructure into modular form
        restructure_prompt = f"""Restructure this output into modular, self-contained components.
Each component should be independent and recombinable.

Output:
{output}

Modular components:"""

        restructure_response = await llm.generate(
            system="You restructure outputs into modular forms.",
            user=restructure_prompt,
            temperature=temperature,
        )
        modular = restructure_response.text if hasattr(restructure_response, "text") else str(restructure_response)

        # Step 2: Reconstitute back from modular form
        reconstitute_prompt = f"""Given these modular components, reconstitute the original output.

Components:
{modular}

Reconstituted output:"""

        reconstitute_response = await llm.generate(
            system="You reconstitute modular components into coherent outputs.",
            user=reconstitute_prompt,
            temperature=temperature,
        )
        reconstituted = reconstitute_response.text if hasattr(reconstitute_response, "text") else str(reconstitute_response)

        # Step 3: Measure semantic distance
        # Simple heuristic: normalized Levenshtein distance
        distance = _levenshtein_distance(output, reconstituted)
        max_len = max(len(output), len(reconstituted), 1)
        loss = min(1.0, distance / max_len)

        logger.debug(f"Galois loss: {loss:.3f} (distance={distance}, max_len={max_len})")
        return loss

    except Exception as e:
        logger.warning(f"Galois loss computation failed: {e}")
        return 1.0  # Max loss on failure


def _levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute Levenshtein (edit) distance between two strings.

    Classic dynamic programming solution.
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer than s2
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Principle (re-exported)
    "Principle",
    # Weights
    "PRINCIPLE_WEIGHTS",
    # Scores
    "PrincipleScore",
    "ConstitutionalEvaluation",
    # Constitution
    "Constitution",
    # Probe rewards
    "ProbeRewards",
    # Galois loss
    "compute_galois_loss",
]
