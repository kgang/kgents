"""
Witness Crystal Adapter - D-gent Crystal backend for WitnessMark storage.

Uses Universe with WITNESS_MARK_SCHEMA for typed Crystal storage.
Provides same interface as current MarkStore for drop-in replacement.

Migration Status: Phase 3 - Crystal Storage Backend
- Feature flag: USE_CRYSTAL_STORAGE (env var)
- Drop-in replacement for SQL-based mark storage
- Uses D-gent Universe with WitnessMark schema

Philosophy:
    "Every mark is a datum. Every datum is a trace.
     The Crystal remembers what SQL forgets."

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/unified-data-crystal.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from agents.d.schemas.witness import WitnessMark
from agents.d.universe import Query, Universe, get_universe

logger = logging.getLogger(__name__)


# =============================================================================
# Result Types (Match persistence.py interface)
# =============================================================================


@dataclass
class MarkResult:
    """Result of a mark save operation."""

    mark_id: str
    action: str
    reasoning: str | None
    principles: list[str]
    tags: list[str]
    author: str
    timestamp: datetime
    datum_id: str | None = None
    parent_mark_id: str | None = None


# =============================================================================
# WitnessCrystalAdapter: Universe-backed Mark Storage
# =============================================================================


class WitnessCrystalAdapter:
    """
    Crystal-backed WitnessMark storage.

    Drop-in replacement for SQL-based MarkStore.
    Uses D-gent Universe with WITNESS_MARK_SCHEMA.

    Architecture:
        WitnessMark (frozen dataclass) → serialize → Datum → Universe → Backend

    Features:
        - Automatic backend selection (Postgres > SQLite > Memory)
        - Schema versioning for evolution
        - Causal lineage via parent_mark_id
        - Tag-based filtering (in-memory for now)

    Usage:
        >>> adapter = WitnessCrystalAdapter()
        >>> mark_id = await adapter.create_mark("Fixed bug", reasoning="Crashes on null input")
        >>> mark = await adapter.get_mark(mark_id)
        >>> marks = await adapter.query_marks(tags=["bugfix"])
    """

    def __init__(self, universe: Universe | None = None):
        """
        Initialize WitnessCrystalAdapter.

        Args:
            universe: Optional Universe instance (uses singleton if None)
        """
        self._universe = universe or get_universe()

        # Register WitnessMark type with Universe (idempotent)
        # This creates a DataclassSchema wrapper for serialization
        self._universe.register_type("witness.mark", WitnessMark)

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    async def create_mark(
        self,
        action: str,
        reasoning: str | None = None,
        tags: list[str] | None = None,
        principles: list[str] | None = None,
        author: str = "kent",
        metadata: dict[str, Any] | None = None,
        origin: str | None = None,
        parent_mark_id: str | None = None,
    ) -> str:
        """
        Create a new WitnessMark and store as Crystal.

        Args:
            action: What was done
            reasoning: Why it was done (optional but encouraged)
            tags: Classification tags (evidence tags, session tags, etc.)
            principles: Which principles were honored
            author: Who created this mark (default: "kent")
            metadata: Additional context metadata
            origin: Mark origin (default: "witness")
            parent_mark_id: Parent mark for causal lineage

        Returns:
            The datum ID (mark_id)

        Evidence Tags:
            - spec:{path}     — Links mark to a spec
            - evidence:impl   — Implementation evidence
            - evidence:test   — Test evidence
            - evidence:usage  — Usage evidence
            - evidence:run    — Test run record
            - evidence:pass   — Test passed
            - evidence:fail   — Test failed
        """
        # Validate parent exists if specified
        if parent_mark_id:
            parent = await self.get_mark(parent_mark_id)
            if not parent:
                raise ValueError(f"Parent mark not found: {parent_mark_id}")

        # Build context dict from metadata
        context = metadata or {}

        # Create WitnessMark dataclass (frozen, immutable)
        mark = WitnessMark(
            action=action,
            reasoning=reasoning or "",
            author=author,
            tags=tuple(tags or []),
            principles=tuple(principles or []),
            parent_mark_id=parent_mark_id,
            context=context,
        )

        # Store via Universe (schema registered in __init__)
        mark_id = await self._universe.store(mark, "witness.mark")

        logger.debug(f"Created mark {mark_id} by {author}: {action}")
        return mark_id

    async def get_mark(self, id: str) -> MarkResult | None:
        """
        Retrieve a mark by ID.

        Args:
            id: The mark ID to retrieve

        Returns:
            MarkResult or None if not found
        """
        # Get from Universe (returns WitnessMark or None)
        witness_mark = await self._universe.get(id)

        if witness_mark is None or not isinstance(witness_mark, WitnessMark):
            return None

        # Extract timestamp from context (injected by Universe.get)
        created_at = witness_mark.context.get("created_at")
        timestamp = (
            datetime.fromtimestamp(created_at, tz=UTC) if created_at else datetime.now(UTC)
        )

        # Convert to MarkResult (matches persistence.py interface)
        return MarkResult(
            mark_id=id,
            action=witness_mark.action,
            reasoning=witness_mark.reasoning or None,
            principles=list(witness_mark.principles),
            tags=list(witness_mark.tags),
            author=witness_mark.author,
            timestamp=timestamp,
            datum_id=id,
            parent_mark_id=witness_mark.parent_mark_id,
        )

    async def query_marks(
        self,
        tags: list[str] | None = None,
        tag_prefix: str | None = None,
        author: str | None = None,
        after: float | None = None,
        limit: int = 100,
    ) -> list[MarkResult]:
        """
        Query marks with optional filters.

        Note: Universe query is limited (schema, prefix, after, limit only).
        Complex filtering (tags, author) done in-memory.

        Args:
            tags: Filter by exact tag match (any of these tags)
            tag_prefix: Filter by tag prefix (e.g., "spec:" for all spec-related)
            author: Filter by author
            after: Filter by created_at > after (timestamp)
            limit: Maximum marks to return

        Returns:
            List of MarkResult objects, newest first
        """
        # Query Universe for witness.mark schema
        # Over-fetch to account for in-memory filtering
        query = Query(
            schema="witness.mark",
            after=after,
            limit=limit * 3,
        )

        witness_marks: list[WitnessMark] = await self._universe.query(query)

        # Filter in-memory
        marks = []
        for wm in witness_marks:
            # Apply author filter
            if author and wm.author != author:
                continue

            # Apply tag filters
            mark_tags = list(wm.tags)
            if tags and not any(t in mark_tags for t in tags):
                continue
            if tag_prefix and not any(t.startswith(tag_prefix) for t in mark_tags):
                continue

            # Extract datum ID and timestamp from context (injected by Universe.query)
            datum_id = wm.context.get("id", f"mark-{id(wm)}")  # Fallback to object id
            created_at = wm.context.get("created_at")
            timestamp = (
                datetime.fromtimestamp(created_at, tz=UTC) if created_at else datetime.now(UTC)
            )

            marks.append(
                MarkResult(
                    mark_id=datum_id,
                    action=wm.action,
                    reasoning=wm.reasoning or None,
                    principles=list(wm.principles),
                    tags=mark_tags,
                    author=wm.author,
                    timestamp=timestamp,
                    datum_id=datum_id,
                    parent_mark_id=wm.parent_mark_id,
                )
            )

        # Limit results
        return marks[:limit]

    async def get_causal_chain(self, id: str) -> list[MarkResult]:
        """
        Get causal ancestors of a mark (parent chain up to root).

        Args:
            id: The mark ID to get ancestry for

        Returns:
            List of MarkResult objects from mark to root (mark first, root last)
        """
        results: list[MarkResult] = []
        current_id: str | None = id
        visited: set[str] = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            mark = await self.get_mark(current_id)
            if not mark:
                break

            results.append(mark)
            current_id = mark.parent_mark_id

        return results


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WitnessCrystalAdapter",
    "MarkResult",
]
