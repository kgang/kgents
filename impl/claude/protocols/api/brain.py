"""
Brain API Endpoints.

Exposes Holographic Brain (Crown Jewel) capabilities via REST API:
- POST /v1/brain/capture - Capture content to holographic memory
- POST /v1/brain/ghost - Surface ghost memories based on context
- GET /v1/brain/map - Get memory cartography/topology
- GET /v1/brain/status - Brain health status

Session 6: Production Brain API for Web UI integration.
Session 9: D-gent persistence - Brain data survives server restarts.
Session 10: StorageRouter - Auto-selects Postgres or SQLite for persistence.

D-gent Integration:
    Brain data is persisted using StorageRouter which auto-selects:
    - PostgreSQL if KGENTS_POSTGRES_URL is set
    - SQLite (~/.local/share/kgents/brain/brain.db) otherwise
"""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import datetime, timezone
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

# Global BrainCrystal instance with thread-safe initialization
_brain_crystal: Any = None
_brain_crystal_lock = threading.Lock()

# Test hook: override to inject a mock brain instance
_brain_crystal_factory: Any = None


async def _get_brain_crystal() -> Any:
    """Get or create the shared BrainCrystal instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization. This is important for API servers that may
    handle concurrent requests.

    D-gent Persistence:
        BrainCrystal uses StorageRouter which auto-selects:
        - PostgreSQL if KGENTS_POSTGRES_URL is set
        - SQLite (~/.local/share/kgents/brain/brain.db) otherwise

    Tests can inject a factory via _set_brain_crystal_factory() to avoid
    network calls and global state mutation.

    Returns:
        BrainCrystal instance
    """
    global _brain_crystal, _brain_crystal_factory

    if _brain_crystal is None:
        with _brain_crystal_lock:
            # Double-check after acquiring lock
            if _brain_crystal is None:
                if _brain_crystal_factory is not None:
                    # Test injection: use factory
                    result = _brain_crystal_factory()
                    if asyncio.iscoroutine(result):
                        _brain_crystal = await result
                    else:
                        _brain_crystal = result
                else:
                    # Production: use BrainCrystal with StorageRouter
                    from agents.brain import get_brain_crystal

                    _brain_crystal = await get_brain_crystal()
                    logger.info(
                        f"Brain initialized with backend: {_brain_crystal._storage_backend}"
                    )

    return _brain_crystal


def _set_brain_crystal_factory(factory: Any) -> None:
    """Set a factory function for brain crystal (test hook).

    Call with None to reset to default behavior.

    Args:
        factory: Callable that returns a BrainCrystal instance, or None to reset.
    """
    global _brain_crystal, _brain_crystal_factory
    with _brain_crystal_lock:
        _brain_crystal_factory = factory
        _brain_crystal = None  # Reset cached instance


