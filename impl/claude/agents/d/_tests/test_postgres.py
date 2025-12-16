"""
Tests for PostgresBackend.

These tests require a running PostgreSQL instance.
Skip by default; run with: pytest -m postgres

Connection: Set KGENTS_POSTGRES_URL environment variable.
"""

from __future__ import annotations

import asyncio
import os
import pytest
import time

from ..datum import Datum

# Check for asyncpg availability
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False


# Check for Postgres URL
POSTGRES_URL = os.environ.get("KGENTS_POSTGRES_URL")
POSTGRES_AVAILABLE = ASYNCPG_AVAILABLE and POSTGRES_URL is not None


@pytest.fixture
async def postgres_backend():
    """Fresh PostgresBackend for each test."""
    if not POSTGRES_AVAILABLE:
        pytest.skip("PostgreSQL not available (set KGENTS_POSTGRES_URL)")

    from ..backends.postgres import PostgresBackend

    # Use test namespace to avoid polluting real data
    backend = PostgresBackend(
        url=POSTGRES_URL,
        namespace="test",
        min_pool_size=1,
        max_pool_size=2,
    )

    # Clean up before test
    async with backend._connection() as conn:
        await conn.execute("DELETE FROM data")

    yield backend

    # Clean up after test
    async with backend._connection() as conn:
        await conn.execute("DELETE FROM data")

    await backend.close()


# --- Protocol Tests ---


@pytest.mark.postgres
@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
class TestPostgresProtocol:
    """Protocol tests for PostgresBackend."""

    async def test_put_returns_id(self, postgres_backend) -> None:
        """put() returns the datum ID."""
        d = Datum.create(b"test")
        result = await postgres_backend.put(d)
        assert result == d.id

    async def test_put_overwrites_existing(self, postgres_backend) -> None:
        """put() overwrites datum with same ID."""
        d1 = Datum.create(b"v1", id="same-id")
        d2 = Datum.create(b"v2", id="same-id")

        await postgres_backend.put(d1)
        await postgres_backend.put(d2)

        result = await postgres_backend.get("same-id")
        assert result is not None
        assert result.content == b"v2"

    async def test_get_returns_datum(self, postgres_backend) -> None:
        """get() returns stored datum."""
        d = Datum.create(b"test content")
        await postgres_backend.put(d)

        result = await postgres_backend.get(d.id)

        assert result is not None
        assert result.id == d.id
        assert result.content == d.content

    async def test_get_returns_none_for_missing(self, postgres_backend) -> None:
        """get() returns None for non-existent ID."""
        result = await postgres_backend.get("nonexistent-id")
        assert result is None

    async def test_get_preserves_metadata(self, postgres_backend) -> None:
        """get() preserves metadata."""
        d = Datum.create(b"test", metadata={"key": "value", "num": "42"})
        await postgres_backend.put(d)

        result = await postgres_backend.get(d.id)

        assert result is not None
        assert result.metadata == {"key": "value", "num": "42"}

    async def test_get_preserves_causal_parent(self, postgres_backend) -> None:
        """get() preserves causal_parent when parent exists."""
        parent = Datum.create(b"parent")
        await postgres_backend.put(parent)

        child = parent.derive(b"child")
        await postgres_backend.put(child)

        result = await postgres_backend.get(child.id)

        assert result is not None
        assert result.causal_parent == parent.id

    async def test_delete_returns_true_on_success(self, postgres_backend) -> None:
        """delete() returns True when datum existed."""
        d = Datum.create(b"test")
        await postgres_backend.put(d)

        result = await postgres_backend.delete(d.id)

        assert result is True

    async def test_delete_removes_datum(self, postgres_backend) -> None:
        """delete() makes datum unavailable."""
        d = Datum.create(b"test")
        await postgres_backend.put(d)
        await postgres_backend.delete(d.id)

        result = await postgres_backend.get(d.id)
        assert result is None

    async def test_delete_returns_false_for_missing(self, postgres_backend) -> None:
        """delete() returns False for non-existent ID."""
        result = await postgres_backend.delete("nonexistent-id")
        assert result is False

    async def test_list_returns_all_data(self, postgres_backend) -> None:
        """list() returns all stored data."""
        d1 = Datum.create(b"one")
        d2 = Datum.create(b"two")
        d3 = Datum.create(b"three")

        await postgres_backend.put(d1)
        await asyncio.sleep(0.01)
        await postgres_backend.put(d2)
        await asyncio.sleep(0.01)
        await postgres_backend.put(d3)

        result = await postgres_backend.list()

        assert len(result) == 3

    async def test_list_sorted_by_created_at_desc(self, postgres_backend) -> None:
        """list() returns newest first."""
        d1 = Datum.create(b"first")
        await postgres_backend.put(d1)
        await asyncio.sleep(0.01)

        d2 = Datum.create(b"second")
        await postgres_backend.put(d2)

        result = await postgres_backend.list()

        assert result[0].content == b"second"
        assert result[1].content == b"first"

    async def test_list_with_prefix_filter(self, postgres_backend) -> None:
        """list() filters by ID prefix."""
        d1 = Datum.create(b"test", id="user:alice:1")
        d2 = Datum.create(b"test", id="user:alice:2")
        d3 = Datum.create(b"test", id="user:bob:1")

        await postgres_backend.put(d1)
        await postgres_backend.put(d2)
        await postgres_backend.put(d3)

        result = await postgres_backend.list(prefix="user:alice:")

        assert len(result) == 2
        assert all(d.id.startswith("user:alice:") for d in result)

    async def test_list_with_after_filter(self, postgres_backend) -> None:
        """list() filters by timestamp."""
        d1 = Datum.create(b"old")
        await postgres_backend.put(d1)

        cutoff = time.time()
        await asyncio.sleep(0.01)

        d2 = Datum.create(b"new")
        await postgres_backend.put(d2)

        result = await postgres_backend.list(after=cutoff)

        assert len(result) == 1
        assert result[0].content == b"new"

    async def test_list_with_limit(self, postgres_backend) -> None:
        """list() respects limit parameter."""
        for i in range(10):
            await postgres_backend.put(Datum.create(f"item-{i}".encode()))

        result = await postgres_backend.list(limit=3)

        assert len(result) == 3

    async def test_list_empty_backend(self, postgres_backend) -> None:
        """list() returns empty list for empty backend."""
        result = await postgres_backend.list()
        assert result == []

    async def test_causal_chain_returns_ancestors(self, postgres_backend) -> None:
        """causal_chain() returns full lineage."""
        a = Datum.create(b"ancestor")
        await postgres_backend.put(a)

        b = a.derive(b"child")
        await postgres_backend.put(b)

        c = b.derive(b"grandchild")
        await postgres_backend.put(c)

        result = await postgres_backend.causal_chain(c.id)

        assert len(result) == 3
        assert result[0].id == a.id
        assert result[1].id == b.id
        assert result[2].id == c.id

    async def test_causal_chain_single_datum(self, postgres_backend) -> None:
        """causal_chain() for datum with no parent."""
        d = Datum.create(b"orphan")
        await postgres_backend.put(d)

        result = await postgres_backend.causal_chain(d.id)

        assert len(result) == 1
        assert result[0].id == d.id

    async def test_causal_chain_missing_datum(self, postgres_backend) -> None:
        """causal_chain() returns empty for missing ID."""
        result = await postgres_backend.causal_chain("nonexistent")
        assert result == []

    async def test_exists_returns_true_for_stored(self, postgres_backend) -> None:
        """exists() returns True for stored datum."""
        d = Datum.create(b"test")
        await postgres_backend.put(d)

        assert await postgres_backend.exists(d.id) is True

    async def test_exists_returns_false_for_missing(self, postgres_backend) -> None:
        """exists() returns False for missing ID."""
        assert await postgres_backend.exists("nonexistent") is False

    async def test_count_returns_total(self, postgres_backend) -> None:
        """count() returns total number of data."""
        for i in range(5):
            await postgres_backend.put(Datum.create(f"item-{i}".encode()))

        assert await postgres_backend.count() == 5

    async def test_count_empty(self, postgres_backend) -> None:
        """count() returns 0 for empty backend."""
        assert await postgres_backend.count() == 0


