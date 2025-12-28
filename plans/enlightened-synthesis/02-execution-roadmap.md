# Execution Roadmap: 10-Week Pilot-Grounded Plan

> *"Depth over breadth. Ship fast, ship right, ship something that lasts."*
>
> *"Every week validates infrastructure THROUGH a pilot, not in isolation."*

**Created**: 2025-12-25
**Revised**: 2025-12-26 (7-Pilot Expanded Edition)
**Status**: Ready for Execution
**Purpose**: Week-by-week implementation plan grounded in 7 pilots across 3 tiers

---

## The Core Bet (Unchanged)

**Bet**: Galois Loss is real, measurable, and useful.

**Validation**: Steel Thread via pilots, first pilot ships Week 6.

**Upside**: First principled coherence metric validated through real products.

**Downside**: If it doesn't work, we've built real products and learned something fundamental.

---

## The 7-Pilot System

### Pilot Tiers

| Tier | Purpose | Pilots |
|------|---------|--------|
| **Core** | Validate fundamental infrastructure | trail-to-crystal, zero-seed-governance |
| **Domain** | Prove domain applicability | wasm-survivors, rap-coach, sprite-lab, disney-portal |
| **Meta** | Package for external use | categorical-foundation |

### Pilot Validation Matrix

| Pilot | Tier | Core Primitive | Amendment Validated | Mathematical Grounding |
|-------|------|----------------|---------------------|------------------------|
| trail-to-crystal | Core | Mark/Trace/Crystal | A (ETHICAL floor) | L < 0.1 for daily coherence |
| zero-seed-governance | Core | Axiom/Constitution | B (Canonical distance) | L < 0.05 fixed points |
| wasm-survivors | Domain | Galois Loss | B (Canonical distance) | Real-time drift detection |
| rap-coach | Domain | Trail, Galois | A, B | Intent/delivery alignment |
| sprite-lab | Domain | Crystal | C (Value Agents) | Style attractor stability |
| disney-portal | Domain | ValueCompass | A (ETHICAL floor) | Constitutional tradeoffs |
| categorical-foundation | Meta | PolyAgent/Operad/Sheaf | All | Law-preserving morphisms |

---

## Implementation Faithfulness Gates

Based on audit findings, these gates MUST be passed before pilot completion:

| Component | Current | Required | Gate Week |
|-----------|---------|----------|-----------|
| K-Block Implementation | 80% | 90%+ | Week 4 |
| Galois Distance | 85% | 95%+ | Week 6 |
| Value Agents | 85% | 95%+ | Week 8 |

**Gate Enforcement**:
- Each gate week includes explicit validation tasks
- Pilot cannot ship if gate not passed
- Missing implementation must be completed before proceeding

---

## Mathematical Validation Milestones

| Week | Milestone | Validation Method |
|------|-----------|-------------------|
| Week 4 | Galois loss produces meaningful values | Run on trail-to-crystal outputs, verify L correlates with coherence |
| Week 6 | Axiom discovery works | Verify zero-seed outputs produce L < 0.05 fixed points |
| Week 8 | Categorical laws hold | Validate PolyAgent/Operad laws in isolated package tests |
| Week 10 | External validation | Open-source package passes external categorical law tests |

---

## Pilot-Grounded Critical Path (10-WEEK)

```
Week 1: Core Pipeline (trail-to-crystal primitives)
    |
    +---> Week 2: Galois Integration (wasm-survivors drift detection)
            |
            +---> Week 3: ValueCompass (disney-portal constitutional scoring)
                    |
                    +---> Week 4: Trail Primitive (rap-coach session navigation)
                            |                     [GATE: K-Block 90%+]
                            |
                            +---> Week 5: Crystal Compression (sprite-lab style crystals)
                                    |
                                    +---> Week 6: FIRST PILOT (trail-to-crystal-daily-lab)
                                            |     [GATE: Galois 95%+]
                                            |     [MILESTONE: Galois loss validation]
                                            |
                                            +---> Week 7: Second Pilot (wasm-survivors OR rap-coach)
                                            |
                                            +---> Week 8: Three Pilots Demo
                                                    |     [GATE: Value Agents 95%+]
                                                    |
                                                    +---> Week 9: Zero Seed Governance Pilot
                                                            |     [MILESTONE: Axiom discovery validation]
                                                            |
                                                            +---> Week 10: Categorical Foundation Package
                                                                          [MILESTONE: External law validation]
```

