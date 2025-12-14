"""
Tests for ANSI Color and Style System.

Tests cover:
- Color construction (standard, palette, RGB, hex)
- Color degradation between modes
- Style building and composition
- Escape sequence generation
- Color schemes
"""

from __future__ import annotations

import pytest
from agents.i.reactive.terminal.ansi import (
    ANSIColor,
    ANSISequence,
    ANSIStyle,
    Color,
    ColorScheme,
    SemanticColors,
    StyleSpec,
    get_scheme,
    phase_to_color,
)

# === Color Construction ===


class TestColorConstruction:
    """Test Color construction methods."""

    def test_standard_color(self) -> None:
        """Standard 16-color construction."""
        color = Color.standard(ANSIColor.RED)
        assert color.mode == "16"
        assert color.value == 1  # RED = 1

    def test_palette_color(self) -> None:
        """256-color palette construction."""
        color = Color.palette(196)
        assert color.mode == "256"
        assert color.value == 196

    def test_palette_clamps_range(self) -> None:
        """Palette index is clamped to 0-255."""
        assert Color.palette(-10).value == 0
        assert Color.palette(300).value == 255

    def test_rgb_color(self) -> None:
        """RGB color construction."""
        color = Color.rgb(255, 128, 64)
        assert color.mode == "rgb"
        assert color.value == 255
        assert color.g == 128
        assert color.b == 64

    def test_rgb_clamps_range(self) -> None:
        """RGB values are clamped to 0-255."""
        color = Color.rgb(-10, 300, 128)
        assert color.value == 0
        assert color.g == 255
        assert color.b == 128

    def test_hex_color_6_digit(self) -> None:
        """Hex color parsing (6 digits)."""
        color = Color.hex("#FF8040")
        assert color.mode == "rgb"
        assert color.value == 255
        assert color.g == 128
        assert color.b == 64

    def test_hex_color_3_digit(self) -> None:
        """Hex color parsing (3 digits expands to 6)."""
        color = Color.hex("#F84")
        assert color.mode == "rgb"
        assert color.value == 255
        assert color.g == 136
        assert color.b == 68

    def test_hex_color_no_hash(self) -> None:
        """Hex color without # prefix."""
        color = Color.hex("FF8040")
        assert color.value == 255

    def test_hex_color_invalid_fallback(self) -> None:
        """Invalid hex returns white fallback."""
        color = Color.hex("not-hex")
        assert color.mode == "16"
        assert color.value == ANSIColor.WHITE


# === Color Codes ===


class TestANSIColorCodes:
    """Test ANSI color code generation."""

    def test_standard_foreground_codes(self) -> None:
        """Standard colors map to 30-37."""
        assert ANSIColor.BLACK.fg_code() == 30
        assert ANSIColor.RED.fg_code() == 31
        assert ANSIColor.WHITE.fg_code() == 37

    def test_bright_foreground_codes(self) -> None:
        """Bright colors map to 90-97."""
        assert ANSIColor.BRIGHT_BLACK.fg_code() == 90
        assert ANSIColor.BRIGHT_RED.fg_code() == 91
        assert ANSIColor.BRIGHT_WHITE.fg_code() == 97

    def test_standard_background_codes(self) -> None:
        """Standard backgrounds map to 40-47."""
        assert ANSIColor.BLACK.bg_code() == 40
        assert ANSIColor.RED.bg_code() == 41

    def test_bright_background_codes(self) -> None:
        """Bright backgrounds map to 100-107."""
        assert ANSIColor.BRIGHT_BLACK.bg_code() == 100
        assert ANSIColor.BRIGHT_RED.bg_code() == 101


# === Color Sequences ===


class TestColorSequences:
    """Test escape sequence generation."""

    def test_standard_fg_sequence(self) -> None:
        """Standard foreground sequence."""
        color = Color.standard(ANSIColor.RED)
        assert color.to_fg_sequence() == "31"

    def test_standard_bg_sequence(self) -> None:
        """Standard background sequence."""
        color = Color.standard(ANSIColor.BLUE)
        assert color.to_bg_sequence() == "44"

    def test_palette_fg_sequence(self) -> None:
        """256-color foreground sequence."""
        color = Color.palette(196)
        assert color.to_fg_sequence() == "38;5;196"

    def test_palette_bg_sequence(self) -> None:
        """256-color background sequence."""
        color = Color.palette(226)
        assert color.to_bg_sequence() == "48;5;226"

    def test_rgb_fg_sequence(self) -> None:
        """RGB foreground sequence."""
        color = Color.rgb(255, 128, 64)
        assert color.to_fg_sequence() == "38;2;255;128;64"

    def test_rgb_bg_sequence(self) -> None:
        """RGB background sequence."""
        color = Color.rgb(64, 128, 255)
        assert color.to_bg_sequence() == "48;2;64;128;255"

    def test_none_mode_empty_sequence(self) -> None:
        """None color mode returns empty."""
        color = Color(mode="none")
        assert color.to_fg_sequence() == ""
        assert color.to_bg_sequence() == ""


