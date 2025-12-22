"""
Tests for the Outline Model.

These tests verify the core data structures and operations for Context Perception.

Spec: spec/protocols/context-perception.md §4
"""

from __future__ import annotations

from datetime import datetime

import pytest

from ..outline import (
    AnnotationSnippet,
    AnnotationType,
    Clipboard,
    Location,
    Outline,
    OutlineNode,
    OutlineOperations,
    PortalToken,
    Range,
    SnippetType,
    TextSnippet,
    create_outline,
    create_snippet,
)

# === Range Tests ===


class TestRange:
    """Tests for Range selection."""

    def test_valid_range(self) -> None:
        """Range with valid coordinates."""
        r = Range(start_line=0, start_col=5, end_line=2, end_col=10)
        assert r.start_line == 0
        assert r.end_col == 10

    def test_single_line_range(self) -> None:
        """Range on a single line."""
        r = Range(start_line=5, start_col=0, end_line=5, end_col=20)
        assert not r.is_empty

    def test_empty_range(self) -> None:
        """Empty range (same start and end)."""
        r = Range(start_line=5, start_col=10, end_line=5, end_col=10)
        assert r.is_empty

    def test_invalid_line_order(self) -> None:
        """Start line after end line raises."""
        with pytest.raises(ValueError, match="start_line must be"):
            Range(start_line=10, start_col=0, end_line=5, end_col=0)

    def test_invalid_col_order_same_line(self) -> None:
        """Start col after end col on same line raises."""
        with pytest.raises(ValueError, match="start_col must be"):
            Range(start_line=5, start_col=20, end_line=5, end_col=10)

    def test_contains_point(self) -> None:
        """Check if point is within range."""
        r = Range(start_line=5, start_col=10, end_line=10, end_col=20)

        # Inside
        assert r.contains(7, 15)

        # On boundaries
        assert r.contains(5, 10)  # Start
        assert r.contains(10, 20)  # End

        # Outside
        assert not r.contains(4, 0)  # Before
        assert not r.contains(11, 0)  # After
        assert not r.contains(5, 5)  # Same line, before start col


# === Location Tests ===


class TestLocation:
    """Tests for Location within outline."""

    def test_location_str(self) -> None:
        """Location string representation."""
        loc = Location(node_path="root.tests.0", line=10, col=5)
        assert str(loc) == "root.tests.0:10:5"


# === TextSnippet Tests ===


class TestTextSnippet:
    """Tests for TextSnippet with invisible metadata."""

    def test_basic_snippet(self) -> None:
        """Create a basic text snippet."""
        s = create_snippet("Hello, world!")
        assert s.visible_text == "Hello, world!"
        assert s.snippet_type == SnippetType.PROSE
        assert s.source_path is None

    def test_snippet_with_source(self) -> None:
        """Snippet with source path."""
        s = create_snippet("Some code", source_path="world.auth.middleware")
        assert s.source_path == "world.auth.middleware"

    def test_with_provenance(self) -> None:
        """Add provenance to snippet."""
        s = create_snippet("Original text")
        s2 = s.with_provenance("world.source", "observer_123")

        # New snippet has provenance
        assert s2.source_path == "world.source"
        assert s2.copied_by == "observer_123"
        assert s2.copied_at is not None

        # Original unchanged
        assert s.source_path is None

        # New ID assigned
        assert s2.id != s.id

    def test_add_link(self) -> None:
        """Add outgoing link to snippet."""
        s = create_snippet("Text with link")
        s2 = s.add_link("world.target")

        assert "world.target" in s2.links
        assert "world.target" not in s.links  # Original unchanged

    def test_add_link_idempotent(self) -> None:
        """Adding same link twice is idempotent."""
        s = create_snippet("Text")
        s2 = s.add_link("world.target")
        s3 = s2.add_link("world.target")

        assert s3.links.count("world.target") == 1


# === PortalToken Tests ===


