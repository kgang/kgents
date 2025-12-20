"""
Agent Presence: Collaborative cursor awareness for CLI v7.

Phase 3: Agent Cursors

RE-EXPORTS from services/conductor/presence.py (the Crown Jewel implementation).

The Figma-inspired insight: agents have presence. When K-gent explores self.memory,
the CLI shows "K-gent is exploring self.memory..." — a gentle reminder that we're
collaborating, not just executing commands.

Key Design Decisions:
1. CursorState: Enum Property Pattern (#2) - emoji, color, animation_speed on values
2. AgentCursor: State machine with Directed State Cycle (#9)
3. CircadianPhase: Circadian Modulation (#11) - animation varies by time of day
4. PresenceChannel: Async pub/sub with asyncio.Queue for SSE/WebSocket

The canonical implementation lives in services/conductor/presence.py.
This module re-exports for backward compatibility with existing AGENTESE nodes.

Principle Alignment:
- Tasteful: Each cursor state serves a clear purpose
- Joy-Inducing: Presence makes agents feel alive
- Composable: Works via event bus, decoupled from rendering

Voice Anchor: "Daring, bold, creative, opinionated but not gaudy"
The presence is subtle but real - one line of text, not a fireworks display.
"""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Any

# =============================================================================
# Re-export from Crown Jewel (services/conductor/presence.py)
# =============================================================================
from services.conductor.presence import (
    # Core data classes
    AgentCursor,
    CircadianPhase,
    # State enums
    CursorState,
    # Channel
    PresenceChannel,
    PresenceEventType,
    PresenceUpdate,
    get_presence_channel,
    # CLI helpers
    render_presence_footer,
    reset_presence_channel,
)

# =============================================================================
# Backward Compatibility: CursorBehavior
# =============================================================================


class CursorBehavior(Enum):
    """
    Agent behavior patterns - personality expressed through movement.

    DEPRECATED: Use CursorState properties instead.

    From the spec:
    - FOLLOWER: Follows human with slight delay
    - EXPLORER: Independent exploration
    - ASSISTANT: Follows but occasionally suggests
    - AUTONOMOUS: Does its own thing entirely
    """

    FOLLOWER = "follower"
    EXPLORER = "explorer"
    ASSISTANT = "assistant"
    AUTONOMOUS = "autonomous"


# =============================================================================
# Factory Functions
# =============================================================================


def create_kgent_cursor() -> AgentCursor:
    """
    Create the K-gent cursor (the soul agent).

    K-gent is the primary agent persona - curious, helpful, slightly playful.
    """
    return AgentCursor(
        agent_id="kgent",
        display_name="K-gent",
        state=CursorState.WAITING,
        activity="Ready",
    )


def create_explorer_cursor(name: str = "Explorer") -> AgentCursor:
    """
    Create an explorer cursor (read-only codebase search).

    Explorers move independently through the graph, never write.
    """
    return AgentCursor(
        agent_id=f"explorer-{uuid.uuid4().hex[:6]}",
        display_name=name,
        state=CursorState.EXPLORING,
        activity="Exploring...",
    )


def create_worker_cursor(name: str = "Worker") -> AgentCursor:
    """
    Create a worker cursor (file modifications).

    Workers focus on specific nodes, working methodically.
    """
    return AgentCursor(
        agent_id=f"worker-{uuid.uuid4().hex[:6]}",
        display_name=name,
        state=CursorState.WORKING,
        activity="Working...",
    )


# =============================================================================
# CLI Presence Formatter (Legacy - prefer render_presence_footer)
# =============================================================================


class CLIPresenceFormatter:
    """
    Format presence for CLI display.

    DEPRECATED: Use render_presence_footer() instead.

    This is the text-based presence for Phase 3.
    Shows a simple status line below the prompt.

    Example output:
        ┌ K-gent is exploring self.memory...
        │ Explorer is working on world.file...
    """

    def __init__(self, max_cursors: int = 3) -> None:
        """
        Args:
            max_cursors: Maximum cursors to show (avoid clutter)
        """
        self.max_cursors = max_cursors

    def format_presence_line(self, cursors: list[AgentCursor]) -> str:
        """
        Format cursors as a presence line.

        Returns empty string if no active cursors.
        """
        if not cursors:
            return ""

        # Filter to active cursors (not just waiting)
        active = [c for c in cursors if c.state != CursorState.WAITING]

        if not active:
            return ""

        # Take first N
        to_show = active[: self.max_cursors]

        # Format each using new method
        lines = [c.to_cli() for c in to_show]

        if len(active) > self.max_cursors:
            lines.append(f"  +{len(active) - self.max_cursors} more agents")

        # Use subtle box drawing
        result = "\n".join(f"  \033[90m│\033[0m {line}" for line in lines)
        return f"\033[90m┌─\033[0m Agent Presence\n{result}"

    def format_single_cursor(self, cursor: AgentCursor) -> str:
        """
        Format a single cursor for inline display.

        Example: "○ K-gent exploring self.memory"
        """
        return f"{cursor.emoji} {cursor.display_name} {cursor.state.name.lower()}"


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # State enums (from Crown Jewel)
    "CursorState",
    "CircadianPhase",
    "PresenceEventType",
    # Core data classes (from Crown Jewel)
    "AgentCursor",
    "PresenceUpdate",
    # Channel (from Crown Jewel)
    "PresenceChannel",
    "get_presence_channel",
    "reset_presence_channel",
    # CLI helpers (from Crown Jewel)
    "render_presence_footer",
    # Backward compatibility
    "CursorBehavior",
    # Factory functions
    "create_kgent_cursor",
    "create_explorer_cursor",
    "create_worker_cursor",
    # Legacy CLI formatting
    "CLIPresenceFormatter",
]
