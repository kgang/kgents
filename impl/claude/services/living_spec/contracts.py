"""
Living Spec Contracts: Shared types for the unified system.

Merges types from:
- services/interactive_text/contracts.py (Observer, Affordance, MeaningToken)
- services/k_block/core/kblock.py (IsolationState, EditDelta, ContentDelta)
- protocols/agentese/contexts/self_context.py (ContextNode edges)

All types are immutable (frozen dataclasses) for safe sharing.
"""

from __future__ import annotations

import difflib
import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, NewType, Protocol, runtime_checkable

# -----------------------------------------------------------------------------
# Identifiers
# -----------------------------------------------------------------------------

SpecId = NewType("SpecId", str)
VersionId = NewType("VersionId", str)
MarkId = NewType("MarkId", str)


def generate_spec_id() -> SpecId:
    """Generate unique spec identifier."""
    return SpecId(f"spec_{uuid.uuid4().hex[:12]}")


def generate_version_id() -> VersionId:
    """Generate unique version identifier."""
    return VersionId(f"v_{uuid.uuid4().hex[:12]}")


# -----------------------------------------------------------------------------
# Spec Classification
# -----------------------------------------------------------------------------


class SpecKind(Enum):
    """Classification of a spec node in the hypergraph."""

    SPEC = "spec"  # Specification document (in spec/)
    IMPLEMENTATION = "implementation"  # Implementation code (in impl/)
    TEST = "test"  # Test file (in _tests/)
    EVIDENCE = "evidence"  # Evidence/proof artifact


# -----------------------------------------------------------------------------
# Isolation States (from K-Block)
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
# Observer (from Interactive Text)
# -----------------------------------------------------------------------------


class ObserverDensity(Enum):
    """
    Display density preference.

    Affects how much information is shown in projections.
    """

    COMPACT = "compact"  # Minimal, glanceable
    COMFORTABLE = "comfortable"  # Balanced (default)
    SPACIOUS = "spacious"  # Full detail


class ObserverRole(Enum):
    """Observer archetype — affects what hyperedges are visible."""

    DEVELOPER = "developer"  # sees: tests, imports, calls, implements
    ARCHITECT = "architect"  # sees: dependencies, patterns, violations
    SECURITY_AUDITOR = "security_auditor"  # sees: auth_flows, vulnerabilities
    NEWCOMER = "newcomer"  # sees: docs, examples, related


@dataclass(frozen=True)
class Observer:
    """
    Entity receiving projections with specific umwelt.

    The observer determines:
    - Which hyperedges are visible (role)
    - How much detail to show (density)
    - What capabilities are available (capabilities)
    """

    id: str
    role: ObserverRole = ObserverRole.DEVELOPER
    density: ObserverDensity = ObserverDensity.COMFORTABLE
    capabilities: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def default(cls) -> "Observer":
        """Create default observer (developer, comfortable)."""
        return cls(
            id="default",
            role=ObserverRole.DEVELOPER,
            density=ObserverDensity.COMFORTABLE,
            capabilities=frozenset({"read", "write", "navigate"}),
        )


# -----------------------------------------------------------------------------
# Delta Types (from K-Block)
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


@dataclass(frozen=True)
class SemanticDelta:
    """
    A semantic change (token-level) rather than character-level.

    Used for witness traces to capture "what changed" meaningfully.
    """

    operation: str  # "add", "remove", "modify"
    token_id: str
    token_kind: str  # "agentese_path", "task_checkbox", "portal", etc.
    old_value: str | None = None
    new_value: str | None = None
    reasoning: str | None = None


# -----------------------------------------------------------------------------
# Result Types
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class CommitResult:
    """Result of committing a SpecMonad to cosmos."""

    version_id: VersionId
    mark_id: MarkId | None  # None if witness disabled
    path: str
    delta_summary: str  # e.g., "+15 -3 lines"

    @property
    def success(self) -> bool:
        """Whether commit succeeded."""
        return bool(self.version_id)


# -----------------------------------------------------------------------------
# Affordance (from Interactive Text)
# -----------------------------------------------------------------------------


class AffordanceAction(Enum):
    """Type of interaction an affordance enables."""

    CLICK = "click"
    HOVER = "hover"
    DRAG = "drag"
    EXPAND = "expand"  # Portal expansion
    TOGGLE = "toggle"  # Task checkbox
    NAVIGATE = "navigate"  # Follow hyperedge
    EDIT = "edit"  # Enter edit mode


@dataclass(frozen=True)
class Affordance:
    """
    An interaction possibility on a token.

    Affordances are observer-dependent — what you can do depends
    on your capabilities.
    """

    action: AffordanceAction
    label: str
    target: str | None = None  # AGENTESE path or URL
    enabled: bool = True
    tooltip: str | None = None


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
# Token Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class TokenProtocol(Protocol):
    """Protocol for all spec tokens."""

    @property
    def token_type(self) -> str:
        """Token type identifier."""
        ...

    @property
    def span(self) -> tuple[int, int]:
        """Character span (start, end) in source."""
        ...

    def affordance(self, observer: Observer) -> Affordance | None:
        """Get primary affordance for this observer."""
        ...

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        ...
