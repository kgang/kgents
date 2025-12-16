"""
GardenerSession: Polynomial Agent for Development Sessions.

The GardenerSession is a state machine that cycles through:
    SENSE → ACT → REFLECT → SENSE → ...

Each position has distinct affordances:
- SENSE: Gather context (forest, codebase, memory)
- ACT: Execute intent (write code, create plans)
- REFLECT: Consolidate learnings (update meta.md, forest)

This is the polynomial functor representation of N-Phase development:
- Positions: {SENSE, ACT, REFLECT}
- Directions: Intent × State → Valid transitions
- Emissions: Artifacts (code, docs, plans)

See: plans/core-apps/the-gardener.md §IV.1
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, FrozenSet

from agents.poly.protocol import PolyAgent
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

if TYPE_CHECKING:
    from .persistence import SessionStore


# =============================================================================
# OTEL Telemetry Constants
# =============================================================================

_tracer: trace.Tracer | None = None


def _get_session_tracer() -> trace.Tracer:
    """Get the GardenerSession tracer, creating if needed."""
    global _tracer
    if _tracer is None:
        _tracer = trace.get_tracer("kgents.gardener.session", "0.1.0")
    return _tracer


# Span attribute constants
ATTR_SESSION_ID = "gardener.session.id"
ATTR_SESSION_NAME = "gardener.session.name"
ATTR_SESSION_PHASE = "gardener.session.phase"
ATTR_SESSION_PLAN = "gardener.session.plan_path"
ATTR_SESSION_ACTION = "gardener.session.action"
ATTR_DURATION_MS = "gardener.duration_ms"


# =============================================================================
# Session Phases (Polynomial Positions)
# =============================================================================


class SessionPhase(Enum):
    """
    Phases of the GardenerSession polynomial.

    The session cycles through: SENSE → ACT → REFLECT → SENSE
    This mirrors the N-Phase development cycle at the micro level.

    From the plan:
        "An N-Phase session is not a passive data structure—it is a
        polynomial agent that maintains its own state."
    """

    SENSE = auto()  # Gather context: forest, codebase, memory
    ACT = auto()  # Execute intent: write code, create docs
    REFLECT = auto()  # Consolidate: update meta.md, forest


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class SessionIntent:
    """
    What the user wants to accomplish.

    Intent is provided when creating or resuming a session.
    It guides the SENSE phase context gathering.
    """

    description: str  # Natural language description
    plan_path: str | None = None  # Link to forest plan file
    target_files: list[str] = field(default_factory=list)  # Files to modify
    constraints: list[str] = field(default_factory=list)  # User constraints
    priority: str = "medium"  # low, medium, high
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "description": self.description,
            "plan_path": self.plan_path,
            "target_files": self.target_files,
            "constraints": self.constraints,
            "priority": self.priority,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionIntent":
        """Create from dictionary."""
        return cls(
            description=data.get("description", ""),
            plan_path=data.get("plan_path"),
            target_files=data.get("target_files", []),
            constraints=data.get("constraints", []),
            priority=data.get("priority", "medium"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SessionArtifact:
    """
    Output from a session phase.

    Artifacts accumulate during ACT and are consolidated in REFLECT.
    """

    artifact_type: str  # "code", "doc", "plan", "learning", "test"
    path: str | None = None  # File path if applicable
    content: str | None = None  # Content for in-memory artifacts
    description: str = ""
    success: bool = True
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "artifact_type": self.artifact_type,
            "path": self.path,
            "content": self.content,
            "description": self.description,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionArtifact":
        """Create from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now()

        return cls(
            artifact_type=data.get("artifact_type", "unknown"),
            path=data.get("path"),
            content=data.get("content"),
            description=data.get("description", ""),
            success=data.get("success", True),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
            created_at=created_at,
        )


