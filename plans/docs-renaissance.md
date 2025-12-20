# Documentation Renaissance Plan

> *"The noun is a lie. There is only the rate of change."*
> — kgents Principle

---

## Phase 1: Deep Audit Findings

### Current State Assessment

**Root-Level Files:**
| File | Status | Issues |
|------|--------|--------|
| `README.md` | ⚠️ Competent but corporate | Missing soul. Technically accurate but reads like enterprise docs. Doesn't reflect "daring, bold, creative, opinionated but not gaudy" |
| `CLAUDE.md` | ✅ Strong | This IS the voice anchor. Skills-first, anti-sausage protocol included |
| `NOW.md` | ✅ Living | Current session state, regularly updated |
| `HYDRATE.md` | ⚠️ Narrow scope | Only covers tmux/terminal integration. Name suggests broader purpose |
| `CHANGELOG.md` | ⚠️ Sparse | Two releases only, last update 2025-12-14 |
| **CONTRIBUTING.md** | ❌ Missing | Critical gap for open-source project |
| **LICENSE** | ✅ Present | MIT |

**docs/ Directory:**
| Area | Status | Notes |
|------|--------|-------|
| `docs/skills/` | ✅ Excellent | 13 curated skills, well-organized, practical |
| `docs/architecture-overview.md` | ✅ Good | Comprehensive technical reference |
| `docs/quickstart.md` | ⚠️ Dry | Functional but joyless. Missing personality |
| `docs/systems-reference.md` | ✅ Good | Exhaustive inventory of built infrastructure |
| `docs/_archive/` | ✅ Appropriate | Consolidated old docs properly |
| `docs/categorical-foundations.md` | ✅ Good | Math grounding for those who want it |

**spec/ Directory:**
| Area | Status | Notes |
|------|--------|-------|
| `spec/principles.md` | ✅ Excellent | THE source of truth. 12 ADs, 7 principles, rich |
| `spec/{a-z}-gents/` | ✅ Good | Genus specifications, well-structured |
| `spec/protocols/` | ✅ Good | Protocol specifications |

### The Voice Problem

The README and quickstart docs have a **voice dilution problem**:

1. **Too enterprise**: Reads like AWS documentation
2. **Missing opinionated stance**: Neutral when it should be bold
3. **No joy-inducing elements**: All function, no delight
4. **Buried philosophy**: The "accursed share" and "noun fallacy" are hidden

Compare:
- ❌ Current: "kgents is a specification-first agent ecosystem"
- ✅ Better: "kgents rejects the noun fallacy. Agents aren't things—they're rates of change that compose."

### The Structure Problem

1. **No CONTRIBUTING.md**: Essential for community
2. **HYDRATE.md mismatch**: Name suggests context seeding for agents, content is terminal integration learnings
3. **docs/ lacks narrative arc**: Good reference docs, no journey from "curious" to "confident"
4. **No examples/ directory**: Quickstart examples are inline only

---

## Phase 2: Documentation Vision

### The Hierarchy of Reader Needs

```
                    ╭─────────────────────────────────────╮
                    │        CURIOUS VISITOR              │
                    │   "What is this? Why should I care?"│
                    ╰────────────────┬────────────────────╯
                                     │
                    ╭────────────────▼────────────────────╮
                    │       EVALUATING USER               │
                    │   "Can I use this? Will it work?"   │
                    ╰────────────────┬────────────────────╯
                                     │
                    ╭────────────────▼────────────────────╮
                    │        ACTIVE DEVELOPER             │
                    │   "How do I build with this?"       │
                    ╰────────────────┬────────────────────╯
                                     │
                    ╭────────────────▼────────────────────╮
                    │      CONTRIBUTING MEMBER            │
                    │   "How do I make this better?"      │
                    ╰─────────────────────────────────────╯
```

Each layer needs different documentation.

### The Personality Manifesto

Documentation should embody:

1. **Daring**: Bold claims, opinionated stances
2. **Bold**: Direct language, no hedging
3. **Creative**: Unexpected metaphors, joy-inducing examples
4. **Opinionated**: Clear recommendations, anti-patterns called out
5. **Not gaudy**: Restrained elegance, no emoji spam, substance over flash

### Target Document Structure

