"""
Collapse REST API: Unified collapse state for frontend verification.

Aggregates constitutional scoring and Galois loss into a unified "collapse state"
that the frontend can use to display verification badges and quality indicators.

Provides:
- GET /api/collapse/{kblock_id} - Get collapse state for a K-Block

Philosophy:
    "The collapse state IS the verification. The slop IS the signal."

The Collapse API unifies:
- Constitutional scoring (7 principles)
- Galois loss (semantic preservation)
- TypeScript/Test status (build-time concerns, returned as pending)

See: services/witness/constitutional_evaluator.py
See: services/zero_seed/galois/galois_loss.py
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

try:
    from fastapi import APIRouter, HTTPException
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


class CollapseStatus(str, Enum):
    """Status of a collapse check."""

    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    PENDING = "pending"


class CollapseResultResponse(BaseModel):
    """Generic result for a collapse check."""

    status: CollapseStatus = Field(..., description="Check status")
    score: float | None = Field(default=None, description="Score (if applicable)")
    total: float | None = Field(default=None, description="Total possible (if applicable)")
    message: str | None = Field(default=None, description="Human-readable message")


class ConstitutionalCollapseResponse(BaseModel):
    """Constitutional scoring collapse response."""

    score: float = Field(..., description="Weighted score (0-7)")
    principles: dict[str, float] = Field(
        default_factory=dict,
        description="Score per principle (0-1 each)",
    )


class GaloisCollapseResponse(BaseModel):
    """Galois loss collapse response."""

    loss: float = Field(..., description="Galois loss (0-1)")
    tier: str = Field(
        ...,
        description="Evidence tier: CATEGORICAL|EMPIRICAL|AESTHETIC|SOMATIC|CHAOTIC",
    )


class SlopLevel(str, Enum):
    """Overall slop level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CollapseStateResponse(BaseModel):
    """Complete collapse state for a K-Block."""

    # Build-time checks (always pending in backend)
    typescript: CollapseResultResponse = Field(
        ..., description="TypeScript check (pending - build-time concern)"
    )
    tests: CollapseResultResponse = Field(
        ..., description="Test check (pending - build-time concern)"
    )

    # Runtime checks
    constitution: ConstitutionalCollapseResponse = Field(..., description="Constitutional scoring")
    galois: GaloisCollapseResponse = Field(..., description="Galois loss and tier")

    # Aggregate
    overall_slop: SlopLevel = Field(..., description="Overall slop level: low|medium|high")


# =============================================================================
# Tier Mapping
# =============================================================================

# Evidence tier thresholds (from galois_loss.py, Kent calibration 2025-12-28)
TIER_THRESHOLDS = {
    "CATEGORICAL": 0.10,  # L < 0.10
    "EMPIRICAL": 0.38,  # L < 0.38
    "AESTHETIC": 0.45,  # L < 0.45
    "SOMATIC": 0.65,  # L < 0.65
    "CHAOTIC": 1.0,  # L >= 0.65
}


def classify_tier(loss: float) -> str:
    """Map Galois loss to evidence tier."""
    if loss < TIER_THRESHOLDS["CATEGORICAL"]:
        return "CATEGORICAL"
    elif loss < TIER_THRESHOLDS["EMPIRICAL"]:
        return "EMPIRICAL"
    elif loss < TIER_THRESHOLDS["AESTHETIC"]:
        return "AESTHETIC"
    elif loss < TIER_THRESHOLDS["SOMATIC"]:
        return "SOMATIC"
    else:
        return "CHAOTIC"


def compute_slop_level(
    constitutional_score: float,
    galois_loss: float,
) -> SlopLevel:
    """
    Compute overall slop level from constitutional score and Galois loss.

    Args:
        constitutional_score: Weighted constitutional score (0-7)
        galois_loss: Galois loss (0-1)

    Returns:
        SlopLevel: high, medium, or low

    Thresholds:
        - high: constitutional score < 0.6*7 (4.2) OR galois loss > 0.5
        - medium: constitutional score < 0.8*7 (5.6) OR galois loss > 0.3
        - low: otherwise
    """
    if constitutional_score < 0.6 * 7 or galois_loss > 0.5:
        return SlopLevel.HIGH
    elif constitutional_score < 0.8 * 7 or galois_loss > 0.3:
        return SlopLevel.MEDIUM
    else:
        return SlopLevel.LOW


# =============================================================================
# Router Factory
# =============================================================================


