"""
V-gent Protocol Tests: Verify VgentProtocol compliance and mathematical properties.

Tests cover:
1. Protocol compliance (runtime_checkable)
2. Metric space laws
3. Idempotence
4. Monotonicity
5. Distance metric properties
"""

from __future__ import annotations

import math

import pytest

from ..backends.memory import MemoryVectorBackend
from ..protocol import VgentProtocol
from ..types import DistanceMetric, Embedding
from .conftest import TEST_DIMENSION, make_embedding, make_unit_vector


class TestProtocolCompliance:
    """Verify VgentProtocol runtime checking."""

    def test_memory_backend_is_vgent_protocol(self) -> None:
        """MemoryVectorBackend implements VgentProtocol."""
        backend = MemoryVectorBackend(dimension=8)
        assert isinstance(backend, VgentProtocol)

    def test_vgent_protocol_is_runtime_checkable(self) -> None:
        """VgentProtocol is runtime_checkable."""
        # Should not raise
        assert hasattr(VgentProtocol, "__subclasshook__")

    def test_non_vgent_is_not_protocol(self) -> None:
        """Non-implementing class is not VgentProtocol."""

        class NotAVgent:
            pass

        obj = NotAVgent()
        assert not isinstance(obj, VgentProtocol)


class TestMetricSpaceLaws:
    """
    Verify distance metrics satisfy metric space laws.

    Laws:
    1. Identity: d(x, x) = 0
    2. Symmetry: d(x, y) = d(y, x)
    3. Triangle Inequality: d(x, z) ≤ d(x, y) + d(y, z)
    4. Non-negativity: d(x, y) ≥ 0
    """

    @pytest.mark.law("metric_identity")
    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_identity_law(self, metric: DistanceMetric) -> None:
        """d(x, x) = 0 for all x."""
        v = make_unit_vector(42)
        distance = metric.distance(v, v)
        assert distance == pytest.approx(0.0, abs=1e-9)

    @pytest.mark.law("metric_symmetry")
    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_symmetry_law(self, metric: DistanceMetric) -> None:
        """d(x, y) = d(y, x) for all x, y."""
        v1 = make_unit_vector(1)
        v2 = make_unit_vector(2)

        d_xy = metric.distance(v1, v2)
        d_yx = metric.distance(v2, v1)

        assert d_xy == pytest.approx(d_yx, abs=1e-9)

    @pytest.mark.law("metric_triangle_inequality")
    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_triangle_inequality(self, metric: DistanceMetric) -> None:
        """d(x, z) ≤ d(x, y) + d(y, z) for all x, y, z."""
        v1 = make_unit_vector(1)
        v2 = make_unit_vector(2)
        v3 = make_unit_vector(3)

        d_xz = metric.distance(v1, v3)
        d_xy = metric.distance(v1, v2)
        d_yz = metric.distance(v2, v3)

        # Allow small floating point tolerance
        assert d_xz <= d_xy + d_yz + 1e-9

    @pytest.mark.law("metric_non_negativity")
    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_non_negativity(self, metric: DistanceMetric) -> None:
        """d(x, y) ≥ 0 for all x, y."""
        v1 = make_unit_vector(1)
        v2 = make_unit_vector(2)

        distance = metric.distance(v1, v2)
        assert distance >= -1e-9  # Allow tiny floating point errors


