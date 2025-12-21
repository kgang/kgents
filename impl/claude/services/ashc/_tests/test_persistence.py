"""
Tests for Postgres-backed LemmaDatabase.

Phase 4 of the proof-generation implementation plan.

Test Categories:
1. PostgresLemmaDatabase basic functionality
2. Stigmergic reinforcement (usage count)
3. Keyword-based search
4. Statistics and counts
5. Protocol compliance

Heritage: Stigmergic Cognition (§13)
    pheromone = usage_count
    reinforcement = increment on find_related
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models.ashc import VerifiedLemmaModel
from models.base import Base

from ..contracts import LemmaId, ObligationId, VerifiedLemma
from ..persistence import LemmaStats, PostgresLemmaDatabase
from ..search import LemmaDatabase


# =============================================================================
# Fixtures
# =============================================================================


@pytest_asyncio.fixture
async def session_factory() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create an in-memory SQLite session factory for testing."""
    # Use in-memory SQLite for fast tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield factory

    await engine.dispose()


@pytest_asyncio.fixture
async def lemma_db(
    session_factory: async_sessionmaker[AsyncSession],
) -> PostgresLemmaDatabase:
    """Create a PostgresLemmaDatabase instance for testing."""
    return PostgresLemmaDatabase(session_factory)


@pytest.fixture
def sample_lemma() -> VerifiedLemma:
    """Create a sample verified lemma."""
    return VerifiedLemma(
        id=LemmaId("lem-test-001"),
        statement="∀ x: int. x + 0 == x",
        proof="lemma AddZero() ensures forall x: int :: x + 0 == x {}",
        checker="dafny",
        obligation_id=ObligationId("obl-test-001"),
        dependencies=(),
        usage_count=0,
        verified_at=datetime.now(UTC),
    )


@pytest.fixture
def identity_lemma() -> VerifiedLemma:
    """Create a lemma about identity."""
    return VerifiedLemma(
        id=LemmaId("lem-identity-001"),
        statement="∀ x: int. x == x",
        proof="lemma Identity() ensures forall x: int :: x == x {}",
        checker="dafny",
        obligation_id=ObligationId("obl-identity-001"),
    )


@pytest.fixture
def composition_lemma() -> VerifiedLemma:
    """Create a lemma about composition."""
    return VerifiedLemma(
        id=LemmaId("lem-composition-001"),
        statement="∀ f, g, h. (f >> g) >> h == f >> (g >> h)",
        proof="lemma Assoc() ensures ... {}",
        checker="dafny",
        obligation_id=ObligationId("obl-composition-001"),
    )


# =============================================================================
# Test: Basic Store and Retrieve
# =============================================================================


