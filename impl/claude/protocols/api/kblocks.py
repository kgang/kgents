"""
K-Blocks REST API: Unified K-Block browsing and discovery.

Provides endpoints for:
- GET /api/kblocks/browse - Browse all K-Blocks organized as a tree
- GET /api/kblocks/layer/{layer} - Get K-Blocks by layer
- GET /api/kblocks/{kblock_id} - Get a specific K-Block

Philosophy:
    "Zero Seed nodes ARE K-Blocks. The derivation IS the lineage."
    "All UI surfaces query the same source of truth."

This API unifies:
- FileExplorer sidebar (zero-seed directory)
- BrowseModal (Ctrl+O)
- Feed page (cosmos view)
- Zero Seed foundation panel

See: services/k_block/postgres_zero_seed_storage.py
"""

from __future__ import annotations

import logging
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class KBlockSummary(BaseModel):
    """Summary of a K-Block for browsing."""

    id: str = Field(..., description="K-Block ID")
    path: str = Field(..., description="K-Block path")
    title: str = Field(..., description="Display title")
    layer: int | None = Field(None, description="Zero Seed layer (0-7)")
    kind: str | None = Field(None, description="Node kind (axiom, value, goal, etc.)")
    confidence: float = Field(default=0.5, description="Confidence score")
    galois_loss: float = Field(default=0.5, description="Galois loss (1 - confidence)")
    preview: str = Field(default="", description="Content preview (first 200 chars)")
    has_proof: bool = Field(default=False, description="Has Toulmin proof")
    tags: list[str] = Field(default_factory=list, description="Tags")
    created_at: str | None = Field(None, description="Creation timestamp")


class LayerGroup(BaseModel):
    """K-Blocks grouped by layer."""

    layer: int
    layer_name: str
    items: list[KBlockSummary]
    count: int


class BrowseResponse(BaseModel):
    """Response from browse endpoint."""

    # Zero Seed organized by layer
    zero_seed: dict[str, list[KBlockSummary]] = Field(
        default_factory=dict,
        description="K-Blocks organized by kind (axioms, values, goals, etc.)",
    )
    # Layer-based grouping
    layers: list[LayerGroup] = Field(default_factory=list, description="K-Blocks grouped by layer")
    # User-created K-Blocks (not part of Zero Seed)
    user: list[KBlockSummary] = Field(default_factory=list, description="User-created K-Blocks")
    # Totals
    total_count: int = Field(default=0, description="Total K-Block count")
    zero_seed_count: int = Field(default=0, description="Zero Seed K-Block count")
    user_count: int = Field(default=0, description="User K-Block count")


class LayerResponse(BaseModel):
    """Response for layer-specific query."""

    layer: int
    layer_name: str
    kblocks: list[KBlockSummary]
    count: int


class KBlockDetailResponse(BaseModel):
    """Detailed K-Block response."""

    id: str
    path: str
    content: str
    base_content: str
    layer: int | None
    kind: str | None
    confidence: float
    lineage: list[str]
    has_proof: bool
    toulmin_proof: dict[str, Any] | None
    tags: list[str]
    created_at: str | None
    incoming_edges: list[dict[str, Any]]
    outgoing_edges: list[dict[str, Any]]


# =============================================================================
# Layer Name Mapping
# =============================================================================

LAYER_NAMES = {
    0: "Ground",  # Zero Seed itself
    1: "Axioms",  # Foundational truths
    2: "Values",  # Core values
    3: "Goals",  # High-level goals
    4: "Specs",  # Specifications
    5: "Actions",  # Implementation
    6: "Reflections",  # Observations
    7: "Representations",  # Outputs
}

KIND_TO_CATEGORY = {
    "axiom": "axioms",
    "ground": "axioms",
    "value": "values",
    "goal": "goals",
    "spec": "specs",
    "action": "actions",
    "reflection": "reflections",
    "representation": "representations",
    "SYSTEM": "system",
}


# =============================================================================
# Router Factory
# =============================================================================


