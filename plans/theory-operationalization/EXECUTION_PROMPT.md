# Theory Operationalization: Execution Prompt

> For agent executing upgrades from CRITICAL_ANALYSIS_AND_UPGRADES_v2.md

---

## Execution Status (Updated 2025-12-26)

| Task | Status | Completed | Tests | Notes |
|------|--------|-----------|-------|-------|
| **TIER 0** | **DONE** | 2025-12-26 | — | C5 and S4 marked as REDUNDANT/DONE |
| **E1** | **DONE** | 2025-12-26 | 36 passing | `services/witness/kleisli.py` — Writer monad with Kleisli composition |
| **E3** | **DONE** | 2025-12-26 | 22 passing | `services/dialectic/fusion.py` — Full fusion service |
| **D1** | **NEXT** | — | — | ConstrainedBellmanEquation — no blockers, constitution.py EXISTS |
| **M1** | **NEXT** | — | — | MultiAgentSheaf binding conflicts — depends on E3 (DONE) |
| **G1** | **NEXT** | — | — | Calibration Pipeline — CRITICAL PATH, no blockers |

### Completed Work Summary

**E1: Kleisli Witness Composition** (`impl/claude/services/witness/kleisli.py`)
- `Witnessed[A]` — Writer monad with value and mark trace
- `kleisli_compose` — Categorical composition (>=>)
- `kleisli_chain` — Compose N Kleisli arrows
- `@witnessed_operation` — Decorator for async traced operations
- `@witnessed_sync` — Decorator for sync traced operations
- All 3 monad laws verified by property tests

**E3: DialecticalFusionService** (`impl/claude/services/dialectic/fusion.py`)
- `Position` — Structured view with principle alignment
- `Fusion` — Complete dialectical record
- `FusionResult` — 6 outcomes (CONSENSUS, SYNTHESIS, KENT_PREVAILS, CLAUDE_PREVAILS, DEFERRED, VETO)
- `DialecticalFusionService` — Full fusion workflow
- Constitution Article IV (Disgust Veto) and Article VI (Fusion as Goal) integrated
- Honest naming: "heuristic synthesis" not "cocone"

---

## Next Execution Phase (UNBLOCKED)

With E1 and E3 complete, three proposals are now unblocked:

### D1: ConstrainedBellmanEquation (1 week)

**Dependencies**: `constitution.py` EXISTS with `Constitution.evaluate()` and `ETHICAL_FLOOR_THRESHOLD`

**Key Integration Points**:
- `services/categorical/constitution.py` — Constitution.evaluate(state, action, next_state) signature
- `ConstitutionalEvaluation.ethical_passes` property
- Bridge class: `ConstitutionScorer` to adapt Bellman ↔ Constitution signatures

**Deliverables**:
- `impl/claude/services/dp/constrained_bellman.py`
- `impl/claude/services/dp/_tests/test_constrained_bellman.py`
- Value iteration that respects ETHICAL floor
- Dead-end states with -inf value (no ethical actions available)

### M1: MultiAgentSheaf Enhancement (3-5 days)

**Dependencies**: E3 (DialecticalFusionService) is DONE — binding conflict resolution can use fusion patterns

**Key Integration Points**:
- E3's `FusionResult` patterns for conflict resolution strategies
- Chapter 14 (Binding Problem) theory: scope-local vs. defer vs. unify

**Deliverables**:
- `_detect_binding_conflicts()` method
- `_resolve_binding_conflicts(strategy)` with 3 strategies
- Integration with `synthesize_disagreement()`

### G1: Calibration Pipeline (CRITICAL PATH, 3-4 weeks)

**Dependencies**: NONE — this is the critical path to validate the Galois bet

**Key Challenge**: "Difficulty" D(P) is not axiomatized. Need to define it before correlation analysis.

**Deliverables — Two Phases**:
1. **Phase 1a (1 week)**: Axiomatize difficulty with `difficulty_oracle(prompt) -> float`
2. **Phase 1b (3 weeks)**: 100+ calibration entries, compute L(P), run correlation

**Go/No-Go Gate (Week 9)**:
- r > 0.5: PROCEED with G2-G5
- 0.3 < r <= 0.5: PIVOT to simpler metrics
- r <= 0.3: REJECT Galois bet

