"""
SharedSubstrate: The building where all agents have rooms.

Phase 5 of Memory Architecture - Shared memory substrate where agents
receive allocated crystals by default, with upgrade paths to dedicated
crystals for justified cases.

Categorical insight: This is a slice category over Agent.
Each allocation is a morphism Agent → MemorySpace.

The Four Pillars integrate here:
- Stigmergy: Routing via pheromone gradients
- Active Inference: Promotion via usage patterns
- Wittgenstein: Each allocation is a language game position
- Accursed Share: Compaction as purposeful forgetting
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Callable, Generic, NewType, TypeVar

from .crystal import MemoryCrystal

if TYPE_CHECKING:
    from .stigmergy import PheromoneField, SenseResult

T = TypeVar("T")
AgentId = NewType("AgentId", str)


# =============================================================================
# Memory Quota
# =============================================================================


@dataclass(frozen=True)
class MemoryQuota:
    """
    Agent's allocated memory budget.

    Categorical: This is a resource object in the category of allocations.
    """

    max_patterns: int = 1000
    max_size_bytes: int = 10 * 1024 * 1024  # 10MB
    soft_limit_ratio: float = 0.8  # Warn at 80%

    def soft_limit_patterns(self) -> int:
        """Patterns at which to warn."""
        return int(self.max_patterns * self.soft_limit_ratio)


# =============================================================================
# Compaction Trigger
# =============================================================================


@dataclass
class CompactionTrigger:
    """When to run automatic consolidation."""

    on_health_degraded: bool = True
    on_schedule: timedelta | None = timedelta(hours=1)
    on_memory_pressure: float = 0.8  # 80% of quota
    custom: Callable[["Allocation[Any]"], bool] | None = None

    def should_compact(self, allocation: "Allocation[Any]") -> bool:
        """Check if compaction should run."""
        # Memory pressure check
        if allocation.pattern_count > 0:
            usage_ratio = allocation.pattern_count / allocation.quota.max_patterns
            if usage_ratio >= self.on_memory_pressure:
                return True

        # Custom trigger
        if self.custom and self.custom(allocation):
            return True

        return False


# =============================================================================
# Lifecycle Policy
# =============================================================================


@dataclass
class LifecyclePolicy:
    """
    Human-readable lifecycle for ghost cache entries.

    Meta principle: "human readable with safeguards by default construction"
    The human_label is REQUIRED—no anonymous debris.
    """

    human_label: str  # REQUIRED: e.g., "k-gent working memory"
    ttl: timedelta = field(default_factory=lambda: timedelta(hours=24))
    max_size_bytes: int = 1024 * 1024  # 1MB per entry
    compaction_trigger: CompactionTrigger = field(default_factory=CompactionTrigger)

    def __post_init__(self) -> None:
        if not self.human_label:
            raise ValueError("human_label is required (no anonymous debris)")

    def is_expired(self, created_at: datetime) -> bool:
        """Check if allocation has exceeded TTL."""
        return datetime.now() - created_at > self.ttl


# =============================================================================
# Allocation
# =============================================================================


@dataclass
class Allocation(Generic[T]):
    """
    An agent's room in the shared substrate.

    Each allocation is a morphism Agent → MemorySpace in the slice category.
    """

    agent_id: AgentId
    namespace: str  # Prefix for concept_ids
    quota: MemoryQuota
    lifecycle: LifecyclePolicy
    _crystal: MemoryCrystal[T] = field(default_factory=lambda: MemoryCrystal())
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    pattern_count: int = 0

    def namespaced_id(self, concept_id: str) -> str:
        """Prefix concept_id with namespace to avoid collisions."""
        return f"{self.namespace}:{concept_id}"

    async def store(self, concept_id: str, content: T, embedding: list[float]) -> bool:
        """
        Store a pattern in this allocation's crystal.

        Returns False if quota exceeded.
        """
        if self.pattern_count >= self.quota.max_patterns:
            return False

        namespaced = self.namespaced_id(concept_id)
        self._crystal.store(namespaced, content, embedding)
        self.pattern_count += 1
        self._record_access()
        return True

    async def retrieve(
        self, cue: list[float], threshold: float = 0.5, limit: int = 10
    ) -> list[Any]:
        """Retrieve patterns by resonance."""
        self._record_access()
        return self._crystal.retrieve(cue, threshold, limit)

    def _record_access(self) -> None:
        """Record an access for tracking."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def is_at_soft_limit(self) -> bool:
        """Check if approaching quota."""
        return self.pattern_count >= self.quota.soft_limit_patterns()

    def usage_ratio(self) -> float:
        """Current usage as ratio of quota."""
        return self.pattern_count / self.quota.max_patterns


# =============================================================================
# Promotion Decision
# =============================================================================


@dataclass(frozen=True)
class PromotionDecision:
    """Result of should_promote evaluation."""

    should_promote: bool
    auto: bool  # Was this system-triggered?
    reason: str | None


