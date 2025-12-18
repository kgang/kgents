"""
Tests for budget store (credit and subscription management).

Covers:
- UserBudgetInfo data structures
- ConsentState logic (debt, force mechanics)
- InMemoryBudgetStore operations
- Monthly resets and allowances
"""

from datetime import datetime, timedelta

import pytest

from agents.town.budget_store import (
    SUBSCRIPTION_TIERS,
    ConsentState,
    InMemoryBudgetStore,
    UserBudgetInfo,
)

# =============================================================================
# ConsentState Tests
# =============================================================================


def test_consent_state_initial():
    """Test initial consent state."""
    consent = ConsentState(citizen_id="alice")

    assert consent.debt == 0.0
    assert consent.forces == 0
    assert consent.cooldown == 0.0
    assert consent.can_force()
    assert not consent.at_rupture()


def test_consent_state_apply_force():
    """Test applying force increases debt."""
    consent = ConsentState(citizen_id="alice")

    consent.apply_force(severity=0.2)

    assert consent.debt == 0.2
    assert consent.forces == 1
    assert consent.cooldown == 60.0
    assert not consent.can_force()  # Cooldown active


def test_consent_state_cooldown_decay():
    """Test cooldown decays over time."""
    consent = ConsentState(citizen_id="alice")
    consent.apply_force()

    # 30 seconds pass
    consent.cool_down(30.0)

    assert consent.cooldown == 30.0
    assert not consent.can_force()  # Still cooling down

    # Another 30 seconds
    consent.cool_down(30.0)

    assert consent.cooldown == 0.0
    assert consent.debt < 0.2  # Debt also decayed
    assert consent.can_force()  # Can force again


def test_consent_state_debt_decay():
    """Test debt decays at 0.001/sec."""
    consent = ConsentState(citizen_id="alice")
    consent.debt = 0.5

    # 100 seconds pass
    consent.cool_down(100.0)

    assert consent.debt == pytest.approx(0.4, abs=0.01)  # 0.5 - 0.1


def test_consent_state_rupture():
    """Test rupture when debt reaches 1.0."""
    consent = ConsentState(citizen_id="alice")

    # Apply force multiple times
    for _ in range(5):
        consent.apply_force(severity=0.2)

    assert consent.debt == 1.0
    assert consent.at_rupture()
    assert not consent.can_force()


def test_consent_state_apologize():
    """Test apologize reduces debt."""
    consent = ConsentState(citizen_id="alice")
    consent.debt = 0.5

    consent.apologize()

    assert consent.debt == 0.4


def test_consent_state_high_debt_blocks_force():
    """Test force blocked when debt >= 0.8."""
    consent = ConsentState(citizen_id="alice")
    consent.debt = 0.8

    assert not consent.can_force()


# =============================================================================
# UserBudgetInfo Tests
# =============================================================================


def test_user_budget_info_tourist():
    """Test TOURIST tier budget."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
    )

    assert budget.tier.name == "TOURIST"
    assert budget.tier.price_monthly == 0.0
    assert budget.credits == 0

    # LOD 0-1 unlimited
    assert budget.monthly_remaining("lod0", lod_level=0) == 999999
    assert budget.monthly_remaining("lod1", lod_level=1) == 999999

    # LOD 2+ not included
    assert budget.monthly_remaining("lod2", lod_level=2) == 0
    assert budget.monthly_remaining("lod3", lod_level=3) == 0


def test_user_budget_info_resident():
    """Test RESIDENT tier budget."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
    )

    assert budget.tier.name == "RESIDENT"
    assert budget.tier.price_monthly == 9.99

    # LOD 0-2 unlimited
    assert budget.monthly_remaining("lod0", lod_level=0) == 999999
    assert budget.monthly_remaining("lod2", lod_level=2) == 999999

    # LOD 3: 50/month included
    assert budget.monthly_remaining("lod3", lod_level=3) == 50

    # LOD 4+ not included
    assert budget.monthly_remaining("lod4", lod_level=4) == 0


def test_user_budget_info_citizen():
    """Test CITIZEN tier budget."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="CITIZEN",
        subscription_renews_at=datetime.now() + timedelta(days=30),
    )

    assert budget.tier.name == "CITIZEN"
    assert budget.tier.price_monthly == 29.99

    # LOD 0-3 unlimited
    assert budget.monthly_remaining("lod3", lod_level=3) == 999999

    # LOD 4: 20/month
    assert budget.monthly_remaining("lod4", lod_level=4) == 20

    # LOD 5 not included
    assert budget.monthly_remaining("lod5", lod_level=5) == 0

    # Branching: 3/month
    assert budget.monthly_remaining("branch") == 3


def test_user_budget_info_founder():
    """Test FOUNDER tier budget."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="FOUNDER",
        subscription_renews_at=datetime.now() + timedelta(days=30),
    )

    assert budget.tier.name == "FOUNDER"
    assert budget.tier.price_monthly == 99.99

    # LOD 0-4 unlimited
    assert budget.monthly_remaining("lod4", lod_level=4) == 999999

    # LOD 5: 50/month
    assert budget.monthly_remaining("lod5", lod_level=5) == 50

    # Branching unlimited
    assert budget.monthly_remaining("branch") == 999999


