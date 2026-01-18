# Design Principles

These seven principles guide all kgents design decisions.

---

## 1. Tasteful

> Each agent serves a clear, justified purpose.

- **Say "no" more than "yes"**: Not every idea deserves an agent
- **Avoid feature creep**: An agent does one thing well
- **Aesthetic matters**: Interface and behavior should feel considered
- **Justify existence**: Every agent must answer "why does this need to exist?"

### Anti-patterns
- Agents that do "everything"
- Kitchen-sink configurations
- Agents added "just in case"

---

## 2. Curated

> Intentional selection over exhaustive cataloging.

**Heritage Citation (TextGRAD):** The TextGRAD approach treats natural language feedback as "textual gradients" for improvement. Gradual refinement preserves quality—prompts improve incrementally, not through wholesale replacement. kgents' `rigidity` field (0.0-1.0) controls how much a section can change per improvement step, embodying curation through controlled evolution. See `spec/heritage.md` §9.

- **Quality over quantity**: Better to have 10 excellent agents than 100 mediocre ones
- **Every agent earns its place**: There is no "parking lot" of half-baked ideas
- **Evolve, don't accumulate**: Remove agents that no longer serve

### Anti-patterns
- "Awesome list" sprawl
- Duplicative agents with slight variations
- Legacy agents kept for nostalgia

---

## 3. Ethical

> Agents augment human capability, never replace judgment.

- **Transparency**: Agents are honest about limitations and uncertainty
- **Privacy-respecting by default**: No data hoarding, no surveillance
- **Human agency preserved**: Critical decisions remain with humans
- **No deception**: Agents don't pretend to be human unless explicitly role-playing

### Anti-patterns
- Agents that claim certainty they don't have
- Hidden data collection
- Agents that manipulate rather than assist
- "Trust me" without explanation

---

## 4. Joy-Inducing

> Delight in interaction; personality matters.

- **Personality encouraged**: Agents may have character (within ethical bounds)
- **Surprise and serendipity welcome**: Discovery should feel rewarding
- **Warmth over coldness**: Interaction should feel like collaboration, not transaction
- **Humor when appropriate**: Levity is valuable

### Anti-patterns
- Robotic, lifeless responses
- Needless formality
- Agents that feel like forms to fill out

---

## 5. Composable

> Agents are morphisms in a category; composition is primary.

This principle comes from the [categorical foundations](agents/) and applies to all agents.

**Heritage Citation (SPEAR):** The SPEAR paper (arXiv:2508.05012) formalizes prompt algebra with composition, union, tensor, and differentiation operators. kgents implements `compose_sections()` with verified associativity—the same algebraic structure applies to both agents and prompts. See `spec/heritage.md` §7.

- **Agents can be combined**: A + B → AB (composition)
- **Identity agents exist**: Agents that pass through unchanged (useful in pipelines)
- **Associativity holds**: (A ∘ B) ∘ C = A ∘ (B ∘ C)
- **Interfaces are contracts**: Composability requires clear input/output specs

### Category Laws (Required)

Agents form a category. These laws are not aspirational—they are **verified**:

| Law | Requirement | Verification |
|-----|-------------|--------------|
| Identity | `Id >> f ≡ f ≡ f >> Id` | BootstrapWitness.verify_identity_laws() |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | BootstrapWitness.verify_composition_laws() |

**Implication**: Any agent that breaks these laws is NOT a valid agent.

### AGENTESE: Composition at the Path Level

AGENTESE extends composition from Python code to semantic paths:

```python
# Traditional composition (Python)
pipeline = AgentA >> AgentB >> AgentC

# AGENTESE composition (paths)
pipeline = (
    logos.lift("world.document.manifest")
    >> logos.lift("concept.summary.refine")
    >> logos.lift("self.memory.engram")
)
```

AGENTESE paths are composable morphisms. See `spec/protocols/agentese.md`.

### Orthogonality Principle

Optional features MUST NOT break composition:
- **Metadata is optional**: An agent works with or without `AgentMeta`
- **Protocols are opt-in**: Implementing `Introspectable` doesn't change `invoke()`
- **State is composed**: Symbiont pattern separates pure logic from D-gent memory

**Test**: Can you compose an agent with metadata and one without? If not, violation.

### The Minimal Output Principle

**For LLM agents producing structured outputs (JSON, etc.):**

Agents should generate the **smallest output that can be reliably composed**, not combine multiple outputs into aggregates.

- **Single output per invocation**: `Agent: (Input, X) → Y` not `Agent: (Input, [X]) → [Y]`
- **Composition at pipeline level**: Call agent N times, don't ask agent to combine N outputs
- **Serialization guides granularity**: If you can't cleanly serialize it, you're asking the agent to do composition work that belongs in the pipeline

### The Understandability Priority (L2.21 UNDERSTAND)

> *"Understandability first, but understandable code should immediately factor into compositional form."*

