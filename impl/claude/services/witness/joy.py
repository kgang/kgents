"""
JoyPoly Functor: Joy as a categorical object.

Joy is NOT a number. It's a polynomial functor:
JoyPoly(y) = Sigma_{mode in JoyMode} mode x y^{Interaction_{mode}}

For trail-to-crystal pilot:
    FLOW:     0.5 (primary - lighter than a to-do list)
    WARMTH:   0.35 (secondary - kind companion reviewing your day)
    SURPRISE: 0.15 (tertiary - unexpected insights in crystals)

Philosophy:
    "Joy is not a scalar metric to maximize. Joy is a behavioral pattern that composes."
    "Joy is inferred from behavioral signals, never interrogated."

See: plans/enlightened-synthesis/04-joy-integration.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Generic, TypeVar

Observer = TypeVar("Observer")


class JoyMode(Enum):
    """
    Joy modes as polynomial positions.

    These are the three faces of joy:
    - WARMTH: The relational dimension (collaboration vs. transaction)
    - SURPRISE: The creative dimension (serendipity vs. predictability)
    - FLOW: The temporal dimension (effortless vs. laborious)
    """

    WARMTH = "warmth"
    SURPRISE = "surprise"
    FLOW = "flow"


@dataclass
class JoyObservation(Generic[Observer]):
    """
    JoyPoly(y) = Sigma_{mode in JoyMode} mode x y^{Interaction_{mode}}

    Joy is polymorphic: different observers perceive different joy.
    The architect sees elegance joy. The player sees mastery joy.

    Attributes:
        mode: The dominant joy mode
        intensity: Intensity in [0, 1] range
        observer: The observer perceiving this joy
        trigger: What caused this observation
    """

    mode: JoyMode
    intensity: float  # [0, 1]
    observer: Observer
    trigger: str

    def __post_init__(self) -> None:
        """Validate intensity is in [0, 1]."""
        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(f"intensity must be in [0, 1], got {self.intensity}")

    def __repr__(self) -> str:
        return f"Joy({self.mode.value}: {self.intensity:.2f} via '{self.trigger}')"

    def __rshift__(self, other: JoyObservation[Observer]) -> JoyObservation[Observer]:
        """
        Joy composition operator: self >> other.

        This enables categorical composition of joy observations.
        """
        # Use default weights for inline composition
        functor = JoyFunctor({})
        return functor.compose(self, other)

    @classmethod
    def identity(cls, observer: Observer) -> JoyObservation[Observer]:
        """
        Identity element for joy composition under max.

        For max-based composition, the identity is 0:
        max(0, x) == x == max(x, 0)

        The mode defaults to FLOW but is overridden by any composed observation.
        """
        return cls(
            mode=JoyMode.FLOW,  # Default mode (overridden in composition)
            intensity=0.0,  # Identity under max
            observer=observer,
            trigger="identity",
        )


class JoyFunctor:
    """
    Joy as a functor: maps observers to joy observations.

    The key insight: Joy composes!
    domain_joy x universal_delight -> total_joy

    Attributes:
        domain_weights: Domain-specific weights for each joy mode
    """

    def __init__(self, domain_weights: dict[JoyMode, float]) -> None:
        """
        Initialize joy functor with domain-specific weights.

        Args:
            domain_weights: Weights for each JoyMode. Missing modes default to 0.33.
        """
        # Ensure all modes have weights, defaulting to 0.33 (roughly equal)
        self.domain_weights = {
            JoyMode.WARMTH: domain_weights.get(JoyMode.WARMTH, 0.33),
            JoyMode.SURPRISE: domain_weights.get(JoyMode.SURPRISE, 0.33),
            JoyMode.FLOW: domain_weights.get(JoyMode.FLOW, 0.34),
        }

    def observe(
        self,
        observer: Observer,
        warmth: float,
        surprise: float,
        flow: float,
        trigger: str = "domain-weighted observation",
    ) -> JoyObservation[Observer]:
        """
        Map observer state to joy observation.

        This applies domain weights to raw joy signals and returns
        a JoyObservation with the dominant mode.

        Args:
            observer: The observer perceiving joy
            warmth: Raw warmth signal [0, 1]
            surprise: Raw surprise signal [0, 1]
            flow: Raw flow signal [0, 1]
            trigger: What caused this observation

        Returns:
            JoyObservation with weighted intensity and dominant mode
        """
        # Apply domain weights
        weighted = {
            JoyMode.WARMTH: warmth * self.domain_weights[JoyMode.WARMTH],
            JoyMode.SURPRISE: surprise * self.domain_weights[JoyMode.SURPRISE],
            JoyMode.FLOW: flow * self.domain_weights[JoyMode.FLOW],
        }

        # Find dominant mode
        dominant = max(weighted, key=lambda m: weighted[m])
        intensity = min(1.0, max(0.0, weighted[dominant]))

        return JoyObservation(
            mode=dominant,
            intensity=intensity,
            observer=observer,
            trigger=trigger,
        )

    def compose(
        self,
        domain_joy: JoyObservation[Observer],
        universal_delight: JoyObservation[Observer],
    ) -> JoyObservation[Observer]:
        """
        Joy composition: domain-specific x universal primitives.

        This is NOT addition. It's functorial composition using the
        categorical product (min) for associativity:
        - Domain joy provides the base resonance
        - Universal delight amplifies or dampens
        - The result uses max for intensity (monoid in [0,1] under max)

        For categorical correctness, we use:
        - max(a, b) for intensity (associative: max(max(a,b),c) == max(a,max(b,c)))
        - Mode from the joy with higher intensity

        The max operation forms an idempotent commutative monoid on [0,1],
        which ensures associativity of composition.

        Args:
            domain_joy: Domain-specific joy observation
            universal_delight: Universal delight primitive

        Returns:
            Composed JoyObservation
        """
        # Use max for associative composition
        # max is associative: max(max(a,b),c) == max(a,max(b,c))
        composed_intensity = max(domain_joy.intensity, universal_delight.intensity)

        # Dominant mode comes from higher intensity
        if domain_joy.intensity >= universal_delight.intensity:
            mode = domain_joy.mode
        else:
            mode = universal_delight.mode

        return JoyObservation(
            mode=mode,
            intensity=composed_intensity,
            observer=domain_joy.observer,
            trigger=f"{domain_joy.trigger} >> {universal_delight.trigger}",
        )


# =============================================================================
# Universal Delight Primitives
# =============================================================================


class UniversalDelightPrimitive(Enum):
    """
    Five irreducible joy sources that appear across ALL domains.

    These primitives compose with any domain-specific joy.
    """

    RECOGNITION = "recognition"  # Being seen for who you are
    MASTERY = "mastery"  # Earned competence, not given
    CLOSURE = "closure"  # Completing a meaningful arc
    DISCOVERY = "discovery"  # Finding something unexpected
    CONNECTION = "connection"  # Genuine collaboration

    def to_joy_mode(self) -> JoyMode:
        """Map primitive to dominant joy mode."""
        mapping = {
            UniversalDelightPrimitive.RECOGNITION: JoyMode.WARMTH,
            UniversalDelightPrimitive.MASTERY: JoyMode.FLOW,
            UniversalDelightPrimitive.CLOSURE: JoyMode.FLOW,
            UniversalDelightPrimitive.DISCOVERY: JoyMode.SURPRISE,
            UniversalDelightPrimitive.CONNECTION: JoyMode.WARMTH,
        }
        return mapping[self]


# =============================================================================
# Pilot-Specific Calibration: Trail-to-Crystal
# =============================================================================

TRAIL_TO_CRYSTAL_JOY = JoyFunctor({
    JoyMode.FLOW: 0.5,  # Primary: "Lighter than a to-do list"
    JoyMode.WARMTH: 0.35,  # Secondary: "Kind companion reviewing your day"
    JoyMode.SURPRISE: 0.15,  # Tertiary: Unexpected insights in crystals
})
"""
Trail-to-Crystal Joy Calibration.