**Key Difference from Original**:
- Expanded from 8 to 10 weeks
- Added Core tier pilot (zero-seed-governance) in Week 9
- Added Meta tier pilot (categorical-foundation) in Week 10
- Added explicit gates and mathematical milestones

---

## Week 1: Core Pipeline (trail-to-crystal primitives)

### Goal

Validate Mark -> Trace -> Crystal pipeline works with trail-to-crystal requirements.

### Pilot Context: trail-to-crystal-daily-lab

From proto-spec:
- Every action must be a mark with reason and principle weights
- The daily trace is immutable and must remain audit-friendly
- Crystals are mandatory at the close of a day

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Run Witness tests | Claude | All tests pass | 30 min | - |
| Mark primitive at <50ms | Claude | Benchmark passing | 2 hrs | trail-to-crystal L2 |
| Trace append at <5ms | Claude | Benchmark passing | 1 hr | trail-to-crystal |
| Implement Amendment A (ETHICAL floor) | Claude | `scoring.py` updated | 2 hrs | All pilots |
| Literature search: Galois Loss novelty | Claude | Report on prior art | 2 hrs | Publication |
| Manual Mark/Trace test | Kent | 5 marks, trace displays | 1 hr | trail-to-crystal |
| Review Steel Thread spec | Kent | Go/no-go decision | 30 min | - |

### Exit Criteria (Measurement Protocols)

| Metric | Target | Measurement | Pass? |
|--------|--------|-------------|-------|
| Mark latency | < 50ms | `pytest --benchmark services/witness/mark.py` | [] |
| Trace append latency | < 5ms | `pytest --benchmark services/witness/trace.py` | [] |
| Witness tests pass | 100% | `uv run pytest services/witness/ -v` | [] |
| Amendment A implemented | Yes | ETHICAL floor test passes | [] |
| Kent approves direction | Go | Kent marks PASS in review | [] |

### No-Go Path

If Week 1 fails:
1. Diagnose which primitive is slow
2. Consider in-memory only (no persistence)
3. Reduce scope to Mark only, defer Trace
4. Extend Week 1 by 3 days before abandoning

---

## Week 2: Galois Integration (wasm-survivors drift detection)

### Goal

Galois loss API works, validated through wasm-survivors drift detection scenario.

### Pilot Context: wasm-survivors-game

From proto-spec:
- Galois loss is the coherence metric for build drift and chaotic deviation
- If Galois loss exceeds threshold during a run, the system must surface the drift

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Create `protocols/api/galois.py` | Claude | 4 endpoints | 3 hrs | wasm-survivors |
| Implement canonical distance (Amendment B) | Claude | `distance.py` updated | 2 hrs | All pilots |
| Galois loss for "build coherence" scenario | Claude | Test case from gaming domain | 2 hrs | wasm-survivors L1 |
| Caching layer | Claude | In-memory cache, 24h TTL | 1 hr | - |
| Performance benchmark | Claude | Latency report | 1 hr | - |
| Manual demo: drift detection | Kent | 3 "build drift" scenarios | 1 hr | wasm-survivors |

### The Four Endpoints (for pilot validation)

```python
# 1. Compute Galois loss (used by wasm-survivors for build coherence)
POST /api/galois/loss
Request: { "content": "...", "context": "build_coherence" }
Response: {
    "loss": 0.23,
    "layer": 3,
    "layer_name": "Goal",
    "confidence": 0.77,
    "latency_ms": 1850
}

# 2. Detect contradiction (used by all pilots)
POST /api/galois/contradiction
# ...

# 3. Check fixed point (axiom detection)
POST /api/galois/fixed-point
# ...

# 4. Assign layer
POST /api/layer/assign
# ...
```

### Exit Criteria

