"""
Tests for AssociativeMemory V-gent Integration (Phase 5).

Tests the V-gent backed similarity search while M-gent manages lifecycle.

Key behaviors tested:
- V-gent stores vectors on remember()
- V-gent search used for recall()
- Lifecycle filtering still works (DREAMING skipped)
- Consolidation cleans up COMPOSTING from V-gent
- Backward compatibility (non-V-gent mode still works)
"""

from __future__ import annotations

import pytest

from agents.d.backends.memory import MemoryBackend
from agents.m.associative import AssociativeMemory
from agents.m.memory import Lifecycle, Memory
from agents.v import MemoryVectorBackend

# === Creation Tests ===


class TestVgentCreation:
    """Test V-gent-backed AssociativeMemory creation."""

    async def test_create_with_vgent(
        self,
        memory_backend: MemoryBackend,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """create_with_vgent returns configured instance."""
        mgent = await AssociativeMemory.create_with_vgent(
            dgent=memory_backend,
            vgent=vgent_memory_backend,
        )

        assert mgent.has_vgent is True
        assert mgent._vgent is vgent_memory_backend

    async def test_standard_creation_has_no_vgent(
        self,
        memory_backend: MemoryBackend,
    ) -> None:
        """Standard creation has no V-gent."""
        mgent = AssociativeMemory(dgent=memory_backend)

        assert mgent.has_vgent is False
        assert mgent._vgent is None


# === Remember Tests (V-gent) ===


class TestVgentRemember:
    """Test remember() with V-gent integration."""

    async def test_remember_adds_to_vgent(
        self,
        vgent_associative_memory: AssociativeMemory,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """Remember adds vector to V-gent."""
        memory_id = await vgent_associative_memory.remember(b"test content")

        # Vector should be in V-gent
        count = await vgent_memory_backend.count()
        assert count == 1

        # Vector ID should match datum ID
        entry = await vgent_memory_backend.get(memory_id)
        assert entry is not None
        assert entry.id == memory_id

    async def test_remember_stores_metadata_in_vgent(
        self,
        vgent_associative_memory: AssociativeMemory,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """Remember stores metadata in V-gent."""
        memory_id = await vgent_associative_memory.remember(
            b"test content",
            metadata={"topic": "testing"},
        )

        entry = await vgent_memory_backend.get(memory_id)
        assert entry is not None
        assert entry.metadata == {"topic": "testing"}

    async def test_remember_maintains_memory_index(
        self,
        vgent_associative_memory: AssociativeMemory,
    ) -> None:
        """Remember also maintains M-gent memory index."""
        memory_id = await vgent_associative_memory.remember(b"test content")

        # Should be in _memories
        memory = await vgent_associative_memory.get(memory_id)
        assert memory is not None
        assert memory.datum_id == memory_id
        assert memory.lifecycle == Lifecycle.ACTIVE


# === Recall Tests (V-gent) ===


class TestVgentRecall:
    """Test recall() with V-gent integration."""

    async def test_recall_uses_vgent_search(
        self,
        populated_vgent_memory: AssociativeMemory,
    ) -> None:
        """Recall finds memories via V-gent search."""
        results = await populated_vgent_memory.recall(
            "Python is a programming language",
            threshold=0.0,
        )

        assert len(results) > 0
        # Best match should have high similarity
        assert results[0].similarity > 0.8

    async def test_recall_respects_limit(
        self,
        populated_vgent_memory: AssociativeMemory,
    ) -> None:
        """Recall respects limit parameter."""
        results = await populated_vgent_memory.recall(
            "test",
            limit=2,
            threshold=0.0,
        )

        assert len(results) <= 2

    async def test_recall_respects_threshold(
        self,
        populated_vgent_memory: AssociativeMemory,
    ) -> None:
        """Recall respects threshold parameter."""
        results = await populated_vgent_memory.recall(
            "completely unrelated query",
            threshold=0.99,
        )

        # Very high threshold should filter most results
        assert all(r.similarity >= 0.99 for r in results)

    async def test_recall_skips_dreaming_memories(
        self,
        vgent_associative_memory: AssociativeMemory,
    ) -> None:
        """Recall skips DREAMING memories (lifecycle filter)."""
        # Add memory
        memory_id = await vgent_associative_memory.remember(b"test content")

        # Manually set to DREAMING
        memory = await vgent_associative_memory.get(memory_id)
        assert memory is not None
        vgent_associative_memory._memories[memory_id] = memory.dream()

        # Recall should not return it
        results = await vgent_associative_memory.recall(
            "test content",
            threshold=0.0,
        )

        # Should be empty (only memory is DREAMING)
        assert len(results) == 0

    async def test_recall_updates_access_count(
        self,
        vgent_associative_memory: AssociativeMemory,
    ) -> None:
        """Recall reinforces accessed memories."""
        memory_id = await vgent_associative_memory.remember(b"test content")

        memory_before = await vgent_associative_memory.get(memory_id)
        assert memory_before is not None
        initial_count = memory_before.access_count

        # Recall it
        await vgent_associative_memory.recall("test content", threshold=0.0)

        # Check access count increased
        memory_after = await vgent_associative_memory.get(memory_id)
        assert memory_after is not None
        assert memory_after.access_count > initial_count


# === Consolidation Tests (V-gent) ===


class TestVgentConsolidation:
    """Test consolidate() with V-gent integration."""

    async def test_consolidate_removes_composting_from_vgent(
        self,
        vgent_associative_memory: AssociativeMemory,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """Consolidation removes COMPOSTING vectors from V-gent."""
        # Add memory
        memory_id = await vgent_associative_memory.remember(b"test content")

        # Verify in V-gent
        count_before = await vgent_memory_backend.count()
        assert count_before == 1

        # Forget it (transitions to COMPOSTING)
        await vgent_associative_memory.forget(memory_id)

        # Vector still in V-gent (not removed until consolidation)
        count_after_forget = await vgent_memory_backend.count()
        assert count_after_forget == 1

        # Consolidate
        await vgent_associative_memory.consolidate()

        # Vector should be removed from V-gent
        count_after_consolidate = await vgent_memory_backend.count()
        assert count_after_consolidate == 0

    async def test_consolidate_preserves_active_vectors(
        self,
        vgent_associative_memory: AssociativeMemory,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """Consolidation preserves ACTIVE memory vectors."""
        memory_id = await vgent_associative_memory.remember(b"active content")

        # Consolidate
        await vgent_associative_memory.consolidate()

        # Vector should still be in V-gent
        count = await vgent_memory_backend.count()
        assert count == 1

        entry = await vgent_memory_backend.get(memory_id)
        assert entry is not None


# === Backward Compatibility Tests ===


class TestBackwardCompatibility:
    """Test that non-V-gent mode still works."""

    async def test_standard_mode_still_works(
        self,
        associative_memory: AssociativeMemory,
    ) -> None:
        """Standard AssociativeMemory (no V-gent) works as before."""
        # Remember
        memory_id = await associative_memory.remember(b"test content")
        assert memory_id is not None

        # Recall
        results = await associative_memory.recall("test content", threshold=0.0)
        assert len(results) >= 1

    async def test_populated_memory_recall_works(
        self,
        populated_memory: AssociativeMemory,
    ) -> None:
        """Populated memory fixture still works."""
        results = await populated_memory.recall("Python", threshold=0.0)
        assert len(results) > 0


# === Parity Tests ===


class TestVgentParity:
    """Test that V-gent mode produces same results as linear mode."""

    async def test_same_results_for_exact_match(
        self,
        memory_backend: MemoryBackend,
        vgent_memory_backend: MemoryVectorBackend,
    ) -> None:
        """V-gent and linear modes produce same results for exact match."""
        # Create both modes
        linear = AssociativeMemory(dgent=MemoryBackend())
        vgent = await AssociativeMemory.create_with_vgent(
            dgent=memory_backend,
            vgent=vgent_memory_backend,
        )

        # Add same content to both
        content = b"Python is a great programming language"
        await linear.remember(content)
        await vgent.remember(content)

        # Query same cue
        cue = "Python is a great programming language"
        linear_results = await linear.recall(cue, threshold=0.0)
        vgent_results = await vgent.recall(cue, threshold=0.0)

        # Both should find it with high similarity
        assert len(linear_results) == 1
        assert len(vgent_results) == 1
        # Similarity scores should be very close (might differ slightly due to float precision)
        assert abs(linear_results[0].similarity - vgent_results[0].similarity) < 0.01
