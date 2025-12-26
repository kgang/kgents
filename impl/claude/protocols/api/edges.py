"""
Edges REST API: Browse and view K-Block edges as first-class entities.

Provides endpoints for:
- GET /api/edges/browse - Browse all edges organized by kind
- GET /api/edges/kind/{kind} - Get edges by kind
- GET /api/edges/{edge_id} - Get a specific edge with full details

Philosophy:
    "The edge IS the proof. The mark IS the witness."
    "Edges are first-class citizens, not hidden metadata."

Edge kinds:
- derives_from: Zero Seed derivation (child -> parent axiom)
- implements: Implementation of a specification
- tests: Test coverage relationship
- references: Cross-references between documents
- contradicts: Logical contradiction (for Zero Seed conflict detection)

See: services/k_block/core/edge.py, spec/protocols/zero-seed.md
"""

from __future__ import annotations

import logging
from typing import Any

# Graceful imports with fallback for environments without FastAPI
try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[misc, assignment]
    HTTPException = None  # type: ignore[misc, assignment]
    # Create stub BaseModel for type hints when pydantic not available
    class BaseModel:  # type: ignore[no-redef]
        pass
    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class EdgeSummary(BaseModel):
    """Summary of an edge for browsing."""

    id: str = Field(..., description="Edge ID")
    source_id: str = Field(..., description="Source K-Block ID")
    target_id: str = Field(..., description="Target K-Block ID")
    source_title: str = Field(..., description="Source K-Block title")
    target_title: str = Field(..., description="Target K-Block title")
    source_path: str = Field(..., description="Source K-Block path")
    target_path: str = Field(..., description="Target K-Block path")
    edge_type: str = Field(..., description="Edge type (derives_from, implements, etc.)")
    context: str | None = Field(None, description="Edge context/justification")
    confidence: float = Field(default=1.0, description="Confidence score [0.0, 1.0]")
    mark_id: str | None = Field(None, description="Witness mark ID if tracked")
    created_at: str | None = Field(None, description="Creation timestamp")


class EdgeKindGroup(BaseModel):
    """Edges grouped by kind."""

    kind: str = Field(..., description="Edge kind")
    display_name: str = Field(..., description="Human-readable kind name")
    edges: list[EdgeSummary] = Field(default_factory=list, description="Edges of this kind")
    count: int = Field(default=0, description="Number of edges in this group")


class EdgeBrowseResponse(BaseModel):
    """Response from browse endpoint."""

    by_kind: dict[str, list[EdgeSummary]] = Field(
        default_factory=dict,
        description="Edges organized by kind",
    )
    kind_groups: list[EdgeKindGroup] = Field(
        default_factory=list,
        description="Edges grouped by kind with metadata",
    )
    total_count: int = Field(default=0, description="Total edge count")
    kind_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Count of edges per kind",
    )


class EdgeKindResponse(BaseModel):
    """Response for kind-specific query."""

    kind: str = Field(..., description="Edge kind")
    display_name: str = Field(..., description="Human-readable kind name")
    edges: list[EdgeSummary] = Field(default_factory=list, description="Edges of this kind")
    count: int = Field(default=0, description="Number of edges")


class EdgeDetailResponse(BaseModel):
    """Detailed edge response."""

    id: str
    source_id: str
    target_id: str
    source_title: str
    target_title: str
    source_path: str
    target_path: str
    source_layer: int | None
    target_layer: int | None
    source_kind: str | None
    target_kind: str | None
    edge_type: str
    context: str | None
    confidence: float
    mark_id: str | None
    created_at: str | None
    # Source and target content previews
    source_preview: str | None
    target_preview: str | None


# =============================================================================
# Kind Display Names
# =============================================================================

KIND_DISPLAY_NAMES = {
    "derives_from": "Derives From",
    "implements": "Implements",
    "tests": "Tests",
    "references": "References",
    "contradicts": "Contradicts",
}


# =============================================================================
# Router Factory
# =============================================================================