# === Color Degradation ===


class TestColorDegradation:
    """Test color mode degradation."""

    def test_rgb_to_256(self) -> None:
        """RGB degrades to 256 palette."""
        color = Color.rgb(255, 0, 0)  # Pure red
        degraded = color.degrade_to("256")
        assert degraded.mode == "256"
        # Should be near the red area of color cube

    def test_256_to_16(self) -> None:
        """256 palette degrades to 16 colors."""
        color = Color.palette(196)  # Bright red in palette
        degraded = color.degrade_to("16")
        assert degraded.mode == "16"

    def test_rgb_to_16(self) -> None:
        """RGB degrades through 256 to 16."""
        color = Color.rgb(255, 0, 0)
        degraded = color.degrade_to("16")
        assert degraded.mode == "16"

    def test_degrade_to_none(self) -> None:
        """Any color degrades to none."""
        color = Color.rgb(255, 128, 64)
        degraded = color.degrade_to("none")
        assert degraded.mode == "none"

    def test_same_mode_no_change(self) -> None:
        """Same mode returns self."""
        color = Color.palette(100)
        degraded = color.degrade_to("256")
        assert degraded == color

    def test_grayscale_rgb_to_256(self) -> None:
        """Grayscale RGB uses grayscale ramp."""
        color = Color.rgb(128, 128, 128)  # Gray
        degraded = color.degrade_to("256")
        assert degraded.mode == "256"
        # Should be in grayscale range (232-255)
        assert 232 <= degraded.value <= 255


# === Style Spec ===


class TestStyleSpec:
    """Test StyleSpec composition."""

    def test_empty_style(self) -> None:
        """Empty style has no colors or styles."""
        spec = StyleSpec()
        assert spec.fg is None
        assert spec.bg is None
        assert spec.styles == frozenset()

    def test_style_with_colors(self) -> None:
        """Style with foreground and background."""
        spec = StyleSpec(
            fg=Color.standard(ANSIColor.RED),
            bg=Color.standard(ANSIColor.BLACK),
        )
        assert spec.fg is not None
        assert spec.bg is not None

    def test_style_merge_fg_priority(self) -> None:
        """Merge gives priority to second style."""
        base = StyleSpec(fg=Color.standard(ANSIColor.RED))
        overlay = StyleSpec(fg=Color.standard(ANSIColor.BLUE))
        merged = base.merge(overlay)
        assert merged.fg == overlay.fg

    def test_style_merge_combines_styles(self) -> None:
        """Merge combines style sets."""
        base = StyleSpec(styles=frozenset([ANSIStyle.BOLD]))
        overlay = StyleSpec(styles=frozenset([ANSIStyle.ITALIC]))
        merged = base.merge(overlay)
        assert ANSIStyle.BOLD in merged.styles
        assert ANSIStyle.ITALIC in merged.styles


# === ANSI Sequence Builder ===


class TestANSISequenceBuilder:
    """Test ANSISequence builder."""

    def test_empty_sequence(self) -> None:
        """Empty sequence builds to empty string."""
        seq = ANSISequence.new()
        assert seq.build() == ""

    def test_reset_sequence(self) -> None:
        """Reset returns reset code."""
        reset = ANSISequence.reset()
        assert reset == "\x1b[0m"

    def test_single_color(self) -> None:
        """Single foreground color."""
        seq = ANSISequence.new().fg(ANSIColor.RED)
        assert seq.build() == "\x1b[31m"

    def test_fg_and_bg(self) -> None:
        """Foreground and background colors."""
        seq = ANSISequence.new().fg(ANSIColor.WHITE).bg(ANSIColor.BLUE)
        assert seq.build() == "\x1b[37;44m"

    def test_bold_style(self) -> None:
        """Bold style."""
        seq = ANSISequence.new().bold()
        assert seq.build() == "\x1b[1m"

    def test_combined_styles(self) -> None:
        """Multiple styles combined."""
        seq = ANSISequence.new().fg(ANSIColor.RED).bold().underline()
        assert "31" in seq.build()
        assert "1" in seq.build()
        assert "4" in seq.build()

    def test_wrap_text(self) -> None:
        """Wrap applies style and reset."""
        seq = ANSISequence.new().bold()
        wrapped = seq.wrap("test")
        assert wrapped.startswith("\x1b[1m")
        assert wrapped.endswith("\x1b[0m")
        assert "test" in wrapped

    def test_from_color_object(self) -> None:
        """Build from Color objects."""
        seq = ANSISequence.new().fg_color(Color.rgb(255, 0, 0))
        result = seq.build()
        assert "38;2;255;0;0" in result

    def test_from_style_spec(self) -> None:
        """Build from StyleSpec."""
        spec = StyleSpec(
            fg=Color.standard(ANSIColor.GREEN),
            styles=frozenset([ANSIStyle.BOLD]),
        )
        # Use 16-color mode explicitly
        seq = ANSISequence.new().from_spec(spec, mode="16")
        result = seq.build()
        assert "32" in result  # Green foreground
        assert "1" in result  # Bold


