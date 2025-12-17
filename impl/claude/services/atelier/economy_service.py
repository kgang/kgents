"""
Atelier Economy Service: TokenPool wrapper for spectator economy.

Wraps agents/atelier/economy.py TokenPool with async-friendly service interface.
Owns domain semantics for Atelier token economy:
- WHEN to accrue (watching workshops, participating in festivals)
- WHY to spend (bidding on constraints, boosting builders)
- HOW to integrate (AGENTESE paths, Stripe purchases)

AGENTESE aspects exposed:
- world.atelier.tokens.manifest - Get balance
- world.atelier.tokens.spend - Spend tokens
- world.atelier.tokens.grant - Admin token grant
- world.atelier.tokens.purchase - Stripe integration (future)

From Bataille: Tokens are the crystallization of attention—
the "accursed share" that must be spent to maintain flow.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from agents.atelier.economy import (
    AccrualResult,
    AccrualTier,
    AsyncTokenPool,
    LicenseTierProvider,
    RefundResult,
    SpendResult,
    TokenPool,
    UserBalance,
    create_async_token_pool,
)

if TYPE_CHECKING:
    from agents.atelier.bidding import Bid, BidType


@dataclass
class TokenBalanceView:
    """View of a user's token balance."""

    user_id: str
    balance: Decimal
    whole_tokens: int
    tier: str
    multiplier: Decimal
    is_watching: bool
    current_session: str | None
    total_accrued: Decimal
    total_spent: Decimal
    total_refunded: Decimal

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "balance": str(self.balance),
            "whole_tokens": self.whole_tokens,
            "tier": self.tier,
            "multiplier": str(self.multiplier),
            "is_watching": self.is_watching,
            "current_session": self.current_session,
            "total_accrued": str(self.total_accrued),
            "total_spent": str(self.total_spent),
            "total_refunded": str(self.total_refunded),
        }

    def to_text(self) -> str:
        lines = [
            f"Token Balance for {self.user_id}",
            "=" * 30,
            f"Balance: {self.whole_tokens} tokens ({self.balance})",
            f"Tier: {self.tier} ({self.multiplier}x)",
            f"Watching: {self.is_watching}",
        ]
        if self.current_session:
            lines.append(f"Session: {self.current_session}")
        lines.extend(
            [
                f"Total Accrued: {self.total_accrued}",
                f"Total Spent: {self.total_spent}",
                f"Total Refunded: {self.total_refunded}",
            ]
        )
        return "\n".join(lines)


@dataclass
class EconomyStatusView:
    """View of overall economy status."""

    total_supply: Decimal
    active_watchers: int
    user_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_supply": str(self.total_supply),
            "active_watchers": self.active_watchers,
            "user_count": self.user_count,
        }

    def to_text(self) -> str:
        return (
            f"Economy Status: {self.total_supply} total supply, "
            f"{self.active_watchers} watchers, {self.user_count} users"
        )


