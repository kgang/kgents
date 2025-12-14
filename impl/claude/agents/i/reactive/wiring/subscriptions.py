"""
Subscriptions: Throttled reactive updates and event coordination.

The subscription system provides:
- Throttled signals for high-frequency events
- Event bus for cross-widget communication
- Deterministic state snapshots for replay
- Batched updates for performance

Key insight: Not every change needs immediate propagation.
Throttling + batching = smooth UI.
"""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass

T = TypeVar("T")
E = TypeVar("E")


class ThrottleMode(Enum):
    """How to throttle updates."""

    LEADING = auto()  # Emit immediately, then wait
    TRAILING = auto()  # Wait, then emit last value
    BOTH = auto()  # Emit immediately AND last value after wait


@dataclass
class ThrottledSignal(Generic[T]):
    """
    A Signal that throttles updates for high-frequency events.

    Prevents UI thrashing by batching rapid updates into controlled intervals.

    Example:
        # Original signal with many rapid updates
        raw_signal = Signal.of(0)

        # Throttled version: max 60 updates per second
        throttled = ThrottledSignal.from_signal(raw_signal, interval_ms=16.67)

        # Subscribe to throttled updates
        throttled.subscribe(lambda v: render(v))

        # Rapid updates only emit at throttled rate
        for i in range(100):
            raw_signal.set(i)  # Only ~6 updates reach subscribers (100ms / 16.67)
    """

    _source: Signal[T]
    _interval_ms: float
    _mode: ThrottleMode = ThrottleMode.TRAILING
    _last_emit: float = field(default=0.0)
    _pending: T | None = field(default=None)
    _has_pending: bool = field(default=False)
    _subscribers: list[Callable[[T], None]] = field(default_factory=list)
    _unsubscribe_source: Callable[[], None] | None = field(default=None)

    @classmethod
    def from_signal(
        cls,
        source: Signal[T],
        interval_ms: float = 16.67,  # ~60fps
        mode: ThrottleMode = ThrottleMode.TRAILING,
    ) -> ThrottledSignal[T]:
        """
        Create a throttled signal from a source signal.

        Args:
            source: The source Signal to throttle
            interval_ms: Minimum interval between emissions (default 16.67ms = 60fps)
            mode: Throttle mode (LEADING, TRAILING, or BOTH)

        Returns:
            ThrottledSignal that emits at most once per interval
        """
        throttled: ThrottledSignal[T] = cls(
            _source=source,
            _interval_ms=interval_ms,
            _mode=mode,
        )

        # Subscribe to source
        def on_source_change(value: T) -> None:
            throttled._handle_update(value)

        throttled._unsubscribe_source = source.subscribe(on_source_change)

        return throttled

    def _handle_update(self, value: T) -> None:
        """Handle an update from the source signal."""
        now = time.time() * 1000
        elapsed = now - self._last_emit

        if elapsed >= self._interval_ms:
            # Enough time has passed, emit now
            if self._mode in (ThrottleMode.LEADING, ThrottleMode.BOTH):
                self._emit(value)
                self._last_emit = now
                self._has_pending = False
            elif self._mode == ThrottleMode.TRAILING:
                self._emit(value)
                self._last_emit = now
                self._has_pending = False
        else:
            # Too soon, store as pending
            self._pending = value
            self._has_pending = True

    def flush(self) -> None:
        """Force emit any pending value."""
        if self._has_pending and self._pending is not None:
            self._emit(self._pending)
            self._last_emit = time.time() * 1000
            self._has_pending = False

    def _emit(self, value: T) -> None:
        """Emit value to all subscribers."""
        for sub in self._subscribers:
            sub(value)

    @property
    def value(self) -> T:
        """Get current value (from source, not pending)."""
        return self._source.value

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        """
        Subscribe to throttled updates.

        Args:
            callback: Function to call on throttled updates

        Returns:
            Unsubscribe function
        """
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)

    def dispose(self) -> None:
        """Clean up subscriptions."""
        if self._unsubscribe_source:
            self._unsubscribe_source()
            self._unsubscribe_source = None
        self._subscribers.clear()


