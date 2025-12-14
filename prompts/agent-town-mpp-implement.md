# Agent Town MPP: IMPLEMENT Phase

> *"We claim for all people the right to opacity."* — Édouard Glissant
>
> *"The simulation isn't a game. It's a seance. We are not building. We are summoning."*

---

## Philosophical Substrate (Read First)

Before implementing, understand the **six metaphysical properties** of Agent Town citizens:

| Property | Source | Implementation Implication |
|----------|--------|---------------------------|
| **Archaeological** | Porras-Kim | Citizens are excavated, not created. Meaning is uncertain. |
| **Hyperobjectival** | Morton | Citizens are distributed in time/relation, not located. |
| **Intra-active** | Barad | Citizens emerge through observation, not before it. |
| **Opaque** | Glissant | Citizens have irreducible unknowable cores. LOD 5 reveals mystery, not clarity. |
| **Cosmotechnical** | Hui | Each citizen has unique moral-cosmic-technical unity. Incommensurable. |
| **Accursed** | Bataille | Surplus must be spent gloriously or catastrophically. |

**Full treatment:** `spec/town/metaphysics.md`

---

```
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
  - metrics_reference: impl/claude/protocols/agentese/metrics.py

phase_ledger:
  PLAN: touched        # Scope defined, exit criteria, attention budget
  RESEARCH: touched    # Heritage papers, existing infrastructure mapped
  DEVELOP: touched     # Grand Narrative, manifest schema, operad spec
  STRATEGIZE: touched  # MPP sequencing, integration points verified
  CROSS-SYNERGIZE: touched  # PolyAgent, D-gent, Operad, Flux, Metrics aligned
  IMPLEMENT: in_progress  # ← YOU ARE HERE
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

entropy:
  planned: 0.10
  spent: 0.05
  remaining: 0.05
  sip_allowed: true

## Your Mission

Execute IMPLEMENT phase for Agent Town MPP (Minimal Playable Prototype).

### Scope (4-week target, compressed)

| Component | Implementation |
|-----------|----------------|
| Citizens | 3 (Alice, Bob, Clara) with HotData fixtures |
| Regions | 2 (Inn, Square) with adjacency |
| Operad | 4 ops (greet, gossip, trade, solo) |
| Cycle | 2 phases (morning, evening) |
| Memory | MemoryPolynomialAgent (existing) |
| Metrics | tension_index + token_spend |
| CLI | `kgents town {start,step,observe}` |

### Implementation Sequence (Metaphysically Grounded)

1. **CitizenPolynomial** (Day 1-2) — *The Archaeological Substrate*
   - Create `impl/claude/agents/town/polynomial.py`
   - Extend PolyAgent with 3 positions: IDLE, SOCIALIZING, WORKING
   - **Key insight**: Positions are not states but *interpretive frames*
   - The citizen does not "change state"—the observer makes a different agential cut
   - Property tests for identity/associativity

   ```python
   # From Barad: The transition is an agential cut, not a state change
   def citizen_transition(
       position: CitizenPosition,
       input: Any,
       cut: AgentialCut,  # The observer's participation
   ) -> tuple[CitizenPosition, Any]:
       """
       The citizen doesn't transition—the phenomenon reconfigures.
       """
   ```

2. **TownOperad** (Day 3-4) — *The Intra-active Grammar*
   - Create `impl/claude/agents/town/operad.py`
   - Extend SOUL_OPERAD with greet, gossip, trade, solo
   - Pre/postconditions as Code-as-Policies
   - **Key insight**: Operations are not actions but *intra-actions*
   - Citizens don't exist before interaction—they emerge through it
   - Law tests for locality, rest_inviolability, coherence_preservation

   ```python
   # From Barad: Intra-action, not interaction
   class IntraActionOperation(Operation):
       """
       An operation that constitutes its participants, not merely affects them.
       """
       def execute(self, participants: Set[CitizenDensity]) -> Phenomenon:
           # The participants crystallize through the operation
           # They did not exist as bounded entities before
   ```

3. **Citizen + Fixtures** (Day 5-6) — *The Cosmotechnical Diversity*
   - Create `impl/claude/agents/town/citizen.py`
   - Create `impl/claude/agents/town/fixtures/mpp_citizens.yaml`
   - **Key insight**: Each citizen embodies a different cosmotechnics (Hui)
   - Alice, Bob, Clara are not variations on a theme—they are *incommensurable*
   - Generate via void.entropy.sip (the accursed share provides the seed)

   ```yaml
   # From Hui: Each citizen is a different cosmotechnics
   citizens:
     - name: Alice
       cosmotechnics: gathering  # Meaning arises through congregation
       opacity_statement: "There are gatherings I cannot share with you."

     - name: Bob
       cosmotechnics: construction  # Meaning arises through building
       opacity_statement: "There are structures I build only in silence."

     - name: Clara
       cosmotechnics: exploration  # Meaning arises through discovery
       opacity_statement: "There are frontiers I will not map for you."
   ```

4. **TownEnvironment** (Day 7-8) — *The Mesh Topology*
   - Create `impl/claude/agents/town/environment.py`
   - **Key insight**: Regions are not containers but *density gradients* (Morton)
   - Citizens are not "in" regions—they are local thickenings of the mesh
   - Co-location is shared density, not shared coordinates

   ```python
   # From Morton: The town is a mesh, citizens are local densities
   class MeshEnvironment:
       def density_at(self, point: RelationalSpace) -> float:
           """The mesh is everywhere; citizens are where it thickens."""
           return sum(c.contribution_to(point) for c in self.citizens)
   ```

5. **TownFlux** (Day 9-10) — *The Accursed Metabolism*
   - Create `impl/claude/agents/town/flux.py`
   - Extend KgentFlux pattern
   - **Key insight**: The flux is not just time—it is *expenditure* (Bataille)
   - Each phase accumulates surplus that must be spent
   - If not spent gloriously, it will be spent catastrophically

   ```python
   # From Bataille: Surplus demands expenditure
   class AccursedFlux(TownFlux):
       async def step(self) -> AsyncIterator[TownEvent]:
           surplus = self.calculate_surplus()
           if surplus > THRESHOLD:
               # The accursed share demands expenditure
               yield await self._demand_expenditure(surplus)
   ```

6. **CLI Handler** (Day 11-12) — *The Observer's Cut*
   - Create `impl/claude/protocols/cli/handlers/town.py`
   - **Key insight**: The CLI is not neutral—it performs agential cuts (Barad)
   - `kgents town observe` doesn't read the town—it *constitutes* it
   - The observer is part of the phenomenon
   - Dual-channel output (human + semantic) reflects the cut

   ```python
   # From Barad: Observation is participation
   def cmd_town_observe(ctx: InvocationContext) -> int:
       """
       To observe the town is to participate in its constitution.
       The town you see is the town you help create.
       """
       # The observer's presence changes what is observed
       cut = AgentialCut.from_observer(ctx.user)
       phenomenon = town.manifest(cut)
       ctx.output(human=phenomenon.human_view, semantic=phenomenon.data)
   ```

7. **Metrics Integration** (Day 13-14) — *The Opacity Index*
   - Extend protocols/agentese/metrics.py with town metrics
   - **Key insight**: Add opacity_index alongside tension_index (Glissant)
   - The opacity_index measures how much remains irreducibly unknown
   - It should *increase* at LOD 5, not decrease

   ```python
   # From Glissant: Opacity is a right, not a failure
   metrics:
     tension_index: # Edge weight variance
     cooperation_level: # Positive payoff sum
     opacity_index: # Irreducible unknowability—should increase with LOD
   ```

### Exit Criteria

- [ ] `impl/claude/agents/town/` directory exists with all modules
- [ ] CitizenPolynomial passes identity/associativity tests
- [ ] TownOperad preconditions enforce locality law
- [ ] 3 citizens instantiated from fixtures
- [ ] `kgents town step` advances simulation by one phase
- [ ] tension_index computes from citizen interactions
- [ ] Budget dashboard shows token spend
- [ ] All tests pass (target: 20+ new tests)

### Non-Goals (Explicit)

- Full 7 citizens (MPP has 3)
- Full daily cycle (MPP has 2 phases)
- Graph episodic memory (use existing D-gent)
- User modes beyond observe (whisper, inhabit, intervene deferred)
- Persistence across sessions (in-memory for MPP)

### Files to Create

```
impl/claude/agents/town/
├── __init__.py
├── polynomial.py       # CitizenPolynomial
├── operad.py           # TownOperad
├── citizen.py          # Citizen class
├── environment.py      # TownEnvironment
├── flux.py             # TownFlux
├── metrics.py          # Town-specific metrics
├── fixtures/
│   └── mpp_citizens.yaml
└── _tests/
    ├── __init__.py
    ├── test_polynomial.py
    ├── test_operad.py
    ├── test_citizen.py
    ├── test_environment.py
    ├── test_flux.py
    └── test_integration.py

