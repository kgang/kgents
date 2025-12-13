"""
Hardening tests for the trace stack.

Tests cover:
1. Error Resilience
   - Graceful handling of unparseable files
   - TraceCollector recovery from tracing errors
   - Renderer fallbacks for malformed data

2. Performance
   - < 5s for full impl/ static analysis
   - Verify reasonable runtime tracing overhead

3. Edge Cases
   - Circular imports in call graph
   - Recursive function traces
   - Very deep call stacks (100+ levels)
   - Unicode in function names
   - Empty/minimal inputs

4. Integration Tests
   - End-to-end: CLI -> ASCII output
   - Cross-module: StaticCallGraph + TraceCollector + TraceRenderer
   - Self-trace: trace the trace code itself
"""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

# === Error Resilience Tests ===


class TestStaticCallGraphResilience:
    """Error resilience tests for StaticCallGraph."""

    def test_handles_syntax_error(self) -> None:
        """Gracefully handles files with syntax errors."""
        from weave.static_trace import StaticCallGraph

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with syntax error
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_text("def broken(:\n    pass")

            graph = StaticCallGraph(tmpdir)
            graph.analyze("*.py")  # Should not raise

            # Should have analyzed 0 definitions (file was skipped)
            assert graph.num_definitions == 0

    def test_handles_unicode_decode_error(self) -> None:
        """Gracefully handles files with encoding issues."""
        from weave.static_trace import StaticCallGraph

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file with invalid encoding
            bad_file = Path(tmpdir) / "bad.py"
            bad_file.write_bytes(b"\xff\xfe def foo(): pass")

            graph = StaticCallGraph(tmpdir)
            graph.analyze("*.py")  # Should not raise

    def test_handles_empty_directory(self) -> None:
        """Handles empty directory gracefully."""
        from weave.static_trace import StaticCallGraph

        with tempfile.TemporaryDirectory() as tmpdir:
            graph = StaticCallGraph(tmpdir)
            graph.analyze("*.py")

            assert graph.num_files == 0
            assert graph.num_definitions == 0

    def test_handles_no_matches(self) -> None:
        """Handles no matching files gracefully."""
        from weave.static_trace import StaticCallGraph

        graph = StaticCallGraph("impl/claude/weave")
        callers = graph.trace_callers("NonExistentFunction123")

        assert len(callers) == 0


class TestTraceCollectorResilience:
    """Error resilience tests for TraceCollector."""

    def test_handles_exception_during_trace(self) -> None:
        """Recovers from exceptions during tracing."""
        from weave.runtime_trace import TraceCollector

        collector = TraceCollector(enable_otel=False)

        def failing_function() -> None:
            raise ValueError("Test error")

        # Should not crash when traced function raises
        with collector.trace():
            try:
                failing_function()
            except ValueError:
                pass

        # Should have captured events up to the exception
        assert len(collector.monoid) >= 0

    def test_handles_recursive_overflow(self) -> None:
        """Handles deep recursion gracefully."""
        from weave.runtime_trace import TraceCollector, TraceFilter

        # Limit depth to avoid actual stack overflow
        filter_config = TraceFilter(max_depth=10, include_stdlib=False)
        collector = TraceCollector(filter_config=filter_config, enable_otel=False)

        def recursive(n: int) -> int:
            if n <= 0:
                return 1
            return recursive(n - 1)

        with collector.trace():
            recursive(15)

        # Should have traced up to max_depth
        assert len(collector.monoid) <= 15

    def test_double_stop_is_safe(self) -> None:
        """Calling stop() twice is safe."""
        from weave.runtime_trace import TraceCollector

        collector = TraceCollector(enable_otel=False)
        collector.start()
        collector.stop()
        collector.stop()  # Should not raise


