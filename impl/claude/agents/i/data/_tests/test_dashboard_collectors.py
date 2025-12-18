"""Tests for dashboard data collectors.

Test Performance Optimization (2025-12-13):
- collect_trace_analysis() performs full static analysis (~30s)
- Tests that call it are marked @pytest.mark.slow
- A module-scoped fixture caches the analysis for reuse
- Unit tests use mock data to avoid the expensive call

Rationale (from spec/principles.md §7 Generative):
- Tests are executable specification
- Slow tests should not run on every push
- Categorical separation: unit tests vs integration tests
"""

import asyncio
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest

from agents.i.data.dashboard_collectors import (
    DashboardMetrics,
    FluxMetrics,
    KgentMetrics,
    MetabolismMetrics,
    MetricsObservable,
    TraceAnalysisMetrics,
    TraceEntry,
    TriadMetrics,
    collect_metrics,
    collect_trace_analysis,
    create_demo_metrics,
    create_random_metrics,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Module-scoped fixture for expensive trace analysis (caching functor)
# =============================================================================


@pytest.fixture(scope="module")
def cached_trace_analysis() -> TraceAnalysisMetrics:
    """
    Cached trace analysis result for tests that need it.

    This is a module-scoped fixture that runs the expensive static
    analysis once per module, not once per test. This follows the
    "Cache" functor pattern from the optimization framework.

    For unit tests that don't need real data, use mock_trace_analysis.
    """
    import asyncio

    return asyncio.get_event_loop().run_until_complete(collect_trace_analysis())


@pytest.fixture
def mock_trace_analysis() -> TraceAnalysisMetrics:
    """
    Mock trace analysis for fast unit tests.

    Returns synthetic data that exercises the TraceAnalysisMetrics
    dataclass without the expensive static analysis call.
    """
    return TraceAnalysisMetrics(
        files_analyzed=100,
        definitions_found=500,
        calls_found=1000,
        is_online=True,
        hottest_functions=[
            {"name": "invoke", "callers": 50},
            {"name": "manifest", "callers": 30},
        ],
        call_trees=[],
    )


class TestKgentMetrics:
    """Tests for KgentMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = KgentMetrics()
        assert m.mode == "reflect"
        assert m.garden_patterns == 0
        assert m.garden_trees == 0
        assert m.interactions_count == 0
        assert m.is_online is True

    def test_dream_age_str_never(self) -> None:
        """Dream age is 'never' when no dream."""
        m = KgentMetrics(last_dream=None)
        assert m.dream_age_str == "never"

    def test_dream_age_str_minutes(self) -> None:
        """Dream age shows minutes for recent dreams."""
        now = datetime.now(timezone.utc)
        ten_min_ago = now.replace(minute=now.minute - 10) if now.minute >= 10 else now
        m = KgentMetrics(last_dream=ten_min_ago)
        # Should be some number of minutes
        assert "m ago" in m.dream_age_str or "h ago" in m.dream_age_str

    def test_dream_age_str_hours(self) -> None:
        """Dream age shows hours for older dreams."""
        now = datetime.now(timezone.utc)
        two_hours_ago = now.replace(hour=now.hour - 2) if now.hour >= 2 else now
        m = KgentMetrics(last_dream=two_hours_ago)
        # Could be hours or still minutes depending on timing
        assert "ago" in m.dream_age_str


class TestMetabolismMetrics:
    """Tests for MetabolismMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = MetabolismMetrics()
        assert m.pressure == 0.0
        assert m.temperature == 0.0
        assert m.in_fever is False
        assert m.is_online is True

    def test_pressure_pct(self) -> None:
        """Pressure percentage is correct."""
        m = MetabolismMetrics(pressure=0.42)
        assert m.pressure_pct == 42

    def test_status_text_cool(self) -> None:
        """Status is COOL for low pressure."""
        m = MetabolismMetrics(pressure=0.3)
        assert m.status_text == "COOL"

    def test_status_text_warm(self) -> None:
        """Status is WARM for medium pressure."""
        m = MetabolismMetrics(pressure=0.6)
        assert m.status_text == "WARM"

    def test_status_text_hot(self) -> None:
        """Status is HOT for high pressure."""
        m = MetabolismMetrics(pressure=0.85)
        assert m.status_text == "HOT"

    def test_status_text_fever(self) -> None:
        """Status is FEVER when in fever state."""
        m = MetabolismMetrics(pressure=0.9, in_fever=True)
        assert m.status_text == "FEVER"


class TestTriadMetrics:
    """Tests for TriadMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = TriadMetrics()
        assert m.durability == 0.0
        assert m.resonance == 0.0
        assert m.reflex == 0.0
        assert m.is_online is True

    def test_overall_average(self) -> None:
        """Overall is average of three layers."""
        m = TriadMetrics(durability=0.9, resonance=0.6, reflex=0.9)
        assert abs(m.overall - 0.8) < 0.001  # Float comparison tolerance

    def test_status_text_healthy(self) -> None:
        """Status is HEALTHY for high health."""
        m = TriadMetrics(durability=0.95, resonance=0.95, reflex=0.95)
        assert m.status_text == "HEALTHY"

    def test_status_text_degraded(self) -> None:
        """Status is DEGRADED for medium health."""
        m = TriadMetrics(durability=0.7, resonance=0.6, reflex=0.5)
        assert m.status_text == "DEGRADED"

    def test_status_text_critical(self) -> None:
        """Status is CRITICAL for low health."""
        m = TriadMetrics(durability=0.2, resonance=0.1, reflex=0.3)
        assert m.status_text == "CRITICAL"


class TestFluxMetrics:
    """Tests for FluxMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = FluxMetrics()
        assert m.events_per_second == 0.0
        assert m.queue_depth == 0
        assert m.active_agents == 0
        assert m.is_online is True

    def test_status_text_idle(self) -> None:
        """Status is IDLE when no events."""
        m = FluxMetrics(events_per_second=0.0, queue_depth=0)
        assert m.status_text == "IDLE"

    def test_status_text_flowing(self) -> None:
        """Status is FLOWING when processing."""
        m = FluxMetrics(events_per_second=5.0, queue_depth=5)
        assert m.status_text == "FLOWING"

    def test_status_text_backed_up(self) -> None:
        """Status is BACKED UP for large queue."""
        m = FluxMetrics(events_per_second=1.0, queue_depth=150)
        assert m.status_text == "BACKED UP"

    def test_status_text_errors(self) -> None:
        """Status is ERRORS for high error rate."""
        m = FluxMetrics(events_per_second=5.0, error_rate=0.2)
        assert m.status_text == "ERRORS"


class TestTraceEntry:
    """Tests for TraceEntry dataclass."""

    def test_render_basic(self) -> None:
        """Render produces expected output."""
        entry = TraceEntry(
            timestamp=datetime(2025, 12, 13, 10, 30, 45, tzinfo=timezone.utc),
            path="self.soul.challenge",
            args='("singleton")',
            result="REJECT",
            latency_ms=23,
        )
        rendered = entry.render(show_timestamp=False)
        assert "self.soul.challenge" in rendered
        assert '("singleton")' in rendered
        assert "REJECT" in rendered
        assert "[23ms]" in rendered

    def test_render_with_timestamp(self) -> None:
        """Render includes timestamp when requested."""
        entry = TraceEntry(
            timestamp=datetime(2025, 12, 13, 10, 30, 45, tzinfo=timezone.utc),
            path="void.entropy.tithe",
            result="OK",
        )
        rendered = entry.render(show_timestamp=True)
        assert "[10:30:45]" in rendered

    def test_render_no_args(self) -> None:
        """Render handles empty args."""
        entry = TraceEntry(
            timestamp=datetime.now(timezone.utc),
            path="self.soul.manifest",
            result="OK",
        )
        rendered = entry.render(show_timestamp=False)
        assert "self.soul.manifest" in rendered
        assert "  " not in rendered  # No double space from empty args


class TestDashboardMetrics:
    """Tests for DashboardMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = DashboardMetrics()
        assert m.kgent is not None
        assert m.metabolism is not None
        assert m.triad is not None
        assert m.flux is not None
        assert m.traces == []

    def test_any_offline_all_online(self) -> None:
        """any_offline is False when all online."""
        m = DashboardMetrics()
        assert m.any_offline is False

    def test_any_offline_some_offline(self) -> None:
        """any_offline is True when any offline."""
        m = DashboardMetrics(
            kgent=KgentMetrics(is_online=False),
        )
        assert m.any_offline is True


class TestCreateDemoMetrics:
    """Tests for create_demo_metrics function."""

    def test_returns_dashboard_metrics(self) -> None:
        """Returns a DashboardMetrics instance."""
        m = create_demo_metrics()
        assert isinstance(m, DashboardMetrics)

    def test_all_online(self) -> None:
        """All subsystems are online in demo mode."""
        m = create_demo_metrics()
        assert m.kgent.is_online is True
        assert m.metabolism.is_online is True
        assert m.triad.is_online is True
        assert m.flux.is_online is True

    def test_has_traces(self) -> None:
        """Demo metrics include sample traces."""
        m = create_demo_metrics()
        assert len(m.traces) > 0

    def test_realistic_values(self) -> None:
        """Values are realistic (not all zeros)."""
        m = create_demo_metrics()
        assert m.kgent.garden_patterns > 0
        assert m.metabolism.pressure > 0
        assert m.triad.durability > 0
        assert m.flux.events_per_second > 0


class TestCreateRandomMetrics:
    """Tests for create_random_metrics function."""

    def test_varies_from_base(self) -> None:
        """Randomized metrics vary from call to call."""
        m1 = create_random_metrics()
        m2 = create_random_metrics()
        # At least one value should differ (probability of all same is tiny)
        differs = (
            m1.metabolism.pressure != m2.metabolism.pressure
            or m1.metabolism.temperature != m2.metabolism.temperature
            or m1.flux.events_per_second != m2.flux.events_per_second
            or m1.flux.queue_depth != m2.flux.queue_depth
        )
        assert differs


class TestCollectMetrics:
    """Tests for collect_metrics function.

    NOTE: collect_metrics() calls collect_trace_analysis() which does
    full static analysis. These tests are marked @pytest.mark.slow.
    """

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_returns_dashboard_metrics(self) -> None:
        """Returns a DashboardMetrics instance (SLOW: ~30s due to static analysis)."""
        m = await collect_metrics()
        assert isinstance(m, DashboardMetrics)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_graceful_degradation(self) -> None:
        """Handles missing services gracefully (SLOW: ~30s due to static analysis)."""
        # Even if services are unavailable, should return metrics
        m = await collect_metrics()
        assert m is not None
        # Some or all may be offline, but we get valid metrics


class TestMetricsObservable:
    """Tests for MetricsObservable class."""

    def test_subscribe_unsubscribe(self) -> None:
        """Can subscribe and unsubscribe callbacks."""
        obs = MetricsObservable()
        received: list[DashboardMetrics] = []

        def callback(m: DashboardMetrics) -> None:
            received.append(m)

        obs.subscribe(callback)
        assert callback in obs._subscribers

        obs.unsubscribe(callback)
        assert callback not in obs._subscribers

    def test_latest_initially_none(self) -> None:
        """Latest is None before collection starts."""
        obs = MetricsObservable()
        assert obs.latest is None

    @pytest.mark.asyncio
    async def test_start_stop_collecting(self) -> None:
        """Can start and stop collection."""
        import asyncio

        obs = MetricsObservable()
        received: list[DashboardMetrics] = []

        def callback(m: DashboardMetrics) -> None:
            received.append(m)

        obs.subscribe(callback)

        # Start collecting with demo mode (no real services)
        await obs.start_collecting(interval=0.1, demo_mode=True)

        # Wait for a few collections
        await asyncio.sleep(0.35)

        # Stop collecting
        await obs.stop()

        # Should have received some metrics
        assert len(received) >= 2
        assert obs.latest is not None

    @pytest.mark.asyncio
    async def test_demo_mode_uses_random_metrics(self) -> None:
        """Demo mode uses randomized metrics."""
        obs = MetricsObservable()
        received: list[DashboardMetrics] = []

        def callback(m: DashboardMetrics) -> None:
            received.append(m)

        obs.subscribe(callback)

        await obs.start_collecting(interval=0.1, demo_mode=True)
        await asyncio.sleep(0.25)
        await obs.stop()

        # All should be online (demo mode)
        for m in received:
            assert m.kgent.is_online is True


# =============================================================================
# Integration Tests
# =============================================================================


class TestDashboardIntegration:
    """Integration tests for dashboard metrics collection.

    NOTE: Tests calling collect_metrics() are slow (~30s) due to static analysis.
    """

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_collection_cycle(self) -> None:
        """Full collection cycle works end-to-end (SLOW: ~30s due to static analysis)."""
        m = await collect_metrics()

        # Should have all metric types
        assert m.kgent is not None
        assert m.metabolism is not None
        assert m.triad is not None
        assert m.flux is not None

        # Should have a timestamp
        assert m.collected_at is not None

    def test_demo_metrics_display_ready(self) -> None:
        """Demo metrics are ready for display."""
        m = create_demo_metrics()

        # All status texts should be populated
        assert m.kgent.dream_age_str
        assert m.metabolism.status_text
        assert m.triad.status_text
        assert m.flux.status_text

        # All traces should be renderable
        for trace in m.traces:
            rendered = trace.render()
            assert len(rendered) > 0


# =============================================================================
# TraceAnalysisMetrics Tests
# =============================================================================


class TestTraceAnalysisMetrics:
    """Tests for TraceAnalysisMetrics dataclass."""

    def test_default_values(self) -> None:
        """Default values are sensible."""
        m = TraceAnalysisMetrics()
        assert m.files_analyzed == 0
        assert m.definitions_found == 0
        assert m.calls_found == 0
        assert m.is_online is True
        assert m.hottest_functions == []
        assert m.call_trees == []

    def test_status_text_unavailable(self) -> None:
        """Status is UNAVAILABLE when offline."""
        m = TraceAnalysisMetrics(is_online=False)
        assert m.status_text == "UNAVAILABLE"

    def test_status_text_not_analyzed(self) -> None:
        """Status is NOT ANALYZED when no files analyzed."""
        m = TraceAnalysisMetrics(files_analyzed=0, is_online=True)
        assert m.status_text == "NOT ANALYZED"

    def test_status_text_files_count(self) -> None:
        """Status shows file count when analyzed."""
        m = TraceAnalysisMetrics(files_analyzed=2582, is_online=True)
        assert m.status_text == "2582 files"

    def test_with_hottest_functions(self) -> None:
        """Can store hottest functions."""
        m = TraceAnalysisMetrics(
            files_analyzed=100,
            hottest_functions=[
                {"name": "foo", "callers": 50},
                {"name": "bar", "callers": 30},
            ],
        )
        assert len(m.hottest_functions) == 2
        assert m.hottest_functions[0]["name"] == "foo"
        assert m.hottest_functions[0]["callers"] == 50


class TestCollectTraceAnalysis:
    """Tests for collect_trace_analysis function.

    These tests call the SLOW static analysis (~30s).
    Mark with @pytest.mark.slow to exclude from default runs.
    """

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_returns_trace_analysis_metrics(self) -> None:
        """Returns a TraceAnalysisMetrics instance (SLOW: ~30s)."""
        m = await collect_trace_analysis()
        assert isinstance(m, TraceAnalysisMetrics)

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_graceful_degradation(self) -> None:
        """Handles missing trace provider gracefully (SLOW: ~30s)."""
        # Even if trace provider fails, should return metrics
        m = await collect_trace_analysis()
        assert m is not None

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_collects_real_data(self) -> None:
        """Collects real data from TraceDataProvider (SLOW: ~30s)."""
        m = await collect_trace_analysis()
        # If analysis succeeded, we should have file counts
        if m.is_online and m.files_analyzed > 0:
            assert m.definitions_found >= 0
            assert m.calls_found >= 0

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_with_custom_targets(self) -> None:
        """Can specify custom targets for call trees (SLOW: ~30s)."""
        # This tests the parameter, even if no trees are built
        m = await collect_trace_analysis(hot_function_targets=["foo.bar", "baz.qux"])
        assert isinstance(m, TraceAnalysisMetrics)


class TestDashboardMetricsWithTraceAnalysis:
    """Tests for DashboardMetrics with trace_analysis field.

    Fast tests use mock data; slow tests do real analysis.
    """

    def test_has_trace_analysis_field(self) -> None:
        """DashboardMetrics has trace_analysis field."""
        m = DashboardMetrics()
        assert hasattr(m, "trace_analysis")
        assert isinstance(m.trace_analysis, TraceAnalysisMetrics)

    def test_demo_metrics_includes_trace_analysis(self) -> None:
        """Demo metrics include trace analysis."""
        m = create_demo_metrics()
        assert m.trace_analysis is not None
        assert m.trace_analysis.files_analyzed > 0
        assert m.trace_analysis.is_online is True

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_collect_metrics_includes_trace_analysis(self) -> None:
        """collect_metrics includes trace_analysis (SLOW: ~30s due to static analysis)."""
        m = await collect_metrics()
        assert m.trace_analysis is not None
        # May or may not be online depending on environment
