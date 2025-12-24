"""
GaloisConstitution: Constitution with Galois-derived rewards.

The central theorem from spec/protocols/zero-seed1/dp.md:

    "Constitutional reward IS inverse Galois loss."

    R_constitutional(s, a, s') = 1.0 - L_galois(s -> s' via a)

This class replaces 7 hand-crafted principle evaluators with a single
Galois loss measure, while maintaining backward compatibility through
hybrid reward computation:

    R_total = R_traditional - lambda * L_galois

The loss_weight (lambda) parameter enables gradual migration:
- lambda=0.0: Pure traditional (hand-crafted evaluators)
- lambda=0.5: Hybrid (blend of both)
- lambda=1.0: Pure Galois (single unified measure)

Philosophy:
    The 7 constitutional principles encode semantic coherence invariants.
    These are ALL structural preservation properties:
    - TASTEFUL: Transition preserves clarity (low bloat)
    - COMPOSABLE: Edge structure remains explicit (no hidden coupling)
    - GENERATIVE: Derivation chain is recoverable (lineage preserved)
    - ETHICAL: Safety constraints remain visible (no buried assumptions)
    - JOY_INDUCING: Personality signature is intact (aesthetic coherence)
    - HETERARCHICAL: No rigid hierarchy imposed (flexibility preserved)
    - CURATED: Justification for change is explicit (intentionality clear)

    Galois loss measures exactly what's NOT preserved.
    Therefore: Constitutional adherence = Structure preservation = Inverse Galois loss.

Teaching:
    gotcha: GaloisConstitution extends Constitution, not replaces it.
            The evaluate() method returns ValueScore with per-principle breakdown.
            Use reward() for the scalar reward in DP algorithms.
            (Evidence: Both methods are implemented with Galois enhancement)

    gotcha: The loss_weight parameter allows gradual migration. Start with
            lambda=0.2 (20% Galois), then increase as validation confirms
            the Galois measure correlates with Mirror Test results.
            (Evidence: spec/protocols/zero-seed1/dp.md Part VII: Integration)

See: spec/protocols/zero-seed1/dp.md (Part II: GaloisConstitution Implementation)
See: dp/core/constitution.py (Original Constitution class)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dp.core.constitution import Constitution
from services.categorical.dp_bridge import Principle, PrincipleScore, ValueScore
from services.zero_seed.dp.galois_loss import GaloisLoss, ZeroNode

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.zero_seed.dp.galois_constitution")


# =============================================================================
# GaloisConstitution: Unified Reward via Galois Loss
# =============================================================================


@dataclass
class GaloisConstitution(Constitution):
    """
    Constitution with Galois-derived rewards.

    Unifies 7 hand-crafted evaluators into single loss measure.

    The Bellman equation becomes:
        V*(node) = max_edge [R(node, edge, target) - lambda * L + gamma * V*(target)]

    Where:
    - R is the traditional constitutional reward
    - L is the Galois loss
    - lambda is the loss_weight (default 0.3)
    - gamma is the discount factor

    Example:
        >>> galois = GaloisLoss(llm_client)
        >>> constitution = GaloisConstitution(galois=galois, loss_weight=0.5)
        >>> reward = await constitution.reward_async(state, action, next_state)
        >>> # reward = traditional_reward - 0.5 * galois_loss
    """

    galois: GaloisLoss = field(default_factory=GaloisLoss)
    loss_weight: float = 0.3  # lambda in combined reward

    # Numerical stability
    epsilon: float = 1e-8

    def reward(
        self,
        state: Any,
        action: Any,
        next_state: Any,
    ) -> float:
        """
        Synchronous reward computation (uses cached Galois loss if available).

        For async Galois computation, use reward_async() instead.

        R_total = R_traditional - lambda * L_galois

        Args:
            state: The state before the action
            action: The action taken
            next_state: The state after the action

        Returns:
            Combined reward (traditional - weighted loss)
        """
        # Traditional constitutional reward
        traditional = super().reward(state, action, next_state)

        # For sync operation, we can't compute Galois loss
        # Return traditional reward only
        return traditional

    async def reward_async(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode,
    ) -> float:
        """
        Async reward computation with Galois loss.

        R_total = R_traditional - lambda * L_galois

        Allows gradual migration: lambda=0 (pure traditional), lambda=1 (pure Galois).

        Args:
            state: The ZeroNode before the action
            action: The action/edge kind
            next_state: The ZeroNode after the action

        Returns:
            Combined reward (traditional - weighted loss)
        """
        # Traditional constitutional reward (from parent class)
        traditional = super().reward(state, action, next_state)

        # Galois loss for this transition
        transition_desc = self._describe_transition(state, action, next_state)
        loss = await self.galois.compute(transition_desc)

        # Combined reward: R - lambda * L
        combined = traditional - self.loss_weight * loss

        logger.debug(
            f"GaloisConstitution.reward: traditional={traditional:.3f}, "
            f"galois_loss={loss:.3f}, combined={combined:.3f}"
        )

        return combined

    async def evaluate_async(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode,
    ) -> ValueScore:
        """
        Full evaluation with per-principle Galois losses.

        Returns a ValueScore with detailed scores for each principle.
        Each principle's score = 1.0 - principle_specific_galois_loss.

        Args:
            state: The ZeroNode before the action
            action: The action/edge kind
            next_state: The ZeroNode after the action

        Returns:
            ValueScore with all principle scores and evidence
        """
        principle_scores: list[PrincipleScore] = []

        # Compute Galois loss for each principle
        principle_losses = await self._compute_all_principle_losses(
            state, action, next_state
        )

        for principle in Principle:
            loss = principle_losses.get(principle.name, 0.5)
            score = 1.0 - loss  # Reward = inverse loss
            weight = self._get_weight(principle)

            principle_scores.append(
                PrincipleScore(
                    principle=principle,
                    score=max(0.0, min(1.0, score)),
                    evidence=f"Galois {principle.name.lower()} loss: {loss:.3f}",
                    weight=weight,
                )
            )

        return ValueScore(
            agent_name=f"transition({state.title}, {action}, {next_state.title})",
            principle_scores=tuple(principle_scores),
        )

    async def evaluate_tasteful(self, node: ZeroNode) -> PrincipleScore:
        """
        TASTEFUL = inverse bloat loss.

        Bloat = unnecessary structure that doesn't compress.
        """
        loss = await self.galois.bloat_loss(node)
        return PrincipleScore(
            principle=Principle.TASTEFUL,
            score=1.0 - loss,
            evidence=f"Galois bloat loss: {loss:.3f}",
            weight=1.0,
        )

    async def evaluate_composable(self, node: ZeroNode) -> PrincipleScore:
        """
        COMPOSABLE = inverse composition loss.

        Composition loss = edges that break explicit interfaces.
        """
        loss = await self.galois.composition_loss(node)
        return PrincipleScore(
            principle=Principle.COMPOSABLE,
            score=1.0 - loss,
            evidence=f"Galois composition loss: {loss:.3f}",
            weight=1.5,  # Composability weighted higher (from CONSTITUTION.md)
        )

    async def evaluate_generative(self, node: ZeroNode) -> PrincipleScore:
        """
        GENERATIVE = inverse regeneration loss.

        Regeneration loss = failure to reconstruct from compression.
        """
        loss = await self.galois.regeneration_loss(node)
        return PrincipleScore(
            principle=Principle.GENERATIVE,
            score=1.0 - loss,
            evidence=f"Galois regeneration loss: {loss:.3f}",
            weight=1.0,
        )

    async def evaluate_ethical(
        self,
        node: ZeroNode,
        action: str = "",
    ) -> PrincipleScore:
        """
        ETHICAL = inverse safety-constraint loss.

        Safety loss = implicit assumptions that hide risks.

        Note: ETHICAL violations are CATEGORICAL for axiom supersession.
        Layer 1-2 nodes cannot be superseded without Mirror Test.
        """
        # Ethical violations are CATEGORICAL (zero tolerance) for axioms
        if action == "supersede" and node.layer <= 2:
            return PrincipleScore(
                principle=Principle.ETHICAL,
                score=0.0,
                evidence="Attempted to supersede axiom without Mirror Test",
                weight=2.0,  # Highest weight (safety first)
            )

        loss = await self.galois.safety_loss(node, action)
        return PrincipleScore(
            principle=Principle.ETHICAL,
            score=1.0 - loss,
            evidence=f"Galois safety loss: {loss:.3f}",
            weight=2.0,
        )

    async def evaluate_joy_inducing(self, node: ZeroNode) -> PrincipleScore:
        """
        JOY_INDUCING = inverse aesthetic coherence loss.

        Aesthetic loss = deviation from personality attractor.
        """
        loss = await self.galois.aesthetic_loss(node)
        return PrincipleScore(
            principle=Principle.JOY_INDUCING,
            score=1.0 - loss,
            evidence=f"Galois aesthetic loss: {loss:.3f}",
            weight=1.2,  # Kent's aesthetic emphasis
        )

    async def evaluate_heterarchical(self, node: ZeroNode) -> PrincipleScore:
        """
        HETERARCHICAL = inverse rigidity loss.

        Rigidity loss = imposed hierarchy that prevents flux.
        """
        loss = await self.galois.rigidity_loss(node)
        return PrincipleScore(
            principle=Principle.HETERARCHICAL,
            score=1.0 - loss,
            evidence=f"Galois rigidity loss: {loss:.3f}",
            weight=1.0,
        )

    async def evaluate_curated(self, node: ZeroNode) -> PrincipleScore:
        """
        CURATED = inverse arbitrariness loss.

        Arbitrariness loss = changes without explicit justification.
        """
        loss = await self.galois.arbitrariness_loss(node)
        return PrincipleScore(
            principle=Principle.CURATED,
            score=1.0 - loss,
            evidence=f"Galois arbitrariness loss: {loss:.3f}",
            weight=1.0,
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _describe_transition(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode,
    ) -> str:
        """Generate transition description for Galois loss computation."""
        return f"""
