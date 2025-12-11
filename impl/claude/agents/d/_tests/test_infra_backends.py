"""
Tests for D-gent Infrastructure Backends.

Tests InstanceDBVectorBackend, InstanceDBRelationalBackend, and CortexAdapter.
"""

import pytest
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Mock the instance_db imports for testing
import sys

# Create mock modules
mock_interfaces = MagicMock()
mock_nervous = MagicMock()


@dataclass
class MockVectorSearchResult:
    id: str
    distance: float
    metadata: dict[str, Any]


@dataclass
class MockSignal:
    signal_type: str
    data: dict[str, Any]
    timestamp: str = ""
    instance_id: str | None = None
    project_hash: str | None = None


mock_interfaces.VectorSearchResult = MockVectorSearchResult
mock_interfaces.IRelationalStore = MagicMock()
mock_interfaces.IVectorStore = MagicMock()
mock_nervous.Signal = MockSignal

sys.modules["protocols.cli.instance_db.interfaces"] = mock_interfaces
sys.modules["protocols.cli.instance_db.nervous"] = mock_nervous

# Now import the module under test
from ..infra_backends import (
    ContentHash,
    VectorMetadata,
    InstanceDBVectorBackend,
    InstanceDBVectorBackendConfig,
    InstanceDBRelationalBackend,
    CortexAdapter,
    NullEmbeddingProvider,
    create_vector_backend,
    create_relational_backend,
    create_cortex_adapter,
)


# ==============================================================================
# ContentHash Tests
# ==============================================================================


class TestContentHash:
    """Tests for ContentHash."""

    def test_compute_basic(self):
        """Compute hash for simple dict."""
        data = {"key": "value"}
        hash1 = ContentHash.compute(data)

        assert hash1.algorithm == "sha256"
        assert len(hash1.hash_value) == 16  # Truncated to 16 chars
        assert hash1.computed_at is not None

    def test_compute_deterministic(self):
        """Same data produces same hash."""
        data = {"key": "value", "count": 42}

        hash1 = ContentHash.compute(data)
        hash2 = ContentHash.compute(data)

        assert hash1.hash_value == hash2.hash_value

    def test_compute_different_data(self):
        """Different data produces different hash."""
        hash1 = ContentHash.compute({"a": 1})
        hash2 = ContentHash.compute({"a": 2})

        assert hash1.hash_value != hash2.hash_value

    def test_compute_order_independent(self):
        """Key order doesn't affect hash (sorted keys)."""
        hash1 = ContentHash.compute({"a": 1, "b": 2})
        hash2 = ContentHash.compute({"b": 2, "a": 1})

        assert hash1.hash_value == hash2.hash_value

    def test_compute_nested(self):
        """Handles nested dicts."""
        data = {"outer": {"inner": "value"}}
        hash1 = ContentHash.compute(data)

        assert hash1.hash_value is not None


# ==============================================================================
# VectorMetadata Tests
# ==============================================================================


class TestVectorMetadata:
    """Tests for VectorMetadata."""

    def test_to_dict(self):
        """Convert to dict for storage."""
        metadata = VectorMetadata(
            relational_id="shape-001",
            content_hash="abc123",
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00",
            table="shapes",
            extra={"custom": "field"},
        )

        d = metadata.to_dict()

        assert d["relational_id"] == "shape-001"
        assert d["content_hash"] == "abc123"
        assert d["table"] == "shapes"
        assert d["custom"] == "field"

    def test_from_dict(self):
        """Create from stored dict."""
        d = {
            "relational_id": "shape-002",
            "content_hash": "def456",
            "created_at": "2025-01-01",
            "updated_at": "2025-01-02",
            "table": "memories",
            "extra_field": "extra_value",
        }

        metadata = VectorMetadata.from_dict(d)

        assert metadata.relational_id == "shape-002"
        assert metadata.content_hash == "def456"
        assert metadata.table == "memories"
        assert metadata.extra["extra_field"] == "extra_value"

    def test_roundtrip(self):
        """to_dict and from_dict are inverse."""
        original = VectorMetadata(
            relational_id="test-123",
            content_hash="hash123",
            created_at="2025-01-01",
            updated_at="2025-01-02",
            table="test_table",
        )

        d = original.to_dict()
        restored = VectorMetadata.from_dict(d)

        assert restored.relational_id == original.relational_id
        assert restored.content_hash == original.content_hash
        assert restored.table == original.table


