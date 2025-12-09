# D-gent Vision: Memory as Landscape

The evolution from functional storage to enlightened memory.

---

## Philosophy

> "Memory is not a warehouse—it is a landscape to be cultivated."

The current D-gent spec provides **solid foundations** (Volatile, Persistent, Lens, Symbiont). But the full potential of data agents emerges when we recognize that memory is **multi-dimensional**:

- **Semantic** (proximity in meaning space)
- **Temporal** (trajectory through time)
- **Relational** (structure of connections)
- **Focused** (compositional access)

This document specifies the **Noosphere Layer**—the enlightened architecture where these dimensions integrate.

---

## The Noosphere Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE NOOSPHERE LAYER                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Semantic    │  │  Temporal   │  │ Relational  │              │
│  │ Manifold    │  │  Witness    │  │   Lattice   │              │
│  │ (Vectors)   │  │  (Events)   │  │  (Graphs)   │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              THE LENS ALGEBRA                            │    │
│  │   Focusing | Composition | Traversals | Prisms | Iso    │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │            THE SYMBIONT LAYER                            │    │
│  │   Pure Logic × Stateful Memory = Composable Agents       │    │
│  └──────────────────────────┬──────────────────────────────┘    │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │           THE PERSISTENCE SPECTRUM                       │    │
│  │   Volatile → Cached → File → DB → Vector → Stream        │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Semantic Manifold (VectorAgent++)

Not just embeddings—a **curved space** of meaning.

### Specification

```python
@dataclass(frozen=True)
class SemanticManifold(Generic[S]):
    """
    State exists in a semantic space with curvature.

    Near similar concepts (low curvature): Easy retrieval
    At conceptual boundaries (high curvature): Creative connections
    In voids (Ma): Generative potential
    """
    dimension: int
    distance: DistanceMetric = "cosine"

    async def embed(self, state: S) -> Point:
        """Project state into semantic space."""
        ...

    async def neighbors(self, point: Point, radius: float) -> list[S]:
        """Find semantically similar states."""
        ...

    async def geodesic(self, a: Point, b: Point) -> list[Point]:
        """Path of minimum semantic distance."""
        ...

    async def curvature_at(self, point: Point) -> float:
        """
        Local semantic complexity.

        High curvature = conceptual boundary (synthesis opportunity)
        Low curvature = stable semantic region
        """
        ...

    async def void_nearby(self, point: Point) -> Optional[Void]:
        """
        Detect unexplored regions (Ma).

        Voids are generative—they suggest what could exist
        but doesn't yet. Aligned with the "Void's Fecundity"
        principle in Membrane Protocol.
        """
        ...
```

### Use Cases

- **RAG with Context**: When retrieving, consider not just similarity but *curvature*—high-curvature regions may offer creative connections
- **Knowledge Discovery**: Voids (Ma) suggest gaps in understanding
- **L-gent Integration**: Tongues positioned by domain semantics, not just keywords

### Category-Theoretic View

The Semantic Manifold is a **functor** from states to geometric space:

$$F: \mathcal{C}_{State} \to \mathcal{C}_{Manifold}$$

Preserving compositional structure: related states map to proximate points.

---

## 2. Temporal Witness (StreamAgent++)

Event sourcing + W-gent pattern observation.

### Specification

```python
@dataclass(frozen=True)
class TemporalWitness(Generic[E, S]):
    """
    Memory as witnessed time, not stored snapshots.

    Every state change is an event.
    Every event is witnessed, not just logged.
    Witnesses can be queried: "When did X drift from Y?"
    """
    fold: Callable[[S, E], S]
    initial: S

    async def append(self, event: E, witness: WitnessReport) -> None:
        """Record event with observation metadata."""
        ...

    async def replay(self, from_time: DateTime, to_time: DateTime) -> S:
        """Reconstruct state at any moment."""
        ...

    async def detect_drift(self, trajectory: str) -> DriftReport:
        """
        When did behavior diverge from expectation?

        Integrates W-gent fidelity tracking—not just "what changed"
        but "was the change consistent with prior patterns?"
        """
        ...

    async def momentum(self) -> Vector:
        """
        Semantic velocity: where is state heading?

        From EventStream protocol: p⃗ = m · v⃗
        where mass is confidence and velocity is change rate.
        """
        ...

    async def entropy(self, window: Duration) -> float:
        """
        Rate of state change (chaos vs stability).

        High entropy = rapid change (careful with interventions)
        Low entropy = stable (safe for reflection)
        """
        ...
```

