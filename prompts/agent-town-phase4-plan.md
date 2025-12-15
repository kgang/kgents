# Agent Town Phase 4: Civilizational Scale

> *"From hamlet to metropolis. From 10 citizens to 25. From terminal to Web UI. The simulation park awakens."*

---

## ATTACH

/hydrate

You are entering **PLAN** phase of the N-Phase Cycle (AD-005) for Agent Town Phase 4.

---

## Heritage Context (from `plans/_focus.md`)

Kent's vision draws from five seminal papers—understand them as conceptual ancestors:

| Paper | Key Insight | Phase 4 Application |
|-------|-------------|---------------------|
| **CHATDEV** (arXiv:2307.07924) | Multi-agent software dev with roles | Citizens with specialized roles (Builder, Trader, Healer) |
| **SIMULACRA** (arXiv:2304.03442) | Generative agents with memory streams | GraphMemory + eigenvector personality → emergent behavior |
| **ALTERA** (arXiv:2411.00114) | Long-horizon agent planning | NPHASE_OPERAD → multi-turn evolution cycles |
| **VOYAGER** (arXiv:2305.16291) | Open-ended learning, skill libraries | Citizen skill acquisition via accursed share |
| **AGENT HOSPITAL** (arXiv:2405.02957) | Domain-specific simulation (medical) | Town as domain-agnostic template for vertical simulations |

**Guiding Principle**: West World-like simulation with holographic depth. Every citizen is a handle yielding different affordances to different observers (umwelt).

---

## Context from Phase 3 (Complete)

### Artifacts Created
- `impl/claude/agents/town/memory.py` — GraphMemory with k-hop BFS, decay, reinforcement
- `impl/claude/agents/town/functor.py` — TOWN→NPHASE functor with verified laws
- `impl/claude/agents/town/evolving.py` — EvolvingCitizen with SENSE→ACT→REFLECT cycle
- `impl/claude/protocols/nphase/operad.py` — NPHASE_OPERAD with phase laws

### Current State
- **Citizens**: 10 (7 static: Ada, Ben, Cal, Dia, Eve, Fay, Gil; 3 evolving: Hana, Igor, Juno)
- **Tests**: 379 passing
- **Architecture**: CitizenPolynomial → TownFlux → EvolvingCitizen

### Key Decisions Made
- Eigenvector drift capped at 0.1 per cycle (prevents personality collapse)
- GraphMemory uses trust-weighted edges (from D-gent garden pattern)
- NPHASE_OPERAD defines SENSE >> ACT >> REFLECT >> (loop)

### Blockers
- None from Phase 3

---

## Your Mission (PLAN Phase)

Shape Phase 4 scope with these targets:

### Target 1: Scale to 25 Citizens

Expand from 10 to 25 citizens with:

1. **Archetypes** (inspired by heritage papers):
   - **Builders** (CHATDEV): Construct town infrastructure
   - **Traders** (economic): Resource exchange
   - **Healers** (AGENT HOSPITAL): Social/emotional repair
   - **Scholars** (VOYAGER): Skill discovery and teaching
   - **Watchers** (SIMULACRA): Memory witnesses, historians

2. **Emergent Dynamics**:
   - Coalition formation (3+ citizens aligning on goals)
   - Reputation propagation (gossip affects eigenvectors)
   - Resource scarcity (drives conflict/cooperation)
   - Generational memory (old citizens mentor new)

3. **Personality Space**:
   - 5D eigenvector → 7D (add `resilience`, `curiosity`)
   - Cosmotechnics expanded (8 worldviews → 12)
   - Relationship graph with typed edges (mentor, rival, ally, stranger)

### Target 2: Web UI (Terrarium Visualization)

Build real-time town observation interface:

1. **Dashboard Components**:
   - Town map (citizen positions, relationships as edges)
   - Citizen inspector (eigenvectors, memory graph, evolution history)
   - Event stream (timestamped actions: gossip, trade, mourn, celebrate)
   - Phase indicator (SENSE/ACT/REFLECT for each citizen)

2. **Technology Stack**:
   - **marimo** (reactive notebooks) OR **Textual** (TUI) → choose one
   - WebSocket bridge for real-time updates
   - NATS streaming for event distribution (existing `nats_bridge.py`)

