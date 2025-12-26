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
from typing import TYPE_CHECKING, Any, NewType, cast

if TYPE_CHECKING:
    from ..views.base import View
    from .cosmos import Cosmos
    from .edge import KBlockEdge
    from .sheaf import KBlockSheaf
    from .verification import SheafVerification

# -----------------------------------------------------------------------------
# Type Aliases
# -----------------------------------------------------------------------------

KBlockId = NewType("KBlockId", str)


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
# K-Block Kind (Unification: Everything is an Agent)
# -----------------------------------------------------------------------------


class KBlockKind(Enum):
    """
    K-Block content taxonomy: Everything is an Agent represented as a K-Block.

    The Radical Insight:
        Agent ≅ K-Block ≅ ZeroNode ≅ File ≅ Upload ≅ Crystal

    This enum captures the morphism type in the category of Content.
    Every K-Block is a morphism: A → B where:
        - Source (A): The origin/context of the content
        - Target (B): The manifestation in the cosmos

    Kind Taxonomy:
        FILE: Traditional filesystem content (specs, implementations)
        UPLOAD: User-uploaded sovereign content
        ZERO_NODE: Zero Seed axiom/value/goal/spec/action/reflection/representation
        AGENT_STATE: Serialized agent state (PolyAgent positions)
        CRYSTAL: Crystallized memory/decision (Witness crystals)

    Category-Theoretic Grounding:
        Each kind forms a subcategory of the K-Block category.
        The inclusion functors preserve composition and identity.

    See: spec/protocols/kblock-unification.md
    """

    FILE = "file"  # Traditional filesystem content
    UPLOAD = "upload"  # User-uploaded content (sovereign)
    ZERO_NODE = "zero_node"  # Zero Seed node (L1-L7)
    AGENT_STATE = "agent_state"  # Serialized agent polynomial state
    CRYSTAL = "crystal"  # Crystallized memory/decision from Witness

    @property
    def is_sovereign(self) -> bool:
        """Whether this kind requires sovereign store."""
        return self in {KBlockKind.UPLOAD, KBlockKind.CRYSTAL}

    @property
    def is_structural(self) -> bool:
        """Whether this kind participates in the Zero Seed hierarchy."""
        return self == KBlockKind.ZERO_NODE

    @property
    def requires_witnessing(self) -> bool:
        """Whether modifications require witness marks."""
        return self in {KBlockKind.ZERO_NODE, KBlockKind.CRYSTAL, KBlockKind.UPLOAD}

    def to_agentese_context(self) -> str:
        """Map kind to AGENTESE context prefix."""
        mapping = {
            KBlockKind.FILE: "world",
            KBlockKind.UPLOAD: "world",
            KBlockKind.ZERO_NODE: "void",  # Zero nodes can be void/concept depending on layer
            KBlockKind.AGENT_STATE: "self",
            KBlockKind.CRYSTAL: "time",
        }
        return mapping[self]


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

    UNIFICATION PRINCIPLE (AD-010):
        Everything is an Agent, and every Agent can be represented as a K-Block.

        The isomorphism:
            KBlock ≅ Agent ≅ ZeroNode ≅ File ≅ Upload ≅ Crystal

        This dataclass is the UNIFIED representation across all content types.
        The `kind` field determines the morphism type in the category of Content.

    Philosophy:
        "Everything in the cosmos affects everything else.
         But inside the K-Block, you are sovereign."

    See: spec/protocols/kblock-unification.md
    """

    # Identity
    id: KBlockId
    path: str  # Cosmos path (e.g., "spec/protocols/k-block.md")

    # Content
    content: str  # Current edited content
    base_content: str  # Content at K-Block creation (for diffing)

    # Kind (Unification: Everything is an Agent)
    # Placed after required fields to maintain dataclass field ordering
    kind: KBlockKind = KBlockKind.FILE  # Default to FILE for backward compatibility

    # State
    isolation: IsolationState = IsolationState.PRISTINE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Temporal (checkpoints within K-Block lifetime)
    checkpoints: list[Checkpoint] = field(default_factory=list)

    # Views (hyperdimensional rendering - populated lazily)
    # Uses dict to store View instances keyed by ViewType enum
    _views: dict[Any, Any] = field(default_factory=dict, repr=False)

    # Entanglement (if ENTANGLED state)
    entangled_with: KBlockId | None = None

    # Reference to cosmos (set by harness)
    _cosmos: "Cosmos | None" = field(default=None, repr=False)

    # Sovereignty indicator: True if content not found in cosmos or sovereign store
    # Frontend should show "not ingested" UI when this is True
    not_ingested: bool = False

    # Analysis gating: True if entity exists but hasn't been analyzed
    # K-Block should be read-only until analysis_required is False
    analysis_required: bool = False

    # -------------------------------------------------------------------------
    # Zero Seed Integration (Phase 1: K-Block/Document Unification)
    # -------------------------------------------------------------------------

    # Zero Seed layer (1-7) if this K-Block represents a Zero Seed node
    zero_seed_layer: int | None = None  # 1=axiom, 2=value, 3=goal, 4=spec, 5=action, 6=reflection, 7=representation

    # Zero Seed kind (human-readable category)
    zero_seed_kind: str | None = None  # "axiom", "value", "goal", "spec", "action", "reflection", "representation"

    # Lineage: parent node IDs (forms the derivation DAG)
    # For a node N, lineage contains IDs of nodes that N derives from
    lineage: list[str] = field(default_factory=list)

    # Proof tracking
    has_proof: bool = False
    toulmin_proof: dict[str, Any] | None = None  # Toulmin proof structure (claim, warrant, backing, etc.)

    # Confidence in this Zero Seed node [0.0, 1.0]
    confidence: float = 1.0

    # Edge tracking (bidirectional for efficient traversal)
    incoming_edges: list["KBlockEdge"] = field(default_factory=list)
    outgoing_edges: list["KBlockEdge"] = field(default_factory=list)

    # -------------------------------------------------------------------------
    # Genesis Feed Integration (P0: K-Block Schema Extension)
    # -------------------------------------------------------------------------

    # Coherence metric: Galois connection loss [0.0, 1.0]
    # 0.0 = perfect coherence (all views agree)
    # 1.0 = complete incoherence (views contradict)
    galois_loss: float = 0.0

    # Author/origin tracking
    created_by: str | None = None

    # Classification tags for filtering/grouping
    tags: list[str] = field(default_factory=list)

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

    def is_zero_seed_node(self) -> bool:
        """
        Check if this K-Block represents a Zero Seed node.

        Zero Seed nodes have a layer (1-7) and kind (axiom, value, etc.).
        Regular file K-Blocks have zero_seed_layer=None.

        Returns:
            True if this is a Zero Seed node, False for regular files
        """
        return self.zero_seed_layer is not None

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
    # Views (Hyperdimensional Rendering)
    # ---------------------------------------------------------------------

    @property
    def views(self) -> dict[Any, Any]:
        """Return active views dict."""
        return self._views

    def activate_view(self, view_type: Any) -> "View":
        """
        Activate a view and render current content.

        Views are created lazily on first activation. The view
        is rendered with current content and cached for reuse.

        Args:
            view_type: ViewType enum value (PROSE, GRAPH, CODE, etc.)

        Returns:
            The activated View instance
        """
        from ..views.base import View as ViewProtocol, ViewType as VT, create_view

        if view_type not in self._views:
            self._views[view_type] = create_view(view_type)

        # Handle view-specific rendering
        if view_type == VT.DIFF:
            self._views[view_type].render(self.content, self.base_content)
        elif view_type == VT.REFERENCES:
            self._views[view_type].render(self.content, spec_path=self.path)
        else:
            self._views[view_type].render(self.content)

        return cast("ViewProtocol", self._views[view_type])

    def refresh_views(self) -> None:
        """
        Re-render all active views with current content.

        Called after content changes to keep views in sync.
        For Prose-canonical model, other views derive from prose.
        """
        from ..views.base import ViewType as VT

        for view_type, view in self._views.items():
            if view_type == VT.DIFF:
                # Diff view needs base_content too
                view.render(self.content, self.base_content)
            elif view_type == VT.REFERENCES:
                # References view needs spec_path for discovery
                view.render(self.content, spec_path=self.path)
            else:
                view.render(self.content)

    def active_view_types(self) -> set[Any]:
        """Return set of currently active view types."""
        return set(self._views.keys())

    # ---------------------------------------------------------------------
    # Sheaf Operations
    # ---------------------------------------------------------------------

    @property
    def sheaf(self) -> "KBlockSheaf":
        """
        Get sheaf for this K-Block.

        The sheaf provides operations for verifying view coherence
        and propagating changes across views.

        Returns:
            KBlockSheaf instance bound to this K-Block
        """
        from .sheaf import KBlockSheaf

        return KBlockSheaf(self)

    def verify_coherence(self) -> "SheafVerification":
        """
        Verify all active views are coherent.

        Convenience method that delegates to sheaf.verify_sheaf_condition().

        Returns:
            SheafVerification with detailed results
        """
        return self.sheaf.verify_sheaf_condition()

    # ---------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize K-Block state for persistence."""
        result: dict[str, Any] = {
            "id": self.id,
            "path": self.path,
            "kind": self.kind.value,  # Unification: Always serialize kind
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
            "active_views": [vt.value for vt in self._views.keys()],
            "entangled_with": self.entangled_with,
        }

        # Zero Seed fields (only if this is a Zero Seed node)
        if self.is_zero_seed_node():
            result["zero_seed_layer"] = self.zero_seed_layer
            result["zero_seed_kind"] = self.zero_seed_kind
            result["lineage"] = self.lineage
            result["has_proof"] = self.has_proof
            result["toulmin_proof"] = self.toulmin_proof
            result["confidence"] = self.confidence
            # Serialize edges
            result["incoming_edges"] = [edge.to_dict() for edge in self.incoming_edges]
            result["outgoing_edges"] = [edge.to_dict() for edge in self.outgoing_edges]

        # Genesis feed fields (always serialized)
        result["galois_loss"] = self.galois_loss
        result["created_by"] = self.created_by
        result["tags"] = self.tags

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KBlock":
        """Deserialize K-Block from persisted state."""
        from .edge import KBlockEdge

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

        # Deserialize edges if present
        incoming_edges = [
            KBlockEdge.from_dict(edge_data)
            for edge_data in data.get("incoming_edges", [])
        ]
        outgoing_edges = [
            KBlockEdge.from_dict(edge_data)
            for edge_data in data.get("outgoing_edges", [])
        ]

        # Parse kind with backward compatibility (default to FILE)
        kind_str = data.get("kind", "file")
        try:
            kind = KBlockKind(kind_str)
        except ValueError:
            kind = KBlockKind.FILE  # Fallback for unknown kinds

        return cls(
            id=KBlockId(data["id"]),
            path=data["path"],
            content=data["content"],
            base_content=data["base_content"],
            kind=kind,  # Unification: Deserialize kind
            isolation=IsolationState[data["isolation"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=datetime.fromisoformat(data["modified_at"]),
            checkpoints=checkpoints,
            # Note: active_views is stored as list of strings, but we don't
            # restore View instances on deserialize - they're recreated on demand
            entangled_with=KBlockId(data["entangled_with"]) if data.get("entangled_with") else None,
            # Zero Seed fields
            zero_seed_layer=data.get("zero_seed_layer"),
            zero_seed_kind=data.get("zero_seed_kind"),
            lineage=data.get("lineage", []),
            has_proof=data.get("has_proof", False),
            toulmin_proof=data.get("toulmin_proof"),
            confidence=data.get("confidence", 1.0),
            incoming_edges=incoming_edges,
            outgoing_edges=outgoing_edges,
            # Genesis feed fields
            galois_loss=data.get("galois_loss", 0.0),
            created_by=data.get("created_by"),
            tags=data.get("tags", []),
        )

    # ---------------------------------------------------------------------
    # String Representation
    # ---------------------------------------------------------------------

    def __repr__(self) -> str:
        lines = len(self.content.split("\n"))
        return (
            f"KBlock(id={self.id!r}, kind={self.kind.value}, path={self.path!r}, "
            f"isolation={self.isolation.name}, lines={lines}, "
            f"checkpoints={len(self.checkpoints)})"
        )


# Type alias for bind function
from typing import Callable  # noqa: E402


# =============================================================================
# Unification: KBlock ≅ ZeroNode Isomorphism
# =============================================================================


def kblock_from_zero_node(
    node: "ZeroNode",
    *,
    base_content: str | None = None,
) -> KBlock:
    """
    Convert a ZeroNode to a KBlock (isomorphism left-to-right).

    This implements the categorical insight:
        Agent ≅ K-Block ≅ ZeroNode

    The ZeroNode's layer and kind map to K-Block's zero_seed_* fields.
    The unified kind is always ZERO_NODE.

    Args:
        node: The ZeroNode to convert
        base_content: Optional base content (defaults to node.content)

    Returns:
        KBlock representing the ZeroNode

    Example:
        >>> from services.zero_seed.core import ZeroNode
        >>> node = ZeroNode(path="void.axiom.entity", layer=1, kind="axiom", ...)
        >>> kblock = kblock_from_zero_node(node)
        >>> assert kblock.kind == KBlockKind.ZERO_NODE
        >>> assert kblock.zero_seed_layer == 1
    """
    # Import here to avoid circular dependency
    from services.zero_seed.core import ZeroNode as ZN

    if not isinstance(node, ZN):
        raise TypeError(f"Expected ZeroNode, got {type(node)}")

    content = node.content
    base = base_content if base_content is not None else content

    # Map lineage from tuple of NodeId to list of strings
    lineage_list = [str(lid) for lid in node.lineage]

    # Map proof to dict if present
    toulmin_proof = node.proof.to_dict() if node.proof else None

    return KBlock(
        id=generate_kblock_id(),
        path=node.path,
        kind=KBlockKind.ZERO_NODE,
        content=content,
        base_content=base,
        # Zero Seed specific fields
        zero_seed_layer=node.layer,
        zero_seed_kind=node.kind,
        lineage=lineage_list,
        has_proof=node.proof is not None,
        toulmin_proof=toulmin_proof,
        confidence=node.confidence,
        # Metadata
        created_by=node.created_by,
        tags=list(node.tags),
    )


def zero_node_from_kblock(kblock: KBlock) -> "ZeroNode":
    """
    Convert a KBlock to a ZeroNode (isomorphism right-to-left).

    This implements the categorical insight:
        Agent ≅ K-Block ≅ ZeroNode

    Only K-Blocks with kind=ZERO_NODE can be converted.
    For other kinds, use appropriate converters.

    Args:
        kblock: The KBlock to convert (must have kind=ZERO_NODE)

    Returns:
        ZeroNode derived from the KBlock

    Raises:
        ValueError: If kblock.kind is not ZERO_NODE

    Example:
        >>> kblock = KBlock(kind=KBlockKind.ZERO_NODE, zero_seed_layer=1, ...)
        >>> node = zero_node_from_kblock(kblock)
        >>> assert node.layer == 1
    """
    # Import here to avoid circular dependency
    from services.zero_seed.core import NodeId, Proof, ZeroNode

    if kblock.kind != KBlockKind.ZERO_NODE:
        raise ValueError(
            f"Cannot convert KBlock with kind={kblock.kind} to ZeroNode. "
            f"Expected kind=ZERO_NODE."
        )

    if kblock.zero_seed_layer is None:
        raise ValueError(
            "Cannot convert KBlock to ZeroNode: zero_seed_layer is None"
        )

    # Parse proof if present
    proof = None
    if kblock.toulmin_proof:
        proof = Proof.from_dict(kblock.toulmin_proof)

    # Map lineage from list of strings to tuple of NodeId
    lineage_tuple = tuple(NodeId(lid) for lid in kblock.lineage)

    return ZeroNode(
        path=kblock.path,
        layer=kblock.zero_seed_layer,
        kind=kblock.zero_seed_kind or "",
        content=kblock.content,
        title=kblock.path.split(".")[-1] if "." in kblock.path else kblock.path,
        proof=proof,
        confidence=kblock.confidence,
        created_at=kblock.created_at,
        created_by=kblock.created_by or "system",
        lineage=lineage_tuple,
        tags=frozenset(kblock.tags),
    )


# Type hint for ZeroNode (deferred import)
if TYPE_CHECKING:
    from services.zero_seed.core import ZeroNode
