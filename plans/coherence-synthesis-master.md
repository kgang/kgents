# Coherence Synthesis Master Plan

> *"The seed IS the garden. The proof IS the decision. The mark IS the witness."*

**Status**: ✅ IMPLEMENTED (Core Integration, 2025-01-10)
**Date**: 2025-01-10
**Scope**: Zero Seed, Constitutional Decision OS, ASHC, Formal Verification
**Goal**: Unified coherence across all theoretical systems, supporting arbitrary intellectual endeavors

---

## Executive Summary

This plan synthesizes the deep audit of kgents' theoretical foundations into actionable integration work. The individual components are sound; the connections between them need strengthening.

### The Coherence Vision

```
                    ┌─────────────────────────────────────┐
                    │         CONSTITUTION                │
                    │   (7 Principles + 7 Articles)       │
                    │   [constitutional commitments]      │
                    └──────────────┬──────────────────────┘
                                   │ enforced by
                    ┌──────────────▼──────────────────────┐
                    │         ZERO SEED                   │
                    │   Galois Stratification (L layers)  │
                    └──────────────┬──────────────────────┘
                                   │ instantiates
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
│   PILOT LAWS      │   │     ASHC          │   │ FORMAL VERIFY     │
│ (5 Schemas)       │   │ (Evidence Engine) │   │ (25 Properties)   │
└─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
          │                       │                       │
          │         witnesses     │   compiles            │   verifies
          │                       │                       │
┌─────────▼─────────────────────────────────────────────────────────┐
│                    MARK SYSTEM                                     │
│   ConstitutionalEvaluator + MarkStore + WitnessProtocol           │
└─────────┬─────────────────────────────────────────────────────────┘
          │ grounds
┌─────────▼─────────────────────────────────────────────────────────┐
│                    PILOTS (Arbitrary Endeavors)                    │
│   WASM Survivors │ Trail-to-Crystal │ Rap Coach │ Any New Pilot   │
└───────────────────────────────────────────────────────────────────┘
```

### The Unifying Design Axiom

All systems converge on:

```
R_constitutional = 1 - L_galois

where:
  R_constitutional = Constitutional reward (ETHICAL gate + 6-principle weighted sum)
  L_galois = Semantic preservation loss under restructuring
```

**Note**: This is a **design axiom**, not a mathematical theorem. It holds by construction when:
- Both R and L are normalized to [0, 1]
- R measures "goodness" (constitutional compliance)
- L measures "badness" (structure loss under R∘C)
- They are defined as complements

**Empirical Validation**: Kent calibration (2025-12-28) shows ρ = 0.8346 (Spearman) correlation.

**Important**: ETHICAL is a **GATE** (≥0.6 floor), not part of the weighted sum. See Amendment A.

---

## Part I: Current State Assessment

### What Works Well

| System | Status | Strength |
|--------|--------|----------|
| **Zero Seed v3.0** | Canonical | Galois stratification is mathematically sound |
| **Pilot Laws** | Implemented | 5 schemas, 24 laws across 5 pilots |
| **Constitutional Evaluator** | Active | 7-principle scoring with weights |
| **ASHC** | 276 tests | Correct insight: evidence over generation |
| **Formal Verification** | Specified | 25 properties, HoTT foundation |
| **WASM Survivors** | Validated | Full stack working in practice |

### What Needs Integration

| Gap | Systems Involved | Impact | Plan Reference |
|-----|------------------|--------|----------------|
| **Galois ↔ Constitutional** | Zero Seed, Constitutional OS | Evaluator doesn't use L | `constitutional-os-revival.md` |
| **Galois ↔ Evidence** | Zero Seed, ASHC | equivalence_score ignores L | `ashc-galois-integration.md` |
| **Schema ↔ Principles** | Pilot Laws, Constitution | No explicit mapping | `pilot-bootstrap-protocol.md` |
| **HoTT ↔ Implementation** | Formal Verification | Bridge is theoretical | `formal-verification-bridge.md` |
| **Bootstrap Protocol** | All | No guide for new pilots | `pilot-bootstrap-protocol.md` |

---

## Part II: Integration Priorities

### P0: Critical Path (Week 1)

These blocks prevent other work:

1. **Galois Loss Computation Service**
   - Central service all systems can call
   - Input: any content (mark, spec, proof)
   - Output: L ∈ [0, 1]
   - See: `zero-seed-integration.md`

2. **Constitutional Evaluator Galois Integration**
   - Currently `galois_loss=None` always
   - Must compute and attach to every alignment
   - See: `constitutional-os-revival.md`

### P1: High Value (Week 2)

These unlock significant capability:

3. **ASHC Evidence ↔ Galois**
   - `equivalence_score()` should use `1 - L`
   - Validates spec-impl equivalence properly
   - See: `ashc-galois-integration.md`

