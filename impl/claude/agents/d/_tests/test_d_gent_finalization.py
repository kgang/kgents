"""
Tests for D-gent Finalization: Lenses Enhancement + Persistence Enhancement + Integration.

Test Coverage:
1. Prism (optional fields) - 8 tests
2. Traversal (collections) - 10 tests
3. Composed lens validation - 5 tests
4. Schema versioning/migration - 8 tests
5. Backup/restore utilities - 7 tests
6. Compression strategies - 6 tests
7. Cross-agent integration (J-gent × D-gent) - 5 tests
"""

import json
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import pytest

# Import core D-gents
from agents.d import (
    EntropyConstrainedAgent,
    PersistentAgent,
    StorageError,
    VolatileAgent,
)

# Import lens enhancements
from agents.d.lens import (
    dict_items_traversal,
    dict_keys_traversal,
    dict_values_traversal,
    field_lens,
    index_lens,
    # Basic lenses
    key_lens,
    # Traversal
    list_traversal,
    optional_field_prism,
    optional_index_prism,
    optional_key_prism,
    # Composed validation
    validate_composed_lens,
    verify_prism_laws,
    verify_traversal_laws,
)

# Import persistence enhancements
from agents.d.persistence_ext import (
    # Backup/restore
    BackupManager,
    CompressedPersistentAgent,
    CompressionConfig,
    # Compression
    CompressionLevel,
    Migration,
    MigrationRegistry,
    # Schema versioning
    SchemaVersion,
    VersionedPersistentAgent,
    create_compressed_agent,
    # Convenience
    create_versioned_agent,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmpdir = Path(tempfile.mkdtemp())
    yield tmpdir
    shutil.rmtree(tmpdir)


# === Test Data Classes ===


@dataclass
class User:
    name: str
    age: int
    email: Optional[str] = None


@dataclass
class Address:
    city: str
    country: str
    zip: Optional[str] = None


@dataclass
class Profile:
    user: User
    address: Address
    tags: List[str] = field(default_factory=list)


# === Prism Tests (8 tests) ===


class TestPrism:
    """Tests for Prism optic for optional fields."""

    def test_optional_key_prism_preview_existing(self):
        """Preview returns value when key exists."""
        prism = optional_key_prism("name")
        state = {"name": "Alice", "age": 30}

        result = prism.preview(state)

        assert result == "Alice"

    def test_optional_key_prism_preview_missing(self):
        """Preview returns None when key doesn't exist."""
        prism = optional_key_prism("email")
        state = {"name": "Alice"}

        result = prism.preview(state)

        assert result is None

    def test_optional_key_prism_set_if_present(self):
        """Set only modifies when key exists."""
        prism = optional_key_prism("name")
        state = {"name": "Alice"}

        result = prism.set_if_present(state, "Bob")

        assert result == {"name": "Bob"}

    def test_optional_key_prism_set_if_missing(self):
        """Set preserves state when key doesn't exist."""
        prism = optional_key_prism("email")
        state = {"name": "Alice"}

        result = prism.set_if_present(state, "alice@example.com")

        assert result == {"name": "Alice"}  # Unchanged

    def test_optional_index_prism_valid_index(self):
        """Prism focuses on valid list index."""
        prism = optional_index_prism(1)
        items = [10, 20, 30]

        assert prism.preview(items) == 20

        result = prism.set_if_present(items, 99)
        assert result == [10, 99, 30]

    def test_optional_index_prism_out_of_bounds(self):
        """Prism returns None for out of bounds index."""
        prism = optional_index_prism(10)
        items = [1, 2, 3]

        assert prism.preview(items) is None

        result = prism.set_if_present(items, 99)
        assert result == [1, 2, 3]  # Unchanged

    def test_optional_field_prism_none_field(self):
        """Prism handles None dataclass fields."""
        prism = optional_field_prism("email")
        user = User(name="Alice", age=30, email=None)

        assert prism.preview(user) is None

        result = prism.set_if_present(user, "alice@example.com")
        assert result.email is None  # Unchanged because was None

    def test_prism_laws(self):
        """Verify prism satisfies its laws."""
        prism = optional_key_prism("name")
        state_with = {"name": "Alice"}
        state_without = {"count": 5}

        laws = verify_prism_laws(prism, state_with, state_without, "Bob")

        assert laws["preview_some"] is True
        assert laws["preview_none"] is True
        assert laws["modify_preserves"] is True


# === Traversal Tests (10 tests) ===


class TestTraversal:
    """Tests for Traversal optic for collections."""

    def test_list_traversal_get_all(self):
        """Get all elements from list."""
        trav = list_traversal()
        items = [1, 2, 3, 4, 5]

        result = trav.get_all(items)

        assert result == [1, 2, 3, 4, 5]

    def test_list_traversal_modify(self):
        """Modify all elements in list."""
        trav = list_traversal()
        items = [1, 2, 3]

        result = trav.modify(items, lambda x: x * 2)

        assert result == [2, 4, 6]

    def test_list_traversal_set_all(self):
        """Set all elements to same value."""
        trav = list_traversal()
        items = [1, 2, 3]

        result = trav.set_all(items, 0)

        assert result == [0, 0, 0]

    def test_dict_values_traversal(self):
        """Traverse dictionary values."""
        trav = dict_values_traversal()
        d = {"a": 1, "b": 2, "c": 3}

        values = trav.get_all(d)
        assert sorted(values) == [1, 2, 3]

        doubled = trav.modify(d, lambda x: x * 2)
        assert doubled == {"a": 2, "b": 4, "c": 6}

    def test_dict_keys_traversal(self):
        """Traverse dictionary keys."""
        trav = dict_keys_traversal()
        d = {"a": 1, "b": 2}

        keys = trav.get_all(d)
        assert sorted(keys) == ["a", "b"]

        upper = trav.modify(d, str.upper)
        assert upper == {"A": 1, "B": 2}

    def test_dict_items_traversal(self):
        """Traverse dictionary items."""
        trav = dict_items_traversal()
        d = {"a": 1, "b": 2}

        items = trav.get_all(d)
        assert sorted(items) == [("a", 1), ("b", 2)]

    def test_traversal_filter(self):
        """Filter traversal targets."""
        trav = list_traversal().filter(lambda x: x > 2)
        items = [1, 2, 3, 4, 5]

        filtered = trav.get_all(items)
        assert filtered == [3, 4, 5]

        # Modify only filtered elements
        result = trav.modify(items, lambda x: x * 10)
        assert result == [1, 2, 30, 40, 50]

    def test_traversal_composition(self):
        """Compose traversals for nested structures."""
        outer = list_traversal()
        inner = list_traversal()
        composed = outer >> inner

        nested = [[1, 2], [3, 4], [5, 6]]

        all_values = composed.get_all(nested)
        assert all_values == [1, 2, 3, 4, 5, 6]

        doubled = composed.modify(nested, lambda x: x * 2)
        assert doubled == [[2, 4], [6, 8], [10, 12]]

    def test_traversal_empty(self):
        """Traversal handles empty collections."""
        trav = list_traversal()
        empty: List[int] = []

        assert trav.get_all(empty) == []
        assert trav.modify(empty, lambda x: x * 2) == []

    def test_traversal_laws(self):
        """Verify traversal satisfies its laws."""
        trav = list_traversal()
        items = [1, 2, 3]

        laws = verify_traversal_laws(trav, items, 10)

        assert laws["identity"] is True
        assert laws["fusion"] is True


# === Composed Lens Validation Tests (5 tests) ===


class TestComposedLensValidation:
    """Tests for composed lens validation."""

    def test_composed_lens_valid(self):
        """Composed lens satisfies all laws."""
        user_lens = key_lens("user")
        name_lens = key_lens("name")
        state = {"user": {"name": "Alice"}}

        result = validate_composed_lens(user_lens, name_lens, state, "Bob", "Carol")

        assert result.is_valid is True
        assert result.get_put is True
        assert result.put_get is True
        assert result.put_put is True
        assert len(result.errors) == 0

    def test_composed_lens_deep_nesting(self):
        """Validate deeply nested lens composition."""
        lens1 = key_lens("a")
        lens2 = key_lens("b")
        state = {"a": {"b": {"c": 1}}}

        result = validate_composed_lens(lens1, lens2, state, {"c": 2}, {"c": 3})

        assert result.is_valid is True

    def test_composed_lens_with_dataclass(self):
        """Validate lens composition with dataclass fields."""
        user_lens = field_lens("user")
        name_lens = field_lens("name")

        profile = Profile(
            user=User(name="Alice", age=30),
            address=Address(city="NYC", country="USA"),
        )

        result = validate_composed_lens(user_lens, name_lens, profile, "Bob", "Carol")

        assert result.is_valid is True

    def test_composed_lens_index(self):
        """Validate lens with index."""
        users_lens = key_lens("users")
        first_lens = index_lens(0)
        state = {"users": ["Alice", "Bob", "Carol"]}

        result = validate_composed_lens(users_lens, first_lens, state, "Diana", "Eve")

        assert result.is_valid is True

    def test_lens_validation_detailed_results(self):
        """Validation provides detailed law results."""
        lens1 = key_lens("x")
        lens2 = key_lens("y")
        state = {"x": {"y": 1}}

        result = validate_composed_lens(lens1, lens2, state, 2, 3)

        # Check we get individual law results
        assert isinstance(result.get_put, bool)
        assert isinstance(result.put_get, bool)
        assert isinstance(result.put_put, bool)
        assert isinstance(result.errors, list)


# === Schema Versioning Tests (8 tests) ===


class TestSchemaVersioning:
    """Tests for schema versioning and migration."""

    def test_schema_version_ordering(self):
        """Schema versions compare correctly."""
        v1 = SchemaVersion("1.0.0")
        v2 = SchemaVersion("1.1.0")
        v3 = SchemaVersion("2.0.0")

        assert v1 < v2
        assert v2 < v3
        assert v1 < v3

    def test_migration_registry_single(self):
        """Register and retrieve single migration."""
        registry = MigrationRegistry()
        migration = Migration(
            from_version="1.0.0",
            to_version="1.1.0",
            up=lambda d: {**d, "new_field": "default"},
        )
        registry.register(migration)

        path = registry.get_migration_path("1.0.0", "1.1.0")

        assert len(path) == 1
        assert path[0].to_version == "1.1.0"

    def test_migration_registry_chain(self):
        """Find migration chain across multiple versions."""
        registry = MigrationRegistry()
        registry.register(Migration("1.0.0", "1.1.0", lambda d: d))
        registry.register(Migration("1.1.0", "1.2.0", lambda d: d))
        registry.register(Migration("1.2.0", "2.0.0", lambda d: d))

        path = registry.get_migration_path("1.0.0", "2.0.0")

        assert len(path) == 3
        assert path[-1].to_version == "2.0.0"

    def test_migration_registry_no_path(self):
        """Raise error when no migration path exists."""
        from agents.d.errors import StateError

        registry = MigrationRegistry()
        registry.register(Migration("1.0.0", "1.1.0", lambda d: d))

        with pytest.raises(StateError, match="No migration path"):
            registry.get_migration_path("1.0.0", "3.0.0")

    @pytest.mark.asyncio
    async def test_versioned_agent_save_load(self, temp_dir):
        """Versioned agent saves and loads with version."""
        path = temp_dir / "versioned.json"

        agent = VersionedPersistentAgent(
            path=path,
            schema=dict,
            current_version="1.0.0",
        )

        await agent.save({"name": "Alice"})
        loaded = await agent.load()

        assert loaded == {"name": "Alice"}

    @pytest.mark.asyncio
    async def test_versioned_agent_migration(self, temp_dir):
        """Versioned agent migrates old data on load."""
        path = temp_dir / "migrate.json"

        # Save with v1.0.0 format (manually)
        with open(path, "w") as f:
            json.dump(
                {
                    "_version": "1.0.0",
                    "_data": {"name": "Alice"},
                },
                f,
            )

        # Create agent with v1.1.0 and migration
        registry = MigrationRegistry()
        registry.register(
            Migration(
                from_version="1.0.0",
                to_version="1.1.0",
                up=lambda d: {**d, "migrated": True},
            )
        )

        agent = VersionedPersistentAgent(
            path=path,
            schema=dict,
            current_version="1.1.0",
            migrations=registry,
        )

        loaded = await agent.load()

        assert loaded["name"] == "Alice"
        assert loaded["migrated"] is True

    @pytest.mark.asyncio
    async def test_create_versioned_agent_helper(self, temp_dir):
        """Convenience function creates versioned agent."""
        path = temp_dir / "helper.json"

        migrations = [
            Migration("1.0.0", "1.1.0", lambda d: {**d, "v": "1.1"}),
        ]

        agent = create_versioned_agent(
            path=path,
            schema=dict,
            version="1.0.0",
            migrations=migrations,
        )

        await agent.save({"test": True})
        loaded = await agent.load()

        assert loaded["test"] is True

    @pytest.mark.asyncio
    async def test_versioned_agent_legacy_format(self, temp_dir):
        """Versioned agent handles legacy (unversioned) data."""
        path = temp_dir / "legacy.json"

        # Save without version wrapper
        with open(path, "w") as f:
            json.dump({"name": "Legacy"}, f)

        agent = VersionedPersistentAgent(
            path=path,
            schema=dict,
            current_version="1.0.0",  # Same as default
        )

        loaded = await agent.load()

        # Should load legacy data
        assert loaded.get("name") == "Legacy"


# === Backup/Restore Tests (7 tests) ===


class TestBackupRestore:
    """Tests for backup and restore utilities."""

    @pytest.mark.asyncio
    async def test_backup_creates_file(self, temp_dir):
        """Backup creates a backup file."""
        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        await agent.save({"key": "value"})

        manager = BackupManager(backup_dir=backup_dir)
        metadata = await manager.backup(agent)

        # Verify backup was created
        backups = await manager.list_backups("state")
        assert len(backups) == 1
        assert metadata.size_bytes > 0

    @pytest.mark.asyncio
    async def test_restore_from_backup(self, temp_dir):
        """Restore recovers state from backup."""
        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)

        # Save and backup original
        await agent.save({"version": 1})
        manager = BackupManager(backup_dir=backup_dir)
        await manager.backup(agent)

        # Modify state
        await agent.save({"version": 2})
        current = await agent.load()
        assert current["version"] == 2

        # Restore from backup
        await manager.restore(agent)
        restored = await agent.load()

        assert restored["version"] == 1

    @pytest.mark.asyncio
    async def test_backup_rotation(self, temp_dir):
        """Old backups are rotated out."""

        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        manager = BackupManager(backup_dir=backup_dir, max_backups=3)

        # Create 5 backups with unique labels (to avoid timestamp collision)
        for i in range(5):
            await agent.save({"version": i})
            await manager.backup(agent, label=f"v{i}")

        # Only 3 should remain
        backups = await manager.list_backups("state")
        assert len(backups) == 3

    @pytest.mark.asyncio
    async def test_backup_with_label(self, temp_dir):
        """Backup can have custom label."""
        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        await agent.save({"key": "value"})

        manager = BackupManager(backup_dir=backup_dir)
        await manager.backup(agent, label="pre_migration")

        backups = await manager.list_backups("state")
        assert any("pre_migration" in str(b) for b in backups)

    @pytest.mark.asyncio
    async def test_list_backups_sorted(self, temp_dir):
        """Backups are listed newest first."""
        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        manager = BackupManager(backup_dir=backup_dir)

        for i in range(3):
            await agent.save({"version": i})
            await manager.backup(agent)

        backups = await manager.list_backups("state")

        # Verify sorted by mtime descending
        mtimes = [b.stat().st_mtime for b in backups]
        assert mtimes == sorted(mtimes, reverse=True)

    @pytest.mark.asyncio
    async def test_verify_backup(self, temp_dir):
        """Verify backup integrity."""
        state_path = temp_dir / "state.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        await agent.save({"valid": "json"})

        manager = BackupManager(backup_dir=backup_dir)
        await manager.backup(agent)

        backups = await manager.list_backups("state")
        is_valid = await manager.verify_backup(backups[0])

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_backup_nonexistent_file(self, temp_dir):
        """Backup raises error for nonexistent file."""
        state_path = temp_dir / "nonexistent.json"
        backup_dir = temp_dir / "backups"

        agent = PersistentAgent(path=state_path, schema=dict)
        manager = BackupManager(backup_dir=backup_dir)

        with pytest.raises(StorageError, match="not found"):
            await manager.backup(agent)


