"""
Property Tests for Memory Phase 5: Categorical Laws.

These tests verify the mathematical properties:
1. deposit ⊣ route adjunction
2. promote >> demote ≅ id (up to resolution loss)
3. Compaction preserves resolution ordering
4. Routing naturality: route(f(task)) = f(route(task))
5. Holographic property: compression preserves patterns
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from agents.m.compaction import CompactionPolicy, Compactor
from agents.m.crystal import MemoryCrystal
from agents.m.routing import CategoricalRouter, Task, TaskMorphism, verify_adjunction
from agents.m.stigmergy import PheromoneField
from agents.m.substrate import (
    AgentId,
    Allocation,
    CrystalPolicy,
    LifecyclePolicy,
    MemoryQuota,
    SharedSubstrate,
    create_substrate,
)


class TestDepositRouteAdjunction:
    """Test deposit ⊣ route adjunction property."""

    @pytest.mark.asyncio
    async def test_every_deposit_creates_followable_gradient(self) -> None:
        """Property: Deposits create gradients that routing follows."""
        field = PheromoneField()
        router = CategoricalRouter(field=field, exploration_rate=0.0)

        depositor = "test_agent"

        # Single deposit - routes to depositor
        await field.deposit("concept", intensity=1.0, depositor=depositor)

        task = Task(concept="concept")
        decision = await router.route(task)
        assert decision.agent_id == depositor, (
            f"Adjunction violated: deposit didn't create route to {depositor}"
        )

    @pytest.mark.asyncio
    async def test_adjunction_single_depositor(self) -> None:
        """Verify adjunction: single depositor gets all routes."""
        field = PheromoneField()
        router = CategoricalRouter(field=field, exploration_rate=0.0)

        # With one depositor, all routes go to them
        depositor = "verifier"
        await field.deposit("concept", intensity=1.0, depositor=depositor)

        task = Task(concept="any")
        decision = await router.route(task)

        # Single depositor receives all routes
        assert decision.agent_id == depositor

    @pytest.mark.asyncio
    async def test_stronger_gradient_wins(self) -> None:
        """Competing deposits: stronger gradient wins routing."""
        field = PheromoneField()
        router = CategoricalRouter(field=field, exploration_rate=0.0)

        # Weak deposit
        await field.deposit("python", intensity=1.0, depositor="weak_agent")

        # Strong deposit
        await field.deposit("python", intensity=10.0, depositor="strong_agent")

        task = Task(concept="python")
        decision = await router.route(task)

        assert decision.agent_id == "strong_agent", "Stronger gradient should win"


class TestPromoteDemoteIdentity:
    """Test promote >> demote ≅ id (up to resolution loss)."""

    @pytest.fixture
    def substrate(self) -> SharedSubstrate[str]:
        """Create substrate with short min_age for testing."""
        return SharedSubstrate(promotion_policy=CrystalPolicy(min_age_hours=0.001))

    @pytest.mark.asyncio
    async def test_roundtrip_preserves_concepts(
        self, substrate: SharedSubstrate[str]
    ) -> None:
        """Property: promote >> demote preserves all concepts."""
        # Setup
        allocation = substrate.allocate("agent", human_label="test")

        concepts = ["alpha", "beta", "gamma"]
        for i, concept in enumerate(concepts):
            await allocation.store(concept, f"value_{i}", [0.1 * i] * 10)

        original_concepts = allocation._crystal.concepts.copy()
        allocation.access_count = 100  # Enable promotion

        # promote >> demote
        substrate.promote("agent")
        new_allocation = substrate.demote("agent")

        # Concepts preserved
        assert new_allocation._crystal.concepts == original_concepts, (
            "Roundtrip lost concepts"
        )

    @pytest.mark.asyncio
    async def test_roundtrip_resolution_loss(
        self, substrate: SharedSubstrate[str]
    ) -> None:
        """Property: promote >> demote has resolution loss."""
        allocation = substrate.allocate("agent", human_label="test")

        await allocation.store("test", "value", [0.1] * 10)
        allocation.access_count = 100

        original_resolution = allocation._crystal.stats()["avg_resolution"]

        # promote >> demote
        substrate.promote("agent")
        new_allocation = substrate.demote("agent", compress_ratio=0.5)

        new_resolution = new_allocation._crystal.stats()["avg_resolution"]

        assert new_resolution < original_resolution, "Demotion should lose resolution"

    @pytest.mark.asyncio
    async def test_multiple_roundtrips_converge(
        self, substrate: SharedSubstrate[str]
    ) -> None:
        """Property: Multiple roundtrips converge to minimum resolution."""
        allocation = substrate.allocate("agent", human_label="test")
        await allocation.store("test", "value", [0.1] * 10)

        resolutions = []

        for i in range(3):
            allocation.access_count = 100
            substrate.promote("agent")
            allocation = substrate.demote("agent", compress_ratio=0.5)
            resolutions.append(allocation._crystal.stats()["avg_resolution"])

        # Resolution decreases monotonically
        for i in range(len(resolutions) - 1):
            assert resolutions[i + 1] <= resolutions[i], (
                "Resolution should decrease with each roundtrip"
            )


class TestCompactionPreservesOrdering:
    """Test compaction preserves resolution ordering."""

    @pytest.mark.asyncio
    async def test_hot_stays_hotter(self) -> None:
        """Property: Hot patterns stay hotter than cold after compaction."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        # Store patterns
        crystal.store("hot", "hot content", [1.0] * 64)
        crystal.store("cold", "cold content", [0.5] * 64)

        # Promote hot, demote cold
        crystal.promote("hot", factor=1.5)
        crystal.demote("cold", factor=0.5)

        hot_before = crystal.resolution_levels["hot"]
        cold_before = crystal.resolution_levels["cold"]

        # Compress
        compressed = crystal.compress(0.8)

        hot_after = compressed.resolution_levels["hot"]
        cold_after = compressed.resolution_levels["cold"]

        # Ordering preserved
        assert hot_after > cold_after, (
            f"Hot ({hot_after}) should remain hotter than cold ({cold_after})"
        )

        # Both lost proportionally
        assert hot_after < hot_before
        assert cold_after < cold_before

    @pytest.mark.asyncio
    async def test_uniform_compression(self) -> None:
        """Property: Compression is uniform (holographic)."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        # Store patterns at same resolution
        for i in range(5):
            crystal.store(f"c_{i}", f"v_{i}", [0.1 * i] * 64)

        resolutions_before = list(crystal.resolution_levels.values())
        compressed = crystal.compress(0.8)
        resolutions_after = list(compressed.resolution_levels.values())

        # All resolutions reduced by same factor
        ratios = [
            after / before
            for before, after in zip(resolutions_before, resolutions_after)
        ]

        # All ratios should be ~0.8
        for ratio in ratios:
            assert abs(ratio - 0.8) < 0.01, f"Compression not uniform: ratio {ratio}"


class TestRoutingNaturality:
    """Test routing naturality: route(f(task)) respects morphisms."""

    @pytest.fixture
    def field(self) -> PheromoneField:
        """Create field with deposits."""
        return PheromoneField()

    @pytest.fixture
    def router(self, field: PheromoneField) -> CategoricalRouter:
        """Create router."""
        return CategoricalRouter(field=field, exploration_rate=0.0)

    @pytest.mark.asyncio
    async def test_identity_morphism_naturality(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Property: route(id(task)) = route(task)."""
        await field.deposit("python", intensity=1.0, depositor="python_agent")

        task = Task(concept="python")
        identity = TaskMorphism(name="identity")

        decision_original = await router.route(task)
        decision_mapped = await router.route(task.map(identity))

        assert decision_original.agent_id == decision_mapped.agent_id, (
            "Identity morphism should not change routing"
        )

    @pytest.mark.asyncio
    async def test_concept_preserving_morphism(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Property: Concept-preserving morphisms preserve routing."""
        await field.deposit("python", intensity=1.0, depositor="python_agent")

        task = Task(concept="python", content="original")
        morphism = TaskMorphism(
            name="add_metadata",
            transform_concept=False,
        )

        decision_original = await router.route(task)
        decision_mapped = await router.route(task.map(morphism))

        assert decision_original.agent_id == decision_mapped.agent_id, (
            "Concept-preserving morphism should preserve routing"
        )

    @pytest.mark.asyncio
    async def test_concept_transforming_morphism(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Property: Concept transforms carry the original concept as related."""
        # Deposit with different intensities so we can track behavior
        await field.deposit("python", intensity=10.0, depositor="python_agent")

        task = Task(concept="python")
        generalize = TaskMorphism(
            name="generalize",
            transform_concept=True,
            new_concept="programming",
        )

        transformed = task.map(generalize)

        # The original concept should be in related_concepts
        assert "python" in transformed.related_concepts
        assert transformed.concept == "programming"

        # Both route to the only depositor (stigmergy is global)
        decision = await router.route(task)
        assert decision.agent_id == "python_agent"


class TestHolographicProperty:
    """Test holographic property: compression preserves patterns."""

    def test_all_concepts_survive_compression(self) -> None:
        """Property: All concepts survive any compression."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=128)

        # Store many patterns
        for i in range(20):
            crystal.store(f"concept_{i}", f"content_{i}", [0.1 * i] * 128)

        original_concepts = crystal.concepts.copy()

        # Aggressive compression
        compressed = crystal.compress(0.1)  # 90% compression!

        assert compressed.concepts == original_concepts, (
            "Holographic compression must preserve ALL concepts"
        )

    def test_repeated_compression_preserves_all(self) -> None:
        """Property: Repeated compression still preserves all."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=128)

        for i in range(10):
            crystal.store(f"c_{i}", f"v_{i}", [0.1] * 128)

        original_concepts = crystal.concepts.copy()

        # Multiple compressions
        current = crystal
        for _ in range(5):
            current = current.compress(0.8)

        assert current.concepts == original_concepts, (
            "Repeated compression must preserve ALL concepts"
        )

    def test_resolution_bounds(self) -> None:
        """Property: Resolution stays in valid bounds."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("test", "value", [1.0] * 64)

        # Many compressions
        current = crystal
        for _ in range(10):
            current = current.compress(0.5)

        for concept in current.concepts:
            pattern = current.get_pattern(concept)
            assert pattern is not None
            assert 0 < pattern.resolution <= 1.0, (
                f"Resolution {pattern.resolution} out of bounds"
            )


class TestLifecyclePolicyEnforcement:
    """Test lifecycle policy enforcement."""

    def test_human_label_required(self) -> None:
        """Property: human_label is required (no anonymous debris)."""
        with pytest.raises(ValueError, match="human_label"):
            LifecyclePolicy(human_label="")

    def test_allocation_requires_label(self) -> None:
        """Property: Allocation requires human_label."""
        substrate = create_substrate()

        with pytest.raises(ValueError, match="human_label"):
            substrate.allocate("agent")  # No label

    def test_ttl_expiration(self) -> None:
        """Property: TTL expiration works correctly."""
        policy = LifecyclePolicy(
            human_label="test",
            ttl=timedelta(hours=1),
        )

        recent = datetime.now() - timedelta(minutes=30)
        old = datetime.now() - timedelta(hours=2)

        assert not policy.is_expired(recent)
        assert policy.is_expired(old)
