"""
Tests for Memory dataclass.

Part of the Data Architecture Rewrite (plans/data-architecture-rewrite.md).
"""

from __future__ import annotations

import time

import pytest

from agents.m.memory import Lifecycle, Memory, simple_embedding

# === Creation Tests ===


class TestMemoryCreation:
    """Test Memory creation and validation."""

    def test_create_basic(self) -> None:
        """Can create a basic memory."""
        memory = Memory.create(
            datum_id="test_001",
            embedding=[0.1, 0.2, 0.3],
        )

        assert memory.datum_id == "test_001"
        assert memory.embedding == (0.1, 0.2, 0.3)
        assert memory.resolution == 1.0
        assert memory.lifecycle == Lifecycle.ACTIVE
        assert memory.relevance == 1.0
        assert memory.access_count == 0

    def test_create_with_metadata(self) -> None:
        """Can create memory with metadata."""
        memory = Memory.create(
            datum_id="test_002",
            embedding=[0.1, 0.2],
            metadata={"topic": "test"},
        )

        assert memory.metadata == {"topic": "test"}

    def test_embedding_list_to_tuple(self) -> None:
        """Embedding list is converted to tuple."""
        memory = Memory.create(
            datum_id="test_003",
            embedding=[0.1, 0.2, 0.3],
        )

        # Should be tuple, not list
        assert isinstance(memory.embedding, tuple)
        assert memory.embedding == (0.1, 0.2, 0.3)

    def test_resolution_clamped(self) -> None:
        """Resolution is clamped to [0, 1]."""
        # Over 1.0
        memory = Memory(
            datum_id="test_004",
            embedding=(0.1,),
            resolution=1.5,
        )
        assert memory.resolution == 1.0

        # Under 0.0
        memory2 = Memory(
            datum_id="test_005",
            embedding=(0.1,),
            resolution=-0.5,
        )
        assert memory2.resolution == 0.0

    def test_relevance_clamped(self) -> None:
        """Relevance is clamped to [0, 1]."""
        # Over 1.0
        memory = Memory(
            datum_id="test_006",
            embedding=(0.1,),
            relevance=1.5,
        )
        assert memory.relevance == 1.0

        # Under 0.0
        memory2 = Memory(
            datum_id="test_007",
            embedding=(0.1,),
            relevance=-0.5,
        )
        assert memory2.relevance == 0.0

    def test_memory_is_frozen(self) -> None:
        """Memory is immutable (frozen dataclass)."""
        memory = Memory.create(
            datum_id="test_008",
            embedding=[0.1],
        )

        with pytest.raises(AttributeError):
            memory.datum_id = "changed"  # type: ignore


# === Lifecycle Tests ===


class TestLifecycleTransitions:
    """Test lifecycle state transitions."""

    def test_activate(self, memory_basic: Memory) -> None:
        """Can activate a memory."""
        # Start as ACTIVE
        assert memory_basic.lifecycle == Lifecycle.ACTIVE

        # Deactivate first
        dormant = memory_basic.deactivate()
        assert dormant.lifecycle == Lifecycle.DORMANT

        # Now activate
        active = dormant.activate()
        assert active.lifecycle == Lifecycle.ACTIVE
        assert active.access_count == dormant.access_count + 1

    def test_deactivate(self, memory_basic: Memory) -> None:
        """Can deactivate a memory."""
        dormant = memory_basic.deactivate()
        assert dormant.lifecycle == Lifecycle.DORMANT

    def test_dream(self, memory_basic: Memory) -> None:
        """Can enter dreaming state."""
        dreaming = memory_basic.dream()
        assert dreaming.lifecycle == Lifecycle.DREAMING

    def test_wake_from_dreaming(self) -> None:
        """Can wake from dreaming to dormant."""
        memory = Memory.create(
            datum_id="test_009",
            embedding=[0.1],
            lifecycle=Lifecycle.DREAMING,
        )

        woken = memory.wake()
        assert woken.lifecycle == Lifecycle.DORMANT

    def test_wake_from_non_dreaming_is_noop(self, memory_basic: Memory) -> None:
        """Wake from non-dreaming state is no-op."""
        assert memory_basic.lifecycle == Lifecycle.ACTIVE
        still_active = memory_basic.wake()
        assert still_active.lifecycle == Lifecycle.ACTIVE

    def test_compost(self, memory_basic: Memory) -> None:
        """Can enter composting state."""
        composting = memory_basic.compost()
        assert composting.lifecycle == Lifecycle.COMPOSTING


# === Resolution Tests ===


class TestResolution:
    """Test resolution (graceful degradation)."""

    def test_degrade(self, memory_basic: Memory) -> None:
        """Can degrade resolution."""
        assert memory_basic.resolution == 1.0

        degraded = memory_basic.degrade(factor=0.5)
        assert degraded.resolution == 0.5

    def test_degrade_multiple_times(self, memory_basic: Memory) -> None:
        """Degradation compounds."""
        degraded1 = memory_basic.degrade(factor=0.5)
        degraded2 = degraded1.degrade(factor=0.5)

        assert degraded2.resolution == 0.25

    def test_degrade_floors_at_zero(self, memory_basic: Memory) -> None:
        """Resolution can't go below 0."""
        # Degrade many times
        m = memory_basic
        for _ in range(20):
            m = m.degrade(factor=0.5)

        assert m.resolution >= 0.0


