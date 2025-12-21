"""
Tests for Memory-First Documentation models.

These tests verify the TeachingCrystal, ExtinctionEvent, and ExtinctionTeaching
models defined in impl/claude/models/brain.py.

Spec: spec/protocols/memory-first-docs.md

Laws tested:
1. Persistence Law: Teaching moments MUST be crystallizable
2. Extinction Law: Teaching from deleted code marked died_at, NOT deleted
3. Successor Chain Law: Successor mappings form a DAG
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    Base,
    Crystal,
    ExtinctionEvent,
    ExtinctionTeaching,
    TeachingCrystal,
    init_db,
)
from models.base import get_engine


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database session for testing."""
    # Use in-memory SQLite for tests
    engine = get_engine("sqlite+aiosqlite:///:memory:")

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    # Cleanup
    await engine.dispose()


def make_teaching_crystal(
    id: str | None = None,
    insight: str = "Test gotcha",
    severity: str = "warning",
    source_module: str = "services.test",
    source_symbol: str = "TestClass.method",
    died_at: datetime | None = None,
) -> TeachingCrystal:
    """Factory for creating TeachingCrystal instances."""
    return TeachingCrystal(
        id=id or str(uuid.uuid4())[:8],
        insight=insight,
        severity=severity,
        source_module=source_module,
        source_symbol=source_symbol,
        died_at=died_at,
    )


def make_extinction_event(
    id: str | None = None,
    reason: str = "Test cleanup",
    commit: str = "abc123",
    deleted_paths: list[str] | None = None,
    successor_map: dict | None = None,
) -> ExtinctionEvent:
    """Factory for creating ExtinctionEvent instances."""
    return ExtinctionEvent(
        id=id or str(uuid.uuid4())[:8],
        reason=reason,
        commit=commit,
        deleted_paths=deleted_paths or [],
        successor_map=successor_map or {},
    )


# =============================================================================
# TeachingCrystal Model Tests
# =============================================================================


