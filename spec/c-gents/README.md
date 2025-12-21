# C-gents: Category Theory

The letter **C** represents agents grounded in category theory—the mathematics of composition.

---

## Why Category Theory?

> "Composition is at the very root of category theory—it's part of the definition of the category itself." — Bartosz Milewski

Category theory provides:
- A rigorous foundation for agent composition
- Abstract patterns that transcend implementation details
- A language for describing transformations

C-gents are not just about math—they're about **composability as a first principle**.

---

## Core Concepts

### Agents as Morphisms

In kgents, agents ARE morphisms:
```
Agent: InputType → OutputType
```

Composition:
```
AgentA: A → B
AgentB: B → C
AgentA ∘ AgentB: A → C
```

---

## The Three Laws

### 1. Associativity
```
(f ∘ g) ∘ h = f ∘ (g ∘ h)
```

### 2. Identity
```
f ∘ id = f
id ∘ f = f
```

### 3. Closure
```
If f: A → B and g: B → C, then (f ∘ g): A → C
```

---

## Specifications

| Document | Description |
|----------|-------------|
| [composition.md](composition.md) | Rules for combining agents |
| [functors.md](functors.md) | Structure-preserving transformations |
| [monads.md](monads.md) | Handling effects and context |

---

## Inspirations

- [Bartosz Milewski's Category Theory for Programmers](https://bartoszmilewski.com/2014/10/28/category-theory-for-programmers-the-preface/)
- [Category Theory for Programming (arXiv)](https://arxiv.org/abs/2209.01259)

---

## See Also

- [composition.md](composition.md) - How agents combine
- [../a-gents/abstract/skeleton.md](../a-gents/abstract/skeleton.md) - Base agent structure
