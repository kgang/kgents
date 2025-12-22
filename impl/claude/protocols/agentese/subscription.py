"""
AGENTESE Subscription Manager

Reactive subscriptions for continuous observation of paths.

From spec §9.1:
    AGENTESE invocations are one-shot. Reactive patterns need continuous observation.

Subscription Grammar:
    # Subscribe to all memory changes
    async for event in logos.subscribe("self.memory.*"):
        print(f"Memory changed: {event.path}")

    # Subscribe with aspect filter
    async for event in logos.subscribe("world.town.*", aspect="flux"):
        ...

    # Context manager for auto-unsubscribe
    async with logos.subscription("self.memory.*") as sub:
        async for event in sub:
            if event.data.updated:
                break

Subscription Semantics (from spec §9.4):
    Delivery:   At-most-once (default), At-least-once (with ack)
    Ordering:   Per-path FIFO (default), Global clock
    Replay:     None (default), From timestamp, From offset
    Buffer:     1000 events (configurable, backpressure on full)
    Heartbeat:  30s (configurable)

Event Model (from spec §9.3):
    @dataclass
    class AgentesEvent:
        path: str               # Which path emitted
        aspect: str             # Which aspect was invoked
        timestamp: datetime
        observer_archetype: str
        data: Any               # The result/payload
        event_type: EventType   # INVOKED, CHANGED, ERROR
"""

from __future__ import annotations

import asyncio
import fnmatch
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable
from uuid import uuid4

if TYPE_CHECKING:
    from .logos import Logos
    from .node import Observer

logger = logging.getLogger(__name__)


# === Event Model ===


class EventType(Enum):
    """Type of event emitted by a subscription."""

    INVOKED = "invoked"  # Path was invoked
    CHANGED = "changed"  # State changed
    ERROR = "error"  # Error occurred
    REFUSED = "refused"  # Consent refusal
    HEARTBEAT = "heartbeat"  # Keep-alive signal


@dataclass(frozen=True)
class AgentesEvent:
    """
    Single event from an AGENTESE subscription.

    Attributes:
        path: The AGENTESE path that emitted this event
        aspect: The aspect that was invoked
        timestamp: When the event occurred
        observer_archetype: Archetype of the observer who triggered it
        data: The result/payload
        event_type: Type of event
        event_id: Unique event identifier
        trace_id: OTEL trace ID if available
    """

    path: str
    aspect: str
    timestamp: datetime
    observer_archetype: str
    data: Any
    event_type: EventType = EventType.INVOKED
    event_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str | None = None

    @classmethod
    def invoked(
        cls,
        path: str,
        aspect: str,
        data: Any,
        observer_archetype: str = "guest",
        trace_id: str | None = None,
    ) -> "AgentesEvent":
        """Create an INVOKED event."""
        return cls(
            path=path,
            aspect=aspect,
            timestamp=datetime.now(timezone.utc),
            observer_archetype=observer_archetype,
            data=data,
            event_type=EventType.INVOKED,
            trace_id=trace_id,
        )

    @classmethod
    def changed(
        cls,
        path: str,
        data: Any,
        observer_archetype: str = "system",
    ) -> "AgentesEvent":
        """Create a CHANGED event."""
        return cls(
            path=path,
            aspect="state",
            timestamp=datetime.now(timezone.utc),
            observer_archetype=observer_archetype,
            data=data,
            event_type=EventType.CHANGED,
        )

    @classmethod
    def error(
        cls,
        path: str,
        error: Exception,
        observer_archetype: str = "system",
    ) -> "AgentesEvent":
        """Create an ERROR event."""
        return cls(
            path=path,
            aspect="error",
            timestamp=datetime.now(timezone.utc),
            observer_archetype=observer_archetype,
            data={"error": str(error), "type": type(error).__name__},
            event_type=EventType.ERROR,
        )

    @classmethod
    def refused(
        cls,
        path: str,
        reason: str,
        observer_archetype: str = "system",
    ) -> "AgentesEvent":
        """Create a REFUSED event."""
        return cls(
            path=path,
            aspect="refusal",
            timestamp=datetime.now(timezone.utc),
            observer_archetype=observer_archetype,
            data={"reason": reason},
            event_type=EventType.REFUSED,
        )

    @classmethod
    def heartbeat(cls) -> "AgentesEvent":
        """Create a HEARTBEAT event."""
        return cls(
            path="system.heartbeat",
            aspect="heartbeat",
            timestamp=datetime.now(timezone.utc),
            observer_archetype="system",
            data=None,
            event_type=EventType.HEARTBEAT,
        )