### Use Cases

- **K-gent Consistency**: "Have I been consistent about X?" → Temporal drift detection
- **J-gent Postmortem**: Failed branches recorded with full temporal context
- **Mirror Protocol Integration**: Tension history enables dialectical analysis

### W-gent Integration

The Temporal Witness embodies W-gent principles:

- **Non-Judgmental Recording**: Events witnessed, not evaluated
- **Fidelity Tracking**: Drift detection measures consistency
- **Pattern Inference**: Momentum reveals emergent trajectories

---

## 3. Relational Lattice (GraphAgent++)

Not just graphs—a **lattice** with joins and meets.

### Specification

```python
@dataclass(frozen=True)
class RelationalLattice(Generic[N, E]):
    """
    State as a lattice of relationships.

    Lattice operations enable reasoning about entailment:
    - Meet (∧): Greatest common sub-state
    - Join (∨): Least common super-state
    - Order (≤): Is A entailed by B?
    """
    node_type: Type[N]
    edge_type: Type[E]

    async def meet(self, a: N, b: N) -> N:
        """What do a and b have in common?"""
        ...

    async def join(self, a: N, b: N) -> N:
        """Smallest state containing both a and b."""
        ...

    async def entails(self, a: N, b: N) -> bool:
        """Is a implied by b?"""
        ...

    async def lineage(self, node: N) -> list[N]:
        """
        Ancestry chain (provenance).

        Every artifact knows its origins—essential for
        ethical memory and the Accursed Share principle.
        """
        ...

    async def descendants(self, node: N) -> list[N]:
        """All derived artifacts."""
        ...

    async def relate(
        self,
        source: N,
        edge: E,
        target: N,
        bidirectional: bool = False
    ) -> None:
        """Establish relationship between nodes."""
        ...
```

### Use Cases

- **L-gent Discovery**: Find related tongues by lattice position, not keyword matching
- **C-gent Composition**: Verify composability via lattice order
- **Provenance Tracking**: Every artifact knows its derivation chain

### Category-Theoretic View

The Relational Lattice forms a **preorder category** where:
- Objects are nodes
- Morphisms are paths
- Composition is path concatenation
- Identity is staying at a node

---

## 4. The Unified Memory Monad

All three layers compose via a universal memory monad.

### Specification

```python
class UnifiedMemory(Generic[S]):
    """
    The enlightened D-gent: all memory modes unified.

    Provides:
    - Immediate: load()/save() (volatile)
    - Durable: persist()/recover() (file/db)
    - Semantic: associate()/recall() (vectors)
    - Temporal: witness()/replay() (events)
    - Relational: relate()/trace() (graphs)

    All through compositional lenses.
    """

    # Core DataAgent interface (existing)
    async def load(self) -> S: ...
    async def save(self, state: S) -> None: ...
    async def history(self, limit: int | None = None) -> list[S]: ...

    # Semantic layer
    async def associate(self, state: S, concept: str) -> None:
        """Tag state with semantic concept."""
        ...

    async def recall(self, concept: str, limit: int = 5) -> list[S]:
        """Find states associated with concept."""
        ...

    async def semantic_neighbors(self, state: S) -> list[tuple[S, float]]:
        """States semantically similar to given state."""
        ...

    # Temporal layer
    async def witness(self, event: str, state: S) -> None:
        """Record state transition with event label."""
        ...

    async def replay(self, timestamp: DateTime) -> S:
        """Reconstruct state at specific time."""
        ...

    async def timeline(self, window: Duration) -> list[tuple[DateTime, S]]:
        """State evolution within time window."""
        ...

    # Relational layer
    async def relate(self, source: str, relation: str, target: str) -> None:
        """Establish relationship between entities."""
        ...

    async def trace(self, start: str, depth: int = 3) -> Graph:
        """Graph traversal from starting node."""
        ...

    async def ancestors(self, node: str) -> list[str]:
        """Lineage chain to root."""
        ...

    # Composition (existing lens algebra)
    def __rshift__(self, lens: Lens[S, A]) -> "UnifiedMemory[A]":
        """Compose with lens for focused access."""
        ...
```

