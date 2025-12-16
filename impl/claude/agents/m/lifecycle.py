"""
Lifecycle: Memory State Machine

Manages memory lifecycle transitions and policies.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
Follows spec/m-gents/architecture.md.

State Machine:
    ACTIVE ─────────────────┐
      │                     │
      │ timeout             │ recall
      ▼                     │
    DORMANT ◄───────────────┘
      │
      │ consolidate
      ▼
    DREAMING (reorganization)
      │
      │ forget (low relevance)
      ▼
    COMPOSTING (graceful degradation)

Policy Types:
    - TimeoutPolicy: ACTIVE -> DORMANT after inactivity
    - RelevancePolicy: DORMANT -> COMPOSTING when relevance < threshold
    - ResolutionPolicy: Degrade resolution in COMPOSTING
    - CherishPolicy: Protect cherished memories from lifecycle changes
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from .memory import Lifecycle, Memory


# === Transition Events ===


@dataclass(frozen=True, slots=True)
class LifecycleEvent:
    """
    Event emitted when a memory transitions between lifecycle states.
    """

    memory_id: str
    from_state: Lifecycle
    to_state: Lifecycle
    timestamp: float = field(default_factory=time.time)
    reason: str = ""

    @property
    def is_demotion(self) -> bool:
        """Is this a demotion (toward COMPOSTING)?"""
        order = {
            Lifecycle.ACTIVE: 0,
            Lifecycle.DORMANT: 1,
            Lifecycle.DREAMING: 2,
            Lifecycle.COMPOSTING: 3,
        }
        return order.get(self.to_state, 0) > order.get(self.from_state, 0)

    @property
    def is_promotion(self) -> bool:
        """Is this a promotion (toward ACTIVE)?"""
        return not self.is_demotion and self.from_state != self.to_state


# === Policies ===


@dataclass
class TimeoutPolicy:
    """
    Policy: ACTIVE -> DORMANT after inactivity period.

    Memories that haven't been accessed within the timeout
    are deactivated to save working memory.
    """

    timeout_seconds: float = 300.0  # 5 minutes default

    def should_deactivate(self, memory: Memory, now: float | None = None) -> bool:
        """Check if memory should transition to DORMANT."""
        if memory.lifecycle != Lifecycle.ACTIVE:
            return False

        now = now or time.time()
        inactive_time = now - memory.last_accessed
        return inactive_time > self.timeout_seconds


@dataclass
class RelevancePolicy:
    """
    Policy: Manage relevance decay and demotion.

    Low-relevance memories are demoted during consolidation.
    """

    decay_factor: float = 0.99  # Per-consolidation decay
    demote_threshold: float = 0.2  # Below this, demote to COMPOSTING

    def should_demote(self, memory: Memory) -> bool:
        """Check if memory should be demoted to COMPOSTING."""
        if memory.is_cherished:
            return False

        return memory.relevance < self.demote_threshold

    def apply_decay(self, memory: Memory) -> Memory:
        """Apply relevance decay to a memory."""
        if memory.is_cherished:
            return memory

        return memory.decay(self.decay_factor)


@dataclass
class ResolutionPolicy:
    """
    Policy: Graceful degradation in COMPOSTING state.

    Resolution gradually decreases until minimal (title-only).
    """

    degrade_factor: float = 0.5  # Per-cycle degradation
    minimum_resolution: float = 0.1  # Never degrade below this

    def should_degrade(self, memory: Memory) -> bool:
        """Check if memory should be degraded."""
        if memory.lifecycle != Lifecycle.COMPOSTING:
            return False

        return memory.resolution > self.minimum_resolution

    def apply_degradation(self, memory: Memory) -> Memory:
        """Apply resolution degradation to a memory."""
        if not self.should_degrade(memory):
            return memory

        new_resolution = max(
            self.minimum_resolution,
            memory.resolution * self.degrade_factor,
        )
        return Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=new_resolution,
            lifecycle=memory.lifecycle,
            relevance=memory.relevance,
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )


# === Lifecycle Manager ===


@dataclass
class LifecycleManager:
    """
    Manages memory lifecycle transitions.

    Coordinates policies and emits events on transitions.

    Usage:
        manager = LifecycleManager()

        # Check if memory needs transition
        event = manager.evaluate(memory)
        if event:
            print(f"Memory {event.memory_id}: {event.from_state} -> {event.to_state}")
            memory = manager.apply(memory, event.to_state)
    """

    timeout_policy: TimeoutPolicy = field(default_factory=TimeoutPolicy)
    relevance_policy: RelevancePolicy = field(default_factory=RelevancePolicy)
    resolution_policy: ResolutionPolicy = field(default_factory=ResolutionPolicy)

    # Event listeners
    _listeners: list[Callable[[LifecycleEvent], None]] = field(default_factory=list)

    def add_listener(self, listener: Callable[[LifecycleEvent], None]) -> None:
        """Add a listener for lifecycle events."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Callable[[LifecycleEvent], None]) -> None:
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _emit(self, event: LifecycleEvent) -> None:
        """Emit event to all listeners."""
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass  # Don't let listener errors break the flow

    def evaluate(self, memory: Memory, now: float | None = None) -> LifecycleEvent | None:
        """
        Evaluate if memory should transition states.

        Returns event if transition needed, None otherwise.
        """
        # Check timeout (ACTIVE -> DORMANT)
        if self.timeout_policy.should_deactivate(memory, now):
            return LifecycleEvent(
                memory_id=memory.datum_id,
                from_state=memory.lifecycle,
                to_state=Lifecycle.DORMANT,
                reason="timeout",
            )

        # Check relevance demotion (DORMANT -> COMPOSTING via DREAMING)
        if memory.lifecycle == Lifecycle.DORMANT and self.relevance_policy.should_demote(memory):
            return LifecycleEvent(
                memory_id=memory.datum_id,
                from_state=memory.lifecycle,
                to_state=Lifecycle.COMPOSTING,
                reason="low_relevance",
            )

        return None

    def apply(self, memory: Memory, target_state: Lifecycle) -> Memory:
        """
        Apply a lifecycle transition.

        Returns the updated memory and emits event.
        """
        if memory.lifecycle == target_state:
            return memory

        from_state = memory.lifecycle

        # Apply transition
        match target_state:
            case Lifecycle.ACTIVE:
                new_memory = memory.activate()
            case Lifecycle.DORMANT:
                new_memory = memory.deactivate()
            case Lifecycle.DREAMING:
                new_memory = memory.dream()
            case Lifecycle.COMPOSTING:
                new_memory = memory.compost()
            case _:
                new_memory = memory

        # Emit event
        event = LifecycleEvent(
            memory_id=memory.datum_id,
            from_state=from_state,
            to_state=target_state,
        )
        self._emit(event)

        return new_memory

    def apply_policies(self, memory: Memory) -> Memory:
        """
        Apply all applicable policies to a memory.

        Returns updated memory after all policies applied.
        """
        # Apply relevance decay (during consolidation)
        memory = self.relevance_policy.apply_decay(memory)

        # Apply resolution degradation (for COMPOSTING)
        memory = self.resolution_policy.apply_degradation(memory)

        return memory

    def batch_evaluate(
        self,
        memories: list[Memory],
        now: float | None = None,
    ) -> list[tuple[Memory, LifecycleEvent | None]]:
        """
        Evaluate multiple memories for transitions.

        Returns list of (memory, event) tuples.
        """
        return [(m, self.evaluate(m, now)) for m in memories]


# === Valid Transitions ===

VALID_TRANSITIONS: dict[Lifecycle, set[Lifecycle]] = {
    Lifecycle.ACTIVE: {Lifecycle.DORMANT},
    Lifecycle.DORMANT: {Lifecycle.ACTIVE, Lifecycle.DREAMING, Lifecycle.COMPOSTING},
    Lifecycle.DREAMING: {Lifecycle.DORMANT},
    Lifecycle.COMPOSTING: {Lifecycle.DORMANT},  # Can be resurrected if re-cherished
}


def is_valid_transition(from_state: Lifecycle, to_state: Lifecycle) -> bool:
    """Check if a lifecycle transition is valid."""
    return to_state in VALID_TRANSITIONS.get(from_state, set())
