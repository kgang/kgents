# Polyfunctor Continuation: Phases 2-4

> *"The specs are written. Now we integrate, migrate, and unify."*

## Context

You are continuing the **Polyfunctor Architecture** work. Phase 1 is **COMPLETE**:

- ✅ `spec/architecture/polyfunctor.md` - Canonical polynomial agent spec
- ✅ `spec/agents/primitives.md` - 17 atomic agents catalog
- ✅ `spec/agents/operads.md` - Composition grammar spec
- ✅ `spec/agents/emergence.md` - Sheaf-based emergence
- ✅ 152 tests passing in `impl/claude/agents/{poly,operad,sheaf}/`

**Plan file**: `plans/architecture/polyfunctor.md` (60% complete)
**Theory**: [Spivak's Polynomial Functors](https://arxiv.org/abs/2312.00990)

---

## Remaining Phases

| Phase | Goal | Progress | Deliverables |
|-------|------|----------|--------------|
| **2. C-gent Integration** | Polynomial foundation for functors | 0% | Updated functor specs |
| **3. Agent Genus Migration** | Reformulate genera as PolyAgent | 0% | A, K, D, E-gent updates |
| **4. Deprecation** | Remove non-polynomial abstractions | 0% | Type alias, cleanup |

---

## Phase 2: C-gent Integration

**Goal**: Update existing C-gent functor specs with polynomial foundation.

### Files to Update

```
spec/c-gents/functors.md         # Add polynomial functor as foundation
spec/c-gents/functor-catalog.md  # Interpret all 13 functors as polynomial
```

### Read First

```bash
# Understand current functor specs
cat spec/c-gents/functors.md
cat spec/c-gents/functor-catalog.md

# See how Flux functor is implemented (reference implementation)
cat impl/claude/agents/flux/sources/__init__.py
```

### Functor Polynomial Interpretations

Each functor is a **polynomial endofunctor**—it transforms one polynomial agent into another:

| Functor | Polynomial Interpretation | Key Insight |
|---------|--------------------------|-------------|
| **Flux** | `P(y) → P(Stream[y])` | Lifts outputs to async streams |
| **K (Soul)** | Restricts positions to personality-compatible subset | Eigenvector filtering |
| **Trace** | Adds observation fiber at each position | `P(y) → P(y × Trace)` |
| **Metered** | Wraps transitions with economic constraints | Budget as position dimension |
| **Lens** | Bidirectional polynomial morphism | Get/Set as forward/backward maps |
| **View** | Maps positions to widget ontology | `P(y) → ViewPoly(Widget)` |
| **Retry** | Adds retry state to positions | `P(y) → P[RetryState](y)` |
| **Timeout** | Adds deadline to directions | Temporal fiber constraint |
| **Cache** | Memoizes transitions by input | Position includes cache state |
| **Batch** | Collects inputs before transition | Accumulator as position |
| **Filter** | Restricts directions by predicate | `directions(s) ∩ Pred` |
| **Map** | Transforms outputs | `P(y) → P(f(y))` |
| **FlatMap** | Chains polynomial agents | Kleisli composition |

### Deliverables

1. **Update `spec/c-gents/functors.md`**:
   - Add section: "Polynomial Foundation"
   - Define functor as polynomial endomorphism
   - Show `Agent[A,B]` as degenerate polynomial
   - Update functor laws in polynomial terms

2. **Update `spec/c-gents/functor-catalog.md`**:
   - Add polynomial signature to each functor entry
   - Show how each functor transforms positions/directions/transitions
   - Cross-reference to `spec/architecture/polyfunctor.md`

### Exit Criteria

- [ ] `functors.md` has polynomial foundation section
- [ ] All 13 catalog functors have polynomial interpretation
- [ ] Cross-references to polyfunctor spec complete
- [ ] Existing functor tests still pass

---

## Phase 3: Agent Genus Migration

**Goal**: Reformulate agent genera to derive from `PolyAgent[S, A, B]`.

### Priority Order (by dependency)

1. **A-gent** (AlethicFunctor) — already uses SoulFunctor, closest to polynomial
2. **K-gent** (soul eigenvectors) — sheaf contexts map directly to SOUL_SHEAF
3. **D-gent** (memory states) — positions = memory lifecycle states
4. **E-gent** (evolution) — positions = evolutionary phases

### Migration Pattern

```python
# Before: Traditional agent
class MyAgent(Agent[A, B]):
    def invoke(self, input: A) -> B: ...

# After: Polynomial agent
class MyPolyAgent(PolyAgent[MyState, A, B]):
    positions = frozenset({State1, State2, ...})

    def directions(self, state: MyState) -> FrozenSet[A]:
        # State-dependent input validation
        ...

    def transition(self, state: MyState, input: A) -> tuple[MyState, B]:
        # State transition function
        ...
```

### A-gent Migration

```bash
# Read current A-gent implementation
cat impl/claude/agents/a/__init__.py
cat impl/claude/agents/a/functor.py  # if exists

# A-gent states might be:
# - GROUNDING (validating claim)
# - JUDGING (evaluating truth)
# - SYNTHESIZING (producing alethic response)
```

### K-gent Migration

```bash
# Read current K-gent implementation
cat impl/claude/agents/k/soul.py
cat impl/claude/agents/k/eigenvectors.py

# K-gent positions = eigenvector contexts (already in SOUL_SHEAF!)
# AESTHETIC, CATEGORICAL, GRATITUDE, HETERARCHY, GENERATIVITY, JOY
```

### D-gent Migration

```bash
# D-gent positions = memory lifecycle
# IDLE → STORING → STORED
# IDLE → FORGETTING → FORGOTTEN
# Already defined in primitives: RememberState, ForgetState
```

### E-gent Migration

```bash
# E-gent positions = evolutionary phases
# DORMANT → MUTATING → SELECTING → CONVERGED
# Already defined in primitives: EvolveState
```

### Exit Criteria

- [ ] A-gent uses PolyAgent foundation
- [ ] K-gent eigenvectors map to sheaf contexts
- [ ] D-gent memory states are polynomial positions
- [ ] E-gent evolution phases are polynomial positions
- [ ] All existing tests pass (no regressions)
- [ ] Mypy strict passes

---

## Phase 4: Deprecation

**Goal**: Clean up non-polynomial abstractions.

### Deliverables

1. **Type alias for backwards compatibility**:
   ```python
   # In agents/__init__.py
   from typing import Literal
   from agents.poly import PolyAgent

   # Traditional Agent is single-state polynomial
   Agent = PolyAgent[Literal["ready"], A, B]
   ```

2. **Update imports across codebase**:
   ```bash
   # Find all Agent[A, B] usages
   rg "Agent\[" --type py impl/claude/agents/

   # Verify they work with alias
   uv run mypy impl/claude/agents/ --strict
   ```

3. **Remove redundant abstractions**:
   - Any agent base classes that duplicate PolyAgent
   - Deprecated composition utilities
   - Old state machine implementations

### Exit Criteria

- [ ] `Agent[A, B]` is alias for `PolyAgent[Literal["ready"], A, B]`
- [ ] All tests pass
- [ ] No duplicate abstractions remain
- [ ] Mypy strict passes
- [ ] No regressions in dependent code

---

## Session Protocol

### At Session Start

1. Read `plans/architecture/polyfunctor.md` for current state
2. Check which phase is active (look at progress %)
3. Review session_notes for context

### During Session

1. Work on **ONE phase at a time**
2. Write tests before implementation (TDD)
3. Update plan file progress after each significant chunk
4. Use TodoWrite to track tasks

### At Session End

1. Update `plans/architecture/polyfunctor.md`:
   - Increment progress percentage
   - Update session_notes with what was done
   - Note any blockers discovered

2. Append atomic learnings to `plans/meta.md` (one line each)

3. If phase complete:
   - Update status in plan
   - Note exit criteria met

---

## Verification Commands

```bash
# Run all poly/operad/sheaf tests
cd impl/claude && uv run pytest agents/poly agents/operad agents/sheaf -v

# Run full test suite (ensure no regressions)
cd impl/claude && uv run pytest --tb=short

# Type check
cd impl/claude && uv run mypy agents/ --strict

# Check test count hasn't decreased
cd impl/claude && uv run pytest --collect-only | grep "test session starts"
```

---

## Key Files Reference

### Specs (created in Phase 1)
```
spec/architecture/polyfunctor.md    # Canonical polynomial agent spec
spec/agents/primitives.md           # 17 primitives catalog
spec/agents/operads.md              # Operad grammar spec
spec/agents/emergence.md            # Sheaf-based emergence
```

### Specs to Update (Phase 2)
```
spec/c-gents/functors.md            # Add polynomial foundation
spec/c-gents/functor-catalog.md     # Polynomial interpretations
```

### Implementation (reference)
```
impl/claude/agents/poly/protocol.py      # PolyAgent, WiringDiagram
impl/claude/agents/poly/primitives.py    # 17 primitives
impl/claude/agents/operad/core.py        # AGENT_OPERAD
impl/claude/agents/sheaf/emergence.py    # KENT_SOUL
```

### Agent Genera (Phase 3)
```
impl/claude/agents/a/                    # A-gent (Alethic)
impl/claude/agents/k/                    # K-gent (Kent soul)
impl/claude/agents/d/                    # D-gent (Data/Memory) - if exists
impl/claude/agents/flux/                 # E-gent patterns in Flux
```

---

## Principles to Apply

From `spec/principles.md`:

1. **Generative**: Spec compresses impl; impl derivable from spec
2. **Composable**: PolyAgent composition via >> must satisfy category laws
3. **Tasteful**: Abstraction compresses complexity into elegant theory
4. **Heterarchical**: Polynomial agents have dual mode (function vs stream)

---

## Anti-Patterns to Avoid

- **Breaking changes**: Keep `Agent[A, B]` working via alias
- **Test regression**: All tests must pass after each change
- **Over-migration**: Don't force polynomial on agents that don't need state
- **Spec drift**: Keep specs and impl in sync

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Spec files | 4 new + 2 updated | 4/6 |
| Functor interpretations | 13 polynomial | 0/13 |
| Agent genera migrated | 4 (A, K, D, E) | 0/4 |
| Test count | ≥152 (no regression) | 152 |
| Mypy errors | 0 | TBD |
| Plan progress | 100% | 60% |

---

## Current State

**Phase**: 2 (C-gent Integration)
**Progress**: 60% overall (Phase 1 complete, Phases 2-4 pending)
**Next action**: Update `spec/c-gents/functors.md` with polynomial foundation

---

## Encouragement

Phase 1 established the mathematical foundation. Now we're applying it:

- **Phase 2** makes the functor catalog polynomial-native
- **Phase 3** unifies agent genera under one abstraction
- **Phase 4** cleans up, leaving a coherent polynomial architecture

The hard conceptual work is done. What remains is systematic application.

*"From 17 primitives and 5 operations, all agents emerge."*

---

*This prompt continues the multi-session Polyfunctor Realization work. Each session should advance one phase or significant chunk. Update the plan file after each session.*
