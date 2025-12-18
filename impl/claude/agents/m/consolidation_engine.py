"""
ConsolidationEngine: Memory Sleep Cycles

The "sleep" cycle for memory reorganization. During consolidation:
1. Low-relevance memories are demoted (DORMANT -> COMPOSTING)
2. Associations are strengthened between related memories
3. Similar memories can be merged (optional)
4. Embeddings can be recomputed with updated context

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

Key Insight:
    Consolidation is when M-gent "sleeps" - memories reorganize,
    weak ones fade, and associations strengthen. This mirrors
    biological memory consolidation during sleep.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Awaitable, Callable

from .lifecycle import (
    LifecycleEvent,
    LifecycleManager,
    RelevancePolicy,
    ResolutionPolicy,
)
from .memory import Lifecycle, Memory
from .protocol import ConsolidationReport

if TYPE_CHECKING:
    from .associative import AssociativeMemory


# === Consolidation Strategies ===


@dataclass
class ConsolidationConfig:
    """
    Configuration for consolidation behavior.

    Attributes:
        relevance_decay: Per-cycle decay factor for relevance (default 0.95)
        demote_threshold: Relevance below which memories are demoted (default 0.2)
        resolution_decay: Per-cycle degradation for COMPOSTING (default 0.5)
        min_resolution: Never degrade below this (default 0.1)
        merge_threshold: Similarity above which memories can merge (default 0.95)
        enable_merging: Whether to merge similar memories (default False)
        strengthen_associations: Whether to strengthen cross-references (default True)
    """

    relevance_decay: float = 0.95
    demote_threshold: float = 0.2
    resolution_decay: float = 0.5
    min_resolution: float = 0.1
    merge_threshold: float = 0.95
    enable_merging: bool = False
    strengthen_associations: bool = True


@dataclass
class ConsolidationStats:
    """
    Statistics from a consolidation cycle.
    """

    total_memories: int
    dreaming_count: int
    demoted_count: int
    merged_count: int
    strengthened_count: int
    degraded_count: int
    duration_ms: float

    @property
    def summary(self) -> str:
        return (
            f"Consolidation: {self.total_memories} memories processed, "
            f"{self.demoted_count} demoted, {self.degraded_count} degraded "
            f"({self.duration_ms:.1f}ms)"
        )


# === Consolidation Engine ===


class ConsolidationEngine:
    """
    Engine for memory consolidation ("sleep" cycles).

    Orchestrates the consolidation process:
    1. Mark DORMANT memories as DREAMING
    2. Apply relevance decay
    3. Demote low-relevance to COMPOSTING
    4. (Optional) Merge similar memories
    5. (Optional) Strengthen associations
    6. Degrade COMPOSTING resolution
    7. Wake DREAMING -> DORMANT

    Usage:
        mgent = AssociativeMemory(dgent)
        engine = ConsolidationEngine(mgent)

        # Run a consolidation cycle
        report = await engine.consolidate()
        print(report.summary)

        # With custom config
        config = ConsolidationConfig(relevance_decay=0.9)
        engine = ConsolidationEngine(mgent, config)
    """

    def __init__(
        self,
        mgent: "AssociativeMemory",
        config: ConsolidationConfig | None = None,
    ) -> None:
        self.mgent = mgent
        self.config = config or ConsolidationConfig()

        # Configure lifecycle manager with our settings
        self.lifecycle_manager = LifecycleManager(
            relevance_policy=RelevancePolicy(
                decay_factor=self.config.relevance_decay,
                demote_threshold=self.config.demote_threshold,
            ),
            resolution_policy=ResolutionPolicy(
                degrade_factor=self.config.resolution_decay,
                minimum_resolution=self.config.min_resolution,
            ),
        )

        # Listeners for consolidation events
        self._listeners: list[Callable[[LifecycleEvent], Awaitable[None] | None]] = []

    def add_listener(self, listener: Callable[[LifecycleEvent], Awaitable[None] | None]) -> None:
        """Add a listener for lifecycle events during consolidation."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[LifecycleEvent], Awaitable[None] | None]) -> None:
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    async def _emit(self, event: LifecycleEvent) -> None:
        """Emit event to listeners."""
        for listener in self._listeners:
            try:
                result = listener(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                pass  # Don't let listener errors break consolidation

    async def consolidate(self) -> ConsolidationReport:
        """
        Run a full consolidation cycle.

        Returns report with statistics on what changed.
        """
        start_time = time.time()
        await self.mgent.count()

        # Phase 1: Mark DORMANT as DREAMING
        dreaming_memories = await self._enter_dreaming()

        # Phase 2: Apply relevance decay and demote
        demoted_count = await self._decay_and_demote()

        # Phase 3: (Optional) Merge similar memories
        merged_count = 0
        if self.config.enable_merging:
            merged_count = await self._merge_similar()

        # Phase 4: (Optional) Strengthen associations
        strengthened_count = 0
        if self.config.strengthen_associations:
            strengthened_count = await self._strengthen_associations()

        # Phase 5: Degrade COMPOSTING resolution
        await self._degrade_composting()

        # Phase 6: Wake DREAMING -> DORMANT
        await self.mgent.wake()

        duration_ms = (time.time() - start_time) * 1000

        return ConsolidationReport(
            dreaming_count=len(dreaming_memories),
            demoted_count=demoted_count,
            merged_count=merged_count,
            strengthened_count=strengthened_count,
            duration_ms=duration_ms,
        )

    async def _enter_dreaming(self) -> list[str]:
        """Mark DORMANT memories as DREAMING."""
        dreaming_ids: list[str] = []

        for memory_id, memory in list(self.mgent._memories.items()):
            if memory.lifecycle == Lifecycle.DORMANT:
                new_memory = memory.dream()
                self.mgent._memories[memory_id] = new_memory
                dreaming_ids.append(memory_id)

                # Emit event
                event = LifecycleEvent(
                    memory_id=memory_id,
                    from_state=Lifecycle.DORMANT,
                    to_state=Lifecycle.DREAMING,
                    reason="consolidation_start",
                )
                await self._emit(event)

        return dreaming_ids

    async def _decay_and_demote(self) -> int:
        """Apply relevance decay and demote low-relevance memories."""
        demoted = 0

        for memory_id, memory in list(self.mgent._memories.items()):
            if memory.lifecycle == Lifecycle.DREAMING:
                # Apply decay (unless cherished)
                if not memory.is_cherished:
                    decayed = memory.decay(self.config.relevance_decay)

                    # Check for demotion
                    if decayed.relevance < self.config.demote_threshold:
                        composted = decayed.compost()
                        self.mgent._memories[memory_id] = composted
                        demoted += 1

                        # Emit event
                        event = LifecycleEvent(
                            memory_id=memory_id,
                            from_state=Lifecycle.DREAMING,
                            to_state=Lifecycle.COMPOSTING,
                            reason="low_relevance",
                        )
                        await self._emit(event)
                    else:
                        self.mgent._memories[memory_id] = decayed

        return demoted

    async def _merge_similar(self) -> int:
        """
        Merge highly similar memories.

        When two memories are > merge_threshold similar:
        - Keep the one with higher access_count
        - Transfer relevance boost to survivor
        - Mark merged memory as COMPOSTING

        Returns count of merged memories.
        """
        merged = 0
        processed: set[str] = set()

        memories = list(self.mgent._memories.items())

        for i, (id_a, mem_a) in enumerate(memories):
            if id_a in processed:
                continue
            if mem_a.lifecycle != Lifecycle.DREAMING:
                continue

            for j, (id_b, mem_b) in enumerate(memories[i + 1 :], i + 1):
                if id_b in processed:
                    continue
                if mem_b.lifecycle != Lifecycle.DREAMING:
                    continue

                similarity = mem_a.similarity(mem_b.embedding)

                if similarity >= self.config.merge_threshold:
                    # Decide which to keep based on access count
                    if mem_a.access_count >= mem_b.access_count:
                        survivor_id, survivor = id_a, mem_a
                        merged_id, merged_mem = id_b, mem_b
                    else:
                        survivor_id, survivor = id_b, mem_b
                        merged_id, merged_mem = id_a, mem_a

                    # Transfer relevance boost
                    boosted = survivor.reinforce(boost=0.05)
                    self.mgent._memories[survivor_id] = boosted

                    # Mark merged as COMPOSTING
                    self.mgent._memories[merged_id] = merged_mem.compost()

                    processed.add(merged_id)
                    merged += 1

                    # Emit merge event
                    event = LifecycleEvent(
                        memory_id=merged_id,
                        from_state=Lifecycle.DREAMING,
                        to_state=Lifecycle.COMPOSTING,
                        reason=f"merged_into_{survivor_id}",
                    )
                    await self._emit(event)

        return merged

    async def _strengthen_associations(self) -> int:
        """
        Strengthen associations between frequently accessed memories.

        Memories with high access counts that were accessed close together
        get mutual relevance boosts.

        Returns count of strengthened associations.
        """
        # Simple implementation: boost relevance of high-access memories
        strengthened = 0
        access_threshold = 3  # Minimum accesses to qualify

        for memory_id, memory in list(self.mgent._memories.items()):
            if memory.lifecycle != Lifecycle.DREAMING:
                continue
            if memory.access_count >= access_threshold and not memory.is_cherished:
                # Small relevance boost for frequently accessed
                boosted = memory.reinforce(boost=0.02)
                self.mgent._memories[memory_id] = boosted
                strengthened += 1

        return strengthened

    async def _degrade_composting(self) -> int:
        """Degrade resolution of COMPOSTING memories."""
        return await self.mgent.degrade_composting(self.config.resolution_decay)


# === Convenience Factory ===


def create_consolidation_engine(
    mgent: "AssociativeMemory",
    aggressive: bool = False,
) -> ConsolidationEngine:
    """
    Create a consolidation engine with sensible defaults.

    Args:
        mgent: The AssociativeMemory to consolidate
        aggressive: If True, use more aggressive decay/demotion

    Returns:
        Configured ConsolidationEngine
    """
    if aggressive:
        config = ConsolidationConfig(
            relevance_decay=0.85,
            demote_threshold=0.3,
            resolution_decay=0.3,
            enable_merging=True,
        )
    else:
        config = ConsolidationConfig()

    return ConsolidationEngine(mgent, config)
