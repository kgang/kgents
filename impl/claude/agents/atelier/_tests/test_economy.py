"""
Tests for TokenPool spectator economy.

Coverage:
1. Balance management (create, query, initial grant)
2. Token accrual (timing, tier multipliers, minimum watch time)
3. Watch sessions (start, stop, accrue mid-session, session tracking)
4. Spending (success, failure, validation, spend_or_raise)
5. Refunds (from bid outcomes)
6. Transfers (between users, self-transfer rejection)
7. Tier integration (FREE, PRO, TEAMS, ENTERPRISE)
8. AGENTESE manifest integration
9. Input validation (empty user_id, negative amounts, NaN, etc.)
10. Bidding integration (process_bid, process_bid_outcome)
11. AsyncTokenPool (thread-safe operations)
12. Edge cases (clock drift, zero amounts, long user_id)
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from agents.atelier.economy import (
    MIN_WATCH_SECONDS,
    TIER_MULTIPLIERS,
    AccrualTier,
    AsyncTokenPool,
    DefaultTierProvider,
    InsufficientBalanceError,
    InvalidAmountError,
    InvalidUserError,
    LicenseTierProvider,
    RefundResult,
    SessionError,
    TokenPool,
    TokenPoolError,
    UserBalance,
    create_async_token_pool,
    create_token_pool,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def pool() -> TokenPool:
    """Create a fresh token pool with default settings."""
    return TokenPool()


@pytest.fixture
def pool_no_grant() -> TokenPool:
    """Create a token pool without initial grant."""
    return TokenPool(initial_grant=Decimal("0"))


@pytest.fixture
def pool_no_min_watch() -> TokenPool:
    """Create a token pool with no minimum watch time."""
    return TokenPool(min_watch_seconds=0)


@pytest.fixture
def tier_provider() -> LicenseTierProvider:
    """Create a tier provider for testing."""
    return LicenseTierProvider()


@pytest.fixture
def pool_with_tiers(tier_provider: LicenseTierProvider) -> TokenPool:
    """Create a pool with configurable tiers."""
    return TokenPool(tier_provider=tier_provider)


# =============================================================================
# Balance Management Tests
# =============================================================================


class TestBalanceManagement:
    """Tests for basic balance operations."""

    def test_new_user_receives_initial_grant(self, pool: TokenPool) -> None:
        """New users should receive the initial grant (default 10 tokens)."""
        balance = pool.get_balance("new_user")
        assert balance.balance == Decimal("10")
        assert balance.total_accrued == Decimal("10")

    def test_get_balance_creates_user(self, pool: TokenPool) -> None:
        """Getting balance for unknown user creates their account."""
        assert "unknown" not in pool.get_all_users()
        pool.get_balance("unknown")
        assert "unknown" in pool.get_all_users()

    def test_get_balance_idempotent(self, pool: TokenPool) -> None:
        """Multiple balance queries don't change balance."""
        pool.get_balance("user1")
        balance1 = pool.get_balance("user1").balance
        balance2 = pool.get_balance("user1").balance
        assert balance1 == balance2 == Decimal("10")

    def test_whole_tokens(self, pool: TokenPool) -> None:
        """whole_tokens should floor fractional balances."""
        balance = pool.get_balance("user1")
        balance.balance = Decimal("15.9")
        assert pool.get_whole_tokens("user1") == 15

    def test_zero_initial_grant(self, pool_no_grant: TokenPool) -> None:
        """Pool with zero initial grant starts users at 0."""
        balance = pool_no_grant.get_balance("user1")
        assert balance.balance == Decimal("0")

    def test_user_exists(self, pool: TokenPool) -> None:
        """user_exists should return False for unknown users."""
        assert not pool.user_exists("unknown")
        pool.get_balance("unknown")
        assert pool.user_exists("unknown")


