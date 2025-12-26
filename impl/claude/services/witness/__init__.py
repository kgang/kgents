"""
Witness Crown Jewel: Primitives for Witnessing, Memory, and Trust.

The Witness service provides:
- Mark: Atomic unit of witnessed execution
- Grant: Permission contracts
- Scope: Budget and context constraints
- Playbook: Lawful workflow orchestration
- Lesson: Immutable curated knowledge

The daemon infrastructure (CLI, watchers, pipelines) has moved to services/kgentsd/.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

See: docs/skills/metaphysical-fullstack.md
See: spec/services/witness.md
"""

import os

# =============================================================================
# Feature Flags
# =============================================================================

USE_CRYSTAL_STORAGE = os.getenv("USE_CRYSTAL_STORAGE", "").lower() in ("1", "true", "yes")

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

# Crystal (Unified Memory Compression)
from .crystal import (
    ConstitutionalCrystalMeta,
    Crystal,
    CrystalId,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)

# Constitutional Evaluator (Phase 1: Witness as Constitutional Enforcement)
from .constitutional_evaluator import (
    BatchConstitutionalEvaluator,
    ConstitutionalEvaluatorProtocol,
    MarkConstitutionalEvaluator,
)
from .crystal_store import (
    CrystalNotFoundError,
    CrystalQuery,
    CrystalStore,
    CrystalStoreError,
    DuplicateCrystalError as DuplicateCrystalError,
    LevelConsistencyError,
    get_crystal_store,
    reset_crystal_store,
    set_crystal_store,
)

# Phase 3: Crystal Adapter (WitnessMark → D-gent Crystal)
from .crystal_adapter import (
    WitnessCrystalAdapter,
)

# Phase 5: Crystal Trail Visualization
from .crystal_trail import (
    CrystalGraph,
    CrystalGraphEdge,
    CrystalGraphNode,
    CrystalTrailAdapter,
    crystals_to_graph,
    format_graph_response,
    get_hierarchy_graph,
)
from .crystallization_node import (
    TimeWitnessManifestRendering,
    TimeWitnessManifestResponse,
    TimeWitnessNode,
)
from .crystallizer import (
    CrystallizationResult,
    Crystallizer,
)

# Evidence Ladder (Phase 1: Witness Assurance Protocol)
from .evidence import (
    Evidence,
    EvidenceLevel,
    compute_content_hash,
    generate_evidence_id,
)

# Phase 6: Witness Assurance Surface (Garden)
from .garden import (
    AccountabilityLens,
    ConfidencePulse,
    EvidenceLadder,
    GardenScene,
    OrphanWeed,
    PlantHealth,
    ProvenanceNode,
    PulseRate,
    SpecPath,
    SpecPlant,
    SpecStatus as GardenSpecStatus,
)
from .garden_service import (
    GardenService,
    get_garden_service,
)

# Grant (renamed from Covenant)
from .grant import (
    GateFallback,
    GateOccurrence,
    GateTriggered,
    Grant,
    GrantEnforcer,
    GrantError,
    GrantId,
    GrantNotGranted,
    GrantRevoked,
    GrantStatus,
    GrantStore,
    ReviewGate,
    generate_grant_id,
    get_grant_store,
    reset_grant_store,
)

