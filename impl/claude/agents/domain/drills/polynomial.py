"""
CrisisPolynomial: Crisis Response as State Machine.

The crisis polynomial models incident response as a dynamical system:
- NORMAL: Steady state operations
- INCIDENT: Active incident detected
- RESPONSE: Response team engaged
- RECOVERY: Systems being restored

From MIT Sloan: "Modern crises strike without warning or a playbook...
organizations need to develop leaders' real-time adaptability."

The polynomial captures decision points under time pressure.

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Crisis Phase (Positions in the Polynomial)
# =============================================================================


class CrisisPhase(Enum):
    """
    Positions in the crisis polynomial.

    These represent the incident response lifecycle.
    Each phase has different valid actions (directions).
    """

    NORMAL = auto()  # Steady state, monitoring
    INCIDENT = auto()  # Active incident detected
    RESPONSE = auto()  # Response team engaged
    RECOVERY = auto()  # Systems being restored


# =============================================================================
# Input Types (Directions at each Position)
# =============================================================================


@dataclass(frozen=True)
class DetectInput:
    """Input for incident detection."""

    description: str
    severity: str  # critical, high, medium, low
    source: str  # monitoring, user_report, automated, external
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class EscalateInput:
    """Input for escalation."""

    target_role: str  # incident_commander, executive, ciso, etc.
    reason: str
    urgency: str = "high"  # critical, high, normal


@dataclass(frozen=True)
class ContainInput:
    """Input for containment actions."""

    action: str  # isolate, disable, revoke, block
    target: str  # system, account, network, etc.
    scope: str = "targeted"  # targeted, broad, full


@dataclass(frozen=True)
class CommunicateInput:
    """Input for communications."""

    message_type: str  # internal, customer, regulatory, media
    audience: str
    content: str
    approved_by: str | None = None


@dataclass(frozen=True)
class InvestigateInput:
    """Input for investigation actions."""

    action: str  # query_logs, forensics, interview, timeline
    target: str
    findings: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ResolveInput:
    """Input for resolution."""

    action: str  # restore, remediate, patch, workaround
    target: str
    verification: str | None = None


@dataclass(frozen=True)
class RecoverInput:
    """Input for recovery transition."""

    containment_confirmed: bool = True
    systems_stable: bool = True


@dataclass(frozen=True)
class CloseInput:
    """Input for incident closure."""

    postmortem_scheduled: bool = True
    documentation_complete: bool = True
    lessons_captured: list[str] = field(default_factory=list)


class CrisisInput:
    """Factory for crisis inputs."""

    @staticmethod
    def detect(
        description: str,
        severity: str = "high",
        source: str = "monitoring",
    ) -> DetectInput:
        """Create a detection input."""
        return DetectInput(
            description=description,
            severity=severity,
            source=source,
        )

    @staticmethod
    def escalate(
        target_role: str,
        reason: str,
        urgency: str = "high",
    ) -> EscalateInput:
        """Create an escalation input."""
        return EscalateInput(
            target_role=target_role,
            reason=reason,
            urgency=urgency,
        )

    @staticmethod
    def contain(
        action: str,
        target: str,
        scope: str = "targeted",
    ) -> ContainInput:
        """Create a containment input."""
        return ContainInput(action=action, target=target, scope=scope)

    @staticmethod
    def communicate(
        message_type: str,
        audience: str,
        content: str,
        approved_by: str | None = None,
    ) -> CommunicateInput:
        """Create a communication input."""
        return CommunicateInput(
            message_type=message_type,
            audience=audience,
            content=content,
            approved_by=approved_by,
        )

    @staticmethod
    def investigate(
        action: str,
        target: str,
        findings: dict[str, Any] | None = None,
    ) -> InvestigateInput:
        """Create an investigation input."""
        return InvestigateInput(
            action=action,
            target=target,
            findings=findings or {},
        )

    @staticmethod
    def resolve(
        action: str,
        target: str,
        verification: str | None = None,
    ) -> ResolveInput:
        """Create a resolution input."""
        return ResolveInput(action=action, target=target, verification=verification)

    @staticmethod
    def recover(
        containment_confirmed: bool = True,
        systems_stable: bool = True,
    ) -> RecoverInput:
        """Create a recovery input."""
        return RecoverInput(
            containment_confirmed=containment_confirmed,
            systems_stable=systems_stable,
        )

    @staticmethod
    def close(
        postmortem_scheduled: bool = True,
        documentation_complete: bool = True,
        lessons: list[str] | None = None,
    ) -> CloseInput:
        """Create a closure input."""
        return CloseInput(
            postmortem_scheduled=postmortem_scheduled,
            documentation_complete=documentation_complete,
            lessons_captured=lessons or [],
        )


# =============================================================================
# Output Types
# =============================================================================


@dataclass
class CrisisOutput:
    """Output from crisis transitions."""

    phase: CrisisPhase
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    audit_required: bool = False  # Flag for compliance logging


# =============================================================================
# Direction Function (Phase-Dependent Valid Inputs)
# =============================================================================


def crisis_directions(phase: CrisisPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each crisis phase.

    This encodes what actions are appropriate at each stage:
    - NORMAL: Can only detect incidents
    - INCIDENT: Can escalate, investigate, contain, communicate, or transition to response
    - RESPONSE: Full action set, can transition to recovery
    - RECOVERY: Can resolve, communicate, close, or return to normal
    """
    match phase:
        case CrisisPhase.NORMAL:
            return frozenset({DetectInput, type, Any})
        case CrisisPhase.INCIDENT:
            return frozenset(
                {
                    EscalateInput,
                    ContainInput,
                    CommunicateInput,
                    InvestigateInput,
                    RecoverInput,  # Transition to response
                    type,
                    Any,
                }
            )
        case CrisisPhase.RESPONSE:
            return frozenset(
                {
                    EscalateInput,
                    ContainInput,
                    CommunicateInput,
                    InvestigateInput,
                    ResolveInput,
                    RecoverInput,  # Transition to recovery
                    type,
                    Any,
                }
            )
        case CrisisPhase.RECOVERY:
            return frozenset(
                {
                    ResolveInput,
                    CommunicateInput,
                    CloseInput,  # Transition to normal
                    type,
                    Any,
                }
            )
        case _:
            return frozenset({Any})