class TestPortalToken:
    """Tests for PortalToken expandable hyperedges."""

    def test_collapsed_portal(self) -> None:
        """Collapsed portal rendering."""
        p = PortalToken(
            source_path="world.auth",
            edge_type="tests",
            destinations=["world.test_auth", "world.test_auth_edge"],
        )

        assert not p.expanded
        assert p.destination_count == 2
        assert p.summary == "2 files"
        assert p.render_collapsed() == "▶ [tests] ──→ 2 files"

    def test_expanded_portal(self) -> None:
        """Expanded portal rendering."""
        p = PortalToken(
            source_path="world.auth",
            edge_type="implements",
            destinations=["world.spec.auth"],
            expanded=True,
        )

        assert p.expanded
        assert p.summary == "auth"  # Single file shows name
        assert p.render_expanded() == "▼ [implements] ──→ auth"

    def test_empty_portal(self) -> None:
        """Portal with no destinations."""
        p = PortalToken(
            source_path="world.foo",
            edge_type="tests",
            destinations=[],
        )

        assert p.destination_count == 0
        assert p.summary == "(empty)"

    def test_lazy_content(self) -> None:
        """Portal content is lazy-loaded."""
        p = PortalToken(
            source_path="world.auth",
            edge_type="tests",
            destinations=["world.test_auth"],
        )

        # Content not loaded initially
        assert p._content is None
        assert p.get_content("world.test_auth") is None

        # Set content
        p.set_content({"world.test_auth": "def test_foo(): pass"})

        # Now available
        assert p.get_content("world.test_auth") == "def test_foo(): pass"


# === OutlineNode Tests ===


class TestOutlineNode:
    """Tests for OutlineNode tree structure."""

    def test_node_with_snippet(self) -> None:
        """Node containing a snippet."""
        s = create_snippet("Hello")
        node = OutlineNode(snippet=s, path="root")

        assert node.content_type == "snippet"
        assert node.visible_text == "Hello"
        assert node.is_expanded  # Prose is expanded by default

    def test_node_with_portal(self) -> None:
        """Node containing a portal."""
        p = PortalToken(
            source_path="world.auth",
            edge_type="tests",
            destinations=["world.test"],
        )
        node = OutlineNode(portal=p, path="root.0")

        assert node.content_type == "portal"
        assert not node.is_expanded  # Portal collapsed by default
        assert "▶" in node.visible_text

    def test_node_requires_content(self) -> None:
        """Node must have either snippet or portal."""
        with pytest.raises(ValueError, match="must have either"):
            OutlineNode(path="root")

    def test_node_exclusive_content(self) -> None:
        """Node cannot have both snippet and portal."""
        s = create_snippet("Hello")
        p = PortalToken(source_path="", edge_type="", destinations=[])

        with pytest.raises(ValueError, match="cannot have both"):
            OutlineNode(snippet=s, portal=p, path="root")

    def test_add_child(self) -> None:
        """Add child nodes."""
        parent = OutlineNode(snippet=create_snippet("Parent"), path="root")
        child = OutlineNode(snippet=create_snippet("Child"))

        parent.add_child(child)

        assert len(parent.children) == 1
        assert child.parent is parent
        assert child.depth == 1
        assert child.path == "root.0"

    def test_find_node(self) -> None:
        """Find node by path."""
        root = OutlineNode(snippet=create_snippet("Root"), path="root")
        child1 = OutlineNode(snippet=create_snippet("Child 1"))
        child2 = OutlineNode(snippet=create_snippet("Child 2"))

        root.add_child(child1)
        root.add_child(child2)

        # Find by path
        assert root.find_node("root") is root
        assert root.find_node("root.0") is child1
        assert root.find_node("root.1") is child2
        assert root.find_node("nonexistent") is None


# === Clipboard Tests ===


class TestClipboard:
    """Tests for Clipboard with provenance."""

    def test_clipboard_creation(self) -> None:
        """Create clipboard with provenance."""
        cb = Clipboard(
            visible_text="Copied text",
            source_path="world.auth.middleware",
            source_range=Range(0, 0, 0, 11),
            copied_by="observer_123",
        )

        assert cb.visible_text == "Copied text"
        assert cb.source_path == "world.auth.middleware"

    def test_clipboard_to_snippet(self) -> None:
        """Convert clipboard to snippet."""
        cb = Clipboard(
            visible_text="Pasted text",
            source_path="world.source",
            source_range=Range(0, 0, 0, 10),
            copied_by="kent",
        )

        snippet = cb.to_snippet()

        assert snippet.visible_text == "Pasted text"
        assert snippet.source_path == "world.source"
        assert snippet.copied_by == "kent"


# === Outline Tests ===


