"""
OpenMeter client for kgents usage-based billing.

Provides real-time usage metering with event aggregation for billing.
Integrates with OpenMeter for usage-based pricing.

Architecture:
    API Endpoints → OpenMeterClient → Buffer → OpenMeter API
                                    → Batch flush on interval/count

Event Types:
    - api.request: API request count
    - llm.tokens: LLM token usage (in/out)
    - session.create: Session creation
    - session.message: Message sent

Usage:
    from protocols.billing import OpenMeterClient, OpenMeterConfig

    config = OpenMeterConfig(api_key="om_...")
    client = OpenMeterClient(config)

    async with client:
        await client.record_tokens(tenant_id, session_id, tokens_in=100, tokens_out=50)
        await client.record_request(tenant_id, "/v1/soul/dialogue", "POST", 200)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class UsageEventType(str, Enum):
    """Types of usage events for billing."""

    API_REQUEST = "api.request"
    LLM_TOKENS = "llm.tokens"
    SESSION_CREATE = "session.create"
    SESSION_MESSAGE = "session.message"
    AGENTESE_INVOKE = "agentese.invoke"
    STORAGE_WRITE = "storage.write"
    STORAGE_READ = "storage.read"


@dataclass
class UsageEventSchema:
    """
    Usage event conforming to OpenMeter CloudEvents format.

    See: https://openmeter.io/docs/getting-started/events
    """

    id: str
    source: str
    type: str
    subject: str  # Tenant ID
    time: str  # ISO 8601
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to OpenMeter event format."""
        return {
            "id": self.id,
            "source": self.source,
            "type": self.type,
            "subject": self.subject,
            "time": self.time,
            "data": self.data,
        }

    @classmethod
    def create(
        cls,
        event_type: UsageEventType,
        subject: str | UUID,
        data: dict[str, Any],
        source: str = "kgents-api",
    ) -> "UsageEventSchema":
        """Create a new usage event."""
        return cls(
            id=str(uuid4()),
            source=source,
            type=event_type.value,
            subject=str(subject),
            time=datetime.now(UTC).isoformat(),
            data=data,
        )


@dataclass
class OpenMeterConfig:
    """Configuration for OpenMeter client."""

    # API Configuration
    api_key: str = ""  # Empty = disabled
    base_url: str = "https://openmeter.cloud"

    # Batching
    batch_size: int = 100
    flush_interval_seconds: float = 1.0

    # Retry
    max_retries: int = 3
    retry_delay_seconds: float = 0.5

    # Feature flags
    enabled: bool = True  # Can disable for local development

    @property
    def is_configured(self) -> bool:
        """Check if OpenMeter is configured."""
        return bool(self.api_key) and self.enabled