```
kgents/
├── README.md              ← THE INVITATION (curiosity → installation)
├── CONTRIBUTING.md        ← THE WELCOME (how to participate)
├── CHANGELOG.md           ← THE HISTORY (what changed)
├── LICENSE                ← MIT
├── NOW.md                 ← THE MOMENT (living session state)
├── CLAUDE.md              ← THE COMPASS (agent context)
├── docs/
│   ├── README.md          ← DOCS INDEX (navigation aid)
│   ├── philosophy.md      ← THE WHY (principles, theory)
│   ├── quickstart.md      ← THE HOW (zero to agent)
│   ├── architecture-overview.md
│   ├── systems-reference.md
│   ├── categorical-foundations.md
│   ├── skills/            ← THE CRAFT (13 skills)
│   ├── examples/          ← THE TASTE (runnable examples)
│   │   ├── hello-world.py
│   │   ├── composition.py
│   │   ├── functors.py
│   │   └── streaming.py
│   └── gallery/           ← THE GALLERY (visual showcase)
└── spec/                  ← THE LAW (specifications)
```

---

## Phase 3: Specific Rewrites

### 3.1 README.md — The Invitation

**Current**: 249 lines, technically accurate, soulless.

**Proposed Structure**:

```markdown
# kgents

> The noun is a lie. There is only the rate of change.

**kgents** isn't just another agent framework. It's a philosophical stance:
agents are morphisms in a category, not objects in a database.
They compose. They observe. They become.

## The Seven Principles (Quick)

1. **Tasteful** — Say "no" more than "yes"
2. **Curated** — Quality over quantity
3. **Ethical** — Augment, never replace, judgment
4. **Joy-Inducing** — Personality matters
5. **Composable** — Agents are morphisms (`>>`)
6. **Heterarchical** — No fixed hierarchy
7. **Generative** — Spec is compression

## See It

[ASCII art or screenshot of the system in action]

## Feel It

```python
from agents import agent

# Agents compose like functions
pipeline = parse >> validate >> transform >> store

# But with governance
from agents.k import soul
governed = soul.lift(pipeline)  # Now it thinks before acting
```

## Install It

```bash
git clone https://github.com/kgang/kgents.git && cd kgents
uv sync && kg --help
```

## Explore It

- **[Quickstart](docs/quickstart.md)** — Zero to agent in 5 minutes
- **[Philosophy](docs/philosophy.md)** — Why kgents exists
- **[Architecture](docs/architecture-overview.md)** — How it works
- **[Skills](docs/skills/)** — The 13 essential skills

## The Accursed Share

We embrace waste. Entropy pressure triggers creative expenditure.
Even urgent tasks leave room for serendipity.

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)
```

