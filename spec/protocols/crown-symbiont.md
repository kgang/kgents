# Crown Symbiont Protocol

**Mapping Crown Jewel surface handlers to canonical D-gent infrastructure.**

> *"The surface is for experience; the substrate is for memory."*

**Status:** Specification v1.0
**Date:** 2025-12-16
**Prerequisites:** `../d-gents/symbiont.md`, `../d-gents/vision.md`, `../protocols/agentese.md`
**Integrations:** Crown Jewels, D-gent Noosphere (TemporalWitness, SemanticManifold, RelationalLattice)
**Guard [phase=PLAN][entropy=0.07][law_check=true]:** Every surface handler wraps a Symbiont; D-gent triple provides persistence, history, projections.

---

## Purpose

The Seven Crown Jewels define AGENTESE paths in `crown_jewels.py` for:
1. Atelier Experience (Flux)
2. Coalition Forge (Operad)
3. Holographic Brain (Sheaf)
4. Punchdrunk Park (Polynomial)
5. Domain Simulation (Tenancy)
6. Gestalt Visualizer (Reactive)
7. The Gardener (N-Phase)

Currently these paths have **declarative metadata** but lack unified **persistence infrastructure**. Each path needs:
- **Event sourcing** (TemporalWitness) — What happened and when
- **Semantic grounding** (SemanticManifold) — Where in meaning-space
- **Relational structure** (RelationalLattice) — How things connect

This spec defines the **Crown Symbiont Protocol**: wrapping every Crown Jewel surface handler in a Symbiont that fuses pure logic with the D-gent triple.

---

## The Core Insight

> **Surface handlers remain pure; D-gent infrastructure handles all state.**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       CROWN SYMBIONT ARCHITECTURE                              │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                     SURFACE LAYER (Pure Logic)                           │  │
│  │   world.atelier.manifest   self.memory.recall   time.simulation.witness │  │
│  │   ────────────────────────────────────────────────────────────────────── │  │
│  │   Observer × Intent → Response (no side effects)                        │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                    ↕ Symbiont Fusion                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │                    D-GENT TRIPLE (State Infrastructure)                  │  │
│  │  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────────┐  │  │
│  │  │ TemporalWitness   │ │ SemanticManifold  │ │ RelationalLattice     │  │  │
│  │  │ ─────────────────  │ │ ─────────────────  │ │ ─────────────────────  │  │  │
│  │  │ • Event stream     │ │ • Vector space     │ │ • Graph structure     │  │  │
│  │  │ • Drift detection  │ │ • Curvature        │ │ • Lattice operations  │  │  │
│  │  │ • Momentum         │ │ • Voids (Ma)       │ │ • Lineage tracking    │  │  │
│  │  │ • Entropy          │ │ • Geodesics        │ │ • Entailment          │  │  │
│  │  └───────────────────┘ └───────────────────┘ └───────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part I: The Crown Symbiont

### 1.1 Definition

