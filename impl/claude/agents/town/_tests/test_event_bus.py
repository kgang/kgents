"""
Tests for EventBus fan-out event distribution.

Verifies:
- Single subscriber receives all events
- Multiple subscribers each receive all events (fan-out)
- Subscription lifecycle (subscribe, iterate, close)
- Backpressure handling (queue overflow)
- Bus close propagates to all subscribers
- Statistics tracking
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import pytest

from agents.town.event_bus import EventBus, Subscription, create_town_event_bus


@dataclass(frozen=True)
class MockEvent:
    """Simple event for testing."""

    id: int
    data: str


class TestEventBusBasic:
    """Basic EventBus functionality."""

    @pytest.mark.asyncio
    async def test_single_subscriber_receives_events(self) -> None:
        """Single subscriber receives all published events."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        # Publish events
        await bus.publish(MockEvent(1, "first"))
        await bus.publish(MockEvent(2, "second"))

        # Receive events
        event1 = await sub.get(timeout=1.0)
        event2 = await sub.get(timeout=1.0)

        assert event1 == MockEvent(1, "first")
        assert event2 == MockEvent(2, "second")

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_multiple_subscribers_fan_out(self) -> None:
        """Multiple subscribers each receive all events."""
        bus: EventBus[MockEvent] = EventBus()
        sub1 = bus.subscribe()
        sub2 = bus.subscribe()
        sub3 = bus.subscribe()

        # Publish single event
        delivered = await bus.publish(MockEvent(1, "broadcast"))

        # All subscribers should receive it
        assert delivered == 3
        assert await sub1.get(timeout=1.0) == MockEvent(1, "broadcast")
        assert await sub2.get(timeout=1.0) == MockEvent(1, "broadcast")
        assert await sub3.get(timeout=1.0) == MockEvent(1, "broadcast")

        sub1.close()
        sub2.close()
        sub3.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_async_iteration(self) -> None:
        """Subscription works as async iterator."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        # Publish in background
        async def publisher() -> None:
            for i in range(3):
                await bus.publish(MockEvent(i, f"event-{i}"))
            await asyncio.sleep(0.1)
            bus.close()

        # Collect via iteration
        events: list[MockEvent] = []

        async def consumer() -> None:
            async for event in sub:
                events.append(event)

        await asyncio.gather(publisher(), consumer())

        assert len(events) == 3
        assert events[0].id == 0
        assert events[1].id == 1
        assert events[2].id == 2


class TestSubscriptionLifecycle:
    """Subscription lifecycle management."""

    @pytest.mark.asyncio
    async def test_subscribe_returns_subscription(self) -> None:
        """subscribe() returns Subscription object."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        assert isinstance(sub, Subscription)
        assert not sub.is_closed
        assert bus.subscriber_count == 1

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_close_removes_subscriber(self) -> None:
        """Closing subscription removes from bus."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        assert bus.subscriber_count == 1

        sub.close()

        assert bus.subscriber_count == 0
        assert sub.is_closed

        bus.close()

    @pytest.mark.asyncio
    async def test_double_close_is_safe(self) -> None:
        """Closing subscription twice is safe."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        sub.close()
        sub.close()  # Should not raise

        assert sub.is_closed
        bus.close()

    @pytest.mark.asyncio
    async def test_subscribe_to_closed_bus_raises(self) -> None:
        """Cannot subscribe to closed bus."""
        bus: EventBus[MockEvent] = EventBus()
        bus.close()

        with pytest.raises(RuntimeError, match="closed"):
            bus.subscribe()


