"""
TaskPolynomial: Task Execution as State Machine.

The task polynomial models coalition task execution as a dynamical system:
- PENDING: Task awaiting coalition formation
- FORMING: Coalition being assembled
- EXECUTING: Task in progress with active coalition
- REVIEWING: Coalition reviewing output quality
- COMPLETED: Task finished successfully
- FAILED: Task failed (recoverable)
- CANCELLED: Task cancelled by user

This follows the same categorical pattern as BuilderPolynomial,
allowing composition via the TASK_OPERAD.

From the synthesis (Pattern 2):
    | Coalition | TaskPolynomial | TASK_OPERAD | OutputCoherence |

See: plans/core-apps/coalition-forge.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Task Phase (Positions in the Polynomial)
# =============================================================================


class TaskPhase(Enum):
    """
    Positions in the task polynomial.

    These represent the lifecycle stages of a ForgeTask execution.
    Each phase has distinct affordances and valid inputs.
    """

    PENDING = auto()  # Awaiting coalition formation
    FORMING = auto()  # Coalition being assembled
    EXECUTING = auto()  # Task in progress
    REVIEWING = auto()  # Output being reviewed
    COMPLETED = auto()  # Successfully finished
    FAILED = auto()  # Failed (may retry)
    CANCELLED = auto()  # User cancelled


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class StartInput:
    """Input to start coalition formation."""

    task_id: str
    template_id: str
    credits_authorized: int


@dataclass(frozen=True)
class CoalitionFormedInput:
    """Input indicating coalition is ready."""

    coalition_id: str
    builders: tuple[str, ...]  # Archetype names


@dataclass(frozen=True)
class ProgressInput:
    """Input for progress updates during execution."""

    progress_pct: float  # 0.0-1.0
    message: str = ""
    current_builder: str | None = None


@dataclass(frozen=True)
class OutputReadyInput:
    """Input indicating output is ready for review."""

    output: Any
    confidence: float = 0.0


@dataclass(frozen=True)
class ApproveInput:
    """Input to approve output and complete task."""

    pass


@dataclass(frozen=True)
class RejectInput:
    """Input to reject output and retry."""

    reason: str


@dataclass(frozen=True)
class FailInput:
    """Input indicating task failure."""

    error: str
    recoverable: bool = True


@dataclass(frozen=True)
class CancelInput:
    """Input to cancel task."""

    reason: str = "User cancelled"


@dataclass(frozen=True)
class RetryInput:
    """Input to retry failed task."""

    pass


# Input union type
TaskInput = (
    StartInput
    | CoalitionFormedInput
    | ProgressInput
    | OutputReadyInput
    | ApproveInput
    | RejectInput
    | FailInput
    | CancelInput
    | RetryInput
)


# =============================================================================
# Output Type
# =============================================================================


@dataclass
class TaskTransitionOutput:
    """Output from task phase transitions."""

    phase: TaskPhase
    success: bool
    message: str = ""
    credits_used: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def task_directions(phase: TaskPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each task phase.

    This encodes the mode-dependent behavior of task execution.
    """
    match phase:
        case TaskPhase.PENDING:
            return frozenset({StartInput, CancelInput})
        case TaskPhase.FORMING:
            return frozenset({CoalitionFormedInput, CancelInput, FailInput})
        case TaskPhase.EXECUTING:
            return frozenset({ProgressInput, OutputReadyInput, FailInput, CancelInput})
        case TaskPhase.REVIEWING:
            return frozenset({ApproveInput, RejectInput, CancelInput})
        case TaskPhase.COMPLETED:
            return frozenset()  # Terminal state
        case TaskPhase.FAILED:
            return frozenset({RetryInput, CancelInput})
        case TaskPhase.CANCELLED:
            return frozenset()  # Terminal state
        case _:
            return frozenset()


# =============================================================================
# Transition Function
# =============================================================================


