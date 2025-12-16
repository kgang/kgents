"""Tests for SparklineWidget - time-series mini-chart visualization."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.sparkline import SparklineState, SparklineWidget
from agents.i.reactive.widget import RenderTarget


class TestSparklineState:
    """Tests for SparklineState immutable state."""

    def test_default_state(self) -> None:
        """Default SparklineState has expected values."""
        state = SparklineState()
        assert state.values == ()
        assert state.max_length == 20
        assert state.entropy == 0.0

    def test_state_is_frozen(self) -> None:
        """SparklineState is immutable (frozen dataclass)."""
        state = SparklineState(values=(0.5,))
        with pytest.raises(Exception):
            state.values = (0.8,)  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """SparklineState can be created with all fields."""
        state = SparklineState(
            values=(0.1, 0.5, 0.9),
            max_length=30,
            fg="#00ff00",
            bg="#000000",
            entropy=0.3,
            seed=42,
            t=1000.0,
            label="CPU",
            show_bounds=True,
        )
        assert state.values == (0.1, 0.5, 0.9)
        assert state.max_length == 30
        assert state.label == "CPU"
        assert state.show_bounds is True


class TestSparklineWidget:
    """Tests for SparklineWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """SparklineWidget can be created with default state."""
        widget = SparklineWidget()
        assert widget.state.value == SparklineState()

    def test_create_with_initial_values(self) -> None:
        """SparklineWidget can be created with initial values."""
        state = SparklineState(values=(0.1, 0.5, 0.9))
        widget = SparklineWidget(state)
        assert widget.state.value.values == (0.1, 0.5, 0.9)

    def test_push_adds_value(self) -> None:
        """push() adds a value to the sparkline."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.5)))
        updated = widget.push(0.9)

        assert widget.state.value.values == (0.1, 0.5)  # Original unchanged
        assert updated.state.value.values == (0.1, 0.5, 0.9)

    def test_push_clamps_value(self) -> None:
        """push() clamps values to 0.0-1.0."""
        widget = SparklineWidget()
        assert widget.push(-0.5).state.value.values == (0.0,)
        assert widget.push(1.5).state.value.values == (1.0,)

    def test_push_trims_to_max_length(self) -> None:
        """push() drops oldest when at max_length."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.2, 0.3), max_length=3))
        updated = widget.push(0.9)

        # Oldest value (0.1) dropped
        assert updated.state.value.values == (0.2, 0.3, 0.9)

    def test_with_values_replaces_all(self) -> None:
        """with_values() replaces all values."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.2)))
        updated = widget.with_values([0.5, 0.6, 0.7])

        assert widget.state.value.values == (0.1, 0.2)
        assert updated.state.value.values == (0.5, 0.6, 0.7)

    def test_with_values_trims_to_max_length(self) -> None:
        """with_values() respects max_length."""
        widget = SparklineWidget(SparklineState(max_length=3))
        updated = widget.with_values([0.1, 0.2, 0.3, 0.4, 0.5])

        # Only last 3 values kept
        assert updated.state.value.values == (0.3, 0.4, 0.5)

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget."""
        original = SparklineWidget(SparklineState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = SparklineWidget(SparklineState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5


class TestSparklineProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_empty_sparkline(self) -> None:
        """Empty sparkline shows placeholder."""
        widget = SparklineWidget(SparklineState(values=()))
        result = widget.project(RenderTarget.CLI)
        assert "─" in result  # Placeholder

    def test_project_cli_uses_spark_chars(self) -> None:
        """Sparkline uses vertical bar characters."""
        widget = SparklineWidget(SparklineState(values=(0.0, 0.5, 1.0)))
        result = widget.project(RenderTarget.CLI)

        # Should contain spark characters
        assert "▁" in result  # Lowest
        assert "█" in result  # Highest

    def test_project_cli_with_label(self) -> None:
        """CLI projection includes label when set."""
        widget = SparklineWidget(SparklineState(values=(0.5,), label="CPU"))
        result = widget.project(RenderTarget.CLI)
        assert result.startswith("CPU: ")

    def test_project_cli_with_bounds(self) -> None:
        """CLI projection shows bounds when requested."""
        widget = SparklineWidget(
            SparklineState(values=(0.2, 0.5, 0.8), show_bounds=True)
        )
        result = widget.project(RenderTarget.CLI)
        assert "[0.20-0.80]" in result


class TestSparklineProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes basic fields."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9), max_length=30))
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "sparkline"
        assert result["values"] == [0.1, 0.5, 0.9]
        assert result["max_length"] == 30

    def test_project_json_includes_stats(self) -> None:
        """JSON projection includes min/max/current."""
        widget = SparklineWidget(SparklineState(values=(0.2, 0.8, 0.5)))
        result = widget.project(RenderTarget.JSON)

        assert result["min"] == 0.2
        assert result["max"] == 0.8
        assert result["current"] == 0.5

    def test_project_json_includes_glyphs(self) -> None:
        """JSON projection includes glyph array."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9)))
        result = widget.project(RenderTarget.JSON)

        assert "glyphs" in result
        assert len(result["glyphs"]) == 3
        assert all(g["type"] == "glyph" for g in result["glyphs"])


class TestSparklineProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        result = widget.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-sparkline" in result
        assert "<span" in result

    def test_project_marimo_inline_flex(self) -> None:
        """Sparkline uses inline-flex for horizontal layout."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.5)))
        result = widget.project(RenderTarget.MARIMO)
        assert "inline-flex" in result


class TestSparklineProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_rich_text(self) -> None:
        """TUI projection returns Rich Text (when available)."""
        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9)))
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            assert isinstance(result, Text)
            assert len(str(result)) == 3
        except ImportError:
            assert isinstance(result, str)


