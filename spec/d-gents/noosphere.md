# The Noosphere Layer

Detailed specifications for advanced D-gent types: Semantic Manifold, Temporal Witness, and Relational Lattice.

---

## Overview

The Noosphere Layer represents the **enlightened architecture** of D-gents, where memory transcends simple storage to become a multi-dimensional landscape:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE NOOSPHERE LAYER                          │
│                                                                 │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │   Semantic    │  │   Temporal    │  │  Relational   │        │
│  │   Manifold    │  │   Witness     │  │   Lattice     │        │
│  │               │  │               │  │               │        │
│  │  "What is     │  │  "When did    │  │  "How does    │        │
│  │   similar?"   │  │   it change?" │  │   it relate?" │        │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘        │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             ▼                                   │
│              ┌───────────────────────────────┐                  │
│              │     Unified Memory Monad      │                  │
│              │                               │                  │
│              │  Compositional access via     │                  │
│              │  Lens Algebra + Symbiont      │                  │
│              └───────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Semantic Manifold

### Philosophy

> "Meaning is not stored—it is navigated."

Traditional vector databases treat embeddings as simple lookup tables. The Semantic Manifold recognizes that meaning space has **geometry**:

- **Curvature**: Regions where concepts cluster tightly (low curvature) vs. boundaries between domains (high curvature)
- **Voids (Ma)**: Unexplored regions with generative potential
- **Geodesics**: Natural paths of semantic transformation

### Specification

```python
from typing import TypeVar, Generic, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

S = TypeVar("S")  # State type

class DistanceMetric(Enum):
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"

@dataclass
class Point:
    """A point in semantic space."""
    coordinates: np.ndarray
    metadata: dict

@dataclass
class Void:
    """An unexplored region (Ma)."""
    center: Point
    radius: float
    potential: float  # Estimated generative value

@dataclass
class SemanticManifold(Generic[S]):
    """
    State exists in a semantic space with curvature.

    The manifold provides:
    - Semantic similarity (neighbors)
    - Creative connections (high-curvature regions)
    - Generative potential (voids)
    """
    dimension: int
    distance: DistanceMetric = DistanceMetric.COSINE
    embedder: Optional["Embedder"] = None  # Pluggable embedding model

    async def embed(self, state: S) -> Point:
        """
        Project state into semantic space.

        The embedding model determines how state maps to coordinates.
        Default: Use sentence-transformers for text, identity for vectors.
        """
        ...

    async def neighbors(
        self,
        point: Point,
        radius: float,
        limit: int = 10
    ) -> List[Tuple[S, float]]:
        """
        Find semantically similar states within radius.

        Returns: List of (state, distance) pairs, sorted by distance.
        """
        ...

    async def nearest(self, point: Point, k: int = 5) -> List[Tuple[S, float]]:
        """
        Find k nearest neighbors.

        Equivalent to neighbors() but bounded by count, not radius.
        """
        ...

    async def geodesic(self, a: Point, b: Point, steps: int = 10) -> List[Point]:
        """
        Path of minimum semantic distance between two points.

        The geodesic is the "natural" transformation path between concepts.
        Useful for:
        - Understanding conceptual transitions
        - Generating intermediate states
        - Detecting barriers (high-curvature regions on the path)
        """
        ...

    async def curvature_at(self, point: Point, radius: float = 0.1) -> float:
        """
        Local semantic complexity.

        High curvature (> 1.0): Conceptual boundary
        - Many different concepts nearby
        - Synthesis opportunities
        - Creative connections possible

        Low curvature (< 0.5): Stable semantic region
        - Similar concepts cluster tightly
        - Easy retrieval
        - High confidence matches
        """
        ...

    async def void_nearby(
        self,
        point: Point,
        search_radius: float = 1.0
    ) -> Optional[Void]:
        """
        Detect unexplored regions (Ma).

        Voids are generative—they suggest what could exist but doesn't yet.

        Detection heuristics:
        - Low density of existing states
        - Distance from all known clusters
        - Semantic coherence (not random noise)

        Returns: Void with highest potential, or None if fully explored.
        """
        ...

    async def cluster_centers(self, k: int = 5) -> List[Point]:
        """
        Find k cluster centers in the manifold.

        Useful for understanding semantic structure.
        """
        ...
```

### Integration with L-gent

```python
# Find tongues by semantic similarity, not keyword matching
tongue_embedding = await manifold.embed(tongue.domain_description)
similar_tongues = await manifold.neighbors(tongue_embedding, radius=0.3)

# Discover synthesis opportunities
curvature = await manifold.curvature_at(tongue_embedding)
if curvature > 1.5:
    # High curvature = boundary between domains
    # Potential for cross-domain tongue synthesis
    synthesis_candidates = await manifold.neighbors(tongue_embedding, radius=0.5)
```