# ==============================================================================
# NullEmbeddingProvider Tests
# ==============================================================================


class TestNullEmbeddingProvider:
    """Tests for NullEmbeddingProvider."""

    def test_dimensions(self):
        """Returns configured dimensions."""
        provider = NullEmbeddingProvider(dimensions=512)
        assert provider.dimensions == 512

    def test_embed_returns_zeros(self):
        """Embed returns zero vector."""
        provider = NullEmbeddingProvider(dimensions=384)
        vector = provider.embed("test text")

        assert len(vector) == 384
        assert all(v == 0.0 for v in vector)

    def test_embed_different_text_same_vector(self):
        """Different text produces same zero vector."""
        provider = NullEmbeddingProvider()
        v1 = provider.embed("text one")
        v2 = provider.embed("text two")

        assert v1 == v2


# ==============================================================================
# InstanceDBVectorBackendConfig Tests
# ==============================================================================


class TestInstanceDBVectorBackendConfig:
    """Tests for InstanceDBVectorBackendConfig."""

    def test_defaults(self):
        """Default configuration values."""
        config = InstanceDBVectorBackendConfig()

        assert config.table == "shapes"
        assert config.id_column == "id"
        assert config.auto_heal_ghosts is True
        assert config.flag_stale_on_recall is True

    def test_custom_values(self):
        """Custom configuration values."""
        config = InstanceDBVectorBackendConfig(
            table="memories",
            auto_heal_ghosts=False,
        )

        assert config.table == "memories"
        assert config.auto_heal_ghosts is False


# ==============================================================================
# InstanceDBVectorBackend Tests
# ==============================================================================


