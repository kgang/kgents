# Agent Foundations

> *"Category theory is not a genus—it IS the foundation."*

The categorical primitives that all agent genera share.

---

## The Unified Agent Model

> *"Everything is an agent. Agents are K-Blocks. K-Blocks are nodes. Nodes are files."*

### The Isomorphism Chain

```
Agent ≅ K-Block ≅ ZeroNode ≅ File
```

| Perspective | What It Sees | Operations |
|-------------|--------------|------------|
| **Agent** | Behavior, state transitions | invoke, compose, judge |
| **K-Block** | Semantic unit, edges | link, derive, witness |
| **ZeroNode** | Axiom, derivation tree | plant, judge, sublate |
| **File** | Persistent content | read, write, version |

These are not different things—they are the **same thing viewed through different lenses**.

### Derivation from Foundational Axioms

Every agent derives from the three pre-categorical axioms:

```
A1 (Entity)   → Agent exists as object in category
A2 (Morphism) → Agent composes with other agents
A3 (Mirror)   → Agent behavior is judged by human oracle

G (Galois)    → Agent has minimal axiom representation
```

The Minimal Kernel operationalizes these:

```
Compose → How agents connect (A2 made operational)
Judge   → How agents are evaluated (A3 made operational)
Ground  → What agents start with (A1 made operational)
```

### Category-Theoretic Grounding

An agent is a **morphism** in the category **Kgents**:

```
Agent[A, B]: A → B

where:
  A = input type (what the agent receives)
  B = output type (what the agent produces)

Composition: Agent[A,B] >> Agent[B,C] = Agent[A,C]
Identity:    Id[A]: A → A (does nothing, composes neutrally)
```

The category laws (identity, associativity) are verified at runtime.

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

| System | Polynomial | Operad | Sheaf |
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
| [t-gent.md](t-gent.md) | T | Testing Agent—verification, probes, categorical laws |

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