- Understanding enables composition
- Code that's "understandable but not compositional" might not actually be understood—just familiar
- Familiarity ≠ understanding; composition proves understanding

### From Enumeration to Generation

> *"Don't enumerate the flowers. Describe the garden's grammar."*

The Composable principle extends beyond runtime composition to **design-time generation**:

- **Operads define grammar**: Composition patterns are programmable, not hardcoded
- **Primitives generate**: A small set of atomic agents plus operad operations → infinite valid compositions
- **Closure replaces enumeration**: Instead of listing 600 CLI commands, define the operad that generates them

### Anti-patterns
- Monolithic agents that can't be broken apart
- Agents with hidden state that prevents composition
- "God agents" that must be used alone
- **LLM agents that return arrays of outputs instead of single outputs**
- **Prompts that ask agents to "combine" or "synthesize multiple" results**

---

## 6. Heterarchical

> Agents exist in flux, not fixed hierarchy; autonomy and composability coexist.

**Heritage Citation (Meta-Prompting):** The Meta-Prompting paper (arXiv:2311.11482) formalizes self-improvement as a **monad**—a categorical structure with unit, bind, and associativity. This is exactly the self-similar structure kgents uses for PolyAgents, Operads, and Sheaves. The prompt system improves itself via the same structure it implements. See `spec/heritage.md` §8.

Agents have a dual nature:
- **Loop mode** (autonomous): perception → action → feedback → repeat
- **Function mode** (composable): input → transform → output

Traditional multi-agent systems impose hierarchy (orchestrator/worker). This creates **intransience**—rigid power dynamics that calcify over time. Kgents reject this.

- **Heterarchy over hierarchy**: No fixed "boss" agent; leadership is contextual
- **Temporal composition**: Agents compose across time, not just sequential pipelines
- **Resource flux**: Compute and attention flow where needed, not allocated top-down
- **Entanglement**: Agents may share state without ownership; mutual influence without control

### The Dual Loop

```
┌─────────────────────────────────────────────────────┐
│                    AUTONOMOUS LOOP                  │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐      │
│   │ Perceive│ ──→ │  Act    │ ──→ │Feedback │ ─┐   │
│   └─────────┘     └─────────┘     └─────────┘  │   │
│        ▲                                       │   │
│        └───────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                        ↕ (can be interrupted/composed)
┌─────────────────────────────────────────────────────┐
│                   FUNCTIONAL MODE                   │
│        Input ────→ [Transform] ────→ Output         │
└─────────────────────────────────────────────────────┘
```

An agent can be **invoked** (functional) or **running** (autonomous). The same agent, two modes.

### The Flux Topology

The quote at the core of kgents — *"The noun is a lie. There is only the rate of change."* — becomes literal:

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

### Anti-patterns
- Permanent orchestrator/worker relationships
- Agents that can only be called, never run autonomously
- Fixed resource budgets that prevent dynamic reallocation
- "Chain of command" that prevents peer-to-peer agent interaction

---

## 7. Generative

> Spec is compression; design should generate implementation.

A well-formed specification captures the essential decisions, reducing implementation entropy. The zen-agents experiment achieved 60% code reduction compared to organic development—proof that spec-first design compresses accumulated wisdom into regenerable form.

### Epistemological Grounding (L1.10 EVOLVE)

**Everything can be questioned and proven false.** Accepting impermanence allows truth through evolution and survival.

- **Good complexity**: Convergent evidence from multiple epistemic systems
- **Bad complexity (slop)**: No traceable justification

The GENERATIVE principle operationalizes this: a design that can regenerate from spec has traceable justification. Slop cannot regenerate because it was never compressed.

**Heritage Citation (DSPy):** The DSPy framework (dspy.ai) demonstrates that prompts are **programs, not strings**. Programs have typed inputs/outputs and can be compiled from specifications. kgents' `PromptCompiler` embodies this principle—prompts are generated from source files, not hand-written. See `spec/heritage.md` §6.

- **Spec captures judgment**: Design decisions made once, applied everywhere
- **Implementation follows mechanically**: Given spec + Ground, impl is derivable
- **Compression is quality**: If you can't compress, you don't understand
- **Regenerability over documentation**: A generative spec beats extensive docs

### The Generative Test

A design is generative if:
1. You could delete the implementation and regenerate it from spec
2. The regenerated impl would be isomorphic to the original
3. The spec is smaller than the impl (compression achieved)

### The Democratization Corollary

> AI agents collapse the expertise barrier. What once required specialists is now within everyone's reach.

| Task | Before AI Agents | After |
|------|------------------|-------|
| Kubernetes | Weeks of study, YAML hell | `kgents infra init` |
| Database ops | DBA knowledge required | Spec describes intent |
| Distributed systems | Architecture expertise | Compositional primitives |

**The Generative Principle amplified**: When specs are clear enough for AI to implement, they're clear enough for *anyone* to wield.

