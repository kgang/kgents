"""
Conductor Crown Jewel: Session orchestration for CLI v7.

The Conductor manages:
- ConversationWindow: Bounded history with context strategies
- Summarizer: LLM-powered context compression
- WindowPersistence: D-gent storage for window state
- Agent Presence: Visible cursor states and activity indicators
- Session: Multi-turn collaborative sessions

Per CLI v7 Implementation Plan Phases 2 & 3.

AGENTESE: self.conductor.*
"""

from __future__ import annotations

from .persistence import (
    WindowPersistence,
    get_window_persistence,
    reset_window_persistence,
)
from .presence import (
    AgentCursor,
    CircadianPhase,
    CursorState,
    PresenceChannel,
    PresenceEventType,
    PresenceUpdate,
    get_presence_channel,
    render_presence_footer,
    reset_presence_channel,
)
from .summarizer import (
    SummarizationResult,
    Summarizer,
    create_summarizer,
)
from .window import (
    ContextMessage,
    ConversationWindow,
    WindowSnapshot,
    create_window_from_config,
)

__all__ = [
    # Window (Phase 2)
    "ConversationWindow",
    "ContextMessage",
    "WindowSnapshot",
    "create_window_from_config",
    # Summarizer (Phase 2)
    "Summarizer",
    "SummarizationResult",
    "create_summarizer",
    # Persistence (Phase 2)
    "WindowPersistence",
    "get_window_persistence",
    "reset_window_persistence",
    # Presence (Phase 3)
    "CursorState",
    "CircadianPhase",
    "AgentCursor",
    "PresenceEventType",
    "PresenceUpdate",
    "PresenceChannel",
    "get_presence_channel",
    "reset_presence_channel",
    "render_presence_footer",
]
