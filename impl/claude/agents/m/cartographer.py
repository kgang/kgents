"""
M-gent CartographerAgent.

Projects high-dimensional memory space into a navigable HoloMap.

Answers:
- "Where am I?" (current position)
- "What is adjacent?" (nearby landmarks)
- "Where are the cliffs?" (voids)

Critical Integrations:
- L-gent: Provides the embedding space (terrain)
- N-gent: Provides SemanticTraces (desire lines)
- O-gent: Provides health annotations
- B-gent: Constrains resolution via token budget
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable
from uuid import uuid4

from .cartography import (
    Attractor,
    ContextVector,
    Horizon,
    HoloMap,
    Region,
    Resolution,
    Void,
    WeightedEdge,
)

if TYPE_CHECKING:
    pass


# ============================================================================
# Protocols for Integration
# ============================================================================


@runtime_checkable
class VectorSearchable(Protocol):
    """Protocol for L-gent vector search capability."""

    async def find_similar(
        self,
        embedding: list[float],
        threshold: float = 0.5,
        limit: int = 100,
    ) -> list[tuple[str, list[float], float]]:
        """
        Find similar items by embedding.

        Returns: List of (id, embedding, similarity)
        """
        ...


@runtime_checkable
class TraceQueryable(Protocol):
    """Protocol for N-gent trace queries."""

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """Query traces."""
        ...


# ============================================================================
# Clustering
# ============================================================================


@dataclass
class Cluster:
    """A cluster of embeddings."""

    centroid: list[float]
    members: list[tuple[str, list[float]]]  # (id, embedding)
    density: float = 0.0
    variance: float = 0.0


def simple_cluster(
    items: list[tuple[str, list[float]]],
    threshold: float = 0.3,
) -> list[Cluster]:
    """
    Simple clustering by greedy assignment.

    Items within `threshold` distance of a centroid are assigned to that cluster.
    Not as sophisticated as HDBSCAN, but fast and sufficient for demos.
    """
    if not items:
        return []

    clusters: list[Cluster] = []
    assigned: set[str] = set()

    for item_id, embedding in items:
        if item_id in assigned:
            continue

        # Start new cluster with this item
        cluster_members = [(item_id, embedding)]
        assigned.add(item_id)

        # Find all items within threshold
        for other_id, other_embedding in items:
            if other_id in assigned:
                continue

            dist = _euclidean_distance(embedding, other_embedding)
            if dist <= threshold:
                cluster_members.append((other_id, other_embedding))
                assigned.add(other_id)

        # Compute centroid
        if cluster_members:
            centroid = _compute_centroid([e for _, e in cluster_members])
            variance = _compute_variance(centroid, [e for _, e in cluster_members])
            density = len(cluster_members) / (
                1.0 + variance
            )  # Higher variance = lower density

            clusters.append(
                Cluster(
                    centroid=centroid,
                    members=cluster_members,
                    density=density,
                    variance=variance,
                )
            )

    return clusters


def _euclidean_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between vectors."""
    if len(a) != len(b):
        return float("inf")
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _compute_centroid(embeddings: list[list[float]]) -> list[float]:
    """Compute centroid of embeddings."""
    if not embeddings:
        return []
    dim = len(embeddings[0])
    centroid = [0.0] * dim
    for emb in embeddings:
        for i, v in enumerate(emb):
            centroid[i] += v
    n = len(embeddings)
    return [v / n for v in centroid]


def _compute_variance(centroid: list[float], embeddings: list[list[float]]) -> float:
    """Compute variance from centroid."""
    if not embeddings:
        return 0.0
    total = sum(_euclidean_distance(centroid, emb) ** 2 for emb in embeddings)
    return total / len(embeddings)


# ============================================================================
# DesireLineComputer
# ============================================================================


@dataclass
class TransitionData:
    """Data about a transition between landmarks."""

    from_landmark_id: str
    to_landmark_id: str
    count: int
    trace_ids: list[str]


