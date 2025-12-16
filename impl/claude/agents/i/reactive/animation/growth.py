"""
Differential Growth Engine: Organic form emergence.

Differential growth produces organic patterns through local interactions.
Instead of placing elements in fixed positions, we let them grow and
adapt based on attraction, repulsion, and noise.

The rules:
- Attraction: Pull toward targets (goals, connections)
- Repulsion: Push away from neighbors (avoid crowding)
- Alignment: Follow local direction (create flow)
- Randomness: The accursed share (prevent sterility)

Applications in kgents:
- Knowledge graph edges that "grow" between nodes
- Memory crystallization (lattice formation)
- Plan progress visualization (frontier zones)
- Coalition structure emergence

Key insight: The structure is not designed—it emerges from rules.
We do not design the flower; we design the soil and the season.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterator
from uuid import uuid4

from agents.i.reactive.signal import Signal

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class GrowthRules:
    """Rules governing differential growth behavior.

    These parameters control how nodes and edges grow, interact,
    and settle into stable patterns.

    Attributes:
        attraction: Pull toward targets (0-1). Higher = faster convergence.
        repulsion: Push from neighbors (0-1). Higher = more spacing.
        alignment: Follow local direction (0-1). Higher = smoother curves.
        randomness: Accursed share injection (0-1). Higher = more organic.
        growth_rate: Base growth per step. Higher = faster growth.
        min_distance: Minimum distance between nodes.
        damping: Velocity damping (0-1). Higher = faster settling.
    """

    attraction: float = 0.3
    repulsion: float = 0.4
    alignment: float = 0.1
    randomness: float = 0.1
    growth_rate: float = 0.05
    min_distance: float = 0.1
    damping: float = 0.9

    @classmethod
    def organic(cls) -> GrowthRules:
        """Organic preset: high randomness, moderate forces."""
        return cls(attraction=0.2, repulsion=0.3, alignment=0.2, randomness=0.2)

    @classmethod
    def crystalline(cls) -> GrowthRules:
        """Crystalline preset: low randomness, strong structure."""
        return cls(attraction=0.4, repulsion=0.5, alignment=0.3, randomness=0.05)

    @classmethod
    def fluid(cls) -> GrowthRules:
        """Fluid preset: low repulsion, high alignment."""
        return cls(attraction=0.3, repulsion=0.2, alignment=0.4, randomness=0.15)


@dataclass
class GrowthNode:
    """A node in the growth simulation.

    Nodes can grow toward targets, be repelled by neighbors,
    and accumulate velocity over time.

    Attributes:
        id: Unique identifier
        position: 3D position (x, y, z)
        velocity: Current velocity vector
        target: Optional target position for attraction
        age: Age in simulation steps
        fixed: If True, node cannot move
        weight: Node importance (affects repulsion strength)
    """

    id: str
    position: tuple[float, float, float]
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
    target: tuple[float, float, float] | None = None
    age: float = 0.0
    fixed: bool = False
    weight: float = 1.0

    def distance_to(self, other: GrowthNode) -> float:
        """Calculate distance to another node."""
        dx = self.position[0] - other.position[0]
        dy = self.position[1] - other.position[1]
        dz = self.position[2] - other.position[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def distance_to_point(self, point: tuple[float, float, float]) -> float:
        """Calculate distance to a point."""
        dx = self.position[0] - point[0]
        dy = self.position[1] - point[1]
        dz = self.position[2] - point[2]
        return math.sqrt(dx * dx + dy * dy + dz * dz)


@dataclass
class GrowthEdge:
    """An edge growing between two nodes.

    Edges don't teleport into existence—they grow from source to target.
    The progress field tracks how much of the edge has "grown".

    Attributes:
        id: Unique identifier
        source_id: Source node ID
        target_id: Target node ID
        progress: Growth progress (0 = none, 1 = complete)
        waypoints: Intermediate points for organic paths
        growth_rate: Speed of growth (can vary per edge)
    """

    id: str
    source_id: str
    target_id: str
    progress: float = 0.0
    waypoints: list[tuple[float, float, float]] = field(default_factory=list)
    growth_rate: float = 1.0

    @property
    def is_complete(self) -> bool:
        """Whether the edge has fully grown."""
        return self.progress >= 1.0


@dataclass
class GrowthEngine:
    """Differential growth simulation engine.

    Manages nodes and edges, simulates growth forces, and produces
    organic structures through iterative relaxation.

    Usage:
        engine = GrowthEngine.create()
        node_a = engine.seed((0, 0, 0))
        node_b = engine.seed((1, 0, 0))
        edge = engine.connect(node_a, node_b)
        for _ in range(100):
            engine.step(0.016)
        path = engine.get_edge_path(edge)
    """

    nodes: dict[str, GrowthNode] = field(default_factory=dict)
    edges: dict[str, GrowthEdge] = field(default_factory=dict)
    rules: GrowthRules = field(default_factory=GrowthRules)
    _time: float = 0.0

    @classmethod
    def create(cls, rules: GrowthRules | None = None) -> GrowthEngine:
        """Create an empty growth engine.

        Args:
            rules: Growth rules (uses defaults if not specified)

        Returns:
            New GrowthEngine instance
        """
        return cls(
            nodes={},
            edges={},
            rules=rules or GrowthRules(),
            _time=0.0,
        )

    @property
    def time(self) -> float:
        """Current simulation time."""
        return self._time

    @property
    def node_count(self) -> int:
        """Number of nodes in the simulation."""
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        """Number of edges in the simulation."""
        return len(self.edges)

    def seed(
        self,
        position: tuple[float, float, float],
        node_id: str | None = None,
        fixed: bool = False,
        weight: float = 1.0,
    ) -> str:
        """Plant a seed node at the given position.

        Args:
            position: Initial position (x, y, z)
            node_id: Optional ID (generated if not provided)
            fixed: If True, node cannot move
            weight: Node importance

        Returns:
            Node ID
        """
        nid = node_id or str(uuid4())[:8]
        self.nodes[nid] = GrowthNode(
            id=nid,
            position=position,
            fixed=fixed,
            weight=weight,
        )
        return nid

    def remove_node(self, node_id: str) -> bool:
        """Remove a node and its connected edges.

        Args:
            node_id: Node to remove

        Returns:
            True if node was removed
        """
        if node_id not in self.nodes:
            return False

        # Remove connected edges
        edges_to_remove = [
            eid
            for eid, edge in self.edges.items()
            if edge.source_id == node_id or edge.target_id == node_id
        ]
        for eid in edges_to_remove:
            del self.edges[eid]

        del self.nodes[node_id]
        return True

    def connect(
        self,
        source_id: str,
        target_id: str,
        edge_id: str | None = None,
        growth_rate: float = 1.0,
    ) -> str:
        """Start growing an edge between two nodes.

        The edge starts with progress=0 and grows over time.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_id: Optional edge ID
            growth_rate: Speed multiplier for this edge

        Returns:
            Edge ID

        Raises:
            KeyError: If source or target node doesn't exist
        """
        if source_id not in self.nodes:
            raise KeyError(f"Source node {source_id} not found")
        if target_id not in self.nodes:
            raise KeyError(f"Target node {target_id} not found")

        eid = edge_id or str(uuid4())[:8]
        self.edges[eid] = GrowthEdge(
            id=eid,
            source_id=source_id,
            target_id=target_id,
            progress=0.0,
            growth_rate=growth_rate,
        )
        return eid

    def disconnect(self, edge_id: str) -> bool:
        """Remove an edge.

        Args:
            edge_id: Edge to remove

        Returns:
            True if edge was removed
        """
        if edge_id in self.edges:
            del self.edges[edge_id]
            return True
        return False

    def set_target(self, node_id: str, target: tuple[float, float, float]) -> None:
        """Set attraction target for a node.

        Args:
            node_id: Node to update
            target: Target position
        """
        if node_id in self.nodes:
            self.nodes[node_id].target = target

    def grow_toward(
        self,
        from_id: str,
        target: tuple[float, float, float],
        iterations: int = 10,
    ) -> None:
        """Grow a node toward a target over multiple iterations.

        This is a convenience method that sets the target and runs steps.

        Args:
            from_id: Node to grow
            target: Target position
            iterations: Number of simulation steps
        """
        self.set_target(from_id, target)
        for _ in range(iterations):
            self.step(0.016)

    def step(self, dt: float) -> None:
        """Advance simulation by one time step.

        This applies:
        1. Attraction forces (toward targets)
        2. Repulsion forces (from neighbors)
        3. Alignment forces (follow local direction)
        4. Random perturbation (accursed share)
        5. Velocity integration
        6. Edge growth

        Args:
            dt: Time delta in seconds
        """
        self._time += dt

        # Collect forces for each node
        forces: dict[str, tuple[float, float, float]] = {
            nid: (0.0, 0.0, 0.0) for nid in self.nodes
        }

        # Apply attraction toward targets
        for nid, node in self.nodes.items():
            if node.fixed or node.target is None:
                continue

            dx = node.target[0] - node.position[0]
            dy = node.target[1] - node.position[1]
            dz = node.target[2] - node.position[2]

            fx, fy, fz = forces[nid]
            forces[nid] = (
                fx + dx * self.rules.attraction,
                fy + dy * self.rules.attraction,
                fz + dz * self.rules.attraction,
            )

        # Apply repulsion from neighbors
        node_list = list(self.nodes.values())
        for i, node_a in enumerate(node_list):
            if node_a.fixed:
                continue

            for node_b in node_list[i + 1 :]:
                dist = node_a.distance_to(node_b)
                if dist < self.rules.min_distance * 3 and dist > 0.001:
                    # Repulsion force inversely proportional to distance
                    strength = self.rules.repulsion / (dist * dist + 0.01)
                    strength *= (node_a.weight + node_b.weight) / 2

                    dx = node_a.position[0] - node_b.position[0]
                    dy = node_a.position[1] - node_b.position[1]
                    dz = node_a.position[2] - node_b.position[2]

                    # Normalize
                    d = max(0.001, dist)
                    dx, dy, dz = dx / d, dy / d, dz / d

                    # Apply to A
                    fx, fy, fz = forces[node_a.id]
                    forces[node_a.id] = (
                        fx + dx * strength,
                        fy + dy * strength,
                        fz + dz * strength,
                    )

                    # Apply opposite to B (if not fixed)
                    if not node_b.fixed:
                        fx, fy, fz = forces[node_b.id]
                        forces[node_b.id] = (
                            fx - dx * strength,
                            fy - dy * strength,
                            fz - dz * strength,
                        )

        # Apply random perturbation (accursed share)
        if self.rules.randomness > 0:
            for nid, node in self.nodes.items():
                if node.fixed:
                    continue
                fx, fy, fz = forces[nid]
                forces[nid] = (
                    fx + (random.random() - 0.5) * self.rules.randomness,
                    fy + (random.random() - 0.5) * self.rules.randomness,
                    fz + (random.random() - 0.5) * self.rules.randomness,
                )

        # Integrate velocity and position
        for nid, node in self.nodes.items():
            if node.fixed:
                continue

            fx, fy, fz = forces[nid]
            vx, vy, vz = node.velocity

            # Update velocity
            vx = (vx + fx * dt) * self.rules.damping
            vy = (vy + fy * dt) * self.rules.damping
            vz = (vz + fz * dt) * self.rules.damping

            # Update position
            x, y, z = node.position
            x += vx * dt
            y += vy * dt
            z += vz * dt

            # Update node
            node.velocity = (vx, vy, vz)
            node.position = (x, y, z)
            node.age += dt

        # Grow edges
        for edge in self.edges.values():
            if not edge.is_complete:
                edge.progress = min(
                    1.0,
                    edge.progress + self.rules.growth_rate * edge.growth_rate * dt,
                )

    def relax(self, iterations: int = 50, dt: float = 0.016) -> None:
        """Let the system settle through multiple iterations.

        Args:
            iterations: Number of simulation steps
            dt: Time delta per step
        """
        for _ in range(iterations):
            self.step(dt)

    def total_kinetic_energy(self) -> float:
        """Calculate total kinetic energy of all nodes.

        Useful for detecting when system has settled.

        Returns:
            Sum of squared velocities
        """
        total = 0.0
        for node in self.nodes.values():
            vx, vy, vz = node.velocity
            total += vx * vx + vy * vy + vz * vz
        return total

    def get_edge_path(self, edge_id: str, segments: int = 10) -> list[tuple[float, float, float]]:
        """Get the current visual path for an edge.

        Returns points from source to current growth progress,
        with optional intermediate waypoints for organic appearance.

        Args:
            edge_id: Edge to get path for
            segments: Number of segments for interpolation

        Returns:
            List of 3D points representing the edge path

        Raises:
            KeyError: If edge doesn't exist
        """
        if edge_id not in self.edges:
            raise KeyError(f"Edge {edge_id} not found")

        edge = self.edges[edge_id]
        source = self.nodes.get(edge.source_id)
        target = self.nodes.get(edge.target_id)

        if source is None or target is None:
            return []

        # Interpolate from source to (source + progress * (target - source))
        sx, sy, sz = source.position
        tx, ty, tz = target.position

        # Current endpoint based on progress
        ex = sx + (tx - sx) * edge.progress
        ey = sy + (ty - sy) * edge.progress
        ez = sz + (tz - sz) * edge.progress

        # Generate path with slight organic curve
        path: list[tuple[float, float, float]] = []
        for i in range(segments + 1):
            t = i / segments

            # Linear interpolation
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            z = sz + (ez - sz) * t

            # Add slight perpendicular offset for organic feel
            # (only for middle points)
            if 0 < t < 1:
                # Use edge id hash for deterministic randomness
                seed = hash(edge_id + str(i)) % 1000 / 1000
                offset = math.sin(t * math.pi) * 0.02 * (seed - 0.5)
                # Offset perpendicular to edge direction
                dx, dy = ty - sy, -(tx - sx)  # Perpendicular in XY
                d = math.sqrt(dx * dx + dy * dy + 0.001)
                x += dx / d * offset
                y += dy / d * offset

            path.append((x, y, z))

        return path

    def get_node(self, node_id: str) -> GrowthNode | None:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> GrowthEdge | None:
        """Get an edge by ID."""
        return self.edges.get(edge_id)

    def all_nodes(self) -> Iterator[GrowthNode]:
        """Iterate over all nodes."""
        yield from self.nodes.values()

    def all_edges(self) -> Iterator[GrowthEdge]:
        """Iterate over all edges."""
        yield from self.edges.values()
