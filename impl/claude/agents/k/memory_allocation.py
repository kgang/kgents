"""
K-gent Memory Allocation: Soul Substrate Integration.

K-gent's memory profile is unique among agents:
- Working memory: Session-scoped, high churn
- Eigenvector cache: Long-term, stable patterns
- Dialogue history: Promotion candidate (hot → dedicated crystal)
- Dream patterns: Consolidated during Hypnagogia

This module integrates K-gent with the SharedSubstrate from M-gent,
providing:
1. Allocation with K-gent specific lifecycle
2. Automatic promotion based on dialogue intensity
3. Semantic routing for soul-related concepts
4. Compaction strategy for dream consolidation

Categorical insight: K-gent's memory allocation is a morphism
Soul → MemorySpace that preserves eigenvector structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..m.stigmergy import PheromoneField
    from ..m.substrate import Allocation, SharedSubstrate
    from .eigenvectors import KentEigenvectors
    from .soul import SoulState


# =============================================================================
# K-gent Memory Profile
# =============================================================================


@dataclass
class KgentMemoryProfile:
    """
    K-gent's memory configuration.

    Defines the memory characteristics specific to K-gent:
    - Working memory for active dialogue
    - Eigenvector cache for personality stability
    - Pattern store for learned behaviors
    """

    # Working memory (session-scoped)
    working_memory_ttl: timedelta = field(default_factory=lambda: timedelta(hours=4))
    working_memory_max_patterns: int = 500

    # Eigenvector cache (long-term, stable)
    eigenvector_ttl: timedelta = field(default_factory=lambda: timedelta(days=30))
    eigenvector_max_patterns: int = 50  # Eigenvectors are compact

    # Dialogue history (promotion candidate)
    dialogue_ttl: timedelta = field(default_factory=lambda: timedelta(days=7))
    dialogue_max_patterns: int = 1000
    dialogue_promotion_threshold: int = 100  # Interactions before promotion

    # Dream patterns (consolidated)
    dream_ttl: timedelta = field(default_factory=lambda: timedelta(days=14))
    dream_max_patterns: int = 200

    def total_max_patterns(self) -> int:
        """Total pattern capacity across all tiers."""
        return (
            self.working_memory_max_patterns
            + self.eigenvector_max_patterns
            + self.dialogue_max_patterns
            + self.dream_max_patterns
        )


# =============================================================================
# K-gent Allocation Manager
# =============================================================================


@dataclass
class AllocationStats:
    """Statistics for K-gent's memory allocation."""

    working_memory_used: int = 0
    eigenvector_used: int = 0
    dialogue_used: int = 0
    dream_used: int = 0
    total_used: int = 0
    total_capacity: int = 0
    usage_ratio: float = 0.0
    promotion_eligible: bool = False
    last_access: Optional[datetime] = None


