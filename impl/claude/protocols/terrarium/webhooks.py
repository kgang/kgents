"""
Webhook Notifications for Semaphore Events.

Fire-and-forget notifications to Slack, PagerDuty, and custom webhooks
when semaphore events occur (ejection, resolution, voiding).

The Rodizio Pattern Integration:
When an agent ejects a SemaphoreToken to Purgatory, this dispatcher
can notify external systems for human attention.

Usage:
    from protocols.terrarium.webhooks import WebhookDispatcher, WebhookConfig

    config = WebhookConfig(
        enabled=True,
        slack_webhook_url="https://hooks.slack.com/...",
        pagerduty_routing_key="...",
        severity_threshold="warning",
    )

    dispatcher = WebhookDispatcher(config)

    # Wire to purgatory
    async def emit_with_webhook(signal: str, data: dict) -> None:
        if signal == "purgatory.ejected":
            token = purgatory.get(data["token_id"])
            if token:
                await dispatcher.notify_ejected(token)

    purgatory._emit_pheromone = emit_with_webhook

AGENTESE: world.terrarium.webhooks
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.flux.semaphore import SemaphoreToken

logger = logging.getLogger(__name__)


@dataclass
class WebhookConfig:
    """
    Webhook notification configuration.

    Can be loaded from environment variables for K8s deployment.
    """

    # Master switch
    enabled: bool = False

    # Slack integration
    slack_webhook_url: str | None = None

    # PagerDuty integration (Events API v2)
    pagerduty_routing_key: str | None = None
    pagerduty_api_url: str = "https://events.pagerduty.com/v2/enqueue"

    # Custom webhooks (POST JSON to these URLs)
    custom_webhook_urls: list[str] = field(default_factory=list)

    # Event filtering
    notify_on_ejected: bool = True
    notify_on_resolved: bool = False  # Usually not needed
    notify_on_cancelled: bool = False
    notify_on_voided: bool = True  # Deadline expired = urgent

    # Severity threshold (only notify if >= threshold)
    # Levels: info < warning < critical
    severity_threshold: str = "warning"

    # Request timeout in seconds
    timeout: float = 5.0

    # Retry configuration
    max_retries: int = 3
    retry_base_delay: float = 1.0  # Base delay in seconds
    retry_max_delay: float = 30.0  # Maximum delay after backoff

    @classmethod
    def from_env(cls) -> "WebhookConfig":
        """Load configuration from environment variables."""
        custom_urls = os.environ.get("WEBHOOK_CUSTOM_URLS", "")
        urls = [u.strip() for u in custom_urls.split(",") if u.strip()]

        return cls(
            enabled=os.environ.get("WEBHOOK_ENABLED", "").lower() in ("true", "1"),
            slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL"),
            pagerduty_routing_key=os.environ.get("PAGERDUTY_ROUTING_KEY"),
            custom_webhook_urls=urls,
            notify_on_ejected=os.environ.get("WEBHOOK_ON_EJECTED", "true").lower()
            in ("true", "1"),
            notify_on_resolved=os.environ.get("WEBHOOK_ON_RESOLVED", "false").lower()
            in ("true", "1"),
            notify_on_voided=os.environ.get("WEBHOOK_ON_VOIDED", "true").lower()
            in ("true", "1"),
            severity_threshold=os.environ.get("WEBHOOK_SEVERITY_THRESHOLD", "warning"),
            timeout=float(os.environ.get("WEBHOOK_TIMEOUT", "5.0")),
            max_retries=int(os.environ.get("WEBHOOK_MAX_RETRIES", "3")),
            retry_base_delay=float(os.environ.get("WEBHOOK_RETRY_BASE_DELAY", "1.0")),
            retry_max_delay=float(os.environ.get("WEBHOOK_RETRY_MAX_DELAY", "30.0")),
        )


# Severity ordering for threshold comparison
SEVERITY_ORDER = {"info": 0, "warning": 1, "critical": 2}


@dataclass
class WebhookDispatcher:
    """
    Fire-and-forget webhook notifications for semaphore events.

    Best-effort: failures are logged but don't affect control flow.
    """

    config: WebhookConfig

    # HTTP client (lazy-initialized)
    _client: Any = field(default=None, init=False)

    async def notify_ejected(self, token: "SemaphoreToken[Any]") -> None:
        """
        Send notification when token ejected to purgatory.

        This is the primary notification - a human needs to decide.
        """
        if not self._should_notify("ejected", token):
            return

        logger.info(f"[webhooks] Notifying ejection: {token.id}")

        tasks = []

        if self.config.slack_webhook_url:
            tasks.append(self._send_slack_ejected(token))

        if self.config.pagerduty_routing_key:
            tasks.append(self._send_pagerduty_ejected(token))

        for url in self.config.custom_webhook_urls:
            tasks.append(self._send_custom_webhook(url, "ejected", token))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def notify_resolved(self, token: "SemaphoreToken[Any]") -> None:
        """
        Send notification when token resolved.

        Usually disabled - resolution is the happy path.
        """
        if not self._should_notify("resolved", token):
            return

        logger.info(f"[webhooks] Notifying resolution: {token.id}")

        tasks = []

        if self.config.pagerduty_routing_key:
            tasks.append(self._send_pagerduty_resolved(token))

        for url in self.config.custom_webhook_urls:
            tasks.append(self._send_custom_webhook(url, "resolved", token))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def notify_voided(self, token: "SemaphoreToken[Any]") -> None:
        """
        Send notification when token deadline expires.

        This is urgent - someone failed to respond in time.
        """
        if not self._should_notify("voided", token):
            return

        logger.info(f"[webhooks] Notifying void: {token.id}")

        tasks = []

        if self.config.slack_webhook_url:
            tasks.append(self._send_slack_voided(token))

        if self.config.pagerduty_routing_key:
            tasks.append(self._send_pagerduty_voided(token))

        for url in self.config.custom_webhook_urls:
            tasks.append(self._send_custom_webhook(url, "voided", token))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def notify_cancelled(self, token: "SemaphoreToken[Any]") -> None:
        """
        Send notification when token cancelled.

        Usually disabled - cancellation is intentional.
        """
        if not self._should_notify("cancelled", token):
            return

        logger.info(f"[webhooks] Notifying cancellation: {token.id}")

        for url in self.config.custom_webhook_urls:
            await self._send_custom_webhook(url, "cancelled", token)

    def _should_notify(self, event: str, token: "SemaphoreToken[Any]") -> bool:
        """Check if notification should be sent."""
        if not self.config.enabled:
            return False

        # Check event type
        if event == "ejected" and not self.config.notify_on_ejected:
            return False
        if event == "resolved" and not self.config.notify_on_resolved:
            return False
        if event == "voided" and not self.config.notify_on_voided:
            return False
        if event == "cancelled" and not self.config.notify_on_cancelled:
            return False

        # Check severity threshold
        token_severity = SEVERITY_ORDER.get(token.severity, 0)
        threshold = SEVERITY_ORDER.get(self.config.severity_threshold, 0)

        if token_severity < threshold:
            return False

        return True

    async def _get_client(self) -> Any:
        """Get or create HTTP client."""
        if self._client is None:
            try:
                import httpx

                self._client = httpx.AsyncClient(timeout=self.config.timeout)
            except ImportError:
                logger.warning("[webhooks] httpx not available")
                return None
        return self._client

    async def _send_with_retry(
        self,
        url: str,
        payload: dict[str, Any],
        name: str,
        expected_status_codes: set[int] | None = None,
    ) -> bool:
        """
        Send webhook with exponential backoff retry.

        Args:
            url: The URL to POST to
            payload: JSON payload
            name: Service name for logging (e.g., "Slack", "PagerDuty")
            expected_status_codes: Set of acceptable status codes (default: {200})

        Returns:
            True if webhook delivered successfully, False otherwise.
        """
        client = await self._get_client()
        if client is None:
            return False

        if expected_status_codes is None:
            expected_status_codes = {200}

        last_error: str = ""
        for attempt in range(self.config.max_retries):
            try:
                response = await client.post(url, json=payload)
                if response.status_code in expected_status_codes:
                    if attempt > 0:
                        logger.info(
                            f"[webhooks] {name} succeeded after {attempt + 1} attempts"
                        )
                    return True
                else:
                    last_error = f"HTTP {response.status_code}"
                    logger.warning(
                        f"[webhooks] {name} returned {response.status_code} "
                        f"(attempt {attempt + 1}/{self.config.max_retries})"
                    )
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"[webhooks] {name} failed: {e} "
                    f"(attempt {attempt + 1}/{self.config.max_retries})"
                )

            # Don't sleep after last attempt
            if attempt < self.config.max_retries - 1:
                # Exponential backoff with jitter
                delay = min(
                    self.config.retry_base_delay * (2**attempt),
                    self.config.retry_max_delay,
                )
                # Add 10% jitter to avoid thundering herd
                import random

                delay *= 0.9 + random.random() * 0.2
                logger.debug(f"[webhooks] Retrying {name} in {delay:.2f}s")
                await asyncio.sleep(delay)

        logger.error(
            f"[webhooks] {name} failed after {self.config.max_retries} attempts: {last_error}"
        )
        return False

    async def _send_slack_ejected(self, token: "SemaphoreToken[Any]") -> None:
        """Send Slack notification for ejection."""
        if self.config.slack_webhook_url is None:
            return

        payload = self._format_slack_ejected(token)
        await self._send_with_retry(self.config.slack_webhook_url, payload, "Slack")

    async def _send_slack_voided(self, token: "SemaphoreToken[Any]") -> None:
        """Send Slack notification for voided token."""
        if self.config.slack_webhook_url is None:
            return

        payload = self._format_slack_voided(token)
        await self._send_with_retry(self.config.slack_webhook_url, payload, "Slack")

    async def _send_pagerduty_ejected(self, token: "SemaphoreToken[Any]") -> None:
        """Send PagerDuty alert for ejection."""
        if self.config.pagerduty_routing_key is None:
            return

        payload = self._format_pagerduty_trigger(token)
        await self._send_with_retry(
            self.config.pagerduty_api_url,
            payload,
            "PagerDuty",
            expected_status_codes={200, 201, 202},
        )

    async def _send_pagerduty_resolved(self, token: "SemaphoreToken[Any]") -> None:
        """Send PagerDuty resolution."""
        if self.config.pagerduty_routing_key is None:
            return

        payload = self._format_pagerduty_resolve(token)
        await self._send_with_retry(
            self.config.pagerduty_api_url,
            payload,
            "PagerDuty",
            expected_status_codes={200, 201, 202},
        )

    async def _send_pagerduty_voided(self, token: "SemaphoreToken[Any]") -> None:
        """Send PagerDuty alert for voided token (deadline expired)."""
        if self.config.pagerduty_routing_key is None:
            return

        # Use trigger with escalated severity
        payload = self._format_pagerduty_trigger(token, escalated=True)
        await self._send_with_retry(
            self.config.pagerduty_api_url,
            payload,
            "PagerDuty",
            expected_status_codes={200, 201, 202},
        )

    async def _send_custom_webhook(
        self, url: str, event: str, token: "SemaphoreToken[Any]"
    ) -> None:
        """Send to custom webhook URL."""
        payload = self._format_custom_webhook(event, token)
        # Accept any 2xx status code for custom webhooks
        await self._send_with_retry(
            url,
            payload,
            f"Custom webhook ({url[:50]}...)",
            expected_status_codes={200, 201, 202, 204},
        )

    def _format_slack_ejected(self, token: "SemaphoreToken[Any]") -> dict[str, Any]:
        """Format Slack Block Kit message for ejection."""
        severity_emoji = {"info": "🔵", "warning": "🟡", "critical": "🔴"}.get(
            token.severity, "⚪"
        )

        options_text = " | ".join(f"`{opt}`" for opt in token.options[:4])

        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{severity_emoji} Semaphore: Decision Needed",
                    },
                },
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"*{token.prompt}*"},
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Severity:* `{token.severity}`"},
                        {
                            "type": "mrkdwn",
                            "text": f"*Reason:* `{token.reason.value}`",
                        },
                        {"type": "mrkdwn", "text": f"*Token ID:* `{token.id}`"},
                        {
                            "type": "mrkdwn",
                            "text": f"*Created:* {token.created_at.strftime('%H:%M:%S')}",
                        },
                    ],
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"Options: {options_text}"}
                    ],
                },
            ]
        }

    def _format_slack_voided(self, token: "SemaphoreToken[Any]") -> dict[str, Any]:
        """Format Slack message for voided token (deadline expired)."""
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⏰ Semaphore Deadline Expired",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{token.prompt}*\n\n"
                        f"Token `{token.id}` was not resolved in time and has been voided.",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Deadline was: {token.deadline.isoformat() if token.deadline else 'None'}",
                        }
                    ],
                },
            ]
        }

    def _format_pagerduty_trigger(
        self, token: "SemaphoreToken[Any]", escalated: bool = False
    ) -> dict[str, Any]:
        """Format PagerDuty Events API v2 trigger payload."""
        # Map severity to PagerDuty severity
        pd_severity = {
            "info": "info",
            "warning": "warning",
            "critical": "critical",
        }.get(token.severity, "warning")

        # Escalate if deadline expired
        if escalated:
            pd_severity = "critical"

        return {
            "routing_key": self.config.pagerduty_routing_key,
            "event_action": "trigger",
            "dedup_key": token.id,
            "payload": {
                "summary": f"Semaphore: {token.prompt}",
                "severity": pd_severity,
                "source": "kgents-terrarium",
                "custom_details": {
                    "token_id": token.id,
                    "reason": token.reason.value,
                    "options": token.options,
                    "deadline": token.deadline.isoformat() if token.deadline else None,
                    "created_at": token.created_at.isoformat(),
                    "escalated": escalated,
                },
            },
        }

    def _format_pagerduty_resolve(self, token: "SemaphoreToken[Any]") -> dict[str, Any]:
        """Format PagerDuty resolve payload."""
        return {
            "routing_key": self.config.pagerduty_routing_key,
            "event_action": "resolve",
            "dedup_key": token.id,
        }

    def _format_custom_webhook(
        self, event: str, token: "SemaphoreToken[Any]"
    ) -> dict[str, Any]:
        """Format custom webhook payload."""
        return {
            "event": f"semaphore.{event}",
            "timestamp": datetime.now().isoformat(),
            "token": {
                "id": token.id,
                "reason": token.reason.value,
                "prompt": token.prompt,
                "options": token.options,
                "severity": token.severity,
                "deadline": token.deadline.isoformat() if token.deadline else None,
                "created_at": token.created_at.isoformat(),
                "resolved_at": (
                    token.resolved_at.isoformat() if token.resolved_at else None
                ),
                "voided_at": token.voided_at.isoformat() if token.voided_at else None,
            },
        }

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