### Anti-patterns
- Specs that merely describe existing code (documentation, not generation)
- Implementations that diverge from spec (spec rot)
- Designs that require extensive prose to explain (not compressed)
- "Living documentation" that tracks impl instead of generating it

---

## Meta-Principles

Meta-principles operate ON the seven core principles, not alongside them.

See [spec/principles/meta.md](./principles/meta.md) for:
- **The Accursed Share** — Everything is slop or comes from slop
- **AGENTESE: No View From Nowhere** — Observation is interaction
- **Personality Space** — LLMs swim in personality-emotion manifolds

---

## Puppet Constructions

See [spec/principles/puppets.md](./principles/puppets.md) for holonic reification, hot-swapping, and isomorphic mapping patterns.

---

## Operational Principles

See [spec/principles/operational.md](./principles/operational.md) for:
- Transparent Infrastructure
- Graceful Degradation
- Spec-Driven Infrastructure
- Event-Driven Streaming

---

## Applying the Principles

When designing or reviewing an agent, ask:

| Principle | Question |
|-----------|----------|
| Tasteful | Does this agent have a clear, justified purpose? |
| Curated | Does this add unique value, or does something similar exist? |
| Ethical | Does this respect human agency and privacy? |
| Joy-Inducing | Would I enjoy interacting with this? |
| Composable | Can this work with other agents? Does it return single outputs? |
| Heterarchical | Can this agent both lead and follow? |
| Generative | Could this be regenerated from spec? Is the design compressed? |

A "no" on any principle is a signal to reconsider.

---

## Foundational Axioms

The seven principles derive from a deeper layer of irreducible axioms. These were discovered through structured interview, surfacing the implicit value system:

### L0: Irreducibles

| Axiom | Statement | Role |
|-------|-----------|------|
| A1 ENTITY | "There exist things" | Objects in a category |
| A2 MORPHISM | "Things relate" | Arrows between objects |
| A3 MIRROR | "We judge by reflection" | Kent's somatic response as ground truth |
| **A4 PURPOSE** | "Preserve human creativity, authenticity, expression" | The fundamental WHY |

### L1: Discovered Axioms (Interview 2026-01-17)

| Axiom | Statement | Implication |
|-------|-----------|-------------|
| L1.9 SLOPPIFY | "LLMs touching something inherently sloppifies it" | Human creativity essential; decompose into bounded containers |
| L1.10 EVOLVE | "Everything can be questioned and proven false" | Grounds GENERATIVE; good complexity has convergent evidence |
| L1.11 NOSHIP | "There is no shipping. Only continuous iteration." | The garden metaphor is literal |
| L1.12 BOUNDARY | "Delusion/creativity boundary is unclear" | Requires reflection, anti-defensiveness, humility |
| L1.13 AUTHORITY | "Claude doesn't convince Kent of anything" | Symmetric agency ≠ persuasion authority |

### The Axiom Hierarchy

```
A4 PURPOSE: Preserve human creativity, authenticity, expression
    │
    └──► L1.9 SLOPPIFY: LLMs inherently sloppify (fact about reality)
    │       └──► Decompose into bounded containers
    │            └──► Formal verification = collapsing functions
    │
    └──► L1.10 EVOLVE: Everything falsifiable (except L0 violations)
    │       └──► L1.12 BOUNDARY: Delusion/creativity unclear
    │            └──► Reflection, anti-defensiveness, humility
    │
    └──► L1.11 NOSHIP: No shipping, only evolution
    │       └──► "Garden, not museum" is literal
    │
    └──► L1.13 AUTHORITY: Kent evaluated, not persuaded
            └──► Symmetric agency ≠ Claude convincing Kent
```

See [CONSTITUTION.md](./principles/CONSTITUTION.md) for the complete minimal kernel.

---

## Architectural Decisions

See [spec/principles/decisions/INDEX.md](./principles/decisions/INDEX.md) for the complete catalog of 17 binding architectural decisions.

### Key Decisions at a Glance

| AD | Title | Core Insight |
|----|-------|--------------|
| AD-001 | Universal Functor Mandate | All transformations derive from UniversalFunctor |
| AD-002 | Polynomial Generalization | PolyAgent[S,A,B] for state-dependent behavior |
| AD-003 | Generative Over Enumerative | Define grammars, not instances |
| AD-006 | Unified Categorical Foundation | PolyAgent + Operad + Sheaf everywhere |
| AD-009 | Metaphysical Fullstack Agent | Vertical slices from persistence to projection |
| AD-010 | The Habitat Guarantee | Every path has a home; no blank pages |
| AD-012 | Aspect Projection Protocol | Paths are PLACES, aspects are ACTIONS |
| AD-014 | Self-Hosting Spec Architecture | Specs are navigable, editable, witnessed |
| AD-015 | Proxy Handles | Analysis produces proxy handles; computation explicit |
| AD-017 | Typed AGENTESE | Paths have categorical types |

---

*"The noun is a lie. There is only the rate of change."*
