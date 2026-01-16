"""
Brain Persistence: Universe-backed Storage for Brain Crown Jewel.

Owns domain semantics for Brain storage:
- WHEN to persist (on capture, on access for usage tracking)
- WHY to persist (Crystal system for typed, versioned data)
- HOW to compose (Universe handles backend selection and schema)

AGENTESE aspects exposed:
- capture: Store content with semantic embedding
- search: Semantic search for similar memories
- surface: Serendipity from the void
- manifest: Show brain status

Migration from SQLAlchemy to Universe/Crystal:
- All data now stored as Crystals via Universe
- Backend auto-selection: Postgres > SQLite > Memory
- Schema versioning via frozen dataclasses
- Graceful degradation when backends unavailable

Differance Integration (Phase 6B):
- capture() → trace with alternatives (auto_tag, defer_embedding)
- surface() → trace with alternatives (different_seed, context_weighted)
- delete() → trace with alternatives (archive_instead, soft_delete)
- search/get/list → NO traces (read-only, high frequency)

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/unified-data-crystal.md

Teaching:
    gotcha: Universe provides basic filtering (prefix, timestamp, schema).
            Complex queries (tag filtering, sorting) done in-memory.
            (Evidence: test_brain_persistence.py::test_tag_filtering)

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
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

# Legacy imports for teaching/extinction methods (not yet migrated)
from sqlalchemy import func, select

from agents.d.crystal import Crystal as CrystalWrapper
from agents.d.schemas.brain import BRAIN_CRYSTAL_SCHEMA, BrainCrystal
from agents.d.universe import Query, Universe, get_universe
from agents.differance.alternatives import get_alternatives
from agents.differance.integration import DifferanceIntegration
from models.brain import ExtinctionEvent, ExtinctionTeaching, TeachingCrystal

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


@dataclass
class ExtinctionResult:
    """Result of an extinction event (mass code deletion)."""

    event_id: str
    reason: str
    affected_count: int  # Teaching crystals in deleted modules
    preserved_count: int  # Teaching crystals marked as extinct


@dataclass
class GhostWisdom:
    """Ancestral wisdom from deleted code, with extinction context."""

    teaching: TeachingCrystal
    extinction_event: ExtinctionEvent | None
    successor: str | None  # What replaced the deleted module


class BrainPersistence:
    """
    Persistence layer for Brain Crown Jewel.

    Uses Universe for typed, versioned data storage:
    - BrainCrystal: Memory crystals with metadata and content
    - Backend auto-selection: Postgres > SQLite > Memory
    - Schema versioning handles evolution

    Domain Semantics:
    - Crystals are the atomic units of memory
    - Each crystal is stored as typed BrainCrystal dataclass
    - Usage tracking enables relevance scoring
    - All queries use Universe with in-memory filtering for complex operations

    Example:
        persistence = BrainPersistence()

        result = await persistence.capture("Python is great for data science")
        results = await persistence.search("programming language", limit=5)
    """

    def __init__(
        self,
        universe: Universe | None = None,
        embedder: Any | None = None,  # L-gent for embeddings
        # Legacy parameters for teaching/extinction (not yet migrated)
        table_adapter: Any | None = None,  # TableAdapter[Crystal] - kept for teaching methods
    ) -> None:
        """
        Initialize BrainPersistence.

        Args:
            universe: Optional Universe instance (uses singleton if None)
            embedder: Optional embedder for semantic search
            table_adapter: (Legacy) TableAdapter for teaching/extinction methods

        Migration Status:
            - Core crystal methods: MIGRATED to Universe ✓
            - Teaching methods: Still use SQLAlchemy (TODO)
            - Extinction methods: Still use SQLAlchemy (TODO)
        """
        self.universe = universe or get_universe()
        self.embedder = embedder
        self._ghosts_healed = 0

        # Legacy: Keep table adapter for teaching/extinction methods
        # TODO: Remove once those are migrated to Universe
        self.table = table_adapter
        if table_adapter:
            self.session_factory = table_adapter.session_factory
        else:
            self.session_factory = None

        # Differance integration for trace recording (Phase 6B)
        self._differance = DifferanceIntegration("brain")

        # Register schema on first init
        self._register_schemas()

    def _register_schemas(self) -> None:
        """Register Brain schemas with Universe."""
        self.universe.register_schema(BRAIN_CRYSTAL_SCHEMA)

    async def _storage_backend(self) -> str:
        """Detect storage backend from Universe stats."""
        stats = await self.universe.stats()
        return stats.backend

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

        Storage via Universe/Crystal:
        - Content stored as BrainCrystal dataclass
        - Schema versioning handles evolution
        - Backend auto-selected (Postgres > SQLite > Memory)

        Args:
            content: The content to capture
            tags: Optional tags for categorization
            source_type: Source type ("capture", "import", "generation")
            source_ref: Source reference (e.g., file path)
            metadata: Additional metadata (currently unused, reserved for future)

        Returns:
            CaptureResult with crystal_id and storage details
        """
        tags = tags or []
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        crystal_id = f"crystal-{uuid.uuid4().hex[:12]}"

        # Create summary (first 200 chars for now, could use LLM later)
        summary = content[:200].strip()
        if len(content) > 200:
            summary += "..."

        # Create BrainCrystal dataclass
        brain_crystal = BrainCrystal(
            summary=summary,
            content=content,
            content_hash=content_hash,
            tags=tuple(tags),  # Frozen dataclass requires tuple
            source_type=source_type,
            source_ref=source_ref,
            access_count=0,
            last_accessed=None,
            datum_id=None,  # Will be set by Universe
        )

        # Store BrainCrystal via Universe with explicit schema name
        datum_id = await self.universe.store(brain_crystal, schema_name="brain.crystal")

        # Check if we have embeddings
        has_embedding = self.embedder is not None

        result = CaptureResult(
            crystal_id=datum_id,  # Universe returns datum ID
            content=content,
            summary=summary,
            captured_at=datetime.now(UTC).isoformat(),
            has_embedding=has_embedding,
            storage=await self._storage_backend(),
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
                    output=datum_id,
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

        Uses keyword-based search with in-memory filtering.
        Future: Use L-gent for true semantic search.

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

        # Strategy 2: Fall back to keyword matching across all crystals
        # Query all brain crystals from Universe
        q = Query(schema="brain.crystal", limit=1000)  # Get more for filtering
        all_crystals = await self.universe.query(q)

        # Filter by tags if specified
        if tags:
            all_crystals = [
                c
                for c in all_crystals
                if isinstance(c, BrainCrystal) and any(tag in c.tags for tag in tags)
            ]

        # Keyword matching
        query_lower = query.lower()
        query_words = query_lower.split()

        for crystal_obj in all_crystals:
            if not isinstance(crystal_obj, BrainCrystal):
                continue

            # Calculate basic similarity (keyword-based)
            content = crystal_obj.content
            content_lower = content.lower()

            if not query:  # Include all if no query
                similarity = 1.0
            else:
                matches = sum(1 for word in query_words if word in content_lower)
                similarity = matches / len(query_words) if query_words else 0.0

            if similarity > 0 or not query:
                results.append(
                    SearchResult(
                        crystal_id=crystal_obj.content_hash,  # Using hash as ID for now
                        content=content,
                        summary=crystal_obj.summary,
                        similarity=similarity,
                        captured_at=datetime.now(UTC).isoformat(),  # TODO: Get from datum
                        is_stale=False,
                    )
                )

                # TODO: Update access_count - needs mutable access pattern
                # Current BrainCrystal is frozen, so can't update directly
                # Will need separate tracking mechanism

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
        # Get all brain crystals
        q = Query(schema="brain.crystal", limit=1000)
        all_crystals = await self.universe.query(q)

        if not all_crystals:
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

        crystal_obj = random.choice(all_crystals)

        if not isinstance(crystal_obj, BrainCrystal):
            return None

        result_obj = SearchResult(
            crystal_id=crystal_obj.content_hash,
            content=crystal_obj.content,
            summary=crystal_obj.summary,
            similarity=1.0 - entropy,  # Surprise factor
            captured_at=datetime.now(UTC).isoformat(),  # TODO: Get from datum
            is_stale=False,
        )

        # Fire-and-forget trace recording (Phase 6B)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                self._differance.record(
                    operation="surface",
                    inputs=(context[:50] if context else "random",),
                    output=crystal_obj.content_hash,
                    context=f"Surfaced with entropy={entropy:.2f}",
                    alternatives=get_alternatives("brain", "surface"),
                )
            )
        except RuntimeError:
            logger.debug("No event loop for surface trace recording")

        return result_obj

    async def manifest(self) -> BrainStatus:
        """
        Get brain health status.

        AGENTESE: self.memory.manifest

        Returns:
            BrainStatus with crystal counts and health metrics
        """
        # Get stats from Universe
        stats = await self.universe.stats()

        # Query all brain crystals to count
        q = Query(schema="brain.crystal", limit=10000)  # High limit for counting
        all_crystals = await self.universe.query(q)
        total_crystals = len(all_crystals)

        # All crystals in Universe have datum_id by design
        coherency_rate = 1.0

        return BrainStatus(
            total_crystals=total_crystals,
            vector_count=0,  # TODO: Count actual vectors when L-gent is wired
            has_semantic=self.embedder is not None,
            coherency_rate=coherency_rate,
            ghosts_healed=self._ghosts_healed,
            storage_path="~/.local/share/kgents/membrane",  # Universe uses XDG paths
            storage_backend=stats.backend,
        )

    # =========================================================================
    # Additional Domain Methods
    # =========================================================================

    async def get_by_id(self, crystal_id: str) -> SearchResult | None:
        """Get a specific crystal by ID."""
        # Get crystal from Universe
        crystal_obj = await self.universe.get(crystal_id)

        if crystal_obj is None or not isinstance(crystal_obj, BrainCrystal):
            return None

        return SearchResult(
            crystal_id=crystal_obj.content_hash,
            content=crystal_obj.content,
            summary=crystal_obj.summary,
            similarity=1.0,
            captured_at=datetime.now(UTC).isoformat(),  # TODO: Get from datum
            is_stale=False,
        )

    async def list_recent(self, limit: int = 10) -> list[SearchResult]:
        """List recent crystals."""
        # Query all brain crystals
        q = Query(schema="brain.crystal", limit=limit * 2)  # Get more for sorting
        all_crystals = await self.universe.query(q)

        # Filter to BrainCrystal type
        brain_crystals = [c for c in all_crystals if isinstance(c, BrainCrystal)]

        # TODO: Sort by created_at when datum metadata is accessible
        # For now, return in query order (most recent first from Universe)
        results = []
        for crystal_obj in brain_crystals[:limit]:
            results.append(
                SearchResult(
                    crystal_id=crystal_obj.content_hash,
                    content=crystal_obj.content,
                    summary=crystal_obj.summary,
                    similarity=1.0,
                    captured_at=datetime.now(UTC).isoformat(),  # TODO: Get from datum
                    is_stale=False,
                )
            )

        return results

    async def list_by_tag(self, tag: str, limit: int = 10) -> list[SearchResult]:
        """List crystals with a specific tag."""
        # Query all brain crystals and filter by tag in-memory
        q = Query(schema="brain.crystal", limit=1000)  # Get more for filtering
        all_crystals = await self.universe.query(q)

        # Filter to crystals with the specified tag
        tagged_crystals = [c for c in all_crystals if isinstance(c, BrainCrystal) and tag in c.tags]

        results = []
        for crystal_obj in tagged_crystals[:limit]:
            results.append(
                SearchResult(
                    crystal_id=crystal_obj.content_hash,
                    content=crystal_obj.content,
                    summary=crystal_obj.summary,
                    similarity=1.0,
                    captured_at=datetime.now(UTC).isoformat(),  # TODO: Get from datum
                    is_stale=False,
                )
            )

        return results

    async def delete(self, crystal_id: str) -> bool:
        """Delete a crystal from Universe."""
        # Get crystal first to capture summary for trace
        crystal_obj = await self.universe.get(crystal_id)

        if crystal_obj is None:
            return False

        deleted_summary = "unknown"
        if isinstance(crystal_obj, BrainCrystal):
            deleted_summary = crystal_obj.summary[:50]

        # Delete from Universe
        success = await self.universe.delete(crystal_id)

        if success:
            # Fire-and-forget trace recording (Phase 6B)
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

        return success

    async def heal_ghosts(self) -> int:
        """
        Heal ghost memories (crystals without D-gent datums).

        NOTE: With Universe, ghosts shouldn't exist - all crystals are
        stored as complete datum+schema pairs. This method exists for
        backward compatibility but should always return 0.

        Returns count of healed ghosts (always 0 with Universe).
        """
        # Universe doesn't have ghosts - data is always complete
        return 0

    # =========================================================================
    # Teaching Crystal Crystallization (Memory-First Docs)
    # =========================================================================
    #
    # NOTE: Teaching and Extinction methods below still use SQLAlchemy.
    # These haven't been migrated to Universe/Crystal yet because:
    # 1. They use separate table models (TeachingCrystal, ExtinctionEvent)
    # 2. They need complex queries (ancestry, tree traversal, keyword search)
    # 3. Migration would require new schemas and query patterns
    #
    # TODO: Create separate schemas (brain.teaching, brain.extinction) and migrate
    # See: https://github.com/kent/kgents/issues/XXX
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
            total_result = await session.execute(select(func.count()).select_from(TeachingCrystal))
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

    # =========================================================================
    # Extinction Protocol (Memory-First Docs Phase 3)
    # =========================================================================

    async def prepare_extinction(
        self,
        reason: str,
        commit: str,
        deleted_paths: list[str],
        decision_doc: str | None = None,
        successor_map: dict[str, str | None] | None = None,
    ) -> ExtinctionResult:
        """
        Prepare wisdom preservation before mass deletion.

        AGENTESE: self.memory.extinction.prepare

        The Extinction Law: Before deleting code, crystallize
        its teaching and mark as extinct.

        Args:
            reason: Why the deletion happened (e.g., "Crown Jewel Cleanup - AD-009")
            commit: Git SHA of the deletion commit
            deleted_paths: Paths being deleted (e.g., ["services/town/", "services/park/"])
            decision_doc: Reference to decision doc (optional)
            successor_map: Mapping of old → new paths (optional)

        Returns:
            ExtinctionResult with event_id, affected_count, preserved_count

        Teaching:
            gotcha: deleted_paths uses filesystem paths but source_module uses dots.
                    Convert "services/town/" → "services.town" for matching.
                    (Evidence: test_extinction.py::test_path_conversion)
        """
        async with self.table.session_factory() as session:
            # Create ExtinctionEvent
            event_id = f"ext-{commit[:8]}-{int(datetime.now(UTC).timestamp())}"
            event = ExtinctionEvent(
                id=event_id,
                reason=reason,
                decision_doc=decision_doc,
                commit=commit,
                deleted_paths=deleted_paths,
                successor_map=successor_map or {},
            )
            session.add(event)

            # Convert paths to module prefixes
            # "services/town/" → "services.town"
            module_prefixes = [p.rstrip("/").replace("/", ".") for p in deleted_paths]

            # Find affected teaching crystals
            affected_crystals: list[TeachingCrystal] = []
            for prefix in module_prefixes:
                stmt = (
                    select(TeachingCrystal)
                    .where(TeachingCrystal.source_module.startswith(prefix))
                    .where(TeachingCrystal.died_at.is_(None))
                )
                result = await session.execute(stmt)
                affected_crystals.extend(result.scalars().all())

            # Mark as extinct and link to event
            preserved_count = 0
            for crystal in affected_crystals:
                crystal.died_at = datetime.now(UTC)

                # Set successor if provided
                if successor_map:
                    for old_path, new_path in successor_map.items():
                        old_module = old_path.rstrip("/").replace("/", ".")
                        if crystal.source_module.startswith(old_module):
                            crystal.successor_module = new_path
                            break

                # Create join record
                link = ExtinctionTeaching(
                    extinction_id=event_id,
                    teaching_id=crystal.id,
                )
                session.add(link)
                preserved_count += 1

            # Update event with preserved count
            event.preserved_count = preserved_count

            await session.commit()

            return ExtinctionResult(
                event_id=event_id,
                reason=reason,
                affected_count=len(affected_crystals),
                preserved_count=preserved_count,
            )

    async def get_extinction_events(self, limit: int = 50) -> list[ExtinctionEvent]:
        """
        List all extinction events.

        AGENTESE: void.extinct.list

        Returns:
            List of ExtinctionEvent ordered by date
        """
        async with self.table.session_factory() as session:
            stmt = select(ExtinctionEvent).order_by(ExtinctionEvent.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_extinction_event(self, event_id: str) -> ExtinctionEvent | None:
        """
        Get a specific extinction event by ID.

        AGENTESE: void.extinct.show

        Args:
            event_id: The extinction event ID

        Returns:
            ExtinctionEvent or None if not found
        """
        async with self.table.session_factory() as session:
            return await session.get(ExtinctionEvent, event_id)

    async def get_extinct_wisdom(
        self,
        keywords: list[str] | None = None,
        module_prefix: str | None = None,
        limit: int = 50,
    ) -> list[GhostWisdom]:
        """
        Get wisdom from deleted code (ancestral teaching).

        AGENTESE: void.extinct.wisdom

        Args:
            keywords: Search for keywords in insights
            module_prefix: Filter by former module location
            limit: Maximum results

        Returns:
            List of GhostWisdom with teaching + extinction context

        Teaching:
            gotcha: GhostWisdom includes extinction context (event, successor).
                    Use get_ancestral_wisdom() for raw TeachingCrystal list.
                    (Evidence: test_extinction.py::test_ghost_wisdom_context)
        """
        async with self.table.session_factory() as session:
            # Get extinct teaching crystals with their extinction events
            stmt = (
                select(TeachingCrystal, ExtinctionEvent)
                .outerjoin(
                    ExtinctionTeaching,
                    TeachingCrystal.id == ExtinctionTeaching.teaching_id,
                )
                .outerjoin(
                    ExtinctionEvent,
                    ExtinctionTeaching.extinction_id == ExtinctionEvent.id,
                )
                .where(TeachingCrystal.died_at.isnot(None))
                .order_by(TeachingCrystal.died_at.desc())
                .limit(limit * 2)  # Over-fetch for filtering
            )

            if module_prefix:
                stmt = stmt.where(TeachingCrystal.source_module.startswith(module_prefix))

            result = await session.execute(stmt)

            ghosts: list[GhostWisdom] = []
            for teaching, event in result:
                # Keyword filtering (if specified)
                if keywords:
                    insight_lower = teaching.insight.lower()
                    if not any(kw.lower() in insight_lower for kw in keywords):
                        continue

                ghosts.append(
                    GhostWisdom(
                        teaching=teaching,
                        extinction_event=event,
                        successor=teaching.successor_module,
                    )
                )

                if len(ghosts) >= limit:
                    break

            return ghosts

    async def query_teaching_by_keywords(
        self,
        keywords: list[str],
        include_extinct: bool = False,
        limit: int = 15,
    ) -> list[TeachingCrystal]:
        """
        Query teaching crystals by keyword matching.

        AGENTESE: self.memory.teaching.query

        This is the primary query method for unified hydration.
        Replaces TeachingCollector.collect_all() + in-memory filtering.

        Args:
            keywords: Keywords to search for in insight, module, symbol
            include_extinct: Include teaching from deleted code
            limit: Maximum results

        Returns:
            List of TeachingCrystal sorted by relevance

        Teaching:
            gotcha: Keywords are matched against insight text, module, AND symbol.
                    Module/symbol matches score higher than insight matches.
                    (Evidence: test_query_teaching.py::test_keyword_scoring)
        """
        if not keywords:
            return []

        async with self.table.session_factory() as session:
            # Get all candidate teaching crystals
            stmt = select(TeachingCrystal)

            if not include_extinct:
                stmt = stmt.where(TeachingCrystal.died_at.is_(None))

            stmt = stmt.limit(500)  # Cap for performance

            result = await session.execute(stmt)
            crystals = result.scalars().all()

            # Score and rank by keyword matches
            scored: list[tuple[int, TeachingCrystal]] = []
            for crystal in crystals:
                score = 0
                insight_lower = crystal.insight.lower()
                module_lower = crystal.source_module.lower()
                symbol_lower = crystal.source_symbol.lower()

                for kw in keywords:
                    kw_lower = kw.lower()
                    # Module match is high signal
                    if kw_lower in module_lower:
                        score += 3
                    # Symbol match is medium signal
                    if kw_lower in symbol_lower:
                        score += 2
                    # Insight match is low signal
                    if kw_lower in insight_lower:
                        score += 1

                if score > 0:
                    scored.append((score, crystal))

            # Sort by score descending, take top N
            scored.sort(key=lambda x: x[0], reverse=True)
            return [crystal for _, crystal in scored[:limit]]


__all__ = [
    "BrainPersistence",
    "CaptureResult",
    "SearchResult",
    "BrainStatus",
    "CrystallizeResult",
    "ExtinctionResult",
    "GhostWisdom",
]
