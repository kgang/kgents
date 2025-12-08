"""
Session models for zen-agents.

Sessions have states: RUNNING, COMPLETED, PAUSED, FAILED, KILLED.

Session types:
  - Provider backends: CLAUDE, CODEX, GEMINI, SHELL, OPENROUTER
  - LLM-backed kgents: ROBIN, CREATIVITY, HYPOTHESIS, KGENT
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SessionState(Enum):
    """Possible states for a session."""
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"
    KILLED = "killed"


class SessionType(Enum):
    """Types of AI sessions.

    Provider backends (infrastructure):
        CLAUDE, CODEX, GEMINI, SHELL, OPENROUTER

    LLM-backed kgents (agent personalities):
        ROBIN - Round-robin orchestrator for multi-agent coordination
        CREATIVITY - Art/creativity coach (A-gents domain)
        HYPOTHESIS - Scientific hypothesis generator (B-gents domain)
        KGENT - Kent simulacra interactive persona (K-gent)
    """
    # Provider backends
    CLAUDE = "claude"
    CODEX = "codex"
    GEMINI = "gemini"
    SHELL = "shell"
    OPENROUTER = "openrouter"

    # LLM-backed kgents
    ROBIN = "robin"
    CREATIVITY = "creativity"
    HYPOTHESIS = "hypothesis"
    KGENT = "kgent"


def session_requires_llm(session_type: SessionType) -> bool:
    """Check if session type requires LLM runtime (kgents agents)."""
    return session_type in {
        SessionType.ROBIN,
        SessionType.CREATIVITY,
        SessionType.HYPOTHESIS,
        SessionType.KGENT,
    }


@dataclass
class NewSessionConfig:
    """Configuration for creating a new session."""
    name: str
    session_type: SessionType
    working_dir: Optional[str] = None
    command: Optional[str] = None
    env: dict[str, str] = field(default_factory=dict)

    # Type-specific config
    model: Optional[str] = None  # For OpenRouter
    api_key_env: Optional[str] = None  # Env var name for API key


@dataclass
class Session:
    """
    A managed AI assistant session.

    Each session runs in an isolated tmux pane for:
    - Process isolation
    - Persistent scrollback (50,000 lines)
    - Detachable/reattachable workflows
    """
    id: UUID
    name: str
    session_type: SessionType
    state: SessionState
    tmux_name: str  # The tmux session/window identifier

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # State tracking
    exit_code: Optional[int] = None
    error_message: Optional[str] = None

    # Config used to create this session
    working_dir: Optional[str] = None
    command: Optional[str] = None

    # Flexible metadata for LLM-backed sessions
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        config: NewSessionConfig,
        tmux_name: str,
    ) -> "Session":
        """Create a new session from config."""
        return cls(
            id=uuid4(),
            name=config.name,
            session_type=config.session_type,
            state=SessionState.RUNNING,
            tmux_name=tmux_name,
            working_dir=config.working_dir,
            command=config.command,
        )

    def with_state(self, state: SessionState) -> "Session":
        """Return a copy with updated state."""
        return Session(
            id=self.id,
            name=self.name,
            session_type=self.session_type,
            state=state,
            tmux_name=self.tmux_name,
            created_at=self.created_at,
            updated_at=datetime.now(),
            exit_code=self.exit_code,
            error_message=self.error_message,
            working_dir=self.working_dir,
            command=self.command,
            metadata=self.metadata.copy(),
        )

    def __repr__(self) -> str:
        return f"Session({self.name}, {self.session_type.value}, {self.state.value})"
