# Forest Health: 2025-12-13 (Evening Update)

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| agents/k-gent | 97% | active | 589 tests. Session/cache added. Deferred: Fractal, Holographic. |
| self/memory | 30% | active | UNBLOCKED. Ghost cache done, crystals next. |
| architecture/turn-gents | 0% | proposed | Chronos-Kairos Protocol. Turn as causal morphism. |
| architecture/polyfunctor | 100% | **COMPLETE** | 201 tests. All 4 phases done. Ready for archive. |

---

## Planned Trees (DevEx Initiative)

| Plan | Priority | Status | Notes |
|------|----------|--------|-------|
| devex/dashboard | 1 | **COMPLETE** | `kg dashboard` — 4-panel TUI, collectors, graceful degradation |
| devex/trace-integration | 2 | planned | Trace into Dashboard, Ghost, Flinch, Status, MRI |
| devex/watch-mode | 3 | **COMPLETE** | `kg soul watch` — 5 heuristics, watchdog, 28 tests |
| devex/gallery | 4 | **COMPLETE** | MkDocs site, 6 examples, Material theme, GitHub Actions |
| devex/telemetry | 5 | planned | OpenTelemetry export |

---

## Dormant Trees

| Plan | Progress | Last Touched | Notes |
|------|----------|--------------|-------|
| agents/t-gent | 90% | 2025-12-12 | Types I-IV complete, Type V (AdversarialGym) remaining. |
| void/entropy | 85% | 2025-12-13 | 69 tests. CLI tithe done. Only TUI FeverOverlay remaining. |

---

## Archived-Partial Trees

| Plan | Progress | Notes |
|------|----------|-------|
| self/cli-refactor | 75% | Reflector+FD3 done. ProposalQueue remaining. |

---

## Blocked Trees

*(none)*

---

## Recently Archived (2025-12-13 Audit)

| Plan | Archive Path | Tests | Notes |
|------|--------------|-------|-------|
| DevEx Playground | `_archive/playground-v1.0-complete.md` | 32 | `kgents play` — Interactive tutorials |
| DevEx Scaffolding | `_archive/scaffolding-v1.0-complete.md` | — | `kgents new` — Agent generator |
| DevEx Trace | `_archive/trace-v1.0-complete.md` | 252 | StaticCallGraph, RuntimeTrace, CLI |
| Alethic Architecture | `_archive/alethic-v1.0-complete.md` | 337 | Functor, Halo, Archetypes, Projectors |
| Categorical Consolidation | `_archive/categorical-consolidation-v1.0-complete.md` | — | Symmetric lifting, ObserverFunctor |
| Agent Semaphores | `_archive/semaphores-v1.0-complete.md` | 182 | Rodizio pattern, Phases 1-6 |
| Terrarium | `_archive/terrarium-v1.0-complete.md` | 176+ | Mirror Protocol, K8s Operator |
| Self Stream | `_archive/stream-v1.0-complete.md` | 302 | ContextWindow, ModalScope, Pulse, Crystal |
| Concept Lattice | `_archive/lattice-v1.0-complete.md` | 69 | Lineage enforcement |
| Concept Creativity | `_archive/creativity-v2.5-complete.md` | 146+ | PAYADOR, Curator, Pataphysics |
| Cluster Native Runtime | `_archive/cluster-native-runtime-v1.0-complete.md` | 145 | K8sProjector, LocalProjector |

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 3 |
| DevEx complete | 3 (dashboard, watch-mode, gallery) |
| DevEx planned | 2 (trace-integration, telemetry) |
| Dormant | 2 |
| Archived-partial | 1 |
| Ready for archive | 4 (polyfunctor, dashboard, watch-mode, gallery) |
| Blocked | 0 |
| Newly archived | 11 |
| Tests | 12,015 |
| Mypy (prod) | 0 errors |
| Last verified | 2025-12-13 (Chief reconciliation) |

---

## Dependency Graph

```
self/stream (ARCHIVED) ──enables──▶ self/memory (30% ACTIVE)
concept/lattice (ARCHIVED) ──enables──▶ concept/creativity (ARCHIVED)
void/entropy (85% DORMANT) ── Flux integration + CLI tithe
agents/semaphores (ARCHIVED) ──enables──▶ void/entropy
agents/terrarium (ARCHIVED) ──uses──▶ agents/semaphores
agents/k-gent (97% ACTIVE) ──uses──▶ agents/semaphores
infra/cluster-native-runtime (ARCHIVED) ──enables──▶ agents/k-gent
architecture/alethic (ARCHIVED) ──enables──▶ agents/k-gent
architecture/polyfunctor (COMPLETE) ──enables──▶ architecture/turn-gents (PROPOSED)
architecture/turn-gents (PROPOSED) ──enables──▶ devex/trace-integration (PLANNED)

devex/trace (ARCHIVED) ──enables──▶ devex/trace-integration (PLANNED)
devex/trace (ARCHIVED) ──enables──▶ devex/telemetry (PLANNED)
devex/trace-integration (PLANNED) ──enhances──▶ devex/dashboard (COMPLETE)
devex/playground (ARCHIVED) ──enables──▶ devex/gallery (COMPLETE)
devex/dashboard (COMPLETE) ──uses──▶ agents/k-gent (collectors)
devex/watch-mode (COMPLETE) ──uses──▶ agents/k-gent (heuristics)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
