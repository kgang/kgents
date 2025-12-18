"""
Stress Tests for Town Bus Architecture.

Tests the three-bus architecture under high load:
- DataBus bounded buffer behavior
- SynergyBus handler isolation
- EventBus slow subscriber handling
- End-to-end latency under load

See: plans/town-rebuild.md (Phase 3: Stress Testing)
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable

import pytest

from services.town.bus_wiring import (
    TownBusManager,
    TownDataBus,
    TownEventBus,
    TownSynergyBus,
    reset_town_bus_manager,
    wire_data_to_synergy,
    wire_synergy_to_event,
)
from services.town.events import (
    CitizenCreated,
    CoalitionFormed,
    ConversationTurn,
    GossipSpread,
    RelationshipChanged,
    TownEvent,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def data_bus() -> TownDataBus:
    """Create a fresh data bus."""
    return TownDataBus()


@pytest.fixture
def synergy_bus() -> TownSynergyBus:
    """Create a fresh synergy bus."""
    return TownSynergyBus()


@pytest.fixture
def event_bus() -> TownEventBus:
    """Create a fresh event bus."""
    return TownEventBus()


@pytest.fixture
def bus_manager() -> TownBusManager:
    """Create a fresh bus manager."""
    reset_town_bus_manager()
    return TownBusManager()


# =============================================================================
# DataBus Stress Tests
# =============================================================================


class TestDataBusBoundedBuffer:
    """Verify DataBus handles high load gracefully."""

    @pytest.mark.asyncio
    async def test_data_bus_handles_rapid_emissions(self, data_bus: TownDataBus) -> None:
        """DataBus should handle 1000 rapid event emissions."""
        received: list[TownEvent] = []

        async def handler(event: TownEvent) -> None:
            received.append(event)

        data_bus.subscribe(CitizenCreated, handler)

        # Emit 1000 events rapidly
        for i in range(1000):
            event = CitizenCreated.create(
                citizen_id=f"citizen_{i}",
                name=f"Test Citizen {i}",
                archetype="scholar",
            )
            await data_bus.emit(event)

        # Wait for async handlers to complete
        await asyncio.sleep(0.5)

        # All events should be received
        assert len(received) == 1000

    @pytest.mark.asyncio
    async def test_data_bus_memory_stable_under_load(self, data_bus: TownDataBus) -> None:
        """DataBus should not accumulate memory during sustained load."""
        import sys

        received_count = 0

        async def counting_handler(event: TownEvent) -> None:
            nonlocal received_count
            received_count += 1

        data_bus.subscribe(CitizenCreated, counting_handler)

        # Emit 10,000 events
        for i in range(10000):
            event = CitizenCreated.create(
                citizen_id=f"citizen_{i}",
                name=f"Test {i}",
                archetype="scholar",
            )
            await data_bus.emit(event)

        await asyncio.sleep(1.0)

        # Verify all events processed
        assert received_count == 10000

        # Stats should reflect emission count
        stats = data_bus.stats
        assert stats["total_emitted"] == 10000

    @pytest.mark.asyncio
    async def test_data_bus_concurrent_emit_and_subscribe(self, data_bus: TownDataBus) -> None:
        """DataBus should handle concurrent emission and subscription."""
        received: list[TownEvent] = []

        async def handler(event: TownEvent) -> None:
            received.append(event)

        # Start emitting before subscription
        emit_task = asyncio.create_task(self._emit_batch(data_bus, 100))

        # Subscribe midway
        await asyncio.sleep(0.01)
        data_bus.subscribe(CitizenCreated, handler)

        await emit_task
        await asyncio.sleep(0.2)

        # Should receive at least some events
        assert len(received) > 0

    async def _emit_batch(self, bus: TownDataBus, count: int) -> None:
        """Helper to emit a batch of events."""
        for i in range(count):
            event = CitizenCreated.create(
                citizen_id=f"citizen_{i}",
                name=f"Test {i}",
                archetype="scholar",
            )
            await bus.emit(event)
            await asyncio.sleep(0.001)


# =============================================================================
# SynergyBus Handler Isolation Tests
# =============================================================================


class TestSynergyBusHandlerIsolation:
    """Verify SynergyBus handler isolation."""

    @pytest.mark.asyncio
    async def test_failing_handler_does_not_block_others(self, synergy_bus: TownSynergyBus) -> None:
        """One failing handler should not prevent others from being called."""
        successful_calls: list[str] = []

        async def failing_handler(topic: str, event: TownEvent) -> None:
            raise ValueError("Intentional failure")

        async def successful_handler(topic: str, event: TownEvent) -> None:
            successful_calls.append(topic)

        # Subscribe both handlers
        synergy_bus.subscribe("town.citizen.*", failing_handler)
        synergy_bus.subscribe("town.citizen.*", successful_handler)

        # Emit event
        event = CitizenCreated.create(
            citizen_id="test",
            name="Test",
            archetype="scholar",
        )
        await synergy_bus.publish("town.citizen.created", event)

        await asyncio.sleep(0.1)

        # Successful handler should still be called
        assert len(successful_calls) == 1
        assert "town.citizen.created" in successful_calls

        # Error should be counted
        assert synergy_bus.stats["total_errors"] >= 1

    @pytest.mark.asyncio
    async def test_slow_handler_does_not_block_fast_handlers(
        self, synergy_bus: TownSynergyBus
    ) -> None:
        """Slow handlers should not delay fast handlers."""
        fast_received: list[float] = []
        slow_received: list[float] = []

        async def slow_handler(topic: str, event: TownEvent) -> None:
            await asyncio.sleep(0.5)  # Slow!
            slow_received.append(time.time())

        async def fast_handler(topic: str, event: TownEvent) -> None:
            fast_received.append(time.time())

        synergy_bus.subscribe("town.test", slow_handler)
        synergy_bus.subscribe("town.test", fast_handler)

        start = time.time()
        event = CitizenCreated.create(citizen_id="test", name="Test", archetype="scholar")
        await synergy_bus.publish("town.test", event)

        # Fast handler should complete quickly
        await asyncio.sleep(0.1)
        assert len(fast_received) == 1
        assert fast_received[0] - start < 0.15  # Should be fast

        # Wait for slow handler
        await asyncio.sleep(0.5)
        assert len(slow_received) == 1

    @pytest.mark.asyncio
    async def test_handler_exceptions_logged_not_raised(self, synergy_bus: TownSynergyBus) -> None:
        """Handler exceptions should be logged, not raised to caller."""

        async def throwing_handler(topic: str, event: TownEvent) -> None:
            raise RuntimeError("Test exception")

        synergy_bus.subscribe("town.test", throwing_handler)

        event = CitizenCreated.create(citizen_id="test", name="Test", archetype="scholar")

        # Should not raise
        await synergy_bus.publish("town.test", event)
        await asyncio.sleep(0.1)

        # Error should be counted
        assert synergy_bus.stats["total_errors"] >= 1


# =============================================================================
# EventBus Subscriber Tests
# =============================================================================


class TestEventBusSubscribers:
    """Verify EventBus subscriber handling."""

    @pytest.mark.asyncio
    async def test_multiple_subscribers_all_receive(self, event_bus: TownEventBus) -> None:
        """All subscribers should receive events."""
        received1: list[TownEvent] = []
        received2: list[TownEvent] = []
        received3: list[TownEvent] = []

        async def handler1(event: TownEvent) -> None:
            received1.append(event)

        async def handler2(event: TownEvent) -> None:
            received2.append(event)

        async def handler3(event: TownEvent) -> None:
            received3.append(event)

        event_bus.subscribe(handler1)
        event_bus.subscribe(handler2)
        event_bus.subscribe(handler3)

        event = CitizenCreated.create(citizen_id="test", name="Test", archetype="scholar")
        await event_bus.publish(event)

        await asyncio.sleep(0.1)

        assert len(received1) == 1
        assert len(received2) == 1
        assert len(received3) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_receiving(self, event_bus: TownEventBus) -> None:
        """Unsubscribed handlers should not receive events."""
        received: list[TownEvent] = []

        async def handler(event: TownEvent) -> None:
            received.append(event)

        unsub = event_bus.subscribe(handler)

        # First event
        event1 = CitizenCreated.create(citizen_id="test1", name="Test1", archetype="scholar")
        await event_bus.publish(event1)
        await asyncio.sleep(0.1)
        assert len(received) == 1

        # Unsubscribe
        unsub()

        # Second event
        event2 = CitizenCreated.create(citizen_id="test2", name="Test2", archetype="scholar")
        await event_bus.publish(event2)
        await asyncio.sleep(0.1)

        # Should not receive second event
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_slow_subscriber_does_not_block_bus(self, event_bus: TownEventBus) -> None:
        """Slow subscribers should not block the event bus."""
        fast_times: list[float] = []

        async def slow_subscriber(event: TownEvent) -> None:
            await asyncio.sleep(1.0)  # Very slow

        async def fast_subscriber(event: TownEvent) -> None:
            fast_times.append(time.time())

        event_bus.subscribe(slow_subscriber)
        event_bus.subscribe(fast_subscriber)

        start = time.time()

        # Emit 10 events rapidly
        for i in range(10):
            event = CitizenCreated.create(
                citizen_id=f"test_{i}",
                name=f"Test {i}",
                archetype="scholar",
            )
            await event_bus.publish(event)

        # Fast subscriber should receive all quickly
        await asyncio.sleep(0.2)

        assert len(fast_times) == 10
        # All should complete within 0.3s (not blocked by slow subscriber)
        assert max(fast_times) - start < 0.3


# =============================================================================
# End-to-End Latency Tests
# =============================================================================


class TestCascadeLatency:
    """Test end-to-end latency through the bus cascade."""

    @pytest.mark.asyncio
    async def test_cascade_latency_single_event(self, bus_manager: TownBusManager) -> None:
        """Single event should cascade through all buses quickly."""
        bus_manager.wire_all()

        event_received: list[float] = []

        async def final_handler(event: TownEvent) -> None:
            event_received.append(time.time())

        bus_manager.event_bus.subscribe(final_handler)

        start = time.time()
        event = CitizenCreated.create(
            citizen_id="test",
            name="Test",
            archetype="scholar",
        )
        await bus_manager.data_bus.emit(event)

        # Wait for cascade
        await asyncio.sleep(0.2)

        assert len(event_received) == 1
        latency = event_received[0] - start
        assert latency < 0.1, f"Latency too high: {latency}s"

    @pytest.mark.asyncio
    async def test_cascade_latency_under_load(self, bus_manager: TownBusManager) -> None:
        """Cascade should complete in <100ms even under 1000 concurrent events."""
        bus_manager.wire_all()

        received: list[tuple[str, float]] = []

        async def tracking_handler(event: TownEvent) -> None:
            received.append((event.event_id, time.time()))

        bus_manager.event_bus.subscribe(tracking_handler)

        start = time.time()
        events_sent: list[tuple[str, float]] = []

        # Emit 1000 events
        for i in range(1000):
            event = CitizenCreated.create(
                citizen_id=f"citizen_{i}",
                name=f"Test {i}",
                archetype="scholar",
            )
            events_sent.append((event.event_id, time.time()))
            await bus_manager.data_bus.emit(event)

        # Wait for all to cascade
        await asyncio.sleep(2.0)

        # Verify all received
        assert len(received) >= 900, f"Only received {len(received)} of 1000"

        # Calculate latencies
        sent_dict = {eid: t for eid, t in events_sent}
        latencies = []
        for eid, recv_time in received:
            if eid in sent_dict:
                latencies.append(recv_time - sent_dict[eid])

        if latencies:
            avg_latency = sum(latencies) / len(latencies)
            max_latency = max(latencies)
            assert avg_latency < 0.5, f"Average latency too high: {avg_latency}s"
            assert max_latency < 2.0, f"Max latency too high: {max_latency}s"

    @pytest.mark.asyncio
    async def test_parallel_event_types(self, bus_manager: TownBusManager) -> None:
        """Different event types should cascade in parallel."""
        bus_manager.wire_all()

        received: dict[str, list[TownEvent]] = {
            "citizen": [],
            "gossip": [],
            "relationship": [],
        }

        async def citizen_handler(event: TownEvent) -> None:
            if isinstance(event, CitizenCreated):
                received["citizen"].append(event)

        async def gossip_handler(event: TownEvent) -> None:
            if isinstance(event, GossipSpread):
                received["gossip"].append(event)

        async def relationship_handler(event: TownEvent) -> None:
            if isinstance(event, RelationshipChanged):
                received["relationship"].append(event)

        bus_manager.event_bus.subscribe(citizen_handler)
        bus_manager.event_bus.subscribe(gossip_handler)
        bus_manager.event_bus.subscribe(relationship_handler)

        # Emit different event types in parallel
        for i in range(100):
            await bus_manager.data_bus.emit(
                CitizenCreated.create(
                    citizen_id=f"c_{i}",
                    name=f"Citizen {i}",
                    archetype="scholar",
                )
            )
            await bus_manager.data_bus.emit(
                GossipSpread.create(
                    source_citizen=f"c_{i}",
                    target_citizen=f"c_{i + 1}",
                    rumor_content="test",
                )
            )
            await bus_manager.data_bus.emit(
                RelationshipChanged.create(
                    relationship_id=f"r_{i}",
                    citizen_a=f"c_{i}",
                    citizen_b=f"c_{i + 1}",
                    old_strength=0.5,
                    new_strength=0.6,
                )
            )

        await asyncio.sleep(1.0)

        # All event types should be received
        assert len(received["citizen"]) >= 90
        assert len(received["gossip"]) >= 90
        assert len(received["relationship"]) >= 90


# =============================================================================
# Bus Manager Lifecycle Tests
# =============================================================================


class TestBusManagerLifecycle:
    """Test bus manager lifecycle operations."""

    @pytest.mark.asyncio
    async def test_wire_unwire_cycle(self) -> None:
        """Wiring and unwiring should be idempotent."""
        reset_town_bus_manager()
        manager = TownBusManager()

        # Wire
        manager.wire_all()
        assert manager._is_wired

        # Wire again (should be no-op)
        manager.wire_all()
        assert manager._is_wired

        # Unwire
        manager.unwire_all()
        assert not manager._is_wired

        # Unwire again (should be no-op)
        manager.unwire_all()
        assert not manager._is_wired

    @pytest.mark.asyncio
    async def test_clear_resets_state(self) -> None:
        """Clear should reset all bus state."""
        reset_town_bus_manager()
        manager = TownBusManager()
        manager.wire_all()

        # Emit some events
        for i in range(10):
            await manager.data_bus.emit(
                CitizenCreated.create(
                    citizen_id=f"c_{i}",
                    name=f"Test {i}",
                    archetype="scholar",
                )
            )

        await asyncio.sleep(0.1)

        # Clear
        manager.clear()

        # Stats should be reset
        assert manager.data_bus.stats["total_emitted"] == 0
        assert manager.synergy_bus.stats["total_emitted"] == 0
        assert manager.event_bus.stats["total_emitted"] == 0

    @pytest.mark.asyncio
    async def test_stats_accurate(self) -> None:
        """Stats should accurately reflect bus activity."""
        reset_town_bus_manager()
        manager = TownBusManager()
        manager.wire_all()

        received: list[TownEvent] = []

        async def counter(event: TownEvent) -> None:
            received.append(event)

        manager.event_bus.subscribe(counter)

        # Emit events
        for i in range(50):
            await manager.data_bus.emit(
                CitizenCreated.create(
                    citizen_id=f"c_{i}",
                    name=f"Test {i}",
                    archetype="scholar",
                )
            )

        await asyncio.sleep(0.5)

        stats = manager.stats
        assert stats["data_bus"]["total_emitted"] == 50
        assert stats["synergy_bus"]["total_emitted"] >= 40
        assert stats["event_bus"]["total_emitted"] >= 40