4. **Zero Seed Bootstrap Verification**
   - `verify_zero_seed_fixed_point()` implementation
   - Self-hosting proof: Zero Seed regenerates from itself
   - See: `zero-seed-integration.md`

### P2: Enabling (Week 3)

These enable arbitrary pilots:

5. **Pilot Bootstrap Protocol**
   - Step-by-step guide for new domains
   - From axiom discovery to law derivation
   - See: `pilot-bootstrap-protocol.md`

6. **Schema ↔ Principle Mapping**
   - COHERENCE_GATE → COMPOSABLE
   - DRIFT_ALERT → GENERATIVE
   - etc.
   - See: `pilot-bootstrap-protocol.md`

### P3: Advanced (Week 4+)

These complete the vision:

7. **ASHC Chaos Testing (Phase 3)**
   - Combinatorial composition testing
   - Sample O(N!) space probabilistically
   - See: `ashc-galois-integration.md`

8. **HoTT Bridge**
   - Export operad laws to Lean
   - Import verification results
   - See: `formal-verification-bridge.md`

---

## Part III: Success Criteria

### Coherence Tests

| Test | Description | Target |
|------|-------------|--------|
| **Zero Seed Regeneration** | `L(ZS, regenerate(ZS)) < 0.15` | 85% regenerability |
| **Constitutional Consistency** | `eval(mark).galois_loss` is never None | 100% coverage |
| **ASHC Evidence** | `evidence.equivalence_score() ≈ 1 - L` | ρ > 0.95 correlation |
| **Pilot Law Derivation** | All 24 laws trace to constitutional principles | 100% documented |
| **Arbitrary Pilot Bootstrap** | New pilot can be created using protocol | < 1 day to first laws |

### Integration Metrics

```python
@dataclass
class CoherenceMetrics:
    """Track coherence across all systems."""

    # Zero Seed
    zero_seed_regenerability: float  # Target: > 0.85
    layer_assignment_consistency: float  # Target: 1.0

    # Constitutional
    galois_coverage: float  # % of marks with galois_loss computed
    principle_correlation: float  # correlation between L and weighted score

    # ASHC
    evidence_galois_correlation: float  # correlation with equivalence_score
    self_hosting_verified: bool  # Can ASHC compile Zero Seed?

    # Pilot Laws
    schema_principle_mapping_coverage: float  # % of laws mapped
    new_pilot_bootstrap_time_hours: float  # Time to first working laws

    @property
    def overall_coherence(self) -> float:
        """Weighted coherence score."""
        return (
            self.zero_seed_regenerability * 0.25 +
            self.galois_coverage * 0.25 +
            self.evidence_galois_correlation * 0.25 +
            self.schema_principle_mapping_coverage * 0.25
        )
```

---

## Part IV: Work Breakdown

### Week 1: Foundation

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1 | Galois loss computation service | - | `services/galois/loss.py` |
| 2 | Constitutional evaluator integration | - | Updated `constitutional_evaluator.py` |
| 3 | Unit tests for galois computation | - | `_tests/test_galois_integration.py` |
| 4 | Zero Seed bootstrap verification | - | `verify_zero_seed_fixed_point()` impl |
| 5 | Integration testing | - | All P0 criteria green |

### Week 2: Evidence

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1-2 | ASHC equivalence_score Galois | - | Updated `evidence.py` |
| 3 | ASHC self-hosting test | - | `test_ashc_compiles_zero_seed()` |
| 4 | Evidence ↔ Constitutional bridge | - | Traces create marks with alignment |
| 5 | Integration testing | - | All P1 criteria green |

### Week 3: Pilots

| Day | Task | Owner | Deliverable |
|-----|------|-------|-------------|
| 1-2 | Schema ↔ Principle mapping | - | Documented in `pilot_laws.py` |
| 3-4 | Pilot Bootstrap Protocol doc | - | `pilot-bootstrap-protocol.md` |
| 5 | Test protocol with new pilot | - | "Academic Paper Lab" prototype |

### Week 4+: Advanced

| Task | Deliverable |
|------|-------------|
| ASHC Chaos Testing | `chaos.py`, `causal.py` |
| HoTT Bridge | `lean_export.py`, verification results |
| Full system integration | All metrics at target |

---

## Part V: Risk Management

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Galois computation too slow | Medium | High | Cache aggressively, batch calls |
| Kent calibration drift | Low | Medium | Re-calibrate quarterly |
| ASHC chaos explosion | Medium | Medium | Sampling with budget limits |
| HoTT complexity | High | Low | Defer, not blocking |

### Process Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | High | Medium | Strict P0/P1/P2/P3 ordering |
| Integration debt | Medium | High | Test each connection explicitly |
| Documentation lag | Medium | Medium | Write docs with code |

---

## Part VI: Related Plans

