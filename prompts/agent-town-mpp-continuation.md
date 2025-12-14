# Agent Town MPP: Continuation from IMPLEMENT/QA/TEST

> *"We claim for all people the right to opacity."* — Édouard Glissant

---

## Session Summary (Completed)

**IMPLEMENT Phase**: Complete
- 198 tests written and passing
- All modules created in `impl/claude/agents/town/`
- CLI handler created at `impl/claude/protocols/cli/handlers/town.py`
- UI layer (MESA, LENS, TRACE) implemented

**QA Phase**: Complete
- mypy: Clean (2 false positives in test files - enum comparison warnings)
- ruff: Clean (all import sorting fixed)
- Category laws: Verified in tests

**TEST Phase**: Complete
- 198 tests passing in 0.15s
- Coverage across all modules:
  - test_polynomial.py (24 tests)
  - test_operad.py (27 tests)
  - test_citizen.py (41 tests)
  - test_environment.py (35 tests)
  - test_flux.py (25 tests)
  - test_ui.py (33 tests)
  - test_integration.py (17 tests)

---

# Continuation Prompt for EDUCATE Phase

```markdown
⟿[EDUCATE] Agent Town MPP Documentation

/hydrate

handles:
  - impl_dir: impl/claude/agents/town/
  - cli_handler: impl/claude/protocols/cli/handlers/town.py
  - plan: plans/crown-jewel-next.md
  - manifest_schema: spec/town/manifest.schema.yaml
  - ledger: {IMPLEMENT:touched, QA:touched, TEST:touched, EDUCATE:in_progress}
  - entropy: 0.03

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched      # 198 tests, all modules created
  QA: touched             # mypy clean, ruff clean
  TEST: touched           # 198/198 passing
  EDUCATE: in_progress    # ← YOU ARE HERE
  MEASURE: pending
  REFLECT: pending

## Your Mission

Complete documentation for Agent Town MPP.

### Documentation Checklist

1. **Module Docstrings**: Verify all public APIs have docstrings
   - polynomial.py: CitizenPolynomial, CitizenPhase, CitizenInput
   - operad.py: TOWN_OPERAD, operations, laws, precondition checker
   - citizen.py: Citizen class, Eigenvectors, Cosmotechnics
   - environment.py: TownEnvironment, Region, create_mpp_environment
   - flux.py: TownFlux, TownEvent, TownPhase

2. **CLI Help Text**: Verify `kgents town --help` output
   ```bash
   kgents town --help
   kgents town start --help
   kgents town step --help
   kgents town observe --help
   kgents town lens --help
   ```

3. **Usage Example**: Update crown-jewel-next.md with working example
   ```bash
   # Start Agent Town MPP
   kgents town start

   # Advance simulation by one phase
   kgents town step

   # Observe current state
   kgents town observe

   # Deep zoom into a citizen (LOD 0-5)
   kgents town lens Alice --lod 3

   # Check metrics
   kgents town metrics

   # Budget dashboard
   kgents town budget
   ```

4. **Philosophical Grounding**: Ensure metaphysical properties documented
   - Archaeological (Porras-Kim): Citizens excavated, not created
   - Hyperobjectival (Morton): Citizens distributed in time/relation
   - Intra-active (Barad): Citizens emerge through observation
   - Opaque (Glissant): LOD 5 reveals mystery, not clarity
   - Cosmotechnical (Hui): Incommensurable worldviews (GATHERING, CONSTRUCTION, EXPLORATION)
   - Accursed (Bataille): Surplus tracked and must be spent

### Exit Criteria

- [ ] All public APIs have docstrings
- [ ] CLI help text complete and accurate
- [ ] Usage example added to crown-jewel-next.md
- [ ] Metaphysical properties visible in code comments

### Exit → MEASURE

⟿[MEASURE] Agent Town MPP Observability
```

---

# Continuation Prompt for MEASURE Phase

