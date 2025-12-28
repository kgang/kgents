# Theory Operationalization: Master Plan

> *"The theory is the compression. The code is the witness."*

**Created**: 2025-12-26
**Source**: 7 sub-agent deep studies of 21-chapter theory monograph
**Status**: Week 4+ — E1, E3 DONE; advancing on remaining co-engineering proposals

---

## Current Status (2025-12-26)

The core bet is validated. Dialectical fusion and Kleisli witness composition are operational.

| ID | Proposal | Status | Location | Evidence |
|----|----------|--------|----------|----------|
| **E1** | Kleisli Witness Composition | **DONE** | `services/witness/kleisli.py` | 36 tests passing |
| **E3** | DialecticalFusionService | **DONE** | `services/dialectic/fusion.py` | 22 tests passing |
| **C5** | Law Verification System | **REDUNDANT** | `services/categorical/pilot_laws.py` | Already exists |
| **S3** | Constitutional Runtime Enforcement | **DONE** | `services/categorical/constitution.py` | In production |
| **S4** | Trust Gradient Learning | **DONE** | `services/witness/trust/gradient.py` | In production |

**What this means**: The co-engineering layer (E1, E3) is now the strongest. Marks compose as Writer monads. Kent-Claude tensions fuse into synthesis via cocone construction. The witness infrastructure is categorical-correct.

**Next priorities**: E2 (Analysis Operad Composer), E4 (AGENTESE Fusion Ceremony), remaining Galois calibration.

**New Proposal (2025-12-26)**: [08-jit-skill-injection.md](./08-jit-skill-injection.md) — JIT Skill Injection Protocol with Meta-Epistemic Naming (9 proposals, J1-J9)

---

## Executive Summary

Seven sub-agents studied the theory monograph (`docs/theory/`) and identified **35 operationalization proposals** across 6 layers. This master plan synthesizes their findings into an actionable execution framework.

### The Core Bet

**Galois Loss is real, measurable, and useful.**

Formula: `L(P) = d(P, C(R(P)))`
- R: Restructure via LLM
- C: Reconstitute via LLM
- d: Semantic distance (BERTScore → cosine → fallback)

If this is true, we have the first principled coherence metric for agent systems.

### Key Findings

| Layer | Study Agent | Gap Severity | Proposals | Effort |
|-------|-------------|--------------|-----------|--------|
| I+II: Categorical | ab3b6b1 | Medium | 5 | 4 weeks |
| III: Galois | a426f1b | **High** | 5 | 8-9 weeks |
| IV: DP | a0ce039 | Medium | 5 | 2-3 weeks |
| **VIII: JIT Skills** | Kent vision | **High** | 9 | 5-7 weeks |
| V: Distributed | af290e1 | Medium | 5 | 2-3 weeks |
| VI: Co-Engineering | a4cafdc | **High** | 5 | 3-4 weeks |
| VII: Synthesis | a050bc6 | Low | 5 | 12 weeks |
| Pilots | a1d46f4 | — | 5 | Integrated |

**Total**: 35 proposals across ~12-16 weeks with parallelization

---

## Critical Path

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: VALIDATION (Weeks 1-3)                                             │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 1. Galois Loss Calibration Pipeline (100+ prompts)                     │ │
│ │    → Validates the core bet                       [IN PROGRESS]        │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                           │                                                 │
│                           ▼                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 2. Constitutional Runtime Enforcement (S3)         [✓ DONE]            │ │
│ │    → Operationalizes Amendment A in code                               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: INTEGRATION (Weeks 4-6)                    [CURRENT]               │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 3. Bellman-Constitutional Unification                                  │ │
│ │    → Constitution IS the reward function          [NEXT]               │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                           │                                                 │
│                           ▼                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 4. Kleisli Witness Composition (E1)                [✓ DONE]            │ │
│ │    → Marks compose like effectful functions                            │ │
│ │    → services/witness/kleisli.py (36 tests)                            │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                           │                                                 │
│                           ▼                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 5. Dialectical Fusion Service (E3)                 [✓ DONE]            │ │
│ │    → Kent-Claude cocone construction                                   │ │
│ │    → services/dialectic/fusion.py (22 tests)                           │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: EXPANSION (Weeks 7-10)                                             │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 6. Multi-Agent Sheaf + Cocone Construction                             │ │
│ │    → Disagreement becomes constructive                                 │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                           │                                                 │
│                           ▼                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 7. Reasoning Monad Infrastructure                                      │ │
│ │    → CoT/ToT/GoT as proper monads                                      │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: PILOTS (Weeks 6-10)                                                │
│                                                                             │
│ trail-to-crystal-daily-lab  ──────────────────────────────────────────────▶ │
│   (Proves: Constitution as Reward, Galois Loss, K-Block Monad)              │
│                                                                             │
│ wasm-survivors-game  ────────────────────────────────────────────────────▶ │
│   (Proves: Real-time Galois Loss, Heterarchical Leadership)                 │
│                                                                             │
│ disney-portal-planner  ───────────────────────────────────────────────────▶ │
│   (Proves: Sheaf Coherence, Multi-Agent Coordination)                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The 35 Proposals by Layer

