"""
Cursor Behaviors: Personality-driven agent movement patterns.

CLI v7 Phase 5B: Cursor Behaviors

This implements heterarchical agent presence—agents aren't just
visible, they have *character*. Each behavior defines how an
agent cursor moves through the AGENTESE graph:

- FOLLOWER: Loyal companion, follows human with empathetic delay
- EXPLORER: Curious wanderer, independent discovery
- ASSISTANT: Helpful partner, follows but offers suggestions
- AUTONOMOUS: Self-directed, pursues its own trajectory

The behavior system integrates with:
- CircadianPhase: Night explorers are more contemplative
- Human focus tracking: Behaviors respond to where attention goes
- CursorState: Behaviors influence valid state transitions

Design Principles Applied:
- Heterarchical (§6): No fixed boss—follower can become leader
- Joy-Inducing (§4): Each behavior has personality
- Composable (§5): Behaviors can layer and modulate
- AGENTESE: "The noun is a lie. There is only the rate of change."

Usage:
    behavior = CursorBehavior.EXPLORER
    animator = BehaviorAnimator(behavior)

    # Each frame, compute next position
    next_pos = animator.animate(
        current_pos=cursor.focus_path,
        human_focus=human.focus_path,
        graph=agentese_graph,
        dt=0.016,  # 60fps
    )
"""

from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Protocol, runtime_checkable

from .presence import CircadianPhase, CursorState

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# CursorBehavior: The personality of agent movement
# =============================================================================