class DesireLineComputer:
    """
    Analyzes N-gent SemanticTraces to find actual navigation patterns.

    Urban planners look at worn grass to find desire lines.
    We look at N-gent traces.
    """

    def __init__(self, trace_store: TraceQueryable | None = None):
        self.trace_store = trace_store

    def compute_from_traces(
        self,
        traces: list[Any],
        landmarks: list[Attractor],
        min_transitions: int = 1,
    ) -> list[WeightedEdge]:
        """
        Derive desire lines from traces.

        Args:
            traces: List of SemanticTrace objects (or any with .vector attribute)
            landmarks: List of landmarks to map traces to
            min_transitions: Minimum transitions to create an edge

        Returns:
            List of weighted edges representing desire lines
        """
        if not traces or not landmarks:
            return []

        # Count transitions between landmarks
        transitions: Counter[tuple[str, str]] = Counter()
        trace_mapping: dict[tuple[str, str], list[str]] = {}

        for i in range(len(traces) - 1):
            trace_a = traces[i]
            trace_b = traces[i + 1]

            # Get embeddings
            vec_a = self._get_vector(trace_a)
            vec_b = self._get_vector(trace_b)

            if vec_a is None or vec_b is None:
                continue

            # Map to nearest landmarks
            from_landmark = self._nearest_landmark(vec_a, landmarks)
            to_landmark = self._nearest_landmark(vec_b, landmarks)

            if from_landmark is None or to_landmark is None:
                continue

            # Skip self-transitions
            if from_landmark.id == to_landmark.id:
                continue

            key = (from_landmark.id, to_landmark.id)
            transitions[key] += 1

            if key not in trace_mapping:
                trace_mapping[key] = []
            trace_id = getattr(trace_a, "trace_id", str(i))
            trace_mapping[key].append(trace_id)

        # Convert to weighted edges
        total = sum(transitions.values())
        if total == 0:
            return []

        edges = []
        for (from_id, to_id), count in transitions.items():
            if count < min_transitions:
                continue

            # Check if reverse exists
            reverse_count = transitions.get((to_id, from_id), 0)
            bidirectional = reverse_count > 0

            edges.append(
                WeightedEdge(
                    source=from_id,
                    target=to_id,
                    weight=count / total,
                    bidirectional=bidirectional,
                    trace_ids=trace_mapping.get((from_id, to_id), [])[:10],
                    transition_count=count,
                )
            )

        return edges

    def _get_vector(self, trace: Any) -> list[float] | None:
        """Extract vector from trace."""
        if hasattr(trace, "vector") and trace.vector is not None:
            return trace.vector
        if hasattr(trace, "embedding"):
            return trace.embedding
        return None

    def _nearest_landmark(
        self, embedding: list[float], landmarks: list[Attractor]
    ) -> Attractor | None:
        """Find nearest landmark to embedding."""
        if not landmarks:
            return None
        return min(landmarks, key=lambda l: l.distance_to(embedding))


# ============================================================================
# CartographerAgent
# ============================================================================


@dataclass
class CartographerConfig:
    """Configuration for the CartographerAgent."""

    # Clustering
    cluster_threshold: float = 0.3  # Distance threshold for clustering
    min_cluster_size: int = 1  # Minimum items to form a landmark

    # Desire lines
    min_transitions: int = 1  # Minimum transitions to create desire line
    lookback_traces: int = 1000  # How many traces to consider

    # Horizon
    base_radius: float = 0.5  # Base horizon radius
    default_budget: int = 4000  # Default token budget

    # Voids
    void_threshold: float = 0.5  # Density below this = void
    min_void_radius: float = 0.2  # Minimum void size to report


