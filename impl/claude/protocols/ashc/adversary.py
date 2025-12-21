"""
ASHC Adversarial Accountability

The implicit counterparty taking the other side of ASHC's bets.

From Kent: "there should implicitly be another person taking the other
'side' of the ASHC compiler's 'bets'."

The adversary doesn't need to be a real entity—it's a mechanism
that ensures ASHC pays when wrong. The adversary "wins" whenever
ASHC's confident prediction fails.

This creates skin in the game: ASHC can't just claim high confidence
without consequence. The payout to the adversary is proportional to
the confidence claim—higher confidence + failure = bigger loss.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from .economy import ASHCBet, ASHCCredibility

# =============================================================================
# BetSettlement: Resolution of a Single Bet
# =============================================================================


@dataclass(frozen=True)
class BetSettlement:
    """
    The settlement of a bet after outcome is known.

    Records who won, how much was paid out, and the credibility impact.
    """

    bet_id: str
    winner: str  # "ashc" or "adversary"
    payout: Decimal  # Amount transferred (0 if ASHC won)
    credibility_delta: float  # Change in ASHC credibility
    settled_at: datetime = field(default_factory=datetime.now)

    @property
    def ashc_won(self) -> bool:
        """Did ASHC win this bet?"""
        return self.winner == "ashc"

    @property
    def was_expensive(self) -> bool:
        """Was this a significant loss for ASHC?"""
        return self.payout > Decimal("0.05") or self.credibility_delta < -0.1


# =============================================================================
# AdversarialAccountability: The Counterparty
# =============================================================================


@dataclass
class AdversarialAccountability:
    """
    The implicit adversary taking the other side of ASHC bets.

    Philosophical grounding (Taleb):
    - You can't have skin in the game without someone on the other side
    - The adversary ensures that confidence claims have consequences
    - High confidence + failure = the adversary wins big

    Mechanism:
    - On success: ASHC keeps stake, adversary gets nothing
    - On failure: Adversary receives stake × confidence
    - On bullshit (high-confidence failure): Adversary wins maximum

    The adversary's winnings are a measure of ASHC's overconfidence.
    If the adversary is getting rich, ASHC is bullshitting.
    """

    adversary_winnings: Decimal = Decimal("0")
    bets_settled: int = 0
    ashc_wins: int = 0
    adversary_wins: int = 0

    def settle_bet(
        self,
        bet: ASHCBet,
        credibility: ASHCCredibility,
    ) -> BetSettlement:
        """
        Settle a bet after outcome is known.

        Payout calculation:
        - If ASHC was right: payout = 0 (ASHC keeps stake)
        - If ASHC was wrong: payout = stake × confidence
          (Higher confidence = bigger loss when wrong)

        The credibility impact is computed from the bet's calibration error.
        """
        if not bet.resolved:
            raise ValueError("Cannot settle unresolved bet")

        self.bets_settled += 1

        if bet.actual_success:
            # ASHC wins: keep stake, no payout to adversary
            self.ashc_wins += 1
            payout = Decimal("0")
            winner = "ashc"

            # Credibility gain from success
            credibility_delta = ASHCCredibility.SUCCESS_RECOVERY
            if bet.is_well_calibrated:
                credibility_delta += ASHCCredibility.CALIBRATED_BONUS

        else:
            # Adversary wins: take stake proportional to confidence
            self.adversary_wins += 1
            winner = "adversary"

            # Payout proportional to confidence (overconfidence costs more)
            payout = bet.stake * Decimal(str(bet.confidence))
            self.adversary_winnings += payout

            # Credibility loss from failure
            credibility_delta = -bet.calibration_error * ASHCCredibility.CALIBRATION_PENALTY
            if bet.was_bullshit:
                credibility_delta -= ASHCCredibility.BULLSHIT_PENALTY

        return BetSettlement(
            bet_id=bet.bet_id,
            winner=winner,
            payout=payout,
            credibility_delta=credibility_delta,
        )

    @property
    def adversary_win_rate(self) -> float:
        """What fraction of bets did the adversary win?"""
        if self.bets_settled == 0:
            return 0.0
        return self.adversary_wins / self.bets_settled

    @property
    def average_payout(self) -> Decimal:
        """Average payout per adversary win."""
        if self.adversary_wins == 0:
            return Decimal("0")
        return self.adversary_winnings / self.adversary_wins

    @property
    def ashc_is_profitable(self) -> bool:
        """Is ASHC winning more than losing?"""
        return self.ashc_wins > self.adversary_wins

    def reset(self) -> None:
        """Reset adversary state (for testing or new epoch)."""
        self.adversary_winnings = Decimal("0")
        self.bets_settled = 0
        self.ashc_wins = 0
        self.adversary_wins = 0


# =============================================================================
# Convenience Functions
# =============================================================================


def create_settlement_report(
    settlements: list[BetSettlement],
) -> dict[str, object]:
    """
    Create a summary report of bet settlements.

    Useful for logging and analysis.
    """
    if not settlements:
        return {
            "total_bets": 0,
            "ashc_wins": 0,
            "adversary_wins": 0,
            "total_payout": Decimal("0"),
            "average_credibility_delta": 0.0,
        }

    ashc_wins = sum(1 for s in settlements if s.ashc_won)
    adversary_wins = len(settlements) - ashc_wins
    total_payout = sum(s.payout for s in settlements)
    avg_credibility = sum(s.credibility_delta for s in settlements) / len(settlements)

    return {
        "total_bets": len(settlements),
        "ashc_wins": ashc_wins,
        "adversary_wins": adversary_wins,
        "total_payout": total_payout,
        "average_credibility_delta": avg_credibility,
        "expensive_losses": sum(1 for s in settlements if s.was_expensive),
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AdversarialAccountability",
    "BetSettlement",
    "create_settlement_report",
]
