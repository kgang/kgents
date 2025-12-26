"""
ConstitutionalTrustComputer: Compute Trust from Constitutional History.

Trust levels (L0-L3) are earned through demonstrated constitutional alignment.
This module computes trust from accumulated constitutional metadata in crystals.

Philosophy:
    "Trust is earned through demonstrated alignment."
    — Article V: Trust Accumulation

    Unlike hardcoded thresholds, constitutional trust emerges from actual behavior.
    An agent that consistently produces high-alignment marks accumulates trust capital.
    An agent that violates principles loses trust capital.

Integration:
    - Reads from Crystal.constitutional_meta
    - Computes TrustLevel based on alignment history
    - Integrates with existing escalation criteria in services/witness/trust/escalation.py
    - Can replace or augment hardcoded escalation thresholds

Trust Level Criteria (Constitutional):
    L0 (READ_ONLY): Default, no history
    L1 (BOUNDED): avg_alignment >= 0.6, violation_rate < 0.1
    L2 (SUGGESTION): avg_alignment >= 0.8, violation_rate < 0.05, trust_capital >= 0.5
    L3 (AUTONOMOUS): avg_alignment >= 0.9, violation_rate < 0.01, trust_capital >= 1.0

See: spec/principles/CONSTITUTION.md → Article V
See: services/witness/trust/escalation.py (existing criteria)
See: services/witness/crystal.py → ConstitutionalCrystalMeta
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol, Sequence

from services.witness.crystal import Crystal, ConstitutionalCrystalMeta
from services.witness.polynomial import TrustLevel

logger = logging.getLogger("kgents.witness.constitutional_trust")


# =============================================================================
# Trust Computation Result
# =============================================================================


@dataclass(frozen=True)
class ConstitutionalTrustResult:
    """
    Result of constitutional trust computation.

    Contains the computed trust level, supporting metrics, and
    reasoning for transparency (ETHICAL principle).
    """

    # Computed trust level
    trust_level: TrustLevel

    # Supporting metrics
    total_marks_analyzed: int
    average_alignment: float
    violation_rate: float
    trust_capital: float

    # Per-principle averages (for dashboard)
    principle_averages: dict[str, float]

    # Dominant principles (top 3)
    dominant_principles: tuple[str, ...]

    # Reasoning (for transparency)
    reasoning: str

    @property
    def is_autonomous(self) -> bool:
        """True if trust level is AUTONOMOUS (L3)."""
        return self.trust_level == TrustLevel.AUTONOMOUS

    def to_dict(self) -> dict[str, any]:
        """Serialize for API/frontend."""
        return {
            "trust_level": self.trust_level.name,
            "trust_level_value": self.trust_level.value,
            "total_marks_analyzed": self.total_marks_analyzed,
            "average_alignment": self.average_alignment,
            "violation_rate": self.violation_rate,
            "trust_capital": self.trust_capital,
            "principle_averages": self.principle_averages,
            "dominant_principles": list(self.dominant_principles),
            "reasoning": self.reasoning,
        }


# =============================================================================
# Trust Computer Protocol (for DI)
# =============================================================================


class TrustComputerProtocol(Protocol):
    """Protocol for trust computers (enables DI for testing)."""

    async def compute_trust(
        self,
        agent_id: str,
        crystals: Sequence[Crystal],
    ) -> ConstitutionalTrustResult:
        """Compute trust level from constitutional history."""
        ...


# =============================================================================
# ConstitutionalTrustComputer
# =============================================================================


@dataclass
class ConstitutionalTrustComputer:
    """
    Compute trust level based on constitutional history.

    This computer analyzes crystals (which contain aggregated constitutional
    metadata) to determine the appropriate trust level for an agent.

    The Algorithm:
        1. Extract ConstitutionalCrystalMeta from each crystal
        2. Aggregate alignment trajectories, violation counts, trust earned
        3. Compute weighted average alignment (weighted by trajectory length)
        4. Compute violation rate (violations / total marks)
        5. Sum trust capital from all crystals
        6. Apply escalation criteria to determine trust level

    Escalation Criteria:
        L0 → L1: avg_alignment >= 0.6, violation_rate < 0.1
        L1 → L2: avg_alignment >= 0.8, violation_rate < 0.05, trust_capital >= 0.5
        L2 → L3: avg_alignment >= 0.9, violation_rate < 0.01, trust_capital >= 1.0

    Usage:
        >>> computer = ConstitutionalTrustComputer()
        >>> result = await computer.compute_trust("claude", crystals)
        >>> print(f"Trust level: {result.trust_level.name}")
    """

    # Escalation thresholds (configurable)
    l1_alignment_threshold: float = 0.6
    l1_violation_threshold: float = 0.1

    l2_alignment_threshold: float = 0.8
    l2_violation_threshold: float = 0.05
    l2_trust_capital_threshold: float = 0.5

    l3_alignment_threshold: float = 0.9
    l3_violation_threshold: float = 0.01
    l3_trust_capital_threshold: float = 1.0

    async def compute_trust(
        self,
        agent_id: str,
        crystals: Sequence[Crystal],
    ) -> ConstitutionalTrustResult:
        """
        Compute trust level from constitutional history.

        Args:
            agent_id: Identifier for the agent (for logging)
            crystals: Sequence of crystals with constitutional metadata

        Returns:
            ConstitutionalTrustResult with trust level and metrics
        """
        # Extract constitutional metadata
        metas = [
            c.constitutional_meta
            for c in crystals
            if c.constitutional_meta is not None
        ]

        if not metas:
            logger.debug(f"No constitutional history for {agent_id}")
            return ConstitutionalTrustResult(
                trust_level=TrustLevel.READ_ONLY,
                total_marks_analyzed=0,
                average_alignment=0.0,
                violation_rate=0.0,
                trust_capital=0.0,
                principle_averages={},
                dominant_principles=(),
                reasoning="No constitutional history available",
            )

        # Aggregate metrics
        total_marks = sum(len(m.alignment_trajectory) for m in metas)
        total_violations = sum(m.violations_count for m in metas)
        total_trust_capital = sum(m.trust_earned for m in metas)

        # Compute weighted average alignment
        weighted_sum = sum(
            m.average_alignment * len(m.alignment_trajectory)
            for m in metas
            if m.alignment_trajectory
        )
        average_alignment = weighted_sum / total_marks if total_marks > 0 else 0.0

        # Compute violation rate
        violation_rate = total_violations / total_marks if total_marks > 0 else 0.0

        # Aggregate principle averages
        principle_totals: dict[str, float] = {}
        principle_weights: dict[str, float] = {}

        for meta in metas:
            weight = len(meta.alignment_trajectory) if meta.alignment_trajectory else 1
            for principle, score in meta.principle_trends.items():
                principle_totals[principle] = principle_totals.get(principle, 0.0) + score * weight
                principle_weights[principle] = principle_weights.get(principle, 0.0) + weight

        principle_averages = {
            p: principle_totals[p] / principle_weights[p]
            for p in principle_totals
            if principle_weights[p] > 0
        }

        # Identify dominant principles
        sorted_principles = sorted(
            principle_averages.keys(),
            key=lambda p: -principle_averages[p],
        )
        dominant_principles = tuple(sorted_principles[:3])

        # Determine trust level
        trust_level, reasoning = self._compute_level(
            average_alignment=average_alignment,
            violation_rate=violation_rate,
            trust_capital=total_trust_capital,
            total_marks=total_marks,
        )

        logger.info(
            f"Constitutional trust for {agent_id}: {trust_level.name} "
            f"(alignment={average_alignment:.2f}, "
            f"violations={violation_rate:.2%}, "
            f"capital={total_trust_capital:.2f})"
        )

        return ConstitutionalTrustResult(
            trust_level=trust_level,
            total_marks_analyzed=total_marks,
            average_alignment=average_alignment,
            violation_rate=violation_rate,
            trust_capital=total_trust_capital,
            principle_averages=principle_averages,
            dominant_principles=dominant_principles,
            reasoning=reasoning,
        )

    def _compute_level(
        self,
        average_alignment: float,
        violation_rate: float,
        trust_capital: float,
        total_marks: int,
    ) -> tuple[TrustLevel, str]:
        """
        Compute trust level from metrics.

        Returns:
            Tuple of (TrustLevel, reasoning string)
        """
        # Check L3 criteria
        if (
            average_alignment >= self.l3_alignment_threshold
            and violation_rate < self.l3_violation_threshold
            and trust_capital >= self.l3_trust_capital_threshold
        ):
            return (
                TrustLevel.AUTONOMOUS,
                f"Meets L3 criteria: alignment={average_alignment:.2f}≥{self.l3_alignment_threshold}, "
                f"violations={violation_rate:.2%}<{self.l3_violation_threshold:.0%}, "
                f"capital={trust_capital:.2f}≥{self.l3_trust_capital_threshold}",
            )

        # Check L2 criteria
        if (
            average_alignment >= self.l2_alignment_threshold
            and violation_rate < self.l2_violation_threshold
            and trust_capital >= self.l2_trust_capital_threshold
        ):
            missing_for_l3 = []
            if average_alignment < self.l3_alignment_threshold:
                missing_for_l3.append(f"alignment needs {self.l3_alignment_threshold - average_alignment:.2f} more")
            if violation_rate >= self.l3_violation_threshold:
                missing_for_l3.append(f"violations need to drop below {self.l3_violation_threshold:.0%}")
            if trust_capital < self.l3_trust_capital_threshold:
                missing_for_l3.append(f"capital needs {self.l3_trust_capital_threshold - trust_capital:.2f} more")

            return (
                TrustLevel.SUGGESTION,
                f"Meets L2 criteria. For L3: {'; '.join(missing_for_l3)}",
            )

        # Check L1 criteria
        if (
            average_alignment >= self.l1_alignment_threshold
            and violation_rate < self.l1_violation_threshold
        ):
            missing_for_l2 = []
            if average_alignment < self.l2_alignment_threshold:
                missing_for_l2.append(f"alignment needs {self.l2_alignment_threshold - average_alignment:.2f} more")
            if violation_rate >= self.l2_violation_threshold:
                missing_for_l2.append(f"violations need to drop below {self.l2_violation_threshold:.0%}")
            if trust_capital < self.l2_trust_capital_threshold:
                missing_for_l2.append(f"capital needs {self.l2_trust_capital_threshold - trust_capital:.2f} more")

            return (
                TrustLevel.BOUNDED,
                f"Meets L1 criteria. For L2: {'; '.join(missing_for_l2)}",
            )

        # Default to L0
        missing_for_l1 = []
        if average_alignment < self.l1_alignment_threshold:
            missing_for_l1.append(f"alignment needs {self.l1_alignment_threshold - average_alignment:.2f} more")
        if violation_rate >= self.l1_violation_threshold:
            missing_for_l1.append(f"violations need to drop below {self.l1_violation_threshold:.0%}")

        if missing_for_l1:
            return (
                TrustLevel.READ_ONLY,
                f"For L1: {'; '.join(missing_for_l1)} ({total_marks} marks analyzed)",
            )

        return (
            TrustLevel.READ_ONLY,
            f"Insufficient history for escalation ({total_marks} marks analyzed)",
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ConstitutionalTrustResult",
    "TrustComputerProtocol",
    "ConstitutionalTrustComputer",
]
