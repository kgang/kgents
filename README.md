# kgents

A framework for building agents that compose reliably and remember why they made decisions.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/kentgang/kgents.git && cd kgents
cd impl/claude && uv sync

# Start Postgres (required for persistence)
docker compose up -d

# Run everything (backend + frontend with hot reload)
uv run kg dev
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Verify Your Setup

```bash
# Backend checks
uv run pytest -q && uv run mypy .

# Frontend checks
cd web && npm run typecheck && npm run lint
```

---

## What This Is

Agent pipelines are fragile. Chaining components together and hoping the output of one fits the input of the next leads to failures that are hard to diagnose.

kgents treats agents as morphisms in a category. The practical implication: composition must be associative, and this is verified at runtime:

```python
assert (f >> g) >> h == f >> (g >> h)  # A law, not a test
```

The framework also measures how much meaning gets lost when ideas are restructured—called **Galois Loss**:

```
L(P) = d(P, C(R(P)))
```

Take a proposition, break it into pieces, rebuild it. The distance between original and rebuilt is the loss. When loss approaches zero, the idea is axiomatic—restructuring can't touch it.

**Theory**: [The Agent Category](docs/theory/02-agent-category.md) | [Galois Modularization](docs/theory/06-galois-modularization.md)

---

## The Stack

```
impl/claude/           Python backend + React frontend
├── services/          Crown Jewels (core systems)
│   ├── witness/       Track decisions and crystallize patterns
│   ├── zero_seed/     Compute Galois loss, assign epistemic layers
│   ├── k_block/       Monadic isolation for rollback-safe changes
│   └── constitutional/ Score compliance against 7 principles
├── web/               React frontend
└── protocols/         AGENTESE protocol + CLI
```

### Crown Jewels

| System | Purpose | Docs |
|--------|---------|------|
| **Witness** | Every action leaves a mark. Marks become traces. Traces crystallize into reusable knowledge. | [Witness Protocol](docs/theory/16-witness.md) |
| **Zero Seed** | Measures coherence loss. Classifies content into epistemic layers (AXIOM → VALUE → SPEC → TUNING). | [Galois Loss](docs/theory/07-galois-loss.md) |
| **K-Block** | Wraps changes monadically. Commit or rollback cleanly. | [spec/k-block/](spec/k-block/) |
| **Constitutional** | Scores everything against seven principles. Ethical is a floor constraint, not a weight. | [spec/principles.md](spec/principles.md) |
| **Brain** | Long-term memory with teaching crystals and spatial organization. | [spec/agents/brain.md](spec/agents/brain.md) |

---

## AGENTESE: The Protocol

Instead of REST routes, kgents uses observer-dependent paths:

```python
await logos.invoke("world.document.manifest", architect)  # → Blueprint
await logos.invoke("world.document.manifest", poet)       # → Metaphor
```

Same path, different observers, different results. Five contexts: `world.*`, `self.*`, `concept.*`, `void.*`, `time.*`.

**Docs**: [AGENTESE Path Structure](docs/skills/agentese-path.md) | [Node Registration](docs/skills/agentese-node-registration.md)

---

## Seven Principles

These aren't aspirational—they form the reward signal the system optimizes toward:

1. **Tasteful** — Each agent earns its place. Say no more than yes.
2. **Curated** — Ten excellent things beat a hundred mediocre ones.
3. **Ethical** — Augment humans, never replace judgment. (Floor constraint.)
4. **Joy-Inducing** — Personality encouraged. Warmth matters.
5. **Composable** — If it doesn't compose associatively, it's not an agent.
6. **Heterarchical** — No permanent boss. Leadership flows where needed.
7. **Generative** — Specs should compress. If you can't compress, you don't understand.

**Full specification**: [spec/principles.md](spec/principles.md)

---

## Project Structure

```
spec/            Formal specifications (the "what")
impl/            Reference implementations (the "how")
docs/theory/     20 chapters on agent architecture theory
docs/skills/     Practical how-tos (24 skills)
pilots/          Active pilots validating the infrastructure
NOW.md           Current focus and status
HYDRATE.md       Quick context for agents
```

**Theory overview**: [docs/theory/README.md](docs/theory/README.md)

---

## Commands

```bash
# Daily development
uv run kg dev              # Unified dev server

# Witness your work
km "what happened"         # Mark a moment
kg decide --fast "choice" --reasoning "why"  # Record a decision
kg witness show --today    # See today's marks

# Health checks
uv run pytest -q           # Run tests
uv run mypy .              # Type checking
```

**Skills reference**: [docs/skills/](docs/skills/)

---

## The Theory

The theoretical foundation spans 20 chapters, from category theory basics through open problems:

```
Part I    Foundations           What is an agent, mathematically?
Part II   Infrastructure        Monads, operads, sheaves—the machinery
Part III  Galois Theory         Measuring coherence loss
Part IV   Dynamic Programming   Optimal policies for agents
Part V    Distributed Systems   When agents collaborate
Part VI   Human-AI Practice     Witness, dialectic, co-engineering
Part VII  Synthesis             What was learned, what remains
```

**Start here**: [docs/theory/00-overture.md](docs/theory/00-overture.md)

---

## Current Status

Five pilots validate the infrastructure:

| Pilot | Domain | Status |
|-------|--------|--------|
| [trail-to-crystal-daily-lab](pilots/trail-to-crystal-daily-lab/) | Productivity | Active wedge |
| [wasm-survivors-game](pilots/wasm-survivors-game/) | Gaming | In development |
| [disney-portal-planner](pilots/disney-portal-planner/) | Consumer | Spec complete |
| [rap-coach-flow-lab](pilots/rap-coach-flow-lab/) | Creative | Spec complete |
| [sprite-procedural-taste-lab](pilots/sprite-procedural-taste-lab/) | Generative | Spec complete |

**Crown Jewel completion**: Witness 98%, Brain 100%, Categorical 95%, Zero Seed 85%, Constitutional 80%, K-Block 75%.

---

## Contributing

This is an active research project. Core ideas are stabilizing, but edges remain rough.

---

MIT License

> *"The proof is the decision. The mark is the witness."*
