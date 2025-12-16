"""
Tests for AssociativeMemory.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
"""

from __future__ import annotations

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.m.memory import Memory, Lifecycle
from agents.m.associative import AssociativeMemory


# === Remember Tests ===


class TestRemember:
    """Test remember() method."""

    async def test_remember_returns_id(self, associative_memory: AssociativeMemory) -> None:
        """Remember returns memory ID."""
        memory_id = await associative_memory.remember(b"test content")

        assert memory_id is not None
        assert len(memory_id) > 0

    async def test_remember_stores_in_dgent(self, associative_memory: AssociativeMemory) -> None:
        """Remember stores content in D-gent."""
        memory_id = await associative_memory.remember(b"test content")

        # Should be in D-gent
        datum = await associative_memory.dgent.get(memory_id)
        assert datum is not None
        assert datum.content == "test content"

    async def test_remember_creates_memory_entry(self, associative_memory: AssociativeMemory) -> None:
        """Remember creates Memory entry in index."""
        memory_id = await associative_memory.remember(b"test content")

        # Should be in memory index
        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.datum_id == memory_id
        assert memory.lifecycle == Lifecycle.ACTIVE

    async def test_remember_with_metadata(self, associative_memory: AssociativeMemory) -> None:
        """Remember stores metadata."""
        memory_id = await associative_memory.remember(
            b"test content",
            metadata={"topic": "testing"},
        )

        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.metadata == {"topic": "testing"}

    async def test_remember_with_custom_embedding(self, associative_memory: AssociativeMemory) -> None:
        """Remember uses custom embedding if provided."""
        custom_embedding = [0.1, 0.2, 0.3]
        memory_id = await associative_memory.remember(
            b"test content",
            embedding=custom_embedding,
        )

        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.embedding == tuple(custom_embedding)


# === Recall Tests ===


class TestRecall:
    """Test recall() method."""

    async def test_recall_empty_returns_empty(self, associative_memory: AssociativeMemory) -> None:
        """Recall on empty memory returns empty list."""
        results = await associative_memory.recall("anything")
        assert results == []

    async def test_recall_finds_similar(self, populated_memory: AssociativeMemory) -> None:
        """Recall finds semantically similar memories."""
        # Note: With hash-based embeddings, "similar" means same text
        # Real semantic search requires L-gent embedder
        results = await populated_memory.recall("Python is a programming language")

        assert len(results) > 0
        # Best match should be exact match (similarity near 1.0)
        assert results[0].similarity > 0.9

    async def test_recall_respects_limit(self, populated_memory: AssociativeMemory) -> None:
        """Recall respects limit parameter."""
        results = await populated_memory.recall("test", limit=2)
        assert len(results) <= 2

    async def test_recall_respects_threshold(self, populated_memory: AssociativeMemory) -> None:
        """Recall respects threshold parameter."""
        # Very high threshold should return few/no results
        results = await populated_memory.recall("unrelated query", threshold=0.99)
        # With hash embeddings, unrelated text won't match at 0.99
        assert all(r.similarity >= 0.99 for r in results)

    async def test_recall_includes_datum_content(self, populated_memory: AssociativeMemory) -> None:
        """Recall includes datum content from D-gent."""
        results = await populated_memory.recall("Python", threshold=0.0, limit=1)

        if results:
            assert results[0].datum_content is not None

    async def test_recall_reinforces_memory(self, associative_memory: AssociativeMemory) -> None:
        """Recall reinforces accessed memories."""
        memory_id = await associative_memory.remember(b"test content")
        memory_before = await associative_memory.get(memory_id)
        assert memory_before is not None
        initial_count = memory_before.access_count

        # Recall it
        await associative_memory.recall("test content", threshold=0.0)

        # Check access count increased
        memory_after = await associative_memory.get(memory_id)
        assert memory_after is not None
        assert memory_after.access_count > initial_count


# === Forget Tests ===


class TestForget:
    """Test forget() method."""

    async def test_forget_transitions_to_composting(self, associative_memory: AssociativeMemory) -> None:
        """Forget transitions memory to COMPOSTING."""
        memory_id = await associative_memory.remember(b"test content")

        # Forget it
        result = await associative_memory.forget(memory_id)
        assert result is True

        # Should be COMPOSTING
        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.lifecycle == Lifecycle.COMPOSTING

    async def test_forget_nonexistent_returns_false(self, associative_memory: AssociativeMemory) -> None:
        """Forget nonexistent memory returns False."""
        result = await associative_memory.forget("nonexistent_id")
        assert result is False

    async def test_forget_cherished_returns_false(self, associative_memory: AssociativeMemory) -> None:
        """Cannot forget cherished memories."""
        memory_id = await associative_memory.remember(b"important content")

        # Cherish it
        await associative_memory.cherish(memory_id)

        # Try to forget - should fail
        result = await associative_memory.forget(memory_id)
        assert result is False

        # Should still be active
        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.lifecycle != Lifecycle.COMPOSTING


# === Cherish Tests ===


class TestCherish:
    """Test cherish() method."""

    async def test_cherish_pins_memory(self, associative_memory: AssociativeMemory) -> None:
        """Cherish pins memory from forgetting."""
        memory_id = await associative_memory.remember(b"test content")

        result = await associative_memory.cherish(memory_id)
        assert result is True

        memory = await associative_memory.get(memory_id)
        assert memory is not None
        assert memory.is_cherished
        assert memory.relevance == 1.0

    async def test_cherish_nonexistent_returns_false(self, associative_memory: AssociativeMemory) -> None:
        """Cherish nonexistent memory returns False."""
        result = await associative_memory.cherish("nonexistent_id")
        assert result is False


# === Consolidate Tests ===


