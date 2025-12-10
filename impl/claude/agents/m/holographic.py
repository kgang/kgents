"""
HolographicMemory: The Core M-gent Substrate.

Memory where information is distributed across the whole.
Unlike localized memory (lose a sector, lose that data),
holographic memory degrades gracefully: compression
reduces resolution uniformly, not catastrophically.

Key Properties:
- Store by superposition (all memories in same distributed space)
- Retrieve by resonance (similarity-based, always returns something)
- Compress without losing memories (just resolution)

Integration:
- Uses D-gent UnifiedMemory for storage
- Uses L-gent VectorBackend for embeddings
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Generic, TypeVar
import math

T = TypeVar("T")


class CompressionLevel(Enum):
    """Resolution levels for holographic storage."""

    FULL = auto()  # Original resolution
    HIGH = auto()  # 75% resolution
    MEDIUM = auto()  # 50% resolution
    LOW = auto()  # 25% resolution
    MINIMAL = auto()  # 10% resolution (highly compressed)


@dataclass
class MemoryPattern(Generic[T]):
    """A single pattern in the holographic interference pattern.

    Each pattern represents one stored memory, distributed across
    the holographic substrate.
    """

    id: str
    content: T
    embedding: list[float]  # Vector representation
    timestamp: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    compression: CompressionLevel = CompressionLevel.FULL
    strength: float = 1.0  # Retention strength (Ebbinghaus)
    concepts: list[str] = field(default_factory=list)  # Semantic tags

    @property
    def age(self) -> timedelta:
        """Time since creation."""
        return datetime.now() - self.timestamp

    @property
    def time_since_access(self) -> timedelta:
        """Time since last access."""
        return datetime.now() - self.last_accessed

    @property
    def temperature(self) -> float:
        """Memory temperature: hot (frequently accessed) to cold (dormant).

        Based on recency and frequency.
        """
        recency = 1.0 / (1.0 + self.time_since_access.total_seconds() / 3600)
        frequency = math.log1p(self.access_count) / 10.0
        return 0.6 * recency + 0.4 * frequency

    @property
    def retention(self) -> float:
        """Current retention level (Ebbinghaus forgetting curve).

        R = e^(-t/S) where t = time, S = strength
        """
        t = self.time_since_access.total_seconds() / 3600  # hours
        S = max(self.strength, 0.1)  # Avoid division issues
        return math.exp(-t / (S * 24))  # Decay over days

    def access(self) -> None:
        """Record an access, updating metadata."""
        self.last_accessed = datetime.now()
        self.access_count += 1
        # Strengthen on access (spaced repetition effect)
        self.strength = min(10.0, self.strength * 1.1)


@dataclass
class ResonanceResult(Generic[T]):
    """Result of resonance-based retrieval."""

    pattern: MemoryPattern[T]
    similarity: float  # 0.0 to 1.0
    resolution: float  # Effective resolution after compression

    @property
    def effective_score(self) -> float:
        """Combined score considering similarity and resolution."""
        return self.similarity * self.resolution


class HolographicMemory(Generic[T]):
    """The core holographic memory substrate.

    Memory where:
    - Store = superimpose on interference pattern
    - Retrieve = resonate with pattern
    - Compress = reduce dimension, keep all memories

    Example:
        memory = HolographicMemory(embedder=my_embedder)

        # Store
        await memory.store(
            id="mem-1",
            content="The user prefers dark mode",
            concepts=["preference", "ui", "dark-mode"]
        )

        # Retrieve by resonance
        results = await memory.retrieve(
            Cue(text="What are the user's UI preferences?")
        )

        # Consolidate (background processing)
        await memory.consolidate()
    """

    def __init__(
        self,
        embedder: Any = None,  # L-gent Embedder
        storage: Any = None,  # D-gent UnifiedMemory
        hot_threshold: float = 0.7,
        cold_threshold: float = 0.3,
        forget_threshold_days: float = 30.0,
    ):
        """Initialize holographic memory.

        Args:
            embedder: L-gent embedder for vector representations
            storage: D-gent UnifiedMemory for persistence
            hot_threshold: Temperature above which patterns are "hot"
            cold_threshold: Temperature below which patterns are "cold"
            forget_threshold_days: Days of inactivity before heavy compression
        """
        self._embedder = embedder
        self._storage = storage
        self._hot_threshold = hot_threshold
        self._cold_threshold = cold_threshold
        self._forget_threshold = timedelta(days=forget_threshold_days)

        # The interference pattern (in-memory cache)
        self._patterns: dict[str, MemoryPattern[T]] = {}

        # Statistics
        self._store_count = 0
        self._retrieve_count = 0

    async def store(
        self,
        id: str,
        content: T,
        concepts: list[str] | None = None,
        embedding: list[float] | None = None,
    ) -> MemoryPattern[T]:
        """Store memory by superposition on the interference pattern.

        Args:
            id: Unique identifier
            content: The memory content
            concepts: Semantic tags for association
            embedding: Pre-computed embedding (computed if not provided)

        Returns:
            The created MemoryPattern
        """
        # Get embedding
        if embedding is None and self._embedder is not None:
            embedding = await self._embedder.embed(str(content))
        elif embedding is None:
            # Fallback: simple hash-based pseudo-embedding
            embedding = self._pseudo_embed(str(content))

        # Create pattern
        pattern = MemoryPattern(
            id=id,
            content=content,
            embedding=embedding,
            concepts=concepts or [],
        )

        # Superimpose on interference pattern
        self._patterns[id] = pattern
        self._store_count += 1

        # Persist if storage available
        if self._storage is not None:
            await self._storage.associate(content, id)

        return pattern

    async def retrieve(
        self,
        query: str | list[float],
        limit: int = 10,
        threshold: float = 0.0,
    ) -> list[ResonanceResult[T]]:
        """Retrieve memories by resonance with the interference pattern.

        Unlike traditional retrieval, this ALWAYS returns something.
        Partial matches return lower-resolution reconstructions.

        Args:
            query: Text query or pre-computed embedding
            limit: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            List of ResonanceResult sorted by effective score
        """
        # Get query embedding
        if isinstance(query, str):
            if self._embedder is not None:
                query_embedding = await self._embedder.embed(query)
            else:
                query_embedding = self._pseudo_embed(query)
        else:
            query_embedding = query

        # Resonate with all patterns
        results: list[ResonanceResult[T]] = []
        for pattern in self._patterns.values():
            similarity = self._cosine_similarity(query_embedding, pattern.embedding)

            if similarity >= threshold:
                # Record access
                pattern.access()

                # Resolution based on compression level
                resolution = self._compression_to_resolution(pattern.compression)

                results.append(
                    ResonanceResult(
                        pattern=pattern,
                        similarity=similarity,
                        resolution=resolution,
                    )
                )

        # Sort by effective score
        results.sort(key=lambda r: r.effective_score, reverse=True)

        self._retrieve_count += 1
        return results[:limit]

    async def retrieve_by_concept(
        self,
        concept: str,
        limit: int = 10,
    ) -> list[ResonanceResult[T]]:
        """Retrieve memories associated with a concept.

        Args:
            concept: Semantic concept to match
            limit: Maximum number of results

        Returns:
            List of matching patterns
        """
        results: list[ResonanceResult[T]] = []
        for pattern in self._patterns.values():
            if concept in pattern.concepts:
                pattern.access()
                resolution = self._compression_to_resolution(pattern.compression)
                results.append(
                    ResonanceResult(
                        pattern=pattern,
                        similarity=1.0,  # Exact concept match
                        resolution=resolution,
                    )
                )

        results.sort(key=lambda r: pattern.temperature, reverse=True)
        return results[:limit]

    def identify_hot(self) -> list[MemoryPattern[T]]:
        """Identify hot (frequently accessed) patterns."""
        return [
            p for p in self._patterns.values() if p.temperature > self._hot_threshold
        ]

    def identify_cold(self) -> list[MemoryPattern[T]]:
        """Identify cold (dormant) patterns."""
        return [
            p for p in self._patterns.values() if p.temperature < self._cold_threshold
        ]

    async def demote(self, pattern_id: str, levels: int = 1) -> None:
        """Reduce resolution of a pattern (graceful forgetting).

        Args:
            pattern_id: Pattern to demote
            levels: Number of compression levels to increase
        """
        if pattern_id not in self._patterns:
            return

        pattern = self._patterns[pattern_id]
        compression_order = list(CompressionLevel)
        current_idx = compression_order.index(pattern.compression)
        new_idx = min(current_idx + levels, len(compression_order) - 1)
        pattern.compression = compression_order[new_idx]

    async def promote(self, pattern_id: str, levels: int = 1) -> None:
        """Increase resolution of a pattern (reinforcement).

        Args:
            pattern_id: Pattern to promote
            levels: Number of compression levels to decrease
        """
        if pattern_id not in self._patterns:
            return

        pattern = self._patterns[pattern_id]
        compression_order = list(CompressionLevel)
        current_idx = compression_order.index(pattern.compression)
        new_idx = max(current_idx - levels, 0)
        pattern.compression = compression_order[new_idx]

    async def compress(self, ratio: float = 0.5) -> int:
        """Compress all cold patterns to save space.

        Args:
            ratio: How much to compress (0.5 = halve resolution)

        Returns:
            Number of patterns compressed
        """
        cold = self.identify_cold()
        levels = max(1, int((1.0 - ratio) * 4))  # 4 compression levels

        for pattern in cold:
            await self.demote(pattern.id, levels=levels)

        return len(cold)

    async def consolidate(self) -> dict[str, Any]:
        """Background consolidation: compress cold, strengthen hot.

        This is the HYPNAGOGIC pattern: system improves while idle.

        Returns:
            Statistics about consolidation
        """
        stats = {
            "demoted": 0,
            "promoted": 0,
            "integrated": 0,
        }

        # Demote cold patterns
        for pattern in self.identify_cold():
            if pattern.time_since_access > self._forget_threshold:
                await self.demote(pattern.id, levels=2)
            else:
                await self.demote(pattern.id, levels=1)
            stats["demoted"] += 1

        # Promote hot patterns
        for pattern in self.identify_hot():
            await self.promote(pattern.id, levels=1)
            stats["promoted"] += 1

        # Integration: merge near-duplicates
        clusters = self._cluster_similar(threshold=0.95)
        for cluster in clusters:
            if len(cluster) > 1:
                await self._integrate_cluster(cluster)
                stats["integrated"] += len(cluster) - 1

        return stats

    def stats(self) -> dict[str, Any]:
        """Get memory statistics."""
        patterns = list(self._patterns.values())
        return {
            "total_patterns": len(patterns),
            "store_count": self._store_count,
            "retrieve_count": self._retrieve_count,
            "hot_count": len(self.identify_hot()),
            "cold_count": len(self.identify_cold()),
            "compression_distribution": {
                level.name: sum(1 for p in patterns if p.compression == level)
                for level in CompressionLevel
            },
            "avg_retention": sum(p.retention for p in patterns) / max(len(patterns), 1),
        }

    # ========== Private Methods ==========

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _pseudo_embed(self, text: str, dim: int = 64) -> list[float]:
        """Simple pseudo-embedding for testing without L-gent."""
        # Hash-based pseudo-embedding
        import hashlib

        h = hashlib.sha256(text.encode()).digest()
        values = [float(b) / 255.0 for b in h[:dim]]
        # Normalize
        norm = math.sqrt(sum(v * v for v in values))
        if norm > 0:
            values = [v / norm for v in values]
        return values

    def _compression_to_resolution(self, compression: CompressionLevel) -> float:
        """Convert compression level to resolution factor."""
        mapping = {
            CompressionLevel.FULL: 1.0,
            CompressionLevel.HIGH: 0.75,
            CompressionLevel.MEDIUM: 0.5,
            CompressionLevel.LOW: 0.25,
            CompressionLevel.MINIMAL: 0.1,
        }
        return mapping.get(compression, 1.0)

    def _cluster_similar(self, threshold: float = 0.95) -> list[list[str]]:
        """Find clusters of highly similar patterns.

        Returns:
            List of pattern ID clusters
        """
        patterns = list(self._patterns.values())
        visited = set()
        clusters = []

        for i, p1 in enumerate(patterns):
            if p1.id in visited:
                continue

            cluster = [p1.id]
            visited.add(p1.id)

            for j, p2 in enumerate(patterns[i + 1 :], i + 1):
                if p2.id in visited:
                    continue
                sim = self._cosine_similarity(p1.embedding, p2.embedding)
                if sim >= threshold:
                    cluster.append(p2.id)
                    visited.add(p2.id)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    async def _integrate_cluster(self, cluster: list[str]) -> None:
        """Merge a cluster of similar patterns into one.

        Keeps the hottest pattern, compresses others.
        """
        if len(cluster) <= 1:
            return

        # Find the hottest pattern
        patterns = [self._patterns[pid] for pid in cluster if pid in self._patterns]
        if not patterns:
            return

        patterns.sort(key=lambda p: p.temperature, reverse=True)
        primary = patterns[0]

        # Merge concepts from all patterns into primary
        for pattern in patterns[1:]:
            for concept in pattern.concepts:
                if concept not in primary.concepts:
                    primary.concepts.append(concept)
            # Remove the merged pattern
            del self._patterns[pattern.id]

        # Strengthen primary
        primary.strength = min(10.0, primary.strength + 0.5 * len(patterns))
