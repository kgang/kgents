---
path: agent-town/builders-workshop-chunk4
status: complete
progress: 100
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - agent-town/builders-workshop
session_notes: |
  CHUNK 4 COMPLETE: BUILDER_POLYNOMIAL implemented.

  DELIVERABLES:
  - agents/town/builders/__init__.py
  - agents/town/builders/polynomial.py (~400 lines)
  - agents/town/builders/_tests/__init__.py
  - agents/town/builders/_tests/test_builder_polynomial.py (71 tests)

  KEY TYPES:
  - BuilderPhase (6 positions): IDLE, EXPLORING, DESIGNING, PROTOTYPING, REFINING, INTEGRATING
  - BuilderInput (factory): assign, handoff, continue_work, complete, query_user, user_response, rest, wake
  - BuilderOutput: phase, success, message, artifact, next_builder, timestamp, metadata
  - BUILDER_POLYNOMIAL: PolyAgent[BuilderPhase, Any, BuilderOutput]

  DESIGN DECISIONS:
  - Handoffs are explicit and flexible (can skip/reverse phases)
  - RestInput → IDLE (graceful exit from any work phase)
  - TaskAssignInput can interrupt work phases
  - Archetype→phase mapping preserved in PHASE_ARCHETYPE_MAP
  - NATURAL_FLOW defines the typical progression
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  STRATEGIZE: skipped  # Strategy set in parent plan
  CROSS-SYNERGIZE: skipped  # No cross-plan deps for this chunk
  IMPLEMENT: complete
  QA: complete
  TEST: complete
  EDUCATE: skipped  # Doc-only deferred
  MEASURE: deferred
  REFLECT: complete
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.0
---

# Builder's Workshop: Chunk 4 - BUILDER_POLYNOMIAL

> *"The polynomial captures state-dependent behavior. A Builder in DESIGNING mode is categorically different from a Builder in PROTOTYPING mode."*

**AGENTESE Context**: `world.builder.*`
**Phase**: RESEARCH → DEVELOP → IMPLEMENT → TEST
**Parent Plan**: `plans/agent-town/builders-workshop.md`
**Heritage**: `impl/claude/agents/town/polynomial.py` (CitizenPolynomial)

---

## ATTACH

/hydrate plans/agent-town/builders-workshop.md

---

## Prior Session Summary (Chunks 1-3)

**Completed**:
1. **TelegramNotifier** (`agents/town/telegram_notifier.py`) - 400 lines, 27 tests
2. **Webhook Integration** (`protocols/api/webhooks.py`) - Auto-notify on payments
3. **CLI Commands** (`kg town telegram status|test|payment`)

**Blockers Resolved**: None (Telegram/Stripe creds still needed for live test)

---

## This Session: BUILDER_POLYNOMIAL (Chunk 4)

### Goal

Define `BUILDER_POLYNOMIAL` extending the `CitizenPolynomial` pattern with builder-specific positions and transitions.

### Research Questions

1. How does `CitizenPolynomial` define positions and transitions? (`agents/town/polynomial.py`)
2. What eigenvector dimensions should builders emphasize?
3. How do `PolyAgent[S, A, B]` semantics apply to builder state machines?
4. What are the composition laws for builder transitions?

### Deliverables

| Artifact | Location | Tests |
|----------|----------|-------|
| `BUILDER_POLYNOMIAL` | `agents/town/builders/polynomial.py` | 15+ |
| `BuilderPhase` enum | Same file | - |
| `BuilderInput` dataclass | Same file | - |
| `BuilderTransition` function | Same file | 10+ |
| Integration with `Citizen` base | Same file | 5+ |

### Key Types (from parent plan)

```python
from agents.town.polynomial import CitizenPolynomial, PolyAgent

class BuilderPhase(Enum):
    """Builder-specific polynomial positions."""
    IDLE = auto()        # Awaiting task
    EXPLORING = auto()   # Scout's specialty
    DESIGNING = auto()   # Sage's specialty
    PROTOTYPING = auto() # Spark's specialty
    REFINING = auto()    # Steady's specialty
    INTEGRATING = auto() # Sync's specialty

@dataclass(frozen=True)
class BuilderInput:
    """Input to builder polynomial transition."""
    task: str | None = None
    handoff_from: str | None = None  # Builder ID
    artifact: Any = None
    user_query: str | None = None

BUILDER_POLYNOMIAL: PolyAgent[BuilderPhase, BuilderInput, BuilderOutput] = ...
```

### Exit Criteria

- [ ] `BUILDER_POLYNOMIAL` defined with 6 positions
- [ ] `transition` function handles all position pairs
- [ ] Composition laws documented and tested
- [ ] Integrates with `Citizen` base class pattern
- [ ] 30+ tests passing

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Understand the existing polynomial infrastructure before building.

### Actions
1. Read `impl/claude/agents/town/polynomial.py` (CitizenPolynomial, CitizenPhase)
2. Read `docs/skills/polynomial-agent.md` for patterns
3. Read `spec/principles.md` AD-006 (Unified Categorical Foundation)
4. Identify eigenvector dimensions relevant to builders

