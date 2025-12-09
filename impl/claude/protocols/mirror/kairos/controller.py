"""
Kairos Controller - Main timing logic and state machine.

Orchestrates attention detection, salience calculation, benefit evaluation,
and budget management to determine opportune moments for surfacing tensions.

From spec/protocols/kairos.md:
  State machine: OBSERVING → EVALUATING → SURFACING/DEFERRING → COOLDOWN
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

from .attention import AttentionDetector, KairosContext
from .benefit import BenefitFunction, TensionEvaluation
from .budget import BudgetLevel, EntropyBudget
from .salience import SalienceCalculator

if TYPE_CHECKING:
    from protocols.mirror.types import Tension


class ControllerState(Enum):
    """State machine states for Kairos controller."""

    OBSERVING = "observing"  # Watching for tensions
    EVALUATING = "evaluating"  # Computing benefit
    SURFACING = "surfacing"  # Presenting tension
    DEFERRING = "deferring"  # Queuing for later
    COOLDOWN = "cooldown"  # Recharging budget


@dataclass
class DeferredTension:
    """A tension queued for later evaluation."""

    tension: Tension
    detected_at: datetime
    defer_reason: str
    min_delay: timedelta
    retry_count: int = 0
    last_evaluated: datetime | None = None


@dataclass
class InterventionRecord:
    """Log of a surfaced tension and user interaction."""

    timestamp: datetime
    tension: Tension
    evaluation: TensionEvaluation
    user_response: str | None = None
    duration_seconds: float | None = None


class KairosController:
    """
    Main controller for opportune moment detection.

    Coordinates all timing logic:
    - Detects attention state from filesystem/git
    - Computes tension salience
    - Evaluates benefit of surfacing
    - Manages entropy budget
    - Maintains deferred tension queue
    - Records intervention history
    """

    def __init__(
        self,
        workspace_path: Path,
        budget_level: BudgetLevel = BudgetLevel.MEDIUM,
        benefit_threshold: float = 0.4,
    ):
        """
        Initialize Kairos controller.

        Args:
            workspace_path: Path to workspace/repository to monitor
            budget_level: Intervention rate limit level
            benefit_threshold: Minimum benefit to surface
        """
        self.workspace_path = workspace_path
        self.state = ControllerState.OBSERVING

        # Core components
        self.attention_detector = AttentionDetector()
        self.salience_calculator = SalienceCalculator()
        self.benefit_function = BenefitFunction(threshold=benefit_threshold)
        self.budget = EntropyBudget(level=budget_level)

        # State
        self.deferred_tensions: dict[str, DeferredTension] = {}
        self.intervention_history: list[InterventionRecord] = []
        self.tension_detected_at: dict[str, datetime] = {}

    def evaluate_timing(
        self,
        tension: Tension,
        momentum_factor: float | None = None,
    ) -> TensionEvaluation:
        """
        Evaluate whether NOW is the right moment to surface tension.

        Args:
            tension: Tension to evaluate
            momentum_factor: Semantic drift velocity (estimated if None)

        Returns:
            TensionEvaluation with surfacing decision
        """
        self.state = ControllerState.EVALUATING

        # Get current context
        context = self.attention_detector.detect_attention_state(
            self.workspace_path,
            recent_interventions=len(self.budget.get_recent_interventions()),
        )

        # Compute salience
        if momentum_factor is None:
            momentum_factor = self.salience_calculator.estimate_momentum_from_tension(
                tension
            )

        detected_at = self.tension_detected_at.get(tension.id)
        salience = self.salience_calculator.compute_salience(
            tension, momentum_factor, detected_at
        )

        # Evaluate benefit
        evaluation = self.benefit_function.evaluate(context, salience)

        # Check budget
        if evaluation.should_surface and not self.budget.can_intervene():
            evaluation.should_surface = False
            evaluation.defer_reason = "budget_exhausted"

        return evaluation

    def surface_tension(
        self,
        tension: Tension,
        evaluation: TensionEvaluation,
    ) -> InterventionRecord:
        """
        Surface a tension to the user.

        Args:
            tension: Tension to surface
            evaluation: Evaluation that approved surfacing

        Returns:
            InterventionRecord for logging
        """
        self.state = ControllerState.SURFACING

        # Consume budget
        self.budget.consume(
            tension_id=tension.id,
            severity=evaluation.severity,
            benefit=evaluation.benefit,
        )

        # Create intervention record
        record = InterventionRecord(
            timestamp=datetime.now(),
            tension=tension,
            evaluation=evaluation,
        )

        self.intervention_history.append(record)

        # Remove from deferred queue if present
        if tension.id in self.deferred_tensions:
            del self.deferred_tensions[tension.id]

        return record

    def defer_tension(
        self,
        tension: Tension,
        reason: str,
        min_delay: timedelta = timedelta(minutes=30),
    ):
        """
        Queue tension for later evaluation.

        Args:
            tension: Tension to defer
            reason: Why deferred
            min_delay: Minimum time before retry
        """
        self.state = ControllerState.DEFERRING

        # Track detection time
        if tension.id not in self.tension_detected_at:
            self.tension_detected_at[tension.id] = datetime.now()

        # Add/update in deferred queue
        if tension.id in self.deferred_tensions:
            deferred = self.deferred_tensions[tension.id]
            deferred.retry_count += 1
            deferred.last_evaluated = datetime.now()
            deferred.defer_reason = reason
        else:
            deferred = DeferredTension(
                tension=tension,
                detected_at=self.tension_detected_at[tension.id],
                defer_reason=reason,
                min_delay=min_delay,
                last_evaluated=datetime.now(),
            )
            self.deferred_tensions[tension.id] = deferred

    def get_next_deferred(self) -> tuple[Tension, float] | None:
        """
        Get next deferred tension ready for re-evaluation.

        Returns:
            Tuple of (tension, age_minutes) or None if queue empty
        """
        now = datetime.now()
        ready = []

        for deferred in self.deferred_tensions.values():
            # Check if min delay has passed
            if deferred.last_evaluated:
                elapsed = now - deferred.last_evaluated
                if elapsed < deferred.min_delay:
                    continue

            # Tension is ready
            age = (now - deferred.detected_at).total_seconds() / 60
            ready.append((deferred.tension, age))

        # Return oldest tension
        if ready:
            return max(ready, key=lambda x: x[1])

        return None

    def force_surface_next(self) -> InterventionRecord | None:
        """
        Force-surface the next deferred tension (override Kairos).

        Used for `kgents mirror surface --next` command.

        Returns:
            InterventionRecord or None if no deferred tensions
        """
        next_tension = self.get_next_deferred()
        if not next_tension:
            return None

        tension, age = next_tension

        # Create evaluation (marked as override)
        evaluation = TensionEvaluation(
            tension_id=tension.id,
            timestamp=datetime.now().isoformat(),
            attention_budget=1.0,  # Override
            salience=1.0,
            cognitive_load=0.0,
            benefit=float("inf"),  # Override
            threshold=0.0,
            should_surface=True,
            defer_reason=None,
            attention_state="OVERRIDE",
            severity="OVERRIDE",
            momentum_factor=1.0,
        )

        return self.surface_tension(tension, evaluation)

    def update_budget(self, elapsed: timedelta):
        """
        Recharge budget based on elapsed time.

        Args:
            elapsed: Time elapsed since last update
        """
        self.state = ControllerState.COOLDOWN
        self.budget.recharge(elapsed)

    def get_current_context(self) -> KairosContext:
        """Get current attention/system context."""
        return self.attention_detector.detect_attention_state(
            self.workspace_path,
            recent_interventions=len(self.budget.get_recent_interventions()),
        )

    def get_intervention_history(
        self, window: timedelta = timedelta(days=7)
    ) -> list[InterventionRecord]:
        """
        Get intervention history within time window.

        Args:
            window: Time window to retrieve

        Returns:
            List of intervention records
        """
        cutoff = datetime.now() - window
        return [
            record for record in self.intervention_history if record.timestamp >= cutoff
        ]

    def record_user_response(
        self, tension_id: str, response: str, duration_seconds: float | None = None
    ):
        """
        Record user's response to an intervention.

        Args:
            tension_id: ID of tension
            response: One of "dismissed", "engaged", "resolved"
            duration_seconds: How long user engaged with tension
        """
        # Update budget log
        self.budget.record_user_response(tension_id, response)

        # Update intervention record
        for record in reversed(self.intervention_history):
            if record.tension.id == tension_id:
                record.user_response = response
                record.duration_seconds = duration_seconds
                break

    def get_status(self) -> dict:
        """
        Get comprehensive controller status.

        Returns:
            Dictionary with current state, budget, queue, etc.
        """
        context = self.get_current_context()

        return {
            "state": self.state.value,
            "timestamp": datetime.now().isoformat(),
            "context": {
                "attention_state": context.attention_state.name,
                "attention_budget": context.attention_budget,
                "cognitive_load": context.cognitive_load,
                "last_activity_age": context.last_activity_age,
                "active_files": context.active_files_count,
            },
            "budget": self.budget.get_status(),
            "deferred_queue": {
                "count": len(self.deferred_tensions),
                "tensions": [
                    {
                        "id": d.tension.id,
                        "detected_at": d.detected_at.isoformat(),
                        "reason": d.defer_reason,
                        "retry_count": d.retry_count,
                    }
                    for d in self.deferred_tensions.values()
                ],
            },
            "history": {
                "total_interventions": len(self.intervention_history),
                "recent_7d": len(self.get_intervention_history()),
            },
        }

    def explain_evaluation(self, evaluation: TensionEvaluation) -> str:
        """Generate explanation for evaluation decision."""
        return self.benefit_function.explain_evaluation(evaluation)
