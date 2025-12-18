"""
Tests for SQLPersonaGarden.

SQLPersonaGarden provides PostgreSQL-backed storage for persona patterns
with automatic CDC to Qdrant via the Database Triad.

These tests verify:
- API compatibility with PersonaGarden
- Database operations (plant, nurture, compost, query)
- CDC outbox trigger integration
- Statistics and lifecycle management
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.k.garden import (
    EntryType,
    GardenEntry,
    GardenLifecycle,
    GardenSeason,
    GardenStats,
)
from agents.k.garden_sql import SQLPersonaGarden, close_sql_garden

# =============================================================================
# Mock Database Fixtures
# =============================================================================


class MockConnection:
    """Mock asyncpg connection."""

    def __init__(self) -> None:
        self._data: dict[int, dict[str, Any]] = {}
        self._id_counter = 0

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        """Mock fetch for SELECT queries."""
        results = []
        for row in self._data.values():
            if "WHERE lifecycle" in query:
                if row["lifecycle"] == args[0]:
                    results.append(row)
            elif "WHERE entry_type" in query:
                if row["entry_type"] == args[0]:
                    results.append(row)
            else:
                results.append(row)
        return results

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        """Mock fetchrow for single-row queries."""
        if "INSERT INTO persona_garden" in query:
            self._id_counter += 1
            row = {
                "id": self._id_counter,
                "content": args[0],
                "entry_type": args[1],
                "lifecycle": args[2],
                "confidence": args[3],
                "source": args[4],
                "planted_at": args[5],
                "last_nurtured": args[6],
                "evidence": args[7],
                "occurrences": args[8],
                "tags": args[9],
                "eigenvector_affinities": args[10],
            }
            self._data[self._id_counter] = row
            return row

        if "WHERE id = " in query or "WHERE id =" in query:
            entry_id = args[-1] if isinstance(args[-1], (int, str)) else args[0]
            if isinstance(entry_id, str):
                entry_id = int(entry_id)
            return self._data.get(entry_id)

        if "SELECT" in query and "COUNT" in query:
            # Stats query
            total = len(self._data)
            preferences = sum(1 for r in self._data.values() if r["entry_type"] == "preference")
            patterns = sum(1 for r in self._data.values() if r["entry_type"] == "pattern")
            seeds = sum(1 for r in self._data.values() if r["lifecycle"] == "seed")
            saplings = sum(1 for r in self._data.values() if r["lifecycle"] == "sapling")
            trees = sum(1 for r in self._data.values() if r["lifecycle"] == "tree")
            flowers = sum(1 for r in self._data.values() if r["lifecycle"] == "flower")
            compost = sum(1 for r in self._data.values() if r["lifecycle"] == "compost")
            avg_conf = sum(r["confidence"] for r in self._data.values()) / total if total > 0 else 0

            return {
                "total": total,
                "preferences": preferences,
                "patterns": patterns,
                "values": 0,
                "behaviors": 0,
                "insights": 0,
                "seeds": seeds,
                "saplings": saplings,
                "trees": trees,
                "flowers": flowers,
                "compost": compost,
                "avg_confidence": avg_conf,
                "total_evidence": 0,
                "oldest_days": 0.0,
                "newest_days": 0.0,
                "auto_planted": 0,
            }

        return None

    async def execute(self, query: str, *args: Any) -> None:
        """Mock execute for UPDATE/DELETE."""
        pass


class MockPool:
    """Mock asyncpg connection pool."""

    def __init__(self) -> None:
        self._conn = MockConnection()

    def acquire(self) -> "MockPoolContext":
        return MockPoolContext(self._conn)

    async def close(self) -> None:
        pass


class MockPoolContext:
    """Async context manager for mock pool."""

    def __init__(self, conn: MockConnection) -> None:
        self._conn = conn

    async def __aenter__(self) -> MockConnection:
        return self._conn

    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.fixture
def mock_pool() -> MockPool:
    """Create a mock database pool."""
    return MockPool()


@pytest.fixture
def sql_garden(mock_pool: MockPool) -> SQLPersonaGarden:
    """Create a SQLPersonaGarden with mock pool."""
    return SQLPersonaGarden(pool=mock_pool)


# =============================================================================
# Basic Tests
# =============================================================================


class TestSQLPersonaGardenBasics:
    """Basic tests for SQLPersonaGarden."""

    def test_season_detection(self, sql_garden: SQLPersonaGarden) -> None:
        """Test season is auto-detected."""
        assert sql_garden.season in [
            GardenSeason.SPRING,
            GardenSeason.SUMMER,
            GardenSeason.AUTUMN,
            GardenSeason.WINTER,
        ]

    def test_season_override(self, mock_pool: MockPool) -> None:
        """Test season can be overridden."""
        garden = SQLPersonaGarden(pool=mock_pool, season=GardenSeason.WINTER)
        assert garden.season == GardenSeason.WINTER

    def test_season_setter(self, sql_garden: SQLPersonaGarden) -> None:
        """Test season can be changed."""
        sql_garden.season = GardenSeason.SPRING
        assert sql_garden.season == GardenSeason.SPRING


# =============================================================================
# Planting Tests
# =============================================================================


class TestSQLPersonaGardenPlanting:
    """Tests for planting entries."""

    @pytest.mark.asyncio
    async def test_plant_basic(self, sql_garden: SQLPersonaGarden) -> None:
        """Test planting a basic entry."""
        entry = await sql_garden.plant(
            content="Test pattern",
            entry_type=EntryType.PATTERN,
        )

        assert entry.content == "Test pattern"
        assert entry.entry_type == EntryType.PATTERN
        assert entry.lifecycle == GardenLifecycle.SEED
        assert entry.confidence == 0.3

    @pytest.mark.asyncio
    async def test_plant_preference(self, sql_garden: SQLPersonaGarden) -> None:
        """Test planting a preference."""
        entry = await sql_garden.plant_preference(
            content="Concise communication",
            confidence=0.5,
            tags=["style"],
        )

        assert entry.content == "Concise communication"
        assert entry.entry_type == EntryType.PREFERENCE
        assert entry.confidence == 0.5

    @pytest.mark.asyncio
    async def test_plant_pattern(self, sql_garden: SQLPersonaGarden) -> None:
        """Test planting a pattern."""
        entry = await sql_garden.plant_pattern(
            content="Uses categorical reasoning",
            source="hypnagogia",
            confidence=0.4,
        )

        assert entry.content == "Uses categorical reasoning"
        assert entry.entry_type == EntryType.PATTERN
        assert entry.source == "hypnagogia"

    @pytest.mark.asyncio
    async def test_plant_with_eigenvectors(self, sql_garden: SQLPersonaGarden) -> None:
        """Test planting with eigenvector affinities."""
        affinities = {"categorical": 0.8, "aesthetic": 0.5}
        entry = await sql_garden.plant_pattern(
            content="Mathematical precision",
            eigenvector_affinities=affinities,
        )

        assert entry.eigenvector_affinities == affinities

    @pytest.mark.asyncio
    async def test_plant_lifecycle_by_confidence(self, sql_garden: SQLPersonaGarden) -> None:
        """Test lifecycle is set based on confidence."""
        seed = await sql_garden.plant(
            content="Low confidence",
            entry_type=EntryType.PATTERN,
            confidence=0.2,
        )
        assert seed.lifecycle == GardenLifecycle.SEED

        sapling = await sql_garden.plant(
            content="Medium confidence",
            entry_type=EntryType.PATTERN,
            confidence=0.5,
        )
        assert sapling.lifecycle == GardenLifecycle.SAPLING

        tree = await sql_garden.plant(
            content="High confidence",
            entry_type=EntryType.PATTERN,
            confidence=0.8,
        )
        assert tree.lifecycle == GardenLifecycle.TREE

        flower = await sql_garden.plant(
            content="Peak confidence",
            entry_type=EntryType.PATTERN,
            confidence=0.95,
        )
        assert flower.lifecycle == GardenLifecycle.FLOWER


# =============================================================================
# Query Tests
# =============================================================================


class TestSQLPersonaGardenQueries:
    """Tests for querying entries."""

    @pytest.mark.asyncio
    async def test_get_entry(self, sql_garden: SQLPersonaGarden) -> None:
        """Test getting an entry by ID."""
        planted = await sql_garden.plant_preference("Test preference")
        retrieved = await sql_garden.get(planted.id)

        assert retrieved is not None
        assert retrieved.id == planted.id
        assert retrieved.content == planted.content

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, sql_garden: SQLPersonaGarden) -> None:
        """Test getting a nonexistent entry."""
        result = await sql_garden.get("999999")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_by_type(self, sql_garden: SQLPersonaGarden) -> None:
        """Test listing entries by type."""
        await sql_garden.plant_preference("Pref 1")
        await sql_garden.plant_preference("Pref 2")
        await sql_garden.plant_pattern("Pattern 1")

        preferences = await sql_garden.preferences()
        assert len(preferences) == 2

    @pytest.mark.asyncio
    async def test_list_by_lifecycle(self, sql_garden: SQLPersonaGarden) -> None:
        """Test listing entries by lifecycle."""
        await sql_garden.plant(
            content="Seed entry",
            entry_type=EntryType.PATTERN,
            confidence=0.2,
        )
        await sql_garden.plant(
            content="Tree entry",
            entry_type=EntryType.PATTERN,
            confidence=0.8,
        )

        seeds = await sql_garden.seeds()
        assert len(seeds) == 1
        assert seeds[0].content == "Seed entry"

        trees = await sql_garden.trees()
        assert len(trees) == 1
        assert trees[0].content == "Tree entry"


# =============================================================================
# Statistics Tests
# =============================================================================


class TestSQLPersonaGardenStats:
    """Tests for garden statistics."""

    @pytest.mark.asyncio
    async def test_empty_stats(self, sql_garden: SQLPersonaGarden) -> None:
        """Test stats for empty garden."""
        stats = await sql_garden.stats()
        assert stats.total_entries == 0
        assert stats.average_confidence == 0.0

    @pytest.mark.asyncio
    async def test_stats_with_entries(self, sql_garden: SQLPersonaGarden) -> None:
        """Test stats with entries."""
        await sql_garden.plant_preference("Pref 1", confidence=0.6)
        await sql_garden.plant_pattern("Pattern 1", confidence=0.4)

        stats = await sql_garden.stats()
        assert stats.total_entries == 2
        assert stats.by_type["preference"] == 1
        assert stats.by_type["pattern"] == 1

    @pytest.mark.asyncio
    async def test_stats_season(self, sql_garden: SQLPersonaGarden) -> None:
        """Test stats includes current season."""
        stats = await sql_garden.stats()
        assert stats.current_season in [
            GardenSeason.SPRING,
            GardenSeason.SUMMER,
            GardenSeason.AUTUMN,
            GardenSeason.WINTER,
        ]


# =============================================================================
# Formatting Tests
# =============================================================================


class TestSQLPersonaGardenFormatting:
    """Tests for formatting methods."""

    def test_format_empty_garden(self, sql_garden: SQLPersonaGarden) -> None:
        """Test formatting empty garden."""
        summary = sql_garden.format_summary()
        assert "GARDEN-SQL" in summary

    def test_format_entry(self, sql_garden: SQLPersonaGarden) -> None:
        """Test formatting an entry."""
        entry = GardenEntry(
            id="test_1",
            content="Test pattern",
            entry_type=EntryType.PATTERN,
            lifecycle=GardenLifecycle.TREE,
            confidence=0.8,
        )

        formatted = sql_garden.format_entry(entry)
        assert "Test pattern" in formatted
        assert "T" in formatted  # Tree icon
        assert "80%" in formatted


# =============================================================================
# Lifecycle Helpers Tests
# =============================================================================


class TestSQLPersonaGardenHelpers:
    """Tests for helper methods."""

    def test_confidence_to_lifecycle(self, sql_garden: SQLPersonaGarden) -> None:
        """Test confidence to lifecycle mapping."""
        assert sql_garden._confidence_to_lifecycle(0.1) == GardenLifecycle.SEED
        assert sql_garden._confidence_to_lifecycle(0.3) == GardenLifecycle.SEED
        assert sql_garden._confidence_to_lifecycle(0.5) == GardenLifecycle.SAPLING
        assert sql_garden._confidence_to_lifecycle(0.7) == GardenLifecycle.TREE
        assert sql_garden._confidence_to_lifecycle(0.9) == GardenLifecycle.FLOWER
        assert sql_garden._confidence_to_lifecycle(1.0) == GardenLifecycle.FLOWER

    def test_pattern_maturity_to_confidence(self, sql_garden: SQLPersonaGarden) -> None:
        """Test pattern maturity to confidence mapping."""
        assert sql_garden._pattern_maturity_to_confidence("seed") == 0.3
        assert sql_garden._pattern_maturity_to_confidence("sapling") == 0.5
        assert sql_garden._pattern_maturity_to_confidence("tree") == 0.8
        assert sql_garden._pattern_maturity_to_confidence("compost") == 0.1
        assert sql_garden._pattern_maturity_to_confidence("unknown") == 0.3


# =============================================================================
# API Compatibility Tests
# =============================================================================


class TestSQLPersonaGardenAPICompatibility:
    """Tests verifying API compatibility with PersonaGarden."""

    @pytest.mark.asyncio
    async def test_has_plant_methods(self, sql_garden: SQLPersonaGarden) -> None:
        """Test that plant methods exist."""
        assert hasattr(sql_garden, "plant")
        assert hasattr(sql_garden, "plant_preference")
        assert hasattr(sql_garden, "plant_pattern")

    @pytest.mark.asyncio
    async def test_has_query_methods(self, sql_garden: SQLPersonaGarden) -> None:
        """Test that query methods exist."""
        assert hasattr(sql_garden, "get")
        assert hasattr(sql_garden, "list_by_type")
        assert hasattr(sql_garden, "list_by_lifecycle")
        assert hasattr(sql_garden, "seeds")
        assert hasattr(sql_garden, "saplings")
        assert hasattr(sql_garden, "trees")
        assert hasattr(sql_garden, "flowers")
        assert hasattr(sql_garden, "preferences")
        assert hasattr(sql_garden, "patterns")

    @pytest.mark.asyncio
    async def test_has_lifecycle_methods(self, sql_garden: SQLPersonaGarden) -> None:
        """Test that lifecycle methods exist."""
        assert hasattr(sql_garden, "nurture")
        assert hasattr(sql_garden, "compost")
        assert hasattr(sql_garden, "prune_stale")
        assert hasattr(sql_garden, "staleness_decay")

    @pytest.mark.asyncio
    async def test_has_stats_and_format(self, sql_garden: SQLPersonaGarden) -> None:
        """Test that stats and format methods exist."""
        assert hasattr(sql_garden, "stats")
        assert hasattr(sql_garden, "format_summary")
        assert hasattr(sql_garden, "format_entry")

    @pytest.mark.asyncio
    async def test_has_hypnagogia_integration(self, sql_garden: SQLPersonaGarden) -> None:
        """Test that hypnagogia integration exists."""
        assert hasattr(sql_garden, "sync_from_hypnagogia")
        assert hasattr(sql_garden, "auto_plant_from_dialogue")


# =============================================================================
# Module-Level Tests
# =============================================================================


class TestSQLPersonaGardenModuleFunctions:
    """Tests for module-level functions."""

    @pytest.mark.asyncio
    async def test_close_sql_garden_noop(self) -> None:
        """Test close_sql_garden when no garden exists."""
        # Should not raise
        await close_sql_garden()


# =============================================================================
# CDC Integration Tests
# =============================================================================


class TestSQLPersonaGardenCDC:
    """Tests for CDC/outbox integration conceptually."""

    @pytest.mark.asyncio
    async def test_plant_would_trigger_outbox(self, sql_garden: SQLPersonaGarden) -> None:
        """
        Test that planting would trigger outbox in real DB.

        In a real database, the outbox_trigger function
        would create an INSERT event for CDC.
        """
        entry = await sql_garden.plant_preference("Concise style")

        # Entry created successfully - in real DB this would have:
        # 1. Inserted into persona_garden
        # 2. Triggered outbox_trigger() which inserts into outbox
        # 3. Synapse would poll and sync to Qdrant
        assert entry.id is not None
        assert entry.content == "Concise style"

    @pytest.mark.asyncio
    async def test_entry_has_required_fields_for_cdc(self, sql_garden: SQLPersonaGarden) -> None:
        """Test entry has fields needed for CDC sync."""
        entry = await sql_garden.plant_pattern("Test pattern")

        # These fields are needed by Synapse for CDC
        assert entry.id is not None  # row_id
        assert entry.content is not None  # text_field for embedding
        assert entry.entry_type is not None  # metadata
        assert entry.lifecycle is not None  # metadata
        assert entry.confidence is not None  # metadata


# =============================================================================
# Integration Smoke Tests (Require Real DB)
# =============================================================================


@pytest.mark.skip(reason="Requires running Database Triad")
class TestSQLPersonaGardenIntegration:
    """Integration tests against real PostgreSQL."""

    @pytest.mark.asyncio
    async def test_real_connection(self) -> None:
        """Test connecting to real Database Triad."""
        from agents.k.garden_sql import close_sql_garden, get_sql_garden

        garden = await get_sql_garden()
        assert garden is not None

        # Plant and retrieve
        entry = await garden.plant_preference("Integration test preference")
        retrieved = await garden.get(entry.id)
        assert retrieved is not None
        assert retrieved.content == entry.content

        # Cleanup
        await close_sql_garden()

    @pytest.mark.asyncio
    async def test_cdc_outbox_population(self) -> None:
        """Test that planting populates the outbox table."""
        import asyncpg

        url = "postgresql://triad:triad-dev-password@localhost:5432/triad"
        pool = await asyncpg.create_pool(url)

        try:
            # Get initial outbox count
            async with pool.acquire() as conn:
                initial_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM outbox WHERE table_name = 'persona_garden'"
                )

            # Plant an entry
            from agents.k.garden_sql import SQLPersonaGarden

            garden = SQLPersonaGarden(pool=pool)
            await garden.plant_preference("CDC test entry")

            # Check outbox grew
            async with pool.acquire() as conn:
                new_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM outbox WHERE table_name = 'persona_garden'"
                )

            assert new_count > initial_count

        finally:
            await pool.close()
