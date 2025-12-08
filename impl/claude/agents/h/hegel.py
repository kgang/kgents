"""
H-hegel: Dialectic Synthesis Agent

Surfaces contradictions and synthesizes them into higher-order understanding.

Composes bootstrap primitives: Contradict >> Sublate

Pattern: thesis + antithesis → synthesis (or hold productive tension)
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import logging

from bootstrap.types import (
    Agent,
    ContradictInput,
    SublateInput,
    Tension,
    TensionMode,
    Synthesis,
    HoldTension,
)
from bootstrap.contradict import Contradict
from bootstrap.sublate import Sublate


logger = logging.getLogger(__name__)


@dataclass
class DialecticInput:
    """Input for dialectic synthesis."""
    thesis: Any
    antithesis: Optional[Any] = None  # If None, H-hegel surfaces it
    context: Optional[dict[str, Any]] = None


@dataclass
class DialecticStep:
    """
    A single step in the dialectic process.

    Tracks the lineage of thesis/antithesis/synthesis for observability.
    """
    stage: str  # "surface_tension", "attempt_sublation", "synthesis", "hold_tension"
    thesis: Any
    antithesis: Optional[Any]
    result: Optional[Any]  # Synthesis or HoldTension
    notes: str
    timestamp: Optional[str] = None  # Future: add timestamps for temporal tracking


@dataclass
class DialecticOutput:
    """
    Result of dialectic synthesis.

    Enhanced with lineage tracking for observability (Issue #7).
    """
    synthesis: Optional[Any]
    sublation_notes: str  # What was preserved, negated, elevated
    productive_tension: bool  # True if synthesis is premature
    next_thesis: Optional[Any] = None  # For recursive dialectic
    tension: Optional[Tension] = None  # The detected tension

    # Issue #7: Lineage tracking
    lineage: list[DialecticStep] = field(default_factory=list)  # Full chain of dialectic steps
    metadata: dict[str, Any] = field(default_factory=dict)  # Extensible observability data


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
        Perform dialectic synthesis with full lineage tracking.

        1. Surface tension (thesis vs antithesis)
        2. Attempt sublation
        3. Return synthesis or acknowledge productive tension
        """
        lineage: list[DialecticStep] = []
        metadata: dict[str, Any] = {
            "has_explicit_antithesis": input.antithesis is not None,
            "thesis_type": type(input.thesis).__name__,
        }

        logger.info(
            "dialectic.start",
            extra={
                "agent": self.name,
                **metadata,
            }
        )

        # Surface tension
        if input.antithesis is not None:
            # Explicit dialectic - tension provided
            tension = Tension(
                mode=TensionMode.LOGICAL,
                thesis=input.thesis,
                antithesis=input.antithesis,
                severity=0.5,
                description=f"Tension between: {input.thesis} vs {input.antithesis}",
            )
            lineage.append(DialecticStep(
                stage="explicit_tension",
                thesis=input.thesis,
                antithesis=input.antithesis,
                result=tension,
                notes=f"Explicit tension provided: {tension.mode.value}",
            ))
            logger.debug(
                "tension.explicit",
                extra={"tension_mode": tension.mode.value}
            )
        else:
            # Implicit dialectic - surface antithesis
            logger.debug("surfacing.antithesis")
            contradict_result = await self._contradict.invoke(ContradictInput(a=input.thesis, b=None))
            if contradict_result.no_tension or not contradict_result.tensions:
                # No contradiction found - thesis stands alone
                lineage.append(DialecticStep(
                    stage="no_antithesis",
                    thesis=input.thesis,
                    antithesis=None,
                    result=input.thesis,
                    notes="No contradiction detected; thesis preserved as-is.",
                ))
                logger.info(
                    "dialectic.complete",
                    extra={
                        "outcome": "no_antithesis",
                        "synthesis_achieved": True,
                    }
                )
                return DialecticOutput(
                    synthesis=input.thesis,
                    sublation_notes="No antithesis surfaced. Thesis preserved as-is.",
                    productive_tension=False,
                    lineage=lineage,
                    metadata=metadata,
                )
            tension = contradict_result.tensions[0]
            lineage.append(DialecticStep(
                stage="surface_antithesis",
                thesis=input.thesis,
                antithesis=tension.antithesis,
                result=tension,
                notes=f"Surfaced antithesis via Contradict: {tension.description}",
            ))
            logger.debug(
                "tension.surfaced",
                extra={"tension_mode": tension.mode.value}
            )

        # Attempt sublation
        logger.debug("attempting.sublation")
        result = await self._sublate.invoke(SublateInput(tensions=(tension,)))

        if isinstance(result, HoldTension):
            # Productive tension - don't force synthesis
            lineage.append(DialecticStep(
                stage="hold_tension",
                thesis=tension.thesis,
                antithesis=tension.antithesis,
                result=result,
                notes=f"Holding productive tension: {result.why_held}",
            ))
            logger.info(
                "dialectic.complete",
                extra={
                    "outcome": "tension_held",
                    "reason": result.why_held,
                    "synthesis_achieved": False,
                }
            )
            return DialecticOutput(
                synthesis=None,
                sublation_notes=result.why_held,
                productive_tension=True,
                tension=tension,
                lineage=lineage,
                metadata=metadata,
            )

        # Synthesis achieved
        synthesis: Synthesis = result
        lineage.append(DialecticStep(
            stage="synthesis",
            thesis=tension.thesis,
            antithesis=tension.antithesis,
            result=synthesis.result,
            notes=f"Synthesis via {synthesis.resolution_type}: {synthesis.explanation}",
        ))
        logger.info(
            "dialectic.complete",
            extra={
                "outcome": "synthesis",
                "resolution_type": synthesis.resolution_type,
                "has_next_thesis": synthesis.resolution_type == "elevate",
            }
        )
        return DialecticOutput(
            synthesis=synthesis.result,
            sublation_notes=synthesis.explanation,
            productive_tension=False,
            next_thesis=synthesis.result if synthesis.resolution_type == "elevate" else None,
            tension=tension,
            lineage=lineage,
            metadata=metadata,
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
            logger.warning("continuous_dialectic.empty_input")
            return []

        logger.info(
            "continuous_dialectic.start",
            extra={
                "thesis_count": len(theses),
                "max_iterations": self._max_iterations,
            }
        )

        if len(theses) == 1:
            # Single thesis - surface antithesis
            result = await self._hegel.invoke(DialecticInput(thesis=theses[0]))
            logger.info(
                "continuous_dialectic.complete",
                extra={"iterations": 1, "stopped_reason": "single_thesis"}
            )
            return [result]

        outputs = []
        current = theses[0]

        for i, antithesis in enumerate(theses[1:], 1):
            logger.debug(
                "continuous_dialectic.iteration",
                extra={"iteration": i, "max_iterations": self._max_iterations}
            )
            result = await self._hegel.invoke(
                DialecticInput(thesis=current, antithesis=antithesis)
            )
            outputs.append(result)

            if result.productive_tension:
                # Stop at productive tension
                logger.info(
                    "continuous_dialectic.complete",
                    extra={
                        "iterations": i,
                        "stopped_reason": "productive_tension",
                    }
                )
                break

            if result.next_thesis:
                current = result.next_thesis
            elif result.synthesis:
                current = result.synthesis
            else:
                logger.info(
                    "continuous_dialectic.complete",
                    extra={
                        "iterations": i,
                        "stopped_reason": "no_progression",
                    }
                )
                break

            if i >= self._max_iterations:
                logger.info(
                    "continuous_dialectic.complete",
                    extra={
                        "iterations": i,
                        "stopped_reason": "max_iterations_reached",
                    }
                )
                break

        if not any([result.productive_tension for result in outputs]) and len(outputs) < len(theses) - 1:
            logger.warning(
                "continuous_dialectic.incomplete",
                extra={
                    "processed": len(outputs),
                    "total_theses": len(theses),
                }
            )

        return outputs


# Convenience functions

def hegel() -> HegelAgent:
    """Create a dialectic synthesis agent."""
    return HegelAgent()


def continuous_dialectic(max_iterations: int = 5) -> ContinuousDialectic:
    """Create a continuous dialectic agent."""
    return ContinuousDialectic(max_iterations)
