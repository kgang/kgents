# kgents

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Category Laws](https://img.shields.io/badge/category%20laws-verified%20at%20runtime-purple.svg)](#composition-is-proven)
[![Theory](https://img.shields.io/badge/theory-21%20chapters-orange.svg)](docs/theory/README.md)

**A category-theoretic framework for AI agents that compose provably, trace their reasoning, and predict failure before execution.**

> *"The proof IS the decision. The mark IS the witness."*

---

## What Is This?

kgents is a **research-grade agent framework** that treats agent composition as a mathematical object rather than an engineering convenience. Built on category theory, Galois adjunctions, and polynomial functors, it provides:

1. **Verified Composition**: Category laws (identity, associativity) are checked at runtime, not assumed
2. **Failure Prediction**: Galois Loss measures task complexity and predicts failure probability *before inference*
3. **Reasoning Traces**: Every action leaves an immutable Mark; marks compose into Traces via the Writer monad
4. **Ethical Floor**: Constitutional principles enforce ethics as a constraint, not a weight to be optimized away

**This is not another LangChain wrapper.** kgents explores what agent architectures look like when designed from first principles.

---

## The Core Insight: Galois Loss

Before running expensive inference, kgents tells you if the task will likely succeed:

```python
from services.zero_seed import compute_galois_loss

loss = await compute_galois_loss(prompt)

if loss < 0.1:
    # Task decomposes cleanly—high success probability
    result = await execute(prompt)
elif loss < 0.5:
    # Moderate entanglement—may need iteration
    result = await execute_with_retry(prompt)
else:
    # High loss—task resists decomposition, restructure first
    raise TaskTooEntangled(f"Galois loss {loss} exceeds threshold")
```

**The mathematics**: When you restructure a prompt into modules and reconstitute it, information is lost. That loss—derived from Galois adjunction theory—correlates with task difficulty. High loss predicts failure.

```
L(P) = d(P, C(R(P)))

P = original prompt
R = restructure into modules
C = reconstitute from modules
d = semantic distance
L = Galois loss (your complexity oracle)
```

**Why this matters**: Most agent failures are predictable—tasks that resist modular decomposition. Galois Loss surfaces this *before* you spend tokens.

---

## Repository Atlas

```
kgents/
├── README.md              # You are here
├── CLAUDE.md              # AI assistant instructions & project philosophy
├── NOW.md                 # Living document: current focus & status
│
├── spec/                  # Formal specifications (the "what")
│   ├── principles.md      # The 7 constitutional principles
│   ├── protocols/         # Protocol specifications (AGENTESE, Witness, etc.)
│   └── agents/            # Agent specifications (A-Z taxonomy)
│
├── impl/claude/           # Reference implementation (the "how")
│   ├── agents/            # Categorical primitives (PolyAgent, Operad, Sheaf)
│   ├── services/          # Crown Jewels (50+ services: Brain, Witness, etc.)
│   ├── protocols/         # AGENTESE protocol + CLI + API
│   └── web/               # React frontend (Hypergraph Editor)
│
├── docs/
│   ├── theory/            # Mathematical foundations (21 chapters)
│   │   ├── 00-overture.md # START HERE for the theory
│   │   └── README.md      # Full chapter index
│   ├── skills/            # Practical how-to guides (30+ skills)
│   ├── GETTING_STARTED.md # Developer onboarding guide
│   ├── ARCHITECTURE.md    # Visual architecture diagrams (Mermaid)
│   └── GLOSSARY.md        # Plain-English definitions
│
├── examples/              # Executable examples (5 progressive tutorials)
│   ├── 01-hello-composition/  # Agent composition & category laws
│   ├── 02-galois-oracle/      # Failure prediction via Galois loss
│   ├── 03-witness-trace/      # Reasoning traces & marks
│   ├── 04-agentese-observer/  # Observer-dependent semantics
│   └── 05-constitutional-check/ # 7 principles & ethical floor
│
├── pilots/                # Validation pilots (proof-of-concept applications)
│   ├── trail-to-crystal-daily-lab/   # Productivity (Core pilot)
│   ├── wasm-survivors-game/          # Gaming (Domain pilot)
│   └── ...                           # 7 pilots across domains
│
└── plans/                 # Strategic planning documents
    └── enlightened-synthesis/        # Master synthesis & roadmap
```

---

## Quick Start

### Prerequisites

- Python 3.12+
- Docker (for PostgreSQL) or run with SQLite fallback
- Node.js 18+ (for web UI)
- [uv](https://github.com/astral-sh/uv) package manager

### Install & Run

```bash
# Clone
git clone https://github.com/kentgang/kgents.git && cd kgents

# Install dependencies
cd impl/claude && uv sync
cd web && npm install && cd ..

# Start Postgres (optional—falls back to SQLite without)
docker compose up -d

# Run everything
uv run kg dev

# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Your First Witness Mark

Every action in kgents leaves a trace:

```bash
# Mark a moment with reasoning
km "Started exploring kgents" --reasoning "Evaluating for research use"

# See today's marks
kg witness show --today

# Record a decision
kg decide --fast "Using kgents" --reasoning "Composition guarantees matter"
```

---

## The Theory

kgents is built on a 21-chapter theoretical monograph that unifies category theory, Galois theory, and dynamic programming into a coherent agent architecture theory.

### Core Mathematical Structures

| Structure | Role in kgents | Key Insight |
|-----------|---------------|-------------|
| **PolyAgent[S,A,B]** | Agent primitive | Agents are polynomial functors—behavior depends on state |
| **Operad** | Composition grammar | Multi-input operations with verified laws |
| **Sheaf** | Consensus | Local views glue to global consistency |
| **Galois Adjunction** | Complexity oracle | Restructure/reconstitute pair measures abstraction cost |
| **Writer Monad** | Reasoning traces | Chain-of-thought as monadic composition |

### Reading Path

**30 minutes**: [Overture](docs/theory/00-overture.md) — Why this theory exists

**2-3 hours** (core concepts):
- [The Agent Category](docs/theory/02-agent-category.md) — Agents as morphisms
- [Galois Loss](docs/theory/07-galois-loss.md) — Failure prediction
- [Witness Protocol](docs/theory/16-witness.md) — Reasoning traces

**Full treatise**: [Theory README](docs/theory/README.md) — 21 chapters, 7 parts

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
│  0. PERSISTENCE LAYER     StorageProvider: PostgreSQL, vectors, blobs      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key insight**: There are no explicit REST routes. AGENTESE—the observer-dependent protocol—IS the API. Same path, different observers, different results:

```python
await logos.invoke("world.document.manifest", architect)  # → Blueprint
await logos.invoke("world.document.manifest", poet)       # → Metaphor
```

---

## The Seven Principles

These aren't aspirational values—they're the reward signal the system optimizes toward:

| Principle | Core Idea | Enforcement |
|-----------|-----------|-------------|
| **Tasteful** | Each agent earns its place. Say no more than yes. | Scored |
| **Curated** | Ten excellent things beat a hundred mediocre ones. | Scored |
| **Ethical** | Augment humans, never replace judgment. | **Floor constraint** (≥0.6) |
| **Joy-Inducing** | Personality matters. Warmth over coldness. | Scored |
| **Composable** | If it doesn't compose associatively, it's not an agent. | Verified at runtime |
| **Heterarchical** | No permanent boss. Leadership flows where needed. | Scored |
| **Generative** | Specs compress. If you can't compress, you don't understand. | Scored |

**The Ethical Floor**: ETHICAL is not a weighted score—it's a constraint. If ETHICAL < 0.6, the action is rejected regardless of other scores. You cannot trade off ethics for other values.

---

## Crown Jewels (Core Services)

| Service | Purpose | Distinguishing Feature |
|---------|---------|----------------------|
| **Witness** | Decision traces | Writer monad composition—traces ARE the audit log |
| **Zero Seed** | Galois loss computation | Predicts task success before inference |
| **Constitutional** | Principle enforcement | Ethics as floor constraint, not optimization weight |
| **Brain** | Long-term memory | Teaching crystals that compress experience |
| **K-Block** | Monadic isolation | Commit or rollback cleanly—no half-states |
| **Morpheus** | LLM gateway | Observer-aware completions |

---

## Examples

Five progressive examples in `examples/` teach the core concepts:

| # | Example | Concept | Run |
|---|---------|---------|-----|
| 01 | Hello Composition | `>>` operator, identity, associativity | `uv run python examples/01-hello-composition/main.py` |
| 02 | Galois Oracle | Loss prediction, layer assignment | `uv run python examples/02-galois-oracle/main.py` |
| 03 | Witness Trace | Marks, traces, Toulmin proofs | `uv run python examples/03-witness-trace/main.py` |
| 04 | AGENTESE Observer | Observer-dependent semantics | `uv run python examples/04-agentese-observer/main.py` |
| 05 | Constitutional | 7 principles, ethical floor | `uv run python examples/05-constitutional-check/main.py` |

From the repo root:
```bash
cd impl/claude && uv run python ../../examples/01-hello-composition/main.py
```

---

## Current Status

### Crown Jewel Completion

| Service | Status | Tests |
|---------|--------|-------|
| Witness | 98% | 678+ |
| Brain | 100% | Production-ready |
| Categorical | 95% | Laws verified at runtime |
| Zero Seed | 85% | Galois loss computation |
| Constitutional | 80% | 7-principle scoring |
| K-Block | 75% | Monadic isolation |

### Validation Pilots

| Pilot | Domain | Status |
|-------|--------|--------|
| trail-to-crystal-daily-lab | Productivity | Active (wedge pilot) |
| wasm-survivors-game | Gaming | In development |
| disney-portal-planner | Consumer | Spec complete |

---

## Research Context

kgents contributes to several research directions:

**Agent Architecture**: What mathematical structure must a system have to count as an agent? We argue: agents are morphisms in a category, with PolyAgent (polynomial functor) as the primitive.

**Failure Prediction**: Can we predict agent task failure before execution? Galois Loss provides an information-theoretic measure that correlates with task complexity.

**Reasoning Traces**: How should we represent the "thinking" of an agent? The Witness protocol treats traces as first-class objects composing via the Writer monad.

**Ethical AI**: How do we prevent ethics from being traded off against other values? Constitutional principles with floor constraints.

**Human-AI Collaboration**: How do agents learn from human feedback while preserving human agency? The Witness protocol records decisions with reasoning, enabling audit and learning.

### Related Work

The [Framework Comparison](docs/theory/18-framework-comparison.md) chapter provides categorical analysis of LangChain, CrewAI, AutoGPT, and other frameworks.

---

## Documentation Index

| Document | Purpose | Audience |
|----------|---------|----------|
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Developer onboarding | Engineers |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Visual diagrams | Engineers, Researchers |
| [GLOSSARY.md](docs/GLOSSARY.md) | Plain-English definitions | Everyone |
| [docs/theory/](docs/theory/README.md) | Mathematical foundations | Researchers |
| [docs/skills/](docs/skills/README.md) | Practical how-to guides | Engineers |
| [CLAUDE.md](CLAUDE.md) | AI assistant instructions | AI collaborators |
| [NOW.md](NOW.md) | Current focus & status | Contributors |

---

## Commands Reference

```bash
# Development
uv run kg dev              # Unified dev server (backend + frontend)

# Witness your work
km "what happened"         # Mark a moment
kg decide --fast "choice" --reasoning "why"  # Record a decision
kg witness show --today    # See today's marks

# Verification
uv run pytest -q           # Run tests (~25K collected)
uv run mypy .              # Type checking
cd web && npm run typecheck # Frontend types

# Health checks
kg probe health --all      # Session start verification
```

---

## Philosophy

> *"Daring, bold, creative, opinionated but not gaudy."*
> *"Tasteful > feature-complete."*
> *"Depth over breadth."*

kgents is specification-first: the spec (`spec/`) is the source of truth; the implementation (`impl/`) is one possible realization. Each letter in the alphabet represents a distinct agent genus. AGENTESE is the verb-first ontology for agent-world interaction.

This is an active research project. Core ideas are stabilizing, but edges remain rough. That's intentional—*"The persona is a garden, not a museum."*

---

## Contributing

This is a personal research project. Ideas, feedback, and discussions are welcome. For significant contributions, please open an issue first to discuss the approach.

---

## License

MIT

---

> *"The proof is the decision. The mark is the witness."*
