"""Tests for pure entropy algebra."""

from __future__ import annotations

import pytest

from agents.i.reactive.entropy import (
    DENSITY_RUNES,
    PHASE_GLYPHS,
    SPARK_CHARS,
    distortion_to_css,
    entropy_to_distortion,
    entropy_to_rune,
    entropy_to_spark,
    phase_to_glyph,
)


class TestEntropyToDistortion:
    """Tests for entropy_to_distortion pure function."""

    def test_pure_same_inputs_same_output(self) -> None:
        """CRITICAL: Same inputs always produce same output."""
        # Call multiple times with same args
        result1 = entropy_to_distortion(0.5, 42, 1000.0)
        result2 = entropy_to_distortion(0.5, 42, 1000.0)
        result3 = entropy_to_distortion(0.5, 42, 1000.0)

        assert result1 == result2 == result3

    def test_pure_different_seeds_different_output(self) -> None:
        """Different seeds produce different output."""
        result1 = entropy_to_distortion(0.5, 42, 1000.0)
        result2 = entropy_to_distortion(0.5, 43, 1000.0)

        assert result1 != result2

    def test_pure_different_time_different_output(self) -> None:
        """Different time produces different output."""
        result1 = entropy_to_distortion(0.5, 42, 1000.0)
        result2 = entropy_to_distortion(0.5, 42, 2000.0)

        assert result1 != result2

    def test_entropy_bounds_zero(self) -> None:
        """Entropy at 0 produces minimal distortion."""
        result = entropy_to_distortion(0.0, 42, 0.0)

        # intensity = 0^2 = 0, so most distortion values should be 0 or near 0
        assert result.blur == pytest.approx(0.0, abs=0.001)
        assert result.skew == pytest.approx(0.0, abs=0.001)
        # pulse still has base of 1.0
        assert result.pulse == pytest.approx(1.0, abs=0.01)

    def test_entropy_bounds_one(self) -> None:
        """Entropy at 1.0 produces maximum distortion."""
        result = entropy_to_distortion(1.0, 42, 0.0)

        # intensity = 1^2 = 1, so distortion is high
        # blur = 1 * 2 * (1 + wave*0.3) -> around 2
        assert result.blur > 1.0
        # skew = 1 * 8 * wave2 -> varies by time/seed
        assert abs(result.skew) <= 8.0

    def test_entropy_bounds_negative_clamped(self) -> None:
        """Negative entropy is clamped to 0."""
        result = entropy_to_distortion(-0.5, 42, 0.0)
        result_zero = entropy_to_distortion(0.0, 42, 0.0)

        assert result == result_zero

    def test_entropy_bounds_above_one_clamped(self) -> None:
        """Entropy above 1.0 is clamped to 1.0."""
        result = entropy_to_distortion(1.5, 42, 0.0)
        result_one = entropy_to_distortion(1.0, 42, 0.0)

        assert result == result_one

    def test_high_entropy_more_distortion(self) -> None:
        """Higher entropy produces more distortion (non-linear)."""
        low = entropy_to_distortion(0.2, 42, 1000.0)
        high = entropy_to_distortion(0.8, 42, 1000.0)

        # Since intensity = e^2, high entropy should have much more
        # 0.2^2 = 0.04, 0.8^2 = 0.64 -> 16x difference
        assert abs(high.blur) > abs(low.blur)

    def test_time_affects_oscillation(self) -> None:
        """Time parameter affects wave-based oscillation."""
        t1 = entropy_to_distortion(0.5, 42, 0.0)
        t2 = entropy_to_distortion(0.5, 42, 3141.59)  # About pi * 1000

        # Different time phases should produce different wave values
        assert t1.blur != pytest.approx(t2.blur, abs=0.01)


class TestEntropyToRune:
    """Tests for entropy_to_rune mapping."""

    def test_zero_entropy_empty_space(self) -> None:
        """Zero entropy maps to space (empty)."""
        assert entropy_to_rune(0.0) == DENSITY_RUNES[0]

    def test_max_entropy_full_block(self) -> None:
        """Maximum entropy maps to full block."""
        assert entropy_to_rune(1.0) == DENSITY_RUNES[-1]

    def test_midpoint_entropy(self) -> None:
        """Midpoint entropy maps to middle character."""
        mid_idx = len(DENSITY_RUNES) // 2
        result = entropy_to_rune(0.5)
        # Should be near middle
        actual_idx = DENSITY_RUNES.index(result)
        assert abs(actual_idx - mid_idx) <= 1

    def test_entropy_clamped(self) -> None:
        """Out-of-bounds entropy is clamped."""
        assert entropy_to_rune(-0.5) == DENSITY_RUNES[0]
        assert entropy_to_rune(1.5) == DENSITY_RUNES[-1]


class TestEntropyToSpark:
    """Tests for entropy_to_spark sparkline mapping."""

    def test_zero_entropy_lowest_bar(self) -> None:
        """Zero entropy maps to lowest sparkline bar."""
        assert entropy_to_spark(0.0) == SPARK_CHARS[0]

    def test_max_entropy_highest_bar(self) -> None:
        """Maximum entropy maps to highest sparkline bar."""
        assert entropy_to_spark(1.0) == SPARK_CHARS[-1]

    def test_progressive_bars(self) -> None:
        """Increasing entropy produces increasing bar heights."""
        sparks = [entropy_to_spark(e / 10) for e in range(11)]
        indices = [SPARK_CHARS.index(s) for s in sparks]

        # Should be non-decreasing
        for i in range(len(indices) - 1):
            assert indices[i] <= indices[i + 1]


class TestPhaseToGlyph:
    """Tests for phase_to_glyph mapping."""

    def test_known_phases(self) -> None:
        """Known phases map to expected glyphs."""
        assert phase_to_glyph("idle") == "○"
        assert phase_to_glyph("active") == "◉"
        assert phase_to_glyph("waiting") == "◐"
        assert phase_to_glyph("error") == "◈"
        assert phase_to_glyph("yielding") == "◇"

    def test_unknown_phase_default(self) -> None:
        """Unknown phase returns default glyph."""
        assert phase_to_glyph("unknown") == "·"
        assert phase_to_glyph("") == "·"


class TestDistortionToCSS:
    """Tests for distortion_to_css conversion."""

    def test_css_contains_filter(self) -> None:
        """CSS output contains filter property."""
        distortion = entropy_to_distortion(0.5, 42, 0.0)
        css = distortion_to_css(distortion)

        assert "filter:" in css
        assert "blur(" in css

    def test_css_contains_transform(self) -> None:
        """CSS output contains transform property."""
        distortion = entropy_to_distortion(0.5, 42, 0.0)
        css = distortion_to_css(distortion)

        assert "transform:" in css
        assert "skewX(" in css
        assert "scale(" in css

    def test_css_is_valid_format(self) -> None:
        """CSS output is properly formatted."""
        distortion = entropy_to_distortion(0.5, 42, 0.0)
        css = distortion_to_css(distortion)

        # Should contain semicolon-separated properties
        parts = css.split("; ")
        assert len(parts) >= 2

        # Each part should be property: value
        for part in parts:
            assert ":" in part
