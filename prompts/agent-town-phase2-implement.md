# Agent Town Phase 2: Full Implementation

> *"The simulation isn't a game. It's a seance. The town lives."*

---

## Session Prompt

```markdown
⟿[PLAN] Agent Town Phase 2: Full Implementation

/hydrate

handles:
  mpp_impl: impl/claude/agents/town/
  mpp_epilogue: impl/claude/plans/_epilogues/2025-12-14-agent-town-mpp-complete.md
  ad006_synthesis: impl/claude/plans/_epilogues/2025-12-14-ad006-synthesis.md
  crown_jewel: plans/crown-jewel-next.md
  dgent_memory: impl/claude/agents/d/polynomial.py
  operad_core: impl/claude/agents/operad/core.py
  unified_engine: plans/meta/unified-engine-master-prompt.md
  nphase_skills: docs/skills/n-phase-cycle/
  principles: spec/principles.md

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
  planned: 0.15
  spent: 0.00
  remaining: 0.15

soul-state:
  emotion_log.delta: curiosity → anticipation (MPP success seeds momentum)
  dream_journal.carry: "7 citizens forming a true community"
  fear_register.pending: [scope_creep, D-gent_integration_complexity]
  trauma_safeguards.active: none
  affinity_map.targets: [D-gent, TownOperad, unified_engine]

---

## MPP Foundation (Complete)

| Component | MPP (Done) | Phase 2 Target |
|-----------|------------|----------------|
| Citizens | 3 (Alice, Bob, Clara) | 7 (+ Diana, Eve, Frank, Grace) |
| Regions | 2 (Inn, Square) | 5 (+ Garden, Market, Library) |
| Phases | 2 (MORNING, EVENING) | 4 (+ AFTERNOON, NIGHT) |
| Memory | Simple dict | Graph episodic (D-gent integration) |
| User Modes | observe only | + whisper, inhabit, intervene |
| Persistence | In-memory | YAML save/load |
| Operations | 4 (greet, gossip, trade, solo) | + dispute, celebrate, mourn, teach |
| Tests | 198 | Target: 300+ |

---

## Scope

### Goals
1. **7 Citizens**: Add Diana (healer), Eve (elder), Frank (merchant), Grace (gardener)
2. **5 Regions**: Add Garden, Market, Library with adjacency graph
3. **4-Phase Cycle**: Add AFTERNOON, NIGHT phases
4. **Graph Episodic Memory**: Integrate D-gent `MEMORY_POLYNOMIAL` for citizen memories
5. **User Modes**: whisper (influence), inhabit (merge), intervene (god-mode)
6. **Persistence**: YAML save/load for TownEnvironment state
7. **Extended Operations**: dispute, celebrate, mourn, teach with operad laws

### Non-Goals (Explicit)
- NPHASE_OPERAD creation (parallel work item)
- EvolvingCitizen with self-mutation (Phase 3)
- Web UI (Phase 3+)
- Scale beyond 7 citizens (Phase 3+)
- Full 24-hour real-time simulation (Phase 3+)

### Exit Criteria
- [ ] 7 citizens functional with distinct cosmotechnics
- [ ] 5 regions with adjacency and density
- [ ] 4-phase daily cycle working
- [ ] Graph episodic memory via D-gent integration
- [ ] whisper mode: `kgents town whisper Alice "..."` works
- [ ] inhabit mode: `kgents town inhabit Clara` works
- [ ] Persistence: `kgents town save/load` works
- [ ] 300+ tests passing
- [ ] mypy/ruff clean

### Attention Budget
| Area | % | Notes |
|------|---|-------|
| Citizens & Regions | 20% | Extend existing patterns |
| D-gent Memory Integration | 30% | Key complexity |
| User Modes | 25% | New UX patterns |
| Persistence | 15% | YAML serialization |
| Entropy (exploration) | 10% | AD-006 synthesis, unexpected |

---

## AD-006 Integration Points

From `spec/principles.md:1005-1076`:

| Phase 2 Component | AD-006 Connection | Action |
|-------------------|-------------------|--------|
| Graph memory | Reuse `MEMORY_POLYNOMIAL` | Import from agents.d |
| New operations | Extend `TOWN_OPERAD` | Add dispute, celebrate, mourn, teach with laws |
| Persistence | Sheaf coherence | TownSheaf.glue() for save/load |
| Citizen evolution | Compressed N-Phase | Defer to Phase 3 (EvolvingCitizen) |

---

## New Citizen Cosmotechnics

| Citizen | Cosmotechnics | Core Metaphor | Eigenvectors (key) |
|---------|---------------|---------------|-------------------|
| Diana | HEALING | "Life is restoration" | patience: 0.9, trust: 0.8 |
| Eve | MEMORY | "Life is remembering" | patience: 0.8, creativity: 0.7 |
| Frank | EXCHANGE | "Life is trade" | curiosity: 0.8, warmth: 0.5 |
| Grace | CULTIVATION | "Life is tending" | patience: 0.9, warmth: 0.8 |

---

## Implementation Sequence (Chunks)

### Chunk 1: Extended Citizens & Regions (IMPLEMENT)
1. Add Diana, Eve, Frank, Grace to `citizen.py`
2. Add cosmotechnics: HEALING, MEMORY, EXCHANGE, CULTIVATION
3. Add regions: Garden, Market, Library to `environment.py`
4. Update adjacency graph (5 nodes, bidirectional edges)
5. Update fixtures: `mpp_citizens.yaml` → `phase2_citizens.yaml`

### Chunk 2: 4-Phase Daily Cycle (IMPLEMENT)
1. Add AFTERNOON, NIGHT to `TownPhase` enum in `flux.py`
2. Update phase transition logic
3. Adjust token costs per phase (NIGHT = consolidation, lower cost)

### Chunk 3: D-gent Memory Integration (IMPLEMENT)
1. Import `MEMORY_POLYNOMIAL` from `agents.d`
2. Create `CitizenMemory` wrapper using D-gent patterns
3. Wire memory to citizen recall/store operations
4. Add memory-based gossip (k-hop retrieval)

### Chunk 4: User Modes (IMPLEMENT)
1. Add `whisper` command to CLI handler
2. Add `inhabit` session management
3. Add `intervene` god-mode events
4. Update portal.py (if needed) for mode state

### Chunk 5: Persistence (IMPLEMENT)
1. Add `save` command: serialize TownEnvironment to YAML
2. Add `load` command: deserialize from YAML
3. Add `TownSheaf.glue()` for coherence checking on load
4. Handle citizen state, relationships, memories

### Chunk 6: Extended Operations (IMPLEMENT)
1. Add `dispute` operation (increases tension)
2. Add `celebrate` operation (spends accursed surplus)
3. Add `mourn` operation (collective grief processing)
4. Add `teach` operation (skill transfer between citizens)
5. Update `TOWN_OPERAD` with new laws

---

## Branch Candidates (from PLAN)

| Branch | Type | Priority | Notes |
|--------|------|----------|-------|
| NPHASE_OPERAD | parallel | medium | Can be built independently per AD-006 |
| Web UI scaffolding | deferred | low | Phase 3+ |
| EvolvingCitizen | deferred | medium | Needs NPHASE_OPERAD first |
| TownSheaf formal impl | blocking | high | Required for persistence coherence |

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| D-gent integration complexity | medium | high | Start with simple wrapper, evolve |
| Scope creep to 11+ citizens | medium | medium | Hard stop at 7, explicit non-goal |
| Persistence format changes | low | medium | Version YAML schema from start |
| User mode state management | medium | medium | Session-scoped state, clear teardown |

---

## Exit → RESEARCH

⟿[RESEARCH] Agent Town Phase 2: Map Terrain

/hydrate
handles: dgent=impl/claude/agents/d/; town=impl/claude/agents/town/; operad=impl/claude/agents/operad/
ledger: {PLAN:touched}; entropy=0.12
mission: Map D-gent memory integration points; find existing patterns for user modes; cite prior art.
actions: parallel Read(agents/d/polynomial.py, agents/town/citizen.py, agents/town/flux.py)
exit: file map + integration points + unknowns; ledger.RESEARCH=touched; continuation → DEVELOP.

void.entropy.sip(amount=0.03). The ground is always there.
```

