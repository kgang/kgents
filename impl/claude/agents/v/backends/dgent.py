"""
DgentVectorBackend: Vector storage backed by D-gent.

Tier 1 in the projection lattice. Persistence via D-gent's projection lattice.

Architecture:
    - Vectors stored as Datum (bytes = struct-packed vector)
    - Metadata stored in Datum.metadata
    - In-memory index rebuilt on startup
    - Index updates are atomic with Datum writes

Characteristics:
    - O(n) search (linear scan of in-memory index)
    - Persists across restarts via D-gent
    - Inherits D-gent's graceful degradation
    - No external dependencies beyond D-gent

Use for:
    - Medium datasets (10K - 100K vectors)
    - Persistence without external dependencies
    - Integration with D-gent projection lattice
"""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from agents.d import Datum, DgentProtocol

from ..protocol import BaseVgent
from ..types import DistanceMetric, Embedding, SearchResult, VectorEntry

if TYPE_CHECKING:
    pass


class DgentVectorBackend(BaseVgent):
    """
    Vector storage backed by D-gent.

    Stores vectors as D-gent Datum with an in-memory index for fast search.
    Persistence is handled by D-gent's projection lattice (Memory → JSONL → SQLite → Postgres).

    Architecture:
        - Each vector is stored as a Datum with:
          - ID: "{namespace}:{vector_id}"
          - Content: struct-packed float array
          - Metadata: vector metadata + dimension info
        - In-memory index maps ID → vector tuple for O(n) search
        - Index is rebuilt from D-gent on startup via load_index()

    Example:
        from agents.d import DgentRouter
        from agents.v import DgentVectorBackend

        dgent = DgentRouter()  # Auto-selects best backend
        backend = DgentVectorBackend(dgent, dimension=768)
        await backend.load_index()  # Rebuild index from D-gent

        await backend.add("doc1", [0.1, 0.2, ...])
        results = await backend.search([0.1, 0.2, ...])

    Thread-safety: Not thread-safe. Use with asyncio only.
    """

    def __init__(
        self,
        dgent: DgentProtocol,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        namespace: str = "vectors",
    ) -> None:
        """
        Initialize D-gent-backed vector storage.

        Args:
            dgent: D-gent backend for persistence
            dimension: Dimension of vectors (must match embeddings)
            metric: Distance metric for similarity computation
            namespace: Prefix for vector IDs in D-gent (default: "vectors")
        """
        self._dgent = dgent
        self._dimension = dimension
        self._metric = metric
        self._namespace = namespace
        # In-memory index: vector_id → (vector_tuple, metadata)
        self._index: dict[str, tuple[tuple[float, ...], dict[str, str]]] = {}

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        return self._dimension

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        return self._metric

    @property
    def namespace(self) -> str:
        """Namespace prefix for D-gent storage."""
        return self._namespace

    # =========================================================================
    # Index Management
    # =========================================================================

    async def load_index(self) -> int:
        """
        Rebuild in-memory index from D-gent on startup.

        Call this after creating the backend to load persisted vectors.

        Returns:
            Number of vectors loaded into index
        """
        self._index.clear()

        # Fetch all vectors from D-gent with our namespace prefix
        prefix = f"{self._namespace}:"
        data = await self._dgent.list(prefix=prefix, limit=1_000_000)

        for datum in data:
            # Extract vector ID from full D-gent ID
            vector_id = datum.id[len(prefix) :]
            vector = self._deserialize_vector(datum.content)

            # Skip vectors with wrong dimension (data corruption or version mismatch)
            if len(vector) != self._dimension:
                continue

            self._index[vector_id] = (vector, dict(datum.metadata))

        return len(self._index)

    # =========================================================================
    # Serialization
    # =========================================================================

    def _serialize_vector(self, vector: tuple[float, ...]) -> bytes:
        """
        Serialize vector to bytes using struct pack.

        Format: packed array of floats (4 bytes each).
        """
        return struct.pack(f"{len(vector)}f", *vector)

    def _deserialize_vector(self, data: bytes) -> tuple[float, ...]:
        """
        Deserialize bytes to vector using struct unpack.
        """
        n = len(data) // 4  # 4 bytes per float
        return struct.unpack(f"{n}f", data)

    def _make_dgent_id(self, vector_id: str) -> str:
        """Create full D-gent ID from vector ID."""
        return f"{self._namespace}:{vector_id}"

    # =========================================================================
    # Write Operations
    # =========================================================================

    async def add(
        self,
        id: str,
        embedding: Embedding | list[float],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Add a vector to the index.

        Args:
            id: Unique identifier for this vector
            embedding: The vector (Embedding or raw list)
            metadata: Optional filterable metadata

        Returns:
            The ID (same as input)
        """
        emb = self._normalize_embedding(embedding)
        meta = metadata or {}

        # Store in D-gent
        dgent_id = self._make_dgent_id(id)
        datum = Datum.create(
            content=self._serialize_vector(emb.vector),
            id=dgent_id,
            metadata={
                **meta,
                "_dimension": str(self._dimension),
                "_source": emb.source,
            },
        )
        await self._dgent.put(datum)

        # Update in-memory index
        self._index[id] = (emb.vector, meta)

        return id

    async def add_batch(
        self,
        entries: list[tuple[str, Embedding | list[float], dict[str, str] | None]],
    ) -> list[str]:
        """
        Add multiple vectors efficiently.

        Args:
            entries: List of (id, embedding, metadata) tuples

        Returns:
            List of IDs added
        """
        ids = []
        for id, embedding, metadata in entries:
            await self.add(id, embedding, metadata)
            ids.append(id)
        return ids

    async def remove(self, id: str) -> bool:
        """
        Remove a vector by ID.

        Args:
            id: The vector ID to remove

        Returns:
            True if removed, False if not found
        """
        if id not in self._index:
            return False

        # Remove from D-gent
        dgent_id = self._make_dgent_id(id)
        await self._dgent.delete(dgent_id)

        # Remove from in-memory index
        del self._index[id]

        return True

    async def clear(self) -> int:
        """
        Remove all vectors from the index.

        Returns:
            Number of vectors removed
        """
        count = len(self._index)

        # Remove all from D-gent
        for vector_id in list(self._index.keys()):
            dgent_id = self._make_dgent_id(vector_id)
            await self._dgent.delete(dgent_id)

        # Clear in-memory index
        self._index.clear()

        return count

    # =========================================================================
    # Read Operations
    # =========================================================================

    async def get(self, id: str) -> VectorEntry | None:
        """
        Retrieve a vector by ID.

        Args:
            id: The vector ID

        Returns:
            VectorEntry if found, None otherwise
        """
        if id not in self._index:
            return None

        vector, metadata = self._index[id]

        return VectorEntry(
            id=id,
            embedding=Embedding(
                vector=vector,
                dimension=self._dimension,
                source="dgent",
            ),
            metadata=metadata,
        )

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """
        Find similar vectors using linear scan.

        Args:
            query: The query vector
            limit: Maximum results to return
            filters: Optional metadata filters (exact match)
            threshold: Optional minimum similarity (0.0 to 1.0)

        Returns:
            List of SearchResult, sorted by similarity (highest first)
        """
        query_emb = self._normalize_embedding(query)

        results: list[SearchResult] = []

        for id, (vector, metadata) in self._index.items():
            # Apply metadata filters
            if filters and not self._matches_filters(metadata, filters):
                continue

            # Compute similarity
            similarity = self._metric.similarity(query_emb.vector, vector)
            distance = self._metric.distance(query_emb.vector, vector)

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            results.append(
                SearchResult(
                    id=id,
                    similarity=similarity,
                    distance=distance,
                    metadata=metadata,
                )
            )

        # Sort by similarity (highest first) and limit
        results.sort()  # Uses __lt__ which sorts by similarity descending
        return results[:limit]

    async def count(self) -> int:
        """
        Get number of vectors in the index.

        Returns:
            Total vector count
        """
        return len(self._index)

    async def exists(self, id: str) -> bool:
        """
        Check if a vector exists (direct lookup, faster than get).

        Args:
            id: The vector ID

        Returns:
            True if exists, False otherwise
        """
        return id in self._index

    # =========================================================================
    # Introspection
    # =========================================================================

    def __repr__(self) -> str:
        return (
            f"DgentVectorBackend("
            f"dimension={self._dimension}, "
            f"metric={self._metric.value}, "
            f"namespace={self._namespace!r}, "
            f"count={len(self._index)})"
        )
