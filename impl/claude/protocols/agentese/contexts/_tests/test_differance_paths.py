"""
Tests for Différance Engine AGENTESE paths.

Phase 4 Exit Criteria: CLI `kg time.trace.why <id>` works

Tests verify:
1. time.differance.* paths (heritage, ghosts, at, why, replay)
2. time.branch.* paths (create, explore, compare)
3. self.differance.* paths (why, navigate, concretize, abstract)
4. Integration with TraceMonoid and DifferanceStore
5. CLI output format for 'why' command

See: spec/protocols/differance.md
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, cast

import pytest

# === Test Fixtures ===


class MockDNA:
    """Mock DNA for testing."""

    def __init__(self, name: str = "test", archetype: str = "default") -> None:
        self.name = name
        self.archetype = archetype
        self.capabilities: tuple[str, ...] = ()


class MockUmwelt:
    """Mock Umwelt for testing."""

    def __init__(self, archetype: str = "default", name: str = "test") -> None:
        self.dna = MockDNA(name=name, archetype=archetype)
        self.gravity: tuple[Any, ...] = ()
        self.context: dict[str, Any] = {}


@pytest.fixture
def observer() -> Any:
    """Default observer."""
    return MockUmwelt()


@pytest.fixture
def trace_monoid() -> Any:
    """Create a TraceMonoid with test data."""
    from agents.differance import Alternative, TraceMonoid, WiringTrace

    trace1 = WiringTrace(
        trace_id="trace_001",
        timestamp=datetime.now(timezone.utc),
        operation="seq",
        inputs=("Brain", "Gardener"),
        output="BrainGardener",
        context="Compose brain and gardener",
        alternatives=(
            Alternative(
                operation="par",
                inputs=("Brain", "Gardener"),
                reason_rejected="Order matters for memory cultivation",
                could_revisit=True,
            ),
        ),
        positions_before={"Brain": frozenset(["ready"]), "Gardener": frozenset(["ready"])},
        positions_after={"BrainGardener": frozenset(["composed"])},
        parent_trace_id=None,
    )

    trace2 = WiringTrace(
        trace_id="trace_002",
        timestamp=datetime.now(timezone.utc),
        operation="branch",
        inputs=("BrainGardener",),
        output="BrainGardenerSpecialized",
        context="Specialize for memory task",
        alternatives=(
            Alternative(
                operation="identity",
                inputs=("BrainGardener",),
                reason_rejected="Needed specialization",
                could_revisit=False,
            ),
        ),
        positions_before={"BrainGardener": frozenset(["composed"])},
        positions_after={"BrainGardenerSpecialized": frozenset(["specialized"])},
        parent_trace_id="trace_001",
    )

    return TraceMonoid(traces=(trace1, trace2))


@pytest.fixture
def differance_node(trace_monoid: Any) -> Any:
    """Create a DifferanceTraceNode with test data."""
    from protocols.agentese.contexts.time_differance import DifferanceTraceNode

    node = DifferanceTraceNode()
    node.set_monoid(trace_monoid)
    return node


@pytest.fixture
def branch_node() -> Any:
    """Create a BranchNode for testing."""
    from protocols.agentese.contexts.time_differance import BranchNode

    return BranchNode()


@pytest.fixture
def self_differance_node(differance_node: Any) -> Any:
    """Create a SelfDifferanceNode with integration."""
    from protocols.agentese.contexts.self_differance import SelfDifferanceNode

    node = SelfDifferanceNode()
    node.set_time_differance_node(differance_node)
    return node


# === DifferanceTraceNode Tests ===


class TestDifferanceTraceAffordances:
    """Tests for differance trace affordances."""

    def test_affordances_include_required_aspects(self, differance_node: Any) -> None:
        """Required aspects are in affordances."""
        affordances = differance_node._get_affordances_for_archetype("default")

        assert "manifest" in affordances
        assert "heritage" in affordances
        assert "ghosts" in affordances
        assert "at" in affordances
        assert "why" in affordances
        assert "replay" in affordances


class TestDifferanceManifest:
    """Tests for time.differance.manifest."""

    @pytest.mark.asyncio
    async def test_manifest_shows_trace_count(self, differance_node: Any, observer: Any) -> None:
        """Manifest shows trace count."""
        rendering = await differance_node.manifest(observer)

        assert rendering.metadata["trace_count"] == 2
        assert rendering.metadata["monoid_available"] is True


class TestDifferanceHeritage:
    """Tests for time.differance.heritage."""

    @pytest.mark.asyncio
    async def test_heritage_requires_output_id(self, differance_node: Any, observer: Any) -> None:
        """Heritage requires output_id."""
        result = await differance_node._invoke_aspect("heritage", observer)

        assert "error" in result
        assert "output_id" in result["error"]

    @pytest.mark.asyncio
    async def test_heritage_builds_dag(self, differance_node: Any, observer: Any) -> None:
        """Heritage builds DAG for valid output."""
        result = await differance_node._invoke_aspect("heritage", observer, output_id="trace_002")

        assert "error" not in result
        assert result["output_id"] == "trace_002"
        assert result["root_id"] == "trace_001"
        assert len(result["chosen_path"]) == 2
        assert result["node_count"] >= 2  # Chosen nodes + ghosts

    @pytest.mark.asyncio
    async def test_heritage_includes_ghost_paths(self, differance_node: Any, observer: Any) -> None:
        """Heritage includes ghost paths."""
        result = await differance_node._invoke_aspect("heritage", observer, output_id="trace_002")

        assert "ghost_paths" in result
        # Should have ghost paths from alternatives
        assert len(result["ghost_paths"]) > 0


class TestDifferanceGhosts:
    """Tests for time.differance.ghosts."""

    @pytest.mark.asyncio
    async def test_ghosts_returns_all_ghosts(self, differance_node: Any, observer: Any) -> None:
        """Ghosts returns all ghost alternatives."""
        result = await differance_node._invoke_aspect("ghosts", observer)

        assert "error" not in result
        assert "ghosts" in result
        assert result["count"] > 0

    @pytest.mark.asyncio
    async def test_ghosts_explorable_only_filter(self, differance_node: Any, observer: Any) -> None:
        """Ghosts respects explorable_only filter."""
        result = await differance_node._invoke_aspect("ghosts", observer, explorable_only=True)

        # All returned ghosts should be explorable
        for ghost in result["ghosts"]:
            assert ghost["could_revisit"] is True


class TestDifferanceAt:
    """Tests for time.differance.at."""

    @pytest.mark.asyncio
    async def test_at_requires_trace_id(self, differance_node: Any, observer: Any) -> None:
        """At requires trace_id."""
        result = await differance_node._invoke_aspect("at", observer)

        assert "error" in result
        assert "trace_id" in result["error"]

    @pytest.mark.asyncio
    async def test_at_returns_trace_details(self, differance_node: Any, observer: Any) -> None:
        """At returns full trace details."""
        result = await differance_node._invoke_aspect("at", observer, trace_id="trace_001")

        assert "error" not in result
        assert result["trace_id"] == "trace_001"
        assert result["operation"] == "seq"
        assert "Brain" in result["inputs"]
        assert "Gardener" in result["inputs"]
        assert len(result["alternatives"]) == 1


class TestDifferanceWhy:
    """Tests for time.differance.why (THE KEY PATH)."""

    @pytest.mark.asyncio
    async def test_why_requires_output_id(self, differance_node: Any, observer: Any) -> None:
        """Why requires output_id."""
        result = await differance_node._invoke_aspect("why", observer)

        assert "error" in result
        assert "output_id" in result["error"]

    @pytest.mark.asyncio
    async def test_why_returns_summary(self, differance_node: Any, observer: Any) -> None:
        """Why returns summary by default."""
        result = await differance_node._invoke_aspect("why", observer, output_id="trace_002")

        assert "error" not in result
        assert result["output_id"] == "trace_002"
        assert result["decisions_made"] == 2
        assert result["alternatives_considered"] > 0
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_why_cli_format(self, differance_node: Any, observer: Any) -> None:
        """Why returns CLI format when requested."""
        result = await differance_node._invoke_aspect(
            "why", observer, output_id="trace_002", format="cli"
        )

        assert "error" not in result
        assert "cli_output" in result
        # CLI output should have visual markers
        cli = result["cli_output"]
        assert "▶" in cli or "│" in cli or "├" in cli

    @pytest.mark.asyncio
    async def test_why_full_format(self, differance_node: Any, observer: Any) -> None:
        """Why returns full format when requested."""
        result = await differance_node._invoke_aspect(
            "why", observer, output_id="trace_002", format="full"
        )

        assert "error" not in result
        assert "chosen_path" in result
        assert len(result["chosen_path"]) == 2
        # Each step should have ghosts
        for step in result["chosen_path"]:
            assert "ghosts" in step


class TestDifferanceReplay:
    """Tests for time.differance.replay."""

    @pytest.mark.asyncio
    async def test_replay_requires_from_id(self, differance_node: Any, observer: Any) -> None:
        """Replay requires from_id."""
        result = await differance_node._invoke_aspect("replay", observer)

        assert "error" in result
        assert "from_id" in result["error"]

    @pytest.mark.asyncio
    async def test_replay_returns_steps(self, differance_node: Any, observer: Any) -> None:
        """Replay returns step sequence."""
        # Query from the leaf trace to get full chain
        result = await differance_node._invoke_aspect("replay", observer, from_id="trace_002")

        assert "error" not in result
        # Causal chain from trace_002 goes back to trace_001
        assert result["step_count"] == 2
        assert len(result["steps"]) == 2


class TestDifferanceRecent:
    """Tests for time.differance.recent (RecentTracesPanel endpoint)."""

    @pytest.fixture
    def buffer_with_traces(self) -> Any:
        """Create isolated buffer with test traces."""
        from agents.differance import Alternative, WiringTrace
        from agents.differance.integration import (
            create_isolated_buffer,
            reset_isolated_buffer,
        )

        buffer = create_isolated_buffer()

        # Add traces with different jewel contexts
        trace1 = WiringTrace(
            trace_id="recent_001",
            timestamp=datetime.now(timezone.utc),
            operation="capture",
            inputs=("test content",),
            output="crystal_001",
            context="[brain] Captured memory",
            alternatives=(),
            positions_before={},
            positions_after={},
            parent_trace_id=None,
        )

        trace2 = WiringTrace(
            trace_id="recent_002",
            timestamp=datetime.now(timezone.utc),
            operation="record_gesture",
            inputs=("prune", "old_item"),
            output="gesture_002",
            context="[gardener] Pruning garden",
            alternatives=(Alternative("water", ("old_item",), "Could water instead", True),),
            positions_before={},
            positions_after={},
            parent_trace_id=None,
        )

        trace3 = WiringTrace(
            trace_id="recent_003",
            timestamp=datetime.now(timezone.utc),
            operation="forge_intent",
            inputs=("build widget",),
            output="intent_003",
            context="[forge] Forging new intent",
            alternatives=(),
            positions_before={},
            positions_after={},
            parent_trace_id=None,
        )

        buffer.extend([trace1, trace2, trace3])

        yield buffer

        # Cleanup
        reset_isolated_buffer()

    @pytest.fixture
    def recent_node(self) -> Any:
        """Create a DifferanceTraceNode for recent tests."""
        from protocols.agentese.contexts.time_differance import DifferanceTraceNode

        return DifferanceTraceNode()

    @pytest.mark.asyncio
    async def test_recent_returns_traces_from_buffer(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent returns traces from buffer."""
        result = await recent_node._invoke_aspect("recent", observer)

        assert "error" not in result
        assert "traces" in result
        assert len(result["traces"]) == 3
        assert result["total"] == 3
        assert result["source"] == "buffer"  # Changed from buffer_size to source

    @pytest.mark.asyncio
    async def test_recent_respects_limit(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent respects limit parameter."""
        result = await recent_node._invoke_aspect("recent", observer, limit=2)

        assert len(result["traces"]) == 2
        assert result["total"] == 3  # Total is still 3

    @pytest.mark.asyncio
    async def test_recent_returns_most_recent_first(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent returns most recent traces first (reversed order)."""
        result = await recent_node._invoke_aspect("recent", observer)

        # Most recent (trace3) should be first
        assert result["traces"][0]["id"] == "recent_003"
        assert result["traces"][2]["id"] == "recent_001"

    @pytest.mark.asyncio
    async def test_recent_extracts_jewel_from_context(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent extracts jewel name from [jewel] context prefix."""
        result = await recent_node._invoke_aspect("recent", observer)

        jewels = {t["jewel"] for t in result["traces"]}
        assert "brain" in jewels
        assert "gardener" in jewels
        assert "forge" in jewels

    @pytest.mark.asyncio
    async def test_recent_filters_by_jewel(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent filters by jewel_filter parameter."""
        result = await recent_node._invoke_aspect("recent", observer, jewel_filter="gardener")

        assert len(result["traces"]) == 1
        assert result["traces"][0]["jewel"] == "gardener"
        assert result["traces"][0]["operation"] == "record_gesture"

    @pytest.mark.asyncio
    async def test_recent_includes_ghost_count(
        self, recent_node: Any, observer: Any, buffer_with_traces: Any
    ) -> None:
        """Recent includes ghost count from alternatives."""
        result = await recent_node._invoke_aspect("recent", observer)

        # Find the gardener trace which has 1 alternative
        gardener_trace = next(t for t in result["traces"] if t["jewel"] == "gardener")
        assert gardener_trace["ghost_count"] == 1

        # Find the brain trace which has 0 alternatives
        brain_trace = next(t for t in result["traces"] if t["jewel"] == "brain")
        assert brain_trace["ghost_count"] == 0

    @pytest.mark.asyncio
    async def test_recent_empty_buffer(self, recent_node: Any, observer: Any) -> None:
        """Recent returns empty list when buffer is empty."""
        from agents.differance.integration import (
            create_isolated_buffer,
            reset_isolated_buffer,
        )

        # Create empty isolated buffer
        create_isolated_buffer()

        try:
            result = await recent_node._invoke_aspect("recent", observer)

            assert result["traces"] == []
            assert result["total"] == 0
            assert result["source"] == "buffer"  # Changed from buffer_size
        finally:
            reset_isolated_buffer()

    def test_recent_in_affordances(self, recent_node: Any) -> None:
        """Recent is included in affordances."""
        affordances = recent_node._get_affordances_for_archetype("default")
        assert "recent" in affordances


# === BranchNode Tests ===


class TestBranchAffordances:
    """Tests for branch affordances."""

    def test_affordances_include_required_aspects(self, branch_node: Any) -> None:
        """Required aspects are in affordances."""
        affordances = branch_node._get_affordances_for_archetype("default")

        assert "manifest" in affordances
        assert "create" in affordances
        assert "explore" in affordances
        assert "compare" in affordances


class TestBranchCreate:
    """Tests for time.branch.create."""

    @pytest.mark.asyncio
    async def test_create_requires_from_trace_id(self, branch_node: Any, observer: Any) -> None:
        """Create requires from_trace_id."""
        result = await branch_node._invoke_aspect("create", observer)

        assert "error" in result
        assert "from_trace_id" in result["error"]

    @pytest.mark.asyncio
    async def test_create_returns_branch_id(self, branch_node: Any, observer: Any) -> None:
        """Create returns branch ID."""
        result = await branch_node._invoke_aspect(
            "create",
            observer,
            from_trace_id="trace_001",
            name="test_branch",
            hypothesis="Testing alternative path",
        )

        assert "error" not in result
        assert "branch_id" in result
        assert result["name"] == "test_branch"
        assert result["status"] == "created"


class TestBranchExplore:
    """Tests for time.branch.explore."""

    @pytest.mark.asyncio
    async def test_explore_requires_ghost_id(self, branch_node: Any, observer: Any) -> None:
        """Explore requires ghost_id."""
        result = await branch_node._invoke_aspect("explore", observer)

        assert "error" in result
        assert "ghost_id" in result["error"]

    @pytest.mark.asyncio
    async def test_explore_returns_deferred_status(self, branch_node: Any, observer: Any) -> None:
        """Explore returns deferred status (not yet implemented)."""
        result = await branch_node._invoke_aspect("explore", observer, ghost_id="trace_001_ghost_0")

        assert result["status"] == "deferred"


class TestBranchCompare:
    """Tests for time.branch.compare."""

    @pytest.mark.asyncio
    async def test_compare_requires_both_branches(self, branch_node: Any, observer: Any) -> None:
        """Compare requires both a and b."""
        result = await branch_node._invoke_aspect("compare", observer, a="branch_0")

        assert "error" in result
        assert "'a'" in result["error"] or "'b'" in result["error"]


# === SelfDifferanceNode Tests ===


class TestSelfDifferanceAffordances:
    """Tests for self differance affordances."""

    def test_affordances_include_required_aspects(self, self_differance_node: Any) -> None:
        """Required aspects are in affordances."""
        affordances = self_differance_node._get_affordances_for_archetype("default")

        assert "manifest" in affordances
        assert "why" in affordances
        assert "navigate" in affordances
        assert "concretize" in affordances
        assert "abstract" in affordances


class TestSelfDifferanceWhy:
    """Tests for self.differance.why (delegates to time.differance)."""

    @pytest.mark.asyncio
    async def test_why_delegates_to_time_differance(
        self, self_differance_node: Any, observer: Any
    ) -> None:
        """Why delegates to time.differance.why."""
        result = await self_differance_node._invoke_aspect("why", observer, output_id="trace_002")

        assert "error" not in result
        assert result["context"] == "self"
        assert "interpretation" in result
        # Should have the data from time.differance.why
        assert result["decisions_made"] == 2


class TestSelfDifferanceNavigate:
    """Tests for self.differance.navigate."""

    @pytest.mark.asyncio
    async def test_navigate_without_target_shows_usage(
        self, self_differance_node: Any, observer: Any
    ) -> None:
        """Navigate without target shows usage."""
        result = await self_differance_node._invoke_aspect("navigate", observer)

        assert "usage" in result
        assert "available_directions" in result

    @pytest.mark.asyncio
    async def test_navigate_to_spec(self, self_differance_node: Any, observer: Any) -> None:
        """Navigate to spec path."""
        result = await self_differance_node._invoke_aspect(
            "navigate", observer, target="spec/agents/brain.md"
        )

        assert result["type"] == "spec"
        assert "related_impls" in result

    @pytest.mark.asyncio
    async def test_navigate_to_impl(self, self_differance_node: Any, observer: Any) -> None:
        """Navigate to impl path."""
        result = await self_differance_node._invoke_aspect(
            "navigate", observer, target="impl/claude/agents/brain/"
        )

        assert result["type"] == "impl"
        assert "related_specs" in result


class TestSelfDifferanceConcretize:
    """Tests for self.differance.concretize."""

    @pytest.mark.asyncio
    async def test_concretize_requires_spec_path(
        self, self_differance_node: Any, observer: Any
    ) -> None:
        """Concretize requires spec_path."""
        result = await self_differance_node._invoke_aspect("concretize", observer)

        assert "error" in result
        assert "spec_path" in result["error"]

    @pytest.mark.asyncio
    async def test_concretize_returns_planned_status(
        self, self_differance_node: Any, observer: Any
    ) -> None:
        """Concretize returns planned status."""
        result = await self_differance_node._invoke_aspect(
            "concretize", observer, spec_path="spec/agents/brain.md"
        )

        assert result["status"] == "planned"


class TestSelfDifferanceAbstract:
    """Tests for self.differance.abstract."""

    @pytest.mark.asyncio
    async def test_abstract_requires_impl_path(
        self, self_differance_node: Any, observer: Any
    ) -> None:
        """Abstract requires impl_path."""
        result = await self_differance_node._invoke_aspect("abstract", observer)

        assert "error" in result
        assert "impl_path" in result["error"]


# === Integration Tests ===


class TestTimeContextResolverIntegration:
    """Integration tests with TimeContextResolver."""

    def test_resolver_returns_differance_node(self) -> None:
        """TimeContextResolver returns DifferanceTraceNode for differance."""
        from protocols.agentese.contexts.time import TimeContextResolver
        from protocols.agentese.contexts.time_differance import DifferanceTraceNode

        resolver = TimeContextResolver()
        resolver.__post_init__()

        node = resolver.resolve("differance", [])

        assert isinstance(node, DifferanceTraceNode)

    def test_resolver_returns_branch_node(self) -> None:
        """TimeContextResolver returns BranchNode for branch."""
        from protocols.agentese.contexts.time import TimeContextResolver
        from protocols.agentese.contexts.time_differance import BranchNode

        resolver = TimeContextResolver()
        resolver.__post_init__()

        node = resolver.resolve("branch", [])

        assert isinstance(node, BranchNode)


class TestNodeRegistration:
    """Tests for @node registration."""

    def test_differance_node_registered(self) -> None:
        """DifferanceTraceNode is registered with @node."""
        from protocols.agentese.contexts.time_differance import DifferanceTraceNode
        from protocols.agentese.registry import get_node_metadata, is_node

        assert is_node(DifferanceTraceNode)
        meta = get_node_metadata(DifferanceTraceNode)
        assert meta is not None
        assert meta.path == "time.differance"

    def test_branch_node_registered(self) -> None:
        """BranchNode is registered with @node."""
        from protocols.agentese.contexts.time_differance import BranchNode
        from protocols.agentese.registry import get_node_metadata, is_node

        assert is_node(BranchNode)
        meta = get_node_metadata(BranchNode)
        assert meta is not None
        assert meta.path == "time.branch"

    def test_self_differance_node_registered(self) -> None:
        """SelfDifferanceNode is registered with @node."""
        from protocols.agentese.contexts.self_differance import SelfDifferanceNode
        from protocols.agentese.registry import get_node_metadata, is_node

        assert is_node(SelfDifferanceNode)
        meta = get_node_metadata(SelfDifferanceNode)
        assert meta is not None
        assert meta.path == "self.differance"
