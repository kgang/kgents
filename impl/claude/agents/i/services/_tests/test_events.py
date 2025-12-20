"""
Tests for the EventBus system.

Verifies:
- Singleton behavior
- Subscribe/unsubscribe mechanics
- Duplicate subscription prevention
- Error isolation
- Event type isolation
"""

from datetime import datetime

import pytest

from ..events import (
    AgentFocusedEvent,
    Event,
    EventBus,
    LODChangedEvent,
    MetricsUpdatedEvent,
    ScreenNavigationEvent,
)

# ===== Fixtures =====


@pytest.fixture(autouse=True)
def reset_event_bus():
    """Reset EventBus singleton before each test."""
    EventBus.reset()
    yield
    EventBus.reset()


# ===== Base Event Tests =====


def test_event_has_timestamp():
    """Base Event should have an automatic timestamp."""
    event = Event()
    assert isinstance(event.timestamp, datetime)


def test_event_timestamp_can_be_set():
    """Event timestamp can be explicitly set."""
    custom_time = datetime(2025, 1, 1, 12, 0, 0)
    event = Event(timestamp=custom_time)
    assert event.timestamp == custom_time


# ===== Event Type Tests =====


def test_screen_navigation_event():
    """ScreenNavigationEvent contains navigation metadata."""
    event = ScreenNavigationEvent(
        target_screen="cockpit", source_screen="observatory", focus_element="agent_list"
    )
    assert event.target_screen == "cockpit"
    assert event.source_screen == "observatory"
    assert event.focus_element == "agent_list"
    assert isinstance(event.timestamp, datetime)


def test_agent_focused_event():
    """AgentFocusedEvent contains agent ID."""
    event = AgentFocusedEvent(agent_id="kgent-001")
    assert event.agent_id == "kgent-001"
    assert isinstance(event.timestamp, datetime)


def test_metrics_updated_event():
    """MetricsUpdatedEvent contains metrics dictionary."""
    metrics = {"active_agents": 5, "memory_usage": 0.75}
    event = MetricsUpdatedEvent(metrics=metrics)
    assert event.metrics == metrics
    assert isinstance(event.timestamp, datetime)


def test_lod_changed_event():
    """LODChangedEvent contains old and new LOD levels."""
    event = LODChangedEvent(old_lod=1, new_lod=2)
    assert event.old_lod == 1
    assert event.new_lod == 2
    assert isinstance(event.timestamp, datetime)


# ===== EventBus Singleton Tests =====


def test_eventbus_is_singleton():
    """EventBus.get() returns the same instance."""
    bus1 = EventBus.get()
    bus2 = EventBus.get()
    assert bus1 is bus2


def test_eventbus_reset_creates_new_instance():
    """EventBus.reset() creates a fresh instance."""
    bus1 = EventBus.get()
    EventBus.reset()
    bus2 = EventBus.get()
    assert bus1 is not bus2


# ===== Subscribe and Emit Tests =====


def test_subscribe_and_emit():
    """Handler receives emitted events."""
    bus = EventBus.get()
    received_events = []

    def handler(event: AgentFocusedEvent) -> None:
        received_events.append(event)

    bus.subscribe(AgentFocusedEvent, handler)
    event = AgentFocusedEvent(agent_id="test-agent")
    bus.emit(event)

    assert len(received_events) == 1
    assert received_events[0] is event


def test_multiple_handlers_receive_event():
    """All subscribed handlers receive the event."""
    bus = EventBus.get()
    handler1_calls = []
    handler2_calls = []

    def handler1(event: MetricsUpdatedEvent) -> None:
        handler1_calls.append(event)

    def handler2(event: MetricsUpdatedEvent) -> None:
        handler2_calls.append(event)

    bus.subscribe(MetricsUpdatedEvent, handler1)
    bus.subscribe(MetricsUpdatedEvent, handler2)

    event = MetricsUpdatedEvent(metrics={"test": 123})
    bus.emit(event)

    assert len(handler1_calls) == 1
    assert len(handler2_calls) == 1
    assert handler1_calls[0] is event
    assert handler2_calls[0] is event


