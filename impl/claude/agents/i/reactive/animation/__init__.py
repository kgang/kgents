"""
Animation Loop: Wave 8 of the reactive substrate.

Frame timing, transitions, and smooth updates for reactive widgets.

Components:
- Easing: Pure mathematical easing functions
- Frame: FrameScheduler for animation coordination
- Tween: Property animation primitive
- Combinators: Sequence and Parallel for composition
- Spring: Physics-based spring dynamics
- Animated: AnimatedWidget base class
- Cymatics: Vibration visualization through wave interference
- Growth: Differential growth for organic forms

Key insight: Animation is time.* context manifesting.
"""

from agents.i.reactive.animation.animated import (
    AnimatedWidget,
    AnimationMixin,
)
from agents.i.reactive.animation.combinators import (
    AnimationCombinator,
    Parallel,
    Sequence,
)
from agents.i.reactive.animation.cymatics import (
    ChladniPattern,
    CymaticsEngine,
    VibrationSource,
    create_dissonant_sources,
    create_harmonic_sources,
    pattern_stability,
)
from agents.i.reactive.animation.easing import (
    Easing,
    EasingFn,
    ease_bounce,
    ease_elastic,
    ease_in,
    ease_in_out,
    ease_linear,
    ease_out,
)
from agents.i.reactive.animation.frame import (
    FrameCallback,
    FrameScheduler,
    FrameSchedulerConfig,
)
from agents.i.reactive.animation.growth import (
    GrowthEdge,
    GrowthEngine,
    GrowthNode,
    GrowthRules,
)
from agents.i.reactive.animation.spring import (
    Spring,
    SpringConfig,
    SpringState,
)
from agents.i.reactive.animation.tween import (
    TransitionStatus,
    Tween,
    TweenConfig,
    TweenState,
)

__all__ = [
    # Easing
    "Easing",
    "EasingFn",
    "ease_linear",
    "ease_in",
    "ease_out",
    "ease_in_out",
    "ease_bounce",
    "ease_elastic",
    # Frame
    "FrameScheduler",
    "FrameSchedulerConfig",
    "FrameCallback",
    # Tween
    "Tween",
    "TweenConfig",
    "TweenState",
    "TransitionStatus",
    # Combinators
    "AnimationCombinator",
    "Sequence",
    "Parallel",
    # Spring
    "Spring",
    "SpringConfig",
    "SpringState",
    # Animated
    "AnimatedWidget",
    "AnimationMixin",
    # Cymatics
    "CymaticsEngine",
    "VibrationSource",
    "ChladniPattern",
    "create_harmonic_sources",
    "create_dissonant_sources",
    "pattern_stability",
    # Growth
    "GrowthEngine",
    "GrowthNode",
    "GrowthEdge",
    "GrowthRules",
]