@dataclass(frozen=True)
class StateSnapshot(Generic[T]):
    """
    Immutable snapshot of state at a point in time.

    Used for replay and debugging.
    """

    state: T
    timestamp_ms: float
    frame: int
    source_id: str


@dataclass
class Subscription(Generic[T]):
    """
    A subscription to a signal with lifecycle management.

    Tracks subscription metadata and provides controlled unsubscribe.
    """

    id: str
    source_id: str
    callback: Callable[[T], None]
    created_at: float = field(default_factory=lambda: time.time() * 1000)
    _active: bool = field(default=True)
    _unsubscribe: Callable[[], None] | None = field(default=None)

    @property
    def active(self) -> bool:
        """Whether subscription is active."""
        return self._active

    def unsubscribe(self) -> None:
        """Unsubscribe and mark as inactive."""
        if self._active and self._unsubscribe:
            self._unsubscribe()
            self._active = False

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Subscription):
            return self.id == other.id
        return False


class EventType(Enum):
    """Standard event types for cross-widget communication."""

    # Agent events
    AGENT_ADDED = "agent.added"
    AGENT_REMOVED = "agent.removed"
    AGENT_STATE_CHANGED = "agent.state_changed"
    AGENT_PHASE_CHANGED = "agent.phase_changed"

    # Yield events
    YIELD_CREATED = "yield.created"
    YIELD_CONSUMED = "yield.consumed"

    # Clock events
    CLOCK_TICK = "clock.tick"
    CLOCK_PAUSED = "clock.paused"
    CLOCK_RESUMED = "clock.resumed"

    # Dashboard events
    DASHBOARD_REFRESH = "dashboard.refresh"
    DASHBOARD_AGENT_SELECTED = "dashboard.agent_selected"

    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class Event(Generic[E]):
    """
    An event for cross-widget communication.

    Events are immutable and carry a payload of type E.
    """

    type: EventType | str
    payload: E
    source_id: str = ""
    timestamp_ms: float = field(default_factory=lambda: time.time() * 1000)

    def __hash__(self) -> int:
        return hash((self.type, self.timestamp_ms, self.source_id))


