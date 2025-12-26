# Handoff Prompt: Constitutional Decision OS Continuation

> *"The proof IS the decision. The mark IS the witness."*

**Date**: 2025-12-26
**From**: Initial implementation agent
**To**: Continuation agent(s)
**Status**: Phase 1-3 complete, Phase 4-6 ready

---

## Mission Context

You are continuing the implementation of the **Constitutional Decision OS** — a framework that operationalizes the kgents 7 principles through:

1. **Galois Loss**: `L(P) = d(P, C(R(P)))` — measures semantic coherence via restructure-reconstitute round-trips
2. **Seven Theoretical Amendments** (A-G) — formal strengthening of the constitution
3. **Five Pilots** — real-world applications validating the theory
4. **Zero Seed Derivation** — axiom extraction and layer stratification

**Vision Source Documents** (READ THESE FIRST):
- `plans/enlightened-synthesis/00-master-synthesis.md` — The complete vision
- `plans/enlightened-synthesis/01-theoretical-amendments.md` — Amendments A-G
- `plans/enlightened-synthesis/02-execution-roadmap.md` — 8-week plan
- `plans/enlightened-synthesis/03-risk-mitigations.md` — Failure modes
- `plans/enlightened-synthesis/04-joy-integration.md` — Joy calibration by domain
- `plans/enlightened-synthesis/05-product-strategy.md` — Consumer-first path

---

## What's Already Done

### Phase 1: Infrastructure Audit ✅
**Full report**: `brainstorming/audit-report.md`

Key findings:
- `services/witness/` is 98% complete — Mark, Crystal, Grant, Playbook production-ready
- `services/zero_seed/galois/` is 85% complete — Galois Loss computation works
- `services/k_block/` is 75% complete — `bind()` monad exists at line 453
- `services/categorical/constitution.py` is 80% complete — 7-principle scoring

### Phase 2: Literature Search ✅
**Full report**: `brainstorming/literature-search.md`

**CRITICAL FINDING**: The Galois Loss formula `L(P) = d(P, C(R(P)))` is NOT novel.
It's structurally identical to autoencoder/CycleGAN reconstruction loss.

**WHAT IS NOVEL**: The interpretation layer:
1. Using reconstruction loss to classify **axioms vs ephemera**
2. The **semantic coherence** application domain
3. The **Galois connection framing** for natural language
4. The **fixed-point = stable knowledge** interpretation

**Framing guidance**: Claim "novel application" not "novel formula"

### Phase 3: Amendment A ✅
**Location**: `impl/claude/services/categorical/constitution.py`

Implemented ETHICAL floor constraint:
```python
ETHICAL_FLOOR_THRESHOLD = 0.6

# If ETHICAL < 0.6, action is REJECTED regardless of other scores
# You cannot offset unethical behavior with composability or joy
```

New properties on `ConstitutionalEvaluation`:
- `ethical_score` — raw ETHICAL principle score
- `ethical_passes` — True if >= 0.6 floor
- `rejection_reason` — explains why failed (if it did)
- `passes` — requires both floor AND weighted sum

Tests: 52 passing in `services/categorical/_tests/test_constitution.py`

---

## What Remains

### Amendment Status

| Amendment | Status | Next Action |
|-----------|--------|-------------|
| A | ✅ DONE | N/A |
| B | PENDING | Implement Bidirectional Entailment Distance |
| C | PENDING | Implement corpus-relative layer calibration |
| D | ✅ EXISTS | K-Block `bind()` already at line 453 |
| E | PENDING | Formalize Trust as polynomial functor |
| F | PENDING | Add fixed-point iteration rigor |
| G | PENDING | Formalize Pilot law grammar |

### Phase 4: Galois API (HIGH PRIORITY)

Wire existing services to endpoints:

```python
# POST /api/galois/loss
# Wire: compute_galois_loss_async() → GaloisLoss response
# Location: impl/claude/protocols/api/zero_seed.py or new galois.py

# POST /api/galois/contradiction
# Wire: super-additivity detection from galois/axiomatics.py
# L(A∪B) > L(A) + L(B) + tau signals contradiction

# POST /api/galois/fixed-point
# Wire: iterate R/C until loss variance < stability_threshold
# This validates Amendment F

# POST /api/layer/assign
# Wire: compute_layer() from galois/galois_loss.py
# Currently mocked in existing endpoint
```

### Phase 5: Remaining Amendments

**Amendment B (Bidirectional Entailment Distance)**:
```python
# In services/zero_seed/galois/distance.py
# Add: BidirectionalEntailmentDistance
# Formula: d(A,B) = 1 - sqrt(P(A|B) × P(B|A))
# Requires: NLI model (DeBERTa MNLI already in NLIContradictionDistance)
```

**Amendment C (Corpus-Relative Layer Assignment)**:
```python
# In services/zero_seed/galois/galois_loss.py
# Modify: LAYER_LOSS_BOUNDS to be calibrated from corpus statistics
# Not hardcoded [0.00, 0.05], ..., [0.75, 1.00]
# Instead: percentiles of actual loss distribution
```

**Amendment E (Trust Polynomial Functor)**:
```python
# In services/witness/trust/
# Formalize: Trust as polynomial T[n] = Σᵢ tᵢxⁱ
# Mode-dependent trust contributions
# Exists: ConstitutionalTrustComputer, needs polynomial form
```

