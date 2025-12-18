"""
DirectorAgent: Session Pacing and Serendipity Injection.

The director monitors INHABIT session pace and injects surprises
via void.entropy.inject when appropriate. Think of the director
as a Westworld narrative director—nudging the experience but
never forcing outcomes.

Key Principles:
1. **Collaboration > Control**: Director suggests, doesn't force
2. **Consent-Aware**: Injection frequency scales with consent debt
3. **Tension Escalation**: Build drama based on player progress
4. **Dynamic Difficulty**: Adjust based on player performance

From the Punchdrunk Handbook:
    "The director's role is to ensure the experience breathes—
    moments of intensity followed by release."

AGENTESE Integration:
    - void.entropy.inject: Source of serendipity events
    - void.serendipity.sip: Tangential discoveries

See: plans/core-apps/punchdrunk-park.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, FrozenSet

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from agents.poly.protocol import PolyAgent

if TYPE_CHECKING:
    from agents.town.inhabit_session import InhabitSession


# =============================================================================
# OTEL Telemetry Constants
# =============================================================================

# Tracer singleton
_tracer: trace.Tracer | None = None


def _get_director_tracer() -> trace.Tracer:
    """Get the DirectorAgent tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.park.director", "0.1.0")
    return _tracer


# Span attribute constants
ATTR_DIRECTOR_PHASE = "director.phase"
ATTR_DIRECTOR_TENSION = "director.tension"
ATTR_DIRECTOR_CONSENT_DEBT = "director.consent_debt"
ATTR_DIRECTOR_ACTION_COUNT = "director.action_count"
ATTR_DIRECTOR_INJECTION_COUNT = "director.injection_count"
ATTR_DIRECTOR_INJECTION_TYPE = "director.injection.type"
ATTR_DIRECTOR_INJECTION_INTENSITY = "director.injection.intensity"
ATTR_DIRECTOR_DECISION = "director.decision"
ATTR_DIRECTOR_REASON = "director.reason"
ATTR_DIRECTOR_COOLDOWN_REMAINING = "director.cooldown_remaining"
ATTR_DURATION_MS = "director.duration_ms"

# =============================================================================
# Director Phases (Polynomial Positions)
# =============================================================================


class DirectorPhase(Enum):
    """
    Phases of the DirectorAgent polynomial.

    The director cycles through these phases:
    OBSERVING → BUILDING_TENSION → (INJECTING | COOLDOWN) → OBSERVING

    This mirrors the theatrical concept of rising action, climax, and release.
    """

    OBSERVING = auto()  # Watching session pace, gathering metrics
    BUILDING_TENSION = auto()  # Tension building, considering intervention
    INJECTING = auto()  # Actively injecting serendipity
    COOLDOWN = auto()  # Post-injection cooldown period
    INTERVENING = auto()  # Special intervention (difficulty adjustment)


# =============================================================================
# Metrics and Data Structures
# =============================================================================


@dataclass
class PacingMetrics:
    """
    Real-time pacing metrics for an INHABIT session.

    These metrics help the director decide when to inject surprises:
    - action_rate: Actions per minute (player engagement)
    - resistance_rate: Citizen refusals per action (alignment issues)
    - consent_debt: Current consent debt level (relationship health)
    - tension_level: Computed tension [0.0, 1.0]
    - session_progress: How far through the session [0.0, 1.0]
    """

    action_rate: float = 0.0  # Actions per minute
    resistance_rate: float = 0.0  # Refusals / total actions
    consent_debt: float = 0.0  # Current consent debt [0.0, 1.0]
    tension_level: float = 0.0  # Computed tension [0.0, 1.0]
    session_progress: float = 0.0  # Progress through session [0.0, 1.0]

    # Time tracking
    session_start: float = field(default_factory=time.time)
    last_action_time: float = field(default_factory=time.time)
    action_count: int = 0
    resistance_count: int = 0

    # Injection tracking
    last_injection_time: float = 0.0
    injection_count: int = 0

    def record_action(self, resisted: bool = False) -> None:
        """Record a player action."""
        now = time.time()
        self.action_count += 1
        if resisted:
            self.resistance_count += 1
        self.last_action_time = now
        self._recompute()

    def update_consent(self, debt: float) -> None:
        """Update consent debt from session."""
        self.consent_debt = debt
        self._recompute()

    def record_injection(self) -> None:
        """Record that a serendipity injection occurred."""
        self.last_injection_time = time.time()
        self.injection_count += 1

    def _recompute(self) -> None:
        """Recompute derived metrics."""
        now = time.time()
        elapsed_minutes = (now - self.session_start) / 60.0

        # Action rate (actions per minute)
        if elapsed_minutes > 0:
            self.action_rate = self.action_count / elapsed_minutes
        else:
            self.action_rate = 0.0

        # Resistance rate
        if self.action_count > 0:
            self.resistance_rate = self.resistance_count / self.action_count
        else:
            self.resistance_rate = 0.0

        # Tension level: weighted combination of factors
        # Higher tension when: low action rate, high resistance, high debt
        engagement_factor = max(
            0.0, 1.0 - (self.action_rate / 5.0)
        )  # Low engagement → high tension
        conflict_factor = self.resistance_rate  # More resistance → higher tension
        debt_factor = self.consent_debt  # More debt → higher tension

        self.tension_level = 0.3 * engagement_factor + 0.3 * conflict_factor + 0.4 * debt_factor
        self.tension_level = max(0.0, min(1.0, self.tension_level))

    @property
    def time_since_last_action(self) -> float:
        """Seconds since last player action."""
        return time.time() - self.last_action_time

    @property
    def time_since_injection(self) -> float:
        """Seconds since last serendipity injection."""
        if self.last_injection_time == 0.0:
            return float("inf")
        return time.time() - self.last_injection_time