class TestUserBalance:
    """Tests for UserBalance dataclass."""

    def test_can_spend_sufficient(self) -> None:
        """can_spend returns True when balance is sufficient."""
        balance = UserBalance(user_id="u1", balance=Decimal("10"))
        assert balance.can_spend(Decimal("5"))
        assert balance.can_spend(Decimal("10"))

    def test_can_spend_insufficient(self) -> None:
        """can_spend returns False when balance is insufficient."""
        balance = UserBalance(user_id="u1", balance=Decimal("10"))
        assert not balance.can_spend(Decimal("10.01"))
        assert not balance.can_spend(Decimal("100"))

    def test_to_dict_serialization(self) -> None:
        """UserBalance should serialize correctly."""
        balance = UserBalance(
            user_id="u1",
            balance=Decimal("25.5"),
            total_accrued=Decimal("30"),
            total_spent=Decimal("4.5"),
            total_refunded=Decimal("2"),
        )
        data = balance.to_dict()
        assert data["user_id"] == "u1"
        assert data["balance"] == "25.5"
        assert data["whole_tokens"] == 25
        assert data["total_refunded"] == "2"


# =============================================================================
# Input Validation Tests
# =============================================================================


class TestInputValidation:
    """Tests for input validation and error handling."""

    def test_empty_user_id_raises(self, pool: TokenPool) -> None:
        """Empty user_id should raise InvalidUserError."""
        with pytest.raises(InvalidUserError):
            pool.get_balance("")

    def test_none_user_id_raises(self, pool: TokenPool) -> None:
        """None user_id should raise InvalidUserError."""
        with pytest.raises(InvalidUserError):
            pool.get_balance(None)  # type: ignore

    def test_long_user_id_raises(self, pool: TokenPool) -> None:
        """user_id over 256 chars should raise InvalidUserError."""
        long_id = "x" * 257
        with pytest.raises(InvalidUserError):
            pool.get_balance(long_id)

    def test_negative_amount_raises(self, pool: TokenPool) -> None:
        """Negative amount should raise InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            pool.grant("user1", Decimal("-5"))

    def test_zero_amount_raises_for_grant(self, pool: TokenPool) -> None:
        """Zero amount should raise for grant."""
        with pytest.raises(InvalidAmountError):
            pool.grant("user1", Decimal("0"))

    def test_nan_amount_raises(self, pool: TokenPool) -> None:
        """NaN amount should raise InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            pool.grant("user1", Decimal("NaN"))

    def test_infinite_amount_raises(self, pool: TokenPool) -> None:
        """Infinite amount should raise InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            pool.grant("user1", Decimal("Infinity"))

    def test_negative_initial_grant_raises(self) -> None:
        """Negative initial_grant should raise InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            TokenPool(initial_grant=Decimal("-5"))

    def test_non_decimal_amount_raises(self, pool: TokenPool) -> None:
        """Non-Decimal amount should raise InvalidAmountError."""
        with pytest.raises(InvalidAmountError):
            pool.grant("user1", 5)  # type: ignore


# =============================================================================
# Watch Session Tests
# =============================================================================


