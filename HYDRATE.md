# HYDRATE.md — The Seed

> *"To read is to invoke. There is no view from nowhere."*

Minimal context for agents. For humans: start with [README.md](README.md).

---

## Principles

**Tasteful** • **Curated** • **Ethical** • **Joy-Inducing** • **Composable** • **Heterarchical** • **Generative**

Full specification: [spec/principles.md](spec/principles.md)

---

## AGENTESE (Five Contexts)

`world.*` `self.*` `concept.*` `void.*` `time.*`

**Aspects**: `manifest` • `witness` • `refine` • `sip` • `tithe` • `lens` • `define`

```python
await logos.invoke("world.house.manifest", umwelt)  # Observer-dependent
```

---

## Built Systems (USE THESE)

| Category | Location | Purpose |
|----------|----------|---------|
| **Categorical** | `agents/poly/`, `agents/operad/`, `agents/sheaf/` | PolyAgent, composition grammar, emergence |
| **Streaming** | `agents/flux/` | Living pipelines, event-driven flows |
| **Semantics** | `protocols/agentese/` | Logos, parser, JIT, wiring |
| **Services** | `services/` | Crown Jewels (Brain, Gardener, Town, Witness...) |
| **Soul** | `agents/k/` | LLM dialogue, hypnagogia, gatekeeper |
| **Memory** | `agents/m/` | Crystals, cartography, stigmergy |
| **UI** | `agents/i/reactive/` | Signal/Computed/Effect → multi-target |

---

## Composition Patterns

```python
# 1. Agent composition
pipeline = AgentA >> AgentB >> AgentC

# 2. Flux lifting
flux_agent = Flux.lift(discrete_agent)
async for result in flux_agent.start(source): ...

# 3. AGENTESE paths
await logos.invoke("self.brain.capture", umwelt, content="...")

# 4. PolyAgent modes
poly = PolyAgent[S, A, B](positions, directions, transition)

# 5. Widget projection
widget.to_cli() | widget.to_marimo() | widget.to_json()
```

---

## Metaphysical Fullstack (AD-009)

```
Projection → AGENTESE Protocol → Node → Service → Infrastructure → Persistence
```

- Layer 0: `StorageProvider` (membrane.db, XDG-compliant)
- `agents/` = Infrastructure (PolyAgent, Operad, Sheaf)
- `services/` = Crown Jewels (Brain, Gardener, Town...)
- **No explicit backend routes** — AGENTESE IS the API

---

## Crown Jewels

| Jewel | Status | Purpose |
|-------|--------|---------|
| Brain | 100% | Spatial cathedral of memory |
| Gardener | 100% | Cultivation practice |
| Gestalt | 85% | Living visualization |
| Forge | 85% | Creative workshop |
| Town | 70% | Multi-agent simulation |
| Park | 60% | Westworld with consent |
| Witness | 98% | Audit core: Mark, Walk, Playbook, Grant, Scope (461+ tests) |
| Conductor | 92% | CLI v7 orchestration (Phase 5B: spring-physics cursors, NodeDetailPanel) |
| ASHC | 95% | Self-hosting compiler: 408 tests, Phases 1-5 complete |
| Liminal | 50% | Transition protocols: Morning Coffee (224 tests, Phase 2 complete) |

---

## Skills (READ THESE)

`docs/skills/` — 13 essential skills covering every task.

**Universal**: `metaphysical-fullstack.md` • `crown-jewel-patterns.md` • `test-patterns.md`

---

## Commands

```bash
# Backend
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend
cd impl/claude/web && npm run typecheck && npm run lint
```

---

*Lines: 90. Ceiling: 100.*
