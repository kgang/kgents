"""
AtelierPolynomial: State machine for Atelier

Auto-generated from: spec/world/atelier.md
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


class AtelierPhase(Enum):
    """
    Positions in the atelier polynomial.

    These are interpretive frames, not internal states.
    """

    GATHERING = auto()
    CREATING = auto()
    REVIEWING = auto()
    EXHIBITING = auto()
    CLOSED = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class AtelierInput:
    """Generic input for atelier transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class AtelierOutput:
    """Output from atelier transitions."""

    phase: AtelierPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def workshop_directions(phase: AtelierPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each atelier phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def workshop_transition(
    phase: AtelierPhase, input: Any
) -> tuple[AtelierPhase, AtelierOutput]:
    """
    Atelier state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, AtelierOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


ATELIER_POLYNOMIAL: PolyAgent[AtelierPhase, Any, AtelierOutput] = PolyAgent(
    name="AtelierPolynomial",
    positions=frozenset(AtelierPhase),
    _directions=workshop_directions,
    _transition=workshop_transition,
)
"""
The Atelier polynomial agent.

Positions: 5 phases
Generated from: spec/world/atelier.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "AtelierPhase",
    # Input/Output
    "AtelierInput",
    "AtelierOutput",
    # Functions
    "workshop_directions",
    "workshop_transition",
    # Polynomial
    "ATELIER_POLYNOMIAL",
]
