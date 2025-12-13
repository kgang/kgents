# Forest Health: 2025-12-13 (Chief Reconciliation)

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

**Agent Protocol**: This file is auto-generated from plan YAML headers. Agents may regenerate it but should not add prose. For human intent, read `_focus.md`.

---

## Active Trees

| Plan | Progress | Status | Notes |
|------|----------|--------|-------|
| agents/k-gent | 97% | active | 589 tests. Session/cache added. Deferred: Fractal, Holographic. |
| self/memory | 30% | active | UNBLOCKED by self/stream. Ghost cache done, crystals next. |

---

## Planned Trees (DevEx Initiative)

| Plan | Priority | Status | Notes |
|------|----------|--------|-------|
| devex/playground | 1 | planned | `kgents play` — Interactive tutorials |
| devex/scaffolding | 2 | planned | `kgents new` — Agent generator |
| devex/dashboard | 3 | planned | `kgents dashboard` — Live metrics TUI |
| devex/gallery | 4 | planned | MkDocs example gallery (blocked by playground) |
| devex/watch-mode | 5 | planned | `kgents soul watch` — Ambient K-gent |
| devex/telemetry | 6 | planned | OpenTelemetry export |
| devex/trace | 7 | planned | `kgents trace` — Hybrid static+runtime tracing (enables telemetry, dashboard) |

---

## Dormant Trees

| Plan | Progress | Last Touched | Notes |
|------|----------|--------------|-------|
| agents/t-gent | 90% | 2025-12-12 | 124 tests. Types I-IV complete, Type V (AdversarialGym) remaining. |
| void/entropy | 85% | 2025-12-13 | 69 tests. CLI tithe ✅. Only TUI FeverOverlay remaining. |

---

## Archived-Partial Trees

| Plan | Progress | Notes |
|------|----------|-------|
| self/cli-refactor | 75% | Reflector+FD3 done. ProposalQueue remaining. See `docs/cli-refactor-assessment.md`. |

---

## Blocked Trees

| Plan | Progress | Blocked By | Notes |
|------|----------|------------|-------|
| *(none)* | - | - | - |

---

## Complete Trees (Archived In-Place)

| Plan | Tests | Notes |
|------|-------|-------|
| architecture/alethic | 337 | Phases 1-6 ALL COMPLETE: Functor, Halo, Archetypes, LocalProjector, K8sProjector, CLI |
| self/stream | 302 | Phases 2.1-2.4 ALL COMPLETE: ContextWindow, ModalScope, Pulse, Crystal |
| agents/terrarium | 254 | Mirror Protocol, K8s Operator, Purgatory Integration (ALL 5 PHASES) |
| agents/semaphores | 182 | Rodizio pattern, Phases 1-6 complete |
| agents/i-gent-widgets | 217 | BranchTree, Entropy, GraphLayout, Slider, Sparkline, Timeline, TriadHealth |
| agents/i-gent-data | 149 | Hints, Loom, LOD systems |
| infra/cluster-native-runtime | 145 | K8sProjector, LocalProjector, system infrastructure |
| concept/lattice | 69 | Lineage enforcement complete |
| concept/creativity | 146+ | PAYADOR, Curator, Pataphysics (v2.5 complete) |

---

## Recently Archived (Moved to `_archive/`)

| Plan | Archive Path | Tests | Notes |
|------|--------------|-------|-------|
| Flux Functor | `_archive/flux-functor-v1.0-complete.md` | 382 | Living Pipelines via `|` |
| I-gent v2.5 | `_archive/igent-v2.5-complete.md` | 566 | Full TUI framework |
| Reflector | `_archive/reflector-v1.0-complete.md` | 36 | CLI ↔ TUI bridge |
| K8-Terrarium v2.0 | `_archive/k8-terrarium-v2.0-complete.md` | 24+ | K8s infrastructure |
| CLI Hollowing | `_archive/cli-hollowing-v1.0-complete.md` | 100+ | Handler patterns |
| Capital Ledger | `_archive/capital-ledger-v1.0-complete.md` | 83+ | Event-sourced ledger |

---

## Emerging Work (Tracked in Git Status)

| Work | Tests | Notes |
|------|-------|-------|
| Flux Synapse | 44 | Synapse core + outbox integration |
| Triad Infrastructure | — | K8s manifests, setup scripts |
| Vitals Context | — | AGENTESE vitals path |

---

## Session Attention Budget

Per `plans/principles.md` §3 and `_focus.md`:

```
Primary (50%):    K-gent ambient presence (97% done — polish, deferred features)
Secondary (30%):  self/memory (30% — ready for crystal integration)
Exploration (15%): Fun toys, interactivity, practical demos
Accursed (5%):    Joy-inducing widgets (FeverOverlay is the last one)
```

---

## Forest Metrics

| Metric | Value |
|--------|-------|
| Active trees | 2 |
| Planned (DevEx) | 7 |
| Dormant | 2 |
| Archived-partial | 1 |
| Blocked | 0 |
| Complete (in-place) | 9 |
| Recently archived | 6 |
| Tests | 11,559 |
| Mypy (prod) | 0 errors |
| Last verified | 2025-12-13 (Chief reconciliation #3) |

---

## Dependency Graph

```
self/stream (100%) ──enables──▶ self/memory (30% ACTIVE)
concept/lattice (100%) ──enables──▶ concept/creativity (100%)
void/entropy (85%) ── done ── Flux integration + CLI tithe
agents/semaphores (100%) ──enables──▶ void/entropy (metabolism pressure)
agents/terrarium (100%) ──uses──▶ agents/semaphores (Purgatory)
agents/k-gent (97%) ──uses──▶ agents/semaphores (Rodizio Sommelier)
infra/cluster-native-runtime (100%) ──enables──▶ agents/k-gent (standard API)
architecture/alethic (100%) ──enables──▶ agents/k-gent (SoulFunctor integration)

devex/trace (0%) ──enables──▶ devex/telemetry (OpenTelemetry spans)
devex/trace (0%) ──enables──▶ devex/dashboard (TRACES panel)
weave/trace_monoid (100%) ──enables──▶ devex/trace (Mazurkiewicz foundation)
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
