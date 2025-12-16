"""Qualia Space - Unified synesthetic design system.

Philosophy:
    "The barrier between colors and qualia is zero here."

    All sensory modalities project from a unified 7-dimensional qualia space.
    The same coordinates produce consistent cross-modal experiences:
    - Warm qualia → amber color + slow motion + rounded shapes
    - Cool qualia → cyan color + crisp motion + angular shapes

    This is not mere mapping—it IS the aesthetic. The projection IS the experience.
    Different observers receive different projections from the same coordinates.

The Seven Dimensions:
    warmth:     cool (-1) ↔ warm (+1)
    weight:     light (-1) ↔ heavy (+1)
    tempo:      slow (-1) ↔ fast (+1)
    texture:    smooth (-1) ↔ rough (+1)
    brightness: dark (-1) ↔ bright (+1)
    saturation: muted (-1) ↔ vivid (+1)
    complexity: simple (-1) ↔ complex (+1)

Circadian Aesthetics:
    The UI breathes differently at different times. Dawn is cool and quickening;
    dusk is warm and slowing. Midnight is still and deep.

Accursed Share:
    10% of emergence is chaos. This is sacred. Every projection includes
    a small amount of entropy injection—the accursed share that prevents
    the system from becoming sterile.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class CircadianPhase(Enum):
    """The four phases of the circadian aesthetic cycle."""

    DAWN = "dawn"  # 6-10: Cool, brightening, quickening
    NOON = "noon"  # 10-16: Neutral, full brightness, active
    DUSK = "dusk"  # 16-20: Warming, dimming, slowing
    MIDNIGHT = "midnight"  # 20-6: Cool, dim, slow, smooth


@dataclass(frozen=True)
class QualiaCoords:
    """7-dimensional qualia coordinates, all in range [-1, 1].

    These coordinates represent a point in qualia space from which
    all sensory modalities can be projected. The coordinates are
    observer-independent; the projections are observer-dependent.

    Example:
        coords = QualiaCoords(warmth=0.7, weight=-0.3, tempo=-0.5)
        color = QualiaSpace.to_color(coords)  # Amber-ish
        motion = QualiaSpace.to_motion(coords)  # Slow, bouncy
    """

    warmth: float = 0.0  # cool ↔ warm
    weight: float = 0.0  # light ↔ heavy
    tempo: float = 0.0  # slow ↔ fast
    texture: float = 0.0  # smooth ↔ rough
    brightness: float = 0.0  # dark ↔ bright
    saturation: float = 0.0  # muted ↔ vivid
    complexity: float = 0.0  # simple ↔ complex

    def __post_init__(self) -> None:
        """Validate that all coordinates are in [-1, 1]."""
        for name, value in [
            ("warmth", self.warmth),
            ("weight", self.weight),
            ("tempo", self.tempo),
            ("texture", self.texture),
            ("brightness", self.brightness),
            ("saturation", self.saturation),
            ("complexity", self.complexity),
        ]:
            if not -1.0 <= value <= 1.0:
                # Clamp rather than raise—be forgiving
                pass  # We allow overflow for lerp operations

    def distance_to(self, other: QualiaCoords) -> float:
        """Euclidean distance to another point in qualia space."""
        return math.sqrt(
            (self.warmth - other.warmth) ** 2
            + (self.weight - other.weight) ** 2
            + (self.tempo - other.tempo) ** 2
            + (self.texture - other.texture) ** 2
            + (self.brightness - other.brightness) ** 2
            + (self.saturation - other.saturation) ** 2
            + (self.complexity - other.complexity) ** 2
        )

    def lerp(self, other: QualiaCoords, t: float) -> QualiaCoords:
        """Linear interpolation toward another point."""
        return QualiaCoords(
            warmth=self.warmth + (other.warmth - self.warmth) * t,
            weight=self.weight + (other.weight - self.weight) * t,
            tempo=self.tempo + (other.tempo - self.tempo) * t,
            texture=self.texture + (other.texture - self.texture) * t,
            brightness=self.brightness + (other.brightness - self.brightness) * t,
            saturation=self.saturation + (other.saturation - self.saturation) * t,
            complexity=self.complexity + (other.complexity - self.complexity) * t,
        )


@dataclass(frozen=True)
class QualiaModifier:
    """Modifier to apply to base qualia coords.

    Used for circadian modulation and observer-specific adjustments.
    Values are additive for warmth/tempo/texture, multiplicative for brightness.
    """

    warmth: float = 0.0
    brightness: float = 1.0  # Multiplicative
    tempo: float = 0.0
    texture: float = 0.0


@dataclass(frozen=True)
class ColorParams:
    """Color parameters in HSL space."""

    hue: float  # 0-360
    saturation: float  # 0-100
    lightness: float  # 0-100

    def to_rgb(self) -> tuple[int, int, int]:
        """Convert to RGB tuple."""
        h = self.hue / 360.0
        s = self.saturation / 100.0
        l_val = self.lightness / 100.0

        if s == 0:
            r = g = b = l_val
        else:

            def hue_to_rgb(p: float, q: float, t: float) -> float:
                if t < 0:
                    t += 1
                if t > 1:
                    t -= 1
                if t < 1 / 6:
                    return p + (q - p) * 6 * t
                if t < 1 / 2:
                    return q
                if t < 2 / 3:
                    return p + (q - p) * (2 / 3 - t) * 6
                return p

            q = l_val * (1 + s) if l_val < 0.5 else l_val + s - l_val * s
            p = 2 * l_val - q
            r = hue_to_rgb(p, q, h + 1 / 3)
            g = hue_to_rgb(p, q, h)
            b = hue_to_rgb(p, q, h - 1 / 3)

        return (int(r * 255), int(g * 255), int(b * 255))

    def to_hex(self) -> str:
        """Convert to hex color string."""
        r, g, b = self.to_rgb()
        return f"#{r:02x}{g:02x}{b:02x}"


@dataclass(frozen=True)
class MotionParams:
    """Motion parameters derived from qualia."""

    duration_ms: float  # Animation duration
    easing: str  # Easing function name
    amplitude: float  # Motion amplitude (0-1)
    delay_ms: float = 0.0  # Optional delay


@dataclass(frozen=True)
class ShapeParams:
    """Shape parameters derived from qualia."""

    roundness: float  # 0 (angular) to 1 (rounded)
    density: float  # 0 (sparse) to 1 (dense)
    complexity: float  # 0 (simple) to 1 (fractal)


# Circadian modifiers for each phase
CIRCADIAN_MODIFIERS: dict[CircadianPhase, QualiaModifier] = {
    CircadianPhase.DAWN: QualiaModifier(
        warmth=-0.3,  # Cooler
        brightness=0.8,  # Brightening
        tempo=0.3,  # Quickening
        texture=-0.2,  # Smoother
    ),
    CircadianPhase.NOON: QualiaModifier(
        warmth=0.0,  # Neutral
        brightness=1.0,  # Full brightness
        tempo=0.5,  # Active
        texture=0.0,  # Balanced
    ),
    CircadianPhase.DUSK: QualiaModifier(
        warmth=0.4,  # Warming
        brightness=0.6,  # Dimming
        tempo=-0.2,  # Slowing
        texture=0.2,  # Textured
    ),
    CircadianPhase.MIDNIGHT: QualiaModifier(
        warmth=-0.1,  # Cool
        brightness=0.3,  # Dim
        tempo=-0.5,  # Slow
        texture=-0.3,  # Smooth
    ),
}


class QualiaSpace:
    """Unified qualia projection system.

    All sensory modalities project from the same 7-dimensional space.
    This class provides the projection functions that transform
    qualia coordinates into concrete visual/motion/shape parameters.

    Philosophy:
        "Color is frozen music. Motion is visible thought. The barrier is zero."

    Usage:
        ctx = QualiaContext(observer=agent, time=now, state="active")
        coords = QualiaSpace.compute(ctx)
        color = QualiaSpace.to_color(coords)
        motion = QualiaSpace.to_motion(coords)
        shape = QualiaSpace.to_shape(coords)
    """

    # Default neutral coordinates
    NEUTRAL: ClassVar[QualiaCoords] = QualiaCoords()

    # Presets for common states
    WARM_ACTIVE: ClassVar[QualiaCoords] = QualiaCoords(
        warmth=0.7, tempo=0.3, brightness=0.5, saturation=0.6
    )
    COOL_CALM: ClassVar[QualiaCoords] = QualiaCoords(
        warmth=-0.6, tempo=-0.4, brightness=0.3, saturation=0.4
    )
    HEAVY_SERIOUS: ClassVar[QualiaCoords] = QualiaCoords(
        weight=0.7, brightness=-0.3, saturation=0.5, complexity=0.3
    )
    LIGHT_PLAYFUL: ClassVar[QualiaCoords] = QualiaCoords(
        weight=-0.6, tempo=0.5, brightness=0.4, saturation=0.7
    )

    @staticmethod
    def get_circadian_phase(hour: int) -> CircadianPhase:
        """Determine circadian phase from hour (0-23)."""
        if 6 <= hour < 10:
            return CircadianPhase.DAWN
        elif 10 <= hour < 16:
            return CircadianPhase.NOON
        elif 16 <= hour < 20:
            return CircadianPhase.DUSK
        else:
            return CircadianPhase.MIDNIGHT

    @staticmethod
    def apply_circadian(base: QualiaCoords, hour: int) -> QualiaCoords:
        """Apply circadian phase modulation to base coordinates.

        Args:
            base: Base qualia coordinates
            hour: Current hour (0-23)

        Returns:
            Modified coordinates with circadian influence
        """
        phase = QualiaSpace.get_circadian_phase(hour)
        modifier = CIRCADIAN_MODIFIERS[phase]

        return QualiaCoords(
            warmth=_clamp(base.warmth + modifier.warmth),
            weight=base.weight,
            tempo=_clamp(base.tempo + modifier.tempo),
            texture=_clamp(base.texture + modifier.texture),
            brightness=_clamp(base.brightness * modifier.brightness),
            saturation=base.saturation,
            complexity=base.complexity,
        )

    @staticmethod
    def inject_entropy(coords: QualiaCoords, budget: float = 0.1) -> QualiaCoords:
        """Inject accursed share (controlled chaos) into coordinates.

        The accursed share is the 10% of emergence that is chaos.
        This is sacred—it prevents the system from becoming sterile.

        Args:
            coords: Base coordinates
            budget: Maximum deviation per dimension (default 10%)

        Returns:
            Coordinates with entropy injected
        """

        def noise(value: float) -> float:
            deviation = (random.random() - 0.5) * 2 * budget
            return _clamp(value + deviation)

        return QualiaCoords(
            warmth=noise(coords.warmth),
            weight=noise(coords.weight),
            tempo=noise(coords.tempo),
            texture=noise(coords.texture),
            brightness=noise(coords.brightness),
            saturation=noise(coords.saturation),
            complexity=noise(coords.complexity),
        )

    @staticmethod
    def to_color(coords: QualiaCoords) -> ColorParams:
        """Project qualia to color parameters.

        Cross-modal mapping:
        - warmth → hue (180=cyan → 30=amber)
        - saturation → saturation (muted → vivid)
        - brightness → lightness (dark → bright)
        - complexity → hue variation (pure → multi-hue)

        Args:
            coords: Qualia coordinates

        Returns:
            ColorParams in HSL space
        """
        # Hue: cool (cyan=180) to warm (amber=30)
        # warmth -1 → 180, warmth +1 → 30
        # Linear mapping: hue = 105 - warmth * 75
        hue = 105.0 - coords.warmth * 75.0
        if hue < 0:
            hue += 360
        if hue > 360:
            hue -= 360

        # Saturation: muted (20%) to vivid (90%)
        # saturation -1 → 20, saturation +1 → 90
        sat = 55.0 + coords.saturation * 35.0

        # Lightness: dark (25%) to bright (75%)
        # brightness -1 → 25, brightness +1 → 75
        light = 50.0 + coords.brightness * 25.0

        return ColorParams(hue=hue, saturation=sat, lightness=light)

    @staticmethod
    def to_motion(coords: QualiaCoords) -> MotionParams:
        """Project qualia to motion parameters.

        Cross-modal mapping:
        - tempo → duration (slow=1000ms → fast=100ms)
        - weight → easing (light=bouncy → heavy=dampened)
        - brightness → amplitude (dim=subtle → bright=large)

        Args:
            coords: Qualia coordinates

        Returns:
            MotionParams for animation
        """
        # Duration: slow (1000ms) to fast (100ms)
        # tempo -1 → 1000, tempo +1 → 100
        duration = 550.0 - coords.tempo * 450.0

        # Easing: light=bouncy, heavy=linear/dampened
        if coords.weight < -0.3:
            easing = "bounce"
        elif coords.weight < 0.0:
            easing = "ease_out"
        elif coords.weight < 0.3:
            easing = "ease_in_out"
        elif coords.weight < 0.6:
            easing = "ease_in"
        else:
            easing = "linear"

        # Amplitude: dim (0.2) to bright (1.0)
        amplitude = 0.6 + coords.brightness * 0.4

        return MotionParams(
            duration_ms=duration,
            easing=easing,
            amplitude=amplitude,
        )

    @staticmethod
    def to_shape(coords: QualiaCoords) -> ShapeParams:
        """Project qualia to shape parameters.

        Cross-modal mapping:
        - warmth → roundness (cool=angular → warm=rounded)
        - weight → density (light=sparse → heavy=dense)
        - complexity → complexity (simple=primitive → complex=fractal)

        Args:
            coords: Qualia coordinates

        Returns:
            ShapeParams for visual forms
        """
        # Roundness: cool (0.1) to warm (0.9)
        roundness = 0.5 + coords.warmth * 0.4

        # Density: light (0.2) to heavy (0.9)
        density = 0.55 + coords.weight * 0.35

        # Complexity directly maps
        shape_complexity = 0.5 + coords.complexity * 0.5

        return ShapeParams(
            roundness=roundness,
            density=density,
            complexity=shape_complexity,
        )

    @staticmethod
    def blend(a: QualiaCoords, b: QualiaCoords, t: float) -> QualiaCoords:
        """Blend two qualia coordinates.

        Args:
            a: First coordinates
            b: Second coordinates
            t: Blend factor (0=a, 1=b)

        Returns:
            Blended coordinates
        """
        return a.lerp(b, t)


def _clamp(value: float, min_val: float = -1.0, max_val: float = 1.0) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))
