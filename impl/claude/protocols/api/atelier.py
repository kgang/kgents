"""
Atelier API Endpoints (Phase 5).

REST API for Tiny Atelier with SSE streaming:
- POST /api/atelier/commission       - Commission artisan (SSE stream)
- GET  /api/atelier/gallery          - List pieces
- GET  /api/atelier/gallery/{id}     - Get piece with provenance
- GET  /api/atelier/gallery/{id}/lineage - Get inspiration graph
- POST /api/atelier/collaborate      - Multi-artisan collaboration (SSE stream)
- POST /api/atelier/queue            - Queue commission
- GET  /api/atelier/queue/pending    - Get pending queue
- POST /api/atelier/queue/process    - Process queue
- GET  /api/atelier/artisans         - List available artisans
- GET  /api/atelier/commission/{id}/status - Fallback polling for commission status

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from fastapi import APIRouter

logger = logging.getLogger(__name__)

# =============================================================================
# SSE Configuration
# =============================================================================

HEARTBEAT_INTERVAL_SECONDS = 15  # Send heartbeat every 15s
SSE_TIMEOUT_SECONDS = 30  # Client should fallback if no event in 30s

# In-memory commission status tracking for fallback polling
# In production, use Redis or similar for multi-instance support
_commission_status: dict[str, dict[str, Any]] = {}


def _update_commission_status(
    commission_id: str,
    status: str,
    piece: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    """Update commission status for fallback polling."""
    _commission_status[commission_id] = {
        "status": status,
        "piece": piece,
        "error": error,
        "updated_at": datetime.now().isoformat(),
    }


def _get_commission_status(commission_id: str) -> dict[str, Any] | None:
    """Get commission status for fallback polling."""
    return _commission_status.get(commission_id)


# Graceful FastAPI import
try:
    from fastapi import APIRouter, HTTPException, Query
    from fastapi.responses import StreamingResponse
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = Exception  # type: ignore
    Query = None  # type: ignore
    BaseModel = object  # type: ignore
    StreamingResponse = None  # type: ignore

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None


# --- Pydantic Models ---


class CommissionRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to commission an artisan."""

    artisan: str = Field(..., description="Artisan name", examples=["calligrapher"])
    request: str = Field(
        ..., description="What to create", examples=["a haiku about persistence"]
    )
    patron: str = Field(default="wanderer", description="Patron name for provenance")


class CollaborateRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request for multi-artisan collaboration."""

    artisans: list[str] = Field(..., description="Artisan names", min_length=1)
    request: str = Field(..., description="What to create together")
    mode: str = Field(
        default="duet",
        description="Collaboration mode: duet, ensemble, refinement, chain",
    )
    patron: str = Field(default="wanderer", description="Patron name")


class QueueRequest(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Request to queue a commission."""

    artisan: str = Field(..., description="Artisan name")
    request: str = Field(..., description="What to create")
    patron: str = Field(default="wanderer", description="Patron name")


class ArtisanResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Artisan information."""

    name: str = Field(..., description="Artisan name")
    specialty: str = Field(..., description="What they create")
    personality: str = Field(default="", description="Brief personality")


class ArtisansResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """List of available artisans."""

    artisans: list[ArtisanResponse] = Field(..., description="Available artisans")
    total: int = Field(..., description="Total artisan count")


class PieceSummary(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Summary of a piece."""

    id: str = Field(..., description="Piece ID")
    artisan: str = Field(..., description="Creating artisan")
    form: str = Field(..., description="Form (haiku, letter, map, etc.)")
    preview: str = Field(..., description="Content preview (50 chars)")
    interpretation: str = Field(..., description="Artisan's interpretation")
    created_at: str = Field(..., description="Creation timestamp")


class GalleryResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Gallery listing response."""

    pieces: list[PieceSummary] = Field(..., description="Pieces in gallery")
    total: int = Field(..., description="Total piece count")


class ProvenanceResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Provenance information."""

    interpretation: str = Field(..., description="Artisan's interpretation")
    considerations: list[str] = Field(..., description="What artisan considered")
    choices: list[dict[str, Any]] = Field(..., description="Creative choices")
    inspirations: list[str] = Field(..., description="Inspiration piece IDs")


class PieceResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Full piece with provenance."""

    id: str = Field(..., description="Piece ID")
    content: Any = Field(..., description="Piece content")
    artisan: str = Field(..., description="Creating artisan")
    commission_id: str = Field(..., description="Original commission ID")
    form: str = Field(..., description="Form")
    provenance: ProvenanceResponse = Field(..., description="Creative provenance")
    created_at: str = Field(..., description="Creation timestamp")


class LineageNodeResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Node in lineage graph."""

    piece_id: str = Field(..., description="Piece ID")
    artisan: str = Field(..., description="Artisan name")
    preview: str = Field(..., description="Content preview")
    depth: int = Field(..., description="Depth from root")


class LineageResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Lineage graph response."""

    piece_id: str = Field(..., description="Root piece ID")
    ancestors: list[LineageNodeResponse] = Field(..., description="Inspiration sources")
    descendants: list[LineageNodeResponse] = Field(..., description="Inspired pieces")


class QueueItemResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Queued commission item."""

    commission_id: str = Field(..., description="Commission ID")
    artisan: str = Field(..., description="Target artisan")
    request: str = Field(..., description="Commission request")
    patron: str = Field(..., description="Patron name")
    queued_at: str = Field(..., description="Queue timestamp")


class PendingResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Pending queue response."""

    items: list[QueueItemResponse] = Field(..., description="Pending commissions")
    total: int = Field(..., description="Total pending count")


class CommissionQueuedResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """Response when commission is queued."""

    commission_id: str = Field(..., description="Commission ID")
    artisan: str = Field(..., description="Target artisan")
    status: str = Field(default="queued", description="Status")


class CommissionStatusResponse(BaseModel if HAS_FASTAPI else object):  # type: ignore[misc]
    """
    Fallback polling response for commission status.

    Use when SSE streaming is unavailable or timed out.
    """

    commission_id: str = Field(..., description="Commission ID")
    status: str = Field(
        ...,
        description="Status: pending, contemplating, working, complete, error",
    )
    piece: Optional[PieceResponse] = Field(
        None, description="Completed piece if status is 'complete'"
    )
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
    updated_at: str = Field(..., description="Last update timestamp")
    sse_timeout_hint: int = Field(
        default=SSE_TIMEOUT_SECONDS,
        description="Suggested timeout for SSE connection before polling",
    )


# --- Router Factory ---


def create_atelier_router() -> "APIRouter | None":
    """
    Create the Atelier API router.

    Returns None if FastAPI is not available.
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/atelier", tags=["atelier"])

    @router.get("/artisans", response_model=ArtisansResponse)
    async def list_artisans() -> ArtisansResponse:
        """List available artisans."""
        from agents.atelier.artisans import ARTISAN_REGISTRY

        artisans = []
        for name, cls in ARTISAN_REGISTRY.items():
            artisan = cls()
            artisans.append(
                ArtisanResponse(
                    name=artisan.name,
                    specialty=artisan.specialty,
                    personality=artisan.personality[:100]
                    if artisan.personality
                    else "",
                )
            )

        return ArtisansResponse(artisans=artisans, total=len(artisans))

    @router.post("/commission")
    async def commission(request: CommissionRequest) -> StreamingResponse:
        """
        Commission an artisan, streaming events via SSE.

        Events:
        - commission_received: Commission accepted
        - contemplating: Artisan thinking
        - working: Creation in progress
        - fragment: Partial content
        - piece_complete: Final piece (data.piece contains full piece)
        - heartbeat: Keep-alive signal (every 15s)
        - error: Error occurred

        Resilience:
        - Heartbeats sent every 15s to detect connection drops
        - If no event for 30s, client should fallback to polling
        - Use GET /api/atelier/commission/{id}/status for fallback
        """
        from agents.atelier.artisan import AtelierEvent, AtelierEventType
        from agents.atelier.workshop import get_workshop

        workshop = get_workshop()
        commission_id: str | None = None

        async def generate() -> AsyncIterator[str]:
            nonlocal commission_id

            # Create heartbeat task
            async def heartbeat_generator() -> AsyncIterator[AtelierEvent]:
                """Generate heartbeat events every HEARTBEAT_INTERVAL_SECONDS."""
                while True:
                    await asyncio.sleep(HEARTBEAT_INTERVAL_SECONDS)
                    yield AtelierEvent(
                        event_type=AtelierEventType.HEARTBEAT,
                        artisan=request.artisan,
                        commission_id=commission_id,
                        message="keep-alive",
                    )

            # Merge workshop events with heartbeats
            workshop_gen = workshop.flux.commission(
                artisan_name=request.artisan,
                request=request.request,
                patron=request.patron,
            )

            # Use asyncio to race between workshop events and heartbeats
            heartbeat_task: asyncio.Task[AtelierEvent] | None = None
            workshop_task: asyncio.Task[AtelierEvent | None] | None = None

            try:
                workshop_iter = workshop_gen.__aiter__()
                heartbeat_iter = heartbeat_generator().__aiter__()

                while True:
                    # Create tasks if needed
                    if workshop_task is None:
                        workshop_task = asyncio.create_task(
                            workshop_iter.__anext__()  # type: ignore
                        )
                    if heartbeat_task is None:
                        heartbeat_task = asyncio.create_task(
                            heartbeat_iter.__anext__()  # type: ignore
                        )

                    # Wait for either
                    done, _ = await asyncio.wait(
                        {workshop_task, heartbeat_task},
                        return_when=asyncio.FIRST_COMPLETED,
                    )

                    for task in done:
                        try:
                            event = task.result()
                        except StopAsyncIteration:
                            # Workshop finished
                            if heartbeat_task and not heartbeat_task.done():
                                heartbeat_task.cancel()
                            return

                        # Skip None events (shouldn't happen but type-safe)
                        if event is None:
                            continue

                        # Track commission ID for status updates
                        if (
                            event.event_type == AtelierEventType.COMMISSION_RECEIVED
                            and event.commission_id
                        ):
                            commission_id = event.commission_id
                            _update_commission_status(commission_id, "pending")

                        # Update status tracking
                        if commission_id:
                            if event.event_type == AtelierEventType.CONTEMPLATING:
                                _update_commission_status(
                                    commission_id, "contemplating"
                                )
                            elif event.event_type == AtelierEventType.WORKING:
                                _update_commission_status(commission_id, "working")
                            elif event.event_type == AtelierEventType.PIECE_COMPLETE:
                                _update_commission_status(
                                    commission_id,
                                    "complete",
                                    piece=event.data.get("piece"),
                                )
                            elif event.event_type == AtelierEventType.ERROR:
                                _update_commission_status(
                                    commission_id, "error", error=event.message
                                )

                        # Emit event
                        event_data = event.to_dict()
                        yield f"event: {event.event_type.value}\n"
                        yield f"data: {json.dumps(event_data)}\n\n"

                        # Reset the completed task
                        if task is workshop_task:
                            workshop_task = None
                        else:
                            heartbeat_task = None

            except asyncio.CancelledError:
                pass
            finally:
                # Cleanup
                if heartbeat_task and not heartbeat_task.done():
                    heartbeat_task.cancel()
                if workshop_task and not workshop_task.done():
                    workshop_task.cancel()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "X-SSE-Timeout-Hint": str(SSE_TIMEOUT_SECONDS),
            },
        )

    @router.post("/collaborate")
    async def collaborate(request: CollaborateRequest) -> StreamingResponse:
        """
        Multi-artisan collaboration via SSE stream.

        Modes:
        - duet: First creates, second transforms
        - ensemble: All create in parallel, results merged
        - refinement: First creates, second refines
        - chain: Sequential pipeline
        """
        from agents.atelier.workshop import get_workshop

        workshop = get_workshop()

        async def generate() -> AsyncIterator[str]:
            async for event in workshop.flux.collaborate(
                artisan_names=request.artisans,
                request=request.request,
                mode=request.mode,
                patron=request.patron,
            ):
                event_data = event.to_dict()
                yield f"event: {event.event_type.value}\n"
                yield f"data: {json.dumps(event_data)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get(
        "/commission/{commission_id}/status", response_model=CommissionStatusResponse
    )
    async def get_commission_status(commission_id: str) -> CommissionStatusResponse:
        """
        Fallback polling endpoint for commission status.

        Use this when:
        - SSE connection is unavailable
        - SSE stream timed out (no event in 30s)
        - Client doesn't support SSE

        Poll interval recommendation: 2-5 seconds
        """
        status_data = _get_commission_status(commission_id)

        if not status_data:
            # Check if there's a piece with this commission ID in the gallery
            from agents.atelier.gallery.store import get_gallery

            gallery = get_gallery()
            piece = await gallery.get_by_commission(commission_id)

            if piece:
                return CommissionStatusResponse(
                    commission_id=commission_id,
                    status="complete",
                    piece=PieceResponse(
                        id=piece.id,
                        content=piece.content,
                        artisan=piece.artisan,
                        commission_id=piece.commission_id,
                        form=piece.form,
                        provenance=ProvenanceResponse(
                            interpretation=piece.provenance.interpretation,
                            considerations=piece.provenance.considerations,
                            choices=[c.to_dict() for c in piece.provenance.choices],
                            inspirations=piece.provenance.inspirations,
                        ),
                        created_at=piece.created_at.isoformat(),
                    ),
                    error=None,
                    updated_at=piece.created_at.isoformat(),
                    sse_timeout_hint=SSE_TIMEOUT_SECONDS,
                )

            raise HTTPException(
                status_code=404,
                detail=f"Commission {commission_id} not found. It may not have started yet.",
            )

        # Build response from tracked status
        piece_response = None
        if status_data.get("piece"):
            piece_data = status_data["piece"]
            piece_response = PieceResponse(
                id=piece_data["id"],
                content=piece_data["content"],
                artisan=piece_data["artisan"],
                commission_id=piece_data["commission_id"],
                form=piece_data.get("form", "reflection"),
                provenance=ProvenanceResponse(
                    interpretation=piece_data.get("provenance", {}).get(
                        "interpretation", ""
                    ),
                    considerations=piece_data.get("provenance", {}).get(
                        "considerations", []
                    ),
                    choices=piece_data.get("provenance", {}).get("choices", []),
                    inspirations=piece_data.get("provenance", {}).get(
                        "inspirations", []
                    ),
                ),
                created_at=piece_data.get("created_at", ""),
            )

        return CommissionStatusResponse(
            commission_id=commission_id,
            status=status_data["status"],
            piece=piece_response,
            error=status_data.get("error"),
            updated_at=status_data["updated_at"],
            sse_timeout_hint=SSE_TIMEOUT_SECONDS,
        )

    @router.get("/gallery", response_model=GalleryResponse)
    async def list_gallery(
        artisan: Optional[str] = Query(None, description="Filter by artisan"),
        form: Optional[str] = Query(None, description="Filter by form"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
    ) -> GalleryResponse:
        """List pieces in the gallery."""
        from agents.atelier.gallery.store import get_gallery

        gallery = get_gallery()
        pieces = await gallery.list_pieces(
            artisan=artisan, form=form, limit=limit, offset=offset
        )
        total = await gallery.count(artisan=artisan, form=form)

        summaries = []
        for piece in pieces:
            preview = str(piece.content)[:50].replace("\n", " ")
            if len(str(piece.content)) > 50:
                preview += "..."
            summaries.append(
                PieceSummary(
                    id=piece.id,
                    artisan=piece.artisan,
                    form=piece.form,
                    preview=preview,
                    interpretation=piece.provenance.interpretation[:100],
                    created_at=piece.created_at.isoformat(),
                )
            )

        return GalleryResponse(pieces=summaries, total=total)

    # Note: Search endpoint MUST come before /gallery/{piece_id} to avoid route conflict
    @router.get("/gallery/search")
    async def search_gallery(
        query: str = Query(..., description="Search query"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
    ) -> GalleryResponse:
        """Search pieces by content or interpretation."""
        from agents.atelier.gallery.store import get_gallery

        gallery = get_gallery()
        results = await gallery.search_content(query, limit=limit)

        summaries = []
        for piece in results:
            preview = str(piece.content)[:50].replace("\n", " ")
            if len(str(piece.content)) > 50:
                preview += "..."
            summaries.append(
                PieceSummary(
                    id=piece.id,
                    artisan=piece.artisan,
                    form=piece.form,
                    preview=preview,
                    interpretation=piece.provenance.interpretation[:100],
                    created_at=piece.created_at.isoformat(),
                )
            )

        return GalleryResponse(pieces=summaries, total=len(summaries))

    @router.get("/gallery/{piece_id}", response_model=PieceResponse)
    async def get_piece(piece_id: str) -> PieceResponse:
        """Get a piece with full provenance."""
        from agents.atelier.gallery.store import get_gallery

        gallery = get_gallery()
        piece = await gallery.get(piece_id)

        if not piece:
            raise HTTPException(status_code=404, detail=f"Piece {piece_id} not found")

        return PieceResponse(
            id=piece.id,
            content=piece.content,
            artisan=piece.artisan,
            commission_id=piece.commission_id,
            form=piece.form,
            provenance=ProvenanceResponse(
                interpretation=piece.provenance.interpretation,
                considerations=piece.provenance.considerations,
                choices=[c.to_dict() for c in piece.provenance.choices],
                inspirations=piece.provenance.inspirations,
            ),
            created_at=piece.created_at.isoformat(),
        )

    @router.get("/gallery/{piece_id}/lineage", response_model=LineageResponse)
    async def get_lineage(piece_id: str) -> LineageResponse:
        """Get the creative lineage of a piece."""
        from agents.atelier.gallery.lineage import LineageGraph
        from agents.atelier.gallery.store import get_gallery

        gallery = get_gallery()
        piece = await gallery.get(piece_id)

        if not piece:
            raise HTTPException(status_code=404, detail=f"Piece {piece_id} not found")

        # Build lineage graph from all pieces
        all_pieces = await gallery.list_pieces(limit=100)
        graph = LineageGraph.from_pieces(all_pieces)

        ancestors = graph.get_ancestors(piece_id)
        descendants = graph.get_descendants(piece_id)

        # Calculate depth for each node relative to root piece
        def get_depth_from_root(
            nodes: list[Any], root_id: str, direction: str
        ) -> list[tuple[Any, int]]:
            """Calculate depth from root for each node."""
            result = []
            for i, node in enumerate(nodes):
                # Simple heuristic: enumerate order approximates depth
                # In a real implementation, we'd track depth during traversal
                result.append((node, i + 1))
            return result

        ancestor_depths = get_depth_from_root(ancestors, piece_id, "up")
        descendant_depths = get_depth_from_root(descendants, piece_id, "down")

        return LineageResponse(
            piece_id=piece_id,
            ancestors=[
                LineageNodeResponse(
                    piece_id=node.piece_id,
                    artisan=node.artisan,
                    preview=node.preview,
                    depth=depth,
                )
                for node, depth in ancestor_depths
            ],
            descendants=[
                LineageNodeResponse(
                    piece_id=node.piece_id,
                    artisan=node.artisan,
                    preview=node.preview,
                    depth=depth,
                )
                for node, depth in descendant_depths
            ],
        )

    @router.delete("/gallery/{piece_id}")
    async def delete_piece(piece_id: str) -> dict[str, str]:
        """Delete a piece from the gallery."""
        from agents.atelier.gallery.store import get_gallery

        gallery = get_gallery()
        deleted = await gallery.delete(piece_id)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Piece {piece_id} not found")

        return {"status": "deleted", "piece_id": piece_id}

    @router.post("/queue", response_model=CommissionQueuedResponse)
    async def queue_commission(request: QueueRequest) -> CommissionQueuedResponse:
        """Queue a commission for background processing."""
        from agents.atelier.artisans import get_artisan
        from agents.atelier.workshop import get_workshop

        # Validate artisan
        if not get_artisan(request.artisan):
            raise HTTPException(
                status_code=400, detail=f"Unknown artisan: {request.artisan}"
            )

        workshop = get_workshop()
        commission = await workshop.queue_commission(
            artisan_name=request.artisan,
            request=request.request,
            patron=request.patron,
        )

        return CommissionQueuedResponse(
            commission_id=commission.id,
            artisan=request.artisan,
            status="queued",
        )

    @router.get("/queue/pending", response_model=PendingResponse)
    async def get_pending() -> PendingResponse:
        """Get pending commissions in queue."""
        from agents.atelier.workshop.commission import get_queue

        queue = get_queue()
        items = await queue.pending()

        queue_items = []
        for item in items:
            queue_items.append(
                QueueItemResponse(
                    commission_id=item.commission.id,
                    artisan=item.artisan_name,
                    request=item.commission.request,
                    patron=item.commission.patron,
                    queued_at=item.queued_at.isoformat(),
                )
            )

        return PendingResponse(items=queue_items, total=len(queue_items))

    @router.post("/queue/process")
    async def process_queue(
        all_items: bool = Query(False, alias="all", description="Process all pending"),
    ) -> StreamingResponse:
        """
        Process queued commissions, streaming events via SSE.

        Use ?all=true to process all pending items.
        """
        from agents.atelier.workshop.commission import get_queue

        queue = get_queue()

        async def generate() -> AsyncIterator[str]:
            if all_items:
                async for event in queue.process_all():
                    event_data = event.to_dict()
                    yield f"event: {event.event_type.value}\n"
                    yield f"data: {json.dumps(event_data)}\n\n"
            else:
                async for event in queue.process_one():
                    event_data = event.to_dict()
                    yield f"event: {event.event_type.value}\n"
                    yield f"data: {json.dumps(event_data)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.get("/status")
    async def get_status() -> dict[str, Any]:
        """Get workshop status and statistics."""
        from agents.atelier.gallery.store import get_gallery
        from agents.atelier.workshop import get_workshop
        from agents.atelier.workshop.commission import get_queue

        workshop = get_workshop()
        gallery = get_gallery()
        queue = get_queue()

        pending_items = await queue.pending()
        total_pieces = await gallery.count()

        return {
            "status": "active",
            "total_commissions": workshop.flux.total_commissions,
            "total_pieces": total_pieces,
            "pending_queue": len(pending_items),
            "available_artisans": list(
                workshop.flux.get_status()["available_artisans"]
            ),
            "event_bus_subscribers": workshop.flux.event_bus.subscriber_count,
        }

    return router


# --- Exports ---


__all__ = [
    "create_atelier_router",
    "CommissionRequest",
    "CollaborateRequest",
    "QueueRequest",
    "ArtisanResponse",
    "ArtisansResponse",
    "PieceSummary",
    "GalleryResponse",
    "PieceResponse",
    "LineageResponse",
    "CommissionStatusResponse",
    "HEARTBEAT_INTERVAL_SECONDS",
    "SSE_TIMEOUT_SECONDS",
]
