"""
GhostAnalyzerAgent: Captures and analyzes paths not taken.

From muse-part-iii.md:
    "With 50 options generated per cycle and only 1 selected, we produce
    49 ghosts per iteration. Over 30-50 iterations, that's 1,500-2,500
    ghosts per session."

Ghosts are the negative space that defines the work. By analyzing:
- What Kent consistently rejects
- Where AI and Kent disagree
- Which rejections were strong vs. mild
- Which ghosts might be worth resurrecting

See: spec/c-gent/muse-part-iii.md
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from ..models import (
    CreativeOption,
    Ghost,
    SessionState,
    TasteVector,
)

T = TypeVar("T")


# =============================================================================
# Ghost Analytics
# =============================================================================


@dataclass
class RejectionPattern:
    """A pattern in Kent's rejections."""

    pattern_type: str  # "word", "taste_dimension", "structure"
    pattern_value: str  # The specific pattern
    occurrences: int  # How many times
    average_strength: float  # Average rejection strength
    examples: list[str] = field(default_factory=list)


@dataclass
class AIDisagreement:
    """Record of AI championing something Kent rejected."""

    ghost_id: str
    ai_reasoning: str  # Why AI liked it
    kent_reasoning: str  # Why Kent rejected
    surprise_level: float  # How surprised AI was
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ResurrectionCandidate:
    """A ghost worth bringing back."""

    ghost: Ghost
    resurrection_reason: str
    confidence: float  # How confident in resurrection
    suggested_modifications: list[str] = field(default_factory=list)


@dataclass
class GhostAnalysis:
    """Complete analysis of session ghosts."""

    total_ghosts: int
    rejection_patterns: list[RejectionPattern]
    ai_disagreements: list[AIDisagreement]
    resurrection_candidates: list[ResurrectionCandidate]
    taste_insights: dict[str, str]  # Insights about taste from rejections


# =============================================================================
# GhostAnalyzerAgent
# =============================================================================