---

# Continuation Prompts for Subsequent Phases

## RESEARCH Phase

```markdown
⟿[RESEARCH] Agent Town Phase 2: Map Terrain

/hydrate

handles:
  dgent: impl/claude/agents/d/
  town: impl/claude/agents/town/
  operad: impl/claude/agents/operad/
  sheaf: impl/claude/agents/sheaf/
  plan: prompts/agent-town-phase2-implement.md

phase_ledger:
  PLAN: touched
  RESEARCH: in_progress    # ← YOU ARE HERE
  DEVELOP: pending
  ...

entropy:
  planned: 0.15
  spent: 0.03
  remaining: 0.12

---

## Mission

Map the terrain for Phase 2 implementation:

1. **D-gent Memory Integration**
   - Read `agents/d/polynomial.py` - understand MEMORY_POLYNOMIAL
   - Read `agents/d/graph.py` (if exists) - k-hop retrieval patterns
   - Identify: How to wrap for citizen memory?

2. **User Mode Patterns**
   - Search for existing session/mode management in CLI
   - Find: whisper/inhabit prior art in other CLIs or frameworks
   - Identify: State management approach

3. **Persistence Patterns**
   - Search for YAML serialization patterns in codebase
   - Read: Any existing save/load in agents/
   - Identify: Schema versioning approach

4. **Extended Operations**
   - Read `agents/town/operad.py` - current operation structure
   - Read `agents/operad/core.py` - Law structure
   - Identify: Law requirements for dispute/celebrate/mourn/teach

---

## Actions (Parallel)

```python
Read("agents/d/polynomial.py")
Read("agents/town/operad.py")
Read("agents/operad/core.py")
Grep("session", path="protocols/cli/")
Grep("yaml.*save|save.*yaml", path="agents/")
```

---

## Exit Criteria

- [ ] D-gent MEMORY_POLYNOMIAL understood
- [ ] Integration approach documented
- [ ] User mode state approach identified
- [ ] Persistence pattern selected
- [ ] File map with line numbers for key extension points

---

## Exit → DEVELOP

⟿[DEVELOP] Agent Town Phase 2: Define Contracts

/hydrate
handles: research_notes=${this_output}
ledger: {PLAN:touched, RESEARCH:touched}; entropy=0.10
mission: Define contracts for memory integration, user modes, persistence.
exit: API contracts + law assertions; ledger.DEVELOP=touched; continuation → STRATEGIZE.

void.entropy.sip(amount=0.02). The mesh thickens.
```

