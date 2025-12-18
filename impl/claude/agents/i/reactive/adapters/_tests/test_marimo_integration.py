"""
Integration tests for the full marimo adapter stack.

Tests the complete flow from KgentsWidget -> MarimoAdapter -> JSON -> ESM rendering.
"""

from __future__ import annotations

import json

import pytest

from agents.i.reactive.adapters import (
    AgentTraceState,
    AgentTraceWidget,
    MarimoAdapter,
    NotebookTheme,
    SpanData,
    create_marimo_adapter,
    create_notebook_theme,
    create_trace_widget,
    inject_theme_css,
    is_anywidget_available,
)
from agents.i.reactive.primitives.agent_card import AgentCardState, AgentCardWidget
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.primitives.glyph import (
    Animation,
    GlyphState,
    GlyphWidget,
    Phase,
)
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.widget import RenderTarget

# ============================================================
# Full Stack Integration Tests
# ============================================================


class TestFullStackIntegration:
    """Test the complete stack from widget to JSON."""

    def test_agent_card_full_flow(self):
        """AgentCardWidget -> MarimoAdapter -> JSON -> renderable."""
        card = AgentCardWidget(
            AgentCardState(
                agent_id="integration-test",
                name="Integration Agent",
                phase="active",
                activity=(0.1, 0.3, 0.5, 0.7, 0.9),
                capability=0.8,
                entropy=0.15,
            )
        )

        # Create adapter
        adapter = MarimoAdapter(card)

        # Verify adapter holds reference
        assert adapter.kgents_widget is card

        # Verify JSON projection works
        json_output = card.project(RenderTarget.JSON)
        assert json_output["type"] == "agent_card"
        assert json_output["agent_id"] == "integration-test"

        # Verify MARIMO projection works
        marimo_output = card.project(RenderTarget.MARIMO)
        assert "kgents-agent-card" in marimo_output
        assert "Integration Agent" in marimo_output

    def test_sparkline_full_flow(self):
        """SparklineWidget full integration."""
        values = tuple(i / 10.0 for i in range(1, 11))
        sparkline = SparklineWidget(SparklineState(values=values))

        adapter = MarimoAdapter(sparkline)

        json_output = sparkline.project(RenderTarget.JSON)
        assert json_output["type"] == "sparkline"
        assert len(json_output["values"]) == 10

        marimo_output = sparkline.project(RenderTarget.MARIMO)
        assert "kgents-sparkline" in marimo_output

    def test_bar_full_flow(self):
        """BarWidget full integration."""
        bar = BarWidget(BarState(value=0.6, width=15, style="gradient"))

        adapter = MarimoAdapter(bar)

        json_output = bar.project(RenderTarget.JSON)
        assert json_output["type"] == "bar"
        assert json_output["value"] == 0.6
        assert json_output["width"] == 15

        marimo_output = bar.project(RenderTarget.MARIMO)
        assert "kgents-bar" in marimo_output

    def test_trace_full_flow(self):
        """AgentTraceWidget full integration."""
        spans = [
            SpanData(
                span_id="root",
                name="agent.execute",
                kind="agent",
                start_time_ms=0,
                end_time_ms=2000,
            ),
            SpanData(
                span_id="llm",
                name="llm.inference",
                kind="llm_call",
                parent_id="root",
                start_time_ms=100,
                end_time_ms=1500,
                attributes={"tokens": 200, "model": "claude-3"},
            ),
        ]

        trace = create_trace_widget(
            trace_id="integration-trace",
            root_agent="test-agent",
            spans=spans,
        )

        adapter = MarimoAdapter(trace)

        json_output = trace.project(RenderTarget.JSON)
        assert json_output["type"] == "agent_trace"
        assert json_output["span_count"] == 2
        assert json_output["total_latency_ms"] == 2000.0

        marimo_output = trace.project(RenderTarget.MARIMO)
        assert "kgents-trace" in marimo_output


# ============================================================
# Theme Integration Tests
# ============================================================