| Metric | Target | Measurement | Pass? |
|--------|--------|-------------|-------|
| Galois loss API works | 4 endpoints | Integration tests pass | [] |
| Fresh latency | < 5s | P95 from benchmark | [] |
| Cached latency | < 500ms | P95 from benchmark | [] |
| wasm-survivors drift detection | 3/3 scenarios | Kent validates | [] |
| API test coverage | > 90% | `pytest --cov` | [] |

### Pivot Trigger

If fresh latency > 20s consistently:
1. Try Claude Haiku for R-C operations
2. Implement aggressive caching
3. Fall back to BERTScore only

---

## Week 3: ValueCompass (disney-portal constitutional scoring)

### Goal

Constitutional scoring works, validated through disney-portal tradeoff explanation.

### Pilot Context: disney-portal-planner

From proto-spec:
- Constitutional scores must be explainable in natural language per day
- L3 Joy Transparency Law: system must surface where joy was traded for composability

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Constitutional service | Claude | `services/constitution/` | 3 hrs | All pilots |
| 7-principle scoring API | Claude | POST /api/constitution/score | 2 hrs | disney-portal |
| Joy/composability tradeoff explanation | Claude | Natural language generator | 2 hrs | disney-portal L3 |
| ValueCompass UI component | Claude | Radar chart | 3 hrs | All pilots |
| Day constitutional summary | Claude | Per-day rollup | 2 hrs | disney-portal |
| Review tradeoff explanations | Kent | Validate 5 day summaries | 1 hr | disney-portal |

### Exit Criteria

| Metric | Target | Measurement | Pass? |
|--------|--------|-------------|-------|
| 7-principle scoring works | Yes | Integration tests | [] |
| ETHICAL floor blocks violations | Yes | Unit test | [] |
| Tradeoff explanation readable | 4/5 | Kent validates | [] |
| ValueCompass UI works | Yes | Visual test | [] |
| disney-portal constitutional | 1 day with 5 decisions scored | Kent validates | [] |

---

## Week 4: Trail Primitive (rap-coach session navigation)

### Goal

Trail navigation works for 100+ marks, validated through rap-coach session navigation.

### Pilot Context: rap-coach-flow-lab

From proto-spec:
- A session trace is immutable; all feedback must attach to a mark
- L2 Feedback Grounding Law: All critique must reference a mark or trace segment

### Implementation Gate: K-Block 90%+

**Current**: 80% implementation faithfulness
**Required**: 90%+ before Week 4 exit

**Gap to close**:
- Complete K-Block postgres storage implementation
- Verify layer factory tests pass
- Run `kg audit spec/k-block.md --full`

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Trail primitive implementation | Claude | `services/witness/trail.py` | 3 hrs | All pilots |
| Navigation API | Claude | GET /api/witness/trail/{session} | 2 hrs | rap-coach |
| Compression ratio display | Claude | Trail metadata | 1 hr | All pilots |
| 100+ mark performance test | Claude | Benchmark | 1 hr | rap-coach |
| Feedback attachment UI | Claude | Mark -> Feedback linking | 2 hrs | rap-coach L2 |
| K-Block gate validation | Claude | 90%+ implementation | 2 hrs | Gate |
| Review session navigation | Kent | Navigate a 20-mark session | 1 hr | rap-coach |

### Mathematical Milestone: Galois Loss on trail-to-crystal

**Validation**: Run Galois loss computation on trail-to-crystal outputs
- Input: 5 representative daily traces
- Expected: L values correlate with perceived coherence
- Pass criterion: Kent confirms L < 0.1 traces feel coherent

### Exit Criteria

| Metric | Target | Measurement | Pass? |
|--------|--------|-------------|-------|
| Trail navigates 100+ marks | < 100ms | Benchmark | [] |
| Feedback attaches to mark | Yes | Integration test | [] |
| Compression ratio displayed | Yes | UI test | [] |
| rap-coach session navigation | 1 session with 20+ marks | Kent validates | [] |
| K-Block implementation | 90%+ | `kg audit` | [] |
| Galois loss correlates | Kent confirms | 5 trace validation | [] |

---

