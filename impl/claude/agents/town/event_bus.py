"""
EventBus: Fan-out event distribution for Agent Town.

Decouples event generation (TownFlux.step()) from consumption
(SSE endpoints, NATS bridge, widgets, metering).

Pattern:
    Producer publishes once → all subscribers receive.

Architecture:
    TownFlux.step()
        │
        ▼
    EventBus[TownEvent]
        │
        ├─► SSE Subscriber (dashboard)
        ├─► NATS Subscriber (distributed)
        ├─► Widget Subscriber (isometric)
        └─► Metrics Subscriber (metering)

See: plans/purring-squishing-duckling.md Phase 1
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Generic, TypeVar

T = TypeVar("T")


@dataclass
class EventBusStats:
    """Statistics for event bus monitoring."""

    events_published: int = 0
    events_delivered: int = 0
    subscribers_current: int = 0
    subscribers_peak: int = 0
    queue_overflow_count: int = 0


@dataclass
class EventBus(Generic[T]):
    """
    Fan-out event distribution with multiple subscribers.

    Thread-safe async event bus using asyncio.Queue for each subscriber.
    Supports backpressure via bounded queues.

    Example:
        bus = EventBus[TownEvent]()

        # Subscribe (returns async iterator)
        async def consumer():
            async for event in bus.subscribe():
                process(event)

        # Publish (delivers to all subscribers)
        await bus.publish(event)

        # Cleanup
        bus.close()
    """

    max_queue_size: int = 1000
    _subscribers: list[asyncio.Queue[T | None]] = field(default_factory=list)
    _stats: EventBusStats = field(default_factory=EventBusStats)
    _closed: bool = False

    async def publish(self, event: T) -> int:
        """
        Publish event to all subscribers.

        Returns count of subscribers that received the event.
        Non-blocking: drops events if subscriber queue is full.
        """
        if self._closed:
            return 0

        self._stats.events_published += 1
        delivered = 0

        for queue in self._subscribers:
            try:
                queue.put_nowait(event)
                delivered += 1
            except asyncio.QueueFull:
                self._stats.queue_overflow_count += 1
                # Drop event for slow subscriber (backpressure)

        self._stats.events_delivered += delivered
        return delivered

    def subscribe(self) -> Subscription[T]:
        """
        Create new subscription.

        Returns Subscription that yields events as async iterator.
        Call subscription.close() when done.
        """
        if self._closed:
            raise RuntimeError("EventBus is closed")

        queue: asyncio.Queue[T | None] = asyncio.Queue(maxsize=self.max_queue_size)
        self._subscribers.append(queue)
        self._stats.subscribers_current += 1
        self._stats.subscribers_peak = max(
            self._stats.subscribers_peak, self._stats.subscribers_current
        )

        return Subscription(bus=self, queue=queue)

    def _unsubscribe(self, queue: asyncio.Queue[T | None]) -> None:
        """Remove subscriber queue. Called by Subscription.close()."""
        if queue in self._subscribers:
            self._subscribers.remove(queue)
            self._stats.subscribers_current -= 1

    def close(self) -> None:
        """
        Close all subscriber queues.

        Sends None sentinel to unblock waiting subscribers.
        """
        self._closed = True
        for queue in self._subscribers:
            try:
                queue.put_nowait(None)  # Sentinel to stop iteration
            except asyncio.QueueFull:
                pass
        self._subscribers.clear()
        self._stats.subscribers_current = 0

    @property
    def stats(self) -> EventBusStats:
        """Get current statistics."""
        return self._stats

    @property
    def subscriber_count(self) -> int:
        """Number of active subscribers."""
        return len(self._subscribers)

    @property
    def is_closed(self) -> bool:
        """Whether the bus is closed."""
        return self._closed


@dataclass
class Subscription(Generic[T]):
    """
    Single subscription to an EventBus.

    Use as async iterator to receive events.
    Must call close() when done to avoid resource leaks.

    Example:
        sub = bus.subscribe()
        try:
            async for event in sub:
                process(event)
        finally:
            sub.close()
    """

    bus: EventBus[T]
    queue: asyncio.Queue[T | None]
    _closed: bool = False

    def __aiter__(self) -> AsyncIterator[T]:
        """Iterate over events."""
        return self

    async def __anext__(self) -> T:
        """Get next event, blocking until available."""
        if self._closed:
            raise StopAsyncIteration

        event = await self.queue.get()
        if event is None:  # Sentinel from bus.close()
            self._closed = True
            raise StopAsyncIteration

        return event

    async def get(self, timeout: float | None = None) -> T | None:
        """
        Get next event with optional timeout.

        Returns None on timeout or if subscription is closed.
        """
        if self._closed:
            return None

        try:
            if timeout is not None:
                event = await asyncio.wait_for(self.queue.get(), timeout=timeout)
            else:
                event = await self.queue.get()

            if event is None:  # Sentinel
                self._closed = True
            return event
        except asyncio.TimeoutError:
            return None

    def close(self) -> None:
        """Close subscription and unsubscribe from bus."""
        if not self._closed:
            self._closed = True
            self.bus._unsubscribe(self.queue)

    @property
    def is_closed(self) -> bool:
        """Whether subscription is closed."""
        return self._closed

    @property
    def pending_count(self) -> int:
        """Number of events waiting in queue."""
        return self.queue.qsize()


# =============================================================================
# Typed Bus Factories
# =============================================================================


def create_town_event_bus(max_queue_size: int = 1000) -> EventBus[Any]:
    """Create EventBus for TownEvent (avoids circular import)."""
    return EventBus(max_queue_size=max_queue_size)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "EventBus",
    "EventBusStats",
    "Subscription",
    "create_town_event_bus",
]
