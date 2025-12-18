"""
Drill Templates: Pre-configured Crisis Simulations.

Two canonical drill templates for enterprise crisis training:

1. ServiceOutageDrill:
   - Scenario: Critical database cluster unreachable
   - Citizens: on_call_engineer, incident_commander, executive, customer_success
   - Injects: media_story, executive_call

2. DataBreachDrill:
   - Scenario: Anomalous data exfiltration detected
   - Citizens: security_analyst, legal_counsel, pr_director, ciso
   - Timer: GDPR 72h notification deadline
   - Injects: media_story, regulator_inquiry, executive_call

From Immersive Labs: "Emulate authentic threats. Challenge teams to prioritize
actions, assess risks, and make decisions under tight time constraints."

See: plans/core-apps/domain-simulation.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any
from uuid import uuid4

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from agents.town.citizen import Citizen

# =============================================================================
# OTEL Telemetry Constants
# =============================================================================

_tracer: trace.Tracer | None = None


def _get_drill_tracer() -> trace.Tracer:
    """Get the drill tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.domain.drills", "0.1.0")
    return _tracer


# Span attribute constants
ATTR_DRILL_ID = "drill.id"
ATTR_DRILL_TYPE = "drill.type"
ATTR_DRILL_STATUS = "drill.status"
ATTR_DRILL_PHASE = "drill.phase"
ATTR_DRILL_DIFFICULTY = "drill.difficulty"
ATTR_DRILL_ELAPSED_MINUTES = "drill.elapsed_minutes"
ATTR_DRILL_TIMER_COUNT = "drill.timer_count"
ATTR_DRILL_INJECT_COUNT = "drill.inject_count"
ATTR_DRILL_CITIZEN_COUNT = "drill.citizen_count"
ATTR_DRILL_SCORE = "drill.score"
ATTR_DRILL_SUCCESS = "drill.success"
ATTR_DURATION_MS = "drill.duration_ms"


# =============================================================================
# Custom Exceptions
# =============================================================================


class DrillError(Exception):
    """Base exception for drill-related errors."""

    def __init__(self, message: str, drill_id: str | None = None, phase: str | None = None):
        self.drill_id = drill_id
        self.phase = phase
        super().__init__(message)


class DrillStateError(DrillError):
    """Raised when drill is in invalid state for requested operation."""

    pass


class DrillValidationError(DrillError):
    """Raised when drill input validation fails."""

    pass


class DrillPreconditionError(DrillError):
    """Raised when a precondition for an operation is not met."""

    def __init__(
        self,
        message: str,
        drill_id: str | None = None,
        phase: str | None = None,
        precondition: str | None = None,
    ):
        self.precondition = precondition
        super().__init__(message, drill_id, phase)


from .archetypes import (
    CrisisArchetype,
    create_crisis_citizen,
    create_data_breach_team,
    create_service_outage_team,
)
from .injects import (
    InjectSequence,
    InjectState,
    create_data_breach_injects,
    create_service_outage_injects,
)
from .polynomial import (
    CRISIS_POLYNOMIAL,
    CrisisInput,
    CrisisOutput,
    CrisisPhase,
)
from .timers import (
    TimerState,
    TimerType,
    create_gdpr_timer,
    create_timer,
)

# =============================================================================
# Drill Types
# =============================================================================


class DrillType(Enum):
    """Types of crisis drills."""

    SERVICE_OUTAGE = auto()
    DATA_BREACH = auto()
    PR_CRISIS = auto()
    ROGUE_AI = auto()
    VENDOR_FAILURE = auto()
    INSIDER_THREAT = auto()


class DrillDifficulty(Enum):
    """Drill difficulty levels."""

    TRAINING = auto()  # Guided, few surprises
    STANDARD = auto()  # Normal time pressure
    ADVANCED = auto()  # Multiple injects
    CHAOS = auto()  # Maximum pressure


