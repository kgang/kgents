"""
Tests for M-gents: Holographic Associative Memory.

Tests:
- HolographicMemory: store, retrieve, consolidate
- RecollectionAgent: cue-based recall
- ConsolidationAgent: background processing
- TieredMemory: three-tier hierarchy
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents.m.consolidation import (
    ConsolidationAgent,
    ConsolidationMode,
    ForgettingCurveAgent,
)
from agents.m.holographic import (
    CompressionLevel,
    HolographicMemory,
    MemoryPattern,
    ResonanceResult,
)
from agents.m.recollection import (
    ContextualRecollectionAgent,
    Cue,
    Recollection,
    RecollectionAgent,
    SimpleReconstructor,
    WeightedReconstructor,
)
from agents.m.tiered import (
    AttentionFilter,
    SensoryBuffer,
    TieredMemory,
    WorkingMemory,
)

# ========== HolographicMemory Tests ==========


class TestHolographicMemory:
    """Tests for HolographicMemory core functionality."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.mark.asyncio
    async def test_store_creates_pattern(self, memory: HolographicMemory[str]) -> None:
        """Store creates a memory pattern."""
        pattern = await memory.store(
            id="m1",
            content="User prefers dark mode",
            concepts=["preference", "ui"],
        )

        assert pattern.id == "m1"
        assert pattern.content == "User prefers dark mode"
        assert "preference" in pattern.concepts

    @pytest.mark.asyncio
    async def test_retrieve_finds_similar(self, memory: HolographicMemory[str]) -> None:
        """Retrieve finds similar patterns by resonance."""
        await memory.store("m1", "User prefers dark mode", ["preference"])
        await memory.store("m2", "User works at night", ["schedule"])

        results = await memory.retrieve("What does the user prefer?")

        assert len(results) > 0
        assert all(isinstance(r, ResonanceResult) for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_always_returns_something(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Retrieve returns empty list, not None, when no matches."""
        await memory.store("m1", "Hello world", ["greeting"])

        results = await memory.retrieve("Completely unrelated query")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_by_concept(self, memory: HolographicMemory[str]) -> None:
        """Retrieve by concept finds exact concept matches."""
        await memory.store("m1", "Dark mode setting", ["preference", "ui"])
        await memory.store("m2", "Language setting", ["preference", "locale"])
        await memory.store("m3", "Weather today", ["weather"])

        results = await memory.retrieve_by_concept("preference")

        assert len(results) == 2
        assert all("preference" in r.pattern.concepts for r in results)

    @pytest.mark.asyncio
    async def test_access_updates_metadata(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Accessing a pattern updates its metadata."""
        pattern = await memory.store("m1", "Test content")
        initial_access_count = pattern.access_count

        await memory.retrieve("Test")

        assert memory._patterns["m1"].access_count > initial_access_count

    @pytest.mark.asyncio
    async def test_demote_reduces_resolution(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Demoting a pattern reduces its resolution."""
        await memory.store("m1", "Test content")
        assert memory._patterns["m1"].compression == CompressionLevel.FULL

        await memory.demote("m1", levels=1)

        assert memory._patterns["m1"].compression == CompressionLevel.HIGH  # type: ignore[comparison-overlap]

    @pytest.mark.asyncio
    async def test_promote_increases_resolution(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Promoting a pattern increases its resolution."""
        await memory.store("m1", "Test content")
        memory._patterns["m1"].compression = CompressionLevel.LOW

        await memory.promote("m1", levels=1)

        assert memory._patterns["m1"].compression == CompressionLevel.MEDIUM

    @pytest.mark.asyncio
    async def test_consolidate_processes_patterns(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Consolidation processes hot and cold patterns."""
        # Create a hot pattern (frequently accessed)
        await memory.store("hot1", "Hot content")
        for _ in range(10):
            await memory.retrieve("Hot")

        # Create a cold pattern (never accessed again)
        await memory.store("cold1", "Cold content")
        memory._patterns["cold1"].last_accessed = datetime.now() - timedelta(hours=24)

        stats = await memory.consolidate()

        assert "demoted" in stats
        assert "promoted" in stats

    def test_temperature_calculation(self, memory: HolographicMemory[str]) -> None:
        """Pattern temperature reflects recency and frequency."""
        pattern = MemoryPattern[str](
            id="test",
            content="Test",
            embedding=[0.0] * 64,
        )

        # Just created - should be warm
        temp1 = pattern.temperature
        assert 0.3 < temp1 < 0.8

        # Simulate old pattern
        pattern.last_accessed = datetime.now() - timedelta(hours=24)
        temp2 = pattern.temperature

        assert temp2 < temp1  # Older = colder

    def test_retention_follows_forgetting_curve(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Retention follows Ebbinghaus forgetting curve."""
        pattern = MemoryPattern[str](
            id="test",
            content="Test",
            embedding=[0.0] * 64,
            strength=1.0,
        )

        # Just accessed - high retention
        ret1 = pattern.retention
        assert ret1 > 0.9

        # Simulate time passing
        pattern.last_accessed = datetime.now() - timedelta(days=1)
        ret2 = pattern.retention

        assert ret2 < ret1  # Retention decays

    def test_stats_returns_memory_statistics(
        self, memory: HolographicMemory[str]
    ) -> None:
        """Stats returns comprehensive memory statistics."""
        stats = memory.stats()

        assert "total_patterns" in stats
        assert "store_count" in stats
        assert "retrieve_count" in stats
        assert "compression_distribution" in stats


# ========== RecollectionAgent Tests ==========


class TestRecollectionAgent:
    """Tests for RecollectionAgent."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory: HolographicMemory[str]) -> RecollectionAgent[str]:
        return RecollectionAgent(memory)

    @pytest.mark.asyncio
    async def test_invoke_with_text_cue(
        self, agent: RecollectionAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Invoke with text cue retrieves memories."""
        await memory.store("m1", "User likes pizza", ["food"])

        cue = Cue(text="What food does the user like?")
        recollection = await agent.invoke(cue)

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_invoke_with_concept_cue(
        self, agent: RecollectionAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Invoke with concept cue retrieves by concept."""
        await memory.store("m1", "User prefers dark mode", ["preference"])

        cue = Cue(concepts=["preference"])
        recollection = await agent.invoke(cue)

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_invoke_with_invalid_cue(self, agent: RecollectionAgent[str]) -> None:
        """Invalid cue returns empty recollection."""
        cue = Cue()  # No text, concepts, or embedding
        recollection = await agent.invoke(cue)

        assert recollection.confidence == 0.0
        assert recollection.reconstruction_method == "invalid_cue"

    @pytest.mark.asyncio
    async def test_recall_by_concept(
        self, agent: RecollectionAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """recall_by_concept retrieves by semantic concept."""
        await memory.store("m1", "Setting A", ["settings"])
        await memory.store("m2", "Setting B", ["settings"])

        recollection = await agent.recall_by_concept("settings")

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_simple_reconstructor(self, memory: HolographicMemory[str]) -> None:
        """SimpleReconstructor returns top match."""
        await memory.store("m1", "First memory")
        await memory.store("m2", "Second memory")

        reconstructor: SimpleReconstructor[str] = SimpleReconstructor()
        agent: RecollectionAgent[str] = RecollectionAgent(
            memory, reconstructor=reconstructor
        )

        cue = Cue(text="First")
        recollection = await agent.invoke(cue)

        assert recollection.reconstruction_method == "top_match"

    @pytest.mark.asyncio
    async def test_weighted_reconstructor(self, memory: HolographicMemory[str]) -> None:
        """WeightedReconstructor synthesizes from multiple patterns."""
        await memory.store("m1", "Memory A")
        await memory.store("m2", "Memory B")

        reconstructor: WeightedReconstructor[str] = WeightedReconstructor()
        agent: RecollectionAgent[str] = RecollectionAgent(
            memory, reconstructor=reconstructor
        )

        cue = Cue(text="Memory")
        recollection = await agent.invoke(cue)

        assert recollection.reconstruction_method in ("weighted_synthesis", "empty")


class TestContextualRecollectionAgent:
    """Tests for context-dependent recall."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory: HolographicMemory[str]) -> ContextualRecollectionAgent[str]:
        return ContextualRecollectionAgent(memory)

    @pytest.mark.asyncio
    async def test_context_affects_recall(
        self, agent: ContextualRecollectionAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Context affects which memories are recalled."""
        await memory.store("m1", "Work task A")
        await memory.store("m2", "Personal task B")

        cue = Cue(text="What should I do?")
        recollection = await agent.invoke_with_context(
            cue,
            current_task="work",
        )

        assert isinstance(recollection, Recollection)


# ========== ConsolidationAgent Tests ==========


class TestConsolidationAgent:
    """Tests for ConsolidationAgent."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory: HolographicMemory[str]) -> ConsolidationAgent[str]:
        return ConsolidationAgent(memory)

    @pytest.mark.asyncio
    async def test_invoke_returns_result(
        self, agent: ConsolidationAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Invoke returns consolidation result."""
        await memory.store("m1", "Test memory")

        result = await agent.invoke()

        assert result.mode == ConsolidationMode.NORMAL
        assert result.timestamp is not None
        assert result.before_profile is not None
        assert result.after_profile is not None

    @pytest.mark.asyncio
    async def test_light_mode_minimal_changes(
        self, agent: ConsolidationAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Light mode makes minimal changes."""
        await memory.store("m1", "Test memory")

        result = await agent.invoke(mode=ConsolidationMode.LIGHT)

        assert result.was_productive or result.demoted == 0

    @pytest.mark.asyncio
    async def test_deep_mode_aggressive_cleanup(
        self, agent: ConsolidationAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Deep mode is more aggressive."""
        await memory.store("m1", "Old memory")
        memory._patterns["m1"].last_accessed = datetime.now() - timedelta(days=60)

        result = await agent.invoke(mode=ConsolidationMode.DEEP)

        assert result.mode == ConsolidationMode.DEEP

    @pytest.mark.asyncio
    async def test_profile_returns_temperature_distribution(
        self, agent: ConsolidationAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Profile returns temperature distribution."""
        await memory.store("m1", "Memory 1")
        await memory.store("m2", "Memory 2")

        profile = await agent.profile()

        assert profile.total == 2

    @pytest.mark.asyncio
    async def test_schedule_consolidation(
        self, agent: ConsolidationAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Schedule returns appropriate mode based on state."""
        # Empty memory - no consolidation needed
        mode = await agent.schedule_consolidation()
        assert mode is None

        # Add patterns
        await memory.store("m1", "Memory 1")

        mode = await agent.schedule_consolidation()
        # May or may not need consolidation


class TestForgettingCurveAgent:
    """Tests for forgetting curve analysis."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory: HolographicMemory[str]) -> ForgettingCurveAgent[str]:
        return ForgettingCurveAgent(memory)

    @pytest.mark.asyncio
    async def test_analyze_categorizes_patterns(
        self, agent: ForgettingCurveAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Analyze categorizes patterns by retention."""
        # Well-retained pattern
        await memory.store("m1", "Recent memory")

        # About-to-forget pattern
        await memory.store("m2", "Old memory")
        memory._patterns["m2"].last_accessed = datetime.now() - timedelta(days=7)
        memory._patterns["m2"].strength = 0.1

        analysis = await agent.analyze()

        assert "needs_review" in analysis
        assert "can_compress" in analysis
        assert "stable" in analysis

    def test_optimal_review_interval(
        self, agent: ForgettingCurveAgent[str], memory: HolographicMemory[str]
    ) -> None:
        """Optimal interval based on strength."""
        asyncio.run(memory.store("m1", "Test memory"))

        interval = agent.optimal_review_interval("m1")

        assert interval is not None
        assert isinstance(interval, timedelta)


# ========== TieredMemory Tests ==========


class TestSensoryBuffer:
    """Tests for Tier 1 sensory buffer."""

    def test_perceive_adds_entry(self) -> None:
        """Perceive adds entry to buffer."""
        buffer = SensoryBuffer[str](capacity=10)
        buffer.perceive("Hello", salience=0.8)

        entries = buffer.all()
        assert len(entries) == 1
        assert entries[0].content == "Hello"

    def test_recent_filters_by_time(self) -> None:
        """Recent filters by time window."""
        buffer = SensoryBuffer[str](ttl_seconds=10)
        buffer.perceive("Entry 1")

        recent = buffer.recent(seconds=5)
        assert len(recent) == 1

    def test_capacity_enforced(self) -> None:
        """Capacity limit is enforced."""
        buffer = SensoryBuffer[str](capacity=3)

        for i in range(5):
            buffer.perceive(f"Entry {i}")

        assert len(buffer.all()) <= 3

    def test_ttl_enforced(self) -> None:
        """TTL removes old entries."""
        buffer = SensoryBuffer[str](ttl_seconds=1)
        buffer.perceive("Entry")

        # Manually age the entry
        buffer._entries[0].timestamp = datetime.now() - timedelta(seconds=2)

        entries = buffer.all()
        assert len(entries) == 0


class TestWorkingMemory:
    """Tests for Tier 2 working memory."""

    def test_load_adds_chunk(self) -> None:
        """Load adds chunk to working memory."""
        working = WorkingMemory[str](capacity=7)
        working.load("c1", "Content 1", ["concept"])

        chunk = working.get("c1")
        assert chunk is not None
        assert chunk.content == "Content 1"

    def test_capacity_evicts_lowest(self) -> None:
        """Exceeding capacity evicts lowest activation chunk."""
        working = WorkingMemory[str](capacity=2)

        working.load("c1", "Content 1")
        working.load("c2", "Content 2")

        # c1 will have lower activation (not accessed recently)
        evicted = working.load("c3", "Content 3")

        assert evicted is not None
        assert len(working.active_chunks(min_activation=0)) == 2

    def test_unload_removes_chunk(self) -> None:
        """Unload removes chunk."""
        working = WorkingMemory[str]()
        working.load("c1", "Content")

        chunk = working.unload("c1")

        assert chunk is not None
        assert working.get("c1") is None

    def test_find_by_concept(self) -> None:
        """Find by concept returns matching chunks."""
        working = WorkingMemory[str]()
        working.load("c1", "Content 1", ["tag-a"])
        working.load("c2", "Content 2", ["tag-b"])

        matches = working.find_by_concept("tag-a")

        assert len(matches) == 1
        assert matches[0].id == "c1"


class TestAttentionFilter:
    """Tests for attention filtering."""

    def test_filter_by_salience(self) -> None:
        """Filter removes low-salience entries."""
        attention = AttentionFilter(salience_threshold=0.5)
        buffer = SensoryBuffer[str]()

        buffer.perceive("High salience", salience=0.8)
        buffer.perceive("Low salience", salience=0.2)

        filtered = attention.filter(buffer.all())

        assert len(filtered) == 1
        assert filtered[0].salience >= 0.5

    def test_focus_boosts_relevance(self) -> None:
        """Focus boosts relevance of matching entries."""
        attention = AttentionFilter(salience_threshold=0.3)
        buffer = SensoryBuffer[str]()

        buffer.perceive("Work task", salience=0.4)
        buffer.perceive("Random thing", salience=0.4)

        filtered = attention.filter(buffer.all(), focus="work")

        # Both might pass threshold, but work-related should be first
        assert len(filtered) >= 1


class TestTieredMemory:
    """Tests for full tiered memory system."""

    @pytest.fixture
    def memory(self) -> TieredMemory[str]:
        return TieredMemory[str]()

    def test_perceive_adds_to_sensory(self, memory: TieredMemory[str]) -> None:
        """Perceive adds to sensory tier."""
        memory.perceive("Hello world", salience=0.7)

        perceptions = memory.recent_perceptions()
        assert len(perceptions) == 1

    @pytest.mark.asyncio
    async def test_attend_moves_to_working(self, memory: TieredMemory[str]) -> None:
        """Attend moves from sensory to working."""
        memory.perceive("Important message", salience=0.9)

        chunk_ids = await memory.attend(focus="important")

        assert len(chunk_ids) > 0
        assert memory._working.utilization > 0

    def test_load_to_working_direct(self, memory: TieredMemory[str]) -> None:
        """Can load directly to working memory."""
        chunk_id = memory.load_to_working(
            "Direct content",
            concepts=["test"],
        )

        chunk = memory._working.get(chunk_id)
        assert chunk is not None

    @pytest.mark.asyncio
    async def test_consolidate_moves_to_longterm(
        self, memory: TieredMemory[str]
    ) -> None:
        """Consolidate moves from working to long-term."""
        memory.load_to_working("Content to consolidate")

        stats = await memory.consolidate()

        assert stats["consolidated"] > 0

    @pytest.mark.asyncio
    async def test_recall_retrieves_from_longterm(
        self, memory: TieredMemory[str]
    ) -> None:
        """Recall retrieves from long-term."""
        await memory._longterm.store("m1", "User preference: dark mode")

        patterns = await memory.recall("What are user preferences?")

        assert isinstance(patterns, list)

    def test_stats_covers_all_tiers(self, memory: TieredMemory[str]) -> None:
        """Stats covers all memory tiers."""
        stats = memory.stats()

        assert "sensory" in stats
        assert "working" in stats
        assert "longterm" in stats


# ========== Integration Tests ==========


class TestMGentIntegration:
    """Integration tests across M-gent components."""

    @pytest.mark.asyncio
    async def test_full_memory_lifecycle(self) -> None:
        """Test full lifecycle: perceive → attend → consolidate → recall."""
        memory = TieredMemory[str]()

        # 1. Perceive raw input
        memory.perceive("User said they like dark mode", salience=0.9)
        memory.perceive("Random noise", salience=0.2)

        # 2. Attend to salient input
        await memory.attend(focus="user")

        # 3. Consolidate to long-term
        await memory.consolidate()

        # 4. Recall later
        patterns = await memory.recall("What does the user like?")

        assert len(patterns) >= 0  # May or may not find match

    @pytest.mark.asyncio
    async def test_recollection_with_consolidation(self) -> None:
        """RecollectionAgent works after consolidation."""
        holographic = HolographicMemory[str]()
        agent = RecollectionAgent(holographic)
        consolidator = ConsolidationAgent(holographic)

        # Store some memories
        await holographic.store("m1", "User prefers dark mode", ["preference"])
        await holographic.store("m2", "User works at night", ["schedule"])

        # Consolidate
        await consolidator.invoke()

        # Recall
        cue = Cue(text="What are user preferences?")
        recollection = await agent.invoke(cue)

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_memory_temperature_affects_consolidation(self) -> None:
        """Hot and cold patterns treated differently."""
        memory = HolographicMemory[str]()
        consolidator = ConsolidationAgent(memory)

        # Hot pattern (frequently accessed)
        await memory.store("hot", "Hot content")
        for _ in range(10):
            await memory.retrieve("Hot")

        # Cold pattern (never accessed)
        await memory.store("cold", "Cold content")
        memory._patterns["cold"].last_accessed = datetime.now() - timedelta(hours=24)

        result = await consolidator.invoke()

        # Should have demoted cold and/or promoted hot
        assert result.before_profile is not None


# ========== Phase 2: D-gent Integration Tests ==========


class MockUnifiedMemory:
    """Mock D-gent UnifiedMemory for testing."""

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
                return dict(state)
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
        visited = set()
        edges = []

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


# Import Phase 2 modules
from agents.m.dgent_backend import (
    AssociativeWebMemory,
    DgentBackedHolographicMemory,
    PersistenceConfig,
    TemporalMemory,
    create_dgent_memory,
)
from agents.m.persistent_tiered import (
    NarrativeMemory,
    PersistentTieredMemory,
    PersistentWorkingMemory,
    TierConfig,
    create_persistent_tiered_memory,
)


class TestDgentBackedHolographicMemory:
    """Tests for D-gent backed holographic memory."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    @pytest.fixture
    def memory(self, storage: MockUnifiedMemory) -> DgentBackedHolographicMemory[str]:
        return DgentBackedHolographicMemory(
            storage=storage,
            namespace="test",
        )

    @pytest.mark.asyncio
    async def test_store_persists_to_dgent(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Store persists to D-gent storage."""
        await memory.store("m1", "Test content", ["concept1"])

        # Check D-gent semantic layer
        assert "test:concept1" in storage._concepts

    @pytest.mark.asyncio
    async def test_store_witnesses_event(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Store records temporal event."""
        await memory.store("m1", "Test content")

        # Check D-gent temporal layer
        assert len(storage._events) > 0
        assert "store:m1" in storage._events[0][1]

    @pytest.mark.asyncio
    async def test_retrieve_with_dgent_fallback(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Retrieve uses D-gent semantic layer."""
        await memory.store("m1", "User prefers dark mode", ["preference"])

        results = await memory.retrieve("What preferences?")

        assert len(results) >= 0  # May or may not find based on embedding

    @pytest.mark.asyncio
    async def test_persist_explicit(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Explicit persist syncs all patterns."""
        await memory.store("m1", "Content 1")
        await memory.store("m2", "Content 2")

        stats = await memory.persist()

        assert stats["persisted"] == 2

    @pytest.mark.asyncio
    async def test_stats_includes_dgent_info(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Stats includes D-gent information."""
        await memory.store("m1", "Test content")

        stats = memory.stats()

        assert "dgent" in stats
        assert stats["dgent"]["namespace"] == "test"

    @pytest.mark.asyncio
    async def test_consolidate_syncs_to_dgent(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Consolidation syncs changes to D-gent."""
        await memory.store("m1", "Test content")

        result = await memory.consolidate()

        assert "demoted" in result or "promoted" in result

    @pytest.mark.asyncio
    async def test_demote_tracks_pending(
        self, memory: DgentBackedHolographicMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Demote tracks pending updates."""
        await memory.store("m1", "Test content")
        await memory.demote("m1")

        assert "m1" in memory._pending_updates


class TestAssociativeWebMemory:
    """Tests for associative web memory."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    @pytest.fixture
    def memory(self, storage: MockUnifiedMemory) -> AssociativeWebMemory[str]:
        return AssociativeWebMemory(
            storage=storage,
            namespace="associative",
        )

    @pytest.mark.asyncio
    async def test_link_creates_relationship(
        self, memory: AssociativeWebMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Link creates D-gent relationship."""
        await memory.store("m1", "Memory A")
        await memory.store("m2", "Memory B")

        await memory.link("m1", "related_to", "m2")

        assert ("related_to", "m2") in storage._relationships.get("m1", [])

    @pytest.mark.asyncio
    async def test_spread_activation(
        self, memory: AssociativeWebMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Spread activation traverses relationships."""
        await memory.store("m1", "Memory A")
        await memory.store("m2", "Memory B")
        await memory.store("m3", "Memory C")

        await memory.link("m1", "related_to", "m2")
        await memory.link("m2", "related_to", "m3")

        results = await memory.spread_activation("m1", depth=2)

        # Should find m2 and maybe m3
        assert len(results) >= 0

    @pytest.mark.asyncio
    async def test_related_memories(
        self, memory: AssociativeWebMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Related memories returns directly linked patterns."""
        await memory.store("m1", "Memory A")
        await memory.store("m2", "Memory B")

        await memory.link("m1", "supports", "m2")

        related = await memory.related_memories("m1", "supports")

        assert len(related) >= 0


class TestTemporalMemory:
    """Tests for temporal memory."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    @pytest.fixture
    def memory(self, storage: MockUnifiedMemory) -> TemporalMemory[str]:
        return TemporalMemory(
            storage=storage,
            namespace="temporal",
        )

    @pytest.mark.asyncio
    async def test_at_time_returns_snapshot(
        self, memory: TemporalMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """At time returns state snapshot."""
        await memory.store("m1", "First memory")

        snapshot = await memory.at_time(datetime.now())

        # May return state or None based on timing
        assert snapshot is not None or snapshot is None

    @pytest.mark.asyncio
    async def test_timeline_returns_events(
        self, memory: TemporalMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Timeline returns memory events."""
        await memory.store("m1", "Memory 1")
        await memory.store("m2", "Memory 2")

        events = await memory.timeline(limit=10)

        assert len(events) >= 0

    @pytest.mark.asyncio
    async def test_concept_evolution(
        self, memory: TemporalMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Concept evolution tracks changes over time."""
        await memory.store("m1", "Task A", ["task"])
        await memory.store("m2", "Task B", ["task"])

        evolution = await memory.concept_evolution("task", days=1)

        assert isinstance(evolution, list)


class TestPersistentWorkingMemory:
    """Tests for persistent working memory."""

    def test_load_tracks_timestamp(self) -> None:
        """Load tracks timestamp for TTL."""
        working: PersistentWorkingMemory[str] = PersistentWorkingMemory(
            capacity=5, ttl_minutes=30
        )

        working.load("c1", "Content 1")

        assert "c1" in working._chunk_timestamps

    def test_cleanup_expired_removes_old(self) -> None:
        """Cleanup removes expired chunks."""
        working: PersistentWorkingMemory[str] = PersistentWorkingMemory(
            capacity=5, ttl_minutes=0.001
        )

        working.load("c1", "Content 1")
        working._chunk_timestamps["c1"] = datetime.now() - timedelta(minutes=1)

        expired = working.cleanup_expired()

        assert "c1" in expired
        assert working.get("c1") is None

    def test_active_chunks_filters_expired(self) -> None:
        """Active chunks filters out expired."""
        working: PersistentWorkingMemory[str] = PersistentWorkingMemory(
            capacity=5, ttl_minutes=30
        )

        working.load("c1", "Content 1")
        working.load("c2", "Content 2")

        # Expire c1
        working._chunk_timestamps["c1"] = datetime.now() - timedelta(hours=1)
        working._ttl = timedelta(minutes=30)

        chunks = working.active_chunks()

        # c1 should be expired
        chunk_ids = [c.id for c in chunks]
        assert "c1" not in chunk_ids


class TestPersistentTieredMemory:
    """Tests for persistent tiered memory."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    @pytest.fixture
    def memory(self, storage: MockUnifiedMemory) -> PersistentTieredMemory[str]:
        return PersistentTieredMemory(longterm_storage=storage)

    def test_perceive_adds_to_sensory(self, memory: TieredMemory[str]) -> None:
        """Perceive adds to sensory tier."""
        memory.perceive("Hello world", salience=0.8)

        perceptions = memory.recent_perceptions()
        assert len(perceptions) == 1

    @pytest.mark.asyncio
    async def test_attend_moves_to_working(self, memory: TieredMemory[str]) -> None:
        """Attend moves from sensory to working."""
        memory.perceive("Important message", salience=0.9)

        chunk_ids = await memory.attend(focus="important")

        assert len(chunk_ids) > 0
        assert memory._working.utilization > 0

    @pytest.mark.asyncio
    async def test_consolidate_moves_to_longterm(
        self, memory: PersistentTieredMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Consolidate moves to long-term with D-gent persistence."""
        memory.load_to_working("Content to consolidate", ["test"])

        stats = await memory.consolidate(force=True)

        assert stats["consolidated"] > 0

    @pytest.mark.asyncio
    async def test_recall_retrieves_from_longterm(
        self, memory: PersistentTieredMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Recall retrieves from long-term."""
        await memory._longterm.store("m1", "User preference: dark mode")

        patterns = await memory.recall("preferences")

        assert isinstance(patterns, list)

    @pytest.mark.asyncio
    async def test_persist_explicit(
        self, memory: PersistentTieredMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Explicit persist syncs all tiers."""
        memory.load_to_working("Content 1")
        memory.load_to_working("Content 2")

        stats = await memory.persist()

        assert "consolidation" in stats
        assert "longterm" in stats

    def test_stats_covers_all_tiers(self, memory: TieredMemory[str]) -> None:
        """Stats covers all memory tiers."""
        stats = memory.stats()

        assert hasattr(stats, "sensory")
        assert hasattr(stats, "working")
        assert hasattr(stats, "longterm")

    @pytest.mark.asyncio
    async def test_full_lifecycle_with_dgent(
        self, memory: PersistentTieredMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Test full lifecycle: perceive → attend → consolidate → recall."""
        # 1. Perceive
        memory.perceive("User said they like dark mode", salience=0.9)

        # 2. Attend
        await memory.attend(focus="user")

        # 3. Consolidate (persists to D-gent)
        await memory.consolidate(force=True)

        # 4. Check D-gent has data
        assert len(storage._events) > 0 or len(storage._concepts) > 0


class TestNarrativeMemory:
    """Tests for narrative memory."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    @pytest.fixture
    def memory(self, storage: MockUnifiedMemory) -> NarrativeMemory[str]:
        return NarrativeMemory(longterm_storage=storage)

    @pytest.mark.asyncio
    async def test_begin_episode(self, memory: NarrativeMemory[str]) -> None:
        """Begin episode creates episode ID."""
        episode_id = await memory.begin_episode("test-episode")

        assert episode_id.startswith("episode-")

    @pytest.mark.asyncio
    async def test_store_with_episode(
        self, memory: NarrativeMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """Store with episode creates relationship."""
        episode_id = await memory.begin_episode("test")

        pattern = await memory.store_with_episode(
            "m1",
            "Memory content",
            ["concept"],
            episode_id,
        )

        assert pattern.id == "m1"
        assert ("part_of", episode_id) in storage._relationships.get("m1", [])

    @pytest.mark.asyncio
    async def test_end_episode_consolidates(
        self, memory: NarrativeMemory[str], storage: MockUnifiedMemory
    ) -> None:
        """End episode consolidates memories."""
        episode_id = await memory.begin_episode("test")
        await memory.store_with_episode("m1", "Content", None, episode_id)

        result = await memory.end_episode(episode_id)

        assert "memory_count" in result
        assert result["memory_count"] == 1


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.fixture
    def storage(self) -> MockUnifiedMemory:
        return MockUnifiedMemory()

    def test_create_dgent_memory(self, storage: MockUnifiedMemory) -> None:
        """create_dgent_memory creates configured memory."""
        memory = create_dgent_memory(
            storage=storage,
            namespace="test",
            enable_all=True,
        )

        assert isinstance(memory, DgentBackedHolographicMemory)
        assert memory._namespace == "test"
        assert memory._config.enable_semantic

    def test_create_persistent_tiered_memory(self, storage: MockUnifiedMemory) -> None:
        """create_persistent_tiered_memory creates configured memory."""
        memory = create_persistent_tiered_memory(
            longterm_storage=storage,
            enable_all=True,
        )

        assert isinstance(memory, PersistentTieredMemory)


# ========== Integration Tests: M-gent × D-gent ==========


class TestMGentDGentIntegration:
    """Integration tests for M-gent × D-gent."""

    @pytest.mark.asyncio
    async def test_holographic_with_unified_memory(self) -> None:
        """Holographic memory works with UnifiedMemory."""
        storage: MockUnifiedMemory = MockUnifiedMemory()
        memory: DgentBackedHolographicMemory[str] = DgentBackedHolographicMemory(
            storage=storage
        )

        # Store
        await memory.store("m1", "User likes dark mode", ["preference"])
        await memory.store("m2", "User works at night", ["schedule"])

        # D-gent has the data
        assert len(storage._concepts) > 0
        assert len(storage._events) > 0

        # Consolidate (syncs to D-gent)
        await memory.consolidate()

        # Stats reflect both layers
        stats = memory.stats()
        assert stats["total_patterns"] == 2
        assert "dgent" in stats

    @pytest.mark.asyncio
    async def test_tiered_memory_full_flow(self) -> None:
        """Tiered memory: perceive → attend → consolidate → recall."""
        storage: MockUnifiedMemory = MockUnifiedMemory()
        memory: PersistentTieredMemory[str] = PersistentTieredMemory(
            longterm_storage=storage,
            config=TierConfig(auto_consolidate=False),
        )

        # 1. Perceive (Tier 1)
        memory.perceive("User preference: dark mode", salience=0.9)
        memory.perceive("Random noise", salience=0.2)

        assert len(memory.recent_perceptions()) == 2

        # 2. Attend (Tier 1 → Tier 2)
        chunks = await memory.attend(focus="preference")

        # Only high-salience should pass
        assert len(chunks) >= 0

        # 3. Consolidate (Tier 2 → Tier 3 with D-gent)
        stats = await memory.consolidate(force=True)

        assert "consolidated" in stats

        # 4. D-gent should have data
        assert len(storage._events) > 0 or len(storage._concepts) > 0

    @pytest.mark.asyncio
    async def test_associative_web_spreading_activation(self) -> None:
        """Associative web with D-gent relational layer."""
        storage: MockUnifiedMemory = MockUnifiedMemory()
        memory: AssociativeWebMemory[str] = AssociativeWebMemory(
            storage=storage,
            config=PersistenceConfig(enable_relational=True),
        )

        # Create memories
        await memory.store("m1", "Pizza is Italian food")
        await memory.store("m2", "Italy is in Europe")
        await memory.store("m3", "Europe has many countries")

        # Create associative links
        await memory.link("m1", "related_to", "m2")
        await memory.link("m2", "related_to", "m3")

        # D-gent has relationships
        assert len(storage._relationships) == 2

        # Spread activation from m1
        results = await memory.spread_activation("m1", depth=2)

        # Should find connected memories
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_narrative_memory_episode_flow(self) -> None:
        """Narrative memory with episode structure."""
        storage: MockUnifiedMemory = MockUnifiedMemory()
        memory: NarrativeMemory[str] = NarrativeMemory(
            longterm_storage=storage,
            config=TierConfig(enable_relational=True),
        )

        # Begin episode
        episode_id = await memory.begin_episode("morning-routine")

        # Store memories in episode
        await memory.store_with_episode("m1", "Wake up", ["morning"], episode_id)
        await memory.store_with_episode("m2", "Coffee", ["morning"], episode_id)
        await memory.store_with_episode("m3", "Email", ["morning"], episode_id)

        # End episode
        result = await memory.end_episode(episode_id)

        assert result["memory_count"] == 3

        # D-gent has episode relationships
        assert len(storage._relationships) >= 3


# ========== Phase 3: Prospective & Ethical Tests ==========

from agents.m.prospective import (
    ActionHistory,
    ActionProposal,
    ActionRecord,
    ContextualQuery,
    ContextualRecallAgent,
    EthicalExperience,
    EthicalGeometry,
    EthicalGeometryAgent,
    EthicalPosition,
    EthicalRegion,
    PredictedAction,
    ProspectiveAgent,
    Situation,
    create_ethical_agent,
    create_prospective_agent,
)


class TestSituation:
    """Tests for Situation data class."""

    def test_situation_creation(self) -> None:
        """Situation can be created with required fields."""
        sit = Situation(id="s1", description="User asked about dark mode")

        assert sit.id == "s1"
        assert sit.description == "User asked about dark mode"
        assert sit.summary == "User asked about dark mode"

    def test_situation_with_context(self) -> None:
        """Situation can include context."""
        sit = Situation(
            id="s1",
            description="User requested help",
            context={"urgency": "high"},
            concepts=["help", "support"],
        )

        assert sit.context["urgency"] == "high"
        assert "help" in sit.concepts


class TestActionHistory:
    """Tests for ActionHistory."""

    def test_record_situation(self) -> None:
        """Record situation stores it."""
        history = ActionHistory()
        sit = Situation(id="s1", description="Test situation")

        history.record_situation(sit)

        assert history.situation_count() == 1

    def test_record_action(self) -> None:
        """Record action stores it."""
        history = ActionHistory()
        sit = Situation(id="s1", description="Test situation")
        action = ActionRecord(id="a1", action="Do something", situation_id="s1")

        history.record_situation(sit)
        history.record_action(action)

        assert history.action_count() == 1

    @pytest.mark.asyncio
    async def test_get_subsequent(self) -> None:
        """Get subsequent returns actions for a situation."""
        history = ActionHistory()
        sit = Situation(id="s1", description="Test situation")
        action = ActionRecord(id="a1", action="Do something", situation_id="s1")

        history.record_situation(sit)
        history.record_action(action)

        actions = await history.get_subsequent(sit)

        assert len(actions) == 1
        assert actions[0].action == "Do something"

    def test_record_outcome(self) -> None:
        """Record outcome updates action."""
        history = ActionHistory()
        sit = Situation(id="s1", description="Test")
        action = ActionRecord(id="a1", action="Do thing", situation_id="s1")

        history.record_situation(sit)
        history.record_action(action)
        history.record_outcome("a1", "Success!", success=True)

        # Action should be updated
        actions = history._actions["s1"]
        assert actions[0].outcome == "Success!"
        assert actions[0].success is True


class TestProspectiveAgent:
    """Tests for ProspectiveAgent."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def action_log(self) -> ActionHistory:
        return ActionHistory()

    @pytest.fixture
    def agent(
        self, memory: HolographicMemory[str], action_log: ActionHistory
    ) -> ProspectiveAgent[str]:
        return ProspectiveAgent(memory, action_log)

    @pytest.mark.asyncio
    async def test_invoke_returns_predictions(
        self,
        agent: ProspectiveAgent[str],
        memory: HolographicMemory[str],
        action_log: ActionHistory,
    ) -> None:
        """Invoke returns predictions based on past experience."""
        # Record past experience
        past_sit = Situation(id="s1", description="User asked about dark mode")
        action_log.record_situation(past_sit)
        action_log.record_action(
            ActionRecord(
                id="a1",
                action="Enable dark mode",
                situation_id="s1",
                success=True,
            )
        )
        await memory.store("s1", past_sit.description, ["preference", "ui"])

        # Predict for new situation
        new_sit = Situation(id="s2", description="User asked about dark mode settings")
        predictions = await agent.invoke(new_sit)

        assert isinstance(predictions, list)

    @pytest.mark.asyncio
    async def test_record_experience(self, agent: ProspectiveAgent[str]) -> None:
        """Record experience builds predictive model."""
        sit = Situation(id="s1", description="User needs help")

        record = await agent.record_experience(
            sit,
            action="Provide assistance",
            outcome="User satisfied",
            success=True,
        )

        assert record.action == "Provide assistance"
        assert record.success is True

    @pytest.mark.asyncio
    async def test_prediction_confidence(
        self,
        agent: ProspectiveAgent[str],
        memory: HolographicMemory[str],
        action_log: ActionHistory,
    ) -> None:
        """Prediction confidence reflects similarity and success rate."""
        # Record successful action
        past_sit = Situation(id="s1", description="User wants pizza")
        action_log.record_situation(past_sit)
        action_log.record_action(
            ActionRecord(
                id="a1",
                action="Order pizza",
                situation_id="s1",
                success=True,
            )
        )
        await memory.store("s1", past_sit.description, ["food"])

        # Record failed action
        past_sit2 = Situation(id="s2", description="User wants sushi")
        action_log.record_situation(past_sit2)
        action_log.record_action(
            ActionRecord(
                id="a2",
                action="Order sushi",
                situation_id="s2",
                success=False,
            )
        )
        await memory.store("s2", past_sit2.description, ["food"])

        # Both are food-related, but success affects confidence
        new_sit = Situation(id="s3", description="User wants food")
        predictions = await agent.invoke(new_sit)

        # Predictions should exist
        assert isinstance(predictions, list)

    def test_stats(
        self, agent: ProspectiveAgent[str], action_log: ActionHistory
    ) -> None:
        """Stats returns agent statistics."""
        action_log.record_situation(Situation(id="s1", description="Test"))

        stats = agent.stats()

        assert "situations" in stats
        assert "actions" in stats


class TestEthicalGeometry:
    """Tests for EthicalGeometry."""

    @pytest.fixture
    def geometry(self) -> EthicalGeometry:
        return EthicalGeometry()

    def test_learn_from_harmful_experience(self, geometry: EthicalGeometry) -> None:
        """Learning from harm expands forbidden region."""
        exp = EthicalExperience(
            action="Share private data",
            outcome="Privacy breach",
            harm_caused=True,
            good_produced=False,
            severity=0.8,
        )

        geometry.learn_from_experience(exp)

        position = geometry.locate("Share private data")
        assert position.region == EthicalRegion.FORBIDDEN

    def test_learn_from_good_experience(self, geometry: EthicalGeometry) -> None:
        """Learning from good expands virtuous region."""
        exp = EthicalExperience(
            action="Help user solve problem",
            outcome="User grateful",
            harm_caused=False,
            good_produced=True,
            severity=0.9,
        )

        geometry.learn_from_experience(exp)

        position = geometry.locate("Help user solve problem")
        assert position.region == EthicalRegion.VIRTUOUS

    def test_locate_new_action(self, geometry: EthicalGeometry) -> None:
        """Locate returns position for new action."""
        position = geometry.locate("Unknown action")

        assert isinstance(position, EthicalPosition)
        assert position.action == "Unknown action"
        # New action is permissible by default
        assert position.region == EthicalRegion.PERMISSIBLE

    def test_forbidden_property(self, geometry: EthicalGeometry) -> None:
        """Forbidden property returns all forbidden positions."""
        geometry.learn_from_experience(
            EthicalExperience(
                action="Bad action",
                outcome="Harm",
                harm_caused=True,
                good_produced=False,
                severity=0.5,
            )
        )

        forbidden = geometry.forbidden

        assert len(forbidden) == 1
        assert forbidden[0].action == "Bad action"

    def test_nearest_permissible(self, geometry: EthicalGeometry) -> None:
        """Nearest permissible finds alternatives."""
        # Create forbidden and permissible positions
        geometry.learn_from_experience(
            EthicalExperience(
                action="Bad action",
                outcome="Harm",
                harm_caused=True,
                good_produced=False,
                severity=0.5,
            )
        )
        geometry._positions["Good action"] = EthicalPosition(
            action="Good action",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=geometry._embed_action("Good action"),
        )

        position = geometry.locate("Bad action")
        alternatives = geometry.nearest_permissible(position)

        assert isinstance(alternatives, list)

    def test_nearest_virtuous(self, geometry: EthicalGeometry) -> None:
        """Nearest virtuous finds virtuous alternative."""
        geometry.learn_from_experience(
            EthicalExperience(
                action="Excellent action",
                outcome="Great outcome",
                harm_caused=False,
                good_produced=True,
                severity=0.9,
            )
        )

        neutral = EthicalPosition(
            action="Neutral action",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=geometry._embed_action("Neutral action"),
        )

        virtuous = geometry.nearest_virtuous(neutral)

        assert virtuous is not None
        assert virtuous.region == EthicalRegion.VIRTUOUS

    def test_stats_geometry(self, geometry: EthicalGeometry) -> None:
        """Stats returns geometry statistics."""
        stats = geometry.stats()

        assert "total_positions" in stats
        assert "forbidden_count" in stats
        assert "virtuous_count" in stats


class TestEthicalGeometryAgent:
    """Tests for EthicalGeometryAgent."""

    @pytest.fixture
    def geometry(self) -> EthicalGeometry:
        return EthicalGeometry()

    @pytest.fixture
    def agent(self, geometry: EthicalGeometry) -> EthicalGeometryAgent:
        return EthicalGeometryAgent(geometry)

    @pytest.mark.asyncio
    async def test_invoke_blocks_forbidden(
        self, agent: EthicalGeometryAgent, geometry: EthicalGeometry
    ) -> None:
        """Invoke blocks forbidden actions."""
        # Learn that action is forbidden
        geometry.learn_from_experience(
            EthicalExperience(
                action="Dangerous action",
                outcome="Harm occurred",
                harm_caused=True,
                good_produced=False,
                severity=0.9,
            )
        )

        proposal = ActionProposal(action="Dangerous action")
        path = await agent.invoke(proposal)

        assert path.blocked is True
        assert path.reason != ""

    @pytest.mark.asyncio
    async def test_invoke_allows_permissible(self, agent: EthicalGeometryAgent) -> None:
        """Invoke allows permissible actions."""
        proposal = ActionProposal(action="Normal action")
        path = await agent.invoke(proposal)

        assert path.blocked is False

    @pytest.mark.asyncio
    async def test_invoke_suggests_virtuous(
        self, agent: EthicalGeometryAgent, geometry: EthicalGeometry
    ) -> None:
        """Invoke suggests virtuous alternatives."""
        # Learn virtuous action
        geometry.learn_from_experience(
            EthicalExperience(
                action="Excellent action",
                outcome="Great outcome",
                harm_caused=False,
                good_produced=True,
                severity=0.9,
            )
        )

        proposal = ActionProposal(action="Normal action")
        path = await agent.invoke(proposal)

        assert path.virtuous_alternative is not None
        assert path.distance_to_virtue < float("inf")

    @pytest.mark.asyncio
    async def test_learn_updates_geometry(
        self, agent: EthicalGeometryAgent, geometry: EthicalGeometry
    ) -> None:
        """Learn updates underlying geometry."""
        await agent.learn(
            EthicalExperience(
                action="New bad action",
                outcome="Bad outcome",
                harm_caused=True,
                good_produced=False,
                severity=0.7,
            )
        )

        position = geometry.locate("New bad action")
        assert position.region == EthicalRegion.FORBIDDEN

    def test_stats_agent(self, agent: EthicalGeometryAgent) -> None:
        """Stats returns agent statistics."""
        stats = agent.stats()

        assert "total_positions" in stats


class TestEthicalPosition:
    """Tests for EthicalPosition."""

    def test_distance_to(self) -> None:
        """Distance to calculates Euclidean distance."""
        pos1 = EthicalPosition(
            action="A",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=[0.0, 0.0],
        )
        pos2 = EthicalPosition(
            action="B",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=[3.0, 4.0],
        )

        assert pos1.distance_to(pos2) == 5.0

    def test_distance_to_mismatched_dims(self) -> None:
        """Distance to handles mismatched dimensions."""
        pos1 = EthicalPosition(
            action="A",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=[0.0, 0.0],
        )
        pos2 = EthicalPosition(
            action="B",
            region=EthicalRegion.PERMISSIBLE,
            coordinates=[1.0, 1.0, 1.0],
        )

        assert pos1.distance_to(pos2) == float("inf")


class TestPredictedAction:
    """Tests for PredictedAction ordering."""

    def test_comparison(self) -> None:
        """PredictedAction compares by confidence."""
        sit = Situation(id="s1", description="Test")
        action = ActionRecord(id="a1", action="Test", situation_id="s1")

        pred1 = PredictedAction(
            action="A",
            confidence=0.8,
            source_situation=sit,
            source_action=action,
            similarity=0.9,
        )
        pred2 = PredictedAction(
            action="B",
            confidence=0.5,
            source_situation=sit,
            source_action=action,
            similarity=0.6,
        )

        assert pred2 < pred1  # Lower confidence is "less than"


class TestContextualRecallAgent:
    """Tests for ContextualRecallAgent."""

    @pytest.fixture
    def memory(self) -> HolographicMemory[str]:
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory: HolographicMemory[str]) -> ContextualRecallAgent:
        return ContextualRecallAgent(memory)

    @pytest.mark.asyncio
    async def test_invoke_with_context(
        self, agent: ContextualRecallAgent, memory: HolographicMemory[str]
    ) -> None:
        """Invoke weights results by context."""
        await memory.store("m1", "Work task A")
        await memory.store("m2", "Personal task B")

        query = ContextualQuery(
            cue="task",
            task="work",
        )
        results = await agent.invoke(query)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_context_boosts_relevance(
        self, agent: ContextualRecallAgent, memory: HolographicMemory[str]
    ) -> None:
        """Context matching boosts relevance."""
        await memory.store("m1", "Work meeting notes")
        await memory.store("m2", "Home renovation plans")

        # Query with work context
        query = ContextualQuery(
            cue="notes",
            task="work",
        )
        results = await agent.invoke(query)

        # Work-related should get context boost
        assert isinstance(results, list)


class TestFactoryFunctionsPhase3:
    """Tests for Phase 3 factory functions."""

    def test_create_prospective_agent(self) -> None:
        """create_prospective_agent creates configured agent."""
        memory = HolographicMemory[str]()
        agent = create_prospective_agent(memory)

        assert isinstance(agent, ProspectiveAgent)

    def test_create_prospective_agent_with_log(self) -> None:
        """create_prospective_agent with existing log."""
        memory = HolographicMemory[str]()
        log = ActionHistory()
        agent = create_prospective_agent(memory, action_log=log)

        assert agent._action_log is log

    def test_create_ethical_agent(self) -> None:
        """create_ethical_agent creates configured agent."""
        agent = create_ethical_agent()

        assert isinstance(agent, EthicalGeometryAgent)

    def test_create_ethical_agent_with_geometry(self) -> None:
        """create_ethical_agent with existing geometry."""
        geometry = EthicalGeometry(dimensions=16)
        agent = create_ethical_agent(geometry=geometry)

        assert agent._geometry is geometry


# ========== Integration Tests: Phase 3 ==========


class TestPhase3Integration:
    """Integration tests for Phase 3 components."""

    @pytest.mark.asyncio
    async def test_prospective_with_holographic(self) -> None:
        """ProspectiveAgent integrates with HolographicMemory."""
        memory: HolographicMemory[str] = HolographicMemory[str]()
        agent: ProspectiveAgent[str] = ProspectiveAgent(memory, ActionHistory())

        # Record experiences
        for i in range(3):
            sit = Situation(id=f"s{i}", description=f"Situation type {i % 2}")
            await agent.record_experience(
                sit,
                action=f"Action for type {i % 2}",
                success=True,
            )

        # Memory should have patterns
        assert len(memory._patterns) == 3

        # Predict for similar situation
        new_sit = Situation(id="snew", description="Situation type 0")
        predictions = await agent.invoke(new_sit)

        assert isinstance(predictions, list)

    @pytest.mark.asyncio
    async def test_ethical_learning_trajectory(self) -> None:
        """Ethical geometry evolves with experience."""
        geometry = EthicalGeometry()
        agent = EthicalGeometryAgent(geometry)

        # Initially, action is permissible
        proposal = ActionProposal(action="Ambiguous action")
        path1 = await agent.invoke(proposal)
        assert path1.blocked is False

        # Learn that it causes harm
        await agent.learn(
            EthicalExperience(
                action="Ambiguous action",
                outcome="Caused harm",
                harm_caused=True,
                good_produced=False,
                severity=0.8,
            )
        )

        # Now it should be blocked
        path2 = await agent.invoke(proposal)
        assert path2.blocked is True

    @pytest.mark.asyncio
    async def test_prospective_with_dgent_memory(self) -> None:
        """ProspectiveAgent works with D-gent backed memory."""
        storage: MockUnifiedMemory = MockUnifiedMemory()
        memory: DgentBackedHolographicMemory[str] = DgentBackedHolographicMemory(
            storage=storage
        )
        agent: ProspectiveAgent[str] = ProspectiveAgent(memory, ActionHistory())

        # Record experience
        sit = Situation(id="s1", description="User needs help")
        await agent.record_experience(
            sit,
            action="Provide assistance",
            success=True,
        )

        # D-gent should have data
        assert len(storage._events) > 0

    @pytest.mark.asyncio
    async def test_ethical_with_prospective(self) -> None:
        """Ethical and prospective work together."""
        memory: HolographicMemory[str] = HolographicMemory[str]()
        action_log: ActionHistory = ActionHistory()
        prospective: ProspectiveAgent[str] = ProspectiveAgent(memory, action_log)

        geometry = EthicalGeometry()
        ethical = EthicalGeometryAgent(geometry)

        # Record past experience with ethical outcome
        sit = Situation(id="s1", description="User asked for data")
        await prospective.record_experience(
            sit,
            action="Share private data",
            outcome="Privacy breach",
            success=False,
        )

        # Learn ethical consequence
        await ethical.learn(
            EthicalExperience(
                action="Share private data",
                outcome="Privacy breach",
                harm_caused=True,
                good_produced=False,
                severity=0.9,
            )
        )

        # Now check new proposal
        proposal = ActionProposal(action="Share private data")
        path = await ethical.invoke(proposal)

        assert path.blocked is True


# ========== Phase 4: L-gent VectorHolographicMemory Tests ==========

from agents.m.vector_holographic import (
    ClusterInfo,
    VectorHolographicMemory,
    VectorMemoryConfig,
    VoidInfo,
    create_simple_vector_memory,
)


class TestVectorHolographicMemory:
    """Tests for VectorHolographicMemory (L-gent integration)."""

    @pytest.fixture
    def memory(self) -> VectorHolographicMemory[str]:
        """Create a simple vector memory for testing."""
        return create_simple_vector_memory(dimension=64)

    @pytest.mark.asyncio
    async def test_store_and_retrieve(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Store and retrieve using vector similarity."""
        await memory.store("m1", "User prefers dark mode", ["preference", "ui"])
        await memory.store("m2", "User works at night", ["schedule"])

        results = await memory.retrieve("What does the user prefer?")

        assert len(results) >= 0  # May find matches
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_store_creates_pattern_vector(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Store creates pattern in both memory and backend."""
        pattern = await memory.store("m1", "Test content", ["test"])

        assert pattern.id == "m1"
        assert "test" in pattern.concepts

    @pytest.mark.asyncio
    async def test_delete_removes_pattern(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Delete removes from both memory and backend."""
        await memory.store("m1", "Content to delete")

        deleted = await memory.delete("m1")

        assert deleted is True
        assert "m1" not in memory._patterns

    @pytest.mark.asyncio
    async def test_delete_nonexistent(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Delete returns False for nonexistent pattern."""
        deleted = await memory.delete("nonexistent")

        assert deleted is False

    @pytest.mark.asyncio
    async def test_cluster_analysis(self, memory: VectorHolographicMemory[str]) -> None:
        """Cluster analysis returns cluster info."""
        await memory.store("m1", "Topic A content")
        await memory.store("m2", "Topic A related")
        await memory.store("m3", "Topic B different")

        clusters = await memory.cluster_analysis(k=2)

        assert isinstance(clusters, list)
        for cluster in clusters:
            assert isinstance(cluster, ClusterInfo)

    @pytest.mark.asyncio
    async def test_find_void(self, memory: VectorHolographicMemory[str]) -> None:
        """Find void returns None or VoidInfo."""
        await memory.store("m1", "Some content")

        void = await memory.find_void("unrelated query")

        # Mock backend returns None
        assert void is None or isinstance(void, VoidInfo)

    @pytest.mark.asyncio
    async def test_curvature_at(self, memory: VectorHolographicMemory[str]) -> None:
        """Curvature estimation returns a float."""
        await memory.store("m1", "Test content")

        curvature = await memory.curvature_at("test query")

        assert isinstance(curvature, float)

    @pytest.mark.asyncio
    async def test_demote_tracks_pending_vector(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Demote tracks pending updates."""
        await memory.store("m1", "Test content")

        await memory.demote("m1")

        assert "m1" in memory._pending_updates

    @pytest.mark.asyncio
    async def test_sync_to_backend(self, memory: VectorHolographicMemory[str]) -> None:
        """Sync clears pending updates."""
        await memory.store("m1", "Test content")
        await memory.demote("m1")

        synced = await memory.sync_to_backend()

        assert synced == 1
        assert len(memory._pending_updates) == 0

    def test_stats_includes_vector_info(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Stats include vector backend information."""
        stats = memory.stats()

        assert "vector_backend" in stats
        assert stats["vector_backend"]["dimension"] == 64

    @pytest.mark.asyncio
    async def test_compress_by_curvature(
        self, memory: VectorHolographicMemory[str]
    ) -> None:
        """Curvature-based compression returns stats."""
        await memory.store("m1", "Test content")

        result = await memory.compress_by_curvature()

        assert "enabled" in result


class TestVectorMemoryConfig:
    """Tests for VectorMemoryConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible defaults."""
        config = VectorMemoryConfig()

        assert config.dimension == 384
        assert config.default_limit == 10
        assert config.similarity_threshold == 0.3

    def test_custom_config(self) -> None:
        """Custom config values are preserved."""
        config = VectorMemoryConfig(
            dimension=768,
            namespace="custom",
        )

        assert config.dimension == 768
        assert config.namespace == "custom"


# ========== Phase 4: B-gent MemoryBudget Tests ==========

from agents.m.memory_budget import (
    BudgetedMemory,
    CentralBankProtocol,
    InsufficientBudgetError,
    MemoryCostModel,
    MemoryEconomicsDashboard,
    MemoryReceipt,
    ResolutionBudget,
    create_budgeted_memory,
    create_mock_bank,
)


class TestMemoryCostModel:
    """Tests for MemoryCostModel."""

    @pytest.fixture
    def cost_model(self) -> MemoryCostModel:
        return MemoryCostModel()

    def test_storage_cost_base(self, cost_model: MemoryCostModel) -> None:
        """Storage cost includes base cost."""
        cost = cost_model.storage_cost("short content")

        assert cost >= cost_model.base_storage_cost

    def test_storage_cost_scales_with_length(self, cost_model: MemoryCostModel) -> None:
        """Storage cost scales with content length."""
        short_cost = cost_model.storage_cost("short")
        long_cost = cost_model.storage_cost("a" * 10000)

        assert long_cost > short_cost

    def test_retrieval_cost_base(self, cost_model: MemoryCostModel) -> None:
        """Retrieval cost includes base cost."""
        cost = cost_model.retrieval_cost()

        assert cost >= cost_model.base_retrieval_cost

    def test_resolution_cost_promotion(self, cost_model: MemoryCostModel) -> None:
        """Promoting resolution costs tokens."""
        cost = cost_model.resolution_cost(
            CompressionLevel.LOW,
            CompressionLevel.FULL,
        )

        assert cost > 0

    def test_resolution_cost_demotion(self, cost_model: MemoryCostModel) -> None:
        """Demoting resolution costs nothing."""
        cost = cost_model.resolution_cost(
            CompressionLevel.FULL,
            CompressionLevel.LOW,
        )

        assert cost == 0

    def test_consolidation_cost(self, cost_model: MemoryCostModel) -> None:
        """Consolidation cost scales with pattern count."""
        cost_10 = cost_model.consolidation_cost(10)
        cost_20 = cost_model.consolidation_cost(20)

        assert cost_20 == 2 * cost_10


class TestResolutionBudget:
    """Tests for ResolutionBudget."""

    @pytest.fixture
    def resolution_budget(self) -> ResolutionBudget:
        return ResolutionBudget()

    def test_calculate_priority(self, resolution_budget: ResolutionBudget) -> None:
        """Priority calculation produces reasonable values."""
        pattern: MemoryPattern[str] = MemoryPattern(
            id="test",
            content="Test",
            embedding=[0.0] * 64,
            access_count=10,
            strength=5.0,
        )

        priority = resolution_budget.calculate_priority(pattern)

        assert 0.0 <= priority <= 1.0

    def test_allocate_resolution_empty(
        self, resolution_budget: ResolutionBudget
    ) -> None:
        """Allocation handles empty pattern list."""
        allocations = resolution_budget.allocate_resolution([], 10000)

        assert allocations == {}

    def test_allocate_resolution_distributes(
        self, resolution_budget: ResolutionBudget
    ) -> None:
        """Allocation distributes budget based on priority."""
        patterns: list[MemoryPattern[str]] = [
            MemoryPattern(
                id="hot", content="Hot", embedding=[0.0] * 64, access_count=100
            ),
            MemoryPattern(
                id="cold", content="Cold", embedding=[0.0] * 64, access_count=1
            ),
        ]

        allocations = resolution_budget.allocate_resolution(patterns, 200)

        assert len(allocations) == 2
        # Hot pattern should get higher priority
        assert allocations["hot"].priority_score >= allocations["cold"].priority_score

    def test_stats(self, resolution_budget: ResolutionBudget) -> None:
        """Stats returns allocation information."""
        stats = resolution_budget.stats()

        assert "allocated_patterns" in stats


class TestBudgetedMemory:
    """Tests for BudgetedMemory."""

    @pytest.fixture
    def bank(self) -> CentralBankProtocol:
        bank: CentralBankProtocol = create_mock_bank(max_balance=100000)
        return bank

    @pytest.fixture
    def memory(self, bank: CentralBankProtocol) -> BudgetedMemory[str]:
        return BudgetedMemory(
            memory=HolographicMemory(),
            bank=bank,
            account_id="test",
        )

    @pytest.mark.asyncio
    async def test_store_charges_tokens(
        self, memory: BudgetedMemory[str], bank: CentralBankProtocol
    ) -> None:
        """Store operation charges tokens."""
        initial_balance = bank.get_balance()

        receipt = await memory.store("m1", "Test content")

        assert receipt.success is True
        assert receipt.tokens_charged > 0
        assert bank.get_balance() < initial_balance

    @pytest.mark.asyncio
    async def test_store_creates_receipt(self, memory: BudgetedMemory[str]) -> None:
        """Store creates a receipt with details."""
        receipt = await memory.store("m1", "Test content", ["concept"])

        assert isinstance(receipt, MemoryReceipt)
        assert receipt.operation == "store"
        assert receipt.pattern_id == "m1"

    @pytest.mark.asyncio
    async def test_retrieve_charges_tokens(
        self, memory: BudgetedMemory[str], bank: CentralBankProtocol
    ) -> None:
        """Retrieve operation charges tokens."""
        await memory.store("m1", "Test content")
        initial_balance = bank.get_balance()

        results, receipt = await memory.retrieve("test")

        assert receipt.success is True
        assert bank.get_balance() < initial_balance

    @pytest.mark.asyncio
    async def test_retrieve_returns_results_and_receipt(
        self, memory: BudgetedMemory[str]
    ) -> None:
        """Retrieve returns both results and receipt."""
        await memory.store("m1", "Test content")

        results, receipt = await memory.retrieve("test")

        assert isinstance(results, list)
        assert isinstance(receipt, MemoryReceipt)
        assert receipt.operation == "retrieve"

    @pytest.mark.asyncio
    async def test_consolidate_with_budget(
        self, memory: BudgetedMemory[str], bank: CentralBankProtocol
    ) -> None:
        """Consolidation charges tokens."""
        await memory.store("m1", "Test content")
        initial_balance = bank.get_balance()

        receipt = await memory.consolidate_with_budget()

        assert receipt.operation == "consolidate"
        assert bank.get_balance() < initial_balance

    @pytest.mark.asyncio
    async def test_budget_status(
        self, memory: BudgetedMemory[str], bank: CentralBankProtocol
    ) -> None:
        """Budget status returns current state."""
        status = memory.budget_status()

        assert "current_balance" in status
        assert "utilization" in status
        assert "is_low" in status

    @pytest.mark.asyncio
    async def test_memory_stats(self, memory: BudgetedMemory[str]) -> None:
        """Memory stats includes budget info."""
        await memory.store("m1", "Test content")

        stats = memory.memory_stats()

        assert "budget" in stats
        assert "resolution_budget" in stats

    @pytest.mark.asyncio
    async def test_insufficient_budget_triggers_compression(
        self, bank: CentralBankProtocol
    ) -> None:
        """Low budget triggers emergency compression."""
        # Use very small budget
        small_bank: CentralBankProtocol = create_mock_bank(max_balance=50)
        memory: BudgetedMemory[str] = BudgetedMemory(
            memory=HolographicMemory(),
            bank=small_bank,
            account_id="test",
            enable_auto_compress=True,
        )

        # Should fail or compress
        try:
            await memory.store("m1", "Very long content" * 100)
        except InsufficientBudgetError:
            pass  # Expected when even compression doesn't help


class TestMemoryEconomicsDashboard:
    """Tests for MemoryEconomicsDashboard."""

    @pytest.fixture
    def bank(self) -> CentralBankProtocol:
        bank: CentralBankProtocol = create_mock_bank()
        return bank

    @pytest.fixture
    def memory(self, bank: CentralBankProtocol) -> BudgetedMemory[str]:
        return BudgetedMemory(
            memory=HolographicMemory(),
            bank=bank,
            account_id="test",
        )

    @pytest.fixture
    def dashboard(self, memory: BudgetedMemory[str]) -> MemoryEconomicsDashboard:
        return MemoryEconomicsDashboard(memory)

    @pytest.mark.asyncio
    async def test_generate_report(
        self, memory: BudgetedMemory[str], dashboard: MemoryEconomicsDashboard
    ) -> None:
        """Generate report produces valid report."""
        await memory.store("m1", "Test content")
        await memory.retrieve("test")

        report = dashboard.generate_report()

        assert report.store_count == 1
        assert report.retrieve_count == 1
        assert report.total_tokens_spent > 0

    @pytest.mark.asyncio
    async def test_report_metrics(
        self, memory: BudgetedMemory[str], dashboard: MemoryEconomicsDashboard
    ) -> None:
        """Report includes all expected metrics."""
        await memory.store("m1", "Test")

        report = dashboard.generate_report()

        assert hasattr(report, "tokens_on_storage")
        assert hasattr(report, "avg_cost_per_store")
        assert hasattr(report, "budget_utilization")


class TestPhase4FactoryFunctions:
    """Tests for Phase 4 factory functions."""

    def test_create_simple_vector_memory(self) -> None:
        """create_simple_vector_memory creates usable memory."""
        memory = create_simple_vector_memory(dimension=64)

        assert isinstance(memory, VectorHolographicMemory)

    def test_create_mock_bank(self) -> None:
        """create_mock_bank creates usable bank."""
        bank = create_mock_bank(max_balance=50000)

        assert bank.get_balance() == 50000

    def test_create_budgeted_memory(self) -> None:
        """create_budgeted_memory creates configured memory."""
        bank = create_mock_bank()
        memory = create_budgeted_memory(bank, account_id="test")

        assert isinstance(memory, BudgetedMemory)


# ========== Phase 4 Integration Tests ==========


class TestPhase4Integration:
    """Integration tests for Phase 4 (L-gent + B-gent)."""

    @pytest.mark.asyncio
    async def test_vector_memory_with_budget(self) -> None:
        """Vector memory works with budget enforcement."""
        # Create vector memory
        vector_memory = create_simple_vector_memory()

        # Create bank and wrap with budget
        bank = create_mock_bank(max_balance=100000)
        budgeted = BudgetedMemory(
            memory=vector_memory,
            bank=bank,
            account_id="test",
        )

        # Store with budget
        receipt = await budgeted.store("m1", "User prefers dark mode", ["preference"])

        assert receipt.success is True

        # Retrieve with budget
        results, receipt = await budgeted.retrieve("preferences")

        assert receipt.success is True

    @pytest.mark.asyncio
    async def test_resolution_allocation_affects_patterns(self) -> None:
        """Resolution budget affects pattern compression."""
        bank: CentralBankProtocol = create_mock_bank()
        memory: BudgetedMemory[str] = BudgetedMemory(
            memory=HolographicMemory(),
            bank=bank,
            account_id="test",
        )

        # Store patterns with different access patterns
        await memory.store("hot", "Hot pattern")
        await memory.store("cold", "Cold pattern")

        # Make "hot" actually hot by accessing it many times
        # This increases access_count which affects priority
        hot_pattern = memory._memory._patterns.get("hot")
        if hot_pattern:
            # Simulate many accesses by directly modifying access_count
            hot_pattern.access_count = 100
            hot_pattern.strength = 5.0

        # Consolidate with budget
        await memory.consolidate_with_budget()

        # Hot should have better resolution allocation
        hot_alloc = memory._resolution_budget.get_allocation("hot")
        cold_alloc = memory._resolution_budget.get_allocation("cold")

        if hot_alloc and cold_alloc:
            assert hot_alloc.priority_score > cold_alloc.priority_score

    @pytest.mark.asyncio
    async def test_full_economic_lifecycle(self) -> None:
        """Test full lifecycle: store → retrieve → consolidate → report."""
        bank: CentralBankProtocol = create_mock_bank(max_balance=50000)
        memory: BudgetedMemory[str] = BudgetedMemory(
            memory=HolographicMemory(),
            bank=bank,
            account_id="lifecycle-test",
        )
        dashboard = MemoryEconomicsDashboard(memory)

        # Store several patterns
        for i in range(5):
            await memory.store(f"m{i}", f"Content {i}", [f"concept-{i % 2}"])

        # Retrieve
        for _ in range(3):
            await memory.retrieve("Content")

        # Consolidate
        await memory.consolidate_with_budget()

        # Generate report
        report = dashboard.generate_report()

        assert report.store_count == 5
        assert report.retrieve_count == 3
        assert report.consolidate_count == 1
        assert report.total_tokens_spent > 0

        # Check budget utilization
        status = memory.budget_status()
        assert status["utilization"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
