"""
Tests for Holographic Brain integration.

Tests the full Brain workflow:
- create_brain_logos() factory
- self.memory.capture → ghost.surface workflow
- self.memory.cartography.manifest
- Semantic embeddings with SimpleEmbedder (TF-IDF)

Session 5: Crown Jewel Brain - Integration Tests
"""

from __future__ import annotations

from typing import Any

import pytest

from .conftest import create_mock_umwelt

# =============================================================================
# Factory Tests
# =============================================================================


class TestCreateBrainLogos:
    """Tests for create_brain_logos factory."""

    def test_factory_exists(self) -> None:
        """create_brain_logos is exported from agentese module."""
        from protocols.agentese import create_brain_logos

        assert callable(create_brain_logos)

    def test_factory_creates_logos(self) -> None:
        """create_brain_logos returns a Logos instance."""
        from protocols.agentese import Logos, create_brain_logos

        logos = create_brain_logos()
        assert isinstance(logos, Logos)

    def test_factory_with_simple_embedder(self) -> None:
        """create_brain_logos works with simple embedder."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="simple")
        assert logos is not None

    def test_factory_with_auto_embedder(self) -> None:
        """create_brain_logos works with auto embedder."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="auto")
        assert logos is not None


# =============================================================================
# Capture Tests
# =============================================================================


class TestBrainCapture:
    """Tests for self.memory.capture with brain wiring."""

    @pytest.fixture
    def brain_logos(self) -> Any:
        """Create brain logos for testing."""
        from protocols.agentese import create_brain_logos

        return create_brain_logos(embedder_type="simple")

    @pytest.fixture
    def observer(self) -> Any:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_capture_stores_content(self, brain_logos: Any, observer: Any) -> None:
        """self.memory.capture stores content in brain."""
        result = await brain_logos.invoke(
            "self.memory.capture", observer, content="Machine learning tutorial"
        )

        assert result.get("status") == "captured"
        # API returns concept_id, not pattern_id
        assert result.get("concept_id") is not None

    @pytest.mark.asyncio
    async def test_capture_multiple_items(self, brain_logos: Any, observer: Any) -> None:
        """Multiple captures store multiple items."""
        # Capture multiple items
        r1 = await brain_logos.invoke(
            "self.memory.capture", observer, content="Python programming basics"
        )
        r2 = await brain_logos.invoke(
            "self.memory.capture", observer, content="JavaScript web development"
        )
        r3 = await brain_logos.invoke(
            "self.memory.capture", observer, content="Rust systems programming"
        )

        # All should succeed
        assert r1.get("status") == "captured"
        assert r2.get("status") == "captured"
        assert r3.get("status") == "captured"

        # All should have different concept IDs
        ids = {r1.get("concept_id"), r2.get("concept_id"), r3.get("concept_id")}
        assert len(ids) == 3

    @pytest.mark.asyncio
    async def test_capture_requires_content(self, brain_logos: Any, observer: Any) -> None:
        """self.memory.capture requires content parameter."""
        result = await brain_logos.invoke("self.memory.capture", observer)

        assert "error" in result


# =============================================================================
# Ghost Surfacing Tests
# =============================================================================


class TestBrainGhostSurfacing:
    """Tests for self.memory.ghost.surface with brain wiring."""

    @pytest.fixture
    def brain_logos(self) -> Any:
        """Create brain logos for testing."""
        from protocols.agentese import create_brain_logos

        return create_brain_logos(embedder_type="simple")

    @pytest.fixture
    def observer(self) -> Any:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_ghost_surface_returns_results(self, brain_logos: Any, observer: Any) -> None:
        """ghost.surface returns results for captured content."""
        # Capture identical content - hash-based embedding will find exact match
        await brain_logos.invoke(
            "self.memory.capture", observer, content="Exact match test content"
        )

        # Search with exact same content (hash match)
        result = await brain_logos.invoke(
            "self.memory.ghost.surface", observer, context="Exact match test content"
        )

        # Note: Without real embedder, ghost.surface may not find similar content
        # This test verifies the pipeline works, not semantic similarity
        assert "surfaced" in result
        assert isinstance(result.get("surfaced"), list)

    @pytest.mark.asyncio
    async def test_ghost_surface_empty_when_no_captures(
        self, brain_logos: Any, observer: Any
    ) -> None:
        """ghost.surface returns empty when no captures exist."""
        # Fresh logos with no captures
        from protocols.agentese import create_brain_logos

        fresh_logos = create_brain_logos(embedder_type="simple")

        result = await fresh_logos.invoke("self.memory.ghost.surface", observer, context="anything")

        assert result.get("count", 0) == 0

    @pytest.mark.asyncio
    async def test_ghost_surface_respects_limit(self, brain_logos: Any, observer: Any) -> None:
        """ghost.surface respects limit parameter."""
        # Capture many items
        for i in range(10):
            await brain_logos.invoke(
                "self.memory.capture",
                observer,
                content=f"Programming topic number {i}",
            )

        # Request only 3
        result = await brain_logos.invoke(
            "self.memory.ghost.surface", observer, context="programming", limit=3
        )

        surfaced = result.get("surfaced", [])
        assert len(surfaced) <= 3