@dataclass
class SessionState:
    """
    Mutable state for GardenerSession.

    Captured by closure in the transition function.
    Persisted to SQLite via SessionStore.
    """

    # Identity
    session_id: str = ""
    name: str = ""
    plan_path: str | None = None

    # Context gathered in SENSE
    forest_context: dict[str, Any] = field(default_factory=dict)
    codebase_context: dict[str, Any] = field(default_factory=dict)
    memory_context: dict[str, Any] = field(default_factory=dict)

    # Current intent
    intent: SessionIntent | None = None

    # Artifacts accumulated in ACT
    artifacts: list[SessionArtifact] = field(default_factory=list)

    # Learnings collected for REFLECT
    learnings: list[str] = field(default_factory=list)

    # Timing
    phase_started_at: datetime = field(default_factory=datetime.now)
    session_started_at: datetime = field(default_factory=datetime.now)

    # Counters
    sense_count: int = 0
    act_count: int = 0
    reflect_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "session_id": self.session_id,
            "name": self.name,
            "plan_path": self.plan_path,
            "forest_context": self.forest_context,
            "codebase_context": self.codebase_context,
            "memory_context": self.memory_context,
            "intent": self.intent.to_dict() if self.intent else None,
            "artifacts": [a.to_dict() for a in self.artifacts],
            "learnings": self.learnings,
            "phase_started_at": self.phase_started_at.isoformat(),
            "session_started_at": self.session_started_at.isoformat(),
            "sense_count": self.sense_count,
            "act_count": self.act_count,
            "reflect_count": self.reflect_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SessionState":
        """Create from dictionary."""

        def parse_dt(val: str | None) -> datetime:
            if val and isinstance(val, str):
                return datetime.fromisoformat(val)
            return datetime.now()

        intent_data = data.get("intent")
        intent = SessionIntent.from_dict(intent_data) if intent_data else None

        artifacts = [SessionArtifact.from_dict(a) for a in data.get("artifacts", [])]

        return cls(
            session_id=data.get("session_id", ""),
            name=data.get("name", ""),
            plan_path=data.get("plan_path"),
            forest_context=data.get("forest_context", {}),
            codebase_context=data.get("codebase_context", {}),
            memory_context=data.get("memory_context", {}),
            intent=intent,
            artifacts=artifacts,
            learnings=data.get("learnings", []),
            phase_started_at=parse_dt(data.get("phase_started_at")),
            session_started_at=parse_dt(data.get("session_started_at")),
            sense_count=data.get("sense_count", 0),
            act_count=data.get("act_count", 0),
            reflect_count=data.get("reflect_count", 0),
        )

    def reset_for_phase(self, phase: SessionPhase) -> None:
        """Reset phase-specific state."""
        self.phase_started_at = datetime.now()
        if phase == SessionPhase.SENSE:
            self.sense_count += 1
        elif phase == SessionPhase.ACT:
            self.act_count += 1
        elif phase == SessionPhase.REFLECT:
            self.reflect_count += 1


@dataclass
class SessionConfig:
    """Configuration for GardenerSession behavior."""

    # Phase timeouts (seconds)
    sense_timeout: float = 60.0
    act_timeout: float = 300.0
    reflect_timeout: float = 60.0

    # Auto-advance settings
    auto_advance_on_sense: bool = False
    auto_advance_on_act: bool = False

    # Persistence
    persist_on_advance: bool = True
    persist_interval: float = 30.0  # Seconds between auto-saves


# =============================================================================
# Direction Functions
# =============================================================================


def _session_directions(phase: SessionPhase) -> FrozenSet[Any]:
    """
    Valid inputs for each session phase.

    This encodes what actions are valid at each phase.
    Uses `Any` to accept both string commands and dict inputs.
    Command validation happens in the transition handler.

    Per meta.md: "DirectorAgent passes dicts to invoke"
    """
    # Use Any to accept both strings and dicts
    # The actual command is extracted and validated in the transition handler
    match phase:
        case SessionPhase.SENSE:
            # Valid commands: gather, advance, set_intent, manifest, abort
            return frozenset({Any})
        case SessionPhase.ACT:
            # Valid commands: execute, artifact, advance, rollback, manifest, abort
            return frozenset({Any})
        case SessionPhase.REFLECT:
            # Valid commands: learn, consolidate, advance, complete, manifest, abort
            return frozenset({Any})


# =============================================================================
# Transition Functions
# =============================================================================


