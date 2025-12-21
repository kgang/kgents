# Monads

> *"A monad is just a monoid in the category of endofunctors."*
> — The classic joke (that happens to be true)

---

## Definition

A **monad** is a functor with additional structure that allows sequencing computations with context.

Monads solve the problem: *"How do I compose agents that produce wrapped results?"*

---

## The Monad Operations

### unit (return, pure)

Wraps a value in the monadic context:

```
unit: A → M[A]
```

### bind (flatMap, >>=)

Sequences computations, unwrapping and rewrapping:

```
bind: M[A] → (A → M[B]) → M[B]
```

---

## Monad Laws

### Left Identity

```
unit(a).bind(f) ≡ f(a)
```

Wrapping then binding is just calling.

### Right Identity

```
m.bind(unit) ≡ m
```

Binding to unit is a no-op.

### Associativity

```
m.bind(f).bind(g) ≡ m.bind(a → f(a).bind(g))
```

Binding order doesn't matter (respects associativity).

---

## Common Monads for Agents

### Maybe Monad

Sequences computations that might fail:

```python
getUser(id).bind(user → getProfile(user)).bind(profile → ...)
```

Short-circuits on `Nothing`.

### Either Monad

Like Maybe, but carries error information:

```
Right(value) - success
Left(error)  - failure with reason
```

### Async Monad

Sequences asynchronous operations:

```python
fetchData().bind(data → process(data)).bind(result → save(result))
```

### State Monad

Threads state through computations:

```python
get().bind(s → put(s + 1)).bind(_ → get())
```

---

## Why Monads Matter for Agents

**Without monads**, composing effectful agents is awkward:

```python
result1 = agent1.invoke(input)
if result1.is_error: return result1
result2 = agent2.invoke(result1.value)
if result2.is_error: return result2
...
```

**With monads**:

```python
agent1.bind(agent2).bind(agent3).invoke(input)
```

The monad handles the unwrapping/rewrapping automatically.

---

## The State Monad in Detail

**Signature**: `State[S]: Agent[A, B] → StatefulAgent[S, A, B]`

**Polynomial**: `PolyAgent[P, A, B] → PolyAgent[P × LoadSave, A, B]`

where `LoadSave = { LOADING, READY, SAVING }`

### Core Insight: State Threading

State is orthogonal to persistence:
- **D-gent**: WHERE state lives (memory, file, database)
- **State Monad**: HOW state threads through computation

The State Monad lifts agents into stateful computation where state is:
1. Loaded before each invocation
2. Threaded through the computation
3. Saved after each invocation

### The Symbiont Pattern

**Symbiont IS StateFunctor.lift_logic with a D-gent backend:**

```python
# These are equivalent:
symbiont = Symbiont(logic=chat_logic, memory=dgent_memory)

stateful = StateFunctor(
    state_type=ConversationState,
    backend=dgent_memory,
).lift_logic(chat_logic)
```

Symbiont is the **ergonomic pattern**; StateFunctor is the **formal monad**.

### Laws

| Law | Statement | Verification |
|-----|-----------|--------------|
| Identity | `StateFunctor.lift(Id) ≅ Id` | `test_state_identity_law` |
| Composition | `lift(f >> g) ≅ lift(f) >> lift(g)` | `test_state_composition_law` |

---

## Monad Transformers

Stack multiple monads:

```python
# Either + Async = can fail, can await
EitherAsync[E, A] = Async[Either[E, A]]

# State + Maybe = can fail, has state
StateMaybe[S, A] = State[S, Maybe[A]]
```

---

## Monads in kgents

| Monad | Use Case | Implementation |
|-------|----------|----------------|
| Maybe | Optional values | `agents/c/maybe.py` |
| Either | Error handling | `agents/c/either.py` |
| State | State threading | `agents/d/symbiont.py` |
| Async | Async operations | Built-in |

---

## Anti-Patterns

1. **Monad escape**: Unwrapping monadic values too early
2. **Monad confusion**: Mixing monads without transformers
3. **Ignoring laws**: Custom monads that break the three laws

---

## See Also

- [composition.md](composition.md) — Basic composition
- [functors.md](functors.md) — Structure-preserving maps
- [functor-catalog.md](functor-catalog.md) — Functor catalog including State

---

*"Monads are burritos... that compose."*
