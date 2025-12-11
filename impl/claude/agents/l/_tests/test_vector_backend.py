"""
Tests for L-gent vector database backends (Phase 6).

Tests cover:
- ChromaDBBackend (if available)
- FAISSBackend (if available)
- VectorBackend protocol compliance
- create_vector_backend

Tests are written to gracefully handle missing dependencies.
"""

from pathlib import Path

import pytest
from agents.l.vector_backend import (
    CHROMADB_AVAILABLE,
    FAISS_AVAILABLE,
    create_vector_backend,
)

if CHROMADB_AVAILABLE:
    from agents.l.vector_backend import ChromaDBBackend

if FAISS_AVAILABLE:
    from agents.l.vector_backend import FAISSBackend


# ============================================================================
# ChromaDBBackend Tests
# ============================================================================


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
class TestChromaDBBackend:
    """Tests for ChromaDBBackend."""

    @pytest.mark.asyncio
    async def test_add_and_search(self, tmp_path: Path) -> None:
        """Test basic add and search."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test"
        )

        # Add entries
        vec1 = [0.1] * 128
        vec2 = [0.2] * 128
        await backend.add("id1", vec1, {"type": "agent", "name": "Agent1"})
        await backend.add("id2", vec2, {"type": "contract", "name": "Contract1"})

        # Search
        results = await backend.search(vec1, limit=2)

        assert len(results) == 2
        assert results[0].id == "id1"  # Closest match
        assert isinstance(results[0].similarity, float)

    @pytest.mark.asyncio
    async def test_dimension_property(self, tmp_path: Path) -> None:
        """Test dimension property."""
        backend = ChromaDBBackend(path=str(tmp_path / "chroma"), dimension=256)
        assert backend.dimension == 256

    @pytest.mark.asyncio
    async def test_metadata_filtering(self, tmp_path: Path) -> None:
        """Test search with metadata filters."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test2"
        )

        vec = [0.5] * 128
        await backend.add("agent1", vec, {"type": "agent"})
        await backend.add("contract1", vec, {"type": "contract"})

        # Search with filter
        results = await backend.search(vec, limit=10, filters={"type": "agent"})

        assert len(results) == 1
        assert results[0].id == "agent1"

    @pytest.mark.asyncio
    async def test_threshold_filtering(self, tmp_path: Path) -> None:
        """Test search with similarity threshold."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test3"
        )

        vec1 = [1.0] + [0.0] * 127
        vec2 = [0.0] + [1.0] + [0.0] * 126  # Orthogonal to vec1

        await backend.add("similar", vec1, {})
        await backend.add("different", vec2, {})

        # Search with high threshold (should only return similar)
        results = await backend.search(vec1, limit=10, threshold=0.9)

        assert len(results) == 1
        assert results[0].id == "similar"

    @pytest.mark.asyncio
    async def test_remove(self, tmp_path: Path) -> None:
        """Test removing entries."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test4"
        )

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Remove one
        await backend.remove("id1")

        # Search should only return id2
        results = await backend.search(vec, limit=10)
        assert len(results) == 1
        assert results[0].id == "id2"

    @pytest.mark.asyncio
    async def test_clear(self, tmp_path: Path) -> None:
        """Test clearing all entries."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test5"
        )

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Clear
        await backend.clear()

        # Count should be 0
        count = await backend.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count(self, tmp_path: Path) -> None:
        """Test counting entries."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test6"
        )

        assert await backend.count() == 0

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        assert await backend.count() == 1

        await backend.add("id2", vec, {})
        assert await backend.count() == 2

    @pytest.mark.asyncio
    async def test_add_batch(self, tmp_path: Path) -> None:
        """Test batch adding."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="test7"
        )

        ids = ["id1", "id2", "id3"]
        vectors = [[0.1] * 128, [0.2] * 128, [0.3] * 128]
        metadata = [{"name": "A"}, {"name": "B"}, {"name": "C"}]

        await backend.add_batch(ids, vectors, metadata)

        assert await backend.count() == 3

    @pytest.mark.asyncio
    async def test_persistence(self, tmp_path: Path) -> None:
        """Test that data persists across instances."""
        path = str(tmp_path / "chroma")
        collection = "test_persist"

        # First instance
        backend1 = ChromaDBBackend(path=path, dimension=128, collection_name=collection)
        vec = [0.5] * 128
        await backend1.add("id1", vec, {"name": "Test"})

        # Second instance (should load from disk)
        backend2 = ChromaDBBackend(path=path, dimension=128, collection_name=collection)
        count = await backend2.count()
        assert count == 1

        results = await backend2.search(vec, limit=1)
        assert results[0].id == "id1"


# ============================================================================
# FAISSBackend Tests
# ============================================================================


@pytest.mark.skipif(not FAISS_AVAILABLE, reason="faiss not installed")
class TestFAISSBackend:
    """Tests for FAISSBackend."""

    @pytest.mark.asyncio
    async def test_add_and_search(self) -> None:
        """Test basic add and search."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        # Add entries
        vec1 = [0.1] * 128
        vec2 = [0.2] * 128
        await backend.add("id1", vec1, {"type": "agent"})
        await backend.add("id2", vec2, {"type": "contract"})

        # Search
        results = await backend.search(vec1, limit=2)

        assert len(results) == 2
        assert results[0].id == "id1"  # Closest match

    @pytest.mark.asyncio
    async def test_dimension_property(self) -> None:
        """Test dimension property."""
        backend = FAISSBackend(dimension=256, index_type="flat")
        assert backend.dimension == 256

    @pytest.mark.asyncio
    async def test_metadata_filtering(self) -> None:
        """Test search with metadata filters."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        vec = [0.5] * 128
        await backend.add("agent1", vec, {"type": "agent"})
        await backend.add("contract1", vec, {"type": "contract"})

        # Search with filter
        results = await backend.search(vec, limit=10, filters={"type": "agent"})

        assert len(results) == 1
        assert results[0].id == "agent1"

    @pytest.mark.asyncio
    async def test_threshold_filtering(self) -> None:
        """Test search with similarity threshold."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        vec1 = [1.0] + [0.0] * 127
        vec2 = [0.0] + [1.0] + [0.0] * 126  # Orthogonal

        await backend.add("similar", vec1, {})
        await backend.add("different", vec2, {})

        # Search with high threshold
        results = await backend.search(vec1, limit=10, threshold=0.9)

        assert len(results) == 1
        assert results[0].id == "similar"

    @pytest.mark.asyncio
    async def test_remove(self) -> None:
        """Test removing entries."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Remove one (note: FAISS doesn't actually remove vectors, just metadata)
        await backend.remove("id1")

        # Search should only return id2
        results = await backend.search(vec, limit=10)
        assert len(results) == 1
        assert results[0].id == "id2"

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        """Test clearing all entries."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Clear
        await backend.clear()

        # Count should be 0
        count = await backend.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count(self) -> None:
        """Test counting entries."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        assert await backend.count() == 0

        vec = [0.5] * 128
        await backend.add("id1", vec, {})
        assert await backend.count() == 1

        await backend.add("id2", vec, {})
        assert await backend.count() == 2

    @pytest.mark.asyncio
    async def test_add_batch(self) -> None:
        """Test batch adding."""
        backend = FAISSBackend(dimension=128, index_type="flat")

        ids = ["id1", "id2", "id3"]
        vectors = [[0.1] * 128, [0.2] * 128, [0.3] * 128]
        metadata = [{"name": "A"}, {"name": "B"}, {"name": "C"}]

        await backend.add_batch(ids, vectors, metadata)

        assert await backend.count() == 3

    @pytest.mark.asyncio
    async def test_persistence(self, tmp_path: Path) -> None:
        """Test saving and loading index."""
        save_path = str(tmp_path / "faiss.index")

        # First instance
        backend1 = FAISSBackend(dimension=128, index_type="flat", save_path=save_path)
        vec = [0.5] * 128
        await backend1.add("id1", vec, {"name": "Test"})

        # Second instance (should load from disk)
        backend2 = FAISSBackend(dimension=128, index_type="flat", save_path=save_path)
        count = await backend2.count()
        assert count == 1

        results = await backend2.search(vec, limit=1)
        assert results[0].id == "id1"

    @pytest.mark.asyncio
    async def test_hnsw_index(self) -> None:
        """Test HNSW index type."""
        backend = FAISSBackend(dimension=128, index_type="hnsw")

        vec = [0.5] * 128
        await backend.add("id1", vec, {})

        results = await backend.search(vec, limit=1)
        assert len(results) == 1
        assert results[0].id == "id1"


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestCreateVectorBackend:
    """Tests for create_vector_backend."""

    @pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
    def test_auto_selects_chroma(self, tmp_path: Path) -> None:
        """Test auto selection prefers ChromaDB."""
        backend = create_vector_backend(
            dimension=128, backend_type="auto", path=str(tmp_path / "chroma")
        )
        assert isinstance(backend, ChromaDBBackend)

    @pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
    def test_explicit_chroma(self, tmp_path: Path) -> None:
        """Test explicit ChromaDB selection."""
        backend = create_vector_backend(
            dimension=128, backend_type="chroma", path=str(tmp_path / "chroma")
        )
        assert isinstance(backend, ChromaDBBackend)

    @pytest.mark.skipif(not FAISS_AVAILABLE, reason="faiss not installed")
    def test_explicit_faiss(self, tmp_path: Path) -> None:
        """Test explicit FAISS selection."""
        backend = create_vector_backend(
            dimension=128, backend_type="faiss", path=str(tmp_path / "faiss.index")
        )
        assert isinstance(backend, FAISSBackend)

    def test_unknown_backend_raises(self) -> None:
        """Test that unknown backend type raises error."""
        with pytest.raises(ValueError, match="Unknown backend type"):
            create_vector_backend(dimension=128, backend_type="invalid")

    @pytest.mark.skipif(
        CHROMADB_AVAILABLE or FAISS_AVAILABLE,
        reason="Test requires no backends available",
    )
    def test_no_backends_available(self) -> None:
        """Test error when no backends available."""
        with pytest.raises(ImportError, match="No vector backend available"):
            create_vector_backend(dimension=128, backend_type="auto")


# ============================================================================
# Integration Tests
# ============================================================================


@pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="chromadb not installed")
class TestVectorBackendIntegration:
    """Integration tests using ChromaDB backend."""

    @pytest.mark.asyncio
    async def test_large_catalog_performance(self, tmp_path: Path) -> None:
        """Test performance with larger catalog (100 entries)."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="perf_test"
        )

        # Add 100 entries
        import random

        for i in range(100):
            vec = [random.random() for _ in range(128)]
            await backend.add(f"id_{i}", vec, {"index": i})

        # Search should still be fast
        query = [0.5] * 128
        results = await backend.search(query, limit=10)

        assert len(results) <= 10
        assert all(isinstance(r.similarity, float) for r in results)

    @pytest.mark.asyncio
    async def test_update_existing_entry(self, tmp_path: Path) -> None:
        """Test updating an existing entry."""
        backend = ChromaDBBackend(
            path=str(tmp_path / "chroma"), dimension=128, collection_name="update_test"
        )

        vec1 = [0.1] * 128
        vec2 = [0.9] * 128

        # Add
        await backend.add("id1", vec1, {"version": 1})

        # Update
        await backend.add("id1", vec2, {"version": 2})

        # Should only have one entry
        count = await backend.count()
        assert count == 1

        # Search with vec2 should return id1
        results = await backend.search(vec2, limit=1)
        assert results[0].id == "id1"
        assert results[0].metadata["version"] == "2"  # ChromaDB converts to string
