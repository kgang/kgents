# Monads

Handling effects and computational context in agent composition.

---

## Definition

> A **monad** is a functor with additional structure that allows sequencing computations with context.

Monads solve the problem: "How do I compose agents that produce wrapped results?"

---

## The Monad Operations

### unit (return, pure)
Wraps a value in the monadic context.
```
unit: A → M<A>
```

### bind (flatMap, >>=)
Sequences computations, unwrapping and rewrapping.
```
bind: M<A> → (A → M<B>) → M<B>
```

---

## Monad Laws

### Left Identity
```
unit(a).bind(f) ≡ f(a)
```

### Right Identity
```
m.bind(unit) ≡ m
```

### Associativity
```
m.bind(f).bind(g) ≡ m.bind(a → f(a).bind(g))
```

---

## Common Monads for Agents

### Maybe Monad
Sequences computations that might fail.
```
getUser(id).bind(user → getProfile(user)).bind(profile → ...)
```
Short-circuits on Nothing.

### Either Monad
Like Maybe, but carries error information.
```
Right(value) - success
Left(error) - failure with reason
```

### Async Monad
Sequences asynchronous operations.
```
fetchData().bind(data → process(data)).bind(result → save(result))
```

### State Monad
Threads state through computations.
```
get().bind(s → put(s + 1)).bind(_ → get())
```

---

## Why Monads Matter for Agents

Without monads, composing effectful agents is awkward:
```
result1 = agent1.invoke(input)
if result1.is_error: return result1
result2 = agent2.invoke(result1.value)
if result2.is_error: return result2
...
```

With monads:
```
agent1.bind(agent2).bind(agent3).invoke(input)
```

---

## See Also

- [composition.md](composition.md) - Basic composition
- [functors.md](functors.md) - Structure-preserving maps