3. **Observer Umwelt**:
   - Different views for different observers (economist sees trades, poet sees emotions)
   - Holographic principle: single town state → multiple projections

### Target 3: Monetization Hook

Prepare for commercial deployment:

1. **Tiered Simulation**:
   - Free: 10 citizens, 1 day cycles
   - Pro: 25 citizens, unlimited cycles, custom archetypes
   - Enterprise: 100+ citizens, domain-specific templates (hospital, market, school)

2. **API Surface**:
   - `/town/create` — Spawn simulation
   - `/town/{id}/step` — Advance one cycle
   - `/town/{id}/citizen/{name}` — Inspect citizen
   - `/town/{id}/events` — SSE stream of events

3. **Metering Integration**:
   - Per-citizen-turn metering (existing `openmeter_client.py`)
   - Token budget awareness (citizens cost API tokens when LLM-backed)

---

## Non-Goals (Scope Boundaries)

- **NOT** building full LLM dialogue for all 25 citizens (too expensive; use k-gent for 3-5, rules for rest)
- **NOT** persistent database (in-memory for Phase 4; Phase 5 adds SQLite)
- **NOT** multi-tenancy (single simulation per process for Phase 4)
- **NOT** mobile UI (desktop/web only)

---

## Proposed Chunks

| Chunk | Description | Depends On | Parallelizable |
|-------|-------------|------------|----------------|
| 4.1 | Extended Eigenvectors (7D) + 12 Cosmotechnics | — | Yes |
| 4.2 | 15 New Citizens (5 archetypes × 3 each) | 4.1 | Yes |
| 4.3 | Coalition/Reputation Mechanics | 4.2 | No |
| 4.4 | Web UI Scaffold (marimo or Textual) | — | Yes (parallel with 4.1-4.3) |
| 4.5 | Real-time Event Bridge (WebSocket/NATS) | 4.4 | No |
| 4.6 | Dashboard Panels (map, inspector, stream) | 4.5 | No |
| 4.7 | API Surface + Metering | 4.3 | No |
| 4.8 | Integration Tests + Demo Script | 4.6, 4.7 | No |

**Parallel Tracks**:
- Track A: 4.1 → 4.2 → 4.3 → 4.7 (citizens/mechanics)
- Track B: 4.4 → 4.5 → 4.6 (UI)
- Merge: 4.8 (integration)

---

## Entropy Budget

| Phase | Allocation | Purpose |
|-------|------------|---------|
| PLAN | 5% | Scope exploration, heritage paper insights |
| RESEARCH | 10% | marimo vs Textual evaluation, WebSocket patterns |
| DEVELOP | 5% | API design alternatives |
| IMPLEMENT | 10% | Wiring experiments, dead-end recovery |
| REFLECT | 5% | Meta-learning capture |

**Total**: 35% reserved for exploration. Draw: `void.entropy.sip(amount=0.07)` per phase.

---

## Exit Criteria (PLAN Phase)

- [ ] Chunks defined with dependencies
- [ ] Technology choice for UI (marimo vs Textual) identified as RESEARCH question
- [ ] Non-goals documented
- [ ] Attention budget allocated
- [ ] Entropy sip recorded
- [ ] Continuation prompt for RESEARCH generated

---

## Questions for RESEARCH Phase

1. **UI Technology**: marimo (reactive notebook) vs Textual (TUI)? Which aligns with Kent's "VISUAL UIs" intent?
2. **LLM Budget**: How many of 25 citizens can be LLM-backed affordably? Rules-based fallback pattern?
3. **Coalition Detection**: Graph algorithm for coalition formation (clique finding)?
4. **Reputation Propagation**: PageRank variant or simpler diffusion model?
5. **Metering Granularity**: Per-turn vs per-citizen-day billing?

---

## Process Metrics Snapshot

| Metric | Value |
|--------|-------|
| Phase | PLAN |
| Tokens in | ~0 |
| Tokens out | ~0 |
| Time (est) | 15 min |
| Entropy sip | 0.05 |
| Laws verified | N/A (PLAN) |
| Branches surfaced | 2 (UI tech, LLM budget) |

---

## Phase Ledger

