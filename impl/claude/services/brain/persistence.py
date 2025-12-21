"""
Brain Persistence: TableAdapter + D-gent integration for Brain Crown Jewel.

Owns domain semantics for Brain storage:
- WHEN to persist (on capture, on access for usage tracking)
- WHY to persist (dual-track: fast queries + semantic search)
- HOW to compose (TableAdapter for metadata, D-gent for semantic content)

AGENTESE aspects exposed:
- capture: Store content with semantic embedding
- search: Semantic search for similar memories
- surface: Serendipity from the void
- manifest: Show brain status

Differance Integration (Phase 6B):
- capture() → trace with alternatives (auto_tag, defer_embedding)
- surface() → trace with alternatives (different_seed, context_weighted)
- delete() → trace with alternatives (archive_instead, soft_delete)
- search/get/list → NO traces (read-only, high frequency)

See: docs/skills/metaphysical-fullstack.md
See: plans/differance-crown-jewel-wiring.md (Phase 6B)

Teaching:
    gotcha: Dual-track storage means Crystal table AND D-gent must both succeed.
            If one fails after the other succeeds, you get "ghost" memories.
            (Evidence: test_brain_persistence.py::test_heal_ghosts)

    gotcha: capture() returns immediately but trace recording is fire-and-forget.
            Never await the trace task or you'll block the hot path.
            (Evidence: test_brain_persistence.py::test_capture_performance)

    gotcha: search() updates access_count via touch(). High-frequency searches
            will cause write amplification. Consider batching access updates.
            (Evidence: test_brain_persistence.py::test_access_tracking)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from agents.differance.alternatives import get_alternatives
from agents.differance.integration import DifferanceIntegration
from models.brain import Crystal, CrystalTag, TeachingCrystal

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def _format_datetime(dt: datetime | str | None) -> str:
    """Format datetime to ISO string, handling SQLite string returns."""
    if dt is None:
        return ""
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


@dataclass
class CaptureResult:
    """Result of a capture operation."""

    crystal_id: str
    content: str
    summary: str
    captured_at: str
    has_embedding: bool
    storage: str  # "sqlite" | "postgres"
    datum_id: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Result of a search operation."""

    crystal_id: str
    content: str
    summary: str
    similarity: float
    captured_at: str
    is_stale: bool = False


@dataclass
class BrainStatus:
    """Brain health status."""

    total_crystals: int
    vector_count: int
    has_semantic: bool
    coherency_rate: float
    ghosts_healed: int
    storage_path: str
    storage_backend: str  # "sqlite" | "postgres"


@dataclass
class CrystallizeResult:
    """Result of crystallizing a teaching moment."""

    teaching_id: str
    insight: str
    severity: Literal["info", "warning", "critical"]
    source_module: str
    source_symbol: str
    is_new: bool  # True if newly created, False if already existed
    evidence_verified: bool