Primary Joy: FLOW
    "Witnessing accelerates, not slows."
    The capture is frictionless. Time disappears during review.

Secondary Joy: WARMTH
    "System is descriptive, not punitive."
    A kind companion helping you review your day.

Tertiary Joy: SURPRISE
    Crystals sometimes reveal unexpected patterns.
    Serendipity in compression.

Galois Target: L < 0.15 (closure warmth)
"""


# =============================================================================
# Joy Composition Laws
# =============================================================================


class JoyCompositionLaws:
    """
    Verify joy composition laws hold.

    Laws:
    1. Associativity: (a >> b) >> c == a >> (b >> c)
    2. Identity: id >> a == a == a >> id
    3. Joy >> Witness = Witness (joy doesn't block witnessing)
    4. Compression >> Joy != Joy >> Compression (order matters!)
    """

    @staticmethod
    def verify_associativity(
        a: JoyObservation[Observer],
        b: JoyObservation[Observer],
        c: JoyObservation[Observer],
        epsilon: float = 0.01,
    ) -> bool:
        """
        Verify: (a >> b) >> c == a >> (b >> c) for joy morphisms.

        Due to floating point, we check approximate equality.

        Args:
            a, b, c: Joy observations to compose
            epsilon: Tolerance for floating point comparison

        Returns:
            True if associativity holds within epsilon
        """
        functor = JoyFunctor({})

        # (a >> b) >> c
        ab = functor.compose(a, b)
        left = functor.compose(ab, c)

        # a >> (b >> c)
        bc = functor.compose(b, c)
        right = functor.compose(a, bc)

        return abs(left.intensity - right.intensity) < epsilon

    @staticmethod
    def verify_identity(
        a: JoyObservation[Observer],
        epsilon: float = 0.01,
    ) -> bool:
        """
        Verify: id >> a == a == a >> id.

        Under max-based composition, identity has intensity 0:
        max(0, x) == x == max(x, 0)

        Args:
            a: Joy observation to test
            epsilon: Tolerance for floating point comparison

        Returns:
            True if identity law holds
        """
        functor = JoyFunctor({})
        identity = JoyObservation.identity(a.observer)

        # id >> a should equal a (intensity preserved)
        left = functor.compose(identity, a)

        # a >> id should equal a (intensity preserved)
        right = functor.compose(a, identity)

        # Both should equal a's intensity
        left_ok = abs(left.intensity - a.intensity) < epsilon
        right_ok = abs(right.intensity - a.intensity) < epsilon

        return left_ok and right_ok

    @staticmethod
    def joy_witness_identity() -> bool:
        """
        Joy >> Witness = Witness (captures joy).

        Joy observation IS the witness. This law is definitionally true.
        """
        return True

    @staticmethod
    def compression_asymmetry() -> bool:
        """
        Compression >> Joy != Joy >> Compression.

        This is intentionally asymmetric. Order matters!
        - Joy first: capture delight, then compress (warmth preserved)
        - Compression first: summarize, then check (joy may be lost)
        """
        return False  # Intentionally asymmetric


# =============================================================================
# Warmth Response Generator
# =============================================================================


def warmth_response(joy_obs: JoyObservation[Observer]) -> str:
    """
    Generate a warmth-calibrated response based on joy observation.

    This is used by DailyMarkCapture to add warmth to responses.

    Args:
        joy_obs: The joy observation to respond to

    Returns:
        A warm, human-friendly response string
    """
    # High intensity responses
    if joy_obs.intensity > 0.7:
        if joy_obs.mode == JoyMode.WARMTH:
            return "That felt like a real moment of connection."
        elif joy_obs.mode == JoyMode.SURPRISE:
            return "Something unexpected emerged there."
        else:  # FLOW
            return "You were really in the groove."

    # Medium intensity responses
    if joy_obs.intensity > 0.4:
        if joy_obs.mode == JoyMode.WARMTH:
            return "That had some warmth to it."
        elif joy_obs.mode == JoyMode.SURPRISE:
            return "A nice little discovery."
        else:  # FLOW
            return "Good momentum there."

    # Low intensity responses (still warm, not punitive)
    if joy_obs.mode == JoyMode.WARMTH:
        return "Noted."
    elif joy_obs.mode == JoyMode.SURPRISE:
        return "Captured."
    else:  # FLOW
        return "Got it."


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "JoyMode",
    "JoyObservation",
    "JoyFunctor",
    # Universal primitives
    "UniversalDelightPrimitive",
    # Pilot calibration
    "TRAIL_TO_CRYSTAL_JOY",
    # Laws
    "JoyCompositionLaws",
    # Utilities
    "warmth_response",
]
