# kgents

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Category Laws](https://img.shields.io/badge/category%20laws-verified%20at%20runtime-purple.svg)](#composition-is-proven)

**Agents that compose provably, remember why they decided, and know when they'll fail—before they try.**

---

## The 30-Second Hook

Most agent frameworks chain components and hope for the best. When something breaks, you debug blind.

kgents is different:

| Other Frameworks | kgents |
|------------------|--------|
| Composition is *assumed* | Composition is **proven** (category laws verified at runtime) |
| Coherence is *hoped for* | Coherence is **measured** (Galois Loss predicts success *before* inference) |
| Ethics is *a weight* | Ethics is **a floor** (constraint, not nudge) |
| Decisions are *forgotten* | Decisions are **traced** (every action has a "why") |

```python
# Other frameworks: fingers crossed
result = agent_a(agent_b(agent_c(input)))

# kgents: mathematically guaranteed
pipeline = agent_a >> agent_b >> agent_c
assert (f >> g) >> h == f >> (g >> h)  # A law, not a test
```

**You don't need to know category theory to use kgents.** The math runs under the hood. What you get is agents that compose reliably and tell you when they can't.

---

## The Killer Feature: Galois Loss

Before running expensive inference, kgents tells you if the task will likely succeed:

```python
from services.zero_seed import compute_galois_loss

# Take a prompt, break it into modules, rebuild it
# The distance between original and rebuilt is the loss
loss = await compute_galois_loss(prompt)

if loss < 0.1:
    # Task decomposes cleanly—high success probability
    result = await execute(prompt)
elif loss < 0.5:
    # Moderate entanglement—may need iteration
    result = await execute_with_retry(prompt)
else:
    # High loss—task resists decomposition
    # Restructure the prompt or use holistic approach
    raise TaskTooEntangled(f"Galois loss {loss} exceeds threshold")
```

**The insight**: When you restructure a prompt into modules and reconstitute it, information is lost. That loss correlates with task difficulty. High loss = entangled dependencies = likely failure. Low loss = clean decomposition = likely success.

```
L(P) = d(P, C(R(P)))

P = original prompt
R = restructure into modules
C = reconstitute from modules
d = semantic distance
L = loss (your complexity oracle)
```

This isn't a heuristic. It's derived from Galois adjunction theory—the same mathematics that explains why some polynomial equations can't be solved by radicals.

**Deep dive**: [Galois Loss Theory](docs/theory/07-galois-loss.md)

---

## 5-Minute Quick Start

### Prerequisites

- Python 3.12+
- Docker (for Postgres)
- Node.js 18+ (for the web UI)
- [uv](https://github.com/astral-sh/uv) package manager

### Install and Run

```bash
# Clone
git clone https://github.com/kentgang/kgents.git && cd kgents

# Install Python dependencies
cd impl/claude && uv sync

# Install frontend dependencies
cd web && npm install && cd ..

# Start Postgres (persistence layer)
docker compose up -d

# Run everything (backend + frontend with hot reload)
uv run kg dev

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Verify It Works

```bash
# Backend health
uv run pytest -q && uv run mypy .

# Frontend health
cd web && npm run typecheck && npm run lint
```

### Your First Witness Mark

Every action in kgents leaves a trace. Try it:

```bash
# Mark a moment with reasoning
km "Started exploring kgents" --reasoning "Evaluating for production use"

# See today's marks
kg witness show --today

# Record a decision
kg decide --fast "Using kgents" --reasoning "Composition guarantees matter"
```

---

## Architecture: The Metaphysical Fullstack

Every kgents agent is a vertical slice through seven layers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. PROJECTION SURFACES   CLI │ TUI │ Web │ marimo │ JSON │ SSE            │
├─────────────────────────────────────────────────────────────────────────────┤
│  6. AGENTESE PROTOCOL     logos.invoke(path, observer, **kwargs)           │
├─────────────────────────────────────────────────────────────────────────────┤
│  5. AGENTESE NODE         @node decorator, aspects, effects, affordances   │
├─────────────────────────────────────────────────────────────────────────────┤
│  4. SERVICE MODULE        services/<name>/ — Crown Jewel business logic    │
├─────────────────────────────────────────────────────────────────────────────┤
│  3. OPERAD GRAMMAR        Composition laws, valid operations               │
├─────────────────────────────────────────────────────────────────────────────┤
│  2. POLYNOMIAL AGENT      PolyAgent[S, A, B]: state × input → output       │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. SHEAF COHERENCE       Local views → global consistency                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  0. PERSISTENCE LAYER     StorageProvider: Postgres, vectors, blobs        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key insight**: There are no explicit backend routes. AGENTESE—the observer-dependent protocol—IS the API. Same path, different observers, different results:

```python
await logos.invoke("world.document.manifest", architect)  # → Blueprint
await logos.invoke("world.document.manifest", poet)       # → Metaphor
```

### Crown Jewels (Core Services)

| Service | Purpose | What Makes It Special |
|---------|---------|----------------------|
| **Witness** | Every action leaves a mark. Marks compose into traces. | Writer monad composition—traces ARE the audit log |
| **Zero Seed** | Computes Galois loss, assigns epistemic layers | Predicts task success before inference |
| **Constitutional** | Scores against seven principles | Ethics as floor constraint, not optimization weight |
| **K-Block** | Monadic isolation for changes | Commit or rollback cleanly—no half-states |
| **Brain** | Long-term memory with spatial organization | Teaching crystals that compress experience |

---

## The Seven Principles

These aren't aspirational values. They're the reward signal the system optimizes toward—and the Constitutional service scores every action against them:

| Principle | Core Idea | Anti-Pattern |
|-----------|-----------|--------------|
| **Tasteful** | Each agent earns its place. Say no more than yes. | Kitchen-sink agents |
| **Curated** | Ten excellent things beat a hundred mediocre ones. | "Awesome list" sprawl |
| **Ethical** | Augment humans, never replace judgment. *Floor constraint.* | "Trust me" without explanation |
| **Joy-Inducing** | Personality encouraged. Warmth matters. | Robotic, lifeless responses |
| **Composable** | If it doesn't compose associatively, it's not an agent. | Monolithic god-agents |
| **Heterarchical** | No permanent boss. Leadership flows where needed. | Rigid orchestrator/worker |
| **Generative** | Specs compress. If you can't compress, you don't understand. | Documentation that tracks rather than generates |

**Full specification**: [spec/principles.md](spec/principles.md)

---

## Composition Is Proven

kgents doesn't just encourage composition—it **verifies category laws at runtime**:

```python
# These laws are checked, not assumed
pipeline = f >> g >> h

# Identity law: Id >> f ≡ f ≡ f >> Id
await BootstrapWitness.verify_identity_laws(f)

# Associativity law: (f >> g) >> h ≡ f >> (g >> h)
await BootstrapWitness.verify_composition_laws(f, g, h)
```

**Why this matters**: Agent pipelines fail silently when composition breaks. Maybe agent A's output doesn't quite fit agent B's input. Maybe the order of composition matters when it shouldn't. With verified category laws, these bugs become immediate, explicit errors—not mysterious downstream failures.

---

## The Witness Protocol: Traces Are Agency

> *"Without trace: stimulus → response (reflex). With trace: stimulus → reasoning → response (agency)."*

Every action in kgents leaves an immutable **Mark**:

```python
@dataclass(frozen=True)
class Mark:
    id: MarkId
    timestamp: datetime

    # What happened
    stimulus: Stimulus
    response: Response

    # Why it happened
    reasoning: str | None
    principles: tuple[str, ...]

    # The chain of causation
    links: tuple[MarkLink, ...]
```

Marks compose via the Writer monad. The trace of a composed pipeline is the composition of individual traces:

```
trace(f >> g >> h) = trace(f) ⊕ trace(g) ⊕ trace(h)
```

This isn't logging. It's a first-class reasoning artifact that enables:
- **Audit**: What happened and why?
- **Crystallization**: Compress recurring patterns into reusable knowledge
- **Debugging**: Follow the causal chain to the source

**Deep dive**: [Witness Protocol](spec/protocols/witness.md)

---

## Project Structure

```
spec/            Formal specifications (the "what")
impl/claude/     Reference implementation (the "how")
  ├── services/    Crown Jewels (core systems)
  ├── agents/      Categorical primitives (PolyAgent, Operad, Sheaf)
  ├── protocols/   AGENTESE protocol + CLI
  └── web/         React frontend
docs/theory/     20 chapters on agent architecture theory
docs/skills/     24 practical how-to guides
pilots/          Active pilots validating the infrastructure
```

---

## The Theory (For the Curious)

The theoretical foundation spans 20 chapters, from category theory basics through open problems:

| Part | Topic | Key Insight |
|------|-------|-------------|
| **I** | Foundations | Agents form a category. Composition is the primitive. |
| **II** | Infrastructure | Monads (CoT = Writer), Operads (composition grammar), Sheaves (local→global) |
| **III** | Galois Theory | Loss measures abstraction cost. High loss predicts failure. |
| **IV** | Dynamic Programming | Optimal policies for sequential decision-making |
| **V** | Distributed Systems | When agents collaborate: consensus, coordination |
| **VI** | Human-AI Practice | Witness, dialectic, co-engineering |
| **VII** | Synthesis | What was learned, what remains open |

**Start here**: [docs/theory/00-overture.md](docs/theory/00-overture.md)

---

## Current Status

**Crown Jewel Completion**:

| Service | Status | Notes |
|---------|--------|-------|
| Witness | 98% | 64+ tests, production-ready |
| Brain | 100% | Long-term memory with teaching crystals |
| Categorical | 95% | PolyAgent, Operad, Sheaf |
| Zero Seed | 85% | Galois loss computation |
| Constitutional | 80% | Seven-principle scoring |
| K-Block | 75% | Monadic isolation |

**Active Pilots**:
- [trail-to-crystal-daily-lab](pilots/trail-to-crystal-daily-lab/) — Productivity (active wedge)
- [wasm-survivors-game](pilots/wasm-survivors-game/) — Gaming (in development)
- [disney-portal-planner](pilots/disney-portal-planner/) — Consumer (spec complete)

---

## Commands Reference

```bash
# Development
uv run kg dev              # Unified dev server (backend + frontend)

# Witness your work
km "what happened"         # Mark a moment
kg decide --fast "choice" --reasoning "why"  # Record a decision
kg witness show --today    # See today's marks

# Strategy tools
kg probe health --all      # Session start health check
kg audit spec/X.md --full  # Validate spec against principles
kg compose --run "pre-commit"  # Pre-commit checks

# Verification
uv run pytest -q           # Run tests
uv run mypy .              # Type checking
```

---

## Philosophy

*"Daring, bold, creative, opinionated but not gaudy."*

*"Tasteful > feature-complete."*

*"Depth over breadth."*

kgents is a specification-first framework. The spec (`spec/`) is the source of truth; the implementation (`impl/`) is one possible realization. Each letter in the alphabet represents a distinct agent genus. AGENTESE is the verb-first ontology for agent-world interaction.

This is an active research project. Core ideas are stabilizing, but edges remain rough.

---

## Contributing

This is a personal research project by Kent. Ideas, feedback, and discussions are welcome.

---

MIT License

> *"The proof is the decision. The mark is the witness."*
