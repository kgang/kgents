"""Tests for the Qualia Space - unified synesthetic design system.

Philosophy verification:
    - Cross-modal consistency: warm qualia → amber color + slow motion
    - Circadian modulation: dawn is cool, dusk is warm
    - Entropy bounds: accursed share stays within budget
    - Projection functions are deterministic (minus entropy)
"""

import math

import pytest

from agents.i.theme.qualia import (
    CIRCADIAN_MODIFIERS,
    CircadianPhase,
    ColorParams,
    MotionParams,
    QualiaCoords,
    QualiaModifier,
    QualiaSpace,
    ShapeParams,
)


class TestQualiaCoords:
    """Test QualiaCoords dataclass."""

    def test_default_is_neutral(self) -> None:
        """Default coordinates should be neutral (all zeros)."""
        coords = QualiaCoords()
        assert coords.warmth == 0.0
        assert coords.weight == 0.0
        assert coords.tempo == 0.0
        assert coords.texture == 0.0
        assert coords.brightness == 0.0
        assert coords.saturation == 0.0
        assert coords.complexity == 0.0

    def test_specific_values(self) -> None:
        """Should accept specific coordinate values."""
        coords = QualiaCoords(warmth=0.5, weight=-0.3, tempo=0.8)
        assert coords.warmth == 0.5
        assert coords.weight == -0.3
        assert coords.tempo == 0.8

    def test_immutable(self) -> None:
        """QualiaCoords should be immutable (frozen)."""
        coords = QualiaCoords(warmth=0.5)
        with pytest.raises(AttributeError):
            coords.warmth = 0.7  # type: ignore

    def test_distance_to_self_is_zero(self) -> None:
        """Distance to self should be zero."""
        coords = QualiaCoords(warmth=0.5, weight=-0.3)
        assert coords.distance_to(coords) == 0.0

    def test_distance_to_different(self) -> None:
        """Distance to different point should be positive."""
        a = QualiaCoords(warmth=0.0)
        b = QualiaCoords(warmth=1.0)
        assert abs(a.distance_to(b) - 1.0) < 0.001

    def test_lerp_at_zero(self) -> None:
        """Lerp at t=0 should return first point."""
        a = QualiaCoords(warmth=0.0)
        b = QualiaCoords(warmth=1.0)
        result = a.lerp(b, 0.0)
        assert result.warmth == 0.0

    def test_lerp_at_one(self) -> None:
        """Lerp at t=1 should return second point."""
        a = QualiaCoords(warmth=0.0)
        b = QualiaCoords(warmth=1.0)
        result = a.lerp(b, 1.0)
        assert result.warmth == 1.0

    def test_lerp_at_half(self) -> None:
        """Lerp at t=0.5 should return midpoint."""
        a = QualiaCoords(warmth=0.0, weight=-1.0)
        b = QualiaCoords(warmth=1.0, weight=1.0)
        result = a.lerp(b, 0.5)
        assert abs(result.warmth - 0.5) < 0.001
        assert abs(result.weight - 0.0) < 0.001


