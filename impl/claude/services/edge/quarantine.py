"""
Nonsense Quarantine: Graceful degradation for incoherent content.

"User may add arbitrary nonsense. Nonsense does not spread. Performance unaffected."

The quarantine system implements Linear design philosophy:
- System adapts to user, not user to system
- Incoherence quarantined, not blocked
- Quarantined content still visible in personal feeds
- Can be refined to exit quarantine

Loss Thresholds (from Grand Strategy):
- loss < 0.5: Coherent
- 0.5 ≤ loss < 0.85: Hand-wavy but tolerable (suggestion given)
- loss ≥ 0.85: Quarantined (likely nonsense)

Philosophy:
    "Never punish. Never lecture. Never block."
    Quarantine gently, with explanation and path to recovery.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class QuarantineEffects(Enum):
    """Effects of quarantine on K-Block behavior."""

    NO_SYSTEM_RANKING = "no_system_ranking"  # Won't affect rankings
    NO_RECOMMENDATIONS = "no_recommendations"  # Won't propagate to recs
    PERSONAL_VISIBLE = "personal_visible"  # Still in personal feeds
    REVERSIBLE = "reversible"  # Can exit via refinement


@dataclass(frozen=True)
class QuarantineDecision:
    """
    Decision about whether to quarantine a K-Block.

    Fields:
        quarantine: Whether to quarantine
        reason: Human-readable reason
        suggestion: Optional suggestion for improvement
        effects: What happens if quarantined
        loss: The Galois loss that triggered the decision
    """

    quarantine: bool
    reason: str
    suggestion: str | None = None
    effects: tuple[QuarantineEffects, ...] = ()
    loss: float | None = None


class NonsenseQuarantine:
    """
    Quarantine system for incoherent content.

    Philosophy:
        The user is sovereign. They may add anything.
        But the system must protect its coherence.

        Strategy: Quarantine gracefully. Don't block, don't shame.
        Show the user what happened and why. Give them a path forward.

    Loss Thresholds:
        LOSS_THRESHOLD = 0.85     # Above this = likely nonsense
        SUGGESTION_THRESHOLD = 0.5 # Above this = suggest improvement

    From plans/zero-seed-genesis-grand-strategy.md:
        "User may add arbitrary nonsense.
         Nonsense does not spread.
         Performance unaffected by incoherent input."
    """

    LOSS_THRESHOLD = 0.85  # Above this = quarantine
    SUGGESTION_THRESHOLD = 0.5  # Above this = suggest improvement

    QUARANTINE_EFFECTS = (
        QuarantineEffects.NO_SYSTEM_RANKING,
        QuarantineEffects.NO_RECOMMENDATIONS,
        QuarantineEffects.PERSONAL_VISIBLE,
        QuarantineEffects.REVERSIBLE,
    )

    def evaluate(self, galois_loss: float, content: str = "") -> QuarantineDecision:
        """
        Evaluate whether to quarantine based on Galois loss.

        Args:
            galois_loss: The Galois loss of the K-Block (0.0-1.0)
            content: Optional content for context

        Returns:
            QuarantineDecision with verdict and suggestions

        Examples:
            >>> quarantine = NonsenseQuarantine()
            >>> # Coherent content
            >>> decision = quarantine.evaluate(0.3)
            >>> assert not decision.quarantine
            >>> # Hand-wavy content
            >>> decision = quarantine.evaluate(0.6)
            >>> assert not decision.quarantine and decision.suggestion
            >>> # Nonsense
            >>> decision = quarantine.evaluate(0.9)
            >>> assert decision.quarantine
        """
        if galois_loss < self.SUGGESTION_THRESHOLD:
            # Coherent - no action needed
            return QuarantineDecision(
                quarantine=False,
                reason="Coherent",
                suggestion=None,
                effects=(),
                loss=galois_loss,
            )

        if galois_loss < self.LOSS_THRESHOLD:
            # Hand-wavy but tolerable - suggest improvement
            return QuarantineDecision(
                quarantine=False,
                reason="Hand-wavy but tolerable",
                suggestion=(
                    f"This content has moderate loss ({galois_loss:.2f}). "
                    "Consider adding more detail, justification, or structure "
                    "to increase coherence."
                ),
                effects=(),
                loss=galois_loss,
            )

        # High loss - quarantine
        return QuarantineDecision(
            quarantine=True,
            reason=f"Very high loss ({galois_loss:.2f}) — quarantined for review",
            suggestion=(
                "This content appears incoherent. It has been quarantined:\n"
                "• It won't affect system-wide rankings\n"
                "• It won't appear in recommendations\n"
                "• It's still visible in your personal feeds\n"
                "• You can refine it to exit quarantine\n\n"
                "No judgment—just protecting the system's coherence while "
                "respecting your sovereignty."
            ),
            effects=self.QUARANTINE_EFFECTS,
            loss=galois_loss,
        )

    def explain_effects(self, effects: tuple[QuarantineEffects, ...]) -> list[str]:
        """
        Convert effects to human-readable descriptions.

        Args:
            effects: Tuple of QuarantineEffects

        Returns:
            List of human-readable effect descriptions
        """
        explanations = {
            QuarantineEffects.NO_SYSTEM_RANKING: "Will not affect system-wide rankings",
            QuarantineEffects.NO_RECOMMENDATIONS: "Will not propagate to recommendations",
            QuarantineEffects.PERSONAL_VISIBLE: "Still visible in your personal feeds",
            QuarantineEffects.REVERSIBLE: "Can be refined to exit quarantine",
        }
        return [explanations[effect] for effect in effects]


def evaluate_for_quarantine(galois_loss: float, content: str = "") -> QuarantineDecision:
    """
    Convenience function for quarantine evaluation.

    Args:
        galois_loss: Galois loss of content
        content: Optional content for context

    Returns:
        QuarantineDecision

    Example:
        >>> decision = evaluate_for_quarantine(0.9)
        >>> assert decision.quarantine
        >>> assert QuarantineEffects.REVERSIBLE in decision.effects
    """
    quarantine = NonsenseQuarantine()
    return quarantine.evaluate(galois_loss, content)
