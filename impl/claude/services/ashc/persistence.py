"""
ASHC Persistence: Postgres-backed LemmaDatabase via D-gent patterns.

Implements the LemmaDatabase protocol with full stigmergic reinforcement.
The lemma database is a knowledge base that grows with each successful proof.

Stigmergic Design (§13):
    pheromone = usage_count (more-used lemmas rank higher)
    decay = age-based relevance scoring
    reinforcement = increment usage on successful hint
    emergent path = tactic selection evolves with corpus

Pattern: Follows BrainPersistence dual-track architecture
- TableAdapter[VerifiedLemmaModel]: Fast queries by statement, usage ranking
- Stigmergic reinforcement: usage_count increments on find_related()

Teaching:
    gotcha: find_related() increments usage_count for returned lemmas.
            This is intentional—lemmas that help more become more visible.
            (Evidence: test_lemma_db.py::test_stigmergic_reinforcement)

    gotcha: store() is idempotent on id. If a lemma with the same id exists,
            it's updated (not duplicated). This supports proof regeneration.
            (Evidence: test_lemma_db.py::test_store_idempotent)

    gotcha: Keyword matching uses simple word overlap for now. Brain vectors
            are deferred to Phase 5 for semantic similarity.
            (Evidence: test_lemma_db.py::test_keyword_matching)

AGENTESE: concept.ashc.lemma.*
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.ashc import VerifiedLemmaModel

from .contracts import LemmaId, ObligationId, VerifiedLemma
from .search import LemmaDatabase

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class LemmaStats:
    """Statistics about the lemma database."""

    total_lemmas: int
    total_usage: int
    avg_usage: float
    most_used_id: str | None
    most_used_count: int
    storage_backend: str


class PostgresLemmaDatabase:
    """
    Postgres-backed implementation of LemmaDatabase protocol.

    Uses SQLAlchemy async sessions for all operations.
    Implements stigmergic reinforcement via usage_count.

    Pattern: Signal Aggregation for Decisions (Pattern 4)
    Multiple signals (keyword overlap, usage count, recency) contribute
    to lemma ranking.

    Example:
        session_factory = get_session_factory()
        lemma_db = PostgresLemmaDatabase(session_factory)

        # Store a verified lemma
        await lemma_db.store(verified_lemma)

        # Find related lemmas (increments usage for returned lemmas)
        related = await lemma_db.find_related("∀ x. x == x", limit=3)

    Laws:
        1. Monotonicity: lemmas only accumulate (no deletes in normal operation)
        2. Reinforcement: find_related() increments usage for returned lemmas
        3. Soundness: only verified lemmas are stored

    Teaching:
        gotcha: PostgresLemmaDatabase is stateless between calls.
                All state is in the database. Safe for concurrent access.
                (Evidence: test_lemma_db.py::test_concurrent_access)
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        """
        Initialize Postgres-backed lemma database.

        Args:
            session_factory: Async session factory for database access
        """
        self._session_factory = session_factory

    # =========================================================================
    # LemmaDatabase Protocol Implementation
    # =========================================================================

    def find_related(
        self,
        property_stmt: str,
        limit: int = 3,
    ) -> list[VerifiedLemma]:
        """
        Find lemmas related to a property statement.

        Synchronous wrapper for async implementation.
        Required by LemmaDatabase protocol.

        Args:
            property_stmt: The property to find related lemmas for
            limit: Maximum number of lemmas to return

        Returns:
            List of related verified lemmas (most relevant first)
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to use a different approach
            # This shouldn't happen in practice since ProofSearcher is async
            raise RuntimeError("Use find_related_async in async context")
        except RuntimeError:
            # No running loop - create one for sync context
            return asyncio.run(self.find_related_async(property_stmt, limit))

    async def find_related_async(
        self,
        property_stmt: str,
        limit: int = 3,
    ) -> list[VerifiedLemma]:
        """
        Find lemmas related to a property statement (async version).

        Strategy:
        1. Extract keywords from property statement
        2. Find lemmas with overlapping keywords
        3. Rank by (keyword_overlap * (1 + usage_count * 0.1))
        4. Increment usage for returned lemmas (stigmergic reinforcement)

        Args:
            property_stmt: The property to find related lemmas for
            limit: Maximum number of lemmas to return

        Returns:
            List of related verified lemmas (most relevant first)
        """
        # Extract keywords from property
        keywords = set(
            re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", property_stmt.lower())
        )

        if not keywords:
            return []

        async with self._session_factory() as session:
            # Get all lemmas (we'll filter in Python for keyword matching)
            # TODO: Use Postgres full-text search for better performance
            stmt = select(VerifiedLemmaModel).order_by(
                VerifiedLemmaModel.usage_count.desc()
            )
            result = await session.execute(stmt)
            models = result.scalars().all()

            if not models:
                return []

            # Score by keyword overlap with stigmergic bias
            scored: list[tuple[float, VerifiedLemmaModel]] = []
            for model in models:
                model_keywords = set(
                    re.findall(
                        r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
                        model.statement.lower(),
                    )
                )
                overlap = len(keywords & model_keywords)
                if overlap > 0:
                    # Stigmergic reinforcement: usage_count boosts score
                    score = overlap * (1 + model.usage_count * 0.1)
                    scored.append((score, model))

            # Sort by score descending
            scored.sort(key=lambda x: x[0], reverse=True)
            top_models = [model for _, model in scored[:limit]]

            # Increment usage for returned lemmas (stigmergic reinforcement)
            if top_models:
                ids_to_update = [m.id for m in top_models]
                await session.execute(
                    update(VerifiedLemmaModel)
                    .where(VerifiedLemmaModel.id.in_(ids_to_update))
                    .values(usage_count=VerifiedLemmaModel.usage_count + 1)
                )
                await session.commit()

            # Convert to domain objects
            return [self._model_to_lemma(m) for m in top_models]

    def store(self, lemma: VerifiedLemma) -> None:
        """
        Store a newly verified lemma.

        Synchronous wrapper for async implementation.
        Required by LemmaDatabase protocol.

        Args:
            lemma: The verified lemma to store
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            raise RuntimeError("Use store_async in async context")
        except RuntimeError:
            asyncio.run(self.store_async(lemma))

    async def store_async(self, lemma: VerifiedLemma) -> None:
        """
        Store a newly verified lemma (async version).

        Idempotent: if a lemma with the same id exists, it's updated.

        Args:
            lemma: The verified lemma to store
        """
        async with self._session_factory() as session:
            # Check for existing lemma
            existing = await session.get(VerifiedLemmaModel, str(lemma.id))

            if existing:
                # Update existing (idempotent upsert)
                existing.statement = lemma.statement
                existing.proof = lemma.proof
                existing.checker = lemma.checker
                existing.obligation_id = str(lemma.obligation_id)
                existing.dependencies = [str(d) for d in lemma.dependencies]
                # Preserve usage_count on update
                existing.verified_at = lemma.verified_at
            else:
                # Create new
                model = VerifiedLemmaModel(
                    id=str(lemma.id),
                    statement=lemma.statement,
                    proof=lemma.proof,
                    checker=lemma.checker,
                    obligation_id=str(lemma.obligation_id),
                    dependencies=[str(d) for d in lemma.dependencies],
                    usage_count=lemma.usage_count,
                    verified_at=lemma.verified_at,
                )
                session.add(model)

            await session.commit()

    # =========================================================================
    # Extended API (beyond protocol)
    # =========================================================================

    async def get_by_id(self, lemma_id: str) -> VerifiedLemma | None:
        """
        Get a specific lemma by ID.

        Args:
            lemma_id: The lemma ID to retrieve

        Returns:
            VerifiedLemma or None if not found
        """
        async with self._session_factory() as session:
            model = await session.get(VerifiedLemmaModel, lemma_id)
            if model is None:
                return None
            return self._model_to_lemma(model)

    async def get_by_obligation(self, obligation_id: str) -> VerifiedLemma | None:
        """
        Get lemma by its origin obligation.

        Args:
            obligation_id: The obligation ID that spawned the lemma

        Returns:
            VerifiedLemma or None if not found
        """
        async with self._session_factory() as session:
            stmt = select(VerifiedLemmaModel).where(
                VerifiedLemmaModel.obligation_id == obligation_id
            )
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._model_to_lemma(model)

    async def list_recent(self, limit: int = 10) -> list[VerifiedLemma]:
        """
        List recently verified lemmas.

        Args:
            limit: Maximum number to return

        Returns:
            List of lemmas, newest first
        """
        async with self._session_factory() as session:
            stmt = (
                select(VerifiedLemmaModel)
                .order_by(VerifiedLemmaModel.verified_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._model_to_lemma(m) for m in models]

    async def list_most_used(self, limit: int = 10) -> list[VerifiedLemma]:
        """
        List most frequently used lemmas.

        This shows the "well-worn paths" in the proof landscape.

        Args:
            limit: Maximum number to return

        Returns:
            List of lemmas, most used first
        """
        async with self._session_factory() as session:
            stmt = (
                select(VerifiedLemmaModel)
                .order_by(VerifiedLemmaModel.usage_count.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            models = result.scalars().all()
            return [self._model_to_lemma(m) for m in models]

    async def stats(self) -> LemmaStats:
        """
        Get statistics about the lemma database.

        Returns:
            LemmaStats with counts and usage metrics
        """
        async with self._session_factory() as session:
            # Total count
            count_result = await session.execute(
                select(func.count()).select_from(VerifiedLemmaModel)
            )
            total = count_result.scalar() or 0

            if total == 0:
                return LemmaStats(
                    total_lemmas=0,
                    total_usage=0,
                    avg_usage=0.0,
                    most_used_id=None,
                    most_used_count=0,
                    storage_backend="postgres",
                )

            # Total usage
            usage_result = await session.execute(
                select(func.sum(VerifiedLemmaModel.usage_count))
            )
            total_usage = usage_result.scalar() or 0

            # Most used
            most_used_stmt = (
                select(VerifiedLemmaModel)
                .order_by(VerifiedLemmaModel.usage_count.desc())
                .limit(1)
            )
            most_used_result = await session.execute(most_used_stmt)
            most_used = most_used_result.scalar_one_or_none()

            return LemmaStats(
                total_lemmas=total,
                total_usage=total_usage,
                avg_usage=total_usage / total if total > 0 else 0.0,
                most_used_id=most_used.id if most_used else None,
                most_used_count=most_used.usage_count if most_used else 0,
                storage_backend="postgres",
            )

    async def count(self) -> int:
        """Count total lemmas."""
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count()).select_from(VerifiedLemmaModel)
            )
            return result.scalar() or 0

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _model_to_lemma(self, model: VerifiedLemmaModel) -> VerifiedLemma:
        """Convert SQLAlchemy model to domain object."""
        return VerifiedLemma(
            id=LemmaId(model.id),
            statement=model.statement,
            proof=model.proof,
            checker=model.checker,
            obligation_id=ObligationId(model.obligation_id),
            dependencies=tuple(LemmaId(d) for d in (model.dependencies or [])),
            usage_count=model.usage_count,
            verified_at=model.verified_at or datetime.now(UTC),
        )


__all__ = ["PostgresLemmaDatabase", "LemmaStats"]
