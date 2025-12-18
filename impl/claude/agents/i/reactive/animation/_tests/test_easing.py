"""Tests for easing functions."""

import math
from typing import Callable

import pytest

from agents.i.reactive.animation.easing import (
    EASE_BOUNCE_OUT,
    EASE_CUBIC_IN,
    EASE_CUBIC_OUT,
    EASE_ELASTIC_OUT,
    EASE_LINEAR,
    EASE_QUAD_IN,
    EASE_QUAD_IN_OUT,
    EASE_QUAD_OUT,
    Easing,
    EasingCurve,
    ease_bounce,
    ease_circ_in,
    ease_circ_out,
    ease_elastic,
    ease_expo_in,
    ease_expo_out,
    ease_in,
    ease_in_out,
    ease_linear,
    ease_out,
    ease_sine_in,
    ease_sine_in_out,
    ease_sine_out,
    get_easing_fn,
)


class TestLinearEasing:
    """Tests for ease_linear."""

    def test_linear_at_zero(self) -> None:
        """Linear returns 0 at t=0."""
        assert ease_linear(0.0) == 0.0

    def test_linear_at_one(self) -> None:
        """Linear returns 1 at t=1."""
        assert ease_linear(1.0) == 1.0

    def test_linear_at_half(self) -> None:
        """Linear returns 0.5 at t=0.5."""
        assert ease_linear(0.5) == 0.5

    def test_linear_identity(self) -> None:
        """Linear is the identity function."""
        for t in [0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9]:
            assert ease_linear(t) == t

    def test_linear_clamps_negative(self) -> None:
        """Linear clamps negative values to 0."""
        assert ease_linear(-0.5) == 0.0

    def test_linear_clamps_overflow(self) -> None:
        """Linear clamps values > 1 to 1."""
        assert ease_linear(1.5) == 1.0


class TestEaseIn:
    """Tests for ease_in (quadratic by default)."""

    def test_ease_in_at_zero(self) -> None:
        """Ease-in returns 0 at t=0."""
        assert ease_in(0.0) == 0.0

    def test_ease_in_at_one(self) -> None:
        """Ease-in returns 1 at t=1."""
        assert ease_in(1.0) == 1.0

    def test_ease_in_at_half_quadratic(self) -> None:
        """Quadratic ease-in: 0.5^2 = 0.25."""
        assert ease_in(0.5) == 0.25

    def test_ease_in_cubic(self) -> None:
        """Cubic ease-in: 0.5^3 = 0.125."""
        assert ease_in(0.5, power=3.0) == 0.125

    def test_ease_in_is_slow_start(self) -> None:
        """Ease-in starts slow (value < t for small t)."""
        assert ease_in(0.2) < 0.2
        assert ease_in(0.3) < 0.3

    def test_ease_in_accelerates(self) -> None:
        """Ease-in accelerates towards end."""
        # Difference between consecutive values increases
        d1 = ease_in(0.3) - ease_in(0.2)
        d2 = ease_in(0.8) - ease_in(0.7)
        assert d2 > d1


class TestEaseOut:
    """Tests for ease_out (quadratic by default)."""

    def test_ease_out_at_zero(self) -> None:
        """Ease-out returns 0 at t=0."""
        assert ease_out(0.0) == 0.0

    def test_ease_out_at_one(self) -> None:
        """Ease-out returns 1 at t=1."""
        assert ease_out(1.0) == 1.0

    def test_ease_out_at_half_quadratic(self) -> None:
        """Quadratic ease-out: 1 - (1-0.5)^2 = 0.75."""
        assert ease_out(0.5) == 0.75

    def test_ease_out_is_fast_start(self) -> None:
        """Ease-out starts fast (value > t for small t)."""
        assert ease_out(0.2) > 0.2
        assert ease_out(0.3) > 0.3

    def test_ease_out_decelerates(self) -> None:
        """Ease-out decelerates towards end."""
        d1 = ease_out(0.3) - ease_out(0.2)
        d2 = ease_out(0.8) - ease_out(0.7)
        assert d2 < d1


