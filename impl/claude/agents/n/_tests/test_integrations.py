"""
Tests for N-gent Phase 5: Integrations (D/L/M/I/B-gent).

Tests:
- IndexedCrystalStore: L-gent semantic indexing
- ResonantCrystalStore: M-gent holographic memory
- VisualizableBard: I-gent visualization support
- BudgetedBard: B-gent token budgeting
- NarrativeOrchestrator: Unified integration layer
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from ..bard import NarrativeGenre, NarrativeRequest, Verbosity
from ..integrations import (
    BudgetedBard,
    CrystalMemoryPattern,
    IndexedCrystalStore,
    InsufficientBudgetError,
    NarrationCost,
    NarrativeOrchestrator,
    NarrativeVisualization,
    ResonantCrystalStore,
    VisualizableBard,
)
from ..store import MemoryCrystalStore
from ..types import Determinism, SemanticTrace

# =============================================================================
# Fixtures
# =============================================================================


def make_trace(
    trace_id: str = "trace-1",
    agent_id: str = "TestAgent",
    action: str = "INVOKE",
    timestamp: datetime | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    vector: tuple[float, ...] | None = None,
    parent_id: str | None = None,
) -> SemanticTrace:
    """Create a test trace."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=timestamp or datetime.now(timezone.utc),
        agent_id=agent_id,
        agent_genus="T",
        action=action,
        inputs=inputs or {"prompt": "test"},
        outputs=outputs or {"result": "success"},
        input_hash="abc123",
        input_snapshot=b'{"prompt": "test"}',
        output_hash="def456",
        gas_consumed=100,
        duration_ms=50,
        vector=vector,
        determinism=Determinism.PROBABILISTIC,
    )


def make_trace_sequence(count: int = 5) -> list[SemanticTrace]:
    """Create a sequence of traces."""
    base_time = datetime.now(timezone.utc)
    traces = []
    for i in range(count):
        traces.append(
            make_trace(
                trace_id=f"trace-{i}",
                agent_id=f"Agent{i % 2}",
                timestamp=base_time + timedelta(seconds=i),
            )
        )
    return traces


class MockEmbedder:
    """Mock embedder for testing."""

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension
        self.call_count = 0

    async def embed(self, text: str) -> list[float]:
        """Generate deterministic embedding based on text."""
        self.call_count += 1
        # Create deterministic embedding based on text hash
        h = hash(text) % 10000
        return [float(i + h) / 10000.0 for i in range(self.dimension)]


class MockVectorIndex:
    """Mock vector index for testing."""

    def __init__(self) -> None:
        self._embeddings: dict[str, tuple[list[float], dict[str, Any]]] = {}

    async def add(
        self, id: str, embedding: list[float], metadata: dict[str, Any] | None = None
    ) -> None:
        """Add embedding."""
        self._embeddings[id] = (embedding, metadata or {})

    async def search(
        self, query: list[float], limit: int = 10
    ) -> list[tuple[str, float]]:
        """Search for similar embeddings."""
        # Simple cosine similarity
        results: list[tuple[str, float]] = []
        for id, (emb, _) in self._embeddings.items():
            similarity = self._cosine_similarity(query, emb)
            results.append((id, similarity))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    async def delete(self, id: str) -> None:
        """Delete embedding."""
        if id in self._embeddings:
            del self._embeddings[id]

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot: float = sum(x * y for x, y in zip(a, b))
        norm_a: float = sum(x * x for x in a) ** 0.5
        norm_b: float = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))


class MockHolographicMemory:
    """Mock holographic memory for testing."""

    def __init__(self) -> None:
        self._patterns: list[Any] = []

    async def store(self, pattern: Any) -> None:
        """Store pattern."""
        self._patterns.append(pattern)

    async def resonate(self, query: Any, threshold: float = 0.5) -> list[Any]:
        """Find resonating patterns."""
        # Return all patterns above threshold
        return self._patterns[:10]


class MockTokenBudget:
    """Mock token budget for testing."""

    def __init__(self, max_balance: int = 10000, initial: int = 5000) -> None:
        self._max = max_balance
        self._balance = initial

    def can_afford(self, tokens: int) -> bool:
        """Check if can afford."""
        return self._balance >= tokens

    def consume(self, tokens: int) -> bool:
        """Consume tokens."""
        if self._balance >= tokens:
            self._balance -= tokens
            return True
        return False

    @property
    def available(self) -> int:
        """Get available tokens."""
        return self._balance


# =============================================================================
# CrystalMemoryPattern Tests
# =============================================================================


