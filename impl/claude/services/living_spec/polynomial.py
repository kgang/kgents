"""
SpecPolynomial: Unified state machine for living specs.

The SpecPolynomial unifies state machines from:
- DocumentPolynomial (VIEWING, EDITING, SYNCING, CONFLICTING)
- PortalState (COLLAPSED, LOADING, EXPANDED, ERROR)
- New states (HOVERING, NAVIGATING, WITNESSING)

The polynomial defines:
1. Positions (states)
2. Directions (valid inputs per state)
3. Transitions (state × input → new state, effect)

Per AD-002, the polynomial is stateless — state lives in the caller,
not in the polynomial itself. Each transition takes state as input
and returns (new_state, effect).

Philosophy:
    "The rate of change of a document IS its interactivity."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, ClassVar

# -----------------------------------------------------------------------------
# States
# -----------------------------------------------------------------------------


class SpecState(Enum):
    """
    Unified states for living specs.

    From DocumentPolynomial:
    - VIEWING: Read-only observation
    - EDITING: Local modifications in progress
    - SYNCING: Reconciling with cosmos
    - CONFLICTING: Both local and upstream changes

    From PortalState (embedded):
    - EXPANDING: Loading portal content
    - NAVIGATING: Following hyperedge

    New:
    - HOVERING: Showing tooltip/preview
    - WITNESSING: Recording decision trace
    """

    # Read states
    VIEWING = auto()  # Default read state
    HOVERING = auto()  # Tooltip/preview visible

    # Navigation states
    EXPANDING = auto()  # Portal loading
    NAVIGATING = auto()  # Following hyperedge

    # Edit states
    EDITING = auto()  # In monad, making changes
    SYNCING = auto()  # Committing to cosmos
    CONFLICTING = auto()  # Merge conflict

    # Meta states
    WITNESSING = auto()  # Recording decision/reasoning


# -----------------------------------------------------------------------------
# Effects
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Effect:
    """
    Effect produced by a state transition.

    Effects are side-effect descriptors — they tell the system
    what should happen, but don't execute it directly.
    """

    effect_type: str
    data: dict[str, Any] = field(default_factory=dict)

    # Standard effect types
    NO_OP: ClassVar[str] = "no_op"
    SHOW_TOOLTIP: ClassVar[str] = "show_tooltip"
    HIDE_TOOLTIP: ClassVar[str] = "hide_tooltip"
    START_EXPANSION: ClassVar[str] = "start_expansion"
    EXPANSION_COMPLETE: ClassVar[str] = "expansion_complete"
    EXPANSION_ERROR: ClassVar[str] = "expansion_error"
    START_NAVIGATION: ClassVar[str] = "start_navigation"
    NAVIGATION_COMPLETE: ClassVar[str] = "navigation_complete"
    BACKTRACK_COMPLETE: ClassVar[str] = "backtrack_complete"
    ENTER_MONAD: ClassVar[str] = "enter_monad"
    EXIT_MONAD: ClassVar[str] = "exit_monad"
    START_COMMIT: ClassVar[str] = "start_commit"
    COMMIT_COMPLETE: ClassVar[str] = "commit_complete"
    DISCARD_CHANGES: ClassVar[str] = "discard_changes"
    CHECKPOINT_CREATED: ClassVar[str] = "checkpoint_created"
    CONFLICT_DETECTED: ClassVar[str] = "conflict_detected"
    CONFLICT_RESOLVED: ClassVar[str] = "conflict_resolved"
    CHANGES_ABORTED: ClassVar[str] = "changes_aborted"
    PROMPT_WITNESS: ClassVar[str] = "prompt_witness"
    MARK_RECORDED: ClassVar[str] = "mark_recorded"
    WITNESS_SKIPPED: ClassVar[str] = "witness_skipped"


# -----------------------------------------------------------------------------
# Polynomial
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SpecPolynomial:
    """
    Unified state machine for living specs.

    The polynomial is stateless — it's a pure function from
    (state, input) → (new_state, effect).

    Usage:
        poly = SpecPolynomial()
        new_state, effect = poly.transition(current_state, "edit")
    """

    # All valid positions (states)
    positions: ClassVar[frozenset[SpecState]] = frozenset(SpecState)

    # Valid inputs per state
    _directions: ClassVar[dict[SpecState, frozenset[str]]] = {
        SpecState.VIEWING: frozenset(
            {
                "hover",  # → HOVERING (show tooltip)
                "click",  # Stay in VIEWING (handle click)
                "edit",  # → EDITING (enter monad)
                "expand",  # → EXPANDING (load portal)
                "navigate",  # → NAVIGATING (follow edge)
                "refresh",  # Stay in VIEWING (reload)
            }
        ),
        SpecState.HOVERING: frozenset(
            {
                "leave",  # → VIEWING (hide tooltip)
                "click",  # → depends on token
                "expand",  # → EXPANDING (from hover)
            }
        ),
        SpecState.EXPANDING: frozenset(
            {
                "complete",  # → VIEWING (show expanded)
                "error",  # → VIEWING (show error)
                "cancel",  # → VIEWING (abort)
            }
        ),
        SpecState.NAVIGATING: frozenset(
            {
                "arrive",  # → VIEWING (at destination)
                "backtrack",  # → VIEWING (go back)
                "error",  # → VIEWING (nav failed)
            }
        ),
        SpecState.EDITING: frozenset(
            {
                "save",  # → SYNCING (commit)
                "cancel",  # → VIEWING (discard)
                "checkpoint",  # Stay in EDITING (save point)
                "continue",  # Stay in EDITING (keep editing)
            }
        ),
        SpecState.SYNCING: frozenset(
            {
                "complete",  # → WITNESSING (prompt for witness)
                "conflict",  # → CONFLICTING (merge needed)
                "error",  # → EDITING (retry possible)
            }
        ),
        SpecState.CONFLICTING: frozenset(
            {
                "resolve",  # → WITNESSING (after resolution)
                "abort",  # → VIEWING (abandon changes)
                "force_local",  # → SYNCING (overwrite)
                "force_remote",  # → VIEWING (accept upstream)
            }
        ),
        SpecState.WITNESSING: frozenset(
            {
                "mark",  # → VIEWING (record witness mark)
                "skip",  # → VIEWING (no witness)
            }
        ),
    }

    # State transition table: (state, input) → (new_state, effect_type)
    _transitions: ClassVar[dict[tuple[SpecState, str], tuple[SpecState, str]]] = {
        # From VIEWING
        (SpecState.VIEWING, "hover"): (SpecState.HOVERING, Effect.SHOW_TOOLTIP),
        (SpecState.VIEWING, "click"): (SpecState.VIEWING, Effect.NO_OP),
        (SpecState.VIEWING, "edit"): (SpecState.EDITING, Effect.ENTER_MONAD),
        (SpecState.VIEWING, "expand"): (SpecState.EXPANDING, Effect.START_EXPANSION),
        (SpecState.VIEWING, "navigate"): (SpecState.NAVIGATING, Effect.START_NAVIGATION),
        (SpecState.VIEWING, "refresh"): (SpecState.VIEWING, Effect.NO_OP),
        # From HOVERING
        (SpecState.HOVERING, "leave"): (SpecState.VIEWING, Effect.HIDE_TOOLTIP),
        (SpecState.HOVERING, "click"): (SpecState.VIEWING, Effect.NO_OP),
        (SpecState.HOVERING, "expand"): (SpecState.EXPANDING, Effect.START_EXPANSION),
        # From EXPANDING
        (SpecState.EXPANDING, "complete"): (SpecState.VIEWING, Effect.EXPANSION_COMPLETE),
        (SpecState.EXPANDING, "error"): (SpecState.VIEWING, Effect.EXPANSION_ERROR),
        (SpecState.EXPANDING, "cancel"): (SpecState.VIEWING, Effect.NO_OP),
        # From NAVIGATING
        (SpecState.NAVIGATING, "arrive"): (SpecState.VIEWING, Effect.NAVIGATION_COMPLETE),
        (SpecState.NAVIGATING, "backtrack"): (SpecState.VIEWING, Effect.BACKTRACK_COMPLETE),
        (SpecState.NAVIGATING, "error"): (SpecState.VIEWING, Effect.NO_OP),
        # From EDITING
        (SpecState.EDITING, "save"): (SpecState.SYNCING, Effect.START_COMMIT),
        (SpecState.EDITING, "cancel"): (SpecState.VIEWING, Effect.DISCARD_CHANGES),
        (SpecState.EDITING, "checkpoint"): (SpecState.EDITING, Effect.CHECKPOINT_CREATED),
        (SpecState.EDITING, "continue"): (SpecState.EDITING, Effect.NO_OP),
        # From SYNCING
        (SpecState.SYNCING, "complete"): (SpecState.WITNESSING, Effect.PROMPT_WITNESS),
        (SpecState.SYNCING, "conflict"): (SpecState.CONFLICTING, Effect.CONFLICT_DETECTED),
        (SpecState.SYNCING, "error"): (SpecState.EDITING, Effect.NO_OP),
        # From CONFLICTING
        (SpecState.CONFLICTING, "resolve"): (SpecState.WITNESSING, Effect.CONFLICT_RESOLVED),
        (SpecState.CONFLICTING, "abort"): (SpecState.VIEWING, Effect.CHANGES_ABORTED),
        (SpecState.CONFLICTING, "force_local"): (SpecState.SYNCING, Effect.START_COMMIT),
        (SpecState.CONFLICTING, "force_remote"): (SpecState.VIEWING, Effect.DISCARD_CHANGES),
        # From WITNESSING
        (SpecState.WITNESSING, "mark"): (SpecState.VIEWING, Effect.MARK_RECORDED),
        (SpecState.WITNESSING, "skip"): (SpecState.VIEWING, Effect.WITNESS_SKIPPED),
    }

    @classmethod
    def directions(cls, state: SpecState) -> frozenset[str]:
        """Get valid inputs for a state."""
        return cls._directions.get(state, frozenset())

    @classmethod
    def transition(cls, state: SpecState, input_action: str) -> tuple[SpecState, Effect]:
        """
        Execute state transition.

        Args:
            state: Current state
            input_action: Input action to process

        Returns:
            Tuple of (new_state, effect)
        """
        key = (state, input_action)
        if key in cls._transitions:
            new_state, effect_type = cls._transitions[key]
            return (new_state, Effect(effect_type=effect_type))

        # Invalid transition — no-op
        return (
            state,
            Effect(
                effect_type=Effect.NO_OP,
                data={"reason": "invalid_transition", "input": input_action},
            ),
        )

    @classmethod
    def is_editing(cls, state: SpecState) -> bool:
        """Whether state is in editing mode (monad active)."""
        return state in {SpecState.EDITING, SpecState.SYNCING, SpecState.CONFLICTING}

    @classmethod
    def is_transitioning(cls, state: SpecState) -> bool:
        """Whether state is mid-transition (loading, navigating)."""
        return state in {SpecState.EXPANDING, SpecState.NAVIGATING, SpecState.SYNCING}

    @classmethod
    def can_edit(cls, state: SpecState) -> bool:
        """Whether edit action is valid from this state."""
        return "edit" in cls.directions(state)

    @classmethod
    def describe_state(cls, state: SpecState) -> str:
        """Human-readable state description."""
        descriptions = {
            SpecState.VIEWING: "Viewing spec (read-only)",
            SpecState.HOVERING: "Previewing token",
            SpecState.EXPANDING: "Loading portal content...",
            SpecState.NAVIGATING: "Following hyperedge...",
            SpecState.EDITING: "Editing in isolation (K-Block active)",
            SpecState.SYNCING: "Committing changes to cosmos...",
            SpecState.CONFLICTING: "Merge conflict detected",
            SpecState.WITNESSING: "Recording decision trace",
        }
        return descriptions.get(state, state.name)


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


def get_valid_actions(state: SpecState) -> list[str]:
    """Get list of valid actions for a state."""
    return sorted(SpecPolynomial.directions(state))


def describe_state(state: SpecState) -> str:
    """Get human-readable description of a state."""
    return SpecPolynomial.describe_state(state)