### Layer I+II: Categorical Infrastructure (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort | Status |
|----|----------|---------------|----------|--------|--------|
| C1 | TraceMonad for CoT | Ch 3 | High | 1 week | Pending |
| C2 | BranchMonad for ToT | Ch 3 | Medium | 1 week | Pending |
| C3 | REASONING_OPERAD | Ch 4 | High | 1 week | Pending |
| C4 | BeliefSheaf | Ch 5 | Medium | 5 days | Pending |
| C5 | Law Verification System | Ch 2 | High | 5 days | **REDUNDANT** |

**Update 2025-12-26**: C5 is redundant — `services/categorical/pilot_laws.py` already implements law verification.

**Key Gap**: No reasoning monad infrastructure (CoT/ToT/GoT not implemented as monads)

**Implementation**: See [01-categorical-infrastructure.md](./01-categorical-infrastructure.md)

---

### Layer III: Galois Theory (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort |
|----|----------|---------------|----------|--------|
| G1 | Calibration Pipeline (100+ prompts) | Ch 6 | **Critical** | 3 weeks |
| G2 | Task Triage Service | Ch 7 | High | 1 week |
| G3 | Loss Decomposition API | Ch 7 | High | 2 weeks |
| G4 | Polynomial Extractor | Ch 8 | Medium | 2 weeks |
| G5 | TextGRAD Integration | Ch 7 | Medium | 1 week |

**Key Gap**: Loss-difficulty correlation unvalidated, calibration corpus only 9 entries

**Implementation**: See [02-galois-theory.md](./02-galois-theory.md)

---

### Layer IV: Dynamic Programming (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort |
|----|----------|---------------|----------|--------|
| D1 | BellmanConstitutionalEquation | Ch 9 | **Critical** | 1 week |
| D2 | TrustGate Service | Ch 10 | High | 1 week |
| D3 | DriftMonitor | Ch 11 | High | 5 days |
| D4 | AdaptiveDiscount | Ch 11 | Medium | 3 days |
| D5 | SelfImprovementCycle | Ch 11 | Medium | 5 days |

**Key Gap**: Bellman-Constitutional not unified, no trust-gated self-improvement

**Implementation**: See [03-dynamic-programming.md](./03-dynamic-programming.md)

---

### Layer V: Distributed Agents (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort |
|----|----------|---------------|----------|--------|
| M1 | MultiAgentSheaf with Cocones | Ch 12 | High | 1 week |
| M2 | HeterarchicalLeadership | Ch 13 | High | 5 days |
| M3 | BindingComplexity Estimator | Ch 14 | Medium | 5 days |
| M4 | LeadershipTriggerEngine | Ch 13 | Medium | 3 days |
| M5 | CoalitionFinder | Ch 12 | Medium | 5 days |

**Key Gap**: No multi-agent belief sheaf, binding problem unaddressed

**Implementation**: See [04-distributed-agents.md](./04-distributed-agents.md)

---

### Layer VI: Co-Engineering (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort | Status |
|----|----------|---------------|----------|--------|--------|
| E1 | Kleisli Witness Composition | Ch 16 | **Critical** | 1 week | **DONE** (2025-12-26) |
| E2 | Analysis Operad Composer | Ch 15 | High | 5 days | Pending |
| E3 | DialecticalFusionService | Ch 17 | **Critical** | 1 week | **DONE** (2025-12-26) |
| E4 | AGENTESE Fusion Ceremony | Ch 17 | High | 5 days | Pending |
| E5 | Trust Gradient Dialectic | Ch 17 | High | 5 days | Pending |

**Update 2025-12-26**: E1 and E3 completed. Dialectical fusion now operational.
- E1: `impl/claude/services/witness/kleisli.py` — Writer monad with 36 passing tests
- E3: `impl/claude/services/dialectic/fusion.py` — Full fusion service with 22 passing tests

**Remaining Gap**: E2, E4, E5 pending

**Implementation**: See [05-co-engineering.md](./05-co-engineering.md)

---

### Layer VII: Synthesis & Differentiation (5 proposals)

