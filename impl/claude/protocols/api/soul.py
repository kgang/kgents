"""
Soul API Endpoints.

Exposes K-gent Soul capabilities via REST API:
- POST /v1/soul/governance - Semantic gatekeeper for operations
- POST /v1/soul/dialogue - Interactive dialogue with K-gent
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .models import (
    DialogueRequest,
    DialogueResponse,
    GovernanceRequest,
    GovernanceResponse,
)

if TYPE_CHECKING:
    from fastapi import APIRouter

    from .auth import ApiKeyData

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


from agents.k.persona import DialogueMode
from agents.k.soul import BudgetTier, KgentSoul

from .auth import can_use_budget_tier, get_api_key
from .metering import check_rate_limit, check_token_quota, record_request


def create_soul_router() -> "APIRouter":
    """
    Create Soul API router.

    Returns:
        FastAPI router with soul endpoints
    """
    if not HAS_FASTAPI:
        raise ImportError("FastAPI is required to create soul router")

    router = APIRouter(prefix="/v1/soul", tags=["soul"])

    # Shared soul instance (in production, this might be per-user or pooled)
    _soul = KgentSoul()

    @router.post("/governance", response_model=GovernanceResponse)
    async def evaluate_governance(
        request: GovernanceRequest,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> GovernanceResponse:
        """
        Evaluate an operation against K-gent's principles.

        Uses the Semantic Gatekeeper pattern to reason about operations
        and provide approve/reject/escalate recommendations.

        Example:
            POST /v1/soul/governance
            {
                "action": "delete user_data table",
                "context": {"environment": "production"},
                "budget": "deep"
            }

        Returns:
            Governance evaluation with reasoning and recommendation
        """
        # Check rate limit
        allowed, error_msg = check_rate_limit(api_key.user_id, api_key.rate_limit)
        if not allowed:
            raise HTTPException(status_code=429, detail=error_msg)

        # Validate budget tier
        budget_str = request.budget or "dialogue"
        if not can_use_budget_tier(api_key.tier, budget_str):
            raise HTTPException(
                status_code=403,
                detail=f"Budget tier '{budget_str}' not available for {api_key.tier} tier",
            )

        # Estimate token usage (rough)
        estimated_tokens = 500 if budget_str == "deep" else 150

        # Check token quota
        allowed, error_msg = check_token_quota(
            api_key.user_id, api_key.monthly_token_limit, estimated_tokens
        )
        if not allowed:
            raise HTTPException(status_code=429, detail=error_msg)

        # Create a mock semaphore token from the request
        class _MockToken:
            def __init__(
                self, prompt: str, reason: str, severity: float, token_id: str
            ) -> None:
                self.prompt = prompt
                self.reason = reason
                self.severity = severity
                self.id = token_id

        token = _MockToken(
            prompt=request.action,
            reason=request.context.get("reason", ""),
            severity=request.context.get("severity", 0.5),
            token_id=f"api_{api_key.user_id}_{request.action[:20]}",
        )

        # Use deep intercept for governance evaluation
        result = await _soul.intercept_deep(token)

        # Build alternatives if rejected
        alternatives = []
        if result.recommendation == "reject":
            alternatives = [
                "Consider using soft delete instead",
                "Archive the data before removing",
                "Add additional confirmation step",
            ]
        elif result.recommendation == "escalate":
            alternatives = [
                "Get explicit confirmation from stakeholders",
                "Review in team meeting",
                "Defer until more context available",
            ]

        # Return response
        return GovernanceResponse(
            approved=result.handled,
            reasoning=result.reasoning or result.annotation or "No reasoning provided",
            alternatives=alternatives,
            confidence=result.confidence,
            tokens_used=estimated_tokens,
            recommendation=result.recommendation or "escalate",
            principles=result.matching_principles,
        )

    @router.post("/dialogue", response_model=DialogueResponse)
    async def create_dialogue(
        request: DialogueRequest,
        api_key: "ApiKeyData" = Depends(get_api_key),
    ) -> DialogueResponse:
        """
        Engage in dialogue with K-gent Soul.

        K-gent responds based on personality eigenvectors and the selected mode.

        Modes:
        - reflect: Explore patterns and behaviors
        - advise: Get guidance on decisions
        - challenge: Have your thinking questioned
        - explore: Open-ended philosophical exploration

        Example:
            POST /v1/soul/dialogue
            {
                "prompt": "What patterns am I avoiding?",
                "mode": "reflect",
                "budget": "dialogue"
            }

        Returns:
            K-gent's response with metadata
        """
        # Record request FIRST (before rate limit check to count this request)
        record_request(api_key.user_id, "/v1/soul/dialogue", 0)

        # Check rate limit (now includes this request)
        allowed, error_msg = check_rate_limit(api_key.user_id, api_key.rate_limit)
        if not allowed:
            raise HTTPException(status_code=429, detail=error_msg)

        # Validate and parse mode
        mode_str = request.mode or "reflect"
        try:
            mode = DialogueMode(mode_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode '{mode_str}'. Valid modes: reflect, advise, challenge, explore",
            )

        # Validate budget format FIRST (400 error for invalid format)
        budget_str = request.budget or "dialogue"
        try:
            budget = BudgetTier(budget_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid budget '{budget_str}'. Valid budgets: dormant, whisper, dialogue, deep",
            )

        # THEN check budget tier permissions (403 for unauthorized tier)
        if not can_use_budget_tier(api_key.tier, budget_str):
            raise HTTPException(
                status_code=403,
                detail=f"Budget tier '{budget_str}' not available for {api_key.tier} tier",
            )

        # Estimate token usage for quota check
        estimated_tokens = {
            BudgetTier.DORMANT: 0,
            BudgetTier.WHISPER: 100,
            BudgetTier.DIALOGUE: 500,
            BudgetTier.DEEP: 1000,
        }.get(budget, 500)

        # Check token quota
        allowed, error_msg = check_token_quota(
            api_key.user_id, api_key.monthly_token_limit, estimated_tokens
        )
        if not allowed:
            raise HTTPException(status_code=429, detail=error_msg)

        # Engage in dialogue
        output = await _soul.dialogue(
            message=request.prompt,
            mode=mode,
            budget=budget,
        )

        # Return response
        return DialogueResponse(
            response=output.response,
            mode=output.mode.value,
            eigenvectors=_soul.eigenvectors.to_dict(),
            tokens_used=output.tokens_used,
            referenced_preferences=output.referenced_preferences or [],
            referenced_patterns=output.referenced_patterns or [],
        )

    return router


def get_soul_instance() -> Optional[KgentSoul]:
    """
    Get the shared soul instance.

    For testing and development.

    Returns:
        KgentSoul instance or None if not initialized
    """
    try:
        return KgentSoul()
    except Exception:
        return None
