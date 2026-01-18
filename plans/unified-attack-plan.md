# Unified Attack Plan: Three-Front Convergence

> *"Depth over breadth. The proof IS the decision."*

**Created**: 2025-01-17
**Status**: ACTIVE EXECUTION
**Coherence Target**: L ~ 0.15 → L ~ 0.10 (move toward CATEGORICAL)

---

## Executive Summary

Three plan areas converge on **one steel thread**: `Mark → Trace → Crystal` with constitutional grounding.

| Plan Area | Current | Target | Critical Path |
|-----------|---------|--------|---------------|
| **enlightened-synthesis** | ~25% | 60% | Amendment A/B, Week 6 pilot |
| **ashc-consumer-integration** | ~35% | 70% | Backend services, 6 UI components |
| **theory-operationalization** | ~45% | 75% | G1 calibration, E2 operad, D1 Bellman |

**Unified Goal**: First pilot (trail-to-crystal) ships by Week 6 with:
- Constitutional scoring (Amendment A)
- Galois Loss integration (Amendment B)
- Derivation visibility (ASHC)
- Witnessed operations (E1, E3 already done)

---

## Phase 1: Foundation Layer (Days 1-5)
### *"Fix the floor before building the walls"*

### 1.1 Amendment A: ETHICAL Floor Constraint (CRITICAL)
**Files**: `impl/claude/services/constitution/scoring.py`
**Effort**: 1 day
**Why First**: Blocks all downstream work—unethical actions must not pass

```python
# Core implementation
def evaluate(self, decision: Decision) -> ConstitutionalScore:
    ethical_score = self._evaluate_ethical(decision)
    if ethical_score < 0.6:
        return ConstitutionalScore(
            weighted_total=0.0,
            ethical_passes=False,
            reason="ETHICAL floor violation"
        )
    # ... continue with weighted sum
```

**Validation**:
- [ ] Test: ETHICAL < 0.6 → weighted_total = 0.0
- [ ] Test: ETHICAL >= 0.6 → normal weighted sum
- [ ] Test: High other scores can't offset low ETHICAL

### 1.2 Amendment B: Canonical Semantic Distance
**Files**: `impl/claude/services/zero_seed/galois/distance.py`
**Effort**: 2 days
**Why**: Foundation for all Galois Loss computation

```python
# Bidirectional entailment distance
def canonical_distance(a: str, b: str) -> float:
    p_a_to_b = entailment_probability(a, b)
    p_b_to_a = entailment_probability(b, a)
    return 1 - math.sqrt(p_a_to_b * p_b_to_a)
```

**Fallback chain**: NLI → BERTScore → Cosine

### 1.3 D1: ConstrainedBellmanEquation
**Files**: `impl/claude/services/dp/bellman.py`
**Effort**: 3 days
**Depends on**: Amendment A (Constitution.evaluate)

```python
# ETHICAL as hard constraint, not soft penalty
def bellman_update(state: S, action: A) -> float:
    if not constitution.is_ethical(action):
        return float('-inf')  # Excluded, not penalized
    return reward(state, action) + gamma * V(next_state)
```

**Monotonic Inheritance Law**: `A_ethical(child) ⊆ A_ethical(parent)`

---

## Phase 2: Theory Operationalization (Days 6-15)
### *"Validate the core bet before building on it"*

### 2.1 G1: Calibration Pipeline (CRITICAL PATH)
**Files**: `impl/claude/services/zero_seed/galois/calibration.py`
**Effort**: 5 days
**Current**: 9 calibration entries
**Target**: 100+ entries with correlation analysis

**The Core Bet**: `L(P) ∝ D(P)` — Galois Loss predicts difficulty

**Tasks**:
1. Expand calibration corpus (9 → 100+)
2. Stratify by domain (coding, writing, reasoning, creative)
3. Compute Pearson correlation r(L, D)
4. Go/No-Go decision at Week 9

**Decision Matrix**:
| Correlation | Action |
|-------------|--------|
| r > 0.5 | VALIDATED → unlock G2-G5 |
| r = 0.3-0.5 | UNCERTAIN → expand to 200+ |
| r < 0.3 | FALSIFIED → pivot to Galois Lite |

### 2.2 E2: Analysis Operad Composer
**Files**: `impl/claude/services/categorical/analysis_operad.py`
**Effort**: 3 days
**Depends on**: E1 (Kleisli Witness) - DONE

**Four modes compose via Kleisli**:
```
CATEGORICAL → EPISTEMIC → DIALECTICAL → GENERATIVE
```

```python
@dataclass
class AnalysisOperad:
    categorical: Callable[[Spec], CategoricalAnalysis]
    epistemic: Callable[[CategoricalAnalysis], EpistemicAnalysis]
    dialectical: Callable[[EpistemicAnalysis], DialecticalAnalysis]
    generative: Callable[[DialecticalAnalysis], GenerativeAnalysis]

    def compose(self, spec: Spec) -> FullAnalysis:
        return kleisli_compose(
            self.categorical,
            self.epistemic,
            self.dialectical,
            self.generative
        )(spec)
```

### 2.3 M3: BindingComplexityEstimator
**Files**: `impl/claude/services/multi_agent/binding.py`
**Effort**: 2 days
**Status**: Fully specified, ready to implement

**Sub-additivity for auto-decomposition**:
```python
def should_decompose(task: Task) -> bool:
    whole = binding_complexity(task)
    parts = sum(binding_complexity(p) for p in decompose(task))
    return parts < whole  # Sub-additive → decompose
```

---

## Phase 3: ASHC Consumer Integration (Days 10-25)
### *"Make derivation visible while you work"*

### 3.1 Backend Services
**Files**: `impl/claude/services/ashc/`
**Effort**: 5 days