def create_kblocks_router() -> "APIRouter | None":
    """Create the K-Blocks API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, K-Blocks routes disabled")
        return None

    router = APIRouter(prefix="/api/kblocks", tags=["kblocks"])

    # =========================================================================
    # Browse All K-Blocks
    # =========================================================================

    @router.get("/browse", response_model=BrowseResponse)
    async def browse_kblocks(
        include_content: bool = Query(default=False, description="Include full content"),
    ) -> BrowseResponse:
        """
        Browse all K-Blocks organized as a tree.

        Returns K-Blocks organized by:
        - zero_seed: Grouped by kind (axioms, values, goals, etc.)
        - layers: Grouped by layer number
        - user: User-created K-Blocks

        This endpoint is used by:
        - FileExplorer sidebar (zero-seed directory)
        - BrowseModal (Ctrl+O)
        - Feed page (cosmos view)
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()

            # Collect all K-Blocks by layer
            zero_seed: dict[str, list[KBlockSummary]] = {
                "axioms": [],
                "values": [],
                "goals": [],
                "specs": [],
                "actions": [],
                "reflections": [],
                "representations": [],
                "system": [],
            }
            layers: dict[int, list[KBlockSummary]] = {}
            user_kblocks: list[KBlockSummary] = []

            # Query each layer (0-7)
            for layer_num in range(8):
                layer_nodes = await storage.get_layer_nodes(layer_num)

                for node in layer_nodes:
                    # Extract metadata
                    kblock_id = str(node.id)
                    path = getattr(node, "path", kblock_id)
                    title = getattr(node, "_title", path)
                    kind = getattr(node, "_kind", None) or node.zero_seed_kind
                    confidence = node.confidence or 0.5
                    tags = getattr(node, "_tags", [])
                    has_proof = bool(node.has_proof)
                    content = node.content or ""

                    summary = KBlockSummary(
                        id=kblock_id,
                        path=path,
                        title=title,
                        layer=layer_num,
                        kind=kind,
                        confidence=confidence,
                        galois_loss=1 - confidence,
                        preview=content[:200] if content else "",
                        has_proof=has_proof,
                        tags=tags,
                        created_at=(node.created_at.isoformat() if node.created_at else None),
                    )

                    # Add to layer grouping
                    if layer_num not in layers:
                        layers[layer_num] = []
                    layers[layer_num].append(summary)

                    # Add to zero_seed category
                    category = KIND_TO_CATEGORY.get(kind or "", "user")
                    if category in zero_seed:
                        zero_seed[category].append(summary)
                    else:
                        user_kblocks.append(summary)

            # Build layer groups
            layer_groups = [
                LayerGroup(
                    layer=layer_num,
                    layer_name=LAYER_NAMES.get(layer_num, f"Layer {layer_num}"),
                    items=items,
                    count=len(items),
                )
                for layer_num, items in sorted(layers.items())
                if items  # Only include non-empty layers
            ]

            # Calculate totals
            zero_seed_count = sum(len(items) for items in zero_seed.values())
            user_count = len(user_kblocks)
            total_count = zero_seed_count + user_count

            return BrowseResponse(
                zero_seed=zero_seed,
                layers=layer_groups,
                user=user_kblocks,
                total_count=total_count,
                zero_seed_count=zero_seed_count,
                user_count=user_count,
            )

        except Exception as e:
            logger.error(f"Browse K-Blocks failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to browse K-Blocks: {str(e)}",
            )

    # =========================================================================
    # Get K-Blocks by Layer
    # =========================================================================

    @router.get("/layer/{layer}", response_model=LayerResponse)
    async def get_layer_kblocks(layer: int) -> LayerResponse:
        """
        Get all K-Blocks in a specific layer.

        Args:
            layer: Layer number (0-7)

        Returns:
            LayerResponse with K-Blocks in that layer
        """
        if layer < 0 or layer > 7:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid layer: {layer}. Must be 0-7.",
            )

        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()
            layer_nodes = await storage.get_layer_nodes(layer)

            kblocks = []
            for node in layer_nodes:
                kblock_id = str(node.id)
                path = getattr(node, "path", kblock_id)
                title = getattr(node, "_title", path)
                kind = getattr(node, "_kind", None) or node.zero_seed_kind
                confidence = node.confidence or 0.5
                tags = getattr(node, "_tags", [])
                content = node.content or ""

                kblocks.append(
                    KBlockSummary(
                        id=kblock_id,
                        path=path,
                        title=title,
                        layer=layer,
                        kind=kind,
                        confidence=confidence,
                        galois_loss=1 - confidence,
                        preview=content[:200],
                        has_proof=bool(node.has_proof),
                        tags=tags,
                        created_at=(node.created_at.isoformat() if node.created_at else None),
                    )
                )

            return LayerResponse(
                layer=layer,
                layer_name=LAYER_NAMES.get(layer, f"Layer {layer}"),
                kblocks=kblocks,
                count=len(kblocks),
            )

        except Exception as e:
            logger.error(f"Get layer {layer} K-Blocks failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get layer K-Blocks: {str(e)}",
            )

    # =========================================================================
    # Get Specific K-Block
    # =========================================================================

    @router.get("/{kblock_id}", response_model=KBlockDetailResponse)
    async def get_kblock(kblock_id: str) -> KBlockDetailResponse:
        """
        Get a specific K-Block by ID.

        Args:
            kblock_id: K-Block ID

        Returns:
            Full K-Block details
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            storage = await get_postgres_zero_seed_storage()
            node = await storage.get_node(kblock_id)

            if not node:
                raise HTTPException(
                    status_code=404,
                    detail=f"K-Block not found: {kblock_id}",
                )

            return KBlockDetailResponse(
                id=str(node.id),
                path=node.path,
                content=node.content,
                base_content=node.base_content,
                layer=node.zero_seed_layer,
                kind=node.zero_seed_kind,
                confidence=node.confidence or 0.5,
                lineage=node.lineage or [],
                has_proof=bool(node.has_proof),
                toulmin_proof=node.toulmin_proof,
                tags=getattr(node, "_tags", []),
                created_at=(node.created_at.isoformat() if node.created_at else None),
                incoming_edges=[edge.to_dict() for edge in node.incoming_edges],
                outgoing_edges=[edge.to_dict() for edge in node.outgoing_edges],
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get K-Block {kblock_id} failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get K-Block: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_kblocks_router",
    "BrowseResponse",
    "LayerResponse",
    "KBlockDetailResponse",
    "KBlockSummary",
    "LayerGroup",
]
