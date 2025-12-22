"""
Tests for Extinction Protocol (Memory-First Docs Phase 3).

These tests verify the prepare_extinction() and get_extinct_wisdom() methods
added to BrainPersistence for the Memory-First Documentation protocol.

Laws tested:
1. Extinction Law: Deletion marks teaching as extinct, doesn't delete
2. Successor Chain: Extinction events link to affected teaching
3. Ghost Wisdom: Ancestral wisdom is queryable with context

See: spec/protocols/memory-first-docs.md, plans/memory-first-docs-execution.md
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Base, Crystal, ExtinctionEvent, ExtinctionTeaching, TeachingCrystal
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
    from agents.d import TableAdapter
    from services.brain.persistence import BrainPersistence

    class SessionFactoryWrapper:
        def __init__(self, session):
            self._session = session

        def __call__(self):
            return self

        async def __aenter__(self):
            return self._session

        async def __aexit__(self, *args):
            pass

    table_adapter = TableAdapter(Crystal, SessionFactoryWrapper(db_session))

    return BrainPersistence(
        table_adapter=table_adapter,
        dgent=mock_dgent,
        embedder=None,
    )


# =============================================================================
# Test: prepare_extinction
# =============================================================================


class TestPrepareExtinction:
    """Tests for prepare_extinction() behavior."""

    @pytest.mark.asyncio
    async def test_extinction_creates_event(self, brain_persistence, db_session: AsyncSession):
        """prepare_extinction() creates an ExtinctionEvent."""
        result = await brain_persistence.prepare_extinction(
            reason="Test cleanup",
            commit="abc12345",
            deleted_paths=["services/test/"],
        )

        # Verify result
        assert result.event_id.startswith("ext-abc12345-")
        assert result.reason == "Test cleanup"
        assert result.affected_count == 0  # No teaching to affect yet
        assert result.preserved_count == 0

        # Verify event in database
        event = await db_session.get(ExtinctionEvent, result.event_id)
        assert event is not None
        assert event.reason == "Test cleanup"
        assert event.commit == "abc12345"

    @pytest.mark.asyncio
    async def test_extinction_marks_teaching_as_dead(
        self, brain_persistence, db_session: AsyncSession
    ):
        """prepare_extinction() marks affected teaching crystals with died_at."""
        # First, crystallize some teaching
        await brain_persistence.crystallize_teaching(
            insight="Town gotcha 1",
            severity="warning",
            source_module="services.town.dialogue",
            source_symbol="DialogueService.process",
        )
        await brain_persistence.crystallize_teaching(
            insight="Town gotcha 2",
            severity="critical",
            source_module="services.town.citizens",
            source_symbol="CitizenManager.spawn",
        )
        await brain_persistence.crystallize_teaching(
            insight="Brain gotcha",
            severity="info",
            source_module="services.brain.persistence",
            source_symbol="BrainPersistence.capture",
        )

        # Prepare extinction for town
        result = await brain_persistence.prepare_extinction(
            reason="Crown Jewel Cleanup",
            commit="12345678",
            deleted_paths=["services/town/"],
        )

        # Verify affected teaching
        assert result.affected_count == 2
        assert result.preserved_count == 2

        # Verify they're marked dead
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.source_module.startswith("services.town")
        )
        res = await db_session.execute(stmt)
        town_teaching = res.scalars().all()

        for teaching in town_teaching:
            assert teaching.died_at is not None
            assert teaching.is_alive is False
            assert teaching.is_ancestor is True

        # Brain teaching should still be alive
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.source_module.startswith("services.brain")
        )
        res = await db_session.execute(stmt)
        brain_teaching = res.scalars().all()
        assert len(brain_teaching) == 1
        assert brain_teaching[0].is_alive is True

    @pytest.mark.asyncio
    async def test_path_to_module_conversion(self, brain_persistence, db_session: AsyncSession):
        """prepare_extinction() converts filesystem paths to module prefixes."""
        # Teaching uses dots, paths use slashes
        await brain_persistence.crystallize_teaching(
            insight="Deep nested gotcha",
            severity="info",
            source_module="services.town.submodule.deep",
            source_symbol="DeepClass.method",
        )

        result = await brain_persistence.prepare_extinction(
            reason="Test",
            commit="testtest",
            deleted_paths=["services/town/submodule/"],  # With trailing slash
        )

        assert result.affected_count == 1

    @pytest.mark.asyncio
    async def test_successor_map_applied(self, brain_persistence, db_session: AsyncSession):
        """prepare_extinction() applies successor_map to affected teaching."""
        await brain_persistence.crystallize_teaching(
            insight="Chat gotcha",
            severity="warning",
            source_module="services.chat.handler",
            source_symbol="ChatHandler.process",
        )

        result = await brain_persistence.prepare_extinction(
            reason="Chat migration",
            commit="migr1234",
            deleted_paths=["services/chat/"],
            successor_map={
                "services/chat": "services.brain.conversation",
            },
        )

        # Verify successor was set
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.source_module.startswith("services.chat")
        )
        res = await db_session.execute(stmt)
        teaching = res.scalars().first()

        assert teaching is not None
        assert teaching.successor_module == "services.brain.conversation"

    @pytest.mark.asyncio
    async def test_extinction_links_created(self, brain_persistence, db_session: AsyncSession):
        """prepare_extinction() creates ExtinctionTeaching links."""
        await brain_persistence.crystallize_teaching(
            insight="Link test gotcha",
            severity="info",
            source_module="services.linktest.module",
            source_symbol="TestClass.method",
        )

        result = await brain_persistence.prepare_extinction(
            reason="Link test",
            commit="link1234",
            deleted_paths=["services/linktest/"],
        )

        # Verify link was created
        stmt = select(ExtinctionTeaching).where(ExtinctionTeaching.extinction_id == result.event_id)
        res = await db_session.execute(stmt)
        links = res.scalars().all()

        assert len(links) == 1


# =============================================================================
# Test: get_extinct_wisdom
# =============================================================================


class TestGetExtinctWisdom:
    """Tests for get_extinct_wisdom() behavior."""

    @pytest.mark.asyncio
    async def test_get_extinct_wisdom_returns_ghosts(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_extinct_wisdom() returns teaching from deleted code."""
        # Create and extinct some teaching
        await brain_persistence.crystallize_teaching(
            insight="Extinct wisdom 1",
            severity="warning",
            source_module="services.old.module1",
            source_symbol="OldClass.method1",
        )
        await brain_persistence.crystallize_teaching(
            insight="Extinct wisdom 2",
            severity="critical",
            source_module="services.old.module2",
            source_symbol="OldClass.method2",
        )

        await brain_persistence.prepare_extinction(
            reason="Test extinction",
            commit="dead1234",
            deleted_paths=["services/old/"],
        )

        # Query ghost wisdom
        ghosts = await brain_persistence.get_extinct_wisdom()

        assert len(ghosts) == 2
        assert all(g.teaching.is_ancestor for g in ghosts)

    @pytest.mark.asyncio
    async def test_ghost_wisdom_includes_event_context(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_extinct_wisdom() includes extinction event context."""
        await brain_persistence.crystallize_teaching(
            insight="Context test",
            severity="info",
            source_module="services.ctx.test",
            source_symbol="ContextClass.method",
        )

        result = await brain_persistence.prepare_extinction(
            reason="Context test cleanup",
            commit="ctx12345",
            deleted_paths=["services/ctx/"],
            decision_doc="spec/test.md",
        )

        ghosts = await brain_persistence.get_extinct_wisdom()

        assert len(ghosts) == 1
        assert ghosts[0].extinction_event is not None
        assert ghosts[0].extinction_event.reason == "Context test cleanup"
        assert ghosts[0].extinction_event.decision_doc == "spec/test.md"

    @pytest.mark.asyncio
    async def test_ghost_wisdom_keyword_filtering(
        self, brain_persistence, db_session: AsyncSession
    ):
        """get_extinct_wisdom() filters by keywords."""
        await brain_persistence.crystallize_teaching(
            insight="Always validate input parameters",
            severity="critical",
            source_module="services.filter.a",
            source_symbol="A.method",
        )
        await brain_persistence.crystallize_teaching(
            insight="Use caching for performance",
            severity="info",
            source_module="services.filter.b",
            source_symbol="B.method",
        )

        await brain_persistence.prepare_extinction(
            reason="Filter test",
            commit="flt12345",
            deleted_paths=["services/filter/"],
        )

        # Filter by keyword
        ghosts = await brain_persistence.get_extinct_wisdom(keywords=["validate"])

        assert len(ghosts) == 1
        assert "validate" in ghosts[0].teaching.insight.lower()

    @pytest.mark.asyncio
    async def test_ghost_wisdom_module_filtering(self, brain_persistence, db_session: AsyncSession):
        """get_extinct_wisdom() filters by module prefix."""
        await brain_persistence.crystallize_teaching(
            insight="Town A gotcha",
            severity="info",
            source_module="services.town.a",
            source_symbol="A.method",
        )
        await brain_persistence.crystallize_teaching(
            insight="Park B gotcha",
            severity="info",
            source_module="services.park.b",
            source_symbol="B.method",
        )

        await brain_persistence.prepare_extinction(
            reason="Multi-module test",
            commit="multi123",
            deleted_paths=["services/town/", "services/park/"],
        )

        # Filter by module
        ghosts = await brain_persistence.get_extinct_wisdom(module_prefix="services.town")

        assert len(ghosts) == 1
        assert ghosts[0].teaching.source_module.startswith("services.town")


# =============================================================================
# Test: get_extinction_events
# =============================================================================


class TestGetExtinctionEvents:
    """Tests for get_extinction_events() behavior."""

    @pytest.mark.asyncio
    async def test_list_extinction_events(self, brain_persistence, db_session: AsyncSession):
        """get_extinction_events() lists all extinction events."""
        # Create multiple events
        await brain_persistence.prepare_extinction(
            reason="Event 1",
            commit="event001",
            deleted_paths=["services/e1/"],
        )
        await brain_persistence.prepare_extinction(
            reason="Event 2",
            commit="event002",
            deleted_paths=["services/e2/"],
        )

        events = await brain_persistence.get_extinction_events()

        assert len(events) == 2

    @pytest.mark.asyncio
    async def test_get_specific_event(self, brain_persistence, db_session: AsyncSession):
        """get_extinction_event() retrieves a specific event."""
        result = await brain_persistence.prepare_extinction(
            reason="Specific event",
            commit="spec1234",
            deleted_paths=["services/spec/"],
            decision_doc="spec/specific.md",
        )

        event = await brain_persistence.get_extinction_event(result.event_id)

        assert event is not None
        assert event.id == result.event_id
        assert event.reason == "Specific event"
        assert event.decision_doc == "spec/specific.md"


__all__ = [
    "TestPrepareExtinction",
    "TestGetExtinctWisdom",
    "TestGetExtinctionEvents",
]