# === Subscription Configuration ===


class DeliveryMode(Enum):
    """Delivery guarantee mode."""

    AT_MOST_ONCE = "at_most_once"  # Fire and forget
    AT_LEAST_ONCE = "at_least_once"  # With acknowledgment


class OrderingMode(Enum):
    """Event ordering mode."""

    PER_PATH_FIFO = "per_path_fifo"  # FIFO per path
    GLOBAL_CLOCK = "global_clock"  # Total ordering


@dataclass(frozen=True)
class SubscriptionConfig:
    """
    Configuration for a subscription.

    Attributes:
        pattern: Path pattern to subscribe to
        delivery: Delivery guarantee mode (default: at_most_once)
        ordering: Event ordering mode (default: per_path_fifo)
        buffer_size: Maximum events to buffer (default: 1000)
        heartbeat_interval: Heartbeat interval in seconds (default: 30)
        replay_from: Optional timestamp to replay from
        replay_offset: Optional offset to replay from
        aspect_filter: Optional aspect to filter on
    """

    pattern: str
    delivery: DeliveryMode = DeliveryMode.AT_MOST_ONCE
    ordering: OrderingMode = OrderingMode.PER_PATH_FIFO
    buffer_size: int = 1000
    heartbeat_interval: float = 30.0
    replay_from: datetime | None = None
    replay_offset: int | None = None
    aspect_filter: str | None = None


# === Subscription ===


