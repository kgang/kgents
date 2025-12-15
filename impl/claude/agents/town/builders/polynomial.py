"""
BuilderPolynomial: Builder Behavior as State Machine.

The builder polynomial models software development behavior as a dynamical system:
- IDLE: Ready for new tasks
- EXPLORING: Research and discovery (Scout's specialty)
- DESIGNING: System architecture (Sage's specialty)
- PROTOTYPING: Rapid experimentation (Spark's specialty)
- REFINING: Polishing and testing (Steady's specialty)
- INTEGRATING: Coordination and handoffs (Sync's specialty)

The Insight (from the Workshop):
    Builders are not just workers—they are interpretive frames.
    Each phase represents a different mode of creative engagement.
    Transitions reconfigure the phenomenon of "software development."

Example:
    >>> poly = BUILDER_POLYNOMIAL
    >>> state, output = poly.invoke(BuilderPhase.IDLE, BuilderInput.assign("add auth"))
    >>> print(state, output)
    BuilderPhase.EXPLORING TaskOutput(...)

See: plans/agent-town/builders-workshop.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Builder Phase (Positions in the Polynomial)
# =============================================================================


class BuilderPhase(Enum):
    """
    Positions in the builder polynomial.

    These are interpretive frames for software development work.
    Each phase has distinct affordances and valid inputs.

    Mapping to archetypes:
    - EXPLORING: Scout (researcher)
    - DESIGNING: Sage (architect)
    - PROTOTYPING: Spark (experimenter)
    - REFINING: Steady (craftsperson)
    - INTEGRATING: Sync (coordinator)
    """

    IDLE = auto()
    EXPLORING = auto()  # Scout's specialty
    DESIGNING = auto()  # Sage's specialty
    PROTOTYPING = auto()  # Spark's specialty
    REFINING = auto()  # Steady's specialty
    INTEGRATING = auto()  # Sync's specialty


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class TaskAssignInput:
    """Input for assigning a new task."""

    task: str
    context: dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1=low, 2=medium, 3=high


@dataclass(frozen=True)
class HandoffInput:
    """Input for handing work to another builder."""

    from_builder: str
    to_builder: str
    artifact: Any = None
    message: str = ""


@dataclass(frozen=True)
class ContinueInput:
    """Input for continuing current work."""

    note: str | None = None


@dataclass(frozen=True)
class CompleteInput:
    """Input for marking work complete."""

    artifact: Any = None
    summary: str = ""


@dataclass(frozen=True)
class UserQueryInput:
    """Input for querying the user."""

    question: str


@dataclass(frozen=True)
class UserResponseInput:
    """Input representing a user's response to a query."""

    response: str


@dataclass(frozen=True)
class RestInput:
    """Input for builder rest (Right to Rest applies)."""

    pass


@dataclass(frozen=True)
class WakeInput:
    """Input for waking from rest."""

    pass


class BuilderInput:
    """Factory for builder inputs."""

    @staticmethod
    def assign(task: str, priority: int = 1, **context: Any) -> TaskAssignInput:
        """Create a task assignment input."""
        return TaskAssignInput(task=task, priority=priority, context=context)

    @staticmethod
    def handoff(
        from_builder: str,
        to_builder: str,
        artifact: Any = None,
        message: str = "",
    ) -> HandoffInput:
        """Create a handoff input."""
        return HandoffInput(
            from_builder=from_builder,
            to_builder=to_builder,
            artifact=artifact,
            message=message,
        )

    @staticmethod
    def continue_work(note: str | None = None) -> ContinueInput:
        """Create a continue input."""
        return ContinueInput(note=note)

    @staticmethod
    def complete(artifact: Any = None, summary: str = "") -> CompleteInput:
        """Create a complete input."""
        return CompleteInput(artifact=artifact, summary=summary)

    @staticmethod
    def query_user(question: str) -> UserQueryInput:
        """Create a user query input."""
        return UserQueryInput(question=question)

    @staticmethod
    def user_response(response: str) -> UserResponseInput:
        """Create a user response input."""
        return UserResponseInput(response=response)

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
class BuilderOutput:
    """Output from builder transitions."""

    phase: BuilderPhase
    success: bool
    message: str = ""
    artifact: Any = None
    next_builder: str | None = None  # Suggested next builder for handoff
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Archetype Mapping
# =============================================================================

