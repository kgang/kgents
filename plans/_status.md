# Implementation Status Matrix

> Last updated: 2025-12-12

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
| Flux Functor | `_archive/flux-functor-v1.0-complete.md` | 261 |
| I-gent v2.5 | `_archive/igent-v2.5-complete.md` | 137 |
| Reflector | `_archive/reflector-v1.0-complete.md` | 36 |
| U-gent Migration | `_archive/u-gent-migration-v1.0-complete.md` | — |
| K8-Terrarium v2.0 | `_archive/k8-terrarium-v2.0-complete.md` | 24+ |
| CLI Hollowing | `_archive/cli-hollowing-v1.0-complete.md` | 100+ |
| Capital Ledger | `_archive/capital-ledger-v1.0-complete.md` | 83+ |

---

## Context Management (`self/stream.md`) — 75%

**Phase 2.1 COMPLETE** (181 tests):

| Component | Status | Tests |
|-----------|--------|-------|
| ContextWindow | ✅ | 41 |
| LinearityMap | ✅ | 38 |
| ContextProjector | ✅ | 28 |
| StreamContextResolver | ✅ | 31 |
| MDL Compression | ✅ | 43 |

**Phase 2.2 COMPLETE** (44 tests):

| Component | Status | Tests |
|-----------|--------|-------|
| ModalScope | ✅ | 44 |

**Remaining (Phases 2.3-2.4)**:

| Phase | Component | Status |
|-------|-----------|--------|
| 2.3 | Pulse + VitalityAnalyzer | 📋 |
| 2.4 | StateCrystal + Reaper | 📋 |

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

| Component | Status |
|-----------|--------|
| Types I-IV | ✅ |
| Type V (AdversarialGym) | 📋 |

---

## Entropy/Metabolism (`void/entropy.md`) — 70%

| Component | Status | Tests |
|-----------|--------|-------|
| MetabolicEngine | ✅ | 36 |
| FeverStream | ✅ | — |
| FluxMetabolism | ✅ | 21 |
| AGENTESE MetabolicNode | ✅ | (in void.py) |
| CLI tithe command | ✅ | 12 |
| TUI FeverOverlay | 📋 | — |

---

## Memory (`self/memory.md`) — 30% [BLOCKED]

| Component | Status | Notes |
|-----------|--------|-------|
| Ghost cache | ✅ | Complete |
| StateCrystal | 📋 | Awaits self/stream Phase 2.4 |

---

## Agent Semaphores (`agents/semaphores.md`) — 95%

| Phase | Component | Status | Tests |
|-------|-----------|--------|-------|
| 1 | SemaphoreToken, ReentryContext, Purgatory | ✅ | 49 |
| 2 | Flux Integration (JSON, deadline, pheromones) | ✅ | 70 |
| 3 | DurablePurgatory (D-gent backing) | ✅ | 19 |
| 4 | AGENTESE Paths (`self.semaphore.*`, `world.purgatory.*`) | ✅ | — |
| 5 | CLI (`kgents semaphore`) | ✅ | — |
| — | QA Integration + Cortex daemon wiring | 📋 | — |

---

## Terrarium (`agents/terrarium.md`) — 0%

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | WebSocket Gateway + Mirror Protocol | 📋 |
| 2 | Prism REST Bridge | 📋 |
| 3 | I-gent Widget Server | 📋 |
| 4 | K8s Operator | 📋 |
| 5 | Purgatory Integration | 📋 |

---

## Verification

```bash
cd impl/claude && pytest -q --tb=no
cd impl/claude && uv run mypy .
```

---

*Last verified: 2025-12-12 (8,938 tests)*
