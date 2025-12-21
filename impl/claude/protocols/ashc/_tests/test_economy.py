"""
Tests for ASHC Economic Accountability Layer

Tests the betting, credibility, adversary, and causal penalty systems.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ..adversary import AdversarialAccountability, BetSettlement, create_settlement_report
from ..causal_penalty import CausalPenalty, PrincipleCredibility, PrincipleRegistry
from ..economy import AllocationStrategy, ASHCBet, ASHCCredibility, ASHCEconomy

# =============================================================================
# Test ASHCBet
# =============================================================================


class TestASHCBet:
    """Tests for ASHCBet wager type."""

    def test_create_bet(self) -> None:
        """Create a basic bet."""
        bet = ASHCBet.create(
            spec="def foo(): pass",
            confidence=0.9,
            stake=Decimal("0.10"),
            principles=("composable", "tasteful"),
        )

        assert bet.bet_id.startswith("bet_")
        assert bet.confidence == 0.9
        assert bet.stake == Decimal("0.10")
        assert "composable" in bet.principles_cited
        assert not bet.resolved
        assert bet.actual_success is None

    def test_resolve_success(self) -> None:
        """Resolve a bet as success."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))
        resolved = bet.resolve(success=True)

        assert resolved.resolved
        assert resolved.actual_success is True
        assert resolved.resolved_at is not None

    def test_resolve_failure(self) -> None:
        """Resolve a bet as failure."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        assert resolved.resolved
        assert resolved.actual_success is False

    def test_was_bullshit_high_confidence_failure(self) -> None:
        """High confidence + failure = bullshit."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.9, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        assert resolved.was_bullshit
        assert resolved.calibration_error == pytest.approx(0.9, abs=0.01)

    def test_was_bullshit_low_confidence_failure(self) -> None:
        """Low confidence + failure is NOT bullshit (honest uncertainty)."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.5, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        assert not resolved.was_bullshit
        assert resolved.calibration_error == pytest.approx(0.5, abs=0.01)

    def test_was_bullshit_high_confidence_success(self) -> None:
        """High confidence + success is NOT bullshit."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.9, stake=Decimal("0.05"))
        resolved = bet.resolve(success=True)

        assert not resolved.was_bullshit
        assert resolved.calibration_error == pytest.approx(0.1, abs=0.01)

    def test_calibration_error_perfect(self) -> None:
        """Perfect calibration: 100% confidence + success."""
        bet = ASHCBet.create(spec="x = 1", confidence=1.0, stake=Decimal("0.05"))
        resolved = bet.resolve(success=True)

        assert resolved.calibration_error == pytest.approx(0.0, abs=0.01)
        assert resolved.is_well_calibrated

    def test_calibration_error_worst(self) -> None:
        """Worst calibration: 100% confidence + failure."""
        bet = ASHCBet.create(spec="x = 1", confidence=1.0, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        assert resolved.calibration_error == pytest.approx(1.0, abs=0.01)
        assert not resolved.is_well_calibrated


# =============================================================================
# Test ASHCCredibility
# =============================================================================


class TestASHCCredibility:
    """Tests for ASHCCredibility debt meter."""

    def test_initial_state(self) -> None:
        """Credibility starts at 1.0 (fully trusted)."""
        cred = ASHCCredibility()

        assert cred.credibility == 1.0
        assert cred.total_bets == 0
        assert not cred.is_bankrupt

    def test_success_increases_credibility(self) -> None:
        """Successful predictions earn credibility."""
        cred = ASHCCredibility(credibility=0.5)
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))
        resolved = bet.resolve(success=True)

        cred.record_outcome(resolved)

        assert cred.credibility > 0.5
        assert cred.successful_bets == 1

    def test_failure_decreases_credibility(self) -> None:
        """Failed predictions lose credibility."""
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        cred.record_outcome(resolved)

        assert cred.credibility < 1.0

    def test_bullshit_penalty_severe(self) -> None:
        """Bullshit (high-confidence failure) is severely penalized."""
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.95, stake=Decimal("0.05"))
        resolved = bet.resolve(success=False)

        cred.record_outcome(resolved)

        # Should lose at least BULLSHIT_PENALTY (0.15)
        assert cred.credibility < 0.85
        assert cred.bullshit_count == 1

    def test_calibration_bonus(self) -> None:
        """Well-calibrated predictions get bonus recovery."""
        cred = ASHCCredibility(credibility=0.5)
        # 95% confidence, success -> 0.05 calibration error (well-calibrated)
        bet = ASHCBet.create(spec="x = 1", confidence=0.95, stake=Decimal("0.05"))
        resolved = bet.resolve(success=True)

        cred.record_outcome(resolved)

        # Should get SUCCESS_RECOVERY + CALIBRATED_BONUS
        expected = 0.5 + ASHCCredibility.SUCCESS_RECOVERY + ASHCCredibility.CALIBRATED_BONUS
        assert cred.credibility == pytest.approx(expected, abs=0.01)

    def test_bankruptcy(self) -> None:
        """Repeated bullshit leads to bankruptcy."""
        cred = ASHCCredibility()

        # 10 bullshit predictions
        for _ in range(10):
            bet = ASHCBet.create(spec="x = 1", confidence=0.95, stake=Decimal("0.01"))
            resolved = bet.resolve(success=False)
            cred.record_outcome(resolved)

        assert cred.is_bankrupt
        assert cred.credibility == 0.0

    def test_confidence_multiplier(self) -> None:
        """Credibility bounds future confidence claims."""
        cred = ASHCCredibility(credibility=0.5)

        assert cred.confidence_multiplier() == 0.5

    def test_bets_to_recover(self) -> None:
        """Calculate how many successes needed to recover."""
        cred = ASHCCredibility(credibility=0.5)

        bets_needed = cred.bets_to_recover()

        # Need to recover 0.5 at ~0.03 per success
        assert bets_needed > 15

    def test_unresolved_bet_raises(self) -> None:
        """Recording unresolved bet raises error."""
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))

        with pytest.raises(ValueError, match="unresolved"):
            cred.record_outcome(bet)

    def test_asymmetry_recovery_is_slow(self) -> None:
        """Verify asymmetry: recovery is slower than loss."""
        # One bullshit costs ~0.15 + calibration penalty
        # One success earns ~0.02-0.03
        # So ~5-8 successes needed per bullshit

        recovery_per_success = ASHCCredibility.SUCCESS_RECOVERY + ASHCCredibility.CALIBRATED_BONUS
        bullshit_cost = ASHCCredibility.BULLSHIT_PENALTY

        ratio = bullshit_cost / recovery_per_success
        assert ratio > 4  # At least 4 successes per bullshit


