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
    BrainTopologyResponse,
    GhostMemory,
    TopologyEdge,
    TopologyGap,
    TopologyNode,
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

# Test hook: override to inject a mock logos instance
_brain_logos_factory: Any = None


def _get_brain_logos() -> tuple[Any, Any]:
    """Get or create the shared Brain Logos instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization. This is important for API servers that may
    handle concurrent requests.

    Tests can inject a factory via _set_brain_logos_factory() to avoid
    network calls and global state mutation.

    Returns:
        Tuple of (logos, observer) instances
    """
    global _brain_logos, _brain_observer, _brain_logos_factory

    if _brain_logos is None:
        with _brain_logos_lock:
            # Double-check after acquiring lock
            if _brain_logos is None:
                from protocols.agentese.node import Observer

                if _brain_logos_factory is not None:
                    # Test injection: use factory
                    _brain_logos = _brain_logos_factory()
                else:
                    # Production: use auto embedder
                    from protocols.agentese import create_brain_logos

                    _brain_logos = create_brain_logos(embedder_type="auto")
                _brain_observer = Observer.guest()

    return _brain_logos, _brain_observer


def _set_brain_logos_factory(factory: Any) -> None:
    """Set a factory function for brain logos (test hook).

    Call with None to reset to default behavior.

    Args:
        factory: Callable that returns a Logos instance, or None to reset.
    """
    global _brain_logos, _brain_observer, _brain_logos_factory
    with _brain_logos_lock:
        _brain_logos_factory = factory
        _brain_logos = None  # Reset cached instance
        _brain_observer = None


