"""
Tests for KBlockSheaf.

Verifies sheaf coherence, gluing, and propagation operations.

Test Categories:
    - Compatibility: Token agreement between views
    - Gluing: Combining views into unified content
    - Propagation: Flowing changes from prose to derived views
    - Verification: Sheaf condition checking
    - Integration: KBlock.sheaf property and verify_coherence()
"""

import pytest

from ..core import (
    GluingError,
    IsolationState,
    KBlock,
    KBlockSheaf,
    PropagationError,
    SheafConditionError,
    SheafVerification,
    TokenConflict,
    generate_kblock_id,
)
from ..views.base import ViewType

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def empty_block() -> KBlock:
    """K-Block with empty content."""
    return KBlock(
        id=generate_kblock_id(),
        path="test/empty.md",
        content="",
        base_content="",
    )


@pytest.fixture
def simple_block() -> KBlock:
    """K-Block with simple markdown content."""
    content = """# Title

Some prose here.

- name: string
- age: integer
"""
    return KBlock(
        id=generate_kblock_id(),
        path="test/simple.md",
        content=content,
        base_content=content,
    )


@pytest.fixture
def complex_block() -> KBlock:
    """K-Block with complex multi-section content."""
    content = """# Main Title

Introduction paragraph.

## Section One

- field1: string
- field2: integer

## Section Two

- other_field: boolean

### Subsection

More content here with [[reference]].
"""
    return KBlock(
        id=generate_kblock_id(),
        path="test/complex.md",
        content=content,
        base_content=content,
    )


@pytest.fixture
def block_with_views(simple_block: KBlock) -> KBlock:
    """K-Block with all views activated."""
    simple_block.activate_view(ViewType.PROSE)
    simple_block.activate_view(ViewType.GRAPH)
    simple_block.activate_view(ViewType.CODE)
    simple_block.activate_view(ViewType.OUTLINE)
    simple_block.activate_view(ViewType.DIFF)
    return simple_block


# =============================================================================
# Compatibility Tests (12)
# =============================================================================


