"""
VgentProtocol: The minimal interface for vector operations.

Seven methods for vector storage and search:
- add: Insert vector with ID and metadata
- add_batch: Insert multiple vectors efficiently
- search: Find similar vectors
- get: Retrieve vector by ID
- remove: Delete vector by ID
- clear: Remove all vectors
- count: Get number of vectors

Plus two introspection properties:
- dimension: Vector dimension
- metric: Distance metric
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .types import DistanceMetric, Embedding, SearchResult, VectorEntry


@runtime_checkable
class VgentProtocol(Protocol):
    """
    The minimal interface every V-gent backend implements.

    V-gent is a pure Agent[Query, Results]—stateless computation over vectors.
    The index state is implicit in the backend, not a polynomial mode.

    Seven methods for vector operations:
    - add: Insert vector with ID and metadata
    - add_batch: Insert multiple vectors efficiently
    - search: Find similar vectors
    - get: Retrieve vector by ID
    - remove: Delete vector by ID
    - clear: Remove all vectors
    - count: Get number of vectors

    Mathematical Properties:
    - Idempotence: add(id, embedding) twice has same effect as once
    - Monotonicity: count() increases with add(), decreases with remove()
    """

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        ...

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        ...

    # --- Write Operations ---

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
            The ID (same as input, for chaining)

        Note:
            If ID already exists, the vector is updated (idempotent).
        """
        ...

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

        Note:
            More efficient than repeated add() calls for bulk ingestion.
        """
        ...

    async def remove(self, id: str) -> bool:
        """
        Remove a vector by ID.

        Args:
            id: The vector ID to remove

        Returns:
            True if removed, False if not found
        """
        ...

    async def clear(self) -> int:
        """
        Remove all vectors from the index.

        Returns:
            Number of vectors removed
        """
        ...

    # --- Read Operations ---

    async def get(self, id: str) -> VectorEntry | None:
        """
        Retrieve a vector by ID.

        Args:
            id: The vector ID

        Returns:
            VectorEntry if found, None otherwise
        """
        ...

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """
        Find similar vectors.

        Args:
            query: The query vector
            limit: Maximum results to return
            filters: Optional metadata filters (exact match)
            threshold: Optional minimum similarity (0.0 to 1.0)

        Returns:
            List of SearchResult, sorted by similarity (highest first)
        """
        ...

    async def count(self) -> int:
        """
        Get number of vectors in the index.

        Returns:
            Total vector count
        """
        ...

    # --- Introspection ---

    async def exists(self, id: str) -> bool:
        """
        Check if a vector exists.

        Args:
            id: The vector ID

        Returns:
            True if exists, False otherwise
        """
        ...


class BaseVgent:
    """
    Base class providing default implementations for optional methods.

    Backends should inherit from this and implement the core methods:
    - add, add_batch, remove, clear, get, search, count
    - dimension (property), metric (property)

    BaseVgent provides:
    - exists() via get()
    - add_batch() via repeated add()

    Subclasses may override for efficiency.
    """

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        raise NotImplementedError

    @property
    def metric(self) -> DistanceMetric:
        """Distance metric used for comparison."""
        raise NotImplementedError

    async def add(
        self,
        id: str,
        embedding: Embedding | list[float],
        metadata: dict[str, str] | None = None,
    ) -> str:
        """Add a vector to the index."""
        raise NotImplementedError

    async def add_batch(
        self,
        entries: list[tuple[str, Embedding | list[float], dict[str, str] | None]],
    ) -> list[str]:
        """Default: add one at a time. Override for efficiency."""
        ids = []
        for id, embedding, metadata in entries:
            await self.add(id, embedding, metadata)
            ids.append(id)
        return ids

    async def remove(self, id: str) -> bool:
        """Remove a vector by ID."""
        raise NotImplementedError

    async def clear(self) -> int:
        """Remove all vectors from the index."""
        raise NotImplementedError

    async def get(self, id: str) -> VectorEntry | None:
        """Retrieve a vector by ID."""
        raise NotImplementedError

    async def search(
        self,
        query: Embedding | list[float],
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list[SearchResult]:
        """Find similar vectors."""
        raise NotImplementedError

    async def count(self) -> int:
        """Get number of vectors in the index."""
        raise NotImplementedError

    async def exists(self, id: str) -> bool:
        """Default: check via get()."""
        return await self.get(id) is not None

    def _normalize_embedding(self, embedding: Embedding | list[float]) -> Embedding:
        """
        Normalize embedding input to Embedding type.

        Args:
            embedding: Embedding or list of floats

        Returns:
            Embedding instance

        Raises:
            ValueError: If dimension doesn't match backend
        """
        if isinstance(embedding, Embedding):
            if embedding.dimension != self.dimension:
                raise ValueError(
                    f"Embedding dimension {embedding.dimension} != backend dimension {self.dimension}"
                )
            return embedding
        else:
            if len(embedding) != self.dimension:
                raise ValueError(
                    f"Vector length {len(embedding)} != backend dimension {self.dimension}"
                )
            return Embedding.from_list(embedding)

    def _matches_filters(self, metadata: dict[str, str], filters: dict[str, str]) -> bool:
        """Check if metadata matches all filters (exact match)."""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