class GhostAnalyzerAgent:
    """
    Analyzer of paths not taken.

    Ghosts reveal taste through absence. What Kent doesn't choose
    is as important as what Kent does choose.

    The agent:
    1. Records all rejected alternatives with reasoning
    2. Analyzes rejection patterns (what does Kent always reject?)
    3. Identifies ghosts worth resurrecting (high surprise_at_rejection)
    4. Tracks AI-championed ghosts (where AI thought Kent was wrong)
    """

    def __init__(self):
        """Initialize the ghost analyzer."""
        self.all_ghosts: list[Ghost] = []
        self.ai_disagreements: list[AIDisagreement] = []
        self.resurrected: list[str] = []  # Ghost IDs that were resurrected

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def record_rejection(
        self,
        option: CreativeOption,
        rejection_reason: str,
        rejection_strength: float = 0.5,
        ai_championed: bool = False,
        ai_surprise: float = 0.5,
        iteration: int = 0,
    ) -> Ghost:
        """
        Record a rejected option as a ghost.

        Args:
            option: The rejected option
            rejection_reason: Why Kent rejected it
            rejection_strength: How strongly (0=mild, 1=visceral)
            ai_championed: Did AI advocate for this?
            ai_surprise: How surprised AI was at rejection
            iteration: Which iteration this occurred

        Returns:
            The created Ghost
        """
        ghost: Ghost[Any] = Ghost(
            original_option=option,
            rejection_reason=rejection_reason,
            rejection_strength=rejection_strength,
            ai_championed=ai_championed,
            surprise_at_rejection=ai_surprise,
            iteration=iteration,
        )

        self.all_ghosts.append(ghost)

        # Track AI disagreements
        if ai_championed:
            self.ai_disagreements.append(
                AIDisagreement(
                    ghost_id=ghost.id,
                    ai_reasoning=option.ai_reasoning,
                    kent_reasoning=rejection_reason,
                    surprise_level=ai_surprise,
                )
            )

        return ghost

    def analyze(self, session: SessionState | None = None) -> GhostAnalysis:
        """
        Analyze accumulated ghosts for patterns.

        Args:
            session: Optional session to include in analysis

        Returns:
            GhostAnalysis with patterns, disagreements, candidates
        """
        ghosts = self.all_ghosts
        if session:
            ghosts = ghosts + session.ghosts

        if not ghosts:
            return GhostAnalysis(
                total_ghosts=0,
                rejection_patterns=[],
                ai_disagreements=[],
                resurrection_candidates=[],
                taste_insights={},
            )

        # Analyze rejection patterns
        patterns = self._find_rejection_patterns(ghosts)

        # Find resurrection candidates
        candidates = self._find_resurrection_candidates(ghosts)

        # Extract taste insights
        insights = self._extract_taste_insights(ghosts, patterns)

        return GhostAnalysis(
            total_ghosts=len(ghosts),
            rejection_patterns=patterns,
            ai_disagreements=self.ai_disagreements,
            resurrection_candidates=candidates,
            taste_insights=insights,
        )

    def find_worth_resurrecting(
        self,
        session: SessionState | None = None,
        limit: int = 5,
    ) -> list[ResurrectionCandidate]:
        """
        Find ghosts that deserve another chance.

        Criteria:
        - High AI surprise at rejection (AI thought it was good)
        - Mild rejection strength (Kent wasn't viscerally opposed)
        - High novelty score (brings something different)

        Args:
            session: Session context
            limit: Maximum candidates to return

        Returns:
            List of resurrection candidates
        """
        ghosts = self.all_ghosts
        if session:
            ghosts = ghosts + session.ghosts

        candidates = []
        for ghost in ghosts:
            if ghost.worth_resurrecting and ghost.id not in self.resurrected:
                modifications = self._suggest_modifications(ghost)
                candidates.append(
                    ResurrectionCandidate(
                        ghost=ghost,
                        resurrection_reason=self._explain_resurrection(ghost),
                        confidence=ghost.surprise_at_rejection * (1 - ghost.rejection_strength),
                        suggested_modifications=modifications,
                    )
                )

        # Sort by confidence
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates[:limit]

    def mark_resurrected(self, ghost_id: str) -> None:
        """Mark a ghost as resurrected (won't suggest again)."""
        self.resurrected.append(ghost_id)

    def get_rejection_patterns(
        self,
        pattern_type: str | None = None,
        min_occurrences: int = 2,
    ) -> list[RejectionPattern]:
        """
        Get rejection patterns, optionally filtered.

        Args:
            pattern_type: Filter by type ("word", "taste_dimension", "structure")
            min_occurrences: Minimum occurrences to include

        Returns:
            List of rejection patterns
        """
        analysis = self.analyze()
        patterns = analysis.rejection_patterns

        if pattern_type:
            patterns = [p for p in patterns if p.pattern_type == pattern_type]

        patterns = [p for p in patterns if p.occurrences >= min_occurrences]
        return sorted(patterns, key=lambda p: p.occurrences, reverse=True)

    def get_ai_disagreements(
        self,
        min_surprise: float = 0.7,
    ) -> list[AIDisagreement]:
        """
        Get cases where AI strongly disagreed with Kent.

        Args:
            min_surprise: Minimum surprise level to include

        Returns:
            List of significant disagreements
        """
        return [d for d in self.ai_disagreements if d.surprise_level >= min_surprise]

    # -------------------------------------------------------------------------
    # Analysis Helpers
    # -------------------------------------------------------------------------

    def _find_rejection_patterns(self, ghosts: list[Ghost]) -> list[RejectionPattern]:
        """Find patterns in rejection reasons."""
        patterns: list[RejectionPattern] = []

        # Word frequency analysis
        word_counts: Counter[str] = Counter()
        for ghost in ghosts:
            words = re.findall(r"\b\w+\b", ghost.rejection_reason.lower())
            word_counts.update(words)

        # Filter common words and create patterns
        stopwords = {"the", "a", "an", "is", "was", "too", "not", "this", "it", "and", "or", "but"}
        for word, count in word_counts.most_common(20):
            if word not in stopwords and count >= 2:
                # Calculate average strength for this word
                matching = [g for g in ghosts if word in g.rejection_reason.lower()]
                avg_strength = sum(g.rejection_strength for g in matching) / len(matching)

                patterns.append(
                    RejectionPattern(
                        pattern_type="word",
                        pattern_value=word,
                        occurrences=count,
                        average_strength=avg_strength,
                        examples=[g.rejection_reason[:50] for g in matching[:3]],
                    )
                )

        # Strength-based patterns
        strong_rejections = [g for g in ghosts if g.rejection_strength > 0.7]
        if len(strong_rejections) >= 2:
            patterns.append(
                RejectionPattern(
                    pattern_type="strength",
                    pattern_value="visceral_rejection",
                    occurrences=len(strong_rejections),
                    average_strength=sum(g.rejection_strength for g in strong_rejections)
                    / len(strong_rejections),
                    examples=[g.rejection_reason[:50] for g in strong_rejections[:3]],
                )
            )

        mild_rejections = [g for g in ghosts if g.rejection_strength < 0.3]
        if len(mild_rejections) >= 2:
            patterns.append(
                RejectionPattern(
                    pattern_type="strength",
                    pattern_value="mild_rejection",
                    occurrences=len(mild_rejections),
                    average_strength=sum(g.rejection_strength for g in mild_rejections)
                    / len(mild_rejections),
                    examples=[g.rejection_reason[:50] for g in mild_rejections[:3]],
                )
            )

        return patterns

    def _find_resurrection_candidates(self, ghosts: list[Ghost]) -> list[ResurrectionCandidate]:
        """Find ghosts worth resurrecting."""
        candidates = []

        for ghost in ghosts:
            if ghost.worth_resurrecting and ghost.id not in self.resurrected:
                candidates.append(
                    ResurrectionCandidate(
                        ghost=ghost,
                        resurrection_reason=self._explain_resurrection(ghost),
                        confidence=ghost.surprise_at_rejection * (1 - ghost.rejection_strength),
                        suggested_modifications=self._suggest_modifications(ghost),
                    )
                )

        return sorted(candidates, key=lambda c: c.confidence, reverse=True)[:5]

    def _extract_taste_insights(
        self,
        ghosts: list[Ghost],
        patterns: list[RejectionPattern],
    ) -> dict[str, str]:
        """Extract taste insights from rejection patterns."""
        insights = {}

        # Look for consistent patterns
        word_patterns = [p for p in patterns if p.pattern_type == "word" and p.occurrences >= 3]
        if word_patterns:
            top_rejected = [p.pattern_value for p in word_patterns[:3]]
            insights["consistent_rejections"] = f"Consistently rejects: {', '.join(top_rejected)}"

        # Look at AI disagreements
        high_surprise = [g for g in ghosts if g.surprise_at_rejection > 0.7]
        if high_surprise:
            insights["ai_blind_spots"] = (
                f"AI surprised {len(high_surprise)} times—possible taste gaps"
            )

        # Strength patterns
        visceral = [g for g in ghosts if g.rejection_strength > 0.8]
        if visceral:
            insights["hard_nos"] = (
                f"{len(visceral)} visceral rejections—these are the 'never' boundaries"
            )

        return insights

    def _explain_resurrection(self, ghost: Ghost) -> str:
        """Explain why a ghost is worth resurrecting."""
        reasons = []

        if ghost.ai_championed:
            reasons.append("AI believed in this option")

        if ghost.rejection_strength < 0.3:
            reasons.append("rejection was mild")

        if ghost.surprise_at_rejection > 0.7:
            reasons.append("AI was surprised by rejection")

        if ghost.original_option and ghost.original_option.novelty_score > 0.7:
            reasons.append("high novelty score")

        return "; ".join(reasons) if reasons else "Worth reconsidering"

    def _suggest_modifications(self, ghost: Ghost) -> list[str]:
        """Suggest how to modify a ghost for resurrection."""
        suggestions = []

        # Based on rejection reason
        reason = ghost.rejection_reason.lower()

        if "too" in reason:
            # Extract what was "too much"
            match = re.search(r"too\s+(\w+)", reason)
            if match:
                suggestions.append(f"Reduce the {match.group(1)}")

        if "not enough" in reason or "needs more" in reason:
            suggestions.append("Strengthen the core element")

        if "unclear" in reason or "vague" in reason:
            suggestions.append("Add specificity")

        if "cliche" in reason or "obvious" in reason:
            suggestions.append("Find unexpected angle")

        if not suggestions:
            suggestions.append("Address rejection reason directly")

        return suggestions


# =============================================================================
# Module-level Functions
# =============================================================================


def create_ghost_analyzer() -> GhostAnalyzerAgent:
    """Create a new GhostAnalyzerAgent."""
    return GhostAnalyzerAgent()


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Types
    "RejectionPattern",
    "AIDisagreement",
    "ResurrectionCandidate",
    "GhostAnalysis",
    # Agent
    "GhostAnalyzerAgent",
    # Functions
    "create_ghost_analyzer",
]
