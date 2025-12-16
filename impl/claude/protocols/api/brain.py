"""
Brain API Endpoints.

Exposes Holographic Brain (Crown Jewel) capabilities via REST API:
- POST /v1/brain/capture - Capture content to holographic memory
- POST /v1/brain/ghost - Surface ghost memories based on context
- GET /v1/brain/map - Get memory cartography/topology
- GET /v1/brain/status - Brain health status

Session 6: Production Brain API for Web UI integration.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

from .models import (
    BrainCaptureRequest,
    BrainCaptureResponse,
    BrainGhostRequest,
    BrainGhostResponse,
    BrainMapResponse,
    BrainStatusResponse,
    GhostMemory,
)

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

logger = logging.getLogger(__name__)

# Graceful FastAPI import
try:
    from fastapi import APIRouter, Depends, HTTPException

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    Depends = None  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


from .auth import get_optional_api_key

# Global Brain Logos instance with thread-safe initialization
_brain_logos: Any = None
_brain_observer: Any = None
_brain_logos_lock = threading.Lock()


def _get_brain_logos() -> tuple[Any, Any]:
    """Get or create the shared Brain Logos instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization. This is important for API servers that may
    handle concurrent requests.

    Returns:
        Tuple of (logos, observer) instances
    """
    global _brain_logos, _brain_observer

    if _brain_logos is None:
        with _brain_logos_lock:
            # Double-check after acquiring lock
            if _brain_logos is None:
                from protocols.agentese import create_brain_logos
                from protocols.agentese.node import Observer

                _brain_logos = create_brain_logos(embedder_type="auto")
                _brain_observer = Observer.guest()

    return _brain_logos, _brain_observer


def create_brain_router() -> "APIRouter | None":
    """
    Create Brain API router.

    Returns:
        FastAPI router with brain endpoints, or None if FastAPI not available
    """
    if not HAS_FASTAPI:
        return None

    router = APIRouter(prefix="/v1/brain", tags=["brain"])

    @router.post("/capture", response_model=BrainCaptureResponse)
    async def capture_content(
        request: BrainCaptureRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> BrainCaptureResponse:
        """
        Capture content to holographic memory.

        Uses semantic embeddings (sentence-transformers if available)
        to store content in the Brain's MemoryCrystal.

        Example:
            POST /v1/brain/capture
            {
                "content": "Python is great for machine learning",
                "metadata": {"source": "meeting"}
            }

        Returns:
            Capture result with concept_id
        """
        try:
            logos, observer = _get_brain_logos()

            kwargs: dict[str, Any] = {"content": request.content}
            if request.concept_id:
                kwargs["concept_id"] = request.concept_id
            if request.metadata:
                kwargs["metadata"] = request.metadata

            result = await logos.invoke("self.memory.capture", observer, **kwargs)

            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return BrainCaptureResponse(
                status=result.get("status", "captured"),
                concept_id=result.get("concept_id", "unknown"),
                storage=result.get("storage", "unknown"),
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Brain capture failed")
            raise HTTPException(status_code=500, detail=f"Capture failed: {e}")

    @router.post("/ghost", response_model=BrainGhostResponse)
    async def surface_ghosts(
        request: BrainGhostRequest,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> BrainGhostResponse:
        """
        Surface ghost memories based on context.

        Uses semantic similarity to find relevant memories
        that may have been forgotten.

        Example:
            POST /v1/brain/ghost
            {
                "context": "machine learning algorithms",
                "limit": 5
            }

        Returns:
            List of surfaced memories with relevance scores
        """
        try:
            logos, observer = _get_brain_logos()

            result = await logos.invoke(
                "self.memory.ghost.surface",
                observer,
                context=request.context,
                limit=request.limit,
            )

            surfaced_memories = []
            for item in result.get("surfaced", []):
                surfaced_memories.append(
                    GhostMemory(
                        concept_id=item.get("concept_id", "unknown"),
                        content=item.get("content"),
                        relevance=item.get("relevance", 0.5),
                    )
                )

            return BrainGhostResponse(
                status=result.get("status", "surfaced"),
                context=request.context,
                surfaced=surfaced_memories,
                count=result.get("count", len(surfaced_memories)),
            )
        except Exception as e:
            logger.exception("Brain ghost surfacing failed")
            raise HTTPException(status_code=500, detail=f"Ghost surfacing failed: {e}")

    @router.get("/map", response_model=BrainMapResponse)
    async def get_brain_map(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> BrainMapResponse:
        """
        Get memory cartography/topology.

        Returns information about the memory landscape including
        concept count, landmarks, and topology summary.

        Example:
            GET /v1/brain/map

        Returns:
            Memory topology information
        """
        try:
            logos, observer = _get_brain_logos()

            result = await logos.invoke("self.memory.cartography.manifest", observer)

            # Extract stats from result
            metadata = getattr(result, "metadata", {}) if result else {}
            summary = (
                getattr(result, "summary", "No topology available")
                if result
                else "No topology available"
            )

            # Get crystal stats directly
            resolvers = logos._context_resolvers
            self_resolver = resolvers.get("self")
            memory_node = getattr(self_resolver, "_memory", None)
            crystal = (
                getattr(memory_node, "_memory_crystal", None) if memory_node else None
            )

            concept_count = 0
            hot_patterns = 0
            dimension = 384

            if crystal:
                concept_count = len(getattr(crystal, "_patterns", {}))
                hot_patterns = len(getattr(crystal, "_hot_patterns", set()))
                dimension = getattr(crystal, "_dimension", 384)

            return BrainMapResponse(
                summary=str(summary),
                concept_count=concept_count,
                landmarks=metadata.get("landmarks", 0),
                hot_patterns=hot_patterns,
                dimension=dimension,
            )
        except Exception as e:
            logger.exception("Brain map failed")
            raise HTTPException(status_code=500, detail=f"Map failed: {e}")

    @router.get("/status", response_model=BrainStatusResponse)
    async def get_brain_status(
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> BrainStatusResponse:
        """
        Get brain health status.

        Returns information about the brain subsystems including
        embedder type, dimensions, and concept count.

        Example:
            GET /v1/brain/status

        Returns:
            Brain health status
        """
        try:
            logos, observer = _get_brain_logos()

            # Get internal state
            resolvers = logos._context_resolvers
            self_resolver = resolvers.get("self")
            memory_node = getattr(self_resolver, "_memory", None)
            crystal = (
                getattr(memory_node, "_memory_crystal", None) if memory_node else None
            )
            embedder = getattr(memory_node, "_embedder", None) if memory_node else None
            cartographer = getattr(self_resolver, "_cartographer", None)

            # Determine status
            status = "healthy"
            if crystal is None:
                status = "degraded"
            if embedder is None and crystal is None:
                status = "unavailable"

            # Get embedder info
            embedder_type = type(embedder).__name__ if embedder else "None"
            embedder_dimension = getattr(embedder, "dimension", 64) if embedder else 64

            # Get concept count
            concept_count = 0
            if crystal:
                concept_count = len(getattr(crystal, "_patterns", {}))

            return BrainStatusResponse(
                status=status,
                embedder_type=embedder_type,
                embedder_dimension=embedder_dimension,
                concept_count=concept_count,
                has_cartographer=cartographer is not None,
            )
        except Exception as e:
            logger.exception("Brain status check failed")
            raise HTTPException(status_code=500, detail=f"Status check failed: {e}")

    return router
