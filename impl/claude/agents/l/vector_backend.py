"""
L-gent Vector Database Backends: Scalable semantic search for large catalogs.

This module provides vector database backends for catalogs with >1000 entries:
- ChromaDBBackend: Persistent vector DB with SQL + vectors
- FAISSBackend: High-performance in-memory vector index
- VectorBackend protocol: Pluggable interface for custom backends

Phase 6 Goals:
- Handle large catalogs (10K+ entries) efficiently
- Persistent vector indices (survives restarts)
- Advanced filtering (metadata + vector similarity)
- Optional dependencies: Graceful degradation if DB not available

Architecture:
- VectorBackend: Protocol defining the interface
- SemanticBrain uses VectorBackend for storage/retrieval
- Backends are swappable at runtime
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol

from .types import CatalogEntry


@dataclass
class VectorSearchResult:
    """Result from vector database search."""

    id: str
    entry: CatalogEntry
    distance: float  # Lower is more similar
    similarity: float  # Cosine similarity (0.0 to 1.0)
    metadata: dict[str, Any]  # Backend-specific metadata


class VectorBackend(Protocol):
    """Protocol for vector database backends.

    Implementations must support:
    - Adding/removing entries with vectors
    - Similarity search with metadata filtering
    - Persistence (save/load state)
    """

    @property
    def dimension(self) -> int:
        """Dimension of vectors in this backend."""
        ...

    async def add(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Add or update entry.

        Args:
            id: Unique identifier
            vector: Embedding vector
            metadata: Entry metadata (description, type, etc.)
        """
        ...

    async def add_batch(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, Any]]
    ) -> None:
        """Add multiple entries efficiently.

        Args:
            ids: List of unique identifiers
            vectors: List of embedding vectors
            metadata: List of entry metadata
        """
        ...

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
        ...

    async def remove(self, id: str) -> None:
        """Remove entry by ID.

        Args:
            id: Entry identifier to remove
        """
        ...

    async def clear(self) -> None:
        """Remove all entries."""
        ...

    async def count(self) -> int:
        """Get number of entries in backend."""
        ...


# Sentinel for optional imports
CHROMADB_AVAILABLE = False
FAISS_AVAILABLE = False

try:
    import chromadb  # type: ignore
    from chromadb.config import Settings  # type: ignore

    CHROMADB_AVAILABLE = True
except ImportError:
    pass

try:
    import faiss  # type: ignore
    import numpy as np  # type: ignore

    FAISS_AVAILABLE = True
except ImportError:
    pass


