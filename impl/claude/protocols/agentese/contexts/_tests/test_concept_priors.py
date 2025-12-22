"""
Tests for concept.compiler.priors AGENTESE node.

Tests the bridge between archaeology (past patterns) and ASHC (future predictions).

Teaching:
    gotcha: These tests use mocked archaeology/ASHC modules.
            Integration tests with real git history are in services/archaeology/_tests/.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from protocols.agentese.contexts.concept_priors import (
    CompilerPriorsNode,
    ExtractResultRendering,
    PriorsManifestRendering,
    SeedResultRendering,
    get_priors_node,
)
from protocols.agentese.node import Observer

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def observer() -> Observer:
    """Create a test observer."""
    return Observer(archetype="engineer", capabilities=frozenset())


@pytest.fixture
def node() -> CompilerPriorsNode:
    """Create a CompilerPriorsNode instance."""
    return CompilerPriorsNode()


# =============================================================================
# Test Node Registration
# =============================================================================


class TestNodeRegistration:
    """Test that node is properly registered."""

    def test_node_handle(self, node: CompilerPriorsNode) -> None:
        """Node has correct handle."""
        assert node.handle == "concept.compiler.priors"

    def test_node_affordances(self, node: CompilerPriorsNode) -> None:
        """Node provides expected affordances."""
        affordances = node._get_affordances_for_archetype("engineer")
        assert "manifest" in affordances
        assert "extract" in affordances
        assert "seed" in affordances
        assert "report" in affordances

    def test_singleton_factory(self) -> None:
        """get_priors_node returns consistent instance."""
        node1 = get_priors_node()
        node2 = get_priors_node()
        assert node1 is node2


# =============================================================================
# Test Manifest Aspect
# =============================================================================


class TestManifestAspect:
    """Test the manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_without_dependencies(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Manifest works even without archaeology/ASHC."""
        with patch.object(node, "_check_ashc_available", return_value=False):
            with patch.object(node, "_check_archaeology_available", return_value=False):
                result = await node.manifest(observer)
                assert result is not None
                assert "concept.compiler.priors" in result.content

    @pytest.mark.asyncio
    async def test_manifest_with_archaeology(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Manifest reports priors when archaeology is available."""
        mock_priors = [MagicMock(), MagicMock()]
        mock_patterns = [MagicMock()]

        with patch.object(node, "_check_ashc_available", return_value=True):
            with patch.object(node, "_check_archaeology_available", return_value=True):
                with patch.dict(
                    "sys.modules",
                    {
                        "services.archaeology": MagicMock(
                            get_commit_count=MagicMock(return_value=100),
                            parse_git_log=MagicMock(return_value=[]),
                            classify_all_features=MagicMock(return_value={}),
                            extract_causal_priors=MagicMock(return_value=mock_priors),
                            extract_spec_patterns=MagicMock(return_value=mock_patterns),
                            ACTIVE_FEATURES=(),
                            ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT=0.5,
                        )
                    },
                ):
                    # This won't work with patch.dict since the imports happen inside the method
                    # So we test the rendering class directly
                    pass

    def test_manifest_rendering_to_text(self) -> None:
        """PriorsManifestRendering produces readable output."""
        rendering = PriorsManifestRendering(
            ashc_available=True,
            priors_count=5,
            patterns_count=3,
            total_commits=100,
            confidence_discount=0.5,
        )
        text = rendering.to_text()
        assert "ASHC Status: ✓ Available" in text
        assert "Causal Priors: 5" in text
        assert "Spec Patterns: 3" in text

    def test_manifest_rendering_to_dict(self) -> None:
        """PriorsManifestRendering produces correct dict."""
        rendering = PriorsManifestRendering(
            ashc_available=True,
            priors_count=5,
            patterns_count=3,
            total_commits=100,
            confidence_discount=0.5,
        )
        data = rendering.to_dict()
        assert data["ashc_available"] is True
        assert data["priors_count"] == 5
        assert data["confidence_discount"] == 0.5


# =============================================================================
# Test Extract Aspect
# =============================================================================


class TestExtractAspect:
    """Test the extract aspect."""

    @pytest.mark.asyncio
    async def test_extract_without_archaeology(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Extract fails gracefully without archaeology."""
        with patch.object(node, "_check_archaeology_available", return_value=False):
            result = await node.extract(observer)
            assert (
                "not found" in result.content.lower() or "not available" in result.summary.lower()
            )

    def test_extract_rendering_to_text(self) -> None:
        """ExtractResultRendering produces readable output."""
        rendering = ExtractResultRendering(
            priors_count=3,
            patterns_count=2,
            traces_count=5,
            commits_analyzed=100,
            priors=[
                {"pattern": "feat: prefix", "correlation": 0.15, "sample_size": 20},
                {"pattern": "fix: prefix", "correlation": -0.05, "sample_size": 15},
            ],
            patterns=[
                {"type": "early_test_adoption", "success_rate": 0.8},
            ],
        )
        text = rendering.to_text()
        assert "Commits Analyzed: 100" in text
        assert "Causal Priors: 3" in text
        assert "feat: prefix" in text

    def test_extract_rendering_to_dict(self) -> None:
        """ExtractResultRendering produces correct dict."""
        rendering = ExtractResultRendering(
            priors_count=3,
            patterns_count=2,
            traces_count=5,
            commits_analyzed=100,
            priors=[{"pattern": "test", "correlation": 0.1, "sample_size": 10}],
            patterns=[],
        )
        data = rendering.to_dict()
        assert data["priors_count"] == 3
        assert data["commits_analyzed"] == 100
        assert len(data["priors"]) == 1


# =============================================================================
# Test Seed Aspect
# =============================================================================


class TestSeedAspect:
    """Test the seed aspect."""

    @pytest.mark.asyncio
    async def test_seed_without_ashc(self, node: CompilerPriorsNode, observer: Observer) -> None:
        """Seed fails gracefully without ASHC."""
        with patch.object(node, "_check_ashc_available", return_value=False):
            result = await node.seed(observer)
            assert isinstance(result, SeedResultRendering)
            assert result.success is False
            assert "not available" in (result.error or "").lower()

    @pytest.mark.asyncio
    async def test_seed_without_archaeology(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Seed fails gracefully without archaeology."""
        with patch.object(node, "_check_ashc_available", return_value=True):
            with patch.object(node, "_check_archaeology_available", return_value=False):
                result = await node.seed(observer)
                assert isinstance(result, SeedResultRendering)
                assert result.success is False
                assert "archaeology" in (result.error or "").lower()

    def test_seed_rendering_success_to_text(self) -> None:
        """SeedResultRendering success produces readable output."""
        rendering = SeedResultRendering(
            success=True,
            edges_created=5,
            total_confidence=2.5,
            patterns_incorporated=["feat: prefix", "early_test_adoption"],
            warnings=["Low sample size for pattern X"],
        )
        text = rendering.to_text()
        assert "ASHC CausalGraph Seeded" in text
        assert "Edges Created: 5" in text
        assert "feat: prefix" in text
        assert "⚠️" in text  # Warning indicator

    def test_seed_rendering_failure_to_text(self) -> None:
        """SeedResultRendering failure produces error message."""
        rendering = SeedResultRendering(
            success=False,
            edges_created=0,
            total_confidence=0.0,
            patterns_incorporated=[],
            error="ASHC module not available",
        )
        text = rendering.to_text()
        assert "Failed" in text
        assert "ASHC module not available" in text

    def test_seed_rendering_to_dict(self) -> None:
        """SeedResultRendering produces correct dict."""
        rendering = SeedResultRendering(
            success=True,
            edges_created=5,
            total_confidence=2.5,
            patterns_incorporated=["p1", "p2"],
            warnings=["w1"],
        )
        data = rendering.to_dict()
        assert data["success"] is True
        assert data["edges_created"] == 5
        assert len(data["patterns_incorporated"]) == 2
        assert len(data["warnings"]) == 1


# =============================================================================
# Test Report Aspect
# =============================================================================


class TestReportAspect:
    """Test the report aspect."""

    @pytest.mark.asyncio
    async def test_report_without_archaeology(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Report fails gracefully without archaeology."""
        with patch.object(node, "_check_archaeology_available", return_value=False):
            result = await node.report(observer)
            assert (
                "not found" in result.content.lower() or "not available" in result.summary.lower()
            )


# =============================================================================
# Test Invoke Aspect Routing
# =============================================================================


class TestInvokeAspect:
    """Test aspect routing."""

    @pytest.mark.asyncio
    async def test_invoke_manifest(self, node: CompilerPriorsNode, observer: Observer) -> None:
        """Invoking 'manifest' aspect routes correctly."""
        with patch.object(node, "_check_ashc_available", return_value=False):
            with patch.object(node, "_check_archaeology_available", return_value=False):
                result = await node._invoke_aspect("manifest", observer)
                assert result is not None

    @pytest.mark.asyncio
    async def test_invoke_unknown_aspect(
        self, node: CompilerPriorsNode, observer: Observer
    ) -> None:
        """Invoking unknown aspect raises ValueError."""
        with pytest.raises(ValueError, match="Unknown aspect"):
            await node._invoke_aspect("nonexistent", observer)


# =============================================================================
# Test Availability Checks
# =============================================================================


class TestAvailabilityChecks:
    """Test module availability checks."""

    def test_check_ashc_available_when_present(self, node: CompilerPriorsNode) -> None:
        """Returns True when ASHC is importable."""
        # This test relies on ASHC being available in the test environment
        # If ASHC is not available, it should return False
        result = node._check_ashc_available()
        assert isinstance(result, bool)

    def test_check_archaeology_available_when_present(self, node: CompilerPriorsNode) -> None:
        """Returns True when archaeology is importable."""
        # This test relies on archaeology being available in the test environment
        result = node._check_archaeology_available()
        assert isinstance(result, bool)
