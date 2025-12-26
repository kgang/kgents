"""
L4 Courage Preservation Law Implementation.

"High-risk takes are protected from negative weighting by default.
Courage is rewarded, not punished."

This module implements the L4 law from PROTO_SPEC:
- Identifies courageous (high-risk) takes
- Protects them from negative scoring
- Generates courage-specific acknowledgments
- Preserves courage moments in crystals

The Core Insight:
    Courage is the point. When an artist takes a risk, that risk
    is the success - regardless of whether the take "works" in
    a conventional sense. The system must never punish courage.

Anti-Success Pattern (Judge Emergence):
    The coach feels evaluative - the artist hesitates before
    taking risks, anticipates criticism, or performs FOR the
    system instead of for themselves. The system has become a critic.

See: pilots/rap-coach-flow-lab/PROTO_SPEC.md (L4)
See: plans/enlightened-synthesis/04-joy-integration.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from services.witness.mark import Mark


# =============================================================================
# Risk Level Classification
# =============================================================================


class RiskLevel(Enum):
    """
    Risk level for a take.

    High-risk takes get L4 protection.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# =============================================================================
# Courage Moment: What Gets Preserved
# =============================================================================


@dataclass(frozen=True)
class CourageMoment:
    """
    A moment of courage captured in a take.

    This is what gets preserved in the VoiceCrystal.
    L4 ensures these are never negatively weighted.

    Attributes:
        moment_id: Unique identifier
        take_id: Reference to the take
        courage_description: What made this courageous
        risk_taken: The specific risk that was taken
        outcome: Optional outcome (but outcome doesn't affect value)
        timestamp: When this courage was witnessed
    """

    moment_id: str
    take_id: str
    courage_description: str
    risk_taken: str
    outcome: str | None = None  # "landed", "missed", "evolving"
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_take(
        cls,
        take_id: str,
        intent_expression_goal: str,
        intent_register: str,
    ) -> "CourageMoment":
        """
        Create a CourageMoment from a high-risk take.

        Args:
            take_id: The take's identifier
            intent_expression_goal: What the artist was trying to express
            intent_register: The register being explored

        Returns:
            CourageMoment capturing the courage
        """
        # Derive courage description from intent
        courage_description = (
            f"Explored the {intent_register} register, "
            f"pushing toward: {intent_expression_goal}"
        )

        # The risk is in the exploration itself
        risk_taken = f"Went for {intent_register} territory"

        return cls(
            moment_id=f"courage-{uuid4().hex[:12]}",
            take_id=take_id,
            courage_description=courage_description,
            risk_taken=risk_taken,
            outcome=None,  # Outcome is not judged
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "moment_id": self.moment_id,
            "take_id": self.take_id,
            "courage_description": self.courage_description,
            "risk_taken": self.risk_taken,
            "outcome": self.outcome,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CourageMoment":
        """Create from dictionary."""
        return cls(
            moment_id=data["moment_id"],
            take_id=data["take_id"],
            courage_description=data["courage_description"],
            risk_taken=data["risk_taken"],
            outcome=data.get("outcome"),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if data.get("timestamp")
            else datetime.now(),
        )


# =============================================================================
# Courage Protection Engine
# =============================================================================


class CourageProtectionEngine:
    """
    Enforces L4 Courage Preservation Law.

    This engine:
    1. Identifies which takes are courageous
    2. Protects them from negative weighting
    3. Generates courage-specific acknowledgments
    4. Aggregates courage moments for crystals

    Usage:
        engine = CourageProtectionEngine()
        is_courageous = engine.is_courageous(risk_level="high")
        if is_courageous:
            moment = engine.create_moment(take_id, intent)
            response = engine.courage_acknowledgment()
    """

    # Minimum protected intensity for courageous takes
    # A courageous take can never score below this
    COURAGE_FLOOR = 0.5

    # Boost applied to courageous takes
    COURAGE_BOOST = 0.15

    def __init__(self) -> None:
        """Initialize the courage protection engine."""
        self._courage_moments: list[CourageMoment] = []

    def is_courageous(self, risk_level: str | RiskLevel) -> bool:
        """
        Determine if a take qualifies for courage protection.

        Currently, only HIGH risk gets protection.
        """
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level.lower())
        return risk_level == RiskLevel.HIGH

    def protect_score(
        self,
        raw_score: float,
        risk_level: str | RiskLevel,
    ) -> float:
        """
        Apply L4 protection to a score.

        For courageous takes:
        - Score can never go below COURAGE_FLOOR
        - Score gets COURAGE_BOOST added

        Args:
            raw_score: The raw score (before protection)
            risk_level: The take's risk level

        Returns:
            Protected score (higher for courageous takes)
        """
        if not self.is_courageous(risk_level):
            return raw_score

        # Apply floor
        protected = max(self.COURAGE_FLOOR, raw_score)

        # Apply boost
        protected = min(1.0, protected + self.COURAGE_BOOST)

        return protected

    def create_moment(
        self,
        take_id: str,
        intent_expression_goal: str,
        intent_register: str,
    ) -> CourageMoment:
        """
        Create and track a courage moment.

        Args:
            take_id: The take's identifier
            intent_expression_goal: What the artist was trying to express
            intent_register: The register being explored

        Returns:
            CourageMoment that will be preserved in crystal
        """
        moment = CourageMoment.from_take(
            take_id=take_id,
            intent_expression_goal=intent_expression_goal,
            intent_register=intent_register,
        )
        self._courage_moments.append(moment)
        return moment

    def courage_acknowledgment(self, register: str | None = None) -> str:
        """
        Generate courage-specific acknowledgment.

        These responses are ALWAYS warm. They celebrate the risk,
        not the outcome.
        """
        import random

        # Register-specific acknowledgments
        register_responses = {
            "aggressive": [
                "Brought the heat. That's energy.",
                "You went for it. I felt that aggression.",
                "Bold move going aggressive there.",
            ],
            "vulnerable": [
                "That vulnerability takes courage.",
                "Real talk. That was honest.",
                "Opening up like that - that's the work.",
            ],
            "experimental": [
                "I see you exploring new territory.",
                "That's how you find new voice.",
                "Experimentation is the point.",
            ],
            "playful": [
                "Playing with the form. Nice.",
                "That playfulness is a choice.",
                "Having fun with it - that matters.",
            ],
        }

        # General courage acknowledgments
        general = [
            "Courage is the win.",
            "That risk was the point.",
            "I see you pushing edges.",
            "Bold territory. Respect.",
            "Taking that chance - that's what grows voice.",
            "The risk is the practice.",
        ]

        if register and register in register_responses:
            return random.choice(register_responses[register])
        return random.choice(general)

    def get_session_moments(self) -> list[CourageMoment]:
        """Get all courage moments from the session."""
        return list(self._courage_moments)

    def clear_session(self) -> None:
        """Clear courage moments for new session."""
        self._courage_moments = []

    @property
    def courage_count(self) -> int:
        """Count of courage moments in session."""
        return len(self._courage_moments)