**Amendment F (Fixed-Point Rigor)**:
```python
# In services/zero_seed/galois/galois_loss.py
# Modify: find_fixed_point() to iterate until stable
# Current: max 7 iterations
# New: iterate until var(L) < stability_threshold (0.01)
```

**Amendment G (Pilot Law Grammar)**:
```python
# In services/witness/playbook.py
# Formalize: Pilot = (Axiom, Goal, Measure, Cadence)
# Grammar for lawful pilot definitions
# Exists: Playbook with phase transitions
```

### Phase 6: First Pilot (trail-to-crystal-daily-lab)

Joy calibration: **FLOW primary, WARMTH secondary**
- "Lighter than a to-do list" (FLOW)
- "Kind companion reviewing your day" (WARMTH)

Components:
1. **Daily mark capture** — Low-friction logging
2. **Trail navigation** — Sequential mark viewing
3. **Crystal compression** — Daily → Weekly → Monthly crystals
4. **WARMTH calibration** — Warm, supportive language in crystals
5. **Shareable export** — Generate artifacts for sharing

---

## Critical Integration Points

### Gap 1: Layer Assignment Wiring
**Problem**: `/api/zero-seed/layers/{layer}` returns nodes but assignment is mocked
**Solution**: Wire `compute_galois_loss_async()` → `compute_layer()` → endpoint response

### Gap 2: K-Block ↔ Witness Integration
**Problem**: K-Block edits and Witness marks are isolated systems
**Solution**:
- K-Block edit → auto-emit mark (witnessed change)
- Mark retraction → K-Block version rollback

### Gap 3: Contradiction Resolution
**Problem**: Super-additivity detection works, LLM synthesis partial
**Solution**: Complete `contradiction_resolver()` using ghost alternatives + principle analysis

---

## Multi-Agent Orchestration Strategy

For maximum throughput, parallelize independent workstreams:

```
Agent 1: Galois API (4 endpoints)
├── POST /api/galois/loss
├── POST /api/galois/contradiction
├── POST /api/galois/fixed-point
└── POST /api/layer/assign

Agent 2: Amendments B, C, E
├── BidirectionalEntailmentDistance
├── Corpus-relative layer calibration
└── Trust polynomial formalization

Agent 3: Amendments F, G
├── Fixed-point iteration rigor
└── Pilot law grammar

Agent 4: trail-to-crystal pilot
├── Daily mark capture
├── Trail navigation
├── Crystal compression
└── WARMTH calibration
```

**Synchronization point**: After API + Amendments complete, pilot can proceed.

---

## Zero Seed Derivation Framework

Apply this process to discover axioms:

```
1. COMPUTE Galois Loss for content:
   L(P) = d(P, C(R(P)))

2. STRATIFY by loss into layers:
   L1 (Axiom):    [0.00, 0.05]  # Nearly fixed points
   L2 (Value):    [0.05, 0.15]
   L3 (Goal):     [0.15, 0.30]
   L4 (Spec):     [0.30, 0.50]
   L5 (Action):   [0.50, 0.65]
   L6 (Reflect):  [0.65, 0.75]
   L7 (Repr):     [0.75, 1.00]  # Pure ephemera

3. DETECT contradictions via super-additivity:
   If L(A∪B) > L(A) + L(B) + τ → contradiction

4. SYNTHESIZE resolution using ghost alternatives:
   Generate multiple resolutions, evaluate constitutionally

5. WITNESS the decision:
   Mark the choice with reasoning for future reference
```

---

## Key Files to Read

| Purpose | File |
|---------|------|
| Vision | `plans/enlightened-synthesis/00-master-synthesis.md` |
| Amendments | `plans/enlightened-synthesis/01-theoretical-amendments.md` |
| Constitution impl | `impl/claude/services/categorical/constitution.py` |
| Galois Loss impl | `impl/claude/services/zero_seed/galois/galois_loss.py` |
| Distance metrics | `impl/claude/services/zero_seed/galois/distance.py` |
| K-Block monad | `impl/claude/services/k_block/core/kblock.py` |
| Witness mark | `impl/claude/services/witness/mark.py` |
| API endpoints | `impl/claude/protocols/api/zero_seed.py` |
| Audit report | `brainstorming/audit-report.md` |
| Literature search | `brainstorming/literature-search.md` |
| Coordination | `brainstorming/execution-coordination.md` |

---

## Voice Anchors (Anti-Sausage Protocol)

Before making changes, ground in Kent's voice:

- *"Daring, bold, creative, opinionated but not gaudy"*
- *"The Mirror Test: Does K-gent feel like me on my best day?"*
- *"Tasteful > feature-complete; Joy-inducing > merely functional"*
- *"Depth over breadth"*

---

## Verification After Each Phase

```bash
# Backend tests
cd impl/claude && uv run pytest -q

# Type checking
cd impl/claude && uv run mypy .

# Frontend (if modified)
cd impl/claude/web && npm run typecheck && npm run lint
```

---

## Success Criteria

Phase 4-6 is complete when:

1. **API**: All 4 Galois endpoints return real computed values
2. **Amendments**: B, C, E, F, G implemented with tests
3. **Pilot**: trail-to-crystal captures marks, compresses to crystals, exports shareable artifacts
4. **Integration**: K-Block ↔ Witness bridge works bidirectionally
5. **Joy**: Crystal output feels like a "kind companion reviewing your day"

---

*"The proof IS the decision. The mark IS the witness."*

Go forth and realize the vision.