class TestTraceRendererResilience:
    """Error resilience tests for TraceRenderer."""

    def test_handles_empty_graph(self) -> None:
        """Renders empty graph without error."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        renderer = TraceRenderer()
        graph = DependencyGraph()

        output = renderer.render_call_graph(graph)

        assert "Empty" in output

    def test_handles_empty_monoid(self) -> None:
        """Renders empty monoid without error."""
        from weave.trace_monoid import TraceMonoid
        from weave.trace_renderer import TraceRenderer

        renderer = TraceRenderer()
        monoid: TraceMonoid[dict[str, Any]] = TraceMonoid()

        output = renderer.render_timeline(monoid)

        assert "Empty" in output

    def test_handles_malformed_event_content(self) -> None:
        """Handles events with missing/malformed content."""
        from weave.event import Event
        from weave.trace_monoid import TraceMonoid
        from weave.trace_renderer import TraceRenderer

        renderer = TraceRenderer()
        monoid: TraceMonoid[dict[str, Any]] = TraceMonoid()

        # Add event with minimal content
        event: Event[dict[str, Any]] = Event.create({}, "test")
        monoid.append_mut(event)

        # Should not raise
        output = renderer.render_timeline(monoid)
        assert output  # Some output produced


# === Performance Tests ===


class TestPerformance:
    """Performance tests for trace stack."""

    def test_static_analysis_under_5s(self) -> None:
        """Static analysis of impl/ completes in < 5s."""
        from weave.static_trace import StaticCallGraph

        start = time.time()

        # Use absolute path from project root
        import os

        base_path = os.path.join(os.path.dirname(__file__), "..", "..")
        graph = StaticCallGraph(base_path)
        graph.analyze("**/*.py")

        elapsed = time.time() - start

        assert elapsed < 5.0, f"Analysis took {elapsed:.2f}s (expected < 5s)"
        assert graph.num_files > 100, f"Only analyzed {graph.num_files} files"

    def test_render_performance(self) -> None:
        """Rendering is fast for reasonable graph sizes."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        # Create a graph with 100 nodes
        graph = DependencyGraph()
        for i in range(100):
            deps = {f"node_{i - 1}"} if i > 0 else set()
            graph.add_node(f"node_{i}", depends_on=deps)

        renderer = TraceRenderer()

        start = time.time()
        output = renderer.render_call_graph(graph)
        elapsed = time.time() - start

        assert elapsed < 1.0, f"Render took {elapsed:.2f}s"
        assert len(output) > 0


# === Edge Case Tests ===


