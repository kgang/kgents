"""
CitizenPolynomial: Citizen Behavior as State Machine.

The citizen polynomial models agent behavior as a dynamical system:
- IDLE: Ready for new interactions
- SOCIALIZING: Engaged in social activity
- WORKING: Performing solo work
- REFLECTING: Internal contemplation
- RESTING: Mandatory rest (Right to Rest)

The Insight (from Barad):
    Positions are not states but *interpretive frames*.
    The citizen does not "change state"—the observer makes a different agential cut.
    Each transition reconfigures the phenomenon, not the entity.

Example:
    >>> poly = CITIZEN_POLYNOMIAL
    >>> state, output = poly.invoke(CitizenPhase.IDLE, CitizenInput.greet())
    >>> print(state, output)
    CitizenPhase.SOCIALIZING GreetingOutput(...)

See: spec/town/metaphysics.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Citizen Phase (Positions in the Polynomial)
# =============================================================================


class CitizenPhase(Enum):
    """
    Positions in the citizen polynomial.

    These are interpretive frames, not internal states.
    The phase determines which interactions are valid (directions).

    From Barad: The transition is an agential cut, not a state change.
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
class SocializeInput:
    """Input for social interaction."""

    partner_id: str
    operation: str  # greet, gossip, trade, etc.
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WorkInput:
    """Input for solo work."""

    activity: str
    duration_minutes: int = 60


@dataclass(frozen=True)
class ReflectInput:
    """Input for reflection."""

    topic: str | None = None


@dataclass(frozen=True)
class RestInput:
    """Input for rest transition."""

    pass


@dataclass(frozen=True)
class WakeInput:
    """Input for waking from rest."""

    pass


