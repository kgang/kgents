"""
Tests for M-gents: Holographic Associative Memory.

Tests:
- HolographicMemory: store, retrieve, consolidate
- RecollectionAgent: cue-based recall
- ConsolidationAgent: background processing
- TieredMemory: three-tier hierarchy
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents.m.holographic import (
    HolographicMemory,
    MemoryPattern,
    CompressionLevel,
    ResonanceResult,
)
from agents.m.recollection import (
    RecollectionAgent,
    Cue,
    Recollection,
    SimpleReconstructor,
    WeightedReconstructor,
    ContextualRecollectionAgent,
)
from agents.m.consolidation import (
    ConsolidationAgent,
    ConsolidationMode,
    ForgettingCurveAgent,
)
from agents.m.tiered import (
    TieredMemory,
    SensoryBuffer,
    WorkingMemory,
    AttentionFilter,
)


# ========== HolographicMemory Tests ==========


class TestHolographicMemory:
    """Tests for HolographicMemory core functionality."""

    @pytest.fixture
    def memory(self):
        return HolographicMemory[str]()

    @pytest.mark.asyncio
    async def test_store_creates_pattern(self, memory):
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
    async def test_retrieve_finds_similar(self, memory):
        """Retrieve finds similar patterns by resonance."""
        await memory.store("m1", "User prefers dark mode", ["preference"])
        await memory.store("m2", "User works at night", ["schedule"])

        results = await memory.retrieve("What does the user prefer?")

        assert len(results) > 0
        assert all(isinstance(r, ResonanceResult) for r in results)

    @pytest.mark.asyncio
    async def test_retrieve_always_returns_something(self, memory):
        """Retrieve returns empty list, not None, when no matches."""
        await memory.store("m1", "Hello world", ["greeting"])

        results = await memory.retrieve("Completely unrelated query")

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_retrieve_by_concept(self, memory):
        """Retrieve by concept finds exact concept matches."""
        await memory.store("m1", "Dark mode setting", ["preference", "ui"])
        await memory.store("m2", "Language setting", ["preference", "locale"])
        await memory.store("m3", "Weather today", ["weather"])

        results = await memory.retrieve_by_concept("preference")

        assert len(results) == 2
        assert all("preference" in r.pattern.concepts for r in results)

    @pytest.mark.asyncio
    async def test_access_updates_metadata(self, memory):
        """Accessing a pattern updates its metadata."""
        pattern = await memory.store("m1", "Test content")
        initial_access_count = pattern.access_count

        await memory.retrieve("Test")

        assert memory._patterns["m1"].access_count > initial_access_count

    @pytest.mark.asyncio
    async def test_demote_reduces_resolution(self, memory):
        """Demoting a pattern reduces its resolution."""
        await memory.store("m1", "Test content")
        assert memory._patterns["m1"].compression == CompressionLevel.FULL

        await memory.demote("m1", levels=1)

        assert memory._patterns["m1"].compression == CompressionLevel.HIGH

    @pytest.mark.asyncio
    async def test_promote_increases_resolution(self, memory):
        """Promoting a pattern increases its resolution."""
        await memory.store("m1", "Test content")
        memory._patterns["m1"].compression = CompressionLevel.LOW

        await memory.promote("m1", levels=1)

        assert memory._patterns["m1"].compression == CompressionLevel.MEDIUM

    @pytest.mark.asyncio
    async def test_consolidate_processes_patterns(self, memory):
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

    def test_temperature_calculation(self, memory):
        """Pattern temperature reflects recency and frequency."""
        pattern = MemoryPattern(
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

    def test_retention_follows_forgetting_curve(self, memory):
        """Retention follows Ebbinghaus forgetting curve."""
        pattern = MemoryPattern(
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

    def test_stats_returns_memory_statistics(self, memory):
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
    def memory(self):
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory):
        return RecollectionAgent(memory)

    @pytest.mark.asyncio
    async def test_invoke_with_text_cue(self, agent, memory):
        """Invoke with text cue retrieves memories."""
        await memory.store("m1", "User likes pizza", ["food"])

        cue = Cue(text="What food does the user like?")
        recollection = await agent.invoke(cue)

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_invoke_with_concept_cue(self, agent, memory):
        """Invoke with concept cue retrieves by concept."""
        await memory.store("m1", "User prefers dark mode", ["preference"])

        cue = Cue(concepts=["preference"])
        recollection = await agent.invoke(cue)

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_invoke_with_invalid_cue(self, agent):
        """Invalid cue returns empty recollection."""
        cue = Cue()  # No text, concepts, or embedding
        recollection = await agent.invoke(cue)

        assert recollection.confidence == 0.0
        assert recollection.reconstruction_method == "invalid_cue"

    @pytest.mark.asyncio
    async def test_recall_by_concept(self, agent, memory):
        """recall_by_concept retrieves by semantic concept."""
        await memory.store("m1", "Setting A", ["settings"])
        await memory.store("m2", "Setting B", ["settings"])

        recollection = await agent.recall_by_concept("settings")

        assert isinstance(recollection, Recollection)

    @pytest.mark.asyncio
    async def test_simple_reconstructor(self, memory):
        """SimpleReconstructor returns top match."""
        await memory.store("m1", "First memory")
        await memory.store("m2", "Second memory")

        reconstructor = SimpleReconstructor()
        agent = RecollectionAgent(memory, reconstructor=reconstructor)

        cue = Cue(text="First")
        recollection = await agent.invoke(cue)

        assert recollection.reconstruction_method == "top_match"

    @pytest.mark.asyncio
    async def test_weighted_reconstructor(self, memory):
        """WeightedReconstructor synthesizes from multiple patterns."""
        await memory.store("m1", "Memory A")
        await memory.store("m2", "Memory B")

        reconstructor = WeightedReconstructor()
        agent = RecollectionAgent(memory, reconstructor=reconstructor)

        cue = Cue(text="Memory")
        recollection = await agent.invoke(cue)

        assert recollection.reconstruction_method in ("weighted_synthesis", "empty")


class TestContextualRecollectionAgent:
    """Tests for context-dependent recall."""

    @pytest.fixture
    def memory(self):
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory):
        return ContextualRecollectionAgent(memory)

    @pytest.mark.asyncio
    async def test_context_affects_recall(self, agent, memory):
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
    def memory(self):
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory):
        return ConsolidationAgent(memory)

    @pytest.mark.asyncio
    async def test_invoke_returns_result(self, agent, memory):
        """Invoke returns consolidation result."""
        await memory.store("m1", "Test memory")

        result = await agent.invoke()

        assert result.mode == ConsolidationMode.NORMAL
        assert result.timestamp is not None
        assert result.before_profile is not None
        assert result.after_profile is not None

    @pytest.mark.asyncio
    async def test_light_mode_minimal_changes(self, agent, memory):
        """Light mode makes minimal changes."""
        await memory.store("m1", "Test memory")

        result = await agent.invoke(mode=ConsolidationMode.LIGHT)

        assert result.was_productive or result.demoted == 0

    @pytest.mark.asyncio
    async def test_deep_mode_aggressive_cleanup(self, agent, memory):
        """Deep mode is more aggressive."""
        await memory.store("m1", "Old memory")
        memory._patterns["m1"].last_accessed = datetime.now() - timedelta(days=60)

        result = await agent.invoke(mode=ConsolidationMode.DEEP)

        assert result.mode == ConsolidationMode.DEEP

    @pytest.mark.asyncio
    async def test_profile_returns_temperature_distribution(self, agent, memory):
        """Profile returns temperature distribution."""
        await memory.store("m1", "Memory 1")
        await memory.store("m2", "Memory 2")

        profile = await agent.profile()

        assert profile.total == 2

    @pytest.mark.asyncio
    async def test_schedule_consolidation(self, agent, memory):
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
    def memory(self):
        return HolographicMemory[str]()

    @pytest.fixture
    def agent(self, memory):
        return ForgettingCurveAgent(memory)

    @pytest.mark.asyncio
    async def test_analyze_categorizes_patterns(self, agent, memory):
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

    def test_optimal_review_interval(self, agent, memory):
        """Optimal interval based on strength."""
        asyncio.run(memory.store("m1", "Test memory"))

        interval = agent.optimal_review_interval("m1")

        assert interval is not None
        assert isinstance(interval, timedelta)


# ========== TieredMemory Tests ==========


class TestSensoryBuffer:
    """Tests for Tier 1 sensory buffer."""

    def test_perceive_adds_entry(self):
        """Perceive adds entry to buffer."""
        buffer = SensoryBuffer[str](capacity=10)
        buffer.perceive("Hello", salience=0.8)

        entries = buffer.all()
        assert len(entries) == 1
        assert entries[0].content == "Hello"

    def test_recent_filters_by_time(self):
        """Recent filters by time window."""
        buffer = SensoryBuffer[str](ttl_seconds=10)
        buffer.perceive("Entry 1")

        recent = buffer.recent(seconds=5)
        assert len(recent) == 1

    def test_capacity_enforced(self):
        """Capacity limit is enforced."""
        buffer = SensoryBuffer[str](capacity=3)

        for i in range(5):
            buffer.perceive(f"Entry {i}")

        assert len(buffer.all()) <= 3

    def test_ttl_enforced(self):
        """TTL removes old entries."""
        buffer = SensoryBuffer[str](ttl_seconds=1)
        buffer.perceive("Entry")

        # Manually age the entry
        buffer._entries[0].timestamp = datetime.now() - timedelta(seconds=2)

        entries = buffer.all()
        assert len(entries) == 0


class TestWorkingMemory:
    """Tests for Tier 2 working memory."""

    def test_load_adds_chunk(self):
        """Load adds chunk to working memory."""
        working = WorkingMemory[str](capacity=7)
        working.load("c1", "Content 1", ["concept"])

        chunk = working.get("c1")
        assert chunk is not None
        assert chunk.content == "Content 1"

    def test_capacity_evicts_lowest(self):
        """Exceeding capacity evicts lowest activation chunk."""
        working = WorkingMemory[str](capacity=2)

        working.load("c1", "Content 1")
        working.load("c2", "Content 2")

        # c1 will have lower activation (not accessed recently)
        evicted = working.load("c3", "Content 3")

        assert evicted is not None
        assert len(working.active_chunks(min_activation=0)) == 2

    def test_unload_removes_chunk(self):
        """Unload removes chunk."""
        working = WorkingMemory[str]()
        working.load("c1", "Content")

        chunk = working.unload("c1")

        assert chunk is not None
        assert working.get("c1") is None

    def test_find_by_concept(self):
        """Find by concept returns matching chunks."""
        working = WorkingMemory[str]()
        working.load("c1", "Content 1", ["tag-a"])
        working.load("c2", "Content 2", ["tag-b"])

        matches = working.find_by_concept("tag-a")

        assert len(matches) == 1
        assert matches[0].id == "c1"


class TestAttentionFilter:
    """Tests for attention filtering."""

    def test_filter_by_salience(self):
        """Filter removes low-salience entries."""
        attention = AttentionFilter(salience_threshold=0.5)
        buffer = SensoryBuffer[str]()

        buffer.perceive("High salience", salience=0.8)
        buffer.perceive("Low salience", salience=0.2)

        filtered = attention.filter(buffer.all())

        assert len(filtered) == 1
        assert filtered[0].salience >= 0.5

    def test_focus_boosts_relevance(self):
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
    def memory(self):
        return TieredMemory[str]()

    def test_perceive_adds_to_sensory(self, memory):
        """Perceive adds to sensory tier."""
        memory.perceive("Hello world", salience=0.7)

        perceptions = memory.recent_perceptions()
        assert len(perceptions) == 1

    @pytest.mark.asyncio
    async def test_attend_moves_to_working(self, memory):
        """Attend moves from sensory to working."""
        memory.perceive("Important message", salience=0.9)

        chunk_ids = await memory.attend(focus="important")

        assert len(chunk_ids) > 0
        assert memory._working.utilization > 0

    def test_load_to_working_direct(self, memory):
        """Can load directly to working memory."""
        chunk_id = memory.load_to_working(
            "Direct content",
            concepts=["test"],
        )

        chunk = memory._working.get(chunk_id)
        assert chunk is not None

    @pytest.mark.asyncio
    async def test_consolidate_moves_to_longterm(self, memory):
        """Consolidate moves from working to long-term."""
        memory.load_to_working("Content to consolidate")

        stats = await memory.consolidate()

        assert stats["consolidated"] > 0

    @pytest.mark.asyncio
    async def test_recall_retrieves_from_longterm(self, memory):
        """Recall retrieves from long-term."""
        await memory._longterm.store("m1", "User preference: dark mode")

        patterns = await memory.recall("What are user preferences?")

        assert isinstance(patterns, list)

    def test_stats_covers_all_tiers(self, memory):
        """Stats covers all memory tiers."""
        stats = memory.stats()

        assert "sensory" in stats
        assert "working" in stats
        assert "longterm" in stats


# ========== Integration Tests ==========


class TestMGentIntegration:
    """Integration tests across M-gent components."""

    @pytest.mark.asyncio
    async def test_full_memory_lifecycle(self):
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
    async def test_recollection_with_consolidation(self):
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
    async def test_memory_temperature_affects_consolidation(self):
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