# Maps phases to their specialist archetypes
PHASE_ARCHETYPE_MAP: dict[BuilderPhase, str] = {
    BuilderPhase.IDLE: "any",
    BuilderPhase.EXPLORING: "Scout",
    BuilderPhase.DESIGNING: "Sage",
    BuilderPhase.PROTOTYPING: "Spark",
    BuilderPhase.REFINING: "Steady",
    BuilderPhase.INTEGRATING: "Sync",
}

# Natural flow: the typical handoff chain
NATURAL_FLOW: list[BuilderPhase] = [
    BuilderPhase.EXPLORING,  # Scout researches
    BuilderPhase.DESIGNING,  # Sage architects
    BuilderPhase.PROTOTYPING,  # Spark experiments
    BuilderPhase.REFINING,  # Steady polishes
    BuilderPhase.INTEGRATING,  # Sync coordinates
]


def get_next_phase(current: BuilderPhase) -> BuilderPhase:
    """Get the next phase in the natural flow."""
    if current == BuilderPhase.IDLE:
        return BuilderPhase.EXPLORING
    try:
        idx = NATURAL_FLOW.index(current)
        if idx < len(NATURAL_FLOW) - 1:
            return NATURAL_FLOW[idx + 1]
        return BuilderPhase.IDLE  # End of flow
    except ValueError:
        return BuilderPhase.IDLE


