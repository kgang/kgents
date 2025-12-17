"""
Tests for TableAdapter: The Alembic -> D-gent bridge.

Tests verify:
1. DgentProtocol compliance (put, get, delete, list, causal_chain)
2. SQLAlchemy model serialization/deserialization
3. Causal chain reconstruction
4. StateBackend integration for StateFunctor
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator

import pytest
from sqlalchemy import String
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from agents.d.adapters.table_adapter import TableAdapter, TableStateBackend
from agents.d.datum import Datum


# =============================================================================
# Test Models
# =============================================================================


class TestBase(DeclarativeBase):
    """Test-only SQLAlchemy base."""
    pass


class TestModel(TestBase):
    """Simple test model without causality."""

    __tablename__ = "test_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    value: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class CausalTestModel(TestBase):
    """Test model with causal_parent for chain tests."""

    __tablename__ = "causal_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    content: Mapped[str] = mapped_column(String(1000))
    causal_parent: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def temp_db() -> AsyncGenerator[tuple[AsyncEngine, async_sessionmaker[AsyncSession]], None]:
    """Create a temporary SQLite database with test tables."""
    with tempfile.TemporaryDirectory() as td:
        db_path = Path(td) / "test.db"
        url = f"sqlite+aiosqlite:///{db_path}"

        engine = create_async_engine(url, echo=False)

        async with engine.begin() as conn:
            await conn.run_sync(TestBase.metadata.create_all)

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        yield engine, factory

        await engine.dispose()


@pytest.fixture
def adapter(temp_db: tuple[AsyncEngine, async_sessionmaker[AsyncSession]]) -> TableAdapter[TestModel]:
    """TableAdapter for TestModel."""
    _, factory = temp_db
    return TableAdapter(model=TestModel, session_factory=factory)


@pytest.fixture
def causal_adapter(temp_db: tuple[AsyncEngine, async_sessionmaker[AsyncSession]]) -> TableAdapter[CausalTestModel]:
    """TableAdapter for CausalTestModel."""
    _, factory = temp_db
    return TableAdapter(model=CausalTestModel, session_factory=factory)


# =============================================================================
# Basic Protocol Tests
# =============================================================================


class TestTableAdapterProtocol:
    """Tests for DgentProtocol compliance."""

    async def test_put_returns_id(self, adapter: TableAdapter[TestModel]) -> None:
        """put() returns the datum ID."""
        datum = Datum.create(
            b'{"name": "test", "value": 42}',
            id="item-001",
        )
        result = await adapter.put(datum)
        assert result == "item-001"

    async def test_get_returns_datum(self, adapter: TableAdapter[TestModel]) -> None:
        """get() returns stored datum."""
        datum = Datum.create(
            b'{"name": "test", "value": 42}',
            id="item-002",
        )
        await adapter.put(datum)

        result = await adapter.get("item-002")
        assert result is not None
        assert result.id == "item-002"
        assert result.metadata["source"] == "alembic"
        assert result.metadata["table"] == "test_items"

        # Verify content is deserializable
        content = json.loads(result.content.decode("utf-8"))
        assert content["name"] == "test"
        assert content["value"] == 42

    async def test_get_missing_returns_none(self, adapter: TableAdapter[TestModel]) -> None:
        """get() returns None for missing ID."""
        result = await adapter.get("nonexistent")
        assert result is None

    async def test_delete_existing(self, adapter: TableAdapter[TestModel]) -> None:
        """delete() removes existing record."""
        datum = Datum.create(b'{"name": "delete-me", "value": 0}', id="to-delete")
        await adapter.put(datum)

        assert await adapter.delete("to-delete")
        assert await adapter.get("to-delete") is None

    async def test_delete_missing(self, adapter: TableAdapter[TestModel]) -> None:
        """delete() returns False for missing record."""
        result = await adapter.delete("nonexistent")
        assert result is False

    async def test_put_overwrites(self, adapter: TableAdapter[TestModel]) -> None:
        """put() with same ID updates existing record."""
        datum1 = Datum.create(b'{"name": "v1", "value": 1}', id="same-id")
        datum2 = Datum.create(b'{"name": "v2", "value": 2}', id="same-id")

        await adapter.put(datum1)
        await adapter.put(datum2)

        result = await adapter.get("same-id")
        assert result is not None
        content = json.loads(result.content.decode("utf-8"))
        assert content["name"] == "v2"
        assert content["value"] == 2

    async def test_exists(self, adapter: TableAdapter[TestModel]) -> None:
        """exists() checks for record presence."""
        datum = Datum.create(b'{"name": "exist", "value": 0}', id="exists-test")
        await adapter.put(datum)

        assert await adapter.exists("exists-test")
        assert not await adapter.exists("does-not-exist")

    async def test_count(self, adapter: TableAdapter[TestModel]) -> None:
        """count() returns total records."""
        assert await adapter.count() == 0

        for i in range(3):
            datum = Datum.create(
                f'{{"name": "item-{i}", "value": {i}}}'.encode(),
                id=f"count-{i}",
            )
            await adapter.put(datum)

        assert await adapter.count() == 3


# =============================================================================
# List Tests
# =============================================================================


class TestTableAdapterList:
    """Tests for list() with filters."""

    async def test_list_all(self, adapter: TableAdapter[TestModel]) -> None:
        """list() returns all records when no filters."""
        for i in range(5):
            datum = Datum.create(
                f'{{"name": "item-{i}", "value": {i}}}'.encode(),
                id=f"list-{i}",
            )
            await adapter.put(datum)

        result = await adapter.list()
        assert len(result) == 5

    async def test_list_with_prefix(self, adapter: TableAdapter[TestModel]) -> None:
        """list() filters by ID prefix."""
        for i in range(3):
            datum = Datum.create(
                f'{{"name": "alpha-{i}", "value": {i}}}'.encode(),
                id=f"alpha-{i}",
            )
            await adapter.put(datum)

        for i in range(2):
            datum = Datum.create(
                f'{{"name": "beta-{i}", "value": {i}}}'.encode(),
                id=f"beta-{i}",
            )
            await adapter.put(datum)

        alpha_items = await adapter.list(prefix="alpha-")
        assert len(alpha_items) == 3

        beta_items = await adapter.list(prefix="beta-")
        assert len(beta_items) == 2

    async def test_list_with_limit(self, adapter: TableAdapter[TestModel]) -> None:
        """list() respects limit parameter."""
        for i in range(10):
            datum = Datum.create(
                f'{{"name": "item-{i}", "value": {i}}}'.encode(),
                id=f"limited-{i}",
            )
            await adapter.put(datum)

        result = await adapter.list(limit=3)
        assert len(result) == 3


# =============================================================================
# Causal Chain Tests
# =============================================================================


class TestTableAdapterCausalChain:
    """Tests for causal_chain() reconstruction."""

    async def test_causal_chain_single(self, causal_adapter: TableAdapter[CausalTestModel]) -> None:
        """causal_chain() returns single item for no parents."""
        datum = Datum.create(
            b'{"content": "root"}',
            id="root",
        )
        await causal_adapter.put(datum)

        chain = await causal_adapter.causal_chain("root")
        assert len(chain) == 1
        assert chain[0].id == "root"

    async def test_causal_chain_linear(self, causal_adapter: TableAdapter[CausalTestModel]) -> None:
        """causal_chain() reconstructs linear ancestry."""
        # Create chain: A -> B -> C
        root = Datum.create(b'{"content": "root"}', id="A")
        await causal_adapter.put(root)

        middle = Datum.create(b'{"content": "middle"}', id="B", causal_parent="A")
        await causal_adapter.put(middle)

        leaf = Datum.create(b'{"content": "leaf"}', id="C", causal_parent="B")
        await causal_adapter.put(leaf)

        chain = await causal_adapter.causal_chain("C")
        assert len(chain) == 3
        assert [d.id for d in chain] == ["A", "B", "C"]

    async def test_causal_chain_missing(self, causal_adapter: TableAdapter[CausalTestModel]) -> None:
        """causal_chain() returns empty for missing ID."""
        chain = await causal_adapter.causal_chain("nonexistent")
        assert chain == []

    async def test_causal_chain_model_without_causality(self, adapter: TableAdapter[TestModel]) -> None:
        """causal_chain() returns single item for models without causal_parent."""
        datum = Datum.create(b'{"name": "test", "value": 0}', id="no-causality")
        await adapter.put(datum)

        chain = await adapter.causal_chain("no-causality")
        assert len(chain) == 1
        assert chain[0].id == "no-causality"


# =============================================================================
# StateBackend Integration Tests
# =============================================================================


class TestTableStateBackend:
    """Tests for StateBackend integration with StateFunctor."""

    async def test_state_load_save_roundtrip(self, adapter: TableAdapter[TestModel]) -> None:
        """State can be saved and loaded."""
        backend = adapter.as_state_backend("state-key")

        # Save state
        async with adapter.session_factory() as session:
            initial = TestModel(id="state-key", name="initial", value=100)
            session.add(initial)
            await session.commit()

        # Load via backend
        loaded = await backend.load()
        assert loaded.name == "initial"
        assert loaded.value == 100

    async def test_state_initial_on_missing(self, adapter: TableAdapter[TestModel]) -> None:
        """Initial state used when key missing."""
        async with adapter.session_factory() as session:
            initial = TestModel(id="initial-id", name="default", value=0)

        backend = TableStateBackend(
            adapter=adapter,
            key="missing-key",
            initial=initial,
        )

        loaded = await backend.load()
        assert loaded.name == "default"
        assert loaded.value == 0

    async def test_state_error_on_missing_no_initial(self, adapter: TableAdapter[TestModel]) -> None:
        """Error raised when key missing and no initial."""
        backend = adapter.as_state_backend("missing-key")

        with pytest.raises(ValueError, match="No state found"):
            await backend.load()

    async def test_state_save_creates_record(self, adapter: TableAdapter[TestModel]) -> None:
        """save() creates new record via TableAdapter."""
        backend = adapter.as_state_backend("new-state")

        # Create state object
        async with adapter.session_factory() as session:
            state = TestModel(id="new-state", name="created", value=42)

        await backend.save(state)

        # Verify via adapter
        datum = await adapter.get("new-state")
        assert datum is not None
        content = json.loads(datum.content.decode("utf-8"))
        assert content["name"] == "created"
        assert content["value"] == 42


# =============================================================================
# Metadata Tests
# =============================================================================


class TestTableAdapterMetadata:
    """Tests for metadata tagging."""

    async def test_source_metadata(self, adapter: TableAdapter[TestModel]) -> None:
        """Datum includes source=alembic metadata."""
        datum = Datum.create(b'{"name": "meta", "value": 0}', id="meta-test")
        await adapter.put(datum)

        result = await adapter.get("meta-test")
        assert result is not None
        assert result.metadata["source"] == "alembic"

    async def test_table_metadata(self, adapter: TableAdapter[TestModel]) -> None:
        """Datum includes table name in metadata."""
        datum = Datum.create(b'{"name": "meta", "value": 0}', id="table-meta")
        await adapter.put(datum)

        result = await adapter.get("table-meta")
        assert result is not None
        assert result.metadata["table"] == "test_items"

    async def test_table_name_property(self, adapter: TableAdapter[TestModel]) -> None:
        """table_name property returns correct value."""
        assert adapter.table_name == "test_items"