| Service | Purpose | Priority |
|---------|---------|----------|
| `DerivationService` | Compute derivation paths | P0 |
| `RealizationService` | Project-wide scanning | P1 |
| `ConstitutionalGraphService` | Graph queries | P1 |

**Key Endpoints**:
```
POST /agentese/self/ashc/context/{blockId}  → DerivationContext
GET  /agentese/self/ashc/graph              → DerivationGraph
POST /agentese/self/ashc/ground             → GroundingResult
GET  /agentese/self/ashc/coherence          → CoherenceSummary
```

### 3.2 Frontend Components (6 total)
**Files**: `impl/claude/web/src/components/ashc/`
**Effort**: 8 days

**Implementation Order** (dependency-driven):
1. **GaloisCoherenceMeter** (2d) - Foundation indicator
2. **DerivationTrailBar** (2d) - Core navigation
3. **DerivationInspector** (1d) - Detail panel
4. **ProjectRealizationWelcome** (1d) - Entry screen
5. **GroundingDialog** (1d) - Orphan resolution
6. **ConstitutionalGraphView** (1d) - Alternative navigation

**Trail Bar Design**:
```
COMPOSABLE(0.95) → witness.md(0.08) → mark.py(0.15) → [YOU]
```

### 3.3 Zustand Store Integration
**Files**: `impl/claude/web/src/stores/ashc/`
**Effort**: 2 days

- `DerivationStore`: Derivation context state
- `KBlockStore` extensions: Grounding metadata
- Subscription architecture for real-time updates

---

## Phase 4: Pilot Integration (Days 20-35)
### *"Validate infrastructure THROUGH pilots, not in isolation"*

### 4.1 trail-to-crystal (Week 6 - FIRST PILOT)
**Domain**: Productivity
**Joy**: FLOW (50%)
**Validates**: Mark → Trace → Crystal spine

**Integration Points**:
- Constitutional scoring (Amendment A)
- Galois Loss for coherence (Amendment B)
- Derivation visibility (ASHC)
- Witness traces (E1, E3)

**Success Criteria (The Mirror Test)**:
- [ ] QA-1: Lighter than to-do list (<5s to mark)
- [ ] QA-2: Honest gaps are data (no shame)
- [ ] QA-3: Crystals deserve re-reading
- [ ] QA-4: Bold choices protected
- [ ] QA-5: Explain day with crystal + trail
- [ ] QA-6: No hustle theater

### 4.2 zero-seed-governance (Week 9)
**Domain**: Personal Constitution
**Validates**: Axiom discovery (L < 0.05)

### 4.3 wasm-survivors, disney-portal, rap-coach (Week 7-8)
**Domain**: Gaming, Consumer, Creative
**Validates**: Real-time Galois drift, Constitutional tradeoffs

---

## Dependency Graph

```
                    Amendment A (Day 1)
                          │
                          ▼
              ┌───────────┴───────────┐
              │                       │
        Amendment B (Day 2-3)    D1 Bellman (Day 3-5)
              │                       │
              ▼                       ▼
        G1 Calibration ────────► Constitutional Scoring
        (Days 6-10)                   │
              │                       │
              ▼                       ▼
        E2 Operad             ASHC Backend
        (Days 8-10)           (Days 10-15)
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                   ASHC Frontend
                   (Days 15-23)
                          │
                          ▼
              ┌───────────┴───────────┐
              │           │           │
        trail-to-     rap-coach   wasm-survivors
        crystal        (Week 7)    (Week 7)
        (Week 6)
```

---

## Resource Allocation

### Parallel Workstreams

**Stream A (Theory)**: G1 → E2 → M3
**Stream B (Infrastructure)**: Amendment A → Amendment B → D1
**Stream C (Consumer)**: ASHC Backend → ASHC Frontend
**Stream D (Pilots)**: trail-to-crystal → governance → domain pilots

### Recommended Execution

| Week | Stream A | Stream B | Stream C | Stream D |
|------|----------|----------|----------|----------|
| 1 | - | Amendment A/B | - | - |
| 2 | G1 start | D1 | ASHC Backend | - |
| 3 | G1 continue | D1 complete | ASHC Backend | - |
| 4 | E2 | - | ASHC Frontend | - |
| 5 | M3 | - | ASHC Frontend | trail-to-crystal prep |
| 6 | - | - | Integration | **FIRST PILOT SHIPS** |

---

## Risk Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| G1 falsifies L ∝ D | HIGH | Pivot to Galois Lite (fixed-point only) |
| ASHC components too complex | MEDIUM | Start with TrailBar only, defer Graph |
| Amendment B distance unreliable | MEDIUM | Fallback chain (NLI → BERT → Cosine) |
| Pilot ships late | HIGH | Reduce scope: crystals → marks only |

---

## Success Metrics

### Week 6 Gate (First Pilot)
- [ ] Amendment A enforcing ETHICAL floor
- [ ] Amendment B computing Galois Loss
- [ ] D1 using constitutional reward
- [ ] trail-to-crystal passing Mirror Test
- [ ] At least 3 ASHC components working

### Week 9 Gate (G1 Validation)
- [ ] 100+ calibration entries
- [ ] Correlation r > 0.3 (minimum)
- [ ] Go/No-Go decision documented

### Week 10 Gate (Full Integration)
- [ ] All 6 ASHC components integrated
- [ ] 3+ pilots demo-ready
- [ ] Constitutional scoring operational
- [ ] Galois Loss API available

---

## Voice Anchors (from Kent)

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"The Mirror Test: Does K-gent feel like me on my best day?"*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*
> *"Depth over breadth"*

Every decision in this plan passes the Mirror Test.

---

*Filed: 2025-01-17 | Status: READY FOR EXECUTION*
