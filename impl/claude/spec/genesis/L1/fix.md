---
genesis_id: "genesis:L1:fix"
layer: 1
layer_name: "kernel"
galois_loss: 0.04
confidence: 0.96
color: "#2E4A2E"
derives_from: ['genesis:L1:compose', 'genesis:L1:judge', 'genesis:L0:galois']
tags: ['L1', 'derived', 'fix', 'fixed-point', 'genesis']
---

# Fix — Fixed-Point Iteration

> *"Self-reference cannot be eliminated from a system that describes itself."*

## Definition

```python
Fix: (A → A) → A
Fix(f) = x where f(x) = x
```

FIX takes a self-referential definition and finds what it stabilizes to.

## Derivation

```
COMPOSE + JUDGE + G (Galois) → FIX
"Fixed-point is composition that passes stability judgment"
```

**Loss**: L = 0.04 (iteration converges, bounding loss)

## What It Grounds

- Recursive agent definitions
- Self-describing specifications
- The bootstrap itself: Fix(Minimal Kernel) = Bootstrap Agents
- All iteration patterns (polling, retry, watch)

## Connection to Lawvere's Fixed-Point Theorem

> In a cartesian closed category, for any point-surjective f: A → A^A,
> there exists x: 1 → A such that f(x) = x.

This is why:
- Self-referential agent definitions are valid (not paradoxical)
- The bootstrap can describe itself
- Agents that modify their own behavior converge to stable points

## The Bootstrap as Fixed Point

The seven bootstrap agents ARE the fixed point:

```
Fix(Compose + Judge + Ground) = {Id, Compose, Judge, Ground,
                                  Contradict, Sublate, Fix}
```
