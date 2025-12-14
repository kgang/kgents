"""
Agent Posture Indicators - Visual encoding of polynomial agent state.

Posture is the "body language" of an agent, conveying its internal state
at a glance. Each posture maps to a symbol and color that communicates:
- Current mode (GROUNDING, DELIBERATING, JUDGING, COMPLETE)
- Confidence level (affects animation intensity)
- Resource state (exhausted, normal, abundant)

Visual vocabulary inspired by geometric primitives:
- Triangles for dynamic states (▲ ▽ △ ▼)
- Circles for stable states (● ○ ◉ ◎)
- Diamonds for uncertain states (◇ ◆ ⬖ ⬗)

Usage:
    posture = get_posture_for_mode("DELIBERATING", confidence=0.8)
    symbol = posture.symbol
    color = posture.color
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class PostureMode(Enum):
    """Agent operational modes."""

    GROUNDING = auto()  # Gathering context, orienting
    DELIBERATING = auto()  # Thinking, considering options
    JUDGING = auto()  # Making decisions, evaluating
    COMPLETE = auto()  # Finished, resolved
    EXHAUSTED = auto()  # Resource depleted
    CONFUSED = auto()  # Uncertain, stuck
    YIELDING = auto()  # Waiting for approval
    IDLE = auto()  # Inactive, waiting


# Symbol vocabulary for postures
POSTURE_SYMBOLS = {
    PostureMode.GROUNDING: "▲",  # Upward triangle: stable, gathering
    PostureMode.DELIBERATING: "△",  # Open triangle: alert, thinking
    PostureMode.JUDGING: "▽",  # Inverted triangle: tense, decisive
    PostureMode.COMPLETE: "●",  # Filled circle: resolved, done
    PostureMode.EXHAUSTED: "○",  # Empty circle: depleted
    PostureMode.CONFUSED: "◇",  # Diamond: uncertain
    PostureMode.YIELDING: "◐",  # Half circle: waiting
    PostureMode.IDLE: "◌",  # Dotted circle: inactive
}

# Alternative symbols for animation frames
POSTURE_ANIMATION_FRAMES = {
    PostureMode.GROUNDING: ["▲", "△", "▲", "▴"],
    PostureMode.DELIBERATING: ["△", "▷", "▽", "◁"],
    PostureMode.JUDGING: ["▽", "▼", "▽", "▾"],
    PostureMode.COMPLETE: ["●", "◉", "●", "◎"],
    PostureMode.EXHAUSTED: ["○", "◌", "○", "◌"],
    PostureMode.CONFUSED: ["◇", "◈", "◆", "◈"],
    PostureMode.YIELDING: ["◐", "◑", "◒", "◓"],
    PostureMode.IDLE: ["◌", "○", "◌", "·"],
}

# Colors for postures (hex)
POSTURE_COLORS = {
    PostureMode.GROUNDING: "#7bc275",  # Green: stable
    PostureMode.DELIBERATING: "#8ac4e8",  # Blue: thinking
    PostureMode.JUDGING: "#f5d08a",  # Gold: decisive
    PostureMode.COMPLETE: "#7bc275",  # Green: success
    PostureMode.EXHAUSTED: "#e88a8a",  # Red: depleted
    PostureMode.CONFUSED: "#b3a89a",  # Gray: uncertain
    PostureMode.YIELDING: "#e6a352",  # Orange: waiting
    PostureMode.IDLE: "#6a6560",  # Dim: inactive
}

# Tooltip descriptions
POSTURE_DESCRIPTIONS = {
    PostureMode.GROUNDING: "Gathering context and orienting to the task",
    PostureMode.DELIBERATING: "Considering options and evaluating possibilities",
    PostureMode.JUDGING: "Making decisions and committing to action",
    PostureMode.COMPLETE: "Task completed successfully",
    PostureMode.EXHAUSTED: "Resources depleted, needs recovery",
    PostureMode.CONFUSED: "Uncertain about next steps",
    PostureMode.YIELDING: "Waiting for human approval",
    PostureMode.IDLE: "Inactive, awaiting input",
}


@dataclass
class Posture:
    """
    Visual representation of agent state.

    Combines symbol, color, and animation data for rendering.
    """

    mode: PostureMode
    symbol: str
    color: str
    description: str
    confidence: float = 1.0
    animation_frames: list[str] | None = None
    animation_speed: float = 1.0  # Frames per second

    @classmethod
    def from_mode(
        cls,
        mode: PostureMode | str,
        confidence: float = 1.0,
        animated: bool = True,
    ) -> Posture:
        """
        Create a posture from a mode.

        Args:
            mode: PostureMode or string mode name
            confidence: Confidence level (affects animation)
            animated: Whether to include animation frames

        Returns:
            Configured Posture instance
        """
        # Convert string to enum if needed
        if isinstance(mode, str):
            try:
                mode = PostureMode[mode.upper()]
            except KeyError:
                mode = PostureMode.IDLE

        return cls(
            mode=mode,
            symbol=POSTURE_SYMBOLS.get(mode, "○"),
            color=POSTURE_COLORS.get(mode, "#b3a89a"),
            description=POSTURE_DESCRIPTIONS.get(mode, "Unknown state"),
            confidence=confidence,
            animation_frames=POSTURE_ANIMATION_FRAMES.get(mode) if animated else None,
            animation_speed=0.5 + confidence,  # Higher confidence = faster animation
        )

    def get_frame(self, frame_index: int) -> str:
        """
        Get animation frame at index.

        Args:
            frame_index: 0-based frame index

        Returns:
            Symbol for that frame
        """
        if not self.animation_frames:
            return self.symbol

        return self.animation_frames[frame_index % len(self.animation_frames)]

    def with_confidence(self, confidence: float) -> Posture:
        """Create a copy with updated confidence."""
        return Posture(
            mode=self.mode,
            symbol=self.symbol,
            color=self.color,
            description=self.description,
            confidence=confidence,
            animation_frames=self.animation_frames,
            animation_speed=0.5 + confidence,
        )


class PostureMapper:
    """
    Maps polynomial agent states to postures.

    Handles the translation between internal agent state
    representations and visual posture indicators.
    """

    # Polynomial mode to posture mode mapping
    MODE_MAP = {
        "GROUNDING": PostureMode.GROUNDING,
        "GROUND": PostureMode.GROUNDING,
        "DELIBERATING": PostureMode.DELIBERATING,
        "DELIBERATE": PostureMode.DELIBERATING,
        "THINK": PostureMode.DELIBERATING,
        "JUDGING": PostureMode.JUDGING,
        "JUDGE": PostureMode.JUDGING,
        "DECIDE": PostureMode.JUDGING,
        "COMPLETE": PostureMode.COMPLETE,
        "DONE": PostureMode.COMPLETE,
        "FINISHED": PostureMode.COMPLETE,
        "EXHAUSTED": PostureMode.EXHAUSTED,
        "DEPLETED": PostureMode.EXHAUSTED,
        "CONFUSED": PostureMode.CONFUSED,
        "STUCK": PostureMode.CONFUSED,
        "UNCERTAIN": PostureMode.CONFUSED,
        "YIELDING": PostureMode.YIELDING,
        "YIELD": PostureMode.YIELDING,
        "WAITING": PostureMode.YIELDING,
        "IDLE": PostureMode.IDLE,
        "DORMANT": PostureMode.IDLE,
    }

    # Phase to posture mode mapping (for simpler phase states)
    PHASE_MAP = {
        "DORMANT": PostureMode.IDLE,
        "WAKING": PostureMode.GROUNDING,
        "ACTIVE": PostureMode.DELIBERATING,
        "WANING": PostureMode.EXHAUSTED,
        "VOID": PostureMode.CONFUSED,
    }

    def __init__(self, confidence_threshold: float = 0.3) -> None:
        """
        Initialize the mapper.

        Args:
            confidence_threshold: Below this, show EXHAUSTED posture
        """
        self.confidence_threshold = confidence_threshold

    def from_polynomial_state(
        self,
        current_mode: str,
        confidence: float = 1.0,
        valid_inputs: list[str] | None = None,
    ) -> Posture:
        """
        Map polynomial agent state to posture.

        Args:
            current_mode: Current polynomial mode name
            confidence: Agent confidence level
            valid_inputs: List of valid next inputs

        Returns:
            Appropriate Posture for the state
        """
        # Check for exhaustion
        if confidence < self.confidence_threshold:
            return Posture.from_mode(PostureMode.EXHAUSTED, confidence)

        # Check for yield state
        if valid_inputs and "APPROVE" in valid_inputs:
            return Posture.from_mode(PostureMode.YIELDING, confidence)

        # Map mode
        posture_mode = self.MODE_MAP.get(
            current_mode.upper(),
            PostureMode.IDLE,
        )

        return Posture.from_mode(posture_mode, confidence)

    def from_phase(self, phase: str, activity: float = 0.5) -> Posture:
        """
        Map simple phase to posture.

        Args:
            phase: Phase name (DORMANT, WAKING, ACTIVE, WANING, VOID)
            activity: Activity level (used as proxy for confidence)

        Returns:
            Appropriate Posture
        """
        posture_mode = self.PHASE_MAP.get(
            phase.upper(),
            PostureMode.IDLE,
        )

        return Posture.from_mode(posture_mode, activity)


def get_posture_for_mode(
    mode: str,
    confidence: float = 1.0,
    animated: bool = True,
) -> Posture:
    """
    Convenience function to get a posture for a mode.

    Args:
        mode: Mode name (polynomial mode or phase)
        confidence: Confidence level
        animated: Include animation frames

    Returns:
        Configured Posture
    """
    mapper = PostureMapper()

    # Try polynomial mode first
    if mode.upper() in PostureMapper.MODE_MAP:
        return mapper.from_polynomial_state(mode, confidence)

    # Try phase
    if mode.upper() in PostureMapper.PHASE_MAP:
        return mapper.from_phase(mode, confidence)

    # Default
    return Posture.from_mode(PostureMode.IDLE, confidence, animated)


def render_posture_with_tooltip(posture: Posture, show_tooltip: bool = False) -> str:
    """
    Render posture symbol with optional tooltip.

    Args:
        posture: Posture to render
        show_tooltip: Include tooltip text

    Returns:
        Rich-formatted string
    """
    if show_tooltip:
        return f"[{posture.color}]{posture.symbol}[/] {posture.description}"
    return f"[{posture.color}]{posture.symbol}[/]"


__all__ = [
    "Posture",
    "PostureMode",
    "PostureMapper",
    "POSTURE_SYMBOLS",
    "POSTURE_COLORS",
    "POSTURE_DESCRIPTIONS",
    "get_posture_for_mode",
    "render_posture_with_tooltip",
]