### Category-Theoretic View

The Semantic Manifold is a **functor** from the category of states to the category of geometric spaces:

$$F: \mathcal{C}_{State} \to \mathcal{C}_{Manifold}$$

**Functor Laws**:
1. `F(id_S) = id_{F(S)}` (identity preservation)
2. `F(g ∘ f) = F(g) ∘ F(f)` (composition preservation)

This ensures that related states map to proximate points, and transformations between states correspond to paths in the manifold.

---

## Part 2: Temporal Witness

### Philosophy

> "Memory is not what happened—it is what was witnessed."

Traditional event sourcing records events. The Temporal Witness adds **observation**:
- Not just "what" but "how confidently"
- Not just "when" but "in what context"
- Not just "change" but "drift from expectation"

### Specification

```python
from typing import TypeVar, Generic, Callable, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

E = TypeVar("E")  # Event type
S = TypeVar("S")  # State type

@dataclass
class WitnessReport:
    """Observation metadata for an event."""
    observer_id: str
    confidence: float  # 0.0 to 1.0
    context: dict  # Ambient conditions at time of observation
    anomaly_score: float  # How unexpected was this event?

@dataclass
class DriftReport:
    """Analysis of behavioral divergence."""
    trajectory: str  # What aspect was analyzed
    drift_detected: bool
    drift_start: Optional[datetime]
    drift_magnitude: float  # 0.0 to 1.0
    expected_value: S
    actual_value: S
    explanation: str

@dataclass
class TemporalWitness(Generic[E, S]):
    """
    Memory as witnessed time, not stored snapshots.

    Every state change is an event.
    Every event is witnessed, not just logged.
    Witnesses can be queried: "When did X drift from Y?"
    """
    fold: Callable[[S, E], S]  # How to apply event to state
    initial: S

    async def append(self, event: E, witness: WitnessReport) -> None:
        """
        Record event with observation metadata.

        Unlike simple event sourcing, we track:
        - Who/what observed the event
        - How confident the observation was
        - What the ambient context was
        - How anomalous the event seemed
        """
        ...

    async def load(self) -> S:
        """Replay all events to reconstruct current state."""
        ...

    async def replay(
        self,
        from_time: datetime,
        to_time: datetime
    ) -> S:
        """
        Reconstruct state at any moment in time.

        Time-travel for debugging, analysis, or rollback.
        """
        ...

    async def replay_with_witnesses(
        self,
        from_time: datetime,
        to_time: datetime
    ) -> List[Tuple[E, S, WitnessReport]]:
        """
        Replay with full observation context.

        Returns: List of (event, state_after, witness_report) tuples.
        """
        ...

    async def detect_drift(
        self,
        trajectory: str,
        window: timedelta = timedelta(days=7)
    ) -> DriftReport:
        """
        When did behavior diverge from expectation?

        Integrates W-gent fidelity tracking—not just "what changed"
        but "was the change consistent with prior patterns?"

        Parameters:
        - trajectory: Aspect to analyze (e.g., "tone", "decisions", "preferences")
        - window: How far back to establish baseline

        Returns: DriftReport with analysis.
        """
        ...

    async def momentum(self) -> "Vector":
        """
        Semantic velocity: where is state heading?

        From EventStream protocol: p⃗ = m · v⃗
        where:
        - m (mass) = confidence/certainty
        - v (velocity) = rate and direction of change

        High momentum = rapid change with high confidence
        Low momentum = stable or uncertain
        """
        ...

    async def entropy(self, window: timedelta) -> float:
        """
        Rate of state change (chaos vs stability).

        High entropy (> 0.7): Rapid change, system in flux
        - Be careful with interventions
        - Wait for stability before acting

        Low entropy (< 0.3): Stable, predictable
        - Safe for reflection
        - Interventions have clearer impact
        """
        ...

    async def history(
        self,
        limit: Optional[int] = None,
        filter_by: Optional[Callable[[E], bool]] = None
    ) -> List[Tuple[datetime, E, S]]:
        """
        Query state evolution over time.

        Returns: List of (timestamp, event, state_after) tuples.
        """
        ...
```

### Integration with K-gent

```python
# K-gent checking consistency
drift = await witness.detect_drift("opinions_on_testing", window=timedelta(days=30))
if drift.drift_detected:
    # K-gent has been inconsistent about testing philosophy
    print(f"Drift started at {drift.drift_start}")
    print(f"Expected: {drift.expected_value}")
    print(f"Actual: {drift.actual_value}")
```

### Integration with J-gent

