"""
Tests for Crystallization Integration (Phase 7).

Tests the bridge between:
- CrystallizationEngine (D-gent)
- SharedSubstrate (M-gent)
- CrystalReaper (D-gent)
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from agents.d.context_window import ContextWindow, TurnRole
from agents.d.crystal import (
    CrystallizationEngine,
    CrystalReaper,
    TaskState,
    TaskStatus,
    create_task_state,
)
from agents.m.compaction import Compactor, create_compactor
from agents.m.crystallization_integration import (
    CrystallizationEvent,
    KgentCrystallizer,
    ReaperIntegration,
    SubstrateCrystallizer,
    create_kgent_crystallizer,
    create_reaper_integration,
    create_substrate_crystallizer,
)
from agents.m.substrate import (
    Allocation,
    LifecyclePolicy,
    MemoryQuota,
    SharedSubstrate,
    create_substrate,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def substrate() -> SharedSubstrate[Any]:
    """Create a test substrate."""
    return create_substrate()


@pytest.fixture
def reaper() -> CrystalReaper:
    """Create a test reaper."""
    return CrystalReaper()


@pytest.fixture
def engine(reaper: CrystalReaper) -> CrystallizationEngine:
    """Create a test crystallization engine."""
    return CrystallizationEngine(reaper=reaper)


@pytest.fixture
def compactor() -> Compactor[Any]:
    """Create a test compactor."""
    return create_compactor()


@pytest.fixture
def allocation(substrate: SharedSubstrate[Any]) -> Allocation[Any]:
    """Create a test allocation."""
    return substrate.allocate(
        agent_id="test_agent",
        quota=MemoryQuota(max_patterns=100),
        lifecycle=LifecyclePolicy(
            human_label="Test allocation",
            ttl=timedelta(hours=1),
        ),
    )


@pytest.fixture
def window() -> ContextWindow:
    """Create a test context window."""
    window = ContextWindow(max_tokens=10000)
    window.append(TurnRole.SYSTEM, "You are a helpful assistant.")
    window.append(TurnRole.USER, "Hello, how are you?")
    window.append(TurnRole.ASSISTANT, "I'm doing well, thank you!")
    return window


@pytest.fixture
def task_state() -> TaskState:
    """Create a test task state."""
    return create_task_state(
        task_id="test_task",
        description="Testing crystallization integration",
        status=TaskStatus.ACTIVE,
    )


# =============================================================================
# CrystallizationEvent Tests
# =============================================================================


class TestCrystallizationEvent:
    """Tests for CrystallizationEvent."""

    def test_event_creation(self) -> None:
        """Test creating a crystallization event."""
        from datetime import datetime

        event = CrystallizationEvent(
            timestamp=datetime.now(),
            event_type="crystallize",
            agent_id="test_agent",
            crystal_id="crystal_123",
            patterns_affected=50,
            resolution_before=1.0,
            resolution_after=0.8,
            duration_ms=100.0,
            reason="Test crystallization",
        )

        assert event.event_type == "crystallize"
        assert event.agent_id == "test_agent"
        assert event.crystal_id == "crystal_123"
        assert event.patterns_affected == 50
        assert event.resolution_loss == pytest.approx(0.2)

    def test_event_resolution_loss(self) -> None:
        """Test resolution loss calculation."""
        from datetime import datetime

        event = CrystallizationEvent(
            timestamp=datetime.now(),
            event_type="reap",
            agent_id="test",
            resolution_before=1.0,
            resolution_after=0.5,
        )

        assert event.resolution_loss == pytest.approx(0.5)


# =============================================================================
# SubstrateCrystallizer Tests
# =============================================================================


class TestSubstrateCrystallizer:
    """Tests for SubstrateCrystallizer."""

    @pytest.mark.asyncio
    async def test_crystallize_allocation(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
        allocation: Allocation[Any],
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test crystallizing an allocation."""
        crystallizer = create_substrate_crystallizer(engine, substrate)

        # Store some patterns
        await allocation.store("concept_1", "test data", [1.0, 0.0, 0.0])
        await allocation.store("concept_2", "more data", [0.0, 1.0, 0.0])

        event = await crystallizer.crystallize_allocation(
            allocation=allocation,
            agent="test_agent",
            task_state=task_state,
            window=window,
        )

        assert event.event_type == "crystallize"
        assert event.agent_id == str(allocation.agent_id)
        assert event.crystal_id is not None
        assert event.patterns_affected == 2

    @pytest.mark.asyncio
    async def test_crystallize_on_promotion(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test crystallization on promotion conditions."""
        crystallizer = create_substrate_crystallizer(engine, substrate)

        # Create allocation with low threshold for testing
        allocation = substrate.allocate(
            agent_id="promo_agent",
            quota=MemoryQuota(max_patterns=10),
            lifecycle=LifecyclePolicy(human_label="Promotion test"),
        )

        # Not enough for promotion yet
        event = await crystallizer.crystallize_on_promotion(
            allocation=allocation,
            agent="promo_agent",
            task_state=task_state,
            window=window,
        )
        assert event is None  # Should not promote young allocation

    @pytest.mark.asyncio
    async def test_crystallize_with_compaction(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
        compactor: Compactor[Any],
        allocation: Allocation[Any],
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test crystallization followed by compaction."""
        crystallizer = create_substrate_crystallizer(engine, substrate, compactor)

        # Store patterns to create pressure
        for i in range(50):
            await allocation.store(f"concept_{i}", f"data_{i}", [float(i), 0.0, 0.0])

        crystal_event, compact_event = await crystallizer.crystallize_with_compaction(
            allocation=allocation,
            agent="test_agent",
            task_state=task_state,
            window=window,
            compress_ratio=0.8,
        )

        assert crystal_event.event_type == "crystallize"
        assert crystal_event.crystal_id is not None
        assert compact_event is not None
        assert compact_event.ratio == 0.8

    def test_crystallizer_stats(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test crystallizer statistics."""
        crystallizer = create_substrate_crystallizer(engine, substrate)

        stats = crystallizer.stats()
        assert stats["total_crystallizations"] == 0
        assert stats["successful"] == 0
        assert stats["failed"] == 0


# =============================================================================
# ReaperIntegration Tests
# =============================================================================


class TestReaperIntegration:
    """Tests for ReaperIntegration."""

    @pytest.mark.asyncio
    async def test_reap_expired_allocations(
        self,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test reaping expired allocations."""
        integration = create_reaper_integration(reaper, substrate)

        # Create an allocation with very short TTL
        allocation = substrate.allocate(
            agent_id="expiring_agent",
            quota=MemoryQuota(max_patterns=10),
            lifecycle=LifecyclePolicy(
                human_label="Short-lived allocation",
                ttl=timedelta(seconds=-1),  # Already expired
            ),
        )

        assert "expiring_agent" in [str(a) for a in substrate.allocations.keys()]

        events = await integration.reap_all()

        # Should have reaped the expired allocation
        expired_events = [e for e in events if e.agent_id == "expiring_agent"]
        assert len(expired_events) == 1
        assert expired_events[0].event_type == "reap"
        assert "expiring_agent" not in [str(a) for a in substrate.allocations.keys()]

    @pytest.mark.asyncio
    async def test_reap_specific_allocation(
        self,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
        allocation: Allocation[Any],
    ) -> None:
        """Test reaping a specific allocation."""
        integration = create_reaper_integration(reaper, substrate)

        await allocation.store("concept_1", "data", [1.0, 0.0])

        event = await integration.reap_allocation(
            allocation=allocation,
            reason="Manual cleanup",
        )

        assert event.event_type == "reap"
        assert event.patterns_affected == 1
        assert event.reason == "Manual cleanup"
        assert allocation.agent_id not in substrate.allocations

    def test_get_expiring_soon(
        self,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test finding allocations expiring soon."""
        integration = create_reaper_integration(reaper, substrate)

        # Create allocation expiring soon (30 minutes)
        expiring = substrate.allocate(
            agent_id="expiring_soon",
            lifecycle=LifecyclePolicy(
                human_label="Expiring soon",
                ttl=timedelta(minutes=30),
            ),
        )

        # Create allocation not expiring soon (24 hours)
        not_expiring = substrate.allocate(
            agent_id="not_expiring",
            lifecycle=LifecyclePolicy(
                human_label="Long-lived",
                ttl=timedelta(hours=24),
            ),
        )

        expiring_list = integration.get_expiring_soon(threshold=timedelta(hours=1))

        assert expiring in expiring_list
        assert not_expiring not in expiring_list

    def test_reaper_stats(
        self,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test reaper integration statistics."""
        integration = create_reaper_integration(reaper, substrate)

        stats = integration.stats()
        assert stats["total_reaps"] == 0
        assert stats["crystals_reaped"] == 0
        assert stats["allocations_reaped"] == 0


# =============================================================================
# KgentCrystallizer Tests
# =============================================================================


class TestKgentCrystallizer:
    """Tests for KgentCrystallizer."""

    @pytest.fixture
    async def kgent_manager(self, substrate: SharedSubstrate[Any]) -> Any:
        """Create a K-gent allocation manager."""
        from agents.k.memory_allocation import KgentAllocationManager

        manager = KgentAllocationManager(substrate, agent_id="kgent")
        await manager.initialize()
        return manager

    @pytest.mark.asyncio
    async def test_crystallize_dialogue_if_needed(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
        kgent_manager: Any,
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test conditional dialogue crystallization."""
        kgent_crystallizer = create_kgent_crystallizer(
            engine=engine,
            substrate=substrate,
            allocation_manager=kgent_manager,
        )

        # Should not crystallize when not at threshold
        event = await kgent_crystallizer.crystallize_dialogue_if_needed(
            window=window,
            task_state=task_state,
        )
        assert event is None  # Not enough interactions

        # Simulate many interactions to trigger promotion
        for i in range(150):
            await kgent_manager.store_dialogue(
                turn_id=f"turn_{i}",
                message=f"User message {i}",
                response=f"Response {i}",
                mode="reflect",
                embedding=[float(i), 0.0, 0.0],
            )

        # Now should crystallize
        assert kgent_manager.should_promote()
        event = await kgent_crystallizer.crystallize_dialogue_if_needed(
            window=window,
            task_state=task_state,
        )
        assert event is not None
        assert event.event_type == "crystallize"

    @pytest.mark.asyncio
    async def test_crystallize_dreams(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
        kgent_manager: Any,
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test dream pattern crystallization."""
        kgent_crystallizer = create_kgent_crystallizer(
            engine=engine,
            substrate=substrate,
            allocation_manager=kgent_manager,
        )

        # Store some dream patterns
        await kgent_manager.store_dream("dream_1", {"pattern": "recurring"}, [1.0, 0.0])
        await kgent_manager.store_dream("dream_2", {"pattern": "new"}, [0.0, 1.0])

        event = await kgent_crystallizer.crystallize_dreams(
            window=window,
            task_state=task_state,
        )

        assert event is not None
        assert event.event_type == "crystallize"
        assert (
            "dream_patterns" in event.metadata.get("note", "")
            or event.patterns_affected == 2
        )


# =============================================================================
# Integration Tests
# =============================================================================


class TestFullIntegration:
    """Full integration tests for crystallization workflow."""

    @pytest.mark.asyncio
    async def test_crystallize_reap_cycle(
        self,
        engine: CrystallizationEngine,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
        window: ContextWindow,
        task_state: TaskState,
    ) -> None:
        """Test the full crystallize → reap cycle."""
        crystallizer = create_substrate_crystallizer(engine, substrate)
        reaper_integration = create_reaper_integration(reaper, substrate)

        # Create allocation
        allocation = substrate.allocate(
            agent_id="lifecycle_test",
            lifecycle=LifecyclePolicy(
                human_label="Lifecycle test",
                ttl=timedelta(hours=1),
            ),
        )

        # Store patterns
        await allocation.store("concept_1", "data", [1.0, 0.0])

        # Crystallize
        crystal_event = await crystallizer.crystallize_allocation(
            allocation=allocation,
            agent="lifecycle_test",
            task_state=task_state,
            window=window,
        )

        assert crystal_event.crystal_id is not None

        # Verify crystal exists
        crystal = engine.get_crystal(crystal_event.crystal_id)
        assert crystal is not None

        # Manually reap the allocation
        reap_event = await reaper_integration.reap_allocation(
            allocation=allocation,
            reason="Test cleanup",
        )

        assert reap_event.event_type == "reap"
        assert allocation.agent_id not in substrate.allocations

        # Crystal should still exist (crystals and allocations are independent)
        crystal = engine.get_crystal(crystal_event.crystal_id)
        assert crystal is not None

    @pytest.mark.asyncio
    async def test_working_memory_lifecycle(
        self,
        engine: CrystallizationEngine,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test working memory lifecycle with crystallization."""
        from agents.k.memory_allocation import (
            KgentAllocationManager,
            KgentMemoryProfile,
        )

        # Configure short TTL for working memory
        profile = KgentMemoryProfile(
            working_memory_ttl=timedelta(seconds=-1),  # Already expired for test
            dialogue_promotion_threshold=10,
        )

        manager = KgentAllocationManager(
            substrate, profile=profile, agent_id="kgent_test"
        )
        await manager.initialize()

        # Store some working memory
        await manager.store_working("context_1", {"data": "test"}, [1.0, 0.0])

        # Check crystallize returns proper info
        info = await manager.crystallize("working")
        assert info["tier"] == "working"
        assert info["ready_for_crystallization"] is True
        assert info["pattern_count"] == 1

        # Reaper integration
        reaper_integration = create_reaper_integration(reaper, substrate)

        # Reap expired (working memory with negative TTL)
        events = await reaper_integration.reap_all()

        # Working memory allocation should be reaped
        working_events = [e for e in events if "working" in e.agent_id.lower()]
        assert len(working_events) > 0


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_substrate_crystallizer(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test substrate crystallizer factory."""
        crystallizer = create_substrate_crystallizer(engine, substrate)
        assert crystallizer is not None
        assert crystallizer.stats()["total_crystallizations"] == 0

    def test_create_reaper_integration(
        self,
        reaper: CrystalReaper,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test reaper integration factory."""
        integration = create_reaper_integration(reaper, substrate)
        assert integration is not None
        assert integration.stats()["total_reaps"] == 0

    @pytest.mark.asyncio
    async def test_create_kgent_crystallizer(
        self,
        engine: CrystallizationEngine,
        substrate: SharedSubstrate[Any],
    ) -> None:
        """Test K-gent crystallizer factory."""
        from agents.k.memory_allocation import KgentAllocationManager

        manager = KgentAllocationManager(substrate, agent_id="kgent_factory")
        await manager.initialize()

        kgent_crystallizer = create_kgent_crystallizer(
            engine=engine,
            substrate=substrate,
            allocation_manager=manager,
        )

        assert kgent_crystallizer is not None
