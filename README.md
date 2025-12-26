# kgents

*A quiet framework for agents that justify their behavior.*

---

## The Central Idea

Here's something that kept us up at night: when you take a complex thought and break it into pieces, how much gets lost?

Not lost like "oops, forgot a comma." Lost like meaning that evaporates. Nuance that simplifies away. The thing that made the thought *that thought* instead of some other thought.

We found a way to measure it:

```
L(P) = d(P, C(R(P)))
```

We call this **Galois Loss**. You take a proposition, restructure it into modular pieces, then reconstitute it back. The distance between what you started with and what you ended up with? That's the loss.

When `L → 0`, you've discovered something remarkable: a fixed point. An idea so fundamental that restructuring can't touch it. An axiom.

When `L → 1`, your abstraction is hemorrhaging meaning everywhere.

Most agent frameworks just assume their pipelines are coherent. We wanted to *know*.

---

## What's Inside

### Composition That Actually Composes

There's a dirty secret in agent tooling: when you chain agents together, you're crossing your fingers. Will the output of one fit the input of the next? Will the whole behave predictably?

Agents in kgents are morphisms in a category. That sounds fancy, but the implication is practical: they *must* compose associatively.

```python
assert (f >> g) >> h == f >> (g >> h)
```

This isn't a unit test. It's a mathematical law. We verify it at runtime because if composition doesn't hold, you don't have a pipeline—you have a prayer.

**Go deeper**: [The Agent Category](docs/theory/02-agent-category.md)

---

### A Loss Function for Thinking

Every decision costs something. Not compute—coherence.

When you simplify "I believe in building things that feel handcrafted even at scale" into "quality matters," you've lost something. That loss is quantifiable:

| Loss | What It Means |
|------|---------------|
| `< 0.05` | You've found bedrock. This is axiomatic. |
| `< 0.15` | Solid ground. Safe to build on. |
| `< 0.30` | Things are shifting. Worth revisiting. |
| `≥ 0.30` | Volatile. The abstraction is leaking badly. |

We use this to figure out which beliefs are foundational and which are derivative. Which decisions anchor the system and which ones float.

**Go deeper**: [Galois Modularization](docs/theory/06-galois-modularization.md) | [The Loss Function](docs/theory/07-galois-loss.md)

---

### The Path Is the API

We got tired of REST routes. `/api/v2/documents/{id}/manifest`—what does that even mean? Who's asking? Why do they care?

AGENTESE flips it around. The path describes what you want, and the system figures out how to give it to you based on who you are:

```python
await logos.invoke("world.document.manifest", architect)  # → Blueprint
await logos.invoke("world.document.manifest", poet)       # → Metaphor
```

Same path. Different observers. Different worlds.

**Go deeper**: [AGENTESE Protocol](docs/skills/agentese-path.md)

---

### Everything Leaves a Mark

Decisions are easy to make and hard to remember. Why did we choose PostgreSQL over SQLite three months ago? What were the tradeoffs? Who was in the room?

In kgents, every action leaves a **mark**. Marks accumulate into traces. Traces crystallize into reusable knowledge. The system doesn't just remember what you decided—it remembers the reasoning, the context, the moment.

```
Mark → Trace → Crystal → Grant → Playbook
```

We call this the Witness. It turns your work into institutional memory.

**Go deeper**: [Witness Protocol](docs/theory/16-witness.md)

---

## The Theory

We didn't want to build another framework. We wanted to understand why agent architectures work when they work, and why they fail when they fail.

So we wrote it down. Twenty chapters, starting from category theory and ending with open problems we haven't solved yet:

```
Part I    Foundations           What is an agent, mathematically?
Part II   Infrastructure        Monads, operads, sheaves—the machinery
Part III  Galois Theory         Measuring coherence loss
Part IV   Dynamic Programming   Optimal policies for agents
Part V    Distributed Systems   When agents collaborate
Part VI   Human-AI Practice     Witness, dialectic, co-engineering
Part VII  Synthesis             What we learned, what remains
```

It's dense in places. But if you want to know *why* we built things this way, it's all there.

**Start here**: [docs/theory/README.md](docs/theory/README.md)

---

## The Implementation

Five components do most of the work:

| Component | What It Does |
|-----------|--------------|
| **Witness** | Marks every decision, crystallizes patterns, tracks trust |
| **Zero Seed** | Computes Galois loss, assigns epistemic layers |
| **K-Block** | Isolates changes monadically so you can roll back cleanly |
| **Constitutional** | Scores compliance against seven principles |
| **Brain** | Long-term memory with teaching crystals |

```bash
# Get it running
git clone https://github.com/kentgang/kgents.git && cd kgents
cd impl/claude && uv sync
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

---

## Seven Principles

These aren't decorative. They're the reward signal—the thing the system optimizes toward:

1. **Tasteful** — Say no more than yes. Each agent earns its place.
2. **Curated** — Ten excellent things beat a hundred mediocre ones.
3. **Ethical** — Augment humans, never replace judgment.
4. **Joy-Inducing** — Personality encouraged. Warmth over coldness.
5. **Composable** — If it doesn't compose associatively, it's not an agent.
6. **Heterarchical** — No permanent boss. Leadership flows to where it's needed.
7. **Generative** — Specs should compress. If you can't compress, you don't understand.

---

## Finding Your Way

```
docs/theory/     The treatise (start with 00-overture.md)
docs/skills/     Practical how-tos
impl/claude/     Reference implementation in Python + React
spec/            Formal specifications
NOW.md           What's happening right now
```

---

## Come In

This isn't finished. It might never be finished.

What we have is an exploration—a serious attempt to figure out what agent architecture looks like when you refuse to hand-wave the hard parts. When every claim about behavior is backed by something you can verify.

If you've ever looked at an agent pipeline and thought "this works but I have no idea why," or "this should work but doesn't and I can't figure out where it breaks"—we've been there too. That frustration is why this exists.

You're welcome to look around.

---

MIT License

> *"The proof is the decision. The mark is the witness."*
