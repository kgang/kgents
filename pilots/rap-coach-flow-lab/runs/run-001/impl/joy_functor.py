"""
RAP_COACH_JOY: Joy Functor Calibrated for Courage Preservation.

This module defines the Joy functor for the rap-coach pilot,
validating the Joy Integration theory from 04-joy-integration.md.

The Core Insight:
    "The voice is the proof. The session is the trace. Courage leaves marks."

Joy Calibration for Rap Coach:
    WARMTH:   0.9 (primary - the kind coach)
    SURPRISE: 0.3 (secondary - unexpected voice breakthroughs)
    FLOW:     0.7 (tertiary - creative momentum)

Philosophy:
    "This pilot celebrates the rough voice, not the polished one.
    The coach is a witness, never a judge."

See: plans/enlightened-synthesis/04-joy-integration.md
See: pilots/rap-coach-flow-lab/PROTO_SPEC.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

# Import from kgents joy infrastructure
from services.witness.joy import (
    JoyFunctor,
    JoyMode,
    JoyObservation,
    UniversalDelightPrimitive,
    warmth_response,
)

if TYPE_CHECKING:
    from typing import TypeVar
    Observer = TypeVar("Observer")

# =============================================================================
# RAP_COACH_JOY Functor Definition
# =============================================================================

RAP_COACH_JOY = JoyFunctor({
    JoyMode.WARMTH: 0.9,    # Primary: The kind coach
    JoyMode.FLOW: 0.7,      # Secondary: Creative momentum
    JoyMode.SURPRISE: 0.3,  # Tertiary: Unexpected breakthroughs
})
"""
Rap Coach Joy Calibration.

Primary Joy: WARMTH (0.9)
    "The coach believes in me, I believe in myself."
    The coach is warm, supportive, never judgmental.
    Even "misses" are acknowledged with kindness.

Secondary Joy: FLOW (0.7)
    "The loop is tight."
    Practice should feel fluid. Witnessing cannot add drag.
    The flow state is sacred.

Tertiary Joy: SURPRISE (0.3)
    "Unexpected voice breakthroughs."
    When the artist discovers something new in their voice,
    that moment of surprise is joy.

Galois Target: L < 0.20 (flow state with courage preserved)

Failure Mode (Judge Emergence):
    The coach feels evaluative - the artist hesitates before
    taking risks, anticipates criticism, or performs FOR the
    system instead of for themselves.
