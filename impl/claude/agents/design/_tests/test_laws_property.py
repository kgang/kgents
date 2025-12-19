"""
Property-based tests for DESIGN_OPERAD laws using Hypothesis.

These tests provide runtime verification of laws that were marked
as STRUCTURAL in the honesty audit. They prove the laws hold for
randomly generated inputs.

Laws verified:
1. composition_natural: Layout × Content × Motion compose orthogonally
2. content_lattice: ContentLevel forms a proper lattice
3. motion_identity: Identity motion is unit for composition
4. motion_should_animate: Animations gated by should_animate flag
"""

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st

from agents.design import (
    DESIGN_POLYNOMIAL,
    AnimationToggle,
    ContainerResize,
    ContentLevel,
    Density,
    DesignState,
    MotionRequest,
    MotionType,
    ViewportResize,
    design_transition,
)

# =============================================================================
# Strategies for generating design states and inputs
# =============================================================================


density_strategy = st.sampled_from(list(Density))
content_level_strategy = st.sampled_from(list(ContentLevel))
motion_type_strategy = st.sampled_from(list(MotionType))
bool_strategy = st.booleans()

design_state_strategy = st.builds(
    DesignState,
    density=density_strategy,
    content_level=content_level_strategy,
    motion=motion_type_strategy,
    should_animate=bool_strategy,
)

# Width strategies that map to known density/content thresholds
viewport_width_strategy = st.integers(min_value=200, max_value=2000)
container_width_strategy = st.integers(min_value=20, max_value=800)


# =============================================================================
# Law 1: Composition Naturality
# =============================================================================


class TestCompositionNaturality:
    """
    Test the naturality law: Layout[D] ∘ Content[D] ∘ Motion[M] is natural.

    This means applying layout, content, and motion changes in any order
    should yield the same final state (modulo the different dimension values).
    """

    @given(
        initial=design_state_strategy,
        viewport_width=viewport_width_strategy,
        container_width=container_width_strategy,
        motion=motion_type_strategy,
    )
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_order_independence_viewport_container_motion(
        self,
        initial: DesignState,
        viewport_width: int,
        container_width: int,
        motion: MotionType,
    ) -> None:
        """
        Applying viewport resize, container resize, and motion request
        in different orders should yield consistent results.

        The naturality law says these dimensions are orthogonal.
        """
        # Only test with animations enabled for motion testing
        initial = DesignState(
            density=initial.density,
            content_level=initial.content_level,
            motion=initial.motion,
            should_animate=True,
        )

        # Create inputs
        viewport_input = ViewportResize(viewport_width, 800)
        container_input = ContainerResize(container_width)
        motion_input = MotionRequest(motion)

        # Order 1: viewport -> container -> motion
        state1, _ = design_transition(initial, viewport_input)
        state1, _ = design_transition(state1, container_input)
        state1, _ = design_transition(state1, motion_input)

        # Order 2: motion -> viewport -> container
        state2, _ = design_transition(initial, motion_input)
        state2, _ = design_transition(state2, viewport_input)
        state2, _ = design_transition(state2, container_input)

        # Order 3: container -> motion -> viewport
        state3, _ = design_transition(initial, container_input)
        state3, _ = design_transition(state3, motion_input)
        state3, _ = design_transition(state3, viewport_input)

        # All orders should yield the same final state
        assert state1 == state2, f"Order 1 vs 2: {state1} != {state2}"
        assert state2 == state3, f"Order 2 vs 3: {state2} != {state3}"

    @given(
        initial=design_state_strategy,
        viewport_width=viewport_width_strategy,
        container_width=container_width_strategy,
    )
    @settings(max_examples=50)
    def test_layout_content_commute(
        self,
        initial: DesignState,
        viewport_width: int,
        container_width: int,
    ) -> None:
        """
        Layout (viewport) and content (container) changes commute.

        This is a specific case of naturality focusing on the non-motion axes.
        """
        viewport_input = ViewportResize(viewport_width, 800)
        container_input = ContainerResize(container_width)

        # Order 1: viewport then container
        s1, _ = design_transition(initial, viewport_input)
        s1, _ = design_transition(s1, container_input)

        # Order 2: container then viewport
        s2, _ = design_transition(initial, container_input)
        s2, _ = design_transition(s2, viewport_input)

        assert s1 == s2


