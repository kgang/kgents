"""
Sovereign Types: Core data structures for Inbound Sovereignty.

These types model the flow of documents across the membrane:

    EXTERNAL ──► IngestEvent ──► SovereignEntity ──► IngestedEntity
                  │                   │
                  │                   └─► Overlay (annotations, edges)
                  │                   └─► Versions (v1, v2, ...)
                  └─► Mark (birth certificate)

Teaching:
    gotcha: IngestEvent.content is bytes, not str. We preserve exact bytes
            for content-addressable hashing. Decode only when needed.

    gotcha: SovereignEntity.overlay is a dict, not a nested structure.
            Keys like "annotations", "edges" map to JSON-serializable data.
            Derived data goes in overlay["derived"] subdirectory.

See: spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

# =============================================================================
# Ingest Event (Document Crossing the Membrane)
# =============================================================================


@dataclass(frozen=True)
class IngestEvent:
    """
    A document crossing the membrane.

    This is the input to the ingest() function. It captures everything
    we know about the document at the moment of crossing.

    Fields:
        source: Where it came from (e.g., "git:repo", "file:/path", "kblock")
        content_hash: SHA256 of content (for deduplication)
        content: The actual bytes (exact copy)
        claimed_path: Where it wants to live (e.g., "spec/protocols/k-block.md")
        source_timestamp: When source says it changed (if known)
        source_author: Who source says wrote it (if known)

    Example:
        >>> event = IngestEvent(
        ...     source="git:/Users/kent/kgents",
        ...     content_hash="abc123...",
        ...     content=b"# My Spec\\n...",
        ...     claimed_path="spec/protocols/my-spec.md",
        ... )
    """

    source: str
    content_hash: str
    content: bytes
    claimed_path: str

    # Optional metadata from source
    source_timestamp: datetime | None = None
    source_author: str | None = None

    @classmethod
    def from_file(cls, path: Path, source: str = "file") -> IngestEvent:
        """Create IngestEvent from a file on disk."""
        content = path.read_bytes()
        content_hash = hashlib.sha256(content).hexdigest()

        return cls(
            source=f"{source}:{path}",
            content_hash=content_hash,
            content=content,
            claimed_path=str(path),
            source_timestamp=datetime.fromtimestamp(path.stat().st_mtime, tz=UTC),
        )

    @classmethod
    def from_content(
        cls,
        content: bytes | str,
        claimed_path: str,
        source: str = "memory",
    ) -> IngestEvent:
        """Create IngestEvent from in-memory content."""
        if isinstance(content, str):
            content = content.encode("utf-8")
        content_hash = hashlib.sha256(content).hexdigest()

        return cls(
            source=source,
            content_hash=content_hash,
            content=content,
            claimed_path=claimed_path,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (content excluded for JSON safety)."""
        return {
            "source": self.source,
            "content_hash": self.content_hash,
            "claimed_path": self.claimed_path,
            "source_timestamp": self.source_timestamp.isoformat()
            if self.source_timestamp
            else None,
            "source_author": self.source_author,
        }


# =============================================================================
# Sovereign Entity (What We Store)
# =============================================================================


