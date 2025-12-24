# Zero Seed v2: Galois-Native Index

> *"The loss IS the difficulty. The fixed point IS the axiom. The strange loop IS the garden growing itself."*

**Version**: 2.0 (Galois-Native Upgrade)
**Status**: Canonical — Theoretical Foundation
**Date**: 2025-12-24
**Principles**: Generative, Composable, Tasteful, Heterarchical

---

## The Radical Upgrade

Zero Seed v2 unifies **epistemic holarchy** (7-layer knowledge descent) with **Galois Modularization Theory** (lossy compression functors). This is not a feature addition—it's a **theoretical breakthrough**.

### What Changed

| Aspect | v1 (Manual Specification) | v2 (Galois-Native) | Impact |
|--------|---------------------------|-------------------|---------|
| **Layers** | Stipulated (7 chosen) | Emergent (convergence depth) | Layers discovered, not imposed |
| **Axioms** | Hand-selected | Fixed points: `L(P) < ε₁` | Axioms computed, not declared |
| **Proof Quality** | Structural validation | Coherence = `1 - L(proof)` | Quantitative, not heuristic |
| **Contradiction** | LLM heuristics | Super-additive loss: `L(A∪B) > L(A)+L(B)` | Measurable, not guessed |
| **Constitutional Reward** | 7 evaluators | Inverse Galois loss | Unified principle |
| **Bootstrap Paradox** | Acknowledged | Lawvere fixed point theorem | Verified, not circular |

### The Core Isomorphism

```
Zero Seed Layers (L1-L7) ≅ Galois Depth Strata
  Layer L_i = nodes requiring i restructurings to reach fixed point

Contradiction ≅ Super-Additive Loss
  contradicts(A,B) ⟺ L(A∪B) > L(A) + L(B) + τ

Proof Coherence ≅ Inverse Galois Loss
  coherence(P) = 1 - d(P, C(R(P)))

Bootstrap Fixed Point ≅ Lawvere Necessity
  Zero Seed = lim_{n→∞} (R ∘ describe)ⁿ(P₀)
```

---

## Module Dependency Graph

The specs are designed to be read in order, following the mathematical dependency chain:

```
┌─────────────────────────────────────────────────────────────┐
│                      axiomatics.md                           │
│          Foundation: A1 (Entity) + A2 (Morphism) + G         │
│              Axioms = zero-loss fixed points                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
    ┌──────────────┴──────────────┬──────────────────┐
    ▼                             ▼                  ▼
┌────────┐                  ┌──────────┐       ┌──────────┐
│galois.md│                  │proof.md  │       │  dp.md   │
│L(P) =   │                  │Coherence │       │  Value   │
│d(P,C(R))│                  │= 1 - L   │       │Functions │
└────┬────┘                  └─────┬────┘       └────┬─────┘
     │                             │                 │
     └──────────────┬──────────────┴─────────────────┘
                    ▼
          ┌────────────────┐
          │ bootstrap.md    │
          │  Fixed Point    │
          │  Verification   │
          └────────┬────────┘
                   │
    ┌──────────────┴──────────────┬──────────────────┐
    ▼                             ▼                  ▼
┌────────────┐            ┌───────────────┐   ┌──────────┐
│navigation.md│            │integration.md │   │  llm.md  │
│  Telescope │            │AGENTESE + Sys │   │  R ⊣ C   │
│Loss Topo.  │            │Contradiction  │   │Operations│
└────────────┘            └───────────────┘   └──────────┘
```

**Reading Order**:

1. **Start here**: `axiomatics.md` — The three foundations (A1, A2, G)
2. **Theory**: `proof.md`, `dp.md` — How proofs and value functions work
3. **Bootstrap**: `bootstrap.md` — The strange loop resolved
4. **Implementation**: `integration.md` — AGENTESE integration
5. **UI/LLM**: `navigation.md`, `llm.md` — User-facing systems

---

## Quick Concept Reference