class CartographerAgent:
    """
    Projects high-dimensional memory space into a navigable HoloMap.

    Answers: "Where am I?", "What is adjacent?", "Where are the cliffs?"

    CRITICAL INTEGRATIONS:
    - L-gent: Provides the embedding space (terrain)
    - N-gent: Provides SemanticTraces (desire lines)
    - B-gent: Constrains resolution via token budget
    """

    def __init__(
        self,
        vector_search: VectorSearchable | None = None,
        trace_store: TraceQueryable | None = None,
        config: CartographerConfig | None = None,
    ):
        self.vector_search = vector_search
        self.trace_store = trace_store
        self.config = config or CartographerConfig()
        self.desire_line_computer = DesireLineComputer(trace_store)

    async def invoke(
        self,
        context: ContextVector,
        resolution: Resolution = Resolution.ADAPTIVE,
        budget_tokens: int | None = None,
    ) -> HoloMap:
        """
        Generate a HoloMap centered on the given context.

        Args:
            context: Current position ("You are here")
            resolution: Map resolution level
            budget_tokens: Token budget for horizon

        Returns:
            HoloMap with landmarks, desire lines, voids, and horizon
        """
        budget = budget_tokens or self.config.default_budget

        # 1. FIND LANDMARKS (high-density memory clusters)
        landmarks = await self.find_attractors(context)

        # 2. COMPUTE DESIRE LINES (from N-gent traces)
        desire_lines = await self.compute_desire_lines(landmarks)

        # 3. CALCULATE HORIZON (progressive disclosure boundary)
        horizon = self._compute_horizon(context, budget, resolution)

        # 4. IDENTIFY VOIDS (sparse regions)
        voids = self._find_voids(landmarks, context)

        return HoloMap(
            origin=context,
            landmarks=landmarks,
            desire_lines=desire_lines,
            voids=voids,
            horizon=horizon,
            resolution=resolution,
        )

    async def find_attractors(
        self,
        context: ContextVector,
        radius: float | None = None,
    ) -> list[Attractor]:
        """
        Find dense clusters of memories that form coherent concepts.

        Uses L-gent's semantic search to find nearby items, then clusters.
        """
        # If no vector search, return empty
        if self.vector_search is None:
            return []

        # Find nearby items
        try:
            nearby = await self.vector_search.find_similar(
                embedding=context.embedding,
                threshold=1.0 - (radius or self.config.cluster_threshold),
                limit=200,
            )
        except Exception:
            return []

        if not nearby:
            return []

        # Convert to cluster input format
        items = [(item_id, embedding) for item_id, embedding, _ in nearby]

        # Cluster into attractors
        clusters = simple_cluster(items, threshold=self.config.cluster_threshold)

        # Convert to Attractor objects
        attractors = []
        for i, cluster in enumerate(clusters):
            if len(cluster.members) < self.config.min_cluster_size:
                continue

            # Generate label from first few member IDs
            member_ids = [m[0] for m in cluster.members]
            label = self._generate_label(member_ids)

            attractors.append(
                Attractor(
                    id=f"attractor_{i}_{uuid4().hex[:8]}",
                    centroid=cluster.centroid,
                    members=member_ids,
                    label=label,
                    density=cluster.density,
                    member_count=len(cluster.members),
                    variance=cluster.variance,
                )
            )

        return attractors

    async def compute_desire_lines(
        self,
        landmarks: list[Attractor],
    ) -> list[WeightedEdge]:
        """
        Derive desire lines from N-gent trace history.

        These are the paths agents ACTUALLY took, not designed paths.
        """
        if not landmarks or self.trace_store is None:
            return []

        # Get recent traces
        try:
            traces = self.trace_store.query(limit=self.config.lookback_traces)
        except Exception:
            return []

        if not traces:
            return []

        return self.desire_line_computer.compute_from_traces(
            traces=traces,
            landmarks=landmarks,
            min_transitions=self.config.min_transitions,
        )

    def _compute_horizon(
        self,
        context: ContextVector,
        budget: int,
        resolution: Resolution,
    ) -> Horizon:
        """Compute horizon based on budget and resolution."""
        # Adjust base radius by resolution
        scale = {
            Resolution.HIGH: 1.5,
            Resolution.MEDIUM: 1.0,
            Resolution.LOW: 0.5,
            Resolution.ADAPTIVE: 1.0,
        }[resolution]

        base_radius = self.config.base_radius * scale

        return Horizon.from_budget(
            center=context.embedding,
            token_budget=budget,
            base_radius=base_radius,
        )

    def _find_voids(
        self,
        landmarks: list[Attractor],
        context: ContextVector,
    ) -> list[Void]:
        """
        Identify sparse regions in semantic space.

        "Here be dragons" - areas with little data.
        """
        if not landmarks:
            # If no landmarks, the whole space is a void
            return [
                Void(
                    id="void_total",
                    region=Region(
                        id="region_total",
                        center=context.embedding,
                        radius=1.0,
                        label="Unexplored Space",
                    ),
                    uncertainty=1.0,
                    reason="no_landmarks",
                )
            ]

        # Find low-density areas between landmarks
        voids = []
        len(context.embedding)

        # Check density in a grid around context
        # Simple approach: check midpoints between landmark pairs
        for i, l1 in enumerate(landmarks):
            for l2 in landmarks[i + 1 :]:
                midpoint = [(a + b) / 2 for a, b in zip(l1.centroid, l2.centroid)]

                # Check if midpoint has low density
                nearby_count = sum(
                    1 for l in landmarks if l.distance_to(midpoint) < 0.3
                )

                if nearby_count == 0:
                    # This is a void
                    void_radius = max(
                        self.config.min_void_radius,
                        l1.distance_to(midpoint) * 0.3,
                    )
                    voids.append(
                        Void(
                            id=f"void_{len(voids)}",
                            region=Region(
                                id=f"region_{len(voids)}",
                                center=midpoint,
                                radius=void_radius,
                                label="Sparse Region",
                            ),
                            uncertainty=0.8,
                            reason="sparse_data",
                        )
                    )

        return voids

    def _generate_label(self, member_ids: list[str]) -> str:
        """Generate a human-readable label for a cluster."""
        if not member_ids:
            return "Unknown"

        # Simple approach: use common prefix or first ID
        # In production, could use LLM to generate label
        first_id = member_ids[0]

        # Try to extract meaningful part
        parts = first_id.replace("_", " ").replace("-", " ").split()
        if parts:
            return " ".join(parts[:3]).title()

        return first_id[:20]


