"""
Tests for Ghost ↔ Substrate Bidirectional Sync.

Phase 8: The final coherence layer.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generator

import pytest
from agents.m.ghost_sync import (
    GhostAwareReaperIntegration,
    GhostSyncAllocation,
    GhostSyncEvent,
    GhostSyncManager,
    create_ghost_aware_reaper,
    create_ghost_sync_manager,
    wrap_with_ghost_sync,
)
from agents.m.substrate import (
    LifecyclePolicy,
    MemoryQuota,
    SharedSubstrate,
    create_substrate,
)
from infra.ghost.lifecycle import LifecycleAwareCache

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
    """Temporary directory for ghost cache."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def ghost_cache(temp_cache_dir: Path) -> LifecycleAwareCache:
    """Fresh ghost cache for testing."""
    return LifecycleAwareCache(cache_dir=temp_cache_dir)


@pytest.fixture
def substrate() -> SharedSubstrate[Any]:
    """Fresh substrate for testing."""
    return create_substrate()


@pytest.fixture
def sync_manager(
    ghost_cache: LifecycleAwareCache, substrate: SharedSubstrate[Any]
) -> GhostSyncManager[Any]:
    """Ghost sync manager for testing."""
    return create_ghost_sync_manager(ghost_cache, substrate)


@pytest.fixture
def allocation(substrate: SharedSubstrate[Any]) -> Any:
    """Sample allocation for testing."""
    return substrate.allocate(
        agent_id="test_agent",
        quota=MemoryQuota(max_patterns=100),
        lifecycle=LifecyclePolicy(
            human_label="Test allocation",
            ttl=timedelta(hours=1),
        ),
    )


# =============================================================================
# GhostSyncEvent Tests
# =============================================================================


class TestGhostSyncEvent:
    """Tests for GhostSyncEvent dataclass."""

    def test_event_creation(self):
        """Event can be created with all fields."""
        event = GhostSyncEvent(
            timestamp=datetime.now(),
            event_type="store_to_ghost",
            agent_id="test_agent",
            key="alloc:test_agent:concept_1",
            success=True,
            reason="Test sync",
        )

        assert event.event_type == "store_to_ghost"
        assert event.agent_id == "test_agent"
        assert event.success is True

    def test_event_with_metadata(self):
        """Event can include metadata."""
        event = GhostSyncEvent(
            timestamp=datetime.now(),
            event_type="invalidate",
            agent_id="test_agent",
            key="alloc:test_agent:*",
            success=True,
            metadata={"count": 5},
        )

        assert event.metadata["count"] == 5


# =============================================================================
# GhostSyncManager Tests
# =============================================================================


