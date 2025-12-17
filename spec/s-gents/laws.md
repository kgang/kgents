# S-gent Functor Laws

> *"Laws are not constraints. They are guarantees."*

---

## Purpose

This document specifies the functor laws that StateFunctor must satisfy, along with verification approaches.

---

## The Laws

### Law 1: Identity

```
StateFunctor.lift(Id) ≅ Id
```

**Statement**: Lifting the identity agent produces behavior equivalent to identity.

**Interpretation**: If you lift an agent that does nothing (returns its input unchanged), the result should still return input unchanged (modulo state loading/saving overhead).

**Formal**:
```python
∀ a ∈ A:
  await StateFunctor.lift(Id).invoke(a) == a
```

### Law 2: Composition

```
StateFunctor.lift(f >> g) ≅ StateFunctor.lift(f) >> StateFunctor.lift(g)
```

**Statement**: Lifting a composition equals composing lifted agents.

**Interpretation**: It doesn't matter whether you:
1. Compose two agents then lift, or
2. Lift each agent then compose

Both produce equivalent behavior.

**Formal**:
```python
∀ f: Agent[A, B], g: Agent[B, C], a ∈ A:
  await StateFunctor.lift(f >> g).invoke(a) == await (StateFunctor.lift(f) >> StateFunctor.lift(g)).invoke(a)
```

---

## Why These Laws Matter

### Predictable Composition

Laws guarantee that agent composition behaves predictably:

```python
# These are equivalent (by composition law)
pipeline1 = state_functor.lift(parse >> validate >> transform)
pipeline2 = state_functor.lift(parse) >> state_functor.lift(validate) >> state_functor.lift(transform)

# Both produce the same result
assert await pipeline1.invoke(x) == await pipeline2.invoke(x)
```

### Refactoring Safety

Laws enable safe refactoring:

```python
# Original
result = await state_functor.lift(complex_agent).invoke(x)

# Refactored (by identity law, we can add Id without changing behavior)
result = await state_functor.lift(Id >> complex_agent >> Id).invoke(x)
```

### Equational Reasoning

Laws enable reasoning about agent behavior without executing:

```
# Given composition law:
lift(f >> g) ≅ lift(f) >> lift(g)

# We can derive:
lift(f >> g >> h)
  = lift((f >> g) >> h)           # by associativity of >>
  = lift(f >> g) >> lift(h)       # by composition law
  = lift(f) >> lift(g) >> lift(h) # by composition law again
```

---

## Verification Strategy

### Property-Based Testing

Use Hypothesis or similar to generate random agents and inputs:

```python
from hypothesis import given, strategies as st

@given(st.integers())
async def test_identity_law(input_val):
    """Identity law: lift(Id) ≅ Id"""
    state_functor = StateFunctor(
        state_type=dict,
        backend=MemoryBackend(),
        initial_state={},
    )

    lifted_id = state_functor.lift(Id)
    result = await lifted_id.invoke(input_val)

    assert result == input_val  # Identity behavior
```

### Composition Law Verification

```python
@given(st.integers())
async def test_composition_law(input_val):
    """Composition law: lift(f >> g) ≅ lift(f) >> lift(g)"""
    state_functor = StateFunctor(
        state_type=dict,
        backend=MemoryBackend(),
        initial_state={},
    )

    # Two simple agents
    double = Agent.from_function(lambda x: x * 2)
    add_one = Agent.from_function(lambda x: x + 1)

    # Path 1: lift(f >> g)
    composed_then_lifted = state_functor.lift(double >> add_one)

    # Path 2: lift(f) >> lift(g)
    lifted_then_composed = state_functor.lift(double) >> state_functor.lift(add_one)

    # Results must match
    result1 = await composed_then_lifted.invoke(input_val)
    result2 = await lifted_then_composed.invoke(input_val)

    assert result1 == result2
```

### State Threading Verification

Verify state threads correctly through composition:

```python
async def test_state_threading():
    """Verify state threads through lifted composition."""

    counter_logic = lambda x, s: (s.get("count", 0), {**s, "count": s.get("count", 0) + 1})

    state_functor = StateFunctor(
        state_type=dict,
        backend=MemoryBackend(),
        initial_state={"count": 0},
    )

    counter = state_functor.lift_logic(counter_logic)

    # Each invocation should see incremented state
    r1 = await counter.invoke("a")  # Returns 0, state becomes {"count": 1}
    r2 = await counter.invoke("b")  # Returns 1, state becomes {"count": 2}
    r3 = await counter.invoke("c")  # Returns 2, state becomes {"count": 3}

    assert r1 == 0
    assert r2 == 1
    assert r3 == 2
```

