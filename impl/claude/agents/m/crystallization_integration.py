"""
Crystallization Integration: Wiring D-gent Crystals to M-gent Substrate.

Phase 7 of Memory Architecture - The bridge between:
- CrystallizationEngine (D-gent): Creates StateCrystals from ContextWindows
- SharedSubstrate (M-gent): Manages holographic memory allocations
- CrystalReaper (D-gent): TTL-based crystal lifecycle management

Key Insight: Crystallization IS compaction at the semantic level.
- D-gent crystallizes: ContextWindow → StateCrystal (semantic compression)
- M-gent compacts: MemoryCrystal → MemoryCrystal (resolution compression)

The integration provides:
1. SubstrateCrystallizer: Crystallize allocation patterns to StateCrystal
2. ReaperIntegration: Connect CrystalReaper to substrate allocations
3. CrystallizationEvent: Unified event for I-gent visualization

Categorical insight: Crystallization is a natural transformation
between the semantic functor (D-gent) and the holographic functor (M-gent).

    crystallize: Semantic[T] ⟹ Holographic[T]
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from uuid import uuid4

if TYPE_CHECKING:
    from ..d.context_window import ContextWindow
    from ..d.crystal import (
        CrystallizationEngine,
        CrystalReaper,
        StateCrystal,
        TaskState,
    )
    from .compaction import CompactionEvent, Compactor
    from .substrate import Allocation, SharedSubstrate

T = TypeVar("T")


# =============================================================================
# Crystallization Event
# =============================================================================


@dataclass
class CrystallizationEvent:
    """
    Unified event for crystallization operations.

    Bridges D-gent crystallization with M-gent compaction events
    for I-gent visualization.
    """

    timestamp: datetime
    event_type: str  # "crystallize", "reap", "promote"
    agent_id: str
    crystal_id: str | None = None
    patterns_affected: int = 0
    resolution_before: float = 1.0
    resolution_after: float = 1.0
    duration_ms: float = 0.0
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def resolution_loss(self) -> float:
        """Resolution lost in this event."""
        return self.resolution_before - self.resolution_after


# =============================================================================
# Substrate Crystallizer
# =============================================================================


class SubstrateCrystallizer(Generic[T]):
    """
    Crystallizes substrate allocations to StateCrystals.

    The bridge between:
    - Allocation patterns (M-gent's holographic memory)
    - StateCrystals (D-gent's semantic checkpoints)

    When should_promote() returns True for an allocation, the
    SubstrateCrystallizer can create a StateCrystal checkpoint
    that captures the allocation's semantic state.

    Example:
        crystallizer = SubstrateCrystallizer(engine, substrate)

        # Check if allocation should crystallize
        if manager.should_promote():
            event = await crystallizer.crystallize_allocation(
                allocation=manager._dialogue,
                agent="kgent",
                task_state=current_task,
            )
            print(f"Crystallized to {event.crystal_id}")
    """

    def __init__(
        self,
        engine: "CrystallizationEngine",
        substrate: "SharedSubstrate[T]",
        compactor: "Compactor[T] | None" = None,
    ) -> None:
        """
        Initialize substrate crystallizer.

        Args:
            engine: CrystallizationEngine for creating StateCrystals
            substrate: SharedSubstrate containing allocations
            compactor: Optional Compactor for resolution-aware crystallization
        """
        self._engine = engine
        self._substrate = substrate
        self._compactor = compactor
        self._events: list[CrystallizationEvent] = []

    @property
    def events(self) -> list[CrystallizationEvent]:
        """Crystallization event history."""
        return self._events.copy()

    async def crystallize_allocation(
        self,
        allocation: "Allocation[T]",
        agent: str,
        task_state: "TaskState",
        window: "ContextWindow",
        working_memory: dict[str, Any] | None = None,
        parent_crystal: "StateCrystal | None" = None,
        ttl: timedelta | None = None,
    ) -> CrystallizationEvent:
        """
        Crystallize an allocation to a StateCrystal.

        This bridges the holographic allocation with semantic crystallization:
        1. Captures allocation's pattern stats
        2. Creates StateCrystal via D-gent engine
        3. Optionally triggers compaction on the allocation

        Args:
            allocation: The allocation to crystallize
            agent: Agent identifier
            task_state: Current task state
            window: ContextWindow to crystallize
            working_memory: Optional key-value memory
            parent_crystal: Optional parent for lineage
            ttl: Optional TTL override

        Returns:
            CrystallizationEvent with details
        """
        start = time.time()

        # Capture pre-crystallization state
        patterns_before = allocation.pattern_count
        resolution_before = allocation._crystal.stats().get("avg_resolution", 1.0)

        # Build working memory with allocation metadata
        memory = working_memory or {}
        memory["_allocation"] = {
            "agent_id": str(allocation.agent_id),
            "namespace": allocation.namespace,
            "pattern_count": patterns_before,
            "usage_ratio": allocation.usage_ratio(),
            "crystallized_at": datetime.now().isoformat(),
        }

        # Crystallize via D-gent engine
        result = await self._engine.crystallize(
            window=window,
            task_state=task_state,
            agent=agent,
            working_memory=memory,
            parent_crystal=parent_crystal,
            ttl=ttl,
        )

        duration_ms = (time.time() - start) * 1000

        if result.success and result.crystal:
            crystal_id = result.crystal.crystal_id
            reason = f"Allocation crystallized: {allocation.lifecycle.human_label}"
        else:
            crystal_id = None
            reason = f"Crystallization failed: {result.error}"

        # Create event
        event = CrystallizationEvent(
            timestamp=datetime.now(),
            event_type="crystallize",
            agent_id=str(allocation.agent_id),
            crystal_id=crystal_id,
            patterns_affected=patterns_before,
            resolution_before=resolution_before,
            resolution_after=resolution_before,  # Crystal doesn't affect resolution
            duration_ms=duration_ms,
            reason=reason,
            metadata={
                "preserved_count": result.preserved_count,
                "dropped_count": result.dropped_count,
                "summary_length": result.summary_length,
            },
        )

        self._events.append(event)
        return event

    async def crystallize_on_promotion(
        self,
        allocation: "Allocation[T]",
        agent: str,
        task_state: "TaskState",
        window: "ContextWindow",
    ) -> CrystallizationEvent | None:
        """
        Crystallize if allocation should be promoted.

        Checks the substrate's promotion policy and crystallizes if
        the allocation qualifies for dedicated crystal promotion.

        Args:
            allocation: The allocation to check
            agent: Agent identifier
            task_state: Current task state
            window: ContextWindow to crystallize

        Returns:
            CrystallizationEvent if crystallized, None otherwise
        """
        decision = self._substrate.promotion_policy.should_promote(allocation)

        if not decision.should_promote:
            return None

        return await self.crystallize_allocation(
            allocation=allocation,
            agent=agent,
            task_state=task_state,
            window=window,
            working_memory={"promotion_reason": decision.reason},
        )

    async def crystallize_with_compaction(
        self,
        allocation: "Allocation[T]",
        agent: str,
        task_state: "TaskState",
        window: "ContextWindow",
        compress_ratio: float = 0.8,
    ) -> tuple[CrystallizationEvent, "CompactionEvent | None"]:
        """
        Crystallize and then compact the allocation.

        The sequence:
        1. Crystallize (create semantic checkpoint)
        2. Compact (reduce holographic resolution)

        This is the full "graceful forgetting" cycle:
        - Hot memory → Crystal (semantic compression)
        - Crystal → Reduced resolution (holographic compression)

        Args:
            allocation: The allocation to process
            agent: Agent identifier
            task_state: Current task state
            window: ContextWindow to crystallize
            compress_ratio: Compression ratio for compaction

        Returns:
            Tuple of (CrystallizationEvent, CompactionEvent or None)
        """
        # First crystallize
        crystal_event = await self.crystallize_allocation(
            allocation=allocation,
            agent=agent,
            task_state=task_state,
            window=window,
        )

        # Then compact if compactor available
        compaction_event = None
        if self._compactor is not None:
            compaction_event = await self._compactor.compact(
                crystal=allocation._crystal,
                target_id=str(allocation.agent_id),
                pressure=allocation.usage_ratio(),
                force=True,
            )

        return (crystal_event, compaction_event)

    def stats(self) -> dict[str, Any]:
        """Get crystallizer statistics."""
        if not self._events:
            return {
                "total_crystallizations": 0,
                "successful": 0,
                "failed": 0,
                "avg_duration_ms": 0.0,
            }

        successful = sum(1 for e in self._events if e.crystal_id is not None)
        failed = len(self._events) - successful

        return {
            "total_crystallizations": len(self._events),
            "successful": successful,
            "failed": failed,
            "avg_duration_ms": sum(e.duration_ms for e in self._events)
            / len(self._events),
            "total_patterns_affected": sum(e.patterns_affected for e in self._events),
        }


# =============================================================================
# Reaper Integration
# =============================================================================


class ReaperIntegration(Generic[T]):
    """
    Connects CrystalReaper to substrate allocations.

    The reaper manages TTL-based expiration of:
    - StateCrystals (D-gent semantic checkpoints)
    - Allocations (M-gent memory rooms)

    When the reaper reaps a crystal, this integration:
    1. Removes the corresponding allocation if expired
    2. Emits a reap event for I-gent visualization
    3. Maintains consistency between crystal and allocation lifecycle

    Example:
        reaper_integration = ReaperIntegration(reaper, substrate)

        # Reap expired crystals and allocations
        events = await reaper_integration.reap_all()
        print(f"Reaped {len(events)} expired entries")
    """

    def __init__(
        self,
        reaper: "CrystalReaper",
        substrate: "SharedSubstrate[T]",
    ) -> None:
        """
        Initialize reaper integration.

        Args:
            reaper: CrystalReaper for crystal lifecycle
            substrate: SharedSubstrate for allocation lifecycle
        """
        self._reaper = reaper
        self._substrate = substrate
        self._events: list[CrystallizationEvent] = []

    @property
    def events(self) -> list[CrystallizationEvent]:
        """Reap event history."""
        return self._events.copy()

    async def reap_all(self) -> list[CrystallizationEvent]:
        """
        Reap all expired crystals and corresponding allocations.

        Returns:
            List of reap events
        """
        events: list[CrystallizationEvent] = []

        # First, reap crystals via D-gent reaper
        reap_result = self._reaper.reap()

        for crystal_id in reap_result.crystal_ids:
            event = CrystallizationEvent(
                timestamp=datetime.now(),
                event_type="reap",
                agent_id="unknown",  # Crystal doesn't track agent
                crystal_id=crystal_id,
                reason="TTL expired",
            )
            events.append(event)
            self._events.append(event)

        # Second, check allocations for expired TTL
        expired_allocations = []
        for agent_id, allocation in list(self._substrate.allocations.items()):
            if allocation.lifecycle.is_expired(allocation.created_at):
                expired_allocations.append((agent_id, allocation))

        for agent_id, allocation in expired_allocations:
            event = CrystallizationEvent(
                timestamp=datetime.now(),
                event_type="reap",
                agent_id=str(agent_id),
                patterns_affected=allocation.pattern_count,
                resolution_before=allocation._crystal.stats().get(
                    "avg_resolution", 1.0
                ),
                resolution_after=0.0,  # Reaped = gone
                reason=f"Allocation TTL expired: {allocation.lifecycle.human_label}",
            )
            events.append(event)
            self._events.append(event)

            # Remove from substrate
            del self._substrate.allocations[agent_id]

        return events

    async def reap_allocation(
        self,
        allocation: "Allocation[T]",
        reason: str = "Manual reap",
    ) -> CrystallizationEvent:
        """
        Reap a specific allocation.

        Args:
            allocation: The allocation to reap
            reason: Reason for reaping

        Returns:
            Reap event
        """
        event = CrystallizationEvent(
            timestamp=datetime.now(),
            event_type="reap",
            agent_id=str(allocation.agent_id),
            patterns_affected=allocation.pattern_count,
            resolution_before=allocation._crystal.stats().get("avg_resolution", 1.0),
            resolution_after=0.0,
            reason=reason,
        )
        self._events.append(event)

        # Remove from substrate
        if allocation.agent_id in self._substrate.allocations:
            del self._substrate.allocations[allocation.agent_id]

        return event

    def get_expiring_soon(
        self,
        threshold: timedelta | None = None,
    ) -> list["Allocation[T]"]:
        """
        Get allocations expiring soon.

        Args:
            threshold: Time until expiration to consider "soon" (default 1 hour)

        Returns:
            List of allocations expiring within threshold
        """
        threshold = threshold or timedelta(hours=1)
        expiring: list[Allocation[T]] = []

        for allocation in self._substrate.allocations.values():
            expires_at = allocation.created_at + allocation.lifecycle.ttl
            time_remaining = expires_at - datetime.now()
            if timedelta(0) < time_remaining < threshold:
                expiring.append(allocation)

        return expiring

    def stats(self) -> dict[str, Any]:
        """Get reaper integration statistics."""
        reap_events = [e for e in self._events if e.event_type == "reap"]

        return {
            "total_reaps": len(reap_events),
            "crystals_reaped": sum(1 for e in reap_events if e.crystal_id is not None),
            "allocations_reaped": sum(
                1
                for e in reap_events
                if e.crystal_id is None and e.agent_id != "unknown"
            ),
            "patterns_released": sum(e.patterns_affected for e in reap_events),
            "active_allocations": len(self._substrate.allocations),
        }


# =============================================================================
# K-gent Crystallizer
# =============================================================================


class KgentCrystallizer:
    """
    K-gent specific crystallization manager.

    Integrates with KgentAllocationManager to provide:
    1. Automatic crystallization when dialogue allocation should promote
    2. Dream pattern crystallization during Hypnagogia
    3. Soul state preservation

    Example:
        kgent_crystallizer = KgentCrystallizer(
            crystallizer=substrate_crystallizer,
            allocation_manager=kgent_manager,
        )

        # Crystallize dialogue when promotion conditions met
        event = await kgent_crystallizer.crystallize_dialogue_if_needed(
            window=current_window,
            task_state=current_task,
        )
    """

    def __init__(
        self,
        crystallizer: SubstrateCrystallizer[Any],
        allocation_manager: Any,  # KgentAllocationManager
    ) -> None:
        """
        Initialize K-gent crystallizer.

        Args:
            crystallizer: SubstrateCrystallizer for core operations
            allocation_manager: KgentAllocationManager for allocations
        """
        self._crystallizer = crystallizer
        self._manager = allocation_manager

    async def crystallize_dialogue_if_needed(
        self,
        window: "ContextWindow",
        task_state: "TaskState",
    ) -> CrystallizationEvent | None:
        """
        Crystallize dialogue allocation if promotion conditions met.

        Returns:
            CrystallizationEvent if crystallized, None otherwise
        """
        if not self._manager.should_promote():
            return None

        if self._manager._dialogue is None:
            return None

        return await self._crystallizer.crystallize_allocation(
            allocation=self._manager._dialogue,
            agent="kgent",
            task_state=task_state,
            window=window,
            working_memory={
                "interaction_count": self._manager.interaction_count,
                "promotion_trigger": "dialogue_threshold",
            },
        )

    async def crystallize_dreams(
        self,
        window: "ContextWindow",
        task_state: "TaskState",
    ) -> CrystallizationEvent | None:
        """
        Crystallize dream patterns during Hypnagogia.

        Returns:
            CrystallizationEvent if crystallized, None otherwise
        """
        if self._manager._dream is None:
            return None

        return await self._crystallizer.crystallize_allocation(
            allocation=self._manager._dream,
            agent="kgent",
            task_state=task_state,
            window=window,
            working_memory={
                "consolidation_type": "hypnagogia",
                "dream_patterns": self._manager._dream.pattern_count,
            },
        )

    async def crystallize_soul_state(
        self,
        window: "ContextWindow",
        task_state: "TaskState",
        soul_state: Any,  # SoulState
    ) -> CrystallizationEvent | None:
        """
        Crystallize eigenvector/soul state.

        Creates a checkpoint of K-gent's personality state.

        Returns:
            CrystallizationEvent if crystallized, None otherwise
        """
        if self._manager._eigenvector is None:
            return None

        return await self._crystallizer.crystallize_allocation(
            allocation=self._manager._eigenvector,
            agent="kgent",
            task_state=task_state,
            window=window,
            working_memory={
                "soul_mode": soul_state.active_mode.value if soul_state else "unknown",
                "checkpoint_type": "soul_state",
            },
            ttl=timedelta(days=30),  # Long TTL for soul state
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_substrate_crystallizer(
    engine: "CrystallizationEngine",
    substrate: "SharedSubstrate[Any]",
    compactor: "Compactor[Any] | None" = None,
) -> SubstrateCrystallizer[Any]:
    """
    Factory function to create a SubstrateCrystallizer.

    Args:
        engine: CrystallizationEngine for creating StateCrystals
        substrate: SharedSubstrate containing allocations
        compactor: Optional Compactor for resolution-aware crystallization

    Returns:
        Configured SubstrateCrystallizer
    """
    return SubstrateCrystallizer(
        engine=engine,
        substrate=substrate,
        compactor=compactor,
    )


def create_reaper_integration(
    reaper: "CrystalReaper",
    substrate: "SharedSubstrate[Any]",
) -> ReaperIntegration[Any]:
    """
    Factory function to create a ReaperIntegration.

    Args:
        reaper: CrystalReaper for crystal lifecycle
        substrate: SharedSubstrate for allocation lifecycle

    Returns:
        Configured ReaperIntegration
    """
    return ReaperIntegration(
        reaper=reaper,
        substrate=substrate,
    )


def create_kgent_crystallizer(
    engine: "CrystallizationEngine",
    substrate: "SharedSubstrate[Any]",
    allocation_manager: Any,  # KgentAllocationManager
    compactor: "Compactor[Any] | None" = None,
) -> KgentCrystallizer:
    """
    Factory function to create a KgentCrystallizer.

    Args:
        engine: CrystallizationEngine
        substrate: SharedSubstrate
        allocation_manager: KgentAllocationManager
        compactor: Optional Compactor

    Returns:
        Configured KgentCrystallizer
    """
    crystallizer = create_substrate_crystallizer(engine, substrate, compactor)
    return KgentCrystallizer(
        crystallizer=crystallizer,
        allocation_manager=allocation_manager,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Events
    "CrystallizationEvent",
    # Core integrations
    "SubstrateCrystallizer",
    "ReaperIntegration",
    # K-gent specific
    "KgentCrystallizer",
    # Factory functions
    "create_substrate_crystallizer",
    "create_reaper_integration",
    "create_kgent_crystallizer",
]
