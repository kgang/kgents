"""
Contradiction Classification: Strength-Based Taxonomy.

Classifies contradictions by strength into four categories:
1. APPARENT (< 0.2): Likely different scopes or contexts
2. PRODUCTIVE (0.2-0.4): Could drive synthesis
3. TENSION (0.4-0.6): Real conflict, needs attention
4. FUNDAMENTAL (>= 0.6): Deep inconsistency

Philosophy:
    Not all contradictions are created equal.
    APPARENT contradictions may resolve with scope clarification.
    PRODUCTIVE contradictions are opportunities for synthesis.
    TENSION requires deliberate engagement.
    FUNDAMENTAL indicates core belief conflict.

See: plans/zero-seed-genesis-grand-strategy.md (Part VIII)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .detection import ContradictionPair


class ContradictionType(Enum):
    """
    Classification of contradiction by strength.

    APPARENT: Likely different scopes/contexts (strength < 0.2)
        Example: "I like dogs" vs "I like cats" — not contradictory
        Action: Suggest scope clarification

    PRODUCTIVE: Could drive synthesis (0.2 <= strength < 0.4)
        Example: "Simplicity is best" vs "Richness is valuable"
        Action: Offer synthesis opportunity

    TENSION: Real conflict needing attention (0.4 <= strength < 0.6)
        Example: "Always be honest" vs "White lies protect feelings"
        Action: Prompt deliberate resolution

    FUNDAMENTAL: Deep inconsistency (strength >= 0.6)
        Example: "All knowledge is constructed" vs "Mathematical truths are discovered"
        Action: Flag for careful examination
    """

    APPARENT = "APPARENT"
    PRODUCTIVE = "PRODUCTIVE"
    TENSION = "TENSION"
    FUNDAMENTAL = "FUNDAMENTAL"

    @property
    def description(self) -> str:
        """Human-readable description of this type."""
        match self:
            case ContradictionType.APPARENT:
                return "Likely different scopes or contexts"
            case ContradictionType.PRODUCTIVE:
                return "Could drive synthesis — opportunity for growth"
            case ContradictionType.TENSION:
                return "Real conflict — needs attention"
            case ContradictionType.FUNDAMENTAL:
                return "Deep inconsistency — examine carefully"

    @property
    def color(self) -> str:
        """UI color indicator for this type."""
        match self:
            case ContradictionType.APPARENT:
                return "gray"  # Neutral
            case ContradictionType.PRODUCTIVE:
                return "green"  # Opportunity
            case ContradictionType.TENSION:
                return "yellow"  # Warning
            case ContradictionType.FUNDAMENTAL:
                return "red"  # Critical

    @property
    def urgency(self) -> int:
        """Urgency level (0-3) for sorting/prioritization."""
        match self:
            case ContradictionType.APPARENT:
                return 0
            case ContradictionType.PRODUCTIVE:
                return 1
            case ContradictionType.TENSION:
                return 2
            case ContradictionType.FUNDAMENTAL:
                return 3


# Classification boundaries
APPARENT_MAX = 0.2
PRODUCTIVE_MAX = 0.4
TENSION_MAX = 0.6


@dataclass(frozen=True)
class ClassificationResult:
    """
    Result of classifying a contradiction.

    Attributes:
        type: The classified type
        strength: The original strength value
        confidence: Confidence in classification [0, 1]
        reasoning: Human-readable explanation
    """

    type: ContradictionType
    strength: float
    confidence: float
    reasoning: str

    def to_dict(self) -> dict:
        """Serialize for API/storage."""
        return {
            "type": self.type.value,
            "strength": round(self.strength, 3),
            "confidence": round(self.confidence, 2),
            "reasoning": self.reasoning,
            "description": self.type.description,
            "color": self.type.color,
            "urgency": self.type.urgency,
        }


class ContradictionClassifier:
    """
    Classifies contradictions by strength.

    Pure classification based on threshold boundaries.
    No external dependencies, deterministic output.
    """

    def __init__(
        self,
        apparent_max: float = APPARENT_MAX,
        productive_max: float = PRODUCTIVE_MAX,
        tension_max: float = TENSION_MAX,
    ):
        """
        Initialize classifier with custom boundaries.

        Args:
            apparent_max: Maximum strength for APPARENT (default 0.2)
            productive_max: Maximum strength for PRODUCTIVE (default 0.4)
            tension_max: Maximum strength for TENSION (default 0.6)
        """
        self.apparent_max = apparent_max
        self.productive_max = productive_max
        self.tension_max = tension_max

    def classify(self, strength: float) -> ClassificationResult:
        """
        Classify a contradiction by its strength.

        Args:
            strength: The super-additive loss value

        Returns:
            ClassificationResult with type and reasoning
        """
        # Determine type based on boundaries
        if strength < self.apparent_max:
            type_ = ContradictionType.APPARENT
            reasoning = (
                f"Strength {strength:.2f} suggests these statements may apply "
                "in different contexts or scopes. Consider clarifying when each applies."
            )
            confidence = 0.8  # High confidence in low-strength classification
        elif strength < self.productive_max:
            type_ = ContradictionType.PRODUCTIVE
            reasoning = (
                f"Strength {strength:.2f} indicates tension that could drive synthesis. "
                "This is an opportunity to find a higher truth that resolves both."
            )
            confidence = 0.7  # Moderate confidence
        elif strength < self.tension_max:
            type_ = ContradictionType.TENSION
            reasoning = (
                f"Strength {strength:.2f} indicates real conflict. "
                "These beliefs are in tension — deliberate resolution recommended."
            )
            confidence = 0.7  # Moderate confidence
        else:
            type_ = ContradictionType.FUNDAMENTAL
            reasoning = (
                f"Strength {strength:.2f} indicates deep inconsistency. "
                "These beliefs fundamentally contradict — careful examination needed."
            )
            confidence = 0.9  # High confidence in high-strength classification

        return ClassificationResult(
            type=type_,
            strength=strength,
            confidence=confidence,
            reasoning=reasoning,
        )

    def classify_pair(self, pair: ContradictionPair) -> ClassificationResult:
        """
        Classify a ContradictionPair.

        Convenience method that extracts strength from the pair.

        Args:
            pair: The ContradictionPair to classify

        Returns:
            ClassificationResult
        """
        return self.classify(pair.strength)

    def batch_classify(
        self,
        pairs: list[ContradictionPair],
    ) -> list[tuple[ContradictionPair, ClassificationResult]]:
        """
        Classify multiple contradiction pairs.

        Args:
            pairs: List of ContradictionPairs

        Returns:
            List of (pair, classification) tuples
        """
        return [(pair, self.classify_pair(pair)) for pair in pairs]


# Singleton classifier for convenience
default_classifier = ContradictionClassifier()


def classify_contradiction(strength: float) -> ClassificationResult:
    """
    Convenience function for one-off classification.

    Args:
        strength: Super-additive loss value

    Returns:
        ClassificationResult
    """
    return default_classifier.classify(strength)


__all__ = [
    "ContradictionType",
    "APPARENT_MAX",
    "PRODUCTIVE_MAX",
    "TENSION_MAX",
    "ClassificationResult",
    "ContradictionClassifier",
    "classify_contradiction",
    "default_classifier",
]