"""


# =============================================================================
# Courage-Aware Joy Observation
# =============================================================================


@dataclass
class CourageAwareJoyObservation:
    """
    Joy observation that accounts for courage preservation (L4).

    The L4 Courage Preservation Law states:
    "High-risk takes are protected from negative weighting by default.
    Courage is rewarded, not punished."

    This means:
    - High-risk takes should NEVER reduce joy
    - Even "failed" courageous takes get warmth
    - The courage itself is the success, not the outcome
    """

    base_observation: JoyObservation
    is_courageous: bool
    courage_boost: float = 0.0  # Additional joy for courage

    @classmethod
    def from_take(
        cls,
        observer: str,
        risk_level: str,
        warmth: float,
        surprise: float,
        flow: float,
        trigger: str,
    ) -> "CourageAwareJoyObservation":
        """
        Create courage-aware joy observation from a take.

        Args:
            observer: Who is observing (typically the artist)
            risk_level: "low", "medium", "high"
            warmth: Raw warmth signal [0, 1]
            surprise: Raw surprise signal [0, 1]
            flow: Raw flow signal [0, 1]
            trigger: What caused this observation

        Returns:
            CourageAwareJoyObservation with courage protection applied
        """
        # Get base observation from RAP_COACH_JOY
        base = RAP_COACH_JOY.observe(
            observer=observer,
            warmth=warmth,
            surprise=surprise,
            flow=flow,
            trigger=trigger,
        )

        # Apply L4 Courage Preservation
        is_courageous = risk_level == "high"
        courage_boost = 0.0

        if is_courageous:
            # High-risk takes get a courage boost
            # This ensures courage is NEVER punished
            courage_boost = 0.15

            # If base intensity is low due to a "miss", boost it
            if base.intensity < 0.5:
                # Create new observation with boosted intensity
                boosted_intensity = min(1.0, base.intensity + courage_boost)
                base = JoyObservation(
                    mode=JoyMode.WARMTH,  # Courage is met with warmth
                    intensity=boosted_intensity,
                    observer=base.observer,
                    trigger=f"{base.trigger} (courage preserved)",
                )

        return cls(
            base_observation=base,
            is_courageous=is_courageous,
            courage_boost=courage_boost,
        )

    @property
    def effective_intensity(self) -> float:
        """
        Get effective intensity with courage preservation.

        For courageous takes, intensity is never below 0.5.
        """
        if self.is_courageous:
            return max(0.5, self.base_observation.intensity)
        return self.base_observation.intensity

    @property
    def mode(self) -> JoyMode:
        """Get the dominant joy mode."""
        return self.base_observation.mode

    def warmth_response(self) -> str:
        """
        Generate warmth-calibrated response.

        For courageous takes, always acknowledge the courage.
        """
        from services.witness.joy import warmth_response as base_warmth

        response = base_warmth(self.base_observation)

        if self.is_courageous:
            # Add courage acknowledgment
            courage_phrases = [
                " That took guts.",
                " I see you taking risks.",
                " The courage is the win.",
                " Bold move.",
            ]
            import random
            response += random.choice(courage_phrases)

        return response


# =============================================================================
# Rap Coach Warmth Templates
# =============================================================================

RAP_COACH_WARMTH_TEMPLATES = {
    # High warmth responses (intensity > 0.7)
    "high": [
        "That was real. I felt it.",
        "You were in your zone.",
        "That's your voice coming through.",
        "Something clicked there.",
        "I heard you finding something new.",
    ],
    # Medium warmth responses (0.4 < intensity <= 0.7)
    "medium": [
        "Good momentum.",
        "You're building something.",
        "Keep that energy.",
        "I see what you're going for.",
        "That's interesting terrain.",
    ],
    # Low intensity but STILL warm (intensity <= 0.4)
    # NOTE: Never punitive, never cold
    "low": [
        "Noted. Let's keep moving.",
        "Take your time.",
        "You're in the process.",
        "Every take teaches something.",
        "The reps are adding up.",
    ],
    # Courage-specific (for high-risk takes)
    "courage": [
        "Courage is the point. Everything else is gravy.",
        "That risk was the win.",
        "I see you pushing edges.",
        "Bold territory. Respect.",
        "That's how you find new voice.",
    ],
}


def rap_coach_warmth_response(
    observation: CourageAwareJoyObservation,
) -> str:
    """
    Generate rap-coach-specific warmth response.

    This follows the PROTO_SPEC personality:
    "This pilot celebrates the rough voice, not the polished one.
    The coach is a witness, never a judge."
    """
    import random

    intensity = observation.effective_intensity

    if observation.is_courageous:
        templates = RAP_COACH_WARMTH_TEMPLATES["courage"]
    elif intensity > 0.7:
        templates = RAP_COACH_WARMTH_TEMPLATES["high"]
    elif intensity > 0.4:
        templates = RAP_COACH_WARMTH_TEMPLATES["medium"]
    else:
        templates = RAP_COACH_WARMTH_TEMPLATES["low"]

    return random.choice(templates)


# =============================================================================
# Joy Composition for Session-Level Analysis
# =============================================================================


@dataclass
class SessionJoyProfile:
    """
    Joy profile aggregated across a practice session.

    This enables L3 Voice Continuity: identifying the through-line
    of voice (and joy) across a session.
    """

    observations: list[CourageAwareJoyObservation] = field(default_factory=list)

    @property
    def courage_count(self) -> int:
        """Count of courageous takes in session."""
        return sum(1 for obs in self.observations if obs.is_courageous)

    @property
    def average_intensity(self) -> float:
        """Average joy intensity across session."""
        if not self.observations:
            return 0.5
        return sum(obs.effective_intensity for obs in self.observations) / len(
            self.observations
        )

    @property
    def dominant_mode(self) -> JoyMode:
        """Most common joy mode in session."""
        if not self.observations:
            return JoyMode.WARMTH

        mode_counts = {mode: 0 for mode in JoyMode}
        for obs in self.observations:
            mode_counts[obs.mode] += 1

        return max(mode_counts, key=lambda m: mode_counts[m])

    @property
    def flow_trajectory(self) -> list[float]:
        """
        Joy intensity over time (for visualization).

        Shows whether the artist found their groove over the session.
        """
        return [obs.effective_intensity for obs in self.observations]

    def add_observation(self, observation: CourageAwareJoyObservation) -> None:
        """Add an observation to the session profile."""
        self.observations.append(observation)

    def session_warmth_summary(self) -> str:
        """
        Generate warmth summary for the session.

        This is used in crystal generation for L3 Voice Continuity.
        """
        if not self.observations:
            return "The session awaits your voice."

        intensity = self.average_intensity
        courage = self.courage_count

        if courage > 0 and intensity > 0.6:
            return f"You showed up with courage ({courage} bold moments) and found your flow."
        elif courage > 0:
            return f"You took {courage} courageous risks. That's the work."
        elif intensity > 0.7:
            return "You were in the zone. The voice was flowing."
        elif intensity > 0.5:
            return "Solid session. Building blocks for the next one."
        else:
            return "Every session is practice. You showed up, and that counts."


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core functor
    "RAP_COACH_JOY",
    # Courage-aware observation
    "CourageAwareJoyObservation",
    # Warmth generation
    "RAP_COACH_WARMTH_TEMPLATES",
    "rap_coach_warmth_response",
    # Session analysis
    "SessionJoyProfile",
]
