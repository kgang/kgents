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
| **Services** | `services/` | Crown Jewels (Brain, Town, Witness, Liminal...) |
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
| Brain | 100% | Spatial cathedral of memory + TeachingCrystal crystallization |
| Town | 70% | Multi-agent simulation |
| Witness | 98% | Audit core: Mark, Walk, Playbook, Grant, Scope (461+ tests) |
| Atelier | 75% | Design forge and creative workshop |
| Liminal | 50% | Transition protocols: Morning Coffee |

---

## Witness: Marks & Decisions

> *"The proof IS the decision. The mark IS the witness."*

### Mark Moments (`km`)

```bash
km "what happened"                         # Basic mark
km "insight" --reasoning "why it matters"  # With justification
km "gotcha" --tag gotcha --tag agentese    # Tagged for retrieval
km "follow-up" --parent mark-abc           # Causal lineage
km "action" --json                         # Machine-readable
```

**Tags**: `eureka` `gotcha` `taste` `friction` `joy` `veto` `decision` `pattern`

### Record Decisions (`kg decide`)

```bash
# Quick decision
kg decide --fast "choice" --reasoning "why"

# Full dialectic (Kent + Claude differ)
kg decide --kent "view" --kent-reasoning "why" \
          --claude "view" --claude-reasoning "why" \
          --synthesis "fusion" --why "justification"
```

### Query & Crystallize

```bash
kg witness show --today                # Today's marks
kg witness show --tag joy              # Filter by tag
kg witness tree mark-abc               # Causal tree
kg witness crystallize                 # Marks → Session crystal
kg witness context --budget 2000       # Budget-aware context
```

### When to Witness

- After fixing something subtle → `km` with `--tag gotcha`
- When choosing between options → `kg decide`
- When something feels right/wrong → `km` with `--tag taste`
- Before ending session → `/crystallize`

**Crystal Hierarchy**: Marks → Session (L0) → Day (L1) → Week (L2) → Epoch (L3)

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

*Lines: 115. Ceiling: 120.*