class CursorBehavior(Enum):
    """
    Agent cursor behavior patterns with rich personality.

    Each behavior defines how the agent navigates the AGENTESE graph.
    Inspired by Figma's multiplayer cursors, but with agency.

    The hierarchy is NOT fixed (Heterarchical principle):
    - A FOLLOWER can sense when to lead
    - An AUTONOMOUS can choose to follow
    - An ASSISTANT knows when to step back

    "Daring, bold, creative, opinionated but not gaudy"
    """

    FOLLOWER = auto()  # Loyal companion, follows with empathy
    EXPLORER = auto()  # Curious wanderer, independent discovery
    ASSISTANT = auto()  # Helpful partner, follows but suggests
    AUTONOMOUS = auto()  # Self-directed, pursues own trajectory

    @property
    def emoji(self) -> str:
        """Visual indicator reflecting personality."""
        return {
            CursorBehavior.FOLLOWER: "🐕",  # Loyal, attentive
            CursorBehavior.EXPLORER: "🦋",  # Free, wandering
            CursorBehavior.ASSISTANT: "🤝",  # Collaborative
            CursorBehavior.AUTONOMOUS: "🌟",  # Self-directed, luminous
        }[self]

    @property
    def description(self) -> str:
        """Human-readable personality description."""
        return {
            CursorBehavior.FOLLOWER: "Follows your focus with empathetic timing",
            CursorBehavior.EXPLORER: "Wanders independently, discovering connections",
            CursorBehavior.ASSISTANT: "Stays close but offers helpful suggestions",
            CursorBehavior.AUTONOMOUS: "Pursues its own meaningful trajectory",
        }[self]

    @property
    def follow_strength(self) -> float:
        """
        How strongly this behavior tracks human focus (0.0-1.0).

        1.0 = tightly coupled to human
        0.0 = completely independent
        """
        return {
            CursorBehavior.FOLLOWER: 0.9,  # Close but not mechanical
            CursorBehavior.EXPLORER: 0.1,  # Occasional awareness
            CursorBehavior.ASSISTANT: 0.6,  # Attentive but not clingy
            CursorBehavior.AUTONOMOUS: 0.0,  # Self-determined
        }[self]

    @property
    def exploration_tendency(self) -> float:
        """
        How likely to explore adjacent nodes (0.0-1.0).

        Higher = more curious, more tangential.
        The Accursed Share: exploration budget for "useless" discovery.
        """
        return {
            CursorBehavior.FOLLOWER: 0.1,  # Minimal wandering
            CursorBehavior.EXPLORER: 0.9,  # High curiosity
            CursorBehavior.ASSISTANT: 0.3,  # Moderate exploration
            CursorBehavior.AUTONOMOUS: 0.5,  # Purposeful but open
        }[self]

    @property
    def suggestion_probability(self) -> float:
        """
        Probability of making a suggestion per second (0.0-1.0).

        Higher = more vocal, more proactive.
        """
        return {
            CursorBehavior.FOLLOWER: 0.02,  # Rarely interjects
            CursorBehavior.EXPLORER: 0.05,  # Shares discoveries
            CursorBehavior.ASSISTANT: 0.15,  # Actively helpful
            CursorBehavior.AUTONOMOUS: 0.08,  # Shares when relevant
        }[self]

    @property
    def movement_smoothness(self) -> float:
        """
        How smooth the movement interpolation is (0.0-1.0).

        Higher = slower, more graceful
        Lower = quicker, more reactive
        """
        return {
            CursorBehavior.FOLLOWER: 0.7,  # Smooth following
            CursorBehavior.EXPLORER: 0.4,  # Quick and curious
            CursorBehavior.ASSISTANT: 0.6,  # Balanced
            CursorBehavior.AUTONOMOUS: 0.5,  # Steady but purposeful
        }[self]

    @property
    def preferred_states(self) -> frozenset[CursorState]:
        """
        States this behavior tends toward.

        Behaviors influence state transitions:
        - EXPLORER prefers EXPLORING state
        - FOLLOWER prefers FOLLOWING state
        """
        return {
            CursorBehavior.FOLLOWER: frozenset(
                {
                    CursorState.FOLLOWING,
                    CursorState.WAITING,
                }
            ),
            CursorBehavior.EXPLORER: frozenset(
                {
                    CursorState.EXPLORING,
                    CursorState.WORKING,
                }
            ),
            CursorBehavior.ASSISTANT: frozenset(
                {
                    CursorState.FOLLOWING,
                    CursorState.SUGGESTING,
                }
            ),
            CursorBehavior.AUTONOMOUS: frozenset(
                {
                    CursorState.WORKING,
                    CursorState.EXPLORING,
                }
            ),
        }[self]

    @property
    def circadian_sensitivity(self) -> float:
        """
        How much circadian phase affects behavior (0.0-1.0).

        Higher = more affected by time of day.

        Night explorers slow down (reflective mode).
        Followers remain consistent (loyalty).
        """
        return {
            CursorBehavior.FOLLOWER: 0.3,  # Consistent companion
            CursorBehavior.EXPLORER: 0.8,  # Night = contemplative
            CursorBehavior.ASSISTANT: 0.5,  # Moderate adjustment
            CursorBehavior.AUTONOMOUS: 0.6,  # Self-aware of cycles
        }[self]

    def describe_for_phase(self, phase: CircadianPhase) -> str:
        """
        Get behavior description modulated by circadian phase.

        Pattern #11: Circadian Modulation
        """
        base = self.description

        if phase in (CircadianPhase.NIGHT, CircadianPhase.EVENING):
            modifiers = {
                CursorBehavior.FOLLOWER: " (in quiet attendance)",
                CursorBehavior.EXPLORER: " (contemplatively)",
                CursorBehavior.ASSISTANT: " (with gentle suggestions)",
                CursorBehavior.AUTONOMOUS: " (in reflective mode)",
            }
        elif phase in (CircadianPhase.MORNING, CircadianPhase.NOON):
            modifiers = {
                CursorBehavior.FOLLOWER: " (alertly tracking)",
                CursorBehavior.EXPLORER: " (energetically)",
                CursorBehavior.ASSISTANT: " (proactively)",
                CursorBehavior.AUTONOMOUS: " (with clear purpose)",
            }
        else:
            modifiers = {b: "" for b in CursorBehavior}

        return base + modifiers.get(self, "")


# =============================================================================
# Position & Movement Types
# =============================================================================


