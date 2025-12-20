"""
Tests for SQLite providers.

Tests the concrete implementations of repository interfaces.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from ..interfaces import TelemetryEvent
from ..providers.sqlite import (
    FilesystemBlobStore,
    NumpyVectorStore,
    SQLiteRelationalStore,
    SQLiteTelemetryStore,
)


class TestSQLiteRelationalStore:
    """Tests for SQLite relational store."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Any:
        """Create a temporary database path."""
        return tmp_path / "test.db"

    @pytest.mark.asyncio
    async def test_create_and_connect(self, temp_db: Any) -> None:
        """Should create database on first use."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("SELECT 1")
        assert temp_db.exists()
        await store.close()

    @pytest.mark.asyncio
    async def test_execute_create_table(self, temp_db: Any) -> None:
        """Should execute DDL statements."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("""
            CREATE TABLE test (id TEXT PRIMARY KEY, value TEXT)
        """)
        # Should not raise
        await store.close()

    @pytest.mark.asyncio
    async def test_execute_insert_with_params(self, temp_db: Any) -> None:
        """Should handle named parameters correctly."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT, value INTEGER)")

        rows = await store.execute(
            "INSERT INTO test (id, value) VALUES (:id, :value)",
            {"id": "a", "value": 42},
        )
        assert rows == 1

        await store.close()

    @pytest.mark.asyncio
    async def test_fetch_one(self, temp_db: Any) -> None:
        """Should fetch single row as dict."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT, value INTEGER)")
        await store.execute(
            "INSERT INTO test VALUES (:id, :value)",
            {"id": "a", "value": 42},
        )

        row = await store.fetch_one("SELECT * FROM test WHERE id = :id", {"id": "a"})
        assert row is not None
        assert row["id"] == "a"
        assert row["value"] == 42

        await store.close()

    @pytest.mark.asyncio
    async def test_fetch_one_not_found(self, temp_db: Any) -> None:
        """Should return None when row not found."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT)")

        row = await store.fetch_one("SELECT * FROM test WHERE id = :id", {"id": "nope"})
        assert row is None

        await store.close()

    @pytest.mark.asyncio
    async def test_fetch_all(self, temp_db: Any) -> None:
        """Should fetch all rows as list of dicts."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT, value INTEGER)")
        await store.execute("INSERT INTO test VALUES ('a', 1)")
        await store.execute("INSERT INTO test VALUES ('b', 2)")
        await store.execute("INSERT INTO test VALUES ('c', 3)")

        rows = await store.fetch_all("SELECT * FROM test ORDER BY id")
        assert len(rows) == 3
        assert rows[0]["id"] == "a"
        assert rows[2]["id"] == "c"

        await store.close()

    @pytest.mark.asyncio
    async def test_executemany(self, temp_db: Any) -> None:
        """Should batch insert multiple rows."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT, value INTEGER)")

        params = [
            {"id": "a", "value": 1},
            {"id": "b", "value": 2},
            {"id": "c", "value": 3},
        ]
        count = await store.executemany(
            "INSERT INTO test (id, value) VALUES (:id, :value)",
            params,
        )
        assert count == 3

        rows = await store.fetch_all("SELECT * FROM test")
        assert len(rows) == 3

        await store.close()

    @pytest.mark.asyncio
    async def test_transaction_commit(self, temp_db: Any) -> None:
        """Should commit transaction on success."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT)")

        async with store.transaction() as tx:
            await tx.execute("INSERT INTO test VALUES (:id)", {"id": "a"})
            await tx.execute("INSERT INTO test VALUES (:id)", {"id": "b"})

        rows = await store.fetch_all("SELECT * FROM test")
        assert len(rows) == 2

        await store.close()

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, temp_db: Any) -> None:
        """Should rollback transaction on error."""
        store = SQLiteRelationalStore(temp_db)
        await store.execute("CREATE TABLE test (id TEXT PRIMARY KEY)")
        await store.execute("INSERT INTO test VALUES ('existing')")

        with pytest.raises(Exception):
            async with store.transaction() as tx:
                await tx.execute("INSERT INTO test VALUES (:id)", {"id": "new"})
                # This should cause constraint violation
                await tx.execute("INSERT INTO test VALUES (:id)", {"id": "existing"})

        # "new" should have been rolled back
        rows = await store.fetch_all("SELECT * FROM test")
        assert len(rows) == 1
        assert rows[0]["id"] == "existing"

        await store.close()

    @pytest.mark.asyncio
    async def test_wal_mode_enabled(self, temp_db: Any) -> None:
        """Should use WAL mode by default."""
        store = SQLiteRelationalStore(temp_db, wal_mode=True)
        await store.execute("SELECT 1")

        row = await store.fetch_one("PRAGMA journal_mode")
        assert row is not None
        assert row["journal_mode"] == "wal"

        await store.close()


class TestNumpyVectorStore:
    """Tests for numpy vector store."""

    @pytest.fixture
    def temp_storage(self, tmp_path: Path) -> Any:
        """Create temporary storage path."""
        return tmp_path / "vectors.json"

    @pytest.mark.asyncio
    async def test_upsert_and_count(self, temp_storage: Any) -> None:
        """Should store vectors and count them."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {"type": "test"})
        await store.upsert("b", [0.0, 1.0, 0.0, 0.0], {"type": "test"})

        count = await store.count()
        assert count == 2

        await store.close()

    @pytest.mark.asyncio
    async def test_upsert_overwrites(self, temp_storage: Any) -> None:
        """Should overwrite existing vector on upsert."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {"v": 1})
        await store.upsert("a", [0.0, 1.0, 0.0, 0.0], {"v": 2})

        count = await store.count()
        assert count == 1  # Still just one entry

        await store.close()

    @pytest.mark.asyncio
    async def test_search_cosine_similarity(self, temp_storage: Any) -> None:
        """Should find similar vectors using cosine similarity."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        # Insert orthogonal vectors
        await store.upsert("north", [1.0, 0.0, 0.0, 0.0], {})
        await store.upsert("east", [0.0, 1.0, 0.0, 0.0], {})
        await store.upsert("south", [-1.0, 0.0, 0.0, 0.0], {})

        # Search for north-ish vector
        results = await store.search([0.9, 0.1, 0.0, 0.0])
        assert len(results) == 3
        # First result should be "north" (closest)
        assert results[0].id == "north"
        assert results[0].distance < 0.1  # Very close

        await store.close()

    @pytest.mark.asyncio
    async def test_search_with_filter(self, temp_storage: Any) -> None:
        """Should filter search results by metadata."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {"type": "insight"})
        await store.upsert("b", [1.0, 0.1, 0.0, 0.0], {"type": "question"})
        await store.upsert("c", [1.0, 0.2, 0.0, 0.0], {"type": "insight"})

        results = await store.search(
            [1.0, 0.0, 0.0, 0.0],
            filter={"type": "insight"},
        )
        assert len(results) == 2
        assert all(r.id in ["a", "c"] for r in results)

        await store.close()

    @pytest.mark.asyncio
    async def test_search_limit(self, temp_storage: Any) -> None:
        """Should respect limit parameter."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        for i in range(10):
            await store.upsert(f"v{i}", [1.0, float(i) * 0.01, 0.0, 0.0], {})

        results = await store.search([1.0, 0.0, 0.0, 0.0], limit=3)
        assert len(results) == 3

        await store.close()

    @pytest.mark.asyncio
    async def test_delete(self, temp_storage: Any) -> None:
        """Should delete vectors by ID."""
        store = NumpyVectorStore(temp_storage, dimensions=4)
        await store.initialize()

        await store.upsert("a", [1.0, 0.0, 0.0, 0.0], {})
        assert await store.count() == 1

        deleted = await store.delete("a")
        assert deleted is True
        assert await store.count() == 0

        deleted_again = await store.delete("a")
        assert deleted_again is False

        await store.close()

    @pytest.mark.asyncio
    async def test_persistence(self, temp_storage: Any) -> None:
        """Should persist vectors to disk."""
        # Create and populate store
        store1 = NumpyVectorStore(temp_storage, dimensions=4)
        await store1.initialize()
        await store1.upsert("a", [1.0, 0.0, 0.0, 0.0], {"key": "value"})
        await store1.close()

        # Verify file exists
        assert temp_storage.exists()

        # Reload in new store
        store2 = NumpyVectorStore(temp_storage, dimensions=4)
        await store2.initialize()
        assert await store2.count() == 1

        results = await store2.search([1.0, 0.0, 0.0, 0.0])
        assert results[0].id == "a"
        assert results[0].metadata == {"key": "value"}

        await store2.close()

    @pytest.mark.asyncio
    async def test_dimensions_property(self, temp_storage: Any) -> None:
        """Should expose dimensions property."""
        store = NumpyVectorStore(temp_storage, dimensions=128)
        assert store.dimensions == 128
        await store.close()


