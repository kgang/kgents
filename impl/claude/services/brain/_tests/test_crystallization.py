"""
Tests for Teaching Crystal crystallization.

These tests verify the crystallize_teaching() methods added to BrainPersistence
for the Memory-First Documentation protocol.

Laws tested:
1. Persistence Law: Teaching moments MUST be crystallizable
2. Deduplication: Same (module, symbol, insight hash) → same teaching_id
3. Query patterns for hydration

See: spec/protocols/memory-first-docs.md
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, Crystal, TeachingCrystal
from models.base import get_engine


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database session for testing."""
    engine = get_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_dgent():
    """Create a mock D-gent protocol."""
    dgent = MagicMock()
    dgent.put = AsyncMock(return_value="datum-123")
    dgent.get = AsyncMock(return_value=None)
    dgent.delete = AsyncMock(return_value=True)
    return dgent


@pytest.fixture
async def brain_persistence(db_session: AsyncSession, mock_dgent):
    """Create a BrainPersistence instance with real DB session and mock D-gent."""
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from agents.d import TableAdapter
    from services.brain.persistence import BrainPersistence

    # Create a session factory from the existing session's engine
    engine = db_session.get_bind()

    # Wrap the existing session in a factory-like context manager
    class SessionFactoryWrapper:
        def __init__(self, session):
            self._session = session

        def __call__(self):
            return self

        async def __aenter__(self):
            return self._session

        async def __aexit__(self, *args):
            pass

    # Create TableAdapter with session factory
    table_adapter = TableAdapter(Crystal, SessionFactoryWrapper(db_session))

    return BrainPersistence(
        table_adapter=table_adapter,
        dgent=mock_dgent,
        embedder=None,
    )


# =============================================================================
# Test: crystallize_teaching
# =============================================================================


class TestCrystallizeTeaching:
    """Tests for crystallize_teaching() behavior."""

    @pytest.mark.asyncio
    async def test_crystallize_creates_teaching_crystal(
        self, brain_persistence, db_session: AsyncSession
    ):
        """crystallize_teaching() creates a TeachingCrystal in the database."""
        result = await brain_persistence.crystallize_teaching(
            insight="Always validate input before processing",
            severity="critical",
            source_module="services.brain.persistence",
            source_symbol="BrainPersistence.capture",
            evidence="test_persistence.py::test_capture",
        )

        # Verify result
        assert result.is_new is True
        assert result.evidence_verified is True
        assert result.severity == "critical"
        assert result.teaching_id.startswith("t-")
        assert len(result.teaching_id) == 52  # "t-" + 50 char hash

        # Verify it's in the database
        crystal = await db_session.get(TeachingCrystal, result.teaching_id)
        assert crystal is not None
        assert crystal.insight == "Always validate input before processing"
        assert crystal.source_module == "services.brain.persistence"
        assert crystal.is_alive is True

    @pytest.mark.asyncio
    async def test_crystallize_deduplication(
        self, brain_persistence, db_session: AsyncSession
    ):
        """Same (module, symbol, insight) returns existing crystal."""
        # First crystallization
        result1 = await brain_persistence.crystallize_teaching(
            insight="Duplicate gotcha",
            severity="warning",
            source_module="services.test",
            source_symbol="TestClass.method",
        )

        # Second crystallization with same parameters
        result2 = await brain_persistence.crystallize_teaching(
            insight="Duplicate gotcha",
            severity="warning",
            source_module="services.test",
            source_symbol="TestClass.method",
        )

        # Should return the same ID
        assert result1.teaching_id == result2.teaching_id
        assert result1.is_new is True
        assert result2.is_new is False

        # Only one crystal in DB
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.source_module == "services.test"
        )
        results = await db_session.execute(stmt)
        crystals = results.scalars().all()
        assert len(crystals) == 1

    @pytest.mark.asyncio
    async def test_crystallize_different_insights_different_ids(
        self, brain_persistence, db_session: AsyncSession
    ):
        """Different insights from same symbol get different IDs."""
        result1 = await brain_persistence.crystallize_teaching(
            insight="First gotcha",
            severity="info",
            source_module="services.test",
            source_symbol="TestClass.method",
        )

        result2 = await brain_persistence.crystallize_teaching(
            insight="Second gotcha",
            severity="info",
            source_module="services.test",
            source_symbol="TestClass.method",
        )

        assert result1.teaching_id != result2.teaching_id
        assert result1.is_new is True
        assert result2.is_new is True

    @pytest.mark.asyncio
    async def test_crystallize_without_evidence(
        self, brain_persistence, db_session: AsyncSession
    ):
        """Crystallization works without evidence, but marks as unverified."""
        result = await brain_persistence.crystallize_teaching(
            insight="Gotcha without proof",
            severity="info",
            source_module="services.test",
            source_symbol="unverified",
        )

        assert result.is_new is True
        assert result.evidence_verified is False


# =============================================================================
# Test: Query Methods
# =============================================================================