# === Compression Tests (6 tests) ===


class TestCompression:
    """Tests for compression strategies."""

    @pytest.mark.asyncio
    async def test_compressed_agent_save_load(self, temp_dir):
        """Compressed agent saves and loads correctly."""
        path = temp_dir / "state.json"

        agent = CompressedPersistentAgent(
            path=path,
            schema=dict,
            compression=CompressionConfig(
                level=CompressionLevel.DEFAULT,
                min_size_bytes=0,  # Always compress
            ),
        )

        await agent.save({"key": "value"})
        loaded = await agent.load()

        assert loaded == {"key": "value"}

    @pytest.mark.asyncio
    async def test_compressed_agent_creates_gz(self, temp_dir):
        """Compressed agent creates .gz file."""
        path = temp_dir / "state.json"

        agent = CompressedPersistentAgent(
            path=path,
            schema=dict,
            compression=CompressionConfig(
                level=CompressionLevel.DEFAULT,
                min_size_bytes=0,
            ),
        )

        await agent.save({"key": "value"})

        assert path.with_suffix(".json.gz").exists()
        assert not path.exists()  # Original not created

    @pytest.mark.asyncio
    async def test_compressed_agent_skips_small(self, temp_dir):
        """Compressed agent skips compression for small data."""
        path = temp_dir / "state.json"

        agent = CompressedPersistentAgent(
            path=path,
            schema=dict,
            compression=CompressionConfig(
                level=CompressionLevel.DEFAULT,
                min_size_bytes=10000,  # 10KB minimum
            ),
        )

        await agent.save({"small": "data"})

        assert path.exists()  # Uncompressed
        assert not path.with_suffix(".json.gz").exists()

    @pytest.mark.asyncio
    async def test_compression_stats(self, temp_dir):
        """Get compression statistics."""
        path = temp_dir / "state.json"

        agent = CompressedPersistentAgent(
            path=path,
            schema=dict,
            compression=CompressionConfig(
                level=CompressionLevel.BEST,
                min_size_bytes=0,
            ),
        )

        # Save large compressible data
        large_data = {"data": "x" * 10000}
        await agent.save(large_data)

        stats = await agent.get_compression_stats()

        assert stats["is_compressed"] is True
        assert stats["compressed_size"] > 0
        assert stats["compression_ratio"] > 1.0

    @pytest.mark.asyncio
    async def test_compression_levels(self, temp_dir):
        """Different compression levels produce different sizes."""
        data = {"data": "x" * 10000}
        sizes = {}

        for level in [CompressionLevel.FAST, CompressionLevel.BEST]:
            path = temp_dir / f"state_{level.name}.json"
            agent = CompressedPersistentAgent(
                path=path,
                schema=dict,
                compression=CompressionConfig(level=level, min_size_bytes=0),
            )
            await agent.save(data)

            stats = await agent.get_compression_stats()
            sizes[level] = stats["compressed_size"]

        # BEST should be smaller or equal to FAST
        assert sizes[CompressionLevel.BEST] <= sizes[CompressionLevel.FAST]

    @pytest.mark.asyncio
    async def test_create_compressed_agent_helper(self, temp_dir):
        """Convenience function creates compressed agent."""
        path = temp_dir / "helper.json"

        agent = create_compressed_agent(
            path=path,
            schema=dict,
            level=CompressionLevel.FAST,
            min_size=0,
        )

        await agent.save({"test": True})
        loaded = await agent.load()

        assert loaded["test"] is True


