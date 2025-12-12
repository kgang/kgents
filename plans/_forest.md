# Forest Health: 2025-12-12

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| self/stream | 75% | active | Phase 2.2 DONE, 2.3-2.4 remaining |

---

## Dormant Trees

| Plan | Progress | Last Touched | Notes |
|------|----------|--------------|-------|
| agents/t-gent | 90% | 2025-12-12 | Type V Adversarial remaining |
| agents/semaphores | 20% | 2025-12-12 | Phase 1 done (78 tests). Rodizio Pattern. |
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
| Creativity v2.5 | `concept/creativity.md` | 146+ | PAYADOR, Curator, Pataphysics |
| Lattice | `concept/lattice.md` | 69 | Lineage enforcement complete |
| Flux Functor | `_archive/flux-functor-v1.0-complete.md` | 261 | Living Pipelines via `\|` |
| I-gent v2.5 | `_archive/igent-v2.5-complete.md` | 137 | Phases 1-5 complete |
| Reflector | `_archive/reflector-v1.0-complete.md` | 36 | Terminal/Headless/Flux |
| U-gent Migration | `_archive/u-gent-migration-v1.0-complete.md` | — | Tool code split from T-gent |

---

## Session Attention Budget

Per `plans/principles.md` §3 and `_focus.md`:

```
Primary (60%):    concept/creativity (Tasks 2-4 polish)
Secondary (25%):  self/stream (Phases 2.2-2.4)
Maintenance (10%): Check blocked/dormant trees
Accursed (5%):    agents/semaphores (explore Purgatory)
```

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 1 |
| Dormant | 3 |
| Blocked | 1 |
| Recently archived | 6 |
| Tests | 8,938 |

---

## Dependency Graph

```
self/memory (30%) ◀── blocked by ── self/stream (75%)
concept/lattice (100%) ──enables──▶ concept/creativity (100%)
void/entropy (70%) ── done ── Flux integration + CLI tithe
agents/semaphores (20%) ──enables──▶ void/entropy (metabolism pressure)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
