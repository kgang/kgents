"""
Emergence Types: Enums and type definitions for the Cymatics Design System.

The Emergence domain captures generative aesthetics:
- EmergencePhase: IDLE/LOADING/GALLERY/EXPLORING/EXPORTING
- PatternFamily: The 9 cymatics pattern families
- CircadianPhase: dawn/noon/dusk/midnight
- QualiaCoords: Cross-modal aesthetic coordinates

These form the state space for EMERGENCE_POLYNOMIAL.

See: docs/creative/emergence-principles.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, TypeVar

# Type variables for generic operations
P = TypeVar("P", bound="PatternFamily")
C = TypeVar("C", bound="CircadianPhase")


class EmergencePhase(Enum):
    """
    Phase of the emergence experience.

    Maps to UI modes:
    - IDLE: No pattern active, showing overview
    - LOADING: Computing/fetching pattern data
    - GALLERY: Browsing pattern variations (grid view)
    - EXPLORING: Fine-tuning single pattern (detail view)
    - EXPORTING: Saving/sharing pattern configuration
    """

    IDLE = auto()
    LOADING = auto()
    GALLERY = auto()
    EXPLORING = auto()
    EXPORTING = auto()


class PatternFamily(Enum):
    """
    The 9 cymatics pattern families.

    Each family has distinct mathematical basis and aesthetic character:
    - CHLADNI: Standing wave patterns (physics)
    - INTERFERENCE: Wave interference (water-like)
    - MANDALA: Radial symmetry (sacred geometry)
    - FLOW: Organic noise-driven (fluid)
    - REACTION: Turing-like (biological)
    - SPIRAL: Logarithmic spirals (golden ratio)
    - VORONOI: Cellular patterns (crystalline)
    - MOIRE: Overlapping gratings (optical)
    - FRACTAL: Self-similar Julia sets (mathematical)
    """

    CHLADNI = "chladni"
    INTERFERENCE = "interference"
    MANDALA = "mandala"
    FLOW = "flow"
    REACTION = "reaction"
    SPIRAL = "spiral"
    VORONOI = "voronoi"
    MOIRE = "moire"
    FRACTAL = "fractal"


class CircadianPhase(Enum):
    """
    Time-of-day phases that modulate aesthetics.

    From unified-vision.md circadian modulation:
    - DAWN: 6-10, cooler, brightening
    - NOON: 10-16, neutral, active
    - DUSK: 16-20, warming, slowing
    - MIDNIGHT: 20-6, cool, dim, slow
    """

    DAWN = "dawn"
    NOON = "noon"
    DUSK = "dusk"
    MIDNIGHT = "midnight"

    @classmethod
    def from_hour(cls, hour: int) -> CircadianPhase:
        """Map hour (0-23) to circadian phase."""
        if 6 <= hour < 10:
            return cls.DAWN
        if 10 <= hour < 16:
            return cls.NOON
        if 16 <= hour < 20:
            return cls.DUSK
        return cls.MIDNIGHT


# Type alias for phase literals (for TypeScript interop)
CircadianPhaseName = Literal["dawn", "noon", "dusk", "midnight"]


# =============================================================================
# Qualia Space (Cross-Modal Aesthetic Coordinates)
# =============================================================================


@dataclass(frozen=True)
class QualiaCoords:
    """
    Cross-modal aesthetic coordinates.

    From emergence-principles.md Part III: The Qualia Space.
    Each dimension ranges from -1 to +1.

    These coordinates project to multiple modalities:
    - warmth: affects hue (cool → warm)
    - weight: affects saturation, dampening
    - tempo: affects duration, speed
    - texture: affects smoothness, noise
    - brightness: affects luminance, amplitude
    - saturation: affects chroma intensity
    - complexity: affects detail level
    """

    warmth: float = 0.0  # -1 (cool/cyan) to +1 (warm/amber)
    weight: float = 0.0  # -1 (light) to +1 (heavy)
    tempo: float = 0.0  # -1 (slow) to +1 (fast)
    texture: float = 0.0  # -1 (smooth) to +1 (rough)
    brightness: float = 0.0  # -1 (dark) to +1 (bright)
    saturation: float = 0.0  # -1 (muted) to +1 (vivid)
    complexity: float = 0.0  # -1 (simple) to +1 (complex)

    def __post_init__(self) -> None:
        """Validate all coordinates are in [-1, 1]."""
        for field_name in [
            "warmth",
            "weight",
            "tempo",
            "texture",
            "brightness",
            "saturation",
            "complexity",
        ]:
            value = getattr(self, field_name)
            if not -1.0 <= value <= 1.0:
                clamped = max(-1.0, min(1.0, value))
                object.__setattr__(self, field_name, clamped)

    def blend(self, other: QualiaCoords, t: float = 0.5) -> QualiaCoords:
        """Linearly interpolate between two qualia coordinates."""
        t = max(0.0, min(1.0, t))
        return QualiaCoords(
            warmth=self.warmth * (1 - t) + other.warmth * t,
            weight=self.weight * (1 - t) + other.weight * t,
            tempo=self.tempo * (1 - t) + other.tempo * t,
            texture=self.texture * (1 - t) + other.texture * t,
            brightness=self.brightness * (1 - t) + other.brightness * t,
            saturation=self.saturation * (1 - t) + other.saturation * t,
            complexity=self.complexity * (1 - t) + other.complexity * t,
        )

    def apply_modifier(self, modifier: QualiaModifier) -> QualiaCoords:
        """Apply a circadian or contextual modifier."""
        return QualiaCoords(
            warmth=max(-1, min(1, self.warmth + modifier.warmth)),
            weight=max(-1, min(1, self.weight + modifier.weight)),
            tempo=max(-1, min(1, self.tempo + modifier.tempo)),
            texture=max(-1, min(1, self.texture + modifier.texture)),
            brightness=self.brightness * modifier.brightness,
            saturation=max(-1, min(1, self.saturation + modifier.saturation)),
            complexity=max(-1, min(1, self.complexity + modifier.complexity)),
        )


@dataclass(frozen=True)
class QualiaModifier:
    """
    Modifier for qualia coordinates (circadian, contextual).

    Unlike QualiaCoords, modifiers can be additive or multiplicative.
    brightness is multiplicative (0.0-1.0), others are additive (-1 to +1).
    """

    warmth: float = 0.0
    weight: float = 0.0
    tempo: float = 0.0
    texture: float = 0.0
    brightness: float = 1.0  # Multiplicative
    saturation: float = 0.0
    complexity: float = 0.0


# Circadian modifiers from unified-vision.md
CIRCADIAN_MODIFIERS: dict[CircadianPhase, QualiaModifier] = {
    CircadianPhase.DAWN: QualiaModifier(warmth=-0.3, brightness=0.8, tempo=0.3, texture=-0.2),
    CircadianPhase.NOON: QualiaModifier(warmth=0.0, brightness=1.0, tempo=0.5, texture=0.0),
    CircadianPhase.DUSK: QualiaModifier(warmth=0.4, brightness=0.6, tempo=-0.2, texture=0.2),
    CircadianPhase.MIDNIGHT: QualiaModifier(warmth=-0.1, brightness=0.3, tempo=-0.5, texture=-0.3),
}


# =============================================================================
# Pattern Configuration
# =============================================================================


@dataclass(frozen=True)
class PatternConfig:
    """
    Complete configuration for a cymatics pattern.

    Combines pattern family, parameters, and visual settings.
    """

    family: PatternFamily
    param1: float  # Family-specific parameter 1
    param2: float  # Family-specific parameter 2
    hue: float = 0.55  # 0-1 (maps to 0-360 degrees)
    saturation: float = 0.7  # 0-1
    speed: float = 0.5  # Animation speed multiplier
    invert: bool = False

    @property
    def preset_key(self) -> str:
        """Generate a preset key from configuration."""
        return f"{self.family.value}-{self.param1:.0f}-{self.param2:.1f}"


# Qualia mappings for each pattern family (from emergence-principles.md)
FAMILY_QUALIA: dict[PatternFamily, QualiaCoords] = {
    PatternFamily.CHLADNI: QualiaCoords(warmth=-0.3, weight=0.2, tempo=0.3, complexity=0.4),
    PatternFamily.INTERFERENCE: QualiaCoords(warmth=-0.2, weight=-0.1, tempo=0.4, complexity=0.3),
    PatternFamily.MANDALA: QualiaCoords(warmth=0.2, weight=0.5, tempo=-0.3, complexity=0.6),
    PatternFamily.FLOW: QualiaCoords(warmth=0.4, weight=-0.2, tempo=-0.1, complexity=0.2),
    PatternFamily.REACTION: QualiaCoords(warmth=0.1, weight=0.3, tempo=0.5, complexity=0.7),
    PatternFamily.SPIRAL: QualiaCoords(warmth=0.0, weight=0.0, tempo=0.2, complexity=0.4),
    PatternFamily.VORONOI: QualiaCoords(warmth=-0.1, weight=0.4, tempo=-0.2, complexity=0.5),
    PatternFamily.MOIRE: QualiaCoords(warmth=-0.4, weight=-0.3, tempo=0.1, complexity=0.3),
    PatternFamily.FRACTAL: QualiaCoords(warmth=0.0, weight=0.1, tempo=-0.4, complexity=0.9),
}


# =============================================================================
# Emergence State
# =============================================================================


@dataclass(frozen=True)
class EmergenceState:
    """
    Complete state for the emergence experience.

    This is the position in EMERGENCE_POLYNOMIAL state machine.
    """

    phase: EmergencePhase
    selected_family: PatternFamily | None = None
    pattern_config: PatternConfig | None = None
    circadian: CircadianPhase = CircadianPhase.NOON
    qualia: QualiaCoords = QualiaCoords()

    def with_phase(self, phase: EmergencePhase) -> EmergenceState:
        """Return new state with updated phase."""
        return EmergenceState(
            phase=phase,
            selected_family=self.selected_family,
            pattern_config=self.pattern_config,
            circadian=self.circadian,
            qualia=self.qualia,
        )

    def with_family(self, family: PatternFamily) -> EmergenceState:
        """Return new state with updated family."""
        return EmergenceState(
            phase=self.phase,
            selected_family=family,
            pattern_config=self.pattern_config,
            circadian=self.circadian,
            qualia=FAMILY_QUALIA[family],  # Auto-update qualia
        )

    def with_config(self, config: PatternConfig) -> EmergenceState:
        """Return new state with updated pattern configuration."""
        return EmergenceState(
            phase=self.phase,
            selected_family=config.family,
            pattern_config=config,
            circadian=self.circadian,
            qualia=FAMILY_QUALIA[config.family],
        )

    def with_circadian(self, circadian: CircadianPhase) -> EmergenceState:
        """Return new state with updated circadian phase."""
        base_qualia = (
            FAMILY_QUALIA[self.selected_family] if self.selected_family else QualiaCoords()
        )
        modified_qualia = base_qualia.apply_modifier(CIRCADIAN_MODIFIERS[circadian])
        return EmergenceState(
            phase=self.phase,
            selected_family=self.selected_family,
            pattern_config=self.pattern_config,
            circadian=circadian,
            qualia=modified_qualia,
        )


# =============================================================================
# Tile View (for Sheaf)
# =============================================================================


@dataclass(frozen=True)
class TileView:
    """
    Local view of a single pattern tile.

    Used by EmergenceSheaf for gluing local views into global state.
    """

    tile_id: str
    config: PatternConfig
    qualia: QualiaCoords
    circadian: CircadianPhase
    is_selected: bool = False
    is_hovered: bool = False


__all__ = [
    # Core Enums
    "EmergencePhase",
    "PatternFamily",
    "CircadianPhase",
    "CircadianPhaseName",
    # Qualia Space
    "QualiaCoords",
    "QualiaModifier",
    "CIRCADIAN_MODIFIERS",
    # Pattern Configuration
    "PatternConfig",
    "FAMILY_QUALIA",
    # State
    "EmergenceState",
    # Tile View (for Sheaf)
    "TileView",
]
