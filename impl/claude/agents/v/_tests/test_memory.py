"""
MemoryVectorBackend Tests: Comprehensive tests for in-memory vector storage.

Tests cover:
1. Basic CRUD operations (add, get, remove, clear)
2. Batch operations
3. Search functionality
4. Metadata filtering
5. Edge cases and error handling
6. Performance characteristics
"""

from __future__ import annotations

import pytest

from ..backends.memory import MemoryVectorBackend
from ..types import DistanceMetric, Embedding, SearchResult, VectorEntry
from .conftest import (
    TEST_DIMENSION,
    make_embedding,
    make_similar_embedding,
    make_unit_vector,
)


class TestMemoryBackendBasics:
    """Test basic CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_backend(self) -> None:
        """Create backend with specified dimension and metric."""
        backend = MemoryVectorBackend(dimension=768, metric=DistanceMetric.EUCLIDEAN)
        assert backend.dimension == 768
        assert backend.metric == DistanceMetric.EUCLIDEAN

    @pytest.mark.asyncio
    async def test_default_metric_is_cosine(self) -> None:
        """Default metric is cosine."""
        backend = MemoryVectorBackend(dimension=8)
        assert backend.metric == DistanceMetric.COSINE

    @pytest.mark.asyncio
    async def test_add_and_get(self, memory_backend: MemoryVectorBackend) -> None:
        """Add vector and retrieve it."""
        emb = make_embedding(1)
        await memory_backend.add("test", emb, {"tag": "sample"})

        entry = await memory_backend.get("test")
        assert entry is not None
        assert entry.id == "test"
        assert entry.embedding.vector == emb.vector
        assert entry.metadata["tag"] == "sample"

    @pytest.mark.asyncio
    async def test_add_with_raw_vector(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Add using raw list instead of Embedding."""
        raw = list(make_unit_vector(1))
        await memory_backend.add("test", raw)

        entry = await memory_backend.get("test")
        assert entry is not None
        assert entry.embedding.vector == tuple(raw)

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, memory_backend: MemoryVectorBackend) -> None:
        """Get nonexistent ID returns None."""
        entry = await memory_backend.get("nonexistent")
        assert entry is None

    @pytest.mark.asyncio
    async def test_remove(self, memory_backend: MemoryVectorBackend) -> None:
        """Remove existing entry."""
        await memory_backend.add("test", make_embedding(1))

        result = await memory_backend.remove("test")
        assert result is True

        entry = await memory_backend.get("test")
        assert entry is None

    @pytest.mark.asyncio
    async def test_remove_nonexistent(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Remove nonexistent returns False."""
        result = await memory_backend.remove("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear(self, memory_backend: MemoryVectorBackend) -> None:
        """Clear removes all entries and returns count."""
        for i in range(5):
            await memory_backend.add(f"entry_{i}", make_embedding(i))

        count = await memory_backend.clear()
        assert count == 5

        remaining = await memory_backend.count()
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_exists(self, memory_backend: MemoryVectorBackend) -> None:
        """Exists returns True for existing, False for nonexistent."""
        await memory_backend.add("test", make_embedding(1))

        assert await memory_backend.exists("test") is True
        assert await memory_backend.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_count(self, memory_backend: MemoryVectorBackend) -> None:
        """Count returns correct number of entries."""
        assert await memory_backend.count() == 0

        await memory_backend.add("a", make_embedding(1))
        assert await memory_backend.count() == 1

        await memory_backend.add("b", make_embedding(2))
        assert await memory_backend.count() == 2


class TestBatchOperations:
    """Test batch add operations."""

    @pytest.mark.asyncio
    async def test_add_batch(self, memory_backend: MemoryVectorBackend) -> None:
        """Add multiple entries in batch."""
        entries = [
            ("entry_1", make_embedding(1), {"type": "a"}),
            ("entry_2", make_embedding(2), {"type": "b"}),
            ("entry_3", make_embedding(3), {"type": "c"}),
        ]

        ids = await memory_backend.add_batch(entries)

        assert ids == ["entry_1", "entry_2", "entry_3"]
        assert await memory_backend.count() == 3

    @pytest.mark.asyncio
    async def test_add_batch_with_raw_vectors(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Batch add with raw vectors."""
        entries = [
            ("entry_1", list(make_unit_vector(1)), None),
            ("entry_2", list(make_unit_vector(2)), None),
        ]

        ids = await memory_backend.add_batch(entries)
        assert len(ids) == 2

    @pytest.mark.asyncio
    async def test_add_batch_empty(self, memory_backend: MemoryVectorBackend) -> None:
        """Batch add with empty list."""
        ids = await memory_backend.add_batch([])
        assert ids == []
        assert await memory_backend.count() == 0


class TestSearch:
    """Test search functionality."""

    @pytest.mark.asyncio
    async def test_search_empty_index(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Search on empty index returns empty list."""
        query = make_embedding(1)
        results = await memory_backend.search(query)
        assert results == []

    @pytest.mark.asyncio
    async def test_search_finds_exact_match(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Search finds exact match with similarity ~1.0."""
        emb = make_embedding(1)
        await memory_backend.add("test", emb)

        results = await memory_backend.search(emb, limit=1)

        assert len(results) == 1
        assert results[0].id == "test"
        assert results[0].similarity == pytest.approx(1.0, abs=1e-6)

    @pytest.mark.asyncio
    async def test_search_with_limit(
        self, populated_backend: MemoryVectorBackend
    ) -> None:
        """Search respects limit parameter."""
        query = make_embedding(0)

        results = await populated_backend.search(query, limit=3)
        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_sorted_by_similarity(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Results are sorted by similarity (highest first)."""
        base = make_embedding(1)
        similar = make_similar_embedding(base, noise=0.1, seed=42)
        different = make_embedding(99)

        await memory_backend.add("base", base)
        await memory_backend.add("similar", similar)
        await memory_backend.add("different", different)

        results = await memory_backend.search(base, limit=3)

        assert results[0].id == "base"
        assert results[0].similarity > results[1].similarity
        # Similar should be second
        assert results[1].id == "similar"

    @pytest.mark.asyncio
    async def test_search_with_threshold(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Search filters by similarity threshold."""
        base = make_embedding(1)
        similar = make_similar_embedding(base, noise=0.1)
        different = make_embedding(99)

        await memory_backend.add("base", base)
        await memory_backend.add("similar", similar)
        await memory_backend.add("different", different)

        # High threshold should only return base
        results = await memory_backend.search(base, threshold=0.99)
        assert len(results) == 1
        assert results[0].id == "base"

    @pytest.mark.asyncio
    async def test_search_with_raw_vector(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Search with raw vector list."""
        raw = list(make_unit_vector(1))
        await memory_backend.add("test", raw)

        results = await memory_backend.search(raw)
        assert len(results) == 1
        assert results[0].id == "test"


class TestMetadataFiltering:
    """Test metadata filter functionality."""

    @pytest.mark.asyncio
    async def test_search_with_single_filter(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Filter results by single metadata key."""
        await memory_backend.add("a", make_embedding(1), {"type": "foo"})
        await memory_backend.add("b", make_embedding(2), {"type": "bar"})
        await memory_backend.add("c", make_embedding(3), {"type": "foo"})

        results = await memory_backend.search(
            make_embedding(1), filters={"type": "foo"}
        )

        assert len(results) == 2
        assert all(r.metadata["type"] == "foo" for r in results)

    @pytest.mark.asyncio
    async def test_search_with_multiple_filters(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Filter results by multiple metadata keys."""
        await memory_backend.add(
            "a", make_embedding(1), {"type": "foo", "status": "active"}
        )
        await memory_backend.add(
            "b", make_embedding(2), {"type": "foo", "status": "inactive"}
        )
        await memory_backend.add(
            "c", make_embedding(3), {"type": "bar", "status": "active"}
        )

        results = await memory_backend.search(
            make_embedding(1), filters={"type": "foo", "status": "active"}
        )

        assert len(results) == 1
        assert results[0].id == "a"

    @pytest.mark.asyncio
    async def test_search_filter_no_match(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Filter with no matching entries returns empty."""
        await memory_backend.add("a", make_embedding(1), {"type": "foo"})

        results = await memory_backend.search(
            make_embedding(1), filters={"type": "nonexistent"}
        )

        assert results == []


class TestDimensionValidation:
    """Test dimension validation."""

    @pytest.mark.asyncio
    async def test_add_wrong_dimension_embedding(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Adding embedding with wrong dimension raises."""
        wrong_dim = Embedding(
            vector=(0.1, 0.2, 0.3),  # 3 dimensions, backend expects TEST_DIMENSION
            dimension=3,
            source="test",
        )

        with pytest.raises(ValueError, match="dimension"):
            await memory_backend.add("test", wrong_dim)

    @pytest.mark.asyncio
    async def test_add_wrong_dimension_list(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Adding raw vector with wrong dimension raises."""
        wrong_dim = [0.1, 0.2, 0.3]  # 3 dimensions, backend expects TEST_DIMENSION

        with pytest.raises(ValueError, match="dimension"):
            await memory_backend.add("test", wrong_dim)

    @pytest.mark.asyncio
    async def test_search_wrong_dimension(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Search with wrong dimension raises."""
        await memory_backend.add("test", make_embedding(1))

        wrong_dim = [0.1, 0.2, 0.3]  # Wrong dimension
        with pytest.raises(ValueError, match="dimension"):
            await memory_backend.search(wrong_dim)


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
    async def test_search_with_metric(self, metric: DistanceMetric) -> None:
        """Search works with all metrics."""
        backend = MemoryVectorBackend(dimension=TEST_DIMENSION, metric=metric)

        base = make_embedding(1)
        await backend.add("base", base)
        await backend.add("other", make_embedding(99))

        results = await backend.search(base)

        assert len(results) == 2
        assert results[0].id == "base"
        assert results[0].similarity == pytest.approx(1.0, abs=1e-6)


class TestSearchResultType:
    """Test SearchResult dataclass."""

    def test_search_result_comparison(self) -> None:
        """SearchResult sorts by similarity descending."""
        r1 = SearchResult(id="a", similarity=0.9, distance=0.1, metadata={})
        r2 = SearchResult(id="b", similarity=0.8, distance=0.2, metadata={})
        r3 = SearchResult(id="c", similarity=0.7, distance=0.3, metadata={})

        sorted_results = sorted([r3, r1, r2])

        # Higher similarity first
        assert sorted_results[0].id == "a"
        assert sorted_results[1].id == "b"
        assert sorted_results[2].id == "c"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_metadata(self, memory_backend: MemoryVectorBackend) -> None:
        """Add with None metadata defaults to empty dict."""
        await memory_backend.add("test", make_embedding(1), None)

        entry = await memory_backend.get("test")
        assert entry is not None
        assert entry.metadata == {}

    @pytest.mark.asyncio
    async def test_update_preserves_id(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Updating entry preserves ID."""
        await memory_backend.add("test", make_embedding(1))
        await memory_backend.add("test", make_embedding(2))

        entry = await memory_backend.get("test")
        assert entry is not None
        assert entry.id == "test"

    @pytest.mark.asyncio
    async def test_clear_empty_backend(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Clear on empty backend returns 0."""
        count = await memory_backend.clear()
        assert count == 0

    @pytest.mark.asyncio
    async def test_limit_larger_than_count(
        self, memory_backend: MemoryVectorBackend
    ) -> None:
        """Limit larger than entry count returns all entries."""
        await memory_backend.add("a", make_embedding(1))
        await memory_backend.add("b", make_embedding(2))

        results = await memory_backend.search(make_embedding(1), limit=100)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_repr(self, memory_backend: MemoryVectorBackend) -> None:
        """Backend has useful repr."""
        repr_str = repr(memory_backend)
        assert "MemoryVectorBackend" in repr_str
        assert str(TEST_DIMENSION) in repr_str
        assert "cosine" in repr_str
