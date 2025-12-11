"""
Stigmergic Field: The core substrate for I-gent visualization.

The field is a 2D grid where entities move, leave traces, and coordinate
through environmental signals (pheromones) rather than direct communication.

Key concepts:
- Entities have positions and phases
- Tasks create gravity wells
- Contradictions create repulsion
- Pheromones decay over time
- Field state emerges from simple rules

See: spec/i-gents/README.md
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .types import Phase


class EntityType(Enum):
    """Types of entities that can exist on the field."""

    # Bootstrap agents (from spec/bootstrap.md)
    ID = "I"  # Identity morphism
    COMPOSE = "C"  # Function composition
    GROUND = "G"  # Reality grounding
    JUDGE = "J"  # Principle evaluation
    CONTRADICT = "X"  # Tension detection
    SUBLATE = "S"  # Synthesis engine
    FIX = "F"  # Convergence iterator

    # Task attractors
    TASK = "*"  # Active task (gravity center)
    HYPOTHESIS = "◊"  # Testable idea
    ARTIFACT = "□"  # Produced output

    @property
    def symbol(self) -> str:
        """Single-character symbol for rendering."""
        return self.value

    @property
    def is_agent(self) -> bool:
        """True if this is a bootstrap agent."""
        return self in (
            EntityType.ID,
            EntityType.COMPOSE,
            EntityType.GROUND,
            EntityType.JUDGE,
            EntityType.CONTRADICT,
            EntityType.SUBLATE,
            EntityType.FIX,
        )

    @property
    def is_attractor(self) -> bool:
        """True if this creates gravity."""
        return self in (EntityType.TASK, EntityType.HYPOTHESIS, EntityType.ARTIFACT)


class DialecticPhase(Enum):
    """System-wide dialectic phases."""

    DORMANT = "dormant"  # No activity
    FLUX = "flux"  # Normal processing
    TENSION = "tension"  # Contradiction detected
    SUBLATE = "sublate"  # Synthesis in progress
    FIX = "fix"  # Stabilization
    COOLING = "cooling"  # Heat dissipation


class PheromoneType(Enum):
    """Types of invisible environmental traces."""

    PROGRESS = "progress"  # Attracts similar agents
    CONFLICT = "conflict"  # Repels all agents
    SYNTHESIS = "synthesis"  # Strengthens composition
    ERROR = "error"  # Creates void zone

    @property
    def decay_rate(self) -> int:
        """Ticks until complete decay."""
        return {
            PheromoneType.PROGRESS: 5,
            PheromoneType.CONFLICT: 2,
            PheromoneType.SYNTHESIS: 3,
            PheromoneType.ERROR: 1,  # Instant clear
        }[self]


@dataclass
class Entity:
    """An entity on the stigmergic field."""

    id: str
    entity_type: EntityType
    x: int
    y: int
    phase: Phase = Phase.ACTIVE
    velocity_x: int = 0
    velocity_y: int = 0
    heat: float = 0.0
    birth_time: datetime = dataclass_field(default_factory=datetime.now)
    metadata: dict[str, Any] = dataclass_field(default_factory=dict)

    @property
    def symbol(self) -> str:
        """Render symbol."""
        return self.entity_type.symbol

    @property
    def position(self) -> tuple[int, int]:
        """Current position."""
        return (self.x, self.y)

    def distance_to(self, other: Entity) -> float:
        """Euclidean distance to another entity."""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def move(self, dx: int, dy: int, bounds: tuple[int, int]) -> None:
        """Move by delta, respecting bounds."""
        max_x, max_y = bounds
        self.x = max(0, min(max_x - 1, self.x + dx))
        self.y = max(0, min(max_y - 1, self.y + dy))


@dataclass
class Pheromone:
    """An invisible trace on the field."""

    ptype: PheromoneType
    x: int
    y: int
    intensity: float  # 0.0 - 1.0
    source_entity: Optional[str] = None
    birth_tick: int = 0

    def decay(self, current_tick: int) -> float:
        """Calculate current intensity after decay."""
        age = current_tick - self.birth_tick
        decay_rate = self.ptype.decay_rate
        if age >= decay_rate:
            return 0.0
        return self.intensity * (1.0 - age / decay_rate)


@dataclass
class FieldState:
    """
    Complete state of the stigmergic field.

    This is the core data structure that the renderer reads from
    and the simulation writes to.
    """

    # Field dimensions
    width: int
    height: int

    # Entities on the field
    entities: dict[str, Entity] = dataclass_field(default_factory=dict)

    # Pheromone traces
    pheromones: list[Pheromone] = dataclass_field(default_factory=list)

    # Global metrics
    entropy: float = 50.0  # 0-100, generative potential
    heat: float = 0.0  # 0-100, processing intensity
    dialectic_phase: DialecticPhase = DialecticPhase.DORMANT

    # Simulation time
    tick: int = 0
    start_time: datetime = dataclass_field(default_factory=datetime.now)

    # Focus (selected entity)
    focus: Optional[str] = None

    # Event log (compost heap)
    events: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the field."""
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id: str) -> Optional[Entity]:
        """Remove an entity from the field."""
        return self.entities.pop(entity_id, None)

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def emit_pheromone(
        self,
        ptype: PheromoneType,
        x: int,
        y: int,
        intensity: float = 1.0,
        source: Optional[str] = None,
    ) -> Pheromone:
        """Emit a pheromone at a location."""
        p = Pheromone(
            ptype=ptype,
            x=x,
            y=y,
            intensity=intensity,
            source_entity=source,
            birth_tick=self.tick,
        )
        self.pheromones.append(p)
        return p

    def get_pheromones_at(self, x: int, y: int) -> list[Pheromone]:
        """Get all active pheromones at a location."""
        return [
            p
            for p in self.pheromones
            if p.x == x and p.y == y and p.decay(self.tick) > 0
        ]

    def decay_pheromones(self) -> int:
        """Remove fully decayed pheromones. Returns count removed."""
        before = len(self.pheromones)
        self.pheromones = [p for p in self.pheromones if p.decay(self.tick) > 0]
        return before - len(self.pheromones)

    def log_event(
        self,
        event_type: str,
        source: str,
        message: str,
        level: str = "info",
    ) -> None:
        """Add an event to the compost heap."""
        self.events.append(
            {
                "tick": self.tick,
                "time": datetime.now().isoformat(),
                "type": event_type,
                "source": source,
                "message": message,
                "level": level,
            }
        )
        # Keep only last 100 events
        if len(self.events) > 100:
            self.events = self.events[-100:]

    def get_recent_events(self, count: int = 10) -> list[dict[str, Any]]:
        """Get most recent events."""
        return self.events[-count:]

    def entities_at(self, x: int, y: int) -> list[Entity]:
        """Get all entities at a position."""
        return [e for e in self.entities.values() if e.x == x and e.y == y]

    def get_attractors(self) -> list[Entity]:
        """Get all task attractors."""
        return [e for e in self.entities.values() if e.entity_type.is_attractor]

    def get_agents(self) -> list[Entity]:
        """Get all bootstrap agents."""
        return [e for e in self.entities.values() if e.entity_type.is_agent]


