"""
Theme System: Consistent styling across widgets.

Provides:
- Color tokens for semantic colors
- Spacing tokens for consistent layout
- Dark/light mode support
- Animation timing presets
- Widget style inheritance

The theme is a value. Switching themes is just changing a Signal.

"A good theme is invisible. Colors guide the eye without shouting."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

from agents.i.reactive.animation.easing import Easing
from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass


class ThemeMode(Enum):
    """Theme mode (light/dark)."""

    LIGHT = auto()
    DARK = auto()
    SYSTEM = auto()  # Follow system preference


# =============================================================================
# Color Tokens
# =============================================================================


@dataclass(frozen=True)
class RGB:
    """RGB color value."""

    r: int
    g: int
    b: int

    def to_ansi_fg(self) -> str:
        """Convert to ANSI foreground color code."""
        return f"\033[38;2;{self.r};{self.g};{self.b}m"

    def to_ansi_bg(self) -> str:
        """Convert to ANSI background color code."""
        return f"\033[48;2;{self.r};{self.g};{self.b}m"

    def to_hex(self) -> str:
        """Convert to hex string."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @classmethod
    def from_hex(cls, hex_str: str) -> RGB:
        """Create from hex string."""
        hex_str = hex_str.lstrip("#")
        return cls(
            r=int(hex_str[0:2], 16),
            g=int(hex_str[2:4], 16),
            b=int(hex_str[4:6], 16),
        )

    def blend(self, other: RGB, t: float) -> RGB:
        """Blend with another color (t=0 is self, t=1 is other)."""
        return RGB(
            r=round(self.r + (other.r - self.r) * t),
            g=round(self.g + (other.g - self.g) * t),
            b=round(self.b + (other.b - self.b) * t),
        )


@dataclass(frozen=True)
class ColorToken:
    """
    Semantic color token.

    Color tokens provide meaning rather than raw values:
    - `primary` for main actions
    - `secondary` for less prominent elements
    - `surface` for backgrounds
    - `error` for error states

    Each token has light and dark mode values.
    """

    name: str
    light: RGB
    dark: RGB

    def resolve(self, mode: ThemeMode) -> RGB:
        """Get the color for the current mode."""
        if mode == ThemeMode.DARK:
            return self.dark
        return self.light


# Standard color palette
class Colors:
    """Standard color palette."""

    # Grays
    WHITE = RGB(255, 255, 255)
    GRAY_50 = RGB(250, 250, 250)
    GRAY_100 = RGB(244, 244, 245)
    GRAY_200 = RGB(228, 228, 231)
    GRAY_300 = RGB(212, 212, 216)
    GRAY_400 = RGB(161, 161, 170)
    GRAY_500 = RGB(113, 113, 122)
    GRAY_600 = RGB(82, 82, 91)
    GRAY_700 = RGB(63, 63, 70)
    GRAY_800 = RGB(39, 39, 42)
    GRAY_900 = RGB(24, 24, 27)
    BLACK = RGB(0, 0, 0)

    # Primary (Blue)
    PRIMARY_50 = RGB(239, 246, 255)
    PRIMARY_100 = RGB(219, 234, 254)
    PRIMARY_200 = RGB(191, 219, 254)
    PRIMARY_300 = RGB(147, 197, 253)
    PRIMARY_400 = RGB(96, 165, 250)
    PRIMARY_500 = RGB(59, 130, 246)
    PRIMARY_600 = RGB(37, 99, 235)
    PRIMARY_700 = RGB(29, 78, 216)
    PRIMARY_800 = RGB(30, 64, 175)
    PRIMARY_900 = RGB(30, 58, 138)

    # Success (Green)
    SUCCESS_500 = RGB(34, 197, 94)
    SUCCESS_600 = RGB(22, 163, 74)

    # Warning (Amber)
    WARNING_500 = RGB(245, 158, 11)
    WARNING_600 = RGB(217, 119, 6)

    # Error (Red)
    ERROR_500 = RGB(239, 68, 68)
    ERROR_600 = RGB(220, 38, 38)

    # Info (Cyan)
    INFO_500 = RGB(6, 182, 212)
    INFO_600 = RGB(8, 145, 178)


