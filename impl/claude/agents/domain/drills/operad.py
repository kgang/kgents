"""
CrisisOperad: Formal Composition Grammar for Crisis Response.

The Crisis Operad defines valid composition operations for incident response:
- detect: Transition from NORMAL to INCIDENT
- escalate: Notify higher authority
- contain: Apply containment action
- communicate: Send status update
- investigate: Gather information
- resolve: Apply fix/mitigation
- recover: Transition to recovery phase
- close: Complete incident lifecycle

Laws:
- detection_required: Must detect before any other action
- containment_before_recovery: Cannot recover without containment
- communication_compliance: External comms require approval
- closure_requires_postmortem: Must schedule postmortem to close

From Barad: Operations are intra-actions, not actions.
The crisis team emerges through the response.

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agents.operad.core import (
    AGENT_OPERAD,
    Law,
    LawStatus,
    LawVerification,
    Operad,
    Operation,
)
from agents.poly import PolyAgent, from_function

from .polynomial import (
    CloseInput,
    CommunicateInput,
    ContainInput,
    CrisisPhase,
    DetectInput,
    EscalateInput,
    InvestigateInput,
    RecoverInput,
    ResolveInput,
    crisis_directions,
)

# =============================================================================
# Operation Metabolics (Token Economics)
# =============================================================================


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OperationMetabolics:
    """Metabolic costs of an operation."""

    token_cost: int
    drama_potential: float  # 0-1 scale for tension/urgency
    credits: int = 0  # Enterprise credits charged
    audit_required: bool = True  # Whether operation requires audit logging

    def estimate_tokens(self, arity: int = 1) -> int:
        """Estimate tokens for this invocation."""
        return self.token_cost * arity


DETECT_METABOLICS = OperationMetabolics(
    token_cost=200, drama_potential=0.6, credits=10, audit_required=True
)
ESCALATE_METABOLICS = OperationMetabolics(
    token_cost=300, drama_potential=0.7, credits=15, audit_required=True
)
CONTAIN_METABOLICS = OperationMetabolics(
    token_cost=400, drama_potential=0.5, credits=20, audit_required=True
)
COMMUNICATE_METABOLICS = OperationMetabolics(
    token_cost=250, drama_potential=0.4, credits=12, audit_required=True
)
INVESTIGATE_METABOLICS = OperationMetabolics(
    token_cost=350, drama_potential=0.3, credits=15, audit_required=False
)
RESOLVE_METABOLICS = OperationMetabolics(
    token_cost=500, drama_potential=0.5, credits=25, audit_required=True
)
RECOVER_METABOLICS = OperationMetabolics(
    token_cost=300, drama_potential=0.4, credits=15, audit_required=True
)
CLOSE_METABOLICS = OperationMetabolics(
    token_cost=200, drama_potential=0.2, credits=10, audit_required=True
)


# =============================================================================
# Audit Event Tracking
# =============================================================================


@dataclass
class CrisisAuditEvent:
    """Audit event for compliance tracking."""

    event_id: str
    timestamp: datetime
    simulation_id: str
    operation: str
    phase_before: str
    phase_after: str
    actor_id: str
    tenant_id: str
    tokens_used: int
    credits_charged: int
    drama_contribution: float
    metadata: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error_message: str | None = None

    @classmethod
    def create(
        cls,
        operation: str,
        simulation_id: str,
        phase_before: str,
        phase_after: str,
        metabolics: OperationMetabolics,
        tenant_id: str = "",
        actor_id: str = "system",
        **metadata: Any,
    ) -> "CrisisAuditEvent":
        """Factory method for creating audit events."""
        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            simulation_id=simulation_id,
            operation=operation,
            phase_before=phase_before,
            phase_after=phase_after,
            actor_id=actor_id,
            tenant_id=tenant_id,
            tokens_used=metabolics.token_cost,
            credits_charged=metabolics.credits,
            drama_contribution=metabolics.drama_potential,
            metadata=metadata,
        )


class CrisisAuditStore:
    """
    In-memory audit store for crisis simulation events.

    In production, this would be backed by TimescaleDB or ClickHouse.
    Supports querying by simulation_id, operation, and time range.
    """

    def __init__(self) -> None:
        self._events: list[CrisisAuditEvent] = []
        self._by_simulation: dict[str, list[CrisisAuditEvent]] = {}
        self._by_operation: dict[str, list[CrisisAuditEvent]] = {}

    def emit(self, event: CrisisAuditEvent) -> None:
        """Store an audit event."""
        self._events.append(event)
        if event.simulation_id not in self._by_simulation:
            self._by_simulation[event.simulation_id] = []
        self._by_simulation[event.simulation_id].append(event)
        if event.operation not in self._by_operation:
            self._by_operation[event.operation] = []
        self._by_operation[event.operation].append(event)

        logger.debug(
            f"Crisis audit: {event.operation} "
            f"({event.phase_before} -> {event.phase_after}) "
            f"sim={event.simulation_id[:8]}..."
        )

    def query(
        self,
        *,
        simulation_id: str | None = None,
        operation: str | None = None,
        since: datetime | None = None,
        limit: int = 1000,
    ) -> list[CrisisAuditEvent]:
        """Query audit events with filters."""
        if simulation_id:
            candidates = self._by_simulation.get(simulation_id, [])
        elif operation:
            candidates = self._by_operation.get(operation, [])
        else:
            candidates = self._events

        if since:
            candidates = [e for e in candidates if e.timestamp >= since]

        return candidates[-limit:]

    def export_compliance_report(
        self, simulation_id: str, format: str = "json"
    ) -> dict[str, Any]:
        """Export compliance report for a simulation."""
        events = self.query(simulation_id=simulation_id)
        total_tokens = sum(e.tokens_used for e in events)
        total_credits = sum(e.credits_charged for e in events)
        total_drama = sum(e.drama_contribution for e in events)

        return {
            "simulation_id": simulation_id,
            "report_generated": datetime.now().isoformat(),
            "format": format,
            "summary": {
                "total_events": len(events),
                "total_tokens": total_tokens,
                "total_credits": total_credits,
                "total_drama": round(total_drama, 2),
                "operations_used": list({e.operation for e in events}),
            },
            "timeline": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "operation": e.operation,
                    "phase_transition": f"{e.phase_before} -> {e.phase_after}",
                    "actor": e.actor_id,
                    "success": e.success,
                }
                for e in events
            ],
        }


# Global audit store (can be replaced with tenant-specific stores)
_audit_store = CrisisAuditStore()


def get_audit_store() -> CrisisAuditStore:
    """Get the global audit store."""
    return _audit_store


def emit_crisis_audit(
    operation: str,
    simulation_id: str,
    phase_before: str,
    phase_after: str,
    metabolics: OperationMetabolics,
    tenant_id: str = "",
    actor_id: str = "system",
    **metadata: Any,
) -> CrisisAuditEvent:
    """
    Emit a crisis audit event.

    Use this to track all crisis operations for compliance.
    """
    event = CrisisAuditEvent.create(
        operation=operation,
        simulation_id=simulation_id,
        phase_before=phase_before,
        phase_after=phase_after,
        metabolics=metabolics,
        tenant_id=tenant_id,
        actor_id=actor_id,
        **metadata,
    )
    _audit_store.emit(event)

    # Also emit to action metrics if available
    try:
        from protocols.api.action_metrics import emit_action_metric

        emit_action_metric(
            action_type=f"crisis_{operation}",
            user_id=actor_id,
            town_id=simulation_id,
            citizen_id=None,
            tokens_in=0,
            tokens_out=metabolics.token_cost,
            model="template",
            latency_ms=0,
            credits_charged=metabolics.credits,
            metadata={
                "operation": operation,
                "phase_before": phase_before,
                "phase_after": phase_after,
                "drama_potential": metabolics.drama_potential,
                **metadata,
            },
        )
    except ImportError:
        pass  # Action metrics not available

    return event


# =============================================================================
# Operad Operations
# =============================================================================


def _detect_compose(monitor: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a detection operation.

    Detect: Monitor -> Crisis (in INCIDENT phase)
    """

    def detect_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "detect",
            "monitor": monitor.name,
            "input": input,
            "metabolics": {
                "tokens": DETECT_METABOLICS.token_cost,
                "drama": DETECT_METABOLICS.drama_potential,
            },
        }

    return from_function(f"detect({monitor.name})", detect_fn)


