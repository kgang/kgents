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

from .conftest import MockUmwelt, create_mock_umwelt

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
    def observer(self) -> MockUmwelt:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_capture_stores_content(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
        """self.memory.capture stores content in brain."""
        result = await brain_logos.invoke(
            "self.memory.capture", observer, content="Machine learning tutorial"
        )

        assert result.get("status") == "captured"
        # API returns concept_id, not pattern_id
        assert result.get("concept_id") is not None

    @pytest.mark.asyncio
    async def test_capture_multiple_items(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
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
    async def test_capture_requires_content(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
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
    def observer(self) -> MockUmwelt:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_ghost_surface_finds_similar(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
        """ghost.surface finds semantically similar memories."""
        # Capture content about programming
        await brain_logos.invoke(
            "self.memory.capture", observer, content="Python programming tutorial"
        )
        await brain_logos.invoke(
            "self.memory.capture", observer, content="Python code examples"
        )
        await brain_logos.invoke(
            "self.memory.capture",
            observer,
            content="Cooking recipes for dinner",  # Unrelated
        )

        # Search for Python-related content
        result = await brain_logos.invoke(
            "self.memory.ghost.surface", observer, context="Python programming"
        )

        assert result.get("count", 0) > 0
        surfaced = result.get("surfaced", [])

        # Should find Python-related content with higher relevance
        assert len(surfaced) > 0

    @pytest.mark.asyncio
    async def test_ghost_surface_empty_when_no_captures(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
        """ghost.surface returns empty when no captures exist."""
        # Fresh logos with no captures
        from protocols.agentese import create_brain_logos

        fresh_logos = create_brain_logos(embedder_type="simple")

        result = await fresh_logos.invoke(
            "self.memory.ghost.surface", observer, context="anything"
        )

        assert result.get("count", 0) == 0

    @pytest.mark.asyncio
    async def test_ghost_surface_respects_limit(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
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
    def observer(self) -> MockUmwelt:
        """Create mock observer with dna attribute."""
        return create_mock_umwelt()

    @pytest.mark.asyncio
    async def test_cartography_manifest_works(
        self, brain_logos: Any, observer: MockUmwelt
    ) -> None:
        """self.memory.cartography.manifest returns topology info."""
        from protocols.agentese.node import BasicRendering

        # Capture some content
        await brain_logos.invoke(
            "self.memory.capture", observer, content="Category theory basics"
        )
        await brain_logos.invoke(
            "self.memory.capture", observer, content="Functor composition"
        )

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
        """Full workflow: capture → ghost surface → verify similarity."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="simple")
        observer = create_mock_umwelt()

        # 1. Capture related content
        await logos.invoke(
            "self.memory.capture",
            observer,
            content="Machine learning is a subset of artificial intelligence",
        )
        await logos.invoke(
            "self.memory.capture",
            observer,
            content="Neural networks learn from data",
        )
        await logos.invoke(
            "self.memory.capture",
            observer,
            content="Deep learning uses multiple layers",
        )

        # 2. Capture unrelated content
        await logos.invoke(
            "self.memory.capture",
            observer,
            content="The quick brown fox jumps over the lazy dog",
        )

        # 3. Ghost surface for AI-related content
        result = await logos.invoke(
            "self.memory.ghost.surface", observer, context="AI training neural"
        )

        # 4. Verify we found related content
        assert result.get("count", 0) > 0
        surfaced = result.get("surfaced", [])
        assert len(surfaced) > 0

        # 5. Top results should have reasonable relevance
        if surfaced:
            top_relevance = surfaced[0].get("relevance", 0)
            assert top_relevance > 0.0  # Some similarity found

    @pytest.mark.asyncio
    async def test_semantic_search_quality(self) -> None:
        """Test that semantic search finds related concepts."""
        from protocols.agentese import create_brain_logos

        logos = create_brain_logos(embedder_type="simple")
        observer = create_mock_umwelt()

        # Capture with semantic variety
        captures = [
            "Python is a programming language for data science",
            "JavaScript runs in web browsers",
            "Rust provides memory safety without garbage collection",
            "Machine learning models predict outcomes",
            "Kubernetes orchestrates container deployments",
        ]

        for content in captures:
            await logos.invoke("self.memory.capture", observer, content=content)

        # Search for web-related
        result = await logos.invoke(
            "self.memory.ghost.surface", observer, context="web browser JavaScript"
        )

        surfaced = result.get("surfaced", [])
        # Should find JavaScript content
        assert len(surfaced) > 0

        # Search for container-related
        result2 = await logos.invoke(
            "self.memory.ghost.surface", observer, context="container deployment"
        )

        surfaced2 = result2.get("surfaced", [])
        # Should find Kubernetes content
        assert len(surfaced2) > 0

    @pytest.mark.asyncio
    async def test_brain_logos_independent_instances(self) -> None:
        """Each create_brain_logos call creates independent instance."""
        from protocols.agentese import create_brain_logos

        logos1 = create_brain_logos(embedder_type="simple")
        logos2 = create_brain_logos(embedder_type="simple")

        observer = create_mock_umwelt()

        # Capture in logos1
        await logos1.invoke(
            "self.memory.capture", observer, content="Content only in logos1"
        )

        # Search in logos2 should find nothing
        result = await logos2.invoke(
            "self.memory.ghost.surface", observer, context="logos1"
        )

        assert result.get("count", 0) == 0
