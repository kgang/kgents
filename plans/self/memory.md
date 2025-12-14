---
path: self/memory
status: active
progress: 75
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [agents/k-gent, interfaces/interaction-flows]
session_notes: |
  Phase 1 (Ghost Cache): COMPLETE - 22 tests
  Phase 2-5 (Crystallization, Stigmergy, Wittgenstein, Active Inference): READY for integration
  Phase 6 (Semantic Routing): COMPLETE - 116 tests
    - SemanticRouter with locality-aware gradient sensing
    - KgentAllocationManager for K→M substrate integration
    - SubstrateScreen for I-gent allocation dashboard
  AGENTESE Four Pillars + Substrate paths wired (17 tests)
  Remaining: Wire to real SharedSubstrate (replace mocks)
---

# Memory Architecture: The Autopoietic Weave

> *"To remember is to participate in a language game."*

**AGENTESE Context**: `self.memory.*`, `time.weave.*`
**Status**: Active (30% complete)
**Principles**: AD-001 (Universal Functor), AD-002 (Polynomial Generalization), Holographic Degradation
**Cross-refs**: `spec/m-gents/`, `docs/research-autopoietic-dynamics.md`, `docs/research-agent-memory-systems.md`

---

## Core Insight

Memory is not storage—it is **autopoietic reconstruction** within the Causal Weave. Four theoretical pillars:

1. **Stigmergy**: Indirect coordination via environmental traces (pheromone fields)
2. **Language Games**: Meaning as use, modeled by polynomial functors
3. **Active Inference**: Self-evidencing via free energy minimization
4. **The Accursed Share**: Entropy as creative force; surplus must be spent

The synthesis: Memory serves **self-evidencing** (maintaining identity through time) while enabling **stigmergic coordination** (collective intelligence without central authority). Language games define **what counts as valid remembering** in context.

---

## Implementation Phases

### Phase 1: Ghost Cache Foundation [COMPLETE]

**Goal**: Basic caching infrastructure for context management.

The Ghost cache provides offline CLI capability:

```
~/.kgents/ghost/
├── status.json         # Last known cortex status
├── map.json            # Last known holoMap
├── agents/             # Per-agent state snapshots
│   └── _index.json
├── pheromones/
│   ├── active.json
│   └── by_type/
│       ├── WARNING.json
│       └── DREAM.json
├── proposals/
│   ├── pending.json
│   └── rejected.json
├── cluster/
│   └── status.json
└── _meta/
    ├── last_sync.txt
    └── stability_score.json
```

**Staleness levels**:
| Level | Age | Behavior |
|-------|-----|----------|
| FRESH | < threshold | Show live |
| STALE | < 2x threshold | Show with `[GHOST]` |
| REFUSE | > 2x threshold | Don't show (misleading) |

**Files**:
```
impl/claude/infra/ghost/collectors.py   # Data collection
impl/claude/protocols/cli/glass.py      # Ghost cache access
impl/claude/agents/d/memory/            # D-gent storage layer
```

**Exit Criteria**: Ghost cache operational, collectors tested. (DONE - Dec 2025)

---

### Phase 2: Memory Crystal Formation [NEXT]

**Goal**: Implement holographic memory with graceful degradation.

**Files**:
```
impl/claude/agents/m/crystal.py        # HolographicMemory implementation
impl/claude/agents/m/consolidator.py   # ConsolidationAgent (hypnagogic)
impl/claude/agents/m/primitives.py     # RecollectionAgent, ProspectiveAgent
impl/claude/agents/m/_tests/           # Test suite
```

**Key Types**:
```python
@dataclass
class StateCrystal:
    """Checkpoint with holographic compression."""
    crystal_id: str
    agent: str
    timestamp: datetime

    # Holographic interference pattern
    interference_pattern: np.ndarray
    resolution: float  # 0.0 to 1.0

    # Focus fragments (PRESERVED: verbatim)
    focus_fragments: list[FocusFragment]

    # Comonadic structure
    parent_crystal: str | None
    branch_depth: int = 0

    # Accursed Share lifecycle
    ttl: timedelta = timedelta(hours=24)
    pinned: bool = False

    def compress(self, ratio: float) -> "StateCrystal":
        """Holographic property: reduce resolution uniformly."""
        ...

@dataclass
class MemoryCrystal:
    """Holographic memory with interference patterns."""
    interference_pattern: np.ndarray
    hot_patterns: set[str]      # Recently accessed
    resolution_levels: dict[str, float]  # Per-concept resolution

    async def store(self, concept: Concept, memory: Memory) -> None:
        """Superimpose on interference pattern."""
        ...

    async def retrieve(self, cue: Concept) -> Recollection:
        """Reconstruct via resonance."""
        ...
```

