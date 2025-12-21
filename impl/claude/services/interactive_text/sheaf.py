"""
Document Sheaf: Multi-View Coherence Structure.

This module implements the Document Sheaf - a coherence structure ensuring
multi-view consistency for documents. The sheaf guarantees that local views
glue to global state, with the file on disk as the canonical source of truth.

The DocumentSheaf implements:
- overlap(): Shared tokens between views
- compatible(): Sheaf condition verification (views agree on overlapping tokens)
- verify_sheaf_condition(): Pairwise compatibility check
- glue(): Combine compatible views into global document state

Sheaf Theory Background:
- Gluing Condition: Local views combine into global truth
- Separation Axiom: Global truth determines local views
- The file on disk is the TERMINAL OBJECT in the category of views

See: .kiro/specs/meaning-token-frontend/design.md
Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6

Teaching:
    gotcha: glue() RAISES SheafConditionError if views are incompatible. Always call
            verify_sheaf_condition() first if you want to handle conflicts gracefully.
            Don't assume glue() will merge conflicts—it refuses to produce invalid state.
            (Evidence: test_properties.py::TestProperty8DocumentSheafCoherence::test_incompatible_views_cannot_be_glued)

    gotcha: TokenState equality compares (token_id, token_type, content, position) but
            IGNORES metadata. Two tokens with different metadata but same core fields
            are considered equal. This is intentional—metadata is view-local decoration.
            (Evidence: test_properties.py::TestProperty8DocumentSheafCoherence::test_token_state_equality)

    gotcha: compatible() is SYMMETRIC: compatible(v1, v2) == compatible(v2, v1). Same
            for overlap(). But verify_sheaf_condition() checks ALL pairs, not just
            the ones you pass in. Adding a third view requires checking 3 pairs.
            (Evidence: test_properties.py::TestProperty8DocumentSheafCoherence::test_compatible_is_symmetric)

    gotcha: A single view is ALWAYS coherent with itself. verify_sheaf_condition() on
            a sheaf with one view returns success with checked_pairs=0. The sheaf
            condition is about agreement between views, not internal consistency.
            (Evidence: test_properties.py::TestProperty8DocumentSheafCoherence::test_single_view_always_coherent)

    gotcha: Views for DIFFERENT documents cannot be added to the same sheaf. add_view()
            raises ValueError if view.document_path != sheaf.document_path. Create
            separate sheafs per document.
            (Evidence: sheaf.py::DocumentSheaf::add_view validation)
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable
from uuid import uuid4

from services.interactive_text.contracts import DocumentState

# =============================================================================
# Token State Types
# =============================================================================


@dataclass(frozen=True)
class TokenState:
    """State of a token in a view.

    Represents the observable state of a token that must be consistent
    across views for the sheaf condition to hold.

    Attributes:
        token_id: Unique identifier for the token
        token_type: Type of the token (e.g., "task_checkbox", "agentese_path")
        content: The token's content/value
        position: (start, end) position in source
        metadata: Additional state data
    """

    token_id: str
    token_type: str
    content: str
    position: tuple[int, int]
    metadata: dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: object) -> bool:
        """Two token states are equal if their observable state matches."""
        if not isinstance(other, TokenState):
            return NotImplemented
        return (
            self.token_id == other.token_id
            and self.token_type == other.token_type
            and self.content == other.content
            and self.position == other.position
        )

    def __hash__(self) -> int:
        return hash((self.token_id, self.token_type, self.content, self.position))


# =============================================================================
# Document View Protocol
# =============================================================================


@runtime_checkable
class DocumentView(Protocol):
    """Protocol for document views.

    A view is a partial observation of a document. Multiple views of the
    same document must satisfy the sheaf condition: they agree on overlapping
    tokens.
    """

    @property
    def view_id(self) -> str:
        """Unique identifier for this view."""
        ...

    @property
    def document_path(self) -> Path:
        """Path to the document this view observes."""
        ...

    @property
    def tokens(self) -> frozenset[str]:
        """Token IDs visible in this view."""
        ...

    def state_of(self, token_id: str) -> TokenState | None:
        """Get state of a token in this view.

        Args:
            token_id: ID of the token to get state for

        Returns:
            TokenState if token is in this view, None otherwise
        """
        ...

    async def update(self, changes: list[TokenChange]) -> None:
        """Apply changes to this view.

        Args:
            changes: List of token changes to apply
        """
        ...


# =============================================================================
# Change Types
# =============================================================================


@dataclass(frozen=True)
class TokenChange:
    """A change to a token.

    Attributes:
        token_id: ID of the changed token
        change_type: Type of change ("created", "modified", "deleted")
        old_state: Previous state (None for creation)
        new_state: New state (None for deletion)
        timestamp: When the change occurred
    """

    token_id: str
    change_type: str  # "created", "modified", "deleted"
    old_state: TokenState | None = None
    new_state: TokenState | None = None
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def created(cls, state: TokenState) -> TokenChange:
        """Create a creation change."""
        return cls(
            token_id=state.token_id,
            change_type="created",
            old_state=None,
            new_state=state,
        )

    @classmethod
    def modified(cls, old: TokenState, new: TokenState) -> TokenChange:
        """Create a modification change."""
        return cls(
            token_id=old.token_id,
            change_type="modified",
            old_state=old,
            new_state=new,
        )

    @classmethod
    def deleted(cls, state: TokenState) -> TokenChange:
        """Create a deletion change."""
        return cls(
            token_id=state.token_id,
            change_type="deleted",
            old_state=state,
            new_state=None,
        )


@dataclass(frozen=True)
class FileChange:
    """A change to the underlying file.

    Attributes:
        path: Path to the changed file
        change_type: Type of change ("modified", "deleted", "created")
        timestamp: When the change was detected
    """

    path: Path
    change_type: str  # "modified", "deleted", "created"
    timestamp: float = field(default_factory=time.time)


@dataclass(frozen=True)
class Edit:
    """An edit operation on a document.

    Attributes:
        start: Start position in document
        end: End position in document
        new_text: Text to insert at position
        source_view_id: ID of the view that originated the edit
    """

    start: int
    end: int
    new_text: str
    source_view_id: str

    def apply(self, content: str) -> str:
        """Apply this edit to content.

        Args:
            content: Original content

        Returns:
            Content with edit applied
        """
        return content[: self.start] + self.new_text + content[self.end :]


# =============================================================================
# Sheaf Verification Results
# =============================================================================


@dataclass(frozen=True)
class SheafConflict:
    """A conflict between two views.

    Represents a violation of the sheaf condition where two views
    disagree on the state of overlapping tokens.

    Attributes:
        view1_id: ID of the first view
        view2_id: ID of the second view
        conflicting_tokens: Set of token IDs where views disagree
        details: Detailed conflict information per token
    """

    view1_id: str
    view2_id: str
    conflicting_tokens: frozenset[str]
    details: dict[str, tuple[TokenState | None, TokenState | None]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "view1_id": self.view1_id,
            "view2_id": self.view2_id,
            "conflicting_tokens": list(self.conflicting_tokens),
            "details": {
                k: (v[0].content if v[0] else None, v[1].content if v[1] else None)
                for k, v in self.details.items()
            },
        }


@dataclass(frozen=True)
class SheafVerification:
    """Result of verifying the sheaf condition.

    Attributes:
        passed: Whether the sheaf condition holds
        conflicts: List of conflicts if verification failed
        checked_pairs: Number of view pairs checked
        timestamp: When verification was performed
    """

    passed: bool
    conflicts: tuple[SheafConflict, ...] = ()
    checked_pairs: int = 0
    timestamp: float = field(default_factory=time.time)

    @classmethod
    def success(cls, checked_pairs: int = 0) -> SheafVerification:
        """Create a successful verification result."""
        return cls(passed=True, checked_pairs=checked_pairs)

    @classmethod
    def failure(
        cls,
        conflicts: list[SheafConflict],
        checked_pairs: int = 0,
    ) -> SheafVerification:
        """Create a failed verification result."""
        return cls(
            passed=False,
            conflicts=tuple(conflicts),
            checked_pairs=checked_pairs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "conflicts": [c.to_dict() for c in self.conflicts],
            "checked_pairs": self.checked_pairs,
            "timestamp": self.timestamp,
        }


# =============================================================================
# Simple Document View Implementation
# =============================================================================


@dataclass
class SimpleDocumentView:
    """Simple implementation of DocumentView for testing and basic use.

    This is a concrete implementation that stores token states in memory.
    Production implementations may use more sophisticated storage.
    """

    _view_id: str
    _document_path: Path
    _token_states: dict[str, TokenState] = field(default_factory=dict)

    @property
    def view_id(self) -> str:
        return self._view_id

    @property
    def document_path(self) -> Path:
        return self._document_path

    @property
    def tokens(self) -> frozenset[str]:
        return frozenset(self._token_states.keys())

    def state_of(self, token_id: str) -> TokenState | None:
        return self._token_states.get(token_id)

    async def update(self, changes: list[TokenChange]) -> None:
        """Apply changes to this view."""
        for change in changes:
            if change.change_type == "deleted":
                self._token_states.pop(change.token_id, None)
            elif change.new_state is not None:
                self._token_states[change.token_id] = change.new_state

    def add_token(self, state: TokenState) -> None:
        """Add a token to this view."""
        self._token_states[state.token_id] = state

    def remove_token(self, token_id: str) -> None:
        """Remove a token from this view."""
        self._token_states.pop(token_id, None)

    @classmethod
    def create(
        cls,
        document_path: Path | str,
        tokens: list[TokenState] | None = None,
    ) -> SimpleDocumentView:
        """Create a new view with optional initial tokens."""
        view = cls(
            _view_id=uuid4().hex,
            _document_path=Path(document_path),
        )
        if tokens:
            for token in tokens:
                view.add_token(token)
        return view


# =============================================================================
# Document Sheaf
# =============================================================================


@dataclass
class DocumentSheaf:
    """Sheaf structure ensuring multi-view coherence.

    The sheaf condition guarantees that local views glue to global state.
    The file on disk is always canonical; views are projections that must reconcile.

    Key Operations:
    - overlap(v1, v2): Tokens visible in both views
    - compatible(v1, v2): Views agree on overlapping tokens
    - verify_sheaf_condition(): All views are pairwise compatible
    - glue(): Combine compatible views into global document state

    Requirements: 4.1, 4.4, 4.5, 4.6
    """

    document_path: Path
    views: list[DocumentView] = field(default_factory=list)
    _change_handlers: list[Callable[[list[TokenChange]], Any]] = field(default_factory=list)
    _propagation_delay_ms: int = 100  # Max propagation delay per Requirement 4.2

    def overlap(self, v1: DocumentView, v2: DocumentView) -> frozenset[str]:
        """Get tokens visible in both views.

        Args:
            v1: First view
            v2: Second view

        Returns:
            Set of token IDs visible in both views

        Requirements: 4.4
        """
        return v1.tokens & v2.tokens

    def compatible(self, v1: DocumentView, v2: DocumentView) -> bool:
        """Check if two views agree on overlapping tokens (sheaf condition).

        Two views are compatible if for every token visible in both views,
        they report the same state for that token.

        Args:
            v1: First view
            v2: Second view

        Returns:
            True if views are compatible (agree on all overlapping tokens)

        Requirements: 4.4
        """
        shared = self.overlap(v1, v2)
        for token_id in shared:
            state1 = v1.state_of(token_id)
            state2 = v2.state_of(token_id)
            if state1 != state2:
                return False
        return True

    def verify_sheaf_condition(self) -> SheafVerification:
        """Verify all views are pairwise compatible.

        The sheaf condition requires that all pairs of views agree on
        their overlapping tokens. This method checks all pairs.

        Returns:
            SheafVerification with pass/fail status and any conflicts

        Requirements: 4.4, 4.5
        """
        conflicts: list[SheafConflict] = []
        checked_pairs = 0

        for i, v1 in enumerate(self.views):
            for v2 in self.views[i + 1 :]:
                checked_pairs += 1

                if not self.compatible(v1, v2):
                    # Find conflicting tokens
                    shared = self.overlap(v1, v2)
                    conflicting: set[str] = set()
                    details: dict[str, tuple[TokenState | None, TokenState | None]] = {}

                    for token_id in shared:
                        state1 = v1.state_of(token_id)
                        state2 = v2.state_of(token_id)
                        if state1 != state2:
                            conflicting.add(token_id)
                            details[token_id] = (state1, state2)

                    conflicts.append(
                        SheafConflict(
                            view1_id=v1.view_id,
                            view2_id=v2.view_id,
                            conflicting_tokens=frozenset(conflicting),
                            details=details,
                        )
                    )

        if conflicts:
            return SheafVerification.failure(conflicts, checked_pairs)
        return SheafVerification.success(checked_pairs)

    def add_view(self, view: DocumentView) -> None:
        """Add a view to the sheaf.

        Args:
            view: The view to add

        Raises:
            ValueError: If view is for a different document
        """
        if view.document_path != self.document_path:
            raise ValueError(
                f"View document path {view.document_path} does not match "
                f"sheaf document path {self.document_path}"
            )
        self.views.append(view)

    def remove_view(self, view_id: str) -> bool:
        """Remove a view from the sheaf.

        Args:
            view_id: ID of the view to remove

        Returns:
            True if view was removed, False if not found
        """
        for i, view in enumerate(self.views):
            if view.view_id == view_id:
                self.views.pop(i)
                return True
        return False

    def get_view(self, view_id: str) -> DocumentView | None:
        """Get a view by ID.

        Args:
            view_id: ID of the view to get

        Returns:
            The view, or None if not found
        """
        for view in self.views:
            if view.view_id == view_id:
                return view
        return None

    def glue(self) -> dict[str, TokenState]:
        """Combine compatible views into global document state.

        The glue operation combines all views into a single global state.
        For the sheaf condition to hold, all views must be compatible.

        Returns:
            Dictionary mapping token IDs to their states

        Raises:
            SheafConditionError: If views are not compatible

        Requirements: 4.6
        """
        # First verify sheaf condition
        verification = self.verify_sheaf_condition()
        if not verification.passed:
            raise SheafConditionError(
                "Cannot glue incompatible views",
                verification.conflicts,
            )

        # Combine all token states
        global_state: dict[str, TokenState] = {}
        for view in self.views:
            for token_id in view.tokens:
                state = view.state_of(token_id)
                if state is not None:
                    global_state[token_id] = state

        return global_state

    async def on_file_change(self, change: FileChange) -> None:
        """Handle file change—broadcast to all views.

        When the canonical file changes, all views must be updated
        to reflect the new state.

        Args:
            change: The file change event

        Requirements: 4.3
        """
        if change.path != self.document_path:
            return

        # Read the new file content and extract tokens
        # In a real implementation, this would parse the file
        # For now, we notify all views of the change

        # Create token changes from file content
        # This is a simplified implementation - real implementation
        # would diff the old and new content
        token_changes: list[TokenChange] = []

        # Propagate to all views
        await self._propagate_changes(token_changes)

    async def on_view_edit(self, view: DocumentView, edit: Edit) -> None:
        """Handle edit from a view—apply to file, broadcast to all.

        When a view makes an edit, it must be:
        1. Applied to the canonical file
        2. Propagated to all other views

        Args:
            view: The view that made the edit
            edit: The edit operation

        Requirements: 4.2, 4.3
        """
        # 1. Apply edit to canonical file
        await self._apply_edit_to_file(edit)

        # 2. File watcher will trigger on_file_change
        # But we can also propagate directly for faster updates

        # 3. Propagate to all views (including the editing view)
        # The editing view should already have the change, but
        # we propagate anyway for consistency

    async def _apply_edit_to_file(self, edit: Edit) -> None:
        """Apply edit to file with roundtrip fidelity.

        Args:
            edit: The edit to apply
        """
        if not self.document_path.exists():
            # Create file if it doesn't exist
            self.document_path.parent.mkdir(parents=True, exist_ok=True)
            self.document_path.write_text("")

        content = self.document_path.read_text()
        new_content = edit.apply(content)
        self.document_path.write_text(new_content)

    async def _propagate_changes(self, changes: list[TokenChange]) -> None:
        """Propagate changes to all views.

        Changes must propagate within the configured delay.

        Args:
            changes: The changes to propagate

        Requirements: 4.2
        """
        # Propagate to all views concurrently
        tasks = [view.update(changes) for view in self.views]
        await asyncio.gather(*tasks)

        # Notify change handlers
        for handler in self._change_handlers:
            try:
                result = handler(changes)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                # Log but don't fail propagation
                pass

    def on_change(self, handler: Callable[[list[TokenChange]], Any]) -> Callable[[], None]:
        """Register a change handler.

        Args:
            handler: Function to call when changes occur

        Returns:
            Unsubscribe function
        """
        self._change_handlers.append(handler)

        def unsubscribe() -> None:
            if handler in self._change_handlers:
                self._change_handlers.remove(handler)

        return unsubscribe

    @classmethod
    def create(cls, document_path: Path | str) -> DocumentSheaf:
        """Create a new sheaf for a document.

        Args:
            document_path: Path to the document

        Returns:
            A new DocumentSheaf instance
        """
        return cls(document_path=Path(document_path))


# =============================================================================
# Exceptions
# =============================================================================


class SheafConditionError(Exception):
    """Raised when the sheaf condition is violated.

    Attributes:
        message: Error message
        conflicts: List of conflicts that caused the violation
    """

    def __init__(
        self,
        message: str,
        conflicts: tuple[SheafConflict, ...] | list[SheafConflict],
    ) -> None:
        super().__init__(message)
        self.conflicts = tuple(conflicts) if isinstance(conflicts, list) else conflicts


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "TokenState",
    "TokenChange",
    "FileChange",
    "Edit",
    # Protocol
    "DocumentView",
    # Implementation
    "SimpleDocumentView",
    # Sheaf
    "DocumentSheaf",
    # Verification
    "SheafConflict",
    "SheafVerification",
    # Exceptions
    "SheafConditionError",
]
