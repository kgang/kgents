# Contributing to kgents

> *"The persona is a garden, not a museum."*

---

## Before You Start

1. **Read the skills** — `docs/skills/` contains 21 skills covering every task. Read the relevant skill before writing code.

2. **Run hydration** — Before any task: `kg docs hydrate "<your task>"` to surface gotchas.

3. **Understand the architecture** — Read [CLAUDE.md](CLAUDE.md) for the Anti-Sausage Protocol and voice anchors.

---

## Development Setup

### Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Node.js 18+
- Docker (optional, for PostgreSQL)

### Install

```bash
git clone https://github.com/kentgang/kgents.git && cd kgents
uv sync

cd impl/claude/web && npm install
```

### Run

```bash
# Terminal 1: Backend
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web
npm run dev
```

---

## Quality Gates (MANDATORY)

**All PRs must pass these checks:**

```bash
# Backend
cd impl/claude
uv run pytest -q           # Tests must pass
uv run mypy .              # Type checking must pass

# Frontend (DO NOT SKIP)
cd impl/claude/web
npm run typecheck          # TypeScript must compile
npm run lint               # Linting must pass
```

**Frontend typecheck is NOT optional.** It catches real bugs that break production.

---

## Making Changes

### The Anti-Sausage Protocol

Kent's voice gets diluted through LLM processing. When working with AI assistance:

- **Quote directly** — Don't paraphrase voice anchors
- **Preserve rough edges** — Don't smooth opinionated stances
- **The Mirror Test** — "Does this feel like Kent on his best day?"

### Voice Anchors

| Anchor | Use When |
|--------|----------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making aesthetic decisions |
| *"Tasteful > feature-complete"* | Scoping work |
| *"The persona is a garden, not a museum"* | Discussing evolution |
| *"Depth over breadth"* | Prioritizing work |

### Code Style

- **Python**: Follow existing patterns. Use type hints. `mypy` strict mode.
- **TypeScript**: Follow existing patterns. No `any` types unless justified.
- **Tests**: See `docs/skills/test-patterns.md` for T-gent taxonomy.

---

## Pull Request Process

1. **Branch**: Create from `main`
2. **Test**: Ensure all quality gates pass
3. **Describe**: Explain what and why
4. **Review**: Wait for review before merging

### Commit Messages

```
feat(component): Short description

Longer explanation if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## What to Work On

- Check `NOW.md` for current focus
- Check `plans/` for active work
- Issues labeled `good first issue` are welcoming

---

## The Seven Principles

Every contribution should embody:

1. **Tasteful** — Clear, justified purpose
2. **Curated** — Quality over quantity
3. **Ethical** — Augment humans, never replace judgment
4. **Joy-Inducing** — Warmth over coldness
5. **Composable** — Agents must compose (`>>`)
6. **Heterarchical** — No fixed hierarchies
7. **Generative** — Spec is compression

---

## Questions?

- Read `CLAUDE.md` for AI-specific guidance
- Read `docs/skills/` for task-specific patterns
- Open an issue if something's unclear

---

*"An agent is a thing that justifies its behavior."*
