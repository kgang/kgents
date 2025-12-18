"""Tests for Town Bus Wiring module."""

from __future__ import annotations

import asyncio

import pytest

from services.town.bus_wiring import (
    TownBusManager,
    TownDataBus,
    TownEventBus,
    TownSynergyBus,
    get_town_bus_manager,
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
    TownTopics,
)

# =============================================================================
# TownDataBus Tests
# =============================================================================


class TestTownDataBus:
    """Tests for TownDataBus."""

    @pytest.fixture
    def bus(self) -> TownDataBus:
        """Create a fresh bus for each test."""
        return TownDataBus()

    @pytest.mark.asyncio
    async def test_emit_basic(self, bus: TownDataBus) -> None:
        """Should emit events."""
        event = CitizenCreated.create("c1", "Alice", "scholar")
        await bus.emit(event)
        assert bus.stats["total_emitted"] == 1

    @pytest.mark.asyncio
    async def test_subscribe_receives_events(self, bus: TownDataBus) -> None:
        """Subscriber should receive events."""
        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        bus.subscribe(CitizenCreated, handler)
        event = CitizenCreated.create("c1", "Alice", "scholar")
        await bus.emit(event)

        await asyncio.sleep(0.01)  # Allow handler to run
        assert len(received) == 1
        assert received[0] == event

    @pytest.mark.asyncio
    async def test_subscribe_type_filtering(self, bus: TownDataBus) -> None:
        """Subscriber should only receive subscribed types."""
        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        bus.subscribe(CitizenCreated, handler)

        # Emit different types
        await bus.emit(CitizenCreated.create("c1", "Alice", "x"))
        await bus.emit(ConversationTurn.create("conv", "c1", 0, "user", "Hi"))

        await asyncio.sleep(0.01)
        assert len(received) == 1  # Only CitizenCreated

    @pytest.mark.asyncio
    async def test_subscribe_all(self, bus: TownDataBus) -> None:
        """subscribe_all should receive all events."""
        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        bus.subscribe_all(handler)

        await bus.emit(CitizenCreated.create("c1", "Alice", "x"))
        await bus.emit(ConversationTurn.create("conv", "c1", 0, "user", "Hi"))

        await asyncio.sleep(0.01)
        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus: TownDataBus) -> None:
        """Unsubscribe should stop receiving events."""
        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        unsub = bus.subscribe(CitizenCreated, handler)
        await bus.emit(CitizenCreated.create("c1", "A", "x"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

        unsub()  # Unsubscribe

        await bus.emit(CitizenCreated.create("c2", "B", "y"))
        await asyncio.sleep(0.01)
        assert len(received) == 1  # No new events

    def test_clear(self, bus: TownDataBus) -> None:
        """Clear should reset the bus."""
        bus._emit_count = 10

        async def handler(e: TownEvent) -> None:
            pass

        bus.subscribe(CitizenCreated, handler)
        bus.clear()

        assert bus.stats["total_emitted"] == 0
        assert bus.stats["type_count"] == 0


# =============================================================================
# TownSynergyBus Tests
# =============================================================================


class TestTownSynergyBus:
    """Tests for TownSynergyBus."""

    @pytest.fixture
    def bus(self) -> TownSynergyBus:
        """Create a fresh bus for each test."""
        return TownSynergyBus()

    @pytest.mark.asyncio
    async def test_publish_basic(self, bus: TownSynergyBus) -> None:
        """Should publish events."""
        event = CitizenCreated.create("c1", "Alice", "scholar")
        await bus.publish(TownTopics.CITIZEN_CREATED, event)
        assert bus.stats["total_emitted"] == 1

    @pytest.mark.asyncio
    async def test_subscribe_exact_topic(self, bus: TownSynergyBus) -> None:
        """Should receive events on exact topic match."""
        received: list[tuple[str, TownEvent]] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append((topic, event))

        bus.subscribe(TownTopics.CITIZEN_CREATED, handler)
        event = CitizenCreated.create("c1", "Alice", "x")
        await bus.publish(TownTopics.CITIZEN_CREATED, event)

        await asyncio.sleep(0.01)
        assert len(received) == 1
        assert received[0][0] == TownTopics.CITIZEN_CREATED

    @pytest.mark.asyncio
    async def test_wildcard_subscription(self, bus: TownSynergyBus) -> None:
        """Wildcard should match multiple topics."""
        received: list[str] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(topic)

        bus.subscribe("town.citizen.*", handler)

        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c1", "A", "x"))
        await bus.publish(TownTopics.CITIZEN_UPDATED, CitizenCreated.create("c2", "B", "y"))
        await bus.publish(
            TownTopics.CONVERSATION_TURN, ConversationTurn.create("c", "c1", 0, "u", "h")
        )

        await asyncio.sleep(0.01)
        assert len(received) == 2  # Only citizen topics

    @pytest.mark.asyncio
    async def test_all_wildcard(self, bus: TownSynergyBus) -> None:
        """town.* should match all town events."""
        received: list[str] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(topic)

        bus.subscribe("town.*", handler)

        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c1", "A", "x"))
        await bus.publish(TownTopics.GOSSIP_SPREAD, GossipSpread.create("a", "b", "x"))

        await asyncio.sleep(0.01)
        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_no_match_on_wrong_topic(self, bus: TownSynergyBus) -> None:
        """Should not receive events on non-matching topics."""
        received: list[TownEvent] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(event)

        bus.subscribe(TownTopics.GOSSIP_SPREAD, handler)
        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c1", "A", "x"))

        await asyncio.sleep(0.01)
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_exact(self, bus: TownSynergyBus) -> None:
        """Unsubscribe from exact topic."""
        received: list[TownEvent] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(event)

        unsub = bus.subscribe(TownTopics.CITIZEN_CREATED, handler)
        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c1", "A", "x"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

        unsub()
        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c2", "B", "y"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_unsubscribe_wildcard(self, bus: TownSynergyBus) -> None:
        """Unsubscribe from wildcard topic."""
        received: list[TownEvent] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(event)

        unsub = bus.subscribe("town.*", handler)
        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c1", "A", "x"))
        await asyncio.sleep(0.01)
        assert len(received) == 1

        unsub()
        await bus.publish(TownTopics.CITIZEN_CREATED, CitizenCreated.create("c2", "B", "y"))
        await asyncio.sleep(0.01)
        assert len(received) == 1


# =============================================================================
# TownEventBus Tests
# =============================================================================


class TestTownEventBus:
    """Tests for TownEventBus."""

    @pytest.fixture
    def bus(self) -> TownEventBus:
        """Create a fresh bus for each test."""
        return TownEventBus()

    @pytest.mark.asyncio
    async def test_publish_basic(self, bus: TownEventBus) -> None:
        """Should publish events."""
        event = CitizenCreated.create("c1", "Alice", "scholar")
        await bus.publish(event)
        assert bus.stats["total_emitted"] == 1

    @pytest.mark.asyncio
    async def test_subscribe_receives_all(self, bus: TownEventBus) -> None:
        """Subscriber receives all events."""
        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        bus.subscribe(handler)

        await bus.publish(CitizenCreated.create("c1", "A", "x"))
        await bus.publish(GossipSpread.create("a", "b", "x"))

        await asyncio.sleep(0.01)
        assert len(received) == 2

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, bus: TownEventBus) -> None:
        """Multiple subscribers all receive events."""
        received1: list[TownEvent] = []
        received2: list[TownEvent] = []

        async def handler1(e: TownEvent) -> None:
            received1.append(e)

        async def handler2(e: TownEvent) -> None:
            received2.append(e)

        bus.subscribe(handler1)
        bus.subscribe(handler2)

        await bus.publish(CitizenCreated.create("c1", "A", "x"))
        await asyncio.sleep(0.01)

        assert len(received1) == 1
        assert len(received2) == 1


# =============================================================================
# Bus Wiring Tests
# =============================================================================


class TestWireDataToSynergy:
    """Tests for wire_data_to_synergy function."""

    @pytest.mark.asyncio
    async def test_citizen_created_wired(self) -> None:
        """CitizenCreated should propagate to synergy bus."""
        data_bus = TownDataBus()
        synergy_bus = TownSynergyBus()

        received: list[str] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(topic)

        synergy_bus.subscribe(TownTopics.CITIZEN_CREATED, handler)
        wire_data_to_synergy(data_bus, synergy_bus)

        await data_bus.emit(CitizenCreated.create("c1", "Alice", "x"))
        await asyncio.sleep(0.01)

        assert TownTopics.CITIZEN_CREATED in received

    @pytest.mark.asyncio
    async def test_gossip_wired(self) -> None:
        """GossipSpread should propagate to synergy bus."""
        data_bus = TownDataBus()
        synergy_bus = TownSynergyBus()

        received: list[str] = []

        async def handler(topic: str, event: TownEvent) -> None:
            received.append(topic)

        synergy_bus.subscribe(TownTopics.GOSSIP_SPREAD, handler)
        wire_data_to_synergy(data_bus, synergy_bus)

        await data_bus.emit(GossipSpread.create("alice", "bob", "news"))
        await asyncio.sleep(0.01)

        assert TownTopics.GOSSIP_SPREAD in received


class TestWireSynergyToEvent:
    """Tests for wire_synergy_to_event function."""

    @pytest.mark.asyncio
    async def test_all_topics_wired(self) -> None:
        """All town events should propagate to event bus."""
        synergy_bus = TownSynergyBus()
        event_bus = TownEventBus()

        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        event_bus.subscribe(handler)
        wire_synergy_to_event(synergy_bus, event_bus)

        event = CitizenCreated.create("c1", "Alice", "x")
        await synergy_bus.publish(TownTopics.CITIZEN_CREATED, event)
        await asyncio.sleep(0.01)

        assert len(received) == 1


# =============================================================================
# TownBusManager Tests
# =============================================================================


class TestTownBusManager:
    """Tests for TownBusManager."""

    @pytest.fixture
    def manager(self) -> TownBusManager:
        """Create a fresh manager for each test."""
        return TownBusManager()

    def test_init_creates_buses(self, manager: TownBusManager) -> None:
        """Manager should create all buses."""
        assert manager.data_bus is not None
        assert manager.synergy_bus is not None
        assert manager.event_bus is not None

    def test_wire_all(self, manager: TownBusManager) -> None:
        """wire_all should wire buses together."""
        manager.wire_all()
        assert manager._is_wired

    def test_wire_all_idempotent(self, manager: TownBusManager) -> None:
        """Multiple wire_all calls should be safe."""
        manager.wire_all()
        manager.wire_all()
        assert manager._is_wired

    @pytest.mark.asyncio
    async def test_end_to_end_flow(self, manager: TownBusManager) -> None:
        """Events should flow from DataBus to EventBus."""
        manager.wire_all()

        received: list[TownEvent] = []

        async def handler(e: TownEvent) -> None:
            received.append(e)

        manager.event_bus.subscribe(handler)

        event = CitizenCreated.create("c1", "Alice", "scholar")
        await manager.data_bus.emit(event)

        await asyncio.sleep(0.02)  # Allow propagation

        assert len(received) == 1

    def test_unwire_all(self, manager: TownBusManager) -> None:
        """unwire_all should disconnect buses."""
        manager.wire_all()
        manager.unwire_all()
        assert not manager._is_wired

    def test_clear(self, manager: TownBusManager) -> None:
        """clear should reset everything."""
        manager.wire_all()
        manager.clear()
        assert not manager._is_wired
        assert manager.data_bus.stats["total_emitted"] == 0

    def test_stats(self, manager: TownBusManager) -> None:
        """stats should aggregate from all buses."""
        stats = manager.stats
        assert "data_bus" in stats
        assert "synergy_bus" in stats
        assert "event_bus" in stats


class TestGlobalBusManager:
    """Tests for global bus manager singleton."""

    def test_get_returns_manager(self) -> None:
        """get_town_bus_manager should return a manager."""
        reset_town_bus_manager()
        manager = get_town_bus_manager()
        assert isinstance(manager, TownBusManager)

    def test_get_returns_same_instance(self) -> None:
        """Multiple calls should return the same instance."""
        reset_town_bus_manager()
        m1 = get_town_bus_manager()
        m2 = get_town_bus_manager()
        assert m1 is m2

    def test_reset_clears_singleton(self) -> None:
        """reset should clear the singleton."""
        reset_town_bus_manager()
        m1 = get_town_bus_manager()
        reset_town_bus_manager()
        m2 = get_town_bus_manager()
        assert m1 is not m2


class TestHandlerIsolation:
    """Tests that handlers are isolated (one failure doesn't affect others)."""

    @pytest.mark.asyncio
    async def test_failing_handler_isolated(self) -> None:
        """A failing handler should not affect other handlers."""
        bus = TownDataBus()
        received: list[TownEvent] = []

        async def failing_handler(e: TownEvent) -> None:
            raise ValueError("Intentional failure")

        async def working_handler(e: TownEvent) -> None:
            received.append(e)

        bus.subscribe_all(failing_handler)
        bus.subscribe_all(working_handler)

        await bus.emit(CitizenCreated.create("c1", "A", "x"))
        await asyncio.sleep(0.01)

        # Working handler should still receive the event
        assert len(received) == 1
