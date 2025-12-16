"""
Legacy stubs for deleted M-gent modules.

DEPRECATED: These are placeholder types for backward compatibility.

The data architecture rewrite simplified M-gent to focus on:
- MgentProtocol for memory operations
- Memory dataclass for semantic memory
- AssociativeMemory for recall
- SoulMemory for K-gent identity

These stubs allow old code to import without errors, but the
implementations are minimal/no-op.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

S = TypeVar("S")
T = TypeVar("T")


@dataclass
class HolographicMemory(Generic[T]):
    """
    DEPRECATED: Old holographic memory abstraction.

    Replaced by AssociativeMemory with embeddings.
    """

    _store: dict[str, T] = field(default_factory=dict, repr=False)

    def store(self, key: str, value: T) -> None:
        self._store[key] = value

    def retrieve(self, key: str) -> T | None:
        return self._store.get(key)


@dataclass
class DgentBackedHolographicMemory(Generic[T]):
    """
    DEPRECATED: Old D-gent backed memory.

    Use AssociativeMemory + D-gent directly.
    """

    namespace: str = "holographic"
    _store: dict[str, T] = field(default_factory=dict, repr=False)

    def store(self, key: str, value: T) -> None:
        self._store[key] = value

    def retrieve(self, key: str) -> T | None:
        return self._store.get(key)


@dataclass
class TieredMemory(Generic[T]):
    """
    DEPRECATED: Old tiered memory.

    Use Memory lifecycle (ACTIVE → DORMANT → COMPOSTING) instead.
    """

    _sensory: dict[str, T] = field(default_factory=dict, repr=False)
    _working: dict[str, T] = field(default_factory=dict, repr=False)
    _long_term: dict[str, T] = field(default_factory=dict, repr=False)

    def perceive(self, key: str, value: T) -> None:
        self._sensory[key] = value

    def attend(self, key: str) -> None:
        if key in self._sensory:
            self._working[key] = self._sensory.pop(key)

    def consolidate(self, key: str) -> None:
        if key in self._working:
            self._long_term[key] = self._working.pop(key)


@dataclass
class BudgetedMemory:
    """
    DEPRECATED: Old budget-constrained memory.

    Use ConsolidationEngine with lifecycle management instead.
    """

    budget: float = 100.0
    _used: float = 0.0
    bank: dict[str, Any] | None = None
    account_id: str = "default"
    _store: dict[str, Any] = field(default_factory=dict, repr=False)

    def can_store(self, size: float) -> bool:
        return self._used + size <= self.budget

    def store_sync(self, key: str, value: Any, size: float) -> bool:
        """Sync store (legacy)."""
        if self.can_store(size):
            self._used += size
            self._store[key] = value
            return True
        return False

    async def store(
        self, id: str, content: Any, concepts: list[str] | None = None
    ) -> dict[str, Any]:
        """Async store with receipt (stub for compatibility)."""
        self._store[id] = {"content": content, "concepts": concepts or []}
        return {"id": id, "cost": 1.0, "success": True}

    def budget_status(self) -> dict[str, Any]:
        """Return budget status (stub for compatibility)."""
        return {
            "budget": self.budget,
            "used": self._used,
            "available": self.budget - self._used,
        }


@dataclass
class ResolutionBudget:
    """
    DEPRECATED: Old resolution budget.

    Use Memory.resolution field instead.
    """

    max_resolution: float = 1.0
    min_resolution: float = 0.1
    max_resolution_budget: float = 1000.0
    cost_model: str = "linear"
    _used: float = 0.0

    def stats(self) -> dict[str, Any]:
        """Return budget stats (stub for compatibility)."""
        return {
            "max": self.max_resolution_budget,
            "used": self._used,
            "available": self.max_resolution_budget - self._used,
        }


@dataclass
class ActionHistory:
    """
    DEPRECATED: Old action history.

    Use TraceMonoid for causal history.
    """

    actions: list[dict[str, Any]] = field(default_factory=list)

    def record(self, action: dict[str, Any]) -> None:
        self.actions.append(action)

    def recent(self, n: int = 10) -> list[dict[str, Any]]:
        return self.actions[-n:]


@dataclass
class Situation:
    """
    DEPRECATED: Old situation model.

    Use Memory with context metadata instead.
    """

    context: dict[str, Any] = field(default_factory=dict)
    entities: list[str] = field(default_factory=list)


@dataclass
class Cue:
    """
    DEPRECATED: Old memory cue.

    Use recall(cue: str) with text query instead.
    """

    text: str = ""
    embedding: list[float] | None = None


@dataclass
class ProspectiveAgent:
    """
    DEPRECATED: Old prospective memory agent.

    Use SoulMemory with seeds instead.
    """

    intentions: list[dict[str, Any]] = field(default_factory=list)

    def intend(self, intention: dict[str, Any]) -> None:
        self.intentions.append(intention)


class AssociativeWebMemory:
    """
    DEPRECATED: Old web-style associative memory.

    Use AssociativeMemory with embeddings.
    """

    def __init__(self) -> None:
        self._links: dict[str, set[str]] = {}

    def link(self, source: str, target: str) -> None:
        if source not in self._links:
            self._links[source] = set()
        self._links[source].add(target)

    def get_links(self, source: str) -> set[str]:
        return self._links.get(source, set())


def create_budgeted_memory(
    budget: float = 100.0,
    bank: dict[str, Any] | None = None,
    account_id: str = "default",
) -> BudgetedMemory:
    """Create a budgeted memory (DEPRECATED)."""
    return BudgetedMemory(budget=budget, bank=bank, account_id=account_id)


def create_mock_bank(max_balance: float = 1000.0) -> dict[str, Any]:
    """Create a mock bank for testing (DEPRECATED)."""
    return {"balance": max_balance, "max_balance": max_balance}


@dataclass
class RecollectionAgent:
    """
    DEPRECATED: Old recollection agent.

    Use AssociativeMemory.recall() instead.
    """

    _memories: dict[str, Any] = field(default_factory=dict, repr=False)

    async def recollect(self, cue: str, limit: int = 5) -> list[Any]:
        """Recollect memories matching the cue."""
        # Simple substring matching
        matches = [
            v for k, v in self._memories.items()
            if cue.lower() in k.lower()
        ]
        return matches[:limit]

    def store(self, key: str, memory: Any) -> None:
        """Store a memory."""
        self._memories[key] = memory
