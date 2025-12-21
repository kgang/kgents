"""
ASHC Economic Accountability Layer

ASHC becomes a betting agent with skin in the game:
- Stakes resources on P(success)
- Accumulates credibility debt when confident predictions fail
- Tracks causal attribution for blame propagation

From Kent: "If ASHC produces confident garbage, the penalty propagates
up to Kent's reputation as developer."

Heritage: Prediction Markets, Skin in the Game (Taleb), ConsentState.debt pattern
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import ClassVar

from .adaptive import BetaPrior, expected_samples_for_ndiff

# =============================================================================
# ASHCBet: A Wager on Compilation Outcome
# =============================================================================


@dataclass(frozen=True)
class ASHCBet:
    """
    A wager ASHC places on a compilation outcome.

    ASHC claims confidence P(success) and stakes resources.
    If wrong, the adversary wins. If high-confidence + wrong,
    it's bullshit and the penalty is severe.
    """

    bet_id: str
    spec_hash: str

    # The wager
    confidence: float  # P(success) claimed (0.0-1.0)
    stake: Decimal  # Resources wagered (tokens, dollars)

    # Causal attribution: what led to this confidence?
    principles_cited: tuple[str, ...] = ()  # Which principles informed this
    evidence_cited: tuple[str, ...] = ()  # Which prior runs informed this
    reasoning_trace: tuple[str, ...] = ()  # Chain of reasoning

    # Timing
    created_at: datetime = field(default_factory=datetime.now)

    # Outcome (filled after resolution)
    resolved: bool = False
    actual_success: bool | None = None
    resolved_at: datetime | None = None

    @property
    def was_bullshit(self) -> bool:
        """
        High confidence + failure = bullshit.

        This is the most expensive outcome: ASHC claimed certainty
        but was wrong. The adversary wins big.
        """
        if not self.resolved or self.actual_success is None:
            return False
        return self.confidence >= 0.8 and not self.actual_success

    @property
    def calibration_error(self) -> float:
        """
        How far off was the confidence from reality?

        0.0 = perfectly calibrated
        1.0 = maximally wrong (100% confident + opposite outcome)
        """
        if not self.resolved or self.actual_success is None:
            return 0.0
        actual = 1.0 if self.actual_success else 0.0
        return abs(self.confidence - actual)

    @property
    def is_well_calibrated(self) -> bool:
        """Was the confidence within 10% of actual outcome?"""
        return self.calibration_error < 0.1

    def resolve(self, success: bool) -> "ASHCBet":
        """Create a resolved copy of this bet."""
        return ASHCBet(
            bet_id=self.bet_id,
            spec_hash=self.spec_hash,
            confidence=self.confidence,
            stake=self.stake,
            principles_cited=self.principles_cited,
            evidence_cited=self.evidence_cited,
            reasoning_trace=self.reasoning_trace,
            created_at=self.created_at,
            resolved=True,
            actual_success=success,
            resolved_at=datetime.now(),
        )

    @classmethod
    def create(
        cls,
        spec: str,
        confidence: float,
        stake: Decimal,
        principles: tuple[str, ...] = (),
        evidence: tuple[str, ...] = (),
        reasoning: tuple[str, ...] = (),
    ) -> "ASHCBet":
        """Create a new bet on a spec."""
        spec_hash = hashlib.sha256(spec.encode()).hexdigest()[:16]
        bet_id = f"bet_{uuid.uuid4().hex[:8]}"
        return cls(
            bet_id=bet_id,
            spec_hash=spec_hash,
            confidence=confidence,
            stake=stake,
            principles_cited=principles,
            evidence_cited=evidence,
            reasoning_trace=reasoning,
        )


# =============================================================================
# ASHCCredibility: The Debt Meter
# =============================================================================


@dataclass
class ASHCCredibility:
    """
    ASHC's credibility score.

    Mirrors ConsentState.debt but inverted:
    - Starts at 1.0 (fully trusted)
    - Erodes with bullshit (high-confidence failures)
    - Recovers ONLY through successful predictions (no time decay)
    - At 0.0 = bankrupt (ASHC refuses to operate)

    Recovery is success-based: you must earn it back through
    accurate predictions. No passive time decay.

    Asymmetry (from Taleb): Losing is fast, recovery is slow.
    - One bullshit: -0.15 credibility
    - One success: +0.02 credibility
    - Recovery cost: ~8 successes to recover from one bullshit
    """

    credibility: float = 1.0  # 1.0 = trusted, 0.0 = bankrupt
    total_bets: int = 0
    successful_bets: int = 0
    bullshit_count: int = 0  # High-confidence failures
    calibration_sum: float = 0.0  # Sum of calibration errors

    # Penalty/recovery rates (class variables for easy tuning)
    BULLSHIT_PENALTY: ClassVar[float] = 0.15  # High-confidence failure
    CALIBRATION_PENALTY: ClassVar[float] = 0.05  # Per unit calibration error
    SUCCESS_RECOVERY: ClassVar[float] = 0.02  # Earned per successful prediction
    CALIBRATED_BONUS: ClassVar[float] = 0.01  # Bonus for well-calibrated prediction

    def record_outcome(self, bet: ASHCBet) -> None:
        """
        Update credibility based on bet outcome.

        Success earns credibility back.
        Failure loses credibility.
        Bullshit (high-confidence failure) is catastrophic.
        """
        if not bet.resolved:
            raise ValueError("Cannot record outcome of unresolved bet")

        self.total_bets += 1
        self.calibration_sum += bet.calibration_error

        if bet.actual_success:
            # SUCCESS: earn back credibility
            self.successful_bets += 1
            self.credibility += self.SUCCESS_RECOVERY

            # Bonus for being well-calibrated (confidence matched reality)
            if bet.is_well_calibrated:
                self.credibility += self.CALIBRATED_BONUS
        else:
            # FAILURE: lose credibility
            if bet.was_bullshit:
                # Bullshit is expensive
                self.bullshit_count += 1
                self.credibility -= self.BULLSHIT_PENALTY

            # Calibration penalty (proportional to overconfidence)
            self.credibility -= bet.calibration_error * self.CALIBRATION_PENALTY

        # Clamp to [0, 1]
        self.credibility = max(0.0, min(1.0, self.credibility))

    def confidence_multiplier(self) -> float:
        """
        Discount future confidence claims by current credibility.

        If ASHC has been bullshitting, its future confidence claims
        are automatically discounted.

        Example: If credibility = 0.7, a 90% confidence claim
        becomes 63% effective confidence (0.9 * 0.7).
        """
        return self.credibility

    @property
    def is_bankrupt(self) -> bool:
        """At zero credibility, ASHC should refuse to operate."""
        return self.credibility <= 0.0

    @property
    def average_calibration_error(self) -> float:
        """How well-calibrated is ASHC on average?"""
        if self.total_bets == 0:
            return 0.0
        return self.calibration_sum / self.total_bets

    @property
    def bullshit_rate(self) -> float:
        """What fraction of bets were bullshit?"""
        if self.total_bets == 0:
            return 0.0
        return self.bullshit_count / self.total_bets

    @property
    def success_rate(self) -> float:
        """What fraction of bets succeeded?"""
        if self.total_bets == 0:
            return 0.0
        return self.successful_bets / self.total_bets

    def bets_to_recover(self) -> int:
        """
        How many successful bets needed to reach full credibility?

        This shows the asymmetry: bullshit is expensive to recover from.
        """
        if self.credibility >= 1.0:
            return 0
        deficit = 1.0 - self.credibility
        # Assume well-calibrated successes (get bonus)
        recovery_per_bet = self.SUCCESS_RECOVERY + self.CALIBRATED_BONUS
        return int(deficit / recovery_per_bet) + 1


# =============================================================================
# AllocationStrategy: Resource Allocation Decision
# =============================================================================


@dataclass(frozen=True)
class AllocationStrategy:
    """
    Computed allocation strategy for a compilation.

    Based on prior belief, current credibility, and available budget.
    """

    expected_samples: int  # How many runs we expect to need
    estimated_cost: Decimal  # Estimated total cost
    effective_confidence: float  # Prior × credibility multiplier
    can_proceed: bool  # True if budget allows


# =============================================================================
# ASHCEconomy: Cost-Aware Resource Allocation
# =============================================================================


@dataclass
class ASHCEconomy:
    """
    Economic layer for ASHC: cost-aware resource allocation.

    Integrates prior beliefs, credibility, and budget constraints
    to compute optimal allocation strategies.
    """

    total_budget: Decimal
    spent: Decimal = Decimal("0")

    # Per-operation costs (configurable)
    LLM_CALL_COST: ClassVar[Decimal] = Decimal("0.01")
    VERIFICATION_COST: ClassVar[Decimal] = Decimal("0.001")

    @property
    def remaining(self) -> Decimal:
        """Remaining budget."""
        return self.total_budget - self.spent

    def can_afford(self, cost: Decimal) -> bool:
        """Check if budget allows this cost."""
        return cost <= self.remaining

    def spend(self, amount: Decimal) -> bool:
        """
        Spend from budget.

        Returns True if successful, False if insufficient funds.
        """
        if not self.can_afford(amount):
            return False
        self.spent += amount
        return True

    def optimal_allocation(
        self,
        prior: BetaPrior,
        credibility: ASHCCredibility,
        n_diff: int = 2,
    ) -> AllocationStrategy:
        """
        Compute optimal resource allocation.

        Considers:
        - Prior belief about success probability
        - Current credibility (affects confidence claims)
        - Available budget

        Returns strategy with expected samples and cost.
        """
        # Effective confidence = prior mean × credibility multiplier
        effective_confidence = prior.mean * credibility.confidence_multiplier()

        # Handle edge cases
        if effective_confidence <= 0.5:
            # Pure uncertainty or worse - can't converge
            return AllocationStrategy(
                expected_samples=int(self.remaining / self.LLM_CALL_COST),
                estimated_cost=self.remaining,
                effective_confidence=effective_confidence,
                can_proceed=self.remaining > Decimal("0"),
            )

        # Compute expected samples needed (from adaptive.py)
        expected = expected_samples_for_ndiff(effective_confidence, n_diff)

        if expected == float("inf"):
            # Won't converge - use all remaining budget
            samples = int(self.remaining / self.LLM_CALL_COST)
            return AllocationStrategy(
                expected_samples=samples,
                estimated_cost=self.remaining,
                effective_confidence=effective_confidence,
                can_proceed=self.remaining > Decimal("0"),
            )

        expected_samples = max(1, int(expected) + 1)  # Round up

        # Cost estimate
        estimated_cost = self.LLM_CALL_COST * Decimal(str(expected_samples))

        return AllocationStrategy(
            expected_samples=expected_samples,
            estimated_cost=estimated_cost,
            effective_confidence=effective_confidence,
            can_proceed=estimated_cost <= self.remaining,
        )

    def stake_for_confidence(self, confidence: float) -> Decimal:
        """
        Compute stake amount based on confidence.

        Higher confidence = higher stake = more to lose if wrong.
        """
        # Stake is proportional to confidence squared
        # (penalizes overconfidence more)
        stake_fraction = Decimal(str(confidence**2))
        max_stake = self.remaining * Decimal("0.1")  # Max 10% of remaining
        return min(max_stake, stake_fraction * self.LLM_CALL_COST * Decimal("10"))


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ASHCBet",
    "ASHCCredibility",
    "ASHCEconomy",
    "AllocationStrategy",
]
