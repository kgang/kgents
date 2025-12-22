---
context: self
---

# kgents Documentation

> *"Read the skills first. They'll save you hours. Skip them and you'll reinvent wheels we already built."*

This documentation is organized for **developers and researchers** who want to build with kgents, not just read about it. Everything here assumes you've cloned the repo and want to ship something.

---

## The One Rule

**Read `docs/skills/` before building anything.**

The 13 skills cover every task you'll encounter. They're battle-tested patterns extracted from building the Crown Jewels. Each skill answers: "How do I do X without breaking Y?"

If you're thinking "I'll just figure it out"—don't. The skills exist because we made the mistakes already.

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

## The 13 Skills (Curated, Not Exhaustive)

These are **necessary and sufficient** to build any kgents component. Organized by layer:

### Foundation (The Ground)

| Skill | When You Need It |
|-------|------------------|
| [polynomial-agent.md](skills/polynomial-agent.md) | Building state machines with mode-dependent inputs |
| [building-agent.md](skills/building-agent.md) | Composition laws, the `>>` operator, testing agents |

### Protocol (The API)

| Skill | When You Need It |
|-------|------------------|
| [agentese-path.md](skills/agentese-path.md) | Understanding `world.town.citizen` path structure |
| [agentese-node-registration.md](skills/agentese-node-registration.md) | Exposing services via `@node` decorator (**read Enlightened Resolution**) |

### Architecture (The Crown Jewels)

| Skill | When You Need It |
|-------|------------------|
| [crown-jewel-patterns.md](skills/crown-jewel-patterns.md) | 14 patterns: Container-Owns-Workflow, Signal Aggregation, Dual-Channel... |
| [metaphysical-fullstack.md](skills/metaphysical-fullstack.md) | "Every agent is a vertical slice from persistence to projection" |
| [data-bus-integration.md](skills/data-bus-integration.md) | DataBus → SynergyBus → EventBus reactive wiring |

### Projection (The UI)

| Skill | When You Need It |
|-------|------------------|
| [projection-target.md](skills/projection-target.md) | CLI, TUI, JSON, marimo, Web—same agent, different surfaces |
| [elastic-ui-patterns.md](skills/elastic-ui-patterns.md) | Responsive: Compact/Comfortable/Spacious density modes |
| [3d-projection-patterns.md](skills/3d-projection-patterns.md) | Three.js, React Three Fiber, the 3D garden |

### Process (The Meta)

| Skill | When You Need It |
|-------|------------------|
| [plan-file.md](skills/plan-file.md) | How to structure implementation plans |
| [spec-template.md](skills/spec-template.md) | Writing specs that generate implementations |
| [spec-hygiene.md](skills/spec-hygiene.md) | Avoiding bloat, keeping specs generative |

### Testing (The Guarantee)

| Skill | When You Need It |
|-------|------------------|
| [test-patterns.md](skills/test-patterns.md) | T-gent Types I-V, property-based tests, chaos testing |

---

## Common Pitfalls (Read Before You Hit Them)

### DI Enlightened Resolution (2025-12-21)
```python
# Required deps (no default) → DependencyNotFoundError with helpful message
@node(dependencies=("foo",))
class MyNode: ...

# Optional deps (with default) → Skip gracefully
def __init__(self, foo: Foo | None = None): ...  # Uses None if not registered

# THE FIX for required: Register in services/providers.py
container.register("foo", get_foo, singleton=True)
```

### Frontend Type Drift
```bash
# You changed a backend model. Frontend now has stale types.
cd impl/claude/web && npm run typecheck  # ALWAYS run before committing
```

### Import-Time Node Registration
```python
# @node runs at import time. If module not imported → node not registered.
# THE FIX: Ensure _import_node_modules() in gateway.py includes your module.
```

### Timer-Driven Loops
```python
# ❌ Creates zombie processes
while True:
    await asyncio.sleep(1.0)
    process()

# ✅ Event-driven Flux
async for event in event_stream:
    process(event)
```

---

## Documentation Index

### Getting Started
- [quickstart.md](quickstart.md) — Zero to agent in 5 minutes
- [cli-reference.md](cli-reference.md) — Complete CLI command reference
- [local-development.md](local-development.md) — Development environment, editor setup

### Architecture
- [architecture-overview.md](architecture-overview.md) — Three pillars, functor system, polynomial architecture
- [systems-reference.md](systems-reference.md) — 17 production systems inventory
- [categorical-foundations.md](categorical-foundations.md) — Category theory for the curious

### Skills (Read These First!)
- [skills/README.md](skills/README.md) — Full index with quick summaries

### Specialized
- [terminal-integration.md](terminal-integration.md) — Tmux, raw mode, terminal handling

### Archived
- [_archive/](_archive/) — Historical docs, consolidated 2025-12-18

---

## AGENTESE Context Mapping

Each doc is annotated with an AGENTESE context (frontmatter `context:`):

| Context | Docs | For Whom |
|---------|------|----------|
| `world` | quickstart | Visitors, evaluators, newcomers |
| `self` | skills/, systems-reference, local-dev | Developers in the codebase |
| `concept` | principles, architecture, categorical | Researchers, architects |

This enables future tooling (context-aware search, navigation) without disrupting existing paths.

---

## For AI Agents

If you're an AI agent working in this codebase:

1. **Read [../CLAUDE.md](../CLAUDE.md)** — Your context, anti-sausage protocol, voice anchors
2. **Read [skills/](skills/)** — Before building anything, these cover every task
3. **Check [systems-reference.md](systems-reference.md)** — Before building new, check what exists

**Critical learnings**:
- DI Enlightened Resolution: Required deps fail fast, optional deps (`= None`) skip gracefully
- `@node` runs at import time (check `_import_node_modules()` in gateway.py)
- Frontend TypeScript must typecheck (`npm run typecheck` catches real bugs)

**Voice preservation**:
- Quote Kent's anchors directly: *"Daring, bold, creative, opinionated but not gaudy"*
- The Mirror Test: *"Does this feel like Kent on his best day?"*
- If you're smoothing rough edges that should stay rough, stop.

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

If you're missing a skill from this composition, your component will have gaps.

---

*"The persona is a garden, not a museum."*