# =============================================================================
# Spacing Tokens
# =============================================================================


class SpacingToken(Enum):
    """Spacing scale tokens."""

    NONE = 0
    XS = 1
    SM = 2
    MD = 4
    LG = 8
    XL = 12
    XXL = 16

    @property
    def value_int(self) -> int:
        """Get the spacing value as int."""
        return self.value


@dataclass(frozen=True)
class Spacing:
    """Spacing configuration."""

    xs: int = 1
    sm: int = 2
    md: int = 4
    lg: int = 8
    xl: int = 12
    xxl: int = 16

    def get(self, token: SpacingToken) -> int:
        """Get spacing value for a token."""
        return {
            SpacingToken.NONE: 0,
            SpacingToken.XS: self.xs,
            SpacingToken.SM: self.sm,
            SpacingToken.MD: self.md,
            SpacingToken.LG: self.lg,
            SpacingToken.XL: self.xl,
            SpacingToken.XXL: self.xxl,
        }[token]


# =============================================================================
# Animation Timing
# =============================================================================


@dataclass(frozen=True)
class AnimationTiming:
    """Animation timing presets."""

    # Durations in milliseconds
    instant: float = 0.0
    fast: float = 100.0
    normal: float = 200.0
    slow: float = 400.0
    slower: float = 600.0

    # Default easing
    ease_default: Easing = Easing.EASE_OUT
    ease_enter: Easing = Easing.EASE_OUT
    ease_exit: Easing = Easing.EASE_IN
    ease_move: Easing = Easing.EASE_IN_OUT

    # Spring presets (stiffness, damping)
    spring_gentle: tuple[float, float] = (120.0, 14.0)
    spring_wobbly: tuple[float, float] = (180.0, 12.0)
    spring_stiff: tuple[float, float] = (300.0, 20.0)
    spring_slow: tuple[float, float] = (120.0, 30.0)


# =============================================================================
# Theme Definition
# =============================================================================


@dataclass(frozen=True)
class ThemeColors:
    """Complete color scheme for a theme."""

    # Semantic colors
    primary: ColorToken
    secondary: ColorToken
    accent: ColorToken

    # State colors
    success: ColorToken
    warning: ColorToken
    error: ColorToken
    info: ColorToken

    # Surface colors
    background: ColorToken
    surface: ColorToken
    surface_variant: ColorToken

    # Text colors
    text_primary: ColorToken
    text_secondary: ColorToken
    text_muted: ColorToken
    text_inverse: ColorToken

    # Border colors
    border: ColorToken
    border_focus: ColorToken

    # Interactive states
    hover: ColorToken
    active: ColorToken
    disabled: ColorToken

    @classmethod
    def default(cls) -> ThemeColors:
        """Create default color scheme."""
        return cls(
            # Primary
            primary=ColorToken("primary", Colors.PRIMARY_600, Colors.PRIMARY_400),
            secondary=ColorToken("secondary", Colors.GRAY_600, Colors.GRAY_400),
            accent=ColorToken("accent", Colors.PRIMARY_500, Colors.PRIMARY_300),
            # State
            success=ColorToken("success", Colors.SUCCESS_600, Colors.SUCCESS_500),
            warning=ColorToken("warning", Colors.WARNING_600, Colors.WARNING_500),
            error=ColorToken("error", Colors.ERROR_600, Colors.ERROR_500),
            info=ColorToken("info", Colors.INFO_600, Colors.INFO_500),
            # Surface
            background=ColorToken("background", Colors.WHITE, Colors.GRAY_900),
            surface=ColorToken("surface", Colors.GRAY_50, Colors.GRAY_800),
            surface_variant=ColorToken("surface_variant", Colors.GRAY_100, Colors.GRAY_700),
            # Text
            text_primary=ColorToken("text_primary", Colors.GRAY_900, Colors.GRAY_50),
            text_secondary=ColorToken("text_secondary", Colors.GRAY_700, Colors.GRAY_300),
            text_muted=ColorToken("text_muted", Colors.GRAY_500, Colors.GRAY_500),
            text_inverse=ColorToken("text_inverse", Colors.WHITE, Colors.GRAY_900),
            # Border
            border=ColorToken("border", Colors.GRAY_200, Colors.GRAY_700),
            border_focus=ColorToken("border_focus", Colors.PRIMARY_500, Colors.PRIMARY_400),
            # Interactive
            hover=ColorToken("hover", Colors.GRAY_100, Colors.GRAY_700),
            active=ColorToken("active", Colors.GRAY_200, Colors.GRAY_600),
            disabled=ColorToken("disabled", Colors.GRAY_300, Colors.GRAY_600),
        )


