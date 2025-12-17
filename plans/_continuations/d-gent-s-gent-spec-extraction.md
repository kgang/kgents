---
path: plans/_continuations/d-gent-s-gent-spec-extraction
status: complete
progress: 100
last_touched: 2025-12-17
touched_by: claude-opus-4
blocking: []
enables:
  - d-gent-dual-track-architecture (Phase 4+)
  - s-gent implementation
  - functor catalog update
session_notes: |
  2025-12-17: Created continuation prompt for spec extraction
  2025-12-17: COMPLETED - Specs extracted and formalized:
    - spec/d-gents/dual-track.md (new)
    - spec/s-gents/README.md (new)
    - spec/s-gents/state-functor.md (new)
    - spec/s-gents/composition.md (new)
    - spec/s-gents/laws.md (new)
    - spec/c-gents/functor-catalog.md (§14 State added)
    - spec/d-gents/README.md (updated with S-gent relationship)
    - CLAUDE.md (S-gent added to taxonomy)
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: complete
  IMPLEMENT: complete
  REFLECT: complete
entropy:
  planned: 0.3
  spent: 0.25
  returned: 0.05
---

# Prompt: D-gent + S-gent Spec Extraction

> Extract and formalize the dual-track architecture into updated specs.

## Context

The plan `plans/d-gent-dual-track-architecture.md` contains:
1. **Dual-track architecture** for D-gent (agent memory vs application state)
2. **StateFunctor specification** for `Flux(State(agent))` composition
3. **TableAdapter bridge** between tracks

This needs to be formalized into:
1. **Updated `spec/d-gents/` specs** — incorporating dual-track, TableAdapter
2. **New `spec/s-gents/` specs** — State functor as its own agent genus

---

## Task 1: Research Phase

### 1.1 Read the Source Plan

```
Read: plans/d-gent-dual-track-architecture.md
```

Extract and understand:
- The dual-track architecture (Agent Memory vs Application State)
- The TableAdapter bridge functor
- The StateFunctor specification
- The relationship between Symbiont and StateFunctor
- The `Flux(State(agent))` composition pattern
- Integration points with Crown Jewels

### 1.2 Read Existing D-gent Specs

```
Read: spec/d-gents/README.md
Read: spec/d-gents/architecture.md
Read: spec/d-gents/symbiont.md
Read: spec/d-gents/lenses.md
Read: spec/d-gents/protocols.md
Read: spec/d-gents/persistence.md
Read: spec/d-gents/vision.md
```

Identify:
- What needs updating vs what stays the same
- Where dual-track fits in the existing spec structure
- How TableAdapter extends DgentProtocol
- Whether Symbiont should stay in D-gent or move to S-gent

### 1.3 Read Related Specs

```
Read: spec/c-gents/functor-catalog.md
Read: spec/agents/flux.md
Read: spec/principles.md (AD-001, AD-002, AD-006)
```

Understand:
- How functors are documented in the catalog
- Flux functor structure (for composition reference)
- Universal Functor Mandate (AD-001)
- Polynomial Generalization (AD-002)
- Unified Categorical Foundation (AD-006)

### 1.4 Check Implementation Reality

```
Read: impl/claude/agents/d/state_monad.py
Read: impl/claude/agents/d/protocol.py
Read: impl/claude/agents/d/backends/memory.py
Grep: "Symbiont" in impl/claude/
```

Understand what actually exists vs what's specified.

---

## Task 2: Analysis Phase

### 2.1 Determine Spec Boundaries

**Question**: Should StateFunctor live in D-gent or become S-gent?

Arguments for **S-gent (new genus)**:
- State is a fundamental categorical concept (State Monad)
- Separates persistence (D-gent) from state-threading (S-gent)
- Follows the Tasteful principle (one agent, one purpose)
- Enables `S >> D` composition (state threading backed by persistence)
- Aligns with alphabetical taxonomy (S for State)