class TestOutline:
    """Tests for Outline container."""

    def test_create_outline(self) -> None:
        """Create a new outline."""
        outline = create_outline("# My Investigation", "kent")

        assert outline.observer_id == "kent"
        assert outline.root is not None
        assert outline.root.snippet.visible_text == "# My Investigation"

    def test_budget_tracking(self) -> None:
        """Track navigation budget."""
        outline = create_outline(max_steps=100)

        assert outline.budget_remaining == 1.0
        assert not outline.is_budget_low

        # Use some budget
        outline.steps_taken = 85
        assert outline.budget_remaining == pytest.approx(0.15)
        assert outline.is_budget_low

    def test_record_step(self) -> None:
        """Record navigation steps."""
        outline = create_outline()

        outline.record_step("expand", "root.tests", "tests")
        outline.record_step("navigate", "root.tests.0")

        assert len(outline.trail_steps) == 2
        assert outline.steps_taken == 2
        assert outline.trail_steps[0]["action"] == "expand"
        assert outline.trail_steps[0]["edge_type"] == "tests"


# === OutlineOperations Tests ===


class TestOutlineOperations:
    """Tests for outline operations with hidden magic."""

    @pytest.fixture
    def outline_with_portal(self) -> Outline:
        """Create outline with a portal."""
        outline = create_outline("# Root")

        portal = PortalToken(
            source_path="world.auth",
            edge_type="tests",
            destinations=["world.test_auth"],
        )
        portal_node = OutlineNode(portal=portal)
        outline.root.add_child(portal_node)

        return outline

    @pytest.mark.asyncio
    async def test_expand_portal(self, outline_with_portal: Outline) -> None:
        """Expand a portal records trail step."""
        ops = OutlineOperations(outline_with_portal, "kent")

        # Initially collapsed
        portal_node = outline_with_portal.root.children[0]
        assert not portal_node.portal.expanded

        # Expand
        result = await ops.expand("root.0")

        assert result is True
        assert portal_node.portal.expanded
        assert len(outline_with_portal.trail_steps) == 1
        assert outline_with_portal.trail_steps[0]["action"] == "expand"

    @pytest.mark.asyncio
    async def test_expand_idempotent(self, outline_with_portal: Outline) -> None:
        """Expanding already-expanded portal is idempotent."""
        ops = OutlineOperations(outline_with_portal)

        await ops.expand("root.0")
        await ops.expand("root.0")  # Second call

        # Only one trail step (first expand)
        # Law 11.1: expand(expand(portal)) ≡ expand(portal)
        assert len(outline_with_portal.trail_steps) == 1

    @pytest.mark.asyncio
    async def test_collapse_portal(self, outline_with_portal: Outline) -> None:
        """Collapse an expanded portal."""
        ops = OutlineOperations(outline_with_portal)

        # Expand first
        await ops.expand("root.0")
        portal_node = outline_with_portal.root.children[0]
        assert portal_node.portal.expanded

        # Collapse
        result = await ops.collapse("root.0")

        assert result is True
        assert not portal_node.portal.expanded
        assert len(outline_with_portal.trail_steps) == 2

    @pytest.mark.asyncio
    async def test_copy_with_provenance(self) -> None:
        """Copy operation preserves provenance."""
        outline = create_outline("Line one\nLine two\nLine three")
        ops = OutlineOperations(outline, "kent")

        selection = Range(start_line=1, start_col=0, end_line=1, end_col=8)
        clipboard = await ops.copy("root", selection)

        # Law 11.3: paste(copy(snippet)).source ≡ snippet.path
        assert clipboard.source_path == "root"
        assert clipboard.copied_by == "kent"
        assert clipboard.visible_text == "Line two"

    @pytest.mark.asyncio
    async def test_paste_creates_link(self) -> None:
        """Paste with provenance creates bidirectional link."""
        outline = create_outline("Target")
        ops = OutlineOperations(outline)

        clipboard = Clipboard(
            visible_text="Pasted content",
            source_path="world.source",
            source_range=Range(0, 0, 0, 10),
        )

        snippet = await ops.paste(clipboard, Location("root"))

        assert snippet is not None
        assert "world.source" in snippet.links  # Link back to source

    @pytest.mark.asyncio
    async def test_link_bidirectional(self) -> None:
        """Link operation creates bidirectional edges."""
        outline = create_outline("Root")

        # Add two child nodes
        child1 = OutlineNode(snippet=create_snippet("Source"))
        child2 = OutlineNode(snippet=create_snippet("Target"))
        outline.root.add_child(child1)
        outline.root.add_child(child2)

        ops = OutlineOperations(outline)

        # Create link from source to target
        result = await ops.link("root.0", "root.1")

        # Law 11.4: link(A, B) ⟹ ∃ reverse_link(B, A)
        assert result is True
        assert "root.1" in child1.snippet.links  # Forward link
        assert "root.0" in child2.snippet.links  # Reverse link

    @pytest.mark.asyncio
    async def test_navigate_records_trail(self) -> None:
        """Navigate records in trail."""
        outline = create_outline("Root")
        child = OutlineNode(snippet=create_snippet("Child"))
        outline.root.add_child(child)

        ops = OutlineOperations(outline)

        result = await ops.navigate("root.0")

        assert result is True
        assert len(outline.trail_steps) == 1
        assert outline.trail_steps[0]["action"] == "navigate"


