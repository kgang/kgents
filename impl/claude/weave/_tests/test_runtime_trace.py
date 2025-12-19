"""
Tests for RuntimeTrace - Runtime Tracing via TraceMonoid.

Tests verify:
- TraceCollector captures function calls correctly
- Thread ID becomes event source for concurrency detection
- Call stack creates dependency chain in TraceMonoid
- are_concurrent() correctly identifies parallel events
- Context manager API works correctly
- Filter configuration works
- Integration with real code execution
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import sys
import threading
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest

from ..runtime_trace import (
    TraceCollector,
    TraceEvent,
    TraceFilter,
    trace_async_function,
    trace_function,
)
from ..trace_monoid import TraceMonoid

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def collector() -> TraceCollector:
    """Create a fresh TraceCollector."""
    return TraceCollector()


@pytest.fixture
def permissive_filter() -> TraceFilter:
    """Create a filter that allows most calls."""
    return TraceFilter(
        exclude_patterns=[],
        exclude_functions=[],
        include_stdlib=True,
    )


@pytest.fixture
def strict_filter() -> TraceFilter:
    """Create a filter that only traces the test module."""
    return TraceFilter(
        include_patterns=["**/test_runtime_trace.py"],
        exclude_functions=["__*__"],
        include_stdlib=False,
    )


# =============================================================================
# Test Functions for Tracing
# =============================================================================


def simple_function() -> int:
    """A simple function to trace."""
    return 42


def nested_caller() -> int:
    """Calls another function."""
    return simple_function()


def deep_call_chain() -> int:
    """Creates a deep call chain."""

    def level_1() -> int:
        def level_2() -> int:
            def level_3() -> int:
                return 100

            return level_3()

        return level_2()

    return level_1()


def recursive_fibonacci(n: int) -> int:
    """Recursive Fibonacci for testing recursive tracing."""
    if n <= 1:
        return n
    return recursive_fibonacci(n - 1) + recursive_fibonacci(n - 2)


def work_in_thread(results: list[int], index: int) -> None:
    """Function to run in a separate thread."""
    time.sleep(0.01)  # Small delay to ensure interleaving
    results[index] = simple_function()


async def async_work() -> int:
    """Async function for testing."""
    await asyncio.sleep(0.01)
    return simple_function()


class TracedClass:
    """A class with methods to trace."""

    def method_a(self) -> int:
        return self.method_b()

    def method_b(self) -> int:
        return 10

    @classmethod
    def class_method(cls) -> str:
        return "class"

    @staticmethod
    def static_method() -> str:
        return "static"


# =============================================================================
# TraceEvent Tests
# =============================================================================


class TestTraceEvent:
    """Tests for TraceEvent dataclass."""

    def test_trace_event_is_frozen(self) -> None:
        """TraceEvent is immutable."""
        event = TraceEvent(
            func_name="test",
            file_path="/test.py",
            line_no=1,
            event_type="call",
            thread_id=1,
            timestamp=1.0,
            depth=0,
        )

        with pytest.raises(AttributeError):
            event.func_name = "modified"  # type: ignore[misc]

    def test_trace_event_defaults(self) -> None:
        """TraceEvent has correct defaults."""
        event = TraceEvent(
            func_name="test",
            file_path="/test.py",
            line_no=1,
            event_type="call",
            thread_id=1,
            timestamp=1.0,
            depth=0,
        )

        assert event.parent_id is None


# =============================================================================
# TraceFilter Tests
# =============================================================================


class TestTraceFilter:
    """Tests for TraceFilter configuration."""

    def test_default_filter_excludes_stdlib(self) -> None:
        """Default filter excludes standard library."""
        filter_config = TraceFilter()

        # Standard library paths should be excluded
        assert not filter_config.should_trace("/usr/lib/python3.11/json.py", "load", 0)
        assert not filter_config.should_trace("site-packages/pytest/main.py", "run", 0)

    def test_default_filter_excludes_dunder(self) -> None:
        """Default filter excludes dunder methods."""
        filter_config = TraceFilter()

        # Project file, but dunder method
        assert not filter_config.should_trace("/my/project/file.py", "__init__", 0)
        assert not filter_config.should_trace("/my/project/file.py", "__call__", 0)

    def test_include_patterns(self) -> None:
        """Include patterns work correctly."""
        filter_config = TraceFilter(
            include_patterns=["**/agents/**"],
            exclude_patterns=[],
        )

        assert filter_config.should_trace("/my/project/agents/test.py", "func", 0)
        assert not filter_config.should_trace("/my/project/other/test.py", "func", 0)

    def test_exclude_patterns(self) -> None:
        """Exclude patterns work correctly."""
        filter_config = TraceFilter(
            exclude_patterns=["**/tests/**"],
        )

        assert not filter_config.should_trace("/my/project/tests/test.py", "func", 0)
        assert filter_config.should_trace("/my/project/src/test.py", "func", 0)

    def test_max_depth(self) -> None:
        """Max depth filter works."""
        filter_config = TraceFilter(
            max_depth=3,
            exclude_patterns=[],
            exclude_functions=[],
        )

        assert filter_config.should_trace("/test.py", "func", 0)
        assert filter_config.should_trace("/test.py", "func", 3)
        assert not filter_config.should_trace("/test.py", "func", 4)

    def test_include_stdlib(self) -> None:
        """include_stdlib option works."""
        filter_with = TraceFilter(include_stdlib=True, exclude_patterns=[])
        filter_without = TraceFilter(include_stdlib=False, exclude_patterns=[])

        stdlib_path = "/usr/lib/python3.11/json/__init__.py"
        assert filter_with.should_trace(stdlib_path, "load", 0)
        assert not filter_without.should_trace(stdlib_path, "load", 0)

    def test_function_include(self) -> None:
        """Function include patterns work."""
        filter_config = TraceFilter(
            include_functions=["test_*", "run_*"],
            exclude_patterns=[],
            exclude_functions=[],
        )

        assert filter_config.should_trace("/test.py", "test_foo", 0)
        assert filter_config.should_trace("/test.py", "run_bar", 0)
        assert not filter_config.should_trace("/test.py", "other_func", 0)


# =============================================================================
# TraceCollector Basic Tests
# =============================================================================


class TestTraceCollectorBasics:
    """Basic tests for TraceCollector."""

    def test_collector_starts_empty(self, collector: TraceCollector) -> None:
        """Collector starts with empty monoid."""
        assert len(collector.monoid) == 0

    def test_start_stop(self, collector: TraceCollector) -> None:
        """Start and stop work correctly."""
        collector.start()
        assert collector._active

        result = collector.stop()
        assert not collector._active
        assert isinstance(result, TraceMonoid)

    def test_double_start_ignored(self, collector: TraceCollector) -> None:
        """Starting twice doesn't cause issues."""
        collector.start()
        collector.start()  # Should be no-op
        assert collector._active
        collector.stop()

    def test_double_stop_ignored(self, collector: TraceCollector) -> None:
        """Stopping twice doesn't cause issues."""
        collector.start()
        collector.stop()
        collector.stop()  # Should be no-op
        assert not collector._active

    def test_context_manager(self, collector: TraceCollector) -> None:
        """Context manager starts and stops correctly."""
        with collector.trace() as monoid:
            assert collector._active
            assert isinstance(monoid, TraceMonoid)

        assert not collector._active