@dataclass(frozen=True)
class Theme:
    """
    Complete theme definition.

    Contains all styling tokens for consistent widget appearance.

    Example:
        theme = Theme.create(mode=ThemeMode.DARK)

        # Get a color for current mode
        bg_color = theme.color(theme.colors.background)

        # Get spacing
        padding = theme.spacing.get(SpacingToken.MD)

        # Get animation timing
        duration = theme.animation.normal
    """

    mode: ThemeMode
    colors: ThemeColors
    spacing: Spacing
    animation: AnimationTiming

    # Typography (terminal-focused)
    monospace: bool = True  # Always true for terminal

    # Borders
    border_radius: int = 0  # Terminal has no curves (0 = square)
    focus_ring_width: int = 1

    @classmethod
    def create(
        cls,
        mode: ThemeMode = ThemeMode.DARK,
        colors: ThemeColors | None = None,
        spacing: Spacing | None = None,
        animation: AnimationTiming | None = None,
    ) -> Theme:
        """
        Create a theme.

        Args:
            mode: Light or dark mode
            colors: Custom color scheme
            spacing: Custom spacing scale
            animation: Custom animation timing

        Returns:
            Configured Theme
        """
        return cls(
            mode=mode,
            colors=colors or ThemeColors.default(),
            spacing=spacing or Spacing(),
            animation=animation or AnimationTiming(),
        )

    def color(self, token: ColorToken) -> RGB:
        """Get resolved color for current mode."""
        return token.resolve(self.mode)

    def with_mode(self, mode: ThemeMode) -> Theme:
        """Create a copy with different mode."""
        return Theme(
            mode=mode,
            colors=self.colors,
            spacing=self.spacing,
            animation=self.animation,
            monospace=self.monospace,
            border_radius=self.border_radius,
            focus_ring_width=self.focus_ring_width,
        )

    # Convenience accessors
    @property
    def primary(self) -> RGB:
        return self.color(self.colors.primary)

    @property
    def secondary(self) -> RGB:
        return self.color(self.colors.secondary)

    @property
    def background(self) -> RGB:
        return self.color(self.colors.background)

    @property
    def surface(self) -> RGB:
        return self.color(self.colors.surface)

    @property
    def text(self) -> RGB:
        return self.color(self.colors.text_primary)

    @property
    def text_muted(self) -> RGB:
        return self.color(self.colors.text_muted)

    @property
    def border(self) -> RGB:
        return self.color(self.colors.border)

    @property
    def success(self) -> RGB:
        return self.color(self.colors.success)

    @property
    def warning(self) -> RGB:
        return self.color(self.colors.warning)

    @property
    def error(self) -> RGB:
        return self.color(self.colors.error)


# =============================================================================
# Theme Provider
# =============================================================================