class TestInstanceDBVectorBackend:
    """Tests for InstanceDBVectorBackend."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = AsyncMock()
        store.dimensions = 384
        store.upsert = AsyncMock()
        store.search = AsyncMock(return_value=[])
        store.delete = AsyncMock(return_value=True)
        store.count = AsyncMock(return_value=0)
        return store

    @pytest.fixture
    def mock_relational_store(self):
        """Create mock relational store."""
        store = AsyncMock()
        store.fetch_all = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def backend(self, mock_vector_store, mock_relational_store):
        """Create backend with mocks."""
        return InstanceDBVectorBackend(
            vector_store=mock_vector_store,
            relational_store=mock_relational_store,
        )

    def test_dimensions(self, backend, mock_vector_store):
        """Returns vector store dimensions."""
        assert backend.dimensions == 384

    @pytest.mark.asyncio
    async def test_upsert(self, backend, mock_vector_store):
        """Upsert stores vector with metadata."""
        content = {"type": "insight", "text": "test"}

        metadata = await backend.upsert(
            id="test-001",
            vector=[0.1, 0.2, 0.3],
            content=content,
        )

        assert metadata.relational_id == "test-001"
        assert metadata.content_hash is not None
        mock_vector_store.upsert.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_no_coherency(self, backend, mock_vector_store):
        """Search without coherency check."""
        mock_vector_store.search.return_value = [
            MockVectorSearchResult(
                id="result-001",
                distance=0.1,
                metadata={"relational_id": "result-001"},
            )
        ]

        results = await backend.search(
            query_vector=[0.1, 0.2, 0.3],
            limit=10,
            validate_coherency=False,
        )

        assert len(results) == 1
        assert results[0].id == "result-001"

    @pytest.mark.asyncio
    async def test_search_with_coherency_valid(
        self, backend, mock_vector_store, mock_relational_store
    ):
        """Search with coherency - valid rows."""
        content_hash = ContentHash.compute({"data": "test"}).hash_value

        mock_vector_store.search.return_value = [
            MockVectorSearchResult(
                id="result-001",
                distance=0.1,
                metadata={
                    "relational_id": "result-001",
                    "content_hash": content_hash,
                    "created_at": "",
                    "updated_at": "",
                    "table": "shapes",
                },
            )
        ]

        mock_relational_store.fetch_all.return_value = [
            {"id": "result-001", "data": "test"}
        ]

        results = await backend.search(
            query_vector=[0.1, 0.2, 0.3],
            limit=10,
            validate_coherency=True,
        )

        assert len(results) == 1
        assert results[0].id == "result-001"

    @pytest.mark.asyncio
    async def test_search_detects_ghost(
        self, backend, mock_vector_store, mock_relational_store
    ):
        """Search detects and heals ghost memory."""
        mock_vector_store.search.return_value = [
            MockVectorSearchResult(
                id="ghost-001",
                distance=0.1,
                metadata={
                    "relational_id": "ghost-001",
                    "content_hash": "hash",
                    "created_at": "",
                    "updated_at": "",
                    "table": "shapes",
                },
            )
        ]

        # No matching row - this is a ghost
        mock_relational_store.fetch_all.return_value = []

        results = await backend.search(
            query_vector=[0.1, 0.2, 0.3],
            limit=10,
            validate_coherency=True,
        )

        # Ghost should be filtered out
        assert len(results) == 0

        # Ghost should be healed
        mock_vector_store.delete.assert_called_with("ghost-001")

    @pytest.mark.asyncio
    async def test_delete(self, backend, mock_vector_store):
        """Delete removes vector."""
        result = await backend.delete("test-001")

        assert result is True
        mock_vector_store.delete.assert_called_with("test-001")

    def test_stats(self, backend):
        """Stats returns backend statistics."""
        stats = backend.stats()

        assert "ghosts_healed" in stats
        assert "stale_flagged" in stats
        assert "config" in stats


# ==============================================================================
# InstanceDBRelationalBackend Tests
# ==============================================================================


class TestInstanceDBRelationalBackend:
    """Tests for InstanceDBRelationalBackend."""

    @pytest.fixture
    def mock_store(self):
        """Create mock relational store."""
        store = AsyncMock()
        store.execute = AsyncMock(return_value=1)
        store.fetch_one = AsyncMock(return_value=None)
        store.fetch_all = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def backend(self, mock_store):
        """Create backend with mock."""
        return InstanceDBRelationalBackend(
            store=mock_store,
            key="test-agent",
        )

    @pytest.mark.asyncio
    async def test_save(self, backend, mock_store):
        """Save stores state with versioning."""
        # First call for version query, second returns None for prune
        mock_store.fetch_one.side_effect = [
            {"next_version": 1},  # For version query
            None,  # For prune history (no old versions)
        ]

        await backend.save({"count": 42})

        # Should have called execute for table creation and insert
        assert mock_store.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_load_not_found(self, backend, mock_store):
        """Load raises error when no state exists."""
        mock_store.fetch_one.return_value = None

        from ..errors import StateNotFoundError

        with pytest.raises(StateNotFoundError):
            await backend.load()

    @pytest.mark.asyncio
    async def test_load_returns_state(self, backend, mock_store):
        """Load returns deserialized state."""
        # Skip table initialization and mock the load query
        backend._initialized = True
        mock_store.fetch_one.return_value = {"state": '{"count": 42}'}

        state = await backend.load()

        assert state == {"count": 42}

    @pytest.mark.asyncio
    async def test_history(self, backend, mock_store):
        """History returns past states."""
        mock_store.fetch_all.return_value = [
            {"state": '{"count": 3}'},  # Current
            {"state": '{"count": 2}'},
            {"state": '{"count": 1}'},
        ]

        backend._initialized = True
        history = await backend.history(limit=2)

        assert len(history) == 2
        assert history[0] == {"count": 2}
        assert history[1] == {"count": 1}

    @pytest.mark.asyncio
    async def test_exists(self, backend, mock_store):
        """Exists checks if state exists."""
        mock_store.fetch_one.return_value = {"1": 1}

        backend._initialized = True
        result = await backend.exists()

        assert result is True


# ==============================================================================
# CortexAdapter Tests
# ==============================================================================


class TestCortexAdapter:
    """Tests for CortexAdapter."""

    @pytest.fixture
    def mock_relational(self):
        """Create mock relational store."""
        store = AsyncMock()
        store.execute = AsyncMock(return_value=1)
        store.fetch_one = AsyncMock(return_value=None)
        store.fetch_all = AsyncMock(return_value=[])
        return store

    @pytest.fixture
    def mock_vector(self):
        """Create mock vector store."""
        store = AsyncMock()
        store.dimensions = 384
        store.upsert = AsyncMock()
        store.search = AsyncMock(return_value=[])
        store.delete = AsyncMock(return_value=True)
        store.count = AsyncMock(return_value=0)
        return store

    @pytest.fixture
    def adapter(self, mock_relational, mock_vector):
        """Create adapter with mocks."""
        return CortexAdapter(
            relational_store=mock_relational,
            vector_store=mock_vector,
        )

    def test_has_semantic_true(self, adapter):
        """has_semantic True when vector store provided."""
        assert adapter.has_semantic is True

    def test_has_semantic_false(self, mock_relational):
        """has_semantic False when no vector store."""
        adapter = CortexAdapter(relational_store=mock_relational)
        assert adapter.has_semantic is False

    def test_create_agent(self, adapter):
        """create_agent returns InstanceDBRelationalBackend."""
        agent = adapter.create_agent("test-key")

        assert isinstance(agent, InstanceDBRelationalBackend)

    @pytest.mark.asyncio
    async def test_store(self, adapter, mock_relational, mock_vector):
        """Store saves to both hemispheres."""
        await adapter.store("test-001", {"type": "insight"})

        mock_relational.execute.assert_called()
        mock_vector.upsert.assert_called()

    @pytest.mark.asyncio
    async def test_fetch(self, adapter, mock_relational):
        """Fetch retrieves from relational store."""
        mock_relational.fetch_one.return_value = {
            "id": "test-001",
            "data": '{"type": "insight"}',
        }

        result = await adapter.fetch("test-001")

        assert result is not None
        assert result["id"] == "test-001"

    @pytest.mark.asyncio
    async def test_delete(self, adapter, mock_relational, mock_vector):
        """Delete removes from both hemispheres."""
        result = await adapter.delete("test-001")

        assert result is True
        mock_relational.execute.assert_called()
        mock_vector.delete.assert_called()

    def test_stats(self, adapter):
        """Stats returns adapter statistics."""
        stats = adapter.stats()

        assert "has_semantic" in stats
        assert stats["has_semantic"] is True


# ==============================================================================
# Factory Function Tests
# ==============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.fixture
    def mock_vector_store(self):
        store = AsyncMock()
        store.dimensions = 384
        return store

    @pytest.fixture
    def mock_relational_store(self):
        return AsyncMock()

    def test_create_vector_backend(self, mock_vector_store, mock_relational_store):
        """create_vector_backend creates backend."""
        backend = create_vector_backend(
            vector_store=mock_vector_store,
            relational_store=mock_relational_store,
            table="custom_table",
        )

        assert isinstance(backend, InstanceDBVectorBackend)
        assert backend._config.table == "custom_table"

    def test_create_relational_backend(self, mock_relational_store):
        """create_relational_backend creates backend."""
        backend = create_relational_backend(
            store=mock_relational_store,
            key="my-agent",
            max_history=50,
        )

        assert isinstance(backend, InstanceDBRelationalBackend)
        assert backend._config.max_history == 50

    def test_create_cortex_adapter(self, mock_relational_store, mock_vector_store):
        """create_cortex_adapter creates adapter."""
        adapter = create_cortex_adapter(
            relational_store=mock_relational_store,
            vector_store=mock_vector_store,
        )

        assert isinstance(adapter, CortexAdapter)
        assert adapter.has_semantic is True