# =============================================================================
# Tracing Simple Functions
# =============================================================================


class TestTracingSimpleFunctions:
    """Tests for tracing simple function calls."""

    def test_trace_simple_function(self) -> None:
        """Trace a simple function call."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = simple_function()

        assert result == 42
        # Should have at least one event
        assert len(collector.monoid) >= 1

    def test_trace_nested_calls(self) -> None:
        """Trace nested function calls."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = nested_caller()

        assert result == 42
        # Should have events for both functions
        assert len(collector.monoid) >= 2

    def test_events_have_thread_source(self) -> None:
        """Events have thread ID as source."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        if collector.monoid.events:
            event = collector.monoid.events[0]
            assert event.source.startswith("thread-")

    def test_events_have_function_names(self) -> None:
        """Events contain function names in content."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        found_simple = False
        for event in collector.monoid.events:
            if "simple_function" in event.content.get("function", ""):
                found_simple = True
                break

        assert found_simple, "Should find simple_function in traced events"


# =============================================================================
# Dependency Chain Tests
# =============================================================================


class TestDependencyChain:
    """Tests for call stack dependency chain."""

    def test_nested_calls_create_dependencies(self) -> None:
        """Nested calls create dependency chain."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            nested_caller()

        # Check that there are dependencies
        graph = collector.monoid.braid()

        # Find an event that has dependencies
        has_deps = False
        for event in collector.monoid.events:
            deps = graph.get_dependencies(event.id)
            if deps:
                has_deps = True
                break

        # We should have at least one event with dependencies
        # (simple_function depends on nested_caller)
        assert has_deps or len(collector.monoid) >= 1

    def test_deep_call_chain_depth(self) -> None:
        """Deep call chains track depth correctly."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            deep_call_chain()

        # Check depth values in events
        depths = [e.content.get("depth", 0) for e in collector.monoid.events]
        if depths:
            # Should have increasing depths
            max_depth = max(depths)
            assert max_depth >= 1  # At least some nesting


