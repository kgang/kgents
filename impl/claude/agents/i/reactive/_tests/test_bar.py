"""Tests for BarWidget - horizontal/vertical bar visualization."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.bar import BarState, BarWidget
from agents.i.reactive.widget import RenderTarget


class TestBarState:
    """Tests for BarState immutable state."""

    def test_default_state(self) -> None:
        """Default BarState has expected values."""
        state = BarState()
        assert state.value == 0.0
        assert state.width == 10
        assert state.orientation == "horizontal"
        assert state.style == "solid"
        assert state.entropy == 0.0

    def test_state_is_frozen(self) -> None:
        """BarState is immutable (frozen dataclass)."""
        state = BarState(value=0.5)
        with pytest.raises(Exception):
            state.value = 0.8  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """BarState can be created with all fields."""
        state = BarState(
            value=0.75,
            width=20,
            orientation="vertical",
            style="gradient",
            fg="#ff0000",
            bg="#000000",
            entropy=0.5,
            seed=42,
            t=1000.0,
            label="Progress",
        )
        assert state.value == 0.75
        assert state.width == 20
        assert state.orientation == "vertical"
        assert state.style == "gradient"
        assert state.label == "Progress"


class TestBarWidget:
    """Tests for BarWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """BarWidget can be created with default state."""
        widget = BarWidget()
        assert widget.state.value == BarState()

    def test_create_with_initial_state(self) -> None:
        """BarWidget can be created with initial state."""
        state = BarState(value=0.5, width=20)
        widget = BarWidget(state)
        assert widget.state.value.value == 0.5
        assert widget.state.value.width == 20

    def test_with_value_returns_new_widget(self) -> None:
        """with_value() returns new widget, doesn't mutate original."""
        original = BarWidget(BarState(value=0.3))
        updated = original.with_value(0.8)

        assert original.state.value.value == 0.3
        assert updated.state.value.value == 0.8

    def test_with_value_clamps(self) -> None:
        """with_value() clamps to 0.0-1.0 range."""
        widget = BarWidget()
        assert widget.with_value(-0.5).state.value.value == 0.0
        assert widget.with_value(1.5).state.value.value == 1.0

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget."""
        original = BarWidget(BarState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = BarWidget(BarState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5


class TestBarProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        widget = BarWidget(BarState(value=0.5, width=10))
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_empty_bar(self) -> None:
        """Empty bar shows all empty chars."""
        widget = BarWidget(BarState(value=0.0, width=5, style="solid"))
        result = widget.project(RenderTarget.CLI)
        assert result == "░░░░░"

    def test_project_cli_full_bar(self) -> None:
        """Full bar shows all filled chars."""
        widget = BarWidget(BarState(value=1.0, width=5, style="solid"))
        result = widget.project(RenderTarget.CLI)
        assert result == "█████"

    def test_project_cli_partial_bar(self) -> None:
        """Partial bar shows mix of filled/empty."""
        widget = BarWidget(BarState(value=0.5, width=10, style="solid"))
        result = widget.project(RenderTarget.CLI)
        # 50% of 10 = 5 filled
        assert len(result) == 10
        assert result.count("█") == 5
        assert result.count("░") == 5

    def test_project_cli_with_label(self) -> None:
        """CLI projection includes label when set."""
        widget = BarWidget(BarState(value=0.5, width=5, label="CPU"))
        result = widget.project(RenderTarget.CLI)
        assert result.startswith("CPU: ")

    def test_project_cli_vertical(self) -> None:
        """Vertical bar uses newlines."""
        widget = BarWidget(
            BarState(value=0.5, width=4, orientation="vertical", style="solid")
        )
        result = widget.project(RenderTarget.CLI)
        assert "\n" in result
        lines = result.split("\n")
        assert len(lines) == 4


class TestBarProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = BarWidget(BarState(value=0.5))
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes basic fields."""
        widget = BarWidget(BarState(value=0.75, width=20, style="gradient"))
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "bar"
        assert result["value"] == 0.75
        assert result["width"] == 20
        assert result["style"] == "gradient"

    def test_project_json_includes_glyphs(self) -> None:
        """JSON projection includes glyph array."""
        widget = BarWidget(BarState(value=0.5, width=10))
        result = widget.project(RenderTarget.JSON)

        assert "glyphs" in result
        assert len(result["glyphs"]) == 10
        assert all(g["type"] == "glyph" for g in result["glyphs"])


class TestBarProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = BarWidget(BarState(value=0.5))
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        widget = BarWidget(BarState(value=0.5))
        result = widget.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-bar" in result
        assert "<span" in result

    def test_project_marimo_vertical_flex_direction(self) -> None:
        """Vertical bar uses column flex direction."""
        widget = BarWidget(BarState(value=0.5, orientation="vertical"))
        result = widget.project(RenderTarget.MARIMO)
        assert "flex-direction: column" in result

    def test_project_marimo_horizontal_flex_direction(self) -> None:
        """Horizontal bar uses row flex direction."""
        widget = BarWidget(BarState(value=0.5, orientation="horizontal"))
        result = widget.project(RenderTarget.MARIMO)
        assert "flex-direction: row" in result


class TestBarProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_rich_text(self) -> None:
        """TUI projection returns Rich Text (when available)."""
        widget = BarWidget(BarState(value=0.5, width=10))
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            assert isinstance(result, Text)
            assert len(str(result)) == 10
        except ImportError:
            # Fallback to string if rich not available
            assert isinstance(result, str)


class TestBarStyles:
    """Tests for different bar styles."""

    def test_solid_style(self) -> None:
        """Solid style uses block chars."""
        widget = BarWidget(BarState(value=0.5, width=4, style="solid"))
        result = widget.project(RenderTarget.CLI)
        assert "█" in result
        assert "░" in result

    def test_segments_style(self) -> None:
        """Segments style uses circle chars."""
        widget = BarWidget(BarState(value=0.5, width=4, style="segments"))
        result = widget.project(RenderTarget.CLI)
        assert "●" in result
        assert "○" in result

    def test_dots_style(self) -> None:
        """Dots style uses dot chars."""
        widget = BarWidget(BarState(value=0.5, width=4, style="dots"))
        result = widget.project(RenderTarget.CLI)
        assert "◉" in result
        assert "·" in result


class TestBarDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = BarState(value=0.5, width=10, entropy=0.3, seed=42, t=1000.0)

        widget1 = BarWidget(state)
        widget2 = BarWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        assert widget1.project(RenderTarget.JSON) == widget2.project(RenderTarget.JSON)
