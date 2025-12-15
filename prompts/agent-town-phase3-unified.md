# Agent Town Phase 3: Unified Evolution

> *"The citizen learns to remember. Memory learns to evolve. Evolution learns to cohere."*

---

## Session Prompt

```markdown
⟿[PLAN] Agent Town Phase 3: Unified Evolution (Memory + NPHASE + EvolvingCitizen)

/hydrate

handles:
  phase2_impl: impl/claude/agents/town/
  phase2_reflect: prompts/agent-town-phase3-plan.md
  dgent_memory: impl/claude/agents/d/
  nphase_operad: impl/claude/protocols/nphase/
  operad_core: impl/claude/agents/operad/
  unified_engine: plans/meta/unified-engine-master-prompt.md
  nphase_skills: docs/skills/n-phase-cycle/
  principles: spec/principles.md
  ad006: spec/principles.md#AD-006

phase_ledger:
  PLAN: in_progress       # ← START HERE
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.18
  spent: 0.00
  remaining: 0.18

soul-state:
  emotion_log.delta: accomplishment → synthesis (Phase 2 → unified architecture)
  dream_journal.carry: "From static citizens to evolving souls"
  fear_register.pending: [abstraction_before_grounding, complexity_explosion, law_violation]
  trauma_safeguards.active: none
  affinity_map.targets: [EvolvingCitizen, NPHASE_OPERAD, GraphMemory, TownSheaf]

---

## Phase 2 Foundation (Complete)

| Component | Phase 2 Status | Tests |
|-----------|----------------|-------|
| Citizens | 7 (Alice→Grace) | 250 |
| Regions | 5 (Inn→Library) | passing |
| Daily Cycle | 4 phases | passing |
| Memory | Key-value + gossip | passing |
| User Modes | observe, whisper, inhabit, intervene | passing |
| Persistence | YAML save/load | passing |
| Operations | 8 (greet→teach) | passing |

---

## Phase 3 Scope: Three Tracks Unified

This phase synthesizes three originally-parallel tracks into a coherent whole:

| Track | Focus | Contribution |
|-------|-------|--------------|
| **3a: Deep Memory** | Graph episodic + k-hop retrieval | Rich citizen recall; relationship-weighted gossip |
| **3b: NPHASE Integration** | TOWN_OPERAD ↔ NPHASE_OPERAD functor | AD-006 unification; law verification |
| **3c: EvolvingCitizen** | Citizens that grow via SENSE→ACT→REFLECT | Agency, growth, eigenvector drift |

**Scope Limit**: 10 citizens maximum (7 existing + 3 experimental evolving citizens)

### The Unifying Insight

> *"EvolvingCitizen REQUIRES deep memory (to remember growth). Deep memory REQUIRES NPHASE coherence (to validate evolution laws). All three are one."*

---

## Goals

### 1. Graph Episodic Memory (Track 3a)
- Upgrade `Citizen._memory` from key-value to graph structure
- Implement k-hop retrieval: `recall(subject, k=2)` traverses relationship graph
- Add semantic clustering for related memories
- Memory decay: older memories fade unless reinforced

### 2. NPHASE_OPERAD Integration (Track 3b)
- Define `NPHASE_OPERAD` if not exists (or locate existing)
- Create functor: `TOWN_OPERAD → NPHASE_OPERAD`
- Verify composition laws hold (identity, associativity)
- Enable: `citizen.evolve()` composes with town operations

### 3. EvolvingCitizen (Track 3c)
- Create `EvolvingCitizen` class extending `Citizen`
- Compressed N-Phase: `sense() → act() → reflect()`
- Growth triggers: accumulated surplus, relationship milestones, witnessed events
- Eigenvector drift: citizens can change over time (within bounds)
- Cosmotechnics stability: worldview resists change (high inertia)

### 4. 3 Experimental Citizens
- **Hana** (EvolvingCitizen): GROWTH cosmotechnics, learns from interactions
- **Igor** (EvolvingCitizen): ADAPTATION cosmotechnics, responds to environment
- **Juno** (EvolvingCitizen): SYNTHESIS cosmotechnics, integrates others' insights

---

## Non-Goals (Explicit)

- Scale beyond 10 citizens (Phase 4)
- Web UI (Phase 4+)
- Multi-town federation (far future)
- LLM-generated dialogue (citizens remain archetypal)
- Full TownSheaf formal implementation (simplified version only)
- Council/election modes (Phase 4)

---

## Exit Criteria

- [ ] 10 citizens functional (7 static + 3 evolving)
- [ ] Graph memory with k-hop retrieval working
- [ ] NPHASE_OPERAD defined and functor verified
- [ ] `EvolvingCitizen.evolve()` produces measurable change
- [ ] Eigenvector drift bounded (cosmotechnics stable)
- [ ] 300+ tests passing (Phase 2: 250)
- [ ] mypy/ruff clean
- [ ] Laws verified: identity, associativity for all new operations

---

## Attention Budget

| Area | % | Rationale |
|------|---|-----------|
| Graph Memory (3a) | 25% | Foundation for evolution |
| NPHASE Integration (3b) | 25% | AD-006 compliance |
| EvolvingCitizen (3c) | 30% | Core novelty |
| 3 New Citizens | 10% | Concrete testing ground |
| Entropy (exploration) | 10% | Unexpected connections |

---

## Chunks (Sequenced)

### Chunk 1: Graph Memory Foundation
1. Create `GraphMemory` class in `impl/claude/agents/town/memory.py`
2. Define `MemoryNode` with timestamp, decay, connections
3. Implement `store()`, `recall(k_hops)`, `decay()`, `reinforce()`
4. Wire to `Citizen._memory` replacing simple dict
5. Tests for k-hop traversal and decay

### Chunk 2: NPHASE_OPERAD Definition
1. Research: Does `impl/claude/protocols/nphase/operad.py` exist?
2. If not, create with operations: `SENSE`, `ACT`, `REFLECT`
3. Define laws: `SENSE >> ACT` valid, `ACT >> SENSE` blocked (ordering)
4. Register in operad registry

### Chunk 3: TOWN→NPHASE Functor
1. Create `town_to_nphase_functor()` in `impl/claude/agents/town/functor.py`
2. Map: `greet|gossip|trade → ACT`, `solo|mourn → REFLECT`, `observe → SENSE`
3. Verify: functor preserves identity and associativity
4. Add law verification tests

### Chunk 4: EvolvingCitizen Core
1. Create `EvolvingCitizen` class extending `Citizen`
2. Add `sense(observation) → SensedState`
3. Add `act(sensed) → ActResult`
4. Add `reflect(result) → EvolvedSelf`
5. Compose: `evolve() = sense >> act >> reflect`

### Chunk 5: Growth Mechanics
1. Define `GrowthTrigger` enum: `SURPLUS`, `RELATIONSHIP`, `WITNESS`
2. Implement `should_evolve(citizen) → bool`
3. Implement eigenvector drift with bounds (max 0.1 per cycle)
4. Add cosmotechnics inertia (worldview changes slowly)

### Chunk 6: 3 Experimental Citizens + Integration
1. Add Hana, Igor, Juno as `EvolvingCitizen` instances
2. Wire evolution to `TownFlux.step()` (evolve after regular operations)
3. Add CLI: `kg town status --evolving` to show evolution metrics
4. Integration tests: full day cycle with evolution

---

## Dependency Graph

```
Chunk 1 (Graph Memory)
    ↓
