"""
Tests for PostgreSQL providers.

Tests the Postgres implementations of repository interfaces.
Requires KGENTS_POSTGRES_URL to be set for integration tests.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from ..providers.postgres import (
    ASYNCPG_AVAILABLE,
    PostgresRelationalStore,
    create_postgres_store,
    get_postgres_url,
    is_postgres_available,
)
from ..providers.router import (
    StorageBackend,
    check_backend_status,
    create_relational_store,
    get_current_backend,
)

# Skip all tests if asyncpg is not available
pytestmark = pytest.mark.skipif(
    not ASYNCPG_AVAILABLE,
    reason="asyncpg not installed",
)


class TestPostgresAvailability:
    """Tests for Postgres availability checks."""

    def test_get_postgres_url_not_set(self, monkeypatch: Any) -> None:
        """Should return None if neither KGENTS_DATABASE_URL nor KGENTS_POSTGRES_URL are set."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        assert get_postgres_url() is None

    def test_get_postgres_url_set(self, monkeypatch: Any) -> None:
        """Should return URL if KGENTS_POSTGRES_URL is set."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)  # Clear canonical first
        monkeypatch.setenv("KGENTS_POSTGRES_URL", "postgresql://localhost/test")
        assert get_postgres_url() == "postgresql://localhost/test"

    def test_is_postgres_available_no_url(self, monkeypatch: Any) -> None:
        """Should return False if URL not set."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        assert is_postgres_available() is False

    @pytest.mark.skipif(
        not ASYNCPG_AVAILABLE,
        reason="asyncpg not installed",
    )
    def test_is_postgres_available_with_url(self, monkeypatch: Any) -> None:
        """Should return True if URL is set and asyncpg available."""
        monkeypatch.setenv("KGENTS_POSTGRES_URL", "postgresql://localhost/test")
        # Just checks that asyncpg is installed and URL is set
        assert is_postgres_available() is True


class TestPostgresRelationalStoreUnit:
    """Unit tests for PostgresRelationalStore (no database required)."""

    def test_param_conversion_simple(self) -> None:
        """Should convert :name to $N."""
        store = PostgresRelationalStore("postgresql://localhost/test")
        query, params = store._convert_params(
            "SELECT * FROM foo WHERE id = :id AND name = :name",
            {"id": 123, "name": "test"},
        )
        assert query == "SELECT * FROM foo WHERE id = $1 AND name = $2"
        assert params == [123, "test"]

    def test_param_conversion_repeated(self) -> None:
        """Should reuse $N for repeated params."""
        store = PostgresRelationalStore("postgresql://localhost/test")
        query, params = store._convert_params(
            "SELECT * FROM foo WHERE id = :id OR other_id = :id",
            {"id": 123},
        )
        assert query == "SELECT * FROM foo WHERE id = $1 OR other_id = $1"
        assert params == [123]

    def test_param_conversion_preserves_typecast(self) -> None:
        """Should preserve ::type casts (not convert them)."""
        store = PostgresRelationalStore("postgresql://localhost/test")
        query, params = store._convert_params(
            "INSERT INTO foo (data) VALUES (:data::jsonb)",
            {"data": '{"key": "value"}'},
        )
        assert query == "INSERT INTO foo (data) VALUES ($1::jsonb)"
        assert params == ['{"key": "value"}']

    def test_param_conversion_none_params(self) -> None:
        """Should handle None params."""
        store = PostgresRelationalStore("postgresql://localhost/test")
        query, params = store._convert_params("SELECT 1", None)
        assert query == "SELECT 1"
        assert params == []