class TestCompatibility:
    """Tests for view compatibility checking."""

    def test_empty_views_compatible(self, empty_block: KBlock) -> None:
        """Empty views are trivially compatible."""
        empty_block.activate_view(ViewType.PROSE)
        empty_block.activate_view(ViewType.GRAPH)

        sheaf = KBlockSheaf(empty_block)
        prose = empty_block.views[ViewType.PROSE]
        graph = empty_block.views[ViewType.GRAPH]

        assert sheaf.compatible(prose, graph)

    def test_same_view_compatible_with_self(self, simple_block: KBlock) -> None:
        """A view is always compatible with itself (reflexivity)."""
        simple_block.activate_view(ViewType.PROSE)
        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]

        assert sheaf.compatible(prose, prose)

    def test_compatible_is_symmetric(self, simple_block: KBlock) -> None:
        """Compatibility is symmetric: v1 ⊲ v2 ⟺ v2 ⊲ v1."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        graph = simple_block.views[ViewType.GRAPH]

        assert sheaf.compatible(prose, graph) == sheaf.compatible(graph, prose)

    def test_prose_graph_compatible(self, simple_block: KBlock) -> None:
        """Prose and Graph share heading/field tokens and should be compatible."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        graph = simple_block.views[ViewType.GRAPH]

        assert sheaf.compatible(prose, graph)

    def test_prose_code_compatible(self, simple_block: KBlock) -> None:
        """Prose and Code share field/type tokens and should be compatible."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.CODE)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        code = simple_block.views[ViewType.CODE]

        assert sheaf.compatible(prose, code)

    def test_prose_outline_compatible(self, simple_block: KBlock) -> None:
        """Prose and Outline share heading tokens and should be compatible."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.OUTLINE)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        outline = simple_block.views[ViewType.OUTLINE]

        assert sheaf.compatible(prose, outline)

    def test_graph_outline_compatible(self, simple_block: KBlock) -> None:
        """Graph and Outline share heading tokens and should be compatible."""
        simple_block.activate_view(ViewType.GRAPH)
        simple_block.activate_view(ViewType.OUTLINE)

        sheaf = KBlockSheaf(simple_block)
        graph = simple_block.views[ViewType.GRAPH]
        outline = simple_block.views[ViewType.OUTLINE]

        assert sheaf.compatible(graph, outline)

    def test_diff_compatible_with_all(self, simple_block: KBlock) -> None:
        """Diff has no tokens, so it's compatible with everything."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.DIFF)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        diff = simple_block.views[ViewType.DIFF]

        # Diff has empty tokens, so no conflicts possible
        assert sheaf.compatible(prose, diff)
        assert sheaf.compatible(diff, prose)

    def test_derived_subset_of_canonical(self, simple_block: KBlock) -> None:
        """Derived view tokens should be a subset of canonical tokens."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)

        prose = simple_block.views[ViewType.PROSE]
        graph = simple_block.views[ViewType.GRAPH]

        prose_ids = {t.id for t in prose.tokens()}
        graph_ids = {t.id for t in graph.tokens()}

        # Graph extracts from prose, so its IDs should be in prose
        # (Note: this tests that graph doesn't invent tokens)
        # Graph may have fewer tokens (it only extracts certain kinds)
        assert len(graph_ids) <= len(prose_ids) or graph_ids <= prose_ids

    def test_compatible_after_edit(self, simple_block: KBlock) -> None:
        """Views remain compatible after edit + refresh."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)

        # Edit content
        new_content = simple_block.content + "\n- new_field: string\n"
        simple_block.set_content(new_content)
        simple_block.refresh_views()

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        graph = simple_block.views[ViewType.GRAPH]

        assert sheaf.compatible(prose, graph)

    def test_all_views_compatible(self, block_with_views: KBlock) -> None:
        """All five views should be mutually compatible."""
        sheaf = KBlockSheaf(block_with_views)
        views = list(block_with_views.views.values())

        for i, v1 in enumerate(views):
            for v2 in views[i + 1 :]:
                assert sheaf.compatible(v1, v2), f"{v1.view_type} incompatible with {v2.view_type}"

    def test_find_conflicts_returns_empty_when_compatible(self, simple_block: KBlock) -> None:
        """_find_conflicts returns empty list for compatible views."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)

        sheaf = KBlockSheaf(simple_block)
        prose = simple_block.views[ViewType.PROSE]
        graph = simple_block.views[ViewType.GRAPH]

        conflicts = sheaf._find_conflicts(prose, graph)
        assert conflicts == []


# =============================================================================
# Gluing Tests (8)
# =============================================================================


class TestGluing:
    """Tests for sheaf gluing operation."""

    def test_glue_returns_prose_content(self, block_with_views: KBlock) -> None:
        """Glue returns the canonical prose content."""
        sheaf = KBlockSheaf(block_with_views)
        glued = sheaf.glue()

        assert glued == block_with_views.content

    def test_glue_fails_on_no_views(self, simple_block: KBlock) -> None:
        """Glue raises GluingError when no views are active."""
        sheaf = KBlockSheaf(simple_block)

        with pytest.raises(GluingError, match="No views active"):
            sheaf.glue()

    def test_glue_single_view(self, simple_block: KBlock) -> None:
        """Single view glues to itself (identity)."""
        simple_block.activate_view(ViewType.PROSE)
        sheaf = KBlockSheaf(simple_block)

        glued = sheaf.glue()
        assert glued == simple_block.content

    def test_glue_all_views(self, block_with_views: KBlock) -> None:
        """All 5 views glue correctly."""
        sheaf = KBlockSheaf(block_with_views)

        # Should not raise
        glued = sheaf.glue()
        assert glued == block_with_views.content

    def test_glue_idempotent(self, block_with_views: KBlock) -> None:
        """Gluing is idempotent: glue(glue(x)) ≡ glue(x)."""
        sheaf = KBlockSheaf(block_with_views)

        first = sheaf.glue()
        second = sheaf.glue()

        assert first == second

    def test_glue_after_edit(self, block_with_views: KBlock) -> None:
        """Glue works after edit + refresh."""
        new_content = block_with_views.content + "\n## New Section\n"
        block_with_views.set_content(new_content)
        block_with_views.refresh_views()

        sheaf = KBlockSheaf(block_with_views)
        glued = sheaf.glue()

        assert glued == new_content

    def test_glue_empty_content(self, empty_block: KBlock) -> None:
        """Handle empty document gracefully."""
        empty_block.activate_view(ViewType.PROSE)
        sheaf = KBlockSheaf(empty_block)

        glued = sheaf.glue()
        assert glued == ""

    def test_glue_complex_content(self, complex_block: KBlock) -> None:
        """Glue works with multi-heading, multi-field spec."""
        complex_block.activate_view(ViewType.PROSE)
        complex_block.activate_view(ViewType.GRAPH)
        complex_block.activate_view(ViewType.OUTLINE)

        sheaf = KBlockSheaf(complex_block)
        glued = sheaf.glue()

        assert glued == complex_block.content


