# Implementation Status Matrix

> Last updated: 2025-12-14 (SaaS Phase 1 complete)

## Legend

| Symbol | Status |
|--------|--------|
| ✅ | Done |
| 🚧 | In Progress |
| 📋 | Planned |

---

## Archived (Complete)

| Plan | Archive Path | Tests |
|------|--------------|-------|
| Lattice | `concept/lattice.md` | 69 |
| Flux Functor | `_archive/flux-functor-v1.0-complete.md` | 382 |
| I-gent v2.5 | `_archive/igent-v2.5-complete.md` | 566 |
| Reflector | `_archive/reflector-v1.0-complete.md` | 36 |
| U-gent Migration | `_archive/u-gent-migration-v1.0-complete.md` | — |
| K8-Terrarium v2.0 | `_archive/k8-terrarium-v2.0-complete.md` | 24+ |
| CLI Hollowing | `_archive/cli-hollowing-v1.0-complete.md` | 100+ |
| Capital Ledger | `_archive/capital-ledger-v1.0-complete.md` | 83+ |

---

## N-Phase Prompt Compiler — 100% COMPLETE ✅

| Component | Status | Tests/Notes |
|-----------|--------|-------------|
| Schema/Parser/Validator | ✅ | `protocols/nphase/schema.py` + `ProjectDefinition.validate` |
| Phase Templates (11) | ✅ | `protocols/nphase/templates/` |
| Compiler | ✅ | `protocols/nphase/compiler.py` |
| State Updater | ✅ | `protocols/nphase/state.py` |
| Operad (compressed phases) | ✅ | `protocols/nphase/operad.py` |
| CLI (`kgents nphase …`) | ✅ | `protocols/cli/handlers/nphase.py` |
| Test Suite | ✅ | `protocols/nphase/_tests` (compiler/schema/state/templates/operad) |
| EDUCATE/MEASURE | ⚠️ pending | Docs/tutorial + metrics hook to be added |

---

## Context Management (`self/stream.md`) — 100% COMPLETE ✅

**ALL PHASES COMPLETE** (302 tests):

| Component | Status | Tests |
|-----------|--------|-------|
| ContextWindow | ✅ | 41 |
| LinearityMap | ✅ | 38 |
| ContextProjector | ✅ | 28 |
| StreamContextResolver | ✅ | 31 |
| MDL Compression | ✅ | 43 |
| ModalScope | ✅ | 44 |
| Pulse + VitalityAnalyzer | ✅ | 35 |
| StateCrystal + CrystallizationEngine + Reaper | ✅ | 42 |

**Archived in place.** self/memory is now UNBLOCKED.

---

## Creativity v2.5 (`concept/creativity.md`) — 100% COMPLETE

| Component | Status | Tests |
|-----------|--------|-------|
| WundtCurator | ✅ | 49 |
| Conceptual Blending | ✅ | — |
| Critic's Loop (PAYADOR) | ✅ | — |
| Contract Melt + Pataphysics | ✅ | 36 |
| MDL Compression | ✅ | 43 |
| Bidirectional Skeleton | ✅ | (in PAYADOR) |
| Wire Pataphysics to LLM | ✅ | 8 |
| Auto-Wire Curator | ✅ | 10 |

---

## Lattice (`concept/lattice.md`) — 100% COMPLETE

| Component | Status |
|-----------|--------|
| LineageChecker | ✅ |
| LineageTracker | ✅ |
| LineageError types | ✅ |
| Wire to concept.*.define | ✅ |
| kgents map --lattice | ✅ |
| 69 tests | ✅ |

---

## T-gent (`agents/t-gent.md`) — 90%

| Component | Status | Tests |
|-----------|--------|-------|
| Types I-IV | ✅ | 124 |
| Type V (AdversarialGym) | 📋 | — |

---

## Entropy/Metabolism (`void/entropy.md`) — 100% COMPLETE ✅