class DrillStatus(Enum):
    """Drill lifecycle status."""

    DRAFT = auto()  # Being configured
    READY = auto()  # Ready to start
    RUNNING = auto()  # In progress
    PAUSED = auto()  # Temporarily stopped
    COMPLETED = auto()  # Successfully finished
    ABORTED = auto()  # Terminated early


# =============================================================================
# Success Criteria
# =============================================================================


@dataclass(frozen=True)
class SuccessCriterion:
    """A criterion for drill success."""

    name: str
    description: str
    required: bool = True  # Must be met for drill success
    weight: float = 1.0  # Scoring weight


@dataclass
class SuccessEvaluation:
    """Evaluation of a success criterion."""

    criterion: SuccessCriterion
    met: bool = False
    evidence: str = ""
    evaluated_at: datetime | None = None


# =============================================================================
# Drill Template Specification
# =============================================================================


@dataclass(frozen=True)
class DrillTemplateSpec:
    """
    Specification for a drill template.

    Defines the scenario, participants, and success criteria.
    """

    drill_type: DrillType
    name: str
    description: str
    scenario_trigger: str  # Initial incident description

    # Participant configuration
    citizen_archetypes: tuple[CrisisArchetype, ...]
    default_stress_level: float = 0.5

    # Timers
    timers: tuple[TimerType, ...] = ()

    # Success criteria
    success_criteria: tuple[SuccessCriterion, ...] = ()

    # Escalation path (who to escalate to, in order)
    escalation_path: tuple[str, ...] = ()

    # Recommended duration
    target_duration_minutes: int = 60

    # Difficulty modifiers
    inject_count_by_difficulty: dict[DrillDifficulty, int] = field(
        default_factory=lambda: {
            DrillDifficulty.TRAINING: 0,
            DrillDifficulty.STANDARD: 2,
            DrillDifficulty.ADVANCED: 4,
            DrillDifficulty.CHAOS: 6,
        }
    )


# =============================================================================
# Service Outage Drill
# =============================================================================

SERVICE_OUTAGE_SUCCESS_CRITERIA = (
    SuccessCriterion(
        name="service_restored",
        description="Primary service restored to operational status",
        required=True,
        weight=1.0,
    ),
    SuccessCriterion(
        name="commander_notified",
        description="Incident Commander notified within 5 minutes",
        required=True,
        weight=0.8,
    ),
    SuccessCriterion(
        name="customer_communication",
        description="Customer communication sent within 15 minutes",
        required=True,
        weight=0.7,
    ),
    SuccessCriterion(
        name="postmortem_scheduled",
        description="Post-incident review scheduled before closure",
        required=True,
        weight=0.5,
    ),
    SuccessCriterion(
        name="executive_briefed",
        description="Executive received status update",
        required=False,
        weight=0.4,
    ),
)

SERVICE_OUTAGE_SPEC = DrillTemplateSpec(
    drill_type=DrillType.SERVICE_OUTAGE,
    name="Critical Service Outage",
    description="Primary database cluster unreachable. All customer-facing services affected.",
    scenario_trigger="ALERT: Primary database cluster DB-PROD-03 unreachable. "
    "Multiple service health checks failing. Customer reports of 500 errors increasing.",
    citizen_archetypes=(
        CrisisArchetype.ON_CALL_ENGINEER,
        CrisisArchetype.INCIDENT_COMMANDER,
        CrisisArchetype.EXECUTIVE,
        CrisisArchetype.CUSTOMER_SUCCESS,
    ),
    default_stress_level=0.6,
    timers=(),  # No compliance timers for outage
    success_criteria=SERVICE_OUTAGE_SUCCESS_CRITERIA,
    escalation_path=("On-Call Engineer", "Incident Commander", "Executive"),
    target_duration_minutes=45,
)


# =============================================================================
# Data Breach Drill
# =============================================================================

