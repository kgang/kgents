"""
DgentCrystalStore: D-gent backed crystal storage.

NOTE: This module is currently a stub implementation using SimpleDgentCrystalStore.
The UnifiedMemory API from D-gents does not match the synchronous interface
required by CrystalStore, so a full implementation would require async/await
throughout the N-gent stack or an adapter layer.

For production use, consider:
1. Using SimpleDgentCrystalStore with a PersistentAgent backend
2. Implementing an async CrystalStore protocol
3. Creating a sync wrapper around UnifiedMemory
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .store import CrystalStore
from .types import Determinism, SemanticTrace

if TYPE_CHECKING:
    from ..d import UnifiedMemory


class DgentCrystalStore(CrystalStore):
    """
    Crystal store backed by D-gent UnifiedMemory.

    NOTE: This is currently a placeholder that delegates to SimpleDgentCrystalStore.
    A full implementation requires resolving the async/sync impedance mismatch.

    For now, use SimpleDgentCrystalStore directly or MemoryCrystalStore for testing.
    """

    def __init__(
        self,
        memory: UnifiedMemory[dict[str, Any]],
        collection: str = "crystals",
    ):
        """
        Initialize the D-gent backed store.

        Args:
            memory: UnifiedMemory instance from D-gent (currently unused)
            collection: Collection name for crystal storage
        """
        self.memory = memory
        self.collection = collection
        # Use simple implementation as fallback
        self._simple_store = SimpleDgentCrystalStore()

    def store(self, crystal: SemanticTrace) -> None:
        """Store a crystal (delegates to simple store)."""
        self._simple_store.store(crystal)

    def get(self, trace_id: str) -> SemanticTrace | None:
        """Retrieve a crystal by ID (delegates to simple store)."""
        return self._simple_store.get(trace_id)

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        action: str | None = None,
        determinism: Determinism | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SemanticTrace]:
        """Query crystals (delegates to simple store)."""
        return self._simple_store.query(
            agent_id=agent_id,
            agent_genus=agent_genus,
            action=action,
            determinism=determinism,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """Get child traces (delegates to simple store)."""
        return self._simple_store.get_children(trace_id)

    def count(self) -> int:
        """Count crystals (delegates to simple store)."""
        return self._simple_store.count()


class SimpleDgentCrystalStore(CrystalStore):
    """
    Simplified D-gent store using basic DataAgent.

    For when full UnifiedMemory is not needed.
    Uses a simple VolatileAgent or PersistentAgent.
    """

    def __init__(self, storage: dict[str, Any] | None = None):
        """
        Initialize with optional external storage dict.

        Args:
            storage: Optional dict to use as storage (for testing)
        """
        self._storage = storage if storage is not None else {}
        self._by_parent: dict[str, list[str]] = {}

    def store(self, crystal: SemanticTrace) -> None:
        """Store a crystal."""
        self._storage[crystal.trace_id] = crystal.to_dict()

        # Index parent relationship
        if crystal.parent_id:
            if crystal.parent_id not in self._by_parent:
                self._by_parent[crystal.parent_id] = []
            self._by_parent[crystal.parent_id].append(crystal.trace_id)

    def get(self, trace_id: str) -> SemanticTrace | None:
        """Retrieve by ID."""
        data = self._storage.get(trace_id)
        if data is None:
            return None
        return SemanticTrace.from_dict(data)

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        action: str | None = None,
        determinism: Determinism | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SemanticTrace]:
        """Query with filtering."""
        results = []

        for data in self._storage.values():
            crystal = SemanticTrace.from_dict(data)

            if agent_id and crystal.agent_id != agent_id:
                continue
            if agent_genus and crystal.agent_genus != agent_genus:
                continue
            if action and crystal.action != action:
                continue
            if determinism and crystal.determinism != determinism:
                continue
            if start_time and crystal.timestamp < start_time:
                continue
            if end_time and crystal.timestamp > end_time:
                continue

            results.append(crystal)

        results.sort(key=lambda c: c.timestamp)
        return results[offset : offset + limit]

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """Get child traces."""
        child_ids = self._by_parent.get(trace_id, [])
        children = []
        for cid in child_ids:
            crystal = self.get(cid)
            if crystal:
                children.append(crystal)
        return sorted(children, key=lambda c: c.timestamp)

    def count(self) -> int:
        """Get count."""
        return len(self._storage)
