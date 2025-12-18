"""
VgentRouter Tests: Backend selection and graceful degradation.

Tests cover:
1. Auto-selection of backends
2. Environment variable override
3. Preferred backend selection
4. Fallback chain behavior
5. Router-specific methods (status, force_backend, reset)
6. Protocol compliance (VgentProtocol delegation)
7. D-gent backend integration
"""

from __future__ import annotations

import os
from typing import AsyncIterator
from unittest.mock import patch

import pytest

from agents.d import MemoryBackend as DgentMemoryBackend

from ..router import (
    ENV_BACKEND,
    ENV_POSTGRES_URL,
    ENV_QDRANT_URL,
    BackendStatus,
    VectorBackend,
    VgentRouter,
    create_vgent,
)
from ..types import DistanceMetric
from .conftest import TEST_DIMENSION, make_embedding, make_unit_vector

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def unique_namespace() -> str:
    """Generate unique namespace for test isolation."""
    import uuid

    return f"test_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def router(unique_namespace: str) -> VgentRouter:
    """Fresh router with isolated namespace (memory backend for isolation)."""
    return VgentRouter(
        dimension_=TEST_DIMENSION,
        namespace=unique_namespace,
        preferred=VectorBackend.MEMORY,  # Memory for test isolation
    )


@pytest.fixture
def dgent_memory() -> DgentMemoryBackend:
    """Fresh D-gent memory backend for injection."""
    return DgentMemoryBackend()


@pytest.fixture
def router_with_dgent(dgent_memory: DgentMemoryBackend, unique_namespace: str) -> VgentRouter:
    """Router with injected D-gent backend."""
    return VgentRouter(
        dimension_=TEST_DIMENSION,
        dgent=dgent_memory,
        namespace=unique_namespace,
        preferred=VectorBackend.DGENT,
    )


@pytest.fixture
async def populated_router(router: VgentRouter) -> AsyncIterator[VgentRouter]:
    """Router pre-populated with sample entries."""
    for i in range(5):
        await router.add(f"entry_{i}", make_embedding(i), {"index": str(i)})

    yield router

    await router.clear()


# =============================================================================
# Backend Selection Tests
# =============================================================================


class TestBackendSelection:
    """Test backend selection logic."""

    @pytest.mark.asyncio
    async def test_auto_selects_memory_as_default(self, router: VgentRouter) -> None:
        """With no D-gent and no env, defaults to memory fallback chain."""
        # Trigger backend selection
        await router.add("test", make_embedding(1))

        # Memory or D-gent should be selected (depends on fallback chain)
        assert router.selected_backend in [VectorBackend.MEMORY, VectorBackend.DGENT]

    @pytest.mark.asyncio
    async def test_preferred_backend_used_when_available(
        self,
    ) -> None:
        """Preferred backend is used when available."""
        router = VgentRouter(
            dimension_=TEST_DIMENSION,
            preferred=VectorBackend.MEMORY,
        )

        await router.add("test", make_embedding(1))

        assert router.selected_backend == VectorBackend.MEMORY

    @pytest.mark.asyncio
    async def test_env_override_memory(self, router: VgentRouter) -> None:
        """Environment variable overrides backend selection."""
        with patch.dict(os.environ, {ENV_BACKEND: "MEMORY"}):
            router2 = VgentRouter(dimension_=TEST_DIMENSION)
            await router2.add("test", make_embedding(1))

            assert router2.selected_backend == VectorBackend.MEMORY

    @pytest.mark.asyncio
    async def test_env_override_dgent(self) -> None:
        """Environment variable can force D-gent backend."""
        with patch.dict(os.environ, {ENV_BACKEND: "DGENT"}):
            router = VgentRouter(dimension_=TEST_DIMENSION)
            await router.add("test", make_embedding(1))

            assert router.selected_backend == VectorBackend.DGENT

    @pytest.mark.asyncio
    async def test_invalid_env_value_falls_back(self) -> None:
        """Invalid environment value falls through to normal selection."""
        with patch.dict(os.environ, {ENV_BACKEND: "INVALID_BACKEND"}):
            router = VgentRouter(
                dimension_=TEST_DIMENSION,
                preferred=VectorBackend.MEMORY,
            )
            await router.add("test", make_embedding(1))

            # Should fall back to preferred
            assert router.selected_backend == VectorBackend.MEMORY

    @pytest.mark.asyncio
    async def test_fallback_chain_order(self) -> None:
        """Fallback chain is tried in order."""
        router = VgentRouter(
            dimension_=TEST_DIMENSION,
            fallback_chain=[VectorBackend.MEMORY],  # Memory first
        )

        await router.add("test", make_embedding(1))
        assert router.selected_backend == VectorBackend.MEMORY

    @pytest.mark.asyncio
    async def test_dgent_preferred_with_injected(self, dgent_memory: DgentMemoryBackend) -> None:
        """Injected D-gent is used when D-gent backend is selected."""
        router = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        await router.add("test", make_embedding(1), {"tag": "injected"})

        assert router.selected_backend == VectorBackend.DGENT

        # Verify it actually used the injected D-gent
        datum = await dgent_memory.get("vectors:test")
        assert datum is not None