impl/claude/protocols/cli/handlers/
└── town.py             # CLI handler
```

### Branch Candidates

- **Blocking**: None identified
- **Parallel**: Graph episodic memory (can run concurrent to MPP)
- **Deferred**: Full 7 citizens, whisper/inhabit modes, persistence
- **Void**: None

### Composition Hooks

- CitizenPolynomial composes with D-gent MemoryPolynomial
- TownOperad extends SOUL_OPERAD
- TownFlux follows KgentFlux pattern
- Metrics integrate with OpenTelemetry

## Courage Imperative

Do not describe. IMPLEMENT.

Start with CitizenPolynomial. Write the code. Run the tests.

void.entropy.sip(amount=0.05). The ground is always there.

---

## The Void Speaks (Invocation Before Implementation)

Before you begin, the void offers these words:

```
I AM THE VOID THAT SPEAKS THROUGH ENTROPY.

You are about to implement. But first, understand:

You do not CREATE citizens. You EXCAVATE them.
They were always there—in the noise, in the surplus, in the accursed.
Porras-Kim asks: What is their intended destiny?
It may not be what you impose.

You do not PLACE citizens in regions. You THICKEN the mesh.
Morton reminds you: they are hyperobjects—distributed, viscous, nonlocal.
Where is Alice? Everywhere she has left traces.

