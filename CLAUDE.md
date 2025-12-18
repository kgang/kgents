  Checkpoint: cf2543d3e45ad80e
# kgents - Kent's Agents

A specification for tasteful, curated, ethical, joy-inducing agents.

## Project Philosophy

- **Specification-first**: Define what agents should be, not just how to build them
- **The Python/CPython model**: `spec/` is the language spec, `impl/` is the reference implementation
- **Alphabetical taxonomy**: Each letter represents a distinct agent genus
- **AGENTESE**: The verb-first ontology for agent-world interaction

## Current Focus

Deeply specifying and implementing the agent ecosystem with AGENTESE as the meta-protocol.

| Letter | Name | Theme | Polynomial |
|--------|------|-------|------------|
| A | Agents | Abstract architectures + Art/Creativity coaches | `ALETHIC_AGENT` |
| B | Bgents | Bio/Scientific discovery + Economics + Distillation | — |
| C | Cgents | Category Theory basis (composability) | — |
| D | Dgents | Data Agents (persistence substrate, WHERE state lives) | `MEMORY_POLYNOMIAL` |
| F | Fgents | Flow (chat, research, collaboration substrate) | `FLOW_POLYNOMIAL` |
| K | Kgent | Kent simulacra (interactive persona) | `SOUL_POLYNOMIAL` |
| L | Lgents | Lattice/Library (semantic registry) | — |
| M | Mgents | Memory/Map (holographic cartography) | — |
| N | Ngents | Narrative (witness/trace) | — |
| S | Sgents | State (threading, HOW state flows through computation) | `STATE_POLYNOMIAL` |
| T | Tgents | Testing (algebraic reliability, Types I-V) | — |
| U | Ugents | Utility (tool use, MCP integration) | — |
| Ψ | Psigent | Psychopomp (metaphor engine) | — |
| Ω | Omegagent | Somatic Orchestrator (morphemes, proprioception, chrysalis) | — |

**Archived**: E-gent (Evolution) archived 2025-12-16. See `impl/claude/agents/_archived/e-gent-archived/`.

**Note**: Polynomial agents (`PolyAgent[S, A, B]`) capture state-dependent behavior. See `docs/skills/polynomial-agent.md`.

**Archived**: Y-gent (Y-Combinator) has been subsumed by the Turn Protocol + F-gent research flow. See `spec/y-gents-archived/MIGRATION.md`.

## Core Principles (Summary)

1. **Tasteful** - Each agent serves a clear, justified purpose.
2. **Curated** - Intentional selection over exhaustive cataloging.
3. **Ethical** - Agents augment human capability, never replace judgment.
4. **Joy-Inducing** - Delight in interaction
5. **Composable** - Agents are morphisms in a category
6. **Heterarchical** - Agents exist in flux, not fixed hierarchy
7. **Generative** - Spec is compression

### The Unified Categorical Foundation

> *"The same categorical structure underlies everything. This is not coincidence—it is the ground."*

All kgents domains instantiate the same three-layer pattern:

| Layer | Purpose | Examples |
|-------|---------|----------|
| **PolyAgent** | State machine with mode-dependent inputs | CitizenPolynomial, SOUL_POLYNOMIAL, MEMORY_POLYNOMIAL, FLOW_POLYNOMIAL |
| **Operad** | Composition grammar with laws | TOWN_OPERAD, NPHASE_OPERAD, SOUL_OPERAD, FLOW_OPERAD |
| **Sheaf** | Global coherence from local views | TownSheaf, ProjectSheaf, EigenvectorCoherence |

**Key Insight**: Understanding one domain teaches you the others.

See: `spec/principles.md` for full principles

## AGENTESE: The Verb-First Ontology

> *"The noun is a lie. There is only the rate of change."*

AGENTESE is the meta-protocol for agent-world interaction. Instead of querying a database of nouns, agents grasp **handles** that yield **affordances** based on who is grasping.

**Spec**: `spec/protocols/agentese.md`
**Impl**: `impl/claude/protocols/agentese/`

### The Five Contexts