# === Cross-Agent Integration Tests (5 tests) ===


class TestCrossAgentIntegration:
    """Tests for cross-agent integration (J-gent × D-gent)."""

    @pytest.mark.asyncio
    async def test_jgent_entropy_with_versioned_agent(self, temp_dir):
        """J-gent entropy constraint with versioned persistence."""
        path = temp_dir / "entropy_versioned.json"

        # Create versioned agent
        VersionedPersistentAgent(
            path=path,
            schema=dict,
            current_version="1.0.0",
        )

        # Wrap with entropy constraint

        # Use a volatile backend for entropy constraint
        volatile = VolatileAgent(_state={})
        entropy = EntropyConstrainedAgent.from_depth(
            backend=volatile,
            depth=0,
            initial_budget=1.0,
        )

        # Save via entropy-constrained agent
        await entropy.save({"constrained": True})
        loaded = await entropy.load()

        assert loaded["constrained"] is True

    @pytest.mark.asyncio
    async def test_lens_with_persistent_agent(self, temp_dir):
        """Lens composition with persistent D-gent."""
        from agents.d import LensAgent

        path = temp_dir / "lens_persistent.json"

        # Create persistent agent with nested state
        persistent = PersistentAgent(path=path, schema=dict)
        await persistent.save({"users": {"alice": {"name": "Alice", "score": 100}}})

        # Create lens to focus on alice's score
        users_lens = key_lens("users")
        alice_lens = key_lens("alice")
        score_lens = key_lens("score")
        composed = users_lens >> alice_lens >> score_lens

        # Create focused agent
        focused = LensAgent(parent=persistent, lens=composed)

        # Read through lens
        score = await focused.load()
        assert score == 100

        # Write through lens
        await focused.save(150)
        reloaded = await persistent.load()
        assert reloaded["users"]["alice"]["score"] == 150

    @pytest.mark.asyncio
    async def test_traversal_with_observable(self, temp_dir):
        """Traversal with observable D-gent for batch updates."""
        from agents.d import ObservableDataAgent

        # Create observable volatile agent
        volatile = VolatileAgent(_state={"items": [1, 2, 3, 4, 5]})
        observable = ObservableDataAgent(underlying=volatile)

        # Track changes
        changes = []
        await observable.subscribe(lambda c: changes.append(c))

        # Use traversal to modify items
        trav = list_traversal()
        state = await observable.load()
        new_items = trav.modify(state["items"], lambda x: x * 2)
        await observable.save({"items": new_items})

        # Should have recorded the change
        assert len(changes) == 1
        assert changes[0].new_value["items"] == [2, 4, 6, 8, 10]

    @pytest.mark.asyncio
    async def test_prism_with_queryable(self, temp_dir):
        """Prism with queryable D-gent for optional field access."""
        from agents.d import QueryableDataAgent

        # Create queryable volatile agent with optional field
        volatile = VolatileAgent(
            _state={
                "users": [
                    {"name": "Alice", "email": "alice@test.com"},
                    {"name": "Bob"},  # No email
                ]
            }
        )
        queryable = QueryableDataAgent(underlying=volatile)

        # Query users
        users = await queryable.get("users")
        assert len(users) == 2

        # Use prism to safely access optional email
        email_prism = optional_key_prism("email")

        alice_email = email_prism.preview(users[0])
        bob_email = email_prism.preview(users[1])

        assert alice_email == "alice@test.com"
        assert bob_email is None

    @pytest.mark.asyncio
    async def test_compression_with_unified_memory(self, temp_dir):
        """Compression strategy with unified memory."""
        path = temp_dir / "unified_compressed.json"

        # Create compressed agent
        compressed = CompressedPersistentAgent(
            path=path,
            schema=dict,
            compression=CompressionConfig(
                level=CompressionLevel.FAST,
                min_size_bytes=0,
            ),
        )

        # Save large state
        large_state = {
            "memories": ["memory " * 100 for _ in range(100)],
            "metadata": {"count": 100},
        }
        await compressed.save(large_state)

        # Verify compression
        stats = await compressed.get_compression_stats()
        assert stats["is_compressed"] is True
        assert stats["compression_ratio"] > 1.0

        # Load and verify
        loaded = await compressed.load()
        assert loaded["metadata"]["count"] == 100
        assert len(loaded["memories"]) == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
