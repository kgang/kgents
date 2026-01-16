---
genesis_id: "genesis:L2:generative"
layer: 2
layer_name: "principle"
galois_loss: 0.15
confidence: 0.85
color: "#F5E6D3"
derives_from: ['genesis:L1:ground', 'genesis:L1:compose', 'genesis:L1:fix', 'genesis:L0:galois']
tags: ['L2', 'compression', 'generative', 'genesis', 'principle']
---

# GENERATIVE — The Compression Principle

> *"Spec is compression; design should generate implementation."*

**Galois Loss**: 0.15

## Derivation

```
GROUND + COMPOSE + FIX + G (Galois) → GENERATIVE
"Spec as fixed point under regeneration"
```

## Definition

**Generative** means spec is compression and design should generate implementation.

### The Generative Test

A design is generative if:
1. You could delete impl and regenerate from spec
2. Regenerated impl is isomorphic to original
3. Spec is smaller than impl (compression achieved)

**Formal**: `L(regenerate(spec)) < epsilon`

### The Galois Connection

```
Compression quality = 1 - L(spec -> impl -> spec)

Where:
  L(P) = d(P, C(R(P)))   # Galois loss
  R = restructure        # spec -> impl
  C = reconstitute       # impl -> spec
```

Good spec = fixed point under regeneration: `R(C(spec)) ~ spec`

### Mandates

| Mandate | Description |
|---------|-------------|
| **Spec captures judgment** | Design decisions made once |
| **Impl follows mechanically** | Given spec + Ground, impl is derivable |
| **Compression is quality** | If you can't compress, you don't understand |
