"""
NotebookTheme: Generate CSS for notebook styling.

Bridges kgents Theme tokens to CSS variables compatible with marimo and Jupyter.
Generates inline styles and CSS classes for notebook rendering.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NotebookTheme:
    """
    Theme configuration for notebook rendering.

    Maps kgents Theme tokens to CSS variables that work in marimo/Jupyter.
    Provides both inline style generation and CSS class definitions.

    Example:
        theme = NotebookTheme(
            primary="#3b82f6",
            surface="#1a1a2e",
            text="#e0e0e0",
            dark_mode=True,
        )

        css = theme.to_css()  # Full CSS with variables
        style = theme.to_inline_style()  # Inline style string
    """

    primary: str = "#3b82f6"
    surface: str = "#1a1a2e"
    surface_border: str = "#333344"
    text: str = "#e0e0e0"
    text_muted: str = "#888888"
    success: str = "#22c55e"
    warning: str = "#eab308"
    error: str = "#ef4444"
    font_mono: str = '"Monaco", "Menlo", monospace'
    dark_mode: bool = True

    def to_css(self) -> str:
        """
        Generate complete CSS with variables and animations.

        Returns:
            CSS string that can be injected into notebook
        """
        return f"""
/* kgents Notebook Theme */
:root {{
    --kgents-primary: {self.primary};
    --kgents-surface: {self.surface};
    --kgents-surface-border: {self.surface_border};
    --kgents-text: {self.text};
    --kgents-text-muted: {self.text_muted};
    --kgents-success: {self.success};
    --kgents-warning: {self.warning};
    --kgents-error: {self.error};
    --kgents-font-mono: {self.font_mono};
}}

.kgents-widget {{
    font-family: var(--kgents-font-mono);
    color: var(--kgents-text);
}}

/* Agent Card Breathing Animation */
@keyframes kgents-breathe {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.92; transform: scale(0.995); }}
}}

.kgents-breathing {{
    animation: kgents-breathe 3s ease-in-out infinite;
}}

/* Phase Glow Effects */
.kgents-phase-active {{
    border-left-color: var(--kgents-success) !important;
}}

.kgents-phase-error {{
    border-left-color: var(--kgents-error) !important;
}}

.kgents-phase-waiting {{
    border-left-color: var(--kgents-warning) !important;
}}
"""

    def to_inline_style(self) -> str:
        """
        Generate inline style string for embedding.

        Returns:
            Inline CSS style string
        """
        return (
            f"font-family: {self.font_mono}; "
            f"color: {self.text}; "
            f"background: {self.surface}; "
            f"border-color: {self.surface_border};"
        )

    def to_css_vars(self) -> dict[str, str]:
        """
        Get theme as CSS variable dictionary.

        Returns:
            Dict mapping variable names to values
        """
        return {
            "--kgents-primary": self.primary,
            "--kgents-surface": self.surface,
            "--kgents-surface-border": self.surface_border,
            "--kgents-text": self.text,
            "--kgents-text-muted": self.text_muted,
            "--kgents-success": self.success,
            "--kgents-warning": self.warning,
            "--kgents-error": self.error,
            "--kgents-font-mono": self.font_mono,
        }

    @classmethod
    def light(cls) -> NotebookTheme:
        """Create a light mode theme."""
        return cls(
            primary="#2563eb",
            surface="#f8f9fa",
            surface_border="#e0e0e0",
            text="#1a1a1a",
            text_muted="#666666",
            success="#16a34a",
            warning="#ca8a04",
            error="#dc2626",
            dark_mode=False,
        )

    @classmethod
    def dark(cls) -> NotebookTheme:
        """Create a dark mode theme (default)."""
        return cls()

    @classmethod
    def from_marimo(cls) -> NotebookTheme:
        """
        Create theme that inherits from marimo's theme variables.

        Uses CSS variable fallbacks so marimo's theme takes precedence.
        """
        return cls(
            primary="var(--marimo-accent-color, #3b82f6)",
            surface="var(--marimo-bg-secondary, #1a1a2e)",
            surface_border="var(--marimo-border-color, #333344)",
            text="var(--marimo-text-color, #e0e0e0)",
            text_muted="var(--marimo-text-muted, #888888)",
            font_mono='var(--marimo-monospace-font, "Monaco", "Menlo", monospace)',
        )


def inject_theme_css(theme: NotebookTheme | None = None) -> str:
    """
    Generate HTML style tag with theme CSS.

    Args:
        theme: Theme to use, defaults to marimo-aware theme

    Returns:
        HTML style tag string
    """
    theme = theme or NotebookTheme.from_marimo()
    return f"<style>{theme.to_css()}</style>"


def create_notebook_theme(
    *,
    dark_mode: bool = True,
    inherit_marimo: bool = True,
) -> NotebookTheme:
    """
    Create a notebook theme.

    Args:
        dark_mode: Use dark mode colors
        inherit_marimo: Inherit from marimo's CSS variables

    Returns:
        NotebookTheme instance
    """
    if inherit_marimo:
        return NotebookTheme.from_marimo()
    return NotebookTheme.dark() if dark_mode else NotebookTheme.light()
