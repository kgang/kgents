"""Tests for YieldCardWidget - agent output/yield display."""

from __future__ import annotations

import pytest
from agents.i.reactive.primitives.yield_card import (
    YIELD_GLYPHS,
    YIELD_GLYPHS_ASCII,
    YieldCardState,
    YieldCardWidget,
)
from agents.i.reactive.widget import RenderTarget


class TestYieldCardState:
    """Tests for YieldCardState immutable state."""

    def test_default_state(self) -> None:
        """Default YieldCardState has expected values."""
        state = YieldCardState()
        assert state.yield_id == "yield"
        assert state.source_agent == "agent"
        assert state.yield_type == "yield"
        assert state.content == ""
        assert state.importance == 0.5
        assert state.entropy == 0.0
        assert state.max_content_length == 50
        assert state.use_emoji is True

    def test_state_is_frozen(self) -> None:
        """YieldCardState is immutable (frozen dataclass)."""
        state = YieldCardState(content="test")
        with pytest.raises(Exception):
            state.content = "modified"  # type: ignore[misc]

    def test_state_with_all_fields(self) -> None:
        """YieldCardState can be created with all fields."""
        state = YieldCardState(
            yield_id="yield-001",
            source_agent="kgent-1",
            yield_type="action",
            content="Executing query...",
            importance=0.9,
            timestamp=1702500000.0,
            entropy=0.3,
            seed=42,
            t=1000.0,
            max_content_length=100,
            use_emoji=False,
        )
        assert state.yield_id == "yield-001"
        assert state.source_agent == "kgent-1"
        assert state.yield_type == "action"
        assert state.content == "Executing query..."
        assert state.importance == 0.9
        assert state.use_emoji is False


class TestYieldCardWidget:
    """Tests for YieldCardWidget reactive widget."""

    def test_create_with_default_state(self) -> None:
        """YieldCardWidget can be created with default state."""
        widget = YieldCardWidget()
        assert widget.state.value == YieldCardState()

    def test_create_with_initial_state(self) -> None:
        """YieldCardWidget can be created with initial state."""
        state = YieldCardState(content="Test content", importance=0.8)
        widget = YieldCardWidget(state)
        assert widget.state.value.content == "Test content"
        assert widget.state.value.importance == 0.8

    def test_has_composed_slots(self) -> None:
        """YieldCardWidget has type_glyph and importance slots."""
        widget = YieldCardWidget()
        assert "type_glyph" in widget.slots
        assert "importance" in widget.slots

    def test_with_content_returns_new_widget(self) -> None:
        """with_content() returns new widget, doesn't mutate original."""
        original = YieldCardWidget(YieldCardState(content="original"))
        updated = original.with_content("updated")

        assert original.state.value.content == "original"
        assert updated.state.value.content == "updated"

    def test_with_importance_returns_new_widget(self) -> None:
        """with_importance() returns new widget."""
        original = YieldCardWidget(YieldCardState(importance=0.5))
        updated = original.with_importance(0.9)

        assert original.state.value.importance == 0.5
        assert updated.state.value.importance == 0.9

    def test_with_importance_clamps(self) -> None:
        """with_importance() clamps to 0.0-1.0 range."""
        widget = YieldCardWidget()
        assert widget.with_importance(-0.5).state.value.importance == 0.0
        assert widget.with_importance(1.5).state.value.importance == 1.0

    def test_with_type_returns_new_widget(self) -> None:
        """with_type() returns new widget."""
        original = YieldCardWidget(YieldCardState(yield_type="yield"))
        updated = original.with_type("action")

        assert original.state.value.yield_type == "yield"
        assert updated.state.value.yield_type == "action"

    def test_with_time_returns_new_widget(self) -> None:
        """with_time() returns new widget."""
        original = YieldCardWidget(YieldCardState(t=0.0))
        updated = original.with_time(1000.0)

        assert original.state.value.t == 0.0
        assert updated.state.value.t == 1000.0

    def test_with_entropy_returns_new_widget(self) -> None:
        """with_entropy() returns new widget."""
        original = YieldCardWidget(YieldCardState(entropy=0.0))
        updated = original.with_entropy(0.5)

        assert original.state.value.entropy == 0.0
        assert updated.state.value.entropy == 0.5


class TestYieldCardContentTruncation:
    """Tests for content truncation."""

    def test_short_content_not_truncated(self) -> None:
        """Short content is not truncated."""
        widget = YieldCardWidget(YieldCardState(content="Short", max_content_length=50))
        result = widget.project(RenderTarget.CLI)
        assert "Short" in result
        assert "..." not in result

    def test_long_content_truncated(self) -> None:
        """Long content is truncated with ellipsis."""
        long_content = "A" * 100
        widget = YieldCardWidget(
            YieldCardState(content=long_content, max_content_length=50)
        )
        result = widget.project(RenderTarget.CLI)
        assert "..." in result
        # Should be max_content_length chars total (including ...)
        assert len(result.split("\n")[0]) < len(long_content) + 10

    def test_exact_length_not_truncated(self) -> None:
        """Content exactly at max length is not truncated."""
        content = "A" * 50
        widget = YieldCardWidget(YieldCardState(content=content, max_content_length=50))
        result = widget.project(RenderTarget.CLI)
        assert "..." not in result


