"""
Tests for ProxyHandleStore.

AD-015: Proxy Handles & Transparent Batch Processes

Tests the five laws:
1. Explicit Computation: compute() is the ONLY way to create handles
2. Provenance Preservation: Every handle knows its origin
3. Event Transparency: Every state transition emits events
4. No Anonymous Debris: human_label is required
5. Idempotent Computation: Concurrent compute() awaits same work
"""

import asyncio
import tempfile
from datetime import timedelta
from pathlib import Path

import pytest

from services.proxy.exceptions import ComputationError, NoProxyHandleError
from services.proxy.store import (
    ProxyHandleStore,
    get_proxy_handle_store,
    reset_proxy_handle_store,
)
from services.proxy.types import HandleStatus, ProxyHandleEvent, SourceType

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def store() -> ProxyHandleStore:
    """Create a fresh store for each test."""
    return ProxyHandleStore()


@pytest.fixture
def persistent_store(tmp_path: Path) -> ProxyHandleStore:
    """Create a store with persistence enabled."""
    return ProxyHandleStore(persist_path=tmp_path / "proxy_handles.json")


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset singleton before each test."""
    reset_proxy_handle_store()


# =============================================================================
# Basic Operations Tests
# =============================================================================


class TestProxyHandleStoreBasics:
    """Tests for basic store operations."""

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_handle(self, store: ProxyHandleStore) -> None:
        """get() should return None when no handle exists."""
        result = await store.get(SourceType.SPEC_CORPUS)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_or_raise_raises_when_no_handle(self, store: ProxyHandleStore) -> None:
        """get_or_raise() should raise NoProxyHandleError when no handle exists."""
        with pytest.raises(NoProxyHandleError) as exc_info:
            await store.get_or_raise(SourceType.SPEC_CORPUS)

        assert exc_info.value.source_type == SourceType.SPEC_CORPUS

    @pytest.mark.asyncio
    async def test_compute_creates_handle(self, store: ProxyHandleStore) -> None:
        """Law 1: compute() creates handles."""

        async def compute_fn() -> dict:
            return {"result": "computed"}

        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test computation",
        )

        assert handle.status == HandleStatus.FRESH
        assert handle.data == {"result": "computed"}
        assert handle.human_label == "Test computation"

    @pytest.mark.asyncio
    async def test_compute_requires_human_label(self, store: ProxyHandleStore) -> None:
        """Law 4: human_label is required."""

        async def compute_fn() -> str:
            return "data"

        with pytest.raises(ValueError, match="human_label is required"):
            await store.compute(
                source_type=SourceType.SPEC_CORPUS,
                compute_fn=compute_fn,
                human_label="",  # Empty label
            )

    @pytest.mark.asyncio
    async def test_get_returns_computed_handle(self, store: ProxyHandleStore) -> None:
        """get() should return handle after compute()."""

        async def compute_fn() -> str:
            return "test data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.data == "test data"


class TestProxyHandleStoreComputation:
    """Tests for computation behavior."""

    @pytest.mark.asyncio
    async def test_compute_returns_fresh_handle_without_recomputing(
        self, store: ProxyHandleStore
    ) -> None:
        """compute() should return existing fresh handle without recomputing."""
        call_count = 0

        async def compute_fn() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call
        handle1 = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )
        assert handle1.data == 1
        assert call_count == 1

        # Second call - should return cached
        handle2 = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )
        assert handle2.data == 1  # Same data
        assert call_count == 1  # compute_fn not called again

    @pytest.mark.asyncio
    async def test_compute_force_recomputes(self, store: ProxyHandleStore) -> None:
        """compute(force=True) should recompute even with fresh handle."""
        call_count = 0

        async def compute_fn() -> int:
            nonlocal call_count
            call_count += 1
            return call_count

        # First call
        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )
        assert call_count == 1

        # Second call with force
        handle2 = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
            force=True,
        )
        assert handle2.data == 2  # New data
        assert call_count == 2  # compute_fn called again

    @pytest.mark.asyncio
    async def test_compute_handles_error(self, store: ProxyHandleStore) -> None:
        """compute() should handle errors and create ERROR handle."""

        async def failing_fn() -> None:
            raise ValueError("Computation failed")

        with pytest.raises(ComputationError):
            await store.compute(
                source_type=SourceType.SPEC_CORPUS,
                compute_fn=failing_fn,
                human_label="Failing test",
            )

        # Should have error handle
        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.status == HandleStatus.ERROR
        assert "Computation failed" in (handle.error or "")

    @pytest.mark.asyncio
    async def test_compute_with_custom_ttl(self, store: ProxyHandleStore) -> None:
        """compute() should respect custom TTL."""

        async def compute_fn() -> str:
            return "data"

        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
            ttl=timedelta(hours=2),
        )

        assert handle.ttl == timedelta(hours=2)

    @pytest.mark.asyncio
    async def test_compute_tracks_provenance(self, store: ProxyHandleStore) -> None:
        """Law 2: Computed handles have provenance."""

        async def compute_fn() -> str:
            await asyncio.sleep(0.01)  # Small delay to measure
            return "data"

        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Provenance test",
            computed_by="test_suite",
        )

        assert handle.computed_by == "test_suite"
        assert handle.computation_duration > 0
        assert handle.computation_count == 1


class TestProxyHandleStoreIdempotency:
    """Tests for Law 5: Idempotent Computation."""

    @pytest.mark.asyncio
    async def test_concurrent_compute_awaits_same_computation(
        self, store: ProxyHandleStore
    ) -> None:
        """Concurrent compute() calls should await the same computation."""
        call_count = 0

        async def slow_compute() -> int:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Slow computation
            return call_count

        # Launch concurrent computations
        task1 = asyncio.create_task(
            store.compute(
                source_type=SourceType.SPEC_CORPUS,
                compute_fn=slow_compute,
                human_label="Concurrent test",
            )
        )
        task2 = asyncio.create_task(
            store.compute(
                source_type=SourceType.SPEC_CORPUS,
                compute_fn=slow_compute,
                human_label="Concurrent test",
            )
        )

        handle1, handle2 = await asyncio.gather(task1, task2)

        # Both should return same handle (same ID)
        assert handle1.handle_id == handle2.handle_id
        # compute_fn should only be called once
        assert call_count == 1


class TestProxyHandleStoreLifecycle:
    """Tests for handle lifecycle operations."""

    @pytest.mark.asyncio
    async def test_invalidate_marks_stale(self, store: ProxyHandleStore) -> None:
        """invalidate() should mark handle as STALE."""

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        result = await store.invalidate(SourceType.SPEC_CORPUS)
        assert result is True

        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.status == HandleStatus.STALE

    @pytest.mark.asyncio
    async def test_invalidate_returns_false_when_no_handle(self, store: ProxyHandleStore) -> None:
        """invalidate() should return False when no handle exists."""
        result = await store.invalidate(SourceType.SPEC_CORPUS)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_removes_handle(self, store: ProxyHandleStore) -> None:
        """delete() should remove handle entirely."""

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        result = await store.delete(SourceType.SPEC_CORPUS)
        assert result is True

        handle = await store.get(SourceType.SPEC_CORPUS)
        assert handle is None

    @pytest.mark.asyncio
    async def test_delete_returns_false_when_no_handle(self, store: ProxyHandleStore) -> None:
        """delete() should return False when no handle exists."""
        result = await store.delete(SourceType.SPEC_CORPUS)
        assert result is False


class TestProxyHandleStoreEvents:
    """Tests for Law 3: Event Transparency."""

    @pytest.mark.asyncio
    async def test_compute_emits_started_and_completed_events(
        self, store: ProxyHandleStore
    ) -> None:
        """compute() should emit started and completed events."""
        events: list[ProxyHandleEvent] = []
        store.subscribe(events.append)

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Event test",
        )

        event_types = [e.event_type for e in events]
        assert "computation_started" in event_types
        assert "computation_completed" in event_types

    @pytest.mark.asyncio
    async def test_compute_emits_failed_event_on_error(self, store: ProxyHandleStore) -> None:
        """compute() should emit failed event on error."""
        events: list[ProxyHandleEvent] = []
        store.subscribe(events.append)

        async def failing_fn() -> None:
            raise ValueError("Test error")

        with pytest.raises(ComputationError):
            await store.compute(
                source_type=SourceType.SPEC_CORPUS,
                compute_fn=failing_fn,
                human_label="Error test",
            )

        event_types = [e.event_type for e in events]
        assert "computation_started" in event_types
        assert "computation_failed" in event_types

    @pytest.mark.asyncio
    async def test_get_emits_accessed_event(self, store: ProxyHandleStore) -> None:
        """get() should emit handle_accessed event."""
        events: list[ProxyHandleEvent] = []

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        # Subscribe after compute to only capture get events
        store.subscribe(events.append)

        await store.get(SourceType.SPEC_CORPUS)

        event_types = [e.event_type for e in events]
        assert "handle_accessed" in event_types

    @pytest.mark.asyncio
    async def test_invalidate_emits_event(self, store: ProxyHandleStore) -> None:
        """invalidate() should emit handle_invalidated event."""
        events: list[ProxyHandleEvent] = []

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        store.subscribe(events.append)
        await store.invalidate(SourceType.SPEC_CORPUS)

        event_types = [e.event_type for e in events]
        assert "handle_invalidated" in event_types

    @pytest.mark.asyncio
    async def test_delete_emits_event(self, store: ProxyHandleStore) -> None:
        """delete() should emit handle_deleted event."""
        events: list[ProxyHandleEvent] = []

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        store.subscribe(events.append)
        await store.delete(SourceType.SPEC_CORPUS)

        event_types = [e.event_type for e in events]
        assert "handle_deleted" in event_types

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_events(self, store: ProxyHandleStore) -> None:
        """unsubscribe() should stop event delivery."""
        events: list[ProxyHandleEvent] = []
        unsubscribe = store.subscribe(events.append)

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )
        first_count = len(events)
        assert first_count > 0

        # Unsubscribe
        unsubscribe()

        # This should not add events
        await store.get(SourceType.SPEC_CORPUS)
        assert len(events) == first_count


class TestProxyHandleStoreQuery:
    """Tests for store query operations."""

    @pytest.mark.asyncio
    async def test_all_returns_all_handles(self, store: ProxyHandleStore) -> None:
        """all() should return all handles."""

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test 1",
        )
        await store.compute(
            source_type=SourceType.WITNESS_GRAPH,
            compute_fn=compute_fn,
            human_label="Test 2",
        )

        all_handles = store.all()
        assert len(all_handles) == 2

    @pytest.mark.asyncio
    async def test_source_types_returns_all_types(self, store: ProxyHandleStore) -> None:
        """source_types() should return all source types with handles."""

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test 1",
        )
        await store.compute(
            source_type=SourceType.WITNESS_GRAPH,
            compute_fn=compute_fn,
            human_label="Test 2",
        )

        types = store.source_types()
        assert SourceType.SPEC_CORPUS in types
        assert SourceType.WITNESS_GRAPH in types

    @pytest.mark.asyncio
    async def test_stats(self, store: ProxyHandleStore) -> None:
        """stats() should return store statistics."""

        async def compute_fn() -> str:
            return "data"

        await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Test",
        )

        stats = store.stats()
        assert stats.total_handles == 1
        assert stats.fresh_count == 1
        assert stats.total_computations == 1
        assert stats.avg_computation_time >= 0


class TestProxyHandleStorePersistence:
    """Tests for persistence."""

    @pytest.mark.asyncio
    async def test_persists_to_disk(self, persistent_store: ProxyHandleStore) -> None:
        """Store should persist handles to disk."""

        async def compute_fn() -> str:
            return "persistent data"

        await persistent_store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Persistence test",
        )

        # File should exist
        assert persistent_store.persist_path is not None
        assert persistent_store.persist_path.exists()

    @pytest.mark.asyncio
    async def test_loads_from_disk(self, tmp_path: Path) -> None:
        """Store should load handles from disk on init."""
        persist_path = tmp_path / "proxy_handles.json"

        # Create store and compute
        store1 = ProxyHandleStore(persist_path=persist_path)

        async def compute_fn() -> str:
            return "persistent data"

        await store1.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=compute_fn,
            human_label="Persistence test",
        )

        # Create new store with same path
        store2 = ProxyHandleStore(persist_path=persist_path)

        # Should have loaded handle
        handle = await store2.get(SourceType.SPEC_CORPUS)
        assert handle is not None
        assert handle.human_label == "Persistence test"


class TestProxyHandleStoreSingleton:
    """Tests for singleton factory."""

    def test_get_proxy_handle_store_returns_singleton(self) -> None:
        """get_proxy_handle_store() should return singleton."""
        store1 = get_proxy_handle_store()
        store2 = get_proxy_handle_store()
        assert store1 is store2

    def test_reset_clears_singleton(self) -> None:
        """reset_proxy_handle_store() should clear singleton."""
        store1 = get_proxy_handle_store()
        reset_proxy_handle_store()
        store2 = get_proxy_handle_store()
        assert store1 is not store2
