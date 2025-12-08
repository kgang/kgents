"""
H-lacan: Representational Triangulation Agent

Navigates the gap between reality, symbolization, and imagination.

Lacan's three registers:
- Real: That which resists symbolization; the impossible kernel
- Symbolic: Language, structure, law, the system of differences
- Imaginary: Images, ideals, the ego, coherent narratives

Problems arise when the registers come unknotted.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

from bootstrap.types import Agent


class Register(Enum):
    REAL = "real"
    SYMBOLIC = "symbolic"
    IMAGINARY = "imaginary"


class KnotStatus(Enum):
    STABLE = "stable"
    LOOSENING = "loosening"
    UNKNOTTED = "unknotted"


@dataclass
class RegisterLocation:
    """Where an output sits in the three registers."""
    symbolic: float  # 0-1 how much in Symbolic
    imaginary: float  # 0-1 how much in Imaginary
    real_proximity: float  # 0-1 how close to the Real

    def __post_init__(self) -> None:
        """Validate register values are in [0, 1]."""
        for field_name in ['symbolic', 'imaginary', 'real_proximity']:
            value = getattr(self, field_name)
            if not (0 <= value <= 1):
                raise ValueError(f"{field_name} must be in [0, 1], got {value}")


@dataclass
class Slippage:
    """Register slippage - claiming to be in one register while actually in another."""
    claimed: Register
    actual: Register
    evidence: str


@dataclass
class LacanInput:
    """Input for register analysis."""
    output: Any
    context: Optional[dict[str, Any]] = None
    focus: Optional[Register] = None  # Focus on specific register


@dataclass
class LacanOutput:
    """Result of register analysis."""
    register_location: RegisterLocation
    gaps: list[str]  # What cannot be represented
    slippages: list[Slippage]
    knot_status: KnotStatus
    objet_petit_a: Optional[str] = None  # What the system is organized around lacking


@dataclass
class LacanError:
    """Error in register analysis - making the Real explicit."""
    error_type: str
    message: str
    input_snapshot: str


# Type alias for validated output
LacanResult = Union[LacanOutput, LacanError]


# Markers for each register
SYMBOLIC_MARKERS = [
    "defined", "specified", "typed", "interface", "contract",
    "rule", "law", "structure", "formal", "protocol",
    "must", "shall", "requires", "returns", "implements",
]

IMAGINARY_MARKERS = [
    "helpful", "friendly", "intelligent", "perfect", "always",
    "completely", "understand", "best", "ideal", "seamless",
    "I am", "we are", "our goal", "we provide",
]

REAL_MARKERS = [
    "cannot", "impossible", "limit", "edge case", "failure",
    "error", "exception", "undefined", "unknown", "crash",
    "timeout", "overflow", "corrupt", "lost",
]


class LacanAgent(Agent[LacanInput, LacanResult]):
    """
    Register triangulation agent.

    Examines outputs for:
    1. Register location (Symbolic/Imaginary/Real proximity)
    2. Gaps (what cannot be represented)
    3. Slippages (miscategorizations)
    4. Knot status (are the registers properly knotted?)
    
    Returns LacanResult (union of LacanOutput | LacanError).
    Failures become data rather than exceptions.
    """

    @property
    def name(self) -> str:
        return "H-lacan"

    async def invoke(self, input: LacanInput) -> LacanResult:
        """Analyze output for register position. Failures return LacanError."""
        try:
            if input.output is None:
                return LacanError(
                    error_type="validation",
                    message="Cannot analyze None output",
                    input_snapshot="None"
                )

            output_str = str(input.output).lower()

            if not output_str.strip():
                return LacanError(
                    error_type="validation",
                    message="Cannot analyze empty output",
                    input_snapshot=""
                )

            location = self._locate_in_registers(output_str)
            gaps = self._identify_gaps(output_str, input.context)
            slippages = self._detect_slippages(output_str, location)
            knot_status = self._assess_knot(location, slippages)
            objet_a = self._identify_objet_a(output_str, gaps)

            return LacanOutput(
                register_location=location,
                gaps=gaps,
                slippages=slippages,
                knot_status=knot_status,
                objet_petit_a=objet_a,
            )

        except ValueError as e:
            return LacanError(
                error_type="value_error",
                message=str(e),
                input_snapshot=str(input.output)[:100]
            )
        except Exception as e:
            # The Real intrudes - something we didn't symbolize
            return LacanError(
                error_type="real_intrusion",
                message=f"Unexpected: {type(e).__name__}: {str(e)}",
                input_snapshot=str(input.output)[:100]
            )

    def _locate_in_registers(self, output: str) -> RegisterLocation:
        """Locate the output in the three registers."""
        words = output.split()

        symbolic_count = sum(1 for marker in SYMBOLIC_MARKERS if marker in output)
        imaginary_count = sum(1 for marker in IMAGINARY_MARKERS if marker in output)
        real_count = sum(1 for marker in REAL_MARKERS if marker in output)

        total = max(symbolic_count + imaginary_count + real_count, 1)

        # Normalize to 0-1 range
        symbolic = min(1.0, symbolic_count / max(total * 0.5, 1))
        imaginary = min(1.0, imaginary_count / max(total * 0.5, 1))
        real_proximity = min(1.0, real_count / max(total * 0.3, 1))

        return RegisterLocation(
            symbolic=symbolic,
            imaginary=imaginary,
            real_proximity=real_proximity,
        )

    def _identify_gaps(self, output: str, context: Optional[dict[str, Any]]) -> list[str]:
        """Identify what cannot be represented."""
        gaps = []

        # Standard gaps in agent systems
        if "understand" in output or "comprehend" in output:
            gaps.append("The Real of user intent (symbolized but never fully captured)")

        if "always" in output or "never" in output:
            gaps.append("Exceptions to absolute claims")

        if "accurate" in output or "correct" in output:
            gaps.append("Contested facts and underdetermined truth")

        if "we" in output or "our" in output:
            gaps.append("The Real of system as collection vs unified entity")

        if "helpful" in output:
            gaps.append("Cases where help conflicts with other values")

        if not gaps:
            gaps.append("The Real of compute limits and resource constraints")
            gaps.append("The gap between representation and reality")

        return gaps

    def _detect_slippages(
        self,
        output: str,
        location: RegisterLocation,
    ) -> list[Slippage]:
        """Detect register slippages."""
        slippages = []

        # High imaginary with claims of factuality
        if location.imaginary > 0.5:
            if any(word in output for word in ["know", "fact", "true", "accurate"]):
                slippages.append(Slippage(
                    claimed=Register.SYMBOLIC,
                    actual=Register.IMAGINARY,
                    evidence="Knowledge claims with high imaginary content",
                ))

        # Low real proximity with completeness claims
        if location.real_proximity < 0.2:
            if any(word in output for word in ["complete", "full", "entire", "all"]):
                slippages.append(Slippage(
                    claimed=Register.SYMBOLIC,
                    actual=Register.IMAGINARY,
                    evidence="Completeness claims that avoid touching the Real (limits, edges)",
                ))

        # Aspirational as factual
        if "we provide" in output or "we are" in output:
            if location.imaginary > location.symbolic:
                slippages.append(Slippage(
                    claimed=Register.SYMBOLIC,
                    actual=Register.IMAGINARY,
                    evidence="Self-description as fact when actually aspirational",
                ))

        return slippages

    def _assess_knot(
        self,
        location: RegisterLocation,
        slippages: list[Slippage],
    ) -> KnotStatus:
        """Assess whether the three registers are properly knotted."""
        # Many slippages = loosening knot
        if len(slippages) >= 2:
            return KnotStatus.LOOSENING

        # High imaginary with low symbolic = drift
        if location.imaginary > 0.7 and location.symbolic < 0.3:
            return KnotStatus.LOOSENING

        # Extreme real proximity without symbolic structure = unknotted
        if location.real_proximity > 0.8 and location.symbolic < 0.2:
            return KnotStatus.UNKNOTTED

        return KnotStatus.STABLE

    def _identify_objet_a(self, output: str, gaps: list[str]) -> Optional[str]:
        """Identify what the system is organized around lacking."""
        # Common objet a in agent systems
        if "understand" in output or "user" in output:
            return "Full user understanding (always deferred)"

        if "complete" in output or "perfect" in output:
            return "System completeness (impossible)"

        if "helpful" in output or "assist" in output:
            return "Perfect helpfulness (asymptotically approached)"

        if gaps:
            return f"Resolution of: {gaps[0]}"

        return None


class QuickRegister(Agent[str, str]):
    """
    Quick register check - given a string, return dominant register.

    Lightweight version for inline use.
    """

    @property
    def name(self) -> str:
        return "QuickRegister"

    async def invoke(self, text: str) -> str:
        """Return the dominant register for a text."""
        text_lower = text.lower()

        symbolic = sum(1 for m in SYMBOLIC_MARKERS if m in text_lower)
        imaginary = sum(1 for m in IMAGINARY_MARKERS if m in text_lower)
        real = sum(1 for m in REAL_MARKERS if m in text_lower)

        if real > max(symbolic, imaginary):
            return "real"
        if imaginary > symbolic:
            return "imaginary"
        return "symbolic"


# Convenience functions

def lacan() -> LacanAgent:
    """Create a register triangulation agent."""
    return LacanAgent()


def quick_register() -> QuickRegister:
    """Create a quick register check agent."""
    return QuickRegister()
