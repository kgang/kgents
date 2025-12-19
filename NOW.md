# NOW.md — What's Happening

> *Updated each session. No metadata. Just truth.*
> *Claude reads this first, updates it before ending.*

---

## Current Work

**KGENTSD: THE 8TH CROWN JEWEL** — Ghost→kgentsd transformation. Event-driven daemon with Trust Level 3 (full Kent autonomy). See `plans/kgentsd-crown-jewel.md`.

| Plan | Status | Key Focus |
|------|--------|-----------|
| `plans/kgentsd-crown-jewel.md` | **EXECUTING (Phase 0.5)** | Vertical slice: Git Watcher end-to-end |

**Phase 0.5 Progress** (Vertical Slice):
- ✅ `services/witness/` Crown Jewel created
- ✅ `WitnessPolynomial` (trust-gated state machine, 29 tests passing)
- ✅ `WITNESS_OPERAD` (merged with AGENT_OPERAD, 5 witness operations, 3 laws)
- ✅ `GitWatcher` (event-driven, no timers)
- ✅ **`WitnessPersistence`** (dual-track: D-gent + SQLAlchemy, 19 tests passing)
- ✅ **`WitnessNode`** (AGENTESE @node("self.witness"), 7 aspects)
- ✅ **SQLAlchemy models** (WitnessTrust, WitnessThought, WitnessAction, WitnessEscalation)
- ✅ **Service registration** (bootstrap.py, providers.py)
- 🔲 CLI handler (`kg witness *` commands)

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
| **Witness** | 60 | **8TH JEWEL**. Polynomial + Operad + Persistence + Node complete (48 tests). Needs CLI. |
| Domain | 0 | Enterprise. Dormant. |

---

**MULTI-AGENT CI SAFETY** — Sentinel patterns for safe multi-agent development.

| Phase | Status | Key Focus |
|-------|--------|-----------|
| Phase 2 | ✅ **COMPLETE** | Blocking hooks, validation scripts, ci-parity-check |
| Phase 3 | ✅ **COMPLETE** | Sentinel testing infrastructure (76 tests) |

**Phase 2 Deliverables** (commit `d86b5b08`):
- ✅ Make lint/mypy BLOCKING in pre-push hook
- ✅ `scripts/validate.sh` — unified developer validation (Tier 2)
- ✅ `scripts/ci-parity-check.sh` — environment functor checking
- ✅ Gated contract sync (only when API files change)

**Phase 3 Deliverables** (commit `42f97f40`):
- ✅ `testing/sentinel/` module with signal aggregation, degradation tiers, isolation morphism
- ✅ 76 tests: `evaluate_push_readiness()`, tier fallback, registry isolation
- ✅ `@pytest.mark.sentinel` marker registered

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
| Multi-Agent CI Safety Phase 2-3 | 2025-12-19 | `testing/sentinel/` |

---

*Last: 2025-12-19 (CI Safety Phase 2-3: blocking hooks, validation scripts, 76 sentinel tests)*
