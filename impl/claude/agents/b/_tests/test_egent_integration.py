"""Tests for B-gent E-gent Integration module."""

import pytest
from datetime import timedelta

from agents.b.egent_integration import (
    # Prediction Market
    BetOutcome,
    PredictionMarket,
    # Grant System (Sun)
    GrantStatus,
    Sun,
    # Staking
    StakingPool,
    # Combined
    create_evolution_economics,
)
from agents.b.metered_functor import CentralBank


# =============================================================================
# Prediction Market Tests
# =============================================================================


class TestPredictionMarket:
    """Tests for PredictionMarket."""

    def test_market_creation(self) -> None:
        """Test creating a prediction market."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        assert market.base_liquidity == 10000
        assert market.min_stake == 10
        assert market.max_stake == 1000

    def test_quote_basic(self) -> None:
        """Test getting a basic quote."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        quote = market.quote("phage_001")

        assert quote.phage_id == "phage_001"
        assert quote.success_odds > 1.0
        assert quote.failure_odds > 1.0
        assert 0.0 < quote.implied_success_probability < 1.0
        assert quote.liquidity > 0

    def test_quote_with_schema_confidence(self) -> None:
        """Test quote adjusts based on schema confidence."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        # High confidence schema should have lower success odds (more likely)
        high_conf_quote = market.quote("phage_001", schema_confidence=0.9)

        # Low confidence schema should have higher success odds (less likely)
        low_conf_quote = market.quote("phage_002", schema_confidence=0.1)

        # Higher confidence → lower odds (more likely to succeed)
        assert high_conf_quote.success_odds < low_conf_quote.success_odds

    def test_quote_with_historical_data(self) -> None:
        """Test quote uses historical success rates."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        # Set historical success rate for a schema
        market.schema_success_rates["schema_good"] = 0.8
        market.schema_success_rates["schema_bad"] = 0.2

        good_quote = market.quote("phage_001", schema_signature="schema_good")
        bad_quote = market.quote("phage_002", schema_signature="schema_bad")

        # Good schema should have better (lower) odds
        assert good_quote.success_odds < bad_quote.success_odds

    @pytest.mark.asyncio
    async def test_place_bet_success(self) -> None:
        """Test placing a bet successfully."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        initial_balance = bank.get_balance()

        bet = await market.place_bet(
            bettor_id="agent_001",
            phage_id="phage_001",
            stake=100,
            predicted_success=True,
        )

        assert bet.bettor_id == "agent_001"
        assert bet.phage_id == "phage_001"
        assert bet.stake == 100
        assert bet.predicted_success is True
        assert bet.outcome == BetOutcome.PENDING

        # Balance should decrease (after tax)
        assert bank.get_balance() < initial_balance

    @pytest.mark.asyncio
    async def test_place_bet_stake_too_low(self) -> None:
        """Test placing a bet with stake below minimum."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank, min_stake=10)

        with pytest.raises(ValueError, match="below minimum"):
            await market.place_bet(
                bettor_id="agent_001",
                phage_id="phage_001",
                stake=5,  # Below minimum
                predicted_success=True,
            )

    @pytest.mark.asyncio
    async def test_place_bet_stake_too_high(self) -> None:
        """Test placing a bet with stake above maximum."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank, max_stake=1000)

        with pytest.raises(ValueError, match="above maximum"):
            await market.place_bet(
                bettor_id="agent_001",
                phage_id="phage_001",
                stake=2000,  # Above maximum
                predicted_success=True,
            )

    @pytest.mark.asyncio
    async def test_settle_winning_bet(self) -> None:
        """Test settling a winning bet."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        bet = await market.place_bet(
            bettor_id="agent_001",
            phage_id="phage_001",
            stake=100,
            predicted_success=True,
        )

        # Mutation succeeds
        results = await market.settle("phage_001", succeeded=True)

        assert len(results) == 1
        result = results[0]
        assert result.bet_id == bet.id
        assert result.outcome == BetOutcome.WON
        assert result.payout > 0
        assert result.winnings > 0  # Won money

    @pytest.mark.asyncio
    async def test_settle_losing_bet(self) -> None:
        """Test settling a losing bet."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        bet = await market.place_bet(
            bettor_id="agent_001",
            phage_id="phage_001",
            stake=100,
            predicted_success=True,
        )

        # Mutation fails
        results = await market.settle("phage_001", succeeded=False)

        assert len(results) == 1
        result = results[0]
        assert result.bet_id == bet.id
        assert result.outcome == BetOutcome.LOST
        assert result.payout == 0
        assert result.winnings == -100  # Lost stake

    @pytest.mark.asyncio
    async def test_multiple_bets_settlement(self) -> None:
        """Test settling multiple bets on same phage."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        # Place multiple bets
        await market.place_bet("agent_001", "phage_001", 100, True)  # Betting success
        await market.place_bet("agent_002", "phage_001", 100, False)  # Betting failure

        # Mutation succeeds
        results = await market.settle("phage_001", succeeded=True)

        assert len(results) == 2

        winners = [r for r in results if r.outcome == BetOutcome.WON]
        losers = [r for r in results if r.outcome == BetOutcome.LOST]

        assert len(winners) == 1
        assert len(losers) == 1

    def test_update_schema_success_rate(self) -> None:
        """Test updating historical success rates."""
        bank = CentralBank(max_balance=100000)
        market = PredictionMarket(bank)

        # Initial rate is 0.5 (default)
        _initial_quote = market.quote(
            "phage_001", schema_signature="schema_test", schema_confidence=0.5
        )

        # Update with success
        market.update_schema_success_rate("schema_test", True)

        # Rate should increase
        assert market.schema_success_rates["schema_test"] > 0.5

        # Update with failure
        market.update_schema_success_rate("schema_test", False)

        # Rate should decrease from previous (but still higher than original 0.5)
        assert market.schema_success_rates["schema_test"] < 0.55