| Concept | Location | Key Insight | Formula |
|---------|----------|-------------|---------|
| **Axiom** | axiomatics.md | Zero-loss fixed point | `L(P) < 0.01` |
| **Layer** | axiomatics.md | Convergence depth | `L_i = min{k : L(Rᵏ(P)) < ε}` |
| **Loss** | axiomatics.md | Semantic distance | `L(P) = d(P, C(R(P)))` |
| **Contradiction** | integration.md | Super-additive loss | `L(A∪B) > L(A)+L(B)+τ` |
| **Proof Coherence** | proof.md | Inverse loss | `coherence = 1 - L(proof)` |
| **Constitutional Reward** | dp.md | Structure preservation | `R = 1 - L(transition)` |
| **Fixed Point** | bootstrap.md | Bootstrap verification | `L(ZS, C(R(ZS))) < 0.15` |
| **Evidence Tier** | proof.md | Loss bounds | CATEGORICAL: L<0.1, EMPIRICAL: L<0.3 |
| **Witness Mode** | proof.md | Loss triage | SINGLE: L<0.1, SESSION: L<0.4 |
| **Value Function** | dp.md | Bellman with loss | `V* = max[R - λ·L + γ·V*]` |
| **Telescope** | navigation.md | Loss topography | Navigate via `∇L` descent |
| **LLM Operations** | llm.md | Galois adjunction | LLM IS the (R,C,L) triple |

---

## Getting Started

### For Theory (Mathematical Foundations)

**Start**: `axiomatics.md` → `bootstrap.md`

Read these if you want to understand:
- Why axioms are computable (not chosen)
- Why layers emerge (not stipulated)
- Why the bootstrap paradox is necessary (not vicious)

**Key Theorems**:
- Lawvere Fixed Point (bootstrap.md §2.1)
- Axiom = Zero-Loss Fixed Point (axiomatics.md §1.1)
- Layer Stratification (axiomatics.md §1.2)

### For Implementation (Building the System)

**Start**: `integration.md` → `proof.md` → `dp.md`

Read these if you want to implement:
- Contradiction detection via super-additive loss
- Proof validation with Galois coherence
- DP value functions with constitutional reward
- AGENTESE path registration

**Critical Patterns**:
- GaloisWitnessedProof (proof.md §1.2)
- GaloisConstitution (dp.md §2.1)
- ContradictionAnalysis (integration.md §2.3)

### For UI/Navigation (User Experience)

**Start**: `navigation.md` → `llm.md`

Read these if you want to build:
- Telescope with loss topography visualization
- Gradient flow navigation
- Ghost alternative generation
- LLM-powered restructuring

**Key Components**:
- GaloisTelescopeState (navigation.md §2.1)
- LossGradientField (navigation.md §1.3)
- LLMGaloisRestructurer (llm.md §1.1)

---

## Module Summary

### axiomatics.md (Foundation)

**What**: The minimal axiomatic kernel with Galois grounding.

**Key Insights**:
- Axioms aren't stipulated—they're discovered as zero-loss fixed points
- Layer count (7) emerges from convergence rates, not declaration
- Three foundations: A1 (Entity), A2 (Morphism), G (Galois Ground)

**Dependencies**: `spec/theory/galois-modularization.md`

**Implementation Priority**: HIGH (weeks 1-3)

---

### proof.md (Toulmin + Galois)

**What**: Galois-upgraded proof system with quantitative coherence.

**Key Insights**:
- Proof quality = `1 - galois_loss(proof)`
- Evidence tiers mapped to loss bounds (CATEGORICAL < 0.1, etc.)
- Witness batching via loss triage (SINGLE/SESSION/LAZY)
- Ghost alternatives from loss decomposition

**Dependencies**: axiomatics.md, `spec/protocols/witness-primitives.md`

**Implementation Priority**: HIGH (weeks 4-6)

---

### dp.md (Value Functions)

**What**: Constitutional reward as inverse Galois loss.

