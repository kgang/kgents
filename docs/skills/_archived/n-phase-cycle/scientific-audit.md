# Scientific Audit: N-Phase Cycle Effectiveness

> *"That which can be measured can be improved. That which can be hypothesized can be tested."*

**Status**: Active Research Document
**Date**: 2025-12-15
**Purpose**: Evaluate the effectiveness of the N-Phase Cycle + Auto-Continuation meta-system through scientific hypotheses and procedural experiments.

---

## Executive Summary

The N-Phase Cycle is a meta-framework for elastic tree/outline building suited to user tastes, project complexity, and substrate constraints. This audit evaluates its effectiveness through:

1. **Hypotheses** — Falsifiable claims about the system
2. **Experiments** — Procedural tests to validate/invalidate
3. **Metrics** — Quantitative measures of effectiveness
4. **Findings** — Observations from system use

---

## Hypotheses

### H1: Elastic Adaptation Reduces Ceremony Overhead

**Claim**: Tasks completed using dynamic phase selection (3↔11 expansion/compression) require fewer tokens than fixed-sequence execution.

**Null Hypothesis**: There is no significant difference in token consumption between elastic and fixed-sequence execution.

**Measurement**:
- Token count per task across matched complexity levels
- Ceremony-to-output ratio (tokens spent on phase transitions vs. artifacts)

**Experiment**: E1 (below)

---

### H2: Serendipitous Branching Improves Discovery

**Claim**: Cycles that use entropy-driven branching (`void.entropy.sip` → `⤳[BRANCH]`) discover more actionable insights than linear cycles.

**Null Hypothesis**: Branching frequency has no correlation with insight discovery rate.

**Measurement**:
- Branches created per cycle
- Insights promoted to `plans/meta.md` per cycle
- Bounty items created and claimed

**Experiment**: E2 (below)

---

### H3: User Taste Adaptation Increases Satisfaction

**Claim**: Agents that adapt tree shape to user preference signals (depth vs. speed vs. exploration) receive higher subjective ratings.

**Null Hypothesis**: Tree shape has no effect on user satisfaction.

**Measurement**:
- User preference surveys (pre/post)
- Session continuation rates
- Explicit feedback ("this is too slow" / "this is too superficial")

**Experiment**: E3 (below)

---

### H4: Auto-Continuation Reduces Interpretive Gap

**Claim**: Sessions using auto-inducer signifiers (`⟿`/`⟂`/`⤳`) have fewer misaligned transitions than sessions with manual prompt handoff.

**Null Hypothesis**: Auto-continuation does not reduce transition errors.

**Measurement**:
- Phase transition coherence (does next phase correctly consume prior output?)
- Rework required due to misaligned handoffs
- Context loss at session boundaries

**Experiment**: E4 (below)

---

### H5: Category Laws Preserve Coherence Under Mutation

**Claim**: Tree operations (FORK, JOIN, COMPRESS, EXPAND) that preserve identity and associativity maintain artifact coherence.

**Null Hypothesis**: Law-preserving operations are no more coherent than arbitrary mutations.

**Measurement**:
- Test suite pass rate before/after tree mutations
- Artifact dependency graph integrity
- Merge conflict rate at JOIN operations

**Experiment**: E5 (below)

---

### H6: Entropy Budget Prevents Premature Optimization

**Claim**: Cycles that reserve and spend 5-10% entropy budget produce more diverse solutions than cycles that skip exploration.

**Null Hypothesis**: Entropy budget has no effect on solution diversity.

**Measurement**:
- Alternative paths considered per task
- Counterfactuals documented
- Accursed Share items that later became primary tracks

**Experiment**: E6 (below)

---

## Experiments

### E1: Elastic vs. Fixed Sequence Token Comparison

**Protocol**:
1. Select 10 tasks of varying complexity (2 trivial, 4 standard, 4 complex)
2. Execute each task twice:
   - **Treatment A**: Full 11-phase fixed sequence
   - **Treatment B**: Elastic selection (3→11 based on signals)
3. Measure:
   - Total tokens consumed
   - Phases actually executed
   - Time to completion
   - Artifact quality (external review)

**Success Criterion**: Treatment B uses ≤70% tokens of Treatment A for equivalent quality.

**Data Collection**: `plans/_experiments/e1-elastic-vs-fixed/`

---

### E2: Branching Frequency vs. Insight Rate

**Protocol**:
1. Track 20 consecutive cycles
2. Record for each cycle:
   - Number of `⤳[BRANCH]` signals emitted
   - Number of insights promoted to meta.md
   - Number of bounty items created
   - Number of bounty items claimed within 7 days
3. Compute correlation between branching frequency and insight metrics

**Success Criterion**: Pearson r ≥ 0.5 between branching frequency and insight promotion rate.

**Data Collection**: `plans/_experiments/e2-branching-insight/`

---

### E3: User Preference Adaptation Survey

