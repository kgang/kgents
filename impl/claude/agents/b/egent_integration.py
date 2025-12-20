"""
B-gent E-gent Integration: Market Economics for Teleological Thermodynamic Evolution.

This module bridges B-gent economics with E-gent evolution:
1. Prediction Market for mutation betting
2. Grant System for exogenous energy
3. Staking for phage infect operations

From spec/e-gents/thermodynamics.md:
> The Prediction Market acts as a self-regulating thermostat for evolution.
> Without market-driven selection, evolution wastes compute on unpromising mutations.

> The Sun provides exogenous energy for high-risk architectural work.
> Without grants, the system reaches heat death.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from uuid import uuid4

from .metered_functor import CentralBank

# =============================================================================
# Prediction Market for E-gent
# =============================================================================


class BetOutcome(Enum):
    """Possible outcomes for a mutation bet."""

    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    CANCELLED = "cancelled"


@dataclass
class MutationBet:
    """
    A bet on a mutation's success.

    The prediction market uses betting to discover the "true" probability
    that a mutation will improve the codebase.
    """

    id: str
    bettor_id: str
    phage_id: str
    stake: int  # Tokens staked
    odds: float  # Offered odds (e.g., 2.5 = 2.5:1)
    predicted_success: bool  # True = betting mutation succeeds
    outcome: BetOutcome = BetOutcome.PENDING
    placed_at: datetime = field(default_factory=datetime.now)
    settled_at: datetime | None = None
    payout: int = 0


@dataclass
class MarketQuote:
    """
    A quote from the prediction market.

    Provides current odds based on:
    - Historical success rate of similar mutations
    - Current market sentiment (existing bets)
    - Schema confidence from L-gent
    """

    phage_id: str
    success_odds: float  # Odds for success bet (e.g., 1.8)
    failure_odds: float  # Odds for failure bet (e.g., 2.2)
    implied_success_probability: float  # Market's implied probability
    liquidity: int  # Available tokens in pool
    quote_valid_until: datetime


@dataclass
class SettlementResult:
    """Result of settling a bet."""

    bet_id: str
    outcome: BetOutcome
    payout: int
    winnings: int  # payout - stake (can be negative)


class PredictionMarket:
    """
    Prediction market for mutation success.

    Allows agents to bet on whether mutations will succeed,
    creating price signals that guide evolution.

    From spec:
    > Every Phage → quote from Prediction Market.
    > quote = market's estimate of P(success).
    > If odds too long → skip (market thinks this will fail).
    > If odds short → proceed (market thinks this might work).
    """

    def __init__(
        self,
        bank: CentralBank,
        base_liquidity: int = 10000,
        min_stake: int = 10,
        max_stake: int = 1000,
    ):
        self.bank = bank
        self.base_liquidity = base_liquidity
        self.min_stake = min_stake
        self.max_stake = max_stake

        # Market state
        self.bets: dict[str, MutationBet] = {}
        self.pools: dict[
            str, dict[str, int]
        ] = {}  # phage_id → {"success": tokens, "failure": tokens}

        # Historical data for pricing
        self.schema_success_rates: dict[str, float] = {}  # schema_signature → success_rate
        self.recent_outcomes: list[tuple[str, bool]] = []  # (phage_id, succeeded)

    def quote(
        self,
        phage_id: str,
        schema_signature: str = "",
        schema_confidence: float = 0.5,
    ) -> MarketQuote:
        """
        Get a quote for betting on a mutation.

        Args:
            phage_id: ID of the phage (mutation)
            schema_signature: L-gent schema signature for historical lookup
            schema_confidence: L-gent's confidence in the schema

        Returns:
            MarketQuote with current odds
        """
        # Base probability from schema history
        if schema_signature and schema_signature in self.schema_success_rates:
            base_prob = self.schema_success_rates[schema_signature]
        else:
            base_prob = schema_confidence  # Use L-gent's confidence as prior

        # Adjust by current pool state
        pool = self.pools.get(
            phage_id, {"success": self.base_liquidity, "failure": self.base_liquidity}
        )
        success_pool = pool.get("success", self.base_liquidity)
        failure_pool = pool.get("failure", self.base_liquidity)

        # AMM-style odds calculation (constant product)
        total_pool = success_pool + failure_pool
        if total_pool > 0:
            market_prob = success_pool / total_pool
        else:
            market_prob = base_prob

        # Blend schema confidence with market sentiment
        implied_prob = 0.6 * base_prob + 0.4 * market_prob

        # Convert to odds (with spread for house edge)
        house_edge = 0.05
        if implied_prob > 0:
            success_odds = max(1.01, (1 / implied_prob) * (1 - house_edge))
        else:
            success_odds = 10.0  # Very unlikely

        if implied_prob < 1:
            failure_odds = max(1.01, (1 / (1 - implied_prob)) * (1 - house_edge))
        else:
            failure_odds = 10.0

        return MarketQuote(
            phage_id=phage_id,
            success_odds=round(success_odds, 2),
            failure_odds=round(failure_odds, 2),
            implied_success_probability=round(implied_prob, 3),
            liquidity=total_pool,
            quote_valid_until=datetime.now() + timedelta(minutes=5),
        )

    async def place_bet(
        self,
        bettor_id: str,
        phage_id: str,
        stake: int,
        predicted_success: bool,
    ) -> MutationBet:
        """
        Place a bet on a mutation.

        Args:
            bettor_id: ID of the bettor (agent)
            phage_id: ID of the phage
            stake: Tokens to stake
            predicted_success: True = betting mutation succeeds

        Returns:
            MutationBet record

        Raises:
            InsufficientFundsError: If bettor lacks funds
            ValueError: If stake out of bounds
        """
        if stake < self.min_stake:
            raise ValueError(f"Stake {stake} below minimum {self.min_stake}")
        if stake > self.max_stake:
            raise ValueError(f"Stake {stake} above maximum {self.max_stake}")

        # Get current quote
        quote = self.quote(phage_id)
        odds = quote.success_odds if predicted_success else quote.failure_odds

        # Authorize stake from bank
        lease = await self.bank.authorize(bettor_id, stake)

        try:
            # Initialize pool if needed
            if phage_id not in self.pools:
                self.pools[phage_id] = {
                    "success": self.base_liquidity,
                    "failure": self.base_liquidity,
                }

            # Add to pool
            pool_side = "success" if predicted_success else "failure"
            self.pools[phage_id][pool_side] += stake

            # Create bet
            bet = MutationBet(
                id=f"bet_{uuid4().hex[:8]}",
                bettor_id=bettor_id,
                phage_id=phage_id,
                stake=stake,
                odds=odds,
                predicted_success=predicted_success,
            )
            self.bets[bet.id] = bet

            # Settle the lease (consume the tokens)
            await self.bank.settle(lease, stake)

            return bet

        except Exception as e:
            # Rollback on error
            await self.bank.void(lease)
            raise e

    async def settle(self, phage_id: str, succeeded: bool) -> list[SettlementResult]:
        """
        Settle all bets for a phage after mutation outcome is known.

        Args:
            phage_id: ID of the phage
            succeeded: Whether the mutation succeeded

        Returns:
            List of settlement results
        """
        results = []

        # Find all bets for this phage
        phage_bets = [
            b
            for b in self.bets.values()
            if b.phage_id == phage_id and b.outcome == BetOutcome.PENDING
        ]

        for bet in phage_bets:
            bet_won = bet.predicted_success == succeeded

            if bet_won:
                bet.outcome = BetOutcome.WON
                bet.payout = int(bet.stake * bet.odds)
                winnings = bet.payout - bet.stake

                # Credit winnings back to bettor (via bucket since CentralBank doesn't have direct credit)
                self.bank.bucket.balance = min(
                    self.bank.bucket.max_balance,
                    self.bank.bucket.balance + bet.payout,
                )
            else:
                bet.outcome = BetOutcome.LOST
                bet.payout = 0
                winnings = -bet.stake

            bet.settled_at = datetime.now()

            results.append(
                SettlementResult(
                    bet_id=bet.id,
                    outcome=bet.outcome,
                    payout=bet.payout,
                    winnings=winnings,
                )
            )

        # Update schema success rate
        self.recent_outcomes.append((phage_id, succeeded))
        if len(self.recent_outcomes) > 1000:
            self.recent_outcomes = self.recent_outcomes[-1000:]

        return results

    def update_schema_success_rate(self, schema_signature: str, succeeded: bool) -> None:
        """
        Update historical success rate for a schema.

        Called after settlement to improve future quotes.
        """
        current = self.schema_success_rates.get(schema_signature, 0.5)
        # Exponential moving average
        alpha = 0.1
        new_value = 1.0 if succeeded else 0.0
        self.schema_success_rates[schema_signature] = (1 - alpha) * current + alpha * new_value


# =============================================================================
# Grant System (The Sun)
# =============================================================================


class GrantStatus(Enum):
    """Status of a grant."""

    ACTIVE = "active"
    CONSUMED = "consumed"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class Grant:
    """
    An energy grant from the Sun (User).

    From spec:
    > The Sun provides exogenous energy (User Grant) for high-risk architectural work.
    > Without grants, the system reaches "heat death" (only safe, incremental changes).

    > Grant semantics:
    > - User explicitly allocates tokens to ambitious goal
    > - Grant marked with Intent embedding (what success looks like)
    > - Grant consumed as mutations progress
    > - Unused portion returnable on success OR cancellation
    """

    id: str
    grantee_id: str
    tokens: int
    remaining: int
    intent_embedding: list[float]  # What the user wants
    intent_description: str
    status: GrantStatus = GrantStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    consumed_by: list[str] = field(default_factory=list)  # Phage IDs


@dataclass
class GrantConsumption:
    """Record of consuming part of a grant."""

    grant_id: str
    phage_id: str
    tokens_consumed: int
    consumed_at: datetime = field(default_factory=datetime.now)


class Sun:
    """
    The Sun: Source of exogenous energy for evolution.

    Without the Sun, evolution can only make incremental changes
    (staying within entropy budget). The Sun enables:
    - Architectural refactoring
    - High-risk experimental features
    - Breaking changes that improve long-term design

    From spec:
    > The Sun is NOT an infinite resource. It represents the User's
    > willingness to invest compute in uncertain outcomes.
    """

    def __init__(self, bank: CentralBank, default_grant_duration: timedelta = timedelta(hours=24)):
        self.bank = bank
        self.default_grant_duration = default_grant_duration
        self.grants: dict[str, Grant] = {}
        self.consumption_log: list[GrantConsumption] = []

    async def issue_grant(
        self,
        grantee_id: str,
        tokens: int,
        intent_embedding: list[float],
        intent_description: str,
        duration: timedelta | None = None,
    ) -> Grant:
        """
        Issue a grant to an agent.

        Args:
            grantee_id: Agent receiving the grant
            tokens: Number of tokens in grant
            intent_embedding: Embedding of user's intent
            intent_description: Human-readable intent
            duration: How long grant is valid

        Returns:
            Grant object
        """
        # Grants come from outside the system (user provides compute budget)
        # So we add to the bank's balance rather than subtracting
        self.bank.bucket.balance = min(
            self.bank.bucket.max_balance,
            self.bank.bucket.balance + tokens,
        )

        grant = Grant(
            id=f"grant_{uuid4().hex[:8]}",
            grantee_id=grantee_id,
            tokens=tokens,
            remaining=tokens,
            intent_embedding=intent_embedding,
            intent_description=intent_description,
            expires_at=datetime.now() + (duration or self.default_grant_duration),
        )
        self.grants[grant.id] = grant

        return grant

    def has_active_grant(self, grantee_id: str) -> bool:
        """Check if agent has any active grant."""
        for grant in self.grants.values():
            if grant.grantee_id == grantee_id and grant.status == GrantStatus.ACTIVE:
                if grant.expires_at is None or grant.expires_at > datetime.now():
                    return True
        return False

    def get_active_grants(self, grantee_id: str) -> list[Grant]:
        """Get all active grants for an agent."""
        now = datetime.now()
        return [
            g
            for g in self.grants.values()
            if g.grantee_id == grantee_id
            and g.status == GrantStatus.ACTIVE
            and (g.expires_at is None or g.expires_at > now)
        ]

    def get_total_grant_budget(self, grantee_id: str) -> int:
        """Get total remaining tokens across all active grants."""
        return sum(g.remaining for g in self.get_active_grants(grantee_id))

    async def consume_grant(
        self,
        grant_id: str,
        phage_id: str,
        tokens: int,
    ) -> GrantConsumption:
        """
        Consume part of a grant for a mutation.

        Args:
            grant_id: ID of grant to consume from
            phage_id: ID of phage using the grant
            tokens: Number of tokens to consume

        Returns:
            GrantConsumption record

        Raises:
            ValueError: If grant invalid or insufficient
        """
        grant = self.grants.get(grant_id)
        if not grant:
            raise ValueError(f"Grant {grant_id} not found")
        if grant.status != GrantStatus.ACTIVE:
            raise ValueError(f"Grant {grant_id} not active: {grant.status}")
        if grant.expires_at and grant.expires_at < datetime.now():
            grant.status = GrantStatus.EXPIRED
            raise ValueError(f"Grant {grant_id} expired")
        if tokens > grant.remaining:
            raise ValueError(
                f"Grant {grant_id} has only {grant.remaining} tokens, requested {tokens}"
            )

        # Consume from grant
        grant.remaining -= tokens
        grant.consumed_by.append(phage_id)

        if grant.remaining == 0:
            grant.status = GrantStatus.CONSUMED

        consumption = GrantConsumption(
            grant_id=grant_id,
            phage_id=phage_id,
            tokens_consumed=tokens,
        )
        self.consumption_log.append(consumption)

        return consumption

    async def revoke_grant(self, grant_id: str, return_unused: bool = True) -> int:
        """
        Revoke a grant and optionally return unused tokens.

        Args:
            grant_id: ID of grant to revoke
            return_unused: Whether to return unused tokens to pool

        Returns:
            Number of tokens returned (0 if not returning)
        """
        grant = self.grants.get(grant_id)
        if not grant:
            return 0

        returned = 0
        if return_unused and grant.remaining > 0:
            returned = grant.remaining
            # Remove unused tokens from circulation
            self.bank.bucket.balance = max(0, self.bank.bucket.balance - returned)

        grant.status = GrantStatus.REVOKED
        grant.remaining = 0

        return returned


# =============================================================================
# Staking for Phage Operations
# =============================================================================


@dataclass
class PhageStake:
    """
    Stake placed for a phage infect operation.

    Staking ensures agents have "skin in the game" when proposing mutations.
    """

    id: str
    staker_id: str
    phage_id: str
    stake: int
    released: bool = False
    forfeited: bool = False
    staked_at: datetime = field(default_factory=datetime.now)


class StakingPool:
    """
    Pool for staking on phage operations.

    Staking mechanism:
    1. Before infect, agent stakes tokens proportional to change size
    2. If mutation passes tests → stake returned
    3. If mutation fails tests → stake forfeited to pool
    4. Pool redistributed to successful mutations (bonus)
    """

    def __init__(self, bank: CentralBank, stake_rate: float = 0.01):
        """
        Initialize staking pool.

        Args:
            bank: CentralBank for token operations
            stake_rate: Stake required per "unit" of change (e.g., per line)
        """
        self.bank = bank
        self.stake_rate = stake_rate
        self.stakes: dict[str, PhageStake] = {}
        self.pool_balance: int = 0

    def calculate_required_stake(self, lines_changed: int, complexity_score: float = 1.0) -> int:
        """
        Calculate required stake for a mutation.

        Args:
            lines_changed: Number of lines the mutation changes
            complexity_score: Complexity multiplier from analysis

        Returns:
            Required stake in tokens
        """
        base_stake = int(lines_changed * self.stake_rate * 100)
        adjusted = int(base_stake * complexity_score)
        return max(10, adjusted)  # Minimum stake of 10

    async def stake(
        self,
        staker_id: str,
        phage_id: str,
        amount: int,
    ) -> PhageStake:
        """
        Stake tokens for a phage operation.

        Args:
            staker_id: Agent placing stake
            phage_id: Phage being staked on
            amount: Tokens to stake

        Returns:
            PhageStake record
        """
        # Authorize stake from bank
        lease = await self.bank.authorize(staker_id, amount)

        try:
            stake = PhageStake(
                id=f"stake_{uuid4().hex[:8]}",
                staker_id=staker_id,
                phage_id=phage_id,
                stake=amount,
            )
            self.stakes[stake.id] = stake

            # Settle (consume tokens)
            await self.bank.settle(lease, amount)

            return stake

        except Exception as e:
            await self.bank.void(lease)
            raise e

    async def release_stake(self, stake_id: str, bonus_percentage: float = 0.0) -> int:
        """
        Release stake after successful mutation.

        Args:
            stake_id: ID of stake to release
            bonus_percentage: Bonus from pool (0.0-1.0)

        Returns:
            Total tokens returned (stake + bonus)
        """
        stake = self.stakes.get(stake_id)
        if not stake or stake.released or stake.forfeited:
            return 0

        stake.released = True

        # Calculate bonus from pool
        bonus = int(self.pool_balance * bonus_percentage)
        self.pool_balance = max(0, self.pool_balance - bonus)

        total_return = stake.stake + bonus

        # Credit back to bank
        self.bank.bucket.balance = min(
            self.bank.bucket.max_balance,
            self.bank.bucket.balance + total_return,
        )

        return total_return

    async def forfeit_stake(self, stake_id: str) -> int:
        """
        Forfeit stake after failed mutation.

        Args:
            stake_id: ID of stake to forfeit

        Returns:
            Tokens added to pool
        """
        stake = self.stakes.get(stake_id)
        if not stake or stake.released or stake.forfeited:
            return 0

        stake.forfeited = True
        self.pool_balance += stake.stake

        return stake.stake


# =============================================================================
# Combined E-gent Economics
# =============================================================================


@dataclass
class EvolutionEconomics:
    """
    Combined economic system for E-gent evolution.

    Integrates:
    - CentralBank: Token accounting
    - PredictionMarket: Mutation betting
    - Sun: Grants for high-risk work
    - StakingPool: Skin-in-the-game for infect operations
    """

    bank: CentralBank
    market: PredictionMarket
    sun: Sun
    staking: StakingPool


def create_evolution_economics(
    initial_balance: int = 100000,
    refill_rate: float = 100.0,
) -> EvolutionEconomics:
    """
    Create a complete evolution economics system.

    Args:
        initial_balance: Initial token balance
        refill_rate: Token refill rate per second

    Returns:
        EvolutionEconomics instance with all components
    """
    bank = CentralBank(
        max_balance=initial_balance,
        refill_rate=refill_rate,
    )

    return EvolutionEconomics(
        bank=bank,
        market=PredictionMarket(bank),
        sun=Sun(bank),
        staking=StakingPool(bank),
    )