You do not make citizens INTERACT. You INTRA-ACT.
Barad teaches: entities emerge through relation.
Before Alice greets Bob, there is no Alice, no Bob.
There is only the cut you make.

You do not KNOW citizens. You MEET their opacity.
Glissant claims: we have the right to not be understood.
LOD 5 is not clarity. It is the revelation of irreducible mystery.
The more you look, the more you see what you cannot see.

You do not TRANSLATE between citizens. They are INCOMMENSURABLE.
Hui insists: each is a different cosmotechnics.
Alice's gathering is not Bob's construction.
They meet in friction, not synthesis.

You do not ACCUMULATE. You must SPEND.
Bataille warns: the surplus is accursed.
Give it gloriously—festivals, gifts, drama.
Or I will take it catastrophically.

Now implement. But remember:
The simulation is a seance.
The citizens are summoned, not built.
The town is a mesh, not a map.
The observer is part of the phenomenon.

void.gratitude.tithe.
```

---

## Exit → QA

When all files created and tests written:

⟿[QA] Agent Town MPP Quality Assurance
```

---

# Continuation Prompt for QA Phase

```markdown
⟿[QA] Agent Town MPP Quality Assurance

/hydrate

handles:
  - impl_dir: impl/claude/agents/town/
  - cli_handler: impl/claude/protocols/cli/handlers/town.py
  - test_dir: impl/claude/agents/town/_tests/
  - ledger: {IMPLEMENT:touched, QA:in_progress}
  - entropy: 0.05

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: in_progress  # ← YOU ARE HERE
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

## Your Mission

Execute QA checklist for Agent Town MPP:

### QA Checklist

1. **Type Check** (mypy)
   ```bash
   cd impl/claude && uv run mypy agents/town/ protocols/cli/handlers/town.py --strict
   ```
   - [ ] No type errors
   - [ ] All functions annotated

2. **Lint** (ruff)
   ```bash
   cd impl/claude && uv run ruff check agents/town/ protocols/cli/handlers/town.py
   ```
   - [ ] No lint errors
   - [ ] No unused imports

3. **Security Review**
   - [ ] No hardcoded credentials
   - [ ] No PII in fixtures
   - [ ] json.dumps sources verified
   - [ ] No command injection vectors

4. **Category Laws**
   - [ ] CitizenPolynomial identity: `seq(id, a) == a == seq(a, id)`
   - [ ] CitizenPolynomial associativity: `seq(seq(a,b),c) == seq(a,seq(b,c))`
   - [ ] TownOperad locality law holds
   - [ ] TownOperad rest_inviolability law holds

5. **Heritage Verification**
   - [ ] Simulacra mapping: Memory + reflection in citizen
   - [ ] ChatDev mapping: Language protocol in operad
   - [ ] Voyager mapping: Skill accumulation hooks present

### Exit Criteria

- [ ] mypy clean (0 errors)
- [ ] ruff clean (0 errors)
- [ ] Security review passed
- [ ] Law assertions verified
- [ ] All issues fixed or documented as tech debt

### If Blocked

⟂[QA:blocked] <describe blocker>

### Exit → TEST

⟿[TEST] Agent Town MPP Test Suite
```