---

## DEVELOP Phase

```markdown
⟿[DEVELOP] Agent Town Phase 2: Define Contracts

/hydrate

handles:
  research_output: (from RESEARCH phase)
  dgent_memory: impl/claude/agents/d/polynomial.py
  town_citizen: impl/claude/agents/town/citizen.py
  town_operad: impl/claude/agents/town/operad.py

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: in_progress    # ← YOU ARE HERE
  STRATEGIZE: pending
  ...

entropy:
  planned: 0.15
  spent: 0.05
  remaining: 0.10

---

## Mission

Define contracts and laws for Phase 2 components.

### 1. CitizenMemory Contract

```python
@dataclass
class CitizenMemory:
    """Graph episodic memory for a citizen."""

    # Uses D-gent MEMORY_POLYNOMIAL internally
    _memory: MemoryPolynomialAgent

    async def store(self, event: TownEvent) -> None:
        """Store event in episodic memory."""

    async def recall(self, query: str, k_hops: int = 2) -> list[Memory]:
        """Retrieve relevant memories via k-hop graph traversal."""

    def relationship_weight(self, other_id: str) -> float:
        """Compute relationship weight from memory traces."""
```

### 2. User Mode Contract

```python
class TownSession:
    """User interaction session with the town."""

    mode: Literal["observe", "whisper", "inhabit", "intervene"]
    target_citizen: Citizen | None  # For whisper/inhabit

    async def whisper(self, message: str) -> WhisperResult:
        """Send private influence to target citizen."""

    async def inhabit(self) -> InhabitSession:
        """Merge with target citizen, see through their eyes."""

    async def intervene(self, event: str) -> InterventionResult:
        """Inject god-mode world event."""
