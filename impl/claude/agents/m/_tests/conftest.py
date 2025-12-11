"""
M-gent test fixtures: Holographic Associative Memory.

Shared fixtures for M-gent test suites:
- HolographicMemory: Core memory system
- TieredMemory: Three-tier hierarchy
- MockUnifiedMemory: D-gent mock storage
- BudgetedMemory: B-gent integration
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytest
from agents.m.consolidation import ConsolidationAgent, ForgettingCurveAgent
from agents.m.holographic import HolographicMemory, MemoryPattern
from agents.m.recollection import RecollectionAgent
from agents.m.tiered import TieredMemory

# ========== Core Memory Fixtures ==========


@pytest.fixture
def holographic_memory() -> HolographicMemory[str]:
    """Create a fresh HolographicMemory for testing."""
    return HolographicMemory[str]()


@pytest.fixture
def tiered_memory() -> TieredMemory[str]:
    """Create a fresh TieredMemory for testing."""
    return TieredMemory[str]()


@pytest.fixture
def sample_pattern() -> MemoryPattern[str]:
    """Create a sample memory pattern for testing."""
    return MemoryPattern(
        id="test-pattern",
        content="Test content",
        embedding=[0.0] * 64,
        concepts=["test", "sample"],
        strength=1.0,
    )


@pytest.fixture
def hot_pattern() -> MemoryPattern[str]:
    """Create a frequently accessed (hot) pattern."""
    pattern = MemoryPattern(
        id="hot-pattern",
        content="Hot content",
        embedding=[0.0] * 64,
        access_count=100,
        strength=5.0,
    )
    return pattern


@pytest.fixture
def cold_pattern() -> MemoryPattern[str]:
    """Create a rarely accessed (cold) pattern."""
    pattern = MemoryPattern(
        id="cold-pattern",
        content="Cold content",
        embedding=[0.0] * 64,
        access_count=1,
        strength=0.5,
    )
    # Make it old
    pattern.last_accessed = datetime.now() - timedelta(hours=24)
    return pattern


# ========== Agent Fixtures ==========


@pytest.fixture
def recollection_agent(
    holographic_memory: HolographicMemory[str],
) -> RecollectionAgent[str]:
    """Create a RecollectionAgent with HolographicMemory."""
    return RecollectionAgent(holographic_memory)


@pytest.fixture
def consolidation_agent(
    holographic_memory: HolographicMemory[str],
) -> ConsolidationAgent[str]:
    """Create a ConsolidationAgent with HolographicMemory."""
    return ConsolidationAgent(holographic_memory)


@pytest.fixture
def forgetting_curve_agent(
    holographic_memory: HolographicMemory[str],
) -> ForgettingCurveAgent[str]:
    """Create a ForgettingCurveAgent with HolographicMemory."""
    return ForgettingCurveAgent(holographic_memory)


# ========== Mock D-gent Storage ==========


class MockUnifiedMemory:
    """Mock D-gent UnifiedMemory for testing M-gent integrations."""

    def __init__(self) -> None:
        self._concepts: dict[str, list[str]] = {}
        self._events: list[tuple[datetime, str, dict[str, Any]]] = []
        self._relationships: dict[str, list[tuple[str, str]]] = {}
        self._current_state: dict[str, Any] = {}

    async def save(self, state: dict[str, Any]) -> str:
        self._current_state = state
        return f"entry-{len(self._events)}"

    async def load(self) -> dict[str, Any]:
        return self._current_state

    async def associate(self, state: dict[str, Any], concept: str) -> None:
        if concept not in self._concepts:
            self._concepts[concept] = []
        entry_id = state.get("id", "unknown")
        if entry_id not in self._concepts[concept]:
            self._concepts[concept].append(entry_id)

    async def recall(self, concept: str, limit: int = 5) -> list[tuple[str, float]]:
        results = []
        for stored_concept, entry_ids in self._concepts.items():
            if concept.lower() in stored_concept.lower():
                for entry_id in entry_ids[:limit]:
                    results.append((entry_id, 0.8))
        return results[:limit]

    async def witness(self, event_label: str, state: dict[str, Any]) -> None:
        self._events.append((datetime.now(), event_label, state))

    async def replay(self, timestamp: datetime) -> dict[str, Any] | None:
        for ts, _, state in reversed(self._events):
            if ts <= timestamp:
                return state
        return None

    async def timeline(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[tuple[datetime, str, dict[str, Any]]]:
        return self._events[:limit] if limit else self._events

    async def events_by_label(
        self, label: str, limit: int = 10
    ) -> list[tuple[datetime, dict[str, Any]]]:
        results = [(ts, state) for ts, l, state in self._events if l == label]
        return results[:limit]

    async def relate(self, source: str, relation: str, target: str) -> None:
        if source not in self._relationships:
            self._relationships[source] = []
        self._relationships[source].append((relation, target))

    async def related_to(
        self, entity_id: str, relation: str | None = None
    ) -> list[tuple[str, str]]:
        rels = self._relationships.get(entity_id, [])
        if relation:
            rels = [(r, t) for r, t in rels if r == relation]
        return rels

    async def related_from(
        self, entity_id: str, relation: str | None = None
    ) -> list[tuple[str, str]]:
        results = []
        for source, rels in self._relationships.items():
            for rel, target in rels:
                if target == entity_id and (relation is None or rel == relation):
                    results.append((rel, source))
        return results

    async def trace(self, start: str, max_depth: int = 3) -> dict[str, Any]:
        visited: set[str] = set()
        edges: list[dict[str, str]] = []

        def dfs(node: str, depth: int) -> None:
            if depth > max_depth or node in visited:
                return
            visited.add(node)
            for rel, target in self._relationships.get(node, []):
                edges.append({"source": node, "relation": rel, "target": target})
                dfs(target, depth + 1)

        dfs(start, 0)
        return {"nodes": list(visited), "edges": edges, "depth": max_depth}

    def stats(self) -> dict[str, int]:
        return {
            "concept_count": len(self._concepts),
            "event_count": len(self._events),
            "relationship_count": sum(len(r) for r in self._relationships.values()),
        }


@pytest.fixture
def mock_unified_memory() -> MockUnifiedMemory:
    """Create a mock D-gent UnifiedMemory for testing."""
    return MockUnifiedMemory()


# ========== B-gent Integration Fixtures ==========


@pytest.fixture
def mock_bank() -> Any:
    """Create a mock B-gent bank for testing."""
    from agents.m.memory_budget import create_mock_bank

    return create_mock_bank(max_balance=100000)


@pytest.fixture
def budgeted_memory(holographic_memory: HolographicMemory[str], mock_bank: Any) -> Any:
    """Create a BudgetedMemory with mock bank."""
    from agents.m.memory_budget import BudgetedMemory

    return BudgetedMemory(
        memory=holographic_memory,
        bank=mock_bank,
        account_id="test",
    )


# ========== D-gent Backend Fixtures ==========


@pytest.fixture
def dgent_backed_memory(mock_unified_memory: MockUnifiedMemory) -> Any:
    """Create a D-gent backed HolographicMemory."""
    from agents.m.dgent_backend import DgentBackedHolographicMemory

    return DgentBackedHolographicMemory(
        storage=mock_unified_memory,
        namespace="test",
    )


@pytest.fixture
def persistent_tiered_memory(mock_unified_memory: MockUnifiedMemory) -> Any:
    """Create a PersistentTieredMemory with mock D-gent storage."""
    from agents.m.persistent_tiered import PersistentTieredMemory

    return PersistentTieredMemory(longterm_storage=mock_unified_memory)


# ========== Phase 3: Prospective/Ethical Fixtures ==========


@pytest.fixture
def action_history() -> Any:
    """Create an ActionHistory for testing prospective memory."""
    from agents.m.prospective import ActionHistory

    return ActionHistory()


@pytest.fixture
def ethical_geometry() -> Any:
    """Create an EthicalGeometry for testing."""
    from agents.m.prospective import EthicalGeometry

    return EthicalGeometry()


@pytest.fixture
def prospective_agent(
    holographic_memory: HolographicMemory[str], action_history: Any
) -> Any:
    """Create a ProspectiveAgent for testing."""
    from agents.m.prospective import ProspectiveAgent

    return ProspectiveAgent(holographic_memory, action_history)


@pytest.fixture
def ethical_agent(ethical_geometry: Any) -> Any:
    """Create an EthicalGeometryAgent for testing."""
    from agents.m.prospective import EthicalGeometryAgent

    return EthicalGeometryAgent(ethical_geometry)


# ========== Phase 4: Vector Memory Fixtures ==========


@pytest.fixture
def vector_memory() -> Any:
    """Create a VectorHolographicMemory for testing."""
    from agents.m.vector_holographic import create_simple_vector_memory

    return create_simple_vector_memory(dimension=64)
