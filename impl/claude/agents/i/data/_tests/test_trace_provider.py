"""
Tests for TraceDataProvider.

Tests verify:
1. Singleton pattern
2. Static analysis collection (real data)
3. Runtime trace metrics
4. Call tree building
5. Anomaly detection
6. Graceful degradation
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import pytest

# === Singleton Tests ===


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_instance_returns_same_object(self) -> None:
        """get_instance returns the same object."""
        from agents.i.data.trace_provider import TraceDataProvider

        # Clear singleton for test
        TraceDataProvider._instance = None

        instance1 = TraceDataProvider.get_instance()
        instance2 = TraceDataProvider.get_instance()

        assert instance1 is instance2

    def test_get_trace_provider_returns_singleton(self) -> None:
        """get_trace_provider returns singleton."""
        from agents.i.data.trace_provider import (
            TraceDataProvider,
            get_trace_provider,
        )

        # Clear singleton for test
        TraceDataProvider._instance = None

        provider = get_trace_provider()
        instance = TraceDataProvider.get_instance()

        assert provider is instance


# === Static Analysis Tests ===


class TestStaticAnalysis:
    """Tests for static analysis with real data."""

    @pytest.mark.asyncio
    async def test_analyze_static_real_data(self) -> None:
        """Static analysis works with real codebase."""
        from agents.i.data.trace_provider import TraceDataProvider

        # Clear singleton for test
        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        # Set path to weave module
        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        provider.set_base_path(weave_path)

        metrics = await provider.analyze_static()

        assert metrics.is_available
        assert metrics.files_analyzed > 0
        assert metrics.definitions_found > 0
        assert metrics.status_text == "OK"

    @pytest.mark.asyncio
    async def test_analyze_static_caches_results(self) -> None:
        """Static analysis caches results."""
        from agents.i.data.trace_provider import TraceDataProvider

        # Clear singleton for test
        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        provider.set_base_path(weave_path)

        # First analysis
        metrics1 = await provider.analyze_static()

        # Second should use cache (analysis_time_ms = 0)
        metrics2 = await provider.analyze_static()

        assert metrics1.files_analyzed == metrics2.files_analyzed
        # Cache returns same metrics
        assert (
            metrics2.analysis_time_ms == 0 or metrics2.analysis_time_ms == metrics1.analysis_time_ms
        )

    @pytest.mark.asyncio
    async def test_analyze_static_force_reanalyze(self) -> None:
        """force=True reanalyzes."""
        from agents.i.data.trace_provider import TraceDataProvider

        # Clear singleton for test
        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        provider.set_base_path(weave_path)

        # First analysis
        await provider.analyze_static()

        # Force reanalyze
        metrics = await provider.analyze_static(force=True)

        # Should have new analysis time
        assert metrics.analysis_time_ms > 0


# === Callers/Callees Tests ===


class TestCallersCallees:
    """Tests for caller/callee lookups."""

    @pytest.fixture(autouse=True)
    async def setup_provider(self) -> None:
        """Set up provider with analyzed data."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        self.provider = TraceDataProvider.get_instance()

        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        self.provider.set_base_path(weave_path)
        await self.provider.analyze_static()

    def test_get_callers(self) -> None:
        """get_callers returns dependency graph."""
        callers = self.provider.get_callers("TraceRenderer", depth=2)

        assert callers is not None
        # May or may not have callers depending on codebase state

    def test_get_callees(self) -> None:
        """get_callees returns dependency graph."""
        callees = self.provider.get_callees("StaticCallGraph", depth=2)

        assert callees is not None

    def test_get_callers_unknown_function(self) -> None:
        """get_callers handles unknown functions."""
        callers = self.provider.get_callers("NonExistentFunction123", depth=2)

        # Returns empty graph, not None
        assert callers is not None
        assert len(callers) == 0


# === Call Tree Tests ===


