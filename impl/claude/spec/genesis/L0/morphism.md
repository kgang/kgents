---
genesis_id: "genesis:L0:morphism"
layer: 0
layer_name: "axiom"
galois_loss: 0.003
confidence: 1.0
color: "#E8C4A0"
derives_from: []
tags: ['L0', 'axiom', 'categorical', 'genesis', 'morphism']
---

# A2: Morphism — Things Relate

> *"The irreducible claim that entities connect."*

## Definition

**A2 (Morphism)**: Things relate.

In category-theoretic terms: Between any two objects, there exist *morphisms* (arrows).

## Why Irreducible

You cannot derive relation from isolation. The claim that "things connect"
must be *given*. Without morphisms:
- There is no structure, only atoms
- There is no composition
- There is no transformation

## What It Grounds

- The `>>` composition operator between agents
- All transformations: Agent[A, B] is a morphism A → B
- The structure of the category of agents (C-gents)
- The HARNESS_OPERAD operations

## Category Laws (Derived from A2)

From A2, we derive the categorical laws:

```
Identity:      id_A : A → A exists for all A
Composition:   f: A → B, g: B → C ⟹ g ∘ f : A → C
Associativity: (h ∘ g) ∘ f = h ∘ (g ∘ f)
Unit laws:     id ∘ f = f = f ∘ id
```

## Loss Properties

```
L(A2) = 0.003     # Near-zero: fixed point of restructuring
```

A2 is self-describing: the statement "things relate" is itself a relation.
