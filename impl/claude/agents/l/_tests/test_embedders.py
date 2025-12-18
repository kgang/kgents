"""
Tests for L-gent advanced embedders (Phase 6).

Tests cover:
- SentenceTransformerEmbedder (if available)
- OpenAIEmbedder (if available)
- CachedEmbedder
- create_best_available_embedder
- compare_embedders

Tests are written to gracefully handle missing dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from agents.l.embedders import (
    OPENAI_AVAILABLE,
    SENTENCE_TRANSFORMERS_AVAILABLE,
    CachedEmbedder,
    EmbeddingMetadata,
    compare_embedders,
    create_best_available_embedder,
)

if SENTENCE_TRANSFORMERS_AVAILABLE:
    from agents.l.embedders import SentenceTransformerEmbedder

if OPENAI_AVAILABLE:
    from agents.l.embedders import OpenAIEmbedder

from agents.l.semantic import SimpleEmbedder

# ============================================================================
# SentenceTransformerEmbedder Tests
# ============================================================================


@pytest.mark.skipif(
    not SENTENCE_TRANSFORMERS_AVAILABLE, reason="sentence-transformers not installed"
)
class TestSentenceTransformerEmbedder:
    """Tests for SentenceTransformerEmbedder."""

    @pytest.mark.asyncio
    async def test_embed_simple(self) -> None:
        """Test basic embedding."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        vector = await embedder.embed("find agents for data processing")

        assert isinstance(vector, list)
        assert len(vector) == embedder.dimension
        assert all(isinstance(x, float) for x in vector)

    @pytest.mark.asyncio
    async def test_dimension(self) -> None:
        """Test dimension property."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        assert embedder.dimension == 384  # all-MiniLM-L6-v2 is 384-dim

    @pytest.mark.asyncio
    async def test_metadata(self) -> None:
        """Test metadata property."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        metadata = embedder.metadata

        assert isinstance(metadata, EmbeddingMetadata)
        assert metadata.name == "all-MiniLM-L6-v2"
        assert metadata.dimension == 384
        assert metadata.provider == "sentence-transformers"
        assert metadata.supports_batch is True

    @pytest.mark.asyncio
    async def test_normalization(self) -> None:
        """Test that embeddings are normalized."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2", normalize=True)
        vector = await embedder.embed("test")

        # Check L2 norm is ~1.0 (normalized)
        import math

        magnitude = math.sqrt(sum(x * x for x in vector))
        assert abs(magnitude - 1.0) < 0.01  # Allow small floating point error

    @pytest.mark.asyncio
    async def test_embed_batch(self) -> None:
        """Test batch embedding."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        texts = ["first text", "second text", "third text"]
        vectors = await embedder.embed_batch(texts)

        assert len(vectors) == 3
        assert all(len(v) == embedder.dimension for v in vectors)

    @pytest.mark.asyncio
    async def test_semantic_similarity(self) -> None:
        """Test that semantically similar texts have higher similarity."""
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")

        vec1 = await embedder.embed("cat")
        vec2 = await embedder.embed("kitten")
        vec3 = await embedder.embed("database")

        # Compute cosine similarity
        def cosine_sim(a: list[float], b: list[float]) -> float:
            import math

            dot = sum(x * y for x, y in zip(a, b))
            mag_a = math.sqrt(sum(x * x for x in a))
            mag_b = math.sqrt(sum(y * y for y in b))
            return dot / (mag_a * mag_b) if mag_a and mag_b else 0.0

        sim_cat_kitten = cosine_sim(vec1, vec2)
        sim_cat_database = cosine_sim(vec1, vec3)

        # cat and kitten should be more similar than cat and database
        assert sim_cat_kitten > sim_cat_database


# ============================================================================
# OpenAIEmbedder Tests
# ============================================================================


@pytest.mark.skipif(not OPENAI_AVAILABLE, reason="openai not installed")
class TestOpenAIEmbedder:
    """Tests for OpenAIEmbedder.

    Note: These tests require OPENAI_API_KEY to be set and will make API calls.
    Skip if running in CI without API key.
    """

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    @pytest.mark.asyncio
    async def test_embed_simple(self) -> None:
        """Test basic embedding."""
        embedder = OpenAIEmbedder(model="text-embedding-3-small")
        vector = await embedder.embed("find agents for data processing")

        assert isinstance(vector, list)
        assert len(vector) == embedder.dimension
        assert all(isinstance(x, float) for x in vector)

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    @pytest.mark.asyncio
    async def test_dimension(self) -> None:
        """Test dimension property."""
        embedder = OpenAIEmbedder(model="text-embedding-3-small")
        # Dimension should be detected on first embed
        await embedder.embed("test")
        assert embedder.dimension == 1536  # text-embedding-3-small is 1536-dim

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    @pytest.mark.asyncio
    async def test_metadata(self) -> None:
        """Test metadata property."""
        embedder = OpenAIEmbedder(model="text-embedding-3-small")
        metadata = embedder.metadata

        assert isinstance(metadata, EmbeddingMetadata)
        assert metadata.name == "text-embedding-3-small"
        assert metadata.provider == "openai"
        assert metadata.supports_batch is True

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    @pytest.mark.asyncio
    async def test_embed_batch(self) -> None:
        """Test batch embedding."""
        embedder = OpenAIEmbedder(model="text-embedding-3-small")
        texts = ["first text", "second text"]
        vectors = await embedder.embed_batch(texts)

        assert len(vectors) == 2
        assert all(len(v) == embedder.dimension for v in vectors)


