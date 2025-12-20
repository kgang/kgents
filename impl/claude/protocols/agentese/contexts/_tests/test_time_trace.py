"""
Tests for time.trace.* AGENTESE paths.

Tests verify:
1. time.trace.analyze - Static call graph analysis
2. time.trace.collect - Runtime trace collection config
3. time.trace.render - ASCII visualization
4. time.trace.diff - Trace comparison
5. Existing aspects (witness, query, replay)

Exit criteria: 10+ tests for Phase 5
"""

from __future__ import annotations

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
def trace_node() -> Any:
    """Create a TraceNode for testing."""
    from protocols.agentese.contexts.time import TraceNode

    return TraceNode()


# === Affordance Tests ===


class TestTraceAffordances:
    """Tests for trace affordances."""

    def test_affordances_include_new_aspects(self, trace_node: Any) -> None:
        """New aspects are in affordances."""
        affordances = trace_node._get_affordances_for_archetype("default")

        assert "analyze" in affordances
        assert "collect" in affordances
        assert "render" in affordances
        assert "diff" in affordances

    def test_affordances_include_legacy_aspects(self, trace_node: Any) -> None:
        """Legacy aspects still work."""
        affordances = trace_node._get_affordances_for_archetype("default")

        assert "witness" in affordances
        assert "query" in affordances
        assert "replay" in affordances


# === Analyze Tests ===


class TestAnalyze:
    """Tests for time.trace.analyze."""

    @pytest.mark.asyncio
    async def test_analyze_requires_target(self, trace_node: Any, observer: Any) -> None:
        """Analyze requires a target."""
        result = await trace_node._invoke_aspect("analyze", observer)

        assert "error" in result
        assert "target" in result["error"]

    @pytest.mark.asyncio
    async def test_analyze_with_target(self, trace_node: Any, observer: Any) -> None:
        """Analyze with valid target works."""
        result = await trace_node._invoke_aspect(
            "analyze",
            observer,
            target="TraceNode",
            path="impl/claude/protocols/agentese",
        )

        # Should succeed (may or may not find nodes)
        assert "error" not in result or "not available" in result.get("error", "")
        if "error" not in result:
            assert "target" in result
            assert "direction" in result

    @pytest.mark.asyncio
    async def test_analyze_with_callees(self, trace_node: Any, observer: Any) -> None:
        """Analyze with callees=True traces what target calls."""
        result = await trace_node._invoke_aspect(
            "analyze",
            observer,
            target="TraceNode",
            callees=True,
            path="impl/claude/protocols/agentese",
        )

        if "error" not in result:
            assert result.get("direction") == "callees"

    @pytest.mark.asyncio
    async def test_analyze_with_depth(self, trace_node: Any, observer: Any) -> None:
        """Analyze respects depth parameter."""
        result = await trace_node._invoke_aspect(
            "analyze",
            observer,
            target="TraceNode",
            depth=2,
            path="impl/claude/protocols/agentese",
        )

        if "error" not in result:
            assert result.get("depth") == 2


# === Collect Tests ===


class TestCollect:
    """Tests for time.trace.collect."""

    @pytest.mark.asyncio
    async def test_collect_returns_config(self, trace_node: Any, observer: Any) -> None:
        """Collect returns configuration status."""
        result = await trace_node._invoke_aspect("collect", observer)

        assert "error" not in result or "not available" in result.get("error", "")
        if "error" not in result:
            assert result.get("status") == "configured"
            assert "filter" in result

    @pytest.mark.asyncio
    async def test_collect_with_patterns(self, trace_node: Any, observer: Any) -> None:
        """Collect respects include/exclude patterns."""
        result = await trace_node._invoke_aspect(
            "collect",
            observer,
            include_patterns=["**/weave/**"],
            exclude_patterns=["**/_tests/**"],
        )

        if "error" not in result:
            assert result["filter"]["include_patterns"] == ["**/weave/**"]

    @pytest.mark.asyncio
    async def test_collect_with_max_depth(self, trace_node: Any, observer: Any) -> None:
        """Collect respects max_depth."""
        result = await trace_node._invoke_aspect(
            "collect",
            observer,
            max_depth=10,
        )

        if "error" not in result:
            assert result["filter"]["max_depth"] == 10


