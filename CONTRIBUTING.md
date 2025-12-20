# Contributing to kgents

> *"We cherish slop. From raw chaos, beauty emerges."*

---

## The Accursed Share of Contribution

Not every idea becomes a PR. This is intentional.

Curation requires an uncurated pool to select from. Your rejected ideas aren't waste—they're the compost from which the garden grows. We genuinely appreciate proposals even when we say no.

---

## Before You Code

Read these first:

1. **[spec/principles.md](spec/principles.md)** — The seven principles + 12 architectural decisions
2. **[CLAUDE.md](CLAUDE.md)** — How AI agents should work in this codebase
3. **[docs/skills/](docs/skills/)** — The 13 skills that cover every task

Seriously, read the skills. They'll save you hours.

---

## The Mirror Test

Before opening a PR, ask:

> *Does this feel like kgents on its best day?*

- **Daring, bold, creative, opinionated—but not gaudy?**
- **Tasteful > feature-complete?**
- **Joy-inducing > merely functional?**

If the answer to any is "no," iterate.

---

## Development Setup

```bash
cd impl/claude

# Backend
uv sync
uv run pytest -m "not slow" -q  # Quick tests (~2 min)
uv run mypy .                    # Type checking (strict)

# Frontend (if touching .tsx files)
cd web
npm install
npm run typecheck && npm run lint
```

### Running Everything

```bash
# Full test suite (slower)
uv run pytest

# Type check + lint + tests (what CI does)
uv run mypy . && uv run pytest -m "not slow" -q
```

---

## The Hierarchy of Taste

When in doubt, prefer:

| Prefer | Over |
|--------|------|
| Tasteful | Feature-complete |
| Curated | Comprehensive |
| Joy-inducing | Merely functional |
| Composable | Convenient |
| Generative | Heavily documented |

If you have to explain it at length, compress the design, not the explanation.

---

## Commit Convention

```bash
# Format:
<type>(<scope>): <description>

# Examples:
feat(witness): Add trust level L2 capabilities
fix(agentese): Resolve path resolution for void context
docs(readme): Reflect personality in opening section
refactor(flux): Extract perturbation logic to separate module
test(town): Add property-based tests for citizen phase transitions
```

**Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Scopes**: The agent genus or module (e.g., `witness`, `agentese`, `brain`, `flux`)

---

## PR Checklist

Before requesting review:

- [ ] **Tests pass**: `uv run pytest -m "not slow" -q`
- [ ] **Types clean**: `uv run mypy .`
- [ ] **Frontend clean** (if applicable): `npm run typecheck && npm run lint`
- [ ] **Principles honored**: Reviewed against [spec/principles.md](spec/principles.md)
- [ ] **CLAUDE.md consulted**: If touching agent patterns or AGENTESE
- [ ] **Anti-Sausage check**: Voice preserved, not smoothed

---

## The Anti-Sausage Check

Claude sessions smooth rough edges. We fight this with explicit checks:

- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Did I add words the project wouldn't use?*
- ❓ *Did I lose any opinionated stances?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*

If yes to any, revise.

---

## Types of Contributions

### Adding a New Agent

1. Check if it fits an existing genus (A-Z, Ψ, Ω)
2. Read `docs/skills/polynomial-agent.md` and `docs/skills/building-agent.md`
3. Write spec FIRST in `spec/{genus}-gents/`
4. Implement in `impl/claude/agents/{genus}/`
5. Verify category laws hold (identity, associativity)

### Adding an AGENTESE Path

1. Read `docs/skills/agentese-node-registration.md`
2. Use `@node` decorator—it IS the API
3. Register dependencies in `services/providers.py`
4. Frontend derives from registry (no hardcoded paths)

### Adding a Crown Jewel Feature

1. Read `docs/skills/crown-jewel-patterns.md`
2. Follow Container-Owns-Workflow pattern
3. Wire events via SynergyBus
4. Service owns its adapters, frontend, and AGENTESE nodes

### Documentation

- Skills go in `docs/skills/` (13 is a soft target)
- System inventories go in `docs/systems-reference.md`
- Philosophy goes in `spec/principles.md`

---

## What We'll Say No To

Tasteful means saying no. We'll likely reject:

- Kitchen-sink agents that do "everything"
- Features added "just in case"
- Duplicative agents with slight variations
- PRs that break category laws (identity, associativity)
- Code that claims certainty it doesn't have
- Silent error swallowing (always surface failures)

This isn't personal. It's the garden being curated.

---

## Getting Help

- **Issues**: For bugs, feature requests, questions
- **Discussions**: For broader architectural conversations
- **CLAUDE.md**: Context for AI agents working on PRs

---

## The Gratitude Loop

```
Slop → Filter → Curate → Cherish → Compost → Slop
       ↑                                ↓
       └──────── gratitude ─────────────┘
```

We do not resent rejected contributions. We thank them for providing the raw material from which beauty emerges.

---

*"The persona is a garden, not a museum."*