---

## Law Proof Sketches

### Identity Law Proof

**Claim**: `StateFunctor.lift(Id) ≅ Id`

**Proof sketch**:
1. `StateFunctor.lift(Id)` produces a `StatefulAgent` wrapping `Id`
2. `StatefulAgent.invoke(a)` does:
   - Load state S
   - Call `Id.invoke((a, S))` → returns `(a, S)` (identity)
   - Save state S
   - Return a
3. Net effect: input a → output a ≡ Id

QED (modulo state effects)

### Composition Law Proof

**Claim**: `StateFunctor.lift(f >> g) ≅ StateFunctor.lift(f) >> StateFunctor.lift(g)`

**Proof sketch**:

**LHS**: `StateFunctor.lift(f >> g)`
1. Load state S₀
2. Call `(f >> g).invoke((a, S₀))`
   - `f.invoke((a, S₀))` → `(b, S₁)`
   - `g.invoke((b, S₁))` → `(c, S₂)`
3. Save state S₂
4. Return c

**RHS**: `StateFunctor.lift(f) >> StateFunctor.lift(g)`
1. `lift(f).invoke(a)`:
   - Load state S₀
   - `f.invoke((a, S₀))` → `(b, S₁)`
   - Save state S₁
   - Return b
2. `lift(g).invoke(b)`:
   - Load state S₁
   - `g.invoke((b, S₁))` → `(c, S₂)`
   - Save state S₂
   - Return c

**Equivalence**:
- Both produce output c
- Both end with state S₂
- RHS has extra load/save between f and g (implementation detail)
- Behavioral equivalence: same input → same output

QED (up to intermediate state saves)

---

## Subtleties and Caveats

### State Loading Overhead

The identity law holds **up to state loading/saving overhead**:

```python
# Pure Id: instant
await Id.invoke(x)  # O(1)

# Lifted Id: includes I/O
await lift(Id).invoke(x)  # O(1) + O(load) + O(save)
```

The **behavior** is equivalent, but performance differs.

### Intermediate Saves

The composition law has a subtlety around intermediate saves:

```python
# lift(f >> g): one load at start, one save at end
# lift(f) >> lift(g): load-save-load-save

# For correctness, this is equivalent
# For performance, lift(f >> g) is more efficient
```

### Non-Deterministic Agents

Laws assume deterministic agents. For non-deterministic agents (e.g., LLM calls), laws hold **in expectation**:

```python
# Stochastic agent: different outputs on each call
# Laws hold if we consider equivalence classes of outputs
```

---

## Integration with FunctorRegistry

StateFunctor should be registered for automatic law verification:

```python
from agents.a.functor_registry import FunctorRegistry

# Register StateFunctor
FunctorRegistry.register(
    name="State",
    functor_class=StateFunctor,
    laws=[
        ("identity", test_state_identity_law),
        ("composition", test_state_composition_law),
    ],
)

# Verify all registered functors
await FunctorRegistry.verify_all()
```

CLI integration:

```bash
kg functor verify state
# Runs identity and composition law tests for StateFunctor
```

---

## Related Laws

### Flux Functor Laws

```
Flux.lift(Id) ≅ Id_Flux
Flux.lift(f >> g) ≅ Flux.lift(f) >> Flux.lift(g)
```

See `spec/c-gents/functor-catalog.md` §13.

### Lens Laws

```
GetPut: lens.set(s, lens.get(s)) == s
PutGet: lens.get(lens.set(s, v)) == v
PutPut: lens.set(lens.set(s, v1), v2) == lens.set(s, v2)
```

See `spec/d-gents/lenses.md`.

### Composed Functor Laws

When composing functors (e.g., Flux ∘ State), the composed functor inherits laws:

```
(F ∘ G).lift(Id) ≅ Id
(F ∘ G).lift(f >> g) ≅ (F ∘ G).lift(f) >> (F ∘ G).lift(g)
```

This follows from functor composition in category theory.

---

## See Also

- [README.md](README.md) — S-gent overview
- [state-functor.md](state-functor.md) — StateFunctor specification
- [composition.md](composition.md) — Composition patterns
- [../c-gents/functor-catalog.md](../c-gents/functor-catalog.md) — Functor catalog and laws
- [../principles.md](../principles.md) — Design principles (§5 Composable)

---

*"A functor without laws is just a function. Laws make it meaningful."*
