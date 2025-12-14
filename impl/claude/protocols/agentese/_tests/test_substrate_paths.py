"""
Tests for self.memory.* substrate AGENTESE paths.

These tests verify the substrate integration added in Phase 5:
- self.memory.allocate - Allocate memory in shared substrate
- self.memory.compact - Compact agent's allocation
- self.memory.route - Route tasks via pheromone gradients
- self.memory.substrate_stats - Get substrate statistics

Property-based tests verify invariants (Phase 6 QA):
- ∀ allocation: usage_ratio ∈ [0.0, 1.0]
- ∀ allocation: pattern_count ≤ quota.max_patterns
- ∀ compaction: patterns_after ≤ patterns_before
- ∀ compaction: resolution_after ≤ resolution_before
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from protocols.agentese.contexts.self_ import (
    MemoryNode,
    SelfContextResolver,
    create_self_resolver,
)
from protocols.agentese.node import BasicRendering

if TYPE_CHECKING:
    from agents.m.compaction import Compactor
    from agents.m.substrate import SharedSubstrate

# Note: mock_umwelt fixture returns Any for type compatibility
# Use Any type annotation for mock_umwelt parameters


# === Mock Substrate Components ===


class MockSubstrate:
    """Mock SharedSubstrate for testing."""

    def __init__(self) -> None:
        self.allocations: dict[str, "MockAllocation"] = {}
        self.dedicated_crystals: dict[str, Any] = {}

    def allocate(
        self, agent_id: str, quota: Any = None, lifecycle: Any = None
    ) -> "MockAllocation":
        """Create an allocation."""
        if agent_id in self.allocations:
            return self.allocations[agent_id]

        allocation = MockAllocation(
            agent_id=agent_id,
            namespace=agent_id,
            quota=quota,
            lifecycle=lifecycle,
        )
        self.allocations[agent_id] = allocation
        return allocation

    def stats(self) -> dict[str, Any]:
        """Get substrate statistics."""
        return {
            "allocation_count": len(self.allocations),
            "dedicated_count": len(self.dedicated_crystals),
            "total_patterns": sum(a.pattern_count for a in self.allocations.values()),
        }


class MockAllocation:
    """Mock Allocation for testing."""

    def __init__(
        self,
        agent_id: str,
        namespace: str,
        quota: Any = None,
        lifecycle: Any = None,
    ) -> None:
        self.agent_id = agent_id
        self.namespace = namespace
        self.quota = quota
        self.lifecycle = lifecycle
        self.pattern_count = 0
        self._max_patterns = quota.max_patterns if quota else 1000

    def usage_ratio(self) -> float:
        return self.pattern_count / self._max_patterns

    def is_at_soft_limit(self) -> bool:
        return self.usage_ratio() >= 0.8


class MockCompactor:
    """Mock Compactor for testing."""

    def __init__(self) -> None:
        self.compaction_count = 0
        self._events: list[MockCompactionEvent] = []

    async def compact_allocation(
        self, allocation: MockAllocation, force: bool = False
    ) -> "MockCompactionEvent | None":
        """Compact an allocation."""
        if not force and allocation.usage_ratio() < 0.8:
            return None

        event = MockCompactionEvent(
            target_id=str(allocation.agent_id),
            ratio=0.8,
            patterns_before=allocation.pattern_count,
            patterns_after=allocation.pattern_count,
            resolution_before=1.0,
            resolution_after=0.8,
            duration_ms=5.0,
            reason="test compaction",
        )
        self._events.append(event)
        self.compaction_count += 1
        return event

    def stats(self) -> dict[str, Any]:
        """Get compactor statistics."""
        return {
            "total_compactions": self.compaction_count,
            "avg_ratio": 0.8 if self._events else 0.0,
        }


class MockCompactionEvent:
    """Mock CompactionEvent for testing."""

    def __init__(
        self,
        target_id: str,
        ratio: float,
        patterns_before: int,
        patterns_after: int,
        resolution_before: float,
        resolution_after: float,
        duration_ms: float,
        reason: str,
    ) -> None:
        self.target_id = target_id
        self.ratio = ratio
        self.patterns_before = patterns_before
        self.patterns_after = patterns_after
        self.resolution_before = resolution_before
        self.resolution_after = resolution_after
        self.duration_ms = duration_ms
        self.reason = reason

    @property
    def resolution_loss(self) -> float:
        return self.resolution_before - self.resolution_after


class MockRouter:
    """Mock CategoricalRouter for testing."""

    def __init__(self) -> None:
        self.route_count = 0
        self._traces: list[Any] = []

    async def route(self, task: Any) -> "MockRoutingDecision":
        """Route a task."""
        self.route_count += 1
        return MockRoutingDecision(
            task=task,
            agent_id="best_agent",
            confidence=0.9,
            gradient_strength=0.8,
            reasoning="Following strongest gradient",
            alternatives=[("alt_agent_1", 0.5), ("alt_agent_2", 0.3)],
        )

    def stats(self) -> dict[str, Any]:
        """Get router statistics."""
        return {
            "route_count": self.route_count,
            "trace_count": len(self._traces),
        }


class MockRoutingDecision:
    """Mock RoutingDecision for testing."""

    def __init__(
        self,
        task: Any,
        agent_id: str,
        confidence: float,
        gradient_strength: float,
        reasoning: str,
        alternatives: list[tuple[str, float]],
    ) -> None:
        self.task = task
        self.agent_id = agent_id
        self.confidence = confidence
        self.gradient_strength = gradient_strength
        self.reasoning = reasoning
        self.alternatives = alternatives


# === Fixtures ===


@pytest.fixture
def mock_substrate() -> MockSubstrate:
    """Create a mock substrate."""
    return MockSubstrate()


@pytest.fixture
def mock_compactor() -> MockCompactor:
    """Create a mock compactor."""
    return MockCompactor()


@pytest.fixture
def mock_router() -> MockRouter:
    """Create a mock router."""
    return MockRouter()


@pytest.fixture
def memory_node_with_substrate(
    mock_substrate: MockSubstrate,
    mock_compactor: MockCompactor,
    mock_router: MockRouter,
) -> MemoryNode:
    """Create a MemoryNode with substrate integration."""
    return MemoryNode(
        _substrate=mock_substrate,
        _compactor=mock_compactor,
        _router=mock_router,
    )


# === Test Cases ===


class TestSubstrateAllocate:
    """Tests for self.memory.allocate."""

    async def test_allocate_without_substrate_returns_error(
        self, mock_umwelt: Any
    ) -> None:
        """Allocation requires substrate to be configured."""
        node = MemoryNode()  # No substrate
        result = await node._invoke_aspect("allocate", mock_umwelt)

        assert "error" in result
        assert "SharedSubstrate not configured" in result["error"]

    async def test_allocate_creates_allocation(
        self,
        memory_node_with_substrate: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Allocation creates an entry in the substrate."""
        result = await memory_node_with_substrate._invoke_aspect(
            "allocate",
            mock_umwelt,
            human_label="test memory",
            max_patterns=500,
            ttl_hours=12,
        )

        assert result["status"] == "allocated"
        assert result["agent_id"] == "test_agent"
        assert result["max_patterns"] == 500
        assert result["human_label"] == "test memory"
        assert result["ttl_hours"] == 12

    async def test_allocate_stores_allocation(
        self,
        memory_node_with_substrate: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Allocation is stored on the node for future use."""
        await memory_node_with_substrate._invoke_aspect("allocate", mock_umwelt)

        assert memory_node_with_substrate._allocation is not None
        assert memory_node_with_substrate._allocation.agent_id == "test_agent"


class TestSubstrateCompact:
    """Tests for self.memory.compact."""

    async def test_compact_without_allocation_returns_error(
        self, mock_umwelt: Any, mock_compactor: MockCompactor
    ) -> None:
        """Compaction requires an existing allocation."""
        node = MemoryNode(_compactor=mock_compactor)  # No allocation
        result = await node._invoke_aspect("compact", mock_umwelt)

        assert "error" in result
        assert "No allocation exists" in result["error"]

    async def test_compact_without_compactor_returns_error(
        self, mock_umwelt: Any
    ) -> None:
        """Compaction requires compactor to be configured."""
        node = MemoryNode()
        node._allocation = MockAllocation("test", "test")  # Has allocation
        result = await node._invoke_aspect("compact", mock_umwelt)

        assert "error" in result
        assert "Compactor not configured" in result["error"]

    async def test_compact_below_threshold_returns_not_needed(
        self,
        memory_node_with_substrate: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Compaction below threshold returns not_needed."""
        # First allocate
        await memory_node_with_substrate._invoke_aspect("allocate", mock_umwelt)

        # Compact without force (allocation is empty, below threshold)
        result = await memory_node_with_substrate._invoke_aspect(
            "compact", mock_umwelt, force=False
        )

        assert result["status"] == "not_needed"
        assert "usage_ratio" in result

    async def test_compact_force_executes_compaction(
        self,
        memory_node_with_substrate: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Force compaction executes even below threshold."""
        # First allocate
        await memory_node_with_substrate._invoke_aspect("allocate", mock_umwelt)

        # Force compact
        result = await memory_node_with_substrate._invoke_aspect(
            "compact", mock_umwelt, force=True
        )

        assert result["status"] == "compacted"
        assert result["ratio"] == 0.8
        assert "resolution_loss" in result


class TestSubstrateRoute:
    """Tests for self.memory.route."""

    async def test_route_without_router_returns_error(self, mock_umwelt: Any) -> None:
        """Routing requires router to be configured."""
        node = MemoryNode()  # No router
        result = await node._invoke_aspect("route", mock_umwelt, concept="python")

        assert "error" in result
        assert "CategoricalRouter not configured" in result["error"]

    async def test_route_requires_concept(
        self, memory_node_with_substrate: MemoryNode, mock_umwelt: Any
    ) -> None:
        """Routing requires a concept."""
        result = await memory_node_with_substrate._invoke_aspect("route", mock_umwelt)

        assert "error" in result
        assert "concept required" in result["error"]

    async def test_route_returns_decision(
        self, memory_node_with_substrate: MemoryNode, mock_umwelt: Any
    ) -> None:
        """Routing returns a decision with agent and alternatives."""
        result = await memory_node_with_substrate._invoke_aspect(
            "route",
            mock_umwelt,
            concept="python_debugging",
            content="Fix type error",
            priority=0.8,
        )

        assert result["status"] == "routed"
        assert result["agent_id"] == "best_agent"
        assert result["confidence"] == 0.9
        assert result["gradient_strength"] == 0.8
        assert len(result["alternatives"]) == 2


class TestSubstrateStats:
    """Tests for self.memory.substrate_stats."""

    async def test_stats_without_substrate_returns_error(
        self, mock_umwelt: Any
    ) -> None:
        """Stats requires substrate to be configured."""
        node = MemoryNode()  # No substrate
        result = await node._invoke_aspect("substrate_stats", mock_umwelt)

        assert "error" in result
        assert "SharedSubstrate not configured" in result["error"]

    async def test_stats_returns_substrate_metrics(
        self, memory_node_with_substrate: MemoryNode, mock_umwelt: Any
    ) -> None:
        """Stats returns substrate metrics."""
        result = await memory_node_with_substrate._invoke_aspect(
            "substrate_stats", mock_umwelt
        )

        assert "allocation_count" in result
        assert "dedicated_count" in result
        assert "total_patterns" in result

    async def test_stats_includes_allocation_info(
        self, memory_node_with_substrate: MemoryNode, mock_umwelt: Any
    ) -> None:
        """Stats includes current allocation info when present."""
        # First allocate
        await memory_node_with_substrate._invoke_aspect("allocate", mock_umwelt)

        result = await memory_node_with_substrate._invoke_aspect(
            "substrate_stats", mock_umwelt
        )

        assert "current_allocation" in result
        assert result["current_allocation"]["agent_id"] == "test_agent"

    async def test_stats_includes_compactor_and_router_stats(
        self, memory_node_with_substrate: MemoryNode, mock_umwelt: Any
    ) -> None:
        """Stats includes compactor and router stats when configured."""
        result = await memory_node_with_substrate._invoke_aspect(
            "substrate_stats", mock_umwelt
        )

        assert "compactor" in result
        assert "router" in result
        assert result["compactor"]["total_compactions"] == 0
        assert result["router"]["route_count"] == 0


class TestSelfContextResolverSubstrate:
    """Tests for SelfContextResolver substrate integration."""

    def test_create_self_resolver_with_substrate(
        self,
        mock_substrate: MockSubstrate,
        mock_compactor: MockCompactor,
        mock_router: MockRouter,
    ) -> None:
        """create_self_resolver accepts substrate parameters."""
        resolver = create_self_resolver(
            substrate=mock_substrate,
            compactor=mock_compactor,
            router=mock_router,
        )

        assert resolver._substrate is mock_substrate
        assert resolver._compactor is mock_compactor
        assert resolver._router is mock_router

    def test_resolver_passes_substrate_to_memory_node(
        self,
        mock_substrate: MockSubstrate,
        mock_compactor: MockCompactor,
        mock_router: MockRouter,
    ) -> None:
        """SelfContextResolver passes substrate to MemoryNode."""
        resolver = create_self_resolver(
            substrate=mock_substrate,
            compactor=mock_compactor,
            router=mock_router,
        )

        base_node = resolver.resolve("memory", [])
        # Cast to MemoryNode to access substrate integration attributes
        memory_node = cast(MemoryNode, base_node)

        assert memory_node._substrate is mock_substrate
        assert memory_node._compactor is mock_compactor
        assert memory_node._router is mock_router

    async def test_full_substrate_workflow(
        self,
        mock_substrate: MockSubstrate,
        mock_compactor: MockCompactor,
        mock_router: MockRouter,
        mock_umwelt: Any,
    ) -> None:
        """Test complete workflow: allocate → route → compact → stats."""
        resolver = create_self_resolver(
            substrate=mock_substrate,
            compactor=mock_compactor,
            router=mock_router,
        )

        memory_node = resolver.resolve("memory", [])

        # Step 1: Allocate
        alloc_result = await memory_node._invoke_aspect(
            "allocate", mock_umwelt, human_label="workflow test"
        )
        assert alloc_result["status"] == "allocated"

        # Step 2: Route a task
        route_result = await memory_node._invoke_aspect(
            "route", mock_umwelt, concept="test_concept"
        )
        assert route_result["status"] == "routed"

        # Step 3: Compact (forced)
        compact_result = await memory_node._invoke_aspect(
            "compact", mock_umwelt, force=True
        )
        assert compact_result["status"] == "compacted"

        # Step 4: Get stats
        stats_result = await memory_node._invoke_aspect("substrate_stats", mock_umwelt)
        assert stats_result["allocation_count"] == 1
        assert stats_result["compactor"]["total_compactions"] == 1
        assert stats_result["router"]["route_count"] == 1


# === Integration Tests with Real Components ===


class TestRealSubstrateIntegration:
    """
    Tests using real SharedSubstrate, Compactor instances (not mocks).

    These tests verify the wiring works end-to-end with actual implementations.
    """

    @pytest.fixture
    def real_substrate(self) -> "SharedSubstrate[Any]":
        """Create a real SharedSubstrate instance."""
        from agents.m.substrate import SharedSubstrate

        return SharedSubstrate()

    @pytest.fixture
    def real_compactor(self) -> "Compactor[Any]":
        """Create a real Compactor instance."""
        from agents.m.compaction import Compactor

        return Compactor()

    @pytest.fixture
    def real_memory_node(
        self,
        real_substrate: "SharedSubstrate[Any]",
        real_compactor: "Compactor[Any]",
    ) -> MemoryNode:
        """Create a MemoryNode with real substrate integration."""
        return MemoryNode(
            _substrate=real_substrate,
            _compactor=real_compactor,
        )

    async def test_real_allocate_creates_allocation(
        self,
        real_memory_node: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Real allocation creates an entry in the real substrate."""
        result = await real_memory_node._invoke_aspect(
            "allocate",
            mock_umwelt,
            human_label="real test memory",
            max_patterns=500,
            ttl_hours=12,
        )

        assert result["status"] == "allocated"
        assert result["agent_id"] == "test_agent"
        assert result["max_patterns"] == 500
        assert result["namespace"] == "test_agent"

        # Verify allocation is stored
        assert real_memory_node._allocation is not None

    async def test_real_substrate_stats_returns_metrics(
        self,
        real_memory_node: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Real substrate stats returns actual substrate metrics."""
        # First allocate
        await real_memory_node._invoke_aspect(
            "allocate", mock_umwelt, human_label="stats test"
        )

        result = await real_memory_node._invoke_aspect("substrate_stats", mock_umwelt)

        assert result["allocation_count"] == 1
        assert result["dedicated_count"] == 0
        assert "current_allocation" in result
        assert result["current_allocation"]["agent_id"] == "test_agent"
        assert result["current_allocation"]["usage_ratio"] == 0.0

    async def test_real_compact_below_threshold_not_needed(
        self,
        real_memory_node: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Real compaction below threshold returns not_needed."""
        # First allocate
        await real_memory_node._invoke_aspect(
            "allocate", mock_umwelt, human_label="compact test"
        )

        # Compact without force (allocation is empty, below threshold)
        result = await real_memory_node._invoke_aspect(
            "compact", mock_umwelt, force=False
        )

        assert result["status"] == "not_needed"
        assert result["usage_ratio"] == 0.0

    async def test_real_compact_force_executes(
        self,
        real_memory_node: MemoryNode,
        mock_umwelt: Any,
    ) -> None:
        """Real force compaction executes even below threshold."""
        # First allocate
        await real_memory_node._invoke_aspect(
            "allocate", mock_umwelt, human_label="force compact test"
        )

        # Force compact
        result = await real_memory_node._invoke_aspect(
            "compact", mock_umwelt, force=True
        )

        assert result["status"] == "compacted"
        assert "ratio" in result
        assert "duration_ms" in result

    async def test_real_full_workflow(
        self,
        real_substrate: "SharedSubstrate[Any]",
        real_compactor: "Compactor[Any]",
        mock_umwelt: Any,
    ) -> None:
        """
        Full integration test: allocate → store → compact → stats.

        This tests the complete substrate workflow with real components.
        """
        # Create resolver with real components
        resolver = create_self_resolver(
            substrate=real_substrate,
            compactor=real_compactor,
        )

        memory_node = resolver.resolve("memory", [])

        # Step 1: Allocate
        alloc_result = await memory_node._invoke_aspect(
            "allocate", mock_umwelt, human_label="full workflow test"
        )
        assert alloc_result["status"] == "allocated"

        # Step 2: Verify stats
        stats_result = await memory_node._invoke_aspect("substrate_stats", mock_umwelt)
        assert stats_result["allocation_count"] == 1

        # Step 3: Compact (forced since allocation is empty)
        compact_result = await memory_node._invoke_aspect(
            "compact", mock_umwelt, force=True
        )
        assert compact_result["status"] == "compacted"

        # Step 4: Verify compaction recorded
        stats_after = await memory_node._invoke_aspect("substrate_stats", mock_umwelt)
        assert stats_after["compactor"]["total_compactions"] == 1


class TestCreateContextResolversSubstrate:
    """Test create_context_resolvers passes substrate to self resolver."""

    def test_substrate_passed_to_self_resolver(
        self, mock_substrate: MockSubstrate
    ) -> None:
        """create_context_resolvers passes substrate to self resolver."""
        from protocols.agentese.contexts import create_context_resolvers

        resolvers = create_context_resolvers(substrate=mock_substrate)

        self_resolver = resolvers["self"]
        assert self_resolver._substrate is mock_substrate

    def test_compactor_passed_to_self_resolver(
        self, mock_compactor: MockCompactor
    ) -> None:
        """create_context_resolvers passes compactor to self resolver."""
        from protocols.agentese.contexts import create_context_resolvers

        resolvers = create_context_resolvers(compactor=mock_compactor)

        self_resolver = resolvers["self"]
        assert self_resolver._compactor is mock_compactor

    def test_router_passed_to_self_resolver(self, mock_router: MockRouter) -> None:
        """create_context_resolvers passes router to self resolver."""
        from protocols.agentese.contexts import create_context_resolvers

        resolvers = create_context_resolvers(router=mock_router)

        self_resolver = resolvers["self"]
        assert self_resolver._router is mock_router

    def test_all_substrate_components_passed(
        self,
        mock_substrate: MockSubstrate,
        mock_compactor: MockCompactor,
        mock_router: MockRouter,
    ) -> None:
        """create_context_resolvers passes all substrate components."""
        from protocols.agentese.contexts import create_context_resolvers

        resolvers = create_context_resolvers(
            substrate=mock_substrate,
            compactor=mock_compactor,
            router=mock_router,
        )

        self_resolver = resolvers["self"]
        memory_node = self_resolver.resolve("memory", [])

        assert memory_node._substrate is mock_substrate
        assert memory_node._compactor is mock_compactor
        assert memory_node._router is mock_router


# === Property-Based Tests (Hypothesis) ===


class TestAllocationInvariants:
    """
    Property-based tests for allocation lifecycle invariants.

    These tests verify mathematical properties that must hold
    for all valid inputs, using Hypothesis for fuzzing.
    """

    @given(
        pattern_count=st.integers(min_value=0, max_value=5000),
        max_patterns=st.integers(min_value=1, max_value=5000),
    )
    @settings(max_examples=100)
    def test_usage_ratio_bounded_when_enforced(
        self, pattern_count: int, max_patterns: int
    ) -> None:
        """
        usage_ratio in [0.0, 1.0] when pattern_count clamped to max_patterns.

        Note: The usage_ratio() method just divides pattern_count by max_patterns.
        The store() method enforces the constraint that pattern_count <= max_patterns.
        """
        from agents.m.substrate import (
            AgentId,
            Allocation,
            LifecyclePolicy,
            MemoryQuota,
        )

        # Only test valid states (enforced by store())
        clamped_pattern_count = min(pattern_count, max_patterns)

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=max_patterns),
            lifecycle=LifecyclePolicy(human_label="property test"),
        )
        allocation.pattern_count = clamped_pattern_count

        ratio = allocation.usage_ratio()

        assert 0.0 <= ratio <= 1.0, f"usage_ratio={ratio} out of bounds"

    @given(
        max_patterns=st.integers(min_value=1, max_value=1000),
        store_attempts=st.integers(min_value=0, max_value=2000),
    )
    @settings(max_examples=50)
    @pytest.mark.asyncio
    async def test_pattern_count_respects_quota(
        self, max_patterns: int, store_attempts: int
    ) -> None:
        """
        pattern_count <= quota.max_patterns.

        The store() method must reject stores when at quota.
        """
        from agents.m.substrate import (
            AgentId,
            Allocation,
            LifecyclePolicy,
            MemoryQuota,
        )

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=max_patterns),
            lifecycle=LifecyclePolicy(human_label="property test"),
        )

        # Attempt to store more than quota
        for i in range(store_attempts):
            await allocation.store(f"concept_{i}", f"content_{i}", [0.1] * 10)

        assert allocation.pattern_count <= max_patterns, (
            f"pattern_count={allocation.pattern_count} "
            f"exceeds max_patterns={max_patterns}"
        )

    @given(
        soft_limit_ratio=st.floats(min_value=0.01, max_value=0.99),
        max_patterns=st.integers(min_value=10, max_value=1000),
    )
    @settings(max_examples=50)
    def test_soft_limit_less_than_max(
        self, soft_limit_ratio: float, max_patterns: int
    ) -> None:
        """Soft limit should always be less than max."""
        from agents.m.substrate import MemoryQuota

        quota = MemoryQuota(
            max_patterns=max_patterns, soft_limit_ratio=soft_limit_ratio
        )

        assert quota.soft_limit_patterns() < quota.max_patterns


