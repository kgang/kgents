"""
Tests for Living Docs Projector.

Type I: Unit tests for observer-dependent projection.
"""

from __future__ import annotations

import pytest

from services.living_docs.projector import (
    DENSITY_PARAMS,
    LivingDocsProjector,
    project,
)
from services.living_docs.types import (
    DocNode,
    LivingDocsObserver,
    TeachingMoment,
    Tier,
)


class TestProjectFunction:
    """Tests for the project() function."""

    @pytest.fixture
    def rich_node(self) -> DocNode:
        """A RICH tier DocNode with teaching moments."""
        return DocNode(
            symbol="important_function",
            signature="def important_function(x: int) -> bool",
            summary="An important function that does something critical.",
            examples=("important_function(42)", "important_function(0)"),
            teaching=(
                TeachingMoment(
                    insight="Always validate input before calling.",
                    severity="critical",
                    evidence="test_important.py::test_validation",
                ),
                TeachingMoment(
                    insight="Consider caching results for performance.",
                    severity="info",
                ),
            ),
            tier=Tier.RICH,
            module="services.core",
        )

    @pytest.fixture
    def minimal_node(self) -> DocNode:
        """A MINIMAL tier DocNode."""
        return DocNode(
            symbol="_helper",
            signature="def _helper()",
            summary="",
            tier=Tier.MINIMAL,
        )

    # === Agent Projection ===

    def test_agent_projection_structured_format(self, rich_node: DocNode) -> None:
        """Agent projection uses structured format."""
        observer = LivingDocsObserver(kind="agent")
        surface = project(rich_node, observer)

        assert surface.format == "structured"
        assert rich_node.symbol in surface.content
        assert rich_node.signature in surface.content

    def test_agent_projection_includes_gotchas(self, rich_node: DocNode) -> None:
        """Agent projection includes gotchas as list."""
        observer = LivingDocsObserver(kind="agent")
        surface = project(rich_node, observer)

        assert "Gotchas:" in surface.content
        assert "validate input" in surface.content.lower()

    def test_agent_projection_limits_examples(self, rich_node: DocNode) -> None:
        """Agent projection includes only first example."""
        observer = LivingDocsObserver(kind="agent")
        surface = project(rich_node, observer)

        # Should have first example but be brief
        assert "important_function(42)" in surface.content

    def test_agent_projection_metadata(self, rich_node: DocNode) -> None:
        """Agent projection includes useful metadata."""
        observer = LivingDocsObserver(kind="agent")
        surface = project(rich_node, observer)

        assert surface.metadata["symbol"] == rich_node.symbol
        assert surface.metadata["gotcha_count"] == 2
        assert surface.metadata["example_count"] == 2

    # === IDE Projection ===

    def test_ide_projection_tooltip_format(self, rich_node: DocNode) -> None:
        """IDE projection uses tooltip format."""
        observer = LivingDocsObserver(kind="ide")
        surface = project(rich_node, observer)

        assert surface.format == "tooltip"

    def test_ide_projection_minimal_content(self, rich_node: DocNode) -> None:
        """IDE projection is minimal: signature + critical gotcha."""
        observer = LivingDocsObserver(kind="ide")
        surface = project(rich_node, observer)

        # Should have signature
        assert rich_node.signature in surface.content

        # Should have critical gotcha (not all)
        lines = surface.content.split("\n")
        assert len(lines) <= 3  # Signature + maybe one gotcha

    def test_ide_projection_prioritizes_critical(self, rich_node: DocNode) -> None:
        """IDE projection shows critical gotcha over info."""
        observer = LivingDocsObserver(kind="ide")
        surface = project(rich_node, observer)

        # Critical one should appear
        assert "validate" in surface.content.lower()
        # Info one should not
        assert "caching" not in surface.content.lower()

    def test_ide_projection_truncates_long_insight(self) -> None:
        """Long insights are truncated for tooltips."""
        node = DocNode(
            symbol="func",
            signature="def func()",
            summary="",
            teaching=(
                TeachingMoment(
                    insight="A" * 200,  # Very long insight
                    severity="critical",
                ),
            ),
            tier=Tier.STANDARD,
        )
        observer = LivingDocsObserver(kind="ide")
        surface = project(node, observer)

        # Should be truncated
        assert "..." in surface.content
        assert len(surface.content) < 200

    # === Human Projection ===

    def test_human_projection_markdown_format(self, rich_node: DocNode) -> None:
        """Human projection uses markdown format."""
        observer = LivingDocsObserver(kind="human")
        surface = project(rich_node, observer)

        assert surface.format == "markdown"

    def test_human_projection_includes_header(self, rich_node: DocNode) -> None:
        """Human projection includes markdown header."""
        observer = LivingDocsObserver(kind="human")
        surface = project(rich_node, observer)

        assert f"## {rich_node.symbol}" in surface.content

    # === Density Tests ===

    def test_compact_density_truncates(self, rich_node: DocNode) -> None:
        """Compact density truncates content."""
        observer = LivingDocsObserver(kind="human", density="compact")
        surface = project(rich_node, observer)

        # Summary should be truncated
        params = DENSITY_PARAMS["compact"]
        # Check that content is shorter (details hidden)
        assert "Things to Know" not in surface.content  # No teaching section

    def test_comfortable_density_shows_details(self, rich_node: DocNode) -> None:
        """Comfortable density shows details."""
        observer = LivingDocsObserver(kind="human", density="comfortable")
        surface = project(rich_node, observer)

        # Should have examples section
        assert "Examples" in surface.content

        # Should have teaching section
        assert "Things to Know" in surface.content

    def test_spacious_density_full_content(self, rich_node: DocNode) -> None:
        """Spacious density shows full content."""
        observer = LivingDocsObserver(kind="human", density="spacious")
        surface = project(rich_node, observer)

        # All examples
        for example in rich_node.examples:
            assert example in surface.content

        # All teaching moments
        for moment in rich_node.teaching:
            assert moment.insight in surface.content

    def test_density_only_affects_human(self, rich_node: DocNode) -> None:
        """Density parameter only affects human observers."""
        agent_compact = project(rich_node, LivingDocsObserver(kind="agent", density="compact"))
        agent_spacious = project(rich_node, LivingDocsObserver(kind="agent", density="spacious"))

        # Agent output should be identical regardless of density
        assert agent_compact.content == agent_spacious.content
        assert agent_compact.format == agent_spacious.format