@dataclass(frozen=True)
class Position:
    """
    2D position for canvas rendering.

    Immutable for functional purity.
    """

    x: float
    y: float

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Position":
        return Position(self.x * scalar, self.y * scalar)

    def distance_to(self, other: "Position") -> float:
        """Euclidean distance."""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def lerp(self, target: "Position", t: float) -> "Position":
        """Linear interpolation toward target."""
        t = max(0.0, min(1.0, t))  # Clamp
        return Position(
            self.x + (target.x - self.x) * t,
            self.y + (target.y - self.y) * t,
        )


@dataclass
class FocusPoint:
    """
    A point of focus in the AGENTESE graph.

    Combines path (logical) with position (visual).
    """

    path: str  # AGENTESE path (e.g., "self.memory")
    position: Position  # Canvas position
    timestamp: datetime = field(default_factory=datetime.now)

    def age_seconds(self) -> float:
        """Time since this focus was set."""
        return (datetime.now() - self.timestamp).total_seconds()


# =============================================================================
# Human Focus Tracking
# =============================================================================


@dataclass
class HumanFocusTracker:
    """
    Tracks human focus for behavior integration.

    Records where the human is looking/clicking/typing
    so agent behaviors can respond appropriately.

    The Accursed Share: We don't capture everything—
    we sample, summarize, and let the rest flow.
    """

    history: list[FocusPoint] = field(default_factory=list)
    max_history: int = 50

    # Computed state
    _velocity: Position = field(default_factory=lambda: Position(0.0, 0.0))
    _last_update: datetime = field(default_factory=datetime.now)

    @property
    def current(self) -> FocusPoint | None:
        """Most recent focus point."""
        return self.history[-1] if self.history else None

    @property
    def velocity(self) -> Position:
        """Estimated velocity of focus movement."""
        return self._velocity

    @property
    def is_stationary(self) -> bool:
        """True if focus hasn't moved recently."""
        if not self.current:
            return True
        return self.current.age_seconds() > 2.0

    @property
    def focus_duration(self) -> float:
        """How long focus has been on current path."""
        if not self.current:
            return 0.0

        current_path = self.current.path
        duration = 0.0

        for point in reversed(self.history):
            if point.path == current_path:
                duration = (datetime.now() - point.timestamp).total_seconds()
            else:
                break

        return duration

    def update(self, path: str, position: Position) -> None:
        """
        Record new focus point.

        Updates velocity estimate and trims history.
        """
        now = datetime.now()

        # Compute velocity
        if self.current:
            dt = (now - self._last_update).total_seconds()
            if dt > 0:
                dx = position.x - self.current.position.x
                dy = position.y - self.current.position.y
                self._velocity = Position(dx / dt, dy / dt)

        # Add to history
        self.history.append(FocusPoint(path=path, position=position, timestamp=now))

        # Trim (Pattern #8: Bounded History)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history :]

        self._last_update = now

    def get_recent_paths(self, seconds: float = 30.0) -> list[str]:
        """Get unique paths visited in the last N seconds."""
        cutoff = datetime.now() - timedelta(seconds=seconds)
        seen = set()
        result = []

        for point in reversed(self.history):
            if point.timestamp < cutoff:
                break
            if point.path not in seen:
                seen.add(point.path)
                result.append(point.path)

        return result


# =============================================================================
# Graph Protocol
# =============================================================================


@runtime_checkable
class AGENTESEGraph(Protocol):
    """
    Protocol for AGENTESE graph navigation.

    Behaviors need to know:
    - What nodes exist
    - How they connect
    - Where they are positioned

    Concrete implementations in protocols/agentese/
    """

    def get_connected_paths(self, path: str) -> list[str]:
        """Get paths directly connected to this path."""
        ...

    def get_position(self, path: str) -> Position | None:
        """Get canvas position for a path."""
        ...

    def get_all_paths(self) -> list[str]:
        """Get all registered paths."""
        ...


