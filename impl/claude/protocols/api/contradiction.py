"""
Contradiction Engine REST API: Detection, Classification, and Resolution.

Provides:
- POST /api/contradictions/detect         - Detect contradictions between K-Blocks
- GET  /api/contradictions                - List all detected contradictions
- POST /api/contradictions/{id}/resolve   - Apply resolution strategy
- GET  /api/contradictions/stats          - Summary statistics

Philosophy:
    "Surfacing, interrogating, and systematically interacting with
     personal beliefs, values, and contradictions is ONE OF THE MOST
     IMPORTANT PARTS of the system."
    - Zero Seed Grand Strategy, LAW 4

Note:
    The Contradiction Engine is Phase 4 of Zero Seed Genesis.
    Backend logic exists, this API exposes it to frontends.

See: plans/zero-seed-genesis-grand-strategy.md (Part VIII)
"""

from __future__ import annotations

import logging
from datetime import datetime, UTC
from typing import Any

try:
    from fastapi import APIRouter, HTTPException, Query
    from pydantic import BaseModel, Field

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Query = None  # type: ignore
    BaseModel = object  # type: ignore
    Field = lambda *args, **kwargs: None  # type: ignore

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models (Request/Response Schemas)
# =============================================================================


class DetectionRequest(BaseModel):
    """Request to detect contradictions between K-Blocks."""

    k_block_ids: list[str] = Field(
        ..., min_length=2, description="K-Block IDs to analyze (min 2)"
    )
    threshold: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Tau threshold for contradiction detection",
    )


class KBlockSummary(BaseModel):
    """Lightweight K-Block summary for responses."""

    id: str = Field(..., description="K-Block ID")
    content: str = Field(..., description="Content preview (truncated)")
    layer: int | None = Field(None, ge=1, le=7, description="Zero Seed layer")
    title: str | None = Field(None, description="K-Block title")


class ContradictionResponse(BaseModel):
    """Single contradiction detection result."""

    id: str = Field(..., description="Contradiction ID (sorted K-Block IDs)")
    type: str = Field(
        ..., description="Type: APPARENT, PRODUCTIVE, TENSION, FUNDAMENTAL"
    )
    severity: float = Field(..., ge=0.0, le=1.0, description="Contradiction strength")
    k_block_a: KBlockSummary = Field(..., description="First K-Block")
    k_block_b: KBlockSummary = Field(..., description="Second K-Block")
    super_additive_loss: float = Field(
        ..., description="Super-additive loss (combined - sum)"
    )
    loss_a: float = Field(..., description="Individual loss of K-Block A")
    loss_b: float = Field(..., description="Individual loss of K-Block B")
    loss_combined: float = Field(..., description="Combined loss")
    detected_at: str = Field(..., description="Detection timestamp (ISO)")
    suggested_strategy: str = Field(
        ..., description="Suggested resolution strategy"
    )
    classification: dict[str, Any] = Field(..., description="Full classification data")


class DetectionResponse(BaseModel):
    """Response from contradiction detection."""

    contradictions: list[ContradictionResponse] = Field(
        ..., description="Detected contradictions"
    )
    total: int = Field(..., ge=0, description="Total contradictions found")
    analyzed_pairs: int = Field(..., ge=0, description="Total K-Block pairs analyzed")
    threshold: float = Field(..., description="Threshold used for detection")


class ListContradictionsResponse(BaseModel):
    """Response for listing contradictions."""

    contradictions: list[ContradictionResponse] = Field(..., description="Contradictions")
    total: int = Field(..., ge=0, description="Total count")
    has_more: bool = Field(default=False, description="More results available")


class ResolutionRequest(BaseModel):
    """Request to resolve a contradiction."""

    strategy: str = Field(
        ..., description="Strategy: SYNTHESIZE, SCOPE, CHOOSE, TOLERATE, IGNORE"
    )
    context: dict[str, Any] | None = Field(
        None, description="Additional context for resolution"
    )
    new_content: str | None = Field(None, description="New content (for SYNTHESIZE)")
    scope_note: str | None = Field(None, description="Scope clarification (for SCOPE)")
    chosen_k_block_id: str | None = Field(
        None, description="Chosen K-Block ID (for CHOOSE)"
    )


class ResolutionResponse(BaseModel):
    """Response from resolution application."""

    contradiction_id: str = Field(..., description="Contradiction ID")
    strategy: str = Field(..., description="Applied strategy")
    resolved_at: str = Field(..., description="Resolution timestamp (ISO)")
    witness_mark_id: str | None = Field(None, description="Witness mark ID")
    new_k_block_id: str | None = Field(None, description="New K-Block ID (if created)")
    outcome: dict[str, Any] = Field(..., description="Full resolution outcome")


