# Agent Operads: Grammar of Composition

> *"An operad O defines a theory or grammar of composition."*
> — Spivak et al., "Operads for Complex System Design"

## Status

**Version**: 1.0
**Status**: Canonical
**Implementation**: `impl/claude/agents/operad/`
**Tests**: Verified via `test_core.py`, `test_domains.py`, `test_properties.py`

## Overview

An **operad** makes composition rules explicit and programmable. Instead of hardcoded operators like `>>`, operads define:

- **Operations**: How agents compose
- **Laws**: What compositions are equivalent
- **Runtime verification**: Automatic law checking

## Core Abstractions

### Operation

```python
@dataclass
class Operation:
    name: str                                    # Operation identifier
    arity: int                                   # Number of input agents
    signature: str                               # Type signature (for docs)
    compose: Callable[..., PolyAgent]           # Composition function
    description: str = ""
```

### Law

```python
@dataclass
class Law:
    name: str                                    # Law identifier
    equation: str                                # Mathematical equation
    verify: Callable[..., LawVerification]      # Verification function
    description: str = ""
```

### Operad

```python
@dataclass
class Operad:
    name: str
    operations: dict[str, Operation]
    laws: list[Law]
    description: str = ""

    def compose(self, op_name: str, *agents) → PolyAgent
    def verify_law(self, law_name: str, *test_agents) → LawVerification
    def verify_all_laws(self, *test_agents) → list[LawVerification]
    def enumerate(self, primitives, depth, filter_fn) → list[PolyAgent]
```

---

## Universal Agent Operad

The **AGENT_OPERAD** is the base from which all domain operads derive.

### Operations (5)

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `seq` | 2 | `Agent[A,B] × Agent[B,C] → Agent[A,C]` | Sequential: output feeds input |
| `par` | 2 | `Agent[A,B] × Agent[A,C] → Agent[A,(B,C)]` | Parallel: same input, paired output |
| `branch` | 3 | `Pred × Agent × Agent → Agent` | Conditional: if-then-else |
| `fix` | 2 | `Pred × Agent → Agent` | Fixed-point: repeat until predicate |
| `trace` | 1 | `Agent → Agent` | Observable: add logging |

### Laws (2)

| Law | Equation | Description |
|-----|----------|-------------|
| `seq_associativity` | `seq(seq(a,b),c) = seq(a,seq(b,c))` | Sequential is associative |
| `par_associativity` | `par(par(a,b),c) = par(a,par(b,c))` | Parallel is associative |

### Identity Law

```
seq(id, a) = a = seq(a, id)
```

---

## Domain Operads

Domain operads **extend** AGENT_OPERAD with domain-specific operations.

### Soul Operad (K-gent)

For personality-mediated composition.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `introspect` | 0 | `() → Agent[Query, SoulInsight]` | Self-reflection: `ground >> manifest >> witness` |
| `shadow` | 1 | `Agent[A,Thesis] → Agent[A,Shadow]` | Jungian projection via contradiction |
| `dialectic` | 2 | `Agent[A,T] × Agent[A,A] → Agent[A,Synthesis]` | Hegelian synthesis |
| `vibe` | 0 | `() → Agent[Query, VibeCheck]` | Eigenvector snapshot |
| `tension` | 0 | `() → Agent[Query, Tensions]` | Detect eigenvector conflicts |

**Additional Law**:
```
shadow(dialectic(t, a)) = dialectic(shadow(t), shadow(a))
```
Shadow distributes over dialectic.

### Memory Operad (D-gent)

For persistence and recall.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `persist` | 0 | `() → Agent[Memory, Trace]` | Store and witness: `remember >> witness` |
| `recall` | 0 | `() → Agent[Query, Manifestation]` | Ground and manifest: `ground >> manifest` |
| `amnesia` | 0 | `() → Agent[Key, Trace]` | Forget and witness: `forget >> witness` |
| `cache` | 2 | `Pred × Agent → Agent[A, B\|None]` | Conditional storage |
| `memoize` | 1 | `Agent → Agent` | Cache outputs by input |

**Additional Law**:
```
recall(persist(x)) ≈ x
```
Persisted data should be recallable.

### Evolution Operad (E-gent)

