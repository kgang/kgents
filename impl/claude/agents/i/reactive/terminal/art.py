"""
ASCII Art Primitives: Text-based graphics for terminal display.

Pure, deterministic ASCII art generation. All functions are stateless
and produce the same output given the same input.

Includes:
- Horizontal/vertical bars with customizable fill characters
- Sparklines using braille characters
- Progress indicators (spinners, progress bars)
- Gauges and meters
- Frame/panel borders

These primitives compose with the box drawing and color systems.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Iterator, Literal, Sequence

if TYPE_CHECKING:
    pass


# === Character Sets ===


# Horizontal bar fill characters (partial to full)
BAR_H_CHARS = " ▏▎▍▌▋▊▉█"
BAR_H_THIN = " ░▒▓█"
BAR_H_DOTS = " ·∘○●"

# Vertical bar fill characters (bottom to top)
BAR_V_CHARS = " ▁▂▃▄▅▆▇█"

# Sparkline characters (uses vertical bars)
SPARK_CHARS = "▁▂▃▄▅▆▇█"

# Braille dot patterns for high-resolution sparklines
# Each braille character is 2x4 dots (columns x rows)
BRAILLE_BASE = 0x2800

# Spinner characters
SPINNER_DOTS = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
SPINNER_CLASSIC = ("|", "/", "-", "\\")
SPINNER_ARROWS = ("←", "↖", "↑", "↗", "→", "↘", "↓", "↙")
SPINNER_BOUNCE = ("⠁", "⠂", "⠄", "⠂")
SPINNER_BLOCKS = ("▖", "▘", "▝", "▗")

# Progress bar styles
PROGRESS_STYLES = {
    "solid": {"empty": "░", "filled": "█", "partial": "▓"},
    "thin": {"empty": "─", "filled": "━", "partial": "╌"},
    "dots": {"empty": "○", "filled": "●", "partial": "◐"},
    "blocks": {"empty": "▱", "filled": "▰", "partial": "▰"},
    "ascii": {"empty": "-", "filled": "#", "partial": "="},
}

# Gauge needles
GAUGE_NEEDLES = ("╲", "│", "╱", "─")


class BarStyle(Enum):
    """Bar rendering styles."""

    SOLID = auto()  # █
    SHADED = auto()  # ░▒▓█
    THIN = auto()  # ▏▎▍▌▋▊▉█
    DOTS = auto()  # ·∘○●
    ASCII = auto()  # #


# === Horizontal Bars ===


@dataclass(frozen=True)
class HBar:
    """
    Horizontal bar configuration.

    Immutable specification for rendering a horizontal bar.
    """

    value: float  # 0.0-1.0
    width: int
    style: BarStyle = BarStyle.SOLID
    show_value: bool = False
    fill_char: str | None = None  # Override fill character
    empty_char: str | None = None  # Override empty character


def render_hbar(bar: HBar) -> str:
    """
    Render a horizontal bar.

    Args:
        bar: Bar specification

    Returns:
        String representing the bar

    Example:
        >>> render_hbar(HBar(value=0.75, width=10))
        '███████▓░░'
    """
    value = max(0.0, min(1.0, bar.value))

    # Get character set
    if bar.fill_char and bar.empty_char:
        chars = bar.empty_char + bar.fill_char
        use_partials = False
    elif bar.style == BarStyle.SHADED:
        chars = BAR_H_THIN
        use_partials = True
    elif bar.style == BarStyle.THIN:
        chars = BAR_H_CHARS
        use_partials = True
    elif bar.style == BarStyle.DOTS:
        chars = BAR_H_DOTS
        use_partials = True
    elif bar.style == BarStyle.ASCII:
        chars = " #"
        use_partials = False
    else:  # SOLID
        chars = " ░█"
        use_partials = True

    # Calculate fill
    fill_float = value * bar.width
    full_chars = int(fill_float)
    partial = fill_float - full_chars

    # Build bar
    if use_partials and len(chars) > 2:
        # Use partial fill characters
        empty = chars[0]
        filled = chars[-1]

        result = filled * full_chars
        if partial > 0.1 and full_chars < bar.width:
            # Add partial character
            partial_idx = int(partial * (len(chars) - 1))
            result += chars[max(1, partial_idx)]
            result += empty * (bar.width - full_chars - 1)
        else:
            result += empty * (bar.width - full_chars)
    else:
        # Simple fill
        empty = chars[0]
        filled = chars[-1]
        result = filled * full_chars + empty * (bar.width - full_chars)

    # Add value display
    if bar.show_value:
        pct = f" {int(value * 100):3d}%"
        if len(result) + len(pct) <= bar.width + 5:
            result = result + pct

    return result


# === Vertical Bars ===


@dataclass(frozen=True)
class VBar:
    """
    Vertical bar configuration.
    """

    value: float  # 0.0-1.0
    height: int
    width: int = 1  # Width in characters
    style: BarStyle = BarStyle.SOLID


def render_vbar(bar: VBar) -> list[str]:
    """
    Render a vertical bar.

    Returns list of strings from top to bottom.

    Example:
        >>> render_vbar(VBar(value=0.5, height=4))
        ['░', '░', '█', '█']
    """
    value = max(0.0, min(1.0, bar.value))

    # Get characters
    if bar.style == BarStyle.SOLID or bar.style == BarStyle.SHADED:
        chars = BAR_V_CHARS
    else:
        chars = " ░█"  # Simplified

    empty = chars[0]
    filled = chars[-1]

    fill_float = value * bar.height
    full_rows = int(fill_float)
    partial = fill_float - full_rows

    lines: list[str] = []
    for i in range(bar.height):
        row_from_bottom = bar.height - 1 - i
        if row_from_bottom < full_rows:
            char = filled
        elif row_from_bottom == full_rows and partial > 0.1 and len(chars) > 2:
            partial_idx = int(partial * (len(chars) - 1))
            char = chars[max(1, partial_idx)]
        else:
            char = empty
        lines.append(char * bar.width)

    return lines


# === Sparklines ===


@dataclass(frozen=True)
class Sparkline:
    """
    Sparkline configuration.

    A sparkline shows a series of values as a mini-chart.
    """

    values: tuple[float, ...]
    height: int = 1  # 1 for standard, 2+ for braille
    min_val: float | None = None  # Auto-detect if None
    max_val: float | None = None  # Auto-detect if None


def render_sparkline(spark: Sparkline) -> str | list[str]:
    """
    Render a sparkline.

    For height=1, returns a single string.
    For height>1, returns list of strings (braille mode).

    Example:
        >>> render_sparkline(Sparkline(values=(0.1, 0.5, 0.8, 0.3)))
        '▁▄▇▂'
    """
    if not spark.values:
        return "─"

    # Normalize values
    min_v = spark.min_val if spark.min_val is not None else min(spark.values)
    max_v = spark.max_val if spark.max_val is not None else max(spark.values)
    range_v = max_v - min_v if max_v > min_v else 1.0

    normalized = tuple((v - min_v) / range_v for v in spark.values)

    if spark.height == 1:
        # Standard sparkline
        chars = SPARK_CHARS
        result = ""
        for v in normalized:
            idx = int(v * (len(chars) - 1))
            result += chars[min(idx, len(chars) - 1)]
        return result

    # Multi-row braille sparkline
    return _render_braille_sparkline(normalized, spark.height)


def _render_braille_sparkline(values: tuple[float, ...], height: int) -> list[str]:
    """Render multi-row sparkline using braille characters."""
    # Braille dots per character: 2 columns, 4 rows
    # Each character can represent 2 data points and 4 vertical levels

    rows_per_char = 4
    total_levels = height * rows_per_char

    # Group values in pairs (2 columns per braille char)
    lines = [[""] * ((len(values) + 1) // 2) for _ in range(height)]

    for i in range(0, len(values), 2):
        v1 = values[i]
        v2 = values[i + 1] if i + 1 < len(values) else 0.0

        # Calculate dot patterns for each row
        for row in range(height):
            row_from_bottom = height - 1 - row
            base_level = row_from_bottom * rows_per_char

            dots = 0
            for level in range(rows_per_char):
                level_threshold = (base_level + level) / total_levels
                # Left column (dots 0, 1, 2, 6)
                if v1 >= level_threshold:
                    dot_index = [0, 1, 2, 6][level]
                    dots |= 1 << dot_index
                # Right column (dots 3, 4, 5, 7)
                if v2 >= level_threshold:
                    dot_index = [3, 4, 5, 7][level]
                    dots |= 1 << dot_index

            lines[row][i // 2] = chr(BRAILLE_BASE + dots)

    return ["".join(row) for row in lines]


# === Progress Indicators ===


@dataclass(frozen=True)
class ProgressBar:
    """
    Progress bar configuration.
    """

    value: float  # 0.0-1.0
    width: int
    style: str = "solid"  # Key from PROGRESS_STYLES
    label: str | None = None
    show_percent: bool = True
    bracket_style: Literal["square", "round", "angle", "none"] = "square"


def render_progress(bar: ProgressBar) -> str:
    """
    Render a progress bar.

    Example:
        >>> render_progress(ProgressBar(value=0.6, width=20))
        '[████████████░░░░░░░░]  60%'
    """
    value = max(0.0, min(1.0, bar.value))
    style = PROGRESS_STYLES.get(bar.style, PROGRESS_STYLES["solid"])

    # Brackets
    brackets = {
        "square": ("[", "]"),
        "round": ("(", ")"),
        "angle": ("<", ">"),
        "none": ("", ""),
    }
    left, right = brackets.get(bar.bracket_style, ("", ""))

    # Inner width
    inner_width = bar.width - len(left) - len(right)

    # Build fill
    fill_float = value * inner_width
    full = int(fill_float)
    partial = fill_float - full

    filled = style["filled"] * full
    if partial > 0.5 and full < inner_width:
        filled += style.get("partial", style["filled"])
        empty = style["empty"] * (inner_width - full - 1)
    else:
        empty = style["empty"] * (inner_width - full)

    result = f"{left}{filled}{empty}{right}"

    # Add label and percent
    if bar.label:
        result = f"{bar.label}: {result}"
    if bar.show_percent:
        result = f"{result} {int(value * 100):3d}%"

    return result


def spinner_frame(t: float, style: str = "dots") -> str:
    """
    Get spinner character for current time.

    Args:
        t: Time in milliseconds
        style: One of "dots", "classic", "arrows", "bounce", "blocks"

    Returns:
        Single character for spinner
    """
    spinners = {
        "dots": SPINNER_DOTS,
        "classic": SPINNER_CLASSIC,
        "arrows": SPINNER_ARROWS,
        "bounce": SPINNER_BOUNCE,
        "blocks": SPINNER_BLOCKS,
    }
    frames = spinners.get(style, SPINNER_DOTS)

    # ~10 FPS for spinner
    idx = int(t / 100) % len(frames)
    return frames[idx]


# === Gauges ===


@dataclass(frozen=True)
class Gauge:
    """
    Circular gauge configuration (rendered as ASCII semicircle).
    """

    value: float  # 0.0-1.0
    width: int  # Width in characters
    label: str | None = None
    show_value: bool = True
    min_label: str = "0"
    max_label: str = "100"


def render_gauge(gauge: Gauge) -> list[str]:
    """
    Render a gauge as ASCII art.

    Example (width=11):
        ┌─────────┐
        │  ╱     ╲  │
        │ ╱   │   ╲ │
        └────┴────┘
           50%
    """
    from .box import BoxStyle, get_chars

    chars = get_chars(BoxStyle.SINGLE)
    value = max(0.0, min(1.0, gauge.value))

    # Gauge needs odd width for centering
    width = gauge.width if gauge.width % 2 == 1 else gauge.width + 1
    inner = width - 2

    lines: list[str] = []

    # Top border
    lines.append(chars.top_left + chars.horizontal * inner + chars.top_right)

    # Arc line (simplified as corners)
    arc = " " * (inner // 4) + "╱" + " " * (inner // 2) + "╲" + " " * (inner // 4)
    arc = arc[:inner].center(inner)
    lines.append(chars.vertical + arc + chars.vertical)

    # Needle line
    needle_pos = int(value * (inner - 1))
    needle_line = " " * inner
    needle_chars = list(needle_line)
    if needle_pos < len(needle_chars):
        # Needle direction based on position
        if value < 0.25:
            needle_chars[needle_pos] = "╲"
        elif value > 0.75:
            needle_chars[needle_pos] = "╱"
        else:
            needle_chars[needle_pos] = "│"
    needle_line = "".join(needle_chars)
    lines.append(chars.vertical + needle_line + chars.vertical)

    # Bottom with tick
    bottom = chars.horizontal * (inner // 2) + "┴" + chars.horizontal * (inner // 2)
    lines.append(chars.bottom_left + bottom[:inner] + chars.bottom_right)

    # Labels below
    if gauge.show_value or gauge.label:
        label = f"{int(value * 100)}%"
        if gauge.label:
            label = f"{gauge.label}: {label}"
        lines.append(label.center(width))

    return lines


# === Frame/Panel Borders ===


@dataclass(frozen=True)
class Panel:
    """
    Panel (bordered content area) configuration.
    """

    content: tuple[str, ...]
    title: str | None = None
    width: int | None = None  # Auto-fit if None
    padding: int = 1
    double_border: bool = False


def render_panel(panel: Panel) -> list[str]:
    """
    Render a panel with border around content.

    Example:
        >>> render_panel(Panel(content=("Hello", "World"), title="Message"))
        ┌─ Message ─┐
        │ Hello     │
        │ World     │
        └───────────┘
    """
    from .box import BoxRenderer, BoxSpec, BoxStyle

    # Calculate width
    if panel.width:
        width = panel.width
    else:
        content_width = max((len(line) for line in panel.content), default=0)
        width = content_width + 2 + (panel.padding * 2)
        if panel.title:
            width = max(width, len(panel.title) + 6)

    style = BoxStyle.DOUBLE if panel.double_border else BoxStyle.SINGLE
    height = len(panel.content) + 2

    renderer = BoxRenderer()
    return renderer.box_with_content(
        BoxSpec(
            width=width,
            height=height,
            style=style,
            title=panel.title,
            padding=panel.padding,
        ),
        list(panel.content),
    )


# === Composition Helpers ===


def horizontal_concat(blocks: Sequence[list[str]], gap: int = 1) -> list[str]:
    """
    Concatenate blocks horizontally.

    Args:
        blocks: Sequence of line lists
        gap: Space between blocks

    Returns:
        Merged lines
    """
    if not blocks:
        return []

    # Normalize heights
    max_height = max(len(b) for b in blocks)
    normalized = []
    for block in blocks:
        width = max((len(line) for line in block), default=0)
        padded = list(block)
        while len(padded) < max_height:
            padded.append(" " * width)
        normalized.append(padded)

    # Merge
    result: list[str] = []
    gap_str = " " * gap
    for row_idx in range(max_height):
        row_parts = [block[row_idx] for block in normalized]
        result.append(gap_str.join(row_parts))

    return result


def vertical_concat(blocks: Sequence[list[str]], gap: int = 0) -> list[str]:
    """
    Concatenate blocks vertically.

    Args:
        blocks: Sequence of line lists
        gap: Blank lines between blocks

    Returns:
        Merged lines
    """
    result: list[str] = []
    for i, block in enumerate(blocks):
        result.extend(block)
        if gap > 0 and i < len(blocks) - 1:
            result.extend([""] * gap)
    return result


def align_text(
    text: str,
    width: int,
    alignment: Literal["left", "center", "right"] = "left",
    fill: str = " ",
) -> str:
    """Align text within a fixed width."""
    if len(text) >= width:
        return text[:width]

    if alignment == "right":
        return text.rjust(width, fill)
    elif alignment == "center":
        return text.center(width, fill)
    return text.ljust(width, fill)