class TestConsolidate:
    """Test consolidate() method (sleep cycle)."""

    async def test_consolidate_demotes_low_relevance(self, associative_memory: AssociativeMemory) -> None:
        """Consolidate demotes low-relevance memories."""
        # Create memory
        memory_id = await associative_memory.remember(b"test content")

        # Manually set to DORMANT with low relevance
        memory = await associative_memory.get(memory_id)
        assert memory is not None
        low_relevance = Memory(
            datum_id=memory.datum_id,
            embedding=memory.embedding,
            resolution=memory.resolution,
            lifecycle=Lifecycle.DORMANT,
            relevance=0.1,  # Below demote threshold
            last_accessed=memory.last_accessed,
            access_count=memory.access_count,
            metadata=memory.metadata,
        )
        associative_memory._memories[memory_id] = low_relevance

        # Consolidate
        report = await associative_memory.consolidate()

        # Should have demoted
        assert report.demoted_count >= 1

        # Memory should be COMPOSTING
        updated = await associative_memory.get(memory_id)
        assert updated is not None
        assert updated.lifecycle == Lifecycle.COMPOSTING

    async def test_consolidate_protects_cherished(self, associative_memory: AssociativeMemory) -> None:
        """Consolidate doesn't demote cherished memories."""
        # Create and cherish
        memory_id = await associative_memory.remember(b"important content")
        await associative_memory.cherish(memory_id)

        # Manually set to DORMANT
        memory = await associative_memory.get(memory_id)
        assert memory is not None
        dormant = memory.deactivate()
        associative_memory._memories[memory_id] = dormant

        # Consolidate
        await associative_memory.consolidate()

        # Should not be composting (cherished)
        updated = await associative_memory.get(memory_id)
        assert updated is not None
        assert updated.lifecycle != Lifecycle.COMPOSTING

    async def test_consolidate_returns_report(self, populated_memory: AssociativeMemory) -> None:
        """Consolidate returns a report."""
        # First deactivate all memories
        for memory_id in list(populated_memory._memories.keys()):
            memory = populated_memory._memories[memory_id]
            populated_memory._memories[memory_id] = memory.deactivate()

        report = await populated_memory.consolidate()

        assert report.dreaming_count >= 0
        assert report.demoted_count >= 0
        assert report.duration_ms >= 0


# === Status Tests ===


class TestStatus:
    """Test status() method."""

    async def test_status_empty(self, associative_memory: AssociativeMemory) -> None:
        """Status on empty memory."""
        status = await associative_memory.status()

        assert status.total_memories == 0
        assert status.active_count == 0
        assert status.is_consolidating is False

    async def test_status_populated(self, populated_memory: AssociativeMemory) -> None:
        """Status on populated memory."""
        status = await populated_memory.status()

        assert status.total_memories == 4
        assert status.active_count == 4  # All start as ACTIVE
        assert status.average_relevance > 0
        assert status.average_resolution > 0

    async def test_status_during_consolidation(self, associative_memory: AssociativeMemory) -> None:
        """Status during consolidation."""
        await associative_memory.remember(b"test")

        # Start consolidation manually
        associative_memory._is_consolidating = True

        status = await associative_memory.status()
        assert status.is_consolidating is True


# === By Lifecycle Tests ===


class TestByLifecycle:
    """Test by_lifecycle() method."""

    async def test_by_lifecycle_active(self, populated_memory: AssociativeMemory) -> None:
        """Get ACTIVE memories."""
        active = await populated_memory.by_lifecycle(Lifecycle.ACTIVE)

        assert len(active) == 4  # All should be active

    async def test_by_lifecycle_composting(self, associative_memory: AssociativeMemory) -> None:
        """Get COMPOSTING memories."""
        # Create and forget
        memory_id = await associative_memory.remember(b"test")
        await associative_memory.forget(memory_id)

        composting = await associative_memory.by_lifecycle(Lifecycle.COMPOSTING)
        assert len(composting) == 1
        assert composting[0].datum_id == memory_id


# === Extended Operations Tests ===


class TestExtendedOperations:
    """Test extended (optional) operations."""

    async def test_exists(self, associative_memory: AssociativeMemory) -> None:
        """Test exists() method."""
        memory_id = await associative_memory.remember(b"test")

        assert await associative_memory.exists(memory_id) is True
        assert await associative_memory.exists("nonexistent") is False

    async def test_count(self, populated_memory: AssociativeMemory) -> None:
        """Test count() method."""
        count = await populated_memory.count()
        assert count == 4

    async def test_decay_all(self, populated_memory: AssociativeMemory) -> None:
        """Test decay_all() method."""
        # Get initial relevance
        memories_before = list(populated_memory._memories.values())
        initial_relevance = sum(m.relevance for m in memories_before) / len(memories_before)

        # Decay all
        decayed = await populated_memory.decay_all(factor=0.5)
        assert decayed == 4

        # Check relevance decreased
        memories_after = list(populated_memory._memories.values())
        final_relevance = sum(m.relevance for m in memories_after) / len(memories_after)
        assert final_relevance < initial_relevance

    async def test_degrade_composting(self, associative_memory: AssociativeMemory) -> None:
        """Test degrade_composting() method."""
        # Create and forget
        memory_id = await associative_memory.remember(b"test")
        await associative_memory.forget(memory_id)

        # Check initial resolution
        memory_before = await associative_memory.get(memory_id)
        assert memory_before is not None
        assert memory_before.resolution == 1.0

        # Degrade
        degraded = await associative_memory.degrade_composting(factor=0.5)
        assert degraded == 1

        # Check resolution decreased
        memory_after = await associative_memory.get(memory_id)
        assert memory_after is not None
        assert memory_after.resolution == 0.5
