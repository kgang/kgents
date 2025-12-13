"""
Tests for holographic memory crystal.

Verifies the key holographic property: 50% compression preserves ALL concepts
at 50% resolution, rather than deleting 50% of concepts.
"""

from __future__ import annotations

import math
import random
from datetime import datetime, timedelta

import pytest
from agents.m.crystal import (
    CrystalPattern,
    MemoryCrystal,
    ResonanceMatch,
    create_crystal,
)


def random_embedding(dim: int = 64, seed: int | None = None) -> list[float]:
    """Generate a random normalized embedding."""
    if seed is not None:
        random.seed(seed)
    vec = [random.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm > 0 else vec


class TestMemoryCrystal:
    """Core memory crystal tests."""

    def test_store_creates_pattern(self) -> None:
        """Storing creates a CrystalPattern with correct metadata."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding = random_embedding(64, seed=42)

        pattern = crystal.store("concept_a", "Test content", embedding)

        assert pattern.concept_id == "concept_a"
        assert pattern.content == "Test content"
        assert pattern.resolution == 1.0
        assert pattern.access_count == 0
        assert "concept_a" in crystal.concepts

    def test_store_adds_to_hot_patterns(self) -> None:
        """Newly stored patterns are hot."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding = random_embedding(64)

        crystal.store("concept_a", "Content", embedding)

        assert "concept_a" in crystal.hot_patterns

    def test_retrieve_similar_embedding(self) -> None:
        """Retrieve finds similar embeddings."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding = random_embedding(64, seed=42)

        crystal.store("concept_a", "Test content", embedding)

        # Query with same embedding should match
        results = crystal.retrieve(embedding, threshold=0.5)
        assert len(results) >= 1
        assert results[0].concept_id == "concept_a"
        assert results[0].similarity > 0.9  # Very similar

    def test_retrieve_dissimilar_embedding(self) -> None:
        """Dissimilar embeddings have low similarity."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding_a = random_embedding(64, seed=42)
        embedding_b = random_embedding(64, seed=123)  # Different seed = different vec

        crystal.store("concept_a", "Content A", embedding_a)

        # Query with different embedding - use very low threshold
        results = crystal.retrieve(embedding_b, threshold=-1.0)
        assert len(results) >= 1
        # Similarity should be lower (random vectors are roughly orthogonal)
        # But not zero since we're using cosine similarity
        assert results[0].similarity < 0.9

    def test_retrieve_updates_access_count(self) -> None:
        """Retrieval increments access count."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding = random_embedding(64, seed=42)

        crystal.store("concept_a", "Content", embedding)
        pattern = crystal.get_pattern("concept_a")
        assert pattern is not None
        assert pattern.access_count == 0

        crystal.retrieve(embedding, threshold=0.5)
        pattern = crystal.get_pattern("concept_a")
        assert pattern is not None
        assert pattern.access_count == 1

        crystal.retrieve(embedding, threshold=0.5)
        pattern = crystal.get_pattern("concept_a")
        assert pattern is not None
        assert pattern.access_count == 2

    def test_retrieve_content(self) -> None:
        """Can retrieve stored content by concept_id."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        embedding = random_embedding(64)

        crystal.store("concept_a", "My stored content", embedding)

        content = crystal.retrieve_content("concept_a")
        assert content == "My stored content"

    def test_retrieve_content_not_found(self) -> None:
        """Retrieve content returns None for unknown concept."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        content = crystal.retrieve_content("nonexistent")
        assert content is None


class TestHolographicProperty:
    """Tests verifying the core holographic property: compression preserves all."""

    def test_compression_preserves_all_concepts(self) -> None:
        """50% compression should NOT lose 50% of concepts."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        # Store 10 concepts
        for i in range(10):
            embedding = random_embedding(64, seed=i)
            crystal.store(f"concept_{i}", f"Content {i}", embedding)

        assert len(crystal.concepts) == 10

        # Compress to 50%
        compressed = crystal.compress(ratio=0.5)

        # ALL concepts should still exist (holographic property!)
        assert len(compressed.concepts) == 10
        for i in range(10):
            assert f"concept_{i}" in compressed.concepts

    def test_compression_reduces_resolution(self) -> None:
        """Compression reduces resolution of all concepts uniformly."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        for i in range(5):
            embedding = random_embedding(64, seed=i)
            crystal.store(f"concept_{i}", f"Content {i}", embedding)

        # All at full resolution
        for cid in crystal.concepts:
            assert crystal.resolution_levels[cid] == 1.0

        # Compress to 50%
        compressed = crystal.compress(ratio=0.5)

        # All at half resolution
        for cid in compressed.concepts:
            assert compressed.resolution_levels[cid] == pytest.approx(0.5)

    def test_compression_reduces_dimension(self) -> None:
        """Compression reduces the vector dimension."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=100)
        crystal.store("concept_a", "Content", random_embedding(100))

        compressed = crystal.compress(ratio=0.5)

        assert compressed.dimension == 50

    def test_multiple_compressions_stack(self) -> None:
        """Multiple compressions further reduce resolution."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        # First compression: 50%
        compressed1 = crystal.compress(ratio=0.5)
        assert compressed1.resolution_levels["concept_a"] == pytest.approx(0.5)

        # Second compression: another 50%
        compressed2 = compressed1.compress(ratio=0.5)
        assert compressed2.resolution_levels["concept_a"] == pytest.approx(0.25)

        # Concept still exists!
        assert "concept_a" in compressed2.concepts

    def test_compression_preserves_content(self) -> None:
        """Compression preserves the actual content."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Important information", random_embedding(64))

        compressed = crystal.compress(ratio=0.5)

        content = compressed.retrieve_content("concept_a")
        assert content == "Important information"


