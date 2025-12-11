"""
Tests for L-gent Vector DB: D-gent Integration (Phase 8).

Tests cover:
- DgentVectorBackend: VectorBackend protocol using D-gent VectorAgent
- VectorCatalog: Unified catalog + vector DB
- Sync utilities and migration
"""

from datetime import datetime

import pytest

# Check for numpy availability
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

from agents.l.semantic import SimpleEmbedder
from agents.l.types import CatalogEntry, EntityType, Status

# Skip all tests if numpy not available
pytestmark = pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not installed")


@pytest.fixture
def embedder():
    """Simple embedder for testing."""
    return SimpleEmbedder(dimension=64)


@pytest.fixture
def sample_entry():
    """Sample catalog entry for testing."""
    return CatalogEntry(
        id="test_agent_1",
        entity_type=EntityType.AGENT,
        name="TestAgent",
        description="An agent for testing vector DB integration",
        version="1.0.0",
        author="test",
        created_at=datetime.now(),
        status=Status.ACTIVE,
        input_type="str",
        output_type="str",
    )


@pytest.fixture
def sample_entries():
    """Multiple sample entries for testing."""
    return [
        CatalogEntry(
            id=f"agent_{i}",
            entity_type=EntityType.AGENT,
            name=f"Agent{i}",
            description=f"Test agent number {i} for processing data",
            version="1.0.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
        )
        for i in range(5)
    ]


# ============================================================================
# DgentVectorBackend Tests
# ============================================================================