@dataclass
class SerendipityInjection:
    """
    A serendipity event to inject into the session.

    These are surprises that the director can insert to
    shift the narrative or break stalemates.
    """

    type: str  # "arrival", "discovery", "revelation", "twist", "callback"
    description: str  # Human-readable description
    intensity: float  # How dramatic [0.0, 1.0]
    entropy_seed: float  # Seed from void.entropy
    target_citizen: str | None = None  # If targeting specific citizen
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_entropy(
        cls,
        seed: float,
        session_context: dict[str, Any],
    ) -> SerendipityInjection:
        """
        Generate an injection from entropy seed and session context.

        The type and content are determined by the entropy seed,
        while the context shapes the specific details.
        """
        # Map seed ranges to injection types
        injection_types = [
            ("arrival", "A new character enters the scene"),
            ("discovery", "Something hidden is revealed"),
            ("revelation", "A secret comes to light"),
            ("twist", "An unexpected development occurs"),
            ("callback", "A past event resurfaces"),
        ]

        type_idx = int(seed * len(injection_types))
        type_idx = min(type_idx, len(injection_types) - 1)
        inj_type, base_desc = injection_types[type_idx]

        # Intensity based on seed (higher seed = higher intensity)
        intensity = 0.3 + 0.5 * seed

        # Customize description based on context
        citizens = session_context.get("citizens", [])
        if citizens and inj_type == "arrival":
            # Pick a citizen to mention
            citizen_idx = int(seed * 1000) % len(citizens)
            citizen = citizens[citizen_idx]
            description = f"{citizen} arrives unexpectedly"
        elif inj_type == "revelation" and citizens:
            citizen_idx = int(seed * 1000) % len(citizens)
            citizen = citizens[citizen_idx]
            description = f"{citizen} reveals something important"
        else:
            description = base_desc

        return cls(
            type=inj_type,
            description=description,
            intensity=intensity,
            entropy_seed=seed,
            target_citizen=session_context.get("current_citizen"),
            metadata={"context": session_context},
        )


@dataclass
class TensionEscalation:
    """
    Represents a tension escalation decision.

    The director uses this to decide whether to increase
    dramatic tension based on current metrics.
    """

    should_escalate: bool
    current_tension: float
    target_tension: float
    method: str  # "inject", "hint", "wait"
    reason: str


@dataclass
class DifficultyAdjustment:
    """
    A dynamic difficulty adjustment.

    Based on player performance, the director can suggest
    adjustments to make the experience more or less challenging.
    """

    direction: str  # "increase", "decrease", "maintain"
    magnitude: float  # How much to adjust [0.0, 1.0]
    reason: str
    suggested_changes: list[str] = field(default_factory=list)


@dataclass
class InjectionDecision:
    """
    The director's decision about whether to inject serendipity.

    This is the output of the director's evaluation phase.
    """

    should_inject: bool
    injection: SerendipityInjection | None
    cooldown_seconds: float  # How long to wait after injection
    reason: str


# =============================================================================
# Director Configuration
# =============================================================================


