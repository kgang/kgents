"""
Tests for self.memory.* substrate AGENTESE paths.

These tests verify the substrate integration added in Phase 5:
- self.memory.allocate - Allocate memory in shared substrate
- self.memory.compact - Compact agent's allocation
- self.memory.route - Route tasks via pheromone gradients
- self.memory.substrate_stats - Get substrate statistics
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, cast

import pytest
from protocols.agentese.contexts.self_ import (
    MemoryNode,
    SelfContextResolver,
    create_self_resolver,
)
from protocols.agentese.node import BasicRendering

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