class BrainPersistence:
    """
    Persistence layer for Brain Crown Jewel.

    Composes:
    - TableAdapter[Crystal]: Fast queries by tag, recency, access frequency
    - D-gent: Semantic search, associative connections

    Domain Semantics:
    - Crystals are the atomic units of memory
    - Each crystal has queryable metadata AND semantic content
    - Usage tracking enables relevance scoring

    Example:
        persistence = BrainPersistence(
            table_adapter=TableAdapter(Crystal, session_factory),
            dgent=dgent_router,
        )

        result = await persistence.capture("Python is great for data science")
        results = await persistence.search("programming language", limit=5)
    """

    def __init__(
        self,
        table_adapter: TableAdapter[Crystal],
        dgent: DgentProtocol,
        embedder: Any | None = None,  # L-gent for embeddings
    ) -> None:
        self.table = table_adapter
        self.dgent = dgent
        self.embedder = embedder
        self._ghosts_healed = 0
        # Differance integration for trace recording (Phase 6B)
        self._differance = DifferanceIntegration("brain")

    # =========================================================================
    # AGENTESE Aspects
    # =========================================================================

    async def capture(
        self,
        content: str,
        tags: list[str] | None = None,
        source_type: str = "capture",
        source_ref: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaptureResult:
        """
        Capture content to holographic memory.

        AGENTESE: self.memory.capture

        Dual-track storage:
        1. Store semantic content in D-gent (for associations)
        2. Store queryable metadata in Crystal table (for fast queries)

        Args:
            content: The content to capture
            tags: Optional tags for categorization
            source_type: Source type ("capture", "import", "generation")
            source_ref: Source reference (e.g., file path)
            metadata: Additional metadata for D-gent

        Returns:
            CaptureResult with crystal_id and storage details
        """
        tags = tags or []
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        crystal_id = f"crystal-{uuid.uuid4().hex[:12]}"

        # 1. Store semantic content in D-gent
        datum_metadata = {
            "type": "brain_crystal",
            "source_type": source_type,
            "source_ref": source_ref,
            **(metadata or {}),
        }

        datum = Datum(
            id=f"brain-{crystal_id}",
            content=content.encode("utf-8"),
            created_at=time.time(),
            causal_parent=None,
            metadata=datum_metadata,
        )

        datum_id = await self.dgent.put(datum)

        # 2. Create summary (first 100 chars for now, could use LLM later)
        summary = content[:200].strip()
        if len(content) > 200:
            summary += "..."

        # 3. Store queryable metadata in Crystal table
        async with self.table.session_factory() as session:
            crystal = Crystal(
                id=crystal_id,
                content_hash=content_hash,
                summary=summary,
                tags=tags,
                datum_id=datum_id,
                source_type=source_type,
                source_ref=source_ref,
                access_count=0,
                last_accessed=None,
            )
            session.add(crystal)

            # Add normalized tags
            for tag in tags:
                crystal_tag = CrystalTag(
                    crystal_id=crystal_id,
                    tag=tag,
                )
                session.add(crystal_tag)

            await session.commit()

        # Check if we have embeddings
        has_embedding = self.embedder is not None

        result = CaptureResult(
            crystal_id=crystal_id,
            content=content,
            summary=summary,
            captured_at=datetime.now(UTC).isoformat(),
            has_embedding=has_embedding,
            storage="postgres"
            if "postgres" in str(self.table.session_factory).lower()
            else "sqlite",
            datum_id=datum_id,
            tags=tags,
        )

        # Fire-and-forget trace recording (Phase 6B)
        # Non-blocking: don't await, don't slow down capture
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                self._differance.record(
                    operation="capture",
                    inputs=(content[:100],),  # Truncate for trace
                    output=crystal_id,
                    context=f"Captured {source_type}",
                    alternatives=get_alternatives("brain", "capture"),
                )
            )
        except RuntimeError:
            # No event loop - skip trace (graceful degradation)
            logger.debug("No event loop for capture trace recording")

        return result

    async def search(
        self,
        query: str,
        limit: int = 10,
        tags: list[str] | None = None,
    ) -> list[SearchResult]:
        """
        Semantic search for similar memories.

        AGENTESE: self.memory.ghost.surface

        Uses D-gent for semantic search, then enriches with Crystal metadata.

        Args:
            query: Search query
            limit: Maximum results
            tags: Filter by tags (optional)

        Returns:
            List of SearchResult sorted by similarity
        """
        results: list[SearchResult] = []

        # Strategy 1: If we have embeddings, use semantic search
        if self.embedder is not None:
            # TODO: Implement vector search via L-gent
            pass

        # Strategy 2: Fall back to recent crystals with keyword match
        async with self.table.session_factory() as session:
            stmt = select(Crystal).order_by(Crystal.created_at.desc()).limit(limit * 2)

            # Filter by tags if specified
            if tags:
                stmt = stmt.where(Crystal.tags.contains(tags))

            result = await session.execute(stmt)
            crystals = result.scalars().all()

            query_lower = query.lower()
            for crystal in crystals:
                # Simple keyword matching for fallback
                # Get content from D-gent if available
                content = crystal.summary
                if crystal.datum_id:
                    datum = await self.dgent.get(crystal.datum_id)
                    if datum:
                        content = datum.content.decode("utf-8")

                # Calculate basic similarity (keyword-based)
                similarity = 0.0
                content_lower = content.lower()
                query_words = query_lower.split()
                matches = sum(1 for word in query_words if word in content_lower)
                if query_words:
                    similarity = matches / len(query_words)

                if similarity > 0 or not query:  # Include all if no query
                    results.append(
                        SearchResult(
                            crystal_id=crystal.id,
                            content=content,
                            summary=crystal.summary,
                            similarity=similarity,
                            captured_at=_format_datetime(crystal.created_at),
                            is_stale=False,
                        )
                    )

                    # Touch the crystal to update access tracking
                    crystal.touch()

            await session.commit()

        # Sort by similarity descending
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:limit]

    async def surface(
        self,
        context: str | None = None,
        entropy: float = 0.7,
    ) -> SearchResult | None:
        """
        Surface a serendipitous memory from the void.

        AGENTESE: void.memory.surface

        If context is provided, bias toward related memories.
        Otherwise, return a random-ish crystal.

        Args:
            context: Optional context to bias selection
            entropy: How random (0.0 = most relevant, 1.0 = random)

        Returns:
            SearchResult or None if brain is empty
        """
        async with self.table.session_factory() as session:
            # Get total count
            count_result = await session.execute(select(func.count()).select_from(Crystal))
            total = count_result.scalar() or 0

            if total == 0:
                return None

            # If context provided, search and apply entropy
            if context:
                results = await self.search(context, limit=10)
                if results:
                    # Apply entropy to selection
                    import random

                    if random.random() < entropy and len(results) > 1:
                        # Pick a random result, not the best
                        return random.choice(results[1:])
                    return results[0]

            # Random selection from all crystals
            import random

            offset = random.randint(0, max(0, total - 1))
            stmt = select(Crystal).offset(offset).limit(1)
            result = await session.execute(stmt)
            crystal = result.scalar_one_or_none()

            if crystal is None:
                return None

            # Get content from D-gent
            content = crystal.summary
            if crystal.datum_id:
                datum = await self.dgent.get(crystal.datum_id)
                if datum:
                    content = datum.content.decode("utf-8")

            # Touch for access tracking
            crystal.touch()
            await session.commit()

            result = SearchResult(
                crystal_id=crystal.id,
                content=content,
                summary=crystal.summary,
                similarity=1.0 - entropy,  # Surprise factor
                captured_at=_format_datetime(crystal.created_at),
                is_stale=False,
            )

            # Fire-and-forget trace recording (Phase 6B)
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    self._differance.record(
                        operation="surface",
                        inputs=(context[:50] if context else "random",),
                        output=crystal.id,
                        context=f"Surfaced with entropy={entropy:.2f}",
                        alternatives=get_alternatives("brain", "surface"),
                    )
                )
            except RuntimeError:
                logger.debug("No event loop for surface trace recording")

            return result

    async def manifest(self) -> BrainStatus:
        """
        Get brain health status.

        AGENTESE: self.memory.manifest

        Returns:
            BrainStatus with crystal counts and health metrics
        """
        async with self.table.session_factory() as session:
            # Count crystals
            count_result = await session.execute(select(func.count()).select_from(Crystal))
            total_crystals = count_result.scalar() or 0

            # Count crystals with datum_id (linked to D-gent)
            linked_result = await session.execute(
                select(func.count()).select_from(Crystal).where(Crystal.datum_id.isnot(None))
            )
            linked_count = linked_result.scalar() or 0

        # Calculate coherency (how many crystals have D-gent links)
        coherency_rate = linked_count / total_crystals if total_crystals > 0 else 1.0

        return BrainStatus(
            total_crystals=total_crystals,
            vector_count=0,  # TODO: Count actual vectors when L-gent is wired
            has_semantic=self.embedder is not None,
            coherency_rate=coherency_rate,
            ghosts_healed=self._ghosts_healed,
            storage_path="~/.local/share/kgents/brain",
            storage_backend="postgres"
            if "postgres" in str(self.table.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Additional Domain Methods
    # =========================================================================

    async def get_by_id(self, crystal_id: str) -> SearchResult | None:
        """Get a specific crystal by ID."""
        async with self.table.session_factory() as session:
            crystal = await session.get(Crystal, crystal_id)
            if crystal is None:
                return None

            content = crystal.summary
            if crystal.datum_id:
                datum = await self.dgent.get(crystal.datum_id)
                if datum:
                    content = datum.content.decode("utf-8")

            crystal.touch()
            await session.commit()

            return SearchResult(
                crystal_id=crystal.id,
                content=content,
                summary=crystal.summary,
                similarity=1.0,
                captured_at=_format_datetime(crystal.created_at),
                is_stale=False,
            )

    async def list_recent(self, limit: int = 10) -> list[SearchResult]:
        """List recent crystals."""
        async with self.table.session_factory() as session:
            stmt = select(Crystal).order_by(Crystal.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            crystals = result.scalars().all()

            results = []
            for crystal in crystals:
                content = crystal.summary
                if crystal.datum_id:
                    datum = await self.dgent.get(crystal.datum_id)
                    if datum:
                        content = datum.content.decode("utf-8")

                results.append(
                    SearchResult(
                        crystal_id=crystal.id,
                        content=content,
                        summary=crystal.summary,
                        similarity=1.0,
                        captured_at=_format_datetime(crystal.created_at),
                        is_stale=False,
                    )
                )

            return results

    async def list_by_tag(self, tag: str, limit: int = 10) -> list[SearchResult]:
        """List crystals with a specific tag."""
        async with self.table.session_factory() as session:
            stmt = (
                select(Crystal)
                .join(CrystalTag)
                .where(CrystalTag.tag == tag)
                .order_by(Crystal.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            crystals = result.scalars().all()

            results = []
            for crystal in crystals:
                content = crystal.summary
                if crystal.datum_id:
                    datum = await self.dgent.get(crystal.datum_id)
                    if datum:
                        content = datum.content.decode("utf-8")

                results.append(
                    SearchResult(
                        crystal_id=crystal.id,
                        content=content,
                        summary=crystal.summary,
                        similarity=1.0,
                        captured_at=_format_datetime(crystal.created_at),
                        is_stale=False,
                    )
                )

            return results

    async def delete(self, crystal_id: str) -> bool:
        """Delete a crystal and its D-gent datum."""
        async with self.table.session_factory() as session:
            crystal = await session.get(Crystal, crystal_id)
            if crystal is None:
                return False

            # Capture summary before deletion for trace
            deleted_summary = crystal.summary[:50] if crystal.summary else "unknown"

            # Delete from D-gent first
            if crystal.datum_id:
                await self.dgent.delete(crystal.datum_id)

            # Delete from table (cascade deletes tags)
            await session.delete(crystal)
            await session.commit()

            # Fire-and-forget trace recording (Phase 6B)
            # Record what was lost — irreversible operation
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    self._differance.record(
                        operation="delete",
                        inputs=(crystal_id,),
                        output=f"deleted:{crystal_id}",
                        context=f"Deleted crystal: {deleted_summary}...",
                        alternatives=get_alternatives("brain", "delete"),
                    )
                )
            except RuntimeError:
                logger.debug("No event loop for delete trace recording")

            return True

    async def heal_ghosts(self) -> int:
        """
        Heal ghost memories (crystals without D-gent datums).

        Returns count of healed ghosts.
        """
        healed = 0
        async with self.table.session_factory() as session:
            # Find crystals with broken D-gent links
            stmt = select(Crystal).where(Crystal.datum_id.isnot(None))
            result = await session.execute(stmt)
            crystals = result.scalars().all()

            for crystal in crystals:
                if crystal.datum_id:
                    datum = await self.dgent.get(crystal.datum_id)
                    if datum is None:
                        # Ghost found - recreate datum from summary
                        new_datum = Datum(
                            id=crystal.datum_id,
                            content=crystal.summary.encode("utf-8"),
                            created_at=time.time(),
                            causal_parent=None,
                            metadata={"type": "brain_crystal", "healed": "true"},
                        )
                        await self.dgent.put(new_datum)
                        healed += 1

            await session.commit()

        self._ghosts_healed += healed
        return healed

    # =========================================================================
    # Teaching Crystal Crystallization (Memory-First Docs)
    # =========================================================================

    async def crystallize_teaching(
        self,
        insight: str,
        severity: Literal["info", "warning", "critical"],
        source_module: str,
        source_symbol: str,
        evidence: str | None = None,
        source_commit: str | None = None,
    ) -> CrystallizeResult:
        """
        Crystallize a teaching moment for persistence.

        AGENTESE: self.memory.crystallize_teaching

        The Persistence Law: Teaching moments extracted from code
        MUST be crystallized in Brain.

        Args:
            insight: The gotcha text
            severity: "info" | "warning" | "critical"
            source_module: Module path (e.g., "services.brain.persistence")
            source_symbol: Symbol name (e.g., "BrainPersistence.capture")
            evidence: Test reference (e.g., "test_persistence.py::test_capture")
            source_commit: Git SHA where learned

        Returns:
            CrystallizeResult with teaching_id and status

        Teaching:
            gotcha: Deduplication is by (source_module, source_symbol, insight hash).
                    Same gotcha from same symbol won't create duplicates.
                    (Evidence: test_crystallization.py::test_deduplication)
        """
        # Generate deterministic ID for deduplication
        # Hash all three components to stay under 64 char limit
        id_source = f"{source_module}:{source_symbol}:{insight}"
        teaching_id = f"t-{hashlib.sha256(id_source.encode()).hexdigest()[:50]}"

        # Check for existing crystal (deduplication)
        async with self.table.session_factory() as session:
            existing = await session.get(TeachingCrystal, teaching_id)

            if existing is not None:
                # Already crystallized - return existing
                # Cast severity to Literal (DB stores as string)
                sev = existing.severity
                if sev not in ("info", "warning", "critical"):
                    sev = "info"
                return CrystallizeResult(
                    teaching_id=teaching_id,
                    insight=existing.insight,
                    severity=sev,  # Validated above
                    source_module=existing.source_module,
                    source_symbol=existing.source_symbol,
                    is_new=False,
                    evidence_verified=existing.evidence is not None,
                )

            # Create new teaching crystal
            # born_at uses database default func.now() - don't pass Python datetime
            teaching = TeachingCrystal(
                id=teaching_id,
                insight=insight,
                severity=severity,
                evidence=evidence,
                source_module=source_module,
                source_symbol=source_symbol,
                source_commit=source_commit,
                # born_at: uses database default
                died_at=None,
                successor_module=None,
                successor_symbol=None,
                applies_to=[],
            )
            session.add(teaching)
            await session.commit()

            return CrystallizeResult(
                teaching_id=teaching_id,
                insight=insight,
                severity=severity,
                source_module=source_module,
                source_symbol=source_symbol,
                is_new=True,
                evidence_verified=evidence is not None,
            )

    async def get_alive_teaching(
        self,
        limit: int = 100,
        severity: Literal["info", "warning", "critical"] | None = None,
    ) -> list[TeachingCrystal]:
        """
        Get all alive (non-extinct) teaching crystals.

        AGENTESE: self.memory.teaching.list

        Args:
            limit: Maximum results
            severity: Filter by severity (optional)

        Returns:
            List of TeachingCrystal ordered by creation date
        """
        async with self.table.session_factory() as session:
            stmt = (
                select(TeachingCrystal)
                .where(TeachingCrystal.died_at.is_(None))
                .order_by(TeachingCrystal.born_at.desc())
                .limit(limit)
            )

            if severity is not None:
                stmt = stmt.where(TeachingCrystal.severity == severity)

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_teaching_by_module(
        self,
        module_prefix: str,
        include_extinct: bool = False,
    ) -> list[TeachingCrystal]:
        """
        Get teaching crystals for a module and its children.

        AGENTESE: self.memory.teaching.by_module

        Args:
            module_prefix: Module path prefix (e.g., "services.brain")
            include_extinct: Include teaching from deleted code

        Returns:
            List of TeachingCrystal for the module
        """
        async with self.table.session_factory() as session:
            stmt = select(TeachingCrystal).where(
                TeachingCrystal.source_module.startswith(module_prefix)
            )

            if not include_extinct:
                stmt = stmt.where(TeachingCrystal.died_at.is_(None))

            stmt = stmt.order_by(TeachingCrystal.severity.desc(), TeachingCrystal.born_at.desc())

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_ancestral_wisdom(
        self,
        module_prefix: str | None = None,
        limit: int = 50,
    ) -> list[TeachingCrystal]:
        """
        Get wisdom from extinct (deleted) code.

        AGENTESE: void.extinct.wisdom

        The Ghost Hydration Law: Hydration MUST surface wisdom
        from extinct code when relevant.

        Args:
            module_prefix: Filter by original module (optional)
            limit: Maximum results

        Returns:
            List of TeachingCrystal from deleted code
        """
        async with self.table.session_factory() as session:
            stmt = (
                select(TeachingCrystal)
                .where(TeachingCrystal.died_at.isnot(None))
                .order_by(TeachingCrystal.died_at.desc())
                .limit(limit)
            )

            if module_prefix is not None:
                stmt = stmt.where(TeachingCrystal.source_module.startswith(module_prefix))

            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def count_teaching_crystals(self) -> dict[str, int]:
        """
        Count teaching crystals by status.

        Returns:
            Dict with counts: alive, extinct, total, by severity
        """
        async with self.table.session_factory() as session:
            # Total count
            total_result = await session.execute(
                select(func.count()).select_from(TeachingCrystal)
            )
            total = total_result.scalar() or 0

            # Alive count
            alive_result = await session.execute(
                select(func.count())
                .select_from(TeachingCrystal)
                .where(TeachingCrystal.died_at.is_(None))
            )
            alive = alive_result.scalar() or 0

            # By severity (alive only)
            critical_result = await session.execute(
                select(func.count())
                .select_from(TeachingCrystal)
                .where(TeachingCrystal.died_at.is_(None))
                .where(TeachingCrystal.severity == "critical")
            )
            critical = critical_result.scalar() or 0

            warning_result = await session.execute(
                select(func.count())
                .select_from(TeachingCrystal)
                .where(TeachingCrystal.died_at.is_(None))
                .where(TeachingCrystal.severity == "warning")
            )
            warning = warning_result.scalar() or 0

            return {
                "total": total,
                "alive": alive,
                "extinct": total - alive,
                "critical": critical,
                "warning": warning,
                "info": alive - critical - warning,
            }


__all__ = [
    "BrainPersistence",
    "CaptureResult",
    "SearchResult",
    "BrainStatus",
    "CrystallizeResult",
]