class TestDemotePromote:
    """Tests for individual concept resolution adjustment."""

    def test_demote_reduces_resolution(self) -> None:
        """Demote reduces a concept's resolution."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        assert crystal.resolution_levels["concept_a"] == 1.0

        crystal.demote("concept_a", factor=0.5)

        assert crystal.resolution_levels["concept_a"] == pytest.approx(0.5)

    def test_demote_removes_from_hot(self) -> None:
        """Demoting below threshold removes from hot patterns."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        assert "concept_a" in crystal.hot_patterns

        # Demote significantly
        crystal.demote("concept_a", factor=0.3)

        assert "concept_a" not in crystal.hot_patterns

    def test_promote_increases_resolution(self) -> None:
        """Promote increases a concept's resolution."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))
        crystal.demote("concept_a", factor=0.5)  # Now at 0.5

        crystal.promote("concept_a", factor=1.5)

        assert crystal.resolution_levels["concept_a"] == pytest.approx(0.75)

    def test_promote_capped_at_one(self) -> None:
        """Resolution cannot exceed 1.0."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        crystal.promote("concept_a", factor=2.0)  # Try to exceed 1.0

        assert crystal.resolution_levels["concept_a"] == 1.0

    def test_promote_adds_to_hot(self) -> None:
        """Promoting above threshold adds to hot patterns."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))
        crystal.demote("concept_a", factor=0.3)  # Remove from hot

        assert "concept_a" not in crystal.hot_patterns

        # Promote back
        crystal.promote("concept_a", factor=3.0)  # 0.3 * 3 = 0.9 > 0.7 threshold

        assert "concept_a" in crystal.hot_patterns

    def test_demote_nonexistent_is_noop(self) -> None:
        """Demoting nonexistent concept is a no-op."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        crystal.demote("nonexistent", factor=0.5)  # Should not raise

    def test_promote_nonexistent_is_noop(self) -> None:
        """Promoting nonexistent concept is a no-op."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        crystal.promote("nonexistent", factor=1.5)  # Should not raise


class TestDemotePromoteCycle:
    """Tests for hot/cold memory promotion cycles."""

    def test_full_cycle(self) -> None:
        """Full cycle: store (hot) -> demote (cold) -> promote (hot)."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("test_concept", "Content", random_embedding(64))

        # Initially hot at full resolution
        assert "test_concept" in crystal.hot_patterns
        assert crystal.resolution_levels["test_concept"] == 1.0

        # Demote significantly to get below 0.5 threshold (0.5 * 0.3 = 0.15)
        crystal.demote("test_concept", factor=0.3)
        assert "test_concept" not in crystal.hot_patterns
        assert crystal.resolution_levels["test_concept"] == pytest.approx(0.3)

        # Promote back (0.3 * 4.0 = 1.2 -> capped at 1.0, which is > 0.7 threshold)
        crystal.promote("test_concept", factor=4.0)
        assert "test_concept" in crystal.hot_patterns
        assert crystal.resolution_levels["test_concept"] == 1.0  # Capped

    def test_gradual_decay(self) -> None:
        """Gradual decay through repeated demotions."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        # Simulate gradual forgetting
        for _ in range(5):
            crystal.demote("concept_a", factor=0.8)

        # Resolution should be 0.8^5 ≈ 0.328
        expected = 0.8**5
        assert crystal.resolution_levels["concept_a"] == pytest.approx(
            expected, rel=0.01
        )

        # Concept still exists (holographic property!)
        assert "concept_a" in crystal.concepts


class TestStats:
    """Tests for crystal statistics."""

    def test_stats_empty_crystal(self) -> None:
        """Stats for empty crystal."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        stats = crystal.stats()

        assert stats["dimension"] == 64
        assert stats["concept_count"] == 0
        assert stats["hot_count"] == 0
        assert stats["avg_resolution"] == 0.0

    def test_stats_with_concepts(self) -> None:
        """Stats with stored concepts."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        for i in range(5):
            crystal.store(f"concept_{i}", f"Content {i}", random_embedding(64, seed=i))

        stats = crystal.stats()

        assert stats["concept_count"] == 5
        assert stats["hot_count"] == 5
        assert stats["avg_resolution"] == 1.0


class TestCreateCrystal:
    """Tests for factory function."""

    def test_create_crystal_default(self) -> None:
        """Create crystal with defaults."""
        crystal = create_crystal(dimension=64)
        assert crystal.dimension == 64

    def test_create_crystal_no_numpy(self) -> None:
        """Create pure Python crystal."""
        crystal = create_crystal(dimension=64, use_numpy=False)
        assert isinstance(crystal, MemoryCrystal)


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_embedding(self) -> None:
        """Handle empty embedding (edge case)."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        # Empty embedding should be handled gracefully
        pattern = crystal.store("concept_a", "Content", [])
        assert pattern is not None
        assert len(pattern.embedding) == 64  # Padded to dimension

    def test_small_embedding(self) -> None:
        """Handle embedding smaller than dimension."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        small_embedding = [1.0, 2.0, 3.0]  # Only 3 elements

        pattern = crystal.store("concept_a", "Content", small_embedding)

        assert len(pattern.embedding) == 64  # Padded

    def test_large_embedding(self) -> None:
        """Handle embedding larger than dimension."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        large_embedding = [1.0] * 128  # Larger than dimension

        pattern = crystal.store("concept_a", "Content", large_embedding)

        assert len(pattern.embedding) == 64  # Truncated

    def test_compression_ratio_validation(self) -> None:
        """Invalid compression ratios raise ValueError."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)
        crystal.store("concept_a", "Content", random_embedding(64))

        with pytest.raises(ValueError):
            crystal.compress(ratio=0.0)

        with pytest.raises(ValueError):
            crystal.compress(ratio=-0.5)

        with pytest.raises(ValueError):
            crystal.compress(ratio=1.5)

    def test_extreme_compression(self) -> None:
        """Very small compression ratio still works."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=100)
        crystal.store("concept_a", "Content", random_embedding(100))

        compressed = crystal.compress(ratio=0.1)

        assert compressed.dimension == 10
        assert "concept_a" in compressed.concepts
        assert compressed.resolution_levels["concept_a"] == pytest.approx(0.1)


