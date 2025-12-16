"""
Prompt Polynomial: The State Machine for CLAUDE.md Lifecycle.

The prompt system is a PolyAgent with positions (states), directions (inputs),
and transitions that govern the lifecycle of the system prompt.

States:
- STABLE: No pending changes, prompt is current
- EVOLVING: Changes proposed, awaiting approval
- VALIDATING: Running category law checks
- COMPILING: Assembling sections into final output

See: spec/protocols/evergreen-prompt-system.md Part II
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, FrozenSet

from agents.poly import PolyAgent

if TYPE_CHECKING:
    from .section_base import Section


class PromptState(Enum):
    """
    Positions in the prompt polynomial.

    These represent the lifecycle states of the Evergreen Prompt System.
    """

    STABLE = auto()  # No pending changes, prompt is current
    EVOLVING = auto()  # Changes proposed, awaiting approval
    VALIDATING = auto()  # Running category law checks
    COMPILING = auto()  # N-Phase compiler assembling output


@dataclass(frozen=True)
class PromptInput:
    """
    Input to the prompt polynomial.

    Different states accept different inputs:
    - STABLE: evolution proposals, compile requests
    - EVOLVING: approval/rejection, validation requests
    - VALIDATING: validation results
    - COMPILING: section inputs
    """

    kind: str  # "propose", "approve", "reject", "validate", "compile", "section"
    payload: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

    def __hash__(self) -> int:
        return hash((self.kind, str(self.payload)))


@dataclass(frozen=True)
class PromptOutput:
    """
    Output from prompt polynomial transitions.

    Captures the result of state transitions with metadata.
    """

    content: str | None = None  # Compiled prompt content (if applicable)
    message: str = ""  # Human-readable status message
    sections: tuple[str, ...] = ()  # Sections involved in this operation
    success: bool = True

    def __hash__(self) -> int:
        return hash((self.content, self.message, self.success))


# =============================================================================
# Valid inputs per state (directions)
# =============================================================================

VALID_INPUTS: dict[PromptState, FrozenSet[str]] = {
    PromptState.STABLE: frozenset({"propose", "compile", "manifest"}),
    PromptState.EVOLVING: frozenset({"approve", "reject", "validate"}),
    PromptState.VALIDATING: frozenset({"validation_pass", "validation_fail"}),
    PromptState.COMPILING: frozenset({"section", "complete", "abort"}),
}


def _prompt_directions(state: PromptState) -> FrozenSet[str]:
    """Get valid input kinds for a given state."""
    return VALID_INPUTS.get(state, frozenset())


# =============================================================================
# State transitions
# =============================================================================


def _prompt_transition(
    state: PromptState,
    input: PromptInput,
) -> tuple[PromptState, PromptOutput]:
    """
    Execute prompt state transition.

    Transition rules:
    - STABLE + propose → EVOLVING
    - STABLE + compile → COMPILING
    - STABLE + manifest → STABLE (returns current prompt)
    - EVOLVING + approve → VALIDATING
    - EVOLVING + reject → STABLE
    - EVOLVING + validate → VALIDATING
    - VALIDATING + validation_pass → COMPILING
    - VALIDATING + validation_fail → EVOLVING (back to fix issues)
    - COMPILING + section → COMPILING (accumulate sections)
    - COMPILING + complete → STABLE (emit compiled prompt)
    - COMPILING + abort → STABLE (cancel compilation)
    """
    kind = input.kind

    if state == PromptState.STABLE:
        if kind == "propose":
            return (
                PromptState.EVOLVING,
                PromptOutput(message=f"Evolution proposed: {input.payload}"),
            )
        elif kind == "compile":
            return (PromptState.COMPILING, PromptOutput(message="Starting compilation"))
        elif kind == "manifest":
            # Stay in STABLE, return current prompt
            return (
                PromptState.STABLE,
                PromptOutput(
                    content=str(input.payload) if input.payload else None,
                    message="Current prompt manifested",
                ),
            )

    elif state == PromptState.EVOLVING:
        if kind == "approve":
            return (
                PromptState.VALIDATING,
                PromptOutput(message="Evolution approved, validating laws"),
            )
        elif kind == "reject":
            return (
                PromptState.STABLE,
                PromptOutput(message="Evolution rejected", success=False),
            )
        elif kind == "validate":
            return (
                PromptState.VALIDATING,
                PromptOutput(message="Validation requested"),
            )

    elif state == PromptState.VALIDATING:
        if kind == "validation_pass":
            return (
                PromptState.COMPILING,
                PromptOutput(message="All laws verified, compiling"),
            )
        elif kind == "validation_fail":
            return (
                PromptState.EVOLVING,
                PromptOutput(message=f"Law violation: {input.payload}", success=False),
            )

    elif state == PromptState.COMPILING:
        if kind == "section":
            # Accumulate section (actual accumulation handled by compiler)
            return (
                PromptState.COMPILING,
                PromptOutput(
                    message=f"Section added: {input.payload}",
                    sections=(str(input.payload),),
                ),
            )
        elif kind == "complete":
            return (
                PromptState.STABLE,
                PromptOutput(
                    content=str(input.payload) if input.payload else None,
                    message="Compilation complete",
                ),
            )
        elif kind == "abort":
            return (
                PromptState.STABLE,
                PromptOutput(message="Compilation aborted", success=False),
            )

    # Invalid transition
    return (
        state,
        PromptOutput(
            message=f"Invalid input '{kind}' for state {state.name}", success=False
        ),
    )


# =============================================================================
# The Prompt Polynomial
# =============================================================================


def _validate_and_transition(
    state: PromptState,
    input: PromptInput,
) -> tuple[PromptState, PromptOutput]:
    """
    Validate input is valid for state, then execute transition.

    This wrapper validates input.kind against VALID_INPUTS before
    calling the transition function.
    """
    valid_kinds = VALID_INPUTS.get(state, frozenset())
    if input.kind not in valid_kinds:
        return (
            state,
            PromptOutput(
                message=f"Invalid input '{input.kind}' for state {state.name}. Valid: {valid_kinds}",
                success=False,
            ),
        )
    return _prompt_transition(state, input)


PROMPT_POLYNOMIAL: PolyAgent[PromptState, PromptInput, PromptOutput] = PolyAgent(
    name="PromptPolynomial",
    positions=frozenset(PromptState),
    _directions=lambda s: frozenset({Any}),  # Accept any input, validate in transition
    _transition=_validate_and_transition,
)
"""
The Evergreen Prompt polynomial agent.

A PolyAgent that manages the lifecycle of CLAUDE.md through
compilation, evolution, and validation states.

Usage:
    state = PromptState.STABLE
    input = PromptInput(kind="propose", payload="Add new skill")
    new_state, output = PROMPT_POLYNOMIAL.invoke(state, input)
    # new_state = PromptState.EVOLVING
    # output.message = "Evolution proposed: Add new skill"
"""


__all__ = [
    "PromptState",
    "PromptInput",
    "PromptOutput",
    "PROMPT_POLYNOMIAL",
    "VALID_INPUTS",
]