# =============================================================================
# Crystal Policy
# =============================================================================


@dataclass
class CrystalPolicy:
    """
    Decides when agents get their own crystal.

    Categorical: This is a predicate in the category of allocations.
    promotion_criteria : Allocation → Bool

    The adjunction: usage ⊣ promotion
    Heavy usage creates "pressure" that promotes to dedicated crystal.
    """

    access_frequency_threshold: float = 10.0  # accesses per hour
    size_threshold_bytes: int = 5 * 1024 * 1024  # 5MB
    min_age_hours: float = 1.0  # Don't promote too young
    explicit_request_allowed: bool = True

    def should_promote(self, allocation: Allocation[Any]) -> PromotionDecision:
        """
        Evaluate whether allocation should be promoted to dedicated crystal.

        Category law: promote >> demote ≅ id (up to resolution loss)
        """
        hours_alive = (datetime.now() - allocation.created_at).total_seconds() / 3600

        # Too young
        if hours_alive < self.min_age_hours:
            return PromotionDecision(False, False, "too_young")

        # Access frequency check
        access_rate = allocation.access_count / max(hours_alive, 0.01)
        if access_rate >= self.access_frequency_threshold:
            return PromotionDecision(True, True, f"access_rate={access_rate:.1f}/hr")

        # Size check (would need actual measurement)
        # Placeholder: use pattern_count as proxy
        estimated_size = allocation.pattern_count * 1024  # ~1KB per pattern
        if estimated_size >= self.size_threshold_bytes:
            return PromotionDecision(True, True, f"size={estimated_size}")

        return PromotionDecision(False, False, None)


# =============================================================================
# Dedicated Crystal
# =============================================================================


@dataclass
class DedicatedCrystal(Generic[T]):
    """
    A promoted agent's dedicated crystal (not shared).

    Once promoted, the agent owns this crystal independently.
    """

    agent_id: AgentId
    crystal: MemoryCrystal[T]
    promoted_at: datetime = field(default_factory=datetime.now)
    promotion_reason: str = ""
    original_allocation: Allocation[T] | None = None


# =============================================================================
# Shared Substrate
# =============================================================================


