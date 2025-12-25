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

## 🔮 DECISION WITNESSING: Capture Reasoning Traces

> *"The proof IS the decision. The mark IS the witness."*

**When to witness decisions**: Architectural choices, design trade-offs, significant implementation decisions, or any choice worth remembering.

### Quick Capture (Trivial Decisions)

```bash
# Single decision with reasoning
kg decide --fast "Use Python 3.12" --reasoning "Latest stable, team familiar"

# Capture that we decided something
kg decide --fast "Added caching layer" --reasoning "API was too slow (200ms → 20ms)"
```

### Full Dialectic (Significant Decisions)

When Kent and Claude have different views, capture the synthesis:

```bash
kg decide --kent "Use LangChain" --kent-reasoning "Scale, resources, production" \
          --claude "Build kgents" --claude-reasoning "Novel contribution, joy-inducing" \
          --synthesis "Build minimal kernel, validate, then decide" \
          --why "Avoids both risks: years of philosophy without validation AND abandoning ideas untested"
```

### Guided Experience (Interactive)

```bash
kg decide
# Walks through: topic → Kent's view → Claude's view → synthesis
```

### When Claude Should Invoke This

1. **After making architectural decisions** with Kent
2. **When Kent asks "should we..."** and you reach a conclusion
3. **When you identify a trade-off** and resolve it
4. **Proactively** for decisions worth remembering

Example during a session:
```
Kent: "Should we use WebSockets or SSE for real-time updates?"
Claude: [discusses trade-offs]
Kent: "Let's go with SSE"
Claude: "I'll record this decision..."

kg decide --kent "WebSockets" --kent-reasoning "Bidirectional, familiar" \
          --claude "SSE" --claude-reasoning "Simpler, HTTP-native, sufficient for our use case" \
          --synthesis "Use SSE" --why "Unidirectional is enough, simpler ops"
```

**Philosophy**: Decisions without traces are reflexes. Decisions with traces are agency.

### Agent-Friendly Mode (Subagents & Pipelines)

When operating programmatically (subagents, pipelines, scripts):

```bash
# Always use --json for machine-readable output
km "Completed audit" --json              # → {"mark_id": "...", "action": "...", ...}
kg witness show --today --json           # → [{"id": "...", ...}, ...]
kg decide --fast "Choice" --reasoning "Why" --json  # → {"fusion_id": "...", ...}

# Query before acting
kg witness show --grep "extinction" --json   # Search marks
kg witness show --tag composable --json      # Filter by principle
```

**Subagent Protocol**:
1. Query recent marks before starting work (`kg witness show --today --json`)
2. Mark significant actions (`km "Completed X" --json`)
3. Record decisions (`kg decide --fast "..." --json`)
4. Return mark IDs for traceability

See: `docs/skills/witness-for-agents.md`

---

## 🛠️ CLI STRATEGY TOOLS: Evidence-Driven Development

> *"Evidence over intuition. Traces over reflexes. Composition over repetition."*

Five native kgents operations for rigorous development. Full guide: `docs/skills/cli-strategy-tools.md`

### The Five Tools

| Tool | Purpose | When | Output |
|------|---------|------|--------|
| `kg audit` | Validate spec against principles/impl | Before modifying specs, pre-PR | Scores + drift + mark |
| `kg annotate` | Link principles↔impl, capture gotchas | After impl, after bugs | Annotation + mark |
| `kg experiment` | Gather evidence with Bayesian rigor | Uncertain generation, hypothesis | Evidence bundle + marks |
| `kg probe` | Fast categorical law checks | Session start, after composition, CI | Pass/fail + mark on fail |
| `kg compose` | Chain operations with unified trace | Pre-commit, PR, saved workflows | Unified trace |

### Mandatory Usage

**Session Start**:
```bash
kg probe health --all  # First command every session
```

**Before Modifying Spec**:
```bash
kg audit spec/protocols/witness.md --full
```

**After Implementation**:
```bash
kg annotate spec/protocols/witness.md --impl \
  --section "MarkStore" \
  --link "services/witness/store.py:MarkStore"
```

**After Bug Fix**:
```bash
kg annotate spec/relevant.md --gotcha \
  --section "Problematic Section" \
  --note "Don't do X, it causes Y"
```

**When Uncertain**:
```bash
kg experiment generate --spec "..." --adaptive --confidence 0.95
```

**Before Commit**:
```bash
kg compose --run "pre-commit"  # Runs: probe health + audit system
```

### Pre-Saved Compositions

These compositions are ready to use:

| Name | Commands | Use When |
|------|----------|----------|
| `pre-commit` | probe health + audit system | Before any commit |
| `validate-spec` | audit + annotate --show | Before modifying spec |
| `full-check` | audit system + probe all + probe identity | After refactor, pre-PR |

**Philosophy**: Every operation witnesses. Every decision traces. Every composition tells a story.

---

## 📚 SKILLS: Your First Stop

> *"24 skills are necessary and sufficient to build any kgents component."*

**Before doing ANYTHING, consult the relevant skill** in `docs/skills/`. Every task—from adding a state machine to building a responsive UI—has a corresponding skill that will save you hours.

### Universal Skills (Apply to ANY Project)

