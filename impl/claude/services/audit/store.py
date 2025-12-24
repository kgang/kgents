"""
Audit Store: Database persistence for spec audit results.

> *"Every audit is witnessed. Every principle score is traced."*

This module provides database-backed storage for audit results with efficient querying:
- Save audit results with automatic witness marking
- Query by spec_path, principle scores, drift severity
- Track principle score evolution over time
- Analyze drift patterns across specs

Storage Pattern:
    - Primary: Database (audit_results table) for queryability
    - Future: Optional D-gent semantic search for drift patterns

Teaching:
    gotcha: We use SQLAlchemy's async session. Always use `async with` for
            session lifecycle management (prevents connection leaks).

    principle: Composable - Store operations compose via async context managers.
               Save → Query → Analyze can be chained cleanly.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 1)
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.audit import AuditResultRow
from models.base import get_async_session

if TYPE_CHECKING:
    from services.audit.types import AuditResult


logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def _generate_audit_id() -> str:
    """Generate unique audit ID."""
    return f"audit-{secrets.token_hex(8)}"


def _result_to_row(result: AuditResult, audit_id: str, mark_id: str) -> AuditResultRow:
    """Convert AuditResult to database row."""
    # Extract principle scores
    scores = result.principle_scores
    principle_mean = scores.mean() if scores else None

    # Count drift items by severity
    from services.audit.types import AuditSeverity

    drift_errors = len(
        [d for d in result.drift_items if d.severity in (AuditSeverity.ERROR, AuditSeverity.CRITICAL)]
    )

    return AuditResultRow(
        id=audit_id,
        spec_path=str(result.spec_path),
        impl_path=str(result.impl_path) if result.impl_path else None,
        # Principle scores
        principle_tasteful=scores.tasteful if scores else None,
        principle_curated=scores.curated if scores else None,
        principle_ethical=scores.ethical if scores else None,
        principle_joy_inducing=scores.joy_inducing if scores else None,
        principle_composable=scores.composable if scores else None,
        principle_heterarchical=scores.heterarchical if scores else None,
        principle_generative=scores.generative if scores else None,
        principle_mean=principle_mean,
        # Drift detection
        drift_items=[d.to_dict() for d in result.drift_items],
        drift_error_count=drift_errors,
        drift_total_count=len(result.drift_items),
        # Coverage
        coverage_pct=result.coverage_pct,
        # Action items
        action_items=result.action_items,
        # Witness trace
        mark_id=mark_id,
    )


# =============================================================================
# AuditStore
# =============================================================================


class AuditStore:
    """
    Database-backed storage for spec audit results.

    Example usage:
        >>> store = AuditStore()
        >>> witness = await get_witness_persistence()
        >>>
        >>> # Save an audit result
        >>> audit_id = await store.save_audit(
        ...     result=audit_result,
        ...     witness=witness,
        ... )
        >>>
        >>> # Get latest audit for a spec
        >>> latest = await store.get_latest_audit("spec/protocols/witness.md")
        >>>
        >>> # Get all audits with low composable scores
        >>> low_composable = await store.query_by_principle(
        ...     principle="composable",
        ...     max_score=0.5,
        ... )
    """

    def __init__(self) -> None:
        """Initialize audit store."""
        pass

    # =========================================================================
    # Save Operations
    # =========================================================================

    async def save_audit(
        self,
        result: AuditResult,
        witness=None,  # WitnessPersistence | None
    ) -> str:
        """
        Save an audit result with automatic witness marking.

        Args:
            result: AuditResult to save
            witness: WitnessPersistence instance (for creating mark)

        Returns:
            The audit ID

        Teaching:
            gotcha: We create a witness mark for EVERY audit, even if it passes.
                    This enables "show me all audits" queries via mark history.
        """
        # Generate ID
        audit_id = _generate_audit_id()

        # Create witness mark
        mark_id = ""
        if witness:
            mark_result = await witness.save_mark(
                action=f"Audited {result.spec_path}",
                reasoning=result.summary(),
                tags=["audit", f"spec:{result.spec_path.name}"],
                principles=self._extract_principles(result),
                author="claude-code",
            )
            mark_id = mark_result.mark_id
            logger.info(f"Created witness mark {mark_id} for audit {audit_id}")
        else:
            logger.warning(f"No witness provided for audit {audit_id} - mark not created")

        # Save to database
        async with get_async_session() as session:
            row = _result_to_row(result, audit_id, mark_id)
            session.add(row)
            await session.commit()
            mean_score_str = f"{row.principle_mean:.2f}" if row.principle_mean else "N/A"
            logger.info(f"Saved audit {audit_id}: {result.spec_path} (mean score: {mean_score_str})")

        return audit_id

    def _extract_principles(self, result: AuditResult) -> list[str]:
        """
        Extract principle names from audit result for witness tagging.

        Returns principles that score >= 0.7 (passing threshold).
        """
        if not result.principle_scores:
            return []

        scores = result.principle_scores
        principles = []

        if scores.tasteful >= 0.7:
            principles.append("tasteful")
        if scores.curated >= 0.7:
            principles.append("curated")
        if scores.ethical >= 0.7:
            principles.append("ethical")
        if scores.joy_inducing >= 0.7:
            principles.append("joy-inducing")
        if scores.composable >= 0.7:
            principles.append("composable")
        if scores.heterarchical >= 0.7:
            principles.append("heterarchical")
        if scores.generative >= 0.7:
            principles.append("generative")

        return principles

    # =========================================================================
    # Query Operations
    # =========================================================================

    async def get_latest_audit(self, spec_path: str | Path) -> AuditResultRow | None:
        """
        Get the most recent audit for a spec.

        Args:
            spec_path: Path to spec file

        Returns:
            Latest AuditResultRow or None if no audits exist
        """
        spec_path_str = str(spec_path)
        async with get_async_session() as session:
            stmt = (
                select(AuditResultRow)
                .where(AuditResultRow.spec_path == spec_path_str)
                .order_by(AuditResultRow.created_at.desc())
                .limit(1)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_audit_history(
        self,
        spec_path: str | Path,
        limit: int = 20,
    ) -> list[AuditResultRow]:
        """
        Get audit history for a spec (most recent first).

        Args:
            spec_path: Path to spec file
            limit: Maximum number of audits to return

        Returns:
            List of AuditResultRow ordered by created_at DESC
        """
        spec_path_str = str(spec_path)
        async with get_async_session() as session:
            stmt = (
                select(AuditResultRow)
                .where(AuditResultRow.spec_path == spec_path_str)
                .order_by(AuditResultRow.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def query_by_principle(
        self,
        principle: str,
        min_score: float | None = None,
        max_score: float | None = None,
        limit: int = 50,
    ) -> list[AuditResultRow]:
        """
        Query audits by principle score.

        Args:
            principle: Principle name (tasteful, curated, etc.)
            min_score: Minimum score threshold (0.0 - 1.0)
            max_score: Maximum score threshold (0.0 - 1.0)
            limit: Maximum number of results

        Returns:
            List of AuditResultRow matching criteria

        Example:
            # Find all specs with low composable scores
            low_composable = await store.query_by_principle(
                principle="composable",
                max_score=0.5,
            )
        """
        async with get_async_session() as session:
            # Map principle name to column
            column_map = {
                "tasteful": AuditResultRow.principle_tasteful,
                "curated": AuditResultRow.principle_curated,
                "ethical": AuditResultRow.principle_ethical,
                "joy_inducing": AuditResultRow.principle_joy_inducing,
                "joy-inducing": AuditResultRow.principle_joy_inducing,
                "composable": AuditResultRow.principle_composable,
                "heterarchical": AuditResultRow.principle_heterarchical,
                "generative": AuditResultRow.principle_generative,
            }

            column = column_map.get(principle.lower())
            if not column:
                logger.warning(f"Unknown principle: {principle}")
                return []

            # Build query
            stmt = select(AuditResultRow).where(column.isnot(None))

            if min_score is not None:
                stmt = stmt.where(column >= min_score)
            if max_score is not None:
                stmt = stmt.where(column <= max_score)

            stmt = stmt.order_by(AuditResultRow.created_at.desc()).limit(limit)

            # Execute
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def query_with_drift_errors(self, limit: int = 50) -> list[AuditResultRow]:
        """
        Query audits that have drift errors (ERROR or CRITICAL severity).

        Args:
            limit: Maximum number of results

        Returns:
            List of AuditResultRow with drift_error_count > 0
        """
        async with get_async_session() as session:
            stmt = (
                select(AuditResultRow)
                .where(AuditResultRow.drift_error_count > 0)
                .order_by(AuditResultRow.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_all_specs_latest(self) -> list[AuditResultRow]:
        """
        Get the latest audit for each spec that has been audited.

        Returns:
            List of AuditResultRow (one per spec, most recent)

        Teaching:
            gotcha: This uses a window function to get the latest audit per spec.
                    It's more efficient than N queries for N specs.
        """
        async with get_async_session() as session:
            from sqlalchemy import func

            # Subquery to get latest audit ID per spec
            subq = (
                select(
                    AuditResultRow.spec_path,
                    func.max(AuditResultRow.created_at).label("max_created"),
                )
                .group_by(AuditResultRow.spec_path)
                .subquery()
            )

            # Join to get full rows
            stmt = (
                select(AuditResultRow)
                .join(
                    subq,
                    (AuditResultRow.spec_path == subq.c.spec_path)
                    & (AuditResultRow.created_at == subq.c.max_created),
                )
                .order_by(AuditResultRow.spec_path)
            )

            result = await session.execute(stmt)
            return list(result.scalars().all())


# Global singleton store
_global_store: AuditStore | None = None


def get_audit_store() -> AuditStore:
    """Get the global audit store (singleton)."""
    global _global_store
    if _global_store is None:
        _global_store = AuditStore()
    return _global_store


def reset_audit_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


__all__ = ["AuditStore", "get_audit_store", "reset_audit_store"]