class TestWatchSessions:
    """Tests for watch session tracking."""

    def test_start_watching(self, pool: TokenPool) -> None:
        """start_watching should initiate a session."""
        assert pool.start_watching("user1")
        assert pool.is_watching("user1")

    def test_start_watching_with_session_id(self, pool: TokenPool) -> None:
        """start_watching should track session ID."""
        pool.start_watching("user1", session_id="session-123")
        balance = pool.get_balance("user1")
        assert balance.current_session_id == "session-123"

    def test_start_watching_returns_false_if_already_watching(self, pool: TokenPool) -> None:
        """Can't start watching if already watching."""
        pool.start_watching("user1")
        assert not pool.start_watching("user1")

    def test_stop_watching_accrues_tokens(self, pool_no_min_watch: TokenPool) -> None:
        """stop_watching should accrue tokens for time watched."""
        start = datetime.now() - timedelta(minutes=5)
        pool_no_min_watch.start_watching("user1", timestamp=start)

        result = pool_no_min_watch.stop_watching("user1")
        assert result is not None
        assert result.minutes_watched >= Decimal("4.9")
        assert result.tokens_accrued >= Decimal("4.9")  # FREE tier = 1x

    def test_stop_watching_clears_session(self, pool: TokenPool) -> None:
        """stop_watching should clear the watch session."""
        pool.start_watching("user1")
        pool.stop_watching("user1")
        assert not pool.is_watching("user1")

    def test_stop_watching_returns_none_if_not_watching(self, pool: TokenPool) -> None:
        """stop_watching returns None if not watching."""
        result = pool.stop_watching("user1")
        assert result is None

    def test_accrue_mid_session(self, pool_no_min_watch: TokenPool) -> None:
        """accrue should credit tokens without stopping the session."""
        start = datetime.now() - timedelta(minutes=5)
        pool_no_min_watch.start_watching("user1", timestamp=start)

        result = pool_no_min_watch.accrue("user1")
        assert result is not None
        assert result.tokens_accrued >= Decimal("4.9")
        # Still watching
        assert pool_no_min_watch.is_watching("user1")

    def test_is_watching_returns_false_for_unknown_user(self, pool: TokenPool) -> None:
        """is_watching returns False for users not in the pool."""
        assert not pool.is_watching("unknown_user")

    def test_minimum_watch_time_enforced(self, pool: TokenPool) -> None:
        """Watch sessions under MIN_WATCH_SECONDS should accrue 0 tokens."""
        start = datetime.now() - timedelta(seconds=MIN_WATCH_SECONDS - 1)
        pool.start_watching("user1", timestamp=start)

        result = pool.stop_watching("user1")
        assert result is not None
        assert result.tokens_accrued == Decimal("0")

    def test_get_watch_session_info(self, pool: TokenPool) -> None:
        """get_watch_session_info should return session details."""
        pool.start_watching("user1", session_id="sess-456")
        info = pool.get_watch_session_info("user1")

        assert info is not None
        assert info["user_id"] == "user1"
        assert info["session_id"] == "sess-456"
        assert "started_at" in info
        assert "elapsed_seconds" in info

    def test_get_watch_session_info_returns_none_if_not_watching(self, pool: TokenPool) -> None:
        """get_watch_session_info returns None if not watching."""
        pool.get_balance("user1")  # Create user
        assert pool.get_watch_session_info("user1") is None

    def test_get_session_watchers(self, pool: TokenPool) -> None:
        """get_session_watchers returns users watching a specific session."""
        pool.start_watching("alice", session_id="sess-1")
        pool.start_watching("bob", session_id="sess-1")
        pool.start_watching("charlie", session_id="sess-2")

        watchers = pool.get_session_watchers("sess-1")
        assert set(watchers) == {"alice", "bob"}


# =============================================================================
# Tier Multiplier Tests
# =============================================================================


class TestTierMultipliers:
    """Tests for tier-based accrual multipliers."""

    def test_free_tier_multiplier(
        self, pool_with_tiers: TokenPool, tier_provider: LicenseTierProvider
    ) -> None:
        """FREE tier should have 1.0x multiplier."""
        tier_provider.set_tier("user1", AccrualTier.FREE)
        pool_with_tiers._min_watch_seconds = 0  # Disable for test

        start = datetime.now() - timedelta(minutes=10)
        pool_with_tiers.start_watching("user1", timestamp=start)
        result = pool_with_tiers.stop_watching("user1")

        assert result is not None
        assert result.tier == AccrualTier.FREE
        assert result.multiplier == Decimal("1.0")
        assert result.tokens_accrued >= Decimal("9.9")
        assert result.tokens_accrued <= Decimal("10.1")

    def test_pro_tier_multiplier(
        self, pool_with_tiers: TokenPool, tier_provider: LicenseTierProvider
    ) -> None:
        """PRO tier should have 2.5x multiplier."""
        tier_provider.set_tier("user1", AccrualTier.PRO)
        pool_with_tiers._min_watch_seconds = 0

        start = datetime.now() - timedelta(minutes=10)
        pool_with_tiers.start_watching("user1", timestamp=start)
        result = pool_with_tiers.stop_watching("user1")

        assert result is not None
        assert result.tier == AccrualTier.PRO
        assert result.multiplier == Decimal("2.5")
        assert result.tokens_accrued >= Decimal("24.9")
        assert result.tokens_accrued <= Decimal("25.1")

    def test_teams_tier_multiplier(
        self, pool_with_tiers: TokenPool, tier_provider: LicenseTierProvider
    ) -> None:
        """TEAMS tier should have 3.5x multiplier."""
        tier_provider.set_tier("user1", AccrualTier.TEAMS)
        pool_with_tiers._min_watch_seconds = 0

        start = datetime.now() - timedelta(minutes=10)
        pool_with_tiers.start_watching("user1", timestamp=start)
        result = pool_with_tiers.stop_watching("user1")

        assert result is not None
        assert result.tier == AccrualTier.TEAMS
        assert result.multiplier == Decimal("3.5")
        assert result.tokens_accrued >= Decimal("34.9")
        assert result.tokens_accrued <= Decimal("35.1")

    def test_enterprise_tier_multiplier(
        self, pool_with_tiers: TokenPool, tier_provider: LicenseTierProvider
    ) -> None:
        """ENTERPRISE tier should have 5.0x multiplier."""
        tier_provider.set_tier("user1", AccrualTier.ENTERPRISE)
        pool_with_tiers._min_watch_seconds = 0

        start = datetime.now() - timedelta(minutes=10)
        pool_with_tiers.start_watching("user1", timestamp=start)
        result = pool_with_tiers.stop_watching("user1")

        assert result is not None
        assert result.tier == AccrualTier.ENTERPRISE
        assert result.multiplier == Decimal("5.0")
        assert result.tokens_accrued >= Decimal("49.9")
        assert result.tokens_accrued <= Decimal("50.1")

    def test_tier_multipliers_defined_correctly(self) -> None:
        """Verify all tier multipliers are defined."""
        assert TIER_MULTIPLIERS[AccrualTier.FREE] == Decimal("1.0")
        assert TIER_MULTIPLIERS[AccrualTier.PRO] == Decimal("2.5")
        assert TIER_MULTIPLIERS[AccrualTier.TEAMS] == Decimal("3.5")
        assert TIER_MULTIPLIERS[AccrualTier.ENTERPRISE] == Decimal("5.0")


