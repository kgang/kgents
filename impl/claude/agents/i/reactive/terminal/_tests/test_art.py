"""
Tests for ASCII Art Primitives.

Tests cover:
- Horizontal and vertical bars
- Sparklines (standard and braille)
- Progress indicators
- Gauges
- Panels
- Composition helpers
"""

from __future__ import annotations

import pytest

from agents.i.reactive.terminal.art import (
    BarStyle,
    Gauge,
    HBar,
    Panel,
    ProgressBar,
    Sparkline,
    VBar,
    align_text,
    horizontal_concat,
    render_gauge,
    render_hbar,
    render_panel,
    render_progress,
    render_sparkline,
    render_vbar,
    spinner_frame,
    vertical_concat,
)

# === Horizontal Bars ===


class TestHorizontalBars:
    """Test horizontal bar rendering."""

    def test_empty_bar(self) -> None:
        """Bar at 0% value."""
        result = render_hbar(HBar(value=0.0, width=10))
        assert len(result) == 10
        assert "█" not in result  # No filled characters

    def test_full_bar(self) -> None:
        """Bar at 100% value."""
        result = render_hbar(HBar(value=1.0, width=10))
        assert len(result) == 10
        assert "█" in result or "#" in result

    def test_half_bar(self) -> None:
        """Bar at 50% value."""
        result = render_hbar(HBar(value=0.5, width=10))
        assert len(result) == 10

    def test_bar_width(self) -> None:
        """Bar respects width."""
        for width in [5, 10, 20, 50]:
            result = render_hbar(HBar(value=0.5, width=width))
            # Without value display, should match width
            assert len(result) == width

    def test_bar_clamps_value(self) -> None:
        """Values are clamped to 0-1."""
        result1 = render_hbar(HBar(value=-0.5, width=10))
        result2 = render_hbar(HBar(value=1.5, width=10))
        assert len(result1) == 10
        assert len(result2) == 10

    def test_bar_styles(self) -> None:
        """Different bar styles render."""
        for style in BarStyle:
            result = render_hbar(HBar(value=0.7, width=10, style=style))
            assert len(result) == 10

    def test_bar_with_value_display(self) -> None:
        """Bar can show percentage value."""
        result = render_hbar(HBar(value=0.75, width=10, show_value=True))
        assert "75%" in result

    def test_bar_custom_chars(self) -> None:
        """Bar with custom fill characters."""
        result = render_hbar(HBar(value=0.5, width=10, fill_char="X", empty_char="."))
        assert "X" in result
        assert "." in result


# === Vertical Bars ===


class TestVerticalBars:
    """Test vertical bar rendering."""

    def test_empty_vbar(self) -> None:
        """Vertical bar at 0%."""
        lines = render_vbar(VBar(value=0.0, height=5))
        assert len(lines) == 5
        # All should be empty characters
        assert "█" not in "".join(lines)

    def test_full_vbar(self) -> None:
        """Vertical bar at 100%."""
        lines = render_vbar(VBar(value=1.0, height=5))
        assert len(lines) == 5
        # All should be filled
        assert all("█" in line for line in lines)

    def test_half_vbar(self) -> None:
        """Vertical bar at 50%."""
        lines = render_vbar(VBar(value=0.5, height=4))
        assert len(lines) == 4

    def test_vbar_width(self) -> None:
        """Vertical bar respects width."""
        lines = render_vbar(VBar(value=0.5, height=4, width=3))
        assert all(len(line) == 3 for line in lines)


# === Sparklines ===


class TestSparklines:
    """Test sparkline rendering."""

    def test_empty_sparkline(self) -> None:
        """Empty sparkline shows placeholder."""
        result = render_sparkline(Sparkline(values=()))
        assert result == "─"

    def test_single_value_sparkline(self) -> None:
        """Single value sparkline."""
        result = render_sparkline(Sparkline(values=(0.5,)))
        assert len(result) == 1

    def test_sparkline_length_matches_values(self) -> None:
        """Sparkline length equals number of values."""
        values = (0.1, 0.3, 0.5, 0.7, 0.9)
        result = render_sparkline(Sparkline(values=values))
        assert len(result) == len(values)

    def test_sparkline_value_range(self) -> None:
        """Sparkline shows value progression."""
        result = render_sparkline(Sparkline(values=(0.0, 0.5, 1.0)))
        # First char should be lowest, last should be highest
        assert len(result) == 3

    def test_sparkline_auto_normalize(self) -> None:
        """Sparkline auto-normalizes values."""
        # Values outside 0-1 should still work
        result = render_sparkline(Sparkline(values=(10.0, 50.0, 100.0)))
        assert len(result) == 3

    def test_sparkline_custom_range(self) -> None:
        """Sparkline with custom min/max."""
        result = render_sparkline(Sparkline(values=(25.0, 50.0, 75.0), min_val=0.0, max_val=100.0))
        assert len(result) == 3

    def test_braille_sparkline(self) -> None:
        """Multi-row braille sparkline."""
        values = tuple(i / 10 for i in range(20))
        result = render_sparkline(Sparkline(values=values, height=2))

        # Should return list for multi-row
        assert isinstance(result, list)
        assert len(result) == 2


