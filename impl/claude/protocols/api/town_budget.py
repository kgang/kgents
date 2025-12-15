"""
Per-tenant token budget management for Agent Town API.

Integrates with BudgetStore (Redis/in-memory) to enforce credit-based limits.
Credits are consumed by LOD actions per the unified-v2.md pricing.

Graceful degradation: When budget exhausted, falls back to template dialogue.

See: plans/agent-town/unified-v2.md §1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .auth import ApiKeyData

logger = logging.getLogger(__name__)


# =============================================================================
# Budget Enforcer
# =============================================================================


@dataclass
class BudgetCheckResult:
    """Result of a budget check."""

    allowed: bool
    credits_requested: int
    credits_remaining: int
    fallback_to_template: bool = False
    reason: str = ""


class TownBudgetEnforcer:
    """
    Enforces per-tenant credit budgets for Agent Town.

    Integrates with BudgetStore and provides:
    - Pre-execution budget checks
    - Post-execution credit recording
    - Graceful degradation to templates
    """

    def __init__(self, use_redis: bool = True) -> None:
        """
        Initialize budget enforcer.

        Args:
            use_redis: Use Redis if available (default True)
        """
        from agents.town.budget_store import create_budget_store

        self._store = create_budget_store(use_redis=use_redis)

    async def check_budget(
        self,
        tenant_id: str,
        tier: str,
        estimated_credits: int,
    ) -> BudgetCheckResult:
        """
        Check if tenant has budget for an operation.

        Args:
            tenant_id: Tenant identifier
            tier: Tenant tier (TOURIST, RESIDENT, CITIZEN, FOUNDER)
            estimated_credits: Estimated credit cost

        Returns:
            BudgetCheckResult with allowed status and fallback info
        """
        budget = await self._store.get_or_create(tenant_id, tier)

        # Check if operation is affordable
        if budget.credits >= estimated_credits:
            return BudgetCheckResult(
                allowed=True,
                credits_requested=estimated_credits,
                credits_remaining=budget.credits,
            )

        # Budget exceeded - check if tier has included allowance
        if tier == "FOUNDER":
            # Founder tier has generous allowances
            return BudgetCheckResult(
                allowed=True,
                credits_requested=estimated_credits,
                credits_remaining=budget.credits,
            )

        # Insufficient credits: fall back to template (0 credits)
        return BudgetCheckResult(
            allowed=True,
            credits_requested=0,  # Template uses 0 credits
            credits_remaining=budget.credits,
            fallback_to_template=True,
            reason="Budget exceeded, using template dialogue",
        )

    async def record_usage(
        self,
        tenant_id: str,
        credits_used: int,
    ) -> bool:
        """
        Record credit usage after operation.

        Args:
            tenant_id: Tenant identifier
            credits_used: Actual credits consumed

        Returns:
            True if recorded successfully
        """
        if credits_used <= 0:
            return True  # Nothing to record

        return await self._store.spend_credits(tenant_id, credits_used)

    async def get_budget_status(
        self,
        tenant_id: str,
        tier: str,
    ) -> dict[str, Any]:
        """
        Get current budget status for a tenant.

        Args:
            tenant_id: Tenant identifier
            tier: Tenant tier

        Returns:
            Budget status dictionary
        """
        budget = await self._store.get_or_create(tenant_id, tier)

        return {
            "tenant_id": tenant_id,
            "tier": budget.subscription_tier,
            "credits": {
                "available": budget.credits,
            },
            "monthly_usage": budget.monthly_usage,
        }


# =============================================================================
# FastAPI Integration
# =============================================================================


def get_tenant_from_api_key(api_key: "ApiKeyData") -> tuple[str, str]:
    """
    Extract tenant_id and tier from API key.

    Args:
        api_key: Validated API key data

    Returns:
        Tuple of (tenant_id, tier)
    """
    tenant_id = str(api_key.tenant_id) if api_key.tenant_id else "anonymous"

    # Map API key tier to budget tier
    tier_map = {
        "free": "TOURIST",
        "pro": "RESIDENT",
        "enterprise": "FOUNDER",
    }
    tier = tier_map.get(api_key.tier.lower(), "TOURIST")

    return tenant_id, tier


# Global enforcer instance (lazy initialization)
_enforcer: TownBudgetEnforcer | None = None


def get_budget_enforcer() -> TownBudgetEnforcer:
    """Get or create the global budget enforcer."""
    global _enforcer
    if _enforcer is None:
        _enforcer = TownBudgetEnforcer()
    return _enforcer


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "BudgetCheckResult",
    "TownBudgetEnforcer",
    "get_budget_enforcer",
    "get_tenant_from_api_key",
]