# === Relevance Tests ===


class TestRelevance:
    """Test relevance (importance score)."""

    def test_reinforce(self, memory_basic: Memory) -> None:
        """Can reinforce relevance."""
        # Start at 1.0
        assert memory_basic.relevance == 1.0

        # Lower it first
        decayed = memory_basic.decay(factor=0.5)
        assert decayed.relevance == 0.5

        # Now reinforce
        reinforced = decayed.reinforce(boost=0.2)
        assert reinforced.relevance == 0.7
        assert reinforced.access_count == decayed.access_count + 1

    def test_decay(self, memory_basic: Memory) -> None:
        """Can decay relevance."""
        decayed = memory_basic.decay(factor=0.9)
        assert decayed.relevance == 0.9

    def test_cherish(self, memory_basic: Memory) -> None:
        """Can cherish a memory."""
        # First decay it
        decayed = memory_basic.decay(factor=0.5)
        assert decayed.relevance == 0.5

        # Cherish
        cherished = decayed.cherish()
        assert cherished.relevance == 1.0
        assert cherished.is_cherished

    def test_is_cherished_checks_metadata(self) -> None:
        """is_cherished checks metadata."""
        memory = Memory.create(
            datum_id="test_010",
            embedding=[0.1],
            metadata={"cherished": "true"},
        )
        assert memory.is_cherished

        memory2 = Memory.create(
            datum_id="test_011",
            embedding=[0.1],
        )
        assert not memory2.is_cherished


# === Similarity Tests ===


class TestSimilarity:
    """Test semantic similarity computation."""

    def test_similarity_identical(self) -> None:
        """Identical embeddings have similarity 1.0."""
        embedding = (0.5, 0.5, 0.5)
        memory = Memory.create(
            datum_id="test_012",
            embedding=embedding,
        )

        similarity = memory.similarity(embedding)
        assert abs(similarity - 1.0) < 0.001

    def test_similarity_orthogonal(self) -> None:
        """Orthogonal embeddings have similarity 0.0."""
        memory = Memory.create(
            datum_id="test_013",
            embedding=(1.0, 0.0),
        )

        similarity = memory.similarity((0.0, 1.0))
        assert abs(similarity) < 0.001

    def test_similarity_opposite(self) -> None:
        """Opposite embeddings have similarity -1.0."""
        memory = Memory.create(
            datum_id="test_014",
            embedding=(1.0, 0.0),
        )

        similarity = memory.similarity((-1.0, 0.0))
        assert abs(similarity - (-1.0)) < 0.001

    def test_similarity_handles_list(self) -> None:
        """Similarity accepts list (converts to tuple)."""
        memory = Memory.create(
            datum_id="test_015",
            embedding=(0.5, 0.5),
        )

        # Pass as list
        similarity = memory.similarity([0.5, 0.5])
        assert abs(similarity - 1.0) < 0.001

    def test_similarity_mismatched_dimensions(self) -> None:
        """Mismatched dimensions return 0.0."""
        memory = Memory.create(
            datum_id="test_016",
            embedding=(0.5, 0.5),
        )

        similarity = memory.similarity((0.5, 0.5, 0.5))
        assert similarity == 0.0


# === Serialization Tests ===


class TestSerialization:
    """Test JSON serialization."""

    def test_to_dict(self, memory_basic: Memory) -> None:
        """Can serialize to dict."""
        d = memory_basic.to_dict()

        assert d["datum_id"] == memory_basic.datum_id
        assert d["embedding"] == list(memory_basic.embedding)
        assert d["resolution"] == memory_basic.resolution
        assert d["lifecycle"] == memory_basic.lifecycle.value
        assert d["relevance"] == memory_basic.relevance

    def test_from_dict(self, memory_basic: Memory) -> None:
        """Can deserialize from dict."""
        d = memory_basic.to_dict()
        restored = Memory.from_dict(d)

        assert restored.datum_id == memory_basic.datum_id
        assert restored.embedding == memory_basic.embedding
        assert restored.resolution == memory_basic.resolution
        assert restored.lifecycle == memory_basic.lifecycle
        assert restored.relevance == memory_basic.relevance

    def test_roundtrip(self, memory_basic: Memory) -> None:
        """Roundtrip preserves data."""
        d = memory_basic.to_dict()
        restored = Memory.from_dict(d)

        assert restored == memory_basic


# === Simple Embedding Tests ===


class TestSimpleEmbedding:
    """Test hash-based pseudo-embeddings."""

    def test_deterministic(self) -> None:
        """Same text produces same embedding."""
        e1 = simple_embedding("test content")
        e2 = simple_embedding("test content")

        assert e1 == e2

    def test_different_text_different_embedding(self) -> None:
        """Different text produces different embedding."""
        e1 = simple_embedding("test content")
        e2 = simple_embedding("different content")

        assert e1 != e2

    def test_correct_dimension(self) -> None:
        """Output has correct dimension."""
        e = simple_embedding("test", dim=64)
        assert len(e) == 64

        e2 = simple_embedding("test", dim=128)
        assert len(e2) == 128

    def test_values_in_range(self) -> None:
        """Values are in [-1, 1] range."""
        e = simple_embedding("test content")

        for value in e:
            assert -1.0 <= value <= 1.0
