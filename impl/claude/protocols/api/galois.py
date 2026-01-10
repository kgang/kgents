"""
Galois API: Loss Computation, Contradiction Detection, Fixed Point Analysis.

Provides:
- POST /api/galois/loss            - Compute Galois loss for content
- POST /api/galois/contradiction   - Detect contradiction via super-additive loss
- POST /api/galois/fixed-point     - Find fixed point through R/C iteration
- POST /api/layer/assign           - Compute layer assignment via Galois loss

Philosophy:
    "The loss IS the layer. The fixed point IS the axiom.
     The contradiction IS the super-additive signal."

The Galois loss formula:
    L(P) = d(P, C(R(P)))

Where:
- R: Prompt -> ModularPrompt (restructure via LLM)
- C: ModularPrompt -> Prompt (reconstitute via LLM)
- d: Prompt x Prompt -> [0,1] (semantic distance)

See: spec/protocols/zero-seed1/galois.md
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

try:
    from fastapi import APIRouter, HTTPException

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    APIRouter = None  # type: ignore[assignment, misc]
    HTTPException = None  # type: ignore[assignment, misc]

try:
    from pydantic import BaseModel, Field, field_validator

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[assignment, misc]
    Field = lambda *args, **kwargs: None  # type: ignore[assignment]
    field_validator = lambda *args, **kwargs: lambda f: f  # noqa: E731

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Validation Constants
# =============================================================================

# Maximum content length to prevent abuse (characters)
MAX_CONTENT_LENGTH = 100_000  # 100KB text is ~25,000 tokens

# Minimum content length for meaningful analysis
MIN_CONTENT_LENGTH = 3  # At least 3 characters


# =============================================================================
# Validation Helpers
# =============================================================================


def _validate_content(content: str, field_name: str = "content") -> str:
    """
    Validate content input for Galois operations.

    Args:
        content: The content to validate
        field_name: Name of the field for error messages

    Returns:
        Validated content (stripped of leading/trailing whitespace)

    Raises:
        ValueError: If content is invalid
    """
    if not content:
        raise ValueError(f"{field_name} cannot be empty")

    stripped = content.strip()
    if not stripped:
        raise ValueError(f"{field_name} cannot be only whitespace")

    if len(stripped) < MIN_CONTENT_LENGTH:
        raise ValueError(
            f"{field_name} must be at least {MIN_CONTENT_LENGTH} characters, got {len(stripped)}"
        )

    if len(content) > MAX_CONTENT_LENGTH:
        raise ValueError(
            f"{field_name} exceeds maximum length of {MAX_CONTENT_LENGTH:,} characters "
            f"(got {len(content):,}). Consider splitting into smaller chunks."
        )

    return stripped


def _sanitize_loss(loss: float, default: float = 0.5) -> float:
    """
    Sanitize loss value, handling NaN/Inf edge cases.

    Args:
        loss: Raw loss value from computation
        default: Default value to use for invalid losses

    Returns:
        Valid loss value in [0, 1]
    """
    import math

    if math.isnan(loss) or math.isinf(loss):
        logger.warning(f"Invalid loss value {loss}, using default {default}")
        return default

    # Clamp to valid range
    return max(0.0, min(1.0, loss))


# =============================================================================
# Pydantic Request/Response Models
# =============================================================================


class GaloisLossRequest(BaseModel):
    """Request to compute Galois loss for content."""

    content: str = Field(
        ...,
        min_length=MIN_CONTENT_LENGTH,
        max_length=MAX_CONTENT_LENGTH,
        description="Content to analyze for Galois loss",
    )
    use_cache: bool = Field(default=True, description="Use cached results if available")

    @field_validator("content")
    @classmethod
    def validate_content_not_whitespace(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be only whitespace")
        return v


class GaloisLossResponse(BaseModel):
    """Response from Galois loss computation."""

    loss: float = Field(..., ge=0.0, le=1.0, description="Galois loss value [0,1]")
    method: str = Field(..., description="Computation method: 'llm' or 'fallback'")
    metric_name: str = Field(..., description="Name of semantic distance metric used")
    cached: bool = Field(..., description="Whether result was from cache")
    evidence_tier: str = Field(
        ...,
        description="Evidence tier: categorical (<0.1), empirical (<0.3), aesthetic (<0.6), somatic (>=0.6)",
    )


class ContradictionRequest(BaseModel):
    """Request to detect contradiction between two contents."""

    content_a: str = Field(
        ...,
        min_length=MIN_CONTENT_LENGTH,
        max_length=MAX_CONTENT_LENGTH,
        description="First content",
    )
    content_b: str = Field(
        ...,
        min_length=MIN_CONTENT_LENGTH,
        max_length=MAX_CONTENT_LENGTH,
        description="Second content",
    )
    tolerance: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Tau tolerance for super-additivity detection"
    )

    @field_validator("content_a", "content_b")
    @classmethod
    def validate_contents_not_whitespace(cls, v: str) -> str:
        """Ensure contents are not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be only whitespace")
        return v


