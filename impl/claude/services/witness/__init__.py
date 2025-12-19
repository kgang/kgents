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

from .contracts import (
    ActionRecordRequest,
    ActionRecordResponse,
    CaptureThoughtRequest,
    CaptureThoughtResponse,
    EscalateRequest,
    EscalateResponse,
    RollbackWindowRequest,
    RollbackWindowResponse,
    ThoughtsRequest,
    ThoughtsResponse,
    TrustRequest,
    TrustResponse,
    WitnessManifestResponse,
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
from .watchers import (
    GitWatcher,
    WatcherState,
    WatcherStats,
    create_git_watcher,
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
]