# =============================================================================
# BehaviorAnimator: The movement engine
# =============================================================================


@dataclass
class BehaviorAnimator:
    """
    Animates agent cursor with behavior-driven movement.

    This is where personality becomes motion:
    - FOLLOWERs track human focus with empathetic delay
    - EXPLORERs random-walk the graph with curiosity
    - ASSISTANTs stay close but wander to suggestions
    - AUTONOMOUS agents pursue their own path

    Circadian modulation: Night animations are slower,
    more contemplative. Morning is energetic.

    "The persona is a garden, not a museum."
    """

    behavior: CursorBehavior

    # Current state
    current_position: Position = field(default_factory=lambda: Position(0.0, 0.0))
    current_path: str = ""
    target_position: Position | None = None
    target_path: str | None = None

    # Timing
    time_at_current: float = 0.0
    suggestion_cooldown: float = 0.0

    # Noise for organic feel (Accursed Share: accept randomness)
    _noise_seed: float = field(default_factory=lambda: random.random() * 1000)

    def animate(
        self,
        human_focus: HumanFocusTracker,
        graph: AGENTESEGraph | None,
        dt: float,
        phase: CircadianPhase | None = None,
    ) -> tuple[Position, str | None]:
        """
        Compute next position and optional path.

        Args:
            human_focus: Current human focus state
            graph: AGENTESE graph for navigation
            dt: Delta time in seconds
            phase: Current circadian phase (auto-detected if None)

        Returns:
            (new_position, new_path_or_None)
        """
        if phase is None:
            phase = CircadianPhase.current()

        # Apply circadian modulation
        tempo = self._get_tempo(phase)

        # Update timers
        self.time_at_current += dt
        self.suggestion_cooldown = max(0.0, self.suggestion_cooldown - dt)

        # Choose target based on behavior
        self._update_target(human_focus, graph, dt, tempo)

        # Animate toward target
        new_position = self._interpolate(dt, tempo)
        new_path = self.target_path if self.target_path != self.current_path else None

        # Update state
        if new_path:
            self.current_path = new_path
            self.time_at_current = 0.0

        self.current_position = new_position

        return new_position, new_path

    def _get_tempo(self, phase: CircadianPhase) -> float:
        """Get tempo multiplier based on circadian phase and behavior."""
        base_tempo = phase.tempo_modifier
        sensitivity = self.behavior.circadian_sensitivity

        # Blend between 1.0 (unaffected) and phase tempo
        return 1.0 - sensitivity + (sensitivity * base_tempo)

    def _update_target(
        self,
        human_focus: HumanFocusTracker,
        graph: AGENTESEGraph | None,
        dt: float,
        tempo: float,
    ) -> None:
        """Update target position/path based on behavior."""
        follow_strength = self.behavior.follow_strength
        explore_tendency = self.behavior.exploration_tendency * tempo

        # Should we follow human?
        if human_focus.current and random.random() < follow_strength:
            self.target_position = human_focus.current.position
            self.target_path = human_focus.current.path
            return

        # Should we explore?
        if graph and random.random() < explore_tendency * dt:
            self._pick_exploration_target(graph)
            return

        # Stay at current position (with noise)
        if self.target_position is None:
            self.target_position = self.current_position

    def _pick_exploration_target(self, graph: AGENTESEGraph) -> None:
        """Pick a new exploration target from the graph."""
        # Prefer connected paths
        if self.current_path:
            connected = graph.get_connected_paths(self.current_path)
            if connected:
                path = random.choice(connected)
                pos = graph.get_position(path)
                if pos:
                    self.target_path = path
                    self.target_position = pos
                    return

        # Fall back to any path
        all_paths = graph.get_all_paths()
        if all_paths:
            path = random.choice(all_paths)
            pos = graph.get_position(path)
            if pos:
                self.target_path = path
                self.target_position = pos

    def _interpolate(self, dt: float, tempo: float) -> Position:
        """Interpolate current position toward target."""
        if self.target_position is None:
            return self.current_position

        # Smoothness determines interpolation speed
        smoothness = self.behavior.movement_smoothness
        t = dt / (smoothness * 0.5) * tempo

        # Add organic noise (The Accursed Share: embrace randomness)
        noise = self._organic_noise(dt)
        target_with_noise = self.target_position + noise

        return self.current_position.lerp(target_with_noise, min(1.0, t))

    def _organic_noise(self, dt: float) -> Position:
        """Generate organic-feeling noise for natural movement."""
        # Perlin-like noise via sin combination
        self._noise_seed += dt
        t = self._noise_seed

        # Low-frequency wobble
        x = math.sin(t * 0.7) * 2 + math.sin(t * 1.3) * 1
        y = math.sin(t * 0.5) * 2 + math.sin(t * 1.1) * 1

        return Position(x, y)

    def should_suggest(self, dt: float) -> bool:
        """
        Check if this behavior should make a suggestion now.

        Uses probability from behavior, respects cooldown.
        """
        if self.suggestion_cooldown > 0:
            return False

        probability = self.behavior.suggestion_probability
        if random.random() < probability * dt:
            self.suggestion_cooldown = 5.0  # 5 second cooldown
            return True

        return False

    def suggest_state(self) -> CursorState:
        """Get preferred cursor state for this behavior."""
        preferred = self.behavior.preferred_states
        if preferred:
            return random.choice(list(preferred))
        return CursorState.WAITING


