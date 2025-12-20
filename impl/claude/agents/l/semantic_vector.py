"""
L-gent Semantic Search with VectorBackend: Scalable semantic search for large catalogs.

This module enhances SemanticBrain with optional VectorBackend support for
catalogs with >1000 entries. Instead of in-memory embeddings, it uses
persistent vector databases (ChromaDB, FAISS) for efficient search.

Phase 7 Enhancement:
- VectorSemanticBrain: SemanticBrain backed by VectorBackend
- Automatic backend selection based on catalog size
- Transparent fallback to in-memory for small catalogs
- D-gent CatalogEntry metadata synchronization

Design Philosophy:
- Graceful scaling: Small catalogs use in-memory, large ones use vector DBs
- Transparent: Same interface regardless of backend
- Persistent: Vector indices survive restarts
- Composable: Works with existing SemanticRegistry
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .semantic import Embedder, SemanticResult
from .types import CatalogEntry, Status
from .vector_backend import VectorBackend, create_vector_backend

if TYPE_CHECKING:
    from .semantic import SemanticBrain


class VectorSemanticBrain:
    """Semantic search backed by a vector database.

    This is an enhanced version of SemanticBrain that uses VectorBackend
    for storage instead of in-memory dictionaries. Benefits:
    - Handles large catalogs (10K+ entries) efficiently
    - Persistent indices (survives restarts)
    - Advanced filtering via metadata
    - Fast approximate nearest neighbor search

    Example:
        # Automatic backend selection
        brain = await create_vector_semantic_brain(
            embedder=SentenceTransformerEmbedder(),
            backend_type="auto"  # Chooses ChromaDB if available
        )

        # Add entries
        await brain.add_entry(entry)

        # Search
        results = await brain.search("process financial documents")
    """

    def __init__(self, embedder: Embedder, backend: VectorBackend):
        """Initialize vector-backed semantic search.

        Args:
            embedder: Embedding implementation
            backend: Vector database backend
        """
        self.embedder = embedder
        self.backend = backend

    async def add_entry(self, entry: CatalogEntry) -> None:
        """Add or update entry in vector index.

        Args:
            entry: Catalog entry to index
        """
        # Create searchable text
        text = self._make_searchable_text(entry)

        # Embed
        embedding = await self.embedder.embed(text)

        # Store in backend with metadata
        metadata = {
            "name": entry.name,
            "entity_type": entry.entity_type.value,
            "status": entry.status.value,
            "description": entry.description,
        }

        await self.backend.add(entry.id, embedding, metadata)

    async def add_batch(self, entries: list[CatalogEntry]) -> None:
        """Add multiple entries efficiently.

        Args:
            entries: List of catalog entries to index
        """
        # Create searchable texts
        texts = [self._make_searchable_text(e) for e in entries]

        # Embed all
        embeddings = [await self.embedder.embed(text) for text in texts]

        # Create metadata
        metadata_list = [
            {
                "name": e.name,
                "entity_type": e.entity_type.value,
                "status": e.status.value,
                "description": e.description,
            }
            for e in entries
        ]

        # Batch add
        ids = [e.id for e in entries]
        await self.backend.add_batch(ids, embeddings, metadata_list)

    async def search(
        self,
        intent: str,
        filters: Optional[dict[str, Any]] = None,
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[SemanticResult]:
        """Search for entries by semantic similarity.

        Args:
            intent: Natural language description of what user wants
            filters: Optional filters (entity_type, status, etc.)
            threshold: Minimum similarity score (0.0 to 1.0)
            limit: Maximum number of results

        Returns:
            List of semantic results, ranked by similarity
        """
        # Embed query
        query_embedding = await self.embedder.embed(intent)

        # Search vector backend
        backend_results = await self.backend.search(
            query_vector=query_embedding,
            limit=limit,
            filters=filters,
            threshold=threshold,
        )

        # Convert to SemanticResult
        # Note: VectorBackend returns results without full CatalogEntry
        # In production, we'd fetch entries from registry here
        results = []
        for backend_result in backend_results:
            # Create minimal entry from metadata
            # In real usage, this would fetch from registry
            entry = self._entry_from_metadata(backend_result.id, backend_result.metadata)

            results.append(
                SemanticResult(
                    id=backend_result.id,
                    entry=entry,
                    similarity=backend_result.similarity,
                    explanation=f"Semantic similarity: {backend_result.similarity:.2f}",
                )
            )

        return results

    async def remove_entry(self, entry_id: str) -> None:
        """Remove entry from vector index.

        Args:
            entry_id: ID of entry to remove
        """
        await self.backend.remove(entry_id)

    async def clear(self) -> None:
        """Remove all entries from vector index."""
        await self.backend.clear()

    async def count(self) -> int:
        """Get number of entries in vector index."""
        return await self.backend.count()

    def _make_searchable_text(self, entry: CatalogEntry) -> str:
        """Create searchable text from entry metadata."""
        parts = [entry.name, entry.description]

        # Add type information
        if entry.input_type:
            parts.append(f"input: {entry.input_type}")
        if entry.output_type:
            parts.append(f"output: {entry.output_type}")

        # Add domain information (for tongues)
        if entry.tongue_domain:
            parts.append(f"domain: {entry.tongue_domain}")

        return " ".join(parts)

    def _entry_from_metadata(self, entry_id: str, metadata: dict[str, Any]) -> CatalogEntry:
        """Create minimal CatalogEntry from backend metadata.

        In production, this should fetch the full entry from the registry.
        This is a fallback for when we only have vector backend data.
        """
        from datetime import datetime

        from .types import EntityType

        return CatalogEntry(
            id=entry_id,
            entity_type=EntityType(metadata.get("entity_type", "agent")),
            name=metadata.get("name", entry_id),
            description=metadata.get("description", ""),
            version="unknown",
            author="unknown",
            created_at=datetime.now(),
            status=Status(metadata.get("status", "active")),
        )


# Convenience functions


async def create_vector_semantic_brain(
    embedder: Embedder,
    backend_type: str = "auto",
    backend_path: Optional[str] = None,
    dimension: Optional[int] = None,
) -> VectorSemanticBrain:
    """Create a vector-backed semantic brain.

    Args:
        embedder: Embedding implementation
        backend_type: Backend type ("auto", "chroma", "faiss")
        backend_path: Optional path for persistent storage
        dimension: Vector dimension (defaults to embedder.dimension)

    Returns:
        VectorSemanticBrain instance
    """
    if dimension is None:
        dimension = embedder.dimension

    # Create backend
    backend = create_vector_backend(
        dimension=dimension, backend_type=backend_type, path=backend_path
    )

    return VectorSemanticBrain(embedder, backend)


async def create_best_semantic_brain(
    embedder: Embedder, catalog_size: int = 0
) -> "SemanticBrain | VectorSemanticBrain":
    """Create the best semantic brain for catalog size.

    Small catalogs (<1000 entries): In-memory SemanticBrain
    Large catalogs (>=1000 entries): VectorSemanticBrain with vector DB

    Args:
        embedder: Embedding implementation
        catalog_size: Expected catalog size

    Returns:
        SemanticBrain or VectorSemanticBrain
    """
    from .semantic import SemanticBrain
    from .vector_backend import CHROMADB_AVAILABLE, FAISS_AVAILABLE

    # Use in-memory for small catalogs
    if catalog_size < 1000:
        return SemanticBrain(embedder)

    # Use vector backend for large catalogs (if available)
    if CHROMADB_AVAILABLE or FAISS_AVAILABLE:
        return await create_vector_semantic_brain(embedder, backend_type="auto")

    # Fallback to in-memory
    return SemanticBrain(embedder)