def _create_session_transition(
    config: SessionConfig,
    state: SessionState,
) -> Callable[[SessionPhase, Any], tuple[SessionPhase, Any]]:
    """
    Create the transition function for the session polynomial.

    The transition function captures the config and mutable state
    via closure, allowing the polynomial to maintain context.
    """

    def transition(phase: SessionPhase, input: Any) -> tuple[SessionPhase, Any]:
        """
        Session state transition function.

        transition: Phase × Input → (NewPhase, Output)
        """
        match phase:
            case SessionPhase.SENSE:
                return _handle_sense(phase, input, config, state)
            case SessionPhase.ACT:
                return _handle_act(phase, input, config, state)
            case SessionPhase.REFLECT:
                return _handle_reflect(phase, input, config, state)

    return transition


def _handle_sense(
    phase: SessionPhase,
    input: Any,
    config: SessionConfig,
    state: SessionState,
) -> tuple[SessionPhase, Any]:
    """Handle SENSE phase transitions."""
    cmd = _extract_command(input)

    match cmd:
        case "gather":
            # Gather context (in production, would call AGENTESE paths)
            context_type = (
                input.get("type", "all") if isinstance(input, dict) else "all"
            )
            gathered = {
                "type": context_type,
                "timestamp": datetime.now().isoformat(),
            }

            if context_type in ("all", "forest"):
                state.forest_context["gathered_at"] = datetime.now().isoformat()
            if context_type in ("all", "codebase"):
                state.codebase_context["gathered_at"] = datetime.now().isoformat()
            if context_type in ("all", "memory"):
                state.memory_context["gathered_at"] = datetime.now().isoformat()

            return SessionPhase.SENSE, {
                "status": "gathered",
                "context": gathered,
            }

        case "set_intent":
            # Set or update intent
            if isinstance(input, dict) and "intent" in input:
                intent_data = input["intent"]
                if isinstance(intent_data, SessionIntent):
                    state.intent = intent_data
                elif isinstance(intent_data, dict):
                    state.intent = SessionIntent.from_dict(intent_data)
                else:
                    state.intent = SessionIntent(description=str(intent_data))
            return SessionPhase.SENSE, {
                "status": "intent_set",
                "intent": state.intent.to_dict() if state.intent else None,
            }

        case "advance":
            # Move to ACT phase
            state.reset_for_phase(SessionPhase.ACT)
            return SessionPhase.ACT, {
                "status": "advanced",
                "from_phase": "SENSE",
                "to_phase": "ACT",
            }

        case "manifest":
            return SessionPhase.SENSE, {
                "status": "manifest",
                "phase": "SENSE",
                "state": state.to_dict(),
            }

        case "abort":
            return SessionPhase.SENSE, {
                "status": "aborted",
                "phase": "SENSE",
            }

        case _:
            return SessionPhase.SENSE, {
                "status": "unknown_command",
                "command": cmd,
            }


def _handle_act(
    phase: SessionPhase,
    input: Any,
    config: SessionConfig,
    state: SessionState,
) -> tuple[SessionPhase, Any]:
    """Handle ACT phase transitions."""
    cmd = _extract_command(input)

    match cmd:
        case "execute":
            # Execute an action (in production, would invoke tools)
            action = (
                input.get("action", "unknown") if isinstance(input, dict) else "unknown"
            )
            return SessionPhase.ACT, {
                "status": "executed",
                "action": action,
            }

        case "artifact":
            # Record an artifact
            if isinstance(input, dict) and "artifact" in input:
                artifact_data = input["artifact"]
                if isinstance(artifact_data, SessionArtifact):
                    state.artifacts.append(artifact_data)
                elif isinstance(artifact_data, dict):
                    state.artifacts.append(SessionArtifact.from_dict(artifact_data))
            return SessionPhase.ACT, {
                "status": "artifact_recorded",
                "artifact_count": len(state.artifacts),
            }

        case "advance":
            # Move to REFLECT phase
            state.reset_for_phase(SessionPhase.REFLECT)
            return SessionPhase.REFLECT, {
                "status": "advanced",
                "from_phase": "ACT",
                "to_phase": "REFLECT",
                "artifacts_count": len(state.artifacts),
            }

        case "rollback":
            # Back to SENSE for more context
            state.reset_for_phase(SessionPhase.SENSE)
            return SessionPhase.SENSE, {
                "status": "rolled_back",
                "from_phase": "ACT",
                "to_phase": "SENSE",
            }

        case "manifest":
            return SessionPhase.ACT, {
                "status": "manifest",
                "phase": "ACT",
                "state": state.to_dict(),
            }

        case "abort":
            return SessionPhase.ACT, {
                "status": "aborted",
                "phase": "ACT",
            }

        case _:
            return SessionPhase.ACT, {
                "status": "unknown_command",
                "command": cmd,
            }


