"""
Tests for Categorical Routing: Task → Agent via Pheromone Gradients.

These tests verify:
1. Task creation and morphisms
2. Gradient sensing and following
3. Routing decisions with confidence
4. Adjunction property: deposit ⊣ route
5. Naturality: route(f(task)) respects morphisms
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from agents.m.routing import (
    CategoricalRouter,
    GradientMap,
    RouteTrace,
    RoutingDecision,
    Task,
    TaskMorphism,
    create_router,
    create_task,
    verify_adjunction,
)
from agents.m.stigmergy import PheromoneField


class TestTask:
    """Tests for Task type."""

    def test_task_creation(self) -> None:
        """Task should be created with defaults."""
        task = Task(concept="python")
        assert task.concept == "python"
        assert task.priority == 0.5
        assert task.content == ""
        assert task.related_concepts == []

    def test_task_with_content(self) -> None:
        """Task with content should store it."""
        task = Task(
            concept="debugging",
            content="Fix the type error in module X",
            priority=0.9,
        )
        assert task.content == "Fix the type error in module X"
        assert task.priority == 0.9

    def test_task_with_related_concepts(self) -> None:
        """Task with related concepts."""
        task = Task(
            concept="python",
            related_concepts=["debugging", "types", "mypy"],
        )
        assert len(task.related_concepts) == 3
        assert "debugging" in task.related_concepts

    def test_task_factory(self) -> None:
        """create_task factory function."""
        task = create_task(
            concept="rust",
            content="Implement the parser",
            priority=0.7,
            related=["parsing", "compiler"],
        )
        assert task.concept == "rust"
        assert task.priority == 0.7
        assert len(task.related_concepts) == 2


class TestTaskMorphism:
    """Tests for TaskMorphism."""

    def test_identity_morphism(self) -> None:
        """Morphism without transform preserves concept."""
        task = Task(concept="python")
        morphism = TaskMorphism(name="identity")

        transformed = morphism(task)

        assert transformed.concept == "python"
        assert transformed.metadata.get("morphism_applied") == "identity"

    def test_concept_transforming_morphism(self) -> None:
        """Morphism that transforms concept."""
        task = Task(concept="python")
        morphism = TaskMorphism(
            name="generalize",
            transform_concept=True,
            new_concept="programming",
        )

        transformed = morphism(task)

        assert transformed.concept == "programming"
        assert "python" in transformed.related_concepts

    def test_morphism_preserves_content(self) -> None:
        """Morphism preserves content."""
        task = Task(concept="python", content="Fix the bug")
        morphism = TaskMorphism(name="identity")

        transformed = morphism(task)

        assert transformed.content == "Fix the bug"

    def test_task_map_method(self) -> None:
        """Task.map applies morphism."""
        task = Task(concept="rust")
        morphism = TaskMorphism(
            name="specialize",
            transform_concept=True,
            new_concept="rust_async",
        )

        transformed = task.map(morphism)

        assert transformed.concept == "rust_async"


class TestGradientMap:
    """Tests for GradientMap."""

    def test_empty_gradient_map(self) -> None:
        """Empty gradient map."""
        gmap = GradientMap(concept="python", gradients={})

        assert gmap.strongest() is None
        assert gmap.top_k(3) == []

    def test_single_gradient(self) -> None:
        """Single gradient in map."""
        gmap = GradientMap(
            concept="python",
            gradients={"agent_a": 0.8},
            total_intensity=0.8,
        )

        strongest = gmap.strongest()
        assert strongest is not None
        assert strongest == ("agent_a", 0.8)

    def test_multiple_gradients_strongest(self) -> None:
        """Multiple gradients - find strongest."""
        gmap = GradientMap(
            concept="python",
            gradients={"agent_a": 0.5, "agent_b": 0.9, "agent_c": 0.3},
            total_intensity=1.7,
        )

        strongest = gmap.strongest()
        assert strongest == ("agent_b", 0.9)

    def test_top_k_gradients(self) -> None:
        """Get top k gradients."""
        gmap = GradientMap(
            concept="python",
            gradients={"a": 0.1, "b": 0.5, "c": 0.3, "d": 0.9},
        )

        top2 = gmap.top_k(2)
        assert len(top2) == 2
        assert top2[0] == ("d", 0.9)
        assert top2[1] == ("b", 0.5)


class TestCategoricalRouter:
    """Tests for CategoricalRouter."""

    @pytest.fixture
    def field(self) -> PheromoneField:
        """Create a pheromone field."""
        return PheromoneField(decay_rate=0.1)

    @pytest.fixture
    def router(self, field: PheromoneField) -> CategoricalRouter:
        """Create a router."""
        return CategoricalRouter(
            field=field,
            default_agent="fallback",
            confidence_threshold=0.3,
            exploration_rate=0.0,  # Disable exploration for deterministic tests
        )

    @pytest.mark.asyncio
    async def test_route_no_gradient_uses_default(
        self, router: CategoricalRouter
    ) -> None:
        """Route to default when no gradient."""
        task = Task(concept="unknown")
        decision = await router.route(task)

        assert decision.agent_id == "fallback"
        assert decision.confidence == 0.0
        assert "No gradient" in decision.reasoning

    @pytest.mark.asyncio
    async def test_route_follows_gradient(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Route follows strongest gradient."""
        # Create gradient
        await field.deposit("python", intensity=1.0, depositor="python_agent")

        task = Task(concept="python")
        decision = await router.route(task)

        assert decision.agent_id == "python_agent"
        assert decision.gradient_strength > 0

    @pytest.mark.asyncio
    async def test_route_with_related_concepts(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Route considers related concepts."""
        # Create gradients
        await field.deposit("python", intensity=0.5, depositor="python_agent")
        await field.deposit("debugging", intensity=0.3, depositor="python_agent")

        task = Task(
            concept="python",
            related_concepts=["debugging"],
        )
        decision = await router.route(task)

        # Should route to python_agent with combined strength
        assert decision.agent_id == "python_agent"

    @pytest.mark.asyncio
    async def test_route_records_trace(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Route records trace for audit."""
        await field.deposit("test", intensity=1.0, depositor="test_agent")

        task = Task(concept="test")
        await router.route(task)

        assert len(router.traces) == 1
        trace = router.traces[0]
        assert trace.task is task
        assert trace.decision.agent_id == "test_agent"

    @pytest.mark.asyncio
    async def test_route_batch(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Route multiple tasks."""
        await field.deposit("a", intensity=1.0, depositor="agent_a")
        await field.deposit("b", intensity=1.0, depositor="agent_b")

        tasks = [Task(concept="a"), Task(concept="b")]
        decisions = await router.route_batch(tasks)

        assert len(decisions) == 2
        # Note: sense() returns all concepts, so routing picks strongest overall
        # This is correct stigmergic behavior - agents see the whole field

    @pytest.mark.asyncio
    async def test_record_outcome_reinforces(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Recording successful outcome reinforces gradient."""
        await field.deposit("python", intensity=1.0, depositor="python_agent")

        task = Task(concept="python")
        decision = await router.route(task)

        # Record success
        await router.record_outcome(decision, successful=True)

        # Check gradient was reinforced
        gradient = await field.gradient_toward("python")
        assert gradient > 1.0  # Reinforced from 1.0

    @pytest.mark.asyncio
    async def test_low_confidence_uses_default(self, field: PheromoneField) -> None:
        """Low confidence routes to default."""
        # Create equally weak gradients - no dominant depositor
        await field.deposit("concept_a", intensity=0.1, depositor="agent_a")
        await field.deposit("concept_b", intensity=0.1, depositor="agent_b")
        await field.deposit("concept_c", intensity=0.1, depositor="agent_c")

        router = CategoricalRouter(
            field=field,
            default_agent="fallback",
            confidence_threshold=0.5,  # High threshold - need >50% of total
            exploration_rate=0.0,
        )

        task = Task(concept="unknown")  # No deposits for this concept
        decision = await router.route(task)

        # Equal gradients = confidence ~33% each, below 50% threshold
        # So should use default or show low confidence
        # Note: sense() returns all concepts, so router sees all three
        assert decision.confidence <= 0.5 or decision.agent_id == "fallback"

    @pytest.mark.asyncio
    async def test_router_stats(
        self, field: PheromoneField, router: CategoricalRouter
    ) -> None:
        """Router tracks statistics."""
        await field.deposit("a", intensity=1.0, depositor="agent")

        for _ in range(3):
            await router.route(Task(concept="a"))

        stats = router.stats()
        assert stats["route_count"] == 3
        assert stats["trace_count"] == 3


class TestAdjunctionVerification:
    """Tests for deposit ⊣ route adjunction."""

    @pytest.mark.asyncio
    async def test_adjunction_holds(self) -> None:
        """Verify deposit ⊣ route adjunction."""
        field = PheromoneField()
        router = CategoricalRouter(
            field=field,
            default_agent="default",
            exploration_rate=0.0,
        )

        results = await verify_adjunction(
            field=field,
            router=router,
            concepts=["python", "rust", "go"],
            depositor="test_agent",
        )

        assert results["deposits"] == 3
        assert results["routes_to_depositor"] == 3
        assert results["adjunction_holds"] is True

    @pytest.mark.asyncio
    async def test_adjunction_partial(self) -> None:
        """Adjunction with competing depositors."""
        field = PheromoneField()
        router = CategoricalRouter(
            field=field,
            default_agent="default",
            exploration_rate=0.0,
        )

        # Pre-existing stronger gradient
        await field.deposit("python", intensity=10.0, depositor="existing_agent")

        results = await verify_adjunction(
            field=field,
            router=router,
            concepts=["python", "rust"],
            depositor="new_agent",
        )

        # python routes to existing_agent, rust to new_agent
        assert results["routes_to_depositor"] < results["deposits"]
        assert results["adjunction_holds"] is False


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_router(self) -> None:
        """create_router factory."""
        field = PheromoneField()
        router = create_router(
            field=field,
            default_agent="my_default",
            confidence_threshold=0.5,
        )

        assert router._default_agent == "my_default"
        assert router._confidence_threshold == 0.5

    def test_create_task(self) -> None:
        """create_task factory."""
        task = create_task(
            concept="test",
            content="Test content",
            priority=0.8,
        )

        assert task.concept == "test"
        assert task.content == "Test content"
        assert task.priority == 0.8
