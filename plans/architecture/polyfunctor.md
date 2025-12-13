---
path: architecture/polyfunctor
status: active
progress: 60
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [architecture/alethic, agents/k-gent]
session_notes: |
  Phase 1 COMPLETE: Spec from Impl
  - Created spec/architecture/polyfunctor.md (canonical spec)
  - Created spec/agents/primitives.md (17 primitives catalog)
  - Created spec/agents/operads.md (operad grammar spec)
  - Created spec/agents/emergence.md (sheaf-based emergence)
  - All 152 tests pass (poly/operad/sheaf)
  Next: Phase 2 - C-gent Integration (update functor catalog with polynomial interpretations)
---

# Polyfunctor Architecture: Agents as Dynamical Systems

> *"Agent[A, B] ≅ A → B is a lie. Real agents have modes."*

**Status**: active (152 tests in impl, 4 spec files)
**AGENTESE Context**: Foundation for all agent abstraction
**Principles**: Composable, Generative, Heterarchical
**Cross-refs**:
- **Spec**: `spec/architecture/polyfunctor.md`, `spec/agents/{primitives,operads,emergence}.md`
- **Impl**: `impl/claude/agents/{poly,operad,sheaf}/`
- **Theory**: [Niu & Spivak, "Polynomial Functors: A Mathematical Theory of Interaction"](https://arxiv.org/abs/2312.00990)

---

## Status Matrix

| Layer | Impl | Spec | Status |
|-------|------|------|--------|
| `poly/` | `PolyAgent[S, A, B]`, 17 primitives | `spec/architecture/polyfunctor.md`, `spec/agents/primitives.md` | **Complete** |
| `operad/` | `AGENT_OPERAD`, 6 domain operads | `spec/agents/operads.md` | **Complete** |
| `sheaf/` | `SOUL_SHEAF`, emergence via gluing | `spec/agents/emergence.md` | **Complete** |
| C-gent functors | 13 documented, Flux implemented | Partial | **Phase 2** |

---

## Core Insight: Polynomial Agents

Traditional agents are functions: `Agent: A → B`. This captures stateless transformation but misses **mode-dependent behavior**—agents that behave differently based on internal state.

### The Polynomial Functor

From [Spivak's theory](https://toposinstitute.github.io/poly/poly-book.pdf):

```
P(y) = Σ_{s ∈ S} y^{E(s)}
```

Where:
- **S** = Set of **positions** (states the agent can be in)
- **E(s)** = **Directions** at position s (valid inputs in that state)
- The polynomial encodes: "In state s, I accept inputs from E(s)"

### PolyAgent: The Generalization

```python
PolyAgent[S, A, B] = (
    positions: Set[S],           # Valid states
    directions: S → Set[A],      # State-dependent valid inputs
    transition: S × A → (S, B)   # State × Input → (NewState, Output)
)
```

**Key property**: `Agent[A, B] ≅ PolyAgent[Unit, A, B]`—traditional agents embed as single-state polynomials.

---

## The Three Layers

### Layer 1: Primitives (17 Atoms)

The implementation defines 17 primitive agents:

| Category | Primitives | Description |
|----------|------------|-------------|
| **Bootstrap (7)** | ID, GROUND, JUDGE, CONTRADICT, SUBLATE, COMPOSE, FIX | Core composition |
| **Perception (3)** | MANIFEST, WITNESS, LENS | Observer-dependent behavior |
| **Entropy (3)** | SIP, TITHE, DEFINE | Accursed Share / void.* |
| **Memory (2)** | REMEMBER, FORGET | D-gent persistence |
| **Teleological (2)** | EVOLVE, NARRATE | E-gent/N-gent evolution |

Each primitive is a `PolyAgent` with well-defined states:

```python
# Example: JUDGE primitive
JUDGE = PolyAgent[JudgeState, Claim, Verdict](
    positions={DELIBERATING, DECIDED},
    directions=lambda s: {Claim} if s == DELIBERATING else {},
    transition=_judge_transition
)
```

### Layer 2: Operads (Composition Grammar)

An **operad** defines how primitives compose. From [Spivak's operad work](https://www.researchgate.net/publication/352685957_Operads_for_complex_system_design_specification_analysis_and_synthesis):

> "An operad O defines a theory or grammar of composition, and operad functors O → Set describe particular applications that obey that grammar."

**AGENT_OPERAD** provides 5 universal operations:

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `seq` | 2 | `Agent[A,B] × Agent[B,C] → Agent[A,C]` | Sequential: `a >> b` |
| `par` | 2 | `Agent[A,B] × Agent[A,C] → Agent[A,(B,C)]` | Parallel: same input |
| `branch` | 3 | `Pred × Agent × Agent → Agent` | Conditional |
| `fix` | 2 | `Pred × Agent → Agent` | Fixed-point iteration |
| `trace` | 1 | `Agent → Agent` | Observable wrapper |

**Domain Operads** extend AGENT_OPERAD:

| Operad | Domain | Additional Operations |
|--------|--------|----------------------|
| SOUL_OPERAD | K-gent | introspect, shadow, dialectic, vibe, tension |
| MEMORY_OPERAD | D-gent | cache, persist, snapshot |
| EVOLUTION_OPERAD | E-gent | mutate, select, converge |
| NARRATIVE_OPERAD | N-gent | begin, witness, conclude |
| PARSE_OPERAD | P-gent | extract, validate, repair |
| REALITY_OPERAD | Q-gent | sandbox, isolate, execute |

**Operad Laws** (verified in tests):
- `seq_associativity`: `seq(seq(a,b),c) = seq(a,seq(b,c))`
- `par_associativity`: `par(par(a,b),c) = par(a,par(b,c))`
- `identity`: `seq(id,a) = a = seq(a,id)`

### Layer 3: Sheaves (Emergence Topology)

A **sheaf** captures emergence—how global behavior arises from compatible local behaviors:

```python
AgentSheaf[Ctx] = (
    contexts: Set[Ctx],                    # Observation contexts
    overlap: Ctx × Ctx → Ctx | None,       # Context intersection
    restrict: Agent × Ctx → Agent,         # Global → Local
    compatible: Dict[Ctx, Agent] → bool,   # Check agreement
    glue: Dict[Ctx, Agent] → Agent         # EMERGENCE: Local → Global
)
```

**SOUL_SHEAF** glues 6 local souls into KENT_SOUL:

| Context | Eigenvector | Local Soul Question |
|---------|-------------|---------------------|
| AESTHETIC | minimalism | "Does this need to exist?" |
| CATEGORICAL | abstraction | "What's the morphism?" |
| GRATITUDE | sacred_lean | "What deserves more respect?" |
| HETERARCHY | peer_lean | "Could this be peer-to-peer?" |
| GENERATIVITY | generation_lean | "What can this generate?" |
| JOY | playfulness | "Where's the delight?" |

**Emergence**: The glued `KENT_SOUL` can operate in **any** eigenvector context—a capability no single local soul has.

---

## Wiring Diagrams: Morphisms Between Polynomials

From [nLab](https://ncatlab.org/nlab/show/polynomial+functor) and [Topos Institute](https://topos.institute/blog/2024-08-19-wiring-diagrams-mealy-machines/):

A **morphism** between polynomials P → Q describes how to connect P's outputs to Q's inputs. These are **wiring diagrams**:

```
┌─────────────────────────────────────────┐
│        WIRING DIAGRAM: P → Q            │
│                                         │
│   ┌───────┐        ┌───────┐           │
│   │   P   │──out──▶│   Q   │           │
│   └───────┘        └───────┘           │
│       ↑                                 │
│      in                                 │
└─────────────────────────────────────────┘
```

**Composition** is polynomial substitution—feeding P's output polynomial into Q's input polynomial.

Implementation in `impl/claude/agents/poly/protocol.py:181-231`:

```python
@dataclass
class WiringDiagram(Generic[S, S2, A, B, C]):
    left: PolyAgent[S, A, B]
    right: PolyAgent[S2, B, C]

    def compose(self) -> PolyAgent[tuple[S, S2], A, C]:
        # State = product of both agent states
        # Output of left feeds input of right
```

---

## Integration with Existing Architecture

### AGENTESE Paths as Polynomial Morphisms

AGENTESE paths become morphisms between polynomial fibers:

```python
# world.house.manifest
# = morphism from observer-fiber to perception-fiber

world.house → Handle           # Positions
manifest(umwelt) → Perception  # Directions parameterized by observer
```

The observer determines which fiber to use—this is exactly polynomial functor semantics.

### Agent Genera as Polynomials

Every agent genus can be reformulated:

| Genus | Polynomial Structure |
|-------|---------------------|
| A-gent | `PolyAgent[AlethicState, Query, AlethicResponse]` |
| K-gent | `PolyAgent[EigenvectorContext, Input, Mediated]` |
| D-gent | `PolyAgent[MemoryState, Op, Result]` |
| E-gent | `PolyAgent[EvolveState, Organism, Evolution]` |
| Flux | `PolyAgent[FluxState, Event, Event]` (streaming) |

### Functor Catalog Update

The existing 13 functors in `spec/c-gents/functor-catalog.md` are **polynomial functor endomorphisms**:

| Functor | Polynomial Interpretation |
|---------|--------------------------|
| Flux | Lifts `P(y)` to `P(Stream[y])` |
| K (Personalization) | Restricts positions to personality-compatible subset |
| Trace | Adds observation fiber at each position |
| Metered | Wraps transitions with economic constraints |

---

## Laws and Verification

### Polynomial Substitution Laws

From category theory:
- **Identity**: `P ∘ Id = P = Id ∘ P`
- **Associativity**: `(P ∘ Q) ∘ R = P ∘ (Q ∘ R)`

### Operad Laws

Verified in `impl/claude/agents/operad/_tests/test_core.py`:
- Operation associativity (seq, par)
- Identity operations
- Interchange law (par distributes over seq)

### Sheaf Laws

From [Mac Lane & Moerdijk](https://www.cambridge.org/core/books/polynomial-functors/5A57527AE303503CDCC9B71D3799231F):
- **Locality**: Restriction of restriction = restriction
- **Gluing**: Compatible locals produce unique global

---

## Implementation Plan

### Phase 1: Spec from Impl (Current)

Write specifications that capture existing implementation:

**Files to create**:
```
spec/architecture/polyfunctor.md       # This document → spec
spec/agents/primitives.md              # 17 primitives catalog
spec/agents/operads.md                 # Operad grammar spec
spec/agents/emergence.md               # Sheaf-based emergence
```

**Exit Criteria**: Specs match impl behavior; can regenerate impl from spec.

### Phase 2: C-gent Integration

Update existing C-gent functor spec:

**Files to update**:
```
spec/c-gents/functors.md      # Add polynomial functor foundation
spec/c-gents/functor-catalog.md   # Interpret functors as polynomial
```

**Exit Criteria**: All 13 functors have polynomial interpretation.

### Phase 3: Agent Genus Migration

Incrementally reformulate agent genera:

**Priority order** (by dependency):
1. A-gent (AlethicFunctor already uses SoulFunctor)
2. K-gent (soul eigenvectors → sheaf contexts)
3. D-gent (memory states → polynomial positions)
4. E-gent (evolution → polynomial dynamics)

**Exit Criteria**: Each genus derives from `PolyAgent[S, A, B]`.

### Phase 4: Deprecation

Remove non-polynomial abstractions:

- Replace `Agent[A, B]` with `PolyAgent[Unit, A, B]` sugar
- Ensure backwards compatibility via type alias

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Complexity**: Polynomial functors are abstract | `Agent[A,B]` remains as sugar; primitives hide the math |
| **Learning curve**: Developers need category theory | Operads provide concrete operations; theory optional |
| **Spec-impl divergence**: Impl ahead of spec | This plan writes spec FROM impl, not vice versa |
| **Principle tension**: Is this too abstract? | The abstraction compresses 17 primitives + ∞ compositions into one theory. That's **tasteful compression**. |

---

## Creative Angles Explored

### Polynomial Agents as Games

- **Positions** = Game states
- **Directions** = Valid moves at each state
- **Transitions** = Game dynamics
- [Libkind & Spivak's work on agent portfolios](https://topos.institute/blog/2024-11-08-neural-wiring-diagrams/) connects here

### Sheaf Emergence as Nash Equilibrium

Local optima glue to global equilibrium—compatible local behaviors produce globally coherent soul.

### Operads as Type Systems

- Operations are type constructors
- Laws are type equations
- [AlgebraicDynamics.jl](https://blog.algebraicjulia.org/post/2021/01/machines/) demonstrates this in practice

### The Accursed Share as Entropy Fiber

`void.*` primitives (SIP, TITHE, DEFINE) live in a special fiber:
- Not deterministic directions
- Entropy budget as fiber dimension
- 10% exploration budget = fiber capacity

---

## Cross-References

**Theory**:
- [Polynomial Functors book (arXiv)](https://arxiv.org/abs/2312.00990)
- [Topos Institute course](https://topos.institute/events/poly-course/)
- [nLab: polynomial functor](https://ncatlab.org/nlab/show/polynomial+functor)
- [Wiring Diagrams for Mealy Machines](https://topos.institute/blog/2024-08-19-wiring-diagrams-mealy-machines/)

**Implementation**:
- `impl/claude/agents/poly/protocol.py` (PolyAgent, WiringDiagram)
- `impl/claude/agents/poly/primitives.py` (17 primitives)
- `impl/claude/agents/operad/core.py` (AGENT_OPERAD)
- `impl/claude/agents/operad/domains/*.py` (domain operads)
- `impl/claude/agents/sheaf/protocol.py` (AgentSheaf)
- `impl/claude/agents/sheaf/emergence.py` (KENT_SOUL)

**Specs to create**:
- `spec/architecture/polyfunctor.md`
- `spec/agents/primitives.md`
- `spec/agents/operads.md`
- `spec/agents/emergence.md`

---

## Changelog

- 2025-12-13: Phase 1 complete - 4 spec files created, all 152 tests pass
- 2025-12-13: Initial plan from research + impl analysis
