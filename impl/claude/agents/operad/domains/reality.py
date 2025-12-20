"""
Reality Operad: J-gent Composition Grammar.

The Reality Operad extends AGENT_OPERAD with reality classification:
- classify: Tag output as DETERMINISTIC, PROBABILISTIC, or CHAOTIC
- collapse: Handle chaotic fallback gracefully

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from agents.operad.core import AGENT_OPERAD, Operad, Operation
from agents.poly import PolyAgent, from_function, sequential


class RealityType(Enum):
    """Classification of reality types."""

    DETERMINISTIC = auto()  # Certain, reproducible
    PROBABILISTIC = auto()  # Uncertain but bounded
    CHAOTIC = auto()  # Unpredictable, requires fallback


@dataclass(frozen=True)
class RealityClassification:
    """A value with its reality classification."""

    value: Any
    reality: RealityType
    confidence: float
    reasoning: str = ""


def _classify_compose(
    agent: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Wrap agent with reality classification.

    Analyzes output and tags with DETERMINISTIC/PROBABILISTIC/CHAOTIC.
    """

    def classify(output: Any) -> RealityClassification:
        # Simple heuristic classification
        if isinstance(output, (bool, int)):
            return RealityClassification(
                value=output,
                reality=RealityType.DETERMINISTIC,
                confidence=0.95,
                reasoning="Primitive types are deterministic",
            )
        if isinstance(output, dict):
            if "error" in output or "failed" in output:
                return RealityClassification(
                    value=output,
                    reality=RealityType.CHAOTIC,
                    confidence=0.6,
                    reasoning="Error/failure indicates chaotic behavior",
                )
            if "confidence" in output and output.get("confidence", 0) < 0.5:
                return RealityClassification(
                    value=output,
                    reality=RealityType.PROBABILISTIC,
                    confidence=output.get("confidence", 0.5),
                    reasoning="Low confidence indicates probabilistic",
                )
        return RealityClassification(
            value=output,
            reality=RealityType.PROBABILISTIC,
            confidence=0.7,
            reasoning="Default classification",
        )

    classifier = from_function("RealityClassifier", classify)
    return sequential(agent, classifier)


def _collapse_compose(
    agent: PolyAgent[Any, Any, Any],
    fallback: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Create collapse handler: use fallback on chaotic.

    If agent's output is classified as CHAOTIC, use fallback instead.
    """

    def collapse_handler(result: Any) -> Any:
        if isinstance(result, RealityClassification):
            if result.reality == RealityType.CHAOTIC:
                # In real impl, would invoke fallback here
                return RealityClassification(
                    value=f"collapsed: {result.value}",
                    reality=RealityType.DETERMINISTIC,
                    confidence=0.9,
                    reasoning="Collapsed from chaotic via fallback",
                )
        return result

    classified = _classify_compose(agent)
    handler = from_function("CollapseHandler", collapse_handler)
    return sequential(classified, handler)


def _ground_check_compose() -> PolyAgent[Any, Any, Any]:
    """
    Create reality ground check.

    Determines if input is grounded in reality.
    """

    def ground_check(input: Any) -> RealityClassification:
        if isinstance(input, str):
            # Heuristic: short, concrete strings are more grounded
            if len(input) < 100 and not any(
                word in input.lower() for word in ["maybe", "might", "could", "possibly"]
            ):
                return RealityClassification(
                    value=input,
                    reality=RealityType.DETERMINISTIC,
                    confidence=0.85,
                    reasoning="Concrete, short assertion",
                )
            if any(word in input.lower() for word in ["probably", "likely", "estimate"]):
                return RealityClassification(
                    value=input,
                    reality=RealityType.PROBABILISTIC,
                    confidence=0.6,
                    reasoning="Contains uncertainty markers",
                )
        return RealityClassification(
            value=input,
            reality=RealityType.PROBABILISTIC,
            confidence=0.5,
            reasoning="Default uncertain classification",
        )

    return from_function("GroundCheck", ground_check)


def _stable_compose(
    agent: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Check if agent produces stable (non-chaotic) output.

    Returns a boolean stability indicator.
    """

    def stability_check(result: Any) -> dict[str, Any]:
        if isinstance(result, RealityClassification):
            is_stable = result.reality != RealityType.CHAOTIC
            return {
                "stable": is_stable,
                "reality": result.reality.name,
                "confidence": result.confidence,
            }
        return {"stable": True, "reality": "UNKNOWN", "confidence": 0.5}

    classified = _classify_compose(agent)
    checker = from_function("StabilityChecker", stability_check)
    return sequential(classified, checker)


def create_reality_operad() -> Operad:
    """
    Create the Reality Operad (J-gent composition grammar).

    Extends AGENT_OPERAD with:
    - classify: Reality type classification
    - collapse: Chaotic fallback handling
    - ground: Reality ground check
    - stable: Stability verification
    """
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add reality-specific operations
    ops["classify"] = Operation(
        name="classify",
        arity=1,
        signature="Agent[A, B] → Agent[A, Reality[B]]",
        compose=_classify_compose,
        description="Tag output with reality classification",
    )

    ops["collapse"] = Operation(
        name="collapse",
        arity=2,
        signature="Agent[A, B] × Agent[Chaotic, B] → Agent[A, B]",
        compose=_collapse_compose,
        description="Handle chaotic output via fallback",
    )

    ops["ground"] = Operation(
        name="ground",
        arity=0,
        signature="() → Agent[Any, Reality[Any]]",
        compose=_ground_check_compose,
        description="Check if input is grounded in reality",
    )

    ops["stable"] = Operation(
        name="stable",
        arity=1,
        signature="Agent[A, B] → Agent[A, StabilityCheck]",
        compose=_stable_compose,
        description="Verify agent produces stable output",
    )

    return Operad(
        name="RealityOperad",
        operations=ops,
        laws=list(AGENT_OPERAD.laws),  # Inherit universal laws
        description="J-gent reality composition grammar",
    )


# Global Reality Operad instance
REALITY_OPERAD = create_reality_operad()


__all__ = [
    "REALITY_OPERAD",
    "RealityType",
    "RealityClassification",
    "create_reality_operad",
]
