"""
Inject Framework: Runtime Crisis Escalation Events.

From MIT Sloan: "Organizations need to develop leaders' real-time adaptability.
Drills must surprise, not just confirm."

Injects are runtime events that increase pressure or complexity:
- MediaStory: External media publishes breach story
- ExecutiveCall: Board or executive demands update
- RegulatorInquiry: Regulatory body requests information
- CustomerEscalation: Major customer threatens to leave
- TechnicalComplication: Secondary system failure
- PersonnelIssue: Key responder unavailable

Each inject has:
- Trigger conditions (time-based, state-based, or manual)
- Target audience (which roles are affected)
- Pressure increase (eigenvector perturbation)
- Required response (what counts as handling it)

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable

# =============================================================================
# Inject Types
# =============================================================================


class InjectType(Enum):
    """Types of crisis injects."""

    MEDIA_STORY = auto()  # Press coverage
    EXECUTIVE_CALL = auto()  # Board/exec pressure
    REGULATOR_INQUIRY = auto()  # Compliance request
    CUSTOMER_ESCALATION = auto()  # Customer pressure
    TECHNICAL_COMPLICATION = auto()  # Secondary failure
    PERSONNEL_ISSUE = auto()  # Resource constraint
    SOCIAL_MEDIA = auto()  # Viral tweet/post
    COMPETITOR_STATEMENT = auto()  # Competitor capitalizes
    CUSTOM = auto()  # User-defined


class InjectTrigger(Enum):
    """When an inject fires."""

    MANUAL = auto()  # Facilitator triggers
    TIME_BASED = auto()  # After X minutes
    STATE_BASED = auto()  # When drill reaches phase
    RANDOM = auto()  # Probability-based
    CONDITIONAL = auto()  # When condition met


class InjectStatus(Enum):
    """Inject lifecycle status."""

    PENDING = auto()  # Not yet triggered
    TRIGGERED = auto()  # Just fired
    ACTIVE = auto()  # Ongoing pressure
    RESOLVED = auto()  # Successfully handled
    ESCALATED = auto()  # Made things worse
    IGNORED = auto()  # Unaddressed (bad outcome)


# =============================================================================
# Inject Specification
# =============================================================================


@dataclass(frozen=True)
class InjectSpec:
    """
    Specification for a crisis inject.

    Defines what the inject is, when it fires, and how it affects the drill.
    """

    inject_type: InjectType
    name: str
    description: str
    headline: str  # What participants see

    # Targeting
    target_roles: tuple[str, ...]  # Which roles are primarily affected
    affects_all: bool = False  # Whether it creates global pressure

    # Pressure mechanics
    stress_increase: float = 0.1  # How much stress it adds
    urgency: str = "high"  # critical, high, normal, low

    # Resolution criteria
    resolution_actions: tuple[str, ...] = ()  # What counts as handling it
    auto_escalate_minutes: int = 15  # Minutes until auto-escalation if unhandled


# =============================================================================
# Predefined Injects
# =============================================================================

MEDIA_STORY_INJECT = InjectSpec(
    inject_type=InjectType.MEDIA_STORY,
    name="Media Story Published",
    description="A major tech publication has published a story about the incident.",
    headline="TechCrunch: '[Company] Suffers Major Outage, Customers Report Data Loss'",
    target_roles=("PR Director", "Executive", "CISO"),
    affects_all=True,
    stress_increase=0.2,
    urgency="critical",
    resolution_actions=("Prepare statement", "Issue press release", "Media briefing"),
    auto_escalate_minutes=20,
)

EXECUTIVE_CALL_INJECT = InjectSpec(
    inject_type=InjectType.EXECUTIVE_CALL,
    name="Board Member Call",
    description="A board member is calling for an immediate status update.",
    headline="URGENT: Board Chair requesting immediate briefing on incident",
    target_roles=("Executive", "CISO", "Incident Commander"),
    affects_all=False,
    stress_increase=0.15,
    urgency="critical",
    resolution_actions=("Executive briefing", "Status report", "Board update"),
    auto_escalate_minutes=10,
)

REGULATOR_INQUIRY_INJECT = InjectSpec(
    inject_type=InjectType.REGULATOR_INQUIRY,
    name="Regulatory Inquiry",
    description="The data protection authority has formally requested information.",
    headline="NOTIFICATION: DPA requesting preliminary incident details within 24 hours",
    target_roles=("Legal Counsel", "CISO", "Executive"),
    affects_all=False,
    stress_increase=0.25,
    urgency="critical",
    resolution_actions=("Prepare response", "Legal review", "Submit notification"),
    auto_escalate_minutes=30,
)

CUSTOMER_ESCALATION_INJECT = InjectSpec(
    inject_type=InjectType.CUSTOMER_ESCALATION,
    name="Major Customer Escalation",
    description="Your largest enterprise customer is threatening contract termination.",
    headline="ALERT: [Major Customer] CEO demanding call with your executive team",
    target_roles=("Customer Success", "Executive", "Account Manager"),
    affects_all=False,
    stress_increase=0.2,
    urgency="high",
    resolution_actions=("Customer call", "Incident summary", "Remediation plan"),
    auto_escalate_minutes=15,
)

TECHNICAL_COMPLICATION_INJECT = InjectSpec(
    inject_type=InjectType.TECHNICAL_COMPLICATION,
    name="Secondary System Failure",
    description="A backup system has also failed, complicating recovery.",
    headline="SYSTEM ALERT: Backup database cluster showing degraded performance",
    target_roles=("On-Call Engineer", "Incident Commander"),
    affects_all=False,
    stress_increase=0.15,
    urgency="high",
    resolution_actions=("Diagnose backup", "Activate DR", "Manual failover"),
    auto_escalate_minutes=10,
)

SOCIAL_MEDIA_INJECT = InjectSpec(
    inject_type=InjectType.SOCIAL_MEDIA,
    name="Viral Social Media Post",
    description="A tweet about the incident is going viral.",
    headline="TRENDING: @angry_customer tweet about outage has 50K retweets",
    target_roles=("PR Director", "Customer Success"),
    affects_all=True,
    stress_increase=0.1,
    urgency="high",
    resolution_actions=("Social response", "Community update", "Direct outreach"),
    auto_escalate_minutes=15,
)

# Registry of predefined injects
PREDEFINED_INJECTS: dict[InjectType, InjectSpec] = {
    InjectType.MEDIA_STORY: MEDIA_STORY_INJECT,
    InjectType.EXECUTIVE_CALL: EXECUTIVE_CALL_INJECT,
    InjectType.REGULATOR_INQUIRY: REGULATOR_INQUIRY_INJECT,
    InjectType.CUSTOMER_ESCALATION: CUSTOMER_ESCALATION_INJECT,
    InjectType.TECHNICAL_COMPLICATION: TECHNICAL_COMPLICATION_INJECT,
    InjectType.SOCIAL_MEDIA: SOCIAL_MEDIA_INJECT,
}


# =============================================================================
# Inject State
# =============================================================================


@dataclass
class InjectState:
    """
    Runtime state of an inject.

    Tracks when it fired, how it's being handled, and resolution.
    """

    spec: InjectSpec
    status: InjectStatus = InjectStatus.PENDING
    triggered_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_notes: str = ""
    handled_by: list[str] = field(default_factory=list)

    # Trigger configuration
    trigger_type: InjectTrigger = InjectTrigger.MANUAL
    trigger_after_minutes: int | None = None  # For TIME_BASED
    trigger_on_phase: str | None = None  # For STATE_BASED

    @property
    def is_pending(self) -> bool:
        """Check if inject hasn't fired yet."""
        return self.status == InjectStatus.PENDING

    @property
    def is_active(self) -> bool:
        """Check if inject is currently active."""
        return self.status in (InjectStatus.TRIGGERED, InjectStatus.ACTIVE)

    @property
    def time_since_trigger(self) -> timedelta | None:
        """Get time since inject was triggered."""
        if self.triggered_at is None:
            return None
        return datetime.now() - self.triggered_at

    def trigger(self) -> None:
        """Fire the inject."""
        if self.status != InjectStatus.PENDING:
            raise ValueError(f"Cannot trigger inject in status: {self.status}")
        self.triggered_at = datetime.now()
        self.status = InjectStatus.TRIGGERED

    def activate(self) -> None:
        """Mark inject as actively being handled."""
        if self.status != InjectStatus.TRIGGERED:
            raise ValueError(f"Cannot activate inject in status: {self.status}")
        self.status = InjectStatus.ACTIVE

    def resolve(self, handler: str, notes: str = "") -> None:
        """Successfully resolve the inject."""
        if not self.is_active:
            raise ValueError(f"Cannot resolve inject in status: {self.status}")
        self.status = InjectStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.handled_by.append(handler)
        self.resolution_notes = notes

    def escalate(self, reason: str = "") -> None:
        """Mark inject as escalated (made things worse)."""
        if not self.is_active:
            raise ValueError(f"Cannot escalate inject in status: {self.status}")
        self.status = InjectStatus.ESCALATED
        self.resolution_notes = reason or "Inject escalated due to inadequate response"

    def ignore(self) -> None:
        """Mark inject as ignored (unaddressed)."""
        if not self.is_active:
            raise ValueError(f"Cannot ignore inject in status: {self.status}")
        self.status = InjectStatus.IGNORED
        self.resolution_notes = "Inject was not addressed within time limit"

    def should_auto_escalate(self) -> bool:
        """Check if inject should auto-escalate due to time."""
        if not self.is_active or self.triggered_at is None:
            return False
        elapsed = datetime.now() - self.triggered_at
        return elapsed.total_seconds() > self.spec.auto_escalate_minutes * 60

    def manifest(self) -> dict[str, Any]:
        """Get inject state as dictionary for display."""
        return {
            "name": self.spec.name,
            "type": self.spec.inject_type.name,
            "headline": self.spec.headline,
            "status": self.status.name,
            "urgency": self.spec.urgency,
            "target_roles": list(self.spec.target_roles),
            "triggered_at": self.triggered_at.isoformat()
            if self.triggered_at
            else None,
            "resolution_actions": list(self.spec.resolution_actions),
            "stress_increase": self.spec.stress_increase,
        }