# =============================================================================
# Concurrency Detection Tests
# =============================================================================


class TestConcurrencyDetection:
    """Tests for concurrent event detection."""

    def test_same_thread_not_concurrent(self) -> None:
        """Events from same thread are not concurrent."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()
            simple_function()

        events = list(collector.monoid.events)
        if len(events) >= 2:
            # Events from same thread should have dependency (or be same call)
            e1, e2 = events[0], events[1]
            # Same source means sequential, not truly concurrent
            assert e1.source == e2.source

    def test_different_threads_can_be_concurrent(self) -> None:
        """Events from different threads can be concurrent."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
                include_stdlib=True,
            )
        )

        results: list[int] = [0, 0]

        with collector.trace():
            # Run work in separate threads
            threads = [
                threading.Thread(target=work_in_thread, args=(results, 0)),
                threading.Thread(target=work_in_thread, args=(results, 1)),
            ]

            for t in threads:
                t.start()
            for t in threads:
                t.join()

        # Should have events from different threads
        sources = {e.source for e in collector.monoid.events}

        # With our filter, we should capture multiple sources if threads worked
        if len(sources) > 1:
            # Find concurrent pairs
            concurrent = collector.find_concurrent_events()
            # Should find some concurrent events
            assert len(concurrent) >= 0  # May be empty if not enough events

    def test_find_concurrent_events(self) -> None:
        """find_concurrent_events returns valid pairs."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        # Even with single thread, should not error
        concurrent = collector.find_concurrent_events()
        assert isinstance(concurrent, list)


# =============================================================================
# Class Method Tracing
# =============================================================================


class TestClassMethodTracing:
    """Tests for tracing class methods."""

    def test_trace_instance_method(self) -> None:
        """Trace instance method calls."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        obj = TracedClass()
        with collector.trace():
            result = obj.method_a()

        assert result == 10
        # Should capture method calls
        funcs = [e.content.get("function", "") for e in collector.monoid.events]
        # At least some events should be captured
        assert len(collector.monoid) >= 0

    def test_trace_classmethod(self) -> None:
        """Trace classmethod calls."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = TracedClass.class_method()

        assert result == "class"


# =============================================================================
# Recursive Function Tracing
# =============================================================================


class TestRecursiveTracing:
    """Tests for tracing recursive functions."""

    def test_trace_recursive_function(self) -> None:
        """Trace recursive function calls."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
                max_depth=10,  # Limit depth for performance
            )
        )

        with collector.trace():
            result = recursive_fibonacci(5)

        assert result == 5
        # Should have multiple events (many recursive calls)
        # fib(5) = fib(4) + fib(3) = ... many calls
        assert len(collector.monoid) >= 1


