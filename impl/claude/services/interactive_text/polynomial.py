"""
Document Polynomial State Machine.

This module implements the Document Polynomial - a state machine governing
document editing modes. Per AD-002, documents have state-dependent behavior
where the polynomial captures valid inputs per state and transition rules.

The DocumentPolynomial implements four positions:
- VIEWING: Normal viewing mode with read-only interactions
- EDITING: Active editing mode with modification capabilities
- SYNCING: Synchronization in progress with remote/file
- CONFLICTING: Conflict detected requiring resolution

Each state has a defined set of valid inputs (directions) and deterministic
transitions to new states with associated outputs.

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 11.1
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, ClassVar, Generic, TypeVar

from services.interactive_text.contracts import DocumentState

# =============================================================================
# Transition Output Types
# =============================================================================


class TransitionOutput(ABC):
    """Base class for all transition outputs."""

    @property
    @abstractmethod
    def output_type(self) -> str:
        """Type identifier for this output."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {"output_type": self.output_type}


@dataclass(frozen=True)
class NoOp(TransitionOutput):
    """No operation - invalid transition attempted."""

    message: str = "Invalid transition"

    @property
    def output_type(self) -> str:
        return "no_op"

    def to_dict(self) -> dict[str, Any]:
        return {"output_type": self.output_type, "message": self.message}


# VIEWING state outputs
@dataclass(frozen=True)
class EditSession(TransitionOutput):
    """Output when entering edit mode."""

    session_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def output_type(self) -> str:
        return "edit_session"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
        }


@dataclass(frozen=True)
class RefreshResult(TransitionOutput):
    """Output when refreshing document."""

    changed: bool = False
    version: str = ""

    @property
    def output_type(self) -> str:
        return "refresh_result"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "changed": self.changed,
            "version": self.version,
        }


@dataclass(frozen=True)
class HoverInfo(TransitionOutput):
    """Output when hovering over element."""

    element_id: str = ""
    content: str = ""

    @property
    def output_type(self) -> str:
        return "hover_info"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "element_id": self.element_id,
            "content": self.content,
        }


@dataclass(frozen=True)
class ClickResult(TransitionOutput):
    """Output when clicking element."""

    element_id: str = ""
    action_taken: str = ""

    @property
    def output_type(self) -> str:
        return "click_result"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "element_id": self.element_id,
            "action_taken": self.action_taken,
        }


@dataclass(frozen=True)
class DragResult(TransitionOutput):
    """Output when dragging element."""

    element_id: str = ""
    target: str = ""

    @property
    def output_type(self) -> str:
        return "drag_result"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "element_id": self.element_id,
            "target": self.target,
        }


# EDITING state outputs
@dataclass(frozen=True)
class SaveRequest(TransitionOutput):
    """Output when requesting save."""

    content_hash: str = ""

    @property
    def output_type(self) -> str:
        return "save_request"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "content_hash": self.content_hash,
        }


@dataclass(frozen=True)
class CancelResult(TransitionOutput):
    """Output when canceling edit."""

    changes_discarded: bool = True

    @property
    def output_type(self) -> str:
        return "cancel_result"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "changes_discarded": self.changes_discarded,
        }


@dataclass(frozen=True)
class EditContinue(TransitionOutput):
    """Output when continuing edit."""

    cursor_position: int = 0

    @property
    def output_type(self) -> str:
        return "edit_continue"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "cursor_position": self.cursor_position,
        }


# SYNCING state outputs
@dataclass(frozen=True)
class SyncComplete(TransitionOutput):
    """Output when sync completes successfully."""

    new_version: str = ""

    @property
    def output_type(self) -> str:
        return "sync_complete"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "new_version": self.new_version,
        }


@dataclass(frozen=True)
class LocalWins(TransitionOutput):
    """Output when forcing local version."""

    overwritten_version: str = ""

    @property
    def output_type(self) -> str:
        return "local_wins"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "overwritten_version": self.overwritten_version,
        }


@dataclass(frozen=True)
class RemoteWins(TransitionOutput):
    """Output when accepting remote version."""

    accepted_version: str = ""

    @property
    def output_type(self) -> str:
        return "remote_wins"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "accepted_version": self.accepted_version,
        }