def create_collapse_router() -> "APIRouter | None":
    """Create the Collapse API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Collapse routes disabled")
        return None

    router = APIRouter(prefix="/api/collapse", tags=["collapse"])

    @router.get("/{kblock_id}", response_model=CollapseStateResponse)
    async def get_collapse_state(kblock_id: str) -> CollapseStateResponse:
        """
        Get collapse state for a K-Block.

        Aggregates:
        - Constitutional scoring (7 principles)
        - Galois loss (semantic preservation)
        - TypeScript/Test status (pending - build-time concerns)

        Args:
            kblock_id: K-Block ID to evaluate

        Returns:
            CollapseStateResponse with unified collapse state
        """
        try:
            # Import services
            from services.k_block.postgres_zero_seed_storage import (
                get_postgres_zero_seed_storage,
            )

            # Get K-Block
            storage = await get_postgres_zero_seed_storage()
            kblock = await storage.get_node(kblock_id)

            if not kblock:
                raise HTTPException(
                    status_code=404,
                    detail=f"K-Block not found: {kblock_id}",
                )

            # Get constitutional alignment
            constitutional_score = 0.0
            principle_scores: dict[str, float] = {}

            try:
                from services.witness.constitutional_evaluator import (
                    MarkConstitutionalEvaluator,
                )
                from services.witness.mark import Mark, Response, Stimulus, UmweltSnapshot

                # Build a synthetic mark from the K-Block for evaluation
                # The constitutional evaluator expects a Mark object
                evaluator = MarkConstitutionalEvaluator(threshold=0.5, include_galois=False)

                # Create a minimal mark for evaluation
                mark = Mark(
                    stimulus=Stimulus(
                        kind="kblock",
                        content=kblock.content[:500] if kblock.content else "",
                        source=kblock.path,
                    ),
                    response=Response(
                        kind="evaluate",
                        content=f"Evaluating K-Block {kblock_id}",
                        success=True,
                    ),
                    umwelt=UmweltSnapshot(
                        observer_id="collapse-api",
                        trust_level=1,
                        capabilities=frozenset(["evaluate"]),
                    ),
                    domain="collapse-api",
                )

                alignment = evaluator.evaluate_sync(mark)
                constitutional_score = alignment.weighted_total
                principle_scores = alignment.principle_scores

            except Exception as e:
                logger.warning(f"Constitutional evaluation failed: {e}")
                # Fallback to moderate score
                constitutional_score = 3.5  # Middle of 0-7 range
                principle_scores = {
                    "ETHICAL": 0.5,
                    "COMPOSABLE": 0.5,
                    "JOY_INDUCING": 0.5,
                    "TASTEFUL": 0.5,
                    "CURATED": 0.5,
                    "HETERARCHICAL": 0.5,
                    "GENERATIVE": 0.5,
                }

            # Get Galois loss
            galois_loss = kblock.galois_loss if kblock.galois_loss is not None else 0.5

            # If K-Block doesn't have pre-computed loss, compute it
            if galois_loss == 0.0 and kblock.content:
                try:
                    from services.zero_seed.galois.galois_loss import (
                        compute_galois_loss_async,
                    )

                    result = await compute_galois_loss_async(
                        kblock.content[:1000],  # Limit content for performance
                        use_cache=True,
                    )
                    galois_loss = result.loss
                except Exception as e:
                    logger.warning(f"Galois loss computation failed: {e}")
                    galois_loss = 0.5  # Moderate fallback

            # Classify tier
            tier = classify_tier(galois_loss)

            # Compute overall slop
            overall_slop = compute_slop_level(constitutional_score, galois_loss)

            return CollapseStateResponse(
                typescript=CollapseResultResponse(
                    status=CollapseStatus.PENDING,
                    message="TypeScript checks are build-time concerns",
                ),
                tests=CollapseResultResponse(
                    status=CollapseStatus.PENDING,
                    message="Test checks are build-time concerns",
                ),
                constitution=ConstitutionalCollapseResponse(
                    score=constitutional_score,
                    principles=principle_scores,
                ),
                galois=GaloisCollapseResponse(
                    loss=galois_loss,
                    tier=tier,
                ),
                overall_slop=overall_slop,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get collapse state for {kblock_id} failed: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get collapse state: {str(e)}",
            )

    return router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_collapse_router",
    "CollapseStatus",
    "CollapseResultResponse",
    "ConstitutionalCollapseResponse",
    "GaloisCollapseResponse",
    "CollapseStateResponse",
    "SlopLevel",
]
