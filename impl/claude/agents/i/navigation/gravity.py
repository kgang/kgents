"""
Semantic Gravity Layouts - Relevance-based agent positioning.

Force-directed layout where agents drift based on semantic relevance:
- Focused agent moves to center
- Related agents cluster nearby
- Irrelevant agents recede to periphery

The gravity field is computed from:
- Shared data/context
- Recent communication patterns
- Task similarity
- Explicit connections

Transitions are smooth (lerp over 500ms) to avoid jarring repositioning.

Usage:
    engine = GravityLayoutEngine()
    positions = engine.compute_positions(agents, focus="A-gent")

    # On each frame:
    engine.update(dt)  # Smooth transitions
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass


@dataclass
class Position:
    """2D position for layout."""

    x: float
    y: float

    def distance_to(self, other: Position) -> float:
        """Euclidean distance to another position."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def lerp(self, target: Position, t: float) -> Position:
        """Linear interpolation toward target."""
        t = max(0.0, min(1.0, t))
        return Position(
            x=self.x + (target.x - self.x) * t,
            y=self.y + (target.y - self.y) * t,
        )

    def __add__(self, other: Position) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Position) -> Position:
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Position:
        return Position(self.x * scalar, self.y * scalar)

    @property
    def magnitude(self) -> float:
        """Vector magnitude."""
        return math.sqrt(self.x**2 + self.y**2)

    def normalized(self) -> Position:
        """Unit vector in same direction."""
        mag = self.magnitude
        if mag < 0.0001:
            return Position(0, 0)
        return Position(self.x / mag, self.y / mag)


@dataclass
class AgentNode:
    """An agent in the gravity layout."""

    id: str
    name: str
    position: Position = field(default_factory=lambda: Position(0, 0))
    target_position: Position = field(default_factory=lambda: Position(0, 0))
    velocity: Position = field(default_factory=lambda: Position(0, 0))
    relevance: float = 0.5  # 0.0 to 1.0 (affects gravity)
    mass: float = 1.0  # Resistance to movement
    is_locked: bool = False  # Manual positioning override
    connections: list[str] = field(default_factory=list)


@dataclass
class GravityConfig:
    """Configuration for the gravity engine."""

    # Layout parameters
    center: Position = field(default_factory=lambda: Position(0, 0))
    max_distance: float = 100.0  # Max distance from center
    min_distance: float = 10.0  # Min distance between agents

    # Animation parameters
    transition_duration: float = 0.5  # Seconds for smooth transition
    damping: float = 0.8  # Velocity damping (0-1)
    spring_strength: float = 0.1  # Connection spring strength
    repulsion_strength: float = 50.0  # Agent repulsion force

    # Relevance thresholds
    high_relevance: float = 0.7
    low_relevance: float = 0.3


class RelevanceScorer:
    """
    Computes relevance scores between agents.

    Relevance is based on:
    - Shared context/data
    - Recent communication
    - Task similarity
    - Explicit connections
    """

    def __init__(self) -> None:
        """Initialize the scorer."""
        self._communication_history: dict[str, list[tuple[str, datetime]]] = {}
        self._context_overlaps: dict[tuple[str, str], float] = {}

    def score(
        self,
        agent_id: str,
        focus_id: str | None,
        connections: list[str],
    ) -> float:
        """
        Compute relevance score for an agent.

        Args:
            agent_id: Agent to score
            focus_id: Currently focused agent (if any)
            connections: Agent's connections

        Returns:
            Relevance score from 0.0 to 1.0
        """
        if focus_id is None:
            return 0.5  # Default neutral relevance

        if agent_id == focus_id:
            return 1.0  # Focus agent is always fully relevant

        score = 0.3  # Base score

        # Direct connection bonus
        if focus_id in connections:
            score += 0.4

        # Recent communication bonus
        recent = self._get_recent_communication(agent_id, focus_id)
        if recent:
            recency_bonus = 0.2 * max(0, 1 - recent.total_seconds() / 60)
            score += recency_bonus

        # Context overlap bonus
        overlap = self._context_overlaps.get((agent_id, focus_id), 0.0)
        score += 0.1 * overlap

        return min(1.0, max(0.0, score))

    def record_communication(self, from_id: str, to_id: str) -> None:
        """Record a communication between agents."""
        now = datetime.now()
        if from_id not in self._communication_history:
            self._communication_history[from_id] = []
        self._communication_history[from_id].append((to_id, now))

        # Keep only recent history
        self._communication_history[from_id] = [
            (tid, t)
            for tid, t in self._communication_history[from_id]
            if now - t < timedelta(minutes=5)
        ]

    def set_context_overlap(self, agent_a: str, agent_b: str, overlap: float) -> None:
        """Set context overlap score between agents."""
        self._context_overlaps[(agent_a, agent_b)] = overlap
        self._context_overlaps[(agent_b, agent_a)] = overlap

    def _get_recent_communication(
        self,
        agent_id: str,
        target_id: str,
    ) -> timedelta | None:
        """Get time since last communication with target."""
        history = self._communication_history.get(agent_id, [])
        for tid, timestamp in reversed(history):
            if tid == target_id:
                return datetime.now() - timestamp
        return None


