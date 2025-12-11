# kgents

**A specification for tasteful, curated, ethical, joy-inducing agents.**

[![Tests](https://img.shields.io/badge/tests-7,025+-brightgreen)](impl/claude)
[![Python](https://img.shields.io/badge/python-3.11+-blue)](pyproject.toml)
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
6. **AGENTESE** - No view from nowhere; observation is interaction

## The Alphabet Garden

Agents are organized into an alphabetical taxonomy of genera:

| Letter | Name | Purpose |
|--------|------|---------|
| **A** | Agents | Abstract architectures, creativity coaches |
| **B** | Bgents | Token economics, scientific discovery |
| **C** | Cgents | Category theory basis (composability laws) |
| **D** | Dgents | State management, bicameral memory |
| **E** | Egents | Thermodynamic evolution, viral libraries |
| **F** | Fgents | Intent grounding, gravity wrappers |
| **G** | Ggents | Grammar inference, fuzzing integration |
| **H** | Hgents | System introspection |
| **I** | Igents | Interface/TUI, semantic fields |
| **J** | Jgents | JIT compilation, template generation |
| **K** | Kgent | Kent simulacra (interactive persona) |
| **L** | Lgents | Semantic registry, vector search |
| **M** | Mgents | Holographic cartography, memory orientation |
| **N** | Ngents | Narrative traces, chronicle witness |
| **O** | Ogents | Observation, panopticon integration |
| **P** | Pgents | Parsing strategies |
| **Q** | Qgents | Quartermaster (K8s disposable execution) |
| **R** | Rgents | Reasoning |
| **T** | Tgents | Testing, MCP integration |
| **W** | Wgents | Wire protocol, interceptor pipelines |
| **Ψ** | Psigent | Metaphor engine, morphic transformations |

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

Requires Python 3.11+.

```bash
git clone https://github.com/kgang/kgents.git
cd kgents

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e "impl/claude[dev]"

# Verify
kgents --help
```

## Quick Start

```bash
# Infrastructure (K-Terrarium)
kgents infra init              # Create Kind cluster
kgents infra apply b-gent      # Deploy agent via CRD
kgents dev b-gent              # Live reload development

# Developer experience
kgents status                  # Cortex health dashboard
kgents signal                  # Semantic field state
kgents map                     # M-gent holographic map

# Analysis
kgents pulse                   # Project health
kgents falsify "hypothesis"    # Find counterexamples
kgents conjecture --limit 3    # Generate hypotheses
```

## Project Structure

```
kgents/
├── spec/                      # Specifications (start here)
│   ├── protocols/             # AGENTESE, Umwelt, etc.
│   ├── principles.md          # Design principles
│   └── [a-z]-gents/           # Agent genus specifications
├── impl/                      # Reference implementations
│   └── claude/                # Claude Code implementation
│       ├── agents/            # 20+ agent implementations
│       ├── protocols/         # AGENTESE runtime
│       ├── infra/             # K-Terrarium (K8s)
│       └── testing/           # Test infrastructure
└── docs/                      # Supporting documentation
```

## Key Systems

### Instance DB - Bicameral Memory
Left-brain (relational) + right-brain (vector) memory with active inference routing.

### Semantic Field
Stigmergic coordination via pheromones—agents emit/sense signals without direct imports.

### K-Terrarium
Kubernetes-native agent isolation with CRD-driven deployment and live reload development.

### W-gent Interceptors
Pipeline-based message processing: Safety → Metering → Telemetry → Persona.

## Development

```bash
# Run tests
pytest -m "not slow" -q

# Type checking (with baseline)
cd impl/claude && uv run mypy --strict agents/ 2>&1 | uv run mypy-baseline filter

# Lint
ruff check .
```

## Philosophy

> "The noun is a lie. There is only the rate of change."

kgents rejects the "noun fallacy" that objects exist statically. Observation collapses potential into actuality. Agents are not things—they are rates of change that compose.

Read more in [spec/principles.md](spec/principles.md).

## License

MIT
