"""
Tests for Design Operads: Law verification and composition.

These tests verify:
1. All operad laws pass
2. Content level lattice is well-formed
3. Density maps correctly from viewport width
4. Motion gating works (no animation when disabled)
5. Polynomial state machine transitions correctly
"""

import pytest
from agents.design import (
    # Operads
    CONTENT_OPERAD,
    DESIGN_OPERAD,
    DESIGN_POLYNOMIAL,
    LAYOUT_OPERAD,
    MOTION_OPERAD,
    # Polynomial
    AnimationToggle,
    ContainerResize,
    # Types
    ContentLevel,
    Density,
    DesignState,
    MotionRequest,
    MotionType,
    NoChange,
    StateChanged,
    ViewportResize,
    create_design_polynomial,
)
from agents.operad import LawStatus, OperadRegistry

# =============================================================================
# Operad Law Tests
# =============================================================================


class TestLayoutOperad:
    """Tests for LAYOUT_OPERAD."""

    def test_layout_operad_registered(self) -> None:
        """LAYOUT_OPERAD should be in the registry."""
        operad = OperadRegistry.get("LAYOUT")
        assert operad is not None
        assert operad.name == "LAYOUT"

    def test_layout_operad_has_operations(self) -> None:
        """LAYOUT_OPERAD should have all four operations."""
        assert "split" in LAYOUT_OPERAD.operations
        assert "stack" in LAYOUT_OPERAD.operations
        assert "drawer" in LAYOUT_OPERAD.operations
        assert "float" in LAYOUT_OPERAD.operations

    def test_split_drawer_equivalence_law(self) -> None:
        """Verify split-drawer equivalence law passes."""
        verifications = LAYOUT_OPERAD.verify_all_laws()
        assert len(verifications) == 1
        assert verifications[0].passed


class TestContentOperad:
    """Tests for CONTENT_OPERAD."""

    def test_content_operad_registered(self) -> None:
        """CONTENT_OPERAD should be in the registry."""
        operad = OperadRegistry.get("CONTENT")
        assert operad is not None
        assert operad.name == "CONTENT"

    def test_content_operad_has_operations(self) -> None:
        """CONTENT_OPERAD should have degrade and compose."""
        assert "degrade" in CONTENT_OPERAD.operations
        assert "compose" in CONTENT_OPERAD.operations

    def test_content_lattice_law(self) -> None:
        """Verify content lattice law passes."""
        verifications = CONTENT_OPERAD.verify_all_laws()
        lattice_law = next(v for v in verifications if v.law_name == "content_lattice")
        assert lattice_law.passed


class TestMotionOperad:
    """Tests for MOTION_OPERAD."""

    def test_motion_operad_registered(self) -> None:
        """MOTION_OPERAD should be in the registry."""
        operad = OperadRegistry.get("MOTION")
        assert operad is not None
        assert operad.name == "MOTION"

    def test_motion_operad_has_operations(self) -> None:
        """MOTION_OPERAD should have all motion operations."""
        expected = {
            "identity",
            "breathe",
            "pop",
            "shake",
            "shimmer",
            "chain",
            "parallel",
        }
        assert set(MOTION_OPERAD.operations.keys()) == expected

    def test_motion_identity_law(self) -> None:
        """Verify motion identity law passes."""
        verifications = MOTION_OPERAD.verify_all_laws()
        identity_law = next(v for v in verifications if v.law_name == "motion_identity")
        assert identity_law.passed

    def test_motion_should_animate_law(self) -> None:
        """Verify motion gating law passes."""
        verifications = MOTION_OPERAD.verify_all_laws()
        gating_law = next(
            v for v in verifications if v.law_name == "motion_should_animate"
        )
        assert gating_law.passed


class TestDesignOperad:
    """Tests for the unified DESIGN_OPERAD."""

    def test_design_operad_registered(self) -> None:
        """DESIGN_OPERAD should be in the registry."""
        operad = OperadRegistry.get("DESIGN")
        assert operad is not None
        assert operad.name == "DESIGN"

    def test_design_operad_combines_all(self) -> None:
        """DESIGN_OPERAD should have all operations from sub-operads."""
        layout_ops = set(LAYOUT_OPERAD.operations.keys())
        content_ops = set(CONTENT_OPERAD.operations.keys())
        motion_ops = set(MOTION_OPERAD.operations.keys())
        design_ops = set(DESIGN_OPERAD.operations.keys())

        assert layout_ops.issubset(design_ops)
        assert content_ops.issubset(design_ops)
        assert motion_ops.issubset(design_ops)

    def test_composition_natural_law(self) -> None:
        """Verify composition naturality law passes."""
        verifications = DESIGN_OPERAD.verify_all_laws()
        natural_law = next(
            v for v in verifications if v.law_name == "composition_natural"
        )
        assert natural_law.passed

    def test_all_laws_pass(self) -> None:
        """All DESIGN_OPERAD laws should pass or be structurally verified."""
        verifications = DESIGN_OPERAD.verify_all_laws()
        assert len(verifications) >= 5  # All sub-operad laws + naturality

        # Laws can be PASSED (runtime verified) or STRUCTURAL (type-level verified)
        acceptable_statuses = {LawStatus.PASSED, LawStatus.STRUCTURAL}
        for v in verifications:
            assert v.status in acceptable_statuses, (
                f"Law {v.law_name} failed: {v.message}"
            )


