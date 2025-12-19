"""
WitnessPolynomial: Trust-Gated Behavior as State Machine.

The Witness polynomial models autonomous agent behavior through earned trust:
- L0 READ_ONLY: Observe and project, no modifications
- L1 BOUNDED: Write to .kgents/ directory only
- L2 SUGGESTION: Propose changes, require human confirmation
- L3 AUTONOMOUS: Full Kent-equivalent developer agency

The Insight (from spec/principles.md):
    "The Mirror Test: Does K-gent feel like me on my best day?"
    A good developer doesn't just react—they earn trust through track record.

The phase (OBSERVING, ANALYZING, SUGGESTING, ACTING) is orthogonal to trust:
- At L0, the witness can OBSERVE and ANALYZE but outputs are read-only
- At L3, the witness can ACT autonomously with the same analysis pipeline

Example:
    >>> poly = WITNESS_POLYNOMIAL
    >>> state, output = poly.invoke(
    ...     WitnessState(trust=TrustLevel.READ_ONLY, phase=WitnessPhase.OBSERVING),
    ...     WitnessInput.git_commit(sha="abc123")
    ... )
    >>> print(output)
    WitnessOutput(success=True, thought="Noticed commit abc123...")

See: plans/kgentsd-crown-jewel.md
See: docs/skills/polynomial-agent.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

# =============================================================================
# Trust Level (Earned, Never Granted)
# =============================================================================


class TrustLevel(IntEnum):
    """
    Trust levels for the Witness.

    Trust is earned through consistent, valuable observations.
    Each level unlocks more capabilities.

    The trust escalation model:
    - L0 → L1: 24h of accurate observations
    - L1 → L2: 100 successful bounded operations
    - L2 → L3: 50 confirmed suggestions with >90% acceptance
    """

    READ_ONLY = 0  # Observe and project, no modifications
    BOUNDED = 1  # Write to .kgents/ directory only
    SUGGESTION = 2  # Propose changes, require human confirmation
    AUTONOMOUS = 3  # Full Kent-equivalent developer agency

    @property
    def can_write_kgents(self) -> bool:
        """Can write to .kgents/ directory."""
        return self >= TrustLevel.BOUNDED

    @property
    def can_suggest(self) -> bool:
        """Can propose code changes for human review."""
        return self >= TrustLevel.SUGGESTION

    @property
    def can_act(self) -> bool:
        """Can execute actions without human confirmation."""
        return self >= TrustLevel.AUTONOMOUS

    @property
    def emoji(self) -> str:
        """Visual indicator for trust level."""
        return {
            TrustLevel.READ_ONLY: "👁️",  # Observer
            TrustLevel.BOUNDED: "📁",  # Can write to directory
            TrustLevel.SUGGESTION: "💬",  # Can suggest
            TrustLevel.AUTONOMOUS: "⚡",  # Full agency
        }[self]

    @property
    def description(self) -> str:
        """Human-readable description."""
        return {
            TrustLevel.READ_ONLY: "Observer (read-only)",
            TrustLevel.BOUNDED: "Bounded (writes to .kgents/)",
            TrustLevel.SUGGESTION: "Suggester (proposes changes)",
            TrustLevel.AUTONOMOUS: "Autonomous (full agency)",
        }[self]


# =============================================================================
# Witness Phase (Activity State)
# =============================================================================


class WitnessPhase(Enum):
    """
    Activity phases for the Witness.

    These are orthogonal to trust level—the witness can be in any phase
    at any trust level, but capabilities are gated by trust.
    """

    IDLE = auto()  # Ready for events
    OBSERVING = auto()  # Actively watching event sources
    ANALYZING = auto()  # Processing observations into thoughts
    SUGGESTING = auto()  # Proposing actions (L2+)
    ACTING = auto()  # Executing actions (L3 only)
    CONFIRMING = auto()  # Awaiting human confirmation (L2)


# =============================================================================
# Input Types (Events and Commands)
# =============================================================================


@dataclass(frozen=True)
class GitEvent:
    """A git event detected by the GitWatcher."""

    event_type: str  # commit, push, pull, checkout, merge
    sha: str | None = None
    branch: str | None = None
    message: str | None = None
    author: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class FileEvent:
    """A filesystem event detected by the FileSystemWatcher."""

    event_type: str  # create, modify, delete, rename
    path: str
    is_directory: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class TestEvent:
    """A test event detected by the TestWatcher."""

    event_type: str  # started, passed, failed, skipped, session_complete
    test_id: str | None = None
    duration_ms: int | None = None
    error: str | None = None
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class AgenteseEvent:
    """An AGENTESE event from SynergyBus."""

    path: str  # world.town.citizen.create, self.memory.capture, etc.
    aspect: str  # The aspect invoked
    jewel: str | None = None  # Source jewel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class CIEvent:
    """A CI/CD event from GitHub Actions."""

    event_type: str  # workflow_started, job_complete, workflow_complete, check_failed
    workflow: str | None = None
    job: str | None = None
    status: str | None = None  # success, failure, cancelled
    duration_seconds: int | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class StartCommand:
    """Command to start the witness."""

    watchers: tuple[str, ...] = ("git",)  # Which watchers to start


@dataclass(frozen=True)
class StopCommand:
    """Command to stop the witness."""

    pass


@dataclass(frozen=True)
class EscalateCommand:
    """Request trust escalation."""

    reason: str = ""


@dataclass(frozen=True)
class ConfirmCommand:
    """Human confirmation for L2 suggestions."""

    suggestion_id: str
    approved: bool


@dataclass(frozen=True)
class ActCommand:
    """L3 action command."""

    action: str  # What to do
    target: str | None = None  # Optional target (file, test, etc.)


WitnessEvent = GitEvent | FileEvent | TestEvent | AgenteseEvent | CIEvent
WitnessCommand = StartCommand | StopCommand | EscalateCommand | ConfirmCommand | ActCommand
WitnessInput = WitnessEvent | WitnessCommand


class WitnessInputFactory:
    """Factory for creating witness inputs."""

    @staticmethod
    def git_commit(sha: str, message: str = "", author: str = "") -> GitEvent:
        """Create a git commit event."""
        return GitEvent(event_type="commit", sha=sha, message=message, author=author)

    @staticmethod
    def git_push(branch: str) -> GitEvent:
        """Create a git push event."""
        return GitEvent(event_type="push", branch=branch)

    @staticmethod
    def file_changed(path: str) -> FileEvent:
        """Create a file change event."""
        return FileEvent(event_type="modify", path=path)

    @staticmethod
    def test_failed(test_id: str, error: str) -> TestEvent:
        """Create a test failure event."""
        return TestEvent(event_type="failed", test_id=test_id, error=error)

    @staticmethod
    def test_session(passed: int, failed: int, skipped: int) -> TestEvent:
        """Create a test session complete event."""
        return TestEvent(
            event_type="session_complete",
            passed=passed,
            failed=failed,
            skipped=skipped,
        )

    @staticmethod
    def start(watchers: tuple[str, ...] = ("git",)) -> StartCommand:
        """Create a start command."""
        return StartCommand(watchers=watchers)

    @staticmethod
    def stop() -> StopCommand:
        """Create a stop command."""
        return StopCommand()


# =============================================================================
# Output Types
# =============================================================================


@dataclass(frozen=True)
class Thought:
    """A thought in the thought stream."""

    content: str
    source: str  # Which watcher produced this
    tags: tuple[str, ...] = ()
    timestamp: datetime = field(default_factory=datetime.now)

    def to_diary_line(self) -> str:
        """Format as a diary entry."""
        time_str = self.timestamp.strftime("%H:%M")
        tags_str = " ".join(f"`{t}`" for t in self.tags) if self.tags else ""
        line = f"- *{time_str}* [{self.source}] {self.content}"
        if tags_str:
            line += f" {tags_str}"
        return line


@dataclass(frozen=True)
class Suggestion:
    """A suggested action (L2+)."""

    suggestion_id: str
    action: str
    reason: str
    confidence: float  # 0.0 to 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ActionResult:
    """Result of an executed action (L3)."""

    action_id: str
    action: str
    success: bool
    message: str
    reversible: bool = True
    inverse_action: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WitnessOutput:
    """Output from witness transitions."""

    phase: WitnessPhase
    success: bool
    message: str = ""
    thought: Thought | None = None
    suggestion: Suggestion | None = None
    action_result: ActionResult | None = None
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# Witness State (Composite: Trust + Phase + History)
# =============================================================================


@dataclass
class WitnessState:
    """
    Complete witness state.

    Tracks trust level, current phase, and recent history.
    """

    trust: TrustLevel = TrustLevel.READ_ONLY
    phase: WitnessPhase = WitnessPhase.IDLE
    thoughts: list[Thought] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)
    actions: list[ActionResult] = field(default_factory=list)
    last_active: datetime = field(default_factory=datetime.now)
    observation_count: int = 0
    successful_operations: int = 0
    confirmed_suggestions: int = 0
    total_suggestions: int = 0

    MAX_THOUGHTS = 50
    MAX_SUGGESTIONS = 20
    MAX_ACTIONS = 100

    def add_thought(self, thought: Thought) -> None:
        """Add a thought to history (bounded)."""
        self.thoughts.append(thought)
        if len(self.thoughts) > self.MAX_THOUGHTS:
            self.thoughts = self.thoughts[-self.MAX_THOUGHTS :]
        self.last_active = datetime.now()
        self.observation_count += 1

    def add_suggestion(self, suggestion: Suggestion) -> None:
        """Add a suggestion to history (bounded)."""
        self.suggestions.append(suggestion)
        if len(self.suggestions) > self.MAX_SUGGESTIONS:
            self.suggestions = self.suggestions[-self.MAX_SUGGESTIONS :]
        self.total_suggestions += 1

    def add_action(self, action: ActionResult) -> None:
        """Add an action to history (bounded)."""
        self.actions.append(action)
        if len(self.actions) > self.MAX_ACTIONS:
            self.actions = self.actions[-self.MAX_ACTIONS :]
        if action.success:
            self.successful_operations += 1

    def confirm_suggestion(self, approved: bool) -> None:
        """Record a suggestion confirmation."""
        if approved:
            self.confirmed_suggestions += 1

    @property
    def acceptance_rate(self) -> float:
        """Suggestion acceptance rate."""
        if self.total_suggestions == 0:
            return 0.0
        return self.confirmed_suggestions / self.total_suggestions

    @property
    def can_escalate_to_bounded(self) -> bool:
        """Check if eligible for L0 → L1 escalation."""
        if self.trust != TrustLevel.READ_ONLY:
            return False
        hours_active = (datetime.now() - self.last_active).total_seconds() / 3600
        return self.observation_count >= 100 and hours_active <= 24

    @property
    def can_escalate_to_suggestion(self) -> bool:
        """Check if eligible for L1 → L2 escalation."""
        if self.trust != TrustLevel.BOUNDED:
            return False
        return self.successful_operations >= 100

    @property
    def can_escalate_to_autonomous(self) -> bool:
        """Check if eligible for L2 → L3 escalation."""
        if self.trust != TrustLevel.SUGGESTION:
            return False
        return self.total_suggestions >= 50 and self.acceptance_rate >= 0.9


# =============================================================================
# Direction Function (Trust-Gated Valid Inputs)
# =============================================================================


def witness_directions(state: WitnessState) -> FrozenSet[Any]:
    """
    Valid inputs for each witness state.

    This encodes trust-gated behavior:
    - All levels can receive events
    - L1+ can receive write commands
    - L2+ can receive suggest commands
    - L3 can receive act commands
    """
    # All levels can receive events
    base: set[type] = {GitEvent, FileEvent, TestEvent, AgenteseEvent, CIEvent}

    # Commands
    base.add(StartCommand)
    base.add(StopCommand)
    base.add(EscalateCommand)

    if state.trust >= TrustLevel.SUGGESTION:
        base.add(ConfirmCommand)

    if state.trust >= TrustLevel.AUTONOMOUS:
        base.add(ActCommand)

    return frozenset(base)


# =============================================================================
# Transition Function
# =============================================================================


def witness_transition(
    state: WitnessState, input: WitnessInput
) -> tuple[WitnessState, WitnessOutput]:
    """
    Witness state transition function.

    This is the polynomial core:
    transition: State × Input → (NewState, Output)

    The witness observes, analyzes, and (at higher trust) suggests or acts.
    """
    # Handle commands first
    if isinstance(input, StartCommand):
        return _handle_start(state, input)
    elif isinstance(input, StopCommand):
        return _handle_stop(state, input)
    elif isinstance(input, EscalateCommand):
        return _handle_escalate(state, input)
    elif isinstance(input, ConfirmCommand):
        return _handle_confirm(state, input)
    elif isinstance(input, ActCommand):
        return _handle_act(state, input)

    # Handle events
    if isinstance(input, GitEvent):
        return _handle_git_event(state, input)
    elif isinstance(input, FileEvent):
        return _handle_file_event(state, input)
    elif isinstance(input, TestEvent):
        return _handle_test_event(state, input)
    elif isinstance(input, AgenteseEvent):
        return _handle_agentese_event(state, input)
    elif isinstance(input, CIEvent):
        return _handle_ci_event(state, input)

    # Unknown input
    return state, WitnessOutput(
        phase=state.phase,
        success=False,
        message=f"Unknown input type: {type(input).__name__}",
    )


# =============================================================================
# Transition Handlers
# =============================================================================


def _handle_start(state: WitnessState, cmd: StartCommand) -> tuple[WitnessState, WitnessOutput]:
    """Handle start command."""
    state.phase = WitnessPhase.OBSERVING
    thought = Thought(
        content=f"Started observing with watchers: {', '.join(cmd.watchers)}",
        source="witness",
        tags=("lifecycle", "start"),
    )
    state.add_thought(thought)
    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Witness started with {len(cmd.watchers)} watcher(s)",
        thought=thought,
    )


def _handle_stop(state: WitnessState, cmd: StopCommand) -> tuple[WitnessState, WitnessOutput]:
    """Handle stop command."""
    state.phase = WitnessPhase.IDLE
    thought = Thought(
        content="Stopped observing",
        source="witness",
        tags=("lifecycle", "stop"),
    )
    state.add_thought(thought)
    return state, WitnessOutput(
        phase=WitnessPhase.IDLE,
        success=True,
        message="Witness stopped",
        thought=thought,
    )


def _handle_escalate(
    state: WitnessState, cmd: EscalateCommand
) -> tuple[WitnessState, WitnessOutput]:
    """Handle trust escalation request."""
    current = state.trust
    next_level: TrustLevel | None = None

    if current == TrustLevel.READ_ONLY and state.can_escalate_to_bounded:
        next_level = TrustLevel.BOUNDED
    elif current == TrustLevel.BOUNDED and state.can_escalate_to_suggestion:
        next_level = TrustLevel.SUGGESTION
    elif current == TrustLevel.SUGGESTION and state.can_escalate_to_autonomous:
        next_level = TrustLevel.AUTONOMOUS

    if next_level is not None:
        state.trust = next_level
        thought = Thought(
            content=f"Trust escalated: {current.description} → {next_level.description}",
            source="witness",
            tags=("trust", "escalation"),
        )
        state.add_thought(thought)
        return state, WitnessOutput(
            phase=state.phase,
            success=True,
            message=f"Escalated to {next_level.description}",
            thought=thought,
        )

    # Cannot escalate
    return state, WitnessOutput(
        phase=state.phase,
        success=False,
        message=f"Cannot escalate from {current.description} (requirements not met)",
    )


def _handle_confirm(state: WitnessState, cmd: ConfirmCommand) -> tuple[WitnessState, WitnessOutput]:
    """Handle suggestion confirmation."""
    if state.trust < TrustLevel.SUGGESTION:
        return state, WitnessOutput(
            phase=state.phase,
            success=False,
            message="Confirm requires SUGGESTION trust level",
        )

    state.confirm_suggestion(cmd.approved)
    state.phase = WitnessPhase.OBSERVING

    action = "approved" if cmd.approved else "rejected"
    thought = Thought(
        content=f"Suggestion {cmd.suggestion_id} {action}",
        source="witness",
        tags=("confirmation", action),
    )
    state.add_thought(thought)

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Suggestion {action}",
        thought=thought,
    )


def _handle_act(state: WitnessState, cmd: ActCommand) -> tuple[WitnessState, WitnessOutput]:
    """Handle L3 action command."""
    if state.trust < TrustLevel.AUTONOMOUS:
        return state, WitnessOutput(
            phase=state.phase,
            success=False,
            message="Act requires AUTONOMOUS trust level",
        )

    # Check forbidden actions
    FORBIDDEN_PATTERNS = frozenset(
        {
            "git push --force",
            "rm -rf /",
            "DROP DATABASE",
            "DELETE FROM",
            "kubectl delete namespace",
            "vault token",
            "stripe",
        }
    )

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.lower() in cmd.action.lower():
            return state, WitnessOutput(
                phase=state.phase,
                success=False,
                message=f"Action forbidden: matches pattern '{pattern}'",
            )

    # Execute action (placeholder - actual execution in service layer)
    state.phase = WitnessPhase.ACTING

    import uuid

    action_id = uuid.uuid4().hex[:8]
    action_result = ActionResult(
        action_id=action_id,
        action=cmd.action,
        success=True,  # Placeholder
        message=f"Executed: {cmd.action}",
        reversible=True,
    )
    state.add_action(action_result)

    thought = Thought(
        content=f"Executed action: {cmd.action}",
        source="witness",
        tags=("action", "autonomous"),
    )
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Action executed: {action_id}",
        thought=thought,
        action_result=action_result,
    )


def _handle_git_event(state: WitnessState, event: GitEvent) -> tuple[WitnessState, WitnessOutput]:
    """Handle git events."""
    state.phase = WitnessPhase.ANALYZING

    # Create thought from git event
    tags: tuple[str, ...]
    if event.event_type == "commit":
        content = f"Noticed commit {event.sha[:7] if event.sha else '?'}"
        if event.message:
            content += f": {event.message[:50]}"
        tags = ("git", "commit")
    elif event.event_type == "push":
        content = f"Detected push to {event.branch or 'unknown'}"
        tags = ("git", "push")
    elif event.event_type == "checkout":
        content = f"Switched to branch {event.branch or 'unknown'}"
        tags = ("git", "checkout")
    else:
        content = f"Git event: {event.event_type}"
        tags = ("git",)

    thought = Thought(content=content, source="git", tags=tags)
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Processed git event: {event.event_type}",
        thought=thought,
    )


def _handle_file_event(state: WitnessState, event: FileEvent) -> tuple[WitnessState, WitnessOutput]:
    """Handle filesystem events."""
    state.phase = WitnessPhase.ANALYZING

    content = f"File {event.event_type}: {event.path}"
    thought = Thought(content=content, source="filesystem", tags=("file", event.event_type))
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Processed file event: {event.event_type}",
        thought=thought,
    )


def _handle_test_event(state: WitnessState, event: TestEvent) -> tuple[WitnessState, WitnessOutput]:
    """Handle test events."""
    state.phase = WitnessPhase.ANALYZING

    tags: tuple[str, ...]
    if event.event_type == "session_complete":
        content = (
            f"Test session: {event.passed} passed, {event.failed} failed, {event.skipped} skipped"
        )
        tags = ("tests", "session")
    elif event.event_type == "failed":
        content = f"Test failed: {event.test_id}"
        if event.error:
            content += f" ({event.error[:50]})"
        tags = ("tests", "failure")
    else:
        content = f"Test {event.event_type}: {event.test_id or '?'}"
        tags = ("tests",)

    thought = Thought(content=content, source="tests", tags=tags)
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Processed test event: {event.event_type}",
        thought=thought,
    )


def _handle_agentese_event(
    state: WitnessState, event: AgenteseEvent
) -> tuple[WitnessState, WitnessOutput]:
    """Handle AGENTESE events."""
    state.phase = WitnessPhase.ANALYZING

    content = f"AGENTESE: {event.path}.{event.aspect}"
    if event.jewel:
        content += f" (from {event.jewel})"
    thought = Thought(content=content, source="agentese", tags=("agentese", event.jewel or ""))
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Processed AGENTESE event: {event.path}",
        thought=thought,
    )


def _handle_ci_event(state: WitnessState, event: CIEvent) -> tuple[WitnessState, WitnessOutput]:
    """Handle CI/CD events."""
    state.phase = WitnessPhase.ANALYZING

    tags: tuple[str, ...]
    if event.event_type == "workflow_complete":
        content = f"CI workflow '{event.workflow}' {event.status}"
        if event.duration_seconds:
            content += f" ({event.duration_seconds}s)"
        tags = ("ci", event.status or "unknown")
    elif event.event_type == "check_failed":
        content = f"CI check failed: {event.job or event.workflow}"
        tags = ("ci", "failure")
    else:
        content = f"CI event: {event.event_type}"
        tags = ("ci",)

    thought = Thought(content=content, source="ci", tags=tags)
    state.add_thought(thought)
    state.phase = WitnessPhase.OBSERVING

    return state, WitnessOutput(
        phase=WitnessPhase.OBSERVING,
        success=True,
        message=f"Processed CI event: {event.event_type}",
        thought=thought,
    )


# =============================================================================
# Polynomial Construction
# =============================================================================


class WitnessPolynomial:
    """
    The Witness polynomial agent.

    Uses composite state (WitnessState) that tracks trust, phase, and history.
    Trust-gated behavior is encoded in directions and transitions.
    """

    def __init__(self) -> None:
        self.name = "WitnessPolynomial"

    @property
    def positions(self) -> FrozenSet[TrustLevel]:
        """Trust levels are the primary positions."""
        return frozenset(TrustLevel)

    def directions(self, state: WitnessState) -> FrozenSet[Any]:
        """Valid inputs at this state."""
        return witness_directions(state)

    def transition(
        self, state: WitnessState, input: WitnessInput
    ) -> tuple[WitnessState, WitnessOutput]:
        """Execute state transition."""
        return witness_transition(state, input)

    def invoke(
        self, state: WitnessState, input: WitnessInput
    ) -> tuple[WitnessState, WitnessOutput]:
        """Invoke the polynomial (alias for transition)."""
        return self.transition(state, input)


# Global polynomial instance
WITNESS_POLYNOMIAL = WitnessPolynomial()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Trust and Phase
    "TrustLevel",
    "WitnessPhase",
    # Events
    "GitEvent",
    "FileEvent",
    "TestEvent",
    "AgenteseEvent",
    "CIEvent",
    # Commands
    "StartCommand",
    "StopCommand",
    "EscalateCommand",
    "ConfirmCommand",
    "ActCommand",
    # Input factory
    "WitnessInputFactory",
    # Output types
    "Thought",
    "Suggestion",
    "ActionResult",
    "WitnessOutput",
    # State and Polynomial
    "WitnessState",
    "WitnessPolynomial",
    "WITNESS_POLYNOMIAL",
]