| Component | Status | Tests |
|-----------|--------|-------|
| MetabolicEngine | ✅ | 36 |
| FeverStream | ✅ | — |
| FluxMetabolism | ✅ | 21 |
| AGENTESE MetabolicNode | ✅ | (in void.py) |
| CLI tithe command | ✅ | 12 |
| TUI FeverOverlay | ✅ | 18 |
| FeverOverlay trigger wiring | ✅ | — |

**Complete**: FeverTriggeredEvent emitted when pressure > 0.7 (threshold crossing),
DashboardApp subscribes via EventBus and pushes FeverOverlay modal.

---

## AGENTESE Docs Alignment — In Progress 🚧

| Component | Status | Notes |
|-----------|--------|-------|
| Spec + plans harmonization | 🚧 | Aligning N-cycle clauses and law/entropy guards across `spec/protocols/agentese.md` + plans (`meta→ops`, doc-only sweep). |

---

## Memory (`self/memory.md`) — 75% [ACTIVE]

| Component | Status | Notes |
|-----------|--------|-------|
| Ghost cache | ✅ | Complete |
| Ghost lifecycle (TTL+labels) | ✅ | 22 tests |
| StateCrystal | ✅ | self/stream Phase 2.4 provides foundation |
| CrystallizationEngine | 📋 | Ready for integration |
| CrystalReaper | 📋 | Ready for integration |
| AGENTESE paths (Four Pillars) | ✅ | store/retrieve/compress/promote/demote/deposit/sense/play/evaluate |
| AGENTESE paths (Substrate) | ✅ | allocate/compact/route/substrate_stats (17 tests) |
| **Phase 6: Semantic Routing** | ✅ | 116 tests |
| - SemanticRouter | ✅ | Locality-aware gradient sensing |
| - KgentAllocationManager | ✅ | K→M substrate integration |
| - SubstrateScreen | ✅ | I-gent allocation dashboard |
| - Edge cases (EmbeddingSimilarity, quota) | ✅ | Graceful fallback tested |
| Wire to real SharedSubstrate | 📋 | Replace mocks with real substrate |

---

## Agent Semaphores (`agents/semaphores.md`) — 100% COMPLETE

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | SemaphoreToken, ReentryContext, Purgatory | ✅ | 49 |
| 2 | Flux Integration (JSON, deadline, pheromones) | ✅ | 70 |
| 3 | DurablePurgatory (D-gent backing) | ✅ | 19 |
| 4 | AGENTESE Paths (`self.semaphore.*`, `world.purgatory.*`) | ✅ | — |
| 5 | CLI (`kgents semaphore`) | ✅ | — |
| 6 | QA Integration + Cortex daemon wiring | ✅ | 44 |

---

## Terrarium (`agents/terrarium.md`) — 100% COMPLETE ✅

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | WebSocket Gateway + Mirror Protocol | ✅ | 45 |
| 2 | Prism REST Bridge | ✅ | 30+ |
| 3 | I-gent Widget Server (metrics) | ✅ | — |
| 4 | K8s Operator (AgentServer CRD) | ✅ | 28 |
| 5 | Purgatory Integration (FluxAgent wiring) | ✅ | 14 |

**Total**: 254 tests. All phases complete. Archived in place.

---

## Alethic Architecture (`architecture/alethic.md`) — 100% COMPLETE ✅

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | UniversalFunctor Protocol | ✅ | 18+ |
| 2 | Halo Capabilities (@Stateful, @Soulful, etc.) | ✅ | 40+ |
| 3 | Genus Archetypes (Kappa, Lambda, Delta) | ✅ | 20+ |
| 4 | LocalProjector | ✅ | 35 |
| 5 | K8sProjector | ✅ | 62 |
| 6 | CLI Integration (`kgents a`) | ✅ | 28 |

**Total**: 337+ tests. All phases complete. Archived in place.

---