# =============================================================================
# Grant System (Sun) Tests
# =============================================================================


class TestSun:
    """Tests for Sun (Grant System)."""

    def test_sun_creation(self) -> None:
        """Test creating the Sun."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        assert len(sun.grants) == 0

    @pytest.mark.asyncio
    async def test_issue_grant(self) -> None:
        """Test issuing a grant."""
        # Start with lower balance so grant can increase it
        bank = CentralBank(max_balance=100000)
        bank.bucket.balance = 50000  # Half of max
        initial_balance = bank.get_balance()

        sun = Sun(bank)

        grant = await sun.issue_grant(
            grantee_id="agent_001",
            tokens=5000,
            intent_embedding=[0.1] * 64,
            intent_description="Refactor authentication system",
        )

        assert grant.grantee_id == "agent_001"
        assert grant.tokens == 5000
        assert grant.remaining == 5000
        assert grant.status == GrantStatus.ACTIVE
        assert grant.intent_description == "Refactor authentication system"

        # Bank balance should increase (grant adds tokens)
        assert bank.get_balance() == initial_balance + 5000

    @pytest.mark.asyncio
    async def test_has_active_grant(self) -> None:
        """Test checking for active grants."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        assert not sun.has_active_grant("agent_001")

        await sun.issue_grant(
            grantee_id="agent_001",
            tokens=1000,
            intent_embedding=[0.1] * 64,
            intent_description="Test grant",
        )

        assert sun.has_active_grant("agent_001")
        assert not sun.has_active_grant("agent_002")

    @pytest.mark.asyncio
    async def test_get_total_grant_budget(self) -> None:
        """Test getting total grant budget."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        await sun.issue_grant("agent_001", 1000, [], "Grant 1")
        await sun.issue_grant("agent_001", 2000, [], "Grant 2")

        assert sun.get_total_grant_budget("agent_001") == 3000
        assert sun.get_total_grant_budget("agent_002") == 0

    @pytest.mark.asyncio
    async def test_consume_grant(self) -> None:
        """Test consuming part of a grant."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        grant = await sun.issue_grant(
            grantee_id="agent_001",
            tokens=1000,
            intent_embedding=[],
            intent_description="Test",
        )

        consumption = await sun.consume_grant(grant.id, "phage_001", 300)

        assert consumption.grant_id == grant.id
        assert consumption.phage_id == "phage_001"
        assert consumption.tokens_consumed == 300

        assert grant.remaining == 700
        assert "phage_001" in grant.consumed_by

    @pytest.mark.asyncio
    async def test_consume_grant_fully(self) -> None:
        """Test consuming a grant fully."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        grant = await sun.issue_grant("agent_001", 500, [], "Test")

        await sun.consume_grant(grant.id, "phage_001", 500)

        assert grant.remaining == 0
        assert grant.status == GrantStatus.CONSUMED

    @pytest.mark.asyncio
    async def test_consume_grant_insufficient(self) -> None:
        """Test consuming more than available."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        grant = await sun.issue_grant("agent_001", 500, [], "Test")

        with pytest.raises(ValueError, match="has only"):
            await sun.consume_grant(grant.id, "phage_001", 600)

    @pytest.mark.asyncio
    async def test_revoke_grant(self) -> None:
        """Test revoking a grant."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        grant = await sun.issue_grant("agent_001", 1000, [], "Test")
        initial_balance = bank.get_balance()

        returned = await sun.revoke_grant(grant.id, return_unused=True)

        assert returned == 1000
        assert grant.status == GrantStatus.REVOKED
        assert grant.remaining == 0

        # Balance should decrease (unused tokens removed)
        assert bank.get_balance() == initial_balance - 1000

    @pytest.mark.asyncio
    async def test_grant_expiration(self) -> None:
        """Test that expired grants are detected."""
        bank = CentralBank(max_balance=100000)
        sun = Sun(bank)

        # Create grant with immediate expiration
        grant = await sun.issue_grant(
            grantee_id="agent_001",
            tokens=1000,
            intent_embedding=[],
            intent_description="Test",
            duration=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(ValueError, match="expired"):
            await sun.consume_grant(grant.id, "phage_001", 100)


# =============================================================================
# Staking Pool Tests
# =============================================================================


class TestStakingPool:
    """Tests for StakingPool."""

    def test_calculate_required_stake(self) -> None:
        """Test calculating required stake."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank, stake_rate=0.01)

        # 100 lines * 0.01 * 100 = 100 tokens
        assert pool.calculate_required_stake(100) == 100

        # With complexity multiplier
        assert pool.calculate_required_stake(100, complexity_score=2.0) == 200

        # Minimum stake enforced
        assert pool.calculate_required_stake(1) == 10  # Minimum

    @pytest.mark.asyncio
    async def test_stake_success(self) -> None:
        """Test staking successfully."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank)

        initial_balance = bank.get_balance()

        stake = await pool.stake(
            staker_id="agent_001",
            phage_id="phage_001",
            amount=100,
        )

        assert stake.staker_id == "agent_001"
        assert stake.phage_id == "phage_001"
        assert stake.stake == 100
        assert not stake.released
        assert not stake.forfeited

        # Balance should decrease
        assert bank.get_balance() < initial_balance

    @pytest.mark.asyncio
    async def test_release_stake(self) -> None:
        """Test releasing a stake after success."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank)

        stake = await pool.stake("agent_001", "phage_001", 100)
        balance_after_stake = bank.get_balance()

        returned = await pool.release_stake(stake.id)

        assert returned == 100
        assert stake.released

        # Balance should increase
        assert bank.get_balance() == balance_after_stake + 100

    @pytest.mark.asyncio
    async def test_release_stake_with_bonus(self) -> None:
        """Test releasing stake with bonus from pool."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank)

        # First stake fails, adding to pool
        stake1 = await pool.stake("agent_001", "phage_001", 100)
        await pool.forfeit_stake(stake1.id)
        assert pool.pool_balance == 100

        # Second stake succeeds with bonus
        stake2 = await pool.stake("agent_002", "phage_002", 100)

        returned = await pool.release_stake(stake2.id, bonus_percentage=0.5)

        # Should get stake + 50% of pool
        assert returned == 150

    @pytest.mark.asyncio
    async def test_forfeit_stake(self) -> None:
        """Test forfeiting a stake after failure."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank)

        stake = await pool.stake("agent_001", "phage_001", 100)

        forfeited = await pool.forfeit_stake(stake.id)

        assert forfeited == 100
        assert stake.forfeited
        assert pool.pool_balance == 100

    @pytest.mark.asyncio
    async def test_cannot_release_forfeited_stake(self) -> None:
        """Test that forfeited stakes cannot be released."""
        bank = CentralBank(max_balance=100000)
        pool = StakingPool(bank)

        stake = await pool.stake("agent_001", "phage_001", 100)
        await pool.forfeit_stake(stake.id)

        # Try to release after forfeit
        returned = await pool.release_stake(stake.id)
        assert returned == 0


