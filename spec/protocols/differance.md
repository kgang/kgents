# Différance Engine: Traced Wiring Diagrams with Memory

**Status:** Draft
**Implementation:** `impl/claude/agents/differance/` (0 tests — to be built)
**Theory:** [Spivak, "Polynomial Functors"](https://arxiv.org/abs/2312.00990) + [Derrida, "Of Grammatology"](https://en.wikipedia.org/wiki/Of_Grammatology)

---

## Purpose

Every kgents output has a lineage—decisions made, alternatives rejected, paths not taken. The Différance Engine makes this lineage **visible, navigable, and generative**. Users can see the ghost heritage graph behind any output: not just what *is*, but what *almost was* and *why*.

> *"The trace is not a presence but the simulacrum of a presence that dislocates, displaces, and refers beyond itself."* — Derrida

This is not surveillance. This is **self-knowledge**: the system that knows how it came to be.

---

## Core Insight

**Différance** = **difference** + **deferral**. Every wiring decision simultaneously:
1. Creates a **difference** (this path, not that one)
2. Creates a **deferral** (the ghost path remains potentially explorable)

The trace monoid records both: what was chosen AND what was deferred.

---

## Theoretical Foundation

### Traced Monoidal Categories

From [nLab](https://ncatlab.org/nlab/show/traced+monoidal+category): A traced monoidal category has a **trace operator** that creates feedback loops while preserving composition laws.

```
Tr_{A,B}^U : Hom(A ⊗ U, B ⊗ U) → Hom(A, B)
```

The Différance Engine extends this: traces are not just feedback loops, they are **recorded wirings** with **ghost alternatives**.

### Polynomial Functor Connection

Every trace records a **wiring diagram** between polynomial agents:

```
Wiring: P → Q
P(y) = Σ_{s ∈ S} y^{E(s)}    (source polynomial)
Q(y) = Σ_{t ∈ T} y^{E'(t)}   (target polynomial)
```

The trace captures: which positions were active, which directions were taken, and which were ghosted.

---

## Type Signatures

### Core Types

```python
@dataclass(frozen=True)
class Alternative:
    """A road not taken — the ghost."""
    operation: str
    inputs: tuple[str, ...]
    reason_rejected: str
    could_revisit: bool


@dataclass(frozen=True)
class WiringTrace:
    """A single recorded wiring decision (ADR-style)."""

    # Identity
    trace_id: str
    timestamp: datetime

    # The Decision
    operation: str                          # "seq", "par", "branch", etc.
    inputs: tuple[str, ...]                 # Agent IDs wired
    output: str                             # Agent ID produced

    # Context (why this decision)
    context: str
    alternatives: tuple[Alternative, ...]   # Ghosts

    # Polynomial State
    positions_before: Mapping[str, FrozenSet[str]]
    positions_after: Mapping[str, FrozenSet[str]]

    # Lineage
    parent_trace_id: str | None


@dataclass(frozen=True)
class TraceMonoid:
    """
    Monoid of wiring traces.

    Laws:
    - Identity: ε ⊗ T = T = T ⊗ ε
    - Associativity: (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)
    """
    traces: tuple[WiringTrace, ...]

    @staticmethod
    def empty() -> TraceMonoid: ...

    def append(self, trace: WiringTrace) -> TraceMonoid: ...
    def compose(self, other: TraceMonoid) -> TraceMonoid: ...
    def ghosts(self) -> Sequence[Alternative]: ...
    def heritage_dag(self, output_id: str) -> GhostHeritageDAG: ...


@dataclass(frozen=True)
class GhostHeritageDAG:
    """The full heritage graph including ghosts."""

    nodes: Mapping[str, HeritageNode]
    edges: Sequence[HeritageEdge]
    root_id: str

    def chosen_path(self) -> Sequence[str]: ...
    def ghost_paths(self) -> Sequence[Sequence[str]]: ...
    def at_depth(self, depth: int) -> Sequence[HeritageNode]: ...


@dataclass(frozen=True)
class HeritageNode:
    """A node in the ghost heritage graph."""

    id: str
    node_type: Literal["chosen", "ghost", "deferred", "spec", "impl"]
    operation: str
    timestamp: datetime

    # For chosen nodes
    output: Any | None

    # For ghost nodes
    reason: str | None
    explorable: bool


@dataclass(frozen=True)
class HeritageEdge:
    """An edge in the ghost heritage graph."""

    source: str
    target: str
    edge_type: Literal["produced", "ghosted", "deferred", "concretized"]
```

### The Différance Polynomial

```python
class DiffState(Enum):
    """Positions in the Différance state machine."""
    ABSTRACT = "abstract"       # Working with specs
    CONCRETE = "concrete"       # Working with implementations
    BIFURCATING = "bifurcating" # Creating branch point
    MERGING = "merging"         # Combining branches
    WITNESSING = "witnessing"   # Recording trace


DIFFERANCE_POLYNOMIAL: PolyAgent[DiffState, DiffInput, DiffOutput]
# positions: frozenset(DiffState)
# directions: state → valid inputs for that state
# transition: state × input → (new_state, output, trace)
```

### Traced Operad Extension

```python
@dataclass
class TracedOperation(Operation):
    """Operation that records its wiring as a trace."""

    record_trace: bool = True
    capture_ghosts: bool = True


TRACED_OPERAD: Operad
# Extends AGENT_OPERAD with:
# - traced_seq: Sequential composition with trace
# - traced_par: Parallel composition with trace
# - branch_explore: Branch with ghost capture
# - fork_speculative: Create alternative wirings without executing
# - merge_traces: Compose trace histories
```

---

## Laws / Invariants

### Trace Monoid Laws

| Law | Equation | Meaning |
|-----|----------|---------|
| **Identity** | `ε ⊗ T = T = T ⊗ ε` | Empty trace is identity |
| **Associativity** | `(A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)` | Trace composition is associative |
| **Commutativity (partial)** | `T_a ⊗ T_b = T_b ⊗ T_a` when independent | Parallel traces commute |

### Traced Operation Laws

| Law | Equation | Meaning |
|-----|----------|---------|
| **Semantic Preservation** | `traced_seq(a, b).agent ≅ seq(a, b)` | Tracing doesn't change behavior |
| **Ghost Preservation** | `ghosts(traced_seq(a, b)) ⊇ ghosts(a) ∪ ghosts(b)` | Ghosts accumulate |
| **Lineage Integrity** | `∀ t ∈ traces: t.parent_trace_id ∈ traces ∨ t.parent_trace_id = None` | DAG is well-formed |

### Yanking Axiom (from traced monoidal categories)

```
                     ┌──────────┐
        ─────────────┤          ├─────────────
                     │    f     │
        ─────────────┤          ├─────────────
                     └──────────┘
                          ↕ (yanking)
        ─────────────────────────────────────
                         f
        ─────────────────────────────────────
```

Feedback loops can be "yanked" to simplify without changing semantics.

### Naturality

```
Tr(f ⊗ id_U) = f    (trace of identity feedback is identity)
```

---

## Integration

### AGENTESE Paths

```python
# Trace Operations (time.* context)
time.trace.manifest          # View current trace state
time.trace.witness           # Record a wiring decision
time.trace.at(trace_id)      # Navigate to specific trace
time.trace.ghosts            # All unexplored alternatives
time.trace.heritage(id)      # Ghost heritage DAG for output
time.trace.replay(from_id)   # Re-execute from trace point

# Branch Operations (time.branch.*)
time.branch.create           # Create speculative branch
time.branch.explore(ghost_id) # Execute a ghost alternative
time.branch.compare(a, b)    # Side-by-side comparison
time.branch.merge            # Synthesize parallel branches

# Différance Navigation (self.différance.*)
self.differance.concretize   # Spec → Impl (traced)
self.differance.abstract     # Impl → Spec (reverse)
self.differance.why(id)      # "Why did this happen?"
self.differance.navigate     # Browse spec/impl graph
```

### Composition with Existing Systems

| System | Integration |
|--------|-------------|
| **L-gent Lineage** | Lineage IS a projection of TraceMonoid |
| **N-gent Narrative** | Narrativizes traces into human stories |
| **M-gent Memory** | Holographic compression of trace history |
| **D-gent Persistence** | Event-sourced storage of traces |
| **I-gent Visualization** | Ghost Heritage Graph rendering |
| **Operad** | Traced operations extend AGENT_OPERAD |

### Crown Jewel Integration

Every Crown Jewel gains trace visibility:

```python
# Brain: "Why did this memory crystallize this way?"
await logos("time.trace.heritage", observer, output_id=crystal.id)

# Gardener: "What alternatives were considered for this plot?"
await logos("time.trace.ghosts", observer, scope="world.garden.plot.abc")

# Town: "What coalitions almost formed but didn't?"
await logos("time.branch.compare", observer, chosen=coalition_a, ghost=coalition_b)
```

---

## The Ghost Heritage Graph

### Visual Grammar

```
┌────────────────────────────────────────────────────────────┐
│                   GHOST HERITAGE GRAPH                      │
│                                                             │
│  ○ Spec node       ● Chosen node      ░ Ghost node         │
│  ─ Produced edge   ┄ Ghosted edge     ═ Concretized edge   │
│                                                             │
│  TIME ──────────────────────────────────────────────────▶  │
│                                                             │
│  Spec:    ○───────────────────○                            │
│           │                   │                            │
│           ═                   ═                            │
│           │                   │                            │
│  Impl:    ●───────────────────●                            │
│           │                   │                            │
│           ├───────┬───────────┤                            │
│           │       │           │                            │
│  Branch:  ░      ●           ░                             │
│         ghost  chosen      ghost                           │
│                   │                                        │
│  Output:          ●                                        │
│                (current)                                   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Interaction Affordances

| Action | AGENTESE Path | Effect |
|--------|---------------|--------|
| Expand ghost | `time.branch.explore(ghost_id)` | Execute deferred alternative |
| Compare | `time.branch.compare(a, b)` | Side-by-side diff |
| Navigate up | `time.trace.at(parent_id)` | Move to parent trace |
| Filter ghosts | `time.trace.ghosts(filter=explorable)` | Show only revisitable |
| Collapse | Local UI action | Hide subtree |

---

## Projection Modes

### CLI (Compact)

```
$ kg time.trace.why dec_abc123

▶ dec_abc123: seq(Brain, Gardener)
│ Context: "Cultivate memory"
├── ✓ seq(Brain, Gardener) [CHOSEN]
├── ░ par(Brain, Gardener) [GHOST: "Order matters"]
└── ░ Brain only [GHOST: "Needs pruning"]
    │
    └── Parent: dec_xyz789
```

### JSON (API)

```json
{
  "trace_id": "dec_abc123",
  "operation": "seq",
  "inputs": ["Brain", "Gardener"],
  "output": "BrainGardener",
  "context": "Cultivate memory",
  "alternatives": [
    {"operation": "par", "reason": "Order matters", "explorable": true},
    {"operation": "identity", "reason": "Needs pruning", "explorable": false}
  ],
  "parent_trace_id": "dec_xyz789",
  "heritage_dag_url": "/api/trace/dec_abc123/heritage"
}
```

### Web (Spacious)

Interactive 3D graph with:
- Depth-based layering (spec → impl → branches → output)
- Ghost nodes semi-transparent
- Click to explore, hover to preview
- Timeline scrubber for temporal navigation

---

## Storage

### Event-Sourced Trace Log

```python
class DifferanceStore(Protocol):
    """D-gent adapter for trace persistence."""

    async def append(self, trace: WiringTrace) -> None:
        """Append-only. Never mutate past traces."""
        ...

    async def get(self, trace_id: str) -> WiringTrace | None: ...

    async def query(
        self,
        output_id: str | None = None,
        operation: str | None = None,
        since: datetime | None = None,
        limit: int = 100
    ) -> AsyncIterator[WiringTrace]: ...

    async def heritage_dag(
        self,
        root_id: str,
        depth: int = 10
    ) -> GhostHeritageDAG: ...
```

### Retention Policy

| Trace Type | Default Retention | Configurable |
|------------|-------------------|--------------|
| Chosen paths | Forever | Yes |
| Explorable ghosts | 30 days | Yes |
| Non-explorable ghosts | 7 days | Yes |
| Compressed summaries | Forever | No |

### Privacy

- All traces live in `self.*` context (user-owned)
- Tenant isolation enforced at storage layer
- No cross-tenant trace visibility
- User can export/delete their full trace history

---

## Anti-Patterns

1. **Trace-as-surveillance**: Traces serve the USER, not external monitoring. Never expose traces without user consent.

2. **Unbounded ghost accumulation**: Ghosts must be prunable. Use retention policies and holographic compression.

3. **Trace-without-context**: A trace that says "chose A over B" without WHY is useless. Always capture context.

4. **Ghost-worship**: Not every ghost is worth exploring. Mark non-explorable ghosts clearly.

5. **Semantic pollution**: Tracing should NOT change agent behavior. `traced_seq(a, b).agent ≅ seq(a, b)` must hold.

6. **Orphan traces**: Every trace (except root) must have a valid parent. DAG integrity is mandatory.

---

## Design Decisions

### Why "Différance" not "Trace"?

"Trace" implies passive recording. "Différance" captures the active duality:
- The trace IS the difference (what was chosen vs not)
- The trace IS a deferral (ghosts remain explorable)

### Why extend Operad, not create separate system?

The traced operations ARE wiring diagrams. They belong in the composition grammar, not as a parallel system. This ensures traces compose correctly by construction.

### Why event-sourced storage?

Traces are inherently append-only. Event sourcing is the natural fit. It also enables:
- Replay from any point
- Temporal queries
- Audit compliance

### Why ghosts as first-class citizens?

The alternatives NOT taken are as important as the path taken. They answer "why this and not that?" — the core question of explainability.

---

## Implementation Reference

```
impl/claude/agents/differance/
├── __init__.py
├── trace.py          # TraceMonoid, WiringTrace, Alternative
├── polynomial.py     # DIFFERANCE_POLYNOMIAL
├── operad.py         # TRACED_OPERAD extension
├── store.py          # DifferanceStore (D-gent adapter)
├── heritage.py       # GhostHeritageDAG builder
└── _tests/
    ├── test_trace_monoid.py
    ├── test_traced_operad.py
    ├── test_heritage_dag.py
    └── test_laws.py

impl/claude/protocols/agentese/contexts/
├── time_.py          # Extended with trace.*, branch.*
└── differance.py     # self.differance.* paths

impl/claude/web/src/components/trace/
├── GhostHeritageGraph.tsx
├── TraceTimeline.tsx
└── GhostComparison.tsx
```

---

## Cross-References

- `spec/agents/operads.md` — Base operad that we extend
- `spec/architecture/polyfunctor.md` — Polynomial functor foundation
- `spec/l-gents/lineage.md` — Artifact lineage (projects from traces)
- `spec/protocols/agentese.md` — Path grammar we extend
- `spec/m-gents/holographic.md` — Compression for trace storage
- `spec/n-gents/narrator.md` — Narrativization of traces

---

## Heritage Citations

| Concept | Source | Application |
|---------|--------|-------------|
| Traced monoidal categories | Joyal, Street, Verity (1996) | Feedback loop semantics |
| Polynomial functors | Spivak, Niu (2024) | Wiring diagram foundation |
| Différance | Derrida (1967) | Difference + deferral duality |
| ADR pattern | Nygard (2011) | Decision record structure |
| Event sourcing | Fowler (2005) | Append-only trace storage |

---

*"The ghost heritage graph is the UI innovation: seeing what almost was alongside what is."*

*Last updated: 2025-12-18*
