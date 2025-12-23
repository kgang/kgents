"""
Annotation Model: SQLAlchemy ORM for spec ↔ impl annotations.

> *"Every annotation leaves a witness mark. Every link is bidirectional."*

This table stores annotations that link spec sections to:
- Constitutional principles (tasteful, composable, etc.)
- Implementation code (services/*, agents/*)
- Gotchas and traps to avoid
- Design decisions (fusion records)
- Aesthetic judgments

The Dual-Track Pattern:
- This table: Fast queries by spec_path, kind, principle, status
- D-gent datum: Semantic search, associative connections (future)

AGENTESE: concept.annotate.*

Teaching:
    gotcha: We use String for paths (not Path objects) to maintain
            database portability across platforms.

    principle: Composable - Annotations are queryable by multiple
               dimensions (spec_path, kind, principle, status).

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SQLEnum, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin

# Use JSON with JSONB variant for PostgreSQL (enables GIN index).
# Falls back to plain JSON for SQLite.
JSONBCompat = JSON().with_variant(JSONB(), "postgresql")


class SpecAnnotationRow(TimestampMixin, Base):
    """
    A single annotation linking spec to principles/impl/gotchas.

    Annotations enable bidirectional tracing:
    - Spec → Impl: Find code that implements a spec section
    - Impl → Spec: Find spec that justifies this code
    - Principle → Spec: Find sections honoring a principle
    - Decision → Spec: Link design decisions to spec context

    Example queries:
        # All annotations for a spec
        SELECT * FROM spec_annotations WHERE spec_path = 'spec/protocols/witness.md';

        # All GOTCHA annotations
        SELECT * FROM spec_annotations WHERE kind = 'gotcha';

        # All sections honoring 'composable' principle
        SELECT * FROM spec_annotations WHERE kind = 'principle' AND principle = 'composable';

        # All impl links for a section
        SELECT * FROM spec_annotations
        WHERE spec_path = 'spec/protocols/witness.md'
          AND section = 'Mark Structure'
          AND kind = 'impl_link';

    Fields:
        id: Unique annotation identifier (primary key)
        spec_path: Path to spec file (relative to repo root)
        section: Section/heading in spec file
        kind: Type of annotation (principle, impl_link, gotcha, taste, decision)
        principle: Constitutional principle name (if kind=principle)
        impl_path: Path to implementation (if kind=impl_link)
        decision_id: Link to fusion decision record (if kind=decision)
        note: Human-readable annotation content
        created_by: Author (kent, claude, etc.)
        mark_id: Witness mark ID (every annotation is witnessed)
        status: Lifecycle status (active, superseded, archived)
        metadata: Additional structured data (JSON/JSONB)

    Teaching:
        gotcha: We store principle as a separate column (not in metadata)
                for efficient querying via indexes.

        principle: Generative - The table schema itself is a spec.
                   It defines the structure of all annotations.
    """

    __tablename__ = "spec_annotations"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Spec location
    spec_path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(256), nullable=False)

    # Annotation type
    kind: Mapped[str] = mapped_column(
        SQLEnum(
            "principle",
            "impl_link",
            "gotcha",
            "taste",
            "decision",
            name="annotation_kind",
            create_constraint=True,
        ),
        nullable=False,
        index=True,
    )

    # Kind-specific fields
    principle: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    impl_path: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    decision_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Content
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Authorship
    created_by: Mapped[str] = mapped_column(String(64), nullable=False, default="kent")

    # Witness trace
    mark_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Lifecycle
    status: Mapped[str] = mapped_column(
        SQLEnum(
            "active",
            "superseded",
            "archived",
            name="annotation_status",
            create_constraint=True,
        ),
        nullable=False,
        default="active",
        index=True,
    )

    # Additional structured data
    # Note: 'metadata' is reserved in SQLAlchemy, use 'annotation_meta' instead
    annotation_meta: Mapped[dict[str, Any]] = mapped_column(
        JSONBCompat, nullable=False, default=dict
    )

    __table_args__: Any = (
        # Composite indexes for common queries
        Index("idx_spec_annotations_spec_section", "spec_path", "section"),
        Index("idx_spec_annotations_spec_kind", "spec_path", "kind"),
        Index("idx_spec_annotations_kind_status", "kind", "status"),
        Index("idx_spec_annotations_spec_status", "spec_path", "status"),
        # GIN index for JSONB annotation_meta (PostgreSQL only)
        Index("idx_spec_annotations_metadata", "annotation_meta", postgresql_using="gin"),
    )

    def __repr__(self) -> str:
        """Human-readable representation."""
        return (
            f"<SpecAnnotationRow(id={self.id!r}, "
            f"spec_path={self.spec_path!r}, "
            f"section={self.section!r}, "
            f"kind={self.kind!r})>"
        )


__all__ = ["SpecAnnotationRow"]