class TestLivingDocsProjector:
    """Tests for LivingDocsProjector class."""

    @pytest.fixture
    def projector(self) -> LivingDocsProjector:
        return LivingDocsProjector()

    @pytest.fixture
    def nodes(self) -> list[DocNode]:
        return [
            DocNode(
                symbol="func1",
                signature="def func1()",
                summary="First function",
                tier=Tier.STANDARD,
            ),
            DocNode(
                symbol="func2",
                signature="def func2()",
                summary="Second function",
                teaching=(TeachingMoment(insight="Watch out!", severity="warning"),),
                tier=Tier.RICH,
            ),
            DocNode(
                symbol="_private",
                signature="def _private()",
                summary="",
                tier=Tier.MINIMAL,
            ),
        ]

    def test_project_many(self, projector: LivingDocsProjector, nodes: list[DocNode]) -> None:
        """project_many projects all nodes."""
        observer = LivingDocsObserver(kind="agent")
        surfaces = projector.project_many(nodes, observer)

        assert len(surfaces) == 3
        assert all(s.format == "structured" for s in surfaces)

    def test_project_with_filter_tier(
        self, projector: LivingDocsProjector, nodes: list[DocNode]
    ) -> None:
        """project_with_filter respects min_tier."""
        observer = LivingDocsObserver(kind="human")

        # Only RICH or higher
        rich_only = projector.project_with_filter(nodes, observer, min_tier=Tier.RICH)
        assert len(rich_only) == 1

        # STANDARD or higher (excludes MINIMAL)
        standard_up = projector.project_with_filter(nodes, observer, min_tier=Tier.STANDARD)
        assert len(standard_up) == 2

    def test_project_with_filter_teaching(
        self, projector: LivingDocsProjector, nodes: list[DocNode]
    ) -> None:
        """project_with_filter respects only_with_teaching."""
        observer = LivingDocsObserver(kind="human")

        with_teaching = projector.project_with_filter(nodes, observer, only_with_teaching=True)
        # Only func2 has teaching moments
        assert len(with_teaching) == 1


class TestFunctorLaw:
    """Test the functor law: project preserves structure."""

    def test_same_observer_same_output(self) -> None:
        """Same node + same observer = same output (deterministic)."""
        node = DocNode(
            symbol="test",
            signature="def test()",
            summary="Test function",
            tier=Tier.STANDARD,
        )
        observer = LivingDocsObserver(kind="agent")

        surface1 = project(node, observer)
        surface2 = project(node, observer)

        assert surface1.content == surface2.content
        assert surface1.format == surface2.format
        assert surface1.metadata == surface2.metadata