```yaml
phase_ledger:
  PLAN: pending
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
  planned: 0.35
  spent: 0.0
  returned: 0.0
```

---

## Continuation Imperative

Upon completing PLAN, emit the continuation prompt for RESEARCH.

---

# Continuation Prompts for Subsequent Phases

## ⟿[RESEARCH] — After PLAN

```markdown
⟿[RESEARCH]

# Agent Town Phase 4: RESEARCH

## ATTACH

/hydrate

You are entering **RESEARCH** phase for Agent Town Phase 4.

handles: chunks=4.1-4.8; scope=25_citizens+web_ui+api; non_goals=llm_all,persistence,multi_tenant; ledger={PLAN:touched}; entropy=0.05/0.35

---

## Mission

Map terrain for Phase 4 implementation:

1. **UI Technology Evaluation**:
   - Read `impl/claude/agents/i/` (existing I-gent Textual code)
   - WebSearch: "marimo reactive notebooks 2025 real-time"
   - WebSearch: "Textual TUI WebSocket integration"
   - Decision matrix: reactivity, real-time updates, deployment ease

2. **Coalition/Reputation Algorithms**:
   - Read `impl/claude/agents/d/graph.py` (existing graph patterns)
   - WebSearch: "clique detection social networks algorithms"
   - WebSearch: "reputation propagation PageRank variants"

3. **LLM Budget Analysis**:
   - Estimate tokens/citizen/turn (from k-gent patterns)
   - Design rules-based fallback for non-LLM citizens
   - Read `impl/claude/protocols/billing/` for metering patterns

4. **Prior Art Check**:
   - Verify no existing town/simulation code duplicates proposed work
   - Check `agents/` for composable components

---

## File Targets

- `impl/claude/agents/i/screens/` — Textual patterns
- `impl/claude/agents/d/graph.py` — Graph algorithms
- `impl/claude/agents/town/` — Current town implementation
- `impl/claude/protocols/api/` — API patterns
- `impl/claude/protocols/streaming/nats_bridge.py` — Event streaming

---

## Exit Criteria

- [ ] UI technology decision documented with rationale
- [ ] Coalition algorithm selected
- [ ] LLM budget model defined (N LLM-backed, M rules-based)
- [ ] File map with invariants captured
- [ ] Blockers enumerated (or "none")
- [ ] ledger.RESEARCH=touched

---

## Continuation

exit: file_map + decisions + blockers; continuation → DEVELOP.

⟂[BLOCKED:ui_unclear] Need human input on marimo vs Textual preference
⟂[BLOCKED:budget_unknown] Token costs unclear, need profiling
```

---

## ⟿[DEVELOP] — After RESEARCH

