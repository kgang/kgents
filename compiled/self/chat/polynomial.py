"""
ChatPolynomial: State machine for Chat

Auto-generated from: spec/self/chat.md
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


class ChatPhase(Enum):
    """
    Positions in the chat polynomial.

    These are interpretive frames, not internal states.
    """

    IDLE = auto()
    LISTENING = auto()
    THINKING = auto()
    RESPONDING = auto()
    REFLECTING = auto()


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class ChatInput:
    """Generic input for chat transitions."""

    action: str
    payload: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class ChatOutput:
    """Output from chat transitions."""

    phase: ChatPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def flow_directions(phase: ChatPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each chat phase.

    TODO: Implement mode-dependent input validation.
    """
    # Default: accept any input in any phase
    return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def flow_transition(phase: ChatPhase, input: Any) -> tuple[ChatPhase, ChatOutput]:
    """
    Chat state transition function.

    TODO: Implement actual transition logic.
    """
    # Default: stay in same phase, report success
    return phase, ChatOutput(
        phase=phase,
        success=True,
        message=f"Processed {type(input).__name__} in {phase.name}",
    )


# =============================================================================
# The Polynomial Agent
# =============================================================================


CHAT_POLYNOMIAL: PolyAgent[ChatPhase, Any, ChatOutput] = PolyAgent(
    name="ChatPolynomial",
    positions=frozenset(ChatPhase),
    _directions=flow_directions,
    _transition=flow_transition,
)
"""
The Chat polynomial agent.

Positions: 5 phases
Generated from: spec/self/chat.md
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "ChatPhase",
    # Input/Output
    "ChatInput",
    "ChatOutput",
    # Functions
    "flow_directions",
    "flow_transition",
    # Polynomial
    "CHAT_POLYNOMIAL",
]