class TestThemeIntegration:
    """Test theme integration with widgets."""

    def test_theme_css_injection(self):
        """Theme CSS can be injected alongside widgets."""
        theme = NotebookTheme(primary="#custom_color")
        css = inject_theme_css(theme)

        assert "<style>" in css
        assert "#custom_color" in css
        assert "--kgents-primary" in css

    def test_theme_with_widget(self):
        """Widget HTML + theme CSS work together."""
        card = AgentCardWidget(AgentCardState(name="Themed Agent"))
        theme = NotebookTheme.from_marimo()

        widget_html = card.project(RenderTarget.MARIMO)
        theme_css = inject_theme_css(theme)

        # Both should be valid HTML/CSS
        assert "<div" in widget_html
        assert "<style>" in theme_css

    def test_all_theme_variants(self):
        """All theme variants produce valid CSS."""
        variants = [
            NotebookTheme(),
            NotebookTheme.light(),
            NotebookTheme.dark(),
            NotebookTheme.from_marimo(),
            create_notebook_theme(dark_mode=True),
            create_notebook_theme(dark_mode=False),
            create_notebook_theme(inherit_marimo=True),
        ]

        for theme in variants:
            css = theme.to_css()
            assert "--kgents-" in css
            assert "{" in css and "}" in css


# ============================================================
# State Update Integration Tests
# ============================================================


@pytest.mark.skipif(
    not is_anywidget_available(),
    reason="anywidget not installed",
)
class TestStateUpdateIntegration:
    """Test state updates propagate through the stack."""

    def test_signal_update_propagates(self):
        """Signal updates propagate to adapter state."""
        card = AgentCardWidget(AgentCardState(name="Before", phase="idle"))
        adapter = MarimoAdapter(card)

        # Initial state
        state1 = json.loads(adapter._state_json)
        assert state1["name"] == "Before"
        assert state1["phase"] == "idle"

        # Update via Signal
        card.state.set(AgentCardState(name="After", phase="active"))

        # Check propagation
        state2 = json.loads(adapter._state_json)
        assert state2["name"] == "After"
        assert state2["phase"] == "active"

    def test_immutable_update_creates_new_widget(self):
        """Immutable updates create new widgets."""
        card1 = AgentCardWidget(AgentCardState(phase="idle"))
        card2 = card1.with_phase("active")

        assert card1.state.value.phase == "idle"
        assert card2.state.value.phase == "active"
        assert card1 is not card2

    def test_sparkline_push_propagates(self):
        """Sparkline push creates updated widget."""
        spark1 = SparklineWidget(SparklineState(values=(0.5,)))
        spark2 = spark1.push(0.8)

        assert spark1.state.value.values == (0.5,)
        assert spark2.state.value.values == (0.5, 0.8)

    def test_trace_add_span_propagates(self):
        """Trace add_span creates updated widget."""
        trace1 = AgentTraceWidget(AgentTraceState(trace_id="test"))
        trace2 = trace1.add_span(
            SpanData(span_id="1", name="span1", start_time_ms=0, end_time_ms=100)
        )

        assert len(trace1.state.value.spans) == 0
        assert len(trace2.state.value.spans) == 1


# ============================================================
# Cross-Widget Integration Tests
# ============================================================


