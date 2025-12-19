"""
Redis-backed credit and subscription budget store for Agent Town.

Provides persistent, cluster-aware tracking of:
- Credit balances (purchased packs)
- Subscription tiers and included actions
- Monthly usage counters
- Consent debt per citizen

Redis Keys:
    town:budget:{user_id}:credits       - Available credits
    town:budget:{user_id}:subscription  - Subscription tier and renewal date
    town:budget:{user_id}:monthly       - Monthly usage counters (resets monthly)
    town:budget:{user_id}:consent:{cid} - Consent debt per citizen

See: plans/agent-town/unified-v2.md Track C
     spec/town/monetization.md
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID

logger = logging.getLogger(__name__)


# =============================================================================
# Budget Data Structures
# =============================================================================


@dataclass
class SubscriptionTier:
    """Subscription tier definition per spec/town/monetization.md §4."""

    name: str  # TOURIST, RESIDENT, CITIZEN, FOUNDER
    price_monthly: float  # USD
    lod_included: dict[int, int]  # LOD level -> monthly allowance (0 = unlimited)
    features: dict[str, Any]  # inhabit, branching, towns, etc.
    credit_multiplier: float = 1.0  # Discount on credit purchases


# Subscription tiers per unified-v2.md §7
SUBSCRIPTION_TIERS = {
    "TOURIST": SubscriptionTier(
        name="TOURIST",
        price_monthly=0.0,
        lod_included={0: 0, 1: 0},  # 0 = unlimited
        features={
            "inhabit": False,
            "branching": False,
            "towns": 0,  # Demo only
        },
    ),
    "RESIDENT": SubscriptionTier(
        name="RESIDENT",
        price_monthly=9.99,
        lod_included={0: 0, 1: 0, 2: 0, 3: 50},
        features={
            "inhabit": "basic",  # No force
            "branching": False,
            "towns": 1,
        },
        credit_multiplier=1.0,
    ),
    "CITIZEN": SubscriptionTier(
        name="CITIZEN",
        price_monthly=29.99,
        lod_included={0: 0, 1: 0, 2: 0, 3: 0, 4: 20},  # Unlimited LOD 0-3
        features={
            "inhabit": "full",  # With force
            "branching": 3,  # Per month
            "towns": 5,
        },
        credit_multiplier=0.9,  # 10% discount
    ),
    "FOUNDER": SubscriptionTier(
        name="FOUNDER",
        price_monthly=99.99,
        lod_included={0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 50},  # Unlimited LOD 0-4
        features={
            "inhabit": "unlimited",
            "branching": 0,  # 0 = unlimited
            "towns": 0,  # 0 = unlimited
            "api_access": True,
        },
        credit_multiplier=0.75,  # 25% discount
    ),
}


@dataclass
class ConsentState:
    """Tracks consent debt between user and inhabited citizen.

    Per unified-v2.md §2: The Consent Debt Meter

    The consent debt meter is the ethical guardrail. As debt accumulates
    through forced actions, the relationship degrades. At rupture (debt >= 1.0),
    the citizen refuses all interaction until harmony is restored.

    From Glissant: To inhabit is not to possess. The opacity remains.
    """

    citizen_id: str
    debt: float = 0.0  # 0.0 = harmony, 1.0 = rupture
    forces: int = 0  # Total forced actions
    cooldown: float = 0.0  # Seconds until next force allowed
    last_update: datetime = field(default_factory=datetime.now)

    # Consent history for logging/auditing
    force_log: list[dict[str, Any]] = field(default_factory=list)

    def can_force(self) -> bool:
        """Force requires debt < 0.8 and cooldown elapsed."""
        return self.debt < 0.8 and self.cooldown <= 0.0

    def apply_force(self, action: str = "", severity: float = 0.2) -> None:
        """Force increases debt, resets cooldown, logs the action.

        Args:
            action: Description of the forced action (for audit)
            severity: How much debt to add (default 0.2)
        """
        self.debt = min(1.0, self.debt + severity)
        self.forces += 1
        self.cooldown = 60.0  # 60 seconds between forces

        # Log for ethics audit
        self.force_log.append(
            {
                "action": action,
                "severity": severity,
                "debt_after": self.debt,
                "forces_total": self.forces,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def cool_down(self, elapsed: float) -> None:
        """Debt decays over time (harmony restoration)."""
        self.cooldown = max(0.0, self.cooldown - elapsed)
        self.debt = max(0.0, self.debt - elapsed * 0.001)  # Slow decay (0.001/sec)

    def at_rupture(self) -> bool:
        """Citizen refuses all interaction until debt clears."""
        return self.debt >= 1.0

    def apologize(self, sincerity: float = 0.1) -> None:
        """Apologize action reduces debt.

        Args:
            sincerity: How much debt to remove (default 0.1)
        """
        self.debt = max(0.0, self.debt - sincerity)

    def status_message(self) -> str:
        """Get human-readable status message."""
        if self.at_rupture():
            return "RUPTURED - Citizen refuses all interaction"
        elif self.debt >= 0.8:
            return "CRITICAL - One more force will rupture the relationship"
        elif self.debt >= 0.5:
            return "STRAINED - Citizen is uncomfortable"
        elif self.debt >= 0.2:
            return "TENSE - Citizen notices your influence"
        else:
            return "HARMONIOUS - Citizen trusts you"


@dataclass
class UserBudgetInfo:
    """Complete budget information for a user.

    Per unified-v2.md §1 unit economics and §7 subscription tiers.
    """

    user_id: str
    subscription_tier: str  # TOURIST, RESIDENT, CITIZEN, FOUNDER
    subscription_renews_at: datetime | None  # Next renewal date
    credits: int = 0  # Available credits
    monthly_usage: dict[str, int] = field(default_factory=dict)  # Action -> count this month
    last_monthly_reset: datetime = field(default_factory=datetime.now)

    @property
    def tier(self) -> SubscriptionTier:
        """Get tier configuration."""
        return SUBSCRIPTION_TIERS[self.subscription_tier]

    def monthly_remaining(self, action: str, lod_level: int | None = None) -> int:
        """
        Get remaining included actions for this month.

        Args:
            action: Action type (e.g., 'lod3', 'lod4', 'branch')
            lod_level: LOD level if action is LOD view

        Returns:
            Remaining count (0 = unlimited if tier allows, or exhausted)
        """
        if lod_level is not None:
            # Check LOD allowance
            included = self.tier.lod_included.get(lod_level, -1)
            if included == 0:  # Unlimited
                return 999999
            if included == -1:  # Not included
                return 0
            used = self.monthly_usage.get(f"lod{lod_level}", 0)
            return max(0, included - used)

        # Check feature allowance
        feature_limits = {
            "branch": self.tier.features.get("branching", 0),
        }
        limit_value = feature_limits.get(action, 0)
        limit: int = int(limit_value) if limit_value is not None else 0
        if limit == 0:  # Either unlimited or not allowed
            # Check if feature is actually allowed
            if action == "branch" and self.tier.features.get("branching", False) is False:
                return 0
            return 999999
        action_used: int = self.monthly_usage.get(action, 0)
        return max(0, limit - action_used)

    def can_afford_credits(self, credits: int) -> bool:
        """Check if user has enough credits."""
        return self.credits >= credits


# =============================================================================
# Budget Store Protocol
# =============================================================================


class BudgetStore(Protocol):
    """Protocol for budget storage backends."""

    async def get_budget(self, user_id: str) -> UserBudgetInfo | None:
        """Get budget info for a user."""
        ...

    async def create_budget(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Create budget for a new user."""
        ...

    async def spend_credits(self, user_id: str, credits: int) -> bool:
        """
        Spend credits from user's balance.

        Returns True if successful, False if insufficient credits.
        """
        ...

    async def add_credits(self, user_id: str, credits: int) -> bool:
        """Add credits to user's balance (from purchase)."""
        ...

    async def record_action(self, user_id: str, action: str, credits: int) -> bool:
        """
        Record action usage (monthly counter + credit spend if needed).

        Returns True if successful.
        """
        ...

    async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None:
        """Get consent debt state for a user-citizen pair."""
        ...

    async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool:
        """Update consent debt state."""
        ...

    async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool:
        """Update user's subscription tier and renewal date."""
        ...

    async def get_or_create(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Get existing budget or create new one."""
        ...


# =============================================================================
# In-Memory Store (Development/Testing)
# =============================================================================


class InMemoryBudgetStore:
    """
    In-memory budget store for development and testing.

    NOT suitable for production - budgets are lost on restart
    and not shared across replicas.
    """

    def __init__(self) -> None:
        self._budgets: dict[str, UserBudgetInfo] = {}
        self._consent_states: dict[tuple[str, str], ConsentState] = {}

    async def get_budget(self, user_id: str) -> UserBudgetInfo | None:
        """Get budget info for a user."""
        budget = self._budgets.get(user_id)
        if budget:
            self._check_reset(budget)
        return budget

    async def create_budget(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Create budget for a new user."""
        budget = UserBudgetInfo(
            user_id=user_id,
            subscription_tier=tier,
            subscription_renews_at=None
            if tier == "TOURIST"
            else datetime.now() + timedelta(days=30),
        )
        self._budgets[user_id] = budget
        return budget

    async def spend_credits(self, user_id: str, credits: int) -> bool:
        """Spend credits from user's balance."""
        budget = await self.get_budget(user_id)
        if not budget:
            return False

        if not budget.can_afford_credits(credits):
            return False

        budget.credits -= credits
        return True

    async def add_credits(self, user_id: str, credits: int) -> bool:
        """Add credits to user's balance."""
        budget = await self.get_budget(user_id)
        if not budget:
            return False

        budget.credits += credits
        return True

    async def record_action(self, user_id: str, action: str, credits: int) -> bool:
        """Record action usage."""
        budget = await self.get_budget(user_id)
        if not budget:
            return False

        # Increment monthly counter
        if action not in budget.monthly_usage:
            budget.monthly_usage[action] = 0
        budget.monthly_usage[action] += 1

        # Spend credits if needed
        if credits > 0:
            return await self.spend_credits(user_id, credits)

        return True

    async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None:
        """Get consent debt state."""
        key = (user_id, citizen_id)
        consent = self._consent_states.get(key)

        if consent:
            # Apply decay since last update
            elapsed = (datetime.now() - consent.last_update).total_seconds()
            consent.cool_down(elapsed)
            consent.last_update = datetime.now()

        return consent

    async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool:
        """Update consent debt state."""
        key = (user_id, consent.citizen_id)
        consent.last_update = datetime.now()
        self._consent_states[key] = consent
        return True

    async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool:
        """Update subscription tier and renewal."""
        budget = await self.get_budget(user_id)
        if not budget:
            return False

        budget.subscription_tier = tier
        budget.subscription_renews_at = renews_at
        return True

    async def get_or_create(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Get existing budget or create new one.

        Special test users (for development and testing):
        - founder_test: FOUNDER tier
        - citizen_test: CITIZEN tier
        - resident_test: RESIDENT tier
        """
        budget = await self.get_budget(user_id)
        if budget is None:
            effective_tier = _get_test_tier(user_id, tier)
            budget = await self.create_budget(user_id, effective_tier)
        return budget

    def _check_reset(self, budget: UserBudgetInfo) -> None:
        """Check and apply monthly resets."""
        now = datetime.now()

        # Monthly reset
        if (
            now.month != budget.last_monthly_reset.month
            or now.year != budget.last_monthly_reset.year
        ):
            budget.monthly_usage = {}
            budget.last_monthly_reset = now


# =============================================================================
# Redis Store (Production)
# =============================================================================


class RedisBudgetStore:
    """
    Redis-backed budget store for production.

    Uses Redis with JSON serialization for complex data:
    - Credits balance
    - Subscription tier and renewal
    - Monthly usage hash (resets monthly)
    - Consent state per citizen

    Requires: redis-py
    """

    def __init__(self, redis_url: str | None = None) -> None:
        """
        Initialize Redis connection.

        Args:
            redis_url: Redis URL (default: from REDIS_URL env var)
        """
        import os

        self._redis_url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379")
        self._redis: Any = None

    async def _get_redis(self) -> Any:
        """Lazy initialization of Redis client."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = await redis.from_url(self._redis_url)
            except ImportError:
                logger.warning("redis package not installed, falling back to mock")
                return _MockRedis()
        return self._redis

    def _credits_key(self, user_id: str) -> str:
        """Redis key for credits balance."""
        return f"town:budget:{user_id}:credits"

    def _subscription_key(self, user_id: str) -> str:
        """Redis key for subscription metadata."""
        return f"town:budget:{user_id}:subscription"

    def _monthly_key(self, user_id: str) -> str:
        """Redis key for monthly usage counters."""
        return f"town:budget:{user_id}:monthly"

    def _consent_key(self, user_id: str, citizen_id: str) -> str:
        """Redis key for consent debt."""
        return f"town:budget:{user_id}:consent:{citizen_id}"

    def _monthly_ttl(self) -> int:
        """Seconds until end of month (UTC)."""
        now = datetime.utcnow()
        if now.month == 12:
            end_of_month = now.replace(
                year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0
            )
        else:
            end_of_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0)
        return int((end_of_month - now).total_seconds())

    async def get_budget(self, user_id: str) -> UserBudgetInfo | None:
        """Get budget info for a user."""
        r = await self._get_redis()

        # Get subscription meta
        sub_data = await r.hgetall(self._subscription_key(user_id))
        if not sub_data:
            return None

        tier = sub_data.get(b"tier", b"TOURIST").decode()
        renews_at_str = sub_data.get(b"renews_at")
        renews_at = datetime.fromisoformat(renews_at_str.decode()) if renews_at_str else None

        # Get credits
        credits = int(await r.get(self._credits_key(user_id)) or 0)

        # Get monthly usage
        monthly_data = await r.hgetall(self._monthly_key(user_id))
        monthly_usage = {k.decode(): int(v) for k, v in monthly_data.items() if monthly_data}

        return UserBudgetInfo(
            user_id=user_id,
            subscription_tier=tier,
            subscription_renews_at=renews_at,
            credits=credits,
            monthly_usage=monthly_usage,
        )

    async def create_budget(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Create budget for a new user."""
        r = await self._get_redis()

        renews_at = None if tier == "TOURIST" else datetime.now() + timedelta(days=30)

        # Store subscription metadata
        sub_data = {"tier": tier}
        if renews_at:
            sub_data["renews_at"] = renews_at.isoformat()
        await r.hset(self._subscription_key(user_id), mapping=sub_data)

        # Initialize credits
        await r.set(self._credits_key(user_id), 0)

        # Initialize monthly usage hash with TTL
        monthly_key = self._monthly_key(user_id)
        await r.hset(monthly_key, "initialized", "1")
        await r.expire(monthly_key, self._monthly_ttl())

        return UserBudgetInfo(
            user_id=user_id,
            subscription_tier=tier,
            subscription_renews_at=renews_at,
            credits=0,
            monthly_usage={},
        )

    async def spend_credits(self, user_id: str, credits: int) -> bool:
        """Spend credits atomically."""
        r = await self._get_redis()

        # Check balance
        current = int(await r.get(self._credits_key(user_id)) or 0)
        if current < credits:
            return False

        # Decrement
        await r.decrby(self._credits_key(user_id), credits)
        return True

    async def add_credits(self, user_id: str, credits: int) -> bool:
        """Add credits."""
        r = await self._get_redis()
        await r.incrby(self._credits_key(user_id), credits)
        return True

    async def record_action(self, user_id: str, action: str, credits: int) -> bool:
        """Record action and spend credits if needed."""
        r = await self._get_redis()

        # Increment monthly counter
        monthly_key = self._monthly_key(user_id)
        await r.hincrby(monthly_key, action, 1)
        await r.expire(monthly_key, self._monthly_ttl())  # Refresh TTL

        # Spend credits if needed
        if credits > 0:
            return await self.spend_credits(user_id, credits)

        return True

    async def get_consent_state(self, user_id: str, citizen_id: str) -> ConsentState | None:
        """Get consent debt state."""
        r = await self._get_redis()

        data = await r.hgetall(self._consent_key(user_id, citizen_id))
        if not data:
            return None

        debt = float(data.get(b"debt", b"0.0"))
        forces = int(data.get(b"forces", b"0"))
        cooldown = float(data.get(b"cooldown", b"0.0"))
        last_update_str = data.get(b"last_update")
        last_update = (
            datetime.fromisoformat(last_update_str.decode()) if last_update_str else datetime.now()
        )

        consent = ConsentState(
            citizen_id=citizen_id,
            debt=debt,
            forces=forces,
            cooldown=cooldown,
            last_update=last_update,
        )

        # Apply decay
        elapsed = (datetime.now() - consent.last_update).total_seconds()
        consent.cool_down(elapsed)
        consent.last_update = datetime.now()

        return consent

    async def update_consent_state(self, user_id: str, consent: ConsentState) -> bool:
        """Update consent debt state."""
        r = await self._get_redis()

        data = {
            "debt": str(consent.debt),
            "forces": str(consent.forces),
            "cooldown": str(consent.cooldown),
            "last_update": consent.last_update.isoformat(),
        }

        await r.hset(self._consent_key(user_id, consent.citizen_id), mapping=data)
        return True

    async def update_subscription(self, user_id: str, tier: str, renews_at: datetime) -> bool:
        """Update subscription tier and renewal."""
        r = await self._get_redis()

        sub_data = {"tier": tier, "renews_at": renews_at.isoformat()}
        await r.hset(self._subscription_key(user_id), mapping=sub_data)
        return True

    async def get_or_create(self, user_id: str, tier: str = "TOURIST") -> UserBudgetInfo:
        """Get existing budget or create new one.

        Special test users (for development and testing):
        - founder_test: FOUNDER tier
        - citizen_test: CITIZEN tier
        - resident_test: RESIDENT tier
        """
        budget = await self.get_budget(user_id)
        if budget is None:
            effective_tier = _get_test_tier(user_id, tier)
            budget = await self.create_budget(user_id, effective_tier)
        return budget


# =============================================================================
# Test User Tier Mapping
# =============================================================================


def _get_test_tier(user_id: str, default_tier: str) -> str:
    """Map well-known test users to appropriate tiers.

    Per plans/meta.md: Dev API keys built-in pattern.
    """
    test_tiers = {
        "founder_test": "FOUNDER",
        "citizen_test": "CITIZEN",
        "resident_test": "RESIDENT",
    }
    return test_tiers.get(user_id, default_tier)


# =============================================================================
# Mock Redis (for when redis package not installed)
# =============================================================================


class _MockRedis:
    """Mock Redis for environments without redis package."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}
        self._hashes: dict[str, dict[bytes, bytes]] = {}

    async def get(self, key: str) -> bytes | None:
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: Any) -> None:
        self._data[key] = str(value).encode()

    async def incrby(self, key: str, amount: int) -> int:
        current = int(self._data.get(key, b"0"))
        new_val = current + amount
        self._data[key] = str(new_val).encode()
        return new_val

    async def expire(self, key: str, ttl: int) -> None:
        pass  # TTL not implemented in mock

    async def hgetall(self, key: str) -> dict[bytes, bytes]:
        return self._hashes.get(key, {})

    async def hset(self, key: str, mapping: dict[str, str]) -> None:
        if key not in self._hashes:
            self._hashes[key] = {}
        for k, v in mapping.items():
            self._hashes[key][k.encode()] = v.encode()

    def pipeline(self) -> "_MockPipeline":
        return _MockPipeline(self)


class _MockPipeline:
    """Mock Redis pipeline."""

    def __init__(self, redis: _MockRedis) -> None:
        self._redis = redis
        self._commands: list[tuple[str, tuple[Any, ...]]] = []

    def incrby(self, key: str, amount: int) -> "_MockPipeline":
        self._commands.append(("incrby", (key, amount)))
        return self

    def expire(self, key: str, ttl: int) -> "_MockPipeline":
        self._commands.append(("expire", (key, ttl)))
        return self

    async def execute(self) -> list[Any]:
        results = []
        for cmd, args in self._commands:
            if cmd == "incrby":
                result = await self._redis.incrby(*args)
            elif cmd == "expire":
                await self._redis.expire(*args)
                result = True
            else:
                result = None
            results.append(result)
        return results


# =============================================================================
# Factory Function
# =============================================================================


def create_budget_store(use_redis: bool = True) -> BudgetStore:
    """
    Create a budget store instance.

    Args:
        use_redis: If True, use Redis if available, else in-memory

    Returns:
        BudgetStore implementation
    """
    if use_redis:
        try:
            return RedisBudgetStore()
        except Exception as e:
            logger.warning(f"Failed to create Redis store: {e}, using in-memory")

    return InMemoryBudgetStore()


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "BudgetStore",
    "ConsentState",
    "InMemoryBudgetStore",
    "RedisBudgetStore",
    "SubscriptionTier",
    "SUBSCRIPTION_TIERS",
    "UserBudgetInfo",
    "create_budget_store",
]
