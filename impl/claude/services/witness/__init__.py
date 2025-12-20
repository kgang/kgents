"""
Witness Crown Jewel: The 8th Jewel That Watches, Learns, and Acts.

The Witness is the only Crown Jewel that can invoke all others. It graduates
from "invisible infrastructure" to a trust-gated agent that earns the right
to act autonomously on Kent's behalf.

Philosophy:
    "The ghost is not a haunting—it's a witnessing that becomes a doing."

The name "Witness" implies:
- Observer that can testify (trust-gated action)
- Presence matters (not just background noise)
- Philosophical alignment with Observer-dependent ontology

AGENTESE Paths (via @node("self.witness")):
- self.witness.manifest   - Witness health, trust level, watcher status
- self.witness.thoughts   - Recent thought stream (reads like a diary)
- self.witness.tensions   - Active tension points requiring attention
- self.witness.trust      - Trust level details, escalation history
- self.witness.start      - Start event-driven watching
- self.witness.stop       - Stop watching
- self.witness.invoke     - Cross-jewel invocation (L3 only)

Trust Escalation (Earned, Never Granted):
- L0: READ_ONLY - Observe and project, no modifications
- L1: BOUNDED - Write to .kgents/ directory only
- L2: SUGGESTION - Propose changes, require human confirmation
- L3: AUTONOMOUS - Full Kent-equivalent developer agency

Event Sources (Watchers):
- GitWatcherFlux - React to commits, pushes, branch changes
- FileSystemWatcherFlux - React to file changes (inotify/FSEvents)
- TestWatcherFlux - React to pytest results
- AgenteseWatcherFlux - React to cross-jewel events
- CIWatcherFlux - React to GitHub Actions events

See: docs/skills/metaphysical-fullstack.md
See: plans/kgentsd-crown-jewel.md
"""

from .audit import (
    AuditEntry,
    AuditingInvoker,
    AuditingPipelineRunner,
    create_auditing_invoker,
    create_auditing_runner,
)

# Re-import contracts for continued compatibility
from .contracts import (
    ActionRecordRequest,
    ActionRecordResponse,
    CaptureThoughtRequest,
    CaptureThoughtResponse,
    EscalateRequest,
    EscalateResponse,
    InvokeRequest,
    InvokeResponse,
    PipelineRequest,
    PipelineResponse,
    PipelineStepItem,
    PipelineStepResultItem,
    RollbackWindowRequest,
    RollbackWindowResponse,
    ThoughtsRequest,
    ThoughtsResponse,
    TrustRequest,
    TrustResponse,
    WitnessManifestResponse,
)
from .crystal import (
    ExperienceCrystal,
    MoodVector,
    Narrative,
    TopologySnapshot,
)
from .crystallization_node import (
    TimeWitnessManifestRendering,
    TimeWitnessManifestResponse,
    TimeWitnessNode,
)
from .invoke import (
    InvocationResult,
    JewelInvoker,
    create_invoker,
    is_mutation_path,
    is_read_only_path,
)
from .node import (
    ThoughtStreamRendering,
    WitnessManifestRendering,
    WitnessNode,
)
from .operad import (
    WITNESS_OPERAD,
    compose_autonomous_workflow,
    compose_observe_workflow,
    compose_suggest_workflow,
    create_witness_operad,
)
from .persistence import (
    ActionResultPersisted,
    EscalationResult,
    ThoughtResult,
    TrustResult,
    WitnessPersistence,
    WitnessStatus,
)
from .pipeline import (
    Branch,
    Pipeline,
    PipelineResult,
    PipelineRunner,
    PipelineStatus,
    Step,
    StepResult,
    branch,
    step,
)
from .polynomial import (
    WITNESS_POLYNOMIAL,
    AgenteseEvent,
    CIEvent,
    EscalateCommand,
    FileEvent,
    # Events
    GitEvent,
    # Commands
    StartCommand,
    StopCommand,
    TestEvent,
    # Outputs
    Thought,
    TrustLevel,
    WitnessInputFactory,
    WitnessOutput,
    WitnessPhase,
    WitnessPolynomial,
    WitnessState,
)
from .reactor import (
    DEFAULT_MAPPINGS,
    Event,
    EventMapping,
    EventSource as ReactorEventSource,  # Alias to avoid conflict with sheaf.EventSource
    Reaction,
    ReactionStatus,
    WitnessReactor,
    ci_status_event,
    create_reactor,
    create_test_failure_event,
    crystallization_ready_event,
    git_commit_event,
    health_tick_event,
    pr_opened_event,
    session_start_event,
)
from .schedule import (
    ScheduledTask,
    ScheduleStatus,
    ScheduleType,
    WitnessScheduler,
    create_scheduler,
    delay,
    every,
)
from .sheaf import (
    SOURCE_CAPABILITIES,
    EventSource,
    GluingError,
    LocalObservation,
    WitnessSheaf,
    source_overlap,
    verify_associativity_law,
    verify_identity_law,
)
from .trust import (
    ActionGate,
    BoundaryChecker,
    BoundaryViolation,
    ConfirmationManager,
    ConfirmationResult,
    EscalationCheckResult,
    EscalationCriteria,
    GateDecision,
    GateResult,
    Level1Criteria,
    Level2Criteria,
    Level3Criteria,
    ObservationStats,
    OperationStats,
    PendingSuggestion,
    SuggestionStats,
    check_escalation,
)
from .watchers import (
    GitWatcher,
    WatcherState,
    WatcherStats,
    create_git_watcher,
)
from .workflows import (
    CI_MONITOR,
    CODE_CHANGE_RESPONSE,
    CRYSTALLIZATION,
    HEALTH_CHECK,
    MORNING_STANDUP,
    PR_REVIEW_WORKFLOW,
    TEST_FAILURE_RESPONSE,
    WORKFLOW_REGISTRY,
    WorkflowCategory,
    WorkflowTemplate,
    chain_workflows,
    extend_workflow,
    get_workflow,
    list_workflows,
    search_workflows,
)