@dataclass
class SovereignEntity:
    """
    A document under our sovereign control.

    After ingestion, this is what we have:
    - path: Where it lives in our membrane
    - content: The exact bytes
    - metadata: Ingest metadata (version, hash, marks)
    - overlay: Our modifications (annotations, edges, corrections)

    The Three Layers:
        1. OVERLAY (ours): annotations, corrections, insights
        2. SOVEREIGN COPY: exact bytes, versioned
        3. WITNESS TRAIL: marks stored separately

    Example:
        >>> entity = SovereignEntity(
        ...     path="spec/protocols/k-block.md",
        ...     content=b"# K-Block\\n...",
        ...     version=2,
        ...     metadata={"ingest_mark": "mark-abc123", ...},
        ...     overlay={"annotations": [...], "edges": {...}},
        ... )
    """

    path: str
    content: bytes
    version: int
    metadata: dict[str, Any] = field(default_factory=dict)
    overlay: dict[str, Any] = field(default_factory=dict)

    @property
    def content_text(self) -> str:
        """Decode content as UTF-8 (with fallback)."""
        try:
            return self.content.decode("utf-8")
        except UnicodeDecodeError:
            return self.content.decode("utf-8", errors="replace")

    @property
    def content_hash(self) -> str:
        """SHA256 of current content."""
        return hashlib.sha256(self.content).hexdigest()

    @property
    def ingest_mark_id(self) -> str | None:
        """The mark ID of the ingest event."""
        return self.metadata.get("ingest_mark")

    @property
    def annotations(self) -> list[dict[str, Any]]:
        """Get annotations from overlay."""
        result: list[dict[str, Any]] = self.overlay.get("annotations", [])
        return result

    @property
    def edges(self) -> list[dict[str, Any]]:
        """Get edges from overlay."""
        edges_data: dict[str, Any] = self.overlay.get("edges", {})
        result: list[dict[str, Any]] = edges_data.get("edges", [])
        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (content as base64 if binary)."""
        import base64

        try:
            content_str = self.content.decode("utf-8")
            content_encoding = "utf-8"
        except UnicodeDecodeError:
            content_str = base64.b64encode(self.content).decode("ascii")
            content_encoding = "base64"

        return {
            "path": self.path,
            "content": content_str,
            "content_encoding": content_encoding,
            "version": self.version,
            "metadata": self.metadata,
            "overlay": self.overlay,
        }


# =============================================================================
# Ingested Entity (Result of Ingest)
# =============================================================================


@dataclass
class IngestedEntity:
    """
    Result of ingesting a document.

    Contains references to the sovereign entity and all witness marks
    created during ingestion.

    Fields:
        path: The entity path
        version: Version number (1, 2, 3, ...)
        ingest_mark_id: The birth certificate mark
        edge_mark_ids: All edge discovery marks
        entity: The stored sovereign entity
    """

    path: str
    version: int
    ingest_mark_id: str
    edge_mark_ids: list[str] = field(default_factory=list)
    entity: SovereignEntity | None = None

    @property
    def edge_count(self) -> int:
        """Number of edges discovered during ingest."""
        return len(self.edge_mark_ids)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "version": self.version,
            "ingest_mark_id": self.ingest_mark_id,
            "edge_mark_ids": self.edge_mark_ids,
            "edge_count": self.edge_count,
        }


# =============================================================================
# Sync Result
# =============================================================================


class SyncStatus(Enum):
    """Status of a sync operation."""

    ACCEPTED = auto()  # Change was accepted and ingested
    REJECTED = auto()  # Change was rejected (policy)
    UNCHANGED = auto()  # No change detected
    CONFLICT = auto()  # Our overlay conflicts with source change
    ERROR = auto()  # Error during sync


@dataclass
class SyncResult:
    """
    Result of a sync operation.

    Sync is receive-only. We decide whether to accept external changes.

    Fields:
        status: What happened
        path: The entity path
        old_version: Previous version (if any)
        new_version: New version (if accepted)
        mark_id: The sync notification mark
        message: Human-readable explanation
    """

    status: SyncStatus
    path: str
    old_version: int | None = None
    new_version: int | None = None
    mark_id: str | None = None
    message: str = ""

    @classmethod
    def accepted(
        cls, path: str, old_version: int | None, new_version: int, mark_id: str
    ) -> SyncResult:
        """Create an accepted sync result."""
        return cls(
            status=SyncStatus.ACCEPTED,
            path=path,
            old_version=old_version,
            new_version=new_version,
            mark_id=mark_id,
            message=f"Accepted sync: v{old_version or 0} -> v{new_version}",
        )

    @classmethod
    def rejected(cls, path: str, reason: str, mark_id: str | None = None) -> SyncResult:
        """Create a rejected sync result."""
        return cls(
            status=SyncStatus.REJECTED,
            path=path,
            mark_id=mark_id,
            message=f"Rejected: {reason}",
        )

    @classmethod
    def unchanged(cls, path: str) -> SyncResult:
        """Create an unchanged sync result."""
        return cls(
            status=SyncStatus.UNCHANGED,
            path=path,
            message="No change detected",
        )

    @classmethod
    def conflict(cls, path: str, reason: str) -> SyncResult:
        """Create a conflict sync result."""
        return cls(
            status=SyncStatus.CONFLICT,
            path=path,
            message=f"Conflict: {reason}",
        )

    @classmethod
    def error(cls, path: str, error: str) -> SyncResult:
        """Create an error sync result."""
        return cls(
            status=SyncStatus.ERROR,
            path=path,
            message=f"Error: {error}",
        )


# =============================================================================
# Diff (Comparison with Source)
# =============================================================================


class DiffType(Enum):
    """Type of difference detected."""

    NEW = auto()  # Entity doesn't exist, source is new
    UNCHANGED = auto()  # No difference
    MODIFIED = auto()  # Content differs
    DELETED = auto()  # We have it, source doesn't


@dataclass
class Diff:
    """
    Difference between our sovereign copy and external source.

    Used during sync to decide what to do with changes.

    Fields:
        diff_type: What kind of difference
        our_content: Our current content (if any)
        source_content: Source content (if any)
        our_hash: SHA256 of our content
        source_hash: SHA256 of source content
    """

    diff_type: DiffType
    our_content: bytes | None = None
    source_content: bytes | None = None
    our_hash: str | None = None
    source_hash: str | None = None

    @classmethod
    def new(cls, source_content: bytes) -> Diff:
        """Source is new (we don't have it)."""
        return cls(
            diff_type=DiffType.NEW,
            source_content=source_content,
            source_hash=hashlib.sha256(source_content).hexdigest(),
        )

    @classmethod
    def unchanged(cls) -> Diff:
        """No difference."""
        return cls(diff_type=DiffType.UNCHANGED)

    @classmethod
    def modified(cls, our_content: bytes, source_content: bytes) -> Diff:
        """Content differs."""
        return cls(
            diff_type=DiffType.MODIFIED,
            our_content=our_content,
            source_content=source_content,
            our_hash=hashlib.sha256(our_content).hexdigest(),
            source_hash=hashlib.sha256(source_content).hexdigest(),
        )

    @classmethod
    def deleted(cls, our_content: bytes) -> Diff:
        """We have it, source doesn't."""
        return cls(
            diff_type=DiffType.DELETED,
            our_content=our_content,
            our_hash=hashlib.sha256(our_content).hexdigest(),
        )

    @property
    def is_changed(self) -> bool:
        """Whether there's a meaningful change."""
        return self.diff_type in (DiffType.NEW, DiffType.MODIFIED, DiffType.DELETED)


# =============================================================================
# Annotation (Our Overlay Contribution)
# =============================================================================


class AnnotationType(Enum):
    """Type of annotation we add to an entity."""

    INSIGHT = "insight"  # We discovered something
    CORRECTION = "correction"  # We fixed an error
    WARNING = "warning"  # Something is concerning
    TODO = "todo"  # Follow-up needed
    LINK = "link"  # Cross-reference


@dataclass
class Annotation:
    """
    An annotation we add to an entity.

    Annotations are stored in the overlay, linked to witness marks.

    Fields:
        annotation_type: What kind of annotation
        line: Line number (1-indexed, or 0 for whole-file)
        content: The annotation content
        mark_id: Link to witness mark
        original: Original text (for corrections)
        corrected: Corrected text (for corrections)
        reasoning: Why we made this annotation
    """

    annotation_type: AnnotationType
    line: int
    content: str
    mark_id: str | None = None

    # For corrections
    original: str | None = None
    corrected: str | None = None

    # Reasoning
    reasoning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        d: dict[str, Any] = {
            "type": self.annotation_type.value,
            "line": self.line,
            "content": self.content,
        }
        if self.mark_id:
            d["mark_id"] = self.mark_id
        if self.original:
            d["original"] = self.original
        if self.corrected:
            d["corrected"] = self.corrected
        if self.reasoning:
            d["reasoning"] = self.reasoning
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Annotation:
        """Create from dictionary."""
        return cls(
            annotation_type=AnnotationType(data["type"]),
            line=data["line"],
            content=data["content"],
            mark_id=data.get("mark_id"),
            original=data.get("original"),
            corrected=data.get("corrected"),
            reasoning=data.get("reasoning"),
        )


# =============================================================================
# Delete Result
# =============================================================================


@dataclass
class DeleteResult:
    """
    Result of a delete operation.

    Contains information about what was deleted and any reference handling.

    Fields:
        success: Whether the delete succeeded
        path: The entity path that was deleted
        mark_id: The witness mark for the deletion
        references_converted_to_placeholders: List of entities whose references
                                              were converted to placeholders
    """

    success: bool
    path: str
    mark_id: str | None = None
    references_converted_to_placeholders: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "path": self.path,
            "mark_id": self.mark_id,
            "references_converted": self.references_converted_to_placeholders,
            "reference_count": len(self.references_converted_to_placeholders),
        }