def _reset_brain_logos() -> None:
    """Reset the brain logos instance (for testing)."""
    global _brain_logos, _brain_observer
    with _brain_logos_lock:
        _brain_logos = None
        _brain_observer = None


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

    @router.get("/topology", response_model=BrainTopologyResponse)
    async def get_brain_topology(
        similarity_threshold: float = 0.3,
        api_key: "ApiKeyData | None" = Depends(get_optional_api_key),
    ) -> BrainTopologyResponse:
        """
        Get 3D topology data for visualization.

        Returns nodes (crystals with positions), edges (similarities),
        gaps (sparse regions), and hub identifiers.

        The positions are computed by projecting high-dimensional embeddings
        to 3D using a simple approach (first 3 principal components or
        normalized dimensions).

        Args:
            similarity_threshold: Minimum similarity for edge creation (0.0-1.0)

        Example:
            GET /v1/brain/topology?similarity_threshold=0.3

        Returns:
            Full topology data for 3D visualization
        """
        import math
        from datetime import datetime, timezone

        try:
            logos, observer = _get_brain_logos()

            # Get internal state
            resolvers = logos._context_resolvers
            self_resolver = resolvers.get("self")
            memory_node = getattr(self_resolver, "_memory", None)
            crystal = (
                getattr(memory_node, "_memory_crystal", None) if memory_node else None
            )

            if crystal is None:
                return BrainTopologyResponse(
                    nodes=[],
                    edges=[],
                    gaps=[],
                    hub_ids=[],
                    stats={"concept_count": 0, "edge_count": 0},
                )

            patterns = getattr(crystal, "_patterns", {})
            hot_patterns = getattr(crystal, "_hot_patterns", set())

            # Build nodes with 3D positions
            nodes: list[TopologyNode] = []
            embeddings: dict[str, list[float]] = {}
            now = datetime.now(timezone.utc)

            for concept_id, pattern in patterns.items():
                embedding = getattr(pattern, "embedding", [])
                embeddings[concept_id] = embedding

                # Compute position from embedding (use first 3 dims, normalized)
                # For better visualization, we spread across a unit sphere
                if len(embedding) >= 3:
                    # Use first 3 dimensions, scale to reasonable range
                    x, y, z = embedding[0] * 10, embedding[1] * 10, embedding[2] * 10
                else:
                    # Fallback: random-ish position based on concept_id hash
                    h = hash(concept_id)
                    x = ((h >> 0) & 0xFF) / 255.0 * 20 - 10
                    y = ((h >> 8) & 0xFF) / 255.0 * 20 - 10
                    z = ((h >> 16) & 0xFF) / 255.0 * 20 - 10

                # Compute age
                stored_at = getattr(pattern, "stored_at", now)
                if stored_at.tzinfo is None:
                    stored_at = stored_at.replace(tzinfo=timezone.utc)
                age_seconds = (now - stored_at).total_seconds()

                # Get content preview
                content = getattr(pattern, "content", "")
                content_preview = str(content)[:100] if content else None

                nodes.append(
                    TopologyNode(
                        id=concept_id,
                        label=concept_id[:20],
                        x=x,
                        y=y,
                        z=z,
                        resolution=getattr(pattern, "resolution", 1.0),
                        is_hot=concept_id in hot_patterns,
                        access_count=getattr(pattern, "access_count", 0),
                        age_seconds=max(0, age_seconds),
                        content_preview=content_preview,
                    )
                )

            # Build edges based on similarity
            edges: list[TopologyEdge] = []
            concept_ids = list(embeddings.keys())
            edge_counts: dict[str, int] = {cid: 0 for cid in concept_ids}

            for i, cid1 in enumerate(concept_ids):
                emb1 = embeddings[cid1]
                for cid2 in concept_ids[i + 1 :]:
                    emb2 = embeddings[cid2]
                    sim = _cosine_similarity(emb1, emb2)
                    if sim >= similarity_threshold:
                        edges.append(
                            TopologyEdge(
                                source=cid1,
                                target=cid2,
                                similarity=sim,
                            )
                        )
                        edge_counts[cid1] += 1
                        edge_counts[cid2] += 1

            # Identify hubs (high connectivity)
            if edge_counts:
                avg_edges = sum(edge_counts.values()) / len(edge_counts)
                hub_ids = [
                    cid for cid, count in edge_counts.items() if count > avg_edges * 1.5
                ]
            else:
                hub_ids = []

            # Detect gaps (sparse regions)
            # Simple approach: find regions with low node density
            gaps: list[TopologyGap] = []
            if len(nodes) >= 5:
                # Sample points in the bounding box and check density
                xs = [n.x for n in nodes]
                ys = [n.y for n in nodes]
                zs = [n.z for n in nodes]

                # Check a few candidate gap locations
                for _ in range(3):
                    # Random point in bounding box
                    cx = (min(xs) + max(xs)) / 2 + (hash(str(_)) % 100 - 50) / 10
                    cy = (min(ys) + max(ys)) / 2 + (hash(str(_ * 2)) % 100 - 50) / 10
                    cz = (min(zs) + max(zs)) / 2 + (hash(str(_ * 3)) % 100 - 50) / 10

                    # Find nearest nodes
                    distances = []
                    for n in nodes:
                        d = math.sqrt(
                            (n.x - cx) ** 2 + (n.y - cy) ** 2 + (n.z - cz) ** 2
                        )
                        distances.append((d, n.id))
                    distances.sort()

                    # If nearest nodes are far, it's a gap
                    if distances and distances[0][0] > 3.0:
                        gaps.append(
                            TopologyGap(
                                x=cx,
                                y=cy,
                                z=cz,
                                radius=distances[0][0],
                                nearest_concepts=[d[1] for d in distances[:3]],
                            )
                        )

            return BrainTopologyResponse(
                nodes=nodes,
                edges=edges,
                gaps=gaps[:5],  # Limit to 5 gaps
                hub_ids=hub_ids,
                stats={
                    "concept_count": len(nodes),
                    "edge_count": len(edges),
                    "hub_count": len(hub_ids),
                    "gap_count": len(gaps),
                    "avg_resolution": (
                        sum(n.resolution for n in nodes) / len(nodes) if nodes else 0
                    ),
                },
            )
        except Exception as e:
            logger.exception("Brain topology failed")
            raise HTTPException(status_code=500, detail=f"Topology failed: {e}")

    return router


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    import math

    if not a or not b:
        return 0.0

    # Pad to same length
    max_len = max(len(a), len(b))
    a = list(a) + [0.0] * (max_len - len(a))
    b = list(b) + [0.0] * (max_len - len(b))

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)