| Plan | Focus | Status |
|------|-------|--------|
| `zero-seed-integration.md` | Galois service, bootstrap verification | New |
| `constitutional-os-revival.md` | Evaluator integration, trust computation | New |
| `ashc-galois-integration.md` | Evidence scoring, chaos testing | New |
| `pilot-bootstrap-protocol.md` | New pilot creation guide | New |
| `formal-verification-bridge.md` | HoTT bridge, Lean export | New |

---

## Appendix: The Coherence Equation Derivation

### Why R = 1 - L?

**Design Axiom**: Constitutional reward and Galois loss are defined as complements.

**Rationale**:
1. Constitutional principles encode semantic coherence invariants
2. Galois loss measures information lost under restructuring
3. If action preserves principle semantics, restructuring preserves structure
4. Therefore: high constitutional reward ⟺ low Galois loss
5. Normalize to [0,1]: R = 1 - L

**Note**: This is a **design axiom** (sensible normalization convention), not a mathematical theorem.
The relationship holds by construction and is validated empirically (Kent calibration ρ = 0.8346).

**Principle-wise mapping**:

| Principle | What Low Galois Loss Implies |
|-----------|------------------------------|
| **TASTEFUL** | Transition preserves clarity (low bloat) |
| **COMPOSABLE** | Edge structure remains explicit |
| **GENERATIVE** | Derivation chain is recoverable |
| **ETHICAL** | Safety constraints remain visible |
| **JOY_INDUCING** | Personality signature is intact |
| **HETERARCHICAL** | No rigid hierarchy imposed |
| **CURATED** | Justification for change is explicit |

---

---

## Appendix B: Terminology Glossary

> *"Be precise about what is mathematical and what is metaphorical."*

| Term | kgents Meaning | Mathematical Source | Relation |
|------|---------------|---------------------|----------|
| **Galois loss** | Semantic preservation loss: L(P) = d(P, C(R(P))) | Galois connections in abstract interpretation | Inspired by, not direct application |
| **R = 1 - L** | Design axiom: reward and loss are complements | Loss/reward duality in optimization | Standard normalization convention |
| **HoTT types** | Python classes modeling paths and isomorphisms | Homotopy Type Theory | Conceptual model, not formal proof |
| **Categorical** | Satisfying composition laws (Identity + Associativity) | Category theory | Direct application |
| **Sheaf** | Local → global consistency via gluing | Sheaf theory | Conceptual model |
| **Fixed point** | L(P) < ε under regeneration: P ≈ C(R(P)) | Lawvere/Knaster-Tarski | Sound application |
| **ETHICAL gate** | Hard constraint (pass/fail), not weighted score | Lexicographic preferences | Sound application |

### Why "Galois"?

The term "Galois loss" is **metaphorically inspired** by Galois connections:
- True Galois connections: adjoint functors between posets
- Our usage: round-trip transformation loss under R (restructure) and C (reconstitute)

Alternative names considered: "semantic preservation loss", "regenerability loss", "structure loss"

We keep "Galois" because:
1. It honors the inspiration from abstract interpretation
2. It connects to the broader vision of Galois stratification
3. It's evocative and memorable (Joy-inducing!)

**Honest caveat**: This is not a direct application of Galois theory.

---

## Appendix C: Trust Level Unification

> *"One trust system to rule them all."*

### The Resolution

Two intentionally distinct trust systems exist:

| System | Location | Purpose |
|--------|----------|---------|
| **Tool Trust** | `chat/trust.py` | Per-tool approval workflow: NEVER/ASK/TRUSTED |
| **Agent Trust (L0-L3)** | `witness/trust/constitutional_trust.py` | Constitutional autonomy tiers |

**`constitutional_trust.TrustLevel` (L0-L3) is authoritative for agent autonomy.**

Rationale:
- Computes level from constitutional alignment history (marks → crystals → trust)
- Aligns with Article V: "Trust is earned through demonstrated alignment"
- Has the most complete implementation (348 lines, including escalation criteria)

**Note**: The gradient.py 5-level system (LEVEL_1-5) is deprecated in favor of 4-level L0-L3.

### Unified Trust Levels

| Level | Name | Constitutional Criteria | Autonomy |
|-------|------|------------------------|----------|
| 0 | READ_ONLY | No history | Full oversight required |
| 1 | BOUNDED | avg_alignment ≥ 0.6, violation_rate < 0.1 | Write to .kgents/ only |
| 2 | SUGGESTION | avg_alignment ≥ 0.8, violation_rate < 0.05, trust_capital ≥ 0.5 | Propose changes |
| 3 | AUTONOMOUS | avg_alignment ≥ 0.9, violation_rate < 0.01, trust_capital ≥ 1.0 | Full agency |

---

*"Axioms are fixed points. Proofs are coherence. Layers are emergence. This plan IS the integration."*
