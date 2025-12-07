"""
zen-agents Theme System

Defines color themes that can be switched at runtime.
Each theme provides a consistent color palette for the TUI.
"""

from dataclasses import dataclass
from enum import Enum


class ThemeName(Enum):
    """Available theme names."""
    DARK = "dark"
    LIGHT = "light"
    TOKYO_NIGHT = "tokyo_night"
    DRACULA = "dracula"
    NORD = "nord"


@dataclass(frozen=True)
class Theme:
    """A complete color theme."""
    name: ThemeName
    display_name: str

    # Core colors
    background: str
    surface: str
    surface_light: str

    # Text colors
    text: str
    text_muted: str
    text_disabled: str

    # Accent colors
    primary: str
    secondary: str

    # Status colors
    success: str
    warning: str
    error: str

    def to_css_vars(self) -> str:
        """Generate CSS variable definitions for this theme."""
        return f"""
        $background: {self.background};
        $surface: {self.surface};
        $surface-lighten-1: {self.surface_light};
        $text: {self.text};
        $text-muted: {self.text_muted};
        $text-disabled: {self.text_disabled};
        $primary: {self.primary};
        $secondary: {self.secondary};
        $success: {self.success};
        $warning: {self.warning};
        $warning-darken-2: {self.warning};
        $error: {self.error};
        $error-darken-2: {self.error};
        """


# Theme definitions
DARK_THEME = Theme(
    name=ThemeName.DARK,
    display_name="Dark",
    background="#1a1a2e",
    surface="#16213e",
    surface_light="#0f3460",
    text="#e8e8e8",
    text_muted="#a0a0a0",
    text_disabled="#606060",
    primary="#4ecdc4",
    secondary="#ff6b6b",
    success="#4ecdc4",
    warning="#f7dc6f",
    error="#ff6b6b",
)

LIGHT_THEME = Theme(
    name=ThemeName.LIGHT,
    display_name="Light",
    background="#fafafa",
    surface="#ffffff",
    surface_light="#f0f0f0",
    text="#1a1a1a",
    text_muted="#666666",
    text_disabled="#999999",
    primary="#0077b6",
    secondary="#e63946",
    success="#2a9d8f",
    warning="#e9c46a",
    error="#e63946",
)

TOKYO_NIGHT_THEME = Theme(
    name=ThemeName.TOKYO_NIGHT,
    display_name="Tokyo Night",
    background="#1a1b26",
    surface="#24283b",
    surface_light="#414868",
    text="#c0caf5",
    text_muted="#9aa5ce",
    text_disabled="#565f89",
    primary="#7aa2f7",
    secondary="#bb9af7",
    success="#9ece6a",
    warning="#e0af68",
    error="#f7768e",
)

DRACULA_THEME = Theme(
    name=ThemeName.DRACULA,
    display_name="Dracula",
    background="#282a36",
    surface="#44475a",
    surface_light="#6272a4",
    text="#f8f8f2",
    text_muted="#bd93f9",
    text_disabled="#6272a4",
    primary="#8be9fd",
    secondary="#ff79c6",
    success="#50fa7b",
    warning="#f1fa8c",
    error="#ff5555",
)

NORD_THEME = Theme(
    name=ThemeName.NORD,
    display_name="Nord",
    background="#2e3440",
    surface="#3b4252",
    surface_light="#434c5e",
    text="#eceff4",
    text_muted="#d8dee9",
    text_disabled="#4c566a",
    primary="#88c0d0",
    secondary="#b48ead",
    success="#a3be8c",
    warning="#ebcb8b",
    error="#bf616a",
)

# Theme registry
THEMES: dict[ThemeName, Theme] = {
    ThemeName.DARK: DARK_THEME,
    ThemeName.LIGHT: LIGHT_THEME,
    ThemeName.TOKYO_NIGHT: TOKYO_NIGHT_THEME,
    ThemeName.DRACULA: DRACULA_THEME,
    ThemeName.NORD: NORD_THEME,
}

DEFAULT_THEME = ThemeName.DARK


def get_theme(name: ThemeName) -> Theme:
    """Get a theme by name."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])


def get_theme_names() -> list[tuple[ThemeName, str]]:
    """Get all theme names and display names."""
    return [(t.name, t.display_name) for t in THEMES.values()]


__all__ = [
    "Theme",
    "ThemeName",
    "THEMES",
    "DEFAULT_THEME",
    "get_theme",
    "get_theme_names",
    "DARK_THEME",
    "LIGHT_THEME",
    "TOKYO_NIGHT_THEME",
    "DRACULA_THEME",
    "NORD_THEME",
]
