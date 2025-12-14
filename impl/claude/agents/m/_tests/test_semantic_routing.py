"""
Tests for semantic_routing.py - Locality-Aware Gradient Sensing.

Phase 6 tests for semantic filtering of pheromone gradients.
"""

from datetime import datetime

import pytest

from ..semantic_routing import (
    EmbeddingSimilarity,
    FilteredSenseResult,
    GraphSimilarity,
    KeywordSimilarity,
    LocalityConfig,
    PrefixSimilarity,
    SemanticGradientMap,
    SemanticRouter,
    create_semantic_router,
)
from ..stigmergy import PheromoneField

# =============================================================================
# Similarity Provider Tests
# =============================================================================


class TestPrefixSimilarity:
    """Tests for PrefixSimilarity."""

    @pytest.fixture
    def similarity(self) -> PrefixSimilarity:
        return PrefixSimilarity(separator=".")

    @pytest.mark.asyncio
    async def test_identical_concepts(self, similarity: PrefixSimilarity) -> None:
        """Identical concepts should have similarity 1.0."""
        score = await similarity.similarity("code.python.debug", "code.python.debug")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_same_prefix(self, similarity: PrefixSimilarity) -> None:
        """Concepts with same prefix should have high similarity."""
        score = await similarity.similarity("code.python.debug", "code.python.test")
        assert score == pytest.approx(2 / 3)  # 2 shared, 3 max

    @pytest.mark.asyncio
    async def test_partial_prefix(self, similarity: PrefixSimilarity) -> None:
        """Partial prefix should give partial similarity."""
        score = await similarity.similarity("code.python", "code.javascript")
        assert score == pytest.approx(1 / 2)  # 1 shared, 2 max

    @pytest.mark.asyncio
    async def test_no_prefix(self, similarity: PrefixSimilarity) -> None:
        """No shared prefix should give 0 similarity."""
        score = await similarity.similarity("code.python", "food.cooking")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_different_depths(self, similarity: PrefixSimilarity) -> None:
        """Different depths should use max length."""
        score = await similarity.similarity("code", "code.python.debug")
        assert score == pytest.approx(1 / 3)  # 1 shared, 3 max

    @pytest.mark.asyncio
    async def test_empty_concepts(self, similarity: PrefixSimilarity) -> None:
        """Empty identical concepts return 1.0 (they're equal)."""
        score = await similarity.similarity("", "")
        assert score == 1.0  # Identical, even if empty

    @pytest.mark.asyncio
    async def test_one_empty_concept(self, similarity: PrefixSimilarity) -> None:
        """One empty concept should return 0."""
        score = await similarity.similarity("", "code.python")
        assert score == 0.0


class TestKeywordSimilarity:
    """Tests for KeywordSimilarity."""

    @pytest.fixture
    def similarity(self) -> KeywordSimilarity:
        return KeywordSimilarity()

    @pytest.mark.asyncio
    async def test_identical_concepts(self, similarity: KeywordSimilarity) -> None:
        """Identical concepts should have similarity 1.0."""
        score = await similarity.similarity("python debugging", "python debugging")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_partial_overlap(self, similarity: KeywordSimilarity) -> None:
        """Partial overlap should give partial similarity."""
        score = await similarity.similarity(
            "python debugging code", "python testing code"
        )
        # python, code shared; debugging, testing unique
        # Jaccard: 2 / 4 = 0.5
        assert score == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_no_overlap(self, similarity: KeywordSimilarity) -> None:
        """No overlap should give 0 similarity."""
        score = await similarity.similarity("python debugging", "food cooking")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_stop_words_filtered(self, similarity: KeywordSimilarity) -> None:
        """Stop words should be filtered out."""
        score = await similarity.similarity("the python and code", "a python or code")
        # Both reduce to {python, code}
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_case_insensitive(self, similarity: KeywordSimilarity) -> None:
        """Similarity should be case insensitive."""
        score = await similarity.similarity("Python Debug", "python debug")
        assert score == 1.0