## Week 5: Crystal Compression (sprite-lab style crystals)

### Goal

Crystal compression works at <10% of trace size, validated through sprite-lab style crystals.

### Pilot Context: sprite-procedural-taste-lab (now: sprite-lab)

From proto-spec:
- Crystals compress the style journey and explain the current attractor
- L5 Style Continuity Law: The crystal must justify why the current style is stable

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Crystal compression service | Claude | `services/witness/crystal.py` | 3 hrs | All pilots |
| Style evolution summary | Claude | Domain-specific crystal | 2 hrs | sprite-lab L5 |
| Compression ratio validation | Claude | < 10% of trace | 1 hr | All pilots |
| Crystal API | Claude | POST /api/witness/crystal | 2 hrs | - |
| "Why stable" explanation | Claude | Natural language | 2 hrs | sprite-lab |
| Review style crystals | Kent | Validate 3 style evolution summaries | 1 hr | sprite-lab |

### Exit Criteria

| Metric | Target | Measurement | Pass? |
|--------|--------|-------------|-------|
| Crystal size | < 10% of trace | Unit test | [] |
| Crystal is readable standalone | 4/5 | Kent validates | [] |
| "Why stable" explanation works | Yes | sprite-lab test | [] |
| Compression preserves causal rationale | Yes | Kent validates | [] |

---

## Week 6: FIRST PILOT COMPLETE (trail-to-crystal-daily-lab)

### Goal

First pilot ships. User can explain their day using crystal + trail.

### Pilot Context: trail-to-crystal-daily-lab

From proto-spec:
- A user can explain their day using only the crystal and trail
- The system can surface at least one honest gap without shaming
- The day ends with a single, shareable artifact

### Implementation Gate: Galois Distance 95%+

**Current**: 85% implementation faithfulness
**Required**: 95%+ before Week 6 exit

**Gap to close**:
- Complete canonical distance implementation
- Verify fixed point detection works
- Run `kg audit spec/zero-seed/galois.md --full`

### Mathematical Milestone: Galois Loss Validation

**Validation**: Comprehensive Galois loss testing
- Run on all Week 4 trail-to-crystal outputs
- Verify L < 0.1 for coherent days
- Verify L > 0.3 for fragmented days
- Document correlation coefficient

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Pilot integration | Claude | Full pipeline | 4 hrs | trail-to-crystal |
| Daily mark capture UI | Claude | Text input + intent tag | 2 hrs | trail-to-crystal |
| End-of-day crystal generation | Claude | Automated or triggered | 2 hrs | trail-to-crystal L1 |
| Honest gap detection | Claude | Provisional mark surfacing | 2 hrs | trail-to-crystal QA-2 |
| Shareable artifact export | Claude | Crystal as image/link | 2 hrs | trail-to-crystal |
| Galois distance gate validation | Claude | 95%+ implementation | 2 hrs | Gate |
| Full day test | Kent | Use pilot for 1 real day | 3 hrs | trail-to-crystal |

### Canary Success Criteria (from proto-spec)

| Criterion | Measurement | Pass? |
|-----------|-------------|-------|
| User can explain day using crystal + trail | Kent narrates day in < 2 min | [] |
| System surfaces one honest gap | Gap appears in crystal | [] |
| Day ends with shareable artifact | Export works | [] |

### Definition of Done for First Pilot

1. All 3 canary success criteria pass
2. Kent used it for 1 full real day
3. No critical bugs in daily workflow
4. Crystal is shareable externally
5. Galois distance implementation at 95%+
6. Galois loss validation documented

---

## Week 7: Second Pilot (wasm-survivors OR rap-coach)

### Goal

Second pilot ships. Run/session crystal works.

### Choice: Which Pilot?

| Criterion | wasm-survivors | rap-coach |
|-----------|----------------|-----------|
| Infrastructure overlap | HIGH (Galois done Week 2) | MEDIUM (Trail done Week 4) |
| Unique validation | Real-time performance | Subjective coherence |
| Joy dimension tested | FLOW | SURPRISE |
| Build complexity | HIGH (WASM) | MEDIUM (audio optional) |