# =============================================================================
# Courage-Aware Mark Factory
# =============================================================================


@dataclass
class TakeMark:
    """
    Mark factory for takes with courage awareness.

    This creates marks that include:
    - Intent (L1 Intent Declaration)
    - Risk level (for L4 protection)
    - Courage moment (if applicable)

    Integrates with services/witness/mark.py Mark primitive.
    """

    take_id: str
    session_id: str
    intent_expression_goal: str
    intent_register: str
    risk_level: RiskLevel
    courage_moment: CourageMoment | None = None

    @classmethod
    def create(
        cls,
        session_id: str,
        expression_goal: str,
        register: str,
        risk_level: str,
        engine: CourageProtectionEngine | None = None,
    ) -> "TakeMark":
        """
        Create a TakeMark with automatic courage detection.

        Args:
            session_id: Session identifier
            expression_goal: What the artist is trying to express
            register: The register being explored
            risk_level: "low", "medium", "high"
            engine: Optional courage protection engine

        Returns:
            TakeMark ready for emission
        """
        take_id = f"take-{uuid4().hex[:12]}"
        risk = RiskLevel(risk_level.lower())

        courage_moment = None
        if engine and engine.is_courageous(risk):
            courage_moment = engine.create_moment(
                take_id=take_id,
                intent_expression_goal=expression_goal,
                intent_register=register,
            )

        return cls(
            take_id=take_id,
            session_id=session_id,
            intent_expression_goal=expression_goal,
            intent_register=register,
            risk_level=risk,
            courage_moment=courage_moment,
        )

    def to_mark_metadata(self) -> dict[str, Any]:
        """
        Convert to metadata dict for Mark emission.

        This is passed to Mark.from_thought() or similar.
        """
        metadata = {
            "take_id": self.take_id,
            "session_id": self.session_id,
            "intent": {
                "expression_goal": self.intent_expression_goal,
                "register": self.intent_register,
            },
            "risk_level": self.risk_level.value,
            "is_courageous": self.courage_moment is not None,
        }

        if self.courage_moment:
            metadata["courage_moment"] = self.courage_moment.to_dict()

        return metadata


# =============================================================================
# Anti-Judge Detection
# =============================================================================


class AntiJudgeDetector:
    """
    Detects when the system is becoming a judge (anti-success pattern).

    Monitors for:
    - Language that sounds evaluative
    - Patterns that might cause artist hesitation
    - Conformity pressure
    """

    # Words/phrases that indicate judge emergence
    JUDGE_INDICATORS = [
        "you should",
        "you need to",
        "that was wrong",
        "mistake",
        "error",
        "failed",
        "not good",
        "do better",
        "try harder",
        "incorrect",
        "weak",
        "poor",
        "bad",
    ]

    # Words/phrases that indicate good coaching
    COACH_INDICATORS = [
        "i noticed",
        "i heard",
        "that felt like",
        "what if",
        "you might try",
        "interesting",
        "curious",
        "exploring",
        "building",
        "courage",
    ]

    def is_judge_language(self, text: str) -> bool:
        """
        Check if text contains judge-like language.

        Returns True if text sounds evaluative/judgmental.
        """
        text_lower = text.lower()

        for indicator in self.JUDGE_INDICATORS:
            if indicator in text_lower:
                return True

        return False

    def is_coach_language(self, text: str) -> bool:
        """
        Check if text contains coach-like language.

        Returns True if text sounds supportive/observational.
        """
        text_lower = text.lower()

        for indicator in self.COACH_INDICATORS:
            if indicator in text_lower:
                return True

        return False

    def transform_to_coach(self, judge_text: str) -> str:
        """
        Transform judge language to coach language.

        This is a fallback for generated text that sounds too judgmental.
        """
        # Simple replacement patterns
        replacements = [
            ("you should", "you might try"),
            ("you need to", "consider"),
            ("that was wrong", "that's interesting territory"),
            ("mistake", "exploration"),
            ("failed", "tried something new"),
            ("not good", "still developing"),
            ("weak", "emerging"),
        ]

        result = judge_text
        for judge, coach in replacements:
            result = result.replace(judge, coach)
            result = result.replace(judge.title(), coach.title())

        return result


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "RiskLevel",
    # Data classes
    "CourageMoment",
    "TakeMark",
    # Engines
    "CourageProtectionEngine",
    "AntiJudgeDetector",
]