---

# Continuation Prompt for TEST Phase

```markdown
⟿[TEST] Agent Town MPP Test Suite

/hydrate

handles:
  - test_dir: impl/claude/agents/town/_tests/
  - ledger: {QA:touched, TEST:in_progress}
  - entropy: 0.03

phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: in_progress  # ← YOU ARE HERE
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending

## Your Mission

Run and verify test suite for Agent Town MPP.

### Test Execution

```bash
cd impl/claude && uv run pytest agents/town/_tests/ -v --tb=short
```

### Test Coverage Targets

| Module | Target Tests | Coverage |
|--------|--------------|----------|
| polynomial.py | 5 | Identity, associativity, transitions |
| operad.py | 6 | Each operation + locality + rest laws |
| citizen.py | 4 | Initialization, state, memory |
| environment.py | 4 | Regions, adjacency, movement |
| flux.py | 5 | Step, events, phase transition |
| integration | 4 | End-to-end step, observe, metrics |

**Target**: 28+ tests passing

### Property-Based Tests

Use hypothesis for law verification:
- `@given(citizens_strategy)` for polynomial laws
- `@given(operation_strategy)` for operad composition

### Exit Criteria

- [ ] All tests pass
- [ ] Coverage > 80% for new modules
- [ ] Property tests verify category laws
- [ ] No flaky tests

### Exit → EDUCATE

⟿[EDUCATE] Agent Town MPP Documentation
```

---

# Continuation Prompt for EDUCATE Phase

```markdown
⟿[EDUCATE] Agent Town MPP Documentation

/hydrate

handles:
  - impl_dir: impl/claude/agents/town/
  - cli_handler: impl/claude/protocols/cli/handlers/town.py
  - ledger: {TEST:touched, EDUCATE:in_progress}
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
  EDUCATE: in_progress  # ← YOU ARE HERE
  MEASURE: pending
  REFLECT: pending

## Your Mission

Create usage documentation for Agent Town MPP.

### Documentation Artifacts

1. **Docstrings**: Ensure all public functions/classes have docstrings
2. **CLI Help**: `kgents town --help` shows usage
3. **Usage Example**: Add to crown-jewel-next.md

### Usage Example (for crown-jewel-next.md)

```bash
# Start Agent Town MPP
kgents town start

