# kgents

> *"The noun is a lie. There is only the rate of change."*

Agents are morphisms in a category. They compose. They observe. They witness.

This is not another orchestration framework. kgents is a **specification** for agents with mathematical structure—composition laws verified at runtime, not promised in documentation. If your agents don't compose associatively, they're not agents. They're functions with aspirations.

---

## Feel It

```python
from agents.poly import from_function, sequential

double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)

pipe = sequential(double, add_one)
_, outputs = pipe.run(initial=("ready", "ready"), inputs=[5, 10])

# 5 → 11, 10 → 21
# (f >> g) >> h == f >> (g >> h) — Verified, not aspirational
```

---

## Core Ideas

### Agents Are Morphisms

Not objects with methods. Not workers with queues. Morphisms in a category—functions that compose, with identity and associativity laws **verified at runtime**.

```python
Agent[A, B]           # A morphism from A to B
PolyAgent[S, A, B]    # State-dependent morphism (mode changes interface)
```

### Witness Everything

> *"The proof IS the decision. The mark IS the witness."*

Every significant action leaves a trace. Marks are the atomic unit of agency. Decisions use dialectical fusion (Kent's view + Claude's view → synthesis).

```bash
km "Completed refactor"                    # Basic mark
km "Key insight" --tag eureka              # Tagged for retrieval
kg decide --fast "Use SSE" --reasoning "Simpler than WebSockets"
```

### AGENTESE: The Protocol IS the API

Five contexts. Verb-first ontology. No explicit backend routes—invoke paths directly.

```python
await logos.invoke("world.document.manifest", observer_umwelt)
await logos.invoke("self.memory.engram", observer_umwelt)
await logos.invoke("concept.graph.sip", observer_umwelt)
```

Different observers get different projections. *"To observe is to act. There is no view from nowhere."*

---

## Systems

### Derivation DAG

Specs aren't static markdown. They form a directed graph with confidence propagation:

```
CONSTITUTION (confidence = 1.0)
       │
       ├──► PRINCIPLES (derived, confidence = f(evidence))
       │
       └──► AGENTESE ──► SERVICES ──► IMPLEMENTATIONS
                                            │
                                    Confidence = f(tests, proofs, marks)
```

Bootstrap specs (principles, composition laws) have confidence 1.0. Everything else inherits confidence from ancestors × accumulated evidence. Marks strengthen edges. Test failures weaken them.

### WitnessedGraph

Edges carry evidence. Every relationship in the system has:
- **Origin**: Where did this edge come from? (Mark ID, test result, proof)
- **Confidence**: How certain are we? (0.0–1.0, propagates through DAG)
- **Visual gutter**: Confidence renders as edge thickness in the graph viewer

This isn't metadata—it's the graph's memory of how it learned what it knows.

### Hypergraph Emacs

Six-mode modal editor for conceptual navigation:

```
MODES:    NORMAL │ INSERT │ EDGE │ VISUAL │ COMMAND │ WITNESS
NAV:      gh/gl (parent/child) │ gj/gk (siblings) │ gd/gr/gt (def/refs/test)
```

Navigate specs like code. `gd` jumps to definition. `gr` shows references. `gt` finds tests. The graph is the filesystem; navigation is traversal.

### Self-Hosting Specs

Claude can navigate specs, edit them in K-Block isolation, witness changes, and update the derivation graph—all from inside the webapp. The loop:

```
NAVIGATE → EXPAND (portals) → EDIT (K-Block) → WITNESS (mark) → PROPAGATE (confidence)
```

The spec that can't be edited by the system it specifies is mere aspiration.

### K-Block

Monadic isolation for spec editing. Changes don't escape to the cosmos until explicit commit. Multiple views (prose, graph, code) sync bidirectionally within the monad. Time travel is free—the cosmos is append-only.

### Crown Jewels

| Jewel | Purpose |
|-------|---------|
| **Brain** | Spatial cathedral of memory, TeachingCrystal crystallization |
| **Witness** | Marks, decisions, crystals, streaming, promotion |
| **Chat** | Witnessed conversations with trust escalation and branching |
| **Categorical** | Constitution as axiomatic root, TruthFunctor probes |
| **Atelier** | Design forge, creative workshop |
| **Liminal** | Transition protocols |

Crown Jewels are production services built on categorical primitives. They own their domain logic, adapters, and frontend components.

---

## Quick Start

### Requirements

| Component | Required | Notes |
|-----------|----------|-------|
| Python 3.12+ | Yes | Core runtime |
| [uv](https://github.com/astral-sh/uv) | Yes | Package manager |
| Node.js 18+ | Yes | Frontend |
| Docker | Optional | PostgreSQL (falls back to SQLite) |

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
# Visit http://localhost:3000
```

### Verify

```bash
cd impl/claude && uv run pytest -q && uv run mypy .
cd impl/claude/web && npm run typecheck && npm run lint
```

---

## Key Directories

```
spec/              # THE LAW — conceptual specification
  principles.md    # The seven principles + 17 architectural decisions
  agents/          # Agent genus specifications
  protocols/       # AGENTESE, storage, living-spec

impl/claude/       # Reference implementation
  agents/          # PolyAgent, Operad, Sheaf, Flux, K-gent, M-gent
  services/        # Crown Jewels: Brain, Witness, Chat, Categorical, Atelier, Liminal
  protocols/       # AGENTESE runtime, CLI, API gateway
  web/             # React + Three.js frontend

docs/skills/       # 29 skills — READ BEFORE BUILDING
plans/             # Active work + _focus.md (human intent)
```

---

## The Seven Principles

1. **Tasteful** — Each agent serves a clear, justified purpose. Say "no" more than "yes."
2. **Curated** — 10 excellent agents beat 100 mediocre ones.
3. **Ethical** — Agents augment humans, never replace judgment.
4. **Joy-Inducing** — Personality encouraged. Warmth over coldness.
5. **Composable** — Agents are morphisms. `(f >> g) >> h = f >> (g >> h)`. Verified.
6. **Heterarchical** — No fixed boss agent. Leadership is contextual.
7. **Generative** — Spec is compression. If you can't compress, you don't understand.

Full treatment: [spec/principles.md](spec/principles.md)

---

## For AI Agents Working Here

Read [CLAUDE.md](CLAUDE.md) first.

- **Anti-Sausage Protocol**: Kent's voice gets diluted through LLM processing. Quote directly; don't paraphrase.
- **Skills-First**: 29 skills in `docs/skills/`. Read them before building.
- **Fail-Fast DI**: Required deps error immediately with actionable messages. Optional deps (`= None`) degrade gracefully.
- **The Mirror Test**: *"Does this feel like Kent on his best day?"*

---

## What Makes This Different

**vs. LangChain/LlamaIndex**: Orchestration libraries—useful plumbing. kgents is a *specification* with mathematical structure.

**vs. AutoGPT/CrewAI**: Those optimize for autonomy. kgents optimizes for *composability*—agents that combine into larger agents without losing guarantees.

**vs. DSPy**: Closest in spirit. DSPy treats prompts as programs; kgents treats agents as morphisms. Both algebraic. Complementary.

---

## Explore

| What | Where |
|------|-------|
| Interactive demos | `impl/claude/demos/` |
| The 29 skills | `docs/skills/` |
| The seven principles | `spec/principles.md` |
| What's happening now | `NOW.md` |
| Categorical foundations | `docs/categorical-foundations.md` |

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

*"The persona is a garden, not a museum."*