class TestYieldCardProjectCLI:
    """Tests for CLI projection."""

    def test_project_cli_returns_string(self) -> None:
        """CLI projection returns string."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.CLI)
        assert isinstance(result, str)

    def test_project_cli_includes_content(self) -> None:
        """CLI projection includes content."""
        widget = YieldCardWidget(YieldCardState(content="Test content"))
        result = widget.project(RenderTarget.CLI)
        assert "Test content" in result

    def test_project_cli_type_glyphs_emoji(self) -> None:
        """CLI projection uses correct type glyphs with emoji."""
        for yield_type, glyph in YIELD_GLYPHS.items():
            widget = YieldCardWidget(
                YieldCardState(yield_type=yield_type, use_emoji=True)
            )
            result = widget.project(RenderTarget.CLI)
            assert glyph in result

    def test_project_cli_type_glyphs_ascii(self) -> None:
        """CLI projection uses correct type glyphs in ASCII mode."""
        for yield_type, glyph in YIELD_GLYPHS_ASCII.items():
            widget = YieldCardWidget(
                YieldCardState(yield_type=yield_type, use_emoji=False)
            )
            result = widget.project(RenderTarget.CLI)
            assert glyph in result

    def test_project_cli_low_importance_no_bar(self) -> None:
        """Low importance yields don't show importance bar."""
        widget = YieldCardWidget(YieldCardState(importance=0.2, content="Test"))
        result = widget.project(RenderTarget.CLI)
        # Should be single line (no bar)
        assert "\n" not in result

    def test_project_cli_high_importance_shows_bar(self) -> None:
        """High importance yields show importance bar."""
        widget = YieldCardWidget(YieldCardState(importance=0.8, content="Test"))
        result = widget.project(RenderTarget.CLI)
        # Should be multi-line (with bar)
        assert "\n" in result