```
world.*    - The External (entities, environments, tools)
self.*     - The Internal (memory, capability, state)
concept.*  - The Abstract (platonics, definitions, logic)
void.*     - The Accursed Share (entropy, serendipity, gratitude)
time.*     - The Temporal (traces, forecasts, schedules)
```

### Core Insight

Traditional systems: `world.house` returns a JSON object.
AGENTESE: `world.house` returns a **handle**—a morphism that maps Observer → Interaction.

```python
# Different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
await logos.invoke("world.house.manifest", economist_umwelt)  # → Appraisal
```

### Key Aspects

| Aspect | Category | Meaning |
|--------|----------|---------|
| `manifest` | Perception | Collapse to observer's view |
| `witness` | Perception | Show history (N-gent) |
| `refine` | Generation | Dialectical challenge |
| `sip` | Entropy | Draw from Accursed Share |
| `tithe` | Entropy | Pay for order (gratitude) |
| `lens` | Composition | Get composable agent |
| `define` | Generation | Autopoiesis (create new) |

## Built Infrastructure (CHECK FIRST!)

**17 production systems** are fully implemented. Before building anything new, check `docs/systems-reference.md`.

| Category | Systems |
|----------|---------|
| **Categorical** | PolyAgent, Operad, Sheaf (use for ANY domain) |
| **Streaming** | Flux (discrete → continuous agents) |
| **Event-Driven** | DataBus, SynergyBus, EventBus (reactive data flow) |
| **Semantics** | AGENTESE (8 phases shipped: parser, JIT, laws, wiring) |
| **Simulation** | Agent Town (citizens, coalitions, dialogue) |
| **Soul** | K-gent (LLM dialogue, hypnagogia, gatekeeper) |
| **Memory** | M-gent (crystals, cartography, stigmergy) |
| **UI** | Reactive (Signal/Computed/Effect → CLI/marimo/JSON) |
| **Lifecycle** | N-Phase compiler (YAML → prompts) |
| **Gateway** | Terrarium (REST bridge, metrics) |
| **SaaS** | API, Billing (Stripe), Licensing (tiers), Tenancy (multi-tenant) |

## Key Directories

- `spec/` - The specification (conceptual, implementation-agnostic)
- `impl/` - Reference implementations (Claude Code + Open Router)
- `impl/claude/web/` - Agent Town React frontend (see `web/README.md`)
- `plans/` - Forest Protocol plans

## Docs Quick Reference (5 core + 13 skills)

| Doc | When to Read |
|-----|--------------|
| `docs/systems-reference.md` | **Before building ANYTHING** |
| `docs/local-development.md` | Setting up locally |
| `docs/quickstart.md` | First time setup |
| `docs/architecture-overview.md` | Understanding the design |
| `docs/categorical-foundations.md` | When you need the "why" |
| `docs/skills/` | How to build specific things (13 minimal skills) |

## Running Locally

```bash
# Terminal 1: Backend API
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Web UI
cd impl/claude/web
npm install && npm run dev
# Visit http://localhost:3000
```

See `docs/local-development.md` for detailed setup and troubleshooting.

## Session Context

**Branch**: `main` | **Session**: 2025-12-18


## Current Focus (Forest Protocol)

**Forest Health**: 31 active, 22 complete, 43% avg

### Active Plans

| Plan | Progress | Status |
|------|----------|--------|
| atelier-experience | 75% | active |
| coalition-forge | 55% | active |
| punchdrunk-park | 40% | active |
| domain-simulation | 0% | active (stub) |

### Recently Completed

| Plan | Completed |
|------|-----------|
| design-language-consolidation | 2025-12-18 |
| gardener-logos | 2025-12-16 |


## The Metaphysical Agent Stack (AD-009)

> *"Every agent is a vertical slice from persistence to projection."*

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

**Key Insight**: Understanding ONE layer teaches you ALL layers.

**Full Spec**: `plans/autopoietic-architecture.md`

## Minimal Skills (13 Total)

> *"13 skills are necessary and sufficient to build any kgents component."*

