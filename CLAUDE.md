# kgents - Kent's Agents

A specification for tasteful, curated, ethical, joy-inducing agents.

## Project Philosophy

- **Specification-first**: Define what agents should be, not just how to build them
- **The Python/CPython model**: `spec/` is the language spec, `impl/` is the reference implementation
- **Alphabetical taxonomy**: Each letter represents a distinct agent genus

## Current Focus (Phase 1)

Deeply specifying: **A-gents, B-gents, C-gents, K-gent**

| Letter | Name | Theme |
|--------|------|-------|
| A | Agents | Abstract architectures + Art/Creativity coaches |
| B | Bgents | Bio/Scientific discovery |
| C | Cgents | Category Theory basis (composability) |
| D | Dgents | Data Agents (state, memory, persistence) |
| K | Kgent | Kent simulacra (interactive persona) |

## Key Directories

- `spec/` - The specification (conceptual, implementation-agnostic)
- `impl/` - Reference implementations (Claude Code + Open Router)
- `docs/` - Supporting documentation

## Working With This Repo

- When adding new agent concepts, **start in `spec/`**
- Implementations should faithfully follow specs
- Composability is paramount (C-gents principles apply everywhere)
- Read `spec/principles.md` before contributing

## Core Principles (Summary)

1. **Tasteful** - Quality over quantity
2. **Curated** - Intentional selection
3. **Ethical** - Augment, don't replace judgment
4. **Joy-Inducing** - Personality encouraged
5. **Composable** - Agents are morphisms; composition is primary
