# Forest Health: 2025-12-12

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| self/stream | 75% | active | Phase 2.2 DONE (ModalScope), 2.3-2.4 remaining |
| agents/k-gent | new | active | Categorical Imperative - LLM-backed dialogue, deep intercept |
| architecture/alethic-algebra | 20% | active | Phase 1 DONE (UniversalFunctor), Phases 2-5 remaining |
| infra/cluster-native-runtime | 100% | complete | All phases done - PVC, DgentClient, integration tests |

---

## Dormant Trees

| Plan | Progress | Last Touched | Notes |
|------|----------|--------------|-------|
| agents/t-gent | 90% | 2025-12-12 | Type V Adversarial remaining |
| void/entropy | 70% | 2025-12-12 | CLI tithe done; TUI remaining |

---

## Archived-Partial Trees

| Plan | Progress | Notes |
|------|----------|-------|
| self/cli-refactor | 75% | Reflector+FD3 done. ProposalQueue remaining. See `docs/cli-refactor-assessment.md` |

---

## Blocked Trees

| Plan | Progress | Blocked By | Notes |
|------|----------|------------|-------|
| self/memory | 30% | self/stream | Ghost cache done; StateCrystal awaits Phase 2.4 |

---

## Recently Archived

| Plan | Archive Path | Tests | Notes |
|------|--------------|-------|-------|
| Cluster-Native Runtime | `infra/cluster-native-runtime.md` | 24+ | PVC, DgentClient, U-gent + D-gent integration |
| Terrarium | `agents/terrarium.md` | 176+ | Mirror Protocol, K8s Operator, Purgatory |
| Agent Semaphores | `agents/semaphores.md` | 182 | Rodizio pattern complete |
| Creativity v2.5 | `concept/creativity.md` | 146+ | PAYADOR, Curator, Pataphysics |
| Lattice | `concept/lattice.md` | 69 | Lineage enforcement complete |
| Flux Functor | `_archive/flux-functor-v1.0-complete.md` | 261 | Living Pipelines via `\|` |
| I-gent v2.5 | `_archive/igent-v2.5-complete.md` | 137 | Phases 1-5 complete |

---

## Session Attention Budget

Per `plans/principles.md` §3 and `_focus.md`:

```
Primary (50%):    agents/k-gent (Categorical Imperative - LLM-backed governance)
Secondary (30%):  self/stream (Phases 2.3-2.4: Pulse, Crystal)
Maintenance (15%): Check blocked/dormant trees
Accursed (5%):    Joy-inducing polish
```

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 3 |
| Dormant | 2 |
| Blocked | 1 |
| Recently archived | 7 |
| Tests | 9,699 |

---

## Dependency Graph

```
self/memory (30%) ◀── blocked by ── self/stream (75%)
concept/lattice (100%) ──enables──▶ concept/creativity (100%)
void/entropy (70%) ── done ── Flux integration + CLI tithe
agents/semaphores (100%) ──enables──▶ void/entropy (metabolism pressure)
agents/terrarium (100%) ──uses──▶ agents/semaphores (Purgatory)
agents/k-gent (new) ──uses──▶ agents/semaphores (Rodizio Sommelier)
infra/cluster-native-runtime (100%) ──enables──▶ agents/k-gent (standard API)
architecture/alethic-algebra (20%) ──enables──▶ agents/k-gent (Guard functor)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
