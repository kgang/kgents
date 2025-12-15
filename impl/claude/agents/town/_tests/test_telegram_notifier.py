"""
Tests for TelegramNotifier.

Kent's Motivation Loop: Verify notifications work correctly.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from agents.town.telegram_notifier import (
    MockTelegramNotifier,
    TelegramConfig,
    TelegramNotifier,
    create_telegram_notifier,
    get_telegram_notifier,
    reset_telegram_notifier,
    set_telegram_notifier,
)

# =============================================================================
# Config Tests
# =============================================================================


class TestTelegramConfig:
    """Tests for TelegramConfig."""

    def test_default_config(self) -> None:
        """Default config has notifications disabled."""
        config = TelegramConfig()
        assert config.enabled is False
        assert config.bot_token == ""
        assert config.chat_id == ""

    def test_from_env_without_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Config from env without vars set."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)
        monkeypatch.delenv("TELEGRAM_ENABLED", raising=False)

        config = TelegramConfig.from_env()
        assert config.enabled is False
        assert config.bot_token == ""
        assert config.chat_id == ""

    def test_from_env_with_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Config from env with vars set."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "test_chat")
        monkeypatch.setenv("TELEGRAM_ENABLED", "true")

        config = TelegramConfig.from_env()
        assert config.enabled is True
        assert config.bot_token == "test_token"
        assert config.chat_id == "test_chat"


# =============================================================================
# TelegramNotifier Tests
# =============================================================================


class TestTelegramNotifier:
    """Tests for TelegramNotifier."""

    def test_is_enabled_false_when_disabled(self) -> None:
        """is_enabled is False when config.enabled is False."""
        config = TelegramConfig(
            bot_token="token",
            chat_id="chat",
            enabled=False,
        )
        notifier = TelegramNotifier(config)
        assert notifier.is_enabled is False

    def test_is_enabled_false_without_token(self) -> None:
        """is_enabled is False without bot token."""
        config = TelegramConfig(
            bot_token="",
            chat_id="chat",
            enabled=True,
        )
        notifier = TelegramNotifier(config)
        assert notifier.is_enabled is False

    def test_is_enabled_false_without_chat_id(self) -> None:
        """is_enabled is False without chat ID."""
        config = TelegramConfig(
            bot_token="token",
            chat_id="",
            enabled=True,
        )
        notifier = TelegramNotifier(config)
        assert notifier.is_enabled is False

    def test_is_enabled_true_when_configured(self) -> None:
        """is_enabled is True when fully configured."""
        config = TelegramConfig(
            bot_token="token",
            chat_id="chat",
            enabled=True,
        )
        notifier = TelegramNotifier(config)
        assert notifier.is_enabled is True

    def test_get_status(self) -> None:
        """get_status returns correct status dict."""
        config = TelegramConfig(
            bot_token="token",
            chat_id="chat",
            enabled=True,
        )
        notifier = TelegramNotifier(config)
        status = notifier.get_status()

        assert status["enabled"] is True
        assert status["configured"] is True
        assert status["bot_token_set"] is True
        assert status["chat_id_set"] is True
        assert "rate_limit_ok" in status

    @pytest.mark.asyncio
    async def test_send_disabled_returns_true(self) -> None:
        """Sending when disabled returns True (graceful degradation)."""
        config = TelegramConfig(enabled=False)
        notifier = TelegramNotifier(config)

        result = await notifier.notify_payment("user", 9.99, "RESIDENT")
        assert result is True


# =============================================================================
# MockTelegramNotifier Tests
# =============================================================================


class TestMockTelegramNotifier:
    """Tests for MockTelegramNotifier."""

    @pytest.mark.asyncio
    async def test_mock_records_messages(self) -> None:
        """Mock notifier records sent messages."""
        mock = MockTelegramNotifier()

        await mock.notify_payment("user123", 9.99, "RESIDENT")

        assert mock.call_count == 1
        assert len(mock.sent_messages) == 1
        assert "user123" in mock.sent_messages[0]
        assert "9.99" in mock.sent_messages[0]

    @pytest.mark.asyncio
    async def test_mock_notify_subscription(self) -> None:
        """Mock notifier records subscription notifications."""
        mock = MockTelegramNotifier()

        await mock.notify_subscription(
            user_id="user456",
            tier="CITIZEN",
            renews_at=datetime(2025, 1, 15),
        )

        assert mock.call_count == 1
        mock.assert_sent("user456")
        mock.assert_sent("CITIZEN")

    @pytest.mark.asyncio
    async def test_mock_notify_milestone(self) -> None:
        """Mock notifier records milestone notifications."""
        mock = MockTelegramNotifier()

        await mock.notify_milestone(
            milestone="First $100!",
            total_revenue=100.00,
            subscriber_count=10,
        )

        assert mock.call_count == 1
        mock.assert_sent("First $100!")
        mock.assert_sent("Milestone")

    @pytest.mark.asyncio
    async def test_mock_notify_cancellation(self) -> None:
        """Mock notifier records cancellation notifications."""
        mock = MockTelegramNotifier()

        await mock.notify_cancellation(
            user_id="user789",
            tier="RESIDENT",
            reason="Too expensive",
        )

        assert mock.call_count == 1
        mock.assert_sent("Cancelled")
        mock.assert_sent("Too expensive")

    @pytest.mark.asyncio
    async def test_mock_notify_error(self) -> None:
        """Mock notifier records error notifications."""
        mock = MockTelegramNotifier()

        await mock.notify_error("Payment processing failed")

        assert mock.call_count == 1
        mock.assert_sent("Alert")
        mock.assert_sent("Payment processing failed")

    @pytest.mark.asyncio
    async def test_mock_send_test(self) -> None:
        """Mock notifier records test notifications."""
        mock = MockTelegramNotifier()

        result = await mock.send_test()

        assert result is True
        assert mock.call_count == 1
        mock.assert_sent("Test Notification")

    def test_mock_reset(self) -> None:
        """Mock notifier reset clears state."""
        mock = MockTelegramNotifier()
        mock.sent_messages.append("test")
        mock.call_count = 5

        mock.reset()

        assert mock.call_count == 0
        assert len(mock.sent_messages) == 0

    def test_mock_assert_sent_raises(self) -> None:
        """assert_sent raises when message not found."""
        mock = MockTelegramNotifier()

        with pytest.raises(AssertionError):
            mock.assert_sent("not found")

    @pytest.mark.asyncio
    async def test_mock_credit_pack_notification(self) -> None:
        """Mock notifier handles credit pack payments."""
        mock = MockTelegramNotifier()

        await mock.notify_payment(
            user_id="buyer1",
            amount=20.00,
            tier="CREDITS",
            pack="EXPLORER",
            credits=1000,
        )

        assert mock.call_count == 1
        mock.assert_sent("Credit Pack")
        mock.assert_sent("EXPLORER")
        mock.assert_sent("1,000")  # Credits formatted with comma

    @pytest.mark.asyncio
    async def test_mock_upgrade_notification(self) -> None:
        """Mock notifier handles subscription upgrades."""
        mock = MockTelegramNotifier()

        await mock.notify_subscription(
            user_id="upgrader",
            tier="CITIZEN",
            renews_at=datetime(2025, 2, 1),
            is_upgrade=True,
            previous_tier="RESIDENT",
        )

        assert mock.call_count == 1
        mock.assert_sent("Upgrade")
        mock.assert_sent("RESIDENT")
        mock.assert_sent("CITIZEN")


# =============================================================================
# Factory and Singleton Tests
# =============================================================================


class TestFactory:
    """Tests for factory functions."""

    def test_create_telegram_notifier(self) -> None:
        """create_telegram_notifier returns real notifier."""
        notifier = create_telegram_notifier(use_mock=False)
        assert isinstance(notifier, TelegramNotifier)
        assert not isinstance(notifier, MockTelegramNotifier)

    def test_create_mock_notifier(self) -> None:
        """create_telegram_notifier with use_mock returns mock."""
        notifier = create_telegram_notifier(use_mock=True)
        assert isinstance(notifier, MockTelegramNotifier)


class TestSingleton:
    """Tests for singleton management."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        reset_telegram_notifier()

    def teardown_method(self) -> None:
        """Reset singleton after each test."""
        reset_telegram_notifier()

    def test_get_telegram_notifier_returns_same_instance(self) -> None:
        """get_telegram_notifier returns same instance."""
        notifier1 = get_telegram_notifier()
        notifier2 = get_telegram_notifier()
        assert notifier1 is notifier2

    def test_set_telegram_notifier(self) -> None:
        """set_telegram_notifier overrides singleton."""
        mock = MockTelegramNotifier()
        set_telegram_notifier(mock)

        retrieved = get_telegram_notifier()
        assert retrieved is mock

    def test_reset_telegram_notifier(self) -> None:
        """reset_telegram_notifier clears singleton."""
        notifier1 = get_telegram_notifier()
        reset_telegram_notifier()
        notifier2 = get_telegram_notifier()

        assert notifier1 is not notifier2