class TestCompactionInvariants:
    """
    Property-based tests for compaction invariants.

    These verify the holographic property: all patterns preserved,
    only resolution is reduced.
    """

    @given(ratio=st.floats(min_value=0.1, max_value=1.0))
    @settings(max_examples=50)
    def test_compression_preserves_patterns(self, ratio: float) -> None:
        """
        patterns_after == patterns_before (holographic).

        Compaction should never lose patterns, only reduce resolution.
        """
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=32)

        # Add some patterns
        for i in range(10):
            crystal.store(f"concept_{i}", f"content_{i}", [float(i) / 10] * 32)

        patterns_before = len(crystal.concepts)

        compressed = crystal.compress(ratio)

        patterns_after = len(compressed.concepts)

        assert patterns_after == patterns_before, (
            f"Patterns lost: before={patterns_before}, after={patterns_after}"
        )

    @given(ratio=st.floats(min_value=0.1, max_value=0.99))
    @settings(max_examples=50)
    def test_compression_reduces_resolution(self, ratio: float) -> None:
        """
        resolution_after <= resolution_before.

        Compression ratio < 1.0 should reduce resolution.
        """
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=32)

        # Add patterns with resolution
        for i in range(5):
            crystal.store(f"concept_{i}", f"content_{i}", [float(i) / 10] * 32)

        resolution_before = crystal.stats().get("avg_resolution", 1.0)

        compressed = crystal.compress(ratio)

        resolution_after = compressed.stats().get("avg_resolution", 1.0)

        # Resolution should decrease (or stay same if already at minimum)
        assert resolution_after <= resolution_before + 0.001, (  # small epsilon
            f"Resolution increased: before={resolution_before}, after={resolution_after}"
        )