```markdown
⟿[DEVELOP]

# Agent Town Phase 4: DEVELOP

## ATTACH

/hydrate

You are entering **DEVELOP** phase for Agent Town Phase 4.

handles: ui_choice=${ui_decision}; coalition_algo=${algo}; llm_budget=${budget_model}; files=${file_map}; ledger={RESEARCH:touched}; entropy=${remaining}

---

## Mission

Design specs and contracts:

1. **Extended Eigenvectors**:
   ```python
   @dataclass(frozen=True)
   class Eigenvectors7D:
       curiosity: float      # [0,1] drive to explore
       sociability: float    # [0,1] seek others
       ambition: float       # [0,1] pursue goals
       empathy: float        # [0,1] feel others
       resilience: float     # [0,1] recover from setbacks (NEW)
       creativity: float     # [0,1] novel solutions (NEW)
       cosmotechnics: Cosmotechnics12  # 12 worldviews
   ```

2. **Citizen Archetypes**:
   - Define 5 archetype interfaces (Builder, Trader, Healer, Scholar, Watcher)
   - Each archetype: preferred operations, eigenvector biases, relationship patterns

3. **Coalition Protocol**:
   ```python
   @dataclass
   class Coalition:
       members: frozenset[str]  # citizen names
       goal: str
       strength: float  # [0,1]
       formation_turn: int

   def detect_coalitions(town: Town) -> list[Coalition]
   def coalition_action(coalition: Coalition, town: Town) -> TownEvent
   ```

4. **API Contract**:
   - OpenAPI spec for `/town/*` endpoints
   - SSE schema for event streaming
   - Metering hooks

5. **UI Wireframes**:
   - Town map layout (if Textual: ASCII grid; if marimo: plotly scatter)
   - Citizen inspector panel schema
   - Event stream format

---

## Laws to Preserve

- Eigenvector drift ≤ 0.1 per cycle (from Phase 3)
- NPHASE_OPERAD: SENSE >> ACT >> REFLECT
- Coalition strength ∈ [0, 1], decays without reinforcement
- API metering: idempotent recording

---

## Exit Criteria

- [ ] Eigenvectors7D spec
- [ ] Archetype interfaces (5)
- [ ] Coalition dataclass + detect/action signatures
- [ ] API contract draft
- [ ] UI wireframe sketch
- [ ] ledger.DEVELOP=touched

---

## Continuation

exit: specs + contracts + wireframes; continuation → STRATEGIZE.

⟂[BLOCKED:law_conflict] Proposed spec violates existing invariant
```

---

## ⟿[STRATEGIZE] — After DEVELOP

```markdown
⟿[STRATEGIZE]

# Agent Town Phase 4: STRATEGIZE

## ATTACH

/hydrate

You are entering **STRATEGIZE** phase for Agent Town Phase 4.

handles: specs=${spec_files}; contracts=${contracts}; wireframes=${wireframes}; ledger={DEVELOP:touched}; entropy=${remaining}

---

## Mission

Choose implementation path:

1. **Track Ordering**:
   - Confirm parallel tracks (A: citizens, B: UI) can proceed independently
   - Identify merge points and sync requirements

2. **Risk Assessment**:
   - UI tech risk (new library learning curve?)
   - LLM cost risk (token budget overrun?)
   - Integration risk (NATS bridge + WebSocket combo?)

3. **Alternative Paths**:
   - Path A: Full implementation (8 chunks, ~500 tests)
   - Path B: MVP (5 chunks: 4.1, 4.2, 4.4, 4.5, 4.8; defer coalition/API)
   - Path C: UI-first (prove visualization, add citizens incrementally)

4. **Decision**: Commit to one path.

---

## Exit Criteria

- [ ] Path selected with rationale
- [ ] Risk mitigations documented
- [ ] Chunk sequence finalized
- [ ] ledger.STRATEGIZE=touched

---

## Continuation

exit: chosen_path + sequence + risks; continuation → CROSS-SYNERGIZE.

⟂[BLOCKED:path_unclear] Multiple viable paths, need human preference
```

---

## ⟿[CROSS-SYNERGIZE] — After STRATEGIZE

```markdown
⟿[CROSS-SYNERGIZE]

# Agent Town Phase 4: CROSS-SYNERGIZE

## ATTACH

/hydrate

You are entering **CROSS-SYNERGIZE** phase for Agent Town Phase 4.

handles: path=${chosen_path}; sequence=${chunk_sequence}; ledger={STRATEGIZE:touched}; entropy=${remaining}

---

## Mission

Compose with adjacent work:

1. **AGENTESE REPL** (65% complete):
   - Can town events flow through REPL? (`town.citizen.ada.manifest`)
   - Add `town.*` context to AGENTESE paths?

2. **K-gent Integration**:
   - K-gent as town narrator/observer?
   - Citizen dialogue via k-gent's LLM backbone?

3. **I-gent Dashboard**:
   - Reuse I-gent Textual patterns for town UI?
   - Share screen mixins (navigation, help)?

4. **Monetization Plan** (0%):
   - API surface aligns with SaaS billing?
   - Metering hooks match openmeter_client patterns?

---

## Exit Criteria

- [ ] AGENTESE path extension documented (or deferred)
- [ ] K-gent integration plan (or deferred)
- [ ] I-gent code reuse identified
- [ ] Metering alignment confirmed
- [ ] ledger.CROSS-SYNERGIZE=touched

---

## Continuation

exit: composition_map + reuse_list; continuation → IMPLEMENT.

⟂[BLOCKED:conflict] Proposed composition breaks existing agent
```

---

## ⟿[IMPLEMENT] — After CROSS-SYNERGIZE

```markdown
⟿[IMPLEMENT]

# Agent Town Phase 4: IMPLEMENT

## ATTACH

/hydrate

You are entering **IMPLEMENT** phase for Agent Town Phase 4.

handles: composition_map=${comp}; reuse=${reuse_list}; sequence=${chunks}; ledger={CROSS-SYNERGIZE:touched}; entropy=${remaining}

---

## Mission

Execute chunks per sequence:

### Chunk 4.1: Extended Eigenvectors
- CREATE `impl/claude/agents/town/eigenvectors.py`
- 7D eigenvectors, 12 cosmotechnics
- Tests: 20+

### Chunk 4.2: 15 New Citizens
- MODIFY `impl/claude/agents/town/environment.py`
- Add archetypes: Builder, Trader, Healer, Scholar, Watcher
- Tests: 30+

### Chunk 4.3: Coalition/Reputation
- CREATE `impl/claude/agents/town/coalition.py`
- Detection, action, decay
- Tests: 25+

### Chunk 4.4: UI Scaffold
- CREATE `impl/claude/agents/i/screens/town.py` (if Textual)
- OR `impl/claude/notebooks/town.py` (if marimo)
- Tests: 15+

### Chunk 4.5: Event Bridge
- MODIFY `impl/claude/protocols/streaming/nats_bridge.py`
- WebSocket/SSE for town events
- Tests: 15+

### Chunk 4.6: Dashboard Panels
- Map, inspector, event stream
- Tests: 20+

### Chunk 4.7: API Surface
- MODIFY `impl/claude/protocols/api/town.py`
- Endpoints + metering
- Tests: 20+

### Chunk 4.8: Integration
- Full cycle test: spawn → evolve → visualize → meter
- Tests: 25+

---

## Protocol

For each chunk:
1. `TodoWrite` — mark in_progress
2. `Edit/Write` — implement
3. `Bash(uv run pytest)` — verify
4. `Bash(uv run mypy)` — type check
5. `TodoWrite` — mark completed

---

## Exit Criteria

- [ ] All 8 chunks complete
- [ ] 550+ tests passing (379 + ~170)
- [ ] mypy clean
- [ ] ledger.IMPLEMENT=touched

---

## Continuation

exit: files=${created}; tests=${count}; continuation → QA.

⟂[BLOCKED:tests_failing] Critical tests failing
⟂[BLOCKED:chunk_incomplete] Chunk not finished
```

---

## ⟿[QA] — After IMPLEMENT

```markdown
⟿[QA]

# Agent Town Phase 4: QA

## ATTACH

/hydrate

You are entering **QA** phase for Agent Town Phase 4.

handles: files=${impl_files}; tests=${test_count}; ledger={IMPLEMENT:touched}; entropy=${remaining}

---

## Mission

Gate quality before broad testing:

1. **Type Safety**: `uv run mypy impl/claude/agents/town/`
2. **Linting**: `uv run ruff check impl/claude/agents/town/`
3. **Security Sweep**: No secrets in code, no SQL injection (if any SQL)
4. **Law Verification**: Eigenvector bounds, NPHASE laws, coalition decay
5. **Docstring Audit**: Public APIs documented

---

## Exit Criteria

- [ ] mypy: 0 errors
- [ ] ruff: 0 errors (or documented exceptions)
- [ ] Security: no issues
- [ ] Laws: verified
- [ ] ledger.QA=touched

---

## Continuation

exit: qa_status=pass; continuation → TEST.

⟂[BLOCKED:type_errors] mypy failures
⟂[BLOCKED:security] Security issue found
```

---

## ⟿[TEST] — After QA

```markdown
⟿[TEST]

# Agent Town Phase 4: TEST

## ATTACH

/hydrate

You are entering **TEST** phase for Agent Town Phase 4.

handles: qa_status=pass; ledger={QA:touched}; entropy=${remaining}

---

## Mission

Broad test execution:

1. **Unit Tests**: `uv run pytest impl/claude/agents/town/ -v`
2. **Integration Tests**: `uv run pytest impl/claude/agents/town/_tests/test_phase4_integration.py -v`
3. **UI Tests**: Manual verification of dashboard (if applicable)
4. **Performance**: Measure step() time with 25 citizens

---

## Exit Criteria

- [ ] All tests passing
- [ ] No regressions in existing tests
- [ ] Performance acceptable (<1s per step with 25 citizens)
- [ ] ledger.TEST=touched

---

## Continuation

exit: test_results=${summary}; continuation → EDUCATE.

⟂[BLOCKED:test_failure] Tests failing
⟂[BLOCKED:regression] Existing tests broken
```

---

## ⟿[EDUCATE] — After TEST

```markdown
⟿[EDUCATE]

# Agent Town Phase 4: EDUCATE

## ATTACH

/hydrate

You are entering **EDUCATE** phase for Agent Town Phase 4.

handles: test_results=pass; ledger={TEST:touched}; entropy=${remaining}

---

## Mission

Document for future observers:

1. **README Update**: `impl/claude/agents/town/README.md`
   - Phase 4 features: 25 citizens, archetypes, UI, API
   - Quick start guide

2. **Skill Creation**: `docs/skills/town-simulation.md`
   - How to create custom citizens
   - How to add archetypes
   - How to extend UI panels

3. **CLAUDE.md Update**: Add town to agent table if not present

---

## Exit Criteria

- [ ] README complete
- [ ] Skill doc created
- [ ] CLAUDE.md updated (if needed)
- [ ] ledger.EDUCATE=touched

---

## Continuation

exit: docs=${doc_files}; continuation → MEASURE.

⟂[BLOCKED:docs_unclear] Documentation scope unclear
```

---

## ⟿[MEASURE] — After EDUCATE

```markdown
⟿[MEASURE]

# Agent Town Phase 4: MEASURE

## ATTACH

/hydrate

You are entering **MEASURE** phase for Agent Town Phase 4.

handles: docs=${doc_files}; ledger={EDUCATE:touched}; entropy=${remaining}

---

## Mission

Quantify Phase 4 outcomes:

1. **Test Metrics**:
   - Total tests: ? (target: 550+)
   - New tests added: ?
   - Coverage: ? (if measured)

2. **Code Metrics**:
   - New files: ?
   - Lines added: ?
   - Cyclomatic complexity: ?

3. **Performance Metrics**:
   - step() latency with 25 citizens
   - Memory footprint
   - API response time

4. **Process Metrics**:
   - Total time (all phases)
   - Entropy spent vs planned
   - Branches surfaced

---

## Exit Criteria

- [ ] Metrics captured
- [ ] Comparison to Phase 3 baseline
- [ ] ledger.MEASURE=touched

---

## Continuation

exit: metrics=${summary}; continuation → REFLECT.

⟂[BLOCKED:metrics_unavailable] Unable to collect metrics
```

---

## ⟿[REFLECT] — After MEASURE

```markdown
⟿[REFLECT]

# Agent Town Phase 4: REFLECT

## ATTACH

/hydrate

You are entering **REFLECT** phase for Agent Town Phase 4.

handles: metrics=${metrics}; ledger={MEASURE:touched}; entropy=${remaining}

---

## Mission

Distill learnings, prepare handoff:

1. **What Worked**:
   - List successes (patterns, decisions, tools)

2. **What Didn't**:
   - List challenges (blockers, rework, surprises)

3. **Learnings for meta.md**:
   - One line per insight (Molasses Test)
   - Example: "Coalition detection: clique > PageRank for small graphs"

4. **Phase 5 Seeds**:
   - What's next? (100 citizens? Persistence? Multi-tenancy?)
   - Bounty board entries

5. **Epilogue**:
   - Write `plans/_epilogues/2025-XX-XX-agent-town-phase4.md`

---

## Exit Criteria

- [ ] Learnings appended to `plans/meta.md`
- [ ] Epilogue written
- [ ] Phase 5 questions documented
- [ ] ledger.REFLECT=touched

---

## Continuation

⟂[DETACH:cycle_complete] Phase 4 complete; epilogue ready

OR

⟿[PLAN]
/hydrate
handles: learnings=${learnings}; phase5_seeds=${seeds}; ledger={REFLECT:touched}
mission: PLAN Phase 5 (100 citizens, persistence, multi-tenancy)
```

---

*"The town grows. The citizens evolve. The simulation awakens. Begin."*
