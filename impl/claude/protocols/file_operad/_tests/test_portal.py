"""
Tests for portal token parsing and rendering.

"Navigation is expansion. Expansion is navigation."
"""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from protocols.file_operad.portal import (
    OPERADS_ROOT,
    PortalLink,
    PortalRenderer,
    PortalState,
    PortalToken,
    parse_portal_link,
    parse_wires_to,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_op_content() -> str:
    """Sample .op file content with Wires To section."""
    return dedent("""
        # mark: Record a Witness Trace

        > "The proof IS the decision. The mark IS the witness."

        **Arity**: 1
        **Symbol**: `\u2299`

        ---

        ## Type Signature

        ```
        mark : (Action, Reasoning, Evidence) -> Witness[Mark]
        ```

        ---

        ## Wires To

        - [enables] `WITNESS_OPERAD/walk` (traverse marks)
        - [feeds] `ASHC` (evidence for proof compilation)
        - [triggered_by] `AGENT_OPERAD/branch` (records alternatives)

        ---

        ## Examples

        ```python
        await witness.mark(action="Selected JWT", reasoning="Stateless")
        ```
    """).strip()


# =============================================================================
# Parsing Tests
# =============================================================================


class TestParsePortalLink:
    """Tests for parse_portal_link function."""

    def test_parse_basic_link(self) -> None:
        """Parse a basic portal link."""
        line = "- [enables] `WITNESS_OPERAD/walk` (traverse marks)"
        link = parse_portal_link(line)

        assert link is not None
        assert link.edge_type == "enables"
        assert link.path == "WITNESS_OPERAD/walk"
        assert link.note == "traverse marks"

    def test_parse_link_without_note(self) -> None:
        """Parse a link without parenthetical note."""
        line = "- [feeds] `ASHC`"
        link = parse_portal_link(line)

        assert link is not None
        assert link.edge_type == "feeds"
        assert link.path == "ASHC"
        assert link.note is None

    def test_parse_link_with_spaces(self) -> None:
        """Parse a link with leading spaces."""
        line = "  - [triggered_by] `AGENT_OPERAD/branch` (records alternatives)"
        link = parse_portal_link(line)

        assert link is not None
        assert link.edge_type == "triggered_by"
        assert link.path == "AGENT_OPERAD/branch"

    def test_non_link_returns_none(self) -> None:
        """Non-link lines return None."""
        assert parse_portal_link("# Some heading") is None
        assert parse_portal_link("Regular text") is None
        assert parse_portal_link("- [not a link]") is None


class TestParseWiresTo:
    """Tests for parse_wires_to function."""

    def test_parse_wires_section(self, sample_op_content: str) -> None:
        """Parse all links from Wires To section."""
        links = parse_wires_to(sample_op_content)

        assert len(links) == 3
        assert links[0].edge_type == "enables"
        assert links[1].edge_type == "feeds"
        assert links[2].edge_type == "triggered_by"

    def test_empty_content(self) -> None:
        """Empty content returns empty list."""
        assert parse_wires_to("") == []

    def test_no_wires_section(self) -> None:
        """Content without Wires To section returns empty list."""
        content = "# Some file\n\nNo wires here."
        assert parse_wires_to(content) == []


# =============================================================================
# PortalLink Tests
# =============================================================================


class TestPortalLink:
    """Tests for PortalLink data class."""

    def test_operad_name(self) -> None:
        """Extract operad name from path."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        assert link.operad_name == "WITNESS_OPERAD"

    def test_operation_name(self) -> None:
        """Extract operation name from path."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        assert link.operation_name == "walk"

    def test_external_reference(self) -> None:
        """External references (no /) have no operad/operation."""
        link = PortalLink(edge_type="feeds", path="ASHC")
        assert link.operad_name is None
        assert link.operation_name is None
        assert link.file_path is None

    def test_file_path_resolution(self) -> None:
        """Resolve to filesystem path."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        assert link.file_path == OPERADS_ROOT / "WITNESS_OPERAD" / "walk.op"


# =============================================================================
# PortalToken Tests
# =============================================================================


class TestPortalToken:
    """Tests for PortalToken state machine."""

    def test_initial_state(self) -> None:
        """Token starts in COLLAPSED state."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = PortalToken(link)

        assert token.state == PortalState.COLLAPSED
        assert token.content is None

    def test_render_collapsed(self) -> None:
        """Render collapsed state."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = PortalToken(link)

        rendered = token.render_collapsed()
        assert "[enables]" in rendered
        assert "WITNESS_OPERAD/walk" in rendered
        assert "\u25b6" in rendered  # Right-pointing triangle

    def test_load_missing_file(self) -> None:
        """Loading missing file sets ERROR state."""
        link = PortalLink(edge_type="enables", path="NONEXISTENT/file")
        token = PortalToken(link)

        result = token.load()
        assert result is False
        assert token.state == PortalState.ERROR

    def test_load_external_reference(self) -> None:
        """Loading external reference sets ERROR state."""
        link = PortalLink(edge_type="feeds", path="ASHC")
        token = PortalToken(link)

        result = token.load()
        assert result is False
        assert token.state == PortalState.ERROR


# =============================================================================
# Renderer Tests
# =============================================================================


class TestPortalRenderer:
    """Tests for PortalRenderer."""

    def test_render_cli_collapsed(self) -> None:
        """Render collapsed token for CLI."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = PortalToken(link)
        renderer = PortalRenderer()

        rendered = renderer.render_cli(token)
        assert "[enables]" in rendered
        assert "WITNESS_OPERAD/walk" in rendered

    def test_render_markdown_collapsed(self) -> None:
        """Render collapsed token for markdown."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = PortalToken(link)
        renderer = PortalRenderer()

        rendered = renderer.render_markdown(token)
        assert rendered.startswith(">")
        assert "[enables]" in rendered

    def test_render_llm_collapsed(self) -> None:
        """Render collapsed token for LLM context."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/walk")
        token = PortalToken(link)
        renderer = PortalRenderer()

        rendered = renderer.render_llm(token)
        assert "<!-- PORTAL:" in rendered
        assert "collapsed" in rendered