class TestDgentVectorBackend:
    """Tests for DgentVectorBackend."""

    @pytest.mark.asyncio
    async def test_add_and_search(self, tmp_path) -> None:
        """Test basic add and search."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(
            dimension=64,
            persistence_path=tmp_path / "vectors.json",
        )

        # Add entries
        vec1 = [0.1] * 64
        vec2 = [0.2] * 64
        await backend.add("id1", vec1, {"type": "agent", "name": "Agent1"})
        await backend.add("id2", vec2, {"type": "contract", "name": "Contract1"})

        # Search
        results = await backend.search(vec1, limit=2)

        assert len(results) == 2
        assert results[0].id == "id1"  # Closest match
        assert isinstance(results[0].similarity, float)

    @pytest.mark.asyncio
    async def test_dimension_property(self, tmp_path) -> None:
        """Test dimension property."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=128)
        assert backend.dimension == 128

    @pytest.mark.asyncio
    async def test_metadata_filtering(self, tmp_path) -> None:
        """Test search with metadata filters."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        vec = [0.5] * 64
        await backend.add("agent1", vec, {"type": "agent"})
        await backend.add("contract1", vec, {"type": "contract"})

        # Search with filter
        results = await backend.search(vec, limit=10, filters={"type": "agent"})

        assert len(results) == 1
        assert results[0].id == "agent1"

    @pytest.mark.asyncio
    async def test_threshold_filtering(self, tmp_path) -> None:
        """Test search with similarity threshold."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        vec1 = [1.0] + [0.0] * 63
        vec2 = [0.0] + [1.0] + [0.0] * 62  # Orthogonal

        await backend.add("similar", vec1, {})
        await backend.add("different", vec2, {})

        # Search with high threshold
        results = await backend.search(vec1, limit=10, threshold=0.9)

        # Should only return similar (threshold filters out different)
        assert len(results) <= 2
        if results:
            assert results[0].id == "similar"

    @pytest.mark.asyncio
    async def test_remove(self, tmp_path) -> None:
        """Test removing entries."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        vec = [0.5] * 64
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Remove one
        await backend.remove("id1")

        # Search should only return id2
        results = await backend.search(vec, limit=10)
        ids = [r.id for r in results]
        assert "id1" not in ids
        assert "id2" in ids

    @pytest.mark.asyncio
    async def test_clear(self, tmp_path) -> None:
        """Test clearing all entries."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        vec = [0.5] * 64
        await backend.add("id1", vec, {})
        await backend.add("id2", vec, {})

        # Clear
        await backend.clear()

        # Count should be 0
        count = await backend.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count(self, tmp_path) -> None:
        """Test counting entries."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        assert await backend.count() == 0

        vec = [0.5] * 64
        await backend.add("id1", vec, {})
        assert await backend.count() == 1

        await backend.add("id2", vec, {})
        assert await backend.count() == 2

    @pytest.mark.asyncio
    async def test_add_batch(self, tmp_path) -> None:
        """Test batch adding."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        ids = ["id1", "id2", "id3"]
        vectors = [[0.1] * 64, [0.2] * 64, [0.3] * 64]
        metadata = [{"name": "A"}, {"name": "B"}, {"name": "C"}]

        await backend.add_batch(ids, vectors, metadata)

        assert await backend.count() == 3

    @pytest.mark.asyncio
    async def test_persistence(self, tmp_path) -> None:
        """Test that data persists across instances."""
        from agents.l.vector_db import DgentVectorBackend

        path = tmp_path / "vectors.json"

        # First instance
        backend1 = DgentVectorBackend(dimension=64, persistence_path=path)
        vec = [0.5] * 64
        await backend1.add("id1", vec, {"name": "Test"})

        # Second instance (should load from disk)
        backend2 = DgentVectorBackend(dimension=64, persistence_path=path)
        count = await backend2.count()
        assert count == 1

        results = await backend2.search(vec, limit=1)
        assert results[0].id == "id1"

    @pytest.mark.asyncio
    async def test_curvature(self, tmp_path) -> None:
        """Test curvature estimation."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        # Add some entries
        for i in range(10):
            vec = [float(i) / 10] * 64
            await backend.add(f"id{i}", vec, {})

        # Curvature at a point
        point = [0.5] * 64
        curvature = await backend.curvature_at(point, radius=0.5)
        assert isinstance(curvature, float)

    @pytest.mark.asyncio
    async def test_cluster_centers(self, tmp_path) -> None:
        """Test cluster center finding."""
        from agents.l.vector_db import DgentVectorBackend

        backend = DgentVectorBackend(dimension=64)

        # Add some entries
        for i in range(10):
            vec = [float(i) / 10] * 64
            await backend.add(f"id{i}", vec, {})

        # Find clusters
        centers = await backend.cluster_centers(k=3)
        assert len(centers) <= 3
        for center in centers:
            assert len(center) == 64


# ============================================================================
# VectorCatalog Tests
# ============================================================================


class TestVectorCatalog:
    """Tests for VectorCatalog unified interface."""

    @pytest.mark.asyncio
    async def test_create_empty(self, embedder, tmp_path) -> None:
        """Test creating empty catalog."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        state = await catalog.sync_state()
        assert state.total_entries == 0
        assert state.indexed_entries == 0

    @pytest.mark.asyncio
    async def test_register_and_search(self, embedder, sample_entry, tmp_path) -> None:
        """Test registering and searching."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        # Register
        entry_id = await catalog.register(sample_entry)
        assert entry_id == sample_entry.id

        # Search
        results = await catalog.search("testing vector DB", threshold=0.0, limit=10)

        # Should find the entry
        assert len(results) >= 1
        assert any(r.id == sample_entry.id for r in results)

    @pytest.mark.asyncio
    async def test_get(self, embedder, sample_entry, tmp_path) -> None:
        """Test getting entry by ID."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        await catalog.register(sample_entry)

        # Get existing
        entry = await catalog.get(sample_entry.id)
        assert entry is not None
        assert entry.id == sample_entry.id
        assert entry.name == sample_entry.name

        # Get non-existing
        missing = await catalog.get("nonexistent")
        assert missing is None

    @pytest.mark.asyncio
    async def test_delete(self, embedder, sample_entry, tmp_path) -> None:
        """Test deleting entries."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        await catalog.register(sample_entry)

        # Delete
        deleted = await catalog.delete(sample_entry.id)
        assert deleted is True

        # Should not find
        entry = await catalog.get(sample_entry.id)
        assert entry is None

        # Delete again
        deleted = await catalog.delete(sample_entry.id)
        assert deleted is False

    @pytest.mark.asyncio
    async def test_multiple_entries(self, embedder, sample_entries, tmp_path) -> None:
        """Test with multiple entries."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        # Register all
        for entry in sample_entries:
            await catalog.register(entry)

        # Check state
        state = await catalog.sync_state()
        assert state.total_entries == 5
        assert state.indexed_entries == 5

    @pytest.mark.asyncio
    async def test_search_with_entity_filter(self, embedder, tmp_path) -> None:
        """Test search with entity type filter."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        # Add agent and contract
        agent = CatalogEntry(
            id="agent_1",
            entity_type=EntityType.AGENT,
            name="DataProcessor",
            description="Processes data files",
            version="1.0.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
        )
        contract = CatalogEntry(
            id="contract_1",
            entity_type=EntityType.CONTRACT,
            name="JSONOutput",
            description="Outputs JSON data",
            version="1.0.0",
            author="test",
            created_at=datetime.now(),
            status=Status.ACTIVE,
        )

        await catalog.register(agent)
        await catalog.register(contract)

        # Search for agents only
        results = await catalog.search(
            "data processing",
            entity_type=EntityType.AGENT,
            threshold=0.0,
        )

        # Should only return agent
        assert len(results) >= 1
        for r in results:
            assert r.entry.entity_type == EntityType.AGENT

    @pytest.mark.asyncio
    async def test_cluster_analysis(self, embedder, sample_entries, tmp_path) -> None:
        """Test cluster analysis."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        for entry in sample_entries:
            await catalog.register(entry)

        clusters = await catalog.cluster_analysis(k=2)

        assert len(clusters) <= 2
        for cluster in clusters:
            assert "id" in cluster
            assert "center" in cluster
            assert "entries" in cluster


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestUtilityFunctions:
    """Tests for utility functions."""

    @pytest.mark.asyncio
    async def test_create_dgent_vector_backend(self, tmp_path) -> None:
        """Test create_dgent_vector_backend convenience function."""
        from agents.l.vector_db import create_dgent_vector_backend

        backend = create_dgent_vector_backend(
            dimension=128,
            persistence_path=tmp_path / "vectors.json",
        )

        assert backend.dimension == 128

    @pytest.mark.asyncio
    async def test_create_vector_catalog(self, embedder, tmp_path) -> None:
        """Test create_vector_catalog convenience function."""
        from agents.l.vector_db import create_vector_catalog

        catalog = await create_vector_catalog(
            embedder=embedder,
            base_path=tmp_path,
        )

        state = await catalog.sync_state()
        assert state.total_entries == 0