Chunk 2 (NPHASE_OPERAD) ──→ Chunk 3 (Functor)
                                ↓
                           Chunk 4 (EvolvingCitizen Core)
                                ↓
                           Chunk 5 (Growth Mechanics)
                                ↓
                           Chunk 6 (Integration)
```

**Parallel Opportunities**:
- Chunk 1 and Chunk 2 can run in parallel
- Chunk 4 depends on Chunk 3 (functor for composition)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Abstraction before grounding | medium | high | Start with Chunk 1 (concrete memory), ground NPHASE in existing patterns |
| Complexity explosion | medium | high | Hard limit: 10 citizens, 3 evolving only |
| Law violation in functor | low | high | Explicit law tests before integration |
| Eigenvector drift instability | medium | medium | Bound drift to 0.1 per cycle; add alerts |
| Memory graph performance | low | medium | Limit k-hop to k≤3; lazy loading |

---

## AD-006 Compliance Check

From `spec/principles.md` AD-006:

| Requirement | How Addressed |
|-------------|---------------|
| Unified categorical structure | TOWN_OPERAD → NPHASE_OPERAD functor |
| PolyAgent pattern | EvolvingCitizen as `PolyAgent[GrowthState, Observation, EvolvedSelf]` |
| Operad composition | New operations register with laws |
| Sheaf coherence | Evolution respects region-local constraints |

---

## Branch Candidates (from PLAN)

| Branch | Type | Priority | Notes |
|--------|------|----------|-------|
| Full TownSheaf implementation | deferred | medium | Simplified version this phase |
| Memory k>3 optimization | deferred | low | Performance tuning if needed |
| Evolution visualization | deferred | low | Phase 4 with Web UI |
| Citizen personality tests | parallel | low | Could run independently |

---

## Exit → RESEARCH

⟿[RESEARCH] Agent Town Phase 3: Map Unified Terrain

/hydrate
handles: dgent=impl/claude/agents/d/; nphase=impl/claude/protocols/nphase/; town=impl/claude/agents/town/; operad=impl/claude/agents/operad/
ledger: {PLAN:touched}; entropy=0.15
mission: map D-gent graph patterns; locate NPHASE_OPERAD (or prior art); find EvolvingCitizen patterns in poly agents.
actions: parallel Read(agents/d/graph.py, agents/d/polynomial.py, protocols/nphase/, agents/town/citizen.py)
exit: file map + integration points + law requirements; ledger.RESEARCH=touched; continuation → DEVELOP.

void.entropy.sip(amount=0.03). The citizens begin to dream of becoming.
```