class TestStorageRouter:
    """Tests for the storage router."""

    @pytest.mark.asyncio
    async def test_create_sqlite_store(self, tmp_path: Path) -> None:
        """Should create SQLite store when explicitly requested."""
        store = await create_relational_store(
            backend="sqlite",
            sqlite_path=tmp_path / "test.db",
        )
        assert store is not None
        # Verify it's SQLite by checking the type
        from ..providers.sqlite import SQLiteRelationalStore

        assert isinstance(store, SQLiteRelationalStore)
        await store.close()

    @pytest.mark.asyncio
    async def test_create_auto_fallback_to_sqlite(self, tmp_path: Path, monkeypatch: Any) -> None:
        """Should fall back to SQLite when Postgres unavailable."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        store = await create_relational_store(
            backend="auto",
            sqlite_path=tmp_path / "test.db",
        )
        assert store is not None
        from ..providers.sqlite import SQLiteRelationalStore

        assert isinstance(store, SQLiteRelationalStore)
        await store.close()

    @pytest.mark.asyncio
    async def test_check_sqlite_backend_status(self) -> None:
        """SQLite should always be available."""
        status = await check_backend_status(StorageBackend.SQLITE)
        assert status.available is True

    @pytest.mark.asyncio
    async def test_check_postgres_backend_status_no_url(self, monkeypatch: Any) -> None:
        """Postgres should be unavailable without URL."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        status = await check_backend_status(StorageBackend.POSTGRES)
        assert status.available is False
        assert "not set" in status.reason

    @pytest.mark.asyncio
    async def test_get_current_backend_no_postgres(self, monkeypatch: Any) -> None:
        """Should return SQLite when Postgres unavailable."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        backend = await get_current_backend()
        assert backend == StorageBackend.SQLITE

    @pytest.mark.asyncio
    async def test_create_postgres_raises_without_url(self, monkeypatch: Any) -> None:
        """Should raise when postgres explicitly requested but unavailable."""
        monkeypatch.delenv("KGENTS_DATABASE_URL", raising=False)
        monkeypatch.delenv("KGENTS_POSTGRES_URL", raising=False)
        with pytest.raises(RuntimeError, match="not set"):
            await create_relational_store(backend="postgres")


# Integration tests that require actual Postgres connection
@pytest.mark.skipif(
    os.environ.get("KGENTS_POSTGRES_URL") is None,
    reason="KGENTS_POSTGRES_URL not set",
)
class TestPostgresRelationalStoreIntegration:
    """Integration tests for PostgresRelationalStore (requires real Postgres)."""

    @pytest.fixture
    async def store(self) -> Any:
        """Create a store connected to real Postgres."""
        url = os.environ.get("KGENTS_POSTGRES_URL")
        assert url is not None
        store = PostgresRelationalStore(url)

        # Create test table
        await store.execute("""
            CREATE TABLE IF NOT EXISTS test_captures (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                captured_at TEXT NOT NULL
            )
        """)

        yield store

        # Cleanup
        await store.execute("DROP TABLE IF EXISTS test_captures")
        await store.close()

    @pytest.mark.asyncio
    async def test_execute_create_table(self, store: Any) -> None:
        """Should execute DDL statements."""
        # Table created in fixture, just verify we can query it
        result = await store.fetch_all("SELECT 1")
        assert result is not None

    @pytest.mark.asyncio
    async def test_execute_insert_with_params(self, store: Any) -> None:
        """Should handle named parameters correctly."""
        await store.execute(
            """
            INSERT INTO test_captures (id, content, captured_at)
            VALUES (:id, :content, :captured_at)
            """,
            {"id": "test-1", "content": "Hello World", "captured_at": "2025-12-16"},
        )

        row = await store.fetch_one(
            "SELECT * FROM test_captures WHERE id = :id",
            {"id": "test-1"},
        )
        assert row is not None
        assert row["content"] == "Hello World"

    @pytest.mark.asyncio
    async def test_fetch_one_not_found(self, store: Any) -> None:
        """Should return None when row not found."""
        row = await store.fetch_one(
            "SELECT * FROM test_captures WHERE id = :id",
            {"id": "nonexistent"},
        )
        assert row is None

    @pytest.mark.asyncio
    async def test_fetch_all(self, store: Any) -> None:
        """Should fetch all rows as list of dicts."""
        # Insert test data
        for i in range(3):
            await store.execute(
                """
                INSERT INTO test_captures (id, content, captured_at)
                VALUES (:id, :content, :captured_at)
                """,
                {
                    "id": f"test-{i}",
                    "content": f"Content {i}",
                    "captured_at": "2025-12-16",
                },
            )

        rows = await store.fetch_all("SELECT * FROM test_captures ORDER BY id")
        assert len(rows) == 3
        assert rows[0]["content"] == "Content 0"

    @pytest.mark.asyncio
    async def test_executemany(self, store: Any) -> None:
        """Should batch insert multiple rows."""
        params_list = [
            {"id": f"batch-{i}", "content": f"Batch {i}", "captured_at": "2025-12-16"}
            for i in range(5)
        ]

        count = await store.executemany(
            """
            INSERT INTO test_captures (id, content, captured_at)
            VALUES (:id, :content, :captured_at)
            """,
            params_list,
        )
        assert count == 5

        rows = await store.fetch_all("SELECT * FROM test_captures WHERE id LIKE 'batch-%'")
        assert len(rows) == 5

    @pytest.mark.asyncio
    async def test_transaction_commit(self, store: Any) -> None:
        """Should commit transaction on success."""
        async with store.transaction() as tx:
            await tx.execute(
                """
                INSERT INTO test_captures (id, content, captured_at)
                VALUES (:id, :content, :captured_at)
                """,
                {"id": "tx-1", "content": "Committed", "captured_at": "2025-12-16"},
            )

        # Should be visible after commit
        row = await store.fetch_one(
            "SELECT * FROM test_captures WHERE id = :id",
            {"id": "tx-1"},
        )
        assert row is not None
        assert row["content"] == "Committed"

    @pytest.mark.asyncio
    async def test_transaction_rollback(self, store: Any) -> None:
        """Should rollback transaction on exception."""
        try:
            async with store.transaction() as tx:
                await tx.execute(
                    """
                    INSERT INTO test_captures (id, content, captured_at)
                    VALUES (:id, :content, :captured_at)
                    """,
                    {
                        "id": "tx-rollback",
                        "content": "Should rollback",
                        "captured_at": "2025-12-16",
                    },
                )
                raise ValueError("Intentional error")
        except ValueError:
            pass

        # Should NOT be visible after rollback
        row = await store.fetch_one(
            "SELECT * FROM test_captures WHERE id = :id",
            {"id": "tx-rollback"},
        )
        assert row is None

    @pytest.mark.asyncio
    async def test_health_check(self, store: Any) -> None:
        """Should return health status."""
        health = await store.health_check()
        assert health["connected"] is True
        assert health["pool_size"] >= 0


@pytest.mark.skipif(
    os.environ.get("KGENTS_POSTGRES_URL") is None,
    reason="KGENTS_POSTGRES_URL not set",
)
class TestRouterWithPostgres:
    """Router integration tests with real Postgres."""

    @pytest.mark.asyncio
    async def test_create_auto_uses_postgres(self, tmp_path: Path) -> None:
        """Should auto-select Postgres when available."""
        store = await create_relational_store(
            backend="auto",
            sqlite_path=tmp_path / "test.db",
        )
        # Should be Postgres, not SQLite
        assert isinstance(store, PostgresRelationalStore)
        await store.close()

    @pytest.mark.asyncio
    async def test_get_current_backend_postgres(self) -> None:
        """Should return Postgres when it's available."""
        backend = await get_current_backend()
        assert backend == StorageBackend.POSTGRES
