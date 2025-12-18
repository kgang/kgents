"""
DgentVectorBackend Tests: Comprehensive tests for D-gent-backed vector storage.

Tests cover:
1. Basic CRUD operations (add, get, remove, clear)
2. Batch operations
3. Search functionality
4. Metadata filtering
5. Index persistence and loading
6. Serialization/deserialization
7. Edge cases and error handling
"""

from __future__ import annotations

from typing import AsyncIterator

import pytest

from agents.d import Datum, MemoryBackend as DgentMemoryBackend

from ..backends.dgent import DgentVectorBackend
from ..types import DistanceMetric, Embedding
from .conftest import (
    TEST_DIMENSION,
    make_embedding,
    make_similar_embedding,
    make_unit_vector,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def dgent_memory() -> DgentMemoryBackend:
    """Fresh D-gent memory backend."""
    return DgentMemoryBackend()


@pytest.fixture
def dgent_backend(dgent_memory: DgentMemoryBackend) -> DgentVectorBackend:
    """Fresh D-gent-backed vector storage with cosine metric."""
    return DgentVectorBackend(
        dgent=dgent_memory,
        dimension=TEST_DIMENSION,
        metric=DistanceMetric.COSINE,
        namespace="test_vectors",
    )


@pytest.fixture
async def populated_dgent_backend(
    dgent_backend: DgentVectorBackend,
) -> AsyncIterator[DgentVectorBackend]:
    """
    D-gent backend pre-populated with sample entries.

    Yields a backend with 10 entries, then clears after test.
    """
    for i in range(10):
        await dgent_backend.add(
            f"entry_{i}",
            make_embedding(i),
            {
                "type": "test",
                "index": str(i),
                "category": "even" if i % 2 == 0 else "odd",
            },
        )

    yield dgent_backend

    await dgent_backend.clear()


# =============================================================================
# Basic CRUD Tests
# =============================================================================


class TestDgentBackendBasics:
    """Test basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_backend(self, dgent_memory: DgentMemoryBackend) -> None:
        """Create backend with specified dimension and metric."""
        backend = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=768,
            metric=DistanceMetric.EUCLIDEAN,
            namespace="custom",
        )
        assert backend.dimension == 768
        assert backend.metric == DistanceMetric.EUCLIDEAN
        assert backend.namespace == "custom"

    @pytest.mark.asyncio
    async def test_default_metric_is_cosine(self, dgent_memory: DgentMemoryBackend) -> None:
        """Default metric is cosine."""
        backend = DgentVectorBackend(dgent=dgent_memory, dimension=8)
        assert backend.metric == DistanceMetric.COSINE

    @pytest.mark.asyncio
    async def test_default_namespace(self, dgent_memory: DgentMemoryBackend) -> None:
        """Default namespace is 'vectors'."""
        backend = DgentVectorBackend(dgent=dgent_memory, dimension=8)
        assert backend.namespace == "vectors"

    @pytest.mark.asyncio
    async def test_add_and_get(self, dgent_backend: DgentVectorBackend) -> None:
        """Add vector and retrieve it."""
        emb = make_embedding(1)
        await dgent_backend.add("test", emb, {"tag": "sample"})

        entry = await dgent_backend.get("test")
        assert entry is not None
        assert entry.id == "test"
        assert entry.embedding.vector == emb.vector
        assert entry.metadata["tag"] == "sample"

    @pytest.mark.asyncio
    async def test_add_with_raw_vector(self, dgent_backend: DgentVectorBackend) -> None:
        """Add using raw list instead of Embedding."""
        raw = list(make_unit_vector(1))
        await dgent_backend.add("test", raw)

        entry = await dgent_backend.get("test")
        assert entry is not None
        # Compare with approximate equality for floats
        for a, b in zip(entry.embedding.vector, raw):
            assert abs(a - b) < 1e-6

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, dgent_backend: DgentVectorBackend) -> None:
        """Get nonexistent ID returns None."""
        entry = await dgent_backend.get("nonexistent")
        assert entry is None

    @pytest.mark.asyncio
    async def test_remove(self, dgent_backend: DgentVectorBackend) -> None:
        """Remove existing entry."""
        await dgent_backend.add("test", make_embedding(1))

        result = await dgent_backend.remove("test")
        assert result is True

        entry = await dgent_backend.get("test")
        assert entry is None

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, dgent_backend: DgentVectorBackend) -> None:
        """Remove nonexistent returns False."""
        result = await dgent_backend.remove("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear(self, dgent_backend: DgentVectorBackend) -> None:
        """Clear removes all entries and returns count."""
        for i in range(5):
            await dgent_backend.add(f"entry_{i}", make_embedding(i))

        count = await dgent_backend.clear()
        assert count == 5

        remaining = await dgent_backend.count()
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_exists(self, dgent_backend: DgentVectorBackend) -> None:
        """Exists returns True for existing, False for nonexistent."""
        await dgent_backend.add("test", make_embedding(1))

        assert await dgent_backend.exists("test") is True
        assert await dgent_backend.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_count(self, dgent_backend: DgentVectorBackend) -> None:
        """Count returns correct number of entries."""
        assert await dgent_backend.count() == 0

        await dgent_backend.add("a", make_embedding(1))
        assert await dgent_backend.count() == 1

        await dgent_backend.add("b", make_embedding(2))
        assert await dgent_backend.count() == 2


# =============================================================================
# Batch Operations
# =============================================================================


class TestBatchOperations:
    """Test batch add operations."""

    @pytest.mark.asyncio
    async def test_add_batch(self, dgent_backend: DgentVectorBackend) -> None:
        """Add multiple entries in batch."""
        entries = [
            ("entry_1", make_embedding(1), {"type": "a"}),
            ("entry_2", make_embedding(2), {"type": "b"}),
            ("entry_3", make_embedding(3), {"type": "c"}),
        ]

        ids = await dgent_backend.add_batch(entries)  # type: ignore[arg-type]

        assert ids == ["entry_1", "entry_2", "entry_3"]
        assert await dgent_backend.count() == 3

    @pytest.mark.asyncio
    async def test_add_batch_with_raw_vectors(self, dgent_backend: DgentVectorBackend) -> None:
        """Batch add with raw vectors."""
        entries = [
            ("entry_1", list(make_unit_vector(1)), None),
            ("entry_2", list(make_unit_vector(2)), None),
        ]

        ids = await dgent_backend.add_batch(entries)  # type: ignore[arg-type]
        assert len(ids) == 2

    @pytest.mark.asyncio
    async def test_add_batch_empty(self, dgent_backend: DgentVectorBackend) -> None:
        """Batch add with empty list."""
        ids = await dgent_backend.add_batch([])
        assert ids == []
        assert await dgent_backend.count() == 0


# =============================================================================
# Search Tests
# =============================================================================


class TestSearch:
    """Test search functionality."""

    @pytest.mark.asyncio
    async def test_search_empty_index(self, dgent_backend: DgentVectorBackend) -> None:
        """Search on empty index returns empty list."""
        query = make_embedding(1)
        results = await dgent_backend.search(query)
        assert results == []

    @pytest.mark.asyncio
    async def test_search_finds_exact_match(self, dgent_backend: DgentVectorBackend) -> None:
        """Search finds exact match with similarity ~1.0."""
        emb = make_embedding(1)
        await dgent_backend.add("test", emb)

        results = await dgent_backend.search(emb, limit=1)

        assert len(results) == 1
        assert results[0].id == "test"
        assert results[0].similarity == pytest.approx(1.0, abs=1e-5)

    @pytest.mark.asyncio
    async def test_search_with_limit(self, populated_dgent_backend: DgentVectorBackend) -> None:
        """Search respects limit parameter."""
        query = make_embedding(0)

        results = await populated_dgent_backend.search(query, limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_sorted_by_similarity(self, dgent_backend: DgentVectorBackend) -> None:
        """Results are sorted by similarity (highest first)."""
        base = make_embedding(1)
        similar = make_similar_embedding(base, noise=0.1, seed=42)
        different = make_embedding(99)

        await dgent_backend.add("base", base)
        await dgent_backend.add("similar", similar)
        await dgent_backend.add("different", different)

        results = await dgent_backend.search(base, limit=3)

        assert results[0].id == "base"
        assert results[0].similarity > results[1].similarity
        # Similar should be second
        assert results[1].id == "similar"

    @pytest.mark.asyncio
    async def test_search_with_threshold(self, dgent_backend: DgentVectorBackend) -> None:
        """Search filters by similarity threshold."""
        base = make_embedding(1)
        similar = make_similar_embedding(base, noise=0.1)
        different = make_embedding(99)

        await dgent_backend.add("base", base)
        await dgent_backend.add("similar", similar)
        await dgent_backend.add("different", different)

        # High threshold should only return base
        results = await dgent_backend.search(base, threshold=0.99)
        assert len(results) == 1
        assert results[0].id == "base"

    @pytest.mark.asyncio
    async def test_search_with_raw_vector(self, dgent_backend: DgentVectorBackend) -> None:
        """Search with raw vector list."""
        raw = list(make_unit_vector(1))
        await dgent_backend.add("test", raw)

        results = await dgent_backend.search(raw)
        assert len(results) == 1
        assert results[0].id == "test"


# =============================================================================
# Metadata Filtering Tests
# =============================================================================


class TestMetadataFiltering:
    """Test metadata filter functionality."""

    @pytest.mark.asyncio
    async def test_search_with_single_filter(self, dgent_backend: DgentVectorBackend) -> None:
        """Filter results by single metadata key."""
        await dgent_backend.add("a", make_embedding(1), {"type": "foo"})
        await dgent_backend.add("b", make_embedding(2), {"type": "bar"})
        await dgent_backend.add("c", make_embedding(3), {"type": "foo"})

        results = await dgent_backend.search(make_embedding(1), filters={"type": "foo"})

        assert len(results) == 2
        assert all(r.metadata["type"] == "foo" for r in results)

    @pytest.mark.asyncio
    async def test_search_with_multiple_filters(self, dgent_backend: DgentVectorBackend) -> None:
        """Filter results by multiple metadata keys."""
        await dgent_backend.add("a", make_embedding(1), {"type": "foo", "status": "active"})
        await dgent_backend.add("b", make_embedding(2), {"type": "foo", "status": "inactive"})
        await dgent_backend.add("c", make_embedding(3), {"type": "bar", "status": "active"})

        results = await dgent_backend.search(
            make_embedding(1), filters={"type": "foo", "status": "active"}
        )

        assert len(results) == 1
        assert results[0].id == "a"

    @pytest.mark.asyncio
    async def test_search_filter_no_match(self, dgent_backend: DgentVectorBackend) -> None:
        """Filter with no matching entries returns empty."""
        await dgent_backend.add("a", make_embedding(1), {"type": "foo"})

        results = await dgent_backend.search(make_embedding(1), filters={"type": "nonexistent"})

        assert results == []


# =============================================================================
# Persistence Tests (D-gent Integration)
# =============================================================================


class TestPersistence:
    """Test D-gent persistence and index loading."""

    @pytest.mark.asyncio
    async def test_persists_to_dgent(self, dgent_memory: DgentMemoryBackend) -> None:
        """Vectors are stored in D-gent."""
        backend = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="persist_test",
        )

        await backend.add("doc1", make_embedding(1), {"author": "alice"})

        # Check D-gent has the datum
        datum = await dgent_memory.get("persist_test:doc1")
        assert datum is not None
        assert datum.metadata["author"] == "alice"
        assert datum.metadata["_dimension"] == str(TEST_DIMENSION)

    @pytest.mark.asyncio
    async def test_load_index_restores_vectors(self, dgent_memory: DgentMemoryBackend) -> None:
        """load_index() restores vectors from D-gent."""
        # Create first backend and add vectors
        backend1 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="load_test",
        )

        await backend1.add("doc1", make_embedding(1), {"tag": "first"})
        await backend1.add("doc2", make_embedding(2), {"tag": "second"})

        # Create new backend (simulates restart) and load index
        backend2 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="load_test",
        )

        # Before load, index is empty
        assert await backend2.count() == 0

        # Load index
        count = await backend2.load_index()
        assert count == 2

        # Verify vectors are restored
        entry1 = await backend2.get("doc1")
        assert entry1 is not None
        assert entry1.metadata["tag"] == "first"

        entry2 = await backend2.get("doc2")
        assert entry2 is not None
        assert entry2.metadata["tag"] == "second"

    @pytest.mark.asyncio
    async def test_load_index_returns_count(self, dgent_memory: DgentMemoryBackend) -> None:
        """load_index() returns number of vectors loaded."""
        backend = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="count_test",
        )

        # Add vectors directly to D-gent (simulating persisted data)
        for i in range(5):
            await backend.add(f"doc_{i}", make_embedding(i))

        # Create new backend and load
        backend2 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="count_test",
        )

        count = await backend2.load_index()
        assert count == 5

    @pytest.mark.asyncio
    async def test_search_after_load(self, dgent_memory: DgentMemoryBackend) -> None:
        """Search works correctly after load_index()."""
        # Create and populate first backend
        backend1 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="search_test",
        )

        base = make_embedding(1)
        await backend1.add("target", base, {"type": "important"})
        await backend1.add("other", make_embedding(99))

        # Create new backend and load
        backend2 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="search_test",
        )
        await backend2.load_index()

        # Search should find the target
        results = await backend2.search(base, limit=1)
        assert len(results) == 1
        assert results[0].id == "target"
        assert results[0].metadata["type"] == "important"

    @pytest.mark.asyncio
    async def test_namespace_isolation(self, dgent_memory: DgentMemoryBackend) -> None:
        """Different namespaces don't interfere."""
        backend_a = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="namespace_a",
        )
        backend_b = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="namespace_b",
        )

        await backend_a.add("doc1", make_embedding(1))
        await backend_b.add("doc1", make_embedding(2))
        await backend_b.add("doc2", make_embedding(3))

        assert await backend_a.count() == 1
        assert await backend_b.count() == 2

        # Loading one namespace doesn't affect another
        backend_a2 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="namespace_a",
        )
        count = await backend_a2.load_index()
        assert count == 1


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Test vector serialization/deserialization."""

    @pytest.mark.asyncio
    async def test_serialization_roundtrip(self, dgent_backend: DgentVectorBackend) -> None:
        """Vector survives serialization roundtrip."""
        original = make_unit_vector(42)

        serialized = dgent_backend._serialize_vector(original)
        deserialized = dgent_backend._deserialize_vector(serialized)

        # Float precision might vary slightly
        for a, b in zip(original, deserialized):
            assert abs(a - b) < 1e-6

    @pytest.mark.asyncio
    async def test_serialization_preserves_values(self, dgent_backend: DgentVectorBackend) -> None:
        """Known values serialize correctly."""
        vector = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)

        serialized = dgent_backend._serialize_vector(vector)
        assert len(serialized) == 8 * 4  # 8 floats * 4 bytes each

        deserialized = dgent_backend._deserialize_vector(serialized)
        for a, b in zip(vector, deserialized):
            assert abs(a - b) < 1e-6


# =============================================================================
# Dimension Validation Tests
# =============================================================================


class TestDimensionValidation:
    """Test dimension validation."""

    @pytest.mark.asyncio
    async def test_add_wrong_dimension_embedding(self, dgent_backend: DgentVectorBackend) -> None:
        """Adding embedding with wrong dimension raises."""
        wrong_dim = Embedding(
            vector=(0.1, 0.2, 0.3),  # 3 dimensions, backend expects TEST_DIMENSION
            dimension=3,
            source="test",
        )

        with pytest.raises(ValueError, match="dimension"):
            await dgent_backend.add("test", wrong_dim)

    @pytest.mark.asyncio
    async def test_add_wrong_dimension_list(self, dgent_backend: DgentVectorBackend) -> None:
        """Adding raw vector with wrong dimension raises."""
        wrong_dim = [0.1, 0.2, 0.3]  # 3 dimensions, backend expects TEST_DIMENSION

        with pytest.raises(ValueError, match="dimension"):
            await dgent_backend.add("test", wrong_dim)

    @pytest.mark.asyncio
    async def test_search_wrong_dimension(self, dgent_backend: DgentVectorBackend) -> None:
        """Search with wrong dimension raises."""
        await dgent_backend.add("test", make_embedding(1))

        wrong_dim = [0.1, 0.2, 0.3]  # Wrong dimension
        with pytest.raises(ValueError, match="dimension"):
            await dgent_backend.search(wrong_dim)


# =============================================================================
# All Metrics Tests
# =============================================================================


class TestAllMetrics:
    """Test backend works with all distance metrics."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "metric",
        [
            DistanceMetric.COSINE,
            DistanceMetric.EUCLIDEAN,
            DistanceMetric.DOT_PRODUCT,
            DistanceMetric.MANHATTAN,
        ],
    )
    async def test_search_with_metric(
        self, dgent_memory: DgentMemoryBackend, metric: DistanceMetric
    ) -> None:
        """Search works with all metrics."""
        backend = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            metric=metric,
            namespace=f"metric_{metric.value}",
        )

        base = make_embedding(1)
        await backend.add("base", base)
        await backend.add("other", make_embedding(99))

        results = await backend.search(base)

        assert len(results) == 2
        assert results[0].id == "base"
        assert results[0].similarity == pytest.approx(1.0, abs=1e-5)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_metadata(self, dgent_backend: DgentVectorBackend) -> None:
        """Add with None metadata defaults to empty dict."""
        await dgent_backend.add("test", make_embedding(1), None)

        entry = await dgent_backend.get("test")
        assert entry is not None
        assert entry.metadata == {}

    @pytest.mark.asyncio
    async def test_update_preserves_id(self, dgent_backend: DgentVectorBackend) -> None:
        """Updating entry preserves ID."""
        await dgent_backend.add("test", make_embedding(1))
        await dgent_backend.add("test", make_embedding(2))

        entry = await dgent_backend.get("test")
        assert entry is not None
        assert entry.id == "test"

    @pytest.mark.asyncio
    async def test_clear_empty_backend(self, dgent_backend: DgentVectorBackend) -> None:
        """Clear on empty backend returns 0."""
        count = await dgent_backend.clear()
        assert count == 0

    @pytest.mark.asyncio
    async def test_limit_larger_than_count(self, dgent_backend: DgentVectorBackend) -> None:
        """Limit larger than entry count returns all entries."""
        await dgent_backend.add("a", make_embedding(1))
        await dgent_backend.add("b", make_embedding(2))

        results = await dgent_backend.search(make_embedding(1), limit=100)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_repr(self, dgent_backend: DgentVectorBackend) -> None:
        """Backend has useful repr."""
        repr_str = repr(dgent_backend)
        assert "DgentVectorBackend" in repr_str
        assert str(TEST_DIMENSION) in repr_str
        assert "cosine" in repr_str
        assert "test_vectors" in repr_str

    @pytest.mark.asyncio
    async def test_load_index_skips_wrong_dimension(self, dgent_memory: DgentMemoryBackend) -> None:
        """load_index() skips vectors with wrong dimension."""
        # Store a vector with wrong dimension directly in D-gent
        import struct

        wrong_vector = (0.1, 0.2, 0.3)  # Only 3 dims
        wrong_content = struct.pack(f"{len(wrong_vector)}f", *wrong_vector)
        wrong_datum = Datum.create(
            content=wrong_content,
            id="dim_test:wrong",
            metadata={"_dimension": "3"},
        )
        await dgent_memory.put(wrong_datum)

        # Store a correct vector
        backend = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="dim_test",
        )
        await backend.add("correct", make_embedding(1))

        # Create new backend and load
        backend2 = DgentVectorBackend(
            dgent=dgent_memory,
            dimension=TEST_DIMENSION,
            namespace="dim_test",
        )
        count = await backend2.load_index()

        # Should only load the correct one
        assert count == 1
        assert await backend2.exists("correct") is True
        assert await backend2.exists("wrong") is False

    @pytest.mark.asyncio
    async def test_remove_also_removes_from_dgent(
        self,
        dgent_memory: DgentMemoryBackend,
        dgent_backend: DgentVectorBackend,
    ) -> None:
        """Remove also deletes from D-gent storage."""
        await dgent_backend.add("test", make_embedding(1))

        # Verify it's in D-gent
        datum = await dgent_memory.get("test_vectors:test")
        assert datum is not None

        # Remove
        await dgent_backend.remove("test")

        # Verify it's gone from D-gent
        datum = await dgent_memory.get("test_vectors:test")
        assert datum is None