---

## Mission

Execute the TIER 1 (Critical Path) upgrades from the theory-operationalization analysis. Total effort: ~3 weeks. Savings from deletions: ~8 weeks of premature work.

---

## Context Files (READ FIRST)

| File | Purpose |
|------|---------|
| `plans/theory-operationalization/CRITICAL_ANALYSIS_AND_UPGRADES_v2.md` | Full analysis with rationale |
| `plans/enlightened-synthesis/00-master-synthesis.md` | Current project state (P0-P2 complete) |
| `plans/enlightened-synthesis/02-execution-roadmap.md` | 10-week timeline |
| `CLAUDE.md` | Project conventions and principles |

---

## TIER 1: Critical Path (Execute in Order)

### 1. E1: Kleisli Witness Composition (4 days)

**Problem**: Witness marks don't compose monadically.

**Create**: `impl/claude/services/witness/kleisli.py`

**Reference impl**:
- Existing witness: `impl/claude/services/witness/__init__.py`
- Mark dataclass: `impl/claude/services/witness/mark.py` (if exists) or in `__init__.py`
- Theory: `docs/theory/16-witness.md`

**Scaffold**:
```python
@dataclass
class Witnessed(Generic[A]):
    value: A
    marks: list[Mark]

    @staticmethod
    def pure(value: A) -> 'Witnessed[A]': ...
    def bind(self, f: Callable[[A], 'Witnessed[B]']) -> 'Witnessed[B]': ...

def kleisli_compose(f, g): ...  # f >=> g
```

**Tests**: `impl/claude/services/witness/_tests/test_kleisli.py`
- Left identity: `pure(a).bind(f) == f(a)`
- Right identity: `m.bind(pure) == m`
- Associativity: `m.bind(f).bind(g) == m.bind(lambda x: f(x).bind(g))`

**Success**: All 3 monad laws pass.

---

### 2. E3: DialecticalFusionService (8 days)

**Problem**: Article VI (Fusion as Goal) has ZERO implementation.

**Create**: `impl/claude/services/dialectic/fusion.py`

**Reference**:
- Constitution: `impl/claude/services/categorical/constitution.py` (lines 1-50 docstring has Article VI)
- Theory: `docs/theory/17-dialectic.md`
- Existing witness for mark integration: `impl/claude/services/witness/`

**Scaffold**:
```python
@dataclass
class Position:
    content: str
    reasoning: str
    confidence: float
    principle_alignment: dict[str, float]

@dataclass
class Cocone:
    apex: Position
    kent_projection: float
    claude_projection: float

    @property
    def is_valid_cocone(self) -> bool:
        return self.kent_projection > 0.6 and self.claude_projection > 0.6

class DialecticalFusionService:
    async def propose_fusion(kent: Position, claude: Position) -> Cocone: ...
    async def _structure_position(view: str, reasoning: str) -> Position: ...
    async def _attempt_synthesis(kent: Position, claude: Position) -> Position: ...
```

**AGENTESE node**: `impl/claude/protocols/agentese/nodes/dialectic.py`
- Path: `self.dialectic.fuse`
- Dependencies: `("dialectic_service", "witness_service")`

**Tests**: `impl/claude/services/dialectic/_tests/test_fusion.py`
- Consensus detection (positions agree → no synthesis needed)
- Synthesis generation (positions disagree → cocone constructed)
- Cocone validity (both projections > 0.6)
- Witness integration (fusion creates mark)

**Success**: Fusion returns valid cocone; AGENTESE node registered.

---

### 3. D1: ConstrainedBellmanEquation (1 week)

**Problem**: Signature mismatch with Constitution.evaluate().

**Create**: `impl/claude/services/dp/constrained_bellman.py`

**Reference**:
- Constitution: `impl/claude/services/categorical/constitution.py`
  - `Constitution.evaluate(state_before, action, state_after, context)` → `ConstitutionalEvaluation`
  - `ConstitutionalEvaluation.ethical_passes` (property, line ~158)
  - `ETHICAL_FLOOR_THRESHOLD = 0.6`
- Theory: `docs/theory/09-agent-dp.md`

**Bridge class** (required):
```python
class ConstitutionScorer:
    """Bridge ConstrainedBellman ↔ Constitution."""
    def evaluate(self, state, action, next_state=None) -> ConstitutionalEvaluation:
        next_state = next_state or state
        return Constitution.evaluate(state, action, next_state)
```

