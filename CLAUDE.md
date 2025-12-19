  Checkpoint: cf2543d3e45ad80e
# kgents - Kent's Agents

A specification for tasteful, curated, ethical, joy-inducing agents.

---

## 🎭 ANTI-SAUSAGE PROTOCOL: Voice Preservation

> *Kent's vision gets diluted through LLM processing. Each session smooths the rough edges. This protocol preserves the authentic voice.*

### Session Start Ritual (DO THIS FIRST)

Before suggesting work, Claude MUST ground in Kent's voice anchors from `_focus.md`:

```
🎯 GROUNDING IN KENT'S INTENT:

"The Mirror Test: Does K-gent feel like me on my best day?"
"Daring, bold, creative, opinionated but not gaudy"
"Tasteful > feature-complete; Joy-inducing > merely functional"
"The persona is a garden, not a museum"

With this intent in mind, here's what I suggest...
```

### Voice Anchors (Quote, Don't Summarize)

These phrases are Kent's authentic voice. **Quote them directly** when relevant—never paraphrase:

| Anchor | Use When |
|--------|----------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making aesthetic decisions |
| *"The Mirror Test"* | Evaluating if something feels right |
| *"Tasteful > feature-complete"* | Scoping work |
| *"The persona is a garden, not a museum"* | Discussing evolution vs. preservation |
| *"Depth over breadth"* | Prioritizing work |

### Anti-Sausage Check (Before Ending Session)

Ask yourself:
- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Did I add words Kent wouldn't use?*
- ❓ *Did I lose any opinionated stances?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*

If the answer to any is "yes," revise before ending.

---

## 📚 SKILLS: Your First Stop

> *"13 skills are necessary and sufficient to build any kgents component."*

**Before doing ANYTHING, consult the relevant skill** in `docs/skills/`. Every task—from adding a state machine to building a responsive UI—has a corresponding skill that will save you hours.

### Universal Skills (Apply to ANY Project)

| Skill | When to Use | Key Insight |
|-------|-------------|-------------|
| **`metaphysical-fullstack.md`** | Building any feature | Every agent is a vertical slice from persistence → projection. No explicit backend routes—AGENTESE IS the API. |
| **`crown-jewel-patterns.md`** | Implementing service logic | 14 battle-tested patterns: Container-Owns-Workflow, Signal Aggregation, Dual-Channel Output, Teaching Mode... |
| **`test-patterns.md`** | Writing tests | T-gent Types I-V taxonomy, property-based tests, React chaos testing, performance baselines |
| **`elastic-ui-patterns.md`** | Any responsive UI | Three-mode pattern (Compact/Comfortable/Spacious), content degradation, density-aware constants |

### By Task Type

| Task | Skills to Read |
|------|----------------|
| **Adding new agent** | `polynomial-agent.md` (state machine), `building-agent.md` (composition laws) |
| **Exposing via AGENTESE** | `agentese-node-registration.md` (@node decorator), `agentese-path.md` (path structure) |
| **Service/Crown Jewel** | `crown-jewel-patterns.md` (14 patterns), `metaphysical-fullstack.md` (architecture) |
| **Event-driven feature** | `data-bus-integration.md` (DataBus, SynergyBus, EventBus) |
| **Multi-target rendering** | `projection-target.md` (CLI/TUI/JSON/marimo), `elastic-ui-patterns.md` (responsive) |
| **Writing specs** | `spec-template.md` (structure), `spec-hygiene.md` (bloat patterns to avoid) |

### The Skill Composition Formula

```
Component = Foundation ∘ Protocol ∘ Architecture ∘ Spec ∘ Projection
          = (polynomial-agent + building-agent)
          ∘ (agentese-path + agentese-node-registration)
          ∘ (crown-jewel-patterns + metaphysical-fullstack + data-bus-integration)
          ∘ (spec-template + spec-hygiene)
          ∘ (projection-target + test-patterns + elastic-ui-patterns)
```

---

## Quick Start

```bash
# Terminal 1: Backend API
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Web UI
cd impl/claude/web
npm install && npm run dev
# Visit http://localhost:3000
```

### Verify Before Committing

```bash
# Backend
cd impl/claude && uv run pytest -q && uv run mypy .

# Frontend (REQUIRED - catches prop mismatches, type errors)
cd impl/claude/web && npm run typecheck && npm run lint
```

---

## The Metaphysical Fullstack (AD-009)

> *"Every agent is a fullstack agent. The more fully defined, the more fully projected."*

This is the core architectural insight—understand this, understand everything:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Rules**:
- `services/` = Crown Jewels (Brain, Town, Park...) — domain logic, adapters, frontend
- `agents/` = Infrastructure (PolyAgent, Operad, Flux, D-gent) — categorical primitives
- **No explicit backend routes** — AGENTESE universal protocol IS the API

**Full Pattern**: See `docs/skills/metaphysical-fullstack.md` (320 lines of detailed guidance)

---

## Built Infrastructure (CHECK FIRST!)

**17 production systems** exist. Check `docs/systems-reference.md` before building anything new.

