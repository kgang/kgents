"""
ParkPolynomial: State machine for Park

Auto-generated from: spec/world/park.md
Edit with care - regeneration will overwrite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Phase Enum (Positions in the Polynomial)
# =============================================================================


class ParkPhase(Enum):
    """
    Positions in the park polynomial.

    These are interpretive frames, not internal states.
    """

    OBSERVING = auto()
    BUILDING = auto()
    INTERVENING = auto()
    COOLDOWN = auto()
    COMPLETE = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class ParkInput:
    """Generic input for park transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class ParkOutput:
    """Output from park transitions."""

    phase: ParkPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def director_directions(phase: ParkPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each park phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def director_transition(phase: ParkPhase, input: Any) -> tuple[ParkPhase, ParkOutput]:
    """
    Park state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, ParkOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


PARK_POLYNOMIAL: PolyAgent[ParkPhase, Any, ParkOutput] = PolyAgent(
    name="ParkPolynomial",
    positions=frozenset(ParkPhase),
    _directions=director_directions,
    _transition=director_transition,
)
"""
The Park polynomial agent.

Positions: 5 phases
Generated from: spec/world/park.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "ParkPhase",
    # Input/Output
    "ParkInput",
    "ParkOutput",
    # Functions
    "director_directions",
    "director_transition",
    # Polynomial
    "PARK_POLYNOMIAL",
]