@dataclass
class OpenMeterClient:
    """
    OpenMeter client for usage-based billing.

    Provides buffered event ingestion with automatic flushing.
    Gracefully degrades when OpenMeter is unavailable.
    """

    config: OpenMeterConfig = field(default_factory=OpenMeterConfig)

    # Event buffer
    _buffer: list[UsageEventSchema] = field(
        default_factory=list, init=False, repr=False
    )
    _buffer_lock: asyncio.Lock = field(
        default_factory=asyncio.Lock, init=False, repr=False
    )

    # Background flush task
    _flush_task: Optional[asyncio.Task[None]] = field(
        default=None, init=False, repr=False
    )
    _running: bool = field(default=False, init=False)

    # Metrics
    _events_sent: int = field(default=0, init=False)
    _events_failed: int = field(default=0, init=False)
    _last_flush: Optional[datetime] = field(default=None, init=False)

    async def start(self) -> None:
        """Start the background flush task."""
        if self._running:
            return

        self._running = True

        if self.config.is_configured:
            self._flush_task = asyncio.create_task(
                self._flush_loop(),
                name="openmeter-flush",
            )
            logger.info(
                f"OpenMeter client started (batch_size={self.config.batch_size})"
            )
        else:
            logger.info("OpenMeter client started in local-only mode")

    async def stop(self) -> None:
        """Stop the client and flush remaining events."""
        self._running = False

        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None

        # Final flush
        await self.flush()
        logger.info(
            f"OpenMeter client stopped (sent={self._events_sent}, failed={self._events_failed})"
        )

    async def __aenter__(self) -> "OpenMeterClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()

    # ─────────────────────────────────────────────────────────────
    # Event Recording
    # ─────────────────────────────────────────────────────────────

    async def record_tokens(
        self,
        tenant_id: str | UUID,
        session_id: str | UUID,
        tokens_in: int,
        tokens_out: int,
        model: str = "kgent",
    ) -> None:
        """
        Record LLM token usage.

        Args:
            tenant_id: Tenant identifier (billing subject)
            session_id: Session identifier
            tokens_in: Input tokens consumed
            tokens_out: Output tokens generated
            model: Model identifier
        """
        event = UsageEventSchema.create(
            event_type=UsageEventType.LLM_TOKENS,
            subject=tenant_id,
            data={
                "tokens_in": tokens_in,
                "tokens_out": tokens_out,
                "tokens_total": tokens_in + tokens_out,
                "model": model,
                "session_id": str(session_id),
            },
        )
        await self._buffer_event(event)

    async def record_request(
        self,
        tenant_id: str | UUID,
        endpoint: str,
        method: str,
        status_code: int,
    ) -> None:
        """
        Record an API request.

        Args:
            tenant_id: Tenant identifier (billing subject)
            endpoint: API endpoint path
            method: HTTP method
            status_code: Response status code
        """
        event = UsageEventSchema.create(
            event_type=UsageEventType.API_REQUEST,
            subject=tenant_id,
            data={
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
            },
        )
        await self._buffer_event(event)

    async def record_session_create(
        self,
        tenant_id: str | UUID,
        session_id: str | UUID,
        agent_type: str = "kgent",
    ) -> None:
        """
        Record session creation.

        Args:
            tenant_id: Tenant identifier (billing subject)
            session_id: Created session ID
            agent_type: Type of agent
        """
        event = UsageEventSchema.create(
            event_type=UsageEventType.SESSION_CREATE,
            subject=tenant_id,
            data={
                "session_id": str(session_id),
                "agent_type": agent_type,
            },
        )
        await self._buffer_event(event)

    async def record_message(
        self,
        tenant_id: str | UUID,
        session_id: str | UUID,
        message_length: int,
        role: str = "user",
    ) -> None:
        """
        Record a message sent in a session.

        Args:
            tenant_id: Tenant identifier (billing subject)
            session_id: Session ID
            message_length: Character length of message
            role: Message role (user/assistant)
        """
        event = UsageEventSchema.create(
            event_type=UsageEventType.SESSION_MESSAGE,
            subject=tenant_id,
            data={
                "session_id": str(session_id),
                "message_length": message_length,
                "role": role,
            },
        )
        await self._buffer_event(event)

    async def record_agentese_invoke(
        self,
        tenant_id: str | UUID,
        path: str,
        aspect: str,
        tokens_used: int = 0,
    ) -> None:
        """
        Record an AGENTESE invocation.

        Args:
            tenant_id: Tenant identifier (billing subject)
            path: AGENTESE path (e.g., "self.soul.reflect")
            aspect: Aspect invoked (e.g., "manifest", "refine")
            tokens_used: Tokens consumed (if any)
        """
        event = UsageEventSchema.create(
            event_type=UsageEventType.AGENTESE_INVOKE,
            subject=tenant_id,
            data={
                "path": path,
                "aspect": aspect,
                "tokens_used": tokens_used,
            },
        )
        await self._buffer_event(event)

    # ─────────────────────────────────────────────────────────────
    # Buffering and Flushing
    # ─────────────────────────────────────────────────────────────

    async def _buffer_event(self, event: UsageEventSchema) -> None:
        """Add event to buffer, flush if full."""
        async with self._buffer_lock:
            self._buffer.append(event)

            if len(self._buffer) >= self.config.batch_size:
                await self._flush_buffer()

    async def flush(self) -> None:
        """Flush buffered events to OpenMeter."""
        async with self._buffer_lock:
            await self._flush_buffer()

    async def _flush_buffer(self) -> None:
        """Internal flush (must hold lock)."""
        if not self._buffer:
            return

        events = self._buffer
        self._buffer = []

        if self.config.is_configured:
            await self._send_to_openmeter(events)
        else:
            # Local-only mode: just count events
            self._events_sent += len(events)
            logger.debug(f"OpenMeter (local): recorded {len(events)} events")

        self._last_flush = datetime.now(UTC)

    async def _flush_loop(self) -> None:
        """Background flush loop."""
        while self._running:
            await asyncio.sleep(self.config.flush_interval_seconds)
            if self._running:
                await self.flush()

    async def _send_to_openmeter(self, events: list[UsageEventSchema]) -> None:
        """Send events to OpenMeter API."""
        if not events:
            return

        try:
            import httpx

            payload = [e.to_dict() for e in events]

            async with httpx.AsyncClient() as client:
                for attempt in range(self.config.max_retries):
                    try:
                        response = await client.post(
                            f"{self.config.base_url}/api/v1/events",
                            json=payload,
                            headers={
                                "Authorization": f"Bearer {self.config.api_key}",
                                "Content-Type": "application/json",
                            },
                            timeout=10.0,
                        )

                        if response.status_code in (200, 201, 202):
                            self._events_sent += len(events)
                            logger.debug(f"OpenMeter: sent {len(events)} events")
                            return
                        elif response.status_code == 429:
                            # Rate limited, retry with backoff
                            await asyncio.sleep(
                                self.config.retry_delay_seconds * (attempt + 1)
                            )
                        else:
                            logger.warning(
                                f"OpenMeter API error: {response.status_code} - {response.text}"
                            )
                            break

                    except httpx.TimeoutException:
                        logger.warning(f"OpenMeter timeout (attempt {attempt + 1})")
                        await asyncio.sleep(self.config.retry_delay_seconds)

            # All retries failed
            self._events_failed += len(events)
            logger.error(
                f"OpenMeter: failed to send {len(events)} events after retries"
            )

        except ImportError:
            # httpx not installed, count locally
            self._events_sent += len(events)
            logger.debug(f"OpenMeter (no httpx): recorded {len(events)} events locally")
        except Exception as e:
            self._events_failed += len(events)
            logger.error(f"OpenMeter error: {e}")

    # ─────────────────────────────────────────────────────────────
    # Metrics and Health
    # ─────────────────────────────────────────────────────────────

    def get_metrics(self) -> dict[str, Any]:
        """Get client metrics."""
        return {
            "events_sent": self._events_sent,
            "events_failed": self._events_failed,
            "events_buffered": len(self._buffer),
            "last_flush": self._last_flush.isoformat() if self._last_flush else None,
            "configured": self.config.is_configured,
            "running": self._running,
        }

    async def health_check(self) -> dict[str, Any]:
        """Check OpenMeter connectivity."""
        if not self.config.is_configured:
            return {
                "status": "disabled",
                "mode": "local",
                "metrics": self.get_metrics(),
            }

        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.config.base_url}/api/v1/meters",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                    timeout=5.0,
                )

                if response.status_code == 200:
                    return {
                        "status": "healthy",
                        "mode": "cloud",
                        "base_url": self.config.base_url,
                        "metrics": self.get_metrics(),
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "mode": "cloud",
                        "error": f"HTTP {response.status_code}",
                        "metrics": self.get_metrics(),
                    }

        except ImportError:
            return {
                "status": "degraded",
                "mode": "local",
                "error": "httpx not installed",
                "metrics": self.get_metrics(),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "mode": "cloud",
                "error": str(e),
                "metrics": self.get_metrics(),
            }