def get_specialist(phase: BuilderPhase) -> str:
    """Get the specialist archetype for a phase."""
    return PHASE_ARCHETYPE_MAP.get(phase, "any")


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def builder_directions(phase: BuilderPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each builder phase.

    This encodes the mode-dependent behavior:
    - IDLE: Can accept tasks or wake; cannot rest (already idle)
    - Work phases: Can continue, complete, handoff, query user, or rest
    - No phase can be forcibly interrupted (graceful transitions only)
    """
    match phase:
        case BuilderPhase.IDLE:
            return frozenset(
                {TaskAssignInput, HandoffInput, WakeInput, type, Any}
            )
        case BuilderPhase.EXPLORING:
            return frozenset(
                {
                    ContinueInput,
                    CompleteInput,
                    HandoffInput,
                    UserQueryInput,
                    UserResponseInput,
                    RestInput,
                    type,
                    Any,
                }
            )
        case BuilderPhase.DESIGNING:
            return frozenset(
                {
                    ContinueInput,
                    CompleteInput,
                    HandoffInput,
                    UserQueryInput,
                    UserResponseInput,
                    RestInput,
                    type,
                    Any,
                }
            )
        case BuilderPhase.PROTOTYPING:
            return frozenset(
                {
                    ContinueInput,
                    CompleteInput,
                    HandoffInput,
                    UserQueryInput,
                    UserResponseInput,
                    RestInput,
                    type,
                    Any,
                }
            )
        case BuilderPhase.REFINING:
            return frozenset(
                {
                    ContinueInput,
                    CompleteInput,
                    HandoffInput,
                    UserQueryInput,
                    UserResponseInput,
                    RestInput,
                    type,
                    Any,
                }
            )
        case BuilderPhase.INTEGRATING:
            return frozenset(
                {
                    ContinueInput,
                    CompleteInput,
                    HandoffInput,
                    UserQueryInput,
                    UserResponseInput,
                    RestInput,
                    type,
                    Any,
                }
            )
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def builder_transition(
    phase: BuilderPhase, input: Any
) -> tuple[BuilderPhase, BuilderOutput]:
    """
    Builder state transition function.

    This is the polynomial core:
    transition: Phase × Input → (NewPhase, Output)

    Key transitions:
    - IDLE + TaskAssignInput → EXPLORING (Scout takes first look)
    - Any work phase + CompleteInput → IDLE (done)
    - Any work phase + HandoffInput → Target phase
    - Any work phase + RestInput → IDLE (graceful exit)
    """
    match phase:
        case BuilderPhase.IDLE:
            if isinstance(input, TaskAssignInput):
                # New task → start exploring
                return BuilderPhase.EXPLORING, BuilderOutput(
                    phase=BuilderPhase.EXPLORING,
                    success=True,
                    message=f"Started exploring: {input.task}",
                    next_builder="Scout",
                    metadata={
                        "task": input.task,
                        "priority": input.priority,
                        "context": input.context,
                    },
                )
            elif isinstance(input, HandoffInput):
                # Direct handoff to specific phase
                target_phase = _archetype_to_phase(input.to_builder)
                return target_phase, BuilderOutput(
                    phase=target_phase,
                    success=True,
                    message=f"Handoff from {input.from_builder} to {input.to_builder}",
                    artifact=input.artifact,
                    next_builder=input.to_builder,
                    metadata={"handoff_message": input.message},
                )
            elif isinstance(input, WakeInput):
                return BuilderPhase.IDLE, BuilderOutput(
                    phase=BuilderPhase.IDLE,
                    success=True,
                    message="Already idle",
                )
            else:
                return BuilderPhase.IDLE, BuilderOutput(
                    phase=BuilderPhase.IDLE,
                    success=False,
                    message=f"Cannot process {type(input).__name__} while IDLE",
                )

        case BuilderPhase.EXPLORING:
            return _handle_work_phase(
                phase, input, "Scout", BuilderPhase.DESIGNING, "Sage"
            )

        case BuilderPhase.DESIGNING:
            return _handle_work_phase(
                phase, input, "Sage", BuilderPhase.PROTOTYPING, "Spark"
            )

        case BuilderPhase.PROTOTYPING:
            return _handle_work_phase(
                phase, input, "Spark", BuilderPhase.REFINING, "Steady"
            )

        case BuilderPhase.REFINING:
            return _handle_work_phase(
                phase, input, "Steady", BuilderPhase.INTEGRATING, "Sync"
            )

        case BuilderPhase.INTEGRATING:
            return _handle_work_phase(
                phase, input, "Sync", BuilderPhase.IDLE, None
            )

        case _:
            return BuilderPhase.IDLE, BuilderOutput(
                phase=BuilderPhase.IDLE,
                success=False,
                message=f"Unknown phase: {phase}",
            )


def _handle_work_phase(
    phase: BuilderPhase,
    input: Any,
    current_archetype: str,
    next_phase: BuilderPhase,
    next_archetype: str | None,
) -> tuple[BuilderPhase, BuilderOutput]:
    """Handle transitions for active work phases."""
    if isinstance(input, ContinueInput):
        # Continue in current phase
        return phase, BuilderOutput(
            phase=phase,
            success=True,
            message=f"{current_archetype} continuing work",
            next_builder=current_archetype,
            metadata={"note": input.note} if input.note else {},
        )
    elif isinstance(input, CompleteInput):
        # Complete and return to IDLE
        return BuilderPhase.IDLE, BuilderOutput(
            phase=BuilderPhase.IDLE,
            success=True,
            message=f"{current_archetype} completed: {input.summary or 'task finished'}",
            artifact=input.artifact,
        )
    elif isinstance(input, HandoffInput):
        # Explicit handoff to another builder
        target_phase = _archetype_to_phase(input.to_builder)
        return target_phase, BuilderOutput(
            phase=target_phase,
            success=True,
            message=f"Handoff: {input.from_builder} → {input.to_builder}",
            artifact=input.artifact,
            next_builder=input.to_builder,
            metadata={"handoff_message": input.message},
        )
    elif isinstance(input, UserQueryInput):
        # Stay in phase, waiting for user response
        return phase, BuilderOutput(
            phase=phase,
            success=True,
            message=f"{current_archetype} asks: {input.question}",
            next_builder=current_archetype,
            metadata={"awaiting_response": True, "question": input.question},
        )
    elif isinstance(input, UserResponseInput):
        # Process user response, stay in phase
        return phase, BuilderOutput(
            phase=phase,
            success=True,
            message=f"{current_archetype} received response",
            next_builder=current_archetype,
            metadata={"user_response": input.response},
        )
    elif isinstance(input, RestInput):
        # Graceful exit to IDLE
        return BuilderPhase.IDLE, BuilderOutput(
            phase=BuilderPhase.IDLE,
            success=True,
            message=f"{current_archetype} stepped back",
        )
    elif isinstance(input, TaskAssignInput):
        # Can accept new task from work phase (interruption)
        return BuilderPhase.EXPLORING, BuilderOutput(
            phase=BuilderPhase.EXPLORING,
            success=True,
            message=f"Interrupted {current_archetype} for new task: {input.task}",
            next_builder="Scout",
            metadata={
                "task": input.task,
                "priority": input.priority,
                "interrupted_phase": phase.name,
            },
        )
    else:
        # Unknown input: stay in phase, report failure
        return phase, BuilderOutput(
            phase=phase,
            success=False,
            message=f"{current_archetype} cannot handle {type(input).__name__}",
            next_builder=current_archetype,
        )


def _archetype_to_phase(archetype: str) -> BuilderPhase:
    """Map archetype name to its specialty phase."""
    archetype_lower = archetype.lower()
    mapping = {
        "scout": BuilderPhase.EXPLORING,
        "sage": BuilderPhase.DESIGNING,
        "spark": BuilderPhase.PROTOTYPING,
        "steady": BuilderPhase.REFINING,
        "sync": BuilderPhase.INTEGRATING,
    }
    return mapping.get(archetype_lower, BuilderPhase.IDLE)


# =============================================================================
# The Polynomial Agent
# =============================================================================


BUILDER_POLYNOMIAL: PolyAgent[BuilderPhase, Any, BuilderOutput] = PolyAgent(
    name="BuilderPolynomial",
    positions=frozenset(BuilderPhase),
    _directions=builder_directions,
    _transition=builder_transition,
)
"""
The Builder polynomial agent.

This models builder behavior as a polynomial state machine:
- positions: 6 phases (IDLE, EXPLORING, DESIGNING, PROTOTYPING, REFINING, INTEGRATING)
- directions: phase-dependent valid inputs
- transition: behavioral transitions with handoff support

Key Properties:
1. Natural Flow: EXPLORING → DESIGNING → PROTOTYPING → REFINING → INTEGRATING → IDLE
2. Handoff Support: Any phase can hand off to any other builder
3. Graceful Exit: RestInput always returns to IDLE
4. Interruptibility: New tasks can interrupt work phases

Composition Laws:
- Identity: IDLE + any input involving no change = IDLE
- Associativity: (handoff >> handoff) >> work = handoff >> (handoff >> work)
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "BuilderPhase",
    # Inputs
    "TaskAssignInput",
    "HandoffInput",
    "ContinueInput",
    "CompleteInput",
    "UserQueryInput",
    "UserResponseInput",
    "RestInput",
    "WakeInput",
    "BuilderInput",
    # Output
    "BuilderOutput",
    # Functions
    "builder_directions",
    "builder_transition",
    "get_next_phase",
    "get_specialist",
    # Constants
    "PHASE_ARCHETYPE_MAP",
    "NATURAL_FLOW",
    # Polynomial
    "BUILDER_POLYNOMIAL",
]