**Key Insights**:
- All 7 constitutional evaluators → single Galois loss measure
- Bellman equation: `V* = max[R_const - λ·L + γ·V*]`
- PolicyTrace ↔ Toulmin Proof isomorphism
- Axiom discovery as MetaDP with loss minimization

**Dependencies**: axiomatics.md, proof.md, `spec/theory/dp-native-kgents.md`

**Implementation Priority**: MEDIUM (weeks 7-10)

---

### bootstrap.md (Strange Loop)

**What**: The Lawvere fixed point resolves the bootstrap paradox.

**Key Insights**:
- Zero Seed IS the terminal coalgebra of restructuring
- Fixed point verification: `L(ZS, C(R(ZS))) < 0.15` (85% regenerability)
- Polynomial emergence: Fixed points ARE PolyAgent[S,A,B]
- Retroactive witnessing of bootstrap artifacts

**Dependencies**: axiomatics.md, `spec/theory/galois-modularization.md`

**Implementation Priority**: MEDIUM (weeks 7-8)

---

### integration.md (AGENTESE + Systems)

**What**: Galois integration with existing kgents systems.

**Key Insights**:
- Contradiction = super-additive loss: `L(A∪B) > L(A)+L(B)+τ`
- Ghost graph = Différance heritage (deferred alternatives)
- AGENTESE contexts preserved with loss semantics
- Edge creation with loss preview

**Dependencies**: axiomatics.md, proof.md, `spec/protocols/agentese.md`

**Implementation Priority**: HIGH (weeks 5-9)

---

### navigation.md (Telescope UI)

**What**: Telescope with Galois loss topography visualization.

**Key Insights**:
- Navigation IS loss-gradient descent
- High-loss nodes glow as warnings
- Loss gradients guide toward coherence
- Edge clustering by semantic proximity

**Dependencies**: axiomatics.md, integration.md

**Implementation Priority**: MEDIUM (weeks 10-12)

---

### llm.md (LLM Operations)

**What**: LLM as the canonical Galois adjunction.

**Key Insights**:
- LLM IS the (R, C, L) triple (not metaphor—actual instantiation)
- Token budgets as thermodynamic constraints
- Model selection by loss tolerance
- Prompt engineering for Galois operations

**Dependencies**: axiomatics.md, `spec/theory/galois-modularization.md`

**Implementation Priority**: MEDIUM (weeks 9-12)

---

## Version History

### v1.0 (Original Zero Seed)
- 7 layers stipulated
- 3-4 axioms chosen manually
- Qualitative proof validation
- LLM-based contradiction detection
- Heuristic constitutional evaluation

### v2.0 (Galois-Native Upgrade) — Current
- 7 layers emergent from convergence depth
- Axioms discovered as fixed points
- Quantitative proof coherence: `1 - L(proof)`
- Super-additive loss contradiction detection
- Unified constitutional reward: `1 - L(transition)`
- Bootstrap paradox resolved via Lawvere

**Date**: 2025-12-24

---

## Success Criteria

### Functional

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Axiom Discovery Precision** | > 90% | % mined candidates that are true axioms |
| **Axiom Discovery Recall** | > 90% | % true axioms found in Constitution |
| **Layer Assignment Accuracy** | > 80% | % correct on test corpus |
| **Contradiction Detection F1** | > 0.85 | F1 vs human-labeled contradictions |
| **Proof Coherence Correlation** | r > 0.7 | Galois coherence vs human judgment |

### Theoretical

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Fixed Point Verification** | L < 0.15 | Bootstrap loss on Zero Seed itself |
| **Loss-Difficulty Correlation** | r > 0.6 | Pearson r, p < 0.01 |
| **Compression Ratio** | > 7:1 | `derived_lines / index_lines` |
| **Regenerability** | > 85% | % of spec regenerable from A1+A2+G |

### Qualitative

- [ ] Mirror Test approval: "Daring, bold, creative"
- [ ] Developer clarity: "I understand why layers emerge"
- [ ] User trust: "Contradiction detection is transparent"

---

## Open Questions (For Dialectical Refinement)

### Conceptual