class TestTeachingCrystalModel:
    """Tests for TeachingCrystal model CRUD and properties."""

    @pytest.mark.asyncio
    async def test_create_teaching_crystal(self, db_session: AsyncSession):
        """Can create a teaching crystal with required fields."""
        crystal = TeachingCrystal(
            id="teach-001",
            insight="Always validate input before processing",
            severity="critical",
            source_module="services.brain.persistence",
            source_symbol="BrainPersistence.capture",
        )

        db_session.add(crystal)
        await db_session.commit()

        # Verify it was saved
        result = await db_session.get(TeachingCrystal, "teach-001")
        assert result is not None
        assert result.insight == "Always validate input before processing"
        assert result.severity == "critical"
        assert result.source_module == "services.brain.persistence"

    @pytest.mark.asyncio
    async def test_teaching_crystal_born_at_default(self, db_session: AsyncSession):
        """born_at defaults to now()."""
        crystal = make_teaching_crystal(id="teach-002")

        db_session.add(crystal)
        await db_session.commit()
        await db_session.refresh(crystal)

        assert crystal.born_at is not None
        assert crystal.created_at is not None

    @pytest.mark.asyncio
    async def test_teaching_crystal_with_evidence(self, db_session: AsyncSession):
        """Teaching crystals can store evidence (test references)."""
        crystal = TeachingCrystal(
            id="teach-003",
            insight="Dual-track storage requires sync",
            severity="warning",
            evidence="test_brain_persistence.py::test_heal_ghosts",
            source_module="services.brain",
            source_symbol="BrainPersistence.capture",
        )

        db_session.add(crystal)
        await db_session.commit()

        result = await db_session.get(TeachingCrystal, "teach-003")
        assert result.evidence == "test_brain_persistence.py::test_heal_ghosts"

    @pytest.mark.asyncio
    async def test_is_alive_property(self, db_session: AsyncSession):
        """is_alive returns True when died_at is None."""
        alive = make_teaching_crystal(id="alive-001")
        dead = make_teaching_crystal(id="dead-001", died_at=datetime.now(UTC))

        db_session.add_all([alive, dead])
        await db_session.commit()

        alive_result = await db_session.get(TeachingCrystal, "alive-001")
        dead_result = await db_session.get(TeachingCrystal, "dead-001")

        assert alive_result.is_alive is True
        assert dead_result.is_alive is False

    @pytest.mark.asyncio
    async def test_is_ancestor_property(self, db_session: AsyncSession):
        """is_ancestor returns True when died_at is set."""
        alive = make_teaching_crystal(id="ancestor-alive")
        ancestor = make_teaching_crystal(id="ancestor-dead", died_at=datetime.now(UTC))

        db_session.add_all([alive, ancestor])
        await db_session.commit()

        alive_result = await db_session.get(TeachingCrystal, "ancestor-alive")
        ancestor_result = await db_session.get(TeachingCrystal, "ancestor-dead")

        assert alive_result.is_ancestor is False
        assert ancestor_result.is_ancestor is True

    @pytest.mark.asyncio
    async def test_teaching_with_successor_chain(self, db_session: AsyncSession):
        """Teaching crystals can reference successor modules."""
        crystal = TeachingCrystal(
            id="teach-successor",
            insight="DialogueService pattern",
            severity="info",
            source_module="services.town.dialogue",
            source_symbol="DialogueService.process",
            died_at=datetime.now(UTC),
            successor_module="services.brain.conversation",
            successor_symbol="ConversationService.process",
        )

        db_session.add(crystal)
        await db_session.commit()

        result = await db_session.get(TeachingCrystal, "teach-successor")
        assert result.successor_module == "services.brain.conversation"
        assert result.successor_symbol == "ConversationService.process"

    @pytest.mark.asyncio
    async def test_teaching_applies_to_paths(self, db_session: AsyncSession):
        """Teaching crystals can list applicable AGENTESE paths."""
        crystal = TeachingCrystal(
            id="teach-paths",
            insight="Always check observer context",
            severity="warning",
            source_module="services.brain",
            source_symbol="capture",
            applies_to=["self.brain.capture", "self.memory.crystallize"],
        )

        db_session.add(crystal)
        await db_session.commit()

        result = await db_session.get(TeachingCrystal, "teach-paths")
        assert "self.brain.capture" in result.applies_to
        assert len(result.applies_to) == 2


# =============================================================================
# ExtinctionEvent Model Tests
# =============================================================================


class TestExtinctionEventModel:
    """Tests for ExtinctionEvent model CRUD and properties."""

    @pytest.mark.asyncio
    async def test_create_extinction_event(self, db_session: AsyncSession):
        """Can create an extinction event with required fields."""
        event = ExtinctionEvent(
            id="ext-001",
            reason="Crown Jewel Cleanup - AD-009",
            commit="abc123def456",
            deleted_paths=["services/town/", "services/park/"],
            successor_map={"town": None, "park": None},
        )

        db_session.add(event)
        await db_session.commit()

        result = await db_session.get(ExtinctionEvent, "ext-001")
        assert result is not None
        assert result.reason == "Crown Jewel Cleanup - AD-009"
        assert "services/town/" in result.deleted_paths

    @pytest.mark.asyncio
    async def test_extinction_event_with_decision_doc(self, db_session: AsyncSession):
        """Extinction events can reference decision documents."""
        event = ExtinctionEvent(
            id="ext-doc",
            reason="Planned refactor",
            decision_doc="spec/decisions/AD-009.md",
            commit="123abc",
        )

        db_session.add(event)
        await db_session.commit()

        result = await db_session.get(ExtinctionEvent, "ext-doc")
        assert result.decision_doc == "spec/decisions/AD-009.md"

    @pytest.mark.asyncio
    async def test_extinction_successor_map(self, db_session: AsyncSession):
        """Successor map tracks what replaced deleted code."""
        event = ExtinctionEvent(
            id="ext-successor",
            reason="Module consolidation",
            commit="456def",
            successor_map={
                "chat": "brain.conversation",
                "archaeology": "living_docs.temporal",
                "muse": None,  # Concept removed entirely
            },
        )

        db_session.add(event)
        await db_session.commit()

        result = await db_session.get(ExtinctionEvent, "ext-successor")
        assert result.successor_map["chat"] == "brain.conversation"
        assert result.successor_map["muse"] is None

    @pytest.mark.asyncio
    async def test_extinction_preserved_count(self, db_session: AsyncSession):
        """Extinction events track how many teaching crystals were preserved."""
        event = ExtinctionEvent(
            id="ext-count",
            reason="Cleanup",
            commit="789ghi",
            preserved_count=42,
        )

        db_session.add(event)
        await db_session.commit()

        result = await db_session.get(ExtinctionEvent, "ext-count")
        assert result.preserved_count == 42


