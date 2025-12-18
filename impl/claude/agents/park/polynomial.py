"""
DirectorPolynomial: Director Behavior as State Machine.

The director polynomial models the Punchdrunk Park director's behavior
as a dynamical system for serendipity injection:

- OBSERVING: Watching session metrics passively
- BUILDING: Building tension toward potential injection
- INJECTING: Executing serendipity injection
- COOLING: Post-injection cooldown period
- INTERVENING: Special difficulty adjustment (atomic)

The Insight (from Punchdrunk):
    The director is invisible—the guest should never feel directed.
    Serendipity appears as "lucky coincidence," not orchestration.
    Each injection maintains the magic circle of the experience.

Example:
    >>> poly = DIRECTOR_POLYNOMIAL
    >>> state, output = poly.invoke(DirectorPhase.OBSERVING, ObserveInput(...))
    >>> print(state, output)
    DirectorPhase.BUILDING TensionOutput(...)

See: plans/core-apps/punchdrunk-park.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Director Phase (Positions in the Polynomial)
# =============================================================================


class DirectorPhase(Enum):
    """
    Positions in the director polynomial.

    These are operational modes, not internal states.
    The phase determines which operations are valid (directions).

    From Punchdrunk: The director orchestrates without being seen.
    Each phase has different capabilities and constraints.
    """

    OBSERVING = auto()  # Passive monitoring
    BUILDING = auto()  # Building tension
    INJECTING = auto()  # Executing injection
    COOLING = auto()  # Post-injection cooldown
    INTERVENING = auto()  # Special adjustment (atomic)


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class ObserveInput:
    """Input for observation."""

    session_id: str
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BuildTensionInput:
    """Input for building tension."""

    target_level: float = 0.7
    reason: str = ""


@dataclass(frozen=True)
class InjectInput:
    """Input for serendipity injection."""

    injection_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    intensity: float = 0.5


@dataclass(frozen=True)
class CooldownInput:
    """Input for cooldown period."""

    duration_seconds: int = 300
    reason: str = "post_injection"


@dataclass(frozen=True)
class InterveneInput:
    """Input for difficulty intervention."""

    adjustment_type: str  # "easier" or "harder"
    magnitude: float = 0.3
    reason: str = ""


@dataclass(frozen=True)
class AbortInput:
    """Input for aborting current operation."""

    reason: str = "user_request"


@dataclass(frozen=True)
class ResetInput:
    """Input for resetting to observing."""

    pass


class DirectorInput:
    """Factory for director inputs."""

    @staticmethod
    def observe(session_id: str, **metrics: Any) -> ObserveInput:
        """Create an observation input."""
        return ObserveInput(session_id=session_id, metrics=metrics)

    @staticmethod
    def build(target_level: float = 0.7, reason: str = "") -> BuildTensionInput:
        """Create a tension building input."""
        return BuildTensionInput(target_level=target_level, reason=reason)

    @staticmethod
    def inject(
        injection_type: str,
        intensity: float = 0.5,
        **payload: Any,
    ) -> InjectInput:
        """Create an injection input."""
        return InjectInput(
            injection_type=injection_type,
            intensity=intensity,
            payload=payload,
        )

    @staticmethod
    def cooldown(duration_seconds: int = 300, reason: str = "") -> CooldownInput:
        """Create a cooldown input."""
        return CooldownInput(duration_seconds=duration_seconds, reason=reason)

    @staticmethod
    def intervene(
        adjustment_type: str,
        magnitude: float = 0.3,
        reason: str = "",
    ) -> InterveneInput:
        """Create an intervention input."""
        return InterveneInput(
            adjustment_type=adjustment_type,
            magnitude=magnitude,
            reason=reason,
        )

    @staticmethod
    def abort(reason: str = "user_request") -> AbortInput:
        """Create an abort input."""
        return AbortInput(reason=reason)

    @staticmethod
    def reset() -> ResetInput:
        """Create a reset input."""
        return ResetInput()


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class DirectorOutput:
    """Output from director transitions."""

    phase: DirectorPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ObserveOutput(DirectorOutput):
    """Output from observation."""

    tension_level: float = 0.0
    consent_debt: float = 0.0
    injection_opportunity: bool = False


@dataclass
class InjectionOutput(DirectorOutput):
    """Output from injection."""

    injection_id: str | None = None
    delivered: bool = False


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def director_directions(phase: DirectorPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each director phase.

    This encodes the mode-dependent behavior:
    - OBSERVING: Can observe, build tension, or intervene
    - BUILDING: Can continue building, inject, or abort
    - INJECTING: Can only complete injection
    - COOLING: Can wait or reset
    - INTERVENING: Can only complete or abort (atomic)
    """
    match phase:
        case DirectorPhase.OBSERVING:
            return frozenset(
                {ObserveInput, BuildTensionInput, InterveneInput, type, Any}
            )
        case DirectorPhase.BUILDING:
            return frozenset(
                {BuildTensionInput, InjectInput, AbortInput, ObserveInput, type, Any}
            )
        case DirectorPhase.INJECTING:
            return frozenset({CooldownInput, AbortInput, type, Any})
        case DirectorPhase.COOLING:
            return frozenset({CooldownInput, ResetInput, type, Any})
        case DirectorPhase.INTERVENING:
            return frozenset({ResetInput, AbortInput, type, Any})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def director_transition(
    phase: DirectorPhase, input: Any
) -> tuple[DirectorPhase, DirectorOutput]:
    """
    Director state transition function.

    This is the polynomial core:
    transition: Phase x Input -> (NewPhase, Output)

    From Punchdrunk: Every transition maintains the magic circle.
    The guest experiences serendipity, not direction.
    """
    match phase:
        case DirectorPhase.OBSERVING:
            if isinstance(input, ObserveInput):
                # Continue observing, possibly detect opportunity
                return DirectorPhase.OBSERVING, ObserveOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message=f"Observing session {input.session_id}",
                    metadata={"session_id": input.session_id, "metrics": input.metrics},
                )
            elif isinstance(input, BuildTensionInput):
                return DirectorPhase.BUILDING, DirectorOutput(
                    phase=DirectorPhase.BUILDING,
                    success=True,
                    message=f"Building tension to {input.target_level}",
                    metadata={
                        "target_level": input.target_level,
                        "reason": input.reason,
                    },
                )
            elif isinstance(input, InterveneInput):
                return DirectorPhase.INTERVENING, DirectorOutput(
                    phase=DirectorPhase.INTERVENING,
                    success=True,
                    message=f"Intervening: {input.adjustment_type}",
                    metadata={
                        "adjustment_type": input.adjustment_type,
                        "magnitude": input.magnitude,
                    },
                )
            else:
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=False,
                    message=f"Invalid input for OBSERVING: {type(input).__name__}",
                )

        case DirectorPhase.BUILDING:
            if isinstance(input, BuildTensionInput):
                return DirectorPhase.BUILDING, DirectorOutput(
                    phase=DirectorPhase.BUILDING,
                    success=True,
                    message="Continuing tension build",
                    metadata={"target_level": input.target_level},
                )
            elif isinstance(input, InjectInput):
                return DirectorPhase.INJECTING, InjectionOutput(
                    phase=DirectorPhase.INJECTING,
                    success=True,
                    message=f"Injecting: {input.injection_type}",
                    metadata={
                        "injection_type": input.injection_type,
                        "intensity": input.intensity,
                    },
                )
            elif isinstance(input, (AbortInput, ObserveInput)):
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message="Returning to observation",
                )
            else:
                return DirectorPhase.BUILDING, DirectorOutput(
                    phase=DirectorPhase.BUILDING,
                    success=False,
                    message=f"Invalid input for BUILDING: {type(input).__name__}",
                )

        case DirectorPhase.INJECTING:
            if isinstance(input, CooldownInput):
                return DirectorPhase.COOLING, DirectorOutput(
                    phase=DirectorPhase.COOLING,
                    success=True,
                    message=f"Entering cooldown for {input.duration_seconds}s",
                    metadata={"duration": input.duration_seconds},
                )
            elif isinstance(input, AbortInput):
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message=f"Injection aborted: {input.reason}",
                )
            else:
                return DirectorPhase.INJECTING, DirectorOutput(
                    phase=DirectorPhase.INJECTING,
                    success=False,
                    message=f"Invalid input for INJECTING: {type(input).__name__}",
                )

        case DirectorPhase.COOLING:
            if isinstance(input, CooldownInput):
                return DirectorPhase.COOLING, DirectorOutput(
                    phase=DirectorPhase.COOLING,
                    success=True,
                    message="Continuing cooldown",
                )
            elif isinstance(input, ResetInput):
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message="Cooldown complete, returning to observation",
                )
            else:
                return DirectorPhase.COOLING, DirectorOutput(
                    phase=DirectorPhase.COOLING,
                    success=False,
                    message=f"Invalid input for COOLING: {type(input).__name__}",
                )

        case DirectorPhase.INTERVENING:
            if isinstance(input, ResetInput):
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message="Intervention complete",
                )
            elif isinstance(input, AbortInput):
                return DirectorPhase.OBSERVING, DirectorOutput(
                    phase=DirectorPhase.OBSERVING,
                    success=True,
                    message=f"Intervention aborted: {input.reason}",
                )
            else:
                return DirectorPhase.INTERVENING, DirectorOutput(
                    phase=DirectorPhase.INTERVENING,
                    success=False,
                    message=f"Invalid input for INTERVENING: {type(input).__name__}",
                )

        case _:
            return DirectorPhase.OBSERVING, DirectorOutput(
                phase=DirectorPhase.OBSERVING,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


DIRECTOR_POLYNOMIAL: PolyAgent[DirectorPhase, Any, DirectorOutput] = PolyAgent(
    name="DirectorPolynomial",
    positions=frozenset(DirectorPhase),
    _directions=director_directions,
    _transition=director_transition,
)
"""
The Director polynomial agent.

This models Punchdrunk Park director behavior as a polynomial state machine:
- positions: 5 phases (OBSERVING, BUILDING, INJECTING, COOLING, INTERVENING)
- directions: phase-dependent valid inputs
- transition: behavioral transitions

Key Property:
    The director is invisible. All actions feel like serendipity to guests.
    The magic circle must never be broken.
"""

# Alias for Park naming consistency
PARK_POLYNOMIAL = DIRECTOR_POLYNOMIAL


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "DirectorPhase",
    # Inputs
    "ObserveInput",
    "BuildTensionInput",
    "InjectInput",
    "CooldownInput",
    "InterveneInput",
    "AbortInput",
    "ResetInput",
    "DirectorInput",
    # Outputs
    "DirectorOutput",
    "ObserveOutput",
    "InjectionOutput",
    # Functions
    "director_directions",
    "director_transition",
    # Polynomial
    "DIRECTOR_POLYNOMIAL",
    "PARK_POLYNOMIAL",
]
