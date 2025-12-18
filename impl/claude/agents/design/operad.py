"""
Design Operads: Grammar of UI Composition.

Three orthogonal operads define the complete design language:
- LAYOUT_OPERAD: Structural composition (split, stack, drawer, float)
- CONTENT_OPERAD: Content degradation (degrade, compose)
- MOTION_OPERAD: Animation composition (breathe, pop, shake, chain, parallel)

The DESIGN_OPERAD combines all three, with the fundamental law:
    Layout[D] ∘ Content[D] ∘ Motion[M] is natural

This means UI = structure × content × motion, and these compose orthogonally.

IMPORTANT CAVEAT (Honesty Principle):
These operads compose PolyAgent state machines, NOT React components directly.
The functor from DESIGN_OPERAD to actual UI elements requires:
1. A React hook (useDesignPolynomial) that consumes DESIGN_POLYNOMIAL state
2. Component adapters that map operad operations to JSX
3. The Projection Protocol (spec/protocols/projection.md) to bridge

Current state: Layer 2-3 (PolyAgent + Operad) are complete.
              Layer 7 (Projection to React) is NOT YET IMPLEMENTED.

See: plans/design-language-consolidation.md for roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agents.operad import (
    Law,
    LawStatus,
    LawVerification,
    Operad,
    OperadRegistry,
    Operation,
)
from agents.poly import PolyAgent

from .types import ContentLevel, Density, DesignState, LayoutType, MotionType

# =============================================================================
# Layout Operations
# =============================================================================


def _split_compose(
    primary: PolyAgent[Any, Any, Any],
    secondary: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Two-pane layout with collapse behavior.

    At compact density: secondary collapses to drawer
    At spacious density: side-by-side with draggable divider
    """
    from agents.poly import parallel

    return parallel(primary, secondary)


