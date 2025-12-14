"""
ANSI Color and Style System: Terminal color abstraction.

Pure, deterministic terminal styling. No side effects in construction.
The escape sequences are only evaluated at render time.

Supports:
- Standard 16 colors (4-bit)
- Extended 256 colors (8-bit)
- True color RGB (24-bit)
- Text styles (bold, dim, italic, underline, etc.)
- Color schemes with semantic meanings

This is the foundation for terminal rendering across the reactive substrate.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    pass


class ANSIColor(IntEnum):
    """
    Standard 16 ANSI colors.

    These are the basic 4-bit colors available in virtually all terminals.
    Each color has a normal and bright variant.
    """

    # Standard colors (foreground 30-37, background 40-47)
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7

    # Bright colors (foreground 90-97, background 100-107)
    BRIGHT_BLACK = 8  # Often "gray"
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15

    def fg_code(self) -> int:
        """Get foreground escape code."""
        if self < 8:
            return 30 + self
        return 90 + (self - 8)

    def bg_code(self) -> int:
        """Get background escape code."""
        if self < 8:
            return 40 + self
        return 100 + (self - 8)


class ANSIStyle(IntEnum):
    """
    Text style modifiers.

    These can be combined to create rich text styling.
    Not all terminals support all styles.
    """

    RESET = 0
    BOLD = 1
    DIM = 2
    ITALIC = 3
    UNDERLINE = 4
    BLINK = 5
    BLINK_FAST = 6  # Rarely supported
    REVERSE = 7
    HIDDEN = 8
    STRIKETHROUGH = 9


ColorMode = Literal["16", "256", "rgb", "none"]


@dataclass(frozen=True)
class Color:
    """
    Universal color representation.

    Can represent any of the three color modes:
    - 16-color (standard ANSI)
    - 256-color (extended palette)
    - RGB (true color)

    Immutable for purity.

    Examples:
        Color.standard(ANSIColor.RED)
        Color.palette(196)  # Bright red from 256 palette
        Color.rgb(255, 100, 50)  # True color orange
    """

    mode: ColorMode = "16"
    value: int = 0  # Standard/palette index, or R for RGB
    g: int = 0  # G for RGB
    b: int = 0  # B for RGB

    @classmethod
    def standard(cls, color: ANSIColor) -> Color:
        """Create from standard 16-color palette."""
        return cls(mode="16", value=int(color))

    @classmethod
    def palette(cls, index: int) -> Color:
        """Create from 256-color palette (0-255)."""
        return cls(mode="256", value=max(0, min(255, index)))

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> Color:
        """Create from RGB values (0-255 each)."""
        return cls(
            mode="rgb",
            value=max(0, min(255, r)),
            g=max(0, min(255, g)),
            b=max(0, min(255, b)),
        )

    @classmethod
    def hex(cls, hex_color: str) -> Color:
        """Create from hex string (e.g., '#FF6432' or 'FF6432')."""
        h = hex_color.lstrip("#")
        if len(h) == 3:
            h = "".join(c + c for c in h)
        if len(h) != 6:
            return cls.standard(ANSIColor.WHITE)  # Fallback
        try:
            r = int(h[0:2], 16)
            g = int(h[2:4], 16)
            b = int(h[4:6], 16)
            return cls.rgb(r, g, b)
        except ValueError:
            return cls.standard(ANSIColor.WHITE)

    def to_fg_sequence(self, force_mode: ColorMode | None = None) -> str:
        """Convert to foreground escape sequence (without ESC prefix)."""
        mode = force_mode or self.mode
        if mode == "none":
            return ""
        if mode == "16":
            color = ANSIColor(self.value) if self.value < 16 else ANSIColor.WHITE
            return str(color.fg_code())
        if mode == "256":
            return f"38;5;{self.value}"
        if mode == "rgb":
            return f"38;2;{self.value};{self.g};{self.b}"
        return ""

    def to_bg_sequence(self, force_mode: ColorMode | None = None) -> str:
        """Convert to background escape sequence (without ESC prefix)."""
        mode = force_mode or self.mode
        if mode == "none":
            return ""
        if mode == "16":
            color = ANSIColor(self.value) if self.value < 16 else ANSIColor.WHITE
            return str(color.bg_code())
        if mode == "256":
            return f"48;5;{self.value}"
        if mode == "rgb":
            return f"48;2;{self.value};{self.g};{self.b}"
        return ""

    def degrade_to(self, target_mode: ColorMode) -> Color:
        """
        Degrade color to a lower color mode.

        This enables graceful degradation for terminals with limited color support.
        """
        if target_mode == "none":
            return Color(mode="none")
        if target_mode == self.mode:
            return self
        if target_mode == "rgb":
            return self  # Can't upgrade, return as-is

        if target_mode == "256" and self.mode == "rgb":
            # RGB to 256: Find closest palette color
            return Color.palette(self._rgb_to_256(self.value, self.g, self.b))

        if target_mode == "16":
            if self.mode == "256":
                # 256 to 16: Map to closest standard color
                return Color.standard(ANSIColor(self._256_to_16(self.value)))
            if self.mode == "rgb":
                # RGB to 16: Go through 256 first
                idx256 = self._rgb_to_256(self.value, self.g, self.b)
                return Color.standard(ANSIColor(self._256_to_16(idx256)))

        return self

    @staticmethod
    def _rgb_to_256(r: int, g: int, b: int) -> int:
        """Convert RGB to closest 256-color palette index."""
        # If grayscale (r ≈ g ≈ b), use grayscale ramp (232-255)
        if abs(r - g) < 10 and abs(g - b) < 10:
            gray = (r + g + b) // 3
            if gray < 8:
                return 16  # Black
            if gray > 248:
                return 231  # White
            return 232 + round((gray - 8) / 247 * 23)

        # Otherwise use 6x6x6 color cube (16-231)
        def to_cube(v: int) -> int:
            if v < 48:
                return 0
            if v < 115:
                return 1
            return min(5, (v - 35) // 40)

        return 16 + 36 * to_cube(r) + 6 * to_cube(g) + to_cube(b)

    @staticmethod
    def _256_to_16(idx: int) -> int:
        """Convert 256-color index to closest standard 16 color."""
        if idx < 16:
            return idx

        # Color cube (16-231)
        if idx < 232:
            idx -= 16
            r = idx // 36
            g = (idx % 36) // 6
            b = idx % 6

            # Map to closest ANSI color
            is_bright = r > 2 or g > 2 or b > 2
            offset = 8 if is_bright else 0

            if r > g and r > b:
                return offset + 1  # Red
            if g > r and g > b:
                return offset + 2  # Green
            if b > r and b > g:
                return offset + 4  # Blue
            if r > 2 and g > 2:
                return offset + 3  # Yellow
            if r > 2 and b > 2:
                return offset + 5  # Magenta
            if g > 2 and b > 2:
                return offset + 6  # Cyan
            if r == g == b and r > 2:
                return 15  # Bright white
            return offset + 7  # White/gray

        # Grayscale (232-255)
        gray = idx - 232
        if gray < 6:
            return 0  # Black
        if gray > 18:
            return 15  # Bright white
        if gray < 12:
            return 8  # Bright black (gray)
        return 7  # White


@dataclass(frozen=True)
class StyleSpec:
    """
    Complete style specification for a text segment.

    Combines foreground color, background color, and text styles.
    All fields are optional for composability.

    Examples:
        # Red bold text
        StyleSpec(fg=Color.standard(ANSIColor.RED), styles=frozenset([ANSIStyle.BOLD]))

        # Warning style
        StyleSpec(
            fg=Color.rgb(255, 200, 0),
            bg=Color.rgb(50, 50, 50),
            styles=frozenset([ANSIStyle.BOLD])
        )
    """

    fg: Color | None = None
    bg: Color | None = None
    styles: frozenset[ANSIStyle] = frozenset()

    def merge(self, other: StyleSpec) -> StyleSpec:
        """Merge with another style, other takes precedence."""
        return StyleSpec(
            fg=other.fg if other.fg else self.fg,
            bg=other.bg if other.bg else self.bg,
            styles=self.styles | other.styles,
        )


# === Escape Sequence Builder ===


ESC = "\x1b"
CSI = f"{ESC}["


@dataclass(frozen=True)
class ANSISequence:
    """
    Builder for ANSI escape sequences.

    Composes styles into efficient escape sequences.
    Immutable - each method returns a new sequence.

    Examples:
        seq = ANSISequence.new().fg(ANSIColor.RED).bold().build()
        print(f"{seq}Hello{ANSISequence.reset()}")

        # Using Color objects
        seq = ANSISequence.new().fg_color(Color.rgb(255, 100, 50)).build()
    """

    parts: tuple[str, ...] = ()

    @classmethod
    def new(cls) -> ANSISequence:
        """Create new empty sequence."""
        return cls()

    @classmethod
    def reset(cls) -> str:
        """Get reset sequence."""
        return f"{CSI}0m"

    def fg(self, color: ANSIColor) -> ANSISequence:
        """Add foreground color (standard 16)."""
        return ANSISequence(parts=(*self.parts, str(color.fg_code())))

    def bg(self, color: ANSIColor) -> ANSISequence:
        """Add background color (standard 16)."""
        return ANSISequence(parts=(*self.parts, str(color.bg_code())))

    def fg_color(self, color: Color, mode: ColorMode | None = None) -> ANSISequence:
        """Add foreground color (any mode)."""
        seq = color.to_fg_sequence(mode)
        if seq:
            return ANSISequence(parts=(*self.parts, seq))
        return self

    def bg_color(self, color: Color, mode: ColorMode | None = None) -> ANSISequence:
        """Add background color (any mode)."""
        seq = color.to_bg_sequence(mode)
        if seq:
            return ANSISequence(parts=(*self.parts, seq))
        return self

    def style(self, style: ANSIStyle) -> ANSISequence:
        """Add a style."""
        return ANSISequence(parts=(*self.parts, str(int(style))))

    def bold(self) -> ANSISequence:
        """Add bold style."""
        return self.style(ANSIStyle.BOLD)

    def dim(self) -> ANSISequence:
        """Add dim style."""
        return self.style(ANSIStyle.DIM)

    def italic(self) -> ANSISequence:
        """Add italic style."""
        return self.style(ANSIStyle.ITALIC)

    def underline(self) -> ANSISequence:
        """Add underline style."""
        return self.style(ANSIStyle.UNDERLINE)

    def blink(self) -> ANSISequence:
        """Add blink style."""
        return self.style(ANSIStyle.BLINK)

    def reverse(self) -> ANSISequence:
        """Add reverse video style."""
        return self.style(ANSIStyle.REVERSE)

    def strikethrough(self) -> ANSISequence:
        """Add strikethrough style."""
        return self.style(ANSIStyle.STRIKETHROUGH)

    def from_spec(self, spec: StyleSpec, mode: ColorMode = "256") -> ANSISequence:
        """Build from StyleSpec."""
        result = self
        if spec.fg:
            result = result.fg_color(spec.fg, mode)
        if spec.bg:
            result = result.bg_color(spec.bg, mode)
        for s in spec.styles:
            result = result.style(s)
        return result

    def build(self) -> str:
        """Build the complete escape sequence."""
        if not self.parts:
            return ""
        return f"{CSI}{';'.join(self.parts)}m"

    def wrap(self, text: str) -> str:
        """Wrap text with this style, adding reset at end."""
        seq = self.build()
        if not seq:
            return text
        return f"{seq}{text}{ANSISequence.reset()}"


# === Color Schemes ===


class ColorScheme(Enum):
    """
    Predefined color schemes for different contexts.

    Each scheme provides semantic colors that work together.
    """

    DARK = "dark"
    LIGHT = "light"
    HIGH_CONTRAST = "high_contrast"
    COLORBLIND_SAFE = "colorblind_safe"
    MONOCHROME = "monochrome"


@dataclass(frozen=True)
class SemanticColors:
    """
    Semantic color mappings for a scheme.

    These represent meanings, not specific colors.
    Maps to actual colors based on the chosen scheme.
    """

    # Primary UI colors
    primary: Color
    secondary: Color
    background: Color
    surface: Color
    text: Color
    text_dim: Color

    # Semantic states
    success: Color
    warning: Color
    error: Color
    info: Color

    # Agent phases (matching entropy.py PHASE_GLYPHS)
    idle: Color
    active: Color
    waiting: Color
    thinking: Color
    yielding: Color
    complete: Color


# Predefined schemes
SCHEMES: dict[ColorScheme, SemanticColors] = {
    ColorScheme.DARK: SemanticColors(
        primary=Color.rgb(100, 180, 255),
        secondary=Color.rgb(180, 100, 255),
        background=Color.standard(ANSIColor.BLACK),
        surface=Color.palette(236),  # Dark gray
        text=Color.standard(ANSIColor.WHITE),
        text_dim=Color.standard(ANSIColor.BRIGHT_BLACK),
        success=Color.rgb(80, 200, 120),
        warning=Color.rgb(255, 180, 50),
        error=Color.rgb(255, 80, 80),
        info=Color.rgb(80, 180, 255),
        idle=Color.standard(ANSIColor.WHITE),
        active=Color.rgb(100, 255, 150),
        waiting=Color.rgb(255, 200, 100),
        thinking=Color.rgb(150, 150, 255),
        yielding=Color.rgb(200, 150, 255),
        complete=Color.rgb(100, 200, 100),
    ),
    ColorScheme.LIGHT: SemanticColors(
        primary=Color.rgb(0, 100, 200),
        secondary=Color.rgb(100, 0, 200),
        background=Color.standard(ANSIColor.WHITE),
        surface=Color.palette(254),  # Light gray
        text=Color.standard(ANSIColor.BLACK),
        text_dim=Color.palette(244),  # Medium gray
        success=Color.rgb(0, 150, 50),
        warning=Color.rgb(200, 120, 0),
        error=Color.rgb(200, 0, 0),
        info=Color.rgb(0, 100, 200),
        idle=Color.palette(240),
        active=Color.rgb(0, 150, 50),
        waiting=Color.rgb(200, 150, 0),
        thinking=Color.rgb(100, 100, 200),
        yielding=Color.rgb(150, 100, 200),
        complete=Color.rgb(0, 150, 0),
    ),
    ColorScheme.HIGH_CONTRAST: SemanticColors(
        primary=Color.standard(ANSIColor.BRIGHT_WHITE),
        secondary=Color.standard(ANSIColor.BRIGHT_CYAN),
        background=Color.standard(ANSIColor.BLACK),
        surface=Color.standard(ANSIColor.BLACK),
        text=Color.standard(ANSIColor.BRIGHT_WHITE),
        text_dim=Color.standard(ANSIColor.WHITE),
        success=Color.standard(ANSIColor.BRIGHT_GREEN),
        warning=Color.standard(ANSIColor.BRIGHT_YELLOW),
        error=Color.standard(ANSIColor.BRIGHT_RED),
        info=Color.standard(ANSIColor.BRIGHT_CYAN),
        idle=Color.standard(ANSIColor.WHITE),
        active=Color.standard(ANSIColor.BRIGHT_GREEN),
        waiting=Color.standard(ANSIColor.BRIGHT_YELLOW),
        thinking=Color.standard(ANSIColor.BRIGHT_BLUE),
        yielding=Color.standard(ANSIColor.BRIGHT_MAGENTA),
        complete=Color.standard(ANSIColor.BRIGHT_GREEN),
    ),
    ColorScheme.COLORBLIND_SAFE: SemanticColors(
        # Using blue-orange palette (safe for most colorblind types)
        primary=Color.rgb(0, 114, 178),  # Blue
        secondary=Color.rgb(230, 159, 0),  # Orange
        background=Color.standard(ANSIColor.BLACK),
        surface=Color.palette(236),
        text=Color.standard(ANSIColor.WHITE),
        text_dim=Color.palette(244),
        success=Color.rgb(0, 158, 115),  # Teal (blue-green)
        warning=Color.rgb(230, 159, 0),  # Orange
        error=Color.rgb(204, 121, 167),  # Pink
        info=Color.rgb(86, 180, 233),  # Light blue
        idle=Color.standard(ANSIColor.WHITE),
        active=Color.rgb(0, 158, 115),
        waiting=Color.rgb(230, 159, 0),
        thinking=Color.rgb(0, 114, 178),
        yielding=Color.rgb(204, 121, 167),
        complete=Color.rgb(0, 158, 115),
    ),
    ColorScheme.MONOCHROME: SemanticColors(
        # All grayscale for extreme compatibility
        primary=Color.standard(ANSIColor.BRIGHT_WHITE),
        secondary=Color.standard(ANSIColor.WHITE),
        background=Color.standard(ANSIColor.BLACK),
        surface=Color.palette(235),
        text=Color.standard(ANSIColor.WHITE),
        text_dim=Color.palette(244),
        success=Color.standard(ANSIColor.WHITE),
        warning=Color.standard(ANSIColor.BRIGHT_WHITE),
        error=Color.standard(ANSIColor.BRIGHT_WHITE),
        info=Color.standard(ANSIColor.WHITE),
        idle=Color.palette(240),
        active=Color.standard(ANSIColor.BRIGHT_WHITE),
        waiting=Color.palette(248),
        thinking=Color.palette(250),
        yielding=Color.palette(252),
        complete=Color.standard(ANSIColor.WHITE),
    ),
}


def get_scheme(scheme: ColorScheme) -> SemanticColors:
    """Get semantic colors for a scheme."""
    return SCHEMES[scheme]


def phase_to_color(phase: str, scheme: ColorScheme = ColorScheme.DARK) -> Color:
    """Get color for an agent phase."""
    colors = get_scheme(scheme)
    mapping = {
        "idle": colors.idle,
        "active": colors.active,
        "waiting": colors.waiting,
        "error": colors.error,
        "yielding": colors.yielding,
        "thinking": colors.thinking,
        "complete": colors.complete,
    }
    return mapping.get(phase, colors.idle)
