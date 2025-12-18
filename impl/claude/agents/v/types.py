"""
V-gent Types: Core data structures for vector operations.

This module defines:
- Embedding: A semantic vector with dimension and metadata
- VectorEntry: A vector stored in an index with its identifier
- SearchResult: Result from a vector search
- DistanceMetric: Distance metrics for vector comparison
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# =============================================================================
# Distance Metrics
# =============================================================================


def _dot_product(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute dot product of two vectors."""
    return sum(x * y for x, y in zip(a, b))


def _magnitude(v: tuple[float, ...]) -> float:
    """Compute magnitude (L2 norm) of a vector."""
    return math.sqrt(sum(x * x for x in v))


def _cosine_similarity(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns a value in [-1, 1], where 1 is identical direction.
    """
    dot = _dot_product(a, b)
    mag_a = _magnitude(a)
    mag_b = _magnitude(b)

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot / (mag_a * mag_b)


def _euclidean_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute Euclidean (L2) distance between two vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _manhattan_distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Compute Manhattan (L1) distance between two vectors."""
    return sum(abs(x - y) for x, y in zip(a, b))


class DistanceMetric(Enum):
    """
    Distance metrics for vector comparison.

    Each metric defines how similarity is computed between vectors.
    The `similarity()` method returns a value where higher = more similar.

    Metric Space Laws (for distance):
    - Identity: d(x, x) = 0
    - Symmetry: d(x, y) = d(y, x)
    - Triangle Inequality: d(x, z) ≤ d(x, y) + d(y, z)
    - Non-negativity: d(x, y) ≥ 0
    """

    COSINE = "cosine"
    """Most common for text embeddings. Direction-based similarity."""

    EUCLIDEAN = "euclidean"
    """Geometric distance. Magnitude-sensitive."""

    DOT_PRODUCT = "dot_product"
    """Fast, assumes normalized vectors. Often used with sentence-transformers."""

    MANHATTAN = "manhattan"
    """L1 norm. Good for sparse data."""

    def distance(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """
        Compute distance between two vectors.

        Returns a non-negative value where 0 = identical.
        """
        if self == DistanceMetric.COSINE:
            # Cosine distance = 1 - cosine similarity
            return 1.0 - _cosine_similarity(a, b)
        elif self == DistanceMetric.DOT_PRODUCT:
            # For normalized vectors, dot product similarity → distance
            # Higher dot product = more similar = lower distance
            return 1.0 - _dot_product(a, b)
        elif self == DistanceMetric.EUCLIDEAN:
            return _euclidean_distance(a, b)
        elif self == DistanceMetric.MANHATTAN:
            return _manhattan_distance(a, b)
        raise ValueError(f"Unknown metric: {self}")

    def similarity(self, a: tuple[float, ...], b: tuple[float, ...]) -> float:
        """
        Compute similarity between two vectors.

        Returns a value where higher = more similar.
        For most metrics, this is in [0, 1].

        Note: Cosine similarity can be negative (opposite directions),
        but we clamp to [0, 1] for consistency.
        """
        if self == DistanceMetric.COSINE:
            # Clamp to [0, 1] for consistency
            sim = _cosine_similarity(a, b)
            return max(0.0, sim)
        elif self == DistanceMetric.DOT_PRODUCT:
            # For normalized vectors, dot product ∈ [-1, 1]
            # Clamp to [0, 1]
            dot = _dot_product(a, b)
            return max(0.0, min(1.0, dot))
        elif self == DistanceMetric.EUCLIDEAN:
            # Convert distance to similarity: 1 / (1 + distance)
            dist = _euclidean_distance(a, b)
            return 1.0 / (1.0 + dist)
        elif self == DistanceMetric.MANHATTAN:
            # Convert distance to similarity: 1 / (1 + distance)
            dist = _manhattan_distance(a, b)
            return 1.0 / (1.0 + dist)
        raise ValueError(f"Unknown metric: {self}")


# =============================================================================
# Core Types
# =============================================================================


@dataclass(frozen=True)
class Embedding:
    """
    A semantic vector with dimension and optional metadata.

    Embeddings capture meaning in geometric space.
    Similar meanings → nearby vectors.

    Attributes:
        vector: Immutable tuple of floats (for hashability)
        dimension: Length of vector (must equal len(vector))
        source: What generated this embedding (e.g., "openai/text-embedding-3-small")
        metadata: Optional metadata (model version, timestamp, etc.)

    Example:
        embedding = Embedding(
            vector=(0.1, 0.2, 0.3),
            dimension=3,
            source="local/test",
        )
        similarity = embedding.similarity(other_embedding)
    """

    vector: tuple[float, ...]
    dimension: int
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate dimension matches vector length."""
        if len(self.vector) != self.dimension:
            raise ValueError(
                f"Vector length {len(self.vector)} != declared dimension {self.dimension}"
            )

    def similarity(self, other: Embedding, metric: DistanceMetric | None = None) -> float:
        """
        Compute similarity to another embedding.

        Args:
            other: Another embedding to compare against
            metric: Distance metric (defaults to COSINE)

        Returns:
            Similarity score (higher = more similar)

        Raises:
            ValueError: If dimensions don't match
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} != {other.dimension}")
        metric = metric or DistanceMetric.COSINE
        return metric.similarity(self.vector, other.vector)

    def distance(self, other: Embedding, metric: DistanceMetric | None = None) -> float:
        """
        Compute distance to another embedding.

        Args:
            other: Another embedding to compare against
            metric: Distance metric (defaults to COSINE)

        Returns:
            Distance (lower = more similar, 0 = identical)

        Raises:
            ValueError: If dimensions don't match
        """
        if self.dimension != other.dimension:
            raise ValueError(f"Dimension mismatch: {self.dimension} != {other.dimension}")
        metric = metric or DistanceMetric.COSINE
        return metric.distance(self.vector, other.vector)

    @classmethod
    def from_list(cls, vector: list[float], source: str = "unknown", **metadata: Any) -> Embedding:
        """
        Create Embedding from a list of floats.

        Args:
            vector: List of floats
            source: Embedding source identifier
            **metadata: Additional metadata

        Returns:
            New Embedding instance
        """
        return cls(
            vector=tuple(vector),
            dimension=len(vector),
            source=source,
            metadata=metadata,
        )

    def to_list(self) -> list[float]:
        """Convert vector to list for serialization."""
        return list(self.vector)


@dataclass(frozen=True)
class VectorEntry:
    """
    A vector stored in an index with its identifier.

    VectorEntry wraps an Embedding with an ID and additional metadata
    for storage in a vector index.

    Attributes:
        id: Unique identifier for this entry
        embedding: The vector
        metadata: Filterable metadata (tags, types, etc.)
    """

    id: str
    embedding: Embedding
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchResult:
    """
    Result from a vector search.

    Attributes:
        id: Entry identifier
        similarity: Similarity score (0.0 to 1.0, higher = more similar)
        distance: Raw distance (metric-dependent, lower = more similar)
        metadata: Entry metadata
    """

    id: str
    similarity: float
    distance: float
    metadata: dict[str, str] = field(default_factory=dict)

    def __lt__(self, other: SearchResult) -> bool:
        """Compare by similarity (descending) for sorting."""
        return self.similarity > other.similarity  # Higher similarity first
