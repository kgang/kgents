"""
TownPolynomial: State machine for Town

Auto-generated from: spec/world/town.md
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


class TownPhase(Enum):
    """
    Positions in the town polynomial.

    These are interpretive frames, not internal states.
    """

    IDLE = auto()
    SOCIALIZING = auto()
    WORKING = auto()
    REFLECTING = auto()
    RESTING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class TownInput:
    """Generic input for town transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class TownOutput:
    """Output from town transitions."""

    phase: TownPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def citizen_directions(phase: TownPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each town phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def citizen_transition(phase: TownPhase, input: Any) -> tuple[TownPhase, TownOutput]:
    """
    Town state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, TownOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


TOWN_POLYNOMIAL: PolyAgent[TownPhase, Any, TownOutput] = PolyAgent(
    name="TownPolynomial",
    positions=frozenset(TownPhase),
    _directions=citizen_directions,
    _transition=citizen_transition,
)
"""
The Town polynomial agent.

Positions: 5 phases
Generated from: spec/world/town.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "TownPhase",
    # Input/Output
    "TownInput",
    "TownOutput",
    # Functions
    "citizen_directions",
    "citizen_transition",
    # Polynomial
    "TOWN_POLYNOMIAL",
]
