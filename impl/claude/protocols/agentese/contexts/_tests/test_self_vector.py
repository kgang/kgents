"""
Tests for self.vector.* paths.

Tests verify:
1. VectorNode basic functionality
2. Affordance exposure
3. V-gent integration when available
4. Graceful fallback when V-gent not configured
5. CRUD operations: add, get, search, remove, clear
6. Introspection: count, exists, dimension, metric, status
"""

from __future__ import annotations

from typing import Any, cast

import pytest

from protocols.agentese.contexts.self_ import (
    SelfContextResolver,
    create_self_resolver,
)
from protocols.agentese.contexts.self_vector import (
    VECTOR_AFFORDANCES,
    VectorNode,
)

# === Test Fixtures ===


class MockDNA:
    """Mock DNA for testing."""

    def __init__(self, name: str = "test", archetype: str = "default") -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class MockUmwelt:
    """Mock Umwelt for testing."""

    def __init__(self, archetype: str = "default", name: str = "test") -> None:
        self.dna = MockDNA(name=name, archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}


@pytest.fixture
def observer() -> Any:
    """Default observer."""
    return MockUmwelt()


@pytest.fixture
def vector_node() -> VectorNode:
    """VectorNode without V-gent (fallback mode)."""
    return VectorNode()


@pytest.fixture
def resolver() -> SelfContextResolver:
    """Self context resolver."""
    return create_self_resolver()


# === Tests: Affordances ===


class TestAffordances:
    """Tests for affordance exposure."""

    def test_affordances_include_core_operations(self) -> None:
        """Core CRUD affordances are present."""
        assert "add" in VECTOR_AFFORDANCES
        assert "search" in VECTOR_AFFORDANCES
        assert "get" in VECTOR_AFFORDANCES
        assert "remove" in VECTOR_AFFORDANCES
        assert "clear" in VECTOR_AFFORDANCES

    def test_affordances_include_introspection(self) -> None:
        """Introspection affordances are present."""
        assert "count" in VECTOR_AFFORDANCES
        assert "exists" in VECTOR_AFFORDANCES
        assert "dimension" in VECTOR_AFFORDANCES
        assert "metric" in VECTOR_AFFORDANCES
        assert "status" in VECTOR_AFFORDANCES

    def test_node_returns_affordances(self, vector_node: VectorNode) -> None:
        """VectorNode returns all affordances for any archetype."""
        affordances = vector_node._get_affordances_for_archetype("default")
        assert affordances == VECTOR_AFFORDANCES


# === Tests: Resolution ===


class TestResolution:
    """Tests for self.vector.* path resolution."""

    def test_resolver_returns_vector_node(self, resolver: SelfContextResolver) -> None:
        """self.vector resolves to VectorNode."""
        node = resolver.resolve("vector", [])
        assert isinstance(node, VectorNode)

    def test_vector_node_handle(self, vector_node: VectorNode) -> None:
        """VectorNode has correct handle."""
        assert vector_node.handle == "self.vector"


# === Tests: Manifest ===


