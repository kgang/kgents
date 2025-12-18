"""
Season Transitions: Auto-Inducer for Gardener-Logos.

The garden should automatically suggest season transitions based on
activity signals. This makes the garden feel alive and responsive.

Transition Rules:
- DORMANT → SPROUTING: Activity detected after rest
- SPROUTING → BLOOMING: Ideas are crystallizing
- BLOOMING → HARVEST: Time to gather results
- HARVEST → COMPOSTING: Gathering complete, time to break down
- COMPOSTING → DORMANT: Decomposition complete, rest needed

See: spec/protocols/gardener-logos.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Callable

from .garden import GardenSeason

if TYPE_CHECKING:
    from .garden import GardenState
    from .tending import TendingGesture


@dataclass(frozen=True)
class TransitionSignals:
    """
    Signals gathered from garden state to evaluate transitions.

    These signals measure the garden's activity patterns and help
    determine when season transitions should be suggested.
    """

    # Activity signals
    gesture_frequency: float  # Gestures per hour
    gesture_diversity: int  # Unique verbs used recently

    # Progress signals
    plot_progress_delta: float  # Change since season start (0-1)
    artifacts_created: int  # Session artifacts count

    # Time signals
    time_in_season_hours: float  # Hours in current season

    # Entropy signals
    entropy_spent_ratio: float  # spent / budget (0-1)

    # Session signals
    reflect_count: int  # Number of REFLECT cycles completed
    session_active: bool  # Whether there's an active session

    @classmethod
    def gather(cls, garden: "GardenState") -> "TransitionSignals":
        """
        Gather transition signals from garden state.

        Args:
            garden: The garden to analyze

        Returns:
            TransitionSignals with computed metrics
        """
        now = datetime.now()

        # Calculate time in current season
        time_in_season = now - garden.season_since
        time_in_season_hours = time_in_season.total_seconds() / 3600

        # Calculate gesture frequency (gestures per hour in last 24h)
        recent_gestures = [g for g in garden.recent_gestures if g.is_recent(hours=24)]

        if time_in_season_hours > 0:
            # Use min of time in season or 24h for frequency calc
            period_hours = min(time_in_season_hours, 24.0)
            gestures_in_period = len(
                [
                    g
                    for g in garden.recent_gestures
                    if (now - g.timestamp).total_seconds() / 3600 <= period_hours
                ]
            )
            gesture_frequency = gestures_in_period / max(period_hours, 0.1)
        else:
            gesture_frequency = 0.0

        # Calculate gesture diversity (unique verbs in recent gestures)
        recent_verbs = {g.verb for g in recent_gestures}
        gesture_diversity = len(recent_verbs)

        # Calculate plot progress delta (average progress change)
        # This is a simplified metric - real impl would track baseline
        total_progress = sum(plot.progress for plot in garden.plots.values())
        num_plots = len(garden.plots) or 1
        avg_progress = total_progress / num_plots
        plot_progress_delta = avg_progress  # Simplified: use current as delta proxy

        # Entropy ratio
        metrics = garden.metrics
        entropy_budget = max(metrics.entropy_budget, 0.01)  # Avoid div by zero
        entropy_spent_ratio = min(1.0, metrics.entropy_spent / entropy_budget)

        # Session signals
        session_active = garden.session is not None
        reflect_count = 0
        artifacts_created = 0

        if garden.session is not None:
            reflect_count = getattr(garden.session.state, "reflect_count", 0)
            artifacts = getattr(garden.session.state, "artifacts", [])
            artifacts_created = len(artifacts)

        return cls(
            gesture_frequency=gesture_frequency,
            gesture_diversity=gesture_diversity,
            plot_progress_delta=plot_progress_delta,
            artifacts_created=artifacts_created,
            time_in_season_hours=time_in_season_hours,
            entropy_spent_ratio=entropy_spent_ratio,
            reflect_count=reflect_count,
            session_active=session_active,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/debugging."""
        return {
            "gesture_frequency": round(self.gesture_frequency, 2),
            "gesture_diversity": self.gesture_diversity,
            "plot_progress_delta": round(self.plot_progress_delta, 3),
            "artifacts_created": self.artifacts_created,
            "time_in_season_hours": round(self.time_in_season_hours, 2),
            "entropy_spent_ratio": round(self.entropy_spent_ratio, 3),
            "reflect_count": self.reflect_count,
            "session_active": self.session_active,
        }


