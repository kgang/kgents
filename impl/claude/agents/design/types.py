"""
Design Types: Enums and type definitions for the Design Language System.

The three orthogonal dimensions of UI composition:
- Density: How much space is available
- ContentLevel: How much detail to show
- MotionType: What animation to apply

These form a product space: UI = Density × ContentLevel × MotionType

Extended for temporal coherence:
- AnimationPhase: Where in an animation lifecycle a component is
- SyncStrategy: How to synchronize overlapping animations
- AnimationConstraint: Constraint telling React how to coordinate animations
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, TypeVar

# Type variables for generic design operations
D = TypeVar("D", bound="Density")
C = TypeVar("C", bound="ContentLevel")
M = TypeVar("M", bound="MotionType")


class Density(Enum):
    """
    Screen density mode.

    Maps to observer's viewport capacity (aligned with spec/protocols/projection.md):
    - compact: <768px (mobile) - minimal chrome, touch-friendly
    - comfortable: 768-1023px (tablet) - balanced, collapsible
    - spacious: >=1024px (desktop) - full panels, draggable dividers
    """

    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"

    @classmethod
    def from_width(cls, width: int) -> Density:
        """Map viewport width to density mode.

        Breakpoints aligned with spec/protocols/projection.md:
        - compact: <768px (mobile)
        - comfortable: 768-1023px (tablet)
        - spacious: >=1024px (desktop)
        """
        if width < 768:
            return cls.COMPACT
        if width < 1024:
            return cls.COMFORTABLE
        return cls.SPACIOUS


class ContentLevel(Enum):
    """
    Content detail level for progressive disclosure.

    The degradation lattice: icon ⊆ title ⊆ summary ⊆ full
    Each level includes all content from previous levels.
    """

    ICON = "icon"  # <60px - icon only
    TITLE = "title"  # <150px - icon + name
    SUMMARY = "summary"  # <280px - icon + name + phase
    FULL = "full"  # ≥400px - full card content

    @classmethod
    def from_width(cls, width: int) -> ContentLevel:
        """Map container width to content level."""
        if width < 60:
            return cls.ICON
        if width < 150:
            return cls.TITLE
        if width < 280:
            return cls.SUMMARY
        return cls.FULL

    def includes(self, other: ContentLevel) -> bool:
        """Check if this level includes another (lattice ordering)."""
        order = [
            ContentLevel.ICON,
            ContentLevel.TITLE,
            ContentLevel.SUMMARY,
            ContentLevel.FULL,
        ]
        return order.index(self) >= order.index(other)


class MotionType(Enum):
    """
    Animation primitives from the Joy library.

    Motion types compose via chain (sequential) and parallel (simultaneous).
    Identity motion is the no-op that preserves the component unchanged.
    """

    IDENTITY = "identity"  # No animation
    BREATHE = "breathe"  # Gentle pulse
    POP = "pop"  # Scale bounce
    SHAKE = "shake"  # Horizontal vibration
    SHIMMER = "shimmer"  # Highlight sweep
    PAGE_TRANSITION = "page_transition"  # Route change animation


class LayoutType(Enum):
    """
    Layout primitives from the Elastic system.

    These map to React components in components/elastic/.
    """

    SPLIT = "split"  # ElasticSplit - two-pane with collapse
    STACK = "stack"  # ElasticContainer - vertical/horizontal
    DRAWER = "drawer"  # BottomDrawer - mobile slide-up
    FLOAT = "float"  # FloatingActions - FAB cluster


# =============================================================================
# Animation Phase (Temporal Coherence)
# =============================================================================

# Type alias for phase literals
AnimationPhaseName = Literal["idle", "entering", "active", "exiting"]


@dataclass(frozen=True)
class AnimationPhase:
    """
    Where in an animation lifecycle a component is.

    This enables the sheaf to detect temporal overlap between
    sibling components and enforce synchronization strategies.

    Attributes:
        phase: Current lifecycle phase (idle, entering, active, exiting)
        progress: Animation progress from 0.0 to 1.0
        started_at: Timestamp when animation started
        duration: Total animation duration in seconds
    """

    phase: AnimationPhaseName
    progress: float  # 0.0 to 1.0
    started_at: float  # timestamp
    duration: float  # seconds

    def __post_init__(self) -> None:
        """Validate progress is in [0, 1]."""
        if not 0.0 <= self.progress <= 1.0:
            object.__setattr__(self, "progress", max(0.0, min(1.0, self.progress)))

    @property
    def end_time(self) -> float:
        """Calculate when this animation will end."""
        return self.started_at + self.duration

    def overlaps_temporally(self, other: AnimationPhase) -> bool:
        """Check if this animation's time window overlaps another's."""
        end1 = self.end_time
        end2 = other.end_time
        return self.started_at < end2 and other.started_at < end1


# =============================================================================
# Synchronization Strategy
# =============================================================================


class SyncStrategy(Enum):
    """
    How to synchronize overlapping animations.

    When two sibling components animate simultaneously, this determines
    how they coordinate to prevent visual artifacts at boundaries.
    """

    # Both animations use same progress curve
    LOCK_STEP = "lock_step"

    # One waits for other to reach threshold before starting
    STAGGER = "stagger"

    # Both run independently but boundary is interpolated
    INTERPOLATE_BOUNDARY = "interpolate_boundary"

    # One animation is primary, other follows
    LEADER_FOLLOWER = "leader_follower"


# =============================================================================
# Animation Constraint
# =============================================================================


@dataclass(frozen=True)
class AnimationConstraint:
    """
    A constraint telling the React layer how to coordinate animations.

    Generated by DesignSheaf.glue() when temporal overlap is detected
    between sibling components.

    Attributes:
        source: Context name of first animating component
        target: Context name of second animating component
        strategy: How to synchronize the animations
        window: (start_time, end_time) of the overlap window
    """

    source: str
    target: str
    strategy: SyncStrategy
    window: tuple[float, float]  # (start_time, end_time)

    def involves(self, context_name: str) -> bool:
        """Check if this constraint involves a given context."""
        return self.source == context_name or self.target == context_name


@dataclass(frozen=True)
class TemporalOverlap:
    """
    Internal structure representing temporal overlap between contexts.

    Used internally by DesignSheaf to compute AnimationConstraints.
    """

    contexts: tuple[str, str]  # (ctx1.name, ctx2.name)
    window: tuple[float, float]  # (overlap_start, overlap_end)
    sync_strategy: SyncStrategy


# =============================================================================
# Design State (Extended)
# =============================================================================


@dataclass(frozen=True)
class DesignState:
    """
    Complete design state for a UI component.

    This is the position in the DESIGN_POLYNOMIAL state machine.
    Extended with optional animation_phase for temporal coherence.
    """

    density: Density
    content_level: ContentLevel
    motion: MotionType = MotionType.IDENTITY
    should_animate: bool = True
    animation_phase: AnimationPhase | None = None

    def with_density(self, density: Density) -> DesignState:
        """Return new state with updated density."""
        return DesignState(
            density=density,
            content_level=self.content_level,
            motion=self.motion,
            should_animate=self.should_animate,
            animation_phase=self.animation_phase,
        )

    def with_content_level(self, level: ContentLevel) -> DesignState:
        """Return new state with updated content level."""
        return DesignState(
            density=self.density,
            content_level=level,
            motion=self.motion,
            should_animate=self.should_animate,
            animation_phase=self.animation_phase,
        )

    def with_motion(self, motion: MotionType) -> DesignState:
        """Return new state with updated motion."""
        return DesignState(
            density=self.density,
            content_level=self.content_level,
            motion=motion,
            should_animate=self.should_animate,
            animation_phase=self.animation_phase,
        )

    def with_animation_phase(self, phase: AnimationPhase | None) -> DesignState:
        """Return new state with updated animation phase."""
        return DesignState(
            density=self.density,
            content_level=self.content_level,
            motion=self.motion,
            should_animate=self.should_animate,
            animation_phase=phase,
        )


# Density-parameterized constants pattern
# Usage: MY_CONST[density] where density is Density.value string
DensityMap = dict[str, int | float | str]


# Common density-parameterized values
DEFAULT_GAP: DensityMap = {"compact": 8, "comfortable": 12, "spacious": 16}
DEFAULT_PADDING: DensityMap = {"compact": 12, "comfortable": 16, "spacious": 24}
DEFAULT_FONT_SIZE: DensityMap = {"compact": 12, "comfortable": 13, "spacious": 14}


__all__ = [
    # Core types
    "Density",
    "ContentLevel",
    "MotionType",
    "LayoutType",
    "DesignState",
    # Temporal coherence types
    "AnimationPhaseName",
    "AnimationPhase",
    "SyncStrategy",
    "AnimationConstraint",
    "TemporalOverlap",
    # Density-parameterized constants
    "DensityMap",
    "DEFAULT_GAP",
    "DEFAULT_PADDING",
    "DEFAULT_FONT_SIZE",
]