@dataclass
class EventBus:
    """
    Central event bus for cross-widget communication.

    Decouples widgets by allowing publish/subscribe pattern.

    Example:
        bus = create_event_bus()

        # Subscribe to agent events
        bus.subscribe(EventType.AGENT_ADDED, lambda e: print(f"Agent: {e.payload}"))

        # Publish event
        bus.publish(Event(EventType.AGENT_ADDED, {"id": "agent-1", "name": "Test"}))

    Features:
        - Type-safe events
        - Multiple subscribers per event type
        - Event history for replay
        - Throttled event emission
    """

    _subscribers: dict[EventType | str, list[Callable[[Event[Any]], None]]] = field(
        default_factory=lambda: defaultdict(list)
    )
    _history: list[Event[Any]] = field(default_factory=list)
    _history_max: int = 1000
    _throttled: dict[EventType | str, ThrottledSignal[Event[Any]]] = field(
        default_factory=dict
    )

    def subscribe(
        self,
        event_type: EventType | str,
        callback: Callable[[Event[Any]], None],
    ) -> Callable[[], None]:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published

        Returns:
            Unsubscribe function
        """
        self._subscribers[event_type].append(callback)
        return lambda: self._subscribers[event_type].remove(callback)

    def subscribe_all(
        self,
        callback: Callable[[Event[Any]], None],
    ) -> Callable[[], None]:
        """
        Subscribe to all events.

        Args:
            callback: Function to call for any event

        Returns:
            Unsubscribe function
        """
        # Use special key for "all" subscribers
        key = "__all__"
        self._subscribers[key].append(callback)
        return lambda: self._subscribers[key].remove(callback)

    def publish(self, event: Event[Any]) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        # Add to history
        self._history.append(event)
        if len(self._history) > self._history_max:
            self._history = self._history[-self._history_max :]

        # Notify type-specific subscribers
        for sub in self._subscribers.get(event.type, []):
            sub(event)

        # Notify "all" subscribers
        for sub in self._subscribers.get("__all__", []):
            sub(event)

    def publish_throttled(
        self,
        event: Event[Any],
        interval_ms: float = 16.67,
    ) -> None:
        """
        Publish an event with throttling.

        High-frequency events will be batched to the specified interval.

        Args:
            event: Event to publish
            interval_ms: Throttle interval in milliseconds
        """
        event_type = event.type

        # Get or create throttled signal for this event type
        if event_type not in self._throttled:
            source: Signal[Event[Any]] = Signal.of(event)
            throttled = ThrottledSignal.from_signal(source, interval_ms)

            # Wire throttled output to actual publish
            throttled.subscribe(lambda e: self._publish_direct(e))

            self._throttled[event_type] = throttled

        # Update the source signal (will be throttled)
        throttled_signal = self._throttled[event_type]
        throttled_signal._source.set(event)

    def _publish_direct(self, event: Event[Any]) -> None:
        """Publish without throttling (used by throttled signals)."""
        for sub in self._subscribers.get(event.type, []):
            sub(event)
        for sub in self._subscribers.get("__all__", []):
            sub(event)

    def flush_throttled(self) -> None:
        """Flush all pending throttled events."""
        for throttled in self._throttled.values():
            throttled.flush()

    def history(
        self,
        event_type: EventType | str | None = None,
        limit: int = 100,
    ) -> list[Event[Any]]:
        """
        Get event history.

        Args:
            event_type: Filter by type (None = all)
            limit: Maximum events to return

        Returns:
            List of events, newest first
        """
        if event_type is None:
            return list(reversed(self._history[-limit:]))

        filtered = [e for e in self._history if e.type == event_type]
        return list(reversed(filtered[-limit:]))

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()

    def subscriber_count(self, event_type: EventType | str | None = None) -> int:
        """Get count of subscribers."""
        if event_type is None:
            return sum(len(subs) for subs in self._subscribers.values())
        return len(self._subscribers.get(event_type, []))


def create_event_bus(history_max: int = 1000) -> EventBus:
    """
    Create an EventBus with configuration.

    Args:
        history_max: Maximum events to keep in history

    Returns:
        Configured EventBus
    """
    bus = EventBus()
    bus._history_max = history_max
    return bus


# Batched update helper
@dataclass
class BatchedUpdates(Generic[T]):
    """
    Batch multiple updates into a single emission.

    Useful for reducing render cycles when many state changes
    happen in quick succession.

    Example:
        batch = BatchedUpdates(interval_ms=16.67)

        # Queue many updates
        batch.queue("agent_1", AgentState(...))
        batch.queue("agent_2", AgentState(...))
        batch.queue("agent_1", AgentState(...))  # Overwrites first

        # Flush all at once
        changes = batch.flush()  # Returns {"agent_1": ..., "agent_2": ...}
    """

    interval_ms: float = 16.67
    _pending: dict[str, T] = field(default_factory=dict)
    _last_flush: float = field(default_factory=lambda: time.time() * 1000)
    _on_flush: Callable[[dict[str, T]], None] | None = field(default=None)

    def queue(self, key: str, value: T) -> None:
        """Queue an update (overwrites previous for same key)."""
        self._pending[key] = value

        # Auto-flush if enough time has passed
        now = time.time() * 1000
        if now - self._last_flush >= self.interval_ms:
            self.flush()

    def flush(self) -> dict[str, T]:
        """
        Flush all pending updates.

        Returns:
            Dict of key -> value for all pending updates
        """
        if not self._pending:
            return {}

        result = dict(self._pending)
        self._pending.clear()
        self._last_flush = time.time() * 1000

        if self._on_flush:
            self._on_flush(result)

        return result

    def on_flush(self, callback: Callable[[dict[str, T]], None]) -> None:
        """Set callback for flush events."""
        self._on_flush = callback

    @property
    def pending_count(self) -> int:
        """Count of pending updates."""
        return len(self._pending)
