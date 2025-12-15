"""
N-Phase Development Cycle.

The meta-meta-prompt: generates N-Phase prompts from project definitions.
Also provides native session management for runtime orchestration.

AGENTESE handle: concept.nphase.*

Usage:
    # Compiler
    from protocols.nphase import compiler
    prompt = compiler.compile_from_yaml_file("project.yaml")

    # Session management
    from protocols.nphase.session import create_session
    session = create_session("Feature Implementation")
    session.advance_phase(NPhase.ACT)

    # Phase detection
    from protocols.nphase.detector import detect_phase
    signal = detect_phase("⟿[ACT]", session.current_phase)
"""

from .compiler import NPhasePrompt, NPhasePromptCompiler, compiler
from .detector import (
    PhaseDetector,
    PhaseSignal,
    SignalAction,
    detect_phase,
    detector,
)
from .events import (
    EntropySpentEvent,
    HandleAddedEvent,
    NPhaseEvent,
    NPhaseEventType,
    PhaseCheckpointEvent,
    PhaseSignalDetectedEvent,
    PhaseTransitionEvent,
    SessionCreatedEvent,
    SessionEndedEvent,
    checkpoint_event,
    phase_transition_event,
    session_created_event,
    session_ended_event,
    signal_detected_event,
)
from .operad import (
    NPHASE_OPERAD,
    NPhase,
    NPhaseInput,
    NPhaseOutput,
    NPhaseState,
    create_nphase_operad,
    get_compressed_phase,
    get_detailed_phases,
    is_valid_transition,
    next_phase,
)
from .schema import (
    COMPRESSED_PHASES,
    PHASE_NAMES,
    Blocker,
    Checkpoint,
    Classification,
    Component,
    Decision,
    Effort,
    EntropyBudget,
    FileRef,
    Invariant,
    PhaseOverride,
    PhaseStatus,
    ProjectDefinition,
    ProjectScope,
    ValidationResult,
    Wave,
)
from .session import (
    Handle,
    NPhaseSession,
    PhaseLedgerEntry,
    SessionCheckpoint,
    SessionStore,
    create_session,
    delete_session,
    get_session,
    get_session_store,
    list_sessions,
    reset_session_store,
)
from .state import (
    CumulativeState,
    NPhaseStateUpdater,
    PhaseOutput,
    state_updater,
)
# Handle is in both session.py and state.py - disambiguate
from .state import Handle as StateHandle

__all__ = [
    # Enums
    "Classification",
    "Effort",
    "PhaseStatus",
    "NPhase",
    "SignalAction",
    "NPhaseEventType",
    # Schema types
    "ProjectScope",
    "Decision",
    "FileRef",
    "Invariant",
    "Blocker",
    "Component",
    "Wave",
    "Checkpoint",
    "EntropyBudget",
    "PhaseOverride",
    "ProjectDefinition",
    "ValidationResult",
    # Constants
    "PHASE_NAMES",
    "COMPRESSED_PHASES",
    # Compiler
    "NPhasePromptCompiler",
    "NPhasePrompt",
    "compiler",
    # State
    "NPhaseStateUpdater",
    "CumulativeState",
    "PhaseOutput",
    "StateHandle",
    "state_updater",
    # Operad
    "NPHASE_OPERAD",
    "NPhaseState",
    "NPhaseInput",
    "NPhaseOutput",
    "create_nphase_operad",
    "get_compressed_phase",
    "get_detailed_phases",
    "is_valid_transition",
    "next_phase",
    # Session (new)
    "Handle",
    "PhaseLedgerEntry",
    "SessionCheckpoint",
    "NPhaseSession",
    "SessionStore",
    "get_session_store",
    "reset_session_store",
    "create_session",
    "get_session",
    "list_sessions",
    "delete_session",
    # Detector (new)
    "PhaseSignal",
    "PhaseDetector",
    "detector",
    "detect_phase",
    # Events (new)
    "NPhaseEvent",
    "PhaseTransitionEvent",
    "PhaseCheckpointEvent",
    "PhaseSignalDetectedEvent",
    "SessionCreatedEvent",
    "SessionEndedEvent",
    "HandleAddedEvent",
    "EntropySpentEvent",
    "phase_transition_event",
    "checkpoint_event",
    "signal_detected_event",
    "session_created_event",
    "session_ended_event",
]
