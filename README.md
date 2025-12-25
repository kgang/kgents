# kgents

> *"The noun is a lie. There is only the rate of change."*

A metatheory for agents that justify their behavior—mathematically grounded, self-witnessing, radically composable.

Not an orchestration framework. Not a chatbot wrapper. kgents is a **specification** for agents with verified structure: composition laws checked at runtime, proofs embedded in decisions, information loss quantified. If your agents don't compose associatively, they're not agents. They're functions with aspirations.

---

## The Four Pillars

### I. AGENTESE — The Universal Protocol

> *"To observe is to act. There is no view from nowhere."*

AGENTESE is kgents' native language—a verb-first ontology where paths ARE the API. No REST routes. No GraphQL schemas. Just context-aware invocation with observer-dependent projections.

```python
# Five contexts, infinite projections
await logos.invoke("world.document.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.document.manifest", poet_umwelt)       # → Metaphor
await logos.invoke("self.memory.engram", observer_umwelt)        # → Personal recall
await logos.invoke("concept.derivation.status", observer_umwelt) # → Proof chain
await logos.invoke("void.axiom.mirror-test", observer_umwelt)    # → Ground truth
```

| Context | Domain | Examples |
|---------|--------|----------|
| `world.*` | External entities | files, APIs, environments |
| `self.*` | Internal state | memory, capability, reflection |
| `concept.*` | Abstract structures | graphs, proofs, derivations |
| `void.*` | Irreducible ground | axioms, entropy, gratitude |
| `time.*` | Temporal traces | marks, crystals, forecasts |

---

### II. D-gents — Persistence with Optics

> *"State is a functor. Storage is a category."*

D-gents provide the persistence layer with **categorical guarantees**: lenses that verify their laws, schemas that validate at read, and reactive buses that propagate changes.

```python
from agents.d import Universe, DataBus, Lens, verify_lens_laws

# Universe: schema-aware typed storage
universe = await get_universe()
crystal = await universe.get(Crystal, id="abc123")

# Lens: law-verified data access (get-put, put-get, put-put)
name_lens = field_lens("name")
assert verify_lens_laws(name_lens)

# DataBus: reactive event propagation
bus = DataBus()
bus.subscribe("crystal.created", lambda e: propagate_confidence(e))
```

**The Stack**: `Universe → DgentRouter → Backends (Memory/JSONL/SQLite/Postgres) → DataBus`

---

### III. Galois Theory + Agent-DP + ASHC — Value-Encoded Self-Justification

> *"The loss IS the difficulty. The fixed point IS the agent. The strange loop IS the bootstrap."*

This is the deep innovation. Every decision is **quantified by Galois loss**—the information destroyed when restructuring content into modular form. Low loss = high coherence = self-justifying.

```python
from agents.d import GaloisLossComputer, classify_tier_by_loss

# Galois Loss: L(P) = d(P, C(R(P)))
# R = restructure, C = reconstitute, d = semantic distance
computer = GaloisLossComputer(metric="bertscore")
loss = await computer.compute("Build minimal kernel, validate, then decide")
# → 0.12 (Low loss = high coherence)

tier = classify_tier_by_loss(loss)
# CATEGORICAL (< 0.1) | EMPIRICAL (< 0.3) | AESTHETIC (< 0.5) | SOMATIC (< 0.7) | CHAOTIC
```

**Agent-DP**: Agent design IS dynamic programming:
- **State** = partial specifications
- **Actions** = design decisions
- **Reward** = Constitution(7 principles) - λ·Galois_loss
- **Trace** = Witness marks accumulated in a Walk

**ASHC**: Automated Self-Healing Code uses Galois loss as quality signal with three gatekeepers (Dafny/Z3, Lean4, Verus) for formal verification.

---

### IV. Hypergraph Editor + K-Blocks + Trails + Marks — Novel UX

> *"The file is a lie. There is only the graph."*

A six-mode modal editor treating specs as **nodes in a knowledge graph**. Navigation is edge traversal. Editing is transactional. Every change is witnessed.

```
┌─────────────────────────────────────────────────────────────────┐
│ ◀ parent │ concept.spec.zero-seed                    [NORMAL]   │
├─────────────────────────────────────────────────────────────────┤
│ TRAIL: void.axiom.entity → concept.goal.bootstrap → [current]  │
├───────┬─────────────────────────────────────────────────┬───────┤
│ [der] │   ## Zero Seed Protocol                         │ [imp] │
│ [ext] │   > "The seed IS the garden."                   │ [tst] │
│       │   ▶ [derives_from] → void.axiom.entity          │ [ref] │
├───────┴─────────────────────────────────────────────────┴───────┤
│ :ag self.witness.mark "insight"                      │ 42,7    │
└─────────────────────────────────────────────────────────────────┘
```

