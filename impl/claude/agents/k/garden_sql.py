"""
SQLPersonaGarden: PostgreSQL-backed PersonaGarden.

Provides durability through the Database Triad:
- PostgreSQL for persistent storage (ANCHOR)
- Automatic CDC via outbox triggers → Qdrant (ASSOCIATOR)
- Redis cache for hot patterns (SPARK)

This replaces JSON file storage with true transactional semantics
while maintaining the garden metaphor and full API compatibility.

Usage:
    from agents.k.garden_sql import SQLPersonaGarden, get_sql_garden

    # Connect to Database Triad
    garden = await get_sql_garden()

    # Use exactly like PersonaGarden
    await garden.plant_preference("Direct communication style")
    await garden.nurture_pattern("categorical", evidence="Used in 5 dialogues")
    stats = await garden.stats()

AGENTESE: self.soul.garden.durable
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional, Protocol, TypeVar

from .garden import (
    EntryType,
    GardenEntry,
    GardenLifecycle,
    GardenSeason,
    GardenStats,
    SeasonConfig,
)

if TYPE_CHECKING:
    from .hypnagogia import HypnagogicCycle

logger = logging.getLogger(__name__)

# Type variable for connection type (covariant for Protocol)
_T_co = TypeVar("_T_co", covariant=True)


# =============================================================================
# Database Protocol
# =============================================================================


class AsyncContextManager(Protocol[_T_co]):
    """Protocol for async context managers."""

    async def __aenter__(self) -> _T_co: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None: ...


class DatabasePool(Protocol):
    """Protocol for asyncpg connection pool."""

    def acquire(self) -> AsyncContextManager[Any]:
        """Acquire a connection from the pool (returns async context manager)."""
        ...

    async def close(self) -> None:
        """Close the pool."""
        ...


# =============================================================================
# SQLPersonaGarden
# =============================================================================


class SQLPersonaGarden:
    """
    PostgreSQL-backed PersonaGarden.

    Implements the same interface as PersonaGarden but stores entries
    in PostgreSQL with automatic CDC to Qdrant via outbox triggers.

    Benefits over JSON storage:
    - ACID transactions
    - Concurrent access
    - Automatic vector sync via CDC
    - Semantic search across gardens
    - Crash recovery

    Example:
        >>> garden = await SQLPersonaGarden.connect(database_url)
        >>> await garden.plant_preference("Concise communication")
        >>> await garden.close()
    """

    def __init__(
        self,
        pool: DatabasePool,
        season: Optional[GardenSeason] = None,
    ) -> None:
        """
        Initialize with a database connection pool.

        Args:
            pool: asyncpg connection pool
            season: Optional season override (defaults to auto-detect)
        """
        self._pool = pool
        self._season = season or self._detect_season()
        self._season_config = SeasonConfig.for_season(self._season)

        # Cache for auto-planted count (updated from DB on access)
        self._auto_planted_count = 0

    @classmethod
    async def connect(
        cls,
        database_url: str,
        min_size: int = 1,
        max_size: int = 5,
        season: Optional[GardenSeason] = None,
    ) -> "SQLPersonaGarden":
        """
        Create and connect a SQLPersonaGarden.

        Args:
            database_url: PostgreSQL connection string
            min_size: Minimum pool size
            max_size: Maximum pool size
            season: Optional season override

        Returns:
            Connected SQLPersonaGarden
        """
        try:
            import asyncpg

            pool = await asyncpg.create_pool(
                database_url,
                min_size=min_size,
                max_size=max_size,
            )

            garden = cls(pool=pool, season=season)
            logger.info(
                f"SQLPersonaGarden connected: {database_url.split('@')[1] if '@' in database_url else database_url}"
            )
            return garden

        except ImportError:
            raise RuntimeError(
                "asyncpg required for SQLPersonaGarden: pip install asyncpg"
            )

    async def close(self) -> None:
        """Close the connection pool."""
        await self._pool.close()

    def _detect_season(self) -> GardenSeason:
        """Detect season based on current month."""
        month = datetime.now().month
        if month in (3, 4, 5):
            return GardenSeason.SPRING
        elif month in (6, 7, 8):
            return GardenSeason.SUMMER
        elif month in (9, 10, 11):
            return GardenSeason.AUTUMN
        else:
            return GardenSeason.WINTER

    @property
    def season(self) -> GardenSeason:
        """Get current garden season."""
        return self._season

    @season.setter
    def season(self, value: GardenSeason) -> None:
        """Set garden season and update config."""
        self._season = value
        self._season_config = SeasonConfig.for_season(value)

    # ─────────────────────────────────────────────────────────────────────────
    # Planting
    # ─────────────────────────────────────────────────────────────────────────

    async def plant(
        self,
        content: str,
        entry_type: EntryType,
        source: str = "manual",
        confidence: float = 0.3,
        tags: Optional[list[str]] = None,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> GardenEntry:
        """
        Plant a new entry in the garden.

        The entry is written to PostgreSQL and automatically
        synced to Qdrant via the outbox trigger.
        """
        lifecycle = self._confidence_to_lifecycle(confidence)
        now = datetime.now(timezone.utc)

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO persona_garden (
                    content, entry_type, lifecycle, confidence, source,
                    planted_at, last_nurtured, evidence, occurrences,
                    tags, eigenvector_affinities
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
                )
                RETURNING id, content, entry_type, lifecycle, confidence, source,
                          planted_at, last_nurtured, evidence, occurrences,
                          tags, eigenvector_affinities
                """,
                content,
                entry_type.value,
                lifecycle.value,
                confidence,
                source,
                now,
                now,
                json.dumps([]),
                1,
                json.dumps(tags or []),
                json.dumps(eigenvector_affinities or {}),
            )

            return self._row_to_entry(row)

    async def plant_preference(
        self,
        content: str,
        confidence: float = 0.5,
        tags: Optional[list[str]] = None,
    ) -> GardenEntry:
        """Convenience method to plant a preference."""
        return await self.plant(
            content=content,
            entry_type=EntryType.PREFERENCE,
            source="manual",
            confidence=confidence,
            tags=tags,
        )

    async def plant_pattern(
        self,
        content: str,
        source: str = "hypnagogia",
        confidence: float = 0.3,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> GardenEntry:
        """Convenience method to plant a pattern."""
        return await self.plant(
            content=content,
            entry_type=EntryType.PATTERN,
            source=source,
            confidence=confidence,
            eigenvector_affinities=eigenvector_affinities,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Nurturing
    # ─────────────────────────────────────────────────────────────────────────

    async def nurture(
        self,
        entry_id: str,
        evidence: str,
        confidence_boost: float = 0.05,
    ) -> Optional[GardenEntry]:
        """
        Nurture an entry with evidence.

        Adds evidence, boosts confidence, and updates lifecycle.
        Change is automatically propagated to Qdrant via CDC.
        """
        async with self._pool.acquire() as conn:
            # First fetch current state
            row = await conn.fetchrow(
                "SELECT * FROM persona_garden WHERE id = $1",
                entry_id,
            )

            if row is None:
                return None

            if row["lifecycle"] == "compost":
                return self._row_to_entry(row)

            # Update entry
            current_evidence = json.loads(row["evidence"]) if row["evidence"] else []
            current_evidence.append(evidence)
            new_confidence = min(1.0, row["confidence"] + confidence_boost)
            new_lifecycle = self._confidence_to_lifecycle(new_confidence).value

            updated = await conn.fetchrow(
                """
                UPDATE persona_garden SET
                    evidence = $1,
                    occurrences = occurrences + 1,
                    last_nurtured = $2,
                    confidence = $3,
                    lifecycle = $4
                WHERE id = $5
                RETURNING *
                """,
                json.dumps(current_evidence),
                datetime.now(timezone.utc),
                new_confidence,
                new_lifecycle,
                entry_id,
            )

            return self._row_to_entry(updated)

    # ─────────────────────────────────────────────────────────────────────────
    # Querying
    # ─────────────────────────────────────────────────────────────────────────

    async def get(self, entry_id: str) -> Optional[GardenEntry]:
        """Get entry by ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM persona_garden WHERE id = $1",
                entry_id,
            )
            return self._row_to_entry(row) if row else None

    async def list_by_type(self, entry_type: EntryType) -> list[GardenEntry]:
        """List entries by type."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM persona_garden WHERE entry_type = $1 ORDER BY planted_at DESC",
                entry_type.value,
            )
            return [self._row_to_entry(row) for row in rows]

    async def list_by_lifecycle(self, lifecycle: GardenLifecycle) -> list[GardenEntry]:
        """List entries by lifecycle stage."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM persona_garden WHERE lifecycle = $1 ORDER BY planted_at DESC",
                lifecycle.value,
            )
            return [self._row_to_entry(row) for row in rows]

    async def seeds(self) -> list[GardenEntry]:
        """Get all seeds."""
        return await self.list_by_lifecycle(GardenLifecycle.SEED)

    async def saplings(self) -> list[GardenEntry]:
        """Get all saplings."""
        return await self.list_by_lifecycle(GardenLifecycle.SAPLING)

    async def trees(self) -> list[GardenEntry]:
        """Get all trees (established patterns)."""
        return await self.list_by_lifecycle(GardenLifecycle.TREE)

    async def flowers(self) -> list[GardenEntry]:
        """Get all flowers (peak insights)."""
        return await self.list_by_lifecycle(GardenLifecycle.FLOWER)

    async def preferences(self) -> list[GardenEntry]:
        """Get all preferences."""
        return await self.list_by_type(EntryType.PREFERENCE)

    async def patterns(self) -> list[GardenEntry]:
        """Get all patterns."""
        return await self.list_by_type(EntryType.PATTERN)

    @property
    def entries(self) -> dict[str, GardenEntry]:
        """
        Get all entries.

        NOTE: This is synchronous for compatibility but hits the DB.
        Prefer async methods in new code.
        """
        import asyncio

        async def _get_all() -> dict[str, GardenEntry]:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch("SELECT * FROM persona_garden")
                return {str(row["id"]): self._row_to_entry(row) for row in rows}

        try:
            asyncio.get_running_loop()
            # If we're in an async context, schedule as task
            asyncio.ensure_future(_get_all())
            return {}  # Return empty dict, caller should use async
        except RuntimeError:
            # No running loop, create one
            return asyncio.run(_get_all())

    # ─────────────────────────────────────────────────────────────────────────
    # Composting
    # ─────────────────────────────────────────────────────────────────────────

    async def compost(self, entry_id: str) -> Optional[GardenEntry]:
        """Compost an entry (mark as deprecated)."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                UPDATE persona_garden SET
                    lifecycle = 'compost',
                    last_nurtured = $1
                WHERE id = $2
                RETURNING *
                """,
                datetime.now(timezone.utc),
                entry_id,
            )
            return self._row_to_entry(row) if row else None

    async def prune_stale(self, days_threshold: int = 30) -> list[GardenEntry]:
        """Compost entries that haven't been nurtured recently."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                UPDATE persona_garden SET
                    lifecycle = 'compost'
                WHERE lifecycle != 'compost'
                AND last_nurtured < NOW() - ($1 || ' days')::INTERVAL
                RETURNING *
                """,
                str(days_threshold),
            )
            return [self._row_to_entry(row) for row in rows]

    async def staleness_decay(self) -> list[tuple[GardenEntry, float]]:
        """Apply natural confidence decay to stale entries."""
        decay_rate = self._season_config.staleness_decay_rate

        if self._season == GardenSeason.WINTER:
            decay_rate *= self._season_config.winter_decay_multiplier

        async with self._pool.acquire() as conn:
            # Get entries that need decay
            rows = await conn.fetch(
                """
                SELECT *,
                       EXTRACT(EPOCH FROM (NOW() - last_nurtured)) / 86400 AS staleness_days
                FROM persona_garden
                WHERE lifecycle != 'compost'
                AND last_nurtured < NOW() - INTERVAL '1 day'
                """
            )

            decayed: list[tuple[GardenEntry, float]] = []

            for row in rows:
                staleness = float(row["staleness_days"])
                decay_amount = (staleness - 1) * decay_rate

                if decay_amount > 0.001:
                    new_confidence = max(0.0, row["confidence"] - decay_amount)
                    new_lifecycle = (
                        "compost"
                        if new_confidence < 0.1
                        else self._confidence_to_lifecycle(new_confidence).value
                    )

                    updated = await conn.fetchrow(
                        """
                        UPDATE persona_garden SET
                            confidence = $1,
                            lifecycle = $2
                        WHERE id = $3
                        RETURNING *
                        """,
                        new_confidence,
                        new_lifecycle,
                        row["id"],
                    )

                    decayed.append((self._row_to_entry(updated), decay_amount))

            return decayed

    # ─────────────────────────────────────────────────────────────────────────
    # Hypnagogia Integration
    # ─────────────────────────────────────────────────────────────────────────

    async def sync_from_hypnagogia(self, cycle: "HypnagogicCycle") -> int:
        """Sync patterns from HypnagogicCycle."""
        synced = 0

        for pattern_id, pattern in cycle.patterns.items():
            async with self._pool.acquire() as conn:
                # Check if exists
                existing = await conn.fetchrow(
                    "SELECT id FROM persona_garden WHERE content = $1",
                    pattern.content,
                )

                if existing:
                    # Update existing
                    await conn.execute(
                        """
                        UPDATE persona_garden SET
                            occurrences = GREATEST(occurrences, $1),
                            last_nurtured = $2
                        WHERE id = $3
                        """,
                        pattern.occurrences,
                        datetime.now(timezone.utc),
                        existing["id"],
                    )
                else:
                    # Create new
                    confidence = self._pattern_maturity_to_confidence(
                        pattern.maturity.value
                    )
                    await self.plant_pattern(
                        content=pattern.content,
                        source="hypnagogia",
                        confidence=confidence,
                        eigenvector_affinities=pattern.eigenvector_affinities,
                    )
                    synced += 1

        return synced

    async def auto_plant_from_dialogue(
        self,
        message: str,
        response: str,
        detected_patterns: Optional[list[str]] = None,
        eigenvector_affinities: Optional[dict[str, float]] = None,
    ) -> list[GardenEntry]:
        """Auto-plant patterns detected from dialogue."""
        affected: list[GardenEntry] = []

        _ = self._season_config.auto_plant_threshold  # For future use
        base_confidence = 0.25

        if self._season == GardenSeason.SPRING:
            base_confidence += self._season_config.spring_plant_boost

        if detected_patterns:
            for pattern in detected_patterns:
                similar = await self._find_similar_entry(pattern, 0.7)
                if similar:
                    updated = await self.nurture(
                        similar.id,
                        f"Dialogue: {message[:50]}",
                        confidence_boost=0.05,
                    )
                    if updated:
                        affected.append(updated)
                else:
                    entry = await self.plant_pattern(
                        content=pattern,
                        source="dialogue",
                        confidence=base_confidence,
                        eigenvector_affinities=eigenvector_affinities,
                    )
                    self._auto_planted_count += 1
                    affected.append(entry)

        return affected

    async def _find_similar_entry(
        self, content: str, threshold: float
    ) -> Optional[GardenEntry]:
        """Find an entry with similar content using trigram similarity."""
        if not content or not content.strip():
            return None

        async with self._pool.acquire() as conn:
            # Use PostgreSQL trigram similarity
            row = await conn.fetchrow(
                """
                SELECT *,
                       similarity(content, $1) AS sim
                FROM persona_garden
                WHERE lifecycle != 'compost'
                AND similarity(content, $1) >= $2
                ORDER BY sim DESC
                LIMIT 1
                """,
                content,
                threshold,
            )

            return self._row_to_entry(row) if row else None

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────

    async def stats(self) -> GardenStats:
        """Get garden statistics."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE entry_type = 'preference') AS preferences,
                    COUNT(*) FILTER (WHERE entry_type = 'pattern') AS patterns,
                    COUNT(*) FILTER (WHERE entry_type = 'value') AS values,
                    COUNT(*) FILTER (WHERE entry_type = 'behavior') AS behaviors,
                    COUNT(*) FILTER (WHERE entry_type = 'insight') AS insights,
                    COUNT(*) FILTER (WHERE lifecycle = 'seed') AS seeds,
                    COUNT(*) FILTER (WHERE lifecycle = 'sapling') AS saplings,
                    COUNT(*) FILTER (WHERE lifecycle = 'tree') AS trees,
                    COUNT(*) FILTER (WHERE lifecycle = 'flower') AS flowers,
                    COUNT(*) FILTER (WHERE lifecycle = 'compost') AS compost,
                    AVG(confidence) AS avg_confidence,
                    SUM(jsonb_array_length(evidence::jsonb)) AS total_evidence,
                    EXTRACT(EPOCH FROM (NOW() - MIN(planted_at))) / 86400 AS oldest_days,
                    EXTRACT(EPOCH FROM (NOW() - MAX(planted_at))) / 86400 AS newest_days,
                    COUNT(*) FILTER (WHERE source = 'dialogue') AS auto_planted
                FROM persona_garden
                """
            )

            if row["total"] == 0:
                return GardenStats(
                    total_entries=0,
                    by_type={},
                    by_lifecycle={},
                    average_confidence=0.0,
                    total_evidence=0,
                    oldest_entry_days=0.0,
                    newest_entry_days=0.0,
                    current_season=self._season,
                    auto_planted_count=0,
                )

            return GardenStats(
                total_entries=row["total"],
                by_type={
                    "preference": row["preferences"],
                    "pattern": row["patterns"],
                    "value": row["values"],
                    "behavior": row["behaviors"],
                    "insight": row["insights"],
                },
                by_lifecycle={
                    "seed": row["seeds"],
                    "sapling": row["saplings"],
                    "tree": row["trees"],
                    "flower": row["flowers"],
                    "compost": row["compost"],
                },
                average_confidence=float(row["avg_confidence"] or 0),
                total_evidence=int(row["total_evidence"] or 0),
                oldest_entry_days=float(row["oldest_days"] or 0),
                newest_entry_days=float(row["newest_days"] or 0),
                current_season=self._season,
                auto_planted_count=int(row["auto_planted"] or 0),
            )

    # ─────────────────────────────────────────────────────────────────────────
    # Formatting
    # ─────────────────────────────────────────────────────────────────────────

    def format_summary(self) -> str:
        """Format garden summary for display."""
        import asyncio

        async def _format() -> str:
            stats = await self.stats()

            if stats.total_entries == 0:
                return "[GARDEN-SQL] Empty - no patterns planted yet"

            lines = [
                "[GARDEN-SQL] PersonaGarden Summary (PostgreSQL)",
                "",
                f"  Total entries: {stats.total_entries}",
                "",
                "  By lifecycle:",
            ]

            lifecycle_icons = {
                "seed": ".",
                "sapling": "|",
                "tree": "T",
                "flower": "*",
                "compost": "~",
            }

            for lc in ["seed", "sapling", "tree", "flower", "compost"]:
                count = stats.by_lifecycle.get(lc, 0)
                icon = lifecycle_icons.get(lc, " ")
                if count > 0:
                    lines.append(f"    {icon} {lc}: {count}")

            return "\n".join(lines)

        try:
            asyncio.get_running_loop()
            return "[GARDEN-SQL] (use async stats() for details)"
        except RuntimeError:
            return asyncio.run(_format())

    def format_entry(self, entry: GardenEntry) -> str:
        """Format a single entry for display."""
        lifecycle_icons = {
            "seed": ".",
            "sapling": "|",
            "tree": "T",
            "flower": "*",
            "compost": "~",
        }
        icon = lifecycle_icons.get(entry.lifecycle.value, " ")

        lines = [
            f"{icon} [{entry.entry_type.value}] {entry.content}",
            f"  Confidence: {entry.confidence:.0%}",
            f"  Source: {entry.source}",
            f"  Age: {entry.age_days:.1f} days",
            f"  Evidence: {len(entry.evidence)} items",
        ]

        if entry.tags:
            lines.append(f"  Tags: {', '.join(entry.tags)}")

        return "\n".join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _row_to_entry(self, row: Any) -> GardenEntry:
        """Convert database row to GardenEntry."""
        return GardenEntry(
            id=str(row["id"]),
            content=row["content"],
            entry_type=EntryType(row["entry_type"]),
            lifecycle=GardenLifecycle(row["lifecycle"]),
            confidence=float(row["confidence"]),
            source=row["source"],
            planted_at=row["planted_at"].replace(tzinfo=timezone.utc),
            last_nurtured=row["last_nurtured"].replace(tzinfo=timezone.utc),
            evidence=json.loads(row["evidence"]) if row["evidence"] else [],
            occurrences=row["occurrences"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            eigenvector_affinities=json.loads(row["eigenvector_affinities"])
            if row["eigenvector_affinities"]
            else {},
        )

    def _confidence_to_lifecycle(self, confidence: float) -> GardenLifecycle:
        """Map confidence to lifecycle stage."""
        if confidence >= 0.9:
            return GardenLifecycle.FLOWER
        elif confidence >= 0.7:
            return GardenLifecycle.TREE
        elif confidence >= 0.4:
            return GardenLifecycle.SAPLING
        else:
            return GardenLifecycle.SEED

    def _pattern_maturity_to_confidence(self, maturity: str) -> float:
        """Map HypnagogicCycle pattern maturity to confidence."""
        maturity_confidence = {
            "seed": 0.3,
            "sapling": 0.5,
            "tree": 0.8,
            "compost": 0.1,
        }
        return maturity_confidence.get(maturity, 0.3)


# =============================================================================
# Factory Functions
# =============================================================================


_sql_garden_instance: Optional[SQLPersonaGarden] = None


async def get_sql_garden(
    database_url: Optional[str] = None,
) -> SQLPersonaGarden:
    """
    Get or create the global SQLPersonaGarden instance.

    Args:
        database_url: PostgreSQL connection string. If not provided,
                     uses DATABASE_URL environment variable.

    Returns:
        Connected SQLPersonaGarden
    """
    global _sql_garden_instance

    if _sql_garden_instance is None:
        import os

        url = database_url or os.environ.get(
            "DATABASE_URL",
            "postgresql://triad:triad-dev-password@localhost:5432/triad",
        )
        _sql_garden_instance = await SQLPersonaGarden.connect(url)

    return _sql_garden_instance


async def close_sql_garden() -> None:
    """Close the global SQLPersonaGarden instance."""
    global _sql_garden_instance

    if _sql_garden_instance is not None:
        await _sql_garden_instance.close()
        _sql_garden_instance = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "SQLPersonaGarden",
    "get_sql_garden",
    "close_sql_garden",
]
