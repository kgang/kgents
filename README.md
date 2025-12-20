# kgents

**A specification for tasteful, curated, ethical, joy-inducing agents.**

[![Tests](https://img.shields.io/badge/tests-11,170+-brightgreen)](impl/claude)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](pyproject.toml)
[![Mypy](https://img.shields.io/badge/mypy-strict-blue)](impl/claude/mypy.ini)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## Overview

kgents is a **specification-first** agent ecosystem. Like Python (language spec) vs CPython (implementation), this repository separates conceptual definitions (`spec/`) from reference implementations (`impl/`).

The project introduces **AGENTESE**—a verb-first ontology where observation is interaction, nouns are frozen verbs, and agents compose like morphisms in a category.

## Design Principles

1. **Tasteful** - Each agent serves a clear, justified purpose
2. **Curated** - Intentional selection over exhaustive cataloging
3. **Ethical** - Agents augment human capability, never replace judgment
4. **Joy-Inducing** - Personality matters; interaction should delight
5. **Composable** - Agents are morphisms; composition is primary (category theory)
6. **Heterarchical** - Agents exist in flux, not fixed hierarchy
7. **Generative** - Spec is compression; design generates implementation

See [spec/principles.md](spec/principles.md) for the full specification.

## The Alphabet Garden

Agents are organized into an alphabetical taxonomy of genera (25+ implemented):

| Letter | Name | Purpose | Tests |
|--------|------|---------|-------|
| **A** | Agents | Abstract architectures, Alethic algebra | 337+ |
| **B** | Bgents | Token economics, scientific discovery | — |
| **C** | Cgents | Category theory (Functor, Monad, Either, Maybe) | — |
| **D** | Dgents | State management, bicameral memory | — |
| **E** | Egents | Thermodynamic evolution | — |
| **F** | Fgents | Intent grounding, futures | — |
| **Flux** | Streams | Living pipelines, event-driven flows | 382 |
| **G** | Ggents | Grammar inference | — |
| **H** | Hgents | Dialectics (Hegel, Jung, Lacan) | — |
| **I** | Igents | Interface/TUI, semantic fields | 566 |
| **J** | Jgents | JIT compilation, templates | — |
| **K** | Kgent | Kent simulacra (interactive persona) | 589 |
| **L** | Lgents | Semantic registry, lattice | 69 |
| **M** | Mgents | Holographic cartography | — |
| **N** | Ngents | Narrative traces | — |
| **O** | Ogents | Observation functors | — |
| **P** | Pgents | Parsing strategies | — |
| **Ψ** | Psigent | Metaphor engine, pataphysics | 36 |
| **Q** | Qgents | Quartermaster (K8s execution) | — |
| **R** | Rgents | Reasoning, resilience | — |
| **T** | Tgents | Testing (Types I-V), TrustGate | 124 |
| **U** | Ugents | Utility (tools, MCP, execution) | — |
| **W** | Wgents | Wire protocol, interceptors | — |

## AGENTESE Protocol

AGENTESE is the meta-protocol for agent-world interaction. Instead of querying static objects, agents grasp **handles** that yield **affordances** based on observer context.

```python
# Different observers, different perceptions
await logos.invoke("world.house.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.house.manifest", poet_umwelt)       # → Metaphor
```

**The Five Contexts:**
- `world.*` - External entities, environments, tools
- `self.*` - Internal memory, capability, state
- `concept.*` - Abstract platonics, definitions, logic
- `void.*` - Entropy, serendipity, gratitude (the Accursed Share)
- `time.*` - Traces, forecasts, schedules

See [spec/protocols/agentese.md](spec/protocols/agentese.md) for the full specification.

## Installation

Requires Python 3.12+.

```bash
git clone https://github.com/kgang/kgents.git
cd kgents

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e "impl/claude[dev]"

# Verify (both `kg` and `kgents` work)
kg --help
```

## Quick Start

```bash
# K-gent: Interactive persona
kg soul                    # Chat with K-gent (REFLECT mode)
kg soul challenge "idea"   # Dialectic challenge
kg soul dream              # Trigger hypnagogia cycle

# Infrastructure
kg infra init              # Create Kind cluster
kg a list                  # List agent archetypes
kg a inspect Kappa         # Inspect agent capabilities
kg a manifest Kappa        # Generate K8s manifests

# Developer experience
kg status                  # Cortex health dashboard
kg signal                  # Semantic field state
kg map                     # M-gent holographic map
kg tithe                   # Discharge entropy pressure

# Observation
kg observe trace           # Execution traces
kg observe metrics         # Metrics snapshot
```

## Project Structure

```
kgents/
├── spec/                           # Specifications (start here)
│   ├── protocols/                  # AGENTESE, Curator, Blending, Critic
│   ├── k8-gents/                   # K8s CRD specs + protocols
│   ├── principles.md               # Design principles (source of truth)
│   └── {a-z}-gents/                # Agent genus specifications
├── impl/claude/                    # Reference implementation (11,170+ tests)
│   ├── agents/                     # 25+ agent implementations
│   │   ├── a/                      # Alethic algebra, Functor registry
│   │   ├── c/                      # Category theory (Maybe, Either, etc.)
│   │   ├── d/                      # Memory, state, modal scope
│   │   ├── flux/                   # Living pipelines, streams
│   │   ├── i/                      # TUI framework, widgets
│   │   ├── k/                      # K-gent persona, hypnagogia
│   │   ├── l/                      # Lattice, semantic registry
│   │   ├── t/                      # Testing (Types I-V)
│   │   └── ...                     # Other genera
│   ├── protocols/
│   │   ├── agentese/               # AGENTESE runtime
│   │   │   ├── contexts/           # Five context resolvers
│   │   │   ├── metabolism/         # Entropy, fever, tithe
│   │   │   └── middleware/         # Curator
│   │   ├── cli/                    # CLI handlers (20+ commands)
│   │   └── terrarium/              # Mirror protocol, K8s operator
│   ├── infra/
│   │   ├── cortex/                 # LLM integration
│   │   ├── stigmergy/              # Redis pheromone store
│   │   └── k8s/                    # Operators, CRDs, scripts
│   └── shared/                     # Capital, Costs, Budget
├── plans/                          # Forest protocol (living plans)
│   ├── _forest.md                  # Forest canopy (auto-generated)
│   ├── _focus.md                   # Human intent (read-only)
│   └── _status.md                  # Implementation status matrix
├── docs/                           # Documentation
│   ├── functor-field-guide.md      # Alethic Algebra without category theory
│   ├── operators-guide.md          # Scenarios, eigenvectors
│   └── categorical-foundations.md  # Category theory, principles
└── HYDRATE.md                      # Context seed for agents
```

## Key Systems

### Alethic Algebra
Universal functor protocol for agent transformations. Every capability (Stateful, Soulful, Observable, Streamable) compiles through functors with verified laws.

### K-gent: The Governance Functor
Not a chatbot—a categorical imperative. K-gent navigates to specific coordinates in the inherent personality-space of LLMs. Six eigenvectors, four dialogue modes, hypnagogic dream cycles.

### Flux: Living Pipelines
Agents are topological knots in event streams, not static transformations. `Flux.lift(agent)` enables real-time processing with metabolism, pressure, and fever states.

### Semantic Field (Stigmergy)
Agents coordinate via pheromones without direct imports. Emit signals, sense intensity, leave trails for future agents.

### K-Terrarium
Kubernetes-native agent isolation with CRD-driven deployment, live reload development, and graceful degradation to subprocess execution.

## Development

```bash
cd impl/claude

# Type checking (strict mode)
uv run mypy .

# Run tests
uv run pytest -m "not slow" -q

# Lint
uv run ruff check

# Full test suite
uv run pytest
```

## Documentation

| Document | Purpose |
|----------|---------|
| [HYDRATE.md](HYDRATE.md) | Context seed for AI agents |
| [Functor Field Guide](docs/functor-field-guide.md) | Alethic Algebra without category theory |
| [Operator's Guide](docs/operators-guide.md) | Complete operational scenarios |
| [Categorical Foundations](docs/categorical-foundations.md) | Mathematical grounding |
| [Principles](spec/principles.md) | Design principles (source of truth) |

## Philosophy

> "The noun is a lie. There is only the rate of change."

kgents rejects the "noun fallacy" that objects exist statically. Observation collapses potential into actuality. Agents are not things—they are rates of change that compose.

The system embraces the **Accursed Share**: surplus must be spent, not conserved. Entropy pressure triggers creative expenditure. Even urgent tasks leave room for serendipity.

## License

MIT