class ContradictionStats(BaseModel):
    """Statistics about contradictions."""

    total: int = Field(..., ge=0, description="Total contradictions")
    by_type: dict[str, int] = Field(..., description="Count by type")
    by_severity: dict[str, int] = Field(..., description="Count by severity range")
    resolved_count: int = Field(..., ge=0, description="Resolved contradictions")
    unresolved_count: int = Field(..., ge=0, description="Unresolved contradictions")
    average_strength: float = Field(..., description="Average contradiction strength")
    most_common_strategy: str | None = Field(
        None, description="Most common resolution strategy"
    )


class ResolutionPromptResponse(BaseModel):
    """Resolution prompt for UI."""

    contradiction_id: str = Field(..., description="Contradiction ID")
    k_block_a: KBlockSummary = Field(..., description="First K-Block")
    k_block_b: KBlockSummary = Field(..., description="Second K-Block")
    strength: float = Field(..., description="Contradiction strength")
    classification: dict[str, Any] = Field(..., description="Classification data")
    suggested_strategy: str = Field(..., description="Suggested strategy")
    reasoning: str = Field(..., description="Why this suggestion")
    available_strategies: list[dict[str, Any]] = Field(
        ..., description="All available strategies"
    )


# =============================================================================
# In-Memory Storage (Placeholder for Persistence)
# =============================================================================

# Global state for detected contradictions
# In production, this would be persisted to D-gent/Postgres
_contradictions: dict[str, ContradictionResponse] = {}
_resolutions: dict[str, ResolutionResponse] = {}


# =============================================================================
# Helper Functions
# =============================================================================


def _create_k_block_summary(k_block: Any) -> KBlockSummary:
    """Create a K-Block summary from a full K-Block object."""
    content = k_block.content if hasattr(k_block, "content") else str(k_block)
    # Truncate long content
    if len(content) > 200:
        content = content[:197] + "..."

    return KBlockSummary(
        id=k_block.id if hasattr(k_block, "id") else str(k_block),
        content=content,
        layer=getattr(k_block, "zero_seed_layer", None),
        title=getattr(k_block, "title", None),
    )


def _contradiction_to_response(
    pair: Any, classification: Any, suggested_strategy: str
) -> ContradictionResponse:
    """Convert ContradictionPair + Classification to API response."""
    return ContradictionResponse(
        id=pair.id,
        type=classification.type.value,
        severity=pair.strength,
        k_block_a=_create_k_block_summary(pair.kblock_a),
        k_block_b=_create_k_block_summary(pair.kblock_b),
        super_additive_loss=pair.strength,
        loss_a=pair.loss_a,
        loss_b=pair.loss_b,
        loss_combined=pair.loss_combined,
        detected_at=pair.detected_at.isoformat(),
        suggested_strategy=suggested_strategy,
        classification=classification.to_dict(),
    )


# =============================================================================
# Router Factory
# =============================================================================


