"""
Pheromone Trail Visualization - Stigmergic communication between agents.

Pheromone trails visualize inter-agent communication patterns inspired by
ant colony communication. Trails fade over time, showing the recency and
intensity of agent interactions.

Key concepts:
- Trails connect source → target agents
- Intensity decays with time (half-life ~30 seconds)
- Different message types have distinct colors
- Direction indicated by arrow heads

Usage:
    manager = PheromoneManager()
    manager.emit(source="A-gent", target="B-gent", msg_type="query")

    # In render loop:
    for trail in manager.active_trails():
        render_trail(trail)

    # Decay trails each frame:
    manager.decay(elapsed_seconds)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class MessageType(Enum):
    """Types of inter-agent messages."""

    QUERY = auto()  # Information request
    RESPONSE = auto()  # Information response
    COMMAND = auto()  # Action directive
    SIGNAL = auto()  # Status update
    YIELD = auto()  # Control handoff
    ERROR = auto()  # Error notification
    SYNC = auto()  # Synchronization


# Color palette for message types (hex colors)
MESSAGE_COLORS = {
    MessageType.QUERY: "#8ac4e8",  # Blue
    MessageType.RESPONSE: "#7bc275",  # Green
    MessageType.COMMAND: "#f5d08a",  # Gold
    MessageType.SIGNAL: "#b3a89a",  # Neutral
    MessageType.YIELD: "#e6a352",  # Orange
    MessageType.ERROR: "#e88a8a",  # Red
    MessageType.SYNC: "#8b7ba5",  # Purple
}


@dataclass
class Position:
    """2D position for rendering."""

    x: float
    y: float

    def distance_to(self, other: Position) -> float:
        """Calculate Euclidean distance to another position."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class PheromoneTrail:
    """
    A fading trace of agent-to-agent communication.

    Trails decay exponentially over time, becoming less visible
    until they fade completely.
    """

    id: str
    source: str  # Source agent ID
    target: str  # Target agent ID
    message_type: MessageType
    created_at: datetime
    content_preview: str = ""  # Brief preview of message content
    intensity: float = 1.0  # Current intensity (0.0 to 1.0)
    half_life: float = 30.0  # Seconds until intensity halves

    # Visual properties (set during rendering)
    source_pos: Position | None = None
    target_pos: Position | None = None

    def decay(self, elapsed_seconds: float) -> float:
        """
        Calculate and apply decay based on elapsed time.

        Args:
            elapsed_seconds: Time elapsed since last decay

        Returns:
            New intensity after decay
        """
        if self.half_life <= 0:
            return self.intensity

        # Exponential decay: I = I0 * 0.5^(t/half_life)
        decay_factor = 0.5 ** (elapsed_seconds / self.half_life)
        self.intensity *= decay_factor
        return self.intensity

    def get_age(self) -> timedelta:
        """Get age of the trail."""
        return datetime.now() - self.created_at

    def get_color(self) -> str:
        """Get the color for this trail type."""
        return MESSAGE_COLORS.get(self.message_type, "#b3a89a")

    def get_opacity(self) -> float:
        """Get render opacity based on intensity."""
        return max(0.0, min(1.0, self.intensity))

    def get_width(self) -> int:
        """Get line width based on intensity."""
        # 1-3 characters wide based on intensity
        return max(1, min(3, int(self.intensity * 3) + 1))

    def is_faded(self, threshold: float = 0.1) -> bool:
        """Check if trail has faded below visibility threshold."""
        return self.intensity < threshold


@dataclass
class PheromoneEmission:
    """Request to emit a new pheromone trail."""

    source: str
    target: str
    message_type: MessageType | str
    content_preview: str = ""
    initial_intensity: float = 1.0


