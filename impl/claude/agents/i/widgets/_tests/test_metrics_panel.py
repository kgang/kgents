"""
Tests for MetricsPanel widget.

Verifies pressure/flow/temperature gauge rendering and reactive updates.
"""

import pytest

from agents.i.widgets.metrics_panel import (
    MetricsPanel,
    MetricState,
    MultiMetricsPanel,
    _gauge_bar,
    _sparkline,
)


class TestGaugeHelpers:
    """Test gauge rendering helpers."""

    def test_gauge_bar_empty(self) -> None:
        """Zero value renders empty bar."""
        bar = _gauge_bar(0, 100, width=10)
        assert bar == " " * 10

    def test_gauge_bar_full(self) -> None:
        """Full value renders full bar."""
        bar = _gauge_bar(100, 100, width=10)
        assert bar == "█" * 10

    def test_gauge_bar_half(self) -> None:
        """Half value renders half bar."""
        bar = _gauge_bar(50, 100, width=10)
        # Should have 5 full blocks
        assert bar.count("█") == 5

    def test_gauge_bar_partial_block(self) -> None:
        """Fractional values use partial blocks."""
        bar = _gauge_bar(55, 100, width=10)
        # Should have 5 full blocks + partial
        full_blocks = bar.count("█")
        assert full_blocks == 5
        # Rest should be space or partial block
        assert len(bar) == 10

    def test_gauge_bar_zero_max(self) -> None:
        """Zero max value returns empty bar."""
        bar = _gauge_bar(50, 0, width=10)
        assert bar == " " * 10

    def test_sparkline_empty(self) -> None:
        """Empty values renders baseline."""
        spark = _sparkline([], width=5)
        assert spark == "▁" * 5

    def test_sparkline_single_value(self) -> None:
        """Single value renders baseline."""
        spark = _sparkline([5.0], width=5)
        # Single value normalizes to top
        assert "▁" in spark

    def test_sparkline_range(self) -> None:
        """Range of values renders varying heights."""
        spark = _sparkline([0, 25, 50, 75, 100], width=5)
        assert len(spark) == 5
        # Should have increasing characters
        assert spark[0] == "▁"  # Min value
        assert spark[-1] == "█"  # Max value

    def test_sparkline_truncates_to_width(self) -> None:
        """Sparkline truncates to width."""
        values = [float(i) for i in range(20)]
        spark = _sparkline(values, width=10)
        assert len(spark) == 10


class TestMetricState:
    """Test MetricState tracking."""

    def test_initial_state(self) -> None:
        """Initial state is zero with empty history."""
        state = MetricState()
        assert state.current == 0.0
        assert state.history == []

    def test_update_adds_to_history(self) -> None:
        """Update adds value to history."""
        state = MetricState()
        state.update(10.0)
        state.update(20.0)

        assert state.current == 20.0
        assert state.history == [10.0, 20.0]

    def test_history_truncates(self) -> None:
        """History truncates to max size."""
        state = MetricState()

        for i in range(40):
            state.update(float(i), max_history=30)

        assert len(state.history) == 30
        assert state.history[0] == 10.0  # First 10 dropped


class TestMetricsPanel:
    """Test MetricsPanel widget."""

    def test_initial_values(self) -> None:
        """Panel initializes with zero metrics."""
        panel = MetricsPanel(agent_id="test-agent")

        assert panel.agent_id == "test-agent"
        assert panel.pressure == 0.0
        assert panel.flow == 0.0
        assert panel.temperature == 0.0
        assert panel.state == "unknown"

    def test_update_metrics(self) -> None:
        """update_metrics sets all values."""
        panel = MetricsPanel(agent_id="test")

        panel.update_metrics(
            pressure=50.0,
            flow=25.0,
            temperature=0.75,
            state="flowing",
        )

        assert panel.pressure == 50.0
        assert panel.flow == 25.0
        assert panel.temperature == 0.75
        assert panel.state == "flowing"

    def test_health_class_healthy(self) -> None:
        """Low pressure sets healthy class."""
        panel = MetricsPanel(agent_id="test")
        panel.update_metrics(pressure=30.0, flow=10.0, temperature=0.5)

        assert panel.has_class("healthy")
        assert not panel.has_class("degraded")
        assert not panel.has_class("critical")

    def test_health_class_degraded(self) -> None:
        """Medium pressure sets degraded class."""
        panel = MetricsPanel(agent_id="test")
        panel.update_metrics(pressure=60.0, flow=10.0, temperature=0.5)

        assert panel.has_class("degraded")
        assert not panel.has_class("healthy")
        assert not panel.has_class("critical")

    def test_health_class_critical(self) -> None:
        """High pressure sets critical class."""
        panel = MetricsPanel(agent_id="test")
        panel.update_metrics(pressure=90.0, flow=10.0, temperature=0.5)

        assert panel.has_class("critical")
        assert not panel.has_class("healthy")
        assert not panel.has_class("degraded")

    def test_fever_class(self) -> None:
        """High temperature sets fever class."""
        panel = MetricsPanel(agent_id="test")
        panel.update_metrics(pressure=30.0, flow=10.0, temperature=0.9)

        assert panel.has_class("fever")

    def test_name_defaults_to_id(self) -> None:
        """agent_name defaults to agent_id."""
        panel = MetricsPanel(agent_id="flux-123")
        assert panel.agent_name == "flux-123"

    def test_name_override(self) -> None:
        """agent_name can be overridden."""
        panel = MetricsPanel(agent_id="flux-123", agent_name="Grammar Agent")
        assert panel.agent_name == "Grammar Agent"


class TestMultiMetricsPanel:
    """Test MultiMetricsPanel widget."""

    def test_add_agent(self) -> None:
        """add_agent creates panel."""
        multi = MultiMetricsPanel()

        panel = multi.add_agent("agent-1", "Agent One")

        assert panel.agent_id == "agent-1"
        assert panel.agent_name == "Agent One"
        assert "agent-1" in multi.agent_ids

    def test_add_agent_idempotent(self) -> None:
        """add_agent returns existing panel."""
        multi = MultiMetricsPanel()

        panel1 = multi.add_agent("agent-1")
        panel2 = multi.add_agent("agent-1")

        assert panel1 is panel2

    def test_remove_agent(self) -> None:
        """remove_agent removes panel."""
        multi = MultiMetricsPanel()
        multi.add_agent("agent-1")

        result = multi.remove_agent("agent-1")

        assert result is True
        assert "agent-1" not in multi.agent_ids

    def test_remove_nonexistent(self) -> None:
        """remove_agent returns False for unknown agent."""
        multi = MultiMetricsPanel()

        result = multi.remove_agent("unknown")

        assert result is False

    def test_update_agent_metrics(self) -> None:
        """update_agent_metrics creates panel if needed."""
        multi = MultiMetricsPanel()

        multi.update_agent_metrics(
            agent_id="new-agent",
            pressure=50.0,
            flow=20.0,
            temperature=0.6,
        )

        assert "new-agent" in multi.agent_ids
        panel = multi._agent_panels["new-agent"]
        assert panel.pressure == 50.0