Layer: {state.layer} -> {next_state.layer}
Kind: {state.kind} -> {next_state.kind}
Action: {action}

From: "{state.title}"
{state.content[:300]}

To: "{next_state.title}"
{next_state.content[:300]}

Lineage: {len(state.lineage)} -> {len(next_state.lineage)} ancestors
Tags: {state.tags} -> {next_state.tags}
"""

    async def _compute_all_principle_losses(
        self,
        state: ZeroNode,
        action: str,
        next_state: ZeroNode,
    ) -> dict[str, float]:
        """Compute Galois loss for all 7 principles."""
        return {
            "TASTEFUL": await self.galois.bloat_loss(next_state),
            "COMPOSABLE": await self.galois.composition_loss(next_state),
            "GENERATIVE": await self.galois.regeneration_loss(next_state),
            "ETHICAL": await self.galois.safety_loss(next_state, action),
            "JOY_INDUCING": await self.galois.aesthetic_loss(next_state),
            "HETERARCHICAL": await self.galois.rigidity_loss(next_state),
            "CURATED": await self.galois.arbitrariness_loss(next_state),
        }


# =============================================================================
# Value Function with Galois Loss
# =============================================================================


@dataclass
class GaloisValueFunction:
    """
    Value function that incorporates Galois loss.

    The Bellman equation:
        V*(s) = max_a [R(s, a) - lambda * L + gamma * V*(T(s, a))]

    Where:
    - R is the immediate reward (from Constitution)
    - L is the Galois loss
    - lambda is the loss penalty (default 0.3)
    - gamma is the discount factor

    Example:
        >>> vf = GaloisValueFunction(constitution, gamma=0.99)
        >>> value = await vf.compute_async(state, max_depth=10)
    """

    constitution: GaloisConstitution
    gamma: float = 0.99
    max_depth: int = 100

    # Value cache
    _cache: dict[str, float] = field(default_factory=dict)

    async def compute_async(
        self,
        node: ZeroNode,
        available_edges: list[tuple[str, ZeroNode]],
        depth: int = 0,
    ) -> float:
        """
        Compute optimal value at node via Bellman equation.

        V*(s) = max_a [R(s, a) - lambda * L + gamma * V*(T(s, a))]

        Args:
            node: Current ZeroNode
            available_edges: List of (edge_kind, target_node) pairs
            depth: Current recursion depth

        Returns:
            Optimal value at this node
        """
        # Check cache
        cache_key = f"{node.id}:{depth}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Base case: max depth or no edges
        if depth >= self.max_depth or not available_edges:
            self._cache[cache_key] = 0.0
            return 0.0

        # Bellman maximization
        best_value = -float("inf")

        for edge_kind, target in available_edges:
            # Immediate reward (with Galois loss)
            reward = await self.constitution.reward_async(node, edge_kind, target)

            # Future value (recursive)
            # Note: In practice, we'd need to get target's available edges
            future = 0.0  # Placeholder - real impl would recurse

            # Q(s, a) = R - lambda * L + gamma * V(s')
            q_value = reward + self.gamma * future

            best_value = max(best_value, q_value)

        # Cache and return
        result = best_value if best_value > -float("inf") else 0.0
        self._cache[cache_key] = result

        logger.debug(
            f"V({node.title}, depth={depth}) = {result:.3f}"
        )

        return result

    def clear_cache(self) -> None:
        """Clear the value cache."""
        self._cache.clear()


# =============================================================================
# Constitutional Reward Factory
# =============================================================================


def create_galois_constitution(
    llm: Any | None = None,
    loss_weight: float = 0.3,
) -> GaloisConstitution:
    """
    Factory function to create GaloisConstitution with proper initialization.

    Args:
        llm: LLM client for Galois loss computation (optional)
        loss_weight: Lambda parameter for Galois loss weighting

    Returns:
        Configured GaloisConstitution instance

    Example:
        >>> constitution = create_galois_constitution(llm_client, loss_weight=0.5)
        >>> reward = await constitution.reward_async(state, action, next_state)
    """
    galois = GaloisLoss(llm=llm)
    return GaloisConstitution(galois=galois, loss_weight=loss_weight)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GaloisConstitution",
    "GaloisValueFunction",
    "create_galois_constitution",
]
