"""
TelegramNotifier: Kent's Motivation Loop.

Push notifications to Telegram when revenue events occur.
The dopamine hit of seeing "💰 $9.99 subscription!" keeps motivation high.

Integration Points:
- Stripe webhooks → TelegramNotifier.notify_payment()
- BudgetStore subscription updates → TelegramNotifier.notify_subscription()
- ActionMetrics aggregates → TelegramNotifier.notify_milestone()

Usage:
    notifier = TelegramNotifier()
    await notifier.notify_payment(user_id="u123", amount=9.99, tier="RESIDENT")

Environment Variables:
    TELEGRAM_BOT_TOKEN: Bot token from @BotFather
    TELEGRAM_CHAT_ID: Chat ID to send notifications to
    TELEGRAM_ENABLED: Set to "true" to enable (defaults to disabled)

See: plans/agent-town/builders-workshop.md
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class TelegramConfig:
    """Configuration for Telegram notifications."""

    bot_token: str = ""
    chat_id: str = ""
    enabled: bool = False

    # Rate limiting
    min_interval_seconds: float = 1.0  # Prevent spam
    max_messages_per_minute: int = 30

    # Message templates
    payment_template: str = "💰 **Payment Received**\n\nUser: `{user_id}`\nAmount: ${amount:.2f}\nTier: {tier}\n\n🎉 Revenue grows!"
    subscription_template: str = "🔔 **New Subscriber**\n\nUser: `{user_id}`\nTier: **{tier}**\nRenews: {renews_at}\n\n📈 MRR increasing!"
    milestone_template: str = "🏆 **Milestone Reached**\n\n{milestone}\n\nTotal: ${total:.2f}\nSubscribers: {subscribers}\n\n🚀 Keep building!"
    error_template: str = "⚠️ **Alert**\n\n{message}\n\nTime: {timestamp}"

    @classmethod
    def from_env(cls) -> "TelegramConfig":
        """Load configuration from environment variables."""
        return cls(
            bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
            enabled=os.environ.get("TELEGRAM_ENABLED", "").lower() == "true",
        )


# =============================================================================
# TelegramNotifier
# =============================================================================


class TelegramNotifier:
    """
    Push notifications to Telegram for revenue events.

    Kent's Motivation Loop:
    1. User subscribes → Stripe webhook fires
    2. Webhook handler calls TelegramNotifier.notify_payment()
    3. Kent's phone buzzes with "💰 $9.99!"
    4. Dopamine hit → keep building

    Graceful Degradation:
    - If Telegram credentials not set: logs warning, returns success
    - If Telegram API fails: logs error, returns failure
    - Rate limited to prevent spam

    Example:
        notifier = TelegramNotifier.from_env()
        if notifier.is_enabled:
            await notifier.notify_payment("user123", 9.99, "RESIDENT")
    """

    def __init__(self, config: TelegramConfig | None = None) -> None:
        """
        Initialize the notifier.

        Args:
            config: Configuration (loads from env if None)
        """
        self.config = config or TelegramConfig.from_env()
        self._last_message_time: float = 0.0
        self._messages_this_minute: int = 0
        self._minute_start: float = 0.0

    @classmethod
    def from_env(cls) -> "TelegramNotifier":
        """Create notifier from environment variables."""
        return cls(TelegramConfig.from_env())

    @property
    def is_enabled(self) -> bool:
        """Check if notifications are enabled and configured."""
        return self.config.enabled and bool(self.config.bot_token) and bool(self.config.chat_id)

    @property
    def is_configured(self) -> bool:
        """Check if credentials are configured (but maybe not enabled)."""
        return bool(self.config.bot_token) and bool(self.config.chat_id)

    def _check_rate_limit(self) -> bool:
        """
        Check if we're within rate limits.

        Returns True if we can send, False if rate limited.
        """
        import time

        now = time.time()

        # Reset minute counter if new minute
        if now - self._minute_start > 60:
            self._minute_start = now
            self._messages_this_minute = 0

        # Check limits
        if self._messages_this_minute >= self.config.max_messages_per_minute:
            return False

        if now - self._last_message_time < self.config.min_interval_seconds:
            return False

        return True

    def _record_message(self) -> None:
        """Record that a message was sent."""
        import time

        self._last_message_time = time.time()
        self._messages_this_minute += 1

    async def _send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message via Telegram Bot API.

        Args:
            text: Message text (supports Markdown)
            parse_mode: Parse mode (Markdown or HTML)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_enabled:
            logger.debug("Telegram notifications disabled, skipping")
            return True  # Return success to not block callers

        if not self._check_rate_limit():
            logger.warning("Telegram rate limit exceeded, skipping message")
            return False

        url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
        payload = {
            "chat_id": self.config.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            # Use aiohttp if available, fall back to httpx
            try:
                import aiohttp  # type: ignore[import-not-found]

                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, json=payload) as resp:
                        if resp.status == 200:
                            self._record_message()
                            logger.info(f"Telegram notification sent: {text[:50]}...")
                            return True
                        else:
                            error_text = await resp.text()
                            logger.error(f"Telegram API error: {resp.status} - {error_text}")
                            return False
            except ImportError:
                # Fall back to httpx
                try:
                    import httpx

                    async with httpx.AsyncClient(timeout=10.0) as client:
                        response = await client.post(url, json=payload)
                        if response.status_code == 200:
                            self._record_message()
                            logger.info(f"Telegram notification sent: {text[:50]}...")
                            return True
                        else:
                            logger.error(
                                f"Telegram API error: {response.status_code} - {response.text}"
                            )
                            return False
                except ImportError:
                    logger.error("No HTTP client available (need aiohttp or httpx)")
                    return False

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

    # =========================================================================
    # Public API
    # =========================================================================

    async def notify_payment(
        self,
        user_id: str,
        amount: float,
        tier: str,
        *,
        pack: str | None = None,
        credits: int | None = None,
    ) -> bool:
        """
        Notify about a successful payment.

        Args:
            user_id: User who paid
            amount: Payment amount in USD
            tier: Subscription tier or "CREDITS" for credit pack
            pack: Credit pack name (if credit purchase)
            credits: Number of credits purchased (if credit purchase)

        Returns:
            True if notification sent, False otherwise
        """
        if pack and credits:
            # Credit pack purchase
            text = (
                f"💰 **Credit Pack Sold!**\n\n"
                f"User: `{user_id}`\n"
                f"Pack: **{pack}**\n"
                f"Credits: {credits:,}\n"
                f"Amount: ${amount:.2f}\n\n"
                f"🎉 Tokens flowing!"
            )
        else:
            text = self.config.payment_template.format(
                user_id=user_id,
                amount=amount,
                tier=tier,
            )

        return await self._send_message(text)

    async def notify_subscription(
        self,
        user_id: str,
        tier: str,
        renews_at: datetime | str,
        *,
        is_upgrade: bool = False,
        previous_tier: str | None = None,
    ) -> bool:
        """
        Notify about a new or upgraded subscription.

        Args:
            user_id: User who subscribed
            tier: Subscription tier
            renews_at: Renewal date
            is_upgrade: Whether this is an upgrade from previous tier
            previous_tier: Previous tier (if upgrade)

        Returns:
            True if notification sent, False otherwise
        """
        if isinstance(renews_at, datetime):
            renews_str = renews_at.strftime("%Y-%m-%d")
        else:
            renews_str = str(renews_at)

        if is_upgrade and previous_tier:
            text = (
                f"⬆️ **Subscription Upgrade!**\n\n"
                f"User: `{user_id}`\n"
                f"From: {previous_tier}\n"
                f"To: **{tier}**\n"
                f"Renews: {renews_str}\n\n"
                f"📈 Value recognized!"
            )
        else:
            text = self.config.subscription_template.format(
                user_id=user_id,
                tier=tier,
                renews_at=renews_str,
            )

        return await self._send_message(text)

    async def notify_milestone(
        self,
        milestone: str,
        total_revenue: float,
        subscriber_count: int,
    ) -> bool:
        """
        Notify about a revenue milestone.

        Args:
            milestone: Description of milestone (e.g., "First $100!")
            total_revenue: Total revenue to date
            subscriber_count: Current subscriber count

        Returns:
            True if notification sent, False otherwise
        """
        text = self.config.milestone_template.format(
            milestone=milestone,
            total=total_revenue,
            subscribers=subscriber_count,
        )

        return await self._send_message(text)

    async def notify_cancellation(
        self,
        user_id: str,
        tier: str,
        *,
        reason: str | None = None,
    ) -> bool:
        """
        Notify about a subscription cancellation (for awareness).

        Args:
            user_id: User who cancelled
            tier: Tier they were on
            reason: Cancellation reason if provided

        Returns:
            True if notification sent, False otherwise
        """
        reason_str = f"\nReason: {reason}" if reason else ""
        text = (
            f"📉 **Subscription Cancelled**\n\n"
            f"User: `{user_id}`\n"
            f"Tier: {tier}{reason_str}\n\n"
            f"🤔 Learn and improve!"
        )

        return await self._send_message(text)

    async def notify_error(self, message: str) -> bool:
        """
        Notify about an error that needs attention.

        Args:
            message: Error description

        Returns:
            True if notification sent, False otherwise
        """
        text = self.config.error_template.format(
            message=message,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        return await self._send_message(text)

    async def send_test(self) -> bool:
        """
        Send a test message to verify configuration.

        Returns:
            True if test succeeded, False otherwise
        """
        text = (
            "🧪 **Test Notification**\n\n"
            "TelegramNotifier is configured and working!\n\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "Ready to receive revenue updates! 🚀"
        )

        return await self._send_message(text)

    def get_status(self) -> dict[str, Any]:
        """Get notifier status for diagnostics."""
        return {
            "enabled": self.is_enabled,
            "configured": self.is_configured,
            "bot_token_set": bool(self.config.bot_token),
            "chat_id_set": bool(self.config.chat_id),
            "messages_this_minute": self._messages_this_minute,
            "rate_limit_ok": self._check_rate_limit(),
        }


# =============================================================================
# Mock Notifier (for testing)
# =============================================================================


class MockTelegramNotifier(TelegramNotifier):
    """
    Mock notifier for testing without Telegram API calls.

    Records all notifications for assertion in tests.
    """

    def __init__(self) -> None:
        """Initialize mock notifier."""
        super().__init__(TelegramConfig(enabled=True, bot_token="mock", chat_id="mock"))
        self.sent_messages: list[str] = []
        self.call_count: int = 0

    async def _send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Record message instead of sending."""
        self.sent_messages.append(text)
        self.call_count += 1
        logger.debug(f"MockTelegram: {text[:50]}...")
        return True

    def reset(self) -> None:
        """Clear recorded messages."""
        self.sent_messages.clear()
        self.call_count = 0

    def assert_sent(self, substring: str) -> None:
        """Assert that a message containing substring was sent."""
        for msg in self.sent_messages:
            if substring in msg:
                return
        raise AssertionError(
            f"No message containing '{substring}' was sent. Sent: {self.sent_messages}"
        )


# =============================================================================
# Factory Function
# =============================================================================


def create_telegram_notifier(use_mock: bool = False) -> TelegramNotifier:
    """
    Create a Telegram notifier.

    Args:
        use_mock: If True, return mock notifier for testing

    Returns:
        TelegramNotifier or MockTelegramNotifier
    """
    if use_mock:
        return MockTelegramNotifier()
    return TelegramNotifier.from_env()


# =============================================================================
# Singleton for Webhook Integration
# =============================================================================

_notifier: TelegramNotifier | None = None


def get_telegram_notifier() -> TelegramNotifier:
    """Get or create the global Telegram notifier singleton."""
    global _notifier
    if _notifier is None:
        _notifier = TelegramNotifier.from_env()
    return _notifier


def set_telegram_notifier(notifier: TelegramNotifier) -> None:
    """Set the global notifier (for testing/DI)."""
    global _notifier
    _notifier = notifier


def reset_telegram_notifier() -> None:
    """Reset the global notifier (for testing)."""
    global _notifier
    _notifier = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TelegramConfig",
    "TelegramNotifier",
    "MockTelegramNotifier",
    "create_telegram_notifier",
    "get_telegram_notifier",
    "set_telegram_notifier",
    "reset_telegram_notifier",
]