class TestPressureThresholds:
    """
    Tests for compaction pressure threshold behavior.

    Verifies correct triggering at different pressure levels:
    - Below 0.8: not_needed
    - 0.8-0.95: normal_ratio (0.8)
    - Above 0.95: aggressive_ratio (0.5)
    - Rate limiting: max 4 compactions per hour
    """

    @given(pressure=st.floats(min_value=0.0, max_value=0.79))
    @settings(max_examples=50)
    def test_below_threshold_not_needed(self, pressure: float) -> None:
        """Below 80% pressure: no compaction needed."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(
            pressure_threshold=0.8,
            critical_threshold=0.95,
        )

        should, ratio, reason = policy.should_compact(
            current_pressure=pressure,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is False
        assert "Pressure OK" in reason

    @given(pressure=st.floats(min_value=0.80, max_value=0.94))
    @settings(max_examples=50)
    def test_normal_threshold_uses_normal_ratio(self, pressure: float) -> None:
        """80-95% pressure: use normal_ratio (0.8)."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(
            pressure_threshold=0.8,
            critical_threshold=0.95,
            normal_ratio=0.8,
        )

        should, ratio, reason = policy.should_compact(
            current_pressure=pressure,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is True
        assert ratio == 0.8
        assert "High pressure" in reason

    @given(pressure=st.floats(min_value=0.95, max_value=1.0))
    @settings(max_examples=50)
    def test_critical_threshold_uses_aggressive_ratio(self, pressure: float) -> None:
        """Above 95% pressure: use aggressive_ratio (0.5)."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(
            pressure_threshold=0.8,
            critical_threshold=0.95,
            aggressive_ratio=0.5,
        )

        should, ratio, reason = policy.should_compact(
            current_pressure=pressure,
            last_compaction=None,
            compactions_last_hour=0,
        )

        assert should is True
        assert ratio == 0.5
        assert "Critical" in reason

    @given(compactions=st.integers(min_value=4, max_value=100))
    @settings(max_examples=50)
    def test_rate_limiting_enforced(self, compactions: int) -> None:
        """Max 4 compactions per hour enforced."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(max_compactions_per_hour=4)

        should, ratio, reason = policy.should_compact(
            current_pressure=0.9,  # Would normally trigger
            last_compaction=None,
            compactions_last_hour=compactions,
        )

        assert should is False
        assert "Rate limit" in reason

    def test_rate_limit_allows_below_max(self) -> None:
        """Rate limiting allows compaction when below max."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(max_compactions_per_hour=4)

        should, ratio, reason = policy.should_compact(
            current_pressure=0.9,
            last_compaction=None,
            compactions_last_hour=3,  # Below max
        )

        assert should is True

    def test_critical_overrides_interval(self) -> None:
        """Critical pressure overrides minimum interval."""
        from agents.m.compaction import CompactionPolicy

        policy = CompactionPolicy(
            min_interval=timedelta(minutes=30),
            critical_threshold=0.95,
        )

        # Compacted 5 minutes ago (below min_interval)
        should, ratio, reason = policy.should_compact(
            current_pressure=0.98,  # Critical
            last_compaction=datetime.now() - timedelta(minutes=5),
            compactions_last_hour=0,
        )

        assert should is True
        assert "Critical pressure override" in reason


class TestEdgeCases:
    """
    Edge case tests drawn from entropy budget exploration.

    These test boundary conditions and graceful degradation.
    """

    def test_zero_patterns_usage_ratio(self) -> None:
        """Zero patterns should have 0.0 usage_ratio."""
        from agents.m.substrate import (
            AgentId,
            Allocation,
            LifecyclePolicy,
            MemoryQuota,
        )

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=1000),
            lifecycle=LifecyclePolicy(human_label="edge case test"),
        )
        allocation.pattern_count = 0

        assert allocation.usage_ratio() == 0.0

    def test_max_patterns_usage_ratio(self) -> None:
        """Max patterns should have 1.0 usage_ratio."""
        from agents.m.substrate import (
            AgentId,
            Allocation,
            LifecyclePolicy,
            MemoryQuota,
        )

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=100),
            lifecycle=LifecyclePolicy(human_label="edge case test"),
        )
        allocation.pattern_count = 100

        assert allocation.usage_ratio() == 1.0

    def test_empty_crystal_compression(self) -> None:
        """Empty crystal compression should be safe."""
        from agents.m.crystal import MemoryCrystal

        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=32)

        compressed = crystal.compress(0.5)

        assert len(compressed.concepts) == 0

    @pytest.mark.asyncio
    async def test_allocation_at_exactly_soft_limit(self) -> None:
        """Allocation at exactly soft limit should report is_at_soft_limit True."""
        from agents.m.substrate import (
            AgentId,
            Allocation,
            LifecyclePolicy,
            MemoryQuota,
        )

        allocation: Allocation[str] = Allocation(
            agent_id=AgentId("test"),
            namespace="test",
            quota=MemoryQuota(max_patterns=100, soft_limit_ratio=0.8),
            lifecycle=LifecyclePolicy(human_label="edge case test"),
        )

        # Store exactly to soft limit
        for i in range(80):
            await allocation.store(f"concept_{i}", f"content_{i}", [0.1] * 10)

        assert allocation.pattern_count == 80
        assert allocation.is_at_soft_limit() is True