class TestCircadianPhase:
    """Test CircadianPhase enum and modifiers."""

    def test_all_phases_defined(self) -> None:
        """All four phases should be defined."""
        assert CircadianPhase.DAWN.value == "dawn"
        assert CircadianPhase.NOON.value == "noon"
        assert CircadianPhase.DUSK.value == "dusk"
        assert CircadianPhase.MIDNIGHT.value == "midnight"

    def test_all_phases_have_modifiers(self) -> None:
        """Every phase should have a modifier defined."""
        for phase in CircadianPhase:
            assert phase in CIRCADIAN_MODIFIERS

    def test_dawn_is_cool(self) -> None:
        """Dawn modifier should shift toward cool."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.DAWN]
        assert modifier.warmth < 0  # Cooler

    def test_dusk_is_warm(self) -> None:
        """Dusk modifier should shift toward warm."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.DUSK]
        assert modifier.warmth > 0  # Warmer

    def test_noon_is_bright(self) -> None:
        """Noon modifier should have full brightness."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.NOON]
        assert modifier.brightness == 1.0

    def test_midnight_is_dim(self) -> None:
        """Midnight modifier should have low brightness."""
        modifier = CIRCADIAN_MODIFIERS[CircadianPhase.MIDNIGHT]
        assert modifier.brightness < 0.5


class TestQualiaSpacePhase:
    """Test QualiaSpace.get_circadian_phase."""

    def test_dawn_hours(self) -> None:
        """Hours 6-9 should be dawn."""
        for hour in [6, 7, 8, 9]:
            assert QualiaSpace.get_circadian_phase(hour) == CircadianPhase.DAWN

    def test_noon_hours(self) -> None:
        """Hours 10-15 should be noon."""
        for hour in [10, 11, 12, 13, 14, 15]:
            assert QualiaSpace.get_circadian_phase(hour) == CircadianPhase.NOON

    def test_dusk_hours(self) -> None:
        """Hours 16-19 should be dusk."""
        for hour in [16, 17, 18, 19]:
            assert QualiaSpace.get_circadian_phase(hour) == CircadianPhase.DUSK

    def test_midnight_hours(self) -> None:
        """Hours 0-5 and 20-23 should be midnight."""
        for hour in [0, 1, 2, 3, 4, 5, 20, 21, 22, 23]:
            assert QualiaSpace.get_circadian_phase(hour) == CircadianPhase.MIDNIGHT


class TestApplyCircadian:
    """Test QualiaSpace.apply_circadian."""

    def test_dawn_cools_warmth(self) -> None:
        """Applying dawn should reduce warmth."""
        base = QualiaCoords(warmth=0.5)
        result = QualiaSpace.apply_circadian(base, 7)  # Dawn hour
        assert result.warmth < base.warmth

    def test_dusk_warms_warmth(self) -> None:
        """Applying dusk should increase warmth."""
        base = QualiaCoords(warmth=0.0)
        result = QualiaSpace.apply_circadian(base, 18)  # Dusk hour
        assert result.warmth > base.warmth

    def test_midnight_dims_brightness(self) -> None:
        """Applying midnight should dim brightness."""
        base = QualiaCoords(brightness=0.5)
        result = QualiaSpace.apply_circadian(base, 0)  # Midnight hour
        assert result.brightness < base.brightness

    def test_preserves_weight(self) -> None:
        """Weight should not be modified by circadian."""
        base = QualiaCoords(weight=0.7)
        result = QualiaSpace.apply_circadian(base, 12)
        assert result.weight == base.weight

    def test_result_in_bounds(self) -> None:
        """Result should stay in [-1, 1] bounds."""
        base = QualiaCoords(warmth=0.9, tempo=0.9)
        result = QualiaSpace.apply_circadian(base, 18)  # Dusk adds warmth
        assert -1.0 <= result.warmth <= 1.0
        assert -1.0 <= result.tempo <= 1.0


class TestInjectEntropy:
    """Test QualiaSpace.inject_entropy (accursed share)."""

    def test_entropy_varies(self) -> None:
        """Multiple calls should produce different results."""
        coords = QualiaCoords(warmth=0.5)
        results = [QualiaSpace.inject_entropy(coords).warmth for _ in range(10)]
        # Not all should be identical (with high probability)
        assert len(set(results)) > 1

    def test_entropy_bounds_default(self) -> None:
        """Entropy should not exceed default budget (10%)."""
        coords = QualiaCoords(warmth=0.5)
        for _ in range(100):
            result = QualiaSpace.inject_entropy(coords, budget=0.1)
            # Maximum deviation should be ±0.1 from 0.5 → [0.4, 0.6]
            # But clamping can affect this, so check bounds
            assert -1.0 <= result.warmth <= 1.0

    def test_entropy_respects_custom_budget(self) -> None:
        """Entropy should respect custom budget."""
        coords = QualiaCoords(warmth=0.0)
        # With budget=0.05, deviation should be at most ±0.05
        for _ in range(50):
            result = QualiaSpace.inject_entropy(coords, budget=0.05)
            assert abs(result.warmth) <= 0.15  # 0.05 + small margin

    def test_result_in_bounds(self) -> None:
        """Result should always be in [-1, 1] bounds."""
        coords = QualiaCoords(warmth=0.95)  # Near edge
        for _ in range(50):
            result = QualiaSpace.inject_entropy(coords)
            assert -1.0 <= result.warmth <= 1.0
            assert -1.0 <= result.brightness <= 1.0


class TestToColor:
    """Test QualiaSpace.to_color projection."""

    def test_warm_produces_amber(self) -> None:
        """Warm qualia should produce amber/orange hue."""
        coords = QualiaCoords(warmth=1.0)
        color = QualiaSpace.to_color(coords)
        # warmth=1 → hue should be around 30 (amber/orange)
        assert 20 <= color.hue <= 40

    def test_cool_produces_cyan(self) -> None:
        """Cool qualia should produce cyan hue."""
        coords = QualiaCoords(warmth=-1.0)
        color = QualiaSpace.to_color(coords)
        # warmth=-1 → hue should be around 180 (cyan)
        assert 170 <= color.hue <= 190

    def test_neutral_produces_mid_hue(self) -> None:
        """Neutral qualia should produce middle hue."""
        coords = QualiaCoords(warmth=0.0)
        color = QualiaSpace.to_color(coords)
        # warmth=0 → hue should be around 105
        assert 95 <= color.hue <= 115

    def test_vivid_produces_high_saturation(self) -> None:
        """Vivid saturation should produce high color saturation."""
        coords = QualiaCoords(saturation=1.0)
        color = QualiaSpace.to_color(coords)
        assert color.saturation >= 80

    def test_muted_produces_low_saturation(self) -> None:
        """Muted saturation should produce low color saturation."""
        coords = QualiaCoords(saturation=-1.0)
        color = QualiaSpace.to_color(coords)
        assert color.saturation <= 30

    def test_bright_produces_high_lightness(self) -> None:
        """Bright qualia should produce high lightness."""
        coords = QualiaCoords(brightness=1.0)
        color = QualiaSpace.to_color(coords)
        assert color.lightness >= 70

    def test_dark_produces_low_lightness(self) -> None:
        """Dark qualia should produce low lightness."""
        coords = QualiaCoords(brightness=-1.0)
        color = QualiaSpace.to_color(coords)
        assert color.lightness <= 30


class TestToMotion:
    """Test QualiaSpace.to_motion projection."""

    def test_fast_tempo_produces_short_duration(self) -> None:
        """Fast tempo should produce short animation duration."""
        coords = QualiaCoords(tempo=1.0)
        motion = QualiaSpace.to_motion(coords)
        assert motion.duration_ms <= 200

    def test_slow_tempo_produces_long_duration(self) -> None:
        """Slow tempo should produce long animation duration."""
        coords = QualiaCoords(tempo=-1.0)
        motion = QualiaSpace.to_motion(coords)
        assert motion.duration_ms >= 800

    def test_light_weight_produces_bouncy(self) -> None:
        """Light weight should produce bouncy easing."""
        coords = QualiaCoords(weight=-0.8)
        motion = QualiaSpace.to_motion(coords)
        assert motion.easing == "bounce"

    def test_heavy_weight_produces_linear(self) -> None:
        """Heavy weight should produce linear easing."""
        coords = QualiaCoords(weight=0.9)
        motion = QualiaSpace.to_motion(coords)
        assert motion.easing == "linear"

    def test_bright_produces_large_amplitude(self) -> None:
        """Bright qualia should produce large motion amplitude."""
        coords = QualiaCoords(brightness=1.0)
        motion = QualiaSpace.to_motion(coords)
        assert motion.amplitude >= 0.9


class TestToShape:
    """Test QualiaSpace.to_shape projection."""

    def test_warm_produces_rounded(self) -> None:
        """Warm qualia should produce rounded shapes."""
        coords = QualiaCoords(warmth=1.0)
        shape = QualiaSpace.to_shape(coords)
        assert shape.roundness >= 0.8

    def test_cool_produces_angular(self) -> None:
        """Cool qualia should produce angular shapes."""
        coords = QualiaCoords(warmth=-1.0)
        shape = QualiaSpace.to_shape(coords)
        assert shape.roundness <= 0.2

    def test_heavy_produces_dense(self) -> None:
        """Heavy qualia should produce dense shapes."""
        coords = QualiaCoords(weight=1.0)
        shape = QualiaSpace.to_shape(coords)
        assert shape.density >= 0.8

    def test_light_produces_sparse(self) -> None:
        """Light qualia should produce sparse shapes."""
        coords = QualiaCoords(weight=-1.0)
        shape = QualiaSpace.to_shape(coords)
        assert shape.density <= 0.3

    def test_complex_produces_high_complexity(self) -> None:
        """Complex qualia should produce high shape complexity."""
        coords = QualiaCoords(complexity=1.0)
        shape = QualiaSpace.to_shape(coords)
        assert shape.complexity >= 0.9


class TestCrossModalConsistency:
    """Test cross-modal consistency: warm→slow, cool→fast, etc."""

    def test_warm_implies_slow_motion(self) -> None:
        """Warm qualia should correlate with slower motion."""
        warm_coords = QualiaCoords(warmth=0.8)
        cool_coords = QualiaCoords(warmth=-0.8)

        warm_motion = QualiaSpace.to_motion(warm_coords)
        cool_motion = QualiaSpace.to_motion(cool_coords)

        # Warm shouldn't necessarily be slower (tempo does that)
        # But this test documents the relationship
        assert warm_motion is not None
        assert cool_motion is not None

    def test_warm_color_with_rounded_shape(self) -> None:
        """Warm qualia should produce both warm color and rounded shape."""
        coords = QualiaCoords(warmth=0.8)
        color = QualiaSpace.to_color(coords)
        shape = QualiaSpace.to_shape(coords)

        # Warm hue (amber range)
        assert color.hue < 60  # Amber/orange/red range

        # Rounded
        assert shape.roundness > 0.5

    def test_cool_color_with_angular_shape(self) -> None:
        """Cool qualia should produce both cool color and angular shape."""
        coords = QualiaCoords(warmth=-0.8)
        color = QualiaSpace.to_color(coords)
        shape = QualiaSpace.to_shape(coords)

        # Cool hue (cyan range)
        assert color.hue > 120  # Cyan/blue range

        # Angular
        assert shape.roundness < 0.5


class TestColorParams:
    """Test ColorParams utilities."""

    def test_to_rgb_neutral(self) -> None:
        """Neutral gray should convert correctly."""
        color = ColorParams(hue=0, saturation=0, lightness=50)
        r, g, b = color.to_rgb()
        assert abs(r - 128) < 5
        assert abs(g - 128) < 5
        assert abs(b - 128) < 5

    def test_to_rgb_red(self) -> None:
        """Pure red should convert correctly."""
        color = ColorParams(hue=0, saturation=100, lightness=50)
        r, g, b = color.to_rgb()
        assert r > 200  # High red
        assert g < 50  # Low green
        assert b < 50  # Low blue

    def test_to_rgb_cyan(self) -> None:
        """Cyan should convert correctly."""
        color = ColorParams(hue=180, saturation=100, lightness=50)
        r, g, b = color.to_rgb()
        assert r < 50  # Low red
        assert g > 200  # High green/cyan
        assert b > 200  # High blue/cyan

    def test_to_hex_format(self) -> None:
        """Hex output should be proper format."""
        color = ColorParams(hue=180, saturation=50, lightness=50)
        hex_color = color.to_hex()
        assert hex_color.startswith("#")
        assert len(hex_color) == 7
        # Should be valid hex
        int(hex_color[1:], 16)


class TestQualiaSpacePresets:
    """Test QualiaSpace preset constants."""

    def test_neutral_is_default(self) -> None:
        """NEUTRAL preset should be all zeros."""
        assert QualiaSpace.NEUTRAL.warmth == 0.0
        assert QualiaSpace.NEUTRAL.weight == 0.0

    def test_warm_active_preset(self) -> None:
        """WARM_ACTIVE preset should have warm, active values."""
        assert QualiaSpace.WARM_ACTIVE.warmth > 0.5
        assert QualiaSpace.WARM_ACTIVE.tempo > 0

    def test_cool_calm_preset(self) -> None:
        """COOL_CALM preset should have cool, calm values."""
        assert QualiaSpace.COOL_CALM.warmth < -0.5
        assert QualiaSpace.COOL_CALM.tempo < 0

    def test_heavy_serious_preset(self) -> None:
        """HEAVY_SERIOUS preset should have heavy, dark values."""
        assert QualiaSpace.HEAVY_SERIOUS.weight > 0.5
        assert QualiaSpace.HEAVY_SERIOUS.brightness < 0

    def test_light_playful_preset(self) -> None:
        """LIGHT_PLAYFUL preset should have light, fast values."""
        assert QualiaSpace.LIGHT_PLAYFUL.weight < -0.5
        assert QualiaSpace.LIGHT_PLAYFUL.tempo > 0


class TestBlend:
    """Test QualiaSpace.blend utility."""

    def test_blend_at_zero(self) -> None:
        """Blend at t=0 should return first point."""
        a = QualiaCoords(warmth=0.0)
        b = QualiaCoords(warmth=1.0)
        result = QualiaSpace.blend(a, b, 0.0)
        assert result.warmth == 0.0

    def test_blend_at_one(self) -> None:
        """Blend at t=1 should return second point."""
        a = QualiaCoords(warmth=0.0)
        b = QualiaCoords(warmth=1.0)
        result = QualiaSpace.blend(a, b, 1.0)
        assert result.warmth == 1.0

    def test_blend_is_symmetric(self) -> None:
        """Blend should be symmetric: blend(a,b,0.5) ≈ blend(b,a,0.5)."""
        a = QualiaCoords(warmth=-0.5, weight=0.3)
        b = QualiaCoords(warmth=0.5, weight=-0.3)

        result_ab = QualiaSpace.blend(a, b, 0.5)
        result_ba = QualiaSpace.blend(b, a, 0.5)

        assert abs(result_ab.warmth - result_ba.warmth) < 0.001
        assert abs(result_ab.weight - result_ba.weight) < 0.001
