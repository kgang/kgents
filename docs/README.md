---
context: self
---

# kgents Documentation

> *"Read the skills first. They'll save you hours. Skip them and you'll reinvent wheels we already built."*

This documentation is organized for **developers, researchers, and AI agents** who want to build with kgents. Everything here assumes you've cloned the repo and want to ship something.

---

## The Four Pillars

kgents rests on four core abstractions. Understanding these unlocks the entire system.

### I. AGENTESE — The Universal Protocol

The native language of kgents. Paths ARE the API.

```python
await logos.invoke("world.document.manifest", observer)  # Different observers → different projections
await logos.invoke("void.axiom.mirror-test", observer)   # Ground truth queries
```

| Context | Domain |
|---------|--------|
| `world.*` | External entities |
| `self.*` | Internal state |
| `concept.*` | Abstract structures |
| `void.*` | Irreducible ground |
| `time.*` | Temporal traces |

**Skill**: [agentese-path.md](skills/agentese-path.md), [agentese-node-registration.md](skills/agentese-node-registration.md)

### II. D-gents — Persistence with Optics

Categorical storage with law-verified access. Universe for typed objects, DataBus for reactive events.

```python
universe = await get_universe()
crystal = await universe.get(Crystal, id="abc123")
bus.subscribe("crystal.created", handler)
```

**Stack**: `Universe → DgentRouter → Backends (Memory/JSONL/SQLite/Postgres) → DataBus`

**Skill**: [unified-storage.md](skills/unified-storage.md), [data-bus-integration.md](skills/data-bus-integration.md)

### III. Galois Theory + Agent-DP + ASHC

Value-encoded self-justification. Every decision quantified by Galois loss.

- **Galois Loss**: L(P) = information destroyed when restructuring. Low loss = self-justifying.
- **Agent-DP**: Design as dynamic programming. State = specs, Actions = decisions, Reward = Constitution - λ·Loss.
- **ASHC**: Automated Self-Healing Code with formal verification gatekeepers.

**Theory**: `spec/theory/galois-modularization.md`, `spec/theory/agent-dp.md`

### IV. Hypergraph Editor + K-Blocks + Trails + Marks

Novel UX for conceptual navigation. Specs as graph nodes, navigation as edge traversal.

| Component | Purpose |
|-----------|---------|
| **Hypergraph Editor** | Six-mode modal editing (NORMAL/INSERT/EDGE/VISUAL/COMMAND/WITNESS) |
| **K-Block** | Monadic isolation—changes don't escape until commit |
| **Trail** | Semantic breadcrumb through the graph |
| **Mark** | Atomic witness with reasoning + principles |

**Skill**: [hypergraph-editor.md](skills/hypergraph-editor.md)

---

## The One Rule

**Read `docs/skills/` before building anything.**

The skills cover every task you'll encounter. Each skill answers: "How do I do X without breaking Y?"

---

## Where to Start (By Goal)

| Your Goal | Start Here | Time |
|-----------|------------|------|
| Get running | [quickstart.md](quickstart.md) | 5 min |
| Use the CLI | [cli-reference.md](cli-reference.md) | 10 min |
| Build a feature | [skills/](skills/) | 30 min to skim |
| Understand the math | [categorical-foundations.md](categorical-foundations.md) | 1 hr |
| Add an AGENTESE path | [skills/agentese-node-registration.md](skills/agentese-node-registration.md) | 15 min |
| Debug DI failures | [skills/agentese-node-registration.md](skills/agentese-node-registration.md) §Enlightened Resolution | 5 min |
| Write tests | [skills/test-patterns.md](skills/test-patterns.md) | 20 min |
| Check what's built | [systems-reference.md](systems-reference.md) | 10 min |

---

## Skills (Organized by Layer)

### Foundation (The Ground)

| Skill | When You Need It |
|-------|------------------|
| [polynomial-agent.md](skills/polynomial-agent.md) | State machines with mode-dependent inputs |
| [building-agent.md](skills/building-agent.md) | Composition laws, the `>>` operator |

### Protocol (The API)

| Skill | When You Need It |
|-------|------------------|
| [agentese-path.md](skills/agentese-path.md) | Understanding path structure |
| [agentese-node-registration.md](skills/agentese-node-registration.md) | Exposing services via `@node` |

### Architecture (Crown Jewels)

| Skill | When You Need It |
|-------|------------------|
| [crown-jewel-patterns.md](skills/crown-jewel-patterns.md) | 14 patterns for production services |
| [metaphysical-fullstack.md](skills/metaphysical-fullstack.md) | Vertical slice architecture |
| [data-bus-integration.md](skills/data-bus-integration.md) | Reactive event wiring |

### Projection (UI)