class TestGraphSimilarity:
    """Tests for GraphSimilarity."""

    @pytest.fixture
    def edges(self) -> dict[str, set[str]]:
        """Simple graph for testing."""
        return {
            "python": {"code", "programming"},
            "code": {"python", "javascript", "debug"},
            "programming": {"python", "javascript"},
            "javascript": {"code", "programming"},
            "debug": {"code", "testing"},
            "testing": {"debug"},
            "cooking": {"food"},
            "food": {"cooking"},
        }

    @pytest.fixture
    def similarity(self, edges: dict[str, set[str]]) -> GraphSimilarity:
        return GraphSimilarity(edges=edges, max_distance=5)

    @pytest.mark.asyncio
    async def test_identical_concepts(self, similarity: GraphSimilarity) -> None:
        """Identical concepts should have similarity 1.0."""
        score = await similarity.similarity("python", "python")
        assert score == 1.0

    @pytest.mark.asyncio
    async def test_direct_neighbors(self, similarity: GraphSimilarity) -> None:
        """Direct neighbors should have high similarity."""
        score = await similarity.similarity("python", "code")
        # Distance 1 → 1 / (1 + 1) = 0.5
        assert score == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_two_hops(self, similarity: GraphSimilarity) -> None:
        """Two-hop neighbors should have lower similarity."""
        score = await similarity.similarity("python", "debug")
        # Distance 2 (python → code → debug) → 1 / (1 + 2) ≈ 0.33
        assert score == pytest.approx(1 / 3)

    @pytest.mark.asyncio
    async def test_disconnected(self, similarity: GraphSimilarity) -> None:
        """Disconnected concepts should have 0 similarity."""
        score = await similarity.similarity("python", "cooking")
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_unknown_concept(self, similarity: GraphSimilarity) -> None:
        """Unknown concepts should return 0."""
        score = await similarity.similarity("python", "unknown")
        assert score == 0.0


# =============================================================================
# LocalityConfig Tests
# =============================================================================


class TestLocalityConfig:
    """Tests for LocalityConfig."""

    def test_default_locality(self) -> None:
        """Default locality should be 0.5."""
        config = LocalityConfig()
        assert config.locality == 0.5

    def test_global_locality(self) -> None:
        """Locality 0 should give weight 1 for any similarity."""
        config = LocalityConfig(locality=0)
        assert config.compute_weight(0.5) == 1.0
        assert config.compute_weight(0.1) == 1.0

    def test_local_locality(self) -> None:
        """Locality 1 should give weight 1 only for perfect match."""
        config = LocalityConfig(locality=0.999)
        assert config.compute_weight(1.0) == 1.0
        assert config.compute_weight(0.5) == 0.0

    def test_threshold_filtering(self) -> None:
        """Similarities below threshold should give 0 weight."""
        config = LocalityConfig(locality=0.5, threshold=0.3)
        assert config.compute_weight(0.2) == 0.0
        assert config.compute_weight(0.4) > 0.0

    def test_decay_curve(self) -> None:
        """Higher locality should give sharper decay."""
        low_locality = LocalityConfig(locality=0.3)
        high_locality = LocalityConfig(locality=0.7)

        sim = 0.5
        low_weight = low_locality.compute_weight(sim)
        high_weight = high_locality.compute_weight(sim)

        # Higher locality → sharper decay → lower weight for same similarity
        assert high_weight < low_weight

    def test_invalid_locality_raises(self) -> None:
        """Invalid locality values should raise."""
        with pytest.raises(ValueError):
            LocalityConfig(locality=-0.1)
        with pytest.raises(ValueError):
            LocalityConfig(locality=1.5)


# =============================================================================
# SemanticRouter Tests
# =============================================================================


class TestSemanticRouter:
    """Tests for SemanticRouter."""

    @pytest.fixture
    def field(self) -> PheromoneField:
        return PheromoneField(decay_rate=0.0, evaporation_threshold=0.0)

    @pytest.fixture
    def router(self, field: PheromoneField) -> SemanticRouter:
        return SemanticRouter(
            field=field,
            similarity=PrefixSimilarity(),
            locality=LocalityConfig(locality=0.5, threshold=0.1),
        )

    @pytest.mark.asyncio
    async def test_sense_empty_field(self, router: SemanticRouter) -> None:
        """Sensing empty field should return empty list."""
        results = await router.sense("code.python")
        assert results == []

    @pytest.mark.asyncio
    async def test_sense_with_deposits(
        self, field: PheromoneField, router: SemanticRouter
    ) -> None:
        """Sensing should return filtered results."""
        # Deposit traces
        await field.deposit("code.python.debug", 1.0, depositor="agent_a")
        await field.deposit("code.python.test", 0.8, depositor="agent_b")
        await field.deposit("food.cooking", 0.5, depositor="agent_c")

        # Sense from python position
        results = await router.sense("code.python")

        # Should find python.debug and python.test (high similarity)
        # Should filter out food.cooking (low similarity)
        concepts = [r.concept for r in results]
        assert "code.python.debug" in concepts
        assert "code.python.test" in concepts
        # food.cooking has 0 similarity to code.python, should be filtered

    @pytest.mark.asyncio
    async def test_sense_weights_by_similarity(
        self, field: PheromoneField, router: SemanticRouter
    ) -> None:
        """Results should be weighted by similarity."""
        await field.deposit("code.python.debug", 1.0, depositor="agent_a")
        await field.deposit("code.javascript", 1.0, depositor="agent_b")

        results = await router.sense("code.python")

        # Find results
        python_result = next((r for r in results if "python" in r.concept), None)
        js_result = next((r for r in results if "javascript" in r.concept), None)

        assert python_result is not None
        assert js_result is not None

        # Python has higher similarity (2/3 vs 1/2)
        assert python_result.similarity > js_result.similarity

    @pytest.mark.asyncio
    async def test_route_follows_gradient(
        self, field: PheromoneField, router: SemanticRouter
    ) -> None:
        """Route should return agent with strongest weighted gradient."""
        await field.deposit("code.python", 2.0, depositor="python_expert")
        await field.deposit("code.javascript", 1.0, depositor="js_expert")

        agent = await router.route("code.python")
        assert agent == "python_expert"

    @pytest.mark.asyncio
    async def test_route_returns_default(self, router: SemanticRouter) -> None:
        """Route should return default agent when no gradient."""
        agent = await router.route("unknown.concept")
        assert agent == "default"

    @pytest.mark.asyncio
    async def test_stats_tracking(
        self, field: PheromoneField, router: SemanticRouter
    ) -> None:
        """Router should track statistics."""
        await field.deposit("code.python", 1.0, depositor="agent")

        await router.sense("code.python")
        await router.sense("code.python")

        stats = router.stats()
        assert stats["sense_count"] == 2