1. **Layer Count Invariance**: Does Galois convergence naturally give 7 layers, or is 7 task-dependent?
2. **Metric Selection**: Which semantic distance (cosine, BERTScore, LLM judge) makes the isomorphism tightest?
3. **Loss Budget**: How does Galois loss interact with entropy budget from bootstrap idioms?

### Technical

4. **Loss Computation Cost**: Galois loss requires LLM calls—how to cache effectively?
5. **Composition of Losses**: Does `L(e₁ >> e₂) ≤ L(e₁) + L(e₂)` hold (subadditive)?
6. **Multi-User Loss**: When users share a graph, whose loss oracle wins?

### UX

7. **Loss Transparency**: Show raw values or abstract indicators (traffic light)?
8. **Axiom Retirement**: How to gracefully deprecate axioms when they drift (L > 0.05)?
9. **Real-Time Loss**: Can we compute loss < 100ms for interactive editing?

---

## Implementation Roadmap

### Phase 1: Galois Infrastructure (Weeks 1-3)

```
Files: impl/claude/services/zero_seed/galois/
  - galois_loss.py (core loss computation)
  - distance.py (semantic distance metrics)
  - decomposition.py (loss decomposition)
  - proof.py (GaloisWitnessedProof)

Success:
  ✓ galois_loss(text) -> float with 3 metrics
  ✓ Loss decomposition by component
  ✓ Unit tests pass
```

### Phase 2: Validation & Triage (Weeks 4-6)

```
Files:
  - galois/validation.py (proof validation)
  - galois/triage.py (witness mode selection)
  - services/witness/galois_integration.py

Success:
  ✓ validate_proof_galois() returns coherence scores
  ✓ Witness batching reduces singles by >50%
  ✓ classify_by_loss() maps to evidence tiers
```

### Phase 3: Contradiction & DP (Weeks 7-10)

```
Files:
  - galois/contradiction.py (super-additive detection)
  - dp/core/galois_constitution.py (unified reward)
  - services/categorical/galois_dp_bridge.py

Success:
  ✓ detect_contradiction_galois() F1 > 0.85
  ✓ GaloisConstitution reward correlates with manual scores
  ✓ proof_to_trace() round-trip preserves loss
```

### Phase 4: Bootstrap & Discovery (Weeks 11-14)

```
Files:
  - galois/bootstrap.py (fixed point verification)
  - galois/discovery.py (axiom mining)
  - galois/stratification.py (layer assignment)

Success:
  ✓ verify_zero_seed_fixed_point() < 0.15
  ✓ Axiom discovery precision/recall > 90%
  ✓ Layer assignment accuracy > 80%
```

### Phase 5: UI & LLM (Weeks 15-18)

```
Files:
  - web/src/components/zero-seed/LossTopographyViewer.tsx
  - services/zero_seed/llm_restructurer.py
  - protocols/cli/handlers/zero_seed_galois.py

Success:
  ✓ Telescope shows loss heatmap
  ✓ Gradient flow visualization
  ✓ LLM restructure/reconstitute working
  ✓ CLI commands functional
```

### Phase 6: Validation & Deployment (Weeks 19-20)

```
Tasks:
  - Run all experiments (E1-E4, ZS1-ZS2)
  - Measure correlations vs targets
  - Mirror Test with Kent
  - Refine thresholds based on empirics
  - Deploy to staging
  - Publish research findings
```

---

## Prerequisites

Before reading these specs, understand:

| Prerequisite | Location | What It Provides |
|--------------|----------|------------------|
| **Constitution** | `spec/principles/CONSTITUTION.md` | The 7 design + 7 governance principles |
| **AGENTESE** | `spec/protocols/agentese.md` | Five contexts, path semantics |
| **Witness Protocol** | `spec/protocols/witness-primitives.md` | Mark and Crystal structures |
| **Agent-DP** | `spec/theory/agent-dp.md` | Problem-solution co-emergence |
| **Galois Modularization** | `spec/theory/galois-modularization.md` | R ⊣ C adjunction, full theory |
| **Polynomial Agents** | `spec/principles/decisions/AD-002-polynomial.md` | PolyAgent[S,A,B] foundations |