```python
from dataclasses import dataclass, field
from typing import Generic, TypeVar, Callable, Any

from agents.d.symbiont import Symbiont
from agents.d.witness import TemporalWitness
from agents.d.manifold import SemanticManifold
from agents.d.lattice import RelationalLattice

I = TypeVar("I")  # Input
O = TypeVar("O")  # Output
S = TypeVar("S")  # State

@dataclass
class CrownSymbiont(Generic[I, O, S]):
    """
    Wraps a Crown Jewel surface handler with D-gent infrastructure.

    The logic function remains pure: (I, S) → (O, S)
    The D-gent triple provides:
        - TemporalWitness: Event sourcing, drift detection, momentum
        - SemanticManifold: Embeddings, curvature, voids
        - RelationalLattice: Graph structure, lineage, entailment

    Principle: Surface handlers are pure projections of state;
               the D-gent triple IS the state.
    """

    # The pure handler logic
    logic: Callable[[I, S], tuple[O, S]]

    # The D-gent triple
    witness: TemporalWitness[Any, S]   # Events + time
    manifold: SemanticManifold[S]       # Vectors + geometry
    lattice: RelationalLattice[S]       # Graph + lineage

    # Internal symbiont for composition
    _symbiont: Symbiont[I, O, S] = field(init=False)

    def __post_init__(self):
        """Wire the symbiont with triple-backed memory."""
        self._symbiont = Symbiont(
            logic=self._wrap_with_triple(),
            memory=TripleBackedMemory(
                witness=self.witness,
                manifold=self.manifold,
                lattice=self.lattice,
            )
        )

    def _wrap_with_triple(self) -> Callable[[I, S], tuple[O, S]]:
        """Wrap logic to record events and update embeddings."""
        original_logic = self.logic

        def wrapped(input_data: I, state: S) -> tuple[O, S]:
            # 1. Execute pure logic
            output, new_state = original_logic(input_data, state)

            # 2. Side-effect: Record to witness (event sourcing)
            # 3. Side-effect: Update manifold (embedding)
            # 4. Side-effect: Update lattice (relationships)
            # These happen in TripleBackedMemory.save()

            return output, new_state

        return wrapped

    async def invoke(self, input_data: I) -> O:
        """Execute via symbiont."""
        return await self._symbiont.invoke(input_data)

    # === Temporal Affordances (from Witness) ===

    async def event_stream(self, window: timedelta | None = None) -> list[Any]:
        """Get event history."""
        return await self.witness.timeline(window or timedelta(hours=1))

    async def detect_drift(self, trajectory: str) -> DriftReport:
        """Detect behavioral drift."""
        return await self.witness.check_drift(trajectory)

    async def momentum(self) -> Vector:
        """Semantic velocity of state."""
        return await self.witness.momentum()

    # === Semantic Affordances (from Manifold) ===

    async def neighbors(self, state: S, radius: float = 0.5) -> list[S]:
        """Find semantically similar states."""
        point = await self.manifold.embed(state)
        return await self.manifold.neighbors(point, radius)

    async def curvature_at(self, state: S) -> float:
        """Local semantic complexity."""
        point = await self.manifold.embed(state)
        return await self.manifold.curvature_at(point)

    async def voids_nearby(self, state: S) -> list[SemanticVoid]:
        """Find unexplored regions (generative potential)."""
        point = await self.manifold.embed(state)
        return await self.manifold.void_nearby(point)

    # === Relational Affordances (from Lattice) ===

    async def lineage(self, node_id: str) -> list[str]:
        """Get ancestry chain (provenance)."""
        return await self.lattice.lineage(node_id)

    async def meet(self, a: str, b: str) -> str | None:
        """Greatest common sub-state."""
        result = await self.lattice.meet(a, b)
        return result.node_id if result.found else None

    async def join(self, a: str, b: str) -> str | None:
        """Least common super-state."""
        result = await self.lattice.join(a, b)
        return result.node_id if result.found else None
```

### 1.2 The Triple-Backed Memory

```python
@dataclass
class TripleBackedMemory(DataAgent[S], Generic[S]):
    """
    Memory backed by the D-gent triple.

    load() reconstructs state from latest witness event.
    save() records event, updates embedding, updates lattice.
    """

    witness: TemporalWitness[Any, S]
    manifold: SemanticManifold[S]
    lattice: RelationalLattice[S]

    async def load(self) -> S:
        """Load current state from witness."""
        return await self.witness.current_state()

    async def save(self, state: S) -> None:
        """Save state to all three components."""
        # 1. Event sourcing (Witness)
        await self.witness.observe(
            event=state,
            witness=WitnessReport(
                observer_id="crown_symbiont",
                timestamp=datetime.now(),
                confidence=1.0,
            )
        )

        # 2. Semantic embedding (Manifold)
        point = await self.manifold.embed(state)
        await self.manifold.store(
            id=str(hash(state)),
            point=point,
            state=state,
        )

        # 3. Relational update (Lattice)
        # Derive node_id and relationships from state
        node_id = self._state_to_node_id(state)
        await self.lattice.add(node_id, state)

        # Link to previous state (lineage)
        prev_id = await self._previous_node_id()
        if prev_id:
            await self.lattice.relate(
                source=node_id,
                edge=EdgeKind.DERIVED_FROM,
                target=prev_id,
            )

    async def history(self, limit: int | None = None) -> list[S]:
        """Get state history from witness."""
        timeline = await self.witness.timeline(timedelta(days=7))
        states = [entry.state for entry in timeline]
        return states[:limit] if limit else states
```

---

## Part II: Crown Path → D-gent Triple Mapping

### 2.1 The `self.*` Context Paths