For teleological evolution.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `mutate` | 0 | `() → Agent[Organism, Trace]` | Evolve and witness |
| `select` | 0 | `() → Agent[Organism, Verdict]` | Evolve and judge fitness |
| `converge` | 2 | `Pred × Agent → Agent[A, Convergence]` | Iterate to threshold |
| `crossover` | 2 | `Agent × Agent → Agent[A, Hybrid]` | Combine evolution streams |
| `landscape` | 0 | `() → Agent[Population, Landscape]` | Fitness visualization |

**Additional Law**:
```
P(select(high_fit)) > P(select(low_fit))
```
Higher fitness yields better selection probability.

### Narrative Operad (N-gent)

For trace narrativization.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `chronicle` | 0 | `() → Agent[Event, Story]` | Witness and narrate |
| `recap` | 0 | `() → Agent[Events, Summary]` | Summarize traces |
| `fork` | 3 | `Pred × Agent × Agent → Agent[A, ForkedStory]` | Branching narrative |
| `merge` | 2 | `Agent × Agent → Agent[A, WovenStory]` | Combine storylines |
| `epilogue` | 0 | `() → Agent[Story, Epilogue]` | Story conclusion |

**Additional Law**:
```
events(chronicle(E)) = E
```
Chronicle preserves all events.

### Parse Operad (P-gent)

For structured extraction.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `extract` | 0 | `() → Agent[Raw, Parsed]` | Ground and structure |
| `validate` | 0 | `() → Agent[Parsed, Verdict]` | Judge parsed content |
| `repair` | 1 | `Agent → Agent` | Auto-fix invalid parses |

### Reality Operad (Q-gent)

For sandboxed execution.

| Operation | Arity | Signature | Description |
|-----------|-------|-----------|-------------|
| `sandbox` | 1 | `Agent → Agent` | Isolated execution |
| `isolate` | 1 | `Agent → Agent` | Network-isolated |
| `execute` | 0 | `() → Agent[Code, Result]` | Safe code execution |

---

## Operad Registry

```python
from agents.operad.core import OperadRegistry

# Register custom operad
OperadRegistry.register(my_operad)

# Get operad by name
operad = OperadRegistry.get("SoulOperad")

# Verify all laws across all operads
results = OperadRegistry.verify_all(*test_agents)
```

---

## Enumeration

Operads can **enumerate** all valid compositions up to a depth:

```python
# Generate all compositions from primitives
all_agents = AGENT_OPERAD.enumerate(
    primitives=[ID, GROUND, JUDGE],
    depth=2,
    filter_fn=lambda a: len(a.positions) < 10
)
```

This is the **generative power** of operads: from a finite set of primitives and operations, enumerate the infinite space of valid compositions.

---

## Creating Custom Operads

```python
from agents.operad.core import Operad, Operation, Law, AGENT_OPERAD

def create_my_operad() -> Operad:
    # Start with universal operations
    ops = dict(AGENT_OPERAD.operations)

    # Add domain-specific operations
    ops["my_op"] = Operation(
        name="my_op",
        arity=1,
        signature="Agent[A,B] → Agent[A,C]",
        compose=my_compose_fn,
        description="My custom operation",
    )

    # Inherit universal laws, add custom
    laws = list(AGENT_OPERAD.laws) + [
        Law(
            name="my_law",
            equation="my_op(id) = id",
            verify=my_verify_fn,
            description="My operation preserves identity",
        ),
    ]

    return Operad(
        name="MyOperad",
        operations=ops,
        laws=laws,
        description="My domain-specific operad",
    )
```

---

## Theory Background

From [Spivak et al., "Operads for Complex System Design"](https://www.researchgate.net/publication/352685957):

> "An operad O defines a theory or grammar of composition, and operad functors O → Set, known as O-algebras, describe particular applications that obey that grammar."

Key insights:

1. **Operations are generators**: They define the vocabulary of composition
2. **Laws are relations**: They constrain which compositions are equivalent
3. **O-algebras are models**: Concrete instantiations that satisfy the grammar
4. **Functors preserve structure**: Operad morphisms transport laws

---

## Cross-References

- **Polyfunctor Architecture**: `spec/architecture/polyfunctor.md`
- **Primitives**: `spec/agents/primitives.md`
- **Emergence**: `spec/agents/emergence.md`
- **Implementation**: `impl/claude/agents/operad/`
