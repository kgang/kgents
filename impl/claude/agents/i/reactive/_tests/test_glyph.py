"""Tests for GlyphWidget - the atomic visual unit."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.glyph import GlyphState, GlyphWidget
from agents.i.reactive.widget import RenderTarget


class TestGlyphState:
    """Tests for GlyphState immutable state."""

    def test_default_state(self) -> None:
        """Default GlyphState has expected values."""
        state = GlyphState()
        assert state.char == "·"
        assert state.fg is None
        assert state.bg is None
        assert state.phase is None
        assert state.entropy == 0.0
        assert state.seed == 0
        assert state.t == 0.0
        assert state.animate == "none"

    def test_state_is_frozen(self) -> None:
        """GlyphState is immutable (frozen dataclass)."""
        state = GlyphState(char="◉")
        with pytest.raises(Exception):
            state.char = "○"  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """GlyphState can be created with all fields."""
        state = GlyphState(
            char="◉",
            fg="#ff0000",
            bg="#000000",
            phase="active",
            entropy=0.5,
            seed=42,
            t=1000.0,
            animate="pulse",
        )
        assert state.char == "◉"
        assert state.fg == "#ff0000"
        assert state.bg == "#000000"
        assert state.phase == "active"
        assert state.entropy == 0.5
        assert state.seed == 42
        assert state.t == 1000.0
        assert state.animate == "pulse"


class TestGlyphWidget:
    """Tests for GlyphWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """GlyphWidget can be created with default state."""
        widget = GlyphWidget()
        assert widget.state.value == GlyphState()

    def test_create_with_initial_state(self) -> None:
        """GlyphWidget can be created with initial state."""
        state = GlyphState(char="◉", phase="active")
        widget = GlyphWidget(state)
        assert widget.state.value.char == "◉"
        assert widget.state.value.phase == "active"

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget, doesn't mutate original."""
        original = GlyphWidget(GlyphState(char="○", t=0.0))
        updated = original.with_time(1000.0)

        # Original unchanged
        assert original.state.value.t == 0.0

        # New widget has updated time
        assert updated.state.value.t == 1000.0

        # Other fields preserved
        assert updated.state.value.char == "○"

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = GlyphWidget(GlyphState(char="○", entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5

    def test_with_phase_returns_new_widget(self) -> None:
        """with_phase() returns new widget."""
        original = GlyphWidget(GlyphState(char="○", phase="idle"))
        updated = original.with_phase("active")

        assert original.state.value.phase == "idle"
        assert updated.state.value.phase == "active"


class TestGlyphProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_returns_char(self) -> None:
        """CLI projection returns the character."""
        widget = GlyphWidget(GlyphState(char="◉"))
        assert widget.project(RenderTarget.CLI) == "◉"

    def test_project_cli_phase_resolves_char(self) -> None:
        """Phase resolves to glyph when char is default."""
        widget = GlyphWidget(GlyphState(char="·", phase="active"))
        assert widget.project(RenderTarget.CLI) == "◉"

    def test_project_cli_char_overrides_phase(self) -> None:
        """Explicit char overrides phase glyph."""
        widget = GlyphWidget(GlyphState(char="X", phase="active"))
        assert widget.project(RenderTarget.CLI) == "X"


class TestGlyphProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes basic fields."""
        widget = GlyphWidget(GlyphState(char="◉", phase="active", entropy=0.3))
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "glyph"
        assert result["char"] == "◉"
        assert result["phase"] == "active"
        assert result["entropy"] == 0.3

    def test_project_json_distortion_included(self) -> None:
        """JSON projection includes distortion when entropy > threshold."""
        widget = GlyphWidget(GlyphState(char="◉", entropy=0.5, seed=42))
        result = widget.project(RenderTarget.JSON)

        assert "distortion" in result
        assert result["distortion"] is not None
        assert "blur" in result["distortion"]
        assert "skew" in result["distortion"]

    def test_project_json_no_distortion_low_entropy(self) -> None:
        """JSON projection has no distortion for low entropy."""
        widget = GlyphWidget(GlyphState(char="◉", entropy=0.05))
        result = widget.project(RenderTarget.JSON)

        assert "distortion" not in result or result.get("distortion") is None

    def test_project_json_optional_fields(self) -> None:
        """JSON projection includes optional fields when set."""
        widget = GlyphWidget(GlyphState(char="◉", fg="#ff0000", bg="#000000"))
        result = widget.project(RenderTarget.JSON)

        assert result["fg"] == "#ff0000"
        assert result["bg"] == "#000000"


class TestGlyphProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html_span(self) -> None:
        """Marimo projection is HTML span element."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.MARIMO)
        assert result.startswith("<span")
        assert result.endswith("</span>")
        assert "◉" in result

    def test_project_marimo_includes_class(self) -> None:
        """Marimo projection includes kgents class."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.MARIMO)
        assert 'class="kgents-glyph' in result

    def test_project_marimo_animation_class(self) -> None:
        """Marimo projection includes animation class."""
        widget = GlyphWidget(GlyphState(char="◉", animate="pulse"))
        result = widget.project(RenderTarget.MARIMO)
        assert "glyph-pulse" in result

    def test_project_marimo_color_style(self) -> None:
        """Marimo projection includes color in style."""
        widget = GlyphWidget(GlyphState(char="◉", fg="#ff0000"))
        result = widget.project(RenderTarget.MARIMO)
        assert "color: #ff0000" in result


class TestGlyphProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_rich_text(self) -> None:
        """TUI projection returns Rich Text (when available)."""
        widget = GlyphWidget(GlyphState(char="◉"))
        result = widget.project(RenderTarget.TUI)

        # Try to import rich to check if it's available
        try:
            from rich.text import Text

            assert isinstance(result, Text)
            assert str(result) == "◉"
        except ImportError:
            # Fallback to string if rich not available
            assert result == "◉"

    def test_project_tui_with_style(self) -> None:
        """TUI projection includes styling."""
        widget = GlyphWidget(GlyphState(char="◉", fg="red", bg="black"))
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            assert isinstance(result, Text)
            # Rich Text stores style info
            style_str = str(result.style) if result.style else ""
            # Style should contain color info
            assert "red" in style_str or result.style is not None
        except ImportError:
            pytest.skip("Rich not available for TUI testing")


class TestGlyphDeterminism:
    """Tests for deterministic rendering (critical for reactive substrate)."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = GlyphState(char="◉", entropy=0.5, seed=42, t=1000.0)

        widget1 = GlyphWidget(state)
        widget2 = GlyphWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        assert widget1.project(RenderTarget.JSON) == widget2.project(RenderTarget.JSON)
        assert widget1.project(RenderTarget.MARIMO) == widget2.project(
            RenderTarget.MARIMO
        )

    def test_different_time_different_distortion(self) -> None:
        """Different time produces different distortion."""
        state1 = GlyphState(char="◉", entropy=0.5, seed=42, t=0.0)
        state2 = GlyphState(char="◉", entropy=0.5, seed=42, t=3141.59)

        json1 = GlyphWidget(state1).project(RenderTarget.JSON)
        json2 = GlyphWidget(state2).project(RenderTarget.JSON)

        # Distortions should differ
        assert json1["distortion"] != json2["distortion"]

    def test_entropy_threshold(self) -> None:
        """Distortion only applied above entropy threshold (0.1)."""
        low = GlyphWidget(GlyphState(entropy=0.05)).project(RenderTarget.JSON)
        high = GlyphWidget(GlyphState(entropy=0.5, seed=42)).project(RenderTarget.JSON)

        assert low.get("distortion") is None
        assert high.get("distortion") is not None