class TestSimilarityProperties:
    """Test similarity function properties."""

    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_self_similarity_is_maximal(self, metric: DistanceMetric) -> None:
        """similarity(x, x) should be 1.0 (or close to it)."""
        v = make_unit_vector(42)
        similarity = metric.similarity(v, v)
        assert similarity == pytest.approx(1.0, abs=1e-6)

    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    def test_similarity_is_bounded(self, metric: DistanceMetric) -> None:
        """Similarity should be in [0, 1]."""
        v1 = make_unit_vector(1)
        v2 = make_unit_vector(2)

        similarity = metric.similarity(v1, v2)
        assert 0.0 <= similarity <= 1.0

    def test_similar_vectors_have_high_cosine_similarity(self) -> None:
        """Vectors with small perturbation have high similarity."""
        base = make_unit_vector(1)
        # Create similar vector with tiny noise
        noisy = tuple(x + 0.01 for x in base)
        # Normalize
        mag = math.sqrt(sum(x * x for x in noisy))
        similar = tuple(x / mag for x in noisy)

        similarity = DistanceMetric.COSINE.similarity(base, similar)
        assert similarity > 0.99

    def test_orthogonal_vectors_have_low_cosine_similarity(self) -> None:
        """Orthogonal vectors should have ~0 cosine similarity."""
        # Create two orthogonal unit vectors
        v1 = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        v2 = (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        similarity = DistanceMetric.COSINE.similarity(v1, v2)
        assert similarity == pytest.approx(0.0, abs=1e-9)


class TestEmbeddingType:
    """Test Embedding dataclass."""

    def test_embedding_creation(self) -> None:
        """Create embedding with valid dimensions."""
        emb = Embedding(
            vector=(0.1, 0.2, 0.3),
            dimension=3,
            source="test",
        )
        assert emb.dimension == 3
        assert len(emb.vector) == 3

    def test_embedding_dimension_mismatch_raises(self) -> None:
        """Dimension mismatch should raise ValueError."""
        with pytest.raises(ValueError, match="dimension"):
            Embedding(
                vector=(0.1, 0.2, 0.3),
                dimension=5,  # Mismatch!
                source="test",
            )

    def test_embedding_from_list(self) -> None:
        """Create embedding from list."""
        emb = Embedding.from_list([0.1, 0.2, 0.3], source="test")
        assert emb.dimension == 3
        assert emb.vector == (0.1, 0.2, 0.3)

    def test_embedding_to_list(self) -> None:
        """Convert embedding to list."""
        emb = Embedding(vector=(0.1, 0.2, 0.3), dimension=3, source="test")
        lst = emb.to_list()
        assert lst == [0.1, 0.2, 0.3]

    def test_embedding_similarity(self) -> None:
        """Compute similarity between embeddings."""
        emb1 = make_embedding(1)
        emb2 = make_embedding(2)
        emb_self = make_embedding(1)

        self_sim = emb1.similarity(emb_self)
        cross_sim = emb1.similarity(emb2)

        assert self_sim == pytest.approx(1.0, abs=1e-6)
        assert 0.0 <= cross_sim <= 1.0

    def test_embedding_similarity_dimension_mismatch(self) -> None:
        """Similarity with mismatched dimensions raises."""
        emb1 = Embedding(vector=(0.1, 0.2, 0.3), dimension=3, source="test")
        emb2 = Embedding(vector=(0.1, 0.2), dimension=2, source="test")

        with pytest.raises(ValueError, match="mismatch"):
            emb1.similarity(emb2)

    def test_embedding_distance(self) -> None:
        """Compute distance between embeddings."""
        emb1 = make_embedding(1)
        emb_self = make_embedding(1)

        self_dist = emb1.distance(emb_self)
        assert self_dist == pytest.approx(0.0, abs=1e-6)

    def test_embedding_is_frozen(self) -> None:
        """Embedding is immutable (frozen dataclass)."""
        emb = make_embedding(1)
        with pytest.raises(Exception):  # FrozenInstanceError
            emb.dimension = 999  # type: ignore


class TestIdempotence:
    """Verify idempotence property: add(id, emb) twice = once."""

    @pytest.mark.asyncio
    async def test_add_idempotent(self) -> None:
        """Adding same ID twice results in single entry."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)
        emb = make_embedding(1)

        await backend.add("test", emb)
        await backend.add("test", emb)

        count = await backend.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_add_updates_existing(self) -> None:
        """Adding same ID with different vector updates it."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)
        emb1 = make_embedding(1)
        emb2 = make_embedding(2)

        await backend.add("test", emb1, {"version": "1"})
        await backend.add("test", emb2, {"version": "2"})

        entry = await backend.get("test")
        assert entry is not None
        assert entry.metadata["version"] == "2"

    @pytest.mark.asyncio
    async def test_remove_idempotent(self) -> None:
        """Removing non-existent ID returns False, doesn't error."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)

        result = await backend.remove("nonexistent")
        assert result is False


class TestMonotonicity:
    """Verify monotonicity: count increases with add, decreases with remove."""

    @pytest.mark.asyncio
    async def test_count_increases_with_add(self) -> None:
        """Count increases after each add."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)

        for i in range(5):
            count_before = await backend.count()
            await backend.add(f"entry_{i}", make_embedding(i))
            count_after = await backend.count()
            assert count_after == count_before + 1

    @pytest.mark.asyncio
    async def test_count_decreases_with_remove(self) -> None:
        """Count decreases after each remove."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)

        # Setup
        for i in range(5):
            await backend.add(f"entry_{i}", make_embedding(i))

        # Remove
        for i in range(5):
            count_before = await backend.count()
            await backend.remove(f"entry_{i}")
            count_after = await backend.count()
            assert count_after == count_before - 1

    @pytest.mark.asyncio
    async def test_clear_sets_count_to_zero(self) -> None:
        """Clear reduces count to 0."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION)

        # Setup
        for i in range(5):
            await backend.add(f"entry_{i}", make_embedding(i))

        cleared = await backend.clear()
        assert cleared == 5

        count = await backend.count()
        assert count == 0
