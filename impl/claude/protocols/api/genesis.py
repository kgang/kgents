"""
Genesis REST API: Zero Seed Bootstrap and Initialization.

Provides endpoints for:
- POST /api/genesis/seed - Create the Zero Seed and initial axioms
- GET /api/genesis/status - Check if system has been seeded
- GET /api/genesis/zero-seed - Get the Zero Seed K-Block

Philosophy:
    "Genesis is visible — users watch it spawn."

This API implements Phase 0 of the Zero Seed Genesis Grand Strategy.

See: plans/zero-seed-genesis-grand-strategy.md
See: spec/protocols/zero-seed.md
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

try:
    from fastapi import APIRouter, HTTPException

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

logger = logging.getLogger(__name__)

# =============================================================================
# Pydantic Models (API Request/Response)
# =============================================================================


class SeedRequest(BaseModel):
    """Request to seed the Zero Seed."""

    force: bool = Field(
        default=False,
        description="Force re-seeding even if already seeded (DANGEROUS)",
    )


class AxiomResponse(BaseModel):
    """Response model for an axiom."""

    id: str = Field(..., description="Axiom ID (A1, A2, G)")
    statement: str = Field(..., description="Axiom statement")
    loss: float = Field(..., description="Galois loss (should be < 0.01)")
    tier: str = Field(..., description="Evidence tier")
    kind: str = Field(..., description="Axiom kind")
    kblock_id: str = Field(..., description="K-Block ID for this axiom")


class DesignLawResponse(BaseModel):
    """Response model for a design law."""

    id: str = Field(..., description="Design law ID")
    name: str = Field(..., description="Design law name")
    statement: str = Field(..., description="Design law statement")
    layer: int = Field(..., description="Layer (1=axiom, 2=value)")
    immutable: bool = Field(..., description="Whether immutable")
    kblock_id: str = Field(..., description="K-Block ID for this law")


class SeedResponse(BaseModel):
    """Response from seeding operation."""

    success: bool = Field(..., description="Whether seeding succeeded")
    message: str = Field(..., description="Status message")
    zero_seed_kblock_id: str = Field(..., description="Zero Seed K-Block ID")
    axioms: list[AxiomResponse] = Field(..., description="Created axioms")
    design_laws: list[DesignLawResponse] = Field(..., description="Created design laws")
    timestamp: str = Field(..., description="Genesis timestamp (ISO)")


class GenesisStatusResponse(BaseModel):
    """Response for genesis status check."""

    is_seeded: bool = Field(..., description="Whether system has been seeded")
    zero_seed_exists: bool = Field(..., description="Whether Zero Seed K-Block exists")
    axiom_count: int = Field(..., description="Number of axioms found")
    design_law_count: int = Field(..., description="Number of design laws found")
    seed_timestamp: str | None = Field(None, description="Seed timestamp if seeded")


class ZeroSeedResponse(BaseModel):
    """Response for Zero Seed K-Block."""

    id: str = Field(..., description="Zero Seed ID")
    kblock_id: str = Field(..., description="K-Block ID")
    created_at: str = Field(..., description="Creation timestamp (t=0)")
    kind: str = Field(..., description="Kind (SYSTEM)")
    layer: int = Field(..., description="Layer (0 = ground of grounds)")
    galois_loss: float = Field(..., description="Galois loss (0.000)")
    content: str = Field(..., description="Markdown content")
    axioms: list[AxiomResponse] = Field(..., description="Embedded axioms")
    design_laws: list[DesignLawResponse] = Field(..., description="Embedded design laws")


# =============================================================================
# Router Factory
# =============================================================================


def create_genesis_router() -> APIRouter | None:
    """Create the Genesis API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Genesis routes disabled")
        return None

    router = APIRouter(prefix="/api/genesis", tags=["genesis"])

    # =========================================================================
    # Seed Zero Seed
    # =========================================================================

    @router.post("/seed", response_model=SeedResponse)
    async def seed_zero_seed(request: SeedRequest) -> SeedResponse:
        """
        Seed the Zero Seed and initial axioms.

        This creates:
        - t=0: Zero Seed (L0, system, loss=0.000)
        - t=1: A1 Entity Axiom (L1, axiom, loss=0.002)
        - t=2: A2 Morphism Axiom (L1, axiom, loss=0.003)
        - t=3: G Galois Ground (L1, ground, loss=0.000)
        - Design Laws as L1-L2 nodes

        Args:
            request: Seed request with optional force flag

        Returns:
            SeedResponse with created K-Block IDs

        Raises:
            HTTPException: If already seeded (and not force) or if seeding fails
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
                reset_postgres_zero_seed_storage,
            )
            from services.zero_seed.seed import check_genesis_status, seed_zero_seed

            # Check if already seeded
            status = await check_genesis_status()
            if status.is_seeded and not request.force:
                raise HTTPException(
                    status_code=409,
                    detail="System already seeded. Use force=true to re-seed (DANGEROUS).",
                )

            # Perform seeding
            storage = await get_postgres_zero_seed_storage()
            if request.force:
                # Reset storage for re-seeding
                reset_postgres_zero_seed_storage()
                storage = await get_postgres_zero_seed_storage()
                logger.warning("Force re-seeding: Storage reset")

            result = await seed_zero_seed(storage)

            if not result.success:
                raise HTTPException(
                    status_code=500,
                    detail=result.message,
                )

            # Convert result to response
            axioms = [
                AxiomResponse(
                    id=axiom.id,
                    statement=axiom.statement,
                    loss=axiom.loss,
                    tier=axiom.tier.name,
                    kind=axiom.kind,
                    kblock_id=result.axiom_kblock_ids.get(axiom.id, ""),
                )
                for axiom in result.zero_seed.axioms
            ]

            design_laws = [
                DesignLawResponse(
                    id=law.id,
                    name=law.name,
                    statement=law.statement,
                    layer=law.layer,
                    immutable=law.immutable,
                    kblock_id=result.design_law_kblock_ids.get(law.id, ""),
                )
                for law in result.zero_seed.design_laws
            ]

            return SeedResponse(
                success=True,
                message=result.message,
                zero_seed_kblock_id=result.zero_seed_kblock_id,
                axioms=axioms,
                design_laws=design_laws,
                timestamp=result.timestamp.isoformat(),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Genesis seeding failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Genesis seeding failed: {str(e)}",
            )

    # =========================================================================
    # Genesis Status
    # =========================================================================

    @router.get("/status", response_model=GenesisStatusResponse)
    async def get_genesis_status() -> GenesisStatusResponse:
        """
        Check if the system has been seeded.

        Returns:
            GenesisStatusResponse with current status
        """
        try:
            from services.zero_seed.seed import check_genesis_status

            status = await check_genesis_status()

            return GenesisStatusResponse(
                is_seeded=status.is_seeded,
                zero_seed_exists=status.zero_seed_exists,
                axiom_count=status.axiom_count,
                design_law_count=status.design_law_count,
                seed_timestamp=(
                    status.seed_timestamp.isoformat() if status.seed_timestamp else None
                ),
            )

        except Exception as e:
            logger.error(f"Status check failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Status check failed: {str(e)}",
            )

    # =========================================================================
    # Design Laws API
    # =========================================================================

    @router.get("/design-laws")
    async def list_design_laws() -> dict[str, Any]:
        """
        List all design laws.

        Returns:
            Dict with "design_laws" key containing list of design laws

        Note:
            Design laws are embedded in the Zero Seed. This endpoint returns the
            canonical set of design laws from the seed module.
        """
        try:
            from services.zero_seed.seed import DESIGN_LAWS, check_genesis_status

            # Check if seeded (optional - design laws exist even before seeding)
            status = await check_genesis_status()

            # Return the canonical design laws
            design_laws = [
                {
                    "id": law.id,
                    "name": law.name,
                    "statement": law.statement,
                    "layer": law.layer,
                    "immutable": law.immutable,
                    "kblock_id": "",  # No K-Block ID until seeded
                }
                for law in DESIGN_LAWS
            ]

            # If seeded, try to get K-Block IDs
            if status.is_seeded:
                try:
                    from services.k_block.postgres_zero_seed_storage import (
                        get_postgres_zero_seed_storage,
                    )

                    storage = await get_postgres_zero_seed_storage()
                    layer_1 = await storage.get_layer_nodes(1)
                    layer_2 = await storage.get_layer_nodes(2)
                    law_nodes = [
                        node
                        for node in layer_1 + layer_2
                        if "design-law" in getattr(node, "_tags", [])
                    ]

                    # Match by name and update K-Block IDs
                    for response in design_laws:
                        for node in law_nodes:
                            node_title = getattr(node, "_title", "")
                            if node_title == response["name"]:
                                response["kblock_id"] = str(node.id)
                                break
                except Exception as e:
                    logger.warning(f"Failed to get K-Block IDs for laws: {e}")

            return {"design_laws": design_laws}

        except Exception as e:
            logger.error(f"Failed to list design laws: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list design laws: {str(e)}",
            )

    @router.get("/design-laws/{law_name}")
    async def get_design_law(law_name: str) -> dict[str, Any]:
        """
        Get specific design law by name.

        Args:
            law_name: Design law name (e.g., "Feed Is Primitive" or "FeedIsPrimitive")
                      Accepts both formats - with or without spaces

        Returns:
            Dict with design law properties including optional "description" field

        Raises:
            HTTPException: If law not found (404)
        """
        try:
            from services.zero_seed.seed import DESIGN_LAWS, check_genesis_status

            # Normalize names for matching - remove spaces, hyphens, convert to lowercase
            def normalize_for_match(name: str) -> str:
                """Normalize name for case/space/hyphen-insensitive matching."""
                import re
                # Remove all whitespace and hyphens, lowercase
                return re.sub(r'[\s\-]', '', name).lower()

            # Find the law by name (case/space/hyphen-insensitive)
            law = None
            normalized_input = normalize_for_match(law_name)

            for candidate in DESIGN_LAWS:
                # Try matching by: exact name, ID, or normalized name
                if (candidate.name.lower() == law_name.lower() or
                    candidate.id == law_name or
                    normalize_for_match(candidate.name) == normalized_input):
                    law = candidate
                    break

            if not law:
                valid_names = ', '.join(f'"{l.name}"' for l in DESIGN_LAWS)
                raise HTTPException(
                    status_code=404,
                    detail=f"Design law '{law_name}' not found. Valid names: {valid_names}",
                )

            # Create response dict
            response = {
                "id": law.id,
                "name": law.name,
                "statement": law.statement,
                "layer": law.layer,
                "immutable": law.immutable,
                "description": law.statement,  # Use statement as description
                "kblock_id": "",  # No K-Block ID until seeded
            }

            # If seeded, try to get K-Block ID
            status = await check_genesis_status()
            if status.is_seeded:
                try:
                    from services.k_block.postgres_zero_seed_storage import (
                        get_postgres_zero_seed_storage,
                    )

                    storage = await get_postgres_zero_seed_storage()
                    layer_nodes = await storage.get_layer_nodes(law.layer)
                    law_nodes = [
                        node
                        for node in layer_nodes
                        if "design-law" in getattr(node, "_tags", [])
                        and getattr(node, "_title", "") == law.name
                    ]

                    if law_nodes:
                        response["kblock_id"] = str(law_nodes[0].id)
                except Exception as e:
                    logger.warning(f"Failed to get K-Block ID for law {law_name}: {e}")

            return response

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get design law {law_name}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get design law: {str(e)}",
            )

    # =========================================================================
    # Get Zero Seed K-Block
    # =========================================================================

    @router.get("/zero-seed", response_model=ZeroSeedResponse)
    async def get_zero_seed() -> ZeroSeedResponse:
        """
        Get the Zero Seed K-Block.

        Returns:
            ZeroSeedResponse with Zero Seed data

        Raises:
            HTTPException: If Zero Seed not found (system not seeded)
        """
        try:
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )
            from services.zero_seed.seed import ZERO_SEED_ID, check_genesis_status

            # Check if seeded
            status = await check_genesis_status()
            if not status.is_seeded:
                raise HTTPException(
                    status_code=404,
                    detail="System not seeded. Call POST /api/genesis/seed first.",
                )

            # Get Zero Seed K-Block
            storage = await get_postgres_zero_seed_storage()
            kblock = await storage.get_node(ZERO_SEED_ID)

            if not kblock:
                raise HTTPException(
                    status_code=404,
                    detail="Zero Seed K-Block not found.",
                )

            # Get axioms and design laws
            # In production, this would query based on lineage
            # For now, get all L1 nodes as axioms
            axiom_nodes = await storage.get_layer_nodes(1)
            axioms = [
                AxiomResponse(
                    id=getattr(node, "_kind", "unknown"),
                    statement=getattr(node, "_title", ""),
                    loss=0.0,  # Would extract from content in production
                    tier="CATEGORICAL",
                    kind=getattr(node, "_kind", "unknown"),
                    kblock_id=str(node.id),
                )
                for node in axiom_nodes
                if "axiom" in getattr(node, "_tags", [])
            ]

            # Get design laws (would query by tag in production)
            layer_1 = await storage.get_layer_nodes(1)
            layer_2 = await storage.get_layer_nodes(2)
            law_nodes = [
                node
                for node in layer_1 + layer_2
                if "design-law" in getattr(node, "_tags", [])
            ]
            design_laws = [
                DesignLawResponse(
                    id=str(node.id),
                    name=getattr(node, "_title", ""),
                    statement="",  # Would extract from content
                    layer=getattr(node, "_layer", 1),
                    immutable=True,
                    kblock_id=str(node.id),
                )
                for node in law_nodes
            ]

            return ZeroSeedResponse(
                id=ZERO_SEED_ID,
                kblock_id=str(kblock.id),
                created_at=kblock.created_at.isoformat(),
                kind="SYSTEM",
                layer=0,
                galois_loss=0.000,
                content=kblock.content,
                axioms=axioms,
                design_laws=design_laws,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get Zero Seed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get Zero Seed: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_genesis_router",
    # Request models
    "SeedRequest",
    # Response models
    "SeedResponse",
    "GenesisStatusResponse",
    "ZeroSeedResponse",
    "AxiomResponse",
    "DesignLawResponse",
]