class TestTierProvider:
    """Tests for tier providers."""

    def test_default_tier_provider_returns_free(self) -> None:
        """DefaultTierProvider always returns FREE."""
        provider = DefaultTierProvider()
        assert provider.get_tier("any_user") == AccrualTier.FREE
        assert provider.get_tier("another_user") == AccrualTier.FREE

    def test_license_tier_provider_set_and_get(self) -> None:
        """LicenseTierProvider should store and retrieve tiers."""
        provider = LicenseTierProvider()
        provider.set_tier("user1", AccrualTier.PRO)
        provider.set_tier("user2", AccrualTier.ENTERPRISE)

        assert provider.get_tier("user1") == AccrualTier.PRO
        assert provider.get_tier("user2") == AccrualTier.ENTERPRISE
        assert provider.get_tier("unknown") == AccrualTier.FREE


# =============================================================================
# Spending Tests
# =============================================================================


class TestSpending:
    """Tests for token spending."""

    def test_spend_success(self, pool: TokenPool) -> None:
        """Spending within balance should succeed."""
        result = pool.spend("user1", Decimal("5"))
        assert result.success
        assert result.new_balance == Decimal("5")  # 10 - 5

    def test_spend_failure_insufficient(self, pool: TokenPool) -> None:
        """Spending more than balance should fail."""
        result = pool.spend("user1", Decimal("15"))
        assert not result.success
        assert "Insufficient" in (result.reason or "")
        assert result.new_balance == Decimal("10")  # Unchanged

    def test_spend_updates_total_spent(self, pool: TokenPool) -> None:
        """Spending should update total_spent tracker."""
        pool.spend("user1", Decimal("3"))
        balance = pool.get_balance("user1")
        assert balance.total_spent == Decimal("3")

    def test_spend_exact_balance(self, pool: TokenPool) -> None:
        """Spending exactly the balance should succeed."""
        result = pool.spend("user1", Decimal("10"))
        assert result.success
        assert result.new_balance == Decimal("0")

    def test_spend_or_raise_success(self, pool: TokenPool) -> None:
        """spend_or_raise should return new balance on success."""
        new_balance = pool.spend_or_raise("user1", Decimal("5"))
        assert new_balance == Decimal("5")

    def test_spend_or_raise_failure(self, pool: TokenPool) -> None:
        """spend_or_raise should raise InsufficientBalanceError on failure."""
        with pytest.raises(InsufficientBalanceError) as exc_info:
            pool.spend_or_raise("user1", Decimal("15"))

        assert exc_info.value.user_id == "user1"
        assert exc_info.value.required == Decimal("15")
        assert exc_info.value.available == Decimal("10")


