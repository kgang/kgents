"""
Flow Polynomial: State machine for flow agents.

The FlowPolynomial captures the mode-dependent behavior of flow agents
using Spivak's polynomial functor formalism.

P(y) = Σ_{s ∈ positions} y^{directions(s)}

See: spec/f-gents/README.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, FrozenSet, Generic, TypeVar

from agents.f.state import FlowState

# Type variables
S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass(frozen=True)
class FlowPolynomial(Generic[S, A, B]):
    """
    Polynomial functor for flow agents.

    Positions (states): {DORMANT, STREAMING, BRANCHING, CONVERGING, DRAINING, COLLAPSED}
    Directions: State-dependent valid inputs
    Transition: (State, Input) -> (State, Output)

    This captures the essential structure of all flow modalities:
    - Chat: Primarily STREAMING with context management
    - Research: STREAMING -> BRANCHING -> CONVERGING cycles
    - Collaboration: STREAMING with multi-agent injection
    """

    name: str
    positions: FrozenSet[S]
    _directions: Callable[[S], FrozenSet[A]]
    _transition: Callable[[S, A], tuple[S, B]]

    def directions(self, state: S) -> FrozenSet[A]:
        """Get valid inputs for a state."""
        return self._directions(state)

    def transition(self, state: S, input: A) -> tuple[S, B]:
        """Execute state transition."""
        return self._transition(state, input)

    def invoke(self, state: S, input: A) -> tuple[S, B]:
        """
        Execute one step of the dynamical system.

        Args:
            state: Current state (must be in positions)
            input: Input value

        Returns:
            Tuple of (new_state, output)

        Raises:
            ValueError: If state is invalid
        """
        if state not in self.positions:
            msg = f"Invalid state: {state} not in {self.positions}"
            raise ValueError(msg)

        return self.transition(state, input)


# ============================================================================
# Flow Polynomial Instances
# ============================================================================


def _flow_directions(state: FlowState) -> FrozenSet[str]:
    """Get valid inputs for each flow state."""
    return {
        FlowState.DORMANT: frozenset(["start", "configure"]),
        FlowState.STREAMING: frozenset(["message", "perturb", "stop", "branch"]),
        FlowState.BRANCHING: frozenset(["expand", "prune", "stream", "stop"]),
        FlowState.CONVERGING: frozenset(["merge", "synthesize", "stream", "stop"]),
        FlowState.DRAINING: frozenset(["stop", "flush"]),
        FlowState.COLLAPSED: frozenset(["reset", "harvest"]),
    }[state]


def _chat_transition(state: FlowState, input: str) -> tuple[FlowState, dict[str, Any]]:
    """State transition for chat modality."""
    match (state, input):
        case (FlowState.DORMANT, "start"):
            return FlowState.STREAMING, {"event": "started"}
        case (FlowState.DORMANT, "configure"):
            return FlowState.DORMANT, {"event": "configured"}
        case (FlowState.STREAMING, "message"):
            return FlowState.STREAMING, {"event": "message_processed"}
        case (FlowState.STREAMING, "perturb"):
            return FlowState.STREAMING, {"event": "perturbation_handled"}
        case (FlowState.STREAMING, "stop"):
            return FlowState.DRAINING, {"event": "stopping"}
        case (FlowState.DRAINING, "flush"):
            return FlowState.DRAINING, {"event": "flushing"}
        case (FlowState.DRAINING, "stop"):
            return FlowState.COLLAPSED, {"event": "stopped"}
        case (FlowState.COLLAPSED, "reset"):
            return FlowState.DORMANT, {"event": "reset"}
        case (FlowState.COLLAPSED, "harvest"):
            return FlowState.COLLAPSED, {"event": "harvested"}
        case _:
            msg = f"Invalid transition: ({state}, {input})"
            raise ValueError(msg)


def _research_transition(
    state: FlowState, input: str
) -> tuple[FlowState, dict[str, Any]]:
    """State transition for research modality."""
    match (state, input):
        case (FlowState.DORMANT, "start"):
            return FlowState.STREAMING, {"event": "started"}
        case (FlowState.STREAMING, "message"):
            return FlowState.STREAMING, {"event": "exploring"}
        case (FlowState.STREAMING, "branch"):
            return FlowState.BRANCHING, {"event": "branching"}
        case (FlowState.STREAMING, "stop"):
            return FlowState.CONVERGING, {"event": "converging"}
        case (FlowState.BRANCHING, "expand"):
            return FlowState.BRANCHING, {"event": "expanded"}
        case (FlowState.BRANCHING, "prune"):
            return FlowState.BRANCHING, {"event": "pruned"}
        case (FlowState.BRANCHING, "stream"):
            return FlowState.STREAMING, {"event": "returning_to_stream"}
        case (FlowState.BRANCHING, "stop"):
            return FlowState.CONVERGING, {"event": "forced_converge"}
        case (FlowState.CONVERGING, "merge"):
            return FlowState.CONVERGING, {"event": "merged"}
        case (FlowState.CONVERGING, "synthesize"):
            return FlowState.COLLAPSED, {"event": "synthesized"}
        case (FlowState.CONVERGING, "stream"):
            return FlowState.STREAMING, {"event": "continuing"}
        case (FlowState.CONVERGING, "stop"):
            return FlowState.COLLAPSED, {"event": "stopped"}
        case (FlowState.COLLAPSED, "reset"):
            return FlowState.DORMANT, {"event": "reset"}
        case (FlowState.COLLAPSED, "harvest"):
            return FlowState.COLLAPSED, {"event": "harvested"}
        case _:
            msg = f"Invalid transition: ({state}, {input})"
            raise ValueError(msg)


def _collaboration_transition(
    state: FlowState, input: str
) -> tuple[FlowState, dict[str, Any]]:
    """State transition for collaboration modality."""
    match (state, input):
        case (FlowState.DORMANT, "start"):
            return FlowState.STREAMING, {"event": "started"}
        case (FlowState.DORMANT, "configure"):
            return FlowState.DORMANT, {"event": "configured"}
        case (FlowState.STREAMING, "message"):
            return FlowState.STREAMING, {"event": "contribution_posted"}
        case (FlowState.STREAMING, "perturb"):
            return FlowState.STREAMING, {"event": "perturbation_handled"}
        case (FlowState.STREAMING, "stop"):
            return FlowState.CONVERGING, {"event": "building_consensus"}
        case (FlowState.CONVERGING, "merge"):
            return FlowState.CONVERGING, {"event": "votes_counted"}
        case (FlowState.CONVERGING, "synthesize"):
            return FlowState.COLLAPSED, {"event": "consensus_reached"}
        case (FlowState.CONVERGING, "stream"):
            return FlowState.STREAMING, {"event": "continuing_discussion"}
        case (FlowState.CONVERGING, "stop"):
            return FlowState.COLLAPSED, {"event": "terminated"}
        case (FlowState.COLLAPSED, "reset"):
            return FlowState.DORMANT, {"event": "reset"}
        case (FlowState.COLLAPSED, "harvest"):
            return FlowState.COLLAPSED, {"event": "harvested"}
        case _:
            msg = f"Invalid transition: ({state}, {input})"
            raise ValueError(msg)


# ============================================================================
# Polynomial Instances
# ============================================================================

FLOW_POSITIONS = frozenset(FlowState)

CHAT_POLYNOMIAL = FlowPolynomial(
    name="ChatPolynomial",
    positions=FLOW_POSITIONS,
    _directions=_flow_directions,
    _transition=_chat_transition,
)
"""Polynomial for chat modality. Primarily STREAMING with context management."""

RESEARCH_POLYNOMIAL = FlowPolynomial(
    name="ResearchPolynomial",
    positions=FLOW_POSITIONS,
    _directions=_flow_directions,
    _transition=_research_transition,
)
"""Polynomial for research modality. STREAMING -> BRANCHING -> CONVERGING cycles."""

COLLABORATION_POLYNOMIAL = FlowPolynomial(
    name="CollaborationPolynomial",
    positions=FLOW_POSITIONS,
    _directions=_flow_directions,
    _transition=_collaboration_transition,
)
"""Polynomial for collaboration modality. STREAMING with multi-agent injection."""

# Alias for the general flow polynomial
FLOW_POLYNOMIAL = CHAT_POLYNOMIAL


def get_polynomial(modality: str) -> FlowPolynomial[FlowState, str, dict[str, Any]]:
    """Get the polynomial for a modality."""
    polynomials = {
        "chat": CHAT_POLYNOMIAL,
        "research": RESEARCH_POLYNOMIAL,
        "collaboration": COLLABORATION_POLYNOMIAL,
    }
    if modality not in polynomials:
        msg = f"Unknown modality: {modality}"
        raise ValueError(msg)
    return polynomials[modality]


__all__ = [
    "FlowPolynomial",
    "FLOW_POLYNOMIAL",
    "CHAT_POLYNOMIAL",
    "RESEARCH_POLYNOMIAL",
    "COLLABORATION_POLYNOMIAL",
    "get_polynomial",
]