class TestCallTree:
    """Tests for call tree building."""

    @pytest.fixture(autouse=True)
    async def setup_provider(self) -> None:
        """Set up provider with analyzed data."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        self.provider = TraceDataProvider.get_instance()

        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        self.provider.set_base_path(weave_path)
        await self.provider.analyze_static()

    def test_build_call_tree_callers(self) -> None:
        """build_call_tree with callers direction."""
        tree = self.provider.build_call_tree("TraceRenderer", depth=2, direction="callers")

        # May be None if no callers found
        if tree is not None:
            assert tree.name == "TraceRenderer"
            assert tree.depth == 0

    def test_build_call_tree_callees(self) -> None:
        """build_call_tree with callees direction."""
        tree = self.provider.build_call_tree("StaticCallGraph", depth=2, direction="callees")

        if tree is not None:
            assert tree.name == "StaticCallGraph"

    def test_call_tree_render(self) -> None:
        """CallTreeNode.render produces ASCII."""
        from agents.i.data.trace_provider import CallTreeNode

        root = CallTreeNode(name="root", depth=0)
        child1 = CallTreeNode(name="child1", depth=1)
        child2 = CallTreeNode(name="child2", depth=1, is_ghost=True)
        root.children = [child1, child2]

        output = root.render()

        assert "root" in output
        assert "child1" in output
        assert "child2" in output
        assert "[ghost]" in output


# === Runtime Metrics Tests ===


class TestRuntimeMetrics:
    """Tests for runtime trace metrics."""

    def test_get_runtime_metrics_empty(self) -> None:
        """get_runtime_metrics works with no trace."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        metrics = provider.get_runtime_metrics()

        assert metrics.is_available
        assert metrics.total_events == 0
        assert metrics.status_text == "IDLE"

    def test_set_runtime_trace(self) -> None:
        """set_runtime_trace stores monoid."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        # Create a mock monoid
        class MockMonoid:
            events: list[Any] = []

        provider.set_runtime_trace(MockMonoid())

        metrics = provider.get_runtime_metrics()
        assert metrics.total_events == 0

    def test_clear_runtime_trace(self) -> None:
        """clear_runtime_trace clears monoid."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        provider.set_runtime_trace("mock")
        provider.clear_runtime_trace()

        assert provider._runtime_monoid is None


# === Anomaly Detection Tests ===


class TestAnomalyDetection:
    """Tests for anomaly detection."""

    def test_detect_anomalies_empty(self) -> None:
        """detect_anomalies with no data returns empty."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        anomalies = provider.detect_anomalies()

        assert anomalies == []

    def test_detect_deep_recursion(self) -> None:
        """Detects deep recursion in trace."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        # Create mock monoid with deep call
        class MockEvent:
            content = {"function": "recursive_func", "depth": 100}
            source = "thread-1"

        class MockMonoid:
            events = [MockEvent()]

        provider.set_runtime_trace(MockMonoid())
        anomalies = provider.detect_anomalies()

        assert len(anomalies) == 1
        assert anomalies[0].type == "deep_recursion"
        assert anomalies[0].severity == "warning"


# === Unified Collection Tests ===


class TestUnifiedCollection:
    """Tests for collect_metrics.

    NOTE: Tests with include_static=True do full static analysis (~20s).
    Mark with @pytest.mark.slow to exclude from default runs.
    """

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_collect_metrics_full(self) -> None:
        """collect_metrics returns complete bundle (SLOW: ~20s due to static analysis)."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        weave_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "weave")
        provider.set_base_path(weave_path)

        metrics = await provider.collect_metrics(include_static=True)

        assert metrics.static.is_available
        assert metrics.runtime.is_available
        assert isinstance(metrics.anomalies, list)
        assert metrics.collected_at is not None

    @pytest.mark.asyncio
    async def test_collect_metrics_skip_static(self) -> None:
        """collect_metrics with include_static=False (fast)."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        metrics = await provider.collect_metrics(include_static=False)

        # Should still return metrics structure
        assert metrics is not None
        assert metrics.runtime.is_available

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_collect_trace_metrics_convenience(self) -> None:
        """collect_trace_metrics convenience function (SLOW: ~20s due to static analysis)."""
        from agents.i.data.trace_provider import collect_trace_metrics

        metrics = await collect_trace_metrics(include_static=True)

        assert metrics is not None


# === Metric Types Tests ===


