"""
Tests for the DesignSheaf.

These tests verify the four sheaf operations:
- overlap: When do contexts share state?
- restrict: Extract local state from global state
- compatible: Check compatibility of local states
- glue: Combine local states into global state
"""

import pytest
from agents.design import (
    ContentLevel,
    Density,
    DesignState,
    MotionType,
)
from agents.design.sheaf import (
    VIEWPORT_CONTEXT,
    DesignContext,
    DesignSheaf,
    GluingError,
    RestrictionError,
    create_container_context,
    create_design_sheaf,
    create_design_sheaf_with_hierarchy,
    create_widget_context,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def simple_sheaf() -> DesignSheaf:
    """Create a simple sheaf with viewport -> container -> widgets."""
    return create_design_sheaf_with_hierarchy(
        containers=["sidebar", "main"],
        widgets={
            "sidebar": ["nav", "actions"],
            "main": ["content", "footer"],
        },
    )


@pytest.fixture
def viewport_state() -> DesignState:
    """Default viewport state."""
    return DesignState(
        density=Density.SPACIOUS,
        content_level=ContentLevel.FULL,
        motion=MotionType.IDENTITY,
        should_animate=True,
    )


# =============================================================================
# DesignContext Tests
# =============================================================================


class TestDesignContext:
    """Tests for DesignContext hierarchy relationships."""

    def test_viewport_is_ancestor_of_all(self) -> None:
        """Viewport context is ancestor of all contexts."""
        container = create_container_context("main")
        widget = create_widget_context("button", "main")

        assert VIEWPORT_CONTEXT.is_ancestor_of(container)
        assert VIEWPORT_CONTEXT.is_ancestor_of(widget)

    def test_container_is_ancestor_of_widgets(self) -> None:
        """Container is ancestor of its child widgets."""
        container = create_container_context("main")
        widget = create_widget_context("button", "main")
        other_widget = create_widget_context("other", "sidebar")

        assert container.is_ancestor_of(widget)
        assert not container.is_ancestor_of(other_widget)

    def test_context_is_ancestor_of_self(self) -> None:
        """A context is its own ancestor (reflexive)."""
        ctx = create_container_context("main")
        assert ctx.is_ancestor_of(ctx)

    def test_siblings_share_parent(self) -> None:
        """Sibling contexts share the same parent."""
        widget1 = create_widget_context("nav", "sidebar")
        widget2 = create_widget_context("actions", "sidebar")
        other = create_widget_context("content", "main")

        assert widget1.shares_parent(widget2)
        assert not widget1.shares_parent(other)

    def test_density_override(self) -> None:
        """Container can have density override."""
        container = create_container_context(
            "sidebar",
            density_override=Density.COMPACT,
        )
        assert container.density_override == Density.COMPACT


# =============================================================================
# Overlap Tests
# =============================================================================


class TestOverlap:
    """Tests for sheaf overlap computation."""

    def test_same_context_overlaps_self(self, simple_sheaf: DesignSheaf) -> None:
        """Same context overlaps with itself."""
        ctx = simple_sheaf.get_context("sidebar")
        assert ctx is not None
        overlap = simple_sheaf.overlap(ctx, ctx)
        assert overlap == ctx

    def test_hierarchical_overlap_returns_descendant(
        self, simple_sheaf: DesignSheaf
    ) -> None:
        """Hierarchical overlap returns the more specific context."""
        sidebar = simple_sheaf.get_context("sidebar")
        nav = simple_sheaf.get_context("nav")

        assert sidebar is not None
        assert nav is not None

        overlap = simple_sheaf.overlap(sidebar, nav)
        assert overlap == nav

        # Order shouldn't matter
        overlap2 = simple_sheaf.overlap(nav, sidebar)
        assert overlap2 == nav

    def test_sibling_overlap_returns_parent(self, simple_sheaf: DesignSheaf) -> None:
        """Sibling contexts overlap at their shared parent."""
        nav = simple_sheaf.get_context("nav")
        actions = simple_sheaf.get_context("actions")
        sidebar = simple_sheaf.get_context("sidebar")

        assert nav is not None
        assert actions is not None
        assert sidebar is not None

        overlap = simple_sheaf.overlap(nav, actions)
        assert overlap == sidebar

    def test_no_overlap_between_different_branches(
        self, simple_sheaf: DesignSheaf
    ) -> None:
        """Contexts in different container branches don't overlap."""
        nav = simple_sheaf.get_context("nav")  # under sidebar
        content = simple_sheaf.get_context("content")  # under main

        assert nav is not None
        assert content is not None

        # They don't share a parent (at widget level)
        overlap = simple_sheaf.overlap(nav, content)
        # Both are under viewport transitively, but shares_parent returns False
        # so no overlap at widget-to-widget level
        assert overlap is None


# =============================================================================
# Restrict Tests
# =============================================================================


class TestRestrict:
    """Tests for sheaf restriction operation."""

    def test_restrict_preserves_viewport_state(
        self, simple_sheaf: DesignSheaf, viewport_state: DesignState
    ) -> None:
        """Restriction without override preserves viewport state."""
        sidebar = simple_sheaf.get_context("sidebar")
        assert sidebar is not None

        restricted = simple_sheaf.restrict(viewport_state, sidebar)

        assert restricted.density == viewport_state.density
        assert restricted.content_level == viewport_state.content_level
        assert restricted.motion == viewport_state.motion

    def test_restrict_applies_density_override(
        self, viewport_state: DesignState
    ) -> None:
        """Restriction applies container's density override."""
        sheaf = create_design_sheaf()
        compact_sidebar = create_container_context(
            "sidebar",
            density_override=Density.COMPACT,
        )
        sheaf.add_context(compact_sidebar)

        restricted = sheaf.restrict(viewport_state, compact_sidebar)

        assert restricted.density == Density.COMPACT
        # Other properties preserved
        assert restricted.content_level == viewport_state.content_level

    def test_restrict_unknown_context_raises(
        self, simple_sheaf: DesignSheaf, viewport_state: DesignState
    ) -> None:
        """Restriction to unknown context raises error."""
        unknown = create_container_context("unknown")

        with pytest.raises(RestrictionError, match="not found"):
            simple_sheaf.restrict(viewport_state, unknown)


# =============================================================================
# Compatible Tests
# =============================================================================


class TestCompatible:
    """Tests for sheaf compatibility checking."""

    def test_single_state_is_compatible(self, simple_sheaf: DesignSheaf) -> None:
        """A single local state is always compatible."""
        sidebar = simple_sheaf.get_context("sidebar")
        assert sidebar is not None

        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )

        assert simple_sheaf.compatible({sidebar: state})

    def test_same_density_siblings_compatible(self, simple_sheaf: DesignSheaf) -> None:
        """Siblings with same density are compatible."""
        nav = simple_sheaf.get_context("nav")
        actions = simple_sheaf.get_context("actions")
        assert nav is not None
        assert actions is not None

        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )

        assert simple_sheaf.compatible({nav: state, actions: state})

    def test_different_density_without_override_incompatible(self) -> None:
        """Different densities without override are incompatible."""
        sheaf = create_design_sheaf()
        container1 = create_container_context("c1")
        container2 = create_container_context("c2")
        sheaf.add_context(container1)
        sheaf.add_context(container2)

        state1 = DesignState(density=Density.SPACIOUS, content_level=ContentLevel.FULL)
        state2 = DesignState(density=Density.COMPACT, content_level=ContentLevel.ICON)

        # Both containers are under viewport (their parent), so they overlap.
        # With different densities and no overrides, they should be incompatible.
        result = sheaf.compatible({container1: state1, container2: state2})
        assert not result  # Different densities without override = incompatible

    def test_different_density_with_override_compatible(self) -> None:
        """Different densities with overrides are compatible."""
        sheaf = create_design_sheaf()
        container1 = create_container_context("c1", density_override=Density.SPACIOUS)
        container2 = create_container_context("c2", density_override=Density.COMPACT)
        sheaf.add_context(container1)
        sheaf.add_context(container2)

        state1 = DesignState(density=Density.SPACIOUS, content_level=ContentLevel.FULL)
        state2 = DesignState(density=Density.COMPACT, content_level=ContentLevel.ICON)

        assert sheaf.compatible({container1: state1, container2: state2})