# =============================================================================
# Backend Status Tests
# =============================================================================


class TestBackendStatus:
    """Test backend availability checks."""

    @pytest.mark.asyncio
    async def test_memory_always_available(self, router: VgentRouter) -> None:
        """Memory backend is always available."""
        statuses = await router.status()
        memory_status = next(s for s in statuses if s.backend == VectorBackend.MEMORY)

        assert memory_status.available is True

    @pytest.mark.asyncio
    async def test_dgent_always_available(self, router: VgentRouter) -> None:
        """D-gent backend is always available (uses its own projection)."""
        statuses = await router.status()
        dgent_status = next(s for s in statuses if s.backend == VectorBackend.DGENT)

        assert dgent_status.available is True

    @pytest.mark.asyncio
    async def test_qdrant_unavailable_without_env(self, router: VgentRouter) -> None:
        """Qdrant is unavailable without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure the env var is not set
            os.environ.pop(ENV_QDRANT_URL, None)

            statuses = await router.status()
            qdrant_status = next(s for s in statuses if s.backend == VectorBackend.QDRANT)

            assert qdrant_status.available is False
            assert "KGENTS_QDRANT_URL" in qdrant_status.reason

    @pytest.mark.asyncio
    async def test_postgres_unavailable_without_env(self, router: VgentRouter) -> None:
        """Postgres is unavailable without environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop(ENV_POSTGRES_URL, None)

            statuses = await router.status()
            pg_status = next(s for s in statuses if s.backend == VectorBackend.POSTGRES)

            assert pg_status.available is False
            assert "KGENTS_POSTGRES_URL" in pg_status.reason

    @pytest.mark.asyncio
    async def test_status_returns_all_backends(self, router: VgentRouter) -> None:
        """Status returns info for all backends."""
        statuses = await router.status()

        backend_types = {s.backend for s in statuses}
        assert backend_types == set(VectorBackend)


# =============================================================================
# Router Control Tests
# =============================================================================


class TestRouterControl:
    """Test router control methods."""

    @pytest.mark.asyncio
    async def test_force_backend_memory(self, router: VgentRouter) -> None:
        """Force memory backend."""
        await router.force_backend(VectorBackend.MEMORY)

        assert router.selected_backend == VectorBackend.MEMORY

        # Verify it works
        await router.add("test", make_embedding(1))
        entry = await router.get("test")
        assert entry is not None

    @pytest.mark.asyncio
    async def test_force_backend_dgent(self, router: VgentRouter) -> None:
        """Force D-gent backend."""
        await router.force_backend(VectorBackend.DGENT)

        assert router.selected_backend == VectorBackend.DGENT

    @pytest.mark.asyncio
    async def test_force_unavailable_backend_raises(self, router: VgentRouter) -> None:
        """Forcing unavailable backend raises RuntimeError."""
        # Qdrant is unavailable without env var
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop(ENV_QDRANT_URL, None)

            with pytest.raises(RuntimeError, match="not available"):
                await router.force_backend(VectorBackend.QDRANT)

    @pytest.mark.asyncio
    async def test_reset_clears_selection(self, populated_router: VgentRouter) -> None:
        """Reset clears backend selection."""
        # Backend is selected and has data
        assert populated_router.selected_backend is not None

        populated_router.reset()

        assert populated_router.selected_backend is None

    @pytest.mark.asyncio
    async def test_reset_allows_reselection(self, router: VgentRouter) -> None:
        """After reset, backend is reselected on next operation."""
        await router.force_backend(VectorBackend.MEMORY)
        assert router.selected_backend == VectorBackend.MEMORY

        router.reset()
        assert router.selected_backend is None

        # Next operation triggers reselection
        await router.add("test", make_embedding(1))
        assert router.selected_backend is not None


# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestProtocolCompliance:
    """Test that router properly delegates to backend."""

    @pytest.mark.asyncio
    async def test_add_and_get(self, router: VgentRouter) -> None:
        """Add and get work through router."""
        emb = make_embedding(1)
        await router.add("test", emb, {"tag": "sample"})

        entry = await router.get("test")
        assert entry is not None
        assert entry.id == "test"
        assert entry.metadata["tag"] == "sample"

    @pytest.mark.asyncio
    async def test_add_batch(self, router: VgentRouter) -> None:
        """Batch add works through router."""
        entries = [
            ("a", make_embedding(1), {"type": "a"}),
            ("b", make_embedding(2), {"type": "b"}),
        ]

        ids = await router.add_batch(entries)  # type: ignore[arg-type]

        assert ids == ["a", "b"]
        assert await router.count() == 2

    @pytest.mark.asyncio
    async def test_search(self, populated_router: VgentRouter) -> None:
        """Search works through router."""
        query = make_embedding(0)

        results = await populated_router.search(query, limit=3)

        assert len(results) == 3
        # First result should be entry_0 (exact match)
        assert results[0].id == "entry_0"

    @pytest.mark.asyncio
    async def test_search_with_filters(self, router: VgentRouter) -> None:
        """Search with filters works through router."""
        await router.add("a", make_embedding(1), {"type": "foo"})
        await router.add("b", make_embedding(2), {"type": "bar"})

        results = await router.search(make_embedding(1), filters={"type": "foo"})

        assert len(results) == 1
        assert results[0].id == "a"

    @pytest.mark.asyncio
    async def test_remove(self, router: VgentRouter) -> None:
        """Remove works through router."""
        await router.add("test", make_embedding(1))

        result = await router.remove("test")
        assert result is True

        entry = await router.get("test")
        assert entry is None

    @pytest.mark.asyncio
    async def test_clear(self, populated_router: VgentRouter) -> None:
        """Clear works through router."""
        count = await populated_router.clear()
        assert count == 5

        remaining = await populated_router.count()
        assert remaining == 0

    @pytest.mark.asyncio
    async def test_count(self, populated_router: VgentRouter) -> None:
        """Count works through router."""
        count = await populated_router.count()
        assert count == 5

    @pytest.mark.asyncio
    async def test_exists(self, populated_router: VgentRouter) -> None:
        """Exists works through router."""
        assert await populated_router.exists("entry_0") is True
        assert await populated_router.exists("nonexistent") is False


# =============================================================================
# Properties Tests
# =============================================================================


class TestProperties:
    """Test router properties."""

    def test_dimension_property(self, router: VgentRouter) -> None:
        """Dimension property returns configured value."""
        assert router.dimension == TEST_DIMENSION

    def test_metric_property(self, router: VgentRouter) -> None:
        """Metric property returns configured value."""
        assert router.metric == DistanceMetric.COSINE

    def test_custom_metric(self) -> None:
        """Custom metric is preserved."""
        router = VgentRouter(
            dimension_=TEST_DIMENSION,
            metric_=DistanceMetric.EUCLIDEAN,
        )
        assert router.metric == DistanceMetric.EUCLIDEAN

    def test_repr(self, router: VgentRouter) -> None:
        """Router has useful repr."""
        repr_str = repr(router)
        assert "VgentRouter" in repr_str
        assert str(TEST_DIMENSION) in repr_str
        assert "cosine" in repr_str

    @pytest.mark.asyncio
    async def test_repr_shows_selected_backend(self, populated_router: VgentRouter) -> None:
        """Repr shows selected backend after selection."""
        repr_str = repr(populated_router)
        # After operations, backend should be selected and shown
        assert "backend=" in repr_str


# =============================================================================
# D-gent Integration Tests
# =============================================================================


