---
genesis_id: "genesis:L1:id"
layer: 1
layer_name: "kernel"
galois_loss: 0.03
confidence: 0.97
color: "#8BAB8B"
derives_from: ['genesis:L1:compose', 'genesis:L1:judge']
tags: ['L1', 'categorical', 'derived', 'genesis', 'identity']
---

# Id — The Identity Morphism

> *"The agent that does nothing. The unit of composition."*

## Definition

```python
Id: A → A
Id(x) = x
```

ID is the agent that returns its input unchanged.

## Derivation

```
COMPOSE + JUDGE → ID
"What JUDGE never rejects composing with anything"
```

**Loss**: L = 0.03 (derived from two L1 primitives)

## What It Grounds

- The unit of composition: `Id >> f = f = f >> Id`
- The existence of agents as a category (requires identity)
- The "do nothing" baseline for comparison
- Idempotence testing

## Category Laws

ID satisfies the identity laws:
```
Left identity:  Id ∘ f = f
Right identity: f ∘ Id = f
```

## Optimization

ID should be **zero-cost** in composition chains:
```python
def optimize_pipeline(agents: list[Agent]) -> list[Agent]:
    return [a for a in agents if not isinstance(a, Id)]
```
