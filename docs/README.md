---
context: self
---

# kgents Documentation

> *"Read the skills first. They'll save you hours."*

---

## Where to Start

| Your Goal | Start Here |
|-----------|------------|
| Get running in 5 minutes | [quickstart.md](quickstart.md) |
| Understand the philosophy | [concept/principles.md](concept/principles.md) |
| Build a feature | [skills/](skills/) (the 13 essential skills) |
| Understand the architecture | [architecture-overview.md](architecture-overview.md) |
| Check what's already built | [systems-reference.md](systems-reference.md) |

---

## Skills — Read These First

The [skills/](skills/) directory contains 13 curated skills that cover every task. They're organized by layer:

| Layer | Skills |
|-------|--------|
| **Foundation** | [polynomial-agent](skills/polynomial-agent.md), [building-agent](skills/building-agent.md) |
| **Protocol** | [agentese-path](skills/agentese-path.md), [agentese-node-registration](skills/agentese-node-registration.md) |
| **Architecture** | [crown-jewel-patterns](skills/crown-jewel-patterns.md), [metaphysical-fullstack](skills/metaphysical-fullstack.md), [data-bus-integration](skills/data-bus-integration.md) |
| **Projection** | [projection-target](skills/projection-target.md), [elastic-ui-patterns](skills/elastic-ui-patterns.md), [3d-projection-patterns](skills/3d-projection-patterns.md) |
| **Process** | [plan-file](skills/plan-file.md), [spec-template](skills/spec-template.md), [spec-hygiene](skills/spec-hygiene.md) |
| **Testing** | [test-patterns](skills/test-patterns.md) |

---

## Documentation Index

### Getting Started
- [quickstart.md](quickstart.md) — Zero to agent in 5 minutes
- [local-development.md](local-development.md) — Development environment setup

### Architecture
- [architecture-overview.md](architecture-overview.md) — How the pieces fit
- [systems-reference.md](systems-reference.md) — Built infrastructure inventory
- [categorical-foundations.md](categorical-foundations.md) — The math behind it

### Skills (The Craft)
- [skills/README.md](skills/README.md) — Index of 13 essential skills

### Specialized Topics
- [terminal-integration.md](terminal-integration.md) — Tmux and raw mode handling

### Archived
- [_archive/](\_archive/) — Consolidated historical docs (2025-12-18)

---

## The Hierarchy

```
README.md (this file)
├── Getting Started
│   ├── quickstart.md         — Zero to agent
│   └── local-development.md  — Dev setup
├── Architecture
│   ├── architecture-overview.md  — How pieces fit
│   ├── systems-reference.md      — What's built
│   └── categorical-foundations.md — The math
├── Skills (read first!)
│   └── skills/*.md           — The 13 skills
└── Specialized
    └── terminal-integration.md — Tmux/raw mode
```

---

## For AI Agents

If you're an AI agent working in this codebase, read:

1. [../CLAUDE.md](../CLAUDE.md) — Your context and instructions
2. [skills/](skills/) — The 13 skills that cover every task
3. [concept/principles.md](concept/principles.md) — The seven principles

Especially important: the **Anti-Sausage Protocol** in CLAUDE.md. Voice preservation matters.

---

## AGENTESE Context Mapping

Each doc is annotated with an AGENTESE context in its frontmatter:

| Context | Docs | Purpose |
|---------|------|---------|
| `world` | quickstart | External-facing, for visitors |
| `self` | skills/, systems-reference, local-development | Internal, for developers |
| `concept` | principles, architecture, categorical-foundations | Abstract, theory |

This enables future tooling without disrupting existing navigation.

---

*"The persona is a garden, not a museum."*
