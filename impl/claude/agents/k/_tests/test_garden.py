"""
Tests for PersonaGarden.

PersonaGarden stores persona patterns, preferences, and observed behaviors
using the garden metaphor (SEED → SAPLING → TREE → FLOWER → COMPOST).
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from agents.k.garden import (
    EntryType,
    GardenEntry,
    GardenLifecycle,
    GardenStats,
    PersonaGarden,
    get_garden,
    set_garden,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_garden() -> Generator[PersonaGarden, None, None]:
    """Create a garden with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        garden = PersonaGarden(storage_path=Path(tmpdir) / "garden")
        yield garden


@pytest.fixture
def empty_garden() -> PersonaGarden:
    """Create an in-memory garden (no persistence)."""
    garden = PersonaGarden(storage_path=Path("/tmp/test_garden_empty"), auto_save=False)
    return garden


# =============================================================================
# Basic Tests
# =============================================================================


class TestGardenEntry:
    """Tests for GardenEntry dataclass."""

    def test_entry_creation(self) -> None:
        """Test creating a garden entry."""
        entry = GardenEntry(
            id="test_1",
            content="Test pattern",
            entry_type=EntryType.PATTERN,
        )
        assert entry.id == "test_1"
        assert entry.content == "Test pattern"
        assert entry.entry_type == EntryType.PATTERN
        assert entry.lifecycle == GardenLifecycle.SEED
        assert entry.confidence == 0.3

    def test_entry_age(self) -> None:
        """Test entry age calculation."""
        entry = GardenEntry(
            id="test_1",
            content="Test",
            entry_type=EntryType.PATTERN,
            planted_at=datetime.now(timezone.utc),
        )
        assert entry.age_days < 0.01  # Just created

    def test_entry_serialization(self) -> None:
        """Test entry to_dict and from_dict."""
        entry = GardenEntry(
            id="test_1",
            content="Test pattern",
            entry_type=EntryType.PREFERENCE,
            lifecycle=GardenLifecycle.TREE,
            confidence=0.8,
            evidence=["ev1", "ev2"],
            tags=["category"],
        )

        data = entry.to_dict()
        restored = GardenEntry.from_dict(data)

        assert restored.id == entry.id
        assert restored.content == entry.content
        assert restored.entry_type == entry.entry_type
        assert restored.lifecycle == entry.lifecycle
        assert restored.confidence == entry.confidence
        assert restored.evidence == entry.evidence
        assert restored.tags == entry.tags


# =============================================================================
# Garden Operations
# =============================================================================


class TestGardenPlanting:
    """Tests for planting entries."""

    @pytest.mark.asyncio
    async def test_plant_preference(self, empty_garden: PersonaGarden) -> None:
        """Test planting a preference."""
        entry = await empty_garden.plant_preference(
            content="Prefer concise communication",
            confidence=0.6,
            tags=["communication"],
        )

        assert entry.entry_type == EntryType.PREFERENCE
        assert entry.content == "Prefer concise communication"
        assert entry.lifecycle == GardenLifecycle.SAPLING  # 0.6 confidence
        assert "communication" in entry.tags

    @pytest.mark.asyncio
    async def test_plant_pattern(self, empty_garden: PersonaGarden) -> None:
        """Test planting a pattern."""
        entry = await empty_garden.plant_pattern(
            content="Asks clarifying questions before answering",
            source="hypnagogia",
            confidence=0.3,
            eigenvector_affinities={"categorical": 0.7},
        )

        assert entry.entry_type == EntryType.PATTERN
        assert entry.source == "hypnagogia"
        assert entry.eigenvector_affinities["categorical"] == 0.7

    @pytest.mark.asyncio
    async def test_plant_multiple(self, empty_garden: PersonaGarden) -> None:
        """Test planting multiple entries."""
        await empty_garden.plant_preference("Pref 1")
        await empty_garden.plant_preference("Pref 2")
        await empty_garden.plant_pattern("Pattern 1")

        assert len(empty_garden.entries) == 3


class TestGardenNurturing:
    """Tests for nurturing entries."""

    @pytest.mark.asyncio
    async def test_nurture_increases_confidence(
        self, empty_garden: PersonaGarden
    ) -> None:
        """Test that nurturing increases confidence."""
        entry = await empty_garden.plant_preference("Test", confidence=0.3)
        original_confidence = entry.confidence

        updated = await empty_garden.nurture(entry.id, "Evidence 1")

        assert updated is not None
        assert updated.confidence > original_confidence
        assert "Evidence 1" in updated.evidence

    @pytest.mark.asyncio
    async def test_nurture_promotes_lifecycle(
        self, empty_garden: PersonaGarden
    ) -> None:
        """Test that nurturing can promote lifecycle."""
        entry = await empty_garden.plant_preference("Test", confidence=0.38)
        assert entry.lifecycle == GardenLifecycle.SEED

        # Nurture with enough boost to cross threshold
        updated = await empty_garden.nurture(
            entry.id, "Strong evidence", confidence_boost=0.1
        )

        assert updated is not None
        assert updated.lifecycle == GardenLifecycle.SAPLING

    @pytest.mark.asyncio
    async def test_nurture_nonexistent(self, empty_garden: PersonaGarden) -> None:
        """Test nurturing nonexistent entry returns None."""
        result = await empty_garden.nurture("nonexistent", "Evidence")
        assert result is None