# --- Postgres-Specific Tests ---


@pytest.mark.postgres
@pytest.mark.asyncio
@pytest.mark.skipif(not POSTGRES_AVAILABLE, reason="PostgreSQL not available")
class TestPostgresSpecific:
    """Tests specific to PostgresBackend."""

    async def test_health_check(self, postgres_backend) -> None:
        """health_check() returns stats."""
        # Add some data
        for i in range(3):
            await postgres_backend.put(Datum.create(f"item-{i}".encode()))

        health = await postgres_backend.health_check()

        assert health["connected"] is True
        assert health["count"] == 3
        assert health["pool_size"] > 0

    async def test_connection_pool(self, postgres_backend) -> None:
        """Connection pool handles concurrent requests."""
        # Run multiple concurrent operations
        async def put_item(i: int) -> str:
            d = Datum.create(f"concurrent-{i}".encode())
            return await postgres_backend.put(d)

        tasks = [put_item(i) for i in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert await postgres_backend.count() == 10

    async def test_async_context_manager(self) -> None:
        """Backend works as async context manager."""
        if not POSTGRES_AVAILABLE:
            pytest.skip("PostgreSQL not available")

        from ..backends.postgres import PostgresBackend

        async with PostgresBackend(
            url=POSTGRES_URL,
            namespace="context_test",
        ) as backend:
            d = Datum.create(b"context test")
            await backend.put(d)
            result = await backend.get(d.id)
            assert result is not None

            # Clean up
            async with backend._connection() as conn:
                await conn.execute("DELETE FROM data")


# --- Unit Tests (No Database Required) ---


class TestPostgresBackendUnit:
    """Unit tests that don't require a database."""

    def test_import_error_without_asyncpg(self) -> None:
        """PostgresBackend raises ImportError when asyncpg missing."""
        # This test verifies the error message, not the actual import failure
        # since asyncpg may or may not be installed
        if ASYNCPG_AVAILABLE:
            pytest.skip("asyncpg is installed")

        with pytest.raises(ImportError) as exc_info:
            from ..backends.postgres import PostgresBackend
            PostgresBackend("postgresql://localhost/test")

        assert "asyncpg" in str(exc_info.value)

    def test_repr_hides_password(self) -> None:
        """__repr__ doesn't expose connection URL."""
        if not ASYNCPG_AVAILABLE:
            pytest.skip("asyncpg not available")

        from ..backends.postgres import PostgresBackend

        # Note: This creates the object but doesn't connect
        backend = PostgresBackend.__new__(PostgresBackend)
        backend.url = "postgresql://user:secret@host/db"
        backend.namespace = "test"

        repr_str = repr(backend)

        assert "secret" not in repr_str
        assert "test" in repr_str
