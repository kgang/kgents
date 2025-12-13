"""
Tests for TraceRenderer - ASCII visualization for traces.

Tests verify:
- Call graph rendering in tree and force layouts
- Timeline rendering with concurrent event display
- Flame graph rendering with depth visualization
- Diff rendering between traces
- Ghost node styling
- Configuration options
- Edge cases (empty graphs, single nodes, cycles)
"""

from __future__ import annotations

import pytest

from ..dependency import DependencyGraph
from ..event import Event
from ..trace_monoid import TraceMonoid
from ..trace_renderer import (
    CHARS,
    RenderConfig,
    TraceRenderer,
    render_diff,
    render_graph,
    render_trace,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def simple_graph() -> DependencyGraph:
    """Create a simple call graph: A -> B -> C."""
    graph = DependencyGraph()
    graph.add_node("A")
    graph.add_node("B", depends_on={"A"})
    graph.add_node("C", depends_on={"B"})
    return graph


@pytest.fixture
def branching_graph() -> DependencyGraph:
    """Create a branching graph: A -> (B, C) -> D."""
    graph = DependencyGraph()
    graph.add_node("A")
    graph.add_node("B", depends_on={"A"})
    graph.add_node("C", depends_on={"A"})
    graph.add_node("D", depends_on={"B", "C"})
    return graph


@pytest.fixture
def diamond_graph() -> DependencyGraph:
    """Create a diamond graph: A -> (B, C) -> D, plus E standalone."""
    graph = DependencyGraph()
    graph.add_node("A")
    graph.add_node("B", depends_on={"A"})
    graph.add_node("C", depends_on={"A"})
    graph.add_node("D", depends_on={"B", "C"})
    graph.add_node("E")  # Standalone node
    return graph


@pytest.fixture
def simple_trace() -> TraceMonoid[dict[str, object]]:
    """Create a simple trace with sequential calls."""
    monoid: TraceMonoid[dict[str, object]] = TraceMonoid()

    e1 = Event.create(
        {"type": "call", "function": "main", "depth": 0},
        source="thread-1",
        event_id="e1",
        timestamp=1.0,
    )
    e2 = Event.create(
        {"type": "call", "function": "helper", "depth": 1},
        source="thread-1",
        event_id="e2",
        timestamp=2.0,
    )
    e3 = Event.create(
        {"type": "call", "function": "util", "depth": 2},
        source="thread-1",
        event_id="e3",
        timestamp=3.0,
    )

    monoid.append_mut(e1)
    monoid.append_mut(e2, depends_on={"e1"})
    monoid.append_mut(e3, depends_on={"e2"})

    return monoid


@pytest.fixture
def concurrent_trace() -> TraceMonoid[dict[str, object]]:
    """Create a trace with concurrent events from multiple threads."""
    monoid: TraceMonoid[dict[str, object]] = TraceMonoid()

    # Thread 1 events
    e1 = Event.create(
        {"type": "call", "function": "worker_a", "depth": 0},
        source="thread-1",
        event_id="e1",
        timestamp=1.0,
    )
    e2 = Event.create(
        {"type": "call", "function": "task_a", "depth": 1},
        source="thread-1",
        event_id="e2",
        timestamp=2.0,
    )

    # Thread 2 events (concurrent)
    e3 = Event.create(
        {"type": "call", "function": "worker_b", "depth": 0},
        source="thread-2",
        event_id="e3",
        timestamp=1.5,
    )
    e4 = Event.create(
        {"type": "call", "function": "task_b", "depth": 1},
        source="thread-2",
        event_id="e4",
        timestamp=2.5,
    )

    monoid.append_mut(e1)
    monoid.append_mut(e2, depends_on={"e1"})
    monoid.append_mut(e3)  # No dependency on thread-1
    monoid.append_mut(e4, depends_on={"e3"})

    return monoid


@pytest.fixture
def trace_with_exception() -> TraceMonoid[dict[str, object]]:
    """Create a trace with an exception event."""
    monoid: TraceMonoid[dict[str, object]] = TraceMonoid()

    e1 = Event.create(
        {"type": "call", "function": "risky_func", "depth": 0},
        source="thread-1",
        event_id="e1",
        timestamp=1.0,
    )
    e2 = Event.create(
        {
            "type": "exception",
            "function": "risky_func",
            "depth": 0,
            "exception": "ValueError",
        },
        source="thread-1",
        event_id="e2",
        timestamp=2.0,
    )

    monoid.append_mut(e1)
    monoid.append_mut(e2, depends_on={"e1"})

    return monoid


@pytest.fixture
def renderer() -> TraceRenderer:
    """Create a renderer with default config."""
    return TraceRenderer()


# =============================================================================
# Call Graph Rendering Tests
# =============================================================================


class TestRenderCallGraph:
    """Tests for render_call_graph method."""

    def test_empty_graph(self, renderer: TraceRenderer) -> None:
        """Empty graph returns appropriate message."""
        graph = DependencyGraph()
        result = renderer.render_call_graph(graph)
        assert result == "Empty graph"

    def test_single_node(self, renderer: TraceRenderer) -> None:
        """Single node graph renders correctly."""
        graph = DependencyGraph()
        graph.add_node("only_node")

        result = renderer.render_call_graph(graph)
        assert "only_node" in result
        assert CHARS["solid"] in result

    def test_simple_chain_tree_layout(
        self, renderer: TraceRenderer, simple_graph: DependencyGraph
    ) -> None:
        """Simple chain renders as tree."""
        result = renderer.render_call_graph(simple_graph, layout="tree")

        # Should contain all nodes
        assert "A" in result
        assert "B" in result
        assert "C" in result

        # Should have tree structure characters
        assert CHARS["branch_start"] in result or CHARS["branch_end"] in result

    def test_branching_graph_tree_layout(
        self, renderer: TraceRenderer, branching_graph: DependencyGraph
    ) -> None:
        """Branching graph renders with proper structure."""
        result = renderer.render_call_graph(branching_graph, layout="tree")

        # All nodes present
        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert "D" in result

    def test_force_layout(
        self, renderer: TraceRenderer, simple_graph: DependencyGraph
    ) -> None:
        """Force layout renders all nodes with connections."""
        result = renderer.render_call_graph(simple_graph, layout="force")

        assert "Call Graph" in result
        assert "A" in result
        assert "B" in result
        assert "C" in result
        assert "3 nodes" in result

    def test_ghost_nodes_shown(
        self, renderer: TraceRenderer, simple_graph: DependencyGraph
    ) -> None:
        """Ghost nodes are marked appropriately."""
        result = renderer.render_call_graph(
            simple_graph, layout="tree", ghost_nodes={"B"}
        )

        assert "[ghost]" in result
        assert CHARS["ghost"] in result

    def test_ghost_nodes_hidden(self, simple_graph: DependencyGraph) -> None:
        """Ghost nodes can be hidden via config."""
        config = RenderConfig(show_ghosts=False)
        renderer = TraceRenderer(config)

        result = renderer.render_call_graph(
            simple_graph, layout="tree", ghost_nodes={"B"}
        )

        assert "[ghost]" not in result

    def test_specific_root(
        self, renderer: TraceRenderer, diamond_graph: DependencyGraph
    ) -> None:
        """Can specify a specific root node."""
        result = renderer.render_call_graph(diamond_graph, layout="tree", root="A")

        # Should start from A
        lines = result.split("\n")
        first_content_line = [l for l in lines if "A" in l][0]
        assert "A" in first_content_line

    def test_truncates_long_names(self) -> None:
        """Long function names are truncated."""
        config = RenderConfig(truncate_names=10)
        renderer = TraceRenderer(config)

        graph = DependencyGraph()
        graph.add_node("very_long_function_name_that_should_be_truncated")

        result = renderer.render_call_graph(graph, layout="tree")

        assert "..." in result
        # With truncate_names=10, we get 7 chars + "..."
        assert "very_lo" in result

    def test_multiple_roots(self, renderer: TraceRenderer) -> None:
        """Handles graphs with multiple roots."""
        graph = DependencyGraph()
        graph.add_node("root1")
        graph.add_node("root2")
        graph.add_node("child", depends_on={"root1"})

        result = renderer.render_call_graph(graph, layout="tree")

        assert "root1" in result
        assert "root2" in result
        assert "child" in result


# =============================================================================
# Timeline Rendering Tests
# =============================================================================


class TestRenderTimeline:
    """Tests for render_timeline method."""

    def test_empty_trace(self, renderer: TraceRenderer) -> None:
        """Empty trace returns appropriate message."""
        monoid: TraceMonoid[dict[str, object]] = TraceMonoid()
        result = renderer.render_timeline(monoid)
        assert result == "Empty trace"

    def test_simple_timeline(
        self, renderer: TraceRenderer, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Simple trace renders as timeline."""
        result = renderer.render_timeline(simple_trace)

        assert "main" in result
        assert "helper" in result
        assert "util" in result
        assert "thread-1" in result

    def test_concurrent_timeline(
        self, renderer: TraceRenderer, concurrent_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Concurrent events from different threads shown side-by-side."""
        result = renderer.render_timeline(concurrent_trace)

        # Both threads should appear
        assert "thread-1" in result
        assert "thread-2" in result

        # Functions from both threads
        assert "worker_a" in result
        assert "worker_b" in result

        # Should report concurrent pairs
        assert "concurrent pairs" in result

    def test_lens_filter(
        self, renderer: TraceRenderer, concurrent_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Lens filter shows only matching source."""
        result = renderer.render_timeline(concurrent_trace, lens="thread-1")

        assert "thread-1" in result
        assert "thread-2" not in result
        assert "worker_a" in result
        assert "worker_b" not in result

    def test_lens_no_match(
        self, renderer: TraceRenderer, concurrent_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Lens with no matching events returns message."""
        result = renderer.render_timeline(concurrent_trace, lens="thread-999")
        assert "No events matching lens" in result

    def test_exception_events_marked(
        self,
        renderer: TraceRenderer,
        trace_with_exception: TraceMonoid[dict[str, object]],
    ) -> None:
        """Exception events are marked with special character."""
        result = renderer.render_timeline(trace_with_exception)
        assert "!" in result  # Exception marker


# =============================================================================
# Flame Graph Rendering Tests
# =============================================================================


class TestRenderFlame:
    """Tests for render_flame method."""

    def test_empty_trace(self, renderer: TraceRenderer) -> None:
        """Empty trace returns appropriate message."""
        monoid: TraceMonoid[dict[str, object]] = TraceMonoid()
        result = renderer.render_flame(monoid)
        assert result == "Empty trace"

    def test_simple_flame(
        self, renderer: TraceRenderer, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Simple trace renders as flame graph."""
        result = renderer.render_flame(simple_trace)

        assert "Flame Graph" in result
        assert "d0" in result  # Depth 0
        assert "d1" in result  # Depth 1
        assert "d2" in result  # Depth 2
        assert CHARS["flame_char"] in result

    def test_flame_shows_depth(
        self, renderer: TraceRenderer, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Flame graph shows depth indicators."""
        result = renderer.render_flame(simple_trace)

        # Should show max depth
        assert "Max depth:" in result
        assert "Total calls:" in result

    def test_flame_legend(
        self, renderer: TraceRenderer, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Flame graph includes legend."""
        result = renderer.render_flame(simple_trace)

        assert "Legend:" in result
        assert "call" in result
        assert "ghost" in result


# =============================================================================
# Diff Rendering Tests
# =============================================================================


class TestRenderDiff:
    """Tests for render_diff method."""

    def test_identical_traces(self, renderer: TraceRenderer) -> None:
        """Identical traces show no changes."""
        monoid: TraceMonoid[dict[str, object]] = TraceMonoid()
        content: dict[str, object] = {"type": "call", "function": "same_func"}
        e1 = Event.create(content, source="thread-1", event_id="e1")
        monoid.append_mut(e1)

        result = renderer.render_diff(monoid, monoid)

        assert "Unchanged:" in result
        assert "Added: 0" in result
        assert "Removed: 0" in result

    def test_added_functions(self, renderer: TraceRenderer) -> None:
        """Shows functions added in after trace."""
        before: TraceMonoid[dict[str, object]] = TraceMonoid()
        after: TraceMonoid[dict[str, object]] = TraceMonoid()

        c1: dict[str, object] = {"type": "call", "function": "original"}
        c2: dict[str, object] = {"type": "call", "function": "new_func"}
        e1 = Event.create(c1, source="thread-1", event_id="e1")
        e2 = Event.create(c2, source="thread-1", event_id="e2")

        before.append_mut(e1)
        after.append_mut(e1)
        after.append_mut(e2)

        result = renderer.render_diff(before, after)

        assert "Added:" in result
        assert "new_func" in result
        assert "+ new_func" in result

    def test_removed_functions(self, renderer: TraceRenderer) -> None:
        """Shows functions removed in after trace."""
        before: TraceMonoid[dict[str, object]] = TraceMonoid()
        after: TraceMonoid[dict[str, object]] = TraceMonoid()

        c1: dict[str, object] = {"type": "call", "function": "kept"}
        c2: dict[str, object] = {"type": "call", "function": "removed_func"}
        e1 = Event.create(c1, source="thread-1", event_id="e1")
        e2 = Event.create(c2, source="thread-1", event_id="e2")

        before.append_mut(e1)
        before.append_mut(e2)
        after.append_mut(e1)

        result = renderer.render_diff(before, after)

        assert "Removed:" in result
        assert "removed_func" in result
        assert "- removed_func" in result

    def test_empty_traces_diff(self, renderer: TraceRenderer) -> None:
        """Handles diff of empty traces."""
        before: TraceMonoid[dict[str, object]] = TraceMonoid()
        after: TraceMonoid[dict[str, object]] = TraceMonoid()

        result = renderer.render_diff(before, after)

        assert "Trace Diff" in result
        assert "Before: 0 events" in result
        assert "After: 0 events" in result


# =============================================================================
# Tree from Monoid Tests
# =============================================================================


class TestRenderTreeFromMonoid:
    """Tests for render_tree_from_monoid method."""

    def test_empty_monoid(self, renderer: TraceRenderer) -> None:
        """Empty monoid returns appropriate message."""
        monoid: TraceMonoid[dict[str, object]] = TraceMonoid()
        result = renderer.render_tree_from_monoid(monoid)
        assert result == "Empty trace"

    def test_simple_tree(
        self, renderer: TraceRenderer, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """Simple trace renders as tree."""
        result = renderer.render_tree_from_monoid(simple_trace)

        assert "main" in result
        assert "helper" in result
        assert "util" in result

    def test_exception_in_tree(
        self,
        renderer: TraceRenderer,
        trace_with_exception: TraceMonoid[dict[str, object]],
    ) -> None:
        """Exception events marked in tree."""
        result = renderer.render_tree_from_monoid(trace_with_exception)
        assert "!" in result  # Exception marker


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_render_graph_function(self, simple_graph: DependencyGraph) -> None:
        """render_graph convenience function works."""
        result = render_graph(simple_graph)
        assert "A" in result
        assert "B" in result

    def test_render_trace_timeline(
        self, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """render_trace with timeline mode."""
        result = render_trace(simple_trace, mode="timeline")
        assert "thread-1" in result

    def test_render_trace_flame(
        self, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """render_trace with flame mode."""
        result = render_trace(simple_trace, mode="flame")
        assert "Flame Graph" in result

    def test_render_trace_tree(
        self, simple_trace: TraceMonoid[dict[str, object]]
    ) -> None:
        """render_trace with tree mode."""
        result = render_trace(simple_trace, mode="tree")
        assert "main" in result

    def test_render_diff_function(self) -> None:
        """render_diff convenience function works."""
        before: TraceMonoid[dict[str, object]] = TraceMonoid()
        after: TraceMonoid[dict[str, object]] = TraceMonoid()

        result = render_diff(before, after)
        assert "Trace Diff" in result


# =============================================================================
# Configuration Tests
# =============================================================================


class TestRenderConfig:
    """Tests for RenderConfig options."""

    def test_width_affects_output(self) -> None:
        """Width config affects output width."""
        narrow = TraceRenderer(RenderConfig(width=40))
        wide = TraceRenderer(RenderConfig(width=120))

        graph = DependencyGraph()
        graph.add_node("test_node")

        # Both should work without error
        narrow_result = narrow.render_call_graph(graph, layout="force")
        wide_result = wide.render_call_graph(graph, layout="force")

        # Force layout header includes width
        assert len(narrow_result.split("\n")[1]) <= 60  # Header line
        assert len(wide_result.split("\n")[1]) <= 80

    def test_truncate_names_zero(self) -> None:
        """truncate_names=0 means no truncation."""
        config = RenderConfig(truncate_names=0)
        renderer = TraceRenderer(config)

        graph = DependencyGraph()
        long_name = "this_is_a_very_long_function_name_that_would_normally_be_truncated"
        graph.add_node(long_name)

        result = renderer.render_call_graph(graph)
        assert long_name in result
        assert "..." not in result


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_non_dict_content_in_trace(self, renderer: TraceRenderer) -> None:
        """Handles events with non-dict content gracefully."""
        monoid: TraceMonoid[str] = TraceMonoid()
        e1 = Event.create(
            "string content",
            source="thread-1",
            event_id="e1",
        )
        monoid.append_mut(e1)

        # Should not raise
        result = renderer.render_flame(monoid)  # type: ignore[arg-type]
        assert "No call events" in result

    def test_special_characters_in_names(self, renderer: TraceRenderer) -> None:
        """Handles special characters in function names."""
        graph = DependencyGraph()
        graph.add_node("func<T>")
        graph.add_node("lambda$1")
        graph.add_node("Class::method")

        result = renderer.render_call_graph(graph)
        assert "func<T>" in result
        assert "lambda$1" in result

    def test_many_depth_levels(self, renderer: TraceRenderer) -> None:
        """Handles traces with many depth levels."""
        monoid: TraceMonoid[dict[str, object]] = TraceMonoid()

        prev_id: str | None = None
        for i in range(10):
            event = Event.create(
                {"type": "call", "function": f"level_{i}", "depth": i},
                source="thread-1",
                event_id=f"e{i}",
            )
            deps = {prev_id} if prev_id else None
            monoid.append_mut(event, depends_on=deps)
            prev_id = f"e{i}"

        result = renderer.render_flame(monoid)
        assert "d0" in result
        assert "d9" in result
        assert "Max depth: 9" in result
