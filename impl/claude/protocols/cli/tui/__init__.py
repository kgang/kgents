"""
TUI Dashboard - The DVR for agent execution.

CLI Phase 7: A Textual-based TUI that provides:
- Real-time agent monitoring
- Session playback and scrubbing
- Thought stream visualization
- Artifact inspection

Philosophy: "Real-time logs are good, but agents are fast.
By the time you see a mistake, it's gone. The TUI should not
just be a monitor; it should be a DVR."

From docs/cli-integration-plan.md Part 7.
"""

from .dashboard import cmd_dash
from .event_store import EventStore
from .types import (
    AgentStatus,
    ArtifactEntry,
    DashboardEvent,
    EventType,
    Session,
    SessionState,
    ThoughtEntry,
)

__all__ = [
    "DashboardEvent",
    "EventType",
    "AgentStatus",
    "Session",
    "SessionState",
    "ThoughtEntry",
    "ArtifactEntry",
    "EventStore",
    "cmd_dash",
]