class TestTeachingQueries:
    """Tests for teaching crystal query methods."""

    @pytest.mark.asyncio
    async def test_get_alive_teaching(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_alive_teaching() returns only living crystals."""
        # Create alive crystals
        await brain_persistence.crystallize_teaching(
            insight="Alive 1",
            severity="warning",
            source_module="services.test",
            source_symbol="alive1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Alive 2",
            severity="critical",
            source_module="services.test",
            source_symbol="alive2",
        )

        # Create a dead crystal directly
        dead = TeachingCrystal(
            id="dead-001",
            insight="Dead gotcha",
            severity="info",
            source_module="services.old",
            source_symbol="deleted",
            died_at=datetime.now(UTC),
        )
        db_session.add(dead)
        await db_session.commit()

        # Query alive teaching
        alive = await brain_persistence.get_alive_teaching()

        assert len(alive) == 2
        assert all(t.is_alive for t in alive)

    @pytest.mark.asyncio
    async def test_get_alive_teaching_by_severity(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_alive_teaching() can filter by severity."""
        await brain_persistence.crystallize_teaching(
            insight="Critical 1",
            severity="critical",
            source_module="services.test",
            source_symbol="crit1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Warning 1",
            severity="warning",
            source_module="services.test",
            source_symbol="warn1",
        )

        critical = await brain_persistence.get_alive_teaching(severity="critical")

        assert len(critical) == 1
        assert critical[0].severity == "critical"

    @pytest.mark.asyncio
    async def test_get_teaching_by_module(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_teaching_by_module() finds crystals by module prefix."""
        await brain_persistence.crystallize_teaching(
            insight="Brain gotcha",
            severity="warning",
            source_module="services.brain.persistence",
            source_symbol="method1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Brain core gotcha",
            severity="info",
            source_module="services.brain.core",
            source_symbol="method2",
        )
        await brain_persistence.crystallize_teaching(
            insight="Other gotcha",
            severity="info",
            source_module="services.town.dialogue",
            source_symbol="method3",
        )

        brain_teaching = await brain_persistence.get_teaching_by_module("services.brain")

        assert len(brain_teaching) == 2
        assert all("services.brain" in t.source_module for t in brain_teaching)

    @pytest.mark.asyncio
    async def test_get_ancestral_wisdom(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_ancestral_wisdom() returns teaching from deleted code."""
        # Create alive crystal
        await brain_persistence.crystallize_teaching(
            insight="Alive wisdom",
            severity="info",
            source_module="services.current",
            source_symbol="active",
        )

        # Create dead crystals
        dead1 = TeachingCrystal(
            id="ancestor-001",
            insight="Old wisdom 1",
            severity="warning",
            source_module="services.old.module1",
            source_symbol="deleted1",
            died_at=datetime.now(UTC),
        )
        dead2 = TeachingCrystal(
            id="ancestor-002",
            insight="Old wisdom 2",
            severity="critical",
            source_module="services.old.module2",
            source_symbol="deleted2",
            died_at=datetime.now(UTC),
        )
        db_session.add_all([dead1, dead2])
        await db_session.commit()

        # Query ancestors
        ancestors = await brain_persistence.get_ancestral_wisdom()

        assert len(ancestors) == 2
        assert all(a.is_ancestor for a in ancestors)

    @pytest.mark.asyncio
    async def test_count_teaching_crystals(
        self, brain_persistence, db_session: AsyncSession
    ):
        """count_teaching_crystals() returns accurate stats."""
        # Create alive crystals of different severities
        await brain_persistence.crystallize_teaching(
            insight="Critical 1",
            severity="critical",
            source_module="services.test",
            source_symbol="crit1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Warning 1",
            severity="warning",
            source_module="services.test",
            source_symbol="warn1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Info 1",
            severity="info",
            source_module="services.test",
            source_symbol="info1",
        )

        # Create dead crystal
        dead = TeachingCrystal(
            id="count-dead",
            insight="Dead gotcha",
            severity="warning",
            source_module="services.old",
            source_symbol="dead",
            died_at=datetime.now(UTC),
        )
        db_session.add(dead)
        await db_session.commit()

        counts = await brain_persistence.count_teaching_crystals()

        assert counts["total"] == 4
        assert counts["alive"] == 3
        assert counts["extinct"] == 1
        assert counts["critical"] == 1
        assert counts["warning"] == 1
        assert counts["info"] == 1


# =============================================================================
# Test: Crystallizer Module
# =============================================================================


class TestTeachingCrystallizer:
    """Tests for the TeachingCrystallizer high-level API."""

    @pytest.mark.asyncio
    async def test_crystallizer_stats(
        self, brain_persistence, db_session: AsyncSession
    ):
        """TeachingCrystallizer tracks crystallization stats."""
        from services.living_docs.crystallizer import TeachingCrystallizer
        from services.living_docs.teaching import TeachingCollector

        # Create a mock collector with fixed results
        mock_collector = MagicMock(spec=TeachingCollector)

        # Create mock teaching moments
        from services.living_docs.types import TeachingMoment

        mock_results = [
            MagicMock(
                moment=TeachingMoment(insight="Gotcha 1", severity="critical", evidence="test.py::test_1"),
                symbol="Symbol1",
                module="services.test",
            ),
            MagicMock(
                moment=TeachingMoment(insight="Gotcha 2", severity="warning", evidence=None),
                symbol="Symbol2",
                module="services.test",
            ),
        ]
        mock_collector.collect_all.return_value = iter(mock_results)

        crystallizer = TeachingCrystallizer(
            brain=brain_persistence,
            collector=mock_collector,
        )

        stats = await crystallizer.crystallize_all()

        assert stats.total_found == 2
        assert stats.newly_crystallized == 2
        assert stats.with_evidence == 1
        assert stats.by_severity["critical"] == 1
        assert stats.by_severity["warning"] == 1


__all__ = [
    "TestCrystallizeTeaching",
    "TestTeachingQueries",
    "TestTeachingCrystallizer",
]