| Skill | When You Need It |
|-------|------------------|
| [projection-target.md](skills/projection-target.md) | Same agent, different surfaces |
| [elastic-ui-patterns.md](skills/elastic-ui-patterns.md) | Responsive density modes |
| [hypergraph-editor.md](skills/hypergraph-editor.md) | Modal graph navigation |

### Process (Meta)

| Skill | When You Need It |
|-------|------------------|
| [spec-template.md](skills/spec-template.md) | Writing generative specs |
| [spec-hygiene.md](skills/spec-hygiene.md) | Avoiding bloat |

### Testing

| Skill | When You Need It |
|-------|------------------|
| [test-patterns.md](skills/test-patterns.md) | Types I-V, property-based, chaos |

---

## Task-to-Skill Routing

| Task | Primary Skill | Supporting |
|------|---------------|------------|
| Add new agent | building-agent.md | polynomial-agent.md, test-patterns.md |
| Expose via AGENTESE | agentese-node-registration.md | agentese-path.md |
| Fix DI errors | agentese-node-registration.md | metaphysical-fullstack.md |
| Debug event flow | data-bus-integration.md | crown-jewel-patterns.md |
| Add Crown Jewel | crown-jewel-patterns.md | metaphysical-fullstack.md |
| Build UI component | elastic-ui-patterns.md | projection-target.md |
| Navigate graph | hypergraph-editor.md | — |

---

## For AI Agents

If you're an AI agent working in this codebase:

### Essential Reads
1. **[../CLAUDE.md](../CLAUDE.md)** — Context, anti-sausage protocol, voice anchors
2. **[skills/](skills/)** — Before building anything
3. **[systems-reference.md](systems-reference.md)** — Before building new, check what exists

### Critical Learnings
```python
# DI Enlightened Resolution
# Required deps fail fast, optional deps (= None) skip gracefully
@node(dependencies=("foo",))  # REQUIRED: must be registered
def __init__(self, bar: Bar | None = None): ...  # OPTIONAL: skips if missing

# @node runs at import time
# If module not imported → node not registered
# Fix: ensure _import_node_modules() in gateway.py includes your module

# Frontend TypeScript must typecheck
cd impl/claude/web && npm run typecheck  # Catches real bugs
```

### Voice Preservation
- Quote Kent's anchors directly: *"Daring, bold, creative, opinionated but not gaudy"*
- The Mirror Test: *"Does this feel like Kent on his best day?"*
- If you're smoothing rough edges that should stay rough, stop.

### Agent-Specific Skills
- [witness-for-agents.md](skills/witness-for-agents.md) — JSON output, subprocess integration
- [zero-seed-for-agents.md](skills/zero-seed-for-agents.md) — Seven-layer navigation

### Quick Error Fixes

| Error Pattern | Fix |
|---------------|-----|
| `DependencyNotFoundError: Missing '*'` | Register in services/providers.py |
| `@node declares X but __init__ has no X` | Add X param to __init__ |
| `object async_generator can't be used in await` | Don't await async generators |

---

## Common Pitfalls

### DI Enlightened Resolution
```python
# THE FIX for required deps: Register in services/providers.py
container.register("foo", get_foo, singleton=True)
```

### Frontend Type Drift
```bash
cd impl/claude/web && npm run typecheck  # ALWAYS before committing
```

### Import-Time Node Registration
```python
# @node runs at import. Module not imported → node not registered.
# Fix: check _import_node_modules() in gateway.py
```

---

## Documentation Structure

### Getting Started
- [quickstart.md](quickstart.md) — Zero to agent in 5 minutes
- [cli-reference.md](cli-reference.md) — CLI command reference
- [local-development.md](local-development.md) — Dev environment

### Architecture
- [architecture-overview.md](architecture-overview.md) — Three pillars, functor system
- [systems-reference.md](systems-reference.md) — Production systems inventory
- [categorical-foundations.md](categorical-foundations.md) — Category theory

### Theory (Core Abstractions)
- `spec/theory/galois-modularization.md` — Galois loss as quality signal
- `spec/theory/agent-dp.md` — Design as dynamic programming
- `spec/protocols/zero-seed.md` — Seven-layer epistemic holarchy
- `spec/protocols/witness.md` — Marks, crystals, dialectical fusion

### Skills
- [skills/README.md](skills/README.md) — Full index

---

## The Composition Formula

Every kgents component follows this structure:

```
Component = Foundation ∘ Protocol ∘ Architecture ∘ Spec ∘ Projection

          = (polynomial-agent + building-agent)           # Foundation
          ∘ (agentese-path + agentese-node-registration)  # Protocol
          ∘ (crown-jewel-patterns + metaphysical-fullstack + data-bus)  # Architecture
          ∘ (spec-template + spec-hygiene)                # Spec
          ∘ (projection-target + test-patterns + elastic-ui)  # Projection
```

---

*"The persona is a garden, not a museum."*