**Scaffold**:
```python
class ConstrainedBellmanEquation(Generic[State, Action]):
    def ethical_actions(self, state: State, scorer: ConstitutionScorer) -> list[Action]:
        return [a for a in self.actions(state) if scorer.evaluate(state, a).ethical_passes]

    def reward(self, state, action, next_state, scorer) -> float:
        eval_result = scorer.evaluate(state, action, next_state)
        if not eval_result.ethical_passes:
            raise ValueError("ETHICAL-invalid action")
        return eval_result.weighted_total

    def value_iteration(self, states, scorer, gamma=0.9, max_iter=100) -> dict[State, float]: ...
```

**Tests**: `impl/claude/services/dp/_tests/test_constrained_bellman.py`
- `test_ethical_constraint_filters_actions()`
- `test_dead_end_state_has_neg_inf_value()`
- `test_value_iteration_converges()`

**Success**: Bellman uses Constitution.evaluate(); all tests pass.

---

### 4. M1 Enhancement: Binding Conflict Handling (3 days)

**Problem**: MultiAgentSheaf ignores Chapter 14 (Binding Problem).

**Modify**: `impl/claude/services/multi_agent/sheaf_coordination.py` (if exists) or create

**Reference**:
- Existing M1 spec: `plans/theory-operationalization/04-distributed-agents.md` (already UPGRADED)
- Theory: `docs/theory/14-binding.md`

**Add methods**:
```python
def _detect_binding_conflicts(self, beliefs: list[AgentBelief]) -> list[BindingConflict]:
    """Detect conflicting variable bindings across agents."""
    ...

def _resolve_binding_conflicts(self, conflicts: list[BindingConflict],
                                strategy: str = "scope") -> dict:
    """Resolve via: 'scope' (separate bindings), 'defer' (alternatives), 'unify'."""
    ...
```

**Integration point**: Call in `synthesize_disagreement()` before LLM synthesis.

**Tests**:
- `test_binding_conflict_detection()`
- `test_scope_resolution_separates_bindings()`
- `test_defer_resolution_preserves_alternatives()`

**Success**: Synthesis handles binding conflicts explicitly.

---

## TIER 0: DELETE (Do First)

Remove these proposals from active consideration:

| File | Section | Action |
|------|---------|--------|
| `plans/theory-operationalization/01-categorical-infrastructure.md` | C5 | Mark as REDUNDANT (pilot_laws.py exists) |
| `plans/theory-operationalization/06-synthesis-differentiation.md` | S1, S3 | Mark as REDUNDANT/DONE |

No code deletion—these proposals were never implemented.

---

## Verification Commands

```bash
# After each implementation:
cd impl/claude && uv run pytest -q services/witness/_tests/test_kleisli.py
cd impl/claude && uv run pytest -q services/dialectic/_tests/test_fusion.py
cd impl/claude && uv run pytest -q services/dp/_tests/test_constrained_bellman.py

# Full suite:
cd impl/claude && uv run pytest -q && uv run mypy .
```

---

## Success Criteria

| Component | Test | Target |
|-----------|------|--------|
| E1 | 3 monad laws | 100% pass |
| E3 | Cocone validity | is_valid_cocone == True for synthesis |
| E3 | AGENTESE node | `self.dialectic.fuse` registered |
| D1 | Value iteration | Converges in < 100 iterations |
| D1 | Ethical filter | Dead-end states have -inf value |
| M1 | Binding conflicts | Detected and resolved |

---

## DO NOT

- Implement G1-G5 until Week 7 (blocked by trail-to-crystal validation)
- Implement D2-D5 until D1 stable
- Implement M2-M5 until M1 enhanced
- Create new proposal files—modify existing ones

---

## Constitutional Grounding

All implementations must satisfy:
- **A5 (ETHICAL)**: Floor constraint enforced (D1)
- **A4 (WITNESS)**: Actions leave traces (E1, E3 integration)
- **A2 (MORPHISM)**: Composition laws hold (E1 monad laws)
- **Article VI**: Fusion goal achieved (E3)

---

*"Daring, bold, creative, opinionated but not gaudy."*