@dataclass
class DirectorConfig:
    """
    Configuration for the DirectorAgent.

    These parameters tune the director's behavior:
    - tension_threshold: When to consider intervention
    - injection_cooldown: Minimum time between injections
    - consent_sensitivity: How much consent debt affects decisions
    - difficulty_window: Actions to consider for difficulty adjustment
    """

    # Tension thresholds
    low_tension_threshold: float = 0.2  # Below this: consider injection
    high_tension_threshold: float = 0.7  # Above this: let things breathe

    # Cooldown settings
    min_injection_cooldown: float = 60.0  # Minimum seconds between injections
    max_injection_cooldown: float = 300.0  # Maximum seconds between injections

    # Consent sensitivity
    consent_debt_multiplier: float = 1.5  # How much debt extends cooldown

    # Difficulty adjustment
    difficulty_window: int = 10  # Number of actions to consider
    difficulty_resistance_threshold: float = 0.5  # Resistance rate for difficulty decrease

    # Intervention probability at different tension levels
    low_tension_inject_prob: float = 0.7  # Inject when boring
    high_tension_inject_prob: float = 0.1  # Rarely inject when tense

    # Entropy budget per session
    entropy_budget: float = 1.0  # Total entropy to spend


# =============================================================================
# Director Polynomial Agent
# =============================================================================


def _director_directions(phase: DirectorPhase) -> FrozenSet[str]:
    """
    Valid inputs for each director phase.

    This encodes what the director can respond to at each phase.
    """
    match phase:
        case DirectorPhase.OBSERVING:
            # Can receive metrics updates, tick, or force inject
            return frozenset({"tick", "metrics", "force_inject", "reset"})
        case DirectorPhase.BUILDING_TENSION:
            # Evaluating whether to inject
            return frozenset({"tick", "metrics", "evaluate", "cancel"})
        case DirectorPhase.INJECTING:
            # Actively injecting
            return frozenset({"complete", "abort"})
        case DirectorPhase.COOLDOWN:
            # Waiting after injection
            return frozenset({"tick", "reset"})
        case DirectorPhase.INTERVENING:
            # Adjusting difficulty
            return frozenset({"tick", "complete", "abort"})


def _create_director_transition(
    config: DirectorConfig,
    state: "DirectorState",
) -> Callable[[DirectorPhase, Any], tuple[DirectorPhase, Any]]:
    """
    Create the transition function for the director polynomial.

    The transition function captures the config and mutable state
    via closure, allowing the polynomial to maintain context.
    """

    def transition(phase: DirectorPhase, input: Any) -> tuple[DirectorPhase, Any]:
        """
        Director state transition function.

        transition: Phase × Input → (NewPhase, Output)
        """
        match phase:
            case DirectorPhase.OBSERVING:
                return _handle_observing(phase, input, config, state)
            case DirectorPhase.BUILDING_TENSION:
                return _handle_building_tension(phase, input, config, state)
            case DirectorPhase.INJECTING:
                return _handle_injecting(phase, input, config, state)
            case DirectorPhase.COOLDOWN:
                return _handle_cooldown(phase, input, config, state)
            case DirectorPhase.INTERVENING:
                return _handle_intervening(phase, input, config, state)

    return transition


def _handle_observing(
    phase: DirectorPhase,
    input: Any,
    config: DirectorConfig,
    state: "DirectorState",
) -> tuple[DirectorPhase, Any]:
    """Handle OBSERVING phase transitions."""
    cmd = (
        input
        if isinstance(input, str)
        else input.get("cmd", "tick")
        if isinstance(input, dict)
        else "tick"
    )

    match cmd:
        case "tick":
            # Evaluate current metrics
            metrics = state.metrics
            tension = metrics.tension_level

            # Low tension → consider building
            if tension < config.low_tension_threshold:
                # Check cooldown
                if metrics.time_since_injection > config.min_injection_cooldown:
                    return DirectorPhase.BUILDING_TENSION, {
                        "status": "building_tension",
                        "tension": tension,
                        "reason": "low_tension",
                    }

            # High tension → monitor but don't intervene
            return DirectorPhase.OBSERVING, {
                "status": "observing",
                "tension": tension,
            }

        case "metrics":
            # Update metrics from session
            if isinstance(input, dict):
                if "consent_debt" in input:
                    state.metrics.update_consent(input["consent_debt"])
                if "action_resisted" in input:
                    state.metrics.record_action(resisted=input["action_resisted"])
                elif "action" in input:
                    state.metrics.record_action(resisted=False)
            return DirectorPhase.OBSERVING, {"status": "metrics_updated"}

        case "force_inject":
            # Force an immediate injection (for testing or special events)
            return DirectorPhase.INJECTING, {
                "status": "force_injecting",
                "reason": "forced",
            }

        case "reset":
            # Reset the director state
            state.reset()
            return DirectorPhase.OBSERVING, {"status": "reset"}

        case _:
            return DirectorPhase.OBSERVING, {"status": "unknown_command", "cmd": cmd}