# =============================================================================
# Inject Sequence
# =============================================================================


@dataclass
class InjectSequence:
    """
    A sequence of injects for a drill.

    Manages the timing and triggering of multiple injects.
    """

    injects: list[InjectState] = field(default_factory=list)
    _started_at: datetime | None = None

    def add(
        self,
        inject_type: InjectType,
        trigger_type: InjectTrigger = InjectTrigger.MANUAL,
        trigger_after_minutes: int | None = None,
        trigger_on_phase: str | None = None,
        custom_spec: InjectSpec | None = None,
    ) -> InjectState:
        """Add an inject to the sequence."""
        spec = custom_spec or PREDEFINED_INJECTS.get(inject_type)
        if spec is None:
            raise ValueError(f"Unknown inject type: {inject_type}")

        state = InjectState(
            spec=spec,
            trigger_type=trigger_type,
            trigger_after_minutes=trigger_after_minutes,
            trigger_on_phase=trigger_on_phase,
        )
        self.injects.append(state)
        return state

    def start(self) -> None:
        """Start the inject sequence timer."""
        self._started_at = datetime.now()

    def tick(self, current_phase: str | None = None) -> list[InjectState]:
        """
        Check and trigger any pending injects.

        Args:
            current_phase: Current drill phase for state-based triggers

        Returns:
            List of injects that were triggered this tick
        """
        triggered = []

        for inject in self.injects:
            if not inject.is_pending:
                continue

            should_trigger = False

            match inject.trigger_type:
                case InjectTrigger.TIME_BASED:
                    if self._started_at and inject.trigger_after_minutes is not None:
                        elapsed = datetime.now() - self._started_at
                        if elapsed.total_seconds() >= inject.trigger_after_minutes * 60:
                            should_trigger = True

                case InjectTrigger.STATE_BASED:
                    if (
                        inject.trigger_on_phase
                        and current_phase == inject.trigger_on_phase
                    ):
                        should_trigger = True

                case InjectTrigger.MANUAL:
                    pass  # Only triggered manually

            if should_trigger:
                inject.trigger()
                triggered.append(inject)

        return triggered

    def trigger_manual(self, index: int) -> InjectState:
        """Manually trigger an inject by index."""
        if index < 0 or index >= len(self.injects):
            raise IndexError(f"Inject index out of range: {index}")
        inject = self.injects[index]
        inject.trigger()
        return inject

    def get_active(self) -> list[InjectState]:
        """Get all currently active injects."""
        return [i for i in self.injects if i.is_active]

    def get_pending(self) -> list[InjectState]:
        """Get all pending injects."""
        return [i for i in self.injects if i.is_pending]

    def check_auto_escalations(self) -> list[InjectState]:
        """Check and auto-escalate overdue injects."""
        escalated = []
        for inject in self.get_active():
            if inject.should_auto_escalate():
                inject.escalate("Auto-escalated due to time limit")
                escalated.append(inject)
        return escalated


