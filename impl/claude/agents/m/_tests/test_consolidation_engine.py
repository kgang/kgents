"""
Tests for ConsolidationEngine.

Tests the "sleep" cycle functionality for memory reorganization.
"""

import time

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.m.associative import AssociativeMemory
from agents.m.consolidation_engine import (
    ConsolidationConfig,
    ConsolidationEngine,
    create_consolidation_engine,
)
from agents.m.lifecycle import LifecycleEvent
from agents.m.memory import Lifecycle, Memory


@pytest.fixture
def dgent():
    """Create a memory backend."""
    return MemoryBackend()


@pytest.fixture
def mgent(dgent):
    """Create an AssociativeMemory instance."""
    return AssociativeMemory(dgent=dgent)


@pytest.fixture
def engine(mgent):
    """Create a ConsolidationEngine instance."""
    return ConsolidationEngine(mgent)


class TestConsolidationBasic:
    """Basic consolidation cycle tests."""

    @pytest.mark.asyncio
    async def test_consolidate_empty(self, engine):
        """Consolidating empty memory returns zero report."""
        report = await engine.consolidate()
        assert report.dreaming_count == 0
        assert report.demoted_count == 0
        assert report.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_consolidate_marks_dormant_as_dreaming(self, engine, mgent):
        """Consolidation marks DORMANT memories as DREAMING."""
        # Store and deactivate a memory
        memory_id = await mgent.remember(b"Test content")
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        assert mgent._memories[memory_id].lifecycle == Lifecycle.DORMANT

        # Consolidate
        report = await engine.consolidate()

        # After consolidation, should return to DORMANT
        assert report.dreaming_count == 1
        assert mgent._memories[memory_id].lifecycle == Lifecycle.DORMANT

    @pytest.mark.asyncio
    async def test_consolidate_applies_relevance_decay(self, engine, mgent):
        """Consolidation decays relevance of non-cherished memories."""
        # Store and deactivate
        memory_id = await mgent.remember(b"Test content")
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        initial_relevance = mgent._memories[memory_id].relevance

        # Consolidate
        await engine.consolidate()

        # Relevance should have decayed
        assert mgent._memories[memory_id].relevance < initial_relevance

    @pytest.mark.asyncio
    async def test_consolidate_demotes_low_relevance(self, engine, mgent):
        """Consolidation demotes low-relevance memories to COMPOSTING."""
        # Store with low relevance
        memory_id = await mgent.remember(b"Low relevance content")
        memory = mgent._memories[memory_id]

        # Set very low relevance and deactivate
        low_rel = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=0.1,  # Below demote threshold
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        mgent._memories[memory_id] = low_rel

        # Consolidate
        report = await engine.consolidate()

        # Should be demoted
        assert report.demoted_count == 1
        assert mgent._memories[memory_id].lifecycle == Lifecycle.COMPOSTING

    @pytest.mark.asyncio
    async def test_consolidate_protects_cherished(self, engine, mgent):
        """Consolidation protects cherished memories from decay."""
        # Store and cherish
        memory_id = await mgent.remember(b"Cherished content")
        await mgent.cherish(memory_id)

        # Deactivate
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        initial_relevance = mgent._memories[memory_id].relevance

        # Consolidate
        await engine.consolidate()

        # Relevance should NOT have decayed
        assert mgent._memories[memory_id].relevance == initial_relevance
        assert mgent._memories[memory_id].lifecycle != Lifecycle.COMPOSTING


class TestConsolidationConfig:
    """Tests for consolidation configuration."""

    @pytest.mark.asyncio
    async def test_custom_decay_factor(self, mgent):
        """Custom decay factor is applied."""
        config = ConsolidationConfig(relevance_decay=0.5)
        engine = ConsolidationEngine(mgent, config)

        # Store and deactivate
        memory_id = await mgent.remember(b"Test content")
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        initial = mgent._memories[memory_id].relevance

        # Consolidate
        await engine.consolidate()

        # Should decay by 0.5
        expected = initial * 0.5
        assert abs(mgent._memories[memory_id].relevance - expected) < 0.01

    @pytest.mark.asyncio
    async def test_custom_demote_threshold(self, mgent):
        """Custom demote threshold is respected."""
        config = ConsolidationConfig(demote_threshold=0.8)
        engine = ConsolidationEngine(mgent, config)

        # Store with moderate relevance
        memory_id = await mgent.remember(b"Moderate relevance")
        memory = mgent._memories[memory_id]

        # Set relevance below custom threshold but above default
        moderate = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=0.5,  # Above default 0.2, below custom 0.8
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        mgent._memories[memory_id] = moderate

        # Consolidate
        report = await engine.consolidate()

        # Should be demoted with higher threshold
        assert report.demoted_count == 1

    @pytest.mark.asyncio
    async def test_aggressive_config(self, dgent):
        """Aggressive config creates engine with stronger decay."""
        mgent = AssociativeMemory(dgent=dgent)
        engine = create_consolidation_engine(mgent, aggressive=True)

        assert engine.config.relevance_decay == 0.85
        assert engine.config.demote_threshold == 0.3
        assert engine.config.enable_merging is True


