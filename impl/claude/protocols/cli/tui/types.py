"""
TUI Dashboard Types - Core data structures for the DVR.

These types support the dashboard features:
- Session persistence (for replay)
- Event streaming (for real-time view)
- Thought stream visualization
- Artifact tracking

All events are immutable and timestamped for DVR scrubbing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# =============================================================================
# Event Types
# =============================================================================


class EventType(Enum):
    """Types of dashboard events."""

    # Session lifecycle
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    SESSION_PAUSE = "session_pause"
    SESSION_RESUME = "session_resume"

    # Agent lifecycle
    AGENT_START = "agent_start"
    AGENT_COMPLETE = "agent_complete"
    AGENT_FAIL = "agent_fail"
    AGENT_SKIP = "agent_skip"

    # Execution
    STEP_START = "step_start"
    STEP_COMPLETE = "step_complete"
    STEP_FAIL = "step_fail"

    # Thought stream
    THOUGHT = "thought"
    THOUGHT_DEBUG = "thought_debug"

    # Artifacts
    ARTIFACT_CREATE = "artifact_create"
    ARTIFACT_UPDATE = "artifact_update"

    # Snapshots (for DVR)
    SNAPSHOT = "snapshot"

    # User interactions
    USER_INPUT = "user_input"
    USER_COMMAND = "user_command"


class AgentStatus(Enum):
    """Status of an agent in the dashboard."""

    PENDING = "pending"  # Not yet started (○)
    RUNNING = "running"  # Currently executing (◐)
    COMPLETE = "complete"  # Finished successfully (●)
    FAILED = "failed"  # Failed with error (✗)
    SKIPPED = "skipped"  # Skipped due to condition (-)


class SessionState(Enum):
    """State of a dashboard session."""

    LIVE = "live"  # Real-time execution
    PAUSED = "paused"  # Paused (can resume)
    REPLAY = "replay"  # Replaying historical session
    ENDED = "ended"  # Session complete


# =============================================================================
# Core Data Structures
# =============================================================================


@dataclass(frozen=True)
class DashboardEvent:
    """
    An immutable event in the dashboard stream.

    Events are the atomic unit of the DVR - every change is
    captured as an event with a timestamp for replay.
    """

    id: str  # Unique event ID (e.g., evt_abc123)
    timestamp: datetime
    event_type: EventType
    source: str  # Agent/step that generated the event
    message: str  # Human-readable message
    data: dict[str, Any] = field(default_factory=dict)  # Structured payload
    session_id: str = ""  # Parent session

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "source": self.source,
            "message": self.message,
            "data": self.data,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DashboardEvent:
        """Create from dictionary."""
        return cls(
            id=d["id"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            event_type=EventType(d["event_type"]),
            source=d["source"],
            message=d["message"],
            data=d.get("data", {}),
            session_id=d.get("session_id", ""),
        )


@dataclass
class ThoughtEntry:
    """
    An entry in the thought stream.

    The thought stream shows agent reasoning in real-time,
    scrolling as new thoughts arrive.
    """

    timestamp: datetime
    source: str  # [parse], [judge], etc.
    content: str  # The thought content
    level: str = "info"  # info, debug, warn, error
    indent: int = 0  # Indentation level for hierarchy

    def render(self, show_timestamp: bool = True) -> str:
        """Render as display string."""
        indent = "  " * self.indent
        ts = f"[{self.timestamp.strftime('%H:%M:%S')}] " if show_timestamp else ""
        return f"{ts}{indent}[{self.source}] {self.content}"


@dataclass
class ArtifactEntry:
    """
    A tracked artifact in the session.

    Artifacts are outputs that persist - files, reports, etc.
    They appear in the artifacts panel and can be inspected.
    """

    id: str  # Unique artifact ID
    name: str  # Display name
    path: Path | None  # File path if saved
    artifact_type: str  # json, markdown, code, etc.
    created_at: datetime
    updated_at: datetime
    size_bytes: int = 0
    content_preview: str = ""  # First ~100 chars

    def render(self) -> str:
        """Render as display string."""
        size_str = self._format_size(self.size_bytes)
        return f"{self.name} ({self.artifact_type}, {size_str})"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes as human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes}B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes // 1024}KB"
        else:
            return f"{size_bytes // (1024 * 1024)}MB"


@dataclass
class AgentEntry:
    """
    An agent tracked in the session.

    Agents appear in the left panel with status indicators.
    """

    id: str  # Agent ID (e.g., step ID in flow)
    name: str  # Display name
    genus: str  # P-gent, J-gent, etc.
    status: AgentStatus = AgentStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = None

    def render(self) -> str:
        """Render as display string with status indicator."""
        symbol = {
            AgentStatus.PENDING: "○",
            AgentStatus.RUNNING: "◐",
            AgentStatus.COMPLETE: "●",
            AgentStatus.FAILED: "✗",
            AgentStatus.SKIPPED: "-",
        }.get(self.status, "?")

        status_suffix = {
            AgentStatus.PENDING: "[wait]",
            AgentStatus.RUNNING: "[run]",
            AgentStatus.COMPLETE: "[done]",
            AgentStatus.FAILED: "[fail]",
            AgentStatus.SKIPPED: "[skip]",
        }.get(self.status, "")

        return f"{symbol} {self.name} {status_suffix}"


# =============================================================================
# Session
# =============================================================================


@dataclass
class Session:
    """
    A dashboard session containing events and state.

    Sessions are persistent - they can be replayed after the fact.
    The session is the unit of DVR recording.
    """

    id: str  # Unique session ID (e.g., sess_abc123)
    name: str  # User-friendly name
    state: SessionState = SessionState.LIVE
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: datetime | None = None

    # Flow information (if running a flowfile)
    flow_name: str | None = None
    flow_path: Path | None = None

    # Collected data
    events: list[DashboardEvent] = field(default_factory=list)
    agents: dict[str, AgentEntry] = field(default_factory=dict)
    artifacts: dict[str, ArtifactEntry] = field(default_factory=dict)
    thoughts: list[ThoughtEntry] = field(default_factory=list)

    # Playback state (for replay mode)
    playback_index: int = 0
    playback_speed: float = 1.0

    # Budget tracking
    budget_level: str = "medium"
    tokens_used: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "flow_name": self.flow_name,
            "flow_path": str(self.flow_path) if self.flow_path else None,
            "budget_level": self.budget_level,
            "tokens_used": self.tokens_used,
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Session:
        """Create from dictionary."""
        session = cls(
            id=d["id"],
            name=d["name"],
            state=SessionState(d["state"]),
            started_at=datetime.fromisoformat(d["started_at"]),
            ended_at=datetime.fromisoformat(d["ended_at"])
            if d.get("ended_at")
            else None,
            flow_name=d.get("flow_name"),
            flow_path=Path(d["flow_path"]) if d.get("flow_path") else None,
            budget_level=d.get("budget_level", "medium"),
            tokens_used=d.get("tokens_used", 0),
        )
        session.events = [DashboardEvent.from_dict(e) for e in d.get("events", [])]
        return session

    def add_event(self, event: DashboardEvent) -> None:
        """Add an event to the session."""
        self.events.append(event)

    def add_thought(self, thought: ThoughtEntry) -> None:
        """Add a thought to the stream."""
        self.thoughts.append(thought)

    def get_event_at(self, index: int) -> DashboardEvent | None:
        """Get event at index for playback."""
        if 0 <= index < len(self.events):
            return self.events[index]
        return None

    @property
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        end = self.ended_at or datetime.now()
        return (end - self.started_at).total_seconds()

    @property
    def event_count(self) -> int:
        """Get total event count."""
        return len(self.events)


# =============================================================================
# Dashboard Layout Types
# =============================================================================


@dataclass
class DashboardLayout:
    """
    Configuration for dashboard panel layout.

    The dashboard has three main panels:
    - Left: Agent list with status
    - Center: Thought stream
    - Right: Artifacts

    Plus a command bar at the bottom.
    """

    show_agents: bool = True
    show_thoughts: bool = True
    show_artifacts: bool = True
    show_command_bar: bool = True

    agents_width: int = 20  # Characters
    artifacts_width: int = 18  # Characters

    # Thought stream formatting
    show_timestamps: bool = True
    max_thoughts: int = 100  # Keep last N in memory

    # Scrub bar
    show_scrub_bar: bool = True


# =============================================================================
# Playback Types
# =============================================================================


@dataclass
class PlaybackState:
    """
    State for DVR playback mode.

    When replaying a historical session, this tracks
    the current position and playback settings.
    """

    session: Session
    current_index: int = 0
    speed: float = 1.0  # Playback speed multiplier
    paused: bool = False

    @property
    def current_event(self) -> DashboardEvent | None:
        """Get current event."""
        return self.session.get_event_at(self.current_index)

    @property
    def progress(self) -> float:
        """Get playback progress (0.0 to 1.0)."""
        if self.session.event_count == 0:
            return 0.0
        return self.current_index / self.session.event_count

    def seek(self, index: int) -> None:
        """Seek to specific event index."""
        self.current_index = max(0, min(index, self.session.event_count - 1))

    def seek_relative(self, delta: int) -> None:
        """Seek relative to current position."""
        self.seek(self.current_index + delta)

    def step_forward(self) -> DashboardEvent | None:
        """Advance to next event."""
        if self.current_index < self.session.event_count - 1:
            self.current_index += 1
            return self.current_event
        return None

    def step_backward(self) -> DashboardEvent | None:
        """Go back to previous event."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.current_event
        return None
