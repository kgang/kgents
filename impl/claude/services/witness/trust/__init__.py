"""
Witness Trust System: Earned Autonomy Through Demonstrated Competence.

"Trust is not given. Trust is earned through accurate observation and successful action."

This module implements the trust escalation model for the 8th Crown Jewel:

Trust Levels:
    L0 READ_ONLY   - Observe and project, no modifications
    L1 BOUNDED     - Write to .kgents/ directory only
    L2 SUGGESTION  - Propose changes, require human confirmation
    L3 AUTONOMOUS  - Full Kent-equivalent developer agency

Escalation Triggers:
    L0 → L1: 100+ observations over 24h with <1% false positive rate
    L1 → L2: 100+ successful bounded operations with <5% failure rate
    L2 → L3: 50+ confirmed suggestions with >90% acceptance rate

Key Components:
    - ActionGate: Trust-gated execution (ALLOW, DENY, CONFIRM, LOG)
    - EscalationCriteria: Criteria for each level transition
    - BoundaryChecker: Forbidden action detection
    - ConfirmationManager: L2 suggestion confirmation flow

Philosophy (from spec/principles.md):
    "The Mirror Test: Does K-gent feel like me on my best day?"
    A good developer earns trust through track record, not grant.

See: plans/kgentsd-trust-system.md
See: docs/skills/crown-jewel-patterns.md
"""

from .boundaries import (
    FORBIDDEN_ACTIONS,
    BoundaryChecker,
    BoundaryViolation,
)
from .confirmation import (
    ConfirmationManager,
    ConfirmationResult,
    PendingSuggestion,
)
from .escalation import (
    EscalationCriteria,
    EscalationResult as EscalationCheckResult,
    Level1Criteria,
    Level2Criteria,
    Level3Criteria,
    ObservationStats,
    OperationStats,
    SuggestionStats,
    check_escalation,
)
from .gate import (
    ActionGate,
    GateDecision,
    GateResult,
)

# Trust Polynomial Functor (Amendment E)
from .gradient import (
    Action as TrustAction,
    ApprovalRequired,
    Autonomous,
    HighImpactOnly,
    MostApproved,
    RoutineApproved,
    TrustLevel as TrustGradientLevel,
    TrustState,
    can_execute_autonomously,
    create_trust_state,
    high_risk_action,
    low_risk_action,
    medium_risk_action,
    requires_approval,
    trivial_action,
)

__all__ = [
    # Gate
    "ActionGate",
    "GateDecision",
    "GateResult",
    # Escalation
    "EscalationCriteria",
    "EscalationCheckResult",
    "Level1Criteria",
    "Level2Criteria",
    "Level3Criteria",
    "ObservationStats",
    "OperationStats",
    "SuggestionStats",
    "check_escalation",
    # Boundaries
    "BoundaryChecker",
    "BoundaryViolation",
    "FORBIDDEN_ACTIONS",
    # Confirmation
    "ConfirmationManager",
    "PendingSuggestion",
    "ConfirmationResult",
    # Trust Polynomial Functor (Amendment E)
    "TrustGradientLevel",
    "TrustState",
    "TrustAction",
    "can_execute_autonomously",
    "requires_approval",
    "create_trust_state",
    "trivial_action",
    "low_risk_action",
    "medium_risk_action",
    "high_risk_action",
    "ApprovalRequired",
    "RoutineApproved",
    "MostApproved",
    "HighImpactOnly",
    "Autonomous",
]
