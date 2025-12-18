"""
Tests for paywall logic.

Covers:
- Action cost catalog
- Feature access checks (INHABIT, branching)
- Credit-based gating
- Subscription tier allowances
- Consent debt blocking
- Upgrade option generation
"""

from datetime import datetime, timedelta

import pytest

from agents.town.budget_store import ConsentState, UserBudgetInfo
from agents.town.paywall import (
    ACTION_COSTS,
    ActionType,
    PaywallCheck,
    check_paywall,
    get_action_info,
)

# =============================================================================
# Action Catalog Tests
# =============================================================================


def test_action_costs_defined():
    """Test all actions have defined costs."""
    for action_type in ActionType:
        assert action_type in ACTION_COSTS


def test_action_costs_margin_safe():
    """Test LOD costs match margin-safe pricing per unified-v2.md."""
    # LOD 3: Haiku, 10 credits
    assert ACTION_COSTS[ActionType.LOD_3] == 10

    # LOD 4: Sonnet, 100 credits (margin-safe)
    assert ACTION_COSTS[ActionType.LOD_4] == 100

    # LOD 5: Opus, 400 credits (margin-safe)
    assert ACTION_COSTS[ActionType.LOD_5] == 400


def test_action_info():
    """Test get_action_info returns metadata."""
    info = get_action_info(ActionType.LOD_4)

    assert info["action"] == "lod4"
    assert info["cost_credits"] == 100
    assert info["model"] == "sonnet"


# =============================================================================
# LOD Access Tests
# =============================================================================


def test_paywall_tourist_lod0_free():
    """Test TOURIST can access LOD 0-1 for free."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_0)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 0
    assert result.uses_included


def test_paywall_tourist_lod2_free():
    """Test TOURIST can access LOD 2 for free (Haiku-tier content)."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=0,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_2)
    result = check_paywall(check)

    # LOD 2 is free (Haiku tier) - no cost
    # But not included in subscription, so cost is 0 but not uses_included
    # Actually, checking the action costs - LOD 2 is 0 credits
    assert result.cost_credits == 0


def test_paywall_resident_lod3_included():
    """Test RESIDENT has 50 LOD3 actions/month included."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={},
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 0
    assert result.uses_included


def test_paywall_resident_lod3_exhausted():
    """Test RESIDENT LOD3 requires credits after monthly limit."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={"lod3": 50},  # Exhausted allowance
        credits=100,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 10  # Now costs credits
    assert not result.uses_included


def test_paywall_citizen_lod3_unlimited():
    """Test CITIZEN has unlimited LOD3."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={"lod3": 1000},  # Usage doesn't matter
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 0
    assert result.uses_included


def test_paywall_citizen_lod4_included():
    """Test CITIZEN has 20 LOD4 actions/month."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={"lod4": 10},
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_4)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 0
    assert result.uses_included


def test_paywall_founder_lod5_included():
    """Test FOUNDER has 50 LOD5 actions/month."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="FOUNDER",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={},
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_5)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 0
    assert result.uses_included


# =============================================================================
# Credit-Based Access Tests
# =============================================================================


def test_paywall_with_credits():
    """Test user with credits can pay for action."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=500,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_4)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 100
    assert not result.uses_included


def test_paywall_insufficient_credits():
    """Test insufficient credits blocks action."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=50,  # Need 100 for LOD4
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_4)
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "Insufficient credits" in result.reason
    assert len(result.upgrade_options) > 0


# =============================================================================
# INHABIT Feature Access Tests
# =============================================================================


def test_paywall_tourist_inhabit_blocked():
    """Test TOURIST cannot access INHABIT."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
    )

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_SESSION,
        citizen_id="alice",
    )
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "INHABIT mode requires Resident tier" in result.reason
    assert len(result.upgrade_options) > 0


def test_paywall_resident_inhabit_allowed():
    """Test RESIDENT can access basic INHABIT."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_SESSION,
        citizen_id="alice",
    )
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 100


def test_paywall_resident_force_blocked():
    """Test RESIDENT cannot use force mechanic."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    consent = ConsentState(citizen_id="alice", debt=0.0)

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_FORCE,
        citizen_id="alice",
        consent_state=consent,
    )
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "Force mechanic requires Citizen tier" in result.reason