# =============================================================================
# Export Bundle (Law 3: No Export Without Witness)
# =============================================================================


@dataclass
class ExportedEntity:
    """
    An entity that has been exported.

    Contains the entity data plus provenance information.
    """

    path: str
    content: bytes
    content_hash: str
    ingest_mark_id: str | None
    version: int
    metadata: dict[str, Any] = field(default_factory=dict)
    overlay: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportBundle:
    """
    Bundle of exported entities with witness trail.

    Law 3 guarantee: Every export has a witness mark created BEFORE export.

    Fields:
        export_mark_id: The witness mark for this export operation
        entities: List of exported entities
        exported_at: When the export happened
        export_format: Format of export (json, zip)
        entity_count: Number of entities in bundle
    """

    export_mark_id: str
    entities: list[ExportedEntity]
    exported_at: datetime
    export_format: str = "json"

    @property
    def entity_count(self) -> int:
        """Number of entities in bundle."""
        return len(self.entities)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import base64

        return {
            "type": "sovereign_export",
            "export_mark_id": self.export_mark_id,
            "exported_at": self.exported_at.isoformat(),
            "export_format": self.export_format,
            "entity_count": self.entity_count,
            "entities": [
                {
                    "path": e.path,
                    "content": base64.b64encode(e.content).decode("ascii"),
                    "content_hash": e.content_hash,
                    "ingest_mark_id": e.ingest_mark_id,
                    "version": e.version,
                    "metadata": e.metadata,
                    "overlay": e.overlay,
                }
                for e in self.entities
            ],
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Ingest
    "IngestEvent",
    "IngestedEntity",
    # Sovereign
    "SovereignEntity",
    # Sync
    "SyncStatus",
    "SyncResult",
    # Diff
    "DiffType",
    "Diff",
    # Annotation
    "AnnotationType",
    "Annotation",
    # Delete
    "DeleteResult",
    # Export
    "ExportedEntity",
    "ExportBundle",
]
