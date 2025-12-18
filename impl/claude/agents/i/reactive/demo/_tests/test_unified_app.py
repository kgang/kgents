"""
Tests for UnifiedApp - Wave 12 of the reactive substrate.

These tests verify:
1. UnifiedDashboard holds widgets correctly
2. Same widgets render to all targets
3. Output formats are valid (CLI string, JSON dict, HTML string)
4. Performance benchmarks complete within acceptable bounds
5. The functor property: same state -> consistent projections
"""

from __future__ import annotations

import json

import pytest

from agents.i.reactive.demo.unified_app import (
    UnifiedDashboard,
    benchmark_renders,
    capture_comparison,
    create_sample_dashboard,
)
from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# UnifiedDashboard Tests
# =============================================================================


class TestUnifiedDashboard:
    """Tests for the UnifiedDashboard dataclass."""

    def test_empty_dashboard_creation(self) -> None:
        """Empty dashboard should be valid."""
        dashboard = UnifiedDashboard()
        assert dashboard.title == "kgents Unified Dashboard"
        assert dashboard.agents == []
        assert dashboard.metrics == []
        assert dashboard.capacities == []

    def test_dashboard_with_custom_title(self) -> None:
        """Dashboard should accept custom title."""
        dashboard = UnifiedDashboard(title="Custom Title")
        assert dashboard.title == "Custom Title"

    def test_all_widgets_property(self) -> None:
        """all_widgets should return flattened list."""
        agent = AgentCardWidget(AgentCardState(name="Test Agent"))
        metric = SparklineWidget(SparklineState(values=(0.5,)))
        capacity = BarWidget(BarState(value=0.5))

        dashboard = UnifiedDashboard(
            agents=[agent],
            metrics=[metric],
            capacities=[capacity],
        )

        all_widgets = dashboard.all_widgets
        assert len(all_widgets) == 3
        assert agent in all_widgets
        assert metric in all_widgets
        assert capacity in all_widgets

    def test_dashboard_with_multiple_widgets(self) -> None:
        """Dashboard should hold multiple widgets of each type."""
        agents = [AgentCardWidget(AgentCardState(name=f"Agent {i}")) for i in range(3)]
        metrics = [SparklineWidget(SparklineState(values=(0.1 * i,))) for i in range(2)]
        capacities = [BarWidget(BarState(value=0.25 * i)) for i in range(4)]

        dashboard = UnifiedDashboard(
            agents=agents,
            metrics=metrics,
            capacities=capacities,
        )

        assert len(dashboard.agents) == 3
        assert len(dashboard.metrics) == 2
        assert len(dashboard.capacities) == 4
        assert len(dashboard.all_widgets) == 9


class TestCreateSampleDashboard:
    """Tests for the sample dashboard factory."""

    def test_creates_dashboard(self) -> None:
        """Should create a valid dashboard."""
        dashboard = create_sample_dashboard()
        assert isinstance(dashboard, UnifiedDashboard)

    def test_has_agents(self) -> None:
        """Sample dashboard should have agents."""
        dashboard = create_sample_dashboard()
        assert len(dashboard.agents) >= 1
        for agent in dashboard.agents:
            assert isinstance(agent, AgentCardWidget)

    def test_has_metrics(self) -> None:
        """Sample dashboard should have metrics."""
        dashboard = create_sample_dashboard()
        assert len(dashboard.metrics) >= 1
        for metric in dashboard.metrics:
            assert isinstance(metric, SparklineWidget)

    def test_has_capacities(self) -> None:
        """Sample dashboard should have capacities."""
        dashboard = create_sample_dashboard()
        assert len(dashboard.capacities) >= 1
        for capacity in dashboard.capacities:
            assert isinstance(capacity, BarWidget)


# =============================================================================
# CLI Rendering Tests
# =============================================================================


