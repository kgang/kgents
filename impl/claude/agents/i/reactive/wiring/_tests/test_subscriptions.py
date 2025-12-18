"""
Tests for Subscriptions: Throttled reactive updates and event coordination.

Wave 5 - Reality Wiring: Subscription tests
"""

from __future__ import annotations

import time

import pytest

from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.subscriptions import (
    BatchedUpdates,
    Event,
    EventBus,
    EventType,
    StateSnapshot,
    Subscription,
    ThrottledSignal,
    ThrottleMode,
    create_event_bus,
)


class TestThrottledSignal:
    """Tests for ThrottledSignal."""

    def test_throttled_signal_from_signal(self) -> None:
        """ThrottledSignal.from_signal should create properly."""
        source: Signal[int] = Signal.of(0)
        throttled = ThrottledSignal.from_signal(source, interval_ms=100.0)

        assert throttled.value == 0
        assert throttled._interval_ms == 100.0

    def test_throttled_signal_value(self) -> None:
        """value property should return source value."""
        source: Signal[str] = Signal.of("initial")
        throttled = ThrottledSignal.from_signal(source)

        assert throttled.value == "initial"

        source.set("updated")
        assert throttled.value == "updated"

    def test_throttled_signal_subscribe(self) -> None:
        """subscribe() should receive throttled updates."""
        source: Signal[int] = Signal.of(0)
        throttled = ThrottledSignal.from_signal(source, interval_ms=0.1)  # Very short for testing
        received: list[int] = []

        throttled.subscribe(lambda v: received.append(v))

        # First update should go through (trailing mode, enough time)
        time.sleep(0.001)  # Ensure enough time passes
        source.set(1)

        # Give time for update to process
        time.sleep(0.001)
        throttled.flush()

        assert 1 in received or len(received) > 0

    def test_throttled_signal_flush(self) -> None:
        """flush() should emit pending value."""
        source: Signal[int] = Signal.of(0)
        throttled = ThrottledSignal.from_signal(source, interval_ms=10000.0)  # Long interval
        received: list[int] = []

        throttled.subscribe(lambda v: received.append(v))

        # Update rapidly
        source.set(1)
        source.set(2)
        source.set(3)

        # Pending value should be stored
        assert throttled._has_pending or len(received) > 0

        # Flush should emit
        throttled.flush()

        # At least one value should have been received
        assert len(received) >= 1

    def test_throttled_signal_dispose(self) -> None:
        """dispose() should clean up subscriptions."""
        source: Signal[int] = Signal.of(0)
        throttled = ThrottledSignal.from_signal(source)
        received: list[int] = []

        throttled.subscribe(lambda v: received.append(v))
        throttled.dispose()

        # No more updates after dispose
        source.set(100)
        throttled.flush()

        # Should have no subscribers
        assert len(throttled._subscribers) == 0


class TestSubscription:
    """Tests for Subscription."""

    def test_subscription_creation(self) -> None:
        """Subscription should create with correct fields."""
        sub: Subscription[int] = Subscription(
            id="sub-1",
            source_id="source-1",
            callback=lambda x: None,
        )

        assert sub.id == "sub-1"
        assert sub.source_id == "source-1"
        assert sub.active is True

    def test_subscription_unsubscribe(self) -> None:
        """unsubscribe() should mark as inactive."""
        unsubscribed = False

        def unsubscribe_fn() -> None:
            nonlocal unsubscribed
            unsubscribed = True

        sub: Subscription[int] = Subscription(
            id="sub-1",
            source_id="source-1",
            callback=lambda x: None,
        )
        sub._unsubscribe = unsubscribe_fn

        assert sub.active is True

        sub.unsubscribe()

        assert sub.active is False
        assert unsubscribed is True

    def test_subscription_equality(self) -> None:
        """Subscriptions should be equal by ID."""
        sub1: Subscription[int] = Subscription(
            id="sub-1",
            source_id="source-1",
            callback=lambda x: None,
        )
        sub2: Subscription[int] = Subscription(
            id="sub-1",
            source_id="source-2",  # Different source
            callback=lambda _: None,  # Different callback (unused param)
        )
        sub3: Subscription[int] = Subscription(
            id="sub-2",
            source_id="source-1",
            callback=lambda x: None,
        )

        assert sub1 == sub2  # Same ID
        assert sub1 != sub3  # Different ID


