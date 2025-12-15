"""
Tests for layout presets module.

Tests verify:
1. metric_row() creates HStack with correct gap
2. metric_stack() creates VStack with correct gap
3. panel() creates header/body VStack
4. labeled() creates label + widget HStack
5. status_row() creates standard agent status
6. Empty inputs handled gracefully
7. All render targets supported
"""

from __future__ import annotations

import pytest
from agents.i.reactive.composable import HStack, VStack
from agents.i.reactive.presets import (
    labeled,
    metric_row,
    metric_stack,
    panel,
    status_row,
)
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# metric_row() Tests
# =============================================================================


class TestMetricRow:
    """Test metric_row() preset function."""

    def test_empty_returns_hstack(self) -> None:
        """Empty metric_row returns empty HStack."""
        result = metric_row()
        assert isinstance(result, HStack)
        assert len(result.children) == 0

    def test_single_widget(self) -> None:
        """Single widget in metric_row."""
        bar = BarWidget(BarState(value=0.5))
        result = metric_row(bar)

        assert isinstance(result, HStack)
        assert len(result.children) == 1
        assert result.children[0] is bar

    def test_multiple_widgets(self) -> None:
        """Multiple widgets in metric_row."""
        bar1 = BarWidget(BarState(value=0.3, label="A"))
        bar2 = BarWidget(BarState(value=0.6, label="B"))
        bar3 = BarWidget(BarState(value=0.9, label="C"))

        result = metric_row(bar1, bar2, bar3)

        assert isinstance(result, HStack)
        assert len(result.children) == 3
        assert result.children[0] is bar1
        assert result.children[1] is bar2
        assert result.children[2] is bar3

    def test_custom_gap(self) -> None:
        """metric_row with custom gap."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.5))

        result = metric_row(bar1, bar2, gap=5)

        assert result.gap == 5

    def test_default_gap(self) -> None:
        """metric_row has default gap of 2."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.5))

        result = metric_row(bar1, bar2)

        assert result.gap == 2

    def test_with_separator(self) -> None:
        """metric_row with separator."""
        g1 = GlyphWidget(GlyphState(char="A"))
        g2 = GlyphWidget(GlyphState(char="B"))

        result = metric_row(g1, g2, separator=" | ")

        assert result.separator == " | "
        cli = result.project(RenderTarget.CLI)
        assert " | " in cli

    def test_cli_projection(self) -> None:
        """metric_row projects to CLI."""
        bar1 = BarWidget(BarState(value=0.5, width=5, label="X"))
        bar2 = BarWidget(BarState(value=0.8, width=5, label="Y"))

        result = metric_row(bar1, bar2)
        cli = result.project(RenderTarget.CLI)

        assert "X:" in cli
        assert "Y:" in cli

    def test_json_projection(self) -> None:
        """metric_row projects to JSON."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.8))

        result = metric_row(bar1, bar2)
        json_out = result.project(RenderTarget.JSON)

        assert json_out["type"] == "hstack"
        assert len(json_out["children"]) == 2

    def test_marimo_projection(self) -> None:
        """metric_row projects to MARIMO."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.8))

        result = metric_row(bar1, bar2)
        html = result.project(RenderTarget.MARIMO)

        assert "kgents-hstack" in html
        assert "inline-flex" in html


# =============================================================================
# metric_stack() Tests
# =============================================================================