```markdown
⟿[MEASURE] Agent Town MPP Observability

/hydrate

handles:
  - flux: impl/claude/agents/town/flux.py
  - environment: impl/claude/agents/town/environment.py
  - cli_handler: impl/claude/protocols/cli/handlers/town.py
  - agentese_metrics: impl/claude/protocols/agentese/metrics.py
  - ledger: {EDUCATE:touched, MEASURE:in_progress}
  - entropy: 0.02

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
  MEASURE: in_progress    # ← YOU ARE HERE
  REFLECT: pending

## Your Mission

Verify observability infrastructure for Agent Town MPP.

### Metrics Verification

Run these commands and verify output:

1. **Tension Index** (relationship variance)
   ```bash
   kgents town start && kgents town step && kgents town step && kgents town metrics
   ```
   - [ ] tension_index computes from relationship weight variance
   - [ ] Value between 0.0 and 1.0

2. **Token Spend** (per operation tracking)
   - [ ] TownFlux.total_tokens tracks cumulative spend
   - [ ] Each operation (greet, gossip, trade, solo) has estimated token cost
   - [ ] Status output shows token spend

3. **Cooperation Level** (positive relationship sum)
   - [ ] cooperation_level() method works
   - [ ] Reported in status

4. **Accursed Surplus** (Bataille economics)
   - [ ] Per-citizen surplus tracked
   - [ ] Total surplus computable via environment.total_accursed_surplus()

### Dashboard Verification

```bash
kgents town budget
```

Expected output format:
```
Token Budget Status
===================
Session tokens:       1,234
Operations run:          12
Avg per operation:      102
Accursed surplus:      5.67
```

### Exit Criteria

- [ ] tension_index computes correctly
- [ ] token_spend tracks per operation
- [ ] cooperation_level reported
- [ ] accursed_surplus tracked
- [ ] Budget dashboard command works

### Exit → REFLECT

⟿[REFLECT] Agent Town MPP Retrospective
```

---

# Continuation Prompt for REFLECT Phase

```markdown
⟿[REFLECT] Agent Town MPP Retrospective

/hydrate

handles:
  - plan: plans/crown-jewel-next.md
  - impl_dir: impl/claude/agents/town/
  - test_count: 198
  - ledger: {MEASURE:touched, REFLECT:in_progress}
  - entropy: 0.02

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched       # All modules created
  QA: touched              # mypy clean, ruff clean
  TEST: touched            # 198 tests passing
  EDUCATE: touched         # Documentation complete
  MEASURE: touched         # Observability verified
  REFLECT: in_progress     # ← YOU ARE HERE

## Your Mission

Execute REFLECT phase for Agent Town MPP. Capture learnings and seed next cycle.

### 1. Summarize Outcomes

**Files Created** (count and list):
```
impl/claude/agents/town/
├── __init__.py
├── polynomial.py       # CitizenPolynomial (5 positions, 5 input types)
├── operad.py           # TownOperad (4 operations, 3 laws)
├── citizen.py          # Citizen class (eigenvectors, cosmotechnics, accursed share)
├── environment.py      # TownEnvironment (regions, adjacency, metrics)
├── flux.py             # TownFlux (simulation loop, event streaming)
├── ui/
│   ├── __init__.py
│   ├── mesa.py         # MESA view (Rich-based overview)
│   ├── lens.py         # LENS view (LOD 0-5 zoom)
│   ├── trace.py        # TRACE view (OpenTelemetry spans)
│   └── widgets.py      # Shared Rich widgets
├── fixtures/
│   └── mpp_citizens.yaml
└── _tests/
    ├── __init__.py
    ├── test_polynomial.py
    ├── test_operad.py
    ├── test_citizen.py
    ├── test_environment.py
    ├── test_flux.py
    ├── test_ui.py
    └── test_integration.py