# =============================================================================
# Glue Tests
# =============================================================================


class TestGlue:
    """Tests for sheaf gluing operation."""

    def test_glue_with_viewport_preserves_viewport_state(
        self, simple_sheaf: DesignSheaf
    ) -> None:
        """Gluing with viewport context preserves viewport state."""
        viewport_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.POP,
            should_animate=True,
        )

        glued = simple_sheaf.glue({VIEWPORT_CONTEXT: viewport_state})

        assert glued.density == viewport_state.density
        assert glued.content_level == viewport_state.content_level
        assert glued.motion == viewport_state.motion

    def test_glue_without_viewport_infers_global(self) -> None:
        """Gluing without viewport infers global state from locals."""
        sheaf = create_design_sheaf()
        container = create_container_context("main")
        sheaf.add_context(container)

        state = DesignState(
            density=Density.COMFORTABLE,
            content_level=ContentLevel.SUMMARY,
        )

        glued = sheaf.glue({container: state})

        assert glued.density == Density.COMFORTABLE
        assert glued.content_level == ContentLevel.SUMMARY

    def test_glue_respects_should_animate(self) -> None:
        """Gluing with should_animate=False forces identity motion."""
        sheaf = create_design_sheaf()

        state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.POP,  # This should be ignored
            should_animate=False,
        )

        glued = sheaf.glue({VIEWPORT_CONTEXT: state})

        assert glued.motion == MotionType.IDENTITY

    def test_glue_incompatible_raises(self) -> None:
        """Gluing incompatible states raises error."""
        # Create a scenario that's incompatible
        # This is hard with current impl since most things are compatible
        # Let's use monkeypatch to force incompatibility
        sheaf = create_design_sheaf()

        # Override compatible to return False
        original_compatible = sheaf.compatible
        sheaf.compatible = lambda _: False  # type: ignore

        with pytest.raises(GluingError):
            sheaf.glue(
                {VIEWPORT_CONTEXT: DesignState(Density.SPACIOUS, ContentLevel.FULL)}
            )

        # Restore
        sheaf.compatible = original_compatible  # type: ignore


