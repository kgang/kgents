"""
Tests for SQLAgent (SQLite and PostgreSQL backends).

Note: SQLite tests run locally, PostgreSQL tests are skipped without a server.
"""

import tempfile
from dataclasses import dataclass
from enum import Enum
from typing import List

import pytest

# Check if aiosqlite is available
try:
    import importlib.util

    AIOSQLITE_AVAILABLE = importlib.util.find_spec("aiosqlite") is not None
except ImportError:
    AIOSQLITE_AVAILABLE = False

# Import agent classes (always available, deps checked at runtime)
from ..sql_agent import (
    SQLAgent,
    SQLiteBackend,
    PostgreSQLBackend,
    create_sqlite_agent,
)
from ..errors import (
    StateNotFoundError,
    StorageError,
)


# Test fixtures


@dataclass
class SimpleState:
    value: int
    name: str


@dataclass
class NestedState:
    simple: SimpleState
    tags: List[str]


class Priority(Enum):
    LOW = "low"
    HIGH = "high"


@dataclass
class EnumState:
    priority: Priority
    count: int


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield f.name
    # Cleanup handled by OS


@pytest.fixture
async def sqlite_agent(temp_db):
    """Create and connect a SQLite agent."""
    if not AIOSQLITE_AVAILABLE:
        pytest.skip("aiosqlite not installed")

    agent = create_sqlite_agent(
        db_path=temp_db,
        table="test_states",
        key="test_key",
        schema=SimpleState,
        max_history=10,
    )
    await agent.connect()
    yield agent
    await agent.close()


# Basic Operations


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteBasicOperations:
    """Tests for basic CRUD operations with SQLite."""

    @pytest.mark.asyncio
    async def test_save_and_load(self, sqlite_agent):
        """State round-trips correctly."""
        state = SimpleState(value=42, name="test")
        await sqlite_agent.save(state)

        loaded = await sqlite_agent.load()
        assert loaded.value == 42
        assert loaded.name == "test"

    @pytest.mark.asyncio
    async def test_load_without_state_raises(self, sqlite_agent):
        """Loading non-existent state raises StateNotFoundError."""
        with pytest.raises(StateNotFoundError):
            await sqlite_agent.load()

    @pytest.mark.asyncio
    async def test_multiple_saves(self, sqlite_agent):
        """Multiple saves create versions, load returns latest."""
        await sqlite_agent.save(SimpleState(value=1, name="v1"))
        await sqlite_agent.save(SimpleState(value=2, name="v2"))
        await sqlite_agent.save(SimpleState(value=3, name="v3"))

        loaded = await sqlite_agent.load()
        assert loaded.value == 3
        assert loaded.name == "v3"

    @pytest.mark.asyncio
    async def test_context_manager(self, temp_db):
        """Agent works as async context manager."""
        agent = create_sqlite_agent(
            db_path=temp_db,
            table="ctx_test",
            key="ctx_key",
            schema=SimpleState,
        )

        async with agent:
            await agent.save(SimpleState(value=100, name="ctx"))
            loaded = await agent.load()
            assert loaded.value == 100


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteHistory:
    """Tests for history functionality."""

    @pytest.mark.asyncio
    async def test_history_returns_previous_states(self, sqlite_agent):
        """History contains previous states, not current."""
        await sqlite_agent.save(SimpleState(value=1, name="first"))
        await sqlite_agent.save(SimpleState(value=2, name="second"))
        await sqlite_agent.save(SimpleState(value=3, name="third"))

        history = await sqlite_agent.history()
        assert len(history) == 2
        assert history[0].value == 2  # Most recent (before current)
        assert history[1].value == 1  # Oldest

    @pytest.mark.asyncio
    async def test_history_with_limit(self, sqlite_agent):
        """History respects limit parameter."""
        for i in range(5):
            await sqlite_agent.save(SimpleState(value=i, name=f"v{i}"))

        history = await sqlite_agent.history(limit=2)
        assert len(history) == 2
        assert history[0].value == 3  # Second most recent
        assert history[1].value == 2

    @pytest.mark.asyncio
    async def test_history_empty_initially(self, sqlite_agent):
        """Empty history for new agent."""
        history = await sqlite_agent.history()
        assert history == []

    @pytest.mark.asyncio
    async def test_max_history_enforced(self, temp_db):
        """Old versions are pruned when max_history exceeded."""
        agent = create_sqlite_agent(
            db_path=temp_db,
            table="prune_test",
            key="prune_key",
            schema=SimpleState,
            max_history=3,
        )
        await agent.connect()

        for i in range(10):
            await agent.save(SimpleState(value=i, name=f"v{i}"))

        history = await agent.history()
        # Should have at most max_history entries (excluding current)
        assert len(history) <= 3

        await agent.close()


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteComplexTypes:
    """Tests for nested dataclasses and enums."""

    @pytest.mark.asyncio
    async def test_nested_dataclass(self, temp_db):
        """Nested dataclasses serialize and deserialize correctly."""
        agent = create_sqlite_agent(
            db_path=temp_db,
            table="nested_test",
            key="nested_key",
            schema=NestedState,
        )
        await agent.connect()

        state = NestedState(
            simple=SimpleState(value=1, name="inner"), tags=["a", "b", "c"]
        )
        await agent.save(state)

        loaded = await agent.load()
        assert loaded.simple.value == 1
        assert loaded.simple.name == "inner"
        assert loaded.tags == ["a", "b", "c"]

        await agent.close()

    @pytest.mark.asyncio
    async def test_enum_serialization(self, temp_db):
        """Enums serialize to values and deserialize back."""
        agent = create_sqlite_agent(
            db_path=temp_db,
            table="enum_test",
            key="enum_key",
            schema=EnumState,
        )
        await agent.connect()

        state = EnumState(priority=Priority.HIGH, count=5)
        await agent.save(state)

        loaded = await agent.load()
        assert loaded.priority == Priority.HIGH
        assert loaded.count == 5

        await agent.close()


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteMultipleKeys:
    """Tests for multiple keys in same table."""

    @pytest.mark.asyncio
    async def test_different_keys_isolated(self, temp_db):
        """Different keys maintain separate state."""
        agent1 = create_sqlite_agent(
            db_path=temp_db,
            table="shared_table",
            key="key_one",
            schema=SimpleState,
        )
        agent2 = create_sqlite_agent(
            db_path=temp_db,
            table="shared_table",
            key="key_two",
            schema=SimpleState,
        )

        await agent1.connect()
        await agent2.connect()

        await agent1.save(SimpleState(value=1, name="one"))
        await agent2.save(SimpleState(value=2, name="two"))

        loaded1 = await agent1.load()
        loaded2 = await agent2.load()

        assert loaded1.value == 1
        assert loaded2.value == 2

        await agent1.close()
        await agent2.close()


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteErrors:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_not_connected_error(self, temp_db):
        """Operations fail if not connected."""
        agent = create_sqlite_agent(
            db_path=temp_db,
            table="test",
            key="key",
            schema=SimpleState,
        )

        with pytest.raises(StorageError, match="Not connected"):
            await agent.load()

    @pytest.mark.asyncio
    async def test_primitive_types(self, temp_db):
        """Agent works with primitive types."""
        agent: SQLAgent[dict] = SQLAgent(
            backend=SQLiteBackend(temp_db),
            table="primitive_test",
            key="dict_key",
            schema=dict,
        )
        await agent.connect()

        await agent.save({"count": 42, "name": "test"})
        loaded = await agent.load()
        assert loaded["count"] == 42

        await agent.close()


