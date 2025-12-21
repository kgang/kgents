"""
ASHC Causal Penalty Propagation

When a bet fails, propagate penalty to the principles and evidence
that led to the decision.

From Kent: "penalize a particular mode of reasoning that ASHC was using,
or the hierarchical 'appearingly causative' principles, values, and
'EVIDENCE' that led to the decision being made in the first place."

This creates accountability at the conceptual level:
- If a principle keeps leading to failures, its credibility erodes
- Evidence that was cited for wrong predictions gets discounted
- The causal chain from decision to outcome is explicit

Integration with existing infrastructure:
- Uses MarkLink (CAUSES relation) from services/witness/mark.py
- Can store principle credibility in witness/trace_store.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

from .economy import ASHCBet

# =============================================================================
# CausalPenalty: Propagating Blame
# =============================================================================


@dataclass(frozen=True)
class CausalPenalty:
    """
    A penalty propagated to principles/evidence that caused a failure.

    When a bet fails, we trace back to what was cited as justification
    and distribute blame proportionally.

    The weights determine how much blame each cited item receives:
    - Higher weight = more blame for this item
    - Weights can be based on how central the item was to the decision
    """

    bet_id: str
    penalty_amount: float  # Total penalty to distribute

    # What gets blamed
    principles_penalized: tuple[str, ...]  # e.g., ("composable", "tasteful")
    evidence_penalized: tuple[str, ...]  # e.g., ("run_abc123", "run_def456")
    reasoning_steps_penalized: tuple[str, ...] = ()  # Chain of reasoning

    # How blame is distributed (principle_id → weight)
    # Weights should sum to 1.0
    principle_weights: dict[str, float] = field(default_factory=dict)
    evidence_weights: dict[str, float] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)

    def blame_for_principle(self, principle_id: str) -> float:
        """Get the blame amount for a specific principle."""
        weight = self.principle_weights.get(principle_id, 0.0)
        return self.penalty_amount * weight

    def blame_for_evidence(self, evidence_id: str) -> float:
        """Get the blame amount for a specific piece of evidence."""
        weight = self.evidence_weights.get(evidence_id, 0.0)
        return self.penalty_amount * weight

    @classmethod
    def from_bet(
        cls,
        bet: ASHCBet,
        penalty_amount: float,
        principle_weights: dict[str, float] | None = None,
        evidence_weights: dict[str, float] | None = None,
    ) -> "CausalPenalty":
        """
        Create a causal penalty from a failed bet.

        If weights aren't provided, distribute blame equally.
        """
        if not bet.resolved or bet.actual_success:
            raise ValueError("Can only create penalty from failed bet")

        # Default to equal distribution
        if principle_weights is None and bet.principles_cited:
            n = len(bet.principles_cited)
            principle_weights = {p: 1.0 / n for p in bet.principles_cited}

        if evidence_weights is None and bet.evidence_cited:
            n = len(bet.evidence_cited)
            evidence_weights = {e: 1.0 / n for e in bet.evidence_cited}

        return cls(
            bet_id=bet.bet_id,
            penalty_amount=penalty_amount,
            principles_penalized=bet.principles_cited,
            evidence_penalized=bet.evidence_cited,
            reasoning_steps_penalized=bet.reasoning_trace,
            principle_weights=principle_weights or {},
            evidence_weights=evidence_weights or {},
        )


# =============================================================================
# PrincipleCredibility: Per-Principle Trust
# =============================================================================


@dataclass
class PrincipleCredibility:
    """
    Track credibility for a single principle.

    Each principle (e.g., "composable", "tasteful", "joy-inducing")
    has its own credibility that erodes when cited for failures.

    This answers: "Which principles are actually predictive of success?"

    Low-credibility principles get less weight in future decisions.
    """

    principle_id: str
    credibility: float = 1.0  # 1.0 = fully trusted, 0.0 = discredited
    times_cited: int = 0  # Total times this principle was invoked
    times_blamed: int = 0  # Times this principle led to failure
    total_blame: float = 0.0  # Cumulative blame received

    # Recovery rate (slower than ASHC global credibility)
    BLAME_DECAY: ClassVar[float] = 0.001  # Per successful citation

    def cite(self) -> None:
        """Record that this principle was cited in a decision."""
        self.times_cited += 1

    def blame(self, weight: float) -> None:
        """
        Reduce credibility when this principle led to failure.

        Args:
            weight: Blame amount (0.0-1.0)
        """
        self.times_blamed += 1
        self.total_blame += weight
        self.credibility = max(0.0, self.credibility - weight)

    def reward(self, weight: float = 0.01) -> None:
        """
        Slightly increase credibility when this principle led to success.

        Recovery is slow—principles must prove themselves repeatedly.
        """
        self.credibility = min(1.0, self.credibility + weight)

    @property
    def blame_rate(self) -> float:
        """What fraction of citations led to blame?"""
        if self.times_cited == 0:
            return 0.0
        return self.times_blamed / self.times_cited

    @property
    def is_discredited(self) -> bool:
        """Has this principle lost all credibility?"""
        return self.credibility <= 0.0

    @property
    def is_predictive(self) -> bool:
        """
        Is this principle predictive of success?

        A principle is predictive if it's been cited often
        and rarely blamed.
        """
        return self.times_cited >= 5 and self.blame_rate < 0.2


# =============================================================================
# PrincipleRegistry: Track All Principles
# =============================================================================


@dataclass
class PrincipleRegistry:
    """
    Registry of all principle credibilities.

    Provides aggregated view of which principles are working
    and which are leading to failures.
    """

    principles: dict[str, PrincipleCredibility] = field(default_factory=dict)

    def get_or_create(self, principle_id: str) -> PrincipleCredibility:
        """Get principle credibility, creating if needed."""
        if principle_id not in self.principles:
            self.principles[principle_id] = PrincipleCredibility(principle_id)
        return self.principles[principle_id]

    def cite_all(self, principle_ids: tuple[str, ...]) -> None:
        """Record citation for multiple principles."""
        for pid in principle_ids:
            self.get_or_create(pid).cite()

    def apply_penalty(self, penalty: CausalPenalty) -> None:
        """
        Apply a causal penalty to all cited principles.

        This propagates blame from a failed bet to the principles
        that were cited in its justification.
        """
        for principle_id in penalty.principles_penalized:
            principle = self.get_or_create(principle_id)
            blame = penalty.blame_for_principle(principle_id)
            if blame > 0:
                principle.blame(blame)

    def apply_reward(self, principle_ids: tuple[str, ...], weight: float = 0.01) -> None:
        """
        Reward principles that led to success.

        Recovery is slow and requires repeated success.
        """
        for pid in principle_ids:
            self.get_or_create(pid).reward(weight)

    @property
    def discredited_principles(self) -> list[str]:
        """Get list of principles that have lost all credibility."""
        return [p.principle_id for p in self.principles.values() if p.is_discredited]

    @property
    def predictive_principles(self) -> list[str]:
        """Get list of principles that are predictive of success."""
        return [p.principle_id for p in self.principles.values() if p.is_predictive]

    def credibility_ranking(self) -> list[tuple[str, float]]:
        """Get principles ranked by credibility (highest first)."""
        return sorted(
            [(p.principle_id, p.credibility) for p in self.principles.values()],
            key=lambda x: x[1],
            reverse=True,
        )

    def effective_weight(self, principle_id: str) -> float:
        """
        Get the effective weight for a principle in future decisions.

        Low-credibility principles get less weight.
        """
        if principle_id not in self.principles:
            return 1.0  # New principles start trusted
        return self.principles[principle_id].credibility


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CausalPenalty",
    "PrincipleCredibility",
    "PrincipleRegistry",
]