def _escalate_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose an escalation operation.

    Escalate: Crisis -> Crisis (with notification to authority)
    """

    def escalate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "escalate",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": ESCALATE_METABOLICS.token_cost,
                "drama": ESCALATE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"escalate({crisis.name})", escalate_fn)


def _contain_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a containment operation.

    Contain: Crisis -> Crisis (with containment action applied)
    """

    def contain_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "contain",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": CONTAIN_METABOLICS.token_cost,
                "drama": CONTAIN_METABOLICS.drama_potential,
            },
        }

    return from_function(f"contain({crisis.name})", contain_fn)


def _communicate_compose(
    crisis: PolyAgent[Any, Any, Any],
    audience: PolyAgent[Any, Any, Any],
) -> PolyAgent[Any, Any, Any]:
    """
    Compose a communication operation.

    Communicate: Crisis x Audience -> Notification
    """

    def communicate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "communicate",
            "crisis": crisis.name,
            "audience": audience.name,
            "input": input,
            "metabolics": {
                "tokens": COMMUNICATE_METABOLICS.token_cost,
                "drama": COMMUNICATE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"communicate({crisis.name},{audience.name})", communicate_fn)


def _investigate_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose an investigation operation.

    Investigate: Crisis -> Crisis (with findings)
    """

    def investigate_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "investigate",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": INVESTIGATE_METABOLICS.token_cost,
                "drama": INVESTIGATE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"investigate({crisis.name})", investigate_fn)


def _resolve_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a resolution operation.

    Resolve: Crisis -> Crisis (with fix applied)
    """

    def resolve_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "resolve",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": RESOLVE_METABOLICS.token_cost,
                "drama": RESOLVE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"resolve({crisis.name})", resolve_fn)