class TestYieldCardProjectJSON:
    """Tests for JSON projection."""

    def test_project_json_returns_dict(self) -> None:
        """JSON projection returns dict."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.JSON)
        assert isinstance(result, dict)

    def test_project_json_type_field(self) -> None:
        """JSON projection has type field."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.JSON)
        assert result["type"] == "yield_card"

    def test_project_json_basic_fields(self) -> None:
        """JSON projection includes all basic fields."""
        widget = YieldCardWidget(
            YieldCardState(
                yield_id="yield-001",
                source_agent="kgent-1",
                yield_type="action",
                content="Test content",
                importance=0.75,
            )
        )
        result = widget.project(RenderTarget.JSON)

        assert result["yield_id"] == "yield-001"
        assert result["source_agent"] == "kgent-1"
        assert result["yield_type"] == "action"
        assert result["content"] == "Test content"
        assert result["importance"] == 0.75

    def test_project_json_includes_content_preview(self) -> None:
        """JSON projection includes truncated content preview."""
        long_content = "A" * 100
        widget = YieldCardWidget(
            YieldCardState(content=long_content, max_content_length=50)
        )
        result = widget.project(RenderTarget.JSON)

        assert "content" in result
        assert "content_preview" in result
        assert result["content"] == long_content
        assert len(result["content_preview"]) <= 50

    def test_project_json_includes_children(self) -> None:
        """JSON projection includes child widget projections."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.JSON)

        assert "children" in result
        assert "type_glyph" in result["children"]
        assert "importance" in result["children"]

    def test_project_json_distortion_on_high_entropy(self) -> None:
        """JSON projection includes distortion when entropy > 0.1."""
        widget = YieldCardWidget(YieldCardState(entropy=0.5))
        result = widget.project(RenderTarget.JSON)
        assert "distortion" in result


class TestYieldCardProjectMarimo:
    """Tests for marimo/HTML projection."""

    def test_project_marimo_returns_string(self) -> None:
        """Marimo projection returns HTML string."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.MARIMO)
        assert isinstance(result, str)

    def test_project_marimo_is_html(self) -> None:
        """Marimo projection is HTML structure."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.MARIMO)
        assert "<div" in result
        assert "kgents-yield-card" in result

    def test_project_marimo_includes_yield_id(self) -> None:
        """Marimo projection includes yield ID as data attribute."""
        widget = YieldCardWidget(YieldCardState(yield_id="test-yield"))
        result = widget.project(RenderTarget.MARIMO)
        assert 'data-yield-id="test-yield"' in result

    def test_project_marimo_includes_source_agent(self) -> None:
        """Marimo projection includes source agent reference."""
        widget = YieldCardWidget(YieldCardState(source_agent="kgent-1"))
        result = widget.project(RenderTarget.MARIMO)
        assert "kgent-1" in result

    def test_project_marimo_high_importance_styling(self) -> None:
        """High importance yields have different styling."""
        low_widget = YieldCardWidget(YieldCardState(importance=0.3))
        high_widget = YieldCardWidget(YieldCardState(importance=0.9))

        low_result = low_widget.project(RenderTarget.MARIMO)
        high_result = high_widget.project(RenderTarget.MARIMO)

        # High importance should have different border color
        assert "#666" in low_result  # Default border
        assert "#f80" in high_result  # Emphasized border


class TestYieldCardProjectTUI:
    """Tests for TUI/Textual projection."""

    def test_project_tui_returns_text_or_fallback(self) -> None:
        """TUI projection returns Rich Text (when available)."""
        widget = YieldCardWidget()
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            assert isinstance(result, Text)
        except ImportError:
            # Fallback to string if rich not available
            assert isinstance(result, str)

    def test_project_tui_includes_source_reference(self) -> None:
        """TUI projection includes source agent in dim style."""
        widget = YieldCardWidget(YieldCardState(source_agent="test-agent"))
        result = widget.project(RenderTarget.TUI)

        try:
            from rich.text import Text

            if isinstance(result, Text):
                text_str = str(result)
                assert "test-agent" in text_str
        except ImportError:
            pass


class TestYieldCardComposition:
    """Tests verifying proper composition from Wave 1-2 primitives."""

    def test_slots_are_correct_types(self) -> None:
        """Verify slots contain correct widget types."""
        from agents.i.reactive.primitives.bar import BarWidget
        from agents.i.reactive.primitives.glyph import GlyphWidget

        widget = YieldCardWidget()
        # Force rebuild
        widget.project(RenderTarget.CLI)

        assert isinstance(widget.slots["type_glyph"], GlyphWidget)
        assert isinstance(widget.slots["importance"], BarWidget)

    def test_entropy_flows_to_children(self) -> None:
        """Entropy value propagates to child widgets."""
        widget = YieldCardWidget(YieldCardState(entropy=0.5))
        # Force rebuild
        widget.project(RenderTarget.CLI)

        # Note: glyph entropy is boosted by importance
        importance_state = widget.slots["importance"].state.value  # type: ignore[attr-defined]
        assert importance_state.entropy == 0.5

    def test_importance_affects_glyph_entropy(self) -> None:
        """High importance boosts glyph entropy for emphasis."""
        widget = YieldCardWidget(YieldCardState(entropy=0.0, importance=0.8))
        # Force rebuild
        widget.project(RenderTarget.CLI)

        glyph_state = widget.slots["type_glyph"].state.value  # type: ignore[attr-defined]
        # entropy + importance * 0.2
        assert glyph_state.entropy == pytest.approx(0.16)

    def test_time_flows_to_children(self) -> None:
        """Time value propagates to child widgets."""
        widget = YieldCardWidget(YieldCardState(t=1000.0))
        # Force rebuild
        widget.project(RenderTarget.CLI)

        glyph_state = widget.slots["type_glyph"].state.value  # type: ignore[attr-defined]
        importance_state = widget.slots["importance"].state.value  # type: ignore[attr-defined]

        assert glyph_state.t == 1000.0
        assert importance_state.t == 1000.0


class TestYieldCardDeterminism:
    """Tests for deterministic rendering."""

    def test_same_state_same_output(self) -> None:
        """Same state always produces same output."""
        state = YieldCardState(
            yield_id="test-yield",
            source_agent="test-agent",
            yield_type="action",
            content="Test content here",
            importance=0.75,
            entropy=0.3,
            seed=42,
            t=1000.0,
        )

        widget1 = YieldCardWidget(state)
        widget2 = YieldCardWidget(state)

        assert widget1.project(RenderTarget.CLI) == widget2.project(RenderTarget.CLI)
        assert widget1.project(RenderTarget.JSON) == widget2.project(RenderTarget.JSON)
        assert widget1.project(RenderTarget.MARIMO) == widget2.project(
            RenderTarget.MARIMO
        )


class TestYieldTypes:
    """Tests for different yield types."""

    def test_thought_type(self) -> None:
        """Thought type uses thought glyph."""
        widget = YieldCardWidget(YieldCardState(yield_type="thought", use_emoji=True))
        result = widget.project(RenderTarget.CLI)
        assert "💭" in result

    def test_action_type(self) -> None:
        """Action type uses action glyph."""
        widget = YieldCardWidget(YieldCardState(yield_type="action", use_emoji=True))
        result = widget.project(RenderTarget.CLI)
        assert "⚡" in result

    def test_artifact_type(self) -> None:
        """Artifact type uses artifact glyph."""
        widget = YieldCardWidget(YieldCardState(yield_type="artifact", use_emoji=True))
        result = widget.project(RenderTarget.CLI)
        assert "📦" in result

    def test_error_type(self) -> None:
        """Error type uses error glyph."""
        widget = YieldCardWidget(YieldCardState(yield_type="error", use_emoji=True))
        result = widget.project(RenderTarget.CLI)
        assert "⚠" in result
