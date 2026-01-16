"""
TasteVectorAgent: The externalized Mirror Test.

From muse.md:
    "Kent's taste is not ineffable. It can be captured, refined,
    and applied algorithmically."

This agent:
1. Maintains Kent's TasteVector (darkness, complexity, warmth, energy, novelty, restraint)
2. Applies the Mirror Test: "Is this me on my best day?"
3. Tracks taste evolution across sessions
4. Detects drift from historical patterns

See: spec/c-gent/muse.md
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from ..models import (
    KENT_TASTE_DEFAULT,
    CreativeOption,
    ResonanceLevel,
    SessionState,
    TasteVector,
)

T = TypeVar("T")


# =============================================================================
# Taste Analysis Results
# =============================================================================


@dataclass
class TasteScore:
    """Score for taste alignment."""

    alignment: float  # Overall alignment (0-1)
    dimension_scores: dict[str, float]  # Per-dimension scores
    violations: list[str]  # Never/always violations
    reasoning: str = ""

    @property
    def resonance(self) -> ResonanceLevel:
        """Convert alignment to resonance level."""
        if self.violations:
            return ResonanceLevel.DISSONANT
        if self.alignment < 0.3:
            return ResonanceLevel.DISSONANT
        if self.alignment < 0.5:
            return ResonanceLevel.FOREIGN
        if self.alignment < 0.8:
            return ResonanceLevel.RESONANT
        return ResonanceLevel.PROFOUND


@dataclass
class MirrorTestResult:
    """Result of applying the Mirror Test."""

    level: ResonanceLevel
    confidence: float = 0.5  # How confident in this judgment
    reasoning: str = ""
    suggestions: list[str] = field(default_factory=list)  # How to improve
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DriftReport:
    """Report on taste drift from baseline."""

    baseline: TasteVector
    current: TasteVector
    drift_amount: float  # Euclidean distance
    dimension_drifts: dict[str, float]  # Per-dimension drift
    is_concerning: bool = False  # Drift > threshold
    explanation: str = ""


@dataclass
class TasteEvolution:
    """Record of taste evolution over time."""

    session_id: str
    selections: list[tuple[str, str]]  # (option_id, reason)
    evolved_taste: TasteVector
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# TasteVectorAgent
# =============================================================================


class TasteVectorAgent:
    """
    The externalized Mirror Test.

    Kent's taste is not mystical—it can be captured as a vector
    and applied algorithmically to creative outputs.

    The agent maintains:
    - Current taste vector (evolves with selections)
    - Historical baseline (for drift detection)
    - Selection history (for learning patterns)
    """

    def __init__(
        self,
        taste: TasteVector | None = None,
        baseline: TasteVector | None = None,
    ):
        """
        Initialize with taste vector.

        Args:
            taste: Current taste vector (defaults to KENT_TASTE_DEFAULT)
            baseline: Historical baseline for drift detection
        """
        self.taste = taste or KENT_TASTE_DEFAULT
        self.baseline = baseline or KENT_TASTE_DEFAULT
        self.selection_history: list[tuple[str, TasteVector]] = []
        self.evolution_history: list[TasteEvolution] = []

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def apply(self, work: Any, estimated_taste: TasteVector | None = None) -> TasteScore:
        """
        Apply taste vector to evaluate a creative work.

        Args:
            work: The creative work to evaluate
            estimated_taste: Predicted taste profile of the work

        Returns:
            TasteScore with alignment, violations, and reasoning
        """
        if estimated_taste is None:
            # If no estimated taste provided, use neutral
            estimated_taste = TasteVector()

        # Calculate dimension alignments
        dimension_scores = {
            "darkness": 1.0 - abs(self.taste.darkness - estimated_taste.darkness),
            "complexity": 1.0 - abs(self.taste.complexity - estimated_taste.complexity),
            "warmth": 1.0 - abs(self.taste.warmth - estimated_taste.warmth),
            "energy": 1.0 - abs(self.taste.energy - estimated_taste.energy),
            "novelty": 1.0 - abs(self.taste.novelty - estimated_taste.novelty),
            "restraint": 1.0 - abs(self.taste.restraint - estimated_taste.restraint),
        }

        # Check never/always violations
        violations = self._check_violations(work)

        # Calculate overall alignment
        alignment = sum(dimension_scores.values()) / len(dimension_scores)

        # Reduce alignment for violations
        if violations:
            alignment *= 0.5  # Significant penalty for violations

        return TasteScore(
            alignment=alignment,
            dimension_scores=dimension_scores,
            violations=violations,
            reasoning=self._generate_reasoning(alignment, dimension_scores, violations),
        )

    def mirror_test(
        self, work: Any, estimated_taste: TasteVector | None = None
    ) -> MirrorTestResult:
        """
        Apply the Mirror Test: "Is this me on my best day?"

        This is the fundamental taste operation—evaluating whether
        a creative output resonates with Kent's authentic voice.

        Args:
            work: The creative work to evaluate
            estimated_taste: Predicted taste profile of the work

        Returns:
            MirrorTestResult with resonance level and suggestions
        """
        score = self.apply(work, estimated_taste)

        suggestions = []
        if score.resonance < ResonanceLevel.RESONANT:
            # Generate improvement suggestions based on misaligned dimensions
            low_dims = [k for k, v in score.dimension_scores.items() if v < 0.5]
            for dim in low_dims:
                target = getattr(self.taste, dim)
                suggestions.append(
                    f"Adjust {dim}: target is {target:.1f}, work is too "
                    f"{'low' if target > 0.5 else 'high'}"
                )

            if score.violations:
                suggestions.extend([f"Remove violation: {v}" for v in score.violations])

        return MirrorTestResult(
            level=score.resonance,
            confidence=score.alignment,
            reasoning=score.reasoning,
            suggestions=suggestions,
        )

    def drift_check(self, session: SessionState | None = None) -> DriftReport:
        """
        Check for taste drift from historical baseline.

        Drift isn't necessarily bad—taste evolves. But sudden drift
        might indicate loss of authentic voice.

        Args:
            session: Optional session to include in analysis

        Returns:
            DriftReport with drift amount and analysis
        """
        current = self.taste
        if session and session.taste:
            current = session.taste

        drift_amount = current.drift_from(self.baseline)

        dimension_drifts = {
            "darkness": abs(current.darkness - self.baseline.darkness),
            "complexity": abs(current.complexity - self.baseline.complexity),
            "warmth": abs(current.warmth - self.baseline.warmth),
            "energy": abs(current.energy - self.baseline.energy),
            "novelty": abs(current.novelty - self.baseline.novelty),
            "restraint": abs(current.restraint - self.baseline.restraint),
        }

        # Flag concerning drift (threshold: 0.3 on any dimension)
        is_concerning = any(d > 0.3 for d in dimension_drifts.values())

        explanation = self._explain_drift(drift_amount, dimension_drifts)

        return DriftReport(
            baseline=self.baseline,
            current=current,
            drift_amount=drift_amount,
            dimension_drifts=dimension_drifts,
            is_concerning=is_concerning,
            explanation=explanation,
        )

    def evolve(
        self,
        selections: list[tuple[CreativeOption, str]],
        session_id: str = "",
    ) -> TasteVector:
        """
        Evolve taste based on selections.

        Kent's taste isn't static. By analyzing what Kent selects,
        we can refine the taste vector.

        Args:
            selections: List of (selected_option, reason) tuples
            session_id: Session ID for tracking

        Returns:
            Updated TasteVector
        """
        if not selections:
            return self.taste

        # Weight dimensions by selection patterns
        new_taste = TasteVector(
            darkness=self.taste.darkness,
            complexity=self.taste.complexity,
            warmth=self.taste.warmth,
            energy=self.taste.energy,
            novelty=self.taste.novelty,
            restraint=self.taste.restraint,
            never=self.taste.never,
            always=self.taste.always,
        )

        # Adjust based on selected options
        for option, _reason in selections:
            if option.estimated_taste:
                # Move slightly toward selected taste
                learning_rate = 0.1
                new_taste = TasteVector(
                    darkness=new_taste.darkness
                    + learning_rate * (option.estimated_taste.darkness - new_taste.darkness),
                    complexity=new_taste.complexity
                    + learning_rate * (option.estimated_taste.complexity - new_taste.complexity),
                    warmth=new_taste.warmth
                    + learning_rate * (option.estimated_taste.warmth - new_taste.warmth),
                    energy=new_taste.energy
                    + learning_rate * (option.estimated_taste.energy - new_taste.energy),
                    novelty=new_taste.novelty
                    + learning_rate * (option.estimated_taste.novelty - new_taste.novelty),
                    restraint=new_taste.restraint
                    + learning_rate * (option.estimated_taste.restraint - new_taste.restraint),
                    never=new_taste.never,
                    always=new_taste.always,
                )

        # Record evolution
        self.evolution_history.append(
            TasteEvolution(
                session_id=session_id,
                selections=[(o.id, r) for o, r in selections],
                evolved_taste=new_taste,
            )
        )

        self.taste = new_taste
        return new_taste

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _check_violations(self, work: Any) -> list[str]:
        """Check for never/always violations."""
        violations = []

        # This would use actual content analysis in production
        # For now, return empty (no violations detected)
        # In production: analyze work content for presence of 'never' items
        # and absence of 'always' items

        return violations

    def _generate_reasoning(
        self,
        alignment: float,
        dimension_scores: dict[str, float],
        violations: list[str],
    ) -> str:
        """Generate human-readable reasoning for taste evaluation."""
        parts = []

        if alignment >= 0.8:
            parts.append("Strong taste alignment across all dimensions.")
        elif alignment >= 0.5:
            parts.append("Moderate taste alignment with room for refinement.")
        else:
            parts.append("Low taste alignment—significant adjustments needed.")

        # Note high/low dimensions
        high = [k for k, v in dimension_scores.items() if v >= 0.8]
        low = [k for k, v in dimension_scores.items() if v < 0.5]

        if high:
            parts.append(f"Strong alignment: {', '.join(high)}")
        if low:
            parts.append(f"Weak alignment: {', '.join(low)}")

        if violations:
            parts.append(f"Violations: {', '.join(violations)}")

        return " ".join(parts)

    def _explain_drift(
        self,
        drift_amount: float,
        dimension_drifts: dict[str, float],
    ) -> str:
        """Explain drift in human-readable terms."""
        if drift_amount < 0.1:
            return "Minimal drift—taste remains stable."

        drifted = [k for k, v in dimension_drifts.items() if v > 0.1]
        if not drifted:
            return f"Small overall drift ({drift_amount:.2f}) but no single dimension dominates."

        explanations = []
        for dim in drifted:
            delta = dimension_drifts[dim]
            direction = (
                "increased"
                if getattr(self.taste, dim) > getattr(self.baseline, dim)
                else "decreased"
            )
            explanations.append(f"{dim} {direction} by {delta:.2f}")

        return f"Drift detected ({drift_amount:.2f}): {', '.join(explanations)}"

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize agent state."""
        return {
            "taste": self.taste.to_dict(),
            "baseline": self.baseline.to_dict(),
            "evolution_history": [
                {
                    "session_id": e.session_id,
                    "selections": e.selections,
                    "evolved_taste": e.evolved_taste.to_dict(),
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in self.evolution_history
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TasteVectorAgent:
        """Deserialize agent state."""
        agent = cls(
            taste=TasteVector.from_dict(data["taste"]),
            baseline=TasteVector.from_dict(data["baseline"]),
        )
        # Restore evolution history if needed
        return agent


# =============================================================================
# Module-level Functions
# =============================================================================


def create_taste_agent(taste: TasteVector | None = None) -> TasteVectorAgent:
    """Create a new TasteVectorAgent."""
    return TasteVectorAgent(taste=taste)


def get_kent_default_taste() -> TasteVector:
    """Get Kent's default taste vector."""
    return KENT_TASTE_DEFAULT


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Types
    "TasteScore",
    "MirrorTestResult",
    "DriftReport",
    "TasteEvolution",
    # Agent
    "TasteVectorAgent",
    # Functions
    "create_taste_agent",
    "get_kent_default_taste",
]
