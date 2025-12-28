# HYDRATE.md — The Seed

> *"To read is to invoke. There is no view from nowhere."*

Minimal context for agents. For humans: start with [README.md](README.md).

---

## FIRST: Get Task-Relevant Gotchas

```bash
kg docs hydrate "<your task>"
```

This surfaces critical gotchas, likely files, and voice anchors for YOUR specific task.

---

## THE ONE TRUTH

**All plans consolidated to**: `plans/enlightened-synthesis/`

```
00-master-synthesis.md       ← Master vision (READ FIRST)
01-theoretical-amendments.md ← 7 amendments
02-execution-roadmap.md      ← 8-week pilot-grounded plan
03-risk-mitigations.md       ← 47 vulnerabilities
04-joy-integration.md        ← Joy calibration by domain
05-product-strategy.md       ← Consumer-first path
```

---

## Principles

**Tasteful** • **Curated** • **Ethical** • **Joy-Inducing** • **Composable** • **Heterarchical** • **Generative**

**Amendment A (2025-12-26)**: ETHICAL is a floor constraint (≥0.6 required), not a weighted principle.

Full specification: [spec/principles.md](spec/principles.md)

---

## AGENTESE (Five Contexts)

`world.*` `self.*` `concept.*` `void.*` `time.*`

**Aspects**: `manifest` • `witness` • `refine` • `sip` • `tithe` • `lens` • `define`

```python
await logos.invoke("world.house.manifest", umwelt)  # Observer-dependent
```

---

## Galois Loss Framework

The core theoretical innovation:

```python
L(P) = d(P, C(R(P)))

# Where:
# R: Restructure via LLM (break into components)
# C: Reconstitute via LLM (rebuild from components)
# d: Semantic distance (BERTScore → cosine → fallback)
```

**Capabilities**:
- Axiom detection: `L < 0.05` = fixed point
- Layer assignment: L1-L7 via loss thresholds
- Contradiction detection: super-additivity signals tension

---

## Crown Jewels (Post-Consolidation)

| Jewel | Status | Purpose |
|-------|--------|---------|
| Witness | 98% | Mark, Crystal, Grant, Playbook (678 tests) |
| Zero Seed | 85% | Galois Loss, Layer Assignment |
| K-Block | 75% | Monad bind, Layer Factories |
| Constitutional | 80% | 7-principle scoring, Amendment A |
| Brain | 100% | Spatial cathedral of memory |

---

## Witness: Marks & Decisions

> *"The proof IS the decision. The mark IS the witness."*

### Mark Moments (`km`)

```bash
km "what happened"                         # Basic mark
km "insight" --reasoning "why it matters"  # With justification
km "gotcha" --tag gotcha --tag agentese    # Tagged for retrieval
km "action" --json                         # Machine-readable
```

### Record Decisions (`kg decide`)

```bash
# Quick decision
kg decide --fast "choice" --reasoning "why"

# Full dialectic (Kent + Claude differ)
kg decide --kent "view" --kent-reasoning "why" \
          --claude "view" --claude-reasoning "why" \
          --synthesis "fusion" --why "justification"
```

### Query & Crystallize

```bash
kg witness show --today                # Today's marks
kg witness crystallize                 # Marks → Session crystal
```

---

## Current Execution: 5 Pilots

| Pilot | Domain | Joy | Status |
|-------|--------|-----|--------|
| **trail-to-crystal-daily-lab** | Productivity | FLOW | Week 6 (FIRST) |
| wasm-survivors-game | Gaming | FLOW | Week 7 |
| disney-portal-planner | Consumer | WARMTH | Week 8 |
| rap-coach-flow-lab | Creative | SURPRISE | Week 7 |
| sprite-procedural-taste-lab | Generative | SURPRISE | Week 8 |

**Wedge**: `trail-to-crystal` — "Turn your day into proof of intention"

---

## Commands

```bash
# Backend
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend
cd impl/claude/web && npm run typecheck && npm run lint
```

---

## Voice Anchors

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"The Mirror Test: Does K-gent feel like me on my best day?"*
> *"Tasteful > feature-complete; Joy-inducing > merely functional"*
> *"Depth over breadth"*

---

*Lines: 120. Ceiling: 150.*
