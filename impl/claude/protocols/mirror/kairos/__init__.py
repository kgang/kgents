"""
Kairos Protocol Implementation - Opportune Moment Detection.

This module implements Phase 3 of the Mirror Protocol: determining the right
moment to surface tensions based on user attention state, tension salience,
and entropy budgets.

From spec/protocols/kairos.md:
  καιρός (kairos): the right, critical, or opportune moment

Core Components:
- AttentionDetector: Filesystem/git activity → AttentionState
- SalienceCalculator: Tension urgency with momentum
- BenefitFunction: B(t) = A(t) × S(t) / (1 + L(t))
- EntropyBudget: Rate limiting for intervention fatigue prevention
- KairosController: Main timing logic and state machine
- WatchMode: Autonomous observation loop

Usage:
    from protocols.mirror.kairos import KairosController, BudgetLevel

    controller = KairosController(budget=BudgetLevel.MEDIUM)
    evaluation = controller.evaluate_timing(tension, context, momentum)

    if evaluation.should_surface:
        controller.surface_tension(tension)
"""

from .attention import AttentionDetector, AttentionState, KairosContext
from .salience import SalienceCalculator, TensionSeverity
from .benefit import BenefitFunction, TensionEvaluation
from .budget import EntropyBudget, BudgetLevel
from .controller import KairosController, InterventionRecord
from .watch import watch_loop

__all__ = [
    "AttentionDetector",
    "AttentionState",
    "KairosContext",
    "SalienceCalculator",
    "TensionSeverity",
    "BenefitFunction",
    "TensionEvaluation",
    "EntropyBudget",
    "BudgetLevel",
    "KairosController",
    "InterventionRecord",
    "watch_loop",
]