class TestBackpressure:
    """Backpressure and queue overflow handling."""

    @pytest.mark.asyncio
    async def test_queue_overflow_drops_events(self) -> None:
        """Events are dropped when subscriber queue is full."""
        bus: EventBus[MockEvent] = EventBus(max_queue_size=2)
        sub = bus.subscribe()

        # Fill the queue
        await bus.publish(MockEvent(1, "first"))
        await bus.publish(MockEvent(2, "second"))

        # This should be dropped (queue full)
        await bus.publish(MockEvent(3, "dropped"))

        assert bus.stats.queue_overflow_count == 1

        # Original events still available
        assert await sub.get(timeout=1.0) == MockEvent(1, "first")
        assert await sub.get(timeout=1.0) == MockEvent(2, "second")

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_pending_count(self) -> None:
        """pending_count shows queued events."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        assert sub.pending_count == 0

        await bus.publish(MockEvent(1, "a"))
        await bus.publish(MockEvent(2, "b"))

        assert sub.pending_count == 2

        await sub.get(timeout=1.0)

        assert sub.pending_count == 1

        sub.close()
        bus.close()


class TestBusClose:
    """Bus close behavior."""

    @pytest.mark.asyncio
    async def test_close_stops_iteration(self) -> None:
        """Closing bus stops all subscriber iterations."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        # Publish then close
        await bus.publish(MockEvent(1, "before"))
        bus.close()

        # Should get the event then stop
        events: list[MockEvent] = []
        async for event in sub:
            events.append(event)

        assert len(events) == 1
        assert events[0].id == 1

    @pytest.mark.asyncio
    async def test_publish_to_closed_bus_returns_zero(self) -> None:
        """Publishing to closed bus returns 0."""
        bus: EventBus[MockEvent] = EventBus()
        bus.close()

        delivered = await bus.publish(MockEvent(1, "ignored"))

        assert delivered == 0

    @pytest.mark.asyncio
    async def test_is_closed_property(self) -> None:
        """is_closed property reflects bus state."""
        bus: EventBus[MockEvent] = EventBus()

        assert not bus.is_closed

        bus.close()

        assert bus.is_closed


class TestStatistics:
    """Statistics tracking."""

    @pytest.mark.asyncio
    async def test_events_published_counter(self) -> None:
        """events_published increments on each publish."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        assert bus.stats.events_published == 0

        await bus.publish(MockEvent(1, "a"))
        await bus.publish(MockEvent(2, "b"))

        assert bus.stats.events_published == 2

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_events_delivered_counter(self) -> None:
        """events_delivered counts per-subscriber delivery."""
        bus: EventBus[MockEvent] = EventBus()
        sub1 = bus.subscribe()
        sub2 = bus.subscribe()

        await bus.publish(MockEvent(1, "a"))

        # 1 event × 2 subscribers = 2 deliveries
        assert bus.stats.events_delivered == 2

        sub1.close()
        sub2.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_subscriber_count_tracking(self) -> None:
        """Subscriber counts track current and peak."""
        bus: EventBus[MockEvent] = EventBus()

        assert bus.stats.subscribers_current == 0
        assert bus.stats.subscribers_peak == 0

        sub1 = bus.subscribe()
        assert bus.stats.subscribers_current == 1
        assert bus.stats.subscribers_peak == 1

        sub2 = bus.subscribe()
        assert bus.stats.subscribers_current == 2
        assert bus.stats.subscribers_peak == 2

        sub1.close()
        assert bus.stats.subscribers_current == 1
        assert bus.stats.subscribers_peak == 2  # Peak unchanged

        sub2.close()
        bus.close()


class TestTimeout:
    """Timeout behavior."""

    @pytest.mark.asyncio
    async def test_get_with_timeout_returns_none(self) -> None:
        """get() with timeout returns None when no events."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        result = await sub.get(timeout=0.1)

        assert result is None

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_get_without_timeout_blocks(self) -> None:
        """get() without timeout blocks until event."""
        bus: EventBus[MockEvent] = EventBus()
        sub = bus.subscribe()

        received: list[MockEvent] = []

        async def consumer() -> None:
            event = await sub.get()  # Blocks
            if event:
                received.append(event)

        async def publisher() -> None:
            await asyncio.sleep(0.05)
            await bus.publish(MockEvent(1, "delayed"))

        await asyncio.gather(consumer(), publisher())

        assert len(received) == 1
        assert received[0].id == 1

        sub.close()
        bus.close()


class TestFactory:
    """Factory function tests."""

    def test_create_town_event_bus(self) -> None:
        """create_town_event_bus creates EventBus."""
        bus = create_town_event_bus()
        assert isinstance(bus, EventBus)
        bus.close()

    def test_create_with_custom_queue_size(self) -> None:
        """create_town_event_bus accepts max_queue_size."""
        bus = create_town_event_bus(max_queue_size=50)
        assert bus.max_queue_size == 50
        bus.close()