def task_transition(
    phase: TaskPhase, input: TaskInput
) -> tuple[TaskPhase, TaskTransitionOutput]:
    """
    Task state transition function.

    transition: Phase × Input → (NewPhase, Output)

    Key transitions:
    - PENDING + StartInput → FORMING
    - FORMING + CoalitionFormedInput → EXECUTING
    - EXECUTING + OutputReadyInput → REVIEWING
    - REVIEWING + ApproveInput → COMPLETED
    - Any + CancelInput → CANCELLED
    - FAILED + RetryInput → FORMING (retry)
    """
    # Universal cancel handler
    if isinstance(input, CancelInput):
        return TaskPhase.CANCELLED, TaskTransitionOutput(
            phase=TaskPhase.CANCELLED,
            success=True,
            message=f"Task cancelled: {input.reason}",
            metadata={"cancel_reason": input.reason},
        )

    match phase:
        case TaskPhase.PENDING:
            if isinstance(input, StartInput):
                return TaskPhase.FORMING, TaskTransitionOutput(
                    phase=TaskPhase.FORMING,
                    success=True,
                    message=f"Starting coalition formation for {input.template_id}",
                    metadata={
                        "task_id": input.task_id,
                        "template_id": input.template_id,
                        "credits_authorized": input.credits_authorized,
                    },
                )

        case TaskPhase.FORMING:
            if isinstance(input, CoalitionFormedInput):
                return TaskPhase.EXECUTING, TaskTransitionOutput(
                    phase=TaskPhase.EXECUTING,
                    success=True,
                    message=f"Coalition formed: {', '.join(input.builders)}",
                    metadata={
                        "coalition_id": input.coalition_id,
                        "builders": input.builders,
                    },
                )
            elif isinstance(input, FailInput):
                return TaskPhase.FAILED, TaskTransitionOutput(
                    phase=TaskPhase.FAILED,
                    success=False,
                    message=f"Coalition formation failed: {input.error}",
                    metadata={"error": input.error, "recoverable": input.recoverable},
                )

        case TaskPhase.EXECUTING:
            if isinstance(input, ProgressInput):
                return TaskPhase.EXECUTING, TaskTransitionOutput(
                    phase=TaskPhase.EXECUTING,
                    success=True,
                    message=input.message or f"Progress: {input.progress_pct:.0%}",
                    metadata={
                        "progress": input.progress_pct,
                        "current_builder": input.current_builder,
                    },
                )
            elif isinstance(input, OutputReadyInput):
                return TaskPhase.REVIEWING, TaskTransitionOutput(
                    phase=TaskPhase.REVIEWING,
                    success=True,
                    message="Output ready for review",
                    metadata={
                        "confidence": input.confidence,
                        "output_type": type(input.output).__name__,
                    },
                )
            elif isinstance(input, FailInput):
                return TaskPhase.FAILED, TaskTransitionOutput(
                    phase=TaskPhase.FAILED,
                    success=False,
                    message=f"Execution failed: {input.error}",
                    metadata={"error": input.error, "recoverable": input.recoverable},
                )

        case TaskPhase.REVIEWING:
            if isinstance(input, ApproveInput):
                return TaskPhase.COMPLETED, TaskTransitionOutput(
                    phase=TaskPhase.COMPLETED,
                    success=True,
                    message="Task completed successfully",
                )
            elif isinstance(input, RejectInput):
                return TaskPhase.EXECUTING, TaskTransitionOutput(
                    phase=TaskPhase.EXECUTING,
                    success=True,
                    message=f"Output rejected, revising: {input.reason}",
                    metadata={"rejection_reason": input.reason},
                )

        case TaskPhase.FAILED:
            if isinstance(input, RetryInput):
                return TaskPhase.FORMING, TaskTransitionOutput(
                    phase=TaskPhase.FORMING,
                    success=True,
                    message="Retrying task execution",
                    metadata={"retry": True},
                )

    # Invalid transition
    return phase, TaskTransitionOutput(
        phase=phase,
        success=False,
        message=f"Invalid input {type(input).__name__} for phase {phase.name}",
    )


# =============================================================================
# The Task Polynomial Agent
# =============================================================================


TASK_POLYNOMIAL: PolyAgent[TaskPhase, TaskInput, TaskTransitionOutput] = PolyAgent(
    name="TaskPolynomial",
    positions=frozenset(TaskPhase),
    _directions=task_directions,
    _transition=task_transition,
)
"""
The Task polynomial agent.

Models ForgeTask execution as a polynomial state machine:
- positions: 7 phases (PENDING → FORMING → EXECUTING → REVIEWING → COMPLETED/FAILED/CANCELLED)
- directions: phase-dependent valid inputs
- transition: behavioral transitions with retry support

Key Properties:
1. Happy Path: PENDING → FORMING → EXECUTING → REVIEWING → COMPLETED
2. Retry Loop: FAILED + RetryInput → FORMING
3. Review Loop: REVIEWING + RejectInput → EXECUTING
4. Universal Cancel: Any phase + CancelInput → CANCELLED

Composition Laws (via TASK_OPERAD):
- Identity: PENDING + no-op = PENDING
- Associativity: (start >> form) >> execute = start >> (form >> execute)
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "TaskPhase",
    # Inputs
    "StartInput",
    "CoalitionFormedInput",
    "ProgressInput",
    "OutputReadyInput",
    "ApproveInput",
    "RejectInput",
    "FailInput",
    "CancelInput",
    "RetryInput",
    "TaskInput",
    # Output
    "TaskTransitionOutput",
    # Functions
    "task_directions",
    "task_transition",
    # Polynomial
    "TASK_POLYNOMIAL",
]