# =============================================================================
# Combined Economics Tests
# =============================================================================


class TestEvolutionEconomics:
    """Tests for combined EvolutionEconomics."""

    def test_create_evolution_economics(self) -> None:
        """Test creating evolution economics system."""
        econ = create_evolution_economics(initial_balance=50000)

        assert econ.bank is not None
        assert econ.market is not None
        assert econ.sun is not None
        assert econ.staking is not None

        assert econ.bank.get_balance() == 50000

    @pytest.mark.asyncio
    async def test_full_evolution_workflow(self) -> None:
        """Test a full evolution workflow with all components."""
        econ = create_evolution_economics(initial_balance=100000)

        # 1. User issues grant for ambitious work
        grant = await econ.sun.issue_grant(
            grantee_id="evolution_agent",
            tokens=5000,
            intent_embedding=[0.1] * 64,
            intent_description="Refactor core module",
        )

        # 2. Agent proposes mutation, gets quote
        quote = econ.market.quote(
            phage_id="phage_refactor_001",
            schema_signature="extract_method",
            schema_confidence=0.7,
        )
        assert quote.implied_success_probability > 0

        # 3. Agent places bet on mutation success
        _bet = await econ.market.place_bet(
            bettor_id="evolution_agent",
            phage_id="phage_refactor_001",
            stake=100,
            predicted_success=True,
        )

        # 4. Agent stakes tokens for infect operation
        stake = await econ.staking.stake(
            staker_id="evolution_agent",
            phage_id="phage_refactor_001",
            amount=200,
        )

        # 5. Consume grant for the mutation work
        _consumption = await econ.sun.consume_grant(
            grant_id=grant.id,
            phage_id="phage_refactor_001",
            tokens=500,
        )

        # 6. Mutation succeeds!
        # Settle bet
        results = await econ.market.settle("phage_refactor_001", succeeded=True)
        assert results[0].outcome == BetOutcome.WON

        # Release stake
        returned = await econ.staking.release_stake(stake.id)
        assert returned == 200

        # 7. Update schema success rate
        econ.market.update_schema_success_rate("extract_method", True)

    @pytest.mark.asyncio
    async def test_evolution_workflow_failure(self) -> None:
        """Test evolution workflow when mutation fails."""
        econ = create_evolution_economics(initial_balance=100000)

        # Place bet and stake
        _bet = await econ.market.place_bet(
            bettor_id="agent",
            phage_id="phage_fail",
            stake=100,
            predicted_success=True,
        )

        stake = await econ.staking.stake(
            staker_id="agent",
            phage_id="phage_fail",
            amount=200,
        )

        # Mutation fails
        results = await econ.market.settle("phage_fail", succeeded=False)
        assert results[0].outcome == BetOutcome.LOST
        assert results[0].winnings == -100

        # Forfeit stake
        forfeited = await econ.staking.forfeit_stake(stake.id)
        assert forfeited == 200
        assert econ.staking.pool_balance == 200
