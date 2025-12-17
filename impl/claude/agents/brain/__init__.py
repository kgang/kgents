"""
Holographic Brain: Crown Jewel Memory with D-gent Triad Integration.

This module wires the Brain CLI to proper infrastructure:
- Left Hemisphere: SQLite relational store (source of truth)
- Right Hemisphere: NumPy vector store (semantic index)
- Embedder: L-gent sentence-transformers (or fallback)
- BicameralMemory: Cross-hemisphere coherency

AGENTESE: self.memory.*

XDG Paths:
- ~/.local/share/kgents/brain/brain.db (SQLite)
- ~/.local/share/kgents/brain/vectors.npy (NumPy vectors)

Usage:
    from agents.brain import get_brain_crystal, BrainCrystal

    brain = await get_brain_crystal()
    await brain.capture("Python is great for data science")
    results = await brain.search("programming language")
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# Thread-safe singleton
_brain_crystal: "BrainCrystal | None" = None
_brain_lock = asyncio.Lock()


def _get_brain_data_dir() -> Path:
    """Get XDG-compliant brain data directory."""
    data_home = Path.home() / ".local" / "share" / "kgents" / "brain"
    data_home.mkdir(parents=True, exist_ok=True)
    return data_home


@dataclass
class CaptureResult:
    """Result of a brain capture operation."""

    concept_id: str
    content: str
    captured_at: str
    has_embedding: bool
    storage: str = "bicameral"


@dataclass
class SearchResult:
    """Result from brain semantic search."""

    concept_id: str
    content: str
    similarity: float
    captured_at: str
    is_stale: bool = False


@dataclass
class BrainStatus:
    """Brain health status."""

    total_captures: int
    vector_count: int
    has_semantic: bool
    coherency_rate: float
    ghosts_healed: int
    storage_path: str
    storage_backend: str = "sqlite"  # "sqlite" or "postgres"


class BrainCrystal:
    """
    Holographic Brain with D-gent Triad Integration.

    Provides:
    - capture(): Store content with semantic embedding
    - search(): Semantic similarity search
    - recall(): Direct lookup by ID
    - status(): Health check

    The BrainCrystal uses BicameralMemory under the hood:
    - Left Hemisphere: SQLite (captures table)
    - Right Hemisphere: NumPy vector store
    - Coherency Protocol: Auto-heals ghost memories
    """

    def __init__(
        self,
        relational_store: Any,
        vector_store: Any | None,
        embedder: Any | None,
        data_dir: Path,
        storage_backend: str = "sqlite",
    ) -> None:
        """Initialize BrainCrystal with stores."""
        self._relational = relational_store
        self._vector = vector_store
        self._embedder = embedder
        self._data_dir = data_dir
        self._storage_backend = storage_backend
        self._initialized = False

        # Stats
        self._total_captures = 0
        self._ghosts_healed = 0

    async def _ensure_initialized(self) -> None:
        """Ensure database schema exists."""
        if self._initialized:
            return

        # Create captures table
        await self._relational.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                content_hash TEXT,
                embedding_json TEXT,
                captured_at TEXT NOT NULL,
                updated_at TEXT,
                metadata_json TEXT
            )
        """)

        # Create index for faster lookups
        await self._relational.execute("""
            CREATE INDEX IF NOT EXISTS idx_captures_captured_at
            ON captures(captured_at)
        """)

        # Migration: Add access_count column if missing (stigmergic trails)
        # SQLite doesn't support ADD COLUMN IF NOT EXISTS, so we check first
        try:
            await self._relational.execute(
                "ALTER TABLE captures ADD COLUMN access_count INTEGER DEFAULT 0"
            )
        except Exception:
            # Column already exists
            pass

        # Initialize vector store (load existing vectors from disk)
        if self._vector is not None and hasattr(self._vector, "initialize"):
            await self._vector.initialize()

        # Load existing count
        result = await self._relational.fetch_one(
            "SELECT COUNT(*) as count FROM captures"
        )
        if result:
            self._total_captures = result["count"]

        self._initialized = True

    async def capture(
        self,
        content: str,
        concept_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CaptureResult:
        """
        Capture content to brain with semantic embedding.

        Args:
            content: Text content to capture
            concept_id: Optional ID (auto-generated if not provided)
            metadata: Optional metadata dict

        Returns:
            CaptureResult with capture details
        """
        await self._ensure_initialized()

        # Generate ID if not provided
        if concept_id is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            import hashlib

            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            concept_id = f"capture_{timestamp}_{content_hash}"

        now = datetime.now().isoformat()

        # Generate embedding if embedder available
        embedding: list[float] | None = None
        has_embedding = False
        if self._embedder is not None:
            try:
                embedding = await self._get_embedding(content)
                has_embedding = True
            except Exception:
                pass

        # Store in relational (Left Hemisphere)
        content_hash = self._compute_hash(content)
        await self._relational.execute(
            """
            INSERT INTO captures (id, content, content_hash, embedding_json, captured_at, metadata_json)
            VALUES (:id, :content, :content_hash, :embedding_json, :captured_at, :metadata_json)
            ON CONFLICT(id) DO UPDATE SET
                content = :content,
                content_hash = :content_hash,
                embedding_json = :embedding_json,
                updated_at = :captured_at,
                metadata_json = :metadata_json
            """,
            {
                "id": concept_id,
                "content": content,
                "content_hash": content_hash,
                "embedding_json": json.dumps(embedding) if embedding else None,
                "captured_at": now,
                "metadata_json": json.dumps(metadata) if metadata else None,
            },
        )

        # Store in vector store (Right Hemisphere)
        if embedding and self._vector is not None:
            await self._vector.upsert(
                id=concept_id,
                vector=embedding,
                metadata={
                    "content_hash": content_hash,
                    "captured_at": now,
                },
            )

        self._total_captures += 1

        return CaptureResult(
            concept_id=concept_id,
            content=content,
            captured_at=now,
            has_embedding=has_embedding,
        )

    async def search(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.3,
    ) -> list[SearchResult]:
        """
        Semantic search for similar captures.

        Args:
            query: Search query text
            limit: Max results to return
            threshold: Minimum similarity threshold (0-1)

        Returns:
            List of SearchResult ordered by similarity
        """
        await self._ensure_initialized()

        # If no embedder/vector store, fall back to text search
        if self._embedder is None or self._vector is None:
            return await self._text_search(query, limit)

        # Get query embedding
        query_embedding = await self._get_embedding(query)

        # Search vector store
        vector_results = await self._vector.search(
            query_vector=query_embedding,
            limit=limit * 2,  # Over-fetch for ghost filtering
        )

        # Validate against relational (Coherency Protocol)
        results = []
        ghost_ids = []

        for vec_result in vector_results:
            if vec_result.distance > (1 - threshold):
                continue  # Below threshold

            # Fetch from relational
            row = await self._relational.fetch_one(
                "SELECT * FROM captures WHERE id = :id",
                {"id": vec_result.id},
            )

            if row is None:
                # Ghost memory detected
                ghost_ids.append(vec_result.id)
                continue

            # Check staleness
            is_stale = False
            if row.get("content_hash") and vec_result.metadata:
                stored_hash = vec_result.metadata.get("content_hash")
                if stored_hash and stored_hash != row["content_hash"]:
                    is_stale = True

            results.append(
                SearchResult(
                    concept_id=vec_result.id,
                    content=row["content"],
                    similarity=1
                    - vec_result.distance,  # Convert distance to similarity
                    captured_at=row["captured_at"],
                    is_stale=is_stale,
                )
            )

            if len(results) >= limit:
                break

        # Heal ghosts (auto-remove from vector store)
        for ghost_id in ghost_ids:
            try:
                await self._vector.delete(ghost_id)
                self._ghosts_healed += 1
            except Exception:
                pass

        # Increment access_count for surfaced results (stigmergic trails)
        # This makes frequently accessed memories "glow brighter"
        if results:
            result_ids = [r.concept_id for r in results]
            for rid in result_ids:
                try:
                    await self._relational.execute(
                        "UPDATE captures SET access_count = COALESCE(access_count, 0) + 1 WHERE id = :id",
                        {"id": rid},
                    )
                except Exception:
                    pass  # Non-critical, don't fail search

        return results

    async def _text_search(self, query: str, limit: int) -> list[SearchResult]:
        """Fallback text search when no embedder available."""
        # Simple LIKE search
        rows = await self._relational.fetch_all(
            """
            SELECT * FROM captures
            WHERE content LIKE :query
            ORDER BY captured_at DESC
            LIMIT :limit
            """,
            {"query": f"%{query}%", "limit": limit},
        )

        return [
            SearchResult(
                concept_id=row["id"],
                content=row["content"],
                similarity=0.5,  # Unknown similarity for text search
                captured_at=row["captured_at"],
            )
            for row in rows
        ]

    async def recall(self, concept_id: str) -> dict[str, Any] | None:
        """
        Direct lookup by ID (Left Hemisphere only).

        Args:
            concept_id: The capture ID

        Returns:
            Capture data or None
        """
        await self._ensure_initialized()

        row = await self._relational.fetch_one(
            "SELECT * FROM captures WHERE id = :id",
            {"id": concept_id},
        )

        if row is None:
            return None

        return {
            "concept_id": row["id"],
            "content": row["content"],
            "captured_at": row["captured_at"],
            "metadata": json.loads(row["metadata_json"])
            if row.get("metadata_json")
            else None,
        }

    async def list_captures(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """List recent captures."""
        await self._ensure_initialized()

        rows = await self._relational.fetch_all(
            """
            SELECT id, content, captured_at FROM captures
            ORDER BY captured_at DESC
            LIMIT :limit OFFSET :offset
            """,
            {"limit": limit, "offset": offset},
        )

        return [
            {
                "concept_id": row["id"],
                "content": row["content"][:100] + "..."
                if len(row["content"]) > 100
                else row["content"],
                "captured_at": row["captured_at"],
            }
            for row in rows
        ]

    async def surface(
        self,
        context: str | None = None,
        entropy: float = 0.7,
    ) -> SearchResult | None:
        """
        Surface a serendipitous memory from the void.

        The Accursed Share: Pull a random-ish relevant memory that might
        spark unexpected connections. Higher entropy = more randomness.

        Args:
            context: Optional context to bias selection (None = fully random)
            entropy: Randomness factor (0.0 = most relevant, 1.0 = fully random)

        Returns:
            A single SearchResult or None if brain is empty
        """
        import random

        await self._ensure_initialized()

        # Get total count
        result = await self._relational.fetch_one(
            "SELECT COUNT(*) as count FROM captures"
        )
        total = result["count"] if result else 0

        if total == 0:
            return None

        if context and self._embedder is not None and self._vector is not None:
            # Context-biased serendipity: search then randomly pick from results
            # Higher entropy = sample from more results
            search_limit = max(5, int(total * entropy * 0.5))
            candidates = await self.search(context, limit=search_limit, threshold=0.2)

            if candidates:
                # Weighted random: favor higher similarity but allow surprises
                weights = [(c.similarity ** (1 - entropy)) for c in candidates]
                selected = random.choices(candidates, weights=weights, k=1)[0]
                return selected

        # Fully random: pick any memory
        random_offset = random.randint(0, max(0, total - 1))
        row = await self._relational.fetch_one(
            """
            SELECT id, content, captured_at FROM captures
            ORDER BY captured_at DESC
            LIMIT 1 OFFSET :offset
            """,
            {"offset": random_offset},
        )

        if row is None:
            return None

        return SearchResult(
            concept_id=row["id"],
            content=row["content"],
            similarity=entropy,  # Use entropy as "surprise" score
            captured_at=row["captured_at"],
        )

    async def get_topology_data(
        self,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """
        Get full topology data including embeddings for 3D visualization.

        Returns:
            List of captures with id, content preview, embedding, and captured_at
        """
        await self._ensure_initialized()

        rows = await self._relational.fetch_all(
            """
            SELECT id, content, embedding_json, captured_at FROM captures
            ORDER BY captured_at DESC
            LIMIT :limit
            """,
            {"limit": limit},
        )

        result = []
        for row in rows:
            embedding = None
            if row.get("embedding_json"):
                try:
                    embedding = json.loads(row["embedding_json"])
                except (json.JSONDecodeError, TypeError):
                    pass

            result.append(
                {
                    "concept_id": row["id"],
                    "content": row["content"],
                    "content_preview": row["content"][:100] + "..."
                    if len(row["content"]) > 100
                    else row["content"],
                    "embedding": embedding,
                    "captured_at": row["captured_at"],
                }
            )

        return result

    async def status(self) -> BrainStatus:
        """Get brain health status."""
        await self._ensure_initialized()

        # Count captures
        result = await self._relational.fetch_one(
            "SELECT COUNT(*) as count FROM captures"
        )
        total_captures = result["count"] if result else 0

        # Count vectors
        vector_count = 0
        if self._vector is not None:
            try:
                vector_count = await self._vector.count()
            except Exception:
                pass

        # Compute coherency rate
        coherency_rate = 1.0
        if vector_count > 0 and total_captures > 0:
            coherency_rate = min(total_captures / vector_count, 1.0)

        return BrainStatus(
            total_captures=total_captures,
            vector_count=vector_count,
            has_semantic=self._embedder is not None,
            coherency_rate=coherency_rate,
            ghosts_healed=self._ghosts_healed,
            storage_path=str(self._data_dir),
            storage_backend=self._storage_backend,
        )

    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text."""
        if self._embedder is None:
            return self._simple_embedding(text)

        # Call embedder - handle both sync and async
        result = self._embedder.embed(text)

        # If result is a coroutine, await it
        if asyncio.iscoroutine(result):
            result = await result

        # If result is all zeros (unfitted embedder), use simple embedding
        if all(x == 0.0 for x in result):
            return self._simple_embedding(text)

        return result

    def _simple_embedding(self, text: str, dimension: int = 128) -> list[float]:
        """Simple n-gram hash embedding with some semantic locality.

        Uses character trigrams to provide basic similarity:
        - "Python" and "python" will be similar
        - Similar words will share some trigrams

        Not as good as real embeddings but works without ML libraries.
        """
        import hashlib
        import math

        # Normalize text
        text = text.lower().strip()

        # Generate character trigrams
        trigrams = []
        for i in range(len(text) - 2):
            trigrams.append(text[i : i + 3])

        # Also add word-level features
        words = text.split()
        trigrams.extend(words)

        # Hash each trigram to a dimension index
        vector = [0.0] * dimension
        for gram in trigrams:
            # Hash to get index and value
            h = hashlib.md5(gram.encode()).digest()
            idx = h[0] % dimension
            val = (h[1] - 128) / 128.0  # Value between -1 and 1
            vector[idx] += val

        # L2 normalize
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude > 0:
            vector = [x / magnitude for x in vector]

        return vector

    def _compute_hash(self, content: str) -> str:
        """Compute content hash for staleness detection."""
        import hashlib

        return hashlib.md5(content.encode()).hexdigest()

    async def close(self) -> None:
        """Close database connections."""
        if self._relational:
            await self._relational.close()
        if self._vector and hasattr(self._vector, "close"):
            await self._vector.close()


async def get_brain_crystal() -> BrainCrystal:
    """
    Get or create the singleton BrainCrystal instance.

    This is the main entry point for Brain operations.

    Returns:
        Configured BrainCrystal with D-gent triad wiring
    """
    global _brain_crystal

    async with _brain_lock:
        if _brain_crystal is not None:
            return _brain_crystal

        _brain_crystal = await _create_brain_crystal()
        return _brain_crystal


async def _create_brain_crystal() -> BrainCrystal:
    """Create a new BrainCrystal with full D-gent wiring."""
    data_dir = _get_brain_data_dir()

    # Import stores lazily
    from protocols.cli.instance_db.providers import (
        NumpyVectorStore,
        StorageBackend,
        create_relational_store,
        get_current_backend,
    )

    # Create relational store - auto-selects Postgres if available, else SQLite
    # This enables Brain to persist to Postgres in production environments
    sqlite_path = data_dir / "brain.db"
    relational = await create_relational_store(
        backend="auto",
        sqlite_path=sqlite_path,
        wal_mode=True,
    )

    # Determine which backend was selected
    current_backend = await get_current_backend()
    import logging

    logger = logging.getLogger(__name__)
    backend_name = (
        "postgres" if current_backend == StorageBackend.POSTGRES else "sqlite"
    )
    if current_backend == StorageBackend.POSTGRES:
        logger.info("Brain using PostgreSQL backend")
    else:
        logger.info(f"Brain using SQLite backend at {sqlite_path}")

    # Create NumPy vector store (Right Hemisphere)
    # Use 128 dimensions (matches our simple embedding fallback)
    vector_path = data_dir / "vectors.json"
    dimension = 128  # Default dimension for n-gram embeddings
    vector: Any = None
    embedder: Any = None

    try:
        # Try to get L-gent embedder
        from agents.l import create_best_available_embedder

        embedder = create_best_available_embedder()
        emb_dimension = getattr(embedder, "dimension", 128)
        # Only use if it provides real embeddings (not TF-IDF which needs fitting)
        if emb_dimension > 0:
            dimension = emb_dimension
    except Exception:
        # Fall back to simple embedding
        pass

    # Create vector store with matching dimension
    vector = NumpyVectorStore(storage_path=vector_path, dimensions=dimension)

    # Note: Vector store will be initialized on first use via _ensure_initialized

    return BrainCrystal(
        relational_store=relational,
        vector_store=vector,
        embedder=embedder,
        data_dir=data_dir,
        storage_backend=backend_name,
    )


def reset_brain_crystal() -> None:
    """Reset the singleton (for testing)."""
    global _brain_crystal
    _brain_crystal = None