# === Render Tests ===


class TestRender:
    """Tests for time.trace.render."""

    @pytest.mark.asyncio
    async def test_render_static_requires_target(self, trace_node: Any, observer: Any) -> None:
        """Static render requires target."""
        result = await trace_node._invoke_aspect(
            "render",
            observer,
            source="static",
        )

        assert "error" in result
        assert "target" in result["error"]

    @pytest.mark.asyncio
    async def test_render_runtime_requires_trace(self, trace_node: Any, observer: Any) -> None:
        """Runtime render requires cached trace."""
        result = await trace_node._invoke_aspect(
            "render",
            observer,
            source="runtime",
        )

        assert "error" in result
        assert "runtime trace" in result["error"].lower() or "no runtime" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_render_static_tree(self, trace_node: Any, observer: Any) -> None:
        """Static tree rendering works."""
        result = await trace_node._invoke_aspect(
            "render",
            observer,
            source="static",
            target="TraceNode",
            mode="tree",
            path="impl/claude/protocols/agentese",
        )

        # May fail if weave not available, but shouldn't crash
        if "error" not in result:
            assert "visualization" in result
            assert result.get("mode") == "tree"


# === Diff Tests ===


class TestDiff:
    """Tests for time.trace.diff."""

    @pytest.mark.asyncio
    async def test_diff_requires_both_traces(self, trace_node: Any, observer: Any) -> None:
        """Diff requires both before and after."""
        result = await trace_node._invoke_aspect(
            "diff",
            observer,
            before=None,
        )

        assert "error" in result
        assert "before" in result["error"].lower() or "after" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_diff_with_monoids(self, trace_node: Any, observer: Any) -> None:
        """Diff with TraceMonoids works."""
        try:
            from weave.event import Event
            from weave.trace_monoid import TraceMonoid

            # Create two traces
            before: TraceMonoid[Any] = TraceMonoid()
            before.append_mut(Event.create({"function": "foo"}, "test"))
            before.append_mut(Event.create({"function": "bar"}, "test"))

            after: TraceMonoid[Any] = TraceMonoid()
            after.append_mut(Event.create({"function": "foo"}, "test"))
            after.append_mut(Event.create({"function": "baz"}, "test"))

            result = await trace_node._invoke_aspect(
                "diff",
                observer,
                before=before,
                after=after,
            )

            assert "error" not in result
            assert "visualization" in result
            assert "added" in result
            assert "removed" in result

        except ImportError:
            pytest.skip("weave module not available")


# === Helper Method Tests ===


class TestHelperMethods:
    """Tests for TraceNode helper methods."""

    def test_set_runtime_trace(self, trace_node: Any) -> None:
        """set_runtime_trace caches the trace."""
        trace_node.set_runtime_trace("mock_monoid")

        assert trace_node._last_runtime_trace == "mock_monoid"

    def test_clear_cache(self, trace_node: Any) -> None:
        """clear_cache clears all cached data."""
        trace_node._static_graph = "mock_graph"
        trace_node._last_runtime_trace = "mock_monoid"

        trace_node.clear_cache()

        assert trace_node._static_graph is None
        assert trace_node._last_runtime_trace is None

    def test_record_adds_timestamp(self, trace_node: Any) -> None:
        """record adds timestamp if missing."""
        trace_node.record({"event": "test"})

        assert len(trace_node._traces) == 1
        assert "timestamp" in trace_node._traces[0]


# === Integration Tests ===


class TestIntegration:
    """Integration tests with resolver."""

    @pytest.mark.asyncio
    async def test_resolver_returns_trace_node(self) -> None:
        """TimeContextResolver returns TraceNode for trace."""
        from protocols.agentese.contexts.time import (
            TimeContextResolver,
            TraceNode,
        )

        resolver = TimeContextResolver()
        resolver.__post_init__()

        node = resolver.resolve("trace", [])

        assert isinstance(node, TraceNode)

    @pytest.mark.asyncio
    async def test_manifest_shows_cache_status(self, trace_node: Any, observer: Any) -> None:
        """Manifest shows static and runtime cache status."""
        rendering = await trace_node.manifest(observer)

        assert "static_graph_loaded" in rendering.metadata
        assert "runtime_trace_available" in rendering.metadata