class ContradictionResponse(BaseModel):
    """Response from contradiction detection."""

    is_contradiction: bool = Field(..., description="True if L(A U B) > L(A) + L(B) + tau")
    strength: float = Field(..., description="Super-additive excess (positive = contradiction)")
    loss_a: float = Field(..., ge=0.0, le=1.0, description="Galois loss of content A")
    loss_b: float = Field(..., ge=0.0, le=1.0, description="Galois loss of content B")
    loss_combined: float = Field(..., ge=0.0, le=1.0, description="Galois loss of combined content")
    contradiction_type: str = Field(..., description="Type: none, weak, moderate, strong")
    synthesis_hint: str | None = Field(
        None, description="Ghost alternative suggestion for synthesis"
    )


class FixedPointRequest(BaseModel):
    """Request to find fixed point through R/C iteration."""

    content: str = Field(
        ...,
        min_length=MIN_CONTENT_LENGTH,
        max_length=MAX_CONTENT_LENGTH,
        description="Content to analyze for fixed point",
    )
    max_iterations: int = Field(default=7, ge=1, le=20, description="Maximum iterations to try")
    stability_threshold: float = Field(
        default=0.05, ge=0.0, le=1.0, description="Loss variance threshold for stability"
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_whitespace(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be only whitespace")
        return v


class FixedPointResponse(BaseModel):
    """Response from fixed point analysis."""

    is_fixed_point: bool = Field(..., description="Whether content converges to fixed point")
    is_axiom: bool = Field(..., description="Whether it's an axiom (fixed point with loss < 0.01)")
    final_loss: float = Field(..., ge=0.0, le=1.0, description="Final loss value")
    iterations_to_converge: int = Field(
        ..., description="Iterations needed to converge (-1 if not converged)"
    )
    loss_history: list[float] = Field(..., description="Loss at each iteration")
    stability_achieved: bool = Field(..., description="Whether loss variance is below threshold")


class LayerAssignRequest(BaseModel):
    """Request to compute layer assignment for content."""

    content: str = Field(
        ...,
        min_length=MIN_CONTENT_LENGTH,
        max_length=MAX_CONTENT_LENGTH,
        description="Content to assign layer",
    )

    @field_validator("content")
    @classmethod
    def validate_content_not_whitespace(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be only whitespace")
        return v


class LayerAssignResponse(BaseModel):
    """Response from layer assignment computation."""

    layer: int = Field(..., ge=1, le=7, description="Assigned layer (1-7)")
    layer_name: str = Field(..., description="Layer name: Axiom, Value, Goal, etc.")
    loss: float = Field(..., ge=0.0, le=1.0, description="Loss at assigned layer")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Assignment confidence")
    loss_by_layer: dict[int, float] = Field(..., description="Loss at each layer")
    insight: str = Field(..., description="Insight about the layer assignment")
    rationale: str = Field(..., description="Detailed rationale")


# =============================================================================
# Router Factory
# =============================================================================


def create_galois_router() -> tuple[APIRouter, APIRouter] | None:
    """Create the Galois API routers (galois and layer)."""
    if not HAS_FASTAPI:
        logger.warning("FastAPI not available, Galois routes disabled")
        return None

    router = APIRouter(prefix="/api/galois", tags=["galois"])
    layer_router = APIRouter(prefix="/api/layer", tags=["galois"])

    # =========================================================================
    # POST /api/galois/loss - Compute Galois Loss
    # =========================================================================

    @router.post("/loss", response_model=GaloisLossResponse)
    async def compute_galois_loss(request: GaloisLossRequest) -> GaloisLossResponse:
        """
        Compute Galois loss for content.

        The Galois loss measures how much semantic information is lost when content
        is restructured and reconstituted: L(P) = d(P, C(R(P)))

        Args:
            request: Content to analyze

        Returns:
            GaloisLossResponse with loss value and metadata
        """
        try:
            from services.zero_seed.galois.galois_loss import (
                classify_evidence_tier,
                compute_galois_loss_async,
            )

            # Compute loss using the async function from galois_loss.py
            result = await compute_galois_loss_async(
                content=request.content,
                use_cache=request.use_cache,
            )

            # Sanitize loss value (handle NaN/Inf edge cases)
            sanitized_loss = _sanitize_loss(result.loss)

            # Classify evidence tier based on sanitized loss
            tier = classify_evidence_tier(sanitized_loss)

            return GaloisLossResponse(
                loss=sanitized_loss,
                method=result.method,
                metric_name=result.metric_name,
                cached=result.cached,
                evidence_tier=tier.name.lower(),
            )

        except ImportError as e:
            logger.error(f"Galois loss service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Galois loss service not available. "
                    f"Ensure 'services.zero_seed.galois.galois_loss' is installed. "
                    f"Error: {e}"
                ),
            )
        except ValueError as e:
            # Input validation errors
            logger.warning(f"Invalid input for Galois loss: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to compute Galois loss: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to compute Galois loss. "
                    f"Content length: {len(request.content)} chars. "
                    f"Error: {e}"
                ),
            )

    # =========================================================================
    # POST /api/galois/contradiction - Detect Contradiction
    # =========================================================================

    @router.post("/contradiction", response_model=ContradictionResponse)
    async def detect_contradiction(request: ContradictionRequest) -> ContradictionResponse:
        """
        Detect contradiction between two contents using super-additive loss.

        A contradiction exists when L(A U B) > L(A) + L(B) + tau.
        This means combining the contents loses more information than
        the sum of individual losses plus tolerance.

        Args:
            request: Two contents to check for contradiction

        Returns:
            ContradictionResponse with strength and type
        """
        try:
            from services.zero_seed.galois.galois_loss import (
                CONTRADICTION_TOLERANCE,
                GaloisLossComputer,
                detect_contradiction as galois_detect_contradiction,
            )

            # Create computer and detect contradiction
            computer = GaloisLossComputer()
            analysis = await galois_detect_contradiction(
                content_a=request.content_a,
                content_b=request.content_b,
                computer=computer,
            )

            # Sanitize all loss values
            loss_a = _sanitize_loss(analysis.loss_a)
            loss_b = _sanitize_loss(analysis.loss_b)
            loss_combined = _sanitize_loss(analysis.loss_combined)

            # Recompute strength from sanitized values
            sanitized_strength = loss_combined - (loss_a + loss_b)

            # Use provided tolerance or default
            tau = request.tolerance if request.tolerance != 0.1 else CONTRADICTION_TOLERANCE
            is_contradiction = sanitized_strength > tau

            # Get synthesis hint from ghost alternatives
            synthesis_hint = None
            if analysis.synthesis_hint:
                synthesis_hint = analysis.synthesis_hint.content

            return ContradictionResponse(
                is_contradiction=is_contradiction,
                strength=sanitized_strength,
                loss_a=loss_a,
                loss_b=loss_b,
                loss_combined=loss_combined,
                contradiction_type=analysis.type.name.lower(),
                synthesis_hint=synthesis_hint,
            )

        except ImportError as e:
            logger.error(f"Contradiction detection service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Contradiction detection service not available. "
                    f"Ensure 'services.zero_seed.galois.galois_loss' is installed. "
                    f"Error: {e}"
                ),
            )
        except ValueError as e:
            logger.warning(f"Invalid input for contradiction detection: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to detect contradiction: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to detect contradiction. "
                    f"Content A: {len(request.content_a)} chars, "
                    f"Content B: {len(request.content_b)} chars. "
                    f"Error: {e}"
                ),
            )

    # =========================================================================
    # POST /api/galois/fixed-point - Find Fixed Point
    # =========================================================================

    @router.post("/fixed-point", response_model=FixedPointResponse)
    async def find_fixed_point(request: FixedPointRequest) -> FixedPointResponse:
        """
        Find fixed point through R/C iteration.

        Iteratively applies restructure-reconstitute until loss variance
        is below the stability threshold. A fixed point with loss < 0.01
        is considered axiomatic.

        This validates Amendment F: Fixed-Point Stability.

        Args:
            request: Content to analyze with iteration parameters

        Returns:
            FixedPointResponse with convergence info
        """
        try:
            from services.zero_seed.galois.galois_loss import (
                FIXED_POINT_THRESHOLD,
                GaloisLossComputer,
                find_fixed_point as galois_find_fixed_point,
            )

            # Create computer and find fixed point
            computer = GaloisLossComputer()
            result = await galois_find_fixed_point(
                content=request.content,
                computer=computer,
                max_iterations=request.max_iterations,
            )

            # Sanitize all loss values in history
            loss_history = [_sanitize_loss(loss) for loss in result.loss_history]
            final_loss = _sanitize_loss(result.loss)

            # Compute loss variance for stability check
            stability_achieved = False
            if len(loss_history) >= 2:
                # Compute variance of last few losses
                recent_losses = loss_history[-min(3, len(loss_history)) :]
                mean_loss = sum(recent_losses) / len(recent_losses)
                variance = sum((loss - mean_loss) ** 2 for loss in recent_losses) / len(
                    recent_losses
                )
                stability_achieved = variance < request.stability_threshold

            return FixedPointResponse(
                is_fixed_point=result.is_fixed_point,
                is_axiom=result.is_axiom,
                final_loss=final_loss,
                iterations_to_converge=result.iterations_to_converge,
                loss_history=loss_history,
                stability_achieved=stability_achieved,
            )

        except ImportError as e:
            logger.error(f"Fixed point service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Fixed point service not available. "
                    f"Ensure 'services.zero_seed.galois.galois_loss' is installed. "
                    f"Error: {e}"
                ),
            )
        except ValueError as e:
            logger.warning(f"Invalid input for fixed point analysis: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to find fixed point: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to find fixed point. "
                    f"Content length: {len(request.content)} chars, "
                    f"Max iterations: {request.max_iterations}. "
                    f"Error: {e}"
                ),
            )

    # =========================================================================
    # POST /api/layer/assign - Compute Layer Assignment
    # =========================================================================

    @layer_router.post("/assign", response_model=LayerAssignResponse)
    async def assign_layer(request: LayerAssignRequest) -> LayerAssignResponse:
        """
        Compute layer assignment via Galois loss minimization.

        Assigns content to the layer (1-7) where it has minimal loss.
        This DERIVES layer assignment rather than requiring manual choice.

        Layers:
        - L1: Axiom (near-zero loss, fixed point)
        - L2: Value (low loss, grounding)
        - L3: Goal (moderate loss)
        - L4: Spec (medium loss)
        - L5: Execution (higher loss)
        - L6: Reflection (high loss)
        - L7: Representation (maximum loss)

        Args:
            request: Content to assign layer

        Returns:
            LayerAssignResponse with layer and rationale
        """
        try:
            from services.zero_seed.galois.galois_loss import (
                LAYER_NAMES,
                GaloisLossComputer,
                assign_layer_via_galois,
            )

            # Create computer and assign layer
            computer = GaloisLossComputer()
            result = await assign_layer_via_galois(
                content=request.content,
                computer=computer,
            )

            # Sanitize loss values
            sanitized_loss = _sanitize_loss(result.loss)
            sanitized_confidence = _sanitize_loss(result.confidence)
            sanitized_loss_by_layer = {
                layer: _sanitize_loss(loss) for layer, loss in result.loss_by_layer.items()
            }

            return LayerAssignResponse(
                layer=result.layer,
                layer_name=LAYER_NAMES.get(result.layer, f"Layer {result.layer}"),
                loss=sanitized_loss,
                confidence=sanitized_confidence,
                loss_by_layer=sanitized_loss_by_layer,
                insight=result.insight,
                rationale=result.rationale,
            )

        except ImportError as e:
            logger.error(f"Layer assignment service not available: {e}")
            raise HTTPException(
                status_code=503,
                detail=(
                    f"Layer assignment service not available. "
                    f"Ensure 'services.zero_seed.galois.galois_loss' is installed. "
                    f"Error: {e}"
                ),
            )
        except ValueError as e:
            logger.warning(f"Invalid input for layer assignment: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid input: {e}",
            )
        except Exception as e:
            logger.error(f"Failed to assign layer: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Failed to assign layer. "
                    f"Content length: {len(request.content)} chars. "
                    f"Error: {e}"
                ),
            )

    # Return both routers - they'll be merged in the factory
    return router, layer_router


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "create_galois_router",
    # Validation constants
    "MAX_CONTENT_LENGTH",
    "MIN_CONTENT_LENGTH",
    # Request models
    "GaloisLossRequest",
    "ContradictionRequest",
    "FixedPointRequest",
    "LayerAssignRequest",
    # Response models
    "GaloisLossResponse",
    "ContradictionResponse",
    "FixedPointResponse",
    "LayerAssignResponse",
]
