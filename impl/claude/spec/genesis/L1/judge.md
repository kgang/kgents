---
genesis_id: "genesis:L1:judge"
layer: 1
layer_name: "kernel"
galois_loss: 0.02
confidence: 0.98
color: "#6B8B6B"
derives_from: ['genesis:L0:mirror']
tags: ['L1', 'evaluation', 'genesis', 'judge', 'primitive']
---

# Judge — Verdict Generation

> *"Taste cannot be computed. But it can be invoked."*

## Definition

```python
Judge: (Agent, Principles) → Verdict
Judge(agent, principles) = {ACCEPT, REJECT, REVISE(how)}
```

JUDGE is the **operational form of A3 (Mirror)**. While A3 asserts that
human judgment grounds value, JUDGE *implements* that judgment through
verdict generation.

## Derivation

```
A3 (Mirror) → JUDGE
"We judge by reflection" → "Reflection produces verdicts"
```

**Loss**: L = 0.02 (application of principles requires interpretation)

## What It Grounds

- Quality control in generation loops
- The seven principles as evaluation criteria
- Constitutional scoring
- The stopping condition for Fix

## The Seven Mini-Judges

| Mini-Judge | Criterion |
|------------|-----------|
| Judge-taste | Is this aesthetically considered? |
| Judge-curate | Does this add unique value? |
| Judge-ethics | Does this respect human agency? |
| Judge-joy | Would I enjoy this? |
| Judge-compose | Can this combine with others? |
| Judge-hetero | Does this avoid fixed hierarchy? |
| Judge-generate | Could this be regenerated from spec? |

## Galois Interpretation

JUDGE is the loss-detecting operation:
- High loss → likely REJECT
- Low loss → likely ACCEPT
- Medium loss → likely REVISE
