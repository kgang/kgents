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
| D | Dgents | Data Agents (state, memory, persistence) | `MEMORY_POLYNOMIAL` |
| E | Egents | Evolution (teleological thermodynamics) | `EVOLUTION_POLYNOMIAL` |
| K | Kgent | Kent simulacra (interactive persona) | `SOUL_POLYNOMIAL` |
| L | Lgents | Lattice/Library (semantic registry) | — |
| M | Mgents | Memory/Map (holographic cartography) | — |
| N | Ngents | Narrative (witness/trace) | — |
| T | Tgents | Testing (algebraic reliability, Types I-V) | — |
| U | Ugents | Utility (tool use, MCP integration) | — |
| Y | Ygent | Y-Combinator (cognitive + somatic topology) | — |
| Ψ | Psigent | Psychopomp (metaphor engine) | — |
| Ω | Omegagent | Somatic Orchestrator (morphemes, proprioception) | — |

**Note**: Polynomial agents (`PolyAgent[S, A, B]`) capture state-dependent behavior. See `plans/skills/polynomial-agent.md`.

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

## Key Directories

- `spec/` - The specification (conceptual, implementation-agnostic)
- `spec/protocols/agentese.md` - AGENTESE specification
- `impl/` - Reference implementations (Claude Code + Open Router)
- `impl/claude/protocols/agentese/` - AGENTESE implementation (559 tests)
- `docs/` - Supporting documentation

## Working With This Repo

- When adding new agent concepts, **start in `spec/`**
- Implementations should faithfully follow specs
- Composability is paramount (C-gents principles apply everywhere)
- Read `spec/principles.md` before contributing
- **Use AGENTESE paths** for agent-world interaction when possible
- **Consult skills** in `plans/skills/` for common patterns

## DevEx Commands (Slash Commands)

| Command | Purpose |
|---------|---------|
| `/harden <target>` | Robustify, shore up durability of a module |
| `/trace <target>` | Trace execution paths and data flow |
| `/diff-spec <spec>` | Compare implementation against specification |
| `/debt <path>` | Technical debt audit |

## Skills Directory

`plans/skills/` contains documented patterns for common tasks:

| Skill | Description |
|-------|-------------|
| `agentese-path.md` | Adding AGENTESE paths (e.g., `self.soul.*`) |
| `building-agent.md` | Creating `Agent[A, B]` with functors |
| `cli-command.md` | Adding CLI commands to kgents |
| `flux-agent.md` | Lifting agents to stream processing |
| `handler-patterns.md` | CLI handler patterns |
| `plan-file.md` | Forest Protocol plan files |
| `polynomial-agent.md` | Creating `PolyAgent[S, A, B]` with state machines |
| `test-patterns.md` | Testing conventions and fixtures |

## Core Principles (Summary)

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary
6. **AGENTESE** - No view from nowhere; observation is interaction
