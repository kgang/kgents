---
path: architecture/polyfunctor
status: complete
progress: 100
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [architecture/turn-gents, agents/k-gent]
session_notes: |
  ALL PHASES COMPLETE (201 tests):
  - Phase 1: Spec from Impl (poly, operad, sheaf specs)
  - Phase 2: C-gent Integration (functor catalog updated)
  - Phase 3: Agent Genus Migration (A, K, D, E polynomials)
  - Phase 4: Robustification (instance isolation, deprecation sugar, property tests)

  Key insight: Agent[A,B] embeds in PolyAgent[S,A,B]. Real agents have modes.
---

# Polyfunctor Architecture: Agents as Dynamical Systems

> *"Agent[A, B] ≅ A → B is a lie. Real agents have modes."*

---

## Summary

The Polyfunctor Architecture reformulates agents as **polynomial functors**—state machines with mode-dependent input/output behavior. This captures what traditional `Agent[A, B]` misses: agents that behave differently based on internal state.

---

## The Core Insight

Traditional agents are functions: `Agent: A → B`. This captures stateless transformation but misses **mode-dependent behavior**.

### The Polynomial Functor

```
P(y) = Σ_{s ∈ S} y^{E(s)}
```

Where:
- **S** = Set of positions (states the agent can be in)
- **E(s)** = Directions at position s (valid inputs in that state)

### PolyAgent: The Generalization

```python
PolyAgent[S, A, B] = (
    positions: Set[S],           # Valid states
    directions: S → Set[A],      # State-dependent valid inputs
    transition: S × A → (S, B)   # State × Input → (NewState, Output)
)
```

**Key property**: `Agent[A, B] ≅ PolyAgent[Unit, A, B]`

---

## The Three Layers

### Layer 1: Primitives (17 Atoms)

| Category | Primitives | Count |
|----------|------------|-------|
| Bootstrap | ID, GROUND, JUDGE, CONTRADICT, SUBLATE, COMPOSE, FIX | 7 |
| Perception | MANIFEST, WITNESS, LENS | 3 |
| Entropy | SIP, TITHE, DEFINE | 3 |
| Memory | REMEMBER, FORGET | 2 |
| Teleological | EVOLVE, NARRATE | 2 |

### Layer 2: Operads (Composition Grammar)

| Operation | Signature |
|-----------|-----------|
| `seq` | `Agent[A,B] × Agent[B,C] → Agent[A,C]` |
| `par` | `Agent[A,B] × Agent[A,C] → Agent[A,(B,C)]` |
| `branch` | `Pred × Agent × Agent → Agent` |
| `fix` | `Pred × Agent → Agent` |
| `trace` | `Agent → Agent` |

### Layer 3: Sheaves (Emergence)

Sheaves capture emergence—how global behavior arises from compatible local behaviors. `SOUL_SHEAF` glues 6 eigenvector contexts into `KENT_SOUL`.

---

## Phase Outcomes

### Phase 1: Spec from Impl
- `spec/architecture/polyfunctor.md`
- `spec/agents/primitives.md`
- `spec/agents/operads.md`
- `spec/agents/emergence.md`

### Phase 2: C-gent Integration
- All 13 functors have polynomial interpretations
- Cross-references between polyfunctor and functor docs

### Phase 3: Agent Genus Migration

| Agent | States | Tests |
|-------|--------|-------|
| A-gent (Alethic) | GROUNDING → DELIBERATING → JUDGING → SYNTHESIZING | 38 |
| K-gent (Soul) | 7 eigenvector contexts | 28 |
| D-gent (Memory) | IDLE, LOADING, STORING, QUERYING, STREAMING, FORGETTING | 29 |
| E-gent (Evolution) | 8-phase thermodynamic cycle | 28 |

### Phase 4: Robustification

1. **Instance Isolation**: `MemoryStore` pattern prevents shared state
2. **Deprecation Sugar**: `StatelessAgent`, `to_bootstrap_agent()`
3. **Property-Based Tests**: Hypothesis tests for categorical laws
4. **Cross-Polynomial Composition**: 12 integration tests
5. **A-gent Robustness**: Bayesian confidence, input validation

---

## Key Learnings

### 1. Instance Isolation is Critical

```python
# BAD: Global state
_memory_state: dict = {}  # All instances share!

# GOOD: Per-instance factory
class MemoryStore:
    def __init__(self):
        self.state = {}

def create_memory_polynomial(store: MemoryStore) -> PolyAgent:
    ...
```

### 2. Bayesian Confidence Prevents Extremes

```python
def compute_confidence(n_support, n_contra, prior=0.5):
    if n_support + n_contra == 0:
        return prior
    alpha = 1.0  # Smoothing
    return max(0.05, min(0.95, (n_support + alpha * prior) / (total + alpha)))
```

### 3. Input Validation Prevents Crashes

```python
def validate_query(input):
    if input is None:
        return Query(claim="<empty>")
    if len(str(input)) > 10000:
        return Query(claim=str(input)[:10000] + "... [truncated]")
    return Query(claim=str(input).strip() or "<empty>")
```

### 4. Property-Based Tests Verify Laws

```python
@given(a=simple_agents(), b=simple_agents(), c=simple_agents())
def test_associativity(a, b, c):
    left = sequential(sequential(a, b), c)
    right = sequential(a, sequential(b, c))
    assert same_behavior(left, right)
```

---

## Files Modified/Created

### New Files
- `impl/claude/agents/a/alethic.py` (AlethicAgent)
- `impl/claude/agents/k/polynomial.py` (SoulPolynomialAgent)
- `impl/claude/agents/d/polynomial.py` (MemoryPolynomialAgent)
- `impl/claude/agents/e/polynomial.py` (EvolutionPolynomialAgent)
- `impl/claude/agents/poly/_tests/test_cross_polynomial.py`
- `plans/skills/polynomial-agent.md`

### Updated Files
- `impl/claude/agents/poly/protocol.py` (deprecation sugar)
- `docs/architecture-overview.md` (polynomial section)
- `plans/_forest.md` (status update)

---

## Test Summary

| Category | Tests |
|----------|-------|
| Alethic (A-gent) | 38 |
| D-gent polynomial | 29 |
| K-gent polynomial | 28 |
| E-gent polynomial | 28 |
| Poly core | 22 |
| Poly primitives | 40 |
| Cross-polynomial | 12 |
| Property-based | 17 |
| **Total** | **201+** |

---

## Cross-References

- **Skill Guide**: `plans/skills/polynomial-agent.md`
- **Spec**: `spec/architecture/polyfunctor.md`
- **Architecture**: `docs/architecture-overview.md`
- **Theory**: [Niu & Spivak, "Polynomial Functors"](https://arxiv.org/abs/2312.00990)

---

*"The noun is a lie. There is only the rate of change."*
