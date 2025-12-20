"""
TokenPool: Spectator Economy for Atelier

The TokenPool manages per-user token balances for the Atelier spectator economy.
Tokens accrue while watching creators work, with tier-based multipliers.

Accrual Rates (per minute watching):
- FREE: 1.0x (1 token/minute)
- PRO: 2.5x (2.5 tokens/minute)
- TEAMS: 3.5x (3.5 tokens/minute)
- ENTERPRISE: 5.0x (5 tokens/minute)

Integration Points:
- protocols/licensing/tiers.py: LicenseTier enum for tier lookup
- agents/atelier/bidding.py: Deduct tokens for bids, handle refunds
- self.tokens.manifest: AGENTESE path for balance queries
- self.tokens.purchase: AGENTESE path for Stripe token purchases

Thread Safety:
- TokenPool provides synchronous methods for simple use cases
- AsyncTokenPool provides async methods with proper locking for concurrent access

From Bataille: Tokens are the crystallization of attention—
the "accursed share" that must be spent to maintain flow.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_DOWN, Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Protocol

if TYPE_CHECKING:
    from agents.atelier.bidding import Bid, BidResult, BidType
    from protocols.licensing.tiers import LicenseTier


# =============================================================================
# Exceptions
# =============================================================================


class TokenPoolError(Exception):
    """Base exception for TokenPool errors."""

    pass


class InvalidUserError(TokenPoolError):
    """Raised when user_id is invalid."""

    pass


class InvalidAmountError(TokenPoolError):
    """Raised when amount is invalid (negative, NaN, etc.)."""

    pass


class InsufficientBalanceError(TokenPoolError):
    """Raised when balance is insufficient for operation."""

    def __init__(self, user_id: str, required: Decimal, available: Decimal) -> None:
        self.user_id = user_id
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient balance for {user_id}: required {required}, available {available}"
        )


class SessionError(TokenPoolError):
    """Raised for watch session errors."""

    pass


# =============================================================================
# Tier Multipliers
# =============================================================================


class AccrualTier(Enum):
    """Token accrual tiers with multipliers."""

    FREE = "FREE"
    PRO = "PRO"
    TEAMS = "TEAMS"
    ENTERPRISE = "ENTERPRISE"

    @property
    def multiplier(self) -> Decimal:
        """Get the accrual multiplier for this tier."""
        return TIER_MULTIPLIERS[self]


# Multipliers per tier (tokens per minute)
TIER_MULTIPLIERS: dict[AccrualTier, Decimal] = {
    AccrualTier.FREE: Decimal("1.0"),
    AccrualTier.PRO: Decimal("2.5"),
    AccrualTier.TEAMS: Decimal("3.5"),
    AccrualTier.ENTERPRISE: Decimal("5.0"),
}

# Base accrual rate: 1 token per minute
BASE_ACCRUAL_RATE = Decimal("1.0")

# Minimum watch time to accrue tokens (prevent micro-farming)
MIN_WATCH_SECONDS = 30


# =============================================================================
# Tier Lookup Protocol
# =============================================================================


class TierProvider(Protocol):
    """Protocol for looking up user tiers."""

    def get_tier(self, user_id: str) -> AccrualTier:
        """Get the accrual tier for a user."""
        ...


class DefaultTierProvider:
    """Default tier provider that returns FREE for all users."""

    def get_tier(self, user_id: str) -> AccrualTier:
        """All users default to FREE tier."""
        return AccrualTier.FREE


class LicenseTierProvider:
    """Tier provider that maps LicenseTier to AccrualTier."""

    def __init__(self) -> None:
        """Initialize with lazy import of licensing."""
        self._tier_cache: dict[str, AccrualTier] = {}

    def get_tier(self, user_id: str) -> AccrualTier:
        """Look up tier from licensing system."""
        if user_id in self._tier_cache:
            return self._tier_cache[user_id]
        # Default to FREE if not in cache
        return AccrualTier.FREE

    def set_tier(self, user_id: str, tier: AccrualTier) -> None:
        """Set a user's tier (for testing or manual override)."""
        self._tier_cache[user_id] = tier

    def set_tier_from_license(self, user_id: str, license_tier: "LicenseTier") -> None:
        """Map a LicenseTier to AccrualTier."""
        mapping = {
            "FREE": AccrualTier.FREE,
            "PRO": AccrualTier.PRO,
            "TEAMS": AccrualTier.TEAMS,
            "ENTERPRISE": AccrualTier.ENTERPRISE,
        }
        self._tier_cache[user_id] = mapping.get(license_tier.name, AccrualTier.FREE)


