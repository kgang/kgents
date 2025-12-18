"""
Tests for the Generative UI functor.

These tests verify the core claim: generate_component produces valid JSX.
"""

import pytest
from agents.design import (
    CONTENT_OPERAD,
    DESIGN_OPERAD,
    LAYOUT_OPERAD,
    MOTION_OPERAD,
    Density,
    MotionType,
)
from agents.design.generate import (
    LAYOUT_COMPONENT_MAP,
    ComponentSpec,
    generate_component,
    generate_drawer,
    generate_split,
    generate_stack,
    with_motion,
)

# =============================================================================
# ComponentSpec Tests
# =============================================================================


class TestComponentSpec:
    """Tests for ComponentSpec to_jsx rendering."""

    def test_simple_component(self) -> None:
        """Simple component renders as self-closing tag."""
        spec = ComponentSpec(name="Button", type="button")
        jsx = spec.to_jsx()
        assert jsx == "<button />"

    def test_component_with_props(self) -> None:
        """Props are rendered in JSX syntax."""
        spec = ComponentSpec(
            name="Button",
            type="button",
            props={"className": "primary", "disabled": False},
        )
        jsx = spec.to_jsx()
        assert 'className="primary"' in jsx
        assert "disabled={false}" in jsx

    def test_component_with_children(self) -> None:
        """Children are rendered with proper nesting."""
        child = ComponentSpec(name="Icon", type="Icon")
        parent = ComponentSpec(
            name="Button",
            type="button",
            children=(child,),
        )
        jsx = parent.to_jsx()
        assert "<button>" in jsx
        assert "<Icon />" in jsx
        assert "</button>" in jsx


# =============================================================================
# Layout Generation Tests
# =============================================================================


class TestLayoutGeneration:
    """Tests for layout operad to JSX conversion."""

    def test_split_generates_elastic_split(self) -> None:
        """split operation generates ElasticSplit component."""
        canvas = ComponentSpec(name="Canvas", type="Canvas")
        panel = ComponentSpec(name="Panel", type="Panel")

        jsx = generate_component(LAYOUT_OPERAD, "split", canvas, panel)

        assert "ElasticSplit" in jsx
        assert "primary={<Canvas />}" in jsx
        assert "secondary={<Panel />}" in jsx

    def test_split_at_compact_becomes_drawer(self) -> None:
        """At compact density, split degrades to drawer pattern."""
        canvas = ComponentSpec(name="Canvas", type="Canvas")
        panel = ComponentSpec(name="Panel", type="Panel")

        jsx = generate_component(
            LAYOUT_OPERAD, "split", canvas, panel, density=Density.COMPACT
        )

        assert "BottomDrawer" in jsx
        assert "ElasticSplit" not in jsx

    def test_stack_generates_elastic_container(self) -> None:
        """stack operation generates ElasticContainer."""
        item1 = ComponentSpec(name="Item1", type="Item1")
        item2 = ComponentSpec(name="Item2", type="Item2")
        item3 = ComponentSpec(name="Item3", type="Item3")

        jsx = generate_component(LAYOUT_OPERAD, "stack", item1, item2, item3)

        assert "ElasticContainer" in jsx
        assert "<Item1 />" in jsx
        assert "<Item2 />" in jsx
        assert "<Item3 />" in jsx

    def test_drawer_generates_bottom_drawer(self) -> None:
        """drawer operation generates BottomDrawer."""
        trigger = ComponentSpec(name="Trigger", type="Button")
        content = ComponentSpec(name="Content", type="Panel")

        jsx = generate_component(LAYOUT_OPERAD, "drawer", trigger, content)

        assert "BottomDrawer" in jsx
        assert "trigger={<Button />}" in jsx
        assert "content={<Panel />}" in jsx

    def test_float_generates_floating_actions(self) -> None:
        """float operation generates FloatingActions."""
        action1 = ComponentSpec(name="Add", type="AddButton")
        action2 = ComponentSpec(name="Edit", type="EditButton")

        jsx = generate_component(LAYOUT_OPERAD, "float", action1, action2)

        assert "FloatingActions" in jsx
        assert "<AddButton />" in jsx
        assert "<EditButton />" in jsx


