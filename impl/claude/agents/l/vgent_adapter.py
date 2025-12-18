"""
L-gent V-gent Adapter: Bridge V-gent protocol to L-gent's VectorBackend.

Phase 9 Implementation (V-gent Integration):
This module provides backward compatibility by adapting the new V-gent
protocol to L-gent's existing VectorBackend interface.

Two adapters:
1. VgentToLgentAdapter: Wraps VgentProtocol for use where L-gent VectorBackend is expected
2. LgentToVgentAdapter: Wraps L-gent VectorBackend for use where VgentProtocol is expected

Migration Path:
1. New code: Use VgentProtocol directly
2. Existing code: Use VgentToLgentAdapter for compatibility
3. Eventually: Deprecate L-gent VectorBackend entirely

Example:
    from agents.v import MemoryVectorBackend, VgentProtocol
    from agents.l.vgent_adapter import VgentToLgentAdapter

    # New V-gent backend
    vgent: VgentProtocol = MemoryVectorBackend(dimension=384)

    # Adapt for L-gent (backward compatible)
    lgent_backend = VgentToLgentAdapter(vgent)

    # Use with existing L-gent code
    results = await lgent_backend.search(query_vector, limit=10)
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from .types import CatalogEntry
from .vector_backend import VectorBackend as LgentVectorBackend, VectorSearchResult

if TYPE_CHECKING:
    from agents.v import SearchResult as VgentSearchResult, VgentProtocol


@dataclass
class VgentAvailability:
    """Check V-gent availability."""

    available: bool
    reason: str | None = None


def check_vgent_available() -> VgentAvailability:
    """Check if V-gent is available for import."""
    try:
        from agents.v import VgentProtocol  # noqa: F401

        return VgentAvailability(available=True)
    except ImportError as e:
        return VgentAvailability(available=False, reason=str(e))


class VgentToLgentAdapter:
    """
    Adapter that wraps VgentProtocol to implement L-gent's VectorBackend.

    This allows V-gent backends to be used in existing L-gent code that
    expects VectorBackend interface.

    Example:
        from agents.v import MemoryVectorBackend
        from agents.l.vgent_adapter import VgentToLgentAdapter

        vgent = MemoryVectorBackend(dimension=384)
        lgent_backend = VgentToLgentAdapter(vgent)

        # Now usable with SemanticBrain, VectorCatalog, etc.
        results = await lgent_backend.search(query_vector, limit=10)
    """

    def __init__(self, vgent: "VgentProtocol"):
        """
        Initialize adapter.

        Args:
            vgent: V-gent protocol implementation to wrap
        """
        self._vgent = vgent

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        return self._vgent.dimension

    async def add(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """
        Add or update entry.

        Args:
            id: Unique identifier
            vector: Embedding vector
            metadata: Entry metadata
        """
        # Convert metadata values to strings for V-gent
        str_metadata = {k: str(v) for k, v in metadata.items()}
        await self._vgent.add(id, vector, str_metadata)

    async def add_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        """
        Add multiple entries efficiently.

        Args:
            ids: List of unique identifiers
            vectors: List of embedding vectors
            metadata: List of entry metadata
        """
        entries: list[tuple[str, list[float], dict[str, str] | None]] = []
        for id, vector, meta in zip(ids, vectors, metadata):
            str_meta: dict[str, str] | None = {k: str(v) for k, v in meta.items()}
            entries.append((id, vector, str_meta))
        await self._vgent.add_batch(entries)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
        threshold: Optional[float] = None,
    ) -> list[VectorSearchResult]:
        """
        Search for similar entries.

        Args:
            query_vector: Query embedding
            limit: Maximum number of results
            filters: Optional metadata filters
            threshold: Optional minimum similarity threshold

        Returns:
            List of results sorted by similarity (descending)
        """
        # Convert filters to string values
        str_filters = None
        if filters:
            str_filters = {k: str(v) for k, v in filters.items()}

        vgent_results = await self._vgent.search(
            query_vector, limit=limit, filters=str_filters, threshold=threshold
        )

        # Convert V-gent SearchResult to L-gent VectorSearchResult
        results = []
        for vr in vgent_results:
            results.append(
                VectorSearchResult(
                    id=vr.id,
                    entry=None,  # type: ignore  # Will be filled by caller
                    distance=vr.distance,
                    similarity=vr.similarity,
                    metadata=dict(vr.metadata),
                )
            )

        return results

    async def remove(self, id: str) -> None:
        """
        Remove entry by ID.

        Args:
            id: Entry identifier to remove
        """
        await self._vgent.remove(id)

    async def clear(self) -> None:
        """Remove all entries."""
        await self._vgent.clear()

    async def count(self) -> int:
        """Get number of entries in backend."""
        return await self._vgent.count()


class LgentToVgentAdapter:
    """
    Adapter that wraps L-gent VectorBackend to implement VgentProtocol.

    This allows existing L-gent backends (ChromaDB, FAISS) to be used
    where VgentProtocol is expected.

    Example:
        from agents.l import ChromaDBBackend
        from agents.l.vgent_adapter import LgentToVgentAdapter

        lgent = ChromaDBBackend(path="./chroma", dimension=384)
        vgent_compatible = LgentToVgentAdapter(lgent)

        # Now usable with V-gent consumers
        result = await vgent_compatible.get("doc1")
    """

    def __init__(self, lgent_backend: LgentVectorBackend, metric: str = "cosine"):
        """
        Initialize adapter.

        Args:
            lgent_backend: L-gent VectorBackend to wrap
            metric: Distance metric name (for VgentProtocol compliance)
        """
        from agents.v import DistanceMetric as VgentDistanceMetric

        self._lgent = lgent_backend
        self._metric_name = metric
        self._DistanceMetric = VgentDistanceMetric  # Store for property access

        # Map string to DistanceMetric enum
        metric_map = {
            "cosine": VgentDistanceMetric.COSINE,
            "euclidean": VgentDistanceMetric.EUCLIDEAN,
            "dot_product": VgentDistanceMetric.DOT_PRODUCT,
            "manhattan": VgentDistanceMetric.MANHATTAN,
        }
        self._metric = metric_map.get(metric, VgentDistanceMetric.COSINE)

        # Track entries for get() since L-gent doesn't have it
        self._entries: dict[str, tuple[list[float], dict[str, str]]] = {}

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        return self._lgent.dimension

    @property
    def metric(self) -> Any:  # Actually DistanceMetric, but type is dynamic import
        """Distance metric used for comparison."""
        return self._metric

    async def add(
        self,
        id: str,
        embedding: Any,  # Embedding | list[float]
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
        """
        from agents.v import Embedding

        # Normalize embedding to list
        if isinstance(embedding, Embedding):
            vector = embedding.to_list()
        else:
            vector = list(embedding)

        meta = metadata or {}
        await self._lgent.add(id, vector, dict(meta))
        self._entries[id] = (vector, meta)
        return id

    async def add_batch(
        self,
        entries: list[tuple[str, Any, dict[str, str] | None]],
    ) -> list[str]:
        """
        Add multiple vectors efficiently.

        Args:
            entries: List of (id, embedding, metadata) tuples

        Returns:
            List of IDs added
        """
        from agents.v import Embedding

        ids = []
        vectors = []
        metadata_list = []

        for id, embedding, metadata in entries:
            if isinstance(embedding, Embedding):
                vector = embedding.to_list()
            else:
                vector = list(embedding)

            meta = metadata or {}
            ids.append(id)
            vectors.append(vector)
            metadata_list.append(dict(meta))
            self._entries[id] = (vector, meta)

        await self._lgent.add_batch(ids, vectors, metadata_list)
        return ids

    async def remove(self, id: str) -> bool:
        """
        Remove a vector by ID.

        Args:
            id: The vector ID to remove

        Returns:
            True if removed, False if not found
        """
        existed = id in self._entries
        await self._lgent.remove(id)
        self._entries.pop(id, None)
        return existed

    async def clear(self) -> int:
        """
        Remove all vectors from the index.

        Returns:
            Number of vectors removed
        """
        count = len(self._entries)
        await self._lgent.clear()
        self._entries.clear()
        return count

    async def get(self, id: str) -> Any:  # VectorEntry | None
        """
        Retrieve a vector by ID.

        Args:
            id: The vector ID

        Returns:
            VectorEntry if found, None otherwise
        """
        from agents.v import Embedding, VectorEntry

        if id not in self._entries:
            return None

        vector, metadata = self._entries[id]
        embedding = Embedding.from_list(vector, source="lgent-adapter")
        return VectorEntry(id=id, embedding=embedding, metadata=metadata)

    async def search(
        self,
        query: Any,  # Embedding | list[float]
        limit: int = 10,
        filters: dict[str, str] | None = None,
        threshold: float | None = None,
    ) -> list["VgentSearchResult"]:
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
        from agents.v import Embedding, SearchResult

        # Normalize query to list
        if isinstance(query, Embedding):
            query_vector = query.to_list()
        else:
            query_vector = list(query)

        lgent_results = await self._lgent.search(
            query_vector, limit=limit, filters=filters, threshold=threshold
        )

        # Convert L-gent VectorSearchResult to V-gent SearchResult
        results = []
        for lr in lgent_results:
            results.append(
                SearchResult(
                    id=lr.id,
                    similarity=lr.similarity,
                    distance=lr.distance,
                    metadata={k: str(v) for k, v in lr.metadata.items()},
                )
            )

        return results

    async def count(self) -> int:
        """
        Get number of vectors in the index.

        Returns:
            Total vector count
        """
        return await self._lgent.count()

    async def exists(self, id: str) -> bool:
        """
        Check if a vector exists.

        Args:
            id: The vector ID

        Returns:
            True if exists, False otherwise
        """
        return id in self._entries