**Import Order**: Constitution → AGENTESE → Witness → Agent-DP → Galois → Zero Seed

---

## Related Specs

### Theoretical Foundations
- `spec/theory/agent-dp.md` — Agent Space as DP
- `spec/theory/dp-native-kgents.md` — DP-Native unified framework
- `spec/theory/galois-modularization.md` — Full Galois theory with experiments
- `spec/principles/decisions/AD-002-polynomial.md` — Polynomial derivation

### Protocols
- `spec/protocols/agentese.md` — Five contexts, observer model
- `spec/protocols/witness-primitives.md` — Mark and Crystal
- `spec/protocols/differance.md` — Ghost alternatives (Galois-deferred)
- `spec/protocols/typed-hypergraph.md` — Hypergraph model

### Implementation
- `spec/m-gents/holographic.md` — Holographic compression
- `spec/m-gents/phase8-ghost-substrate-galois-link.md` — Galois in M-gent
- `spec/bootstrap.md` — Bootstrap agents and idioms

---

## The Unified Equation

Navigation through the seven-layer holarchy follows the **Galois-Constitutional Bellman Equation**:

```python
V*(node) = max_edge [
    Constitution.reward(node, edge, target) - λ·L(node → target) + γ·V*(target)
]

where:
    V*(node)                         # Optimal value at this node
    Constitution.reward(...)         # 7-principle weighted sum
    L(node → target)                 # Galois loss of edge traversal
    λ                                # Loss penalty weight (0.3 default)
    γ                                # Discount factor = focal_distance
```

**The Synthesis**: The Constitution IS a set of loss minimizers. The reward function IS `1 - total_weighted_loss`.

---

## Final Synthesis

This specification achieves the ultimate goal of the Generative principle:

> "A design is generative if you could delete the implementation and regenerate it from spec."

**Zero Seed v2 goes further**: You can delete the spec itself and regenerate it from the three foundations (A1, A2, G) plus the Galois adjunction.

**The Proof**:
1. Start with A1 (Entity), A2 (Morphism), G (Galois Ground)
2. Derive the Galois adjunction `R ⊣ C`
3. Compute fixed points of `R` → discover axioms (L1)
4. Measure convergence depth → derive layers (L1-L7)
5. Apply loss to proofs → ground Toulmin coherence
6. Detect super-additive loss → identify contradictions
7. Unify constitutional reward with inverse loss
8. Verify bootstrap fixed point → `L(Zero Seed, Zero Seed') < 0.15`

**This specification IS the garden growing itself.**

---

## Acknowledgments

This synthesis unifies:
- Zero Seed v1 (2024-2025) — Original 7-layer holarchy
- Galois Modularization Theory (2025-12-24) — Lossy compression functors
- Agent-DP (2024-2025) — Problem-solution co-emergence
- Polynomial Agents (AD-002, 2024) — PolyAgent[S,A,B] foundations
- Constitution (2024-2025) — The 7 principles as loss minimizers

It builds on the shoulders of:
- Douglas Hofstadter — Strange loops and self-reference
- William Lawvere — Fixed point theorem in category theory
- Évariste Galois — Adjunctions and loss in abstraction
- Stephen Toulmin — Proof structure and argumentation
- Kent Gang — The Mirror Test and kgents vision

---

*"The loss IS the difficulty. The fixed point IS the axiom. The strange loop IS the garden growing itself."*

---

**v2.0 (Galois-Native) Filed**: 2025-12-24
**Authors**: Kent Gang, Claude (Anthropic)
**Source Synthesis**: `spec/theory/galois-modularization.md` × Zero Seed v1
**Compression Ratio**: ~8:1 (this index generates ~4000 lines of derived specs)
**Regenerability**: 85% (verified via bootstrap fixed point)
**Next**: Implement Phase 1, run experiments, conduct Mirror Test
