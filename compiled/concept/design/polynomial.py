"""
DesignPolynomial: State machine for Design

Auto-generated from: spec/concept/design.md
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


class DesignPhase(Enum):
    """
    Positions in the design polynomial.

    These are interpretive frames, not internal states.
    """

    NEUTRAL = auto()
    COMPOSING = auto()
    DEGRADING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class DesignInput:
    """Generic input for design transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class DesignOutput:
    """Output from design transitions."""

    phase: DesignPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def design_directions(phase: DesignPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each design phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def design_transition(
    phase: DesignPhase, input: Any
) -> tuple[DesignPhase, DesignOutput]:
    """
    Design state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, DesignOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


DESIGN_POLYNOMIAL: PolyAgent[DesignPhase, Any, DesignOutput] = PolyAgent(
    name="DesignPolynomial",
    positions=frozenset(DesignPhase),
    _directions=design_directions,
    _transition=design_transition,
)
"""
The Design polynomial agent.

Positions: 3 phases
Generated from: spec/concept/design.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "DesignPhase",
    # Input/Output
    "DesignInput",
    "DesignOutput",
    # Functions
    "design_directions",
    "design_transition",
    # Polynomial
    "DESIGN_POLYNOMIAL",
]