class TestPostgreSQLBackend:
    """Tests for PostgreSQL backend (skip if not available)."""

    @pytest.mark.asyncio
    async def test_placeholder_conversion(self):
        """PostgreSQL placeholder conversion works."""
        backend = PostgreSQLBackend("postgresql://localhost/test")

        query = "SELECT * FROM t WHERE a = ? AND b = ? AND c = ?"
        converted = backend._convert_placeholders(query)
        assert converted == "SELECT * FROM t WHERE a = $1 AND b = $2 AND c = $3"

    @pytest.mark.asyncio
    async def test_no_placeholders(self):
        """Queries without placeholders are unchanged."""
        backend = PostgreSQLBackend("postgresql://localhost/test")

        query = "SELECT * FROM t"
        converted = backend._convert_placeholders(query)
        assert converted == query


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLiteBackend:
    """Tests for SQLiteBackend internals."""

    @pytest.mark.asyncio
    async def test_backend_lifecycle(self, temp_db):
        """Backend connects and closes properly."""
        backend = SQLiteBackend(temp_db)

        await backend.connect()
        assert backend._conn is not None

        await backend.close()
        assert backend._conn is None

    @pytest.mark.asyncio
    async def test_execute_and_fetch(self, temp_db):
        """Direct execute and fetch operations work."""
        backend = SQLiteBackend(temp_db)
        await backend.connect()

        await backend.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        await backend.execute("INSERT INTO test VALUES (?, ?)", (1, "hello"))

        row = await backend.fetchone("SELECT * FROM test WHERE id = ?", (1,))
        assert row == (1, "hello")

        rows = await backend.fetchall("SELECT * FROM test")
        assert len(rows) == 1

        await backend.close()


# Integration test


@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
class TestSQLitePersistence:
    """Test that state persists across connections."""

    @pytest.mark.asyncio
    async def test_state_survives_reconnect(self, temp_db):
        """State persists when agent reconnects."""
        # First connection: save state
        agent1 = create_sqlite_agent(
            db_path=temp_db,
            table="persist_test",
            key="persist_key",
            schema=SimpleState,
        )
        await agent1.connect()
        await agent1.save(SimpleState(value=42, name="persistent"))
        await agent1.close()

        # Second connection: load state
        agent2 = create_sqlite_agent(
            db_path=temp_db,
            table="persist_test",
            key="persist_key",
            schema=SimpleState,
        )
        await agent2.connect()
        loaded = await agent2.load()
        await agent2.close()

        assert loaded.value == 42
        assert loaded.name == "persistent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
