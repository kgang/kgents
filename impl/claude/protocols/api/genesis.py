"""
Genesis REST API: Zero Seed Bootstrap and Clean Slate Genesis.

Provides endpoints for:
- POST /api/genesis/seed - [DEPRECATED] Create the Zero Seed and initial axioms
- POST /api/genesis/clean-slate - Seed the Constitutional Graph (22 K-Blocks)
- GET /api/genesis/clean-slate/status - Check clean slate genesis status
- GET /api/genesis/clean-slate/graph - Get the Constitutional derivation graph
- GET /api/genesis/status - Check if system has been seeded
- GET /api/genesis/zero-seed - Get the Zero Seed K-Block

Philosophy:
    "Genesis is self-description, not interrogation."
    "The system illuminates, not enforces."

The Clean Slate Genesis creates a pre-populated Constitutional Graph:
- 4 L0 axioms (Entity, Morphism, Mirror Test, Galois Ground)
- 7 L1 kernel primitives (Compose, Judge, Ground, Id, Contradict, Sublate, Fix)
- 7 L2 principles (Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative)
- 4 L3 architecture descriptions (ASHC, Metaphysical Fullstack, Hypergraph Editor, Crown Jewels)

See: spec/protocols/genesis-clean-slate.md
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
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]

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
# Clean Slate Genesis Models
# =============================================================================


class CleanSlateRequest(BaseModel):
    """Request to seed the clean slate genesis."""

    wipe_existing: bool = Field(
        default=False,
        description="Wipe existing genesis before seeding (DANGEROUS)",
    )
    force: bool = Field(
        default=False,
        description="Force re-seeding even if already seeded",
    )


class GenesisKBlockInfo(BaseModel):
    """Information about a K-Block in the Constitutional Graph."""

    id: str = Field(..., description="K-Block ID (e.g., 'genesis:L0:entity')")
    title: str = Field(..., description="K-Block title")
    layer: int = Field(..., description="Layer (0-3)")
    galois_loss: float = Field(..., description="Galois loss (lower = more fundamental)")
    derives_from: list[str] = Field(
        default_factory=list, description="IDs of K-Blocks this derives from"
    )
    tags: list[str] = Field(default_factory=list, description="K-Block tags")


class CleanSlateResponse(BaseModel):
    """Response from clean slate seeding operation."""

    success: bool = Field(..., description="Whether seeding succeeded")
    message: str = Field(..., description="Status message")
    kblocks: list[GenesisKBlockInfo] = Field(default_factory=list, description="Created K-Blocks")
    total_kblocks: int = Field(default=0, description="Total number of K-Blocks created")
    average_loss: float = Field(default=0.0, description="Average Galois loss across all K-Blocks")
    timestamp: str = Field(..., description="Genesis timestamp (ISO)")


class CleanSlateStatusResponse(BaseModel):
    """Response for clean slate genesis status check."""

    is_seeded: bool = Field(..., description="Whether clean slate genesis is complete")
    kblock_count: int = Field(..., description="Number of K-Blocks found")
    expected_count: int = Field(default=22, description="Expected number of K-Blocks (22)")
    missing_kblocks: list[str] = Field(default_factory=list, description="IDs of missing K-Blocks")
    average_loss: float | None = Field(None, description="Average Galois loss if seeded")


class DerivationEdge(BaseModel):
    """An edge in the derivation graph."""

    source: str = Field(..., description="Source K-Block ID", alias="from")
    target: str = Field(..., description="Target K-Block ID", alias="to")
    edge_type: str = Field(default="DERIVES_FROM", description="Edge type", alias="type")

    class Config:
        """Pydantic config for serialization."""

        populate_by_name = True


class DerivationGraphResponse(BaseModel):
    """Response for the Constitutional derivation graph."""

    nodes: list[GenesisKBlockInfo] = Field(
        default_factory=list, description="All K-Blocks in the graph"
    )
    edges: list[dict[str, str]] = Field(
        default_factory=list,
        description='Derivation edges [{"from": id, "to": id, "type": "DERIVES_FROM"}, ...]',
    )
    layers: dict[int, list[str]] = Field(
        default_factory=dict, description="Layer number -> K-Block IDs mapping"
    )


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

    @router.post(
        "/seed",
        response_model=SeedResponse,
        deprecated=True,
        summary="[DEPRECATED] Seed Zero Seed",
        description=(
            "DEPRECATED: Use POST /api/genesis/clean-slate instead. "
            "This endpoint seeds the old Zero Seed structure. "
            "The clean-slate endpoint creates the full Constitutional Graph with 22 K-Blocks."
        ),
    )
    async def seed_zero_seed(request: SeedRequest) -> SeedResponse:
        """
        [DEPRECATED] Seed the Zero Seed and initial axioms.

        .. deprecated::
            Use POST /api/genesis/clean-slate instead. The clean-slate endpoint
            creates the full Constitutional Graph (22 K-Blocks) instead of
            the minimal Zero Seed structure.

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
        import warnings

        warnings.warn(
            "POST /api/genesis/seed is deprecated. Use POST /api/genesis/clean-slate instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        logger.warning(
            "Deprecated endpoint called: POST /api/genesis/seed. "
            "Use POST /api/genesis/clean-slate instead."
        )
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
                return re.sub(r"[\s\-]", "", name).lower()

            # Find the law by name (case/space/hyphen-insensitive)
            law = None
            normalized_input = normalize_for_match(law_name)

            for candidate in DESIGN_LAWS:
                # Try matching by: exact name, ID, or normalized name
                if (
                    candidate.name.lower() == law_name.lower()
                    or candidate.id == law_name
                    or normalize_for_match(candidate.name) == normalized_input
                ):
                    law = candidate
                    break

            if not law:
                valid_names = ", ".join(f'"{l.name}"' for l in DESIGN_LAWS)
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
                node for node in layer_1 + layer_2 if "design-law" in getattr(node, "_tags", [])
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

    # =========================================================================
    # Clean Slate Genesis Endpoints
    # =========================================================================

    @router.post("/clean-slate", response_model=CleanSlateResponse)
    async def seed_clean_slate(request: CleanSlateRequest) -> CleanSlateResponse:
        """
        Seed the clean slate genesis.

        This creates 22 self-describing K-Blocks forming the Constitutional Graph:
        - 4 L0 axioms (Entity, Morphism, Mirror Test, Galois Ground)
        - 7 L1 kernel primitives (Compose, Judge, Ground, Id, Contradict, Sublate, Fix)
        - 7 L2 principles (Tasteful, Curated, Ethical, Joy-Inducing, Composable, Heterarchical, Generative)
        - 4 L3 architecture descriptions (ASHC, Metaphysical Fullstack, Hypergraph Editor, Crown Jewels)

        Philosophy: "Genesis is self-description, not interrogation."

        Args:
            request: CleanSlateRequest with optional wipe_existing and force flags

        Returns:
            CleanSlateResponse with created K-Block information

        Raises:
            HTTPException: If already seeded (and not force) or if seeding fails
        """
        try:
            # Import the clean slate genesis service (being created in parallel)
            try:
                from services.zero_seed.clean_slate_genesis import (
                    check_clean_slate_status,
                    seed_clean_slate as do_seed_clean_slate,
                    wipe_clean_slate,
                )
            except ImportError:
                # Service not yet implemented - provide helpful error
                raise HTTPException(
                    status_code=501,
                    detail=(
                        "Clean slate genesis service not yet implemented. "
                        "Expected at services/zero_seed/clean_slate_genesis.py"
                    ),
                )

            # Check if already seeded
            status = await check_clean_slate_status()
            if status.is_seeded and not request.force:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        "Clean slate genesis already complete. "
                        "Use force=true to re-seed (existing K-Blocks will be preserved). "
                        "Use wipe_existing=true to delete and re-seed (DANGEROUS)."
                    ),
                )

            # Wipe if requested
            if request.wipe_existing:
                logger.warning("Wiping existing clean slate genesis...")
                await wipe_clean_slate()

            # Perform seeding
            result = await do_seed_clean_slate()

            if not result.success:
                raise HTTPException(
                    status_code=500,
                    detail=result.message,
                )

            # Get the specs to build response
            from services.zero_seed.clean_slate_genesis import get_genesis_specs

            specs = get_genesis_specs()

            # Build K-Block info list from specs and result IDs
            kblocks = []
            for spec in specs:
                if spec.id in result.kblock_ids:
                    kblocks.append(
                        GenesisKBlockInfo(
                            id=spec.id,
                            title=spec.title,
                            layer=spec.layer,
                            galois_loss=spec.loss,
                            derives_from=list(spec.derivations_from),
                            tags=list(spec.tags),
                        )
                    )

            return CleanSlateResponse(
                success=True,
                message=result.message,
                kblocks=kblocks,
                total_kblocks=len(kblocks),
                average_loss=result.average_loss,
                timestamp=result.timestamp.isoformat(),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Clean slate genesis failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Clean slate genesis failed: {str(e)}",
            )

    @router.get("/clean-slate/status", response_model=CleanSlateStatusResponse)
    async def get_clean_slate_status() -> CleanSlateStatusResponse:
        """
        Check if clean slate genesis has been completed.

        Returns:
            CleanSlateStatusResponse with seeding status and K-Block counts

        The expected count is 22 K-Blocks:
        - 4 L0 axioms
        - 7 L1 kernel primitives
        - 7 L2 principles
        - 4 L3 architecture descriptions
        """
        try:
            # Import the clean slate genesis service
            try:
                from services.zero_seed.clean_slate_genesis import (
                    check_clean_slate_status,
                )
            except ImportError:
                # Service not yet implemented - return not seeded
                return CleanSlateStatusResponse(
                    is_seeded=False,
                    kblock_count=0,
                    expected_count=22,
                    missing_kblocks=[
                        "genesis:L0:entity",
                        "genesis:L0:morphism",
                        "genesis:L0:mirror",
                        "genesis:L0:galois",
                        "genesis:L1:compose",
                        "genesis:L1:judge",
                        "genesis:L1:ground",
                        "genesis:L1:id",
                        "genesis:L1:contradict",
                        "genesis:L1:sublate",
                        "genesis:L1:fix",
                        "genesis:L2:tasteful",
                        "genesis:L2:curated",
                        "genesis:L2:ethical",
                        "genesis:L2:joy",
                        "genesis:L2:composable",
                        "genesis:L2:heterarchical",
                        "genesis:L2:generative",
                        "genesis:L3:ashc",
                        "genesis:L3:metaphysical",
                        "genesis:L3:hypergraph",
                        "genesis:L3:crown-jewels",
                    ],
                    average_loss=None,
                )

            status = await check_clean_slate_status()

            return CleanSlateStatusResponse(
                is_seeded=status.is_seeded,
                kblock_count=status.kblock_count,
                expected_count=22,
                missing_kblocks=status.missing_kblocks,
                average_loss=status.average_loss if status.is_seeded else None,
            )

        except Exception as e:
            logger.error(f"Clean slate status check failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Status check failed: {str(e)}",
            )

    @router.get("/clean-slate/graph", response_model=DerivationGraphResponse)
    async def get_genesis_graph() -> DerivationGraphResponse:
        """
        Get the Constitutional derivation graph seeded by genesis.

        Returns the DAG of K-Blocks with their derivation relationships.
        This is the self-describing Constitutional Graph that teaches the
        system about itself.

        Returns:
            DerivationGraphResponse with nodes, edges, and layer mapping

        Raises:
            HTTPException: If clean slate genesis not completed
        """
        try:
            # Import the clean slate genesis service
            try:
                from services.zero_seed.clean_slate_genesis import (
                    check_clean_slate_status,
                    get_constitutional_graph,
                )
            except ImportError:
                raise HTTPException(
                    status_code=501,
                    detail=(
                        "Clean slate genesis service not yet implemented. "
                        "Expected at services/zero_seed/clean_slate_genesis.py"
                    ),
                )

            # Check if seeded
            status = await check_clean_slate_status()
            if not status.is_seeded:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Clean slate genesis not complete. "
                        "Call POST /api/genesis/clean-slate first."
                    ),
                )

            # Get the graph
            graph = await get_constitutional_graph()

            # Convert nodes to response format
            # graph.nodes is a list of dicts, graph.edges is a list of edge dicts
            nodes = [
                GenesisKBlockInfo(
                    id=node["id"],
                    title=node["title"],
                    layer=node["layer"],
                    galois_loss=node["galois_loss"],
                    derives_from=node.get("derives_from", []),
                    tags=node.get("tags", []),
                )
                for node in graph.nodes
            ]

            # graph.edges is already in the correct format
            # [{"from": id, "to": id, "type": "DERIVES_FROM"}, ...]
            edges = graph.edges

            # graph.layers is already in the correct format
            # {0: [ids], 1: [ids], 2: [ids], 3: [ids]}
            layers = graph.layers

            return DerivationGraphResponse(
                nodes=nodes,
                edges=edges,
                layers=layers,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get genesis graph: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get genesis graph: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_genesis_router",
    # Legacy request models
    "SeedRequest",
    # Legacy response models
    "SeedResponse",
    "GenesisStatusResponse",
    "ZeroSeedResponse",
    "AxiomResponse",
    "DesignLawResponse",
    # Clean slate genesis models
    "CleanSlateRequest",
    "CleanSlateResponse",
    "CleanSlateStatusResponse",
    "GenesisKBlockInfo",
    "DerivationEdge",
    "DerivationGraphResponse",
]