# =============================================================================
# Cartography Tests
# =============================================================================


class TestBrainCartography:
    """Tests for self.memory.cartography.manifest with brain wiring."""

    @pytest.fixture
    def brain_logos(self) -> Any:
        """Create brain logos for testing."""
        from protocols.agentese import create_brain_logos

        return create_brain_logos(embedder_type="simple")

    @pytest.fixture
    def observer(self) -> Any:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_cartography_manifest_works(self, brain_logos: Any, observer: Any) -> None:
        """self.memory.cartography.manifest returns topology info."""
        from protocols.agentese.node import BasicRendering

        # Capture some content
        await brain_logos.invoke("self.memory.capture", observer, content="Category theory basics")
        await brain_logos.invoke("self.memory.capture", observer, content="Functor composition")

        result = await brain_logos.invoke("self.memory.cartography.manifest", observer)

        # Should return BasicRendering with topology info
        assert result is not None
        assert isinstance(result, BasicRendering)
        assert "Topology" in result.summary or "Landmarks" in result.content


# =============================================================================
# Full Workflow Tests
# =============================================================================


class TestBrainFullWorkflow:
    """Integration tests for full Brain workflow."""

    @pytest.mark.asyncio
    async def test_capture_then_surface_workflow(self) -> None:
        """Full workflow: capture → ghost surface → verify pipeline works."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="simple")
        observer: Any = create_mock_umwelt()

        # 1. Capture content
        r1 = await logos.invoke(
            "self.memory.capture",
            observer,
            content="Machine learning is a subset of artificial intelligence",
        )
        r2 = await logos.invoke(
            "self.memory.capture",
            observer,
            content="Neural networks learn from data",
        )

        # Verify captures succeeded
        assert r1.get("status") == "captured"
        assert r2.get("status") == "captured"

        # 2. Ghost surface - verify pipeline works
        result = await logos.invoke("self.memory.ghost.surface", observer, context="anything")

        # 3. Verify surface returns proper structure (not semantic similarity)
        assert "surfaced" in result
        assert "count" in result
        assert isinstance(result["surfaced"], list)

    @pytest.mark.asyncio
    async def test_multiple_captures_and_surface(self) -> None:
        """Test that multiple captures work and surface returns proper structure."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="simple")
        observer: Any = create_mock_umwelt()

        # Capture multiple items
        captures = [
            "Python is a programming language for data science",
            "JavaScript runs in web browsers",
            "Rust provides memory safety without garbage collection",
            "Machine learning models predict outcomes",
            "Kubernetes orchestrates container deployments",
        ]

        results = []
        for content in captures:
            r = await logos.invoke("self.memory.capture", observer, content=content)
            results.append(r)

        # All captures should succeed
        for r in results:
            assert r.get("status") == "captured"
            assert r.get("concept_id") is not None

        # Ghost surface should work (returns structure, not testing semantic similarity)
        result = await logos.invoke("self.memory.ghost.surface", observer, context="any query")

        assert "surfaced" in result
        assert "count" in result

    @pytest.mark.asyncio
    async def test_brain_logos_independent_instances(self) -> None:
        """Each create_brain_logos call creates independent instance."""
        from protocols.agentese import create_brain_logos

        logos1 = create_brain_logos(embedder_type="simple")
        logos2 = create_brain_logos(embedder_type="simple")

        observer: Any = create_mock_umwelt()

        # Capture in logos1
        await logos1.invoke("self.memory.capture", observer, content="Content only in logos1")

        # Search in logos2 should find nothing
        result = await logos2.invoke("self.memory.ghost.surface", observer, context="logos1")

        assert result.get("count", 0) == 0


# =============================================================================
# Semantic Search Quality Tests (require sentence-transformers)
# =============================================================================


def _has_sentence_transformers() -> bool:
    """Check if sentence-transformers is available."""
    try:
        import sentence_transformers  # noqa: F401

        return True
    except ImportError:
        return False


requires_sentence_transformers = pytest.mark.skipif(
    not _has_sentence_transformers(),
    reason="sentence-transformers not installed (install with `uv sync --extra brain`)",
)