def _handle_reflect(
    phase: SessionPhase,
    input: Any,
    config: SessionConfig,
    state: SessionState,
) -> tuple[SessionPhase, Any]:
    """Handle REFLECT phase transitions."""
    cmd = _extract_command(input)

    match cmd:
        case "learn":
            # Record a learning
            if isinstance(input, dict) and "learning" in input:
                learning = input["learning"]
                if isinstance(learning, str):
                    state.learnings.append(learning)
                elif isinstance(learning, list):
                    state.learnings.extend(learning)
            return SessionPhase.REFLECT, {
                "status": "learned",
                "learning_count": len(state.learnings),
            }

        case "consolidate":
            # Consolidate learnings (would update meta.md in production)
            return SessionPhase.REFLECT, {
                "status": "consolidated",
                "learnings": state.learnings,
                "artifacts": [a.to_dict() for a in state.artifacts],
            }

        case "advance":
            # Start new cycle back to SENSE
            state.reset_for_phase(SessionPhase.SENSE)
            return SessionPhase.SENSE, {
                "status": "advanced",
                "from_phase": "REFLECT",
                "to_phase": "SENSE",
                "cycle_complete": True,
            }

        case "complete":
            # End the session
            return SessionPhase.REFLECT, {
                "status": "completed",
                "learnings": state.learnings,
                "artifacts": [a.to_dict() for a in state.artifacts],
                "cycles": state.reflect_count,
            }

        case "manifest":
            return SessionPhase.REFLECT, {
                "status": "manifest",
                "phase": "REFLECT",
                "state": state.to_dict(),
            }

        case "abort":
            return SessionPhase.REFLECT, {
                "status": "aborted",
                "phase": "REFLECT",
            }

        case _:
            return SessionPhase.REFLECT, {
                "status": "unknown_command",
                "command": cmd,
            }


def _extract_command(input: Any) -> str:
    """Extract command from various input formats."""
    if isinstance(input, str):
        return input
    if isinstance(input, dict):
        return input.get("cmd", input.get("command", "unknown"))
    return "unknown"


# =============================================================================
# GardenerSession Agent Class
# =============================================================================