@dataclass(frozen=True)
class ConflictDetected(TransitionOutput):
    """Output when conflict is detected during sync."""

    local_version: str = ""
    remote_version: str = ""
    conflict_regions: list[tuple[int, int]] = field(default_factory=list)

    @property
    def output_type(self) -> str:
        return "conflict_detected"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "local_version": self.local_version,
            "remote_version": self.remote_version,
            "conflict_regions": self.conflict_regions,
        }


# CONFLICTING state outputs
@dataclass(frozen=True)
class Resolved(TransitionOutput):
    """Output when conflict is resolved."""

    resolution_strategy: str = ""
    merged_version: str = ""

    @property
    def output_type(self) -> str:
        return "resolved"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "resolution_strategy": self.resolution_strategy,
            "merged_version": self.merged_version,
        }


@dataclass(frozen=True)
class Aborted(TransitionOutput):
    """Output when conflict resolution is aborted."""

    reverted_to: str = ""

    @property
    def output_type(self) -> str:
        return "aborted"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "reverted_to": self.reverted_to,
        }


@dataclass(frozen=True)
class DiffView(TransitionOutput):
    """Output when viewing diff in conflict state."""

    diff_content: str = ""

    @property
    def output_type(self) -> str:
        return "diff_view"

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_type": self.output_type,
            "diff_content": self.diff_content,
        }


# =============================================================================
# Document Polynomial State Machine
# =============================================================================


