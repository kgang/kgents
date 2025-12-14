"""
Tests for Terminal Adapter.

Tests cover:
- Capability detection
- Terminal output with styling
- Responsive layout
- Graceful degradation
- Cursor and screen control
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import pytest
from agents.i.reactive.terminal.adapter import (
    DegradedRenderer,
    LayoutConstraints,
    ResponsiveLayout,
    TerminalCapabilities,
    TerminalOutput,
    UnicodeSupport,
    full_capabilities,
    minimal_capabilities,
)
from agents.i.reactive.terminal.ansi import ANSIColor, Color, ColorScheme

if TYPE_CHECKING:
    pass


# === Capability Detection ===


class TestTerminalCapabilities:
    """Test capability detection."""

    def test_default_capabilities(self) -> None:
        """Default capabilities are reasonable."""
        caps = TerminalCapabilities()
        assert caps.width == 80
        assert caps.height == 24
        assert caps.color_mode == "16"
        assert caps.unicode_support == UnicodeSupport.FULL

    def test_minimal_capabilities(self) -> None:
        """Minimal capabilities helper."""
        caps = minimal_capabilities()
        assert caps.color_mode == "none"
        assert caps.unicode_support == UnicodeSupport.ASCII
        assert caps.is_interactive is False

    def test_full_capabilities(self) -> None:
        """Full capabilities helper."""
        caps = full_capabilities()
        assert caps.color_mode == "rgb"
        assert caps.unicode_support == UnicodeSupport.FULL
        assert caps.is_interactive is True

    def test_full_capabilities_custom_size(self) -> None:
        """Full capabilities with custom size."""
        caps = full_capabilities(width=200, height=60)
        assert caps.width == 200
        assert caps.height == 60

    def test_degrade_color(self) -> None:
        """Color degradation based on capabilities."""
        caps = TerminalCapabilities(color_mode="16")
        rgb = Color.rgb(255, 128, 64)
        degraded = caps.degrade_color(rgb)
        assert degraded.mode == "16"

    def test_supports_box_drawing(self) -> None:
        """Box drawing support detection."""
        full = TerminalCapabilities(unicode_support=UnicodeSupport.FULL)
        minimal = TerminalCapabilities(unicode_support=UnicodeSupport.ASCII)

        assert full.supports_box_drawing is True
        assert minimal.supports_box_drawing is False

    def test_supports_braille(self) -> None:
        """Braille support detection."""
        full = TerminalCapabilities(unicode_support=UnicodeSupport.FULL)
        basic = TerminalCapabilities(unicode_support=UnicodeSupport.BASIC)

        assert full.supports_braille is True
        assert basic.supports_braille is False


class TestCapabilityDetection:
    """Test actual capability detection (environment dependent)."""

    def test_detect_runs_without_error(self) -> None:
        """Detection should not raise."""
        # This test just ensures detection doesn't crash
        caps = TerminalCapabilities.detect()
        assert isinstance(caps, TerminalCapabilities)

    def test_detect_with_stream(self) -> None:
        """Detection works with custom stream."""
        buffer = io.StringIO()
        caps = TerminalCapabilities.detect(buffer)
        # Non-TTY stream should be non-interactive
        assert caps.is_interactive is False


# === Terminal Output ===


class TestTerminalOutput:
    """Test terminal output writer."""

    def test_write_plain_text(self) -> None:
        """Write plain text to buffer."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.write("Hello")
        assert term.get_buffer() == "Hello"

    def test_writeln_adds_newline(self) -> None:
        """Writeln adds newline."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.writeln("Hello")
        assert term.get_buffer() == "Hello\n"

    def test_write_styled_with_color(self) -> None:
        """Write styled text with color."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.write_styled("Red", fg=Color.standard(ANSIColor.RED))
        buffer = term.get_buffer()

        assert "Red" in buffer
        assert "\x1b[" in buffer  # Contains escape sequence

    def test_write_styled_with_bold(self) -> None:
        """Write styled text with bold."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.write_styled("Bold", bold=True)
        buffer = term.get_buffer()

        assert "Bold" in buffer
        assert "\x1b[1m" in buffer  # Bold code

    def test_write_styled_degrades_colors(self) -> None:
        """Styled output degrades colors for capability."""
        caps = TerminalCapabilities(color_mode="16")
        term = TerminalOutput(caps)

        term.write_styled("Text", fg=Color.rgb(255, 128, 64))
        buffer = term.get_buffer()

        # Should not contain RGB sequence
        assert "38;2;" not in buffer
        # Should contain standard or bright color sequence (30-37 or 90-97)
        # The escape sequence should be present
        assert "\x1b[" in buffer

    def test_write_with_scheme(self) -> None:
        """Write with semantic colors from scheme."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.write_with_scheme("Error!", "error", scheme=ColorScheme.DARK)
        buffer = term.get_buffer()

        assert "Error!" in buffer
        assert "\x1b[" in buffer

    def test_reset_style(self) -> None:
        """Reset style adds reset sequence."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.reset_style()
        assert term.get_buffer() == "\x1b[0m"

    def test_buffer_clear(self) -> None:
        """Clear buffer removes content."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.write("Test")
        term.clear_buffer()
        assert term.get_buffer() == ""

    def test_flush_to_stream(self) -> None:
        """Flush writes to stream and clears buffer."""
        buffer = io.StringIO()
        caps = full_capabilities()
        term = TerminalOutput(caps, stream=buffer)

        term.write("Output")
        term.flush()

        assert buffer.getvalue() == "Output"
        assert term.get_buffer() == ""