class TestMetricStack:
    """Test metric_stack() preset function."""

    def test_empty_returns_vstack(self) -> None:
        """Empty metric_stack returns empty VStack."""
        result = metric_stack()
        assert isinstance(result, VStack)
        assert len(result.children) == 0

    def test_single_widget(self) -> None:
        """Single widget in metric_stack."""
        bar = BarWidget(BarState(value=0.5))
        result = metric_stack(bar)

        assert isinstance(result, VStack)
        assert len(result.children) == 1
        assert result.children[0] is bar

    def test_multiple_widgets(self) -> None:
        """Multiple widgets in metric_stack."""
        bar1 = BarWidget(BarState(value=0.3, label="A"))
        bar2 = BarWidget(BarState(value=0.6, label="B"))
        bar3 = BarWidget(BarState(value=0.9, label="C"))

        result = metric_stack(bar1, bar2, bar3)

        assert isinstance(result, VStack)
        assert len(result.children) == 3

    def test_custom_gap(self) -> None:
        """metric_stack with custom gap."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.5))

        result = metric_stack(bar1, bar2, gap=2)

        assert result.gap == 2

    def test_default_gap(self) -> None:
        """metric_stack has default gap of 0."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.5))

        result = metric_stack(bar1, bar2)

        assert result.gap == 0

    def test_with_separator(self) -> None:
        """metric_stack with separator."""
        g1 = GlyphWidget(GlyphState(char="A"))
        g2 = GlyphWidget(GlyphState(char="B"))

        result = metric_stack(g1, g2, separator="---")

        assert result.separator == "---"
        cli = result.project(RenderTarget.CLI)
        assert "---" in cli

    def test_cli_projection(self) -> None:
        """metric_stack projects to CLI with newlines."""
        bar1 = BarWidget(BarState(value=0.5, width=5, label="X"))
        bar2 = BarWidget(BarState(value=0.8, width=5, label="Y"))

        result = metric_stack(bar1, bar2)
        cli = result.project(RenderTarget.CLI)

        assert "\n" in cli
        assert "X:" in cli
        assert "Y:" in cli

    def test_json_projection(self) -> None:
        """metric_stack projects to JSON."""
        bar1 = BarWidget(BarState(value=0.5))
        bar2 = BarWidget(BarState(value=0.8))

        result = metric_stack(bar1, bar2)
        json_out = result.project(RenderTarget.JSON)

        assert json_out["type"] == "vstack"
        assert len(json_out["children"]) == 2


# =============================================================================
# panel() Tests
# =============================================================================


class TestPanel:
    """Test panel() preset function."""

    def test_creates_vstack(self) -> None:
        """panel creates VStack with header and body."""
        header = GlyphWidget(GlyphState(char="Title"))
        body = BarWidget(BarState(value=0.75))

        result = panel(header, body)

        assert isinstance(result, VStack)
        assert len(result.children) == 2
        assert result.children[0] is header
        assert result.children[1] is body

    def test_with_gap(self) -> None:
        """panel with gap between header and body."""
        header = GlyphWidget(GlyphState(char="Title"))
        body = BarWidget(BarState(value=0.75))

        result = panel(header, body, gap=1)

        assert result.gap == 1

    def test_cli_projection(self) -> None:
        """panel projects to CLI."""
        header = GlyphWidget(GlyphState(char="=== Status ==="))
        body = BarWidget(BarState(value=0.75, width=10))

        result = panel(header, body)
        cli = result.project(RenderTarget.CLI)

        assert "===" in cli
        assert "\n" in cli

    def test_with_composite_body(self) -> None:
        """panel with composite body (metric_row)."""
        header = GlyphWidget(GlyphState(char="Metrics"))
        body = metric_row(
            BarWidget(BarState(value=0.5)),
            BarWidget(BarState(value=0.8)),
        )

        result = panel(header, body)

        assert isinstance(result, VStack)
        assert isinstance(result.children[1], HStack)


# =============================================================================
# labeled() Tests
# =============================================================================