def _handle_building_tension(
    phase: DirectorPhase,
    input: Any,
    config: DirectorConfig,
    state: "DirectorState",
) -> tuple[DirectorPhase, Any]:
    """Handle BUILDING_TENSION phase transitions."""
    cmd = (
        input
        if isinstance(input, str)
        else input.get("cmd", "tick")
        if isinstance(input, dict)
        else "tick"
    )

    match cmd:
        case "tick" | "evaluate":
            # Decide whether to inject
            decision = _evaluate_injection(config, state)
            if decision.should_inject:
                state.pending_injection = decision.injection
                return DirectorPhase.INJECTING, {
                    "status": "injecting",
                    "decision": decision,
                }
            else:
                return DirectorPhase.OBSERVING, {
                    "status": "no_injection",
                    "reason": decision.reason,
                }

        case "metrics":
            # Update metrics during evaluation
            if isinstance(input, dict) and "consent_debt" in input:
                state.metrics.update_consent(input["consent_debt"])
            return DirectorPhase.BUILDING_TENSION, {"status": "metrics_updated"}

        case "cancel":
            # Cancel evaluation, return to observing
            return DirectorPhase.OBSERVING, {"status": "cancelled"}

        case _:
            return DirectorPhase.BUILDING_TENSION, {"status": "unknown_command"}


def _handle_injecting(
    phase: DirectorPhase,
    input: Any,
    config: DirectorConfig,
    state: "DirectorState",
) -> tuple[DirectorPhase, Any]:
    """Handle INJECTING phase transitions."""
    cmd = (
        input
        if isinstance(input, str)
        else input.get("cmd", "complete")
        if isinstance(input, dict)
        else "complete"
    )

    match cmd:
        case "complete":
            # Injection complete, enter cooldown
            if state.pending_injection:
                state.metrics.record_injection()
                state.injection_history.append(state.pending_injection)
                injection = state.pending_injection
                state.pending_injection = None

                # Calculate cooldown based on consent debt
                cooldown = config.min_injection_cooldown * (
                    1.0 + config.consent_debt_multiplier * state.metrics.consent_debt
                )
                cooldown = min(cooldown, config.max_injection_cooldown)
                state.cooldown_until = time.time() + cooldown

                return DirectorPhase.COOLDOWN, {
                    "status": "injection_complete",
                    "injection": injection,
                    "cooldown_seconds": cooldown,
                }

            return DirectorPhase.OBSERVING, {"status": "no_pending_injection"}

        case "abort":
            # Abort injection
            state.pending_injection = None
            return DirectorPhase.OBSERVING, {"status": "injection_aborted"}

        case _:
            return DirectorPhase.INJECTING, {"status": "unknown_command"}


def _handle_cooldown(
    phase: DirectorPhase,
    input: Any,
    config: DirectorConfig,
    state: "DirectorState",
) -> tuple[DirectorPhase, Any]:
    """Handle COOLDOWN phase transitions."""
    cmd = (
        input
        if isinstance(input, str)
        else input.get("cmd", "tick")
        if isinstance(input, dict)
        else "tick"
    )

    match cmd:
        case "tick":
            now = time.time()
            if now >= state.cooldown_until:
                return DirectorPhase.OBSERVING, {
                    "status": "cooldown_complete",
                }
            remaining = state.cooldown_until - now
            return DirectorPhase.COOLDOWN, {
                "status": "cooling_down",
                "remaining_seconds": remaining,
            }

        case "reset":
            state.cooldown_until = 0.0
            return DirectorPhase.OBSERVING, {"status": "cooldown_reset"}

        case _:
            return DirectorPhase.COOLDOWN, {"status": "unknown_command"}


def _handle_intervening(
    phase: DirectorPhase,
    input: Any,
    config: DirectorConfig,
    state: "DirectorState",
) -> tuple[DirectorPhase, Any]:
    """Handle INTERVENING phase transitions."""
    cmd = (
        input
        if isinstance(input, str)
        else input.get("cmd", "complete")
        if isinstance(input, dict)
        else "complete"
    )

    match cmd:
        case "tick":
            # Continue intervention
            return DirectorPhase.INTERVENING, {"status": "intervening"}

        case "complete":
            # Intervention complete
            return DirectorPhase.OBSERVING, {"status": "intervention_complete"}

        case "abort":
            return DirectorPhase.OBSERVING, {"status": "intervention_aborted"}

        case _:
            return DirectorPhase.INTERVENING, {"status": "unknown_command"}


