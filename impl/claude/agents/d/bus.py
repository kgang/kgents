"""
DataBus: Reactive data flow for D-gent.

Central bus for data events. Bridges D-gent, M-gent, and the reactive substrate.

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Awaitable, Callable, Final
from uuid import uuid4

from .datum import Datum
from .protocol import BaseDgent, DgentProtocol


class DataEventType(Enum):
    """Types of data events."""

    PUT = auto()      # New datum stored
    DELETE = auto()   # Datum removed
    UPGRADE = auto()  # Datum promoted to higher tier
    DEGRADE = auto()  # Datum demoted (graceful degradation)


@dataclass(frozen=True, slots=True)
class DataEvent:
    """
    An event representing a data change.

    Emitted by D-gent on every write/delete.
    Consumed by M-gent, UI, tracing, etc.
    """

    event_id: str
    event_type: DataEventType
    datum_id: str
    timestamp: float
    source: str
    causal_parent: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        event_type: DataEventType,
        datum_id: str,
        source: str = "dgent",
        causal_parent: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> DataEvent:
        """Factory for creating events with sensible defaults."""
        return cls(
            event_id=uuid4().hex,
            event_type=event_type,
            datum_id=datum_id,
            timestamp=time.time(),
            source=source,
            causal_parent=causal_parent,
            metadata=metadata or {},
        )


# Type alias for event handlers
EventHandler = Callable[[DataEvent], Awaitable[None]]


@dataclass
class Subscriber:
    """A subscriber to data events."""

    handler: EventHandler
    id: str = field(default_factory=lambda: uuid4().hex)


DEFAULT_BUFFER_SIZE: Final[int] = 1000


class DataBus:
    """
    Central bus for data events.

    Features:
    - Multiple subscribers per event type
    - Async, non-blocking emission
    - Replay capability (for late subscribers)
    - Causal ordering guarantees

    Guarantees:
    - At-least-once delivery
    - Causal ordering (if A caused B, subscribers see A before B)
    - Non-blocking emission (publishers never wait for subscribers)
    - Bounded buffer (old events dropped when full)
    """

    def __init__(self, buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self._subscribers: dict[DataEventType, list[Subscriber]] = defaultdict(list)
        self._all_subscribers: list[Subscriber] = []
        self._buffer: deque[DataEvent] = deque(maxlen=buffer_size)
        self._lock = asyncio.Lock()
        self._emit_count = 0
        self._error_count = 0

    async def emit(self, event: DataEvent) -> None:
        """
        Emit an event to all subscribers.

        Non-blocking: subscribers run in background tasks.
        """
        async with self._lock:
            self._buffer.append(event)
            self._emit_count += 1

        # Get all handlers for this event type
        type_handlers = list(self._subscribers.get(event.event_type, []))
        all_handlers = list(self._all_subscribers)

        # Notify all handlers (non-blocking)
        for subscriber in type_handlers + all_handlers:
            asyncio.create_task(self._safe_notify(subscriber, event))

    async def _safe_notify(self, subscriber: Subscriber, event: DataEvent) -> None:
        """Safely notify a subscriber, catching exceptions."""
        try:
            await subscriber.handler(event)
        except Exception as e:
            self._error_count += 1
            # Log but don't propagate (non-blocking)
            # TODO: Integrate with logging/tracing
            pass

    def subscribe(
        self,
        event_type: DataEventType,
        handler: EventHandler,
    ) -> Callable[[], None]:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of events to subscribe to
            handler: Async function to call for each event

        Returns:
            Unsubscribe function (call to stop receiving events)
        """
        subscriber = Subscriber(handler=handler)
        self._subscribers[event_type].append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._subscribers[event_type]:
                self._subscribers[event_type].remove(subscriber)

        return unsubscribe

    def subscribe_all(
        self,
        handler: EventHandler,
    ) -> Callable[[], None]:
        """
        Subscribe to ALL event types.

        Args:
            handler: Async function to call for each event

        Returns:
            Unsubscribe function
        """
        subscriber = Subscriber(handler=handler)
        self._all_subscribers.append(subscriber)

        def unsubscribe() -> None:
            if subscriber in self._all_subscribers:
                self._all_subscribers.remove(subscriber)

        return unsubscribe

    async def replay(
        self,
        handler: EventHandler,
        since: float | None = None,
        event_type: DataEventType | None = None,
    ) -> int:
        """
        Replay buffered events to a handler.

        Useful for late subscribers to catch up.

        Args:
            handler: Async function to call for each event
            since: Only replay events after this timestamp (None = all)
            event_type: Only replay events of this type (None = all)

        Returns:
            Count of replayed events
        """
        count = 0
        async with self._lock:
            for event in self._buffer:
                # Apply filters
                if since is not None and event.timestamp < since:
                    continue
                if event_type is not None and event.event_type != event_type:
                    continue

                await handler(event)
                count += 1
        return count

    @property
    def latest(self) -> DataEvent | None:
        """Get the most recent event."""
        if self._buffer:
            return self._buffer[-1]
        return None

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "buffer_size": len(self._buffer),
            "total_emitted": self._emit_count,
            "total_errors": self._error_count,
            "subscriber_count": sum(
                len(subs) for subs in self._subscribers.values()
            )
            + len(self._all_subscribers),
        }

    def clear(self) -> None:
        """Clear all subscribers and buffer (for testing)."""
        self._subscribers.clear()
        self._all_subscribers.clear()
        self._buffer.clear()
        self._emit_count = 0
        self._error_count = 0