class TestGardenComposting:
    """Tests for composting entries."""

    @pytest.mark.asyncio
    async def test_compost_entry(self, empty_garden: PersonaGarden) -> None:
        """Test composting an entry."""
        entry = await empty_garden.plant_preference("Old pattern")
        composted = await empty_garden.compost(entry.id)

        assert composted is not None
        assert composted.lifecycle == GardenLifecycle.COMPOST

    @pytest.mark.asyncio
    async def test_prune_stale(self, empty_garden: PersonaGarden) -> None:
        """Test pruning stale entries."""
        # Create entry with old last_nurtured
        entry = await empty_garden.plant_preference("Old")
        # Manually set old timestamp
        entry.last_nurtured = datetime(2020, 1, 1, tzinfo=timezone.utc)

        composted = await empty_garden.prune_stale(days_threshold=30)

        assert len(composted) == 1
        assert composted[0].lifecycle == GardenLifecycle.COMPOST


class TestGardenQuerying:
    """Tests for querying the garden."""

    @pytest.mark.asyncio
    async def test_list_by_type(self, empty_garden: PersonaGarden) -> None:
        """Test listing entries by type."""
        await empty_garden.plant_preference("Pref 1")
        await empty_garden.plant_preference("Pref 2")
        await empty_garden.plant_pattern("Pattern 1")

        preferences = await empty_garden.list_by_type(EntryType.PREFERENCE)
        patterns = await empty_garden.list_by_type(EntryType.PATTERN)

        assert len(preferences) == 2
        assert len(patterns) == 1

    @pytest.mark.asyncio
    async def test_list_by_lifecycle(self, empty_garden: PersonaGarden) -> None:
        """Test listing entries by lifecycle."""
        await empty_garden.plant_preference("Seed", confidence=0.2)
        await empty_garden.plant_preference("Tree", confidence=0.75)
        await empty_garden.plant_preference("Flower", confidence=0.95)

        seeds = await empty_garden.seeds()
        trees = await empty_garden.trees()
        flowers = await empty_garden.flowers()

        assert len(seeds) == 1
        assert len(trees) == 1
        assert len(flowers) == 1

    @pytest.mark.asyncio
    async def test_convenience_methods(self, empty_garden: PersonaGarden) -> None:
        """Test convenience query methods."""
        await empty_garden.plant_preference("Pref")
        await empty_garden.plant_pattern("Pattern")

        preferences = await empty_garden.preferences()
        patterns = await empty_garden.patterns()

        assert len(preferences) == 1
        assert len(patterns) == 1


class TestGardenStats:
    """Tests for garden statistics."""

    @pytest.mark.asyncio
    async def test_empty_stats(self, empty_garden: PersonaGarden) -> None:
        """Test stats on empty garden."""
        stats = await empty_garden.stats()

        assert stats.total_entries == 0
        assert stats.average_confidence == 0.0

    @pytest.mark.asyncio
    async def test_stats_with_entries(self, empty_garden: PersonaGarden) -> None:
        """Test stats with entries."""
        await empty_garden.plant_preference("Pref 1", confidence=0.5)
        await empty_garden.plant_preference("Pref 2", confidence=0.7)
        await empty_garden.plant_pattern("Pattern", confidence=0.6)

        stats = await empty_garden.stats()

        assert stats.total_entries == 3
        assert stats.by_type["preference"] == 2
        assert stats.by_type["pattern"] == 1
        assert 0.5 < stats.average_confidence < 0.7


