# Functors

Structure-preserving maps between agent categories.

---

## Definition

> A **functor** maps agents from one category to another while preserving composition.

---

## Functor Laws

### Identity Preservation
```
F(id_A) = id_F(A)
```

### Composition Preservation
```
F(g ∘ f) = F(g) ∘ F(f)
```

---

## Polynomial Foundation

> *"Functors in kgents are polynomial endofunctors—they transform agents as dynamical systems."*

### The Polynomial Perspective

Traditional functor theory treats agents as functions: `Agent: A → B`. The **polyfunctor architecture** (see `spec/architecture/polyfunctor.md`) reveals that kgents functors are actually **polynomial functor endomorphisms**:

```
Functor: PolyAgent[S, A, B] → PolyAgent[S', A', B']
```

A functor transforms:
- **Positions** (S → S'): The agent's state space
- **Directions** (A → A'): Valid inputs at each state
- **Transitions** ((S × A → (S, B)) → (S' × A' → (S', B'))): Dynamics

### Why This Matters

1. **State-Aware Transformation**: Functors can modify how agents handle internal state
2. **Direction Filtering**: Functors can restrict/expand valid inputs per state
3. **Transition Interception**: Functors wrap state transitions (not just outputs)

### Functor as Endomorphism

Most kgents functors are **endofunctors**—they map the Agent category to itself:

```
F: Agent[A, B] → Agent[A', B']  (traditional view)
F: PolyAgent[S, A, B] → PolyAgent[S', A', B']  (polynomial view)
```

The polynomial view reveals that even "signature-preserving" functors (like Trace) may transform the state space.

### Laws in Polynomial Terms

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

### Functor Categories

| Category | State Transform | Direction Transform | Transition Transform |
|----------|-----------------|---------------------|----------------------|
| **Lifting** | Add states | Wrap types | Wrap dynamics |
| **Filtering** | Restrict states | Restrict inputs | Guard transitions |
| **Observing** | Add observation state | Identity | Emit side effects |
| **Economizing** | Add budget state | Identity | Meter transitions |

---

## Common Functors

| Functor | Purpose |
|---------|---------|
| Maybe | Handle optional values |
| List | Process collections |
| Async | Non-blocking execution |
| Logged | Add observability |
| Promise | Defer computation until needed |

---

## Example: Maybe Functor

```
Agent: A → B
MaybeAgent: Maybe<A> → Maybe<B>

If input is Nothing: output is Nothing
If input is Just(a): output is Just(agent.invoke(a))
```

---

## Example: Promise Functor

```
Agent: A → B
PromiseAgent: A → Promise<B>

Promise<B> is not computed until resolve() called.
If resolve() fails, returns Ground value.
```

**Functor Laws for Promise**:

```python
# Identity preservation
Promise(Id) = PromiseId
# where PromiseId returns resolved Promise(x) for any x

# Composition preservation
Promise(f >> g) = Promise(f) >> Promise(g)
# Composing promises defers both operations
```

**Structure**:

```python
@dataclass
class Promise(Generic[T]):
    intent: str                    # What this promises to deliver
    computation: Callable[[], T]   # Deferred computation
    ground: T                      # Fallback if computation fails
    resolved: Optional[T] = None   # Cached result after resolve()

    async def resolve(self) -> T:
        """Execute deferred computation, cache result."""
        if self.resolved is not None:
            return self.resolved

        try:
            result = await self.computation()
            self.resolved = result
            return result
        except Exception:
            return self.ground  # Collapse to Ground on failure
```

**Key Property**: Promises are **lazy functors**—they defer the functor's action until explicitly requested. This enables:
- Computation on demand
- Parallel resolution of independent promises
- Safe fallback via Ground

**See**: `spec/j-gents/lazy.md` for full Promise specification

---

## See Also

- [composition.md](composition.md) - Agent composition
- [monads.md](monads.md) - Functors with structure
- [functor-catalog.md](functor-catalog.md) - Complete functor catalog with polynomial interpretations
- [../architecture/polyfunctor.md](../architecture/polyfunctor.md) - Polyfunctor architecture specification
- [../agents/primitives.md](../agents/primitives.md) - 17 primitive polynomial agents
