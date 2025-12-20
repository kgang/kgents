"""
Witness Reactor: Event-to-Workflow Mapping.

"When something happens, the daemon knows what to do."

The Reactor is the missing link between events and workflows.
It maps external events (git commits, test failures, CI status)
to appropriate workflow responses.

Pattern: Event-Driven Architecture (data-bus-integration.md)
The reactor subscribes to event sources and triggers workflows.

Event → Workflow Mappings (default):
- GitCommit → CODE_CHANGE_RESPONSE (L2+)
- TestFailure → TEST_FAILURE_RESPONSE (L3)
- PROpened → PR_REVIEW_WORKFLOW (L1+)
- CIFailure → CI_MONITOR (L0)
- SessionStart → MORNING_STANDUP (L0)
- HealthTick → HEALTH_CHECK (L0)
- CrystallizationReady → CRYSTALLIZATION (L1+)

Trust Gating:
Each mapping has a minimum trust level. If current trust is below
the threshold, the reaction is queued for human approval.

Philosophy:
    "The daemon notices patterns and responds—but knows when NOT to."

See: plans/kgentsd-cross-jewel.md
See: docs/skills/data-bus-integration.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol
from uuid import uuid4

from .polynomial import TrustLevel
from .workflows import (
    CI_MONITOR,
    CODE_CHANGE_RESPONSE,
    CRYSTALLIZATION,
    HEALTH_CHECK,
    MORNING_STANDUP,
    PR_REVIEW_WORKFLOW,
    TEST_FAILURE_RESPONSE,
    WorkflowTemplate,
)

if TYPE_CHECKING:
    from protocols.agentese.node import Observer

    from .invoke import JewelInvoker
    from .pipeline import PipelineResult, PipelineRunner
    from .schedule import WitnessScheduler


logger = logging.getLogger(__name__)


# =============================================================================
# Event Types
# =============================================================================


class EventSource(Enum):
    """Sources of events the reactor can subscribe to."""

    GIT = auto()  # Git commits, pushes, branches
    TEST = auto()  # Test runs, failures, coverage
    CI = auto()  # CI/CD pipeline status
    PR = auto()  # Pull request events
    SESSION = auto()  # Developer session events
    TIMER = auto()  # Periodic timer events
    HEALTH = auto()  # Health check events
    CRYSTAL = auto()  # Crystallization triggers


@dataclass(frozen=True)
class Event:
    """
    A generic event that the reactor can respond to.

    Events are immutable records of something that happened.
    The reactor matches events to workflows based on event_type.
    """

    event_id: str = field(default_factory=lambda: f"evt-{uuid4().hex[:12]}")
    source: EventSource = EventSource.TIMER
    event_type: str = ""  # e.g., "commit", "test_failure", "pr_opened"
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Frozen dataclass, so we can't modify after creation
        pass


# Convenience event constructors
def git_commit_event(
    sha: str,
    message: str,
    author: str = "",
    files_changed: list[str] | None = None,
) -> Event:
    """Create a git commit event."""
    return Event(
        source=EventSource.GIT,
        event_type="commit",
        data={
            "sha": sha,
            "message": message,
            "author": author,
            "files_changed": files_changed or [],
        },
    )


def create_test_failure_event(
    test_file: str,
    test_name: str,
    error_message: str = "",
    traceback: str = "",
) -> Event:
    """Create a test failure event."""
    return Event(
        source=EventSource.TEST,
        event_type="failure",
        data={
            "test_file": test_file,
            "test_name": test_name,
            "error_message": error_message,
            "traceback": traceback,
        },
    )


def pr_opened_event(
    pr_number: int,
    title: str,
    author: str = "",
    base_branch: str = "main",
    head_branch: str = "",
) -> Event:
    """Create a PR opened event."""
    return Event(
        source=EventSource.PR,
        event_type="opened",
        data={
            "pr_number": pr_number,
            "title": title,
            "author": author,
            "base_branch": base_branch,
            "head_branch": head_branch,
        },
    )


def ci_status_event(
    status: str,
    pipeline_name: str = "",
    url: str = "",
) -> Event:
    """Create a CI status event."""
    return Event(
        source=EventSource.CI,
        event_type="status",
        data={
            "status": status,  # "passing", "failing", "pending"
            "pipeline_name": pipeline_name,
            "url": url,
        },
    )


def session_start_event(
    session_id: str = "",
    context: str = "",
) -> Event:
    """Create a session start event."""
    return Event(
        source=EventSource.SESSION,
        event_type="start",
        data={
            "session_id": session_id,
            "context": context,
        },
    )


def health_tick_event() -> Event:
    """Create a health check tick event."""
    return Event(
        source=EventSource.HEALTH,
        event_type="tick",
        data={},
    )


def crystallization_ready_event(
    session_id: str,
    thought_count: int,
) -> Event:
    """Create a crystallization ready event."""
    return Event(
        source=EventSource.CRYSTAL,
        event_type="ready",
        data={
            "session_id": session_id,
            "thought_count": thought_count,
        },
    )


# =============================================================================
# Reaction
# =============================================================================


class ReactionStatus(Enum):
    """Status of a reaction."""

    PENDING = auto()  # Waiting for trust approval
    APPROVED = auto()  # Trust approved, ready to run
    RUNNING = auto()  # Currently executing
    COMPLETED = auto()  # Finished successfully
    FAILED = auto()  # Execution failed
    REJECTED = auto()  # Trust rejected
    EXPIRED = auto()  # Pending reaction expired


@dataclass
class Reaction:
    """
    A pending or completed reaction to an event.

    Captures:
    - The triggering event
    - The workflow to run
    - Trust requirements and approval status
    - Execution result
    """

    reaction_id: str = field(default_factory=lambda: f"rxn-{uuid4().hex[:12]}")
    event: Event = field(default_factory=Event)
    workflow: WorkflowTemplate | None = None
    workflow_name: str = ""

    # Trust gating
    required_trust: TrustLevel = TrustLevel.READ_ONLY
    current_trust: TrustLevel = TrustLevel.READ_ONLY
    status: ReactionStatus = ReactionStatus.PENDING

    # Timing
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime | None = None  # For pending reactions

    # Result
    result: Any = None
    error: str | None = None

    @property
    def is_approved(self) -> bool:
        """Check if reaction has trust approval."""
        return self.current_trust.value >= self.required_trust.value

    @property
    def can_run(self) -> bool:
        """Check if reaction can run now."""
        return (
            self.is_approved
            and self.status in (ReactionStatus.PENDING, ReactionStatus.APPROVED)
            and not self.is_expired
        )

    @property
    def is_expired(self) -> bool:
        """Check if pending reaction has expired."""
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def approve(self, trust_level: TrustLevel) -> bool:
        """
        Approve reaction with given trust level.

        Returns True if approval succeeded.
        """
        if self.status != ReactionStatus.PENDING:
            return False

        self.current_trust = trust_level
        if self.is_approved:
            self.status = ReactionStatus.APPROVED
            return True

        return False

    def reject(self, reason: str = "") -> None:
        """Reject the reaction."""
        self.status = ReactionStatus.REJECTED
        self.error = reason or "Rejected by user"
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "reaction_id": self.reaction_id,
            "event_id": self.event.event_id,
            "event_type": self.event.event_type,
            "event_source": self.event.source.name,
            "workflow_name": self.workflow_name,
            "required_trust": self.required_trust.name,
            "current_trust": self.current_trust.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


# =============================================================================
# Event-Workflow Mapping
# =============================================================================


@dataclass(frozen=True)
class EventMapping:
    """
    Maps an event pattern to a workflow.

    The pattern is a tuple of (source, event_type).
    If event_type is "*", matches all events from that source.
    """

    source: EventSource
    event_type: str  # "*" means all events from source
    workflow: WorkflowTemplate
    required_trust: TrustLevel
    delay: timedelta = timedelta(seconds=0)  # Optional delay before execution
    debounce: timedelta = timedelta(seconds=0)  # Debounce window
    enabled: bool = True

    def matches(self, event: Event) -> bool:
        """Check if this mapping matches an event."""
        if not self.enabled:
            return False
        if event.source != self.source:
            return False
        if self.event_type != "*" and event.event_type != self.event_type:
            return False
        return True


# Default event-workflow mappings
DEFAULT_MAPPINGS: tuple[EventMapping, ...] = (
    # Git commit → Analyze changes and capture
    EventMapping(
        source=EventSource.GIT,
        event_type="commit",
        workflow=CODE_CHANGE_RESPONSE,
        required_trust=TrustLevel.BOUNDED,
        delay=timedelta(seconds=5),  # Small delay to batch rapid commits
        debounce=timedelta(seconds=10),
    ),
    # Test failure → Analyze and attempt fix
    EventMapping(
        source=EventSource.TEST,
        event_type="failure",
        workflow=TEST_FAILURE_RESPONSE,
        required_trust=TrustLevel.AUTONOMOUS,
    ),
    # PR opened → Review workflow
    EventMapping(
        source=EventSource.PR,
        event_type="opened",
        workflow=PR_REVIEW_WORKFLOW,
        required_trust=TrustLevel.BOUNDED,
        delay=timedelta(seconds=30),  # Allow PR to stabilize
    ),
    # CI failure → Monitor and alert
    EventMapping(
        source=EventSource.CI,
        event_type="status",
        workflow=CI_MONITOR,
        required_trust=TrustLevel.READ_ONLY,
    ),
    # Session start → Morning standup
    EventMapping(
        source=EventSource.SESSION,
        event_type="start",
        workflow=MORNING_STANDUP,
        required_trust=TrustLevel.READ_ONLY,
    ),
    # Health tick → Health check
    EventMapping(
        source=EventSource.HEALTH,
        event_type="tick",
        workflow=HEALTH_CHECK,
        required_trust=TrustLevel.READ_ONLY,
    ),
    # Crystallization ready → Crystallize
    EventMapping(
        source=EventSource.CRYSTAL,
        event_type="ready",
        workflow=CRYSTALLIZATION,
        required_trust=TrustLevel.BOUNDED,
    ),
)


# =============================================================================
# Reactor
# =============================================================================


class EventHandler(Protocol):
    """Protocol for event handlers."""

    async def __call__(self, event: Event) -> None:
        """Handle an event."""
        ...


@dataclass
class WitnessReactor:
    """
    The Witness's event-to-workflow reactor.

    Maps events to workflows and manages reaction execution.

    Features:
    - Event subscription by source
    - Pattern-based event matching
    - Trust-gated execution
    - Debouncing for rapid events
    - Delayed reactions

    Pattern: "Event-Driven Architecture" (data-bus-integration.md)

    Example:
        reactor = WitnessReactor(invoker, scheduler, observer)

        # React to git commit
        await reactor.react(git_commit_event("abc123", "Fix bug"))

        # Check pending reactions
        pending = reactor.pending_reactions

        # Approve a pending reaction
        reactor.approve("rxn-abc123", TrustLevel.AUTONOMOUS)
    """

    invoker: "JewelInvoker | None" = None
    scheduler: "WitnessScheduler | None" = None
    observer: "Observer | None" = None

    # Mappings
    mappings: list[EventMapping] = field(default_factory=lambda: list(DEFAULT_MAPPINGS))

    # State
    _reactions: dict[str, Reaction] = field(default_factory=dict)
    _debounce_timers: dict[str, datetime] = field(default_factory=dict)
    _handlers: dict[EventSource, list[EventHandler]] = field(default_factory=dict)
    _running: bool = False
    _reaction_count: int = 0

    # Configuration
    pending_expiry: timedelta = timedelta(hours=24)  # How long pending reactions last
    max_pending: int = 100  # Maximum pending reactions

    async def react(self, event: Event) -> Reaction | None:
        """
        React to an event.

        Finds matching mappings and creates reactions.
        Returns the reaction if one was created, None otherwise.
        """
        # Find matching mapping
        mapping = self._find_mapping(event)
        if mapping is None:
            logger.debug(f"No mapping for event {event.event_type} from {event.source.name}")
            return None

        # Check debounce
        debounce_key = f"{mapping.source.name}:{mapping.event_type}"
        if self._is_debounced(debounce_key, mapping.debounce):
            logger.debug(f"Event {event.event_type} debounced")
            return None

        # Update debounce timer
        self._debounce_timers[debounce_key] = datetime.now(UTC)

        # Create reaction
        reaction = Reaction(
            event=event,
            workflow=mapping.workflow,
            workflow_name=mapping.workflow.name,
            required_trust=mapping.required_trust,
            expires_at=datetime.now(UTC) + self.pending_expiry,
        )

        # Store reaction
        self._reactions[reaction.reaction_id] = reaction
        self._reaction_count += 1

        # Check if we can run immediately
        if mapping.delay.total_seconds() > 0:
            # Schedule delayed execution
            if self.scheduler:
                self.scheduler.schedule_pipeline(
                    mapping.workflow.pipeline,
                    delay=mapping.delay,
                    name=f"Reaction: {reaction.workflow_name}",
                    initial_kwargs=event.data,
                )
            reaction.status = ReactionStatus.APPROVED
        elif reaction.can_run:
            # Run immediately
            await self._execute_reaction(reaction, event.data)

        logger.info(
            f"Reaction {reaction.reaction_id}: {event.event_type} → {reaction.workflow_name} "
            f"(status={reaction.status.name})"
        )

        return reaction

    def _find_mapping(self, event: Event) -> EventMapping | None:
        """Find the first matching mapping for an event."""
        for mapping in self.mappings:
            if mapping.matches(event):
                return mapping
        return None

    def _is_debounced(self, key: str, window: timedelta) -> bool:
        """Check if an event is within debounce window."""
        if window.total_seconds() == 0:
            return False

        last_time = self._debounce_timers.get(key)
        if last_time is None:
            return False

        return (datetime.now(UTC) - last_time) < window

    async def _execute_reaction(
        self,
        reaction: Reaction,
        initial_kwargs: dict[str, Any] | None = None,
    ) -> None:
        """Execute a reaction's workflow."""
        if self.invoker is None or self.observer is None:
            reaction.status = ReactionStatus.FAILED
            reaction.error = "Invoker or observer not configured"
            return

        if reaction.workflow is None:
            reaction.status = ReactionStatus.FAILED
            reaction.error = "No workflow associated"
            return

        from .pipeline import PipelineRunner

        reaction.status = ReactionStatus.RUNNING
        reaction.started_at = datetime.now(UTC)

        try:
            runner = PipelineRunner(
                invoker=self.invoker,
                observer=self.observer,
            )
            result = await runner.run(reaction.workflow.pipeline, initial_kwargs)

            reaction.result = result.to_dict()
            if result.success:
                reaction.status = ReactionStatus.COMPLETED
            else:
                reaction.status = ReactionStatus.FAILED
                reaction.error = result.error

        except Exception as e:
            reaction.status = ReactionStatus.FAILED
            reaction.error = str(e)
            logger.error(f"Reaction {reaction.reaction_id} failed: {e}")

        finally:
            reaction.completed_at = datetime.now(UTC)

    def approve(self, reaction_id: str, trust_level: TrustLevel) -> bool:
        """
        Approve a pending reaction with given trust level.

        Returns True if approval succeeded and reaction is queued.
        """
        reaction = self._reactions.get(reaction_id)
        if reaction is None:
            return False

        if reaction.approve(trust_level):
            # Queue for execution
            asyncio.create_task(self._execute_reaction(reaction, reaction.event.data))
            return True

        return False

    def reject(self, reaction_id: str, reason: str = "") -> bool:
        """Reject a pending reaction."""
        reaction = self._reactions.get(reaction_id)
        if reaction is None:
            return False

        reaction.reject(reason)
        return True

    def add_mapping(self, mapping: EventMapping) -> None:
        """Add a custom event-workflow mapping."""
        self.mappings.append(mapping)

    def remove_mapping(
        self,
        source: EventSource,
        event_type: str,
    ) -> bool:
        """Remove a mapping by source and event type."""
        for i, m in enumerate(self.mappings):
            if m.source == source and m.event_type == event_type:
                self.mappings.pop(i)
                return True
        return False

    def subscribe(self, source: EventSource, handler: EventHandler) -> None:
        """Subscribe a handler to an event source."""
        if source not in self._handlers:
            self._handlers[source] = []
        self._handlers[source].append(handler)

    def unsubscribe(self, source: EventSource, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event source."""
        if source in self._handlers:
            try:
                self._handlers[source].remove(handler)
            except ValueError:
                pass

    @property
    def pending_reactions(self) -> list[Reaction]:
        """Get all pending reactions."""
        return [
            r
            for r in self._reactions.values()
            if r.status == ReactionStatus.PENDING and not r.is_expired
        ]

    @property
    def active_reactions(self) -> list[Reaction]:
        """Get all active (pending or running) reactions."""
        return [
            r
            for r in self._reactions.values()
            if r.status in (ReactionStatus.PENDING, ReactionStatus.RUNNING, ReactionStatus.APPROVED)
            and not r.is_expired
        ]

    def get_reaction(self, reaction_id: str) -> Reaction | None:
        """Get a reaction by ID."""
        return self._reactions.get(reaction_id)

    def get_stats(self) -> dict[str, Any]:
        """Get reactor statistics."""
        by_status: dict[str, int] = {}
        for reaction in self._reactions.values():
            status = reaction.status.name
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_reactions": self._reaction_count,
            "stored_reactions": len(self._reactions),
            "pending": len(self.pending_reactions),
            "active": len(self.active_reactions),
            "by_status": by_status,
            "mappings_count": len(self.mappings),
            "active_subscriptions": list(self._handlers.keys()),
        }

    def cleanup_expired(self) -> int:
        """Remove expired pending reactions. Returns count removed."""
        expired = [
            r.reaction_id
            for r in self._reactions.values()
            if r.is_expired and r.status == ReactionStatus.PENDING
        ]

        for reaction_id in expired:
            reaction = self._reactions.pop(reaction_id, None)
            if reaction:
                reaction.status = ReactionStatus.EXPIRED

        return len(expired)


# =============================================================================
# Factory Functions
# =============================================================================


def create_reactor(
    invoker: "JewelInvoker | None" = None,
    scheduler: "WitnessScheduler | None" = None,
    observer: "Observer | None" = None,
) -> WitnessReactor:
    """
    Create a WitnessReactor instance.

    Args:
        invoker: JewelInvoker for executing workflows
        scheduler: WitnessScheduler for delayed reactions
        observer: Observer context for executions

    Returns:
        Configured WitnessReactor
    """
    return WitnessReactor(
        invoker=invoker,
        scheduler=scheduler,
        observer=observer,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Event types
    "Event",
    "EventSource",
    # Event constructors
    "git_commit_event",
    "create_test_failure_event",
    "pr_opened_event",
    "ci_status_event",
    "session_start_event",
    "health_tick_event",
    "crystallization_ready_event",
    # Reaction types
    "Reaction",
    "ReactionStatus",
    # Mapping
    "EventMapping",
    "DEFAULT_MAPPINGS",
    # Reactor
    "WitnessReactor",
    "EventHandler",
    "create_reactor",
]
