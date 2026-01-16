# Contributing to kgents

> *"The persona is a garden, not a museum."*

---

## Welcome!

Thank you for your interest in contributing to kgents. Whether you're fixing a typo, adding a feature, or proposing a new agent design, **every contribution matters**.

This project builds tasteful, curated, ethical, joy-inducing agents. We value quality over quantity, depth over breadth, and thoughtful contributions over hurried ones.

**Before contributing, please read our [Code of Conduct](CODE_OF_CONDUCT.md).** We're committed to maintaining a welcoming, inclusive community.

---

## Good First Issues

New to kgents? Start here.

Issues labeled **`good first issue`** are specifically chosen for newcomers:
- They have clear scope and acceptance criteria
- They don't require deep knowledge of categorical foundations
- They include pointers to relevant skills and documentation

**What to expect:**
- **Mentorship** — We'll guide you through the codebase and answer questions
- **Quick review** — First-time PRs get priority review (typically within 48 hours)
- **Patience** — No question is too basic

**Find them:** [GitHub Issues: good first issue](https://github.com/kentgang/kgents/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

---

## Development Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| [uv](https://github.com/astral-sh/uv) | Latest | Python package manager |
| Node.js | 22+ | Frontend runtime |
| npm | Latest | Node package manager |
| Docker | Latest | PostgreSQL (optional but recommended) |

### 1. Fork and Clone

```bash
# Fork on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/kgents.git
cd kgents
git remote add upstream https://github.com/kentgang/kgents.git
```

### 2. Backend Setup

```bash
cd impl/claude
uv sync --dev

# Optional: Start PostgreSQL
docker compose up -d
```

### 3. Frontend Setup

```bash
cd impl/claude/web
npm install
```

### 4. Run the Dev Server

```bash
# Unified dev server (recommended)
cd impl/claude && uv run kg dev
# Backend: http://localhost:8000
# Frontend: http://localhost:3000

# Or run separately in two terminals:
# Terminal 1:
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2:
cd impl/claude/web && npm run dev
```

### 5. Verify Your Setup

```bash
# Backend tests and type checking
cd impl/claude
uv run pytest -q
uv run mypy .

# Frontend type checking and linting
cd impl/claude/web
npm run typecheck
npm run lint
```

All commands should pass with no errors. If something fails, check the prerequisites or open an issue.

---

## Making Changes

### Create a Feature Branch

```bash
git checkout main
git pull upstream main
git checkout -b feat/your-feature-name
```

### Follow Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear history:

| Prefix | Use For |
|--------|---------|
| `feat:` | New features |
| `fix:` | Bug fixes |
| `docs:` | Documentation only |
| `style:` | Formatting, no logic change |
| `refactor:` | Code restructuring |
| `test:` | Adding or fixing tests |
| `chore:` | Maintenance tasks |

**Example:**
```bash
git commit -m "feat(brain): add semantic search to memory crystals"
```

### Run Quality Checks Before Committing

```bash
# If kg CLI is available:
kg probe health --all

# Or run manually:
cd impl/claude
uv run pytest -q && uv run mypy .

cd impl/claude/web
npm run typecheck && npm run lint
```

### Write Tests for New Functionality

- Unit tests go in the same directory as the code (e.g., `services/brain/tests/`)
- Use pytest markers: `@pytest.mark.tier1` for unit, `@pytest.mark.tier2` for integration
- See `docs/skills/test-patterns.md` for the T-gent taxonomy

### Update Relevant Documentation

- If you add a new feature, update the relevant skill in `docs/skills/`
- If you change behavior, update `CLAUDE.md` or `NOW.md` as needed
- Keep documentation close to the code it describes

---

## Pull Request Process

### 1. Push Your Branch

```bash
git push origin feat/your-feature-name
```

### 2. Open a Pull Request

- Use a clear title following conventional commits: `feat(component): description`
- Fill out the PR template completely
- Link related issues with `Closes #123` or `Fixes #456`

### 3. Ensure CI Passes

Our CI runs automatically:
- **Tier 1**: Lint, format, and type checks (< 1 min)
- **Tier 2**: Unit tests across 7 domains in parallel (< 5 min)
- **Tier 3**: Category law verification (< 2 min)
- **Tier 4**: Integration tests (< 5 min)
- **Tier 5**: Property-based tests (< 5 min)

All checks must pass before review.

### 4. Address Review Feedback

- Respond to all comments
- Push fixes as new commits (squash on merge)
- Be patient — reviewers have other responsibilities

### 5. Celebrate When Merged!

Your contribution is now part of kgents. Thank you!

---

## Code Style

### Python

- **Formatter**: `ruff format`
- **Linter**: `ruff check`
- **Type checker**: `mypy --strict` (for core modules)
- **Line length**: 100 characters
- **Style**: Follow existing patterns in the codebase

### TypeScript

- **Formatter**: Prettier
- **Linter**: ESLint with strict TypeScript rules
- **Type checker**: `tsc --noEmit`
- **No `any` types** unless explicitly justified

### Commit Messages

Follow conventional commits with optional scope:

```
feat(brain): add semantic search capability

Implements vector similarity search using pgvector.
Crystals now support k-nearest-neighbor queries.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Tests

- **Markers**: `tier1`, `tier2`, `tier3`, `law`, `property`, `slow`
- **Naming**: `test_<what>_<condition>_<expected>`
- **Philosophy**: DI > mocking, property tests > example tests

See `docs/skills/test-patterns.md` for comprehensive guidance.

---

## Architecture Overview

```
kgents/
├── impl/claude/           # Reference implementation
│   ├── agents/            # Categorical infrastructure (PolyAgent, Operad, Sheaf)
│   ├── services/          # Crown Jewels (Brain, Town, etc.) — business logic
│   ├── protocols/         # AGENTESE, CLI, API
│   ├── bootstrap/         # System initialization
│   ├── runtime/           # Execution environment
│   └── web/               # React frontend
├── spec/                  # Specifications (conceptual, implementation-agnostic)
├── docs/                  # Documentation and skills
└── plans/                 # Planning documents
```

**Key Concepts:**

- **services/** = Crown Jewels — Domain logic, adapters, frontend. This is where business value lives.
- **agents/** = Infrastructure — Categorical primitives (PolyAgent, Operad, Flux). Rarely modified.
- **protocols/** = Interface — AGENTESE (the universal protocol), CLI handlers, API routes.
- **web/** = React frontend — TypeScript, Tailwind, Zustand for state.

**The Metaphysical Fullstack**: Every agent is a vertical slice from persistence to projection. AGENTESE IS the API — no explicit backend routes needed.

Read `docs/skills/metaphysical-fullstack.md` for deep understanding.

---

## Getting Help

### For Questions

- **GitHub Discussions** — Best for conceptual questions, design discussions
- **Issues** — Best for bugs, feature requests with clear scope

### For Learning

- **`docs/skills/`** — 24 skills covering every task
- **`CLAUDE.md`** — Project philosophy and voice anchors
- **`NOW.md`** — Current focus and recent progress

### The Anti-Sausage Protocol

Kent's vision gets diluted through LLM processing. When contributing:

- **Quote directly** — Don't paraphrase voice anchors
- **Preserve rough edges** — Don't smooth opinionated stances
- **The Mirror Test** — "Does this feel like Kent on his best day?"

Voice anchors to preserve:

| Anchor | Use When |
|--------|----------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Making aesthetic decisions |
| *"Tasteful > feature-complete"* | Scoping work |
| *"The persona is a garden, not a museum"* | Discussing evolution |
| *"Depth over breadth"* | Prioritizing work |

---

## Recognition

We believe in celebrating contributors:

- **Co-Authored-By** — Significant contributions get co-author credit in commits
- **Release Notes** — Contributors are mentioned in release announcements
- **AUTHORS.md** — Repeat contributors are listed in the authors file (coming soon)

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

## What to Work On

Not sure where to start?

1. **Good First Issues** — [Labeled issues](https://github.com/kentgang/kgents/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) for newcomers
2. **NOW.md** — Current project focus and priorities
3. **Documentation** — Every docs improvement helps
4. **Tests** — More coverage is always welcome
5. **Bug Reports** — Found something broken? Tell us!

---

*"An agent is a thing that justifies its behavior."*

We can't wait to see what you build.