class TestLabeled:
    """Test labeled() preset function."""

    def test_creates_hstack(self) -> None:
        """labeled creates HStack with glyph and widget."""
        bar = BarWidget(BarState(value=0.75))
        result = labeled("CPU:", bar)

        assert isinstance(result, HStack)
        assert len(result.children) == 2
        # First child is label glyph
        assert isinstance(result.children[0], GlyphWidget)
        # Second child is the widget
        assert result.children[1] is bar

    def test_cli_projection(self) -> None:
        """labeled projects to CLI."""
        bar = BarWidget(BarState(value=0.75, width=5))
        result = labeled("Load:", bar)
        cli = result.project(RenderTarget.CLI)

        assert "Load:" in cli

    def test_custom_separator(self) -> None:
        """labeled with custom separator."""
        bar = BarWidget(BarState(value=0.75, width=5))
        result = labeled("Load", bar, separator=": ")
        cli = result.project(RenderTarget.CLI)

        assert "Load" in cli

    def test_empty_label(self) -> None:
        """labeled with empty string label."""
        bar = BarWidget(BarState(value=0.75))
        result = labeled("", bar)

        assert isinstance(result, HStack)
        assert len(result.children) == 2

    def test_with_sparkline(self) -> None:
        """labeled with sparkline widget."""
        spark = SparklineWidget(SparklineState(values=(0.2, 0.5, 0.8)))
        result = labeled("Trend:", spark)
        cli = result.project(RenderTarget.CLI)

        assert "Trend:" in cli


# =============================================================================
# status_row() Tests
# =============================================================================


class TestStatusRow:
    """Test status_row() preset function."""

    def test_creates_hstack(self) -> None:
        """status_row creates HStack with status elements."""
        result = status_row("SENSE", "Analyzing...", 0.85)

        assert isinstance(result, HStack)
        # Should have: phase symbol, phase name, activity, health bar
        assert len(result.children) == 4

    def test_phase_symbols(self) -> None:
        """status_row uses correct phase symbols."""
        sense = status_row("SENSE", "Working", 0.5)
        act = status_row("ACT", "Working", 0.5)
        reflect = status_row("REFLECT", "Working", 0.5)

        # Check CLI output contains symbols
        sense_cli = sense.project(RenderTarget.CLI)
        act_cli = act.project(RenderTarget.CLI)
        reflect_cli = reflect.project(RenderTarget.CLI)

        assert "◉" in sense_cli  # SENSE symbol
        assert "▶" in act_cli  # ACT symbol
        assert "◐" in reflect_cli  # REFLECT symbol

    def test_health_clamped(self) -> None:
        """status_row clamps health to 0.0-1.0."""
        high = status_row("ACT", "Test", 1.5)
        low = status_row("ACT", "Test", -0.5)

        # Should not raise, health clamped internally
        assert isinstance(high, HStack)
        assert isinstance(low, HStack)

    def test_cli_projection(self) -> None:
        """status_row projects to CLI."""
        result = status_row("SENSE", "Analyzing data...", 0.75)
        cli = result.project(RenderTarget.CLI)

        assert "SENSE" in cli
        assert "Analyzing data..." in cli

    def test_json_projection(self) -> None:
        """status_row projects to JSON."""
        result = status_row("ACT", "Processing", 0.5)
        json_out = result.project(RenderTarget.JSON)

        assert json_out["type"] == "hstack"
        assert len(json_out["children"]) == 4

    def test_marimo_projection(self) -> None:
        """status_row projects to MARIMO."""
        result = status_row("REFLECT", "Thinking...", 0.9)
        html = result.project(RenderTarget.MARIMO)

        assert "kgents-hstack" in html

    def test_unknown_phase(self) -> None:
        """status_row handles unknown phase with default symbol."""
        result = status_row("UNKNOWN", "Test", 0.5)
        cli = result.project(RenderTarget.CLI)

        # Should use default symbol
        assert "●" in cli

    def test_all_standard_phases(self) -> None:
        """status_row works for all 11 standard phases."""
        phases = [
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "SENSE",
            "ACT",
            "REFLECT",
        ]

        for phase in phases:
            result = status_row(phase, "Activity", 0.5)
            assert isinstance(result, HStack)
            cli = result.project(RenderTarget.CLI)
            assert phase in cli


# =============================================================================
# Composition Tests
# =============================================================================