**Exit Criteria**:
- [ ] HolographicMemory with store/retrieve/compress
- [ ] ConsolidationAgent with hot/cold promotion/demotion
- [ ] Ebbinghaus forgetting curves integrated
- [ ] 50+ tests passing

---

### Phase 3: Stigmergic Layer

**Goal**: Enable indirect coordination via pheromone fields.

**Files**:
```
impl/claude/agents/m/stigmergy.py      # PheromoneField, PheromoneAgent
impl/claude/agents/m/hivemind.py       # HiveMindAgent for collective memory
```

**Key Types**:
```python
@dataclass
class PheromoneField:
    """Environmental memory via traces."""
    traces: dict[Concept, float]
    decay_rate: float = 0.1

    async def deposit(self, concept: Concept, intensity: float):
        """Leave trace (void.tithe integration)."""
        ...

    async def sense(self, position: Concept) -> list[tuple[Concept, float]]:
        """Perceive gradients for navigation."""
        ...

    async def decay(self, elapsed: timedelta):
        """Natural forgetting."""
        ...
```

**Exit Criteria**:
- [ ] PheromoneField with deposit/sense/decay
- [ ] PheromoneAgent following gradients
- [ ] HiveMindAgent achieving consensus from distributed traces
- [ ] Integration with void.tithe (deposits as tithes)
- [ ] 40+ tests passing

---

### Phase 4: Wittgenstein Operator

**Goal**: Implement language games as memory access patterns.

**Files**:
```
impl/claude/agents/m/games.py          # LanguageGame, LanguageGameAgent
impl/claude/agents/m/grammar.py        # GrammarEvolver
```

**Key Types**:
```python
@dataclass
class LanguageGame(Generic[S]):
    """Memory access as playing a game."""
    name: str
    positions: set[S]                    # Valid states
    directions: Callable[[S], set[Direction]]  # Valid moves from state
    rules: Callable[[S, Direction], bool]      # Grammar check

    def is_grammatical(self, position: S, direction: Direction) -> bool:
        """Is this move valid in the game?"""
        return direction in self.directions(position) and self.rules(position, direction)
```

**Exit Criteria**:
- [ ] LanguageGame with polynomial functor structure
- [ ] LanguageGameAgent knowing-how-to-play
- [ ] GrammarEvolver learning from interaction
- [ ] Integration with concept.* AGENTESE paths
- [ ] 40+ tests passing

---

### Phase 5: Active Inference Engine

**Goal**: Memory retrieval as free energy minimization.

**Files**:
```
impl/claude/agents/m/inference.py      # FreeEnergyAgent, SurpriseMinimizer
impl/claude/agents/m/generative.py     # GenerativeModel base
```

**Key Types**:
```python
@dataclass
class GenerativeModel:
    """Agent's beliefs about causal structure."""
    prior: Distribution
    likelihood: Callable[[State, Observation], float]

    def predict(self, state: State) -> Distribution:
        """What observations do I expect?"""
        ...

    def infer(self, observation: Observation) -> Distribution:
        """What states explain this observation?"""
        ...

@dataclass
class FreeEnergyAgent:
    """Memory in service of self-evidencing."""
    model: GenerativeModel
    preferences: Distribution  # Desired states

    async def expected_free_energy(self, policy: Policy) -> float:
        """G = pragmatic value - epistemic value"""
        ...
```

**Exit Criteria**:
- [ ] GenerativeModel with predict/infer
- [ ] FreeEnergyAgent selecting policies
- [ ] SurpriseMinimizer for consolidation
- [ ] 40+ tests passing

---

### Phase 6: Bi-Temporal Store

**Goal**: Separate event-time from knowledge-time.

**Files**:
```
impl/claude/agents/m/temporal.py       # BiTemporalStore, BiTemporalFact
impl/claude/agents/m/archaeology.py    # BeliefArchaeologist
```

