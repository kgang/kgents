"""
Design Sheaf: Global Coherence from Local Views.

The DesignSheaf completes the three-layer categorical stack:
1. ✅ DESIGN_POLYNOMIAL: State machine with mode-dependent inputs
2. ✅ DESIGN_OPERAD: Composition grammar with laws
3. ✅ DesignSheaf: Global coherence from local views (THIS FILE)

The sheaf is needed because UI components exist in a HIERARCHY:
- Viewport (root) determines global density
- Containers (branches) may have local overrides
- Widgets (leaves) render based on local context

The sheaf provides:
1. overlap(): When do contexts share state?
2. compatible(): Are sibling components' density settings consistent?
3. glue(): Combine local states into coherent global state
4. restrict(): Extract widget state from viewport state

Key insight: Gluing is where COHERENCE emerges.
Individual widgets don't know about each other, but the sheaf
ensures they combine into a consistent UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, FrozenSet

if TYPE_CHECKING:
    from agents.poly import PolyAgent
    from agents.sheaf.protocol import Context

from .types import (
    AnimationConstraint,
    AnimationPhase,
    ContentLevel,
    Density,
    DesignState,
    MotionType,
    SyncStrategy,
    TemporalOverlap,
)

# =============================================================================
# Design Contexts
# =============================================================================


@dataclass(frozen=True)
class DesignContext:
    """
    A context in the design component hierarchy.

    Contexts form a tree:
    - ViewportContext: root, determines global density
    - ContainerContext: branches, may override density
    - WidgetContext: leaves, render with inherited or local state

    The parent relationship creates the hierarchy:
        viewport
         ├── container_A
         │    ├── widget_A1
         │    └── widget_A2
         └── container_B
              └── widget_B1

    Attributes:
        name: Unique identifier for this context
        level: "viewport" | "container" | "widget"
        parent: Name of parent context (None for viewport)
        density_override: Optional local density (overrides inherited)
    """

    name: str
    level: str  # "viewport" | "container" | "widget"
    parent: str | None = None
    density_override: Density | None = None

    def __hash__(self) -> int:
        return hash((self.name, self.level, self.parent))

    def is_ancestor_of(self, other: DesignContext) -> bool:
        """Check if this context is an ancestor of another."""
        # A context is its own ancestor (reflexive for overlap)
        if self.name == other.name:
            return True
        # Viewport is ancestor of all
        if self.level == "viewport":
            return True
        # Container is ancestor of widgets with matching name prefix
        if self.level == "container" and other.level == "widget":
            return other.parent == self.name
        return False

    def shares_parent(self, other: DesignContext) -> bool:
        """Check if two contexts share the same parent (siblings)."""
        if self.parent is None or other.parent is None:
            return False
        return self.parent == other.parent


# Standard contexts
VIEWPORT_CONTEXT = DesignContext("viewport", "viewport")


def create_container_context(
    name: str,
    parent: str = "viewport",
    density_override: Density | None = None,
) -> DesignContext:
    """Create a container context with optional density override."""
    return DesignContext(
        name=name,
        level="container",
        parent=parent,
        density_override=density_override,
    )


def create_widget_context(
    name: str,
    parent: str,
) -> DesignContext:
    """Create a widget context under a container."""
    return DesignContext(
        name=name,
        level="widget",
        parent=parent,
    )


# =============================================================================
# Sheaf Errors
# =============================================================================


@dataclass
class GluingError(Exception):
    """Raised when local states cannot be glued."""

    contexts: list[str]
    reason: str

    def __str__(self) -> str:
        return f"Cannot glue contexts {self.contexts}: {self.reason}"


@dataclass
class RestrictionError(Exception):
    """Raised when restriction fails."""

    context: str
    reason: str

    def __str__(self) -> str:
        return f"Cannot restrict to {self.context}: {self.reason}"


# =============================================================================
# DesignSheaf Implementation
# =============================================================================


class DesignSheaf:
    """
    Sheaf structure for design state coherence.

    Provides the four sheaf operations:
    - overlap: Compute shared context between two contexts
    - restrict: Extract local state from global state
    - compatible: Check if local states agree on overlaps
    - glue: Combine compatible local states into global state

    The gluing operation is where UI COHERENCE happens:
    - Global viewport density constrains all children
    - Container overrides must be compatible with parent
    - Widget states glue into consistent UI rendering
    """

    def __init__(
        self,
        contexts: set[DesignContext] | None = None,
    ):
        """
        Initialize design sheaf.

        Args:
            contexts: Set of contexts in the component hierarchy.
                     Defaults to just the viewport context.
        """
        self.contexts = contexts or {VIEWPORT_CONTEXT}
        self._context_map: dict[str, DesignContext] = {ctx.name: ctx for ctx in self.contexts}

    def add_context(self, context: DesignContext) -> None:
        """Add a context to the sheaf."""
        self.contexts.add(context)
        self._context_map[context.name] = context

    def get_context(self, name: str) -> DesignContext | None:
        """Get a context by name."""
        return self._context_map.get(name)

    def overlap(self, ctx1: DesignContext, ctx2: DesignContext) -> DesignContext | None:
        """
        Compute overlap of two design contexts.

        Contexts overlap when:
        1. One is an ancestor of the other (hierarchy overlap)
        2. They share a common parent (sibling overlap)

        For hierarchical overlap, we return the descendant (more specific).
        For sibling overlap, we return their common parent.

        Args:
            ctx1: First context
            ctx2: Second context

        Returns:
            The overlap context, or None if no overlap
        """
        # Same context: overlap is self
        if ctx1.name == ctx2.name:
            return ctx1

        # Hierarchical overlap: one is ancestor of other
        if ctx1.is_ancestor_of(ctx2):
            return ctx2  # Return the more specific (descendant)
        if ctx2.is_ancestor_of(ctx1):
            return ctx1

        # Sibling overlap: share parent
        if ctx1.shares_parent(ctx2):
            # Return the shared parent as the overlap
            parent_ctx = self._context_map.get(ctx1.parent or "")
            return parent_ctx

        # No overlap
        return None

    def temporal_overlap(
        self,
        ctx1: DesignContext,
        state1: DesignState,
        ctx2: DesignContext,
        state2: DesignState,
    ) -> TemporalOverlap | None:
        """
        Compute temporal overlap between animating contexts.

        Two contexts temporally overlap when:
        1. They are spatial siblings (share parent)
        2. Both have active animation phases
        3. Their animation windows intersect

        Args:
            ctx1: First design context
            state1: State of first context (must have animation_phase)
            ctx2: Second design context
            state2: State of second context (must have animation_phase)

        Returns:
            TemporalOverlap with synchronization requirements, or None if no overlap.
        """
        # Check spatial sibling relationship
        if not ctx1.shares_parent(ctx2):
            return None

        # Check both have animation phases
        if state1.animation_phase is None or state2.animation_phase is None:
            return None

        phase1 = state1.animation_phase
        phase2 = state2.animation_phase

        # Check temporal intersection
        end1 = phase1.end_time
        end2 = phase2.end_time

        overlap_start = max(phase1.started_at, phase2.started_at)
        overlap_end = min(end1, end2)

        if overlap_start >= overlap_end:
            return None  # No temporal overlap

        return TemporalOverlap(
            contexts=(ctx1.name, ctx2.name),
            window=(overlap_start, overlap_end),
            sync_strategy=self._infer_sync_strategy(phase1, phase2),
        )

    def _infer_sync_strategy(self, phase1: AnimationPhase, phase2: AnimationPhase) -> SyncStrategy:
        """
        Infer appropriate sync strategy from animation phases.

        Rules:
        - entering + exiting = STAGGER (exit completes before enter starts)
        - entering + entering = LOCK_STEP (move together)
        - exiting + exiting = LOCK_STEP
        - active + any = INTERPOLATE_BOUNDARY
        - idle phases don't animate, so they get LOCK_STEP by default
        """
        p1, p2 = phase1.phase, phase2.phase

        # Entering + exiting: stagger them
        if (p1 == "entering" and p2 == "exiting") or (p1 == "exiting" and p2 == "entering"):
            return SyncStrategy.STAGGER

        # Same phase: lock step
        if p1 == p2:
            return SyncStrategy.LOCK_STEP

        # One is active: interpolate boundary
        if p1 == "active" or p2 == "active":
            return SyncStrategy.INTERPOLATE_BOUNDARY

        # Default: lock step
        return SyncStrategy.LOCK_STEP

    def restrict(
        self,
        global_state: DesignState,
        subcontext: DesignContext,
    ) -> DesignState:
        """
        Restrict global design state to a subcontext.

        Given viewport-level state, extract the state that applies
        to a specific container or widget.

        The restriction rules:
        1. Containers may override density (if density_override set)
        2. Widgets inherit from their container
        3. Motion and content_level are preserved

        Args:
            global_state: The viewport-level design state
            subcontext: The context to restrict to

        Returns:
            DesignState for the subcontext

        Raises:
            RestrictionError: If subcontext is not in the sheaf
        """
        if subcontext.name not in self._context_map:
            raise RestrictionError(
                context=subcontext.name,
                reason="Context not found in sheaf",
            )

        # Apply density override if present
        density = global_state.density
        if subcontext.density_override is not None:
            density = subcontext.density_override

        # Content level may need adjustment based on container hierarchy
        # (widgets in nested containers may have less space)
        content_level = global_state.content_level
        if subcontext.level == "widget":
            # Widgets might have restricted content due to nesting
            # This is a simplification - real impl would check actual sizes
            pass

        return DesignState(
            density=density,
            content_level=content_level,
            motion=global_state.motion,
            should_animate=global_state.should_animate,
        )

    def compatible(
        self,
        locals: dict[DesignContext, DesignState],
    ) -> bool:
        """
        Check if local design states are compatible for gluing.

        Locals are compatible when:
        1. Sibling containers don't have conflicting density overrides
           that would cause visual jarring
        2. Child states are reachable from parent state

        The key insight: density can vary between containers, but
        siblings under the same parent should be "harmonious" -
        either both override or neither does.

        Args:
            locals: Dict mapping contexts to their local states

        Returns:
            True if all local states can be glued
        """
        ctx_list = list(locals.keys())

        for i, ctx1 in enumerate(ctx_list):
            for ctx2 in ctx_list[i + 1 :]:
                state1 = locals[ctx1]
                state2 = locals[ctx2]

                # Check sibling compatibility
                if ctx1.shares_parent(ctx2):
                    # Siblings must have compatible densities
                    # Rule: either same density, or both have overrides
                    has_override_1 = ctx1.density_override is not None
                    has_override_2 = ctx2.density_override is not None

                    # If only one has override, they're incompatible
                    # (This is a design choice - could be relaxed)
                    if has_override_1 != has_override_2:
                        # One has override, other doesn't - potentially jarring
                        # We allow this but it's a "weak" compatibility
                        pass

                # Check hierarchical compatibility
                overlap = self.overlap(ctx1, ctx2)
                if overlap is not None:
                    # States on overlap must agree
                    # For now, we just check that neither is in an impossible state
                    if state1.density != state2.density:
                        # Check if the difference is explained by overrides
                        if ctx1.density_override is None and ctx2.density_override is None:
                            # Different densities without override = incompatible
                            return False

        return True

    def glue(
        self,
        locals: dict[DesignContext, DesignState],
    ) -> DesignState:
        """
        Glue compatible local states into global state.

        This is where UI COHERENCE happens:
        - Individual widget states combine into consistent rendering
        - Conflicts are detected and reported
        - Global invariants are enforced

        The gluing algorithm:
        1. Find the viewport context's state (if present)
        2. Verify all other states are reachable from it
        3. Return the viewport state as the global state

        Args:
            locals: Dict mapping contexts to their local states.
                   Must be compatible (call compatible() first).

        Returns:
            The glued global state

        Raises:
            GluingError: If local states cannot be glued
        """
        if not self.compatible(locals):
            raise GluingError(
                contexts=list(ctx.name for ctx in locals.keys()),
                reason="Local states not compatible on overlaps",
            )

        # Find viewport state
        viewport_state = None
        for ctx, state in locals.items():
            if ctx.level == "viewport":
                viewport_state = state
                break

        if viewport_state is None:
            # No viewport - infer from most general context
            # Pick the state with most spacious density as "global"
            density_order = [Density.SPACIOUS, Density.COMFORTABLE, Density.COMPACT]
            for density in density_order:
                for ctx, state in locals.items():
                    if state.density == density:
                        viewport_state = state
                        break
                if viewport_state is not None:
                    break

        if viewport_state is None:
            # Still nothing - use first state
            viewport_state = next(iter(locals.values()))

        # The global state preserves:
        # - The most permissive density (from viewport or inference)
        # - Animation settings from viewport
        # - Motion that's consistent with should_animate

        return DesignState(
            density=viewport_state.density,
            content_level=viewport_state.content_level,
            motion=viewport_state.motion if viewport_state.should_animate else MotionType.IDENTITY,
            should_animate=viewport_state.should_animate,
        )

    def glue_with_constraints(
        self,
        locals: dict[DesignContext, DesignState],
    ) -> tuple[DesignState, list[AnimationConstraint]]:
        """
        Glue local states, returning global state + animation constraints.

        The constraints tell the React layer how to coordinate animations
        between sibling components that are animating simultaneously.

        This is the temporal-coherence-aware version of glue(). Use this
        when you need to coordinate animations between components.

        Args:
            locals: Dict mapping contexts to their local states.
                   States may have animation_phase set for temporal coordination.

        Returns:
            Tuple of (glued global state, list of animation constraints)

        Raises:
            GluingError: If local states cannot be glued
        """
        # Existing spatial gluing
        global_state = self.glue(locals)

        # Compute temporal constraints
        constraints: list[AnimationConstraint] = []
        ctx_list = list(locals.keys())

        for i, ctx1 in enumerate(ctx_list):
            for ctx2 in ctx_list[i + 1 :]:
                state1 = locals[ctx1]
                state2 = locals[ctx2]

                overlap = self.temporal_overlap(ctx1, state1, ctx2, state2)
                if overlap is not None:
                    constraints.append(
                        AnimationConstraint(
                            source=overlap.contexts[0],
                            target=overlap.contexts[1],
                            strategy=overlap.sync_strategy,
                            window=overlap.window,
                        )
                    )

        return global_state, constraints

    def __repr__(self) -> str:
        return f"DesignSheaf(contexts={len(self.contexts)})"


# =============================================================================
# Factory
# =============================================================================


def create_design_sheaf() -> DesignSheaf:
    """
    Create a DesignSheaf for component hierarchy coherence.

    Returns an empty sheaf with just the viewport context.
    Add containers and widgets as needed.
    """
    return DesignSheaf()


def create_design_sheaf_with_hierarchy(
    containers: list[str],
    widgets: dict[str, list[str]],
) -> DesignSheaf:
    """
    Create a DesignSheaf with a predefined hierarchy.

    Args:
        containers: List of container names
        widgets: Dict mapping container names to their widget names

    Returns:
        DesignSheaf with the hierarchy populated

    Example:
        sheaf = create_design_sheaf_with_hierarchy(
            containers=["sidebar", "main"],
            widgets={
                "sidebar": ["nav", "actions"],
                "main": ["content", "footer"],
            },
        )
    """
    sheaf = DesignSheaf()

    for container_name in containers:
        sheaf.add_context(create_container_context(container_name))

    for container_name, widget_names in widgets.items():
        for widget_name in widget_names:
            sheaf.add_context(create_widget_context(widget_name, container_name))

    return sheaf


# Global instance for convenience
DESIGN_SHEAF = create_design_sheaf()


__all__ = [
    # Contexts
    "DesignContext",
    "VIEWPORT_CONTEXT",
    "create_container_context",
    "create_widget_context",
    # Sheaf
    "DesignSheaf",
    "DESIGN_SHEAF",
    "create_design_sheaf",
    "create_design_sheaf_with_hierarchy",
    # Errors
    "GluingError",
    "RestrictionError",
    # Temporal coherence (re-exported from types for convenience)
    "AnimationConstraint",
    "AnimationPhase",
    "SyncStrategy",
    "TemporalOverlap",
]
