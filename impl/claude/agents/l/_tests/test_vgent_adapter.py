"""
Tests for L-gent V-gent adapter (Phase 9).

Tests cover:
- VgentToLgentAdapter: V-gent → L-gent compatibility
- LgentToVgentAdapter: L-gent → V-gent compatibility
- VectorCatalog with V-gent injection
- Migration utilities
"""

import pytest
from agents.l.semantic import SimpleEmbedder
from agents.l.types import Catalog, CatalogEntry, EntityType, Status
from agents.l.vgent_adapter import (
    LgentToVgentAdapter,
    VgentToLgentAdapter,
    check_vgent_available,
    create_vgent_adapter,
)

# Import V-gent for testing
try:
    from agents.v import (
        DistanceMetric,
        Embedding,
        MemoryVectorBackend,
        SearchResult,
        VgentProtocol,
        create_vgent,
    )

    VGENT_AVAILABLE = True
except ImportError:
    VGENT_AVAILABLE = False


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestVgentToLgentAdapter:
    """Tests for adapting V-gent to L-gent VectorBackend."""

    @pytest.fixture
    def memory_vgent(self) -> "VgentProtocol":
        """Create a memory V-gent backend."""
        return MemoryVectorBackend(dimension=128)

    @pytest.fixture
    def adapter(self, memory_vgent: "VgentProtocol") -> VgentToLgentAdapter:
        """Create adapter wrapping memory backend."""
        return VgentToLgentAdapter(memory_vgent)

    @pytest.mark.asyncio
    async def test_dimension_property(self, adapter: VgentToLgentAdapter) -> None:
        """Test dimension is passed through."""
        assert adapter.dimension == 128

    @pytest.mark.asyncio
    async def test_add_and_search(self, adapter: VgentToLgentAdapter) -> None:
        """Test basic add and search via adapter."""
        # Use vectors that are clearly different
        vec1 = [1.0] + [0.0] * 127
        vec2 = [0.5] + [0.5] + [0.0] * 126  # Different direction

        await adapter.add("id1", vec1, {"type": "agent", "name": "Agent1"})
        await adapter.add("id2", vec2, {"type": "contract"})

        # Search should work - id1 should be closer to vec1
        results = await adapter.search(vec1, limit=2)

        assert len(results) == 2
        assert results[0].id == "id1"
        # The first result should be more similar than the second
        assert results[0].similarity >= results[1].similarity

    @pytest.mark.asyncio
    async def test_add_batch(self, adapter: VgentToLgentAdapter) -> None:
        """Test batch add via adapter."""
        ids = ["id1", "id2", "id3"]
        vectors = [[0.1] * 128, [0.2] * 128, [0.3] * 128]
        metadata = [{"a": "1"}, {"a": "2"}, {"a": "3"}]

        await adapter.add_batch(ids, vectors, metadata)

        count = await adapter.count()
        assert count == 3

    @pytest.mark.asyncio
    async def test_remove(self, adapter: VgentToLgentAdapter) -> None:
        """Test remove via adapter."""
        vec = [0.5] * 128
        await adapter.add("id1", vec, {})
        await adapter.add("id2", vec, {})

        await adapter.remove("id1")

        count = await adapter.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_clear(self, adapter: VgentToLgentAdapter) -> None:
        """Test clear via adapter."""
        vec = [0.5] * 128
        await adapter.add("id1", vec, {})
        await adapter.add("id2", vec, {})

        await adapter.clear()

        count = await adapter.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_metadata_conversion(self, adapter: VgentToLgentAdapter) -> None:
        """Test metadata values are converted to strings."""
        vec = [0.5] * 128
        # Pass non-string metadata values
        await adapter.add("id1", vec, {"count": 5, "active": True})

        results = await adapter.search(vec, limit=1)
        assert results[0].metadata["count"] == "5"
        assert results[0].metadata["active"] == "True"

    @pytest.mark.asyncio
    async def test_threshold_filtering(self, adapter: VgentToLgentAdapter) -> None:
        """Test search with similarity threshold."""
        vec1 = [1.0] + [0.0] * 127
        vec2 = [0.0] + [1.0] + [0.0] * 126  # Orthogonal

        await adapter.add("similar", vec1, {})
        await adapter.add("different", vec2, {})

        # High threshold should filter out dissimilar
        results = await adapter.search(vec1, limit=10, threshold=0.9)
        assert len(results) == 1
        assert results[0].id == "similar"


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestLgentToVgentAdapter:
    """Tests for adapting L-gent VectorBackend to V-gent protocol."""

    @pytest.fixture
    def lgent_backend(self) -> "MemoryVectorBackend":
        """Create a memory V-gent as L-gent style backend for testing."""
        # We need a real L-gent backend to test; use V-gent memory as proxy
        # since we don't want ChromaDB/FAISS dependency
        return MemoryVectorBackend(dimension=128)

    @pytest.fixture
    def adapter(self, lgent_backend: "MemoryVectorBackend") -> LgentToVgentAdapter:
        """Create adapter wrapping L-gent backend."""
        # Create a VgentToLgent then wrap back to test both directions
        lgent_adapter = VgentToLgentAdapter(lgent_backend)
        return LgentToVgentAdapter(lgent_adapter)

    @pytest.mark.asyncio
    async def test_dimension_property(self, adapter: LgentToVgentAdapter) -> None:
        """Test dimension is passed through."""
        assert adapter.dimension == 128

    @pytest.mark.asyncio
    async def test_metric_property(self, adapter: LgentToVgentAdapter) -> None:
        """Test metric property."""
        assert adapter.metric == DistanceMetric.COSINE

    @pytest.mark.asyncio
    async def test_add_and_get(self, adapter: LgentToVgentAdapter) -> None:
        """Test add and get via adapter."""
        vec = [0.1] * 128

        await adapter.add("id1", vec, {"key": "value"})

        entry = await adapter.get("id1")
        assert entry is not None
        assert entry.id == "id1"
        assert entry.metadata["key"] == "value"

    @pytest.mark.asyncio
    async def test_exists(self, adapter: LgentToVgentAdapter) -> None:
        """Test exists check."""
        vec = [0.1] * 128

        assert not await adapter.exists("id1")

        await adapter.add("id1", vec, {})

        assert await adapter.exists("id1")

    @pytest.mark.asyncio
    async def test_remove_returns_bool(self, adapter: LgentToVgentAdapter) -> None:
        """Test remove returns True/False."""
        vec = [0.1] * 128

        # Remove non-existent
        assert not await adapter.remove("id1")

        await adapter.add("id1", vec, {})

        # Remove existing
        assert await adapter.remove("id1")

    @pytest.mark.asyncio
    async def test_clear_returns_count(self, adapter: LgentToVgentAdapter) -> None:
        """Test clear returns count of removed."""
        vec = [0.1] * 128

        await adapter.add("id1", vec, {})
        await adapter.add("id2", vec, {})

        count = await adapter.clear()
        assert count == 2

    @pytest.mark.asyncio
    async def test_search_returns_vgent_results(
        self, adapter: LgentToVgentAdapter
    ) -> None:
        """Test search returns V-gent SearchResult."""
        vec = [0.1] * 128

        await adapter.add("id1", vec, {"type": "test"})

        results = await adapter.search(vec, limit=1)

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].id == "id1"

    @pytest.mark.asyncio
    async def test_add_with_embedding_type(self, adapter: LgentToVgentAdapter) -> None:
        """Test add accepts Embedding type."""
        embedding = Embedding.from_list([0.1] * 128, source="test")

        await adapter.add("id1", embedding, {"key": "value"})

        entry = await adapter.get("id1")
        assert entry is not None


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestVgentAvailabilityCheck:
    """Tests for V-gent availability checking."""

    def test_check_vgent_available(self) -> None:
        """Test availability check."""
        result = check_vgent_available()
        assert result.available is True
        assert result.reason is None


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestCreateVgentAdapter:
    """Tests for create_vgent_adapter factory."""

    @pytest.mark.asyncio
    async def test_create_with_existing_vgent(self) -> None:
        """Test creating adapter with existing V-gent."""
        vgent = MemoryVectorBackend(dimension=128)
        adapter = create_vgent_adapter(vgent=vgent)

        assert adapter.dimension == 128

    @pytest.mark.asyncio
    async def test_create_default(self) -> None:
        """Test creating adapter with default V-gent."""
        adapter = create_vgent_adapter(dimension=256)

        assert adapter.dimension == 256


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestVectorCatalogWithVgent:
    """Tests for VectorCatalog with V-gent injection."""

    @pytest.fixture
    def embedder(self) -> SimpleEmbedder:
        """Create simple embedder."""
        return SimpleEmbedder(dimension=128)

    @pytest.fixture
    def sample_entry(self) -> CatalogEntry:
        """Create sample catalog entry."""
        return CatalogEntry(
            id="test-entry",
            name="Test Agent",
            description="A test agent for processing data",
            entity_type=EntityType.AGENT,
            status=Status.ACTIVE,
            version="1.0.0",
        )

    @pytest.mark.asyncio
    async def test_create_with_vgent(self, embedder: SimpleEmbedder) -> None:
        """Test VectorCatalog.create_with_vgent()."""
        from agents.l.vector_db import VectorCatalog

        vgent = MemoryVectorBackend(dimension=embedder.dimension)

        catalog = await VectorCatalog.create_with_vgent(
            embedder=embedder,
            vgent=vgent,
        )

        assert catalog is not None
        assert catalog._vgent is vgent

    @pytest.mark.asyncio
    async def test_register_and_search_with_vgent(
        self, embedder: SimpleEmbedder, sample_entry: CatalogEntry
    ) -> None:
        """Test registering and searching with V-gent backend."""
        from agents.l.vector_db import VectorCatalog

        vgent = MemoryVectorBackend(dimension=embedder.dimension)

        catalog = await VectorCatalog.create_with_vgent(
            embedder=embedder,
            vgent=vgent,
        )

        # Fit embedder with sample text first
        await embedder.fit([sample_entry.name, sample_entry.description])

        # Register entry
        await catalog.register(sample_entry)

        # Search should find it
        results = await catalog.search("test agent", threshold=0.0)

        assert len(results) >= 1
        assert any(r.id == sample_entry.id for r in results)

    @pytest.mark.asyncio
    async def test_sync_state_with_vgent(
        self, embedder: SimpleEmbedder, sample_entry: CatalogEntry
    ) -> None:
        """Test sync_state works with V-gent backend."""
        from agents.l.vector_db import VectorCatalog

        vgent = MemoryVectorBackend(dimension=embedder.dimension)

        catalog = await VectorCatalog.create_with_vgent(
            embedder=embedder,
            vgent=vgent,
        )

        await embedder.fit([sample_entry.name])
        await catalog.register(sample_entry)

        state = await catalog.sync_state()

        assert state.total_entries == 1
        assert state.indexed_entries == 1

    @pytest.mark.asyncio
    async def test_delete_with_vgent(
        self, embedder: SimpleEmbedder, sample_entry: CatalogEntry
    ) -> None:
        """Test delete works with V-gent backend."""
        from agents.l.vector_db import VectorCatalog

        vgent = MemoryVectorBackend(dimension=embedder.dimension)

        catalog = await VectorCatalog.create_with_vgent(
            embedder=embedder,
            vgent=vgent,
        )

        await embedder.fit([sample_entry.name])
        await catalog.register(sample_entry)

        # Delete
        deleted = await catalog.delete(sample_entry.id)
        assert deleted is True

        # Should be gone
        entry = await catalog.get(sample_entry.id)
        assert entry is None

        # Vector index should be updated
        count = await vgent.count()
        assert count == 0


@pytest.mark.skipif(not VGENT_AVAILABLE, reason="V-gent not available")
class TestRoundTripAdapters:
    """Tests for round-trip adapter conversions."""

    @pytest.mark.asyncio
    async def test_vgent_to_lgent_to_vgent(self) -> None:
        """Test V-gent → L-gent → V-gent round trip."""
        # Original V-gent
        original = MemoryVectorBackend(dimension=128)

        # Wrap as L-gent
        lgent_adapter = VgentToLgentAdapter(original)

        # Wrap back as V-gent
        vgent_adapter = LgentToVgentAdapter(lgent_adapter)

        # Add via adapter
        vec = [0.1] * 128
        await vgent_adapter.add("id1", vec, {"key": "value"})

        # Should be in original
        count = await original.count()
        assert count == 1

        # Search via adapter
        results = await vgent_adapter.search(vec, limit=1)
        assert len(results) == 1
        assert results[0].id == "id1"