# =============================================================================
# Grant Tests
# =============================================================================


class TestGranting:
    """Tests for token grants."""

    def test_grant_adds_tokens(self, pool: TokenPool) -> None:
        """Grant should add tokens to balance."""
        new_balance = pool.grant("user1", Decimal("25"))
        assert new_balance == Decimal("35")  # 10 + 25

    def test_grant_updates_total_accrued(self, pool: TokenPool) -> None:
        """Grant should update total_accrued."""
        pool.grant("user1", Decimal("25"))
        balance = pool.get_balance("user1")
        assert balance.total_accrued == Decimal("35")  # 10 initial + 25


# =============================================================================
# Refund Tests
# =============================================================================


class TestRefunds:
    """Tests for token refunds."""

    def test_refund_adds_tokens(self, pool: TokenPool) -> None:
        """Refund should add tokens to balance."""
        result = pool.refund("user1", Decimal("5"), reason="bid rejected")
        assert result.amount == Decimal("5")
        assert result.new_balance == Decimal("15")  # 10 + 5

    def test_refund_updates_total_refunded(self, pool: TokenPool) -> None:
        """Refund should update total_refunded (not total_accrued)."""
        pool.refund("user1", Decimal("5"))
        balance = pool.get_balance("user1")
        assert balance.total_refunded == Decimal("5")
        assert balance.total_accrued == Decimal("10")  # Unchanged

    def test_refund_zero_is_noop(self, pool: TokenPool) -> None:
        """Refund of 0 should work but not change anything."""
        result = pool.refund("user1", Decimal("0"), reason="no refund")
        assert result.amount == Decimal("0")
        assert result.new_balance == Decimal("10")


# =============================================================================
# Transfer Tests
# =============================================================================


class TestTransfers:
    """Tests for token transfers."""

    def test_transfer_success(self, pool: TokenPool) -> None:
        """Successful transfer should debit sender and credit receiver."""
        spend_result, new_balance = pool.transfer("user1", "user2", Decimal("5"))

        assert spend_result.success
        assert pool.get_balance_amount("user1") == Decimal("5")
        assert new_balance == Decimal("15")  # 10 + 5

    def test_transfer_failure_insufficient(self, pool: TokenPool) -> None:
        """Failed transfer should not affect either balance."""
        spend_result, new_balance = pool.transfer("user1", "user2", Decimal("15"))

        assert not spend_result.success
        assert new_balance is None
        assert pool.get_balance_amount("user1") == Decimal("10")
        assert pool.get_balance_amount("user2") == Decimal("10")

    def test_transfer_to_self_raises(self, pool: TokenPool) -> None:
        """Transfer to self should raise InvalidUserError."""
        with pytest.raises(InvalidUserError, match="Cannot transfer to self"):
            pool.transfer("user1", "user1", Decimal("5"))


# =============================================================================
# Query Tests
# =============================================================================


class TestQueries:
    """Tests for pool queries."""

    def test_get_all_users(self, pool: TokenPool) -> None:
        """get_all_users should return all user IDs."""
        pool.get_balance("alice")
        pool.get_balance("bob")
        pool.get_balance("charlie")

        users = pool.get_all_users()
        assert set(users) == {"alice", "bob", "charlie"}

    def test_get_total_supply(self, pool: TokenPool) -> None:
        """get_total_supply should sum all balances."""
        pool.get_balance("user1")  # 10
        pool.get_balance("user2")  # 10
        pool.grant("user1", Decimal("5"))  # user1 now 15

        assert pool.get_total_supply() == Decimal("25")

    def test_get_total_supply_empty_pool(self, pool: TokenPool) -> None:
        """get_total_supply should return 0 for empty pool."""
        assert pool.get_total_supply() == Decimal("0")

    def test_get_leaderboard(self, pool: TokenPool) -> None:
        """get_leaderboard should return top users by balance."""
        pool.grant("alice", Decimal("50"))  # 60 total
        pool.get_balance("bob")  # 10
        pool.grant("charlie", Decimal("20"))  # 30 total

        leaderboard = pool.get_leaderboard(limit=2)
        assert len(leaderboard) == 2
        assert leaderboard[0].user_id == "alice"
        assert leaderboard[1].user_id == "charlie"

    def test_get_active_watchers(self, pool: TokenPool) -> None:
        """get_active_watchers should return watching users."""
        pool.start_watching("alice")
        pool.start_watching("bob")
        pool.get_balance("charlie")  # Not watching

        watchers = pool.get_active_watchers()
        assert set(watchers) == {"alice", "bob"}