class TestCrystalMemoryPattern:
    """Tests for CrystalMemoryPattern."""

    def test_from_crystal(self) -> None:
        """Test creating pattern from crystal."""
        trace = make_trace(vector=(0.1, 0.2, 0.3))
        pattern = CrystalMemoryPattern.from_crystal(trace)

        assert pattern.trace_id == trace.trace_id
        assert pattern.agent_id == trace.agent_id
        assert pattern.action == trace.action
        assert pattern.vector == [0.1, 0.2, 0.3]

    def test_from_crystal_with_custom_vector(self) -> None:
        """Test creating pattern with custom vector."""
        trace = make_trace()
        custom_vector = [1.0, 2.0, 3.0]
        pattern = CrystalMemoryPattern.from_crystal(trace, custom_vector)

        assert pattern.vector == custom_vector

    def test_to_dict(self) -> None:
        """Test serialization."""
        trace = make_trace()
        pattern = CrystalMemoryPattern.from_crystal(trace, [0.1, 0.2])

        data = pattern.to_dict()

        assert "trace_id" in data
        assert "agent_id" in data
        assert "vector" in data
        assert data["vector"] == [0.1, 0.2]


# =============================================================================
# IndexedCrystalStore Tests
# =============================================================================


class TestIndexedCrystalStore:
    """Tests for IndexedCrystalStore."""

    def test_store(self) -> None:
        """Test storing a crystal."""
        base = MemoryCrystalStore()
        embedder = MockEmbedder()
        index = MockVectorIndex()

        store = IndexedCrystalStore(base, embedder, index)
        trace = make_trace()

        store.store(trace)

        assert base.count() == 1

    @pytest.mark.asyncio
    async def test_store_and_index(self) -> None:
        """Test storing and indexing a crystal."""
        base = MemoryCrystalStore()
        embedder = MockEmbedder()
        index = MockVectorIndex()

        store = IndexedCrystalStore(base, embedder, index)
        trace = make_trace()

        await store.store_and_index(trace)

        assert base.count() == 1
        assert len(index._embeddings) == 1
        assert embedder.call_count == 1

    @pytest.mark.asyncio
    async def test_search_semantic(self) -> None:
        """Test semantic search."""
        base = MemoryCrystalStore()
        embedder = MockEmbedder()
        index = MockVectorIndex()

        store = IndexedCrystalStore(base, embedder, index)

        # Add multiple traces
        traces = make_trace_sequence(5)
        for trace in traces:
            await store.store_and_index(trace)

        # Search
        results = await store.search_semantic("test query", limit=3)

        assert len(results) <= 3
        assert all(isinstance(r[0], SemanticTrace) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    def test_get(self) -> None:
        """Test getting a crystal."""
        base = MemoryCrystalStore()
        store = IndexedCrystalStore(base, MockEmbedder(), MockVectorIndex())

        trace = make_trace("t-1")
        store.store(trace)

        result = store.get("t-1")
        assert result is not None
        assert result.trace_id == "t-1"

    def test_query(self) -> None:
        """Test querying crystals."""
        base = MemoryCrystalStore()
        store = IndexedCrystalStore(base, MockEmbedder(), MockVectorIndex())

        traces = make_trace_sequence(5)
        for trace in traces:
            store.store(trace)

        results = store.query(agent_id="Agent0")
        assert all(t.agent_id == "Agent0" for t in results)

    def test_count(self) -> None:
        """Test counting crystals."""
        base = MemoryCrystalStore()
        store = IndexedCrystalStore(base, MockEmbedder(), MockVectorIndex())

        traces = make_trace_sequence(3)
        for trace in traces:
            store.store(trace)

        assert store.count() == 3


# =============================================================================
# ResonantCrystalStore Tests
# =============================================================================


class TestResonantCrystalStore:
    """Tests for ResonantCrystalStore."""

    @pytest.mark.asyncio
    async def test_store(self) -> None:
        """Test storing a crystal creates memory pattern."""
        base = MemoryCrystalStore()
        memory = MockHolographicMemory()
        embedder = MockEmbedder()

        store = ResonantCrystalStore(base, memory, embedder)
        trace = make_trace()

        await store.store(trace)

        assert base.count() == 1
        assert len(memory._patterns) == 1

    @pytest.mark.asyncio
    async def test_resonate_query(self) -> None:
        """Test resonance query."""
        base = MemoryCrystalStore()
        memory = MockHolographicMemory()
        embedder = MockEmbedder()

        store = ResonantCrystalStore(base, memory, embedder)

        # Add traces
        for trace in make_trace_sequence(3):
            await store.store(trace)

        # Query
        results = await store.resonate_query("test query")

        assert len(results) <= 10

    def test_get(self) -> None:
        """Test getting a crystal."""
        base = MemoryCrystalStore()
        memory = MockHolographicMemory()

        store = ResonantCrystalStore(base, memory)
        base.store(make_trace("t-1"))

        result = store.get("t-1")
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_pattern(self) -> None:
        """Test getting the memory pattern for a crystal."""
        base = MemoryCrystalStore()
        memory = MockHolographicMemory()
        embedder = MockEmbedder()

        store = ResonantCrystalStore(base, memory, embedder)
        trace = make_trace("t-1")

        await store.store(trace)

        pattern = store.get_pattern("t-1")
        assert pattern is not None
        assert pattern.trace_id == "t-1"


# =============================================================================
# VisualizableBard Tests
# =============================================================================


class TestVisualizableBard:
    """Tests for VisualizableBard."""

    @pytest.mark.asyncio
    async def test_invoke_with_viz(self) -> None:
        """Test generating narrative with visualization."""
        bard = VisualizableBard()
        traces = make_trace_sequence(5)
        request = NarrativeRequest(traces=traces, genre=NarrativeGenre.TECHNICAL)

        result = await bard.invoke_with_viz(request)

        assert isinstance(result, NarrativeVisualization)
        assert result.narrative is not None
        assert len(result.timeline_events) == 5

    @pytest.mark.asyncio
    async def test_timeline_data(self) -> None:
        """Test timeline visualization data."""
        bard = VisualizableBard()
        traces = make_trace_sequence(3)
        request = NarrativeRequest(traces=traces)

        result = await bard.invoke_with_viz(request)
        timeline = result.to_timeline_data()

        assert len(timeline) == 3
        assert all("timestamp" in event for event in timeline)
        assert all("agent" in event for event in timeline)

    @pytest.mark.asyncio
    async def test_swimlane_data(self) -> None:
        """Test swimlane visualization data."""
        bard = VisualizableBard()
        traces = make_trace_sequence(5)
        request = NarrativeRequest(traces=traces)

        result = await bard.invoke_with_viz(request)
        swimlanes = result.to_swimlane_data()

        assert "agents" in swimlanes
        assert "lanes" in swimlanes
        assert len(swimlanes["agents"]) == 2  # Agent0 and Agent1

    @pytest.mark.asyncio
    async def test_graph_data(self) -> None:
        """Test graph visualization data."""
        bard = VisualizableBard()
        # Create traces with parent-child relationships
        base_time = datetime.now(timezone.utc)
        traces = [
            make_trace("p-1", "ParentAgent", timestamp=base_time),
            make_trace(
                "c-1",
                "ChildAgent",
                parent_id="p-1",
                timestamp=base_time + timedelta(seconds=1),
            ),
        ]
        request = NarrativeRequest(traces=traces)

        result = await bard.invoke_with_viz(request)
        graph = result.to_graph_data()

        assert "nodes" in graph
        assert "edges" in graph

    @pytest.mark.asyncio
    async def test_summary_stats(self) -> None:
        """Test summary statistics."""
        bard = VisualizableBard()
        traces = make_trace_sequence(5)
        request = NarrativeRequest(traces=traces)

        result = await bard.invoke_with_viz(request)

        assert result.summary_stats["total_traces"] == 5
        assert result.summary_stats["unique_agents"] == 2
        assert result.summary_stats["total_gas"] == 500


# =============================================================================
# BudgetedBard Tests
# =============================================================================


class TestBudgetedBard:
    """Tests for BudgetedBard."""

    def test_estimate_cost(self) -> None:
        """Test cost estimation."""
        bard = BudgetedBard()
        traces = make_trace_sequence(5)
        request = NarrativeRequest(traces=traces)

        cost = bard.estimate_cost(request)

        assert isinstance(cost, NarrationCost)
        assert cost.estimated_input_tokens > 0
        assert cost.estimated_output_tokens > 0
        assert (
            cost.total_estimated
            == cost.estimated_input_tokens + cost.estimated_output_tokens
        )

    def test_estimate_cost_verbosity(self) -> None:
        """Test cost varies with verbosity."""
        bard = BudgetedBard()
        traces = make_trace_sequence(5)

        terse_request = NarrativeRequest(traces=traces, verbosity=Verbosity.TERSE)
        verbose_request = NarrativeRequest(traces=traces, verbosity=Verbosity.VERBOSE)

        terse_cost = bard.estimate_cost(terse_request)
        verbose_cost = bard.estimate_cost(verbose_request)

        assert terse_cost.estimated_output_tokens < verbose_cost.estimated_output_tokens

    @pytest.mark.asyncio
    async def test_invoke_with_budget(self) -> None:
        """Test invoking with sufficient budget."""
        budget = MockTokenBudget(max_balance=10000, initial=10000)
        bard = BudgetedBard(budget=budget)
        traces = make_trace_sequence(3)
        request = NarrativeRequest(traces=traces)

        narrative = await bard.invoke(request)

        assert narrative is not None
        assert "budget" in narrative.metadata
        assert budget.available < 10000  # Some tokens consumed

    @pytest.mark.asyncio
    async def test_invoke_insufficient_budget(self) -> None:
        """Test invoking with insufficient budget."""
        budget = MockTokenBudget(max_balance=100, initial=10)  # Very low budget
        bard = BudgetedBard(budget=budget)
        traces = make_trace_sequence(10)
        request = NarrativeRequest(traces=traces)

        with pytest.raises(InsufficientBudgetError):
            await bard.invoke(request)

    @pytest.mark.asyncio
    async def test_invoke_if_affordable_success(self) -> None:
        """Test invoke_if_affordable with sufficient budget."""
        budget = MockTokenBudget(max_balance=10000, initial=10000)
        bard = BudgetedBard(budget=budget)
        traces = make_trace_sequence(3)
        request = NarrativeRequest(traces=traces)

        narrative = await bard.invoke_if_affordable(request)

        assert narrative is not None

    @pytest.mark.asyncio
    async def test_invoke_if_affordable_insufficient(self) -> None:
        """Test invoke_if_affordable with insufficient budget."""
        budget = MockTokenBudget(max_balance=100, initial=10)
        bard = BudgetedBard(budget=budget)
        traces = make_trace_sequence(10)
        request = NarrativeRequest(traces=traces)

        narrative = await bard.invoke_if_affordable(request)

        assert narrative is None


class TestNarrationCost:
    """Tests for NarrationCost."""

    def test_estimate_property(self) -> None:
        """Test estimate property."""
        cost = NarrationCost(
            estimated_input_tokens=100,
            estimated_output_tokens=200,
            total_estimated=300,
        )

        assert cost.estimate == 300

    def test_with_actual(self) -> None:
        """Test with_actual method."""
        cost = NarrationCost(
            estimated_input_tokens=100,
            estimated_output_tokens=200,
            total_estimated=300,
        )

        updated = cost.with_actual(250)

        assert updated.actual_tokens == 250
        assert updated.estimated_input_tokens == 100  # Preserved


# =============================================================================
# NarrativeOrchestrator Tests
# =============================================================================


class TestNarrativeOrchestrator:
    """Tests for NarrativeOrchestrator."""

    def test_creation(self) -> None:
        """Test creating an orchestrator."""
        store = MemoryCrystalStore()
        orchestrator = NarrativeOrchestrator(store=store)

        assert orchestrator.store == store
        assert orchestrator.bard is not None

    def test_creation_with_budget(self) -> None:
        """Test creating with budget creates BudgetedBard."""
        store = MemoryCrystalStore()
        budget = MockTokenBudget()
        orchestrator = NarrativeOrchestrator(store=store, budget=budget)

        assert isinstance(orchestrator.bard, BudgetedBard)

    @pytest.mark.asyncio
    async def test_record(self) -> None:
        """Test recording a crystal."""
        store = MemoryCrystalStore()
        orchestrator = NarrativeOrchestrator(store=store)
        trace = make_trace()

        await orchestrator.record(trace)

        assert store.count() == 1

    @pytest.mark.asyncio
    async def test_record_with_memory(self) -> None:
        """Test recording with M-gent memory."""
        store = MemoryCrystalStore()
        memory = MockHolographicMemory()
        embedder = MockEmbedder()
        orchestrator = NarrativeOrchestrator(
            store=store,
            memory=memory,
            embedder=embedder,
        )
        trace = make_trace()

        await orchestrator.record(trace)

        assert store.count() == 1
        assert len(memory._patterns) == 1

    @pytest.mark.asyncio
    async def test_record_many(self) -> None:
        """Test recording multiple crystals."""
        store = MemoryCrystalStore()
        orchestrator = NarrativeOrchestrator(store=store)
        traces = make_trace_sequence(5)

        await orchestrator.record_many(traces)

        assert store.count() == 5

    @pytest.mark.asyncio
    async def test_narrate(self) -> None:
        """Test generating a narrative."""
        store = MemoryCrystalStore()
        orchestrator = NarrativeOrchestrator(store=store)
        traces = make_trace_sequence(3)

        for trace in traces:
            store.store(trace)

        narrative = await orchestrator.narrate(
            traces=traces,
            genre=NarrativeGenre.TECHNICAL,
        )

        assert narrative is not None
        assert len(narrative.traces_used) == 3

    def test_get_stats(self) -> None:
        """Test getting statistics."""
        store = MemoryCrystalStore()
        orchestrator = NarrativeOrchestrator(store=store)

        stats = orchestrator.get_stats()

        assert "crystal_count" in stats
        assert "has_memory" in stats
        assert "bard_type" in stats