**Changes:**
- Lead with philosophy, not features
- Immediate code taste
- Shorter, punchier
- Accursed share mentioned (it's our differentiator)

### 3.2 CONTRIBUTING.md — The Welcome (NEW)

**Create this file from scratch:**

```markdown
# Contributing to kgents

> We cherish slop. From raw chaos, beauty emerges.

## The Accursed Share of Contribution

Not every idea becomes a PR. This is intentional. Curation requires an
uncurated pool to select from. Your rejected ideas aren't waste—they're
the compost from which the garden grows.

## Before You Code

Read these first:
1. **[spec/principles.md](spec/principles.md)** — The seven principles
2. **[CLAUDE.md](CLAUDE.md)** — How AI agents should work in this codebase
3. **[docs/skills/](docs/skills/)** — The 13 skills that cover every task

## The Mirror Test

Before opening a PR, ask:

> Does this feel like kgents on its best day?

- **Daring, bold, creative, opinionated—but not gaudy?**
- **Tasteful > feature-complete?**
- **Joy-inducing > merely functional?**

## Development Setup

```bash
cd impl/claude

# Backend
uv sync
uv run pytest -m "not slow" -q  # Quick tests
uv run mypy .                    # Type checking (strict)

# Frontend
cd web && npm install
npm run typecheck && npm run lint
```

## Commit Convention

```bash
# Format:
<type>(<scope>): <description>

# Examples:
feat(witness): Add trust level L2 capabilities
fix(agentese): Resolve path resolution for void context
docs(readme): Reflect personality in opening section
```

## PR Checklist

- [ ] Tests pass: `uv run pytest -m "not slow" -q`
- [ ] Types clean: `uv run mypy .`
- [ ] Frontend clean: `npm run typecheck && npm run lint`
- [ ] Principles honored: Review against spec/principles.md
- [ ] CLAUDE.md consulted: If touching agent patterns

## The Hierarchy of Taste

When in doubt, prefer:
- **Tasteful** over feature-complete
- **Curated** over comprehensive
- **Joy-inducing** over merely functional
- **Composable** over convenient
- **Generative** over documented

---

*"The persona is a garden, not a museum."*
```

### 3.3 docs/quickstart.md — The How

**Current**: 126 lines, functional but dry.

**Proposed changes:**
- Add personality to section headers
- Show personality of the system, not just mechanics
- Include the "feel" not just the "do"

```markdown
# Quickstart — Zero to Agent

> *"The difference between a good system and a great one is the last 5%."*

This guide takes you from installation to running your first agent.
Five minutes. No fluff.

---

## The Installation Dance

```bash
# Clone the garden
git clone https://github.com/kgang/kgents.git
cd kgents

# Grow the environment
uv sync

# Verify life
kg --help   # (or 'kgents --help')
```

---

## Your First Agent (60 seconds)

```python
from agents import agent

@agent
async def greet(name: str) -> str:
    return f"Hello, {name}!"

# Run it
result = await greet.invoke("World")
print(result)  # "Hello, World!"
```

That's it. An agent is just a function with superpowers.

---

## Composition — The Real Magic

Agents compose via `>>`. This isn't syntax sugar—it's category theory
made practical.

```python
@agent
async def parse(s: str) -> int:
    return int(s)

@agent
async def double(x: int) -> int:
    return x * 2

@agent
async def format(x: int) -> str:
    return f"Result: {x}"

# Compose
pipe = parse >> double >> format

# Run
result = await pipe.invoke("21")
print(result)  # "Result: 42"
```

The `>>` operator satisfies associativity: `(a >> b) >> c == a >> (b >> c)`.
This isn't a nice-to-have—it's verified at runtime via `BootstrapWitness`.

---

## Adding Superpowers with Functors

Want to handle optional values? Lift your agent:

```python
from agents import Maybe, Just, Nothing, MaybeFunctor

@agent
async def divide(pair: tuple[int, int]) -> float:
    a, b = pair
    return a / b

# Lift to Maybe domain
safe_divide = MaybeFunctor.lift(divide)

await safe_divide.invoke(Just((10, 2)))  # Just(5.0)
await safe_divide.invoke(Nothing)         # Nothing (no crash!)
```

Functors preserve composition: if `f >> g` works, so does
`F.lift(f) >> F.lift(g)`. Laws, not vibes.

---

## Talk to K-gent (The Soul)

```bash
# Interactive dialogue
kg soul

# Challenge an idea
kg soul challenge "Should we add feature X?"

# Trigger dream cycle
kg soul dream
```

K-gent isn't a chatbot. It's a categorical imperative—a point
in personality-space that every response navigates toward.

---

## What's Next?

| Resource | What You'll Learn |
|----------|-------------------|
| [Philosophy](philosophy.md) | Why kgents exists |
| [Architecture](architecture-overview.md) | How the pieces fit |
| [Skills](skills/) | The 13 essential skills for building |
| [Principles](../spec/principles.md) | The seven principles + 12 ADs |

---

*"The river that knows its course flows without thinking."*
```

### 3.4 docs/philosophy.md — The Why (NEW)

**Create this file to separate philosophy from quickstart:**

Extract the philosophical content from README and expand it:
- The Noun Fallacy
- AGENTESE and observer-dependent reality
- The Accursed Share
- Category theory as foundation
- Why tasteful matters

### 3.5 Consolidate HYDRATE.md

**Problem**: Name suggests "context hydration for agents" but content is terminal integration.

**Options**:
1. Rename to `docs/terminal-integration.md` (accurate)
2. Transform into true context seed for agents (match name)

**Recommendation**: Option 1 — move to `docs/terminal-integration.md` and make root `HYDRATE.md` a true context seed OR just remove from root (CLAUDE.md serves this purpose better).

---

## Phase 4: Execution Sequence

### Step 1: Create Missing Files
- [x] Audit complete
- [ ] Create `CONTRIBUTING.md`
- [ ] Create `docs/philosophy.md` (extract from README)
- [ ] Create `docs/examples/` directory with runnable examples

### Step 2: Rewrite Core Files
- [ ] Rewrite `README.md` with personality
- [ ] Rewrite `docs/quickstart.md` with joy
- [ ] Update `CHANGELOG.md` with recent changes

### Step 3: Consolidate/Reorganize
- [ ] Move `HYDRATE.md` to `docs/terminal-integration.md`
- [ ] Create `docs/README.md` as navigation index

### Step 4: Verify
- [ ] All links work
- [ ] Voice consistent with principles
- [ ] Anti-Sausage Check passed

---

## The Anti-Sausage Check

Before completing:
- ❓ *Did I smooth anything that should stay rough?*
- ❓ *Did I add words Kent wouldn't use?*
- ❓ *Did I lose any opinionated stances?*
- ❓ *Is this still daring, bold, creative—or did I make it safe?*

---

*Plan created: 2025-12-20*
*Grounded in: "Daring, bold, creative, opinionated but not gaudy"*