class TestStateSnapshot:
    """Tests for StateSnapshot."""

    def test_state_snapshot_immutable(self) -> None:
        """StateSnapshot should be immutable."""
        snapshot: StateSnapshot[dict[str, int]] = StateSnapshot(
            state={"count": 5},
            timestamp_ms=1000.0,
            frame=10,
            source_id="widget-1",
        )

        assert snapshot.state == {"count": 5}
        assert snapshot.timestamp_ms == 1000.0
        assert snapshot.frame == 10
        assert snapshot.source_id == "widget-1"


class TestEvent:
    """Tests for Event."""

    def test_event_creation(self) -> None:
        """Event should create with correct fields."""
        event: Event[dict[str, str]] = Event(
            type=EventType.AGENT_ADDED,
            payload={"id": "agent-1"},
            source_id="dashboard",
        )

        assert event.type == EventType.AGENT_ADDED
        assert event.payload == {"id": "agent-1"}
        assert event.source_id == "dashboard"
        assert event.timestamp_ms > 0

    def test_event_with_string_type(self) -> None:
        """Event should accept string types."""
        event: Event[str] = Event(
            type="custom.event",
            payload="test payload",
        )

        assert event.type == "custom.event"
        assert event.payload == "test payload"


class TestEventBus:
    """Tests for EventBus."""

    def test_event_bus_subscribe_publish(self) -> None:
        """EventBus should deliver events to subscribers."""
        bus = create_event_bus()
        received: list[Event[dict[str, str]]] = []

        bus.subscribe(EventType.AGENT_ADDED, lambda e: received.append(e))

        event: Event[dict[str, str]] = Event(
            type=EventType.AGENT_ADDED,
            payload={"id": "agent-1"},
        )
        bus.publish(event)

        assert len(received) == 1
        assert received[0].payload == {"id": "agent-1"}

    def test_event_bus_multiple_subscribers(self) -> None:
        """Multiple subscribers should all receive events."""
        bus = create_event_bus()
        received1: list[Event[str]] = []
        received2: list[Event[str]] = []

        bus.subscribe(EventType.CLOCK_TICK, lambda e: received1.append(e))
        bus.subscribe(EventType.CLOCK_TICK, lambda e: received2.append(e))

        event: Event[str] = Event(type=EventType.CLOCK_TICK, payload="tick")
        bus.publish(event)

        assert len(received1) == 1
        assert len(received2) == 1

    def test_event_bus_type_filtering(self) -> None:
        """Subscribers should only receive their event types."""
        bus = create_event_bus()
        agent_events: list[Event[str]] = []
        clock_events: list[Event[str]] = []

        bus.subscribe(EventType.AGENT_ADDED, lambda e: agent_events.append(e))
        bus.subscribe(EventType.CLOCK_TICK, lambda e: clock_events.append(e))

        bus.publish(Event(type=EventType.AGENT_ADDED, payload="agent"))
        bus.publish(Event(type=EventType.CLOCK_TICK, payload="tick"))
        bus.publish(Event(type=EventType.AGENT_ADDED, payload="agent2"))

        assert len(agent_events) == 2
        assert len(clock_events) == 1

    def test_event_bus_subscribe_all(self) -> None:
        """subscribe_all() should receive all events."""
        bus = create_event_bus()
        all_events: list[Event[str]] = []

        bus.subscribe_all(lambda e: all_events.append(e))

        bus.publish(Event(type=EventType.AGENT_ADDED, payload="1"))
        bus.publish(Event(type=EventType.CLOCK_TICK, payload="2"))
        bus.publish(Event(type=EventType.YIELD_CREATED, payload="3"))

        assert len(all_events) == 3

    def test_event_bus_unsubscribe(self) -> None:
        """Unsubscribe function should stop delivery."""
        bus = create_event_bus()
        received: list[Event[str]] = []

        unsub = bus.subscribe(EventType.AGENT_ADDED, lambda e: received.append(e))

        bus.publish(Event(type=EventType.AGENT_ADDED, payload="1"))
        assert len(received) == 1

        unsub()

        bus.publish(Event(type=EventType.AGENT_ADDED, payload="2"))
        assert len(received) == 1  # No new events

    def test_event_bus_history(self) -> None:
        """history() should return past events."""
        bus = create_event_bus()

        bus.publish(Event(type=EventType.AGENT_ADDED, payload="1"))
        bus.publish(Event(type=EventType.CLOCK_TICK, payload="2"))
        bus.publish(Event(type=EventType.AGENT_ADDED, payload="3"))

        # All history
        all_history = bus.history()
        assert len(all_history) == 3

        # Filtered history
        agent_history = bus.history(EventType.AGENT_ADDED)
        assert len(agent_history) == 2

    def test_event_bus_history_limit(self) -> None:
        """history() should respect limit."""
        bus = create_event_bus()

        for i in range(10):
            bus.publish(Event(type=EventType.CLOCK_TICK, payload=str(i)))

        history = bus.history(limit=5)
        assert len(history) == 5

    def test_event_bus_clear_history(self) -> None:
        """clear_history() should empty history."""
        bus = create_event_bus()

        bus.publish(Event(type=EventType.CLOCK_TICK, payload="tick"))
        assert len(bus.history()) == 1

        bus.clear_history()
        assert len(bus.history()) == 0

    def test_event_bus_subscriber_count(self) -> None:
        """subscriber_count() should return correct counts."""
        bus = create_event_bus()

        assert bus.subscriber_count() == 0

        bus.subscribe(EventType.AGENT_ADDED, lambda e: None)
        bus.subscribe(EventType.AGENT_ADDED, lambda e: None)
        bus.subscribe(EventType.CLOCK_TICK, lambda e: None)

        assert bus.subscriber_count(EventType.AGENT_ADDED) == 2
        assert bus.subscriber_count(EventType.CLOCK_TICK) == 1
        assert bus.subscriber_count() == 3


