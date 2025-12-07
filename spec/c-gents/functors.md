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

## Common Functors

| Functor | Purpose |
|---------|---------|
| Maybe | Handle optional values |
| List | Process collections |
| Async | Non-blocking execution |
| Logged | Add observability |

---

## Example: Maybe Functor

```
Agent: A → B
MaybeAgent: Maybe<A> → Maybe<B>

If input is Nothing: output is Nothing
If input is Just(a): output is Just(agent.invoke(a))
```

---

## See Also

- [composition.md](composition.md) - Agent composition
- [monads.md](monads.md) - Functors with structure