def _reset_brain_crystal() -> None:
    """Reset the brain crystal instance (for testing)."""
    global _brain_crystal
    with _brain_crystal_lock:
        _brain_crystal = None
        # Also reset the singleton in agents.brain
        from agents.brain import reset_brain_crystal

        reset_brain_crystal()


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
        to store content in the Brain's BrainCrystal.

        D-gent persistence is automatic via StorageRouter:
        - PostgreSQL if KGENTS_POSTGRES_URL is set
        - SQLite otherwise

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
            brain = await _get_brain_crystal()

            result = await brain.capture(
                content=request.content,
                concept_id=request.concept_id,
                metadata=request.metadata,
            )

            return BrainCaptureResponse(
                status="captured",
                concept_id=result.concept_id,
                storage=result.storage,
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
            brain = await _get_brain_crystal()

            results = await brain.search(
                query=request.context,
                limit=request.limit,
            )

            surfaced_memories = []
            for result in results:
                surfaced_memories.append(
                    GhostMemory(
                        concept_id=result.concept_id,
                        content=result.content,
                        relevance=result.similarity,
                    )
                )

            return BrainGhostResponse(
                status="surfaced",
                context=request.context,
                surfaced=surfaced_memories,
                count=len(surfaced_memories),
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
            brain = await _get_brain_crystal()
            status = await brain.status()

            return BrainMapResponse(
                summary=f"Brain using {status.storage_backend} backend",
                concept_count=status.total_captures,
                landmarks=0,  # TODO: implement landmark detection
                hot_patterns=0,  # TODO: implement hot pattern tracking
                dimension=128,  # Default dimension for embeddings
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
        embedder type, dimensions, concept count, and storage backend.

        Example:
            GET /v1/brain/status

        Returns:
            Brain health status
        """
        try:
            brain = await _get_brain_crystal()
            status = await brain.status()

            # Determine embedder type
            embedder = brain._embedder
            embedder_type = type(embedder).__name__ if embedder else "hash-based"
            embedder_dimension = (
                getattr(embedder, "dimension", 128) if embedder else 128
            )

            return BrainStatusResponse(
                status="healthy" if status.total_captures >= 0 else "degraded",
                embedder_type=embedder_type,
                embedder_dimension=embedder_dimension,
                concept_count=status.total_captures,
                has_cartographer=False,  # Cartographer removed in rewrite
                storage_backend=status.storage_backend,
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

        try:
            brain = await _get_brain_crystal()
            topology_data = await brain.get_topology_data(limit=500)

            if not topology_data:
                return BrainTopologyResponse(
                    nodes=[],
                    edges=[],
                    gaps=[],
                    hub_ids=[],
                    stats={"concept_count": 0, "edge_count": 0},
                )

            now = datetime.now(timezone.utc)

            # Build nodes with 3D positions
            nodes: list[TopologyNode] = []
            embeddings: dict[str, list[float]] = {}

            for item in topology_data:
                concept_id = item["concept_id"]
                embedding = item.get("embedding") or []
                embeddings[concept_id] = embedding

                # Compute position from embedding (use first 3 dims, normalized)
                use_hash_position = True  # Default to hash-based

                if len(embedding) >= 3:
                    # Check if first 3 dims have meaningful values (not all zeros)
                    first_3_magnitude = (
                        abs(embedding[0]) + abs(embedding[1]) + abs(embedding[2])
                    )
                    if first_3_magnitude > 0.001:
                        # Use first 3 dimensions, scale to reasonable range
                        x, y, z = (
                            embedding[0] * 10,
                            embedding[1] * 10,
                            embedding[2] * 10,
                        )
                        use_hash_position = False

                if use_hash_position:
                    # Fallback: deterministic position based on concept_id hash
                    h = hash(concept_id)
                    x = ((h >> 0) & 0xFF) / 255.0 * 20 - 10
                    y = ((h >> 8) & 0xFF) / 255.0 * 20 - 10
                    z = ((h >> 16) & 0xFF) / 255.0 * 20 - 10

                # Compute age from captured_at
                captured_at_str = item.get("captured_at", "")
                try:
                    captured_at = datetime.fromisoformat(
                        captured_at_str.replace("Z", "+00:00")
                    )
                    if captured_at.tzinfo is None:
                        captured_at = captured_at.replace(tzinfo=timezone.utc)
                    age_seconds = max(0, (now - captured_at).total_seconds())
                except (ValueError, AttributeError):
                    age_seconds = 0

                nodes.append(
                    TopologyNode(
                        id=concept_id,
                        label=concept_id[:20],
                        x=x,
                        y=y,
                        z=z,
                        resolution=1.0,
                        is_hot=False,
                        access_count=0,
                        age_seconds=age_seconds,
                        content_preview=item.get("content_preview"),
                    )
                )

            # Build edges based on similarity
            edges: list[TopologyEdge] = []
            concept_ids = list(embeddings.keys())
            edge_counts: dict[str, int] = {cid: 0 for cid in concept_ids}

            for i, cid1 in enumerate(concept_ids):
                emb1 = embeddings[cid1]
                if not emb1:
                    continue
                for cid2 in concept_ids[i + 1 :]:
                    emb2 = embeddings[cid2]
                    if not emb2:
                        continue
                    sim = _cosine_similarity(emb1, emb2)
                    # Clamp to [0, 1] to handle floating point precision
                    sim = max(0.0, min(1.0, sim))
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
            hub_ids = []
            if edge_counts:
                non_zero_counts = [c for c in edge_counts.values() if c > 0]
                if non_zero_counts:
                    avg_edges = sum(non_zero_counts) / len(non_zero_counts)
                    hub_ids = [
                        cid
                        for cid, count in edge_counts.items()
                        if count > avg_edges * 1.5
                    ]

            # Detect gaps (sparse regions)
            gaps: list[TopologyGap] = []
            if len(nodes) >= 5:
                xs = [n.x for n in nodes]
                ys = [n.y for n in nodes]
                zs = [n.z for n in nodes]

                for i in range(3):
                    cx = (min(xs) + max(xs)) / 2 + (hash(str(i)) % 100 - 50) / 10
                    cy = (min(ys) + max(ys)) / 2 + (hash(str(i * 2)) % 100 - 50) / 10
                    cz = (min(zs) + max(zs)) / 2 + (hash(str(i * 3)) % 100 - 50) / 10

                    distances = []
                    for n in nodes:
                        d = math.sqrt(
                            (n.x - cx) ** 2 + (n.y - cy) ** 2 + (n.z - cz) ** 2
                        )
                        distances.append((d, n.id))
                    distances.sort()

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
                gaps=gaps[:5],
                hub_ids=hub_ids,
                stats={
                    "concept_count": len(nodes),
                    "edge_count": len(edges),
                    "hub_count": len(hub_ids),
                    "gap_count": len(gaps),
                    "avg_resolution": 1.0,
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