# ============================================================================
# CachedEmbedder Tests
# ============================================================================


class TestCachedEmbedder:
    """Tests for CachedEmbedder."""

    @pytest.mark.asyncio
    async def test_cache_hit(self, tmp_path: Path) -> None:
        """Test that cache is hit on repeated queries."""
        cache_path = str(tmp_path / "cache.json")
        base_embedder = SimpleEmbedder(dimension=128)
        await base_embedder.fit(["test document"])

        embedder = CachedEmbedder(base_embedder, cache_path=cache_path)

        # First call: cache miss
        vec1 = await embedder.embed("test query")

        # Second call: cache hit
        vec2 = await embedder.embed("test query")

        assert vec1 == vec2

    @pytest.mark.asyncio
    async def test_cache_persistence(self, tmp_path: Path) -> None:
        """Test that cache persists across instances."""
        cache_path = str(tmp_path / "cache.json")
        base_embedder = SimpleEmbedder(dimension=128)
        await base_embedder.fit(["test document"])

        # First instance
        embedder1 = CachedEmbedder(base_embedder, cache_path=cache_path)
        vec1 = await embedder1.embed("test query")

        # Second instance (should load from disk)
        embedder2 = CachedEmbedder(base_embedder, cache_path=cache_path)
        vec2 = await embedder2.embed("test query")

        assert vec1 == vec2

    @pytest.mark.asyncio
    async def test_batch_caching(self, tmp_path: Path) -> None:
        """Test batch embedding with partial cache hits."""
        cache_path = str(tmp_path / "cache.json")
        base_embedder = SimpleEmbedder(dimension=128)
        await base_embedder.fit(["test document"])

        embedder = CachedEmbedder(base_embedder, cache_path=cache_path)

        # Cache first text
        await embedder.embed("first")

        # Batch with one cached, one uncached
        vectors = await embedder.embed_batch(["first", "second"])

        assert len(vectors) == 2
        assert all(len(v) == 128 for v in vectors)

    @pytest.mark.asyncio
    async def test_dimension_passthrough(self, tmp_path: Path) -> None:
        """Test that dimension is passed through from base embedder."""
        cache_path = str(tmp_path / "cache.json")
        base_embedder = SimpleEmbedder(dimension=256)

        embedder = CachedEmbedder(base_embedder, cache_path=cache_path)
        assert embedder.dimension == 256

    @pytest.mark.asyncio
    async def test_corrupted_cache_recovery(self, tmp_path: Path) -> None:
        """Test recovery from corrupted cache file."""
        cache_path = str(tmp_path / "cache.json")

        # Write corrupted cache
        with open(cache_path, "w") as f:
            f.write("not valid json{")

        base_embedder = SimpleEmbedder(dimension=128)
        await base_embedder.fit(["test"])

        # Should not crash, just start with empty cache
        embedder = CachedEmbedder(base_embedder, cache_path=cache_path)
        vector = await embedder.embed("test")

        assert isinstance(vector, list)
        assert len(vector) == 128


# ============================================================================
# Utility Function Tests
# ============================================================================


class TestCreateBestAvailableEmbedder:
    """Tests for create_best_available_embedder."""

    def test_returns_embedder(self) -> None:
        """Test that it returns an embedder."""
        embedder = create_best_available_embedder()
        assert hasattr(embedder, "embed")
        assert hasattr(embedder, "dimension")

    def test_prefer_sentence_transformers(self) -> None:
        """Test preference for sentence-transformers."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            embedder = create_best_available_embedder(prefer="sentence-transformers")
            assert isinstance(embedder, SentenceTransformerEmbedder)
        else:
            # Should fall back to SimpleEmbedder
            embedder = create_best_available_embedder(prefer="sentence-transformers")
            assert isinstance(embedder, SimpleEmbedder)

    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
    def test_prefer_openai(self) -> None:
        """Test preference for OpenAI."""
        if OPENAI_AVAILABLE:
            embedder = create_best_available_embedder(prefer="openai")
            assert isinstance(embedder, OpenAIEmbedder)


class TestCompareEmbedders:
    """Tests for compare_embedders utility."""

    @pytest.mark.asyncio
    async def test_compare_simple(self) -> None:
        """Test comparing multiple embedders."""
        embedder1 = SimpleEmbedder(dimension=64)
        embedder2 = SimpleEmbedder(dimension=128)

        await embedder1.fit(["test"])
        await embedder2.fit(["test"])

        results = await compare_embedders(
            "test query", [("simple-64", embedder1), ("simple-128", embedder2)]
        )

        assert "simple-64" in results
        assert "simple-128" in results
        assert len(results["simple-64"]) == 64
        assert len(results["simple-128"]) == 128

    @pytest.mark.asyncio
    async def test_compare_empty(self) -> None:
        """Test with no embedders."""
        results = await compare_embedders("test", [])
        assert results == {}
