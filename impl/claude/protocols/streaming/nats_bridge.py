"""
NATS JetStream bridge for kgents streaming.

Provides real-time event streaming for SSE and inter-agent communication.
Bridges KgentFlux events to NATS JetStream for multi-consumer scenarios.

Architecture:
    KgentFlux → NATSBridge → JetStream → SSE consumers
                          → Metering processor
                          → Terrarium observers

Usage:
    from protocols.streaming import NATSBridge, NATSBridgeConfig

    config = NATSBridgeConfig(servers=["nats://localhost:4222"])
    bridge = NATSBridge(config)

    async with bridge:
        # Publish events
        await bridge.publish_soul_event(session_id, event)

        # Subscribe to session events
        async for event in bridge.subscribe_session(session_id):
            yield f"event: chunk\\ndata: {event.to_json()}\\n\\n"
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Literal, Optional
from uuid import UUID

# OpenTelemetry tracing (optional)
try:
    from opentelemetry import trace

    _tracer = trace.get_tracer("kgents.streaming.nats", "0.1.0")
    HAS_OTEL = True
except ImportError:
    _tracer = None  # type: ignore[assignment]
    HAS_OTEL = False

if TYPE_CHECKING:
    from agents.k.events import SoulEvent

logger = logging.getLogger(__name__)


class NATSConnectionError(Exception):
    """Raised when NATS connection fails."""

    pass


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, using fallback
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for NATS connection resilience.

    Prevents cascade failures by stopping attempts to use NATS
    when it's consistently failing, and automatically recovers
    when the connection is healthy again.
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0  # seconds

    # State
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failures: int = field(default=0, init=False)
    _last_failure: Optional[datetime] = field(default=None, init=False)
    _successes_in_half_open: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    def should_allow_request(self) -> bool:
        """
        Determine if a request should be allowed.

        Returns:
            True if request should proceed, False to use fallback.
        """
        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            # Check if we should try half-open
            if self._last_failure and self._should_attempt_recovery():
                self._state = CircuitState.HALF_OPEN
                self._successes_in_half_open = 0
                logger.info("Circuit breaker entering half-open state")
                return True
            return False

        # Half-open: allow limited requests to test recovery
        return True

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure is None:
            return True
        elapsed = (datetime.now(UTC) - self._last_failure).total_seconds()
        return elapsed >= self.recovery_timeout

    def record_success(self) -> None:
        """Record a successful operation."""
        if self._state == CircuitState.HALF_OPEN:
            self._successes_in_half_open += 1
            # Require 3 successes to close circuit
            if self._successes_in_half_open >= 3:
                self._state = CircuitState.CLOSED
                self._failures = 0
                logger.info("Circuit breaker closed after recovery")
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failures = 0

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._failures += 1
        self._last_failure = datetime.now(UTC)

        if self._state == CircuitState.HALF_OPEN:
            # Immediately open on any failure in half-open
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker re-opened after half-open failure")
        elif self._state == CircuitState.CLOSED:
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker opened after {self._failures} failures"
                )

    def reset(self) -> None:
        """Reset circuit breaker to initial state."""
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._last_failure = None
        self._successes_in_half_open = 0

    def to_dict(self) -> dict[str, Any]:
        """Get circuit breaker status as dictionary."""
        return {
            "state": self._state.value,
            "failures": self._failures,
            "last_failure": self._last_failure.isoformat()
            if self._last_failure
            else None,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout": self.recovery_timeout,
        }


@dataclass
class NATSBridgeConfig:
    """Configuration for NATS JetStream bridge."""

    # Connection
    servers: list[str] = field(default_factory=lambda: ["nats://localhost:4222"])
    connect_timeout: float = 5.0
    reconnect_time_wait: float = 1.0
    max_reconnect_attempts: int = 10

    # JetStream stream configuration
    stream_name: str = "kgent-events"
    stream_subjects: list[str] = field(default_factory=lambda: ["kgent.>"])
    stream_max_age_hours: int = 168  # 7 days
    stream_max_msgs_per_subject: int = 10000

    # Consumer configuration
    consumer_batch_size: int = 10
    consumer_timeout: float = 0.1
    consumer_max_deliver: int = 3

    # Feature flags
    enabled: bool = True  # Can disable for local development


@dataclass
class NATSBridge:
    """
    NATS JetStream bridge for real-time event streaming.

    Provides publish/subscribe for KgentFlux events via NATS JetStream,
    enabling multi-consumer scenarios (SSE, metering, observability).

    Includes circuit breaker for resilience against cascading failures.
    """

    config: NATSBridgeConfig = field(default_factory=NATSBridgeConfig)

    # NATS client state (set on connect)
    _nc: Any = field(default=None, init=False, repr=False)
    _js: Any = field(default=None, init=False, repr=False)
    _connected: bool = field(default=False, init=False)

    # Circuit breaker for resilience
    _circuit: CircuitBreaker = field(default_factory=CircuitBreaker, init=False)

    # Graceful degradation when NATS unavailable
    _fallback_queues: dict[str, asyncio.Queue[dict[str, Any]]] = field(
        default_factory=dict, init=False, repr=False
    )

    @property
    def circuit_breaker(self) -> CircuitBreaker:
        """Get the circuit breaker instance."""
        return self._circuit

    async def connect(self) -> None:
        """
        Connect to NATS and initialize JetStream.

        Raises:
            NATSConnectionError: If connection fails after retries
        """
        if not self.config.enabled:
            logger.info("NATS bridge disabled, using in-memory fallback")
            return

        try:
            import nats
            from nats.js.api import StreamConfig

            self._nc = await nats.connect(
                servers=self.config.servers,
                connect_timeout=self.config.connect_timeout,
                reconnect_time_wait=self.config.reconnect_time_wait,
                max_reconnect_attempts=self.config.max_reconnect_attempts,
            )

            self._js = self._nc.jetstream()

            # Ensure stream exists
            try:
                await self._js.stream_info(self.config.stream_name)
                logger.info(f"Connected to existing stream: {self.config.stream_name}")
            except Exception:
                # Create stream if it doesn't exist
                stream_config = StreamConfig(
                    name=self.config.stream_name,
                    subjects=self.config.stream_subjects,
                    max_age=self.config.stream_max_age_hours
                    * 3600
                    * 1_000_000_000,  # nanoseconds
                    max_msgs_per_subject=self.config.stream_max_msgs_per_subject,
                )
                await self._js.add_stream(stream_config)
                logger.info(f"Created stream: {self.config.stream_name}")

            self._connected = True
            logger.info(f"NATS bridge connected to {self.config.servers}")

        except ImportError:
            logger.warning("nats-py not installed, using in-memory fallback")
            self._connected = False
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            self._connected = False
            # Don't raise - graceful degradation

    async def disconnect(self) -> None:
        """Disconnect from NATS."""
        if self._nc is not None:
            try:
                await self._nc.close()
            except Exception as e:
                logger.warning(f"Error closing NATS connection: {e}")
            finally:
                self._nc = None
                self._js = None
                self._connected = False

    async def __aenter__(self) -> "NATSBridge":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._connected and self._nc is not None

    # ─────────────────────────────────────────────────────────────
    # Publishing
    # ─────────────────────────────────────────────────────────────

    async def publish_soul_event(
        self,
        session_id: str | UUID,
        event: "SoulEvent",
    ) -> None:
        """
        Publish a SoulEvent to JetStream.

        Uses circuit breaker to prevent cascade failures.

        Args:
            session_id: Session identifier
            event: SoulEvent to publish
        """
        session_id_str = str(session_id)
        subject = f"kgent.session.{session_id_str}.{event.event_type.value}"
        payload = event.to_dict()

        # Check circuit breaker first
        if not self._circuit.should_allow_request():
            await self._fallback_publish(session_id_str, payload)
            return

        if self.is_connected:
            try:
                await self._js.publish(
                    subject,
                    json.dumps(payload).encode("utf-8"),
                )
                self._circuit.record_success()
            except Exception as e:
                self._circuit.record_failure()
                logger.warning(f"NATS publish failed, using fallback: {e}")
                await self._fallback_publish(session_id_str, payload)
        else:
            await self._fallback_publish(session_id_str, payload)

    async def publish_chunk(
        self,
        session_id: str | UUID,
        chunk_text: str,
        chunk_index: int,
    ) -> None:
        """
        Publish a streaming chunk to JetStream.

        Uses circuit breaker to prevent cascade failures.
        Creates OpenTelemetry span when tracing is enabled.

        Args:
            session_id: Session identifier
            chunk_text: Text content of the chunk
            chunk_index: Index of the chunk in the stream
        """
        session_id_str = str(session_id)
        subject = f"kgent.session.{session_id_str}.chunk"
        payload = {
            "type": "chunk",
            "session_id": session_id_str,
            "text": chunk_text,
            "index": chunk_index,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Create span if tracing enabled
        span_context = None
        if HAS_OTEL and _tracer is not None:
            span_context = _tracer.start_as_current_span(
                "nats.publish_chunk",
                attributes={
                    "nats.session_id": session_id_str,
                    "nats.chunk_index": chunk_index,
                    "nats.subject": subject,
                    "nats.circuit_state": self._circuit.state.value,
                },
            )

        try:
            if span_context:
                span_context.__enter__()

            # Check circuit breaker first
            if not self._circuit.should_allow_request():
                if span_context:
                    span_context.__exit__(None, None, None)
                await self._fallback_publish(session_id_str, payload)
                return

            if self.is_connected:
                try:
                    await self._js.publish(
                        subject,
                        json.dumps(payload).encode("utf-8"),
                    )
                    self._circuit.record_success()
                except Exception as e:
                    self._circuit.record_failure()
                    logger.warning(f"NATS chunk publish failed: {e}")
                    await self._fallback_publish(session_id_str, payload)
            else:
                await self._fallback_publish(session_id_str, payload)
        finally:
            if span_context:
                span_context.__exit__(None, None, None)

    async def _fallback_publish(
        self,
        session_id: str,
        payload: dict[str, Any],
    ) -> None:
        """Fallback publish to in-memory queue when NATS unavailable."""
        if session_id not in self._fallback_queues:
            self._fallback_queues[session_id] = asyncio.Queue(maxsize=1000)

        try:
            self._fallback_queues[session_id].put_nowait(payload)
        except asyncio.QueueFull:
            # Drop oldest if full
            try:
                self._fallback_queues[session_id].get_nowait()
                self._fallback_queues[session_id].put_nowait(payload)
            except asyncio.QueueEmpty:
                pass

    # ─────────────────────────────────────────────────────────────
    # Subscribing
    # ─────────────────────────────────────────────────────────────

    async def subscribe_session(
        self,
        session_id: str | UUID,
        from_beginning: bool = False,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Subscribe to events for a session.

        Args:
            session_id: Session identifier
            from_beginning: If True, replay from stream start

        Yields:
            Event payloads as dictionaries
        """
        session_id_str = str(session_id)

        if self.is_connected:
            async for event in self._jetstream_subscribe(
                session_id_str, from_beginning
            ):
                yield event
        else:
            async for event in self._fallback_subscribe(session_id_str):
                yield event

    async def _jetstream_subscribe(
        self,
        session_id: str,
        from_beginning: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """Subscribe via JetStream pull consumer."""
        from nats.js.api import ConsumerConfig, DeliverPolicy

        subject = f"kgent.session.{session_id}.>"
        durable_name = f"sse-{session_id}"

        deliver_policy = DeliverPolicy.ALL if from_beginning else DeliverPolicy.NEW

        try:
            psub = await self._js.pull_subscribe(
                subject,
                durable=durable_name,
                config=ConsumerConfig(
                    deliver_policy=deliver_policy,
                    max_deliver=self.config.consumer_max_deliver,
                ),
            )

            while True:
                try:
                    msgs = await psub.fetch(
                        batch=self.config.consumer_batch_size,
                        timeout=self.config.consumer_timeout,
                    )
                    for msg in msgs:
                        try:
                            payload = json.loads(msg.data.decode("utf-8"))
                            yield payload
                            await msg.ack()
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in message: {msg.data}")
                            await msg.nak()
                except asyncio.TimeoutError:
                    # No messages available, yield control
                    await asyncio.sleep(0.01)
                except Exception as e:
                    logger.error(f"JetStream subscribe error: {e}")
                    break

        except Exception as e:
            logger.error(f"Failed to create JetStream subscription: {e}")

    async def _fallback_subscribe(
        self,
        session_id: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """Subscribe via in-memory fallback queue."""
        if session_id not in self._fallback_queues:
            self._fallback_queues[session_id] = asyncio.Queue(maxsize=1000)

        queue = self._fallback_queues[session_id]

        while True:
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield payload
            except asyncio.TimeoutError:
                # Yield control periodically
                await asyncio.sleep(0.01)

    # ─────────────────────────────────────────────────────────────
    # Batch Operations (for metering)
    # ─────────────────────────────────────────────────────────────

    async def consume_batch(
        self,
        consumer_name: str,
        subject_filter: str,
        batch_size: int = 100,
        timeout: float = 1.0,
    ) -> list[dict[str, Any]]:
        """
        Consume a batch of messages (for metering/processing).

        Args:
            consumer_name: Durable consumer name
            subject_filter: Subject filter pattern
            batch_size: Maximum messages to fetch
            timeout: Fetch timeout in seconds

        Returns:
            List of message payloads
        """
        if not self.is_connected:
            return []

        try:
            psub = await self._js.pull_subscribe(
                subject_filter,
                durable=consumer_name,
            )

            msgs = await psub.fetch(batch=batch_size, timeout=timeout)
            results = []

            for msg in msgs:
                try:
                    payload = json.loads(msg.data.decode("utf-8"))
                    results.append(payload)
                    await msg.ack()
                except Exception as e:
                    logger.warning(f"Error processing message: {e}")
                    await msg.nak()

            return results

        except asyncio.TimeoutError:
            return []
        except Exception as e:
            logger.error(f"Batch consume error: {e}")
            return []

    # ─────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────

    async def health_check(self) -> dict[str, Any]:
        """
        Check NATS connection health.

        Returns:
            Health status dictionary including circuit breaker status
        """
        base_status = {
            "circuit_breaker": self._circuit.to_dict(),
            "fallback_queues": len(self._fallback_queues),
        }

        if not self.config.enabled:
            return {
                **base_status,
                "status": "disabled",
                "mode": "fallback",
            }

        if not self.is_connected:
            return {
                **base_status,
                "status": "disconnected",
                "mode": "fallback",
            }

        # Check if circuit is open
        if not self._circuit.is_closed:
            return {
                **base_status,
                "status": "circuit_open",
                "mode": "fallback",
                "servers": self.config.servers,
            }

        try:
            # Try to get stream info as health probe
            await self._js.stream_info(self.config.stream_name)
            return {
                **base_status,
                "status": "healthy",
                "mode": "jetstream",
                "servers": self.config.servers,
                "stream": self.config.stream_name,
            }
        except Exception as e:
            return {
                **base_status,
                "status": "unhealthy",
                "mode": "fallback",
                "error": str(e),
            }
