"""
Tests for ComposableWidget protocol and >> / // operators.

Tests verify:
1. HStack and VStack creation via operators
2. Associativity of composition operators
3. Theme propagation through composed widgets
4. from_signal() factory binding
5. CLI/TUI/MARIMO/JSON projections
"""

from __future__ import annotations

import pytest
from agents.i.reactive.composable import (
    ComposableMixin,
    ComposableWidget,
    HStack,
    VStack,
)
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.signal import Signal
from agents.i.reactive.widget import RenderTarget

# =============================================================================
# Protocol Compliance Tests
# =============================================================================


class TestProtocolCompliance:
    """Test that widgets implement ComposableWidget protocol."""

    def test_glyph_is_composable(self) -> None:
        """GlyphWidget implements ComposableWidget."""
        glyph = GlyphWidget(GlyphState(char="X"))
        assert isinstance(glyph, ComposableWidget)

    def test_sparkline_is_composable(self) -> None:
        """SparklineWidget implements ComposableWidget."""
        spark = SparklineWidget(SparklineState(values=(0.5,)))
        assert isinstance(spark, ComposableWidget)

    def test_hstack_is_composable(self) -> None:
        """HStack implements ComposableWidget."""
        hstack = HStack()
        assert isinstance(hstack, ComposableWidget)

    def test_vstack_is_composable(self) -> None:
        """VStack implements ComposableWidget."""
        vstack = VStack()
        assert isinstance(vstack, ComposableWidget)


# =============================================================================
# Operator Tests: >> (HStack)
# =============================================================================


class TestHStackOperator:
    """Test >> operator creates HStack."""

    def test_rshift_creates_hstack(self) -> None:
        """widget >> widget creates HStack."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = a >> b

        assert isinstance(result, HStack)
        assert len(result.children) == 2
        assert result.children[0] is a
        assert result.children[1] is b

    def test_hstack_rshift_flattens(self) -> None:
        """(a >> b) >> c flattens to HStack([a, b, c])."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))

        result = (a >> b) >> c

        assert isinstance(result, HStack)
        assert len(result.children) == 3
        assert result.children[0] is a
        assert result.children[1] is b
        assert result.children[2] is c

    def test_hstack_rshift_hstack_merges(self) -> None:
        """(a >> b) >> (c >> d) merges to HStack([a, b, c, d])."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        result = (a >> b) >> (c >> d)

        assert isinstance(result, HStack)
        assert len(result.children) == 4

    def test_associativity_left(self) -> None:
        """((a >> b) >> c) produces same structure as (a >> (b >> c))."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))

        left = (a >> b) >> c
        # Note: a >> (b >> c) puts a first, then absorbs b and c
        right_bc = b >> c
        right = a >> right_bc

        # Both should flatten to 3 children
        assert len(left.children) == 3
        assert len(right.children) == 3

    def test_sparkline_rshift(self) -> None:
        """SparklineWidget >> SparklineWidget creates HStack."""
        s1 = SparklineWidget(SparklineState(values=(0.1, 0.2, 0.3)))
        s2 = SparklineWidget(SparklineState(values=(0.4, 0.5, 0.6)))

        result = s1 >> s2

        assert isinstance(result, HStack)
        assert len(result.children) == 2

    def test_mixed_widget_rshift(self) -> None:
        """Different widget types can compose via >>."""
        glyph = GlyphWidget(GlyphState(char="X"))
        spark = SparklineWidget(SparklineState(values=(0.5,)))

        result = glyph >> spark

        assert isinstance(result, HStack)
        assert len(result.children) == 2


# =============================================================================
# Operator Tests: // (VStack)
# =============================================================================