def test_user_budget_info_monthly_usage_tracking():
    """Test monthly usage tracking."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="RESIDENT",
        subscription_renews_at=datetime.now() + timedelta(days=30),
    )

    # Use 10 LOD3 actions
    budget.monthly_usage["lod3"] = 10

    assert budget.monthly_remaining("lod3", lod_level=3) == 40  # 50 - 10


def test_user_budget_info_can_afford_credits():
    """Test credit affordability check."""
    budget = UserBudgetInfo(
        user_id="user1",
        subscription_tier="TOURIST",
        subscription_renews_at=None,
        credits=100,
    )

    assert budget.can_afford_credits(50)
    assert budget.can_afford_credits(100)
    assert not budget.can_afford_credits(101)


# =============================================================================
# InMemoryBudgetStore Tests
# =============================================================================


@pytest.mark.asyncio
async def test_budget_store_create_budget():
    """Test creating a budget."""
    store = InMemoryBudgetStore()

    budget = await store.create_budget("user1", "RESIDENT")

    assert budget.user_id == "user1"
    assert budget.subscription_tier == "RESIDENT"
    assert budget.credits == 0
    assert budget.subscription_renews_at is not None


@pytest.mark.asyncio
async def test_budget_store_get_or_create():
    """Test get_or_create creates if missing."""
    store = InMemoryBudgetStore()

    # First call creates
    budget1 = await store.get_or_create("user1", "CITIZEN")
    assert budget1.user_id == "user1"

    # Second call retrieves
    budget2 = await store.get_or_create("user1", "CITIZEN")
    assert budget2.user_id == "user1"
    assert budget2.subscription_tier == "CITIZEN"


@pytest.mark.asyncio
async def test_budget_store_spend_credits():
    """Test spending credits."""
    store = InMemoryBudgetStore()
    await store.create_budget("user1", "TOURIST")

    # Add credits
    await store.add_credits("user1", 100)

    # Spend credits
    success = await store.spend_credits("user1", 50)
    assert success

    budget = await store.get_budget("user1")
    assert budget is not None
    assert budget.credits == 50


@pytest.mark.asyncio
async def test_budget_store_spend_credits_insufficient():
    """Test spending more credits than available."""
    store = InMemoryBudgetStore()
    await store.create_budget("user1", "TOURIST")
    await store.add_credits("user1", 50)

    success = await store.spend_credits("user1", 100)
    assert not success

    budget = await store.get_budget("user1")
    assert budget is not None
    assert budget.credits == 50  # Unchanged


@pytest.mark.asyncio
async def test_budget_store_record_action():
    """Test recording action usage."""
    store = InMemoryBudgetStore()
    await store.create_budget("user1", "RESIDENT")

    # Record LOD3 action (no credits needed if under allowance)
    success = await store.record_action("user1", "lod3", 0)
    assert success

    budget = await store.get_budget("user1")
    assert budget is not None
    assert budget.monthly_usage["lod3"] == 1


@pytest.mark.asyncio
async def test_budget_store_record_action_with_credits():
    """Test recording action that costs credits."""
    store = InMemoryBudgetStore()
    await store.create_budget("user1", "TOURIST")
    await store.add_credits("user1", 100)

    # Record LOD4 action (100 credits)
    success = await store.record_action("user1", "lod4", 100)
    assert success

    budget = await store.get_budget("user1")
    assert budget is not None
    assert budget.monthly_usage["lod4"] == 1
    assert budget.credits == 0


@pytest.mark.asyncio
async def test_budget_store_update_subscription():
    """Test updating subscription tier."""
    store = InMemoryBudgetStore()
    await store.create_budget("user1", "TOURIST")

    renews_at = datetime.now() + timedelta(days=30)
    success = await store.update_subscription("user1", "CITIZEN", renews_at)
    assert success

    budget = await store.get_budget("user1")
    assert budget is not None
    assert budget.subscription_tier == "CITIZEN"
    assert budget.subscription_renews_at == renews_at


@pytest.mark.asyncio
async def test_budget_store_consent_state():
    """Test consent state tracking."""
    store = InMemoryBudgetStore()

    # Initially no consent state
    consent = await store.get_consent_state("user1", "alice")
    assert consent is None

    # Create and update
    new_consent = ConsentState(citizen_id="alice", debt=0.2, forces=1)
    await store.update_consent_state("user1", new_consent)

    # Retrieve
    consent = await store.get_consent_state("user1", "alice")
    assert consent is not None
    assert consent.citizen_id == "alice"
    assert consent.debt == pytest.approx(0.2, abs=0.01)


@pytest.mark.asyncio
async def test_budget_store_consent_decay():
    """Test consent debt decays when retrieved."""
    store = InMemoryBudgetStore()

    # Create consent with debt
    consent = ConsentState(
        citizen_id="alice",
        debt=0.5,
        last_update=datetime.now() - timedelta(seconds=100),
    )
    await store.update_consent_state("user1", consent)

    # Retrieve (should apply decay)
    retrieved = await store.get_consent_state("user1", "alice")
    assert retrieved is not None
    assert retrieved.debt < 0.5  # Decayed


# =============================================================================
# Monthly Reset Tests
# =============================================================================


@pytest.mark.asyncio
async def test_budget_store_monthly_reset():
    """Test monthly usage resets."""
    store = InMemoryBudgetStore()
    budget = await store.create_budget("user1", "RESIDENT")

    # Use some actions
    budget.monthly_usage["lod3"] = 20

    # Simulate month passing
    budget.last_monthly_reset = datetime.now() - timedelta(days=32)

    # Check reset happens
    store._check_reset(budget)

    assert budget.monthly_usage == {}