class TestPresetComposition:
    """Test composing presets together."""

    def test_stacked_rows(self) -> None:
        """Stack multiple metric_rows."""
        row1 = metric_row(
            BarWidget(BarState(value=0.3, label="A")),
            BarWidget(BarState(value=0.5, label="B")),
        )
        row2 = metric_row(
            BarWidget(BarState(value=0.7, label="C")),
            BarWidget(BarState(value=0.9, label="D")),
        )

        result = metric_stack(row1, row2)

        assert isinstance(result, VStack)
        assert len(result.children) == 2

    def test_panel_with_labeled_body(self) -> None:
        """Panel with labeled widgets in body."""
        header = GlyphWidget(GlyphState(char="System Status"))
        body = metric_stack(
            labeled("CPU:", BarWidget(BarState(value=0.5))),
            labeled("MEM:", BarWidget(BarState(value=0.7))),
        )

        result = panel(header, body)

        assert isinstance(result, VStack)
        cli = result.project(RenderTarget.CLI)
        assert "System Status" in cli
        assert "CPU:" in cli
        assert "MEM:" in cli

    def test_dashboard_layout(self) -> None:
        """Full dashboard layout using presets."""
        # Header
        header = GlyphWidget(GlyphState(char="═══ Agent Dashboard ═══"))

        # Status rows
        sense_status = status_row("SENSE", "Scanning...", 0.9)
        act_status = status_row("ACT", "Idle", 0.5)
        reflect_status = status_row("REFLECT", "Complete", 1.0)

        # Metrics
        metrics = metric_row(
            BarWidget(BarState(value=0.6, label="Health")),
            BarWidget(BarState(value=0.4, label="Energy")),
        )

        # Assemble
        body = metric_stack(sense_status, act_status, reflect_status, metrics)
        dashboard = panel(header, body, gap=1)

        cli = dashboard.project(RenderTarget.CLI)

        assert "Agent Dashboard" in cli
        assert "SENSE" in cli
        assert "ACT" in cli
        assert "REFLECT" in cli


# =============================================================================
# BarWidget Composition Tests (verifies ComposableMixin added correctly)
# =============================================================================


class TestBarWidgetComposition:
    """Test that BarWidget now has >> and // operators."""

    def test_bar_rshift_bar(self) -> None:
        """bar >> bar creates HStack."""
        bar1 = BarWidget(BarState(value=0.3))
        bar2 = BarWidget(BarState(value=0.7))

        result = bar1 >> bar2

        assert isinstance(result, HStack)
        assert len(result.children) == 2
        assert result.children[0] is bar1
        assert result.children[1] is bar2

    def test_bar_floordiv_bar(self) -> None:
        """bar // bar creates VStack."""
        bar1 = BarWidget(BarState(value=0.3))
        bar2 = BarWidget(BarState(value=0.7))

        result = bar1 // bar2

        assert isinstance(result, VStack)
        assert len(result.children) == 2
        assert result.children[0] is bar1
        assert result.children[1] is bar2

    def test_bar_chain_composition(self) -> None:
        """bar >> bar >> bar chains correctly."""
        bar1 = BarWidget(BarState(value=0.2))
        bar2 = BarWidget(BarState(value=0.5))
        bar3 = BarWidget(BarState(value=0.8))

        result = bar1 >> bar2 >> bar3

        assert isinstance(result, HStack)
        assert len(result.children) == 3

    def test_bar_with_glyph(self) -> None:
        """bar >> glyph composes correctly."""
        bar = BarWidget(BarState(value=0.5))
        glyph = GlyphWidget(GlyphState(char="X"))

        result = bar >> glyph

        assert isinstance(result, HStack)
        assert len(result.children) == 2

    def test_bar_in_metric_row(self) -> None:
        """BarWidget works in metric_row."""
        bar1 = BarWidget(BarState(value=0.5, label="A"))
        bar2 = BarWidget(BarState(value=0.8, label="B"))

        result = metric_row(bar1, bar2)
        cli = result.project(RenderTarget.CLI)

        assert "A:" in cli
        assert "B:" in cli