@dataclass
class Subscription:
    """
    Active subscription to AGENTESE paths.

    Use as an async iterator:
        async for event in subscription:
            handle(event)

    Or with context manager:
        async with subscription:
            async for event in subscription:
                handle(event)

    For AT_LEAST_ONCE delivery:
        - Events are tracked until acknowledged
        - Unacknowledged events are redelivered after timeout
        - Use subscription.acknowledge(event_id) to confirm receipt
    """

    id: str
    config: SubscriptionConfig
    _queue: asyncio.Queue[AgentesEvent] = field(default_factory=lambda: asyncio.Queue(maxsize=1000))
    _active: bool = field(default=True)
    _acknowledged: set[str] = field(default_factory=set)
    _heartbeat_task: asyncio.Task[None] | None = field(default=None)
    _manager: "SubscriptionManager | None" = field(default=None)
    # AT_LEAST_ONCE: Track pending events for redelivery
    _pending_events: dict[str, tuple[AgentesEvent, datetime]] = field(default_factory=dict)
    _redelivery_task: asyncio.Task[None] | None = field(default=None)
    # Redelivery settings
    _redelivery_timeout: float = field(default=30.0)  # seconds
    _max_redelivery_attempts: int = field(default=3)
    _redelivery_attempts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize buffer with configured size."""
        self._queue = asyncio.Queue(maxsize=self.config.buffer_size)
        self._pending_events = {}
        self._redelivery_attempts = {}

    @property
    def pattern(self) -> str:
        """Get the subscription pattern."""
        return self.config.pattern

    @property
    def active(self) -> bool:
        """Check if subscription is active."""
        return self._active

    async def __aiter__(self) -> AsyncIterator[AgentesEvent]:
        """Async iteration over events."""
        # Start heartbeat task if configured
        if self._heartbeat_task is None and self.config.heartbeat_interval > 0:
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

        # Start redelivery task for AT_LEAST_ONCE
        if self.config.delivery == DeliveryMode.AT_LEAST_ONCE and self._redelivery_task is None:
            self._redelivery_task = asyncio.create_task(self._redelivery_loop())

        while self._active:
            try:
                event = await asyncio.wait_for(
                    self._queue.get(), timeout=self.config.heartbeat_interval
                )
                if event.event_type == EventType.HEARTBEAT:
                    # Yield heartbeat so consumers can detect liveness
                    yield event
                    continue

                # For AT_LEAST_ONCE, track the event until acknowledged
                if self.config.delivery == DeliveryMode.AT_LEAST_ONCE:
                    self._pending_events[event.event_id] = (
                        event,
                        datetime.now(timezone.utc),
                    )

                yield event
            except asyncio.TimeoutError:
                # Timeout without event - emit heartbeat
                heartbeat = AgentesEvent.heartbeat()
                yield heartbeat

    async def _heartbeat_loop(self) -> None:
        """Background task to emit periodic heartbeats."""
        while self._active:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                if self._active:
                    self._emit(AgentesEvent.heartbeat())
            except asyncio.CancelledError:
                break

    async def _redelivery_loop(self) -> None:
        """Background task to redeliver unacknowledged events (AT_LEAST_ONCE)."""
        while self._active:
            try:
                await asyncio.sleep(self._redelivery_timeout / 2)  # Check twice per timeout
                if not self._active:
                    break

                now = datetime.now(timezone.utc)
                events_to_redeliver: list[AgentesEvent] = []

                for event_id, (event, sent_at) in list(self._pending_events.items()):
                    # Check if already acknowledged
                    if event_id in self._acknowledged:
                        del self._pending_events[event_id]
                        continue

                    # Check if timeout exceeded
                    age = (now - sent_at).total_seconds()
                    if age > self._redelivery_timeout:
                        attempts = self._redelivery_attempts.get(event_id, 0)
                        if attempts < self._max_redelivery_attempts:
                            events_to_redeliver.append(event)
                            self._redelivery_attempts[event_id] = attempts + 1
                            # Reset sent time for next timeout check
                            self._pending_events[event_id] = (event, now)
                        else:
                            # Max attempts reached, drop the event
                            logger.warning(
                                f"Subscription {self.id}: Dropping event {event_id} "
                                f"after {attempts} redelivery attempts"
                            )
                            del self._pending_events[event_id]
                            del self._redelivery_attempts[event_id]

                # Redeliver events
                for event in events_to_redeliver:
                    logger.debug(f"Subscription {self.id}: Redelivering event {event.event_id}")
                    self._emit(event)

            except asyncio.CancelledError:
                break

    async def __aenter__(self) -> "Subscription":
        """Enter context manager."""
        return self

    async def __aexit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any
    ) -> None:
        """Exit context manager, close subscription."""
        await self.close()

    async def close(self) -> None:
        """Close the subscription."""
        self._active = False
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        if self._redelivery_task is not None:
            self._redelivery_task.cancel()
            try:
                await self._redelivery_task
            except asyncio.CancelledError:
                pass
        if self._manager is not None:
            await self._manager.unsubscribe(self.id)

    def _emit(self, event: AgentesEvent) -> bool:
        """
        Emit an event to the subscription.

        Returns:
            True if event was queued, False if buffer full (backpressure)
        """
        if not self._active:
            return False

        try:
            self._queue.put_nowait(event)
            return True
        except asyncio.QueueFull:
            logger.warning(f"Subscription {self.id} buffer full, dropping event for {event.path}")
            return False

    def _matches(self, path: str, aspect: str | None = None) -> bool:
        """Check if a path/aspect matches this subscription."""
        # Check path pattern
        if not _matches_pattern(path, self.config.pattern):
            return False

        # Check aspect filter
        if self.config.aspect_filter and aspect:
            if not _matches_pattern(aspect, self.config.aspect_filter):
                return False

        return True

    def acknowledge(self, event_id: str) -> bool:
        """
        Acknowledge receipt of an event (for AT_LEAST_ONCE).

        Args:
            event_id: The event ID to acknowledge

        Returns:
            True if the event was pending, False if already acknowledged or not found
        """
        if event_id in self._acknowledged:
            return False

        self._acknowledged.add(event_id)

        # Remove from pending events
        if event_id in self._pending_events:
            del self._pending_events[event_id]
            if event_id in self._redelivery_attempts:
                del self._redelivery_attempts[event_id]
            return True

        return False

    def pending_count(self) -> int:
        """Get number of pending events in buffer."""
        return self._queue.qsize()


# === Pattern Matching ===


def _matches_pattern(value: str, pattern: str) -> bool:
    """
    Check if a value matches a pattern.

    Patterns:
        "*"  - matches any single segment
        "**" - matches any path (multiple segments)
        "foo" - exact match
        "foo.*" - foo followed by any single segment
        "foo.**" - foo followed by anything (multiple segments)
    """
    import re

    # Handle pure wildcards
    if pattern == "*" or pattern == "**":
        return True

    # Convert pattern to regex
    if "*" in pattern:
        # Replace ** with a placeholder first to avoid confusion
        DOUBLE_STAR = "\x00DOUBLE_STAR\x00"
        regex_pattern = pattern.replace("**", DOUBLE_STAR)
        # Escape dots
        regex_pattern = regex_pattern.replace(".", r"\.")
        # Single * matches any characters except dots (single segment)
        regex_pattern = regex_pattern.replace("*", r"[^.]*")
        # Double ** matches anything including dots (greedy)
        regex_pattern = regex_pattern.replace(DOUBLE_STAR, ".*")
        return bool(re.match(f"^{regex_pattern}$", value))

    return value == pattern


# === Subscription Manager ===


@dataclass
class SubscriptionManager:
    """
    Manager for AGENTESE subscriptions.

    Handles:
    - Subscription lifecycle
    - Event routing
    - Heartbeat management
    - Metrics

    Example:
        manager = SubscriptionManager()

        # Create subscription
        sub = await manager.subscribe("self.memory.*")

        # Iterate events
        async for event in sub:
            print(event)

        # Or with context manager
        async with manager.subscription("world.town.*") as sub:
            async for event in sub:
                handle(event)
    """

    _subscriptions: dict[str, Subscription] = field(default_factory=dict)
    _pattern_index: dict[str, set[str]] = field(default_factory=dict)
    _heartbeat_task: asyncio.Task[None] | None = field(default=None)
    _active: bool = field(default=True)

    # Callbacks for integration
    _on_subscribe: Callable[[str, SubscriptionConfig], None] | None = None
    _on_unsubscribe: Callable[[str], None] | None = None
    _on_event: Callable[[str, AgentesEvent], None] | None = None

    async def subscribe(
        self,
        pattern: str,
        *,
        delivery: DeliveryMode = DeliveryMode.AT_MOST_ONCE,
        ordering: OrderingMode = OrderingMode.PER_PATH_FIFO,
        buffer_size: int = 1000,
        heartbeat_interval: float = 30.0,
        replay_from: datetime | None = None,
        replay_offset: int | None = None,
        aspect: str | None = None,
    ) -> Subscription:
        """
        Create a new subscription.

        Args:
            pattern: Path pattern to subscribe to (e.g., "self.memory.*")
            delivery: Delivery guarantee mode
            ordering: Event ordering mode
            buffer_size: Maximum events to buffer
            heartbeat_interval: Heartbeat interval in seconds
            replay_from: Optional timestamp to replay events from
            replay_offset: Optional offset to replay events from
            aspect: Optional aspect filter

        Returns:
            Active Subscription

        Example:
            sub = await manager.subscribe("self.memory.*")
            async for event in sub:
                print(f"Memory changed: {event.path}")
        """
        config = SubscriptionConfig(
            pattern=pattern,
            delivery=delivery,
            ordering=ordering,
            buffer_size=buffer_size,
            heartbeat_interval=heartbeat_interval,
            replay_from=replay_from,
            replay_offset=replay_offset,
            aspect_filter=aspect,
        )

        sub_id = str(uuid4())
        subscription = Subscription(
            id=sub_id,
            config=config,
            _manager=self,
        )

        self._subscriptions[sub_id] = subscription

        # Index by pattern prefix for efficient routing
        # Handle special patterns:
        # - "**" matches everything (index under "**")
        # - "*" matches any single segment (index under "*")
        # - "*.foo" matches any context with foo holon (index under "*")
        # - "world.*" matches all in world context (index under "world")
        if pattern == "**":
            prefix = "**"
        elif pattern.startswith("**"):
            # e.g., "**.manifest" - catch-all pattern
            prefix = "**"
        elif pattern.startswith("*"):
            # e.g., "*" or "*.foo" - wildcard patterns
            prefix = "*"
        else:
            # Normal prefix (e.g., "world" from "world.foo")
            prefix = pattern.split(".")[0] if "." in pattern else pattern
        if prefix not in self._pattern_index:
            self._pattern_index[prefix] = set()
        self._pattern_index[prefix].add(sub_id)

        # Callback
        if self._on_subscribe:
            self._on_subscribe(sub_id, config)

        logger.debug(f"Created subscription {sub_id} for pattern {pattern}")

        return subscription

    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Remove a subscription.

        Args:
            subscription_id: ID of subscription to remove

        Returns:
            True if subscription was removed, False if not found
        """
        if subscription_id not in self._subscriptions:
            return False

        subscription = self._subscriptions[subscription_id]
        subscription._active = False

        # Remove from index (use same prefix calculation as subscribe)
        pattern = subscription.config.pattern
        if pattern == "**":
            prefix = "**"
        elif pattern.startswith("**"):
            prefix = "**"
        elif pattern.startswith("*"):
            prefix = "*"
        else:
            prefix = pattern.split(".")[0] if "." in pattern else pattern
        if prefix in self._pattern_index:
            self._pattern_index[prefix].discard(subscription_id)
            if not self._pattern_index[prefix]:
                del self._pattern_index[prefix]

        del self._subscriptions[subscription_id]

        # Callback
        if self._on_unsubscribe:
            self._on_unsubscribe(subscription_id)

        logger.debug(f"Removed subscription {subscription_id}")

        return True

    @asynccontextmanager
    async def subscription(
        self,
        pattern: str,
        **kwargs: Any,
    ) -> AsyncIterator[Subscription]:
        """
        Context manager for subscriptions.

        Example:
            async with manager.subscription("self.memory.*") as sub:
                async for event in sub:
                    if event.data.updated:
                        break
        """
        sub = await self.subscribe(pattern, **kwargs)
        try:
            yield sub
        finally:
            await sub.close()

    def emit(
        self,
        path: str,
        aspect: str,
        data: Any,
        observer_archetype: str = "guest",
        event_type: EventType = EventType.INVOKED,
        trace_id: str | None = None,
    ) -> int:
        """
        Emit an event to all matching subscriptions.

        Args:
            path: The AGENTESE path that emitted
            aspect: The aspect that was invoked
            data: The result/payload
            observer_archetype: Archetype of observer
            event_type: Type of event
            trace_id: Optional OTEL trace ID

        Returns:
            Number of subscriptions that received the event
        """
        event = AgentesEvent(
            path=path,
            aspect=aspect,
            timestamp=datetime.now(timezone.utc),
            observer_archetype=observer_archetype,
            data=data,
            event_type=event_type,
            trace_id=trace_id,
        )

        return self.emit_event(event)

    def emit_event(self, event: AgentesEvent) -> int:
        """
        Emit a pre-built event to all matching subscriptions.

        Returns:
            Number of subscriptions that received the event
        """
        # Get potential subscriptions by prefix
        prefix = event.path.split(".")[0] if "." in event.path else event.path
        potential_sub_ids: set[str] = set()

        # Check prefix-indexed subscriptions
        if prefix in self._pattern_index:
            potential_sub_ids.update(self._pattern_index[prefix])

        # Check wildcard subscriptions (* patterns)
        if "*" in self._pattern_index:
            potential_sub_ids.update(self._pattern_index["*"])

        # Check catch-all subscriptions (** patterns)
        if "**" in self._pattern_index:
            potential_sub_ids.update(self._pattern_index["**"])

        delivered = 0
        for sub_id in potential_sub_ids:
            subscription = self._subscriptions.get(sub_id)
            if subscription and subscription._matches(event.path, event.aspect):
                if subscription._emit(event):
                    delivered += 1
                    # Callback
                    if self._on_event:
                        self._on_event(sub_id, event)

        return delivered

    def emit_invoked(
        self,
        path: str,
        aspect: str,
        data: Any,
        observer_archetype: str = "guest",
        trace_id: str | None = None,
    ) -> int:
        """Convenience method to emit an INVOKED event."""
        return self.emit(
            path=path,
            aspect=aspect,
            data=data,
            observer_archetype=observer_archetype,
            event_type=EventType.INVOKED,
            trace_id=trace_id,
        )

    def emit_changed(
        self,
        path: str,
        data: Any,
    ) -> int:
        """Convenience method to emit a CHANGED event."""
        return self.emit(
            path=path,
            aspect="state",
            data=data,
            observer_archetype="system",
            event_type=EventType.CHANGED,
        )

    def emit_error(
        self,
        path: str,
        error: Exception,
    ) -> int:
        """Convenience method to emit an ERROR event."""
        return self.emit(
            path=path,
            aspect="error",
            data={"error": str(error), "type": type(error).__name__},
            observer_archetype="system",
            event_type=EventType.ERROR,
        )

    def list_subscriptions(self) -> list[dict[str, Any]]:
        """List all active subscriptions with their status."""
        return [
            {
                "id": sub.id,
                "pattern": sub.config.pattern,
                "active": sub.active,
                "pending": sub.pending_count(),
                "delivery": sub.config.delivery.value,
                "buffer_size": sub.config.buffer_size,
            }
            for sub in self._subscriptions.values()
        ]

    def get_subscription(self, subscription_id: str) -> Subscription | None:
        """Get a subscription by ID."""
        return self._subscriptions.get(subscription_id)

    @property
    def subscription_count(self) -> int:
        """Number of active subscriptions."""
        return len(self._subscriptions)

    async def close(self) -> None:
        """Close all subscriptions and cleanup."""
        self._active = False
        for sub in list(self._subscriptions.values()):
            await sub.close()
        self._subscriptions.clear()
        self._pattern_index.clear()