class TestGardenPersistence:
    """Tests for garden persistence."""

    @pytest.mark.asyncio
    async def test_save_and_load(self) -> None:
        """Test saving and loading garden."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "garden"

            # Create and populate
            garden1 = PersonaGarden(storage_path=path)
            await garden1.plant_preference("Persistent pref", confidence=0.7)
            await garden1.plant_pattern("Persistent pattern")

            # Create new instance (should load from disk)
            garden2 = PersonaGarden(storage_path=path)

            assert len(garden2.entries) == 2

            # Verify content
            prefs = await garden2.preferences()
            assert len(prefs) == 1
            assert prefs[0].content == "Persistent pref"


class TestGardenFormatting:
    """Tests for garden formatting."""

    @pytest.mark.asyncio
    async def test_format_summary_empty(self, empty_garden: PersonaGarden) -> None:
        """Test formatting empty garden."""
        summary = empty_garden.format_summary()
        assert "Empty" in summary

    @pytest.mark.asyncio
    async def test_format_summary_with_entries(
        self, empty_garden: PersonaGarden
    ) -> None:
        """Test formatting garden with entries."""
        await empty_garden.plant_preference("Test pref", confidence=0.75)
        await empty_garden.plant_pattern("Test pattern", confidence=0.3)

        summary = empty_garden.format_summary()

        assert "PersonaGarden Summary" in summary
        assert "Total entries: 2" in summary
        assert "tree" in summary.lower()
        assert "seed" in summary.lower()

    def test_format_entry(self, empty_garden: PersonaGarden) -> None:
        """Test formatting a single entry."""
        entry = GardenEntry(
            id="test_1",
            content="Test content",
            entry_type=EntryType.PREFERENCE,
            lifecycle=GardenLifecycle.TREE,
            confidence=0.8,
            source="manual",
        )

        formatted = empty_garden.format_entry(entry)

        assert "T" in formatted  # Tree icon
        assert "Test content" in formatted
        assert "80%" in formatted


# =============================================================================
# Module-Level Functions
# =============================================================================


class TestGardenModule:
    """Tests for module-level functions."""

    def test_get_garden_singleton(self) -> None:
        """Test that get_garden returns a singleton."""
        garden1 = get_garden()
        garden2 = get_garden()
        assert garden1 is garden2

    def test_set_garden(self, empty_garden: PersonaGarden) -> None:
        """Test setting custom garden instance."""
        set_garden(empty_garden)
        assert get_garden() is empty_garden


# =============================================================================
# Lifecycle Transitions
# =============================================================================


class TestLifecycleTransitions:
    """Tests for lifecycle state machine."""

    @pytest.mark.asyncio
    async def test_seed_to_sapling(self, empty_garden: PersonaGarden) -> None:
        """Test SEED → SAPLING transition."""
        entry = await empty_garden.plant_preference("Test", confidence=0.35)
        assert entry.lifecycle == GardenLifecycle.SEED

        # Nurture past 0.4 threshold
        await empty_garden.nurture(entry.id, "ev1", confidence_boost=0.1)
        updated = await empty_garden.get(entry.id)

        assert updated is not None
        assert updated.lifecycle == GardenLifecycle.SAPLING

    @pytest.mark.asyncio
    async def test_sapling_to_tree(self, empty_garden: PersonaGarden) -> None:
        """Test SAPLING → TREE transition."""
        entry = await empty_garden.plant_preference("Test", confidence=0.65)
        assert entry.lifecycle == GardenLifecycle.SAPLING

        # Nurture past 0.7 threshold
        await empty_garden.nurture(entry.id, "ev1", confidence_boost=0.1)
        updated = await empty_garden.get(entry.id)

        assert updated is not None
        assert updated.lifecycle == GardenLifecycle.TREE

    @pytest.mark.asyncio
    async def test_tree_to_flower(self, empty_garden: PersonaGarden) -> None:
        """Test TREE → FLOWER transition."""
        entry = await empty_garden.plant_preference("Test", confidence=0.85)
        assert entry.lifecycle == GardenLifecycle.TREE

        # Nurture past 0.9 threshold
        await empty_garden.nurture(entry.id, "ev1", confidence_boost=0.1)
        updated = await empty_garden.get(entry.id)

        assert updated is not None
        assert updated.lifecycle == GardenLifecycle.FLOWER


# =============================================================================
# Entry Types
# =============================================================================


class TestEntryTypes:
    """Tests for different entry types."""

    @pytest.mark.asyncio
    async def test_all_entry_types(self, empty_garden: PersonaGarden) -> None:
        """Test planting all entry types."""
        await empty_garden.plant(
            content="Preference",
            entry_type=EntryType.PREFERENCE,
        )
        await empty_garden.plant(
            content="Pattern",
            entry_type=EntryType.PATTERN,
        )
        await empty_garden.plant(
            content="Value",
            entry_type=EntryType.VALUE,
        )
        await empty_garden.plant(
            content="Behavior",
            entry_type=EntryType.BEHAVIOR,
        )
        await empty_garden.plant(
            content="Insight",
            entry_type=EntryType.INSIGHT,
        )

        stats = await empty_garden.stats()
        assert stats.total_entries == 5
        assert len(stats.by_type) == 5
