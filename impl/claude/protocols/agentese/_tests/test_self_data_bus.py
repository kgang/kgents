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