class GravityLayoutEngine:
    """
    Force-directed layout with semantic gravity.

    Positions agents based on relevance to the focused agent,
    with smooth animated transitions.
    """

    def __init__(self, config: GravityConfig | None = None) -> None:
        """
        Initialize the gravity engine.

        Args:
            config: Layout configuration
        """
        self.config = config or GravityConfig()
        self._nodes: dict[str, AgentNode] = {}
        self._focus_id: str | None = None
        self._scorer = RelevanceScorer()
        self._last_update = datetime.now()

    def add_agent(
        self,
        agent_id: str,
        name: str,
        initial_position: Position | None = None,
        connections: list[str] | None = None,
    ) -> AgentNode:
        """
        Add an agent to the layout.

        Args:
            agent_id: Unique agent ID
            name: Display name
            initial_position: Starting position
            connections: Connected agent IDs

        Returns:
            Created AgentNode
        """
        pos = initial_position or self._random_position()
        node = AgentNode(
            id=agent_id,
            name=name,
            position=pos,
            target_position=pos,
            connections=connections or [],
        )
        self._nodes[agent_id] = node
        return node

    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the layout."""
        self._nodes.pop(agent_id, None)

    def set_focus(self, agent_id: str | None) -> None:
        """
        Set the focused agent.

        The focused agent moves to center, related agents cluster nearby.

        Args:
            agent_id: Agent to focus (None to clear focus)
        """
        self._focus_id = agent_id
        self._recompute_targets()

    def lock_position(self, agent_id: str, locked: bool = True) -> None:
        """Lock or unlock an agent's position."""
        if agent_id in self._nodes:
            self._nodes[agent_id].is_locked = locked

    def set_position(self, agent_id: str, position: Position) -> None:
        """Manually set an agent's position."""
        if agent_id in self._nodes:
            node = self._nodes[agent_id]
            node.position = position
            node.target_position = position

    def update(self, dt: float | None = None) -> None:
        """
        Update layout animation.

        Call this each frame to animate smooth transitions.

        Args:
            dt: Delta time in seconds (auto-calculated if None)
        """
        now = datetime.now()
        if dt is None:
            dt = (now - self._last_update).total_seconds()
        self._last_update = now

        # Clamp dt to avoid huge jumps
        dt = min(dt, 0.1)

        for node in self._nodes.values():
            if node.is_locked:
                continue

            # Compute forces
            force = Position(0, 0)

            # 1. Attraction to target (semantic gravity)
            to_target = node.target_position - node.position
            force = force + to_target * self.config.spring_strength

            # 2. Repulsion from other agents
            for other in self._nodes.values():
                if other.id == node.id:
                    continue
                diff = node.position - other.position
                dist = diff.magnitude
                if dist < self.config.min_distance:
                    # Strong repulsion when too close
                    repel = diff.normalized() * (
                        self.config.repulsion_strength / max(dist * dist, 1)
                    )
                    force = force + repel

            # 3. Apply force as acceleration (F = ma, a = F/m)
            acceleration = force * (1.0 / node.mass)
            node.velocity = node.velocity + acceleration * dt

            # 4. Apply damping
            node.velocity = node.velocity * self.config.damping

            # 5. Update position
            node.position = node.position + node.velocity * dt

    def compute_positions(
        self,
        focus: str | None = None,
    ) -> dict[str, Position]:
        """
        Compute target positions for all agents.

        Args:
            focus: Agent ID to focus on

        Returns:
            Dict mapping agent IDs to positions
        """
        if focus is not None:
            self.set_focus(focus)

        return {agent_id: node.position for agent_id, node in self._nodes.items()}

    def get_positions(self) -> dict[str, Position]:
        """Get current positions of all agents."""
        return {agent_id: node.position for agent_id, node in self._nodes.items()}

    def get_node(self, agent_id: str) -> AgentNode | None:
        """Get a specific agent node."""
        return self._nodes.get(agent_id)

    def reset_to_gravity(self) -> None:
        """Reset all agents to gravity-computed positions."""
        for node in self._nodes.values():
            node.is_locked = False
        self._recompute_targets()

    # ─────────────────────────────────────────────────────────────
    # Internal Methods
    # ─────────────────────────────────────────────────────────────

    def _recompute_targets(self) -> None:
        """Recompute target positions based on current focus."""
        if not self._nodes:
            return

        center = self.config.center

        # If no focus, spread evenly in a circle
        if self._focus_id is None:
            self._distribute_circular()
            return

        # Focus agent goes to center
        if self._focus_id in self._nodes:
            self._nodes[self._focus_id].target_position = center
            self._nodes[self._focus_id].relevance = 1.0

        # Compute relevance for all agents
        for agent_id, node in self._nodes.items():
            if agent_id == self._focus_id:
                continue

            relevance = self._scorer.score(
                agent_id,
                self._focus_id,
                node.connections,
            )
            node.relevance = relevance

            # Position based on relevance
            # Higher relevance = closer to center
            distance = self.config.max_distance * (1.0 - relevance)
            angle = self._compute_angle(agent_id)

            node.target_position = Position(
                x=center.x + distance * math.cos(angle),
                y=center.y + distance * math.sin(angle),
            )

    def _distribute_circular(self) -> None:
        """Distribute agents in a circle when no focus."""
        if not self._nodes:
            return

        center = self.config.center
        radius = self.config.max_distance * 0.6
        n = len(self._nodes)

        for i, (agent_id, node) in enumerate(self._nodes.items()):
            angle = 2 * math.pi * i / n
            node.target_position = Position(
                x=center.x + radius * math.cos(angle),
                y=center.y + radius * math.sin(angle),
            )
            node.relevance = 0.5

    def _compute_angle(self, agent_id: str) -> float:
        """
        Compute angle for agent based on relationships.

        Agents with similar connections cluster together.
        """
        node = self._nodes.get(agent_id)
        if not node:
            return 0.0

        # Use hash of connections to get consistent angle
        conn_hash = hash(frozenset(node.connections))
        return (conn_hash % 360) * math.pi / 180

    def _random_position(self) -> Position:
        """Generate a random starting position."""
        import random

        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(
            self.config.min_distance,
            self.config.max_distance,
        )
        return Position(
            x=self.config.center.x + radius * math.cos(angle),
            y=self.config.center.y + radius * math.sin(angle),
        )


def create_demo_layout(agent_ids: list[str]) -> GravityLayoutEngine:
    """Create a demo layout for testing."""
    engine = GravityLayoutEngine()

    # Add agents with some connections
    for i, agent_id in enumerate(agent_ids):
        connections = []
        if i > 0:
            connections.append(agent_ids[i - 1])  # Connect to previous
        if i < len(agent_ids) - 1:
            connections.append(agent_ids[i + 1])  # Connect to next

        engine.add_agent(
            agent_id=agent_id,
            name=agent_id.replace("-", " ").title(),
            connections=connections,
        )

    return engine


__all__ = [
    "GravityLayoutEngine",
    "GravityConfig",
    "AgentNode",
    "Position",
    "RelevanceScorer",
    "create_demo_layout",
]
