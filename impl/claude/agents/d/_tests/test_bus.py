"""
Tests for DataBus (reactive data flow).

Tests verify:
1. Event emission and subscription
2. Replay capability
3. BusEnabledDgent integration
4. Non-blocking behavior
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from ..backends.memory import MemoryBackend
from ..bus import (
    BusEnabledDgent,
    DataBus,
    DataEvent,
    DataEventType,
    get_data_bus,
    reset_data_bus,
)
from ..datum import Datum


@pytest.fixture
def bus() -> DataBus:
    """Fresh bus for each test."""
    return DataBus()


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Fresh memory backend for each test."""
    return MemoryBackend()


@pytest.fixture(autouse=True)
def cleanup_global_bus() -> None:
    """Reset global bus after each test."""
    yield
    reset_data_bus()


class TestDataEvent:
    """Tests for DataEvent dataclass."""

    def test_create_event(self) -> None:
        """create() generates event with defaults."""
        event = DataEvent.create(
            event_type=DataEventType.PUT,
            datum_id="test-123",
        )

        assert event.event_type == DataEventType.PUT
        assert event.datum_id == "test-123"
        assert len(event.event_id) == 32  # UUID hex
        assert event.source == "dgent"
        assert event.timestamp > 0

    def test_create_with_causal_parent(self) -> None:
        """create() accepts causal_parent."""
        event = DataEvent.create(
            event_type=DataEventType.PUT,
            datum_id="child",
            causal_parent="parent-event-id",
        )

        assert event.causal_parent == "parent-event-id"

    def test_create_with_metadata(self) -> None:
        """create() accepts metadata."""
        event = DataEvent.create(
            event_type=DataEventType.PUT,
            datum_id="test",
            metadata={"key": "value"},
        )

        assert event.metadata == {"key": "value"}


