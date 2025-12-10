"""
CrystalStore: Storage abstraction for SemanticTraces.

Crystals are immutable once stored. The store provides:
- Store: Persist a crystal
- Get: Retrieve by trace_id
- Query: Search by criteria
- Get children: Nested call traces

Implementations:
- MemoryCrystalStore: In-memory (for testing)
- DgentCrystalStore: D-gent backed (for production)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterator

from .types import Determinism, SemanticTrace


class CrystalStore(ABC):
    """
    Abstract storage for crystals.

    Crystals are sacred—once stored, they cannot be modified.
    Only store, query, and (carefully) delete.
    """

    @abstractmethod
    def store(self, crystal: SemanticTrace) -> None:
        """
        Store a crystal.

        The crystal is immutable once stored.
        """
        ...

    @abstractmethod
    def get(self, trace_id: str) -> SemanticTrace | None:
        """
        Retrieve a crystal by ID.

        Returns None if not found.
        """
        ...

    @abstractmethod
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
        Query crystals by criteria.

        All criteria are AND-ed together.
        """
        ...

    @abstractmethod
    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """
        Get child traces (nested calls).

        Returns traces where parent_id == trace_id.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Get total number of crystals stored."""
        ...

    def get_ancestors(self, trace_id: str) -> list[SemanticTrace]:
        """
        Get all ancestor traces.

        Returns traces from parent up to root.
        """
        ancestors = []
        current = self.get(trace_id)
        while current and current.parent_id:
            parent = self.get(current.parent_id)
            if parent:
                ancestors.append(parent)
                current = parent
            else:
                break
        return ancestors

    def get_tree(self, trace_id: str) -> dict[str, Any]:
        """
        Get the full trace tree rooted at trace_id.

        Returns a nested dict with the trace and its children.
        """
        trace = self.get(trace_id)
        if not trace:
            return {}

        children = self.get_children(trace_id)
        return {
            "trace": trace,
            "children": [self.get_tree(c.trace_id) for c in children],
        }

    def iter_all(self) -> Iterator[SemanticTrace]:
        """
        Iterate over all crystals.

        Default implementation uses query with pagination.
        Override for more efficient implementations.
        """
        offset = 0
        limit = 100
        while True:
            batch = self.query(limit=limit, offset=offset)
            if not batch:
                break
            yield from batch
            offset += limit


class MemoryCrystalStore(CrystalStore):
    """
    In-memory crystal store for testing.

    Fast but ephemeral—crystals are lost when process exits.
    """

    def __init__(self):
        self._crystals: dict[str, SemanticTrace] = {}
        # Indices for efficient queries
        self._by_agent: dict[str, list[str]] = {}
        self._by_parent: dict[str, list[str]] = {}
        self._by_action: dict[str, list[str]] = {}

    def store(self, crystal: SemanticTrace) -> None:
        """Store a crystal with indexing."""
        self._crystals[crystal.trace_id] = crystal

        # Update indices
        if crystal.agent_id not in self._by_agent:
            self._by_agent[crystal.agent_id] = []
        self._by_agent[crystal.agent_id].append(crystal.trace_id)

        if crystal.parent_id:
            if crystal.parent_id not in self._by_parent:
                self._by_parent[crystal.parent_id] = []
            self._by_parent[crystal.parent_id].append(crystal.trace_id)

        if crystal.action not in self._by_action:
            self._by_action[crystal.action] = []
        self._by_action[crystal.action].append(crystal.trace_id)

    def get(self, trace_id: str) -> SemanticTrace | None:
        """Retrieve by ID."""
        return self._crystals.get(trace_id)

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
        # Start with all or indexed subset
        if agent_id and agent_id in self._by_agent:
            candidates = [self._crystals[tid] for tid in self._by_agent[agent_id]]
        elif action and action in self._by_action:
            candidates = [self._crystals[tid] for tid in self._by_action[action]]
        else:
            candidates = list(self._crystals.values())

        # Apply filters
        results = []
        for crystal in candidates:
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

        # Sort by timestamp
        results.sort(key=lambda c: c.timestamp)

        # Apply pagination
        return results[offset : offset + limit]

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        """Get child traces."""
        child_ids = self._by_parent.get(trace_id, [])
        children = [self._crystals[tid] for tid in child_ids if tid in self._crystals]
        return sorted(children, key=lambda c: c.timestamp)

    def count(self) -> int:
        """Get count."""
        return len(self._crystals)

    def clear(self) -> None:
        """Clear all crystals (for testing)."""
        self._crystals.clear()
        self._by_agent.clear()
        self._by_parent.clear()
        self._by_action.clear()


@dataclass
class CrystalStats:
    """Statistics about a crystal store."""

    total_crystals: int
    unique_agents: int
    unique_actions: int
    oldest_timestamp: datetime | None
    newest_timestamp: datetime | None
    total_gas: int
    total_duration_ms: int
    error_count: int
    by_determinism: dict[str, int] = field(default_factory=dict)
    by_genus: dict[str, int] = field(default_factory=dict)


def compute_stats(store: CrystalStore) -> CrystalStats:
    """
    Compute statistics for a crystal store.

    Useful for dashboards and debugging.
    """
    crystals = list(store.iter_all())

    if not crystals:
        return CrystalStats(
            total_crystals=0,
            unique_agents=0,
            unique_actions=0,
            oldest_timestamp=None,
            newest_timestamp=None,
            total_gas=0,
            total_duration_ms=0,
            error_count=0,
        )

    agents = set()
    actions = set()
    total_gas = 0
    total_duration = 0
    error_count = 0
    by_determinism: dict[str, int] = {}
    by_genus: dict[str, int] = {}

    oldest = crystals[0].timestamp
    newest = crystals[0].timestamp

    for crystal in crystals:
        agents.add(crystal.agent_id)
        actions.add(crystal.action)
        total_gas += crystal.gas_consumed
        total_duration += crystal.duration_ms

        if crystal.action == "ERROR":
            error_count += 1

        det = crystal.determinism.value
        by_determinism[det] = by_determinism.get(det, 0) + 1

        genus = crystal.agent_genus
        by_genus[genus] = by_genus.get(genus, 0) + 1

        if crystal.timestamp < oldest:
            oldest = crystal.timestamp
        if crystal.timestamp > newest:
            newest = crystal.timestamp

    return CrystalStats(
        total_crystals=len(crystals),
        unique_agents=len(agents),
        unique_actions=len(actions),
        oldest_timestamp=oldest,
        newest_timestamp=newest,
        total_gas=total_gas,
        total_duration_ms=total_duration,
        error_count=error_count,
        by_determinism=by_determinism,
        by_genus=by_genus,
    )