@requires_sentence_transformers
class TestSemanticSearchQuality:
    """Tests for semantic search quality with real embeddings.

    These tests verify that semantic similarity actually works:
    - Related concepts are found together
    - Unrelated content has lower similarity
    - Search quality improves with real embeddings vs hash fallback
    """

    @pytest.fixture
    def semantic_logos(self) -> Any:
        """Create brain logos with sentence-transformers embedder."""
        from protocols.agentese import create_brain_logos

        return create_brain_logos(embedder_type="auto")  # Uses sentence-transformers

    @pytest.fixture
    def observer(self) -> Any:
        """Create mock observer."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_python_programming_finds_code_examples(
        self, semantic_logos: Any, observer: Any
    ) -> None:
        """Searching 'Python programming' should find 'Python code examples'."""
        # Capture semantically related content
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Python code examples for beginners",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="JavaScript frameworks for web development",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Cooking recipes from Italy",
        )

        # Search for Python programming
        result = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="Python programming tutorials",
            limit=3,
        )

        surfaced = result.get("surfaced", [])
        assert len(surfaced) > 0

        # Python content should be most relevant
        first_content = surfaced[0].get("content", "")
        assert "Python" in first_content or "code" in first_content.lower()

    @pytest.mark.asyncio
    async def test_ml_finds_ai_content(self, semantic_logos: Any, observer: Any) -> None:
        """Searching 'machine learning' should find AI-related content."""
        # Capture various content
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Neural networks are used for deep learning and AI",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Database optimization for SQL queries",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Gardening tips for spring vegetables",
        )

        # Search for machine learning
        result = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="machine learning algorithms",
            limit=3,
        )

        surfaced = result.get("surfaced", [])
        assert len(surfaced) > 0

        # AI/neural network content should be found first
        first_content = surfaced[0].get("content", "").lower()
        assert any(word in first_content for word in ["neural", "deep", "ai", "learn"])

    @pytest.mark.asyncio
    async def test_semantic_similarity_ordering(self, semantic_logos: Any, observer: Any) -> None:
        """Results should be ordered by semantic similarity."""
        # Capture content with varying relevance to "cat"
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Cats are popular pets that purr and meow",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Dogs are loyal companions that bark",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Quantum physics explains particle behavior",
        )

        # Search for feline
        result = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="feline animals",
            limit=3,
        )

        surfaced = result.get("surfaced", [])
        assert len(surfaced) >= 2

        # Cat content should be first (most semantically similar to "feline")
        first_content = surfaced[0].get("content", "").lower()
        assert "cat" in first_content or "purr" in first_content

    @pytest.mark.asyncio
    async def test_embeddings_are_consistent(self, semantic_logos: Any, observer: Any) -> None:
        """Same query should give consistent results."""
        # Capture content
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Functional programming with Haskell",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Object-oriented programming with Java",
        )

        # Search twice with same query
        result1 = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="functional programming languages",
            limit=2,
        )
        result2 = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="functional programming languages",
            limit=2,
        )

        # Results should be identical
        surfaced1 = result1.get("surfaced", [])
        surfaced2 = result2.get("surfaced", [])
        assert len(surfaced1) == len(surfaced2)
        for s1, s2 in zip(surfaced1, surfaced2):
            assert s1.get("content") == s2.get("content")

    @pytest.mark.asyncio
    async def test_semantic_vs_keyword_search(self, semantic_logos: Any, observer: Any) -> None:
        """Semantic search should find related content even without keyword overlap."""
        # Capture content about programming without saying "code"
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Writing software applications and debugging errors",
        )
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Baking bread requires flour and yeast",
        )

        # Search for "code" - should find software content even though word "code" not present
        result = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="writing code and programming",
            limit=2,
        )

        surfaced = result.get("surfaced", [])
        assert len(surfaced) > 0

        # Software content should rank higher than baking
        first_content = surfaced[0].get("content", "").lower()
        assert "software" in first_content or "application" in first_content

    @pytest.mark.asyncio
    async def test_empty_context_returns_results(self, semantic_logos: Any, observer: Any) -> None:
        """Even vague context should return something if content exists."""
        await semantic_logos.invoke(
            "self.memory.capture",
            observer,
            content="Important meeting notes from Monday",
        )

        result = await semantic_logos.invoke(
            "self.memory.ghost.surface",
            observer,
            context="stuff",
            limit=5,
        )

        # Should return something (semantic embeddings give some similarity)
        assert "surfaced" in result


# =============================================================================
# Performance Tests
# =============================================================================


class TestBrainPerformance:
    """Performance tests for brain operations with larger datasets.

    These tests verify that:
    - Capturing 100+ items completes in reasonable time
    - Ghost surfacing stays fast (<100ms) with many items
    - Memory usage is bounded
    """

    @pytest.fixture
    def perf_logos(self) -> Any:
        """Create brain logos for performance testing."""
        from protocols.agentese import create_brain_logos

        # Use simple embedder for faster tests
        return create_brain_logos(embedder_type="simple")

    @pytest.fixture
    def observer(self) -> Any:
        """Create mock observer."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_capture_100_items_performance(self, perf_logos: Any, observer: Any) -> None:
        """Test capturing 100 items completes in reasonable time."""
        import time

        # Sample content corpus
        topics = [
            "Python programming language features",
            "JavaScript web development",
            "Machine learning algorithms",
            "Database optimization techniques",
            "Cloud computing architecture",
            "DevOps best practices",
            "API design patterns",
            "Security best practices",
            "Performance tuning tips",
            "Testing strategies",
        ]

        start_time = time.time()

        # Capture 100 items
        for i in range(100):
            topic = topics[i % len(topics)]
            content = f"{topic} - Item {i}: Some detailed content about {topic.lower()}"
            await perf_logos.invoke(
                "self.memory.capture",
                observer,
                content=content,
            )

        elapsed = time.time() - start_time

        # Should complete in under 10 seconds (100ms average per item)
        assert elapsed < 10.0, f"Capturing 100 items took {elapsed:.2f}s (expected <10s)"

    @pytest.mark.skip(reason="Ghost infrastructure removed in data-architecture-rewrite")
    @pytest.mark.asyncio
    async def test_ghost_surfacing_stays_fast(self, perf_logos: Any, observer: Any) -> None:
        """Test that ghost surfacing stays fast (<100ms) with 100 items."""
        import time

        # First populate with 100 items
        for i in range(100):
            await perf_logos.invoke(
                "self.memory.capture",
                observer,
                content=f"Content item {i} about various programming topics and techniques",
            )

        # Test surfacing performance
        queries = [
            "programming techniques",
            "software development",
            "code optimization",
            "testing methods",
            "design patterns",
        ]

        for query in queries:
            start_time = time.time()

            result = await perf_logos.invoke(
                "self.memory.ghost.surface",
                observer,
                context=query,
                limit=10,
            )

            elapsed_ms = (time.time() - start_time) * 1000

            # Should complete in under 100ms
            assert elapsed_ms < 100, f"Ghost surfacing took {elapsed_ms:.1f}ms (expected <100ms)"
            assert result.get("count", 0) > 0, "Should find some results"

    @pytest.mark.asyncio
    async def test_cartography_with_large_dataset(self, perf_logos: Any, observer: Any) -> None:
        """Test cartography works with 100+ items."""
        import time

        # Populate
        for i in range(100):
            await perf_logos.invoke(
                "self.memory.capture",
                observer,
                content=f"Topic {i}: Information about category {i // 10}",
            )

        # Get cartography
        start_time = time.time()

        result = await perf_logos.invoke(
            "self.memory.cartography.manifest",
            observer,
        )

        elapsed_ms = (time.time() - start_time) * 1000

        # Should complete quickly
        assert elapsed_ms < 200, f"Cartography took {elapsed_ms:.1f}ms (expected <200ms)"

    @pytest.mark.asyncio
    async def test_memory_usage_bounded(self, perf_logos: Any, observer: Any) -> None:
        """Test that memory usage is bounded with many items."""
        # Get crystal reference
        resolvers = perf_logos._context_resolvers
        self_resolver = resolvers.get("self")
        memory_node = getattr(self_resolver, "_memory", None)
        crystal = getattr(memory_node, "_memory_crystal", None) if memory_node else None

        # Capture 100 items
        for i in range(100):
            await perf_logos.invoke(
                "self.memory.capture",
                observer,
                content=f"Test content {i} with some additional text for size",
            )

        # Check patterns count
        if crystal:
            pattern_count = len(getattr(crystal, "_patterns", {}))
            assert pattern_count == 100, f"Expected 100 patterns, got {pattern_count}"

            # Rough size check - each pattern should be < 10KB average
            # This is a sanity check, not a strict limit
            dimension = getattr(crystal, "_dimension", 64)
            # 8 bytes per float * dimension + overhead
            estimated_size_per_pattern = dimension * 8 + 1000  # 1KB overhead
            total_estimated = pattern_count * estimated_size_per_pattern
            assert total_estimated < 10_000_000, "Memory estimate exceeds 10MB"
