# Polyfunctor Realization: Multi-Part Execution Prompt

> *"Agent[A, B] ≅ A → B is a lie. Real agents have modes."*

## Context

You are continuing the **Polyfunctor Architecture** work. The implementation exists (`impl/claude/agents/{poly,operad,sheaf}/`, 152 tests) but no specification exists. Your task is to write specs from impl, then migrate the codebase to polynomial foundations.

**Plan file**: `plans/architecture/polyfunctor.md`
**Theory**: [Spivak's Polynomial Functors](https://arxiv.org/abs/2312.00990)

---

## The Core Abstraction

```python
# Traditional (insufficient)
Agent[A, B] = A → B

# Polynomial (captures mode-dependent behavior)
PolyAgent[S, A, B] = (
    positions: Set[S],           # States agent can be in
    directions: S → Set[A],      # Valid inputs per state
    transition: S × A → (S, B)   # State × Input → (NewState, Output)
)
```

**Key insight**: `Agent[A, B] ≅ PolyAgent[Unit, A, B]` — traditional agents embed as single-state polynomials.

---

## Phase Overview

| Phase | Goal | Deliverables | Tests |
|-------|------|--------------|-------|
| **1. Spec from Impl** | Document what exists | 4 spec files | Spec matches impl |
| **2. C-gent Integration** | Polynomial foundation for functors | Updated functor catalog | Law verification |
| **3. Agent Genus Migration** | Reformulate genera as PolyAgent | A, K, D, E-gent updates | Existing tests pass |
| **4. Deprecation** | Remove non-polynomial abstractions | Type alias, cleanup | No regressions |

---

## Phase 1: Spec from Impl

**Goal**: Write specifications that capture the existing implementation.

### Deliverables

1. **`spec/architecture/polyfunctor.md`** (~200 lines)
   - Polynomial functor definition
   - PolyAgent protocol
   - Wiring diagrams
   - Integration with AGENTESE

2. **`spec/agents/primitives.md`** (~150 lines)
   - 17 primitives catalog with signatures
   - State machines for each
   - Categories: Bootstrap, Perception, Entropy, Memory, Teleological

3. **`spec/agents/operads.md`** (~200 lines)
   - AGENT_OPERAD (5 universal operations)
   - Domain operads (Soul, Memory, Evolution, Narrative, Parse, Reality)
   - Laws and verification

4. **`spec/agents/emergence.md`** (~100 lines)
   - AgentSheaf protocol
   - SOUL_SHEAF and eigenvector contexts
   - Gluing as emergence

### Verification

```bash
# Specs should be generative - impl derivable from spec
cd impl/claude
uv run pytest agents/poly agents/operad agents/sheaf -v
# All 152 tests must pass
```

### Exit Criteria

- [ ] All 4 spec files created
- [ ] Spec language matches impl behavior
- [ ] Cross-references complete
- [ ] No new implementation code (spec only)

---

## Phase 2: C-gent Integration

**Goal**: Update existing C-gent functor specs with polynomial foundation.

### Deliverables

1. **Update `spec/c-gents/functors.md`**
   - Add polynomial functor as foundation
   - Show Agent[A,B] as degenerate polynomial
   - Update functor laws in polynomial terms

2. **Update `spec/c-gents/functor-catalog.md`**
   - Interpret all 13 functors as polynomial endomorphisms
   - Add polynomial signatures to each functor

### Functor Interpretations

| Functor | Polynomial Interpretation |
|---------|--------------------------|
| Flux | Lifts `P(y)` to `P(Stream[y])` |
| K | Restricts positions to personality-compatible subset |
| Trace | Adds observation fiber at each position |
| Metered | Wraps transitions with economic constraints |
| Lens | Bidirectional polynomial morphism |
| View | Maps positions to widget ontology |

### Exit Criteria

- [ ] functors.md has polynomial foundation
- [ ] All 13 catalog functors have polynomial interpretation
- [ ] Existing functor tests still pass

---

## Phase 3: Agent Genus Migration

**Goal**: Reformulate agent genera to derive from PolyAgent.

### Priority Order (by dependency)

1. **A-gent** (AlethicFunctor) — already uses SoulFunctor
2. **K-gent** (soul eigenvectors) — sheaf contexts map directly
3. **D-gent** (memory states) — positions = memory lifecycle states
4. **E-gent** (evolution) — positions = evolutionary phases

### Migration Pattern

```python
# Before
class MyAgent(Agent[A, B]):
    def invoke(self, input: A) -> B: ...

# After
class MyPolyAgent(PolyAgent[MyState, A, B]):
    positions = frozenset({State1, State2, ...})

    def directions(self, state: MyState) -> FrozenSet[A]:
        # State-dependent input validation
        ...

    def transition(self, state: MyState, input: A) -> tuple[MyState, B]:
        # State transition function
        ...
```

### Exit Criteria

- [ ] A-gent uses PolyAgent foundation
- [ ] K-gent eigenvectors map to sheaf contexts
- [ ] D-gent memory states are polynomial positions
- [ ] E-gent evolution phases are polynomial positions
- [ ] All existing tests pass (no regressions)

---

## Phase 4: Deprecation

**Goal**: Clean up non-polynomial abstractions.

### Deliverables

1. **Type alias for backwards compatibility**
   ```python
   # In agents/__init__.py
   Agent = PolyAgent[Literal["ready"], A, B]  # Single-state sugar
   ```

2. **Update imports across codebase**
   - Find all `Agent[A, B]` usages
   - Verify they work with alias
   - Update docstrings

3. **Remove redundant abstractions**
   - Any agent base classes that duplicate PolyAgent
   - Deprecated composition utilities

### Exit Criteria

- [ ] `Agent[A, B]` is alias for `PolyAgent[Unit, A, B]`
- [ ] All tests pass
- [ ] No duplicate abstractions remain
- [ ] Mypy strict passes

---

## Session Protocol

### At Session Start

1. Read `plans/architecture/polyfunctor.md` for current state
2. Check which phase is active
3. Review session_notes for context

### During Session

1. Work on ONE phase at a time
2. Write tests before implementation (TDD)
3. Update plan file progress after each chunk

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

## Key Files Reference

### Implementation (read these)
```
impl/claude/agents/poly/protocol.py      # PolyAgent, WiringDiagram
impl/claude/agents/poly/primitives.py    # 17 primitives
impl/claude/agents/operad/core.py        # AGENT_OPERAD
impl/claude/agents/operad/domains/*.py   # Domain operads
impl/claude/agents/sheaf/protocol.py     # AgentSheaf
impl/claude/agents/sheaf/emergence.py    # KENT_SOUL
```

### Specs (create/update these)
```
spec/architecture/polyfunctor.md    # NEW
spec/agents/primitives.md           # NEW
spec/agents/operads.md              # NEW
spec/agents/emergence.md            # NEW
spec/c-gents/functors.md            # UPDATE
spec/c-gents/functor-catalog.md     # UPDATE
```

### Theory (consult as needed)
```
https://arxiv.org/abs/2312.00990           # Spivak book
https://ncatlab.org/nlab/show/polynomial+functor
https://topos.institute/events/poly-course/
```

---

## Principles to Apply

From `spec/principles.md`:

1. **Generative**: Spec should compress impl; impl derivable from spec
2. **Composable**: PolyAgent composition via >> must satisfy category laws
3. **Tasteful**: Abstraction compresses 17 primitives + ∞ compositions into one theory
4. **Heterarchical**: Polynomial agents have dual mode (function vs stream)

---

## Anti-Patterns to Avoid

- **Spec drift**: Spec must match impl behavior exactly
- **Over-abstraction**: Keep Agent[A,B] sugar working
- **Test regression**: All 152 poly/operad/sheaf tests must pass
- **Principle violation**: Every change must satisfy category laws

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Spec files created | 4 new |
| Functor catalog updated | 13 polynomial interpretations |
| Agent genera migrated | 4 (A, K, D, E) |
| Test count | ≥152 (no regression) |
| Mypy errors | 0 |

---

## Current State

**Phase**: 1 (Spec from Impl)
**Progress**: 30% (plan created, research complete)
**Next action**: Create `spec/architecture/polyfunctor.md`

---

*This prompt is designed for multi-session execution. Each session should advance one phase or significant chunk. Update the plan file after each session.*