@dataclass(frozen=True)
class DocumentPolynomial:
    """Document as polynomial functor: editing states with mode-dependent inputs.
    
    Per AD-002, documents have state-dependent behavior. The polynomial
    captures valid inputs per state and transition rules.
    
    The DocumentPolynomial implements:
    - Four positions (states): VIEWING, EDITING, SYNCING, CONFLICTING
    - directions(): Returns valid inputs for each state
    - transition(): Maps (state, input) → (new_state, output)
    
    This is a pure state machine - it does not hold state itself but
    defines the transition function. Actual document state is managed
    by the DocumentSheaf.
    
    Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
    """

    # Class-level constants
    positions: ClassVar[frozenset[DocumentState]] = frozenset(DocumentState)

    # Valid inputs per state
    _directions: ClassVar[dict[DocumentState, frozenset[str]]] = {
        DocumentState.VIEWING: frozenset({"edit", "refresh", "hover", "click", "drag"}),
        DocumentState.EDITING: frozenset({"save", "cancel", "continue_edit", "hover"}),
        DocumentState.SYNCING: frozenset({"wait", "force_local", "force_remote"}),
        DocumentState.CONFLICTING: frozenset({"resolve", "abort", "view_diff"}),
    }

    # Transition table: (state, input) → (new_state, output_factory)
    _transitions: ClassVar[dict[tuple[DocumentState, str], tuple[DocumentState, type[TransitionOutput]]]] = {
        # VIEWING transitions (Requirement 3.2)
        (DocumentState.VIEWING, "edit"): (DocumentState.EDITING, EditSession),
        (DocumentState.VIEWING, "refresh"): (DocumentState.VIEWING, RefreshResult),
        (DocumentState.VIEWING, "hover"): (DocumentState.VIEWING, HoverInfo),
        (DocumentState.VIEWING, "click"): (DocumentState.VIEWING, ClickResult),
        (DocumentState.VIEWING, "drag"): (DocumentState.VIEWING, DragResult),

        # EDITING transitions (Requirement 3.3)
        (DocumentState.EDITING, "save"): (DocumentState.SYNCING, SaveRequest),
        (DocumentState.EDITING, "cancel"): (DocumentState.VIEWING, CancelResult),
        (DocumentState.EDITING, "continue_edit"): (DocumentState.EDITING, EditContinue),
        (DocumentState.EDITING, "hover"): (DocumentState.EDITING, HoverInfo),

        # SYNCING transitions (Requirement 3.4)
        (DocumentState.SYNCING, "wait"): (DocumentState.VIEWING, SyncComplete),
        (DocumentState.SYNCING, "force_local"): (DocumentState.VIEWING, LocalWins),
        (DocumentState.SYNCING, "force_remote"): (DocumentState.VIEWING, RemoteWins),

        # CONFLICTING transitions (Requirement 3.5)
        (DocumentState.CONFLICTING, "resolve"): (DocumentState.VIEWING, Resolved),
        (DocumentState.CONFLICTING, "abort"): (DocumentState.VIEWING, Aborted),
        (DocumentState.CONFLICTING, "view_diff"): (DocumentState.CONFLICTING, DiffView),
    }

    @classmethod
    def directions(cls, state: DocumentState) -> frozenset[str]:
        """Get valid inputs for a given state.
        
        Args:
            state: The current document state
            
        Returns:
            Set of valid input strings for this state
            
        Requirements: 3.2, 3.3, 3.4, 3.5
        """
        return cls._directions.get(state, frozenset())

    @classmethod
    def transition(
        cls,
        state: DocumentState,
        input_action: str,
    ) -> tuple[DocumentState, TransitionOutput]:
        """Compute state transition for given state and input.
        
        This is a pure function: same (state, input) always produces
        same (new_state, output). The polynomial is deterministic.
        
        Args:
            state: Current document state
            input_action: The input action to process
            
        Returns:
            Tuple of (new_state, output) where output is a TransitionOutput
            
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        key = (state, input_action)

        if key in cls._transitions:
            new_state, output_type = cls._transitions[key]
            return (new_state, output_type())

        # Invalid transition - return NoOp
        return (state, NoOp(message=f"Invalid input '{input_action}' for state {state.value}"))

    @classmethod
    def is_valid_input(cls, state: DocumentState, input_action: str) -> bool:
        """Check if an input is valid for a given state.
        
        Args:
            state: The current document state
            input_action: The input to check
            
        Returns:
            True if the input is valid for this state
        """
        return input_action in cls.directions(state)

    @classmethod
    def get_all_transitions(cls) -> dict[tuple[DocumentState, str], tuple[DocumentState, type[TransitionOutput]]]:
        """Get the complete transition table.
        
        Returns:
            Dictionary mapping (state, input) to (new_state, output_type)
        """
        return dict(cls._transitions)

    @classmethod
    def verify_determinism(cls) -> bool:
        """Verify that the polynomial is deterministic.
        
        A polynomial is deterministic if the same (state, input) always
        produces the same (new_state, output_type).
        
        Returns:
            True if the polynomial is deterministic
        """
        # Since we use a dictionary for transitions, determinism is guaranteed
        # by the data structure. This method verifies the invariant.
        for state in DocumentState:
            for input_action in cls.directions(state):
                result1 = cls.transition(state, input_action)
                result2 = cls.transition(state, input_action)
                if result1[0] != result2[0]:
                    return False
                if type(result1[1]) != type(result2[1]):
                    return False
        return True

    @classmethod
    def verify_completeness(cls) -> bool:
        """Verify that all states have defined directions.
        
        Returns:
            True if all states have at least one valid input
        """
        for state in DocumentState:
            if not cls.directions(state):
                return False
        return True

    @classmethod
    def verify_laws(cls) -> bool:
        """Verify polynomial laws hold.
        
        Verifies:
        1. Determinism: Same (state, input) always produces same output
        2. Completeness: All states have defined directions
        3. Closure: All transitions lead to valid states
        
        Returns:
            True if all laws hold
        """
        # Check determinism
        if not cls.verify_determinism():
            return False

        # Check completeness
        if not cls.verify_completeness():
            return False

        # Check closure - all target states are valid
        for (_, _), (new_state, _) in cls._transitions.items():
            if new_state not in cls.positions:
                return False

        return True


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State machine
    "DocumentPolynomial",
    # Output types
    "TransitionOutput",
    "NoOp",
    "EditSession",
    "RefreshResult",
    "HoverInfo",
    "ClickResult",
    "DragResult",
    "SaveRequest",
    "CancelResult",
    "EditContinue",
    "SyncComplete",
    "LocalWins",
    "RemoteWins",
    "ConflictDetected",
    "Resolved",
    "Aborted",
    "DiffView",
]