## K-gent (`agents/k-gent.md`) — 100% COMPLETE ✅

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | Core Governance (LLM dialogue) | ✅ | 88 |
| 2 | Flux Integration (events, KgentFlux) | ✅ | — |
| 3 | CLI Stream (`kgents soul stream`) | ✅ | — |
| 4 | Hypnagogia (dream cycle) | ✅ | 38 |
| 5 | Completion Sprint (Garden, Gatekeeper) | ✅ | 70 |
| — | Session/Soul Cache (NEW) | ✅ | 58 |
| — | K-Terrarium LLM Agents (Crown Jewel) | ✅ | — |

**Total**: 589+ tests. **CROWN JEWEL COMPLETE**: Kent said "this is amazing."

---

## CLI Unification (`devex/cli-unification.md`) — 40% [ACTIVE]

| Phase | Component | Status | Result |
|-------|-----------|--------|--------|
| 1 | Shared Infrastructure | ✅ | `cli/shared/` — 439 lines |
| 2 | Soul Command Refactor | ✅ | 2019→283 lines (-86%) |
| 3 | Agent Command Refactor | 🚧 | 1110→<300 lines (next) |
| 4 | Infra/DevEx Consolidation | 📋 | Merge related |
| 5 | Flow Composition | 📋 | Pipe support |
| 6 | Testing & Polish | 📋 | Full coverage |

**Artifacts**: `cli/shared/` (439), `cli/commands/soul/` (1379), `handlers/soul.py` (283).
**Tests**: 34 passing. **Next**: Phase 3 (a_gent.py).

---

## AGENTESE REPL (`devex/agentese-repl-crown-jewel.md`) — 95% COMPLETE ✅

| Wave | Component | Status | Tests |
|------|-----------|--------|-------|
| 1 | Core REPL, Navigation, Tab Completion | ✅ | 44 |
| 2 | Async Logos, Pipelines, Observer/Umwelt | ✅ | — |
| 2.5 | Hardening (edge cases, security, stress) | ✅ | 29 |
| 3 | Fuzzy matching, LLM suggestions, Session persistence | ✅ | 25 |
| 4 | Joy-inducing (K-gent, easter eggs, welcome variations) | ✅ | 23 |
| 5 | Ambient mode, Dotted path completion | ✅ | 28 |
| 6 | Adaptive learning guide, Tutorial mode | ✅ | 136 |
| 7 | Mastery tier skills | ✅ | 4 |

**Total**: 289 tests, mypy clean, security audited.

**Files**:
- `protocols/cli/repl.py` — Core REPL engine
- `protocols/cli/repl_fuzzy.py` — Fuzzy matching, LLM suggester
- `protocols/cli/repl_session.py` — Session persistence
- `protocols/cli/repl_guide.py` — Adaptive learning guide
- `protocols/cli/repl_tutorial.py` — Tutorial mode

---

## I-gent Widgets (NEW) — 100% COMPLETE ✅

| Component | Status | Tests |
|-----------|--------|-------|
| Core widgets (DensityField, Glitch) | ✅ | — |
| BranchTree | ✅ | — |
| Entropy widget | ✅ | — |
| GraphLayout | ✅ | — |
| Slider | ✅ | — |
| Sparkline | ✅ | — |
| Timeline | ✅ | — |
| TriadHealth | ✅ | — |
| Data hints/loom/LOD | ✅ | 149 |

**Total**: 217 widget tests. Full widget toolkit.

---

## Flux Synapse (NEW) — In Progress 🚧

| Component | Status | Tests |
|-----------|--------|-------|
| Synapse core | ✅ | 44 |
| Outbox integration | ✅ | — |
| Robustification | 🚧 | — |

---