def create_edges_router() -> "APIRouter | None":
    """Create the Edges API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Edges routes disabled")
        return None

    router = APIRouter(prefix="/api/edges", tags=["edges"])

    # =========================================================================
    # Browse All Edges
    # =========================================================================

    @router.get("/browse", response_model=EdgeBrowseResponse)
    async def browse_edges() -> EdgeBrowseResponse:
        """
        Browse all edges organized by kind.

        Returns edges organized by:
        - by_kind: Grouped by edge type (derives_from, implements, etc.)
        - kind_groups: Same data with metadata
        - kind_counts: Count per kind

        This endpoint is used by:
        - FileExplorer sidebar (edges/ directory)
        - BrowseModal edge view
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()

            # Collect all edges from all K-Blocks
            by_kind: dict[str, list[EdgeSummary]] = {
                "derives_from": [],
                "implements": [],
                "tests": [],
                "references": [],
                "contradicts": [],
            }

            # Get all K-Blocks and extract edges
            seen_edge_ids: set[str] = set()

            for layer_num in range(8):
                layer_nodes = await storage.get_layer_nodes(layer_num)

                for node in layer_nodes:
                    source_id = str(node.id)
                    source_path = node.path
                    source_title = getattr(node, "_title", source_path)

                    # Process outgoing edges
                    for edge in node.outgoing_edges:
                        if edge.id in seen_edge_ids:
                            continue
                        seen_edge_ids.add(edge.id)

                        # Get target info
                        target_node = await storage.get_node(edge.target_id)
                        target_title = (
                            getattr(target_node, "_title", edge.target_id)
                            if target_node
                            else edge.target_id
                        )
                        target_path = (
                            target_node.path if target_node else edge.target_id
                        )

                        summary = EdgeSummary(
                            id=edge.id,
                            source_id=source_id,
                            target_id=edge.target_id,
                            source_title=source_title,
                            target_title=target_title,
                            source_path=source_path,
                            target_path=target_path,
                            edge_type=edge.edge_type,
                            context=edge.context,
                            confidence=edge.confidence,
                            mark_id=edge.mark_id,
                            created_at=(
                                edge.created_at.isoformat()
                                if hasattr(edge, "created_at") and edge.created_at
                                else None
                            ),
                        )

                        if edge.edge_type in by_kind:
                            by_kind[edge.edge_type].append(summary)
                        else:
                            # Unknown edge type, add to a generic bucket
                            if "other" not in by_kind:
                                by_kind["other"] = []
                            by_kind["other"].append(summary)

            # Build kind groups
            kind_groups = [
                EdgeKindGroup(
                    kind=kind,
                    display_name=KIND_DISPLAY_NAMES.get(kind, kind.replace("_", " ").title()),
                    edges=edges,
                    count=len(edges),
                )
                for kind, edges in by_kind.items()
                if edges  # Only include non-empty kinds
            ]

            # Calculate totals
            kind_counts = {kind: len(edges) for kind, edges in by_kind.items()}
            total_count = sum(kind_counts.values())

            return EdgeBrowseResponse(
                by_kind=by_kind,
                kind_groups=kind_groups,
                total_count=total_count,
                kind_counts=kind_counts,
            )

        except Exception as e:
            logger.error(f"Browse edges failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to browse edges: {str(e)}",
            )

    # =========================================================================
    # Get Edges by Kind
    # =========================================================================

    @router.get("/kind/{kind}", response_model=EdgeKindResponse)
    async def get_edges_by_kind(kind: str) -> EdgeKindResponse:
        """
        Get all edges of a specific kind.

        Args:
            kind: Edge kind (derives_from, implements, tests, references, contradicts)

        Returns:
            EdgeKindResponse with edges of that kind
        """
        valid_kinds = {"derives_from", "implements", "tests", "references", "contradicts"}
        if kind not in valid_kinds:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid kind: {kind}. Must be one of: {valid_kinds}",
            )

        try:
            # Use browse and filter
            browse_response = await browse_edges()
            edges = browse_response.by_kind.get(kind, [])

            return EdgeKindResponse(
                kind=kind,
                display_name=KIND_DISPLAY_NAMES.get(kind, kind.replace("_", " ").title()),
                edges=edges,
                count=len(edges),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get edges by kind {kind} failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get edges by kind: {str(e)}",
            )

    # =========================================================================
    # Get Specific Edge
    # =========================================================================

    @router.get("/{edge_id}", response_model=EdgeDetailResponse)
    async def get_edge(edge_id: str) -> EdgeDetailResponse:
        """
        Get a specific edge by ID.

        Args:
            edge_id: Edge ID

        Returns:
            Full edge details including source/target K-Block info
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()

            # Search all K-Blocks for this edge
            found_edge = None
            source_node = None

            for layer_num in range(8):
                if found_edge:
                    break

                layer_nodes = await storage.get_layer_nodes(layer_num)

                for node in layer_nodes:
                    for edge in node.outgoing_edges:
                        if edge.id == edge_id:
                            found_edge = edge
                            source_node = node
                            break
                    if found_edge:
                        break

            if not found_edge or not source_node:
                raise HTTPException(
                    status_code=404,
                    detail=f"Edge not found: {edge_id}",
                )

            # Get target node
            target_node = await storage.get_node(found_edge.target_id)

            return EdgeDetailResponse(
                id=found_edge.id,
                source_id=str(source_node.id),
                target_id=found_edge.target_id,
                source_title=getattr(source_node, "_title", source_node.path),
                target_title=(
                    getattr(target_node, "_title", found_edge.target_id)
                    if target_node
                    else found_edge.target_id
                ),
                source_path=source_node.path,
                target_path=target_node.path if target_node else found_edge.target_id,
                source_layer=source_node.zero_seed_layer,
                target_layer=target_node.zero_seed_layer if target_node else None,
                source_kind=source_node.zero_seed_kind,
                target_kind=target_node.zero_seed_kind if target_node else None,
                edge_type=found_edge.edge_type,
                context=found_edge.context,
                confidence=found_edge.confidence,
                mark_id=found_edge.mark_id,
                created_at=(
                    found_edge.created_at.isoformat()
                    if hasattr(found_edge, "created_at") and found_edge.created_at
                    else None
                ),
                source_preview=source_node.content[:200] if source_node.content else None,
                target_preview=(
                    target_node.content[:200]
                    if target_node and target_node.content
                    else None
                ),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get edge {edge_id} failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get edge: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_edges_router",
    "EdgeBrowseResponse",
    "EdgeKindResponse",
    "EdgeDetailResponse",
    "EdgeSummary",
    "EdgeKindGroup",
]