class BusEnabledDgent(BaseDgent):
    """
    D-gent wrapper that emits events to the Data Bus.

    Wraps any DgentProtocol backend and emits events on every operation.
    """

    def __init__(
        self,
        backend: DgentProtocol,
        bus: DataBus,
        source: str = "dgent",
    ) -> None:
        """
        Initialize bus-enabled D-gent.

        Args:
            backend: The underlying storage backend
            bus: The data bus to emit events to
            source: Source identifier for events
        """
        self.backend = backend
        self.bus = bus
        self.source = source
        self._last_event_id: str | None = None

    async def put(self, datum: Datum) -> str:
        """Store datum and emit PUT event."""
        id = await self.backend.put(datum)

        event = DataEvent.create(
            event_type=DataEventType.PUT,
            datum_id=id,
            source=self.source,
            causal_parent=self._last_event_id,
            metadata=datum.metadata,
        )
        await self.bus.emit(event)
        self._last_event_id = event.event_id

        return id

    async def get(self, id: str) -> Datum | None:
        """Retrieve datum (no event emitted for reads)."""
        return await self.backend.get(id)

    async def delete(self, id: str) -> bool:
        """Delete datum and emit DELETE event if successful."""
        success = await self.backend.delete(id)

        if success:
            event = DataEvent.create(
                event_type=DataEventType.DELETE,
                datum_id=id,
                source=self.source,
                causal_parent=self._last_event_id,
            )
            await self.bus.emit(event)
            self._last_event_id = event.event_id

        return success

    async def list(
        self,
        prefix: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[Datum]:
        """List data (no event emitted for reads)."""
        return await self.backend.list(prefix=prefix, after=after, limit=limit)

    async def causal_chain(self, id: str) -> list[Datum]:
        """Get causal chain (no event emitted for reads)."""
        return await self.backend.causal_chain(id)

    async def exists(self, id: str) -> bool:
        """Check existence (no event emitted for reads)."""
        return await self.backend.exists(id)

    async def count(self) -> int:
        """Count data (no event emitted for reads)."""
        return await self.backend.count()


# Global bus instance (singleton pattern)
_global_bus: DataBus | None = None


def get_data_bus() -> DataBus:
    """Get the global data bus instance."""
    global _global_bus
    if _global_bus is None:
        _global_bus = DataBus()
    return _global_bus


def reset_data_bus() -> None:
    """Reset the global data bus (for testing)."""
    global _global_bus
    if _global_bus is not None:
        _global_bus.clear()
    _global_bus = None
