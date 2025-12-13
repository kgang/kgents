# Implementation Status Matrix

> Last updated: 2025-12-12 (post-audit)

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

## Entropy/Metabolism (`void/entropy.md`) — 85%

| Component | Status | Tests |
|-----------|--------|-------|
| MetabolicEngine | ✅ | 36 |
| FeverStream | ✅ | — |
| FluxMetabolism | ✅ | 21 |
| AGENTESE MetabolicNode | ✅ | (in void.py) |
| CLI tithe command | ✅ | 12 |
| TUI FeverOverlay | 📋 | — |

---

## Memory (`self/memory.md`) — 30% [ACTIVE]

| Component | Status | Notes |
|-----------|--------|-------|
| Ghost cache | ✅ | Complete |
| StateCrystal | ✅ | self/stream Phase 2.4 provides foundation |
| CrystallizationEngine | 📋 | Ready for integration |
| CrystalReaper | 📋 | Ready for integration |
| AGENTESE paths | 📋 | self.memory.* wiring |

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

## K-gent (`agents/k-gent.md`) — 97% [ACTIVE]

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | Core Governance (LLM dialogue) | ✅ | 88 |
| 2 | Flux Integration (events, KgentFlux) | ✅ | — |
| 3 | CLI Stream (`kgents soul stream`) | ✅ | — |
| 4 | Hypnagogia (dream cycle) | ✅ | 38 |
| 5 | Completion Sprint (Garden, Gatekeeper) | ✅ | 70 |
| — | Session/Soul Cache (NEW) | ✅ | 58 |
| — | Deferred (Fractal, Holographic) | 📋 | — |

**Total**: 589 tests. Core complete; deferred features remaining.

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

*Last verified: 2025-12-13 Chief reconciliation (12,515 tests, mypy clean)*
