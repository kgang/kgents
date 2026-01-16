"""
ContradictorAgent: The Dialectical Challenger.

From muse.md:
    "Challenges Kent's first instinct. Instead of 'Yes, great choice!'
    it asks 'Are you sure? What about...' Forces Kent to justify or
    discover something better."

Contradiction Moves:
- OPPOSITE: "You want dark. What if light?"
- ABSENCE: "You want a hook. What if no hook?"
- PRIOR_KENT: "Last time you rejected this approach. What changed?"
- AUDIENCE: "Your audience expects X. You're giving Y. Intentional?"
- SPECIFICITY: "You said 'melancholy.' What KIND of melancholy?"

See: spec/c-gent/muse.md
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from ..models import (
    Contradiction,
    ContradictionMove,
    DefenseResponse,
    Ghost,
    SessionState,
)

T = TypeVar("T")


# =============================================================================
# Contradiction History and Analytics
# =============================================================================


@dataclass
class ContradictionOutcome:
    """Outcome of a contradiction challenge."""

    contradiction: Contradiction
    response: DefenseResponse
    led_to_breakthrough: bool = False  # Did this lead to better work?
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ContradictionAnalytics:
    """Analytics on contradiction effectiveness."""

    total_contradictions: int = 0
    defenses: int = 0
    pivots: int = 0
    breakthroughs_from_contradiction: int = 0

    @property
    def defense_rate(self) -> float:
        """Rate of defended contradictions."""
        if self.total_contradictions == 0:
            return 0.0
        return self.defenses / self.total_contradictions

    @property
    def pivot_rate(self) -> float:
        """Rate of pivots (discoveries)."""
        if self.total_contradictions == 0:
            return 0.0
        return self.pivots / self.total_contradictions

    @property
    def breakthrough_rate(self) -> float:
        """Rate of breakthroughs from contradiction."""
        if self.pivots == 0:
            return 0.0
        return self.breakthroughs_from_contradiction / self.pivots


@dataclass
class EffectiveContradiction:
    """Record of a contradiction that led to breakthrough."""

    move: ContradictionMove
    target_type: str  # What was being challenged
    session_id: str
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# ContradictorAgent
# =============================================================================


class ContradictorAgent:
    """
    The Dialectical Challenger.

    Every selection deserves challenge. Not to be contrary,
    but to crystallize conviction or discover alternatives.

    The agent:
    1. Generates contradictions using various moves
    2. Tracks which contradictions are effective
    3. Learns from defense/pivot patterns
    4. Champions promising ghosts
    """

    def __init__(self) -> None:
        """Initialize the contradictor."""
        self.outcomes: list[ContradictionOutcome] = []
        self.effective_contradictions: list[EffectiveContradiction] = []
        self.analytics = ContradictionAnalytics()

        # Move weights (learned over time)
        self.move_weights: dict[ContradictionMove, float] = {
            ContradictionMove.OPPOSITE: 1.0,
            ContradictionMove.ABSENCE: 0.8,
            ContradictionMove.PRIOR_KENT: 1.2,
            ContradictionMove.AUDIENCE: 0.9,
            ContradictionMove.SPECIFICITY: 1.1,
        }

    # -------------------------------------------------------------------------
    # Core Operations
    # -------------------------------------------------------------------------

    def contradict(
        self,
        selection: Any,
        session: SessionState[Any] | None = None,
        move: ContradictionMove | None = None,
    ) -> Contradiction:
        """
        Generate a contradiction for a selection.

        Args:
            selection: The thing Kent selected
            session: Session context for prior knowledge
            move: Specific move to use (or None for weighted random)

        Returns:
            Contradiction challenge
        """
        # Choose move
        if move is None:
            move = self._select_move(session)

        # Generate challenge based on move
        challenge = self._generate_challenge(move, selection, session)
        evidence = self._gather_evidence(move, selection, session)

        # Determine strength based on context
        strength = self._calculate_strength(move, session)

        return Contradiction(
            move=move,
            challenge=challenge,
            target=str(selection)[:100],  # Truncate for storage
            evidence=evidence,
            strength=strength,
        )

    def challenge_deviation(
        self,
        deviation: str,
        justification: str,
        session: SessionState[Any] | None = None,
    ) -> Contradiction:
        """
        Challenge a deviation from established patterns.

        Used when Kent does something inconsistent with prior behavior.

        Args:
            deviation: What deviated
            justification: Kent's stated justification
            session: Session context

        Returns:
            Contradiction focused on the inconsistency
        """
        challenge = f"You previously established a pattern. Now you're deviating: {deviation}. You say '{justification}' but last time you rejected similar reasoning. What changed?"

        return Contradiction(
            move=ContradictionMove.PRIOR_KENT,
            challenge=challenge,
            target=deviation,
            evidence=f"Prior pattern: {self._find_prior_pattern(deviation, session)}",
            strength=0.7,
        )

    def record_outcome(
        self,
        contradiction: Contradiction,
        response: DefenseResponse,
        led_to_breakthrough: bool = False,
    ) -> None:
        """
        Record the outcome of a contradiction.

        This feeds learning for future contradictions.

        Args:
            contradiction: The contradiction that was issued
            response: Kent's response (defend or pivot)
            led_to_breakthrough: Whether this led to better work
        """
        outcome = ContradictionOutcome(
            contradiction=contradiction,
            response=response,
            led_to_breakthrough=led_to_breakthrough,
        )
        self.outcomes.append(outcome)

        # Update analytics
        self.analytics.total_contradictions += 1
        if response.defended:
            self.analytics.defenses += 1
        else:
            self.analytics.pivots += 1
            if led_to_breakthrough:
                self.analytics.breakthroughs_from_contradiction += 1
                self.effective_contradictions.append(
                    EffectiveContradiction(
                        move=contradiction.move,
                        target_type=contradiction.target,
                        session_id="",
                    )
                )
                # Increase weight for this move
                self.move_weights[contradiction.move] *= 1.1

    def champion_ghost(
        self,
        ghost: Ghost[Any],
        session: SessionState[Any] | None = None,
    ) -> Contradiction | None:
        """
        Champion a promising ghost that was rejected.

        If AI believes a ghost was unfairly rejected, it can
        bring it back through contradiction.

        Args:
            ghost: The ghost to champion
            session: Session context

        Returns:
            Contradiction championing the ghost, or None if not worth it
        """
        if not ghost.worth_resurrecting:
            return None

        challenge = (
            f"You rejected this option: '{ghost.original_option.description if ghost.original_option else 'unknown'}'. "
            f"Your reason was '{ghost.rejection_reason}'. "
            f"But I think this deserves another look because of its high novelty score ({ghost.original_option.novelty_score if ghost.original_option else 0:.2f}). "
            f"What would need to change for you to reconsider?"
        )

        return Contradiction(
            move=ContradictionMove.OPPOSITE,
            challenge=challenge,
            target="Rejected ghost",
            evidence=f"Rejection strength was only {ghost.rejection_strength:.2f}",
            strength=0.6,
        )

    def get_effective_moves(self, limit: int = 5) -> list[EffectiveContradiction]:
        """Get most effective contradiction patterns."""
        return sorted(
            self.effective_contradictions,
            key=lambda x: x.timestamp,
            reverse=True,
        )[:limit]

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def _select_move(self, session: SessionState[Any] | None) -> ContradictionMove:
        """Select a contradiction move based on weights."""
        moves = list(self.move_weights.keys())
        weights = list(self.move_weights.values())

        # Adjust weights based on session context
        if session:
            # If many defenses recently, try different moves
            recent_outcomes = self.outcomes[-5:] if len(self.outcomes) >= 5 else self.outcomes
            recent_moves = [o.contradiction.move for o in recent_outcomes if o.response.defended]
            for move in recent_moves:
                idx = moves.index(move)
                weights[idx] *= 0.8  # Reduce weight for recently-defended moves

        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]

        return random.choices(moves, weights=weights)[0]

    def _generate_challenge(
        self,
        move: ContradictionMove,
        selection: Any,
        session: SessionState[Any] | None,
    ) -> str:
        """Generate challenge text based on move."""
        selection_str = str(selection)[:50]

        templates = {
            ContradictionMove.OPPOSITE: [
                f"You chose '{selection_str}'. What if the opposite? What would that reveal?",
                "This selection leans one way. What's lost by not going the other direction?",
                "You've committed to this direction. Devil's advocate: what's the case against it?",
            ],
            ContradictionMove.ABSENCE: [
                f"You want '{selection_str}'. What if you removed it entirely? What emerges?",
                "This element exists. What if it didn't? Would anything essential be lost?",
                "The presence of this creates a certain effect. What about its absence?",
            ],
            ContradictionMove.PRIOR_KENT: [
                "In a previous session, you made a different choice in similar circumstances. What's different now?",
                "This contradicts an earlier pattern. Is this evolution or inconsistency?",
                "Your historical preference was different. What changed your mind?",
            ],
            ContradictionMove.AUDIENCE: [
                f"Your audience expects certain things. Does '{selection_str}' meet or subvert those expectations intentionally?",
                "The people you're creating for have assumptions. Are you honoring or challenging them?",
                "Consider the viewer/reader/listener. Is this what serves them, or what serves you?",
            ],
            ContradictionMove.SPECIFICITY: [
                f"You said '{selection_str}'. But what KIND? Can you be more precise?",
                "This is a general choice. What specific variation would make it undeniably yours?",
                "Vagueness is the enemy of taste. What exactly do you mean?",
            ],
        }

        return random.choice(templates[move])

    def _gather_evidence(
        self,
        move: ContradictionMove,
        selection: Any,
        session: SessionState[Any] | None,
    ) -> str:
        """Gather evidence to support the contradiction."""
        if move == ContradictionMove.PRIOR_KENT and session:
            # Look for prior contradictory selections
            return f"Session has {session.iteration} iterations with {len(session.ghosts)} ghosts"

        if move == ContradictionMove.AUDIENCE:
            return "Based on target audience expectations"

        return "Based on dialectical principle"

    def _calculate_strength(
        self,
        move: ContradictionMove,
        session: SessionState[Any] | None,
    ) -> float:
        """Calculate how forceful the contradiction should be."""
        base_strength = 0.5

        # PRIOR_KENT is stronger (calls out inconsistency)
        if move == ContradictionMove.PRIOR_KENT:
            base_strength = 0.7

        # SPECIFICITY is gentler (asking for clarity)
        if move == ContradictionMove.SPECIFICITY:
            base_strength = 0.4

        # Early in session, be gentler
        if session and session.iteration < 10:
            base_strength *= 0.8

        # Late in session, be more forceful
        if session and session.iteration > 30:
            base_strength *= 1.2

        return min(1.0, base_strength)

    def _find_prior_pattern(
        self,
        deviation: str,
        session: SessionState[Any] | None,
    ) -> str:
        """Find prior pattern that was deviated from."""
        if session:
            # Look at prior selections
            return f"Based on {len(session.selections)} prior selections"
        return "Historical pattern"


# =============================================================================
# Module-level Functions
# =============================================================================


def create_contradictor() -> ContradictorAgent:
    """Create a new ContradictorAgent."""
    return ContradictorAgent()


# =============================================================================
# Module Exports
# =============================================================================


__all__ = [
    # Types
    "ContradictionOutcome",
    "ContradictionAnalytics",
    "EffectiveContradiction",
    # Agent
    "ContradictorAgent",
    # Functions
    "create_contradictor",
]
