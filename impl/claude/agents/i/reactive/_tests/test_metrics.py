"""Tests for reactive substrate metrics."""

import time

import pytest
from agents.i.reactive._metrics import (
    RenderTimer,
    get_error_count,
    get_metrics_summary,
    get_p95_duration,
    get_render_count,
    record_error,
    record_render,
    reset_metrics,
)


@pytest.fixture(autouse=True)
def clean_metrics():
    """Reset metrics before and after each test."""
    reset_metrics()
    yield
    reset_metrics()


class TestRecordRender:
    """Tests for record_render function."""

    def test_records_successful_render(self):
        """Should record a successful render."""
        record_render("TestWidget", "CLI", 0.001, success=True)

        summary = get_metrics_summary()
        assert summary["total_renders"] == 1
        assert summary["total_errors"] == 0
        assert summary["renders_by_widget"]["TestWidget"] == 1
        assert summary["renders_by_target"]["CLI"] == 1

    def test_records_failed_render(self):
        """Should record a failed render."""
        record_render("TestWidget", "CLI", 0.001, success=False)

        summary = get_metrics_summary()
        assert summary["total_renders"] == 1
        assert summary["total_errors"] == 1
        assert summary["error_rates_by_widget"]["TestWidget"] == 1.0

    def test_accumulates_duration(self):
        """Should accumulate total duration."""
        record_render("TestWidget", "CLI", 0.001)
        record_render("TestWidget", "CLI", 0.002)

        summary = get_metrics_summary()
        assert summary["total_duration_s"] == pytest.approx(0.003, rel=0.1)
        assert summary["avg_duration_s"] == pytest.approx(0.0015, rel=0.1)

    def test_tracks_multiple_widgets(self):
        """Should track renders for different widgets."""
        record_render("WidgetA", "CLI", 0.001)
        record_render("WidgetA", "CLI", 0.001)
        record_render("WidgetB", "TUI", 0.002)

        summary = get_metrics_summary()
        assert summary["renders_by_widget"]["WidgetA"] == 2
        assert summary["renders_by_widget"]["WidgetB"] == 1
        assert summary["renders_by_target"]["CLI"] == 2
        assert summary["renders_by_target"]["TUI"] == 1

    def test_tracks_multiple_targets(self):
        """Should track renders for different targets."""
        record_render("Widget", "CLI", 0.001)
        record_render("Widget", "TUI", 0.001)
        record_render("Widget", "JSON", 0.001)
        record_render("Widget", "MARIMO", 0.001)

        summary = get_metrics_summary()
        assert summary["renders_by_target"]["CLI"] == 1
        assert summary["renders_by_target"]["TUI"] == 1
        assert summary["renders_by_target"]["JSON"] == 1
        assert summary["renders_by_target"]["MARIMO"] == 1


class TestRecordError:
    """Tests for record_error function."""

    def test_records_error(self):
        """Should record an error without duration."""
        record_error("TestWidget", "CLI", "render_failed")

        summary = get_metrics_summary()
        assert summary["total_errors"] == 1
        assert summary["errors_by_widget"]["TestWidget"] == 1


class TestGetMetricsSummary:
    """Tests for get_metrics_summary function."""

    def test_empty_summary(self):
        """Should return zeros for empty metrics."""
        summary = get_metrics_summary()

        assert summary["total_renders"] == 0
        assert summary["total_errors"] == 0
        assert summary["error_rate"] == 0.0
        assert summary["avg_duration_s"] == 0.0

    def test_computes_error_rate(self):
        """Should compute error rate correctly."""
        record_render("Widget", "CLI", 0.001, success=True)
        record_render("Widget", "CLI", 0.001, success=False)
        record_render("Widget", "CLI", 0.001, success=True)
        record_render("Widget", "CLI", 0.001, success=False)

        summary = get_metrics_summary()
        assert summary["error_rate"] == 0.5  # 2 errors / 4 renders

    def test_top_widgets(self):
        """Should return top widgets by render count."""
        for _ in range(10):
            record_render("Popular", "CLI", 0.001)
        for _ in range(5):
            record_render("Medium", "CLI", 0.001)
        record_render("Rare", "CLI", 0.001)

        summary = get_metrics_summary()
        top = list(summary["top_widgets"].keys())
        assert top[0] == "Popular"
        assert top[1] == "Medium"
        assert top[2] == "Rare"


