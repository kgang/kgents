"""
L-gent Vector DB: Tight D-gent Integration for Semantic Search.

This module bridges L-gent's vector backends with D-gent's VectorAgent,
providing a unified vector database layer as specified in the L-gent spec:

    "L-gent uses D-gents for persistence:
     - PersistentAgent: Store the catalog itself
     - VectorAgent: Semantic embedding index"

Key Features:
- DgentVectorBackend: VectorBackend protocol using D-gent's VectorAgent
- VectorCatalog: Complete integration of Catalog + Vector DB (now uses V-gent)
- Sync utilities: Keep L-gent catalog and D-gent vectors in sync
- Migration: Move between in-memory and D-gent backends

Architecture (Phase 9 - V-gent Integration):
    ┌─────────────────────────────────────────────────────────────┐
    │                       VectorCatalog                          │
    │    (Unified view: metadata via Registry, vectors via V-gent) │
    ├─────────────────────────────────────────────────────────────┤
    │   PersistentRegistry              VgentProtocol              │
    │   (D-gent: PersistentAgent)       (V-gent: any backend)      │
    └─────────────────────────────────────────────────────────────┘

Phase 8: Full D-gent integration for production workloads.
Phase 9: V-gent integration - VectorCatalog now uses VgentProtocol.
"""

from __future__ import annotations

# Import D-gent components
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, cast

from .semantic import Embedder, SemanticResult
from .types import Catalog, CatalogEntry, EntityType
from .vector_backend import VectorBackend, VectorSearchResult

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# V-gent integration (Phase 9)
VGENT_AVAILABLE = False
try:
    from agents.v import SearchResult as VgentSearchResult, VgentProtocol, create_vgent

    VGENT_AVAILABLE = True
except ImportError:
    VgentProtocol = None
    create_vgent = None
    VgentSearchResult = None

# Check for numpy (required for D-gent VectorAgent)
try:
    import numpy as np
    from agents.d.vector import NUMPY_AVAILABLE, DistanceMetric, VectorAgent
except ImportError:
    np = None
    VectorAgent = None
    DistanceMetric = None
    NUMPY_AVAILABLE = False


@dataclass
class VectorSyncState:
    """Track synchronization state between catalog and vector DB."""

    total_entries: int
    indexed_entries: int
    pending_entries: list[str]  # Entry IDs not yet indexed
    orphaned_vectors: list[str]  # Vector IDs without catalog entries
    last_sync: Optional[str] = None  # ISO timestamp


