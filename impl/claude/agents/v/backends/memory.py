"""
MemoryVectorBackend: In-memory vector storage for V-gent.

Tier 0 in the projection lattice. Fast but ephemeral.
Vectors are lost when the process exits.

Characteristics:
- O(n) search (linear scan)
- O(1) add/remove/get
- No persistence
- No external dependencies
- Always available (tier 0 fallback)

Use for:
- Testing
- Small datasets (< 10K vectors)
- Ephemeral operations
"""

from __future__ import annotations

from ..protocol import BaseVgent
from ..types import DistanceMetric, Embedding, SearchResult, VectorEntry


class MemoryVectorBackend(BaseVgent):
    """
    In-memory vector storage backend.

    Fast but ephemeral. Vectors are lost on process exit.
    Uses linear scan for search—suitable for small datasets (<10K vectors).

    Example:
        backend = MemoryVectorBackend(dimension=768)
        await backend.add("doc1", [0.1, 0.2, ...])
        results = await backend.search([0.1, 0.2, ...], limit=10)

    Thread-safety: Not thread-safe. Use with asyncio only.
    """

    def __init__(
        self,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
    ) -> None:
        """
        Initialize memory backend.

        Args:
            dimension: Dimension of vectors (must match embeddings)
            metric: Distance metric for similarity computation
        """
        self._dimension = dimension
        self._metric = metric
        self._store: dict[str, VectorEntry] = {}

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        return self._dimension

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        return self._metric

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

        entry = VectorEntry(
            id=id,
            embedding=emb,
            metadata=metadata or {},
        )
        self._store[id] = entry
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
            emb = self._normalize_embedding(embedding)
            entry = VectorEntry(
                id=id,
                embedding=emb,
                metadata=metadata or {},
            )
            self._store[id] = entry
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
        if id in self._store:
            del self._store[id]
            return True
        return False

    async def clear(self) -> int:
        """
        Remove all vectors from the index.

        Returns:
            Number of vectors removed
        """
        count = len(self._store)
        self._store.clear()
        return count

    async def get(self, id: str) -> VectorEntry | None:
        """
        Retrieve a vector by ID.

        Args:
            id: The vector ID

        Returns:
            VectorEntry if found, None otherwise
        """
        return self._store.get(id)

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

        for entry in self._store.values():
            # Apply metadata filters
            if filters and not self._matches_filters(entry.metadata, filters):
                continue

            # Compute similarity
            similarity = self._metric.similarity(query_emb.vector, entry.embedding.vector)
            distance = self._metric.distance(query_emb.vector, entry.embedding.vector)

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            results.append(
                SearchResult(
                    id=entry.id,
                    similarity=similarity,
                    distance=distance,
                    metadata=entry.metadata,
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
        return len(self._store)

    async def exists(self, id: str) -> bool:
        """
        Check if a vector exists (direct lookup, faster than get).

        Args:
            id: The vector ID

        Returns:
            True if exists, False otherwise
        """
        return id in self._store

    def __repr__(self) -> str:
        return f"MemoryVectorBackend(dimension={self._dimension}, metric={self._metric.value}, count={len(self._store)})"