class ChromaDBBackend:
    """Vector backend using ChromaDB.

    ChromaDB provides:
    - Persistent storage (SQLite + vectors on disk)
    - Metadata filtering
    - Automatic indexing
    - No separate server needed

    Requires: pip install chromadb

    Example:
        backend = ChromaDBBackend(path=".kgents/chroma")
        await backend.add("agent_1", embedding, {"type": "agent"})
        results = await backend.search(query_embedding, limit=10)
    """

    def __init__(
        self,
        path: str = ".kgents/chroma",
        collection_name: str = "l_gent_catalog",
        dimension: int = 384,
    ):
        """Initialize ChromaDB backend.

        Args:
            path: Directory for persistent storage
            collection_name: Name of the collection
            dimension: Dimension of vectors (must match embedder)

        Raises:
            ImportError: If chromadb not installed
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb not installed. Install with: pip install chromadb"
            )

        self._dimension = dimension
        self._path = path
        self._collection_name = collection_name

        # Initialize ChromaDB client
        self._client = chromadb.PersistentClient(
            path=path, settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"dimension": dimension},
        )

    @property
    def dimension(self) -> int:
        """Dimension of vectors."""
        return self._dimension

    async def add(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Add entry to ChromaDB.

        Args:
            id: Entry ID
            vector: Embedding vector
            metadata: Entry metadata
        """
        # ChromaDB requires all metadata values to be strings, ints, floats, or bools
        # Convert complex types to strings
        clean_metadata = self._clean_metadata(metadata)

        self._collection.upsert(
            ids=[id], embeddings=[vector], metadatas=[clean_metadata]
        )

    async def add_batch(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, Any]]
    ) -> None:
        """Add multiple entries to ChromaDB.

        Args:
            ids: Entry IDs
            vectors: Embedding vectors
            metadata: Entry metadata
        """
        clean_metadata = [self._clean_metadata(m) for m in metadata]
        self._collection.upsert(ids=ids, embeddings=vectors, metadatas=clean_metadata)

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
        threshold: Optional[float] = None,
    ) -> list[VectorSearchResult]:
        """Search ChromaDB for similar entries.

        Args:
            query_vector: Query embedding
            limit: Maximum results
            filters: Metadata filters ({"entity_type": "agent"})
            threshold: Minimum similarity (0.0 to 1.0)

        Returns:
            List of search results
        """
        # Build where clause for filters
        where = None
        if filters:
            where = self._build_where_clause(filters)

        # Query ChromaDB
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=limit,
            where=where,
        )

        # Convert to VectorSearchResult
        search_results = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                entry_id = results["ids"][0][i]
                distance = results["distances"][0][i]
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}

                # Convert distance to similarity (ChromaDB uses L2 distance)
                # For normalized vectors: similarity ≈ 1 - (distance²/4)
                similarity = max(0.0, 1.0 - (distance * distance / 4.0))

                # Apply threshold
                if threshold is not None and similarity < threshold:
                    continue

                # We don't have the full CatalogEntry here, just metadata
                # In practice, SemanticBrain will reconstruct from its own registry
                search_results.append(
                    VectorSearchResult(
                        id=entry_id,
                        entry=None,  # type: ignore  # Will be filled by caller
                        distance=distance,
                        similarity=similarity,
                        metadata=metadata,
                    )
                )

        return search_results

    async def remove(self, id: str) -> None:
        """Remove entry from ChromaDB.

        Args:
            id: Entry ID to remove
        """
        try:
            self._collection.delete(ids=[id])
        except Exception:
            # Entry doesn't exist, that's fine
            pass

    async def clear(self) -> None:
        """Remove all entries from ChromaDB."""
        # Delete and recreate collection
        self._client.delete_collection(name=self._collection_name)
        self._collection = self._client.create_collection(
            name=self._collection_name, metadata={"dimension": self._dimension}
        )

    async def count(self) -> int:
        """Get number of entries in ChromaDB."""
        return self._collection.count()

    def _clean_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Clean metadata for ChromaDB (only primitives allowed)."""
        clean = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                clean[key] = value
            elif value is None:
                clean[key] = ""
            else:
                # Convert complex types to string
                clean[key] = str(value)
        return clean

    def _build_where_clause(self, filters: dict[str, Any]) -> dict[str, Any]:
        """Build ChromaDB where clause from filters.

        Args:
            filters: Filter dictionary

        Returns:
            ChromaDB where clause
        """
        # Simple equality filters
        where = {}
        for key, value in filters.items():
            where[key] = {"$eq": value}
        return where


class FAISSBackend:
    """Vector backend using FAISS (Facebook AI Similarity Search).

    FAISS provides:
    - Extremely fast similarity search
    - Multiple index types (flat, IVF, HNSW)
    - GPU support
    - Memory-efficient

    Trade-offs:
    - In-memory only (requires manual save/load)
    - No metadata filtering (must filter results after search)

    Requires: pip install faiss-cpu (or faiss-gpu for GPU support)

    Example:
        backend = FAISSBackend(dimension=384, index_type="flat")
        await backend.add("agent_1", embedding, {"type": "agent"})
        results = await backend.search(query_embedding, limit=10)
    """

    def __init__(
        self,
        dimension: int = 384,
        index_type: str = "flat",
        save_path: Optional[str] = None,
    ):
        """Initialize FAISS backend.

        Args:
            dimension: Vector dimension
            index_type: Index type ("flat", "ivf", "hnsw")
            save_path: Optional path to save/load index

        Raises:
            ImportError: If faiss not installed
        """
        if not FAISS_AVAILABLE:
            raise ImportError(
                "faiss not installed. Install with: pip install faiss-cpu"
            )

        self._dimension = dimension
        self._index_type = index_type
        self._save_path = save_path

        # Create index
        if index_type == "flat":
            # Flat index: exhaustive search, most accurate
            self._index = faiss.IndexFlatIP(dimension)  # Inner product (for cosine)
        elif index_type == "ivf":
            # IVF index: partitions space, faster for large datasets
            quantizer = faiss.IndexFlatIP(dimension)
            self._index = faiss.IndexIVFFlat(quantizer, dimension, 100)  # 100 clusters
            # Requires training before use
            self._index.nprobe = 10  # Search 10 clusters
        elif index_type == "hnsw":
            # HNSW index: graph-based, very fast
            self._index = faiss.IndexHNSWFlat(dimension, 32)  # 32 links per node
        else:
            raise ValueError(f"Unknown index type: {index_type}")

        # Metadata storage (FAISS doesn't store metadata)
        self._id_to_idx: dict[str, int] = {}
        self._idx_to_id: dict[int, str] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._next_idx = 0

        # Load from disk if path provided
        if save_path:
            self._load()

    @property
    def dimension(self) -> int:
        """Dimension of vectors."""
        return self._dimension

    async def add(self, id: str, vector: list[float], metadata: dict[str, Any]) -> None:
        """Add entry to FAISS index.

        Args:
            id: Entry ID
            vector: Embedding vector
            metadata: Entry metadata
        """
        # Convert to numpy
        vec = np.array([vector], dtype=np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(vec)

        # Add to index
        if id in self._id_to_idx:
            # Update existing
            idx = self._id_to_idx[id]
            # FAISS doesn't support updates, would need to rebuild
            # For now, just update metadata
            self._metadata[id] = metadata
        else:
            # Add new
            idx = self._next_idx
            self._index.add(vec)
            self._id_to_idx[id] = idx
            self._idx_to_id[idx] = id
            self._metadata[id] = metadata
            self._next_idx += 1

        # Save if path configured
        if self._save_path:
            self._save()

    async def add_batch(
        self, ids: list[str], vectors: list[list[float]], metadata: list[dict[str, Any]]
    ) -> None:
        """Add multiple entries to FAISS index.

        Args:
            ids: Entry IDs
            vectors: Embedding vectors
            metadata: Entry metadata
        """
        # Convert to numpy
        vecs = np.array(vectors, dtype=np.float32)

        # Normalize for cosine similarity
        faiss.normalize_L2(vecs)

        # Add to index
        self._index.add(vecs)

        # Update mappings
        for i, (entry_id, meta) in enumerate(zip(ids, metadata)):
            idx = self._next_idx + i
            self._id_to_idx[entry_id] = idx
            self._idx_to_id[idx] = entry_id
            self._metadata[entry_id] = meta

        self._next_idx += len(ids)

        # Save if path configured
        if self._save_path:
            self._save()

    async def search(
        self,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
        threshold: Optional[float] = None,
    ) -> list[VectorSearchResult]:
        """Search FAISS index for similar entries.

        Args:
            query_vector: Query embedding
            limit: Maximum results
            filters: Metadata filters (applied after search)
            threshold: Minimum similarity (0.0 to 1.0)

        Returns:
            List of search results
        """
        # Convert to numpy and normalize
        vec = np.array([query_vector], dtype=np.float32)
        faiss.normalize_L2(vec)

        # Search (returns distances and indices)
        # For normalized vectors with IndexFlatIP, distance = cosine similarity
        distances, indices = self._index.search(
            vec, limit * 2
        )  # Search more for filtering

        # Convert to results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:  # No more results
                break

            entry_id = self._idx_to_id.get(idx)
            if not entry_id:
                continue

            metadata = self._metadata.get(entry_id, {})

            # Apply metadata filters
            if filters and not self._matches_filters(metadata, filters):
                continue

            # Distance is already cosine similarity for normalized vectors
            similarity = float(distance)

            # Apply threshold
            if threshold is not None and similarity < threshold:
                continue

            results.append(
                VectorSearchResult(
                    id=entry_id,
                    entry=None,  # type: ignore  # Will be filled by caller
                    distance=1.0 - similarity,  # Convert to distance
                    similarity=similarity,
                    metadata=metadata,
                )
            )

            if len(results) >= limit:
                break

        return results

    async def remove(self, id: str) -> None:
        """Remove entry from FAISS index.

        Note: FAISS doesn't support deletion efficiently.
        This removes from metadata but vector remains in index.

        Args:
            id: Entry ID to remove
        """
        if id in self._id_to_idx:
            idx = self._id_to_idx[id]
            del self._id_to_idx[id]
            del self._idx_to_id[idx]
            del self._metadata[id]

        # Save if path configured
        if self._save_path:
            self._save()

    async def clear(self) -> None:
        """Remove all entries from FAISS index."""
        # Reset index
        self._index.reset()
        self._id_to_idx.clear()
        self._idx_to_id.clear()
        self._metadata.clear()
        self._next_idx = 0

        # Save if path configured
        if self._save_path:
            self._save()

    async def count(self) -> int:
        """Get number of entries in FAISS index."""
        return self._index.ntotal

    def _matches_filters(
        self, metadata: dict[str, Any], filters: dict[str, Any]
    ) -> bool:
        """Check if metadata matches filters."""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True

    def _save(self) -> None:
        """Save FAISS index and metadata to disk."""
        if not self._save_path:
            return

        import json
        import os

        # Create directory
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)

        # Save index
        faiss.write_index(self._index, self._save_path)

        # Save metadata
        meta_path = self._save_path + ".meta.json"
        with open(meta_path, "w") as f:
            json.dump(
                {
                    "id_to_idx": self._id_to_idx,
                    "idx_to_id": {int(k): v for k, v in self._idx_to_id.items()},
                    "metadata": self._metadata,
                    "next_idx": self._next_idx,
                },
                f,
            )

    def _load(self) -> None:
        """Load FAISS index and metadata from disk."""
        if not self._save_path:
            return

        import json
        import os

        if not os.path.exists(self._save_path):
            return

        # Load index
        self._index = faiss.read_index(self._save_path)

        # Load metadata
        meta_path = self._save_path + ".meta.json"
        if os.path.exists(meta_path):
            with open(meta_path, "r") as f:
                data = json.load(f)
                self._id_to_idx = data["id_to_idx"]
                self._idx_to_id = {int(k): v for k, v in data["idx_to_id"].items()}
                self._metadata = data["metadata"]
                self._next_idx = data["next_idx"]


# Convenience function


def create_vector_backend(
    dimension: int = 384,
    backend_type: str = "auto",
    path: Optional[str] = None,
) -> VectorBackend:
    """Create a vector backend based on available dependencies.

    Args:
        dimension: Vector dimension
        backend_type: Backend type ("auto", "chroma", "faiss")
        path: Optional path for persistence

    Returns:
        Vector backend instance
    """
    if backend_type == "auto":
        # Prefer ChromaDB for persistence, FAISS for speed
        if CHROMADB_AVAILABLE:
            backend_type = "chroma"
        elif FAISS_AVAILABLE:
            backend_type = "faiss"
        else:
            raise ImportError(
                "No vector backend available. "
                "Install chromadb or faiss: pip install chromadb faiss-cpu"
            )

    if backend_type == "chroma":
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb not installed. Install with: pip install chromadb"
            )
        return ChromaDBBackend(path=path or ".kgents/chroma", dimension=dimension)
    elif backend_type == "faiss":
        if not FAISS_AVAILABLE:
            raise ImportError(
                "faiss not installed. Install with: pip install faiss-cpu"
            )
        return FAISSBackend(dimension=dimension, save_path=path)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
