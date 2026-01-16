# kgents Glossary

> **You don't need to know category theory to use kgents.** But if you're curious, here's what these terms mean in plain English.

This glossary translates the mathematical concepts used in kgents into practical, accessible language. When you see these terms in the codebase or documentation, this is what they mean.

---

## Core Concepts

### Agent

A piece of software that takes input, does something, and produces output. In kgents, agents are like Lego blocks that can snap together. Every agent has a clear input type and output type, so you always know what goes in and what comes out.

**Example**: A summarization agent takes a document (input) and produces a summary (output).

### Morphism

A transformation from one thing to another. In kgents, every agent IS a morphism. When you hear "morphism," think "transformer" or "converter" or just "function that does something."

**Example**: An agent that converts markdown to HTML is a morphism from Markdown to HTML.

### Composition (the >> operator)

Plugging agents together so the output of one becomes the input of the next. The `>>` operator is kgents' way of saying "then do this next."

**Example**: `summarize >> translate >> format` means: first summarize, then translate the summary, then format the translation.

### Identity

A do-nothing agent that passes input through unchanged. Sounds useless, but it's essential for building pipelines where sometimes you want to skip a step.

**Example**: `conditional_transform = transform if should_transform else identity`

### Associativity

When chaining agents together, the grouping doesn't matter. `(A >> B) >> C` gives the same result as `A >> (B >> C)`. This means you can build pipelines in any order without worrying about parentheses.

**Why it matters**: If this weren't true, combining agents would be fragile and confusing.

### Category

A collection of things (objects) and transformations between them (morphisms) that follow specific rules. In kgents, agents form a category where the transformations are agent invocations and the rules guarantee that composition always works correctly.

**Why it matters**: The category structure is why agents reliably compose together.

### Functor

A mapping that preserves structure. A functor takes things from one category and maps them to another while keeping all the relationships intact. Think of it as a "well-behaved translator."

**Example**: The Universal Functor in kgents maps any agent to its traced version, preserving how agents compose while adding logging.

### Monad

A pattern for handling context or side effects while keeping composition clean. If you've used Promises in JavaScript or async/await, you've used a monad. It's a wrapper that lets you chain operations while managing something extra (like errors, state, or async behavior).

**Example**: Chain-of-thought reasoning is a monad called "Writer" that chains reasoning steps while accumulating the reasoning trace.

### Operad

A way to define how things can legally combine. While regular composition is linear (A >> B >> C), operads handle tree-shaped combinations where multiple inputs feed into one output. Think of it as "composition rules for complex structures."

**Example**: A proof tree where multiple premises combine into a conclusion. The operad defines which combinations are valid.

### Sheaf

A way to glue local views into a global picture. When multiple observers each see part of a system, a sheaf ensures their views are consistent and can be combined into one coherent understanding.

**Example**: Five people describe the same elephant from different angles. A sheaf is what lets us know they're describing the same elephant and combine their views into a complete picture.

### Polynomial Functor

A state machine pattern where the available actions depend on your current state. Different states unlock different operations. In kgents, this powers agents that behave differently based on their mode.

**Example**: A document editor with VIEW mode (can only read) and EDIT mode (can read and write). The polynomial describes which operations exist in which mode.

### PolyAgent

The core agent primitive in kgents. A PolyAgent is a polynomial functor that adds state-dependent behavior to agents. The same agent can behave differently based on its current state.

**Example**: `PolyAgent[EditingState, Document, Document]` is an agent that edits documents, and the available editing operations depend on whether you're in draft mode, review mode, or published mode.

---

## kgents-Specific Terms

### Galois Loss (L)

How much meaning is lost when you break something apart and put it back together. When you restructure a complex prompt into modules, then recombine them, you rarely get exactly what you started with. The Galois Loss measures this information leakage.

**Why it matters**: High Galois Loss predicts that a task will be hard or likely to fail. It's an early warning system.

**Example**: Splitting a nuanced essay into bullet points and reconstructing it loses the subtle connections. That loss is measurable.

### K-Block

A safe editing bubble. Make changes freely without affecting the outside world until you explicitly commit. Think of it like a Git staging area, but for specifications and documents.

**Why it matters**: You can experiment boldly without breaking anything. Discard if it doesn't work out; commit when you're ready.

**Example**: Editing a spec in a K-Block lets you refactor types, rename sections, and restructure everything. The rest of the system only sees your changes when you save.

### Mark

A record of what happened, why, and what principles applied. Every significant action in kgents leaves a Mark. Marks are immutable and form the audit trail of the system.

**Why it matters**: Reasoning traces transform reflexes into genuine agency. Without marks, actions are just reactions.

**Example**: When Claude refactors code, a Mark records: what changed, why, which principles guided the decision, and who was involved.

### Witness

The protocol that ensures every action is recorded. Witnessing is the practice of leaving Marks. An unwitnessed action is an unremembered action.

**Why it matters**: Traceability, accountability, and learning all depend on having a complete record.

**Example**: The `kg witness` command shows recent marks. Every AGENTESE invocation automatically creates a Mark.

### Crystal

Compressed knowledge extracted from Marks. As Marks accumulate, they get distilled into Crystals that capture the essential insights. Crystals are layered: session crystals compress into day crystals, which compress into week crystals, and so on.