# =============================================================================
# AGENTESE Integration Tests
# =============================================================================


class TestAGENTESEIntegration:
    """Tests for AGENTESE path integration."""

    def test_manifest_returns_correct_structure(self, pool: TokenPool) -> None:
        """manifest should return proper AGENTESE structure."""
        result = pool.manifest("user1")

        assert result["path"] == "self.tokens"
        assert result["aspect"] == "manifest"
        assert result["user_id"] == "user1"
        assert result["balance"] == "10"
        assert result["whole_tokens"] == 10
        assert result["tier"] == "FREE"
        assert result["multiplier"] == "1.0"
        assert result["total_refunded"] == "0"

    def test_manifest_reflects_watching_state(self, pool: TokenPool) -> None:
        """manifest should indicate watching status."""
        assert not pool.manifest("user1")["watching"]

        pool.start_watching("user1", session_id="sess-xyz")
        manifest = pool.manifest("user1")
        assert manifest["watching"]
        assert manifest["current_session"] == "sess-xyz"

        pool.stop_watching("user1")
        assert not pool.manifest("user1")["watching"]

    def test_manifest_with_tier(
        self, pool_with_tiers: TokenPool, tier_provider: LicenseTierProvider
    ) -> None:
        """manifest should reflect user's tier."""
        tier_provider.set_tier("user1", AccrualTier.PRO)

        result = pool_with_tiers.manifest("user1")
        assert result["tier"] == "PRO"
        assert result["multiplier"] == "2.5"

    def test_to_dict_pool_serialization(self, pool: TokenPool) -> None:
        """to_dict should serialize entire pool state."""
        pool.get_balance("user1")
        pool.start_watching("user2")

        data = pool.to_dict()
        assert "users" in data
        assert "user1" in data["users"]
        assert "user2" in data["users"]
        assert data["active_watchers"] == 1
        assert data["user_count"] == 2


# =============================================================================
# Bidding Integration Tests
# =============================================================================


class TestBiddingIntegration:
    """Tests for bidding system integration."""

    def test_process_bid_success(self, pool: TokenPool) -> None:
        """process_bid should deduct tokens and create bid."""
        from agents.atelier.bidding import BidType

        spend_result, bid = pool.process_bid(
            user_id="user1",
            bid_type=BidType.REQUEST_DIRECTION,
            session_id="sess-123",
            content="Add more contrast",
        )

        assert spend_result.success
        assert bid is not None
        assert bid.spectator_id == "user1"
        assert bid.session_id == "sess-123"
        assert bid.content == "Add more contrast"
        assert spend_result.new_balance == Decimal("5")  # 10 - 5

    def test_process_bid_insufficient_balance(self, pool_no_grant: TokenPool) -> None:
        """process_bid should fail with insufficient balance."""
        from agents.atelier.bidding import BidType

        spend_result, bid = pool_no_grant.process_bid(
            user_id="broke_user",
            bid_type=BidType.INJECT_CONSTRAINT,  # Costs 10
            session_id="sess-123",
            content="some constraint",
        )

        assert not spend_result.success
        assert bid is None

    def test_process_bid_outcome_refund(self, pool: TokenPool) -> None:
        """process_bid_outcome should refund tokens."""
        # Simulate spending tokens on a bid first
        pool.spend("user1", Decimal("10"))  # Balance now 0

        # Process refund
        result = pool.process_bid_outcome("user1", "bid-123", refund_tokens=5)

        assert result is not None
        assert result.amount == Decimal("5")
        assert result.new_balance == Decimal("5")
        assert "bid_outcome:bid-123" in result.reason

    def test_process_bid_outcome_no_refund(self, pool: TokenPool) -> None:
        """process_bid_outcome with 0 refund should return None."""
        result = pool.process_bid_outcome("user1", "bid-456", refund_tokens=0)
        assert result is None


