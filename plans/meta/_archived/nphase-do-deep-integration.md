# N-Phase Deep Integration: `kg do` + Forest + NPhase Compiler

> *"The prompt that grows prompts. The forest that tends itself."*

**PHASE**: `PHASE=[PLAN|RESEARCH|DEVELOP|STRATEGIZE|CROSS-SYNERGIZE|IMPLEMENT|QA|TEST|EDUCATE|MEASURE|REFLECT]`

---

## ATTACH

/hydrate

---

## Project Overview

**Goal**: Deeply integrate the N-Phase Prompt Compiler with `kg do`, creating a unified natural language interface for forest management, agent streaming, and phase-aware execution.

**Non-Goals**:
- Replacing existing CLI commands (backward compatible)
- Building a full GUI (TUI via Textual is acceptable)
- External API integration (keep local-first)

**Parallel Tracks**:

| Track | Description |
|-------|-------------|
| T1 | Intent Router Enhancement (`kg do` expansion) |
| T2 | Forest Integration (tree operations) |
| T3 | Agent Stream + Turn-gent decision points |
| T4 | Completeness Auditor (principles alignment) |

**Key Decisions** (from prior sessions):
- **D1**: Python-first schema with frozen dataclasses (nphase already done)
- **D2**: Hardcoded phase templates (no runtime I/O)
- **D3**: Turn-gents for decision points (YIELD turns)
- **D4**: Forest Protocol for multi-session coordination

---

## Shared Context

### File Map

| Path | Lines | Purpose |
|------|-------|---------|
| `protocols/cli/intent/router.py` | 1-787 | Intent Router core (`kg do`) |
| `protocols/cli/handlers/forest.py` | 1-536 | Forest Protocol handler |
| `protocols/nphase/` | * | N-Phase Prompt Compiler (just built) |
| `protocols/cli/handlers/turns.py` | * | Turn-gent debugging/visualization |
| `protocols/cli/handlers/approve.py` | * | YIELD turn governance |
| `weave/turn.py` | * | Turn, TurnType, YieldTurn |
| `plans/_forest.md` | * | Forest health aggregation |

### Key Operations to Implement

| Operation | Intent Pattern | Description |
|-----------|----------------|-------------|
| `show forest` | "show forest", "forest health" | Display forest health summary |
| `list trees` | "list trees", "show plans" | List all plans with status |
| `show tree <name>` | "show tree X", "detail X" | Deep view of single plan |
| `stream <agent>` | "stream X", "watch agent X" | Live agent execution stream |
| `check completeness` | "check stage", "audit phase" | Pre-generated completeness check |
| `audit statuses` | "audit", "rebuild statuses" | Sync statuses from impl/metrics |
| `logs` | "show logs" | Status logs |
| `show stats` | "stats", "metrics" | Trees completed, progress, etc. |

### Invariants

| Name | Requirement | Verification |
|------|-------------|--------------|
| **Forest Consistency** | `_forest.md` reflects all plan headers | `kg forest check` |
| **Phase Accountability** | Each phase produces minimum artifact | `phase_ledger` tracking |
| **Turn-gent Governance** | YIELD turns require explicit approval | `kg pending` shows outstanding |
| **Principles Alignment** | Completeness check validates 7 principles | `kg judge` integration |

### Blockers

| ID | Description | Evidence | Resolution | Status |
|----|-------------|----------|------------|--------|
| B1 | Intent patterns need forest vocabulary | `router.py:114-142` | Add forest/tree patterns | open |
| B2 | No agent stream abstraction | - | Create `AgentStreamView` | open |
| B3 | Completeness check not codified | - | Define per-phase criteria | open |
| B4 | Status audit logic missing | - | Map impl→plan statuses | open |

### Components

| ID | Name | Location | Effort | Dependencies |
|----|------|----------|--------|--------------|
| C1 | IntentPatterns (Forest) | `intent/router.py` | S | - |
| C2 | ForestCommands | `intent/forest_ops.py` | M | C1 |
| C3 | AgentStreamView | `agents/i/reactive/streams/` | L | - |
| C4 | TurnGentDecisionUI | `agents/i/reactive/screens/` | M | C3 |
| C5 | CompletenessAuditor | `protocols/nphase/auditor.py` | M | - |
| C6 | StatusReconciler | `protocols/nphase/reconciler.py` | M | C5 |
| C7 | MilestoneLogger | `protocols/nphase/milestone.py` | S | - |
| C8 | ForestStats | `protocols/cli/handlers/forest.py` | S | - |
| C9 | UnifiedDoHandler | `intent/router.py` | M | C1,C2,C3,C5 |