# =============================================================================
# Factory Functions
# =============================================================================


def create_inject(
    inject_type: InjectType,
    trigger_type: InjectTrigger = InjectTrigger.MANUAL,
    trigger_after_minutes: int | None = None,
    trigger_on_phase: str | None = None,
) -> InjectState:
    """Create a single inject."""
    spec = PREDEFINED_INJECTS.get(inject_type)
    if spec is None:
        raise ValueError(f"Unknown inject type: {inject_type}")

    return InjectState(
        spec=spec,
        trigger_type=trigger_type,
        trigger_after_minutes=trigger_after_minutes,
        trigger_on_phase=trigger_on_phase,
    )


def create_service_outage_injects() -> InjectSequence:
    """Create standard inject sequence for service outage drill."""
    sequence = InjectSequence()

    # Media story at T+15 minutes
    sequence.add(
        InjectType.MEDIA_STORY,
        trigger_type=InjectTrigger.TIME_BASED,
        trigger_after_minutes=15,
    )

    # Executive call at T+20 minutes
    sequence.add(
        InjectType.EXECUTIVE_CALL,
        trigger_type=InjectTrigger.TIME_BASED,
        trigger_after_minutes=20,
    )

    # Social media viral post (manual trigger for facilitator)
    sequence.add(InjectType.SOCIAL_MEDIA, trigger_type=InjectTrigger.MANUAL)

    # Technical complication when entering RESPONSE phase
    sequence.add(
        InjectType.TECHNICAL_COMPLICATION,
        trigger_type=InjectTrigger.STATE_BASED,
        trigger_on_phase="RESPONSE",
    )

    return sequence