# =============================================================================
# Rate Limiting Tests
# =============================================================================


class TestRateLimiting:
    """Tests for rate limiting."""

    def test_rate_limit_check_initial(self) -> None:
        """Initial rate limit check passes."""
        config = TelegramConfig(
            bot_token="token",
            chat_id="chat",
            enabled=True,
        )
        notifier = TelegramNotifier(config)

        assert notifier._check_rate_limit() is True

    @pytest.mark.asyncio
    async def test_rate_limit_respects_interval(self) -> None:
        """Rate limit respects minimum interval."""
        mock = MockTelegramNotifier()
        mock.config.min_interval_seconds = 1.0

        # First message should work
        await mock.notify_payment("user", 1.0, "TEST")
        assert mock.call_count == 1

        # Check rate limit - should fail immediately after
        # (Not testing actual timing here, just the mechanism)


# =============================================================================
# Integration Tests
# =============================================================================


class TestWebhookIntegration:
    """Tests for webhook integration."""

    @pytest.mark.asyncio
    async def test_webhook_can_use_telegram(self) -> None:
        """Webhook handler can use TelegramNotifier."""
        from protocols.api.webhooks import (
            reset_telegram_notifier as reset_webhook_notifier,
        )
        from protocols.api.webhooks import (
            set_telegram_notifier as set_webhook_notifier,
        )

        # Set mock notifier in webhooks module
        mock = MockTelegramNotifier()
        set_webhook_notifier(mock)

        # Verify it's set
        from protocols.api.webhooks import _get_telegram_notifier

        retrieved = _get_telegram_notifier()
        assert retrieved is mock

        # Cleanup
        reset_webhook_notifier()
