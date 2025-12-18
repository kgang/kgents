"""
AtelierPolynomial: Workshop Lifecycle as State Machine.

The atelier polynomial models workshop behavior as a dynamical system:
- GATHERING: Workshop setup, artisans joining
- CREATING: Active creative work in progress
- REVIEWING: Work being reviewed/refined
- EXHIBITING: Exhibition open for viewing
- CLOSED: Workshop archived (terminal state)

The Insight (from Punchdrunk):
    The workshop is a fishbowl—spectators observe the creative process.
    Each phase has different valid operations for artisans and observers.
    The polynomial captures who can do what, when.

Example:
    >>> poly = WORKSHOP_POLYNOMIAL
    >>> state, output = poly.invoke(WorkshopPhase.GATHERING, JoinInput(...))
    >>> print(state, output)
    WorkshopPhase.GATHERING JoinOutput(...)

See: spec/atelier/fishbowl.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Workshop Phase (Positions in the Polynomial)
# =============================================================================


class WorkshopPhase(Enum):
    """
    Positions in the workshop polynomial.

    These are lifecycle stages, not internal states.
    The phase determines which operations are valid (directions).

    From Punchdrunk: The workshop is a performative space.
    Each phase has different dramaturgy.
    """

    GATHERING = auto()  # Setup, artisans joining
    CREATING = auto()  # Active creative work
    REVIEWING = auto()  # Refinement phase
    EXHIBITING = auto()  # Exhibition open
    CLOSED = auto()  # Terminal state


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class CreateWorkshopInput:
    """Input for creating a workshop."""

    name: str
    description: str | None = None
    theme: str | None = None


@dataclass(frozen=True)
class JoinInput:
    """Input for artisan joining."""

    artisan_name: str
    specialty: str
    style: str | None = None


@dataclass(frozen=True)
class ContributeInput:
    """Input for creative contribution."""

    artisan_id: str
    content: str
    content_type: str = "text"
    contribution_type: str = "draft"
    prompt: str | None = None


@dataclass(frozen=True)
class RefineInput:
    """Input for refining a contribution."""

    contribution_id: str
    refined_content: str
    refiner_id: str


@dataclass(frozen=True)
class StartExhibitionInput:
    """Input for starting exhibition."""

    name: str
    description: str | None = None
    curator_notes: str | None = None


@dataclass(frozen=True)
class OpenExhibitionInput:
    """Input for opening exhibition to public."""

    exhibition_id: str


@dataclass(frozen=True)
class ViewInput:
    """Input for viewing exhibition."""

    exhibition_id: str


@dataclass(frozen=True)
class CloseInput:
    """Input for closing the workshop."""

    reason: str = "completed"


class WorkshopInput:
    """Factory for workshop inputs."""

    @staticmethod
    def create(
        name: str,
        description: str | None = None,
        theme: str | None = None,
    ) -> CreateWorkshopInput:
        """Create a workshop creation input."""
        return CreateWorkshopInput(name=name, description=description, theme=theme)

    @staticmethod
    def join(
        artisan_name: str,
        specialty: str,
        style: str | None = None,
    ) -> JoinInput:
        """Create a join input."""
        return JoinInput(artisan_name=artisan_name, specialty=specialty, style=style)

    @staticmethod
    def contribute(
        artisan_id: str,
        content: str,
        content_type: str = "text",
        contribution_type: str = "draft",
    ) -> ContributeInput:
        """Create a contribution input."""
        return ContributeInput(
            artisan_id=artisan_id,
            content=content,
            content_type=content_type,
            contribution_type=contribution_type,
        )

    @staticmethod
    def refine(
        contribution_id: str,
        refined_content: str,
        refiner_id: str,
    ) -> RefineInput:
        """Create a refine input."""
        return RefineInput(
            contribution_id=contribution_id,
            refined_content=refined_content,
            refiner_id=refiner_id,
        )

    @staticmethod
    def exhibit(name: str, description: str | None = None) -> StartExhibitionInput:
        """Create an exhibition start input."""
        return StartExhibitionInput(name=name, description=description)

    @staticmethod
    def open(exhibition_id: str) -> OpenExhibitionInput:
        """Create an exhibition open input."""
        return OpenExhibitionInput(exhibition_id=exhibition_id)

    @staticmethod
    def view(exhibition_id: str) -> ViewInput:
        """Create a view input."""
        return ViewInput(exhibition_id=exhibition_id)

    @staticmethod
    def close(reason: str = "completed") -> CloseInput:
        """Create a close input."""
        return CloseInput(reason=reason)


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class WorkshopOutput:
    """Output from workshop transitions."""

    phase: WorkshopPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class JoinOutput(WorkshopOutput):
    """Output from artisan join."""

    artisan_id: str | None = None


@dataclass
class ContributeOutput(WorkshopOutput):
    """Output from contribution."""

    contribution_id: str | None = None


@dataclass
class ExhibitOutput(WorkshopOutput):
    """Output from exhibition operations."""

    exhibition_id: str | None = None
    is_open: bool = False


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def workshop_directions(phase: WorkshopPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each workshop phase.

    This encodes the mode-dependent behavior:
    - GATHERING: Join, Contribute (warm-up), move to CREATING
    - CREATING: Contribute, Refine, move to REVIEWING/EXHIBITING
    - REVIEWING: Refine, move to EXHIBITING/CREATING
    - EXHIBITING: View, Close
    - CLOSED: Nothing (terminal)
    """
    match phase:
        case WorkshopPhase.GATHERING:
            return frozenset({JoinInput, ContributeInput, type, Any})
        case WorkshopPhase.CREATING:
            return frozenset(
                {ContributeInput, RefineInput, StartExhibitionInput, type, Any}
            )
        case WorkshopPhase.REVIEWING:
            return frozenset(
                {RefineInput, ContributeInput, StartExhibitionInput, type, Any}
            )
        case WorkshopPhase.EXHIBITING:
            return frozenset({ViewInput, OpenExhibitionInput, CloseInput, type, Any})
        case WorkshopPhase.CLOSED:
            # Terminal state - no valid inputs
            return frozenset({type})
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def workshop_transition(
    phase: WorkshopPhase, input: Any
) -> tuple[WorkshopPhase, WorkshopOutput]:
    """
    Workshop state transition function.

    This is the polynomial core:
    transition: Phase × Input → (NewPhase, Output)

    From Punchdrunk: The workshop evolves through creative phases.
    Each transition is a dramaturgical beat.
    """
    match phase:
        case WorkshopPhase.GATHERING:
            if isinstance(input, JoinInput):
                return WorkshopPhase.GATHERING, JoinOutput(
                    phase=WorkshopPhase.GATHERING,
                    success=True,
                    message=f"{input.artisan_name} joined as {input.specialty}",
                    metadata={
                        "artisan_name": input.artisan_name,
                        "specialty": input.specialty,
                        "style": input.style,
                    },
                )
            elif isinstance(input, ContributeInput):
                # First contribution moves to CREATING
                return WorkshopPhase.CREATING, ContributeOutput(
                    phase=WorkshopPhase.CREATING,
                    success=True,
                    message="First contribution submitted, workshop now creating",
                    metadata={
                        "artisan_id": input.artisan_id,
                        "contribution_type": input.contribution_type,
                    },
                )
            else:
                return WorkshopPhase.GATHERING, WorkshopOutput(
                    phase=WorkshopPhase.GATHERING,
                    success=False,
                    message=f"Invalid input for GATHERING: {type(input).__name__}",
                )

        case WorkshopPhase.CREATING:
            if isinstance(input, ContributeInput):
                return WorkshopPhase.CREATING, ContributeOutput(
                    phase=WorkshopPhase.CREATING,
                    success=True,
                    message="Contribution submitted",
                    metadata={
                        "artisan_id": input.artisan_id,
                        "content_type": input.content_type,
                    },
                )
            elif isinstance(input, RefineInput):
                # Refinement moves to REVIEWING
                return WorkshopPhase.REVIEWING, WorkshopOutput(
                    phase=WorkshopPhase.REVIEWING,
                    success=True,
                    message="Entering review phase",
                    metadata={
                        "contribution_id": input.contribution_id,
                        "refiner_id": input.refiner_id,
                    },
                )
            elif isinstance(input, StartExhibitionInput):
                return WorkshopPhase.EXHIBITING, ExhibitOutput(
                    phase=WorkshopPhase.EXHIBITING,
                    success=True,
                    message=f"Exhibition '{input.name}' created",
                    metadata={
                        "exhibition_name": input.name,
                        "description": input.description,
                    },
                )
            else:
                return WorkshopPhase.CREATING, WorkshopOutput(
                    phase=WorkshopPhase.CREATING,
                    success=False,
                    message=f"Invalid input for CREATING: {type(input).__name__}",
                )

        case WorkshopPhase.REVIEWING:
            if isinstance(input, RefineInput):
                return WorkshopPhase.REVIEWING, WorkshopOutput(
                    phase=WorkshopPhase.REVIEWING,
                    success=True,
                    message="Refinement applied",
                    metadata={
                        "contribution_id": input.contribution_id,
                        "refiner_id": input.refiner_id,
                    },
                )
            elif isinstance(input, ContributeInput):
                # New contribution returns to CREATING
                return WorkshopPhase.CREATING, ContributeOutput(
                    phase=WorkshopPhase.CREATING,
                    success=True,
                    message="New contribution, returning to creating",
                    metadata={"artisan_id": input.artisan_id},
                )
            elif isinstance(input, StartExhibitionInput):
                return WorkshopPhase.EXHIBITING, ExhibitOutput(
                    phase=WorkshopPhase.EXHIBITING,
                    success=True,
                    message=f"Exhibition '{input.name}' created after review",
                    metadata={"exhibition_name": input.name},
                )
            else:
                return WorkshopPhase.REVIEWING, WorkshopOutput(
                    phase=WorkshopPhase.REVIEWING,
                    success=False,
                    message=f"Invalid input for REVIEWING: {type(input).__name__}",
                )

        case WorkshopPhase.EXHIBITING:
            if isinstance(input, ViewInput):
                return WorkshopPhase.EXHIBITING, WorkshopOutput(
                    phase=WorkshopPhase.EXHIBITING,
                    success=True,
                    message="Exhibition viewed",
                    metadata={"exhibition_id": input.exhibition_id},
                )
            elif isinstance(input, OpenExhibitionInput):
                return WorkshopPhase.EXHIBITING, ExhibitOutput(
                    phase=WorkshopPhase.EXHIBITING,
                    success=True,
                    message="Exhibition opened to public",
                    is_open=True,
                    metadata={"exhibition_id": input.exhibition_id},
                )
            elif isinstance(input, CloseInput):
                return WorkshopPhase.CLOSED, WorkshopOutput(
                    phase=WorkshopPhase.CLOSED,
                    success=True,
                    message=f"Workshop closed: {input.reason}",
                    metadata={"reason": input.reason},
                )
            else:
                return WorkshopPhase.EXHIBITING, WorkshopOutput(
                    phase=WorkshopPhase.EXHIBITING,
                    success=False,
                    message=f"Invalid input for EXHIBITING: {type(input).__name__}",
                )

        case WorkshopPhase.CLOSED:
            # Terminal state - reject all inputs
            return WorkshopPhase.CLOSED, WorkshopOutput(
                phase=WorkshopPhase.CLOSED,
                success=False,
                message="Workshop is closed, no further operations allowed",
            )

        case _:
            return WorkshopPhase.GATHERING, WorkshopOutput(
                phase=WorkshopPhase.GATHERING,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


WORKSHOP_POLYNOMIAL: PolyAgent[WorkshopPhase, Any, WorkshopOutput] = PolyAgent(
    name="WorkshopPolynomial",
    positions=frozenset(WorkshopPhase),
    _directions=workshop_directions,
    _transition=workshop_transition,
)
"""
The Workshop polynomial agent.

This models workshop behavior as a polynomial state machine:
- positions: 5 phases (GATHERING, CREATING, REVIEWING, EXHIBITING, CLOSED)
- directions: phase-dependent valid inputs
- transition: lifecycle transitions

Key Property:
    CLOSED is terminal: once closed, a workshop cannot reopen.
    This is intentional—workshops are ephemeral creative spaces.
"""

# Alias for backward compatibility
ATELIER_POLYNOMIAL = WORKSHOP_POLYNOMIAL


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "WorkshopPhase",
    # Inputs
    "CreateWorkshopInput",
    "JoinInput",
    "ContributeInput",
    "RefineInput",
    "StartExhibitionInput",
    "OpenExhibitionInput",
    "ViewInput",
    "CloseInput",
    "WorkshopInput",
    # Outputs
    "WorkshopOutput",
    "JoinOutput",
    "ContributeOutput",
    "ExhibitOutput",
    # Functions
    "workshop_directions",
    "workshop_transition",
    # Polynomial
    "WORKSHOP_POLYNOMIAL",
    "ATELIER_POLYNOMIAL",
]