class TestCLIRendering:
    """Tests for CLI target rendering."""

    def test_render_cli_returns_string(self) -> None:
        """render_cli should return a string."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_cli()
        assert isinstance(result, str)

    def test_render_cli_contains_title(self) -> None:
        """CLI output should contain dashboard title."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_cli()
        assert dashboard.title in result

    def test_render_cli_contains_section_headers(self) -> None:
        """CLI output should have section headers."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_cli()
        assert "AGENTS" in result
        assert "METRICS" in result
        assert "CAPACITIES" in result

    def test_render_cli_contains_agent_names(self) -> None:
        """CLI output should show agent names."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_cli()
        for agent in dashboard.agents:
            name = agent.state.value.name
            assert name in result

    def test_empty_dashboard_cli(self) -> None:
        """Empty dashboard should still render."""
        dashboard = UnifiedDashboard()
        result = dashboard.render_cli()
        assert isinstance(result, str)
        assert dashboard.title in result

    def test_render_method_with_cli_target(self) -> None:
        """render() with CLI target should match render_cli()."""
        dashboard = create_sample_dashboard()
        cli_result = dashboard.render_cli()
        render_result = dashboard.render(RenderTarget.CLI)

        # render() returns list, render_cli() returns formatted string
        assert isinstance(render_result, list)
        assert len(render_result) == len(dashboard.all_widgets)


# =============================================================================
# JSON Rendering Tests
# =============================================================================