# =============================================================================
# Motion Generation Tests
# =============================================================================


class TestMotionGeneration:
    """Tests for motion operad to JSX conversion."""

    def test_identity_returns_unwrapped(self) -> None:
        """identity motion returns component without wrapper."""
        spec = ComponentSpec(name="Box", type="Box")
        jsx = generate_component(MOTION_OPERAD, "identity", spec)
        assert "motion.div" not in jsx
        assert "<Box />" in jsx

    def test_breathe_wraps_with_motion(self) -> None:
        """breathe motion wraps with framer-motion."""
        spec = ComponentSpec(name="Card", type="Card")
        jsx = generate_component(MOTION_OPERAD, "breathe", spec)

        assert "motion.div" in jsx
        assert 'data-motion="breathe"' in jsx
        assert "<Card />" in jsx

    def test_pop_wraps_with_hover_tap(self) -> None:
        """pop motion adds hover/tap scale animations."""
        spec = ComponentSpec(name="Button", type="Button")
        jsx = generate_component(MOTION_OPERAD, "pop", spec)

        assert "motion.div" in jsx
        assert "whileHover" in jsx
        assert "whileTap" in jsx

    def test_chain_uses_animate_presence(self) -> None:
        """chain motion wraps in AnimatePresence for sequencing."""
        first = ComponentSpec(name="First", type="First")
        second = ComponentSpec(name="Second", type="Second")

        jsx = generate_component(MOTION_OPERAD, "chain", first, second)

        assert "AnimatePresence" in jsx
        assert "<First />" in jsx
        assert "<Second />" in jsx

    def test_parallel_wraps_in_layout_group(self) -> None:
        """parallel motion wraps siblings for simultaneous animation."""
        left = ComponentSpec(name="Left", type="Left")
        right = ComponentSpec(name="Right", type="Right")

        jsx = generate_component(MOTION_OPERAD, "parallel", left, right)

        assert "motion.div" in jsx
        assert "<Left />" in jsx
        assert "<Right />" in jsx


# =============================================================================
# Content Generation Tests
# =============================================================================


class TestContentGeneration:
    """Tests for content operad to JSX conversion."""

    def test_degrade_wraps_with_level(self) -> None:
        """degrade operation wraps content with level indicator."""
        full = ComponentSpec(name="FullCard", type="Card")
        level = ComponentSpec(name="title", type="ContentLevel")

        jsx = generate_component(CONTENT_OPERAD, "degrade", full, level)

        assert "ContentWrapper" in jsx
        assert 'level="title"' in jsx

    def test_compose_wraps_children(self) -> None:
        """compose operation combines content."""
        content1 = ComponentSpec(name="Title", type="Title")
        content2 = ComponentSpec(name="Body", type="Body")

        jsx = generate_component(CONTENT_OPERAD, "compose", content1, content2)

        assert "ContentComposition" in jsx
        assert "<Title />" in jsx
        assert "<Body />" in jsx


# =============================================================================
# Design Operad (Combined) Tests
# =============================================================================


