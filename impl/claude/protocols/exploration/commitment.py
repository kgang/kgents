"""
ASHC Commitment Protocol: Claims require evidence from exploration.

Before an agent can commit a claim, the protocol enforces:
1. Evidence Quantity: Minimum N evidence items
2. Evidence Quality: At least M "strong" evidence items
3. No Counterevidence: All counterevidence addressed
4. Trail Exists: Exploration trail supporting claim

Commitment Levels:
- TENTATIVE: Any evidence → "I observed X"
- MODERATE: 3+ evidence, 1+ strong → "Evidence suggests X"
- STRONG: 5+ evidence, 2+ strong, no counter → "X is likely true"
- DEFINITIVE: 10+ evidence, 5+ strong, all counter addressed → "X is true"

Teaching:
    gotcha: ASHC = Agentic Self-Hosted Compiler (NOT "Argument-Structured
            Hierarchical Commitment"). The commitment protocol is part of
            how the compiler accumulates evidence.

    gotcha: Commitment is irreversible at a level. Once committed as "strong",
            cannot downgrade to "weak". This is Law 11.2.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .types import (
    Claim,
    CommitmentLevel,
    CommitmentResult,
    Counterevidence,
    Evidence,
    EvidenceStrength,
    Trail,
)


# =============================================================================
# Commitment Requirements
# =============================================================================


@dataclass(frozen=True)
class CommitmentRequirements:
    """Requirements for a commitment level."""

    min_evidence: int
    min_strong: int
    allow_unaddressed_counter: bool
    require_trail: bool

    @classmethod
    def for_level(cls, level: CommitmentLevel) -> CommitmentRequirements:
        """Get requirements for a commitment level."""
        requirements = {
            CommitmentLevel.TENTATIVE: cls(
                min_evidence=1,
                min_strong=0,
                allow_unaddressed_counter=True,
                require_trail=False,
            ),
            CommitmentLevel.MODERATE: cls(
                min_evidence=3,
                min_strong=1,
                allow_unaddressed_counter=True,
                require_trail=True,
            ),
            CommitmentLevel.STRONG: cls(
                min_evidence=5,
                min_strong=2,
                allow_unaddressed_counter=False,
                require_trail=True,
            ),
            CommitmentLevel.DEFINITIVE: cls(
                min_evidence=10,
                min_strong=5,
                allow_unaddressed_counter=False,
                require_trail=True,
            ),
        }
        return requirements[level]


# =============================================================================
# Commitment Check Result
# =============================================================================


@dataclass
class CommitmentCheckResult:
    """Detailed result of a commitment check."""

    result: CommitmentResult
    level: CommitmentLevel | None  # The level being checked
    evidence_count: int
    strong_count: int
    unaddressed_counter_count: int
    trail_supports: bool
    message: str

    @property
    def approved(self) -> bool:
        return self.result == CommitmentResult.APPROVED


# =============================================================================
# ASHC Commitment
# =============================================================================


@dataclass
class ASHCCommitment:
    """
    Agentic Self-Hosted Compiler commitment protocol.

    Claims require evidence from exploration. This class checks
    whether a claim can be committed at a given level based on
    the evidence gathered during exploration.
    """

    # Configurable thresholds (defaults match spec)
    min_evidence_for_tentative: int = 1
    min_evidence_for_moderate: int = 3
    min_evidence_for_strong: int = 5
    min_evidence_for_definitive: int = 10

    min_strong_for_moderate: int = 1
    min_strong_for_strong: int = 2
    min_strong_for_definitive: int = 5

    # Committed claims (for irreversibility check)
    _committed: dict[str, CommitmentLevel] = field(default_factory=dict)

    def can_commit(
        self,
        claim: Claim,
        trail: Trail,
        evidence: list[Evidence],
        counterevidence: list[Counterevidence] | None = None,
        target_level: CommitmentLevel = CommitmentLevel.MODERATE,
    ) -> CommitmentCheckResult:
        """
        Check if a claim can be committed at the target level.

        Args:
            claim: The claim to commit
            trail: The exploration trail
            evidence: Evidence supporting the claim
            counterevidence: Evidence contradicting the claim
            target_level: The commitment level to check

        Returns:
            CommitmentCheckResult with detailed information
        """
        counterevidence = counterevidence or []
        requirements = CommitmentRequirements.for_level(target_level)

        # Count evidence
        evidence_count = len(evidence)
        strong_count = sum(
            1 for e in evidence if e.strength == EvidenceStrength.STRONG
        )
        unaddressed_counter = [c for c in counterevidence if not c.addressed]

        # Check trail support
        trail_supports = self._trail_supports_claim(trail, claim, evidence)

        # Check quantity
        if evidence_count < requirements.min_evidence:
            return CommitmentCheckResult(
                result=CommitmentResult.INSUFFICIENT_QUANTITY,
                level=target_level,
                evidence_count=evidence_count,
                strong_count=strong_count,
                unaddressed_counter_count=len(unaddressed_counter),
                trail_supports=trail_supports,
                message=(
                    f"Need {requirements.min_evidence} evidence items, "
                    f"have {evidence_count}"
                ),
            )

        # Check quality
        if strong_count < requirements.min_strong:
            return CommitmentCheckResult(
                result=CommitmentResult.INSUFFICIENT_QUALITY,
                level=target_level,
                evidence_count=evidence_count,
                strong_count=strong_count,
                unaddressed_counter_count=len(unaddressed_counter),
                trail_supports=trail_supports,
                message=(
                    f"Need {requirements.min_strong} strong evidence, "
                    f"have {strong_count}"
                ),
            )

        # Check counterevidence
        if not requirements.allow_unaddressed_counter and unaddressed_counter:
            return CommitmentCheckResult(
                result=CommitmentResult.UNADDRESSED_COUNTEREVIDENCE,
                level=target_level,
                evidence_count=evidence_count,
                strong_count=strong_count,
                unaddressed_counter_count=len(unaddressed_counter),
                trail_supports=trail_supports,
                message=(
                    f"{len(unaddressed_counter)} unaddressed counterevidence items"
                ),
            )

        # Check trail support
        if requirements.require_trail and not trail_supports:
            return CommitmentCheckResult(
                result=CommitmentResult.TRAIL_DOES_NOT_SUPPORT,
                level=target_level,
                evidence_count=evidence_count,
                strong_count=strong_count,
                unaddressed_counter_count=len(unaddressed_counter),
                trail_supports=trail_supports,
                message="Exploration trail does not support this claim",
            )

        # All checks passed
        return CommitmentCheckResult(
            result=CommitmentResult.APPROVED,
            level=target_level,
            evidence_count=evidence_count,
            strong_count=strong_count,
            unaddressed_counter_count=len(unaddressed_counter),
            trail_supports=trail_supports,
            message=f"Claim can be committed at {target_level.value} level",
        )

    def commit(
        self,
        claim: Claim,
        level: CommitmentLevel,
        trail: Trail,
        evidence: list[Evidence],
        counterevidence: list[Counterevidence] | None = None,
    ) -> CommitmentCheckResult:
        """
        Attempt to commit a claim at the given level.

        If approved, records the commitment (irreversible).
        Cannot downgrade an existing commitment.
        """
        # Check if already committed at higher level
        existing = self._committed.get(claim.id)
        if existing is not None:
            level_order = [
                CommitmentLevel.TENTATIVE,
                CommitmentLevel.MODERATE,
                CommitmentLevel.STRONG,
                CommitmentLevel.DEFINITIVE,
            ]
            if level_order.index(level) < level_order.index(existing):
                return CommitmentCheckResult(
                    result=CommitmentResult.TRAIL_DOES_NOT_SUPPORT,
                    level=level,
                    evidence_count=len(evidence),
                    strong_count=sum(
                        1 for e in evidence if e.strength == EvidenceStrength.STRONG
                    ),
                    unaddressed_counter_count=len(
                        [c for c in (counterevidence or []) if not c.addressed]
                    ),
                    trail_supports=False,
                    message=f"Cannot downgrade from {existing.value} to {level.value}",
                )

        # Check if can commit
        result = self.can_commit(claim, trail, evidence, counterevidence, level)

        # Record if approved
        if result.approved:
            self._committed[claim.id] = level

        return result

    def max_achievable_level(
        self,
        evidence: list[Evidence],
        counterevidence: list[Counterevidence] | None = None,
        has_trail: bool = True,
    ) -> CommitmentLevel:
        """
        Determine the maximum commitment level achievable with given evidence.

        Useful for showing agents what level they could reach.
        """
        counterevidence = counterevidence or []
        evidence_count = len(evidence)
        strong_count = sum(
            1 for e in evidence if e.strength == EvidenceStrength.STRONG
        )
        has_unaddressed = any(not c.addressed for c in counterevidence)

        # Check from highest to lowest
        if (
            evidence_count >= self.min_evidence_for_definitive
            and strong_count >= self.min_strong_for_definitive
            and not has_unaddressed
            and has_trail
        ):
            return CommitmentLevel.DEFINITIVE

        if (
            evidence_count >= self.min_evidence_for_strong
            and strong_count >= self.min_strong_for_strong
            and not has_unaddressed
            and has_trail
        ):
            return CommitmentLevel.STRONG

        if (
            evidence_count >= self.min_evidence_for_moderate
            and strong_count >= self.min_strong_for_moderate
            and has_trail
        ):
            return CommitmentLevel.MODERATE

        if evidence_count >= self.min_evidence_for_tentative:
            return CommitmentLevel.TENTATIVE

        # Can't commit at any level
        return CommitmentLevel.TENTATIVE

    def _trail_supports_claim(
        self,
        trail: Trail,
        claim: Claim,
        evidence: list[Evidence],
    ) -> bool:
        """
        Check if the trail supports the claim.

        Trail supports if:
        1. At least one evidence item came from a visited node
        2. The trail has meaningful length (not just start node)
        """
        if len(trail.steps) < 2:
            return False

        visited = trail.nodes_visited

        # Check if any evidence came from visited nodes
        for e in evidence:
            node_path = e.metadata.get("node_path", "")
            if node_path in visited:
                return True

        # Check if trail ID is in evidence metadata
        for e in evidence:
            if e.metadata.get("trail_id") == trail.id:
                return True

        return False


__all__ = [
    "ASHCCommitment",
    "CommitmentRequirements",
    "CommitmentCheckResult",
]