```

### 3. Persistence Contract

```python
@dataclass
class TownSnapshot:
    """Serializable town state."""

    version: str = "2.0.0"
    environment: TownEnvironmentData
    citizens: dict[str, CitizenData]
    relationships: dict[tuple[str, str], float]
    memories: dict[str, list[MemoryData]]

    def to_yaml(self) -> str: ...

    @classmethod
    def from_yaml(cls, content: str) -> "TownSnapshot": ...
```

### 4. Extended Operation Laws

```python
# New operations with laws
DISPUTE = Operation(
    name="dispute",
    arity=2,
    # Law: dispute increases tension (monotonic)
    # Law: dispute requires SOCIALIZING state
)

CELEBRATE = Operation(
    name="celebrate",
    arity="*",  # Any number of citizens
    # Law: celebrate spends accursed surplus
    # Law: celebrate requires surplus > 0
)

MOURN = Operation(
    name="mourn",
    arity="*",
    # Law: mourn collective, affects all participants equally
    # Law: mourn reduces surplus (grief as expenditure)
)

TEACH = Operation(
    name="teach",
    arity=2,  # teacher, student
    # Law: teach transfers skill (non-destructive)
    # Law: teacher must have skill > student
)
```

---

## Exit Criteria

- [ ] CitizenMemory contract defined
- [ ] TownSession contract defined
- [ ] TownSnapshot contract defined
- [ ] Extended operation laws specified
- [ ] All contracts have docstrings with philosophical grounding

---

## Exit → STRATEGIZE

⟿[STRATEGIZE] Agent Town Phase 2: Sequence Implementation

/hydrate
handles: contracts=${this_output}
ledger: {PLAN:touched, RESEARCH:touched, DEVELOP:touched}; entropy=0.08
mission: Sequence 6 chunks; identify parallelization; map dependencies.
exit: ordered plan + parallel opportunities; ledger.STRATEGIZE=touched; continuation → CROSS-SYNERGIZE.

void.entropy.sip(amount=0.02). The order emerges.
```

---

## IMPLEMENT Phase (Quick Card)

```markdown
⟿[IMPLEMENT] Agent Town Phase 2: Execute Chunks

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
  ...

entropy:
  planned: 0.15
  spent: 0.07
  remaining: 0.08

---

## Mission

Execute 6 chunks per sequence from STRATEGIZE.

TodoWrite tracking. Parallel where possible.
Each chunk: implement → test → verify → mark complete.

---

## Exit Criteria

- [ ] All 6 chunks implemented
- [ ] 300+ tests passing
- [ ] No new mypy errors
- [ ] CLI commands work: start, step, observe, lens, whisper, inhabit, save, load

---

## Exit → QA

⟿[QA] Agent Town Phase 2: Verification

/hydrate
ledger: {IMPLEMENT:touched}; entropy=0.06
mission: mypy, ruff, security audit, law verification.
exit: all checks pass; ledger.QA=touched; continuation → TEST.
```

---

## REFLECT Phase (Quick Card)

