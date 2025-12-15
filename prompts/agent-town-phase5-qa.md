# Agent Town Phase 5: QA Phase

**Predecessor**: `plans/_epilogues/2025-12-14-agent-town-phase5-implement.md`
**Phase**: QA (N-Phase 7 of 11)
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, CROSS-SYNERGIZE:touched, IMPLEMENT:touched, QA:in_progress}`

---

## Context

Phase 5 IMPLEMENT delivered:
- `project_scatter_to_ascii()` - ASCII scatter plot (12 tests)
- `EigenvectorScatterWidgetImpl` - Signal-based widget (11 tests)
- `TownSSEEndpoint` - Queue-based SSE (6 tests)
- `TownNATSBridge` - JetStream + memory fallback (7 tests)
- API routes: `GET /{id}/scatter`, `GET /{id}/events`

Test status: 481 town tests pass, 63 visualization tests pass.

---

## QA Checklist

Execute the following QA gates:

### 1. Type Checking (mypy)
```bash
uv run mypy agents/town/visualization.py protocols/api/town.py --ignore-missing-imports
```

### 2. Linting (ruff)
```bash
uv run ruff check agents/town/visualization.py protocols/api/town.py
```

### 3. Security Scan
- [ ] No hardcoded credentials
- [ ] No SQL injection vectors (N/A - no SQL)
- [ ] No XSS vectors in SSE output (JSON-encoded data)
- [ ] No command injection (no shell exec)

### 4. Functor Law Verification
- [ ] Identity law: `scatter.map(id) ≡ scatter` (tested)
- [ ] Composition law: `scatter.map(f).map(g) ≡ scatter.map(g . f)` (tested)
- [ ] with_state law: `scatter.map(f) ≡ scatter.with_state(f(state.value))` (tested)

### 5. Contract Compliance
- [ ] `EigenvectorScatterWidgetImpl` satisfies `EigenvectorScatterWidgetProtocol`
- [ ] `TownSSEEndpoint` satisfies `TownSSEEndpointProtocol`
- [ ] `TownNATSBridge` satisfies `TownNATSBridgeProtocol`

### 6. Export Verification
```python
from agents.town.visualization import (
    ScatterPoint, ScatterState, ProjectionMethod,
    EigenvectorScatterWidgetImpl, TownSSEEndpoint, TownNATSBridge,
    project_scatter_to_ascii,
)
```

---

## Actions

1. Run mypy on visualization and API modules
2. Run ruff check on same
3. Verify all exports are accessible
4. Check protocol compliance (duck typing)
5. Document any issues found

---

## Exit Criteria

- [ ] mypy: PASS (0 errors)
- [ ] ruff: PASS (0 errors)
- [ ] Security: PASS (no vulnerabilities)
- [ ] Laws: VERIFIED (all 3 functor laws)
- [ ] Exports: VERIFIED (all public API accessible)

---

## Branch Candidates

- **Parallel**: Performance benchmarking (defer to MEASURE)
- **Deferred**: Integration tests with real NATS (requires infrastructure)

---

## Entropy Budget

- Allocated: 0.05
- Draw: `void.entropy.sip(amount=0.05)`
- Purpose: Edge case discovery in QA

---

## Continuation

On success: `⟿[TEST]` - Add edge case tests discovered during QA
On failure: `⟂[QA:blocked]` - Fix issues before proceeding

---

*Guard [phase=QA][entropy=0.05][law_check=true][minimal_output=true]*

---

## Auto-Inducer

⟿[QA]
/hydrate prompts/agent-town-phase5-qa.md
handles: scope=agent-town-phase5-visualization; ledger={PLAN:touched,RESEARCH:touched,DEVELOP:touched,STRATEGIZE:touched,CROSS-SYNERGIZE:touched,IMPLEMENT:touched,QA:in_progress}; entropy=0.05
mission: QA gates (mypy, ruff, security, law verification); verify all contracts satisfied.
actions: Bash(uv run mypy), Bash(uv run ruff check), verify exports, check protocol compliance.
exit: all gates PASS → ledger.QA=touched; continuation → TEST | any gate FAIL → ⟂[QA:blocked].

---

**LAW**: This prompt auto-continues. The signifier `⟿[QA]` triggers immediate execution without human intervention. Halt conditions: mypy errors, ruff errors, law violations, or `⟂[HUMAN_INTERRUPT]`.
