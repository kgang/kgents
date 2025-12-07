"""
H-hegel: Dialectic Synthesis Agent

Surfaces contradictions and synthesizes them into higher-order understanding.

The dialectic is not mere compromise—synthesis **sublates** (aufheben):
it preserves, negates, and elevates both thesis and antithesis into
something that transcends both while containing both.

Bootstrap dependency: Contradict, Sublate
"""

from typing import Any

from bootstrap import (
    Agent,
    Contradict,
    Sublate,
    contradict_agent,
    sublate_agent,
    contradict,
    sublate,
    Tension,
    Synthesis,
    HoldTension,
    ContradictInput,
)
from ..types import HegelInput, HegelOutput


class Hegel(Agent[HegelInput, HegelOutput]):
    """
    Dialectic Synthesis Agent.

    Examines agent outputs for dialectical opportunities:
    1. Identify thesis: The dominant position/output
    2. Surface antithesis: The negation, contradiction, or opposing force
    3. Attempt synthesis: Seek the higher unity that contains both
    4. Recurse: The synthesis becomes new thesis for further development

    Type signature: Hegel: (thesis, antithesis?, context) → HegelOutput

    Critical constraint: Must recognize when to HOLD tension rather than
    force premature synthesis. Some contradictions are generative.
    """

    def __init__(
        self,
        contradictor: Contradict | None = None,
        sublator: Sublate | None = None
    ):
        self._contradict = contradictor or contradict_agent
        self._sublate = sublator or sublate_agent

    @property
    def name(self) -> str:
        return "H-hegel"

    @property
    def genus(self) -> str:
        return "h"

    @property
    def purpose(self) -> str:
        return "Dialectic synthesis; surfaces contradictions and attempts aufhebung"

    async def invoke(self, input: HegelInput) -> HegelOutput:
        """
        Process thesis/antithesis through dialectic.

        If antithesis is provided, directly attempt synthesis.
        If antithesis is None, first surface contradictions in thesis.
        """
        thesis = input.thesis
        antithesis = input.antithesis

        # If no explicit antithesis, try to surface one
        if antithesis is None:
            antithesis = await self._surface_antithesis(thesis, input.context)
            if antithesis is None:
                # No contradiction found - thesis stands alone
                return HegelOutput(
                    synthesis=thesis,
                    sublation_notes="No antithesis surfaced; thesis stands without contradiction",
                    productive_tension=False,
                    next_thesis=thesis
                )

        # Detect tension between thesis and antithesis
        tension = await contradict(thesis, antithesis)

        if tension is None:
            # No actual tension - apparent contradiction isn't real
            return HegelOutput(
                synthesis=thesis,
                sublation_notes="Apparent contradiction resolved; no genuine tension",
                productive_tension=False,
                next_thesis=thesis
            )

        # Attempt sublation
        result = await sublate(tension)

        if isinstance(result, HoldTension):
            # Tension should be held, not resolved
            return HegelOutput(
                synthesis=None,
                sublation_notes=f"Holding tension: {result.reason}",
                productive_tension=True,
                next_thesis=None
            )

        # Synthesis achieved
        assert isinstance(result, Synthesis)
        return HegelOutput(
            synthesis=result.synthesis,
            sublation_notes=self._format_sublation_notes(result),
            productive_tension=False,
            next_thesis=result.synthesis  # Synthesis becomes new thesis
        )

    async def _surface_antithesis(
        self,
        thesis: Any,
        context: dict[str, Any]
    ) -> Any | None:
        """
        Surface implicit antithesis from thesis.

        Strategies:
        1. Direct negation (not-thesis)
        2. Context-based opposition
        3. Value conflict identification
        """
        # Strategy 1: Direct negation for simple types
        if isinstance(thesis, bool):
            return not thesis

        if isinstance(thesis, str):
            # Look for implicit oppositions
            opposition_map = {
                "simple": "complex",
                "fast": "thorough",
                "readable": "performant",
                "centralized": "distributed",
                "automated": "manual",
                "strict": "flexible",
            }
            thesis_lower = thesis.lower()
            for key, opposite in opposition_map.items():
                if key in thesis_lower:
                    return thesis.replace(key, opposite).replace(key.capitalize(), opposite.capitalize())

        # Strategy 2: Context-based opposition
        if "opposing_view" in context:
            return context["opposing_view"]

        # Strategy 3: Check for internal tension in thesis
        if isinstance(thesis, str) and " but " in thesis.lower():
            # Thesis contains internal tension
            parts = thesis.lower().split(" but ")
            if len(parts) == 2:
                return parts[1].strip()

        return None

    def _format_sublation_notes(self, synthesis: Synthesis) -> str:
        """Format synthesis into readable sublation notes"""
        preserved = ", ".join(str(p) for p in synthesis.preserved)
        negated = ", ".join(str(n) for n in synthesis.negated)

        notes = []
        if preserved:
            notes.append(f"Preserved: {preserved}")
        if negated:
            notes.append(f"Negated: {negated}")
        notes.append(f"Elevated: {synthesis.synthesis}")

        return "; ".join(notes)


# Singleton instance
hegel_agent = Hegel()


async def dialectic(
    thesis: Any,
    antithesis: Any | None = None,
    context: dict[str, Any] | None = None
) -> HegelOutput:
    """
    Convenience function for dialectic synthesis.

    Example:
        result = await dialectic(
            thesis="Code should be readable",
            antithesis="Code should be fast"
        )
    """
    return await hegel_agent.invoke(HegelInput(
        thesis=thesis,
        antithesis=antithesis,
        context=context or {}
    ))


async def hold_or_synthesize(thesis: Any, antithesis: Any) -> tuple[bool, Any]:
    """
    Convenience function that returns (is_held, result).

    Returns:
        (True, None) if tension should be held
        (False, synthesis) if synthesis achieved
    """
    result = await dialectic(thesis, antithesis)
    return (result.productive_tension, result.synthesis)
