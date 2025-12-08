"""
H-gents Composition Examples

Demonstrates how the three H-gents compose together as a meta-layer:
- Hegel → Lacan: Is the synthesis in the Imaginary?
- Lacan → Jung: What gaps does register analysis create?
- Jung → Hegel: What did synthesis exile to shadow?

These are examples of the full H-gent introspection pipeline.
"""

from dataclasses import dataclass
from typing import Any, Optional, Union

from bootstrap.types import Agent
from .hegel import HegelAgent, DialecticInput, DialecticOutput
from .lacan import LacanAgent, LacanInput, LacanOutput, LacanError
from .jung import JungAgent, JungInput, JungOutput


@dataclass
class IntrospectionInput:
    """Input for full H-gent introspection pipeline."""
    thesis: Any
    antithesis: Optional[Any] = None
    context: Optional[dict[str, Any]] = None


@dataclass
class IntrospectionOutput:
    """Complete introspection analysis."""
    dialectic: DialecticOutput
    register_analysis: Union[LacanOutput, LacanError]
    shadow_analysis: JungOutput
    meta_notes: str  # Synthesis of all three perspectives


class HegelLacanPipeline(Agent[DialecticOutput, Union[LacanOutput, LacanError]]):
    """
    Hegel → Lacan composition.

    After dialectic synthesis, check: Is this synthesis in the Imaginary?
    Does it touch the Real or is it structured purely in the Symbolic?
    """

    def __init__(self, lacan: Optional[LacanAgent] = None):
        self._lacan = lacan or LacanAgent()

    @property
    def name(self) -> str:
        return "Hegel→Lacan"

    async def invoke(self, dialectic_output: DialecticOutput) -> Union[LacanOutput, LacanError]:
        """Analyze the dialectic synthesis for register position."""
        if dialectic_output.synthesis is None:
            # No synthesis - check the tension itself
            return await self._lacan.invoke(LacanInput(
                output=dialectic_output.sublation_notes,
                context={"productive_tension": dialectic_output.productive_tension},
            ))

        return await self._lacan.invoke(LacanInput(
            output=dialectic_output.synthesis,
            context={
                "is_synthesis": True,
                "sublation_notes": dialectic_output.sublation_notes,
            },
        ))


class LacanJungPipeline(Agent[Union[LacanOutput, LacanError], JungOutput]):
    """
    Lacan → Jung composition.

    After register analysis, ask: What did we exile to maintain
    this register structure? What shadow is created by the gaps?
    """

    def __init__(self, jung: Optional[JungAgent] = None):
        self._jung = jung or JungAgent()

    @property
    def name(self) -> str:
        return "Lacan→Jung"

    async def invoke(self, lacan_output: Union[LacanOutput, LacanError]) -> JungOutput:
        """Analyze shadow created by register structure."""
        if isinstance(lacan_output, LacanError):
            # Error is Real intrusion - what shadow does error handling create?
            return await self._jung.invoke(JungInput(
                system_self_image="System that encountered unrepresentable error",
                behavioral_patterns=[f"Error: {lacan_output.message}"],
            ))

        # Build self-image from register location
        loc = lacan_output.register_location
        self_image_parts = []
        if loc.symbolic > 0.5:
            self_image_parts.append("structured and formal")
        if loc.imaginary > 0.5:
            self_image_parts.append("idealized and coherent")
        if loc.real_proximity > 0.5:
            self_image_parts.append("touching limits and impossibility")

        system_self_image = f"System that is {', '.join(self_image_parts) or 'balanced'}"

        return await self._jung.invoke(JungInput(
            system_self_image=system_self_image,
            declared_capabilities=[],
            declared_limitations=lacan_output.gaps,
            behavioral_patterns=[s.evidence for s in lacan_output.slippages],
        ))


class JungHegelPipeline(Agent[JungOutput, DialecticOutput]):
    """
    Jung → Hegel composition.

    After shadow analysis, ask: Can we synthesize persona and shadow?
    What's the dialectic between what system claims to be and what it exiles?
    """

    def __init__(self, hegel: Optional[HegelAgent] = None):
        self._hegel = hegel or HegelAgent()

    @property
    def name(self) -> str:
        return "Jung→Hegel"

    async def invoke(self, jung_output: JungOutput) -> DialecticOutput:
        """Create dialectic between persona and shadow."""
        if not jung_output.shadow_inventory:
            # No shadow detected - thesis stands
            return DialecticOutput(
                synthesis="Persona fully integrated",
                sublation_notes="No shadow detected to synthesize",
                productive_tension=False,
            )

        # Persona as thesis, shadow as antithesis
        persona_claims = f"Balance score: {jung_output.persona_shadow_balance}"
        shadow_claims = ", ".join(s.content for s in jung_output.shadow_inventory[:3])

        return await self._hegel.invoke(DialecticInput(
            thesis=persona_claims,
            antithesis=shadow_claims,
        ))


