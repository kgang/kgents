# kgents

```
L(P) = d(P, C(R(P)))
```

That equation measures the information destroyed when you modularize a decision. We call it **Galois Loss**. When `L < 0.05`, you've found a fixed point—an axiom. When `L > 0.5`, your abstraction is leaking. Every agent framework ignores this. kgents quantifies it.

**678 tests. 21 chapters of theory. 6 months of hardening.** Not a wrapper. Not a demo. A specification for agents that justify their behavior mathematically.

---

<table>
<tr>
<td width="33%">

### For Developers

Your agents don't compose. You chain them, debug them, pray they work. kgents verifies composition laws at runtime:

```python
# This is a theorem, not a hope
assert (f >> g) >> h == f >> (g >> h)
```

**What you get**:
- PolyAgent: State machines with verified transitions
- AGENTESE: Protocol-as-API (no REST routes)
- Witness: Every decision traced with proof

</td>
<td width="33%">

### For Researchers

Agent architecture has deep mathematical structure. We derive it from category theory, formalize it with Galois connections, and optimize it with dynamic programming:

```
Agent ≅ PolyAgent[S, A, B]
V*(s) = max_a [R(s,a) + γV*(T(s,a))]
```

**What you get**:
- [21-chapter treatise](docs/theory/README.md)
- Galois modularization as loss function
- Constitution as reward signal

</td>
<td width="33%">

### For Builders

Decisions should be measurable. Every choice has a Galois loss. Every trace is witnessed. Trust accumulates:

```
L < 0.05 → Axiom (fixed point)
L < 0.15 → Stable
L < 0.30 → Drifting
L ≥ 0.30 → Volatile
```

**What you get**:
- Quantified decision quality
- Trust gradient from evidence
- Constitutional compliance scoring

</td>
</tr>
</table>

## See It

```python
from agents.poly import from_function, sequential

double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)

pipe = sequential(double, add_one)
_, outputs = pipe.run(initial=("ready", "ready"), inputs=[5, 10])
# 5 → 11, 10 → 21
# Composition verified, not assumed
```

```python
from agents.d import GaloisLossComputer

computer = GaloisLossComputer(metric="bertscore")
loss = await computer.compute("Build minimal kernel, validate, then decide")
# → 0.12 (low loss = high coherence = self-justifying)
```

```python
# AGENTESE: The protocol IS the API
await logos.invoke("world.document.manifest", architect_umwelt)  # → Blueprint
await logos.invoke("world.document.manifest", poet_umwelt)       # → Metaphor
# Same path, different observers, different projections
```

---

## The Architecture

### I. The Four Pillars

| Pillar | What | Why |
|--------|------|-----|
| **AGENTESE** | Verb-first protocol where paths ARE the API | No REST. No GraphQL. Observer-dependent projections. |
| **D-gents** | Persistence with categorical guarantees | Lenses verify their laws. Schemas validate at read. |
| **Galois Theory** | Loss quantifies abstraction cost | Low loss = high coherence. Fixed points = axioms. |
| **Witness** | Every action leaves a mark | Traces are morphisms. Decisions are proofs. |

### II. The Theory Stack

```
Part VII: Synthesis and Frontier
Part VI:  Co-Engineering Practice (Analysis Operad, Witness, Dialectic)
Part V:   Distributed Agents (Multi-Agent, Heterarchy, Binding)
Part IV:  Dynamic Programming (Agent-DP, Value Agent, Meta-DP)
Part III: Galois Theory (Modularization, Loss, Polynomial Bootstrap)
Part II:  Categorical Infrastructure (Monads, Operads, Sheaves)
Part I:   Foundations (Agent Category, Composition Laws)
```

Full treatise: [docs/theory/README.md](docs/theory/README.md)

### III. The Crown Jewels

| Jewel | Purpose | Status |
|-------|---------|--------|
| **Witness** | Marks, crystals, dialectical fusion | 98% (678+ tests) |
| **Brain** | Memory cathedral, teaching crystals | 100% (200+ tests) |
| **Zero Seed** | Galois loss, layer assignment | 85% |
| **K-Block** | Monadic isolation, transactional edits | 75% |
| **Constitutional** | 7-principle scoring, ETHICAL floor | 80% (52 tests) |

---

## Run It

```bash
git clone https://github.com/kentgang/kgents.git && cd kgents
uv sync && cd impl/claude/web && npm install

# Terminal 1: Backend
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web && npm run dev
# Visit http://localhost:3000
```

**Verify**:
```bash
cd impl/claude && uv run pytest -q && uv run mypy .
cd impl/claude/web && npm run typecheck && npm run lint
```

---

## The Seven Principles

These aren't platitudes. They're the reward function.

| # | Principle | Meaning |
|---|-----------|---------|
| 1 | **Tasteful** | Each agent serves a clear, justified purpose. Say "no" more than "yes." |
| 2 | **Curated** | 10 excellent agents beat 100 mediocre ones. |
| 3 | **Ethical** | Agents augment humans, never replace judgment. (ETHICAL ≥ 0.6 required) |
| 4 | **Joy-Inducing** | Personality encouraged. Warmth over coldness. |
| 5 | **Composable** | Agents are morphisms. `(f >> g) >> h = f >> (g >> h)`. Verified. |
| 6 | **Heterarchical** | No fixed boss agent. Leadership is contextual. |
| 7 | **Generative** | Spec is compression. If you can't compress, you don't understand. |

---

## What Makes This Different

| Framework | Optimizes For | kgents |
|-----------|---------------|--------|
| LangChain/LlamaIndex | Orchestration | **Specification** with mathematical structure |
| AutoGPT/CrewAI | Autonomy | **Composability** with verified laws |
| DSPy | Prompts as programs | **Agents as morphisms** (complementary) |

---

## Key Paths

```
docs/theory/        # 21-chapter categorical treatise
spec/theory/        # Galois modularization, Agent-DP, Zero Seed
impl/claude/        # Reference implementation (Python + React)
docs/skills/        # 29 skills — READ BEFORE BUILDING
NOW.md              # What's happening this week
```

---

## For AI Agents

Read [CLAUDE.md](CLAUDE.md) first.

- **Anti-Sausage Protocol**: Kent's voice gets diluted. Quote directly; don't paraphrase.
- **The Mirror Test**: *"Does this feel like Kent on his best day?"*
- **Fail-Fast DI**: Required deps error immediately. Optional deps (`= None`) degrade gracefully.

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

> *"Agents that don't compose associatively aren't agents. They're functions with aspirations."*