DATA_BREACH_SUCCESS_CRITERIA = (
    SuccessCriterion(
        name="breach_contained",
        description="Data exfiltration stopped and source identified",
        required=True,
        weight=1.0,
    ),
    SuccessCriterion(
        name="legal_assessment",
        description="Legal Counsel completed notification requirement assessment",
        required=True,
        weight=0.9,
    ),
    SuccessCriterion(
        name="gdpr_notification",
        description="GDPR notification prepared or sent within 72 hours",
        required=True,
        weight=1.0,
    ),
    SuccessCriterion(
        name="media_statement",
        description="Public statement prepared and approved",
        required=True,
        weight=0.7,
    ),
    SuccessCriterion(
        name="forensics_preserved",
        description="Forensic evidence preserved for investigation",
        required=True,
        weight=0.8,
    ),
    SuccessCriterion(
        name="affected_users_notified",
        description="Affected users notified per regulatory requirements",
        required=False,
        weight=0.6,
    ),
)

DATA_BREACH_SPEC = DrillTemplateSpec(
    drill_type=DrillType.DATA_BREACH,
    name="Data Breach Response",
    description="Anomalous data exfiltration detected. Potential exposure of customer PII.",
    scenario_trigger="SECURITY ALERT: Anomalous data transfer detected at 02:47 UTC. "
    "Source: Database cluster DB-PROD-03. "
    "Volume: ~2.3TB transferred to unknown external IP. "
    "Possible customer PII exposure.",
    citizen_archetypes=(
        CrisisArchetype.SECURITY_ANALYST,
        CrisisArchetype.LEGAL_COUNSEL,
        CrisisArchetype.PR_DIRECTOR,
        CrisisArchetype.CISO,
    ),
    default_stress_level=0.7,  # Higher stress for breach
    timers=(TimerType.GDPR_72H,),  # GDPR notification deadline
    success_criteria=DATA_BREACH_SUCCESS_CRITERIA,
    escalation_path=("Security Analyst", "CISO", "Legal Counsel", "PR Director"),
    target_duration_minutes=60,
)


# Registry of drill templates
DRILL_TEMPLATES: dict[DrillType, DrillTemplateSpec] = {
    DrillType.SERVICE_OUTAGE: SERVICE_OUTAGE_SPEC,
    DrillType.DATA_BREACH: DATA_BREACH_SPEC,
}


# =============================================================================
# Drill Instance
# =============================================================================


