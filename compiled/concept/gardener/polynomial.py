"""
GardenerPolynomial: State machine for Gardener

Auto-generated from: spec/concept/gardener.md
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


class GardenerPhase(Enum):
    """
    Positions in the gardener polynomial.

    These are interpretive frames, not internal states.
    """

    SURVEYING = auto()
    PLANTING = auto()
    TENDING = auto()
    HARVESTING = auto()
    COMPOSTING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class GardenerInput:
    """Generic input for gardener transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class GardenerOutput:
    """Output from gardener transitions."""

    phase: GardenerPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def growth_directions(phase: GardenerPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each gardener phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def growth_transition(
    phase: GardenerPhase, input: Any
) -> tuple[GardenerPhase, GardenerOutput]:
    """
    Gardener state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, GardenerOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


GARDENER_POLYNOMIAL: PolyAgent[GardenerPhase, Any, GardenerOutput] = PolyAgent(
    name="GardenerPolynomial",
    positions=frozenset(GardenerPhase),
    _directions=growth_directions,
    _transition=growth_transition,
)
"""
The Gardener polynomial agent.

Positions: 5 phases
Generated from: spec/concept/gardener.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "GardenerPhase",
    # Input/Output
    "GardenerInput",
    "GardenerOutput",
    # Functions
    "growth_directions",
    "growth_transition",
    # Polynomial
    "GARDENER_POLYNOMIAL",
]