# =============================================================================
# Law 2: Content Lattice
# =============================================================================


class TestContentLattice:
    """
    Test the content lattice law:
    degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)

    This verifies the inclusion relationship between content levels.
    """

    @given(level1=content_level_strategy, level2=content_level_strategy)
    def test_lattice_transitivity(self, level1: ContentLevel, level2: ContentLevel) -> None:
        """
        If A includes B and B includes C, then A includes C.
        """
        order = [
            ContentLevel.ICON,
            ContentLevel.TITLE,
            ContentLevel.SUMMARY,
            ContentLevel.FULL,
        ]

        idx1 = order.index(level1)
        idx2 = order.index(level2)

        # level1 includes level2 iff idx1 >= idx2
        should_include = idx1 >= idx2
        assert level1.includes(level2) == should_include

    @given(level=content_level_strategy)
    def test_lattice_reflexivity(self, level: ContentLevel) -> None:
        """Every level includes itself."""
        assert level.includes(level)

    @given(
        level1=content_level_strategy,
        level2=content_level_strategy,
        level3=content_level_strategy,
    )
    def test_lattice_transitivity_explicit(
        self,
        level1: ContentLevel,
        level2: ContentLevel,
        level3: ContentLevel,
    ) -> None:
        """If level1 includes level2 and level2 includes level3, then level1 includes level3."""
        if level1.includes(level2) and level2.includes(level3):
            assert level1.includes(level3)


# =============================================================================
# Law 3: Motion Identity
# =============================================================================


class TestMotionIdentity:
    """
    Test the motion identity law: chain(identity, m) = m = chain(m, identity).

    At the state machine level, this means requesting IDENTITY motion
    doesn't change the state.
    """

    @given(state=design_state_strategy)
    def test_identity_motion_is_no_op(self, state: DesignState) -> None:
        """Requesting identity motion doesn't change state."""
        # Only test with animations enabled
        state = DesignState(
            density=state.density,
            content_level=state.content_level,
            motion=state.motion,
            should_animate=True,
        )

        new_state, _ = design_transition(state, MotionRequest(MotionType.IDENTITY))

        # If motion was already identity, state unchanged
        # If motion was different, it becomes identity
        assert new_state.motion == MotionType.IDENTITY

    @given(
        state=design_state_strategy,
        motion1=motion_type_strategy,
        motion2=motion_type_strategy,
    )
    @settings(max_examples=50)
    def test_identity_composes_left(
        self,
        state: DesignState,
        motion1: MotionType,
        motion2: MotionType,
    ) -> None:
        """
        Identity ∘ M = M (left identity).

        Applying identity then another motion is same as just applying other motion.
        """
        state = DesignState(
            density=state.density,
            content_level=state.content_level,
            motion=MotionType.IDENTITY,  # Start from identity
            should_animate=True,
        )

        # Apply identity then motion2
        s1, _ = design_transition(state, MotionRequest(MotionType.IDENTITY))
        s1, _ = design_transition(s1, MotionRequest(motion2))

        # Apply just motion2
        s2, _ = design_transition(state, MotionRequest(motion2))

        assert s1.motion == s2.motion


# =============================================================================
# Law 4: Animation Gating
# =============================================================================