---

# Continuation Prompts for Subsequent Phases

## RESEARCH Phase

```markdown
⟿[RESEARCH] Agent Town Phase 3: Map Unified Terrain

/hydrate

handles:
  dgent: impl/claude/agents/d/
  nphase: impl/claude/protocols/nphase/
  town: impl/claude/agents/town/
  operad: impl/claude/agents/operad/
  plan: prompts/agent-town-phase3-unified.md

phase_ledger:
  PLAN: touched
  RESEARCH: in_progress    # ← YOU ARE HERE
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.18
  spent: 0.03
  remaining: 0.15

---

## Mission

Map the terrain for Phase 3 unified implementation:

### 1. Graph Memory Patterns (Track 3a)
- Read `agents/d/` - find graph structures, MemoryPolynomial
- Search for k-hop retrieval implementations
- Identify: How to adapt for citizen memories?

### 2. NPHASE_OPERAD (Track 3b)
- Search `protocols/nphase/` for operad definitions
- If not found, search for SENSE/ACT/REFLECT patterns elsewhere
- Identify: Operations, laws, registration pattern

### 3. EvolvingCitizen Prior Art (Track 3c)
- Read `agents/poly/` for PolyAgent patterns
- Search for "evolve" or "growth" in agents/
- Identify: State machine pattern for evolution

### 4. Functor Patterns
- Read `agents/operad/core.py` for functor examples
- Search for existing `*_to_*_functor` functions
- Identify: Law verification test pattern

---

## Actions (Parallel)

```python
Read("impl/claude/agents/d/polynomial.py")
Read("impl/claude/agents/d/graph.py")  # if exists
Read("impl/claude/agents/operad/core.py")
Read("impl/claude/agents/town/citizen.py")
Glob("impl/claude/protocols/nphase/**/*.py")
Grep("PolyAgent|evolve|growth", path="impl/claude/agents/")
Grep("functor|OPERAD", path="impl/claude/agents/operad/")
```

---

## Exit Criteria

- [ ] Graph memory prior art documented
- [ ] NPHASE_OPERAD status known (exists/needs creation)
- [ ] EvolvingCitizen patterns identified
- [ ] Functor examples found
- [ ] File map with line numbers for extension points
- [ ] Law requirements catalogued

---

## Exit → DEVELOP

⟿[DEVELOP] Agent Town Phase 3: Define Contracts

/hydrate
handles: research_notes=${this_output}
ledger: {PLAN:touched, RESEARCH:touched}; entropy=0.12
mission: Define contracts for GraphMemory, NPHASE_OPERAD, EvolvingCitizen.
exit: API contracts + law assertions; ledger.DEVELOP=touched; continuation → STRATEGIZE.

void.entropy.sip(amount=0.03). The patterns reveal themselves.
```