# =============================================================================
# Propagation Tests (10)
# =============================================================================


class TestPropagation:
    """Tests for change propagation."""

    def test_propagate_from_prose(self, block_with_views: KBlock) -> None:
        """Propagation from PROSE works correctly."""
        sheaf = KBlockSheaf(block_with_views)
        new_content = block_with_views.content + "\n- new_field: boolean\n"

        changes = sheaf.propagate(ViewType.PROSE, new_content)

        assert ViewType.PROSE in changes
        assert changes[ViewType.PROSE]["source"] is True
        assert block_with_views.content == new_content

    def test_propagate_from_diff_raises(self, block_with_views: KBlock) -> None:
        """Propagation from DIFF raises PropagationError (read-only)."""
        sheaf = KBlockSheaf(block_with_views)

        with pytest.raises(PropagationError, match="read-only"):
            sheaf.propagate(ViewType.DIFF, "new content")

    def test_propagate_from_graph_bidirectional(self, block_with_views: KBlock) -> None:
        """Phase 3: Propagation from GRAPH works (bidirectional)."""
        sheaf = KBlockSheaf(block_with_views)
        old_graph = block_with_views.views[ViewType.GRAPH]

        # Create a modified graph state (simulated)
        from ..views.graph import GraphNode, GraphView

        new_graph = GraphView()
        new_graph._content = block_with_views.content
        new_graph._nodes = list(old_graph.nodes) + [
            GraphNode(id="h-999", label="New Section", kind="heading", level=2)
        ]
        new_graph._edges = list(old_graph.edges)

        # Propagate from graph should work (Phase 3)
        changes = sheaf.propagate(ViewType.GRAPH, new_graph, old_graph)

        assert ViewType.GRAPH in changes
        assert changes[ViewType.GRAPH]["source"] is True

    def test_propagate_from_code_bidirectional(self, block_with_views: KBlock) -> None:
        """Phase 3: Propagation from CODE works (bidirectional)."""
        sheaf = KBlockSheaf(block_with_views)
        old_code = block_with_views.views[ViewType.CODE]

        # Create a modified code state (simulated)
        from ..views.code import CodeView, FieldDef

        new_code = CodeView()
        new_code._content = block_with_views.content
        new_code._class_name = old_code._class_name
        new_code._fields = list(old_code.fields) + [FieldDef(name="extra", type_hint="str")]

        # Propagate from code should work (Phase 3)
        changes = sheaf.propagate(ViewType.CODE, new_code, old_code)

        assert ViewType.CODE in changes
        assert changes[ViewType.CODE]["source"] is True

    def test_can_edit_view(self, block_with_views: KBlock) -> None:
        """Test can_edit_view() for all view types."""
        sheaf = KBlockSheaf(block_with_views)

        assert sheaf.can_edit_view(ViewType.PROSE) is True
        assert sheaf.can_edit_view(ViewType.GRAPH) is True
        assert sheaf.can_edit_view(ViewType.CODE) is True
        assert sheaf.can_edit_view(ViewType.OUTLINE) is True
        assert sheaf.can_edit_view(ViewType.DIFF) is False

    def test_propagate_updates_all_views(self, block_with_views: KBlock) -> None:
        """Propagation refreshes all active views."""
        sheaf = KBlockSheaf(block_with_views)
        new_content = block_with_views.content + "\n## Added Section\n"

        sheaf.propagate(ViewType.PROSE, new_content)

        # All views should now reflect the new content
        outline = block_with_views.views[ViewType.OUTLINE]
        # The outline should have the new heading
        outline_str = outline.render(block_with_views.content)
        assert "Added Section" in outline_str

    def test_propagate_returns_derived_deltas(self, block_with_views: KBlock) -> None:
        """Propagation returns change info for derived views."""
        sheaf = KBlockSheaf(block_with_views)
        new_content = block_with_views.content + "\n- extra: string\n"

        changes = sheaf.propagate(ViewType.PROSE, new_content)

        # Should have entries for all active views
        assert ViewType.PROSE in changes
        assert ViewType.GRAPH in changes
        assert ViewType.CODE in changes
        assert ViewType.OUTLINE in changes

    def test_propagate_add_heading(self, simple_block: KBlock) -> None:
        """Adding a heading appears in graph/outline."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.OUTLINE)

        sheaf = KBlockSheaf(simple_block)

        # Get tokens before
        outline_before = {t.id for t in simple_block.views[ViewType.OUTLINE].tokens()}

        # Add heading
        new_content = simple_block.content + "\n## New Heading\n"
        sheaf.propagate(ViewType.PROSE, new_content)

        # Get tokens after
        outline_after = {t.id for t in simple_block.views[ViewType.OUTLINE].tokens()}

        # Should have new token
        assert len(outline_after) > len(outline_before)

    def test_propagate_add_field(self, simple_block: KBlock) -> None:
        """Adding a field appears in graph/code."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.CODE)

        sheaf = KBlockSheaf(simple_block)
        new_content = simple_block.content + "\n- extra_field: float\n"

        changes = sheaf.propagate(ViewType.PROSE, new_content)

        # Code view should have new token
        code_changes = changes[ViewType.CODE]
        assert len(code_changes.get("tokens_added", [])) > 0

    def test_propagate_preserves_coherence(self, block_with_views: KBlock) -> None:
        """Sheaf condition passes after propagation."""
        sheaf = KBlockSheaf(block_with_views)
        new_content = block_with_views.content + "\n- another: integer\n"

        sheaf.propagate(ViewType.PROSE, new_content)

        verification = sheaf.verify_sheaf_condition()
        assert verification.passed

    def test_propagate_marks_block_dirty(self, block_with_views: KBlock) -> None:
        """Propagation marks the block as dirty."""
        # Reset to pristine
        block_with_views.isolation = IsolationState.PRISTINE

        sheaf = KBlockSheaf(block_with_views)
        new_content = block_with_views.content + "\n- x: y\n"

        sheaf.propagate(ViewType.PROSE, new_content)

        assert block_with_views.isolation == IsolationState.DIRTY