def _evaluate_injection(
    config: DirectorConfig,
    state: "DirectorState",
) -> InjectionDecision:
    """
    Evaluate whether to inject serendipity.

    The decision considers:
    1. Current tension level
    2. Consent debt (higher debt → less injection)
    3. Time since last injection
    4. Session progress
    """
    metrics = state.metrics
    tension = metrics.tension_level
    debt = metrics.consent_debt

    # Don't inject if consent debt is too high
    if debt > 0.7:
        return InjectionDecision(
            should_inject=False,
            injection=None,
            cooldown_seconds=config.min_injection_cooldown,
            reason="consent_debt_too_high",
        )

    # Don't inject if cooldown hasn't elapsed
    if metrics.time_since_injection < config.min_injection_cooldown:
        return InjectionDecision(
            should_inject=False,
            injection=None,
            cooldown_seconds=config.min_injection_cooldown - metrics.time_since_injection,
            reason="cooldown_active",
        )

    # Calculate injection probability based on tension
    if tension < config.low_tension_threshold:
        inject_prob = config.low_tension_inject_prob
        reason = "low_tension_boost"
    elif tension > config.high_tension_threshold:
        inject_prob = config.high_tension_inject_prob
        reason = "high_tension_caution"
    else:
        # Linear interpolation in the middle range
        range_size = config.high_tension_threshold - config.low_tension_threshold
        normalized = (tension - config.low_tension_threshold) / range_size
        inject_prob = (
            config.low_tension_inject_prob * (1 - normalized)
            + config.high_tension_inject_prob * normalized
        )
        reason = "moderate_tension"

    # Consent debt reduces injection probability
    inject_prob *= 1.0 - (debt * 0.5)

    # Use entropy pool sample for decision
    sample = state.entropy_sample()
    should_inject = sample < inject_prob

    if should_inject:
        # Generate the injection
        context = {
            "tension": tension,
            "consent_debt": debt,
            "session_progress": metrics.session_progress,
            "action_count": metrics.action_count,
            "citizens": state.citizen_names,
            "current_citizen": state.current_citizen,
        }
        injection = SerendipityInjection.from_entropy(sample, context)

        return InjectionDecision(
            should_inject=True,
            injection=injection,
            cooldown_seconds=config.min_injection_cooldown,
            reason=reason,
        )
    else:
        return InjectionDecision(
            should_inject=False,
            injection=None,
            cooldown_seconds=0.0,
            reason=f"probability_check_failed ({inject_prob:.2f})",
        )


# =============================================================================
# Director State (Mutable Context)
# =============================================================================


@dataclass
class DirectorState:
    """
    Mutable state for the DirectorAgent.

    This is captured by closure in the transition function,
    providing the polynomial with persistent context.
    """

    metrics: PacingMetrics = field(default_factory=PacingMetrics)
    pending_injection: SerendipityInjection | None = None
    injection_history: list[SerendipityInjection] = field(default_factory=list)
    cooldown_until: float = 0.0
    entropy_remaining: float = 1.0

    # Session context
    citizen_names: list[str] = field(default_factory=list)
    current_citizen: str | None = None

    # Random state for entropy sampling
    _random_state: float = field(default_factory=lambda: time.time() % 1.0)

    def reset(self) -> None:
        """Reset state for a new session."""
        self.metrics = PacingMetrics()
        self.pending_injection = None
        self.injection_history = []
        self.cooldown_until = 0.0
        self.entropy_remaining = 1.0

    def entropy_sample(self) -> float:
        """
        Sample from entropy pool.

        Uses a simple LCG for deterministic testing.
        In production, would use void.entropy.sip.
        """
        # Linear congruential generator
        self._random_state = (self._random_state * 1103515245 + 12345) % (2**31)
        return self._random_state / (2**31)


# =============================================================================
# Director Agent Class
# =============================================================================