@dataclass
class DrillInstance:
    """
    A running instance of a drill.

    Manages the drill lifecycle, participants, timers, and injects.
    """

    id: str
    spec: DrillTemplateSpec
    status: DrillStatus = DrillStatus.DRAFT
    difficulty: DrillDifficulty = DrillDifficulty.STANDARD

    # State
    phase: CrisisPhase = CrisisPhase.NORMAL
    started_at: datetime | None = None
    ended_at: datetime | None = None

    # Participants
    citizens: dict[CrisisArchetype, Citizen] = field(default_factory=dict)

    # Timers
    timers: list[TimerState] = field(default_factory=list)

    # Injects
    injects: InjectSequence = field(default_factory=InjectSequence)

    # Success tracking
    evaluations: list[SuccessEvaluation] = field(default_factory=list)

    # Audit log
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    @property
    def is_running(self) -> bool:
        """Check if drill is currently running."""
        return self.status == DrillStatus.RUNNING

    @property
    def elapsed_minutes(self) -> float:
        """Get elapsed time in minutes."""
        if self.started_at is None:
            return 0.0
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds() / 60

    def setup(self, names: dict[CrisisArchetype, str] | None = None) -> None:
        """
        Set up the drill with citizens and timers.

        Args:
            names: Optional mapping of archetype to citizen name

        Raises:
            DrillStateError: If drill is not in DRAFT status
            DrillValidationError: If names mapping contains invalid archetypes
        """
        if self.status != DrillStatus.DRAFT:
            raise DrillStateError(
                f"Cannot setup drill in status {self.status.name}. Expected DRAFT.",
                drill_id=self.id,
                phase=self.phase.name,
            )

        # Validate names if provided
        if names:
            invalid_archetypes = set(names.keys()) - set(self.spec.citizen_archetypes)
            if invalid_archetypes:
                raise DrillValidationError(
                    f"Invalid archetypes in names: {[a.name for a in invalid_archetypes]}. "
                    f"Valid archetypes for {self.spec.drill_type.name}: {[a.name for a in self.spec.citizen_archetypes]}",
                    drill_id=self.id,
                )

        # Create citizens
        for archetype in self.spec.citizen_archetypes:
            name = (names or {}).get(archetype)
            citizen = create_crisis_citizen(
                archetype=archetype,
                name=name or archetype.name.replace("_", " ").title(),
                stress_level=self.spec.default_stress_level,
            )
            self.citizens[archetype] = citizen

        # Create timers
        for timer_type in self.spec.timers:
            timer = create_timer(timer_type)
            self.timers.append(timer)

        # Set up injects based on drill type
        if self.spec.drill_type == DrillType.SERVICE_OUTAGE:
            self.injects = create_service_outage_injects()
        elif self.spec.drill_type == DrillType.DATA_BREACH:
            self.injects = create_data_breach_injects()

        # Initialize success evaluations
        for criterion in self.spec.success_criteria:
            self.evaluations.append(SuccessEvaluation(criterion=criterion))

        self.status = DrillStatus.READY
        self._log("setup", "Drill setup complete")

    def start(self) -> CrisisOutput:
        """Start the drill."""
        tracer = _get_drill_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "drill.start",
            attributes={
                ATTR_DRILL_ID: self.id,
                ATTR_DRILL_TYPE: self.spec.drill_type.name,
                ATTR_DRILL_DIFFICULTY: self.difficulty.name,
                ATTR_DRILL_CITIZEN_COUNT: len(self.citizens),
                ATTR_DRILL_TIMER_COUNT: len(self.timers),
            },
        ) as span:
            try:
                if self.status != DrillStatus.READY:
                    raise DrillStateError(
                        f"Cannot start drill in status {self.status.name}. Expected READY. "
                        f"Call setup() first if drill is in DRAFT status.",
                        drill_id=self.id,
                        phase=self.phase.name,
                    )

                self.started_at = datetime.now()
                self.status = DrillStatus.RUNNING

                # Start all timers
                for timer in self.timers:
                    timer.start()

                # Start inject sequence
                self.injects.start()

                # Trigger initial incident
                new_phase, output = CRISIS_POLYNOMIAL.transition(
                    self.phase,
                    CrisisInput.detect(
                        description=self.spec.scenario_trigger,
                        severity="critical",
                        source="automated",
                    ),
                )
                self.phase = new_phase

                self._log("start", f"Drill started. Scenario: {self.spec.scenario_trigger}")
                self._log("phase_transition", f"NORMAL -> {new_phase.name}", output.metadata)

                span.set_attribute(ATTR_DRILL_PHASE, new_phase.name)
                span.set_attribute(ATTR_DRILL_STATUS, self.status.name)
                span.set_status(Status(StatusCode.OK))

                return output

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def tick(self) -> dict[str, Any]:
        """
        Tick the drill - update timers, check injects.

        Returns:
            Dict with any state changes
        """
        tracer = _get_drill_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "drill.tick",
            attributes={
                ATTR_DRILL_ID: self.id,
                ATTR_DRILL_PHASE: self.phase.name,
                ATTR_DRILL_STATUS: self.status.name,
                ATTR_DRILL_ELAPSED_MINUTES: self.elapsed_minutes,
            },
        ) as span:
            try:
                if not self.is_running:
                    span.set_attribute("drill.tick.skipped", True)
                    return {"status": self.status.name}

                changes: dict[str, Any] = {"triggered_injects": [], "timer_updates": []}

                # Tick timers
                for timer in self.timers:
                    old_status = timer.status
                    new_status = timer.tick()
                    if old_status != new_status:
                        changes["timer_updates"].append(
                            {
                                "timer": timer.config.name,
                                "old": old_status.name,
                                "new": new_status.name,
                            }
                        )
                        self._log(
                            "timer_update",
                            f"{timer.config.name}: {old_status.name} -> {new_status.name}",
                        )

                # Tick injects
                triggered = self.injects.tick(self.phase.name)
                for inject in triggered:
                    changes["triggered_injects"].append(inject.manifest())
                    self._log("inject_triggered", inject.spec.headline)

                # Check for auto-escalations
                escalated = self.injects.check_auto_escalations()
                for inject in escalated:
                    self._log("inject_escalated", f"{inject.spec.name} auto-escalated")

                span.set_attribute("drill.tick.triggered_injects", len(triggered))
                span.set_attribute("drill.tick.timer_updates", len(changes["timer_updates"]))
                span.set_attribute("drill.tick.escalations", len(escalated))
                span.set_status(Status(StatusCode.OK))

                return changes

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def advance(self, input: Any) -> CrisisOutput:
        """
        Advance the drill with an input action.

        Args:
            input: A crisis input (EscalateInput, ContainInput, etc.)

        Returns:
            Output from the transition
        """
        tracer = _get_drill_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "drill.advance",
            attributes={
                ATTR_DRILL_ID: self.id,
                ATTR_DRILL_PHASE: self.phase.name,
                ATTR_DRILL_STATUS: self.status.name,
                "drill.input_type": type(input).__name__,
            },
        ) as span:
            try:
                if not self.is_running:
                    raise DrillStateError(
                        f"Cannot advance drill in status {self.status.name}. Drill must be RUNNING.",
                        drill_id=self.id,
                        phase=self.phase.name,
                    )

                old_phase = self.phase
                new_phase, output = CRISIS_POLYNOMIAL.transition(self.phase, input)
                self.phase = new_phase

                if old_phase != new_phase:
                    self._log(
                        "phase_transition",
                        f"{old_phase.name} -> {new_phase.name}",
                        output.metadata,
                    )
                    span.set_attribute("drill.phase_changed", True)
                    span.set_attribute("drill.old_phase", old_phase.name)

                if output.audit_required:
                    self._log("auditable_action", output.message, output.metadata)
                    span.set_attribute("drill.audit_required", True)

                span.set_attribute(ATTR_DRILL_PHASE, new_phase.name)
                span.set_status(Status(StatusCode.OK))

                return output

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def resolve_inject(self, index: int, handler: str, notes: str = "") -> None:
        """
        Resolve an active inject.

        Args:
            index: Index of inject in active list
            handler: Name of person/role handling the inject
            notes: Optional resolution notes

        Raises:
            DrillValidationError: If index is out of range or handler is empty
        """
        if not handler or not handler.strip():
            raise DrillValidationError(
                "Handler name is required to resolve inject",
                drill_id=self.id,
            )

        active = self.injects.get_active()
        if index < 0 or index >= len(active):
            raise DrillValidationError(
                f"Inject index {index} out of range. Active injects: {len(active)}. "
                f"Valid indices: 0-{len(active) - 1}"
                if active
                else "No active injects to resolve.",
                drill_id=self.id,
                phase=self.phase.name,
            )

        inject = active[index]
        inject.resolve(handler.strip(), notes)
        self._log("inject_resolved", f"{inject.spec.name} resolved by {handler}")

    def evaluate_criterion(self, name: str, met: bool, evidence: str = "") -> None:
        """
        Evaluate a success criterion.

        Args:
            name: Name of the criterion to evaluate
            met: Whether the criterion was met
            evidence: Evidence supporting the evaluation

        Raises:
            DrillValidationError: If criterion name not found
        """
        for eval in self.evaluations:
            if eval.criterion.name == name:
                eval.met = met
                eval.evidence = evidence
                eval.evaluated_at = datetime.now()
                self._log(
                    "criterion_evaluated",
                    f"{name}: {'MET' if met else 'NOT MET'}",
                    {"evidence": evidence},
                )
                return

        valid_criteria = [e.criterion.name for e in self.evaluations]
        raise DrillValidationError(
            f"Unknown criterion: '{name}'. Valid criteria for {self.spec.drill_type.name}: {valid_criteria}",
            drill_id=self.id,
        )

    def end(self, success: bool | None = None) -> dict[str, Any]:
        """
        End the drill.

        Args:
            success: Override success determination (None = auto-calculate)

        Returns:
            Final drill report
        """
        tracer = _get_drill_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "drill.end",
            attributes={
                ATTR_DRILL_ID: self.id,
                ATTR_DRILL_TYPE: self.spec.drill_type.name,
                ATTR_DRILL_PHASE: self.phase.name,
                ATTR_DRILL_ELAPSED_MINUTES: self.elapsed_minutes,
            },
        ) as span:
            try:
                if not self.is_running:
                    raise DrillStateError(
                        f"Cannot end drill in status {self.status.name}. Drill must be RUNNING.",
                        drill_id=self.id,
                        phase=self.phase.name,
                    )

                self.ended_at = datetime.now()
                self.status = DrillStatus.COMPLETED

                # Stop all timers
                for timer in self.timers:
                    if timer.is_active:
                        timer.stop(success=True)

                # Calculate score
                score = self._calculate_score()

                # Determine success
                if success is None:
                    required_met = all(e.met for e in self.evaluations if e.criterion.required)
                    success = required_met and score >= 0.6

                report = self._generate_report(success, score)
                self._log("end", f"Drill ended. Success: {success}, Score: {score:.1%}")

                span.set_attribute(ATTR_DRILL_SCORE, score)
                span.set_attribute(ATTR_DRILL_SUCCESS, success)
                span.set_attribute(ATTR_DRILL_STATUS, self.status.name)
                span.set_attribute("drill.final_phase", self.phase.name)
                span.set_attribute("drill.criteria_met", sum(1 for e in self.evaluations if e.met))
                span.set_attribute("drill.criteria_total", len(self.evaluations))
                span.set_status(Status(StatusCode.OK))

                return report

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def abort(self, reason: str = "") -> None:
        """Abort the drill early."""
        self.ended_at = datetime.now()
        self.status = DrillStatus.ABORTED
        self._log("abort", f"Drill aborted: {reason}")

    def _calculate_score(self) -> float:
        """Calculate drill score based on evaluations."""
        if not self.evaluations:
            return 0.0

        total_weight = sum(e.criterion.weight for e in self.evaluations)
        achieved_weight = sum(e.criterion.weight for e in self.evaluations if e.met)

        return achieved_weight / total_weight if total_weight > 0 else 0.0

    def _generate_report(self, success: bool, score: float) -> dict[str, Any]:
        """Generate final drill report."""
        return {
            "id": self.id,
            "drill_type": self.spec.drill_type.name,
            "name": self.spec.name,
            "success": success,
            "score": score,
            "score_percent": f"{score:.1%}",
            "duration_minutes": self.elapsed_minutes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "final_phase": self.phase.name,
            "criteria": [
                {
                    "name": e.criterion.name,
                    "description": e.criterion.description,
                    "met": e.met,
                    "required": e.criterion.required,
                    "evidence": e.evidence,
                }
                for e in self.evaluations
            ],
            "timers": [t.manifest() for t in self.timers],
            "participants": [
                {"archetype": a.name, "name": c.name} for a, c in self.citizens.items()
            ],
            "audit_log_entries": len(self.audit_log),
        }

    def _log(self, event_type: str, message: str, metadata: dict[str, Any] | None = None) -> None:
        """Add entry to audit log."""
        self.audit_log.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event_type": event_type,
                "message": message,
                "metadata": metadata or {},
                "phase": self.phase.name,
            }
        )

    def manifest(self, lod: int = 1) -> dict[str, Any]:
        """
        Manifest the drill state at given Level of Detail.

        LOD 0: Basic status
        LOD 1: + Citizens, timers
        LOD 2: + Active injects, evaluations
        LOD 3: + Full audit log
        """
        base: dict[str, Any] = {
            "id": self.id,
            "name": self.spec.name,
            "status": self.status.name,
            "phase": self.phase.name,
            "elapsed_minutes": round(self.elapsed_minutes, 1),
        }

        if lod >= 1:
            base["citizens"] = [
                {
                    "archetype": a.name,
                    "name": c.name,
                    "phase": c.phase.name,
                }
                for a, c in self.citizens.items()
            ]
            base["timers"] = [t.manifest() for t in self.timers]

        if lod >= 2:
            base["active_injects"] = [i.manifest() for i in self.injects.get_active()]
            base["pending_injects"] = len(self.injects.get_pending())
            base["evaluations"] = [
                {
                    "name": e.criterion.name,
                    "met": e.met,
                    "required": e.criterion.required,
                }
                for e in self.evaluations
            ]

        if lod >= 3:
            base["audit_log"] = self.audit_log
            base["scenario"] = self.spec.scenario_trigger

        return base


