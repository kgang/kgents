"""Tests for WebhookDispatcher and WebhookConfig."""

import os
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from agents.flux.semaphore import SemaphoreReason, SemaphoreToken
from protocols.terrarium.webhooks import (
    SEVERITY_ORDER,
    WebhookConfig,
    WebhookDispatcher,
)


def make_test_token(
    severity: str = "warning",
    prompt: str = "Test prompt?",
    reason: SemaphoreReason = SemaphoreReason.APPROVAL_NEEDED,
    deadline: datetime | None = None,
) -> SemaphoreToken[str]:
    """Create a test token."""
    return SemaphoreToken(
        reason=reason,
        frozen_state=b"test",
        original_event="test",
        prompt=prompt,
        options=["Yes", "No", "Maybe"],
        severity=severity,
        deadline=deadline,
    )


class TestWebhookConfigDefaults:
    """Default configuration values."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = WebhookConfig()

        assert config.enabled is False
        assert config.slack_webhook_url is None
        assert config.pagerduty_routing_key is None
        assert config.custom_webhook_urls == []
        assert config.notify_on_ejected is True
        assert config.notify_on_resolved is False
        assert config.notify_on_voided is True
        assert config.severity_threshold == "warning"
        assert config.timeout == 5.0

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            pagerduty_routing_key="test-key",
            custom_webhook_urls=["https://example.com/webhook"],
            severity_threshold="critical",
        )

        assert config.enabled is True
        assert config.slack_webhook_url == "https://hooks.slack.com/test"
        assert config.pagerduty_routing_key == "test-key"
        assert config.custom_webhook_urls == ["https://example.com/webhook"]
        assert config.severity_threshold == "critical"


class TestWebhookConfigFromEnv:
    """Configuration from environment variables."""

    def test_from_env_defaults(self) -> None:
        """from_env uses defaults when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = WebhookConfig.from_env()

            assert config.enabled is False
            assert config.slack_webhook_url is None
            assert config.pagerduty_routing_key is None

    def test_from_env_custom_values(self) -> None:
        """from_env reads custom values from environment."""
        env = {
            "WEBHOOK_ENABLED": "true",
            "SLACK_WEBHOOK_URL": "https://hooks.slack.com/test",
            "PAGERDUTY_ROUTING_KEY": "test-key",
            "WEBHOOK_CUSTOM_URLS": "https://a.com, https://b.com",
            "WEBHOOK_ON_EJECTED": "true",
            "WEBHOOK_ON_RESOLVED": "true",
            "WEBHOOK_ON_VOIDED": "false",
            "WEBHOOK_SEVERITY_THRESHOLD": "critical",
            "WEBHOOK_TIMEOUT": "10.0",
        }

        with patch.dict(os.environ, env, clear=False):
            config = WebhookConfig.from_env()

            assert config.enabled is True
            assert config.slack_webhook_url == "https://hooks.slack.com/test"
            assert config.pagerduty_routing_key == "test-key"
            assert config.custom_webhook_urls == ["https://a.com", "https://b.com"]
            assert config.notify_on_ejected is True
            assert config.notify_on_resolved is True
            assert config.notify_on_voided is False
            assert config.severity_threshold == "critical"
            assert config.timeout == 10.0


class TestSeverityOrder:
    """Severity ordering for threshold comparison."""

    def test_severity_order(self) -> None:
        """Severities are ordered correctly."""
        assert SEVERITY_ORDER["info"] < SEVERITY_ORDER["warning"]
        assert SEVERITY_ORDER["warning"] < SEVERITY_ORDER["critical"]


class TestWebhookDispatcherShouldNotify:
    """_should_notify filtering tests."""

    def test_disabled_returns_false(self) -> None:
        """Disabled dispatcher returns False."""
        config = WebhookConfig(enabled=False)
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        assert dispatcher._should_notify("ejected", token) is False

    def test_enabled_ejected_returns_true(self) -> None:
        """Enabled dispatcher returns True for ejected."""
        config = WebhookConfig(enabled=True, notify_on_ejected=True)
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        assert dispatcher._should_notify("ejected", token) is True

    def test_disabled_event_type_returns_false(self) -> None:
        """Disabled event type returns False."""
        config = WebhookConfig(enabled=True, notify_on_resolved=False)
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        assert dispatcher._should_notify("resolved", token) is False

    def test_below_threshold_returns_false(self) -> None:
        """Token below severity threshold returns False."""
        config = WebhookConfig(enabled=True, severity_threshold="warning")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="info")

        assert dispatcher._should_notify("ejected", token) is False

    def test_at_threshold_returns_true(self) -> None:
        """Token at severity threshold returns True."""
        config = WebhookConfig(enabled=True, severity_threshold="warning")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="warning")

        assert dispatcher._should_notify("ejected", token) is True

    def test_above_threshold_returns_true(self) -> None:
        """Token above severity threshold returns True."""
        config = WebhookConfig(enabled=True, severity_threshold="warning")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="critical")

        assert dispatcher._should_notify("ejected", token) is True