class TestMetricTypes:
    """Tests for metric dataclasses."""

    def test_static_analysis_metrics_status(self) -> None:
        """StaticAnalysisMetrics status_text."""
        from agents.i.data.trace_provider import StaticAnalysisMetrics

        unavailable = StaticAnalysisMetrics(is_available=False)
        assert unavailable.status_text == "UNAVAILABLE"

        not_analyzed = StaticAnalysisMetrics(is_available=True, files_analyzed=0)
        assert not_analyzed.status_text == "NOT ANALYZED"

        ok = StaticAnalysisMetrics(is_available=True, files_analyzed=10)
        assert ok.status_text == "OK"

    def test_runtime_trace_metrics_status(self) -> None:
        """RuntimeTraceMetrics status_text."""
        from agents.i.data.trace_provider import RuntimeTraceMetrics

        unavailable = RuntimeTraceMetrics(is_available=False)
        assert unavailable.status_text == "UNAVAILABLE"

        collecting = RuntimeTraceMetrics(is_available=True, is_collecting=True)
        assert collecting.status_text == "COLLECTING"

        idle = RuntimeTraceMetrics(is_available=True, total_events=0)
        assert idle.status_text == "IDLE"

        active = RuntimeTraceMetrics(is_available=True, total_events=100)
        assert active.status_text == "100 events"

    def test_trace_metrics_health(self) -> None:
        """TraceMetrics is_healthy."""
        from agents.i.data.trace_provider import (
            StaticAnalysisMetrics,
            TraceAnomaly,
            TraceMetrics,
        )

        healthy = TraceMetrics(
            static=StaticAnalysisMetrics(is_available=True),
            anomalies=[],
        )
        assert healthy.is_healthy

        unhealthy = TraceMetrics(
            static=StaticAnalysisMetrics(is_available=True),
            anomalies=[TraceAnomaly(type="error", description="", location="", severity="error")],
        )
        assert not unhealthy.is_healthy


# === Subscription Tests ===


class TestSubscription:
    """Tests for subscription mechanism."""

    def test_subscribe_and_notify(self) -> None:
        """Subscribers receive metrics updates."""
        from agents.i.data.trace_provider import TraceDataProvider, TraceMetrics

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        received: list[TraceMetrics] = []

        def callback(metrics: TraceMetrics) -> None:
            received.append(metrics)

        provider.subscribe(callback)

        # Manually notify (collect_metrics does this)
        provider._subscribers[0](TraceMetrics())

        assert len(received) == 1

    def test_unsubscribe(self) -> None:
        """Unsubscribe removes callback."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        def callback(metrics: Any) -> None:
            pass

        provider.subscribe(callback)
        assert len(provider._subscribers) == 1

        provider.unsubscribe(callback)
        assert len(provider._subscribers) == 0


# === Hardening Tests ===


class TestThreadSafety:
    """Tests for thread-safe singleton pattern."""

    def test_concurrent_singleton_access(self) -> None:
        """Concurrent access returns same instance."""
        import threading

        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        instances: list[TraceDataProvider] = []
        errors: list[Exception] = []

        def get_instance() -> None:
            try:
                inst = TraceDataProvider.get_instance()
                instances.append(inst)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(instances) == 10
        # All instances should be the same object
        assert all(inst is instances[0] for inst in instances)


class TestGracefulDegradation:
    """Tests for graceful degradation on invalid inputs."""

    def test_get_ghost_calls_invalid_target(self) -> None:
        """get_ghost_calls handles invalid targets gracefully."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        # Empty string
        result = provider.get_ghost_calls("")
        assert result == []

        # None (via type ignore for testing)
        result = provider.get_ghost_calls(None)  # type: ignore[arg-type]
        assert result == []

    def test_detect_anomalies_with_malformed_monoid(self) -> None:
        """detect_anomalies handles malformed monoid gracefully."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        # Monoid without events attribute
        class BrokenMonoid:
            pass

        provider.set_runtime_trace(BrokenMonoid())
        anomalies = provider.detect_anomalies()
        assert anomalies == []

        # Monoid with non-iterable events
        class NonIterableMonoid:
            events = 42  # Not a list

        provider.set_runtime_trace(NonIterableMonoid())
        anomalies = provider.detect_anomalies()
        assert anomalies == []

    def test_build_tree_handles_missing_methods(self) -> None:
        """_build_tree_from_graph handles graphs without get_dependencies."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        class GraphWithoutMethod:
            pass

        tree = provider._build_tree_from_graph("test", GraphWithoutMethod(), set())
        assert tree.name == "test"
        assert tree.children == []

    def test_build_tree_handles_non_string_deps(self) -> None:
        """_build_tree_from_graph skips non-string dependencies."""
        from agents.i.data.trace_provider import TraceDataProvider

        TraceDataProvider._instance = None
        provider = TraceDataProvider.get_instance()

        class GraphWithMixedDeps:
            def get_dependencies(self, node: str) -> list[Any]:
                return ["valid_dep", 123, None, "another_valid"]

        tree = provider._build_tree_from_graph("test", GraphWithMixedDeps(), set())
        assert tree.name == "test"
        # Should only include string deps
        child_names = [c.name for c in tree.children]
        assert "valid_dep" in child_names
        assert "another_valid" in child_names
        assert len(tree.children) == 2  # Only the two strings