class TestFilesystemBlobStore:
    """Tests for filesystem blob store."""

    @pytest.fixture
    def temp_blobs(self, tmp_path: Path) -> Any:
        """Create temporary blob directory."""
        return tmp_path / "blobs"

    @pytest.mark.asyncio
    async def test_put_and_get(self, temp_blobs: Any) -> None:
        """Should store and retrieve blobs."""
        store = FilesystemBlobStore(temp_blobs)

        path = await store.put("test.txt", b"hello world")
        assert "test.txt" in path

        data = await store.get("test.txt")
        assert data == b"hello world"

        await store.close()

    @pytest.mark.asyncio
    async def test_put_creates_directories(self, temp_blobs: Any) -> None:
        """Should create parent directories."""
        store = FilesystemBlobStore(temp_blobs)

        await store.put("deep/nested/path/file.bin", b"data")
        data = await store.get("deep/nested/path/file.bin")
        assert data == b"data"

        await store.close()

    @pytest.mark.asyncio
    async def test_get_not_found(self, temp_blobs: Any) -> None:
        """Should return None for missing keys."""
        store = FilesystemBlobStore(temp_blobs)

        data = await store.get("nonexistent.txt")
        assert data is None

        await store.close()

    @pytest.mark.asyncio
    async def test_delete(self, temp_blobs: Any) -> None:
        """Should delete blobs."""
        store = FilesystemBlobStore(temp_blobs)

        await store.put("test.txt", b"data")
        assert await store.exists("test.txt") is True

        deleted = await store.delete("test.txt")
        assert deleted is True
        assert await store.exists("test.txt") is False

        deleted_again = await store.delete("test.txt")
        assert deleted_again is False

        await store.close()

    @pytest.mark.asyncio
    async def test_list_with_prefix(self, temp_blobs: Any) -> None:
        """Should list keys with prefix."""
        store = FilesystemBlobStore(temp_blobs)

        await store.put("images/a.png", b"1")
        await store.put("images/b.png", b"2")
        await store.put("docs/readme.md", b"3")

        images = await store.list("images")
        assert len(images) == 2
        assert all("images" in k for k in images)

        all_keys = await store.list()
        assert len(all_keys) == 3

        await store.close()

    @pytest.mark.asyncio
    async def test_exists(self, temp_blobs: Any) -> None:
        """Should check existence."""
        store = FilesystemBlobStore(temp_blobs)

        assert await store.exists("nope") is False
        await store.put("yes", b"data")
        assert await store.exists("yes") is True

        await store.close()

    @pytest.mark.asyncio
    async def test_binary_data(self, temp_blobs: Any) -> None:
        """Should handle binary data correctly."""
        store = FilesystemBlobStore(temp_blobs)

        # Binary data with null bytes
        binary = bytes(range(256))
        await store.put("binary.bin", binary)

        retrieved = await store.get("binary.bin")
        assert retrieved == binary

        await store.close()


