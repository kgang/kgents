"""
Easing Functions: Pure mathematical curves for smooth transitions.

Easing functions map [0, 1] -> [0, 1], transforming linear progress
into perceptually smooth motion.

All functions are PURE - no side effects, deterministic output.

Standard curves:
- linear: Constant velocity
- ease_in: Slow start, fast end (acceleration)
- ease_out: Fast start, slow end (deceleration)
- ease_in_out: Slow start and end (S-curve)
- bounce: Bouncy physics simulation
- elastic: Spring-like overshoot

Key insight: Easing is the soul of animation. The same duration
with different easing feels completely different.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable

# Type alias for easing functions
EasingFn = Callable[[float], float]


class Easing(Enum):
    """Named easing functions for convenience."""

    LINEAR = auto()
    EASE_IN = auto()
    EASE_OUT = auto()
    EASE_IN_OUT = auto()
    BOUNCE = auto()
    ELASTIC = auto()


def ease_linear(t: float) -> float:
    """
    Linear easing - constant velocity.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]

    Example:
        >>> ease_linear(0.5)
        0.5
    """
    return _clamp(t)


def ease_in(t: float, power: float = 2.0) -> float:
    """
    Ease-in - slow start, accelerating.

    Uses polynomial curve: t^power

    Args:
        t: Progress [0, 1]
        power: Curve steepness (2.0 = quadratic, 3.0 = cubic)

    Returns:
        Eased value [0, 1]

    Example:
        >>> ease_in(0.5)  # Quadratic
        0.25
        >>> ease_in(0.5, power=3.0)  # Cubic
        0.125
    """
    t = _clamp(t)
    return float(t**power)


def ease_out(t: float, power: float = 2.0) -> float:
    """
    Ease-out - fast start, decelerating.

    Uses inverted polynomial: 1 - (1-t)^power

    Args:
        t: Progress [0, 1]
        power: Curve steepness (2.0 = quadratic, 3.0 = cubic)

    Returns:
        Eased value [0, 1]

    Example:
        >>> ease_out(0.5)  # Quadratic
        0.75
    """
    t = _clamp(t)
    return float(1.0 - (1.0 - t) ** power)


def ease_in_out(t: float, power: float = 2.0) -> float:
    """
    Ease-in-out - slow start and end (S-curve).

    Combines ease_in and ease_out for smooth acceleration/deceleration.

    Args:
        t: Progress [0, 1]
        power: Curve steepness

    Returns:
        Eased value [0, 1]

    Example:
        >>> ease_in_out(0.5)
        0.5
        >>> ease_in_out(0.25)
        0.125
    """
    t = _clamp(t)
    if t < 0.5:
        return float((2 ** (power - 1)) * (t**power))
    else:
        return float(1.0 - ((-2 * t + 2) ** power) / 2)


def ease_bounce(t: float) -> float:
    """
    Bounce easing - physics-inspired bouncing effect.

    Simulates a ball bouncing to rest.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1] (can exceed 1 during bounces)

    Example:
        >>> ease_bounce(1.0)
        1.0
    """
    t = _clamp(t)
    n1 = 7.5625
    d1 = 2.75

    if t < 1 / d1:
        return n1 * t * t
    elif t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    elif t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    else:
        t -= 2.625 / d1
        return n1 * t * t + 0.984375


def ease_elastic(t: float, amplitude: float = 1.0, period: float = 0.3) -> float:
    """
    Elastic easing - spring-like overshoot.

    Creates an elastic effect with configurable amplitude and period.

    Args:
        t: Progress [0, 1]
        amplitude: Overshoot amplitude (1.0 = 100%)
        period: Oscillation period

    Returns:
        Eased value (can exceed [0, 1] during overshoot)

    Example:
        >>> abs(ease_elastic(1.0) - 1.0) < 0.01
        True
    """
    t = _clamp(t)
    if t == 0.0:
        return 0.0
    if t == 1.0:
        return 1.0

    s = (
        period / 4.0
        if amplitude < 1.0
        else period / (2 * math.pi) * math.asin(1.0 / amplitude)
    )

    amplitude = max(amplitude, 1.0)
    return float(
        amplitude * (2.0 ** (-10 * t)) * math.sin((t - s) * (2 * math.pi) / period)
        + 1.0
    )


def ease_sine_in(t: float) -> float:
    """
    Sine ease-in - gentle acceleration using sine curve.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return 1.0 - math.cos((t * math.pi) / 2)