### Exit Criteria
- [ ] CitizenPolynomial structure documented
- [ ] Builder-specific position set defined
- [ ] Eigenvector mapping for 5 builder archetypes drafted

### Minimum Artifact
Session notes with polynomial structure and builder position definitions.

### Continuation
On completion: `[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design the BUILDER_POLYNOMIAL API before implementation.

### Actions
1. Define `BuilderPhase` enum with 6 positions
2. Define `BuilderInput` dataclass with task, handoff, artifact, query
3. Define `BuilderOutput` dataclass with artifact, next_phase, message
4. Draft `transition(phase, input) -> (new_phase, output)` signature
5. Document composition laws (associativity, identity)

### Exit Criteria
- [ ] All types defined in design doc
- [ ] Transition matrix sketched (6x4 = 24 cases)
- [ ] Laws identified and named

### Minimum Artifact
Type definitions in `polynomial.py` stub (no implementation yet).

### Continuation
On completion: `[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT

<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Write the BUILDER_POLYNOMIAL implementation.

### Actions
1. Create `impl/claude/agents/town/builders/` directory structure
2. Implement `polynomial.py` with all types
3. Implement `transition` function for all 24 cases
4. Wire to `Citizen` base class (extend or compose)
5. Add logging/tracing for transitions

### Exit Criteria
- [ ] All types implemented
- [ ] Transition function handles all inputs
- [ ] No mypy errors
- [ ] Imports work from `agents.town.builders`

### Minimum Artifact
Working `polynomial.py` that can be imported.

### Continuation
On completion: `[TEST]`

</details>

---

## Phase: TEST

<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Verify BUILDER_POLYNOMIAL correctness and laws.

### Actions
1. Create `_tests/test_builder_polynomial.py`
2. Test each position transition
3. Test composition laws (associativity, identity)
4. Test edge cases (invalid inputs, null handling)
5. Test integration with Citizen base

### Exit Criteria
- [ ] 30+ tests passing
- [ ] All transition cases covered
- [ ] Law compliance verified
- [ ] No regressions in existing town tests

### Minimum Artifact
Test file with passing tests.

### Continuation
On completion: `[REFLECT]`

</details>

---

## Phase: REFLECT

<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Document learnings and update parent plan.

### Actions
1. Update `builders-workshop.md` session_notes
2. Note any design decisions for future reference
3. Identify what Chunk 5 (5 Builder classes) needs from this
4. Update progress percentage

### Exit Criteria
- [ ] Parent plan updated
- [ ] Learnings captured
- [ ] Ready for Chunk 5

### Minimum Artifact
Updated session_notes in parent plan.

### Continuation
`[COMPLETE]` - Chunk 4 done. Tithe remaining entropy.

</details>

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `agents/town/polynomial.py` | ~400 | CitizenPolynomial (heritage) |
| `agents/town/citizen.py` | ~600 | Citizen base class |
| `agents/town/eigenvector.py` | ~200 | 7D personality space |
| `docs/skills/polynomial-agent.md` | - | Patterns guide |

### Builder Eigenvector Profiles (Draft)

| Builder | Warmth | Curiosity | Trust | Creativity | Patience | Resilience | Ambition |
|---------|--------|-----------|-------|------------|----------|------------|----------|
| Sage | 0.7 | 0.5 | 0.8 | 0.6 | 0.9 | 0.8 | 0.5 |
| Spark | 0.8 | 0.9 | 0.6 | 0.95 | 0.3 | 0.5 | 0.7 |
| Steady | 0.6 | 0.4 | 0.9 | 0.4 | 0.95 | 0.9 | 0.4 |
| Scout | 0.5 | 0.95 | 0.5 | 0.7 | 0.6 | 0.6 | 0.6 |
| Sync | 0.9 | 0.6 | 0.7 | 0.5 | 0.7 | 0.7 | 0.8 |

### Transition Matrix (Draft)

| From \ To | IDLE | EXPLORING | DESIGNING | PROTOTYPING | REFINING | INTEGRATING |
|-----------|------|-----------|-----------|-------------|----------|-------------|
| IDLE | - | task_assign | task_assign | task_assign | task_assign | task_assign |
| EXPLORING | complete | - | handoff | handoff | - | handoff |
| DESIGNING | complete | - | - | handoff | handoff | handoff |
| PROTOTYPING | complete | - | - | - | handoff | handoff |
| REFINING | complete | - | - | - | - | handoff |
| INTEGRATING | complete | - | - | - | - | - |

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | touched | This document |
| RESEARCH | pending | - |
| DEVELOP | pending | - |
| STRATEGIZE | skipped | - |
| CROSS-SYNERGIZE | skipped | - |
| IMPLEMENT | pending | - |
| QA | pending | - |
| TEST | pending | - |
| EDUCATE | skipped | - |
| MEASURE | deferred | - |
| REFLECT | pending | - |

---

*"The form that generates forms."*
