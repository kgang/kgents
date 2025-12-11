"""
Tests for CortexDashboard (Instance DB Phase 6).

Tests dashboard rendering, sparklines, and wire protocol integration.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from agents.o.cortex_observer import (
    CortexObserver,
    create_mock_cortex_observer,
)
from agents.w.cortex_dashboard import (
    CortexDashboard,
    CortexDashboardConfig,
    DashboardPanel,
    SparklineData,
    create_cortex_dashboard,
    create_minimal_dashboard,
)


class TestDashboardPanel:
    """Tests for DashboardPanel enum."""

    def test_panel_values(self):
        """Test panel enum values."""
        assert DashboardPanel.HEMISPHERE_STATUS.value == "hemisphere_status"
        assert DashboardPanel.COHERENCY_MONITOR.value == "coherency_monitor"
        assert DashboardPanel.SYNAPSE_MONITOR.value == "synapse_monitor"


class TestSparklineData:
    """Tests for SparklineData."""

    def test_add_values(self):
        """Test adding values."""
        sparkline = SparklineData()
        sparkline.add(0.5)
        sparkline.add(0.7)

        assert len(sparkline.values) == 2
        assert sparkline.values[-1] == 0.7

    def test_max_size_limit(self):
        """Test max size limit."""
        sparkline = SparklineData(max_size=5)

        for i in range(10):
            sparkline.add(float(i))

        assert len(sparkline.values) == 5
        assert sparkline.values[0] == 5.0  # Oldest kept

    def test_render_empty(self):
        """Test rendering empty sparkline."""
        sparkline = SparklineData()
        result = sparkline.render(width=10)

        assert len(result) == 10
        assert result == " " * 10

    def test_render_with_values(self):
        """Test rendering sparkline with values."""
        sparkline = SparklineData()
        sparkline.add(0.0)
        sparkline.add(0.5)
        sparkline.add(1.0)

        result = sparkline.render(width=10)

        assert len(result) == 10
        # Should contain sparkline characters
        assert any(c in result for c in "▁▂▃▄▅▆▇█")

    def test_render_constant_values(self):
        """Test rendering with constant values."""
        sparkline = SparklineData()
        for _ in range(5):
            sparkline.add(0.5)

        result = sparkline.render(width=10)
        # All same value should render consistently
        assert len(result) == 10


class TestCortexDashboardConfig:
    """Tests for CortexDashboardConfig."""

    def test_defaults(self):
        """Test default configuration."""
        config = CortexDashboardConfig()

        assert config.wire_agent_name == "cortex-dashboard"
        assert config.emission_interval == 1.0
        assert len(config.panels) > 0
        assert config.compact_mode is False

    def test_from_dict(self):
        """Test creating config from dict."""
        config = CortexDashboardConfig.from_dict(
            {
                "wire_agent_name": "test-dashboard",
                "emission_interval": 2.0,
                "compact_mode": True,
            }
        )

        assert config.wire_agent_name == "test-dashboard"
        assert config.emission_interval == 2.0
        assert config.compact_mode is True

    def test_from_dict_with_panels(self):
        """Test creating config with panel list."""
        config = CortexDashboardConfig.from_dict(
            {
                "panels": ["hemisphere_status", "coherency_monitor"],
            }
        )

        assert len(config.panels) == 2
        assert DashboardPanel.HEMISPHERE_STATUS in config.panels


class TestCortexDashboard:
    """Tests for CortexDashboard."""

    def test_create_dashboard(self):
        """Test creating dashboard."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        assert dashboard._observer is observer
        assert dashboard._running is False

    def test_render_compact(self):
        """Test compact rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        compact = dashboard.render_compact()

        assert "[CORTEX]" in compact
        # When no components available, may just show status
        # When components available, sections separated by |

    def test_render_compact_includes_status(self):
        """Test compact includes health status."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        compact = dashboard.render_compact()

        # Should include one of these statuses
        statuses = ["HEALTHY", "DEGRADED", "CRITICAL", "UNKNOWN"]
        assert any(s in compact for s in statuses)

    def test_render_full(self):
        """Test full dashboard rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        full = dashboard.render_full()

        # Should have header
        assert "BICAMERAL CORTEX" in full
        # Should have section separators
        assert "==" in full

    def test_render_full_has_panels(self):
        """Test full dashboard has panels."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        full = dashboard.render_full()

        # Check for panel headers
        assert "Hemisphere Status" in full or "hemisphere" in full.lower()

    def test_get_wire_state(self):
        """Test wire state export."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        state = dashboard.get_wire_state()

        assert "status" in state
        assert "timestamp" in state or state.get("status") == "initializing"
        assert "compact" in state or state.get("status") == "initializing"

    def test_to_json(self):
        """Test JSON export."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        json_str = dashboard.to_json()
        data = json.loads(json_str)

        assert isinstance(data, dict)

    def test_sparkline_updates(self):
        """Test sparklines update with observations."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)

        # Trigger multiple updates
        for _ in range(5):
            dashboard._update()

        assert len(dashboard._surprise_sparkline.values) == 5
        assert len(dashboard._hippocampus_sparkline.values) == 5


class TestDashboardPanels:
    """Tests for individual dashboard panels."""

    def test_hemisphere_panel(self):
        """Test hemisphere panel rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)
        dashboard._update()

        from agents.o.cortex_observer import CortexHealthSnapshot

        snapshot = dashboard._last_snapshot

        lines = dashboard._render_hemisphere_panel(snapshot)

        assert len(lines) > 0
        assert any("Left" in line for line in lines)
        assert any("Right" in line for line in lines)

    def test_coherency_panel(self):
        """Test coherency panel rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)
        dashboard._update()

        snapshot = dashboard._last_snapshot
        lines = dashboard._render_coherency_panel(snapshot)

        assert len(lines) > 0
        assert any("Coherency" in line for line in lines)
        # Should have progress bar
        assert any("█" in line or "░" in line for line in lines)

    def test_synapse_panel(self):
        """Test synapse panel rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)
        dashboard._update()

        snapshot = dashboard._last_snapshot
        lines = dashboard._render_synapse_panel(snapshot)

        assert len(lines) > 0
        assert any("Synapse" in line for line in lines)

    def test_hippocampus_panel(self):
        """Test hippocampus panel rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)
        dashboard._update()

        snapshot = dashboard._last_snapshot
        lines = dashboard._render_hippocampus_panel(snapshot)

        assert len(lines) > 0
        assert any("Hippocampus" in line for line in lines)

    def test_dream_panel(self):
        """Test dream panel rendering."""
        observer = create_mock_cortex_observer()
        dashboard = CortexDashboard(observer)
        dashboard._update()

        snapshot = dashboard._last_snapshot
        lines = dashboard._render_dream_panel(snapshot)

        assert len(lines) > 0
        assert any("Dreamer" in line for line in lines)


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_cortex_dashboard(self):
        """Test factory function."""
        observer = create_mock_cortex_observer()
        dashboard = create_cortex_dashboard(observer)

        assert isinstance(dashboard, CortexDashboard)

    def test_create_cortex_dashboard_with_config(self):
        """Test factory with config."""
        observer = create_mock_cortex_observer()
        dashboard = create_cortex_dashboard(
            observer,
            config_dict={"emission_interval": 5.0},
        )

        assert dashboard._config.emission_interval == 5.0

    def test_create_minimal_dashboard(self):
        """Test minimal dashboard factory."""
        observer = create_mock_cortex_observer()
        dashboard = create_minimal_dashboard(observer)

        assert isinstance(dashboard, CortexDashboard)
        assert len(dashboard._config.panels) == 2
        assert dashboard._config.compact_mode is True
