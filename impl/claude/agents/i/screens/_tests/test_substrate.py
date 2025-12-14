"""
Tests for SubstrateScreen and its widgets.

Phase 6 integration tests for SubstrateScreen:
- Demo mode rendering
- Live mode with real substrate
- Widget rendering (AllocationMeter, GradientHeatmap, CompactionTimeline)
- Actions (refresh, compact, promotions)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest

from ..substrate import (
    AllocationMeterWidget,
    AllocationView,
    CompactionEventView,
    CompactionTimelineWidget,
    GradientHeatmapWidget,
    GradientView,
    SubstrateScreen,
    SubstrateSummaryWidget,
    create_substrate_screen,
)

# =============================================================================
# View Model Tests
# =============================================================================


class TestAllocationView:
    """Tests for AllocationView data model."""

    def test_create_allocation_view(self) -> None:
        """Should create AllocationView with required fields."""
        view = AllocationView(
            agent_id="kgent:working",
            human_label="K-gent working memory",
            pattern_count=100,
            max_patterns=500,
            usage_ratio=0.2,
            at_soft_limit=False,
        )
        assert view.agent_id == "kgent:working"
        assert view.usage_ratio == 0.2

    def test_allocation_view_with_last_access(self) -> None:
        """Should include optional last_access."""
        now = datetime.now()
        view = AllocationView(
            agent_id="test",
            human_label="Test",
            pattern_count=50,
            max_patterns=100,
            usage_ratio=0.5,
            at_soft_limit=False,
            last_access=now,
        )
        assert view.last_access == now

    def test_allocation_view_dedicated(self) -> None:
        """Should mark dedicated allocations."""
        view = AllocationView(
            agent_id="dgent",
            human_label="D-gent dedicated",
            pattern_count=1000,
            max_patterns=5000,
            usage_ratio=0.2,
            at_soft_limit=False,
            is_dedicated=True,
        )
        assert view.is_dedicated is True


class TestGradientView:
    """Tests for GradientView data model."""

    def test_create_gradient_view(self) -> None:
        """Should create GradientView with required fields."""
        view = GradientView(
            concept="soul.dialogue.reflect",
            agent_id="kgent",
            intensity=2.5,
            trace_count=10,
        )
        assert view.concept == "soul.dialogue.reflect"
        assert view.intensity == 2.5


class TestCompactionEventView:
    """Tests for CompactionEventView data model."""

    def test_create_compaction_event_view(self) -> None:
        """Should create CompactionEventView with required fields."""
        now = datetime.now()
        view = CompactionEventView(
            allocation_id="kgent:dream",
            patterns_before=200,
            patterns_after=160,
            strategy="uniform",
            timestamp=now,
        )
        assert view.allocation_id == "kgent:dream"
        assert view.patterns_before == 200
        assert view.patterns_after == 160


# =============================================================================
# Widget Rendering Tests
# =============================================================================


class TestAllocationMeterWidget:
    """Tests for AllocationMeterWidget rendering."""

    def test_render_idle_allocation(self) -> None:
        """Should render idle allocation with green bar."""
        allocation = AllocationView(
            agent_id="test",
            human_label="Test allocation",
            pattern_count=50,
            max_patterns=500,
            usage_ratio=0.1,
            at_soft_limit=False,
        )
        widget = AllocationMeterWidget(allocation)
        output = widget.render()

        assert "test" in output.lower()
        assert "Test allocation" in output
        assert "IDLE" in output

    def test_render_active_allocation(self) -> None:
        """Should render active allocation with appropriate status."""
        allocation = AllocationView(
            agent_id="kgent:working",
            human_label="K-gent working memory",
            pattern_count=300,
            max_patterns=500,
            usage_ratio=0.6,
            at_soft_limit=False,
        )
        widget = AllocationMeterWidget(allocation)
        output = widget.render()

        assert "kgent:working" in output
        assert "ACTIVE" in output

    def test_render_pressure_allocation(self) -> None:
        """Should render allocation at soft limit with pressure status."""
        allocation = AllocationView(
            agent_id="kgent:dialogue",
            human_label="K-gent dialogue",
            pattern_count=850,
            max_patterns=1000,
            usage_ratio=0.85,
            at_soft_limit=True,
        )
        widget = AllocationMeterWidget(allocation)
        output = widget.render()

        assert "PRESSURE" in output

    def test_render_dedicated_allocation(self) -> None:
        """Should render dedicated allocation with special status."""
        allocation = AllocationView(
            agent_id="dgent",
            human_label="D-gent dedicated",
            pattern_count=2000,
            max_patterns=10000,
            usage_ratio=0.2,
            at_soft_limit=False,
            is_dedicated=True,
        )
        widget = AllocationMeterWidget(allocation)
        output = widget.render()

        assert "DEDICATED" in output

    def test_render_with_last_access(self) -> None:
        """Should render last access time."""
        allocation = AllocationView(
            agent_id="test",
            human_label="Test",
            pattern_count=100,
            max_patterns=500,
            usage_ratio=0.2,
            at_soft_limit=False,
            last_access=datetime.now() - timedelta(seconds=30),
        )
        widget = AllocationMeterWidget(allocation)
        output = widget.render()

        assert "30s ago" in output or "29s ago" in output or "31s ago" in output


class TestGradientHeatmapWidget:
    """Tests for GradientHeatmapWidget rendering."""

    def test_render_empty_gradients(self) -> None:
        """Should render message for empty gradients."""
        widget = GradientHeatmapWidget([])
        output = widget.render()

        assert "No active gradients" in output

    def test_render_with_gradients(self) -> None:
        """Should render gradient heatmap."""
        gradients = [
            GradientView("soul.dialogue.reflect", "kgent", 2.5, 15),
            GradientView("code.python.debug", "bgent", 1.8, 10),
        ]
        widget = GradientHeatmapWidget(gradients)
        output = widget.render()

        assert "soul.dialogue" in output
        assert "kgent" in output
        assert "bgent" in output

    def test_render_sorts_by_intensity(self) -> None:
        """Should sort gradients by intensity descending."""
        gradients = [
            GradientView("low", "a", 0.5, 1),
            GradientView("high", "b", 5.0, 10),
            GradientView("medium", "c", 2.0, 5),
        ]
        widget = GradientHeatmapWidget(gradients)
        output = widget.render()

        # High should appear before low in the output
        high_pos = output.find("high")
        low_pos = output.find("low")
        assert high_pos < low_pos


class TestCompactionTimelineWidget:
    """Tests for CompactionTimelineWidget rendering."""

    def test_render_empty_events(self) -> None:
        """Should render message for no events."""
        widget = CompactionTimelineWidget([])
        output = widget.render()

        assert "No compaction events" in output

    def test_render_with_events(self) -> None:
        """Should render compaction timeline."""
        events = [
            CompactionEventView(
                allocation_id="kgent:dream",
                patterns_before=200,
                patterns_after=160,
                strategy="uniform",
                timestamp=datetime.now(),
            ),
        ]
        widget = CompactionTimelineWidget(events)
        output = widget.render()

        assert "kgent:dream" in output
        assert "200" in output
        assert "160" in output
        assert "uniform" in output


class TestSubstrateSummaryWidget:
    """Tests for SubstrateSummaryWidget rendering."""

    def test_render_summary(self) -> None:
        """Should render substrate summary."""
        stats = {
            "allocation_count": 4,
            "dedicated_count": 1,
            "total_patterns": 5000,
        }
        widget = SubstrateSummaryWidget(stats)
        output = widget.render()

        assert "4" in output
        assert "1" in output
        assert "5,000" in output or "5000" in output

    def test_render_empty_stats(self) -> None:
        """Should handle empty stats."""
        widget = SubstrateSummaryWidget({})
        output = widget.render()

        assert "0" in output


# =============================================================================
# SubstrateScreen Tests
# =============================================================================


class TestSubstrateScreen:
    """Tests for SubstrateScreen."""

    def test_create_demo_mode(self) -> None:
        """Should create screen in demo mode."""
        screen = create_substrate_screen(demo_mode=True)
        assert screen._demo_mode is True

    def test_create_with_substrate(self) -> None:
        """Should accept substrate parameter."""
        # We can't easily create a real substrate here without imports
        # but we can verify the parameter is accepted
        screen = SubstrateScreen(substrate=None, demo_mode=True)
        assert screen._substrate is None

    def test_screen_has_bindings(self) -> None:
        """Should have expected key bindings."""
        from textual.binding import Binding

        screen = create_substrate_screen(demo_mode=True)
        # BINDINGS can be Binding objects or tuples; extract keys uniformly
        binding_keys: list[str] = []
        for b in screen.BINDINGS:
            if isinstance(b, Binding):
                binding_keys.append(b.key)
            else:
                binding_keys.append(b[0])

        assert "escape" in binding_keys
        assert "r" in binding_keys
        assert "c" in binding_keys
        assert "p" in binding_keys


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_substrate_screen_demo(self) -> None:
        """Should create demo mode screen."""
        screen = create_substrate_screen(demo_mode=True)
        assert isinstance(screen, SubstrateScreen)
        assert screen._demo_mode is True

    def test_create_substrate_screen_live(self) -> None:
        """Should create live mode screen (fallback to demo without substrate)."""
        screen = create_substrate_screen(demo_mode=False, substrate=None)
        assert isinstance(screen, SubstrateScreen)
        # Without substrate, live mode falls back to demo data
