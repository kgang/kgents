"""
L-gent Registry Tests

Tests for the L-gent catalog registry implementation.
"""

from __future__ import annotations

import pytest

from agents.l import CatalogEntry, EntityType, Registry, Status

# ============================================================================
# CatalogEntry Tests
# ============================================================================


def test_catalog_entry_creation() -> None:
    """Test creating a catalog entry."""
    entry = CatalogEntry(
        id="test:example:1.0.0",
        entity_type=EntityType.AGENT,
        name="Example Agent",
        version="1.0.0",
        description="An example agent for testing",
    )

    assert entry.id == "test:example:1.0.0"
    assert entry.entity_type == EntityType.AGENT
    assert entry.name == "Example Agent"
    assert entry.version == "1.0.0"
    assert entry.description == "An example agent for testing"
    assert entry.status == Status.ACTIVE  # Default


def test_catalog_entry_tongue_metadata() -> None:
    """Test tongue-specific metadata fields."""
    entry = CatalogEntry(
        id="tongue:calendar:1.0.0",
        entity_type=EntityType.TONGUE,
        name="Calendar Commands",
        version="1.0.0",
        description="DSL for calendar operations",
        tongue_domain="Calendar Management",
        tongue_constraints=["No deletes", "No overwrites"],
        tongue_level="command",
        tongue_format="bnf",
    )

    assert entry.entity_type == EntityType.TONGUE
    assert entry.tongue_domain == "Calendar Management"
    assert entry.tongue_constraints == ["No deletes", "No overwrites"]
    assert entry.tongue_level == "command"
    assert entry.tongue_format == "bnf"


def test_catalog_entry_serialization() -> None:
    """Test entry to_dict and from_dict round-trip."""
    entry = CatalogEntry(
        id="test:serialization:1.0.0",
        entity_type=EntityType.TONGUE,
        name="Serialization Test",
        version="1.0.0",
        description="Testing serialization",
        keywords=["test", "serialization"],
        tongue_domain="Testing",
        tongue_constraints=["Constraint 1"],
    )

    # Serialize
    data = entry.to_dict()
    assert data["id"] == "test:serialization:1.0.0"
    assert data["entity_type"] == "tongue"

    # Deserialize
    restored = CatalogEntry.from_dict(data)
    assert restored.id == entry.id
    assert restored.entity_type == entry.entity_type
    assert restored.tongue_domain == entry.tongue_domain


# ============================================================================
# Registry Tests
# ============================================================================


@pytest.mark.asyncio
async def test_registry_register_and_get() -> None:
    """Test registering and retrieving entries."""
    registry = Registry()

    entry = CatalogEntry(
        id="test:register:1.0.0",
        entity_type=EntityType.AGENT,
        name="Register Test",
        version="1.0.0",
        description="Test registration",
    )

    # Register
    entry_id = await registry.register(entry)
    assert entry_id == "test:register:1.0.0"

    # Get
    retrieved = await registry.get(entry_id)
    assert retrieved is not None
    assert retrieved.id == entry_id
    assert retrieved.name == "Register Test"


@pytest.mark.asyncio
async def test_registry_exists() -> None:
    """Test exists check."""
    registry = Registry()

    entry = CatalogEntry(
        id="test:exists:1.0.0",
        entity_type=EntityType.AGENT,
        name="Exists Test",
        version="1.0.0",
        description="Test exists",
    )

    # Should not exist initially
    assert not await registry.exists(entry.id)

    # Register
    await registry.register(entry)

    # Should exist now
    assert await registry.exists(entry.id)


@pytest.mark.asyncio
async def test_registry_list_with_filters() -> None:
    """Test listing entries with filters."""
    registry = Registry()

    # Register multiple entries
    entries = [
        CatalogEntry(
            id=f"test:list:{i}",
            entity_type=EntityType.TONGUE if i % 2 == 0 else EntityType.AGENT,
            name=f"Entry {i}",
            version="1.0.0",
            description=f"Entry {i}",
            author="alice" if i < 3 else "bob",
        )
        for i in range(5)
    ]

    for entry in entries:
        await registry.register(entry)

    # List all
    all_entries = await registry.list_entries()
    assert len(all_entries) == 5

    # Filter by entity_type
    tongues = await registry.list_entries(entity_type=EntityType.TONGUE)
    assert len(tongues) == 3  # 0, 2, 4

    # Filter by author
    alice_entries = await registry.list_entries(author="alice")
    assert len(alice_entries) == 3  # 0, 1, 2

    # Filter with limit
    limited = await registry.list_entries(limit=2)
    assert len(limited) == 2


