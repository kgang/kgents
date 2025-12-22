"""Tests for K-Block views.

Tests cover:
- View protocol compliance
- Token extraction from content
- View-specific rendering
- KBlock view integration
"""

import pytest

from ..core.kblock import KBlock, generate_kblock_id
from ..views import (
    SemanticToken,
    TokenKind,
    ViewType,
    create_view,
)
from ..views.code import CodeView
from ..views.diff import DiffView
from ..views.graph import GraphView
from ..views.outline import OutlineView
from ..views.prose import ProseView

# =============================================================================
# ProseView Tests
# =============================================================================


class TestProseView:
    """Tests for ProseView token extraction."""

    def test_extracts_headings(self) -> None:
        """ProseView extracts heading tokens from markdown."""
        view = ProseView()
        view.render("# Title\n\nSome content\n\n## Subsection")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.HEADING and t.value == "Title" for t in tokens)
        assert any(t.kind == TokenKind.HEADING and t.value == "Subsection" for t in tokens)

    def test_extracts_fields(self) -> None:
        """ProseView extracts field definitions."""
        view = ProseView()
        view.render("# Type\n- name: string\n- age: int")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.FIELD and t.value == "name" for t in tokens)
        assert any(t.kind == TokenKind.FIELD and t.value == "age" for t in tokens)

    def test_extracts_types(self) -> None:
        """ProseView extracts type declarations."""
        view = ProseView()
        view.render("# Code\nclass Person:\n    name: str")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.TYPE and t.value == "Person" for t in tokens)

    def test_extracts_references(self) -> None:
        """ProseView extracts wiki-style references."""
        view = ProseView()
        view.render("See [[other-doc]] for details about [[concept]].")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.RELATION and t.value == "other-doc" for t in tokens)
        assert any(t.kind == TokenKind.RELATION and t.value == "concept" for t in tokens)

    def test_view_type(self) -> None:
        """ProseView reports correct view type."""
        view = ProseView()
        assert view.view_type == ViewType.PROSE

    def test_to_canonical(self) -> None:
        """ProseView returns original content for to_canonical."""
        view = ProseView()
        content = "# Title\nSome content"
        view.render(content)
        assert view.to_canonical() == content

    def test_ignores_urls_in_fields(self) -> None:
        """ProseView ignores URLs that look like field definitions."""
        view = ProseView()
        view.render("- http://example.com: some site")
        tokens = view.tokens()

        # Should NOT extract http as a field
        assert not any(t.value.startswith("http") for t in tokens)


# =============================================================================
# GraphView Tests
# =============================================================================


class TestGraphView:
    """Tests for GraphView DAG rendering."""

    def test_extracts_nodes_from_headings(self) -> None:
        """GraphView creates nodes from headings."""
        view = GraphView()
        view.render("# Root\n## Child\n### Grandchild")

        assert len(view.nodes) == 3
        assert any(n.label == "Root" for n in view.nodes)
        assert any(n.label == "Child" for n in view.nodes)

    def test_creates_containment_edges(self) -> None:
        """GraphView creates edges for heading hierarchy."""
        view = GraphView()
        view.render("# Root\n## Child")

        assert len(view.edges) >= 1
        assert any(e.kind == "contains" for e in view.edges)

    def test_creates_field_nodes(self) -> None:
        """GraphView creates nodes for fields under headings."""
        view = GraphView()
        view.render("# Person\n- name: string\n- age: int")

        field_nodes = [n for n in view.nodes if n.kind == "field"]
        assert len(field_nodes) == 2

    def test_renders_dot_format(self) -> None:
        """GraphView renders to DOT graph format."""
        view = GraphView()
        output = view.render("# Root\n## Child")

        assert "digraph G" in output
        assert "Root" in output
        assert "Child" in output

    def test_tokens_match_nodes(self) -> None:
        """GraphView tokens correspond to graph nodes."""
        view = GraphView()
        view.render("# Title\n- field: type")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.HEADING and t.value == "Title" for t in tokens)
        assert any(t.kind == TokenKind.FIELD and t.value == "field" for t in tokens)


# =============================================================================
# CodeView Tests
# =============================================================================


