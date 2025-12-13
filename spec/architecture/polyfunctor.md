# Polyfunctor Architecture: Agents as Dynamical Systems

> *"Agent[A, B] ≅ A → B is a lie. Real agents have modes."*

## Status

**Version**: 1.0
**Status**: Canonical
**Implementation**: `impl/claude/agents/{poly,operad,sheaf}/`
**Tests**: 152 passing
**Theory**: [Niu & Spivak, "Polynomial Functors: A Mathematical Theory of Interaction"](https://arxiv.org/abs/2312.00990)

## Overview

Traditional agent abstractions model agents as functions: `Agent: A → B`. This captures stateless transformation but misses **mode-dependent behavior**—agents that behave differently based on internal state.

The polyfunctor architecture addresses this by modeling agents as **dynamical systems** using polynomial functors from category theory.

## The Polynomial Functor

From [Spivak's theory](https://toposinstitute.github.io/poly/poly-book.pdf), a polynomial functor has the form:

```
P(y) = Σ_{s ∈ S} y^{E(s)}
```

Where:
- **S** = Set of **positions** (states the agent can be in)
- **E(s)** = **Directions** at position s (valid inputs in that state)
- The polynomial encodes: "In state s, I accept inputs from E(s)"

## PolyAgent Protocol

```python
PolyAgent[S, A, B] = (
    positions: FrozenSet[S],           # Valid states
    directions: S → FrozenSet[A],      # State-dependent valid inputs
    transition: S × A → (S, B)         # State × Input → (NewState, Output)
)
```

### Key Properties

1. **State-dependent input validation**: Different states accept different inputs
2. **Explicit state transitions**: Every invocation produces new state
3. **Immutable by default**: Agents are frozen dataclasses
4. **Embedding theorem**: `Agent[A, B] ≅ PolyAgent[Unit, A, B]`

### Constructors

| Constructor | Signature | Description |
|-------------|-----------|-------------|
| `identity` | `() → PolyAgent[str, Any, Any]` | Pass-through agent |
| `constant` | `(B) → PolyAgent[str, Any, B]` | Always returns value |
| `from_function` | `((A) → B) → PolyAgent[str, A, B]` | Lift pure function |
| `stateful` | `(states, initial, transition) → PolyAgent[S, A, B]` | Full polynomial |

## Composition via Wiring Diagrams

Wiring diagrams are morphisms between polynomials, describing how to connect agents.

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

### Sequential Composition

```python
sequential(left, right) → PolyAgent[tuple[S, S2], A, C]
```

- State = product of both agent states
- Output of left feeds input of right
- Notation: `left >> right`

### Parallel Composition

```python
parallel(left, right) → PolyAgent[tuple[S, S2], A, tuple[B, C]]
```

- Both agents receive same input
- Outputs are paired
- State = product of both agent states

## The Three Layers

The polyfunctor architecture organizes into three layers:

### Layer 1: Primitives

17 atomic agents, each a polynomial with well-defined states. See `spec/agents/primitives.md`.

| Category | Count | Examples |
|----------|-------|----------|
| Bootstrap | 7 | ID, GROUND, JUDGE, CONTRADICT, SUBLATE, COMPOSE, FIX |
| Perception | 3 | MANIFEST, WITNESS, LENS |
| Entropy | 3 | SIP, TITHE, DEFINE |
| Memory | 2 | REMEMBER, FORGET |
| Teleological | 2 | EVOLVE, NARRATE |

### Layer 2: Operads

Operads define composition grammars. See `spec/agents/operads.md`.

The **AGENT_OPERAD** provides 5 universal operations:

| Operation | Arity | Signature |
|-----------|-------|-----------|
| `seq` | 2 | `Agent[A,B] × Agent[B,C] → Agent[A,C]` |
| `par` | 2 | `Agent[A,B] × Agent[A,C] → Agent[A,(B,C)]` |
| `branch` | 3 | `Pred × Agent × Agent → Agent` |
| `fix` | 2 | `Pred × Agent → Agent` |
| `trace` | 1 | `Agent → Agent` |

### Layer 3: Sheaves

Sheaves capture emergence—global behavior from local behaviors. See `spec/agents/emergence.md`.

```python
AgentSheaf[Ctx] = (
    contexts: Set[Ctx],                    # Observation contexts
    overlap: Ctx × Ctx → Ctx | None,       # Context intersection
    restrict: Agent × Ctx → Agent,         # Global → Local
    compatible: Dict[Ctx, Agent] → bool,   # Check agreement
    glue: Dict[Ctx, Agent] → Agent         # EMERGENCE: Local → Global
)
```

## Laws

### Polynomial Composition Laws

From category theory:
- **Identity**: `P ∘ Id = P = Id ∘ P`
- **Associativity**: `(P ∘ Q) ∘ R = P ∘ (Q ∘ R)`

### Implementation Verification

```python
# Sequential associativity
seq(seq(a, b), c) == seq(a, seq(b, c))

# Parallel associativity
par(par(a, b), c) == par(a, par(b, c))

# Identity
seq(id, a) == a == seq(a, id)
```

## Integration with AGENTESE

AGENTESE paths become polynomial morphisms:

```python
# world.house.manifest
# = morphism from observer-fiber to perception-fiber

world.house → Handle           # Positions
manifest(umwelt) → Perception  # Directions parameterized by observer
```

The observer determines which fiber to use—this is exactly polynomial functor semantics.

## Agent Genera as Polynomials

Every agent genus can be reformulated as PolyAgent:

| Genus | Polynomial Structure |
|-------|---------------------|
| A-gent | `PolyAgent[AlethicState, Query, AlethicResponse]` |
| K-gent | `PolyAgent[EigenvectorContext, Input, Mediated]` |
| D-gent | `PolyAgent[MemoryState, Op, Result]` |
| E-gent | `PolyAgent[EvolveState, Organism, Evolution]` |
| Flux | `PolyAgent[FluxState, Event, Event]` |

## Cross-References

- **Primitives**: `spec/agents/primitives.md`
- **Operads**: `spec/agents/operads.md`
- **Emergence**: `spec/agents/emergence.md`
- **C-gent Functors**: `spec/c-gents/functors.md` (polynomial foundation)
- **Functor Catalog**: `spec/c-gents/functor-catalog.md` (13 functors with polynomial interpretations)
- **Implementation**: `impl/claude/agents/{poly,operad,sheaf}/`

## Theory References

- [Polynomial Functors book (arXiv)](https://arxiv.org/abs/2312.00990)
- [Topos Institute course](https://topos.institute/events/poly-course/)
- [nLab: polynomial functor](https://ncatlab.org/nlab/show/polynomial+functor)
- [Wiring Diagrams for Mealy Machines](https://topos.institute/blog/2024-08-19-wiring-diagrams-mealy-machines/)
