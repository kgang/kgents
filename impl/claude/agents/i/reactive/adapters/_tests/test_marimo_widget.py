"""
Tests for MarimoAdapter - Wave 11 anywidget bridge.

Tests the Signal → Traitlets → JSON sync mechanism without requiring
the full anywidget stack (which needs Jupyter).
"""

from __future__ import annotations

import json

import pytest
from agents.i.reactive.adapters.marimo_widget import (
    MarimoAdapter,
    create_marimo_adapter,
    is_anywidget_available,
)
from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import KgentsWidget, RenderTarget

# ============================================================
# Basic Adapter Tests
# ============================================================


class TestMarimoAdapterCreation:
    """Test adapter creation and basic properties."""

    def test_create_adapter_from_agent_card(self):
        """Adapter can wrap AgentCardWidget."""
        card = AgentCardWidget(
            AgentCardState(
                agent_id="test-agent",
                name="Test Agent",
                phase="active",
            )
        )
        adapter = MarimoAdapter(card)

        assert adapter.kgents_widget is card

    def test_create_adapter_from_sparkline(self):
        """Adapter can wrap SparklineWidget."""
        sparkline = SparklineWidget(SparklineState(values=(0.2, 0.4, 0.6, 0.8)))
        adapter = MarimoAdapter(sparkline)

        assert adapter.kgents_widget is sparkline

    def test_create_adapter_from_bar(self):
        """Adapter can wrap BarWidget."""
        bar = BarWidget(BarState(value=0.75, width=10))
        adapter = MarimoAdapter(bar)

        assert adapter.kgents_widget is bar

    def test_factory_function(self):
        """create_marimo_adapter factory works."""
        card = AgentCardWidget(AgentCardState(name="Factory Test"))
        adapter = create_marimo_adapter(card)

        assert adapter.kgents_widget is card


class TestAnywidgetAvailability:
    """Test anywidget detection."""

    def test_is_anywidget_available_returns_bool(self):
        """is_anywidget_available returns a boolean."""
        result = is_anywidget_available()
        assert isinstance(result, bool)


# ============================================================
# State Sync Tests (when anywidget is available)
# ============================================================


@pytest.mark.skipif(
    not is_anywidget_available(),
    reason="anywidget not installed",
)
class TestStateSyncWithAnywidget:
    """Test state synchronization with anywidget installed."""

    def test_initial_state_sync(self):
        """Initial state is synced to traitlets."""
        card = AgentCardWidget(
            AgentCardState(
                agent_id="sync-test",
                name="Sync Test",
                phase="active",
                capability=0.75,
            )
        )
        adapter = MarimoAdapter(card)

        # Check traitlet values
        assert adapter._widget_type == "agent_card"
        assert adapter._widget_id == "sync-test"

        # Parse state JSON
        state = json.loads(adapter._state_json)
        assert state["name"] == "Sync Test"
        assert state["phase"] == "active"
        assert state["capability"] == 0.75

    def test_state_update_triggers_sync(self):
        """Signal updates trigger traitlet sync."""
        card = AgentCardWidget(AgentCardState(name="Update Test", phase="idle"))
        adapter = MarimoAdapter(card)

        # Initial state
        state1 = json.loads(adapter._state_json)
        assert state1["phase"] == "idle"

        # Update state via Signal
        card.state.set(AgentCardState(name="Update Test", phase="active"))

        # Check sync happened
        state2 = json.loads(adapter._state_json)
        assert state2["phase"] == "active"

    def test_sparkline_state_sync(self):
        """Sparkline state syncs correctly."""
        sparkline = SparklineWidget(SparklineState(values=(0.1, 0.3, 0.5, 0.7, 0.9)))
        adapter = MarimoAdapter(sparkline)

        state = json.loads(adapter._state_json)
        assert state["type"] == "sparkline"
        assert state["values"] == [0.1, 0.3, 0.5, 0.7, 0.9]

    def test_bar_state_sync(self):
        """Bar state syncs correctly."""
        bar = BarWidget(BarState(value=0.6, width=20, style="gradient"))
        adapter = MarimoAdapter(bar)

        state = json.loads(adapter._state_json)
        assert state["type"] == "bar"
        assert state["value"] == 0.6
        assert state["width"] == 20
        assert state["style"] == "gradient"

    def test_refresh_forces_sync(self):
        """refresh() forces state sync."""
        card = AgentCardWidget(AgentCardState(name="Refresh Test"))
        adapter = MarimoAdapter(card)

        # Manually modify widget state (bypassing Signal)
        # This simulates an edge case where state might be stale
        adapter.refresh()

        # Should not error
        state = json.loads(adapter._state_json)
        assert state["name"] == "Refresh Test"

    def test_close_unsubscribes(self):
        """close() unsubscribes from Signal."""
        card = AgentCardWidget(AgentCardState(name="Close Test"))
        adapter = MarimoAdapter(card)

        # Should have subscription
        assert adapter._unsubscribe is not None

        # Close
        adapter.close()

        # Subscription cleared
        assert adapter._unsubscribe is None


