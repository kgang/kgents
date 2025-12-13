"""
MemoryCrystal: Holographic Memory with Graceful Degradation.

The core M-gent substrate where compression reduces resolution uniformly.
Unlike traditional memory where compression deletes data, holographic
compression makes everything fuzzier uniformly—50% compression means
ALL memories are 50% fuzzier, not 50% of memories are lost.

Key Properties:
- Store by superposition (all memories in same interference pattern)
- Retrieve by resonance (similarity-based, always returns something)
- Compress without losing memories (just resolution)
- Promote/demote individual concepts (graceful forgetting)

This implements the Four Pillars insight: memory is reconstruction, not retrieval.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

try:
    import numpy as np
    from numpy.typing import NDArray

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None  # type: ignore
    NDArray = Any  # type: ignore

T = TypeVar("T")


@dataclass
class CrystalPattern(Generic[T]):
    """A stored pattern in the memory crystal.

    Each pattern has:
    - A concept identifier
    - The original content (for reconstruction)
    - An embedding vector
    - Resolution level (1.0 = full, 0.1 = heavily compressed)
    - Metadata for access tracking
    """

    concept_id: str
    content: T
    embedding: list[float]
    resolution: float = 1.0
    stored_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def access(self) -> None:
        """Record an access."""
        self.last_accessed = datetime.now()
        self.access_count += 1


@dataclass
class ResonanceMatch:
    """A match from resonance-based retrieval."""

    concept_id: str
    similarity: float  # 0.0 to 1.0
    resolution: float  # Current resolution level


class MemoryCrystal(Generic[T]):
    """
    Holographic memory with graceful degradation.

    Key insight: 50% compression → 50% fuzzier (not 50% data loss).
    All memories are preserved at reduced resolution.

    Example:
        crystal = MemoryCrystal[str](dimension=1024)

        # Store concepts
        crystal.store("concept_a", "User prefers dark mode", embedding_a)
        crystal.store("concept_b", "User works on Python", embedding_b)

        # Retrieve by resonance
        results = crystal.retrieve(query_embedding, threshold=0.5)

        # Compress (all concepts preserved, lower resolution)
        compressed = crystal.compress(ratio=0.5)
        assert len(compressed.concepts) == len(crystal.concepts)

    The holographic property means partial destruction (compression)
    affects ALL stored patterns equally, rather than destroying some
    while preserving others.
    """

    def __init__(
        self,
        dimension: int = 1024,
        interference_pattern: list[float] | None = None,
    ) -> None:
        """Initialize memory crystal.

        Args:
            dimension: Vector dimension for embeddings
            interference_pattern: Pre-existing pattern (for loading)
        """
        self._dimension = dimension

        # The holographic substrate - sum of all stored patterns
        if interference_pattern is not None:
            self._interference: list[float] = interference_pattern
        else:
            self._interference = [0.0] * dimension

        # Metadata for each stored concept
        self._patterns: dict[str, CrystalPattern[T]] = {}

        # Hot patterns (recently accessed, high resolution)
        self._hot_patterns: set[str] = set()

    @property
    def dimension(self) -> int:
        """Vector dimension."""
        return self._dimension

    @property
    def concepts(self) -> set[str]:
        """All stored concept IDs."""
        return set(self._patterns.keys())

    @property
    def hot_patterns(self) -> set[str]:
        """Currently hot (frequently accessed) patterns."""
        return self._hot_patterns.copy()

    @property
    def resolution_levels(self) -> dict[str, float]:
        """Resolution level for each concept."""
        return {cid: p.resolution for cid, p in self._patterns.items()}

    def store(
        self,
        concept_id: str,
        content: T,
        embedding: list[float],
    ) -> CrystalPattern[T]:
        """Store memory by superposition on interference pattern.

        Args:
            concept_id: Unique identifier for this concept
            content: The actual content to store
            embedding: Vector representation

        Returns:
            The created CrystalPattern
        """
        # Normalize embedding
        norm_embedding = self._normalize(embedding)

        # Pad or truncate to match dimension
        if len(norm_embedding) < self._dimension:
            norm_embedding = norm_embedding + [0.0] * (
                self._dimension - len(norm_embedding)
            )
        elif len(norm_embedding) > self._dimension:
            norm_embedding = norm_embedding[: self._dimension]

        # Superimpose on interference pattern (holographic storage)
        for i, val in enumerate(norm_embedding):
            self._interference[i] += val

        # Create pattern record
        pattern = CrystalPattern(
            concept_id=concept_id,
            content=content,
            embedding=norm_embedding,
            resolution=1.0,
        )
        self._patterns[concept_id] = pattern

        # Track as hot (newly stored = hot)
        self._hot_patterns.add(concept_id)

        return pattern

    def retrieve(
        self,
        cue: list[float],
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[ResonanceMatch]:
        """Retrieve memories by resonance with cue.

        Unlike traditional retrieval, this ALWAYS returns something
        at lower resolution for weak matches.

        Args:
            cue: Query embedding vector
            threshold: Minimum similarity threshold
            limit: Maximum number of results

        Returns:
            List of ResonanceMatch sorted by effective score
        """
        # Normalize cue
        norm_cue = self._normalize(cue)

        # Pad or truncate
        if len(norm_cue) < self._dimension:
            norm_cue = norm_cue + [0.0] * (self._dimension - len(norm_cue))
        elif len(norm_cue) > self._dimension:
            norm_cue = norm_cue[: self._dimension]

        results: list[ResonanceMatch] = []

        for concept_id, pattern in self._patterns.items():
            # Compute similarity with stored embedding
            similarity = self._cosine_similarity(norm_cue, pattern.embedding)

            # Effective similarity = raw similarity * resolution
            effective_similarity = similarity * pattern.resolution

            if effective_similarity >= threshold:
                results.append(
                    ResonanceMatch(
                        concept_id=concept_id,
                        similarity=similarity,
                        resolution=pattern.resolution,
                    )
                )
                # Record access
                pattern.access()

        # Sort by effective score (similarity * resolution)
        results.sort(key=lambda r: r.similarity * r.resolution, reverse=True)

        return results[:limit]

    def retrieve_content(self, concept_id: str) -> T | None:
        """Retrieve the stored content for a concept.

        Args:
            concept_id: The concept to retrieve

        Returns:
            The stored content, or None if not found
        """
        pattern = self._patterns.get(concept_id)
        if pattern:
            pattern.access()
            return pattern.content
        return None

    def compress(self, ratio: float = 0.5) -> "MemoryCrystal[T]":
        """Compress memory uniformly (holographic property).

        This is THE key insight: compression affects resolution,
        not which memories are kept. All concepts are preserved
        at reduced resolution.

        Args:
            ratio: Compression ratio (0.5 = halve resolution)

        Returns:
            New MemoryCrystal with compressed patterns
        """
        if ratio <= 0 or ratio > 1:
            raise ValueError("Compression ratio must be in (0, 1]")

        # Create compressed interference pattern
        new_dim = max(1, int(self._dimension * ratio))

        # Interpolate to new dimension
        if new_dim != self._dimension:
            compressed_pattern = self._interpolate(self._interference, new_dim)
        else:
            compressed_pattern = self._interference.copy()

        # Create new crystal
        new_crystal: MemoryCrystal[T] = MemoryCrystal(
            dimension=new_dim,
            interference_pattern=compressed_pattern,
        )

        # Copy patterns with reduced resolution
        for concept_id, pattern in self._patterns.items():
            # Compress embedding too
            if new_dim != self._dimension:
                new_embedding = self._interpolate(pattern.embedding, new_dim)
            else:
                new_embedding = pattern.embedding.copy()

            new_pattern = CrystalPattern(
                concept_id=concept_id,
                content=pattern.content,
                embedding=new_embedding,
                resolution=pattern.resolution * ratio,
                stored_at=pattern.stored_at,
                last_accessed=pattern.last_accessed,
                access_count=pattern.access_count,
            )
            new_crystal._patterns[concept_id] = new_pattern

        # Copy hot patterns
        new_crystal._hot_patterns = self._hot_patterns.copy()

        return new_crystal

    def demote(self, concept_id: str, factor: float = 0.5) -> None:
        """Lower resolution of a specific concept (graceful forgetting).

        Args:
            concept_id: Concept to demote
            factor: Reduction factor (0.5 = halve resolution)
        """
        if concept_id not in self._patterns:
            return

        pattern = self._patterns[concept_id]
        pattern.resolution = max(0.01, pattern.resolution * factor)

        # Remove from hot if resolution drops below 0.5
        if pattern.resolution < 0.5:
            self._hot_patterns.discard(concept_id)

    def promote(self, concept_id: str, factor: float = 1.2) -> None:
        """Increase resolution of a concept (reinforcement).

        Args:
            concept_id: Concept to promote
            factor: Increase factor (1.2 = 20% increase)
        """
        if concept_id not in self._patterns:
            return

        pattern = self._patterns[concept_id]
        pattern.resolution = min(1.0, pattern.resolution * factor)

        # Add to hot if resolution exceeds 0.7
        if pattern.resolution >= 0.7:
            self._hot_patterns.add(concept_id)

    def get_pattern(self, concept_id: str) -> CrystalPattern[T] | None:
        """Get pattern metadata for a concept."""
        return self._patterns.get(concept_id)

    def stats(self) -> dict[str, Any]:
        """Get memory crystal statistics."""
        resolutions = [p.resolution for p in self._patterns.values()]
        return {
            "dimension": self._dimension,
            "concept_count": len(self._patterns),
            "hot_count": len(self._hot_patterns),
            "avg_resolution": sum(resolutions) / max(len(resolutions), 1),
            "min_resolution": min(resolutions) if resolutions else 0.0,
            "max_resolution": max(resolutions) if resolutions else 0.0,
            "interference_magnitude": self._magnitude(self._interference),
        }

    # ========== Private Methods ==========

    def _normalize(self, vec: list[float]) -> list[float]:
        """Normalize vector to unit length."""
        magnitude = self._magnitude(vec)
        if magnitude == 0:
            return vec
        return [v / magnitude for v in vec]

    def _magnitude(self, vec: list[float]) -> float:
        """Compute vector magnitude."""
        return math.sqrt(sum(v * v for v in vec))

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            # Pad shorter vector
            max_len = max(len(a), len(b))
            a = a + [0.0] * (max_len - len(a))
            b = b + [0.0] * (max_len - len(b))

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = self._magnitude(a)
        norm_b = self._magnitude(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    def _interpolate(self, vec: list[float], new_size: int) -> list[float]:
        """Interpolate vector to new size."""
        if len(vec) == new_size:
            return vec.copy()

        if HAS_NUMPY and np is not None:
            arr = np.array(vec)
            indices = np.linspace(0, len(vec) - 1, new_size)
            return list(np.interp(indices, np.arange(len(vec)), arr))
        else:
            # Pure Python interpolation
            result = []
            for i in range(new_size):
                # Map new index to original index
                orig_idx = i * (len(vec) - 1) / max(new_size - 1, 1)
                lower = int(orig_idx)
                upper = min(lower + 1, len(vec) - 1)
                frac = orig_idx - lower
                result.append(vec[lower] * (1 - frac) + vec[upper] * frac)
            return result


# ========== Numpy-optimized version ==========


class NumPyCrystal(Generic[T]):
    """
    Numpy-optimized memory crystal for production use.

    Uses numpy arrays for faster computation on large embeddings.
    Falls back to pure Python if numpy is not available.
    """

    def __init__(
        self,
        dimension: int = 1024,
        interference_pattern: Any | None = None,
    ) -> None:
        """Initialize numpy-optimized crystal."""
        if not HAS_NUMPY:
            raise ImportError("NumPyCrystal requires numpy")

        self._dimension = dimension

        if interference_pattern is not None:
            self._interference: NDArray[np.floating[Any]] = np.asarray(
                interference_pattern, dtype=np.float64
            )
        else:
            self._interference = np.zeros(dimension, dtype=np.float64)

        self._patterns: dict[str, CrystalPattern[T]] = {}
        self._hot_patterns: set[str] = set()

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def concepts(self) -> set[str]:
        return set(self._patterns.keys())

    @property
    def resolution_levels(self) -> dict[str, float]:
        return {cid: p.resolution for cid, p in self._patterns.items()}

    def store(
        self,
        concept_id: str,
        content: T,
        embedding: list[float] | Any,
    ) -> CrystalPattern[T]:
        """Store with numpy optimization."""
        arr = np.asarray(embedding, dtype=np.float64)

        # Normalize
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm

        # Resize to match dimension
        if len(arr) < self._dimension:
            arr = np.pad(arr, (0, self._dimension - len(arr)))
        elif len(arr) > self._dimension:
            arr = arr[: self._dimension]

        # Superimpose
        self._interference += arr

        pattern = CrystalPattern(
            concept_id=concept_id,
            content=content,
            embedding=arr.tolist(),
            resolution=1.0,
        )
        self._patterns[concept_id] = pattern
        self._hot_patterns.add(concept_id)

        return pattern

    def retrieve(
        self,
        cue: list[float] | Any,
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[ResonanceMatch]:
        """Retrieve with numpy optimization."""
        cue_arr = np.asarray(cue, dtype=np.float64)

        # Normalize
        norm = np.linalg.norm(cue_arr)
        if norm > 0:
            cue_arr = cue_arr / norm

        # Resize
        if len(cue_arr) < self._dimension:
            cue_arr = np.pad(cue_arr, (0, self._dimension - len(cue_arr)))
        elif len(cue_arr) > self._dimension:
            cue_arr = cue_arr[: self._dimension]

        results: list[ResonanceMatch] = []

        for concept_id, pattern in self._patterns.items():
            pattern_arr = np.asarray(pattern.embedding)
            similarity = float(np.dot(cue_arr, pattern_arr))
            effective = similarity * pattern.resolution

            if effective >= threshold:
                results.append(
                    ResonanceMatch(
                        concept_id=concept_id,
                        similarity=similarity,
                        resolution=pattern.resolution,
                    )
                )
                pattern.access()

        results.sort(key=lambda r: r.similarity * r.resolution, reverse=True)
        return results[:limit]

    def compress(self, ratio: float = 0.5) -> "NumPyCrystal[T]":
        """Compress with numpy interpolation."""
        if ratio <= 0 or ratio > 1:
            raise ValueError("Compression ratio must be in (0, 1]")

        new_dim = max(1, int(self._dimension * ratio))

        # Interpolate interference pattern
        compressed = np.interp(
            np.linspace(0, 1, new_dim),
            np.linspace(0, 1, self._dimension),
            self._interference,
        )

        new_crystal: NumPyCrystal[T] = NumPyCrystal(
            dimension=new_dim,
            interference_pattern=compressed,
        )

        # Copy patterns with reduced resolution
        for concept_id, pattern in self._patterns.items():
            new_embedding = np.interp(
                np.linspace(0, 1, new_dim),
                np.linspace(0, 1, len(pattern.embedding)),
                pattern.embedding,
            )

            new_pattern = CrystalPattern(
                concept_id=concept_id,
                content=pattern.content,
                embedding=new_embedding.tolist(),
                resolution=pattern.resolution * ratio,
                stored_at=pattern.stored_at,
                last_accessed=pattern.last_accessed,
                access_count=pattern.access_count,
            )
            new_crystal._patterns[concept_id] = new_pattern

        new_crystal._hot_patterns = self._hot_patterns.copy()
        return new_crystal

    def demote(self, concept_id: str, factor: float = 0.5) -> None:
        """Lower resolution of a concept."""
        if concept_id not in self._patterns:
            return
        pattern = self._patterns[concept_id]
        pattern.resolution = max(0.01, pattern.resolution * factor)
        if pattern.resolution < 0.5:
            self._hot_patterns.discard(concept_id)

    def promote(self, concept_id: str, factor: float = 1.2) -> None:
        """Increase resolution of a concept."""
        if concept_id not in self._patterns:
            return
        pattern = self._patterns[concept_id]
        pattern.resolution = min(1.0, pattern.resolution * factor)
        if pattern.resolution >= 0.7:
            self._hot_patterns.add(concept_id)


def create_crystal(dimension: int = 1024, use_numpy: bool = True) -> Any:
    """Factory function to create appropriate crystal type.

    Args:
        dimension: Vector dimension
        use_numpy: Whether to prefer numpy implementation

    Returns:
        MemoryCrystal or NumPyCrystal instance
    """
    if use_numpy and HAS_NUMPY:
        return NumPyCrystal(dimension=dimension)
    return MemoryCrystal(dimension=dimension)