**Key Types**:
```python
@dataclass
class BiTemporalFact:
    """Fact with two temporal dimensions."""
    content: Any
    t_event: datetime      # When it happened
    t_known: datetime      # When agent learned it
    superseded_by: Optional[str] = None
```

**Exit Criteria**:
- [ ] BiTemporalStore with point-in-time queries
- [ ] Retroactive correction without history loss
- [ ] BeliefArchaeologist for belief evolution
- [ ] 30+ tests passing

---

### Phase 7: Causal Weave Integration

**Goal**: Memory operations within trace monoid structure.

**Files**:
```
impl/claude/agents/m/weave.py          # TraceMemory, CausalConeAgent
impl/claude/agents/m/knot.py           # KnotAgent for synchronization
impl/claude/weave/memory_integration.py # Wire to existing trace_monoid
```

**Exit Criteria**:
- [ ] TraceMemory respecting partial order
- [ ] CausalConeAgent finding past/future cones
- [ ] KnotAgent merging memory branches
- [ ] Integration with impl/claude/weave/trace_monoid.py
- [ ] 40+ tests passing

---

## AGENTESE Path Registry

| Path | Operation | Description |
|------|-----------|-------------|
| `self.memory.crystallize` | Create checkpoint | Context → Crystal |
| `self.memory.resume` | Restore checkpoint | Crystal → Context |
| `self.memory.cherish` | Pin from reaping | Set pinned=True |
| `self.memory.manifest` | Get cached state | Ghost cache read |
| `self.memory.engram` | Persist state | Ghost cache write |
| `self.memory.compost` | Force expiration | Delete crystal |
| `self.memory.recall` | Reconstruct | Cue → Recollection |
| `world.pheromone.deposit` | Leave trace | Stigmergic coordination |
| `world.pheromone.sense` | Perceive gradients | Navigation |
| `time.weave.causal_cone` | Find causality | Past/future cones |

---

## Cross-Agent Dependencies

| Agent | Role in Memory |
|-------|---------------|
| **D-gent** | Storage layer (UnifiedMemory, VectorAgent) |
| **L-gent** | Embedding space (terrain for cartography) |
| **N-gent** | SemanticTraces (desire lines for navigation) |
| **B-gent** | Economics (token budget for foveation) |
| **K-gent** | Soul integration (memory defines identity) |

---

## Memory Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ Hot Memory (ContextWindow)                              │
│   • Current session                                     │
│   • In-memory, fast                                     │
│   • Compressed via ContextProjector                     │
└───────────────────────────┬─────────────────────────────┘
                            │ crystallize
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Warm Memory (StateCrystals)                             │
│   • Recent checkpoints                                  │
│   • D-gent persistence (etcd/PVC)                       │
│   • TTL-based expiration                                │
│   • Holographic compression                             │
└───────────────────────────┬─────────────────────────────┘
                            │ expire (unpinned)
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Cold Memory (Ghost Cache + Pheromone Fields)            │
│   • CLI-local fallback (~/.kgents/ghost/)               │
│   • Stigmergic traces (collective memory)               │
│   • Staleness-aware                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Chunks (Parallelizable Work)

### Chunk A: Crystal Core (Phase 2)
- HolographicMemory with SVD compression
- Exit: store/retrieve/compress work, 25+ tests

### Chunk B: Consolidation (Phase 2)
- ConsolidationAgent with Ebbinghaus curves
- Exit: hot/cold promotion works, 25+ tests

### Chunk C: Pheromones (Phase 3)
- PheromoneField with decay
- Exit: deposit/sense/decay work, 20+ tests

### Chunk D: Language Games (Phase 4)
- LanguageGame polynomial functor
- Exit: grammar checking works, 20+ tests

---

## Research References

- `docs/research-autopoietic-dynamics.md` — Synthesis of Four Pillars
- `docs/research-agent-memory-systems.md` — Survey of existing systems
- `docs/kgents_ A Next-Generation Agentic Memory Architecture.pdf` — Trace Monoid theory
- `spec/m-gents/README.md` — M-gent specification

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Test count | 300+ |
| Holographic property | 50% compression → 50% resolution (not 50% data loss) |
| Stigmergic convergence | Consensus in < 10 iterations |
| Language game coverage | 5+ games defined |
| Bi-temporal queries | Point-in-time accuracy 100% |

---

*"Memory is the performance of identity across time."*
