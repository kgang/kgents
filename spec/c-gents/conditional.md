# Conditional Composition

Branching patterns for agent composition.

---

## Definition

> **Conditional composition** allows agent selection based on runtime predicates, enabling dynamic agent pipelines.

```
input → [predicate?] → [A] if true
                      → [B] if false
```

---

## Agents

### Branch

The fundamental conditional combinator.

```
Branch: (Predicate, Agent[A,B], Agent[A,C]) → Agent[A, B|C]
```

**Semantics**:
- If predicate(input) is True, runs if_true agent
- If predicate(input) is False, runs if_false agent
- Returns output from whichever branch was taken

**Example**:
```python
classify = branch(
    predicate=lambda x: x.confidence > 0.8,
    if_true=accept_agent,
    if_false=review_agent,
)
```

---

### Switch

Multi-way branching based on a key function.

```
Switch: (KeyFn, Cases, Default) → Agent[A, B]
```

**Semantics**:
- Computes key = key_fn(input)
- Selects agent from cases[key], or default if not found
- Runs selected agent on input

**Example**:
```python
router = switch(
    key_fn=lambda x: x.type,
    cases={
        "query": query_agent,
        "command": command_agent,
        "chat": chat_agent,
    },
    default=fallback_agent,
)
```

---

### Guarded

Runs agent only if guard passes.

```
Guarded: (Guard, Agent, OnFail) → Agent[A, B]
```

**Semantics**:
- If guard(input) is True, runs agent
- If guard(input) is False, returns on_fail value
- Useful for validation-then-transform patterns

**Example**:
```python
safe_delete = guarded(
    guard=lambda x: x.user.has_permission("delete"),
    agent=delete_agent,
    on_fail=PermissionDenied(),
)
```

---

### Filter

Filters a list based on a predicate.

```
Filter: Predicate → Agent[List[A], List[A]]
```

**Semantics**:
- Keeps only elements where predicate returns True
- Preserves order

---

## Laws

### Exhaustive Branch

For any input, exactly one branch is taken:
```
branch(p, A, B)(x) = A(x) if p(x) else B(x)
```

### Default Safety

Switch with default never fails:
```
switch(k, cases, default)(x) always succeeds
```

### Guard Composition

Guards compose with boolean operations:
```
guarded(p1 AND p2, A, fail) = guarded(p1, guarded(p2, A, fail), fail)
```

---

## See Also

- [composition.md](composition.md) - Base composition laws
- [parallel.md](parallel.md) - Concurrent composition
- [functors.md](functors.md) - Structure-preserving maps