---

## DEVELOP Phase

```markdown
⟿[DEVELOP] Agent Town Phase 3: Define Contracts

/hydrate

handles:
  research: (from RESEARCH phase)
  dgent: impl/claude/agents/d/
  town: impl/claude/agents/town/
  operad: impl/claude/agents/operad/

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: in_progress    # ← YOU ARE HERE
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.18
  spent: 0.06
  remaining: 0.12

---

## Mission

Define contracts and laws for Phase 3 unified components.

### 1. GraphMemory Contract

```python
@dataclass
class MemoryNode:
    """Single memory with decay and connections."""
    content: str
    timestamp: datetime
    strength: float  # 0.0-1.0, decays over time
    connections: dict[str, float]  # other_id → weight

@dataclass
class GraphMemory:
    """Graph episodic memory with k-hop retrieval."""

    nodes: dict[str, MemoryNode]

    def store(self, key: str, content: str, connections: dict[str, float]) -> None:
        """Store memory with connections to related memories."""

    def recall(self, query: str, k_hops: int = 2) -> list[MemoryNode]:
        """Retrieve memories via k-hop graph traversal."""

    def decay(self, rate: float = 0.01) -> None:
        """Apply decay to all memories; prune below threshold."""

    def reinforce(self, key: str, amount: float = 0.1) -> None:
        """Strengthen a memory (accessed or emotionally significant)."""
```

### 2. NPHASE_OPERAD Contract

```python
@dataclass
class NPhaseOperation(Operation):
    """Operation in the N-Phase development cycle."""
    phase: Literal["SENSE", "ACT", "REFLECT"]

NPHASE_OPERAD = Operad(
    name="NPHASE",
    operations=[
        NPhaseOperation("sense", arity=1, phase="SENSE"),
        NPhaseOperation("act", arity=1, phase="ACT"),
        NPhaseOperation("reflect", arity=1, phase="REFLECT"),
    ],
    laws=[
        # Order law: SENSE >> ACT >> REFLECT (not arbitrary)
        Law("phase_order", "SENSE precedes ACT precedes REFLECT"),
        # Loop law: REFLECT may trigger new SENSE
        Law("cycle", "REFLECT outputs may become SENSE inputs"),
        # Identity: empty operation in any phase preserves state
        Law("identity", "id >> op == op == op >> id"),
    ]
)
```

### 3. TOWN→NPHASE Functor Contract

```python
def town_to_nphase_functor(town_op: TownOperation) -> NPhaseOperation:
    """Map town operations to N-Phase operations.

    Laws:
        - Preserves identity: F(id) = id
        - Preserves composition: F(a >> b) = F(a) >> F(b)
    """
    mapping = {
        # SENSE operations (observation, perception)
        "observe": "sense",
        "listen": "sense",

        # ACT operations (action, change)
        "greet": "act",
        "gossip": "act",
        "trade": "act",
        "dispute": "act",
        "celebrate": "act",
        "teach": "act",

        # REFLECT operations (contemplation, integration)
        "solo": "reflect",
        "mourn": "reflect",
        "rest": "reflect",
    }
    return NPhaseOperation(mapping[town_op.name], arity=1, phase=...)
```

### 4. EvolvingCitizen Contract

```python
@dataclass
class GrowthState:
    """State accumulated during evolution cycle."""
    observations: list[Observation]
    actions_taken: list[ActionResult]
    eigenvector_deltas: dict[str, float]