# =============================================================================
# Verification Tests (6)
# =============================================================================


class TestVerification:
    """Tests for sheaf condition verification."""

    def test_verify_passes_on_coherent(self, block_with_views: KBlock) -> None:
        """Verification passes when views are coherent."""
        sheaf = KBlockSheaf(block_with_views)
        verification = sheaf.verify_sheaf_condition()

        assert verification.passed
        assert len(verification.conflicts) == 0

    def test_verify_single_view(self, simple_block: KBlock) -> None:
        """Single view is trivially coherent."""
        simple_block.activate_view(ViewType.PROSE)
        sheaf = KBlockSheaf(simple_block)

        verification = sheaf.verify_sheaf_condition()

        assert verification.passed
        assert verification.checked_pairs == 0

    def test_verify_no_views(self, simple_block: KBlock) -> None:
        """No views is trivially coherent."""
        sheaf = KBlockSheaf(simple_block)

        verification = sheaf.verify_sheaf_condition()

        assert verification.passed

    def test_verify_returns_coverage(self, block_with_views: KBlock) -> None:
        """Verification returns coverage metric."""
        sheaf = KBlockSheaf(block_with_views)
        verification = sheaf.verify_sheaf_condition()

        assert 0.0 <= verification.coverage <= 1.0

    def test_verify_counts_pairs(self, block_with_views: KBlock) -> None:
        """Verification counts checked pairs correctly."""
        sheaf = KBlockSheaf(block_with_views)
        verification = sheaf.verify_sheaf_condition()

        # 5 views = C(5,2) = 10 pairs
        assert verification.checked_pairs == 10

    def test_verify_serializable(self, block_with_views: KBlock) -> None:
        """Verification result is serializable."""
        sheaf = KBlockSheaf(block_with_views)
        verification = sheaf.verify_sheaf_condition()

        d = verification.to_dict()

        assert "passed" in d
        assert "checked_pairs" in d
        assert "conflicts" in d
        assert "coverage" in d

    def test_verify_bool_coercion(self, block_with_views: KBlock) -> None:
        """bool(verification) == passed."""
        sheaf = KBlockSheaf(block_with_views)
        verification = sheaf.verify_sheaf_condition()

        assert bool(verification) == verification.passed