| Mode | Purpose | Trigger |
|------|---------|---------|
| **NORMAL** | Navigate graph | Default |
| **INSERT** | Edit (K-Block active) | `i` |
| **EDGE** | Create connections | `ge` |
| **VISUAL** | Select nodes | `v` |
| **COMMAND** | AGENTESE invoke | `:` |
| **WITNESS** | Mark moments | `gw` |

**K-Block**: Monadic isolation—changes don't escape until commit.
**Trail**: Semantic breadcrumb through the graph.
**Mark**: Atomic witness with reasoning + principles.

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

## Systems

### Derivation DAG

Specs form a directed graph with confidence propagation through seven layers:

```
CONSTITUTION (confidence = 1.0)
       │
       ├──► void.axiom.* (L1: fixed points, Galois loss ≈ 0)
       │       │
       │       └──► void.value.* (L2: grounded, L < 0.15)
       │               │
       └──────────────► concept.spec.* (L4: specified, L < 0.45)
                               │
                               └──► world.action.* (L5: implemented)
```

### WitnessedGraph

Every edge carries evidence:
- **Origin**: Mark ID, test result, or proof
- **Confidence**: 0.0–1.0, propagates through DAG
- **Galois loss**: Information lost in transition

### Crown Jewels

| Jewel | Purpose | Status |
|-------|---------|--------|
| **Brain** | Memory cathedral, TeachingCrystal | 100% |
| **Witness** | Marks, decisions, crystals, dialectical fusion | 98% |
| **Chat** | Witnessed conversations with trust escalation | 90% |
| **Categorical** | Constitution as root, TruthFunctor probes | New |
| **Atelier** | Design forge, creative workshop | 75% |
| **Liminal** | Transition protocols | 50% |

---

## Quick Start

### Requirements

| Component | Required | Notes |
|-----------|----------|-------|
| Python 3.12+ | Yes | Core runtime |
| [uv](https://github.com/astral-sh/uv) | Yes | Package manager |
| Node.js 18+ | Yes | Frontend |
| Docker | Optional | PostgreSQL (falls back to SQLite) |

### Install & Run

```bash
git clone https://github.com/kentgang/kgents.git && cd kgents
uv sync && cd impl/claude/web && npm install

# Terminal 1: Backend
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web && npm run dev
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
  theory/          # Galois modularization, Agent-DP, Analysis operads
  protocols/       # AGENTESE, Zero Seed, Witness, K-Block

impl/claude/       # Reference implementation
  agents/          # PolyAgent, Operad, Sheaf, D-gent, Galois
  services/        # Crown Jewels: Brain, Witness, Chat, Categorical
  web/             # React frontend with Hypergraph Editor

docs/skills/       # 29 skills — READ BEFORE BUILDING
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

---

## For AI Agents Working Here

Read [CLAUDE.md](CLAUDE.md) first.

- **Anti-Sausage Protocol**: Kent's voice gets diluted. Quote directly; don't paraphrase.
- **Skills-First**: 29 skills in `docs/skills/`. Read them before building.
- **Fail-Fast DI**: Required deps error immediately. Optional deps (`= None`) degrade gracefully.
- **The Mirror Test**: *"Does this feel like Kent on his best day?"*

**Core Theory Files** (for deep understanding):
- `spec/theory/galois-modularization.md` — Galois loss as quality signal
- `spec/theory/agent-dp.md` — Design as dynamic programming
- `spec/protocols/zero-seed.md` — Seven-layer epistemic holarchy
- `spec/protocols/witness.md` — Marks, crystals, dialectical fusion

---

## What Makes This Different

**vs. LangChain/LlamaIndex**: Orchestration libraries. kgents is a *specification* with mathematical structure.

**vs. AutoGPT/CrewAI**: Optimize for autonomy. kgents optimizes for *composability*.

**vs. DSPy**: DSPy treats prompts as programs; kgents treats agents as morphisms. Both algebraic. Complementary.

---

## Explore

| What | Where |
|------|-------|
| The 29 skills | `docs/skills/` |
| Theory foundations | `spec/theory/` |
| What's happening now | `NOW.md` |
| Categorical foundations | `docs/categorical-foundations.md` |

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

*"The persona is a garden, not a museum."*