def create_vgent_adapter(
    vgent: Optional["VgentProtocol"] = None,
    dimension: int = 384,
    use_dgent: bool = True,
) -> VgentToLgentAdapter:
    """
    Create a V-gent adapter for use with L-gent code.

    This is the recommended way to integrate V-gent with existing L-gent code.

    Args:
        vgent: Optional V-gent protocol implementation (creates default if None)
        dimension: Vector dimension (only used if vgent is None)
        use_dgent: If True and vgent is None, try to use D-gent backend

    Returns:
        VgentToLgentAdapter wrapping the V-gent backend
    """
    if vgent is None:
        from agents.v import MemoryVectorBackend, create_vgent

        if use_dgent:
            # Try to create V-gent router (will fall back to memory if D-gent unavailable)
            try:
                vgent = create_vgent(dimension=dimension)
            except Exception:
                # Fall back to memory if D-gent isn't available
                vgent = MemoryVectorBackend(dimension=dimension)
        else:
            # Explicitly use memory backend
            vgent = MemoryVectorBackend(dimension=dimension)

    return VgentToLgentAdapter(vgent)


def migrate_lgent_backend_to_vgent(
    lgent_backend: LgentVectorBackend,
) -> LgentToVgentAdapter:
    """
    Wrap an existing L-gent VectorBackend to make it V-gent compatible.

    This is for gradually migrating codebases from L-gent to V-gent.

    Args:
        lgent_backend: Existing L-gent VectorBackend

    Returns:
        LgentToVgentAdapter wrapping the backend

    Example:
        # Existing L-gent code
        from agents.l import ChromaDBBackend
        backend = ChromaDBBackend(path="./chroma", dimension=384)

        # Migrate to V-gent compatible
        from agents.l.vgent_adapter import migrate_lgent_backend_to_vgent
        vgent_compatible = migrate_lgent_backend_to_vgent(backend)

        # Now usable with V-gent consumers
        result = await vgent_compatible.get("doc1")
    """
    warnings.warn(
        "migrate_lgent_backend_to_vgent is for migration only. "
        "New code should use agents.v directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    return LgentToVgentAdapter(lgent_backend)
