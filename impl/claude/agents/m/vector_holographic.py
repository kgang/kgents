"""
VectorHolographicMemory: L-gent Integration for M-gent (Phase 4).

This module integrates M-gent's holographic memory with L-gent's vector
infrastructure, providing high-quality semantic embeddings for memory
operations.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │              VectorHolographicMemory                         │
    │    (Holographic operations + vector similarity search)       │
    ├─────────────────────────────────────────────────────────────┤
    │   L-gent DgentVectorBackend      L-gent Embedder             │
    │   (D-gent VectorAgent)           (semantic vectors)          │
    └─────────────────────────────────────────────────────────────┘

Key Features:
- Vector similarity = holographic resonance
- Semantic compression via curvature analysis
- Void detection for memory gaps
- Cluster analysis for memory structure
- Integration with L-gent VectorCatalog

Integration Points:
- DgentVectorBackend (impl/claude/agents/l/vector_db.py)
- Embedder protocol (impl/claude/agents/l/semantic.py)
- D-gent VectorAgent (impl/claude/agents/d/vector.py)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, TypeVar

from .holographic import (
    HolographicMemory,
    MemoryPattern,
    ResonanceResult,
)

# Import L-gent components
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

T = TypeVar("T")


@dataclass
class VectorMemoryConfig:
    """Configuration for VectorHolographicMemory."""

    # Embedding settings
    dimension: int = 384
    normalize_embeddings: bool = True

    # Search settings
    default_limit: int = 10
    similarity_threshold: float = 0.3

    # Storage settings
    persistence_path: Optional[Path] = None
    namespace: str = "holographic"

    # Compression settings
    enable_curvature_compression: bool = True
    compression_threshold: float = 0.2  # Low curvature = compressible


@dataclass
class VoidInfo:
    """Information about a semantic void (memory gap)."""

    center: list[float]  # Embedding coordinates
    radius: float  # Size of the void
    potential: float  # Semantic potential (how "important" the gap might be)
    nearest_memories: list[str] = field(default_factory=list)  # IDs of nearest patterns


@dataclass
class ClusterInfo:
    """Information about a memory cluster."""

    id: str
    center: list[float]
    member_ids: list[str]
    size: int
    avg_similarity: float = 0.0
    dominant_concepts: list[str] = field(default_factory=list)


class VectorHolographicMemory(HolographicMemory[T]):
    """Holographic memory backed by L-gent vector search.

    This is the M-gent + L-gent integration point. Vector similarity
    search provides the "resonance" mechanism for holographic retrieval.

    Benefits over base HolographicMemory:
    - High-quality semantic embeddings (sentence-transformers, OpenAI)
    - Efficient similarity search via D-gent VectorAgent
    - Semantic features: curvature, voids, geodesics
    - Scalable to large memory stores (vector DB backends)

    Example:
        from agents.l.embedders import SentenceTransformerEmbedder
        from agents.l.vector_db import DgentVectorBackend

        embedder = SentenceTransformerEmbedder()
        backend = DgentVectorBackend(dimension=384)

        memory = VectorHolographicMemory(
            embedder=embedder,
            vector_backend=backend,
        )

        await memory.store("m1", "User prefers dark mode", ["preference"])
        results = await memory.retrieve("What are user preferences?")
    """

    def __init__(
        self,
        embedder: Any,  # L-gent Embedder
        vector_backend: Any,  # DgentVectorBackend
        config: Optional[VectorMemoryConfig] = None,
    ):
        """Initialize vector-backed holographic memory.

        Args:
            embedder: L-gent embedder for semantic vectors
            vector_backend: DgentVectorBackend for vector storage
            config: Configuration options
        """
        self._embedder = embedder
        self._vector_backend = vector_backend
        self._config = config or VectorMemoryConfig()

        # Initialize base holographic memory
        super().__init__(
            embedder=embedder,
            storage=None,  # We use vector_backend instead
        )

        # Pending updates for sync
        self._pending_updates: set[str] = set()

    async def store(
        self,
        id: str,
        content: T,
        concepts: list[str] | None = None,
        embedding: list[float] | None = None,
    ) -> MemoryPattern[T]:
        """Store memory with vector indexing.

        Extends base store to add vector backend indexing.

        Args:
            id: Unique identifier
            content: Memory content
            concepts: Semantic tags
            embedding: Pre-computed embedding (computed if not provided)

        Returns:
            Created MemoryPattern
        """
        # Compute embedding if not provided
        if embedding is None:
            embedding = await self._embedder.embed(str(content))

        # Store in base holographic memory
        pattern = await super().store(id, content, concepts, embedding)

        # Index in vector backend
        metadata = {
            "concepts": concepts or [],
            "timestamp": pattern.timestamp.isoformat(),
            "compression": pattern.compression.name,
        }
        await self._vector_backend.add(id, embedding, metadata)

        return pattern

    async def retrieve(
        self,
        query: str | list[float],
        limit: int | None = None,
        threshold: float | None = None,
    ) -> list[ResonanceResult[T]]:
        """Retrieve by vector resonance.

        Uses vector backend for efficient similarity search,
        then wraps results in ResonanceResult format.

        Args:
            query: Text query or pre-computed embedding
            limit: Maximum results (uses config default if None)
            threshold: Minimum similarity (uses config default if None)

        Returns:
            List of ResonanceResult sorted by effective score
        """
        limit = limit or self._config.default_limit
        threshold = threshold or self._config.similarity_threshold

        # Get query embedding
        if isinstance(query, str):
            query_embedding = await self._embedder.embed(query)
        else:
            query_embedding = query

        # Search via vector backend
        vector_results = await self._vector_backend.search(
            query_vector=query_embedding,
            limit=limit,
            threshold=threshold,
        )

        # Convert to ResonanceResult with full pattern info
        results: list[ResonanceResult[T]] = []
        for vr in vector_results:
            pattern = self._patterns.get(vr.id)
            if pattern:
                # Record access
                pattern.access()

                # Resolution based on compression
                resolution = self._compression_to_resolution(pattern.compression)

                results.append(
                    ResonanceResult(
                        pattern=pattern,
                        similarity=vr.similarity,
                        resolution=resolution,
                    )
                )

        self._retrieve_count += 1
        return results

    async def delete(self, pattern_id: str) -> bool:
        """Delete a pattern from memory and vector index.

        Args:
            pattern_id: Pattern ID to delete

        Returns:
            True if deleted, False if not found
        """
        if pattern_id not in self._patterns:
            return False

        del self._patterns[pattern_id]
        await self._vector_backend.remove(pattern_id)
        self._pending_updates.discard(pattern_id)

        return True

    # ========== L-gent Specific Features ==========

    async def find_void(
        self,
        query: str | list[float],
        radius: float = 1.0,
        min_void_radius: float = 0.2,
    ) -> Optional[VoidInfo]:
        """Find semantic voids (memory gaps) near a query.

        Voids are regions in embedding space with no memories.
        These represent potential areas for new learning.

        Args:
            query: Query to search around
            radius: Search radius
            min_void_radius: Minimum void size to report

        Returns:
            VoidInfo if a void is found, None otherwise
        """
        # Get query embedding
        if isinstance(query, str):
            query_embedding = await self._embedder.embed(query)
        else:
            query_embedding = query

        # Use vector backend's void detection
        void_data = await self._vector_backend.find_void(
            query_embedding, radius, min_void_radius
        )

        if void_data is None:
            return None

        # Find nearest memories to the void
        nearest = await self._vector_backend.search(
            query_vector=void_data["center"],
            limit=5,
        )

        return VoidInfo(
            center=void_data["center"],
            radius=void_data["radius"],
            potential=void_data["potential"],
            nearest_memories=[r.id for r in nearest],
        )

    async def curvature_at(
        self, query: str | list[float], radius: float = 0.5
    ) -> float:
        """Estimate semantic curvature at a point.

        High curvature indicates conceptual boundaries (useful for
        detecting semantic clusters or domain transitions).

        Args:
            query: Point to measure curvature
            radius: Search radius

        Returns:
            Curvature estimate (higher = sharper boundary)
        """
        if isinstance(query, str):
            query_embedding = await self._embedder.embed(query)
        else:
            query_embedding = query

        return await self._vector_backend.curvature_at(query_embedding, radius)

    async def cluster_analysis(self, k: int = 5) -> list[ClusterInfo]:
        """Analyze memory structure via clustering.

        Returns cluster centers with member information,
        useful for understanding memory organization.

        Args:
            k: Number of clusters

        Returns:
            List of ClusterInfo describing memory clusters
        """
        centers = await self._vector_backend.cluster_centers(k)

        clusters = []
        for i, center in enumerate(centers):
            # Find members near this center
            members = await self._vector_backend.search(center, limit=20)
            member_ids = [r.id for r in members]

            # Get dominant concepts from members
            concept_counts: dict[str, int] = {}
            for mid in member_ids:
                pattern = self._patterns.get(mid)
                if pattern:
                    for concept in pattern.concepts:
                        concept_counts[concept] = concept_counts.get(concept, 0) + 1

            dominant = sorted(concept_counts.items(), key=lambda x: -x[1])[:5]

            # Calculate average similarity
            avg_sim = sum(r.similarity for r in members) / max(len(members), 1)

            clusters.append(
                ClusterInfo(
                    id=f"cluster_{i}",
                    center=center,
                    member_ids=member_ids,
                    size=len(member_ids),
                    avg_similarity=avg_sim,
                    dominant_concepts=[c for c, _ in dominant],
                )
            )

        return clusters

    async def compress_by_curvature(self) -> dict[str, Any]:
        """Compress memories in low-curvature regions.

        Low curvature = flat semantic space = can be compressed
        more aggressively without losing important distinctions.

        Returns:
            Compression statistics
        """
        if not self._config.enable_curvature_compression:
            return {"enabled": False}

        compressed_count = 0
        for pattern in self._patterns.values():
            try:
                curvature = await self.curvature_at(pattern.embedding)
                if curvature < self._config.compression_threshold:
                    # Low curvature: safe to compress
                    await self.demote(pattern.id)
                    compressed_count += 1
            except Exception:
                # Vector backend might not support curvature
                pass

        return {
            "enabled": True,
            "compressed": compressed_count,
            "threshold": self._config.compression_threshold,
        }

    async def sync_to_backend(self) -> int:
        """Sync pending pattern updates to vector backend.

        Returns:
            Number of patterns synced
        """
        synced = 0
        for pattern_id in list(self._pending_updates):
            pattern = self._patterns.get(pattern_id)
            if pattern:
                metadata = {
                    "concepts": pattern.concepts,
                    "timestamp": pattern.timestamp.isoformat(),
                    "compression": pattern.compression.name,
                    "strength": pattern.strength,
                }
                await self._vector_backend.add(pattern_id, pattern.embedding, metadata)
                synced += 1

        self._pending_updates.clear()
        return synced

    async def demote(self, pattern_id: str, levels: int = 1) -> None:
        """Demote with pending update tracking."""
        await super().demote(pattern_id, levels)
        self._pending_updates.add(pattern_id)

    async def promote(self, pattern_id: str, levels: int = 1) -> None:
        """Promote with pending update tracking."""
        await super().promote(pattern_id, levels)
        self._pending_updates.add(pattern_id)

    def stats(self) -> dict[str, Any]:
        """Get memory statistics including vector backend info."""
        base_stats = super().stats()
        base_stats["vector_backend"] = {
            "dimension": self._config.dimension,
            "namespace": self._config.namespace,
            "pending_updates": len(self._pending_updates),
        }
        return base_stats


# ========== Factory Functions ==========


async def create_vector_holographic_memory(
    embedder: Any,
    persistence_path: Optional[Path] = None,
    namespace: str = "holographic",
    **config_kwargs,
) -> VectorHolographicMemory:
    """Create a VectorHolographicMemory with default configuration.

    Args:
        embedder: L-gent embedder for semantic vectors
        persistence_path: Optional path for persistence
        namespace: Memory namespace
        **config_kwargs: Additional config options

    Returns:
        Configured VectorHolographicMemory instance
    """
    # Import here to avoid circular imports
    try:
        from agents.l.vector_db import DgentVectorBackend
    except ImportError:
        from impl.claude.agents.l.vector_db import DgentVectorBackend

    config = VectorMemoryConfig(
        dimension=embedder.dimension,
        persistence_path=persistence_path,
        namespace=namespace,
        **config_kwargs,
    )

    vector_backend = DgentVectorBackend(
        dimension=config.dimension,
        persistence_path=persistence_path,
    )

    return VectorHolographicMemory(
        embedder=embedder,
        vector_backend=vector_backend,
        config=config,
    )


def create_simple_vector_memory(dimension: int = 64) -> VectorHolographicMemory:
    """Create a VectorHolographicMemory with mock components for testing.

    This uses the base HolographicMemory's pseudo-embedding instead of
    real L-gent components, useful for unit testing.

    Args:
        dimension: Embedding dimension for mock embeddings

    Returns:
        VectorHolographicMemory with mock backend
    """

    class MockEmbedder:
        """Mock embedder for testing."""

        def __init__(self, dim: int):
            self.dimension = dim

        async def embed(self, text: str) -> list[float]:
            """Generate deterministic pseudo-embedding."""
            import hashlib
            import math

            h = hashlib.sha256(text.encode()).digest()
            values = [float(b) / 255.0 for b in h[: self.dimension]]
            # Normalize
            norm = math.sqrt(sum(v * v for v in values))
            if norm > 0:
                values = [v / norm for v in values]
            return values

    class MockVectorBackend:
        """Mock vector backend for testing."""

        def __init__(self):
            self._vectors: dict[str, tuple[list[float], dict]] = {}

        async def add(self, id: str, vector: list[float], metadata: dict) -> None:
            self._vectors[id] = (vector, metadata)

        async def search(
            self,
            query_vector: list[float],
            limit: int = 10,
            threshold: float = 0.0,
            filters: Optional[dict] = None,
        ) -> list[Any]:
            import math

            @dataclass
            class MockResult:
                id: str
                similarity: float

            def cosine(a: list[float], b: list[float]) -> float:
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return dot / (norm_a * norm_b)

            results = []
            for vid, (vec, _) in self._vectors.items():
                sim = cosine(query_vector, vec)
                if sim >= threshold:
                    results.append(MockResult(id=vid, similarity=sim))

            results.sort(key=lambda r: r.similarity, reverse=True)
            return results[:limit]

        async def remove(self, id: str) -> None:
            self._vectors.pop(id, None)

        async def find_void(self, *args, **kwargs) -> Optional[dict]:
            return None

        async def curvature_at(self, *args, **kwargs) -> float:
            return 0.5

        async def cluster_centers(self, k: int) -> list[list[float]]:
            # Return centers from actual vectors
            vectors = list(self._vectors.values())
            if not vectors:
                return []
            return [v[0] for v in vectors[:k]]

    return VectorHolographicMemory(
        embedder=MockEmbedder(dimension),
        vector_backend=MockVectorBackend(),
        config=VectorMemoryConfig(dimension=dimension),
    )