class TestWebhookDispatcherFormatting:
    """Message formatting tests."""

    def test_format_slack_ejected(self) -> None:
        """Slack ejection message is formatted correctly."""
        config = WebhookConfig()
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(prompt="Delete 47 files?", severity="warning")

        payload = dispatcher._format_slack_ejected(token)

        assert "blocks" in payload
        blocks = payload["blocks"]
        assert len(blocks) >= 3

        # Header
        assert blocks[0]["type"] == "header"
        assert "Decision Needed" in blocks[0]["text"]["text"]

        # Prompt
        assert blocks[1]["type"] == "section"
        assert "Delete 47 files?" in blocks[1]["text"]["text"]

    def test_format_slack_voided(self) -> None:
        """Slack voided message is formatted correctly."""
        config = WebhookConfig()
        dispatcher = WebhookDispatcher(config)
        deadline = datetime.now() - timedelta(hours=1)
        token = make_test_token(deadline=deadline)

        payload = dispatcher._format_slack_voided(token)

        assert "blocks" in payload
        assert "Deadline Expired" in payload["blocks"][0]["text"]["text"]

    def test_format_pagerduty_trigger(self) -> None:
        """PagerDuty trigger payload is formatted correctly."""
        config = WebhookConfig(pagerduty_routing_key="test-key")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="critical")

        payload = dispatcher._format_pagerduty_trigger(token)

        assert payload["routing_key"] == "test-key"
        assert payload["event_action"] == "trigger"
        assert payload["dedup_key"] == token.id
        assert payload["payload"]["severity"] == "critical"
        assert payload["payload"]["source"] == "kgents-terrarium"

    def test_format_pagerduty_trigger_escalated(self) -> None:
        """PagerDuty escalated trigger uses critical severity."""
        config = WebhookConfig(pagerduty_routing_key="test-key")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="info")  # Low severity

        payload = dispatcher._format_pagerduty_trigger(token, escalated=True)

        # Escalated always uses critical
        assert payload["payload"]["severity"] == "critical"
        assert payload["payload"]["custom_details"]["escalated"] is True

    def test_format_pagerduty_resolve(self) -> None:
        """PagerDuty resolve payload is formatted correctly."""
        config = WebhookConfig(pagerduty_routing_key="test-key")
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        payload = dispatcher._format_pagerduty_resolve(token)

        assert payload["routing_key"] == "test-key"
        assert payload["event_action"] == "resolve"
        assert payload["dedup_key"] == token.id

    def test_format_custom_webhook(self) -> None:
        """Custom webhook payload is formatted correctly."""
        config = WebhookConfig()
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        payload = dispatcher._format_custom_webhook("ejected", token)

        assert payload["event"] == "semaphore.ejected"
        assert "timestamp" in payload
        assert payload["token"]["id"] == token.id
        assert payload["token"]["prompt"] == "Test prompt?"
        assert payload["token"]["options"] == ["Yes", "No", "Maybe"]


