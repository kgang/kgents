"""
MemoryPolynomial: State machine for Memory

Auto-generated from: spec/self/memory.md
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


class MemoryPhase(Enum):
    """
    Positions in the memory polynomial.

    These are interpretive frames, not internal states.
    """

    IDLE = auto()
    CAPTURING = auto()
    SEARCHING = auto()
    SURFACING = auto()
    HEALING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class MemoryInput:
    """Generic input for memory transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class MemoryOutput:
    """Output from memory transitions."""

    phase: MemoryPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def brain_directions(phase: MemoryPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each memory phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def brain_transition(
    phase: MemoryPhase, input: Any
) -> tuple[MemoryPhase, MemoryOutput]:
    """
    Memory state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, MemoryOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


MEMORY_POLYNOMIAL: PolyAgent[MemoryPhase, Any, MemoryOutput] = PolyAgent(
    name="MemoryPolynomial",
    positions=frozenset(MemoryPhase),
    _directions=brain_directions,
    _transition=brain_transition,
)
"""
The Memory polynomial agent.

Positions: 5 phases
Generated from: spec/self/memory.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "MemoryPhase",
    # Input/Output
    "MemoryInput",
    "MemoryOutput",
    # Functions
    "brain_directions",
    "brain_transition",
    # Polynomial
    "MEMORY_POLYNOMIAL",
]
