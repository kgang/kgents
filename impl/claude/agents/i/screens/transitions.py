"""Gentle Eye transition system - choreography of change without violence.

Philosophy:
    "Guide the eye where it needs to go, sans screen violence."

    - Anchor points stay stable during transitions
    - No jarring flashes or sudden appearances
    - Stagger updates to avoid overwhelming the eye
    - Use crossfade as default (perceptible but not slow)

Transitions encode semantic meaning:
    - Slide left: drilling down (more detail)
    - Slide right: drilling up (less detail)
    - Crossfade: peer navigation (same LOD)
    - Morph: element expansion (focus shift)
"""

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class TransitionStyle(Enum):
    """How screens transition - the choreography of change."""

    CROSSFADE = "crossfade"  # Old fades out as new fades in (default)
    SLIDE_LEFT = "slide_left"  # Drill down (more detail)
    SLIDE_RIGHT = "slide_right"  # Drill up (less detail)
    MORPH = "morph"  # Element expands into screen


@dataclass(frozen=True)
class ScreenTransition:
    """Choreographed screen transition specification.

    A transition is not just animation - it's semantic communication
    about the relationship between screens.

    Attributes:
        style: The choreography pattern to use
        duration_ms: How long the transition takes (200ms default)
        anchor_element: Element that stays fixed during transition
        stagger_ms: Delay between element animations (50ms default)
    """

    style: TransitionStyle = TransitionStyle.CROSSFADE
    duration_ms: int = 200
    anchor_element: str | None = None  # Element that stays fixed
    stagger_ms: int = 50  # Delay between element animations

    @property
    def duration_seconds(self) -> float:
        """Duration in seconds for timing calculations."""
        return self.duration_ms / 1000

    def __post_init__(self) -> None:
        """Validate transition parameters."""
        if self.duration_ms < 0:
            raise ValueError(f"Duration must be non-negative: {self.duration_ms}")
        if self.stagger_ms < 0:
            raise ValueError(f"Stagger must be non-negative: {self.stagger_ms}")
        if self.duration_ms > 1000:
            # Gentle warning - transitions over 1s feel sluggish
            pass

    def with_anchor(self, element_id: str) -> "ScreenTransition":
        """Create new transition with specified anchor element."""
        return ScreenTransition(
            style=self.style,
            duration_ms=self.duration_ms,
            anchor_element=element_id,
            stagger_ms=self.stagger_ms,
        )

    def with_duration(self, ms: int) -> "ScreenTransition":
        """Create new transition with different duration."""
        return ScreenTransition(
            style=self.style,
            duration_ms=ms,
            anchor_element=self.anchor_element,
            stagger_ms=self.stagger_ms,
        )


class GentleNavigator:
    """Navigate between screens without violence.

    The Gentle Eye philosophy:
        - Anchor points stay stable during transitions
        - No jarring flashes or sudden appearances
        - Stagger updates to avoid overwhelming the eye
        - Use crossfade as default (perceptible but not slow)

    Semantic transitions:
        - LOD down (0→1, 1→2): slide left (drilling deeper)
        - LOD up (2→1, 1→0): slide right (zooming out)
        - Peer (same LOD): crossfade (lateral movement)
    """

    # Default transitions based on navigation direction
    LOD_DOWN_TRANSITION: ClassVar[ScreenTransition] = ScreenTransition(
        style=TransitionStyle.SLIDE_LEFT,
        duration_ms=200,
    )
    LOD_UP_TRANSITION: ClassVar[ScreenTransition] = ScreenTransition(
        style=TransitionStyle.SLIDE_RIGHT,
        duration_ms=200,
    )
    PEER_TRANSITION: ClassVar[ScreenTransition] = ScreenTransition(
        style=TransitionStyle.CROSSFADE,
        duration_ms=150,
    )

    # Special transitions for specific contexts
    MORPH_TRANSITION: ClassVar[ScreenTransition] = ScreenTransition(
        style=TransitionStyle.MORPH,
        duration_ms=250,
    )

    def get_transition_for_lod_change(
        self,
        old_lod: int,
        new_lod: int,
    ) -> ScreenTransition:
        """Get appropriate transition for LOD change.

        Args:
            old_lod: Previous level of detail (0=strategy, 1=tactical, 2=forensic)
            new_lod: New level of detail

        Returns:
            Appropriate transition encoding the semantic relationship
        """
        if new_lod > old_lod:
            # Drilling down - more detail
            return self.LOD_DOWN_TRANSITION
        elif new_lod < old_lod:
            # Zooming out - less detail
            return self.LOD_UP_TRANSITION
        # Same level - peer navigation
        return self.PEER_TRANSITION

    def get_transition_for_screens(
        self,
        old_screen: str,
        new_screen: str,
    ) -> ScreenTransition:
        """Get transition based on screen names and their relationship.

        This is a heuristic-based approach for when LOD isn't explicit.

        Args:
            old_screen: Previous screen identifier
            new_screen: New screen identifier

        Returns:
            Appropriate transition
        """
        # LOD mapping (heuristic)
        lod_map = {
            "cockpit": 0,  # Strategy
            "observatory": 0,  # Strategy
            "flux": 1,  # Tactical
            "mri": 1,  # Tactical
            "forge": 1,  # Tactical
            "terrarium": 1,  # Tactical
            "debugger": 2,  # Forensic
        }

        old_lod = lod_map.get(old_screen.lower(), 1)
        new_lod = lod_map.get(new_screen.lower(), 1)

        return self.get_transition_for_lod_change(old_lod, new_lod)

    def get_instant_transition(self) -> ScreenTransition:
        """Get instant transition (no animation) for urgent updates."""
        return ScreenTransition(
            style=TransitionStyle.CROSSFADE,
            duration_ms=0,
        )