class TestCodeView:
    """Tests for CodeView dataclass rendering."""

    def test_extracts_class_name_from_heading(self) -> None:
        """CodeView uses first heading as class name."""
        view = CodeView()
        view.render("# Person\n- name: string")

        assert view._class_name == "Person"

    def test_extracts_fields(self) -> None:
        """CodeView extracts field definitions."""
        view = CodeView()
        view.render("# Person\n- name: string\n- age: int")

        assert len(view.fields) == 2
        assert any(f.name == "name" for f in view.fields)
        assert any(f.name == "age" for f in view.fields)

    def test_normalizes_types(self) -> None:
        """CodeView normalizes common type names."""
        view = CodeView()
        view.render("# Type\n- name: string\n- count: integer")

        name_field = next(f for f in view.fields if f.name == "name")
        count_field = next(f for f in view.fields if f.name == "count")

        assert name_field.type_hint == "str"
        assert count_field.type_hint == "int"

    def test_renders_python_dataclass(self) -> None:
        """CodeView renders valid Python dataclass code."""
        view = CodeView()
        output = view.render("# Person\n- name: str\n- age: int")

        assert "@dataclass" in output
        assert "class Person:" in output
        assert "name: str" in output
        assert "age: int" in output

    def test_tokens_from_fields(self) -> None:
        """CodeView tokens include extracted fields."""
        view = CodeView()
        view.render("# Person\n- name: str")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.TYPE and t.value == "Person" for t in tokens)
        assert any(t.kind == TokenKind.FIELD and t.value == "name" for t in tokens)


# =============================================================================
# DiffView Tests
# =============================================================================


class TestDiffView:
    """Tests for DiffView unified diff rendering."""

    def test_no_changes(self) -> None:
        """DiffView shows no changes for identical content."""
        view = DiffView()
        content = "Same content"
        view.render(content, content)

        assert "(no changes)" in view.diff
        assert not view.has_changes

    def test_shows_additions(self) -> None:
        """DiffView shows added lines."""
        view = DiffView()
        view.render("Line 1\nLine 2\nLine 3", "Line 1\nLine 2")

        assert view.additions >= 1
        assert "+Line 3" in view.diff or "Line 3" in view.diff

    def test_shows_deletions(self) -> None:
        """DiffView shows deleted lines."""
        view = DiffView()
        view.render("Line 1", "Line 1\nLine 2")

        assert view.deletions >= 1

    def test_read_only(self) -> None:
        """DiffView tokens are empty (read-only view)."""
        view = DiffView()
        view.render("New", "Old")

        assert len(view.tokens()) == 0

    def test_has_changes_property(self) -> None:
        """DiffView.has_changes reflects content difference."""
        view = DiffView()

        view.render("A", "A")
        assert not view.has_changes

        view.render("A", "B")
        assert view.has_changes


# =============================================================================
# OutlineView Tests
# =============================================================================


class TestOutlineView:
    """Tests for OutlineView heading hierarchy."""

    def test_builds_tree_from_headings(self) -> None:
        """OutlineView builds tree structure from headings."""
        view = OutlineView()
        view.render("# Root\n## Child 1\n## Child 2")

        assert len(view.root.children) >= 1
        root_child = view.root.children[0]
        assert root_child.title == "Root"

    def test_nests_by_level(self) -> None:
        """OutlineView nests children by heading level."""
        view = OutlineView()
        view.render("# A\n## B\n### C")

        # A is child of root
        a_node = view.root.children[0]
        assert a_node.title == "A"

        # B is child of A
        assert len(a_node.children) == 1
        b_node = a_node.children[0]
        assert b_node.title == "B"

        # C is child of B
        assert len(b_node.children) == 1
        assert b_node.children[0].title == "C"

    def test_renders_indented_text(self) -> None:
        """OutlineView renders as indented text."""
        view = OutlineView()
        output = view.render("# Title\n## Section")

        assert "Title" in output
        assert "Section" in output

    def test_tokens_from_headings(self) -> None:
        """OutlineView tokens include all headings."""
        view = OutlineView()
        view.render("# A\n## B")
        tokens = view.tokens()

        assert any(t.kind == TokenKind.HEADING and t.value == "A" for t in tokens)
        assert any(t.kind == TokenKind.HEADING and t.value == "B" for t in tokens)

    def test_to_dict(self) -> None:
        """OutlineView can convert to dictionary."""
        view = OutlineView()
        view.render("# Title")
        d = view.to_dict()

        assert d["id"] == "root"
        assert len(d["children"]) >= 1


# =============================================================================
# View Factory Tests
# =============================================================================