| Crown Path | Jewel | Witness Usage | Manifold Usage | Lattice Usage |
|------------|-------|---------------|----------------|---------------|
| `self.memory.manifest` | Brain | View event stream | Show memory topology | Display memory graph |
| `self.memory.capture` | Brain | Record capture event | Embed content | Link to related |
| `self.memory.recall` | Brain | Query event timeline | Semantic search | Graph traversal |
| `self.memory.ghost.surface` | Brain | Drift detection | Curvature check | Orphan detection |
| `self.tokens.manifest` | Atelier | Balance history | — | Token relationships |
| `self.tokens.purchase` | Atelier | Purchase event | — | Link to session |
| `self.credits.manifest` | Coalition | Credit history | — | Credit allocation |
| `self.consent.manifest` | Park | Consent history | — | Force/apology graph |
| `self.consent.force` | Park | Force event | — | Apology linkage |
| `self.forest.manifest` | Gardener | Plan evolution | — | Plan dependencies |
| `self.forest.evolve` | Gardener | Evolution event | — | Proposal linkage |
| `self.meta.append` | Gardener | Meta event | Semantic index | — |

### 2.2 The `time.*` Context Paths

| Crown Path | Jewel | Witness Usage | Manifold Usage | Lattice Usage |
|------------|-------|---------------|----------------|---------------|
| `time.inhabit.witness` | Park | Session replay | — | Character graph |
| `time.simulation.witness` | Simulation | Audit replay | — | Event causality |
| `time.simulation.export` | Simulation | Export events | — | Compliance graph |

### 2.3 Complete Self/Time Path Registry

```python
CROWN_DGENT_MAPPINGS: dict[str, CrownTripleConfig] = {
    # === self.memory.* (Brain) ===
    "self.memory.manifest": CrownTripleConfig(
        witness_aspect="timeline",     # Show recent events
        manifold_aspect="topology",    # Memory curvature map
        lattice_aspect="graph",        # Memory relationships
    ),
    "self.memory.capture": CrownTripleConfig(
        witness_aspect="record",       # Log capture event
        manifold_aspect="embed",       # Create embedding
        lattice_aspect="link",         # Link to related
    ),
    "self.memory.recall": CrownTripleConfig(
        witness_aspect="query",        # Find in history
        manifold_aspect="search",      # Semantic retrieval
        lattice_aspect="traverse",     # Follow relationships
    ),
    "self.memory.ghost.surface": CrownTripleConfig(
        witness_aspect="drift",        # Detect forgotten patterns
        manifold_aspect="voids",       # Find semantic gaps
        lattice_aspect="orphans",      # Find disconnected nodes
    ),

    # === self.tokens.* (Atelier) ===
    "self.tokens.manifest": CrownTripleConfig(
        witness_aspect="timeline",
        manifold_aspect=None,
        lattice_aspect="balance_graph",
    ),
    "self.tokens.purchase": CrownTripleConfig(
        witness_aspect="record",
        manifold_aspect=None,
        lattice_aspect="session_link",
    ),

    # === self.credits.* (Coalition) ===
    "self.credits.manifest": CrownTripleConfig(
        witness_aspect="timeline",
        manifold_aspect=None,
        lattice_aspect="allocation_graph",
    ),

    # === self.consent.* (Park) ===
    "self.consent.manifest": CrownTripleConfig(
        witness_aspect="history",
        manifold_aspect=None,
        lattice_aspect="consent_chain",
    ),
    "self.consent.force": CrownTripleConfig(
        witness_aspect="record",
        manifold_aspect=None,
        lattice_aspect="apology_link",
    ),

    # === self.forest.* (Gardener) ===
    "self.forest.manifest": CrownTripleConfig(
        witness_aspect="evolution",
        manifold_aspect=None,
        lattice_aspect="dependency_graph",
    ),
    "self.forest.evolve": CrownTripleConfig(
        witness_aspect="record",
        manifold_aspect=None,
        lattice_aspect="proposal_chain",
    ),

    # === self.meta.* (Gardener) ===
    "self.meta.append": CrownTripleConfig(
        witness_aspect="record",
        manifold_aspect="semantic_index",
        lattice_aspect=None,
    ),

    # === time.inhabit.* (Park) ===
    "time.inhabit.witness": CrownTripleConfig(
        witness_aspect="replay",
        manifold_aspect=None,
        lattice_aspect="character_graph",
    ),

    # === time.simulation.* (Simulation) ===
    "time.simulation.witness": CrownTripleConfig(
        witness_aspect="replay",
        manifold_aspect=None,
        lattice_aspect="causality_graph",
    ),
    "time.simulation.export": CrownTripleConfig(
        witness_aspect="export",
        manifold_aspect=None,
        lattice_aspect="compliance_graph",
    ),
}
```

