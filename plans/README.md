# Plans: AGENTESE-Organized Implementation Roadmap

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

This directory contains implementation plans organized by AGENTESE context paths.

## The Forest Protocol

**Read first**: `plans/principles.md` and `plans/_forest.md`

Plans are managed as a **forest**, not a single tree. Each session should:
1. Read `_forest.md` for canopy view
2. Allocate attention across multiple trees (60/25/10/5 split)
3. Write an epilogue to `_epilogues/` for the next session

See `plans/principles.md` for the full Forest Protocol.

---

## Directory Structure

```
plans/
├── README.md                    # This file: overview + decision log
├── principles.md                # The Forest Protocol (read this!)
├── _forest.md                   # Canopy view (session start)
├── _status.md                   # Implementation status matrix
├── _epilogues/                  # Session continuity (session end)
├── _focus.md                    # Current session focus (formerly NEXT_SESSION_PROMPT.md)
├── world/                        # (Empty - k8-gents.md archived)
├── self/
│   ├── stream.md                # self.stream.* (Store Comonad, ContextProjector)
│   ├── memory.md                # self.memory.* (D-gent, Ghost cache)
│   └── interface.md             # self.interface.* (I-gent v2.5, Semantic Flux)
├── void/
│   └── entropy.md               # void.entropy.* (Metabolism, tithe)
├── concept/
│   ├── creativity.md            # concept.blend.* + self.judgment.* (ICCC v2.5)
│   └── lattice.md               # concept.*.define (Genealogical typing)
├── agents/
│   ├── t-gent.md                # Testing agents (Types I-V)
│   └── u-gent.md                # Utility agents (Tool use)
└── _archive/                    # Completed plans (historical reference)
    ├── cli-hollowing-v1.0-complete.md
    ├── capital-ledger-v1.0-complete.md
    └── ...
```

---

## What's Done vs. What's Next

### Archived (Complete)

| Plan | Summary | Tests |
|------|---------|-------|
| CLI Hollowing | ResilientClient, Ghost, hollowed handlers | 100+ |
| Capital Ledger | Event-sourced, TrustGate, CLI commands | 83+ |
| **K8-Terrarium v2.0** | Passive Stigmergy, LogosResolver, StigmergyStore | 24+ |
| **T/U-gent Separation** | Tool files moved to `agents/u/` | 7,741 total |

### Active Plans

| Plan | Status | Next Action |
|------|--------|-------------|
| `concept/lattice.md` | 40% | Wire to concept.*.define |
| `concept/creativity.md` | 90% | Tasks 2-4: Bidirectional Skeleton |
| `self/stream.md` | 70% | **Rewritten** — Phase 2.2 (ModalScope: git-backed branching) |
| `agents/t-gent.md` | 90% | Type V Adversarial |
| `self/memory.md` | 30% | StateCrystal (blocked by stream Phase 2.4) |
| `void/entropy.md` | 10% | MetabolicEngine (research complete, Flux unblocks) |

### Recently Completed

| Plan | Status | Notes |
|------|--------|-------|
| **`agents/loop.md` (Flux)** | ✅ | **261 tests**. Flux Functor: Agent[A,B] → Agent[Flux[A], Flux[B]] |
| `self/reflector.md` | ✅ | Phases 1-4 complete, FluxReflector done |
| `self/interface.md` | ✅ | I-gent v2.5 Phase 5 complete |

---

## Decision Log

Major architectural decisions with rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-11 | **Archive CLI Hollowing** | Complete: ResilientClient, Ghost Protocol, hollowed handlers |
| 2025-12-11 | **Archive Capital Ledger** | Complete: Event-sourced, BypassToken, TrustGate, CLI |
| 2025-12-11 | **Reject Dapr** | K8s Operator IS the actor runtime; Dapr adds bloat |
| 2025-12-11 | **Store Comonad** | `ContextWindow` uses `(S -> A, S)` structure |
| 2025-12-11 | **ContextProjector (not Lens)** | Lossy compression violates Get-Put law |
| 2025-12-11 | **Resource Accounting** | Python cannot enforce linearity at type level |
| 2025-12-11 | **Event-Sourced Ledger** | Balance is derived projection, not stored state |
| 2025-12-11 | **Capital as Capability (OCap)** | BypassToken is unforgeable object |
| 2025-12-11 | **I-gent v2.5: Semantic Flux** | Agents are currents, not rooms |
| 2025-12-11 | **Single operator pod** | Sufficient for <100 agents |
| 2025-12-11 | **Cognitive probes via ClaudeCLIRuntime** | LLM health != HTTP 200 |
| 2025-12-11 | **Passive Stigmergy (K8-Terrarium v2.0)** | Intensity calculated on read, not stored |
| 2025-12-11 | **LogosResolver** | Stateless AGENTESE→K8s translation layer |
| 2025-12-11 | **T/U-gent Separation** | Tools in U-gent, testing in T-gent (categorical split) |
| 2025-12-12 | **Stream Plan Rewrite** | Comprehensive plan with category theory foundation, GCC research |
| 2025-12-12 | **ModalScope via duplicate()** | Git-backed branching is comonadic duplicate() made persistent |
| 2025-12-12 | **Context = Thermodynamics** | Pressure/entropy/phase transitions model for context management |
| 2025-12-12 | **Flux Functor Complete** | Event-driven streams, not timer-driven loops. 261 tests. |

---

## Horizon Decisions

Decisions that may need revisiting:

### Capital Decay Model
Start with 0.01 time-based decay. Revisit activity-based after collecting metrics.

### Temporal/CRD Division
- CRDs for Loop Mode (state observation)
- Temporal for Function Mode (sequential orchestration)

### Y-gent/D-gent/Git Layering
- Git = Puppet (substrate)
- D-gent = Lens (observer)
- Y-gent = Weaver (strategy)

---

## Quick Reference

```bash
# Session start: read the forest
cat plans/_forest.md
cat plans/principles.md

# Check detailed status
cat plans/_status.md

# Read last epilogue
ls -la plans/_epilogues/

# Run tests
cd impl/claude && pytest -q --tb=no

# Check types
cd impl/claude && uv run mypy .

# Session end: write epilogue
# Create plans/_epilogues/YYYY-MM-DD-<session>.md
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*

*"The forest is wiser than any single tree." — Forest Protocol*