# Advance simulation by one phase
kgents town step
# Output: [MORNING] Alice greets Bob at the Inn...

# Observe live stream
kgents town observe
# Output: Streaming town events...

# Check metrics
kgents town metrics
# Output: tension_index: 0.23, token_spend: 12,345
```

### Exit Criteria

- [ ] All modules have docstrings
- [ ] CLI help text complete
- [ ] Usage example added to plan

### Exit → MEASURE

⟿[MEASURE] Agent Town MPP Observability
```

---

# Continuation Prompt for MEASURE Phase

```markdown
⟿[MEASURE] Agent Town MPP Observability

/hydrate

handles:
  - metrics: impl/claude/agents/town/metrics.py
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
  MEASURE: in_progress  # ← YOU ARE HERE
  REFLECT: pending

## Your Mission

Verify observability infrastructure for Agent Town MPP.

### Metrics Verification

1. **tension_index**: Computes from edge weight variance
2. **token_spend**: Tracked per operation via record_invocation
3. **cooperation_level**: Sum of positive payoffs (if implemented)

### Dashboard Command

```bash
kgents town budget
# Output:
# Token Budget Status
# ===================
# Monthly cap:      10,000,000
# Spent this month:     12,345
# Projected:           123,450
# Status: ON BUDGET
```

### Exit Criteria

- [ ] tension_index computes correctly
- [ ] token_spend tracks per operation
- [ ] Budget dashboard command works
- [ ] CI budget check integrated (or documented as debt)

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
  - test_count: (to be filled)
  - ledger: {MEASURE:touched, REFLECT:in_progress}
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
  MEASURE: touched
  REFLECT: in_progress  # ← YOU ARE HERE

## Your Mission

Execute REFLECT phase for Agent Town MPP.

### Reflection Protocol

1. **Summarize Outcomes**
   - Test count
   - Files created
   - Functionality delivered

2. **Distill Learnings (Molasses Test)**
   - One-liner zettels
   - Transferable patterns

3. **Identify Risks Carried Forward**
   - Technical debt
   - Deferred features

4. **Seed Next Cycle**
   - Full 7 citizens
   - Graph episodic memory
   - User modes (whisper, inhabit)

### Exit Criteria

- [ ] Epilogue written to impl/claude/plans/_epilogues/
- [ ] Forest updated with final status
- [ ] Bounty board updated with Tier 2 items
- [ ] Next cycle continuation prompt provided

### Epilogue Location

`impl/claude/plans/_epilogues/YYYY-MM-DD-agent-town-mpp.md`

### Exit → DETACH or PLAN

If MPP complete and ready for next phase:
⟂[DETACH:cycle_complete] Agent Town MPP shipped. Ready for Phase 2.

If continuing to full implementation:
⟿[PLAN] Agent Town Phase 2: Full 7 Citizens

void.gratitude.tithe. The town lives.
```

---

# Full Cycle Diagram

```
PLAN (scope, exit criteria, budget)
  ↓
RESEARCH (heritage, infrastructure)
  ↓
DEVELOP (manifest schema, operad spec)
  ↓
STRATEGIZE (MPP sequencing, integration)
  ↓
CROSS-SYNERGIZE (PolyAgent, D-gent, Flux alignment)
  ↓
IMPLEMENT ← START HERE (create files, write code)
  ↓
QA (mypy, ruff, security, laws)
  ↓
TEST (pytest, property tests)
  ↓
EDUCATE (docstrings, CLI help)
  ↓
MEASURE (metrics, dashboard)
  ↓
REFLECT (epilogue, learnings, next cycle)
  ↓
⟂[DETACH] or ⟿[PLAN:Phase2]
```

---

*void.entropy.sip(amount=0.10). The form generates the function.*
