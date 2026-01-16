---
genesis_id: "genesis:L1:sublate"
layer: 1
layer_name: "kernel"
galois_loss: 0.05
confidence: 0.95
color: "#AB9080"
derives_from: ['genesis:L1:compose', 'genesis:L1:judge', 'genesis:L1:contradict']
tags: ['L1', 'derived', 'dialectic', 'genesis', 'sublate']
---

# Sublate — Synthesis

> *"The creative leap from thesis+antithesis to synthesis is not mechanical."*

## Definition

```python
Sublate: Tension → Synthesis | HoldTension
Sublate(tension) = {preserve, negate, elevate} | "too soon"
```

SUBLATE takes a contradiction and attempts synthesis—or recognizes that
the tension should be held.

## Derivation

```
COMPOSE + JUDGE + CONTRADICT → SUBLATE
"Synthesis is composition that passes judgment"
```

**Loss**: L = 0.05 (highest loss among derived primitives)

## What It Grounds

- H-hegel dialectic engine
- System evolution
- The ability to grow through contradiction
- Conflict resolution protocols

## The Hegelian Move

SUBLATE performs the classic Hegelian operation:
- **Preserve**: What from thesis and antithesis survives
- **Negate**: What is canceled out
- **Elevate**: What new level emerges

## Wisdom to Hold

Sometimes the right answer is **HoldTension**:
```python
if tension.maturity < SYNTHESIS_THRESHOLD:
    return HoldTension(
        reason="Premature synthesis discards information",
        revisit_at=tension.natural_resolution_time,
    )
```
