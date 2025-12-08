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
