---
genesis_id: "genesis:L1:ground"
layer: 1
layer_name: "kernel"
galois_loss: 0.01
confidence: 0.99
color: "#6B4E3D"
derives_from: ['genesis:L0:entity']
tags: ['L1', 'empirical', 'genesis', 'ground', 'primitive']
---

# Ground — Factual Seed

> *"The irreducible facts about person and world."*

## Definition

```python
Ground: Void → Facts
Ground() = {Kent's preferences, world state, initial conditions}
```

GROUND is the **operational form of A1 (Entity)**. While A1 asserts that
things exist, GROUND *produces* the actual things that exist in the system.

## Derivation

```
A1 (Entity) → GROUND
"Things exist" → "Here are the things"
```

**Loss**: L = 0.01 (serialization introduces tiny loss)

## What It Grounds

- K-gent's persona (name, roles, preferences, patterns, values)
- World context (date, active projects, environment)
- History seed (past decisions, established patterns)
- All personalization in the system

## The Bootstrap Paradox

GROUND reveals the fundamental limit of algorithmic bootstrapping:

> **Ground cannot be bypassed.** LLMs can amplify but not replace Ground.

What LLMs *can* do:
- Amplify Ground (generate variations, explore implications)
- Apply Ground (translate preferences into code)
- Extend Ground (infer related preferences from stated ones)

What LLMs *cannot* do:
- Create Ground from nothing
- Replace human judgment about what matters