# === Progress Indicators ===


class TestProgressIndicators:
    """Test progress bar and spinner rendering."""

    def test_progress_bar_empty(self) -> None:
        """Progress bar at 0%."""
        result = render_progress(ProgressBar(value=0.0, width=20))
        assert len(result) > 0
        assert "0%" in result or "  0%" in result

    def test_progress_bar_full(self) -> None:
        """Progress bar at 100%."""
        result = render_progress(ProgressBar(value=1.0, width=20))
        assert "100%" in result

    def test_progress_bar_styles(self) -> None:
        """Different progress bar styles."""
        for style in ["solid", "thin", "dots", "blocks", "ascii"]:
            result = render_progress(ProgressBar(value=0.5, width=20, style=style))
            assert len(result) > 0

    def test_progress_bar_brackets(self) -> None:
        """Progress bar bracket styles."""
        square = render_progress(ProgressBar(value=0.5, width=20, bracket_style="square"))
        assert "[" in square

        round_bar = render_progress(ProgressBar(value=0.5, width=20, bracket_style="round"))
        assert "(" in round_bar

        angle = render_progress(ProgressBar(value=0.5, width=20, bracket_style="angle"))
        assert "<" in angle

        no_bracket = render_progress(ProgressBar(value=0.5, width=20, bracket_style="none"))
        assert "[" not in no_bracket

    def test_progress_bar_with_label(self) -> None:
        """Progress bar with label."""
        result = render_progress(ProgressBar(value=0.5, width=20, label="Loading"))
        assert "Loading" in result

    def test_progress_bar_without_percent(self) -> None:
        """Progress bar without percentage display."""
        result = render_progress(ProgressBar(value=0.5, width=20, show_percent=False))
        assert "%" not in result

    def test_spinner_frames(self) -> None:
        """Spinner returns different frames over time."""
        frames = set()
        for t in range(0, 1000, 100):
            frame = spinner_frame(t, style="dots")
            frames.add(frame)

        # Should have multiple different frames
        assert len(frames) > 1

    def test_spinner_styles(self) -> None:
        """Different spinner styles exist."""
        for style in ["dots", "classic", "arrows", "bounce", "blocks"]:
            frame = spinner_frame(0.0, style=style)
            assert len(frame) > 0


# === Gauges ===


class TestGauges:
    """Test gauge rendering."""

    def test_gauge_renders(self) -> None:
        """Gauge produces output."""
        lines = render_gauge(Gauge(value=0.5, width=11))
        assert len(lines) > 0

    def test_gauge_shows_value(self) -> None:
        """Gauge displays percentage."""
        lines = render_gauge(Gauge(value=0.75, width=15, show_value=True))
        combined = "\n".join(lines)
        assert "75%" in combined

    def test_gauge_with_label(self) -> None:
        """Gauge with label."""
        lines = render_gauge(Gauge(value=0.5, width=15, label="Speed"))
        combined = "\n".join(lines)
        assert "Speed" in combined

    def test_gauge_boundary_values(self) -> None:
        """Gauge at min and max values."""
        min_gauge = render_gauge(Gauge(value=0.0, width=11))
        max_gauge = render_gauge(Gauge(value=1.0, width=11))
        assert len(min_gauge) > 0
        assert len(max_gauge) > 0


# === Panels ===


class TestPanels:
    """Test panel rendering."""

    def test_simple_panel(self) -> None:
        """Render simple panel."""
        lines = render_panel(Panel(content=("Hello",)))
        assert len(lines) == 3  # content + borders
        assert "Hello" in "".join(lines)

    def test_panel_with_title(self) -> None:
        """Panel with title."""
        lines = render_panel(Panel(content=("Content",), title="Title"))
        assert "Title" in lines[0]

    def test_panel_with_multiple_lines(self) -> None:
        """Panel with multiple content lines."""
        content = ("Line 1", "Line 2", "Line 3")
        lines = render_panel(Panel(content=content))
        assert len(lines) == 5  # 3 content + 2 borders

    def test_panel_auto_width(self) -> None:
        """Panel auto-sizes to content."""
        short = render_panel(Panel(content=("Hi",)))
        long_panel = render_panel(Panel(content=("This is a longer line",)))

        # Longer content should produce wider panel
        assert len(long_panel[0]) > len(short[0])

    def test_panel_explicit_width(self) -> None:
        """Panel with explicit width."""
        lines = render_panel(Panel(content=("Hi",), width=30))
        assert len(lines[0]) == 30

    def test_panel_double_border(self) -> None:
        """Panel with double border."""
        lines = render_panel(Panel(content=("Test",), double_border=True))
        assert "═" in lines[0]