# === Logos Integration ===


class LogosSubscriptionMixin:
    """
    Mixin to add subscription methods to Logos.

    This is wired in by add_subscription_methods_to_logos().
    """

    _subscription_manager: SubscriptionManager | None = None

    def _get_subscription_manager(self) -> SubscriptionManager:
        """Get or create the subscription manager."""
        if self._subscription_manager is None:
            self._subscription_manager = SubscriptionManager()
        return self._subscription_manager

    async def subscribe(
        self,
        pattern: str,
        **kwargs: Any,
    ) -> Subscription:
        """
        Subscribe to AGENTESE path events.

        Args:
            pattern: Path pattern (e.g., "self.memory.*")
            **kwargs: Subscription options

        Returns:
            Active Subscription

        Example:
            async for event in logos.subscribe("self.memory.*"):
                print(f"Memory changed: {event.path}")
        """
        manager = self._get_subscription_manager()
        return await manager.subscribe(pattern, **kwargs)

    @asynccontextmanager
    async def subscription(
        self,
        pattern: str,
        **kwargs: Any,
    ) -> AsyncIterator[Subscription]:
        """
        Context manager for subscriptions.

        Example:
            async with logos.subscription("self.memory.*") as sub:
                async for event in sub:
                    if event.data.updated:
                        break
        """
        manager = self._get_subscription_manager()
        async with manager.subscription(pattern, **kwargs) as sub:
            yield sub


