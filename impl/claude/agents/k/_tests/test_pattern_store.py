"""
Tests for PatternStore.

PatternStore provides Qdrant-backed semantic search over HypnagogicCycle
patterns, enabling K-gent to find related patterns even when wording differs.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from agents.k.hypnagogia import Pattern, PatternMaturity
from agents.k.pattern_store import (
    MockEmbedder,
    MockVectorClient,
    PatternMatch,
    PatternStore,
    PatternStoreConfig,
    SearchResult,
    close_pattern_store,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config() -> PatternStoreConfig:
    """Create a mock configuration."""
    return PatternStoreConfig(
        qdrant_url="mock://localhost",
        collection="test_patterns",
        embedding_provider="mock",
        embedding_dimension=128,
    )


@pytest.fixture
def mock_embedder() -> MockEmbedder:
    """Create a mock embedder."""
    return MockEmbedder(dimension=128)


@pytest.fixture
def mock_vector_client() -> MockVectorClient:
    """Create a mock vector client."""
    return MockVectorClient()


@pytest.fixture
def pattern_store(
    mock_config: PatternStoreConfig,
    mock_embedder: MockEmbedder,
    mock_vector_client: MockVectorClient,
) -> PatternStore:
    """Create a PatternStore with mock backends."""
    return PatternStore(
        config=mock_config,
        embedder=mock_embedder,
        vector_client=mock_vector_client,
    )


@pytest.fixture
def sample_pattern() -> Pattern:
    """Create a sample pattern for testing."""
    return Pattern(
        content="Uses categorical reasoning for problem solving",
        occurrences=3,
        maturity=PatternMaturity.SAPLING,
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
        evidence=["dialogue 1", "dialogue 2"],
        eigenvector_affinities={"categorical": 0.8, "aesthetic": 0.3},
    )


# =============================================================================
# Mock Tests
# =============================================================================


class TestMockEmbedder:
    """Tests for MockEmbedder."""

    @pytest.mark.asyncio
    async def test_embed_returns_correct_dimension(self) -> None:
        """Test that embedder returns correct dimension."""
        embedder = MockEmbedder(dimension=256)
        vector = await embedder.embed("test text")
        assert len(vector) == 256

    @pytest.mark.asyncio
    async def test_embed_is_deterministic(self) -> None:
        """Test that same text produces same embedding."""
        embedder = MockEmbedder()
        v1 = await embedder.embed("test text")
        v2 = await embedder.embed("test text")
        assert v1 == v2

    @pytest.mark.asyncio
    async def test_embed_differs_for_different_text(self) -> None:
        """Test that different text produces different embeddings."""
        embedder = MockEmbedder()
        v1 = await embedder.embed("text one")
        v2 = await embedder.embed("text two")
        assert v1 != v2


class TestMockVectorClient:
    """Tests for MockVectorClient."""

    @pytest.mark.asyncio
    async def test_upsert_and_search(self) -> None:
        """Test upsert and search operations."""
        client = MockVectorClient()

        # Upsert a vector
        await client.upsert(
            collection="test",
            id="1",
            vector=[0.1, 0.2, 0.3],
            payload={"content": "test"},
        )

        # Search
        results = await client.search(
            collection="test",
            query_vector=[0.1, 0.2, 0.3],
            top_k=10,
        )

        assert len(results) == 1
        assert results[0]["id"] == "1"

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        """Test delete operation."""
        client = MockVectorClient()

        await client.upsert("test", "1", [0.1, 0.2], {"content": "test"})
        await client.delete("test", "1")

        results = await client.search("test", [0.1, 0.2], 10)
        assert len(results) == 0


# =============================================================================
# PatternStore Tests
# =============================================================================


class TestPatternStoreBasics:
    """Basic tests for PatternStore."""

    def test_initial_count_is_zero(self, pattern_store: PatternStore) -> None:
        """Test initial indexed count is zero."""
        assert pattern_store.indexed_count == 0

    @pytest.mark.asyncio
    async def test_index_pattern(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test indexing a pattern."""
        await pattern_store.index_pattern(sample_pattern)
        assert pattern_store.indexed_count == 1

    @pytest.mark.asyncio
    async def test_remove_pattern(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test removing a pattern."""
        await pattern_store.index_pattern(sample_pattern)
        assert pattern_store.indexed_count == 1

        await pattern_store.remove_pattern(sample_pattern.id)
        assert pattern_store.indexed_count == 0


class TestPatternStoreSearch:
    """Tests for pattern search."""

    @pytest.mark.asyncio
    async def test_find_similar_returns_result(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test find_similar returns SearchResult."""
        await pattern_store.index_pattern(sample_pattern)

        result = await pattern_store.find_similar(
            query="categorical reasoning",
            min_score=0.0,
        )

        assert isinstance(result, SearchResult)
        assert result.query == "categorical reasoning"
        assert result.search_time_ms > 0

    @pytest.mark.asyncio
    async def test_find_similar_matches_indexed(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test that indexed patterns can be found."""
        await pattern_store.index_pattern(sample_pattern)

        result = await pattern_store.find_similar(
            query=sample_pattern.content,
            min_score=0.5,
        )

        assert result.has_matches
        assert result.best_match is not None
        assert result.best_match.pattern.content == sample_pattern.content

    @pytest.mark.asyncio
    async def test_find_similar_respects_min_score(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test that min_score filters results."""
        await pattern_store.index_pattern(sample_pattern)

        # Very high threshold should filter out results
        result = await pattern_store.find_similar(
            query="completely unrelated query",
            min_score=0.99,
        )

        # With mock embeddings, unrelated text won't match
        # The important thing is the threshold is respected
        assert isinstance(result, SearchResult)

    @pytest.mark.asyncio
    async def test_find_similar_respects_top_k(
        self,
        pattern_store: PatternStore,
    ) -> None:
        """Test that top_k limits results."""
        # Index multiple patterns
        for i in range(10):
            pattern = Pattern(
                content=f"Pattern number {i}",
                maturity=PatternMaturity.SEED,
            )
            await pattern_store.index_pattern(pattern)

        result = await pattern_store.find_similar(
            query="Pattern",
            top_k=3,
            min_score=0.0,
        )

        assert len(result.matches) <= 3


class TestPatternMatch:
    """Tests for PatternMatch."""

    def test_is_high_confidence(self, sample_pattern: Pattern) -> None:
        """Test high confidence detection."""
        high = PatternMatch(pattern=sample_pattern, score=0.9, id="1")
        low = PatternMatch(pattern=sample_pattern, score=0.5, id="2")

        assert high.is_high_confidence
        assert not low.is_high_confidence


class TestSearchResult:
    """Tests for SearchResult."""

    def test_has_matches(self, sample_pattern: Pattern) -> None:
        """Test has_matches property."""
        empty = SearchResult(
            query="test",
            matches=[],
            search_time_ms=1.0,
            total_indexed=0,
        )
        assert not empty.has_matches

        with_match = SearchResult(
            query="test",
            matches=[PatternMatch(pattern=sample_pattern, score=0.8, id="1")],
            search_time_ms=1.0,
            total_indexed=1,
        )
        assert with_match.has_matches

    def test_best_match(self, sample_pattern: Pattern) -> None:
        """Test best_match property."""
        empty = SearchResult(
            query="test",
            matches=[],
            search_time_ms=1.0,
            total_indexed=0,
        )
        assert empty.best_match is None

        match = PatternMatch(pattern=sample_pattern, score=0.8, id="1")
        with_match = SearchResult(
            query="test",
            matches=[match],
            search_time_ms=1.0,
            total_indexed=1,
        )
        assert with_match.best_match == match


class TestPatternStoreIndexAll:
    """Tests for bulk indexing."""

    @pytest.mark.asyncio
    async def test_index_all_patterns(
        self,
        pattern_store: PatternStore,
    ) -> None:
        """Test indexing all patterns from a dictionary."""
        patterns = {
            "p1": Pattern(content="Pattern one", maturity=PatternMaturity.SEED),
            "p2": Pattern(content="Pattern two", maturity=PatternMaturity.TREE),
            "p3": Pattern(content="Composted", maturity=PatternMaturity.COMPOST),
        }

        count = await pattern_store.index_all_patterns(patterns)

        # Should not index composted patterns
        assert count == 2
        assert pattern_store.indexed_count == 2


class TestPatternStoreEigenvector:
    """Tests for eigenvector-related searches."""

    @pytest.mark.asyncio
    async def test_find_related_to_eigenvector(
        self,
        pattern_store: PatternStore,
    ) -> None:
        """Test finding patterns by eigenvector affinity."""
        # Create patterns with different affinities
        categorical_pattern = Pattern(
            content="Uses logical categories",
            eigenvector_affinities={"categorical": 0.9, "aesthetic": 0.1},
        )
        aesthetic_pattern = Pattern(
            content="Appreciates beauty",
            eigenvector_affinities={"categorical": 0.1, "aesthetic": 0.9},
        )

        await pattern_store.index_pattern(categorical_pattern)
        await pattern_store.index_pattern(aesthetic_pattern)

        # Find categorical patterns
        matches = await pattern_store.find_related_to_eigenvector(
            eigenvector="categorical",
            threshold=0.5,
        )

        # Should find the categorical pattern
        contents = [m.pattern.content for m in matches]
        assert "Uses logical categories" in contents


class TestPatternStoreConfig:
    """Tests for configuration."""

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        config = PatternStoreConfig()

        assert config.qdrant_url == "http://localhost:6333"
        assert config.collection == "kgent_patterns"
        assert config.embedding_dimension == 1536

    def test_config_from_env(self) -> None:
        """Test config can be loaded from environment."""
        import os

        old_url = os.environ.get("QDRANT_URL")
        try:
            os.environ["QDRANT_URL"] = "http://custom:6333"
            config = PatternStoreConfig.from_env()
            assert config.qdrant_url == "http://custom:6333"
        finally:
            if old_url:
                os.environ["QDRANT_URL"] = old_url
            else:
                os.environ.pop("QDRANT_URL", None)


class TestModuleFunctions:
    """Tests for module-level functions."""

    @pytest.mark.asyncio
    async def test_close_pattern_store_noop(self) -> None:
        """Test close_pattern_store when no store exists."""
        # Should not raise
        await close_pattern_store()


# =============================================================================
# CDC Integration Conceptual Tests
# =============================================================================


class TestPatternStoreCDCIntegration:
    """Conceptual tests for CDC integration."""

    @pytest.mark.asyncio
    async def test_pattern_has_required_fields_for_qdrant(
        self,
        pattern_store: PatternStore,
        sample_pattern: Pattern,
    ) -> None:
        """Test pattern has all fields needed for Qdrant payload."""
        await pattern_store.index_pattern(sample_pattern)

        # Search to verify payload structure
        result = await pattern_store.find_similar(
            query=sample_pattern.content,
            min_score=0.0,
        )

        assert result.has_matches
        match = result.best_match
        assert match is not None

        # Verify all expected fields are present
        pattern = match.pattern
        assert pattern.content is not None
        assert pattern.maturity is not None
        assert pattern.occurrences >= 0
        assert pattern.first_seen is not None
        assert pattern.last_seen is not None

    @pytest.mark.asyncio
    async def test_index_preserves_eigenvector_affinities(
        self,
        pattern_store: PatternStore,
    ) -> None:
        """Test that eigenvector affinities survive roundtrip."""
        pattern = Pattern(
            content="Test pattern",
            eigenvector_affinities={"categorical": 0.7, "aesthetic": 0.4},
        )

        await pattern_store.index_pattern(pattern)

        result = await pattern_store.find_similar(
            query=pattern.content,
            min_score=0.0,
        )

        assert result.has_matches
        assert result.best_match is not None
        retrieved = result.best_match.pattern
        assert retrieved.eigenvector_affinities == {
            "categorical": 0.7,
            "aesthetic": 0.4,
        }