class GardenerSession:
    """
    High-level wrapper for the GardenerSession polynomial.

    Provides a more ergonomic async interface while using
    the polynomial state machine internally.

    Usage:
        session = GardenerSession.create(name="My Feature", plan_path="plans/foo.md")

        # Gather context
        await session.sense()

        # Set intent
        await session.set_intent(SessionIntent(description="Implement X"))

        # Advance to ACT
        await session.advance()

        # Record work
        await session.record_artifact(SessionArtifact(artifact_type="code", path="foo.py"))

        # Advance to REFLECT
        await session.advance()

        # Record learnings
        await session.learn("Pattern X works well for Y")

        # Complete or cycle
        await session.complete()
    """

    def __init__(
        self,
        polynomial: PolyAgent[SessionPhase, Any, Any],
        state: SessionState,
        config: SessionConfig,
        store: "SessionStore | None" = None,
    ) -> None:
        self._poly = polynomial
        self._state = state
        self._config = config
        self._store = store
        self._phase = SessionPhase.SENSE

    @classmethod
    def create(
        cls,
        name: str,
        plan_path: str | None = None,
        config: SessionConfig | None = None,
        store: "SessionStore | None" = None,
    ) -> "GardenerSession":
        """Create a new GardenerSession."""
        config = config or SessionConfig()
        state = SessionState(
            session_id=str(uuid.uuid4()),
            name=name,
            plan_path=plan_path,
            session_started_at=datetime.now(),
            phase_started_at=datetime.now(),
        )
        transition = _create_session_transition(config, state)

        polynomial: PolyAgent[SessionPhase, Any, Any] = PolyAgent(
            name="GardenerSession",
            positions=frozenset(SessionPhase),
            _directions=_session_directions,
            _transition=transition,
        )

        return cls(polynomial, state, config, store)

    @classmethod
    def from_state(
        cls,
        state: SessionState,
        phase: SessionPhase,
        config: SessionConfig | None = None,
        store: "SessionStore | None" = None,
    ) -> "GardenerSession":
        """Resume a session from persisted state."""
        config = config or SessionConfig()
        transition = _create_session_transition(config, state)

        polynomial: PolyAgent[SessionPhase, Any, Any] = PolyAgent(
            name="GardenerSession",
            positions=frozenset(SessionPhase),
            _directions=_session_directions,
            _transition=transition,
        )

        session = cls(polynomial, state, config, store)
        session._phase = phase
        return session

    # === Properties ===

    @property
    def session_id(self) -> str:
        """Session ID."""
        return self._state.session_id

    @property
    def name(self) -> str:
        """Session name."""
        return self._state.name

    @property
    def plan_path(self) -> str | None:
        """Linked plan file path."""
        return self._state.plan_path

    @property
    def phase(self) -> SessionPhase:
        """Current session phase."""
        return self._phase

    @property
    def state(self) -> SessionState:
        """Current session state."""
        return self._state

    @property
    def config(self) -> SessionConfig:
        """Session configuration."""
        return self._config

    @property
    def intent(self) -> SessionIntent | None:
        """Current intent."""
        return self._state.intent

    @property
    def artifacts(self) -> list[SessionArtifact]:
        """Accumulated artifacts."""
        return list(self._state.artifacts)

    @property
    def learnings(self) -> list[str]:
        """Accumulated learnings."""
        return list(self._state.learnings)

    # === Core Operations ===

    async def sense(self, context_type: str = "all") -> dict[str, Any]:
        """Gather context in SENSE phase."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.sense") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)
            span.set_attribute(ATTR_SESSION_PHASE, self._phase.name)

            if self._phase != SessionPhase.SENSE:
                span.set_status(Status(StatusCode.ERROR, "Not in SENSE phase"))
                return {"status": "error", "message": "Not in SENSE phase"}

            self._phase, result = self._poly.invoke(
                self._phase,
                {
                    "cmd": "gather",
                    "type": context_type,
                },
            )

            span.set_status(Status(StatusCode.OK))
            return result

    async def set_intent(
        self, intent: SessionIntent | dict[str, Any]
    ) -> dict[str, Any]:
        """Set the session intent."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.set_intent") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)

            self._phase, result = self._poly.invoke(
                self._phase,
                {
                    "cmd": "set_intent",
                    "intent": intent,
                },
            )

            span.set_status(Status(StatusCode.OK))
            return result

    async def advance(self) -> dict[str, Any]:
        """Advance to the next phase."""
        tracer = _get_session_tracer()
        start_time = time.perf_counter()

        with tracer.start_as_current_span("session.advance") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)
            span.set_attribute(ATTR_SESSION_PHASE, self._phase.name)

            old_phase = self._phase
            self._phase, result = self._poly.invoke(self._phase, "advance")

            span.set_attribute("session.new_phase", self._phase.name)
            span.set_attribute(
                ATTR_DURATION_MS, (time.perf_counter() - start_time) * 1000
            )

            # Persist if configured
            if self._config.persist_on_advance and self._store:
                await self._store.advance_phase(
                    self.session_id,
                    old_phase.name,
                    self._phase.name,
                    result,
                )

            span.set_status(Status(StatusCode.OK))
            return result

    async def record_artifact(
        self, artifact: SessionArtifact | dict[str, Any]
    ) -> dict[str, Any]:
        """Record an artifact in ACT phase."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.record_artifact") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)

            if self._phase != SessionPhase.ACT:
                span.set_status(Status(StatusCode.ERROR, "Not in ACT phase"))
                return {"status": "error", "message": "Not in ACT phase"}

            self._phase, result = self._poly.invoke(
                self._phase,
                {
                    "cmd": "artifact",
                    "artifact": artifact,
                },
            )

            span.set_status(Status(StatusCode.OK))
            return result

    async def learn(self, learning: str | list[str]) -> dict[str, Any]:
        """Record a learning in REFLECT phase."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.learn") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)

            if self._phase != SessionPhase.REFLECT:
                span.set_status(Status(StatusCode.ERROR, "Not in REFLECT phase"))
                return {"status": "error", "message": "Not in REFLECT phase"}

            self._phase, result = self._poly.invoke(
                self._phase,
                {
                    "cmd": "learn",
                    "learning": learning,
                },
            )

            span.set_status(Status(StatusCode.OK))
            return result

    async def consolidate(self) -> dict[str, Any]:
        """Consolidate learnings in REFLECT phase."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.consolidate") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)

            if self._phase != SessionPhase.REFLECT:
                span.set_status(Status(StatusCode.ERROR, "Not in REFLECT phase"))
                return {"status": "error", "message": "Not in REFLECT phase"}

            self._phase, result = self._poly.invoke(self._phase, "consolidate")

            span.set_status(Status(StatusCode.OK))
            return result

    async def complete(self) -> dict[str, Any]:
        """Complete the session."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.complete") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)
            span.set_attribute(ATTR_SESSION_PHASE, self._phase.name)

            if self._phase != SessionPhase.REFLECT:
                span.set_status(
                    Status(StatusCode.ERROR, "Must be in REFLECT phase to complete")
                )
                return {
                    "status": "error",
                    "message": "Must be in REFLECT phase to complete",
                }

            self._phase, result = self._poly.invoke(self._phase, "complete")

            # Persist completion if configured
            if self._store:
                await self._store.complete(
                    self.session_id,
                    result,
                )

            span.set_status(Status(StatusCode.OK))
            return result

    async def manifest(self) -> dict[str, Any]:
        """View current session state."""
        self._phase, result = self._poly.invoke(self._phase, "manifest")
        return result

    async def abort(self) -> dict[str, Any]:
        """Abort the session."""
        self._phase, result = self._poly.invoke(self._phase, "abort")
        return result

    async def rollback(self) -> dict[str, Any]:
        """Roll back from ACT to SENSE."""
        tracer = _get_session_tracer()
        with tracer.start_as_current_span("session.rollback") as span:
            span.set_attribute(ATTR_SESSION_ID, self.session_id)

            if self._phase != SessionPhase.ACT:
                span.set_status(
                    Status(StatusCode.ERROR, "Can only rollback from ACT phase")
                )
                return {
                    "status": "error",
                    "message": "Can only rollback from ACT phase",
                }

            self._phase, result = self._poly.invoke(self._phase, "rollback")

            span.set_status(Status(StatusCode.OK))
            return result

    # === Persistence Integration ===

    async def save(self) -> bool:
        """Save current state to store."""
        if not self._store:
            return False

        return await self._store.update(
            self.session_id,
            phase=self._phase.name,
            state=self._state.to_dict(),
            intent=self._state.intent.to_dict() if self._state.intent else None,
        )