# =============================================================================
# Integration Tests (require actual files)
# =============================================================================


@pytest.mark.skipif(
    not (OPERADS_ROOT / "WITNESS_OPERAD" / "mark.op").exists(),
    reason="Requires bootstrapped operads",
)
class TestIntegration:
    """Integration tests requiring actual .op files."""

    def test_load_real_file(self) -> None:
        """Load a real .op file."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/mark")
        token = PortalToken(link)

        result = token.load()
        assert result is True
        assert token.state == PortalState.EXPANDED
        assert token.content is not None
        assert "mark" in token.content.lower()

    def test_nested_links_parsed(self) -> None:
        """Nested portal links are parsed from loaded content."""
        link = PortalLink(edge_type="enables", path="WITNESS_OPERAD/mark")
        token = PortalToken(link)
        token.load()

        # mark.op should have portal links
        assert len(token.nested_links) > 0


# =============================================================================
# PortalTree Tests
# =============================================================================


class TestPortalTreeToTrail:
    """Tests for PortalTree.to_trail() method."""

    def test_empty_tree_produces_single_step_trail(self) -> None:
        """A tree with just root produces a single-step trail."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        root = PortalNode(path="root.op", depth=0)
        tree = PortalTree(root=root)

        trail = tree.to_trail()

        assert len(trail.steps) == 1
        assert trail.steps[0].node == "root.op"
        assert trail.steps[0].edge_taken is None  # Root has no edge

    def test_expanded_tree_produces_dfs_trail(self) -> None:
        """Expanded tree produces trail in DFS order."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        # Build tree: root -> child1 (expanded) -> grandchild
        #                  -> child2 (collapsed)
        grandchild = PortalNode(path="grandchild.op", edge_type="covers", depth=2)
        child1 = PortalNode(
            path="child1.op",
            edge_type="tests",
            expanded=True,
            children=[grandchild],
            depth=1,
        )
        child2 = PortalNode(path="child2.op", edge_type="imports", expanded=False, depth=1)
        root = PortalNode(path="root.op", expanded=True, children=[child1, child2], depth=0)
        tree = PortalTree(root=root)

        trail = tree.to_trail(name="exploration")

        # DFS order: root -> child1 -> grandchild -> child2
        assert len(trail.steps) == 4
        assert trail.steps[0].node == "root.op"
        assert trail.steps[1].node == "child1.op"
        assert trail.steps[1].edge_taken == "tests"
        assert trail.steps[2].node == "grandchild.op"
        assert trail.steps[2].edge_taken == "covers"
        assert trail.steps[3].node == "child2.op"
        assert trail.name == "exploration"

    def test_collapsed_tree_only_includes_root(self) -> None:
        """Collapsed tree only includes root in trail."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        child = PortalNode(path="child.op", edge_type="tests", depth=1)
        root = PortalNode(path="root.op", expanded=False, children=[child], depth=0)
        tree = PortalTree(root=root)

        trail = tree.to_trail()

        # Only root because it's not expanded
        assert len(trail.steps) == 1
        assert trail.steps[0].node == "root.op"

    def test_trail_preserves_edge_types(self) -> None:
        """Trail preserves edge types from navigation."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        child = PortalNode(path="test_file.op", edge_type="tests", expanded=False, depth=1)
        root = PortalNode(path="main.op", expanded=True, children=[child], depth=0)
        tree = PortalTree(root=root)

        trail = tree.to_trail()

        assert trail.steps[1].edge_taken == "tests"


class TestPortalTreeRender:
    """Tests for PortalTree.render() method."""

    def test_render_collapsed_shows_triangle(self) -> None:
        """Collapsed nodes show right-pointing triangle."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        child = PortalNode(path="child.op", edge_type="tests", expanded=False, depth=1)
        root = PortalNode(path="root.op", expanded=True, children=[child], depth=0)
        tree = PortalTree(root=root)

        rendered = tree.render()

        assert "\u25b6" in rendered  # Right-pointing triangle (collapsed)
        assert "[tests]" in rendered
        assert "child.op" in rendered

    def test_render_expanded_shows_down_triangle(self) -> None:
        """Expanded nodes show down-pointing triangle."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        child = PortalNode(path="child.op", edge_type="tests", expanded=True, depth=1)
        root = PortalNode(path="root.op", expanded=True, children=[child], depth=0)
        tree = PortalTree(root=root)

        rendered = tree.render()

        assert "\u25bc" in rendered  # Down-pointing triangle (expanded)

    def test_render_respects_depth_limit(self) -> None:
        """Rendering respects max_depth parameter."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        # Deep tree: root -> child -> grandchild -> great_grandchild
        great = PortalNode(path="great.op", edge_type="deep", depth=3)
        grand = PortalNode(
            path="grand.op", edge_type="related", expanded=True, children=[great], depth=2
        )
        child = PortalNode(
            path="child.op", edge_type="tests", expanded=True, children=[grand], depth=1
        )
        root = PortalNode(path="root.op", expanded=True, children=[child], depth=0)
        tree = PortalTree(root=root)

        # Limit to depth 2 - should NOT include great_grandchild
        rendered = tree.render(max_depth=2)

        assert "root.op" in rendered
        assert "child.op" in rendered
        assert "grand.op" in rendered
        assert "great.op" not in rendered  # Beyond depth limit

    def test_render_root_has_no_connector(self) -> None:
        """Root node renders without edge type or connector."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        root = PortalNode(path="root.op", depth=0)
        tree = PortalTree(root=root)

        rendered = tree.render()

        # Root should just be the path, no connector symbols
        assert rendered.strip() == "root.op"

    def test_render_uses_box_drawing_characters(self) -> None:
        """Rendering uses proper box-drawing characters."""
        from protocols.file_operad.portal import PortalNode, PortalTree

        child = PortalNode(path="child.op", edge_type="tests", depth=1)
        root = PortalNode(path="root.op", expanded=True, children=[child], depth=0)
        tree = PortalTree(root=root)

        rendered = tree.render()

        # Should contain box-drawing L-corner
        assert "\u2514" in rendered or "\u251c" in rendered
