"""
zen-agents: Zenportal reimagined through kgents

Agent-based architecture for terminal session management.
"""

from .types import (
    SessionState,
    SessionType,
    SessionConfig,
    Session,
    TmuxSession,
    ZenGroundState,
    SessionVerdict,
    ConfigLayer,
)

from .ground import ZenGround, zen_ground
from .judge import ZenJudge, zen_judge
from .conflicts import (
    SessionContradict,
    SessionSublate,
    SessionConflictPipeline,
    SessionConflict,
    ConflictResolution,
    ConflictPipelineResult,
    ConflictType,
    session_contradict,
    session_sublate,
    conflict_pipeline,
    detect_conflicts,
    resolve_conflicts,
)
from .persistence import (
    StateSave,
    StateLoad,
    SessionPersist,
    state_save,
    state_load,
    session_persist,
)
from .discovery import (
    DiscoveryInput,
    ReconcileInput,
    ReconcileResult,
    ClaudeSessionInfo,
    TmuxDiscovery,
    SessionReconcile,
    ClaudeSessionDiscovery,
    tmux_discovery,
    session_reconcile,
    claude_session_discovery,
)
from .commands import (
    CommandBuild,
    CommandValidate,
    CommandResult,
    ValidationResult,
    command_build,
    command_validate,
)

__all__ = [
    # Types
    'SessionState', 'SessionType', 'SessionConfig', 'Session', 'TmuxSession',
    'ZenGroundState', 'SessionVerdict', 'ConfigLayer',
    # Ground
    'ZenGround', 'zen_ground',
    # Judge
    'ZenJudge', 'zen_judge',
    # Conflicts (Contradict/Sublate)
    'SessionContradict', 'SessionSublate', 'SessionConflictPipeline',
    'SessionConflict', 'ConflictResolution', 'ConflictPipelineResult', 'ConflictType',
    'session_contradict', 'session_sublate', 'conflict_pipeline',
    'detect_conflicts', 'resolve_conflicts',
    # Persistence
    'StateSave', 'StateLoad', 'SessionPersist',
    'state_save', 'state_load', 'session_persist',
    # Discovery types
    'DiscoveryInput', 'ReconcileInput', 'ReconcileResult', 'ClaudeSessionInfo',
    # Discovery agents
    'TmuxDiscovery', 'SessionReconcile', 'ClaudeSessionDiscovery',
    # Discovery singletons
    'tmux_discovery', 'session_reconcile', 'claude_session_discovery',
    # Command factory types
    'CommandResult', 'ValidationResult',
    # Command factory agents
    'CommandBuild', 'CommandValidate',
    # Command factory singletons
    'command_build', 'command_validate',
]
