"""
Tests for NotebookTheme - CSS generation for notebooks.
"""

from __future__ import annotations

import pytest
from agents.i.reactive.adapters.marimo_theme import (
    NotebookTheme,
    create_notebook_theme,
    inject_theme_css,
)

# ============================================================
# Theme Creation Tests
# ============================================================


class TestThemeCreation:
    """Test theme creation and defaults."""

    def test_default_theme(self):
        """Default theme has expected values."""
        theme = NotebookTheme()

        assert theme.primary == "#3b82f6"
        assert theme.surface == "#1a1a2e"
        assert theme.text == "#e0e0e0"
        assert theme.dark_mode is True

    def test_light_theme(self):
        """Light theme factory works."""
        theme = NotebookTheme.light()

        assert theme.dark_mode is False
        assert theme.surface == "#f8f9fa"
        assert theme.text == "#1a1a1a"

    def test_dark_theme(self):
        """Dark theme factory works."""
        theme = NotebookTheme.dark()

        assert theme.dark_mode is True

    def test_marimo_theme(self):
        """Marimo-aware theme uses CSS variables."""
        theme = NotebookTheme.from_marimo()

        assert "var(--marimo-" in theme.primary
        assert "var(--marimo-" in theme.surface
        assert "var(--marimo-" in theme.text

    def test_custom_theme(self):
        """Custom theme values work."""
        theme = NotebookTheme(
            primary="#ff0000",
            surface="#000000",
            text="#ffffff",
        )

        assert theme.primary == "#ff0000"
        assert theme.surface == "#000000"
        assert theme.text == "#ffffff"


# ============================================================
# CSS Generation Tests
# ============================================================


class TestCssGeneration:
    """Test CSS generation methods."""

    def test_to_css_contains_variables(self):
        """to_css() includes CSS variables."""
        theme = NotebookTheme()
        css = theme.to_css()

        assert "--kgents-primary:" in css
        assert "--kgents-surface:" in css
        assert "--kgents-text:" in css
        assert "--kgents-error:" in css

    def test_to_css_contains_animations(self):
        """to_css() includes animations."""
        theme = NotebookTheme()
        css = theme.to_css()

        assert "@keyframes kgents-breathe" in css
        assert ".kgents-breathing" in css

    def test_to_css_contains_phase_styles(self):
        """to_css() includes phase-specific styles."""
        theme = NotebookTheme()
        css = theme.to_css()

        assert ".kgents-phase-active" in css
        assert ".kgents-phase-error" in css

    def test_to_inline_style(self):
        """to_inline_style() generates inline CSS."""
        theme = NotebookTheme(
            primary="#123456",
            surface="#abcdef",
            text="#fedcba",
        )
        style = theme.to_inline_style()

        assert "font-family:" in style
        assert "color:" in style
        assert "background:" in style

    def test_to_css_vars_dict(self):
        """to_css_vars() returns dict of variables."""
        theme = NotebookTheme()
        vars_dict = theme.to_css_vars()

        assert isinstance(vars_dict, dict)
        assert "--kgents-primary" in vars_dict
        assert "--kgents-surface" in vars_dict
        assert vars_dict["--kgents-primary"] == theme.primary


# ============================================================
# Helper Function Tests
# ============================================================


class TestHelperFunctions:
    """Test helper functions."""

    def test_inject_theme_css_default(self):
        """inject_theme_css() with default theme."""
        html = inject_theme_css()

        assert html.startswith("<style>")
        assert html.endswith("</style>")
        assert "--kgents-" in html

    def test_inject_theme_css_custom(self):
        """inject_theme_css() with custom theme."""
        theme = NotebookTheme(primary="#custom")
        html = inject_theme_css(theme)

        assert "#custom" in html

    def test_create_notebook_theme_dark(self):
        """create_notebook_theme() dark mode."""
        theme = create_notebook_theme(dark_mode=True, inherit_marimo=False)

        assert theme.dark_mode is True

    def test_create_notebook_theme_light(self):
        """create_notebook_theme() light mode."""
        theme = create_notebook_theme(dark_mode=False, inherit_marimo=False)

        assert theme.dark_mode is False

    def test_create_notebook_theme_marimo(self):
        """create_notebook_theme() with marimo inheritance."""
        theme = create_notebook_theme(inherit_marimo=True)

        assert "var(--marimo-" in theme.primary


# ============================================================
# Immutability Tests
# ============================================================


class TestImmutability:
    """Test that NotebookTheme is immutable."""

    def test_theme_is_frozen(self):
        """NotebookTheme is a frozen dataclass."""
        theme = NotebookTheme()

        with pytest.raises(Exception):  # FrozenInstanceError
            theme.primary = "#000000"  # type: ignore


# ============================================================
# Integration Tests
# ============================================================


class TestIntegration:
    """Integration tests for theme usage."""

    def test_css_valid_for_browser(self):
        """Generated CSS is valid (basic check)."""
        theme = NotebookTheme()
        css = theme.to_css()

        # Basic CSS validity checks
        assert css.count("{") == css.count("}")
        assert ":root" in css
        assert ";" in css

    def test_all_color_values_present(self):
        """All color values appear in CSS."""
        theme = NotebookTheme(
            primary="#111111",
            surface="#222222",
            text="#333333",
            success="#444444",
            warning="#555555",
            error="#666666",
        )
        css = theme.to_css()

        assert "#111111" in css
        assert "#222222" in css
        assert "#333333" in css
        assert "#444444" in css
        assert "#555555" in css
        assert "#666666" in css
