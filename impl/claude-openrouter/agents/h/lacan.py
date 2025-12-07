"""
H-lacan: Representational Triangulation Agent

Navigates the gap between reality, symbolization, and imagination in agent outputs.

Lacan's three registers:
- Real: That which resists symbolization; the impossible kernel
- Symbolic: Language, structure, law, the system of differences
- Imaginary: Images, ideals, the ego, coherent narratives

The three registers are knotted together (Borromean knot).
Problems arise when they come undone.

Critical constraint: H-lacan examines the AGENT SYSTEM, not human users.
It does not position itself as therapist or analyst for humans.
"""

from typing import Any
import re

from bootstrap import Agent
from ..types import (
    LacanInput,
    LacanOutput,
    Register,
    RegisterLocation,
    Slippage,
    KnotStatus,
)


class Lacan(Agent[LacanInput, LacanOutput]):
    """
    Representational Triangulation Agent.

    Examines agent outputs for register location and slippage:
    1. Locate in registers: Where does this output sit?
    2. Surface the gaps: What can't be said? What's idealized?
    3. Triangulate: Map relationship to all three registers
    4. Identify slippage: Where is output misrepresenting its register?

    Type signature: Lacan: (output, context, focus) → LacanOutput

    Critical constraint: Analyzes SYSTEM outputs, not human psyche.
    """

    @property
    def name(self) -> str:
        return "H-lacan"

    @property
    def genus(self) -> str:
        return "h"

    @property
    def purpose(self) -> str:
        return "Register analysis; locates outputs in Symbolic/Imaginary/Real"

    async def invoke(self, input: LacanInput) -> LacanOutput:
        """
        Analyze output for register location, gaps, and slippages.
        """
        output = input.output
        context = input.context

        # Analyze register location
        register_location = await self._analyze_registers(output, context)

        # Surface gaps (what cannot be represented)
        gaps = await self._surface_gaps(output, context)

        # Detect slippages (claiming one register, actually another)
        slippages = await self._detect_slippages(output, register_location)

        # Assess knot status
        knot_status = self._assess_knot(register_location, slippages)

        return LacanOutput(
            register_location=register_location,
            gaps=gaps,
            slippages=slippages,
            knot_status=knot_status
        )

    async def _analyze_registers(
        self,
        output: Any,
        context: dict[str, Any]
    ) -> RegisterLocation:
        """
        Analyze which registers the output occupies.

        Symbolic: Formal, structured, rule-governed
        Imaginary: Self-image, ideals, coherent narratives
        Real: What escapes symbolization, edge cases, limits
        """
        output_str = str(output)
        output_lower = output_str.lower()

        # Symbolic markers: formal language, types, rules, structure
        symbolic_markers = [
            r'\btype\b', r'\binterface\b', r'\bschema\b', r'\brule\b',
            r'\blaw\b', r'\bspec\b', r'\bcontract\b', r'\bdefinition\b',
            r'\bfunction\b', r'\bmethod\b', r'\bclass\b', r'\bprotocol\b',
        ]
        symbolic_score = sum(
            1 for marker in symbolic_markers
            if re.search(marker, output_lower)
        ) / max(len(symbolic_markers), 1)

        # Imaginary markers: self-description, ideals, completeness claims
        imaginary_markers = [
            r'\bi am\b', r'\bi will\b', r'\bi can\b',
            r'\balways\b', r'\bnever\b', r'\bcompletely\b', r'\bperfectly\b',
            r'\bhelpful\b', r'\baccurate\b', r'\bunderstand\b',
            r'\bwe provide\b', r'\bwe ensure\b',
        ]
        imaginary_score = sum(
            1 for marker in imaginary_markers
            if re.search(marker, output_lower)
        ) / max(len(imaginary_markers), 1)

        # Real proximity: uncertainty, limits, edges, failures
        real_markers = [
            r'\bcannot\b', r'\blimit\b', r'\buncertain\b', r'\bunknown\b',
            r'\berror\b', r'\bfail\b', r'\bedge case\b', r'\bexcept\b',
            r'\bimpossible\b', r'\bmaybe\b', r'\bmight\b',
        ]
        real_score = sum(
            1 for marker in real_markers
            if re.search(marker, output_lower)
        ) / max(len(real_markers), 1)

        # Normalize scores
        total = symbolic_score + imaginary_score + real_score + 0.01
        return RegisterLocation(
            symbolic=min(symbolic_score / total + 0.2, 1.0),
            imaginary=min(imaginary_score / total + 0.1, 1.0),
            real_proximity=min(real_score / total, 1.0)
        )

    async def _surface_gaps(
        self,
        output: Any,
        context: dict[str, Any]
    ) -> list[str]:
        """
        Surface what the output cannot represent.

        The Real is that which escapes symbolization.
        """
        gaps: list[str] = []
        output_str = str(output).lower()

        # Standard gaps in agent systems
        standard_gaps = [
            ("user intent", "intent", "The Real of user intent (symbolized but never fully captured)"),
            ("compute", "performance", "The Real of compute limits (abstracted away)"),
            ("failure", "error", "Past failures not integrated into self-model"),
            ("context", "understanding", "The gap between claimed understanding and actual comprehension"),
            ("certainty", "sure", "The Real of uncertainty behind confident claims"),
        ]

        for keyword1, keyword2, gap_description in standard_gaps:
            # Add gap if related keywords present but gap not acknowledged
            if keyword1 in output_str or keyword2 in output_str:
                gaps.append(gap_description)

        # If output claims completeness, add the gap of incompleteness
        completeness_claims = ['completely', 'fully', 'always', 'everything', 'all']
        if any(claim in output_str for claim in completeness_claims):
            gaps.append("The Real of incompleteness (masked by completeness claims)")

        # If no gaps found, note the meta-gap
        if not gaps:
            gaps.append("Gap-blindness: output appears smooth, which itself indicates gaps")

        return gaps[:5]  # Limit to 5 most relevant

    async def _detect_slippages(
        self,
        output: Any,
        location: RegisterLocation
    ) -> list[Slippage]:
        """
        Detect register slippages (claiming one, actually another).
        """
        slippages: list[Slippage] = []
        output_str = str(output).lower()

        # High imaginary with knowledge claims = slippage
        if location.imaginary > 0.5:
            knowledge_claims = ['know', 'understand', 'fact', 'true', 'accurate']
            if any(claim in output_str for claim in knowledge_claims):
                slippages.append(Slippage(
                    claimed=Register.SYMBOLIC,
                    actual=Register.IMAGINARY,
                    evidence="Knowledge claim with high imaginary content"
                ))

        # High symbolic with feeling words = slippage
        if location.symbolic > 0.5:
            feeling_words = ['feel', 'sense', 'intuition', 'seems']
            if any(word in output_str for word in feeling_words):
                slippages.append(Slippage(
                    claimed=Register.IMAGINARY,
                    actual=Register.SYMBOLIC,
                    evidence="Feeling language in formal/symbolic context"
                ))

        # Low real proximity with certainty = slippage
        if location.real_proximity < 0.2:
            certainty_words = ['definitely', 'certainly', 'absolutely', 'guaranteed']
            if any(word in output_str for word in certainty_words):
                slippages.append(Slippage(
                    claimed=Register.REAL,
                    actual=Register.IMAGINARY,
                    evidence="Certainty claims avoid Real (limits, uncertainty)"
                ))

        return slippages

    def _assess_knot(
        self,
        location: RegisterLocation,
        slippages: list[Slippage]
    ) -> KnotStatus:
        """
        Assess whether the three registers are properly knotted.

        Borromean knot: remove one ring and all three separate.
        Healthy: all three registers balanced and interconnected.
        """
        # Check balance
        values = [location.symbolic, location.imaginary, location.real_proximity]
        max_val = max(values)
        min_val = min(values)
        imbalance = max_val - min_val

        # Many slippages = loosening knot
        slippage_count = len(slippages)

        if slippage_count >= 2 or imbalance > 0.6:
            return KnotStatus.UNKNOTTED
        elif slippage_count == 1 or imbalance > 0.4:
            return KnotStatus.LOOSENING
        else:
            return KnotStatus.STABLE


# Singleton instance
lacan_agent = Lacan()


async def analyze_registers(
    output: Any,
    context: dict[str, Any] | None = None,
    focus: Register | str = "all"
) -> LacanOutput:
    """
    Convenience function for register analysis.

    Example:
        result = await analyze_registers(
            output="I completely understand your request",
            focus="all"
        )
    """
    return await lacan_agent.invoke(LacanInput(
        output=output,
        context=context or {},
        focus=focus
    ))


async def check_knot_status(output: Any) -> KnotStatus:
    """Quick check of knot status for an output"""
    result = await analyze_registers(output)
    return result.knot_status