class TestSparklineValueMapping:
    """Tests for value to spark character mapping."""

    def test_zero_value_lowest_char(self) -> None:
        """Zero value maps to lowest spark char."""
        widget = SparklineWidget(SparklineState(values=(0.0,)))
        result = widget.project(RenderTarget.CLI)
        assert "▁" in result

    def test_one_value_highest_char(self) -> None:
        """One value maps to highest spark char."""
        widget = SparklineWidget(SparklineState(values=(1.0,)))
        result = widget.project(RenderTarget.CLI)
        assert "█" in result

    def test_mid_value_mid_char(self) -> None:
        """Mid value maps to mid spark char."""
        widget = SparklineWidget(SparklineState(values=(0.5,)))
        result = widget.project(RenderTarget.CLI)
        # 0.5 should be around middle of spark chars
        assert result in "▃▄▅"


class TestSparklineDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = SparklineState(values=(0.1, 0.5, 0.9), entropy=0.3, seed=42, t=1000.0)

        widget1 = SparklineWidget(state)
        widget2 = SparklineWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        assert widget1.project(RenderTarget.JSON) == widget2.project(RenderTarget.JSON)


# =============================================================================
# Projection Functor Law Tests
# =============================================================================


class TestSparklineProjectionLaws:
    """Tests that SparklineWidget satisfies projection functor laws.

    These tests verify:
    1. Identity Law: project(id(state)) ≡ project(state)
    2. Composition Law: Composed state changes project correctly
    3. Determinism: Same state → same output (no hidden randomness)

    See: spec/protocols/projection.md
    See: agents/i/reactive/projection/laws.py
    """

    def test_identity_law_cli(self) -> None:
        """SparklineWidget satisfies identity law for CLI target."""
        from agents.i.reactive.projection import ExtendedTarget, verify_identity_law

        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9), max_length=20))
        assert verify_identity_law(widget, ExtendedTarget.CLI)

    def test_identity_law_json(self) -> None:
        """SparklineWidget satisfies identity law for JSON target."""
        from agents.i.reactive.projection import ExtendedTarget, verify_identity_law

        widget = SparklineWidget(SparklineState(values=(0.2, 0.4, 0.6, 0.8), entropy=0.3))
        assert verify_identity_law(widget, ExtendedTarget.JSON)

    def test_identity_law_marimo(self) -> None:
        """SparklineWidget satisfies identity law for MARIMO target."""
        from agents.i.reactive.projection import ExtendedTarget, verify_identity_law

        widget = SparklineWidget(SparklineState(values=(0.3, 0.7), label="CPU"))
        assert verify_identity_law(widget, ExtendedTarget.MARIMO)

    def test_identity_law_tui(self) -> None:
        """SparklineWidget satisfies identity law for TUI target."""
        from agents.i.reactive.projection import ExtendedTarget, verify_identity_law

        widget = SparklineWidget(SparklineState(values=(0.1, 0.2, 0.3), fg="cyan"))
        assert verify_identity_law(widget, ExtendedTarget.TUI)

    def test_composition_law_append_value(self) -> None:
        """SparklineWidget satisfies composition law with append transformation."""
        from agents.i.reactive.projection import ExtendedTarget, verify_composition_law

        def append_value(s: SparklineState) -> SparklineState:
            new_values = s.values + (0.75,)
            if len(new_values) > s.max_length:
                new_values = new_values[-s.max_length:]
            return SparklineState(
                values=new_values, max_length=s.max_length, fg=s.fg, bg=s.bg,
                entropy=s.entropy, seed=s.seed, t=s.t, label=s.label, show_bounds=s.show_bounds,
            )

        def identity(s: SparklineState) -> SparklineState:
            return s

        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9)))
        assert verify_composition_law(widget, append_value, identity, ExtendedTarget.CLI)

    def test_composition_law_scale_values(self) -> None:
        """SparklineWidget satisfies composition law with scale transformation."""
        from agents.i.reactive.projection import ExtendedTarget, verify_composition_law

        def scale_values(s: SparklineState) -> SparklineState:
            scaled = tuple(min(1.0, v * 1.2) for v in s.values)
            return SparklineState(
                values=scaled, max_length=s.max_length, fg=s.fg, bg=s.bg,
                entropy=s.entropy, seed=s.seed, t=s.t, label=s.label, show_bounds=s.show_bounds,
            )

        def add_label(s: SparklineState) -> SparklineState:
            return SparklineState(
                values=s.values, max_length=s.max_length, fg=s.fg, bg=s.bg,
                entropy=s.entropy, seed=s.seed, t=s.t, label="Memory", show_bounds=s.show_bounds,
            )

        widget = SparklineWidget(SparklineState(values=(0.3, 0.5, 0.7)))
        assert verify_composition_law(widget, scale_values, add_label, ExtendedTarget.JSON)

    def test_determinism_cli(self) -> None:
        """SparklineWidget projection is deterministic for CLI."""
        from agents.i.reactive.projection import ExtendedTarget, verify_determinism

        widget = SparklineWidget(SparklineState(values=(0.1, 0.5, 0.9), entropy=0.3, seed=42))
        assert verify_determinism(widget, ExtendedTarget.CLI, iterations=10)

    def test_determinism_json(self) -> None:
        """SparklineWidget projection is deterministic for JSON."""
        from agents.i.reactive.projection import ExtendedTarget, verify_determinism

        widget = SparklineWidget(SparklineState(values=(0.2, 0.4, 0.6, 0.8, 1.0), seed=99))
        assert verify_determinism(widget, ExtendedTarget.JSON, iterations=10)

    def test_all_laws_comprehensive(self) -> None:
        """SparklineWidget passes all projection laws."""
        from agents.i.reactive.projection import ExtendedTarget, verify_all_laws

        def shift_values(s: SparklineState) -> SparklineState:
            shifted = s.values[1:] + (0.5,) if s.values else (0.5,)
            return SparklineState(
                values=shifted, max_length=s.max_length, fg=s.fg, bg=s.bg,
                entropy=s.entropy, seed=s.seed, t=s.t, label=s.label, show_bounds=s.show_bounds,
            )

        def identity(s: SparklineState) -> SparklineState:
            return s

        widget = SparklineWidget(SparklineState(values=(0.1, 0.3, 0.5, 0.7)))
        result = verify_all_laws(
            widget,
            ExtendedTarget.CLI,
            state_transforms=[shift_values, identity],
        )

        assert result.all_passed, f"Law violations: {result.errors}"