# =============================================================================
# Factory Functions
# =============================================================================


def create_gardener_session(
    name: str,
    plan_path: str | None = None,
    config: SessionConfig | None = None,
    store: "SessionStore | None" = None,
) -> GardenerSession:
    """
    Create a new GardenerSession.

    Args:
        name: Human-readable session name
        plan_path: Path to linked forest plan file
        config: Optional configuration
        store: Optional persistence store

    Returns:
        A new GardenerSession ready to use.
    """
    return GardenerSession.create(name, plan_path, config, store)


# =============================================================================
# Singleton Polynomial (for protocol compliance)
# =============================================================================

_default_state = SessionState()
_default_config = SessionConfig()

GARDENER_SESSION_POLYNOMIAL: PolyAgent[SessionPhase, Any, Any] = PolyAgent(
    name="GardenerSessionPolynomial",
    positions=frozenset(SessionPhase),
    _directions=_session_directions,
    _transition=_create_session_transition(_default_config, _default_state),
)
"""
The GardenerSession polynomial.

Use create_gardener_session() for instances with isolated state.
This singleton is for protocol compliance verification only.
"""


# =============================================================================
# CLI Projection Functions
# =============================================================================


def project_session_to_ascii(
    session: GardenerSession,
    width: int = 60,
) -> str:
    """
    Project session state to ASCII art for CLI rendering.

    Layout:
        ┌──────────────────────────────────────────────────────────┐
        │ 🌱 SESSION [SENSE]                    Coalition Forge API │
        ├──────────────────────────────────────────────────────────┤
        │                                                          │
        │  Phase: SENSE → ACT → REFLECT                            │
        │         ████                                             │
        │                                                          │
        │  Intent: Implement Coalition Forge API                   │
        │  Plan: plans/core-apps/coalition-forge.md                │
        │                                                          │
        │  Cycles: 2  |  Artifacts: 5  |  Learnings: 3             │
        │                                                          │
        └──────────────────────────────────────────────────────────┘
    """
    state = session.state
    phase = session.phase

    lines: list[str] = []

    # Top border
    border = "┌" + "─" * (width - 2) + "┐"
    lines.append(border)

    # Header with phase and name
    phase_emoji = {"SENSE": "👁️", "ACT": "⚡", "REFLECT": "💭"}.get(phase.name, "🌱")
    phase_str = f"{phase_emoji} SESSION [{phase.name}]"
    name_str = state.name[: width - len(phase_str) - 6] if state.name else ""
    padding = width - len(phase_str) - len(name_str) - 4
    header = f"│ {phase_str}{' ' * padding}{name_str} │"
    lines.append(header)

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Phase progress
    phase_map = {
        SessionPhase.SENSE: (1, 3),
        SessionPhase.ACT: (2, 3),
        SessionPhase.REFLECT: (3, 3),
    }
    current, total = phase_map.get(phase, (0, 3))
    progress_bar = "█" * current + "░" * (total - current)
    phase_line = "│  Phase: SENSE → ACT → REFLECT"
    phase_line = phase_line + " " * (width - len(phase_line) - 1) + "│"
    lines.append(phase_line)

    progress_line = f"│         {progress_bar}"
    progress_line = progress_line + " " * (width - len(progress_line) - 1) + "│"
    lines.append(progress_line)

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Intent
    intent_str = state.intent.description[: width - 12] if state.intent else "Not set"
    intent_line = f"│  Intent: {intent_str}"
    intent_line = intent_line + " " * (width - len(intent_line) - 1) + "│"
    lines.append(intent_line)

    # Plan path
    plan_str = state.plan_path[: width - 10] if state.plan_path else "None"
    plan_line = f"│  Plan: {plan_str}"
    plan_line = plan_line + " " * (width - len(plan_line) - 1) + "│"
    lines.append(plan_line)

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Stats
    stats_str = f"Cycles: {state.reflect_count}  |  Artifacts: {len(state.artifacts)}  |  Learnings: {len(state.learnings)}"
    stats_line = f"│  {stats_str}"
    stats_line = stats_line + " " * (width - len(stats_line) - 1) + "│"
    lines.append(stats_line)

    # Blank line
    lines.append("│" + " " * (width - 2) + "│")

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def project_session_to_dict(session: GardenerSession) -> dict[str, Any]:
    """
    Project session state to a dictionary for API/JSON rendering.

    Returns a dictionary suitable for JSON serialization or API responses.
    """
    state = session.state

    return {
        "id": session.session_id,
        "name": session.name,
        "plan_path": session.plan_path,
        "phase": session.phase.name,
        "intent": state.intent.to_dict() if state.intent else None,
        "artifacts": [a.to_dict() for a in state.artifacts],
        "learnings": state.learnings,
        "context": {
            "forest": state.forest_context,
            "codebase": state.codebase_context,
            "memory": state.memory_context,
        },
        "timing": {
            "session_started_at": state.session_started_at.isoformat(),
            "phase_started_at": state.phase_started_at.isoformat(),
        },
        "counters": {
            "sense_count": state.sense_count,
            "act_count": state.act_count,
            "reflect_count": state.reflect_count,
        },
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Phases
    "SessionPhase",
    # Data structures
    "SessionState",
    "SessionConfig",
    "SessionIntent",
    "SessionArtifact",
    # Agent
    "GardenerSession",
    "GARDENER_SESSION_POLYNOMIAL",
    # Factory
    "create_gardener_session",
    # Telemetry
    "ATTR_SESSION_ID",
    "ATTR_SESSION_NAME",
    "ATTR_SESSION_PHASE",
    "ATTR_SESSION_PLAN",
    # Projections
    "project_session_to_ascii",
    "project_session_to_dict",
]