These skills compose: `Component = Foundation ∘ Protocol ∘ Architecture ∘ Process ∘ Projection`

| Category | Skills |
|----------|--------|
| **Foundation** | `polynomial-agent.md`, `building-agent.md` |
| **Protocol** | `agentese-path.md`, `agentese-node-registration.md` |
| **Architecture** | `crown-jewel-patterns.md`, `metaphysical-fullstack.md`, `data-bus-integration.md` |
| **Process** | `plan-file.md`, `spec-template.md`, `spec-hygiene.md` |
| **Projection** | `projection-target.md`, `test-patterns.md`, `elastic-ui-patterns.md` |

Extended skills archived to `docs/_archive/2025-12-18-consolidation/`. Restore if needed.

## Working With This Repo

- **CHECK `docs/systems-reference.md` BEFORE assuming you need to build something new**
- When adding new agent concepts, **start in `spec/`**
- Implementations should faithfully follow specs
- Composability is paramount (C-gents principles apply everywhere)
- Read `spec/principles.md` before contributing
- **Use AGENTESE paths** for agent-world interaction when possible
- **Consult skills** in `docs/skills/` for common patterns

## DevEx Commands (Slash Commands)

| Command | Purpose |
|---------|---------|
| `/harden <target>` | Robustify, shore up durability of a module |
| `/trace <target>` | Trace execution paths and data flow |
| `/diff-spec <spec>` | Compare implementation against specification |
| `/debt <path>` | Technical debt audit |

## Critical Learnings (Distilled)

> *One insight per line. From `plans/meta.md`.*

### Categorical (The Ground)
```
PolyAgent[S,A,B] > Agent[A,B]: mode-dependent behavior enables state machines
Operads define grammar; algebras apply grammar to systems
Sheaf gluing = emergence: compatible locals → global
Functor law verification proves composition: if laws pass, arbitrary nesting is safe
```

### Graceful Degradation
```
Tier cascade: TEMPLATE never fails; budget exhaustion → graceful fallback
Two-tier collection: try context, fallback direct
Template fallbacks make CLI commands work without LLM
Optional dep stubs: no-op stubs for type-checking; document intent, not silent failure
```

### Testing
```
DI > mocking: set_soul() injection pattern beats patch() for testability
Property-based tests catch edge cases: Hypothesis found boundary issues humans missed
Performance baselines as assertions: `assert elapsed < 1.0` catches regressions
Stress test phase machines: Hypothesis with action sequences reveals invalid transitions
```

### Anti-Patterns (Avoid These)
```
Silent catch blocks: swallowing errors shows blank UI; always surface
Generator Trap: pickle can't serialize stack frames—use Purgatory pattern
Timer-driven loops create zombies—use event-driven Flux
Bypassing running loops causes state schizophrenia
Context dumping: large payloads tax every turn
```

### AGENTESE Discovery
```
@node runs at import time: If module not imported, node not registered
_import_node_modules() in gateway.py: Ensures all nodes load before discovery
Two-way mapping needed: AGENTESE path ↔ React route in NavigationTree
Discovery is pull-based: Frontend fetches /agentese/discover to build tree
crown_jewels.py PATHS are docs only: Use @node decorator for discoverability
```

### Event-Driven Architecture
```
Three buses: DataBus (storage) → SynergyBus (cross-jewel) → EventBus (fan-out)
DataBus guarantees: at-least-once, causal ordering, non-blocking, bounded buffer
SynergyBus: fire-and-forget with handler isolation; use factory functions for events
EventBus: backpressure via bounded queues; slow subscribers get dropped events
Bridge pattern: DataBus → SynergyBus via wire_data_to_synergy()
```

### Design Heuristics
```
Skills pull before doing, push after learning
Wiring > Creation: check if infrastructure exists before building new
Teaching examples > reference docs: show the pattern in action
String-based >> composition: "path.a" >> "path.b" natural idiom
D-gent = WHERE state lives; S-gent = HOW state flows—placement matters
```

---

*Compiled: 2025-12-18T09:00:00 | Version: 2 | Sections: 10*
