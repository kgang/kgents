"""
Feedback Parser: Extract actionable targets from natural language feedback.

Parses user feedback like "be more concise in the principles section"
into structured targets that can be converted to gradient steps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING

from .gradient import GradientDirection, GradientStep, TextualGradient

if TYPE_CHECKING:
    pass


class FeedbackType(Enum):
    """Type of feedback provided."""

    LENGTH = auto()  # About verbosity
    STYLE = auto()  # About tone/formality
    CONTENT = auto()  # About what's included
    STRUCTURE = auto()  # About organization
    EMPHASIS = auto()  # About what's highlighted
    GENERAL = auto()  # Unspecified


@dataclass(frozen=True)
class FeedbackTarget:
    """A specific target extracted from feedback."""

    section_name: str | None  # None = all sections
    feedback_type: FeedbackType
    direction: GradientDirection
    specifics: str | None = None  # Specific content mentioned
    confidence: float = 0.5

    def to_gradient_step(self, magnitude: float = 0.5) -> GradientStep:
        """Convert to a GradientStep."""
        description = f"{self.feedback_type.name.lower()}: {self.direction.name.lower()}"
        if self.specifics:
            description += f" ({self.specifics})"

        return GradientStep(
            section_name=self.section_name or "*",
            direction=self.direction,
            magnitude=magnitude * self.confidence,
            description=description,
            target_content=self.specifics,
        )


@dataclass(frozen=True)
class ParsedFeedback:
    """Result of parsing natural language feedback."""

    original: str
    targets: tuple[FeedbackTarget, ...]
    reasoning: tuple[str, ...]

    def to_gradient(self, base_magnitude: float = 0.5) -> TextualGradient:
        """Convert to a TextualGradient."""
        steps = [t.to_gradient_step(base_magnitude) for t in self.targets]
        return TextualGradient(
            steps=tuple(steps),
            reasoning=self.reasoning,
            source_feedback=self.original,
        )

    @property
    def is_empty(self) -> bool:
        """True if no targets were extracted."""
        return len(self.targets) == 0


class FeedbackParser:
    """
    Parse natural language feedback into structured targets.

    Uses pattern matching and keyword detection to extract:
    - Which sections are targeted
    - What type of change is requested
    - The direction of change

    This is a rule-based parser. For production use, an LLM-based
    parser would provide better coverage.
    """

    # Known section names (lowercase)
    SECTION_NAMES = frozenset(
        [
            "identity",
            "principles",
            "systems",
            "skills",
            "directories",
            "commands",
            "agentese",
            "forest",
            "context",
            "habits",
            "memory",
        ]
    )

    # Keywords mapping to directions
    DIRECTION_KEYWORDS: dict[str, GradientDirection] = {
        # Length
        "shorter": GradientDirection.CONDENSE,
        "shorten": GradientDirection.CONDENSE,
        "concise": GradientDirection.CONDENSE,
        "brief": GradientDirection.CONDENSE,
        "terse": GradientDirection.CONDENSE,
        "compact": GradientDirection.CONDENSE,
        "trim": GradientDirection.CONDENSE,
        "reduce": GradientDirection.CONDENSE,
        "longer": GradientDirection.EXPAND,
        "more detail": GradientDirection.EXPAND,
        "expand": GradientDirection.EXPAND,
        "elaborate": GradientDirection.EXPAND,
        "verbose": GradientDirection.EXPAND,
        # Style
        "formal": GradientDirection.FORMALIZE,
        "professional": GradientDirection.FORMALIZE,
        "serious": GradientDirection.FORMALIZE,
        "casual": GradientDirection.CASUALIZE,
        "friendly": GradientDirection.CASUALIZE,
        "relaxed": GradientDirection.CASUALIZE,
        # Clarity
        "clearer": GradientDirection.CLARIFY,
        "simpler": GradientDirection.CLARIFY,
        "easier": GradientDirection.CLARIFY,
        "explain": GradientDirection.CLARIFY,
        # Emphasis
        "emphasize": GradientDirection.EMPHASIZE,
        "highlight": GradientDirection.EMPHASIZE,
        "focus": GradientDirection.EMPHASIZE,
        "important": GradientDirection.EMPHASIZE,
        "deemphasize": GradientDirection.DEEMPHASIZE,
        "less focus": GradientDirection.DEEMPHASIZE,
        # Structure
        "reorder": GradientDirection.REORDER,
        "reorganize": GradientDirection.REORDER,
        "restructure": GradientDirection.REORDER,
        # Add/Remove
        "remove": GradientDirection.REMOVE,
        "delete": GradientDirection.REMOVE,
        "drop": GradientDirection.REMOVE,
        "add": GradientDirection.ADD,
        "include": GradientDirection.ADD,
        "insert": GradientDirection.ADD,
    }

    # Type keywords
    TYPE_KEYWORDS: dict[str, FeedbackType] = {
        "shorter": FeedbackType.LENGTH,
        "longer": FeedbackType.LENGTH,
        "concise": FeedbackType.LENGTH,
        "verbose": FeedbackType.LENGTH,
        "formal": FeedbackType.STYLE,
        "casual": FeedbackType.STYLE,
        "tone": FeedbackType.STYLE,
        "clear": FeedbackType.STYLE,
        "add": FeedbackType.CONTENT,
        "remove": FeedbackType.CONTENT,
        "include": FeedbackType.CONTENT,
        "reorder": FeedbackType.STRUCTURE,
        "emphasize": FeedbackType.EMPHASIS,
        "focus": FeedbackType.EMPHASIS,
    }

    def parse(self, feedback: str) -> ParsedFeedback:
        """
        Parse natural language feedback into targets.

        Args:
            feedback: Natural language feedback string

        Returns:
            ParsedFeedback with extracted targets
        """
        if not feedback or not feedback.strip():
            return ParsedFeedback(
                original=feedback,
                targets=(),
                reasoning=("Empty feedback, no changes",),
            )

        feedback_lower = feedback.lower()
        reasoning: list[str] = [f"Parsing: '{feedback}'"]
        targets: list[FeedbackTarget] = []

        # Extract mentioned sections
        mentioned_sections = self._extract_sections(feedback_lower)
        reasoning.append(f"Mentioned sections: {mentioned_sections or 'none (global)'}")

        # Extract direction
        direction = self._extract_direction(feedback_lower)
        reasoning.append(f"Direction: {direction.name if direction else 'unclear'}")

        # Extract type
        feedback_type = self._extract_type(feedback_lower)
        reasoning.append(f"Type: {feedback_type.name}")

        # Build targets
        if direction:
            if mentioned_sections:
                for section in mentioned_sections:
                    targets.append(
                        FeedbackTarget(
                            section_name=section,
                            feedback_type=feedback_type,
                            direction=direction,
                            specifics=self._extract_specifics(feedback, section),
                            confidence=0.7,
                        )
                    )
                    reasoning.append(f"  Target: {section} → {direction.name}")
            else:
                # Global feedback
                targets.append(
                    FeedbackTarget(
                        section_name=None,
                        feedback_type=feedback_type,
                        direction=direction,
                        confidence=0.5,
                    )
                )
                reasoning.append(f"  Target: all sections → {direction.name}")
        else:
            reasoning.append("Could not determine direction, creating general target")
            targets.append(
                FeedbackTarget(
                    section_name=None,
                    feedback_type=FeedbackType.GENERAL,
                    direction=GradientDirection.CLARIFY,  # Default
                    specifics=feedback[:100],
                    confidence=0.3,
                )
            )

        return ParsedFeedback(
            original=feedback,
            targets=tuple(targets),
            reasoning=tuple(reasoning),
        )

    def _extract_sections(self, text: str) -> list[str]:
        """Extract mentioned section names."""
        found: list[str] = []
        for section in self.SECTION_NAMES:
            if section in text:
                found.append(section)
        return found

    def _extract_direction(self, text: str) -> GradientDirection | None:
        """Extract the direction of change from keywords."""
        for keyword, direction in self.DIRECTION_KEYWORDS.items():
            if keyword in text:
                return direction
        return None

    def _extract_type(self, text: str) -> FeedbackType:
        """Extract the type of feedback."""
        for keyword, ftype in self.TYPE_KEYWORDS.items():
            if keyword in text:
                return ftype
        return FeedbackType.GENERAL

    def _extract_specifics(self, text: str, section: str) -> str | None:
        """Extract specific content mentioned in context of a section."""
        # Look for quoted content
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            return str(quoted[0])

        # Look for content after "about" or "regarding"
        match = re.search(rf"{section}\s+(?:about|regarding|on)\s+(.+?)(?:\.|$)", text, re.I)
        if match:
            return match.group(1).strip()

        return None


def parse_feedback(feedback: str) -> ParsedFeedback:
    """Convenience function to parse feedback."""
    return FeedbackParser().parse(feedback)


__all__ = [
    "FeedbackType",
    "FeedbackTarget",
    "ParsedFeedback",
    "FeedbackParser",
    "parse_feedback",
]