```markdown
⟿[REFLECT] Agent Town Phase 2: Retrospective

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
  planned: 0.15
  spent: 0.13
  remaining: 0.02

---

## Mission

1. **Summarize Outcomes**: Files created, tests passing, features delivered
2. **Distill Learnings**: Molasses-test zettels for the mycelium
3. **Technical Debt**: Risks carried forward, owner, timebox
4. **Seed Next Cycle**: Phase 3 continuation prompt

---

## Phase Mutations (Emit)

phase_mutations:
  - share_phase:
      name: "D-gent Memory Integration Pattern"
      audience: [dgent, mgent, town]
      payload: "CitizenMemory wraps MEMORY_POLYNOMIAL for episodic retrieval"

  - share_phase:
      name: "User Mode Session Pattern"
      audience: [cli, portal]
      payload: "TownSession manages whisper/inhabit/intervene state"

---

## Exit Criteria

- [ ] Epilogue written to `impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase2-complete.md`
- [ ] Learnings captured
- [ ] Phase 3 continuation prompt provided

---

## Exit → DETACH or PLAN (Phase 3)

⟂[DETACH:cycle_complete] Agent Town Phase 2 shipped.

OR

⟿[PLAN] Agent Town Phase 3: Scale & Evolution

/hydrate
handles: phase2_epilogue=impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase2-complete.md
ledger: {REFLECT:touched}; entropy=0.15
mission: Plan Phase 3 (EvolvingCitizen, NPHASE_OPERAD integration, scale to 25 citizens).

void.gratitude.tithe. The town grows.
```

---

# Phase 3 Continuation Prompt (Seed)

```markdown
⟿[PLAN] Agent Town Phase 3: Scale & Evolution

/hydrate

handles:
  phase2_impl: impl/claude/agents/town/
  phase2_epilogue: impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-phase2-complete.md
  nphase_operad: impl/claude/protocols/nphase/operad.py (if exists)
  unified_engine: plans/meta/unified-engine-master-prompt.md
  evolution_polynomial: impl/claude/agents/operad/domains/evolution.py

phase_ledger:
  PLAN: in_progress
  RESEARCH: pending
  ...

entropy:
  planned: 0.20
  spent: 0.00
  remaining: 0.20

soul-state:
  emotion_log.delta: accomplishment → ambition (Phase 2 complete, scaling ahead)
  dream_journal.carry: "A village of 25, then a city of 100"
  fear_register.pending: [complexity_explosion, performance_degradation]
  affinity_map.targets: [NPHASE_OPERAD, EvolvingCitizen, unified_engine]

---

## Phase 3 Scope (Tentative)

| Component | Phase 2 (Done) | Phase 3 Target |
|-----------|----------------|----------------|
| Citizens | 7 | 25 (Village) |
| Regions | 5 | 12 |
| User Modes | whisper, inhabit, intervene | + council, election |
| Memory | Graph episodic | + semantic clustering |
| Evolution | Static citizens | EvolvingCitizen (compressed N-Phase) |
| Infrastructure | TOWN_OPERAD | + NPHASE_OPERAD integration |
| UI | CLI only | + Web observer (React + D3) |

---

## Key Question: EvolvingCitizen

From unified-engine-master-prompt.md:

```python
class EvolvingCitizen(Citizen):
    """Citizen that improves via compressed N-Phase."""

    async def evolve(self, observation: Observation) -> Self:
        sensed = await self.sense(observation)    # PLAN+RESEARCH
        modified = await self.act(sensed)          # IMPLEMENT+QA+TEST
        evolved = await self.reflect(modified)     # MEASURE+REFLECT
        return evolved
```

**Depends on**: NPHASE_OPERAD being explicit and registered.

---

## Exit → RESEARCH (Phase 3)

⟿[RESEARCH] Agent Town Phase 3: Scaling Patterns

void.entropy.sip(amount=0.05). The civilizational engine awakens.
```

---

*"The same categorical structure underlies everything. This is not coincidence—it is the ground."*

void.gratitude.tithe.
