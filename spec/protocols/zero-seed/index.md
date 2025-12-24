# Zero Seed Protocol (v2)

> *"The proof IS the decision. The mark IS the witness. The seed IS the garden."*

**Filed**: 2025-12-24
**Status**: Genesis v2 — Radical Axiom Reduction
**Grade Target**: A+ (95%+)

---

## The Core Insight

**Two axioms. One meta-principle. Seven layers. Infinite gardens.**

Zero Seed achieves maximum generativity through radical compression. The entire seven-layer epistemic holarchy derives from:

| Component | Statement |
|-----------|-----------|
| **A1: Entity** | Everything is a node |
| **A2: Morphism** | Everything composes |
| **M: Justification** | Every node justifies its existence—or admits it cannot |

From these three foundations, the full system regenerates:
- Seven epistemic layers (L1-L7)
- Full witnessing (every change traced)
- Proof requirements (Toulmin structure for L3+)
- Contradiction tolerance (paraconsistent dialectics)
- AGENTESE mapping (five contexts)

---

## Module Index

| Module | Purpose | Key Content |
|--------|---------|-------------|
| [`core.md`](./core.md) | Foundation | 2 Axioms + Meta, data model, laws |
| [`layers.md`](./layers.md) | **Galois derivation** | **Why 7 layers, loss-depth correspondence, automatic assignment** ⭐ |
| [`navigation.md`](./navigation.md) | Telescope UI | Focal model, keybindings, clustering |
| [`discovery.md`](./discovery.md) | Axiom discovery | Three-stage process, Mirror Test |
| [`proof.md`](./proof.md) | Witnessing | Toulmin proofs, batching strategies, paraconsistency |
| [`integration.md`](./integration.md) | Ecosystem | Void services, edge creation, AGENTESE |
| [`bootstrap.md`](./bootstrap.md) | Initialization | Strange loop, retroactive witnessing |
| [`dp.md`](./dp.md) | DP-Native | Agent-DP isomorphism, value functions |
| [`llm.md`](./llm.md) | LLM intelligence | Liberal budgets, self-awareness, minimal-edit UX |

---

## Prerequisites

| Prerequisite | Location | What It Provides |
|--------------|----------|------------------|
| **Constitution** | `spec/principles/CONSTITUTION.md` | The 7+7 principles (design + governance) |
| **AGENTESE** | `spec/protocols/agentese.md` | Five contexts, path semantics, observer model |
| **Witness Protocol** | `spec/protocols/witness-primitives.md` | Mark and Crystal structures |
| **K-Block** | `spec/protocols/k-block.md` | Transactional isolation for editing |

**Import Order**: Constitution → AGENTESE → Witness → K-Block → Zero Seed

---

## What's New in v2

### Radical Changes

| Aspect | v1 | v2 | Rationale |
|--------|----|----|-----------|
| **Axiom Structure** | "3 axioms" (implicit 4th) | 2 Axioms + 1 Meta | More categorical rigor |
| **Organization** | 2498-line monolith | 8 modular files | Easier maintenance |
| **Witness Batching** | "Full witnessing, no exceptions" | Three modes (single/session/lazy) | Address performance tension |
| **Composition** | Mentioned but unformal | Explicit `>>` operator with laws | Category-theoretic correctness |
| **Paraconsistency** | Tolerated but undefined | Three-valued logic + explosion prevention | Formal guarantees |

### Addressing Review Findings

| Priority | Issue | Resolution |
|----------|-------|------------|
| **P1** | Composition operator unformal | Added `__rshift__` with laws in `core.md` |
| **P1** | Witness batching missing | Added three modes in `proof.md` |
| **P1** | Layer type unconstrained | Added `Annotated[int, Field(ge=1, le=7)]` |
| **P2** | Paraconsistency undefined | Added three-valued logic in `proof.md` |
| **P2** | Minimal kernel was 3 (actually 4) | Reframed as 2 Axioms + 1 Meta |
| **P3** | 7-layer justification weak | **Galois Modularization derivation in `layers.md`** ⭐ |

---

## Self-Validation

### This Spec's Toulmin Proof

```yaml
data: |
  - 3 years kgents development
  - ~52K lines across 20+ systems
  - Four independent self-validation analyses (categorical, epistemic, dialectical, generative)
  - 85% regenerable from 2 axioms + 1 meta-principle

warrant: |
  Radical axiom reduction achieves maximum generativity.
  2 Axioms + 1 Meta-Principle derives the full seven-layer system.
  Justification-as-meta-principle grounds both layers AND witnessing.

claim: |
  The Zero Seed Protocol provides a minimal generative kernel —
  enough structure to grow from, sparse enough to make your own.

qualifier: probably

rebuttals:
  - "Unless radical compression makes the system harder to understand"
  - "Unless justification-as-meta-principle is too abstract for users"
  - "Unless 7-layer taxonomy proves too complex for working memory"

tier: CATEGORICAL
principles: [generative, composable, tasteful]
```

### Grounding Chain

```
A1 (Entity) + A2 (Morphism)
    ↓ generates
M (Justification)
    ↓ derives
void.axiom.generative-principle (L1)
    ↓ grounds
void.value.cultivable-bootstrap (L2)
    ↓ justifies
concept.goal.provide-zero-seed (L3)
    ↓ specifies
concept.spec.zero-seed (L4) ← THIS SPEC
```

---

## Open Questions

These remain for dialectical refinement:

### Conceptual

1. **Is justification-as-meta too abstract?** May need more concrete derivation examples.
2. **Layer skip semantics**: When is L1→L4 valid? When is it a smell?
3. **Multi-user semantics**: When users share a graph, whose Mirror Test wins?

### Technical

4. **Composition of edge kinds**: `compose_edge_kinds(GROUNDS, JUSTIFIES) = ?`
5. **Value iteration convergence**: Does Zero Seed guarantee convergence?
6. **Lazy witness durability**: How do we handle crashes in lazy mode?

### UX

7. **Axiom retirement**: How do we gracefully deprecate axioms?
8. **Tier selection**: Should users choose LLM tier or let system decide?
9. **3D/VR projection**: What affordances make sense in spatial computing?

---

## Related Specs

- `spec/protocols/witness-primitives.md` — Mark and Crystal structures
- `spec/protocols/k-block.md` — K-Block isolation
- `spec/protocols/typed-hypergraph.md` — Hypergraph model
- `spec/principles/CONSTITUTION.md` — The 7+7 principles
- `spec/theory/dp-native-kgents.md` — DP-Agent Isomorphism
- `spec/theory/agent-dp.md` — Agent Space as Dynamic Programming

---

## Implementation Path

1. Implement `ZeroNode` and `ZeroEdge` in `services/zero_seed/`
2. Create `ZeroSeedConstitution` extending `dp/core/constitution.py`
3. Implement `AxiomDiscoveryMetaDP` for three-stage discovery
4. Add `TelescopeValueAgent` for value-guided navigation
5. Bridge PolicyTrace ↔ Toulmin Proof with `dp/witness/bridge.py`
6. Implement `LLMCallMark` and `TokenBudget`
7. Add LLM operations: axiom mining, proof validation, contradiction detection
8. Implement retroactive witnessing for bootstrap
9. Run Mirror Test with Kent on revised spec

---

*"Two axioms. One meta-principle. Seven layers. Infinite gardens."*

---

**v2 Filed**: 2025-12-24
**Previous**: `spec/protocols/zero-seed.md` (2498 lines, monolithic)
**Review Source**: `plans/zero-seed-review.md`