class FieldSimulator:
    """
    Simulation engine for the stigmergic field.

    Applies the dynamics from spec/i-gents/README.md:
    - Brownian motion (jitter)
    - Context gravity (task attraction)
    - Tension repulsion (conflict avoidance)
    - Heat accumulation
    - Entropy decay
    """

    def __init__(
        self,
        state: FieldState,
        brownian_probability: float = 0.4,
        gravity_probability: float = 0.2,
        heat_generation: float = 0.3,
        entropy_decay: float = 0.1,
    ):
        self.state = state
        self.brownian_probability = brownian_probability
        self.gravity_probability = gravity_probability
        self.heat_generation = heat_generation
        self.entropy_decay = entropy_decay
        self._paused = False

    def pause(self) -> None:
        """Pause simulation."""
        self._paused = True

    def resume(self) -> None:
        """Resume simulation."""
        self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    def tick(self) -> None:
        """Advance simulation by one tick."""
        if self._paused:
            return

        self.state.tick += 1

        # Apply dynamics to each agent
        for entity in self.state.get_agents():
            dx, dy = self._calculate_movement(entity)
            entity.move(dx, dy, (self.state.width, self.state.height))

            # Heat accumulation
            if entity.phase == Phase.ACTIVE:
                entity.heat += self.heat_generation
                self.state.heat += self.heat_generation * 0.1

        # Decay pheromones
        removed = self.state.decay_pheromones()
        if removed > 0:
            self.state.log_event("decay", "field", f"Decayed {removed} pheromones")

        # Entropy decay
        self.state.entropy = max(0, self.state.entropy - self.entropy_decay)

        # Update dialectic phase
        self._update_dialectic_phase()

        # Check for cooling
        if self.state.heat > 90:
            self._trigger_cooling()

    def _calculate_movement(self, entity: Entity) -> tuple[int, int]:
        """Calculate movement delta for an entity."""
        dx, dy = 0, 0

        # Brownian motion (jitter)
        if random.random() < self.brownian_probability:
            dx += random.choice([-1, 0, 1])
            dy += random.choice([-1, 0, 1])

        # Context gravity (task attraction)
        for attractor in self.state.get_attractors():
            dist = entity.distance_to(attractor)
            if dist > 0 and random.random() < self.gravity_probability:
                dx += self._sign(attractor.x - entity.x)
                dy += self._sign(attractor.y - entity.y)

        # Tension repulsion (conflict avoidance)
        for other in self.state.get_agents():
            if other.id != entity.id and self._is_contradicting(entity, other):
                dx -= self._sign(other.x - entity.x)
                dy -= self._sign(other.y - entity.y)

        # Pheromone response
        for p in self.state.get_pheromones_at(entity.x, entity.y):
            if p.ptype == PheromoneType.CONFLICT:
                # Flee from conflict
                dx += random.choice([-1, 1])
                dy += random.choice([-1, 1])

        return (dx, dy)

    def _is_contradicting(self, a: Entity, b: Entity) -> bool:
        """Check if two entities are in tension."""
        # Judge and Contradict are always in tension
        contradicting_pairs = {
            (EntityType.JUDGE, EntityType.CONTRADICT),
            (EntityType.CONTRADICT, EntityType.JUDGE),
        }
        return (a.entity_type, b.entity_type) in contradicting_pairs

    def _sign(self, n: int) -> int:
        """Sign function."""
        if n > 0:
            return 1
        elif n < 0:
            return -1
        return 0

    def _update_dialectic_phase(self) -> None:
        """Update system-wide dialectic phase based on entity states."""
        agents = self.state.get_agents()
        if not agents:
            self.state.dialectic_phase = DialecticPhase.DORMANT
            return

        active_count = sum(1 for e in agents if e.phase == Phase.ACTIVE)
        len(agents)

        # Check for contradictions
        has_contradiction = any(
            e.entity_type == EntityType.CONTRADICT and e.phase == Phase.ACTIVE
            for e in agents
        )
        has_synthesis = any(
            e.entity_type == EntityType.SUBLATE and e.phase == Phase.ACTIVE
            for e in agents
        )
        has_fix = any(
            e.entity_type == EntityType.FIX and e.phase == Phase.ACTIVE for e in agents
        )

        if has_synthesis:
            self.state.dialectic_phase = DialecticPhase.SUBLATE
        elif has_contradiction:
            self.state.dialectic_phase = DialecticPhase.TENSION
        elif has_fix:
            self.state.dialectic_phase = DialecticPhase.FIX
        elif self.state.heat > 70:
            self.state.dialectic_phase = DialecticPhase.COOLING
        elif active_count > 0:
            self.state.dialectic_phase = DialecticPhase.FLUX
        else:
            self.state.dialectic_phase = DialecticPhase.DORMANT

    def _trigger_cooling(self) -> None:
        """Trigger cooling phase."""
        self.state.heat -= 25
        self.state.dialectic_phase = DialecticPhase.COOLING
        self.state.log_event("cooling", "field", "Heat threshold exceeded, cooling")

        # Slow down active agents
        for entity in self.state.get_agents():
            if entity.phase == Phase.ACTIVE:
                entity.phase = Phase.WANING

    def synthesize(self, source_ids: list[str], result: str) -> Optional[Entity]:
        """
        Perform synthesis: merge multiple entities into one.

        Returns the new synthesized entity, or None if synthesis fails.
        """
        sources = [self.state.get_entity(id) for id in source_ids]
        sources = [e for e in sources if e is not None]

        if len(sources) < 2:
            return None

        # Calculate synthesis position (centroid)
        cx = sum(e.x for e in sources) // len(sources)
        cy = sum(e.y for e in sources) // len(sources)

        # Create synthesized entity
        synthesized = Entity(
            id=result,
            entity_type=EntityType.ARTIFACT,
            x=cx,
            y=cy,
            phase=Phase.ACTIVE,
        )
        self.state.add_entity(synthesized)

        # Emit synthesis pheromone
        self.state.emit_pheromone(PheromoneType.SYNTHESIS, cx, cy, 1.0, result)

        # Add entropy from synthesis
        self.state.entropy = min(100, self.state.entropy + 15)

        self.state.log_event(
            "synthesis",
            "sublate",
            f"Synthesized {source_ids} → {result}",
            level="success",
        )

        return synthesized