class TestGhostSyncManager:
    """Tests for GhostSyncManager."""

    def test_manager_creation(
        self, ghost_cache: LifecycleAwareCache, substrate: SharedSubstrate[Any]
    ) -> None:
        """Manager can be created."""
        manager: GhostSyncManager[Any] = GhostSyncManager(ghost_cache, substrate)
        assert manager is not None
        assert len(manager.events) == 0

    def test_make_ghost_key(self, sync_manager: GhostSyncManager[Any]) -> None:
        """Ghost keys are formatted correctly."""
        key = sync_manager._make_ghost_key("agent_1", "concept_a")
        assert key == "alloc:agent_1:concept_a"

    def test_parse_ghost_key(self, sync_manager: GhostSyncManager[Any]) -> None:
        """Ghost keys can be parsed back."""
        result = sync_manager._parse_ghost_key("alloc:agent_1:concept_a")
        assert result == ("agent_1", "concept_a")

    def test_parse_ghost_key_with_colons(
        self, sync_manager: GhostSyncManager[Any]
    ) -> None:
        """Concept IDs with colons are parsed correctly."""
        result = sync_manager._parse_ghost_key("alloc:agent_1:ns:concept:sub")
        assert result is not None
        agent_id, concept_id = result
        assert agent_id == "agent_1"
        assert concept_id == "ns:concept:sub"

    def test_parse_invalid_key(self, sync_manager: GhostSyncManager[Any]) -> None:
        """Invalid keys return None."""
        assert sync_manager._parse_ghost_key("invalid") is None
        assert sync_manager._parse_ghost_key("wrong:format") is None

    @pytest.mark.asyncio
    async def test_store_with_sync(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """Store creates both allocation pattern and ghost entry."""
        success = await sync_manager.store_with_sync(
            allocation=allocation,
            concept_id="test_concept",
            content={"data": "test"},
            embedding=[1.0, 0.0, 0.0],
        )

        assert success is True
        assert allocation.pattern_count == 1

        # Ghost entry exists
        ghost_key = "alloc:test_agent:test_concept"
        entry = ghost_cache.read(ghost_key)
        assert entry is not None
        assert entry.data["concept_id"] == "test_concept"

        # Event recorded
        assert len(sync_manager.events) == 1
        assert sync_manager.events[0].event_type == "store_to_ghost"
        assert sync_manager.events[0].success is True

    @pytest.mark.asyncio
    async def test_store_quota_exceeded(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """When quota exceeded, no ghost entry is created."""
        # Create allocation with very small quota
        allocation = substrate.allocate(
            agent_id="small_agent",
            quota=MemoryQuota(max_patterns=1),
            lifecycle=LifecyclePolicy(human_label="Small allocation"),
        )

        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        # First store succeeds
        success1 = await sync_manager.store_with_sync(
            allocation, "concept_1", {"x": 1}, [1.0]
        )
        assert success1 is True

        # Second store fails (quota exceeded)
        success2 = await sync_manager.store_with_sync(
            allocation, "concept_2", {"x": 2}, [0.0]
        )
        assert success2 is False

        # Only one ghost entry
        assert len([k for k in ghost_cache.all_keys() if "small_agent" in k]) == 1

    def test_on_ghost_access_touches_allocation(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
    ) -> None:
        """Ghost access updates allocation last_accessed."""
        original_access = allocation.last_accessed
        original_count = allocation.access_count

        # Simulate ghost access
        success = sync_manager.on_ghost_access("alloc:test_agent:some_concept")

        assert success is True
        assert allocation.access_count == original_count + 1
        assert allocation.last_accessed >= original_access

        # Event recorded
        assert len(sync_manager.events) == 1
        assert sync_manager.events[0].event_type == "ghost_access"

    def test_on_ghost_access_unknown_allocation(
        self, sync_manager: GhostSyncManager[Any]
    ) -> None:
        """Ghost access for unknown allocation returns False."""
        success = sync_manager.on_ghost_access("alloc:unknown_agent:concept")
        assert success is False

    @pytest.mark.asyncio
    async def test_invalidate_for_allocation(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """Invalidation removes all ghost entries for allocation."""
        # Store multiple patterns
        await sync_manager.store_with_sync(allocation, "c1", {"x": 1}, [1.0])
        await sync_manager.store_with_sync(allocation, "c2", {"x": 2}, [0.0])
        await sync_manager.store_with_sync(allocation, "c3", {"x": 3}, [0.5])

        assert len(ghost_cache.all_keys()) == 3

        # Invalidate
        count = await sync_manager.invalidate_for_allocation(
            allocation, reason="Test invalidation"
        )

        assert count == 3
        assert len(ghost_cache.all_keys()) == 0

        # Event recorded
        invalidate_events = [
            e for e in sync_manager.events if e.event_type == "invalidate"
        ]
        assert len(invalidate_events) == 1
        assert invalidate_events[0].metadata["count"] == 3

    def test_stats(self, sync_manager: GhostSyncManager[Any]) -> None:
        """Stats returns sync manager metrics."""
        stats = sync_manager.stats()

        assert "total_events" in stats
        assert "events_by_type" in stats
        assert "tracked_keys" in stats
        assert "ghost_entries" in stats


# =============================================================================
# GhostSyncAllocation Tests
# =============================================================================


class TestGhostSyncAllocation:
    """Tests for GhostSyncAllocation wrapper."""

    @pytest.mark.asyncio
    async def test_wrapped_store(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """Wrapped allocation syncs on store."""
        synced = wrap_with_ghost_sync(allocation, sync_manager)

        success = await synced.store("wrapped_concept", {"wrapped": True}, [1.0, 0.0])

        assert success is True
        assert synced.pattern_count == 1
        assert ghost_cache.read("alloc:test_agent:wrapped_concept") is not None

    @pytest.mark.asyncio
    async def test_wrapped_retrieve(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
    ) -> None:
        """Wrapped allocation retrieves normally."""
        synced = wrap_with_ghost_sync(allocation, sync_manager)

        await synced.store("concept", {"data": "test"}, [1.0, 0.0])
        results = await synced.retrieve([1.0, 0.0], threshold=0.5)

        # Results depend on crystal implementation
        assert isinstance(results, list)

    def test_attribute_delegation(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
    ) -> None:
        """Wrapper delegates unknown attributes to allocation."""
        synced = wrap_with_ghost_sync(allocation, sync_manager)

        assert synced.agent_id == allocation.agent_id
        assert synced.namespace == allocation.namespace
        assert synced.quota == allocation.quota


# =============================================================================
# GhostAwareReaperIntegration Tests
# =============================================================================


class TestGhostAwareReaperIntegration:
    """Tests for GhostAwareReaperIntegration."""

    @pytest.fixture
    def mock_reaper(self) -> Any:
        """Mock CrystalReaper for testing."""

        class MockReaper:
            def __init__(self) -> None:
                self._crystals: dict[str, Any] = {}

            def reap(self) -> Any:
                """Return empty reap result."""

                class ReapResult:
                    crystal_ids: list[str] = []

                return ReapResult()

        return MockReaper()

    @pytest.fixture
    def ghost_reaper(
        self,
        mock_reaper: Any,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> GhostAwareReaperIntegration[Any]:
        """Ghost-aware reaper for testing."""
        return create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)

    def test_reaper_creation(
        self, ghost_reaper: GhostAwareReaperIntegration[Any]
    ) -> None:
        """Ghost-aware reaper can be created."""
        assert ghost_reaper is not None
        assert len(ghost_reaper.events) == 0
        assert len(ghost_reaper.sync_events) == 0

    @pytest.mark.asyncio
    async def test_reap_all_invalidates_ghost(
        self,
        mock_reaper: Any,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """reap_all invalidates ghost entries for expired allocations."""
        # Create allocation with very short TTL
        allocation = substrate.allocate(
            agent_id="expiring_agent",
            quota=MemoryQuota(max_patterns=10),
            lifecycle=LifecyclePolicy(
                human_label="Expiring allocation",
                ttl=timedelta(seconds=-1),  # Already expired
            ),
        )

        # Store some patterns with ghost sync
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)
        await sync_manager.store_with_sync(allocation, "c1", {"x": 1}, [1.0])
        await sync_manager.store_with_sync(allocation, "c2", {"x": 2}, [0.0])

        assert len(ghost_cache.all_keys()) == 2

        # Create ghost-aware reaper
        ghost_reaper = create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)

        # Reap
        events = await ghost_reaper.reap_all()

        # Allocation was reaped
        assert len(events) == 1
        assert events[0].event_type == "reap"

        # Ghost entries were invalidated
        assert len(ghost_cache.all_keys()) == 0

    @pytest.mark.asyncio
    async def test_reap_allocation_with_sync(
        self,
        mock_reaper: Any,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """reap_allocation invalidates ghost entries for specific allocation."""
        allocation = substrate.allocate(
            agent_id="manual_reap",
            lifecycle=LifecyclePolicy(human_label="Manual reap test"),
        )

        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)
        await sync_manager.store_with_sync(allocation, "c1", {"x": 1}, [1.0])

        ghost_reaper = create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)

        # Reap specific allocation
        event = await ghost_reaper.reap_allocation(allocation, reason="Manual test")

        assert event.event_type == "reap"
        assert event.agent_id == "manual_reap"

        # Ghost invalidated
        assert len(ghost_cache.all_keys()) == 0

    def test_get_expiring_soon(
        self,
        mock_reaper: Any,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """get_expiring_soon delegates to base reaper."""
        allocation = substrate.allocate(
            agent_id="expiring_soon",
            lifecycle=LifecyclePolicy(
                human_label="Expiring soon",
                ttl=timedelta(minutes=30),
            ),
        )

        ghost_reaper = create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)

        expiring = ghost_reaper.get_expiring_soon(threshold=timedelta(hours=1))
        assert len(expiring) == 1
        assert str(expiring[0].agent_id) == "expiring_soon"

    def test_stats(self, ghost_reaper: GhostAwareReaperIntegration[Any]) -> None:
        """Stats includes both reaper and sync stats."""
        stats = ghost_reaper.stats()

        assert "total_reaps" in stats
        assert "ghost_sync" in stats
        assert "total_events" in stats["ghost_sync"]


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_ghost_sync_manager(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Factory creates working sync manager."""
        manager = create_ghost_sync_manager(ghost_cache, substrate)
        assert isinstance(manager, GhostSyncManager)

    def test_create_ghost_sync_manager_custom_prefix(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Factory respects custom key prefix."""
        manager = create_ghost_sync_manager(ghost_cache, substrate, key_prefix="custom")
        key = manager._make_ghost_key("agent", "concept")
        assert key.startswith("custom:")

    def test_create_ghost_aware_reaper(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Factory creates working ghost-aware reaper."""

        class MockReaper:
            def reap(self) -> Any:
                class Result:
                    crystal_ids: list[str] = []

                return Result()

        reaper = create_ghost_aware_reaper(MockReaper(), substrate, ghost_cache)
        assert isinstance(reaper, GhostAwareReaperIntegration)

    def test_wrap_with_ghost_sync(
        self,
        sync_manager: GhostSyncManager[Any],
        allocation: Any,
    ) -> None:
        """Factory creates working wrapped allocation."""
        synced = wrap_with_ghost_sync(allocation, sync_manager)
        assert isinstance(synced, GhostSyncAllocation)
        assert synced.allocation is allocation


# =============================================================================
# Integration Tests
# =============================================================================


class TestGhostSyncIntegration:
    """Integration tests for the full sync flow."""

    @pytest.mark.asyncio
    async def test_full_lifecycle(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test complete lifecycle: store → access → reap → invalidate."""
        # Setup
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        allocation = substrate.allocate(
            agent_id="lifecycle_test",
            lifecycle=LifecyclePolicy(
                human_label="Lifecycle test",
                ttl=timedelta(seconds=-1),  # Already expired
            ),
        )

        # 1. Store patterns with sync
        await sync_manager.store_with_sync(allocation, "pattern_1", {"a": 1}, [1.0])
        await sync_manager.store_with_sync(allocation, "pattern_2", {"b": 2}, [0.0])

        assert allocation.pattern_count == 2
        assert len(ghost_cache.all_keys()) == 2

        # 2. Ghost access touches allocation
        original_count = allocation.access_count
        sync_manager.on_ghost_access("alloc:lifecycle_test:pattern_1")
        assert allocation.access_count == original_count + 1

        # 3. Invalidate on reap
        await sync_manager.invalidate_for_allocation(
            allocation, reason="Lifecycle complete"
        )

        assert len(ghost_cache.all_keys()) == 0

        # 4. Check event history
        store_events = [
            e for e in sync_manager.events if e.event_type == "store_to_ghost"
        ]
        access_events = [
            e for e in sync_manager.events if e.event_type == "ghost_access"
        ]
        invalidate_events = [
            e for e in sync_manager.events if e.event_type == "invalidate"
        ]

        assert len(store_events) == 2
        assert len(access_events) == 1
        assert len(invalidate_events) == 1

    @pytest.mark.asyncio
    async def test_multiple_allocations_isolated(
        self,
        ghost_cache: LifecycleAwareCache,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Ghost entries from different allocations are isolated."""
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        alloc_a = substrate.allocate(
            agent_id="agent_a",
            lifecycle=LifecyclePolicy(human_label="Agent A"),
        )
        alloc_b = substrate.allocate(
            agent_id="agent_b",
            lifecycle=LifecyclePolicy(human_label="Agent B"),
        )

        # Store in both
        await sync_manager.store_with_sync(alloc_a, "c1", {"from": "a"}, [1.0])
        await sync_manager.store_with_sync(alloc_a, "c2", {"from": "a"}, [0.5])
        await sync_manager.store_with_sync(alloc_b, "c1", {"from": "b"}, [0.0])

        assert len(ghost_cache.all_keys()) == 3

        # Invalidate only A
        count = await sync_manager.invalidate_for_allocation(alloc_a, "Test")

        assert count == 2
        assert len(ghost_cache.all_keys()) == 1

        # B's entry still exists
        entry = ghost_cache.read("alloc:agent_b:c1")
        assert entry is not None
