"""
Integration Smoke Test: Full Memory Lifecycle.

Phase 8 of Memory Architecture - End-to-end validation.

Tests the complete flow:
AGENTESE → Substrate → Ghost → Crystallization → Reap
"""

import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any, Generator

import pytest
from agents.m.crystallization_integration import (
    CrystallizationEvent,
    ReaperIntegration,
    create_reaper_integration,
)
from agents.m.ghost_sync import (
    GhostAwareReaperIntegration,
    GhostSyncManager,
    create_ghost_aware_reaper,
    create_ghost_sync_manager,
    wrap_with_ghost_sync,
)
from agents.m.substrate import (
    LifecyclePolicy,
    MemoryQuota,
    SharedSubstrate,
    create_allocation_for_agent,
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
def mock_reaper() -> Any:
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


# =============================================================================
# Integration Smoke Tests
# =============================================================================


class TestFullMemoryLifecycle:
    """Integration tests for the complete memory lifecycle."""

    @pytest.mark.asyncio
    async def test_substrate_allocation_and_storage(
        self, substrate: SharedSubstrate[Any]
    ) -> None:
        """Test basic substrate allocation and pattern storage."""
        # 1. Allocate
        allocation = substrate.allocate(
            agent_id="smoke_test_1",
            quota=MemoryQuota(max_patterns=100),
            lifecycle=LifecyclePolicy(
                human_label="Smoke test allocation",
                ttl=timedelta(hours=1),
            ),
        )

        assert allocation is not None
        assert str(allocation.agent_id) == "smoke_test_1"
        assert allocation.pattern_count == 0

        # 2. Store patterns
        stored = await allocation.store(
            "concept_1", {"data": "first pattern"}, [1.0, 0.0, 0.0]
        )
        assert stored is True
        assert allocation.pattern_count == 1

        stored = await allocation.store(
            "concept_2", {"data": "second pattern"}, [0.0, 1.0, 0.0]
        )
        assert stored is True
        assert allocation.pattern_count == 2

        # 3. Retrieve by resonance
        results = await allocation.retrieve([1.0, 0.0, 0.0], threshold=0.5)
        assert isinstance(results, list)

        # 4. Check stats
        stats = substrate.stats()
        assert stats["allocation_count"] == 1
        assert stats["total_patterns"] == 2

    @pytest.mark.asyncio
    async def test_allocation_with_ghost_sync(
        self,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """Test allocation with ghost cache synchronization."""
        # Setup sync
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        allocation = substrate.allocate(
            agent_id="ghost_sync_test",
            lifecycle=LifecyclePolicy(
                human_label="Ghost sync test",
                ttl=timedelta(hours=1),
            ),
        )

        # Wrap with sync
        synced = wrap_with_ghost_sync(allocation, sync_manager)

        # Store with sync
        await synced.store("pattern_a", {"ghost": "test"}, [1.0, 0.0])

        # Verify allocation has pattern
        assert synced.pattern_count == 1

        # Verify ghost entry exists
        ghost_keys = ghost_cache.all_keys()
        assert len(ghost_keys) == 1
        assert "ghost_sync_test" in ghost_keys[0]

        # Ghost access touches allocation
        original_count = allocation.access_count
        sync_manager.on_ghost_access(ghost_keys[0])
        assert allocation.access_count == original_count + 1

    @pytest.mark.asyncio
    async def test_reaper_with_ghost_invalidation(
        self,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
        mock_reaper: Any,
    ) -> None:
        """Test reaper integration invalidates ghost entries."""
        # Create allocation that's already expired
        allocation = substrate.allocate(
            agent_id="expiring_test",
            lifecycle=LifecyclePolicy(
                human_label="Expiring test",
                ttl=timedelta(seconds=-1),  # Already expired
            ),
        )

        # Store with ghost sync
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)
        await sync_manager.store_with_sync(
            allocation, "ephemeral_1", {"temp": True}, [1.0]
        )
        await sync_manager.store_with_sync(
            allocation, "ephemeral_2", {"temp": True}, [0.0]
        )

        assert len(ghost_cache.all_keys()) == 2
        assert "expiring_test" in substrate.allocations

        # Reap with ghost sync
        ghost_reaper = create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)
        events = await ghost_reaper.reap_all()

        # Allocation reaped
        assert len(events) == 1
        assert events[0].event_type == "reap"
        assert "expiring_test" not in substrate.allocations

        # Ghost entries invalidated
        assert len(ghost_cache.all_keys()) == 0

    @pytest.mark.asyncio
    async def test_multiple_agents_isolated(
        self,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
        mock_reaper: Any,
    ) -> None:
        """Test that multiple agents have isolated allocations."""
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        # Agent A with short TTL (already expired)
        alloc_a = substrate.allocate(
            agent_id="agent_a",
            lifecycle=LifecyclePolicy(
                human_label="Agent A",
                ttl=timedelta(seconds=-1),
            ),
        )

        # Agent B with long TTL
        alloc_b = substrate.allocate(
            agent_id="agent_b",
            lifecycle=LifecyclePolicy(
                human_label="Agent B",
                ttl=timedelta(hours=24),
            ),
        )

        # Store patterns in both
        await sync_manager.store_with_sync(alloc_a, "a_pattern", {"agent": "a"}, [1.0])
        await sync_manager.store_with_sync(alloc_b, "b_pattern", {"agent": "b"}, [0.0])

        assert len(ghost_cache.all_keys()) == 2

        # Reap expired
        ghost_reaper = create_ghost_aware_reaper(mock_reaper, substrate, ghost_cache)
        events = await ghost_reaper.reap_all()

        # Only A was reaped
        assert len(events) == 1
        assert events[0].agent_id == "agent_a"

        # A's ghost gone, B's remains
        remaining_keys = ghost_cache.all_keys()
        assert len(remaining_keys) == 1
        assert "agent_b" in remaining_keys[0]

        # B still in substrate
        assert "agent_b" in substrate.allocations
        assert "agent_a" not in substrate.allocations

    @pytest.mark.asyncio
    async def test_promotion_flow(self, substrate: SharedSubstrate[Any]) -> None:
        """Test allocation promotion to dedicated crystal."""
        allocation = substrate.allocate(
            agent_id="promotable",
            lifecycle=LifecyclePolicy(
                human_label="Promotable allocation",
                ttl=timedelta(days=7),
            ),
        )

        # Store enough patterns to approach promotion threshold
        for i in range(50):
            await allocation.store(f"concept_{i}", {"i": i}, [float(i % 10) / 10])

        assert allocation.pattern_count == 50

        # Force promote
        dedicated = substrate.promote("promotable")

        assert dedicated is not None
        assert str(dedicated.agent_id) == "promotable"
        assert dedicated.crystal is not None

        # No longer in shared allocations
        assert "promotable" not in substrate.allocations
        assert "promotable" in substrate.dedicated_crystals

    @pytest.mark.asyncio
    async def test_demote_flow(self, substrate: SharedSubstrate[Any]) -> None:
        """Test demotion from dedicated back to shared."""
        allocation = substrate.allocate(
            agent_id="demotable",
            lifecycle=LifecyclePolicy(
                human_label="Demotable allocation",
                ttl=timedelta(days=1),
            ),
        )

        # Store and promote
        await allocation.store("c1", {"x": 1}, [1.0])
        substrate.promote("demotable")

        assert "demotable" in substrate.dedicated_crystals
        assert "demotable" not in substrate.allocations

        # Demote
        new_alloc = substrate.demote("demotable", compress_ratio=0.5)

        assert "demotable" in substrate.allocations
        assert "demotable" not in substrate.dedicated_crystals
        assert new_alloc.lifecycle.human_label == "demotable (demoted)"

    @pytest.mark.asyncio
    async def test_compaction_flow(self, substrate: SharedSubstrate[Any]) -> None:
        """Test memory compaction under pressure."""
        # Create allocation with low pressure threshold
        allocation = substrate.allocate(
            agent_id="compactable",
            quota=MemoryQuota(max_patterns=10, soft_limit_ratio=0.8),
            lifecycle=LifecyclePolicy(
                human_label="Compactable allocation",
                ttl=timedelta(hours=1),
            ),
        )

        # Fill to trigger compaction (9 patterns = 90% of 10)
        for i in range(9):
            await allocation.store(f"c_{i}", {"i": i}, [float(i) / 10])

        assert allocation.pattern_count == 9
        assert allocation.is_at_soft_limit()

        # Compact
        patterns_affected = await substrate.compact(allocation)

        # Compaction happened
        assert patterns_affected == 9  # All patterns affected by compression