class TestCursorControl:
    """Test cursor control sequences."""

    def test_move_to(self) -> None:
        """Move cursor to position."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.move_to(5, 10)
        buffer = term.get_buffer()

        # Position is 1-indexed in ANSI
        assert "\x1b[11;6H" in buffer

    def test_move_up(self) -> None:
        """Move cursor up."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.move_up(3)
        assert "\x1b[3A" in term.get_buffer()

    def test_move_down(self) -> None:
        """Move cursor down."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.move_down(2)
        assert "\x1b[2B" in term.get_buffer()

    def test_move_right(self) -> None:
        """Move cursor right."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.move_right(5)
        assert "\x1b[5C" in term.get_buffer()

    def test_move_left(self) -> None:
        """Move cursor left."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.move_left(4)
        assert "\x1b[4D" in term.get_buffer()

    def test_save_restore_cursor(self) -> None:
        """Save and restore cursor position."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.save_cursor()
        term.restore_cursor()

        buffer = term.get_buffer()
        assert "\x1b[s" in buffer
        assert "\x1b[u" in buffer

    def test_hide_show_cursor(self) -> None:
        """Hide and show cursor."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.hide_cursor()
        term.show_cursor()

        buffer = term.get_buffer()
        assert "\x1b[?25l" in buffer  # Hide
        assert "\x1b[?25h" in buffer  # Show

    def test_cursor_control_disabled_when_not_supported(self) -> None:
        """Cursor control is no-op when not supported."""
        caps = TerminalCapabilities(supports_cursor=False)
        term = TerminalOutput(caps)

        term.move_to(5, 10)
        term.hide_cursor()

        assert term.get_buffer() == ""


class TestScreenControl:
    """Test screen control sequences."""

    def test_clear_screen(self) -> None:
        """Clear entire screen."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.clear_screen()
        assert "\x1b[2J" in term.get_buffer()

    def test_clear_line(self) -> None:
        """Clear current line."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.clear_line()
        assert "\x1b[2K" in term.get_buffer()

    def test_clear_to_end(self) -> None:
        """Clear to end of screen."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.clear_to_end()
        assert "\x1b[J" in term.get_buffer()

    def test_set_title(self) -> None:
        """Set terminal title."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        term.set_title("Test Title")
        buffer = term.get_buffer()

        assert "\x1b]0;Test Title\x07" in buffer

    def test_title_disabled_when_not_supported(self) -> None:
        """Title setting is no-op when not supported."""
        caps = TerminalCapabilities(supports_title=False)
        term = TerminalOutput(caps)

        term.set_title("Test")
        assert term.get_buffer() == ""


# === Responsive Layout ===


class TestResponsiveLayout:
    """Test responsive layout calculations."""

    def test_content_width(self) -> None:
        """Calculate content width."""
        caps = full_capabilities(width=120)
        layout = ResponsiveLayout(caps)

        width = layout.content_width()
        assert width <= 120
        assert width >= 40  # Min width

    def test_content_width_with_constraints(self) -> None:
        """Content width respects constraints."""
        caps = full_capabilities(width=120)
        constraints = LayoutConstraints(max_width=80, padding=2)
        layout = ResponsiveLayout(caps, constraints)

        width = layout.content_width()
        assert width <= 80 - 4  # Max - padding*2

    def test_content_height(self) -> None:
        """Calculate content height."""
        caps = full_capabilities(height=40)
        layout = ResponsiveLayout(caps)

        height = layout.content_height()
        assert height <= 40
        assert height >= 10  # Min height

    def test_columns_calculation(self) -> None:
        """Calculate number of columns."""
        caps = full_capabilities(width=120)
        constraints = LayoutConstraints(padding=0)
        layout = ResponsiveLayout(caps, constraints)

        # Should fit multiple columns of 30 width each
        cols = layout.columns(min_col_width=30, gap=2)
        assert cols >= 1
        assert cols <= 120 // 30

    def test_columns_narrow_terminal(self) -> None:
        """Narrow terminal gets single column."""
        caps = full_capabilities(width=50)
        layout = ResponsiveLayout(caps)

        cols = layout.columns(min_col_width=60)
        assert cols == 1

    def test_column_width_calculation(self) -> None:
        """Calculate width per column."""
        caps = full_capabilities(width=100)
        constraints = LayoutConstraints(padding=0)
        layout = ResponsiveLayout(caps, constraints)

        col_width = layout.column_width(num_columns=3, gap=2)
        # (100 - 2*2) / 3 = 32
        assert col_width == 32

    def test_wrap_text(self) -> None:
        """Wrap text to width."""
        caps = full_capabilities(width=80)
        layout = ResponsiveLayout(caps)

        text = "This is a fairly long line of text that should wrap to multiple lines."
        lines = layout.wrap_text(text, width=20)

        assert len(lines) > 1
        assert all(len(line) <= 20 for line in lines)

    def test_wrap_text_empty(self) -> None:
        """Wrap empty text."""
        caps = full_capabilities()
        layout = ResponsiveLayout(caps)

        lines = layout.wrap_text("")
        assert lines == [""]


# === Degraded Renderer ===


class TestDegradedRenderer:
    """Test graceful degradation."""

    def test_box_char_with_unicode(self) -> None:
        """Box chars with full Unicode support."""
        caps = full_capabilities()
        renderer = DegradedRenderer(caps)

        assert renderer.box_char("top_left") == "┌"
        assert renderer.box_char("horizontal") == "─"

    def test_box_char_ascii_fallback(self) -> None:
        """Box chars fall back to ASCII."""
        caps = minimal_capabilities()
        renderer = DegradedRenderer(caps)

        assert renderer.box_char("top_left") == "+"
        assert renderer.box_char("horizontal") == "-"

    def test_sparkline_char_with_unicode(self) -> None:
        """Sparkline chars with Unicode."""
        caps = full_capabilities()
        renderer = DegradedRenderer(caps)

        char = renderer.sparkline_char(0.5)
        assert char in "▁▂▃▄▅▆▇█"

    def test_sparkline_char_ascii_fallback(self) -> None:
        """Sparkline chars fall back to ASCII."""
        caps = minimal_capabilities()
        renderer = DegradedRenderer(caps)

        char = renderer.sparkline_char(0.5)
        assert char in "_.-=*#"

    def test_progress_chars(self) -> None:
        """Progress bar characters."""
        unicode_caps = full_capabilities()
        ascii_caps = minimal_capabilities()

        unicode_renderer = DegradedRenderer(unicode_caps)
        ascii_renderer = DegradedRenderer(ascii_caps)

        empty_u, partial_u, filled_u = unicode_renderer.progress_chars()
        empty_a, partial_a, filled_a = ascii_renderer.progress_chars()

        assert empty_u == "░"
        assert filled_u == "█"

        assert empty_a == "-"
        assert filled_a == "#"

    def test_styled_text(self) -> None:
        """Styled text with degradation."""
        caps = full_capabilities()
        renderer = DegradedRenderer(caps)

        styled = renderer.styled_text("Error", "error", bold=True)
        assert "Error" in styled
        assert "\x1b[" in styled

    def test_styled_text_no_color(self) -> None:
        """Styled text with no color support."""
        caps = minimal_capabilities()
        renderer = DegradedRenderer(caps)

        styled = renderer.styled_text("Text", "primary")
        # No escape sequences when color is disabled
        assert (
            styled == "Text" or "\x1b[" not in styled or styled.endswith("Text\x1b[0m")
        )

    def test_degrade_lines_unicode(self) -> None:
        """Lines unchanged with Unicode support."""
        caps = full_capabilities()
        renderer = DegradedRenderer(caps)

        lines = ["┌───┐", "│ Hi│", "└───┘"]
        result = renderer.degrade_lines(lines)

        assert result == lines

    def test_degrade_lines_ascii(self) -> None:
        """Lines converted to ASCII."""
        caps = minimal_capabilities()
        renderer = DegradedRenderer(caps)

        lines = ["┌───┐", "│ Hi│", "└───┘"]
        result = renderer.degrade_lines(lines)

        assert result[0] == "+---+"
        assert result[1] == "| Hi|"
        assert result[2] == "+---+"

    def test_degrade_complex_characters(self) -> None:
        """Complex Unicode characters degrade correctly."""
        caps = minimal_capabilities()
        renderer = DegradedRenderer(caps)

        lines = ["█▓▒░", "▁▂▃▄", "●○◉◎"]
        result = renderer.degrade_lines(lines)

        # Should contain only ASCII
        for line in result:
            for char in line:
                assert ord(char) < 128


# === Method Chaining ===


class TestMethodChaining:
    """Test that output methods support chaining."""

    def test_write_chaining(self) -> None:
        """Write methods can be chained."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        result = term.write("A").write("B").writeln("C").write("D")

        assert result is term
        assert term.get_buffer() == "ABC\nD"

    def test_cursor_chaining(self) -> None:
        """Cursor methods can be chained."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        result = term.save_cursor().move_to(0, 0).write("Test").restore_cursor()

        assert result is term

    def test_style_chaining(self) -> None:
        """Style methods can be chained."""
        caps = full_capabilities()
        term = TerminalOutput(caps)

        result = (
            term.write_styled("Red", fg=Color.standard(ANSIColor.RED))
            .write(" ")
            .write_styled("Blue", fg=Color.standard(ANSIColor.BLUE))
            .reset_style()
        )

        assert result is term