# Phase 4: Integration & Streaming
from .integration import (
    HandoffContext,
    NowMdProposal,
    PromotionCandidate,
    apply_now_proposal,
    auto_promote_crystals,
    identify_promotion_candidates,
    prepare_handoff_context,
    promote_to_brain,
    propose_now_update,
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

# Lesson (renamed from Terrace)
from .lesson import (
    Lesson,
    LessonId,
    LessonStatus,
    LessonStore,
    generate_lesson_id,
    get_lesson_store,
    reset_lesson_store,
    set_lesson_store,
)

# Mark (renamed from TraceNode)
from .mark import (
    ConstitutionalAlignment,
    EvidenceTier,
    LinkRelation,
    Mark,
    MarkId,
    MarkLink,
    NPhase,
    PlanPath,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    WalkId,
    WitnessDomain,
    generate_mark_id,
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

# Playbook (renamed from Ritual)
from .playbook import (
    GuardEvaluation,
    GuardFailed,
    GuardResult,
    InvalidPhaseTransition,
    MissingGrant,
    MissingScope,
    Playbook,
    PlaybookError,
    PlaybookId,
    PlaybookNotActive,
    PlaybookPhase,
    PlaybookStatus,
    PlaybookStore,
    SentinelGuard,
    generate_playbook_id,
    get_playbook_store,
    reset_playbook_store,
)
from .polynomial import (
    WITNESS_POLYNOMIAL,
    ActionResult,
    AgenteseEvent,
    CIEvent,
    EscalateCommand,
    FileEvent,
    GitEvent,
    StartCommand,
    StopCommand,
    TestEvent,
    Thought,
    TrustLevel,
    WitnessInputFactory,
    WitnessOutput,
    WitnessPhase,
    WitnessPolynomial,
    WitnessState,
)

# Portal Marks (Phase 2: Witness Mark Integration)
from .portal_marks import (
    mark_portal_collapse,
    mark_portal_expansion,
    mark_trail_save,
)

# Scope (renamed from Offering)
from .scope import (
    Budget,
    BudgetExceeded,
    HandleNotInScope,
    Scope,
    ScopeError,
    ScopeExpired,
    ScopeId,
    ScopeStatus,
    ScopeStore,
    generate_scope_id,
    get_scope_store,
    reset_scope_store,
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
from .status import (
    ContextGraphProtocol,
    SpecStatus,
    WitnessedCriteria,
    compute_status,
    compute_status_from_evidence_only,
)
from .stream import (
    CrystalEvent,
    CrystalEventType,
    create_crystal_sse_response,
    crystal_stream,
    publish_crystal_created,
    stream_crystals_cli,
)

# Trace (Immutable Mark Sequence)
from .trace import (
    Trace,
)

# MarkStore (renamed from TraceStore)
from .trace_store import (
    CausalityViolation,
    DuplicateMarkError,
    MarkNotFoundError,
    MarkQuery,
    MarkStore,
    MarkStoreError,
    get_mark_store,
    reset_mark_store,
    set_mark_store,
)

# Trail Bridge (Context Perception integration)
from .trail_bridge import (
    EvidenceTier as TrailEvidenceTier,
    TrailEvidence,
    TrailMark,
    analyze_trail,
    convert_trail_to_mark,
    emit_trail_as_mark,
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

# Constitutional Trust (Phase 1: Witness as Constitutional Enforcement)
from .trust.constitutional_trust import (
    ConstitutionalTrustComputer,
    ConstitutionalTrustResult,
    TrustComputerProtocol,
)
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

# Explicit exports for mypy
__all__ = [
    # Contracts
    "ActionRecordRequest",
    "ActionRecordResponse",
    "CaptureThoughtRequest",
    "CaptureThoughtResponse",
    "EscalateRequest",
    "EscalateResponse",
    "InvokeRequest",
    "InvokeResponse",
    "PipelineRequest",
    "PipelineResponse",
    "PipelineStepItem",
    "PipelineStepResultItem",
    "RollbackWindowRequest",
    "RollbackWindowResponse",
    "ThoughtsRequest",
    "ThoughtsResponse",
    "TrustRequest",
    "TrustResponse",
    "WitnessManifestResponse",
    # Crystal (Unified Memory Compression)
    "ConstitutionalCrystalMeta",
    "Crystal",
    "CrystalId",
    "CrystalLevel",
    "MoodVector",
    "generate_crystal_id",
    # Constitutional Evaluator (Phase 1)
    "BatchConstitutionalEvaluator",
    "ConstitutionalEvaluatorProtocol",
    "MarkConstitutionalEvaluator",
    # Crystal Store
    "CrystalNotFoundError",
    "CrystalQuery",
    "CrystalStore",
    "CrystalStoreError",
    "DuplicateCrystalError",
    "LevelConsistencyError",
    "get_crystal_store",
    "reset_crystal_store",
    "set_crystal_store",
    # Crystal Adapter (Phase 3: WitnessMark → D-gent Crystal)
    "WitnessCrystalAdapter",
    # Crystallizer
    "CrystallizationResult",
    "Crystallizer",
    # Crystallization Node
    "TimeWitnessManifestRendering",
    "TimeWitnessManifestResponse",
    "TimeWitnessNode",
    # Grant (renamed from Covenant)
    "GateFallback",
    "GateOccurrence",
    "GateTriggered",
    "Grant",
    "GrantEnforcer",
    "GrantError",
    "GrantId",
    "GrantNotGranted",
    "GrantRevoked",
    "GrantStatus",
    "GrantStore",
    "ReviewGate",
    "generate_grant_id",
    "get_grant_store",
    "reset_grant_store",
    # Intent
    "CyclicDependencyError",
    "Intent",
    "IntentId",
    "IntentStatus",
    "IntentTree",
    "IntentType",
    "generate_intent_id",
    "get_intent_tree",
    "reset_intent_tree",
    # Lesson (renamed from Terrace)
    "Lesson",
    "LessonId",
    "LessonStatus",
    "LessonStore",
    "generate_lesson_id",
    "get_lesson_store",
    "reset_lesson_store",
    "set_lesson_store",
    # Mark (renamed from TraceNode)
    "ConstitutionalAlignment",
    "EvidenceTier",
    "LinkRelation",
    "Mark",
    "MarkId",
    "MarkLink",
    "NPhase",
    "PlanPath",
    "Proof",
    "Response",
    "Stimulus",
    "UmweltSnapshot",
    "WalkId",
    "WitnessDomain",
    "generate_mark_id",
    # Node
    "ThoughtStreamRendering",
    "WitnessManifestRendering",
    "WitnessNode",
    # Operad
    "WITNESS_OPERAD",
    "compose_autonomous_workflow",
    "compose_observe_workflow",
    "compose_suggest_workflow",
    "create_witness_operad",
    # Persistence
    "ActionResultPersisted",
    "EscalationResult",
    "ThoughtResult",
    "TrustResult",
    "WitnessPersistence",
    "WitnessStatus",
    # Playbook (renamed from Ritual)
    "GuardEvaluation",
    "GuardFailed",
    "GuardResult",
    "InvalidPhaseTransition",
    "MissingGrant",
    "MissingScope",
    "Playbook",
    "PlaybookError",
    "PlaybookId",
    "PlaybookNotActive",
    "PlaybookPhase",
    "PlaybookStatus",
    "PlaybookStore",
    "SentinelGuard",
    "generate_playbook_id",
    "get_playbook_store",
    "reset_playbook_store",
    # Polynomial
    "WITNESS_POLYNOMIAL",
    "ActionResult",
    "AgenteseEvent",
    "CIEvent",
    "EscalateCommand",
    "FileEvent",
    "GitEvent",
    "StartCommand",
    "StopCommand",
    "TestEvent",
    "Thought",
    "TrustLevel",
    "WitnessInputFactory",
    "WitnessOutput",
    "WitnessPhase",
    "WitnessPolynomial",
    "WitnessState",
    # Scope (renamed from Offering)
    "Budget",
    "BudgetExceeded",
    "HandleNotInScope",
    "Scope",
    "ScopeError",
    "ScopeExpired",
    "ScopeId",
    "ScopeStatus",
    "ScopeStore",
    "generate_scope_id",
    "get_scope_store",
    "reset_scope_store",
    # Session Walk
    "SessionWalkBinding",
    "SessionWalkBridge",
    "get_session_walk_bridge",
    "reset_session_walk_bridge",
    # Sheaf
    "SOURCE_CAPABILITIES",
    "EventSource",
    "GluingError",
    "LocalObservation",
    "WitnessSheaf",
    "source_overlap",
    "verify_associativity_law",
    "verify_identity_law",
    # Trace (Immutable Mark Sequence)
    "Trace",
    # Mark Store
    "CausalityViolation",
    "DuplicateMarkError",
    "MarkNotFoundError",
    "MarkQuery",
    "MarkStore",
    "MarkStoreError",
    "get_mark_store",
    "reset_mark_store",
    "set_mark_store",
    # Trust
    "ActionGate",
    "BoundaryChecker",
    "BoundaryViolation",
    "ConfirmationManager",
    "ConfirmationResult",
    "EscalationCheckResult",
    "EscalationCriteria",
    "GateDecision",
    "GateResult",
    "Level1Criteria",
    "Level2Criteria",
    "Level3Criteria",
    "ObservationStats",
    "OperationStats",
    "PendingSuggestion",
    "SuggestionStats",
    "check_escalation",
    # Constitutional Trust (Phase 1)
    "ConstitutionalTrustComputer",
    "ConstitutionalTrustResult",
    "TrustComputerProtocol",
    # Voice Gate
    "DENYLIST_PATTERNS",
    "HEDGE_PATTERNS",
    "VOICE_ANCHORS",
    "VoiceAction",
    "VoiceCheckResult",
    "VoiceGate",
    "VoiceRule",
    "VoiceViolation",
    "get_voice_gate",
    "reset_voice_gate",
    "set_voice_gate",
    # Walk
    "Participant",
    "Walk",
    "WalkIntent",
    "WalkStatus",
    "WalkStore",
    "get_walk_store",
    "reset_walk_store",
    # Portal Marks (Phase 2: Witness Mark Integration)
    "mark_portal_collapse",
    "mark_portal_expansion",
    "mark_trail_save",
    # Trail Bridge (Context Perception integration)
    "TrailEvidenceTier",
    "TrailEvidence",
    "TrailMark",
    "analyze_trail",
    "convert_trail_to_mark",
    "emit_trail_as_mark",
    # Evidence Ladder (Phase 1: Witness Assurance Protocol)
    "Evidence",
    "EvidenceLevel",
    "compute_content_hash",
    "generate_evidence_id",
    "ContextGraphProtocol",
    "SpecStatus",
    "WitnessedCriteria",
    "compute_status",
    "compute_status_from_evidence_only",
    # Phase 4: Integration & Streaming
    "HandoffContext",
    "NowMdProposal",
    "PromotionCandidate",
    "apply_now_proposal",
    "auto_promote_crystals",
    "identify_promotion_candidates",
    "prepare_handoff_context",
    "promote_to_brain",
    "propose_now_update",
    "CrystalEvent",
    "CrystalEventType",
    "create_crystal_sse_response",
    "crystal_stream",
    "publish_crystal_created",
    "stream_crystals_cli",
    # Phase 5: Crystal Trail Visualization
    "CrystalGraph",
    "CrystalGraphEdge",
    "CrystalGraphNode",
    "CrystalTrailAdapter",
    "crystals_to_graph",
    "format_graph_response",
    "get_hierarchy_graph",
    # Phase 6: Witness Assurance Surface (Garden)
    "AccountabilityLens",
    "ConfidencePulse",
    "EvidenceLadder",
    "GardenScene",
    "GardenService",
    "GardenSpecStatus",
    "OrphanWeed",
    "PlantHealth",
    "ProvenanceNode",
    "PulseRate",
    "SpecPath",
    "SpecPlant",
    "get_garden_service",
    # Feature Flags
    "USE_CRYSTAL_STORAGE",
]
