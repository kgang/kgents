# Implementation Status Matrix

> Last updated: 2025-12-12

## Legend

| Symbol | Status |
|--------|--------|
| ✅ | Done - implemented and verified |
| 🚧 | In Progress - partially implemented |
| 📋 | Planned - not yet started |

---

## Completed (Archived)

These plans are fully implemented and moved to `_archive/`:

| Plan | Archive Path | Tests |
|------|--------------|-------|
| **Flux Functor** | `agents/loop.md` (kept as reference) | **261** |
| CLI Hollowing | `_archive/cli-hollowing-v1.0-complete.md` | 100+ |
| Capital Ledger | `_archive/capital-ledger-v1.0-complete.md` | 83+ |
| **K8-Terrarium v2.0** | `_archive/k8-terrarium-v2.0-complete.md` | 24+ (pheromone) |
| **T/U-gent Separation** | N/A (git-moved) | 7,812 total |

---

## K8s Infrastructure (✅ COMPLETE → Archived)

All K8-Terrarium v2.0 work is done and archived:

| Component | Status | Notes |
|-----------|--------|-------|
| CRDs (all 5) | ✅ Done | Agent, Pheromone, Memory, Umwelt, Proposal |
| Operators | ✅ Done | agent_operator, pheromone_operator, proposal_operator |
| Cluster scripts | ✅ Done | setup, verify, teardown, deploy |
| MCP Resources | ✅ Done | `kgents://` URI scheme |
| LLM Integration | ✅ Done | CognitiveProbe, PathProbe, agents |
| **Passive Stigmergy** | ✅ Done | Pheromone intensity calculated on read (v2.0) |
| **LogosResolver** | ✅ Done | Stateless AGENTESE→K8s translation (536 lines) |
| **Stigmergy Store** | ✅ Done | Redis-backed ephemeral pheromones |
| **Spec Extraction** | ✅ Done | `spec/k8-gents/` with ontology, protocols |

**Remaining (Future)**:
- L-gent HTTP wrapper (`agents/l/server.py`)
- T-gent ValidatingAdmissionWebhook
- Terrarium TUI enhancements

---

## Context Management (`self/stream.md`) — 70%

**Phase 2.1 COMPLETE** (181 tests):

| Component | Status | Tests | Notes |
|-----------|--------|-------|-------|
| ContextWindow | ✅ Done | 41 | Store Comonad (extract/extend/duplicate) |
| LinearityMap | ✅ Done | 38 | DROPPABLE/REQUIRED/PRESERVED monotonicity |
| ContextProjector | ✅ Done | 28 | Galois Connection (NOT lens—explicitly lossy) |
| StreamContextResolver | ✅ Done | 31 | AGENTESE `self.stream.*` routing |
| MDL Compression | ✅ Done | 43 | Ventura Fix: Quality = Ratio × (1 - Error) |

**Phases 2.2-2.4 PLANNED**:

| Phase | Component | AGENTESE Path | Notes |
|-------|-----------|---------------|-------|
| 2.2 | ModalScope | `void.entropy.sip/pour` | Git-backed branching via duplicate() |
| 2.3 | Pulse + VitalityAnalyzer | `time.trace.pulse` | Zero-token health (loop detection) |
| 2.4 | StateCrystal + Reaper | `self.memory.crystallize` | Comonadic checkpoints with TTL |

**Novel insights** (see `self/stream.md` Part IV):
- Context as thermodynamic system (pressure, entropy, phase transitions)
- GCC mapping: Git operations → comonadic operations
- Adaptive thresholds (implemented in projector.py, needs wiring)

---

## Creativity v2.5 (`concept/creativity.md`) — 90%

| Component | Status | Notes |
|-----------|--------|-------|
| WundtCurator | ✅ Done | Phase 5 |
| Conceptual Blending | ✅ Done | Phase 6 |
| Critic's Loop | ✅ Done | Phase 7 |
| Contract Melt + Pataphysics | ✅ Done | Phase 8 |
| MDL Compression | ✅ Done | Task 1 |
| Bidirectional Skeleton | 📋 | Task 2 (PAYADOR) |
| Wire Pataphysics to LLM | 📋 | Task 3 |
| Auto-Wire Curator Middleware | 📋 | Task 4 |

---

## Agent Separation (`agents/t-gent.md`, `agents/u-gent.md`)

| Component | Status | Notes |
|-----------|--------|-------|
| T-gent Types I-IV | ✅ Done | Testing agents |
| T-gent Type V | 📋 | AdversarialGym |
| **U-gent module** | ✅ Done | Files git-moved from `agents/t/` to `agents/u/` |
| **U-gent registry entry** | ✅ Done | Added to AGENT_REGISTRY (22 agents total) |

---

## Reflector Pattern (`self/reflector.md`) — ✅ COMPLETE

| Component | Status | Notes |
|-----------|--------|-------|
| Reflector Protocol | ✅ Done | `protocols/cli/reflector/protocol.py` |
| RuntimeEvent types | ✅ Done | 10+ event types in `events.py` |
| TerminalReflector | ✅ Done | stdout + FD3 file output |
| HeadlessReflector | ✅ Done | test-friendly capture |
| FluxReflector | ✅ Done | `agents/i/reflector/flux_reflector.py` |
| hollow.py wiring | ✅ Done | Reflector created in main(), events emitted |
| status.py pilot | ✅ Done | Uses ctx.output() for dual-channel |
| Tests | ✅ Done | 36 tests passing |

---

## I-gent v2.5 (`self/interface.md`) — ✅ COMPLETE

| Component | Status | Notes |
|-----------|--------|-------|
| Phase 1: Core Flux | ✅ Done | FluxApp, DensityField, FlowArrow (40 tests) |
| Phase 2: Live Data | ✅ Done | Registry, OgentPoller, XYZ bars (30 tests) |
| Phase 3: Overlays | ✅ Done | WIRE/BODY overlays, waveform (31 tests) |
| Phase 4: Glitch & HUD | ✅ Done | GlitchController, AGENTESE HUD (36 tests) |
| Phase 5: Polish & FD3 | ✅ Done | FD3 bridge, FluxReflector integration |

---

## Lattice v1 (`concept/lattice.md`) — 40%

| Component | Status | Notes |
|-----------|--------|-------|
| LineageChecker | ✅ Done | `protocols/agentese/lattice/checker.py` |
| LineageTracker | ✅ Done | `protocols/agentese/lattice/lineage.py` |
| LineageError types | ✅ Done | `protocols/agentese/lattice/errors.py` |
| Wire to concept.*.define | 📋 | Pending: connect to Logos |
| Tests | 🚧 | In lattice/_tests/ |

---

## Researched (Ready for Implementation)

| Plan | Priority | Notes |
|------|----------|-------|
| `void/entropy.md` (Metabolism) | Medium | **Research complete** 2025-12-12. See `entropy-research-report.md` |

## Still Planned (No Progress)

| Plan | Priority | Blocked By |
|------|----------|------------|
| `self/memory.md` (StateCrystal) | Low | `self/stream.md` Phase 2.4 |

---

## Verification Commands

```bash
# Run all tests
cd impl/claude && pytest -q --tb=no

# Check types
cd impl/claude && uv run mypy .

# Check test counts
cd impl/claude && pytest --collect-only -q | tail -1
```

---

*Last verified: 2025-12-12 (8,337+ tests, **Flux Functor complete (261 tests)**, FluxReflector complete, Lattice v1 40%, void/entropy researched)*