class TestStoreAndRetrieve:
    """Tests for basic store and retrieve operations."""

    @pytest.mark.asyncio
    async def test_store_and_get_by_id(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Store a lemma and retrieve it by ID."""
        await lemma_db.store_async(sample_lemma)

        retrieved = await lemma_db.get_by_id(str(sample_lemma.id))

        assert retrieved is not None
        assert retrieved.id == sample_lemma.id
        assert retrieved.statement == sample_lemma.statement
        assert retrieved.proof == sample_lemma.proof
        assert retrieved.checker == sample_lemma.checker

    @pytest.mark.asyncio
    async def test_store_idempotent(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Storing the same lemma twice updates rather than duplicates."""
        await lemma_db.store_async(sample_lemma)

        # Modify and store again
        updated = VerifiedLemma(
            id=sample_lemma.id,
            statement="Updated statement",
            proof=sample_lemma.proof,
            checker=sample_lemma.checker,
            obligation_id=sample_lemma.obligation_id,
        )
        await lemma_db.store_async(updated)

        # Should have only one lemma
        count = await lemma_db.count()
        assert count == 1

        # Should have updated statement
        retrieved = await lemma_db.get_by_id(str(sample_lemma.id))
        assert retrieved is not None
        assert retrieved.statement == "Updated statement"

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_none(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Getting a nonexistent lemma returns None."""
        result = await lemma_db.get_by_id("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_obligation(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Retrieve lemma by its origin obligation."""
        await lemma_db.store_async(sample_lemma)

        retrieved = await lemma_db.get_by_obligation(str(sample_lemma.obligation_id))

        assert retrieved is not None
        assert retrieved.id == sample_lemma.id


# =============================================================================
# Test: Find Related (Keyword Matching)
# =============================================================================


class TestFindRelated:
    """Tests for keyword-based related lemma search."""

    @pytest.mark.asyncio
    async def test_empty_db_returns_empty(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Empty database returns no related lemmas."""
        related = await lemma_db.find_related_async("∀ x. x == x")
        assert related == []

    @pytest.mark.asyncio
    async def test_find_by_keyword_overlap(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Find lemmas with overlapping keywords."""
        await lemma_db.store_async(sample_lemma)

        # Search for statement with shared keywords
        related = await lemma_db.find_related_async("∀ x: int. x + 1 == x + 1")

        assert len(related) >= 1
        assert related[0].id == sample_lemma.id

    @pytest.mark.asyncio
    async def test_limit_respected(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Find related respects limit parameter."""
        # Store many similar lemmas
        for i in range(10):
            lemma = VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"∀ x: int. x + {i} == x + {i}",
                proof="",
                checker="dafny",
                obligation_id=ObligationId(f"obl-{i}"),
            )
            await lemma_db.store_async(lemma)

        related = await lemma_db.find_related_async("∀ x: int. something", limit=3)

        assert len(related) <= 3

    @pytest.mark.asyncio
    async def test_no_match_returns_empty(
        self,
        lemma_db: PostgresLemmaDatabase,
        composition_lemma: VerifiedLemma,
    ) -> None:
        """No keyword overlap returns empty list."""
        await lemma_db.store_async(composition_lemma)

        # Search for completely unrelated keywords
        related = await lemma_db.find_related_async("banana apple orange")

        assert related == []


# =============================================================================
# Test: Stigmergic Reinforcement
# =============================================================================


class TestStigmergicReinforcement:
    """Tests for pheromone = usage_count behavior."""

    @pytest.mark.asyncio
    async def test_find_related_increments_usage(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """find_related increments usage_count for returned lemmas."""
        await lemma_db.store_async(sample_lemma)

        # Initial usage should be 0
        before = await lemma_db.get_by_id(str(sample_lemma.id))
        assert before is not None
        assert before.usage_count == 0

        # Find related (should increment)
        await lemma_db.find_related_async("∀ x: int. x + 1")

        # Usage should be incremented
        after = await lemma_db.get_by_id(str(sample_lemma.id))
        assert after is not None
        assert after.usage_count == 1

    @pytest.mark.asyncio
    async def test_multiple_finds_accumulate_usage(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Multiple find_related calls accumulate usage count."""
        await lemma_db.store_async(sample_lemma)

        # Find related multiple times
        for _ in range(5):
            await lemma_db.find_related_async("∀ x: int. something")

        result = await lemma_db.get_by_id(str(sample_lemma.id))
        assert result is not None
        assert result.usage_count == 5

    @pytest.mark.asyncio
    async def test_high_usage_ranks_higher(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """More-used lemmas rank higher in search results."""
        # Store two similar lemmas with different initial usage
        low_usage = VerifiedLemma(
            id=LemmaId("lem-low"),
            statement="∀ x: int. x == x",
            proof="",
            checker="dafny",
            obligation_id=ObligationId("obl-1"),
            usage_count=1,
        )
        high_usage = VerifiedLemma(
            id=LemmaId("lem-high"),
            statement="∀ x: int. x == x",
            proof="",
            checker="dafny",
            obligation_id=ObligationId("obl-2"),
            usage_count=100,
        )

        await lemma_db.store_async(low_usage)
        await lemma_db.store_async(high_usage)

        related = await lemma_db.find_related_async("∀ x: int. x == x", limit=2)

        # High usage should be first (due to stigmergic bias)
        assert len(related) == 2
        assert related[0].id == LemmaId("lem-high")

    @pytest.mark.asyncio
    async def test_store_preserves_usage_on_update(
        self,
        lemma_db: PostgresLemmaDatabase,
        sample_lemma: VerifiedLemma,
    ) -> None:
        """Updating a lemma preserves its usage count."""
        await lemma_db.store_async(sample_lemma)

        # Increment usage
        await lemma_db.find_related_async("∀ x: int. something")
        await lemma_db.find_related_async("∀ x: int. something")

        # Update the lemma
        updated = VerifiedLemma(
            id=sample_lemma.id,
            statement="Updated",
            proof=sample_lemma.proof,
            checker=sample_lemma.checker,
            obligation_id=sample_lemma.obligation_id,
            usage_count=0,  # This should be ignored on update
        )
        await lemma_db.store_async(updated)

        # Usage should be preserved
        result = await lemma_db.get_by_id(str(sample_lemma.id))
        assert result is not None
        assert result.usage_count == 2  # Not reset to 0


# =============================================================================
# Test: List Operations
# =============================================================================


class TestListOperations:
    """Tests for list_recent and list_most_used."""

    @pytest.mark.asyncio
    async def test_list_recent(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """list_recent returns lemmas in newest-first order."""
        # Store lemmas with different timestamps
        for i in range(5):
            lemma = VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"Statement {i}",
                proof="",
                checker="dafny",
                obligation_id=ObligationId(f"obl-{i}"),
            )
            await lemma_db.store_async(lemma)

        recent = await lemma_db.list_recent(limit=3)

        assert len(recent) == 3
        # Most recent should be first (lem-4 was stored last)
        assert recent[0].id == LemmaId("lem-4")

    @pytest.mark.asyncio
    async def test_list_most_used(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """list_most_used returns lemmas by usage count."""
        # Store lemmas with different usage counts
        for i in range(5):
            lemma = VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"Statement {i}",
                proof="",
                checker="dafny",
                obligation_id=ObligationId(f"obl-{i}"),
                usage_count=i * 10,  # 0, 10, 20, 30, 40
            )
            await lemma_db.store_async(lemma)

        most_used = await lemma_db.list_most_used(limit=3)

        assert len(most_used) == 3
        # Highest usage should be first (lem-4 has usage_count=40)
        assert most_used[0].id == LemmaId("lem-4")
        assert most_used[0].usage_count == 40


# =============================================================================
# Test: Statistics
# =============================================================================


class TestStatistics:
    """Tests for lemma database statistics."""

    @pytest.mark.asyncio
    async def test_stats_empty_db(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Stats on empty database."""
        stats = await lemma_db.stats()

        assert stats.total_lemmas == 0
        assert stats.total_usage == 0
        assert stats.avg_usage == 0.0
        assert stats.most_used_id is None
        assert stats.most_used_count == 0
        assert stats.storage_backend == "postgres"

    @pytest.mark.asyncio
    async def test_stats_with_lemmas(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Stats with stored lemmas."""
        # Store lemmas with different usage
        for i in range(3):
            lemma = VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"Statement {i}",
                proof="",
                checker="dafny",
                obligation_id=ObligationId(f"obl-{i}"),
                usage_count=(i + 1) * 10,  # 10, 20, 30
            )
            await lemma_db.store_async(lemma)

        stats = await lemma_db.stats()

        assert stats.total_lemmas == 3
        assert stats.total_usage == 60  # 10 + 20 + 30
        assert stats.avg_usage == 20.0
        assert stats.most_used_id == "lem-2"
        assert stats.most_used_count == 30

    @pytest.mark.asyncio
    async def test_count(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Count returns correct total."""
        assert await lemma_db.count() == 0

        for i in range(5):
            lemma = VerifiedLemma(
                id=LemmaId(f"lem-{i}"),
                statement=f"Statement {i}",
                proof="",
                checker="dafny",
                obligation_id=ObligationId(f"obl-{i}"),
            )
            await lemma_db.store_async(lemma)

        assert await lemma_db.count() == 5


# =============================================================================
# Test: Dependencies
# =============================================================================


class TestDependencies:
    """Tests for lemma dependency tracking."""

    @pytest.mark.asyncio
    async def test_store_with_dependencies(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Store a lemma with dependencies."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-derived"),
            statement="∀ x. derived(x)",
            proof="uses base lemmas",
            checker="dafny",
            obligation_id=ObligationId("obl-derived"),
            dependencies=(LemmaId("lem-base-1"), LemmaId("lem-base-2")),
        )

        await lemma_db.store_async(lemma)

        retrieved = await lemma_db.get_by_id("lem-derived")
        assert retrieved is not None
        assert len(retrieved.dependencies) == 2
        assert LemmaId("lem-base-1") in retrieved.dependencies
        assert LemmaId("lem-base-2") in retrieved.dependencies


# =============================================================================
# Test: Protocol Compliance
# =============================================================================


class TestProtocolCompliance:
    """Tests for LemmaDatabase protocol compliance."""

    def test_implements_protocol(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """PostgresLemmaDatabase implements LemmaDatabase protocol."""
        db = PostgresLemmaDatabase(session_factory)

        # Protocol methods exist
        assert hasattr(db, "find_related")
        assert hasattr(db, "store")

        # Can be used as LemmaDatabase (duck typing)
        assert isinstance(db, LemmaDatabase)

    @pytest.mark.asyncio
    async def test_sync_wrapper_raises_in_async_context(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Sync wrappers raise when called in async context."""
        # The sync wrappers detect running loop and raise
        # This is intentional—use _async versions in async code
        with pytest.raises(RuntimeError, match="running event loop"):
            lemma_db.find_related("test")


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_empty_statement(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Handle lemma with empty statement."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-empty"),
            statement="",
            proof="",
            checker="dafny",
            obligation_id=ObligationId("obl-empty"),
        )

        await lemma_db.store_async(lemma)
        retrieved = await lemma_db.get_by_id("lem-empty")

        assert retrieved is not None
        assert retrieved.statement == ""

    @pytest.mark.asyncio
    async def test_unicode_in_statement(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Handle unicode characters in statement."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-unicode"),
            statement="∀ α: τ. α ≡ α",
            proof="lemma with unicode",
            checker="dafny",
            obligation_id=ObligationId("obl-unicode"),
        )

        await lemma_db.store_async(lemma)
        retrieved = await lemma_db.get_by_id("lem-unicode")

        assert retrieved is not None
        assert "∀" in retrieved.statement
        assert "≡" in retrieved.statement

    @pytest.mark.asyncio
    async def test_long_proof(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Handle very long proof text."""
        long_proof = "lemma " * 10000  # ~60KB of text

        lemma = VerifiedLemma(
            id=LemmaId("lem-long"),
            statement="Long proof",
            proof=long_proof,
            checker="dafny",
            obligation_id=ObligationId("obl-long"),
        )

        await lemma_db.store_async(lemma)
        retrieved = await lemma_db.get_by_id("lem-long")

        assert retrieved is not None
        assert len(retrieved.proof) == len(long_proof)

    @pytest.mark.asyncio
    async def test_special_characters_in_id(
        self,
        lemma_db: PostgresLemmaDatabase,
    ) -> None:
        """Handle special characters in lemma ID."""
        lemma = VerifiedLemma(
            id=LemmaId("lem-special_chars-123-abc"),
            statement="Test",
            proof="",
            checker="dafny",
            obligation_id=ObligationId("obl-special"),
        )

        await lemma_db.store_async(lemma)
        retrieved = await lemma_db.get_by_id("lem-special_chars-123-abc")

        assert retrieved is not None