---

## Part III: The Symbiont Wrapper Pattern

### 3.1 Wrapping an Existing Handler

```python
# Before: Pure handler without persistence
async def memory_capture_logic(
    input_data: CaptureInput,
    state: MemoryState,
) -> tuple[CaptureResult, MemoryState]:
    """Pure logic for self.memory.capture."""
    # Embed content
    embedding = embed(input_data.content)

    # Create crystal
    crystal = MemoryCrystal(
        content=input_data.content,
        embedding=embedding,
        timestamp=datetime.now(),
    )

    # Update state (immutable)
    new_state = state.with_crystal(crystal)

    return CaptureResult(crystal_id=crystal.id), new_state


# After: Wrapped with D-gent triple
memory_capture_symbiont = CrownSymbiont(
    logic=memory_capture_logic,
    witness=TemporalWitness(fold=memory_fold, initial=MemoryState()),
    manifold=SemanticManifold(dimension=768),
    lattice=RelationalLattice(persistence_path="data/memory_lattice.json"),
)

# The CrownSymbiont automatically:
# 1. Records event to witness on each invocation
# 2. Updates embedding in manifold
# 3. Maintains lineage in lattice
```

### 3.2 Handler Factory

```python
def create_crown_symbiont(
    path: str,
    logic: Callable[[I, S], tuple[O, S]],
    initial_state: S,
) -> CrownSymbiont[I, O, S]:
    """
    Factory for creating CrownSymbionts from handlers.

    Automatically configures D-gent triple based on path.
    """
    config = CROWN_DGENT_MAPPINGS.get(path)
    if not config:
        raise ValueError(f"No D-gent mapping for path: {path}")

    # Create triple components
    witness = TemporalWitness(
        fold=lambda s, e: e,  # Simple event replacement
        initial=initial_state,
    ) if config.witness_aspect else None

    manifold = SemanticManifold(
        dimension=768,
    ) if config.manifold_aspect else None

    lattice = RelationalLattice(
        persistence_path=f"data/{path.replace('.', '_')}_lattice.json",
    ) if config.lattice_aspect else None

    return CrownSymbiont(
        logic=logic,
        witness=witness,
        manifold=manifold,
        lattice=lattice,
    )
```

---

## Part IV: Projections from the D-gent Triple

### 4.1 The Projection Protocol

Each D-gent triple component provides distinct projections:

```python
class TripleProjection:
    """
    Projections available from the D-gent triple.

    Aligned with the Projection Protocol (spec/protocols/projection.md).
    """

    # === Temporal Projections (from Witness) ===

    async def project_timeline(self, window: timedelta) -> TimelineView:
        """Event timeline visualization."""
        ...

    async def project_drift(self, trajectories: list[str]) -> DriftView:
        """Behavioral drift dashboard."""
        ...

    async def project_momentum(self) -> MomentumView:
        """Semantic velocity indicator."""
        ...

    # === Semantic Projections (from Manifold) ===

    async def project_topology(self) -> TopologyView:
        """2D/3D semantic space visualization."""
        ...

    async def project_curvature(self) -> CurvatureMap:
        """Heatmap of semantic complexity."""
        ...

    async def project_voids(self) -> VoidExplorer:
        """Interactive void (Ma) discovery."""
        ...

    # === Relational Projections (from Lattice) ===

    async def project_graph(self, root: str | None = None) -> GraphView:
        """Interactive knowledge graph."""
        ...

    async def project_lineage(self, node_id: str) -> LineageView:
        """Provenance chain visualization."""
        ...

    async def project_lattice(self) -> LatticeView:
        """Full lattice structure with meet/join."""
        ...
```

### 4.2 Cross-Projection Synthesis

```python
async def project_holographic(
    symbiont: CrownSymbiont,
    focus: str | None = None,
) -> HolographicView:
    """
    Synthesize all three D-gent projections.

    The holographic view shows:
    - Temporal layer: Events flowing through time
    - Semantic layer: Embeddings in curved space
    - Relational layer: Graph structure beneath

    These three layers are ALWAYS consistent because
    they derive from the same CrownSymbiont state.
    """
    return HolographicView(
        temporal=await symbiont.project_timeline(timedelta(days=7)),
        semantic=await symbiont.project_topology(),
        relational=await symbiont.project_graph(root=focus),
    )
```