# === Composition Helpers ===


class TestCompositionHelpers:
    """Test composition helper functions."""

    def test_horizontal_concat_empty(self) -> None:
        """Horizontal concat of empty list."""
        result = horizontal_concat([])
        assert result == []

    def test_horizontal_concat_single(self) -> None:
        """Horizontal concat of single block."""
        block = ["ABC", "DEF"]
        result = horizontal_concat([block])
        assert result == block

    def test_horizontal_concat_multiple(self) -> None:
        """Horizontal concat of multiple blocks."""
        block1 = ["AA", "BB"]
        block2 = ["CC", "DD"]
        result = horizontal_concat([block1, block2], gap=1)

        assert len(result) == 2
        assert "AA" in result[0]
        assert "CC" in result[0]

    def test_horizontal_concat_different_heights(self) -> None:
        """Horizontal concat normalizes heights."""
        block1 = ["A", "B", "C"]
        block2 = ["X"]
        result = horizontal_concat([block1, block2])

        assert len(result) == 3  # Height of tallest block

    def test_vertical_concat_empty(self) -> None:
        """Vertical concat of empty list."""
        result = vertical_concat([])
        assert result == []

    def test_vertical_concat_single(self) -> None:
        """Vertical concat of single block."""
        block = ["Line 1", "Line 2"]
        result = vertical_concat([block])
        assert result == block

    def test_vertical_concat_multiple(self) -> None:
        """Vertical concat of multiple blocks."""
        block1 = ["Top"]
        block2 = ["Bottom"]
        result = vertical_concat([block1, block2])

        assert len(result) == 2
        assert result[0] == "Top"
        assert result[1] == "Bottom"

    def test_vertical_concat_with_gap(self) -> None:
        """Vertical concat with gap."""
        block1 = ["A"]
        block2 = ["B"]
        result = vertical_concat([block1, block2], gap=2)

        assert len(result) == 4  # 1 + 2 gap + 1
        assert result[0] == "A"
        assert result[3] == "B"


# === Text Alignment ===


class TestTextAlignment:
    """Test text alignment helper."""

    def test_align_left(self) -> None:
        """Left alignment."""
        result = align_text("Hi", 10, "left")
        assert result == "Hi        "
        assert len(result) == 10

    def test_align_right(self) -> None:
        """Right alignment."""
        result = align_text("Hi", 10, "right")
        assert result == "        Hi"
        assert len(result) == 10

    def test_align_center(self) -> None:
        """Center alignment."""
        result = align_text("Hi", 10, "center")
        assert result == "    Hi    "
        assert len(result) == 10

    def test_align_with_custom_fill(self) -> None:
        """Alignment with custom fill character."""
        result = align_text("X", 5, "center", fill=".")
        assert result == "..X.."

    def test_align_truncates_long_text(self) -> None:
        """Text longer than width is truncated."""
        result = align_text("Hello World", 5, "left")
        assert result == "Hello"
        assert len(result) == 5


# === Edge Cases ===


class TestEdgeCases:
    """Test edge cases."""

    def test_zero_width_bar(self) -> None:
        """Zero width bar."""
        result = render_hbar(HBar(value=0.5, width=0))
        assert result == ""

    def test_zero_height_vbar(self) -> None:
        """Zero height vertical bar."""
        lines = render_vbar(VBar(value=0.5, height=0))
        assert lines == []

    def test_negative_value_clamped(self) -> None:
        """Negative values are clamped."""
        result = render_hbar(HBar(value=-0.5, width=10))
        # Should render as empty
        assert len(result) == 10

    def test_value_over_100_clamped(self) -> None:
        """Values over 1.0 are clamped."""
        result = render_hbar(HBar(value=2.0, width=10))
        # Should render as full
        assert len(result) == 10

    def test_sparkline_all_same_values(self) -> None:
        """Sparkline with identical values."""
        result = render_sparkline(Sparkline(values=(0.5, 0.5, 0.5)))
        assert len(result) == 3
        # All characters should be the same
        assert len(set(result)) == 1
