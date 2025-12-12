# Implementation Status Matrix

> Last updated: 2025-12-11

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
| CLI Hollowing | `_archive/cli-hollowing-v1.0-complete.md` | 100+ |
| Capital Ledger | `_archive/capital-ledger-v1.0-complete.md` | 83+ |
| **K8-Terrarium v2.0** | `_archive/k8-terrarium-v2.0-complete.md` | 24+ (pheromone) |
| **T/U-gent Separation** | N/A (git-moved) | 7,741 total |

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

## Context Management (`self/stream.md`)

| Component | Status | Notes |
|-----------|--------|-------|
| ContextWindow (Store Comonad) | ✅ Done | 41 tests |
| LinearityMap | ✅ Done | 38 tests |
| ContextProjector | ✅ Done | 28 tests |
| AGENTESE `self.stream.*` | ✅ Done | 31 tests |
| MDL Compression | ✅ Done | 43 tests |
| Modal Scope | 📋 | Git-backed branching |
| StateCrystal | 📋 | Checkpointing |
| Dual-lane pheromones | 📋 | Fast/slow channels |

---

## Creativity v2.5 (`concept/creativity.md`)

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

## Still Planned (No Progress)

| Plan | Priority | Blocked By |
|------|----------|------------|
| `self/interface.md` (I-gent v2.5) | Medium | Nothing |
| `self/memory.md` (StateCrystal) | Low | `self/stream.md` |
| `void/entropy.md` (Metabolism) | Low | Nothing |
| `concept/lattice.md` (Genealogy) | Low | Nothing |

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

*Last verified: 2025-12-11 (7,741 tests passed, K8-Terrarium v2.0 + T/U-gent separation complete)*