### Monad Laws

UnifiedMemory satisfies the monad laws:

1. **Left Identity**: `return(a) >>= f ≡ f(a)`
2. **Right Identity**: `m >>= return ≡ m`
3. **Associativity**: `(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)`

This ensures UnifiedMemory composes correctly with other kgents infrastructure.

---

## 5. Entropy-Aware Persistence Selection

The system **automatically** chooses persistence strategy based on context.

### Specification

```python
class AdaptiveMemory(Generic[S]):
    """
    Memory that adapts its persistence strategy.

    Hot data → Volatile (fast)
    Warm data → Cached (balanced)
    Cold data → Persistent (durable)
    Semantic data → Vector (searchable)
    Evolving data → Stream (auditable)
    """

    def __init__(self, entropy_budget: float):
        self.budget = entropy_budget
        self.strategies = {
            "volatile": VolatileAgent,
            "cached": CachedAgent,
            "persistent": PersistentAgent,
            "vector": VectorAgent,
            "stream": StreamAgent,
        }

    async def save(self, state: S, hints: dict = {}) -> None:
        """
        Auto-select strategy based on:
        - Access patterns (hot vs cold)
        - State characteristics (size, type)
        - Entropy budget (J-gent depth)
        - Semantic richness (embedding potential)
        """
        strategy = self._select_strategy(state, hints)
        await strategy.save(state)

    def _select_strategy(self, state: S, hints: dict) -> DataAgent[S]:
        """
        Strategy selection heuristics:

        1. If budget < 0.3: Volatile only (entropy constrained)
        2. If state has embeddings: Vector
        3. If hints["auditable"]: Stream
        4. If access_frequency > threshold: Cached
        5. Default: Persistent
        """
        ...
```

### J-gent Integration

```python
# At recursion depth 0: full memory access
root_memory = AdaptiveMemory(budget=1.0)

# At depth 3: constrained to volatile
deep_memory = AdaptiveMemory(budget=0.25)

# Ground collapse: persist to stream for postmortem
if ground_collapse:
    await stream_agent.append(failure_event, witness_report)
```

---

## 6. The Memory Garden

Long-term vision: Memory as a **cultivated space**.

### The Metaphor

```
┌────────────────────────────────────────────────────────────┐
│                    THE MEMORY GARDEN                        │
│                                                            │
│  🌱 Seeds: New ideas, unvalidated hypotheses               │
│  🌿 Saplings: Emerging patterns, growing certainty         │
│  🌳 Trees: Established knowledge, high trust               │
│  🍂 Compost: Deprecated ideas, recycled into new growth    │
│  🌸 Flowers: Peak insights, ready for harvesting           │
│  🍄 Mycelium: Hidden connections (relational lattice)      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Specification

```python
class MemoryGarden(Generic[S]):
    """
    Memory with lifecycle, trust, and cultivation.

    Aligns with kgents' joy-inducing principle:
    Data management should feel like gardening, not filing.
    """

    async def plant(self, seed: S, hypothesis: str) -> GardenEntry:
        """
        Track new hypothesis.

        Seeds have low trust, high potential.
        They need nurturing (evidence) to grow.
        """
        ...

    async def nurture(self, entry: GardenEntry, evidence: Evidence) -> None:
        """
        Add evidence, increase trust.

        As a sapling receives evidence, it grows toward
        tree status. Contradictory evidence may cause
        wilting (trust decay).
        """
        ...

    async def harvest(self, flower: GardenEntry) -> Insight:
        """
        Extract and act on insight.

        Peak insights (flowers) are ready for use.
        Harvesting doesn't destroy—it transforms.
        """
        ...

    async def prune(self, tree: GardenEntry, reason: str) -> None:
        """
        Remove outdated branches.

        Even established trees need pruning.
        Removed material goes to compost, not oblivion.
        """
        ...

    async def compost(self, dead: GardenEntry) -> Nutrients:
        """
        Transform deprecated to potential.

        Nothing is truly deleted—deprecated ideas
        become nutrients for future growth.
        This is the Accursed Share principle:
        excess feeds the system's evolution.
        """
        ...

    async def trace_mycelium(self, entry: GardenEntry) -> list[GardenEntry]:
        """
        Find hidden connections.

        The mycelium (relational lattice) connects entries
        in non-obvious ways. Like fungal networks in forests.
        """
        ...
