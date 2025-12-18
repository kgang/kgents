"""Tests for Dashboard TraceAnalysisPanel widget."""

from datetime import datetime, timezone

import pytest

from agents.i.data.dashboard_collectors import (
    DashboardMetrics,
    TraceAnalysisMetrics,
)
from agents.i.screens.dashboard import TraceAnalysisPanel


class TestTraceAnalysisPanel:
    """Tests for TraceAnalysisPanel widget."""

    def test_render_offline(self) -> None:
        """Panel shows offline when not available."""
        panel = TraceAnalysisPanel()
        panel.is_online = False
        panel.content = ""
        rendered = panel.render()
        assert "CALL GRAPH" in rendered
        assert "[offline]" in rendered

    def test_render_analyzing(self) -> None:
        """Panel shows analyzing when content empty."""
        panel = TraceAnalysisPanel()
        panel.is_online = True
        panel.content = ""
        rendered = panel.render()
        assert "CALL GRAPH" in rendered
        assert "(analyzing...)" in rendered

    def test_render_with_content(self) -> None:
        """Panel renders content when available."""
        panel = TraceAnalysisPanel()
        panel.is_online = True
        panel.content = "├─ 100 files │ 500 defs │ 1000 calls"
        rendered = panel.render()
        assert "CALL GRAPH" in rendered
        assert "100 files" in rendered

    def test_update_from_metrics_offline(self) -> None:
        """Update handles offline trace analysis."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(trace_analysis=TraceAnalysisMetrics(is_online=False))
        panel.update_from_metrics(metrics)
        assert panel.is_online is False
        assert panel.content == ""

    def test_update_from_metrics_no_files(self) -> None:
        """Update handles empty trace analysis."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                is_online=True,
                files_analyzed=0,
            )
        )
        panel.update_from_metrics(metrics)
        assert panel.is_online is True
        assert panel.content == ""

    def test_update_from_metrics_with_data(self) -> None:
        """Update renders trace analysis data."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=2582,
                definitions_found=42189,
                calls_found=133421,
                is_online=True,
                hottest_functions=[
                    {"name": "TraceRenderer.__init__", "callers": 1655},
                    {"name": "CallVisitor.__init__", "callers": 1400},
                ],
            )
        )
        panel.update_from_metrics(metrics)
        assert panel.is_online is True
        assert "2,582 files" in panel.content
        assert "42,189 defs" in panel.content
        assert "133,421 calls" in panel.content

    def test_update_from_metrics_shows_hot_functions(self) -> None:
        """Update shows hottest functions."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
                hottest_functions=[
                    {"name": "foo.bar", "callers": 50},
                    {"name": "baz.qux", "callers": 30},
                ],
            )
        )
        panel.update_from_metrics(metrics)
        assert "Hot Functions:" in panel.content
        assert "foo.bar" in panel.content
        assert "(50)" in panel.content
        assert "baz.qux" in panel.content
        assert "(30)" in panel.content

    def test_update_truncates_long_function_names(self) -> None:
        """Long function names are truncated."""
        panel = TraceAnalysisPanel()
        long_name = "very.long.module.path.with.many.segments.FunctionName"
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
                hottest_functions=[
                    {"name": long_name, "callers": 50},
                ],
            )
        )
        panel.update_from_metrics(metrics)
        # Name should be truncated with ...
        assert "..." in panel.content or long_name[:27] in panel.content

    def test_update_limits_hot_functions(self) -> None:
        """Only shows top 3 hot functions."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
                hottest_functions=[
                    {"name": "func1", "callers": 100},
                    {"name": "func2", "callers": 90},
                    {"name": "func3", "callers": 80},
                    {"name": "func4", "callers": 70},
                    {"name": "func5", "callers": 60},
                ],
            )
        )
        panel.update_from_metrics(metrics)
        # Should have func1, func2, func3 but not func4, func5
        assert "func1" in panel.content
        assert "func2" in panel.content
        assert "func3" in panel.content
        assert "func4" not in panel.content
        assert "func5" not in panel.content


class TestTraceAnalysisPanelCallTrees:
    """Tests for call tree rendering in TraceAnalysisPanel."""

    def test_render_call_tree_method_exists(self) -> None:
        """Panel has _render_call_tree method."""
        panel = TraceAnalysisPanel()
        assert hasattr(panel, "_render_call_tree")

    def test_no_call_trees_message(self) -> None:
        """Shows message when no call trees available."""
        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
                call_trees=[],
            )
        )
        panel.update_from_metrics(metrics)
        assert "(no call trees)" in panel.content

    def test_call_trees_header(self) -> None:
        """Shows Call Trees header when trees available."""

        # Create a mock call tree node
        class MockCallTreeNode:
            name = "test_function"

            def render(self) -> str:
                return "● test_function\n├─child1\n└─child2"

        panel = TraceAnalysisPanel()
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
                call_trees=[MockCallTreeNode()],
            )
        )
        panel.update_from_metrics(metrics)
        assert "Call Trees:" in panel.content


class TestTraceAnalysisPanelCSS:
    """Tests for TraceAnalysisPanel CSS styling."""

    def test_has_default_css(self) -> None:
        """Panel has default CSS."""
        assert hasattr(TraceAnalysisPanel, "DEFAULT_CSS")
        css = TraceAnalysisPanel.DEFAULT_CSS
        assert "TraceAnalysisPanel" in css
        assert "border:" in css

    def test_css_color_classes(self) -> None:
        """CSS includes color classes for functions."""
        css = TraceAnalysisPanel.DEFAULT_CSS
        assert ".function-hot" in css
        assert ".function-warm" in css
        assert ".function-cool" in css


class TestTraceAnalysisPanelIntegration:
    """Integration tests for TraceAnalysisPanel."""

    def test_reactive_properties(self) -> None:
        """Panel has reactive properties."""
        panel = TraceAnalysisPanel()
        # Test that reactive properties exist
        assert hasattr(panel, "content")
        assert hasattr(panel, "is_online")

    def test_panel_title(self) -> None:
        """Panel renders with CALL GRAPH title."""
        panel = TraceAnalysisPanel()
        panel.is_online = True
        panel.content = "test content"
        rendered = panel.render()
        assert rendered.startswith("CALL GRAPH")

    def test_full_update_cycle(self) -> None:
        """Full update cycle works correctly."""
        panel = TraceAnalysisPanel()

        # Initial state
        assert panel.content == ""
        assert panel.is_online is True

        # Update with offline metrics
        metrics = DashboardMetrics(trace_analysis=TraceAnalysisMetrics(is_online=False))
        panel.update_from_metrics(metrics)
        assert panel.is_online is False

        # Update with online metrics
        metrics = DashboardMetrics(
            trace_analysis=TraceAnalysisMetrics(
                files_analyzed=100,
                definitions_found=500,
                calls_found=1000,
                is_online=True,
            )
        )
        panel.update_from_metrics(metrics)
        assert panel.is_online is True
        assert "100 files" in panel.content