class TestConsolidationMerging:
    """Tests for memory merging during consolidation."""

    @pytest.mark.asyncio
    async def test_merge_similar_memories(self, mgent):
        """Similar memories can be merged."""
        config = ConsolidationConfig(
            enable_merging=True,
            merge_threshold=0.99,  # Very high to only merge nearly identical
        )
        engine = ConsolidationEngine(mgent, config)

        # Store two nearly identical memories
        id1 = await mgent.remember(b"Python programming", embedding=[1.0, 0.0, 0.0])
        id2 = await mgent.remember(
            b"Python coding",
            embedding=[1.0, 0.0, 0.0],  # Identical embedding
        )

        # Deactivate both
        for mid in [id1, id2]:
            mem = mgent._memories[mid]
            mgent._memories[mid] = mem.deactivate()

        # Consolidate
        report = await engine.consolidate()

        # One should be merged (composted)
        assert report.merged_count == 1

        # One composting, one dormant
        lifecycles = [m.lifecycle for m in mgent._memories.values()]
        assert Lifecycle.COMPOSTING in lifecycles

    @pytest.mark.asyncio
    async def test_merge_keeps_higher_access(self, mgent):
        """Merging keeps the memory with higher access count."""
        config = ConsolidationConfig(enable_merging=True, merge_threshold=0.99)
        engine = ConsolidationEngine(mgent, config)

        # Store two similar memories
        id1 = await mgent.remember(b"Content A", embedding=[1.0, 0.0])
        id2 = await mgent.remember(b"Content B", embedding=[1.0, 0.0])

        # Give id2 higher access count
        mem1 = mgent._memories[id1].deactivate()
        mem2 = mgent._memories[id2]

        high_access = Memory(
            datum_id=mem2.datum_id,
            embedding=mem2.embedding,
            resolution=mem2.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=mem2.relevance,
            last_accessed=mem2.last_accessed,
            access_count=10,  # Higher
            metadata=mem2.metadata,
        )
        mgent._memories[id1] = mem1
        mgent._memories[id2] = high_access

        # Consolidate
        await engine.consolidate()

        # id2 should survive (higher access), id1 should compost
        assert mgent._memories[id1].lifecycle == Lifecycle.COMPOSTING
        assert mgent._memories[id2].lifecycle == Lifecycle.DORMANT


class TestConsolidationEvents:
    """Tests for lifecycle event emission."""

    @pytest.mark.asyncio
    async def test_events_emitted_on_transitions(self, mgent):
        """Events are emitted when memories transition."""
        events: list[LifecycleEvent] = []

        async def listener(event: LifecycleEvent):
            events.append(event)

        engine = ConsolidationEngine(mgent)
        engine.add_listener(listener)

        # Store and deactivate
        memory_id = await mgent.remember(b"Test content")
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        # Consolidate
        await engine.consolidate()

        # Should have received enter-dreaming event
        assert len(events) >= 1
        assert events[0].memory_id == memory_id
        assert events[0].to_state == Lifecycle.DREAMING

    @pytest.mark.asyncio
    async def test_remove_listener(self, mgent):
        """Listeners can be removed."""
        events: list[LifecycleEvent] = []

        async def listener(event: LifecycleEvent):
            events.append(event)

        engine = ConsolidationEngine(mgent)
        engine.add_listener(listener)
        engine.remove_listener(listener)

        # Store and deactivate
        memory_id = await mgent.remember(b"Test content")
        memory = mgent._memories[memory_id]
        mgent._memories[memory_id] = memory.deactivate()

        # Consolidate
        await engine.consolidate()

        # No events should be received
        assert len(events) == 0


class TestConsolidationDegradation:
    """Tests for COMPOSTING resolution degradation."""

    @pytest.mark.asyncio
    async def test_degrades_composting_resolution(self, engine, mgent):
        """Consolidation degrades resolution of COMPOSTING memories."""
        # Store and compost
        memory_id = await mgent.remember(b"Degrading content")
        await mgent.forget(memory_id)  # Transitions to COMPOSTING

        initial_resolution = mgent._memories[memory_id].resolution

        # Consolidate
        await engine.consolidate()

        # Resolution should have degraded
        assert mgent._memories[memory_id].resolution < initial_resolution

    @pytest.mark.asyncio
    async def test_degradation_applies_factor(self, mgent):
        """Resolution degrades by the configured factor."""
        config = ConsolidationConfig(
            resolution_decay=0.5,  # 50% each cycle
        )
        engine = ConsolidationEngine(mgent, config)

        # Store and compost
        memory_id = await mgent.remember(b"Content")
        await mgent.forget(memory_id)

        initial_resolution = mgent._memories[memory_id].resolution

        # Consolidate once
        await engine.consolidate()

        # Should degrade by factor
        expected = initial_resolution * config.resolution_decay
        assert abs(mgent._memories[memory_id].resolution - expected) < 0.01


class TestConsolidationPerformance:
    """Performance-related tests."""

    @pytest.mark.asyncio
    async def test_consolidation_duration_tracked(self, engine, mgent):
        """Consolidation duration is tracked."""
        # Store some memories
        for i in range(10):
            await mgent.remember(f"Content {i}".encode())

        report = await engine.consolidate()

        # Should have non-zero duration
        assert report.duration_ms > 0

    @pytest.mark.asyncio
    async def test_handles_large_memory_count(self, engine, mgent):
        """Can consolidate many memories."""
        # Store many memories
        for i in range(100):
            mid = await mgent.remember(f"Content {i}".encode())
            # Deactivate some
            if i % 2 == 0:
                mem = mgent._memories[mid]
                mgent._memories[mid] = mem.deactivate()

        # Should complete without error
        report = await engine.consolidate()

        assert report.dreaming_count == 50  # Half were dormant