class TestSQLiteTelemetryStore:
    """Tests for SQLite telemetry store."""

    @pytest.fixture
    def temp_db(self, tmp_path: Path) -> Any:
        """Create temporary database path."""
        return tmp_path / "telemetry.db"

    @pytest.mark.asyncio
    async def test_append_and_query(self, temp_db: Any) -> None:
        """Should append events and query them."""
        store = SQLiteTelemetryStore(temp_db)

        events = [
            TelemetryEvent("test.event", "2025-12-10T12:00:00", {"n": 1}),
            TelemetryEvent("test.event", "2025-12-10T12:01:00", {"n": 2}),
        ]
        count = await store.append(events)
        assert count == 2

        results = await store.query()
        assert len(results) == 2
        # Newest first
        assert results[0].data["n"] == 2

        await store.close()

    @pytest.mark.asyncio
    async def test_query_by_type(self, temp_db: Any) -> None:
        """Should filter by event type."""
        store = SQLiteTelemetryStore(temp_db)

        await store.append(
            [
                TelemetryEvent("type_a", "2025-12-10T12:00:00", {}),
                TelemetryEvent("type_b", "2025-12-10T12:01:00", {}),
                TelemetryEvent("type_a", "2025-12-10T12:02:00", {}),
            ]
        )

        results = await store.query(event_type="type_a")
        assert len(results) == 2
        assert all(e.event_type == "type_a" for e in results)

        await store.close()

    @pytest.mark.asyncio
    async def test_query_time_range(self, temp_db: Any) -> None:
        """Should filter by time range."""
        store = SQLiteTelemetryStore(temp_db)

        await store.append(
            [
                TelemetryEvent("test", "2025-12-10T10:00:00", {"h": 10}),
                TelemetryEvent("test", "2025-12-10T12:00:00", {"h": 12}),
                TelemetryEvent("test", "2025-12-10T14:00:00", {"h": 14}),
            ]
        )

        results = await store.query(
            since="2025-12-10T11:00:00",
            until="2025-12-10T13:00:00",
        )
        assert len(results) == 1
        assert results[0].data["h"] == 12

        await store.close()

    @pytest.mark.asyncio
    async def test_query_by_instance(self, temp_db: Any) -> None:
        """Should filter by instance ID."""
        store = SQLiteTelemetryStore(temp_db)

        await store.append(
            [
                TelemetryEvent("test", "2025-12-10T12:00:00", {}, instance_id="inst-a"),
                TelemetryEvent("test", "2025-12-10T12:01:00", {}, instance_id="inst-b"),
            ]
        )

        results = await store.query(instance_id="inst-a")
        assert len(results) == 1
        assert results[0].instance_id == "inst-a"

        await store.close()

    @pytest.mark.asyncio
    async def test_query_limit(self, temp_db: Any) -> None:
        """Should respect limit."""
        store = SQLiteTelemetryStore(temp_db)

        events = [TelemetryEvent("test", f"2025-12-10T12:{i:02d}:00", {"n": i}) for i in range(10)]
        await store.append(events)

        results = await store.query(limit=3)
        assert len(results) == 3

        await store.close()

    @pytest.mark.asyncio
    async def test_prune(self, temp_db: Any) -> None:
        """Should delete old events."""
        store = SQLiteTelemetryStore(temp_db)

        # Events from different times
        old_time = (datetime.now() - timedelta(days=10)).isoformat()
        recent_time = datetime.now().isoformat()

        await store.append(
            [
                TelemetryEvent("test", old_time, {"age": "old"}),
                TelemetryEvent("test", recent_time, {"age": "new"}),
            ]
        )

        deleted = await store.prune(older_than_days=5)
        assert deleted == 1

        results = await store.query()
        assert len(results) == 1
        assert results[0].data["age"] == "new"

        await store.close()

    @pytest.mark.asyncio
    async def test_count(self, temp_db: Any) -> None:
        """Should count events."""
        store = SQLiteTelemetryStore(temp_db)

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

        await store.close()

    @pytest.mark.asyncio
    async def test_event_with_complex_data(self, temp_db: Any) -> None:
        """Should handle complex JSON data."""
        store = SQLiteTelemetryStore(temp_db)

        complex_data = {
            "nested": {"deep": {"value": 42}},
            "list": [1, 2, 3],
            "unicode": "\u4e2d\u6587",
        }

        await store.append(
            [
                TelemetryEvent("test", "2025-12-10T12:00:00", complex_data),
            ]
        )

        results = await store.query()
        assert results[0].data == complex_data

        await store.close()