```

### Trust Model

```python
@dataclass
class GardenEntry:
    content: S
    lifecycle: Lifecycle  # SEED | SAPLING | TREE | FLOWER | COMPOST
    trust: float  # 0.0 to 1.0
    evidence: list[Evidence]
    contradictions: list[Contradiction]
    planted_at: DateTime
    last_nurtured: DateTime
```

Trust evolves based on:
- **Supporting evidence** increases trust
- **Contradictions** decrease trust (but don't immediately kill)
- **Time without nurturing** causes decay (unused ideas wilt)
- **Successful harvests** increase trust of connected entries

---

## Integration Points

### With L-gent (Library)

UnifiedMemory becomes L-gent's persistence layer:
- Catalog entries stored with semantic embeddings
- Relationships form the relational lattice
- Usage history tracked via temporal witness

### With G-gent (Grammar)

Tongues benefit from all memory modes:
- **Semantic**: Find similar grammars by domain
- **Temporal**: Track tongue evolution over time
- **Relational**: Tongue composition graphs

### With J-gent (JIT)

Entropy-aware persistence integrates directly:
- Shallow recursion: Full memory access
- Deep recursion: Constrained to volatile only
- Ground collapse: Persist to stream for postmortem

### With K-gent (Kent)

The Memory Garden metaphor aligns perfectly:
- K-gent personality = long-term trees
- Session context = daily flowers
- Deprecated opinions = composted for growth

### With Mirror Protocol

TemporalWitness integrates with dialectical introspection:
- Tensions tracked as temporal events
- Drift detection reveals inconsistencies
- Momentum shows where thinking is heading

---

## Principles Alignment

| Principle | How This Vision Embodies It |
|-----------|----------------------------|
| **Tasteful** | Memory modes are curated, not exhaustive |
| **Curated** | Adaptive selection, not manual configuration |
| **Ethical** | Time-travel enables accountability; lineage tracks provenance |
| **Joy-Inducing** | Garden metaphor makes memory delightful |
| **Composable** | Lens algebra + unified monad |
| **Heterarchical** | No single source of truth—multi-modal |
| **Generative** | Voids (Ma) enable new discoveries; compost feeds growth |

---

## Implementation Phases

### Phase 2: Advanced D-gents (~800 lines)

```
impl/claude/agents/d/
  vector.py           # VectorAgent (numpy/FAISS backend)
  graph.py            # GraphAgent (networkx backend)
  stream.py           # StreamAgent (event sourcing)
```

### Phase 3: Extended Protocols (~400 lines)

```
impl/claude/agents/d/
  transactional.py    # TransactionalDataAgent
  queryable.py        # QueryableDataAgent
  observable.py       # ObservableDataAgent
  unified.py          # UnifiedMemory composition
```

### Phase 4: The Noosphere (~600 lines)

```
impl/claude/agents/d/
  manifold.py         # SemanticManifold
  witness.py          # TemporalWitness
  lattice.py          # RelationalLattice
  garden.py           # MemoryGarden metaphor layer
```

---

## Key Insight

The current D-gent impl is **solid but shallow**. It covers Types I-III beautifully (Volatile, Persistent, Lens), but the spec's vision of semantic/temporal/relational memory (Types IV-VI) needs deepening.

The futuristic system isn't just "add VectorDB"—it's recognizing that **memory is a multi-dimensional space** where:
- Embeddings provide *semantic proximity*
- Events provide *temporal trajectory*
- Graphs provide *relational structure*
- Lenses provide *compositional focus*

The kgents philosophy ("tasteful, curated, ethical, joy-inducing") demands that data management be **as thoughtfully designed as agent logic itself**. Memory should feel like cultivation, not storage.

---

## See Also

- [README.md](README.md) - D-gents overview
- [persistence.md](persistence.md) - Current persistence spectrum
- [lenses.md](lenses.md) - Compositional access
- [symbiont.md](symbiont.md) - Endosymbiotic pattern
- [../protocols/event_stream.md](../protocols/event_stream.md) - Temporal foundations
- [../protocols/membrane.md](../protocols/membrane.md) - Semantic manifold concepts
