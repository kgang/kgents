"""
Benefit Function - Determine if NOW is the right moment to surface.

Computes benefit of surfacing a tension at moment t:
  B(t) = A(t) × S(t) / (1 + L(t))

Where:
- A(t): Attention budget (user availability)
- S(t): Tension salience (urgency)
- L(t): Cognitive load (cost of interruption)

Higher benefit = better moment to surface.

From spec/protocols/kairos.md (corrected cost function).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .attention import KairosContext
    from .salience import TensionSalience


@dataclass
class TensionEvaluation:
    """
    Evaluation result for surfacing decision.

    Contains all factors that went into the timing decision,
    for transparency and debugging.
    """

    tension_id: str
    timestamp: str  # ISO format

    # Input factors
    attention_budget: float  # A(t)
    salience: float  # S(t)
    cognitive_load: float  # L(t)

    # Computed benefit
    benefit: float  # B(t)
    threshold: float  # Decision boundary

    # Decision
    should_surface: bool
    defer_reason: str | None  # Why deferred (if applicable)

    # Additional context
    attention_state: str  # Human-readable state name
    severity: str  # Human-readable severity
    momentum_factor: float


class BenefitFunction:
    """
    Computes benefit of surfacing a tension at moment t.

    The benefit function balances:
    1. User availability (attention budget)
    2. Tension urgency (salience)
    3. Interruption cost (cognitive load)

    Surface when: B(t) > threshold AND budget available
    """

    def __init__(
        self,
        threshold: float = 0.4,
        min_attention: float = 0.1,
    ):
        """
        Initialize benefit function.

        Args:
            threshold: Minimum benefit required to surface (0.0-1.0)
            min_attention: Minimum attention budget to ever surface
        """
        self.threshold = threshold
        self.min_attention = min_attention

    def evaluate(
        self,
        context: KairosContext,
        salience: TensionSalience,
    ) -> TensionEvaluation:
        """
        Evaluate whether NOW is the right moment to surface tension.

        Args:
            context: Current attention/system state
            salience: Computed urgency of tension

        Returns:
            TensionEvaluation with decision and reasoning
        """
        # Extract factors
        A_t = context.attention_budget
        S_t = salience.salience
        L_t = context.cognitive_load

        # Compute benefit: B(t) = A(t) × S(t) / (1 + L(t))
        benefit = (A_t * S_t) / (1.0 + L_t)

        # Determine if should surface
        should_surface = False
        defer_reason = None

        if A_t < self.min_attention:
            defer_reason = "insufficient_attention"
        elif benefit < self.threshold:
            defer_reason = "benefit_below_threshold"
        else:
            should_surface = True

        # Emergency override for critical + accelerating tensions
        if salience.base_severity.name == "CRITICAL" and salience.momentum_factor > 2.0:
            should_surface = True
            defer_reason = None

        return TensionEvaluation(
            tension_id=salience.tension_id,
            timestamp=context.timestamp.isoformat(),
            attention_budget=A_t,
            salience=S_t,
            cognitive_load=L_t,
            benefit=benefit,
            threshold=self.threshold,
            should_surface=should_surface,
            defer_reason=defer_reason,
            attention_state=context.attention_state.name,
            severity=salience.base_severity.name,
            momentum_factor=salience.momentum_factor,
        )

    def explain_evaluation(self, evaluation: TensionEvaluation) -> str:
        """
        Generate human-readable explanation of evaluation.

        Used for --explain flag in CLI.
        """
        lines = [
            f"Tension: {evaluation.tension_id}",
            f"Timestamp: {evaluation.timestamp}",
            "",
            "Input Factors:",
            f"  Attention Budget: {evaluation.attention_budget:.2f} ({evaluation.attention_state})",
            f"  Salience: {evaluation.salience:.2f} ({evaluation.severity}, momentum={evaluation.momentum_factor:.2f})",
            f"  Cognitive Load: {evaluation.cognitive_load:.2f}",
            "",
            "Computation:",
            f"  B(t) = {evaluation.attention_budget:.2f} × {evaluation.salience:.2f} / (1 + {evaluation.cognitive_load:.2f})",
            f"       = {evaluation.benefit:.2f}",
            f"  Threshold = {evaluation.threshold:.2f}",
            "",
            "Decision:",
        ]

        if evaluation.should_surface:
            lines.append(
                f"  ✓ SURFACE (B(t) = {evaluation.benefit:.2f} > {evaluation.threshold:.2f})"
            )
        else:
            reason_text = {
                "insufficient_attention": "User attention too low",
                "benefit_below_threshold": "Benefit below threshold",
            }.get(evaluation.defer_reason, evaluation.defer_reason)
            lines.append(f"  ✗ DEFER: {reason_text}")
            lines.append(
                f"    (B(t) = {evaluation.benefit:.2f} {'<' if evaluation.benefit < evaluation.threshold else '≥'} {evaluation.threshold:.2f})"
            )

        return "\n".join(lines)

    def compute_optimal_threshold(
        self,
        evaluations: list[TensionEvaluation],
        target_surface_rate: float = 0.2,
    ) -> float:
        """
        Compute optimal threshold from historical evaluations.

        Used for Phase 3b: learning personalized timing.

        Args:
            evaluations: Historical evaluation results
            target_surface_rate: Desired fraction of tensions to surface

        Returns:
            Optimal threshold that achieves target surface rate
        """
        if not evaluations:
            return self.threshold

        # Extract benefits and sort
        benefits = sorted([e.benefit for e in evaluations], reverse=True)

        # Find threshold that achieves target surface rate
        target_index = int(len(benefits) * target_surface_rate)
        if target_index >= len(benefits):
            target_index = len(benefits) - 1

        return benefits[target_index]