# === Law Verification Tests ===


class TestOutlineLaws:
    """Verify the laws from spec §11."""

    @pytest.mark.asyncio
    async def test_law_11_1_expand_idempotent(self) -> None:
        """Law 11.1: expand(collapse(portal)) ≡ expand(portal)"""
        outline = create_outline("Root")
        portal = PortalToken(
            source_path="world.foo",
            edge_type="tests",
            destinations=["world.test"],
        )
        outline.root.add_child(OutlineNode(portal=portal))

        ops = OutlineOperations(outline)

        # expand(portal)
        await ops.expand("root.0")
        state1 = outline.root.children[0].portal.expanded

        # collapse then expand
        await ops.collapse("root.0")
        await ops.expand("root.0")
        state2 = outline.root.children[0].portal.expanded

        assert state1 == state2 == True

    @pytest.mark.asyncio
    async def test_law_11_2_trail_monotonicity(self) -> None:
        """Law 11.2: |trail(t₁)| ≤ |trail(t₂)| for t₁ < t₂"""
        outline = create_outline("Root")
        portal = PortalToken(
            source_path="world.foo",
            edge_type="tests",
            destinations=["world.test"],
        )
        outline.root.add_child(OutlineNode(portal=portal))

        ops = OutlineOperations(outline)

        lengths = []
        lengths.append(len(outline.trail_steps))

        await ops.expand("root.0")
        lengths.append(len(outline.trail_steps))

        await ops.collapse("root.0")
        lengths.append(len(outline.trail_steps))

        await ops.expand("root.0")
        lengths.append(len(outline.trail_steps))

        # Trail only grows
        assert lengths == [0, 1, 2, 3]
        assert all(lengths[i] <= lengths[i + 1] for i in range(len(lengths) - 1))

    @pytest.mark.asyncio
    async def test_law_11_3_copy_preserves_provenance(self) -> None:
        """Law 11.3: paste(copy(snippet)).source ≡ snippet.path"""
        outline = create_outline("Source content")
        # Add a target node for paste
        target = OutlineNode(snippet=create_snippet("Target"))
        outline.root.add_child(target)

        ops = OutlineOperations(outline, "kent")

        # Copy from source
        clipboard = await ops.copy("root", Range(0, 0, 0, 14))

        # Paste creates snippet with provenance (use valid target path)
        snippet = await ops.paste(clipboard, Location("root.0"))

        assert snippet is not None
        assert snippet.source_path == "root"

    @pytest.mark.asyncio
    async def test_law_11_4_link_bidirectionality(self) -> None:
        """Law 11.4: link(A, B) ⟹ ∃ reverse_link(B, A)"""
        outline = create_outline("Root")
        outline.root.add_child(OutlineNode(snippet=create_snippet("A")))
        outline.root.add_child(OutlineNode(snippet=create_snippet("B")))

        ops = OutlineOperations(outline)

        await ops.link("root.0", "root.1")

        # Forward link exists
        assert "root.1" in outline.root.children[0].snippet.links

        # Reverse link exists
        assert "root.0" in outline.root.children[1].snippet.links


# === AnnotationSnippet Tests (Phase 4C) ===