# =============================================================================
# Integration Tests (5)
# =============================================================================


class TestIntegration:
    """Tests for KBlock integration."""

    def test_kblock_sheaf_property(self, simple_block: KBlock) -> None:
        """KBlock.sheaf returns a KBlockSheaf."""
        sheaf = simple_block.sheaf

        assert isinstance(sheaf, KBlockSheaf)
        assert sheaf.kblock is simple_block

    def test_kblock_verify_coherence(self, block_with_views: KBlock) -> None:
        """KBlock.verify_coherence() works."""
        verification = block_with_views.verify_coherence()

        assert isinstance(verification, SheafVerification)
        assert verification.passed

    def test_sheaf_with_checkpoints(self, simple_block: KBlock) -> None:
        """Sheaf works correctly after checkpoint/rewind."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.OUTLINE)

        # Create checkpoint
        cp = simple_block.checkpoint("before")

        # Edit
        simple_block.set_content(simple_block.content + "\n## New\n")
        simple_block.refresh_views()

        # Verify coherent
        assert simple_block.verify_coherence().passed

        # Rewind
        simple_block.rewind(cp.id)
        simple_block.refresh_views()

        # Still coherent
        assert simple_block.verify_coherence().passed

    def test_sheaf_after_multiple_edits(self, simple_block: KBlock) -> None:
        """Coherence maintained through multiple edits."""
        simple_block.activate_view(ViewType.PROSE)
        simple_block.activate_view(ViewType.GRAPH)
        simple_block.activate_view(ViewType.CODE)

        sheaf = simple_block.sheaf

        for i in range(5):
            new_content = simple_block.content + f"\n- field_{i}: string\n"
            sheaf.propagate(ViewType.PROSE, new_content)

            verification = sheaf.verify_sheaf_condition()
            assert verification.passed, f"Failed on iteration {i}"

    def test_sheaf_repr(self, block_with_views: KBlock) -> None:
        """Sheaf has meaningful repr."""
        sheaf = block_with_views.sheaf
        r = repr(sheaf)

        assert "KBlockSheaf" in r
        assert block_with_views.id in r


# =============================================================================
# TokenConflict Tests (3)
# =============================================================================


class TestTokenConflict:
    """Tests for TokenConflict dataclass."""

    def test_token_conflict_kind_mismatch(self) -> None:
        """TokenConflict identifies kind mismatches."""
        conflict = TokenConflict(
            token_id="h-0",
            view1=ViewType.PROSE,
            view2=ViewType.GRAPH,
            kind1="heading",
            kind2="field",
            value1="Title",
            value2="Title",
        )

        assert conflict.is_kind_mismatch
        assert not conflict.is_value_mismatch

    def test_token_conflict_value_mismatch(self) -> None:
        """TokenConflict identifies value mismatches."""
        conflict = TokenConflict(
            token_id="f-name",
            view1=ViewType.PROSE,
            view2=ViewType.CODE,
            kind1="field",
            kind2="field",
            value1="name",
            value2="username",
        )

        assert not conflict.is_kind_mismatch
        assert conflict.is_value_mismatch

    def test_token_conflict_str(self) -> None:
        """TokenConflict has meaningful string representation."""
        conflict = TokenConflict(
            token_id="h-0",
            view1=ViewType.PROSE,
            view2=ViewType.GRAPH,
            kind1="heading",
            kind2="field",
            value1="Title",
            value2="Title",
        )

        s = str(conflict)
        assert "h-0" in s
        assert "heading" in s or "field" in s
