# Plans: AGENTESE-Organized Implementation Roadmap

> *"The noun is a lie. There is only the rate of change."*

This directory contains implementation plans organized by AGENTESE context paths.

---

## Directory Structure

```
plans/
├── README.md                    # This file: overview + decision log
├── _status.md                   # Implementation status matrix
├── NEXT_SESSION_PROMPT.md       # Quick-start for next session
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
| `self/stream.md` | 70% | Modal Scope (Phase 2.2) |
| `concept/creativity.md` | 80% | Bidirectional Skeleton (Task 2) |
| `agents/t-gent.md` | 90% | Type V Adversarial |
| `self/interface.md` | 0% | Phase 1: Core Flux |
| `self/memory.md` | 30% | StateCrystal |
| `void/entropy.md` | 0% | MetabolicEngine |
| `concept/lattice.md` | 0% | define_concept |

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
# Check status
cat plans/_status.md

# What to work on next
cat plans/NEXT_SESSION_PROMPT.md

# Run tests
cd impl/claude && pytest -q --tb=no

# Check types
cd impl/claude && uv run mypy .
```

---

*"Plans are worthless, but planning is everything." — Eisenhower*
