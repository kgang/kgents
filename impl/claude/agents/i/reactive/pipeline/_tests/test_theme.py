"""Tests for Theme System."""

import pytest
from agents.i.reactive.pipeline.theme import (
    ANSI_BOLD,
    ANSI_RESET,
    RGB,
    AnimationTiming,
    Colors,
    ColorToken,
    Spacing,
    SpacingToken,
    Theme,
    ThemeColors,
    ThemeMode,
    ThemeProvider,
    create_dark_theme,
    create_light_theme,
    create_theme,
    create_theme_provider,
    styled_text,
    theme_styled,
)


class TestRGB:
    """Tests for RGB color."""

    def test_create_rgb(self) -> None:
        """RGB can be created."""
        color = RGB(128, 64, 255)

        assert color.r == 128
        assert color.g == 64
        assert color.b == 255

    def test_to_hex(self) -> None:
        """RGB converts to hex string."""
        color = RGB(255, 128, 0)

        assert color.to_hex() == "#ff8000"

    def test_from_hex(self) -> None:
        """RGB can be created from hex."""
        color = RGB.from_hex("#ff8000")

        assert color.r == 255
        assert color.g == 128
        assert color.b == 0

    def test_from_hex_without_hash(self) -> None:
        """RGB.from_hex works without # prefix."""
        color = RGB.from_hex("00ff00")

        assert color.r == 0
        assert color.g == 255
        assert color.b == 0

    def test_to_ansi_fg(self) -> None:
        """RGB converts to ANSI foreground code."""
        color = RGB(128, 64, 32)
        code = color.to_ansi_fg()

        assert code == "\033[38;2;128;64;32m"

    def test_to_ansi_bg(self) -> None:
        """RGB converts to ANSI background code."""
        color = RGB(128, 64, 32)
        code = color.to_ansi_bg()

        assert code == "\033[48;2;128;64;32m"

    def test_blend(self) -> None:
        """RGB blends between colors."""
        black = RGB(0, 0, 0)
        white = RGB(255, 255, 255)

        mid = black.blend(white, 0.5)

        assert mid.r == 128  # Rounded
        assert mid.g == 128
        assert mid.b == 128

    def test_blend_at_zero(self) -> None:
        """blend(t=0) returns first color."""
        a = RGB(100, 100, 100)
        b = RGB(200, 200, 200)

        result = a.blend(b, 0.0)

        assert result.r == 100
        assert result.g == 100
        assert result.b == 100

    def test_blend_at_one(self) -> None:
        """blend(t=1) returns second color."""
        a = RGB(100, 100, 100)
        b = RGB(200, 200, 200)

        result = a.blend(b, 1.0)

        assert result.r == 200
        assert result.g == 200
        assert result.b == 200


class TestColorToken:
    """Tests for color tokens."""

    def test_create_token(self) -> None:
        """ColorToken can be created."""
        token = ColorToken(
            name="primary",
            light=Colors.PRIMARY_600,
            dark=Colors.PRIMARY_400,
        )

        assert token.name == "primary"

    def test_resolve_light(self) -> None:
        """ColorToken resolves light mode color."""
        token = ColorToken(
            name="test",
            light=RGB(100, 100, 100),
            dark=RGB(200, 200, 200),
        )

        color = token.resolve(ThemeMode.LIGHT)

        assert color.r == 100

    def test_resolve_dark(self) -> None:
        """ColorToken resolves dark mode color."""
        token = ColorToken(
            name="test",
            light=RGB(100, 100, 100),
            dark=RGB(200, 200, 200),
        )

        color = token.resolve(ThemeMode.DARK)

        assert color.r == 200


