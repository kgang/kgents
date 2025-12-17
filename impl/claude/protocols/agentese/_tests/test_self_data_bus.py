"""
Tests for self.data.* and self.bus.* AGENTESE contexts.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
"""

from __future__ import annotations

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.d.bus import DataBus, DataEventType, get_data_bus, reset_data_bus
from agents.d.datum import Datum
from protocols.agentese.contexts import (
    BUS_AFFORDANCES,
    DATA_AFFORDANCES,
    BusNode,
    DataNode,
    create_bus_resolver,
    create_data_resolver,
)
from protocols.agentese.node import Observer


@pytest.fixture
def observer() -> Observer:
    """Create test observer."""
    return Observer.test()


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Create fresh memory backend."""
    return MemoryBackend()


@pytest.fixture
def data_bus() -> DataBus:
    """Create fresh data bus."""
    reset_data_bus()
    return DataBus()


class TestDataNode:
    """Tests for self.data.* context."""

    def test_affordances(self) -> None:
        """DATA_AFFORDANCES includes core 5 methods."""
        assert "put" in DATA_AFFORDANCES
        assert "get" in DATA_AFFORDANCES
        assert "delete" in DATA_AFFORDANCES
        assert "list" in DATA_AFFORDANCES
        assert "causal_chain" in DATA_AFFORDANCES

    def test_create_unconfigured_node(self) -> None:
        """DataNode can be created without D-gent."""
        node = create_data_resolver()
        assert node.handle == "self.data"
        assert node._dgent is None

    def test_create_configured_node(self, memory_backend: MemoryBackend) -> None:
        """DataNode can be created with D-gent backend."""
        node = create_data_resolver(dgent=memory_backend)
        assert node._dgent is memory_backend

    @pytest.mark.asyncio
    async def test_manifest_unconfigured(self, observer: Observer) -> None:
        """Manifest shows unconfigured state."""
        node = create_data_resolver()
        result = await node.manifest(observer)
        assert "Not Configured" in result.summary

    @pytest.mark.asyncio
    async def test_manifest_configured(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Manifest shows configured state."""
        node = create_data_resolver(dgent=memory_backend)
        result = await node.manifest(observer)
        assert "MemoryBackend" in result.content
        assert result.metadata["configured"] is True

    @pytest.mark.asyncio
    async def test_put_requires_content(self, observer: Observer) -> None:
        """Put aspect requires content."""
        node = create_data_resolver(dgent=MemoryBackend())
        result = await node._invoke_aspect("put", observer)
        assert "error" in result
        assert "content is required" in result["error"]

    @pytest.mark.asyncio
    async def test_put_stores_data(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Put aspect stores datum and returns ID."""
        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect(
            "put", observer, content="test content", metadata={"key": "value"}
        )
        assert result["status"] == "stored"
        assert "id" in result

        # Verify stored
        datum = await memory_backend.get(result["id"])
        assert datum is not None
        assert datum.content == "test content"

    @pytest.mark.asyncio
    async def test_get_returns_datum(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Get aspect retrieves datum by ID."""
        # Store a datum first
        datum = Datum.create(content="hello world")
        await memory_backend.put(datum)

        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("get", observer, id=datum.id)

        assert result["status"] == "found"
        assert result["content"] == "hello world"

    @pytest.mark.asyncio
    async def test_get_returns_not_found(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Get aspect returns not_found for missing datum."""
        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("get", observer, id="nonexistent")
        assert result["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_delete_removes_datum(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Delete aspect removes datum."""
        datum = Datum.create(content="to delete")
        await memory_backend.put(datum)

        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("delete", observer, id=datum.id)

        assert result["status"] == "deleted"
        assert await memory_backend.get(datum.id) is None

    @pytest.mark.asyncio
    async def test_list_returns_data(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """List aspect returns stored data."""
        # Store some data
        for i in range(3):
            await memory_backend.put(Datum.create(content=f"item {i}"))

        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("list", observer)

        assert result["status"] == "ok"
        assert result["count"] == 3

    @pytest.mark.asyncio
    async def test_causal_chain_traces_ancestry(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Causal chain aspect traces ancestry."""
        # Create chain: A -> B -> C
        a = Datum.create(content="ancestor")
        await memory_backend.put(a)
        b = Datum.create(content="middle", causal_parent=a.id)
        await memory_backend.put(b)
        c = Datum.create(content="descendant", causal_parent=b.id)
        await memory_backend.put(c)

        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("causal_chain", observer, id=c.id)

        assert result["chain_length"] == 3
        assert result["chain"][0]["content_preview"].startswith("ancestor")

    @pytest.mark.asyncio
    async def test_exists_checks_presence(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Exists aspect checks datum presence."""
        datum = Datum.create(content="exists test")
        await memory_backend.put(datum)

        node = create_data_resolver(dgent=memory_backend)

        result = await node._invoke_aspect("exists", observer, id=datum.id)
        assert result["exists"] is True

        result = await node._invoke_aspect("exists", observer, id="nonexistent")
        assert result["exists"] is False

    @pytest.mark.asyncio
    async def test_count_returns_total(
        self, observer: Observer, memory_backend: MemoryBackend
    ) -> None:
        """Count aspect returns total count."""
        for i in range(5):
            await memory_backend.put(Datum.create(content=f"item {i}"))

        node = create_data_resolver(dgent=memory_backend)
        result = await node._invoke_aspect("count", observer)

        assert result["count"] == 5


class TestBusNode:
    """Tests for self.bus.* context."""

    def test_affordances(self) -> None:
        """BUS_AFFORDANCES includes subscription methods."""
        assert "subscribe" in BUS_AFFORDANCES
        assert "unsubscribe" in BUS_AFFORDANCES
        assert "replay" in BUS_AFFORDANCES
        assert "latest" in BUS_AFFORDANCES
        assert "stats" in BUS_AFFORDANCES

    def test_create_unconfigured_node(self) -> None:
        """BusNode can be created without DataBus."""
        node = create_bus_resolver()
        assert node.handle == "self.bus"
        assert node._bus is None

    def test_create_configured_node(self, data_bus: DataBus) -> None:
        """BusNode can be created with DataBus."""
        node = create_bus_resolver(bus=data_bus)
        assert node._bus is data_bus

    @pytest.mark.asyncio
    async def test_manifest_unconfigured(self, observer: Observer) -> None:
        """Manifest shows unconfigured state."""
        node = create_bus_resolver()
        result = await node.manifest(observer)
        assert "Not Configured" in result.summary

    @pytest.mark.asyncio
    async def test_manifest_configured(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """Manifest shows bus statistics."""
        node = create_bus_resolver(bus=data_bus)
        result = await node.manifest(observer)
        assert "Buffer" in result.content
        assert result.metadata["configured"] is True

    @pytest.mark.asyncio
    async def test_stats_returns_bus_stats(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """Stats aspect returns bus statistics."""
        node = create_bus_resolver(bus=data_bus)
        result = await node._invoke_aspect("stats", observer)

        assert result["status"] == "ok"
        assert "buffer_size" in result
        assert "total_emitted" in result

    @pytest.mark.asyncio
    async def test_latest_when_no_events(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """Latest aspect returns no_events when empty."""
        node = create_bus_resolver(bus=data_bus)
        result = await node._invoke_aspect("latest", observer)

        assert result["status"] == "no_events"
        assert result["latest"] is None

    @pytest.mark.asyncio
    async def test_subscribe_creates_subscription(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """Subscribe aspect creates subscription."""
        node = create_bus_resolver(bus=data_bus)
        result = await node._invoke_aspect(
            "subscribe", observer, event_type="PUT", handler_id="test_handler"
        )

        assert result["status"] == "subscribed"
        assert result["handler_id"] == "test_handler"
        assert "test_handler" in node._subscriptions

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_subscription(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """Unsubscribe aspect removes subscription."""
        node = create_bus_resolver(bus=data_bus)

        # Subscribe first
        await node._invoke_aspect(
            "subscribe", observer, event_type="ALL", handler_id="to_remove"
        )
        assert "to_remove" in node._subscriptions

        # Unsubscribe
        result = await node._invoke_aspect(
            "unsubscribe", observer, handler_id="to_remove"
        )

        assert result["status"] == "unsubscribed"
        assert "to_remove" not in node._subscriptions

    @pytest.mark.asyncio
    async def test_history_returns_events(
        self, observer: Observer, data_bus: DataBus
    ) -> None:
        """History aspect returns buffered events."""
        from agents.d.bus import DataEvent

        # Emit some events
        for i in range(3):
            event = DataEvent.create(
                event_type=DataEventType.PUT, datum_id=f"datum_{i}", source="test"
            )
            await data_bus.emit(event)

        node = create_bus_resolver(bus=data_bus)
        result = await node._invoke_aspect("history", observer, limit=10)

        assert result["status"] == "ok"
        assert result["count"] == 3
        assert len(result["events"]) == 3


class TestSelfResolverIntegration:
    """Tests for self context resolver integration."""

    def test_resolve_data_path(self, memory_backend: MemoryBackend) -> None:
        """Self resolver resolves self.data path."""
        from protocols.agentese.contexts import create_self_resolver

        resolver = create_self_resolver(dgent_new=memory_backend)
        node = resolver.resolve("data", [])

        assert isinstance(node, DataNode)
        assert node._dgent is memory_backend

    def test_resolve_bus_path(self, data_bus: DataBus) -> None:
        """Self resolver resolves self.bus path."""
        from protocols.agentese.contexts import create_self_resolver

        resolver = create_self_resolver(data_bus=data_bus)
        node = resolver.resolve("bus", [])

        assert isinstance(node, BusNode)
        assert node._bus is data_bus

    def test_affordances_include_data_and_bus(self) -> None:
        """SELF_AFFORDANCES includes data and bus."""
        from protocols.agentese.contexts import SELF_AFFORDANCES

        assert "data" in SELF_AFFORDANCES
        assert "bus" in SELF_AFFORDANCES
        assert SELF_AFFORDANCES["data"] == DATA_AFFORDANCES
        assert SELF_AFFORDANCES["bus"] == BUS_AFFORDANCES


# =============================================================================
# Phase 5: Upgrader Node Tests
# =============================================================================


class TestUpgraderNode:
    """Tests for self.data.upgrader AGENTESE path."""

    def test_affordances(self) -> None:
        """UPGRADER_AFFORDANCES includes status, history, pending."""
        from protocols.agentese.contexts.self_data import UPGRADER_AFFORDANCES

        assert "status" in UPGRADER_AFFORDANCES
        assert "history" in UPGRADER_AFFORDANCES
        assert "pending" in UPGRADER_AFFORDANCES

    def test_data_affordances_includes_upgrader(self) -> None:
        """DATA_AFFORDANCES includes upgrader as sub-node."""
        assert "upgrader" in DATA_AFFORDANCES

    def test_create_data_resolver_creates_upgrader_node(
        self, memory_backend: MemoryBackend
    ) -> None:
        """create_data_resolver creates upgrader sub-node."""
        node = create_data_resolver(dgent=memory_backend)

        assert node._upgrader_node is not None
        assert node._upgrader_node.handle == "self.data.upgrader"

    @pytest.mark.asyncio
    async def test_manifest_unconfigured(self, observer: Observer) -> None:
        """Manifest shows unconfigured state without upgrader."""
        from protocols.agentese.contexts.self_data import UpgraderNode

        node = UpgraderNode()
        result = await node.manifest(observer)

        assert "Not Configured" in result.summary
        assert result.metadata["configured"] is False

    @pytest.mark.asyncio
    async def test_status_unconfigured(self, observer: Observer) -> None:
        """Status returns error when not configured."""
        from protocols.agentese.contexts.self_data import UpgraderNode

        node = UpgraderNode()
        result = await node._invoke_aspect("status", observer)

        assert "error" in result
        assert "not configured" in result["error"].lower()


# =============================================================================
# Phase 5: Upgrader + Synergy Integration Tests
# =============================================================================


class TestUpgraderSynergyIntegration:
    """
    Integration tests for upgrade → synergy event flow.

    Phase 5 Goal: Make tier promotions visible in UI via synergy events.
    """

    @pytest.fixture
    def jsonl_backend(self, tmp_path):
        """Create fresh JSONL backend."""
        from agents.d.backends.jsonl import JSONLBackend

        backend = JSONLBackend(namespace="synergy_test", data_dir=tmp_path)
        yield backend
        backend.clear()

    @pytest.fixture
    def upgrader(self, memory_backend, jsonl_backend, data_bus):
        """Create AutoUpgrader with fast thresholds for testing."""
        from agents.d.upgrader import AutoUpgrader, UpgradePolicy
        from agents.d.router import Backend

        return AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=data_bus,
            policy=UpgradePolicy(
                memory_to_jsonl_accesses=2,  # Fast threshold for testing
                memory_to_jsonl_seconds=999.0,  # Don't trigger on time
            ),
            check_interval=0.05,  # Fast checks for testing
            emit_synergy=True,
        )

    @pytest.mark.asyncio
    async def test_upgrader_node_with_upgrader(
        self, observer: Observer, memory_backend: MemoryBackend, upgrader
    ) -> None:
        """UpgraderNode shows correct state when wired."""
        node = create_data_resolver(dgent=memory_backend, upgrader=upgrader)

        # Get the upgrader sub-node
        upgrader_node = await node._invoke_aspect("upgrader", observer)

        # Check manifest
        result = await upgrader_node.manifest(observer)
        assert "Data Tier Upgrader" in result.summary
        assert result.metadata["configured"] is True

    @pytest.mark.asyncio
    async def test_upgrader_status_shows_tracked_data(
        self, observer: Observer, memory_backend: MemoryBackend, upgrader, data_bus
    ) -> None:
        """Status shows tracked data count."""
        from agents.d.bus import DataEvent

        await upgrader.start()
        try:
            # Emit events to trigger tracking
            event = DataEvent.create(DataEventType.PUT, "test-datum")
            await data_bus.emit(event)

            import asyncio

            await asyncio.sleep(0.05)  # Let event process

            node = create_data_resolver(dgent=memory_backend, upgrader=upgrader)
            upgrader_node = await node._invoke_aspect("upgrader", observer)
            status = await upgrader_node._invoke_aspect("status", observer)

            assert status["status"] == "running"
            assert status["tracked_data"] >= 1
        finally:
            await upgrader.stop()

    @pytest.mark.asyncio
    async def test_upgrade_emits_synergy_event(
        self, memory_backend: MemoryBackend, jsonl_backend, data_bus
    ) -> None:
        """
        Upgrade emits DATA_UPGRADED synergy event.

        This is the core Phase 5 test:
        1. Store datum in memory
        2. Force upgrade to JSONL
        3. Verify synergy event was emitted
        """
        from agents.d.upgrader import AutoUpgrader, UpgradePolicy
        from agents.d.router import Backend
        from protocols.synergy.bus import get_synergy_bus, reset_synergy_bus
        from protocols.synergy.events import SynergyEventType

        # Reset synergy bus for clean test
        reset_synergy_bus()
        synergy_bus = get_synergy_bus()

        # Track received events
        received_events = []

        # Create a simple handler to capture events
        class TestHandler:
            name = "test_handler"

            async def handle(self, event):
                received_events.append(event)
                from protocols.synergy.events import SynergyResult

                return SynergyResult(success=True, handler_name=self.name)

        # Register handler for DATA_UPGRADED events
        synergy_bus.register(SynergyEventType.DATA_UPGRADED, TestHandler())

        # Create upgrader with synergy emission enabled
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            bus=data_bus,
            policy=UpgradePolicy(memory_to_jsonl_accesses=2),
            emit_synergy=True,
            synergy_bus=synergy_bus,
        )

        # Store datum in memory (JSONL backend expects bytes)
        datum = Datum.create(content=b"test data for synergy")
        await memory_backend.put(datum)

        # Force upgrade
        success = await upgrader.force_upgrade(datum.id, Backend.JSONL)
        assert success is True

        # Wait for synergy event to be processed
        await synergy_bus.drain(timeout=1.0)

        # Verify synergy event was received
        assert len(received_events) == 1
        event = received_events[0]
        assert event.event_type == SynergyEventType.DATA_UPGRADED
        assert event.source_id == datum.id
        assert event.payload["old_tier"] == "MEMORY"
        assert event.payload["new_tier"] == "JSONL"

    @pytest.mark.asyncio
    async def test_upgrader_history_tracks_transitions(
        self, observer: Observer, memory_backend: MemoryBackend, jsonl_backend
    ) -> None:
        """History aspect tracks tier transitions."""
        from agents.d.upgrader import AutoUpgrader, UpgradePolicy
        from agents.d.router import Backend

        # Create upgrader
        upgrader = AutoUpgrader(
            source=memory_backend,
            source_tier=Backend.MEMORY,
            targets={Backend.JSONL: jsonl_backend},
            policy=UpgradePolicy(memory_to_jsonl_accesses=2),
            emit_synergy=False,  # Don't need synergy for this test
        )

        # Store and upgrade multiple data (JSONL backend expects bytes)
        for i in range(3):
            datum = Datum.create(content=f"history test {i}".encode())
            await memory_backend.put(datum)
            await upgrader.force_upgrade(datum.id, Backend.JSONL)

        # Check history via UpgraderNode
        node = create_data_resolver(dgent=memory_backend, upgrader=upgrader)
        upgrader_node = await node._invoke_aspect("upgrader", observer)
        history = await upgrader_node._invoke_aspect("history", observer)

        assert history["transitions"]["MEMORY_to_JSONL"] == 3
        assert history["total"] == 3
