"""
zen-agents Type Definitions

Core types for session management agents.
Maps zenportal concepts to kgents primitives.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# =============================================================================
# SESSION TYPES
# =============================================================================

class SessionState(Enum):
    """State machine for session lifecycle"""
    CREATING = "creating"     # Being spawned
    RUNNING = "running"       # Active and responsive
    PAUSED = "paused"         # Detached but alive
    COMPLETED = "completed"   # Finished successfully
    FAILED = "failed"         # Crashed or errored
    UNKNOWN = "unknown"       # State indeterminate


class SessionType(Enum):
    """Types of sessions (maps to zenportal session kinds)"""
    CLAUDE = "claude"         # Claude Code CLI
    CODEX = "codex"           # OpenAI Codex
    GEMINI = "gemini"         # Google Gemini
    SHELL = "shell"           # Plain shell
    CUSTOM = "custom"         # User-defined


@dataclass
class SessionConfig:
    """
    Configuration for a session.

    Maps to zenportal's 3-tier config (config > portal > session).
    In kgents terms: this is what Ground produces for a specific session.
    """
    name: str
    session_type: SessionType
    working_dir: str | None = None
    command: str | None = None
    env: dict[str, str] = field(default_factory=dict)

    # Session-type specific
    model: str | None = None              # For AI sessions
    system_prompt: str | None = None      # For AI sessions
    max_tokens: int | None = None         # For AI sessions

    # Metadata
    tags: list[str] = field(default_factory=list)
    priority: int = 0


@dataclass
class TmuxSession:
    """
    Low-level tmux session representation.

    The empirical facts about a tmux window/pane.
    """
    id: str
    name: str
    pane_id: str
    created_at: datetime
    is_attached: bool = False


@dataclass
class Session:
    """
    High-level session abstraction.

    Combines config (intent) with tmux (reality).
    This is the morphism input/output type for session agents.
    """
    id: str
    config: SessionConfig
    state: SessionState
    tmux: TmuxSession | None = None

    # Runtime state
    output_lines: list[str] = field(default_factory=list)
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def is_alive(self) -> bool:
        return self.state in {SessionState.CREATING, SessionState.RUNNING, SessionState.PAUSED}


# =============================================================================
# GROUND STATE (Session-Specific)
# =============================================================================

@dataclass
class ConfigLayer:
    """One layer in the config cascade"""
    name: str  # "global", "portal", "session"
    values: dict[str, Any]


@dataclass
class ZenGroundState:
    """
    Ground state for zen-agents.

    Extends kgents Ground with session-specific state.

    Structure:
        - config_cascade: The 3-tier config hierarchy
        - sessions: Known sessions and their states
        - tmux: Raw tmux facts (windows, panes)
        - preferences: User preferences for zen behavior
    """
    # Config cascade (global > portal > session)
    config_cascade: list[ConfigLayer]

    # Session state
    sessions: dict[str, Session]  # id -> Session

    # tmux facts
    tmux_sessions: list[TmuxSession]

    # Preferences (inherited from K-gent ground)
    default_session_type: SessionType = SessionType.CLAUDE
    auto_discovery: bool = True
    max_sessions: int = 10

    # Timestamps
    last_discovery: datetime | None = None
    last_updated: datetime = field(default_factory=datetime.now)


# =============================================================================
# VERDICT EXTENSIONS (for ZenJudge)
# =============================================================================

@dataclass
class SessionVerdict:
    """Verdict specifically for session validation"""
    valid: bool
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    @classmethod
    def accept(cls) -> 'SessionVerdict':
        return cls(valid=True)

    @classmethod
    def reject(cls, *issues: str) -> 'SessionVerdict':
        return cls(valid=False, issues=list(issues))