def add_subscription_methods_to_logos(logos_cls: type) -> type:
    """
    Add subscription methods to Logos class.

    This adds:
    - logos.subscribe(pattern): Create subscription
    - logos.subscription(pattern): Context manager
    - logos._emit_subscription_event(): Internal event emission
    - logos._subscription_manager: Lazy subscription manager

    Args:
        logos_cls: The Logos class to extend

    Returns:
        The modified class (for chaining)
    """
    # Add _subscription_manager property
    if not hasattr(logos_cls, "_subscription_manager"):
        logos_cls._subscription_manager = None  # type: ignore[attr-defined]

    def _get_subscription_manager(self: Any) -> SubscriptionManager:
        """Get or create the subscription manager."""
        if self._subscription_manager is None:
            self._subscription_manager = SubscriptionManager()
        manager: SubscriptionManager = self._subscription_manager
        return manager

    async def subscribe(
        self: Any,
        pattern: str,
        **kwargs: Any,
    ) -> Subscription:
        """
        Subscribe to AGENTESE path events.

        Args:
            pattern: Path pattern (e.g., "self.memory.*")
            **kwargs: Subscription options (delivery, ordering, buffer_size, etc.)

        Returns:
            Active Subscription

        Example:
            async for event in logos.subscribe("self.memory.*"):
                print(f"Memory changed: {event.path}")
        """
        manager = _get_subscription_manager(self)
        return await manager.subscribe(pattern, **kwargs)

    @asynccontextmanager
    async def subscription(
        self: Any,
        pattern: str,
        **kwargs: Any,
    ) -> AsyncIterator[Subscription]:
        """
        Context manager for subscriptions.

        Example:
            async with logos.subscription("self.memory.*") as sub:
                async for event in sub:
                    if event.data.updated:
                        break
        """
        manager = _get_subscription_manager(self)
        async with manager.subscription(pattern, **kwargs) as sub:
            yield sub

    def _emit_subscription_event(
        self: Any,
        path: str,
        aspect: str,
        data: Any,
        observer_archetype: str = "guest",
        event_type: EventType = EventType.INVOKED,
        trace_id: str | None = None,
    ) -> int:
        """
        Emit an event to all matching subscriptions.

        Returns:
            Number of subscriptions that received the event
        """
        if self._subscription_manager is None:
            return 0
        manager: SubscriptionManager = self._subscription_manager
        return manager.emit(
            path=path,
            aspect=aspect,
            data=data,
            observer_archetype=observer_archetype,
            event_type=event_type,
            trace_id=trace_id,
        )

    # Wire methods if not already present
    if not hasattr(logos_cls, "_get_subscription_manager"):
        logos_cls._get_subscription_manager = _get_subscription_manager  # type: ignore[attr-defined]
    if not hasattr(logos_cls, "subscribe"):
        logos_cls.subscribe = subscribe  # type: ignore[attr-defined]
    if not hasattr(logos_cls, "subscription"):
        logos_cls.subscription = subscription  # type: ignore[attr-defined]
    if not hasattr(logos_cls, "_emit_subscription_event"):
        logos_cls._emit_subscription_event = _emit_subscription_event  # type: ignore[attr-defined]

    return logos_cls


