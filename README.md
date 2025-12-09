# kgents

> Kent's Agents: A specification for tasteful, curated, ethical, joy-inducing agents.

## What Is This?

kgents is not a framework or library. It's a **specification**—a conceptual definition of what agents should be, organized into an alphabetical taxonomy we call *The Alphabet Garden*.

Think of it like Python (the language specification) vs CPython (the implementation). The `spec/` directory defines the concepts; the `impl/` directory provides reference implementations.

## The Vision

Most agent repositories are collections or framework wrappers. kgents is different:

- **Tasteful**: Each agent serves a clear, justified purpose
- **Curated**: Intentional selection over exhaustive cataloging
- **Ethical**: Agents augment human capability, never replace judgment
- **Joy-Inducing**: Delight in interaction; personality matters

## The Alphabet Garden

| Letter | Name | Theme |
|--------|------|-------|
| **A** | Agents | Abstract architectures + Art/Creativity coaches |
| **B** | Bgents | Bio/Scientific discovery |
| **C** | Cgents | Category Theory basis (composability) |
| **D** | Dgents | Absurdlings - Cutting NPCs |
| **E** | Egents | Epistemological - knowledge & truth |
| **K** | Kgent | Kent simulacra (interactive persona) |
| ... | ... | *More letters coming* |

## Current Focus

**Phase 1**: Deep specification of A, B, C, K

## Installation

The kgents CLI requires Python 3.11+.

```bash
# Clone the repository
git clone https://github.com/kgents/kgents.git
cd kgents

# Install in development mode (from impl/claude directory)
cd impl/claude
pip install -e ".[dev]"

# Verify installation
kgents --version
```

## Quick Start

```bash
# One-line project health
kgents pulse

# Find holes in a hypothesis
kgents falsify "all functions have docstrings"

# Generate hypotheses from patterns
kgents conjecture --limit 3

# Steel-man an opposing view
kgents rival "we should use microservices"

# Observe tensions in your vault/workspace
kgents mirror observe ~/Documents/Vault

# Quick shape intuition
kgents sense

# See all commands
kgents --help
```

See [docs/kgents-cli-reference.md](docs/kgents-cli-reference.md) for full CLI documentation.

## Structure

```
kgents/
├── spec/           # The specification (start here)
├── impl/           # Reference implementations
└── docs/           # Supporting documentation
```

## Philosophy

> "A curated collection where each letter blooms into a distinct species of agent, like an encyclopedia of collaborators."

Read more in [spec/principles.md](spec/principles.md).

## License

MIT