class TestCrystalPattern:
    """Tests for CrystalPattern dataclass."""

    def test_pattern_access(self) -> None:
        """Pattern access updates metadata."""
        pattern = CrystalPattern(
            concept_id="test",
            content="Content",
            embedding=[0.1, 0.2, 0.3],
        )

        original_time = pattern.last_accessed
        original_count = pattern.access_count

        pattern.access()

        assert pattern.access_count == original_count + 1
        assert pattern.last_accessed >= original_time


class TestMultipleConcepts:
    """Tests with multiple concepts."""

    def test_store_multiple_retrieve_one(self) -> None:
        """Store multiple, retrieve specific."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        embeddings = [random_embedding(64, seed=i) for i in range(5)]
        for i, emb in enumerate(embeddings):
            crystal.store(f"concept_{i}", f"Content {i}", emb)

        # Query with embedding[2] should return concept_2 first
        results = crystal.retrieve(embeddings[2], threshold=0.5)

        assert len(results) >= 1
        assert results[0].concept_id == "concept_2"
        assert results[0].similarity > 0.95

    def test_retrieve_limit(self) -> None:
        """Retrieve respects limit parameter."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        for i in range(20):
            crystal.store(f"concept_{i}", f"Content {i}", random_embedding(64, seed=i))

        # Low threshold to get all, but limit to 5
        results = crystal.retrieve([0.5] * 64, threshold=0.0, limit=5)

        assert len(results) <= 5

    def test_independent_resolutions(self) -> None:
        """Concepts can have independent resolution levels."""
        crystal: MemoryCrystal[str] = MemoryCrystal(dimension=64)

        crystal.store("concept_a", "A", random_embedding(64, seed=1))
        crystal.store("concept_b", "B", random_embedding(64, seed=2))
        crystal.store("concept_c", "C", random_embedding(64, seed=3))

        # Demote only A
        crystal.demote("concept_a", factor=0.5)

        assert crystal.resolution_levels["concept_a"] == pytest.approx(0.5)
        assert crystal.resolution_levels["concept_b"] == 1.0
        assert crystal.resolution_levels["concept_c"] == 1.0
