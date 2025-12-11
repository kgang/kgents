"""
Tests for L-gent + D-gent Persistence Integration

Tests the PersistentRegistry implementation which wraps
Registry with PersistentAgent for durable storage.
"""

import tempfile
from pathlib import Path

import pytest

from ..persistence import (
    PersistenceConfig,
    PersistentRegistry,
    SaveStrategy,
    create_persistent_registry,
    load_or_create_registry,
)
from ..types import CatalogEntry, EntityType, Status

# ========== Fixtures ==========


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_entry() -> CatalogEntry:
    """Create a sample catalog entry for testing."""
    return CatalogEntry(
        id="test-agent-001",
        entity_type=EntityType.AGENT,
        name="TestAgent",
        version="1.0.0",
        description="A test agent for unit testing",
        keywords=["test", "sample"],
        author="test-suite",
    )


@pytest.fixture
def sample_tongue_entry() -> CatalogEntry:
    """Create a sample tongue entry for testing."""
    return CatalogEntry(
        id="test-tongue-001",
        entity_type=EntityType.TONGUE,
        name="CalendarTongue",
        version="1.0.0",
        description="Calendar management DSL",
        keywords=["calendar", "dsl", "scheduling"],
        author="g-gent",
        tongue_domain="Calendar Management",
        tongue_constraints=["No DELETE", "No past dates"],
        tongue_level="COMMAND",
        tongue_format="BNF",
    )


# ========== Basic Persistence Tests ==========


class TestPersistentRegistryCreation:
    """Tests for PersistentRegistry creation and initialization."""

    @pytest.mark.asyncio
    async def test_create_new_registry(self, temp_dir) -> None:
        """Creating a new persistent registry should work."""
        path = temp_dir / "catalog.json"

        registry = await PersistentRegistry.create(path=path)

        assert registry is not None
        assert registry.path == path
        assert registry.catalog.entries == {}

    @pytest.mark.asyncio
    async def test_create_loads_existing(self, temp_dir, sample_entry) -> None:
        """Creating registry should load existing catalog from disk."""
        path = temp_dir / "catalog.json"

        # Create and populate first registry
        registry1 = await PersistentRegistry.create(path=path)
        await registry1.register(sample_entry)

        # Create second registry from same path
        registry2 = await PersistentRegistry.create(path=path)

        assert len(registry2.catalog.entries) == 1
        entry = await registry2.get("test-agent-001")
        assert entry is not None
        assert entry.name == "TestAgent"

    @pytest.mark.asyncio
    async def test_create_with_custom_config(self, temp_dir) -> None:
        """Custom configuration should be respected."""
        path = temp_dir / "catalog.json"
        config = PersistenceConfig(
            save_strategy=SaveStrategy.MANUAL,
            max_history=100,
        )

        registry = await PersistentRegistry.create(path=path, config=config)

        assert registry.config.save_strategy == SaveStrategy.MANUAL
        assert registry.config.max_history == 100

    @pytest.mark.asyncio
    async def test_create_fails_if_missing_and_not_allowed(self, temp_dir) -> None:
        """Should fail if catalog doesn't exist and create_if_missing=False."""
        path = temp_dir / "nonexistent.json"
        config = PersistenceConfig(create_if_missing=False)

        with pytest.raises(FileNotFoundError):
            await PersistentRegistry.create(path=path, config=config)