class PheromoneManager:
    """
    Manages pheromone trails for stigmergic visualization.

    Handles:
    - Trail creation and emission
    - Decay over time
    - Garbage collection of faded trails
    - Query of active trails
    """

    def __init__(
        self,
        default_half_life: float = 30.0,
        fade_threshold: float = 0.1,
        max_trails: int = 100,
    ) -> None:
        """
        Initialize the pheromone manager.

        Args:
            default_half_life: Default decay half-life in seconds
            fade_threshold: Intensity below which trails are removed
            max_trails: Maximum number of active trails
        """
        self._trails: dict[str, PheromoneTrail] = {}
        self._default_half_life = default_half_life
        self._fade_threshold = fade_threshold
        self._max_trails = max_trails
        self._next_id = 0
        self._last_decay_time = datetime.now()

    def emit(
        self,
        source: str,
        target: str,
        message_type: MessageType | str,
        content_preview: str = "",
        intensity: float = 1.0,
        half_life: float | None = None,
    ) -> PheromoneTrail:
        """
        Emit a new pheromone trail between agents.

        Args:
            source: Source agent ID
            target: Target agent ID
            message_type: Type of message
            content_preview: Brief preview of content
            intensity: Initial intensity
            half_life: Decay half-life (defaults to manager default)

        Returns:
            The created trail
        """
        # Convert string message type if needed
        if isinstance(message_type, str):
            try:
                message_type = MessageType[message_type.upper()]
            except KeyError:
                message_type = MessageType.SIGNAL

        # Create trail
        trail_id = f"trail-{self._next_id:06d}"
        self._next_id += 1

        trail = PheromoneTrail(
            id=trail_id,
            source=source,
            target=target,
            message_type=message_type,
            created_at=datetime.now(),
            content_preview=content_preview,
            intensity=intensity,
            half_life=half_life or self._default_half_life,
        )

        self._trails[trail_id] = trail

        # Prune if over limit
        self._prune_oldest()

        return trail

    def emit_batch(self, emissions: list[PheromoneEmission]) -> list[PheromoneTrail]:
        """Emit multiple trails at once."""
        return [
            self.emit(
                source=e.source,
                target=e.target,
                message_type=e.message_type,
                content_preview=e.content_preview,
                intensity=e.initial_intensity,
            )
            for e in emissions
        ]

    def decay_all(self, elapsed_seconds: float | None = None) -> int:
        """
        Apply decay to all trails.

        Args:
            elapsed_seconds: Time since last decay. If None, calculated automatically.

        Returns:
            Number of trails removed due to fading
        """
        now = datetime.now()

        if elapsed_seconds is None:
            elapsed_seconds = (now - self._last_decay_time).total_seconds()

        self._last_decay_time = now

        # Apply decay and collect faded trails
        faded_ids = []
        for trail_id, trail in self._trails.items():
            trail.decay(elapsed_seconds)
            if trail.is_faded(self._fade_threshold):
                faded_ids.append(trail_id)

        # Remove faded trails
        for trail_id in faded_ids:
            del self._trails[trail_id]

        return len(faded_ids)

    def active_trails(self) -> list[PheromoneTrail]:
        """Get all currently active (non-faded) trails."""
        return [
            t for t in self._trails.values() if not t.is_faded(self._fade_threshold)
        ]

    def trails_from(self, agent_id: str) -> list[PheromoneTrail]:
        """Get trails originating from a specific agent."""
        return [t for t in self.active_trails() if t.source == agent_id]

    def trails_to(self, agent_id: str) -> list[PheromoneTrail]:
        """Get trails targeting a specific agent."""
        return [t for t in self.active_trails() if t.target == agent_id]

    def trails_between(self, agent_a: str, agent_b: str) -> list[PheromoneTrail]:
        """Get trails between two agents (in either direction)."""
        return [
            t
            for t in self.active_trails()
            if (t.source == agent_a and t.target == agent_b)
            or (t.source == agent_b and t.target == agent_a)
        ]

    def get_trail(self, trail_id: str) -> PheromoneTrail | None:
        """Get a specific trail by ID."""
        return self._trails.get(trail_id)

    def clear(self) -> None:
        """Clear all trails."""
        self._trails.clear()

    def count(self) -> int:
        """Get number of active trails."""
        return len(self._trails)

    def _prune_oldest(self) -> None:
        """Remove oldest trails if over limit."""
        while len(self._trails) > self._max_trails:
            # Find oldest trail
            oldest_id = min(
                self._trails.keys(),
                key=lambda k: self._trails[k].created_at,
            )
            del self._trails[oldest_id]


def render_trail_ascii(
    trail: PheromoneTrail,
    source_pos: tuple[int, int],
    target_pos: tuple[int, int],
) -> list[tuple[int, int, str]]:
    """
    Render a trail as ASCII characters for terminal display.

    Args:
        trail: The trail to render
        source_pos: (x, y) position of source
        target_pos: (x, y) position of target

    Returns:
        List of (x, y, char) tuples for rendering
    """
    chars: list[tuple[int, int, str]] = []
    sx, sy = source_pos
    tx, ty = target_pos

    # Calculate direction
    dx = tx - sx
    dy = ty - sy
    length = max(abs(dx), abs(dy))

    if length == 0:
        return chars

    # Determine line characters based on direction
    if abs(dx) > abs(dy) * 2:
        line_char = "─"
        arrow = "→" if dx > 0 else "←"
    elif abs(dy) > abs(dx) * 2:
        line_char = "│"
        arrow = "↓" if dy > 0 else "↑"
    elif dx > 0 and dy > 0:
        line_char = "╲"
        arrow = "↘"
    elif dx > 0 and dy < 0:
        line_char = "╱"
        arrow = "↗"
    elif dx < 0 and dy > 0:
        line_char = "╱"
        arrow = "↙"
    else:
        line_char = "╲"
        arrow = "↖"

    # Draw line (simplified - just show start, middle, end)
    if length >= 3:
        # Midpoint
        mx = sx + dx // 2
        my = sy + dy // 2
        chars.append((mx, my, line_char))

    # Arrow at target
    chars.append((tx, ty, arrow))

    return chars


def create_demo_trails(agent_ids: list[str]) -> list[PheromoneTrail]:
    """Create demo trails for testing."""
    if len(agent_ids) < 2:
        return []

    manager = PheromoneManager()

    # Create some sample trails
    trails = []
    for i, source in enumerate(agent_ids[:-1]):
        target = agent_ids[(i + 1) % len(agent_ids)]
        msg_type = list(MessageType)[i % len(MessageType)]

        trail = manager.emit(
            source=source,
            target=target,
            message_type=msg_type,
            content_preview=f"Message from {source} to {target}",
            intensity=0.5 + 0.5 * (i / len(agent_ids)),
        )
        trails.append(trail)

    return trails


__all__ = [
    "PheromoneTrail",
    "PheromoneEmission",
    "PheromoneManager",
    "MessageType",
    "MESSAGE_COLORS",
    "Position",
    "render_trail_ascii",
    "create_demo_trails",
]
