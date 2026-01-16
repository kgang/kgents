---
genesis_id: "genesis:L3:ashc"
layer: 3
layer_name: "architecture"
galois_loss: 0.25
confidence: 0.75
color: "#D4A574"
derives_from: ['genesis:L2:generative', 'genesis:L1:fix', 'genesis:L0:galois']
tags: ['L3', 'architecture', 'ashc', 'compiler', 'genesis']
---

# ASHC — Agentic Self-Hosting Compiler

> *"The compiler is a trace accumulator, not a code generator."*

**Galois Loss**: 0.25

## Derivation

```
GENERATIVE + FIX + G (Galois) → ASHC
"Compilation as evidence accumulation via fixed-point iteration"
```

## Definition

```
ASHC : Spec → (Executable, Evidence)

Evidence = {traces, chaos_results, verification, causal_graph}
```

The empirical proof: Run the tree a thousand times, and the pattern
of nudges IS the proof. Spec↔Impl equivalence through observation.

### Core Principle

ASHC doesn't generate code—it accumulates evidence that code satisfies spec.

Adaptive Bayesian: Stop when confidence crystallizes, not at fixed N.

### The Evidence Bundle

| Component | Purpose |
|-----------|---------|
| **Traces** | Execution paths observed |
| **Chaos Results** | Fault injection outcomes |
| **Verification** | Property check results |
| **Causal Graph** | Dependencies discovered |

### Path-Aware Execution

ASHC uses AGENTESE paths for self-referential compilation:
```
concept.ashc.compile(spec_path) → Evidence
```