class TestP95Duration:
    """Tests for P95 duration tracking."""

    def test_computes_p95(self):
        """Should compute P95 duration correctly."""
        # Add 100 renders with durations 0.001 to 0.100
        for i in range(100):
            record_render("Widget", "CLI", (i + 1) * 0.001)

        p95 = get_p95_duration("Widget")
        # P95 of 1..100 is ~95
        assert p95 is not None
        assert p95 >= 0.095  # Should be around 0.095

    def test_p95_none_for_unknown_widget(self):
        """Should return None for unknown widget."""
        p95 = get_p95_duration("Unknown")
        assert p95 is None

    def test_p95_in_summary(self):
        """Should include P95 in summary."""
        for i in range(100):
            record_render("Widget", "CLI", (i + 1) * 0.001)

        summary = get_metrics_summary()
        assert "Widget" in summary["p95_duration_by_widget"]


class TestGetRenderCount:
    """Tests for get_render_count function."""

    def test_total_count(self):
        """Should return total count when no filter."""
        record_render("A", "CLI", 0.001)
        record_render("B", "TUI", 0.001)

        assert get_render_count() == 2

    def test_filter_by_widget(self):
        """Should filter by widget type."""
        record_render("A", "CLI", 0.001)
        record_render("A", "CLI", 0.001)
        record_render("B", "CLI", 0.001)

        assert get_render_count(widget_type="A") == 2
        assert get_render_count(widget_type="B") == 1

    def test_filter_by_target(self):
        """Should filter by target."""
        record_render("A", "CLI", 0.001)
        record_render("A", "TUI", 0.001)

        assert get_render_count(target="CLI") == 1
        assert get_render_count(target="TUI") == 1


class TestGetErrorCount:
    """Tests for get_error_count function."""

    def test_total_errors(self):
        """Should return total errors when no filter."""
        record_render("A", "CLI", 0.001, success=False)
        record_render("B", "CLI", 0.001, success=False)
        record_render("C", "CLI", 0.001, success=True)

        assert get_error_count() == 2

    def test_filter_by_widget(self):
        """Should filter by widget type."""
        record_render("A", "CLI", 0.001, success=False)
        record_render("A", "CLI", 0.001, success=False)
        record_render("B", "CLI", 0.001, success=False)

        assert get_error_count(widget_type="A") == 2
        assert get_error_count(widget_type="B") == 1


class TestResetMetrics:
    """Tests for reset_metrics function."""

    def test_clears_all_metrics(self):
        """Should clear all metrics."""
        record_render("Widget", "CLI", 0.001)
        record_render("Widget", "TUI", 0.001, success=False)

        reset_metrics()

        summary = get_metrics_summary()
        assert summary["total_renders"] == 0
        assert summary["total_errors"] == 0
        assert summary["renders_by_widget"] == {}
        assert summary["renders_by_target"] == {}


class TestRenderTimer:
    """Tests for RenderTimer context manager."""

    def test_records_successful_render(self):
        """Should record successful render on normal exit."""
        with RenderTimer("TestWidget", "CLI"):
            time.sleep(0.001)  # Small delay

        summary = get_metrics_summary()
        assert summary["total_renders"] == 1
        assert summary["total_errors"] == 0
        assert summary["total_duration_s"] >= 0.001

    def test_records_failed_render_on_exception(self):
        """Should record failed render when exception raised."""
        with pytest.raises(ValueError):
            with RenderTimer("TestWidget", "CLI"):
                raise ValueError("test error")

        summary = get_metrics_summary()
        assert summary["total_renders"] == 1
        assert summary["total_errors"] == 1

    def test_measures_duration(self):
        """Should measure actual duration."""
        with RenderTimer("TestWidget", "CLI"):
            time.sleep(0.01)

        summary = get_metrics_summary()
        assert summary["total_duration_s"] >= 0.01


class TestThreadSafety:
    """Tests for thread safety of metrics."""

    def test_concurrent_recording(self):
        """Should handle concurrent recording safely."""
        import threading

        def record_many():
            for _ in range(100):
                record_render("Widget", "CLI", 0.001)

        threads = [threading.Thread(target=record_many) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert get_render_count() == 1000
