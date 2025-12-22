"""
KBlock: The transactional editing container.

A K-Block is a pocket universe where you can edit freely without
affecting the cosmos until you explicitly commit.

Philosophy:
    "The K-Block is not where you edit a document. It's where you edit a possible world."

See: spec/protocols/k-block.md
"""

from __future__ import annotations

import difflib
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, NewType

if TYPE_CHECKING:
    from .cosmos import Cosmos

# -----------------------------------------------------------------------------
# Type Aliases
# -----------------------------------------------------------------------------

KBlockId = NewType("KBlockId", str)
ViewType = NewType("ViewType", str)

# Standard view types
VIEW_PROSE: ViewType = ViewType("prose")
VIEW_GRAPH: ViewType = ViewType("graph")
VIEW_CODE: ViewType = ViewType("code")
VIEW_DIFF: ViewType = ViewType("diff")
VIEW_OUTLINE: ViewType = ViewType("outline")
VIEW_TIMELINE: ViewType = ViewType("timeline")


def generate_kblock_id() -> KBlockId:
    """Generate a unique K-Block identifier."""
    return KBlockId(f"kb_{uuid.uuid4().hex[:12]}")


# -----------------------------------------------------------------------------
# Isolation States
# -----------------------------------------------------------------------------


class IsolationState(Enum):
    """
    K-Block isolation states.

    These determine what harness operations are valid and what
    UI indicators to show.
    """

    PRISTINE = auto()  # No local changes (base == content)
    DIRTY = auto()  # Has uncommitted changes
    STALE = auto()  # Upstream (cosmos) changed since creation
    CONFLICTING = auto()  # Both local and upstream changes
    ENTANGLED = auto()  # Linked to another K-Block


