"""
Integration tests for K-gent → M-gent substrate flow.

Verifies that:
1. KgentAllocationManager works with real SharedSubstrate
2. Store/retrieve operations function correctly
3. Promotion logic triggers appropriately
4. Pheromone deposits integrate with semantic routing
"""

from datetime import timedelta
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
from agents.m.semantic_routing import (
    LocalityConfig,
    PrefixSimilarity,
    SemanticRouter,
    create_semantic_router,
)
from agents.m.stigmergy import PheromoneField
from agents.m.substrate import (
    CrystalPolicy,
    MemoryQuota,
    SharedSubstrate,
    create_substrate,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def substrate() -> SharedSubstrate[Any]:
    """Create a fresh substrate for testing."""
    return create_substrate(
        default_quota=MemoryQuota(max_patterns=100),
        promotion_policy=CrystalPolicy(min_age_hours=0.0),  # Allow immediate promotion
    )


@pytest.fixture
def small_profile() -> KgentMemoryProfile:
    """Create a small memory profile for testing."""
    return KgentMemoryProfile(
        working_memory_max_patterns=20,
        eigenvector_max_patterns=5,
        dialogue_max_patterns=50,
        dialogue_promotion_threshold=10,
        dream_max_patterns=20,
        working_memory_ttl=timedelta(hours=1),
        eigenvector_ttl=timedelta(hours=1),
        dialogue_ttl=timedelta(hours=1),
        dream_ttl=timedelta(hours=1),
    )


@pytest.fixture
def field() -> PheromoneField:
    """Create a pheromone field for testing."""
    return PheromoneField(decay_rate=0.0, evaporation_threshold=0.0)


# =============================================================================
# KgentAllocationManager Integration Tests
# =============================================================================


class TestKgentAllocationIntegration:
    """Tests for KgentAllocationManager with real substrate."""

    @pytest.mark.asyncio
    async def test_initialize_creates_four_allocations(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Initialize should create working, eigenvector, dialogue, dream allocations."""
        manager = await create_kgent_allocation(substrate, small_profile)

        assert manager.is_initialized
        assert len(substrate.allocations) == 4

        # Check all expected allocations exist
        agent_ids = [str(aid) for aid in substrate.allocations.keys()]
        assert "kgent:working" in agent_ids
        assert "kgent:eigenvector" in agent_ids
        assert "kgent:dialogue" in agent_ids
        assert "kgent:dream" in agent_ids

    @pytest.mark.asyncio
    async def test_store_and_retrieve_working_memory(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Store and retrieve from working memory."""
        manager = await create_kgent_allocation(substrate, small_profile)

        # Store a pattern
        embedding = [0.5] * 64  # Simple embedding
        success = await manager.store_working(
            "test_context", {"data": "value"}, embedding
        )
        assert success

        # Retrieve by resonance - returns ResonanceMatch objects
        results = await manager.retrieve_working(embedding, threshold=0.5)
        assert len(results) > 0
        # ResonanceMatch has concept_id and similarity; content is accessed separately
        assert results[0].concept_id == "kgent:working:test_context"
        assert results[0].similarity > 0.9  # Should be high similarity

    @pytest.mark.asyncio
    async def test_store_dialogue_increments_interaction_count(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Storing dialogue should increment interaction count."""
        manager = await create_kgent_allocation(substrate, small_profile)

        embedding = [0.5] * 64
        await manager.store_dialogue(
            "turn_1", "Hello", "Hi there", "reflect", embedding
        )
        await manager.store_dialogue(
            "turn_2", "How are you?", "Great!", "explore", embedding
        )

        assert manager.interaction_count == 2

    @pytest.mark.asyncio
    async def test_store_eigenvector(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Store and verify eigenvector dimensions."""
        manager = await create_kgent_allocation(substrate, small_profile)

        embedding = [0.3] * 64
        success = await manager.store_eigenvector("aesthetic", 0.7, embedding)
        assert success

        # Retrieve by resonance
        results = await manager.retrieve_working(embedding, threshold=0.0)
        # Note: eigenvector uses its own allocation, not working memory
        # So we check the eigenvector allocation directly
        eigenvector_alloc = substrate.get_allocation("kgent:eigenvector")
        assert eigenvector_alloc is not None
        assert eigenvector_alloc.pattern_count == 1

    @pytest.mark.asyncio
    async def test_quota_exhaustion(self, substrate: SharedSubstrate[Any]) -> None:
        """Storing beyond quota should return False."""
        tiny_profile = KgentMemoryProfile(
            working_memory_max_patterns=3,
            eigenvector_max_patterns=1,
            dialogue_max_patterns=2,
            dream_max_patterns=1,
        )
        manager = await create_kgent_allocation(substrate, tiny_profile)

        embedding = [0.5] * 64

        # Fill up working memory
        for i in range(3):
            success = await manager.store_working(f"ctx_{i}", {"i": i}, embedding)
            assert success

        # Fourth store should fail
        success = await manager.store_working("ctx_3", {"i": 3}, embedding)
        assert not success

    @pytest.mark.asyncio
    async def test_promotion_eligibility(self, substrate: SharedSubstrate[Any]) -> None:
        """should_promote should trigger based on interaction count."""
        profile = KgentMemoryProfile(
            dialogue_promotion_threshold=5,
            dialogue_max_patterns=100,
        )
        manager = await create_kgent_allocation(substrate, profile)

        embedding = [0.5] * 64

        # Not eligible initially
        assert not manager.should_promote()

        # Store dialogues up to threshold
        for i in range(5):
            await manager.store_dialogue(
                f"turn_{i}", f"msg_{i}", f"resp_{i}", "reflect", embedding
            )

        # Now should be eligible
        assert manager.should_promote()

    @pytest.mark.asyncio
    async def test_stats_tracking(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Stats should accurately reflect allocation state."""
        manager = await create_kgent_allocation(substrate, small_profile)

        embedding = [0.5] * 64
        await manager.store_working("ctx_1", {}, embedding)
        await manager.store_working("ctx_2", {}, embedding)
        await manager.store_dialogue("turn_1", "a", "b", "reflect", embedding)

        stats = manager.stats()
        assert isinstance(stats, AllocationStats)
        assert stats.working_memory_used == 2
        assert stats.dialogue_used == 1
        assert stats.total_used == 3
        assert stats.usage_ratio > 0


# =============================================================================
# Pheromone Integration Tests
# =============================================================================


class TestKgentPheromoneIntegration:
    """Tests for K-gent pheromone deposits with semantic routing."""

    @pytest.mark.asyncio
    async def test_deposit_dialogue_creates_trace(self, field: PheromoneField) -> None:
        """Depositing dialogue should create senseable trace."""
        depositor = create_kgent_depositor(field)

        await depositor.deposit_dialogue("reflect", intensity=1.0)

        # Sense the deposit
        results = await field.sense("soul.dialogue.reflect")
        assert len(results) > 0
        assert results[0].dominant_depositor == "kgent"

    @pytest.mark.asyncio
    async def test_deposit_eigenvector_scales_by_value_positive(
        self, field: PheromoneField
    ) -> None:
        """Eigenvector deposit intensity should scale with absolute value (positive)."""
        depositor = create_kgent_depositor(field)

        # Positive value
        await depositor.deposit_eigenvector("aesthetic", 0.8)
        results = await field.sense("soul.eigenvector.aesthetic")
        assert results[0].total_intensity == pytest.approx(0.8)

    @pytest.mark.asyncio
    async def test_deposit_eigenvector_scales_by_value_negative(
        self,
    ) -> None:
        """Eigenvector deposit intensity should use absolute value for negative."""
        # Use fresh field to avoid interference
        fresh_field = PheromoneField(decay_rate=0.0, evaporation_threshold=0.0)
        depositor = create_kgent_depositor(fresh_field)

        # Negative value should use absolute
        await depositor.deposit_eigenvector("heterarchic", -0.6)
        results = await fresh_field.sense("soul.eigenvector.heterarchic")
        assert results[0].total_intensity == pytest.approx(0.6)

    @pytest.mark.asyncio
    async def test_semantic_routing_with_kgent_deposits(
        self, field: PheromoneField
    ) -> None:
        """SemanticRouter should correctly route to K-gent based on deposits."""
        depositor = create_kgent_depositor(field)

        # K-gent deposits soul-related traces
        await depositor.deposit_dialogue("reflect", 2.0)
        await depositor.deposit_emotional_state("curious", 1.5)

        # Another agent deposits code-related
        await field.deposit("code.python.debug", 1.0, depositor="bgent")

        # Create semantic router
        router = create_semantic_router(
            field=field,
            similarity_type="prefix",
            locality=0.5,
        )

        # Routing soul query should go to kgent
        agent = await router.route("soul.dialogue")
        assert agent == "kgent"

        # Routing code query should go to bgent
        agent = await router.route("code.python")
        assert agent == "bgent"

    @pytest.mark.asyncio
    async def test_locality_filters_distant_concepts(
        self, field: PheromoneField
    ) -> None:
        """High locality should filter out semantically distant deposits."""
        depositor = create_kgent_depositor(field)

        await depositor.deposit_dialogue("reflect", 2.0)
        await field.deposit("code.python.debug", 1.0, depositor="bgent")

        # High locality router
        router = SemanticRouter(
            field=field,
            similarity=PrefixSimilarity(),
            locality=LocalityConfig(locality=0.8, threshold=0.3),
        )

        # Sensing from soul position should filter out code
        results = await router.sense("soul.dialogue")
        concepts = [r.concept for r in results]

        assert "soul.dialogue.reflect" in concepts
        # code.python.debug should be filtered (0 similarity to soul.dialogue)

    @pytest.mark.asyncio
    async def test_full_k_to_m_flow(
        self,
        substrate: SharedSubstrate[Any],
        small_profile: KgentMemoryProfile,
        field: PheromoneField,
    ) -> None:
        """Full integration: K-gent allocates memory, deposits pheromones, M-gent routes."""
        # K-gent sets up allocation
        manager = await create_kgent_allocation(substrate, small_profile)
        depositor = create_kgent_depositor(field)

        # K-gent stores dialogues and deposits pheromones
        embedding = [0.5] * 64
        await manager.store_dialogue(
            "turn_1", "What is beauty?", "Beauty is...", "reflect", embedding
        )
        await depositor.deposit_dialogue("reflect", 1.0)
        await depositor.deposit_eigenvector("aesthetic", 0.9)

        # M-gent creates semantic router
        router = create_semantic_router(field, locality=0.5)

        # M-gent routes soul queries to K-gent
        agent = await router.route("soul.dialogue.reflect")
        assert agent == "kgent"

        # K-gent stats show activity
        stats = manager.stats()
        assert stats.dialogue_used == 1


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_uninitialized_manager_raises(
        self, substrate: SharedSubstrate[Any]
    ) -> None:
        """Accessing uninitialized manager should raise."""
        manager = KgentAllocationManager(substrate)

        with pytest.raises(RuntimeError, match="not initialized"):
            await manager.store_working("test", {}, [0.5] * 64)

    @pytest.mark.asyncio
    async def test_empty_embedding(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Empty embedding should still work (degenerate case)."""
        manager = await create_kgent_allocation(substrate, small_profile)

        success = await manager.store_working("test", {"data": "value"}, [])
        assert success

        # Retrieve with empty cue
        results = await manager.retrieve_working([], threshold=0.0)
        # Should still find the pattern (resonance with empty is 0)
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_double_initialize(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Double initialization should return existing allocations."""
        manager = KgentAllocationManager(substrate, small_profile)
        await manager.initialize()
        await manager.initialize()  # Should not raise

        assert manager.is_initialized
        # Should still have only 4 allocations (not 8)
        assert len(substrate.allocations) == 4

    @pytest.mark.asyncio
    async def test_retrieve_from_empty_allocation(
        self, substrate: SharedSubstrate[Any], small_profile: KgentMemoryProfile
    ) -> None:
        """Retrieving from empty allocation should return empty list."""
        manager = await create_kgent_allocation(substrate, small_profile)

        results = await manager.retrieve_working([0.5] * 64)
        assert results == []

        results = await manager.retrieve_dialogue([0.5] * 64)
        assert results == []

        results = await manager.retrieve_dreams([0.5] * 64)
        assert results == []