# ============================================================================
# Mock Implementations for Testing
# ============================================================================


class MockVectorSearch:
    """Mock L-gent vector search for testing."""

    def __init__(self, items: list[tuple[str, list[float]]] | None = None):
        self.items = items or []

    async def find_similar(
        self,
        embedding: list[float],
        threshold: float = 0.5,
        limit: int = 100,
    ) -> list[tuple[str, list[float], float]]:
        """Find similar items."""
        results = []
        for item_id, item_embedding in self.items:
            dist = _euclidean_distance(embedding, item_embedding)
            similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
            if similarity >= threshold:
                results.append((item_id, item_embedding, similarity))

        # Sort by similarity descending
        results.sort(key=lambda x: -x[2])
        return results[:limit]


class MockTraceStore:
    """Mock N-gent trace store for testing."""

    def __init__(self, traces: list[Any] | None = None):
        self._traces = traces or []

    def add_trace(self, trace: Any) -> None:
        """Add a trace."""
        self._traces.append(trace)

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Any]:
        """Query traces."""
        results = self._traces

        if agent_id:
            results = [t for t in results if getattr(t, "agent_id", None) == agent_id]
        if agent_genus:
            results = [
                t for t in results if getattr(t, "agent_genus", None) == agent_genus
            ]

        return results[offset : offset + limit]


@dataclass
class MockTrace:
    """Mock trace for testing."""

    trace_id: str
    vector: list[float] | None = None
    agent_id: str = "test_agent"
    agent_genus: str = "test"


# ============================================================================
# Factory Functions
# ============================================================================


def create_cartographer(
    vector_search: VectorSearchable | None = None,
    trace_store: TraceQueryable | None = None,
    config: CartographerConfig | None = None,
) -> CartographerAgent:
    """Create a CartographerAgent."""
    return CartographerAgent(
        vector_search=vector_search,
        trace_store=trace_store,
        config=config,
    )


def create_mock_cartographer(
    items: list[tuple[str, list[float]]] | None = None,
    traces: list[Any] | None = None,
) -> CartographerAgent:
    """Create a CartographerAgent with mock backends."""
    return CartographerAgent(
        vector_search=MockVectorSearch(items),
        trace_store=MockTraceStore(traces),
    )
