"""
Tests for K-gent memory allocation integration.

Phase 6 tests for K-gent's substrate integration.
"""

from datetime import datetime, timedelta
from typing import Any

import pytest
from agents.k.memory_allocation import (
    AllocationStats,
    KgentAllocationManager,
    KgentMemoryProfile,
    KgentPheromoneDepositor,
    create_kgent_allocation,
    create_kgent_depositor,
)
from agents.m.stigmergy import PheromoneField
from agents.m.substrate import MemoryQuota, SharedSubstrate, create_substrate

# =============================================================================
# KgentMemoryProfile Tests
# =============================================================================


class TestKgentMemoryProfile:
    """Tests for KgentMemoryProfile."""

    def test_default_profile(self) -> None:
        """Default profile should have sensible defaults."""
        profile = KgentMemoryProfile()

        assert profile.working_memory_max_patterns == 500
        assert profile.eigenvector_max_patterns == 50
        assert profile.dialogue_max_patterns == 1000
        assert profile.dream_max_patterns == 200

    def test_total_max_patterns(self) -> None:
        """Total should sum all tiers."""
        profile = KgentMemoryProfile()
        total = profile.total_max_patterns()
        assert total == 500 + 50 + 1000 + 200  # 1750

    def test_custom_profile(self) -> None:
        """Should accept custom values."""
        profile = KgentMemoryProfile(
            working_memory_max_patterns=100,
            dialogue_max_patterns=200,
        )
        assert profile.working_memory_max_patterns == 100
        assert profile.dialogue_max_patterns == 200

    def test_ttl_defaults(self) -> None:
        """TTL defaults should be reasonable."""
        profile = KgentMemoryProfile()

        assert profile.working_memory_ttl == timedelta(hours=4)
        assert profile.eigenvector_ttl == timedelta(days=30)
        assert profile.dialogue_ttl == timedelta(days=7)
        assert profile.dream_ttl == timedelta(days=14)


# =============================================================================
# KgentAllocationManager Tests
# =============================================================================


class TestKgentAllocationManager:
    """Tests for KgentAllocationManager."""

    @pytest.fixture
    def substrate(self) -> SharedSubstrate[Any]:
        return create_substrate()

    @pytest.fixture
    def profile(self) -> KgentMemoryProfile:
        return KgentMemoryProfile(
            working_memory_max_patterns=100,
            eigenvector_max_patterns=20,
            dialogue_max_patterns=200,
            dream_max_patterns=50,
        )

    @pytest.fixture
    def manager(
        self, substrate: SharedSubstrate[Any], profile: KgentMemoryProfile
    ) -> KgentAllocationManager:
        return KgentAllocationManager(substrate, profile)

    def test_not_initialized_initially(self, manager: KgentAllocationManager) -> None:
        """Manager should not be initialized before calling initialize()."""
        assert manager.is_initialized is False

    @pytest.mark.asyncio
    async def test_initialize_creates_allocations(
        self, substrate: SharedSubstrate[Any], manager: KgentAllocationManager
    ) -> None:
        """Initialize should create four allocations."""
        await manager.initialize()

        assert manager.is_initialized is True
        assert "kgent:working" in [str(k) for k in substrate.allocations.keys()]
        assert "kgent:eigenvector" in [str(k) for k in substrate.allocations.keys()]
        assert "kgent:dialogue" in [str(k) for k in substrate.allocations.keys()]
        assert "kgent:dream" in [str(k) for k in substrate.allocations.keys()]

    @pytest.mark.asyncio
    async def test_store_working(self, manager: KgentAllocationManager) -> None:
        """Should store patterns in working memory."""
        await manager.initialize()

        embedding = [0.1, 0.2, 0.3]
        success = await manager.store_working("context_1", {"data": "test"}, embedding)
        assert success is True

    @pytest.mark.asyncio
    async def test_store_eigenvector(self, manager: KgentAllocationManager) -> None:
        """Should store eigenvector values."""
        await manager.initialize()

        embedding = [0.1, 0.2, 0.3]
        success = await manager.store_eigenvector("aesthetic", 0.8, embedding)
        assert success is True

    @pytest.mark.asyncio
    async def test_store_dialogue(self, manager: KgentAllocationManager) -> None:
        """Should store dialogue turns and track interactions."""
        await manager.initialize()

        embedding = [0.1, 0.2, 0.3]
        initial_count = manager.interaction_count

        success = await manager.store_dialogue(
            turn_id="turn_1",
            message="Hello",
            response="Hi there",
            mode="reflect",
            embedding=embedding,
        )

        assert success is True
        assert manager.interaction_count == initial_count + 1

    @pytest.mark.asyncio
    async def test_store_dream(self, manager: KgentAllocationManager) -> None:
        """Should store dream patterns."""
        await manager.initialize()

        embedding = [0.1, 0.2, 0.3]
        success = await manager.store_dream(
            pattern_id="pattern_1",
            content={"insight": "test insight"},
            embedding=embedding,
        )
        assert success is True

    @pytest.mark.asyncio
    async def test_should_promote_by_interactions(
        self, manager: KgentAllocationManager, profile: KgentMemoryProfile
    ) -> None:
        """Should recommend promotion when interactions exceed threshold."""
        await manager.initialize()

        # Initially should not promote
        assert manager.should_promote() is False

        # Simulate many interactions
        embedding = [0.1, 0.2, 0.3]
        for i in range(profile.dialogue_promotion_threshold + 1):
            await manager.store_dialogue(
                turn_id=f"turn_{i}",
                message=f"message {i}",
                response=f"response {i}",
                mode="reflect",
                embedding=embedding,
            )

        assert manager.should_promote() is True

    @pytest.mark.asyncio
    async def test_stats(self, manager: KgentAllocationManager) -> None:
        """Should return allocation statistics."""
        await manager.initialize()

        # Store some patterns
        embedding = [0.1, 0.2, 0.3]
        await manager.store_working("w1", {}, embedding)
        await manager.store_working("w2", {}, embedding)
        await manager.store_dialogue("d1", "msg", "resp", "reflect", embedding)

        stats = manager.stats()

        assert isinstance(stats, AllocationStats)
        assert stats.working_memory_used == 2
        assert stats.dialogue_used == 1
        assert stats.total_used == 3
        assert stats.usage_ratio > 0

    @pytest.mark.asyncio
    async def test_not_initialized_raises(
        self, manager: KgentAllocationManager
    ) -> None:
        """Operations should raise if not initialized."""
        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.store_working("test", {}, [0.1])


