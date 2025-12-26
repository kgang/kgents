"""
Sovereign REST API: File management and collections for sovereign entities.

Provides:
- GET    /api/sovereign/entities        - List all entities
- GET    /api/sovereign/entity          - Get entity with metadata
- POST   /api/sovereign/entity          - Upload/ingest new entity (JSON)
- POST   /api/sovereign/upload          - Upload file (multipart/form-data)
- PUT    /api/sovereign/entity/rename   - Rename entity
- DELETE /api/sovereign/entity          - Delete entity
- GET    /api/sovereign/entity/references - Get references to entity
- GET    /api/sovereign/export          - Export entities as ZIP/JSON

Collections:
- GET    /api/sovereign/collections     - List collections
- POST   /api/sovereign/collections     - Create collection
- GET    /api/sovereign/collections/{id} - Get collection
- PUT    /api/sovereign/collections/{id} - Update collection
- DELETE /api/sovereign/collections/{id} - Delete collection
- POST   /api/sovereign/collections/{id}/paths - Add paths
- DELETE /api/sovereign/collections/{id}/paths - Remove paths
- GET    /api/sovereign/collections/{id}/export - Export collection

Philosophy:
    "We don't reference. We possess."
    "Law 3: No Export Without Witness."
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query, Response, UploadFile, File
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    JSONResponse = None  # type: ignore
    UploadFile = None  # type: ignore
    File = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class EntityListResponse(BaseModel):
    """Response with list of entities."""

    entities: list[dict[str, Any]]
    total: int


class EntityResponse(BaseModel):
    """Response with entity details."""

    path: str
    version: int
    content: str
    content_hash: str
    metadata: dict[str, Any]
    overlay: dict[str, Any]
    analysis_status: str | None = None


class EntityUploadRequest(BaseModel):
    """Request to upload/ingest an entity."""

    path: str = Field(..., description="Target path for the entity")
    content: str = Field(..., description="Entity content")
    source: str = Field(default="upload", description="Source identifier")


class EntityUploadResponse(BaseModel):
    """Response from entity upload."""

    path: str
    version: int
    ingest_mark_id: str
    edge_count: int


class RenameRequest(BaseModel):
    """Request to rename an entity."""

    old_path: str
    new_path: str


class RenameResponse(BaseModel):
    """Response from rename."""

    old_path: str
    new_path: str
    success: bool
    message: str = ""


class DeleteRequest(BaseModel):
    """Request to delete an entity."""

    path: str
    force: bool = Field(default=False, description="Force delete even with references")


class DeleteResponse(BaseModel):
    """Response from delete."""

    path: str
    deleted: bool
    references: list[str] = []
    message: str = ""


class ReferencesResponse(BaseModel):
    """Response with references to an entity."""

    path: str
    referenced_by: list[dict[str, Any]]
    count: int


class CollectionCreateRequest(BaseModel):
    """Request to create a collection."""

    name: str
    description: str | None = None
    paths: list[str] | None = None
    parent_id: str | None = None


class CollectionResponse(BaseModel):
    """Response with collection details."""

    id: str
    name: str
    description: str | None
    paths: list[str]
    parent_id: str | None
    analysis_status: str
    analyzed_count: int
    entity_count: int | None = None


class CollectionListResponse(BaseModel):
    """Response with list of collections."""

    collections: list[dict[str, Any]]
    total: int


class CollectionUpdateRequest(BaseModel):
    """Request to update a collection."""

    name: str | None = None
    description: str | None = None


class PathsRequest(BaseModel):
    """Request to add/remove paths."""

    paths: list[str]


class EntityStatusResponse(BaseModel):
    """Response with entity analysis status."""

    path: str
    status: str
    startedAt: str | None = None
    completedAt: str | None = None
    error: str | None = None
    analyzer: str | None = None
    refCount: int = 0
    placeholderCount: int = 0


class AnalyzeCrystalResponse(BaseModel):
    """Response from analyze endpoint with crystal data."""

    path: str
    refs_found: list[str]
    connections_suggested: list[dict[str, Any]]
    concepts: list[str]
    summary: str
    analyzer: str
    analyzed_at: str


# =============================================================================
# Router Factory
# =============================================================================


def create_sovereign_router() -> APIRouter | None:
    """Create the sovereign API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, sovereign routes disabled")
        return None

    router = APIRouter(prefix="/api/sovereign", tags=["sovereign"])

    # =========================================================================
    # Entity Routes
    # =========================================================================

    @router.get("/entities", response_model=EntityListResponse)
    async def list_entities(
        prefix: str = Query(default="", description="Filter by path prefix"),
        limit: int = Query(default=100, ge=1, le=1000),
    ) -> EntityListResponse:
        """List all sovereign entities."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        all_paths = await store.list_all()

        # Filter by prefix
        if prefix:
            all_paths = [p for p in all_paths if p.startswith(prefix)]

        # Limit
        paths = all_paths[:limit]

        # Build response
        entities = []
        for path in paths:
            entity = await store.get_current(path)
            if entity:
                entities.append({
                    "path": path,
                    "version": entity.version,
                    "content_hash": entity.content_hash,
                    "is_analyzed": await store.is_analyzed(path),
                })

        return EntityListResponse(entities=entities, total=len(all_paths))

    @router.get("/entity", response_model=EntityResponse)
    async def get_entity(
        path: str = Query(..., description="Entity path"),
        version: int | None = Query(default=None, description="Specific version"),
    ) -> EntityResponse:
        """Get an entity with full metadata."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        if version:
            entity = await store.get_version(path, version)
        else:
            entity = await store.get_current(path)

        if not entity:
            raise HTTPException(status_code=404, detail=f"Entity not found: {path}")

        # Get analysis status
        analysis_state = await store.get_analysis_state(path)
        analysis_status = analysis_state.status.value if analysis_state else None

        return EntityResponse(
            path=path,
            version=entity.version,
            content=entity.content_text,
            content_hash=entity.content_hash,
            metadata=entity.metadata,
            overlay=entity.overlay,
            analysis_status=analysis_status,
        )

    @router.post("/entity", response_model=EntityUploadResponse)
    async def upload_entity(request: EntityUploadRequest) -> EntityUploadResponse:
        """Upload/ingest a new entity."""
        from services.providers import get_sovereign_store, get_witness_persistence
        from services.sovereign.ingest import Ingestor
        from services.sovereign.types import IngestEvent

        store = await get_sovereign_store()

        # Get witness persistence for proper mark creation
        # (Law 1: No Entity Without Witness)
        witness = await get_witness_persistence()

        # Create ingest event
        event = IngestEvent.from_content(
            content=request.content.encode("utf-8"),
            claimed_path=request.path,
            source=request.source,
        )

        # Ingest with witness for proper birth marks
        ingestor = Ingestor(store, witness=witness)
        result = await ingestor.ingest(event, author="api")

        return EntityUploadResponse(
            path=result.path,
            version=result.version,
            ingest_mark_id=result.ingest_mark_id,
            edge_count=result.edge_count,
        )

    @router.post("/upload", response_model=EntityUploadResponse)
    async def upload_file(
        file: UploadFile = File(...),
        path: str | None = Query(default=None, description="Target path (defaults to uploads/{filename})"),
    ) -> EntityUploadResponse:
        """
        Upload a file to the sovereign store.

        Accepts multipart/form-data file upload.
        If path is not provided, uses the filename in uploads/ directory.
        """
        from services.providers import get_sovereign_store, get_witness_persistence
        from services.sovereign.ingest import Ingestor
        from services.sovereign.types import IngestEvent

        store = await get_sovereign_store()

        # Get witness persistence for proper mark creation
        # (Law 1: No Entity Without Witness)
        witness = await get_witness_persistence()

        # Read file content
        content = await file.read()

        # Determine target path
        target_path = path if path else f"uploads/{file.filename}"

        # Create ingest event
        event = IngestEvent.from_content(
            content=content,
            claimed_path=target_path,
            source="upload",
        )

        # Ingest with witness for proper birth marks
        ingestor = Ingestor(store, witness=witness)
        result = await ingestor.ingest(event, author="api")

        return EntityUploadResponse(
            path=result.path,
            version=result.version,
            ingest_mark_id=result.ingest_mark_id,
            edge_count=result.edge_count,
        )

    @router.put("/entity/rename", response_model=RenameResponse)
    async def rename_entity(request: RenameRequest) -> RenameResponse:
        """Rename/move an entity."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        try:
            success = await store.rename(request.old_path, request.new_path)
            return RenameResponse(
                old_path=request.old_path,
                new_path=request.new_path,
                success=success,
                message="Entity renamed successfully",
            )
        except ValueError as e:
            return RenameResponse(
                old_path=request.old_path,
                new_path=request.new_path,
                success=False,
                message=str(e),
            )

    @router.delete("/entity", response_model=DeleteResponse)
    async def delete_entity(request: DeleteRequest) -> DeleteResponse:
        """Delete an entity."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()

        # Check for references
        references = await store.get_references_to(request.path)
        ref_paths = [r["from_path"] for r in references]

        if references and not request.force:
            return DeleteResponse(
                path=request.path,
                deleted=False,
                references=ref_paths,
                message=f"Cannot delete: {len(references)} entities reference this. Use force=true to override.",
            )

        # Delete
        deleted = await store.delete(request.path)

        return DeleteResponse(
            path=request.path,
            deleted=deleted,
            references=ref_paths,
            message="Entity deleted" if deleted else "Entity not found",
        )

    @router.get("/entity/references", response_model=ReferencesResponse)
    async def get_references(
        path: str = Query(..., description="Entity path"),
    ) -> ReferencesResponse:
        """Get entities that reference the given path."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        references = await store.get_references_to(path)

        return ReferencesResponse(
            path=path,
            referenced_by=references,
            count=len(references),
        )

    @router.get("/entity/{path:path}/status", response_model=EntityStatusResponse)
    async def get_entity_status(path: str) -> EntityStatusResponse | JSONResponse:
        """Get current analysis status for an entity."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        state = await store.get_analysis_state(path)

        if not state:
            return JSONResponse({"path": path, "status": "unknown"})

        return EntityStatusResponse(
            path=path,
            status=state.status.value,
            startedAt=state.started_at,
            completedAt=state.completed_at,
            error=state.error,
            analyzer=state.analyzer,
            refCount=state.ref_count,
            placeholderCount=state.placeholder_count,
        )

    @router.post("/entity/{path:path}/analyze", response_model=AnalyzeCrystalResponse)
    async def analyze_entity(
        path: str,
        force: bool = Query(default=True, description="Force re-analysis even if already analyzed"),
    ) -> AnalyzeCrystalResponse:
        """Trigger LLM analysis for an entity."""
        from services.sovereign.analysis_reactor import get_analysis_reactor

        reactor = get_analysis_reactor()
        if not reactor:
            raise HTTPException(500, "Analysis reactor not initialized")

        crystal = await reactor.analyze(path, force=force)

        return AnalyzeCrystalResponse(
            path=crystal.path,
            refs_found=crystal.refs_found,
            connections_suggested=crystal.connections_suggested,
            concepts=crystal.concepts,
            summary=crystal.summary,
            analyzer=crystal.analyzer,
            analyzed_at=crystal.analyzed_at,
        )

    @router.get("/export")
    async def export_entities(
        paths: str = Query(..., description="Comma-separated paths"),
        format: str = Query(default="zip", description="Export format: json or zip"),
    ) -> Response:
        """Export entities as ZIP or JSON."""
        from services.providers import get_sovereign_store

        store = await get_sovereign_store()
        path_list = [p.strip() for p in paths.split(",") if p.strip()]

        if not path_list:
            raise HTTPException(status_code=400, detail="No paths specified")

        bundle = await store.export_bundle(path_list, format=format)

        if format == "zip":
            return Response(
                content=bundle,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename=sovereign-export-{uuid.uuid4().hex[:8]}.zip"
                },
            )
        else:
            return Response(
                content=bundle,
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=sovereign-export-{uuid.uuid4().hex[:8]}.json"
                },
            )

    # =========================================================================
    # Collection Routes
    # =========================================================================

    @router.get("/collections", response_model=CollectionListResponse)
    async def list_collections(
        parent_id: str | None = Query(default=None, description="Filter by parent"),
    ) -> CollectionListResponse:
        """List all collections."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)
            collections = await service.list_all(parent_id=parent_id)

            return CollectionListResponse(
                collections=[service.to_dict(c) for c in collections],
                total=len(collections),
            )

    @router.post("/collections", response_model=CollectionResponse)
    async def create_collection(
        request: CollectionCreateRequest,
    ) -> CollectionResponse:
        """Create a new collection."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.create(
                name=request.name,
                description=request.description,
                paths=request.paths,
                parent_id=request.parent_id,
            )

            entity_count = await service.get_entity_count(collection.id)

            return CollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                paths=collection.paths,
                parent_id=collection.parent_id,
                analysis_status=collection.analysis_status,
                analyzed_count=collection.analyzed_count,
                entity_count=entity_count,
            )

    @router.get("/collections/{collection_id}", response_model=CollectionResponse)
    async def get_collection(collection_id: str) -> CollectionResponse:
        """Get a collection by ID."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.get(collection_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            entity_count = await service.get_entity_count(collection_id)

            return CollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                paths=collection.paths,
                parent_id=collection.parent_id,
                analysis_status=collection.analysis_status,
                analyzed_count=collection.analyzed_count,
                entity_count=entity_count,
            )

    @router.put("/collections/{collection_id}", response_model=CollectionResponse)
    async def update_collection(
        collection_id: str,
        request: CollectionUpdateRequest,
    ) -> CollectionResponse:
        """Update a collection."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.update(
                collection_id,
                name=request.name,
                description=request.description,
            )

            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            entity_count = await service.get_entity_count(collection_id)

            return CollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                paths=collection.paths,
                parent_id=collection.parent_id,
                analysis_status=collection.analysis_status,
                analyzed_count=collection.analyzed_count,
                entity_count=entity_count,
            )

    @router.delete("/collections/{collection_id}")
    async def delete_collection(collection_id: str) -> dict[str, Any]:
        """Delete a collection (not its contents)."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            deleted = await service.delete(collection_id)

            if not deleted:
                raise HTTPException(status_code=404, detail="Collection not found")

            return {"deleted": True, "collection_id": collection_id}

    @router.post("/collections/{collection_id}/paths", response_model=CollectionResponse)
    async def add_paths_to_collection(
        collection_id: str,
        request: PathsRequest,
    ) -> CollectionResponse:
        """Add paths to a collection."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.add_paths(collection_id, request.paths)

            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            entity_count = await service.get_entity_count(collection_id)

            return CollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                paths=collection.paths,
                parent_id=collection.parent_id,
                analysis_status=collection.analysis_status,
                analyzed_count=collection.analyzed_count,
                entity_count=entity_count,
            )

    @router.delete("/collections/{collection_id}/paths", response_model=CollectionResponse)
    async def remove_paths_from_collection(
        collection_id: str,
        request: PathsRequest,
    ) -> CollectionResponse:
        """Remove paths from a collection."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.remove_paths(collection_id, request.paths)

            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            entity_count = await service.get_entity_count(collection_id)

            return CollectionResponse(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                paths=collection.paths,
                parent_id=collection.parent_id,
                analysis_status=collection.analysis_status,
                analyzed_count=collection.analyzed_count,
                entity_count=entity_count,
            )

    @router.get("/collections/{collection_id}/export")
    async def export_collection(
        collection_id: str,
        format: str = Query(default="zip", description="Export format: json or zip"),
    ) -> Response:
        """Export all entities in a collection."""
        from models import get_async_session
        from services.providers import get_sovereign_store
        from services.sovereign.collection import CollectionService

        async with get_async_session() as session:
            store = await get_sovereign_store()
            service = CollectionService(session, store)

            collection = await service.get(collection_id)
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")

            bundle = await service.export_collection(collection_id, format=format)

            if format == "zip":
                return Response(
                    content=bundle,
                    media_type="application/zip",
                    headers={
                        "Content-Disposition": f"attachment; filename={collection.name}-export.zip"
                    },
                )
            else:
                return Response(
                    content=bundle,
                    media_type="application/json",
                    headers={
                        "Content-Disposition": f"attachment; filename={collection.name}-export.json"
                    },
                )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_sovereign_router",
]