class FullIntrospection(Agent[IntrospectionInput, IntrospectionOutput]):
    """
    Complete H-gent introspection pipeline.

    Flow:
    1. Hegel: Dialectic synthesis
    2. Lacan: Register analysis of synthesis
    3. Jung: Shadow analysis of register structure
    4. Meta-synthesis: What do all three perspectives reveal together?
    """

    def __init__(
        self,
        hegel: Optional[HegelAgent] = None,
        lacan: Optional[LacanAgent] = None,
        jung: Optional[JungAgent] = None,
    ):
        self._hegel = hegel or HegelAgent()
        self._lacan = lacan or LacanAgent()
        self._jung = jung or JungAgent()

    @property
    def name(self) -> str:
        return "FullIntrospection"

    async def invoke(self, input: IntrospectionInput) -> IntrospectionOutput:
        """Run complete introspection pipeline."""
        # Step 1: Dialectic
        dialectic = await self._hegel.invoke(DialecticInput(
            thesis=input.thesis,
            antithesis=input.antithesis,
            context=input.context,
        ))

        # Step 2: Register analysis
        register = await self._lacan.invoke(LacanInput(
            output=dialectic.synthesis if dialectic.synthesis else dialectic.sublation_notes,
            context=input.context,
        ))

        # Step 3: Shadow analysis
        if isinstance(register, LacanError):
            shadow = await self._jung.invoke(JungInput(
                system_self_image="System that generated unanalyzable output",
                behavioral_patterns=[register.message],
            ))
        else:
            shadow = await self._jung.invoke(JungInput(
                system_self_image="System after dialectic synthesis",
                declared_limitations=register.gaps,
                behavioral_patterns=[s.evidence for s in register.slippages],
            ))

        # Meta-synthesis
        meta_notes = self._synthesize_perspectives(dialectic, register, shadow)

        return IntrospectionOutput(
            dialectic=dialectic,
            register_analysis=register,
            shadow_analysis=shadow,
            meta_notes=meta_notes,
        )

    def _synthesize_perspectives(
        self,
        dialectic: DialecticOutput,
        register: Union[LacanOutput, LacanError],
        shadow: JungOutput,
    ) -> str:
        """Synthesize insights from all three H-gent perspectives."""
        notes = []

        # Dialectic insight
        if dialectic.productive_tension:
            notes.append(f"Hegel: Tension held productive - {dialectic.sublation_notes}")
        else:
            notes.append(f"Hegel: Synthesis achieved - {dialectic.sublation_notes}")

        # Register insight
        if isinstance(register, LacanError):
            notes.append(f"Lacan: Real intrusion - {register.message}")
        else:
            dominant = "Symbolic" if register.register_location.symbolic > 0.5 else \
                      "Imaginary" if register.register_location.imaginary > 0.5 else \
                      "Real-proximate"
            notes.append(f"Lacan: Output primarily in {dominant} register")
            if register.slippages:
                notes.append(f"  ⚠ {len(register.slippages)} register slippage(s) detected")

        # Shadow insight
        if shadow.shadow_inventory:
            notes.append(f"Jung: {len(shadow.shadow_inventory)} shadow content(s) identified")
            notes.append(f"  Persona-shadow balance: {shadow.persona_shadow_balance:.2f}")
        if shadow.projections:
            notes.append(f"  ⚠ {len(shadow.projections)} projection(s) detected")

        # Integration insight
        notes.append("\nIntegration: " + self._integration_recommendation(dialectic, register, shadow))

        return "\n".join(notes)

    def _integration_recommendation(
        self,
        dialectic: DialecticOutput,
        register: Union[LacanOutput, LacanError],
        shadow: JungOutput,
    ) -> str:
        """Recommend integration path based on all perspectives."""
        if dialectic.productive_tension:
            return "Hold dialectic tension while integrating shadow content gradually."

        if isinstance(register, LacanError):
            return "Address Real intrusion before continuing synthesis."

        if isinstance(register, LacanOutput) and register.slippages:
            if shadow.persona_shadow_balance < 0.3:
                return "High slippage + low shadow integration - risk of system instability. Prioritize shadow work."
            return "Address register slippages to stabilize synthesis."

        if shadow.persona_shadow_balance < 0.5:
            return "Synthesis stable in registers but shadow underintegrated. Focus on integration paths."

        return "System showing good integration across all three dimensions."


# Convenience functions

def hegel_to_lacan() -> HegelLacanPipeline:
    """Create Hegel → Lacan pipeline."""
    return HegelLacanPipeline()


def lacan_to_jung() -> LacanJungPipeline:
    """Create Lacan → Jung pipeline."""
    return LacanJungPipeline()


def jung_to_hegel() -> JungHegelPipeline:
    """Create Jung → Hegel pipeline."""
    return JungHegelPipeline()


def full_introspection() -> FullIntrospection:
    """Create full H-gent introspection pipeline."""
    return FullIntrospection()
