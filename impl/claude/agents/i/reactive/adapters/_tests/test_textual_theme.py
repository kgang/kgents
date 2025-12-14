"""Tests for ThemeBinding - Theme → Textual CSS bridge."""

from __future__ import annotations

import pytest
from agents.i.reactive.adapters.textual_theme import (
    ThemeBinding,
    create_theme_binding,
    generate_theme_css,
    get_dark_css,
    get_light_css,
)
from agents.i.reactive.pipeline.theme import (
    RGB,
    Theme,
    ThemeColors,
    ThemeMode,
    ThemeProvider,
    create_theme,
    create_theme_provider,
)

# =============================================================================
# ThemeBinding Creation Tests
# =============================================================================


class TestThemeBindingCreation:
    """Test ThemeBinding creation."""

    def test_create_binding(self) -> None:
        """Create a ThemeBinding."""
        binding = ThemeBinding()

        assert binding._app is None
        assert binding._unsubscribe is None

    def test_create_with_factory(self) -> None:
        """Create with factory function."""
        binding = create_theme_binding()

        assert isinstance(binding, ThemeBinding)


# =============================================================================
# CSS Generation Tests
# =============================================================================


class TestThemeBindingCSS:
    """Test CSS generation."""

    def test_generates_css_string(self) -> None:
        """Binding generates CSS string from theme."""
        theme = create_theme(ThemeMode.DARK)
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert isinstance(css, str)
        assert len(css) > 0

    def test_css_contains_screen_selector(self) -> None:
        """CSS contains Screen selector."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "Screen {" in css

    def test_css_contains_background(self) -> None:
        """CSS contains background color."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "background:" in css

    def test_css_contains_widget_color(self) -> None:
        """CSS contains Widget text color."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "Widget {" in css
        assert "color:" in css

    def test_css_contains_button_styles(self) -> None:
        """CSS contains Button styles."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "Button {" in css
        assert "Button:hover {" in css
        assert "Button:focus {" in css

    def test_css_contains_input_styles(self) -> None:
        """CSS contains Input styles."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "Input {" in css
        assert "Input:focus {" in css

    def test_css_contains_surface_classes(self) -> None:
        """CSS contains surface utility classes."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert ".surface {" in css
        assert ".surface-variant {" in css

    def test_css_contains_text_classes(self) -> None:
        """CSS contains text utility classes."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert ".text-muted {" in css
        assert ".text-secondary {" in css

    def test_css_contains_status_colors(self) -> None:
        """CSS contains status color classes."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert ".success {" in css
        assert ".warning {" in css
        assert ".error {" in css

    def test_css_contains_card_styles(self) -> None:
        """CSS contains card styles."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert ".card {" in css
        assert ".card:focus-within {" in css

    def test_css_contains_header_footer(self) -> None:
        """CSS contains Header and Footer styles."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "Header {" in css
        assert "Footer {" in css

    def test_css_contains_datatable(self) -> None:
        """CSS contains DataTable styles."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "DataTable {" in css


class TestThemeBindingColorOutput:
    """Test color output format."""

    def test_rgb_to_css_format(self) -> None:
        """RGB converts to CSS rgb() format."""
        binding = ThemeBinding()
        rgb = RGB(255, 128, 0)

        css_color = binding._rgb_to_css(rgb)

        assert css_color == "rgb(255, 128, 0)"

    def test_rgb_black(self) -> None:
        """Black RGB converts correctly."""
        binding = ThemeBinding()
        rgb = RGB(0, 0, 0)

        css_color = binding._rgb_to_css(rgb)

        assert css_color == "rgb(0, 0, 0)"

    def test_rgb_white(self) -> None:
        """White RGB converts correctly."""
        binding = ThemeBinding()
        rgb = RGB(255, 255, 255)

        css_color = binding._rgb_to_css(rgb)

        assert css_color == "rgb(255, 255, 255)"


class TestDarkLightCSS:
    """Test dark/light mode CSS differences."""

    def test_dark_mode_css(self) -> None:
        """Dark mode generates appropriate CSS."""
        theme = create_theme(ThemeMode.DARK)
        binding = ThemeBinding()

        css = binding.to_css(theme)

        # Dark mode should have dark background colors
        assert "rgb(24, 24, 27)" in css  # GRAY_900 background

    def test_light_mode_css(self) -> None:
        """Light mode generates appropriate CSS."""
        theme = create_theme(ThemeMode.LIGHT)
        binding = ThemeBinding()

        css = binding.to_css(theme)

        # Light mode should have light background colors
        assert "rgb(255, 255, 255)" in css  # WHITE background

    def test_dark_light_differ(self) -> None:
        """Dark and light CSS are different."""
        dark_theme = create_theme(ThemeMode.DARK)
        light_theme = create_theme(ThemeMode.LIGHT)
        binding = ThemeBinding()

        dark_css = binding.to_css(dark_theme)
        light_css = binding.to_css(light_theme)

        assert dark_css != light_css


# =============================================================================
# CSS Variables Tests
# =============================================================================


class TestThemeBindingCSSVars:
    """Test CSS variable generation."""

    def test_generates_css_vars(self) -> None:
        """Binding generates CSS variables dict."""
        theme = create_theme()
        binding = ThemeBinding()

        vars_dict = binding.to_tcss_vars(theme)

        assert isinstance(vars_dict, dict)

    def test_has_primary_var(self) -> None:
        """Variables include --primary."""
        theme = create_theme()
        binding = ThemeBinding()

        vars_dict = binding.to_tcss_vars(theme)

        assert "--primary" in vars_dict

    def test_has_background_var(self) -> None:
        """Variables include --background."""
        theme = create_theme()
        binding = ThemeBinding()

        vars_dict = binding.to_tcss_vars(theme)

        assert "--background" in vars_dict

    def test_has_text_var(self) -> None:
        """Variables include --text."""
        theme = create_theme()
        binding = ThemeBinding()

        vars_dict = binding.to_tcss_vars(theme)

        assert "--text" in vars_dict

    def test_has_status_vars(self) -> None:
        """Variables include status colors."""
        theme = create_theme()
        binding = ThemeBinding()

        vars_dict = binding.to_tcss_vars(theme)

        assert "--success" in vars_dict
        assert "--warning" in vars_dict
        assert "--error" in vars_dict


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestCSSFactoryFunctions:
    """Test CSS generation factory functions."""

    def test_generate_theme_css(self) -> None:
        """generate_theme_css creates CSS."""
        css = generate_theme_css()

        assert isinstance(css, str)
        assert len(css) > 0

    def test_generate_dark_css(self) -> None:
        """generate_theme_css creates dark CSS."""
        css = generate_theme_css(ThemeMode.DARK)

        assert "rgb(24, 24, 27)" in css

    def test_generate_light_css(self) -> None:
        """generate_theme_css creates light CSS."""
        css = generate_theme_css(ThemeMode.LIGHT)

        assert "rgb(255, 255, 255)" in css

    def test_get_dark_css(self) -> None:
        """get_dark_css helper works."""
        css = get_dark_css()

        assert isinstance(css, str)
        assert "rgb(24, 24, 27)" in css

    def test_get_light_css(self) -> None:
        """get_light_css helper works."""
        css = get_light_css()

        assert isinstance(css, str)
        assert "rgb(255, 255, 255)" in css


# =============================================================================
# Binding Lifecycle Tests
# =============================================================================


class TestThemeBindingLifecycle:
    """Test binding lifecycle."""

    def test_unbind_clears_state(self) -> None:
        """Unbind clears app and unsubscribe."""
        from typing import cast

        from textual.app import App

        binding = ThemeBinding()
        binding._app = cast(App[object], object())  # Mock app
        binding._unsubscribe = lambda: None

        binding.unbind()

        assert binding._app is None
        assert binding._unsubscribe is None


# =============================================================================
# CSS Output Quality Tests
# =============================================================================


class TestCSSOutputQuality:
    """Test CSS output quality."""

    def test_css_is_valid_format(self) -> None:
        """CSS has valid selector format."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        # Check for basic CSS structure
        assert "{" in css
        assert "}" in css
        assert ":" in css
        assert ";" in css

    def test_css_has_comments(self) -> None:
        """CSS includes helpful comments."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        assert "/* kgents theme" in css

    def test_css_properly_formatted(self) -> None:
        """CSS has proper formatting (newlines, indentation)."""
        theme = create_theme()
        binding = ThemeBinding()

        css = binding.to_css(theme)

        # Should have newlines for readability
        assert "\n" in css
        # Should have indentation
        assert "    " in css