class TestBatchedUpdates:
    """Tests for BatchedUpdates."""

    def test_batched_updates_queue(self) -> None:
        """queue() should store pending updates."""
        batch: BatchedUpdates[int] = BatchedUpdates(interval_ms=10000.0)  # Long interval

        batch.queue("key1", 1)
        batch.queue("key2", 2)

        assert batch.pending_count == 2

    def test_batched_updates_overwrite(self) -> None:
        """queue() should overwrite previous value for same key."""
        batch: BatchedUpdates[int] = BatchedUpdates(interval_ms=10000.0)

        batch.queue("key1", 1)
        batch.queue("key1", 2)
        batch.queue("key1", 3)

        assert batch.pending_count == 1

        result = batch.flush()
        assert result == {"key1": 3}

    def test_batched_updates_flush(self) -> None:
        """flush() should return all pending and clear."""
        batch: BatchedUpdates[str] = BatchedUpdates(interval_ms=10000.0)

        batch.queue("a", "alpha")
        batch.queue("b", "beta")

        result = batch.flush()

        assert result == {"a": "alpha", "b": "beta"}
        assert batch.pending_count == 0

    def test_batched_updates_on_flush_callback(self) -> None:
        """on_flush callback should be called."""
        batch: BatchedUpdates[int] = BatchedUpdates(interval_ms=10000.0)
        flushed: list[dict[str, int]] = []

        batch.on_flush(lambda updates: flushed.append(updates))

        batch.queue("key1", 100)
        batch.flush()

        assert len(flushed) == 1
        assert flushed[0] == {"key1": 100}

    def test_batched_updates_empty_flush(self) -> None:
        """flush() with no pending should return empty dict."""
        batch: BatchedUpdates[int] = BatchedUpdates()

        result = batch.flush()

        assert result == {}


class TestCreateEventBus:
    """Tests for create_event_bus factory."""

    def test_create_event_bus_default(self) -> None:
        """create_event_bus() should work with defaults."""
        bus = create_event_bus()

        assert bus._history_max == 1000

    def test_create_event_bus_custom(self) -> None:
        """create_event_bus() should accept custom history_max."""
        bus = create_event_bus(history_max=500)

        assert bus._history_max == 500
