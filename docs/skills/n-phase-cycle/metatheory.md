---
path: docs/skills/n-phase-cycle/metatheory
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Meta Skill: Metatheory of the N-Phase Cycle

> *"The 'N' is not a number—it is a variable. The cycle adapts to the task."*

**Difficulty**: High
**Prerequisites**: `spec/principles.md`, all phase skills, familiarity with decision and learning theory
**Files Touched**: This file is reference; modifications via `meta-skill-operad.md`

---

## Why "N-Phase"?

The cycle is named N-Phase because:

1. **Variable granularity**: Some tasks need 3 phases (SENSE→ACT→REFLECT), others need 11, others need 2
2. **Domain agnostic**: Different domains may discover different optimal phase counts
3. **Evolutionary**: The cycle itself can add/remove/merge phases over time
4. **Self-similar**: Each phase contains a hologram of the full cycle, so N can nest

The number is not sacred. The **structure** is sacred:
- **Intention before action** (SENSE family)
- **Action with verification** (ACT family)
- **Learning from outcomes** (REFLECT family)

---

## Metatheoretical Grounding

The N-Phase Cycle is not invented from nothing. It synthesizes established frameworks:

### 1. OODA Loop (Boyd, 1970s)

**Observe → Orient → Decide → Act**

Military decision cycle for competitive advantage. Key insight: the faster you cycle, the more you shape the environment.

| OODA | N-Phase Mapping |
|------|-----------------|
| Observe | RESEARCH (data gathering) |
| Orient | DEVELOP, STRATEGIZE (framing, context) |
| Decide | CROSS-SYNERGIZE (composition selection) |
| Act | IMPLEMENT, QA, TEST |

**What OODA contributes**: Speed through iteration. "Tempo" as competitive edge. The loop doesn't end—it perpetuates.