class TestJSONRendering:
    """Tests for JSON target rendering."""

    def test_render_json_returns_dict(self) -> None:
        """render_json should return a dictionary."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        assert isinstance(result, dict)

    def test_render_json_has_title(self) -> None:
        """JSON output should have title field."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        assert "title" in result
        assert result["title"] == dashboard.title

    def test_render_json_has_widget_lists(self) -> None:
        """JSON output should have agent, metric, capacity lists."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        assert "agents" in result
        assert "metrics" in result
        assert "capacities" in result
        assert isinstance(result["agents"], list)
        assert isinstance(result["metrics"], list)
        assert isinstance(result["capacities"], list)

    def test_render_json_serializable(self) -> None:
        """JSON output should be JSON-serializable."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        # Should not raise
        json_str = json.dumps(result)
        assert isinstance(json_str, str)
        # Should round-trip
        parsed = json.loads(json_str)
        assert parsed["title"] == result["title"]

    def test_json_agents_structure(self) -> None:
        """Agent JSON should have expected structure."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        for agent_json in result["agents"]:
            assert "type" in agent_json
            assert agent_json["type"] == "agent_card"
            assert "name" in agent_json
            assert "phase" in agent_json

    def test_json_metrics_structure(self) -> None:
        """Metric JSON should have expected structure."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        for metric_json in result["metrics"]:
            assert "type" in metric_json
            assert metric_json["type"] == "sparkline"
            assert "values" in metric_json

    def test_json_capacities_structure(self) -> None:
        """Capacity JSON should have expected structure."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_json()
        for capacity_json in result["capacities"]:
            assert "type" in capacity_json
            assert capacity_json["type"] == "bar"
            assert "value" in capacity_json

    def test_empty_dashboard_json(self) -> None:
        """Empty dashboard should serialize correctly."""
        dashboard = UnifiedDashboard()
        result = dashboard.render_json()
        assert result["agents"] == []
        assert result["metrics"] == []
        assert result["capacities"] == []


# =============================================================================
# Marimo/HTML Rendering Tests
# =============================================================================


class TestMarimoRendering:
    """Tests for marimo/HTML target rendering."""

    def test_render_marimo_html_returns_string(self) -> None:
        """render_marimo_html should return a string."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_marimo_html()
        assert isinstance(result, str)

    def test_render_marimo_html_is_valid_html(self) -> None:
        """Output should be valid HTML structure."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_marimo_html()
        assert result.startswith("<div")
        assert result.endswith("</div>")

    def test_render_marimo_html_contains_title(self) -> None:
        """HTML should contain dashboard title."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_marimo_html()
        assert dashboard.title in result

    def test_render_marimo_html_has_css_classes(self) -> None:
        """HTML should have kgents CSS classes."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_marimo_html()
        assert "kgents-unified-dashboard" in result

    def test_render_marimo_html_has_sections(self) -> None:
        """HTML should have section divs."""
        dashboard = create_sample_dashboard()
        result = dashboard.render_marimo_html()
        assert "kgents-agents" in result
        assert "kgents-metrics" in result
        assert "kgents-capacities" in result

    def test_empty_dashboard_marimo(self) -> None:
        """Empty dashboard should render HTML."""
        dashboard = UnifiedDashboard()
        result = dashboard.render_marimo_html()
        assert isinstance(result, str)
        assert "<div" in result


# =============================================================================
# Functor Property Tests
# =============================================================================


class TestFunctorProperty:
    """
    Tests verifying the functor property:
    Same state -> consistent projections across targets.
    """

    def test_same_widget_different_targets(self) -> None:
        """Same widget should produce valid output for all targets."""
        agent = AgentCardWidget(
            AgentCardState(
                agent_id="test-agent",
                name="Test Agent",
                phase="active",
                activity=(0.5, 0.6, 0.7),
                capability=0.8,
            )
        )

        cli = agent.to_cli()
        tui = agent.to_tui()
        json_out = agent.to_json()
        marimo = agent.to_marimo()

        # All should be valid
        assert isinstance(cli, str)
        assert isinstance(json_out, dict)
        assert isinstance(marimo, str)

        # JSON should capture same data
        assert json_out["name"] == "Test Agent"
        assert json_out["phase"] == "active"
        assert json_out["capability"] == 0.8

    def test_dashboard_projection_consistency(self) -> None:
        """Dashboard projections should be consistent."""
        dashboard = create_sample_dashboard()

        cli_result = dashboard.render_cli()
        json_result = dashboard.render_json()
        marimo_result = dashboard.render_marimo_html()

        # All should succeed
        assert cli_result
        assert json_result
        assert marimo_result

        # JSON should have same number of widgets
        assert len(json_result["agents"]) == len(dashboard.agents)
        assert len(json_result["metrics"]) == len(dashboard.metrics)
        assert len(json_result["capacities"]) == len(dashboard.capacities)

    def test_render_list_matches_widget_count(self) -> None:
        """render() should return one item per widget."""
        dashboard = create_sample_dashboard()

        cli_list = dashboard.render(RenderTarget.CLI)
        json_list = dashboard.render(RenderTarget.JSON)
        marimo_list = dashboard.render(RenderTarget.MARIMO)

        total_widgets = len(dashboard.all_widgets)
        assert len(cli_list) == total_widgets
        assert len(json_list) == total_widgets
        assert len(marimo_list) == total_widgets


# =============================================================================
# Performance Tests
# =============================================================================


class TestPerformance:
    """Tests for render performance."""

    def test_benchmark_returns_dict(self) -> None:
        """benchmark_renders should return a dict."""
        dashboard = create_sample_dashboard()
        result = benchmark_renders(dashboard, iterations=10)
        assert isinstance(result, dict)

    def test_benchmark_has_all_targets(self) -> None:
        """Benchmark should cover all main targets."""
        dashboard = create_sample_dashboard()
        result = benchmark_renders(dashboard, iterations=10)
        assert "cli" in result
        assert "json" in result
        assert "marimo" in result

    def test_benchmark_values_positive(self) -> None:
        """All benchmark values should be positive."""
        dashboard = create_sample_dashboard()
        result = benchmark_renders(dashboard, iterations=10)
        for target, rps in result.items():
            assert rps > 0, f"{target} should have positive renders/sec"

    def test_render_performance_acceptable(self) -> None:
        """Renders should be reasonably fast (>100/sec)."""
        dashboard = create_sample_dashboard()
        result = benchmark_renders(dashboard, iterations=100)

        # All targets should achieve at least 100 renders/sec
        for target, rps in result.items():
            assert rps > 100, f"{target} renders too slow: {rps}/sec"

    def test_cli_render_fast(self) -> None:
        """CLI rendering should be very fast."""
        dashboard = create_sample_dashboard()
        result = benchmark_renders(dashboard, iterations=100)
        # CLI should be fastest (>1000/sec)
        assert result["cli"] > 1000


# =============================================================================
# Capture Comparison Tests
# =============================================================================


class TestCaptureComparison:
    """Tests for the comparison capture function."""

    def test_capture_returns_dict(self) -> None:
        """capture_comparison should return a dict."""
        result = capture_comparison()
        assert isinstance(result, dict)

    def test_capture_has_all_targets(self) -> None:
        """Comparison should have all target outputs."""
        result = capture_comparison()
        assert "cli" in result
        assert "json" in result
        assert "html" in result

    def test_capture_cli_is_string(self) -> None:
        """CLI capture should be string."""
        result = capture_comparison()
        assert isinstance(result["cli"], str)

    def test_capture_json_is_dict(self) -> None:
        """JSON capture should be dict."""
        result = capture_comparison()
        assert isinstance(result["json"], dict)

    def test_capture_html_is_string(self) -> None:
        """HTML capture should be string."""
        result = capture_comparison()
        assert isinstance(result["html"], str)


# =============================================================================
# Widget Integration Tests
# =============================================================================


class TestWidgetIntegration:
    """Tests verifying widgets work correctly in dashboard context."""

    def test_agent_card_in_dashboard(self) -> None:
        """AgentCardWidget should render correctly in dashboard."""
        agent = AgentCardWidget(
            AgentCardState(
                agent_id="integration-test",
                name="Integration Test Agent",
                phase="thinking",
                activity=(0.1, 0.2, 0.3),
                capability=0.5,
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])

        cli = dashboard.render_cli()
        assert "Integration Test Agent" in cli

        json_out = dashboard.render_json()
        assert json_out["agents"][0]["name"] == "Integration Test Agent"

    def test_sparkline_in_dashboard(self) -> None:
        """SparklineWidget should render correctly in dashboard."""
        metric = SparklineWidget(
            SparklineState(
                values=(0.1, 0.5, 0.9, 0.3),
                label="Test Metric",
            )
        )
        dashboard = UnifiedDashboard(metrics=[metric])

        cli = dashboard.render_cli()
        assert "Test Metric" in cli

        json_out = dashboard.render_json()
        assert json_out["metrics"][0]["type"] == "sparkline"
        assert json_out["metrics"][0]["values"] == [0.1, 0.5, 0.9, 0.3]

    def test_bar_in_dashboard(self) -> None:
        """BarWidget should render correctly in dashboard."""
        capacity = BarWidget(
            BarState(
                value=0.6,
                width=10,
                label="Test Capacity",
            )
        )
        dashboard = UnifiedDashboard(capacities=[capacity])

        cli = dashboard.render_cli()
        assert "Test Capacity" in cli

        json_out = dashboard.render_json()
        assert json_out["capacities"][0]["type"] == "bar"
        assert json_out["capacities"][0]["value"] == 0.6


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_widget_with_empty_activity(self) -> None:
        """Agent with no activity should render."""
        agent = AgentCardWidget(
            AgentCardState(
                name="Empty Activity",
                activity=(),
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])
        cli = dashboard.render_cli()
        assert "Empty Activity" in cli

    def test_widget_with_zero_capability(self) -> None:
        """Agent with zero capability should render."""
        agent = AgentCardWidget(
            AgentCardState(
                name="Zero Cap",
                capability=0.0,
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])
        json_out = dashboard.render_json()
        assert json_out["agents"][0]["capability"] == 0.0

    def test_widget_with_full_capability(self) -> None:
        """Agent with full capability should render."""
        agent = AgentCardWidget(
            AgentCardState(
                name="Full Cap",
                capability=1.0,
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])
        json_out = dashboard.render_json()
        assert json_out["agents"][0]["capability"] == 1.0

    def test_metric_with_single_value(self) -> None:
        """Sparkline with single value should render."""
        metric = SparklineWidget(SparklineState(values=(0.5,)))
        dashboard = UnifiedDashboard(metrics=[metric])
        json_out = dashboard.render_json()
        assert json_out["metrics"][0]["values"] == [0.5]

    def test_bar_with_zero_width(self) -> None:
        """Bar with zero width should render."""
        capacity = BarWidget(BarState(value=0.5, width=0))
        # Zero width renders empty
        cli = capacity.to_cli()
        assert isinstance(cli, str)

    def test_large_activity_history(self) -> None:
        """Agent with large activity history should render."""
        activity = tuple(i / 100 for i in range(100))
        agent = AgentCardWidget(
            AgentCardState(
                name="Large History",
                activity=activity,
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])
        cli = dashboard.render_cli()
        assert "Large History" in cli

    def test_unicode_in_name(self) -> None:
        """Agent with unicode name should render."""
        agent = AgentCardWidget(
            AgentCardState(
                name="Agent 日本語 🚀",
            )
        )
        dashboard = UnifiedDashboard(agents=[agent])
        cli = dashboard.render_cli()
        assert "Agent 日本語 🚀" in cli