class DirectorAgent:
    """
    High-level wrapper for the DirectorAgent polynomial.

    Provides a more ergonomic async interface while using
    the polynomial state machine internally.

    Usage:
        director = DirectorAgent.create()
        director.bind_session(session)

        # On each tick
        result = await director.tick()
        if result.get("injection"):
            # Apply injection to session
            ...
    """

    def __init__(
        self,
        polynomial: PolyAgent[DirectorPhase, Any, Any],
        state: DirectorState,
        config: DirectorConfig,
    ) -> None:
        self._poly = polynomial
        self._state = state
        self._config = config
        self._phase = DirectorPhase.OBSERVING
        self._session: InhabitSession | None = None

    @classmethod
    def create(cls, config: DirectorConfig | None = None) -> DirectorAgent:
        """Create a new DirectorAgent with optional config."""
        config = config or DirectorConfig()
        state = DirectorState()
        transition = _create_director_transition(config, state)

        polynomial: PolyAgent[DirectorPhase, Any, Any] = PolyAgent(
            name="DirectorAgent",
            positions=frozenset(DirectorPhase),
            _directions=_director_directions,
            _transition=transition,
        )

        return cls(polynomial, state, config)

    @property
    def phase(self) -> DirectorPhase:
        """Current director phase."""
        return self._phase

    @property
    def metrics(self) -> PacingMetrics:
        """Current pacing metrics."""
        return self._state.metrics

    @property
    def config(self) -> DirectorConfig:
        """Director configuration."""
        return self._config

    @property
    def injection_history(self) -> list[SerendipityInjection]:
        """History of injections in this session."""
        return list(self._state.injection_history)

    def bind_session(self, session: InhabitSession) -> None:
        """
        Bind the director to an INHABIT session.

        This allows the director to monitor session state
        and inject surprises at appropriate moments.
        """
        self._session = session
        self._state.current_citizen = session.citizen.name
        # Collect citizen names from session context if available
        if hasattr(session, "scenario_citizens"):
            self._state.citizen_names = list(session.scenario_citizens)

    def update_metrics(
        self,
        action_resisted: bool = False,
        consent_debt: float | None = None,
    ) -> None:
        """
        Update pacing metrics from session events.

        Call this after each player action.
        """
        tracer = _get_director_tracer()

        with tracer.start_as_current_span(
            "director.update_metrics",
            attributes={
                ATTR_DIRECTOR_PHASE: self._phase.name,
                "director.action_resisted": action_resisted,
            },
        ) as span:
            if action_resisted is not None:
                self._state.metrics.record_action(resisted=action_resisted)

            if consent_debt is not None:
                self._state.metrics.update_consent(consent_debt)
            elif self._session:
                self._state.metrics.update_consent(self._session.consent.debt)

            # Record resulting metrics
            span.set_attribute(ATTR_DIRECTOR_TENSION, self._state.metrics.tension_level)
            span.set_attribute(ATTR_DIRECTOR_CONSENT_DEBT, self._state.metrics.consent_debt)
            span.set_attribute(ATTR_DIRECTOR_ACTION_COUNT, self._state.metrics.action_count)
            span.set_attribute("director.resistance_rate", self._state.metrics.resistance_rate)
            span.set_status(Status(StatusCode.OK))

    async def tick(self) -> dict[str, Any]:
        """
        Tick the director forward.

        Returns the result of the tick, including any injection
        decisions or status updates.
        """
        tracer = _get_director_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "director.tick",
            attributes={
                ATTR_DIRECTOR_PHASE: self._phase.name,
                ATTR_DIRECTOR_TENSION: self._state.metrics.tension_level,
                ATTR_DIRECTOR_CONSENT_DEBT: self._state.metrics.consent_debt,
                ATTR_DIRECTOR_ACTION_COUNT: self._state.metrics.action_count,
            },
        ) as span:
            try:
                self._phase, result = self._poly.invoke(self._phase, "tick")

                span.set_attribute("director.new_phase", self._phase.name)
                span.set_attribute("director.status", result.get("status", "unknown"))
                span.set_status(Status(StatusCode.OK))

                return result

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    async def evaluate_injection(self) -> InjectionDecision:
        """
        Force evaluation of whether to inject serendipity.

        Returns the injection decision.
        """
        tracer = _get_director_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "director.evaluate_injection",
            attributes={
                ATTR_DIRECTOR_PHASE: self._phase.name,
                ATTR_DIRECTOR_TENSION: self._state.metrics.tension_level,
                ATTR_DIRECTOR_CONSENT_DEBT: self._state.metrics.consent_debt,
                ATTR_DIRECTOR_INJECTION_COUNT: self._state.metrics.injection_count,
            },
        ) as span:
            try:
                decision = _evaluate_injection(self._config, self._state)

                span.set_attribute(ATTR_DIRECTOR_DECISION, decision.should_inject)
                span.set_attribute(ATTR_DIRECTOR_REASON, decision.reason)
                if decision.injection:
                    span.set_attribute(ATTR_DIRECTOR_INJECTION_TYPE, decision.injection.type)
                    span.set_attribute(
                        ATTR_DIRECTOR_INJECTION_INTENSITY, decision.injection.intensity
                    )
                span.set_status(Status(StatusCode.OK))

                return decision

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    async def inject_serendipity(
        self,
        entropy_seed: float | None = None,
    ) -> SerendipityInjection:
        """
        Inject serendipity into the session.

        Can provide an entropy seed or use internal sampling.
        """
        tracer = _get_director_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span(
            "director.inject_serendipity",
            attributes={
                ATTR_DIRECTOR_PHASE: self._phase.name,
                ATTR_DIRECTOR_TENSION: self._state.metrics.tension_level,
                ATTR_DIRECTOR_CONSENT_DEBT: self._state.metrics.consent_debt,
                ATTR_DIRECTOR_INJECTION_COUNT: self._state.metrics.injection_count,
            },
        ) as span:
            try:
                if entropy_seed is None:
                    entropy_seed = self._state.entropy_sample()

                span.set_attribute("director.entropy_seed", entropy_seed)

                context = {
                    "tension": self._state.metrics.tension_level,
                    "consent_debt": self._state.metrics.consent_debt,
                    "session_progress": self._state.metrics.session_progress,
                    "citizens": self._state.citizen_names,
                    "current_citizen": self._state.current_citizen,
                }

                injection = SerendipityInjection.from_entropy(entropy_seed, context)
                self._state.pending_injection = injection

                # Record injection details
                span.set_attribute(ATTR_DIRECTOR_INJECTION_TYPE, injection.type)
                span.set_attribute(ATTR_DIRECTOR_INJECTION_INTENSITY, injection.intensity)
                span.set_attribute("director.injection.description", injection.description)

                # Transition to injecting phase
                self._phase, _ = self._poly.invoke(DirectorPhase.OBSERVING, "force_inject")

                # Complete the injection
                self._phase, result = self._poly.invoke(DirectorPhase.INJECTING, "complete")

                span.set_attribute("director.new_phase", self._phase.name)
                span.set_attribute(
                    ATTR_DIRECTOR_COOLDOWN_REMAINING, result.get("cooldown_seconds", 0)
                )
                span.set_status(Status(StatusCode.OK))

                return injection

            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise

            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span.set_attribute(ATTR_DURATION_MS, duration_ms)

    def reset(self) -> None:
        """Reset the director for a new session."""
        self._phase = DirectorPhase.OBSERVING
        self._state.reset()
        self._session = None