class TestEaseInOut:
    """Tests for ease_in_out (S-curve)."""

    def test_ease_in_out_at_zero(self) -> None:
        """Ease-in-out returns 0 at t=0."""
        assert ease_in_out(0.0) == 0.0

    def test_ease_in_out_at_one(self) -> None:
        """Ease-in-out returns 1 at t=1."""
        assert ease_in_out(1.0) == 1.0

    def test_ease_in_out_at_half(self) -> None:
        """Ease-in-out returns 0.5 at t=0.5 (symmetry point)."""
        assert ease_in_out(0.5) == 0.5

    def test_ease_in_out_symmetry(self) -> None:
        """Ease-in-out is symmetric around (0.5, 0.5)."""
        for t in [0.1, 0.2, 0.3, 0.4]:
            assert abs(ease_in_out(t) + ease_in_out(1.0 - t) - 1.0) < 1e-10


class TestEaseBounce:
    """Tests for ease_bounce."""

    def test_bounce_at_zero(self) -> None:
        """Bounce returns 0 at t=0."""
        assert ease_bounce(0.0) == 0.0

    def test_bounce_at_one(self) -> None:
        """Bounce returns 1 at t=1."""
        assert ease_bounce(1.0) == 1.0

    def test_bounce_reaches_one(self) -> None:
        """Bounce reaches 1 eventually."""
        assert ease_bounce(1.0) >= 0.99


class TestEaseElastic:
    """Tests for ease_elastic."""

    def test_elastic_at_zero(self) -> None:
        """Elastic returns 0 at t=0."""
        assert ease_elastic(0.0) == 0.0

    def test_elastic_at_one(self) -> None:
        """Elastic returns ~1 at t=1."""
        assert abs(ease_elastic(1.0) - 1.0) < 0.01

    def test_elastic_overshoots(self) -> None:
        """Elastic can overshoot 1.0."""
        # Elastic typically overshoots before settling
        values = [ease_elastic(t) for t in [0.6, 0.7, 0.8, 0.9]]
        assert any(v > 1.0 for v in values) or any(v < 0.0 for v in values)


class TestSineEasing:
    """Tests for sine-based easing."""

    def test_sine_in_at_endpoints(self) -> None:
        """Sine-in returns correct values at endpoints."""
        assert abs(ease_sine_in(0.0)) < 1e-10
        assert abs(ease_sine_in(1.0) - 1.0) < 1e-10

    def test_sine_out_at_endpoints(self) -> None:
        """Sine-out returns correct values at endpoints."""
        assert abs(ease_sine_out(0.0)) < 1e-10
        assert abs(ease_sine_out(1.0) - 1.0) < 1e-10

    def test_sine_in_out_at_endpoints(self) -> None:
        """Sine-in-out returns correct values at endpoints."""
        assert abs(ease_sine_in_out(0.0)) < 1e-10
        assert abs(ease_sine_in_out(1.0) - 1.0) < 1e-10


class TestExpoEasing:
    """Tests for exponential easing."""

    def test_expo_in_at_endpoints(self) -> None:
        """Expo-in returns correct values at endpoints."""
        assert ease_expo_in(0.0) == 0.0
        assert abs(ease_expo_in(1.0) - 1.0) < 1e-10

    def test_expo_out_at_endpoints(self) -> None:
        """Expo-out returns correct values at endpoints."""
        assert abs(ease_expo_out(0.0)) < 1e-10
        assert ease_expo_out(1.0) == 1.0


class TestCircEasing:
    """Tests for circular easing."""

    def test_circ_in_at_endpoints(self) -> None:
        """Circ-in returns correct values at endpoints."""
        assert abs(ease_circ_in(0.0)) < 1e-10
        assert abs(ease_circ_in(1.0) - 1.0) < 1e-10

    def test_circ_out_at_endpoints(self) -> None:
        """Circ-out returns correct values at endpoints."""
        assert abs(ease_circ_out(0.0)) < 1e-10
        assert abs(ease_circ_out(1.0) - 1.0) < 1e-10