# === Metrics (from spec §9.5) ===


@dataclass
class SubscriptionMetrics:
    """
    Metrics for subscription observability.

    From spec §9.5:
        agentese_subscription_active{pattern, tenant}
        agentese_subscription_events_delivered{pattern, event_type}
        agentese_subscription_events_dropped{pattern, reason}
        agentese_subscription_lag_seconds{pattern}
    """

    active_subscriptions: int = 0
    events_delivered: int = 0
    events_dropped: int = 0
    total_lag_seconds: float = 0.0

    def record_delivered(self, count: int = 1) -> None:
        """Record delivered events."""
        self.events_delivered += count

    def record_dropped(self, count: int = 1) -> None:
        """Record dropped events."""
        self.events_dropped += count

    def record_lag(self, seconds: float) -> None:
        """Record subscription lag."""
        self.total_lag_seconds += seconds

    def to_dict(self) -> dict[str, Any]:
        """Export as dictionary."""
        return {
            "active_subscriptions": self.active_subscriptions,
            "events_delivered": self.events_delivered,
            "events_dropped": self.events_dropped,
            "total_lag_seconds": self.total_lag_seconds,
            "avg_lag_seconds": (
                self.total_lag_seconds / self.events_delivered if self.events_delivered > 0 else 0.0
            ),
        }


# === Factory Functions ===


def create_subscription_manager(
    *,
    on_subscribe: Callable[[str, SubscriptionConfig], None] | None = None,
    on_unsubscribe: Callable[[str], None] | None = None,
    on_event: Callable[[str, AgentesEvent], None] | None = None,
) -> SubscriptionManager:
    """
    Create a subscription manager with optional callbacks.

    Args:
        on_subscribe: Called when subscription is created
        on_unsubscribe: Called when subscription is removed
        on_event: Called when event is delivered

    Returns:
        Configured SubscriptionManager
    """
    manager = SubscriptionManager()
    manager._on_subscribe = on_subscribe
    manager._on_unsubscribe = on_unsubscribe
    manager._on_event = on_event
    return manager