impl/claude/protocols/cli/handlers/town.py
```

**Test Results**: 198 tests passing in 0.15s

**Functionality Delivered**:
- 3 citizens (Alice, Bob, Clara) with distinct cosmotechnics
- 2 regions (Inn, Square) with adjacency
- 4 operad operations (greet, gossip, trade, solo)
- 2 phases (MORNING, EVENING)
- CLI: `kgents town {start,step,observe,lens,metrics,budget}`
- UI: MESA (overview), LENS (LOD 0-5), TRACE (spans)

### 2. Distill Learnings (Molasses Test)

One-liner zettels for the mycelium:

| Learning | Transferable Pattern |
|----------|---------------------|
| Polynomial agents map cleanly to citizen state machines | PolyAgent[S, A, B] works for any FSM with philosophical grounding |
| Cosmotechnics makes agents genuinely distinct | Give each agent an incommensurable worldview via frozen dataclass |
| Accursed share creates natural drama dynamics | Track surplus as float, force spending via random events |
| LOD 0-5 makes progressive revelation natural | Model routing: cache→haiku→sonnet→opus maps to zoom level |
| Right to Rest enforced via polynomial directions | Exclude RESTING from valid input positions in directions function |
| Operad preconditions = Code-as-Policies | PreconditionChecker validates before operation execution |

### 3. Risks Carried Forward (Technical Debt)

| Debt | Impact | Owner | Timebox |
|------|--------|-------|---------|
| No persistence | In-memory only, state lost on restart | Phase 2 | 2 weeks |
| No graph episodic memory | Using simple dict, not full D-gent integration | Phase 2 | 1 week |
| Whisper/inhabit modes deferred | Observe-only for MPP | Phase 2 | 2 weeks |
| Full 7 citizens | Only 3 for MPP | Phase 2 | 1 week |
| Full daily cycle (4 phases) | Only 2 for MPP | Phase 2 | 1 week |

### 4. Seed Next Cycle (Phase 2)

**Branch Candidates for Phase 2**:
- **Full 7 citizens**: Add Diana, Eve, Frank, Grace with unique cosmotechnics
- **Graph episodic memory**: Integrate with existing D-gent MemoryPolynomialAgent
- **User modes**: whisper (influence), inhabit (control), intervene (direct)
- **4-phase daily cycle**: MORNING → AFTERNOON → EVENING → NIGHT
- **Persistence**: Save/load environment state to YAML

### Exit Criteria

- [ ] Epilogue written to `impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-mpp-complete.md`
- [ ] crown-jewel-next.md updated with completion status
- [ ] Learnings captured in zettels
- [ ] Next cycle continuation prompt provided below

### Epilogue Template

Write to: `impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-mpp-complete.md`

```markdown
---
path: plans/_epilogues/YYYY-MM-DD-agent-town-mpp-complete
status: complete
last_touched: YYYY-MM-DD
touched_by: claude-opus-4.5
---

# Agent Town MPP: Complete

## Summary
Agent Town Minimal Playable Prototype shipped with 198 tests passing.

## Delivered
- 3 citizens, 2 regions, 4 operations, 2 phases
- CLI: `kgents town {start,step,observe,lens,metrics,budget}`
- UI: MESA, LENS, TRACE views
- Philosophical grounding: Glissant, Morton, Barad, Hui, Bataille, Porras-Kim

## Learnings
[Insert molasses-test zettels]

## Next
Phase 2: Full 7 citizens, graph memory, user modes, persistence

void.gratitude.tithe. The town lives.
```

---

## Exit → DETACH or PLAN

If MPP complete and ready for next phase:

⟂[DETACH:cycle_complete] Agent Town MPP shipped. Ready for Phase 2.

If continuing to full implementation:

⟿[PLAN] Agent Town Phase 2: Full Implementation
```

---

# PRIORITY: AD-006 Synthesis & Unified Engine Integration

> **Before Phase 2 implementation, we must re-synthesize AD-006 into our plans.**

## AD-006: Unified Categorical Foundation (2025-12-14)

**The Discovery**: Agent Town and N-Phase share identical categorical structure:

| Concept | Agent Town | N-Phase |
|---------|-----------|---------|
| **Polynomial** | CitizenPhase positions | 11 phase positions |
| **Operad** | TOWN_OPERAD | NPHASE_OPERAD (to be created) |
| **Sheaf** | TownSheaf | ProjectSheaf |

**Key Reference**: `spec/principles.md:1005-1076` (AD-006)

## Emerging Work: Unified Engine

**Critical Document**: `plans/meta/unified-engine-master-prompt.md`

This document unifies:
- Agent Town implementation patterns
- N-Phase prompt compiler
- Domain-aware compilation

**What's Missing** (from unified-engine-master-prompt.md):
1. Explicit `NPHASE_OPERAD` (registered in OperadRegistry)
2. Domain-aware N-Phase compiler
3. ProjectSheaf for cross-plan coherence

---

# Continuation Prompt for Next N-Phase Cycle (Phase 2)