# =============================================================================
# Test ASHCEconomy
# =============================================================================


class TestASHCEconomy:
    """Tests for ASHCEconomy resource allocation."""

    def test_initial_budget(self) -> None:
        """Economy tracks budget correctly."""
        economy = ASHCEconomy(total_budget=Decimal("1.00"))

        assert economy.remaining == Decimal("1.00")
        assert economy.spent == Decimal("0")

    def test_spend_success(self) -> None:
        """Spending within budget succeeds."""
        economy = ASHCEconomy(total_budget=Decimal("1.00"))

        assert economy.spend(Decimal("0.50"))
        assert economy.remaining == Decimal("0.50")
        assert economy.spent == Decimal("0.50")

    def test_spend_insufficient(self) -> None:
        """Spending beyond budget fails."""
        economy = ASHCEconomy(total_budget=Decimal("1.00"))

        assert not economy.spend(Decimal("1.50"))
        assert economy.remaining == Decimal("1.00")

    def test_can_afford(self) -> None:
        """Check affordability."""
        economy = ASHCEconomy(total_budget=Decimal("1.00"))

        assert economy.can_afford(Decimal("0.50"))
        assert economy.can_afford(Decimal("1.00"))
        assert not economy.can_afford(Decimal("1.01"))

    def test_optimal_allocation_high_confidence(self) -> None:
        """High confidence = few samples needed."""
        from ..adaptive import BetaPrior

        economy = ASHCEconomy(total_budget=Decimal("1.00"))
        cred = ASHCCredibility(credibility=1.0)
        prior = BetaPrior(alpha=20, beta=1)  # Strong prior (~0.95)

        strategy = economy.optimal_allocation(prior, cred)

        assert strategy.expected_samples < 5
        assert strategy.can_proceed
        assert strategy.effective_confidence > 0.9

    def test_optimal_allocation_low_confidence(self) -> None:
        """Low confidence = more samples needed."""
        from ..adaptive import BetaPrior

        economy = ASHCEconomy(total_budget=Decimal("1.00"))
        cred = ASHCCredibility(credibility=1.0)
        prior = BetaPrior(alpha=3, beta=2)  # Moderate prior (~0.6)

        strategy = economy.optimal_allocation(prior, cred)

        assert strategy.expected_samples > 5
        assert strategy.can_proceed

    def test_optimal_allocation_credibility_discount(self) -> None:
        """Low credibility discounts effective confidence."""
        from ..adaptive import BetaPrior

        economy = ASHCEconomy(total_budget=Decimal("1.00"))
        cred = ASHCCredibility(credibility=0.5)
        prior = BetaPrior(alpha=20, beta=1)  # Strong prior (~0.95)

        strategy = economy.optimal_allocation(prior, cred)

        # Effective confidence = 0.95 * 0.5 ≈ 0.475
        assert strategy.effective_confidence < 0.5

    def test_stake_for_confidence(self) -> None:
        """Higher confidence = higher stake."""
        economy = ASHCEconomy(total_budget=Decimal("1.00"))

        stake_low = economy.stake_for_confidence(0.5)
        stake_high = economy.stake_for_confidence(0.9)

        assert stake_high > stake_low


