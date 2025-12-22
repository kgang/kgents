"""
Trail Storage Adapter: D-gent integration for trail persistence.

Implements durable storage for trails with:
- Postgres persistence via D-gent
- Semantic search via embeddings
- Version conflict detection
- Fork/merge lineage tracking

AGENTESE: self.trail.*

Teaching:
    gotcha: All writes are transactional—trails persist atomically.
            If step save fails, trail is not updated.

    gotcha: Version conflicts are detected via optimistic locking.
            Load trail before update to get current version.

See: docs/skills/metaphysical-fullstack.md
See: services/witness/persistence.py (reference implementation)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Awaitable, Callable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol
from models.trail import (
    TrailAnnotationRow,
    TrailCommitmentRow,
    TrailEvidenceRow,
    TrailForkRow,
    TrailRow,
    TrailStepRow,
    generate_step_id,
    generate_trail_id,
)

if TYPE_CHECKING:
    from protocols.exploration.types import (
        Claim,
        Evidence as ExplorationEvidence,
        Observer,
        Trail as ExplorationTrail,
        TrailStep as ExplorationTrailStep,
    )

logger = logging.getLogger(__name__)


# =============================================================================
# Result Dataclasses
# =============================================================================


@dataclass
class TrailSaveResult:
    """Result of a trail save operation."""

    trail_id: str
    name: str
    step_count: int
    version: int
    timestamp: datetime
    datum_id: str | None = None


@dataclass
class TrailLoadResult:
    """Result of a trail load operation."""

    trail_id: str
    name: str
    steps: list[dict[str, Any]]
    annotations: dict[int, str]
    version: int
    created_at: datetime
    updated_at: datetime
    forked_from_id: str | None = None
    topics: list[str] = field(default_factory=list)


@dataclass
class TrailSearchResult:
    """Result of a semantic search operation."""

    trail_id: str
    name: str
    score: float
    step_count: int
    topics: list[str]


@dataclass
class VersionConflict:
    """Raised when trail version conflicts on update."""

    trail_id: str
    expected_version: int
    actual_version: int
    message: str = ""


@dataclass
class TrailStatus:
    """Trail storage health status."""

    total_trails: int
    total_steps: int
    active_trails: int
    forked_trails: int
    storage_backend: str


# =============================================================================
# Trail Storage Adapter
# =============================================================================


class TrailStorageAdapter:
    """
    D-gent adapter for trail persistence.

    Composes:
    - SQLAlchemy models for structured queries
    - D-gent for semantic content and causal chains

    Domain Semantics:
    - Trails are first-class knowledge artifacts
    - Steps are immutable once persisted (append-only)
    - Forks create independent lineages
    - Version conflicts are detected on update

    Example:
        storage = TrailStorageAdapter(
            session_factory=session_factory,
            dgent=dgent_router,
        )

        result = await storage.save_trail(exploration_trail)
        loaded = await storage.load_trail(trail_id)
        similar = await storage.search_semantic(query_embedding)
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        dgent: DgentProtocol | None = None,
    ) -> None:
        self.session_factory = session_factory
        self.dgent = dgent

    # =========================================================================
    # Save Operations
    # =========================================================================

    async def save_trail(
        self,
        trail: "ExplorationTrail",
        observer: "Observer | None" = None,
    ) -> TrailSaveResult:
        """
        Save an exploration trail to Postgres.

        AGENTESE: self.trail.save

        Persists:
        1. Trail metadata (name, observer, topics)
        2. All steps (immutable, append-only)
        3. Annotations (mutable)
        4. Semantic content in D-gent

        Args:
            trail: The exploration Trail from types.py
            observer: Optional observer context

        Returns:
            TrailSaveResult with trail_id and storage details
        """
        # Use provided ID, or generate one if not provided
        # Note: exploration Trail has default uuid, check if it's really user-provided
        trail_id = trail.id if trail.id and trail.id.startswith("trail-") else generate_trail_id()
        now = datetime.now(UTC)

        # Compute content hash for integrity
        content_hash = self._compute_content_hash(trail)

        # Extract topics from steps (simple keyword extraction)
        topics = self._extract_topics(trail)

        async with self.session_factory() as session:
            # Check if trail exists (update vs insert)
            existing = await session.get(TrailRow, trail_id)

            if existing:
                # Update existing trail
                existing.name = trail.name or existing.name
                existing.topics = topics
                existing.content_hash = content_hash
                existing.bump_version()

                # Add new steps (append-only)
                existing_step_count = await self._get_step_count(session, trail_id)
                for i, step in enumerate(
                    trail.steps[existing_step_count:], start=existing_step_count
                ):
                    await self._save_step(session, trail_id, i, step, observer)

                await session.commit()
                await session.refresh(existing)

                # Get updated step count
                new_step_count = await self._get_step_count(session, trail_id)

                return TrailSaveResult(
                    trail_id=trail_id,
                    name=existing.name,
                    step_count=new_step_count,
                    version=existing.version,
                    timestamp=now,
                )
            else:
                # Create new trail
                trail_row = TrailRow(
                    id=trail_id,
                    name=trail.name or "",
                    created_by_id=observer.id if observer else None,
                    created_by_archetype=observer.archetype if observer else "developer",
                    topics=topics,
                    content_hash=content_hash,
                )
                session.add(trail_row)

                # Save all steps
                for i, step in enumerate(trail.steps):
                    await self._save_step(session, trail_id, i, step, observer)

                # Save annotations
                for step_index, annotation_text in trail.annotations.items():
                    annotation = TrailAnnotationRow(
                        trail_id=trail_id,
                        step_index=step_index,
                        author_id=observer.id if observer else None,
                        content=annotation_text,
                    )
                    session.add(annotation)

                await session.commit()

        # Store semantic content in D-gent if available
        datum_id = None
        if self.dgent:
            datum_id = await self._store_semantic_content(trail_id, trail)

        return TrailSaveResult(
            trail_id=trail_id,
            name=trail.name or "",
            step_count=len(trail.steps),
            version=1,
            timestamp=now,
            datum_id=datum_id,
        )

    async def _save_step(
        self,
        session: AsyncSession,
        trail_id: str,
        index: int,
        step: "ExplorationTrailStep",
        observer: "Observer | None",
        embedding: list[float] | None = None,
    ) -> None:
        """
        Save a single step (internal helper).

        Args:
            session: SQLAlchemy async session
            trail_id: Parent trail ID
            index: Step index in trail
            step: ExplorationTrailStep from types.py
            observer: Optional observer context
            embedding: Optional embedding vector (1536 dimensions for OpenAI)

        Teaching:
            gotcha: Embedding is stored in both embedding_json (TEXT, legacy)
                    and embedding (VECTOR, native pgvector) columns.
                    The native column enables fast <=> similarity search.
        """
        step_row = TrailStepRow(
            id=generate_step_id(),
            trail_id=trail_id,
            index=index,
            explorer_id=observer.id if observer else None,
            explorer_archetype=observer.archetype if observer else "developer",
            source_path=step.node,
            edge=step.edge_taken,
            destination_paths=[step.node],  # Destinations are the node itself
            reasoning=step.annotation,
            loop_status="OK",
        )

        # Store embedding if provided
        if embedding is not None:
            # Legacy: JSON-serialized for fallback search
            step_row.embedding_json = json.dumps(embedding)

            # Native: pgvector VECTOR column (if available)
            # The model handles fallback to TEXT if pgvector not installed
            try:
                step_row.embedding = embedding
            except Exception:
                # pgvector not available, embedding_json is sufficient
                pass

        session.add(step_row)

    async def _get_step_count(self, session: AsyncSession, trail_id: str) -> int:
        """Get current step count for a trail."""
        result = await session.execute(
            select(func.count()).select_from(TrailStepRow).where(TrailStepRow.trail_id == trail_id)
        )
        return result.scalar() or 0

    async def create_trail(
        self,
        name: str,
        steps: list[dict[str, Any]],
        topics: list[str] | None = None,
        observer: "Observer | None" = None,
    ) -> TrailSaveResult:
        """
        Create a new trail from raw dict data (for UI).

        AGENTESE: self.trail.create

        This is a simplified interface for the Trail Builder UI that accepts
        raw step dicts instead of ExplorationTrail objects.

        Args:
            name: Trail name
            steps: List of step dicts with {source_path, edge, reasoning, ...}
            topics: Optional topic tags
            observer: Who is creating the trail

        Returns:
            TrailSaveResult with trail_id and metadata
        """
        trail_id = generate_trail_id()
        now = datetime.now(UTC)

        # Compute content hash
        content_hash = hashlib.sha256(
            json.dumps({"name": name, "steps": steps}, sort_keys=True).encode()
        ).hexdigest()[:32]

        async with self.session_factory() as session:
            # Create trail row
            trail_row = TrailRow(
                id=trail_id,
                name=name,
                created_by_id=observer.id if observer else None,
                created_by_archetype=observer.archetype if observer else "developer",
                topics=topics or [],
                content_hash=content_hash,
            )
            session.add(trail_row)

            # Save steps
            for i, step in enumerate(steps):
                step_row = TrailStepRow(
                    id=generate_step_id(),
                    trail_id=trail_id,
                    index=i,
                    parent_index=step.get("parent_index"),  # For branching trails
                    explorer_id=observer.id if observer else None,
                    explorer_archetype=observer.archetype if observer else "developer",
                    source_path=step.get("source_path", ""),
                    edge=step.get("edge"),
                    destination_paths=step.get("destination_paths", [step.get("source_path", "")]),
                    reasoning=step.get("reasoning", ""),
                    loop_status=step.get("loop_status", "OK"),
                )
                session.add(step_row)

            await session.commit()

        return TrailSaveResult(
            trail_id=trail_id,
            name=name,
            step_count=len(steps),
            version=1,
            timestamp=now,
        )

    # =========================================================================
    # Load Operations
    # =========================================================================

    async def load_trail(self, trail_id: str) -> TrailLoadResult | None:
        """
        Load a trail from Postgres.

        AGENTESE: self.trail.manifest

        Args:
            trail_id: The trail ID to load

        Returns:
            TrailLoadResult with all trail data, or None if not found
        """
        async with self.session_factory() as session:
            trail = await session.get(TrailRow, trail_id)
            if trail is None:
                return None

            # Load steps
            steps_result = await session.execute(
                select(TrailStepRow)
                .where(TrailStepRow.trail_id == trail_id)
                .order_by(TrailStepRow.index)
            )
            steps = steps_result.scalars().all()

            # Load annotations
            annotations_result = await session.execute(
                select(TrailAnnotationRow).where(TrailAnnotationRow.trail_id == trail_id)
            )
            annotations = annotations_result.scalars().all()
            annotations_dict = {ann.step_index: ann.content for ann in annotations}

            return TrailLoadResult(
                trail_id=trail.id,
                name=trail.name,
                steps=[
                    {
                        "index": s.index,
                        "parent_index": s.parent_index,  # For branching trails
                        "source_path": s.source_path,
                        "edge": s.edge,
                        "destination_paths": s.destination_paths,
                        "reasoning": s.reasoning,
                        "loop_status": s.loop_status,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                    }
                    for s in steps
                ],
                annotations=annotations_dict,
                version=trail.version,
                created_at=trail.created_at,
                updated_at=trail.updated_at,
                forked_from_id=trail.forked_from_id,
                topics=trail.topics or [],
            )

    async def list_trails(
        self,
        limit: int = 50,
        created_by_id: str | None = None,
        active_only: bool = True,
    ) -> list[TrailLoadResult]:
        """
        List trails with optional filters.

        AGENTESE: self.trail.list

        Args:
            limit: Maximum trails to return (default 50)
            created_by_id: Filter by creator
            active_only: Only return active trails (default True)

        Returns:
            List of TrailLoadResult objects, newest first
        """
        async with self.session_factory() as session:
            stmt = select(TrailRow).order_by(TrailRow.created_at.desc())

            if created_by_id:
                stmt = stmt.where(TrailRow.created_by_id == created_by_id)
            if active_only:
                stmt = stmt.where(TrailRow.is_active == True)  # noqa: E712

            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            trails = result.scalars().all()

            results = []
            for trail in trails:
                loaded = await self.load_trail(trail.id)
                if loaded:
                    results.append(loaded)

            return results

    # =========================================================================
    # Fork/Merge Operations
    # =========================================================================

    async def fork_trail(
        self,
        trail_id: str,
        new_name: str,
        fork_point: int | None = None,
        observer: "Observer | None" = None,
    ) -> TrailSaveResult:
        """
        Fork a trail at a specific point.

        AGENTESE: self.trail.fork

        Creates an independent copy of the trail up to fork_point.
        Changes to the fork don't affect the parent.

        Args:
            trail_id: The trail to fork
            new_name: Name for the forked trail
            fork_point: Step index to fork at (default: current end)
            observer: Who is forking

        Returns:
            TrailSaveResult for the new forked trail
        """
        async with self.session_factory() as session:
            # Load parent trail
            parent = await session.get(TrailRow, trail_id)
            if parent is None:
                raise ValueError(f"Trail {trail_id} not found")

            # Get step count via direct query (avoid lazy loading)
            step_count_result = await session.execute(
                select(func.count())
                .select_from(TrailStepRow)
                .where(TrailStepRow.trail_id == trail_id)
            )
            current_step_count = step_count_result.scalar() or 0

            # Get steps up to fork point
            if fork_point is None:
                fork_point = current_step_count

            steps_result = await session.execute(
                select(TrailStepRow)
                .where(TrailStepRow.trail_id == trail_id)
                .where(TrailStepRow.index <= fork_point)
                .order_by(TrailStepRow.index)
            )
            steps = steps_result.scalars().all()

            # Create forked trail
            forked_trail = TrailRow(
                id=generate_trail_id(),
                name=new_name,
                created_by_id=observer.id if observer else None,
                created_by_archetype=observer.archetype if observer else "developer",
                forked_from_id=trail_id,
                fork_point=fork_point,
                topics=parent.topics,
            )
            session.add(forked_trail)

            # Copy steps
            for i, step in enumerate(steps):
                new_step = TrailStepRow(
                    id=generate_step_id(),
                    trail_id=forked_trail.id,
                    index=i,
                    explorer_id=step.explorer_id,
                    explorer_archetype=step.explorer_archetype,
                    source_path=step.source_path,
                    edge=step.edge,
                    destination_paths=step.destination_paths,
                    reasoning=step.reasoning,
                    loop_status=step.loop_status,
                )
                session.add(new_step)

            # Record fork relationship
            fork_record = TrailForkRow(
                parent_trail_id=trail_id,
                child_trail_id=forked_trail.id,
                fork_point=fork_point,
                forked_by_id=observer.id if observer else None,
            )
            session.add(fork_record)

            await session.commit()

            return TrailSaveResult(
                trail_id=forked_trail.id,
                name=new_name,
                step_count=len(steps),
                version=1,
                timestamp=datetime.now(UTC),
            )

    # =========================================================================
    # Semantic Search
    # =========================================================================

    async def search_semantic(
        self,
        query_embedding: list[float],
        limit: int = 10,
    ) -> list[TrailSearchResult]:
        """
        Search trails by semantic similarity.

        AGENTESE: self.trail.search

        Uses native pgvector <=> (cosine distance) operator.
        pgvector is required for semantic search.

        Args:
            query_embedding: Query embedding vector (1536 dimensions for OpenAI)
            limit: Maximum results (default 10)

        Returns:
            List of TrailSearchResult ordered by similarity (highest first)
        """
        return await self._search_semantic_pgvector(query_embedding, limit)

    async def _search_semantic_pgvector(
        self,
        query_embedding: list[float],
        limit: int,
    ) -> list[TrailSearchResult]:
        """
        Search using native pgvector <=> operator.

        Uses IVFFlat index for O(log n) approximate nearest neighbor search.

        Teaching:
            gotcha: pgvector <=> returns DISTANCE (lower = more similar).
                    We convert to similarity: similarity = 1 - distance.
        """
        from sqlalchemy import text

        async with self.session_factory() as session:
            # Check if we're on Postgres (pgvector only works there)
            dialect = session.get_bind().dialect.name
            if dialect != "postgresql":
                raise RuntimeError("pgvector requires PostgreSQL")

            # Native pgvector query using cosine distance operator
            # Returns distinct trails ordered by best matching step
            result = await session.execute(
                text("""
                    SELECT DISTINCT ON (t.id)
                        t.id as trail_id,
                        t.name,
                        t.topics,
                        (SELECT COUNT(*) FROM trail_steps WHERE trail_id = t.id) as step_count,
                        s.embedding <=> :query AS distance
                    FROM trails t
                    JOIN trail_steps s ON t.id = s.trail_id
                    WHERE s.embedding IS NOT NULL
                    AND t.is_active = TRUE
                    ORDER BY t.id, s.embedding <=> :query
                    LIMIT :limit
                """),
                {"query": str(query_embedding), "limit": limit * 2},  # Get more for dedup
            )
            rows = result.fetchall()

        # Convert to TrailSearchResult with similarity scores
        # Sort by distance (ascending = most similar first)
        sorted_rows = sorted(rows, key=lambda r: r.distance)

        search_results: list[TrailSearchResult] = []
        for row in sorted_rows[:limit]:
            # Convert distance to similarity (cosine distance → cosine similarity)
            similarity = max(0.0, 1.0 - row.distance)

            # Parse topics from JSON if needed
            topics = row.topics if isinstance(row.topics, list) else []

            search_results.append(
                TrailSearchResult(
                    trail_id=row.trail_id,
                    name=row.name or "",
                    score=similarity,
                    step_count=row.step_count,
                    topics=topics,
                )
            )

        return search_results

    async def update_step_embedding(
        self,
        step_id: str,
        embedding: list[float],
    ) -> bool:
        """
        Update embedding for an existing step.

        Useful for backfilling embeddings after pgvector migration.

        Args:
            step_id: The step ID to update
            embedding: Embedding vector (1536 dimensions for OpenAI)

        Returns:
            True if step was updated, False if not found

        AGENTESE: self.trail.step.embed
        """
        async with self.session_factory() as session:
            step = await session.get(TrailStepRow, step_id)
            if step is None:
                return False

            # Update both columns
            step.embedding_json = json.dumps(embedding)
            try:
                step.embedding = embedding
            except Exception:
                pass  # pgvector not available

            await session.commit()
            return True

    async def backfill_embeddings(
        self,
        embedder_fn: "Callable[[str], Awaitable[list[float]]]",
        limit: int = 100,
    ) -> int:
        """
        Backfill embeddings for steps that don't have them.

        Args:
            embedder_fn: Async function that takes text and returns embedding
            limit: Maximum steps to process

        Returns:
            Number of steps updated

        Example:
            async def embed(text: str) -> list[float]:
                return await openai.embeddings.create(input=text, model="text-embedding-3-small")

            updated = await storage.backfill_embeddings(embed, limit=1000)
        """
        updated = 0

        async with self.session_factory() as session:
            # Find steps without embeddings
            result = await session.execute(
                select(TrailStepRow).where(TrailStepRow.embedding.is_(None)).limit(limit)
            )
            steps = result.scalars().all()

            for step in steps:
                # Generate text for embedding
                text_parts = [step.source_path]
                if step.edge:
                    text_parts.append(step.edge)
                if step.reasoning:
                    text_parts.append(step.reasoning)
                text = " ".join(text_parts)

                try:
                    embedding = await embedder_fn(text)
                    step.embedding_json = json.dumps(embedding)
                    try:
                        step.embedding = embedding
                    except Exception:
                        pass
                    updated += 1
                except Exception as e:
                    logger.warning(f"Failed to embed step {step.id}: {e}")

            await session.commit()

        return updated

    async def search_by_topics(
        self,
        topics: list[str],
        limit: int = 20,
    ) -> list[TrailLoadResult]:
        """
        Search trails by topic.

        AGENTESE: self.trail.search?topics=...

        Args:
            topics: Topics to search for (any match)
            limit: Maximum results (default 20)

        Returns:
            List of TrailLoadResult with matching topics
        """
        async with self.session_factory() as session:
            # Note: This is a simplified search—real impl would use GIN index
            stmt = select(TrailRow).where(TrailRow.is_active == True).limit(limit)  # noqa: E712

            result = await session.execute(stmt)
            trails = result.scalars().all()

            # Filter by topics (in-memory for now)
            matching = []
            for trail in trails:
                trail_topics = trail.topics or []
                if any(t in trail_topics for t in topics):
                    loaded = await self.load_trail(trail.id)
                    if loaded:
                        matching.append(loaded)

            return matching

    # =========================================================================
    # Evidence and Commitments
    # =========================================================================

    async def save_evidence(
        self,
        trail_id: str,
        evidence: "ExplorationEvidence",
        source_step_index: int | None = None,
    ) -> str:
        """
        Save evidence linked to a trail.

        AGENTESE: self.trail.evidence.add

        Args:
            trail_id: The trail to attach evidence to
            evidence: The Evidence object
            source_step_index: Optional step that generated this evidence

        Returns:
            Evidence ID
        """
        async with self.session_factory() as session:
            evidence_row = TrailEvidenceRow(
                trail_id=trail_id,
                claim=evidence.claim,
                strength=evidence.strength.value
                if hasattr(evidence.strength, "value")
                else str(evidence.strength),
                content={"source": evidence.source, "content": evidence.content},
                source_step_index=source_step_index,
            )
            session.add(evidence_row)
            await session.commit()
            return evidence_row.id

    async def save_commitment(
        self,
        trail_id: str,
        claim: "Claim",
        level: str,
        evidence_ids: list[str],
        observer: "Observer | None" = None,
    ) -> str:
        """
        Save a commitment linked to a trail.

        AGENTESE: self.trail.commit

        Args:
            trail_id: The trail supporting this commitment
            claim: The Claim object
            level: Commitment level (tentative, moderate, strong, definitive)
            evidence_ids: Evidence supporting this commitment
            observer: Who is committing

        Returns:
            Commitment ID
        """
        async with self.session_factory() as session:
            commitment = TrailCommitmentRow(
                trail_id=trail_id,
                claim=claim.statement,
                level=level,
                evidence_ids=evidence_ids,
                committed_by_id=observer.id if observer else None,
            )
            session.add(commitment)
            await session.commit()
            return commitment.id

    # =========================================================================
    # Status Operations
    # =========================================================================

    async def manifest(self) -> TrailStatus:
        """
        Get trail storage health status.

        AGENTESE: self.trail.status

        Returns:
            TrailStatus with counts and health metrics
        """
        async with self.session_factory() as session:
            # Count trails
            trail_count = await session.execute(select(func.count()).select_from(TrailRow))
            total_trails = trail_count.scalar() or 0

            # Count active trails
            active_count = await session.execute(
                select(func.count()).select_from(TrailRow).where(TrailRow.is_active == True)  # noqa: E712
            )
            active_trails = active_count.scalar() or 0

            # Count forked trails
            forked_count = await session.execute(
                select(func.count())
                .select_from(TrailRow)
                .where(TrailRow.forked_from_id.isnot(None))
            )
            forked_trails = forked_count.scalar() or 0

            # Count steps
            step_count = await session.execute(select(func.count()).select_from(TrailStepRow))
            total_steps = step_count.scalar() or 0

        # Detect backend
        try:
            engine = self.session_factory.kw.get("bind")
            backend = engine.dialect.name if engine and hasattr(engine, "dialect") else "unknown"
        except Exception:
            backend = "unknown"

        return TrailStatus(
            total_trails=total_trails,
            total_steps=total_steps,
            active_trails=active_trails,
            forked_trails=forked_trails,
            storage_backend=backend,
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _compute_content_hash(self, trail: "ExplorationTrail") -> str:
        """Compute SHA256 hash of trail content for integrity."""
        content = json.dumps(
            {
                "name": trail.name,
                "steps": [
                    {"node": s.node, "edge": s.edge_taken, "annotation": s.annotation}
                    for s in trail.steps
                ],
            },
            sort_keys=True,
        )
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def _extract_topics(self, trail: "ExplorationTrail") -> list[str]:
        """Extract topics from trail steps (simple keyword extraction)."""
        topics: set[str] = set()
        for step in trail.steps:
            # Extract from node path
            parts = step.node.split(".")
            for part in parts:
                if len(part) > 2 and part not in ("world", "self", "concept", "void", "time"):
                    topics.add(part.lower())
            # Extract from edge
            if step.edge_taken:
                topics.add(step.edge_taken.lower())
        return list(topics)[:10]  # Cap at 10 topics

    async def _store_semantic_content(
        self,
        trail_id: str,
        trail: "ExplorationTrail",
    ) -> str | None:
        """Store trail semantic content in D-gent."""
        if not self.dgent:
            return None

        # Build semantic content
        content_parts = [f"Trail: {trail.name or trail_id}"]
        for step in trail.steps:
            edge_str = f" --[{step.edge_taken}]--> " if step.edge_taken else "(start) "
            content_parts.append(f"  {edge_str}{step.node}")
            if step.annotation:
                content_parts.append(f"      ^ {step.annotation}")

        datum = Datum(
            id=f"trail-{trail_id}",
            content="\n".join(content_parts).encode("utf-8"),
            created_at=time.time(),
            causal_parent=None,
            metadata={
                "type": "trail",
                "name": trail.name or "",
                "step_count": str(len(trail.steps)),
            },
        )

        return await self.dgent.put(datum)


__all__ = [
    "TrailStorageAdapter",
    "TrailSaveResult",
    "TrailLoadResult",
    "TrailSearchResult",
    "TrailStatus",
    "VersionConflict",
]