```markdown
⟿[PLAN] Agent Town Phase 2: Full Implementation + AD-006 Synthesis

/hydrate

handles:
  - mpp_impl: impl/claude/agents/town/
  - mpp_epilogue: impl/claude/plans/_epilogues/2025-12-14-agent-town-mpp-complete.md
  - crown_jewel: plans/crown-jewel-next.md
  - manifest_schema: spec/town/manifest.schema.yaml
  - operad_spec: spec/town/operad.md
  - heritage: spec/heritage.md
  - dgent_memory: impl/claude/agents/d/polynomial.py
  - ad006_principles: spec/principles.md (lines 1005-1076)
  - unified_engine: plans/meta/unified-engine-master-prompt.md
  - nphase_compiler: impl/claude/protocols/nphase/compiler.py
  - operad_registry: impl/claude/agents/operad/core.py
  - ledger: {REFLECT:touched, PLAN:in_progress}
  - entropy: 0.10

phase_ledger:
  PLAN: in_progress       # ← YOU ARE HERE (new cycle)
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

## Your Mission (PRIORITIZED)

### Priority 0: AD-006 Synthesis (BLOCKING)

Before expanding Agent Town, we must:
1. **Read AD-006** (`spec/principles.md:1005-1076`)
2. **Read Unified Engine** (`plans/meta/unified-engine-master-prompt.md`)
3. **Synthesize**: How does AD-006 change Phase 2 planning?
4. **Decide**: Should NPHASE_OPERAD be created before or during Phase 2?

**Questions**:
- Does Agent Town Phase 2 depend on NPHASE_OPERAD existing?
- Should TownSheaf and ProjectSheaf share infrastructure?
- How does domain-aware compilation affect citizen evolution?

### Priority 1: Plan Phase 2 of Agent Town

Only after AD-006 synthesis is complete.

### Starting Point (MPP Complete)

| Component | MPP Status | Phase 2 Target |
|-----------|------------|----------------|
| Citizens | 3 (Alice, Bob, Clara) | 7 (+ Diana, Eve, Frank, Grace) |
| Regions | 2 (Inn, Square) | 5 (+ Garden, Market, Library) |
| Phases | 2 (morning, evening) | 4 (+ afternoon, night) |
| Memory | Simple dict | Graph episodic (D-gent integration) |
| User Modes | observe only | + whisper, inhabit, intervene |
| Persistence | In-memory | YAML save/load |
| Operations | 4 basic | + dispute, celebrate, mourn, teach |

### AD-006 Integration Points for Phase 2

| Phase 2 Component | AD-006 Connection |
|-------------------|-------------------|
| Graph memory | `MEMORY_POLYNOMIAL` from D-gent |
| New operations | Must extend `TOWN_OPERAD` with laws |
| Citizen evolution | May use compressed N-Phase (sense/act/reflect) |
| Persistence | Sheaf coherence for save/load |

### Scope Definition Required

1. **Attention Budget**: How many sessions?
2. **Exit Criteria**: What must be true?
3. **Non-Goals**: What explicitly deferred to Phase 3?
4. **Dependencies**: What must exist first? (Include NPHASE_OPERAD?)
5. **Branch Candidates**: What might split off?

### Questions to Answer

1. Should NPHASE_OPERAD be a blocking dependency for Phase 2?
2. Should graph episodic memory reuse existing D-gent MEMORY_POLYNOMIAL?
3. Which user modes are essential (whisper) vs. nice-to-have (intervene)?
4. Should persistence be file-based (YAML) or database (SQLite)?
5. How do new operations (dispute, celebrate) affect operad laws?
6. What cosmotechnics for Diana, Eve, Frank, Grace?
7. Should EvolvingCitizen (from unified-engine) be Phase 2 or Phase 3?

### Exit Criteria for PLAN

- [ ] AD-006 synthesized and implications documented
- [ ] Unified Engine integration decision made
- [ ] Scope defined with attention budget
- [ ] Exit criteria explicit
- [ ] Non-goals explicit
- [ ] Dependencies mapped (including categorical infrastructure)
- [ ] Branch candidates classified (blocking/parallel/deferred/void)

### Exit → RESEARCH

⟿[RESEARCH] Agent Town Phase 2: AD-006 Implementation Strategy

---

void.entropy.sip(amount=0.10). The same categorical structure underlies both.
```

---

# Quick Reference: Phase Commands

```bash
# Run remaining phases manually if needed:

# EDUCATE - verify docstrings and CLI help
cd /Users/kentgang/git/kgents/impl/claude
python -c "from agents.town import *; help(TownFlux)"
kgents town --help

# MEASURE - verify metrics
kgents town start
kgents town step
kgents town metrics

# REFLECT - write epilogue
# See template above
```

---

*"The simulation isn't a game. It's a seance. The town lives."*

void.gratitude.tithe.