**Recommendation**: Ship **rap-coach** if audio can be text-only (voice transcript). Ship **wasm-survivors** if WASM infrastructure is already available.

### Tasks (rap-coach assumed)

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Take mark UI | Claude | Intent + stance capture | 2 hrs | rap-coach L1 |
| Session trace view | Claude | Timeline of takes | 2 hrs | rap-coach |
| Intent/delivery mismatch (Galois) | Claude | Take-level loss | 2 hrs | rap-coach L4 |
| Courage preservation | Claude | High-risk takes protected | 1 hr | rap-coach L4 |
| Voice continuity crystal | Claude | Through-line summary | 2 hrs | rap-coach L3 |
| Full session test | Kent | 5-take practice session | 2 hrs | rap-coach |

### Exit Criteria

| Metric | Target | Pass? |
|--------|--------|-------|
| User can describe voice shift via crystal | Yes | [] |
| User can replay session trace | Yes | [] |
| System surfaces repair path for high-loss take | Yes | [] |

---

## Week 8: Three Pilots Demo

### Goal

Three pilots demo-ready. External stakeholders see the vision.

### Implementation Gate: Value Agents 95%+

**Current**: 85% implementation faithfulness
**Required**: 95%+ before Week 8 exit

**Gap to close**:
- Complete value agent scoring implementation
- Verify constitutional integration works
- Run `kg audit spec/value-agents.md --full`

### Mathematical Milestone: Categorical Law Validation

**Validation**: Pre-validation of categorical package
- Run isolated tests on PolyAgent morphism laws
- Verify Operad composition is associative
- Test Sheaf gluing produces global consistency

### Tasks

| Task | Owner | Deliverable | Duration |
|------|-------|-------------|----------|
| Third pilot quick MVP | Claude | Any of remaining 3 | 4 hrs |
| Demo script for 3 pilots | Claude | 10-minute walkthrough | 2 hrs |
| Performance hardening | Claude | No critical bugs | 2 hrs |
| Value Agents gate validation | Claude | 95%+ implementation | 2 hrs |
| Categorical law pre-validation | Claude | PolyAgent/Operad tests | 2 hrs |
| External stakeholder demo | Kent | 2-3 people see demos | 2 hrs |
| Feedback crystallization | Claude | Witness marks of feedback | 1 hr |

### Exit Criteria

| Metric | Target | Pass? |
|--------|--------|-------|
| 3 pilots demo-ready | Yes | [] |
| External stakeholders impressed | 2/3 positive | [] |
| No critical bugs during demo | Yes | [] |
| Feedback captured as witness marks | Yes | [] |
| Value Agents implementation | 95%+ | [] |
| Categorical laws validated | All pass | [] |

---

## Week 9: Zero Seed Personal Governance Pilot

### Goal

Zero Seed Governance pilot ships. User can discover axioms and build personal constitution.

### Pilot Context: zero-seed-governance

**New Core Tier Pilot**:
- Axiom discovery from personal decisions
- Personal constitution building
- L < 0.05 fixed point validation for true axioms

### Mathematical Milestone: Axiom Discovery Validation

**Validation**: Verify axiom discovery produces true fixed points
- Input: 10 personal decisions from Kent
- Process: Run zero-seed axiom discovery
- Expected: Discovered axioms have L < 0.05
- Pass criterion: At least 3 axioms reach fixed point status

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Axiom discovery service | Claude | `services/zero_seed/axiom_discovery.py` | 3 hrs | zero-seed-governance |
| Personal constitution builder | Claude | `services/constitution/personal.py` | 3 hrs | zero-seed-governance |
| Fixed point validation API | Claude | POST /api/zero-seed/validate-axiom | 2 hrs | zero-seed-governance |
| Axiom stability visualization | Claude | UI showing fixed point convergence | 2 hrs | zero-seed-governance |
| Contradiction detection | Claude | Surface axiom conflicts | 2 hrs | zero-seed-governance |
| Personal governance test | Kent | Discover 3 personal axioms | 2 hrs | zero-seed-governance |

### Exit Criteria

