"""
Psi-gent TopologicalValidator: The Y-axis of the 4-axis tensor.

Controls Lacanian topology - knot integrity between Real/Symbolic/Imaginary.

Hallucination = Symbolic OK, Real FAIL (map doesn't match territory).
Delegates to H-lacan for RSI analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .types import (
    AxisType,
    AntiPattern,
    AntiPatternDetection,
    Projection,
    StabilityStatus,
    ValidationResult,
)


# =============================================================================
# Lacanian Register Types
# =============================================================================


class Register(Enum):
    """The three Lacanian registers."""

    REAL = "real"  # What actually is (unmediated reality)
    SYMBOLIC = "symbolic"  # What can be said (language, structure)
    IMAGINARY = "imaginary"  # What is perceived (self-image, gestalt)


@dataclass(frozen=True)
class RegisterState:
    """State of a register for an entity."""

    register: Register
    content: str
    integrity: float = 1.0  # 0 = broken, 1 = intact
    notes: str = ""


@dataclass(frozen=True)
class KnotAnalysis:
    """
    Analysis of the Borromean knot between RSI registers.

    In Lacan, the three registers are linked like a Borromean knot:
    if any one is removed, the other two fall apart.
    """

    real: RegisterState
    symbolic: RegisterState
    imaginary: RegisterState

    # Knot properties
    is_intact: bool  # All three properly linked
    slippage: float  # How much the knot has loosened (0 = tight, 1 = loose)
    break_point: Register | None = None  # Which register is breaking (if any)

    @property
    def weakest_register(self) -> Register:
        """Find the weakest register."""
        states = [self.real, self.symbolic, self.imaginary]
        return min(states, key=lambda s: s.integrity).register


# =============================================================================
# Knot Analyzer (Lacanian Pattern)
# =============================================================================


class KnotAnalyzer:
    """
    Analyzes the Borromean knot between Real, Symbolic, and Imaginary.

    This is the H-lacan delegate functionality within Psi-gent.
    """

    def analyze(self, projection: Projection) -> KnotAnalysis:
        """
        Analyze the RSI knot for a metaphor projection.

        Checks:
        - Real: Does the projection match actual problem structure?
        - Symbolic: Is the projection expressible in metaphor language?
        - Imaginary: Does the projection form a coherent gestalt?
        """
        real = self._analyze_real(projection)
        symbolic = self._analyze_symbolic(projection)
        imaginary = self._analyze_imaginary(projection)

        # Calculate slippage
        slippage = self._calculate_slippage(real, symbolic, imaginary)

        # Determine if knot is intact
        is_intact = (
            all(s.integrity > 0.3 for s in [real, symbolic, imaginary])
            and slippage < 0.5
        )

        # Find break point if not intact
        break_point = None
        if not is_intact:
            weakest = min([real, symbolic, imaginary], key=lambda s: s.integrity)
            break_point = weakest.register

        return KnotAnalysis(
            real=real,
            symbolic=symbolic,
            imaginary=imaginary,
            is_intact=is_intact,
            slippage=slippage,
            break_point=break_point,
        )

    def _analyze_real(self, projection: Projection) -> RegisterState:
        """
        Analyze the Real register.

        The Real is what resists symbolization - the actual problem
        structure independent of how we talk about it.
        """
        source = projection.source

        # Real integrity based on:
        # 1. How much of the problem's actual structure is captured
        # 2. Whether constraints are preserved

        # Check constraint preservation
        constraint_preserved = len(source.constraints) == 0 or any(
            c in projection.projected_description for c in source.constraints
        )

        # Check if complexity is honestly represented
        complexity_honest = (
            projection.coverage > 0.3
        )  # At least 30% of problem captured

        integrity = 0.5
        if constraint_preserved:
            integrity += 0.25
        if complexity_honest:
            integrity += 0.25

        return RegisterState(
            register=Register.REAL,
            content=f"Problem structure: {source.domain} @ complexity {source.complexity:.2f}",
            integrity=integrity,
            notes="Real = actual problem structure independent of representation",
        )

    def _analyze_symbolic(self, projection: Projection) -> RegisterState:
        """
        Analyze the Symbolic register.

        The Symbolic is the language/structure used to express the projection.
        """
        metaphor = projection.target

        # Symbolic integrity based on:
        # 1. Are the concept mappings coherent?
        # 2. Do the operations form a complete language?

        # Check mapping coherence
        mapping_coherent = len(projection.mapped_concepts) > 0

        # Check operation coverage
        ops_available = len(projection.applicable_operations) > 0

        integrity = 0.5
        if mapping_coherent:
            integrity += 0.25
        if ops_available:
            integrity += 0.25

        return RegisterState(
            register=Register.SYMBOLIC,
            content=f"Metaphor language: {metaphor.name} with {len(metaphor.operations)} operations",
            integrity=integrity,
            notes="Symbolic = the language structure of the metaphor",
        )

    def _analyze_imaginary(self, projection: Projection) -> RegisterState:
        """
        Analyze the Imaginary register.

        The Imaginary is the coherent gestalt - how the projection
        "looks" as a unified whole.
        """
        # Imaginary integrity based on:
        # 1. Does the projection form a coherent narrative?
        # 2. Is there a clear "image" of the solution path?

        # Check narrative coherence (proxy: confidence)
        coherent = projection.confidence > 0.4

        # Check completeness
        complete = projection.coverage > 0.5

        integrity = 0.5
        if coherent:
            integrity += 0.25
        if complete:
            integrity += 0.25

        return RegisterState(
            register=Register.IMAGINARY,
            content=f"Projection gestalt: confidence {projection.confidence:.2f}",
            integrity=integrity,
            notes="Imaginary = the unified image of the projected problem",
        )

    def _calculate_slippage(
        self, real: RegisterState, symbolic: RegisterState, imaginary: RegisterState
    ) -> float:
        """
        Calculate knot slippage.

        Slippage = how much the three registers are drifting apart.
        High slippage means the metaphor is becoming incoherent.
        """
        # Slippage is variance in integrity across registers
        integrities = [real.integrity, symbolic.integrity, imaginary.integrity]
        mean = sum(integrities) / 3
        variance = sum((i - mean) ** 2 for i in integrities) / 3

        # Also consider if any register is very low
        min_integrity = min(integrities)
        if min_integrity < 0.3:
            return 1.0 - min_integrity  # High slippage

        return variance  # Low variance = tight knot


# =============================================================================
# Topological Validator
# =============================================================================


@dataclass
class TopologicalValidator:
    """
    The Y-axis controller: Lacanian topology validation.

    Ensures the Borromean knot between Real, Symbolic, and Imaginary
    is intact. Hallucination = when Symbolic claims don't match Real.

    Responsibilities:
    1. Analyze RSI registers for projections
    2. Detect map-territory confusion
    3. Validate knot integrity
    4. Warn on hallucination risk
    """

    # Configuration
    slippage_threshold: float = 0.5  # Above this = unstable
    knot_analyzer: KnotAnalyzer = field(default_factory=KnotAnalyzer)

    def validate(self, projection: Projection) -> ValidationResult:
        """
        Validate a projection's topological integrity.

        Returns a ValidationResult for the Y-axis.
        """
        analysis = self.knot_analyzer.analyze(projection)

        if analysis.is_intact and analysis.slippage < 0.3:
            return ValidationResult(
                axis=AxisType.Y_LACANIAN,
                status=StabilityStatus.STABLE,
                score=1.0 - analysis.slippage,
                message="Borromean knot is intact",
                details={
                    "real_integrity": analysis.real.integrity,
                    "symbolic_integrity": analysis.symbolic.integrity,
                    "imaginary_integrity": analysis.imaginary.integrity,
                },
            )
        elif analysis.is_intact:
            return ValidationResult(
                axis=AxisType.Y_LACANIAN,
                status=StabilityStatus.FRAGILE,
                score=1.0 - analysis.slippage,
                message=f"Knot is loosening, weakest: {analysis.weakest_register.value}",
                details={
                    "slippage": analysis.slippage,
                    "weakest_register": analysis.weakest_register.value,
                },
            )
        else:
            return ValidationResult(
                axis=AxisType.Y_LACANIAN,
                status=StabilityStatus.UNSTABLE,
                score=1.0 - analysis.slippage,
                message=f"Knot breaking at {analysis.break_point.value if analysis.break_point else 'unknown'}",
                details={
                    "break_point": analysis.break_point.value
                    if analysis.break_point
                    else None,
                    "real": analysis.real.notes,
                    "symbolic": analysis.symbolic.notes,
                    "imaginary": analysis.imaginary.notes,
                },
            )

    def detect_hallucination_risk(self, projection: Projection) -> float:
        """
        Detect risk of hallucination (Symbolic != Real).

        Returns a risk score from 0.0 (no risk) to 1.0 (certain hallucination).
        """
        analysis = self.knot_analyzer.analyze(projection)

        # Hallucination = Symbolic claims confidence but Real doesn't support
        symbolic_confidence = analysis.symbolic.integrity
        real_support = analysis.real.integrity

        # High symbolic + low real = hallucination
        if symbolic_confidence > 0.7 and real_support < 0.4:
            return 0.8 + (symbolic_confidence - real_support) * 0.2

        # Moderate difference is warning
        if symbolic_confidence > real_support + 0.3:
            return (symbolic_confidence - real_support) * 0.5

        return 0.0

    def detect_map_territory_confusion(
        self, projection: Projection
    ) -> AntiPatternDetection:
        """
        Detect the map-territory confusion anti-pattern.

        Map-territory confusion = believing the metaphor IS reality.
        """
        analysis = self.knot_analyzer.analyze(projection)

        # Confusion indicators:
        # 1. High imaginary (strong belief in projection) +
        # 2. Low real (weak connection to actual problem) +
        # 3. High confidence

        high_imaginary = analysis.imaginary.integrity > 0.7
        low_real = analysis.real.integrity < 0.5
        high_confidence = projection.confidence > 0.7

        detected = high_imaginary and low_real and high_confidence

        return AntiPatternDetection(
            pattern=AntiPattern.MAP_TERRITORY_CONFUSION,
            detected=detected,
            confidence=0.7 if detected else 0.0,
            evidence=(
                f"Imaginary={analysis.imaginary.integrity:.2f}, "
                f"Real={analysis.real.integrity:.2f}"
                if detected
                else ""
            ),
            mitigation="Ground the metaphor with concrete examples from the original problem",
        )

    def analyze_registers(self, projection: Projection) -> dict[str, Any]:
        """
        Get detailed register analysis.

        Useful for debugging and understanding projection topology.
        """
        analysis = self.knot_analyzer.analyze(projection)

        return {
            "real": {
                "content": analysis.real.content,
                "integrity": analysis.real.integrity,
                "notes": analysis.real.notes,
            },
            "symbolic": {
                "content": analysis.symbolic.content,
                "integrity": analysis.symbolic.integrity,
                "notes": analysis.symbolic.notes,
            },
            "imaginary": {
                "content": analysis.imaginary.content,
                "integrity": analysis.imaginary.integrity,
                "notes": analysis.imaginary.notes,
            },
            "knot": {
                "intact": analysis.is_intact,
                "slippage": analysis.slippage,
                "break_point": analysis.break_point.value
                if analysis.break_point
                else None,
            },
            "hallucination_risk": self.detect_hallucination_risk(projection),
        }
