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

**16 production systems** are fully implemented. Before building anything new, check `docs/systems-reference.md`.

| Category | Systems |
|----------|---------|
| **Categorical** | PolyAgent, Operad, Sheaf (use for ANY domain) |
| **Streaming** | Flux (discrete → continuous agents) |
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
- `spec/protocols/agentese.md` - AGENTESE specification
- `spec/protocols/projection.md` - Projection Protocol (CLI/TUI/marimo/JSON/VR)
- `spec/protocols/auto-inducer.md` - Phase transition signifiers
- `impl/` - Reference implementations (Claude Code + Open Router)
- `impl/claude/protocols/agentese/` - AGENTESE implementation (559 tests)
- `impl/claude/agents/i/reactive/` - Reactive substrate (widgets, projections)
- `docs/` - Supporting documentation
- `docs/skills` - Project specific procedural knowledge
- `docs/systems-reference.md` - **Full inventory of built systems**
- `docs/local-development.md` - **Local dev setup guide**
- `impl/claude/web/` - Agent Town React frontend (see `web/README.md`)

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

**Branch**: `main` | **Session**: 2025-12-16 12:47


## Current Focus (Forest Protocol)

**Forest Health**: 32 active, 20 complete, 28% avg

### Active Plans

| Plan | Progress | Status |
|------|----------|--------|
| coalition-forge | 40% | active |
| domain-simulation | 35% | active |
| punchdrunk-park | 50% | active |
| atelier-experience | 60% | active |
| gardener-logos | 100% | **complete** |


## Skills Directory

`docs/skills/` contains 41 documented patterns for common tasks:

| Skill | Description |
|-------|-------------|
| `agentese-path.md` | Adding AGENTESE paths (e.g., `self.soul.*`) |
| `building-agent.md` | Creating `Agent[A, B]` with functors |
| `cli-command.md` | Adding CLI commands to kgents |
| `crown-jewel-patterns.md` | Reusable patterns for all Crown Jewels |
| `flux-agent.md` | Lifting agents to stream processing |
| `gardener-logos.md` | Tending Calculus, Seasons, Auto-Inducer |
| `handler-patterns.md` | CLI handler patterns |
| `plan-file.md` | Forest Protocol plan files |
| `polynomial-agent.md` | Creating `PolyAgent[S, A, B]` with state machines |
| `spec-hygiene.md` | **NEW** Bloat patterns, compression patterns, distillation checklist |
| `spec-template.md` | **NEW** Structure for writing spec files (200-400 lines) |
| `test-patterns.md` | Testing conventions and fixtures |
| `ux-reference-patterns.md` | Cross-cutting UX patterns from research |
| `user-flow-documentation.md` | Documenting precise user flows with ASCII wireframes |
| `3d-lighting-patterns.md` | 3D Lighting and Visual Clarity Patterns |
| `agent-observability.md` | Agent Observability |
| `agent-town-archetypes.md` | Agent Town Archetypes |
| `agent-town-coalitions.md` | Agent Town Coalitions |
| `agent-town-inhabit.md` | Agent Town INHABIT Mode |

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

### Design Heuristics
```
Skills pull before doing, push after learning
Wiring > Creation: check if infrastructure exists before building new
Teaching examples > reference docs: show the pattern in action
String-based >> composition: "path.a" >> "path.b" natural idiom
D-gent = WHERE state lives; S-gent = HOW state flows—placement matters
```

---

*Compiled: 2025-12-16T12:47:08 | Version: 1 | Sections: 10*