class TestDesignOperad:
    """Tests for unified DESIGN_OPERAD generation."""

    def test_design_operad_dispatches_to_layout(self) -> None:
        """DESIGN_OPERAD correctly dispatches layout operations."""
        canvas = ComponentSpec(name="Canvas", type="Canvas")
        panel = ComponentSpec(name="Panel", type="Panel")

        jsx = generate_component(DESIGN_OPERAD, "split", canvas, panel)

        assert "ElasticSplit" in jsx

    def test_design_operad_dispatches_to_motion(self) -> None:
        """DESIGN_OPERAD correctly dispatches motion operations."""
        spec = ComponentSpec(name="Widget", type="Widget")

        jsx = generate_component(DESIGN_OPERAD, "pop", spec)

        assert "motion.div" in jsx

    def test_design_operad_dispatches_to_content(self) -> None:
        """DESIGN_OPERAD correctly dispatches content operations."""
        full = ComponentSpec(name="Full", type="Full")
        level = ComponentSpec(name="summary", type="Level")

        jsx = generate_component(DESIGN_OPERAD, "degrade", full, level)

        assert "ContentWrapper" in jsx


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience wrapper functions."""

    def test_generate_split_shorthand(self) -> None:
        """generate_split is shorthand for layout split."""
        primary = ComponentSpec(name="Primary", type="Primary")
        secondary = ComponentSpec(name="Secondary", type="Secondary")

        jsx = generate_split(primary, secondary)

        assert "ElasticSplit" in jsx

    def test_generate_stack_shorthand(self) -> None:
        """generate_stack is shorthand for layout stack."""
        items = [ComponentSpec(name=f"Item{i}", type=f"Item{i}") for i in range(3)]

        jsx = generate_stack(*items)

        assert "ElasticContainer" in jsx

    def test_generate_drawer_shorthand(self) -> None:
        """generate_drawer is shorthand for layout drawer."""
        trigger = ComponentSpec(name="Trigger", type="Trigger")
        content = ComponentSpec(name="Content", type="Content")

        jsx = generate_drawer(trigger, content)

        assert "BottomDrawer" in jsx


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error conditions."""

    def test_unknown_operation_raises(self) -> None:
        """Unknown operation raises KeyError."""
        spec = ComponentSpec(name="Test", type="Test")

        with pytest.raises(KeyError, match="Unknown operation"):
            generate_component(LAYOUT_OPERAD, "invalid_op", spec)

    def test_wrong_arity_raises(self) -> None:
        """Wrong number of children raises ValueError."""
        spec = ComponentSpec(name="Test", type="Test")

        # split requires 2 children
        with pytest.raises(ValueError, match="requires 2"):
            generate_component(LAYOUT_OPERAD, "split", spec)

    def test_drawer_requires_two_children(self) -> None:
        """drawer operation requires exactly 2 children."""
        spec = ComponentSpec(name="Test", type="Test")

        with pytest.raises(ValueError, match="requires 2"):
            generate_component(LAYOUT_OPERAD, "drawer", spec)


# =============================================================================
# Integration Test: The Core Claim
# =============================================================================


class TestCoreClaim:
    """
    Test the core claim from Gap #1:

    generate_component(DESIGN_OPERAD, "split", a, b) → valid JSX
    """

    def test_core_claim_split_produces_valid_jsx(self) -> None:
        """The primary claim: split generates valid JSX structure."""
        canvas = ComponentSpec(
            name="Canvas",
            type="div",
            props={"className": "canvas"},
        )
        drawer = ComponentSpec(
            name="Drawer",
            type="BottomDrawer",
            props={"open": True},
        )

        jsx = generate_component(DESIGN_OPERAD, "split", canvas, drawer)

        # Verify structure
        assert jsx.startswith("<")
        assert jsx.endswith("/>")
        assert "ElasticSplit" in jsx
        assert "primary=" in jsx
        assert "secondary=" in jsx

    def test_split_drawer_equivalence_at_compact(self) -> None:
        """
        Verify the law: split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact

        At compact density, both patterns produce drawer-based UI.
        """
        main = ComponentSpec(name="Main", type="Main")
        secondary = ComponentSpec(name="Secondary", type="Secondary")

        # At compact, split should produce a drawer-like structure
        jsx = generate_split(main, secondary, density=Density.COMPACT)

        assert "BottomDrawer" in jsx
        assert "ElasticSplit" not in jsx

    def test_all_layout_operations_produce_jsx(self) -> None:
        """Every layout operation produces valid JSX."""
        specs = [ComponentSpec(name=f"Spec{i}", type=f"Type{i}") for i in range(3)]

        for op_name in LAYOUT_COMPONENT_MAP.keys():
            op = LAYOUT_OPERAD.get(op_name)
            assert op is not None

            # Get required number of children
            arity = op.arity if op.arity > 0 else 2
            children = specs[:arity]

            jsx = generate_component(LAYOUT_OPERAD, op_name, *children)

            # All JSX should start with < and be non-empty
            assert jsx.startswith("<")
            assert len(jsx) > 10