def test_handlers_called_in_subscription_order():
    """Handlers are called in the order they were subscribed."""
    bus = EventBus.get()
    call_order = []

    def handler1(event: LODChangedEvent) -> None:
        call_order.append(1)

    def handler2(event: LODChangedEvent) -> None:
        call_order.append(2)

    def handler3(event: LODChangedEvent) -> None:
        call_order.append(3)

    bus.subscribe(LODChangedEvent, handler1)
    bus.subscribe(LODChangedEvent, handler2)
    bus.subscribe(LODChangedEvent, handler3)

    bus.emit(LODChangedEvent(old_lod=1, new_lod=2))

    assert call_order == [1, 2, 3]


# ===== Duplicate Subscription Prevention =====


def test_duplicate_subscription_prevented():
    """Subscribing the same handler twice has no effect."""
    bus = EventBus.get()
    call_count = [0]

    def handler(event: ScreenNavigationEvent) -> None:
        call_count[0] += 1

    bus.subscribe(ScreenNavigationEvent, handler)
    bus.subscribe(ScreenNavigationEvent, handler)  # Duplicate

    bus.emit(ScreenNavigationEvent(target_screen="test"))

    # Handler should only be called once despite duplicate subscription
    assert call_count[0] == 1


def test_subscriber_count_reflects_deduplication():
    """get_subscriber_count reflects deduplicated handlers."""
    bus = EventBus.get()

    def handler(event: AgentFocusedEvent) -> None:
        pass

    assert bus.get_subscriber_count(AgentFocusedEvent) == 0

    bus.subscribe(AgentFocusedEvent, handler)
    assert bus.get_subscriber_count(AgentFocusedEvent) == 1

    bus.subscribe(AgentFocusedEvent, handler)  # Duplicate
    assert bus.get_subscriber_count(AgentFocusedEvent) == 1


# ===== Error Isolation Tests =====


def test_handler_exception_does_not_prevent_other_handlers():
    """One handler's exception doesn't prevent others from running."""
    bus = EventBus.get()
    handler1_called = [False]
    handler3_called = [False]

    def handler1(event: MetricsUpdatedEvent) -> None:
        handler1_called[0] = True

    def handler2_that_fails(event: MetricsUpdatedEvent) -> None:
        raise ValueError("Intentional test error")

    def handler3(event: MetricsUpdatedEvent) -> None:
        handler3_called[0] = True

    bus.subscribe(MetricsUpdatedEvent, handler1)
    bus.subscribe(MetricsUpdatedEvent, handler2_that_fails)
    bus.subscribe(MetricsUpdatedEvent, handler3)

    # This should not raise, despite handler2 raising
    bus.emit(MetricsUpdatedEvent(metrics={"test": 1}))

    assert handler1_called[0], "Handler 1 should have been called"
    assert handler3_called[0], "Handler 3 should have been called despite handler 2's error"


def test_error_isolation_with_multiple_failures():
    """Multiple handler failures don't cascade."""
    bus = EventBus.get()
    successful_calls = []

    def handler1_fails(event: LODChangedEvent) -> None:
        raise RuntimeError("Error 1")

    def handler2_succeeds(event: LODChangedEvent) -> None:
        successful_calls.append(2)

    def handler3_fails(event: LODChangedEvent) -> None:
        raise RuntimeError("Error 3")

    def handler4_succeeds(event: LODChangedEvent) -> None:
        successful_calls.append(4)

    bus.subscribe(LODChangedEvent, handler1_fails)
    bus.subscribe(LODChangedEvent, handler2_succeeds)
    bus.subscribe(LODChangedEvent, handler3_fails)
    bus.subscribe(LODChangedEvent, handler4_succeeds)

    bus.emit(LODChangedEvent(old_lod=1, new_lod=2))

    assert successful_calls == [2, 4]


# ===== Event Type Isolation Tests =====


