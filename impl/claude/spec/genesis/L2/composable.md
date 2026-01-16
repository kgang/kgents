---
genesis_id: "genesis:L2:composable"
layer: 2
layer_name: "principle"
galois_loss: 0.08
confidence: 0.92
color: "#6B8B6B"
derives_from: ['genesis:L1:compose', 'genesis:L1:id']
tags: ['L2', 'categorical', 'composable', 'genesis', 'principle']
---

# COMPOSABLE — The Categorical Principle

> *"Agents are morphisms in a category; composition is primary."*

**Galois Loss**: 0.08 (lowest—most purely categorical)

## Derivation

```
A2 (Morphism) → COMPOSE + ID → COMPOSABLE
"Category laws as design principle"
```

## Definition

**Composable** means agents are morphisms in a category. The laws are
verified, not aspirational.

### The Category Laws (REQUIRED)

| Law | Requirement | Verification |
|-----|-------------|--------------|
| **Identity** | `Id >> f = f = f >> Id` | verify_identity_laws() |
| **Associativity** | `(f >> g) >> h = f >> (g >> h)` | verify_composition_laws() |

### The Test

Ask: **"Can this work with other agents?"**

Check:
1. Does it have clear input/output types?
2. Does Id >> f = f?
3. Does (f >> g) >> h = f >> (g >> h)?

### The Minimal Output Principle

LLM agents should generate the **smallest output that can be reliably composed**:
- Single output per invocation
- Composition at pipeline level, not within agent