def ease_sine_out(t: float) -> float:
    """
    Sine ease-out - gentle deceleration using sine curve.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return math.sin((t * math.pi) / 2)


def ease_sine_in_out(t: float) -> float:
    """
    Sine ease-in-out - gentle S-curve using sine.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return -(math.cos(math.pi * t) - 1) / 2


def ease_expo_in(t: float) -> float:
    """
    Exponential ease-in - dramatic acceleration.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return 0.0 if t == 0.0 else 2.0 ** (10 * t - 10)


def ease_expo_out(t: float) -> float:
    """
    Exponential ease-out - dramatic deceleration.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return 1.0 if t == 1.0 else 1.0 - 2.0 ** (-10 * t)


def ease_circ_in(t: float) -> float:
    """
    Circular ease-in - follows quarter circle curve.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return 1.0 - math.sqrt(1.0 - t * t)


def ease_circ_out(t: float) -> float:
    """
    Circular ease-out - inverse quarter circle.

    Args:
        t: Progress [0, 1]

    Returns:
        Eased value [0, 1]
    """
    t = _clamp(t)
    return math.sqrt(1.0 - (t - 1.0) ** 2)


def _clamp(t: float) -> float:
    """Clamp t to [0, 1]."""
    return max(0.0, min(1.0, t))


def get_easing_fn(easing: Easing) -> EasingFn:
    """
    Get the easing function for a named easing type.

    Args:
        easing: Named easing type

    Returns:
        The corresponding easing function

    Example:
        >>> fn = get_easing_fn(Easing.EASE_IN)
        >>> fn(0.5)
        0.25
    """
    mapping: dict[Easing, EasingFn] = {
        Easing.LINEAR: ease_linear,
        Easing.EASE_IN: ease_in,
        Easing.EASE_OUT: ease_out,
        Easing.EASE_IN_OUT: ease_in_out,
        Easing.BOUNCE: ease_bounce,
        Easing.ELASTIC: ease_elastic,
    }
    return mapping[easing]


@dataclass(frozen=True)
class EasingCurve:
    """
    Configurable easing curve with presets.

    Allows combining easing type with custom parameters.
    """

    easing: Easing = Easing.EASE_OUT
    power: float = 2.0
    amplitude: float = 1.0
    period: float = 0.3

    def apply(self, t: float) -> float:
        """Apply this curve to a progress value."""
        match self.easing:
            case Easing.LINEAR:
                return ease_linear(t)
            case Easing.EASE_IN:
                return ease_in(t, self.power)
            case Easing.EASE_OUT:
                return ease_out(t, self.power)
            case Easing.EASE_IN_OUT:
                return ease_in_out(t, self.power)
            case Easing.BOUNCE:
                return ease_bounce(t)
            case Easing.ELASTIC:
                return ease_elastic(t, self.amplitude, self.period)


# Pre-configured common curves
EASE_LINEAR = EasingCurve(Easing.LINEAR)
EASE_QUAD_IN = EasingCurve(Easing.EASE_IN, power=2.0)
EASE_QUAD_OUT = EasingCurve(Easing.EASE_OUT, power=2.0)
EASE_QUAD_IN_OUT = EasingCurve(Easing.EASE_IN_OUT, power=2.0)
EASE_CUBIC_IN = EasingCurve(Easing.EASE_IN, power=3.0)
EASE_CUBIC_OUT = EasingCurve(Easing.EASE_OUT, power=3.0)
EASE_CUBIC_IN_OUT = EasingCurve(Easing.EASE_IN_OUT, power=3.0)
EASE_BOUNCE_OUT = EasingCurve(Easing.BOUNCE)
EASE_ELASTIC_OUT = EasingCurve(Easing.ELASTIC)