**Source**: [OODA Loop - Wikipedia](https://en.wikipedia.org/wiki/OODA_loop)

---

### 2. PDCA / Deming Cycle (Shewhart, 1920s; Deming, 1950s)

**Plan → Do → Check → Act**

Quality improvement cycle. Key insight: treat action as hypothesis testing.

| PDCA | N-Phase Mapping |
|------|-----------------|
| Plan | PLAN, DEVELOP, STRATEGIZE |
| Do | IMPLEMENT |
| Check | QA, TEST, MEASURE |
| Act | REFLECT, Re-Metabolize |

**What PDCA contributes**: Continuous improvement. No "done"—only "better". The cycle is a **control loop** with feedback.

**Source**: [PDCA Cycle - ASQ](https://asq.org/quality-resources/pdca-cycle)

---

### 3. Double-Loop Learning (Argyris & Schön, 1970s)

**Single-loop**: Change actions to fix error.
**Double-loop**: Change governing variables (goals, values, frames) to fix error.

| Learning Type | N-Phase Mapping |
|---------------|-----------------|
| Single-loop | IMPLEMENT → QA → fix → retry |
| Double-loop | REFLECT → PLAN revision → RESEARCH reframe |

**What double-loop contributes**: The ability to question the question. REFLECT doesn't just ask "did we do it right?" but "are we doing the right thing?"

The `lookback-revision.md` skill operationalizes double-loop learning.

**Source**: [Double-Loop Learning - infed.org](https://infed.org/dir/welcome/chris-argyris-theories-of-action-double-loop-learning-and-organizational-learning/)

---

### 4. Reflection-in-Action (Schön, 1983)

**Reflection-on-action**: After the fact.
**Reflection-in-action**: During the act, adjusting in real-time.

| Reflection Type | N-Phase Mapping |
|-----------------|-----------------|
| Reflection-on-action | REFLECT phase at end of cycle |
| Reflection-in-action | Recursive hologram within each phase |

**What Schön contributes**: The insight that every phase contains its own micro-cycle. IMPLEMENT contains sensing, acting, reflecting—just at smaller scale.

---

### 5. Category Theory (Compositional Structure)

Phases are **morphisms** in a category where:
- **Objects**: Phase boundaries (states of knowledge)
- **Morphisms**: Phase executions (transformations)
- **Composition**: `(A >> B) >> C ≡ A >> (B >> C)` (associativity)
- **Identity**: Empty phase (pass-through)

| Category Concept | N-Phase Mapping |
|------------------|-----------------|
| Morphism | Phase execution |
| Composition | Phase chaining |
| Functor | Cycle embedding (11 → 3 → 11) |
| Natural transformation | Cycle evolution over time |

**What category theory contributes**: The **lawfulness** of composition. Any mutation to phases must preserve identity and associativity. This prevents drift and ensures the cycle remains coherent.

**Source**: [Category Theory - Wikipedia](https://en.wikipedia.org/wiki/Category_theory)

---

### 6. Kaizen (Continuous Improvement)

Not a cycle but a **mindset**: small, frequent improvements compound into significant change.

**What Kaizen contributes**: The 5-10% Accursed Share in each phase. Exploration is not waste—it's the source of all improvement.

**Source**: [PDCA and Kaizen - The Lean Way](https://theleanway.net/the-continuous-improvement-cycle-pdca)

---

## The Synthesis

The N-Phase Cycle is the intersection of these frameworks:

```
                    ┌─────────────────────────────────────────┐
                    │           N-PHASE CYCLE                 │
                    │                                         │
    OODA (tempo)    │   PDCA (control)   Argyris (double-loop)│
    ───────────────►│◄────────────────   ────────────────────►│
                    │                                         │
    Category Theory │   Schön (reflection)   Kaizen (entropy) │
    ───────────────►│◄────────────────   ────────────────────►│
                    │                                         │
                    │   = Self-similar, composable, adaptive  │
                    │     lifecycle for agent-human work      │
                    └─────────────────────────────────────────┘
```

---

## Optimal Phase Count

| Context | Optimal N | Phases Used |
|---------|-----------|-------------|
| Trivial (typo) | 0 | Direct action |
| Quick win (bug fix) | 2 | ACT → REFLECT |
| Standard feature | 3 | SENSE → ACT → REFLECT |
| Multi-session feature | 7 | PLAN → RESEARCH → DEVELOP → IMPLEMENT → TEST → MEASURE → REFLECT |
| Crown Jewel (multi-week) | 11 | Full cycle |
| Meta-work (cycle evolution) | 11+ | Full cycle + Re-Metabolize |

**Principle**: Start with 3 phases. Expand only when complexity demands.

---

## The Flexibility Invariant

While N is variable, these properties are **invariant**:

1. **Intention precedes action** — No IMPLEMENT without some SENSE
2. **Action produces artifacts** — Phases have outputs, not just activities
3. **Reflection feeds forward** — Learnings propagate to next cycle
4. **Entropy budget exists** — Every phase reserves exploration capacity
5. **Continuity is explicit** — Every phase generates the next prompt
6. **Laws hold** — Identity, associativity, branching rules

Any instantiation of the N-Phase Cycle must satisfy these invariants. A "3-phase cycle" that lacks reflection is **not** a valid instantiation.

---

## Evolution Mechanism

The cycle evolves via `meta-re-metabolize.md`:

1. REFLECT surfaces staleness or drift
2. Meta-re-metabolize triggers re-ingestion of all phase skills
3. Mutations applied via `meta-skill-operad.md`
4. Laws verified (identity/associativity)
5. Updated cycle deployed

The N-Phase Cycle is **autopoietic**—it maintains and reproduces itself through its own operations.

---

## Recursive Hologram

This metatheory skill applies to itself:

- PLAN: Define the theoretical grounding
- RESEARCH: Survey decision theory, learning theory, category theory
- DEVELOP: Synthesize into coherent framework
- IMPLEMENT: Write this document
- TEST: Do the metatheoretical claims hold in practice?
- REFLECT: Are the cited frameworks accurately represented?

---

## Sources

- [OODA Loop - Wikipedia](https://en.wikipedia.org/wiki/OODA_loop)
- [PDCA Cycle - ASQ](https://asq.org/quality-resources/pdca-cycle)
- [Double-Loop Learning - infed.org](https://infed.org/dir/welcome/chris-argyris-theories-of-action-double-loop-learning-and-organizational-learning/)
- [Reflective Practitioner - Schön, 1983](https://en.wikipedia.org/wiki/The_Reflective_Practitioner)
- [Category Theory - Wikipedia](https://en.wikipedia.org/wiki/Category_theory)
- [Kaizen and PDCA - The Lean Way](https://theleanway.net/the-continuous-improvement-cycle-pdca)

---

## Related Skills

- `auto-continuation.md` — How the cycle perpetuates
- `meta-skill-operad.md` — Lawful cycle mutation
- `meta-re-metabolize.md` — Periodic cycle refresh
- `lookback-revision.md` — Double-loop operationalized
- `three-phase.md` — The 3-phase compression

---

## Changelog

- 2025-12-13: Initial version (per user request to formalize metatheory grounding).