# =============================================================================
# Integration Tests
# =============================================================================


class TestSheafIntegration:
    """Integration tests for the complete sheaf workflow."""

    def test_full_restrict_glue_cycle(self, simple_sheaf: DesignSheaf) -> None:
        """Test the full cycle: global -> restrict to locals -> glue back."""
        global_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.BREATHE,
            should_animate=True,
        )

        # Restrict to each context
        sidebar = simple_sheaf.get_context("sidebar")
        main = simple_sheaf.get_context("main")
        assert sidebar is not None
        assert main is not None

        sidebar_state = simple_sheaf.restrict(global_state, sidebar)
        main_state = simple_sheaf.restrict(global_state, main)

        # Glue back together
        glued = simple_sheaf.glue(
            {
                VIEWPORT_CONTEXT: global_state,
                sidebar: sidebar_state,
                main: main_state,
            }
        )

        # Should recover original state
        assert glued.density == global_state.density
        assert glued.motion == global_state.motion

    def test_coherence_with_overrides(self) -> None:
        """Test that overrides are respected in the coherence cycle."""
        sheaf = create_design_sheaf()
        compact_panel = create_container_context(
            "panel",
            density_override=Density.COMPACT,
        )
        sheaf.add_context(compact_panel)

        global_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
        )

        # Restrict to the compact panel
        local_state = sheaf.restrict(global_state, compact_panel)

        # Local should have compact density
        assert local_state.density == Density.COMPACT

        # But gluing back should preserve viewport's spacious
        glued = sheaf.glue(
            {
                VIEWPORT_CONTEXT: global_state,
                compact_panel: local_state,
            }
        )

        assert glued.density == Density.SPACIOUS

    def test_hierarchy_factory(self) -> None:
        """Test the convenience factory creates proper hierarchy."""
        sheaf = create_design_sheaf_with_hierarchy(
            containers=["left", "right"],
            widgets={
                "left": ["header", "body"],
                "right": ["sidebar"],
            },
        )

        # Check all contexts exist
        assert sheaf.get_context("left") is not None
        assert sheaf.get_context("right") is not None
        assert sheaf.get_context("header") is not None
        assert sheaf.get_context("body") is not None
        assert sheaf.get_context("sidebar") is not None

        # Check parent relationships
        header = sheaf.get_context("header")
        assert header is not None
        assert header.parent == "left"


# =============================================================================
# The Three-Layer Stack Completion Test
# =============================================================================


class TestThreeLayerStack:
    """
    Test that DesignSheaf completes the three-layer categorical stack.

    Layer 1: Sheaf (global coherence)
    Layer 2: PolyAgent (state machine)
    Layer 3: Operad (composition grammar)
    """

    def test_sheaf_works_with_polynomial_states(self) -> None:
        """Sheaf operations work with DesignState from polynomial."""
        from agents.design import DESIGN_POLYNOMIAL, ViewportResize

        sheaf = create_design_sheaf()

        # Get a state from the polynomial
        initial_pos = next(iter(DESIGN_POLYNOMIAL.positions))

        # Use it in sheaf operations
        assert sheaf.compatible({VIEWPORT_CONTEXT: initial_pos})

    def test_sheaf_respects_operad_laws(self) -> None:
        """Sheaf gluing respects operad composition laws."""
        # The key law: animations are gated by should_animate
        sheaf = create_design_sheaf()

        # Create a state that violates the motion law
        invalid_state = DesignState(
            density=Density.SPACIOUS,
            content_level=ContentLevel.FULL,
            motion=MotionType.POP,  # Has motion
            should_animate=False,  # But animations disabled
        )

        # Gluing should enforce the law
        glued = sheaf.glue({VIEWPORT_CONTEXT: invalid_state})

        # Motion should be forced to identity
        assert glued.motion == MotionType.IDENTITY