| Metric | Target | Pass? |
|--------|--------|-------|
| Axiom discovery works | Yes | [] |
| Fixed points have L < 0.05 | 3/3 axioms | [] |
| Personal constitution builds | Yes | [] |
| Contradiction detection works | Yes | [] |
| Kent validates personal axioms | Feels true | [] |

### Canary Success Criteria

| Criterion | Measurement | Pass? |
|-----------|-------------|-------|
| User can articulate 3 personal axioms | Kent states axioms naturally | [] |
| Axioms feel stable (not contextual) | Kent confirms fixed point intuition | [] |
| Constitution feels like "me on my best day" | Mirror Test passes | [] |

---

## Week 10: Categorical Foundation Package

### Goal

Categorical Foundation packages for external use. PolyAgent, Operad, Sheaf as libraries.

### Pilot Context: categorical-foundation

**Meta Tier Pilot**:
- Package categorical primitives for open-source release
- Validate laws hold in isolated tests
- Enable external developers to build with kgents foundations

### Mathematical Milestone: External Law Validation

**Validation**: Laws hold in isolated package
- PolyAgent: Functor laws, naturality of mode transitions
- Operad: Associativity of composition, unit laws
- Sheaf: Gluing preserves local-to-global consistency

### Tasks

| Task | Owner | Deliverable | Duration | Pilot Validation |
|------|-------|-------------|----------|------------------|
| Extract PolyAgent to package | Claude | `kgents-categorical/polyagent/` | 3 hrs | categorical-foundation |
| Extract Operad to package | Claude | `kgents-categorical/operad/` | 3 hrs | categorical-foundation |
| Extract Sheaf to package | Claude | `kgents-categorical/sheaf/` | 2 hrs | categorical-foundation |
| Comprehensive law tests | Claude | Categorical law test suite | 3 hrs | categorical-foundation |
| Documentation | Claude | Usage examples, API docs | 2 hrs | categorical-foundation |
| Package publication prep | Claude | PyPI-ready package | 1 hr | categorical-foundation |
| External validation | Kent | Share with 2 external developers | 2 hrs | categorical-foundation |

### Exit Criteria

| Metric | Target | Pass? |
|--------|--------|-------|
| PolyAgent laws pass | All functor laws | [] |
| Operad laws pass | Associativity + unit | [] |
| Sheaf laws pass | Gluing consistency | [] |
| Package is installable | pip install works | [] |
| Documentation complete | 2 external devs understand | [] |
| External feedback positive | 2/2 positive | [] |

### Canary Success Criteria

| Criterion | Measurement | Pass? |
|-----------|-------------|-------|
| External developer can build with package | Working example in < 1 hour | [] |
| Laws feel natural to external dev | No confusion about categorical structure | [] |
| Package is "daring, bold, creative" | Kent validates aesthetic | [] |

---

## Resource Allocation (REVISED)

### Kent's Weekly Time Budget

| Week | Pilot Context | Review | Testing | Total |
|------|---------------|--------|---------|-------|
| 1 | Core pipeline | 0.5 hr | 1 hr | 1.5 hrs |
| 2 | wasm-survivors | 0.5 hr | 1 hr | 1.5 hrs |
| 3 | disney-portal | 0.5 hr | 1 hr | 1.5 hrs |
| 4 | rap-coach | 0.5 hr | 1.5 hr | 2 hrs |
| 5 | sprite-lab | 0.5 hr | 1 hr | 1.5 hrs |
| 6 | trail-to-crystal (FULL DAY) | 0.5 hr | 3 hrs | 3.5 hrs |
| 7 | Second pilot | 0.5 hr | 2 hrs | 2.5 hrs |
| 8 | Demo | 0.5 hr | 2 hrs | 2.5 hrs |
| 9 | zero-seed-governance | 0.5 hr | 2 hrs | 2.5 hrs |
| 10 | categorical-foundation | 0.5 hr | 2 hrs | 2.5 hrs |

**Average**: ~2.1 hrs/week (slightly more due to expanded scope)

---

## Research Track (Parallel, REVISED)

### Week 1: Literature Search FIRST