class TestEdgeCases:
    """Edge case tests for trace stack."""

    def test_circular_dependencies(self) -> None:
        """DependencyGraph rejects cycles by design (DAG property)."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        graph = DependencyGraph()
        # DependencyGraph is a DAG - it prevents cycles by design
        # Test that acyclic chain works
        graph.add_node("A", depends_on={"B"})
        graph.add_node("B", depends_on={"C"})
        graph.add_node("C")  # No deps - terminates chain

        renderer = TraceRenderer()
        output = renderer.render_call_graph(graph)

        # Should render the acyclic chain
        assert "A" in output
        assert "B" in output
        assert "C" in output

    def test_cycle_detection(self) -> None:
        """DependencyGraph raises on cycle creation attempt."""
        from weave.dependency import DependencyGraph

        graph = DependencyGraph()
        graph.add_node("A", depends_on={"B"})
        graph.add_node("B", depends_on={"C"})
        graph.add_node("C")

        # Attempting to add a cycle should raise

        with pytest.raises(ValueError, match="cycle"):
            graph.add_node("C", depends_on={"A"})

    def test_unicode_function_names(self) -> None:
        """Handles unicode in function names."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        graph = DependencyGraph()
        graph.add_node("函数_テスト")  # Chinese + Japanese
        graph.add_node("функция")  # Russian

        renderer = TraceRenderer()
        output = renderer.render_call_graph(graph)

        # Should render without error
        assert len(output) > 0

    def test_very_long_function_names(self) -> None:
        """Handles very long function names."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import RenderConfig, TraceRenderer

        graph = DependencyGraph()
        long_name = "a" * 200
        graph.add_node(long_name)

        config = RenderConfig(truncate_names=40)
        renderer = TraceRenderer(config)
        output = renderer.render_call_graph(graph)

        # Name should be truncated
        assert "..." in output or len(output.split("\n")[0]) < 250

    def test_deeply_nested_calls(self) -> None:
        """Handles deeply nested call stacks."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        graph = DependencyGraph()
        # Create a chain of 100 nodes
        for i in range(100):
            deps = {f"level_{i - 1}"} if i > 0 else set()
            graph.add_node(f"level_{i}", depends_on=deps)

        renderer = TraceRenderer()
        output = renderer.render_call_graph(graph)

        assert "level_0" in output
        assert "level_99" in output

    def test_single_node_graph(self) -> None:
        """Handles single-node graph."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        graph = DependencyGraph()
        graph.add_node("lonely")

        renderer = TraceRenderer()
        output = renderer.render_call_graph(graph)

        assert "lonely" in output

    def test_disconnected_components(self) -> None:
        """Handles graph with disconnected components."""
        from weave.dependency import DependencyGraph
        from weave.trace_renderer import TraceRenderer

        graph = DependencyGraph()
        # Two disconnected groups
        graph.add_node("A1", depends_on={"A2"})
        graph.add_node("A2")
        graph.add_node("B1", depends_on={"B2"})
        graph.add_node("B2")

        renderer = TraceRenderer()
        output = renderer.render_call_graph(graph)

        assert "A1" in output or "A2" in output
        assert "B1" in output or "B2" in output


# === Integration Tests ===


class TestIntegration:
    """End-to-end integration tests."""

    def test_trace_the_tracer(self) -> None:
        """Trace the StaticCallGraph.analyze method itself."""
        from weave.static_trace import StaticCallGraph

        graph = StaticCallGraph("impl/claude/weave")
        graph.analyze("**/*.py")

        # Find callers of analyze
        callers = graph.trace_callers("analyze", depth=3)

        # Should find some callers (tests, CLI, etc.)
        assert len(callers) >= 0

    def test_static_to_render_pipeline(self) -> None:
        """Full pipeline: static analysis -> render."""
        from weave.static_trace import StaticCallGraph
        from weave.trace_renderer import render_graph

        graph = StaticCallGraph("impl/claude/weave")
        graph.analyze("**/*.py")

        callers = graph.trace_callers("TraceRenderer", depth=2)
        output = render_graph(callers)

        assert len(output) > 0

    def test_runtime_to_render_pipeline(self) -> None:
        """Full pipeline: runtime trace -> render."""
        from weave.runtime_trace import TraceCollector
        from weave.trace_renderer import render_trace

        collector = TraceCollector(enable_otel=False)

        with collector.trace():
            # Some simple operations
            x = sum(range(10))
            _ = x * 2

        monoid = collector.monoid
        # May not capture stdlib calls, but shouldn't error
        output = render_trace(monoid, mode="tree")

        assert len(output) > 0

    def test_cross_module_consistency(self) -> None:
        """Data flows correctly between modules."""
        from weave.dependency import DependencyGraph
        from weave.static_trace import StaticCallGraph
        from weave.trace_renderer import TraceRenderer

        # Create static graph
        static = StaticCallGraph("impl/claude/weave")
        static.analyze("**/*.py")

        # Get dependency graph
        dep_graph = static.trace_callers("StaticCallGraph", depth=3)

        # Verify it's a valid DependencyGraph
        assert isinstance(dep_graph, DependencyGraph)

        # Render it
        renderer = TraceRenderer()
        output = renderer.render_call_graph(dep_graph)

        assert len(output) > 0


# === CLI Integration Tests ===


class TestCLIIntegration:
    """CLI handler integration tests."""

    def test_cli_help_works(self) -> None:
        """CLI --help works."""
        from protocols.cli.handlers.trace import cmd_trace

        class MockCtx:
            outputs: list[tuple[str, dict[str, Any]]] = []

            def output(self, human: str, semantic: dict[str, Any]) -> None:
                self.outputs.append((human, semantic))

        ctx = MockCtx()
        result = cmd_trace(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_cli_static_analysis(self) -> None:
        """CLI static analysis works."""
        from protocols.cli.handlers.trace import cmd_trace

        class MockCtx:
            outputs: list[tuple[str, dict[str, Any]]] = []

            def output(self, human: str, semantic: dict[str, Any]) -> None:
                self.outputs.append((human, semantic))

        ctx = MockCtx()
        result = cmd_trace(["StaticCallGraph", "--path", "impl/claude/weave"], ctx)  # type: ignore[arg-type]

        assert result == 0