def _stack_compose(*widgets: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Vertical/horizontal stack of widgets.

    The variadic version of sequential composition.
    """
    from agents.poly import identity, sequential

    if len(widgets) == 0:
        return identity()
    if len(widgets) == 1:
        return widgets[0]

    result = widgets[0]
    for w in widgets[1:]:
        result = sequential(result, w)
    return result


def _drawer_compose(
    trigger: PolyAgent[Any, Any, Any],
    content: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Collapsible drawer pattern.

    Mobile: slide-up bottom drawer
    Desktop: collapsible side panel
    """
    from agents.poly import parallel

    return parallel(trigger, content)


def _float_compose(*actions: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Floating action buttons cluster.

    Touch-friendly action buttons that float over content.
    """
    return _stack_compose(*actions)


# =============================================================================
# Content Operations
# =============================================================================


def _degrade_compose(
    full_widget: PolyAgent[Any, Any, Any],
    level_widget: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Reduce content to fit available space.

    The level determines what to show:
    - icon: just the icon
    - title: icon + name
    - summary: icon + name + brief
    - full: everything

    Law: degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)
    """
    from agents.poly import sequential

    return sequential(full_widget, level_widget)


def _content_compose(
    widget_a: PolyAgent[Any, Any, Any],
    widget_b: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Combine widget content.

    Law: compose(degrade(a, L), degrade(b, L)) = degrade(compose(a, b), L)
    """
    from agents.poly import parallel

    return parallel(widget_a, widget_b)


# =============================================================================
# Motion Operations
# =============================================================================


def _identity_motion(widget: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """No animation - identity functor."""
    return widget


def _breathe_motion(widget: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """Gentle pulse animation."""
    # Motion is metadata; the widget passes through unchanged
    return widget


def _pop_motion(widget: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """Scale bounce animation."""
    return widget


def _shake_motion(widget: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """Horizontal vibration animation."""
    return widget


def _shimmer_motion(widget: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """Highlight sweep animation."""
    return widget


def _chain_motion(
    first: PolyAgent[Any, Any, Any],
    second: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Sequential animation: first then second."""
    from agents.poly import sequential

    return sequential(first, second)


def _parallel_motion(
    left: PolyAgent[Any, Any, Any],
    right: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """Parallel animation: both simultaneously."""
    from agents.poly import parallel

    return parallel(left, right)


# =============================================================================
# Law Verification
# =============================================================================


def _verify_content_lattice(*args: Any) -> LawVerification:
    """
    Verify: degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)

    This is a type-level law - content levels form a lattice.
    """
    # Verify the lattice ordering is correct
    try:
        assert ContentLevel.ICON.includes(ContentLevel.ICON)
        assert ContentLevel.TITLE.includes(ContentLevel.ICON)
        assert ContentLevel.SUMMARY.includes(ContentLevel.TITLE)
        assert ContentLevel.FULL.includes(ContentLevel.SUMMARY)

        # Verify antisymmetry
        assert not ContentLevel.ICON.includes(ContentLevel.TITLE)

        return LawVerification(
            law_name="content_lattice",
            status=LawStatus.PASSED,
            message="Content levels form a proper lattice",
        )
    except AssertionError as e:
        return LawVerification(
            law_name="content_lattice",
            status=LawStatus.FAILED,
            message=str(e),
        )


def _verify_motion_identity(*args: Any) -> LawVerification:
    """
    Verify: chain(identity, m) = m = chain(m, identity).

    HONESTY: This is a structural law verified by the type system,
    not by runtime tests. The identity motion returns its input unchanged,
    so composition with it is a no-op by construction.
    """
    return LawVerification(
        law_name="motion_identity",
        status=LawStatus.STRUCTURAL,
        message="Identity law holds by construction: _identity_motion returns input unchanged",
    )


def _verify_motion_should_animate(*args: Any) -> LawVerification:
    """
    Verify: !shouldAnimate => all operations = identity.

    HONESTY: This law is enforced by DESIGN_POLYNOMIAL.transition(),
    not by this verification. When should_animate=False, MotionRequest
    inputs are ignored. The verification confirms the code path exists.
    """
    # Check that the transition logic exists
    from .polynomial import MotionRequest, design_transition
    from .types import ContentLevel

    # Create a state with animations disabled
    disabled_state = DesignState(
        density=Density.SPACIOUS,
        content_level=ContentLevel.FULL,
        motion=MotionType.IDENTITY,
        should_animate=False,
    )

    # Attempt to apply a motion - should be ignored
    new_state, output = design_transition(disabled_state, MotionRequest(MotionType.POP))

    if new_state.motion == MotionType.IDENTITY:
        return LawVerification(
            law_name="motion_should_animate",
            status=LawStatus.PASSED,
            message="Animation gating verified: MotionRequest ignored when should_animate=False",
        )
    else:
        return LawVerification(
            law_name="motion_should_animate",
            status=LawStatus.FAILED,
            message=f"Animation gating FAILED: motion changed to {new_state.motion} despite should_animate=False",
        )


def _verify_composition_natural(*args: Any) -> LawVerification:
    """
    Verify: Layout[D] ∘ Content[D] ∘ Motion[M] is natural.

    This means the three functors compose without interference.

    HONESTY: This is a design assertion, not a runtime verification.
    The claim is that Layout, Content, and Motion are orthogonal dimensions
    that don't interfere with each other. This is enforced by:
    1. DesignState being a product type (density × content_level × motion)
    2. Each input type only affecting its own dimension
    3. The polynomial transition handling each independently

    A true runtime test would require showing that for any state s and
    inputs (l, c, m), the order of application doesn't matter:
        apply(apply(apply(s, l), c), m) = apply(apply(apply(s, m), c), l)

    We mark this as STRUCTURAL because the independence is guaranteed by
    the type structure, but we have NOT tested all orderings.
    """
    return LawVerification(
        law_name="composition_natural",
        status=LawStatus.STRUCTURAL,
        message=(
            "Naturality asserted by design: DesignState is a product type "
            "with independent dimensions. Full permutation test NOT performed."
        ),
    )


def _verify_split_drawer_equivalence(*args: Any) -> LawVerification:
    """
    Verify: split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact density.

    At compact density, split collapses to drawer, so these are isomorphic.

    HONESTY: This law describes the INTENDED behavior of React components
    at compact density, not the behavior of the PolyAgent compositions.
    The _split_compose and _drawer_compose functions both wrap to parallel(),
    so the PolyAgent compositions ARE equivalent by construction.

    However, this law is really about UI RENDERING:
    - At compact: split's secondary pane becomes a drawer
    - Therefore: nesting order shouldn't matter

    We cannot verify this without actual React components. We mark as
    STRUCTURAL because the PolyAgent level IS equivalent (both use parallel).
    """
    return LawVerification(
        law_name="split_drawer_equivalence",
        status=LawStatus.STRUCTURAL,
        message=(
            "PolyAgent level: equivalent by construction (both use parallel). "
            "React UI level: NOT YET TESTABLE (components not implemented)."
        ),
    )


# =============================================================================
# Operad Definitions
# =============================================================================


def create_layout_operad() -> Operad:
    """Create the LAYOUT_OPERAD for structural composition."""
    return Operad(
        name="LAYOUT",
        operations={
            "split": Operation(
                name="split",
                arity=2,
                signature="(Widget, Widget) → ElasticSplit",
                compose=_split_compose,
                description="Two-pane layout with collapse behavior",
            ),
            "stack": Operation(
                name="stack",
                arity=-1,  # Variadic
                signature="(*Widget) → ElasticContainer",
                compose=_stack_compose,
                description="Vertical/horizontal stack",
            ),
            "drawer": Operation(
                name="drawer",
                arity=2,
                signature="(Trigger, Content) → BottomDrawer",
                compose=_drawer_compose,
                description="Collapsible drawer pattern",
            ),
            "float": Operation(
                name="float",
                arity=-1,  # Variadic
                signature="(*Action) → FloatingActions",
                compose=_float_compose,
                description="Floating action buttons",
            ),
        },
        laws=[
            Law(
                name="split_drawer_equivalence",
                equation="split(a, drawer(t, b)) ≅ drawer(t, split(a, b)) at compact",
                verify=_verify_split_drawer_equivalence,
                description="At compact density, split and drawer are isomorphic",
            ),
        ],
        description="Grammar for structural UI composition",
    )


def create_content_operad() -> Operad:
    """Create the CONTENT_OPERAD for content degradation."""
    return Operad(
        name="CONTENT",
        operations={
            "degrade": Operation(
                name="degrade",
                arity=2,
                signature="(Full, Level) → Truncated",
                compose=_degrade_compose,
                description="Reduce content to fit space",
            ),
            "compose": Operation(
                name="compose",
                arity=2,
                signature="(Widget, Widget) → Combined",
                compose=_content_compose,
                description="Combine widget content",
            ),
        },
        laws=[
            Law(
                name="content_lattice",
                equation="degrade(x, icon) ⊆ degrade(x, title) ⊆ degrade(x, summary) ⊆ degrade(x, full)",
                verify=_verify_content_lattice,
                description="Content levels form a lattice under inclusion",
            ),
        ],
        description="Grammar for content degradation",
    )


def create_motion_operad() -> Operad:
    """Create the MOTION_OPERAD for animation composition."""
    return Operad(
        name="MOTION",
        operations={
            "identity": Operation(
                name="identity",
                arity=1,
                signature="Widget → Widget",
                compose=_identity_motion,
                description="No animation",
            ),
            "breathe": Operation(
                name="breathe",
                arity=1,
                signature="Widget → Animated",
                compose=_breathe_motion,
                description="Gentle pulse",
            ),
            "pop": Operation(
                name="pop",
                arity=1,
                signature="Widget → Animated",
                compose=_pop_motion,
                description="Scale bounce",
            ),
            "shake": Operation(
                name="shake",
                arity=1,
                signature="Widget → Animated",
                compose=_shake_motion,
                description="Horizontal vibration",
            ),
            "shimmer": Operation(
                name="shimmer",
                arity=1,
                signature="Widget → Animated",
                compose=_shimmer_motion,
                description="Highlight sweep",
            ),
            "chain": Operation(
                name="chain",
                arity=2,
                signature="(Motion, Motion) → Sequential",
                compose=_chain_motion,
                description="Sequential animation",
            ),
            "parallel": Operation(
                name="parallel",
                arity=2,
                signature="(Motion, Motion) → Simultaneous",
                compose=_parallel_motion,
                description="Parallel animation",
            ),
        },
        laws=[
            Law(
                name="motion_identity",
                equation="chain(identity, m) = m = chain(m, identity)",
                verify=_verify_motion_identity,
                description="Identity is the unit for animation composition",
            ),
            Law(
                name="motion_should_animate",
                equation="!shouldAnimate => all operations = identity",
                verify=_verify_motion_should_animate,
                description="Animation gating law",
            ),
        ],
        description="Grammar for animation composition",
    )


def create_design_operad() -> Operad:
    """
    Create the unified DESIGN_OPERAD.

    This combines all three sub-operads with the naturality law.
    """
    layout = create_layout_operad()
    content = create_content_operad()
    motion = create_motion_operad()

    return Operad(
        name="DESIGN",
        operations={
            **layout.operations,
            **content.operations,
            **motion.operations,
        },
        laws=[
            *layout.laws,
            *content.laws,
            *motion.laws,
            Law(
                name="composition_natural",
                equation="Layout[D] ∘ Content[D] ∘ Motion[M] is natural",
                verify=_verify_composition_natural,
                description="The three dimensions compose orthogonally",
            ),
        ],
        description="Unified grammar for UI composition: Layout × Content × Motion",
    )


# =============================================================================
# Global Instances
# =============================================================================

LAYOUT_OPERAD = create_layout_operad()
CONTENT_OPERAD = create_content_operad()
MOTION_OPERAD = create_motion_operad()
DESIGN_OPERAD = create_design_operad()

# Register with the operad registry
OperadRegistry.register(LAYOUT_OPERAD)
OperadRegistry.register(CONTENT_OPERAD)
OperadRegistry.register(MOTION_OPERAD)
OperadRegistry.register(DESIGN_OPERAD)


__all__ = [
    # Operads
    "LAYOUT_OPERAD",
    "CONTENT_OPERAD",
    "MOTION_OPERAD",
    "DESIGN_OPERAD",
    # Factories
    "create_layout_operad",
    "create_content_operad",
    "create_motion_operad",
    "create_design_operad",
]