class TestPersistentRegistryOperations:
    """Tests for registry operations with persistence."""

    @pytest.mark.asyncio
    async def test_register_auto_saves(self, temp_dir, sample_entry) -> None:
        """Register should auto-save when strategy is ON_WRITE."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_entry)

        # Verify file was created
        assert path.exists()

        # Load fresh registry and verify entry persisted
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-agent-001")
        assert entry is not None

    @pytest.mark.asyncio
    async def test_register_manual_save(self, temp_dir, sample_entry) -> None:
        """Register should NOT auto-save when strategy is MANUAL."""
        path = temp_dir / "catalog.json"
        config = PersistenceConfig(save_strategy=SaveStrategy.MANUAL)
        registry = await PersistentRegistry.create(path=path, config=config)

        await registry.register(sample_entry)
        assert registry.is_dirty  # Marked as having unsaved changes

        # Entry should NOT be persisted yet
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-agent-001")
        assert entry is None

        # Now explicitly save
        await registry.save()
        assert not registry.is_dirty

        # Now it should be persisted
        registry3 = await PersistentRegistry.create(path=path)
        entry = await registry3.get("test-agent-001")
        assert entry is not None

    @pytest.mark.asyncio
    async def test_delete_persists(self, temp_dir, sample_entry) -> None:
        """Delete should persist changes."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_entry)
        await registry.delete("test-agent-001")

        # Verify deletion persisted
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-agent-001")
        assert entry is None

    @pytest.mark.asyncio
    async def test_update_usage_persists(self, temp_dir, sample_entry) -> None:
        """Update usage should persist metrics."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_entry)
        await registry.update_usage("test-agent-001", success=True)
        await registry.update_usage("test-agent-001", success=True)
        await registry.update_usage("test-agent-001", success=False, error="Test error")

        # Verify persisted
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-agent-001")
        assert entry is not None
        assert entry.usage_count == 3
        assert 0.6 <= entry.success_rate <= 0.7  # 2/3 success
        assert entry.last_error == "Test error"

    @pytest.mark.asyncio
    async def test_deprecate_persists(self, temp_dir, sample_entry) -> None:
        """Deprecation should persist."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_entry)
        await registry.deprecate("test-agent-001", reason="Superseded by v2")

        # Verify persisted
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-agent-001")
        assert entry is not None
        assert entry.status == Status.DEPRECATED
        assert entry.deprecation_reason == "Superseded by v2"

    @pytest.mark.asyncio
    async def test_add_relationship_persists(self, temp_dir, sample_entry) -> None:
        """Relationships should persist."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        # Create two entries
        entry2 = CatalogEntry(
            id="test-agent-002",
            entity_type=EntityType.AGENT,
            name="TestAgent2",
            version="1.0.0",
            description="Another test agent",
        )
        await registry.register(sample_entry)
        await registry.register(entry2)

        # Add relationship
        await registry.add_relationship(
            "test-agent-001", "test-agent-002", "depends_on"
        )

        # Verify persisted
        registry2 = await PersistentRegistry.create(path=path)
        related = await registry2.find_related("test-agent-001", "depends_on")
        assert len(related) == 1
        assert related[0].id == "test-agent-002"


class TestPersistentRegistryReload:
    """Tests for reload functionality."""

    @pytest.mark.asyncio
    async def test_reload_discards_changes(self, temp_dir, sample_entry) -> None:
        """Reload should discard in-memory changes."""
        path = temp_dir / "catalog.json"
        config = PersistenceConfig(save_strategy=SaveStrategy.MANUAL)
        registry = await PersistentRegistry.create(path=path, config=config)

        # Register and save
        await registry.register(sample_entry)
        await registry.save()

        # Make changes without saving
        entry2 = CatalogEntry(
            id="test-agent-002",
            entity_type=EntityType.AGENT,
            name="TestAgent2",
            version="1.0.0",
            description="Should be discarded",
        )
        await registry.register(entry2)
        assert await registry.exists("test-agent-002")

        # Reload - should discard entry2
        await registry.reload()
        assert await registry.exists("test-agent-001")
        assert not await registry.exists("test-agent-002")


class TestCatalogHistory:
    """Tests for catalog history tracking."""

    @pytest.mark.asyncio
    async def test_history_tracks_changes(self, temp_dir, sample_entry) -> None:
        """Catalog history should track saves."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        # Make multiple changes
        await registry.register(sample_entry)

        entry2 = CatalogEntry(
            id="test-agent-002",
            entity_type=EntityType.AGENT,
            name="TestAgent2",
            version="1.0.0",
            description="Second agent",
        )
        await registry.register(entry2)

        entry3 = CatalogEntry(
            id="test-agent-003",
            entity_type=EntityType.AGENT,
            name="TestAgent3",
            version="1.0.0",
            description="Third agent",
        )
        await registry.register(entry3)

        # Get history
        history = await registry.catalog_history(limit=3)

        # Should have 3 snapshots (each register triggered save)
        assert len(history) == 3

        # History is newest first
        assert len(history[0].entries) == 3  # 3 entries
        assert len(history[1].entries) == 2  # 2 entries
        assert len(history[2].entries) == 1  # 1 entry

    @pytest.mark.asyncio
    async def test_history_respects_limit(self, temp_dir, sample_entry) -> None:
        """History should respect limit parameter."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        # Make 5 changes
        for i in range(5):
            entry = CatalogEntry(
                id=f"test-agent-{i:03d}",
                entity_type=EntityType.AGENT,
                name=f"TestAgent{i}",
                version="1.0.0",
                description=f"Agent {i}",
            )
            await registry.register(entry)

        # Get limited history
        history = await registry.catalog_history(limit=2)
        assert len(history) == 2


class TestTonguePersistence:
    """Tests for tongue-specific persistence."""

    @pytest.mark.asyncio
    async def test_tongue_metadata_persists(
        self, temp_dir, sample_tongue_entry
    ) -> None:
        """Tongue-specific metadata should persist correctly."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_tongue_entry)

        # Reload and verify
        registry2 = await PersistentRegistry.create(path=path)
        entry = await registry2.get("test-tongue-001")

        assert entry is not None
        assert entry.entity_type == EntityType.TONGUE
        assert entry.tongue_domain == "Calendar Management"
        assert entry.tongue_constraints == ["No DELETE", "No past dates"]
        assert entry.tongue_level == "COMMAND"
        assert entry.tongue_format == "BNF"

    @pytest.mark.asyncio
    async def test_tongue_search_after_reload(
        self, temp_dir, sample_tongue_entry
    ) -> None:
        """Search should work correctly after reload."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        await registry.register(sample_tongue_entry)

        # Reload and search
        registry2 = await PersistentRegistry.create(path=path)
        results = await registry2.find(query="Calendar", entity_type=EntityType.TONGUE)

        assert len(results) >= 1
        assert results[0].entry.id == "test-tongue-001"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_create_persistent_registry(self, temp_dir, sample_entry) -> None:
        """create_persistent_registry should work with defaults."""
        path = temp_dir / "catalog.json"

        registry = await create_persistent_registry(path)

        assert registry is not None
        assert registry.config.save_strategy == SaveStrategy.ON_WRITE

        await registry.register(sample_entry)
        assert path.exists()

    @pytest.mark.asyncio
    async def test_create_persistent_registry_no_auto_save(
        self, temp_dir, sample_entry
    ):
        """create_persistent_registry with auto_save=False."""
        path = temp_dir / "catalog.json"

        registry = await create_persistent_registry(path, auto_save=False)

        assert registry.config.save_strategy == SaveStrategy.MANUAL

    @pytest.mark.asyncio
    async def test_load_or_create_registry_new(self, temp_dir) -> None:
        """load_or_create_registry should create new catalog."""
        path = temp_dir / "catalog.json"

        registry = await load_or_create_registry(path)

        assert registry is not None
        assert len(registry.catalog.entries) == 0

    @pytest.mark.asyncio
    async def test_load_or_create_registry_existing(
        self, temp_dir, sample_entry
    ) -> None:
        """load_or_create_registry should load existing catalog."""
        path = temp_dir / "catalog.json"

        # Create with data
        registry1 = await load_or_create_registry(path)
        await registry1.register(sample_entry)

        # Load existing
        registry2 = await load_or_create_registry(path)

        assert len(registry2.catalog.entries) == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_concurrent_registrations(self, temp_dir) -> None:
        """Multiple registrations should not corrupt data."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        # Register many entries
        entries = [
            CatalogEntry(
                id=f"agent-{i:03d}",
                entity_type=EntityType.AGENT,
                name=f"Agent{i}",
                version="1.0.0",
                description=f"Agent number {i}",
            )
            for i in range(20)
        ]

        for entry in entries:
            await registry.register(entry)

        # Verify all persisted
        registry2 = await PersistentRegistry.create(path=path)
        assert len(registry2.catalog.entries) == 20

    @pytest.mark.asyncio
    async def test_unicode_content(self, temp_dir) -> None:
        """Unicode content should persist correctly."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        entry = CatalogEntry(
            id="unicode-test",
            entity_type=EntityType.AGENT,
            name="日本語Agent",
            version="1.0.0",
            description="Agent with émojis 🤖 and 中文字符",
            keywords=["テスト", "prueba", "тест"],
        )
        await registry.register(entry)

        # Verify persisted
        registry2 = await PersistentRegistry.create(path=path)
        loaded = await registry2.get("unicode-test")
        assert loaded is not None
        assert loaded.name == "日本語Agent"
        assert "🤖" in loaded.description
        assert "テスト" in loaded.keywords

    @pytest.mark.asyncio
    async def test_empty_fields(self, temp_dir) -> None:
        """Entries with minimal fields should work."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        entry = CatalogEntry(
            id="minimal-test",
            entity_type=EntityType.SPEC,
            name="MinimalSpec",
            version="0.1.0",
            description="A minimal specification",
        )
        await registry.register(entry)

        registry2 = await PersistentRegistry.create(path=path)
        loaded = await registry2.get("minimal-test")
        assert loaded is not None
        assert loaded.keywords == []
        assert loaded.contracts_implemented == []

    @pytest.mark.asyncio
    async def test_close_saves_on_exit(self, temp_dir, sample_entry) -> None:
        """close() should save when strategy is ON_EXIT."""
        path = temp_dir / "catalog.json"
        config = PersistenceConfig(save_strategy=SaveStrategy.ON_EXIT)
        registry = await PersistentRegistry.create(path=path, config=config)

        await registry.register(sample_entry)
        assert registry.is_dirty

        # Verify not yet persisted
        registry2 = await PersistentRegistry.create(path=path)
        assert await registry2.get("test-agent-001") is None

        # Close should save
        await registry.close()
        assert not registry.is_dirty

        # Now should be persisted
        registry3 = await PersistentRegistry.create(path=path)
        assert await registry3.get("test-agent-001") is not None


