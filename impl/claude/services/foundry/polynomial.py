"""
FoundryPolynomial — State Machine for Agent Foundry.

The Foundry polynomial models the JIT agent compilation pipeline as a
mode-dependent state machine following AD-002 (Polynomial Generalization).

States:
- IDLE: Ready for new forge request
- CLASSIFYING: Running RealityClassifier
- GENERATING: Running MetaArchitect (PROBABILISTIC only)
- VALIDATING: Running Chaosmonger
- SELECTING: Running TargetSelector
- PROJECTING: Running Projector
- CACHING: Storing result
- FAILED: Error state

Teaching:
    gotcha: The polynomial defines DIRECTION SETS (valid inputs per state).
            _foundry_directions(state) returns FrozenSet[FoundryEvent] — the
            events that are legal to receive in each state. This is the
            type-safe way to enforce state machine invariants.
            (Evidence: services/foundry/_tests/test_polynomial.py::TestPolynomial::test_valid_inputs_for_idle)

    gotcha: GENERATING is only reachable from CLASSIFYING when reality is
            PROBABILISTIC. DETERMINISTIC/CHAOTIC skip straight to SELECTING.
            This is visible in VALID_TRANSITIONS: CLASSIFYING → {GENERATING, SELECTING}.
            (Evidence: services/foundry/_tests/test_polynomial.py::TestTransitions::test_valid_transitions_from_classifying)

    gotcha: FAILED state only accepts RESET event. This ensures the Foundry
            can always recover to IDLE after an error — no stuck states.
            (Evidence: services/foundry/_tests/test_polynomial.py::TestStateMachine::test_fail)

Example:
    >>> fsm = FoundryStateMachine()
    >>> fsm.state
    FoundryState.IDLE
    >>> fsm.transition(FoundryState.CLASSIFYING, FoundryEvent.START_FORGE)
    True
    >>> FOUNDRY_POLYNOMIAL.valid_inputs(FoundryState.CLASSIFYING)
    frozenset({FoundryEvent.REALITY_CLASSIFIED, FoundryEvent.ERROR})

See: spec/services/foundry.md, spec/principles.md (AD-002)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, FrozenSet


class FoundryState(Enum):
    """
    States for the Foundry polynomial.

    Each state represents a step in the forge pipeline.
    """

    IDLE = auto()  # Ready for new request
    CLASSIFYING = auto()  # Running RealityClassifier
    GENERATING = auto()  # Running MetaArchitect (PROBABILISTIC only)
    VALIDATING = auto()  # Running Chaosmonger
    SELECTING = auto()  # Running TargetSelector
    PROJECTING = auto()  # Running Projector
    CACHING = auto()  # Storing result
    FAILED = auto()  # Error state

    @property
    def is_terminal(self) -> bool:
        """True if this state ends a pipeline."""
        return self in (FoundryState.IDLE, FoundryState.FAILED)

    @property
    def is_processing(self) -> bool:
        """True if actively processing."""
        return self not in (FoundryState.IDLE, FoundryState.FAILED)


class FoundryEvent(Enum):
    """Events that trigger state transitions."""

    START_FORGE = auto()  # Begin forge operation
    REALITY_CLASSIFIED = auto()  # RealityClassifier complete
    SOURCE_GENERATED = auto()  # MetaArchitect complete
    STABILITY_CHECKED = auto()  # Chaosmonger complete
    TARGET_SELECTED = auto()  # TargetSelector complete
    PROJECTION_COMPLETE = auto()  # Projector complete
    CACHED = auto()  # Cache write complete
    ERROR = auto()  # Error occurred
    RESET = auto()  # Return to IDLE


# Valid state transitions
VALID_TRANSITIONS: dict[FoundryState, set[FoundryState]] = {
    FoundryState.IDLE: {FoundryState.CLASSIFYING},
    FoundryState.CLASSIFYING: {
        FoundryState.GENERATING,  # PROBABILISTIC path
        FoundryState.SELECTING,  # DETERMINISTIC/CHAOTIC path (skip generation)
        FoundryState.FAILED,
    },
    FoundryState.GENERATING: {FoundryState.VALIDATING, FoundryState.FAILED},
    FoundryState.VALIDATING: {FoundryState.SELECTING, FoundryState.FAILED},
    FoundryState.SELECTING: {FoundryState.PROJECTING, FoundryState.FAILED},
    FoundryState.PROJECTING: {FoundryState.CACHING, FoundryState.FAILED},
    FoundryState.CACHING: {FoundryState.IDLE, FoundryState.FAILED},
    FoundryState.FAILED: {FoundryState.IDLE},  # Can reset from failed
}


def can_transition(from_state: FoundryState, to_state: FoundryState) -> bool:
    """Check if a state transition is valid."""
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def get_valid_next_states(state: FoundryState) -> set[FoundryState]:
    """Get all valid next states from current state."""
    return VALID_TRANSITIONS.get(state, set())


@dataclass(frozen=True)
class FoundryTransition:
    """Record of a state transition."""

    from_state: FoundryState
    to_state: FoundryState
    event: FoundryEvent
    payload: dict[str, Any] | None = None


class FoundryStateMachine:
    """
    State machine for tracking Foundry pipeline progress.

    This is a simple state machine that tracks the current state
    and validates transitions. The actual work is done by the
    AgentFoundry orchestrator.
    """

    def __init__(self) -> None:
        self._state = FoundryState.IDLE
        self._history: list[FoundryTransition] = []

    @property
    def state(self) -> FoundryState:
        """Current state."""
        return self._state

    @property
    def history(self) -> list[FoundryTransition]:
        """Transition history."""
        return self._history.copy()

    def transition(
        self,
        to_state: FoundryState,
        event: FoundryEvent,
        payload: dict[str, Any] | None = None,
    ) -> bool:
        """
        Attempt to transition to a new state.

        Returns True if transition was successful, False if invalid.
        """
        if not can_transition(self._state, to_state):
            return False

        transition = FoundryTransition(
            from_state=self._state,
            to_state=to_state,
            event=event,
            payload=payload,
        )
        self._history.append(transition)
        self._state = to_state
        return True

    def reset(self) -> None:
        """Reset to IDLE state."""
        if self._state != FoundryState.IDLE:
            self._history.append(
                FoundryTransition(
                    from_state=self._state,
                    to_state=FoundryState.IDLE,
                    event=FoundryEvent.RESET,
                )
            )
        self._state = FoundryState.IDLE

    def fail(self, error: str) -> None:
        """Transition to FAILED state."""
        self._history.append(
            FoundryTransition(
                from_state=self._state,
                to_state=FoundryState.FAILED,
                event=FoundryEvent.ERROR,
                payload={"error": error},
            )
        )
        self._state = FoundryState.FAILED


# =============================================================================
# Polynomial Definition (AD-002 Pattern)
# =============================================================================


def _foundry_directions(state: FoundryState) -> FrozenSet[FoundryEvent]:
    """Valid inputs (events) for each state."""
    match state:
        case FoundryState.IDLE:
            return frozenset({FoundryEvent.START_FORGE})
        case FoundryState.CLASSIFYING:
            return frozenset({FoundryEvent.REALITY_CLASSIFIED, FoundryEvent.ERROR})
        case FoundryState.GENERATING:
            return frozenset({FoundryEvent.SOURCE_GENERATED, FoundryEvent.ERROR})
        case FoundryState.VALIDATING:
            return frozenset({FoundryEvent.STABILITY_CHECKED, FoundryEvent.ERROR})
        case FoundryState.SELECTING:
            return frozenset({FoundryEvent.TARGET_SELECTED, FoundryEvent.ERROR})
        case FoundryState.PROJECTING:
            return frozenset({FoundryEvent.PROJECTION_COMPLETE, FoundryEvent.ERROR})
        case FoundryState.CACHING:
            return frozenset({FoundryEvent.CACHED, FoundryEvent.ERROR})
        case FoundryState.FAILED:
            return frozenset({FoundryEvent.RESET})


@dataclass(frozen=True)
class FoundryPolynomial:
    """
    Polynomial functor for the Foundry.

    P(y) = Σ_{s ∈ positions} y^{directions(s)}

    This captures the mode-dependent behavior of the Foundry:
    different states accept different events (inputs).
    """

    positions: FrozenSet[FoundryState]
    directions: Callable[[FoundryState], FrozenSet[FoundryEvent]]

    def valid_inputs(self, state: FoundryState) -> FrozenSet[FoundryEvent]:
        """Get valid inputs for a state."""
        if state not in self.positions:
            return frozenset()
        return self.directions(state)


# The singleton polynomial for Foundry
FOUNDRY_POLYNOMIAL = FoundryPolynomial(
    positions=frozenset(FoundryState),
    directions=_foundry_directions,
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "FoundryState",
    "FoundryEvent",
    "FoundryTransition",
    "FoundryStateMachine",
    "FoundryPolynomial",
    "FOUNDRY_POLYNOMIAL",
    "can_transition",
    "get_valid_next_states",
    "VALID_TRANSITIONS",
]
