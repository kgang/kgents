"""
Terminal Adapter: Size and capability detection for graceful degradation.

Pure detection of terminal capabilities. All state is immutable.
No side effects except when explicitly writing output.

Supports:
- Terminal size detection
- Color capability detection (16, 256, RGB, none)
- Unicode support detection
- Graceful degradation for limited terminals
- Cursor control and screen management

This is the bridge between abstract rendering and actual terminal output.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Literal, TextIO

from .ansi import (
    ANSISequence,
    Color,
    ColorMode,
    ColorScheme,
    SemanticColors,
    get_scheme,
)

if TYPE_CHECKING:
    pass


# === Capability Detection ===


class UnicodeSupport(Enum):
    """Level of Unicode support."""

    FULL = auto()  # All Unicode including box drawing
    BASIC = auto()  # Basic Unicode but limited box drawing
    ASCII = auto()  # ASCII only


@dataclass(frozen=True)
class TerminalCapabilities:
    """
    Detected terminal capabilities.

    Immutable snapshot of what the terminal supports.
    """

    width: int = 80
    height: int = 24
    color_mode: ColorMode = "16"
    unicode_support: UnicodeSupport = UnicodeSupport.FULL
    supports_cursor: bool = True
    supports_title: bool = True
    is_interactive: bool = True

    @classmethod
    def detect(cls, output: TextIO | None = None) -> TerminalCapabilities:
        """
        Detect capabilities from the current terminal.

        Uses environment variables and terminal queries.
        Falls back to safe defaults when detection fails.
        """
        stream = output or sys.stdout

        # Check if interactive
        is_interactive = hasattr(stream, "isatty") and stream.isatty()

        # Size detection
        width, height = cls._detect_size()

        # Color detection
        color_mode = cls._detect_colors(is_interactive)

        # Unicode detection
        unicode_support = cls._detect_unicode()

        # Cursor support (assume yes for interactive)
        supports_cursor = is_interactive

        # Title support
        supports_title = is_interactive and os.environ.get("TERM", "") not in (
            "dumb",
            "linux",
        )

        return cls(
            width=width,
            height=height,
            color_mode=color_mode,
            unicode_support=unicode_support,
            supports_cursor=supports_cursor,
            supports_title=supports_title,
            is_interactive=is_interactive,
        )

    @staticmethod
    def _detect_size() -> tuple[int, int]:
        """Detect terminal size."""
        try:
            import shutil

            size = shutil.get_terminal_size(fallback=(80, 24))
            return size.columns, size.lines
        except Exception:
            return 80, 24

    @staticmethod
    def _detect_colors(is_interactive: bool) -> ColorMode:
        """Detect color support level."""
        if not is_interactive:
            return "none"

        # Check NO_COLOR environment variable
        if os.environ.get("NO_COLOR"):
            return "none"

        # Check COLORTERM for true color
        colorterm = os.environ.get("COLORTERM", "").lower()
        if colorterm in ("truecolor", "24bit"):
            return "rgb"

        # Check terminal type
        term = os.environ.get("TERM", "").lower()

        # True color terminals
        if any(x in term for x in ("256color", "truecolor", "24bit", "kitty", "alacritty")):
            return "rgb" if colorterm else "256"

        # 256 color support
        if "256" in term:
            return "256"

        # Basic color
        if term and term != "dumb":
            return "16"

        return "none"

    @staticmethod
    def _detect_unicode() -> UnicodeSupport:
        """Detect Unicode support level."""
        # Check locale
        lang = os.environ.get("LANG", "").lower()
        lc_all = os.environ.get("LC_ALL", "").lower()
        lc_ctype = os.environ.get("LC_CTYPE", "").lower()

        for locale_var in (lc_all, lc_ctype, lang):
            if "utf-8" in locale_var or "utf8" in locale_var:
                return UnicodeSupport.FULL

        # Check terminal
        term = os.environ.get("TERM", "").lower()
        if term in ("dumb", "linux"):
            return UnicodeSupport.ASCII

        # Check for known good terminals
        if any(t in term for t in ("xterm", "vt", "screen", "tmux", "kitty")):
            return UnicodeSupport.FULL

        return UnicodeSupport.BASIC

    def degrade_color(self, color: Color) -> Color:
        """Degrade a color to match terminal capabilities."""
        return color.degrade_to(self.color_mode)

    @property
    def supports_box_drawing(self) -> bool:
        """Check if box drawing characters are supported."""
        return self.unicode_support == UnicodeSupport.FULL

    @property
    def supports_braille(self) -> bool:
        """Check if braille characters are supported."""
        return self.unicode_support == UnicodeSupport.FULL


# === Mock Capabilities for Testing ===


def minimal_capabilities() -> TerminalCapabilities:
    """Create minimal capabilities for testing."""
    return TerminalCapabilities(
        width=80,
        height=24,
        color_mode="none",
        unicode_support=UnicodeSupport.ASCII,
        supports_cursor=False,
        supports_title=False,
        is_interactive=False,
    )


def full_capabilities(width: int = 120, height: int = 40) -> TerminalCapabilities:
    """Create full capabilities for testing."""
    return TerminalCapabilities(
        width=width,
        height=height,
        color_mode="rgb",
        unicode_support=UnicodeSupport.FULL,
        supports_cursor=True,
        supports_title=True,
        is_interactive=True,
    )


# === Terminal Output ===


ESC = "\x1b"
CSI = f"{ESC}["


@dataclass
class TerminalOutput:
    """
    Terminal output writer with capability awareness.

    Handles cursor control, colors, and screen management.
    Automatically degrades based on capabilities.

    Example:
        caps = TerminalCapabilities.detect()
        term = TerminalOutput(caps)

        term.clear_screen()
        term.move_to(0, 0)
        term.write_styled("Hello", Color.rgb(255, 100, 50))
        term.flush()
    """

    caps: TerminalCapabilities
    stream: TextIO = field(default_factory=lambda: sys.stdout)
    _buffer: list[str] = field(default_factory=list)

    # === Cursor Control ===

    def move_to(self, x: int, y: int) -> TerminalOutput:
        """Move cursor to position (0-indexed)."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}{y + 1};{x + 1}H")
        return self

    def move_up(self, n: int = 1) -> TerminalOutput:
        """Move cursor up n lines."""
        if self.caps.supports_cursor and n > 0:
            self._buffer.append(f"{CSI}{n}A")
        return self

    def move_down(self, n: int = 1) -> TerminalOutput:
        """Move cursor down n lines."""
        if self.caps.supports_cursor and n > 0:
            self._buffer.append(f"{CSI}{n}B")
        return self

    def move_right(self, n: int = 1) -> TerminalOutput:
        """Move cursor right n columns."""
        if self.caps.supports_cursor and n > 0:
            self._buffer.append(f"{CSI}{n}C")
        return self

    def move_left(self, n: int = 1) -> TerminalOutput:
        """Move cursor left n columns."""
        if self.caps.supports_cursor and n > 0:
            self._buffer.append(f"{CSI}{n}D")
        return self

    def save_cursor(self) -> TerminalOutput:
        """Save cursor position."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}s")
        return self

    def restore_cursor(self) -> TerminalOutput:
        """Restore saved cursor position."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}u")
        return self

    def hide_cursor(self) -> TerminalOutput:
        """Hide cursor."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}?25l")
        return self

    def show_cursor(self) -> TerminalOutput:
        """Show cursor."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}?25h")
        return self

    # === Screen Control ===

    def clear_screen(self) -> TerminalOutput:
        """Clear entire screen."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}2J")
        return self

    def clear_line(self) -> TerminalOutput:
        """Clear current line."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}2K")
        return self

    def clear_to_end(self) -> TerminalOutput:
        """Clear from cursor to end of screen."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}J")
        return self

    def clear_to_line_end(self) -> TerminalOutput:
        """Clear from cursor to end of line."""
        if self.caps.supports_cursor:
            self._buffer.append(f"{CSI}K")
        return self

    def set_title(self, title: str) -> TerminalOutput:
        """Set terminal window title."""
        if self.caps.supports_title:
            self._buffer.append(f"{ESC}]0;{title}\x07")
        return self

    # === Writing ===

    def write(self, text: str) -> TerminalOutput:
        """Write plain text."""
        self._buffer.append(text)
        return self

    def writeln(self, text: str = "") -> TerminalOutput:
        """Write text with newline."""
        self._buffer.append(text + "\n")
        return self

    def write_styled(
        self,
        text: str,
        fg: Color | None = None,
        bg: Color | None = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        underline: bool = False,
    ) -> TerminalOutput:
        """
        Write styled text.

        Automatically degrades colors based on capabilities.
        """
        seq = ANSISequence.new()

        if fg:
            degraded_fg = self.caps.degrade_color(fg)
            seq = seq.fg_color(degraded_fg, self.caps.color_mode)

        if bg:
            degraded_bg = self.caps.degrade_color(bg)
            seq = seq.bg_color(degraded_bg, self.caps.color_mode)

        if bold:
            seq = seq.bold()
        if dim:
            seq = seq.dim()
        if italic:
            seq = seq.italic()
        if underline:
            seq = seq.underline()

        styled = seq.wrap(text)
        self._buffer.append(styled)
        return self

    def write_with_scheme(
        self,
        text: str,
        semantic: Literal[
            "primary",
            "secondary",
            "text",
            "text_dim",
            "success",
            "warning",
            "error",
            "info",
        ],
        scheme: ColorScheme = ColorScheme.DARK,
        bold: bool = False,
    ) -> TerminalOutput:
        """Write text using semantic colors from a scheme."""
        colors = get_scheme(scheme)
        color_map = {
            "primary": colors.primary,
            "secondary": colors.secondary,
            "text": colors.text,
            "text_dim": colors.text_dim,
            "success": colors.success,
            "warning": colors.warning,
            "error": colors.error,
            "info": colors.info,
        }
        return self.write_styled(text, fg=color_map[semantic], bold=bold)

    def reset_style(self) -> TerminalOutput:
        """Reset all styling."""
        self._buffer.append(ANSISequence.reset())
        return self

    # === Buffer Management ===

    def flush(self) -> None:
        """Flush buffer to output stream."""
        if self._buffer:
            self.stream.write("".join(self._buffer))
            self.stream.flush()
            self._buffer.clear()

    def get_buffer(self) -> str:
        """Get buffer contents without flushing."""
        return "".join(self._buffer)

    def clear_buffer(self) -> None:
        """Clear buffer without writing."""
        self._buffer.clear()


# === Responsive Layout ===


@dataclass(frozen=True)
class LayoutConstraints:
    """
    Constraints for responsive layout.

    Immutable specification of layout bounds.
    """

    min_width: int = 40
    max_width: int | None = None  # None = terminal width
    min_height: int = 10
    max_height: int | None = None  # None = terminal height
    padding: int = 1


@dataclass
class ResponsiveLayout:
    """
    Responsive layout calculator.

    Adapts content width based on terminal size.

    Example:
        layout = ResponsiveLayout(caps)

        # Get available width for content
        width = layout.content_width()

        # Get columns for multi-column layout
        cols = layout.columns(min_col_width=30)
    """

    caps: TerminalCapabilities
    constraints: LayoutConstraints = field(default_factory=LayoutConstraints)

    def content_width(self) -> int:
        """Get available content width."""
        max_w = self.constraints.max_width or self.caps.width
        width = min(self.caps.width, max_w) - (self.constraints.padding * 2)
        return max(self.constraints.min_width, width)

    def content_height(self) -> int:
        """Get available content height."""
        max_h = self.constraints.max_height or self.caps.height
        height = min(self.caps.height, max_h) - (self.constraints.padding * 2)
        return max(self.constraints.min_height, height)

    def columns(self, min_col_width: int, gap: int = 2) -> int:
        """Calculate number of columns that fit."""
        width = self.content_width()
        if width < min_col_width:
            return 1
        # Each column after first needs gap
        # width = n * min_col_width + (n-1) * gap
        # width = n * (min_col_width + gap) - gap
        # n = (width + gap) / (min_col_width + gap)
        return max(1, (width + gap) // (min_col_width + gap))

    def column_width(self, num_columns: int, gap: int = 2) -> int:
        """Calculate width per column."""
        if num_columns <= 1:
            return self.content_width()
        width = self.content_width()
        total_gaps = (num_columns - 1) * gap
        return (width - total_gaps) // num_columns

    def wrap_text(self, text: str, width: int | None = None) -> list[str]:
        """Wrap text to width."""
        target_width = width or self.content_width()
        words = text.split()
        lines: list[str] = []
        current_line = ""

        for word in words:
            if not current_line:
                current_line = word
            elif len(current_line) + 1 + len(word) <= target_width:
                current_line += " " + word
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines or [""]


# === Graceful Degradation ===


@dataclass
class DegradedRenderer:
    """
    Renderer that gracefully degrades based on capabilities.

    Provides fallbacks for limited terminals.

    Example:
        renderer = DegradedRenderer(caps)

        # Automatically uses ASCII fallback if needed
        box = renderer.box_char("top_left")  # Returns '┌' or '+'

        # Degrades colors
        styled = renderer.styled_text("Error", "error")
    """

    caps: TerminalCapabilities
    scheme: ColorScheme = ColorScheme.DARK

    def box_char(
        self,
        position: Literal[
            "horizontal",
            "vertical",
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
        ],
    ) -> str:
        """Get appropriate box drawing character."""
        from .box import BoxStyle, get_chars

        if self.caps.supports_box_drawing:
            chars = get_chars(BoxStyle.SINGLE)
        else:
            chars = get_chars(BoxStyle.ASCII)

        result: str = getattr(chars, position)
        return result

    def sparkline_char(self, value: float) -> str:
        """Get sparkline character for value."""
        from .art import SPARK_CHARS

        if self.caps.supports_box_drawing:
            idx = int(value * (len(SPARK_CHARS) - 1))
            return SPARK_CHARS[min(idx, len(SPARK_CHARS) - 1)]
        else:
            # ASCII fallback
            chars = "_.-=*#"
            idx = int(value * (len(chars) - 1))
            return chars[min(idx, len(chars) - 1)]

    def progress_chars(self) -> tuple[str, str, str]:
        """Get progress bar characters (empty, partial, filled)."""
        if self.caps.supports_box_drawing:
            return ("░", "▓", "█")
        return ("-", "=", "#")

    def styled_text(
        self,
        text: str,
        semantic: str,
        bold: bool = False,
    ) -> str:
        """Get styled text with degradation."""
        colors = get_scheme(self.scheme)

        color_map = {
            "primary": colors.primary,
            "secondary": colors.secondary,
            "text": colors.text,
            "text_dim": colors.text_dim,
            "success": colors.success,
            "warning": colors.warning,
            "error": colors.error,
            "info": colors.info,
            "idle": colors.idle,
            "active": colors.active,
            "waiting": colors.waiting,
            "thinking": colors.thinking,
            "yielding": colors.yielding,
            "complete": colors.complete,
        }

        color = color_map.get(semantic, colors.text)
        degraded = self.caps.degrade_color(color)

        seq = ANSISequence.new().fg_color(degraded, self.caps.color_mode)
        if bold:
            seq = seq.bold()

        return seq.wrap(text)

    def degrade_lines(self, lines: list[str]) -> list[str]:
        """
        Degrade lines for limited terminals.

        Replaces Unicode with ASCII equivalents.
        """
        if self.caps.unicode_support == UnicodeSupport.FULL:
            return lines

        # Character replacement map for degradation
        replacements = {
            # Box drawing
            "─": "-",
            "│": "|",
            "┌": "+",
            "┐": "+",
            "└": "+",
            "┘": "+",
            "├": "+",
            "┤": "+",
            "┬": "+",
            "┴": "+",
            "┼": "+",
            "═": "=",
            "║": "|",
            "╔": "+",
            "╗": "+",
            "╚": "+",
            "╝": "+",
            "╭": "+",
            "╮": "+",
            "╰": "+",
            "╯": "+",
            "━": "-",
            "┃": "|",
            "┏": "+",
            "┓": "+",
            "┗": "+",
            "┛": "+",
            # Blocks
            "█": "#",
            "▓": "#",
            "▒": "=",
            "░": "-",
            "▏": "|",
            "▎": "|",
            "▍": "|",
            "▌": "|",
            "▋": "|",
            "▊": "|",
            "▉": "|",
            # Bars
            "▁": "_",
            "▂": "_",
            "▃": "_",
            "▄": "=",
            "▅": "=",
            "▆": "#",
            "▇": "#",
            # Dots/circles
            "●": "o",
            "○": "o",
            "◉": "@",
            "◎": "@",
            "◐": "o",
            "◑": "o",
            "◒": "o",
            "◓": "o",
            "◦": ".",
            "·": ".",
            "∘": "o",
            "⠋": "/",
            "⠙": "/",
            "⠹": "\\",
            "⠸": "\\",
            "⠼": "\\",
            "⠴": "/",
            "⠦": "/",
            "⠧": "|",
            "⠇": "|",
            "⠏": "/",
        }

        result: list[str] = []
        for line in lines:
            for old, new in replacements.items():
                line = line.replace(old, new)
            result.append(line)

        return result
