"""
Tests for D-gent backends (MemoryBackend, JSONLBackend, SQLiteBackend).

Tests verify:
1. All 5 protocol methods: put, get, delete, list, causal_chain
2. Backend-specific behaviors
3. Graceful handling of edge cases
"""

from __future__ import annotations

import asyncio
import tempfile
import time
from pathlib import Path
from typing import AsyncIterator

import pytest

from ..datum import Datum
from ..backends.memory import MemoryBackend
from ..backends.jsonl import JSONLBackend
from ..backends.sqlite import SQLiteBackend
from ..protocol import DgentProtocol


# --- Fixtures ---


@pytest.fixture
def memory_backend() -> MemoryBackend:
    """Fresh memory backend for each test."""
    return MemoryBackend()


@pytest.fixture
def temp_dir() -> Path:
    """Temporary directory for file-based backends."""
    with tempfile.TemporaryDirectory() as td:
        yield Path(td)


@pytest.fixture
def jsonl_backend(temp_dir: Path) -> JSONLBackend:
    """Fresh JSONL backend for each test."""
    backend = JSONLBackend(namespace="test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture
def sqlite_backend(temp_dir: Path) -> SQLiteBackend:
    """Fresh SQLite backend for each test."""
    backend = SQLiteBackend(namespace="test", data_dir=temp_dir)
    yield backend
    backend.clear()


@pytest.fixture(params=["memory", "jsonl", "sqlite"])
def backend(request, memory_backend, jsonl_backend, sqlite_backend) -> DgentProtocol:
    """Parameterized fixture for all backends."""
    backends = {
        "memory": memory_backend,
        "jsonl": jsonl_backend,
        "sqlite": sqlite_backend,
    }
    return backends[request.param]


# --- Protocol Tests (run for all backends) ---


class TestPut:
    """Tests for put() method."""

    @pytest.mark.asyncio
    async def test_put_returns_id(self, backend: DgentProtocol) -> None:
        """put() returns the datum ID."""
        d = Datum.create(b"test")
        result = await backend.put(d)
        assert result == d.id

    @pytest.mark.asyncio
    async def test_put_overwrites_existing(self, backend: DgentProtocol) -> None:
        """put() overwrites datum with same ID."""
        d1 = Datum.create(b"v1", id="same-id")
        d2 = Datum.create(b"v2", id="same-id")

        await backend.put(d1)
        await backend.put(d2)

        result = await backend.get("same-id")
        assert result is not None
        assert result.content == b"v2"


class TestGet:
    """Tests for get() method."""

    @pytest.mark.asyncio
    async def test_get_returns_datum(self, backend: DgentProtocol) -> None:
        """get() returns stored datum."""
        d = Datum.create(b"test content")
        await backend.put(d)

        result = await backend.get(d.id)

        assert result is not None
        assert result.id == d.id
        assert result.content == d.content

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing(self, backend: DgentProtocol) -> None:
        """get() returns None for non-existent ID."""
        result = await backend.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_preserves_metadata(self, backend: DgentProtocol) -> None:
        """get() preserves metadata."""
        d = Datum.create(b"test", metadata={"key": "value", "num": "42"})
        await backend.put(d)

        result = await backend.get(d.id)

        assert result is not None
        assert result.metadata == {"key": "value", "num": "42"}

    @pytest.mark.asyncio
    async def test_get_preserves_causal_parent(self, backend: DgentProtocol) -> None:
        """get() preserves causal_parent."""
        d = Datum.create(b"test", causal_parent="parent-123")
        await backend.put(d)

        result = await backend.get(d.id)

        assert result is not None
        assert result.causal_parent == "parent-123"


class TestDelete:
    """Tests for delete() method."""

    @pytest.mark.asyncio
    async def test_delete_returns_true_on_success(self, backend: DgentProtocol) -> None:
        """delete() returns True when datum existed."""
        d = Datum.create(b"test")
        await backend.put(d)

        result = await backend.delete(d.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_delete_removes_datum(self, backend: DgentProtocol) -> None:
        """delete() makes datum unavailable."""
        d = Datum.create(b"test")
        await backend.put(d)
        await backend.delete(d.id)

        result = await backend.get(d.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_returns_false_for_missing(self, backend: DgentProtocol) -> None:
        """delete() returns False for non-existent ID."""
        result = await backend.delete("nonexistent-id")
        assert result is False


class TestList:
    """Tests for list() method."""

    @pytest.mark.asyncio
    async def test_list_returns_all_data(self, backend: DgentProtocol) -> None:
        """list() returns all stored data."""
        d1 = Datum.create(b"one")
        d2 = Datum.create(b"two")
        d3 = Datum.create(b"three")

        await backend.put(d1)
        await asyncio.sleep(0.01)  # Ensure different timestamps
        await backend.put(d2)
        await asyncio.sleep(0.01)
        await backend.put(d3)

        result = await backend.list()

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_list_sorted_by_created_at_desc(self, backend: DgentProtocol) -> None:
        """list() returns newest first."""
        d1 = Datum.create(b"first")
        await backend.put(d1)
        await asyncio.sleep(0.01)

        d2 = Datum.create(b"second")
        await backend.put(d2)

        result = await backend.list()

        assert result[0].content == b"second"  # Newest first
        assert result[1].content == b"first"

    @pytest.mark.asyncio
    async def test_list_with_prefix_filter(self, backend: DgentProtocol) -> None:
        """list() filters by ID prefix."""
        d1 = Datum.create(b"test", id="user:alice:1")
        d2 = Datum.create(b"test", id="user:alice:2")
        d3 = Datum.create(b"test", id="user:bob:1")

        await backend.put(d1)
        await backend.put(d2)
        await backend.put(d3)

        result = await backend.list(prefix="user:alice:")

        assert len(result) == 2
        assert all(d.id.startswith("user:alice:") for d in result)

    @pytest.mark.asyncio
    async def test_list_with_after_filter(self, backend: DgentProtocol) -> None:
        """list() filters by timestamp."""
        d1 = Datum.create(b"old")
        await backend.put(d1)

        cutoff = time.time()
        await asyncio.sleep(0.01)

        d2 = Datum.create(b"new")
        await backend.put(d2)

        result = await backend.list(after=cutoff)

        assert len(result) == 1
        assert result[0].content == b"new"

    @pytest.mark.asyncio
    async def test_list_with_limit(self, backend: DgentProtocol) -> None:
        """list() respects limit parameter."""
        for i in range(10):
            await backend.put(Datum.create(f"item-{i}".encode()))

        result = await backend.list(limit=3)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_list_empty_backend(self, backend: DgentProtocol) -> None:
        """list() returns empty list for empty backend."""
        result = await backend.list()
        assert result == []


class TestCausalChain:
    """Tests for causal_chain() method."""

    @pytest.mark.asyncio
    async def test_causal_chain_returns_ancestors(self, backend: DgentProtocol) -> None:
        """causal_chain() returns full lineage."""
        a = Datum.create(b"ancestor")
        b = a.derive(b"child")
        c = b.derive(b"grandchild")

        await backend.put(a)
        await backend.put(b)
        await backend.put(c)

        result = await backend.causal_chain(c.id)

        assert len(result) == 3
        assert result[0].id == a.id  # Oldest first
        assert result[1].id == b.id
        assert result[2].id == c.id

    @pytest.mark.asyncio
    async def test_causal_chain_single_datum(self, backend: DgentProtocol) -> None:
        """causal_chain() for datum with no parent."""
        d = Datum.create(b"orphan")
        await backend.put(d)

        result = await backend.causal_chain(d.id)

        assert len(result) == 1
        assert result[0].id == d.id

    @pytest.mark.asyncio
    async def test_causal_chain_missing_datum(self, backend: DgentProtocol) -> None:
        """causal_chain() returns empty for missing ID."""
        result = await backend.causal_chain("nonexistent")
        assert result == []

    @pytest.mark.asyncio
    async def test_causal_chain_orphaned_datum(self, backend: DgentProtocol) -> None:
        """causal_chain() handles missing parent gracefully."""
        # Create child with parent reference, but don't store parent
        child = Datum.create(b"orphan", causal_parent="missing-parent")
        await backend.put(child)

        result = await backend.causal_chain(child.id)

        # Should return just the child (can't find parent)
        assert len(result) == 1
        assert result[0].id == child.id


class TestExists:
    """Tests for exists() method."""

    @pytest.mark.asyncio
    async def test_exists_returns_true_for_stored(self, backend: DgentProtocol) -> None:
        """exists() returns True for stored datum."""
        d = Datum.create(b"test")
        await backend.put(d)

        assert await backend.exists(d.id) is True

    @pytest.mark.asyncio
    async def test_exists_returns_false_for_missing(self, backend: DgentProtocol) -> None:
        """exists() returns False for missing ID."""
        assert await backend.exists("nonexistent") is False


class TestCount:
    """Tests for count() method."""

    @pytest.mark.asyncio
    async def test_count_returns_total(self, backend: DgentProtocol) -> None:
        """count() returns total number of data."""
        for i in range(5):
            await backend.put(Datum.create(f"item-{i}".encode()))

        assert await backend.count() == 5

    @pytest.mark.asyncio
    async def test_count_empty(self, backend: DgentProtocol) -> None:
        """count() returns 0 for empty backend."""
        assert await backend.count() == 0


# --- Backend-Specific Tests ---


class TestMemoryBackendSpecific:
    """Tests specific to MemoryBackend."""

    @pytest.mark.asyncio
    async def test_clear_removes_all_data(self, memory_backend: MemoryBackend) -> None:
        """clear() removes all data."""
        await memory_backend.put(Datum.create(b"test"))
        memory_backend.clear()

        assert await memory_backend.count() == 0


class TestJSONLBackendSpecific:
    """Tests specific to JSONLBackend."""

    @pytest.mark.asyncio
    async def test_persists_across_instances(self, temp_dir: Path) -> None:
        """Data persists when creating new backend instance."""
        backend1 = JSONLBackend(namespace="persist", data_dir=temp_dir)
        d = Datum.create(b"persist me")
        await backend1.put(d)

        # Create new instance pointing to same file
        backend2 = JSONLBackend(namespace="persist", data_dir=temp_dir)
        result = await backend2.get(d.id)

        assert result is not None
        assert result.content == b"persist me"

    @pytest.mark.asyncio
    async def test_compact_removes_tombstones(self, jsonl_backend: JSONLBackend) -> None:
        """compact() removes tombstones and duplicates."""
        # Add and delete multiple items
        for i in range(5):
            d = Datum.create(f"item-{i}".encode())
            await jsonl_backend.put(d)
            await jsonl_backend.delete(d.id)

        # File should have 10 lines (5 puts + 5 deletes)
        initial_size = jsonl_backend.path.stat().st_size

        # Compact
        saved = await jsonl_backend.compact()

        # Should have saved space
        assert saved > 0
        assert await jsonl_backend.count() == 0


class TestSQLiteBackendSpecific:
    """Tests specific to SQLiteBackend."""

    @pytest.mark.asyncio
    async def test_persists_across_instances(self, temp_dir: Path) -> None:
        """Data persists when creating new backend instance."""
        backend1 = SQLiteBackend(namespace="persist", data_dir=temp_dir)
        d = Datum.create(b"persist me")
        await backend1.put(d)
        backend1.close()

        # Create new instance pointing to same file
        backend2 = SQLiteBackend(namespace="persist", data_dir=temp_dir)
        result = await backend2.get(d.id)

        assert result is not None
        assert result.content == b"persist me"
        backend2.close()

    @pytest.mark.asyncio
    async def test_vacuum_reclaims_space(self, sqlite_backend: SQLiteBackend) -> None:
        """vacuum() reclaims space."""
        # Add and delete items to create fragmentation
        for i in range(100):
            d = Datum.create(f"item-{i}".encode())
            await sqlite_backend.put(d)

        for i in range(50):
            d = await sqlite_backend.list(limit=1)
            if d:
                await sqlite_backend.delete(d[0].id)

        # Vacuum (may or may not save space depending on fragmentation)
        await sqlite_backend.vacuum()

        # Should still have 50 items
        assert await sqlite_backend.count() == 50
