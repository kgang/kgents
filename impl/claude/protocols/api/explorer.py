"""
Explorer REST API: SSE stream for real-time unified events.

Provides:
- GET /api/explorer/stream - SSE for real-time events from WitnessSynergyBus

The radical simplification: Instead of creating a separate ExplorerBus,
we subscribe to the existing WitnessSynergyBus with wildcard `witness.*`
and normalize events to UnifiedEvent format.

Why this works:
- WitnessSynergyBus already publishes mark, crystal, trail, spec events
- All kgents data flows through witness (Law 3: every action emits Mark)
- Zero new infrastructure, maximum reuse

> *"The file is a lie. There is only the graph."*

See: plans/hidden-crunching-ripple.md (Brain Page Redesign)
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator

try:
    from fastapi import APIRouter, Query
    from fastapi.responses import StreamingResponse

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    Query = None  # type: ignore
    StreamingResponse = None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Topic to EntityType Mapping
# =============================================================================


def _topic_to_entity_type(topic: str) -> str:
    """
    Map WitnessSynergyBus topic to Explorer EntityType.

    The witness bus uses topics like:
    - witness.mark.* → mark
    - witness.crystal.* → crystal
    - witness.trail.* → trail
    - witness.thought.* → mark (thoughts become marks)
    - witness.kblock.* → mark (K-Block edits become marks)
    - witness.spec.* → evidence (spec events are verification evidence)
    - witness.agentese.* → mark (AGENTESE invocations are marks)
    - witness.proxy.* → evidence (proxy events are computation evidence)
    - witness.sovereign.* → evidence (sovereign analysis events)
    """
    topic_lower = topic.lower()

    # Direct mappings
    if "crystal" in topic_lower:
        return "crystal"
    if "trail" in topic_lower:
        return "trail"
    if "teaching" in topic_lower:
        return "teaching"
    if "lemma" in topic_lower:
        return "lemma"

    # Evidence-like events
    if any(x in topic_lower for x in ("spec", "proxy", "sovereign", "verification")):
        return "evidence"

    # Everything else is a mark (default)
    return "mark"


def _normalize_event(topic: str, event: Any) -> dict[str, Any]:
    """
    Normalize a WitnessSynergyBus event to UnifiedEvent shape.

    The frontend expects:
    {
        "id": "...",
        "type": "mark" | "crystal" | "trail" | "evidence" | "teaching" | "lemma",
        "title": "...",
        "summary": "...",
        "timestamp": "ISO 8601",
        "metadata": {...}
    }
    """
    entity_type = _topic_to_entity_type(topic)

    if not isinstance(event, dict):
        # Wrap non-dict events
        return {
            "id": f"event-{datetime.now().timestamp()}",
            "type": entity_type,
            "title": str(event)[:100],
            "summary": str(event)[:200],
            "timestamp": datetime.now().isoformat(),
            "metadata": {"raw": str(event), "topic": topic},
        }

    # Extract common fields with fallbacks
    event_id = (
        event.get("id")
        or event.get("mark_id")
        or event.get("crystal_id")
        or event.get("entity_id")
        or f"event-{datetime.now().timestamp()}"
    )

    title = (
        event.get("title")
        or event.get("action")
        or event.get("content", "")[:100]
        or event.get("message", "")[:100]
        or topic.split(".")[-1]
    )

    summary = (
        event.get("summary")
        or event.get("reasoning")
        or event.get("content", "")[:200]
        or event.get("message", "")[:200]
        or ""
    )

    timestamp = (
        event.get("timestamp")
        or event.get("created_at")
        or event.get("captured_at")
        or datetime.now().isoformat()
    )

    # Ensure timestamp is string
    if hasattr(timestamp, "isoformat"):
        timestamp = timestamp.isoformat()

    return {
        "id": str(event_id),
        "type": entity_type,
        "title": str(title)[:100],
        "summary": str(summary)[:200],
        "timestamp": str(timestamp),
        "metadata": {
            "topic": topic,
            **{k: v for k, v in event.items() if k not in ("id", "title", "summary", "timestamp")},
        },
    }


# =============================================================================
# Router Factory
# =============================================================================


def create_explorer_router() -> "APIRouter | None":
    """Create the explorer API router."""
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/api/explorer", tags=["explorer"])

    @router.get("/stream")
    async def stream_events(
        types: str | None = Query(
            default=None, description="Comma-separated entity types to filter"
        ),
    ) -> StreamingResponse:
        """
        SSE stream for real-time unified events.

        Subscribes to WitnessSynergyBus with wildcard `witness.*` and normalizes
        all events to UnifiedEvent format for the Brain page.

        Args:
            types: Optional comma-separated types to filter (mark,crystal,trail,evidence,teaching,lemma)

        Event-driven via WitnessSynergyBus - instant delivery, no polling.

        > *"The proof IS the decision. The mark IS the witness."*
        """
        # Parse type filter
        type_filter: set[str] | None = None
        if types:
            type_filter = {t.strip().lower() for t in types.split(",") if t.strip()}

        async def generate() -> AsyncGenerator[str, None]:
            """Generate SSE events from WitnessSynergyBus subscription."""
            from services.witness.bus import WitnessTopics, get_synergy_bus

            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'type': 'connected'})}\n\n"

            bus = get_synergy_bus()
            event_queue: asyncio.Queue[tuple[str, Any]] = asyncio.Queue()

            # Subscribe to all witness events
            async def on_event(topic: str, event: Any) -> None:
                await event_queue.put((topic, event))

            unsub = bus.subscribe(WitnessTopics.ALL, on_event)

            try:
                while True:
                    try:
                        # Wait for event with 30s timeout for heartbeat
                        topic, event = await asyncio.wait_for(
                            event_queue.get(),
                            timeout=30.0,
                        )

                        # Normalize to UnifiedEvent
                        normalized = _normalize_event(topic, event)
                        entity_type = normalized["type"]

                        # Apply type filter if specified
                        if type_filter and entity_type not in type_filter:
                            continue

                        # Yield SSE event
                        yield f"event: {entity_type}\ndata: {json.dumps(normalized)}\n\n"

                    except asyncio.TimeoutError:
                        # Heartbeat on timeout
                        yield f"event: heartbeat\ndata: {json.dumps({'type': 'heartbeat', 'time': datetime.now().isoformat()})}\n\n"

            except asyncio.CancelledError:
                yield f"event: disconnected\ndata: {json.dumps({'status': 'disconnected'})}\n\n"
            except Exception as e:
                logger.exception("Error in explorer stream")
                yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            finally:
                unsub()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    @router.get("/list")
    async def list_events(
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        types: str | None = Query(default=None, description="Comma-separated entity types"),
        author: str | None = Query(default=None),
    ) -> dict[str, Any]:
        """
        List unified events with pagination.

        This REST endpoint wraps UnifiedQueryService.list_events() for
        frontend polling fallback when SSE isn't available.

        Args:
            limit: Max events to return (1-200)
            offset: Pagination offset
            types: Comma-separated types (mark,crystal,trail,evidence,teaching,lemma)
            author: Filter by author
        """
        try:
            from services.explorer.contracts import EntityType, ListEventsRequest, StreamFilters
            from services.providers import get_unified_query_service

            service = await get_unified_query_service()

            # Build filters
            filters = None
            if types or author:
                parsed_types = []
                if types:
                    for t in types.split(","):
                        try:
                            parsed_types.append(EntityType(t.strip().lower()))
                        except ValueError:
                            pass  # Skip invalid types

                filters = StreamFilters(
                    types=parsed_types,
                    author=author,
                )

            request = ListEventsRequest(
                filters=filters,
                limit=limit,
                offset=offset,
            )
            response = await service.list_events(request)

            return {
                "events": [e.to_dict() for e in response.events],
                "total": response.total,
                "has_more": response.has_more,
            }
        except Exception as e:
            logger.exception("Error listing events")
            return {
                "events": [],
                "total": 0,
                "has_more": False,
                "error": str(e),
            }

    @router.get("/health")
    async def explorer_health() -> dict[str, Any]:
        """
        Explorer health check.

        Returns status of explorer service and connected buses.
        """
        try:
            from services.providers import get_unified_query_service
            from services.witness.bus import get_synergy_bus

            service = await get_unified_query_service()
            manifest = await service.manifest()
            bus = get_synergy_bus()

            return {
                "status": "ok",
                "total_events": manifest.total_events,
                "counts_by_type": manifest.counts_by_type,
                "storage_backend": manifest.storage_backend,
                "bus_stats": bus.stats,
            }
        except Exception as e:
            logger.exception("Explorer health check failed")
            return {
                "status": "error",
                "error": str(e),
            }

    return router


__all__ = ["create_explorer_router"]