| Skill | When to Use | Key Insight |
|-------|-------------|-------------|
| **`cli-strategy-tools.md`** | Every session, every commit | Five tools for evidence-driven development: audit, annotate, experiment, probe, compose. |
| **`metaphysical-fullstack.md`** | Building any feature | Every agent is a vertical slice from persistence → projection. No explicit backend routes—AGENTESE IS the API. |
| **`elastic-ui-patterns.md`** | Any responsive UI | Three-mode pattern (Compact/Comfortable/Spacious), content degradation, density-aware constants |

### By Task Type

| Task | Skills to Read |
|------|----------------|
| **Adding new agent** | `polynomial-agent.md` (state machine) |
| **Exposing via AGENTESE** | `agentese-node-registration.md` (@node decorator), `agentese-path.md` (path structure) |
| **Service implementation** | `metaphysical-fullstack.md` (architecture), `data-bus-integration.md` (events) |
| **Hypergraph editing** | `hypergraph-editor.md` (six-mode modal editing, graph navigation, K-Block) |
| **Event-driven feature** | `data-bus-integration.md` (DataBus, SynergyBus, EventBus) |
| **Multi-target rendering** | `projection-target.md` (CLI/TUI/JSON/marimo), `elastic-ui-patterns.md` (responsive) |
| **Writing specs** | `spec-template.md` (structure), `spec-hygiene.md` (bloat patterns to avoid) |

### The Skill Composition Formula

```
Component = Foundation ∘ Protocol ∘ Architecture ∘ Spec ∘ Projection
          = polynomial-agent
          ∘ (agentese-path + agentese-node-registration)
          ∘ (metaphysical-fullstack + data-bus-integration + hypergraph-editor)
          ∘ (spec-template + spec-hygiene)
          ∘ (projection-target + elastic-ui-patterns)
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

### Storage Configuration

All storage uses Docker Postgres by default:

```bash
# Start Postgres
cd impl/claude && docker compose up -d

# Set env and verify (should show "Backend: 🐘 PostgreSQL")
KGENTS_DATABASE_URL="postgresql+asyncpg://kgents:kgents@localhost:5432/kgents" kg brain status
```

See `spec/protocols/storage-migration.md` for migration patterns.

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
├─────────────────────────────────────────────────────────────────────────────┤
│  0. PERSISTENCE LAYER     StorageProvider: membrane.db, vectors, blobs     │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Rules**:
- `services/` = Crown Jewels (Brain, Town, Park...) — domain logic, adapters, frontend
- `agents/` = Infrastructure (PolyAgent, Operad, Flux, D-gent) — categorical primitives
- **No explicit backend routes** — AGENTESE universal protocol IS the API
- **Persistence through D-gent** — All state via `StorageProvider` (XDG-compliant)

**Full Pattern**: See `docs/skills/metaphysical-fullstack.md` and `spec/agents/d-gent.md`

---

## Built Infrastructure (CHECK FIRST!)

**20 production systems** exist. Check `docs/systems-reference.md` before building anything new.

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
docs/skills/    - THE 17 SKILLS (read these!)
plans/          - Meta files only (_focus.md, meta.md)
```

---

## Session Context

**Branch**: `main` | **Session**: 2025-12-20

### What's Happening Now

See `NOW.md` — the one living document that replaces 22 plan files.

**Quick Status**: Brain 100%, Town 70%, Witness 98%, Atelier 75%, Liminal 50%

*Post-Extinction (2025-12-21): Gestalt, Park, Emergence, Coalition, Drills removed. ~52K lines archived.*

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

### ✅ DI Enlightened Resolution (2025-12-21)
```
Container respects Python signature semantics:

REQUIRED deps (no default) → DependencyNotFoundError immediately with helpful message
OPTIONAL deps (= None default) → skipped gracefully, uses default
DECLARED deps (@node(dependencies=(...))) → ALL treated as required

FAIL-FAST: @node validates dependency names at IMPORT time
  If @node(dependencies=("foo",)) but __init__ has no 'foo' param → TypeError
  Error: "@node('path') declares 'foo' but Class.__init__ has no 'foo'"
  This catches mismatches at startup, not at runtime invocation!

THE FIX: For EVERY required dep:
  1. Add get_foo() to services/providers.py
  2. Register: container.register("foo", get_foo, singleton=True)
  3. Names MUST match exactly (case-sensitive)
  4. Field/param name in __init__ MUST match dependency name

To make optional: def __init__(self, foo: Foo | None = None): ...

See: docs/skills/agentese-node-registration.md → "Enlightened Resolution"
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
2. **HEALTH CHECK** — Run `kg probe health --all` at session start
3. **READ SKILLS** — `docs/skills/` has the answer (especially `cli-strategy-tools.md`)
4. **CHECK SYSTEMS** — `docs/systems-reference.md` before building new
5. **AUDIT SPECS** — Run `kg audit <spec> --full` before modifying any spec
6. **ANNOTATE DISCOVERIES** — Capture gotchas with `kg annotate --gotcha`
7. **EXPERIMENT WHEN UNCERTAIN** — Use `kg experiment` for evidence, not guesses
8. **TYPECHECK FRONTEND** — Run `npm run typecheck` after any `.tsx` changes
9. **PRE-COMMIT CHECK** — Run `kg compose --run "pre-commit"` before committing
10. **UPDATE NOW.md** — At session end, update the living document
11. **USE AGENTESE** — The protocol IS the API

---

*Compiled: 2025-12-20 | Version: 4 | Docs Renaissance Edition*