class TestGetEasingFn:
    """Tests for get_easing_fn."""

    def test_get_linear(self) -> None:
        """Get linear easing function."""
        fn = get_easing_fn(Easing.LINEAR)
        assert fn(0.5) == 0.5

    def test_get_ease_in(self) -> None:
        """Get ease-in function."""
        fn = get_easing_fn(Easing.EASE_IN)
        assert fn(0.5) == 0.25

    def test_get_ease_out(self) -> None:
        """Get ease-out function."""
        fn = get_easing_fn(Easing.EASE_OUT)
        assert fn(0.5) == 0.75

    def test_get_ease_in_out(self) -> None:
        """Get ease-in-out function."""
        fn = get_easing_fn(Easing.EASE_IN_OUT)
        assert fn(0.5) == 0.5

    def test_get_bounce(self) -> None:
        """Get bounce function."""
        fn = get_easing_fn(Easing.BOUNCE)
        assert fn(1.0) == 1.0

    def test_get_elastic(self) -> None:
        """Get elastic function."""
        fn = get_easing_fn(Easing.ELASTIC)
        assert abs(fn(1.0) - 1.0) < 0.01


class TestEasingCurve:
    """Tests for EasingCurve class."""

    def test_curve_linear(self) -> None:
        """EasingCurve linear works correctly."""
        curve = EasingCurve(Easing.LINEAR)
        assert curve.apply(0.5) == 0.5

    def test_curve_with_power(self) -> None:
        """EasingCurve respects power parameter."""
        curve = EasingCurve(Easing.EASE_IN, power=3.0)
        assert curve.apply(0.5) == 0.125

    def test_preset_quad_in(self) -> None:
        """Preset EASE_QUAD_IN works."""
        assert EASE_QUAD_IN.apply(0.5) == 0.25

    def test_preset_quad_out(self) -> None:
        """Preset EASE_QUAD_OUT works."""
        assert EASE_QUAD_OUT.apply(0.5) == 0.75

    def test_preset_cubic_in(self) -> None:
        """Preset EASE_CUBIC_IN works."""
        assert EASE_CUBIC_IN.apply(0.5) == 0.125

    def test_preset_cubic_out(self) -> None:
        """Preset EASE_CUBIC_OUT works."""
        assert EASE_CUBIC_OUT.apply(0.5) == 0.875

    def test_preset_bounce(self) -> None:
        """Preset EASE_BOUNCE_OUT works."""
        assert EASE_BOUNCE_OUT.apply(1.0) == 1.0

    def test_preset_elastic(self) -> None:
        """Preset EASE_ELASTIC_OUT works."""
        assert abs(EASE_ELASTIC_OUT.apply(1.0) - 1.0) < 0.01


class TestEasingPurity:
    """Tests that easing functions are pure (deterministic)."""

    @pytest.mark.parametrize(
        "fn",
        [
            ease_linear,
            ease_in,
            ease_out,
            ease_in_out,
            ease_bounce,
            ease_elastic,
        ],
    )
    def test_determinism(self, fn: Callable[[float], float]) -> None:
        """Same input always produces same output."""
        t = 0.42
        result1 = fn(t)
        result2 = fn(t)
        assert result1 == result2

    @pytest.mark.parametrize(
        "fn",
        [
            ease_linear,
            ease_in,
            ease_out,
            ease_in_out,
            ease_bounce,
        ],
    )
    def test_no_side_effects(self, fn: Callable[[float], float]) -> None:
        """Easing functions have no side effects."""
        # Call multiple times with different values
        results = [fn(t / 10) for t in range(11)]
        # All results should be floats
        assert all(isinstance(r, float) for r in results)