__all__ = [
    # State machine
    "TrustLevel",
    "WitnessPhase",
    "WitnessState",
    "WitnessPolynomial",
    "WITNESS_POLYNOMIAL",
    # Operad
    "WITNESS_OPERAD",
    "create_witness_operad",
    "compose_observe_workflow",
    "compose_suggest_workflow",
    "compose_autonomous_workflow",
    # Watchers
    "GitWatcher",
    "WatcherState",
    "WatcherStats",
    "create_git_watcher",
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
    # Outputs
    "Thought",
    "WitnessOutput",
    "WitnessInputFactory",
    # Persistence
    "WitnessPersistence",
    "ThoughtResult",
    "TrustResult",
    "EscalationResult",
    "ActionResultPersisted",
    "WitnessStatus",
    # Node
    "WitnessNode",
    "WitnessManifestRendering",
    "ThoughtStreamRendering",
    # Contracts
    "WitnessManifestResponse",
    "ThoughtsRequest",
    "ThoughtsResponse",
    "TrustRequest",
    "TrustResponse",
    "CaptureThoughtRequest",
    "CaptureThoughtResponse",
    "ActionRecordRequest",
    "ActionRecordResponse",
    "RollbackWindowRequest",
    "RollbackWindowResponse",
    "EscalateRequest",
    "EscalateResponse",
    # Cross-jewel contracts
    "InvokeRequest",
    "InvokeResponse",
    "PipelineRequest",
    "PipelineResponse",
    "PipelineStepItem",
    "PipelineStepResultItem",
    # Cross-jewel invocation
    "InvocationResult",
    "JewelInvoker",
    "create_invoker",
    "is_mutation_path",
    "is_read_only_path",
    # Cross-jewel pipeline
    "Step",
    "Branch",
    "Pipeline",
    "PipelineStatus",
    "StepResult",
    "PipelineResult",
    "PipelineRunner",
    "step",
    "branch",
    # Trust system
    "ActionGate",
    "GateDecision",
    "GateResult",
    "EscalationCriteria",
    "EscalationCheckResult",
    "Level1Criteria",
    "Level2Criteria",
    "Level3Criteria",
    "ObservationStats",
    "OperationStats",
    "SuggestionStats",
    "check_escalation",
    "BoundaryChecker",
    "BoundaryViolation",
    "ConfirmationManager",
    "PendingSuggestion",
    "ConfirmationResult",
    # Experience Crystallization (new - time.witness)
    "ExperienceCrystal",
    "MoodVector",
    "TopologySnapshot",
    "Narrative",
    # Witness Sheaf (crystallization gluing)
    "EventSource",
    "SOURCE_CAPABILITIES",
    "source_overlap",
    "LocalObservation",
    "GluingError",
    "WitnessSheaf",
    "verify_identity_law",
    "verify_associativity_law",
    # Scheduler (temporal composition)
    "ScheduledTask",
    "ScheduleStatus",
    "ScheduleType",
    "WitnessScheduler",
    "create_scheduler",
    "delay",
    "every",
    # Audit trail (action history)
    "AuditEntry",
    "AuditingInvoker",
    "AuditingPipelineRunner",
    "create_auditing_invoker",
    "create_auditing_runner",
    # Time Witness (crystallization node)
    "TimeWitnessNode",
    "TimeWitnessManifestResponse",
    "TimeWitnessManifestRendering",
    # Workflow templates
    "WorkflowTemplate",
    "WorkflowCategory",
    "TEST_FAILURE_RESPONSE",
    "CODE_CHANGE_RESPONSE",
    "PR_REVIEW_WORKFLOW",
    "MORNING_STANDUP",
    "CI_MONITOR",
    "HEALTH_CHECK",
    "CRYSTALLIZATION",
    "WORKFLOW_REGISTRY",
    "get_workflow",
    "list_workflows",
    "search_workflows",
    "extend_workflow",
    "chain_workflows",
    # Reactor (event-to-workflow mapping)
    "Event",
    "EventMapping",
    "ReactorEventSource",
    "Reaction",
    "ReactionStatus",
    "WitnessReactor",
    "DEFAULT_MAPPINGS",
    "create_reactor",
    # Reactor event constructors
    "git_commit_event",
    "create_test_failure_event",
    "pr_opened_event",
    "ci_status_event",
    "session_start_event",
    "health_tick_event",
    "crystallization_ready_event",
]