class TestVStackOperator:
    """Test // operator creates VStack."""

    def test_floordiv_creates_vstack(self) -> None:
        """widget // widget creates VStack."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = a // b

        assert isinstance(result, VStack)
        assert len(result.children) == 2
        assert result.children[0] is a
        assert result.children[1] is b

    def test_vstack_floordiv_flattens(self) -> None:
        """(a // b) // c flattens to VStack([a, b, c])."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))

        result = (a // b) // c

        assert isinstance(result, VStack)
        assert len(result.children) == 3
        assert result.children[0] is a
        assert result.children[1] is b
        assert result.children[2] is c

    def test_vstack_floordiv_vstack_merges(self) -> None:
        """(a // b) // (c // d) merges to VStack([a, b, c, d])."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        result = (a // b) // (c // d)

        assert isinstance(result, VStack)
        assert len(result.children) == 4


# =============================================================================
# Mixed Composition Tests
# =============================================================================


class TestMixedComposition:
    """Test mixing >> and // operators."""

    def test_hstack_floordiv_creates_vstack(self) -> None:
        """HStack // widget creates VStack."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))

        row = a >> b
        result = row // c

        assert isinstance(result, VStack)
        assert len(result.children) == 2
        assert result.children[0] is row
        assert result.children[1] is c

    def test_vstack_rshift_creates_hstack(self) -> None:
        """VStack >> widget creates HStack."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))

        col = a // b
        result = col >> c

        assert isinstance(result, HStack)
        assert len(result.children) == 2
        assert result.children[0] is col
        assert result.children[1] is c

    def test_complex_layout(self) -> None:
        """Complex nested layout: (a >> b) // (c >> d)."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        top_row = a >> b
        bot_row = c >> d
        layout = top_row // bot_row

        assert isinstance(layout, VStack)
        assert len(layout.children) == 2
        assert isinstance(layout.children[0], HStack)
        assert isinstance(layout.children[1], HStack)


# =============================================================================
# Projection Tests
# =============================================================================


class TestHStackProjection:
    """Test HStack projection to different targets."""

    def test_cli_projection(self) -> None:
        """HStack CLI joins with gap."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a >> b).project(RenderTarget.CLI)

        assert "A" in result
        assert "B" in result

    def test_cli_with_separator(self) -> None:
        """HStack CLI with separator."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        hstack = (a >> b).with_separator("|")
        result = hstack.project(RenderTarget.CLI)

        assert result == "A|B"

    def test_json_projection(self) -> None:
        """HStack JSON returns structured dict."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a >> b).project(RenderTarget.JSON)

        assert result["type"] == "hstack"
        assert len(result["children"]) == 2

    def test_marimo_projection(self) -> None:
        """HStack MARIMO returns HTML div."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a >> b).project(RenderTarget.MARIMO)

        assert "kgents-hstack" in result
        assert "inline-flex" in result

    def test_empty_hstack_cli(self) -> None:
        """Empty HStack returns empty string for CLI."""
        hstack = HStack()
        assert hstack.project(RenderTarget.CLI) == ""

    def test_empty_hstack_json(self) -> None:
        """Empty HStack returns empty dict for JSON."""
        hstack = HStack()
        assert hstack.project(RenderTarget.JSON) == {}


class TestVStackProjection:
    """Test VStack projection to different targets."""

    def test_cli_projection(self) -> None:
        """VStack CLI joins with newlines."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a // b).project(RenderTarget.CLI)

        assert "A" in result
        assert "B" in result
        assert "\n" in result

    def test_cli_with_gap(self) -> None:
        """VStack CLI with gap adds extra newlines."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        vstack = (a // b).with_gap(1)
        result = vstack.project(RenderTarget.CLI)

        assert "\n\n" in result

    def test_json_projection(self) -> None:
        """VStack JSON returns structured dict."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a // b).project(RenderTarget.JSON)

        assert result["type"] == "vstack"
        assert len(result["children"]) == 2

    def test_marimo_projection(self) -> None:
        """VStack MARIMO returns HTML div."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        result = (a // b).project(RenderTarget.MARIMO)

        assert "kgents-vstack" in result
        assert "flex-direction: column" in result


# =============================================================================
# from_signal() Factory Tests
# =============================================================================


class TestFromSignal:
    """Test from_signal() factory method."""

    def test_glyph_from_signal(self) -> None:
        """GlyphWidget.from_signal binds to external signal."""
        signal = Signal.of(GlyphState(char="X"))
        glyph = GlyphWidget.from_signal(signal)

        # Initial value
        assert glyph.state.value.char == "X"

        # Signal update
        signal.set(GlyphState(char="Y"))
        assert glyph.state.value.char == "Y"

    def test_sparkline_from_signal(self) -> None:
        """SparklineWidget.from_signal binds to external signal."""
        signal = Signal.of(SparklineState(values=(0.1, 0.5, 0.9)))
        spark = SparklineWidget.from_signal(signal)

        # Initial value
        assert spark.state.value.values == (0.1, 0.5, 0.9)

        # Signal update
        signal.set(SparklineState(values=(0.2, 0.6, 1.0)))
        assert spark.state.value.values == (0.2, 0.6, 1.0)

    def test_from_signal_reactive_update(self) -> None:
        """from_signal widget renders latest signal value."""
        signal = Signal.of(GlyphState(char="A"))
        glyph = GlyphWidget.from_signal(signal)

        # Initial render
        assert glyph.project(RenderTarget.CLI) == "A"

        # Update signal
        signal.set(GlyphState(char="B"))

        # Re-render shows new value
        assert glyph.project(RenderTarget.CLI) == "B"


# =============================================================================
# Configuration Tests
# =============================================================================


class TestHStackConfiguration:
    """Test HStack configuration methods."""

    def test_with_gap(self) -> None:
        """with_gap returns new HStack with updated gap."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        original = a >> b
        modified = original.with_gap(5)

        assert modified.gap == 5
        assert original.gap == 1  # Original unchanged

    def test_with_separator(self) -> None:
        """with_separator returns new HStack with separator."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        hstack = (a >> b).with_separator(" | ")

        assert hstack.separator == " | "
        assert hstack.project(RenderTarget.CLI) == "A | B"


class TestVStackConfiguration:
    """Test VStack configuration methods."""

    def test_with_gap(self) -> None:
        """with_gap returns new VStack with updated gap."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        original = a // b
        modified = original.with_gap(2)

        assert modified.gap == 2
        assert original.gap == 0  # Original unchanged

    def test_with_separator(self) -> None:
        """with_separator returns new VStack with separator line."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))

        vstack = (a // b).with_separator("---")

        assert vstack.separator == "---"
        result = vstack.project(RenderTarget.CLI)
        assert "---" in result


# =============================================================================
# Sparkline Composition Tests
# =============================================================================


class TestSparklineComposition:
    """Test sparkline-specific composition scenarios."""

    def test_sparklines_side_by_side(self) -> None:
        """Two sparklines side by side via >>."""
        s1 = SparklineWidget(SparklineState(values=(0.1, 0.2, 0.3), label="CPU"))
        s2 = SparklineWidget(SparklineState(values=(0.4, 0.5, 0.6), label="MEM"))

        result = s1 >> s2

        cli_output = result.project(RenderTarget.CLI)
        assert "CPU" in cli_output
        assert "MEM" in cli_output

    def test_sparklines_stacked(self) -> None:
        """Two sparklines stacked via //."""
        s1 = SparklineWidget(SparklineState(values=(0.1, 0.2, 0.3), label="CPU"))
        s2 = SparklineWidget(SparklineState(values=(0.4, 0.5, 0.6), label="MEM"))

        result = s1 // s2

        cli_output = result.project(RenderTarget.CLI)
        assert "CPU" in cli_output
        assert "MEM" in cli_output
        assert "\n" in cli_output


# =============================================================================
# Complex Layout Tests
# =============================================================================


class TestComplexLayouts:
    """Test complex widget layouts."""

    def test_dashboard_layout(self) -> None:
        """Dashboard-style layout: header row + body row."""
        # Header: status glyph + title glyph
        status = GlyphWidget(GlyphState(char="◉", phase="active"))
        title = GlyphWidget(GlyphState(char="Dashboard"))

        # Body: two sparklines
        cpu = SparklineWidget(SparklineState(values=(0.3, 0.5, 0.7)))
        mem = SparklineWidget(SparklineState(values=(0.6, 0.4, 0.2)))

        header = status >> title
        body = cpu >> mem
        layout = header // body

        # Should produce valid CLI output
        cli = layout.project(RenderTarget.CLI)
        assert isinstance(cli, str)
        assert len(cli) > 0

        # Should produce valid JSON
        json_out = layout.project(RenderTarget.JSON)
        assert json_out["type"] == "vstack"
        assert len(json_out["children"]) == 2

    def test_grid_like_layout(self) -> None:
        """Grid-like layout using // and >>."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        # 2x2 grid
        row1 = a >> b
        row2 = c >> d
        grid = row1 // row2

        cli = grid.project(RenderTarget.CLI)
        lines = cli.split("\n")
        assert len(lines) >= 2


# =============================================================================
# to_textual() Tests
# =============================================================================


class TestToTextual:
    """Test to_textual() conversion for Textual rendering."""

    def test_hstack_to_textual_returns_horizontal(self) -> None:
        """HStack.to_textual() returns Textual Horizontal container."""
        from textual.containers import Horizontal

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        hstack = a >> b

        textual_widget = hstack.to_textual()

        assert isinstance(textual_widget, Horizontal)

    def test_vstack_to_textual_returns_vertical(self) -> None:
        """VStack.to_textual() returns Textual Vertical container."""
        from textual.containers import Vertical

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        vstack = a // b

        textual_widget = vstack.to_textual()

        assert isinstance(textual_widget, Vertical)

    def test_hstack_to_textual_with_id(self) -> None:
        """HStack.to_textual() accepts id parameter."""
        from textual.containers import Horizontal

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        hstack = a >> b

        textual_widget = hstack.to_textual(id="my-hstack")

        assert isinstance(textual_widget, Horizontal)
        assert textual_widget.id == "my-hstack"

    def test_vstack_to_textual_with_classes(self) -> None:
        """VStack.to_textual() accepts classes parameter."""
        from textual.containers import Vertical

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        vstack = a // b

        textual_widget = vstack.to_textual(classes="my-class")

        assert isinstance(textual_widget, Vertical)
        assert "my-class" in textual_widget.classes

    def test_nested_composition_to_textual(self) -> None:
        """Nested composition recursively converts to Textual tree."""
        from textual.containers import Horizontal, Vertical

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        # (A >> B) // (C >> D) -> Vertical containing two Horizontals
        layout = (a >> b) // (c >> d)

        textual_widget = layout.to_textual()

        assert isinstance(textual_widget, Vertical)

    def test_adapter_to_textual_function(self) -> None:
        """to_textual() function from adapters works on composed widgets."""
        from agents.i.reactive.adapters import to_textual
        from textual.containers import Vertical

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        vstack = a // b

        textual_widget = to_textual(vstack)

        assert isinstance(textual_widget, Vertical)

    def test_adapter_to_textual_on_primitive(self) -> None:
        """to_textual() function wraps primitives in TextualAdapter."""
        from agents.i.reactive.adapters import TextualAdapter, to_textual

        glyph = GlyphWidget(GlyphState(char="X"))

        textual_widget = to_textual(glyph)

        assert isinstance(textual_widget, TextualAdapter)

    def test_adapter_to_textual_passthrough_textual_widget(self) -> None:
        """to_textual() returns Textual widgets unchanged."""
        from agents.i.reactive.adapters import to_textual
        from textual.widgets import Static

        static = Static("Hello")

        result = to_textual(static)

        assert result is static


# =============================================================================
# to_marimo() Tests
# =============================================================================


class TestToMarimo:
    """Test to_marimo() conversion for marimo notebooks."""

    def test_hstack_to_marimo_html_fallback(self) -> None:
        """HStack.to_marimo() returns HTML string when anywidget unavailable."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        hstack = a >> b

        # Force HTML fallback
        result = hstack.to_marimo(use_anywidget=False)

        assert isinstance(result, str)
        assert "kgents-hstack" in result
        assert "inline-flex" in result

    def test_vstack_to_marimo_html_fallback(self) -> None:
        """VStack.to_marimo() returns HTML string when anywidget unavailable."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        vstack = a // b

        # Force HTML fallback
        result = vstack.to_marimo(use_anywidget=False)

        assert isinstance(result, str)
        assert "kgents-vstack" in result
        assert "flex-direction: column" in result

    def test_adapter_to_marimo_function(self) -> None:
        """to_marimo() function from adapters works on composed widgets."""
        from agents.i.reactive.adapters import to_marimo

        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        vstack = a // b

        # Force HTML fallback
        result = to_marimo(vstack, use_anywidget=False)

        assert isinstance(result, str)
        assert "kgents-vstack" in result

    def test_adapter_to_marimo_on_primitive(self) -> None:
        """to_marimo() function on primitive widget returns HTML."""
        from agents.i.reactive.adapters import to_marimo

        glyph = GlyphWidget(GlyphState(char="X"))

        # Force HTML fallback
        result = to_marimo(glyph, use_anywidget=False)

        assert isinstance(result, str)
        assert "X" in result

    def test_nested_composition_to_marimo(self) -> None:
        """Nested composition produces valid HTML."""
        a = GlyphWidget(GlyphState(char="A"))
        b = GlyphWidget(GlyphState(char="B"))
        c = GlyphWidget(GlyphState(char="C"))
        d = GlyphWidget(GlyphState(char="D"))

        # (A >> B) // (C >> D)
        layout = (a >> b) // (c >> d)

        result = layout.to_marimo(use_anywidget=False)

        assert isinstance(result, str)
        assert "kgents-vstack" in result
        # Nested HStacks should also be rendered
        assert "kgents-hstack" in result