# ============================================================
# Fallback Tests (when anywidget is NOT available)
# ============================================================


class TestFallbackBehavior:
    """Test fallback behavior without anywidget."""

    def test_repr_html_fallback(self):
        """Fallback provides _repr_html_."""
        card = AgentCardWidget(AgentCardState(name="Fallback Test", phase="active"))
        adapter = MarimoAdapter(card)

        # Fallback should have _repr_html_ if not anywidget
        if not is_anywidget_available():
            html = adapter._repr_html_()
            assert "kgents-agent-card" in html
            assert "Fallback Test" in html


# ============================================================
# Widget Type Detection Tests
# ============================================================


class TestWidgetTypeDetection:
    """Test widget type is correctly detected."""

    @pytest.mark.skipif(
        not is_anywidget_available(),
        reason="anywidget not installed",
    )
    def test_agent_card_type(self):
        """AgentCardWidget reports agent_card type."""
        card = AgentCardWidget(AgentCardState())
        adapter = MarimoAdapter(card)
        assert adapter._widget_type == "agent_card"

    @pytest.mark.skipif(
        not is_anywidget_available(),
        reason="anywidget not installed",
    )
    def test_sparkline_type(self):
        """SparklineWidget reports sparkline type."""
        sparkline = SparklineWidget(SparklineState())
        adapter = MarimoAdapter(sparkline)
        assert adapter._widget_type == "sparkline"

    @pytest.mark.skipif(
        not is_anywidget_available(),
        reason="anywidget not installed",
    )
    def test_bar_type(self):
        """BarWidget reports bar type."""
        bar = BarWidget(BarState())
        adapter = MarimoAdapter(bar)
        assert adapter._widget_type == "bar"


# ============================================================
# JSON Serialization Edge Cases
# ============================================================


@pytest.mark.skipif(
    not is_anywidget_available(),
    reason="anywidget not installed",
)
class TestJsonSerialization:
    """Test JSON serialization handles edge cases."""

    def test_empty_activity(self):
        """Empty activity tuple serializes correctly."""
        card = AgentCardWidget(AgentCardState(activity=()))
        adapter = MarimoAdapter(card)

        state = json.loads(adapter._state_json)
        # activity is in children
        assert "children" in state

    def test_high_entropy(self):
        """High entropy includes distortion data."""
        card = AgentCardWidget(AgentCardState(entropy=0.5, seed=42, t=1000.0))
        adapter = MarimoAdapter(card)

        state = json.loads(adapter._state_json)
        assert "distortion" in state

    def test_all_phases(self):
        """All phases serialize correctly."""
        for phase in ["idle", "active", "waiting", "error", "complete", "thinking"]:
            card = AgentCardWidget(AgentCardState(phase=phase))
            adapter = MarimoAdapter(card)

            state = json.loads(adapter._state_json)
            assert state["phase"] == phase


# ============================================================
# ESM Loading Tests
# ============================================================


@pytest.mark.skipif(
    not is_anywidget_available(),
    reason="anywidget not installed",
)
class TestEsmLoading:
    """Test ESM module loading."""

    def test_esm_loaded(self):
        """ESM module is loaded into traitlet."""
        card = AgentCardWidget(AgentCardState())
        adapter = MarimoAdapter(card)

        # ESM should contain render function
        assert "function render" in adapter._esm
        assert "export default" in adapter._esm

    def test_css_loaded(self):
        """CSS is loaded into traitlet."""
        card = AgentCardWidget(AgentCardState())
        adapter = MarimoAdapter(card)

        # CSS should contain kgents classes
        assert ".kgents-" in adapter._css or adapter._css == ""