class AtelierEconomyService:
    """
    Service layer for Atelier spectator economy.

    Wraps AsyncTokenPool with service-level methods for:
    - Balance management
    - Watch session tracking
    - Token spending/granting
    - Bid processing integration

    Usage:
        service = AtelierEconomyService.create()

        # Start watching
        await service.start_watching("user123", session_id="workshop-abc")

        # Get balance
        balance = await service.get_balance("user123")

        # Stop watching (accrues tokens)
        result = await service.stop_watching("user123")
    """

    def __init__(self, pool: AsyncTokenPool) -> None:
        """
        Initialize with an AsyncTokenPool.

        Args:
            pool: The underlying token pool
        """
        self._pool = pool

    @classmethod
    def create(
        cls,
        initial_grant: Decimal = Decimal("10"),
        with_licensing: bool = False,
    ) -> "AtelierEconomyService":
        """
        Factory method to create a new economy service.

        Args:
            initial_grant: Initial tokens for new users
            with_licensing: Whether to integrate with licensing tiers

        Returns:
            New AtelierEconomyService instance
        """
        tier_provider = LicenseTierProvider() if with_licensing else None
        pool = create_async_token_pool(
            tier_provider=tier_provider,
            initial_grant=initial_grant,
        )
        return cls(pool)

    # === Balance Operations ===

    async def get_balance(self, user_id: str) -> TokenBalanceView:
        """
        Get balance for a user.

        Args:
            user_id: User identifier

        Returns:
            TokenBalanceView with balance details
        """
        balance = await self._pool.get_balance(user_id)
        manifest = await self._pool.manifest(user_id)

        return TokenBalanceView(
            user_id=user_id,
            balance=balance.balance,
            whole_tokens=balance.whole_tokens,
            tier=manifest["tier"],
            multiplier=Decimal(manifest["multiplier"]),
            is_watching=manifest["watching"],
            current_session=manifest.get("current_session"),
            total_accrued=balance.total_accrued,
            total_spent=balance.total_spent,
            total_refunded=balance.total_refunded,
        )

    async def get_balance_amount(self, user_id: str) -> Decimal:
        """Get just the balance amount for a user."""
        return await self._pool.get_balance_amount(user_id)

    async def get_whole_tokens(self, user_id: str) -> int:
        """Get integer token count for a user."""
        balance = await self._pool.get_balance(user_id)
        return balance.whole_tokens

    # === Watch Session Operations ===

    async def start_watching(
        self,
        user_id: str,
        session_id: str | None = None,
    ) -> bool:
        """
        Start a watch session for a user.

        Args:
            user_id: User starting to watch
            session_id: Optional Atelier session ID

        Returns:
            True if session started, False if already watching
        """
        return await self._pool.start_watching(user_id, session_id=session_id)

    async def stop_watching(
        self,
        user_id: str,
    ) -> AccrualResult | None:
        """
        Stop watching and accrue tokens.

        Args:
            user_id: User stopping watch

        Returns:
            AccrualResult if tokens were accrued, None if not watching
        """
        return await self._pool.stop_watching(user_id)

    async def accrue(
        self,
        user_id: str,
    ) -> AccrualResult | None:
        """
        Checkpoint accrual without stopping session.

        Args:
            user_id: User to accrue for

        Returns:
            AccrualResult if tokens were accrued, None if not watching
        """
        return await self._pool.accrue(user_id)

    def is_watching(self, user_id: str) -> bool:
        """Check if user is currently watching."""
        return self._pool.is_watching(user_id)

    # === Token Operations ===

    async def spend(
        self,
        user_id: str,
        amount: Decimal,
        reason: str = "spend",
    ) -> SpendResult:
        """
        Spend tokens from a user's balance.

        Args:
            user_id: User to deduct from
            amount: Amount to spend
            reason: Reason for spend

        Returns:
            SpendResult indicating success/failure
        """
        return await self._pool.spend(user_id, amount, reason)

    async def grant(
        self,
        user_id: str,
        amount: Decimal,
        reason: str = "grant",
    ) -> Decimal:
        """
        Grant tokens to a user.

        Args:
            user_id: User to grant tokens to
            amount: Amount to grant
            reason: Reason for grant

        Returns:
            New balance
        """
        return await self._pool.grant(user_id, amount, reason)

    async def refund(
        self,
        user_id: str,
        amount: Decimal,
        reason: str = "refund",
    ) -> RefundResult:
        """
        Refund tokens to a user.

        Args:
            user_id: User to refund
            amount: Amount to refund
            reason: Reason for refund

        Returns:
            RefundResult with new balance
        """
        return await self._pool.refund(user_id, amount, reason)

    async def transfer(
        self,
        from_user: str,
        to_user: str,
        amount: Decimal,
    ) -> tuple[SpendResult, Decimal | None]:
        """
        Transfer tokens between users.

        Args:
            from_user: Sender user ID
            to_user: Recipient user ID
            amount: Amount to transfer

        Returns:
            (spend_result, recipient_new_balance or None on failure)
        """
        return await self._pool.transfer(from_user, to_user, amount)

    # === Bid Integration ===

    async def process_bid(
        self,
        user_id: str,
        bid_type: "BidType",
        session_id: str,
        content: str,
    ) -> tuple[SpendResult, "Bid | None"]:
        """
        Process a bid by deducting tokens and creating the Bid object.

        Args:
            user_id: Spectator making the bid
            bid_type: Type of bid (determines cost)
            session_id: Atelier session ID
            content: Bid content

        Returns:
            (spend_result, Bid if successful or None)
        """
        return await self._pool.process_bid(user_id, bid_type, session_id, content)

    # === Status Operations ===

    async def manifest(self, user_id: str) -> dict[str, Any]:
        """
        AGENTESE manifest for user's token state.

        Args:
            user_id: User to manifest

        Returns:
            Token state dict
        """
        return await self._pool.manifest(user_id)

    async def status(self) -> EconomyStatusView:
        """
        Get overall economy status.

        Returns:
            EconomyStatusView with aggregate stats
        """
        data = await self._pool.to_dict()
        return EconomyStatusView(
            total_supply=Decimal(data["total_supply"]),
            active_watchers=data["active_watchers"],
            user_count=data["user_count"],
        )

    def get_all_users(self) -> list[str]:
        """Get all user IDs with balances."""
        return self._pool.get_all_users()

    @property
    def pool(self) -> AsyncTokenPool:
        """Access the underlying token pool."""
        return self._pool


__all__ = [
    "AtelierEconomyService",
    "TokenBalanceView",
    "EconomyStatusView",
]