### Waves

| Wave | Components | Strategy |
|------|------------|----------|
| Wave 1: Foundation | C1, C5, C7, C8 | Intent patterns + auditor + stats |
| Wave 2: Forest Ops | C2, C6 | Forest commands + status reconciliation |
| Wave 3: Streaming | C3, C4 | Agent stream + turn-gent UI |
| Wave 4: Integration | C9 | Unified `kg do` handler |

### Checkpoints

| ID | Name | Criteria |
|----|------|----------|
| CP1 | Intent Recognition | `kg do "show forest"` produces forest view |
| CP2 | Completeness Audit | `kg do "check phase"` validates current stage |
| CP3 | Agent Streaming | `kg do "stream soul"` shows live execution |
| CP4 | Full Integration | All 8 operations work via `kg do` |

---

## Cumulative State

### Handles Created

| Handle | Location | Phase |
|--------|----------|-------|
| `nphase.schema` | `protocols/nphase/schema.py` | IMPLEMENT |
| `nphase.templates` | `protocols/nphase/templates/` | IMPLEMENT |
| `nphase.compiler` | `protocols/nphase/compiler.py` | IMPLEMENT |
| `nphase.state` | `protocols/nphase/state.py` | IMPLEMENT |
| `nphase.cli` | `protocols/cli/handlers/nphase.py` | IMPLEMENT |

### Entropy Budget

**Total**: 0.75
**Remaining**: 0.75 (fresh allocation for this phase)

| Phase | Allocated | Spent |
|-------|-----------|-------|
| PLAN | 0.05 | 0.00 |
| RESEARCH | 0.10 | 0.00 |
| DEVELOP | 0.10 | 0.00 |
| STRATEGIZE | 0.05 | 0.00 |
| CROSS-SYNERGIZE | 0.05 | 0.00 |
| IMPLEMENT | 0.25 | 0.00 |
| QA | 0.05 | 0.00 |
| TEST | 0.05 | 0.00 |
| EDUCATE | 0.02 | 0.00 |
| MEASURE | 0.02 | 0.00 |
| REFLECT | 0.01 | 0.00 |

---

## Phase: PLAN
<details>
<summary>Expand if PHASE=PLAN</summary>

### Mission
Define scope, exit criteria, and attention budget. Draw entropy sip.