Before claiming novelty, search for:
- Round-trip semantic distance
- VAE reconstruction loss for semantics
- Lossy compression for coherence
- Bidirectional entailment metrics

**Deliverable**: 2-page report on prior art and differentiation

### Timeline

```
Week 1:   LITERATURE SEARCH (before any novelty claims)
Week 2-5: PRODUCT FOCUS (build and validate with pilots)
Week 5-6: START WRITING (if novelty confirmed)
Week 7:   ARXIV PREPRINT (timestamp the idea)
Week 8+:  WORKSHOP SUBMISSION (if pilots successful)
Week 10:  OPEN-SOURCE RELEASE (categorical-foundation package)
```

---

## Week-by-Week Checklist (Pilot-Grounded)

### Week 1

- [ ] Mark latency < 50ms
- [ ] Trace append < 5ms
- [ ] Witness tests pass
- [ ] Amendment A implemented
- [ ] Literature search complete
- [ ] Kent gives go/no-go

### Week 2

- [ ] Galois API works (4 endpoints)
- [ ] wasm-survivors drift detection: 3/3 scenarios
- [ ] Fresh latency < 5s
- [ ] Cached latency < 500ms

### Week 3

- [ ] 7-principle scoring works
- [ ] disney-portal constitutional: 1 day with 5 decisions
- [ ] Tradeoff explanation readable: 4/5
- [ ] ValueCompass UI works

### Week 4

- [ ] Trail navigates 100+ marks < 100ms
- [ ] rap-coach session navigation works
- [ ] Feedback attaches to mark
- [ ] **GATE: K-Block implementation 90%+**
- [ ] **MILESTONE: Galois loss correlates with coherence**

### Week 5

- [ ] Crystal compression < 10%
- [ ] sprite-lab style crystals work
- [ ] "Why stable" explanation works

### Week 6 (FIRST PILOT)

- [ ] trail-to-crystal-daily-lab ships
- [ ] Kent uses for 1 full real day
- [ ] All 3 canary success criteria pass
- [ ] Crystal is shareable
- [ ] **GATE: Galois distance implementation 95%+**
- [ ] **MILESTONE: Galois loss validation documented**

### Week 7

- [ ] Second pilot ships
- [ ] Canary success criteria pass

### Week 8

- [ ] Three pilots demo-ready
- [ ] External stakeholders see demos
- [ ] Feedback crystallized
- [ ] **GATE: Value Agents implementation 95%+**
- [ ] **MILESTONE: Categorical laws pre-validated**

### Week 9 (ZERO SEED GOVERNANCE)

- [ ] Axiom discovery service works
- [ ] Personal constitution builder works
- [ ] Fixed point validation API works
- [ ] Kent discovers 3 personal axioms
- [ ] **MILESTONE: Axiom discovery produces L < 0.05 fixed points**

### Week 10 (CATEGORICAL FOUNDATION)

- [ ] PolyAgent package extracted
- [ ] Operad package extracted
- [ ] Sheaf package extracted
- [ ] All categorical law tests pass
- [ ] Package is PyPI-ready
- [ ] External developers validate
- [ ] **MILESTONE: External categorical law tests pass**

---

## Grounding Statement

This roadmap has been restructured based on:
- **Analysis Operad critique** (Categorical 0.65 -> fixed false parallelism)
- **Zero Seed audit** (timeline/scope contradiction resolved)
- **Pilot Coherence Analysis** (each week validates infrastructure THROUGH a pilot)
- **7-Pilot System** (Core/Domain/Meta tiers for comprehensive validation)
- **Implementation Faithfulness Gates** (audit-driven quality gates)
- **Mathematical Validation Milestones** (explicit grounding checkpoints)

The key insight: **Pilots are the test suite**. Infrastructure that doesn't serve a pilot shouldn't be built.

---

**Document Metadata**
- **Lines**: ~650
- **Status**: Execution Roadmap - 7-Pilot Expanded Edition
- **Audited**: 2025-12-26 (Analysis Operad + Zero Seed + Faithfulness Audit)
- **Next Action**: Begin Week 1 Core Pipeline
- **Owner**: Kent Gang + Claude
