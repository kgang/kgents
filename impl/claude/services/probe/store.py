"""
Probe Store: Database persistence for categorical law probe results.

> *"Every probe violation is witnessed. Every pattern is detected."*

This module provides database-backed storage for probe results:
- Save probe results (primarily failures)
- Query by probe_type, status, name
- Analyze failure patterns over time
- Track Crown Jewel health

Storage Pattern:
    - Primary: Database (probe_results table) for queryability
    - Tasteful: Store only failures by default (keep table lean)
    - Future: Optional D-gent semantic search for failure patterns

Teaching:
    gotcha: We use SQLAlchemy's async session. Always use `async with` for
            session lifecycle management (prevents connection leaks).

    principle: Tasteful - We only store failures, not successes.
               This keeps the table lean and focused on problems.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 3)
"""

from __future__ import annotations

import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from models.probe import ProbeResultRow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import get_async_session

if TYPE_CHECKING:
    from services.probe.types import ProbeResult, ProbeStatus, ProbeType


logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def _generate_probe_id() -> str:
    """Generate unique probe result ID."""
    return f"probe-{secrets.token_hex(8)}"


def _result_to_row(result: ProbeResult, probe_id: str) -> ProbeResultRow:
    """Convert ProbeResult to database row."""
    return ProbeResultRow(
        id=probe_id,
        name=result.name,
        probe_type=result.probe_type.value,
        status=result.status.value,
        details=result.details,
        duration_ms=result.duration_ms,
        mark_id=result.mark_id,
    )


# =============================================================================
# ProbeStore
# =============================================================================


