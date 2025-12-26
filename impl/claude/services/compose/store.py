"""
Composition Store: Database persistence for named compositions.

"Compositions worth repeating are compositions worth naming."

The store enables:
- Saving named compositions for reuse
- Retrieving composition history
- Listing saved compositions
- Loading compositions by name or ID

Pattern: Append-Only History (Pattern 7 from crown-jewel-patterns.md)
    Compositions are immutable once saved. Updates create new versions.

Storage strategy:
    Database-backed with SQLAlchemy for persistence across sessions.

Teaching:
    gotcha: We use SQLAlchemy's async session. Always use `async with` for
            session lifecycle management (prevents connection leaks).

    principle: Composable - Store operations compose via async context managers.
               Save → Query → Load can be chained cleanly.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 5)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session
from models.composition import CompositionRow

if TYPE_CHECKING:
    from .types import Composition, CompositionStatus

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def _composition_to_row(comp: Composition) -> CompositionRow:
    """Convert Composition to database row."""
    return CompositionRow(
        id=comp.id,
        name=comp.name,
        author=comp.author,
        commands=[step.command for step in comp.steps],
        dependencies={str(step.index): step.depends_on for step in comp.steps},
        last_status=comp.status.value if comp.status else None,
        last_trace_id=comp.trace_id,
        last_executed_at=comp.started_at,
        last_duration_ms=_calculate_duration(comp),
        last_success_count=_count_successes(comp),
        last_failure_count=_count_failures(comp),
        execution_count=1,  # Increment on each save
    )


def _calculate_duration(comp: Composition) -> float | None:
    """Calculate total duration from results."""
    if not comp.results:
        return None
    return sum(r.duration_ms for r in comp.results)


def _count_successes(comp: Composition) -> int:
    """Count successful steps."""
    return sum(1 for r in comp.results if r.success and not r.skipped)


def _count_failures(comp: Composition) -> int:
    """Count failed steps."""
    return sum(1 for r in comp.results if not r.success and not r.skipped)


# =============================================================================
# CompositionStore
# =============================================================================


class CompositionStore:
    """
    Database-backed store for compositions.

    Example usage:
        >>> store = CompositionStore()
        >>>
        >>> # Save a composition
        >>> await store.save(composition)
        >>>
        >>> # Get by ID
        >>> comp = await store.get(comp_id)
        >>>
        >>> # Get by name
        >>> comp = await store.get_by_name("validate-witness")
        >>>
        >>> # List recent history
        >>> recent = await store.history(limit=20)
    """

    def __init__(self) -> None:
        """Initialize composition store."""
        pass

    async def save(self, composition: Composition) -> None:
        """
        Save a composition to database.

        Named compositions are indexed by name for retrieval.
        All compositions are added to history.

        Args:
            composition: Composition to save
        """
        async with get_async_session() as session:
            # Check if exists
            stmt = select(CompositionRow).where(CompositionRow.id == composition.id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing (increment execution count)
                existing.last_status = composition.status.value if composition.status else None
                existing.last_trace_id = composition.trace_id
                existing.last_executed_at = composition.started_at
                existing.last_duration_ms = _calculate_duration(composition)
                existing.last_success_count = _count_successes(composition)
                existing.last_failure_count = _count_failures(composition)
                existing.execution_count += 1
                logger.debug(f"Updated composition {composition.id} (execution #{existing.execution_count})")
            else:
                # Create new
                row = _composition_to_row(composition)
                session.add(row)
                logger.info(f"Saved composition {composition.id} (name={composition.name})")

            await session.commit()

    async def get(self, composition_id: str) -> CompositionRow | None:
        """
        Get a composition by ID.

        Args:
            composition_id: Composition ID

        Returns:
            CompositionRow if found, None otherwise
        """
        async with get_async_session() as session:
            stmt = select(CompositionRow).where(CompositionRow.id == composition_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> CompositionRow | None:
        """
        Get the most recent composition by name.

        If multiple compositions exist with the same name,
        returns the most recent one.

        Args:
            name: Composition name

        Returns:
            CompositionRow if found, None otherwise
        """
        async with get_async_session() as session:
            stmt = (
                select(CompositionRow)
                .where(CompositionRow.name == name)
                .order_by(CompositionRow.created_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_named(self) -> list[str]:
        """
        List all named compositions.

        Returns:
            List of unique composition names
        """
        async with get_async_session() as session:
            from sqlalchemy import distinct

            stmt = select(distinct(CompositionRow.name)).where(CompositionRow.name.isnot(None))
            result = await session.execute(stmt)
            return [name for (name,) in result.all()]

    async def history(self, limit: int = 20) -> list[CompositionRow]:
        """
        Get recent composition history.

        Args:
            limit: Maximum number of results

        Returns:
            List of CompositionRow ordered by created_at DESC
        """
        async with get_async_session() as session:
            stmt = select(CompositionRow).order_by(CompositionRow.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count(self) -> int:
        """
        Count total compositions.

        Returns:
            Total number of compositions
        """
        async with get_async_session() as session:
            from sqlalchemy import func

            stmt = select(func.count(CompositionRow.id))
            result = await session.execute(stmt)
            return result.scalar_one()


# Global singleton store
_global_store: CompositionStore | None = None


def get_composition_store() -> CompositionStore:
    """Get the global composition store (singleton)."""
    global _global_store
    if _global_store is None:
        _global_store = CompositionStore()
    return _global_store


def reset_composition_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


__all__ = ["CompositionStore", "get_composition_store", "reset_composition_store"]