class TestConcurrency:
    """Concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_publish_and_consume(self) -> None:
        """Multiple publishers and consumers work correctly."""
        bus: EventBus[MockEvent] = EventBus()
        received: list[MockEvent] = []
        lock = asyncio.Lock()

        async def publisher(start_id: int) -> None:
            for i in range(5):
                await bus.publish(MockEvent(start_id + i, f"pub-{start_id}"))
                await asyncio.sleep(0.01)

        async def consumer(sub: Subscription[MockEvent]) -> None:
            while not sub.is_closed:
                event = await sub.get(timeout=0.1)
                if event:
                    async with lock:
                        received.append(event)

        sub1 = bus.subscribe()
        sub2 = bus.subscribe()

        # Run publishers then close
        await asyncio.gather(
            publisher(0),
            publisher(100),
        )

        # Let events propagate
        await asyncio.sleep(0.1)

        # Start consumers briefly
        consumer_task1 = asyncio.create_task(consumer(sub1))
        consumer_task2 = asyncio.create_task(consumer(sub2))

        # Wait for consumers to drain queues
        await asyncio.sleep(0.2)

        # Close to stop consumers
        sub1.close()
        sub2.close()
        bus.close()

        # Cancel consumer tasks
        consumer_task1.cancel()
        consumer_task2.cancel()

        try:
            await consumer_task1
        except asyncio.CancelledError:
            pass
        try:
            await consumer_task2
        except asyncio.CancelledError:
            pass

        # Each subscriber should have received events from both publishers
        # 10 events × 2 subscribers = 20 received
        assert len(received) == 20


class TestFluxIntegration:
    """Integration with TownFlux."""

    @pytest.mark.asyncio
    async def test_flux_publishes_to_event_bus(self) -> None:
        """TownFlux publishes events to wired event bus."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux

        # Create environment with 3 citizens (minimum viable)
        env = create_mpp_environment()

        # Create event bus and subscribe
        bus: EventBus[Any] = EventBus()
        sub = bus.subscribe()

        # Create flux with event bus
        flux = TownFlux(env, seed=42, event_bus=bus)

        # Run one step
        events_yielded = []
        async for event in flux.step():
            events_yielded.append(event)

        # Subscriber should have received all events
        events_received = []
        while sub.pending_count > 0:
            received = await sub.get(timeout=0.1)
            if received:
                events_received.append(received)

        assert len(events_received) == len(events_yielded)
        assert events_received == events_yielded

        sub.close()
        bus.close()

    @pytest.mark.asyncio
    async def test_set_event_bus_after_construction(self) -> None:
        """Can wire event bus after TownFlux construction."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux

        env = create_mpp_environment()
        flux = TownFlux(env, seed=42)

        # Initially no bus
        assert flux.event_bus is None

        # Wire bus
        bus: EventBus[Any] = EventBus()
        flux.set_event_bus(bus)

        assert flux.event_bus is bus

        bus.close()

    @pytest.mark.asyncio
    async def test_multiple_subscribers_receive_flux_events(self) -> None:
        """Multiple subscribers each receive all flux events."""
        from agents.town.environment import create_mpp_environment
        from agents.town.flux import TownFlux

        env = create_mpp_environment()
        bus: EventBus[Any] = EventBus()
        flux = TownFlux(env, seed=42, event_bus=bus)

        # Multiple subscribers
        sub1 = bus.subscribe()
        sub2 = bus.subscribe()

        # Run step
        async for _ in flux.step():
            pass

        # Both should have same events
        events1 = []
        events2 = []
        while sub1.pending_count > 0:
            event = await sub1.get(timeout=0.1)
            if event:
                events1.append(event)
        while sub2.pending_count > 0:
            event = await sub2.get(timeout=0.1)
            if event:
                events2.append(event)

        assert len(events1) == len(events2)
        assert len(events1) > 0

        sub1.close()
        sub2.close()
        bus.close()
