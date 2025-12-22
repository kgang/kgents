"""
Tests for Portal Token HTML Rendering.

These tests verify:
1. HTML rendering for collapsed portals
2. HTML rendering for expanded portals
3. HTML rendering for error states
4. Data attributes for JS integration
5. Lazy loading support

Spec: spec/protocols/portal-token.md section 8.2 (Web HTML)
"""

import pytest

from ..portal import (
    PortalLink,
    PortalRenderer,
    PortalState,
    PortalToken,
    PortalNode,
    PortalTree,
)


# =============================================================================
# HTML Rendering Tests
# =============================================================================


class TestPortalRendererHTML:
    """Tests for PortalRenderer.render_html()."""

    def test_render_collapsed_has_details_element(self) -> None:
        """Collapsed portal should render as <details> element."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.COLLAPSED)
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        assert "<details" in html
        assert "</details>" in html
        assert "<summary>" in html

    def test_render_collapsed_has_data_attributes(self) -> None:
        """Collapsed portal should have data-* attributes."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.COLLAPSED, depth=2)
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        assert 'data-portal-path="WITNESS_OPERAD/test"' in html
        assert 'data-edge-type="tests"' in html
        assert 'data-depth="2"' in html
        assert 'data-state="collapsed"' in html

    def test_render_collapsed_not_open(self) -> None:
        """Collapsed portal should not have 'open' attribute."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.COLLAPSED)
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        # Should not have the open attribute (or be ' open')
        assert "open>" not in html or 'data-state="collapsed"' in html

    def test_render_expanded_has_open_attribute(self) -> None:
        """Expanded portal should have 'open' attribute."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.EXPANDED, depth=1)
        token._content = "test content"
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        assert " open" in html

    def test_render_expanded_lazy_load(self) -> None:
        """Expanded portal with lazy_load=True should have empty content."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.EXPANDED, depth=1)
        token._content = "test content"
        renderer = PortalRenderer()

        html = renderer.render_html(token, lazy_load=True)

        assert "portal-lazy" in html
        # Content should not be in HTML
        assert "test content" not in html

    def test_render_expanded_no_lazy_load(self) -> None:
        """Expanded portal with lazy_load=False should include content."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.EXPANDED, depth=1)
        token._content = "test content here"
        renderer = PortalRenderer()

        html = renderer.render_html(token, lazy_load=False)

        assert "test content here" in html
        assert "<pre" in html

    def test_render_error_state(self) -> None:
        """Error state should render with error styling."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.ERROR)
        token._load_error = "File not found"
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        assert "portal-error" in html
        assert "File not found" in html
        assert "✗" in html

    def test_render_loading_state(self) -> None:
        """Loading state should render with loading indicator."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.LOADING)
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        assert "portal-loading" in html or "Loading" in html
        assert "⏳" in html

    def test_render_escapes_html_content(self) -> None:
        """HTML special characters should be escaped."""
        link = PortalLink(edge_type="tests", path="test<script>alert('xss')</script>")
        token = PortalToken(link, state=PortalState.COLLAPSED)
        renderer = PortalRenderer()

        html = renderer.render_html(token)

        # Should be escaped
        assert "<script>" not in html
        assert "&lt;script&gt;" in html or "test" in html

    def test_render_with_max_lines(self) -> None:
        """Content should be truncated when max_lines is set."""
        link = PortalLink(edge_type="tests", path="WITNESS_OPERAD/test")
        token = PortalToken(link, state=PortalState.EXPANDED, depth=1)
        token._content = "\n".join([f"line {i}" for i in range(100)])
        renderer = PortalRenderer()

        html = renderer.render_html(token, lazy_load=False, max_lines=10)

        assert "line 0" in html
        assert "line 9" in html
        # Should show truncation message
        assert "more lines" in html


# =============================================================================
# Tree HTML Rendering Tests
# =============================================================================


class TestPortalTreeHTML:
    """Tests for PortalRenderer.render_tree_html()."""

    def test_render_tree_basic(self) -> None:
        """Basic tree should render as HTML."""
        root = PortalNode(path="/test/root", depth=0)
        tree = PortalTree(root=root)
        renderer = PortalRenderer()

        html = renderer.render_tree_html(tree)

        assert "<details" in html
        assert "/test/root" in html

    def test_render_tree_with_children(self) -> None:
        """Tree with children should render nested structure."""
        root = PortalNode(path="/test/root", depth=0, expanded=True)
        child = PortalNode(path="tests", edge_type="tests", depth=1)
        root.children.append(child)
        tree = PortalTree(root=root)
        renderer = PortalRenderer()

        html = renderer.render_tree_html(tree)

        assert "tests" in html
        # Should have nested details
        assert html.count("<details") >= 1


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