# =============================================================================
# Factory Functions
# =============================================================================


def create_director(config: DirectorConfig | None = None) -> DirectorAgent:
    """
    Create a new DirectorAgent.

    Args:
        config: Optional configuration. Uses defaults if not provided.

    Returns:
        A new DirectorAgent ready to bind to a session.
    """
    return DirectorAgent.create(config)


# Create the singleton polynomial for reference
_default_state = DirectorState()
_default_config = DirectorConfig()

DIRECTOR_POLYNOMIAL: PolyAgent[DirectorPhase, Any, Any] = PolyAgent(
    name="DirectorPolynomial",
    positions=frozenset(DirectorPhase),
    _directions=_director_directions,
    _transition=_create_director_transition(_default_config, _default_state),
)
"""
The DirectorAgent polynomial.

Use create_director() for instances with isolated state.
This singleton is for protocol compliance verification only.
"""


# =============================================================================
# CLI Projection Functions
# =============================================================================


def project_director_to_ascii(
    director: DirectorAgent,
    width: int = 60,
) -> str:
    """
    Project director state to ASCII art for CLI rendering.

    Layout:
        ┌──────────────────────────────────────────────────────────┐
        │ DIRECTOR [OBSERVING]                          Session: 5m│
        ├──────────────────────────────────────────────────────────┤
        │                                                          │
        │  Tension:     ████░░░░░░  40%                            │
        │  Consent:     ██░░░░░░░░  20%                            │
        │  Actions:     42 (resistance: 15%)                       │
        │                                                          │
        ├──────────────────────────────────────────────────────────┤
        │ Injections: 3                          Cooldown: 45s     │
        │  → arrival: Alice arrives unexpectedly                   │
        │  → revelation: Bob reveals something important           │
        └──────────────────────────────────────────────────────────┘
    """
    state = director._state
    metrics = state.metrics
    phase = director.phase

    lines: list[str] = []

    # Top border
    border = "┌" + "─" * (width - 2) + "┐"
    lines.append(border)

    # Header with phase and session duration
    session_duration = int(time.time() - metrics.session_start)
    session_str = f"Session: {session_duration // 60}m{session_duration % 60}s"
    phase_str = f"DIRECTOR [{phase.name}]"
    padding = width - len(phase_str) - len(session_str) - 4
    header = f"│ {phase_str}{' ' * padding}{session_str} │"
    lines.append(header)

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Tension bar
    tension = metrics.tension_level
    tension_filled = int(tension * 10)
    tension_bar = "█" * tension_filled + "░" * (10 - tension_filled)
    tension_pct = f"{int(tension * 100)}%"
    tension_line = f"│  Tension:     {tension_bar}  {tension_pct:<5}" + " " * (width - 35) + "│"
    lines.append(tension_line)

    # Consent debt bar
    debt = min(metrics.consent_debt, 1.0)
    debt_filled = int(debt * 10)
    debt_bar = "█" * debt_filled + "░" * (10 - debt_filled)
    debt_pct = f"{int(debt * 100)}%"
    debt_line = f"│  Consent:     {debt_bar}  {debt_pct:<5}" + " " * (width - 35) + "│"
    lines.append(debt_line)

    # Action count and resistance
    resist_pct = int(metrics.resistance_rate * 100) if metrics.action_count > 0 else 0
    action_line = f"│  Actions:     {metrics.action_count} (resistance: {resist_pct}%)"
    action_line = action_line + " " * (width - len(action_line) - 1) + "│"
    lines.append(action_line)

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Injection count and cooldown
    cooldown_remaining = max(0, state.cooldown_until - time.time())
    cooldown_str = f"Cooldown: {int(cooldown_remaining)}s" if cooldown_remaining > 0 else "Ready"
    inj_header = f"│ Injections: {metrics.injection_count}"
    inj_header = (
        inj_header + " " * (width - len(inj_header) - len(cooldown_str) - 2) + cooldown_str + " │"
    )
    lines.append(inj_header)

    # Recent injections (last 3)
    for injection in state.injection_history[-3:]:
        desc = injection.description[: width - 15]
        inj_line = f"│  → {injection.type}: {desc}"
        inj_line = inj_line + " " * (width - len(inj_line) - 1) + "│"
        lines.append(inj_line)

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def project_metrics_to_dict(director: DirectorAgent) -> dict[str, Any]:
    """
    Project director metrics to a dictionary for API/JSON rendering.

    Returns a dictionary suitable for JSON serialization or API responses.
    """
    state = director._state
    metrics = state.metrics

    return {
        "phase": director.phase.name,
        "metrics": {
            "tension_level": metrics.tension_level,
            "consent_debt": metrics.consent_debt,
            "action_count": metrics.action_count,
            "action_rate": metrics.action_rate,
            "resistance_count": metrics.resistance_count,
            "resistance_rate": metrics.resistance_rate,
            "injection_count": metrics.injection_count,
            "session_progress": metrics.session_progress,
        },
        "timing": {
            "session_start": metrics.session_start,
            "last_action_time": metrics.last_action_time,
            "last_injection_time": metrics.last_injection_time,
            "time_since_last_action": metrics.time_since_last_action,
            "time_since_injection": metrics.time_since_injection,
        },
        "cooldown": {
            "until": state.cooldown_until,
            "remaining": max(0, state.cooldown_until - time.time()),
            "is_active": time.time() < state.cooldown_until,
        },
        "injections": [
            {
                "type": inj.type,
                "description": inj.description,
                "intensity": inj.intensity,
                "entropy_seed": inj.entropy_seed,
            }
            for inj in state.injection_history
        ],
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Phases
    "DirectorPhase",
    # Data structures
    "PacingMetrics",
    "SerendipityInjection",
    "TensionEscalation",
    "DifficultyAdjustment",
    "InjectionDecision",
    "DirectorConfig",
    "DirectorState",
    # Agent
    "DirectorAgent",
    "DIRECTOR_POLYNOMIAL",
    # Factory
    "create_director",
    # Telemetry
    "ATTR_DIRECTOR_PHASE",
    "ATTR_DIRECTOR_TENSION",
    "ATTR_DIRECTOR_CONSENT_DEBT",
    "ATTR_DIRECTOR_INJECTION_TYPE",
    # Projections
    "project_director_to_ascii",
    "project_metrics_to_dict",
]