class TestManifest:
    """Tests for self.vector.manifest."""

    @pytest.mark.asyncio
    async def test_manifest_fallback_mode(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Manifest returns fallback state when V-gent not configured."""
        result = await vector_node.manifest(observer)

        assert result.summary == "Vector State (Fallback)"  # type: ignore[attr-defined]
        assert "Total vectors: 0" in result.content  # type: ignore[attr-defined]
        assert result.metadata["backend"] == "fallback"  # type: ignore[attr-defined]


# === Tests: Add Operation ===


class TestAddOperation:
    """Tests for self.vector.add."""

    @pytest.mark.asyncio
    async def test_add_requires_id(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add fails without id."""
        result = await vector_node._invoke_aspect(
            "add",
            observer,
            embedding=[0.1, 0.2, 0.3],
        )

        assert result.get("error") == "id is required"

    @pytest.mark.asyncio
    async def test_add_requires_embedding(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add fails without embedding."""
        result = await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
        )

        assert result.get("error") == "embedding is required"

    @pytest.mark.asyncio
    async def test_add_success_fallback(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add succeeds in fallback mode."""
        result = await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
        )

        assert result["status"] == "added"
        assert result["id"] == "doc1"
        assert result["backend"] == "fallback"

    @pytest.mark.asyncio
    async def test_add_with_metadata(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add with metadata works."""
        result = await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            metadata={"type": "test"},
        )

        assert result["status"] == "added"

        # Verify metadata stored
        get_result = await vector_node._invoke_aspect("get", observer, id="doc1")
        assert get_result["metadata"]["type"] == "test"


# === Tests: Add Batch Operation ===


class TestAddBatchOperation:
    """Tests for self.vector.add_batch."""

    @pytest.mark.asyncio
    async def test_add_batch_requires_entries(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add batch fails without entries."""
        result = await vector_node._invoke_aspect("add_batch", observer)

        assert result.get("error") == "entries is required"

    @pytest.mark.asyncio
    async def test_add_batch_success(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add batch succeeds."""
        entries = [
            ("doc1", [0.1, 0.2, 0.3], {"type": "a"}),
            ("doc2", [0.4, 0.5, 0.6], {"type": "b"}),
        ]
        result = await vector_node._invoke_aspect(
            "add_batch",
            observer,
            entries=entries,
        )

        assert result["status"] == "added"
        assert result["count"] == 2
        assert "doc1" in result["ids"]
        assert "doc2" in result["ids"]


# === Tests: Get Operation ===


class TestGetOperation:
    """Tests for self.vector.get."""

    @pytest.mark.asyncio
    async def test_get_requires_id(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Get fails without id."""
        result = await vector_node._invoke_aspect("get", observer)

        assert result.get("error") == "id is required"

    @pytest.mark.asyncio
    async def test_get_not_found(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Get returns not_found for missing vectors."""
        result = await vector_node._invoke_aspect("get", observer, id="missing")

        assert result["status"] == "not_found"
        assert result["id"] == "missing"

    @pytest.mark.asyncio
    async def test_get_success(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Get returns stored vector."""
        # Add first
        await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
            metadata={"key": "value"},
        )

        # Get
        result = await vector_node._invoke_aspect("get", observer, id="doc1")

        assert result["status"] == "found"
        assert result["id"] == "doc1"
        assert result["embedding"] == [0.1, 0.2, 0.3]
        assert result["metadata"]["key"] == "value"


# === Tests: Search Operation ===


class TestSearchOperation:
    """Tests for self.vector.search."""

    @pytest.mark.asyncio
    async def test_search_requires_query(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search fails without query."""
        result = await vector_node._invoke_aspect("search", observer)

        assert result.get("error") == "query is required"

    @pytest.mark.asyncio
    async def test_search_empty_index(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search returns empty for empty index."""
        result = await vector_node._invoke_aspect(
            "search",
            observer,
            query=[0.1, 0.2, 0.3],
        )

        assert result["status"] == "found"
        assert result["count"] == 0
        assert result["results"] == []

    @pytest.mark.asyncio
    async def test_search_finds_similar(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search finds similar vectors."""
        # Add vectors
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[1.0, 0.0, 0.0])
        await vector_node._invoke_aspect("add", observer, id="doc2", embedding=[0.0, 1.0, 0.0])
        await vector_node._invoke_aspect("add", observer, id="doc3", embedding=[0.9, 0.1, 0.0])

        # Search for similar to doc1
        result = await vector_node._invoke_aspect(
            "search",
            observer,
            query=[1.0, 0.0, 0.0],
            limit=2,
        )

        assert result["status"] == "found"
        assert result["count"] == 2
        # doc1 should be most similar (exact match)
        assert result["results"][0]["id"] == "doc1"
        # doc3 should be second (high similarity)
        assert result["results"][1]["id"] == "doc3"

    @pytest.mark.asyncio
    async def test_search_with_threshold(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search respects threshold."""
        # Add vectors
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[1.0, 0.0, 0.0])
        await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc2",
            embedding=[0.0, 1.0, 0.0],  # Orthogonal
        )

        # Search with high threshold
        result = await vector_node._invoke_aspect(
            "search",
            observer,
            query=[1.0, 0.0, 0.0],
            threshold=0.9,
        )

        # Only doc1 should pass threshold
        assert result["count"] == 1
        assert result["results"][0]["id"] == "doc1"

    @pytest.mark.asyncio
    async def test_search_with_filters(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search respects metadata filters."""
        # Add vectors with metadata
        await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
            embedding=[1.0, 0.0, 0.0],
            metadata={"type": "A"},
        )
        await vector_node._invoke_aspect(
            "add",
            observer,
            id="doc2",
            embedding=[0.9, 0.1, 0.0],
            metadata={"type": "B"},
        )

        # Search with filter
        result = await vector_node._invoke_aspect(
            "search",
            observer,
            query=[1.0, 0.0, 0.0],
            filters={"type": "B"},
        )

        assert result["count"] == 1
        assert result["results"][0]["id"] == "doc2"


# === Tests: Remove Operation ===


class TestRemoveOperation:
    """Tests for self.vector.remove."""

    @pytest.mark.asyncio
    async def test_remove_requires_id(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Remove fails without id."""
        result = await vector_node._invoke_aspect("remove", observer)

        assert result.get("error") == "id is required"

    @pytest.mark.asyncio
    async def test_remove_not_found(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Remove returns not_found for missing vectors."""
        result = await vector_node._invoke_aspect("remove", observer, id="missing")

        assert result["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_remove_success(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Remove deletes vector."""
        # Add first
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[0.1, 0.2, 0.3])

        # Remove
        result = await vector_node._invoke_aspect("remove", observer, id="doc1")

        assert result["status"] == "removed"
        assert result["id"] == "doc1"

        # Verify removed
        get_result = await vector_node._invoke_aspect("get", observer, id="doc1")
        assert get_result["status"] == "not_found"


# === Tests: Clear Operation ===


class TestClearOperation:
    """Tests for self.vector.clear."""

    @pytest.mark.asyncio
    async def test_clear_empty(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Clear on empty index returns 0."""
        result = await vector_node._invoke_aspect("clear", observer)

        assert result["status"] == "cleared"
        assert result["removed"] == 0

    @pytest.mark.asyncio
    async def test_clear_removes_all(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Clear removes all vectors."""
        # Add vectors
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[0.1, 0.2, 0.3])
        await vector_node._invoke_aspect("add", observer, id="doc2", embedding=[0.4, 0.5, 0.6])

        # Clear
        result = await vector_node._invoke_aspect("clear", observer)

        assert result["status"] == "cleared"
        assert result["removed"] == 2

        # Verify empty
        count_result = await vector_node._invoke_aspect("count", observer)
        assert count_result["count"] == 0


# === Tests: Count Operation ===


class TestCountOperation:
    """Tests for self.vector.count."""

    @pytest.mark.asyncio
    async def test_count_empty(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Count returns 0 for empty index."""
        result = await vector_node._invoke_aspect("count", observer)

        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_count_after_add(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Count reflects added vectors."""
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[0.1, 0.2, 0.3])
        await vector_node._invoke_aspect("add", observer, id="doc2", embedding=[0.4, 0.5, 0.6])

        result = await vector_node._invoke_aspect("count", observer)

        assert result["count"] == 2


# === Tests: Exists Operation ===


class TestExistsOperation:
    """Tests for self.vector.exists."""

    @pytest.mark.asyncio
    async def test_exists_requires_id(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Exists fails without id."""
        result = await vector_node._invoke_aspect("exists", observer)

        assert result.get("error") == "id is required"

    @pytest.mark.asyncio
    async def test_exists_false(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Exists returns false for missing vectors."""
        result = await vector_node._invoke_aspect("exists", observer, id="missing")

        assert result["exists"] is False

    @pytest.mark.asyncio
    async def test_exists_true(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Exists returns true for existing vectors."""
        await vector_node._invoke_aspect("add", observer, id="doc1", embedding=[0.1, 0.2, 0.3])

        result = await vector_node._invoke_aspect("exists", observer, id="doc1")

        assert result["exists"] is True


# === Tests: Dimension Operation ===


class TestDimensionOperation:
    """Tests for self.vector.dimension."""

    @pytest.mark.asyncio
    async def test_dimension_fallback(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Dimension returns fallback default."""
        result = await vector_node._invoke_aspect("dimension", observer)

        assert result["dimension"] == 384  # Default
        assert result["backend"] == "fallback"


# === Tests: Metric Operation ===


class TestMetricOperation:
    """Tests for self.vector.metric."""

    @pytest.mark.asyncio
    async def test_metric_fallback(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Metric returns fallback default."""
        result = await vector_node._invoke_aspect("metric", observer)

        assert result["metric"] == "cosine"
        assert result["backend"] == "fallback"


# === Tests: Status Operation ===


class TestStatusOperation:
    """Tests for self.vector.status."""

    @pytest.mark.asyncio
    async def test_status_fallback(
        self,
        vector_node: VectorNode,
        observer: Any,
    ) -> None:
        """Status shows fallback state."""
        result = await vector_node._invoke_aspect("status", observer)

        assert result["configured"] is False
        assert result["backend"] == "fallback"
        assert "note" in result


# === Tests: With V-gent Integration ===


class TestVgentIntegration:
    """Tests for V-gent integration when available."""

    @pytest.fixture
    def vgent_node(self) -> VectorNode:
        """VectorNode with mock V-gent."""
        # Lazy import to avoid circular dependency
        try:
            from agents.v import MemoryVectorBackend

            vgent = MemoryVectorBackend(dimension=3)
            return VectorNode(_vgent=vgent)
        except ImportError:
            pytest.skip("V-gent not available")

    @pytest.mark.asyncio
    async def test_add_with_vgent(
        self,
        vgent_node: VectorNode,
        observer: Any,
    ) -> None:
        """Add uses V-gent when available."""
        result = await vgent_node._invoke_aspect(
            "add",
            observer,
            id="doc1",
            embedding=[0.1, 0.2, 0.3],
        )

        assert result["status"] == "added"
        assert result["backend"] == "vgent"

    @pytest.mark.asyncio
    async def test_search_with_vgent(
        self,
        vgent_node: VectorNode,
        observer: Any,
    ) -> None:
        """Search uses V-gent when available."""
        # Add vectors
        await vgent_node._invoke_aspect("add", observer, id="doc1", embedding=[1.0, 0.0, 0.0])
        await vgent_node._invoke_aspect("add", observer, id="doc2", embedding=[0.0, 1.0, 0.0])

        # Search
        result = await vgent_node._invoke_aspect(
            "search",
            observer,
            query=[1.0, 0.0, 0.0],
        )

        assert result["status"] == "found"
        assert result["backend"] == "vgent"
        assert result["results"][0]["id"] == "doc1"

    @pytest.mark.asyncio
    async def test_status_with_vgent(
        self,
        vgent_node: VectorNode,
        observer: Any,
    ) -> None:
        """Status shows V-gent configured."""
        result = await vgent_node._invoke_aspect("status", observer)

        assert result["configured"] is True
        assert result["backend"] == "vgent"
        assert result["dimension"] == 3