# =============================================================================
# Validation Helpers
# =============================================================================


def _validate_user_id(user_id: str) -> None:
    """Validate user_id is non-empty string."""
    if not user_id or not isinstance(user_id, str):
        raise InvalidUserError(f"Invalid user_id: {user_id!r}")
    if len(user_id) > 256:
        raise InvalidUserError(f"user_id too long: {len(user_id)} chars (max 256)")


def _validate_amount(amount: Decimal, allow_zero: bool = False) -> None:
    """Validate amount is a valid positive Decimal."""
    if not isinstance(amount, Decimal):
        raise InvalidAmountError(f"Amount must be Decimal, got {type(amount).__name__}")
    if amount.is_nan() or amount.is_infinite():
        raise InvalidAmountError(f"Amount must be finite, got {amount}")
    if amount < 0:
        raise InvalidAmountError(f"Amount must be non-negative, got {amount}")
    if not allow_zero and amount == 0:
        raise InvalidAmountError("Amount must be positive")


# =============================================================================
# User Balance
# =============================================================================


@dataclass
class UserBalance:
    """
    Token balance for a single user.

    Tracks:
    - Current balance (fractional tokens allowed)
    - Total accrued over lifetime
    - Total spent over lifetime
    - Watch session tracking for accrual
    - Session-specific tracking for SpectatorStats sync
    """

    user_id: str
    balance: Decimal = field(default_factory=lambda: Decimal("0"))
    total_accrued: Decimal = field(default_factory=lambda: Decimal("0"))
    total_spent: Decimal = field(default_factory=lambda: Decimal("0"))
    total_refunded: Decimal = field(default_factory=lambda: Decimal("0"))
    created_at: datetime = field(default_factory=datetime.now)
    last_accrual_at: Optional[datetime] = None
    watch_session_start: Optional[datetime] = None
    # Session tracking for SpectatorStats sync
    current_session_id: Optional[str] = None
    session_watch_seconds: float = 0.0

    @property
    def whole_tokens(self) -> int:
        """Get integer token count (floor)."""
        return int(self.balance.quantize(Decimal("1"), rounding=ROUND_DOWN))

    def can_spend(self, amount: Decimal) -> bool:
        """Check if user can spend the given amount."""
        return self.balance >= amount

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage/API."""
        return {
            "user_id": self.user_id,
            "balance": str(self.balance),
            "whole_tokens": self.whole_tokens,
            "total_accrued": str(self.total_accrued),
            "total_spent": str(self.total_spent),
            "total_refunded": str(self.total_refunded),
            "created_at": self.created_at.isoformat(),
            "last_accrual_at": (self.last_accrual_at.isoformat() if self.last_accrual_at else None),
            "watching": self.watch_session_start is not None,
            "current_session_id": self.current_session_id,
            "session_watch_seconds": self.session_watch_seconds,
        }


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class AccrualResult:
    """Result of a token accrual operation."""

    user_id: str
    tokens_accrued: Decimal
    new_balance: Decimal
    minutes_watched: Decimal
    tier: AccrualTier
    multiplier: Decimal
    session_id: Optional[str] = None


@dataclass
class SpendResult:
    """Result of a token spend operation."""

    success: bool
    user_id: str
    amount: Decimal
    new_balance: Decimal
    reason: Optional[str] = None


@dataclass
class RefundResult:
    """Result of a token refund operation."""

    user_id: str
    amount: Decimal
    new_balance: Decimal
    reason: str


# =============================================================================
# Token Pool
# =============================================================================


class TokenPool:
    """
    Token pool for managing spectator economy.

    Features:
    - Per-user balance tracking
    - Time-based accrual with tier multipliers
    - Input validation and error handling
    - Integration with AGENTESE self.tokens.* paths
    - Integration with bidding system (deduct/refund)

    Note: This class is NOT thread-safe. For concurrent access,
    use AsyncTokenPool instead.

    Usage:
        pool = TokenPool()
        pool.start_watching("user123", session_id="session-abc")
        # ... time passes ...
        result = pool.accrue("user123")
        pool.stop_watching("user123")
    """

    def __init__(
        self,
        tier_provider: Optional[TierProvider] = None,
        initial_grant: Decimal = Decimal("10"),
        min_watch_seconds: float = MIN_WATCH_SECONDS,
    ) -> None:
        """
        Initialize token pool.

        Args:
            tier_provider: Provider for user tier lookup
            initial_grant: Tokens granted to new users (must be >= 0)
            min_watch_seconds: Minimum watch time before accrual
        """
        if initial_grant < 0:
            raise InvalidAmountError(f"initial_grant must be >= 0, got {initial_grant}")

        self._balances: dict[str, UserBalance] = {}
        self._tier_provider = tier_provider or DefaultTierProvider()
        self._initial_grant = initial_grant
        self._min_watch_seconds = min_watch_seconds

    # -------------------------------------------------------------------------
    # Balance Management
    # -------------------------------------------------------------------------

    def get_balance(self, user_id: str) -> UserBalance:
        """
        Get balance for a user, creating if needed.

        New users receive an initial grant.

        Raises:
            InvalidUserError: If user_id is invalid
        """
        _validate_user_id(user_id)

        if user_id not in self._balances:
            self._balances[user_id] = UserBalance(
                user_id=user_id,
                balance=self._initial_grant,
                total_accrued=self._initial_grant,
            )
        return self._balances[user_id]

    def get_balance_amount(self, user_id: str) -> Decimal:
        """Get just the balance amount for a user."""
        return self.get_balance(user_id).balance

    def get_whole_tokens(self, user_id: str) -> int:
        """Get integer token count for a user."""
        return self.get_balance(user_id).whole_tokens

    def user_exists(self, user_id: str) -> bool:
        """Check if user exists in pool (without creating)."""
        return user_id in self._balances

    # -------------------------------------------------------------------------
    # Watch Session Tracking
    # -------------------------------------------------------------------------

    def start_watching(
        self,
        user_id: str,
        timestamp: Optional[datetime] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Start a watch session for a user.

        Args:
            user_id: User starting to watch
            timestamp: Optional start timestamp (defaults to now)
            session_id: Optional Atelier session ID for SpectatorStats sync

        Returns:
            True if session started, False if already watching

        Raises:
            InvalidUserError: If user_id is invalid
        """
        _validate_user_id(user_id)

        balance = self.get_balance(user_id)
        if balance.watch_session_start is not None:
            return False  # Already watching

        balance.watch_session_start = timestamp or datetime.now()
        balance.current_session_id = session_id
        balance.session_watch_seconds = 0.0
        return True

    def stop_watching(
        self, user_id: str, timestamp: Optional[datetime] = None
    ) -> Optional[AccrualResult]:
        """
        Stop watching and accrue tokens.

        Returns AccrualResult if tokens were accrued, None if not watching.
        """
        _validate_user_id(user_id)

        balance = self.get_balance(user_id)
        if balance.watch_session_start is None:
            return None  # Not watching

        result = self._accrue_tokens(balance, timestamp or datetime.now())
        balance.watch_session_start = None
        balance.current_session_id = None
        return result

    def is_watching(self, user_id: str) -> bool:
        """Check if user is currently watching."""
        if user_id not in self._balances:
            return False
        return self._balances[user_id].watch_session_start is not None

    def get_watch_session_info(self, user_id: str) -> Optional[dict[str, Any]]:
        """Get watch session info for a user, or None if not watching."""
        if user_id not in self._balances:
            return None
        balance = self._balances[user_id]
        if balance.watch_session_start is None:
            return None
        return {
            "user_id": user_id,
            "session_id": balance.current_session_id,
            "started_at": balance.watch_session_start.isoformat(),
            "elapsed_seconds": (datetime.now() - balance.watch_session_start).total_seconds(),
        }

    # -------------------------------------------------------------------------
    # Token Accrual
    # -------------------------------------------------------------------------

    def accrue(self, user_id: str, timestamp: Optional[datetime] = None) -> Optional[AccrualResult]:
        """
        Accrue tokens for a watching user without stopping the session.

        Useful for periodic accrual checkpoints.
        Returns None if not watching.
        """
        _validate_user_id(user_id)

        balance = self.get_balance(user_id)
        if balance.watch_session_start is None:
            return None

        now = timestamp or datetime.now()
        result = self._accrue_tokens(balance, now)
        # Reset session start to now (tokens already credited)
        balance.watch_session_start = now
        return result

    def _accrue_tokens(self, balance: UserBalance, end_time: datetime) -> AccrualResult:
        """
        Internal: Calculate and apply token accrual.

        Tokens = minutes_watched * base_rate * tier_multiplier

        Enforces minimum watch time to prevent micro-farming.
        """
        if balance.watch_session_start is None:
            raise SessionError("Cannot accrue without active watch session")

        # Calculate watch duration
        duration = end_time - balance.watch_session_start
        total_seconds = duration.total_seconds()

        # Enforce minimum watch time
        if total_seconds < self._min_watch_seconds:
            return AccrualResult(
                user_id=balance.user_id,
                tokens_accrued=Decimal("0"),
                new_balance=balance.balance,
                minutes_watched=Decimal("0"),
                tier=self._tier_provider.get_tier(balance.user_id),
                multiplier=Decimal("0"),
                session_id=balance.current_session_id,
            )

        # Clamp negative duration (clock drift edge case)
        if total_seconds < 0:
            total_seconds = 0

        minutes = Decimal(str(total_seconds)) / Decimal("60")

        # Get tier and multiplier
        tier = self._tier_provider.get_tier(balance.user_id)
        multiplier = tier.multiplier

        # Calculate tokens: minutes * base_rate * multiplier
        tokens = minutes * BASE_ACCRUAL_RATE * multiplier

        # Apply to balance
        balance.balance += tokens
        balance.total_accrued += tokens
        balance.last_accrual_at = end_time
        balance.session_watch_seconds += total_seconds

        return AccrualResult(
            user_id=balance.user_id,
            tokens_accrued=tokens,
            new_balance=balance.balance,
            minutes_watched=minutes,
            tier=tier,
            multiplier=multiplier,
            session_id=balance.current_session_id,
        )

    def grant(self, user_id: str, amount: Decimal, reason: str = "grant") -> Decimal:
        """
        Grant tokens to a user (admin/purchase).

        Args:
            user_id: User to grant tokens to
            amount: Amount to grant (must be positive)
            reason: Reason for grant (for logging)

        Returns:
            New balance

        Raises:
            InvalidUserError: If user_id is invalid
            InvalidAmountError: If amount is invalid
        """
        _validate_user_id(user_id)
        _validate_amount(amount)

        balance = self.get_balance(user_id)
        balance.balance += amount
        balance.total_accrued += amount
        return balance.balance

    # -------------------------------------------------------------------------
    # Token Spending
    # -------------------------------------------------------------------------

    def spend(self, user_id: str, amount: Decimal, reason: str = "spend") -> SpendResult:
        """
        Spend tokens from a user's balance.

        Args:
            user_id: User to deduct from
            amount: Amount to spend (must be positive)
            reason: Reason for spend (for logging)

        Returns:
            SpendResult indicating success/failure

        Raises:
            InvalidUserError: If user_id is invalid
            InvalidAmountError: If amount is invalid
        """
        _validate_user_id(user_id)
        _validate_amount(amount)

        balance = self.get_balance(user_id)

        if not balance.can_spend(amount):
            return SpendResult(
                success=False,
                user_id=user_id,
                amount=amount,
                new_balance=balance.balance,
                reason=f"Insufficient balance: {balance.balance} < {amount}",
            )

        balance.balance -= amount
        balance.total_spent += amount

        return SpendResult(
            success=True,
            user_id=user_id,
            amount=amount,
            new_balance=balance.balance,
        )

    def spend_or_raise(self, user_id: str, amount: Decimal, reason: str = "spend") -> Decimal:
        """
        Spend tokens, raising exception on failure.

        Args:
            user_id: User to deduct from
            amount: Amount to spend

        Returns:
            New balance

        Raises:
            InsufficientBalanceError: If balance is insufficient
        """
        result = self.spend(user_id, amount, reason)
        if not result.success:
            raise InsufficientBalanceError(user_id, amount, result.new_balance)
        return result.new_balance

    def refund(self, user_id: str, amount: Decimal, reason: str = "refund") -> RefundResult:
        """
        Refund tokens to a user (e.g., from rejected/acknowledged bid).

        Unlike grant(), this tracks refunds separately and doesn't
        count toward total_accrued.

        Args:
            user_id: User to refund
            amount: Amount to refund
            reason: Reason for refund

        Returns:
            RefundResult with new balance
        """
        _validate_user_id(user_id)
        _validate_amount(amount, allow_zero=True)

        if amount == 0:
            balance = self.get_balance(user_id)
            return RefundResult(
                user_id=user_id,
                amount=Decimal("0"),
                new_balance=balance.balance,
                reason=reason,
            )

        balance = self.get_balance(user_id)
        balance.balance += amount
        balance.total_refunded += amount

        return RefundResult(
            user_id=user_id,
            amount=amount,
            new_balance=balance.balance,
            reason=reason,
        )

    def transfer(
        self, from_user: str, to_user: str, amount: Decimal
    ) -> tuple[SpendResult, Optional[Decimal]]:
        """
        Transfer tokens between users.

        Args:
            from_user: Sender user ID
            to_user: Recipient user ID
            amount: Amount to transfer

        Returns:
            (spend_result, recipient_new_balance or None on failure)
        """
        _validate_user_id(from_user)
        _validate_user_id(to_user)
        _validate_amount(amount)

        if from_user == to_user:
            raise InvalidUserError("Cannot transfer to self")

        spend_result = self.spend(from_user, amount, reason=f"transfer to {to_user}")
        if not spend_result.success:
            return spend_result, None

        new_balance = self.grant(to_user, amount, reason=f"transfer from {from_user}")
        return spend_result, new_balance

    # -------------------------------------------------------------------------
    # Bidding Integration
    # -------------------------------------------------------------------------

    def process_bid(
        self,
        user_id: str,
        bid_type: "BidType",
        session_id: str,
        content: str,
    ) -> tuple[SpendResult, Optional["Bid"]]:
        """
        Process a bid by deducting tokens and creating the Bid object.

        This is the integration point with agents/atelier/bidding.py.
        Call this BEFORE submitting to BidQueue.

        Args:
            user_id: Spectator making the bid
            bid_type: Type of bid (determines cost)
            session_id: Atelier session ID
            content: Bid content

        Returns:
            (spend_result, Bid if successful or None)
        """
        from agents.atelier.bidding import BID_COSTS, Bid

        cost = Decimal(BID_COSTS[bid_type])
        spend_result = self.spend(user_id, cost, reason=f"bid:{bid_type.name}")

        if not spend_result.success:
            return spend_result, None

        bid = Bid.create(
            spectator_id=user_id,
            session_id=session_id,
            bid_type=bid_type,
            content=content,
        )

        return spend_result, bid

    def process_bid_outcome(
        self, user_id: str, bid_id: str, refund_tokens: int
    ) -> Optional[RefundResult]:
        """
        Process bid outcome by handling refunds.

        Called after BidQueue.record_outcome() to refund tokens
        for acknowledged/ignored/rejected bids.

        Args:
            user_id: User who made the bid
            bid_id: ID of the bid
            refund_tokens: Number of tokens to refund

        Returns:
            RefundResult if refund was applied, None if no refund
        """
        if refund_tokens <= 0:
            return None

        return self.refund(
            user_id,
            Decimal(refund_tokens),
            reason=f"bid_outcome:{bid_id}",
        )

    # -------------------------------------------------------------------------
    # Queries
    # -------------------------------------------------------------------------

    def get_all_users(self) -> list[str]:
        """Get all user IDs with balances."""
        return list(self._balances.keys())

    def get_total_supply(self) -> Decimal:
        """Get total token supply across all users."""
        if not self._balances:
            return Decimal("0")
        return sum(b.balance for b in self._balances.values())

    def get_leaderboard(self, limit: int = 10) -> list[UserBalance]:
        """Get top users by balance."""
        sorted_balances = sorted(self._balances.values(), key=lambda b: b.balance, reverse=True)
        return sorted_balances[:limit]

    def get_active_watchers(self) -> list[str]:
        """Get list of currently watching users."""
        return [uid for uid, b in self._balances.items() if b.watch_session_start is not None]

    def get_session_watchers(self, session_id: str) -> list[str]:
        """Get users watching a specific session."""
        return [uid for uid, b in self._balances.items() if b.current_session_id == session_id]

    # -------------------------------------------------------------------------
    # AGENTESE Integration
    # -------------------------------------------------------------------------

    def manifest(self, user_id: str) -> dict[str, Any]:
        """
        AGENTESE: self.tokens.manifest

        Returns user's token state for rendering.
        """
        _validate_user_id(user_id)

        balance = self.get_balance(user_id)
        tier = self._tier_provider.get_tier(user_id)

        return {
            "path": "self.tokens",
            "aspect": "manifest",
            "user_id": user_id,
            "balance": str(balance.balance),
            "whole_tokens": balance.whole_tokens,
            "tier": tier.value,
            "multiplier": str(tier.multiplier),
            "watching": balance.watch_session_start is not None,
            "current_session": balance.current_session_id,
            "total_accrued": str(balance.total_accrued),
            "total_spent": str(balance.total_spent),
            "total_refunded": str(balance.total_refunded),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize entire pool state."""
        return {
            "users": {uid: b.to_dict() for uid, b in self._balances.items()},
            "total_supply": str(self.get_total_supply()),
            "active_watchers": len(self.get_active_watchers()),
            "user_count": len(self._balances),
        }


# =============================================================================
# Async Token Pool
# =============================================================================


class AsyncTokenPool:
    """
    Thread-safe async wrapper around TokenPool.

    Use this when accessing the token pool from multiple async tasks.

    Example:
        pool = AsyncTokenPool()
        await pool.start_watching("user123")
        result = await pool.accrue("user123")
        await pool.stop_watching("user123")
    """

    def __init__(
        self,
        tier_provider: Optional[TierProvider] = None,
        initial_grant: Decimal = Decimal("10"),
    ) -> None:
        self._pool = TokenPool(tier_provider=tier_provider, initial_grant=initial_grant)
        self._lock = asyncio.Lock()

    async def get_balance(self, user_id: str) -> UserBalance:
        async with self._lock:
            return self._pool.get_balance(user_id)

    async def get_balance_amount(self, user_id: str) -> Decimal:
        async with self._lock:
            return self._pool.get_balance_amount(user_id)

    async def start_watching(
        self,
        user_id: str,
        timestamp: Optional[datetime] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        async with self._lock:
            return self._pool.start_watching(user_id, timestamp, session_id)

    async def stop_watching(
        self, user_id: str, timestamp: Optional[datetime] = None
    ) -> Optional[AccrualResult]:
        async with self._lock:
            return self._pool.stop_watching(user_id, timestamp)

    async def accrue(
        self, user_id: str, timestamp: Optional[datetime] = None
    ) -> Optional[AccrualResult]:
        async with self._lock:
            return self._pool.accrue(user_id, timestamp)

    async def spend(self, user_id: str, amount: Decimal, reason: str = "spend") -> SpendResult:
        async with self._lock:
            return self._pool.spend(user_id, amount, reason)

    async def grant(self, user_id: str, amount: Decimal, reason: str = "grant") -> Decimal:
        async with self._lock:
            return self._pool.grant(user_id, amount, reason)

    async def refund(self, user_id: str, amount: Decimal, reason: str = "refund") -> RefundResult:
        async with self._lock:
            return self._pool.refund(user_id, amount, reason)

    async def transfer(
        self, from_user: str, to_user: str, amount: Decimal
    ) -> tuple[SpendResult, Optional[Decimal]]:
        async with self._lock:
            return self._pool.transfer(from_user, to_user, amount)

    async def process_bid(
        self,
        user_id: str,
        bid_type: "BidType",
        session_id: str,
        content: str,
    ) -> tuple[SpendResult, Optional["Bid"]]:
        async with self._lock:
            return self._pool.process_bid(user_id, bid_type, session_id, content)

    async def process_bid_outcome(
        self, user_id: str, bid_id: str, refund_tokens: int
    ) -> Optional[RefundResult]:
        async with self._lock:
            return self._pool.process_bid_outcome(user_id, bid_id, refund_tokens)

    async def manifest(self, user_id: str) -> dict[str, Any]:
        async with self._lock:
            return self._pool.manifest(user_id)

    async def to_dict(self) -> dict[str, Any]:
        async with self._lock:
            return self._pool.to_dict()

    def is_watching(self, user_id: str) -> bool:
        """Sync method - safe to call without lock for read-only check."""
        return self._pool.is_watching(user_id)

    def get_all_users(self) -> list[str]:
        """Sync method - safe for read-only access."""
        return self._pool.get_all_users()


# =============================================================================
# Factory Functions
# =============================================================================


def create_token_pool(
    tier_provider: Optional[TierProvider] = None,
    initial_grant: Decimal = Decimal("10"),
) -> TokenPool:
    """Create a TokenPool with optional tier provider."""
    return TokenPool(tier_provider=tier_provider, initial_grant=initial_grant)


def create_async_token_pool(
    tier_provider: Optional[TierProvider] = None,
    initial_grant: Decimal = Decimal("10"),
) -> AsyncTokenPool:
    """Create a thread-safe AsyncTokenPool."""
    return AsyncTokenPool(tier_provider=tier_provider, initial_grant=initial_grant)


def create_token_pool_with_licensing() -> TokenPool:
    """Create a TokenPool integrated with the licensing system."""
    return TokenPool(tier_provider=LicenseTierProvider())
