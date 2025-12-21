# Agent Foundations

> *"Category theory is not a genus—it IS the foundation."*

The categorical primitives that all agent genera share.

---

## Core Abstractions

| Document | Description |
|----------|-------------|
| [primitives.md](primitives.md) | The 17 irreducible polynomial agents |
| [operads.md](operads.md) | Grammar of composition |
| [composition.md](composition.md) | The `>>` operator and composition laws |
| [functors.md](functors.md) | Structure-preserving transformations |
| [functor-catalog.md](functor-catalog.md) | Catalog of all functors across genera |
| [monads.md](monads.md) | Effect sequencing patterns |
| [flux.md](flux.md) | Discrete → Continuous transformation |
| [emergence.md](emergence.md) | Sheaf-based emergence |

---

## The Three Layers

Every domain-specific system instantiates this pattern:

```
┌────────────────────────────────────────────────────────────────────┐
│  SHEAF       Global coherence from local views                     │
│              Emergence, gluing, consistency                        │
├────────────────────────────────────────────────────────────────────┤
│  OPERAD      Composition grammar with laws                         │
│              Operations, laws, verification                        │
├────────────────────────────────────────────────────────────────────┤
│  POLYAGENT   State machine with mode-dependent inputs              │
│              Positions, directions, transitions                    │
└────────────────────────────────────────────────────────────────────┘
```

See: AD-006 (Unified Categorical Foundation) in `spec/principles.md`

---

## Unified Foundation

All kgents genera (B-gent, D-gent, K-gent, etc.) are built on these primitives:

| Domain | Polynomial | Operad | Sheaf |
|--------|-----------|--------|-------|
| Agent Town | `CitizenPolynomial` | `TOWN_OPERAD` | `TownSheaf` |
| N-Phase | `NPhasePolynomial` | `NPHASE_OPERAD` | `ProjectSheaf` |
| K-gent Soul | `SOUL_POLYNOMIAL` | `SOUL_OPERAD` | `EigenvectorCoherence` |
| D-gent Memory | `MEMORY_POLYNOMIAL` | `MEMORY_OPERAD` | `MemoryConsistency` |

**The Meta-Insight**: Understanding one domain teaches you the others.

---

## Category Laws

These laws are not aspirational—they are **verified**:

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Identity | `Id >> f ≡ f ≡ f >> Id` | `BootstrapWitness.verify_identity_laws()` |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | `BootstrapWitness.verify_composition_laws()` |

**Implication**: Any agent that breaks these laws is NOT a valid agent.

---

## Genus-Specific Extensions

While the foundation is universal, each genus extends it:

| Document | Genus | Description |
|----------|-------|-------------|
| [d-gent.md](d-gent.md) | D | Data Agent—persistence, memory, state |

Other genera live in their own directories (`spec/k-gent/`, `spec/b-gents/`, etc.) but all compose using these foundational primitives.

---

## Implementation

```
impl/claude/agents/poly/       # PolyAgent, primitives
impl/claude/agents/operad/     # Operad, operations, laws
impl/claude/agents/sheaf/      # Sheaf, gluing, emergence
impl/claude/agents/c/          # C-gent categorical implementations
impl/claude/agents/flux/       # Flux functor
```

---

## See Also

- `spec/principles.md` — The seven principles (especially §5 Composable)
- `spec/bootstrap.md` — The irreducible kernel
- `spec/architecture/polyfunctor.md` — Polyfunctor architecture

---

*"From 17 atoms, all agents emerge."*