class TestSpacing:
    """Tests for spacing tokens."""

    def test_spacing_values(self) -> None:
        """SpacingToken has expected values."""
        assert SpacingToken.NONE.value == 0
        assert SpacingToken.XS.value == 1
        assert SpacingToken.SM.value == 2
        assert SpacingToken.MD.value == 4
        assert SpacingToken.LG.value == 8
        assert SpacingToken.XL.value == 12
        assert SpacingToken.XXL.value == 16

    def test_spacing_get(self) -> None:
        """Spacing.get returns correct value."""
        spacing = Spacing()

        assert spacing.get(SpacingToken.NONE) == 0
        assert spacing.get(SpacingToken.MD) == 4
        assert spacing.get(SpacingToken.XXL) == 16

    def test_custom_spacing(self) -> None:
        """Custom spacing values work."""
        spacing = Spacing(xs=2, sm=4, md=8, lg=16, xl=24, xxl=32)

        assert spacing.get(SpacingToken.XS) == 2
        assert spacing.get(SpacingToken.MD) == 8
        assert spacing.get(SpacingToken.XXL) == 32


class TestAnimationTiming:
    """Tests for animation timing."""

    def test_default_durations(self) -> None:
        """Default durations are reasonable."""
        timing = AnimationTiming()

        assert timing.instant == 0.0
        assert timing.fast == 100.0
        assert timing.normal == 200.0
        assert timing.slow == 400.0
        assert timing.slower == 600.0

    def test_spring_presets(self) -> None:
        """Spring presets are tuples of (stiffness, damping)."""
        timing = AnimationTiming()

        stiff, damp = timing.spring_stiff
        assert stiff == 300.0
        assert damp == 20.0


class TestTheme:
    """Tests for Theme."""

    def test_create_dark_theme(self) -> None:
        """Dark theme can be created."""
        theme = create_dark_theme()

        assert theme.mode == ThemeMode.DARK

    def test_create_light_theme(self) -> None:
        """Light theme can be created."""
        theme = create_light_theme()

        assert theme.mode == ThemeMode.LIGHT

    def test_color_accessors(self) -> None:
        """Theme has color accessors."""
        theme = create_dark_theme()

        # These should return RGB values
        assert isinstance(theme.primary, RGB)
        assert isinstance(theme.background, RGB)
        assert isinstance(theme.text, RGB)

    def test_color_method(self) -> None:
        """theme.color() resolves token for mode."""
        theme = create_dark_theme()

        primary = theme.color(theme.colors.primary)

        assert isinstance(primary, RGB)
        # Dark mode uses PRIMARY_400
        assert primary == Colors.PRIMARY_400

    def test_with_mode(self) -> None:
        """with_mode creates new theme with different mode."""
        dark = create_dark_theme()
        light = dark.with_mode(ThemeMode.LIGHT)

        assert dark.mode == ThemeMode.DARK
        assert light.mode == ThemeMode.LIGHT
        # Should share same color tokens
        assert dark.colors == light.colors

    def test_light_vs_dark_colors_differ(self) -> None:
        """Light and dark modes have different colors."""
        light = create_light_theme()
        dark = create_dark_theme()

        # Background should differ
        assert light.background != dark.background

        # Light has white-ish background
        assert light.background.r > 200
        # Dark has dark background
        assert dark.background.r < 50


class TestThemeColors:
    """Tests for ThemeColors."""

    def test_default_colors(self) -> None:
        """Default colors include all required tokens."""
        colors = ThemeColors.default()

        assert colors.primary is not None
        assert colors.secondary is not None
        assert colors.success is not None
        assert colors.warning is not None
        assert colors.error is not None
        assert colors.background is not None
        assert colors.surface is not None
        assert colors.text_primary is not None
        assert colors.border is not None