# =============================================================================
# Type Tests
# =============================================================================


class TestDensity:
    """Tests for Density enum and mapping."""

    def test_from_width_compact(self) -> None:
        """Width < 768 should map to compact (per spec/protocols/projection.md)."""
        assert Density.from_width(320) == Density.COMPACT
        assert Density.from_width(640) == Density.COMPACT
        assert Density.from_width(767) == Density.COMPACT

    def test_from_width_comfortable(self) -> None:
        """Width 768-1023 should map to comfortable (per spec/protocols/projection.md)."""
        assert Density.from_width(768) == Density.COMFORTABLE
        assert Density.from_width(900) == Density.COMFORTABLE
        assert Density.from_width(1023) == Density.COMFORTABLE

    def test_from_width_spacious(self) -> None:
        """Width >= 1024 should map to spacious."""
        assert Density.from_width(1024) == Density.SPACIOUS
        assert Density.from_width(1440) == Density.SPACIOUS
        assert Density.from_width(2560) == Density.SPACIOUS


class TestContentLevel:
    """Tests for ContentLevel enum and lattice."""

    def test_from_width_icon(self) -> None:
        """Width < 60 should map to icon."""
        assert ContentLevel.from_width(30) == ContentLevel.ICON
        assert ContentLevel.from_width(59) == ContentLevel.ICON

    def test_from_width_title(self) -> None:
        """Width 60-149 should map to title."""
        assert ContentLevel.from_width(60) == ContentLevel.TITLE
        assert ContentLevel.from_width(149) == ContentLevel.TITLE

    def test_from_width_summary(self) -> None:
        """Width 150-279 should map to summary."""
        assert ContentLevel.from_width(150) == ContentLevel.SUMMARY
        assert ContentLevel.from_width(279) == ContentLevel.SUMMARY

    def test_from_width_full(self) -> None:
        """Width >= 280 should map to full."""
        assert ContentLevel.from_width(280) == ContentLevel.FULL
        assert ContentLevel.from_width(400) == ContentLevel.FULL

    def test_lattice_ordering(self) -> None:
        """Content levels should form a lattice under includes()."""
        # Reflexivity
        assert ContentLevel.ICON.includes(ContentLevel.ICON)
        assert ContentLevel.FULL.includes(ContentLevel.FULL)

        # Transitivity
        assert ContentLevel.FULL.includes(ContentLevel.SUMMARY)
        assert ContentLevel.SUMMARY.includes(ContentLevel.TITLE)
        assert ContentLevel.FULL.includes(ContentLevel.TITLE)  # transitive

        # Antisymmetry
        assert not ContentLevel.ICON.includes(ContentLevel.TITLE)
        assert not ContentLevel.TITLE.includes(ContentLevel.SUMMARY)

    def test_full_includes_all(self) -> None:
        """FULL should include all other levels."""
        for level in ContentLevel:
            assert ContentLevel.FULL.includes(level)

    def test_icon_includes_only_self(self) -> None:
        """ICON should only include itself."""
        assert ContentLevel.ICON.includes(ContentLevel.ICON)
        assert not ContentLevel.ICON.includes(ContentLevel.TITLE)
        assert not ContentLevel.ICON.includes(ContentLevel.SUMMARY)
        assert not ContentLevel.ICON.includes(ContentLevel.FULL)


class TestDesignState:
    """Tests for DesignState dataclass."""

    def test_immutable(self) -> None:
        """DesignState should be immutable (frozen)."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        with pytest.raises(AttributeError):
            state.density = Density.COMPACT  # type: ignore

    def test_with_density(self) -> None:
        """with_density should return new state with updated density."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        new_state = state.with_density(Density.COMPACT)

        assert new_state.density == Density.COMPACT
        assert new_state.content_level == ContentLevel.FULL
        assert state.density == Density.SPACIOUS  # original unchanged

    def test_with_content_level(self) -> None:
        """with_content_level should return new state with updated level."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        new_state = state.with_content_level(ContentLevel.ICON)

        assert new_state.content_level == ContentLevel.ICON
        assert new_state.density == Density.SPACIOUS

    def test_with_motion(self) -> None:
        """with_motion should return new state with updated motion."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        new_state = state.with_motion(MotionType.BREATHE)

        assert new_state.motion == MotionType.BREATHE
        assert state.motion == MotionType.IDENTITY  # original unchanged