class CitizenInput:
    """Factory for citizen inputs."""

    @staticmethod
    def greet(partner_id: str) -> SocializeInput:
        """Create a greet input."""
        return SocializeInput(partner_id=partner_id, operation="greet")

    @staticmethod
    def gossip(partner_id: str, topic: str) -> SocializeInput:
        """Create a gossip input."""
        return SocializeInput(
            partner_id=partner_id,
            operation="gossip",
            payload={"topic": topic},
        )

    @staticmethod
    def trade(partner_id: str, offer: Any, request: Any) -> SocializeInput:
        """Create a trade input."""
        return SocializeInput(
            partner_id=partner_id,
            operation="trade",
            payload={"offer": offer, "request": request},
        )

    @staticmethod
    def work(activity: str, duration_minutes: int = 60) -> WorkInput:
        """Create a work input."""
        return WorkInput(activity=activity, duration_minutes=duration_minutes)

    @staticmethod
    def reflect(topic: str | None = None) -> ReflectInput:
        """Create a reflect input."""
        return ReflectInput(topic=topic)

    @staticmethod
    def rest() -> RestInput:
        """Create a rest input."""
        return RestInput()

    @staticmethod
    def wake() -> WakeInput:
        """Create a wake input."""
        return WakeInput()


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class CitizenOutput:
    """Output from citizen transitions."""

    phase: CitizenPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def citizen_directions(phase: CitizenPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each citizen phase.

    This encodes the mode-dependent behavior:
    - IDLE: Can do anything except wake (already awake)
    - SOCIALIZING: Can continue socializing or exit
    - WORKING: Can continue working or exit
    - REFLECTING: Can continue reflecting or exit
    - RESTING: Can ONLY wake (Right to Rest - cannot be disturbed)
    """
    match phase:
        case CitizenPhase.IDLE:
            return frozenset(
                {SocializeInput, WorkInput, ReflectInput, RestInput, type, Any}
            )
        case CitizenPhase.SOCIALIZING:
            return frozenset({SocializeInput, RestInput, type, Any})
        case CitizenPhase.WORKING:
            return frozenset({WorkInput, RestInput, type, Any})
        case CitizenPhase.REFLECTING:
            return frozenset({ReflectInput, SocializeInput, RestInput, type, Any})
        case CitizenPhase.RESTING:
            # Right to Rest: ONLY wake is valid. No interruptions.
            return frozenset({WakeInput, type})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def citizen_transition(
    phase: CitizenPhase, input: Any
) -> tuple[CitizenPhase, CitizenOutput]:
    """
    Citizen state transition function.

    This is the polynomial core:
    transition: Phase × Input → (NewPhase, Output)

    From Barad: The transition reconfigures the phenomenon.
    The citizen doesn't change—our cut on them changes.
    """
    match phase:
        case CitizenPhase.IDLE:
            if isinstance(input, SocializeInput):
                return CitizenPhase.SOCIALIZING, CitizenOutput(
                    phase=CitizenPhase.SOCIALIZING,
                    success=True,
                    message=f"Began {input.operation} with {input.partner_id}",
                    metadata={
                        "partner": input.partner_id,
                        "operation": input.operation,
                    },
                )
            elif isinstance(input, WorkInput):
                return CitizenPhase.WORKING, CitizenOutput(
                    phase=CitizenPhase.WORKING,
                    success=True,
                    message=f"Started working on {input.activity}",
                    metadata={"activity": input.activity},
                )
            elif isinstance(input, ReflectInput):
                return CitizenPhase.REFLECTING, CitizenOutput(
                    phase=CitizenPhase.REFLECTING,
                    success=True,
                    message=f"Began reflecting on {input.topic or 'nothing in particular'}",
                    metadata={"topic": input.topic},
                )
            elif isinstance(input, RestInput):
                return CitizenPhase.RESTING, CitizenOutput(
                    phase=CitizenPhase.RESTING,
                    success=True,
                    message="Went to rest",
                )
            else:
                return CitizenPhase.IDLE, CitizenOutput(
                    phase=CitizenPhase.IDLE,
                    success=False,
                    message=f"Unknown input type: {type(input).__name__}",
                )

        case CitizenPhase.SOCIALIZING:
            if isinstance(input, SocializeInput):
                # Continue socializing
                return CitizenPhase.SOCIALIZING, CitizenOutput(
                    phase=CitizenPhase.SOCIALIZING,
                    success=True,
                    message=f"Continued {input.operation} with {input.partner_id}",
                    metadata={
                        "partner": input.partner_id,
                        "operation": input.operation,
                    },
                )
            elif isinstance(input, RestInput):
                return CitizenPhase.RESTING, CitizenOutput(
                    phase=CitizenPhase.RESTING,
                    success=True,
                    message="Finished socializing and went to rest",
                )
            else:
                # Exit to IDLE
                return CitizenPhase.IDLE, CitizenOutput(
                    phase=CitizenPhase.IDLE,
                    success=True,
                    message="Finished socializing",
                )

        case CitizenPhase.WORKING:
            if isinstance(input, WorkInput):
                # Continue working
                return CitizenPhase.WORKING, CitizenOutput(
                    phase=CitizenPhase.WORKING,
                    success=True,
                    message=f"Continued working on {input.activity}",
                    metadata={"activity": input.activity},
                )
            elif isinstance(input, RestInput):
                return CitizenPhase.RESTING, CitizenOutput(
                    phase=CitizenPhase.RESTING,
                    success=True,
                    message="Finished working and went to rest",
                )
            else:
                # Exit to IDLE
                return CitizenPhase.IDLE, CitizenOutput(
                    phase=CitizenPhase.IDLE,
                    success=True,
                    message="Finished working",
                )

        case CitizenPhase.REFLECTING:
            if isinstance(input, ReflectInput):
                # Continue reflecting
                return CitizenPhase.REFLECTING, CitizenOutput(
                    phase=CitizenPhase.REFLECTING,
                    success=True,
                    message=f"Continued reflecting on {input.topic or 'existence'}",
                    metadata={"topic": input.topic},
                )
            elif isinstance(input, SocializeInput):
                # Exit reflection for social interaction
                return CitizenPhase.SOCIALIZING, CitizenOutput(
                    phase=CitizenPhase.SOCIALIZING,
                    success=True,
                    message=f"Interrupted reflection to {input.operation} with {input.partner_id}",
                    metadata={
                        "partner": input.partner_id,
                        "operation": input.operation,
                    },
                )
            elif isinstance(input, RestInput):
                return CitizenPhase.RESTING, CitizenOutput(
                    phase=CitizenPhase.RESTING,
                    success=True,
                    message="Finished reflecting and went to rest",
                )
            else:
                # Exit to IDLE
                return CitizenPhase.IDLE, CitizenOutput(
                    phase=CitizenPhase.IDLE,
                    success=True,
                    message="Finished reflecting",
                )

        case CitizenPhase.RESTING:
            # RIGHT TO REST: Only wake is valid
            if isinstance(input, WakeInput):
                return CitizenPhase.IDLE, CitizenOutput(
                    phase=CitizenPhase.IDLE,
                    success=True,
                    message="Woke from rest",
                )
            else:
                # Reject all other inputs
                return CitizenPhase.RESTING, CitizenOutput(
                    phase=CitizenPhase.RESTING,
                    success=False,
                    message="Cannot be disturbed while resting (Right to Rest)",
                )

        case _:
            return CitizenPhase.IDLE, CitizenOutput(
                phase=CitizenPhase.IDLE,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


CITIZEN_POLYNOMIAL: PolyAgent[CitizenPhase, Any, CitizenOutput] = PolyAgent(
    name="CitizenPolynomial",
    positions=frozenset(CitizenPhase),
    _directions=citizen_directions,
    _transition=citizen_transition,
)
"""
The Citizen polynomial agent.

This models citizen behavior as a polynomial state machine:
- positions: 5 phases (IDLE, SOCIALIZING, WORKING, REFLECTING, RESTING)
- directions: phase-dependent valid inputs
- transition: behavioral transitions

Key Property:
    Right to Rest: Citizens in RESTING phase cannot be disturbed.
    Only WakeInput is valid during RESTING.
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "CitizenPhase",
    # Inputs
    "SocializeInput",
    "WorkInput",
    "ReflectInput",
    "RestInput",
    "WakeInput",
    "CitizenInput",
    # Output
    "CitizenOutput",
    # Functions
    "citizen_directions",
    "citizen_transition",
    # Polynomial
    "CITIZEN_POLYNOMIAL",
]
