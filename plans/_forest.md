# Forest Health: 2025-12-12

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| agents/k-gent | 60% | active | Phases 1-3 COMPLETE, Phase 4 (Hypnagogia) next |
| architecture/alethic | 70% | active | Phases 1-3 COMPLETE (Functor, Halo, Archetypes), Phases 4-6 remaining |

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
| *(none)* | - | - | self/memory is now UNBLOCKED (self/stream complete) |

---

## Recently Archived

| Plan | Archive Path | Tests | Notes |
|------|--------------|-------|-------|
| self/stream | `self/stream.md` | 302 | Phases 2.1-2.4 ALL COMPLETE: ContextWindow, ModalScope, Pulse, Crystal |
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
Primary (50%):    agents/k-gent Phase 2 (KgentFlux, events, Terrarium wire)
Secondary (30%):  self/memory (UNBLOCKED by self/stream)
Exploration (15%): Terrarium Phase 3 (metrics for I-gent widgets)
Accursed (5%):    Joy-inducing polish
```

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 2 |
| Dormant | 2 |
| Blocked | 0 |
| Recently archived | 8 |
| Tests | 9,990 |
| Last verified | 2025-12-12 |

---

## Dependency Graph

```
self/stream (100%) ──enables──▶ self/memory (UNBLOCKED)
concept/lattice (100%) ──enables──▶ concept/creativity (100%)
void/entropy (70%) ── done ── Flux integration + CLI tithe
agents/semaphores (100%) ──enables──▶ void/entropy (metabolism pressure)
agents/terrarium (100%) ──uses──▶ agents/semaphores (Purgatory)
agents/k-gent (60%) ──uses──▶ agents/semaphores (Rodizio Sommelier)
infra/cluster-native-runtime (100%) ──enables──▶ agents/k-gent (standard API)
architecture/alethic (70%) ──enables──▶ agents/k-gent (SoulFunctor integration)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
