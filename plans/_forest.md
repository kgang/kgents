# Forest Health: 2025-12-13 (Night Reconciliation)

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`. For detailed component-level status, read `_status.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| agents/k-gent | 97% | active | 589 tests. Session/cache added. Deferred: Fractal, Holographic. |
| self/memory | 40% | active | Four Pillars + Substrate AGENTESE wired. Real substrate wiring next. |
| self/memory-phase5-substrate | 0% | proposed | Shared substrate architecture. N-Phase Cycle: Full 11-phase. |
| architecture/turn-gents | 100% | complete | Chronos-Kairos Protocol. 187 tests. All 7 phases complete. |
| devex/hotdata-infrastructure | 100% | complete | HotData core + CLI + 11 fixtures + Dashboard consolidation done. |
| interfaces/dashboard-consolidation | 100% | complete | The dashboard IS the demo. Standalone script removed. |
| interfaces/dashboard-textual-refactor | 0% | proposed | EventBus, Base Screen, Mixins (zenportal patterns). Fix key eating. |

---

## Dormant Trees

| Plan | Progress | Last Touched | Notes |
|------|----------|--------------|-------|
| agents/t-gent | 90% | 2025-12-12 | Types I-IV complete, Type V (AdversarialGym) remaining. |
| void/entropy | 95% | 2025-12-13 | 87 tests. FeverOverlay done. Only trigger wiring remaining. |

---

## Archived-Partial Trees

| Plan | Progress | Notes |
|------|----------|-------|
| self/cli-refactor | 75% | Reflector+FD3 done. ProposalQueue remaining. |

---

## Blocked Trees

*(none)*

---

## Recently Archived (2025-12-13 DevEx Audit)

| Plan | Archive Path | Tests | Notes |
|------|--------------|-------|-------|
| DevEx Dashboard | `_archive/dashboard-v1.0-complete.md` | 74 | `kg dashboard` — 4-panel TUI |
| DevEx Trace Integration | `_archive/trace-integration-v1.0-complete.md` | 101+ | TraceDataProvider, 8 integrations |
| DevEx Watch Mode | `_archive/watch-mode-v1.0-complete.md` | 28 | `kg soul watch` — 5 heuristics |
| DevEx Gallery | `_archive/gallery-v1.0-complete.md` | — | MkDocs site, 6 examples |
| DevEx Telemetry | `_archive/telemetry-v1.0-complete.md` | 50 | O-gent Dim X: OTEL spans, metrics |
| Polyfunctor | `_archive/polyfunctor-v1.0-complete.md` | 201 | All 4 phases, 4 agent polynomials |
| DevEx Playground | `_archive/playground-v1.0-complete.md` | 32 | `kg play` — Interactive tutorials |
| DevEx Scaffolding | `_archive/scaffolding-v1.0-complete.md` | — | `kg new` — Agent generator |
| DevEx Trace | `_archive/trace-v1.0-complete.md` | 252 | StaticCallGraph, RuntimeTrace |
| Alethic Architecture | `_archive/alethic-v1.0-complete.md` | 337 | Functor, Halo, Archetypes |
| Categorical Consolidation | `_archive/categorical-consolidation-v1.0-complete.md` | — | Symmetric lifting |
| Agent Semaphores | `_archive/semaphores-v1.0-complete.md` | 182 | Rodizio pattern |
| Terrarium | `_archive/terrarium-v1.0-complete.md` | 176+ | Mirror Protocol, K8s |
| Self Stream | `_archive/stream-v1.0-complete.md` | 302 | ContextWindow, ModalScope |
| Concept Lattice | `_archive/lattice-v1.0-complete.md` | 69 | Lineage enforcement |
| Concept Creativity | `_archive/creativity-v2.5-complete.md` | 146+ | PAYADOR, Pataphysics |
| Cluster Native Runtime | `_archive/cluster-native-runtime-v1.0-complete.md` | 145 | K8sProjector |

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 3 |
| Complete | 4 |
| Proposed | 2 |
| Dormant | 2 |
| Archived-partial | 1 |
| Blocked | 0 |
| Newly archived | 19 |
| Tests | 13,210 |
| Mypy (prod) | 0 errors |
| Last verified | 2025-12-13 night (Chief reconciliation) |

---

## Session Attention Budget

Aligned with `_focus.md` (2025-12-13):

| Category | Allocation | Trees |
|----------|------------|-------|
| Visual UIs/Refined Interactions | 50% | turn-gents, k-gent |
| Self/Memory | 30% | memory |
| Accursed Share | 20% | exploration, entropy |

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
architecture/polyfunctor (ARCHIVED) ──enables──▶ architecture/turn-gents (100% COMPLETE)

devex/trace (ARCHIVED) ──enables──▶ devex/trace-integration (ARCHIVED)
devex/trace (ARCHIVED) ──enables──▶ devex/telemetry (ARCHIVED)
devex/trace-integration (ARCHIVED) ──enhances──▶ devex/dashboard (ARCHIVED)
devex/telemetry (ARCHIVED) ──realizes──▶ spec/o-gents Dimension X
devex/playground (ARCHIVED) ──enables──▶ devex/gallery (ARCHIVED)
devex/dashboard (ARCHIVED) ──uses──▶ agents/k-gent (collectors)
devex/watch-mode (ARCHIVED) ──uses──▶ agents/k-gent (heuristics)

devex/hotdata-infrastructure (COMPLETE) ──enables──▶ interfaces/dashboard-consolidation (COMPLETE)
interfaces/dashboard-consolidation (COMPLETE) ──consumes──▶ devex/dashboard (ARCHIVED)
interfaces/dashboard-textual-refactor (PROPOSED) ──refines──▶ interfaces/dashboard-consolidation (COMPLETE)
interfaces/dashboard-textual-refactor (PROPOSED) ──ports-from──▶ zenportal (EventBus, Base Screen, Mixins)

## Turn-gents Synergies (NEW)

architecture/turn-gents (100% COMPLETE) ──integrates──▶
├── self/memory (Phase 7: CausalConeAgent, TraceMemory)
├── interfaces/dashboard-overhaul (Debugger Screen LOD 2, TurnDAGRenderer)
├── agents/k-gent (Soul intercept via TurnBasedCapability)
└── polynomial-agent (State transitions emit Turns)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