class TestCrossWidgetIntegration:
    """Test interactions between different widget types."""

    def test_multiple_widgets_same_adapter_type(self):
        """Multiple widgets can use adapters simultaneously."""
        card = AgentCardWidget(AgentCardState(name="Card"))
        spark = SparklineWidget(SparklineState(values=(0.5,)))
        bar = BarWidget(BarState(value=0.7))

        adapter_card = MarimoAdapter(card)
        adapter_spark = MarimoAdapter(spark)
        adapter_bar = MarimoAdapter(bar)

        # All should have correct widget types
        assert adapter_card.kgents_widget is card
        assert adapter_spark.kgents_widget is spark
        assert adapter_bar.kgents_widget is bar

    def test_all_render_targets_consistent(self):
        """All render targets produce consistent data."""
        card = AgentCardWidget(
            AgentCardState(
                agent_id="consistent-test",
                name="Consistent Agent",
                phase="active",
            )
        )

        cli = card.project(RenderTarget.CLI)
        tui = card.project(RenderTarget.TUI)
        marimo = card.project(RenderTarget.MARIMO)
        json_out = card.project(RenderTarget.JSON)

        # All should contain agent name
        assert "Consistent Agent" in cli
        # TUI returns a Rich Panel - check its title contains agent_id
        assert hasattr(tui, "title")  # It's a Panel
        assert "consistent-test" in str(tui.title)
        assert "Consistent Agent" in marimo
        assert json_out["name"] == "Consistent Agent"


# ============================================================
# Glyph Widget Tests
# ============================================================


class TestGlyphWidgetIntegration:
    """Test GlyphWidget integration (atomic unit)."""

    def test_glyph_all_phases(self):
        """Glyph renders correctly for all phases."""
        phases = [
            "idle",
            "active",
            "waiting",
            "error",
            "yielding",
            "thinking",
            "complete",
        ]

        from typing import cast

        for phase in phases:
            glyph = GlyphWidget(GlyphState(phase=cast(Phase, phase)))
            json_out = glyph.project(RenderTarget.JSON)
            assert json_out["phase"] == phase

    def test_glyph_with_entropy(self):
        """Glyph with entropy includes distortion."""
        glyph = GlyphWidget(GlyphState(char="●", entropy=0.5, seed=42))
        json_out = glyph.project(RenderTarget.JSON)

        assert json_out["entropy"] == 0.5
        assert "distortion" in json_out

    def test_glyph_animations(self):
        """Glyph animations in marimo output."""
        from typing import cast

        animations = ["none", "pulse", "blink", "breathe", "wiggle"]

        for anim in animations:
            glyph = GlyphWidget(GlyphState(char="◉", animate=cast(Animation, anim)))
            marimo_out = glyph.project(RenderTarget.MARIMO)

            if anim != "none":
                assert f"glyph-{anim}" in marimo_out


# ============================================================
# Edge Case Integration Tests
# ============================================================


class TestEdgeCaseIntegration:
    """Edge case integration tests."""

    def test_empty_card(self):
        """Empty/default card renders without error."""
        card = AgentCardWidget()
        adapter = MarimoAdapter(card)

        # Should not error
        json_out = card.project(RenderTarget.JSON)
        assert json_out["type"] == "agent_card"

    def test_empty_sparkline(self):
        """Empty sparkline renders placeholder."""
        spark = SparklineWidget()
        cli_out = spark.project(RenderTarget.CLI)

        assert "─" in cli_out  # Empty placeholder

    def test_zero_bar(self):
        """Zero-value bar renders correctly."""
        bar = BarWidget(BarState(value=0.0))
        json_out = bar.project(RenderTarget.JSON)

        assert json_out["value"] == 0.0

    def test_full_bar(self):
        """Full bar renders correctly."""
        bar = BarWidget(BarState(value=1.0))
        json_out = bar.project(RenderTarget.JSON)

        assert json_out["value"] == 1.0

    def test_max_length_sparkline(self):
        """Sparkline at max length truncates correctly."""
        values = tuple(0.5 for _ in range(100))
        spark = SparklineWidget(SparklineState(values=values, max_length=20))

        # Push more values
        for _ in range(10):
            spark = spark.push(0.8)

        assert len(spark.state.value.values) <= 20

    def test_unicode_in_name(self):
        """Unicode in agent name renders correctly."""
        card = AgentCardWidget(AgentCardState(name="Agent 日本語 🤖"))

        json_out = card.project(RenderTarget.JSON)
        assert json_out["name"] == "Agent 日本語 🤖"

        marimo_out = card.project(RenderTarget.MARIMO)
        assert "日本語" in marimo_out
        assert "🤖" in marimo_out
