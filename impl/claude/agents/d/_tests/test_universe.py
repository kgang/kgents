"""
Tests for Universe - D-gent's schema-aware data management.

The Universe provides a higher-level interface over DgentProtocol for typed objects.
"""

import json
from dataclasses import dataclass

import pytest

from agents.d import (
    DataclassSchema,
    Datum,
    Query,
    Schema,
    Universe,
    UniverseStats,
    get_universe,
    init_universe,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@dataclass
class TestObject:
    """Test object with to_dict/from_dict."""

    id: str
    name: str
    value: int

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "TestObject":
        return cls(id=data["id"], name=data["name"], value=data["value"])


@pytest.fixture
async def universe():
    """Create a fresh Universe instance for testing."""
    # Use memory backend for fast tests
    universe = Universe(namespace="test", preferred_backend="memory")
    await universe._ensure_initialized()
    return universe


# =============================================================================
# Schema Tests
# =============================================================================


@pytest.mark.asyncio
async def test_register_schema(universe: Universe):
    """Test schema registration."""
    schema = DataclassSchema(name="test_obj", type_cls=TestObject)
    universe.register_schema(schema)

    retrieved = universe.schema_for("test_obj")
    assert retrieved is not None
    assert retrieved.name == "test_obj"


@pytest.mark.asyncio
async def test_register_type_convenience(universe: Universe):
    """Test convenience register_type method."""
    universe.register_type("test_obj", TestObject)

    schema = universe.schema_for("test_obj")
    assert schema is not None
    assert schema.name == "test_obj"

    schema_by_type = universe.schema_for_type(TestObject)
    assert schema_by_type is not None
    assert schema_by_type.name == "test_obj"


# =============================================================================
# Store/Retrieve Tests
# =============================================================================


@pytest.mark.asyncio
async def test_store_and_get_typed_object(universe: Universe):
    """Test storing and retrieving a typed object."""
    # Register schema
    universe.register_type("test_obj", TestObject)

    # Store object
    obj = TestObject(id="obj-1", name="Test", value=42)
    obj_id = await universe.store(obj)

    # Retrieve object
    retrieved = await universe.get(obj_id)

    # Should get back a TestObject, not a Datum
    assert isinstance(retrieved, TestObject)
    assert retrieved.id == "obj-1"
    assert retrieved.name == "Test"
    assert retrieved.value == 42


@pytest.mark.asyncio
async def test_store_datum_schema_free(universe: Universe):
    """Test storing raw Datum without schema."""
    # Create raw datum
    datum = Datum.create(content=b"raw bytes")

    # Store datum
    datum_id = await universe.store_datum(datum)

    # Retrieve - should get Datum back (no schema)
    retrieved = await universe.get(datum_id)
    assert isinstance(retrieved, Datum)
    assert retrieved.content == b"raw bytes"


@pytest.mark.asyncio
async def test_get_nonexistent(universe: Universe):
    """Test retrieving nonexistent data."""
    result = await universe.get("does-not-exist")
    assert result is None


# =============================================================================
# Query Tests
# =============================================================================


@pytest.mark.asyncio
async def test_query_by_schema(universe: Universe):
    """Test querying by schema type."""
    universe.register_type("test_obj", TestObject)

    # Store multiple objects
    obj1 = TestObject(id="obj-1", name="First", value=1)
    obj2 = TestObject(id="obj-2", name="Second", value=2)

    await universe.store(obj1)
    await universe.store(obj2)

    # Query by schema
    q = Query(schema="test_obj", limit=10)
    results = await universe.query(q)

    assert len(results) == 2
    assert all(isinstance(r, TestObject) for r in results)


@pytest.mark.asyncio
async def test_query_with_limit(universe: Universe):
    """Test query limit parameter."""
    universe.register_type("test_obj", TestObject)

    # Store multiple objects
    for i in range(5):
        obj = TestObject(id=f"obj-{i}", name=f"Object {i}", value=i)
        await universe.store(obj)

    # Query with limit
    q = Query(schema="test_obj", limit=3)
    results = await universe.query(q)

    assert len(results) == 3


# =============================================================================
# Delete Tests
# =============================================================================


@pytest.mark.asyncio
async def test_delete(universe: Universe):
    """Test deleting data."""
    universe.register_type("test_obj", TestObject)

    # Store object
    obj = TestObject(id="obj-1", name="Test", value=42)
    obj_id = await universe.store(obj)

    # Verify it exists
    retrieved = await universe.get(obj_id)
    assert retrieved is not None

    # Delete it
    deleted = await universe.delete(obj_id)
    assert deleted is True

    # Verify it's gone
    retrieved = await universe.get(obj_id)
    assert retrieved is None

    # Deleting again should return False
    deleted = await universe.delete(obj_id)
    assert deleted is False


# =============================================================================
# Convenience Method Tests
# =============================================================================


@pytest.mark.asyncio
async def test_remember_fluent_api(universe: Universe):
    """Test remember() convenience method."""
    universe.register_type("test_obj", TestObject)

    # Remember returns the object
    obj = TestObject(id="obj-1", name="Test", value=42)
    returned = await universe.remember(obj)

    assert returned is obj  # Same instance


@pytest.mark.asyncio
async def test_recall_convenience(universe: Universe):
    """Test recall() convenience method."""
    universe.register_type("test_obj", TestObject)

    # Store some objects
    obj1 = TestObject(id="obj-1", name="First", value=1)
    obj2 = TestObject(id="obj-2", name="Second", value=2)

    await universe.store(obj1)
    await universe.store(obj2)

    # Recall by schema
    results = await universe.recall(schema="test_obj", limit=10)

    assert len(results) == 2


# =============================================================================
# Stats Tests
# =============================================================================


@pytest.mark.asyncio
async def test_stats(universe: Universe):
    """Test Universe statistics."""
    universe.register_type("test_obj", TestObject)

    # Store some objects
    for i in range(3):
        obj = TestObject(id=f"obj-{i}", name=f"Object {i}", value=i)
        await universe.store(obj)

    # Get stats
    stats = await universe.stats()

    assert stats.backend == "memory"
    assert stats.total_data == 3
    assert stats.schemas_registered == 1
    assert stats.namespace == "test"


# =============================================================================
# Backend Selection Tests
# =============================================================================


@pytest.mark.asyncio
async def test_auto_backend_selection():
    """Test automatic backend selection."""
    # Default should fall back to memory
    universe = Universe(namespace="test-auto", preferred_backend="auto")
    await universe._ensure_initialized()

    stats = await universe.stats()
    # Should be memory (SQLite/Postgres likely unavailable in test)
    assert stats.backend in ("memory", "sqlite", "postgres")


# =============================================================================
# Singleton Tests
# =============================================================================


def test_get_universe_singleton():
    """Test singleton access pattern."""
    u1 = get_universe()
    u2 = get_universe()

    # Should be the same instance
    assert u1 is u2


@pytest.mark.asyncio
async def test_init_universe():
    """Test explicit initialization with fresh instance."""
    # Create a fresh instance directly (not using singleton)
    universe = Universe(namespace="test-init", preferred_backend="memory")
    await universe._ensure_initialized()

    stats = await universe.stats()
    assert stats.backend == "memory"
    assert stats.namespace == "test-init"


# =============================================================================
# Error Cases
# =============================================================================


@pytest.mark.asyncio
async def test_store_without_schema_raises(universe: Universe):
    """Test storing unregistered type raises error."""
    obj = TestObject(id="obj-1", name="Test", value=42)

    with pytest.raises(ValueError, match="No schema registered"):
        await universe.store(obj)


@pytest.mark.asyncio
async def test_store_with_invalid_schema_raises(universe: Universe):
    """Test storing with invalid schema name raises error."""
    obj = TestObject(id="obj-1", name="Test", value=42)

    with pytest.raises(ValueError, match="Schema not found"):
        await universe.store(obj, schema_name="nonexistent")


# =============================================================================
# Galois Integration
# =============================================================================


class MockGaloisLossComputer:
    """Mock Galois loss computer for testing."""

    async def compute(self, content: str) -> float:
        """Return mock loss based on content length."""
        return len(content) * 0.01


@pytest.mark.asyncio
async def test_galois_integration():
    """Test Universe with Galois loss computation."""
    galois = MockGaloisLossComputer()
    universe = Universe(
        namespace="test-galois", preferred_backend="memory", galois=galois
    )
    await universe._ensure_initialized()

    # Register schema
    universe.register_type("test", TestObject)

    # Store an object
    obj = TestObject(id="obj-1", name="Test", value=42)
    obj_id = await universe.store(obj)

    # Compute loss
    loss = await universe.compute_loss(obj_id)
    assert loss is not None
    assert isinstance(loss, float)
    assert loss > 0

    # Stats should show galois enabled
    stats = await universe.stats()
    assert stats.galois_enabled is True


@pytest.mark.asyncio
async def test_galois_not_configured():
    """Test Universe without Galois returns None for loss."""
    universe = Universe(namespace="test-no-galois", preferred_backend="memory")
    await universe._ensure_initialized()

    # Register schema
    universe.register_type("test", TestObject)

    # Store an object
    obj = TestObject(id="obj-1", name="Test", value=42)
    obj_id = await universe.store(obj)

    # Compute loss should return None
    loss = await universe.compute_loss(obj_id)
    assert loss is None

    # Stats should show galois not enabled
    stats = await universe.stats()
    assert stats.galois_enabled is False


@pytest.mark.asyncio
async def test_compute_loss_nonexistent_object():
    """Test compute_loss on nonexistent object returns None."""
    galois = MockGaloisLossComputer()
    universe = Universe(
        namespace="test-galois-missing", preferred_backend="memory", galois=galois
    )
    await universe._ensure_initialized()

    # Compute loss for nonexistent object
    loss = await universe.compute_loss("nonexistent-id")
    assert loss is None
