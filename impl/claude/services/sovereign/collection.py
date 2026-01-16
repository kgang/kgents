"""
Sovereign Collection Service: Manage entity collections (pointer-based grouping).

> *"Collections are directories of the mind, not the filesystem."*

Collections enable semantic organization without moving files:
- "Phase 1 Specs"
- "Agent Definitions"
- "Crown Jewels"
- "My Session Uploads"

Key insight: Collections are POINTERS, not copies.
The same entity can appear in multiple collections (like tags).

Teaching:
    gotcha: Collections store paths, not content. No duplication.
    gotcha: Can include glob patterns: ["spec/agents/**/*.md"]
    gotcha: Hierarchical via parent_id (tree structure)

See: spec/protocols/sovereign-data-guarantees.md
"""

from __future__ import annotations

import fnmatch
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sovereign import (
    SovereignCollectionRow,
    SovereignPlaceholderRow,
    generate_collection_id,
    generate_placeholder_id,
)

if TYPE_CHECKING:
    from .store import SovereignStore

logger = logging.getLogger(__name__)


# =============================================================================
# Collection Service
# =============================================================================


class CollectionService:
    """
    Service for managing sovereign collections.

    Collections are pointer-based groupings stored in the database,
    while actual content lives in the SovereignStore filesystem.

    Example:
        >>> service = CollectionService(session, store)
        >>> collection = await service.create("Phase 1 Specs", description="...")
        >>> await service.add_paths(collection.id, ["spec/phase1/*.md"])
        >>> entities = await service.resolve_paths(collection.id)
    """

    def __init__(
        self,
        session: AsyncSession,
        store: "SovereignStore",
    ):
        """
        Initialize the collection service.

        Args:
            session: Database session for collection persistence
            store: Sovereign store for resolving paths
        """
        self.session = session
        self.store = store

    # =========================================================================
    # CRUD Operations
    # =========================================================================

    async def create(
        self,
        name: str,
        description: str | None = None,
        paths: list[str] | None = None,
        parent_id: str | None = None,
        created_by: str | None = None,
    ) -> SovereignCollectionRow:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Optional description
            paths: Initial paths (can include globs)
            parent_id: Parent collection ID for hierarchy
            created_by: Creator identifier

        Returns:
            The created collection
        """
        collection = SovereignCollectionRow(
            id=generate_collection_id(),
            name=name,
            description=description,
            paths=paths or [],
            parent_id=parent_id,
            created_by=created_by,
            analysis_status="pending",
            analyzed_count=0,
        )

        self.session.add(collection)
        await self.session.commit()
        await self.session.refresh(collection)

        logger.info(f"Created collection: {collection.name} ({collection.id})")
        return collection

    async def get(self, collection_id: str) -> SovereignCollectionRow | None:
        """Get a collection by ID."""
        result = await self.session.execute(
            select(SovereignCollectionRow).where(SovereignCollectionRow.id == collection_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> SovereignCollectionRow | None:
        """Get a collection by name."""
        result = await self.session.execute(
            select(SovereignCollectionRow).where(SovereignCollectionRow.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        parent_id: str | None = None,
        include_children: bool = False,
    ) -> list[SovereignCollectionRow]:
        """
        List collections.

        Args:
            parent_id: Filter by parent (None = root collections)
            include_children: Include nested children recursively

        Returns:
            List of collections
        """
        query = select(SovereignCollectionRow)

        if parent_id is not None:
            query = query.where(SovereignCollectionRow.parent_id == parent_id)
        elif not include_children:
            query = query.where(SovereignCollectionRow.parent_id.is_(None))

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(
        self,
        collection_id: str,
        name: str | None = None,
        description: str | None = None,
        parent_id: str | None = None,
    ) -> SovereignCollectionRow | None:
        """
        Update collection metadata.

        Args:
            collection_id: Collection to update
            name: New name (if provided)
            description: New description (if provided)
            parent_id: New parent (if provided)

        Returns:
            Updated collection or None if not found
        """
        collection = await self.get(collection_id)
        if not collection:
            return None

        if name is not None:
            collection.name = name
        if description is not None:
            collection.description = description
        if parent_id is not None:
            collection.parent_id = parent_id

        await self.session.commit()
        await self.session.refresh(collection)
        return collection

    async def delete(self, collection_id: str) -> bool:
        """
        Delete a collection (not its contents).

        Args:
            collection_id: Collection to delete

        Returns:
            True if deleted, False if not found
        """
        collection = await self.get(collection_id)
        if not collection:
            return False

        await self.session.delete(collection)
        await self.session.commit()

        logger.info(f"Deleted collection: {collection.name} ({collection_id})")
        return True

    # =========================================================================
    # Path Management
    # =========================================================================

    async def add_paths(
        self,
        collection_id: str,
        paths: list[str],
    ) -> SovereignCollectionRow | None:
        """
        Add paths to a collection (idempotent).

        Args:
            collection_id: Collection to modify
            paths: Paths to add (can include globs)

        Returns:
            Updated collection or None if not found
        """
        collection = await self.get(collection_id)
        if not collection:
            return None

        for path in paths:
            collection.add_path(path)

        await self.session.commit()
        await self.session.refresh(collection)
        return collection

    async def remove_paths(
        self,
        collection_id: str,
        paths: list[str],
    ) -> SovereignCollectionRow | None:
        """
        Remove paths from a collection.

        Args:
            collection_id: Collection to modify
            paths: Paths to remove

        Returns:
            Updated collection or None if not found
        """
        collection = await self.get(collection_id)
        if not collection:
            return None

        for path in paths:
            collection.remove_path(path)

        await self.session.commit()
        await self.session.refresh(collection)
        return collection

    async def resolve_paths(
        self,
        collection_id: str,
    ) -> list[str]:
        """
        Resolve collection paths to actual entity paths.

        Expands glob patterns against the sovereign store.

        Args:
            collection_id: Collection to resolve

        Returns:
            List of actual entity paths (no globs)
        """
        collection = await self.get(collection_id)
        if not collection:
            return []

        all_entities = await self.store.list_all()
        resolved = set()

        for pattern in collection.paths:
            if "*" in pattern or "?" in pattern:
                # Glob pattern - match against all entities
                for entity_path in all_entities:
                    if fnmatch.fnmatch(entity_path, pattern):
                        resolved.add(entity_path)
            else:
                # Direct path - check if exists
                if await self.store.exists(pattern):
                    resolved.add(pattern)

        return sorted(resolved)

    async def get_entity_count(self, collection_id: str) -> int:
        """Get the number of entities in a collection (after resolving globs)."""
        paths = await self.resolve_paths(collection_id)
        return len(paths)

    # =========================================================================
    # Analysis Tracking
    # =========================================================================

    async def update_analysis_status(
        self,
        collection_id: str,
    ) -> SovereignCollectionRow | None:
        """
        Update collection analysis status based on entity states.

        Checks how many entities in the collection are analyzed
        and updates the collection's analysis_status accordingly.

        Returns:
            Updated collection or None if not found
        """
        collection = await self.get(collection_id)
        if not collection:
            return None

        resolved_paths = await self.resolve_paths(collection_id)
        analyzed_count = 0

        for path in resolved_paths:
            if await self.store.is_analyzed(path):
                analyzed_count += 1

        collection.update_analysis_status(analyzed_count)
        await self.session.commit()
        await self.session.refresh(collection)

        return collection

    # =========================================================================
    # Export
    # =========================================================================

    async def export_collection(
        self,
        collection_id: str,
        format: str = "zip",
    ) -> bytes:
        """
        Export all entities in a collection.

        Args:
            collection_id: Collection to export
            format: Export format ("json" or "zip")

        Returns:
            Exported bundle as bytes
        """
        resolved_paths = await self.resolve_paths(collection_id)
        return await self.store.export_bundle(resolved_paths, format=format)

    def to_dict(self, collection: SovereignCollectionRow) -> dict[str, Any]:
        """Convert collection to dictionary for API response."""
        return {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "paths": collection.paths,
            "parent_id": collection.parent_id,
            "created_by": collection.created_by,
            "analysis_status": collection.analysis_status,
            "analyzed_count": collection.analyzed_count,
            "created_at": collection.created_at.isoformat() if collection.created_at else None,
            "updated_at": collection.updated_at.isoformat() if collection.updated_at else None,
        }


# =============================================================================
# Placeholder Service
# =============================================================================


class PlaceholderService:
    """
    Service for managing sovereign placeholders.

    Placeholders are auto-created during analysis when a document
    references a non-existent file. They're resolved when the
    real document is uploaded.
    """

    def __init__(
        self,
        session: AsyncSession,
        store: "SovereignStore",
    ):
        self.session = session
        self.store = store

    async def create(
        self,
        path: str,
        referenced_by: str,
        edge_type: str = "references",
        context: dict[str, Any] | None = None,
    ) -> SovereignPlaceholderRow:
        """
        Create or update a placeholder.

        If placeholder already exists for path, adds the new reference.

        Args:
            path: The missing entity path
            referenced_by: Path of entity that references this
            edge_type: Type of reference edge
            context: Optional context snippet

        Returns:
            The placeholder (created or updated)
        """
        # Check if placeholder exists
        result = await self.session.execute(
            select(SovereignPlaceholderRow).where(SovereignPlaceholderRow.path == path)
        )
        placeholder = result.scalar_one_or_none()

        if placeholder:
            # Add reference to existing
            placeholder.add_reference(referenced_by, edge_type, context)
        else:
            # Create new
            placeholder = SovereignPlaceholderRow(
                id=generate_placeholder_id(),
                path=path,
                referenced_by=[referenced_by],
                edge_types=[edge_type],
                contexts=[context] if context else [],
            )
            self.session.add(placeholder)

        await self.session.commit()
        await self.session.refresh(placeholder)

        logger.debug(f"Placeholder for {path} (ref by {referenced_by})")
        return placeholder

    async def get(self, path: str) -> SovereignPlaceholderRow | None:
        """Get placeholder by path."""
        result = await self.session.execute(
            select(SovereignPlaceholderRow).where(SovereignPlaceholderRow.path == path)
        )
        return result.scalar_one_or_none()

    async def list_unresolved(self) -> list[SovereignPlaceholderRow]:
        """List all unresolved placeholders."""
        result = await self.session.execute(
            select(SovereignPlaceholderRow).where(
                SovereignPlaceholderRow.resolved == False  # noqa: E712
            )
        )
        return list(result.scalars().all())

    async def resolve(self, path: str) -> bool:
        """
        Mark a placeholder as resolved.

        Called when the real document is uploaded.

        Returns:
            True if resolved, False if not found
        """
        placeholder = await self.get(path)
        if not placeholder:
            return False

        placeholder.resolve()
        await self.session.commit()

        logger.info(f"Resolved placeholder: {path}")
        return True

    async def check_and_resolve(self, path: str) -> bool:
        """
        Check if path matches an unresolved placeholder and resolve it.

        Called after ingest to auto-resolve placeholders.

        Returns:
            True if a placeholder was resolved
        """
        placeholder = await self.get(path)
        if placeholder and not placeholder.resolved:
            return await self.resolve(path)
        return False

    def to_dict(self, placeholder: SovereignPlaceholderRow) -> dict[str, Any]:
        """Convert placeholder to dictionary for API response."""
        return {
            "id": placeholder.id,
            "path": placeholder.path,
            "referenced_by": placeholder.referenced_by,
            "edge_types": placeholder.edge_types,
            "contexts": placeholder.contexts,
            "resolved": placeholder.resolved,
            "resolved_at": placeholder.resolved_at.isoformat() if placeholder.resolved_at else None,
            "annotation": placeholder.annotation,
            "created_at": placeholder.created_at.isoformat() if placeholder.created_at else None,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "CollectionService",
    "PlaceholderService",
]
