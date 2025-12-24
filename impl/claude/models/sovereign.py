"""
Sovereign Crown Jewel: Database Models.

Tables for sovereign entity management:
- SovereignCollectionRow: Semantic groupings of entities (pointers, not copies)
- SovereignPlaceholderRow: Referenced-but-not-uploaded entities

Collections are "directory abstractions as pointers":
- Stored in DB, not filesystem
- Same entity can belong to multiple collections
- Used for batch operations and semantic organization

Placeholders are auto-created during analysis:
- When Doc A references Doc B (not yet uploaded)
- Placeholder for B created automatically
- Resolved when B is actually uploaded

AGENTESE: concept.sovereign.collection.*, concept.sovereign.placeholder.*
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Use JSON with JSONB variant for PostgreSQL (enables GIN index).
# Falls back to plain JSON for SQLite.
JSONBCompat = JSON().with_variant(JSONB(), "postgresql")

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


def generate_collection_id() -> str:
    """Generate a unique collection ID."""
    return f"coll-{uuid.uuid4().hex[:12]}"


def generate_placeholder_id() -> str:
    """Generate a unique placeholder ID."""
    return f"ph-{uuid.uuid4().hex[:12]}"


class SovereignCollectionRow(TimestampMixin, Base):
    """
    A collection of sovereign entities.

    Collections enable semantic organization without moving files:
    - "Phase 1 Specs"
    - "Agent Definitions"
    - "Crown Jewels"
    - "My Session Uploads"

    Key insight: Collections are POINTERS, not copies.
    The same entity can appear in multiple collections (like tags).

    The sovereign store remains flat: .kgents/sovereign/{path}/v{N}/...
    Collections are metadata pointing INTO that flat store.

    Operations:
    - analyze_collection: Batch analyze all paths
    - export_collection: Export as ZIP
    - add/remove paths

    AGENTESE: concept.sovereign.collection.*
    """

    __tablename__ = "sovereign_collections"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_collection_id
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Paths in this collection (JSON array of strings)
    # These are pointers into the sovereign store, not copies
    # Can include glob patterns: ["spec/agents/**/*.md", "uploads/session-2025/*"]
    paths: Mapped[list[str]] = mapped_column(JSONBCompat, default=list)

    # Creator (git email hash or user ID)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Parent collection (for hierarchy)
    parent_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("sovereign_collections.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Analysis status for the collection
    # "pending" = not all paths analyzed
    # "partial" = some paths analyzed
    # "complete" = all paths analyzed
    analysis_status: Mapped[str] = mapped_column(
        String(32), default="pending", nullable=False
    )
    analyzed_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    children: Mapped[list["SovereignCollectionRow"]] = relationship(
        back_populates="parent",
        foreign_keys=[parent_id],
    )
    parent: Mapped["SovereignCollectionRow | None"] = relationship(
        back_populates="children",
        foreign_keys=[parent_id],
        remote_side=[id],
    )

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_sovereign_collections_name", "name"),
        Index("idx_sovereign_collections_created_by", "created_by"),
        Index("idx_sovereign_collections_paths", "paths", postgresql_using="gin"),
    )

    def add_path(self, path: str) -> None:
        """Add a path to the collection (idempotent)."""
        if path not in self.paths:
            self.paths = [*self.paths, path]

    def remove_path(self, path: str) -> None:
        """Remove a path from the collection."""
        self.paths = [p for p in self.paths if p != path]

    def update_analysis_status(self, analyzed_count: int) -> None:
        """Update analysis status based on analyzed count."""
        self.analyzed_count = analyzed_count
        total = len(self.paths)
        if analyzed_count == 0:
            self.analysis_status = "pending"
        elif analyzed_count >= total:
            self.analysis_status = "complete"
        else:
            self.analysis_status = "partial"


class SovereignPlaceholderRow(TimestampMixin, Base):
    """
    A placeholder for a referenced-but-not-uploaded entity.

    Placeholders are auto-created during analysis when a reference
    points to a non-existent path:

    1. Doc A references Doc B (not uploaded)
    2. Analysis discovers reference to B
    3. Placeholder created for B (automatic, no user approval)
    4. Placeholder appears in graph with visual distinction
    5. When B uploaded, placeholder is resolved/replaced

    Visual treatment:
    - Dashed border
    - 70% opacity
    - "Referenced by N files" badge
    - Upload button in context

    AGENTESE: concept.sovereign.placeholder.*
    """

    __tablename__ = "sovereign_placeholders"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_placeholder_id
    )

    # The path that was referenced but doesn't exist
    path: Mapped[str] = mapped_column(
        String(1024), nullable=False, unique=True, index=True
    )

    # Who referenced this (JSON array of paths)
    # Multiple documents can reference the same missing file
    referenced_by: Mapped[list[str]] = mapped_column(JSONBCompat, default=list)

    # Edge types that created this placeholder
    # e.g., ["references", "implements", "tests"]
    edge_types: Mapped[list[str]] = mapped_column(JSONBCompat, default=list)

    # Context snippets from referencing documents
    # e.g., [{"path": "spec/foo.md", "line": 42, "context": "See spec/bar.md for..."}]
    contexts: Mapped[list[dict]] = mapped_column(JSONBCompat, default=list)

    # Resolved when real document uploaded
    resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Optional user annotation (even for placeholders)
    annotation: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (  # type: ignore[assignment]
        Index("idx_sovereign_placeholders_resolved", "resolved"),
        Index("idx_sovereign_placeholders_path", "path"),
        Index(
            "idx_sovereign_placeholders_referenced_by",
            "referenced_by",
            postgresql_using="gin",
        ),
    )

    def add_reference(
        self, referenced_by_path: str, edge_type: str, context: dict | None = None
    ) -> None:
        """Add a reference from another document."""
        if referenced_by_path not in self.referenced_by:
            self.referenced_by = [*self.referenced_by, referenced_by_path]
        if edge_type not in self.edge_types:
            self.edge_types = [*self.edge_types, edge_type]
        if context:
            self.contexts = [*self.contexts, context]

    def resolve(self) -> None:
        """Mark placeholder as resolved (real doc uploaded)."""
        self.resolved = True
        self.resolved_at = datetime.now()


__all__ = [
    "SovereignCollectionRow",
    "SovereignPlaceholderRow",
    "generate_collection_id",
    "generate_placeholder_id",
]