**Protocol**:
1. Survey users on preferred working style (depth/speed/exploration/certainty)
2. Randomly assign to:
   - **Treatment A**: Adaptive tree shape matching preference
   - **Treatment B**: Fixed tree shape (default 11-phase)
3. After 5 sessions, survey satisfaction and measure:
   - Session continuation rate
   - Explicit complaints logged
   - Self-reported alignment ("Did the process match your style?")

**Success Criterion**: Treatment A satisfaction score ≥1.5 standard deviations above Treatment B.

**Data Collection**: `plans/_experiments/e3-user-preference/`

---

### E4: Auto-Continuation Coherence Audit

**Protocol**:
1. Review 50 phase transitions (25 auto-induced, 25 manual)
2. Score each transition on:
   - Context preservation (0-3): Did all artifacts transfer?
   - Intent alignment (0-3): Did next phase address correct goal?
   - Rework required (0-3): How much backtracking needed?
3. Compare aggregate scores between groups

**Success Criterion**: Auto-induced transitions score ≥20% higher than manual.

**Data Collection**: `plans/_experiments/e4-auto-coherence/`

---

### E5: Category Law Preservation Test

**Protocol**:
1. Create a test harness for tree operations (impl/claude/protocols/nphase/tree_ops.py)
2. Define property-based tests:
   - Identity: `FORK >> JOIN ≈ Id` (on single branch)
   - Associativity: `(COMPRESS >> EXPAND) >> COMPRESS ≈ COMPRESS >> (EXPAND >> COMPRESS)`
3. Generate 1000 random tree mutations
4. Verify artifact coherence after each mutation

**Success Criterion**: 100% of law-preserving operations maintain coherence; ≥10% of non-law-preserving operations produce incoherence.

**Data Collection**: `impl/claude/protocols/nphase/_tests/test_tree_laws.py`

---

### E6: Entropy Budget Diversity Analysis

**Protocol**:
1. Track 30 cycles, split into:
   - **Group A**: 5-10% entropy budget enforced
   - **Group B**: No explicit entropy budget
2. Measure for each cycle:
   - Number of alternative paths considered
   - Number of counterfactuals documented
   - Number of void.* items later promoted to primary track
3. Compute diversity score = (alternatives + counterfactuals + promotions) / phases

**Success Criterion**: Group A diversity score ≥50% higher than Group B.

**Data Collection**: `plans/_experiments/e6-entropy-diversity/`

---

## Metrics Dashboard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Average tokens per standard task | ≤5000 | TBD | Pending |
| Elastic compression ratio | ≥30% | TBD | Pending |
| Branch-to-insight conversion rate | ≥20% | TBD | Pending |
| Auto-continuation coherence score | ≥2.5/3 | TBD | Pending |
| Law preservation rate | 100% | TBD | Pending |
| Entropy-driven diversity score | ≥0.5 | TBD | Pending |

---

## Findings Log

### 2025-12-15: Initial Audit

**Observation**: The N-Phase Cycle documentation was strong on theory but weak on elasticity language. The spec emphasized "N is variable" but didn't provide mechanisms for dynamic selection.

**Action**: Added Elasticity Principle to `spec/protocols/n-phase-cycle.md` with:
- Dynamic phase selection criteria
- Tree operations (FORK, JOIN, COMPRESS, EXPAND)
- User/project/substrate adaptation tables

**Observation**: Auto-inducer had only two signifiers (⟿/⟂), lacking elastic operations.

**Action**: Added third signifier (⤳) to `spec/protocols/auto-inducer.md` for:
- BRANCH (fork parallel track)
- JOIN (merge tracks)
- COMPRESS (condense phases)
- EXPAND (expand phases)
- Serendipity evaluation protocol

**Next**: Implement experiments E1-E6 to validate hypotheses.

---

## Recursive Hologram

This audit applies the N-Phase Cycle to itself:

| Phase | Action |
|-------|--------|
| PLAN | Define audit scope and hypotheses |
| RESEARCH | Read existing documentation |
| DEVELOP | Formulate testable hypotheses |
| STRATEGIZE | Design experiments |
| CROSS-SYNERGIZE | Connect to process-metrics.md |
| IMPLEMENT | Write this document, update specs |
| QA | Review for internal consistency |
| TEST | Run experiments |
| EDUCATE | Document findings |
| MEASURE | Populate metrics dashboard |
| REFLECT | Update hypotheses based on findings |

---

## Related

- `spec/protocols/n-phase-cycle.md` — Core spec (updated with Elasticity)
- `spec/protocols/auto-inducer.md` — Signifier spec (updated with ⤳)
- `process-metrics.md` — Metrics collection
- `metatheory.md` — Theoretical grounding
- `branching-protocol.md` — Branch classification

---

## Changelog

- 2025-12-15: Initial audit. 6 hypotheses, 6 experiments defined. Spec updates completed.