class TestDGentIntegration:
    """Tests verifying D-gent behavior through L-gent interface."""

    @pytest.mark.asyncio
    async def test_atomic_writes(self, temp_dir, sample_entry) -> None:
        """Saves should be atomic (no corruption on partial writes)."""
        path = temp_dir / "catalog.json"
        registry = await PersistentRegistry.create(path=path)

        # Register entry
        await registry.register(sample_entry)

        # File should exist and be valid JSON
        import json

        with open(path) as f:
            data = json.load(f)
        assert "entries" in data
        assert "test-agent-001" in data["entries"]

    @pytest.mark.asyncio
    async def test_history_file_created(self, temp_dir, sample_entry) -> None:
        """JSONL history file should be created."""
        path = temp_dir / "catalog.json"
        history_path = path.with_suffix(".json.jsonl")

        registry = await PersistentRegistry.create(path=path)
        await registry.register(sample_entry)

        # History file should exist
        assert history_path.exists()

    @pytest.mark.asyncio
    async def test_parent_directory_created(self, temp_dir, sample_entry) -> None:
        """Parent directories should be created if missing."""
        path = temp_dir / "nested" / "deep" / "catalog.json"

        registry = await PersistentRegistry.create(path=path)
        await registry.register(sample_entry)

        assert path.exists()
        assert path.parent.exists()
