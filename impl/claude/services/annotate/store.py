"""
Annotation Store: Database persistence for spec ↔ impl annotations.

> *"Every annotation is witnessed. Every query is fast."*

This module provides database-backed storage for annotations with efficient querying:
- Save annotations with automatic witness marking
- Query by spec_path, kind, principle, status
- Build impl graphs from IMPL_LINK annotations
- Calculate coverage metrics

Storage Pattern:
    - Primary: Database (spec_annotations table) for queryability
    - Future: Optional inline YAML in spec files for visibility

Teaching:
    gotcha: We use SQLAlchemy's async session. Always use `async with` for
            session lifecycle management (prevents connection leaks).

    principle: Composable - Store operations compose via async context managers.
               Save → Query → Build Graph can be chained cleanly.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

import logging
import secrets
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.annotation import SpecAnnotationRow
from models.base import get_async_session

from .types import (
    AnnotationKind,
    AnnotationQueryResult,
    AnnotationStatus,
    SpecAnnotation,
)

if TYPE_CHECKING:
    from services.witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================


def _generate_annotation_id() -> str:
    """Generate unique annotation ID."""
    return f"ann-{secrets.token_hex(8)}"


def _row_to_annotation(row: SpecAnnotationRow) -> SpecAnnotation:
    """Convert database row to SpecAnnotation dataclass."""
    return SpecAnnotation(
        id=row.id,
        spec_path=row.spec_path,
        section=row.section,
        kind=AnnotationKind(row.kind),
        principle=row.principle,
        impl_path=row.impl_path,
        decision_id=row.decision_id,
        note=row.note,
        created_by=row.created_by,
        created_at=row.created_at,
        mark_id=row.mark_id,
        status=AnnotationStatus(row.status),
    )


def _annotation_to_row(ann: SpecAnnotation) -> SpecAnnotationRow:
    """Convert SpecAnnotation dataclass to database row."""
    return SpecAnnotationRow(
        id=ann.id,
        spec_path=ann.spec_path,
        section=ann.section,
        kind=ann.kind.value,
        principle=ann.principle,
        impl_path=ann.impl_path,
        decision_id=ann.decision_id,
        note=ann.note,
        created_by=ann.created_by,
        mark_id=ann.mark_id,
        status=ann.status.value,
        annotation_meta={},
    )


# =============================================================================
# AnnotationStore
# =============================================================================


class AnnotationStore:
    """
    Database-backed storage for spec ↔ impl annotations.

    Example usage:
        >>> store = AnnotationStore()
        >>> witness = await get_witness_persistence()
        >>>
        >>> # Save a principle annotation
        >>> ann = await store.save_annotation(
        ...     spec_path="spec/protocols/witness.md",
        ...     section="Mark Structure",
        ...     kind=AnnotationKind.PRINCIPLE,
        ...     principle="composable",
        ...     note="Single output per mark",
        ...     created_by="kent",
        ...     witness=witness,
        ... )
        >>>
        >>> # Query annotations for a spec
        >>> result = await store.query_annotations(spec_path="spec/protocols/witness.md")
        >>> for ann in result.annotations:
        ...     print(f"{ann.section}: {ann.note}")
        >>>
        >>> # Get impl links
        >>> impl_links = await store.get_impl_links("spec/protocols/witness.md")
    """

    def __init__(self) -> None:
        """Initialize annotation store."""
        pass

    # =========================================================================
    # Save Operations
    # =========================================================================

    async def save_annotation(
        self,
        spec_path: str,
        section: str,
        kind: AnnotationKind,
        note: str,
        created_by: str = "kent",
        witness: WitnessPersistence | None = None,
        principle: str | None = None,
        impl_path: str | None = None,
        decision_id: str | None = None,
    ) -> SpecAnnotation:
        """
        Save a new annotation with automatic witness marking.

        Args:
            spec_path: Path to spec file (relative to repo root)
            section: Section/heading in spec file
            kind: Type of annotation (principle, impl_link, gotcha, etc.)
            note: Human-readable annotation content
            created_by: Author (kent, claude, etc.)
            witness: WitnessPersistence instance (for creating mark)
            principle: Constitutional principle (if kind=PRINCIPLE)
            impl_path: Path to implementation (if kind=IMPL_LINK)
            decision_id: Fusion decision ID (if kind=DECISION)

        Returns:
            The saved SpecAnnotation

        Raises:
            ValueError: If required fields missing for annotation kind
        """
        # Generate ID
        ann_id = _generate_annotation_id()

        # Create witness mark
        mark_id = ""
        if witness:
            mark_result = await witness.save_mark(
                action=f"Annotated {spec_path} ({section})",
                reasoning=f"{kind.value}: {note}",
                tags=["annotation", f"kind:{kind.value}"],
                author=created_by,
            )
            mark_id = mark_result.mark_id
            logger.info(f"Created witness mark {mark_id} for annotation {ann_id}")
        else:
            logger.warning(f"No witness provided for annotation {ann_id} - mark not created")

        # Create annotation
        annotation = SpecAnnotation(
            id=ann_id,
            spec_path=spec_path,
            section=section,
            kind=kind,
            principle=principle,
            impl_path=impl_path,
            decision_id=decision_id,
            note=note,
            created_by=created_by,
            created_at=datetime.utcnow(),
            mark_id=mark_id,
            status=AnnotationStatus.ACTIVE,
        )

        # Validate (raises ValueError if invalid)
        annotation.__post_init__()

        # Save to database
        async with get_async_session() as session:
            row = _annotation_to_row(annotation)
            session.add(row)
            await session.commit()
            logger.info(f"Saved annotation {ann_id}: {spec_path} / {section} ({kind.value})")

        return annotation

    # =========================================================================
    # Query Operations
    # =========================================================================

    async def query_annotations(
        self,
        spec_path: str | None = None,
        kind: AnnotationKind | None = None,
        principle: str | None = None,
        impl_path: str | None = None,
        status: AnnotationStatus | None = None,
    ) -> AnnotationQueryResult:
        """
        Query annotations by multiple filters.

        Args:
            spec_path: Filter by spec file path
            kind: Filter by annotation kind
            principle: Filter by principle name
            impl_path: Filter by implementation path
            status: Filter by lifecycle status

        Returns:
            AnnotationQueryResult with matching annotations

        Example:
            # All annotations for a spec
            result = await store.query_annotations(spec_path="spec/protocols/witness.md")

            # All GOTCHA annotations
            result = await store.query_annotations(kind=AnnotationKind.GOTCHA)

            # All sections honoring 'composable' principle
            result = await store.query_annotations(
                kind=AnnotationKind.PRINCIPLE,
                principle="composable"
            )
        """
        async with get_async_session() as session:
            # Build query
            stmt = select(SpecAnnotationRow)

            if spec_path:
                stmt = stmt.where(SpecAnnotationRow.spec_path == spec_path)
            if kind:
                stmt = stmt.where(SpecAnnotationRow.kind == kind.value)
            if principle:
                stmt = stmt.where(SpecAnnotationRow.principle == principle)
            if impl_path:
                stmt = stmt.where(SpecAnnotationRow.impl_path == impl_path)
            if status:
                stmt = stmt.where(SpecAnnotationRow.status == status.value)

            # Execute
            result = await session.execute(stmt)
            rows = result.scalars().all()

            # Convert to dataclasses
            annotations = [_row_to_annotation(row) for row in rows]

            # Group by kind
            grouped_by_kind: dict[AnnotationKind, list[SpecAnnotation]] = {}
            for ann in annotations:
                if ann.kind not in grouped_by_kind:
                    grouped_by_kind[ann.kind] = []
                grouped_by_kind[ann.kind].append(ann)

            # Group by principle
            grouped_by_principle: dict[str, list[SpecAnnotation]] = {}
            for ann in annotations:
                if ann.principle:
                    if ann.principle not in grouped_by_principle:
                        grouped_by_principle[ann.principle] = []
                    grouped_by_principle[ann.principle].append(ann)

            return AnnotationQueryResult(
                annotations=annotations,
                total_count=len(annotations),
                grouped_by_kind=grouped_by_kind,
                grouped_by_principle=grouped_by_principle,
            )

    async def get_annotation(self, annotation_id: str) -> SpecAnnotation | None:
        """Get a single annotation by ID."""
        async with get_async_session() as session:
            stmt = select(SpecAnnotationRow).where(SpecAnnotationRow.id == annotation_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return _row_to_annotation(row) if row else None

    async def get_impl_links(self, spec_path: str) -> list[SpecAnnotation]:
        """Get all IMPL_LINK annotations for a spec."""
        result = await self.query_annotations(
            spec_path=spec_path,
            kind=AnnotationKind.IMPL_LINK,
            status=AnnotationStatus.ACTIVE,
        )
        return result.annotations

    async def get_principles(self, spec_path: str) -> list[SpecAnnotation]:
        """Get all PRINCIPLE annotations for a spec."""
        result = await self.query_annotations(
            spec_path=spec_path,
            kind=AnnotationKind.PRINCIPLE,
            status=AnnotationStatus.ACTIVE,
        )
        return result.annotations

    async def get_gotchas(self, spec_path: str) -> list[SpecAnnotation]:
        """Get all GOTCHA annotations for a spec."""
        result = await self.query_annotations(
            spec_path=spec_path,
            kind=AnnotationKind.GOTCHA,
            status=AnnotationStatus.ACTIVE,
        )
        return result.annotations

    async def search_annotations(
        self,
        search_text: str,
        spec_path: str | None = None,
        kind: AnnotationKind | None = None,
    ) -> list[SpecAnnotation]:
        """
        Search annotations by substring in note, section, or spec_path.

        Args:
            search_text: Text to search for (case-insensitive)
            spec_path: Optional filter by spec file
            kind: Optional filter by annotation kind

        Returns:
            List of matching annotations

        Example:
            # Find all annotations mentioning "fire-and-forget"
            result = await store.search_annotations("fire-and-forget")

            # Find gotchas about "bus"
            result = await store.search_annotations("bus", kind=AnnotationKind.GOTCHA)
        """
        async with get_async_session() as session:
            # Build query
            stmt = select(SpecAnnotationRow)

            if spec_path:
                stmt = stmt.where(SpecAnnotationRow.spec_path == spec_path)
            if kind:
                stmt = stmt.where(SpecAnnotationRow.kind == kind.value)

            # Execute
            result = await session.execute(stmt)
            rows = result.scalars().all()

            # Filter by search text (case-insensitive substring match)
            search_lower = search_text.lower()
            matching_rows = [
                row
                for row in rows
                if search_lower in row.note.lower()
                or search_lower in row.section.lower()
                or search_lower in row.spec_path.lower()
                or (row.principle and search_lower in row.principle.lower())
                or (row.impl_path and search_lower in row.impl_path.lower())
            ]

            return [_row_to_annotation(row) for row in matching_rows]

    # =========================================================================
    # Update Operations
    # =========================================================================

    async def update_status(
        self,
        annotation_id: str,
        status: AnnotationStatus,
    ) -> SpecAnnotation | None:
        """Update annotation status (supersede or archive)."""
        async with get_async_session() as session:
            stmt = select(SpecAnnotationRow).where(SpecAnnotationRow.id == annotation_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()

            if not row:
                return None

            row.status = status.value
            await session.commit()

            logger.info(f"Updated annotation {annotation_id} status to {status.value}")
            return _row_to_annotation(row)

    async def supersede_annotation(
        self,
        old_id: str,
        new_annotation: SpecAnnotation,
    ) -> tuple[SpecAnnotation | None, SpecAnnotation]:
        """
        Supersede an old annotation with a new one.

        Args:
            old_id: ID of annotation to supersede
            new_annotation: New annotation to save

        Returns:
            Tuple of (old_annotation with SUPERSEDED status, new_annotation)
        """
        # Mark old as superseded
        old = await self.update_status(old_id, AnnotationStatus.SUPERSEDED)

        # Save new annotation
        async with get_async_session() as session:
            row = _annotation_to_row(new_annotation)
            session.add(row)
            await session.commit()

        logger.info(f"Superseded annotation {old_id} with {new_annotation.id}")
        return old, new_annotation

    async def delete_annotation(self, annotation_id: str) -> bool:
        """
        Delete an annotation permanently.

        Args:
            annotation_id: ID of annotation to delete

        Returns:
            True if deleted, False if not found

        Warning:
            This is a hard delete. Consider using update_status(..., ARCHIVED) instead
            for soft deletion that preserves history.
        """
        async with get_async_session() as session:
            stmt = select(SpecAnnotationRow).where(SpecAnnotationRow.id == annotation_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()

            if not row:
                return False

            await session.delete(row)
            await session.commit()

            logger.info(f"Deleted annotation {annotation_id}")
            return True

    async def bulk_import_annotations(
        self,
        annotations: list[SpecAnnotation],
        witness: WitnessPersistence | None = None,
    ) -> int:
        """
        Bulk import a list of annotations.

        Args:
            annotations: List of SpecAnnotation objects to import
            witness: Optional WitnessPersistence for marking imports

        Returns:
            Number of annotations successfully imported

        Example:
            # Load from YAML and import
            import yaml
            with open("annotations.yaml") as f:
                data = yaml.safe_load(f)
            annotations = [SpecAnnotation(**item) for item in data]
            count = await store.bulk_import_annotations(annotations)
        """
        imported = 0
        async with get_async_session() as session:
            for annotation in annotations:
                try:
                    # Validate
                    annotation.__post_init__()

                    # Convert and save
                    row = _annotation_to_row(annotation)
                    session.add(row)
                    imported += 1
                except Exception as e:
                    logger.error(f"Failed to import annotation {annotation.id}: {e}")
                    continue

            await session.commit()

        logger.info(f"Bulk imported {imported}/{len(annotations)} annotations")

        # Create single witness mark for bulk import
        if witness and imported > 0:
            await witness.save_mark(
                action=f"Bulk imported {imported} annotations",
                reasoning="Imported from external source",
                tags=["annotation", "bulk-import"],
            )

        return imported


__all__ = ["AnnotationStore"]