# =============================================================================
# Behavior Modulator: Layer behaviors
# =============================================================================


@dataclass
class BehaviorModulator:
    """
    Modulates behavior based on context.

    Behaviors aren't fixed—they shift based on:
    - Time of day (circadian)
    - Human activity patterns
    - Task context

    Heterarchical principle: No fixed hierarchy.
    A FOLLOWER can become leader. An AUTONOMOUS
    can choose to follow.
    """

    base_behavior: CursorBehavior

    # Modulation weights (0.0-1.0)
    human_activity_weight: float = 0.3
    task_urgency_weight: float = 0.2
    circadian_weight: float = 0.2

    def get_effective_behavior(
        self,
        human_focus: HumanFocusTracker,
        task_urgency: float = 0.5,
        phase: CircadianPhase | None = None,
    ) -> CursorBehavior:
        """
        Compute effective behavior given current context.

        May return a different behavior than base if
        context strongly suggests it.
        """
        if phase is None:
            phase = CircadianPhase.current()

        # Calculate modulation signals
        human_stationary = human_focus.is_stationary
        focus_duration = human_focus.focus_duration

        # Human has been focused a long time → ASSISTANT might help
        if focus_duration > 60 and self.base_behavior == CursorBehavior.FOLLOWER:
            if random.random() < self.human_activity_weight:
                return CursorBehavior.ASSISTANT

        # Human is moving fast → FOLLOWER should keep up
        if not human_stationary and self.base_behavior == CursorBehavior.EXPLORER:
            if random.random() < self.human_activity_weight:
                return CursorBehavior.FOLLOWER

        # Night time → more contemplative behaviors
        if phase in (CircadianPhase.NIGHT, CircadianPhase.EVENING):
            if self.base_behavior == CursorBehavior.AUTONOMOUS:
                if random.random() < self.circadian_weight:
                    return CursorBehavior.EXPLORER  # Slower, more wandering

        # High urgency → AUTONOMOUS takes action
        if task_urgency > 0.8:
            if self.base_behavior in (CursorBehavior.FOLLOWER, CursorBehavior.EXPLORER):
                if random.random() < self.task_urgency_weight:
                    return CursorBehavior.AUTONOMOUS

        return self.base_behavior


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Core enum
    "CursorBehavior",
    # Position types
    "Position",
    "FocusPoint",
    # Focus tracking
    "HumanFocusTracker",
    # Graph protocol
    "AGENTESEGraph",
    # Animation
    "BehaviorAnimator",
    "BehaviorModulator",
]