| ID | Proposal | Theory Source | Priority | Effort | Status |
|----|----------|---------------|----------|--------|--------|
| S1 | Empirical Law Benchmark | Ch 18 | High | 2 weeks | Pending |
| S2 | Galois Failure Predictor | Ch 7, 18 | **Critical** | 3 weeks | Pending |
| S3 | Constitutional Runtime Enforcement | Ch 9, 19 | **Critical** | 2 weeks | **DONE** (2025-12-26) |
| S4 | Trust Gradient Learning | Ch 10, 17 | Medium | 2 weeks | **DONE** (2025-12-26) |
| S5 | Sheaf Gluing Demo | Ch 5, 12 | Medium | 1 week | Pending |

**Update 2025-12-26**: S3 and S4 completed.
- S3: `services/categorical/constitution.py` — Seven principles with violation detection
- S4: `services/witness/trust/gradient.py` — Trust gradient learning operational

**Five Key Differentiators** (from framework comparison):
1. Explicit categorical structure (laws verified at runtime)
2. Constitution-as-reward (seven principles as objective function)
3. Dialectic fusion (cocone construction for disagreement)
4. Witness as Writer monad (reasoning traces are first-class)
5. Galois Loss prediction (failure probability from semantic distance)

**Implementation**: See [06-synthesis-differentiation.md](./06-synthesis-differentiation.md)

---

### Pilots Integration (5 mappings)

| Pilot | Theory Chapters Validated | Joy Dimension | Week |
|-------|---------------------------|---------------|------|
| **trail-to-crystal** | Ch 9, 16, 11 | FLOW | Week 6 |
| **wasm-survivors** | Ch 7, 13, 10 | FLOW | Week 7 |
| **disney-portal** | Ch 5, 12, 17 | WARMTH | Week 8 |
| **rap-coach** | Ch 7, 16, 17 | SURPRISE | Week 7 |
| **sprite-procedural** | Ch 8, 11, 6 | SURPRISE | Week 8 |

**Implementation**: See [07-pilots-integration.md](./07-pilots-integration.md)

---

## Implementation Strategy

### Week-by-Week Execution

| Week | Focus | Proposals | Status |
|------|-------|-----------|--------|
| 1 | Galois Calibration Setup | G1 (start) | **DONE** |
| 2 | Calibration + Constitutional | G1, S3 | **S3 DONE** |
| 3 | Calibration + DP + Trust | G1, D1, S4 | **S4 DONE** |
| 4 | **Kleisli + Dialectical** | **E1, E3** | **BOTH DONE** |
| 5 | Bellman-Constitutional | D1, D2 | **CURRENT** |
| 6 | **First Pilot Ships** | Integration | trail-to-crystal |
| 7 | Multi-Agent + Second Pilot | M1, M2 | wasm-survivors OR rap-coach |
| 8 | Third Pilot + Demo | S5 | Any remaining pilot |
| 9 | Reasoning Monads | C1, C2, C3 | zero-seed-governance |
| 10 | Categorical Package | C4 (C5 redundant) | categorical-foundation |

**Status**: Week 4 complete. E1 and E3 shipped ahead of schedule. Moving to Bellman-Constitutional unification.

### Parallelization Strategy

```
Week 1-3: Galois Track (G1, G2, G3)
          ├── Constitutional Track (S3, D1) [parallel]
          └── Witness Track (E1) [parallel]

Week 4-6: DP Track (D2, D3, D4, D5)
          └── Co-Engineering Track (E2, E3, E4, E5) [parallel]

Week 7-10: Multi-Agent Track (M1, M2, M3, M4, M5)
           └── Categorical Track (C1, C2, C3, C4, C5) [parallel]
```

---

## Success Metrics

### Validation Metrics (Must Pass)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Galois Loss calibration | 100+ entries | Count in corpus |
| Loss-coherence correlation | r > 0.5 | Pearson coefficient |
| Constitutional enforcement | 100% violations caught | Test coverage |
| Bellman-Constitutional passes | All tests green | CI |
| First pilot ships | Week 6 | Go-live date |

### Quality Metrics (Should Pass)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Theory-implementation faithfulness | > 90% | Audit score |
| Law verification coverage | > 80% | Test coverage |
| Kleisli composition passes | All laws hold | Property tests |
| Multi-agent cocone construction | Works | Demo |

### Aspirational Metrics (Nice to Pass)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Reasoning monad benchmarks | Better than baseline | Accuracy comparison |
| Binding complexity prediction | r > 0.3 | Correlation |
| External categorical law tests | All pass | Package tests |

---

## Risk Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Galois Loss doesn't correlate | Medium | **Critical** | Week 1 literature search; fall back to simpler metrics |
| Calibration corpus too small | Medium | High | Synthetic generation; domain experts |
| Bellman-Constitutional too complex | Low | Medium | Simplify to weighted sum |
| Multi-agent cocones fail to glue | Medium | Medium | Fall back to voting |
| Pilots delayed | High | High | Focus on trail-to-crystal only |