# =============================================================================
# Transition Function
# =============================================================================


def crisis_transition(
    phase: CrisisPhase, input: Any
) -> tuple[CrisisPhase, CrisisOutput]:
    """
    Crisis state transition function.

    This is the polynomial core:
    transition: Phase x Input -> (NewPhase, Output)

    Key transitions:
    - NORMAL + DetectInput -> INCIDENT
    - INCIDENT + RecoverInput (when ready) -> RESPONSE
    - RESPONSE + RecoverInput (when contained) -> RECOVERY
    - RECOVERY + CloseInput -> NORMAL
    """
    match phase:
        case CrisisPhase.NORMAL:
            if isinstance(input, DetectInput):
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=True,
                    message=f"Incident detected: {input.description}",
                    metadata={
                        "severity": input.severity,
                        "source": input.source,
                        "detected_at": input.timestamp.isoformat(),
                    },
                    audit_required=True,
                )
            else:
                return CrisisPhase.NORMAL, CrisisOutput(
                    phase=CrisisPhase.NORMAL,
                    success=False,
                    message="System in normal state. Only detect inputs valid.",
                )

        case CrisisPhase.INCIDENT:
            if isinstance(input, EscalateInput):
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=True,
                    message=f"Escalated to {input.target_role}: {input.reason}",
                    metadata={
                        "target": input.target_role,
                        "urgency": input.urgency,
                    },
                    audit_required=True,
                )
            elif isinstance(input, ContainInput):
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=True,
                    message=f"Containment action: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "scope": input.scope,
                    },
                    audit_required=True,
                )
            elif isinstance(input, InvestigateInput):
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=True,
                    message=f"Investigation: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "findings": input.findings,
                    },
                )
            elif isinstance(input, CommunicateInput):
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=True,
                    message=f"Communication sent to {input.audience}",
                    metadata={
                        "type": input.message_type,
                        "audience": input.audience,
                        "approved_by": input.approved_by,
                    },
                    audit_required=input.message_type in ("regulatory", "customer"),
                )
            elif isinstance(input, RecoverInput):
                # Transition to RESPONSE phase
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message="Transitioning to active response phase",
                    metadata={
                        "containment_confirmed": input.containment_confirmed,
                        "systems_stable": input.systems_stable,
                    },
                    audit_required=True,
                )
            else:
                return CrisisPhase.INCIDENT, CrisisOutput(
                    phase=CrisisPhase.INCIDENT,
                    success=False,
                    message=f"Invalid action during incident: {type(input).__name__}",
                )

        case CrisisPhase.RESPONSE:
            if isinstance(input, EscalateInput):
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message=f"Escalated to {input.target_role}: {input.reason}",
                    metadata={
                        "target": input.target_role,
                        "urgency": input.urgency,
                    },
                    audit_required=True,
                )
            elif isinstance(input, ContainInput):
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message=f"Containment action: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "scope": input.scope,
                    },
                    audit_required=True,
                )
            elif isinstance(input, InvestigateInput):
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message=f"Investigation: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "findings": input.findings,
                    },
                )
            elif isinstance(input, CommunicateInput):
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message=f"Communication sent to {input.audience}",
                    metadata={
                        "type": input.message_type,
                        "audience": input.audience,
                        "approved_by": input.approved_by,
                    },
                    audit_required=input.message_type in ("regulatory", "customer"),
                )
            elif isinstance(input, ResolveInput):
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=True,
                    message=f"Resolution action: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "verification": input.verification,
                    },
                    audit_required=True,
                )
            elif isinstance(input, RecoverInput):
                if not input.containment_confirmed:
                    return CrisisPhase.RESPONSE, CrisisOutput(
                        phase=CrisisPhase.RESPONSE,
                        success=False,
                        message="Cannot transition to recovery: containment not confirmed",
                    )
                # Transition to RECOVERY phase
                return CrisisPhase.RECOVERY, CrisisOutput(
                    phase=CrisisPhase.RECOVERY,
                    success=True,
                    message="Transitioning to recovery phase",
                    metadata={
                        "containment_confirmed": input.containment_confirmed,
                        "systems_stable": input.systems_stable,
                    },
                    audit_required=True,
                )
            else:
                return CrisisPhase.RESPONSE, CrisisOutput(
                    phase=CrisisPhase.RESPONSE,
                    success=False,
                    message=f"Invalid action during response: {type(input).__name__}",
                )

        case CrisisPhase.RECOVERY:
            if isinstance(input, ResolveInput):
                return CrisisPhase.RECOVERY, CrisisOutput(
                    phase=CrisisPhase.RECOVERY,
                    success=True,
                    message=f"Recovery action: {input.action} on {input.target}",
                    metadata={
                        "action": input.action,
                        "target": input.target,
                        "verification": input.verification,
                    },
                )
            elif isinstance(input, CommunicateInput):
                return CrisisPhase.RECOVERY, CrisisOutput(
                    phase=CrisisPhase.RECOVERY,
                    success=True,
                    message=f"Recovery communication to {input.audience}",
                    metadata={
                        "type": input.message_type,
                        "audience": input.audience,
                    },
                    audit_required=input.message_type in ("regulatory", "customer"),
                )
            elif isinstance(input, CloseInput):
                if not input.postmortem_scheduled:
                    return CrisisPhase.RECOVERY, CrisisOutput(
                        phase=CrisisPhase.RECOVERY,
                        success=False,
                        message="Cannot close: postmortem not scheduled",
                    )
                # Transition back to NORMAL
                return CrisisPhase.NORMAL, CrisisOutput(
                    phase=CrisisPhase.NORMAL,
                    success=True,
                    message="Incident closed. Returning to normal operations.",
                    metadata={
                        "postmortem_scheduled": input.postmortem_scheduled,
                        "documentation_complete": input.documentation_complete,
                        "lessons_captured": input.lessons_captured,
                    },
                    audit_required=True,
                )
            else:
                return CrisisPhase.RECOVERY, CrisisOutput(
                    phase=CrisisPhase.RECOVERY,
                    success=False,
                    message=f"Invalid action during recovery: {type(input).__name__}",
                )

        case _:
            return CrisisPhase.NORMAL, CrisisOutput(
                phase=CrisisPhase.NORMAL,
                success=False,
                message=f"Unknown phase: {phase}",
            )


# =============================================================================
# The Polynomial Agent
# =============================================================================


CRISIS_POLYNOMIAL: PolyAgent[CrisisPhase, Any, CrisisOutput] = PolyAgent(
    name="CrisisPolynomial",
    positions=frozenset(CrisisPhase),
    _directions=crisis_directions,
    _transition=crisis_transition,
)
"""
The Crisis polynomial agent.

This models incident response as a polynomial state machine:
- positions: 4 phases (NORMAL, INCIDENT, RESPONSE, RECOVERY)
- directions: phase-dependent valid actions
- transition: response lifecycle transitions

Key Property:
    Compliance Auditability: All significant transitions set audit_required=True.
"""


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Phase
    "CrisisPhase",
    # Inputs
    "DetectInput",
    "EscalateInput",
    "ContainInput",
    "CommunicateInput",
    "InvestigateInput",
    "ResolveInput",
    "RecoverInput",
    "CloseInput",
    "CrisisInput",
    # Output
    "CrisisOutput",
    # Functions
    "crisis_directions",
    "crisis_transition",
    # Polynomial
    "CRISIS_POLYNOMIAL",
]
