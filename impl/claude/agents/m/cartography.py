"""
M-gent Holographic Cartography.

From Memory-as-Retrieval to Memory-as-Orientation.

The core question: "What is the most perfect context injection for any given turn?"
The answer: Not a search result—a *map* that shows position, adjacency, and horizon.

Phase 1: Core Data Structures
- HoloMap: Fuzzy isomorphism of agent knowledge state
- Attractor: Dense memory cluster (landmark)
- WeightedEdge: Desire line between landmarks
- Horizon: Progressive disclosure boundary
- Void: Unexplored region ("Here be dragons")

Integrations:
- L-gent: Provides embedding space (terrain)
- N-gent: Provides SemanticTraces (desire lines)
- O-gent: Provides health annotations
- B-gent: Constrains resolution via token budget
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

# ============================================================================
# Core Types
# ============================================================================


class Resolution(Enum):
    """Map resolution levels."""

    HIGH = "high"  # Full detail, high token cost
    MEDIUM = "medium"  # Balanced detail/cost
    LOW = "low"  # Summaries only, low cost
    ADAPTIVE = "adaptive"  # Auto-adjust based on budget


@dataclass
class ContextVector:
    """
    The "You are here" marker.

    Represents current position in semantic space.
    """

    embedding: list[float]
    label: str = ""  # Human-readable description
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return len(self.embedding)

    def distance_to(self, other: ContextVector) -> float:
        """Euclidean distance to another vector."""
        if len(self.embedding) != len(other.embedding):
            raise ValueError("Embedding dimensions must match")
        return math.sqrt(
            sum((a - b) ** 2 for a, b in zip(self.embedding, other.embedding))
        )

    def cosine_similarity(self, other: ContextVector) -> float:
        """Cosine similarity to another vector."""
        if len(self.embedding) != len(other.embedding):
            raise ValueError("Embedding dimensions must match")

        dot = sum(a * b for a, b in zip(self.embedding, other.embedding))
        norm_a = math.sqrt(sum(a * a for a in self.embedding))
        norm_b = math.sqrt(sum(b * b for b in other.embedding))

        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


@dataclass
class Attractor:
    """
    A landmark in the HoloMap—a dense cluster of memories.

    Like a city on a real map: a point of interest that draws attention.
    Named "Attractor" from dynamical systems theory.
    """

    id: str
    centroid: list[float]  # Embedding center
    members: list[str]  # Member memory IDs
    label: str  # Human-readable name
    density: float  # How concentrated (higher = tighter cluster)

    # Statistics
    member_count: int = 0  # Explicit count for efficiency
    variance: float = 0.0  # Spread of members around centroid

    # O-gent annotations (optional)
    semantic_drift: float | None = None  # Drift since last observation
    last_visited: datetime | None = None  # Last access time
    visit_count: int = 0  # Total visits

    # Additional metadata
    artifact_type: str | None = None  # Type of artifacts in cluster
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.member_count == 0:
            self.member_count = len(self.members)

    @property
    def is_hot(self) -> bool:
        """High visit count indicates frequently accessed landmark."""
        return self.visit_count > 10

    @property
    def is_drifting(self) -> bool:
        """Check if semantic drift exceeds threshold."""
        if self.semantic_drift is None:
            return False
        return self.semantic_drift > 0.2

    def distance_to(self, embedding: list[float]) -> float:
        """Euclidean distance from centroid to a point."""
        if len(self.centroid) != len(embedding):
            raise ValueError("Embedding dimensions must match")
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(self.centroid, embedding)))


@dataclass
class WeightedEdge:
    """
    A desire line between landmarks.

    Named for urban planning concept: paths people naturally walk,
    regardless of designed sidewalks.
    """

    source: str  # Landmark ID
    target: str  # Landmark ID
    weight: float  # Transition probability [0, 1]

    # Direction
    bidirectional: bool = True  # True if traffic flows both ways

    # N-gent provenance
    trace_ids: list[str] = field(default_factory=list)  # For audit trail
    transition_count: int = 0  # Raw count of transitions

    # O-gent annotations (optional)
    latency_p95: float | None = None  # 95th percentile latency on this path
    error_rate: float | None = None  # Error rate on this path
    last_traversed: datetime | None = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_well_trodden(self) -> bool:
        """High-traffic path."""
        return self.transition_count > 20 or self.weight > 0.5

    @property
    def is_reliable(self) -> bool:
        """Path with low error rate."""
        if self.error_rate is None:
            return True  # Unknown = assume OK
        return self.error_rate < 0.1

    def cost(self) -> float:
        """
        Cost to traverse this edge.

        Lower weight = higher cost (inverse relationship).
        We want to follow high-traffic paths.
        """
        if self.weight <= 0:
            return float("inf")
        return 1.0 / self.weight


@dataclass
class Region:
    """A region in semantic space."""

    id: str
    center: list[float]  # Center embedding
    radius: float  # Size of region
    label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def contains(self, embedding: list[float]) -> bool:
        """Check if a point is within this region."""
        if len(self.center) != len(embedding):
            return False
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(self.center, embedding)))
        return distance <= self.radius


@dataclass
class Void:
    """
    An unexplored region in semantic space.

    "Here be dragons" - areas where we have little data.
    """

    id: str
    region: Region
    uncertainty: float = 1.0  # 0.0 = known, 1.0 = completely unknown

    # Why is this a void?
    reason: str = "sparse_data"  # sparse_data, never_visited, high_error

    # Metadata
    last_probed: datetime | None = None  # Last exploration attempt
    probe_count: int = 0  # How many times we've tried to explore

    @property
    def is_dangerous(self) -> bool:
        """Voids with high uncertainty after many probes are dangerous."""
        return self.uncertainty > 0.8 and self.probe_count > 3


@dataclass
class Horizon:
    """
    The boundary of progressive disclosure.

    Like human foveal vision: high resolution at center, blur at periphery.
    """

    center: list[float]  # Origin embedding
    inner_radius: float  # Full detail zone
    outer_radius: float  # Blur zone boundary

    # Budget constraint
    max_tokens: int = 4000  # Token budget for this horizon
    used_tokens: int = 0

    def resolution_at(self, distance: float) -> float:
        """
        Resolution falls off with distance from center.

        Returns:
            1.0 = full detail (within inner_radius)
            0.0-1.0 = partial detail (in blur zone)
            0.0 = beyond horizon
        """
        if distance <= self.inner_radius:
            return 1.0
        elif distance <= self.outer_radius:
            # Linear falloff in blur zone
            blur_range = self.outer_radius - self.inner_radius
            if blur_range == 0:
                return 0.0
            return 1.0 - (distance - self.inner_radius) / blur_range
        else:
            return 0.0  # Beyond horizon

    def resolution_at_point(self, embedding: list[float]) -> float:
        """Get resolution for a specific embedding."""
        if len(self.center) != len(embedding):
            return 0.0
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(self.center, embedding)))
        return self.resolution_at(distance)

    @property
    def remaining_tokens(self) -> int:
        """Tokens remaining in budget."""
        return max(0, self.max_tokens - self.used_tokens)

    def spend_tokens(self, amount: int) -> bool:
        """
        Spend tokens from budget.

        Returns True if successful, False if insufficient budget.
        """
        if amount > self.remaining_tokens:
            return False
        self.used_tokens += amount
        return True

    @classmethod
    def from_budget(
        cls,
        center: list[float],
        token_budget: int,
        base_radius: float = 0.5,
    ) -> Horizon:
        """
        Create horizon scaled by token budget.

        More tokens = wider horizon.
        """
        # Scale factor: sqrt to avoid runaway at high budgets
        scale = math.sqrt(token_budget / 1000)  # 1000 tokens = scale 1.0
        return cls(
            center=center,
            inner_radius=base_radius * scale * 0.3,  # 30% of radius is focal
            outer_radius=base_radius * scale,
            max_tokens=token_budget,
        )


# ============================================================================
# HoloMap: The Complete Map
# ============================================================================


@dataclass
class HoloMap:
    """
    A fuzzy isomorphism of the agent's knowledge state.

    Properties:
    - Topological: Preserves connectivity, not distance.
    - Foveated: High resolution at center (origin), low at edges.
    - Probabilistic: Edges represent transition probabilities.

    This is the answer to: "What does the agent's semantic neighborhood look like?"
    """

    origin: ContextVector  # "You are here"

    # LANDMARKS: Clusters of memories that form coherent concepts
    landmarks: list[Attractor]

    # DESIRE LINES: Historical paths between landmarks
    desire_lines: list[WeightedEdge]

    # VOIDS: Unexplored regions
    voids: list[Void]

    # HORIZON: The fovea boundary
    horizon: Horizon

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    resolution: Resolution = Resolution.ADAPTIVE
    metadata: dict[str, Any] = field(default_factory=dict)

    # Internal indices (built lazily)
    _landmark_index: dict[str, Attractor] = field(default_factory=dict, repr=False)
    _edge_index: dict[str, list[WeightedEdge]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """Build indices for efficient lookup."""
        self._build_indices()

    def _build_indices(self) -> None:
        """Build internal indices."""
        self._landmark_index = {l.id: l for l in self.landmarks}
        self._edge_index = {}
        for edge in self.desire_lines:
            if edge.source not in self._edge_index:
                self._edge_index[edge.source] = []
            self._edge_index[edge.source].append(edge)
            if edge.bidirectional:
                if edge.target not in self._edge_index:
                    self._edge_index[edge.target] = []
                # Create reverse edge
                reverse = WeightedEdge(
                    source=edge.target,
                    target=edge.source,
                    weight=edge.weight,
                    bidirectional=True,
                    trace_ids=edge.trace_ids,
                    transition_count=edge.transition_count,
                )
                self._edge_index[edge.target].append(reverse)

    # ───────────────────────────────────────────────
    # LOOKUP METHODS
    # ───────────────────────────────────────────────

    def get_landmark(self, landmark_id: str) -> Attractor | None:
        """Get a landmark by ID."""
        return self._landmark_index.get(landmark_id)

    def nearest_landmark(self, point: ContextVector | list[float]) -> Attractor | None:
        """Find the nearest landmark to a point."""
        if not self.landmarks:
            return None

        embedding = point.embedding if isinstance(point, ContextVector) else point
        return min(
            self.landmarks,
            key=lambda l: l.distance_to(embedding),
        )

    def landmarks_within(
        self, point: ContextVector | list[float], radius: float
    ) -> list[Attractor]:
        """Find all landmarks within radius of a point."""
        embedding = point.embedding if isinstance(point, ContextVector) else point
        return [l for l in self.landmarks if l.distance_to(embedding) <= radius]

    def edges_from(self, landmark_id: str) -> list[WeightedEdge]:
        """Get all edges originating from a landmark."""
        return self._edge_index.get(landmark_id, [])

    # ───────────────────────────────────────────────
    # NAVIGATION METHODS
    # ───────────────────────────────────────────────

    def has_path(
        self,
        from_point: ContextVector | list[float],
        to_point: ContextVector | list[float],
    ) -> bool:
        """Check if a desire-line path exists between two points."""
        from_landmark = self.nearest_landmark(from_point)
        to_landmark = self.nearest_landmark(to_point)

        if not from_landmark or not to_landmark:
            return False
        if from_landmark.id == to_landmark.id:
            return True

        # BFS to check connectivity
        visited = set()
        queue = [from_landmark.id]

        while queue:
            current = queue.pop(0)
            if current == to_landmark.id:
                return True
            if current in visited:
                continue
            visited.add(current)

            for edge in self.edges_from(current):
                if edge.target not in visited:
                    queue.append(edge.target)

        return False

    def get_paved_path(
        self,
        from_point: ContextVector | list[float],
        to_point: ContextVector | list[float],
    ) -> list[Attractor]:
        """
        Return the desire-line path (most-traveled path).

        This is NOT shortest path—it's the historical "beaten path".
        """
        from_landmark = self.nearest_landmark(from_point)
        to_landmark = self.nearest_landmark(to_point)

        if not from_landmark or not to_landmark:
            return []
        if from_landmark.id == to_landmark.id:
            return [from_landmark]

        # Dijkstra with edge cost = 1/weight (prefer high-traffic paths)
        return self._dijkstra(from_landmark.id, to_landmark.id)

    def _dijkstra(self, start_id: str, end_id: str) -> list[Attractor]:
        """
        Dijkstra's algorithm using desire line weights.

        Cost = 1/weight, so high-traffic paths are preferred.
        """
        if start_id not in self._landmark_index:
            return []
        if end_id not in self._landmark_index:
            return []

        # Priority queue: (cost, current_id, path)
        pq = [(0.0, start_id, [start_id])]
        visited = set()

        while pq:
            cost, current, path = heapq.heappop(pq)

            if current in visited:
                continue
            visited.add(current)

            if current == end_id:
                return [self._landmark_index[lid] for lid in path]

            for edge in self.edges_from(current):
                if edge.target not in visited:
                    new_cost = cost + edge.cost()
                    new_path = path + [edge.target]
                    heapq.heappush(pq, (new_cost, edge.target, new_path))

        return []  # No path found

    def adjacent_to(self, point: ContextVector | list[float]) -> list[Attractor]:
        """Get landmarks immediately adjacent to a point."""
        landmark = self.nearest_landmark(point)
        if not landmark:
            return []

        adjacent_ids = set()
        for edge in self.edges_from(landmark.id):
            adjacent_ids.add(edge.target)

        return [
            self._landmark_index[lid]
            for lid in adjacent_ids
            if lid in self._landmark_index
        ]

    # ───────────────────────────────────────────────
    # VOID METHODS
    # ───────────────────────────────────────────────

    def is_in_void(self, point: ContextVector | list[float]) -> bool:
        """Check if a point is in a void region."""
        embedding = point.embedding if isinstance(point, ContextVector) else point
        return any(v.region.contains(embedding) for v in self.voids)

    def get_void_at(self, point: ContextVector | list[float]) -> Void | None:
        """Get the void containing a point, if any."""
        embedding = point.embedding if isinstance(point, ContextVector) else point
        for void in self.voids:
            if void.region.contains(embedding):
                return void
        return None

    # ───────────────────────────────────────────────
    # RESOLUTION METHODS
    # ───────────────────────────────────────────────

    def resolution_at(self, point: ContextVector | list[float]) -> float:
        """Get resolution at a point based on horizon."""
        embedding = point.embedding if isinstance(point, ContextVector) else point
        return self.horizon.resolution_at_point(embedding)

    def get_focal_landmarks(self, threshold: float = 0.7) -> list[Attractor]:
        """Get landmarks in the focal zone (high resolution)."""
        return [
            l
            for l in self.landmarks
            if self.horizon.resolution_at_point(l.centroid) >= threshold
        ]

    def get_peripheral_landmarks(
        self, low: float = 0.1, high: float = 0.7
    ) -> list[Attractor]:
        """Get landmarks in the blur zone."""
        return [
            l
            for l in self.landmarks
            if low <= self.horizon.resolution_at_point(l.centroid) < high
        ]

    # ───────────────────────────────────────────────
    # STATISTICS
    # ───────────────────────────────────────────────

    @property
    def landmark_count(self) -> int:
        """Number of landmarks."""
        return len(self.landmarks)

    @property
    def edge_count(self) -> int:
        """Number of desire lines."""
        return len(self.desire_lines)

    @property
    def void_count(self) -> int:
        """Number of voids."""
        return len(self.voids)

    @property
    def coverage(self) -> float:
        """
        Estimate of how much semantic space is covered.

        Based on landmark count and horizon size.
        """
        if not self.landmarks:
            return 0.0
        # Rough estimate: each landmark covers a unit sphere
        covered = sum(1.0 / (1.0 + l.variance) for l in self.landmarks)
        total = self.horizon.outer_radius**2 * math.pi
        if total == 0:
            return 0.0
        return min(1.0, covered / total)


# ============================================================================
# Navigation Types
# ============================================================================


@dataclass
class NavigationPlan:
    """A plan for getting from here to there."""

    waypoints: list[Attractor]  # Landmarks to pass through
    confidence: float  # Based on desire line strength
    mode: str  # "desire_line" | "exploration"
    warning: str | None = None
    total_cost: float = 0.0  # Accumulated path cost

    @property
    def is_safe(self) -> bool:
        """High-confidence navigation."""
        return self.confidence > 0.5 and self.mode == "desire_line"

    @property
    def length(self) -> int:
        """Number of waypoints."""
        return len(self.waypoints)


@dataclass
class Goal:
    """A navigation goal."""

    current_context: ContextVector
    target: ContextVector | list[float]  # Where we want to go
    urgency: float = 0.5  # 0.0 = leisurely, 1.0 = urgent
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Context Injection Types
# ============================================================================


@dataclass
class FoveatedView:
    """
    A foveated rendering of the semantic space.

    Like human vision: sharp in center, blurry at edges.
    """

    # Full detail (within inner radius)
    focal_zone: list[tuple[Attractor, float]]  # (landmark, resolution)

    # Partial detail (blur zone)
    blur_zone: list[tuple[Attractor, float]]  # (landmark, resolution)

    # Budget accounting
    tokens_used: int = 0


@dataclass
class InjectionRequest:
    """Request for optimal context injection."""

    current_context: ContextVector
    goal: ContextVector | None = None  # Optional goal
    budget_tokens: int = 4000  # Token budget
    include_voids: bool = True  # Warn about unexplored regions
    include_paths: bool = True  # Show desire lines


@dataclass
class OptimalContext:
    """
    The answer to: "What is the most perfect context injection?"

    A foveated, budget-constrained view of semantic space.
    """

    # Position marker
    position: str  # "You are here" description

    # High-detail memories for current + goal landmarks
    focal_memories: list[str]

    # Blurred summaries of peripheral landmarks
    peripheral_summaries: list[str]

    # Navigation hints
    desire_lines: list[str]  # "Error → Retry (80%)"

    # Warnings about voids
    void_warnings: list[str]

    # Budget accounting
    tokens_used: int
    tokens_remaining: int

    def to_context_string(self) -> str:
        """Render to a context string for injection."""
        parts = []

        # Position
        parts.append(f"## Current Position\n{self.position}")

        # Focal memories
        if self.focal_memories:
            parts.append("## Relevant Context (High Detail)")
            parts.extend(self.focal_memories)

        # Peripheral
        if self.peripheral_summaries:
            parts.append("## Adjacent Topics (Summary)")
            parts.extend(self.peripheral_summaries)

        # Navigation
        if self.desire_lines:
            parts.append("## Common Transitions")
            parts.extend(self.desire_lines)

        # Warnings
        if self.void_warnings:
            parts.append("## Caution")
            parts.extend(self.void_warnings)

        return "\n\n".join(parts)


# ============================================================================
# Protocols for Integration
# ============================================================================


@runtime_checkable
class TraceProvider(Protocol):
    """
    Protocol for N-gent trace retrieval.

    The Cartographer needs access to trace history to compute desire lines.
    """

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """Query traces."""
        ...

    def count(self) -> int:
        """Count total traces."""
        ...


@runtime_checkable
class SemanticBackend(Protocol):
    """
    Protocol for L-gent semantic search.

    The Cartographer needs similarity search to find landmarks.
    """

    async def find(
        self,
        embedding: list[float],
        threshold: float = 0.5,
        limit: int = 100,
    ) -> list[tuple[Any, float]]:
        """Find similar items."""
        ...

    async def similarity(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:
        """Compute similarity between embeddings."""
        ...


# ============================================================================
# Factory Functions
# ============================================================================


def create_empty_holomap(
    origin: ContextVector,
    budget_tokens: int = 4000,
) -> HoloMap:
    """Create an empty HoloMap centered on origin."""
    return HoloMap(
        origin=origin,
        landmarks=[],
        desire_lines=[],
        voids=[],
        horizon=Horizon.from_budget(
            center=origin.embedding,
            token_budget=budget_tokens,
        ),
    )


def create_context_vector(
    embedding: list[float],
    label: str = "",
) -> ContextVector:
    """Create a ContextVector."""
    return ContextVector(embedding=embedding, label=label)


def create_attractor(
    id: str,
    centroid: list[float],
    label: str,
    members: list[str] | None = None,
    density: float = 1.0,
) -> Attractor:
    """Create an Attractor landmark."""
    return Attractor(
        id=id,
        centroid=centroid,
        label=label,
        members=members or [],
        density=density,
    )


def create_desire_line(
    source: str,
    target: str,
    weight: float,
    bidirectional: bool = True,
) -> WeightedEdge:
    """Create a desire line edge."""
    return WeightedEdge(
        source=source,
        target=target,
        weight=weight,
        bidirectional=bidirectional,
    )