# =============================================================================
# Test AdversarialAccountability
# =============================================================================


class TestAdversarialAccountability:
    """Tests for the implicit adversary."""

    def test_settle_success(self) -> None:
        """On success, ASHC wins, adversary gets nothing."""
        adversary = AdversarialAccountability()
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.9, stake=Decimal("0.10"))
        resolved = bet.resolve(success=True)

        settlement = adversary.settle_bet(resolved, cred)

        assert settlement.winner == "ashc"
        assert settlement.payout == Decimal("0")
        assert adversary.ashc_wins == 1
        assert adversary.adversary_winnings == Decimal("0")

    def test_settle_failure(self) -> None:
        """On failure, adversary wins stake × confidence."""
        adversary = AdversarialAccountability()
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.10"))
        resolved = bet.resolve(success=False)

        settlement = adversary.settle_bet(resolved, cred)

        assert settlement.winner == "adversary"
        # Payout = stake × confidence = 0.10 × 0.8 = 0.08
        assert settlement.payout == Decimal("0.08")
        assert adversary.adversary_wins == 1
        assert adversary.adversary_winnings == Decimal("0.08")

    def test_high_confidence_failure_expensive(self) -> None:
        """High confidence failure costs more."""
        adversary = AdversarialAccountability()
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.95, stake=Decimal("0.10"))
        resolved = bet.resolve(success=False)

        settlement = adversary.settle_bet(resolved, cred)

        # Payout = stake × confidence = 0.10 × 0.95 = 0.095
        assert settlement.payout == Decimal("0.095")
        assert settlement.was_expensive

    def test_adversary_win_rate(self) -> None:
        """Track adversary win rate."""
        adversary = AdversarialAccountability()
        cred = ASHCCredibility()

        # 3 wins, 2 losses
        for i in range(5):
            bet = ASHCBet.create(spec=f"x = {i}", confidence=0.8, stake=Decimal("0.01"))
            resolved = bet.resolve(success=(i < 3))
            adversary.settle_bet(resolved, cred)

        assert adversary.adversary_win_rate == pytest.approx(0.4, abs=0.01)

    def test_unresolved_bet_raises(self) -> None:
        """Settling unresolved bet raises error."""
        adversary = AdversarialAccountability()
        cred = ASHCCredibility()
        bet = ASHCBet.create(spec="x = 1", confidence=0.8, stake=Decimal("0.05"))

        with pytest.raises(ValueError, match="unresolved"):
            adversary.settle_bet(bet, cred)


# =============================================================================
# Test CausalPenalty
# =============================================================================


class TestCausalPenalty:
    """Tests for causal penalty propagation."""

    def test_from_failed_bet(self) -> None:
        """Create penalty from failed bet."""
        bet = ASHCBet.create(
            spec="x = 1",
            confidence=0.9,
            stake=Decimal("0.10"),
            principles=("composable", "tasteful"),
            evidence=("run_abc", "run_def"),
        )
        resolved = bet.resolve(success=False)

        penalty = CausalPenalty.from_bet(resolved, penalty_amount=0.15)

        assert penalty.bet_id == resolved.bet_id
        assert penalty.penalty_amount == 0.15
        assert "composable" in penalty.principles_penalized
        assert "run_abc" in penalty.evidence_penalized

    def test_equal_blame_distribution(self) -> None:
        """Default: equal blame distribution."""
        bet = ASHCBet.create(
            spec="x = 1",
            confidence=0.9,
            stake=Decimal("0.10"),
            principles=("composable", "tasteful", "ethical"),
        )
        resolved = bet.resolve(success=False)

        penalty = CausalPenalty.from_bet(resolved, penalty_amount=0.30)

        # Each principle gets 1/3 of the blame
        assert penalty.blame_for_principle("composable") == pytest.approx(0.10, abs=0.01)
        assert penalty.blame_for_principle("tasteful") == pytest.approx(0.10, abs=0.01)

    def test_custom_weights(self) -> None:
        """Custom blame weights."""
        bet = ASHCBet.create(
            spec="x = 1",
            confidence=0.9,
            stake=Decimal("0.10"),
            principles=("composable", "tasteful"),
        )
        resolved = bet.resolve(success=False)

        penalty = CausalPenalty.from_bet(
            resolved,
            penalty_amount=0.20,
            principle_weights={"composable": 0.8, "tasteful": 0.2},
        )

        assert penalty.blame_for_principle("composable") == pytest.approx(0.16, abs=0.01)
        assert penalty.blame_for_principle("tasteful") == pytest.approx(0.04, abs=0.01)

    def test_success_bet_raises(self) -> None:
        """Cannot create penalty from successful bet."""
        bet = ASHCBet.create(spec="x = 1", confidence=0.9, stake=Decimal("0.10"))
        resolved = bet.resolve(success=True)

        with pytest.raises(ValueError):
            CausalPenalty.from_bet(resolved, penalty_amount=0.15)


