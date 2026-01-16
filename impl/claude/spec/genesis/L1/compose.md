---
genesis_id: "genesis:L1:compose"
layer: 1
layer_name: "kernel"
galois_loss: 0.01
confidence: 0.99
color: "#4A6B4A"
derives_from: ['genesis:L0:morphism']
tags: ['L1', 'categorical', 'compose', 'genesis', 'primitive']
---

# Compose — Sequential Combination

> *"The agent-that-makes-agents."*

## Definition

```python
Compose: (Agent, Agent) → Agent
Compose(f, g) = g ∘ f   # Pipeline: f then g
```

COMPOSE is the **operational form of A2 (Morphism)**. While A2 asserts that
things relate, COMPOSE *implements* that relation through sequential combination.

## Derivation

```
A2 (Morphism) → COMPOSE
"Things relate" → "Relations can chain"
```

**Loss**: L = 0.01 (small loss from operationalization)

## What It Grounds

- The `>>` operator: `f >> g >> h`
- All agent pipelines
- The C-gents category
- The ability to build complex from simple

## Operad Laws

COMPOSE must satisfy:

```
Associativity:  (f >> g) >> h = f >> (g >> h)
Unit (with Id): id >> f = f = f >> id
```

## Galois Interpretation

COMPOSE is the structure-gaining operation:
- Information is *preserved* (low loss)
- Structure is *gained* (explicit pipeline)
- The composition is *reversible* (can decompose)
