"""
Design: Grammar of UI Composition.

This module provides the categorical foundation for kgents UI design:

1. **Types** (types.py):
   - Density: compact/comfortable/spacious
   - ContentLevel: icon/title/summary/full
   - MotionType: identity/breathe/pop/shake/shimmer
   - DesignState: complete state for a UI component

2. **Operads** (operad.py):
   - LAYOUT_OPERAD: split, stack, drawer, float
   - CONTENT_OPERAD: degrade, compose
   - MOTION_OPERAD: identity, breathe, pop, shake, shimmer, chain, parallel
   - DESIGN_OPERAD: unified grammar with naturality law

3. **Polynomial** (polynomial.py):
   - DESIGN_POLYNOMIAL: state machine for design state
   - Inputs: ViewportResize, ContainerResize, AnimationToggle, MotionRequest
   - Outputs: StateChanged, NoChange

4. **Sheaf** (sheaf.py) - NOT YET IMPLEMENTED:
   - DESIGN_SHEAF: Global coherence from local views
   - DesignContext: Viewport/Container/Widget hierarchy
   - Gluing: Combine compatible local states

The core insight: UI = Layout[D] ∘ Content[D] ∘ Motion[M]

These three dimensions are orthogonal and compose naturally.

IMPLEMENTATION STATUS:
  ✅ Layer 2: DESIGN_POLYNOMIAL (complete)
  ✅ Layer 3: DESIGN_OPERAD (complete)
  🚧 Layer 1: DESIGN_SHEAF (stub - raises NotImplementedError)
  🚧 Layer 7: React Projection (not started)
"""

# Types
# Generation (operad → JSX functor)
from .generate import (
    LAYOUT_COMPONENT_MAP,
    MOTION_COMPONENT_MAP,
    ComponentSpec,
    generate_component,
    generate_drawer,
    generate_split,
    generate_stack,
    with_motion,
)

# Operads
from .operad import (
    CONTENT_OPERAD,
    DESIGN_OPERAD,
    LAYOUT_OPERAD,
    MOTION_OPERAD,
    create_content_operad,
    create_design_operad,
    create_layout_operad,
    create_motion_operad,
)

# Polynomial
from .polynomial import (
    DESIGN_POLYNOMIAL,
    AnimationToggle,
    ContainerResize,
    DesignInput,
    DesignOutput,
    MotionRequest,
    NoChange,
    StateChanged,
    ViewportResize,
    create_design_polynomial,
    design_directions,
    design_transition,
)

# Sheaf (complete implementation)
from .sheaf import (
    DESIGN_SHEAF,
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
from .types import (
    DEFAULT_FONT_SIZE,
    DEFAULT_GAP,
    DEFAULT_PADDING,
    AnimationConstraint,
    AnimationPhase,
    AnimationPhaseName,
    ContentLevel,
    Density,
    DensityMap,
    DesignState,
    LayoutType,
    MotionType,
    SyncStrategy,
    TemporalOverlap,
)

__all__ = [
    # Core Types
    "Density",
    "ContentLevel",
    "MotionType",
    "LayoutType",
    "DesignState",
    "DensityMap",
    "DEFAULT_GAP",
    "DEFAULT_PADDING",
    "DEFAULT_FONT_SIZE",
    # Temporal Coherence Types
    "AnimationPhaseName",
    "AnimationPhase",
    "SyncStrategy",
    "AnimationConstraint",
    "TemporalOverlap",
    # Operads
    "LAYOUT_OPERAD",
    "CONTENT_OPERAD",
    "MOTION_OPERAD",
    "DESIGN_OPERAD",
    "create_layout_operad",
    "create_content_operad",
    "create_motion_operad",
    "create_design_operad",
    # Polynomial
    "DESIGN_POLYNOMIAL",
    "ViewportResize",
    "ContainerResize",
    "AnimationToggle",
    "MotionRequest",
    "DesignInput",
    "StateChanged",
    "NoChange",
    "DesignOutput",
    "design_directions",
    "design_transition",
    "create_design_polynomial",
    # Sheaf (complete implementation)
    "DESIGN_SHEAF",
    "DesignContext",
    "DesignSheaf",
    "VIEWPORT_CONTEXT",
    "create_design_sheaf",
    "create_design_sheaf_with_hierarchy",
    "create_container_context",
    "create_widget_context",
    "GluingError",
    "RestrictionError",
    # Generation (operad → JSX functor)
    "ComponentSpec",
    "generate_component",
    "generate_split",
    "generate_stack",
    "generate_drawer",
    "with_motion",
    "LAYOUT_COMPONENT_MAP",
    "MOTION_COMPONENT_MAP",
]