```python
# J-gent postmortem after Ground collapse
if ground_collapse:
    # Record failure with full witness context
    await witness.append(
        event=FailureEvent(reason=collapse_reason, depth=recursion_depth),
        witness=WitnessReport(
            observer_id="j-gent",
            confidence=1.0,
            context={"entropy_budget": remaining_budget},
            anomaly_score=0.0  # Expected outcome
        )
    )

    # Replay to understand what led to collapse
    history = await witness.replay_with_witnesses(
        from_time=branch_start,
        to_time=collapse_time
    )
```

---

## Part 3: Relational Lattice

### Philosophy

> "Understanding is not possession—it is relationship."

Traditional graphs store connections. The Relational Lattice adds **lattice structure**:
- Meet (∧): What do two concepts have in common?
- Join (∨): What is the smallest concept containing both?
- Order (≤): Does A entail B?

### Specification

```python
from typing import TypeVar, Generic, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

N = TypeVar("N")  # Node type
E = TypeVar("E")  # Edge type

class EdgeKind(Enum):
    """Standard relationship types."""
    IS_A = "is_a"           # Inheritance
    HAS_A = "has_a"         # Composition
    USES = "uses"           # Dependency
    DERIVES_FROM = "derives_from"  # Provenance
    CONTRADICTS = "contradicts"    # Opposition
    SYNTHESIZES = "synthesizes"    # H-gent sublation

@dataclass
class Edge(Generic[N]):
    """A typed relationship between nodes."""
    source: N
    kind: EdgeKind
    target: N
    metadata: dict = None

@dataclass
class Graph(Generic[N, E]):
    """A subgraph returned by traversal."""
    nodes: Set[N]
    edges: List[Edge[N]]

@dataclass
class RelationalLattice(Generic[N, E]):
    """
    State as a lattice of relationships.

    Lattice operations enable reasoning about entailment:
    - Meet (∧): Greatest common sub-state
    - Join (∨): Least common super-state
    - Order (≤): Is A entailed by B?
    """
    node_type: type
    edge_type: type

    # Basic graph operations

    async def add_node(self, node: N, metadata: dict = None) -> None:
        """Add a node to the lattice."""
        ...

    async def add_edge(
        self,
        source: N,
        kind: EdgeKind,
        target: N,
        metadata: dict = None
    ) -> None:
        """Establish a relationship between nodes."""
        ...

    async def get_node(self, node_id: str) -> Optional[N]:
        """Retrieve a node by ID."""
        ...

    async def get_edges(
        self,
        node: N,
        direction: str = "out",  # "out", "in", "both"
        kind: Optional[EdgeKind] = None
    ) -> List[Edge[N]]:
        """Get edges connected to a node."""
        ...

    # Lattice operations

    async def meet(self, a: N, b: N) -> N:
        """
        Greatest common sub-state (∧).

        "What do a and b have in common?"

        Returns: The most specific node that is an ancestor of both a and b.
        """
        ...

    async def join(self, a: N, b: N) -> N:
        """
        Least common super-state (∨).

        "What is the smallest state containing both a and b?"

        Returns: The most general node that is a descendant of both a and b.
        """
        ...

    async def entails(self, a: N, b: N) -> bool:
        """
        Does b entail a? (a ≤ b)

        "Is a implied by b?"

        Returns: True if a can be derived from b via lattice traversal.
        """
        ...

    async def compare(self, a: N, b: N) -> str:
        """
        Compare two nodes in the lattice order.

        Returns:
        - "a ≤ b": a is below b
        - "b ≤ a": b is below a
        - "a = b": same node
        - "incomparable": neither above nor below
        """
        ...

    # Provenance operations

    async def lineage(self, node: N, max_depth: int = 10) -> List[N]:
        """
        Ancestry chain (provenance).

        Every artifact knows its origins—essential for ethical memory.

        Returns: List of ancestors from immediate parent to root.
        """
        ...

    async def descendants(self, node: N, max_depth: int = 10) -> List[N]:
        """
        All derived artifacts.

        Returns: List of nodes derived from this node.
        """
        ...

    async def derivation_path(self, from_node: N, to_node: N) -> Optional[List[N]]:
        """
        Path from one node to another.

        Returns: Sequence of nodes, or None if no path exists.
        """
        ...

    # Traversal operations

    async def traverse(
        self,
        start: N,
        depth: int = 3,
        filter_kinds: Optional[List[EdgeKind]] = None
    ) -> Graph[N, E]:
        """
        Graph traversal from starting node.

        Returns: Subgraph containing all reachable nodes within depth.
        """
        ...

    async def find_path(
        self,
        source: N,
        target: N,
        max_depth: int = 10
    ) -> Optional[List[Edge[N]]]:
        """
        Find shortest path between two nodes.

        Returns: List of edges forming the path, or None if unreachable.
        """
        ...

    async def connected_components(self) -> List[Set[N]]:
        """
        Find all connected components in the lattice.

        Useful for identifying isolated clusters of knowledge.
        """
        ...
```