@dataclass(frozen=True)
class SeasonTransition:
    """
    A suggested season transition.

    Transitions are suggested, not auto-applied. The user confirms
    whether to accept the transition.
    """

    from_season: GardenSeason
    to_season: GardenSeason
    confidence: float  # 0-1, suggestion threshold is 0.7
    reason: str
    signals: TransitionSignals
    triggered_at: datetime = field(default_factory=datetime.now)

    @property
    def should_suggest(self) -> bool:
        """Whether this transition should be suggested (confidence > 0.7)."""
        return self.confidence >= 0.7

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API."""
        return {
            "from_season": self.from_season.name,
            "to_season": self.to_season.name,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "signals": self.signals.to_dict(),
            "triggered_at": self.triggered_at.isoformat(),
        }


# =============================================================================
# Transition Rules
# =============================================================================

# Each rule: (from_season, to_season, evaluator_function)
# Evaluator returns (confidence: float, reason: str)


def _eval_dormant_to_sprouting(signals: TransitionSignals) -> tuple[float, str]:
    """
    DORMANT → SPROUTING
    When: gesture_frequency > 2/hour AND entropy_spent_ratio < 0.5
    Why: Activity detected after rest
    """
    confidence = 0.0
    reasons = []

    # Primary trigger: activity after rest
    if signals.gesture_frequency > 2.0:
        confidence += 0.5
        reasons.append(f"High activity ({signals.gesture_frequency:.1f} gestures/hour)")
    elif signals.gesture_frequency > 1.0:
        confidence += 0.3
        reasons.append(f"Moderate activity ({signals.gesture_frequency:.1f} gestures/hour)")

    # Must have entropy to grow
    if signals.entropy_spent_ratio < 0.5:
        confidence += 0.3
        reasons.append(
            f"Entropy available ({(1 - signals.entropy_spent_ratio) * 100:.0f}% remaining)"
        )
    elif signals.entropy_spent_ratio < 0.7:
        confidence += 0.15
        reasons.append("Some entropy available")

    # Bonus: session started
    if signals.session_active:
        confidence += 0.2
        reasons.append("Session active")

    # Penalty: been dormant too long might indicate intentional rest
    if signals.time_in_season_hours > 48:
        confidence -= 0.2
        reasons.append("Extended dormancy (intentional rest?)")

    reason = "; ".join(reasons) if reasons else "Insufficient activity"
    return min(1.0, confidence), reason


def _eval_sprouting_to_blooming(signals: TransitionSignals) -> tuple[float, str]:
    """
    SPROUTING → BLOOMING
    When: plot_progress_delta > 0.2 AND time_in_season > 2 hours
    Why: Ideas are crystallizing
    """
    confidence = 0.0
    reasons = []

    # Primary trigger: progress being made
    if signals.plot_progress_delta > 0.3:
        confidence += 0.5
        reasons.append(f"Strong progress ({signals.plot_progress_delta * 100:.0f}%)")
    elif signals.plot_progress_delta > 0.2:
        confidence += 0.4
        reasons.append(f"Good progress ({signals.plot_progress_delta * 100:.0f}%)")
    elif signals.plot_progress_delta > 0.1:
        confidence += 0.2
        reasons.append(f"Some progress ({signals.plot_progress_delta * 100:.0f}%)")

    # Time requirement: ideas need time to form
    if signals.time_in_season_hours >= 2.0:
        confidence += 0.3
        reasons.append(f"Sufficient time in sprouting ({signals.time_in_season_hours:.1f}h)")
    elif signals.time_in_season_hours >= 1.0:
        confidence += 0.15
        reasons.append("Some time in sprouting")

    # Bonus: gesture diversity shows exploration
    if signals.gesture_diversity >= 4:
        confidence += 0.2
        reasons.append(f"Diverse gestures ({signals.gesture_diversity} types)")
    elif signals.gesture_diversity >= 3:
        confidence += 0.1
        reasons.append("Varied gestures")

    reason = "; ".join(reasons) if reasons else "Ideas still forming"
    return min(1.0, confidence), reason


def _eval_blooming_to_harvest(signals: TransitionSignals) -> tuple[float, str]:
    """
    BLOOMING → HARVEST
    When: session.reflect_count >= 3 OR artifacts_created > 5
    Why: Time to gather results
    """
    confidence = 0.0
    reasons = []

    # Primary trigger: reflection cycles completed
    if signals.reflect_count >= 3:
        confidence += 0.5
        reasons.append(f"Multiple reflect cycles ({signals.reflect_count})")
    elif signals.reflect_count >= 2:
        confidence += 0.3
        reasons.append(f"Some reflection ({signals.reflect_count} cycles)")
    elif signals.reflect_count >= 1:
        confidence += 0.15
        reasons.append("At least one reflection")

    # Alternative trigger: artifacts created
    if signals.artifacts_created > 5:
        confidence += 0.4
        reasons.append(f"Many artifacts ({signals.artifacts_created})")
    elif signals.artifacts_created > 2:
        confidence += 0.25
        reasons.append(f"Some artifacts ({signals.artifacts_created})")

    # Time bonus: blooming has matured
    if signals.time_in_season_hours >= 3.0:
        confidence += 0.2
        reasons.append(f"Bloom matured ({signals.time_in_season_hours:.1f}h)")

    reason = "; ".join(reasons) if reasons else "Work not yet ready for harvest"
    return min(1.0, confidence), reason


def _eval_harvest_to_composting(signals: TransitionSignals) -> tuple[float, str]:
    """
    HARVEST → COMPOSTING
    When: time_in_season > 4 hours AND gesture_frequency < 1/hour
    Why: Gathering complete, time to break down
    """
    confidence = 0.0
    reasons = []

    # Primary trigger: time in harvest
    if signals.time_in_season_hours > 4.0:
        confidence += 0.5
        reasons.append(f"Extended harvest ({signals.time_in_season_hours:.1f}h)")
    elif signals.time_in_season_hours > 2.0:
        confidence += 0.3
        reasons.append(f"Harvest underway ({signals.time_in_season_hours:.1f}h)")

    # Secondary trigger: activity slowing
    if signals.gesture_frequency < 0.5:
        confidence += 0.4
        reasons.append(f"Low activity ({signals.gesture_frequency:.1f}/h)")
    elif signals.gesture_frequency < 1.0:
        confidence += 0.25
        reasons.append(f"Declining activity ({signals.gesture_frequency:.1f}/h)")

    # Entropy signal: much was consumed
    if signals.entropy_spent_ratio > 0.6:
        confidence += 0.15
        reasons.append("Significant entropy consumed")

    reason = "; ".join(reasons) if reasons else "Still harvesting"
    return min(1.0, confidence), reason


def _eval_composting_to_dormant(signals: TransitionSignals) -> tuple[float, str]:
    """
    COMPOSTING → DORMANT
    When: entropy_spent_ratio > 0.8 OR time_in_season > 6 hours
    Why: Decomposition complete, rest needed
    """
    confidence = 0.0
    reasons = []

    # Primary trigger: entropy exhausted
    if signals.entropy_spent_ratio > 0.8:
        confidence += 0.6
        reasons.append(f"Entropy depleted ({signals.entropy_spent_ratio * 100:.0f}% used)")
    elif signals.entropy_spent_ratio > 0.6:
        confidence += 0.35
        reasons.append(f"Entropy running low ({signals.entropy_spent_ratio * 100:.0f}% used)")

    # Time trigger: composting complete
    if signals.time_in_season_hours > 6.0:
        confidence += 0.4
        reasons.append(f"Composting complete ({signals.time_in_season_hours:.1f}h)")
    elif signals.time_in_season_hours > 3.0:
        confidence += 0.2
        reasons.append(f"Composting underway ({signals.time_in_season_hours:.1f}h)")

    # Activity very low
    if signals.gesture_frequency < 0.3:
        confidence += 0.15
        reasons.append("Minimal activity")

    reason = "; ".join(reasons) if reasons else "Still composting"
    return min(1.0, confidence), reason


# Map seasons to their transition evaluators
# TransitionEvaluator = Callable taking GardenState and returning (confidence, reason)
TransitionEvaluator = Callable[["GardenState"], tuple[float, str]]
TRANSITION_RULES: dict[GardenSeason, list[tuple[GardenSeason, TransitionEvaluator]]] = {
    GardenSeason.DORMANT: [
        (GardenSeason.SPROUTING, _eval_dormant_to_sprouting),
    ],
    GardenSeason.SPROUTING: [
        (GardenSeason.BLOOMING, _eval_sprouting_to_blooming),
    ],
    GardenSeason.BLOOMING: [
        (GardenSeason.HARVEST, _eval_blooming_to_harvest),
    ],
    GardenSeason.HARVEST: [
        (GardenSeason.COMPOSTING, _eval_harvest_to_composting),
    ],
    GardenSeason.COMPOSTING: [
        (GardenSeason.DORMANT, _eval_composting_to_dormant),
    ],
}


# =============================================================================
# Main Evaluation Function
# =============================================================================


def evaluate_season_transition(
    garden: "GardenState",
    *,
    signals: TransitionSignals | None = None,
) -> SeasonTransition | None:
    """
    Evaluate whether the garden should transition to a new season.

    Gathers signals from the garden state and evaluates each possible
    transition from the current season. Returns the highest-confidence
    transition if one exceeds the suggestion threshold (0.7).

    Args:
        garden: The garden to evaluate
        signals: Pre-computed signals (gathered if not provided)

    Returns:
        SeasonTransition if a suggestion should be made, None otherwise
    """
    # Gather signals if not provided
    if signals is None:
        signals = TransitionSignals.gather(garden)

    current_season = garden.season

    # Get possible transitions from current season
    possible_transitions = TRANSITION_RULES.get(current_season, [])

    if not possible_transitions:
        return None

    # Evaluate each possible transition
    best_transition: SeasonTransition | None = None
    best_confidence = 0.0

    for to_season, evaluator in possible_transitions:
        confidence, reason = evaluator(signals)

        if confidence > best_confidence:
            best_confidence = confidence
            best_transition = SeasonTransition(
                from_season=current_season,
                to_season=to_season,
                confidence=confidence,
                reason=reason,
                signals=signals,
            )

    # Only return if meets suggestion threshold
    if best_transition and best_transition.should_suggest:
        return best_transition

    return None


# =============================================================================
# Dismissal Memory
# =============================================================================

# Simple in-memory dismissal tracking
# Key: (garden_id, from_season, to_season), Value: datetime of dismissal
_dismissed_transitions: dict[tuple[str, str, str], datetime] = {}
_DISMISSAL_COOLDOWN_HOURS = 4  # Don't re-suggest dismissed for N hours


def dismiss_transition(
    garden_id: str,
    from_season: GardenSeason,
    to_season: GardenSeason,
) -> None:
    """
    Record that a transition suggestion was dismissed.

    The same transition won't be suggested again for DISMISSAL_COOLDOWN_HOURS.

    Args:
        garden_id: ID of the garden
        from_season: Season being transitioned from
        to_season: Season being transitioned to
    """
    key = (garden_id, from_season.name, to_season.name)
    _dismissed_transitions[key] = datetime.now()


def is_transition_dismissed(
    garden_id: str,
    from_season: GardenSeason,
    to_season: GardenSeason,
) -> bool:
    """
    Check if a transition was recently dismissed.

    Args:
        garden_id: ID of the garden
        from_season: Season being transitioned from
        to_season: Season being transitioned to

    Returns:
        True if transition was dismissed within cooldown period
    """
    key = (garden_id, from_season.name, to_season.name)
    dismissed_at = _dismissed_transitions.get(key)

    if dismissed_at is None:
        return False

    cooldown = timedelta(hours=_DISMISSAL_COOLDOWN_HOURS)
    return datetime.now() - dismissed_at < cooldown


def clear_dismissals(garden_id: str) -> None:
    """Clear all dismissals for a garden."""
    keys_to_remove = [k for k in _dismissed_transitions if k[0] == garden_id]
    for key in keys_to_remove:
        del _dismissed_transitions[key]


# =============================================================================
# Combined Evaluation with Dismissal Check
# =============================================================================


def suggest_season_transition(
    garden: "GardenState",
) -> SeasonTransition | None:
    """
    Suggest a season transition, respecting dismissal memory.

    This is the main entry point for the auto-inducer. It:
    1. Gathers signals from garden state
    2. Evaluates possible transitions
    3. Filters out recently dismissed transitions
    4. Returns the best suggestion (if any)

    Args:
        garden: The garden to evaluate

    Returns:
        SeasonTransition suggestion, or None if no suggestion
    """
    transition = evaluate_season_transition(garden)

    if transition is None:
        return None

    # Check if this transition was recently dismissed
    if is_transition_dismissed(
        garden.garden_id,
        transition.from_season,
        transition.to_season,
    ):
        return None

    return transition


__all__ = [
    "TransitionSignals",
    "SeasonTransition",
    "evaluate_season_transition",
    "suggest_season_transition",
    "dismiss_transition",
    "is_transition_dismissed",
    "clear_dismissals",
    "TRANSITION_RULES",
]
