# kgents

*A quiet framework for agents that justify their behavior.*

---

## The Central Idea

What if we could measure how much meaning is lost when we restructure a thought?

```
L(P) = d(P, C(R(P)))
```

This is **Galois Loss**. Take a proposition, restructure it, reconstitute it, measure the distance. When `L → 0`, you've found something stable—a fixed point. An axiom. When `L → 1`, your abstraction leaks meaning everywhere.

Most agent frameworks assume coherence. kgents measures it.

---

## What You'll Find Here

### A Theory of Agent Composition

Agents aren't just functions with LLMs inside. They're morphisms in a category. This means they must compose:

```python
# If this isn't true, something is broken
assert (f >> g) >> h == f >> (g >> h)
```

kgents verifies these laws at runtime. Not as a nice-to-have, but because composition that isn't associative isn't really composition at all.

**Explore**: [The Agent Category](docs/theory/02-agent-category.md)

### A Loss Function for Decisions

Every decision has a cost—not in compute, but in coherence. We quantify it:

| Loss | Interpretation |
|------|----------------|
| `< 0.05` | Fixed point (axiomatic) |
| `< 0.15` | Stable |
| `< 0.30` | Drifting |
| `≥ 0.30` | Volatile |

**Explore**: [Galois Modularization](docs/theory/06-galois-modularization.md) | [Galois Loss](docs/theory/07-galois-loss.md)

### A Protocol Where the Path *Is* the API

AGENTESE replaces REST routes with semantic paths. The same path yields different projections for different observers:

```python
await logos.invoke("world.document.manifest", architect)  # → Blueprint
await logos.invoke("world.document.manifest", poet)       # → Metaphor
```

**Explore**: [AGENTESE Path Protocol](docs/skills/agentese-path.md)

### A Witness for Every Action

Every decision leaves a mark. Marks compose into traces. Traces crystallize into knowledge:

```
Mark → Trace → Crystal → Grant → Playbook
```

The system remembers not just what you decided, but *why*.

**Explore**: [Witness Protocol](docs/theory/16-witness.md)

---

## The Theory

Twenty chapters derive agent architecture from first principles:

```
Part I    Foundations           Agent category, composition laws
Part II   Infrastructure        Monads, operads, sheaves
Part III  Galois Theory         Modularization, loss, bootstrap
Part IV   Dynamic Programming   Agent-DP, value functions, meta-DP
Part V    Distributed Agents    Multi-agent, heterarchy, binding
Part VI   Co-Engineering        Witness, dialectic, analysis operad
Part VII  Synthesis             Framework comparison, open problems
```

**Start here**: [docs/theory/README.md](docs/theory/README.md)

---

## The Implementation

| Component | Purpose |
|-----------|---------|
| **Witness** | Marks, crystals, trust gradients |
| **Zero Seed** | Galois loss computation, layer assignment |
| **K-Block** | Monadic isolation for transactional edits |
| **Constitutional** | Seven-principle compliance scoring |
| **Brain** | Memory cathedral with teaching crystals |

```bash
# Quick start
git clone https://github.com/kentgang/kgents.git && cd kgents
cd impl/claude && uv sync
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

---

## The Seven Principles

These shape what we build and how:

1. **Tasteful** — Each agent justifies its existence
2. **Curated** — Quality over quantity, always
3. **Ethical** — Augment humans, never replace judgment
4. **Joy-Inducing** — Warmth and personality matter
5. **Composable** — Verified morphisms, not hopeful chaining
6. **Heterarchical** — No permanent hierarchies; context determines leadership
7. **Generative** — Specs compress; if you can't compress, you don't understand

---

## Navigating

```
docs/theory/     Theory treatise (start with 00-overture.md)
docs/skills/     Practical guides for building
impl/claude/     Reference implementation
spec/            Formal specifications
NOW.md           Current focus and status
```

---

## An Invitation

This is not a finished product. It's an exploration of what agent architecture could be if we took mathematical structure seriously.

The ideas here emerged from asking: *What would agents look like if every claim about their behavior could be verified?*

If that question interests you, you're welcome here.

---

MIT License

> *"The proof is the decision. The mark is the witness."*