@dataclass
class SharedSubstrate(Generic[T]):
    """
    The building where all agents have rooms.

    Categorical insight: This is a slice category over Agent.
    Each allocation is a morphism Agent → MemorySpace.

    The substrate provides:
    1. Shared interference pattern (all agents contribute)
    2. Namespaced allocations (each agent has a "room")
    3. Promotion policy (upgrade to dedicated crystal)
    4. Auto-compaction (graceful forgetting)
    """

    global_crystal: MemoryCrystal[T] = field(default_factory=MemoryCrystal)
    allocations: dict[AgentId, Allocation[T]] = field(default_factory=dict)
    dedicated_crystals: dict[AgentId, DedicatedCrystal[T]] = field(default_factory=dict)
    promotion_policy: CrystalPolicy = field(default_factory=CrystalPolicy)
    _default_quota: MemoryQuota = field(default_factory=MemoryQuota)

    def allocate(
        self,
        agent_id: AgentId | str,
        quota: MemoryQuota | None = None,
        lifecycle: LifecyclePolicy | None = None,
        human_label: str | None = None,
    ) -> Allocation[T]:
        """
        Give agent a room in the shared building.

        Args:
            agent_id: Unique agent identifier
            quota: Memory quota (defaults to standard)
            lifecycle: Lifecycle policy (requires human_label if not provided)
            human_label: Human-readable label (required if lifecycle not provided)

        Returns:
            The created Allocation

        Raises:
            ValueError: If human_label not provided and no lifecycle
        """
        agent_id = AgentId(agent_id) if isinstance(agent_id, str) else agent_id

        # Already allocated?
        if agent_id in self.allocations:
            return self.allocations[agent_id]

        # Already promoted?
        if agent_id in self.dedicated_crystals:
            raise ValueError(f"Agent {agent_id} already has dedicated crystal")

        # Build quota
        quota = quota or self._default_quota

        # Build lifecycle (requires human_label)
        if lifecycle is None:
            if human_label is None:
                raise ValueError(
                    "human_label required (no anonymous debris). "
                    "Provide either lifecycle or human_label."
                )
            lifecycle = LifecyclePolicy(human_label=human_label)

        # Create allocation
        allocation: Allocation[T] = Allocation(
            agent_id=agent_id,
            namespace=str(agent_id),
            quota=quota,
            lifecycle=lifecycle,
        )

        self.allocations[agent_id] = allocation
        return allocation

    def get_allocation(self, agent_id: AgentId | str) -> Allocation[T] | None:
        """Get an existing allocation."""
        agent_id = AgentId(agent_id) if isinstance(agent_id, str) else agent_id
        return self.allocations.get(agent_id)

    def promote(self, agent_id: AgentId | str) -> DedicatedCrystal[T]:
        """
        Upgrade agent to own crystal.

        Category law: promote >> demote ≅ id (up to resolution loss)

        The roundtrip isn't exact because:
        1. Dedicated crystal may have grown
        2. Demotion requires compression (resolution loss)
        """
        agent_id = AgentId(agent_id) if isinstance(agent_id, str) else agent_id

        if agent_id in self.dedicated_crystals:
            return self.dedicated_crystals[agent_id]

        allocation = self.allocations.get(agent_id)
        if allocation is None:
            raise ValueError(f"No allocation for {agent_id}")

        # Check policy
        decision = self.promotion_policy.should_promote(allocation)

        # Create dedicated crystal (copy from allocation)
        dedicated = DedicatedCrystal(
            agent_id=agent_id,
            crystal=allocation._crystal,  # Transfer ownership
            promotion_reason=decision.reason or "explicit_request",
            original_allocation=allocation,
        )

        # Record
        self.dedicated_crystals[agent_id] = dedicated

        # Remove from shared allocations
        del self.allocations[agent_id]

        return dedicated

    def demote(
        self, agent_id: AgentId | str, compress_ratio: float = 0.5
    ) -> Allocation[T]:
        """
        Demote dedicated crystal back to shared allocation.

        Category law: promote >> demote ≅ id (up to resolution loss)

        Args:
            agent_id: Agent to demote
            compress_ratio: Compression for the crystal (resolution loss)

        Returns:
            New allocation in shared substrate
        """
        agent_id = AgentId(agent_id) if isinstance(agent_id, str) else agent_id

        if agent_id not in self.dedicated_crystals:
            raise ValueError(f"No dedicated crystal for {agent_id}")

        dedicated = self.dedicated_crystals[agent_id]

        # Compress crystal (resolution loss)
        compressed_crystal = dedicated.crystal.compress(compress_ratio)

        # Create new allocation
        lifecycle = LifecyclePolicy(human_label=f"{agent_id} (demoted)")
        allocation: Allocation[T] = Allocation(
            agent_id=agent_id,
            namespace=str(agent_id),
            quota=self._default_quota,
            lifecycle=lifecycle,
            _crystal=compressed_crystal,
        )

        # Record
        self.allocations[agent_id] = allocation
        del self.dedicated_crystals[agent_id]

        return allocation

    async def compact(self, allocation: Allocation[T]) -> int:
        """
        Run compaction on an allocation.

        Compaction = purposeful forgetting (Accursed Share principle).

        Returns:
            Number of patterns affected
        """
        if not allocation.lifecycle.compaction_trigger.should_compact(allocation):
            return 0

        # Compress the crystal (holographic: all patterns fuzzier)
        old_crystal = allocation._crystal
        allocation._crystal = old_crystal.compress(0.8)  # 20% resolution loss

        return len(old_crystal.concepts)

    def stats(self) -> dict[str, Any]:
        """Get substrate statistics."""
        return {
            "allocation_count": len(self.allocations),
            "dedicated_count": len(self.dedicated_crystals),
            "total_patterns": sum(a.pattern_count for a in self.allocations.values()),
            "global_crystal_stats": self.global_crystal.stats(),
        }


# =============================================================================
# Factory Functions
# =============================================================================

# NOTE: CategoricalRouter has been moved to routing.py
# Import from there for the full-featured router with Task types,
# gradient maps, route traces, and adjunction verification.
# The simpler version here has been removed to avoid duplication.


def create_substrate(
    default_quota: MemoryQuota | None = None,
    promotion_policy: CrystalPolicy | None = None,
) -> SharedSubstrate[Any]:
    """Create a SharedSubstrate with sensible defaults."""
    return SharedSubstrate(
        _default_quota=default_quota or MemoryQuota(),
        promotion_policy=promotion_policy or CrystalPolicy(),
    )


def create_allocation_for_agent(
    substrate: SharedSubstrate[Any],
    agent_id: str,
    human_label: str,
    max_patterns: int = 1000,
    ttl_hours: int = 24,
) -> Allocation[Any]:
    """Convenience function to create an allocation."""
    return substrate.allocate(
        agent_id=agent_id,
        quota=MemoryQuota(max_patterns=max_patterns),
        lifecycle=LifecyclePolicy(
            human_label=human_label,
            ttl=timedelta(hours=ttl_hours),
        ),
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "AgentId",
    "MemoryQuota",
    "CompactionTrigger",
    "LifecyclePolicy",
    "Allocation",
    "PromotionDecision",
    "CrystalPolicy",
    "DedicatedCrystal",
    "SharedSubstrate",
    # Factory functions
    "create_substrate",
    "create_allocation_for_agent",
    # NOTE: CategoricalRouter now lives in routing.py
]