# -----------------------------------------------------------------------------
# Content Delta Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class EditDelta:
    """
    An atomic edit operation within a K-Block.

    Represents a single user action (insert, delete, replace).
    """

    operation: str  # "insert", "delete", "replace"
    position: int  # Character offset
    old_text: str = ""  # For delete/replace
    new_text: str = ""  # For insert/replace
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def serialize(self) -> dict[str, Any]:
        """Serialize for witness traces."""
        return {
            "operation": self.operation,
            "position": self.position,
            "old_text": self.old_text,
            "new_text": self.new_text,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> "EditDelta":
        """Deserialize from witness trace."""
        return cls(
            operation=data["operation"],
            position=data["position"],
            old_text=data.get("old_text", ""),
            new_text=data.get("new_text", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


@dataclass(frozen=True)
class ContentDelta:
    """
    The difference between two content states.

    Used for save operations to compute what changed.
    """

    old_content: str
    new_content: str
    unified_diff: str = field(default="", repr=False)

    @classmethod
    def compute(cls, old: str, new: str) -> "ContentDelta":
        """Compute delta between old and new content."""
        diff_lines = list(
            difflib.unified_diff(
                old.splitlines(keepends=True),
                new.splitlines(keepends=True),
                fromfile="base",
                tofile="edited",
            )
        )
        return cls(
            old_content=old,
            new_content=new,
            unified_diff="".join(diff_lines),
        )

    @property
    def has_changes(self) -> bool:
        """Whether there are any changes."""
        return self.old_content != self.new_content

    @property
    def additions(self) -> int:
        """Count of added lines."""
        return sum(
            1
            for line in self.unified_diff.split("\n")
            if line.startswith("+") and not line.startswith("+++")
        )

    @property
    def deletions(self) -> int:
        """Count of deleted lines."""
        return sum(
            1
            for line in self.unified_diff.split("\n")
            if line.startswith("-") and not line.startswith("---")
        )


# -----------------------------------------------------------------------------
# Checkpoint
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Checkpoint:
    """
    A named restore point within a K-Block.

    Checkpoints exist only within the K-Block's lifetime (not persisted to cosmos).
    """

    id: str
    name: str
    content: str
    content_hash: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, name: str, content: str) -> "Checkpoint":
        """Create a checkpoint from current content."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        return cls(
            id=f"cp_{uuid.uuid4().hex[:8]}",
            name=name,
            content=content,
            content_hash=content_hash,
        )


# -----------------------------------------------------------------------------
# KBlock
# -----------------------------------------------------------------------------


@dataclass
class KBlock:
    """
    Transactional editing container with hyperdimensional views.

    A K-Block is an isolated editing universe. FILE_OPERAD operations
    run inside it without affecting the cosmos. Only HARNESS_OPERAD
    operations (create, save, discard, fork, merge) cross the boundary.

    The K-Block forms a monad over Documents:
        return : Doc -> KBlock Doc     (create)
        bind   : KBlock Doc -> (Doc -> KBlock Doc) -> KBlock Doc
        join   : KBlock (KBlock Doc) -> KBlock Doc  (prohibited - no nesting)

    Philosophy:
        "Everything in the cosmos affects everything else.
         But inside the K-Block, you are sovereign."
    """

    # Identity
    id: KBlockId
    path: str  # Cosmos path (e.g., "spec/protocols/k-block.md")

    # Content
    content: str  # Current edited content
    base_content: str  # Content at K-Block creation (for diffing)

    # State
    isolation: IsolationState = IsolationState.PRISTINE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Temporal (checkpoints within K-Block lifetime)
    checkpoints: list[Checkpoint] = field(default_factory=list)

    # Views (hyperdimensional rendering - populated lazily)
    active_views: set[ViewType] = field(default_factory=set)

    # Entanglement (if ENTANGLED state)
    entangled_with: KBlockId | None = None

    # Reference to cosmos (set by harness)
    _cosmos: "Cosmos | None" = field(default=None, repr=False)

    # ---------------------------------------------------------------------
    # Content Operations
    # ---------------------------------------------------------------------

    def edit(self, delta: EditDelta) -> None:
        """
        Apply an edit to content.

        This is a local operation — no cosmic side effects.
        """
        if delta.operation == "insert":
            self.content = (
                self.content[: delta.position] + delta.new_text + self.content[delta.position :]
            )
        elif delta.operation == "delete":
            end = delta.position + len(delta.old_text)
            self.content = self.content[: delta.position] + self.content[end:]
        elif delta.operation == "replace":
            end = delta.position + len(delta.old_text)
            self.content = self.content[: delta.position] + delta.new_text + self.content[end:]

        self._mark_dirty()

    def set_content(self, new_content: str) -> None:
        """
        Replace content entirely.

        Convenience method for bulk updates.
        """
        if new_content != self.content:
            self.content = new_content
            self._mark_dirty()

    def _mark_dirty(self) -> None:
        """Update state after edit."""
        self.modified_at = datetime.now(timezone.utc)
        if self.isolation == IsolationState.PRISTINE:
            self.isolation = IsolationState.DIRTY
        elif self.isolation == IsolationState.STALE:
            self.isolation = IsolationState.CONFLICTING

    # ---------------------------------------------------------------------
    # Delta Computation
    # ---------------------------------------------------------------------

    def compute_delta(self) -> ContentDelta:
        """Compute delta between base and current content."""
        return ContentDelta.compute(self.base_content, self.content)

    @property
    def is_dirty(self) -> bool:
        """Whether content differs from base."""
        return self.content != self.base_content

    @property
    def content_hash(self) -> str:
        """SHA256 hash of current content (first 16 chars)."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]

    # ---------------------------------------------------------------------
    # Checkpoints
    # ---------------------------------------------------------------------

    def checkpoint(self, name: str) -> Checkpoint:
        """Create a named restore point."""
        cp = Checkpoint.create(name, self.content)
        self.checkpoints.append(cp)
        return cp

    def rewind(self, checkpoint_id: str) -> None:
        """Restore content to checkpoint state."""
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                self.content = cp.content
                self._mark_dirty()
                return
        raise ValueError(f"Checkpoint not found: {checkpoint_id}")

    def get_checkpoint(self, checkpoint_id: str) -> Checkpoint | None:
        """Get checkpoint by ID."""
        for cp in self.checkpoints:
            if cp.id == checkpoint_id:
                return cp
        return None

    # ---------------------------------------------------------------------
    # Monad Operations
    # ---------------------------------------------------------------------

    def bind(self, f: "Callable[[str], KBlock]") -> "KBlock":
        """
        Monadic bind: chain editing operations.

        Takes current content, applies f, returns resulting K-Block.
        Used for composing edit operations without escaping to cosmos.

        Note: The returned K-Block inherits this block's cosmos reference
        but has fresh state. This is how edit operations chain.
        """
        result = f(self.content)
        # Transfer cosmos reference
        result._cosmos = self._cosmos
        return result

    # ---------------------------------------------------------------------
    # State Queries
    # ---------------------------------------------------------------------

    def can_save(self) -> bool:
        """Whether save operation is valid."""
        return self.isolation in (IsolationState.DIRTY, IsolationState.PRISTINE)

    def can_discard(self) -> bool:
        """Whether discard operation is valid."""
        return self.isolation != IsolationState.ENTANGLED

    def can_fork(self) -> bool:
        """Whether fork operation is valid."""
        return True  # Always valid

    def needs_refresh(self) -> bool:
        """Whether upstream changes need attention."""
        return self.isolation in (IsolationState.STALE, IsolationState.CONFLICTING)

    # ---------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize K-Block state for persistence."""
        return {
            "id": self.id,
            "path": self.path,
            "content": self.content,
            "base_content": self.base_content,
            "isolation": self.isolation.name,
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
            "active_views": list(self.active_views),
            "entangled_with": self.entangled_with,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlock":
        """Deserialize K-Block from persisted state."""
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
            id=KBlockId(data["id"]),
            path=data["path"],
            content=data["content"],
            base_content=data["base_content"],
            isolation=IsolationState[data["isolation"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            checkpoints=checkpoints,
            active_views={ViewType(v) for v in data.get("active_views", [])},
            entangled_with=KBlockId(data["entangled_with"]) if data.get("entangled_with") else None,
        )

    # ---------------------------------------------------------------------
    # String Representation
    # ---------------------------------------------------------------------

    def __repr__(self) -> str:
        lines = len(self.content.split("\n"))
        return (
            f"KBlock(id={self.id!r}, path={self.path!r}, "
            f"isolation={self.isolation.name}, lines={lines}, "
            f"checkpoints={len(self.checkpoints)})"
        )


# Type alias for bind function
from typing import Callable  # noqa: E402
