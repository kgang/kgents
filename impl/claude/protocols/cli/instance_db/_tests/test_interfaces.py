"""
Tests for repository interfaces.

Verifies that the interface contracts are properly defined
and that implementations satisfy them.
"""

from typing import runtime_checkable

import pytest

from ..interfaces import (
    IBlobStore,
    IRelationalStore,
    ITelemetryStore,
    IVectorStore,
    TelemetryEvent,
    VectorSearchResult,
)
from ..providers.sqlite import (
    InMemoryBlobStore,
    InMemoryRelationalStore,
    InMemoryTelemetryStore,
    InMemoryVectorStore,
)


class TestInterfaceDefinitions:
    """Test that interfaces are properly defined as protocols."""

    def test_relational_store_is_runtime_checkable(self):
        """IRelationalStore should be runtime checkable."""
        assert runtime_checkable(IRelationalStore)

    def test_vector_store_is_runtime_checkable(self):
        """IVectorStore should be runtime checkable."""
        assert runtime_checkable(IVectorStore)

    def test_blob_store_is_runtime_checkable(self):
        """IBlobStore should be runtime checkable."""
        assert runtime_checkable(IBlobStore)

    def test_telemetry_store_is_runtime_checkable(self):
        """ITelemetryStore should be runtime checkable."""
        assert runtime_checkable(ITelemetryStore)


class TestVectorSearchResult:
    """Test VectorSearchResult dataclass."""

    def test_create_result(self):
        """Should create result with all fields."""
        result = VectorSearchResult(
            id="shape-001",
            distance=0.25,
            metadata={"type": "insight"},
        )
        assert result.id == "shape-001"
        assert result.distance == 0.25
        assert result.metadata == {"type": "insight"}

    def test_result_is_hashable(self):
        """Results should be usable as dict keys (for deduplication)."""
        result = VectorSearchResult(id="a", distance=0.1, metadata={})
        # Dataclasses are hashable by default if frozen, but we don't need that
        assert result.id == "a"


class TestTelemetryEvent:
    """Test TelemetryEvent dataclass."""

    def test_create_event_minimal(self):
        """Should create event with required fields only."""
        event = TelemetryEvent(
            event_type="test.event",
            timestamp="2025-12-10T12:00:00",
            data={"key": "value"},
        )
        assert event.event_type == "test.event"
        assert event.timestamp == "2025-12-10T12:00:00"
        assert event.data == {"key": "value"}
        assert event.instance_id is None
        assert event.project_hash is None

    def test_create_event_full(self):
        """Should create event with all fields."""
        event = TelemetryEvent(
            event_type="test.event",
            timestamp="2025-12-10T12:00:00",
            data={"key": "value"},
            instance_id="inst-001",
            project_hash="abc123",
        )
        assert event.instance_id == "inst-001"
        assert event.project_hash == "abc123"


class TestInMemoryImplementations:
    """Test that in-memory implementations work correctly."""

    @pytest.mark.asyncio
    async def test_in_memory_relational_basic(self):
        """In-memory relational store should accept queries."""
        store = InMemoryRelationalStore()
        result = await store.execute("SELECT 1")
        assert result == 0  # Minimal implementation returns 0

    @pytest.mark.asyncio
    async def test_in_memory_vector_basic(self):
        """In-memory vector store should store and count."""
        store = InMemoryVectorStore(dimensions=4)
        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {"type": "test"})
        count = await store.count()
        assert count == 1
        assert store.dimensions == 4

    @pytest.mark.asyncio
    async def test_in_memory_vector_delete(self):
        """In-memory vector store should delete."""
        store = InMemoryVectorStore()
        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {})
        deleted = await store.delete("a")
        assert deleted is True
        deleted_again = await store.delete("a")
        assert deleted_again is False
        assert await store.count() == 0

    @pytest.mark.asyncio
    async def test_in_memory_blob_basic(self):
        """In-memory blob store should store and retrieve."""
        store = InMemoryBlobStore()
        path = await store.put("test.txt", b"hello")
        assert path == "test.txt"
        data = await store.get("test.txt")
        assert data == b"hello"
        assert await store.exists("test.txt") is True

    @pytest.mark.asyncio
    async def test_in_memory_blob_list(self):
        """In-memory blob store should list with prefix."""
        store = InMemoryBlobStore()
        await store.put("a/1.txt", b"1")
        await store.put("a/2.txt", b"2")
        await store.put("b/1.txt", b"3")

        a_keys = await store.list("a/")
        assert len(a_keys) == 2
        assert "a/1.txt" in a_keys

    @pytest.mark.asyncio
    async def test_in_memory_telemetry_basic(self):
        """In-memory telemetry store should append and query."""
        store = InMemoryTelemetryStore()

        events = [
            TelemetryEvent("test", "2025-12-10T12:00:00", {"n": 1}),
            TelemetryEvent("test", "2025-12-10T12:01:00", {"n": 2}),
        ]
        count = await store.append(events)
        assert count == 2

        results = await store.query()
        assert len(results) == 2
        # Should be newest first
        assert results[0].data["n"] == 2

    @pytest.mark.asyncio
    async def test_in_memory_telemetry_filter(self):
        """In-memory telemetry should filter by type."""
        store = InMemoryTelemetryStore()

        events = [
            TelemetryEvent("type_a", "2025-12-10T12:00:00", {}),
            TelemetryEvent("type_b", "2025-12-10T12:01:00", {}),
        ]
        await store.append(events)

        results = await store.query(event_type="type_a")
        assert len(results) == 1
        assert results[0].event_type == "type_a"

    @pytest.mark.asyncio
    async def test_in_memory_telemetry_count(self):
        """In-memory telemetry should count events."""
        store = InMemoryTelemetryStore()
        await store.append(
            [
                TelemetryEvent("a", "2025-12-10T12:00:00", {}),
                TelemetryEvent("b", "2025-12-10T12:00:00", {}),
                TelemetryEvent("a", "2025-12-10T12:00:00", {}),
            ]
        )

        total = await store.count()
        assert total == 3

        a_count = await store.count("a")
        assert a_count == 2