class KgentAllocationManager:
    """
    Manages K-gent's memory allocation in the SharedSubstrate.

    This class provides:
    1. Multi-tier allocation (working, eigenvector, dialogue, dream)
    2. Automatic promotion based on usage patterns
    3. Compaction during Hypnagogia
    4. Integration with soul state

    Example:
        substrate = create_substrate()
        manager = KgentAllocationManager(substrate, profile=KgentMemoryProfile())

        # Initialize allocations
        await manager.initialize()

        # Store working memory
        await manager.store_working("current_context", context_data, embedding)

        # Store eigenvector state
        await manager.store_eigenvector("aesthetic", eigenvector_value, embedding)

        # Check if dialogue should be promoted
        if manager.should_promote():
            await manager.promote_dialogue()
    """

    def __init__(
        self,
        substrate: "SharedSubstrate[Any]",
        profile: Optional[KgentMemoryProfile] = None,
        agent_id: str = "kgent",
    ) -> None:
        """
        Initialize K-gent allocation manager.

        Args:
            substrate: The shared substrate
            profile: K-gent memory profile
            agent_id: K-gent's agent ID prefix
        """
        self._substrate = substrate
        self._profile = profile or KgentMemoryProfile()
        self._agent_id = agent_id

        # Allocation references (set during initialize)
        self._working: Optional["Allocation[Any]"] = None
        self._eigenvector: Optional["Allocation[Any]"] = None
        self._dialogue: Optional["Allocation[Any]"] = None
        self._dream: Optional["Allocation[Any]"] = None

        # Tracking
        self._initialized = False
        self._interaction_count = 0

    @property
    def is_initialized(self) -> bool:
        """Check if allocations are initialized."""
        return self._initialized

    @property
    def interaction_count(self) -> int:
        """Number of interactions since initialization."""
        return self._interaction_count

    async def initialize(self) -> None:
        """
        Initialize K-gent's memory allocations.

        Creates four allocations in the substrate:
        1. Working memory (session-scoped)
        2. Eigenvector cache (long-term)
        3. Dialogue history (promotion candidate)
        4. Dream patterns (consolidated)
        """
        from ..m.substrate import LifecyclePolicy, MemoryQuota

        # Working memory allocation
        self._working = self._substrate.allocate(
            agent_id=f"{self._agent_id}:working",
            quota=MemoryQuota(max_patterns=self._profile.working_memory_max_patterns),
            lifecycle=LifecyclePolicy(
                human_label="K-gent working memory (session)",
                ttl=self._profile.working_memory_ttl,
            ),
        )

        # Eigenvector cache allocation
        self._eigenvector = self._substrate.allocate(
            agent_id=f"{self._agent_id}:eigenvector",
            quota=MemoryQuota(max_patterns=self._profile.eigenvector_max_patterns),
            lifecycle=LifecyclePolicy(
                human_label="K-gent eigenvector cache (stable)",
                ttl=self._profile.eigenvector_ttl,
            ),
        )

        # Dialogue history allocation
        self._dialogue = self._substrate.allocate(
            agent_id=f"{self._agent_id}:dialogue",
            quota=MemoryQuota(max_patterns=self._profile.dialogue_max_patterns),
            lifecycle=LifecyclePolicy(
                human_label="K-gent dialogue history",
                ttl=self._profile.dialogue_ttl,
            ),
        )

        # Dream patterns allocation
        self._dream = self._substrate.allocate(
            agent_id=f"{self._agent_id}:dream",
            quota=MemoryQuota(max_patterns=self._profile.dream_max_patterns),
            lifecycle=LifecyclePolicy(
                human_label="K-gent dream patterns (consolidated)",
                ttl=self._profile.dream_ttl,
            ),
        )

        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Ensure allocations are initialized."""
        if not self._initialized:
            raise RuntimeError(
                "KgentAllocationManager not initialized. Call initialize() first."
            )

    # -------------------------------------------------------------------------
    # Working Memory
    # -------------------------------------------------------------------------

    async def store_working(
        self,
        concept_id: str,
        content: Any,
        embedding: list[float],
    ) -> bool:
        """
        Store pattern in working memory.

        Args:
            concept_id: Unique concept identifier
            content: Pattern content
            embedding: Vector embedding

        Returns:
            True if stored, False if quota exceeded
        """
        self._ensure_initialized()
        assert self._working is not None
        return await self._working.store(concept_id, content, embedding)

    async def retrieve_working(
        self,
        cue: list[float],
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[Any]:
        """Retrieve from working memory by resonance."""
        self._ensure_initialized()
        assert self._working is not None
        return await self._working.retrieve(cue, threshold, limit)

    # -------------------------------------------------------------------------
    # Eigenvector Cache
    # -------------------------------------------------------------------------

    async def store_eigenvector(
        self,
        dimension: str,
        value: float,
        embedding: list[float],
    ) -> bool:
        """
        Store eigenvector dimension value.

        Args:
            dimension: Eigenvector dimension name (aesthetic, heterarchic, etc.)
            value: Dimension value (-1 to 1)
            embedding: Vector embedding of the eigenvector state

        Returns:
            True if stored, False if quota exceeded
        """
        self._ensure_initialized()
        assert self._eigenvector is not None

        content = {
            "dimension": dimension,
            "value": value,
            "stored_at": datetime.now().isoformat(),
        }
        return await self._eigenvector.store(
            f"eigenvector:{dimension}", content, embedding
        )

    async def cache_soul_state(
        self,
        soul_state: "SoulState",
        embedding: list[float],
    ) -> bool:
        """
        Cache the full soul state.

        Args:
            soul_state: Current soul state
            embedding: Vector embedding of the state

        Returns:
            True if cached successfully
        """
        self._ensure_initialized()
        assert self._eigenvector is not None

        content = {
            "mode": soul_state.active_mode.value,
            "interactions": soul_state.interactions_count,
            "cached_at": datetime.now().isoformat(),
        }
        return await self._eigenvector.store("soul:state", content, embedding)

    # -------------------------------------------------------------------------
    # Dialogue History
    # -------------------------------------------------------------------------

    async def store_dialogue(
        self,
        turn_id: str,
        message: str,
        response: str,
        mode: str,
        embedding: list[float],
    ) -> bool:
        """
        Store a dialogue turn.

        Args:
            turn_id: Unique turn identifier
            message: User message
            response: K-gent response
            mode: Dialogue mode
            embedding: Vector embedding of the turn

        Returns:
            True if stored, False if quota exceeded
        """
        self._ensure_initialized()
        assert self._dialogue is not None

        content = {
            "message": message,
            "response": response,
            "mode": mode,
            "turn_at": datetime.now().isoformat(),
        }
        success = await self._dialogue.store(f"turn:{turn_id}", content, embedding)

        if success:
            self._interaction_count += 1

        return success

    async def retrieve_dialogue(
        self,
        cue: list[float],
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[Any]:
        """Retrieve dialogue history by resonance."""
        self._ensure_initialized()
        assert self._dialogue is not None
        return await self._dialogue.retrieve(cue, threshold, limit)

    # -------------------------------------------------------------------------
    # Dream Patterns
    # -------------------------------------------------------------------------

    async def store_dream(
        self,
        pattern_id: str,
        content: Any,
        embedding: list[float],
    ) -> bool:
        """
        Store a consolidated dream pattern.

        Args:
            pattern_id: Pattern identifier
            content: Pattern content
            embedding: Vector embedding

        Returns:
            True if stored, False if quota exceeded
        """
        self._ensure_initialized()
        assert self._dream is not None
        return await self._dream.store(f"dream:{pattern_id}", content, embedding)

    async def retrieve_dreams(
        self,
        cue: list[float],
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[Any]:
        """Retrieve dream patterns by resonance."""
        self._ensure_initialized()
        assert self._dream is not None
        return await self._dream.retrieve(cue, threshold, limit)

    # -------------------------------------------------------------------------
    # Promotion & Compaction
    # -------------------------------------------------------------------------

    def should_promote(self) -> bool:
        """
        Check if dialogue allocation should be promoted to dedicated crystal.

        Promotion happens when:
        1. Interaction count exceeds threshold
        2. Dialogue allocation is at soft limit
        """
        self._ensure_initialized()
        assert self._dialogue is not None

        if self._interaction_count >= self._profile.dialogue_promotion_threshold:
            return True

        if self._dialogue.is_at_soft_limit():
            return True

        return False

    async def promote_dialogue(self) -> bool:
        """
        Promote dialogue allocation to dedicated crystal.

        Returns:
            True if promoted, False if already promoted or ineligible
        """
        self._ensure_initialized()
        assert self._dialogue is not None

        # Check eligibility
        decision = self._substrate.promotion_policy.should_promote(self._dialogue)
        if not decision.should_promote:
            return False

        try:
            self._substrate.promote(f"{self._agent_id}:dialogue")
            return True
        except ValueError:
            # Already promoted
            return False

    async def compact_dreams(self, ratio: float = 0.8) -> int:
        """
        Compact dream patterns during Hypnagogia.

        This implements the Accursed Share principle: purposeful forgetting.

        Args:
            ratio: Compression ratio (0.8 = 20% resolution loss)

        Returns:
            Number of patterns affected
        """
        self._ensure_initialized()
        assert self._dream is not None

        return await self._substrate.compact(self._dream)

    async def crystallize(
        self,
        tier: str = "dialogue",
    ) -> dict[str, Any]:
        """
        Trigger crystallization for a specific tier.

        This creates a semantic checkpoint (StateCrystal) of the tier's
        allocation state. Requires external wiring to CrystallizationEngine.

        Args:
            tier: Which tier to crystallize (working, eigenvector, dialogue, dream)

        Returns:
            Dict with crystallization info (requires KgentCrystallizer wiring)

        Note:
            For full crystallization, use KgentCrystallizer which provides
            the integration with D-gent's CrystallizationEngine.
        """
        self._ensure_initialized()

        tier_map = {
            "working": self._working,
            "eigenvector": self._eigenvector,
            "dialogue": self._dialogue,
            "dream": self._dream,
        }

        allocation = tier_map.get(tier)
        if allocation is None:
            return {"error": f"Unknown tier: {tier}"}

        # Return allocation state for external crystallization
        return {
            "tier": tier,
            "agent_id": str(allocation.agent_id),
            "pattern_count": allocation.pattern_count,
            "usage_ratio": allocation.usage_ratio(),
            "human_label": allocation.lifecycle.human_label,
            "avg_resolution": allocation._crystal.stats().get("avg_resolution", 1.0),
            "ready_for_crystallization": True,
            "note": "Use KgentCrystallizer for full crystallization with CrystallizationEngine",
        }

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    def stats(self) -> AllocationStats:
        """Get K-gent allocation statistics."""
        self._ensure_initialized()
        assert self._working is not None
        assert self._eigenvector is not None
        assert self._dialogue is not None
        assert self._dream is not None

        working_used = self._working.pattern_count
        eigenvector_used = self._eigenvector.pattern_count
        dialogue_used = self._dialogue.pattern_count
        dream_used = self._dream.pattern_count

        total_used = working_used + eigenvector_used + dialogue_used + dream_used
        total_capacity = self._profile.total_max_patterns()

        return AllocationStats(
            working_memory_used=working_used,
            eigenvector_used=eigenvector_used,
            dialogue_used=dialogue_used,
            dream_used=dream_used,
            total_used=total_used,
            total_capacity=total_capacity,
            usage_ratio=total_used / total_capacity if total_capacity > 0 else 0.0,
            promotion_eligible=self.should_promote(),
            last_access=max(
                filter(
                    None,
                    [
                        self._working.last_accessed,
                        self._eigenvector.last_accessed,
                        self._dialogue.last_accessed,
                        self._dream.last_accessed,
                    ],
                ),
                default=None,
            ),
        )


# =============================================================================
# Pheromone Integration
# =============================================================================


class KgentPheromoneDepositor:
    """
    Deposits pheromones for K-gent's activity.

    K-gent leaves traces for:
    - Dialogue modes (reflect, advise, challenge, explore)
    - Eigenvector dimensions
    - Emotional states
    - Pattern matches

    This enables other agents to sense K-gent's activity
    and route soul-related tasks appropriately.
    """

    def __init__(
        self,
        field: "PheromoneField",
        agent_id: str = "kgent",
    ) -> None:
        """
        Initialize K-gent pheromone depositor.

        Args:
            field: The pheromone field
            agent_id: K-gent's agent ID
        """
        self._field = field
        self._agent_id = agent_id

    async def deposit_dialogue(
        self,
        mode: str,
        intensity: float = 1.0,
    ) -> None:
        """
        Deposit trace for dialogue activity.

        Args:
            mode: Dialogue mode (reflect, advise, challenge, explore)
            intensity: Trace intensity
        """
        await self._field.deposit(
            concept=f"soul.dialogue.{mode}",
            intensity=intensity,
            depositor=self._agent_id,
            metadata={"mode": mode},
        )

    async def deposit_eigenvector(
        self,
        dimension: str,
        value: float,
    ) -> None:
        """
        Deposit trace for eigenvector state.

        Args:
            dimension: Eigenvector dimension
            value: Dimension value
        """
        # Intensity proportional to absolute value
        intensity = abs(value)
        await self._field.deposit(
            concept=f"soul.eigenvector.{dimension}",
            intensity=intensity,
            depositor=self._agent_id,
            metadata={"dimension": dimension, "value": value},
        )

    async def deposit_pattern(
        self,
        pattern_type: str,
        pattern_id: str,
        intensity: float = 1.0,
    ) -> None:
        """
        Deposit trace for pattern recognition.

        Args:
            pattern_type: Type of pattern (behavior, thought, feeling)
            pattern_id: Pattern identifier
            intensity: Trace intensity
        """
        await self._field.deposit(
            concept=f"soul.pattern.{pattern_type}",
            intensity=intensity,
            depositor=self._agent_id,
            metadata={"pattern_type": pattern_type, "pattern_id": pattern_id},
        )

    async def deposit_emotional_state(
        self,
        state: str,
        intensity: float = 1.0,
    ) -> None:
        """
        Deposit trace for emotional state.

        Args:
            state: Emotional state (curious, grateful, challenged, etc.)
            intensity: Trace intensity
        """
        await self._field.deposit(
            concept=f"soul.emotion.{state}",
            intensity=intensity,
            depositor=self._agent_id,
            metadata={"state": state},
        )


# =============================================================================
# Factory Functions
# =============================================================================


async def create_kgent_allocation(
    substrate: "SharedSubstrate[Any]",
    profile: Optional[KgentMemoryProfile] = None,
) -> KgentAllocationManager:
    """
    Factory function to create and initialize K-gent allocation.

    Args:
        substrate: The shared substrate
        profile: Optional memory profile

    Returns:
        Initialized KgentAllocationManager
    """
    manager = KgentAllocationManager(substrate, profile)
    await manager.initialize()
    return manager


def create_kgent_depositor(
    field: "PheromoneField",
) -> KgentPheromoneDepositor:
    """
    Factory function to create K-gent pheromone depositor.

    Args:
        field: The pheromone field

    Returns:
        KgentPheromoneDepositor
    """
    return KgentPheromoneDepositor(field)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Profile
    "KgentMemoryProfile",
    # Manager
    "KgentAllocationManager",
    "AllocationStats",
    # Pheromone Integration
    "KgentPheromoneDepositor",
    # Factory Functions
    "create_kgent_allocation",
    "create_kgent_depositor",
]