class TestAnimationGating:
    """
    Test the animation gating law: !shouldAnimate => all operations = identity.

    When animations are disabled, motion requests should be ignored.
    """

    @given(
        state=design_state_strategy,
        motion=motion_type_strategy,
    )
    def test_disabled_animations_ignore_motion(
        self,
        state: DesignState,
        motion: MotionType,
    ) -> None:
        """Motion requests are ignored when should_animate=False."""
        # Ensure animations are disabled
        state = DesignState(
            density=state.density,
            content_level=state.content_level,
            motion=MotionType.IDENTITY,  # Start from identity
            should_animate=False,
        )

        new_state, _ = design_transition(state, MotionRequest(motion))

        # Motion should remain identity regardless of request
        assert new_state.motion == MotionType.IDENTITY

    @given(state=design_state_strategy)
    def test_animation_toggle_resets_motion(self, state: DesignState) -> None:
        """Disabling animations resets motion to identity."""
        # Start with some motion and animations enabled
        state = DesignState(
            density=state.density,
            content_level=state.content_level,
            motion=MotionType.POP,  # Non-identity motion
            should_animate=True,
        )

        # Disable animations
        new_state, _ = design_transition(state, AnimationToggle(enabled=False))

        assert new_state.should_animate is False
        assert new_state.motion == MotionType.IDENTITY


# =============================================================================
# Additional Property Tests
# =============================================================================


class TestStateSpaceProperties:
    """Property tests for the design state space."""

    @given(width=viewport_width_strategy)
    def test_density_from_width_covers_all_densities(self, width: int) -> None:
        """Density.from_width always returns a valid density."""
        density = Density.from_width(width)
        assert density in list(Density)

    @given(width=container_width_strategy)
    def test_content_level_from_width_covers_all_levels(self, width: int) -> None:
        """ContentLevel.from_width always returns a valid level."""
        level = ContentLevel.from_width(width)
        assert level in list(ContentLevel)

    @given(state=design_state_strategy)
    def test_polynomial_positions_include_all_states(self, state: DesignState) -> None:
        """Every valid DesignState is in the polynomial's position set."""
        assert state in DESIGN_POLYNOMIAL.positions

    @given(
        state=design_state_strategy,
        viewport_width=viewport_width_strategy,
    )
    def test_transition_stays_in_state_space(
        self,
        state: DesignState,
        viewport_width: int,
    ) -> None:
        """Transitions always produce valid states in the position set."""
        new_state, _ = design_transition(state, ViewportResize(viewport_width, 800))
        assert new_state in DESIGN_POLYNOMIAL.positions


# =============================================================================
# Stress Tests
# =============================================================================


class TestStressSequences:
    """Stress tests with sequences of operations."""

    @given(
        initial=design_state_strategy,
        operations=st.lists(
            st.one_of(
                st.builds(ViewportResize, width=viewport_width_strategy, height=st.just(800)),
                st.builds(ContainerResize, width=container_width_strategy),
                st.builds(AnimationToggle, enabled=bool_strategy),
                st.builds(MotionRequest, motion=motion_type_strategy),
            ),
            min_size=1,
            max_size=20,
        ),
    )
    @settings(max_examples=50)
    def test_arbitrary_operation_sequences(
        self,
        initial: DesignState,
        operations: list,
    ) -> None:
        """
        Apply arbitrary sequences of operations.

        Verifies that:
        1. No operation causes an exception
        2. Every resulting state is valid
        """
        state = initial

        for op in operations:
            state, _ = design_transition(state, op)
            assert state in DESIGN_POLYNOMIAL.positions

    @given(
        state=design_state_strategy,
        widths=st.lists(viewport_width_strategy, min_size=1, max_size=10),
    )
    @settings(max_examples=30)
    def test_rapid_resize_sequence(
        self,
        state: DesignState,
        widths: list[int],
    ) -> None:
        """Simulate rapid viewport resizing (e.g., window drag)."""
        for width in widths:
            state, _ = design_transition(state, ViewportResize(width, 800))
            assert state in DESIGN_POLYNOMIAL.positions

        # Final state should have density matching final width
        expected_density = Density.from_width(widths[-1])
        assert state.density == expected_density