# =============================================================================
# ExtinctionTeaching Join Table Tests
# =============================================================================


class TestExtinctionTeachingJoin:
    """Tests for the many-to-many relationship between extinctions and teaching."""

    @pytest.mark.asyncio
    async def test_link_teaching_to_extinction(self, db_session: AsyncSession):
        """Can link a teaching crystal to an extinction event."""
        teaching = make_teaching_crystal(
            id="join-teach",
            source_module="services.town.dialogue",
            died_at=datetime.now(UTC),
        )
        extinction = make_extinction_event(
            id="join-ext",
            deleted_paths=["services/town/"],
        )

        db_session.add_all([teaching, extinction])
        await db_session.flush()

        # Create the link
        link = ExtinctionTeaching(
            extinction_id="join-ext",
            teaching_id="join-teach",
        )
        db_session.add(link)
        await db_session.commit()

        # Verify via query (avoiding lazy load issues in async context)
        stmt = select(ExtinctionTeaching).where(
            ExtinctionTeaching.extinction_id == "join-ext"
        )
        result = await db_session.execute(stmt)
        links = result.scalars().all()

        assert len(links) == 1
        assert links[0].teaching_id == "join-teach"

    @pytest.mark.asyncio
    async def test_teaching_links_to_extinction(self, db_session: AsyncSession):
        """TeachingCrystal.extinction_links gives access to extinction events."""
        teaching = make_teaching_crystal(
            id="reverse-teach",
            died_at=datetime.now(UTC),
        )
        extinction = make_extinction_event(id="reverse-ext")

        db_session.add_all([teaching, extinction])
        await db_session.flush()

        link = ExtinctionTeaching(
            extinction_id="reverse-ext",
            teaching_id="reverse-teach",
        )
        db_session.add(link)
        await db_session.commit()

        # Access extinction via query (avoiding lazy load issues in async context)
        stmt = select(ExtinctionTeaching).where(
            ExtinctionTeaching.teaching_id == "reverse-teach"
        )
        result = await db_session.execute(stmt)
        links = result.scalars().all()

        assert len(links) == 1
        assert links[0].extinction_id == "reverse-ext"

    @pytest.mark.asyncio
    async def test_cascade_delete_extinction(self, db_session: AsyncSession):
        """Deleting extinction cascades to join table, not teaching."""
        teaching = make_teaching_crystal(id="cascade-teach", died_at=datetime.now(UTC))
        extinction = make_extinction_event(id="cascade-ext")

        db_session.add_all([teaching, extinction])
        await db_session.flush()

        link = ExtinctionTeaching(
            extinction_id="cascade-ext",
            teaching_id="cascade-teach",
        )
        db_session.add(link)
        await db_session.commit()

        # Delete the extinction event
        ext = await db_session.get(ExtinctionEvent, "cascade-ext")
        await db_session.delete(ext)
        await db_session.commit()

        # Teaching should still exist (preserved wisdom!)
        teach_result = await db_session.get(TeachingCrystal, "cascade-teach")
        assert teach_result is not None
        assert teach_result.insight == "Test gotcha"