class ProbeStore:
    """
    Database-backed storage for probe results.

    Philosophy:
        "The proof IS the decision. The mark IS the witness."
        Only emit marks on FAILURE to keep probes cheap.

    Example usage:
        >>> store = ProbeStore()
        >>> witness = await get_witness_persistence()
        >>>
        >>> # Save a failed probe
        >>> probe_id = await store.save_probe(
        ...     result=probe_result,
        ...     witness=witness,
        ... )
        >>>
        >>> # Get recent failures
        >>> failures = await store.get_recent_failures(hours=24)
        >>>
        >>> # Get identity law violations
        >>> identity_failures = await store.query_by_type(
        ...     probe_type=ProbeType.IDENTITY,
        ...     status=ProbeStatus.FAILED,
        ... )
    """

    def __init__(self) -> None:
        """Initialize probe store."""
        pass

    # =========================================================================
    # Save Operations
    # =========================================================================

    async def save_probe(
        self,
        result: ProbeResult,
        witness=None,  # WitnessPersistence | None
        store_all: bool = False,
    ) -> str | None:
        """
        Save a probe result with optional witness marking.

        Args:
            result: ProbeResult to save
            witness: WitnessPersistence instance (for creating mark on failure)
            store_all: If True, store all probes. If False, only store failures.

        Returns:
            The probe ID if saved, None if skipped

        Teaching:
            gotcha: By default, we only store FAILED probes to keep the table lean.
                    Set store_all=True to store all probes (e.g., for debugging).

            principle: Tasteful - We focus on problems, not successes.
                       This keeps the signal-to-noise ratio high.
        """
        from services.probe.types import ProbeStatus

        # Skip successful probes unless store_all=True
        if not store_all and result.status == ProbeStatus.PASSED:
            return None

        # Generate ID
        probe_id = _generate_probe_id()

        # Create witness mark on FAILURE
        mark_id = result.mark_id
        if not mark_id and witness and result.status == ProbeStatus.FAILED:
            mark_result = await witness.save_mark(
                action=f"Probe failed: {result.name}",
                reasoning=result.details,
                tags=["probe", f"type:{result.probe_type.value}", "failure"],
                author="categorical-probe",
            )
            mark_id = mark_result.mark_id
            logger.warning(f"Created witness mark {mark_id} for failed probe {result.name}")

        # Save to database
        async with get_async_session() as session:
            row = _result_to_row(result, probe_id)
            if mark_id:
                row.mark_id = mark_id
            session.add(row)
            await session.commit()
            logger.debug(f"Saved probe {probe_id}: {result.name} ({result.status.value})")

        return probe_id

    # =========================================================================
    # Query Operations
    # =========================================================================

    async def get_recent_failures(
        self,
        hours: int = 24,
        limit: int = 50,
    ) -> list[ProbeResultRow]:
        """
        Get recent probe failures within the last N hours.

        Args:
            hours: Look back this many hours
            limit: Maximum number of results

        Returns:
            List of ProbeResultRow with status=FAILED
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        async with get_async_session() as session:
            stmt = (
                select(ProbeResultRow)
                .where(ProbeResultRow.status == "failed")
                .where(ProbeResultRow.created_at >= cutoff)
                .order_by(ProbeResultRow.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def query_by_type(
        self,
        probe_type: ProbeType,
        status: ProbeStatus | None = None,
        limit: int = 50,
    ) -> list[ProbeResultRow]:
        """
        Query probes by type and optional status.

        Args:
            probe_type: Probe type to filter by
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of ProbeResultRow matching criteria

        Example:
            # Get all identity law failures
            identity_failures = await store.query_by_type(
                probe_type=ProbeType.IDENTITY,
                status=ProbeStatus.FAILED,
            )
        """
        async with get_async_session() as session:
            stmt = select(ProbeResultRow).where(ProbeResultRow.probe_type == probe_type.value)

            if status:
                stmt = stmt.where(ProbeResultRow.status == status.value)

            stmt = stmt.order_by(ProbeResultRow.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def query_by_name(
        self,
        name_pattern: str,
        limit: int = 50,
    ) -> list[ProbeResultRow]:
        """
        Query probes by name pattern (supports SQL LIKE).

        Args:
            name_pattern: Pattern to match (e.g., "health:brain%")
            limit: Maximum number of results

        Returns:
            List of ProbeResultRow matching pattern

        Example:
            # Get all brain health probes
            brain_health = await store.query_by_name("health:brain%")
        """
        async with get_async_session() as session:
            stmt = (
                select(ProbeResultRow)
                .where(ProbeResultRow.name.like(name_pattern))
                .order_by(ProbeResultRow.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_failure_count_by_type(self) -> dict[str, int]:
        """
        Get count of failures grouped by probe type.

        Returns:
            Dictionary mapping probe_type → failure_count

        Example:
            >>> counts = await store.get_failure_count_by_type()
            >>> print(counts)
            {"identity": 3, "associativity": 1, "health": 5}
        """
        async with get_async_session() as session:
            from sqlalchemy import func

            stmt = (
                select(
                    ProbeResultRow.probe_type,
                    func.count(ProbeResultRow.id).label("count"),
                )
                .where(ProbeResultRow.status == "failed")
                .group_by(ProbeResultRow.probe_type)
            )

            result = await session.execute(stmt)
            rows = result.all()

            return {row[0]: row[1] for row in rows}

    async def get_health_summary(self, hours: int = 24) -> dict[str, dict]:
        """
        Get health summary for Crown Jewels over the last N hours.

        Args:
            hours: Look back this many hours

        Returns:
            Dictionary mapping jewel_name → {total, failed, healthy}

        Example:
            >>> summary = await store.get_health_summary(hours=24)
            >>> print(summary)
            {
                "brain": {"total": 10, "failed": 0, "healthy": True},
                "witness": {"total": 8, "failed": 2, "healthy": False},
            }
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        async with get_async_session() as session:
            from sqlalchemy import func

            # Get all health probes in time window
            stmt = (
                select(ProbeResultRow)
                .where(ProbeResultRow.probe_type == "health")
                .where(ProbeResultRow.created_at >= cutoff)
            )

            result = await session.execute(stmt)
            probes = list(result.scalars().all())

            # Group by jewel name (extract from probe name like "health:brain")
            jewel_stats: dict[str, dict] = {}

            for probe in probes:
                # Extract jewel name from "health:jewel_name"
                parts = probe.name.split(":", 1)
                if len(parts) < 2:
                    continue

                jewel_name = parts[1].split(".", 1)[0]  # Get jewel before any dot

                if jewel_name not in jewel_stats:
                    jewel_stats[jewel_name] = {"total": 0, "failed": 0}

                jewel_stats[jewel_name]["total"] += 1
                if probe.status == "failed":
                    jewel_stats[jewel_name]["failed"] += 1

            # Add healthy flag
            for jewel_name, stats in jewel_stats.items():
                stats["healthy"] = stats["failed"] == 0

            return jewel_stats


# Global singleton store
_global_store: ProbeStore | None = None


def get_probe_store() -> ProbeStore:
    """Get the global probe store (singleton)."""
    global _global_store
    if _global_store is None:
        _global_store = ProbeStore()
    return _global_store


def reset_probe_store() -> None:
    """Reset the global store (for testing)."""
    global _global_store
    _global_store = None


__all__ = ["ProbeStore", "get_probe_store", "reset_probe_store"]
