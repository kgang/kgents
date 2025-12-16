"""
Tests for GardenStore persistence layer.

Phase 3 of Gardener-Logos Enactment Plan.
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from ..garden import GardenSeason, GardenState, create_garden
from ..persistence import (
    GardenStore,
    StoredGesture,
    create_garden_store,
    get_garden_store,
    reset_garden_store,
)
from ..plots import PlotState, create_crown_jewel_plots, create_plot
from ..tending import TendingGesture, TendingVerb, apply_gesture, graft, observe

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Create a temporary database path."""
    return tmp_path / "test_gardens.db"


@pytest.fixture
async def store(temp_db_path: Path) -> GardenStore:
    """Create and initialize a GardenStore."""
    store = GardenStore(db_path=temp_db_path)
    await store.init()
    return store


@pytest.fixture
def sample_garden() -> GardenState:
    """Create a sample garden for testing."""
    garden = create_garden(name="Test Garden", season=GardenSeason.SPROUTING)
    garden.plots["test-plot"] = create_plot(
        name="test-plot",
        path="world.test",
        description="A test plot",
        crown_jewel="Test",
    )
    return garden


# =============================================================================
# Schema Tests
# =============================================================================


class TestGardenStoreInit:
    """Tests for store initialization."""

    async def test_init_creates_database(self, temp_db_path: Path) -> None:
        """Test that init creates the database file."""
        store = GardenStore(db_path=temp_db_path)
        await store.init()

        assert temp_db_path.exists()

    async def test_init_is_idempotent(self, store: GardenStore) -> None:
        """Test that init can be called multiple times."""
        # Already initialized in fixture, call again
        await store.init()
        # Should not raise

    async def test_init_creates_tables(
        self, store: GardenStore, temp_db_path: Path
    ) -> None:
        """Test that init creates all required tables."""
        import sqlite3

        conn = sqlite3.connect(str(temp_db_path))
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        assert "gardens" in tables
        assert "garden_plots" in tables
        assert "garden_gestures" in tables
        assert "garden_default" in tables


# =============================================================================
# Save/Load Tests
# =============================================================================