class TestSubstrateStats:
    """Tests for substrate statistics."""

    @pytest.mark.asyncio
    async def test_stats_accuracy(self, substrate: SharedSubstrate[Any]) -> None:
        """Test that stats accurately reflect substrate state."""
        # Initial state
        stats = substrate.stats()
        assert stats["allocation_count"] == 0
        assert stats["dedicated_count"] == 0
        assert stats["total_patterns"] == 0

        # Add allocations
        alloc1 = substrate.allocate(
            "agent_1", lifecycle=LifecyclePolicy(human_label="Agent 1")
        )
        alloc2 = substrate.allocate(
            "agent_2", lifecycle=LifecyclePolicy(human_label="Agent 2")
        )

        await alloc1.store("c1", {"x": 1}, [1.0])
        await alloc2.store("c2", {"x": 2}, [0.0])
        await alloc2.store("c3", {"x": 3}, [0.5])

        stats = substrate.stats()
        assert stats["allocation_count"] == 2
        assert stats["total_patterns"] == 3

        # Promote one
        substrate.promote("agent_1")

        stats = substrate.stats()
        assert stats["allocation_count"] == 1
        assert stats["dedicated_count"] == 1


class TestGhostSyncStats:
    """Tests for ghost sync statistics."""

    @pytest.mark.asyncio
    async def test_sync_stats(
        self,
        substrate: SharedSubstrate[Any],
        ghost_cache: LifecycleAwareCache,
    ) -> None:
        """Test sync manager stats accuracy."""
        sync_manager = create_ghost_sync_manager(ghost_cache, substrate)

        allocation = substrate.allocate(
            agent_id="stats_test",
            lifecycle=LifecyclePolicy(human_label="Stats test"),
        )

        # Initial stats
        stats = sync_manager.stats()
        assert stats["total_events"] == 0

        # Store
        await sync_manager.store_with_sync(allocation, "c1", {"x": 1}, [1.0])

        stats = sync_manager.stats()
        assert stats["total_events"] == 1
        assert stats["events_by_type"]["store_to_ghost"] == 1

        # Access
        sync_manager.on_ghost_access("alloc:stats_test:c1")

        stats = sync_manager.stats()
        assert stats["total_events"] == 2
        assert stats["events_by_type"]["ghost_access"] == 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_store_quota_exceeded(self, substrate: SharedSubstrate[Any]) -> None:
        """Test behavior when quota is exceeded."""
        allocation = substrate.allocate(
            agent_id="quota_test",
            quota=MemoryQuota(max_patterns=2),
            lifecycle=LifecyclePolicy(human_label="Quota test"),
        )

        # Fill quota
        await allocation.store("c1", {"x": 1}, [1.0])
        await allocation.store("c2", {"x": 2}, [0.0])

        # Try to exceed
        success = await allocation.store("c3", {"x": 3}, [0.5])
        assert success is False
        assert allocation.pattern_count == 2

    def test_double_allocation(self, substrate: SharedSubstrate[Any]) -> None:
        """Test allocating same agent twice returns existing."""
        alloc1 = substrate.allocate(
            "double", lifecycle=LifecyclePolicy(human_label="First")
        )
        alloc2 = substrate.allocate(
            "double", lifecycle=LifecyclePolicy(human_label="Second")
        )

        # Should return same allocation
        assert alloc1 is alloc2

    def test_allocation_without_label_fails(
        self, substrate: SharedSubstrate[Any]
    ) -> None:
        """Test that allocation without human_label fails."""
        with pytest.raises(ValueError, match="human_label required"):
            substrate.allocate("no_label")

    def test_promote_unknown_fails(self, substrate: SharedSubstrate[Any]) -> None:
        """Test promoting unknown agent fails."""
        with pytest.raises(ValueError, match="No allocation"):
            substrate.promote("unknown_agent")

    def test_demote_non_dedicated_fails(self, substrate: SharedSubstrate[Any]) -> None:
        """Test demoting non-dedicated agent fails."""
        substrate.allocate(
            "not_dedicated", lifecycle=LifecyclePolicy(human_label="Not dedicated")
        )

        with pytest.raises(ValueError, match="No dedicated crystal"):
            substrate.demote("not_dedicated")


