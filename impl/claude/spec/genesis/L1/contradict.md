---
genesis_id: "genesis:L1:contradict"
layer: 1
layer_name: "kernel"
galois_loss: 0.04
confidence: 0.96
color: "#8B6F5C"
derives_from: ['genesis:L1:judge']
tags: ['L1', 'contradict', 'derived', 'dialectic', 'genesis']
---

# Contradict — Antithesis Generation

> *"The recognition that 'something's off' precedes logic."*

## Definition

```python
Contradict: (Output, Output) → Tension | None
Contradict(a, b) = Tension(thesis=a, antithesis=b) | None
```

CONTRADICT examines two outputs and surfaces if they are in tension.

## Derivation

```
JUDGE → CONTRADICT
"Contradiction is the failure of consistency judgment"
```

**Loss**: L = 0.04 (semantic analysis adds loss)

## What It Grounds

- H-gents dialectic
- Quality assurance
- The ability to catch inconsistency
- Ghost alternative detection

## Tension Modes

| Mode | Signature | Example |
|------|-----------|---------|
| LOGICAL | A and not-A | "We value speed" + "We never rush" |
| EMPIRICAL | Claim vs evidence | Principle says X, metrics show not-X |
| PRAGMATIC | A recommends X, B recommends not-X | Conflicting advice |
| TEMPORAL | Past-self said X, present-self says not-X | Drift over time |

## Galois Interpretation

CONTRADICT detects high loss between alternatives:
```python
def is_contradictory(a, b) -> bool:
    return galois_loss(merge(a, b)) > CONTRADICTION_THRESHOLD
```