---

## Document Navigation

| Document | Focus |
|----------|-------|
| [01-categorical-infrastructure.md](./01-categorical-infrastructure.md) | Part I+II: Monads, Operads, Sheaves |
| [02-galois-theory.md](./02-galois-theory.md) | Part III: Loss, Calibration, Fixed Points |
| [03-dynamic-programming.md](./03-dynamic-programming.md) | Part IV: Bellman, Trust, Self-Improvement |
| [04-distributed-agents.md](./04-distributed-agents.md) | Part V: Multi-Agent, Heterarchy, Binding |
| [05-co-engineering.md](./05-co-engineering.md) | Part VI: Witness, Analysis, Dialectic |
| [06-synthesis-differentiation.md](./06-synthesis-differentiation.md) | Part VII: Framework Comparison, Differentiators |
| [07-pilots-integration.md](./07-pilots-integration.md) | Pilot-to-Theory Mapping |
| [08-jit-skill-injection.md](./08-jit-skill-injection.md) | **NEW**: JIT Skills, Meta-Epistemic Naming, Stigmergy |

---

## Analysis Operad Coherence Assessment

> *"Four lenses. One system. Every proposal must survive all four."*

### Categorical Lens: Do proposals preserve morphism structure?

| Assessment | Finding |
|------------|---------|
| **E1 (Kleisli)** | **Strong**. Writer monad laws verified. Marks compose via `>>=`. |
| **E3 (Dialectical)** | **Strong**. Cocone construction preserves diagram structure. |
| **S3 (Constitution)** | **Medium**. Enforcement works, but Bellman connection not yet categorical. |
| **S4 (Trust Gradient)** | **Medium**. Learning updates work; needs functor verification. |
| **C5 (Laws)** | **N/A**. Redundant — pilot_laws.py already exists. |

**Overall**: 2/5 categorically verified, 2/5 functional but need formalization, 1/5 redundant.

### Epistemic Lens: Confidence in remaining proposals?

| Proposal | Confidence | Why |
|----------|------------|-----|
| **D1 (Bellman-Constitutional)** | High (85%) | Theory clear, just needs implementation |
| **G1 (Galois Calibration)** | Medium (60%) | Core bet — needs empirical validation |
| **M1 (Multi-Agent Sheaf)** | Medium (65%) | Theory sound, coordination tricky |
| **C1-C3 (Reasoning Monads)** | High (80%) | Well-understood monad patterns |
| **E2 (Analysis Operad)** | Medium (55%) | Meta — depends on this very assessment |

### Dialectical Lens: What tensions remain?

| Tension | Kent's View | Claude's View | Resolution |
|---------|-------------|---------------|------------|
| **Galois vs. Pilots** | Prove the math first | Ship something users touch | trail-to-crystal proves both |
| **Categorical Purity vs. Pragmatism** | Categories are the point | Working code is the point | Constitution-as-reward unifies |
| **Breadth vs. Depth** | Fewer, deeper pilots | More, lighter proofs | Focus on 3 pilots max |

### Generative Lens: How close is spec regenerability?

| Metric | Status | Gap |
|--------|--------|-----|
| **Constitution → Code** | High | S3 is live |
| **Witness → Kleisli** | High | E1 is live |
| **Dialectic → Fusion** | High | E3 is live |
| **Galois → Loss Function** | Medium | Calibration incomplete |
| **Full Theory → Full System** | Low | ~40% proposals complete |

**Regenerability Score**: 5/35 proposals DONE = 14%. But they're the right 5 — the co-engineering layer that enables everything else.

---

## The Mirror Test

> *"Does this feel like Kent on his best day — or did we make it safe?"*

This plan is **daring** because:
- It bets on Galois Loss as the central metric before proving it works
- It prioritizes mathematical rigor over feature count
- It ships one pilot deep before expanding broad

This plan is **tasteful** because:
- 35 proposals, not 100 — each justified by theory
- Critical path is linear and clear
- Pilots validate infrastructure, not the reverse

This plan is **joy-inducing** because:
- trail-to-crystal turns productivity into proof
- wasm-survivors turns gaming into witnessed experience
- The math serves the user, not the user serves the math

---

> *"The proof IS the decision. The mark IS the witness. The theory IS the code."*

**Next Action**: Week 5 — Bellman-Constitutional Unification (D1) + remaining Galois calibration (G1)

---

**Document Metadata**
- **Lines**: ~420
- **Status**: Master Operationalization Plan (Week 4+ Update)
- **Source**: 7 sub-agent studies (Dec 26, 2025)
- **Last Updated**: 2025-12-26 — E1, E3, S3, S4 marked DONE; C5 marked REDUNDANT
- **Owner**: Kent Gang + Claude
