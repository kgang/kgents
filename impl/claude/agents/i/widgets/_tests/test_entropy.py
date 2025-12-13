"""
Tests for EntropyVisualizer module.

Verifies that entropy levels map deterministically to visual distortion parameters.
"""

import pytest
from agents.i.widgets.entropy import (
    EntropyParams,
    entropy_to_border_style,
    entropy_to_params,
)


class TestEntropyToParams:
    """Test entropy_to_params function."""

    def test_zero_entropy(self) -> None:
        """Zero entropy produces no distortion."""
        params = entropy_to_params(0.0)

        assert params.edge_opacity == 1.0
        assert params.dither_rate == 0.0
        assert params.jitter_amplitude == 0
        assert params.glitch_intensity == 0.0

    def test_low_entropy(self) -> None:
        """Low entropy (0.3) produces minimal distortion."""
        params = entropy_to_params(0.3)

        # Edge opacity decreases linearly
        assert params.edge_opacity == pytest.approx(0.85)
        # Dither rate increases linearly
        assert params.dither_rate == pytest.approx(0.12)
        # Jitter amplitude scales linearly (int)
        assert params.jitter_amplitude == 0  # int(0.3 * 3) = 0
        # No glitch below 0.7 threshold
        assert params.glitch_intensity == 0.0

    def test_medium_entropy(self) -> None:
        """Medium entropy (0.5) produces moderate distortion."""
        params = entropy_to_params(0.5)

        assert params.edge_opacity == pytest.approx(0.75)
        assert params.dither_rate == pytest.approx(0.2)
        assert params.jitter_amplitude == 1  # int(0.5 * 3) = 1
        # Still below glitch threshold
        assert params.glitch_intensity == 0.0

    def test_high_entropy_threshold(self) -> None:
        """Entropy at 0.7 threshold begins glitch."""
        params = entropy_to_params(0.7)

        assert params.edge_opacity == pytest.approx(0.65)
        assert params.dither_rate == pytest.approx(0.28)
        assert params.jitter_amplitude == 2  # int(0.7 * 3) = 2
        # Just at threshold - glitch starts
        assert params.glitch_intensity == pytest.approx(0.0, abs=0.01)

    def test_high_entropy(self) -> None:
        """High entropy (0.85) produces heavy distortion."""
        params = entropy_to_params(0.85)

        assert params.edge_opacity == pytest.approx(0.575)
        assert params.dither_rate == pytest.approx(0.34)
        assert params.jitter_amplitude == 2  # int(0.85 * 3) = 2
        # Glitch intensity: (0.85 - 0.7) / 0.3 * 0.6 = 0.3
        assert params.glitch_intensity == pytest.approx(0.3)

    def test_max_entropy(self) -> None:
        """Maximum entropy (1.0) produces maximum distortion."""
        params = entropy_to_params(1.0)

        assert params.edge_opacity == pytest.approx(0.5)
        assert params.dither_rate == pytest.approx(0.4)
        assert params.jitter_amplitude == 3  # int(1.0 * 3) = 3
        # Maximum glitch: (1.0 - 0.7) / 0.3 * 0.6 = 0.6
        assert params.glitch_intensity == pytest.approx(0.6)

    def test_entropy_clamping_low(self) -> None:
        """Negative entropy is clamped to 0.0."""
        params = entropy_to_params(-0.5)

        assert params.edge_opacity == 1.0
        assert params.dither_rate == 0.0
        assert params.jitter_amplitude == 0
        assert params.glitch_intensity == 0.0

    def test_entropy_clamping_high(self) -> None:
        """Entropy above 1.0 is clamped to 1.0."""
        params = entropy_to_params(1.5)

        # Should be same as 1.0
        assert params.edge_opacity == pytest.approx(0.5)
        assert params.dither_rate == pytest.approx(0.4)
        assert params.jitter_amplitude == 3
        assert params.glitch_intensity == pytest.approx(0.6)

    def test_deterministic_mapping(self) -> None:
        """Same entropy always produces same parameters."""
        params1 = entropy_to_params(0.42)
        params2 = entropy_to_params(0.42)

        assert params1.edge_opacity == params2.edge_opacity
        assert params1.dither_rate == params2.dither_rate
        assert params1.jitter_amplitude == params2.jitter_amplitude
        assert params1.glitch_intensity == params2.glitch_intensity

    def test_params_are_frozen(self) -> None:
        """EntropyParams is immutable (frozen dataclass)."""
        params = entropy_to_params(0.5)

        with pytest.raises(AttributeError):
            params.edge_opacity = 0.9  # type: ignore


class TestEntropyToBorderStyle:
    """Test entropy_to_border_style function."""

    def test_low_entropy_solid(self) -> None:
        """Low entropy (< 0.3) produces solid borders."""
        assert entropy_to_border_style(0.0) == "solid"
        assert entropy_to_border_style(0.1) == "solid"
        assert entropy_to_border_style(0.29) == "solid"

    def test_medium_entropy_soft(self) -> None:
        """Medium entropy (0.3-0.6) produces soft borders."""
        assert entropy_to_border_style(0.3) == "soft"
        assert entropy_to_border_style(0.45) == "soft"
        assert entropy_to_border_style(0.59) == "soft"

    def test_high_entropy_broken(self) -> None:
        """High entropy (0.6-0.8) produces broken borders."""
        assert entropy_to_border_style(0.6) == "broken"
        assert entropy_to_border_style(0.7) == "broken"
        assert entropy_to_border_style(0.79) == "broken"

    def test_void_entropy_none(self) -> None:
        """Void entropy (≥ 0.8) produces no borders."""
        assert entropy_to_border_style(0.8) == "none"
        assert entropy_to_border_style(0.9) == "none"
        assert entropy_to_border_style(1.0) == "none"


class TestEntropyParams:
    """Test EntropyParams dataclass."""

    def test_creation(self) -> None:
        """Can create EntropyParams directly."""
        params = EntropyParams(
            edge_opacity=0.8,
            dither_rate=0.1,
            jitter_amplitude=1,
            glitch_intensity=0.0,
        )

        assert params.edge_opacity == 0.8
        assert params.dither_rate == 0.1
        assert params.jitter_amplitude == 1
        assert params.glitch_intensity == 0.0

    def test_all_fields_required(self) -> None:
        """All fields are required."""
        with pytest.raises(TypeError):
            EntropyParams()  # type: ignore

    def test_immutable(self) -> None:
        """EntropyParams is immutable."""
        params = EntropyParams(
            edge_opacity=0.5,
            dither_rate=0.2,
            jitter_amplitude=2,
            glitch_intensity=0.3,
        )

        with pytest.raises(AttributeError):
            params.dither_rate = 0.5  # type: ignore