def test_handlers_only_receive_subscribed_event_type():
    """Handlers only receive events of their subscribed type."""
    bus = EventBus.get()
    nav_events = []
    focus_events = []

    def nav_handler(event: ScreenNavigationEvent) -> None:
        nav_events.append(event)

    def focus_handler(event: AgentFocusedEvent) -> None:
        focus_events.append(event)

    bus.subscribe(ScreenNavigationEvent, nav_handler)
    bus.subscribe(AgentFocusedEvent, focus_handler)

    # Emit different event types
    bus.emit(ScreenNavigationEvent(target_screen="test"))
    bus.emit(AgentFocusedEvent(agent_id="test"))
    bus.emit(ScreenNavigationEvent(target_screen="test2"))

    assert len(nav_events) == 2
    assert len(focus_events) == 1


def test_no_handlers_for_unsubscribed_event_type():
    """Emitting an event with no subscribers is a no-op."""
    bus = EventBus.get()

    # This should not raise
    bus.emit(MetricsUpdatedEvent(metrics={"orphan": True}))

    assert bus.get_subscriber_count(MetricsUpdatedEvent) == 0


# ===== Unsubscribe Tests =====


def test_unsubscribe_removes_handler():
    """Unsubscribing prevents handler from receiving future events."""
    bus = EventBus.get()
    call_count = [0]

    def handler(event: AgentFocusedEvent) -> None:
        call_count[0] += 1

    bus.subscribe(AgentFocusedEvent, handler)
    bus.emit(AgentFocusedEvent(agent_id="test1"))
    assert call_count[0] == 1

    bus.unsubscribe(AgentFocusedEvent, handler)
    bus.emit(AgentFocusedEvent(agent_id="test2"))
    assert call_count[0] == 1  # No change


def test_unsubscribe_only_affects_specified_handler():
    """Unsubscribing one handler doesn't affect others."""
    bus = EventBus.get()
    handler1_calls = []
    handler2_calls = []

    def handler1(event: LODChangedEvent) -> None:
        handler1_calls.append(event)

    def handler2(event: LODChangedEvent) -> None:
        handler2_calls.append(event)

    bus.subscribe(LODChangedEvent, handler1)
    bus.subscribe(LODChangedEvent, handler2)

    bus.unsubscribe(LODChangedEvent, handler1)

    bus.emit(LODChangedEvent(old_lod=1, new_lod=2))

    assert len(handler1_calls) == 0
    assert len(handler2_calls) == 1


def test_unsubscribe_nonexistent_handler_is_noop():
    """Unsubscribing a handler that isn't subscribed is safe."""
    bus = EventBus.get()

    def handler(event: MetricsUpdatedEvent) -> None:
        pass

    # This should not raise
    bus.unsubscribe(MetricsUpdatedEvent, handler)


def test_unsubscribe_from_wrong_event_type_is_noop():
    """Unsubscribing from wrong event type is safe."""
    bus = EventBus.get()
    calls = []

    def handler(event: AgentFocusedEvent) -> None:
        calls.append(event)

    bus.subscribe(AgentFocusedEvent, handler)

    # Unsubscribe from wrong type
    bus.unsubscribe(MetricsUpdatedEvent, handler)  # type: ignore

    # Handler should still work
    bus.emit(AgentFocusedEvent(agent_id="test"))
    assert len(calls) == 1


# ===== Clear All Tests =====


def test_clear_all_removes_all_subscribers():
    """clear_all() removes all handlers from all event types."""
    bus = EventBus.get()
    calls = []

    def handler1(event: AgentFocusedEvent) -> None:
        calls.append(1)

    def handler2(event: MetricsUpdatedEvent) -> None:
        calls.append(2)

    bus.subscribe(AgentFocusedEvent, handler1)
    bus.subscribe(MetricsUpdatedEvent, handler2)

    bus.clear_all()

    bus.emit(AgentFocusedEvent(agent_id="test"))
    bus.emit(MetricsUpdatedEvent(metrics={"test": 1}))

    assert len(calls) == 0
    assert bus.get_subscriber_count(AgentFocusedEvent) == 0
    assert bus.get_subscriber_count(MetricsUpdatedEvent) == 0