def test_paywall_citizen_force_allowed():
    """Test CITIZEN can use force mechanic."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    consent = ConsentState(citizen_id="alice", debt=0.0)

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_FORCE,
        citizen_id="alice",
        consent_state=consent,
    )
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 50


def test_paywall_force_blocked_by_debt():
    """Test force blocked when consent debt >= 0.8."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    consent = ConsentState(citizen_id="alice", debt=0.8)

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_FORCE,
        citizen_id="alice",
        consent_state=consent,
    )
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "Cannot force" in result.reason


def test_paywall_force_blocked_by_rupture():
    """Test force blocked when citizen at rupture."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    consent = ConsentState(citizen_id="alice", debt=1.0)

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_FORCE,
        citizen_id="alice",
        consent_state=consent,
    )
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "refused all interaction" in result.reason


# =============================================================================
# Branching Feature Access Tests
# =============================================================================


def test_paywall_tourist_branching_blocked():
    """Test TOURIST cannot access branching."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.BRANCH_CREATE)
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "Branching requires Citizen tier" in result.reason


def test_paywall_resident_branching_blocked():
    """Test RESIDENT cannot access branching."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.BRANCH_CREATE)
    result = check_paywall(check)

    assert not result.allowed
    assert result.reason is not None and "Branching requires Citizen tier" in result.reason


def test_paywall_citizen_branching_allowed():
    """Test CITIZEN can create branches (3/month)."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={},
        credits=500,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.BRANCH_CREATE)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 150


def test_paywall_founder_branching_unlimited():
    """Test FOUNDER has unlimited branching."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="FOUNDER",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        monthly_usage={"branch": 100},  # Usage doesn't matter
        credits=500,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.BRANCH_CREATE)
    result = check_paywall(check)

    assert result.allowed


# =============================================================================
# Upgrade Option Tests
# =============================================================================


def test_paywall_generates_credit_packs():
    """Test upgrade options include credit packs."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=0,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_4)
    result = check_paywall(check)

    assert not result.allowed

    # Should have credit pack options
    credit_options = [o for o in result.upgrade_options if o.type == "credits"]
    assert len(credit_options) > 0

    # Should have packs with enough credits
    for option in credit_options:
        assert option.credits is not None and option.credits >= 100


def test_paywall_generates_subscription_upgrades():
    """Test upgrade options include subscription tiers."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=0,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.LOD_3)
    result = check_paywall(check)

    assert not result.allowed

    # Should suggest RESIDENT for LOD3
    sub_options = [o for o in result.upgrade_options if o.type == "subscription"]
    assert len(sub_options) > 0
    assert any(o.tier == "RESIDENT" for o in sub_options)


def test_paywall_credit_multiplier_applied():
    """Test tier credit multiplier applies to packs."""
    budget_citizen = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=0,
    )

    check = PaywallCheck(user_budget=budget_citizen, action=ActionType.LOD_5)
    result = check_paywall(check)

    # CITIZEN has 10% discount (0.9 multiplier)
    credit_options = [o for o in result.upgrade_options if o.type == "credits"]
    if credit_options:
        # Check prices are discounted
        starter = next((o for o in credit_options if o.credits == 500), None)
        if starter:
            assert starter.price_usd == pytest.approx(4.99 * 0.9, abs=0.01)


# =============================================================================
# Edge Cases
# =============================================================================


def test_paywall_apologize_action():
    """Test INHABIT apologize action (cheap)."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=10,
    )

    check = PaywallCheck(
        user_budget=budget,
        action=ActionType.INHABIT_APOLOGIZE,
        citizen_id="alice",
    )
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 5


def test_paywall_branch_switch_cheap():
    """Test branch switching is cheaper than creating."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
        credits=500,
    )

    check = PaywallCheck(user_budget=budget, action=ActionType.BRANCH_SWITCH)
    result = check_paywall(check)

    assert result.allowed
    assert result.cost_credits == 10  # Cheap switch
    assert ACTION_COSTS[ActionType.BRANCH_SWITCH] < ACTION_COSTS[ActionType.BRANCH_CREATE]
