"""
CodebasePolynomial: State machine for Codebase

Auto-generated from: spec/world/codebase.md
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


class CodebasePhase(Enum):
    """
    Positions in the codebase polynomial.

    These are interpretive frames, not internal states.
    """

    IDLE = auto()
    SCANNING = auto()
    WATCHING = auto()
    ANALYZING = auto()
    HEALING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class CodebaseInput:
    """Generic input for codebase transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class CodebaseOutput:
    """Output from codebase transitions."""

    phase: CodebasePhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def gestalt_directions(phase: CodebasePhase) -> FrozenSet[Any]:
    """
    Valid inputs for each codebase phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def gestalt_transition(
    phase: CodebasePhase, input: Any
) -> tuple[CodebasePhase, CodebaseOutput]:
    """
    Codebase state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, CodebaseOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


CODEBASE_POLYNOMIAL: PolyAgent[CodebasePhase, Any, CodebaseOutput] = PolyAgent(
    name="CodebasePolynomial",
    positions=frozenset(CodebasePhase),
    _directions=gestalt_directions,
    _transition=gestalt_transition,
)
"""
The Codebase polynomial agent.

Positions: 5 phases
Generated from: spec/world/codebase.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "CodebasePhase",
    # Input/Output
    "CodebaseInput",
    "CodebaseOutput",
    # Functions
    "gestalt_directions",
    "gestalt_transition",
    # Polynomial
    "CODEBASE_POLYNOMIAL",
]