@dataclass
class ThemeProvider:
    """
    Theme provider with reactive switching.

    Provides the current theme as a Signal for reactive updates.

    Example:
        provider = ThemeProvider.create(ThemeMode.DARK)

        # Subscribe to theme changes
        provider.signal.subscribe(lambda theme: redraw_ui(theme))

        # Toggle mode
        provider.toggle_mode()

        # Or set specific mode
        provider.set_mode(ThemeMode.LIGHT)
    """

    _signal: Signal[Theme] = field(default_factory=lambda: Signal.of(Theme.create()))
    _system_mode: ThemeMode = ThemeMode.DARK  # Default if system detection fails

    @classmethod
    def create(
        cls,
        mode: ThemeMode = ThemeMode.DARK,
        colors: ThemeColors | None = None,
    ) -> ThemeProvider:
        """Create a theme provider."""
        theme = Theme.create(mode=mode, colors=colors)
        return cls(_signal=Signal.of(theme))

    @property
    def theme(self) -> Theme:
        """Get current theme."""
        return self._signal.value

    @property
    def signal(self) -> Signal[Theme]:
        """Signal for theme changes."""
        return self._signal

    @property
    def mode(self) -> ThemeMode:
        """Current theme mode."""
        return self._signal.value.mode

    def set_mode(self, mode: ThemeMode) -> None:
        """Set theme mode."""
        current = self._signal.value
        if mode == ThemeMode.SYSTEM:
            mode = self._system_mode
        self._signal.set(current.with_mode(mode))

    def toggle_mode(self) -> ThemeMode:
        """Toggle between light and dark mode."""
        current_mode = self._signal.value.mode
        new_mode = ThemeMode.LIGHT if current_mode == ThemeMode.DARK else ThemeMode.DARK
        self.set_mode(new_mode)
        return new_mode

    def set_system_mode(self, mode: ThemeMode) -> None:
        """Set system mode preference (for SYSTEM mode)."""
        self._system_mode = mode
        if self._signal.value.mode == ThemeMode.SYSTEM:
            self.set_mode(ThemeMode.SYSTEM)

    def subscribe(self, callback: Callable[[Theme], None]) -> Callable[[], None]:
        """Subscribe to theme changes."""
        return self._signal.subscribe(callback)


# =============================================================================
# Factory Functions
# =============================================================================


def create_theme(
    mode: ThemeMode = ThemeMode.DARK,
    colors: ThemeColors | None = None,
) -> Theme:
    """Create a theme with defaults."""
    return Theme.create(mode=mode, colors=colors)


def create_light_theme(colors: ThemeColors | None = None) -> Theme:
    """Create a light theme."""
    return Theme.create(mode=ThemeMode.LIGHT, colors=colors)


def create_dark_theme(colors: ThemeColors | None = None) -> Theme:
    """Create a dark theme."""
    return Theme.create(mode=ThemeMode.DARK, colors=colors)


def create_theme_provider(
    mode: ThemeMode = ThemeMode.DARK,
    colors: ThemeColors | None = None,
) -> ThemeProvider:
    """Create a theme provider."""
    return ThemeProvider.create(mode=mode, colors=colors)


# =============================================================================
# ANSI Helpers for Terminal Rendering
# =============================================================================


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"
ANSI_BLINK = "\033[5m"
ANSI_REVERSE = "\033[7m"


def styled_text(
    text: str,
    fg: RGB | None = None,
    bg: RGB | None = None,
    bold: bool = False,
    dim: bool = False,
    underline: bool = False,
) -> str:
    """
    Create ANSI-styled text.

    Args:
        text: Text to style
        fg: Foreground color
        bg: Background color
        bold: Bold text
        dim: Dim text
        underline: Underlined text

    Returns:
        ANSI-escaped styled text
    """
    codes: list[str] = []

    if bold:
        codes.append(ANSI_BOLD)
    if dim:
        codes.append(ANSI_DIM)
    if underline:
        codes.append(ANSI_UNDERLINE)
    if fg:
        codes.append(fg.to_ansi_fg())
    if bg:
        codes.append(bg.to_ansi_bg())

    if not codes:
        return text

    return "".join(codes) + text + ANSI_RESET


def theme_styled(
    text: str,
    theme: Theme,
    color_token: ColorToken,
    bg_token: ColorToken | None = None,
    bold: bool = False,
) -> str:
    """
    Create styled text using theme colors.

    Args:
        text: Text to style
        theme: Current theme
        color_token: Foreground color token
        bg_token: Optional background color token
        bold: Bold text

    Returns:
        ANSI-escaped styled text
    """
    fg = theme.color(color_token)
    bg = theme.color(bg_token) if bg_token else None
    return styled_text(text, fg=fg, bg=bg, bold=bold)