@pytest.mark.asyncio
async def test_registry_find() -> None:
    """Test finding entries by search."""
    registry = Registry()

    # Register test entries
    await registry.register(
        CatalogEntry(
            id="tongue:calendar:1.0.0",
            entity_type=EntityType.TONGUE,
            name="Calendar Commands",
            version="1.0.0",
            description="DSL for calendar management operations",
            keywords=["calendar", "scheduling"],
            tongue_domain="Calendar Management",
        )
    )

    await registry.register(
        CatalogEntry(
            id="tongue:database:1.0.0",
            entity_type=EntityType.TONGUE,
            name="Database Queries",
            version="1.0.0",
            description="DSL for database query operations",
            keywords=["database", "query"],
            tongue_domain="Database Operations",
        )
    )

    # Search by query
    results = await registry.find(query="calendar")
    assert len(results) > 0
    assert any(
        "calendar" in r.entry.name.lower() or "calendar" in r.entry.description.lower()
        for r in results
    )

    # Search by entity_type
    tongue_results = await registry.find(entity_type=EntityType.TONGUE)
    assert len(tongue_results) == 2

    # Search by keywords
    keyword_results = await registry.find(keywords=["calendar"])
    assert len(keyword_results) > 0


@pytest.mark.asyncio
async def test_registry_update_usage() -> None:
    """Test updating usage metrics."""
    registry = Registry()

    entry = CatalogEntry(
        id="test:usage:1.0.0",
        entity_type=EntityType.TONGUE,
        name="Usage Test",
        version="1.0.0",
        description="Test usage tracking",
        usage_count=0,
        success_rate=1.0,
    )

    await registry.register(entry)

    # Update usage - success
    await registry.update_usage("test:usage:1.0.0", success=True)

    updated = await registry.get("test:usage:1.0.0")
    assert updated is not None
    assert updated.usage_count == 1
    assert updated.success_rate == 1.0
    assert updated.last_used is not None

    # Update usage - failure
    await registry.update_usage("test:usage:1.0.0", success=False, error="Test error")

    updated = await registry.get("test:usage:1.0.0")
    assert updated is not None
    assert updated.usage_count == 2
    assert updated.success_rate < 1.0  # Should decrease
    assert updated.last_error == "Test error"


@pytest.mark.asyncio
async def test_registry_deprecate() -> None:
    """Test deprecating an entry."""
    registry = Registry()

    entry = CatalogEntry(
        id="test:deprecate:1.0.0",
        entity_type=EntityType.AGENT,
        name="Deprecated Agent",
        version="1.0.0",
        description="Agent to be deprecated",
    )

    await registry.register(entry)

    # Deprecate
    success = await registry.deprecate(
        "test:deprecate:1.0.0",
        reason="Replaced by v2.0.0",
        successor_id="test:deprecate:2.0.0",
    )
    assert success

    # Check status
    deprecated = await registry.get("test:deprecate:1.0.0")
    assert deprecated is not None
    assert deprecated.status == Status.DEPRECATED
    assert deprecated.deprecation_reason == "Replaced by v2.0.0"
    assert deprecated.deprecated_in_favor_of == "test:deprecate:2.0.0"


@pytest.mark.asyncio
async def test_registry_relationships() -> None:
    """Test adding and finding relationships."""
    registry = Registry()

    # Register two entries
    entry1 = CatalogEntry(
        id="test:rel1:1.0.0",
        entity_type=EntityType.TONGUE,
        name="Entry 1",
        version="1.0.0",
        description="First entry",
    )

    entry2 = CatalogEntry(
        id="test:rel2:1.0.0",
        entity_type=EntityType.TONGUE,
        name="Entry 2",
        version="1.0.0",
        description="Second entry",
    )

    await registry.register(entry1)
    await registry.register(entry2)

    # Add relationship
    success = await registry.add_relationship(
        "test:rel1:1.0.0",
        "test:rel2:1.0.0",
        "composes_with",
    )
    assert success

    # Find related
    related = await registry.find_related("test:rel1:1.0.0", "composes_with")
    assert len(related) == 1
    assert related[0].id == "test:rel2:1.0.0"


@pytest.mark.asyncio
async def test_registry_delete() -> None:
    """Test deleting an entry."""
    registry = Registry()

    entry = CatalogEntry(
        id="test:delete:1.0.0",
        entity_type=EntityType.AGENT,
        name="Delete Test",
        version="1.0.0",
        description="Test deletion",
    )

    await registry.register(entry)
    assert await registry.exists("test:delete:1.0.0")

    # Delete
    success = await registry.delete("test:delete:1.0.0")
    assert success
    assert not await registry.exists("test:delete:1.0.0")

    # Delete non-existent
    success = await registry.delete("test:nonexistent")
    assert not success


@pytest.mark.asyncio
async def test_registry_serialization() -> None:
    """Test catalog serialization."""
    registry = Registry()

    # Add entries
    for i in range(3):
        await registry.register(
            CatalogEntry(
                id=f"test:serial:{i}",
                entity_type=EntityType.TONGUE,
                name=f"Entry {i}",
                version="1.0.0",
                description=f"Description {i}",
            )
        )

    # Export
    data = registry.to_dict()
    assert len(data["entries"]) == 3

    # Import
    restored = Registry.from_dict(data)
    assert len(restored.catalog.entries) == 3
    assert await restored.exists("test:serial:0")
    assert await restored.exists("test:serial:1")
    assert await restored.exists("test:serial:2")