class TestCreateView:
    """Tests for create_view factory function."""

    @pytest.mark.parametrize(
        "view_type,expected_class",
        [
            (ViewType.PROSE, ProseView),
            (ViewType.GRAPH, GraphView),
            (ViewType.CODE, CodeView),
            (ViewType.DIFF, DiffView),
            (ViewType.OUTLINE, OutlineView),
        ],
    )
    def test_creates_correct_view_type(self, view_type: ViewType, expected_class: type) -> None:
        """create_view returns correct view class for each type."""
        view = create_view(view_type)
        assert isinstance(view, expected_class)


# =============================================================================
# KBlock View Integration Tests
# =============================================================================


class TestKBlockViews:
    """Tests for KBlock view integration."""

    def test_activate_view(self) -> None:
        """KBlock.activate_view creates and caches view."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# Test\n- field: type",
            base_content="# Test",
        )

        view = block.activate_view(ViewType.PROSE)

        assert view.view_type == ViewType.PROSE
        assert ViewType.PROSE in block.views

    def test_activate_multiple_views(self) -> None:
        """KBlock can activate multiple views."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# Test\n- field: type",
            base_content="# Test",
        )

        block.activate_view(ViewType.PROSE)
        block.activate_view(ViewType.GRAPH)
        block.activate_view(ViewType.CODE)

        assert len(block.views) == 3

    def test_views_share_tokens(self) -> None:
        """Multiple views extract consistent tokens from same content."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# Title\n- name: string",
            base_content="",
        )

        prose = block.activate_view(ViewType.PROSE)
        graph = block.activate_view(ViewType.GRAPH)
        code = block.activate_view(ViewType.CODE)

        # All views should have "name" field token
        prose_fields = {t.value for t in prose.tokens() if t.kind == TokenKind.FIELD}
        graph_fields = {t.value for t in graph.tokens() if t.kind == TokenKind.FIELD}
        code_fields = {t.value for t in code.tokens() if t.kind == TokenKind.FIELD}

        assert "name" in prose_fields
        assert "name" in graph_fields
        assert "name" in code_fields

    def test_refresh_views(self) -> None:
        """KBlock.refresh_views updates all views with current content."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# Old",
            base_content="# Old",
        )

        # Activate views with old content
        block.activate_view(ViewType.PROSE)
        block.activate_view(ViewType.OUTLINE)

        # Change content
        block.content = "# New\n## Section"

        # Refresh views
        block.refresh_views()

        # Outline should now have "New" and "Section"
        outline_tokens = block.views[ViewType.OUTLINE].tokens()
        assert any(t.value == "New" for t in outline_tokens)
        assert any(t.value == "Section" for t in outline_tokens)

    def test_diff_view_uses_base_content(self) -> None:
        """DiffView compares current content against base_content."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# New Content",
            base_content="# Old Content",
        )

        diff = block.activate_view(ViewType.DIFF)
        assert diff.has_changes

    def test_active_view_types(self) -> None:
        """active_view_types returns set of activated views."""
        block = KBlock(
            id=generate_kblock_id(),
            path="test.md",
            content="# Test",
            base_content="",
        )

        assert len(block.active_view_types()) == 0

        block.activate_view(ViewType.PROSE)
        block.activate_view(ViewType.CODE)

        types = block.active_view_types()
        assert ViewType.PROSE in types
        assert ViewType.CODE in types


# =============================================================================
# Token Tests
# =============================================================================


class TestSemanticToken:
    """Tests for SemanticToken."""

    def test_frozen(self) -> None:
        """SemanticToken is immutable."""
        token = SemanticToken(id="t-1", kind=TokenKind.HEADING, value="Title")

        with pytest.raises(AttributeError):
            token.value = "Changed"  # type: ignore

    def test_hashable(self) -> None:
        """SemanticToken is hashable for use in sets."""
        t1 = SemanticToken(id="t-1", kind=TokenKind.HEADING, value="A")
        t2 = SemanticToken(id="t-2", kind=TokenKind.HEADING, value="B")

        tokens = {t1, t2}
        assert len(tokens) == 2

    def test_repr(self) -> None:
        """SemanticToken has readable repr."""
        token = SemanticToken(id="t-1", kind=TokenKind.HEADING, value="Title", position=5)
        r = repr(token)

        assert "heading" in r
        assert "Title" in r
        assert "@5" in r