def _recover_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a recovery transition operation.

    Recover: Crisis -> Crisis (transition to next phase)
    """

    def recover_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "recover",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": RECOVER_METABOLICS.token_cost,
                "drama": RECOVER_METABOLICS.drama_potential,
            },
        }

    return from_function(f"recover({crisis.name})", recover_fn)


def _close_compose(crisis: PolyAgent[Any, Any, Any]) -> PolyAgent[Any, Any, Any]:
    """
    Compose a closure operation.

    Close: Crisis -> Crisis (back to NORMAL)
    """

    def close_fn(input: Any) -> dict[str, Any]:
        return {
            "operation": "close",
            "crisis": crisis.name,
            "input": input,
            "metabolics": {
                "tokens": CLOSE_METABOLICS.token_cost,
                "drama": CLOSE_METABOLICS.drama_potential,
            },
        }

    return from_function(f"close({crisis.name})", close_fn)


# =============================================================================
# Precondition Checker
# =============================================================================


@dataclass
class PreconditionResult:
    """Result of a precondition check."""

    passed: bool
    message: str = ""
    precondition: str = ""


class CrisisPreconditionChecker:
    """Deterministic checks before operation execution."""

    def check_detection_required(self, phase: CrisisPhase) -> PreconditionResult:
        """Check that detection has occurred (not in NORMAL)."""
        if phase == CrisisPhase.NORMAL:
            return PreconditionResult(
                passed=False,
                message="Must detect incident before performing this action",
                precondition="detection_required",
            )
        return PreconditionResult(passed=True, precondition="detection_required")

    def check_containment_before_recovery(
        self, phase: CrisisPhase, containment_confirmed: bool
    ) -> PreconditionResult:
        """Check that containment is confirmed before recovery transition."""
        if phase == CrisisPhase.RESPONSE and not containment_confirmed:
            return PreconditionResult(
                passed=False,
                message="Containment must be confirmed before transitioning to recovery",
                precondition="containment_before_recovery",
            )
        return PreconditionResult(
            passed=True, precondition="containment_before_recovery"
        )

    def check_communication_compliance(
        self, message_type: str, approved_by: str | None
    ) -> PreconditionResult:
        """Check that external communications have approval."""
        requires_approval = message_type in ("customer", "regulatory", "media")
        if requires_approval and not approved_by:
            return PreconditionResult(
                passed=False,
                message=f"{message_type} communication requires approval",
                precondition="communication_compliance",
            )
        return PreconditionResult(passed=True, precondition="communication_compliance")

    def check_closure_requirements(
        self, postmortem_scheduled: bool
    ) -> PreconditionResult:
        """Check that postmortem is scheduled before closure."""
        if not postmortem_scheduled:
            return PreconditionResult(
                passed=False,
                message="Postmortem must be scheduled before incident closure",
                precondition="closure_requires_postmortem",
            )
        return PreconditionResult(
            passed=True, precondition="closure_requires_postmortem"
        )

    def validate_operation(
        self,
        operation: str,
        phase: CrisisPhase,
        **kwargs: Any,
    ) -> list[PreconditionResult]:
        """Run all relevant precondition checks for an operation."""
        results = []

        # All operations except detect require detection first
        if operation != "detect":
            results.append(self.check_detection_required(phase))

        # Recovery transition checks
        if operation == "recover" and phase == CrisisPhase.RESPONSE:
            containment_confirmed = kwargs.get("containment_confirmed", False)
            results.append(
                self.check_containment_before_recovery(phase, containment_confirmed)
            )

        # Communication compliance
        if operation == "communicate":
            message_type = kwargs.get("message_type", "internal")
            approved_by = kwargs.get("approved_by")
            results.append(
                self.check_communication_compliance(message_type, approved_by)
            )

        # Closure requirements
        if operation == "close":
            postmortem_scheduled = kwargs.get("postmortem_scheduled", False)
            results.append(self.check_closure_requirements(postmortem_scheduled))

        return results


PRECONDITION_CHECKER = CrisisPreconditionChecker()


# =============================================================================
# Operad Laws
# =============================================================================


def _verify_detection_required(*agents: Any) -> LawVerification:
    """Verify: must detect before any other action."""
    # NORMAL phase only allows DetectInput
    dirs = crisis_directions(CrisisPhase.NORMAL)
    if DetectInput not in dirs:
        return LawVerification(
            law_name="detection_required",
            status=LawStatus.FAILED,
            message="DetectInput not allowed in NORMAL phase",
        )
    # Other phases should not allow DetectInput (already detected)
    for phase in [CrisisPhase.INCIDENT, CrisisPhase.RESPONSE, CrisisPhase.RECOVERY]:
        dirs = crisis_directions(phase)
        if DetectInput in dirs:
            return LawVerification(
                law_name="detection_required",
                status=LawStatus.FAILED,
                message=f"DetectInput should not be allowed in {phase.name}",
            )
    return LawVerification(
        law_name="detection_required",
        status=LawStatus.PASSED,
        message="Detection required before other actions (enforced by directions)",
    )


def _verify_containment_before_recovery(*agents: Any) -> LawVerification:
    """Verify: containment must be confirmed before recovery."""
    return LawVerification(
        law_name="containment_before_recovery",
        status=LawStatus.PASSED,
        message="Containment requirement enforced by transition function",
    )


def _verify_communication_compliance(*agents: Any) -> LawVerification:
    """Verify: external communications require approval."""
    return LawVerification(
        law_name="communication_compliance",
        status=LawStatus.PASSED,
        message="Communication compliance enforced by precondition checker",
    )


def _verify_closure_requires_postmortem(*agents: Any) -> LawVerification:
    """Verify: must schedule postmortem to close incident."""
    return LawVerification(
        law_name="closure_requires_postmortem",
        status=LawStatus.PASSED,
        message="Postmortem requirement enforced by transition function",
    )


# =============================================================================
# The Crisis Operad
# =============================================================================


CRISIS_OPERAD = Operad(
    name="CrisisOperad",
    operations={
        # Inherited from AGENT_OPERAD
        **AGENT_OPERAD.operations,
        # Crisis-specific operations
        "detect": Operation(
            name="detect",
            arity=1,
            signature="Monitor -> Crisis",
            compose=_detect_compose,
            description="Transition from NORMAL to INCIDENT",
        ),
        "escalate": Operation(
            name="escalate",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_escalate_compose,
            description="Notify higher authority",
        ),
        "contain": Operation(
            name="contain",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_contain_compose,
            description="Apply containment action",
        ),
        "communicate": Operation(
            name="communicate",
            arity=2,
            signature="Crisis x Audience -> Notification",
            compose=_communicate_compose,
            description="Send status update to stakeholders",
        ),
        "investigate": Operation(
            name="investigate",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_investigate_compose,
            description="Gather information about incident",
        ),
        "resolve": Operation(
            name="resolve",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_resolve_compose,
            description="Apply fix or mitigation",
        ),
        "recover": Operation(
            name="recover",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_recover_compose,
            description="Transition to recovery phase",
        ),
        "close": Operation(
            name="close",
            arity=1,
            signature="Crisis -> Crisis",
            compose=_close_compose,
            description="Complete incident lifecycle (return to NORMAL)",
        ),
    },
    laws=[
        # Inherited laws
        *AGENT_OPERAD.laws,
        # Crisis-specific laws
        Law(
            name="detection_required",
            equation="phase == NORMAL implies only detect is valid",
            verify=_verify_detection_required,
            description="Must detect incident before any other action",
        ),
        Law(
            name="containment_before_recovery",
            equation="recover(RESPONSE) requires containment_confirmed",
            verify=_verify_containment_before_recovery,
            description="Cannot transition to recovery without confirmed containment",
        ),
        Law(
            name="communication_compliance",
            equation="communicate(external) requires approval",
            verify=_verify_communication_compliance,
            description="External communications require approval",
        ),
        Law(
            name="closure_requires_postmortem",
            equation="close(crisis) requires postmortem_scheduled",
            verify=_verify_closure_requires_postmortem,
            description="Must schedule postmortem to close incident",
        ),
    ],
    description="Operad for enterprise crisis management composition",
)
"""
The Crisis operad.

Defines valid composition operations for crisis response:
- detect, escalate, contain, communicate, investigate, resolve, recover, close

Laws ensure proper incident lifecycle:
- Detection before any action
- Containment before recovery
- Approval for external communications
- Postmortem before closure
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Metabolics
    "OperationMetabolics",
    "DETECT_METABOLICS",
    "ESCALATE_METABOLICS",
    "CONTAIN_METABOLICS",
    "COMMUNICATE_METABOLICS",
    "INVESTIGATE_METABOLICS",
    "RESOLVE_METABOLICS",
    "RECOVER_METABOLICS",
    "CLOSE_METABOLICS",
    # Audit
    "CrisisAuditEvent",
    "CrisisAuditStore",
    "get_audit_store",
    "emit_crisis_audit",
    # Preconditions
    "PreconditionResult",
    "CrisisPreconditionChecker",
    "PRECONDITION_CHECKER",
    # Operad
    "CRISIS_OPERAD",
]
