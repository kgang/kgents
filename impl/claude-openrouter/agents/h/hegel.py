"""
H-hegel: Dialectic Synthesis Agent

Surfaces contradictions and synthesizes them into higher-order understanding.

Composes bootstrap primitives: Contradict >> Sublate

Pattern: thesis + antithesis → synthesis (or hold productive tension)
"""

from dataclasses import dataclass
from typing import Any, Optional

from bootstrap.types import (
    Agent,
    Tension,
    TensionMode,
    Synthesis,
    ResolutionType,
    HoldTension,
)
from bootstrap.contradict import Contradict
from bootstrap.sublate import Sublate


@dataclass
class DialecticInput:
    """Input for dialectic synthesis."""
    thesis: Any
    antithesis: Optional[Any] = None  # If None, H-hegel surfaces it
    context: Optional[dict] = None


@dataclass
class DialecticOutput:
    """Result of dialectic synthesis."""
    synthesis: Optional[Any]
    sublation_notes: str  # What was preserved, negated, elevated
    productive_tension: bool  # True if synthesis is premature
    next_thesis: Optional[Any] = None  # For recursive dialectic
    tension: Optional[Tension] = None  # The detected tension


class HegelAgent(Agent[DialecticInput, DialecticOutput]):
    """
    Dialectic synthesis agent.

    Composes Contradict and Sublate:
    1. If antithesis not provided, surfaces it via Contradict
    2. Attempts synthesis via Sublate
    3. Returns synthesis or holds productive tension
    """

    def __init__(self, contradict: Optional[Contradict] = None, sublate: Optional[Sublate] = None):
        self._contradict = contradict or Contradict()
        self._sublate = sublate or Sublate()

    @property
    def name(self) -> str:
        return "H-hegel"

    async def invoke(self, input: DialecticInput) -> DialecticOutput:
        """
        Perform dialectic synthesis.

        1. Surface tension (thesis vs antithesis)
        2. Attempt sublation
        3. Return synthesis or acknowledge productive tension
        """
        # Surface tension
        if input.antithesis is not None:
            # Explicit dialectic - tension provided
            tension = Tension(
                mode=TensionMode.LOGICAL,
                thesis=input.thesis,
                antithesis=input.antithesis,
                description=f"Tension between: {input.thesis} vs {input.antithesis}",
            )
        else:
            # Implicit dialectic - surface antithesis
            tension = await self._contradict.invoke((input.thesis, None))
            if tension is None:
                # No contradiction found - thesis stands alone
                return DialecticOutput(
                    synthesis=input.thesis,
                    sublation_notes="No antithesis surfaced. Thesis preserved as-is.",
                    productive_tension=False,
                )

        # Attempt sublation
        result = await self._sublate.invoke(tension)

        if isinstance(result, HoldTension):
            # Productive tension - don't force synthesis
            return DialecticOutput(
                synthesis=None,
                sublation_notes=result.reason,
                productive_tension=True,
                tension=tension,
            )

        # Synthesis achieved
        synthesis: Synthesis = result
        return DialecticOutput(
            synthesis=synthesis.result,
            sublation_notes=synthesis.explanation,
            productive_tension=False,
            next_thesis=synthesis.result if synthesis.resolution_type == ResolutionType.ELEVATE else None,
            tension=tension,
        )


class ContinuousDialectic(Agent[list[Any], list[DialecticOutput]]):
    """
    Recursive dialectic - apply Hegel repeatedly until stability.

    Each synthesis becomes the new thesis.
    Stops when no more contradictions emerge or tension is held.
    """

    def __init__(self, max_iterations: int = 5):
        self._hegel = HegelAgent()
        self._max_iterations = max_iterations

    @property
    def name(self) -> str:
        return "ContinuousDialectic"

    async def invoke(self, theses: list[Any]) -> list[DialecticOutput]:
        """Apply dialectic recursively to a list of theses."""
        if len(theses) == 0:
            return []

        if len(theses) == 1:
            # Single thesis - surface antithesis
            result = await self._hegel.invoke(DialecticInput(thesis=theses[0]))
            return [result]

        outputs = []
        current = theses[0]

        for i, antithesis in enumerate(theses[1:], 1):
            result = await self._hegel.invoke(
                DialecticInput(thesis=current, antithesis=antithesis)
            )
            outputs.append(result)

            if result.productive_tension:
                # Stop at productive tension
                break

            if result.next_thesis:
                current = result.next_thesis
            elif result.synthesis:
                current = result.synthesis
            else:
                break

            if i >= self._max_iterations:
                break

        return outputs


# Convenience functions

def hegel() -> HegelAgent:
    """Create a dialectic synthesis agent."""
    return HegelAgent()


def continuous_dialectic(max_iterations: int = 5) -> ContinuousDialectic:
    """Create a continuous dialectic agent."""
    return ContinuousDialectic(max_iterations)