class TestSubscription:
    """Tests for subscribe() and emit()."""

    @pytest.mark.asyncio
    async def test_subscribe_receives_events(self, bus: DataBus) -> None:
        """Subscribers receive emitted events."""
        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe(DataEventType.PUT, handler)

        event = DataEvent.create(DataEventType.PUT, "test-id")
        await bus.emit(event)

        # Give handler time to run
        await asyncio.sleep(0.01)

        assert len(received) == 1
        assert received[0].datum_id == "test-id"

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_events(self, bus: DataBus) -> None:
        """Unsubscribing stops event delivery."""
        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        unsub = bus.subscribe(DataEventType.PUT, handler)

        # First event should be received
        await bus.emit(DataEvent.create(DataEventType.PUT, "first"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

        # Unsubscribe
        unsub()

        # Second event should not be received
        await bus.emit(DataEvent.create(DataEventType.PUT, "second"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_subscribe_filters_by_type(self, bus: DataBus) -> None:
        """Subscribers only receive events of subscribed type."""
        put_events: list[DataEvent] = []
        delete_events: list[DataEvent] = []

        async def put_handler(event: DataEvent) -> None:
            put_events.append(event)

        async def delete_handler(event: DataEvent) -> None:
            delete_events.append(event)

        bus.subscribe(DataEventType.PUT, put_handler)
        bus.subscribe(DataEventType.DELETE, delete_handler)

        await bus.emit(DataEvent.create(DataEventType.PUT, "put-1"))
        await bus.emit(DataEvent.create(DataEventType.DELETE, "del-1"))
        await bus.emit(DataEvent.create(DataEventType.PUT, "put-2"))
        await asyncio.sleep(0.01)

        assert len(put_events) == 2
        assert len(delete_events) == 1

    @pytest.mark.asyncio
    async def test_subscribe_all_receives_all_types(self, bus: DataBus) -> None:
        """subscribe_all() receives all event types."""
        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe_all(handler)

        await bus.emit(DataEvent.create(DataEventType.PUT, "put"))
        await bus.emit(DataEvent.create(DataEventType.DELETE, "del"))
        await bus.emit(DataEvent.create(DataEventType.UPGRADE, "up"))
        await asyncio.sleep(0.01)

        assert len(received) == 3

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, bus: DataBus) -> None:
        """Multiple subscribers all receive events."""
        results: list[list[str]] = [[], [], []]

        for i in range(3):
            idx = i

            async def handler(event: DataEvent, idx: int = idx) -> None:
                results[idx].append(event.datum_id)

            bus.subscribe(DataEventType.PUT, handler)

        await bus.emit(DataEvent.create(DataEventType.PUT, "test"))
        await asyncio.sleep(0.01)

        for r in results:
            assert r == ["test"]


class TestReplay:
    """Tests for replay() method."""

    @pytest.mark.asyncio
    async def test_replay_sends_buffered_events(self, bus: DataBus) -> None:
        """replay() sends buffered events to handler."""
        # Emit some events
        for i in range(3):
            await bus.emit(DataEvent.create(DataEventType.PUT, f"datum-{i}"))

        # Late subscriber uses replay
        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        count = await bus.replay(handler)

        assert count == 3
        assert len(received) == 3

    @pytest.mark.asyncio
    async def test_replay_with_since_filter(self, bus: DataBus) -> None:
        """replay() filters by timestamp."""
        e1 = DataEvent.create(DataEventType.PUT, "old")
        await bus.emit(e1)

        # Wait a bit to ensure timestamp difference
        await asyncio.sleep(0.01)
        cutoff = e1.timestamp + 0.001

        e2 = DataEvent.create(DataEventType.PUT, "new")
        await bus.emit(e2)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        count = await bus.replay(handler, since=cutoff)

        assert count == 1
        assert received[0].datum_id == "new"

    @pytest.mark.asyncio
    async def test_replay_with_event_type_filter(self, bus: DataBus) -> None:
        """replay() filters by event type."""
        await bus.emit(DataEvent.create(DataEventType.PUT, "put"))
        await bus.emit(DataEvent.create(DataEventType.DELETE, "del"))

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        count = await bus.replay(handler, event_type=DataEventType.PUT)

        assert count == 1
        assert received[0].event_type == DataEventType.PUT


class TestBusProperties:
    """Tests for bus properties."""

    @pytest.mark.asyncio
    async def test_latest_returns_most_recent(self, bus: DataBus) -> None:
        """latest returns most recent event."""
        assert bus.latest is None

        await bus.emit(DataEvent.create(DataEventType.PUT, "first"))
        await bus.emit(DataEvent.create(DataEventType.PUT, "second"))

        assert bus.latest is not None
        assert bus.latest.datum_id == "second"

    @pytest.mark.asyncio
    async def test_stats_tracks_counts(self, bus: DataBus) -> None:
        """stats tracks emission count."""
        assert bus.stats["total_emitted"] == 0

        await bus.emit(DataEvent.create(DataEventType.PUT, "test"))

        assert bus.stats["total_emitted"] == 1
        assert bus.stats["buffer_size"] == 1


class TestBusEnabledDgent:
    """Tests for BusEnabledDgent wrapper."""

    @pytest.mark.asyncio
    async def test_put_emits_event(self, bus: DataBus, memory_backend: MemoryBackend) -> None:
        """put() emits PUT event."""
        dgent = BusEnabledDgent(memory_backend, bus)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe(DataEventType.PUT, handler)

        d = Datum.create(b"test")
        await dgent.put(d)
        await asyncio.sleep(0.01)

        assert len(received) == 1
        assert received[0].event_type == DataEventType.PUT
        assert received[0].datum_id == d.id

    @pytest.mark.asyncio
    async def test_delete_emits_event(self, bus: DataBus, memory_backend: MemoryBackend) -> None:
        """delete() emits DELETE event when successful."""
        dgent = BusEnabledDgent(memory_backend, bus)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe(DataEventType.DELETE, handler)

        d = Datum.create(b"test")
        await dgent.put(d)
        await dgent.delete(d.id)
        await asyncio.sleep(0.01)

        assert len(received) == 1
        assert received[0].event_type == DataEventType.DELETE

    @pytest.mark.asyncio
    async def test_delete_no_event_for_missing(
        self, bus: DataBus, memory_backend: MemoryBackend
    ) -> None:
        """delete() doesn't emit event when datum missing."""
        dgent = BusEnabledDgent(memory_backend, bus)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe(DataEventType.DELETE, handler)

        await dgent.delete("nonexistent")
        await asyncio.sleep(0.01)

        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_get_does_not_emit(self, bus: DataBus, memory_backend: MemoryBackend) -> None:
        """get() does not emit events (reads are silent)."""
        dgent = BusEnabledDgent(memory_backend, bus)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe_all(handler)

        d = Datum.create(b"test")
        await dgent.put(d)
        await asyncio.sleep(0.01)

        initial_count = len(received)

        await dgent.get(d.id)
        await dgent.list()
        await dgent.exists(d.id)
        await asyncio.sleep(0.01)

        # No new events for reads
        assert len(received) == initial_count

    @pytest.mark.asyncio
    async def test_causal_linking_in_events(
        self, bus: DataBus, memory_backend: MemoryBackend
    ) -> None:
        """Events have causal linking."""
        dgent = BusEnabledDgent(memory_backend, bus)

        received: list[DataEvent] = []

        async def handler(event: DataEvent) -> None:
            received.append(event)

        bus.subscribe(DataEventType.PUT, handler)

        d1 = Datum.create(b"first")
        d2 = Datum.create(b"second")

        await dgent.put(d1)
        await dgent.put(d2)
        await asyncio.sleep(0.01)

        # Second event should have first's event_id as causal_parent
        assert received[1].causal_parent == received[0].event_id


class TestGlobalBus:
    """Tests for global bus singleton."""

    def test_get_data_bus_returns_singleton(self) -> None:
        """get_data_bus() returns same instance."""
        bus1 = get_data_bus()
        bus2 = get_data_bus()

        assert bus1 is bus2

    def test_reset_data_bus_clears_singleton(self) -> None:
        """reset_data_bus() clears singleton."""
        bus1 = get_data_bus()
        reset_data_bus()
        bus2 = get_data_bus()

        assert bus1 is not bus2


class TestErrorHandling:
    """Tests for error handling in bus."""

    @pytest.mark.asyncio
    async def test_subscriber_error_does_not_block(self, bus: DataBus) -> None:
        """Subscriber errors don't block other subscribers."""
        results: list[str] = []

        async def failing_handler(event: DataEvent) -> None:
            raise RuntimeError("Handler error")

        async def success_handler(event: DataEvent) -> None:
            results.append(event.datum_id)

        bus.subscribe(DataEventType.PUT, failing_handler)
        bus.subscribe(DataEventType.PUT, success_handler)

        await bus.emit(DataEvent.create(DataEventType.PUT, "test"))
        await asyncio.sleep(0.01)

        # Success handler should still receive event
        assert results == ["test"]

        # Error should be tracked
        assert bus.stats["total_errors"] >= 1
