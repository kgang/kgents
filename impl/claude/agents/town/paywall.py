"""
Paywall logic for Agent Town monetization.

Implements the pure function check_paywall() per spec/town/monetization.md §9.

This module determines whether a user can perform an action based on:
- Subscription tier and included allowances
- Credit balance
- Feature access (INHABIT, branching)
- Consent debt state

Per unified-v2.md §1: Margin-safe pricing with kill-switch enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .budget_store import SUBSCRIPTION_TIERS, ConsentState, UserBudgetInfo

# =============================================================================
# Action Catalog (per unified-v2.md §1 and spec/town/monetization.md §3)
# =============================================================================


class ActionType(str, Enum):
    """Billable action types."""

    # LOD actions
    LOD_0 = "lod0"
    LOD_1 = "lod1"
    LOD_2 = "lod2"
    LOD_3 = "lod3"
    LOD_4 = "lod4"
    LOD_5 = "lod5"

    # INHABIT actions
    INHABIT_SESSION = "inhabit_session"
    INHABIT_FORCE = "inhabit_force"
    INHABIT_APOLOGIZE = "inhabit_apologize"

    # Branch actions
    BRANCH_CREATE = "branch_create"
    BRANCH_SWITCH = "branch_switch"
    BRANCH_MERGE = "branch_merge"


# Credit costs per action (revised per unified-v2.md §1)
ACTION_COSTS = {
    # LOD costs (margin-safe pricing)
    ActionType.LOD_0: 0,  # Free
    ActionType.LOD_1: 0,  # Free
    ActionType.LOD_2: 0,  # Free (for paid tiers)
    ActionType.LOD_3: 10,  # Haiku: $0.0005 raw → 10 credits = $0.01-0.05
    ActionType.LOD_4: 100,  # Sonnet: $0.014 raw → 100 credits = $0.02-0.05
    ActionType.LOD_5: 400,  # Opus: $0.108 raw → 400 credits = $0.10-0.40
    # INHABIT costs
    ActionType.INHABIT_SESSION: 100,  # 10 min session, mixed models
    ActionType.INHABIT_FORCE: 50,  # 3x normal action (ethical premium)
    ActionType.INHABIT_APOLOGIZE: 5,  # Cheap action to reduce debt
    # Branch costs (state storage)
    ActionType.BRANCH_CREATE: 150,  # $0.01 storage → 150 credits
    ActionType.BRANCH_SWITCH: 10,  # Cheap switching
    ActionType.BRANCH_MERGE: 50,  # Moderate merge cost
}


# Model used for each action (for routing and transparency)
ACTION_MODELS = {
    ActionType.LOD_0: "haiku",
    ActionType.LOD_1: "haiku",
    ActionType.LOD_2: "haiku",
    ActionType.LOD_3: "haiku",
    ActionType.LOD_4: "sonnet",
    ActionType.LOD_5: "opus",
    ActionType.INHABIT_SESSION: "mixed",
    ActionType.INHABIT_FORCE: "sonnet",
    ActionType.INHABIT_APOLOGIZE: "haiku",
    ActionType.BRANCH_CREATE: "none",
    ActionType.BRANCH_SWITCH: "none",
    ActionType.BRANCH_MERGE: "none",
}


# =============================================================================
# Paywall Data Structures
# =============================================================================


@dataclass(frozen=True)
class UpgradeOption:
    """An option presented to user for unlocking an action."""

    type: str  # "subscription" or "credits"
    tier: str | None  # Target tier if subscription upgrade
    credits: int | None  # Credits to purchase if credit pack
    price_usd: float
    unlocks: str  # What this upgrade unlocks


@dataclass(frozen=True)
class PaywallCheck:
    """Input to paywall decision."""

    user_budget: UserBudgetInfo
    action: ActionType
    citizen_id: str | None = None  # Required for INHABIT/consent checks
    consent_state: ConsentState | None = None  # Required for FORCE checks


@dataclass(frozen=True)
class PaywallResult:
    """Output of paywall decision."""

    allowed: bool
    reason: str | None = None
    cost_credits: int = 0  # Credits charged if allowed
    uses_included: bool = False  # True if covered by subscription
    upgrade_options: list[UpgradeOption] = field(default_factory=list)


# =============================================================================
# Paywall Logic
# =============================================================================


def check_paywall(check: PaywallCheck) -> PaywallResult:
    """
    Pure function implementing paywall logic.

    Laws (per spec/town/monetization.md §9):
    1. If action in included allowance and under limit: allowed, cost=0
    2. If action requires credits and user has enough: allowed, cost=action.credits
    3. If action requires credits and user lacks: blocked, show upgrade options
    4. If action requires feature user doesn't have: blocked, show tier upgrade

    Args:
        check: Paywall check input

    Returns:
        PaywallResult with decision and upgrade options
    """
    budget = check.user_budget
    action = check.action
    tier_config = SUBSCRIPTION_TIERS[budget.subscription_tier]

    # Step 1: Check if action requires a feature the user doesn't have
    feature_check = _check_feature_access(budget, action, check.citizen_id, check.consent_state)
    if not feature_check.allowed:
        return feature_check

    # Step 2: Check if action is LOD and covered by subscription
    if action in [
        ActionType.LOD_0,
        ActionType.LOD_1,
        ActionType.LOD_2,
        ActionType.LOD_3,
        ActionType.LOD_4,
        ActionType.LOD_5,
    ]:
        lod_level = int(action.value.replace("lod", ""))
        remaining = budget.monthly_remaining(action=action.value, lod_level=lod_level)

        # Check if LOD is included in subscription
        if lod_level in tier_config.lod_included:
            allowance = tier_config.lod_included[lod_level]

            if allowance == 0:  # Unlimited
                return PaywallResult(
                    allowed=True,
                    cost_credits=0,
                    uses_included=True,
                )

            if allowance > 0 and remaining > 0:
                # Still have monthly allowance
                return PaywallResult(
                    allowed=True,
                    cost_credits=0,
                    uses_included=True,
                )

    # Step 3: Action requires credits (either not included or monthly limit exhausted)
    cost = ACTION_COSTS[action]

    if budget.can_afford_credits(cost):
        return PaywallResult(
            allowed=True,
            cost_credits=cost,
            uses_included=False,
        )

    # Step 4: Insufficient credits - generate upgrade options
    upgrade_options = _generate_upgrade_options(budget, action, cost)

    return PaywallResult(
        allowed=False,
        reason=f"Insufficient credits. Need {cost}, have {budget.credits}.",
        upgrade_options=upgrade_options,
    )


def _check_feature_access(
    budget: UserBudgetInfo,
    action: ActionType,
    citizen_id: str | None,
    consent_state: ConsentState | None,
) -> PaywallResult:
    """Check if user has access to the feature (INHABIT, branching)."""
    tier_config = SUBSCRIPTION_TIERS[budget.subscription_tier]

    # INHABIT checks
    if action in [
        ActionType.INHABIT_SESSION,
        ActionType.INHABIT_FORCE,
        ActionType.INHABIT_APOLOGIZE,
    ]:
        inhabit_level = tier_config.features.get("inhabit", False)

        if not inhabit_level:
            # Tourist tier: no INHABIT access
            return PaywallResult(
                allowed=False,
                reason="INHABIT mode requires Resident tier or higher.",
                upgrade_options=[
                    UpgradeOption(
                        type="subscription",
                        tier="RESIDENT",
                        credits=None,
                        price_usd=9.99,
                        unlocks="INHABIT mode (basic, no force)",
                    ),
                    UpgradeOption(
                        type="subscription",
                        tier="CITIZEN",
                        credits=None,
                        price_usd=29.99,
                        unlocks="INHABIT mode (full, with force)",
                    ),
                ],
            )

        if action == ActionType.INHABIT_FORCE:
            # Force requires "full" INHABIT (Citizen+)
            if inhabit_level != "full" and inhabit_level != "unlimited":
                return PaywallResult(
                    allowed=False,
                    reason="Force mechanic requires Citizen tier or higher.",
                    upgrade_options=[
                        UpgradeOption(
                            type="subscription",
                            tier="CITIZEN",
                            credits=None,
                            price_usd=29.99,
                            unlocks="INHABIT mode with force mechanic",
                        ),
                    ],
                )

            # Check consent debt
            if consent_state and not consent_state.can_force():
                if consent_state.at_rupture():
                    return PaywallResult(
                        allowed=False,
                        reason="Citizen has refused all interaction due to rupture (debt >= 1.0).",
                    )
                else:
                    return PaywallResult(
                        allowed=False,
                        reason=f"Cannot force: debt={consent_state.debt:.2f} (max 0.8) or cooldown active ({consent_state.cooldown:.0f}s).",
                    )

    # Branching checks
    if action in [
        ActionType.BRANCH_CREATE,
        ActionType.BRANCH_SWITCH,
        ActionType.BRANCH_MERGE,
    ]:
        branching = tier_config.features.get("branching", False)

        if branching is False:
            # Not allowed at all
            return PaywallResult(
                allowed=False,
                reason="Branching requires Citizen tier or higher.",
                upgrade_options=[
                    UpgradeOption(
                        type="subscription",
                        tier="CITIZEN",
                        credits=None,
                        price_usd=29.99,
                        unlocks="Timeline branching (3 branches/month)",
                    ),
                ],
            )

        if action == ActionType.BRANCH_CREATE:
            # Check monthly limit (unless unlimited)
            if branching > 0:  # Has limit
                remaining = budget.monthly_remaining("branch")
                if remaining == 0:
                    return PaywallResult(
                        allowed=False,
                        reason=f"Monthly branch limit exhausted ({branching}/month).",
                        upgrade_options=[
                            UpgradeOption(
                                type="subscription",
                                tier="FOUNDER",
                                credits=None,
                                price_usd=99.99,
                                unlocks="Unlimited branching",
                            ),
                        ],
                    )

    # Feature access granted
    return PaywallResult(allowed=True)


def _generate_upgrade_options(
    budget: UserBudgetInfo, action: ActionType, cost: int
) -> list[UpgradeOption]:
    """Generate upgrade options for when user lacks credits."""
    options: list[UpgradeOption] = []

    # Credit packs (per unified-v2.md §1)
    credit_packs: list[tuple[int, float, str]] = [
        (500, 4.99, "Starter Pack"),
        (2500, 19.99, "Explorer Pack"),
        (10000, 59.99, "Adventurer Pack"),
    ]

    # Apply tier discount
    tier_config = SUBSCRIPTION_TIERS[budget.subscription_tier]
    multiplier = tier_config.credit_multiplier

    for credits, price, name in credit_packs:
        if credits >= cost:
            options.append(
                UpgradeOption(
                    type="credits",
                    tier=None,
                    credits=credits,
                    price_usd=price * multiplier,
                    unlocks=f"{credits} credits ({name})",
                )
            )

    # Subscription upgrade if lower tier
    if budget.subscription_tier == "TOURIST":
        # Suggest Resident for LOD 3
        if action == ActionType.LOD_3:
            options.append(
                UpgradeOption(
                    type="subscription",
                    tier="RESIDENT",
                    credits=None,
                    price_usd=9.99,
                    unlocks="50 LOD 3 actions/month + more",
                )
            )
        # Suggest Citizen for LOD 4
        elif action == ActionType.LOD_4:
            options.append(
                UpgradeOption(
                    type="subscription",
                    tier="CITIZEN",
                    credits=None,
                    price_usd=29.99,
                    unlocks="20 LOD 4 actions/month + unlimited LOD 3 + branching",
                )
            )
        # Suggest Founder for LOD 5
        elif action == ActionType.LOD_5:
            options.append(
                UpgradeOption(
                    type="subscription",
                    tier="FOUNDER",
                    credits=None,
                    price_usd=99.99,
                    unlocks="50 LOD 5 actions/month + unlimited LOD 3-4 + API access",
                )
            )

    return options


# =============================================================================
# Helper Functions
# =============================================================================


def get_action_info(action: ActionType) -> dict[str, str | int]:
    """Get metadata about an action for display."""
    return {
        "action": action.value,
        "cost_credits": ACTION_COSTS[action],
        "model": ACTION_MODELS[action],
    }


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "ActionType",
    "ACTION_COSTS",
    "ACTION_MODELS",
    "PaywallCheck",
    "PaywallResult",
    "UpgradeOption",
    "check_paywall",
    "get_action_info",
]
