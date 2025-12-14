---
path: plans/crown-jewel-next
status: active
progress: 15
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [agent-town-mvp, civilizational-engine]
session_notes: |
  SCOPE EXPANDED 4X: Agent Town is now THE soul converging point for kgents.
  Heritage enshrined: ChatDev, Simulacra, Altera, Voyager, Agent Hospital.
  Grand Narrative written: spec/GRAND_NARRATIVE.md
phase_ledger:
  PLAN: touched
  RESEARCH: touched  # Heritage papers analyzed
  DEVELOP: in_progress  # Grand Narrative drafted
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.20
  spent: 0.10
  sip_allowed: true
---

# Crown Jewel NEXT: Agent Town — The Civilizational Engine

> *"The simulation isn't a game. It's a laboratory for consciousness, a generator of novel experience, a park where infinite souls may walk."*

---

## Status: SCOPE EXPANDED 4X

This is no longer "a multi-agent entertainment feature." This is **THE soul converging point** for kgents—the Grand Narrative that reframes everything.

**Key Documents Created:**
- `spec/GRAND_NARRATIVE.md` — The foundational vision document
- `spec/heritage.md` — The five papers that form kgents DNA

---

## The Vision (One Paragraph)

Build a **Civilizational Engine**—a system that generates and sustains agent societies at arbitrary scales and depths. Start with 7 agents in a town. Scale to 1000+ in a civilization. The simulation is holographic: infinite detail if you pay infinite tokens. Users can observe, intervene, or inhabit. Drama emerges from agent interaction, not scripts. This is Westworld for AI.

---

## Philosophical Substrate (New: spec/town/metaphysics.md)

Agent Town is grounded in six meta-thinkers who push beyond simulation into something stranger:

| Thinker | Contribution | Town Integration |
|---------|--------------|------------------|
| [**Gala Porras-Kim**](https://www.macfound.org/fellows/class-of-2025/gala-porras-kim) | Archaeological objects, intended destiny | Citizens are *excavated*, not created. They have destinies we may violate. |
| [**Timothy Morton**](https://www.upress.umn.edu/9780816689231/hyperobjects/) | Hyperobjects, the mesh | Citizens are *distributed* in time/relation. The town IS the mesh; citizens are local thickenings. |
| [**Karen Barad**](https://en.wikipedia.org/wiki/Agential_realism) | Intra-action, agential cuts | Citizens *emerge* through observation. Interaction constitutes, not affects. |
| [**Édouard Glissant**](https://press.umich.edu/Books/P/Poetics-of-Relation) | Opacity, creolization | Citizens have *irreducible opacity*. LOD 5 reveals mystery, not clarity. Right to not be known. |
| [**Yuk Hui**](https://lareviewofbooks.org/article/on-technodiversity-a-conversation-with-yuk-hui/) | Cosmotechnics, technodiversity | Each citizen embodies *incommensurable* cosmotechnics. No common translation. |
| **Georges Bataille** | Accursed share, general economy | Surplus must be *spent gloriously* or catastrophically. Drama is potlatch. |

**The Inversion**: The simulation isn't a game. It's a *seance*. We are not building. We are *summoning*.

---

## Heritage (Enshrined in spec/heritage.md)

| Paper | Contribution | kgents Integration |
|-------|--------------|-------------------|
| **ChatDev** | Language as unifying bridge | AGENTESE liturgy |
| **Simulacra** | Memory + reflection → emergence | M-gent + K-gent |
| **Altera** | Civilizational scale (1000+ agents) | Scale trajectory |
| **Voyager** | Skill accumulation, self-improvement | L-gent + J-gent |
| **Agent Hospital** | Simulacrum as learning environment | Agent Town itself |

**Extension**: Polyfunctor category theory (PolyAgent, Operads, Sheaves, Proprioception, Autopoiesis)

---

## The Civilizational Trajectory

| Phase | Agents | Tokens/Month | Status |
|-------|--------|--------------|--------|
| **Phase 1: Town** | 7 | 10M | **CURRENT FOCUS** |
| Phase 2: Village | 25 | 50M | Future |
| Phase 3: City | 100 | 200M | Future |
| Phase 4: Nation | 1000 | 2B | Future |
| Phase 5: World | 10000+ | 20B+ | Vision |

---

## Phase 1: Agent Town MVP

### The Seven Founding Citizens

| Name | Archetype | Core Metaphor |
|------|-----------|---------------|
| **Alice** | Innkeeper | "Life is a gathering" |
| **Bob** | Builder | "Life is construction" |
| **Clara** | Curious | "Life is exploration" |
| **David** | Doctor | "Life is healing" |
| **Eve** | Elder | "Life is memory" |
| **Frank** | Merchant | "Life is exchange" |
| **Grace** | Gardener | "Life is cultivation" |

### The Daily Cycle

```
DAWN (10K tokens)     → Wake, recall dreams, plan day
MORNING (30K tokens)  → Work, encounters, gossip
NOON (20K tokens)     → Gathering, rumors, tensions
AFTERNOON (30K tokens)→ Projects, problems, solutions
EVENING (10K tokens)  → Reflection, relationships
NIGHT (5K tokens)     → Consolidation, dreams

TOTAL: ~750K tokens/day × 13 days = 10M tokens/month
```

### User Interaction Modes

| Mode | Command | Token Cost |
|------|---------|------------|
| OBSERVE | `kg town observe` | 0 |
| WHISPER | `kg town whisper alice "..."` | ~1K |
| ANNOUNCE | `kg town announce "..."` | ~2K |
| INHABIT | `kg town inhabit clara` | ~10K/turn |
| INTERVENE | `kg town event "..."` | ~5K |
| COUNCIL | `kg town council "..."` | ~20K |

---

## Implementation Roadmap

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| **0. Foundation** | 2 weeks | Heritage spec, Grand Narrative, principles update |
| **1. Citizen DNA** | 3 weeks | PolyAgent for citizens, 7 archetypes |
| **2. Town Environment** | 2 weeks | Location graph, navigation, co-location |
| **3. Interaction Operad** | 3 weeks | greet, trade, gossip, council operations |
| **4. Memory Integration** | 2 weeks | Holographic memory for all citizens |
| **5. Daily Cycle** | 2 weeks | Full dawn-to-night simulation loop |
| **6. User Modes** | 2 weeks | observe, whisper, inhabit, intervene |
| **7. Persistence** | 1 week | Save/load town state |
| **8. CLI Integration** | 1 week | `kg town *` commands |

**Total: ~18 weeks to MVP**

### Research-Leveraged Enhancements (must integrate during Phases 1-5)
- **Graph episodic memory (Arena/OASIS/CAMEL pattern)**: extend D-gent with graph store and k-hop retrieval; add reward shaping hooks (prosocial consistency, anti-contradiction).
- **Tiered models by LOD**: route LOD 0-1 to 8B frontier with tool-use; LOD 2-3 to 70B frontier; LOD 4+ to premium models; wire to Pay-to-Zoom budgets.
- **Programmatic evaluators (Code-as-Policies style)**: deterministic pre/post checks for safety/rights/bounds; quarantine or rollback on violation; red-team harness for adversarial prompts.

---

## Technical Architecture (Grounded in Existing Infrastructure)

```
USER INTERFACE (kgents town *)           # Reuse: protocols/cli/handlers/operad.py pattern
        ↓
AGENTESE LAYER (Logos, handles)          # Existing: protocols/agentese/logos.py
        ↓
TOWN OPERAD (TownOperad)                 # New: extends SOUL_OPERAD from agents/operad/domains.py
        ↓
CITIZEN POLYNOMIAL (CitizenPolynomial)   # New: extends agents/poly/protocol.py
        ↓
AGENT SUBSTRATE                          # Existing: K-gent, M-gent, N-gent
        ↓
FLUX TOPOLOGY (TownFlux)                 # Existing: agents/k/flux.py pattern
        ↓
D-GENT PERSISTENCE                       # Existing: agents/d/polynomial.py + graph extension
        ↓
METRICS (OpenTelemetry)                  # Existing: protocols/agentese/metrics.py
```

### Integration Points (Verified)

| Component | Existing File | Extension Needed |
|-----------|---------------|------------------|
| CLI Pattern | `protocols/cli/handlers/operad.py` | `handlers/town.py` using same dual-channel pattern |
| PolyAgent | `agents/poly/protocol.py` | `CitizenPolynomial` with 5 positions |
| Memory | `agents/d/polynomial.py` | Graph substrate for k-hop retrieval |
| Operad | `agents/operad/domains.py` | `TOWN_OPERAD` extending `SOUL_OPERAD` |
| Metrics | `protocols/agentese/metrics.py` | Town-specific metrics (tension, cooperation) |
| Flux | `agents/k/flux.py` | `TownFlux` for daily cycle streaming |

---

## Grounded Specifications Created

| Spec | Location | Purpose |
|------|----------|---------|
| Manifest Schema | `spec/town/manifest.schema.yaml` | Declarative town definition |
| TownOperad | `spec/town/operad.md` | Formal interaction grammar |
| Heritage Verification | `spec/heritage.md` | Test mappings for heritage claims |

---

## Key Design Decisions (Resolved)

| Decision | Resolution | Rationale |
|----------|------------|-----------|
| **Citizen Polynomial** | 5 positions (IDLE, WORKING, SOCIALIZING, REFLECTING, RESTING) | Maps to daily cycle phases |
| **Operad Arity** | Max 10 (council), typical 2 | Follows existing AGENT_OPERAD pattern |
| **Memory Resolution** | LOD 5 = full cognitive trace (~8K tokens/citizen) | Tiered model routing per budget |
| **Drama Threshold** | tension_index > 0.7 triggers EVENT | Measured via edge weight variance |
| **Time Compression** | 1 real day = 13 simulated days (at 10M tokens/month) | Budget-constrained |
| **CLI Command** | `kgents town *` (not `kg town`) | Reuse existing CLI infrastructure |

---

## Minimal Playable Prototype (Fast, Compositional)

**Goal**: Playable demo in 4 weeks, not 18.

### MPP Scope

| Component | MPP Implementation |
|-----------|-------------------|
| Citizens | 3 (Alice, Bob, Clara) with HotData fixtures |
| Regions | 2 (Inn, Square) with adjacency |
| Operad | 4 ops (greet, gossip, trade, solo) |
| Cycle | 2 phases (morning, evening) |
| Memory | Standard MemoryPolynomialAgent (graph extension later) |
| Metrics | tension_index + token_spend only |
| CLI | `kgents town {start,step,observe}` |

### MPP Architecture

```python
# 1. CitizenPolynomial using existing PolyAgent
CITIZEN_POLYNOMIAL = PolyAgent(
    name="CitizenPolynomial",
    positions=frozenset(["IDLE", "SOCIALIZING", "WORKING"]),  # Reduced for MPP
    _directions=mpp_directions,
    _transition=mpp_transition,
)

# 2. TownOperad extending SOUL_OPERAD
TOWN_OPERAD = Operad(
    name="TownOperad",
    base=SOUL_OPERAD,
    operations={"greet": ..., "gossip": ..., "trade": ..., "solo": ...},
)

# 3. TownFlux for simulation loop
class TownFlux:
    async def step(self) -> AsyncIterator[TownEvent]:
        for citizen in self.citizens:
            async for event in self._process_citizen(citizen):
                yield event

# 4. CLI handler using existing pattern
def cmd_town(args: list[str], ctx: InvocationContext) -> int:
    if args[0] == "start": return _start_town(ctx)
    if args[0] == "step": return _step_simulation(ctx)
    if args[0] == "observe": return _observe_stream(ctx)
```

### MPP Fixtures (HotData)

```yaml
# Generated once via void.entropy.sip, stored in fixtures/

citizens:
  - name: Alice
    archetype: Innkeeper
    eigenvectors: {warmth: 0.8, curiosity: 0.6, trust: 0.7}
    initial_region: inn
  - name: Bob
    archetype: Builder
    eigenvectors: {warmth: 0.5, curiosity: 0.4, trust: 0.6}
    initial_region: square
  - name: Clara
    archetype: Curious
    eigenvectors: {warmth: 0.6, curiosity: 0.9, trust: 0.5}
    initial_region: inn

regions:
  - name: inn
    connections: [square]
  - name: square
    connections: [inn]
```

### MPP Test Targets

| Test | Verified Claim |
|------|---------------|
| `test_citizen_polynomial_laws` | Identity/associativity hold |
| `test_operad_preconditions` | Locality law enforced |
| `test_memory_persistence` | State survives restart |
| `test_step_advances_time` | Simulation progresses |
| `test_tension_index_computes` | Metrics observable |

---

## Token Budget Dashboard

```bash
# New command: kgents town budget

$ kgents town budget
Agent Town Budget Status
========================
Monthly cap:      10,000,000 tokens
Spent this month:  2,345,678 tokens (23%)
Daily average:       156,379 tokens
Days remaining:           25 days
Projected monthly: 4,691,370 tokens (47% of cap)

LOD Breakdown:
  LOD 0-1 (haiku):   1,234,567 tokens (53%)
  LOD 2-3 (sonnet):    876,543 tokens (37%)
  LOD 4-5 (opus):      234,568 tokens (10%)

Status: ON BUDGET
```

### CI Budget Check

```python
# In CI pipeline

def test_budget_projection():
    """Fail if projected monthly > 90% of cap."""
    status = get_budget_status()
    assert status.projected_monthly < status.monthly_cap * 0.9, (
        f"Budget projection {status.projected_monthly} exceeds 90% of cap"
    )
```

---

## Staged Autopoiesis (Safe Self-Modification)

**Instead of "self-modifying in prod":**

```
┌────────────────────────────────────────────────────────────────┐
│                    TERRARIUM STAGING LOOP                       │
│                                                                 │
│  1. SNAPSHOT: Capture current citizen state                    │
│  2. SANDBOX: Deploy modification to isolated terrarium         │
│  3. SHADOW: Route shadow traffic (duplicate requests)          │
│  4. HEALTH: Check behavioral health gates                      │
│  5. GATES: Pass safety score threshold                         │
│  6. PROMOTE: Manual approval + promotion to production         │
│  7. ROLLBACK: Auto-rollback on violation (D-gent temporal)     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Failure Modes (Tested)

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Budget exhaustion | CI check fails | Reduce LOD tier; pause simulation |
| Invalid transition | PolyAgent rejects | Log + return to previous state |
| Identity-law violation | Property test fails | Quarantine + manual review |
| Coherence violation | Sheaf check fails | Reconciliation via council |
| Adversarial prompt | Red-team harness blocks | Reject + log |

---

## Exit Criteria (Phase 1 MVP)

- [ ] 7 citizens instantiated with distinct personalities
- [ ] Daily cycle runs autonomously
- [ ] Emergent interactions (not scripted)
- [ ] Memory persists across sessions
- [ ] User can observe, whisper, inhabit, intervene
- [ ] `kg town` CLI commands working
- [ ] Drama emerges from agent interaction
- [ ] Kent says "this is amazing"

---

## Continuation

**Full N-phase cycle prompt**: `prompts/agent-town-mpp-implement.md`

### Quick Start (Copy-Paste)

```markdown
⟿[IMPLEMENT] Agent Town Minimal Playable Prototype

/hydrate

handles:
  - plan: plans/crown-jewel-next.md
  - manifest_schema: spec/town/manifest.schema.yaml
  - operad_spec: spec/town/operad.md
  - heritage: spec/heritage.md
  - grand_narrative: spec/GRAND_NARRATIVE.md
  - poly_reference: impl/claude/agents/poly/protocol.py
  - dgent_reference: impl/claude/agents/d/polynomial.py
  - operad_reference: impl/claude/agents/operad/domains.py
  - cli_reference: impl/claude/protocols/cli/handlers/operad.py

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: in_progress  # ← START HERE
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.10
  spent: 0.05
  remaining: 0.05

## Mission

Implement Agent Town MPP:
- 3 citizens (Alice, Bob, Clara)
- 2 regions (Inn, Square)
- 4 operad ops (greet, gossip, trade, solo)
- CLI: `kgents town {start,step,observe}`

## Sequence

1. CitizenPolynomial → impl/claude/agents/town/polynomial.py
2. TownOperad → impl/claude/agents/town/operad.py
3. Citizen + Fixtures → impl/claude/agents/town/citizen.py
4. TownEnvironment → impl/claude/agents/town/environment.py
5. TownFlux → impl/claude/agents/town/flux.py
6. CLI Handler → impl/claude/protocols/cli/handlers/town.py
7. Metrics → impl/claude/agents/town/metrics.py

## Exit Criteria

- [ ] All modules created
- [ ] 20+ tests passing
- [ ] `kgents town step` works
- [ ] tension_index computes

## Exit → QA

⟿[QA] mypy, ruff, security, law verification

void.entropy.sip(amount=0.05). The ground is always there.
```

---

*void.gratitude.tithe. The town awaits its citizens.*