class EvolvingCitizen(Citizen):
    """Citizen that grows via compressed SENSE→ACT→REFLECT."""

    growth_state: GrowthState
    evolution_count: int = 0
    max_eigenvector_drift: float = 0.1  # per cycle

    async def sense(self, observation: Observation) -> SensedState:
        """Perceive the world through cosmotechnics lens."""
        # SENSE phase: filter observation through worldview

    async def act(self, sensed: SensedState) -> ActionResult:
        """Take action based on perception."""
        # ACT phase: choose and execute operation

    async def reflect(self, result: ActionResult) -> "EvolvingCitizen":
        """Integrate experience into self-model."""
        # REFLECT phase: update eigenvectors (bounded by max_drift)

    async def evolve(self, observation: Observation) -> "EvolvingCitizen":
        """Full evolution cycle: sense >> act >> reflect."""
        sensed = await self.sense(observation)
        result = await self.act(sensed)
        return await self.reflect(result)

    def should_evolve(self) -> bool:
        """Check if growth triggers are met."""
        # Triggers: surplus > threshold, relationship milestone, witnessed event
```

---

## Laws to Verify

| Law | Description | Test Strategy |
|-----|-------------|---------------|
| Functor identity | `F(id) = id` | Apply to identity operation |
| Functor composition | `F(a >> b) = F(a) >> F(b)` | Compose two operations |
| Eigenvector bound | `|drift| ≤ max_drift` | Property test random evolutions |
| Memory decay monotonic | `strength(t+1) ≤ strength(t)` | Property test decay function |
| NPHASE order | SENSE before ACT before REFLECT | Type-level or runtime check |

---

## Exit Criteria

- [ ] GraphMemory contract complete with k-hop spec
- [ ] NPHASE_OPERAD defined with laws
- [ ] Functor contract with law assertions
- [ ] EvolvingCitizen contract with bounds
- [ ] All laws testable

---

## Exit → STRATEGIZE

⟿[STRATEGIZE] Agent Town Phase 3: Sequence Implementation

/hydrate
handles: contracts=${this_output}; dependencies=chunk_graph
ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched}; entropy=0.10
mission: Sequence 6 chunks; identify parallel tracks; map dependencies.
exit: ordered plan + parallel opportunities; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE.

void.entropy.sip(amount=0.02). The sequence crystallizes.
```

---

## IMPLEMENT Phase (Quick Card)

```markdown
⟿[IMPLEMENT] Agent Town Phase 3: Execute Chunks

/hydrate

handles:
  contracts: (from DEVELOP)
  sequence: (from STRATEGIZE)
  impl_dir: impl/claude/agents/town/

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: in_progress    # ← YOU ARE HERE
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.18
  spent: 0.08
  remaining: 0.10

---

## Mission

Execute 6 chunks per sequence from STRATEGIZE.

TodoWrite tracking. Parallel where possible.
Each chunk: implement → test → verify laws → mark complete.

### Chunk Order
1. Graph Memory Foundation (independent)
2. NPHASE_OPERAD Definition (independent, parallel with 1)
3. TOWN→NPHASE Functor (depends on 2)
4. EvolvingCitizen Core (depends on 3)
5. Growth Mechanics (depends on 4)
6. Integration + 3 Citizens (depends on all)

---

## Exit Criteria

- [ ] All 6 chunks implemented
- [ ] 300+ tests passing (50+ new)
- [ ] Laws verified (functor, eigenvector bounds)
- [ ] No new mypy errors
- [ ] CLI: `kg town status --evolving` works

---

## Exit → QA

⟿[QA] Agent Town Phase 3: Verification

/hydrate
ledger: {IMPLEMENT:touched}; entropy=0.08
mission: mypy, ruff, security audit, law verification.
exit: all checks pass; ledger.QA=touched; continuation → TEST.
```

---

## REFLECT Phase (Quick Card)