# =============================================================================
# FilteredSenseResult Tests
# =============================================================================


class TestFilteredSenseResult:
    """Tests for FilteredSenseResult."""

    def test_creation(self) -> None:
        """Should create with all fields."""
        result = FilteredSenseResult(
            concept="code.python",
            total_intensity=0.8,
            trace_count=5,
            dominant_depositor="agent_a",
            raw_intensity=1.0,
            similarity=0.8,
            locality_weight=0.8,
            query_position="code",
        )
        assert result.concept == "code.python"
        assert result.total_intensity == 0.8
        assert result.raw_intensity == 1.0
        assert result.similarity == 0.8


class TestSemanticGradientMap:
    """Tests for SemanticGradientMap."""

    def test_strongest(self) -> None:
        """Should return strongest gradient."""
        gmap = SemanticGradientMap(
            position="code",
            gradients={"agent_a": 0.8, "agent_b": 0.5, "agent_c": 0.3},
            similarities={"code.python": 0.9, "code.js": 0.7},
        )
        strongest = gmap.strongest()
        assert strongest == ("agent_a", 0.8)

    def test_top_k(self) -> None:
        """Should return top k gradients."""
        gmap = SemanticGradientMap(
            position="code",
            gradients={"a": 0.8, "b": 0.5, "c": 0.3, "d": 0.1},
            similarities={},
        )
        top_2 = gmap.top_k(2)
        assert len(top_2) == 2
        assert top_2[0] == ("a", 0.8)
        assert top_2[1] == ("b", 0.5)

    def test_concepts_by_similarity(self) -> None:
        """Should return concepts sorted by similarity."""
        gmap = SemanticGradientMap(
            position="code",
            gradients={},
            similarities={"code.python": 0.9, "code.js": 0.7, "food": 0.1},
        )
        sorted_concepts = gmap.concepts_by_similarity()
        assert sorted_concepts[0] == ("code.python", 0.9)
        assert sorted_concepts[1] == ("code.js", 0.7)


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_semantic_router_prefix(self) -> None:
        """Should create router with prefix similarity."""
        field = PheromoneField()
        router = create_semantic_router(
            field=field,
            similarity_type="prefix",
            locality=0.5,
        )
        assert isinstance(router, SemanticRouter)

    def test_create_semantic_router_keyword(self) -> None:
        """Should create router with keyword similarity."""
        field = PheromoneField()
        router = create_semantic_router(
            field=field,
            similarity_type="keyword",
            locality=0.5,
        )
        assert isinstance(router, SemanticRouter)

    def test_create_semantic_router_graph(self) -> None:
        """Should create router with graph similarity."""
        field = PheromoneField()
        edges = {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}
        router = create_semantic_router(
            field=field,
            similarity_type="graph",
            locality=0.5,
            edges=edges,
        )
        assert isinstance(router, SemanticRouter)

    def test_create_semantic_router_invalid_type(self) -> None:
        """Should raise for invalid similarity type."""
        field = PheromoneField()
        with pytest.raises(ValueError, match="Unknown similarity type"):
            create_semantic_router(
                field=field,
                similarity_type="invalid",
            )

    def test_create_semantic_router_missing_edges(self) -> None:
        """Graph similarity should require edges argument."""
        field = PheromoneField()
        with pytest.raises(ValueError, match="requires 'edges'"):
            create_semantic_router(
                field=field,
                similarity_type="graph",
            )