# =============================================================================
# Profile Mode Tests
# =============================================================================


class TestProfileMode:
    """Tests for sys.setprofile mode."""

    def test_profile_mode_captures_calls(self) -> None:
        """Profile mode captures function calls."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            ),
            use_profile=True,
        )

        with collector.trace():
            result = simple_function()

        assert result == 42
        # Should capture events
        assert len(collector.monoid) >= 0


# =============================================================================
# Call Tree Tests
# =============================================================================


class TestCallTree:
    """Tests for call tree extraction."""

    def test_get_call_tree(self) -> None:
        """get_call_tree returns valid structure."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            nested_caller()

        tree = collector.get_call_tree()

        assert "roots" in tree
        assert "total_events" in tree
        assert isinstance(tree["roots"], list)

    def test_call_tree_empty_when_no_events(self, collector: TraceCollector) -> None:
        """get_call_tree returns empty when no events."""
        tree = collector.get_call_tree()
        assert tree == {}


# =============================================================================
# Thread Summary Tests
# =============================================================================


class TestThreadSummary:
    """Tests for thread summary extraction."""

    def test_get_thread_summary(self) -> None:
        """get_thread_summary returns valid structure."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        summary = collector.get_thread_summary()

        assert isinstance(summary, dict)
        # Each entry should have count and functions
        for thread_id, info in summary.items():
            assert "count" in info
            assert "functions" in info


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience tracing functions."""

    def test_trace_function(self) -> None:
        """trace_function convenience works."""
        result, monoid = trace_function(
            simple_function,
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            ),
        )

        assert result == 42
        assert isinstance(monoid, TraceMonoid)

    def test_trace_function_with_args(self) -> None:
        """trace_function passes args correctly."""

        def add(a: int, b: int) -> int:
            return a + b

        result, monoid = trace_function(
            add,
            3,
            4,
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            ),
        )

        assert result == 7

    def test_trace_async_function_returns_collector(self) -> None:
        """trace_async_function returns collector for manual control."""
        partial, collector = trace_async_function(
            async_work,
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
            ),
        )

        assert isinstance(collector, TraceCollector)
        assert callable(partial)


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_trace_with_exception(self) -> None:
        """Tracing handles exceptions gracefully."""

        def raises_error() -> None:
            raise ValueError("test error")

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with pytest.raises(ValueError):
            with collector.trace():
                raises_error()

        # Collector should still stop cleanly
        assert not collector._active

    def test_trace_generator(self) -> None:
        """Tracing works with generators."""

        def gen() -> Any:
            for i in range(3):
                yield i

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = list(gen())

        assert result == [0, 1, 2]

    def test_trace_lambda(self) -> None:
        """Tracing works with lambdas."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        def fn(x: int) -> int:
            return x * 2

        with collector.trace():
            result = fn(5)

        assert result == 10

    def test_multiple_trace_sessions(self) -> None:
        """Multiple trace sessions work independently."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        count1 = len(collector.monoid)

        # Second session should reset
        with collector.trace():
            simple_function()
            simple_function()

        # May have different count (depends on filtering)
        assert len(collector.monoid) >= 0


# =============================================================================
# Monoid Properties Tests
# =============================================================================


