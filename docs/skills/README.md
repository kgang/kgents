---
context: self
---

# Agent Skills Directory

> *"13 skills are necessary and sufficient to build any kgents component."*

**READ SKILLS FIRST.** Every task has a corresponding skill. Before writing code, find the right skill—it will save you hours.

---

## 🌟 Universal Skills (Start Here)

These four skills apply to virtually ANY work you'll do:

| Skill | When to Use | Lines |
|-------|-------------|-------|
| **[metaphysical-fullstack](metaphysical-fullstack.md)** | Building any feature—the core architecture pattern | 320 |
| **[crown-jewel-patterns](crown-jewel-patterns.md)** | Implementing service logic (14 battle-tested patterns) | 850 |
| **[test-patterns](test-patterns.md)** | Writing any tests (T-gent Types I-V, property-based, React chaos) | 1250 |
| **[elastic-ui-patterns](elastic-ui-patterns.md)** | Any responsive UI (three-mode pattern, density constants) | 330 |

---

## By Task Type

| Task | Skills to Read |
|------|----------------|
| **Adding new agent** | `polynomial-agent.md`, `building-agent.md` |
| **Exposing via AGENTESE** | `agentese-node-registration.md`, `agentese-path.md` |
| **Service/Crown Jewel** | `crown-jewel-patterns.md`, `metaphysical-fullstack.md` |
| **Event-driven feature** | `data-bus-integration.md` |
| **Multi-target rendering** | `projection-target.md`, `elastic-ui-patterns.md` |
| **Writing specs** | `spec-template.md`, `spec-hygiene.md` |
| **Planning work** | `plan-file.md` |

---

## Full Skill Index

### Foundation (Categorical Ground)

| Skill | Purpose |
|-------|---------|
| [polynomial-agent](polynomial-agent.md) | State machines with mode-dependent inputs (PolyAgent[S,A,B]) |
| [building-agent](building-agent.md) | Agent[A,B] composition, functors, D-gent memory patterns |

### Protocol (AGENTESE)

| Skill | Purpose |
|-------|---------|
| [agentese-path](agentese-path.md) | Adding paths to the five contexts |
| [agentese-node-registration](agentese-node-registration.md) | @node decorator, discovery, BE/FE type sync |

### Architecture (Vertical Slice)

| Skill | Purpose |
|-------|---------|
| [crown-jewel-patterns](crown-jewel-patterns.md) | 14 patterns: Container-Owns-Workflow, Signal Aggregation, Teaching Mode... |
| [metaphysical-fullstack](metaphysical-fullstack.md) | AD-009 stack—AGENTESE IS the API, no explicit routes |
| [data-bus-integration](data-bus-integration.md) | DataBus, SynergyBus, EventBus patterns |

### Process (N-Phase)

| Skill | Purpose |
|-------|---------|
| [plan-file](plan-file.md) | Forest Protocol YAML headers, chunks, status lifecycle |
| [spec-template](spec-template.md) | Writing generative specs (200-400 lines) |
| [spec-hygiene](spec-hygiene.md) | 7 bloat patterns to avoid, 5 compression patterns |

### Projection (Multi-Target)

| Skill | Purpose |
|-------|---------|
| [projection-target](projection-target.md) | Custom targets (CLI/TUI/JSON/marimo/WebGL) |
| [test-patterns](test-patterns.md) | T-gent Types I-V, Hypothesis, chaos testing, performance baselines |
| [elastic-ui-patterns](elastic-ui-patterns.md) | Three-mode (Compact/Comfortable/Spacious), content degradation |

---

## The Skill Composition Formula

```
Component = Foundation ∘ Protocol ∘ Architecture ∘ Process ∘ Projection
          = (polynomial-agent + building-agent)
          ∘ (agentese-path + agentese-node-registration)
          ∘ (crown-jewel-patterns + metaphysical-fullstack + data-bus-integration)
          ∘ (plan-file + spec-template + spec-hygiene)
          ∘ (projection-target + test-patterns + elastic-ui-patterns)
```

---

## Archived Skills

Extended skills archived to `docs/_archive/2025-12-18-consolidation/`. Restore if needed:
- agent-town-archetypes, flux-agent, reactive-primitives
- agentese-contract-protocol, frontend-contracts
- gardener-logos, specgraph-workflow, turn-projectors

---

*Consolidated: 2025-12-18 | Skills: 13 active | Skills-First Edition*