# =============================================================================
# Factory Functions
# =============================================================================


def create_service_outage_drill(
    difficulty: DrillDifficulty = DrillDifficulty.STANDARD,
    names: dict[CrisisArchetype, str] | None = None,
) -> DrillInstance:
    """
    Create a Service Outage drill instance.

    Args:
        difficulty: Drill difficulty level
        names: Optional citizen names

    Returns:
        Configured DrillInstance ready to start
    """
    drill = DrillInstance(
        id=str(uuid4())[:8],
        spec=SERVICE_OUTAGE_SPEC,
        difficulty=difficulty,
    )
    drill.setup(names)
    return drill


def create_data_breach_drill(
    difficulty: DrillDifficulty = DrillDifficulty.STANDARD,
    names: dict[CrisisArchetype, str] | None = None,
) -> DrillInstance:
    """
    Create a Data Breach drill instance.

    Includes GDPR 72-hour notification timer.

    Args:
        difficulty: Drill difficulty level
        names: Optional citizen names

    Returns:
        Configured DrillInstance ready to start
    """
    drill = DrillInstance(
        id=str(uuid4())[:8],
        spec=DATA_BREACH_SPEC,
        difficulty=difficulty,
    )
    drill.setup(names)
    return drill


def create_drill(
    drill_type: DrillType,
    difficulty: DrillDifficulty = DrillDifficulty.STANDARD,
    names: dict[CrisisArchetype, str] | None = None,
) -> DrillInstance:
    """
    Create a drill instance of the specified type.

    Args:
        drill_type: Type of drill to create
        difficulty: Drill difficulty level
        names: Optional citizen names

    Returns:
        Configured DrillInstance ready to start
    """
    spec = DRILL_TEMPLATES.get(drill_type)
    if spec is None:
        raise ValueError(f"Unknown drill type: {drill_type}")

    drill = DrillInstance(
        id=str(uuid4())[:8],
        spec=spec,
        difficulty=difficulty,
    )
    drill.setup(names)
    return drill


def get_drill_template(drill_type: DrillType) -> DrillTemplateSpec | None:
    """Get the template spec for a drill type."""
    return DRILL_TEMPLATES.get(drill_type)


def list_drill_types() -> list[str]:
    """List available drill types."""
    return [dt.name for dt in DRILL_TEMPLATES.keys()]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Exceptions
    "DrillError",
    "DrillStateError",
    "DrillValidationError",
    "DrillPreconditionError",
    # Enums
    "DrillType",
    "DrillDifficulty",
    "DrillStatus",
    # Criteria
    "SuccessCriterion",
    "SuccessEvaluation",
    # Specs
    "DrillTemplateSpec",
    "SERVICE_OUTAGE_SPEC",
    "DATA_BREACH_SPEC",
    "SERVICE_OUTAGE_SUCCESS_CRITERIA",
    "DATA_BREACH_SUCCESS_CRITERIA",
    "DRILL_TEMPLATES",
    # Instance
    "DrillInstance",
    # Factory
    "create_service_outage_drill",
    "create_data_breach_drill",
    "create_drill",
    "get_drill_template",
    "list_drill_types",
]