## SaaS Foundation (`saas/strategy-implementation.md`) — Phase 1 COMPLETE ✅

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | Multi-tenant Auth (API Keys, Scopes) | ✅ | 69 |
| 1 | AGENTESE REST API (3 endpoints) | ✅ | 13 |
| 1 | K-gent Sessions API (5 endpoints) | ✅ | 17 |
| 1 | Usage Metering (in-memory) | ✅ | — |
| 2 | NATS JetStream | 📋 | — |
| 2 | OpenMeter Integration | 📋 | — |
| 2 | Real SSE Streaming | 📋 | — |
| 3 | Dashboard UI | 📋 | — |
| 3 | Playground UI | 📋 | — |

**Total Phase 1**: 215 tests, 3,769 LOC source, 2,485 LOC tests.

---

## Turn-gents (`architecture/turn-gents.md`) — 100% COMPLETE ✅

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | Turn Schema (Turn, TurnType, YieldTurn) | ✅ | 46 |
| 2 | CausalCone + linearize_subset() | ✅ | 21 |
| 3 | TurnBasedCapability Halo decorator | ✅ | 8 |
| 4 | TurnBasedAdapter + LocalProjector | ✅ | 12 |
| 5 | YieldHandler + approval strategies | ✅ | 40 |
| 6 | TurnDAGRenderer for Terrarium TUI | ✅ | 25 |
| 7 | TurnBudgetTracker (order + surplus) | ✅ | 35 |

**Total**: 187 tests. All phases complete.

---

## Visualization Strategy (`interfaces/visualization-strategy.md`) — 100% COMPLETE ✅

| Phase | Component | Status | Files |
|-------|-----------|--------|-------|
| 1.1 | LOD Navigation (Observatory→Terrarium→Cockpit→Debugger) | ✅ | screens/*.py |
| 1.2 | HeartbeatMixin + Controller | ✅ | theme/heartbeat.py |
| 2.1 | ReplayController (animated playback) | ✅ | navigation/replay.py |
| 2.2 | PheromoneManager (stigmergic trails) | ✅ | data/pheromone.py |
| 2.3 | Posture indicators (visual state) | ✅ | theme/posture.py |
| 3.1 | AgentChatPanel (Q&A overlay) | ✅ | overlays/chat.py |
| 3.2 | WeatherEngine (entropy as climate) | ✅ | data/weather.py |
| 3.3 | GravityLayoutEngine (relevance layout) | ✅ | navigation/gravity.py |
| 4.1 | Debugger ReplayController wiring | ✅ | screens/debugger_screen.py |
| 4.2 | WeatherWidget in Observatory/Dashboard | ✅ | widgets/weather_widget.py |
| 4.3 | Chat keybinding (? in Cockpit) | ✅ | screens/cockpit.py |
| 4.4 | Posture symbols in AgentCard/GardenCard | ✅ | screens/flux.py, observatory.py |
| 4.5 | Unit tests (88 new) | ✅ | _tests/*.py |
| 4.6 | Weather trend forecasting (metabolism→forecast) | ✅ | data/weather.py |
| 4.7 | Garden lifecycle visualization | ✅ | screens/dashboard.py |
| 4.8 | HotData "Day in the Life" fixture | ✅ | data/hot_data.py |

**Total**: 9 new modules, 88+ new tests. All phases complete.

**Files**:
- `weave/turn.py` — Turn, TurnType, YieldTurn
- `weave/causal_cone.py` — CausalCone, CausalConeStats
- `weave/yield_handler.py` — YieldHandler, ApprovalStrategy
- `weave/economics.py` — TurnBudgetTracker, BudgetPolicy
- `agents/i/screens/turn_dag.py` — TurnDAGRenderer
- `qa/demo_turn_gents.py` — Interactive demo

**Integration Points**:
- self/memory Phase 7: CausalConeAgent
- interfaces/dashboard-overhaul: Debugger Screen LOD 2
- agents/k-gent: Soul intercept via TurnBasedCapability
- polynomial-agent: State transitions emit Turns

---

## Verification

```bash
cd impl/claude && pytest -q --tb=no
cd impl/claude && uv run mypy .
```

---

*Last verified: 2025-12-14 Chief Reconciliation (16,892 tests, mypy clean)*
