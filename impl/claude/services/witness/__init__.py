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
from .covenant import (
    Covenant,
    CovenantEnforcer,
    CovenantError,
    CovenantId,
    CovenantNotGranted,
    CovenantRevoked,
    CovenantStatus,
    CovenantStore,
    GateFallback,
    GateOccurrence,
    GateTriggered,
    ReviewGate,
    generate_covenant_id,
    get_covenant_store,
    reset_covenant_store,
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
from .intent import (
    CyclicDependencyError,
    Intent,
    IntentId,
    IntentStatus,
    IntentTree,
    IntentType,
    generate_intent_id,
    get_intent_tree,
    reset_intent_tree,
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

# WARP Phase 1 - Chunks 3-6
from .offering import (
    Budget,
    BudgetExceeded,
    HandleNotInScope,
    Offering,
    OfferingError,
    OfferingExpired,
    OfferingId,
    OfferingStatus,
    OfferingStore,
    generate_offering_id,
    get_offering_store,
    reset_offering_store,
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
from .ritual import (
    GuardEvaluation,
    GuardFailed,
    GuardResult,
    InvalidPhaseTransition,
    MissingCovenant,
    MissingOffering,
    Ritual,
    RitualError,
    RitualId,
    RitualNotActive,
    RitualPhase,
    RitualStatus,
    RitualStore,
    SentinelGuard,
    generate_ritual_id,
    get_ritual_store,
    reset_ritual_store,
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
from .session_walk import (
    SessionWalkBinding,
    SessionWalkBridge,
    get_session_walk_bridge,
    reset_session_walk_bridge,
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
from .terrace import (
    Terrace,
    TerraceId,
    TerraceStatus,
    TerraceStore,
    generate_terrace_id,
    get_terrace_store,
    reset_terrace_store,
    set_terrace_store,
)

# WARP Primitives (Phase 1)
from .trace_node import (
    LinkRelation,
    NPhase,
    PlanPath,
    Response,
    Stimulus,
    TraceLink,
    TraceNode,
    TraceNodeId,
    UmweltSnapshot,
    WalkId,
    generate_trace_id,
)
from .trace_store import (
    CausalityViolation,
    DuplicateTraceError,
    TraceNodeStore,
    TraceNotFoundError,
    TraceQuery,
    TraceStoreError,
    get_trace_store,
    reset_trace_store,
    set_trace_store,
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

# WARP Phase 1 - Chunks 7-8
from .voice_gate import (
    DENYLIST_PATTERNS,
    HEDGE_PATTERNS,
    VOICE_ANCHORS,
    VoiceAction,
    VoiceCheckResult,
    VoiceGate,
    VoiceRule,
    VoiceViolation,
    get_voice_gate,
    reset_voice_gate,
    set_voice_gate,
)
from .walk import (
    Participant,
    Walk,
    WalkIntent,
    WalkStatus,
    WalkStore,
    get_walk_store,
    reset_walk_store,
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
    # WARP Primitives (Phase 1)
    "TraceNode",
    "TraceNodeId",
    "TraceLink",
    "LinkRelation",
    "NPhase",
    "PlanPath",
    "WalkId",
    "Stimulus",
    "Response",
    "UmweltSnapshot",
    "generate_trace_id",
    # TraceNodeStore
    "TraceNodeStore",
    "TraceQuery",
    "TraceStoreError",
    "CausalityViolation",
    "DuplicateTraceError",
    "TraceNotFoundError",
    "get_trace_store",
    "set_trace_store",
    "reset_trace_store",
    # Walk
    "Walk",
    "WalkStatus",
    "WalkIntent",
    "Participant",
    "WalkStore",
    "get_walk_store",
    "reset_walk_store",
    # Session-Walk Bridge (Session 7)
    "SessionWalkBinding",
    "SessionWalkBridge",
    "get_session_walk_bridge",
    "reset_session_walk_bridge",
    # Offering (Chunk 3)
    "OfferingId",
    "generate_offering_id",
    "Budget",
    "OfferingStatus",
    "OfferingError",
    "BudgetExceeded",
    "OfferingExpired",
    "HandleNotInScope",
    "Offering",
    "OfferingStore",
    "get_offering_store",
    "reset_offering_store",
    # Covenant (Chunk 4)
    "CovenantId",
    "generate_covenant_id",
    "CovenantStatus",
    "GateFallback",
    "ReviewGate",
    "GateOccurrence",
    "CovenantError",
    "CovenantNotGranted",
    "CovenantRevoked",
    "GateTriggered",
    "Covenant",
    "CovenantEnforcer",
    "CovenantStore",
    "get_covenant_store",
    "reset_covenant_store",
    # Ritual (Chunk 5)
    "RitualId",
    "generate_ritual_id",
    "RitualStatus",
    "GuardResult",
    "SentinelGuard",
    "GuardEvaluation",
    "RitualPhase",
    "RitualError",
    "RitualNotActive",
    "InvalidPhaseTransition",
    "GuardFailed",
    "MissingCovenant",
    "MissingOffering",
    "Ritual",
    "RitualStore",
    "get_ritual_store",
    "reset_ritual_store",
    # Intent (Chunk 6)
    "IntentId",
    "generate_intent_id",
    "IntentType",
    "IntentStatus",
    "CyclicDependencyError",
    "Intent",
    "IntentTree",
    "get_intent_tree",
    "reset_intent_tree",
    # VoiceGate (Chunk 7)
    "VOICE_ANCHORS",
    "DENYLIST_PATTERNS",
    "HEDGE_PATTERNS",
    "VoiceAction",
    "VoiceRule",
    "VoiceViolation",
    "VoiceCheckResult",
    "VoiceGate",
    "get_voice_gate",
    "set_voice_gate",
    "reset_voice_gate",
    # Terrace (Chunk 8)
    "TerraceId",
    "generate_terrace_id",
    "TerraceStatus",
    "Terrace",
    "TerraceStore",
    "get_terrace_store",
    "set_terrace_store",
    "reset_terrace_store",
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
