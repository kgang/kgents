"""
V-gent test fixtures.

Provides common fixtures for testing V-gent backends:
- memory_backend: Fresh MemoryVectorBackend
- sample_embeddings: Pre-generated test embeddings
- sample_vectors: Raw vector data
- sample_entries: Pre-built VectorEntry objects
"""

from __future__ import annotations

import math
import random
from typing import AsyncIterator

import pytest

from ..backends.memory import MemoryVectorBackend
from ..types import DistanceMetric, Embedding, VectorEntry


# =============================================================================
# Constants
# =============================================================================

TEST_DIMENSION = 8  # Small dimension for fast tests


# =============================================================================
# Vector Generation Utilities
# =============================================================================


def make_unit_vector(seed: int, dimension: int = TEST_DIMENSION) -> tuple[float, ...]:
    """
    Generate a deterministic unit vector (normalized to length 1).

    Args:
        seed: Random seed for reproducibility
        dimension: Vector dimension

    Returns:
        Normalized vector as tuple
    """
    rng = random.Random(seed)
    raw = [rng.gauss(0, 1) for _ in range(dimension)]
    magnitude = math.sqrt(sum(x * x for x in raw))
    if magnitude == 0:
        magnitude = 1.0
    return tuple(x / magnitude for x in raw)


def make_embedding(
    seed: int, dimension: int = TEST_DIMENSION, source: str = "test"
) -> Embedding:
    """
    Generate a deterministic test embedding.

    Args:
        seed: Random seed for reproducibility
        dimension: Vector dimension
        source: Source identifier

    Returns:
        Embedding instance
    """
    vector = make_unit_vector(seed, dimension)
    return Embedding(
        vector=vector,
        dimension=dimension,
        source=source,
        metadata={"seed": str(seed)},
    )


def make_similar_embedding(
    base: Embedding, noise: float = 0.1, seed: int = 42
) -> Embedding:
    """
    Generate an embedding similar to the base with added noise.

    Args:
        base: Base embedding to perturb
        noise: Noise magnitude (0 = identical, 1 = random)
        seed: Random seed

    Returns:
        Similar embedding
    """
    rng = random.Random(seed)
    noisy = []
    for x in base.vector:
        noisy.append(x + rng.gauss(0, noise))

    # Normalize
    magnitude = math.sqrt(sum(x * x for x in noisy))
    if magnitude == 0:
        magnitude = 1.0
    normalized = tuple(x / magnitude for x in noisy)

    return Embedding(
        vector=normalized,
        dimension=base.dimension,
        source=f"{base.source}/similar",
        metadata={"noise": str(noise)},
    )


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def memory_backend() -> MemoryVectorBackend:
    """Fresh in-memory backend with cosine metric."""
    return MemoryVectorBackend(dimension=TEST_DIMENSION, metric=DistanceMetric.COSINE)


@pytest.fixture
def euclidean_backend() -> MemoryVectorBackend:
    """Fresh in-memory backend with euclidean metric."""
    return MemoryVectorBackend(
        dimension=TEST_DIMENSION, metric=DistanceMetric.EUCLIDEAN
    )


@pytest.fixture
def sample_embeddings() -> list[Embedding]:
    """Generate 10 deterministic test embeddings."""
    return [make_embedding(i) for i in range(10)]


@pytest.fixture
def sample_vectors() -> list[list[float]]:
    """Generate 10 deterministic raw vectors."""
    return [list(make_unit_vector(i)) for i in range(10)]


@pytest.fixture
def sample_entries(sample_embeddings: list[Embedding]) -> list[VectorEntry]:
    """Generate 10 VectorEntry objects with metadata."""
    entries = []
    for i, emb in enumerate(sample_embeddings):
        entries.append(
            VectorEntry(
                id=f"entry_{i}",
                embedding=emb,
                metadata={
                    "type": "test",
                    "index": str(i),
                    "category": "even" if i % 2 == 0 else "odd",
                },
            )
        )
    return entries


@pytest.fixture
async def populated_backend(
    memory_backend: MemoryVectorBackend, sample_entries: list[VectorEntry]
) -> AsyncIterator[MemoryVectorBackend]:
    """
    Memory backend pre-populated with sample entries.

    Yields a backend with 10 entries, then clears after test.
    """
    for entry in sample_entries:
        await memory_backend.add(entry.id, entry.embedding, entry.metadata)

    yield memory_backend

    await memory_backend.clear()


# =============================================================================
# Protocol Compliance Fixtures
# =============================================================================


@pytest.fixture(
    params=[
        DistanceMetric.COSINE,
        DistanceMetric.EUCLIDEAN,
        DistanceMetric.DOT_PRODUCT,
        DistanceMetric.MANHATTAN,
    ]
)
def metric(request: pytest.FixtureRequest) -> DistanceMetric:
    """Parametrized fixture for all distance metrics."""
    return request.param


@pytest.fixture
def backend_with_metric(metric: DistanceMetric) -> MemoryVectorBackend:
    """Memory backend with parametrized metric."""
    return MemoryVectorBackend(dimension=TEST_DIMENSION, metric=metric)