### Actions
1. Read existing context (nphase compiler, forest handler, intent router)
2. Clarify scope boundaries (what IS and ISN'T in scope)
3. Define exit criteria for this integration
4. Allocate entropy budget across phases
5. Identify parallel tracks (T1-T4)

### Phase-Specific Investigations
- What natural language patterns should trigger forest operations?
- How should agent streaming integrate with turn-gents?
- What constitutes "completeness" for each N-Phase stage?

### Exit Criteria
- [ ] 8 key operations defined with intent patterns
- [ ] Parallel tracks identified (T1: Intent, T2: Forest, T3: Stream, T4: Audit)
- [ ] Entropy budget allocated
- [ ] Non-goals explicit

### Minimum Artifact
Scope, exit criteria, attention budget, entropy sip

### Continuation
On completion: `⟿[RESEARCH]`

</details>

---

## Phase: RESEARCH
<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Map the terrain. Build file map, surface blockers with evidence.

### Actions
1. Search for existing forest/tree operations in codebase
2. Document file locations with line numbers
3. Identify blockers with file:line evidence
4. Note prior art that can be reused
5. Surface invariants from existing code

### Phase-Specific Investigations
- How does `forest_status()` aggregate plan data?
- What intent patterns exist in `INTENT_PATTERNS`?
- How does `AgentStreamView` work in reactive screens?
- What's the `YieldHandler` API for turn-gent governance?

### Exit Criteria
- [ ] File map complete with line references
- [ ] Blockers surfaced with evidence (B1-B4)
- [ ] Prior art documented (forest.py, turns.py, approve.py)
- [ ] Did NOT modify source files

### Minimum Artifact
File map + blockers with refs

### Continuation
On completion: `⟿[DEVELOP]`

</details>

---

## Phase: DEVELOP
<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design contracts and APIs. Define what will be built.

### Actions
1. Define data schemas/types for forest operations
2. Specify API contracts for AgentStreamView
3. Document invariants/laws for completeness auditor
4. Resolve blockers with design decisions
5. Create component breakdown (C1-C9)

### Phase-Specific Investigations
- What schema for `ForestOperation` dataclass?
- What events does `AgentStreamView` emit?
- How does `CompletenessAuditor` map phases to criteria?
- What's the `StatusReconciler` algorithm?

### Exit Criteria
- [ ] `ForestOperation`, `AgentStream`, `CompletenessReport` schemas defined
- [ ] API contracts for each component specified
- [ ] Invariants documented (Forest Consistency, Phase Accountability, etc.)
- [ ] All blockers resolved with decisions

### Minimum Artifact
Contract/API deltas or law assertions

### Continuation
On completion: `⟿[STRATEGIZE]`

</details>

---

## Phase: STRATEGIZE
<details>
<summary>Expand if PHASE=STRATEGIZE</summary>

### Mission
Sequence the work. Define waves and checkpoints.

### Actions
1. Order components by dependencies
2. Group into execution waves (Wave 1-4)
3. Define checkpoints between waves (CP1-CP4)
4. Identify parallelization opportunities
5. Set risk mitigation order

### Exit Criteria
- [ ] 4 waves defined with rationale
- [ ] 4 checkpoints specified
- [ ] Dependencies mapped (C1→C2→C9)
- [ ] Critical path identified

### Minimum Artifact
Sequencing with rationale

### Continuation
On completion: `⟿[CROSS-SYNERGIZE]`

</details>

---

## Phase: CROSS-SYNERGIZE
<details>
<summary>Expand if PHASE=CROSS-SYNERGIZE</summary>

### Mission
Find compositions. Identify cross-cutting concerns and synergies.

### Actions
1. Identify shared types/interfaces (nphase schema reuse)
2. Find cross-plan dependencies (forest ↔ nphase ↔ intent)
3. Document runtime compositions (stream + turn-gent)
4. Note potential conflicts
5. Design integration points

### Phase-Specific Synergies
- `ProjectDefinition` from nphase → `PlanHeader` from forest
- `PhaseStatus` → forest `status` field mapping
- `Turn` events → `AgentStreamView` updates
- `YieldTurn` → TUI decision point

### Exit Criteria
- [ ] nphase ↔ forest schema mapping documented
- [ ] Turn ↔ AgentStream event flow designed
- [ ] YIELD ↔ TUI decision point wired
- [ ] No conflicts (or conflicts resolved)

### Minimum Artifact
Named compositions or explicit skip

### Continuation
On completion: `⟿[IMPLEMENT]`

</details>

---

## Phase: IMPLEMENT
<details>
<summary>Expand if PHASE=IMPLEMENT</summary>

### Mission
Write the code. Execute the plan.

### Actions
1. Follow wave sequence (Wave 1 → Wave 4)
2. Implement each component (C1-C9)
3. Run tests as you go
4. Document deviations from plan
5. Update handles with new artifacts

### Wave 1 Implementation
```python
# C1: Add forest intent patterns to INTENT_PATTERNS
IntentCategory.FOREST = "forest"  # new category
INTENT_PATTERNS[IntentCategory.FOREST] = [
    r"\b(forest|trees?|plans?|show|list|status)\b",
]

# C5: CompletenessAuditor
class CompletenessAuditor:
    def audit_phase(self, project: ProjectDefinition, phase: str) -> CompletenessReport:
        ...

# C7: MilestoneLogger
class MilestoneLogger:
    def log(self, tree: str, milestone: str) -> None:
        ...

# C8: ForestStats
def forest_stats() -> ForestStatsReport:
    ...
```

### Wave 2-4: Continue per STRATEGIZE wave plan

### Exit Criteria
- [ ] All 9 components implemented
- [ ] Tests passing locally
- [ ] No new blockers introduced
- [ ] Handles updated

### Minimum Artifact
Code changes or commit-ready diff

### Continuation
On completion: `⟿[QA]`

</details>

---

## Phase: QA
<details>
<summary>Expand if PHASE=QA</summary>

### Mission
Verify quality. Run linters, type checkers, static analysis.

### Actions
1. Run `uv run mypy protocols/nphase/ protocols/cli/intent/`
2. Run `uv run ruff protocols/nphase/ protocols/cli/intent/`
3. Check for security issues (no command injection in intent parsing)
4. Verify code style
5. Review for edge cases (empty forest, no plans, etc.)

### Exit Criteria
- [ ] mypy clean
- [ ] ruff clean
- [ ] No security issues
- [ ] Edge cases handled

### Minimum Artifact
Checklist run with result

### Continuation
On completion: `⟿[TEST]`

</details>

---

## Phase: TEST
<details>
<summary>Expand if PHASE=TEST</summary>

### Mission
Verify behavior. Write and run tests.

### Actions
1. Write unit tests for new components
2. Add integration tests for `kg do` forest operations
3. Verify law tests pass (forest consistency, phase accountability)
4. Check edge cases
5. Run full test suite

### Test Contracts
```python
def test_do_show_forest_produces_output():
    """kg do 'show forest' produces forest health view."""
    plan = generate_plan("show forest")
    assert plan.category == IntentCategory.FOREST
    assert any(s.command == "forest" for s in plan.steps)

def test_completeness_auditor_validates_phase():
    """Auditor detects missing minimum artifacts."""
    project = ProjectDefinition(...)  # missing file_map
    report = auditor.audit_phase(project, "RESEARCH")
    assert not report.is_complete
    assert "file_map" in report.missing
```

### Exit Criteria
- [ ] Unit tests for C1-C9
- [ ] Integration tests for 8 operations
- [ ] Law tests verified
- [ ] All tests passing

### Minimum Artifact
Tests added/updated or explicit no-op with risk

### Continuation
On completion: `⟿[EDUCATE]`

</details>

---

## Phase: EDUCATE
<details>
<summary>Expand if PHASE=EDUCATE</summary>

### Mission
Document for users and maintainers.

### Actions
1. Update `kg do --help` with forest examples
2. Add inline documentation for new components
3. Create usage examples in skills/
4. Document gotchas (intent patterns, edge cases)
5. Update CLAUDE.md if needed

### Exit Criteria
- [ ] `kg do --help` includes forest operations
- [ ] Component docstrings complete
- [ ] skills/do-forest-ops.md created

### Minimum Artifact
User/maintainer note or explicit skip

### Continuation
On completion: `⟿[MEASURE]`

</details>

---

## Phase: MEASURE
<details>
<summary>Expand if PHASE=MEASURE</summary>

### Mission
Define metrics. Set up measurement for success.

### Actions
1. Identify key metrics (intent recognition accuracy, audit coverage)
2. Add telemetry instrumentation if needed
3. Define success criteria
4. Set up monitoring
5. Document baseline

### Metrics
| Metric | Target | Baseline |
|--------|--------|----------|
| Intent recognition rate | >90% | TBD |
| Completeness audit coverage | 100% phases | 0% |
| Forest op latency | <100ms | TBD |

### Exit Criteria
- [ ] Metrics identified
- [ ] Telemetry in place (optional)
- [ ] Success criteria defined

### Minimum Artifact
Metric hook/plan or defer with owner/timebox

### Continuation
On completion: `⟿[REFLECT]`

</details>

---

## Phase: REFLECT
<details>
<summary>Expand if PHASE=REFLECT</summary>

### Mission
Extract learnings. Seed the next cycle.

### Actions
1. Review what worked well
2. Document what didn't
3. Extract reusable patterns
4. Identify follow-up work
5. Update entropy accounting

### Follow-up Work Seeds
- [ ] TUI dashboard for forest visualization
- [ ] LLM-backed intent refinement (haiku fallback)
- [ ] Auto-audit on git commit hooks
- [ ] Forest → Kanban view

### Exit Criteria
- [ ] Learnings documented
- [ ] Patterns extracted
- [ ] Follow-up work identified
- [ ] Entropy accounted

### Minimum Artifact
Learnings + next-loop seeds

### Continuation
`⟂[COMPLETE]` — Work done. Tithe remaining entropy.

</details>

---

## Phase Accountability

| Phase | Status | Artifact |
|-------|--------|----------|
| PLAN | pending | - |
| RESEARCH | pending | - |
| DEVELOP | pending | - |
| STRATEGIZE | pending | - |
| CROSS-SYNERGIZE | pending | - |
| IMPLEMENT | pending | - |
| QA | pending | - |
| TEST | pending | - |
| EDUCATE | pending | - |
| MEASURE | pending | - |
| REFLECT | pending | - |

---

*"The form that generates forms."*