class TestAnnotationSnippet:
    """Tests for AnnotationSnippet (Phase 4C: Agent Collaboration Layer)."""

    def test_creates_annotation_with_defaults(self) -> None:
        """Create an annotation with default type."""
        annotation = AnnotationSnippet(
            visible_text="This looks like a good pattern",
            agent_id="k-gent",
            agent_name="K-gent",
        )

        assert annotation.visible_text == "This looks like a good pattern"
        assert annotation.agent_id == "k-gent"
        assert annotation.agent_name == "K-gent"
        assert annotation.annotation_type == AnnotationType.NOTE
        assert annotation.snippet_type == SnippetType.ANNOTATION

    def test_creates_suggestion_annotation(self) -> None:
        """Create a suggestion annotation."""
        annotation = AnnotationSnippet(
            visible_text="Consider using a dataclass here",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.SUGGESTION,
        )

        assert annotation.annotation_type == AnnotationType.SUGGESTION
        assert annotation.emoji == "💡"

    def test_creates_question_annotation(self) -> None:
        """Create a question annotation."""
        annotation = AnnotationSnippet(
            visible_text="Why is this function async?",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.QUESTION,
        )

        assert annotation.annotation_type == AnnotationType.QUESTION
        assert annotation.emoji == "❓"

    def test_creates_warning_annotation(self) -> None:
        """Create a warning annotation."""
        annotation = AnnotationSnippet(
            visible_text="This may cause a race condition",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.WARNING,
        )

        assert annotation.annotation_type == AnnotationType.WARNING
        assert annotation.emoji == "⚠️"

    def test_creates_evidence_annotation(self) -> None:
        """Create an evidence annotation."""
        annotation = AnnotationSnippet(
            visible_text="This pattern is used in 5 other modules",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.EVIDENCE,
        )

        assert annotation.annotation_type == AnnotationType.EVIDENCE
        assert annotation.emoji == "📎"

    def test_emoji_for_note(self) -> None:
        """Note annotation has 💭 emoji."""
        annotation = AnnotationSnippet(
            visible_text="Test",
            agent_id="test",
            agent_name="Test",
            annotation_type=AnnotationType.NOTE,
        )
        assert annotation.emoji == "💭"

    def test_render_format(self) -> None:
        """render() produces correct format."""
        annotation = AnnotationSnippet(
            visible_text="Good use of dependency injection",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.NOTE,
        )

        rendered = annotation.render()
        assert rendered == "💭 [K-gent] Good use of dependency injection"

    def test_to_dict_serialization(self) -> None:
        """to_dict() serializes all fields."""
        annotation = AnnotationSnippet(
            visible_text="Test annotation",
            agent_id="k-gent",
            agent_name="K-gent",
            annotation_type=AnnotationType.SUGGESTION,
            source_path="world.auth.middleware",
        )

        data = annotation.to_dict()

        assert data["id"] is not None
        assert data["agent_id"] == "k-gent"
        assert data["agent_name"] == "K-gent"
        assert data["annotation_type"] == "suggestion"
        assert data["visible_text"] == "Test annotation"
        assert data["source_path"] == "world.auth.middleware"
        assert data["emoji"] == "💡"
        assert "rendered" in data

    def test_dismissed_flag(self) -> None:
        """Annotation can be dismissed."""
        annotation = AnnotationSnippet(
            visible_text="Test",
            agent_id="test",
            agent_name="Test",
        )

        assert annotation.dismissed is False
        annotation.dismissed = True
        assert annotation.dismissed is True

    def test_converted_to_action_flag(self) -> None:
        """Annotation can be converted to action."""
        annotation = AnnotationSnippet(
            visible_text="Test",
            agent_id="test",
            agent_name="Test",
        )

        assert annotation.converted_to_action is False
        annotation.converted_to_action = True
        assert annotation.converted_to_action is True

    def test_inherits_from_text_snippet(self) -> None:
        """AnnotationSnippet inherits TextSnippet capabilities."""
        annotation = AnnotationSnippet(
            visible_text="Test annotation",
            agent_id="k-gent",
            agent_name="K-gent",
            source_path="world.foo",
        )

        # Should have TextSnippet methods
        assert hasattr(annotation, "with_provenance")
        assert hasattr(annotation, "add_link")
        assert annotation.source_path == "world.foo"