class TestDgentIntegration:
    """Test D-gent backend integration."""

    @pytest.mark.asyncio
    async def test_dgent_backend_persists(self, dgent_memory: DgentMemoryBackend) -> None:
        """D-gent backend persists vectors."""
        router = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        await router.add("doc1", make_embedding(1), {"author": "alice"})

        # Check D-gent has the datum
        datum = await dgent_memory.get("vectors:doc1")
        assert datum is not None
        assert datum.metadata["author"] == "alice"

    @pytest.mark.asyncio
    async def test_dgent_index_loads_on_first_operation(
        self, dgent_memory: DgentMemoryBackend
    ) -> None:
        """D-gent index is loaded on first operation."""
        # Pre-populate D-gent directly
        router1 = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )
        await router1.add("doc1", make_embedding(1))
        await router1.add("doc2", make_embedding(2))

        # Create new router (simulates restart)
        router2 = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        # First operation should load index
        count = await router2.count()
        assert count == 2

    @pytest.mark.asyncio
    async def test_dgent_search_works_after_load(self, dgent_memory: DgentMemoryBackend) -> None:
        """Search works correctly with D-gent after index load."""
        router1 = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        base = make_embedding(1)
        await router1.add("target", base, {"type": "important"})
        await router1.add("other", make_embedding(99))

        # New router
        router2 = VgentRouter(
            dimension_=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        results = await router2.search(base, limit=1)
        assert len(results) == 1
        assert results[0].id == "target"


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactory:
    """Test create_vgent factory function."""

    def test_create_vgent_defaults(self) -> None:
        """Factory creates router with defaults."""
        router = create_vgent(dimension=768)

        assert router.dimension == 768
        assert router.metric == DistanceMetric.COSINE
        assert router.namespace == "vectors"

    def test_create_vgent_custom(self) -> None:
        """Factory respects custom parameters."""
        router = create_vgent(
            dimension=1536,
            metric=DistanceMetric.DOT_PRODUCT,
            namespace="my_vectors",
            preferred=VectorBackend.MEMORY,
        )

        assert router.dimension == 1536
        assert router.metric == DistanceMetric.DOT_PRODUCT
        assert router.namespace == "my_vectors"
        assert router.preferred == VectorBackend.MEMORY

    @pytest.mark.asyncio
    async def test_create_vgent_with_dgent(self, dgent_memory: DgentMemoryBackend) -> None:
        """Factory accepts D-gent injection."""
        router = create_vgent(
            dimension=TEST_DIMENSION,
            dgent=dgent_memory,
            preferred=VectorBackend.DGENT,
        )

        await router.add("test", make_embedding(1))

        datum = await dgent_memory.get("vectors:test")
        assert datum is not None


# =============================================================================
# Concurrency Tests
# =============================================================================


class TestConcurrency:
    """Test concurrent access patterns."""

    @pytest.mark.asyncio
    async def test_concurrent_adds(self, router: VgentRouter) -> None:
        """Concurrent adds work correctly."""
        import asyncio

        async def add_entry(i: int) -> str:
            return await router.add(f"entry_{i}", make_embedding(i))

        # Add 10 entries concurrently
        tasks = [add_entry(i) for i in range(10)]
        ids = await asyncio.gather(*tasks)

        assert len(ids) == 10
        assert await router.count() == 10

    @pytest.mark.asyncio
    async def test_backend_selection_is_atomic(self, router: VgentRouter) -> None:
        """Backend selection happens only once under concurrent access."""
        import asyncio

        async def trigger_selection(i: int) -> VectorBackend | None:
            await router.add(f"entry_{i}", make_embedding(i))
            return router.selected_backend

        # Trigger selection from 5 concurrent operations
        tasks = [trigger_selection(i) for i in range(5)]
        backends = await asyncio.gather(*tasks)

        # All should see the same backend (selection was atomic)
        assert all(b == backends[0] for b in backends)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_router_count(self, router: VgentRouter) -> None:
        """Empty router has count 0."""
        count = await router.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_empty_router_search(self, router: VgentRouter) -> None:
        """Search on empty router returns empty list."""
        results = await router.search(make_embedding(1))
        assert results == []

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, router: VgentRouter) -> None:
        """Get nonexistent ID returns None."""
        entry = await router.get("nonexistent")
        assert entry is None

    @pytest.mark.asyncio
    async def test_remove_nonexistent(self, router: VgentRouter) -> None:
        """Remove nonexistent returns False."""
        result = await router.remove("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear_empty_router(self, router: VgentRouter) -> None:
        """Clear on empty router returns 0."""
        count = await router.clear()
        assert count == 0