# =============================================================================
# Polynomial Tests
# =============================================================================


class TestDesignPolynomial:
    """Tests for DESIGN_POLYNOMIAL state machine."""

    def test_initial_state(self) -> None:
        """Default polynomial should start spacious with full content."""
        poly = create_design_polynomial()
        # The polynomial has positions but no "current state" - we test via invoke
        assert poly.name == "DESIGN_POLYNOMIAL"
        assert len(poly.positions) > 0

    def test_viewport_resize_changes_density(self) -> None:
        """ViewportResize should update density."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        input = ViewportResize(width=375, height=667)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert new_state.density == Density.COMPACT
        assert isinstance(output, StateChanged)
        assert output.old_state == state
        assert output.new_state == new_state

    def test_viewport_resize_no_change(self) -> None:
        """ViewportResize to same density should return NoChange."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        input = ViewportResize(width=1440, height=900)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert new_state == state
        assert isinstance(output, NoChange)

    def test_container_resize_changes_content_level(self) -> None:
        """ContainerResize should update content level."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        input = ContainerResize(width=50)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert new_state.content_level == ContentLevel.ICON
        assert isinstance(output, StateChanged)

    def test_animation_toggle_off(self) -> None:
        """AnimationToggle(False) should disable animations."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.BREATHE,
            should_animate=True,
        )
        input = AnimationToggle(enabled=False)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert not new_state.should_animate
        assert new_state.motion == MotionType.IDENTITY  # Reset to identity
        assert isinstance(output, StateChanged)

    def test_motion_request_when_enabled(self) -> None:
        """MotionRequest should change motion when animations enabled."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            should_animate=True,
        )
        input = MotionRequest(motion=MotionType.POP)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert new_state.motion == MotionType.POP
        assert isinstance(output, StateChanged)

    def test_motion_request_when_disabled(self) -> None:
        """MotionRequest should be ignored when animations disabled (law enforcement)."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.IDENTITY,
            should_animate=False,
        )
        input = MotionRequest(motion=MotionType.POP)

        new_state, output = DESIGN_POLYNOMIAL.invoke(state, input)

        assert new_state.motion == MotionType.IDENTITY  # Unchanged
        assert isinstance(output, NoChange)

    def test_directions_returns_all_input_types(self) -> None:
        """directions() should return all available input types plus Any marker."""
        from typing import Any

        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )
        directions = DESIGN_POLYNOMIAL.directions(state)

        # The directions include both types and Any marker for universal acceptance
        # mypy complains about type/instance comparison, but this is correct at runtime
        assert ViewportResize in directions  # type: ignore[comparison-overlap]
        assert ContainerResize in directions  # type: ignore[comparison-overlap]
        assert AnimationToggle in directions  # type: ignore[comparison-overlap]
        assert MotionRequest in directions  # type: ignore[comparison-overlap]
        assert Any in directions  # type: ignore[comparison-overlap]


# =============================================================================
# Integration Tests
# =============================================================================


class TestDesignModuleIntegration:
    """Integration tests for the design module."""

    def test_operad_operation_count(self) -> None:
        """DESIGN_OPERAD should have at least 13 operations (4+2+7)."""
        assert len(DESIGN_OPERAD.operations) >= 13

    def test_operad_law_count(self) -> None:
        """DESIGN_OPERAD should have at least 5 laws."""
        assert len(DESIGN_OPERAD.laws) >= 5

    def test_polynomial_position_count(self) -> None:
        """DESIGN_POLYNOMIAL should have all state combinations."""
        # 3 densities × 4 content levels × 6 motions × 2 animate flags = 144
        expected = len(Density) * len(ContentLevel) * len(MotionType) * 2
        assert len(DESIGN_POLYNOMIAL.positions) == expected

    def test_full_resize_flow(self) -> None:
        """Simulate a full resize flow: desktop → mobile → tablet."""
        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )

        # Desktop → Mobile
        state, _ = DESIGN_POLYNOMIAL.invoke(state, ViewportResize(375, 667))
        assert state.density == Density.COMPACT

        # Mobile → Tablet
        state, _ = DESIGN_POLYNOMIAL.invoke(state, ViewportResize(768, 1024))
        assert state.density == Density.COMFORTABLE

        # Container shrinks
        state, _ = DESIGN_POLYNOMIAL.invoke(state, ContainerResize(100))
        assert state.content_level == ContentLevel.TITLE

        # Container expands
        state, _ = DESIGN_POLYNOMIAL.invoke(state, ContainerResize(400))
        assert state.content_level == ContentLevel.FULL