# =============================================================================
# KgentPheromoneDepositor Tests
# =============================================================================


class TestKgentPheromoneDepositor:
    """Tests for KgentPheromoneDepositor."""

    @pytest.fixture
    def field(self) -> PheromoneField:
        return PheromoneField(decay_rate=0.0)

    @pytest.fixture
    def depositor(self, field: PheromoneField) -> KgentPheromoneDepositor:
        return KgentPheromoneDepositor(field)

    @pytest.mark.asyncio
    async def test_deposit_dialogue(
        self, field: PheromoneField, depositor: KgentPheromoneDepositor
    ) -> None:
        """Should deposit dialogue trace."""
        await depositor.deposit_dialogue("reflect", intensity=1.0)

        # Verify trace exists
        traces = await field.sense()
        assert any("soul.dialogue.reflect" in t.concept for t in traces)

    @pytest.mark.asyncio
    async def test_deposit_eigenvector(
        self, field: PheromoneField, depositor: KgentPheromoneDepositor
    ) -> None:
        """Should deposit eigenvector trace with intensity from value."""
        await depositor.deposit_eigenvector("aesthetic", 0.8)

        traces = await field.sense()
        matching = [t for t in traces if "soul.eigenvector.aesthetic" in t.concept]
        assert len(matching) == 1
        assert matching[0].total_intensity == pytest.approx(0.8)

    @pytest.mark.asyncio
    async def test_deposit_pattern(
        self, field: PheromoneField, depositor: KgentPheromoneDepositor
    ) -> None:
        """Should deposit pattern trace."""
        await depositor.deposit_pattern("behavior", "pattern_123", intensity=1.5)

        traces = await field.sense()
        assert any("soul.pattern.behavior" in t.concept for t in traces)

    @pytest.mark.asyncio
    async def test_deposit_emotional_state(
        self, field: PheromoneField, depositor: KgentPheromoneDepositor
    ) -> None:
        """Should deposit emotional state trace."""
        await depositor.deposit_emotional_state("curious", intensity=0.9)

        traces = await field.sense()
        assert any("soul.emotion.curious" in t.concept for t in traces)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.mark.asyncio
    async def test_create_kgent_allocation(self) -> None:
        """Should create and initialize manager."""
        substrate = create_substrate()
        manager = await create_kgent_allocation(substrate)

        assert manager.is_initialized is True
        assert len(substrate.allocations) == 4

    @pytest.mark.asyncio
    async def test_create_kgent_allocation_with_profile(self) -> None:
        """Should accept custom profile."""
        substrate = create_substrate()
        profile = KgentMemoryProfile(working_memory_max_patterns=50)
        manager = await create_kgent_allocation(substrate, profile)

        assert manager.is_initialized is True

    def test_create_kgent_depositor(self) -> None:
        """Should create depositor."""
        field = PheromoneField()
        depositor = create_kgent_depositor(field)

        assert isinstance(depositor, KgentPheromoneDepositor)


# =============================================================================
# AllocationStats Tests
# =============================================================================


class TestAllocationStats:
    """Tests for AllocationStats."""

    def test_default_stats(self) -> None:
        """Default stats should be zeros."""
        stats = AllocationStats()

        assert stats.working_memory_used == 0
        assert stats.eigenvector_used == 0
        assert stats.dialogue_used == 0
        assert stats.dream_used == 0
        assert stats.total_used == 0
        assert stats.promotion_eligible is False

    def test_stats_with_values(self) -> None:
        """Stats should accept values."""
        stats = AllocationStats(
            working_memory_used=100,
            dialogue_used=500,
            total_used=600,
            total_capacity=1000,
            usage_ratio=0.6,
            promotion_eligible=True,
        )

        assert stats.working_memory_used == 100
        assert stats.dialogue_used == 500
        assert stats.usage_ratio == 0.6
        assert stats.promotion_eligible is True
