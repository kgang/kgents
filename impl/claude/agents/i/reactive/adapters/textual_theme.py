"""
ThemeBinding: Generate Textual CSS from Theme tokens.

Bridges the reactive Theme system to Textual's CSS theming.

Usage:
    from agents.i.reactive.adapters import ThemeBinding
    from agents.i.reactive.pipeline.theme import ThemeProvider, ThemeMode

    # Create theme provider
    provider = ThemeProvider.create(ThemeMode.DARK)

    # Create binding
    binding = ThemeBinding()

    # Bind to Textual app
    binding.bind(app, provider)

    # Toggle theme - CSS updates automatically
    provider.toggle_mode()
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from agents.i.reactive.pipeline.theme import (
    RGB,
    ColorToken,
    SpacingToken,
    Theme,
    ThemeColors,
    ThemeMode,
    ThemeProvider,
)

if TYPE_CHECKING:
    from textual.app import App


class ThemeBinding:
    """
    Generates Textual CSS from Theme tokens.

    The binding:
    1. Converts Theme colors to CSS variables
    2. Generates spacing scale as CSS
    3. Subscribes to ThemeProvider for reactive updates

    Example:
        provider = ThemeProvider.create(ThemeMode.DARK)
        binding = ThemeBinding()

        # Generate CSS string
        css = binding.to_css(provider.theme)

        # Or bind to app for reactive updates
        binding.bind(app, provider)
    """

    def __init__(self) -> None:
        self._unsubscribe: Callable[[], None] | None = None
        self._app: App[object] | None = None
        self._css_class: str = "kgents-theme"

    def to_css(self, theme: Theme) -> str:
        """
        Generate Textual CSS from Theme.

        Args:
            theme: Theme to convert

        Returns:
            CSS string with color variables and styles
        """
        lines: list[str] = []

        # Root selector for CSS variables
        lines.append("/* kgents theme - auto-generated */")
        lines.append("")

        # Generate color palette CSS
        colors = theme.colors

        # Core colors
        lines.append("Screen {")
        lines.append(f"    background: {self._rgb_to_css(theme.background)};")
        lines.append("}")
        lines.append("")

        # Widget defaults
        lines.append("Widget {")
        lines.append(f"    color: {self._rgb_to_css(theme.text)};")
        lines.append("}")
        lines.append("")

        # Button styling
        lines.append("Button {")
        lines.append(f"    background: {self._rgb_to_css(theme.primary)};")
        lines.append(f"    color: {self._rgb_to_css(theme.color(colors.text_inverse))};")
        lines.append(f"    border: tall {self._rgb_to_css(theme.color(colors.border))};")
        lines.append("}")
        lines.append("")

        lines.append("Button:hover {")
        lines.append(f"    background: {self._rgb_to_css(theme.color(colors.hover))};")
        lines.append("}")
        lines.append("")

        lines.append("Button:focus {")
        lines.append(f"    border: tall {self._rgb_to_css(theme.color(colors.border_focus))};")
        lines.append("}")
        lines.append("")

        # Input styling
        lines.append("Input {")
        lines.append(f"    background: {self._rgb_to_css(theme.surface)};")
        lines.append(f"    border: tall {self._rgb_to_css(theme.border)};")
        lines.append("}")
        lines.append("")

        lines.append("Input:focus {")
        lines.append(f"    border: tall {self._rgb_to_css(theme.color(colors.border_focus))};")
        lines.append("}")
        lines.append("")

        # Container surfaces
        lines.append(".surface {")
        lines.append(f"    background: {self._rgb_to_css(theme.surface)};")
        lines.append("}")
        lines.append("")

        lines.append(".surface-variant {")
        lines.append(f"    background: {self._rgb_to_css(theme.color(colors.surface_variant))};")
        lines.append("}")
        lines.append("")

        # Text variants
        lines.append(".text-muted {")
        lines.append(f"    color: {self._rgb_to_css(theme.text_muted)};")
        lines.append("}")
        lines.append("")

        lines.append(".text-secondary {")
        lines.append(f"    color: {self._rgb_to_css(theme.secondary)};")
        lines.append("}")
        lines.append("")

        # Status colors
        lines.append(".success {")
        lines.append(f"    color: {self._rgb_to_css(theme.success)};")
        lines.append("}")
        lines.append("")

        lines.append(".warning {")
        lines.append(f"    color: {self._rgb_to_css(theme.warning)};")
        lines.append("}")
        lines.append("")

        lines.append(".error {")
        lines.append(f"    color: {self._rgb_to_css(theme.error)};")
        lines.append("}")
        lines.append("")

        # Focus ring (for custom focus indicators)
        lines.append(".focus-ring {")
        lines.append(f"    border: tall {self._rgb_to_css(theme.color(colors.border_focus))};")
        lines.append("}")
        lines.append("")

        # Cards
        lines.append(".card {")
        lines.append(f"    background: {self._rgb_to_css(theme.surface)};")
        lines.append(f"    border: tall {self._rgb_to_css(theme.border)};")
        lines.append("    padding: 1 2;")
        lines.append("}")
        lines.append("")

        lines.append(".card:focus-within {")
        lines.append(f"    border: tall {self._rgb_to_css(theme.color(colors.border_focus))};")
        lines.append("}")
        lines.append("")

        # Header/Footer
        lines.append("Header {")
        lines.append(f"    background: {self._rgb_to_css(theme.primary)};")
        lines.append(f"    color: {self._rgb_to_css(theme.color(colors.text_inverse))};")
        lines.append("}")
        lines.append("")

        lines.append("Footer {")
        lines.append(f"    background: {self._rgb_to_css(theme.color(colors.surface_variant))};")
        lines.append("}")
        lines.append("")

        # DataTable
        lines.append("DataTable {")
        lines.append(f"    background: {self._rgb_to_css(theme.surface)};")
        lines.append("}")
        lines.append("")

        lines.append("DataTable > .datatable--header {")
        lines.append(f"    background: {self._rgb_to_css(theme.color(colors.surface_variant))};")
        lines.append(f"    color: {self._rgb_to_css(theme.text)};")
        lines.append("}")
        lines.append("")

        lines.append("DataTable > .datatable--cursor {")
        lines.append(f"    background: {self._rgb_to_css(theme.primary)};")
        lines.append(f"    color: {self._rgb_to_css(theme.color(colors.text_inverse))};")
        lines.append("}")
        lines.append("")

        return "\n".join(lines)

    def to_tcss_vars(self, theme: Theme) -> dict[str, str]:
        """
        Generate CSS variable dict from Theme.

        Returns a dict that can be passed to app.set_css_variables().

        Args:
            theme: Theme to convert

        Returns:
            Dict of CSS variable name -> value
        """
        colors = theme.colors

        return {
            "--primary": self._rgb_to_css(theme.primary),
            "--secondary": self._rgb_to_css(theme.secondary),
            "--background": self._rgb_to_css(theme.background),
            "--surface": self._rgb_to_css(theme.surface),
            "--text": self._rgb_to_css(theme.text),
            "--text-muted": self._rgb_to_css(theme.text_muted),
            "--border": self._rgb_to_css(theme.border),
            "--success": self._rgb_to_css(theme.success),
            "--warning": self._rgb_to_css(theme.warning),
            "--error": self._rgb_to_css(theme.error),
            "--border-focus": self._rgb_to_css(theme.color(colors.border_focus)),
        }

    def bind(self, app: App[object], provider: ThemeProvider) -> Callable[[], None]:
        """
        Bind to a Textual App for reactive theme updates.

        Args:
            app: Textual App to bind to
            provider: ThemeProvider for reactive updates

        Returns:
            Unsubscribe function
        """
        self._app = app

        def on_theme_change(theme: Theme) -> None:
            if self._app:
                # Generate CSS (future: inject into app stylesheet)
                _ = self.to_css(theme)
                # Force refresh of all widgets
                self._app.refresh()

        # Subscribe and store unsubscribe
        self._unsubscribe = provider.subscribe(on_theme_change)

        # Initial CSS generation
        on_theme_change(provider.theme)

        return self._unsubscribe

    def unbind(self) -> None:
        """Unbind from app and provider."""
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        self._app = None

    @staticmethod
    def _rgb_to_css(rgb: RGB) -> str:
        """Convert RGB to CSS color string."""
        return f"rgb({rgb.r}, {rgb.g}, {rgb.b})"


def create_theme_binding() -> ThemeBinding:
    """Create a ThemeBinding instance."""
    return ThemeBinding()


def generate_theme_css(
    mode: ThemeMode = ThemeMode.DARK,
    colors: ThemeColors | None = None,
) -> str:
    """
    Generate Textual CSS for a theme.

    Args:
        mode: Light or dark mode
        colors: Custom color scheme

    Returns:
        CSS string
    """
    from agents.i.reactive.pipeline.theme import Theme

    theme = Theme.create(mode=mode, colors=colors)
    binding = ThemeBinding()
    return binding.to_css(theme)


def get_dark_css() -> str:
    """Get CSS for dark theme."""
    return generate_theme_css(ThemeMode.DARK)


def get_light_css() -> str:
    """Get CSS for light theme."""
    return generate_theme_css(ThemeMode.LIGHT)