---

## Part V: Category Laws

### 5.1 Symbiont Composition

CrownSymbionts compose like regular Symbionts:

```python
# Pipeline: capture → index → crystallize
pipeline = (
    memory_capture_symbiont
    >> semantic_index_symbiont
    >> crystallization_symbiont
)

# Each stage:
# 1. Loads state from its D-gent triple
# 2. Applies pure logic
# 3. Saves state to its D-gent triple
```

### 5.2 Triple Coherence Laws

**Law 1: Temporal Consistency**
```
∀ events e₁, e₂ in Witness:
  e₁.timestamp < e₂.timestamp ⟹
    Lattice.lineage(e₂.state) contains e₁.state_id
```

**Law 2: Semantic Continuity**
```
∀ consecutive states s₁, s₂:
  Manifold.distance(s₁, s₂) < δ (bounded change)
```

**Law 3: Relational Integrity**
```
∀ node n in Lattice:
  n.derived_from is null ⟹ n is root
  n.derived_from is not null ⟹ edge(n, n.derived_from) exists
```

---

## Part VI: Integration with Crown Jewels

### 6.1 Atelier (Flux)

```python
# Atelier session state backed by triple
atelier_symbiont = CrownSymbiont(
    logic=atelier_session_logic,
    witness=TemporalWitness(...),   # Stream of bids, tithes
    manifold=SemanticManifold(...), # Creation embeddings
    lattice=RelationalLattice(...), # Session → purchases graph
)
```

### 6.2 Brain (Sheaf)

```python
# Brain memory state backed by triple
brain_symbiont = CrownSymbiont(
    logic=brain_memory_logic,
    witness=TemporalWitness(...),   # Capture/recall events
    manifold=SemanticManifold(...), # Memory crystal embeddings
    lattice=RelationalLattice(...), # Crystal → crystal associations
)
```

### 6.3 Simulation (Tenancy)

```python
# Simulation state backed by triple
simulation_symbiont = CrownSymbiont(
    logic=simulation_logic,
    witness=TemporalWitness(...),   # Simulation events (audit log)
    manifold=None,                   # Simulations not embedded
    lattice=RelationalLattice(...), # Event causality graph
)
```

---

## Part VII: Anti-patterns

1. **Bypassing the Symbiont**: Directly accessing D-gent components breaks coherence laws.
   - *Correction*: Always invoke through CrownSymbiont.

2. **State mutation in logic**: Mutating state directly instead of returning new state.
   - *Correction*: Logic is pure; return (output, new_state).

3. **Missing triple component**: Using CrownSymbiont with null witness/manifold/lattice when path requires it.
   - *Correction*: Consult CROWN_DGENT_MAPPINGS for required components.

4. **Ignoring projections**: Not exposing D-gent triple affordances through AGENTESE.
   - *Correction*: Every `*.manifest` should include triple projections.

---

## Part VIII: Success Criteria

A Crown Symbiont is well-designed if:

- ✓ **Pure Logic**: Handler function has no side effects
- ✓ **Triple-Backed**: State persisted to all applicable D-gent components
- ✓ **Law-Compliant**: Temporal, semantic, and relational laws hold
- ✓ **Composable**: Works with >> operator
- ✓ **Projectable**: All three projections available via AGENTESE
- ✓ **Cross-Jewel Consistent**: Same pattern across all seven Crown Jewels

---

## Files to Create

```
impl/claude/protocols/agentese/contexts/
├── crown_symbiont.py          # CrownSymbiont class
├── triple_backed_memory.py    # TripleBackedMemory implementation
├── crown_mappings.py          # CROWN_DGENT_MAPPINGS registry
└── _tests/
    ├── test_crown_symbiont.py
    └── test_triple_backed_memory.py

impl/claude/agents/d/
├── (existing: manifold.py, witness.py, lattice.py, symbiont.py)
└── triple.py                  # Unified triple factory
```

---

## See Also

- [../d-gents/symbiont.md](../d-gents/symbiont.md) - Symbiont pattern
- [../d-gents/vision.md](../d-gents/vision.md) - Noosphere architecture
- [../protocols/agentese.md](../protocols/agentese.md) - AGENTESE specification
- [../protocols/projection.md](../protocols/projection.md) - Projection protocol
- `impl/claude/protocols/agentese/contexts/crown_jewels.py` - Crown Jewel paths