class TestCrystallizationEventFlow:
    """Tests for crystallization events in reaper flow."""

    @pytest.mark.asyncio
    async def test_reap_events_contain_metadata(
        self,
        substrate: SharedSubstrate[Any],
        mock_reaper: Any,
    ) -> None:
        """Test that reap events contain useful metadata."""
        allocation = substrate.allocate(
            agent_id="event_test",
            lifecycle=LifecyclePolicy(
                human_label="Event test",
                ttl=timedelta(seconds=-1),
            ),
        )

        # Store patterns
        await allocation.store("c1", {"x": 1}, [1.0])
        await allocation.store("c2", {"x": 2}, [0.0])

        reaper_integration = create_reaper_integration(mock_reaper, substrate)
        events = await reaper_integration.reap_all()

        assert len(events) == 1
        event = events[0]

        assert event.event_type == "reap"
        assert event.agent_id == "event_test"
        assert event.patterns_affected == 2
        assert event.reason.startswith("Allocation TTL expired")

    @pytest.mark.asyncio
    async def test_expiring_soon(
        self,
        substrate: SharedSubstrate[Any],
        mock_reaper: Any,
    ) -> None:
        """Test finding allocations expiring soon."""
        # Expiring in 30 minutes
        substrate.allocate(
            agent_id="soon",
            lifecycle=LifecyclePolicy(
                human_label="Expiring soon",
                ttl=timedelta(minutes=30),
            ),
        )

        # Expiring in 2 hours
        substrate.allocate(
            agent_id="later",
            lifecycle=LifecyclePolicy(
                human_label="Expiring later",
                ttl=timedelta(hours=2),
            ),
        )

        reaper_integration = create_reaper_integration(mock_reaper, substrate)

        # Check 1 hour threshold
        expiring = reaper_integration.get_expiring_soon(threshold=timedelta(hours=1))
        assert len(expiring) == 1
        assert str(expiring[0].agent_id) == "soon"