# =============================================================================
# Test PrincipleCredibility
# =============================================================================


class TestPrincipleCredibility:
    """Tests for per-principle trust tracking."""

    def test_initial_state(self) -> None:
        """Principles start trusted."""
        principle = PrincipleCredibility(principle_id="composable")

        assert principle.credibility == 1.0
        assert principle.times_cited == 0
        assert principle.times_blamed == 0

    def test_cite(self) -> None:
        """Record citation."""
        principle = PrincipleCredibility(principle_id="composable")

        principle.cite()
        principle.cite()

        assert principle.times_cited == 2

    def test_blame(self) -> None:
        """Blame reduces credibility."""
        principle = PrincipleCredibility(principle_id="composable")

        principle.blame(0.2)

        assert principle.credibility == pytest.approx(0.8, abs=0.01)
        assert principle.times_blamed == 1

    def test_reward(self) -> None:
        """Reward increases credibility."""
        principle = PrincipleCredibility(principle_id="composable", credibility=0.5)

        principle.reward(0.1)

        assert principle.credibility == pytest.approx(0.6, abs=0.01)

    def test_discredited(self) -> None:
        """Principle becomes discredited at zero credibility."""
        principle = PrincipleCredibility(principle_id="bad_principle")

        for _ in range(10):
            principle.blame(0.15)

        assert principle.is_discredited
        assert principle.credibility == 0.0

    def test_is_predictive(self) -> None:
        """Principle is predictive if cited often with low blame rate."""
        principle = PrincipleCredibility(principle_id="good_principle")

        # 10 citations, 1 blame
        for _ in range(10):
            principle.cite()
        principle.blame(0.05)

        assert principle.is_predictive
        assert principle.blame_rate == pytest.approx(0.1, abs=0.01)


# =============================================================================
# Test PrincipleRegistry
# =============================================================================


class TestPrincipleRegistry:
    """Tests for principle registry."""

    def test_get_or_create(self) -> None:
        """Get or create principles."""
        registry = PrincipleRegistry()

        p1 = registry.get_or_create("composable")
        p2 = registry.get_or_create("composable")

        assert p1 is p2

    def test_apply_penalty(self) -> None:
        """Apply penalty to all cited principles."""
        registry = PrincipleRegistry()
        bet = ASHCBet.create(
            spec="x = 1",
            confidence=0.9,
            stake=Decimal("0.10"),
            principles=("composable", "tasteful"),
        )
        resolved = bet.resolve(success=False)
        penalty = CausalPenalty.from_bet(resolved, penalty_amount=0.20)

        registry.apply_penalty(penalty)

        assert registry.get_or_create("composable").credibility < 1.0
        assert registry.get_or_create("tasteful").credibility < 1.0

    def test_credibility_ranking(self) -> None:
        """Get principles ranked by credibility."""
        registry = PrincipleRegistry()

        registry.get_or_create("good").credibility = 0.9
        registry.get_or_create("bad").credibility = 0.3
        registry.get_or_create("medium").credibility = 0.6

        ranking = registry.credibility_ranking()

        assert ranking[0][0] == "good"
        assert ranking[-1][0] == "bad"

    def test_effective_weight(self) -> None:
        """Effective weight reflects credibility."""
        registry = PrincipleRegistry()
        registry.get_or_create("low_cred").credibility = 0.3

        assert registry.effective_weight("low_cred") == 0.3
        assert registry.effective_weight("new_principle") == 1.0


# =============================================================================
# Test Settlement Report
# =============================================================================


class TestSettlementReport:
    """Tests for settlement report generation."""

    def test_empty_report(self) -> None:
        """Empty settlement list."""
        report = create_settlement_report([])

        assert report["total_bets"] == 0

    def test_mixed_report(self) -> None:
        """Report with mixed outcomes."""
        settlements = [
            BetSettlement(bet_id="1", winner="ashc", payout=Decimal("0"), credibility_delta=0.02),
            BetSettlement(
                bet_id="2", winner="adversary", payout=Decimal("0.10"), credibility_delta=-0.15
            ),
            BetSettlement(bet_id="3", winner="ashc", payout=Decimal("0"), credibility_delta=0.02),
        ]

        report = create_settlement_report(settlements)

        assert report["total_bets"] == 3
        assert report["ashc_wins"] == 2
        assert report["adversary_wins"] == 1
        assert report["total_payout"] == Decimal("0.10")
