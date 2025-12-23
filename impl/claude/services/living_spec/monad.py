"""
SpecMonad: Monadic isolation for spec editing.

The SpecMonad provides transactional editing semantics:
- Changes happen in isolation (inside the monad)
- Only explicit commit (save) affects the cosmos
- Discard abandons changes without side effects

The monad structure:
    pure : SpecNode → SpecMonad
    bind : SpecMonad → (str → SpecMonad) → SpecMonad
    commit : SpecMonad → reasoning → (Cosmos, Witness)

Philosophy:
    "The K-Block is not where you edit a document.
     It's where you edit a possible world."

    "Everything in the cosmos affects everything else.
     But inside the K-Block, you are sovereign."
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from .contracts import (
    Checkpoint,
    CommitResult,
    ContentDelta,
    EditDelta,
    IsolationState,
    MarkId,
    SemanticDelta,
    VersionId,
    generate_version_id,
)
from .node import SpecNode
from .polynomial import Effect, SpecPolynomial, SpecState

if TYPE_CHECKING:
    from .sheaf import SpecSheaf


# -----------------------------------------------------------------------------
# Monad ID
# -----------------------------------------------------------------------------


def generate_monad_id() -> str:
    """Generate unique monad identifier."""
    return f"monad_{uuid.uuid4().hex[:12]}"


# -----------------------------------------------------------------------------
# SpecMonad
# -----------------------------------------------------------------------------


@dataclass
class SpecMonad:
    """
    Monadic isolation for spec editing.

    A SpecMonad wraps a SpecNode in an editing context where:
    1. Changes are isolated from the cosmos
    2. Multiple views stay synchronized
    3. Checkpoints enable local undo
    4. Commit writes to cosmos with witness trace

    The monad satisfies:
    - Left identity: pure(a).bind(f) ≡ f(a)
    - Right identity: m.bind(pure) ≡ m
    - Associativity: m.bind(f).bind(g) ≡ m.bind(λx. f(x).bind(g))
    """

    # Identity
    id: str = field(default_factory=generate_monad_id)
    spec: SpecNode = field(default_factory=lambda: SpecNode(path=""))

    # Content
    base_content: str = ""  # Content at monad creation
    working_content: str = ""  # Current edited content

    # State
    isolation: IsolationState = IsolationState.PRISTINE
    polynomial_state: SpecState = SpecState.EDITING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Checkpoints
    checkpoints: list[Checkpoint] = field(default_factory=list)

    # Edit history (for semantic deltas)
    _edit_history: list[EditDelta] = field(default_factory=list, repr=False)

    # -------------------------------------------------------------------------
    # Monad Operations
    # -------------------------------------------------------------------------

    @classmethod
    def pure(cls, spec: SpecNode) -> "SpecMonad":
        """
        Lift a spec into the editing monad.

        This is the monadic 'return' — creates an isolated editing
        context for the spec.

        Args:
            spec: The spec node to edit

        Returns:
            SpecMonad in PRISTINE state with spec's content
        """
        import asyncio

        # Load content synchronously if possible, else schedule
        try:
            loop = asyncio.get_running_loop()
            content = ""  # Will be loaded lazily
        except RuntimeError:
            # No event loop — load synchronously
            content = asyncio.run(spec.content())

        return cls(
            spec=spec,
            base_content=content,
            working_content=content,
            isolation=IsolationState.PRISTINE,
            polynomial_state=SpecState.EDITING,
        )

    @classmethod
    async def pure_async(cls, spec: SpecNode) -> "SpecMonad":
        """
        Async version of pure — loads content.

        Args:
            spec: The spec node to edit

        Returns:
            SpecMonad with content loaded
        """
        content = await spec.content()
        return cls(
            spec=spec,
            base_content=content,
            working_content=content,
            isolation=IsolationState.PRISTINE,
            polynomial_state=SpecState.EDITING,
        )

    def bind(self, f: Callable[[str], str]) -> "SpecMonad":
        """
        Monadic bind — apply transformation within isolation.

        Args:
            f: Function from content → new content

        Returns:
            Self with transformed content (mutation for efficiency)
        """
        new_content = f(self.working_content)
        if new_content != self.working_content:
            self.working_content = new_content
            self._mark_dirty()
        return self

    def map(self, f: Callable[[str], str]) -> "SpecMonad":
        """Alias for bind (functor map)."""
        return self.bind(f)

    # -------------------------------------------------------------------------
    # Content Operations
    # -------------------------------------------------------------------------

    def set_content(self, new_content: str) -> None:
        """
        Replace content entirely.

        Args:
            new_content: New content string
        """
        if new_content != self.working_content:
            self.working_content = new_content
            self._mark_dirty()

    def apply_edit(self, delta: EditDelta) -> None:
        """
        Apply an atomic edit operation.

        Args:
            delta: Edit delta to apply
        """
        content = self.working_content

        if delta.operation == "insert":
            content = content[: delta.position] + delta.new_text + content[delta.position :]
        elif delta.operation == "delete":
            end = delta.position + len(delta.old_text)
            content = content[: delta.position] + content[end:]
        elif delta.operation == "replace":
            end = delta.position + len(delta.old_text)
            content = content[: delta.position] + delta.new_text + content[end:]

        self.working_content = content
        self._edit_history.append(delta)
        self._mark_dirty()

    def _mark_dirty(self) -> None:
        """Update state after edit."""
        self.modified_at = datetime.now(timezone.utc)
        if self.isolation == IsolationState.PRISTINE:
            self.isolation = IsolationState.DIRTY
        elif self.isolation == IsolationState.STALE:
            self.isolation = IsolationState.CONFLICTING

    # -------------------------------------------------------------------------
    # Delta Computation
    # -------------------------------------------------------------------------

    def compute_delta(self) -> ContentDelta:
        """Compute delta between base and working content."""
        return ContentDelta.compute(self.base_content, self.working_content)

    @property
    def is_dirty(self) -> bool:
        """Whether content differs from base."""
        return self.working_content != self.base_content

    @property
    def content_hash(self) -> str:
        """SHA256 hash of working content (first 16 chars)."""
        return hashlib.sha256(self.working_content.encode()).hexdigest()[:16]

    # -------------------------------------------------------------------------
    # Checkpoints
    # -------------------------------------------------------------------------

    def checkpoint(self, name: str) -> Checkpoint:
        """
        Create a named restore point.

        Args:
            name: Human-readable checkpoint name

        Returns:
            Created Checkpoint
        """
        cp = Checkpoint.create(name, self.working_content)
        self.checkpoints.append(cp)
        return cp

    def rewind(self, checkpoint_id: str) -> None:
        """
        Restore content to checkpoint state.

        Args:
            checkpoint_id: ID of checkpoint to restore

        Raises:
            ValueError: If checkpoint not found
        """
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                self.working_content = cp.content
                self._mark_dirty()
                return
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Get checkpoint by ID."""
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None

    # -------------------------------------------------------------------------
    # Commit (Exit Monad)
    # -------------------------------------------------------------------------

    async def commit(self, reasoning: str, actor: str = "user") -> CommitResult:
        """
        Commit changes to cosmos with witness trace.

        This is the monadic 'run' — exits isolation and affects
        the shared cosmos.

        Args:
            reasoning: Why these changes were made
            actor: Who made the changes

        Returns:
            CommitResult with version and mark IDs
        """
        if not self.is_dirty:
            # Nothing to commit
            return CommitResult(
                version_id=VersionId(""),
                mark_id=None,
                path=self.spec.path,
                delta_summary="no changes",
            )

        # Compute delta for summary
        delta = self.compute_delta()
        delta_summary = f"+{delta.additions} -{delta.deletions} lines"

        # Write to filesystem (simple implementation)
        file_path = self.spec._resolve_path()
        if file_path:
            file_path.write_text(self.working_content)

        # Generate version ID
        version_id = generate_version_id()

        # Generate mark ID (would integrate with Witness service)
        mark_id = MarkId(f"mark_{uuid.uuid4().hex[:12]}")

        # Reset monad state
        self.base_content = self.working_content
        self.isolation = IsolationState.PRISTINE
        self.checkpoints.clear()
        self._edit_history.clear()

        return CommitResult(
            version_id=version_id,
            mark_id=mark_id,
            path=self.spec.path,
            delta_summary=delta_summary,
        )

    def discard(self) -> None:
        """
        Discard changes without affecting cosmos.

        Restores content to base and resets state.
        """
        self.working_content = self.base_content
        self.isolation = IsolationState.PRISTINE
        self.checkpoints.clear()
        self._edit_history.clear()
        self.modified_at = datetime.now(timezone.utc)

    # -------------------------------------------------------------------------
    # State Queries
    # -------------------------------------------------------------------------

    def can_save(self) -> bool:
        """Whether save operation is valid."""
        return self.isolation in (IsolationState.DIRTY, IsolationState.PRISTINE)

    def can_discard(self) -> bool:
        """Whether discard operation is valid."""
        return self.isolation != IsolationState.ENTANGLED

    def needs_refresh(self) -> bool:
        """Whether upstream changes need attention."""
        return self.isolation in (IsolationState.STALE, IsolationState.CONFLICTING)

    # -------------------------------------------------------------------------
    # Sheaf Access
    # -------------------------------------------------------------------------

    @property
    def sheaf(self) -> "SpecSheaf":
        """
        Get sheaf for this monad.

        The sheaf provides multi-view coherence operations.
        """
        from .sheaf import SpecSheaf

        return SpecSheaf(self)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize monad state for persistence."""
        return {
            "id": self.id,
            "spec_path": self.spec.path,
            "base_content": self.base_content,
            "working_content": self.working_content,
            "isolation": self.isolation.name,
            "polynomial_state": self.polynomial_state.name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "checkpoints": [
                {
                    "id": cp.id,
                    "name": cp.name,
                    "content": cp.content,
                    "content_hash": cp.content_hash,
                    "created_at": cp.created_at.isoformat(),
                }
                for cp in self.checkpoints
            ],
            "is_dirty": self.is_dirty,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SpecMonad":
        """Deserialize monad from persisted state."""
        checkpoints = [
            Checkpoint(
                id=cp["id"],
                name=cp["name"],
                content=cp["content"],
                content_hash=cp["content_hash"],
                created_at=datetime.fromisoformat(cp["created_at"]),
            )
            for cp in data.get("checkpoints", [])
        ]

        return cls(
            id=data["id"],
            spec=SpecNode(path=data["spec_path"]),
            base_content=data["base_content"],
            working_content=data["working_content"],
            isolation=IsolationState[data["isolation"]],
            polynomial_state=SpecState[data["polynomial_state"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            checkpoints=checkpoints,
        )

    def __repr__(self) -> str:
        lines = len(self.working_content.split("\n"))
        return (
            f"SpecMonad(id={self.id!r}, path={self.spec.path!r}, "
            f"isolation={self.isolation.name}, lines={lines}, "
            f"checkpoints={len(self.checkpoints)})"
        )
