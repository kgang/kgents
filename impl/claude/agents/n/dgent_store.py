"""
DgentCrystalStore: D-gent backed crystal storage.

Persists crystals using D-gent's UnifiedMemory, providing:
- Semantic layer: Associate/recall crystals by content
- Temporal layer: Time-travel through crystal history
- Relational layer: Navigate parent/child relationships

This is the production-grade crystal store.
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

    Provides persistent, queryable crystal storage with:
    - Semantic search via the semantic layer
    - Time-travel via the temporal layer
    - Relationship navigation via the relational layer

    Usage:
        from agents.d import create_unified_memory

        memory = create_unified_memory(MemoryConfig(
            enable_semantic=True,
            enable_temporal=True,
            enable_relational=True,
        ))
        store = DgentCrystalStore(memory)
    """

    def __init__(
        self,
        memory: UnifiedMemory,
        collection: str = "crystals",
    ):
        """
        Initialize the D-gent backed store.

        Args:
            memory: UnifiedMemory instance from D-gent
            collection: Collection name for crystal storage
        """
        self.memory = memory
        self.collection = collection

    def store(self, crystal: SemanticTrace) -> None:
        """
        Store a crystal in UnifiedMemory.

        Uses all three layers:
        - Semantic: For content-based retrieval
        - Temporal: For time-based navigation
        - Relational: For parent-child relationships
        """
        # Serialize crystal (excluding input_snapshot for semantic storage)
        data = crystal.to_dict()

        # Store in semantic layer with action as key
        key = f"{self.collection}:{crystal.trace_id}"
        self.memory.associate(key, data)

        # Record temporal event
        self.memory.temporal_event(
            event_type="crystal_stored",
            data={
                "trace_id": crystal.trace_id,
                "agent_id": crystal.agent_id,
                "action": crystal.action,
                "timestamp": crystal.timestamp.isoformat(),
            },
        )

        # Create relational edges
        if crystal.parent_id:
            self.memory.add_edge(
                from_id=crystal.parent_id,
                to_id=crystal.trace_id,
                edge_type="parent_child",
            )

        # Edge to agent
        agent_key = f"agent:{crystal.agent_id}"
        self.memory.add_edge(
            from_id=agent_key,
            to_id=crystal.trace_id,
            edge_type="agent_trace",
        )

    def get(self, trace_id: str) -> SemanticTrace | None:
        """Retrieve a crystal by ID."""
        key = f"{self.collection}:{trace_id}"
        data = self.memory.recall(key)

        if data is None:
            return None

        if isinstance(data, dict):
            return SemanticTrace.from_dict(data)

        return None

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
        """
        Query crystals using UnifiedMemory.

        Combines relational queries for agent_id with
        temporal filtering for time ranges.
        """
        results = []

        # If agent_id specified, use relational query
        if agent_id:
            agent_key = f"agent:{agent_id}"
            related = self.memory.query_edges(
                from_id=agent_key,
                edge_type="agent_trace",
            )

            for edge in related:
                crystal = self.get(edge.to_id)
                if crystal:
                    results.append(crystal)
        else:
            # Otherwise, scan temporal events
            events = self.memory.temporal_query(
                event_type="crystal_stored",
                start_time=start_time,
                end_time=end_time,
                limit=limit * 2,  # Over-fetch for filtering
            )

            for event in events:
                trace_id = event.data.get("trace_id")
                if trace_id:
                    crystal = self.get(trace_id)
                    if crystal:
                        results.append(crystal)

        # Apply filters
        filtered = []
        for crystal in results:
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
            filtered.append(crystal)

        # Sort by timestamp
        filtered.sort(key=lambda c: c.timestamp)

        # Apply pagination
        return filtered[offset : offset + limit]

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """Get child traces via relational layer."""
        edges = self.memory.query_edges(
            from_id=trace_id,
            edge_type="parent_child",
        )

        children = []
        for edge in edges:
            crystal = self.get(edge.to_id)
            if crystal:
                children.append(crystal)

        return sorted(children, key=lambda c: c.timestamp)

    def count(self) -> int:
        """Count crystals via temporal layer."""
        events = self.memory.temporal_query(
            event_type="crystal_stored",
            limit=10000,  # Reasonable upper bound
        )
        return len(events)

    def search_semantic(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SemanticTrace]:
        """
        Search crystals by semantic similarity.

        Uses D-gent's semantic layer for embedding-based search.
        """
        results = self.memory.semantic_search(
            query=query,
            limit=limit,
        )

        crystals = []
        for result in results:
            if result.key.startswith(f"{self.collection}:"):
                trace_id = result.key[len(f"{self.collection}:") :]
                crystal = self.get(trace_id)
                if crystal:
                    crystals.append(crystal)

        return crystals

    def replay_from(
        self,
        start_time: datetime,
        end_time: datetime | None = None,
    ) -> list[SemanticTrace]:
        """
        Replay crystals from a time range.

        Uses D-gent's temporal layer for time-travel.
        """
        events = self.memory.temporal_query(
            event_type="crystal_stored",
            start_time=start_time,
            end_time=end_time,
        )

        crystals = []
        for event in events:
            trace_id = event.data.get("trace_id")
            if trace_id:
                crystal = self.get(trace_id)
                if crystal:
                    crystals.append(crystal)

        return sorted(crystals, key=lambda c: c.timestamp)


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