def create_contradiction_router() -> "APIRouter | None":
    """Create the Contradiction Engine API router."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Contradiction routes disabled")
        return None

    router = APIRouter(prefix="/api/contradictions", tags=["contradictions"])

    # =========================================================================
    # POST /api/contradictions/detect - Detect contradictions
    # =========================================================================

    @router.post("/detect", response_model=DetectionResponse)
    async def detect_contradictions(request: DetectionRequest) -> DetectionResponse:
        """
        Detect contradictions between K-Blocks using super-additive loss.

        Formula: strength = loss_combined - (loss_a + loss_b)
        If strength > threshold: contradiction detected

        Args:
            request: Detection request with K-Block IDs and threshold

        Returns:
            Detection results with all contradictions found

        Raises:
            HTTPException: If K-Blocks not found or Galois loss unavailable
        """
        try:
            from services.contradiction import (
                ContradictionDetector,
                default_classifier,
                default_engine,
            )
            from services.k_block.zero_seed_storage import get_zero_seed_storage

            # Get K-Block storage
            storage = get_zero_seed_storage()

            # Load K-Blocks
            k_blocks = []
            for kb_id in request.k_block_ids:
                kblock = storage.get_node(kb_id)
                if not kblock:
                    raise HTTPException(
                        status_code=404, detail=f"K-Block not found: {kb_id}"
                    )
                k_blocks.append(kblock)

            # Get Galois loss calculator
            # TODO: Inject from providers when ready
            # For now, create a mock that returns plausible loss values
            class MockGaloisLoss:
                async def compute_loss(self, content: str) -> float:
                    # Mock: return loss based on content length (longer = higher loss)
                    # Real implementation uses LLM-based R -| C adjunction
                    base_loss = min(0.7, len(content) / 1000.0)
                    return base_loss

            galois = MockGaloisLoss()

            # Detect contradictions
            detector = ContradictionDetector(threshold=request.threshold)
            pairs = await detector.detect_matrix(k_blocks, galois)

            # Classify and format responses
            contradictions = []
            for pair in pairs:
                classification = default_classifier.classify_pair(pair)
                suggested_strategy = default_engine.suggest_strategy(
                    pair, classification
                )
                response = _contradiction_to_response(
                    pair, classification, suggested_strategy.value
                )

                # Store in global state
                _contradictions[pair.id] = response

                contradictions.append(response)

            # Calculate analyzed pairs count
            n = len(k_blocks)
            analyzed_pairs = (n * (n - 1)) // 2  # Upper triangle iteration

            return DetectionResponse(
                contradictions=contradictions,
                total=len(contradictions),
                analyzed_pairs=analyzed_pairs,
                threshold=request.threshold,
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error detecting contradictions")
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # GET /api/contradictions/stats - Summary statistics
    # =========================================================================

    @router.get("/stats", response_model=ContradictionStats)
    async def get_contradiction_stats() -> ContradictionStats:
        """
        Get summary statistics about contradictions.

        Returns:
            Statistics including counts by type, severity, resolution status
        """
        all_contradictions = list(_contradictions.values())
        total = len(all_contradictions)

        # Count by type
        by_type: dict[str, int] = {}
        for c in all_contradictions:
            by_type[c.type] = by_type.get(c.type, 0) + 1

        # Count by severity range
        by_severity = {
            "low": sum(1 for c in all_contradictions if c.severity < 0.3),
            "medium": sum(
                1 for c in all_contradictions if 0.3 <= c.severity < 0.6
            ),
            "high": sum(1 for c in all_contradictions if c.severity >= 0.6),
        }

        # Resolution counts
        resolved_count = len(_resolutions)
        unresolved_count = total - resolved_count

        # Average strength
        average_strength = (
            sum(c.severity for c in all_contradictions) / total if total > 0 else 0.0
        )

        # Most common resolution strategy
        strategy_counts: dict[str, int] = {}
        for r in _resolutions.values():
            strategy_counts[r.strategy] = strategy_counts.get(r.strategy, 0) + 1

        most_common_strategy = (
            max(strategy_counts.items(), key=lambda x: x[1])[0]
            if strategy_counts
            else None
        )

        return ContradictionStats(
            total=total,
            by_type=by_type,
            by_severity=by_severity,
            resolved_count=resolved_count,
            unresolved_count=unresolved_count,
            average_strength=average_strength,
            most_common_strategy=most_common_strategy,
        )

    # =========================================================================
    # GET /api/contradictions - List all contradictions
    # =========================================================================

    @router.get("", response_model=ListContradictionsResponse)
    async def list_contradictions(
        limit: int = Query(default=50, ge=1, le=200),
        offset: int = Query(default=0, ge=0),
        type: str | None = Query(default=None, description="Filter by type"),
        min_severity: float | None = Query(
            default=None, ge=0.0, le=1.0, description="Minimum severity"
        ),
    ) -> ListContradictionsResponse:
        """
        List all detected contradictions.

        Args:
            limit: Maximum number to return
            offset: Offset for pagination
            type: Filter by type (APPARENT, PRODUCTIVE, TENSION, FUNDAMENTAL)
            min_severity: Filter by minimum severity

        Returns:
            List of contradictions with pagination
        """
        # Filter contradictions
        filtered = list(_contradictions.values())

        if type:
            filtered = [c for c in filtered if c.type == type]

        if min_severity is not None:
            filtered = [c for c in filtered if c.severity >= min_severity]

        # Sort by severity descending (highest first)
        filtered.sort(key=lambda c: c.severity, reverse=True)

        # Pagination
        total = len(filtered)
        filtered = filtered[offset : offset + limit]
        has_more = total > offset + limit

        return ListContradictionsResponse(
            contradictions=filtered, total=total, has_more=has_more
        )

    # =========================================================================
    # GET /api/contradictions/{id} - Get single contradiction with prompt
    # =========================================================================

    @router.get("/{contradiction_id}", response_model=ResolutionPromptResponse)
    async def get_contradiction_prompt(
        contradiction_id: str,
    ) -> ResolutionPromptResponse:
        """
        Get resolution prompt for a specific contradiction.

        Includes:
        - Contradiction details
        - Classification reasoning
        - Suggested strategy
        - All available strategies with descriptions

        Args:
            contradiction_id: Contradiction ID

        Returns:
            Resolution prompt for UI

        Raises:
            HTTPException: If contradiction not found
        """
        contradiction = _contradictions.get(contradiction_id)
        if not contradiction:
            raise HTTPException(
                status_code=404, detail=f"Contradiction not found: {contradiction_id}"
            )

        try:
            from services.contradiction import ResolutionStrategy

            # Generate available strategies
            strategies = [
                {
                    "value": s.value,
                    "description": s.description,
                    "action_verb": s.action_verb,
                    "icon": s.icon,
                }
                for s in ResolutionStrategy
            ]

            # Get reasoning from classification
            reasoning = contradiction.classification.get(
                "reasoning", "Consider how these statements relate."
            )

            return ResolutionPromptResponse(
                contradiction_id=contradiction.id,
                k_block_a=contradiction.k_block_a,
                k_block_b=contradiction.k_block_b,
                strength=contradiction.severity,
                classification=contradiction.classification,
                suggested_strategy=contradiction.suggested_strategy,
                reasoning=reasoning,
                available_strategies=strategies,
            )

        except Exception as e:
            logger.exception(f"Error creating resolution prompt for {contradiction_id}")
            raise HTTPException(status_code=500, detail=str(e))

    # =========================================================================
    # POST /api/contradictions/{id}/resolve - Apply resolution strategy
    # =========================================================================

    @router.post("/{contradiction_id}/resolve", response_model=ResolutionResponse)
    async def resolve_contradiction(
        contradiction_id: str, request: ResolutionRequest
    ) -> ResolutionResponse:
        """
        Apply a resolution strategy to a contradiction.

        Strategies:
        - SYNTHESIZE: Create new K-Block that resolves both
        - SCOPE: Clarify these apply in different contexts
        - CHOOSE: Decide which K-Block to keep
        - TOLERATE: Accept as productive tension
        - IGNORE: Defer decision for later

        Every resolution is witnessed via Witness protocol.

        Args:
            contradiction_id: Contradiction ID
            request: Resolution request with strategy and context

        Returns:
            Resolution outcome with witness mark

        Raises:
            HTTPException: If contradiction not found or resolution fails
        """
        contradiction = _contradictions.get(contradiction_id)
        if not contradiction:
            raise HTTPException(
                status_code=404, detail=f"Contradiction not found: {contradiction_id}"
            )

        try:
            from services.contradiction import ResolutionStrategy
            from services.providers import get_witness_persistence

            # Validate strategy
            try:
                strategy = ResolutionStrategy[request.strategy]
            except KeyError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid strategy: {request.strategy}"
                )

            # Create witness mark for resolution
            witness = await get_witness_persistence()
            mark = await witness.save_mark(
                action=f"Resolved contradiction {contradiction_id}",
                reasoning=f"Applied {strategy.value} strategy",
                principles=["tasteful", "composable"],
                author="user",
            )

            # Build outcome based on strategy
            outcome = {
                "strategy": strategy.value,
                "resolved_at": datetime.now(UTC).isoformat(),
                "witness_mark": mark.mark_id,
                "context": request.context or {},
            }

            new_k_block_id = None

            if strategy == ResolutionStrategy.SYNTHESIZE and request.new_content:
                # Create new K-Block synthesizing both
                from services.k_block.zero_seed_storage import get_zero_seed_storage

                storage = get_zero_seed_storage()
                lineage = [contradiction.k_block_a.id, contradiction.k_block_b.id]

                kblock, node_id = storage.create_node(
                    layer=3,  # Goals layer
                    title="Synthesis",
                    content=request.new_content,
                    lineage=lineage,
                    created_by="user",
                )

                new_k_block_id = node_id
                outcome["new_kblock_id"] = node_id

            elif strategy == ResolutionStrategy.SCOPE and request.scope_note:
                outcome["scope_note"] = request.scope_note

            elif strategy == ResolutionStrategy.CHOOSE and request.chosen_k_block_id:
                outcome["chosen_kblock_id"] = request.chosen_k_block_id

            # Create resolution response
            resolved_at_str = str(outcome["resolved_at"])
            resolution = ResolutionResponse(
                contradiction_id=contradiction_id,
                strategy=strategy.value,
                resolved_at=resolved_at_str,
                witness_mark_id=mark.mark_id,
                new_k_block_id=new_k_block_id,
                outcome=outcome,
            )

            # Store resolution
            _resolutions[contradiction_id] = resolution

            return resolution

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Error resolving contradiction {contradiction_id}")
            raise HTTPException(status_code=500, detail=str(e))

    return router


__all__ = ["create_contradiction_router"]
