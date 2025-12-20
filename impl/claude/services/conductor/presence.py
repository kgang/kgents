"""
Agent Presence: Visible cursor states and activity indicators.

CLI v7 Phase 3: Agent Presence

This implements Pattern #2 (Enum Property Pattern) and Pattern #9 (Directed State Cycle)
from crown-jewel-patterns.md:
- CursorState has color, emoji, animation properties
- Valid state transitions form a directed graph

The presence layer makes agents "visible" in the workspace:
- Agents have cursor states (following, exploring, working, suggesting, waiting)
- Activity descriptions show what the agent is doing
- Circadian modulation adjusts animation speed by time of day

Industry Inspiration: sshx terminal sharing, Figma multiplayer cursors

Usage:
    cursor = AgentCursor(
        agent_id="k-gent",
        display_name="K-gent",
        state=CursorState.WORKING,
        activity="Reading self.memory...",
    )

    # Broadcast to all subscribers
    await presence_channel.broadcast(cursor)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, AsyncIterator, Callable

if TYPE_CHECKING:
    from .behaviors import CursorBehavior, Position

logger = logging.getLogger(__name__)


# =============================================================================
# CursorState: Pattern #2 (Enum Property Pattern)
# =============================================================================


class CursorState(Enum):
    """
    Agent cursor state with rich properties.

    Pattern #2: Enum Property Pattern - metadata on enum values via @property.
    Pattern #9: Directed State Cycle - valid transitions form a graph.

    States represent what the agent is currently doing:
    - WAITING: Idle, ready for input
    - FOLLOWING: Tracking human cursor/focus
    - EXPLORING: Independent navigation
    - WORKING: Actively processing
    - SUGGESTING: Has a suggestion ready
    """

    WAITING = auto()
    FOLLOWING = auto()
    EXPLORING = auto()
    WORKING = auto()
    SUGGESTING = auto()

    @property
    def emoji(self) -> str:
        """Visual indicator for CLI/UI display."""
        return {
            CursorState.WAITING: "⏳",
            CursorState.FOLLOWING: "👁️",
            CursorState.EXPLORING: "🔍",
            CursorState.WORKING: "⚡",
            CursorState.SUGGESTING: "💡",
        }[self]

    @property
    def color(self) -> str:
        """CLI color for Rich/terminal output."""
        return {
            CursorState.WAITING: "dim",
            CursorState.FOLLOWING: "cyan",
            CursorState.EXPLORING: "blue",
            CursorState.WORKING: "yellow",
            CursorState.SUGGESTING: "green",
        }[self]

    @property
    def tailwind_color(self) -> str:
        """Tailwind CSS class for web UI."""
        return {
            CursorState.WAITING: "text-gray-400",
            CursorState.FOLLOWING: "text-cyan-400",
            CursorState.EXPLORING: "text-blue-400",
            CursorState.WORKING: "text-yellow-400",
            CursorState.SUGGESTING: "text-green-400",
        }[self]

    @property
    def animation_speed(self) -> float:
        """
        Animation speed multiplier (0.0-1.0).

        Higher = faster animation (more active).
        Used for cursor pulse/breathing effects.
        """
        return {
            CursorState.WAITING: 0.1,  # Slow breathing
            CursorState.FOLLOWING: 0.8,  # Quick tracking
            CursorState.EXPLORING: 1.0,  # Full speed exploration
            CursorState.WORKING: 0.5,  # Steady pulse
            CursorState.SUGGESTING: 0.3,  # Gentle attention pulse
        }[self]

    @property
    def description(self) -> str:
        """Human-readable description of state."""
        return {
            CursorState.WAITING: "Idle, ready for input",
            CursorState.FOLLOWING: "Following your cursor",
            CursorState.EXPLORING: "Exploring independently",
            CursorState.WORKING: "Processing...",
            CursorState.SUGGESTING: "Has a suggestion",
        }[self]

    @property
    def can_transition_to(self) -> frozenset["CursorState"]:
        """
        Valid state transitions (Pattern #9: Directed State Cycle).

        Not all transitions are valid:
        - WAITING → anything (wake up)
        - WORKING → SUGGESTING, WAITING (complete or pause)
        - SUGGESTING → FOLLOWING, WAITING (after suggestion)
        - etc.
        """
        return {
            CursorState.WAITING: frozenset(
                {
                    CursorState.FOLLOWING,
                    CursorState.EXPLORING,
                    CursorState.WORKING,
                }
            ),
            CursorState.FOLLOWING: frozenset(
                {
                    CursorState.EXPLORING,
                    CursorState.SUGGESTING,
                    CursorState.WAITING,
                    CursorState.WORKING,
                }
            ),
            CursorState.EXPLORING: frozenset(
                {
                    CursorState.WORKING,
                    CursorState.SUGGESTING,
                    CursorState.FOLLOWING,
                    CursorState.WAITING,
                }
            ),
            CursorState.WORKING: frozenset(
                {
                    CursorState.SUGGESTING,
                    CursorState.WAITING,
                    CursorState.FOLLOWING,
                }
            ),
            CursorState.SUGGESTING: frozenset(
                {
                    CursorState.FOLLOWING,
                    CursorState.WAITING,
                    CursorState.WORKING,
                }
            ),
        }[self]

    def can_transition(self, target: "CursorState") -> bool:
        """Check if transition to target state is valid."""
        return target in self.can_transition_to


# =============================================================================
# CircadianPhase: Pattern #11 (Circadian Modulation)
# =============================================================================


class CircadianPhase(Enum):
    """
    Time of day phases for UI modulation.

    Pattern #11: Circadian Modulation - adjust behavior by time of day.
    """

    DAWN = auto()  # 5-9
    MORNING = auto()  # 9-12
    NOON = auto()  # 12-14
    AFTERNOON = auto()  # 14-17
    DUSK = auto()  # 17-20
    EVENING = auto()  # 20-23
    NIGHT = auto()  # 23-5

    @classmethod
    def from_hour(cls, hour: int) -> "CircadianPhase":
        """Get phase from hour (0-23)."""
        if 5 <= hour < 9:
            return cls.DAWN
        elif 9 <= hour < 12:
            return cls.MORNING
        elif 12 <= hour < 14:
            return cls.NOON
        elif 14 <= hour < 17:
            return cls.AFTERNOON
        elif 17 <= hour < 20:
            return cls.DUSK
        elif 20 <= hour < 23:
            return cls.EVENING
        else:
            return cls.NIGHT

    @classmethod
    def current(cls) -> "CircadianPhase":
        """Get current phase based on local time."""
        return cls.from_hour(datetime.now().hour)

    @property
    def tempo_modifier(self) -> float:
        """
        Animation tempo modifier.

        Morning = energetic (1.0), Night = calm (0.3).
        """
        return {
            CircadianPhase.DAWN: 0.6,
            CircadianPhase.MORNING: 1.0,
            CircadianPhase.NOON: 0.9,
            CircadianPhase.AFTERNOON: 0.8,
            CircadianPhase.DUSK: 0.6,
            CircadianPhase.EVENING: 0.4,
            CircadianPhase.NIGHT: 0.3,
        }[self]

    @property
    def warmth(self) -> float:
        """
        Color warmth (0.0 = cool, 1.0 = warm).

        Dusk/dawn are warmer, noon is neutral.
        """
        return {
            CircadianPhase.DAWN: 0.8,
            CircadianPhase.MORNING: 0.4,
            CircadianPhase.NOON: 0.3,
            CircadianPhase.AFTERNOON: 0.4,
            CircadianPhase.DUSK: 0.9,
            CircadianPhase.EVENING: 0.7,
            CircadianPhase.NIGHT: 0.5,
        }[self]


# =============================================================================
# AgentCursor: The visible presence of an agent
# =============================================================================


@dataclass
class AgentCursor:
    """
    Represents an agent's visible presence in the workspace.

    Think of it as a Figma cursor for AI agents:
    - Position (focus_path): where the agent is looking
    - State: what the agent is doing
    - Behavior: how the agent moves (Phase 5B)
    - Activity: human-readable description
    - Visual properties: emoji, color, animation

    Phase 5B Enhancement:
    - behavior: CursorBehavior defines personality
    - canvas_position: 2D position for canvas rendering
    - velocity: Movement direction for smooth animation
    """

    agent_id: str
    display_name: str
    state: CursorState
    activity: str  # "Reading self.memory...", "Planning next step..."
    focus_path: str | None = None  # AGENTESE path being focused on
    last_update: datetime = field(default_factory=datetime.now)

    # Phase 5B: Behavior-driven movement
    behavior: "CursorBehavior | None" = None  # Import at runtime to avoid circular
    canvas_position: tuple[float, float] | None = None  # (x, y) for canvas
    velocity: tuple[float, float] = (0.0, 0.0)  # Movement direction

    # Optional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def emoji(self) -> str:
        """Delegate to state emoji."""
        return self.state.emoji

    @property
    def color(self) -> str:
        """Delegate to state color."""
        return self.state.color

    @property
    def effective_animation_speed(self) -> float:
        """
        Animation speed with circadian modulation.

        Pattern #11: Nighttime animations are slower (reflective mode).
        """
        base_speed = self.state.animation_speed
        phase = CircadianPhase.current()
        return base_speed * phase.tempo_modifier

    def transition_to(self, new_state: CursorState) -> bool:
        """
        Attempt state transition.

        Returns True if transition was valid and applied.
        Returns False if transition is invalid (state unchanged).
        """
        if not self.state.can_transition(new_state):
            logger.warning(
                f"Invalid cursor transition: {self.state.name} → {new_state.name} "
                f"(allowed: {', '.join(s.name for s in self.state.can_transition_to)})"
            )
            return False

        self.state = new_state
        self.last_update = datetime.now()
        return True

    def update_activity(self, activity: str, focus_path: str | None = None) -> None:
        """Update activity description and optional focus path."""
        self.activity = activity
        if focus_path is not None:
            self.focus_path = focus_path
        self.last_update = datetime.now()

    @property
    def behavior_emoji(self) -> str:
        """
        Get emoji combining state and behavior.

        Phase 5B: Behavior adds personality overlay.
        """
        if self.behavior is not None:
            return f"{self.behavior.emoji}{self.state.emoji}"
        return self.state.emoji

    def to_cli(self, teaching_mode: bool = False) -> str:
        """
        Render for CLI output.

        Pattern #14: Teaching Mode adds state transition info.
        Phase 5B: Includes behavior when present.
        """
        # Use behavior emoji if available
        emoji = self.behavior_emoji if self.behavior else self.emoji
        base = f"  {emoji} {self.display_name} is {self.activity}"

        if self.focus_path:
            base += f" [{self.focus_path}]"

        if teaching_mode:
            transitions = ", ".join(s.name for s in self.state.can_transition_to)
            base += f"\n     └─ State: {self.state.name} → can transition to: {transitions}"
            if self.behavior is not None:
                phase = CircadianPhase.current()
                base += f"\n     └─ Behavior: {self.behavior.describe_for_phase(phase)}"

        return base

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence/API."""
        result = {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "state": self.state.name,
            "activity": self.activity,
            "focus_path": self.focus_path,
            "last_update": self.last_update.isoformat(),
            "emoji": self.emoji,
            "color": self.color,
            "animation_speed": self.effective_animation_speed,
            "metadata": self.metadata,
        }

        # Phase 5B: Include behavior fields
        if self.behavior is not None:
            result["behavior"] = self.behavior.name
            result["behavior_emoji"] = self.behavior_emoji
        if self.canvas_position is not None:
            result["canvas_position"] = {
                "x": self.canvas_position[0],
                "y": self.canvas_position[1],
            }
        result["velocity"] = {"x": self.velocity[0], "y": self.velocity[1]}

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentCursor":
        """Deserialize from dict."""
        # Phase 5B: Parse behavior if present
        behavior = None
        if "behavior" in data:
            # Lazy import to avoid circular dependency
            from .behaviors import CursorBehavior
            behavior = CursorBehavior[data["behavior"]]

        # Parse canvas position
        canvas_position = None
        if "canvas_position" in data:
            cp = data["canvas_position"]
            canvas_position = (cp["x"], cp["y"])

        # Parse velocity
        velocity = (0.0, 0.0)
        if "velocity" in data:
            v = data["velocity"]
            velocity = (v["x"], v["y"])

        return cls(
            agent_id=data["agent_id"],
            display_name=data["display_name"],
            state=CursorState[data["state"]],
            activity=data["activity"],
            focus_path=data.get("focus_path"),
            last_update=datetime.fromisoformat(data["last_update"]),
            behavior=behavior,
            canvas_position=canvas_position,
            velocity=velocity,
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# PresenceUpdate: Event for presence changes
# =============================================================================


class PresenceEventType(Enum):
    """Types of presence events."""

    CURSOR_JOINED = "cursor_joined"
    CURSOR_LEFT = "cursor_left"
    CURSOR_MOVED = "cursor_moved"
    STATE_CHANGED = "state_changed"
    ACTIVITY_UPDATED = "activity_updated"


@dataclass
class PresenceUpdate:
    """
    Event emitted when agent presence changes.

    Used for real-time UI updates via EventBus.
    """

    event_type: PresenceEventType
    agent_id: str
    cursor: AgentCursor | None
    timestamp: datetime = field(default_factory=datetime.now)

    # For state changes
    old_state: CursorState | None = None
    new_state: CursorState | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for SSE/WebSocket."""
        return {
            "event_type": self.event_type.value,
            "agent_id": self.agent_id,
            "cursor": self.cursor.to_dict() if self.cursor else None,
            "timestamp": self.timestamp.isoformat(),
            "old_state": self.old_state.name if self.old_state else None,
            "new_state": self.new_state.name if self.new_state else None,
        }


# =============================================================================
# PresenceChannel: Broadcast channel for presence updates
# =============================================================================


class PresenceChannel:
    """
    Broadcast channel for real-time cursor positions.

    Uses a simple pub/sub pattern for fan-out to multiple subscribers
    (CLI, Web, sshx-like terminals).

    Usage:
        channel = PresenceChannel()

        # Publisher (agent)
        await channel.broadcast(cursor)

        # Subscriber (UI)
        async for update in channel.subscribe():
            render_cursor(update.cursor)
    """

    def __init__(self, max_queue_size: int = 100):
        """
        Initialize presence channel.

        Args:
            max_queue_size: Max events to buffer per subscriber
        """
        self._subscribers: list[asyncio.Queue[PresenceUpdate]] = []
        self._cursors: dict[str, AgentCursor] = {}
        self._max_queue_size = max_queue_size
        self._lock = asyncio.Lock()

    @property
    def active_cursors(self) -> list[AgentCursor]:
        """Get all active cursors."""
        return list(self._cursors.values())

    @property
    def subscriber_count(self) -> int:
        """Number of active subscribers."""
        return len(self._subscribers)

    async def join(self, cursor: AgentCursor) -> None:
        """
        Register an agent cursor.

        Broadcasts CURSOR_JOINED event to all subscribers.
        """
        async with self._lock:
            self._cursors[cursor.agent_id] = cursor

        update = PresenceUpdate(
            event_type=PresenceEventType.CURSOR_JOINED,
            agent_id=cursor.agent_id,
            cursor=cursor,
        )
        await self._broadcast(update)

        logger.info(f"Agent joined: {cursor.display_name} ({cursor.agent_id})")

    async def leave(self, agent_id: str) -> bool:
        """
        Unregister an agent cursor.

        Broadcasts CURSOR_LEFT event to all subscribers.
        Returns True if agent was present.
        """
        async with self._lock:
            cursor = self._cursors.pop(agent_id, None)

        if cursor is None:
            return False

        update = PresenceUpdate(
            event_type=PresenceEventType.CURSOR_LEFT,
            agent_id=agent_id,
            cursor=cursor,
        )
        await self._broadcast(update)

        logger.info(f"Agent left: {cursor.display_name} ({agent_id})")
        return True

    async def broadcast(self, cursor: AgentCursor) -> int:
        """
        Broadcast cursor update to all subscribers.

        Returns number of subscribers notified.
        """
        async with self._lock:
            old_cursor = self._cursors.get(cursor.agent_id)
            self._cursors[cursor.agent_id] = cursor

        # Determine event type
        if old_cursor is None:
            event_type = PresenceEventType.CURSOR_JOINED
            old_state = None
        elif old_cursor.state != cursor.state:
            event_type = PresenceEventType.STATE_CHANGED
            old_state = old_cursor.state
        elif old_cursor.activity != cursor.activity or old_cursor.focus_path != cursor.focus_path:
            event_type = PresenceEventType.ACTIVITY_UPDATED
            old_state = None
        else:
            event_type = PresenceEventType.CURSOR_MOVED
            old_state = None

        update = PresenceUpdate(
            event_type=event_type,
            agent_id=cursor.agent_id,
            cursor=cursor,
            old_state=old_state,
            new_state=cursor.state if old_state else None,
        )

        return await self._broadcast(update)

    async def _broadcast(self, update: PresenceUpdate) -> int:
        """Internal broadcast to all subscriber queues."""
        notified = 0
        dead_subscribers: list[asyncio.Queue[PresenceUpdate]] = []

        for queue in self._subscribers:
            try:
                # Non-blocking put - drop if queue full
                queue.put_nowait(update)
                notified += 1
            except asyncio.QueueFull:
                # Queue full, skip this subscriber
                logger.warning("Presence subscriber queue full, dropping update")
            except Exception:
                # Queue closed/broken
                dead_subscribers.append(queue)

        # Clean up dead subscribers
        for dead in dead_subscribers:
            self._subscribers.remove(dead)

        return notified

    async def subscribe(self) -> AsyncIterator[PresenceUpdate]:
        """
        Subscribe to presence updates.

        Yields PresenceUpdate events as they occur.
        Clean up by breaking from the loop or calling unsubscribe().
        """
        queue: asyncio.Queue[PresenceUpdate] = asyncio.Queue(maxsize=self._max_queue_size)
        self._subscribers.append(queue)

        try:
            while True:
                update = await queue.get()
                yield update
        finally:
            # Unsubscribe when iterator exits
            if queue in self._subscribers:
                self._subscribers.remove(queue)

    def get_cursor(self, agent_id: str) -> AgentCursor | None:
        """Get cursor by agent ID."""
        return self._cursors.get(agent_id)

    async def get_presence_snapshot(self) -> dict[str, Any]:
        """
        Get current presence state as a snapshot.

        Useful for initial page load before subscribing to updates.
        """
        async with self._lock:
            cursors = [c.to_dict() for c in self._cursors.values()]

        return {
            "cursors": cursors,
            "count": len(cursors),
            "phase": CircadianPhase.current().name,
            "tempo_modifier": CircadianPhase.current().tempo_modifier,
        }


# =============================================================================
# Singleton Channel
# =============================================================================


_channel: PresenceChannel | None = None


def get_presence_channel() -> PresenceChannel:
    """Get or create the singleton PresenceChannel."""
    global _channel
    if _channel is None:
        _channel = PresenceChannel()
    return _channel


def reset_presence_channel() -> None:
    """Reset the singleton (for testing)."""
    global _channel
    _channel = None


# =============================================================================
# CLI Presence Footer
# =============================================================================


def render_presence_footer(
    cursors: list[AgentCursor],
    teaching_mode: bool = False,
    width: int = 80,
) -> str:
    """
    Render presence footer for CLI output.

    Shows active agents and their current state.

    Example output:
        ─── Active Agents ────────────────────────────────────────
          👁️ K-gent is following your cursor [self.memory]
          ⚡ Explorer is working on pattern analysis
    """
    if not cursors:
        return ""

    # Build header
    header = "─── Active Agents " + "─" * max(0, width - 18)

    lines = [header]
    for cursor in cursors:
        lines.append(cursor.to_cli(teaching_mode=teaching_mode))

    return "\n".join(lines)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # State enums
    "CursorState",
    "CircadianPhase",
    "PresenceEventType",
    # Data classes
    "AgentCursor",
    "PresenceUpdate",
    # Channel
    "PresenceChannel",
    "get_presence_channel",
    "reset_presence_channel",
    # CLI helpers
    "render_presence_footer",
]