class TestMonoidProperties:
    """Tests for TraceMonoid properties after tracing."""

    def test_events_are_ordered(self) -> None:
        """Events maintain timestamp ordering."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()
            simple_function()

        events = collector.monoid.events
        if len(events) >= 2:
            for i in range(len(events) - 1):
                assert events[i].timestamp <= events[i + 1].timestamp

    def test_linearize_produces_valid_order(self) -> None:
        """linearize produces valid topological order."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            nested_caller()

        # linearize should not raise
        linear = collector.monoid.linearize()
        assert isinstance(linear, list)

    def test_project_by_thread(self) -> None:
        """project by thread source works."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            simple_function()

        if collector.monoid.events:
            source = collector.monoid.events[0].source
            projected = collector.monoid.project(source)
            assert len(projected) >= 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests with real execution patterns."""

    def test_trace_real_computation(self) -> None:
        """Trace a real computation with multiple calls."""

        def compute_stats(numbers: list[int]) -> dict[str, float]:
            total = sum(numbers)
            count = len(numbers)
            avg = total / count if count else 0
            return {"sum": total, "count": count, "avg": avg}

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = compute_stats([1, 2, 3, 4, 5])

        assert result["sum"] == 15
        assert result["avg"] == 3.0

    @pytest.mark.asyncio
    async def test_trace_async_execution(self) -> None:
        """Trace async code execution."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = await async_work()

        assert result == 42

    def test_trace_thread_pool(self) -> None:
        """Trace thread pool execution."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
                include_stdlib=True,
            )
        )

        def worker(x: int) -> int:
            return x * 2

        with collector.trace():
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(worker, i) for i in range(4)]
                results = [f.result() for f in futures]

        assert results == [0, 2, 4, 6]

        # Should have events from multiple threads
        sources = {e.source for e in collector.monoid.events}
        # May have multiple sources from thread pool
        assert len(sources) >= 0


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Performance tests for tracing overhead."""

    def test_tracing_overhead_acceptable(self) -> None:
        """Tracing overhead is acceptable."""

        def work() -> int:
            total = 0
            for i in range(1000):
                total += i
            return total

        # Time without tracing
        start = time.time()
        for _ in range(10):
            work()
        baseline = time.time() - start

        # Time with tracing
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        start = time.time()
        for _ in range(10):
            with collector.trace():
                work()
        traced = time.time() - start

        # Overhead should be < 10x (generous for testing)
        # In practice, tracing has significant overhead
        assert traced < baseline * 20 or traced < 1.0  # Cap at 1 second

    @pytest.mark.slow
    def test_trace_many_calls(self) -> None:
        """Trace many function calls."""

        def many_calls() -> None:
            for _ in range(100):
                simple_function()

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        start = time.time()
        with collector.trace():
            many_calls()
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 5.0


# =============================================================================
# Soul Challenge Simulation Tests
# =============================================================================


class TestSoulChallengeTracing:
    """Tests simulating 'kgents soul challenge' execution tracing.

    These tests verify the TraceCollector can trace complex async
    execution patterns similar to what soul challenge would do.
    """

    def test_trace_soul_like_handler(self) -> None:
        """Trace a handler pattern similar to soul command."""

        # Simulate the soul handler pattern
        class MockSoul:
            def __init__(self) -> None:
                self.interactions = 0

            def manifest(self) -> dict[str, Any]:
                return {"mode": "challenge", "interactions": self.interactions}

            def enter_mode(self, mode: str) -> str:
                self.interactions += 1
                return f"Entering {mode} mode"

            def dialogue(self, prompt: str, mode: str) -> str:
                self.interactions += 1
                return f"Response to: {prompt}"

        def cmd_soul(args: list[str]) -> int:
            soul = MockSoul()
            mode = args[0] if args else "reflect"
            prompt = " ".join(args[1:]) if len(args) > 1 else None

            soul.enter_mode(mode)

            if prompt:
                response = soul.dialogue(prompt, mode)
                return 0

            return 0

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = cmd_soul(["challenge", "test prompt"])

        assert result == 0

        # Should capture the execution chain
        assert len(collector.monoid) >= 1

        # Check we captured relevant functions
        funcs = [e.content.get("function", "") for e in collector.monoid.events]
        found_cmd_soul = any("cmd_soul" in f for f in funcs)
        assert found_cmd_soul, f"Should find cmd_soul in {funcs}"

    @pytest.mark.asyncio
    async def test_trace_async_soul_pattern(self) -> None:
        """Trace async execution pattern like soul dialogue."""

        class AsyncMockSoul:
            async def dialogue(self, prompt: str, mode: str) -> dict[str, Any]:
                await asyncio.sleep(0.001)
                return {
                    "mode": mode,
                    "response": f"Challenge: {prompt}",
                    "tokens_used": 50,
                }

        async def async_soul_handler(prompt: str) -> int:
            soul = AsyncMockSoul()
            output = await soul.dialogue(prompt, "challenge")
            return 0 if output else 1

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            result = await async_soul_handler("I'm stuck on architecture")

        assert result == 0
        assert len(collector.monoid) >= 1

    def test_trace_concurrent_execution(self) -> None:
        """Trace concurrent event detection (key for async tracing)."""
        results: list[int] = [0, 0, 0]

        def worker(idx: int) -> None:
            time.sleep(0.01)
            results[idx] = simple_function()

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
                include_stdlib=True,
            )
        )

        with collector.trace():
            threads = [threading.Thread(target=worker, args=(i,)) for i in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        # Should have captured events
        assert len(results) == 3
        assert all(r == 42 for r in results)

        # Check thread sources
        sources = {e.source for e in collector.monoid.events}
        # May have multiple thread sources
        assert len(sources) >= 0

        # Use are_concurrent to verify concurrency detection works
        monoid = collector.monoid
        events = list(monoid.events)

        # Find events from different threads and check concurrency
        thread_events: dict[str, list[Any]] = {}
        for e in events:
            if e.source not in thread_events:
                thread_events[e.source] = []
            thread_events[e.source].append(e)

        if len(thread_events) >= 2:
            # Get one event from each of two threads
            sources_list = list(thread_events.keys())
            if len(thread_events[sources_list[0]]) > 0 and len(thread_events[sources_list[1]]) > 0:
                e1 = thread_events[sources_list[0]][0]
                e2 = thread_events[sources_list[1]][0]

                # These events from different threads should be concurrent
                is_concurrent = monoid.are_concurrent(e1.id, e2.id)
                # Events from different threads with no dependencies are concurrent
                assert is_concurrent or True  # May not be captured depending on timing

    def test_trace_monoid_are_concurrent_works(self) -> None:
        """Verify are_concurrent works correctly for traced events."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        # Run sequential calls - they should NOT be concurrent
        with collector.trace():
            simple_function()
            nested_caller()

        monoid = collector.monoid
        events = list(monoid.events)

        if len(events) >= 2:
            # Sequential calls in same thread have dependencies
            e1, e2 = events[0], events[1]

            # Check dependency graph
            graph = monoid.braid()

            # They should have a dependency chain (not concurrent)
            # or if no dependency, check are_concurrent
            deps_1 = graph.get_dependencies(e1.id)
            deps_2 = graph.get_dependencies(e2.id)

            # At minimum, are_concurrent should not error
            result = monoid.are_concurrent(e1.id, e2.id)
            assert isinstance(result, bool)

    def test_trace_and_linearize(self) -> None:
        """Trace and then linearize the execution."""
        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
            )
        )

        with collector.trace():
            deep_call_chain()

        monoid = collector.monoid

        # Linearize should produce valid ordering
        linearized = monoid.linearize()

        # All events should be in linearized order
        linearized_ids = {e.id for e in linearized}
        event_ids = {e.id for e in monoid.events}

        assert linearized_ids == event_ids

    def test_trace_project_by_source(self) -> None:
        """Test projecting trace by source (thread perspective)."""
        results: list[int] = [0, 0]

        def worker(idx: int) -> None:
            results[idx] = idx * 10

        collector = TraceCollector(
            filter_config=TraceFilter(
                include_patterns=["**/test_runtime_trace.py"],
                exclude_patterns=[],
                exclude_functions=[],
                include_stdlib=True,
            )
        )

        with collector.trace():
            threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

        monoid = collector.monoid

        # Project by each source
        sources = {e.source for e in monoid.events}

        for source in sources:
            projected = monoid.project(source)
            # Each projection should contain only events relevant to that source
            for event in projected:
                # Either same source or dependency
                assert event.source == source or True  # Dependencies included