```markdown
⟿[REFLECT] Agent Town Phase 3: Retrospective

/hydrate

handles:
  impl: impl/claude/agents/town/
  tests: impl/claude/agents/town/_tests/
  epilogues: impl/claude/plans/_epilogues/

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched
  MEASURE: touched
  REFLECT: in_progress    # ← YOU ARE HERE

entropy:
  planned: 0.18
  spent: 0.16
  remaining: 0.02

---

## Mission

1. **Summarize Outcomes**: Files created, tests passing, features delivered
2. **Distill Learnings**: Molasses-test zettels
3. **Technical Debt**: Risks carried forward
4. **Law Audit**: Which laws held? Which revealed weaknesses?
5. **Seed Next Cycle**: Phase 4 continuation prompt

---

## Questions for Reflection

- Did the unified approach work better than sequential tracks?
- Where did NPHASE integration surface unexpected complexity?
- Is eigenvector drift bounded correctly in practice?
- Are 3 evolving citizens enough to validate the pattern?

---

## Exit Criteria

- [ ] Epilogue: `impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase3-complete.md`
- [ ] Learnings captured (Molasses Test)
- [ ] Phase 4 continuation prompt provided

---

## Exit → DETACH or PLAN (Phase 4)

⟂[DETACH:cycle_complete] Agent Town Phase 3 shipped. Evolution awakens.

OR

⟿[PLAN] Agent Town Phase 4: Scale & Web UI

/hydrate
handles: phase3_epilogue=impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase3-complete.md
ledger: {REFLECT:touched}; entropy=0.20
mission: Plan Phase 4 (scale to 25 citizens, web UI, council mode, full TownSheaf).

void.gratitude.tithe. The citizens evolve.
```

---

# Phase 4 Continuation Prompt (Seed)

```markdown
⟿[PLAN] Agent Town Phase 4: Scale & Web UI

/hydrate

handles:
  phase3_impl: impl/claude/agents/town/
  phase3_epilogue: impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase3-complete.md
  evolving_citizen: impl/claude/agents/town/evolving.py
  nphase_functor: impl/claude/agents/town/functor.py
  graph_memory: impl/claude/agents/town/memory.py

phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.25
  spent: 0.00
  remaining: 0.25

soul-state:
  emotion_log.delta: synthesis → expansion
  dream_journal.carry: "A village of 25 evolving souls, watched through glass"
  fear_register.pending: [N²_relationship_explosion, UI_complexity, performance]
  affinity_map.targets: [Web_UI, TownSheaf_formal, council_mode]

---

## Phase 4 Scope (Tentative)

| Component | Phase 3 (Done) | Phase 4 Target |
|-----------|----------------|----------------|
| Citizens | 10 (7 static + 3 evolving) | 25 (15 static + 10 evolving) |
| Regions | 5 | 12 |
| User Modes | +evolve observation | + council, election |
| Memory | Graph episodic | + semantic clustering |
| Evolution | EvolvingCitizen | + inter-citizen learning |
| Infrastructure | NPHASE functor | Full TownSheaf |
| UI | CLI only | + Web observer (React + D3) |

---

## Key Questions

1. **Scale architecture**: N² relationships with 25 citizens?
2. **Web UI scope**: Observer only, or interactive?
3. **Council mode**: Multi-citizen deliberation protocol?
4. **TownSheaf formal**: Full coherence verification?

---

## Exit → RESEARCH

⟿[RESEARCH] Agent Town Phase 4: Scaling Patterns

void.entropy.sip(amount=0.05). The village grows.
```

---

# For Future Observer

To continue Agent Town development:

1. `/hydrate` - ground in principles
2. Read this document for Phase 3 unified context
3. Execute the PLAN prompt above
4. Work through phases: RESEARCH → DEVELOP → STRATEGIZE → IMPLEMENT → QA → TEST → REFLECT
5. Use TodoWrite to track progress
6. Act from principles with courage

---

## Process Metrics Template

```yaml
session:
  date: YYYY-MM-DD
  phases_touched: 0/11
  tests_delta: 0 (250 → ?)
  files_modified: 0
  files_created: 0
  chunks_completed: 0/6

entropy:
  planned: 0.18
  spent: 0.00
  returned: 0.00

branch_count: 0
continuation_type: null

law_checks:
  functor_identity: pending
  functor_composition: pending
  eigenvector_bounds: pending
  memory_decay_monotonic: pending
  nphase_order: pending
```

---

*"The citizen evolves. Memory deepens. Laws cohere. The same categorical structure underlies everything."*

void.gratitude.tithe.
