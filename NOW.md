# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**KGENTSD: THE 8TH CROWN JEWEL** — Ghost→kgentsd transformation. Event-driven daemon with Trust Level 3 (full Kent autonomy). See `plans/kgentsd-crown-jewel.md`.

| Plan | Status | Key Focus |
|------|--------|-----------|
| `plans/kgentsd-crown-jewel.md` | **Phase 2 IN PROGRESS** | Cross-jewel handlers, bus wiring |

**Phase 1 Complete** (Event-Driven Flux Integration):
- ✅ `GitWatcherFlux` (DORMANT → FLOWING → STOPPED state machine, 9 tests)
- ✅ `WitnessSynergyBus` + `WitnessEventBus` (three-bus architecture, 15 tests)
- ✅ `WitnessBusManager` (orchestrator with cross-jewel wiring)
- ✅ Daemon is now pure event publisher (no HTTP coupling)
- ✅ 72 witness tests passing, mypy clean

**Phase 2 Progress** (Cross-Jewel Awakening):
- ✅ `Jewel.WITNESS` added to synergy events
- ✅ 5 new event types: `WITNESS_THOUGHT_CAPTURED`, `WITNESS_GIT_COMMIT`, etc.
- ✅ `WitnessToBrainHandler` (thoughts → crystals, auto-capture)
- ✅ `WitnessToGardenHandler` (commits → plot updates)
- ✅ `wire_witness_to_global_synergy()` bridge function
- ✅ `register_witness_handlers()` for global bus
- ✅ 18 new handler tests (90 total witness-related tests)
- 🔲 CLI handler (`kg witness logs` command)

---

**UMWELT V2 EXPANSION** — Observer reality deepening. See `plans/umwelt-v2-expansion.md`.

| Phase | Status | Key Focus |
|-------|--------|-----------|
| Phase 0 | ✅ **COMPLETE** | Correctness foundation: registry-backed capabilities |
| Phase 1 | NEXT | Education: PathExplorer dimming, Ghost interaction |

**Phase 0 Deliverables** (2025-12-19):
- ✅ `@aspect(required_capability=...)` decorator v3.3
- ✅ `/discover` returns per-aspect `aspectMetadata` with `requiredCapability`
- ✅ Frontend: `getRequiredCapability()` uses registry with heuristic fallback
- ✅ Frontend: `hasContract` wired from aspect metadata
- ✅ `useObserverPersistence` hook created

---

**AGENTESE NODE OVERHAUL** — Sessions 1-6 + Phases 4-5 COMPLETE. See `plans/agentese-node-overhaul-strategy.md`.

| Session | Status | Key Deliverables |
|---------|--------|------------------|
| Sessions 1-6 | ✅ | Projections, Gardener/Soul wiring, Park Scenarios, SSE Streaming |
| **Session 7** | **NEXT** | **Neutral Error UX** — consistent errors, actionable hints |
| Sessions 8-10 | Pending | Observer audit, CI gates, E2E tests |

---

## Crown Jewel Status

| Jewel | % | One-liner |
|-------|---|-----------|
| Brain | 100 | Spatial cathedral of memory. Ship-ready. |
| Gardener | 100 | Cultivation practice. Ship-ready. |
| Gestalt | 85 | Living garden where code breathes. Gestalt2D complete. |
| Forge | 85 | Phase 1-4 done. Four creative artisans do real work. |
| Town/Coalition | 70 | Workshop where agents collaborate. Dialogue complete. |
| Park | 60 | Westworld where hosts can say no. Scenarios + Consent Debt complete. |
| **Witness** | 75 | **8TH JEWEL**. Phase 2: Cross-jewel handlers + bus wiring (90 tests). Just needs CLI. |
| Domain | 0 | Enterprise. Dormant. |

---

## What I'm Stuck On

**Voice dilution** — The project is losing its edge through LLM processing. Each Claude session smooths a little. Added Anti-Sausage Protocol to CLAUDE.md to address this.

---

## What I Want Next

**Metaphysical Forge Phase 5**: Sentinel (security review) and Witness (test generation) artisans. Plus SSE streaming for real-time progress and cross-jewel wiring (Brain capture, Gardener plots).

*"The Forge is where we build ourselves."*

---

## Key Completions (Reference)

These are DONE and documented elsewhere:

| Feature | Completion | Documentation |
|---------|------------|---------------|
| 2D Renaissance | 2025-12-18 | `spec/protocols/2d-renaissance.md` |
| AGENTESE-as-Route | 2025-12-18 | `spec/protocols/agentese-as-route.md` |
| Différance Engine | 2025-12-18 | `docs/systems-reference.md` |
| Metaphysical Forge Phase 1-4 | 2025-12-18 | `spec/protocols/metaphysical-forge.md` |
| Habitat 2.0 (Ghost/Examples/Polynomial) | 2025-12-18 | `spec/principles.md` AD-010 |
| AD-012 Aspect Projection Protocol | 2025-12-19 | `spec/principles.md` AD-012 |

---

*Last: 2025-12-19 (Witness Phase 2: Cross-jewel handlers + bus wiring, 90 tests)*