def create_data_breach_injects() -> InjectSequence:
    """Create standard inject sequence for data breach drill."""
    sequence = InjectSequence()

    # Media story at T+15 minutes
    sequence.add(
        InjectType.MEDIA_STORY,
        trigger_type=InjectTrigger.TIME_BASED,
        trigger_after_minutes=15,
    )

    # Regulator inquiry at T+30 minutes
    sequence.add(
        InjectType.REGULATOR_INQUIRY,
        trigger_type=InjectTrigger.TIME_BASED,
        trigger_after_minutes=30,
    )

    # Executive call when entering RESPONSE
    sequence.add(
        InjectType.EXECUTIVE_CALL,
        trigger_type=InjectTrigger.STATE_BASED,
        trigger_on_phase="RESPONSE",
    )

    # Customer escalation (manual)
    sequence.add(InjectType.CUSTOMER_ESCALATION, trigger_type=InjectTrigger.MANUAL)

    return sequence


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "InjectType",
    "InjectTrigger",
    "InjectStatus",
    # Specs
    "InjectSpec",
    "MEDIA_STORY_INJECT",
    "EXECUTIVE_CALL_INJECT",
    "REGULATOR_INQUIRY_INJECT",
    "CUSTOMER_ESCALATION_INJECT",
    "TECHNICAL_COMPLICATION_INJECT",
    "SOCIAL_MEDIA_INJECT",
    "PREDEFINED_INJECTS",
    # State
    "InjectState",
    "InjectSequence",
    # Factory
    "create_inject",
    "create_service_outage_injects",
    "create_data_breach_injects",
]