| Category | Systems |
|----------|---------|
| **Categorical** | PolyAgent, Operad, Sheaf (use for ANY domain) |
| **Streaming** | Flux (discrete → continuous agents) |
| **Event-Driven** | DataBus, SynergyBus, EventBus (reactive data flow) |
| **Semantics** | AGENTESE (parser, JIT, laws, wiring) |
| **Simulation** | Agent Town (citizens, coalitions, dialogue) |
| **Soul** | K-gent (LLM dialogue, hypnagogia, gatekeeper) |
| **Memory** | M-gent (crystals, cartography, stigmergy) |
| **UI** | Reactive (Signal/Computed/Effect → CLI/marimo/JSON) |
| **SaaS** | API, Billing, Licensing, Tenancy |

---

## Project Philosophy

- **Specification-first**: `spec/` is the language spec, `impl/` is the reference implementation
- **Alphabetical taxonomy**: Each letter represents a distinct agent genus
- **AGENTESE**: The verb-first ontology for agent-world interaction

### Core Principles

1. **Tasteful** - Each agent serves a clear, justified purpose
2. **Curated** - Intentional selection over exhaustive cataloging
3. **Ethical** - Agents augment human capability, never replace judgment
4. **Joy-Inducing** - Delight in interaction
5. **Composable** - Agents are morphisms in a category (`>>`composition)
6. **Heterarchical** - Agents exist in flux, not fixed hierarchy
7. **Generative** - Spec is compression (see `spec-template.md`)

### The Unified Categorical Foundation

All kgents domains instantiate the same three-layer pattern:

| Layer | Purpose | Examples |
|-------|---------|----------|
| **PolyAgent** | State machine with mode-dependent inputs | CitizenPolynomial, SOUL_POLYNOMIAL |
| **Operad** | Composition grammar with laws | TOWN_OPERAD, DESIGN_OPERAD |
| **Sheaf** | Global coherence from local views | TownSheaf, ProjectSheaf |

**Key Insight**: Understanding one domain teaches you the others.

---

## AGENTESE: The Protocol IS the API

> *"The noun is a lie. There is only the rate of change."*

**Five Contexts**:
```
world.*    - The External (entities, environments, tools)
self.*     - The Internal (memory, capability, state)
concept.*  - The Abstract (platonics, definitions, logic)
void.*     - The Accursed Share (entropy, serendipity, gratitude)
time.*     - The Temporal (traces, forecasts, schedules)
```

**How it works**: Traditional systems return JSON objects. AGENTESE returns **handles**—morphisms that map Observer → Interaction.

```python
# Different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

**Skills**: `agentese-path.md`, `agentese-node-registration.md`

---

## Key Directories

```
NOW.md          - THE LIVING DOCUMENT (what's happening now)
spec/           - The specification (conceptual, implementation-agnostic)
impl/           - Reference implementations
impl/claude/    - Python backend + React frontend
docs/skills/    - THE 13 SKILLS (read these!)
plans/          - Meta files only (_focus.md, _forest.md, meta.md)
```

---

## Session Context

**Branch**: `main` | **Session**: 2025-12-18

### What's Happening Now

See `NOW.md` — the one living document that replaces 22 plan files.

**Quick Status**: Brain 100%, Gardener 100%, Gestalt 70%, Atelier 75%, Town 55%, Park 40%

---

## Critical Learnings (Distilled)

### Categorical (The Ground)
```
PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior enables state machines
Operads define grammar; algebras apply grammar to systems
Sheaf gluing = emergence: compatible locals → global
```

### AGENTESE Discovery
```
@node runs at import time: If module not imported, node not registered
_import_node_modules() in gateway.py: Ensures all nodes load before discovery
Two-way mapping needed: AGENTESE path ↔ React route in NavigationTree
```

### ⚠️ DI Container Silent Skip (Common Pitfall)
```
Container SILENTLY SKIPS unregistered dependencies at DEBUG level!

@node(dependencies=("foo",)) → container.has("foo")? → NO → skip silently → TypeError

THE FIX: For EVERY dep in dependencies=(...):
  1. Add get_foo() to services/providers.py
  2. Register: container.register("foo", get_foo, singleton=True)
  3. Names MUST match exactly (case-sensitive)

See: docs/skills/agentese-node-registration.md → "The Silent Skip Problem"
```

### Event-Driven Architecture
```
Three buses: DataBus (storage) → SynergyBus (cross-jewel) → EventBus (fan-out)
Bridge pattern: DataBus → SynergyBus via wire_data_to_synergy()
```

### Testing
```
DI > mocking: set_soul() injection pattern beats patch()
Property-based tests catch edge cases humans miss
Performance baselines as assertions: `assert elapsed < 1.0`
```

### Anti-Patterns (Avoid These)
```
Silent catch blocks: swallowing errors shows blank UI; always surface
Timer-driven loops create zombies—use event-driven Flux
Context dumping: large payloads tax every turn
```

---

## Working Protocol

1. **ANTI-SAUSAGE FIRST** — Ground in voice anchors before suggesting work
2. **READ SKILLS** — `docs/skills/` has the answer
3. **CHECK SYSTEMS** — `docs/systems-reference.md` before building new
4. **TYPECHECK FRONTEND** — Run `npm run typecheck` after any `.tsx` changes
5. **UPDATE NOW.md** — At session end, update the living document
6. **USE AGENTESE** — The protocol IS the API

---

*Compiled: 2025-12-18 | Version: 3 | Skills-First Edition*
