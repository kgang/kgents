"""
Ghost ↔ Substrate Bidirectional Sync.

Phase 8 of Memory Architecture - The final coherence layer.

The ghost cache and substrate allocation are two views of the same truth.
When one changes, the other must follow:
- Store in allocation → create ghost entry
- Access ghost → touch allocation
- Reap allocation → invalidate ghost entries

Categorical insight: This is a two-way galois connection.
    floor ⊣ ceiling : Ghost ⇆ Substrate
    floor(ghost_entry) = allocation_state
    ceiling(allocation) = ghost_representation

The sync maintains coherence: floor(ceiling(a)) ≅ a (up to serialization)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    from agents.m.crystallization_integration import (
        CrystallizationEvent,
        ReaperIntegration,
    )
    from agents.m.substrate import Allocation, SharedSubstrate
    from infra.ghost.lifecycle import LifecycleAwareCache

T = TypeVar("T")


# =============================================================================
# Sync Event Types
# =============================================================================


@dataclass
class GhostSyncEvent:
    """
    Record of a ghost ↔ substrate sync operation.

    For I-gent visualization and debugging.
    """

    timestamp: datetime
    event_type: str  # "store_to_ghost", "ghost_access", "invalidate"
    agent_id: str
    key: str
    success: bool
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Ghost Sync Manager
# =============================================================================


class GhostSyncManager(Generic[T]):
    """
    Manages bidirectional sync between Ghost cache and Substrate allocations.

    The sync protocol:
    1. On allocation store → create ghost entry (floor)
    2. On ghost access → touch allocation last_accessed (ceiling)
    3. On reap/evict → invalidate ghost entries

    Example:
        ghost_cache = get_lifecycle_cache()
        substrate = create_substrate()
        sync = GhostSyncManager(ghost_cache, substrate)

        # Register allocation for sync
        sync.register_allocation(allocation)

        # Store with sync (creates ghost entry)
        await sync.store_with_sync(allocation, concept_id, content, embedding)

        # Ghost access updates allocation
        sync.on_ghost_access(key)

        # Reap with sync (invalidates ghost)
        await sync.reap_with_sync(allocation)
    """

    def __init__(
        self,
        ghost_cache: "LifecycleAwareCache",
        substrate: "SharedSubstrate[T]",
        key_prefix: str = "alloc",
    ) -> None:
        """
        Initialize ghost sync manager.

        Args:
            ghost_cache: The lifecycle-aware ghost cache
            substrate: The shared substrate
            key_prefix: Prefix for ghost cache keys (default "alloc")
        """
        self._ghost = ghost_cache
        self._substrate = substrate
        self._key_prefix = key_prefix
        self._events: list[GhostSyncEvent] = []

        # Mapping: ghost_key -> allocation agent_id
        self._key_to_agent: dict[str, str] = {}

    @property
    def events(self) -> list[GhostSyncEvent]:
        """Sync event history."""
        return self._events.copy()

    def _make_ghost_key(self, agent_id: str, concept_id: str) -> str:
        """Create ghost cache key from agent and concept IDs."""
        return f"{self._key_prefix}:{agent_id}:{concept_id}"

    def _parse_ghost_key(self, key: str) -> tuple[str, str] | None:
        """Parse ghost key back to (agent_id, concept_id)."""
        parts = key.split(":")
        if len(parts) >= 3 and parts[0] == self._key_prefix:
            agent_id = parts[1]
            concept_id = ":".join(parts[2:])  # Handle concept_ids with colons
            return (agent_id, concept_id)
        return None

    def register_allocation(self, allocation: "Allocation[T]") -> None:
        """
        Register an allocation for ghost sync.

        This enables the sync manager to track which ghost entries
        belong to which allocations.
        """
        # Build mapping for existing patterns
        # (In practice, patterns would be registered as they're stored)
        pass

    async def store_with_sync(
        self,
        allocation: "Allocation[T]",
        concept_id: str,
        content: T,
        embedding: list[float],
    ) -> bool:
        """
        Store pattern in allocation AND create ghost entry.

        This is the "floor" operation: allocation → ghost

        Args:
            allocation: The allocation to store in
            concept_id: Concept identifier
            content: Pattern content
            embedding: Vector embedding

        Returns:
            True if both allocation store and ghost write succeeded
        """
        # Store in allocation
        success = await allocation.store(concept_id, content, embedding)

        if success:
            # Create ghost entry
            ghost_key = self._make_ghost_key(str(allocation.agent_id), concept_id)
            human_label = (
                f"Pattern {concept_id} from {allocation.lifecycle.human_label}"
            )

            try:
                self._ghost.write(
                    key=ghost_key,
                    data={
                        "concept_id": concept_id,
                        "agent_id": str(allocation.agent_id),
                        "content_type": type(content).__name__,
                        "stored_at": datetime.now().isoformat(),
                        # Don't store actual content in ghost (too large)
                        # Ghost is for metadata/existence checking
                    },
                    human_label=human_label,
                    ttl=allocation.lifecycle.ttl,
                    metadata={
                        "namespace": allocation.namespace,
                        "sync_source": "allocation_store",
                    },
                )

                # Record mapping
                self._key_to_agent[ghost_key] = str(allocation.agent_id)

                # Record event
                self._events.append(
                    GhostSyncEvent(
                        timestamp=datetime.now(),
                        event_type="store_to_ghost",
                        agent_id=str(allocation.agent_id),
                        key=ghost_key,
                        success=True,
                        reason="Allocation store → Ghost write",
                    )
                )
            except Exception as e:
                # Ghost write failed, but allocation store succeeded
                self._events.append(
                    GhostSyncEvent(
                        timestamp=datetime.now(),
                        event_type="store_to_ghost",
                        agent_id=str(allocation.agent_id),
                        key=ghost_key,
                        success=False,
                        reason=f"Ghost write failed: {e}",
                    )
                )

        return success

    def on_ghost_access(self, key: str) -> bool:
        """
        Handle ghost cache access by touching the corresponding allocation.

        This is the "ceiling" operation: ghost → allocation

        Args:
            key: The ghost cache key that was accessed

        Returns:
            True if allocation was found and touched
        """
        parsed = self._parse_ghost_key(key)
        if parsed is None:
            return False

        agent_id, concept_id = parsed

        # Find allocation
        from agents.m.substrate import AgentId

        allocation = self._substrate.get_allocation(AgentId(agent_id))
        if allocation is None:
            return False

        # Touch allocation (record access)
        allocation._record_access()

        # Record event
        self._events.append(
            GhostSyncEvent(
                timestamp=datetime.now(),
                event_type="ghost_access",
                agent_id=agent_id,
                key=key,
                success=True,
                reason="Ghost access → Allocation touch",
            )
        )

        return True

    async def invalidate_for_allocation(
        self,
        allocation: "Allocation[T]",
        reason: str = "Allocation invalidation",
    ) -> int:
        """
        Invalidate all ghost entries for an allocation.

        Called when an allocation is reaped or evicted.

        Args:
            allocation: The allocation being invalidated
            reason: Reason for invalidation

        Returns:
            Number of ghost entries invalidated
        """
        agent_id = str(allocation.agent_id)
        prefix = f"{self._key_prefix}:{agent_id}:"
        invalidated = 0

        # Find all ghost entries for this allocation
        keys_to_delete = [
            key for key in self._ghost.all_keys() if key.startswith(prefix)
        ]

        for key in keys_to_delete:
            try:
                self._ghost.delete(key, reason=reason)
                invalidated += 1

                # Clean up mapping
                if key in self._key_to_agent:
                    del self._key_to_agent[key]

            except Exception:
                pass  # Best effort

        # Record event
        if invalidated > 0:
            self._events.append(
                GhostSyncEvent(
                    timestamp=datetime.now(),
                    event_type="invalidate",
                    agent_id=agent_id,
                    key=prefix + "*",
                    success=True,
                    reason=f"{reason}: {invalidated} entries",
                    metadata={"count": invalidated},
                )
            )

        return invalidated

    async def reap_with_sync(
        self,
        allocation: "Allocation[T]",
        reason: str = "TTL expired",
    ) -> int:
        """
        Reap an allocation and invalidate its ghost entries.

        This is the full eviction flow:
        1. Invalidate ghost entries
        2. Remove allocation from substrate

        Args:
            allocation: The allocation to reap
            reason: Reason for reaping

        Returns:
            Number of ghost entries invalidated
        """
        # First invalidate ghost entries
        invalidated = await self.invalidate_for_allocation(allocation, reason)

        # Then remove from substrate (caller is responsible for this typically)
        # We don't do it here to avoid coupling

        return invalidated

    def stats(self) -> dict[str, Any]:
        """Get sync manager statistics."""
        events_by_type: dict[str, int] = {}
        for e in self._events:
            events_by_type[e.event_type] = events_by_type.get(e.event_type, 0) + 1

        return {
            "total_events": len(self._events),
            "events_by_type": events_by_type,
            "tracked_keys": len(self._key_to_agent),
            "ghost_entries": len(self._ghost.all_keys()),
        }


# =============================================================================
# Enhanced Allocation with Ghost Sync
# =============================================================================


class GhostSyncAllocation(Generic[T]):
    """
    Wrapper that adds ghost sync to an allocation.

    Usage:
        allocation = substrate.allocate(...)
        synced = GhostSyncAllocation(allocation, sync_manager)
        await synced.store(concept_id, content, embedding)  # Also syncs to ghost
    """

    def __init__(
        self,
        allocation: "Allocation[T]",
        sync_manager: GhostSyncManager[T],
    ) -> None:
        """
        Initialize ghost sync allocation wrapper.

        Args:
            allocation: The underlying allocation
            sync_manager: The ghost sync manager
        """
        self._allocation = allocation
        self._sync = sync_manager

    @property
    def allocation(self) -> "Allocation[T]":
        """Get the underlying allocation."""
        return self._allocation

    async def store(
        self,
        concept_id: str,
        content: T,
        embedding: list[float],
    ) -> bool:
        """Store with automatic ghost sync."""
        return await self._sync.store_with_sync(
            self._allocation, concept_id, content, embedding
        )

    async def retrieve(
        self,
        cue: list[float],
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[Any]:
        """Retrieve from allocation (no sync needed for reads)."""
        return await self._allocation.retrieve(cue, threshold, limit)

    def __getattr__(self, name: str) -> Any:
        """Delegate to underlying allocation."""
        return getattr(self._allocation, name)


# =============================================================================
# Reaper Integration with Ghost Sync
# =============================================================================


class GhostAwareReaperIntegration(Generic[T]):
    """
    ReaperIntegration enhanced with ghost cache invalidation.

    When reaping:
    1. Reap crystals via CrystalReaper
    2. Reap allocations via TTL check
    3. Invalidate ghost entries for reaped allocations

    Example:
        reaper = CrystalReaper()
        substrate = create_substrate()
        ghost_cache = get_lifecycle_cache()

        ghost_reaper = GhostAwareReaperIntegration(
            reaper=reaper,
            substrate=substrate,
            ghost_cache=ghost_cache,
        )

        events = await ghost_reaper.reap_all()
    """

    def __init__(
        self,
        reaper: Any,  # CrystalReaper
        substrate: "SharedSubstrate[T]",
        ghost_cache: "LifecycleAwareCache",
    ) -> None:
        """
        Initialize ghost-aware reaper integration.

        Args:
            reaper: CrystalReaper for crystal lifecycle
            substrate: SharedSubstrate for allocation lifecycle
            ghost_cache: Ghost cache for invalidation
        """
        # Import here to avoid circular imports
        from agents.m.crystallization_integration import ReaperIntegration

        self._base_reaper = ReaperIntegration(reaper=reaper, substrate=substrate)
        self._ghost_sync = GhostSyncManager(ghost_cache, substrate)

    @property
    def events(self) -> list["CrystallizationEvent"]:
        """Combined event history from base reaper."""
        return self._base_reaper.events

    @property
    def sync_events(self) -> list[GhostSyncEvent]:
        """Ghost sync event history."""
        return self._ghost_sync.events

    async def reap_all(self) -> list["CrystallizationEvent"]:
        """
        Reap all expired crystals and allocations with ghost sync.

        Returns:
            List of crystallization events
        """
        # Get allocations before reaping (for ghost invalidation)
        from agents.m.crystallization_integration import (
            CrystallizationEvent,
        )

        expired_allocations = []
        for allocation in list(self._base_reaper._substrate.allocations.values()):
            if allocation.lifecycle.is_expired(allocation.created_at):
                expired_allocations.append(allocation)

        # Reap via base reaper
        events = await self._base_reaper.reap_all()

        # Invalidate ghost entries for reaped allocations
        for allocation in expired_allocations:
            await self._ghost_sync.invalidate_for_allocation(
                allocation, reason="TTL expired"
            )

        return events

    async def reap_allocation(
        self,
        allocation: "Allocation[T]",
        reason: str = "Manual reap",
    ) -> "CrystallizationEvent":
        """
        Reap a specific allocation with ghost sync.

        Args:
            allocation: The allocation to reap
            reason: Reason for reaping

        Returns:
            Reap event
        """
        # Invalidate ghost first
        await self._ghost_sync.invalidate_for_allocation(allocation, reason)

        # Then reap via base
        return await self._base_reaper.reap_allocation(allocation, reason)

    def get_expiring_soon(
        self,
        threshold: timedelta | None = None,
    ) -> list["Allocation[T]"]:
        """Get allocations expiring soon."""
        return self._base_reaper.get_expiring_soon(threshold)

    def stats(self) -> dict[str, Any]:
        """Get combined statistics."""
        base_stats = self._base_reaper.stats()
        sync_stats = self._ghost_sync.stats()

        return {
            **base_stats,
            "ghost_sync": sync_stats,
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_ghost_sync_manager(
    ghost_cache: "LifecycleAwareCache",
    substrate: "SharedSubstrate[Any]",
    key_prefix: str = "alloc",
) -> GhostSyncManager[Any]:
    """
    Factory function to create a GhostSyncManager.

    Args:
        ghost_cache: The lifecycle-aware ghost cache
        substrate: The shared substrate
        key_prefix: Prefix for ghost cache keys

    Returns:
        Configured GhostSyncManager
    """
    return GhostSyncManager(ghost_cache, substrate, key_prefix)


def create_ghost_aware_reaper(
    reaper: Any,  # CrystalReaper
    substrate: "SharedSubstrate[Any]",
    ghost_cache: "LifecycleAwareCache",
) -> GhostAwareReaperIntegration[Any]:
    """
    Factory function to create a GhostAwareReaperIntegration.

    Args:
        reaper: CrystalReaper for crystal lifecycle
        substrate: SharedSubstrate for allocation lifecycle
        ghost_cache: Ghost cache for invalidation

    Returns:
        Configured GhostAwareReaperIntegration
    """
    return GhostAwareReaperIntegration(reaper, substrate, ghost_cache)


def wrap_with_ghost_sync(
    allocation: "Allocation[Any]",
    sync_manager: GhostSyncManager[Any],
) -> GhostSyncAllocation[Any]:
    """
    Wrap an allocation with ghost sync.

    Args:
        allocation: The allocation to wrap
        sync_manager: The ghost sync manager

    Returns:
        GhostSyncAllocation wrapper
    """
    return GhostSyncAllocation(allocation, sync_manager)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Events
    "GhostSyncEvent",
    # Core sync
    "GhostSyncManager",
    "GhostSyncAllocation",
    # Reaper integration
    "GhostAwareReaperIntegration",
    # Factory functions
    "create_ghost_sync_manager",
    "create_ghost_aware_reaper",
    "wrap_with_ghost_sync",
]