class TestWebhookDispatcherNotify:
    """Notification dispatch tests."""

    @pytest.mark.asyncio
    async def test_notify_ejected_disabled(self) -> None:
        """notify_ejected does nothing when disabled."""
        config = WebhookConfig(enabled=False)
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        # Should not raise
        await dispatcher.notify_ejected(token)

    @pytest.mark.asyncio
    async def test_notify_ejected_sends_slack(self) -> None:
        """notify_ejected sends Slack webhook."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        # Mock the client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        # Should have called post
        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/test"

    @pytest.mark.asyncio
    async def test_notify_ejected_sends_pagerduty(self) -> None:
        """notify_ejected sends PagerDuty alert."""
        config = WebhookConfig(
            enabled=True,
            pagerduty_routing_key="test-key",
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        assert "pagerduty" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_notify_ejected_sends_custom(self) -> None:
        """notify_ejected sends to custom webhooks."""
        config = WebhookConfig(
            enabled=True,
            custom_webhook_urls=["https://example.com/webhook"],
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://example.com/webhook"

    @pytest.mark.asyncio
    async def test_notify_resolved_sends_pagerduty_resolve(self) -> None:
        """notify_resolved sends PagerDuty resolve."""
        config = WebhookConfig(
            enabled=True,
            pagerduty_routing_key="test-key",
            notify_on_resolved=True,
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        await dispatcher.notify_resolved(token)

        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["event_action"] == "resolve"

    @pytest.mark.asyncio
    async def test_notify_voided_sends_escalated(self) -> None:
        """notify_voided sends escalated PagerDuty alert."""
        config = WebhookConfig(
            enabled=True,
            pagerduty_routing_key="test-key",
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token(severity="info")

        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        await dispatcher.notify_voided(token)

        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        # Should be escalated to critical
        assert payload["payload"]["severity"] == "critical"


class TestWebhookDispatcherErrorHandling:
    """Error handling tests."""

    @pytest.mark.asyncio
    async def test_http_error_does_not_raise(self) -> None:
        """HTTP errors are logged but don't raise."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
            max_retries=1,  # Disable retries for quick test
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        # Should not raise
        await dispatcher.notify_ejected(token)

    @pytest.mark.asyncio
    async def test_connection_error_does_not_raise(self) -> None:
        """Connection errors are logged but don't raise."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
            max_retries=1,  # Disable retries for quick test
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Connection failed"))
        dispatcher._client = mock_client

        # Should not raise
        await dispatcher.notify_ejected(token)


class TestWebhookRetry:
    """Retry with exponential backoff tests."""

    @pytest.mark.asyncio
    async def test_retry_on_failure(self) -> None:
        """Retries on transient failure then succeeds."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
            max_retries=3,
            retry_base_delay=0.01,  # Fast retries for testing
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        # Fail twice, then succeed
        fail_response = MagicMock()
        fail_response.status_code = 500
        success_response = MagicMock()
        success_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=[fail_response, fail_response, success_response]
        )
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        # Should have called post 3 times (2 failures + 1 success)
        assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted(self) -> None:
        """Stops retrying after max_retries."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
            max_retries=3,
            retry_base_delay=0.01,  # Fast retries for testing
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        # Always fail
        fail_response = MagicMock()
        fail_response.status_code = 500
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=fail_response)
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        # Should have called exactly max_retries times
        assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_exception(self) -> None:
        """Retries on exception then succeeds."""
        config = WebhookConfig(
            enabled=True,
            slack_webhook_url="https://hooks.slack.com/test",
            severity_threshold="info",
            max_retries=3,
            retry_base_delay=0.01,  # Fast retries for testing
        )
        dispatcher = WebhookDispatcher(config)
        token = make_test_token()

        # Exception, then succeed
        success_response = MagicMock()
        success_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(
            side_effect=[
                Exception("Network error"),
                success_response,
            ]
        )
        dispatcher._client = mock_client

        await dispatcher.notify_ejected(token)

        # Should have called post 2 times (1 exception + 1 success)
        assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_send_with_retry_returns_success(self) -> None:
        """_send_with_retry returns True on success."""
        config = WebhookConfig(max_retries=1)
        dispatcher = WebhookDispatcher(config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        result = await dispatcher._send_with_retry("https://test.com", {}, "Test")

        assert result is True

    @pytest.mark.asyncio
    async def test_send_with_retry_returns_false_on_exhaustion(self) -> None:
        """_send_with_retry returns False when retries exhausted."""
        config = WebhookConfig(max_retries=2, retry_base_delay=0.01)
        dispatcher = WebhookDispatcher(config)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        result = await dispatcher._send_with_retry("https://test.com", {}, "Test")

        assert result is False


class TestWebhookDispatcherIntegration:
    """Integration tests with Purgatory."""

    @pytest.mark.asyncio
    async def test_purgatory_ejection_triggers_webhook(self) -> None:
        """Purgatory ejection can trigger webhook notification."""
        from agents.flux.semaphore import Purgatory

        config = WebhookConfig(
            enabled=True,
            custom_webhook_urls=["https://example.com/webhook"],
            severity_threshold="info",
        )
        dispatcher = WebhookDispatcher(config)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        dispatcher._client = mock_client

        purgatory = Purgatory()

        # Wire dispatcher to purgatory
        async def emit_with_webhook(signal: str, data: dict[str, Any]) -> None:
            if signal == "purgatory.ejected":
                token = purgatory.get(data["token_id"])
                if token:
                    await dispatcher.notify_ejected(token)

        purgatory._emit_pheromone = emit_with_webhook

        # Save token to purgatory
        token = make_test_token()
        await purgatory.save(token)

        # Webhook should have been called
        mock_client.post.assert_called()
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["event"] == "semaphore.ejected"
        assert payload["token"]["id"] == token.id
