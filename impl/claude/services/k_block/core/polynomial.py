"""
KBlockPolynomial: State machine for K-Block isolation.

K-Blocks have state-dependent behavior at two levels:
1. IsolationState: PRISTINE, DIRTY, STALE, CONFLICTING, ENTANGLED
2. EditingState: VIEWING, EDITING (inherited from DocumentPolynomial)

The KBlockPolynomial composes these, defining valid transitions
and allowed operations per state.

Philosophy:
    "The polynomial is the territory. The state is the map.
     Valid transitions are the roads you may travel."

See: spec/protocols/k-block.md
See: spec/agents/polyfunctor.md (AD-002)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, ClassVar

from .kblock import IsolationState

# -----------------------------------------------------------------------------
# Editing States (from DocumentPolynomial)
# -----------------------------------------------------------------------------


class EditingState(Enum):
    """
    Editing states within a K-Block.

    Inherited from DocumentPolynomial in interactive-text.md.
    """

    VIEWING = auto()  # Read-only observation
    EDITING = auto()  # Local modifications in progress


# -----------------------------------------------------------------------------
# Compound State
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class KBlockState:
    """
    Compound state: isolation x editing.

    This is a position in the KBlockPolynomial.
    """

    isolation: IsolationState
    editing: EditingState

    def __str__(self) -> str:
        return f"{self.isolation.name}:{self.editing.name}"

    @classmethod
    def initial(cls) -> "KBlockState":
        """The initial state after K-Block creation."""
        return cls(IsolationState.PRISTINE, EditingState.VIEWING)


# -----------------------------------------------------------------------------
# Input Types (Directions)
# -----------------------------------------------------------------------------


class KBlockInput(Enum):
    """
    Valid inputs to the K-Block state machine.

    These are the "directions" at each position.
    """

    # Editing inputs
    START_EDIT = auto()  # Begin editing
    FINISH_EDIT = auto()  # End editing (content committed locally)
    CANCEL_EDIT = auto()  # Abort edit, revert

    # Harness inputs
    SAVE = auto()  # Commit to cosmos
    DISCARD = auto()  # Abandon K-Block
    FORK = auto()  # Create parallel universe
    CHECKPOINT = auto()  # Create restore point
    REWIND = auto()  # Restore to checkpoint

    # Refresh inputs
    REFRESH = auto()  # Pull latest from cosmos
    IGNORE_STALE = auto()  # Acknowledge but continue
    RESOLVE_CONFLICT = auto()  # Mark conflict as resolved

    # Entanglement inputs
    ENTANGLE = auto()  # Link to another K-Block
    DISENTANGLE = auto()  # Unlink from partner


# -----------------------------------------------------------------------------
# Output Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class KBlockOutput:
    """
    Output from a state transition.

    Contains the action to perform and any side effects.
    """

    action: str
    success: bool = True
    message: str = ""
    data: Any = None


# -----------------------------------------------------------------------------
# KBlockPolynomial
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class KBlockPolynomial:
    """
    K-Block as polynomial functor: state-dependent behavior.

    A polynomial functor P : Set -> Set is defined by:
        P(X) = Σ_{s ∈ S} X^{D(s)}

    Where S is the set of states (positions) and D(s) is the
    set of valid inputs (directions) at state s.

    For K-Blocks:
        S = IsolationState x EditingState
        D(s) = valid inputs at compound state s
    """

    # All possible positions (cross-product of isolation and editing)
    POSITIONS: ClassVar[frozenset[KBlockState]] = frozenset(
        KBlockState(iso, edit) for iso in IsolationState for edit in EditingState
    )

    @staticmethod
    def directions(state: KBlockState) -> frozenset[KBlockInput]:
        """
        Valid inputs at a given state.

        This defines the "directions" available at each "position".
        """
        iso, edit = state.isolation, state.editing

        # Base directions always available
        base = frozenset({KBlockInput.FORK})

        # Editing-dependent directions
        if edit == EditingState.VIEWING:
            edit_dirs = frozenset({KBlockInput.START_EDIT})
        else:  # EDITING
            edit_dirs = frozenset({KBlockInput.FINISH_EDIT, KBlockInput.CANCEL_EDIT})

        # Isolation-dependent directions
        iso_dirs: frozenset[KBlockInput]
        if iso == IsolationState.PRISTINE:
            iso_dirs = frozenset({KBlockInput.SAVE, KBlockInput.DISCARD})
        elif iso == IsolationState.DIRTY:
            iso_dirs = frozenset(
                {KBlockInput.SAVE, KBlockInput.DISCARD, KBlockInput.CHECKPOINT, KBlockInput.REWIND}
            )
        elif iso == IsolationState.STALE:
            iso_dirs = frozenset(
                {KBlockInput.REFRESH, KBlockInput.IGNORE_STALE, KBlockInput.DISCARD}
            )
        elif iso == IsolationState.CONFLICTING:
            iso_dirs = frozenset({KBlockInput.RESOLVE_CONFLICT, KBlockInput.DISCARD})
        elif iso == IsolationState.ENTANGLED:
            iso_dirs = frozenset({KBlockInput.DISENTANGLE})
        else:
            iso_dirs = frozenset()

        return base | edit_dirs | iso_dirs

    @staticmethod
    def transition(state: KBlockState, input: KBlockInput) -> tuple[KBlockState, KBlockOutput]:
        """
        State transition function.

        (State, Input) -> (NewState, Output)

        Returns the new state and any output/side-effects.
        """
        iso, edit = state.isolation, state.editing

        # Editing transitions
        if input == KBlockInput.START_EDIT:
            if edit == EditingState.VIEWING:
                return (
                    KBlockState(iso, EditingState.EDITING),
                    KBlockOutput("start_edit", message="Editing started"),
                )
            return (state, KBlockOutput("noop", success=False, message="Already editing"))

        if input == KBlockInput.FINISH_EDIT:
            if edit == EditingState.EDITING:
                new_iso = IsolationState.DIRTY if iso == IsolationState.PRISTINE else iso
                return (
                    KBlockState(new_iso, EditingState.VIEWING),
                    KBlockOutput("finish_edit", message="Edit finished"),
                )
            return (state, KBlockOutput("noop", success=False, message="Not editing"))

        if input == KBlockInput.CANCEL_EDIT:
            if edit == EditingState.EDITING:
                return (
                    KBlockState(iso, EditingState.VIEWING),
                    KBlockOutput("cancel_edit", message="Edit cancelled"),
                )
            return (state, KBlockOutput("noop", success=False, message="Not editing"))

        # Harness transitions
        if input == KBlockInput.SAVE:
            if iso in (IsolationState.PRISTINE, IsolationState.DIRTY):
                return (
                    KBlockState(IsolationState.PRISTINE, edit),
                    KBlockOutput("save", message="Saved to cosmos"),
                )
            return (
                state,
                KBlockOutput("save", success=False, message="Cannot save in current state"),
            )

        if input == KBlockInput.DISCARD:
            if iso != IsolationState.ENTANGLED:
                return (
                    state,  # State doesn't matter, block is discarded
                    KBlockOutput("discard", message="K-Block discarded"),
                )
            return (
                state,
                KBlockOutput("discard", success=False, message="Cannot discard entangled K-Block"),
            )

        if input == KBlockInput.FORK:
            return (
                state,  # Original keeps its state
                KBlockOutput("fork", message="K-Block forked", data={"creates_clone": True}),
            )

        if input == KBlockInput.CHECKPOINT:
            if iso == IsolationState.DIRTY:
                return (
                    state,
                    KBlockOutput("checkpoint", message="Checkpoint created"),
                )
            return (
                state,
                KBlockOutput("checkpoint", success=False, message="No changes to checkpoint"),
            )

        if input == KBlockInput.REWIND:
            if iso == IsolationState.DIRTY:
                return (
                    KBlockState(IsolationState.DIRTY, edit),
                    KBlockOutput("rewind", message="Rewound to checkpoint"),
                )
            return (
                state,
                KBlockOutput("rewind", success=False, message="No checkpoint to rewind to"),
            )

        # Refresh transitions
        if input == KBlockInput.REFRESH:
            if iso == IsolationState.STALE:
                return (
                    KBlockState(IsolationState.PRISTINE, edit),
                    KBlockOutput("refresh", message="Refreshed from cosmos"),
                )
            if iso == IsolationState.CONFLICTING:
                return (
                    KBlockState(IsolationState.DIRTY, edit),
                    KBlockOutput("refresh", message="Refreshed, conflicts remain"),
                )
            return (state, KBlockOutput("refresh", success=False, message="Not stale"))

        if input == KBlockInput.IGNORE_STALE:
            if iso == IsolationState.STALE:
                return (
                    KBlockState(IsolationState.DIRTY, edit),
                    KBlockOutput("ignore_stale", message="Continuing with stale base"),
                )
            return (state, KBlockOutput("ignore_stale", success=False, message="Not stale"))

        if input == KBlockInput.RESOLVE_CONFLICT:
            if iso == IsolationState.CONFLICTING:
                return (
                    KBlockState(IsolationState.DIRTY, edit),
                    KBlockOutput("resolve_conflict", message="Conflict resolved"),
                )
            return (state, KBlockOutput("resolve_conflict", success=False, message="No conflict"))

        # Entanglement transitions
        if input == KBlockInput.ENTANGLE:
            if iso not in (IsolationState.ENTANGLED,):
                return (
                    KBlockState(IsolationState.ENTANGLED, edit),
                    KBlockOutput("entangle", message="Entangled with partner"),
                )
            return (state, KBlockOutput("entangle", success=False, message="Already entangled"))

        if input == KBlockInput.DISENTANGLE:
            if iso == IsolationState.ENTANGLED:
                return (
                    KBlockState(IsolationState.DIRTY, edit),
                    KBlockOutput("disentangle", message="Disentangled"),
                )
            return (state, KBlockOutput("disentangle", success=False, message="Not entangled"))

        # Unknown input
        return (state, KBlockOutput("unknown", success=False, message=f"Unknown input: {input}"))

    @classmethod
    def is_valid_transition(cls, state: KBlockState, input: KBlockInput) -> bool:
        """Check if an input is valid at a given state."""
        return input in cls.directions(state)

    @classmethod
    def can_reach(cls, from_state: KBlockState, to_state: KBlockState) -> list[KBlockInput] | None:
        """
        Find a path of inputs from one state to another.

        Returns list of inputs if reachable, None otherwise.
        Simple BFS implementation.
        """
        if from_state == to_state:
            return []

        from collections import deque

        visited: set[KBlockState] = {from_state}
        queue: deque[tuple[KBlockState, list[KBlockInput]]] = deque([(from_state, [])])

        while queue:
            current, path = queue.popleft()

            for input in cls.directions(current):
                new_state, output = cls.transition(current, input)
                if output.success and new_state not in visited:
                    new_path = path + [input]
                    if new_state == to_state:
                        return new_path
                    visited.add(new_state)
                    queue.append((new_state, new_path))

        return None


# -----------------------------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------------------------


def get_valid_actions(block_state: KBlockState) -> list[str]:
    """Get human-readable list of valid actions at a state."""
    directions = KBlockPolynomial.directions(block_state)
    return [d.name.lower().replace("_", " ") for d in directions]


def describe_state(block_state: KBlockState) -> str:
    """Get human-readable description of a state."""
    iso, edit = block_state.isolation, block_state.editing

    iso_desc = {
        IsolationState.PRISTINE: "No local changes",
        IsolationState.DIRTY: "Has uncommitted changes",
        IsolationState.STALE: "Upstream changed",
        IsolationState.CONFLICTING: "Has merge conflicts",
        IsolationState.ENTANGLED: "Linked to another K-Block",
    }

    edit_desc = {
        EditingState.VIEWING: "viewing",
        EditingState.EDITING: "editing",
    }

    return f"{iso_desc[iso]} ({edit_desc[edit]})"
