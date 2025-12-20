"""
Story Arc Detection for The Muse.

Uses Freytag's Pyramid to model development work as narrative:
- EXPOSITION: Understanding the problem
- RISING_ACTION: Building complexity
- CLIMAX: The breakthrough (or wall)
- FALLING_ACTION: Cleanup, refinement
- DENOUEMENT: Reflection, documentation

The Insight:
    "Every coding session tells a story. The Muse reads the arc."

See: plans/witness-muse-implementation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.witness.crystal import ExperienceCrystal, MoodVector


# =============================================================================
# Arc Phase (Freytag's Pyramid)
# =============================================================================


class ArcPhase(Enum):
    """
    Freytag's Pyramid adapted for development work.

    Each phase has characteristic patterns:
    - EXPOSITION: High reading, low writing, neutral mood
    - RISING_ACTION: Increasing tempo, mixed success, growing complexity
    - CLIMAX: High activity, peak tension, breakthrough or wall
    - FALLING_ACTION: Decreasing complexity, cleanup patterns
    - DENOUEMENT: Low tempo, documentation, reflection
    """

    EXPOSITION = auto()  # Understanding the problem
    RISING_ACTION = auto()  # Building complexity, experiments
    CLIMAX = auto()  # The turning point
    FALLING_ACTION = auto()  # Cleanup, refinement
    DENOUEMENT = auto()  # Reflection, next steps

    @property
    def is_rising(self) -> bool:
        """Is tension generally increasing?"""
        return self in (ArcPhase.EXPOSITION, ArcPhase.RISING_ACTION)

    @property
    def is_falling(self) -> bool:
        """Is tension generally decreasing?"""
        return self in (ArcPhase.FALLING_ACTION, ArcPhase.DENOUEMENT)

    @property
    def is_peak(self) -> bool:
        """Is this the peak?"""
        return self == ArcPhase.CLIMAX

    @property
    def next_phase(self) -> ArcPhase:
        """Natural progression to next phase."""
        order = [
            ArcPhase.EXPOSITION,
            ArcPhase.RISING_ACTION,
            ArcPhase.CLIMAX,
            ArcPhase.FALLING_ACTION,
            ArcPhase.DENOUEMENT,
        ]
        idx = order.index(self)
        return order[min(idx + 1, len(order) - 1)]

    @property
    def emoji(self) -> str:
        """Visual indicator."""
        return {
            ArcPhase.EXPOSITION: "📖",  # Reading
            ArcPhase.RISING_ACTION: "🔺",  # Climbing
            ArcPhase.CLIMAX: "⚡",  # Peak moment
            ArcPhase.FALLING_ACTION: "🔻",  # Descending
            ArcPhase.DENOUEMENT: "🌅",  # Sunset/conclusion
        }[self]


# =============================================================================
# Story Arc
# =============================================================================


@dataclass
class StoryArc:
    """
    Current story arc state.

    Tracks phase, confidence, and tension level.
    """

    phase: ArcPhase = ArcPhase.EXPOSITION
    confidence: float = 0.5  # How confident in current phase [0, 1]
    tension: float = 0.0  # Current tension level [0, 1]
    momentum: float = 0.0  # Rate of change (-1 to 1)
    entered_phase_at: datetime = field(default_factory=datetime.now)

    def advance(self) -> StoryArc:
        """Advance to next phase."""
        return StoryArc(
            phase=self.phase.next_phase,
            confidence=0.6,  # Reset confidence for new phase
            tension=self.tension,
            momentum=self.momentum,
            entered_phase_at=datetime.now(),
        )

    def regress(self) -> StoryArc:
        """Return to previous phase (rare—usually indicates false climax)."""
        order = [
            ArcPhase.EXPOSITION,
            ArcPhase.RISING_ACTION,
            ArcPhase.CLIMAX,
            ArcPhase.FALLING_ACTION,
            ArcPhase.DENOUEMENT,
        ]
        idx = order.index(self.phase)
        prev_phase = order[max(0, idx - 1)]
        return StoryArc(
            phase=prev_phase,
            confidence=0.4,  # Lower confidence after regression
            tension=self.tension,
            momentum=self.momentum,
            entered_phase_at=datetime.now(),
        )

    def update_tension(self, delta: float) -> StoryArc:
        """Update tension level."""
        new_tension = max(0.0, min(1.0, self.tension + delta))
        return StoryArc(
            phase=self.phase,
            confidence=self.confidence,
            tension=new_tension,
            momentum=delta,
            entered_phase_at=self.entered_phase_at,
        )

    @property
    def phase_duration_seconds(self) -> float:
        """How long in current phase."""
        return (datetime.now() - self.entered_phase_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Serialize for storage."""
        return {
            "phase": self.phase.name,
            "confidence": self.confidence,
            "tension": self.tension,
            "momentum": self.momentum,
            "entered_phase_at": self.entered_phase_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryArc:
        """Deserialize from storage."""
        return cls(
            phase=ArcPhase[data["phase"]],
            confidence=data.get("confidence", 0.5),
            tension=data.get("tension", 0.0),
            momentum=data.get("momentum", 0.0),
            entered_phase_at=datetime.fromisoformat(data["entered_phase_at"]),
        )


# =============================================================================
# Arc Detector
# =============================================================================


class StoryArcDetector:
    """
    Detects story arc phase from Experience Crystals.

    Uses mood vectors, activity patterns, and temporal signals
    to infer narrative structure.
    """

    def __init__(self) -> None:
        self.current_arc = StoryArc()
        self._crystal_buffer: list[Any] = []  # CrystalObserved from polynomial
        self._max_buffer = 10

    def observe(self, crystal: "ExperienceCrystal") -> StoryArc:
        """
        Observe a crystal and update arc detection.

        Returns updated arc with potential phase shift.
        """
        # Add to buffer
        from services.muse.polynomial import CrystalObserved

        observation = CrystalObserved(
            crystal_id=crystal.crystal_id,
            session_id=crystal.session_id,
            mood_brightness=crystal.mood.brightness,
            topics=tuple(crystal.topics),
            complexity=crystal.complexity,
        )
        self._crystal_buffer.append(observation)
        if len(self._crystal_buffer) > self._max_buffer:
            self._crystal_buffer = self._crystal_buffer[-self._max_buffer :]

        # Analyze buffer for phase detection
        self.current_arc = self._detect_phase_shift()
        return self.current_arc

    def _detect_phase_shift(self) -> StoryArc:
        """
        Analyze crystal buffer to detect phase shifts.

        Heuristics:
        - EXPOSITION → RISING_ACTION: Activity increases, complexity grows
        - RISING_ACTION → CLIMAX: Tension spikes, mood polarizes
        - CLIMAX → FALLING_ACTION: Complexity drops, mood brightens
        - FALLING_ACTION → DENOUEMENT: Activity slows, commits appear
        """
        if len(self._crystal_buffer) < 2:
            return self.current_arc

        recent = self._crystal_buffer[-3:]  # Last 3 crystals

        # Calculate aggregate signals
        avg_brightness = sum(c.mood_brightness for c in recent) / len(recent)
        avg_complexity = sum(c.complexity for c in recent) / len(recent)

        # Brightness trend
        brightness_trend = recent[-1].mood_brightness - recent[0].mood_brightness

        # Complexity trend
        complexity_trend = recent[-1].complexity - recent[0].complexity

        # Phase detection based on current phase
        current = self.current_arc

        if current.phase == ArcPhase.EXPOSITION:
            # Look for rising action signals: increasing complexity
            if complexity_trend > 0.1 and len(recent) >= 3:
                return current.advance()

        elif current.phase == ArcPhase.RISING_ACTION:
            # Look for climax signals: high complexity + polarized mood
            if avg_complexity > 0.7 or (avg_brightness < 0.3 and len(recent) >= 3):
                return current.advance()

        elif current.phase == ArcPhase.CLIMAX:
            # Look for falling action: complexity dropping, mood improving
            if complexity_trend < -0.1 and brightness_trend > 0.1:
                return current.advance()
            # Or regression on false climax
            if brightness_trend < -0.2:
                return current.regress()

        elif current.phase == ArcPhase.FALLING_ACTION:
            # Look for denouement: low activity, commits
            if avg_complexity < 0.3:
                return current.advance()

        # Update tension based on mood
        tension_delta = (1.0 - avg_brightness) * 0.1 - 0.05  # Neutral at 0.5 brightness
        return current.update_tension(tension_delta)

    def reset(self) -> None:
        """Reset arc detection for new session."""
        self.current_arc = StoryArc()
        self._crystal_buffer = []


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ArcPhase",
    "StoryArc",
    "StoryArcDetector",
]