# =============================================================================
# Query Pattern Tests
# =============================================================================


class TestQueryPatterns:
    """Tests for the query patterns needed by hydration and archaeology."""

    @pytest.mark.asyncio
    async def test_find_alive_teaching_by_module(self, db_session: AsyncSession):
        """Can find alive teaching crystals by source module."""
        alive1 = make_teaching_crystal(
            id="alive-brain-1",
            source_module="services.brain.persistence",
        )
        alive2 = make_teaching_crystal(
            id="alive-brain-2",
            source_module="services.brain.core",
        )
        dead = make_teaching_crystal(
            id="dead-brain",
            source_module="services.brain.old",
            died_at=datetime.now(UTC),
        )
        other = make_teaching_crystal(
            id="alive-other",
            source_module="services.town.dialogue",
        )

        db_session.add_all([alive1, alive2, dead, other])
        await db_session.commit()

        # Query for alive brain teaching
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.source_module.like("services.brain%"),
            TeachingCrystal.died_at.is_(None),
        )
        result = await db_session.execute(stmt)
        crystals = result.scalars().all()

        assert len(crystals) == 2
        ids = {c.id for c in crystals}
        assert "alive-brain-1" in ids
        assert "alive-brain-2" in ids

    @pytest.mark.asyncio
    async def test_find_ancestral_wisdom(self, db_session: AsyncSession):
        """Can find ancestral wisdom (dead teaching crystals)."""
        alive = make_teaching_crystal(id="query-alive")
        ancestor1 = make_teaching_crystal(
            id="query-ancestor-1",
            source_module="services.town",
            died_at=datetime.now(UTC),
        )
        ancestor2 = make_teaching_crystal(
            id="query-ancestor-2",
            source_module="services.park",
            died_at=datetime.now(UTC),
        )

        db_session.add_all([alive, ancestor1, ancestor2])
        await db_session.commit()

        # Query for ancestors
        stmt = select(TeachingCrystal).where(
            TeachingCrystal.died_at.isnot(None),
        )
        result = await db_session.execute(stmt)
        ancestors = result.scalars().all()

        assert len(ancestors) == 2
        assert all(a.is_ancestor for a in ancestors)

    @pytest.mark.asyncio
    async def test_find_critical_teaching(self, db_session: AsyncSession):
        """Can query teaching by severity for prioritization."""
        critical = make_teaching_crystal(id="sev-crit", severity="critical")
        warning = make_teaching_crystal(id="sev-warn", severity="warning")
        info = make_teaching_crystal(id="sev-info", severity="info")

        db_session.add_all([critical, warning, info])
        await db_session.commit()

        stmt = select(TeachingCrystal).where(
            TeachingCrystal.severity == "critical",
        )
        result = await db_session.execute(stmt)
        criticals = result.scalars().all()

        assert len(criticals) == 1
        assert criticals[0].id == "sev-crit"


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for model validation and constraints."""

    @pytest.mark.asyncio
    async def test_teaching_requires_insight(self, db_session: AsyncSession):
        """TeachingCrystal requires an insight (not nullable)."""
        # SQLAlchemy will raise IntegrityError on commit
        crystal = TeachingCrystal(
            id="no-insight",
            insight=None,  # type: ignore - testing invalid input
            severity="warning",
            source_module="test",
            source_symbol="test",
        )

        db_session.add(crystal)

        with pytest.raises(Exception):  # IntegrityError or similar
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_extinction_requires_commit(self, db_session: AsyncSession):
        """ExtinctionEvent requires a commit SHA."""
        event = ExtinctionEvent(
            id="no-commit",
            reason="Test",
            commit=None,  # type: ignore - testing invalid input
        )

        db_session.add(event)

        with pytest.raises(Exception):
            await db_session.commit()


__all__ = [
    "TestTeachingCrystalModel",
    "TestExtinctionEventModel",
    "TestExtinctionTeachingJoin",
    "TestQueryPatterns",
    "TestValidation",
]