Arguments for **D-gent extension**:
- Symbiont already in D-gent spec
- State requires persistence (they're coupled)
- Fewer abstractions to learn

**Recommended decision**: Create S-gent as the State Monad functor, keep D-gent focused on persistence. Symbiont becomes the canonical `S >> D` composition.

### 2.2 Define the Boundary

```
D-gent: Persistence substrate (WHERE data lives)
  - DgentProtocol (put/get/delete/list/causal_chain)
  - Backends (Memory, JSONL, SQLite, Postgres)
  - TableAdapter (bridge to Alembic)
  - Lenses (focused access)
  - Projection lattice (graceful degradation)

S-gent: State threading (HOW state flows through computation)
  - StateFunctor (lift agents to stateful computation)
  - StatefulAgent (agent with state threading)
  - Flux composition (Flux ∘ State)
  - State laws (identity, composition)

Symbiont: The canonical S >> D composition
  - Pure logic + D-gent persistence
  - Could stay in D-gent spec OR be the example in S-gent spec
```

### 2.3 Identify New Content

**D-gent updates needed**:
- Dual-track architecture section
- TableAdapter specification
- AGENTESE `self.data.table.*` paths
- Bridge functor laws
- Crown Jewel integration examples

**S-gent content needed**:
- Purpose and Core Insight
- StateFunctor formal definition
- StatefulAgent protocol
- Functor laws (with proofs)
- Composition with Flux
- Composition with D-gent (Symbiont)
- Integration with PolyAgent
- AGENTESE `self.state.*` paths (if any)
- Anti-patterns

---

## Task 3: Write Updated D-gent Spec

### 3.1 Update `spec/d-gents/architecture.md`

Add after existing content:

```markdown
## Dual-Track Architecture

> *"Memory is not monolithic. Agent cognition and application state serve different masters."*

### The Two Tracks

| Track | Purpose | Schema | Migration | Access |
|-------|---------|--------|-----------|--------|
| **Agent Memory** | Cognition, association | Schema-free (Datum) | None (append-only) | Lenses |
| **Application State** | Consistent app data | Typed (Alembic) | Versioned | SQL/ORM |

### The Insight

Don't force D-gent to support migrations. Each track excels at what it's designed for.

[Include architecture diagram from plan]

### TableAdapter: The Bridge Functor

[Include TableAdapter specification from plan]

### Laws

1. **Round-trip**: `TableAdapter.get(TableAdapter.put(datum).id) ≅ datum`
2. **Source tagging**: `Datum.metadata["source"] == "alembic"` for bridged data
3. **Track isolation**: Agent memory changes don't affect Alembic tables
```

### 3.2 Create `spec/d-gents/dual-track.md`

New file with full dual-track details:
- Motivation (Crown Jewels need both tracks)
- TableAdapter full specification
- AGENTESE paths (`self.data.table.*`)
- Crown Jewel examples (Brain, Town, Gardener)
- Migration strategy

### 3.3 Update `spec/d-gents/README.md`

Add to table of contents:
- `dual-track.md` — Dual-track architecture

Update description to mention both agent memory and application state bridge.

---

## Task 4: Write S-gent Spec

### 4.1 Create `spec/s-gents/README.md`

```markdown
# S-gents: State Agents

> *"The Symbiont IS the State Monad. S-gent makes this explicit."*

## Purpose

S-gent provides **state threading** for agent computation—the categorical State Monad lifted to the agent domain.

| Concept | Traditional | S-gent |
|---------|-------------|--------|
| State Monad | `s -> (a, s)` | `Agent[A, B]` with S threading |
| StateT | `s -> m (a, s)` | `StatefulAgent[S, A, B]` |
| Composition | `>>=` (bind) | `>>` (agent composition) |

## The Core Insight

**State is orthogonal to persistence.**

- **D-gent**: WHERE state lives (memory, file, database)
- **S-gent**: HOW state threads through computation

The Symbiont pattern is `S >> D`—state threading backed by persistence.

## Contents

- [state-functor.md](state-functor.md) — The StateFunctor specification
- [composition.md](composition.md) — Flux and D-gent composition
- [laws.md](laws.md) — Functor laws and verification
- [symbiont.md](symbiont.md) — The canonical S >> D pattern

## Relationship to Other Agents

| Agent | Relationship |
|-------|--------------|
| **D-gent** | Persistence backend for StateFunctor |
| **Flux** | Composes as `Flux ∘ State` for streaming stateful agents |
| **PolyAgent** | StatefulAgent can be lifted to polynomial positions |
| **K-gent** | Soul state threads through K-gent interactions |

## AGENTESE Paths

S-gent does not expose direct AGENTESE paths. State threading is implicit in agent composition. Access state through:
- `self.data.*` (D-gent) for persisted state
- Agent invocation for threaded state
```

### 4.2 Create `spec/s-gents/state-functor.md`

```markdown
# StateFunctor: The State Monad as Functor

> *"Lift agents into stateful computation."*

## Purpose

StateFunctor lifts `Agent[A, B]` into stateful computation where state S is:
1. Loaded before each invocation
2. Threaded through the computation
3. Saved after each invocation

## Formal Definition

### The Functor

```
StateFunctor[S]: 𝒞_Agent → 𝒞_Agent

Where:
- Objects: Agent[A, B]
- Morphisms: Natural transformations
- S: The state type
```

### Core Operations

```python
class StateFunctor(Generic[S]):
    state_type: type[S]
    backend: DgentProtocol  # Where state persists
    initial_state: S | None

    def lift(self, agent: Agent[A, B]) -> StatefulAgent[S, A, B]:
        """Lift agent into stateful computation."""
        ...

    def lift_logic(self, f: Callable[[A, S], tuple[B, S]]) -> StatefulAgent[S, A, B]:
        """Lift pure logic directly (Symbiont pattern)."""
        ...
```

### StatefulAgent

```python
class StatefulAgent(Agent[A, B], Generic[S, A, B]):
    """Agent with explicit state threading."""

    inner: Agent[A, B]
    backend: DgentProtocol
    state_type: type[S]

    async def invoke(self, input: A) -> B:
        state = await self._load_state()
        result = await self.inner.invoke((input, state))
        output, new_state = result
        await self._save_state(new_state)
        return output
```

## Functor Laws

[Include law specifications and verification approach]

## Composition

### With Flux

```python
FluxState = StateFunctor.compose_flux(state_functor)
# Type: Agent[A, B] → FluxAgent[A, B] with state threading
```

### With D-gent (Symbiont)

```python
# Symbiont IS StateFunctor.lift_logic with D-gent backend
symbiont = StateFunctor(
    state_type=S,
    backend=dgent,
).lift_logic(pure_logic)
```

## Anti-patterns

- **State without persistence**: Use D-gent backend, not in-memory only
- **Bypassing state loading**: Always go through StatefulAgent.invoke()
- **Mutable state in logic**: Logic function must be pure `(A, S) → (B, S)`
```

### 4.3 Create `spec/s-gents/composition.md`

Detailed composition patterns:
- `Flux ∘ State` — streaming stateful agents
- `State ∘ D-gent` — state backed by persistence (Symbiont)
- `Flux ∘ State ∘ D-gent` — full stack
- TableAdapter integration for typed state

### 4.4 Create `spec/s-gents/laws.md`

Functor law specifications:
- Identity law with proof sketch
- Composition law with proof sketch
- State threading invariants
- Test strategy (property-based)

---

## Task 5: Update Functor Catalog

### 5.1 Add to `spec/c-gents/functor-catalog.md`

After Flux functor (§13), add:

```markdown
## §14: State Functor (S-gent)

> *"Thread state through agent computation."*

### Signature

```
State[S]: Agent[A, B] → StatefulAgent[S, A, B]
```

### Purpose

Lifts agents into stateful computation. State is:
- Loaded before invocation
- Passed to inner agent as extended input `(A, S)`
- Saved after invocation

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `State.lift(Id) ≅ Id` | `test_state_identity_law` |
| Composition | `State.lift(f >> g) ≅ State.lift(f) >> State.lift(g)` | `test_state_composition_law` |

### Composition with Flux

```
Flux ∘ State: Agent[A, B] → FluxAgent[A, B]

# Creates streaming agent with state threading
```

### Relationship to Symbiont

Symbiont = `State[S].lift_logic(f)` where backend is D-gent.

The Symbiont pattern is the canonical use of StateFunctor.

### See Also

- `spec/s-gents/` — Full S-gent specification
- `spec/d-gents/symbiont.md` — The S >> D composition
```

---

## Task 6: Validation

### 6.1 Cross-Reference Check

Verify all specs reference each other correctly:
- D-gent → S-gent (for state threading)
- S-gent → D-gent (for persistence backend)
- S-gent → Flux (for streaming composition)
- Functor catalog → S-gent spec

### 6.2 Principle Alignment

Verify specs align with:
- **Tasteful**: S-gent has clear, justified purpose (state threading)
- **Composable**: StateFunctor composes with Flux, D-gent
- **Generative**: Spec enables mechanical implementation
- **AD-001**: StateFunctor follows Universal Functor Mandate
- **AD-006**: Fits PolyAgent + Operad + Sheaf pattern

### 6.3 Implementation Path

Verify specs provide clear implementation guidance:
- File locations specified
- Types fully defined
- Laws testable
- Examples concrete

---

## Deliverables

1. **Updated D-gent specs**:
   - `spec/d-gents/architecture.md` (updated)
   - `spec/d-gents/dual-track.md` (new)
   - `spec/d-gents/README.md` (updated)

2. **New S-gent specs**:
   - `spec/s-gents/README.md`
   - `spec/s-gents/state-functor.md`
   - `spec/s-gents/composition.md`
   - `spec/s-gents/laws.md`
   - `spec/s-gents/symbiont.md` (moved from D-gent or cross-referenced)

3. **Functor catalog update**:
   - `spec/c-gents/functor-catalog.md` (§14 added)

4. **CLAUDE.md update**:
   - Add S-gent to agent taxonomy table

---

## Success Criteria

- [ ] D-gent dual-track architecture fully specified
- [ ] TableAdapter bridge functor documented
- [ ] S-gent purpose and boundary clear
- [ ] StateFunctor formally defined with laws
- [ ] Flux ∘ State composition documented
- [ ] Symbiont positioned correctly (S >> D)
- [ ] Functor catalog includes State functor
- [ ] All cross-references valid
- [ ] Implementation path clear from specs

---

*"State threads through computation like a river through landscape. D-gent is the riverbed. S-gent is the flow."*
