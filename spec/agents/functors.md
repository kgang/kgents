# Functors

> *"A functor is a structure-preserving map between categories."*
> — Bartosz Milewski

---

## Definition

A **functor** maps agents from one category to another while preserving composition:

```
F: Category C → Category D
```

For every agent `f: A → B` in C, there exists `F(f): F(A) → F(B)` in D.

---

## Functor Laws

### Identity Preservation

```
F(id_A) = id_F(A)
```

Functors map identity to identity.

### Composition Preservation

```
F(g ∘ f) = F(g) ∘ F(f)
```

Functors preserve how morphisms compose.

---

## Polynomial Foundation

> *"Functors in kgents are polynomial endofunctors—they transform agents as dynamical systems."*

### Traditional vs Polynomial View

```
Traditional: F: Agent[A, B] → Agent[A', B']
Polynomial:  F: PolyAgent[S, A, B] → PolyAgent[S', A', B']
```

A polynomial functor transforms:
- **Positions** (S → S'): The agent's state space
- **Directions** (A → A'): Valid inputs at each state
- **Transitions** ((S × A → (S, B)) → (S' × A' → (S', B'))): Dynamics

### Why This Matters

1. **State-Aware Transformation**: Functors can modify how agents handle internal state
2. **Direction Filtering**: Functors can restrict/expand valid inputs per state
3. **Transition Interception**: Functors wrap state transitions (not just outputs)

---

## Functor Categories

| Category | State Transform | Direction Transform | Transition Transform |
|----------|-----------------|---------------------|----------------------|
| **Lifting** | Add states | Wrap types | Wrap dynamics |
| **Filtering** | Restrict states | Restrict inputs | Guard transitions |
| **Observing** | Add observation state | Identity | Emit side effects |
| **Economizing** | Add budget state | Identity | Meter transitions |

---

## Common Functors

| Functor | Signature | Purpose |
|---------|-----------|---------|
| Maybe | `Agent[A,B] → Agent[Maybe[A], Maybe[B]]` | Handle optional values |
| Either | `Agent[A,B] → Agent[A, Either[E,B]]` | Carry error information |
| Async | `Agent[A,B] → Agent[A, Awaitable[B]]` | Non-blocking execution |
| Logged | `Agent[A,B] → Agent[A, B]` + side effect | Add observability |
| Promise | `Agent[A,B] → Agent[A, Promise[B]]` | Defer computation |

---

## The Maybe Functor

```
Agent: A → B
MaybeAgent: Maybe[A] → Maybe[B]

If input is Nothing: output is Nothing
If input is Just(a): output is Just(agent.invoke(a))
```

---

## The Promise Functor

```
Agent: A → B
PromiseAgent: A → Promise[B]

Promise[B] is not computed until resolve() called.
If resolve() fails, returns Ground value.
```

**Functor Laws for Promise**:

```python
# Identity preservation
Promise(Id) = PromiseId

# Composition preservation
Promise(f >> g) = Promise(f) >> Promise(g)
```

**Key Property**: Promises are **lazy functors**—they defer the functor's action until explicitly requested.

---

## Universal Functor Protocol (AD-001)

All functor-like patterns derive from `UniversalFunctor`:

```python
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

This enables:
- Uniform law verification via `FunctorRegistry.verify_all()`
- K-gent's `intercept()` as a functor (`SoulFunctor`)
- Halo capabilities compiling to functor composition

---

## Laws in Polynomial Terms

**Identity Preservation** (polynomial):
```
F(Id_P) = Id_{F(P)}
```
Where `Id_P` is the identity polynomial (single state, pass-through).

**Composition Preservation** (polynomial):
```
F(P ∘ Q) = F(P) ∘ F(Q)
```
Where `∘` is polynomial substitution (wiring diagram composition).

---

## Anti-Patterns

1. **Breaking functor laws**: Transformation that doesn't preserve identity/composition
2. **Implicit functor stacking**: Hidden wrapping without documentation
3. **Non-commuting functors without documentation**: Order matters—document it

```python
# Order matters!
Metered(Trace(agent)) != Trace(Metered(agent))
# First: Measures traced execution cost
# Second: Traces metering overhead
```

---

## Implementation

```
impl/claude/agents/c/functor.py       # UniversalFunctor protocol
impl/claude/agents/c/maybe.py         # Maybe functor
impl/claude/agents/c/either.py        # Either functor
impl/claude/agents/j/promise.py       # Promise functor
```

---

## See Also

- [functor-catalog.md](functor-catalog.md) — Complete catalog with polynomial interpretations
- [composition.md](composition.md) — Agent composition
- [monads.md](monads.md) — Functors with structure
- [primitives.md](primitives.md) — 17 primitive polynomial agents
- `spec/architecture/polyfunctor.md` — Polyfunctor architecture

---

*"The structure is preserved because the functor IS structure-preserving."*
