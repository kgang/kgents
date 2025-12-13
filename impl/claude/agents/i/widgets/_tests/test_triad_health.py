"""
Tests for TriadHealthWidget.

TriadHealthWidget displays Database Triad health status including:
- Durability (PostgreSQL)
- Resonance (Qdrant)
- Reflex (Redis)
- CDC lag and coherency metrics
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from agents.i.widgets.triad_health import (
    CompactTriadHealth,
    MiniTriadHealth,
    TriadHealth,
    TriadHealthWidget,
)

# =============================================================================
# TriadHealth Data Tests
# =============================================================================


class TestTriadHealth:
    """Tests for TriadHealth dataclass."""

    def test_default_values(self) -> None:
        """Test default health values."""
        health = TriadHealth()

        assert health.durability == 0.0
        assert health.resonance == 0.0
        assert health.reflex == 0.0
        assert health.cdc_lag_ms == 0.0

    def test_overall_calculation(self) -> None:
        """Test overall health calculation."""
        health = TriadHealth(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
        )

        # Average of 0.9, 0.8, 0.7 = 0.8
        assert health.overall == pytest.approx(0.8, abs=0.01)

    def test_coherency_with_truth_perfect(self) -> None:
        """Test coherency at 0ms lag."""
        health = TriadHealth(cdc_lag_ms=0.0)
        assert health.coherency_with_truth == 1.0

    def test_coherency_with_truth_threshold(self) -> None:
        """Test coherency at threshold (5000ms)."""
        health = TriadHealth(cdc_lag_ms=5000.0)
        assert health.coherency_with_truth == 0.0

    def test_coherency_with_truth_partial(self) -> None:
        """Test coherency at partial lag."""
        health = TriadHealth(cdc_lag_ms=2500.0)
        assert health.coherency_with_truth == pytest.approx(0.5, abs=0.01)

    def test_coherency_with_truth_beyond_threshold(self) -> None:
        """Test coherency beyond threshold is clamped to 0."""
        health = TriadHealth(cdc_lag_ms=10000.0)
        assert health.coherency_with_truth == 0.0

    def test_status_text_healthy(self) -> None:
        """Test status text for healthy state."""
        health = TriadHealth(durability=0.95, resonance=0.95, reflex=0.95)
        assert health.status_text == "HEALTHY"

    def test_status_text_degraded(self) -> None:
        """Test status text for degraded state."""
        health = TriadHealth(durability=0.6, resonance=0.6, reflex=0.6)
        assert health.status_text == "DEGRADED"

    def test_status_text_critical(self) -> None:
        """Test status text for critical state."""
        health = TriadHealth(durability=0.2, resonance=0.2, reflex=0.2)
        assert health.status_text == "CRITICAL"


# =============================================================================
# TriadHealthWidget Tests
# =============================================================================


class TestTriadHealthWidget:
    """Tests for TriadHealthWidget."""

    def test_widget_creation(self) -> None:
        """Test creating a widget."""
        widget = TriadHealthWidget()

        assert widget.durability == 0.0
        assert widget.resonance == 0.0
        assert widget.reflex == 0.0

    def test_widget_with_health(self) -> None:
        """Test creating widget with initial health."""
        health = TriadHealth(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
        )
        widget = TriadHealthWidget(health=health)

        assert widget.durability == 0.9
        assert widget.resonance == 0.8
        assert widget.reflex == 0.7

    def test_update_health(self) -> None:
        """Test updating widget health."""
        widget = TriadHealthWidget()
        health = TriadHealth(
            durability=0.85,
            resonance=0.75,
            reflex=0.65,
        )

        widget.update_health(health)

        assert widget.durability == 0.85
        assert widget.resonance == 0.75
        assert widget.reflex == 0.65

    def test_render_includes_layers(self) -> None:
        """Test that render includes all layers."""
        widget = TriadHealthWidget()
        rendered = str(widget.render())

        # Should include all layer labels
        assert "D " in rendered  # Durability
        assert "R " in rendered  # Resonance
        assert "F " in rendered  # Reflex

    def test_render_includes_labels(self) -> None:
        """Test that render includes layer labels."""
        widget = TriadHealthWidget()
        rendered = str(widget.render())

        assert "PG" in rendered  # PostgreSQL
        assert "Qd" in rendered  # Qdrant
        assert "Rd" in rendered  # Redis

    def test_render_compact_mode(self) -> None:
        """Test compact rendering."""
        widget = TriadHealthWidget(compact=True)
        rendered = str(widget.render())

        # Compact mode should not include coherency/lag details
        assert "Coherency" not in rendered

    def test_render_with_title(self) -> None:
        """Test rendering with title."""
        widget = TriadHealthWidget(show_title=True)
        rendered = str(widget.render())

        assert "Triad Health" in rendered

    def test_render_without_title(self) -> None:
        """Test rendering without title."""
        widget = TriadHealthWidget(show_title=False)
        rendered = str(widget.render())

        assert "Triad Health" not in rendered

    def test_bar_width_configurable(self) -> None:
        """Test that bar width is configurable."""
        widget = TriadHealthWidget(bar_width=10)
        assert widget.bar_width == 10


class TestCompactTriadHealth:
    """Tests for CompactTriadHealth widget."""

    def test_widget_creation(self) -> None:
        """Test creating a compact widget."""
        widget = CompactTriadHealth()

        assert widget.durability == 0.0
        assert widget.resonance == 0.0
        assert widget.reflex == 0.0

    def test_render_format(self) -> None:
        """Test compact render format."""
        health = TriadHealth(
            durability=0.87,
            resonance=0.92,
            reflex=0.78,
            synapse_active=True,
        )
        widget = CompactTriadHealth(health=health)
        rendered = str(widget.render())

        assert "D:87%" in rendered
        assert "R:92%" in rendered
        assert "F:78%" in rendered
        assert "[●]" in rendered  # Synapse active

    def test_synapse_inactive_indicator(self) -> None:
        """Test synapse inactive indicator."""
        health = TriadHealth(synapse_active=False)
        widget = CompactTriadHealth(health=health)
        rendered = str(widget.render())

        assert "[○]" in rendered  # Synapse inactive


class TestMiniTriadHealth:
    """Tests for MiniTriadHealth widget."""

    def test_widget_creation(self) -> None:
        """Test creating a mini widget."""
        widget = MiniTriadHealth()
        assert widget.overall == 0.0

    def test_update_health(self) -> None:
        """Test updating mini widget health."""
        health = TriadHealth(
            durability=0.9,
            resonance=0.9,
            reflex=0.9,
        )
        widget = MiniTriadHealth()
        widget.update_health(health)

        assert widget.overall == pytest.approx(0.9, abs=0.01)

    def test_render_uses_block_chars(self) -> None:
        """Test that render uses block characters."""
        health = TriadHealth(
            durability=0.9,
            resonance=0.9,
            reflex=0.9,
        )
        widget = MiniTriadHealth(health=health)
        rendered = str(widget.render())

        # Should be 5 chars of block characters
        assert len(rendered) == 5
        for char in rendered:
            assert char in "░▒▓█"


# =============================================================================
# CSS Class Tests
# =============================================================================


class TestHealthClasses:
    """Tests for CSS class assignment based on health."""

    def test_compact_healthy_class(self) -> None:
        """Test healthy class assignment."""
        health = TriadHealth(
            durability=0.9,
            resonance=0.9,
            reflex=0.9,
        )
        widget = CompactTriadHealth(health=health)

        assert widget.has_class("healthy")

    def test_compact_degraded_class(self) -> None:
        """Test degraded class assignment."""
        health = TriadHealth(
            durability=0.6,
            resonance=0.6,
            reflex=0.6,
        )
        widget = CompactTriadHealth(health=health)

        assert widget.has_class("degraded")

    def test_compact_critical_class(self) -> None:
        """Test critical class assignment."""
        health = TriadHealth(
            durability=0.2,
            resonance=0.2,
            reflex=0.2,
        )
        widget = CompactTriadHealth(health=health)

        assert widget.has_class("critical")


# =============================================================================
# Integration with Database Triad
# =============================================================================


class TestTriadIntegration:
    """Tests for integration with Database Triad concepts."""

    def test_health_maps_to_triad_roles(self) -> None:
        """Test that health dimensions map to triad roles."""
        health = TriadHealth(
            durability=0.95,  # PostgreSQL - "Is truth safe?"
            resonance=0.85,  # Qdrant - "Is meaning accessible?"
            reflex=0.75,  # Redis - "Is it fast?"
        )

        # Durability is highest (source of truth is stable)
        assert health.durability > health.resonance > health.reflex

    def test_cdc_lag_affects_coherency(self) -> None:
        """Test that CDC lag affects coherency calculation."""
        low_lag = TriadHealth(cdc_lag_ms=100)
        high_lag = TriadHealth(cdc_lag_ms=3000)

        assert low_lag.coherency_with_truth > high_lag.coherency_with_truth

    def test_outbox_pending_tracking(self) -> None:
        """Test outbox pending count tracking."""
        health = TriadHealth(outbox_pending=42)
        widget = TriadHealthWidget(health=health)

        assert widget.outbox_pending == 42

    def test_synapse_active_tracking(self) -> None:
        """Test synapse active state tracking."""
        health_active = TriadHealth(synapse_active=True)
        health_inactive = TriadHealth(synapse_active=False)

        widget_active = TriadHealthWidget(health=health_active)
        widget_inactive = TriadHealthWidget(health=health_inactive)

        assert widget_active.synapse_active is True
        assert widget_inactive.synapse_active is False