def create_default_field(width: int = 60, height: int = 20) -> FieldState:
    """Create a field with default bootstrap agents."""
    state = FieldState(width=width, height=height)

    # Add bootstrap agents at random positions
    agents = [
        (EntityType.ID, "id"),
        (EntityType.COMPOSE, "compose"),
        (EntityType.GROUND, "ground"),
        (EntityType.JUDGE, "judge"),
        (EntityType.CONTRADICT, "contradict"),
        (EntityType.SUBLATE, "sublate"),
        (EntityType.FIX, "fix"),
    ]

    for etype, eid in agents:
        entity = Entity(
            id=eid,
            entity_type=etype,
            x=random.randint(5, width - 5),
            y=random.randint(2, height - 2),
            phase=Phase.ACTIVE,
        )
        state.add_entity(entity)

    state.log_event(
        "init", "field", f"Created field with {len(agents)} bootstrap agents"
    )
    state.dialectic_phase = DialecticPhase.FLUX

    return state


def create_demo_field() -> FieldState:
    """Create a demo field with some tasks and activity."""
    state = create_default_field()

    # Add a task attractor
    task = Entity(
        id="main-task",
        entity_type=EntityType.TASK,
        x=state.width // 2,
        y=state.height // 2,
        phase=Phase.ACTIVE,
    )
    state.add_entity(task)

    # Add a hypothesis
    hypo = Entity(
        id="hypothesis-1",
        entity_type=EntityType.HYPOTHESIS,
        x=state.width // 3,
        y=state.height // 3,
        phase=Phase.ACTIVE,
    )
    state.add_entity(hypo)

    state.entropy = 72
    state.heat = 35
    state.focus = "judge"

    state.log_event("demo", "system", "Demo field initialized")

    return state