class TestGardenSaveLoad:
    """Tests for saving and loading gardens."""

    async def test_save_garden(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test saving a garden."""
        await store.save(sample_garden)

        # Verify it was saved
        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert loaded.garden_id == sample_garden.garden_id
        assert loaded.name == sample_garden.name

    async def test_load_garden_with_plots(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test loading a garden includes plots."""
        await store.save(sample_garden)

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert "test-plot" in loaded.plots
        assert loaded.plots["test-plot"].path == "world.test"

    async def test_load_nonexistent_garden(self, store: GardenStore) -> None:
        """Test loading a non-existent garden returns None."""
        result = await store.load("nonexistent-id")
        assert result is None

    async def test_save_updates_existing(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that save updates existing garden."""
        await store.save(sample_garden)

        # Modify and save again
        sample_garden.name = "Updated Name"
        sample_garden.season = GardenSeason.BLOOMING
        await store.save(sample_garden)

        # Verify update
        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert loaded.name == "Updated Name"
        assert loaded.season == GardenSeason.BLOOMING

    async def test_save_preserves_season_since(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that season_since is preserved."""
        original_season_since = sample_garden.season_since
        await store.save(sample_garden)

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        # Should be within 1 second (accounting for serialization)
        assert abs((loaded.season_since - original_season_since).total_seconds()) < 1

    async def test_save_garden_with_crown_jewel_plots(self, store: GardenStore) -> None:
        """Test saving garden with all crown jewel plots."""
        garden = create_garden(name="Crown Garden")
        garden.plots = create_crown_jewel_plots()

        await store.save(garden)

        loaded = await store.load(garden.garden_id)
        assert loaded is not None
        assert len(loaded.plots) == 7
        assert "atelier" in loaded.plots
        assert "holographic-brain" in loaded.plots
        assert loaded.plots["atelier"].crown_jewel == "Atelier"


# =============================================================================
# Default Garden Tests
# =============================================================================


class TestDefaultGarden:
    """Tests for default garden management."""

    async def test_get_default_creates_garden(self, store: GardenStore) -> None:
        """Test that get_default creates a garden if none exists."""
        garden = await store.get_default()

        assert garden is not None
        assert garden.name == "Default Garden"
        assert garden.season == GardenSeason.DORMANT

    async def test_get_default_includes_crown_jewels(self, store: GardenStore) -> None:
        """Test that default garden includes crown jewel plots."""
        garden = await store.get_default()

        assert len(garden.plots) == 7
        assert "gardener" in garden.plots
        assert "atelier" in garden.plots

    async def test_get_default_returns_same_garden(self, store: GardenStore) -> None:
        """Test that get_default returns the same garden on subsequent calls."""
        garden1 = await store.get_default()
        garden2 = await store.get_default()

        assert garden1.garden_id == garden2.garden_id

    async def test_set_default(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test setting a specific garden as default."""
        await store.save(sample_garden)
        await store.set_default(sample_garden.garden_id)

        default = await store.get_default()
        assert default.garden_id == sample_garden.garden_id


# =============================================================================
# Gesture Tests
# =============================================================================


class TestGestureStorage:
    """Tests for gesture persistence."""

    async def test_save_gesture(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test saving a gesture."""
        await store.save(sample_garden)

        gesture = observe("world.test", "Testing observation")
        gesture_id = await store.save_gesture(sample_garden.garden_id, gesture)

        assert gesture_id > 0

    async def test_get_gestures(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test retrieving gestures."""
        await store.save(sample_garden)

        # Save multiple gestures
        await store.save_gesture(
            sample_garden.garden_id,
            observe("world.test.a", "First observation"),
        )
        await store.save_gesture(
            sample_garden.garden_id,
            graft("world.test.b", "Adding something"),
        )

        gestures = await store.get_gestures(sample_garden.garden_id)

        assert len(gestures) == 2
        # Most recent first
        assert gestures[0].verb == TendingVerb.GRAFT
        assert gestures[1].verb == TendingVerb.OBSERVE

    async def test_get_gestures_filtered_by_verb(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test filtering gestures by verb."""
        await store.save(sample_garden)

        await store.save_gesture(
            sample_garden.garden_id,
            observe("a", ""),
        )
        await store.save_gesture(
            sample_garden.garden_id,
            graft("b", ""),
        )
        await store.save_gesture(
            sample_garden.garden_id,
            observe("c", ""),
        )

        observe_gestures = await store.get_gestures(
            sample_garden.garden_id, verb=TendingVerb.OBSERVE
        )

        assert len(observe_gestures) == 2
        assert all(g.verb == TendingVerb.OBSERVE for g in observe_gestures)

    async def test_gestures_loaded_with_garden(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that gestures are loaded when loading a garden."""
        await store.save(sample_garden)

        await store.save_gesture(
            sample_garden.garden_id,
            observe("test", "Observation"),
        )

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert len(loaded.recent_gestures) == 1
        assert loaded.recent_gestures[0].verb == TendingVerb.OBSERVE


# =============================================================================
# Plot Tests
# =============================================================================


class TestPlotStorage:
    """Tests for plot persistence."""

    async def test_plots_saved_with_garden(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that plots are saved with garden."""
        extra_plot = create_plot(
            name="extra",
            path="world.extra",
            rigidity=0.8,
        )
        extra_plot.progress = 0.5
        sample_garden.plots["extra"] = extra_plot

        await store.save(sample_garden)

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert "extra" in loaded.plots
        assert loaded.plots["extra"].progress == 0.5
        assert loaded.plots["extra"].rigidity == 0.8

    async def test_update_plot(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test updating a specific plot."""
        await store.save(sample_garden)

        success = await store.update_plot(
            sample_garden.garden_id,
            "test-plot",
            progress=0.75,
            rigidity=0.3,
        )

        assert success

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert loaded.plots["test-plot"].progress == 0.75
        assert loaded.plots["test-plot"].rigidity == 0.3

    async def test_plot_season_override(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test plot season override persists."""
        sample_garden.plots["test-plot"].season_override = GardenSeason.HARVEST
        await store.save(sample_garden)

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert loaded.plots["test-plot"].season_override == GardenSeason.HARVEST


# =============================================================================
# List & Count Tests
# =============================================================================


class TestListAndCount:
    """Tests for listing and counting gardens."""

    async def test_list_gardens(self, store: GardenStore) -> None:
        """Test listing gardens."""
        for i in range(3):
            garden = create_garden(name=f"Garden {i}")
            await store.save(garden)

        gardens = await store.list_gardens()

        assert len(gardens) == 3

    async def test_list_gardens_limit(self, store: GardenStore) -> None:
        """Test list limit."""
        for i in range(5):
            garden = create_garden(name=f"Garden {i}")
            await store.save(garden)

        gardens = await store.list_gardens(limit=2)

        assert len(gardens) == 2

    async def test_count(self, store: GardenStore) -> None:
        """Test counting gardens."""
        assert await store.count() == 0

        garden = create_garden(name="Test")
        await store.save(garden)

        assert await store.count() == 1


# =============================================================================
# Delete Tests
# =============================================================================


class TestDelete:
    """Tests for deleting gardens."""

    async def test_delete_garden(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test deleting a garden."""
        await store.save(sample_garden)
        assert await store.count() == 1

        success = await store.delete(sample_garden.garden_id)

        assert success
        assert await store.count() == 0

    async def test_delete_nonexistent(self, store: GardenStore) -> None:
        """Test deleting non-existent garden returns False."""
        success = await store.delete("nonexistent")
        assert not success

    async def test_delete_clears_default(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that deleting the default garden clears it."""
        await store.save(sample_garden)
        await store.set_default(sample_garden.garden_id)

        await store.delete(sample_garden.garden_id)

        # get_default should create a new garden
        new_default = await store.get_default()
        assert new_default.garden_id != sample_garden.garden_id


# =============================================================================
# Auto-Save Integration Tests
# =============================================================================


class TestAutoSaveIntegration:
    """Tests for auto-save during apply_gesture."""

    async def test_apply_gesture_with_store(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test that apply_gesture auto-saves when store provided."""
        await store.save(sample_garden)

        gesture = observe("world.test", "Testing auto-save")
        result = await apply_gesture(sample_garden, gesture, store=store)

        assert result.accepted

        # Verify gesture was persisted
        gestures = await store.get_gestures(sample_garden.garden_id)
        assert len(gestures) >= 1
        assert any(g.target == "world.test" for g in gestures)

    async def test_apply_gesture_without_store(
        self, sample_garden: GardenState
    ) -> None:
        """Test that apply_gesture works without store."""
        gesture = observe("world.test", "No store")
        result = await apply_gesture(sample_garden, gesture)

        assert result.accepted
        # Should still record in garden momentum
        assert len(sample_garden.recent_gestures) == 1

    async def test_apply_gesture_auto_save_disabled(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test disabling auto-save."""
        await store.save(sample_garden)

        gesture = observe("world.test", "No auto-save")
        result = await apply_gesture(
            sample_garden, gesture, store=store, auto_save=False
        )

        assert result.accepted

        # Gesture should NOT be in store
        gestures = await store.get_gestures(sample_garden.garden_id)
        assert len(gestures) == 0


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactory:
    """Tests for factory functions."""

    def test_create_garden_store_custom_path(self, temp_db_path: Path) -> None:
        """Test creating store with custom path."""
        store = create_garden_store(temp_db_path)
        assert store.db_path == temp_db_path

    def test_create_garden_store_default_path(self) -> None:
        """Test creating store with default path."""
        store = create_garden_store()
        assert "gardener_gardens.db" in str(store.db_path)

    async def test_get_garden_store_singleton(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that get_garden_store returns singleton."""
        reset_garden_store()

        # Use temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            monkeypatch.setenv("XDG_DATA_HOME", tmpdir)

            store1 = await get_garden_store()
            store2 = await get_garden_store()

            assert store1 is store2

        reset_garden_store()


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    async def test_empty_garden_name(self, store: GardenStore) -> None:
        """Test garden with empty name."""
        garden = create_garden(name="")
        await store.save(garden)

        loaded = await store.load(garden.garden_id)
        assert loaded is not None
        assert loaded.name == ""

    async def test_garden_with_no_plots(self, store: GardenStore) -> None:
        """Test garden with no plots."""
        garden = create_garden(name="Empty")
        garden.plots = {}
        await store.save(garden)

        loaded = await store.load(garden.garden_id)
        assert loaded is not None
        assert len(loaded.plots) == 0

    async def test_plot_with_metadata(
        self, store: GardenStore, sample_garden: GardenState
    ) -> None:
        """Test plot with complex metadata."""
        sample_garden.plots["test-plot"].metadata = {
            "key": "value",
            "nested": {"a": 1, "b": 2},
            "list": [1, 2, 3],
        }
        await store.save(sample_garden)

        loaded = await store.load(sample_garden.garden_id)
        assert loaded is not None
        assert loaded.plots["test-plot"].metadata["key"] == "value"
        assert loaded.plots["test-plot"].metadata["nested"]["a"] == 1

    async def test_garden_with_memory_crystals(self, store: GardenStore) -> None:
        """Test garden with memory crystal references."""
        garden = create_garden(name="With Crystals")
        garden.memory_crystals = ["crystal-1", "crystal-2", "crystal-3"]
        await store.save(garden)

        loaded = await store.load(garden.garden_id)
        assert loaded is not None
        assert loaded.memory_crystals == ["crystal-1", "crystal-2", "crystal-3"]

    async def test_concurrent_saves(self, store: GardenStore) -> None:
        """Test concurrent saves don't conflict."""
        garden = create_garden(name="Concurrent")
        await store.save(garden)

        async def save_with_update(n: int) -> None:
            garden.name = f"Update {n}"
            await store.save(garden)

        # Run multiple saves concurrently
        await asyncio.gather(*[save_with_update(i) for i in range(5)])

        # Should not raise, final state should be one of the updates
        loaded = await store.load(garden.garden_id)
        assert loaded is not None
        assert "Update" in loaded.name
