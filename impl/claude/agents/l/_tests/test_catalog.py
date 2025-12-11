"""
Tests for L-gent catalog (Registry and CatalogEntry).
"""

import os
import tempfile

import pytest
from agents.l.catalog import CatalogEntry, EntityType, Registry, Status


@pytest.fixture
def temp_storage():
    """Temporary storage file for testing."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    yield path
    os.unlink(path)


@pytest.fixture
def sample_entry():
    """Sample catalog entry for testing."""
    return CatalogEntry(
        id="test-agent-001",
        entity_type=EntityType.AGENT,
        name="TestAgent",
        version="1.0.0",
        description="A test agent for unit testing",
        keywords=["test", "unit", "example"],
        author="test-user",
        input_type="str",
        output_type="int",
    )


@pytest.mark.asyncio
async def test_catalog_entry_serialization(sample_entry) -> None:
    """Test CatalogEntry can be serialized and deserialized."""
    # Serialize
    data = sample_entry.to_dict()

    assert data["id"] == "test-agent-001"
    assert data["entity_type"] == "agent"
    assert data["name"] == "TestAgent"
    assert data["version"] == "1.0.0"

    # Deserialize
    restored = CatalogEntry.from_dict(data)

    assert restored.id == sample_entry.id
    assert restored.entity_type == sample_entry.entity_type
    assert restored.name == sample_entry.name
    assert restored.version == sample_entry.version
    assert restored.keywords == sample_entry.keywords


@pytest.mark.asyncio
async def test_registry_register_and_get(temp_storage, sample_entry) -> None:
    """Test registering and retrieving entries."""
    registry = Registry(storage_path=temp_storage)

    # Register entry
    await registry.register(sample_entry)

    # Retrieve entry
    retrieved = await registry.get("test-agent-001")

    assert retrieved is not None
    assert retrieved.id == sample_entry.id
    assert retrieved.name == sample_entry.name


@pytest.mark.asyncio
async def test_registry_persistence(temp_storage, sample_entry) -> None:
    """Test that registry persists across instances."""
    # First instance - register entry
    registry1 = Registry(storage_path=temp_storage)
    await registry1.register(sample_entry)

    # Second instance - should load from storage
    registry2 = Registry(storage_path=temp_storage)
    retrieved = await registry2.get("test-agent-001")

    assert retrieved is not None
    assert retrieved.id == sample_entry.id
    assert retrieved.name == sample_entry.name


@pytest.mark.asyncio
async def test_registry_list_by_type(temp_storage) -> None:
    """Test filtering entries by type."""
    registry = Registry(storage_path=temp_storage)

    # Register multiple entries of different types
    agent1 = CatalogEntry(
        id="agent-1",
        entity_type=EntityType.AGENT,
        name="Agent1",
        version="1.0.0",
        description="First agent",
        keywords=["agent"],
    )

    agent2 = CatalogEntry(
        id="agent-2",
        entity_type=EntityType.AGENT,
        name="Agent2",
        version="1.0.0",
        description="Second agent",
        keywords=["agent"],
    )

    contract = CatalogEntry(
        id="contract-1",
        entity_type=EntityType.CONTRACT,
        name="Contract1",
        version="1.0.0",
        description="A contract",
        keywords=["contract"],
    )

    await registry.register(agent1)
    await registry.register(agent2)
    await registry.register(contract)

    # List agents only
    agents = await registry.list_by_type(EntityType.AGENT)

    assert len(agents) == 2
    assert all(e.entity_type == EntityType.AGENT for e in agents)


@pytest.mark.asyncio
async def test_registry_deprecate(temp_storage, sample_entry) -> None:
    """Test deprecating an entry."""
    registry = Registry(storage_path=temp_storage)

    await registry.register(sample_entry)

    # Create replacement
    replacement = CatalogEntry(
        id="test-agent-002",
        entity_type=EntityType.AGENT,
        name="TestAgentV2",
        version="2.0.0",
        description="Improved test agent",
        keywords=["test", "unit", "improved"],
    )
    await registry.register(replacement)

    # Deprecate original
    await registry.deprecate(
        "test-agent-001", reason="Replaced by v2", replacement_id="test-agent-002"
    )

    # Check deprecated entry
    deprecated = await registry.get("test-agent-001")

    assert deprecated is not None
    assert deprecated.status == Status.DEPRECATED
    assert deprecated.deprecation_reason == "Replaced by v2"
    assert deprecated.deprecated_in_favor_of == "test-agent-002"


@pytest.mark.asyncio
async def test_registry_record_usage(temp_storage, sample_entry) -> None:
    """Test recording usage statistics."""
    registry = Registry(storage_path=temp_storage)

    await registry.register(sample_entry)

    # Record successful usage
    await registry.record_usage("test-agent-001", success=True)

    entry = await registry.get("test-agent-001")
    assert entry.usage_count == 1
    assert entry.success_rate == 1.0
    assert entry.last_used is not None

    # Record failure
    await registry.record_usage("test-agent-001", success=False, error="Test error")

    entry = await registry.get("test-agent-001")
    assert entry.usage_count == 2
    assert entry.success_rate < 1.0  # Should decrease
    assert entry.last_error == "Test error"


@pytest.mark.asyncio
async def test_registry_find_by_keyword(temp_storage) -> None:
    """Test finding entries by keyword."""
    registry = Registry(storage_path=temp_storage)

    entry1 = CatalogEntry(
        id="entry-1",
        entity_type=EntityType.AGENT,
        name="Entry1",
        version="1.0.0",
        description="First entry",
        keywords=["test", "alpha"],
    )

    entry2 = CatalogEntry(
        id="entry-2",
        entity_type=EntityType.AGENT,
        name="Entry2",
        version="1.0.0",
        description="Second entry",
        keywords=["test", "beta"],
    )

    entry3 = CatalogEntry(
        id="entry-3",
        entity_type=EntityType.AGENT,
        name="Entry3",
        version="1.0.0",
        description="Third entry",
        keywords=["production", "beta"],
    )

    await registry.register(entry1)
    await registry.register(entry2)
    await registry.register(entry3)

    # Find by keyword "test"
    test_entries = await registry.find_by_keyword("test")
    assert len(test_entries) == 2

    # Find by keyword "beta"
    beta_entries = await registry.find_by_keyword("beta")
    assert len(beta_entries) == 2