# =============================================================================
# AsyncTokenPool Tests
# =============================================================================


class TestAsyncTokenPool:
    """Tests for AsyncTokenPool thread-safe wrapper."""

    @pytest.mark.asyncio
    async def test_async_get_balance(self) -> None:
        """Async get_balance should work."""
        pool = AsyncTokenPool()
        balance = await pool.get_balance("user1")
        assert balance.balance == Decimal("10")

    @pytest.mark.asyncio
    async def test_async_watch_session(self) -> None:
        """Async watch session operations should work."""
        pool = AsyncTokenPool()
        pool._pool._min_watch_seconds = 0  # Disable for test

        started = await pool.start_watching("user1")
        assert started
        assert pool.is_watching("user1")

        # Wait and accrue
        start = datetime.now() - timedelta(minutes=1)
        pool._pool._balances["user1"].watch_session_start = start

        result = await pool.stop_watching("user1")
        assert result is not None
        assert result.tokens_accrued >= Decimal("0.9")

    @pytest.mark.asyncio
    async def test_async_spend(self) -> None:
        """Async spend should work."""
        pool = AsyncTokenPool()
        result = await pool.spend("user1", Decimal("5"))
        assert result.success
        assert result.new_balance == Decimal("5")

    @pytest.mark.asyncio
    async def test_async_manifest(self) -> None:
        """Async manifest should work."""
        pool = AsyncTokenPool()
        manifest = await pool.manifest("user1")
        assert manifest["path"] == "self.tokens"
        assert manifest["balance"] == "10"


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_token_pool_default(self) -> None:
        """create_token_pool should create pool with defaults."""
        pool = create_token_pool()
        balance = pool.get_balance("user1")
        assert balance.balance == Decimal("10")

    def test_create_token_pool_custom_grant(self) -> None:
        """create_token_pool should respect custom initial grant."""
        pool = create_token_pool(initial_grant=Decimal("100"))
        balance = pool.get_balance("user1")
        assert balance.balance == Decimal("100")

    def test_create_token_pool_custom_tier_provider(self) -> None:
        """create_token_pool should accept custom tier provider."""
        provider = LicenseTierProvider()
        provider.set_tier("user1", AccrualTier.ENTERPRISE)

        pool = create_token_pool(tier_provider=provider)
        pool._min_watch_seconds = 0

        start = datetime.now() - timedelta(minutes=1)
        pool.start_watching("user1", timestamp=start)
        result = pool.stop_watching("user1")

        assert result is not None
        assert result.tier == AccrualTier.ENTERPRISE

    def test_create_async_token_pool(self) -> None:
        """create_async_token_pool should create AsyncTokenPool."""
        pool = create_async_token_pool()
        assert isinstance(pool, AsyncTokenPool)


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_exception_hierarchy(self) -> None:
        """All custom exceptions should inherit from TokenPoolError."""
        assert issubclass(InvalidUserError, TokenPoolError)
        assert issubclass(InvalidAmountError, TokenPoolError)
        assert issubclass(InsufficientBalanceError, TokenPoolError)
        assert issubclass(SessionError, TokenPoolError)

    def test_insufficient_balance_error_attributes(self) -> None:
        """InsufficientBalanceError should have useful attributes."""
        err = InsufficientBalanceError("user1", Decimal("100"), Decimal("10"))
        assert err.user_id == "user1"
        assert err.required == Decimal("100")
        assert err.available == Decimal("10")
        assert "user1" in str(err)
        assert "100" in str(err)
        assert "10" in str(err)

    def test_256_char_user_id_allowed(self, pool: TokenPool) -> None:
        """user_id of exactly 256 chars should be allowed."""
        user_id = "x" * 256
        balance = pool.get_balance(user_id)
        assert balance.user_id == user_id

    def test_accrual_result_includes_session_id(self, pool_no_min_watch: TokenPool) -> None:
        """AccrualResult should include session_id."""
        start = datetime.now() - timedelta(minutes=1)
        pool_no_min_watch.start_watching("user1", timestamp=start, session_id="sess-1")
        result = pool_no_min_watch.stop_watching("user1")

        assert result is not None
        assert result.session_id == "sess-1"
