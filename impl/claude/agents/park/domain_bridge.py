"""
Park-Domain Integration Bridge: Connecting scenarios with crisis mechanics.

Wave 3 integration - allows Park scenarios to incorporate Domain
simulation elements including:
- Compliance timers (GDPR, SEC, HIPAA, custom)
- Crisis polynomials (state transitions)
- Domain-specific injects

This bridge enables:
- Practice scenarios with time pressure
- Crisis rehearsal with consent mechanics
- Enterprise training with Punchdrunk principles

Example:
    # Create a timed practice scenario
    bridge = ParkDomainBridge()
    scenario = await bridge.create_crisis_scenario(
        scenario_type="practice",
        timer_type=TimerType.GDPR_72H,
        citizens=["security_analyst", "legal_counsel"],
    )

See: plans/crown-jewels-enlightened.md (Wave 3)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

from agents.domain.drills import (
    CRISIS_POLYNOMIAL,
    CrisisPhase,
    DrillDifficulty,
    TimerState,
    TimerStatus,
    TimerType,
    create_timer,
    format_countdown,
)
from agents.park.director import DirectorAgent, PacingMetrics, SerendipityInjection

if TYPE_CHECKING:
    from agents.town.inhabit_session import InhabitSession


# =============================================================================
# Integrated Scenario Types
# =============================================================================


class IntegratedScenarioType(Enum):
    """
    Scenario types that integrate Park and Domain mechanics.

    These go beyond pure INHABIT scenarios by adding
    Domain-specific compliance and crisis elements.
    """

    # Pure Park scenarios (no Domain elements)
    MYSTERY = auto()
    COLLABORATION = auto()
    CONFLICT = auto()
    EMERGENCE = auto()

    # Integrated scenarios (Park + Domain)
    CRISIS_PRACTICE = auto()  # Practice responding to crises with time pressure
    COMPLIANCE_DRILL = auto()  # Formal compliance exercise
    TABLETOP = auto()  # Full crisis simulation (multi-role)
    INCIDENT_RESPONSE = auto()  # Single-incident with escalation


# =============================================================================
# Integrated Scenario Configuration
# =============================================================================


@dataclass
class TimerConfig:
    """Configuration for a scenario timer."""

    timer_type: TimerType
    accelerated: bool = False  # If True, timer runs faster for training
    acceleration_factor: float = 60.0  # 1 minute = 1 hour if accelerated


@dataclass
class IntegratedScenarioConfig:
    """
    Configuration for an integrated Park+Domain scenario.

    Combines Punchdrunk principles (consent, serendipity) with
    Domain mechanics (timers, polynomials, injects).
    """

    scenario_type: IntegratedScenarioType
    name: str
    description: str

    # Park elements
    citizen_archetypes: list[str] = field(default_factory=list)
    consent_enabled: bool = True
    serendipity_enabled: bool = True

    # Domain elements
    timers: list[TimerConfig] = field(default_factory=list)
    crisis_phase_enabled: bool = False
    initial_crisis_phase: CrisisPhase = CrisisPhase.NORMAL
    difficulty: DrillDifficulty = DrillDifficulty.STANDARD

    # Inject configuration
    inject_templates: list[str] = field(default_factory=list)
    auto_inject_on_phase_transition: bool = True


# =============================================================================
# Integrated Scenario State
# =============================================================================


@dataclass
class IntegratedScenarioState:
    """
    Runtime state for an integrated scenario.

    Tracks both Park state (consent, tension) and Domain state
    (timers, polynomial phase).
    """

    config: IntegratedScenarioConfig
    scenario_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = field(default_factory=datetime.now)

    # Park state
    consent_debt: float = 0.0
    forces_used: int = 0
    tension_level: float = 0.0

    # Domain state
    timers: list[TimerState] = field(default_factory=list)
    crisis_phase: CrisisPhase = CrisisPhase.NORMAL

    # Integration state
    phase_transitions: list[dict[str, Any]] = field(default_factory=list)
    injections_triggered: list[SerendipityInjection] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        """Check if scenario is active."""
        # Scenario is active if any timer is still running
        for timer in self.timers:
            if timer.is_active:
                return True
        return True  # Also active if no timers

    @property
    def any_timer_critical(self) -> bool:
        """Check if any timer is in critical state."""
        return any(t.status == TimerStatus.CRITICAL for t in self.timers)

    @property
    def any_timer_expired(self) -> bool:
        """Check if any timer has expired."""
        return any(t.status == TimerStatus.EXPIRED for t in self.timers)

    def tick_timers(self) -> list[TimerState]:
        """Tick all timers and return those that changed status."""
        changed = []
        for timer in self.timers:
            old_status = timer.status
            timer.tick()
            if timer.status != old_status:
                changed.append(timer)
        return changed

    def record_phase_transition(self, from_phase: CrisisPhase, to_phase: CrisisPhase) -> None:
        """Record a polynomial phase transition."""
        self.phase_transitions.append({
            "timestamp": datetime.now().isoformat(),
            "from": from_phase.name,
            "to": to_phase.name,
            "consent_debt": self.consent_debt,
            "forces_used": self.forces_used,
        })
        self.crisis_phase = to_phase


# =============================================================================
# Park-Domain Bridge
# =============================================================================


class ParkDomainBridge:
    """
    Bridge between Park scenarios and Domain mechanics.

    This is the core Wave 3 integration that enables:
    - Timed Park scenarios (crisis practice)
    - Domain drills with consent mechanics
    - Unified experience across jewels

    Usage:
        bridge = ParkDomainBridge()

        # Create a crisis practice scenario
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Data Breach Response",
            timer_type=TimerType.GDPR_72H,
            accelerated=True,  # Training mode
            citizen_archetypes=["security_analyst", "legal_counsel"],
        )

        # Start timers
        bridge.start_timers(state)

        # During scenario, tick timers
        changed = bridge.tick(state)
        for timer in changed:
            if timer.status == TimerStatus.WARNING:
                # Inject pressure!
                ...
    """

    def __init__(self, director: DirectorAgent | None = None) -> None:
        """
        Initialize the bridge.

        Args:
            director: Optional DirectorAgent for serendipity injection.
                     If not provided, creates a new one.
        """
        self._director = director
        self._active_scenarios: dict[str, IntegratedScenarioState] = {}

    def create_crisis_scenario(
        self,
        scenario_type: IntegratedScenarioType,
        name: str,
        description: str = "",
        timer_type: TimerType | None = None,
        accelerated: bool = True,
        citizen_archetypes: list[str] | None = None,
        difficulty: DrillDifficulty = DrillDifficulty.STANDARD,
    ) -> IntegratedScenarioState:
        """
        Create an integrated crisis scenario.

        Args:
            scenario_type: Type of integrated scenario
            name: Human-readable scenario name
            description: Optional description
            timer_type: Optional compliance timer type
            accelerated: If True, timer runs faster (training mode)
            citizen_archetypes: List of archetype names for citizens
            difficulty: Drill difficulty level

        Returns:
            IntegratedScenarioState ready to start
        """
        timers = []
        if timer_type:
            timers.append(TimerConfig(
                timer_type=timer_type,
                accelerated=accelerated,
            ))

        config = IntegratedScenarioConfig(
            scenario_type=scenario_type,
            name=name,
            description=description,
            citizen_archetypes=citizen_archetypes or [],
            timers=timers,
            crisis_phase_enabled=scenario_type in (
                IntegratedScenarioType.CRISIS_PRACTICE,
                IntegratedScenarioType.COMPLIANCE_DRILL,
                IntegratedScenarioType.TABLETOP,
                IntegratedScenarioType.INCIDENT_RESPONSE,
            ),
            initial_crisis_phase=CrisisPhase.NORMAL,
            difficulty=difficulty,
        )

        state = IntegratedScenarioState(config=config)

        # Create timers
        for timer_config in config.timers:
            timer_state = create_timer(timer_config.timer_type)
            state.timers.append(timer_state)

        # Track active scenario
        self._active_scenarios[state.scenario_id] = state

        return state

    def start_timers(self, state: IntegratedScenarioState) -> None:
        """Start all timers in the scenario."""
        for timer in state.timers:
            if timer.status == TimerStatus.PENDING:
                timer.start()

    def tick(self, state: IntegratedScenarioState) -> list[TimerState]:
        """
        Tick the scenario forward.

        Updates all timers and returns any that changed status.
        This is called periodically during the scenario.
        """
        return state.tick_timers()

    def transition_crisis_phase(
        self,
        state: IntegratedScenarioState,
        to_phase: CrisisPhase,
    ) -> dict[str, Any]:
        """
        Transition the crisis polynomial to a new phase.

        Valid transitions:
        - NORMAL → INCIDENT (via detect)
        - INCIDENT → RESPONSE (via recover input)
        - RESPONSE → RECOVERY (via resolve input)
        - RECOVERY → NORMAL (via close input)

        Returns a dict with transition details and any triggered events.
        """
        from_phase = state.crisis_phase

        # Define valid phase transitions (simplified for bridge use)
        valid_transitions = {
            CrisisPhase.NORMAL: [CrisisPhase.INCIDENT],
            CrisisPhase.INCIDENT: [CrisisPhase.RESPONSE],
            CrisisPhase.RESPONSE: [CrisisPhase.RECOVERY],
            CrisisPhase.RECOVERY: [CrisisPhase.NORMAL],
        }

        # Validate transition
        if to_phase not in valid_transitions.get(from_phase, []):
            return {
                "success": False,
                "error": f"Invalid transition from {from_phase.name} to {to_phase.name}",
                "valid_transitions": [p.name for p in valid_transitions.get(from_phase, [])],
            }

        # Record transition
        state.record_phase_transition(from_phase, to_phase)

        # Check if auto-inject is enabled
        triggered_events = []
        if state.config.auto_inject_on_phase_transition and self._director:
            # Director might inject serendipity on phase transition
            decision = self._evaluate_transition_injection(state, from_phase, to_phase)
            if decision.get("inject"):
                triggered_events.append(decision.get("injection"))

        return {
            "success": True,
            "from_phase": from_phase.name,
            "to_phase": to_phase.name,
            "triggered_events": triggered_events,
        }

    def _evaluate_transition_injection(
        self,
        state: IntegratedScenarioState,
        from_phase: CrisisPhase,
        to_phase: CrisisPhase,
    ) -> dict[str, Any]:
        """Evaluate whether to inject serendipity on phase transition."""
        # Higher probability of injection when transitioning to INCIDENT or RESPONSE
        inject_probability = {
            CrisisPhase.NORMAL: 0.1,
            CrisisPhase.INCIDENT: 0.5,
            CrisisPhase.RESPONSE: 0.3,
            CrisisPhase.RECOVERY: 0.2,
        }.get(to_phase, 0.2)

        # Reduce injection if consent debt is high
        inject_probability *= (1.0 - state.consent_debt * 0.5)

        # Use director's entropy sampling if available
        if self._director:
            sample = self._director._state.entropy_sample()
            if sample < inject_probability:
                context = {
                    "transition": f"{from_phase.name} → {to_phase.name}",
                    "tension": state.tension_level,
                    "consent_debt": state.consent_debt,
                }
                injection = SerendipityInjection.from_entropy(sample, context)
                state.injections_triggered.append(injection)
                return {"inject": True, "injection": injection}

        return {"inject": False}

    def update_consent(self, state: IntegratedScenarioState, debt: float) -> None:
        """Update consent debt from Park session."""
        state.consent_debt = min(1.0, max(0.0, debt))

    def use_force(self, state: IntegratedScenarioState) -> bool:
        """
        Use a force mechanic.

        Returns True if force was available and used, False otherwise.
        """
        if state.forces_used >= 3:
            return False
        state.forces_used += 1
        # Force significantly increases consent debt
        state.consent_debt = min(1.0, state.consent_debt + 0.2)
        return True

    def get_timer_display(self, state: IntegratedScenarioState) -> list[dict[str, Any]]:
        """Get displayable timer information."""
        return [
            {
                "name": timer.config.name,
                "countdown": format_countdown(timer),
                "status": timer.status.name,
                "progress": timer.progress,
                "remaining_seconds": timer.remaining.total_seconds(),
            }
            for timer in state.timers
        ]

    def get_polynomial_display(self, state: IntegratedScenarioState) -> dict[str, Any]:
        """Get displayable polynomial state information."""
        if not state.config.crisis_phase_enabled:
            return {"enabled": False}

        # Define valid phase transitions
        valid_transitions = {
            CrisisPhase.NORMAL: [CrisisPhase.INCIDENT],
            CrisisPhase.INCIDENT: [CrisisPhase.RESPONSE],
            CrisisPhase.RESPONSE: [CrisisPhase.RECOVERY],
            CrisisPhase.RECOVERY: [CrisisPhase.NORMAL],
        }

        available_phases = valid_transitions.get(state.crisis_phase, [])

        return {
            "enabled": True,
            "current_phase": state.crisis_phase.name,
            "available_transitions": [p.name for p in available_phases],
            "transition_history": state.phase_transitions,
        }

    def complete_scenario(
        self,
        state: IntegratedScenarioState,
        outcome: str = "success",
    ) -> dict[str, Any]:
        """
        Complete the scenario and return summary.

        Stops all timers and computes final metrics.
        """
        # Stop all active timers
        for timer in state.timers:
            if timer.is_active:
                timer.stop(success=(outcome == "success"))

        # Compute final state
        duration = (datetime.now() - state.started_at).total_seconds()

        # Remove from active
        if state.scenario_id in self._active_scenarios:
            del self._active_scenarios[state.scenario_id]

        return {
            "scenario_id": state.scenario_id,
            "name": state.config.name,
            "scenario_type": state.config.scenario_type.name,
            "outcome": outcome,
            "duration_seconds": duration,
            "consent_debt_final": state.consent_debt,
            "forces_used": state.forces_used,
            "timer_outcomes": {
                timer.config.name: {
                    "status": timer.status.name,
                    "elapsed_seconds": timer.elapsed.total_seconds(),
                    "expired": timer.status == TimerStatus.EXPIRED,
                }
                for timer in state.timers
            },
            "phase_transitions": state.phase_transitions,
            "injections_count": len(state.injections_triggered),
        }


# =============================================================================
# Pre-built Scenario Templates
# =============================================================================


def create_data_breach_practice(
    bridge: ParkDomainBridge,
    accelerated: bool = True,
) -> IntegratedScenarioState:
    """
    Create a data breach practice scenario.

    A streamlined crisis practice with GDPR timer and standard citizens.
    """
    return bridge.create_crisis_scenario(
        scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
        name="Data Breach Response Practice",
        description="Practice responding to a data breach with GDPR timeline pressure.",
        timer_type=TimerType.GDPR_72H,
        accelerated=accelerated,
        citizen_archetypes=["security_analyst", "legal_counsel", "pr_director", "ciso"],
        difficulty=DrillDifficulty.STANDARD,
    )


def create_service_outage_practice(
    bridge: ParkDomainBridge,
    accelerated: bool = True,
) -> IntegratedScenarioState:
    """
    Create a service outage practice scenario.

    Crisis practice with internal SLA timer.
    """
    return bridge.create_crisis_scenario(
        scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
        name="Service Outage Response Practice",
        description="Practice coordinating response to a critical service outage.",
        timer_type=TimerType.INTERNAL_SLA,
        accelerated=accelerated,
        citizen_archetypes=["on_call_engineer", "incident_commander", "executive", "customer_success"],
        difficulty=DrillDifficulty.STANDARD,
    )


def create_compliance_drill(
    bridge: ParkDomainBridge,
    timer_type: TimerType = TimerType.SEC_4DAY,
) -> IntegratedScenarioState:
    """
    Create a formal compliance drill.

    Full timed drill for compliance documentation purposes.
    NOT accelerated - runs in real-time for authentic experience.
    """
    return bridge.create_crisis_scenario(
        scenario_type=IntegratedScenarioType.COMPLIANCE_DRILL,
        name="Quarterly Compliance Drill",
        description="Formal compliance exercise for regulatory documentation.",
        timer_type=timer_type,
        accelerated=False,  # Real-time for compliance purposes
        citizen_archetypes=["security_analyst", "legal_counsel", "compliance_officer", "executive"],
        difficulty=DrillDifficulty.ADVANCED,
    )


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Types
    "IntegratedScenarioType",
    # Configuration
    "TimerConfig",
    "IntegratedScenarioConfig",
    # State
    "IntegratedScenarioState",
    # Bridge
    "ParkDomainBridge",
    # Templates
    "create_data_breach_practice",
    "create_service_outage_practice",
    "create_compliance_drill",
]