class DgentVectorBackend:
    """VectorBackend implementation using D-gent's VectorAgent.

    This bridges L-gent's VectorBackend protocol with D-gent's VectorAgent,
    enabling L-gent to use D-gent's vector storage primitives.

    Benefits over standalone backends (ChromaDB, FAISS):
    - Unified D-gent interface (same patterns as PersistentAgent)
    - Built-in persistence (D-gent handles disk I/O)
    - Semantic features: curvature, voids, geodesics from D-gent
    - No additional dependencies (only numpy)

    Example:
        backend = DgentVectorBackend(
            dimension=384,
            persistence_path=Path(".kgents/vectors.json")
        )
        await backend.add("agent_1", embedding, {"type": "agent"})
        results = await backend.search(query_embedding, limit=10)
    """

    def __init__(
        self,
        dimension: int = 384,
        persistence_path: Optional[Path] = None,
        distance: str = "cosine",
    ):
        """Initialize D-gent backed vector storage.

        Args:
            dimension: Vector dimension (must match embedder)
            persistence_path: Path for persistent storage (optional)
            distance: Distance metric ("cosine", "euclidean", "dot_product")

        Raises:
            ImportError: If numpy/D-gent VectorAgent not available
        """
        if not NUMPY_AVAILABLE:
            raise ImportError(
                "numpy required for DgentVectorBackend. Install with: pip install numpy"
            )

        self._dimension = dimension
        self._persistence_path = persistence_path

        # Map distance string to D-gent DistanceMetric
        distance_map = {
            "cosine": DistanceMetric.COSINE,
            "euclidean": DistanceMetric.EUCLIDEAN,
            "dot_product": DistanceMetric.DOT_PRODUCT,
        }
        d_metric = distance_map.get(distance, DistanceMetric.COSINE)

        # Create D-gent VectorAgent
        self._agent: VectorAgent[dict[str, Any]] = VectorAgent(
            dimension=dimension,
            distance=d_metric,
            persistence_path=persistence_path,
        )

        # Cache entries for reconstructing CatalogEntry from search
        self._entry_cache: dict[str, dict[str, Any]] = {}

    @property
    def dimension(self) -> int:
        """Dimension of vectors."""
        return self._dimension

    async def add(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Add or update entry.

        Args:
            id: Unique identifier
            vector: Embedding vector
            metadata: Entry metadata
        """
        vec = np.array(vector, dtype=np.float32)
        await self._agent.add(id, metadata, vec, metadata)
        self._entry_cache[id] = metadata

    async def add_batch(
        self,
        ids: list[str],
        vectors: list[list[float]],
        metadata: list[dict[str, Any]],
    ) -> None:
        """Add multiple entries efficiently.

        Args:
            ids: List of unique identifiers
            vectors: List of embedding vectors
            metadata: List of entry metadata
        """
        for entry_id, vec, meta in zip(ids, vectors, metadata):
            await self.add(entry_id, vec, meta)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
        threshold: Optional[float] = None,
    ) -> list[VectorSearchResult]:
        """Search for similar entries.

        Args:
            query_vector: Query embedding
            limit: Maximum number of results
            filters: Optional metadata filters
            threshold: Optional minimum similarity threshold

        Returns:
            List of results sorted by similarity (descending)
        """
        vec = np.array(query_vector, dtype=np.float32)

        # Use D-gent's neighbors method
        neighbors = await self._agent.neighbors(vec, k=limit * 2)

        results: list[VectorSearchResult] = []
        for entry, distance in neighbors:
            entry_id = entry.id
            metadata = self._entry_cache.get(entry_id, entry.metadata)

            # Apply filters
            if filters and not self._matches_filters(metadata, filters):
                continue

            # Convert distance to similarity (cosine distance: similarity = 1 - distance)
            similarity = 1.0 - distance

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            results.append(
                VectorSearchResult(
                    id=entry_id,
                    entry=None,  # type: ignore  # Will be filled by caller
                    distance=distance,
                    similarity=similarity,
                    metadata=metadata,
                )
            )

            if len(results) >= limit:
                break

        return results

    async def remove(self, id: str) -> None:
        """Remove entry by ID.

        Args:
            id: Entry identifier to remove
        """
        await self._agent.delete(id)
        self._entry_cache.pop(id, None)

    async def clear(self) -> None:
        """Remove all entries."""
        entries = await self._agent.load()
        for entry_id in list(entries.keys()):
            await self._agent.delete(entry_id)
        self._entry_cache.clear()

    async def count(self) -> int:
        """Get number of entries in backend."""
        entries = await self._agent.load()
        return len(entries)

    def _matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True

    # ========== D-gent Specific Features ==========

    async def curvature_at(self, vector: list[float], radius: float = 0.5) -> float:
        """Estimate semantic curvature at a point.

        High curvature indicates conceptual boundaries (useful for
        detecting semantic clusters or domain transitions).

        Args:
            vector: Point to measure curvature at
            radius: Search radius

        Returns:
            Curvature estimate (higher = sharper boundary)
        """
        vec = np.array(vector, dtype=np.float32)
        return float(await self._agent.curvature_at(vec, radius))

    async def find_void(
        self,
        vector: list[float],
        search_radius: float = 1.0,
        min_void_radius: float = 0.2,
    ) -> Optional[dict[str, Any]]:
        """Find unexplored regions (Ma) near a point.

        Voids are regions with high semantic potential but low coverage.
        Useful for discovering gaps in the catalog.

        Args:
            vector: Point to search from
            search_radius: How far to look
            min_void_radius: Minimum void size to report

        Returns:
            Void info with center, radius, and potential
        """
        try:
            vec = np.array(vector, dtype=np.float32)
            void = await self._agent.void_nearby(vec, search_radius, min_void_radius)
            if void:
                return {
                    "center": void.center.coordinates.tolist(),
                    "radius": void.radius,
                    "potential": void.potential,
                }
        except Exception:
            pass
        return None

    async def cluster_centers(self, k: int = 5) -> list[list[float]]:
        """Find cluster centers in the vector space.

        Useful for understanding catalog structure and identifying
        semantic groupings.

        Args:
            k: Number of clusters

        Returns:
            List of cluster center vectors
        """
        centers = await self._agent.cluster_centers(k)
        return [c.coordinates.tolist() for c in centers]


class VectorCatalog:
    """Unified Catalog + Vector DB using V-gent (or legacy D-gent) storage.

    Phase 9 Update: Now supports VgentProtocol injection for vector operations.

    This is the complete L-gent + V-gent integration:
    - Catalog metadata: D-gent PersistentAgent (via PersistentRegistry)
    - Vector embeddings: VgentProtocol (any V-gent backend)

    All operations keep both in sync automatically.

    Example (new - V-gent injection):
        from agents.v import create_vgent

        vgent = create_vgent(dimension=384)
        catalog = await VectorCatalog.create_with_vgent(
            embedder=SentenceTransformerEmbedder(),
            vgent=vgent,
        )

        # Register auto-indexes
        await catalog.register(entry)

        # Search uses V-gent vectors
        results = await catalog.search("process financial data")

    Example (legacy - auto-creates DgentVectorBackend):
        catalog = await VectorCatalog.create(
            embedder=SentenceTransformerEmbedder(),
            catalog_path=Path(".kgents/catalog.json"),
            vector_path=Path(".kgents/vectors.json")
        )

        # Sync check
        state = await catalog.sync_state()
    """

    def __init__(
        self,
        embedder: Embedder,
        catalog: Catalog,
        vector_backend: Union[DgentVectorBackend, "VgentProtocol"],
        *,
        _vgent: Optional["VgentProtocol"] = None,
    ):
        """Initialize unified catalog.

        Note: Use VectorCatalog.create() or VectorCatalog.create_with_vgent()
        factory methods instead.

        Args:
            embedder: Embedding implementation
            catalog: Catalog instance
            vector_backend: DgentVectorBackend (legacy) or VgentProtocol adapter
            _vgent: Direct VgentProtocol (used internally for Phase 9 integration)
        """
        self.embedder = embedder
        self.catalog = catalog
        self.vector_backend = vector_backend
        self._vgent = _vgent  # Direct V-gent reference for new methods
        self._fitted = False

    @classmethod
    async def create(
        cls,
        embedder: Embedder,
        catalog_path: Optional[Path] = None,
        vector_path: Optional[Path] = None,
        dimension: Optional[int] = None,
    ) -> "VectorCatalog":
        """Create a unified VectorCatalog (legacy D-gent backend).

        .. deprecated::
            Use create_with_vgent() for new code.

        Args:
            embedder: Embedding implementation
            catalog_path: Path for catalog persistence (optional)
            vector_path: Path for vector persistence (optional)
            dimension: Vector dimension (defaults to embedder.dimension)

        Returns:
            VectorCatalog instance
        """
        if dimension is None:
            dimension = embedder.dimension

        # Load or create catalog
        catalog = Catalog()
        if catalog_path and catalog_path.exists():
            import json

            with open(catalog_path, "r") as f:
                data = json.load(f)
                catalog = Catalog.from_dict(data)

        # Create D-gent vector backend
        vector_backend = DgentVectorBackend(
            dimension=dimension,
            persistence_path=vector_path,
        )

        instance = cls(embedder, catalog, vector_backend)

        # Index existing entries
        if catalog.entries:
            await instance._index_all()

        return instance

    @classmethod
    async def create_with_vgent(
        cls,
        embedder: Embedder,
        vgent: "VgentProtocol",
        catalog: Optional[Catalog] = None,
        catalog_path: Optional[Path] = None,
    ) -> "VectorCatalog":
        """Create a VectorCatalog using V-gent protocol (Phase 9).

        This is the recommended way to create a VectorCatalog for new code.
        It accepts any VgentProtocol implementation, giving you flexibility
        to use MemoryVectorBackend, DgentVectorBackend, or custom backends.

        Args:
            embedder: Embedding implementation
            vgent: V-gent protocol implementation (from agents.v)
            catalog: Optional pre-existing catalog
            catalog_path: Path for catalog persistence (optional)

        Returns:
            VectorCatalog instance

        Example:
            from agents.v import create_vgent, MemoryVectorBackend

            # Option 1: Use router (auto-selects best backend)
            vgent = create_vgent(dimension=384)

            # Option 2: Explicit memory backend
            vgent = MemoryVectorBackend(dimension=384)

            catalog = await VectorCatalog.create_with_vgent(
                embedder=SimpleEmbedder(dimension=384),
                vgent=vgent,
            )
        """
        if not VGENT_AVAILABLE:
            raise ImportError("V-gent not available. Install agents.v or use create() instead.")

        # Load or create catalog
        if catalog is None:
            catalog = Catalog()
            if catalog_path and catalog_path.exists():
                import json

                with open(catalog_path, "r") as f:
                    data = json.load(f)
                    catalog = Catalog.from_dict(data)

        # Create adapter to use V-gent with legacy vector_backend interface
        from .vgent_adapter import VgentToLgentAdapter

        adapter = VgentToLgentAdapter(vgent)

        instance = cls(embedder, catalog, adapter, _vgent=vgent)

        # Index existing entries
        if catalog.entries:
            await instance._index_all()

        return instance

    async def register(self, entry: CatalogEntry) -> str:
        """Register entry and index for vector search.

        Args:
            entry: Catalog entry to register

        Returns:
            Entry ID
        """
        # Add to catalog
        self.catalog.entries[entry.id] = entry

        # Index for vector search
        await self._index_entry(entry)

        return entry.id

    async def get(self, id: str) -> Optional[CatalogEntry]:
        """Get entry by ID.

        Args:
            id: Entry ID

        Returns:
            CatalogEntry if found, None otherwise
        """
        return self.catalog.entries.get(id)

    async def delete(self, id: str) -> bool:
        """Delete entry from catalog and vector index.

        Args:
            id: Entry ID to delete

        Returns:
            True if deleted, False if not found
        """
        if id not in self.catalog.entries:
            return False

        # Remove from catalog
        del self.catalog.entries[id]

        # Remove from vector index
        await self.vector_backend.remove(id)

        return True

    async def search(
        self,
        intent: str,
        entity_type: Optional[EntityType] = None,
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[SemanticResult]:
        """Search by semantic similarity.

        Args:
            intent: Natural language description
            entity_type: Optional entity type filter
            threshold: Minimum similarity score
            limit: Maximum number of results

        Returns:
            List of semantic results
        """
        # Embed query
        query_embedding = await self.embedder.embed(intent)

        # Build filters
        filters = {}
        if entity_type:
            filters["entity_type"] = entity_type.value

        # Search vectors
        vector_results = await self.vector_backend.search(
            query_vector=query_embedding,
            limit=limit,
            filters=filters,
            threshold=threshold,
        )

        # Convert to SemanticResult with full CatalogEntry
        results: list[SemanticResult] = []
        for vr in vector_results:
            entry = self.catalog.entries.get(vr.id)
            if entry:
                results.append(
                    SemanticResult(
                        id=vr.id,
                        entry=entry,
                        similarity=vr.similarity,
                        explanation=f"Semantic similarity: {vr.similarity:.2f}",
                    )
                )

        return results

    async def find_gaps(self, query: str, radius: float = 1.0) -> Optional[dict[str, Any]]:
        """Find gaps in catalog coverage near a query.

        Args:
            query: Natural language description
            radius: Search radius

        Returns:
            Gap info if found
        """
        query_embedding = await self.embedder.embed(query)
        return await self.vector_backend.find_void(query_embedding, radius)

    async def sync_state(self) -> VectorSyncState:
        """Check synchronization between catalog and vector index.

        Returns:
            Sync state with counts and issues
        """
        catalog_ids = set(self.catalog.entries.keys())
        vector_count = await self.vector_backend.count()

        # Find pending (in catalog but not indexed)
        # For now, assume all are indexed after _index_all
        pending: list[str] = []

        # Find orphaned (in vectors but not catalog)
        # Would need to enumerate vector IDs for full check
        orphaned: list[str] = []

        return VectorSyncState(
            total_entries=len(catalog_ids),
            indexed_entries=vector_count,
            pending_entries=pending,
            orphaned_vectors=orphaned,
        )

    async def cluster_analysis(self, k: int = 5) -> list[dict[str, Any]]:
        """Analyze catalog structure via clustering.

        Returns cluster centers with nearby entries.

        Args:
            k: Number of clusters

        Returns:
            List of cluster info dicts
        """
        centers = await self.vector_backend.cluster_centers(k)

        clusters: list[dict[str, Any]] = []
        for i, center in enumerate(centers):
            # Find entries near this center
            nearby = await self.vector_backend.search(center, limit=5)

            clusters.append(
                {
                    "id": f"cluster_{i}",
                    "center": center,
                    "entries": [r.id for r in nearby],
                    "entry_count": len(nearby),
                }
            )

        return clusters

    async def _index_entry(self, entry: CatalogEntry) -> None:
        """Index single entry for vector search."""
        text = self._make_searchable_text(entry)
        embedding = await self.embedder.embed(text)

        metadata = {
            "name": entry.name,
            "entity_type": entry.entity_type.value,
            "status": entry.status.value,
            "description": entry.description,
        }

        await self.vector_backend.add(entry.id, embedding, metadata)

    async def _index_all(self) -> None:
        """Index all catalog entries."""
        for entry in self.catalog.entries.values():
            await self._index_entry(entry)
        self._fitted = True

    def _make_searchable_text(self, entry: CatalogEntry) -> str:
        """Create searchable text from entry."""
        parts = [entry.name, entry.description]

        if entry.input_type:
            parts.append(f"input: {entry.input_type}")
        if entry.output_type:
            parts.append(f"output: {entry.output_type}")
        if entry.tongue_domain:
            parts.append(f"domain: {entry.tongue_domain}")

        return " ".join(parts)


# Convenience functions


def create_dgent_vector_backend(
    dimension: int = 384,
    persistence_path: Optional[Path] = None,
) -> VectorBackend:
    """Create a D-gent backed vector backend.

    This is the recommended way to create a VectorBackend when you want
    to use D-gent's vector storage primitives.

    Args:
        dimension: Vector dimension
        persistence_path: Optional path for persistence

    Returns:
        DgentVectorBackend instance
    """
    return DgentVectorBackend(
        dimension=dimension,
        persistence_path=persistence_path,
    )


async def create_vector_catalog(
    embedder: Embedder,
    base_path: Path = Path(".kgents"),
) -> VectorCatalog:
    """Create a VectorCatalog with default paths.

    Args:
        embedder: Embedding implementation
        base_path: Base directory for persistence

    Returns:
        VectorCatalog instance
    """
    base_path.mkdir(parents=True, exist_ok=True)

    return await VectorCatalog.create(
        embedder=embedder,
        catalog_path=base_path / "catalog.json",
        vector_path=base_path / "vectors.json",
    )


# Migration utilities


async def migrate_to_dgent_backend(
    entries: dict[str, CatalogEntry],
    embedder: Embedder,
    persistence_path: Optional[Path] = None,
) -> DgentVectorBackend:
    """Migrate existing entries to a D-gent vector backend.

    Useful for transitioning from in-memory or other backends.

    Args:
        entries: Existing catalog entries
        embedder: Embedder for creating vectors
        persistence_path: Path for persistence

    Returns:
        DgentVectorBackend with all entries indexed
    """
    backend = DgentVectorBackend(
        dimension=embedder.dimension,
        persistence_path=persistence_path,
    )

    for entry in entries.values():
        text = " ".join([entry.name, entry.description])
        embedding = await embedder.embed(text)

        metadata = {
            "name": entry.name,
            "entity_type": entry.entity_type.value,
            "status": entry.status.value,
        }

        await backend.add(entry.id, embedding, metadata)

    return backend