**Why it matters**: Raw Marks would overwhelm any context window. Crystals are how kgents remembers without drowning in detail.

**Example**: A week's worth of coding sessions might crystallize into: "Dependency injection patterns significantly improved testability. Avoid mocking; prefer real implementations with test fixtures."

### AGENTESE

The language for talking to agents. A verb-first protocol where every path like `world.file.read` or `self.memory.recall` represents an action, not a thing. Different observers invoking the same path may get different results.

**Why it matters**: AGENTESE is how the entire kgents system communicates internally. Learning the path structure lets you invoke any capability.

**Example**: `logos.invoke("time.witness.mark", observer, action="Completed review")` creates a Mark through the AGENTESE protocol.

### Crown Jewel

A core service in kgents that handles a major domain. Brain handles memory. Witness handles tracing. Foundry handles code generation. Each Crown Jewel is a self-contained module with its own state, operations, and responsibilities.

**Why it matters**: The Crown Jewel pattern keeps the system modular. Each jewel can evolve independently.

**Example**: The Witness Crown Jewel owns everything related to Marks, Crystals, Walks, and the audit trail.

### Heterarchy

Leadership flows where needed, no fixed boss. Unlike a hierarchy where one agent always commands others, heterarchy means any agent can lead or follow depending on context. Power is fluid.

**Why it matters**: Fixed hierarchies create bottlenecks and single points of failure. Heterarchy is more resilient and adaptive.

**Example**: In a coding task, the code generation agent leads. In a review task, the verification agent leads. Same agents, different leadership.

### The Accursed Share

The value of productive waste. Derived from Georges Bataille's theory, this is the recognition that surplus, experimentation, and apparent "waste" are essential to creativity. Not every token must serve the immediate goal.

**Why it matters**: Systems that ruthlessly optimize for efficiency lose the serendipity that produces breakthroughs.

**Example**: The 10% exploration budget that allows tangential investigation. Failed experiments are offerings, not waste.

---

## The Seven Principles

| Principle | One-Line Summary |
|-----------|------------------|
| **Tasteful** | Each agent serves a clear, justified purpose—say "no" more than "yes" |
| **Curated** | Quality over quantity—10 excellent agents beat 100 mediocre ones |
| **Ethical** | Agents augment human capability, never replace human judgment |
| **Joy-Inducing** | Delight in interaction—warmth over coldness, personality welcome |
| **Composable** | Agents snap together like Lego—composition is the primary operation |
| **Heterarchical** | No fixed boss—leadership is contextual and fluid |
| **Generative** | Specifications compress; implementations expand from them |

---

## Quick Reference Table

| Term | Plain English | In kgents |
|------|---------------|-----------|
| **Agent** | Software that transforms input to output | The basic building block you combine |
| **Morphism** | A transformation | An agent that takes input and produces output |
| **Composition** | Chaining transformations | The `>>` operator: `agent1 >> agent2` |
| **Identity** | Do-nothing pass-through | `Id` agent for conditional pipelines |
| **Category** | A collection with composition rules | The structure that makes agents reliable |
| **Functor** | Structure-preserving translation | Maps agents while keeping composition intact |
| **Monad** | Chainable wrapper for context | How chain-of-thought and async work |
| **Operad** | Rules for tree-shaped combination | How proofs and multi-input agents compose |
| **Sheaf** | Gluing local views to global | How consensus emerges from partial knowledge |
| **PolyAgent** | State-dependent agent | Core primitive: behavior varies by mode |
| **Galois Loss** | Information lost in restructuring | Predicts task difficulty |
| **K-Block** | Safe editing bubble | Experiment without consequences until commit |
| **Mark** | Action record with reasoning | Atomic unit of the audit trail |
| **Witness** | Tracing protocol | Ensures every action is recorded |
| **Crystal** | Compressed insight | Distilled wisdom from marks |
| **AGENTESE** | Agent communication language | Verb-first paths like `world.file.read` |
| **Crown Jewel** | Core service module | Brain, Witness, Foundry, etc. |
| **Heterarchy** | Fluid leadership | No fixed hierarchy, context-dependent |
| **Accursed Share** | Productive waste | Exploration budget, valued surplus |

---

## When You Encounter These In Code

**Seeing `>>` operator?**
That's composition. Read it as "then": `parse >> validate >> transform` means "parse, then validate, then transform."

**Seeing `PolyAgent[S, A, B]`?**
That's a stateful agent. `S` is the state type, `A` is input, `B` is output. The state determines which operations are available.

**Seeing `Operad` or algebra?**
That's defining valid combinations. The operad says what operations exist; the algebra says how to execute them on a specific domain.

**Seeing `Sheaf` or gluing?**
That's about consistency. Multiple partial views need to agree on overlaps to form a coherent global view.

**Seeing `@node` decorator?**
That's registering an AGENTESE path. The decorated class becomes invokable through the protocol.

**Seeing `witness.mark()` or `km`?**
That's creating an audit record. The action and reasoning are being preserved.

---

## Further Reading

- **Want the full theory?** See `docs/theory/00-overture.md` for the mathematical foundations.
- **Want the principles in depth?** See `spec/principles.md` for the seven core principles.
- **Want practical patterns?** See `docs/skills/` for the 30+ skills that cover common tasks.

---

*"The noun is a lie. There is only the rate of change."*

*— kgents core philosophy*
