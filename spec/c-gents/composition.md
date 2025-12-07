# Agent Composition

The formal rules for combining agents.

---

## Definition

> **Composition** is the operation that takes two agents and produces a third agent whose behavior is the sequential application of both.

```
Given: Agent f: A → B, Agent g: B → C
Composition: (g ∘ f): A → C
```

---

## Laws

### Associativity
```
(f ∘ g) ∘ h ≡ f ∘ (g ∘ h)
```

### Identity
```
id ∘ f ≡ f
f ∘ id ≡ f
```

### Closure
The composition of two agents is itself an agent.

---

## Type Compatibility

For composition to be valid, f's output type MUST be compatible with g's input type.

```
f: String → Number
g: Number → Boolean
(g ∘ f): String → Boolean  ✓
```

---

## Composition Patterns

### Pipeline
```
input → [A] → [B] → [C] → output
```

### Parallel
```
        ┌→ [A] ─┐
input ──┼→ [B] ─┼→ combine → output
        └→ [C] ─┘
```

### Conditional
```
input → [condition?] → [A] if true
                     → [B] if false
```

---

## See Also

- [functors.md](functors.md) - Maps between categories
- [monads.md](monads.md) - Effect handling