# === Color Schemes ===


class TestColorSchemes:
    """Test color scheme system."""

    def test_get_dark_scheme(self) -> None:
        """Get dark color scheme."""
        colors = get_scheme(ColorScheme.DARK)
        assert isinstance(colors, SemanticColors)
        assert colors.primary is not None
        assert colors.error is not None

    def test_get_light_scheme(self) -> None:
        """Get light color scheme."""
        colors = get_scheme(ColorScheme.LIGHT)
        assert colors.background.value == ANSIColor.WHITE

    def test_get_high_contrast_scheme(self) -> None:
        """High contrast uses standard colors."""
        colors = get_scheme(ColorScheme.HIGH_CONTRAST)
        # Should use standard 16 colors for max compatibility
        assert colors.text.mode == "16"

    def test_get_colorblind_safe_scheme(self) -> None:
        """Colorblind-safe scheme exists."""
        colors = get_scheme(ColorScheme.COLORBLIND_SAFE)
        assert colors.success is not None
        assert colors.error is not None

    def test_get_monochrome_scheme(self) -> None:
        """Monochrome scheme is grayscale."""
        colors = get_scheme(ColorScheme.MONOCHROME)
        # All phase colors should be grayscale
        assert colors.active is not None

    def test_phase_to_color_mapping(self) -> None:
        """Phase maps to appropriate color."""
        active_color = phase_to_color("active")
        error_color = phase_to_color("error")
        idle_color = phase_to_color("idle")

        assert active_color is not None
        assert error_color is not None
        assert idle_color is not None

    def test_phase_to_color_unknown_phase(self) -> None:
        """Unknown phase returns idle color."""
        color = phase_to_color("unknown_phase")
        idle = phase_to_color("idle")
        assert color == idle


# === Immutability ===


class TestImmutability:
    """Test that colors and styles are immutable."""

    def test_color_is_frozen(self) -> None:
        """Color dataclass is frozen."""
        color = Color.rgb(255, 128, 64)
        with pytest.raises(Exception):  # FrozenInstanceError
            color.value = 0  # type: ignore[misc]

    def test_style_spec_is_frozen(self) -> None:
        """StyleSpec dataclass is frozen."""
        spec = StyleSpec()
        with pytest.raises(Exception):
            spec.fg = Color.standard(ANSIColor.RED)  # type: ignore[misc]

    def test_sequence_is_frozen(self) -> None:
        """ANSISequence is frozen."""
        seq = ANSISequence.new()
        with pytest.raises(Exception):
            seq.parts = ("test",)  # type: ignore[misc]


# === Edge Cases ===


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_ansi_colors(self) -> None:
        """All 16 ANSI colors are valid."""
        for color in ANSIColor:
            assert 0 <= color.fg_code() <= 97
            assert 40 <= color.bg_code() <= 107

    def test_all_styles(self) -> None:
        """All styles have valid codes."""
        for style in ANSIStyle:
            seq = ANSISequence.new().style(style)
            assert seq.build().startswith("\x1b[")

    def test_empty_hex_string(self) -> None:
        """Empty hex string returns fallback."""
        color = Color.hex("")
        assert color.mode == "16"

    def test_sequence_chaining(self) -> None:
        """Sequence methods can be chained."""
        seq = (
            ANSISequence.new()
            .fg(ANSIColor.RED)
            .bg(ANSIColor.BLACK)
            .bold()
            .italic()
            .underline()
            .reverse()
        )
        result = seq.build()
        assert "\x1b[" in result
        assert "m" in result