### Integration with L-gent

```python
# L-gent using lattice for tongue discovery
lattice = catalog_registry.relational_lattice

# Find tongues related to "data validation"
validation_tongue = await lattice.get_node("ValidationTongue")
related = await lattice.traverse(validation_tongue, depth=2)

# Check if Schema tongue entails Command tongue
if await lattice.entails(schema_tongue, command_tongue):
    # Schema is more general; Command is a specialization
    pass

# Find common abstraction between two tongues
common = await lattice.meet(json_tongue, xml_tongue)
# common = "SerializationTongue" (their shared ancestor)
```

### Integration with H-gent

```python
# Track dialectical relationships
await lattice.add_edge(
    source=thesis_node,
    kind=EdgeKind.CONTRADICTS,
    target=antithesis_node
)

await lattice.add_edge(
    source=synthesis_node,
    kind=EdgeKind.SYNTHESIZES,
    target=thesis_node
)
await lattice.add_edge(
    source=synthesis_node,
    kind=EdgeKind.SYNTHESIZES,
    target=antithesis_node
)

# Find all resolved contradictions
syntheses = await lattice.get_edges(
    node=any_node,
    kind=EdgeKind.SYNTHESIZES
)
```

### Category-Theoretic View

The Relational Lattice forms a **preorder category** where:
- Objects are nodes
- Morphisms are paths (or existence of ≤ relationship)
- Composition is path concatenation (transitive closure)
- Identity is staying at a node

The lattice operations (meet, join) make this a **lattice category**, enabling reasoning about information content:
- Meet is the categorical product
- Join is the categorical coproduct

---

## Unified Memory Composition

The three Noosphere components compose via the Lens Algebra:

```python
# Create unified memory with all three layers
memory = UnifiedMemory[AgentState](
    semantic=SemanticManifold(dimension=768),
    temporal=TemporalWitness(fold=apply_event, initial=initial_state),
    relational=RelationalLattice(node_type=Entity, edge_type=Relation),
    persistence=PersistentAgent(path="memory.json", schema=AgentState)
)

# Access semantic layer via lens
semantic_lens = Lens(
    get=lambda m: m.semantic,
    set=lambda m, s: replace(m, semantic=s)
)
semantic_memory = LensAgent(memory, semantic_lens)

# Compose operations across layers
async def find_related_and_similar(entity_id: str) -> List[Entity]:
    # Use relational lattice to find related
    entity = await memory.relational.get_node(entity_id)
    related = await memory.relational.traverse(entity, depth=2)

    # For each related, find semantically similar
    results = []
    for node in related.nodes:
        point = await memory.semantic.embed(node)
        similar = await memory.semantic.neighbors(point, radius=0.3)
        results.extend(similar)

    return results
```

---

## Implementation Notes

### Dependencies

**Required**:
- `numpy` (vector operations)
- `networkx` (graph operations)

**Optional** (for full functionality):
- `faiss-cpu` or `faiss-gpu` (fast vector search)
- `sentence-transformers` (text embeddings)
- `scikit-learn` (curvature estimation)

### Performance Considerations

| Layer | Operation | Complexity | Optimization |
|-------|-----------|------------|--------------|
| Semantic | neighbors | O(log n) with index | Use FAISS HNSW |
| Temporal | replay | O(n) events | Checkpoint snapshots |
| Relational | traverse | O(V + E) | Index by edge kind |

### Error Handling

```python
class NoosphereError(StateError):
    """Base for Noosphere layer errors."""
    pass

class SemanticError(NoosphereError):
    """Semantic manifold operation failed."""
    pass

class TemporalError(NoosphereError):
    """Temporal witness operation failed."""
    pass

class LatticeError(NoosphereError):
    """Relational lattice operation failed."""
    pass

class VoidNotFoundError(SemanticError):
    """No unexplored regions detected."""
    pass

class DriftDetectionError(TemporalError):
    """Could not analyze drift (insufficient data)."""
    pass

class NodeNotFoundError(LatticeError):
    """Node does not exist in lattice."""
    pass
```

---

## See Also

- [README.md](README.md) - D-gents overview
- [vision.md](vision.md) - Memory as Landscape philosophy
- [persistence.md](persistence.md) - Storage strategies
- [lenses.md](lenses.md) - Compositional access
- [../protocols/event_stream.md](../protocols/event_stream.md) - Temporal foundations
- [../protocols/membrane.md](../protocols/membrane.md) - Semantic manifold concepts