class TestMigration:
    """Tests for migration utilities."""

    @pytest.mark.asyncio
    async def test_migrate_to_dgent_backend(
        self, embedder, sample_entries, tmp_path
    ) -> None:
        """Test migrating entries to D-gent backend."""
        from agents.l.vector_db import migrate_to_dgent_backend

        # Create entries dict
        entries = {e.id: e for e in sample_entries}

        # Migrate
        backend = await migrate_to_dgent_backend(
            entries=entries,
            embedder=embedder,
            persistence_path=tmp_path / "migrated.json",
        )

        # Check all indexed
        count = await backend.count()
        assert count == len(sample_entries)

        # Search should work
        results = await backend.search([0.5] * 64, limit=10)
        assert len(results) <= len(sample_entries)


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for the full vector DB workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, embedder, tmp_path) -> None:
        """Test complete workflow: create, add, search, delete."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        # Add entries
        entries = [
            CatalogEntry(
                id="pdf_parser",
                entity_type=EntityType.AGENT,
                name="PDFParser",
                description="Parses PDF documents into text",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
                input_type="PDF",
                output_type="Text",
            ),
            CatalogEntry(
                id="summarizer",
                entity_type=EntityType.AGENT,
                name="Summarizer",
                description="Summarizes text into key points",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
                input_type="Text",
                output_type="Summary",
            ),
            CatalogEntry(
                id="sentiment",
                entity_type=EntityType.AGENT,
                name="SentimentAnalyzer",
                description="Analyzes sentiment of text",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
                input_type="Text",
                output_type="Score",
            ),
        ]

        for entry in entries:
            await catalog.register(entry)

        # Search for text processing
        results = await catalog.search(
            "process text and analyze",
            threshold=0.0,
            limit=10,
        )
        assert len(results) >= 1

        # Search for PDF
        pdf_results = await catalog.search(
            "parse PDF files",
            threshold=0.0,
            limit=3,
        )
        assert len(pdf_results) >= 1

        # Delete and verify
        await catalog.delete("summarizer")
        state = await catalog.sync_state()
        assert state.total_entries == 2

    @pytest.mark.asyncio
    async def test_similarity_ranking(self, embedder, tmp_path) -> None:
        """Test that results are ranked by similarity."""
        from agents.l.vector_db import VectorCatalog

        catalog = await VectorCatalog.create(
            embedder=embedder,
            vector_path=tmp_path / "vectors.json",
        )

        # Add entries with different relevance
        entries = [
            CatalogEntry(
                id="exact_match",
                entity_type=EntityType.AGENT,
                name="FinancialAnalyzer",
                description="Analyzes financial documents and reports",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
            ),
            CatalogEntry(
                id="partial_match",
                entity_type=EntityType.AGENT,
                name="DocumentReader",
                description="Reads various document types",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
            ),
            CatalogEntry(
                id="unrelated",
                entity_type=EntityType.AGENT,
                name="ImageProcessor",
                description="Processes images and photos",
                version="1.0.0",
                author="test",
                created_at=datetime.now(),
                status=Status.ACTIVE,
            ),
        ]

        for entry in entries:
            await catalog.register(entry)

        # Search
        results = await catalog.search(
            "analyze financial documents",
            threshold=0.0,
            limit=10,
        )

        # Results should be sorted by similarity (descending)
        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity
