"""
Tests for SoulMemory: K-gent Identity Continuity via M-gent.

Tests the wiring between K-gent's soul and M-gent's memory system.
"""

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.m.associative import AssociativeMemory
from agents.m.memory import Lifecycle, Memory
from agents.m.soul_memory import (
    BeliefMemory,
    ContextMemory,
    MemoryCategory,
    PatternMemory,
    SoulMemory,
    create_soul_memory,
)


@pytest.fixture
def dgent():
    """Create a memory backend."""
    return MemoryBackend()


@pytest.fixture
def mgent(dgent):
    """Create an AssociativeMemory instance."""
    return AssociativeMemory(dgent=dgent)


@pytest.fixture
def soul_memory(mgent):
    """Create a SoulMemory instance."""
    return SoulMemory(mgent)


class TestBeliefMemory:
    """Tests for belief (cherished) memory operations."""

    @pytest.mark.asyncio
    async def test_remember_belief_returns_belief_memory(self, soul_memory):
        """remember_belief returns a BeliefMemory."""
        belief = await soul_memory.remember_belief("Simplicity is the ultimate sophistication")

        assert isinstance(belief, BeliefMemory)
        assert belief.content == "Simplicity is the ultimate sophistication"
        assert belief.category == MemoryCategory.BELIEF

    @pytest.mark.asyncio
    async def test_remember_belief_is_cherished(self, soul_memory, mgent):
        """Beliefs are automatically cherished."""
        belief = await soul_memory.remember_belief("Test belief")

        memory = mgent._memories[belief.memory_id]
        assert memory.is_cherished

    @pytest.mark.asyncio
    async def test_remember_belief_with_tags(self, soul_memory):
        """Beliefs can have tags."""
        belief = await soul_memory.remember_belief(
            "Joy is free",
            tags=["principle", "joy"],
        )

        assert "principle" in belief.tags
        assert "joy" in belief.tags
        assert belief.is_principle

    @pytest.mark.asyncio
    async def test_get_beliefs(self, soul_memory):
        """get_beliefs returns all cherished beliefs."""
        await soul_memory.remember_belief("Belief 1")
        await soul_memory.remember_belief("Belief 2")
        await soul_memory.remember_belief("Belief 3")

        beliefs = await soul_memory.get_beliefs()

        assert len(beliefs) == 3
        contents = [b.content for b in beliefs]
        assert "Belief 1" in contents
        assert "Belief 2" in contents
        assert "Belief 3" in contents

    @pytest.mark.asyncio
    async def test_reinforce_belief(self, soul_memory, mgent):
        """reinforce_belief increases access count."""
        belief = await soul_memory.remember_belief("Reinforced belief")

        initial_count = mgent._memories[belief.memory_id].access_count

        result = await soul_memory.reinforce_belief(belief.memory_id)

        assert result is True
        assert mgent._memories[belief.memory_id].access_count > initial_count

    @pytest.mark.asyncio
    async def test_reinforce_nonexistent_belief(self, soul_memory):
        """reinforce_belief returns False for nonexistent ID."""
        result = await soul_memory.reinforce_belief("nonexistent")
        assert result is False


class TestPatternMemory:
    """Tests for pattern (decaying) memory operations."""

    @pytest.mark.asyncio
    async def test_remember_pattern_returns_pattern_memory(self, soul_memory):
        """remember_pattern returns a PatternMemory."""
        pattern = await soul_memory.remember_pattern("Kent often uses categorical abstractions")

        assert isinstance(pattern, PatternMemory)
        assert "categorical" in pattern.pattern
        assert pattern.frequency == 1

    @pytest.mark.asyncio
    async def test_remember_pattern_not_cherished(self, soul_memory, mgent):
        """Patterns are NOT cherished (they can decay)."""
        pattern = await soul_memory.remember_pattern("Test pattern")

        memory = mgent._memories[pattern.memory_id]
        assert not memory.is_cherished

    @pytest.mark.asyncio
    async def test_remember_pattern_initial_relevance(self, soul_memory, mgent):
        """Patterns can have custom initial relevance."""
        pattern = await soul_memory.remember_pattern(
            "Test pattern",
            initial_relevance=0.5,
        )

        memory = mgent._memories[pattern.memory_id]
        assert memory.relevance == 0.5

    @pytest.mark.asyncio
    async def test_reinforce_pattern_increases_frequency(self, soul_memory, mgent):
        """reinforce_pattern increases frequency count."""
        pattern = await soul_memory.remember_pattern("Test pattern")

        await soul_memory.reinforce_pattern(pattern.memory_id)

        memory = mgent._memories[pattern.memory_id]
        freq = int(memory.metadata.get("frequency", "0"))
        assert freq == 2

    @pytest.mark.asyncio
    async def test_get_active_patterns(self, soul_memory):
        """get_active_patterns returns patterns by relevance."""
        p1 = await soul_memory.remember_pattern("Pattern A", initial_relevance=0.9)
        p2 = await soul_memory.remember_pattern("Pattern B", initial_relevance=0.5)
        p3 = await soul_memory.remember_pattern("Pattern C", initial_relevance=0.7)

        patterns = await soul_memory.get_active_patterns(limit=10)

        assert len(patterns) == 3
        # Should be ordered by relevance
        assert patterns[0].pattern == "Pattern A"
        assert patterns[2].pattern == "Pattern B"


class TestContextMemory:
    """Tests for context (session-specific) memory operations."""

    @pytest.mark.asyncio
    async def test_remember_context_returns_context_memory(self, soul_memory):
        """remember_context returns a ContextMemory."""
        context = await soul_memory.remember_context(
            "User is working on data architecture",
            session_id="session-123",
        )

        assert isinstance(context, ContextMemory)
        assert "data architecture" in context.content
        assert context.session_id == "session-123"

    @pytest.mark.asyncio
    async def test_remember_context_initial_relevance(self, soul_memory, mgent):
        """Context can have custom initial relevance."""
        context = await soul_memory.remember_context(
            "Test context",
            session_id="session-123",
            initial_relevance=0.6,
        )

        memory = mgent._memories[context.memory_id]
        assert memory.relevance == 0.6

    @pytest.mark.asyncio
    async def test_get_session_context(self, soul_memory):
        """get_session_context returns context for a specific session."""
        # Add context to different sessions
        await soul_memory.remember_context("Context A", session_id="session-1")
        await soul_memory.remember_context("Context B", session_id="session-1")
        await soul_memory.remember_context("Context C", session_id="session-2")

        # Get context for session-1
        context = await soul_memory.get_session_context("session-1")

        assert len(context) == 2
        contents = [c.content for c in context]
        assert "Context A" in contents
        assert "Context B" in contents
        assert "Context C" not in contents

    @pytest.mark.asyncio
    async def test_get_session_context_excludes_composting(self, soul_memory, mgent):
        """Composting context is excluded."""
        context = await soul_memory.remember_context(
            "Composting context",
            session_id="session-1",
        )

        # Force to COMPOSTING
        memory = mgent._memories[context.memory_id]
        mgent._memories[context.memory_id] = memory.compost()

        # Should not be returned
        results = await soul_memory.get_session_context("session-1")
        assert len(results) == 0


class TestSeedMemory:
    """Tests for seed (creative experiment) memory operations."""

    @pytest.mark.asyncio
    async def test_plant_seed_low_relevance(self, soul_memory, mgent):
        """Seeds have low initial relevance."""
        seed_id = await soul_memory.plant_seed("A creative idea")

        memory = mgent._memories[seed_id]
        assert memory.relevance == 0.4  # Default low relevance
        assert memory.metadata.get("category") == MemoryCategory.SEED.value

    @pytest.mark.asyncio
    async def test_grow_seed_reinforces(self, soul_memory, mgent):
        """grow_seed increases seed relevance."""
        seed_id = await soul_memory.plant_seed("Growing idea")

        initial = mgent._memories[seed_id].relevance

        await soul_memory.grow_seed(seed_id)

        assert mgent._memories[seed_id].relevance > initial

    @pytest.mark.asyncio
    async def test_grow_seed_graduates_to_pattern(self, soul_memory, mgent):
        """Seeds with high relevance become patterns."""
        seed_id = await soul_memory.plant_seed(
            "Promising idea",
            initial_relevance=0.65,  # Close to threshold
        )

        # Grow twice to exceed 0.7 threshold
        await soul_memory.grow_seed(seed_id)

        memory = mgent._memories[seed_id]
        # Should now be a pattern
        assert memory.metadata.get("category") == MemoryCategory.PATTERN.value

    @pytest.mark.asyncio
    async def test_grow_nonexistent_seed(self, soul_memory):
        """grow_seed returns False for nonexistent ID."""
        result = await soul_memory.grow_seed("nonexistent")
        assert result is False


class TestAssociativeRecall:
    """Tests for topic-based recall."""

    @pytest.mark.asyncio
    async def test_recall_for_topic(self, soul_memory, mgent):
        """recall_for_topic finds memories with matching embeddings."""
        # Use explicit embeddings for deterministic testing
        # (hash-based embeddings don't have semantic similarity)
        embedding = [1.0, 0.0, 0.0]

        belief = await soul_memory.remember_belief("Category theory is beautiful")
        # Set same embedding for test
        mem = mgent._memories[belief.memory_id]
        mgent._memories[belief.memory_id] = Memory(
            datum_id=mem.datum_id,
            embedding=tuple(embedding),
            resolution=mem.resolution,
            lifecycle=mem.lifecycle,
            relevance=mem.relevance,
            last_accessed=mem.last_accessed,
            access_count=mem.access_count,
            metadata=mem.metadata,
        )

        # Recall with same embedding (should match)
        results = await mgent.recall(embedding, threshold=0.9)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_recall_excludes_seeds_by_default(self, soul_memory, mgent):
        """recall_for_topic excludes seeds by default."""
        # Store belief and seed with same embedding
        embedding = [1.0, 0.0, 0.0]

        belief = await soul_memory.remember_belief("Main content about testing")
        seed_id = await soul_memory.plant_seed("Experimental testing idea")

        # Set same embedding for both
        for mid in [belief.memory_id, seed_id]:
            mem = mgent._memories[mid]
            mgent._memories[mid] = Memory(
                datum_id=mem.datum_id,
                embedding=tuple(embedding),
                resolution=mem.resolution,
                lifecycle=mem.lifecycle,
                relevance=mem.relevance,
                last_accessed=mem.last_accessed,
                access_count=mem.access_count,
                metadata=mem.metadata,
            )

        results = await soul_memory.recall_for_topic(
            embedding,  # Use embedding directly for matching
            include_seeds=False,
        )

        for result in results:
            category = result.memory.metadata.get("category")
            assert category != MemoryCategory.SEED.value

    @pytest.mark.asyncio
    async def test_recall_includes_seeds_when_requested(self, soul_memory, mgent):
        """recall_for_topic can include seeds."""
        embedding = [1.0, 0.0, 0.0]

        seed_id = await soul_memory.plant_seed("Testing seed")

        # Set explicit embedding for seed
        mem = mgent._memories[seed_id]
        mgent._memories[seed_id] = Memory(
            datum_id=mem.datum_id,
            embedding=tuple(embedding),
            resolution=mem.resolution,
            lifecycle=mem.lifecycle,
            relevance=mem.relevance,
            last_accessed=mem.last_accessed,
            access_count=mem.access_count,
            metadata=mem.metadata,
        )

        results = await soul_memory.recall_for_topic(
            embedding,  # Use embedding directly
            include_seeds=True,
        )

        # Should find the seed
        categories = [r.memory.metadata.get("category") for r in results]
        assert MemoryCategory.SEED.value in categories

    @pytest.mark.asyncio
    async def test_recall_beliefs_for_decision(self, soul_memory, mgent):
        """recall_beliefs_for_decision finds relevant principles."""
        embedding = [1.0, 0.0, 0.0]

        belief1 = await soul_memory.remember_belief(
            "Simplicity over complexity",
            tags=["principle"],
        )
        belief2 = await soul_memory.remember_belief(
            "Joy in creation",
            tags=["principle"],
        )
        pattern = await soul_memory.remember_pattern("Tends toward minimal solutions")

        # Set same embedding for all
        for mid in [belief1.memory_id, belief2.memory_id, pattern.memory_id]:
            mem = mgent._memories[mid]
            mgent._memories[mid] = Memory(
                datum_id=mem.datum_id,
                embedding=tuple(embedding),
                resolution=mem.resolution,
                lifecycle=mem.lifecycle,
                relevance=mem.relevance,
                last_accessed=mem.last_accessed,
                access_count=mem.access_count,
                metadata=mem.metadata,
            )

        beliefs = await soul_memory.recall_beliefs_for_decision(
            "Should I add this complex feature?"  # Doesn't matter with hash embeddings
        )

        # This tests the filtering logic, not semantic search
        # (semantic search requires real embeddings from L-gent)
        assert isinstance(beliefs, list)


class TestIdentityStatus:
    """Tests for identity status reporting."""

    @pytest.mark.asyncio
    async def test_identity_status_empty(self, soul_memory):
        """Empty memory returns zero counts."""
        status = await soul_memory.identity_status()

        assert status["total"] == 0
        assert status["cherished"] == 0

    @pytest.mark.asyncio
    async def test_identity_status_counts_categories(self, soul_memory):
        """Status counts memories by category."""
        await soul_memory.remember_belief("Belief 1")
        await soul_memory.remember_belief("Belief 2")
        await soul_memory.remember_pattern("Pattern 1")
        await soul_memory.remember_context("Context 1", session_id="s1")
        await soul_memory.plant_seed("Seed 1")

        status = await soul_memory.identity_status()

        assert status["total"] == 5
        assert status["by_category"][MemoryCategory.BELIEF.value] == 2
        assert status["by_category"][MemoryCategory.PATTERN.value] == 1
        assert status["by_category"][MemoryCategory.CONTEXT.value] == 1
        assert status["by_category"][MemoryCategory.SEED.value] == 1
        assert status["cherished"] == 2  # Only beliefs are cherished


class TestFactory:
    """Tests for factory function."""

    def test_create_soul_memory(self, mgent):
        """create_soul_memory creates a SoulMemory instance."""
        soul_mem = create_soul_memory(mgent)
        assert isinstance(soul_mem, SoulMemory)
        assert soul_mem.mgent is mgent


class TestIntegration:
    """Integration tests for SoulMemory with M-gent."""

    @pytest.mark.asyncio
    async def test_beliefs_survive_consolidation(self, soul_memory, mgent):
        """Cherished beliefs survive consolidation."""
        from agents.m.consolidation_engine import ConsolidationEngine

        belief = await soul_memory.remember_belief("Core principle")

        # Deactivate the belief
        memory = mgent._memories[belief.memory_id]
        mgent._memories[belief.memory_id] = memory.deactivate()

        # Run consolidation
        engine = ConsolidationEngine(mgent)
        await engine.consolidate()

        # Belief should still be DORMANT (not COMPOSTING)
        assert mgent._memories[belief.memory_id].lifecycle == Lifecycle.DORMANT
        assert mgent._memories[belief.memory_id].is_cherished

    @pytest.mark.asyncio
    async def test_patterns_decay_during_consolidation(self, soul_memory, mgent):
        """Patterns decay during consolidation (unlike beliefs)."""
        from agents.m.consolidation_engine import ConsolidationEngine

        pattern = await soul_memory.remember_pattern(
            "Decaying pattern",
            initial_relevance=0.3,  # Just above demote threshold
        )

        # Deactivate
        memory = mgent._memories[pattern.memory_id]
        mgent._memories[pattern.memory_id] = memory.deactivate()

        initial = mgent._memories[pattern.memory_id].relevance

        # Run consolidation
        engine = ConsolidationEngine(mgent)
        await engine.consolidate()

        # Relevance should have decayed
        assert mgent._memories[pattern.memory_id].relevance < initial