class TestThemeProvider:
    """Tests for ThemeProvider."""

    def test_create_provider(self) -> None:
        """ThemeProvider can be created."""
        provider = create_theme_provider()

        assert provider.theme is not None
        assert provider.mode == ThemeMode.DARK

    def test_set_mode(self) -> None:
        """Can set theme mode."""
        provider = create_theme_provider(mode=ThemeMode.DARK)

        provider.set_mode(ThemeMode.LIGHT)

        assert provider.mode == ThemeMode.LIGHT

    def test_toggle_mode(self) -> None:
        """toggle_mode switches between light and dark."""
        provider = create_theme_provider(mode=ThemeMode.DARK)

        new_mode = provider.toggle_mode()
        assert new_mode == ThemeMode.LIGHT
        assert provider.mode == ThemeMode.LIGHT

        new_mode2 = provider.toggle_mode()
        assert new_mode2 == ThemeMode.DARK
        assert new_mode2 == provider.mode  # type: ignore[comparison-overlap]

    def test_subscribe_to_changes(self) -> None:
        """Can subscribe to theme changes."""
        provider = create_theme_provider(mode=ThemeMode.DARK)
        themes_received: list[Theme] = []

        def on_theme(theme: Theme) -> None:
            themes_received.append(theme)

        provider.subscribe(on_theme)
        provider.set_mode(ThemeMode.LIGHT)

        assert len(themes_received) == 1
        assert themes_received[0].mode == ThemeMode.LIGHT

    def test_signal_access(self) -> None:
        """Signal can be accessed for reactive binding."""
        provider = create_theme_provider()

        signal = provider.signal

        assert signal.value == provider.theme


class TestStyledText:
    """Tests for styled text helpers."""

    def test_plain_text(self) -> None:
        """Plain text with no styling."""
        result = styled_text("hello")

        assert result == "hello"

    def test_text_with_color(self) -> None:
        """Text with foreground color."""
        color = RGB(255, 0, 0)
        result = styled_text("red", fg=color)

        assert "\033[38;2;255;0;0m" in result
        assert "red" in result
        assert ANSI_RESET in result

    def test_text_with_bold(self) -> None:
        """Bold text."""
        result = styled_text("bold", bold=True)

        assert ANSI_BOLD in result
        assert "bold" in result
        assert ANSI_RESET in result

    def test_text_with_background(self) -> None:
        """Text with background color."""
        bg = RGB(0, 0, 255)
        result = styled_text("blue bg", bg=bg)

        assert "\033[48;2;0;0;255m" in result

    def test_combined_styles(self) -> None:
        """Text with multiple styles."""
        fg = RGB(255, 255, 255)
        bg = RGB(0, 0, 0)
        result = styled_text("styled", fg=fg, bg=bg, bold=True, underline=True)

        assert "\033[1m" in result  # bold
        assert "\033[4m" in result  # underline
        assert fg.to_ansi_fg() in result
        assert bg.to_ansi_bg() in result


class TestThemeStyled:
    """Tests for theme-aware styled text."""

    def test_theme_styled_uses_token(self) -> None:
        """theme_styled uses resolved color from token."""
        theme = create_dark_theme()
        result = theme_styled("primary", theme, theme.colors.primary)

        # Should include the primary color's ANSI code
        primary_color = theme.color(theme.colors.primary)
        assert primary_color.to_ansi_fg() in result
        assert "primary" in result

    def test_theme_styled_with_background(self) -> None:
        """theme_styled with background token."""
        theme = create_dark_theme()
        result = theme_styled(
            "button",
            theme,
            theme.colors.text_inverse,
            bg_token=theme.colors.primary,
        )

        bg_color = theme.color(theme.colors.primary)
        assert bg_color.to_ansi_bg() in result


class TestColors:
    """Tests for standard color palette."""

    def test_gray_scale(self) -> None:
        """Gray scale goes from white to black."""
        assert Colors.WHITE.r == 255
        assert Colors.WHITE.g == 255
        assert Colors.WHITE.b == 255

        assert Colors.BLACK.r == 0
        assert Colors.BLACK.g == 0
        assert Colors.BLACK.b == 0

        # Grays should be in between
        assert 0 < Colors.GRAY_500.r < 255

    def test_primary_colors_exist(self) -> None:
        """Primary color scale exists."""
        assert Colors.PRIMARY_50 is not None
        assert Colors.PRIMARY_500 is not None
        assert Colors.PRIMARY_900 is not None

    def test_semantic_colors_exist(self) -> None:
        """Semantic colors exist."""
        assert Colors.SUCCESS_500 is not None
        assert Colors.WARNING_500 is not None
        assert Colors.ERROR_500 is not None
        assert Colors.INFO_500 is not None
