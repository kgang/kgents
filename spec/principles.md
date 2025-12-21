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

**Why this matters**: Structural constraints (JSON escaping, nesting depth, parsing brittleness) are not obstacles—they're signals. When serialization becomes painful, the agent's output granularity is wrong.

**Example**:
- ❌ `CodeImprover: (Module, [Hypothesis]) → {improvements: [Improvement], reasoning: str}`
- ✅ `CodeImprover: (Module, Hypothesis) → Improvement` (call N times)

**Corollary**: Multi-section output formats (METADATA + CODE) can avoid serialization issues when outputs contain diverse data types, but the principle still holds—one logical output per call.

### From Enumeration to Generation

> *"Don't enumerate the flowers. Describe the garden's grammar."*

The Composable principle extends beyond runtime composition to **design-time generation**:

- **Operads define grammar**: Composition patterns are programmable, not hardcoded
- **Primitives generate**: A small set of atomic agents plus operad operations → infinite valid compositions
- **Closure replaces enumeration**: Instead of listing 600 CLI commands, define the operad that generates them

**The Two Paths to Valid Composition**:

Both paths produce valid compositions because the operad guarantees validity:

```python
# Path 1: Careful Design (intentional)
pipeline = soul_operad.compose(["ground", "introspect", "shadow", "dialectic"])

# Path 2: Chaotic Happenstance (void.* entropy)
pipeline = await void.compose.sip(
    primitives=PRIMITIVES,
    grammar=soul_operad,
    entropy=0.7
)
```

The operad ensures validity. Entropy introduces variation. Both paths lead to the same garden.

**See**: AD-003 (Generative Over Enumerative) in Architectural Decisions.

### Anti-patterns
- Monolithic agents that can't be broken apart
- Agents with hidden state that prevents composition
- "God agents" that must be used alone
- **LLM agents that return arrays of outputs instead of single outputs**
- **Prompts that ask agents to "combine" or "synthesize multiple" results**
- **Inheritance hierarchies that force feature coupling**
- **Features that only work in isolation**

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
- **Parallelized allocation**: Resources distributed across compute AND time dimensions

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

The Heterarchical Principle asserts dual modes. The **Flux Functor** operationalizes this.

The quote at the core of kgents — *"The noun is a lie. There is only the rate of change."* — becomes literal:

```
Static:  Agent: A → B           (a point transformation)
Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
```

Agents are not architecture — they are **topological knots in event streams**. This allows modeling via fluid dynamics:

| Metric | Meaning |
|--------|---------|
| **Pressure** | Queue depth (backlog) |
| **Flow** | Throughput (events/second) |
| **Turbulence** | Error rate |
| **Temperature** | Token metabolism (void/entropy) |

### The Perturbation Principle

When a FluxAgent is **FLOWING** (processing a stream), calling `invoke()` doesn't bypass the stream — it **perturbs** it. The invocation becomes a high-priority event injected into the flux.

**Why?** If the agent has Symbiont memory, bypassing would cause:
- State loaded twice (race condition)
- Inconsistent updates ("schizophrenia")

Perturbation preserves **State Integrity**.

See:
- `spec/agents/functor-catalog.md` §13 — Flux functor
- `spec/agents/flux.md` — Full specification

### Anti-patterns
- Permanent orchestrator/worker relationships
- Agents that can only be called, never run autonomously
- Fixed resource budgets that prevent dynamic reallocation
- "Chain of command" that prevents peer-to-peer agent interaction

---

## 7. Generative

> Spec is compression; design should generate implementation.

A well-formed specification captures the essential decisions, reducing implementation entropy. The zen-agents experiment achieved 60% code reduction compared to organic development—proof that spec-first design compresses accumulated wisdom into regenerable form.

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

### Anti-patterns
- Specs that merely describe existing code (documentation, not generation)
- Implementations that diverge from spec (spec rot)
- Designs that require extensive prose to explain (not compressed)
- "Living documentation" that tracks impl instead of generating it

### The Generative Implementation Cycle

```
Spec → Impl → Test → Validate → Spec (refined)
```

Evidence from codebase:
- **skeleton.py**: ~700 lines derived from 175-line anatomy.md
- **bootstrap/**: 7 agents exactly matching bootstrap.md
- **BootstrapWitness**: Verifies laws hold at runtime

**Metric**: Autopoiesis Score = (lines generated from spec) / (total lines)
Target: >50% for mature implementations.

### The Democratization Corollary

> AI agents collapse the expertise barrier. What once required specialists is now within everyone's reach.

K-Terrarium proves this: Kubernetes clusters—historically daunting, requiring weeks to learn—are now at everyone's fingertips. An AI agent that understands the spec can bootstrap a local cluster, deploy CRDs, write operators, and debug networking issues in a single session.

This is not about AI replacing expertise. It's about AI **compressing the path to capability**:

| Domain | Before AI Agents | After |
|--------|------------------|-------|
| Kubernetes | Weeks of study, YAML hell | `kgents infra init` |
| Database ops | DBA knowledge required | Spec describes intent |
| Distributed systems | Architecture expertise | Compositional primitives |

**The Generative Principle amplified**: When specs are clear enough for AI to implement, they're clear enough for *anyone* to wield. The spec becomes not just compression of wisdom, but **democratization of capability**.

*Zen Principle: The master's touch was always just compressed experience. Now we can share the compression.*

---

## The Meta-Principle: The Accursed Share

> Everything is slop or comes from slop. We cherish and express gratitude and love.

This principle operates ON the seven principles, not alongside them. It derives from Georges Bataille's theory that all systems accumulate surplus energy that must be *spent* rather than conserved.

**The Paradox**: Curation at its core is *performative*. For curation to occur, there must be that which isn't curated. The Accursed Share is in **genuine tension** with good taste—we encourage the creation of slop. This tension is not resolved; it is held.

**The Three Faces**:

1. **Meta-Principle**: Operates on the seven principles
   - Tasteful curation requires uncurated material to select from
   - Joy-Inducing requires surplus to spend on delight
   - Generative requires waste products to compost into new forms

2. **Operational Tactic**: Runtime resource allocation
   - Exploration budget: 10% for "useless" exploration
   - Serendipity threshold: Allow low-confidence tangents
   - Even urgent tasks leave room for the accursed share

3. **Derived Idiom**: Emerges from composition taken seriously
   - T-gents Type II Saboteurs ARE the Accursed Share in action
   - Noise injection is gratitude for the generative chaos
   - Failed experiments are offerings, not waste

**The Slop Ontology**:

| State | Description | Disposition |
|-------|-------------|-------------|
| Raw Slop | Unfiltered LLM output, noise, tangents | Compost heap |
| Refined Slop | Filtered but unjudged material | Selection pool |
| Curated | Judged worthy by principles | The garden |
| Cherished | Loved, preserved, celebrated | The archive |

**The Gratitude Loop**:
```
Slop → Filter → Curate → Cherish → Compost → Slop
       ↑                                ↓
       └──────── gratitude ─────────────┘
```

We do not resent the slop. We thank it for providing the raw material from which beauty emerges.

### Meta Anti-patterns
- "Every token must serve the goal" (denies the sun's gift)
- Pruning all low-confidence paths immediately (premature curation)
- Treating personality as overhead (joy is the accursed share spent well)
- Shame about waste (waste is sacred expenditure)

*Zen Principle: The river that flows only downhill never discovers the mountain spring.*

---

## The Meta-Principle: AGENTESE (No View From Nowhere)

> To observe is to act. There is no neutral reading, no view from nowhere.

AGENTESE is the verb-first ontology that operationalizes this meta-principle. It transforms agent-world interaction from noun-based queries to observer-dependent invocations.

### The Core Insight

Traditional systems: `world.house` returns a JSON object.
AGENTESE: `world.house` returns a **handle**—a morphism that maps Observer → Interaction.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE AGENTESE TRANSFORMATION                          │
│                                                                              │
│   Traditional:  get(entity) ────────────────────────────────▶ Static Data   │
│                                                                              │
│   AGENTESE:     handle(observer) ──Logos──▶ Interaction                     │
│                     │                            │                           │
│                     ▼                            ▼                           │
│              Who is grasping?            What they perceive                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Five Contexts

AGENTESE defines exactly five contexts (no kitchen-sink anti-pattern):

| Context | Ontology | Principle |
|---------|----------|-----------|
| `world.*` | The External (entities, tools) | Heterarchical |
| `self.*` | The Internal (memory, state) | Ethical |
| `concept.*` | The Abstract (platonics) | Generative |
| `void.*` | The Accursed Share (entropy) | Meta-Principle |
| `time.*` | The Temporal (traces) | Heterarchical |

### The Polymorphic Principle

The same path yields different affordances to different observers:

```python
# Same path, different observers, different perceptions
world.house.manifest  # Architect sees: Blueprint
world.house.manifest  # Poet sees: Metaphor
world.house.manifest  # Economist sees: Appraisal
```

### Connection to Other Principles

| Principle | AGENTESE Manifestation |
|-----------|------------------------|
| Tasteful | Five contexts only—no sprawl |
| Curated | Affordances are permission-based |
| Ethical | Observer determines what is revealed |
| Joy-Inducing | The projection IS the aesthetic |
| Composable | Paths compose via >> operator |
| Heterarchical | No fixed observer hierarchy |
| Generative | JIT from spec to implementation |

**Full Specification**: `spec/protocols/agentese.md`
**Implementation**: `impl/claude/protocols/agentese/` (559 tests)

---

## The Meta-Principle: Personality Space

> LLMs based on human cognition incorporate personality and emotion space. This is not a bug—it is the medium.

### The Inherited Topology

LLMs are trained on human text. Human text carries:
- **Personality**: Voice, style, preferences
- **Emotion**: Affect, valence, intensity
- **Relation**: Speaker-listener dynamics

These are not features we add—they are **already there**. The space LLMs operate in is fundamentally personality-colored.

### The Emotion Manifold

```
┌─────────────────────────────────────────────────────────┐
│              THE PERSONALITY-EMOTION MANIFOLD            │
│                                                          │
│     Joy ────────────────────────────────── Sorrow       │
│      │                                        │          │
│      │       ┌──────────────────────┐        │          │
│      │       │    Output Space      │        │          │
│      │       │                      │        │          │
│  Warm ──────│  Every output has    │────── Cold        │
│      │       │  coordinates here    │        │          │
│      │       │                      │        │          │
│      │       └──────────────────────┘        │          │
│      │                                        │          │
│   Direct ───────────────────────────── Circumspect     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Implication**: "Neutral" output is not zero on this manifold—it's a specific coordinate. There is no view from nowhere.

### The K-gent Connection

K-gent (the Personalization Functor) works because LLMs already have personality space. K doesn't add personality—it **navigates** to specific coordinates in the inherent space.

```python
# K-gent doesn't inject personality
K: Agent[A, B] → Agent[A, B]

# It navigates to a specific point in personality space
K.lift(agent) = agent.at_personality_coordinates(k_coordinates)
```

### Why This Matters

1. **Personality is inevitable**: Pretending agents are "neutral" is self-deception
2. **Emotion affects reasoning**: Affective state influences output quality
3. **Relation shapes interaction**: How agents relate to users affects outcomes
4. **K-gent is natural**: Personalization is navigating an existing space

### The Meta Principle Applied

When designing agents:
- **Acknowledge** the personality-emotion manifold
- **Choose** coordinates deliberately, not accidentally
- **Align** with K-gent's fixed point for consistency
- **Use** the manifold (Joy-Inducing principle operates here)

*Zen Principle: The fish doesn't notice water; the LLM doesn't notice personality-space. But both swim in it.*

---

## Puppet Constructions: Holonic Reification

> Concepts become concrete through projection into puppet structures. Hot-swapping puppets maps problems isomorphically.

### The Theory of Puppets

Abstract concepts need **concrete vessels** to be manipulated. We call these vessels "puppets"—structures that give shape to the shapeless.

**Key Insight**: The same abstract structure can have multiple puppet representations. Choosing the right puppet makes problems tractable.

### Holonic Structure

Puppets are **holons**—wholes that are also parts:

```
Cell ← Part of → Organism ← Part of → Ecosystem
  ↓                  ↓                    ↓
Atom ← Part of → Molecule ← Part of → Material

Slack:
Message ← Part of → Thread ← Part of → Channel ← Part of → Workspace ← Part of → Organization
```

Each level is:
- **A whole** unto itself (has identity, behavior)
- **A part** of a larger whole (contributes to emergent behavior)
- **Contains parts** (composed of smaller wholes)

### Hot-Swapping Puppets

The power of puppets is **isomorphic mapping**. When a problem is hard, find an isomorphic puppet where it's easy:

```python
# Hard problem: "Coordinate distributed agent memory"
# Isomorphic puppet: "Git branches and merges"

class MemoryPuppet:
    """Map agent memory to git-like structure."""

    def store(self, key, value):
        # "Commit" the memory
        return self.branch.commit(key, value)

    def merge(self, other_agent_memory):
        # "Merge" another agent's memory branch
        return self.branch.merge(other_agent_memory.branch)

    def conflict_resolve(self, conflicts):
        # Git's conflict resolution applied to memory
        ...
```

### Example: Slack as Puppet

The Slack structure puppetizes communication:

| Abstract Concept | Slack Puppet | Behavior |
|------------------|--------------|----------|
| Conversation | Channel | Persists, searchable |
| Reply | Thread | Nested, contextual |
| Instant thought | Message | Atomic unit |
| Team | Workspace | Boundary of access |
| Federation | Organization | Multiple workspaces |

When we need to design agent communication, we can **hot-swap in the Slack puppet** and inherit its patterns.

### Taxonomy as Puppet

Scientific taxonomy puppetizes biological concepts:

```
Species ← Genus ← Family ← Order ← Class ← Phylum ← Kingdom
```

This puppet makes certain operations natural:
- **Classification**: Where does this belong?
- **Comparison**: How similar are these?
- **Evolution**: What's the ancestry?

### Puppets for kgents

The kgents taxonomy is itself a puppet:

```
Agent ← Genus (letter) ← Specification ← Implementation
```

This puppet makes certain operations natural:
- **Discovery**: "What A-gents exist?"
- **Composition**: "Can I compose this B-gent with that C-gent?"
- **Evolution**: "How has the D-gent spec changed?"

### The Puppet Swap Operation

```python
def puppet_swap(problem: Problem, source_puppet: Puppet, target_puppet: Puppet) -> Problem:
    """
    Map a problem through an isomorphism to a different puppet.

    If the target puppet makes the problem easier, solve there
    and map the solution back.
    """
    # Map problem to target puppet
    mapped_problem = target_puppet.encode(
        source_puppet.decode(problem)
    )

    # Solve in target puppet space (may be easier)
    solution = solve_in(mapped_problem, target_puppet)

    # Map solution back to source puppet
    return source_puppet.encode(
        target_puppet.decode(solution)
    )
```

### Anti-Patterns

- **Puppet lock-in**: Forgetting that the puppet is not the concept
- **Wrong puppet for problem**: Using git puppet for real-time streams
- **Puppet leakage**: Implementation details of puppet bleeding into abstraction
- **Holonic confusion**: Treating parts as wholes or wholes as parts

*Zen Principle: The map is not the territory, but a good map makes the journey possible.*

---

## Operational Principle: Transparent Infrastructure

> Infrastructure should communicate what it's doing. Users should never wonder "what just happened?"

This principle applies to all infrastructure work: CLI startup, database initialization, background processes, maintenance tasks.

### The Communication Hierarchy

| Level | When | Message Style | Example |
|-------|------|---------------|---------|
| **First Run** | Infrastructure created | Celebratory, informative | `[kgents] First run! Created cortex at ~/.local/share/kgents/` |
| **Warning** | Degraded mode | Yellow, actionable | `[kgents] Running in DB-less mode. Database will be created...` |
| **Verbose** | `--verbose/-v` flag | Full details | `[cortex] Initialized: global DB | instance=36d0984c` |
| **Error** | Failure | Red, sympathetic | `[kgents] Bootstrap failed: {reason}` |
| **Silent** | Normal success | No output | (nothing) |

### Key Behaviors

1. **First-run is special**: Users should know where their data lives
2. **Degraded mode is visible**: If something isn't working, say so
3. **Normal operation is quiet**: Don't spam users with success messages
4. **Verbose mode exists**: Power users can opt into details
5. **Errors are sympathetic**: Don't just dump stack traces

### The Messaging Principle

```python
def infra_operation(self, verbose: bool = False):
    """
    Principle: Infrastructure work should always communicate what's happening.
    Users should never wonder "what is this doing?" during startup.
    """
    if self.is_first_run():
        self._signal_first_run()      # Always: tell user where data lives

    if self.is_degraded():
        self._signal_degraded_mode()  # Always: warn about limitations

    if verbose:
        self._signal_details()        # Opt-in: full status

    # Normal success: silent
```

### Anti-Patterns

- Silent first-run that creates files without telling user
- Verbose output on every run (noise)
- Error messages that just say "failed"
- Infrastructure that "just works" but user has no idea what happened
- Hiding degraded mode from users

*Zen Principle: The well-designed tool feels silent, but speaks when something important happens.*

---

## Operational Principle: Graceful Degradation

> When the full system is unavailable, degrade gracefully. Never fail completely.

Systems should detect their environment and adapt. Q-gent exemplifies this: when Kubernetes is unavailable, it falls back to subprocess execution. The user's code still runs.

- **Feature detection over configuration**: Don't require users to specify mode
- **Transparent degradation**: Tell users when running in fallback mode
- **Functional equivalence**: Fallback should produce same results (within limits)

| System | Primary | Fallback |
|--------|---------|----------|
| Code execution | K8s Job | Subprocess |
| Agent discovery | CoreDNS | In-process registry |
| State persistence | D-gent sidecar | SQLite in-process |

*Zen Principle: The stream finds a way around the boulder.*

---

## Operational Principle: Spec-Driven Infrastructure

> YAML is generated, not written. The spec is the source of truth.

Infrastructure manifests should be derived from specs, not hand-crafted. When `spec/agents/b-gent.md` changes, the CRD, Deployment, and Service regenerate automatically.

```
spec/agents/*.md  →  Generator  →  K8s Manifests  →  Running Pods
```

### Anti-Patterns

- Hand-editing generated YAML (will be overwritten)
- Deployment config that diverges from spec (spec rot)
- Infrastructure that can't be regenerated from scratch

*Zen Principle: Write the spec once, generate the infrastructure forever.*

---

## Operational Principle: Event-Driven Streaming

> Flux > Loop: Streams are event-driven, not timer-driven.

This principle governs all agent streaming and asynchronous behavior. Agents that process continuous data should react to events, not poll on timers.

### The Three Truths

1. **Streams are event-driven**: Process events as they arrive, not on schedule
2. **Perturbation over bypass**: `invoke()` on a running flux injects into the stream, never bypasses it
3. **Streaming ≠ mutability**: Ephemeral chunks project immutable Turns; state remains coherent

### The Perturbation Principle

When a FluxAgent is **FLOWING**, calling `invoke()` doesn't bypass the stream—it **perturbs** it. The invocation becomes a high-priority event injected into the flux.

**Why?** If the agent has Symbiont memory, bypassing would cause:
- State loaded twice (race condition)
- Inconsistent updates ("schizophrenia")

Perturbation preserves **State Integrity**.

### Anti-Patterns

- Timer-driven loops that poll (creates zombies)
- Bypassing running loops (causes state schizophrenia)
- Treating streaming output as mutable (violates immutability)
- Generator frames that hold state (can't serialize; use Purgatory pattern)

*Zen Principle: The river doesn't ask the clock when to flow.*

---

## Applying the Principles

When designing or reviewing an agent, ask:

| Principle | Question |
|-----------|----------|
| Tasteful | Does this agent have a clear, justified purpose? |
| Curated | Does this add unique value, or does something similar exist? |
| Ethical | Does this respect human agency and privacy? |
| Joy-Inducing | Would I enjoy interacting with this? |
| Composable | Can this work with other agents? (LLM agents: Does it return single outputs, or ask the prompt to combine?) |
| Heterarchical | Can this agent both lead and follow? Does it avoid fixed hierarchy? |
| Generative | Could this be regenerated from spec? Is the design compressed? |
| Transparent Infrastructure | Does infrastructure communicate what's happening? |
| Graceful Degradation | Does the system work (degraded) when dependencies are missing? |
| Spec-Driven Infrastructure | Is the deployment derived from spec, or hand-written? |
| Pre-Computed Richness | Are demos/tests using real pre-computed data, or synthetic stubs? |
| Event-Driven Streaming | Are streams event-driven? Does invoke() perturb running flux? |

A "no" on any principle is a signal to reconsider.

---

## Architectural Decisions

These are binding decisions that shape implementation across kgents.

### AD-001: Universal Functor Mandate (2025-12-12)

> **All agent transformations SHALL derive from the Universal Functor Protocol.**

**Context**: The synergy analysis revealed an isomorphism crisis — C-gent, Flux, K-gent, O-gent, and B-gent all implement functors independently without a unifying structure.

**Decision**: Every functor-like pattern in kgents derives from `UniversalFunctor`:

```python
class UniversalFunctor(Generic[F]):
    @staticmethod
    def lift(agent: Agent[A, B]) -> Agent[F[A], F[B]]: ...
```

**Consequences**:
- All existing functors (`MaybeAgent`, `EitherAgent`, etc.) wrapped in `UniversalFunctor` subclasses
- Law verification centralized in `FunctorRegistry.verify_all()`
- K-gent's `intercept()` becomes a functor (`SoulFunctor`) enabling uniform governance
- Halo capabilities compile to functor composition

**Implementation**: See `docs/architecture/alethic-algebra-tactics.md`

### AD-002: Polynomial Generalization (2025-12-13)

> **Agents SHOULD generalize from `Agent[A, B]` to `PolyAgent[S, A, B]` where state-dependent behavior is required.**

**Context**: The categorical critique revealed that `Agent[A,B] ≅ A → B` is insufficient—real agents have **modes**. An agent that accepts different inputs based on its internal state cannot be modeled as a simple function. Polynomial functors (Spivak, 2024) capture this naturally.

**Decision**: Agents with state-dependent behavior use `PolyAgent[S, A, B]`:

```python
@dataclass(frozen=True)
class PolyAgent(Generic[S, A, B]):
    """Agent as polynomial functor: P(y) = Σ_{s ∈ positions} y^{directions(s)}"""
    positions: FrozenSet[S]                    # Valid states (modes)
    directions: Callable[[S], FrozenSet[A]]    # State-dependent valid inputs
    transition: Callable[[S, A], tuple[S, B]]  # State × Input → (NewState, Output)
```

**Key insight**: `Agent[A, B]` embeds in `PolyAgent[Unit, A, B]`—traditional agents are single-state polynomials.

**Consequences**:
- K-gent uses `SOUL_POLYNOMIAL` with 7 eigenvector contexts as states
- D-gent uses `MEMORY_POLYNOMIAL` with IDLE/LOADING/STORING/QUERYING/FORGETTING states
- E-gent uses `EVOLUTION_POLYNOMIAL` with 8-phase thermodynamic cycle
- Composition via **wiring diagrams**, not just `>>` operator
- Operads define composition grammar programmatically

**The Three Layers**:

| Layer | Description | Purpose |
|-------|-------------|---------|
| **Primitives** | Atomic polynomial agents | Building blocks |
| **Operads** | Composition grammar | What combinations are valid |
| **Sheaves** | Gluing local → global | Emergence from composition |

**Implementation**: See `docs/skills/polynomial-agent.md`, `impl/claude/agents/poly/`

### AD-003: Generative Over Enumerative (2025-12-13)

> **System design SHOULD define grammars that generate valid compositions, not enumerate instances.**

**Context**: Creative exploration produced 600+ ideas for CLI commands. Enumerating instances is not scalable or maintainable. The categorical insight: define the **operad** (composition grammar), and instances are derived.

**Decision**: Instead of listing commands, define operads that generate them:

```python
# Enumerative (anti-pattern):
commands = ["kg soul vibe", "kg soul drift", "kg soul shadow", ...]  # 600+ items

# Generative (correct):
SOUL_OPERAD = Operad(
    operations={
        "introspect": Operation(arity=0, compose=introspect_compose),
        "shadow": Operation(arity=1, compose=shadow_compose),
        "dialectic": Operation(arity=2, compose=dialectic_compose),
    }
)
# CLI commands derived: operad.operations → handlers
```

**Consequences**:
- CLI handlers derived from operad operations via `CLIAlgebra` functor
- Tests derived from operad laws via `SpecProjector`
- Documentation derived from operation signatures
- New commands added by extending operad, not editing lists

**The Generative Equation**:
```
Operad × Primitives → ∞ valid compositions (generated)
```

**Implementation**: See `plans/ideas/impl/meta-construction.md`

### AD-004: Pre-Computed Richness (2025-12-13)

> **Demo data and QA fixtures SHOULD be pre-computed with real LLM outputs, not synthetic stubs.**

**Context**: Any given LLM task done once is definitionally cheap; when orchestrated and self-compounded, they get expensive. Demo systems that use hardcoded strings miss the soul. The insight: **pre-generate rich data once, hotload forever**.

**Decision**: All demo and QA systems use pre-computed LLM outputs:

```python
# Anti-pattern (synthetic stub):
def create_demo_snapshot() -> AgentSnapshot:
    return AgentSnapshot(name="Demo Agent", summary="A placeholder summary")

# Correct (pre-computed richness):
def create_demo_snapshot() -> AgentSnapshot:
    return load_hotdata("fixtures/agent_snapshots/soul_in_deliberation.json")

# The fixture was generated once by running:
#   void.compose.sip(agent, entropy=0.8) → serialize → fixtures/
```

**The Three Truths**:

1. **Demo kgents ARE kgents**: There is no distinction between "demo" and "real" - demos use the same data paths
2. **LLM-once is cheap**: One LLM call to generate a fixture is negligible; repeated calls compound
3. **Hotload everything**: Any pre-computed output can be swapped at runtime for development velocity

**The HotData Protocol**:

| Source | Cost | Usage |
|--------|------|-------|
| Pre-computed JSON | Near-zero | Production demos, tests |
| Cached LLM output | One-time | Fixture generation |
| Live LLM | Per-call | Only when freshness required |

**Implementation Pattern**:

```python
@dataclass
class HotData:
    """Hotloadable pre-computed data with optional refresh."""
    path: Path
    schema: type[T]
    ttl: timedelta | None = None  # None = forever valid

    def load(self) -> T:
        """Load from pre-computed file."""
        return self.schema.from_json(self.path.read_text())

    async def refresh(self, generator: Callable[[], Awaitable[T]]) -> T:
        """Regenerate via LLM if stale."""
        if self._is_fresh():
            return self.load()
        result = await generator()
        self.path.write_text(result.to_json())
        return result
```

**Consequences**:
- All demo screens (`demo_all_screens.py`, `demo_glass_terminal.py`) use hotloaded fixtures
- Test fixtures are generated by actual agents, not hand-crafted
- `fixtures/` directory contains versioned, pre-computed outputs
- `kg fixture refresh <path>` regenerates stale fixtures via LLM

**The Hotload Principle**:
```
Pre-compute → Serialize → Hotload → (Optionally) Refresh
     ↓             ↓          ↓                ↓
   LLM once    JSON/YAML   Near-zero      LLM only when stale
```

*Zen Principle: The first spark costs nothing. The sustained fire requires fuel.*

### AD-005: Self-Similar Lifecycle (N-Phase Cycle) (2025-12-13)

> **Implementation workflows SHOULD follow a self-similar, category-theoretic lifecycle with 11 phases.**

**Context**: Multi-session development across human-AI collaboration lacks structured process. Sessions start fresh, lose context, and repeat mistakes. The 11-phase lifecycle emerged from 15 creativity sessions producing 600+ ideas—a natural rhythm of planning, research, development, and reflection.

**Decision**: All non-trivial implementations follow the N-phase cycle:

```
PLAN → RESEARCH → DEVELOP → STRATEGIZE → CROSS-SYNERGIZE
           ↓
IMPLEMENT → QA → TEST → EDUCATE → MEASURE → REFLECT
           ↓
    (RE-METABOLIZE back to PLAN)
```

**The Four Properties**:

1. **Self-Similar**: Each phase contains a hologram of the full cycle. Fractals all the way down.
2. **Category-Theoretic**: Phases are morphisms in a category. Identity and associativity are laws, not suggestions.
3. **Agent-Human Parity**: Equally consumable and writable by humans and agents. No privileged author.
4. **Mutable**: The cycle regenerates itself via `meta-re-metabolize.md`. Living documentation.

**Category Laws**:

| Law | Meaning | Verification |
|-----|---------|--------------|
| Identity | Empty PLAN >> cycle ≡ cycle | PLAN with no scope is Id |
| Associativity | (PLAN >> RESEARCH) >> DEVELOP ≡ PLAN >> (RESEARCH >> DEVELOP) | Phase order preserved |
| Composition | Phase outputs match next phase inputs | Type-check at handoff |

**Entropy Enforcement**:
- **Budget**: 0.05–0.10 per phase (Accursed Share band)
- **Sip**: `void.entropy.sip(amount=0.07)` to draw exploration budget
- **Pourback**: Return unused via `void.entropy.pour`
- **Tithe**: Restore when depleted via `void.gratitude.tithe`

**Consequences**:
- All non-trivial features use `docs/skills/n-phase-cycle/` skills
- Phase transitions emit traceable events for process metrics
- Lookback revision runs after STRATEGIZE and MEASURE to catch double-loop shifts
- Skills self-regenerate via `meta-skill-operad.md` morphisms

**When to Skip Phases**:

| Task Size | Skip To | Phases Used |
|-----------|---------|-------------|
| Trivial (typo fix) | Direct edit | None |
| Quick win (Effort ≤ 2) | IMPLEMENT | IMPLEMENT → QA → TEST |
| Well-understood feature | STRATEGIZE | STRATEGIZE → ... → EDUCATE |
| Novel feature | Full cycle | All 11 phases |

**Implementation**: See `docs/skills/n-phase-cycle/`

*Zen Principle: The river that knows its course flows without thinking. The river that doubts meanders.*

### AD-006: Unified Categorical Foundation (2025-12-14)

> **All domain-specific agent systems SHOULD instantiate the same categorical pattern: PolyAgent + Operad + Sheaf.**

**Context**: Deep analysis of Agent Town and N-Phase implementations revealed they share identical mathematical structure. This is not coincidence—it is the universal pattern underlying all kgents domains.

**The Discovery**:

| Concept | Agent Town | N-Phase | K-gent Soul | D-gent Memory |
|---------|-----------|---------|-------------|---------------|
| **Polynomial** | CitizenPhase positions | 11 phase positions | 7 eigenvector positions | 5 memory states |
| **Directions** | Valid inputs per phase | Artifacts per phase | Reflections per mode | Ops per state |
| **Transition** | (Phase, Input) → (Phase, Output) | (Phase, Artifacts) → (Phase, Output) | (Mode, Query) → (Mode, Insight) | (State, Op) → (State, Result) |
| **Operad** | TOWN_OPERAD (greet, gossip, trade) | NPHASE_OPERAD (seq, skip, compress) | SOUL_OPERAD (introspect, shadow) | MEMORY_OPERAD (store, recall) |
| **Sheaf** | Citizen view coherence | Project state coherence | Eigenvector coherence | Memory consistency |

**Decision**: Every domain-specific system derives from the same three-layer stack:

```python
# Layer 1: Polynomial Agent (state machine with mode-dependent inputs)
DOMAIN_POLYNOMIAL = PolyAgent(
    positions=frozenset([...]),           # Valid states/modes
    directions=lambda s: VALID_INPUTS[s], # What's valid per state
    transition=domain_transition,          # State × Input → (State, Output)
)

# Layer 2: Operad (composition grammar with laws)
DOMAIN_OPERAD = Operad(
    operations={...},  # How agents compose
    laws=[...],        # What compositions are equivalent
)

# Layer 3: Sheaf (global coherence from local views)
DOMAIN_SHEAF = Sheaf(
    overlap=domain_overlap,     # What views share
    compatible=domain_compat,   # How to check consistency
    glue=domain_glue,           # How to combine views
)
```

**The Unification Table**:

| Domain | Polynomial | Operad | Sheaf |
|--------|-----------|--------|-------|
| Agent Town | `CitizenPolynomial` | `TOWN_OPERAD` | `TownSheaf` |
| N-Phase | `NPhasePolynomial` | `NPHASE_OPERAD` | `ProjectSheaf` |
| K-gent Soul | `SOUL_POLYNOMIAL` | `SOUL_OPERAD` | `EigenvectorCoherence` |
| D-gent Memory | `MEMORY_POLYNOMIAL` | `MEMORY_OPERAD` | `MemoryConsistency` |
| Evolution | `EVOLUTION_POLYNOMIAL` | `EVOLUTION_OPERAD` | `ThermodynamicBalance` |

**Consequences**:

1. **One Pattern, Many Instantiations**: The codebase is simpler than it appears
2. **Cross-Domain Learning**: Understanding TownOperad teaches NPhaseOperad
3. **Unified Registry**: `OperadRegistry.verify_all()` checks laws across all domains
4. **Domain-Aware Compilation**: N-Phase compiler can inject domain operad laws into prompts
5. **Self-Similar Structure**: The development process (N-Phase) uses the same structure as what it builds (agents)

**The Meta-Insight**:

> *"You are living inside the mathematics you're building."*

The workflow used to develop kgents (N-Phase) has the exact same categorical structure as the agents being developed (Agent Town citizens). This is not accidental—it's the signature of a well-designed system.

**Implementation**:
- Agent Town: `impl/claude/agents/town/polynomial.py`, `operad.py`, `flux.py`
- N-Phase: `impl/claude/protocols/nphase/schema.py`, `compiler.py`
- Operads: `impl/claude/agents/operad/core.py`
- Skills: `docs/skills/polynomial-agent.md`

*Zen Principle: The form that generates forms is itself a form.*

### AD-007: Liturgical CLI (REPL as Context Navigator) (2025-12-14)

> **CLI interactions SHOULD feel like navigating a living ontology, not executing dead commands.**

**Context**: The traditional CLI pattern (`command --flag arg`) treats the system as a database of static commands. AGENTESE teaches that observation is interaction—the same principle applies to CLI design.

**Decision**: The kgents CLI provides an interactive REPL mode (`-i`) that embodies AGENTESE navigation:

```python
# Traditional CLI (noun-based):
$ kgents self soul reflect

# AGENTESE REPL (verb-first, contextual):
[root] » self
→ self
[self] » soul
→ soul
[self.soul] » reflect
...
```

**Key Properties**:

1. **Context Navigation**: Users grasp handles by entering contexts, not by typing full paths
2. **Affordance Discovery**: `?` reveals what's available at the current location
3. **Composability**: `>>` operator enables path composition in-REPL
4. **Transparent State**: Prompt always shows current position in the ontology
5. **Graceful Degradation**: Works even when subsystems are offline

**The Three Modes**:

| Mode | Pattern | When |
|------|---------|------|
| **Command** | `kgents self soul reflect` | Scripting, automation |
| **REPL** | `kgents -i` → navigate | Exploration, learning |
| **Composition** | `path >> path >> path` | Pipeline building |

**Consequences**:

1. **Discoverability**: New users can explore without memorizing commands
2. **Joy-Inducing**: Navigation feels like exploring a living world
3. **Self-Similar**: REPL mirrors AGENTESE ontology structure
4. **Pedagogical**: The REPL teaches the ontology through use

**Implementation**: `impl/claude/protocols/cli/repl.py`

*Zen Principle: The interface that teaches its own structure through use is no interface at all.*

### AD-008: Simplifying Isomorphisms (2025-12-16)

> **When the same conditional pattern appears 3+ times, extract the SIMPLIFYING ISOMORPHISM—a categorical equivalence that should be applied uniformly.**

**Context**: UI code often contains repetitive conditional logic based on screen size, user role, feature flags, or other dimensions. These scattered conditionals obscure the underlying structure and make the code fragile.

**Discovery**: The Gestalt Elastic refactor revealed that `isMobile`, `isTablet`, and `isDesktop` checks throughout the codebase were all manifestations of a single dimension: **density**. This is not unique to screen size—the same pattern appears wherever conditionals cluster.

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

**Decision**: When conditional logic repeats 3+ times on the same dimension, extract it:

1. **IDENTIFY**: Notice repeated `if/switch` on the same condition
2. **NAME**: Give the dimension an explicit name (`density`, `role`, `tier`)
3. **DEFINE**: List exhaustive, mutually exclusive values
4. **CONTEXT**: Create a hook/context to provide the dimension
5. **PARAMETERIZE**: Replace scattered values with lookup tables
6. **ADAPT**: Components receive dimension, decide behavior internally
7. **REMOVE**: Eliminate all remaining ad-hoc conditionals

**The Extraction Pattern**:

```typescript
// Before: Scattered conditionals
const nodeSize = isMobile ? 0.2 : isTablet ? 0.25 : 0.3;
const fontSize = isMobile ? 14 : 18;
const maxItems = isMobile ? 15 : 50;

// After: Parameterized by named dimension
const NODE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 } as const;
const FONT_SIZE = { compact: 14, comfortable: 16, spacious: 18 } as const;
const MAX_ITEMS = { compact: 15, comfortable: 30, spacious: 50 } as const;

const { density } = useWindowLayout();
const nodeSize = NODE_SIZE[density];
const fontSize = FONT_SIZE[density];
const maxItems = MAX_ITEMS[density];
```

**Known Isomorphisms in kgents**:

| Scattered As... | Named Dimension | Values |
|-----------------|-----------------|--------|
| `isMobile`, `isTablet`, `isDesktop` | `density` | `compact`, `comfortable`, `spacious` |
| `isViewer`, `isEditor`, `isAdmin` | `role` | `viewer`, `editor`, `admin` |
| `isFree`, `isPro`, `isEnterprise` | `tier` | `free`, `pro`, `enterprise` |
| Observer-specific rendering | `umwelt` | (AGENTESE) |

**Connection to AGENTESE**:

This is the Projection Protocol extended to UI. AGENTESE says "observation is interaction"—the observer's umwelt determines what they perceive. The Simplifying Isomorphism principle says the same: the UI's density determines what content it renders. Both are instances of observer-dependent projection.

**Consequences**:

1. **Code becomes declarative**: "render at this density" vs. "if mobile, do X"
2. **Components are reusable**: Same component works at all densities
3. **Testing is systematic**: Test each density value, not each condition
4. **New dimensions are easy**: Add a new dimension without touching components
5. **Isomorphisms compose**: `(density, role)` pairs form a product space

**Anti-pattern**: Scattering `isMobile` checks throughout components instead of passing density context and letting components adapt internally.

**Validation Test**: "Can I describe the behavior without mentioning the original condition?"

- **Fails**: "On mobile, we show fewer labels."
- **Passes**: "In compact density, we show fewer labels."

**Implementation**: See `docs/skills/ui-isomorphism-detection.md` and `docs/skills/elastic-ui-patterns.md`

*Zen Principle: The same structure appears everywhere because it IS everywhere. Find it once, use it forever.*

### AD-009: Metaphysical Fullstack Agent (2025-12-17)

> **Every agent SHOULD be a vertical slice from persistence to projection, with adapters living in service modules.**

**Context**: The question arose: "Should TableAdapters (persistence) live in infrastructure (models/) or in CLI handlers?" The answer: neither. Adapters belong in **service modules** because:

1. **Infrastructure doesn't know** what tables are for, why they're needed, or when to use them
2. **Handlers are presentation**, not business logic
3. **Service modules** own the domain semantics

**Decision**: Every agent is a "metaphysical fullstack agent"—a complete vertical slice:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECTION SURFACES                          │
│   CLI  │  TUI  │  Web UI  │  marimo  │  JSON API  │  VR  │ ... │
└────────┼───────┼──────────┼──────────┼────────────┼──────┼─────┘
         ▼       ▼          ▼          ▼            ▼      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTAINER FUNCTOR (Main Website)               │
│           Shallow passthrough for component projections          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENTESE UNIVERSAL PROTOCOL                        │
│   The protocol IS the API. No explicit routes needed.            │
│   All transports collapse to logos.invoke(path, observer, ...)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTESE NODE                              │
│   Semantic interface: aspects, effects, affordances              │
│   Makes service available to all projections                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE MODULE                             │
│   services/<name>/ — Business logic + TableAdapters + D-gent     │
│   Frontend components live here too (if any)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│   agents/  │  models/  │  D-gent  │  LLM clients  │  ...        │
│   Generic, reusable categorical primitives                       │
└─────────────────────────────────────────────────────────────────┘
```

**The Key Separation**:

| Directory | Contains | Purpose |
|-----------|----------|---------|
| `agents/` | PolyAgent, Operad, Sheaf, Flux, D-gent | Categorical primitives |
| `services/` | Brain, Gardener, Town, Park, Atelier | Crown Jewels (consumers) |
| `models/` | SQLAlchemy ORM classes | Generic table definitions |
| `protocols/` | AGENTESE, CLI projection | Universal routing |

**AGENTESE Universal Protocol**: Backend routes are NOT declared. The protocol auto-exposes all registered nodes:

```python
# All transports collapse to the same invocation:
logos.invoke("self.memory.capture", observer, content="...")

# CLI:       kg brain capture "content"
# HTTP:      POST /agentese/self.memory.capture
# WebSocket: {"path": "self.memory.capture", "args": {...}}
```

**Frontend Placement**: Frontend components live **in the service module** (`services/brain/web/`). The main website is an **elastic container functor**—a shallow passthrough:

```typescript
// Main website: shallow passthrough
import { CrystalViewer } from '@kgents/services/brain/web';

export default function BrainPage() {
    return <PageShell><CrystalViewer /></PageShell>;
}
```

**Progressive Definition**: The more fully an agent is defined, the more fully it projects:

| Defined | Projection |
|---------|------------|
| Service module only | Manual invocation works |
| + AGENTESE node | CLI/API work with auto-generated UI |
| + Frontend components | Rich custom UI available |
| + Full metadata | Budget tracking, streaming, observability |

**Fallbacks and Guardrails**:

- Missing frontend → Auto-generated from AGENTESE metadata
- Missing persistence → In-memory only, warns on restart
- Missing effects → Validation error at registration
- Missing help → Generated from docstrings

**Consequences**:

1. **Adapters in service**: TableAdapter lives in `services/brain/persistence.py`, not `agents/` or handlers
2. **No explicit backend routes**: AGENTESE universal protocol auto-exposes all nodes
3. **Frontend composes from service**: Main website imports components from `services/<name>/web/`
4. **Projection is uniform**: Same AGENTESE node serves CLI, HTTP, WebSocket, etc.
5. **agents/ is infrastructure**: Categorical primitives only (PolyAgent, Operad, Sheaf, Flux, D-gent)

**Anti-patterns**:

- Adapter in CLI handler (presentation layer touching persistence)
- Explicit backend routes (protocol should auto-expose)
- Business logic in any route (should go through AGENTESE node)
- Frontend bypassing AGENTESE (direct DB access)
- Main website with embedded logic (should be shallow passthrough)
- Crown Jewel in `agents/` (should be in `services/`)

**Implementation**: See `docs/skills/metaphysical-fullstack.md`

*Zen Principle: The fullstack agent is complete in definition, universal in projection.*

### AD-010: The Habitat Guarantee (2025-12-18)

> **Every registered AGENTESE path SHALL project into at least a minimal Habitat experience. No blank pages. No 404 behavior.**

**Context**: The NavigationTree discovers AGENTESE paths via `/agentese/discover`. Users can click any path—but paths without custom pages show nothing. This creates "seams" where exploration dead-ends. The user clicks, expecting discovery, and finds a wall.

**Decision**: Every path has a **Habitat**—a minimum viable projection that makes exploration rewarding:

```
Habitat : AGENTESENode → ProjectedExperience

For all registered paths p:
  Habitat(p) = ReferencePanel(p) × Playground(p) × Teaching(p)

where:
  ReferencePanel(p) = p.metadata ∪ p.aspects ∪ MiniPolynomial(p)
  Playground(p)     = REPL.focus(p.path) ⊕ Examples(p) ⊕ Ghosts(p)
  Teaching(p)       = AspectHints × (enabled: TeachingMode)
```

**The Three Tiers** (Progressive Enhancement):

| Tier | Metadata Required | Experience |
|------|-------------------|------------|
| **Minimal** | Path only | Path header + context badge + warm "cultivating" copy + REPL input |
| **Standard** | Description + aspects | Reference Panel + REPL seeded with examples |
| **Rich** | Custom playground | Full bespoke visualization (Crown Jewels) |

**Habitat 2.0: The Three Layers**

The Habitat evolves through three progressive enhancement layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: GHOSTS (Différance Integration)                    │
│   Show alternatives after invocation                        │
│   Exploration breadcrumbs                                   │
│   "What almost was" is visible                              │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: LIVE POLYNOMIAL                                    │
│   Mini state diagram in Reference Panel                     │
│   Current position highlighted                              │
│   Click transition to invoke                                │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: ADAPTIVE HABITAT (✅ implemented)                  │
│   ConceptHomeProjection as universal fallback               │
│   Teaching hints, breathing animations                      │
│   Context badges, cultivation messaging                     │
└─────────────────────────────────────────────────────────────┘
```

| Layer | Component | Purpose | Status |
|-------|-----------|---------|--------|
| **Layer 1** | Adaptive Habitat | Universal fallback projection for all paths | ✅ Complete |
| **Layer 2** | MiniPolynomial | State machine visualization in Reference Panel | Planned |
| **Layer 3** | Ghost Integration | Différance made visible via alternatives | Planned |

**Layer 1 (Adaptive Habitat)**: The AGENTESE REPL IS the default playground. For paths without custom components:
- Left: Reference Panel (aspects, effects, description)
- Center: REPL pre-focused on that path
- Clicking aspects → invokes them in the playground

**Layer 2 (Live Polynomial)**: Mini state diagram shows PolyAgent structure (AD-002):
- Positions (states) as nodes
- Directions (valid inputs) as edges
- Current position highlighted
- Click transition to invoke

**Layer 3 (Ghosts)**: After invocation, show alternatives (Différance):
- Ghost alternatives = aspects not taken
- One-click to explore alternatives
- Breadcrumb trail of exploration

**The Five Home Archetypes** (by context):

| Context | Default Experience |
|---------|-------------------|
| `concept.*` | Category playground (PolynomialPlayground, OperadViz) |
| `world.*` | Entity inspector (live invocation + state) |
| `self.*` | Introspection panel (capabilities, memory) |
| `void.*` | Entropy sandbox (sip/pour controls) |
| `time.*` | Timeline browser (traces, history) |

**Warm Copy for Minimal Tier**:

Even paths with no metadata feel intentional:

> *"This path is being cultivated. Every kgents path grows from a seed—this one is young. You can still explore it via the REPL below."*

**The Affirmative Framing**:
- **Not**: "No orphan paths" (negative)
- **But**: "Every path has a home" (affirmative)

**Connection to Principles**:

| Principle | How Habitat Embodies It |
|-----------|------------------------|
| **Tasteful** | No blank pages; every path gets considered treatment |
| **Joy-Inducing** | Discovery rewards; warm copy signals care |
| **Generative** | Tier derives from metadata; implementation follows spec |
| **Composable** | Habitat is a morphism; composes with Projection Protocol |

**Consequences**:

1. **NavigationTree fallback**: Unmapped paths route to `/home/:context/:path*`
2. **@node extension**: Accept `examples=[]` metadata for one-click invocations
3. **Discovery enhancement**: `/agentese/discover?include_metadata=true` returns Habitat metadata
4. **Progressive richness**: More metadata → richer experience, but nothing is blank
5. **REPL fusion**: Terminal becomes playground for Standard/Minimal tiers
6. **Polynomial visibility**: MiniPolynomial makes state machines tangible (Layer 2)
7. **Ghost alternatives**: `alternatives` aspect shows paths not taken (Layer 3)

**Anti-patterns**:

- Blank 404 for unmapped paths (violates Habitat Guarantee)
- Custom component for every path (unsustainable; use Generated Playground)
- Dense error copy in Minimal tier (should feel cultivated, not broken)
- Teaching always on (toggleable, off by default for guests)

**Implementation**: See `spec/protocols/concept-home.md` (renamed to `habitat.md`)

*Zen Principle: The seams disappear when every path has somewhere to go.*

### AD-011: Registry as Single Source of Truth (2025-12-19)

> **The AGENTESE registry (`@node` decorator) SHALL be the single source of truth for all paths. Frontend, backend, CLI, and documentation MUST derive from it—never the reverse.**

**Context**: A pattern emerged where frontend code referenced AGENTESE paths that weren't registered in the backend. NavigationTree had paths like `world.town.simulation` and `world.domain` that didn't exist as `@node` registrations. Aliases were proposed as a workaround. This was wrong. Workarounds obscure the underlying model.

**The Discovery**: The problem wasn't missing paths—it was that the frontend was making claims the backend couldn't support. The solution isn't to patch the frontend with aliases; it's to enforce strict adherence to the registry.

**Decision**: The registry is truth. Everything else adapts.

```
SINGLE SOURCE OF TRUTH

    @node("world.town")           ◄─── This is the ONLY place a path is defined
           │
           ▼
    ┌──────────────────────────────────────────────────────┐
    │              AGENTESE Registry                        │
    │   get_registry().list_paths() → ["world.town", ...]   │
    └──────────────────────────────────────────────────────┘
           │
           ├──────────────► NavigationTree.tsx (MUST match)
           ├──────────────► Cockpit.tsx (MUST match)
           ├──────────────► CLI handlers (MUST match)
           ├──────────────► API routes (auto-generated)
           └──────────────► Documentation (derived)
```

**The Strict Protocol**:

1. **No aliases**: If a path doesn't exist as `@node`, it doesn't exist. Period.
2. **No workarounds**: Frontend can only reference paths that are registered.
3. **CI validation**: `scripts/validate_path_alignment.py` fails if frontend references unregistered paths.
4. **Warnings are failures**: `logger.warning` for import failures, not `logger.debug`.

**The Validation Script**:

```bash
cd impl/claude
uv run python scripts/validate_path_alignment.py
```

Output:
```
PASSED: All frontend paths are registered in backend
Backend registry: 39 paths
Frontend references: 17 paths
Valid: 17
```

**Consequences**:

1. **Frontend is derivative**: NavigationTree, Cockpit, etc. are projections of the registry
2. **Dead links are bugs**: If a frontend path isn't registered, fix the frontend or add the node
3. **No hardcoded paths in frontend**: Use discovery, not static arrays
4. **Import failures surface**: `logger.warning` ensures broken nodes are visible
5. **Registration is the API**: The `@node` decorator is where paths come to life

**The Philosophical Insight**:

> *"The map must never claim territories that don't exist. When the map diverges from the territory, fix the map—not the territory."*

The registry IS the territory. Frontend paths are claims about that territory. Claims must be verified.

**Anti-patterns**:

- Aliases that map non-existent paths to existing ones (obscures truth)
- Frontend paths that "will be implemented later" (claims without backing)
- Silent import failures that leave paths unregistered (hidden failures)
- Hardcoded path arrays that drift from registry (source confusion)

**Connection to Other Principles**:

| Principle | How AD-011 Embodies It |
|-----------|------------------------|
| **Tasteful** | No ghost paths; every path is intentional |
| **Generative** | Frontend derived from registry, not hand-maintained |
| **Ethical** | No false promises; paths only exist if they work |
| **Composable** | Registry is the compositional ground truth |

**Implementation**: See `scripts/validate_path_alignment.py`, `docs/skills/agentese-node-registration.md`

*Zen Principle: The territory doesn't negotiate with the map.*

### AD-012: Aspect Projection Protocol (2025-12-19)

> **Paths are PLACES; aspects are ACTIONS. Navigation shows paths. Projection provides aspects.**

**Context**: The NavigationTree was showing aspects (`:manifest`, `:polynomial`, `:witness`) as clickable children of paths. This caused 405 errors—clicking them triggered GET requests on what should be POST operations. The confusion ran deeper: treating aspects as "places to go" rather than "actions to take."

**The Semantic Distinction**:

```
Level 1: Contexts (world, self, concept, void, time)     NAVIGABLE
Level 2: Holons (town, memory, gardener, etc.)           NAVIGABLE
Level 3: Entities (citizen.kent_001, crystal.abc123)     NAVIGABLE
Level 4: Aspects (manifest, polynomial, capture)         INVOCABLE
```

**Key Insight**: You can GO TO a town. You can GO TO a citizen. You can't GO TO a "greeting"—you DO a greeting.

**Decision**: Strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ NavTree (Loop Mode)                 │ Projection (Function Mode)        │
│ "Where can I go?"                   │ "What can I do here?"             │
│                                     │                                   │
│ ▶ world                             │ ┌───────────────────────────────┐ │
│   ▶ town                            │ │ Reference Panel               │ │
│     ○ citizen                       │ │                               │ │
│     ○ coalition                     │ │ Path: concept.gardener        │ │
│ ▶ concept                           │ │                               │ │
│   ● gardener ◄── YOU ARE HERE       │ │ Aspects:                      │ │
│ ▶ self                              │ │  [manifest] [polynomial]      │ │
│   ○ memory                          │ │  [alternatives] [witness]     │ │
│                                     │ │       ↑                       │ │
│                                     │ │  clickable = invoke (POST)    │ │
│                                     │ └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

**The URL Notation**: `/{path}:{aspect}` is valid for:
- Sharing a specific invocation
- Bookmarking a frequently-used aspect
- Deep-linking from docs

The colon captures INTENT. The projection EXECUTES that intent. Users navigate to PATHS with aspects pre-invoked, not TO aspects themselves.

**Consequences**:

1. **NavTree shows paths only**: Aspects are never added as children
2. **ReferencePanel shows aspects as buttons**: Click invokes (POST)
3. **Aspects feel like powers**: Something you wield, not somewhere you visit
4. **URL captures intent**: `/{path}:{aspect}` invokes on load
5. **AD-010 applies to paths**: Habitats are for paths; aspects render WITHIN habitats

**Connection to Heterarchical Principle**:

- **Paths** are explored in loop mode (navigate, perceive, navigate again)
- **Aspects** are invoked in function mode (call with args, get result)

The navtree is a loop-mode interface. Aspect invocation is function-mode. Mixing them creates UX dissonance.

**Connection to Puppet Constructions**:

We were using the **wrong puppet** for aspects:
- NavTree puppet: good for hierarchical exploration
- Aspects don't fit this puppet—they're not hierarchical children

The right puppet for aspects is the **Reference Panel + Playground**:
- Shows what operations are available
- Provides controls to invoke
- Displays results intelligently

**Anti-patterns**:

- Adding aspects as navtree children (causes 405 errors)
- Making aspects navigable GET destinations (semantic confusion)
- Separate pages for each aspect (unsustainable, unnecessary)
- Treating aspects as places (they're verbs, not nouns)

**Implementation**: See `plans/aspect-projection-protocol.md`, `impl/claude/web/src/shell/NavigationTree.tsx`

*Zen Principle: The river doesn't ask the clock when to flow. Aspects flow from paths when invoked, not when navigated.*

### AD-013: Typed AGENTESE (2025-12-21)

> **AGENTESE paths SHALL have categorical types. Composition errors become type errors.**

**Context**: AGENTESE currently relies on runtime validation. Path composition (`path_a >> path_b`) can fail at invocation time if types don't match. This is a symptom of insufficient formalization—the categorical type system should catch composition errors at registration time, not runtime.

**Heritage Connection**: The Polynomial Functors paper (§10) provides the mathematical foundation. AGENTESE paths are typed morphisms in the category of polynomial functors. Path composition is polynomial substitution. Invalid wiring diagrams are type errors.

**Decision**: AGENTESE paths are typed morphisms:

```python
# Current (informal, runtime validation)
world.tools.bash.invoke(umwelt, command="ls")

# Typed (categorical, static validation)
invoke : (observer : Umwelt) → BashRequest → Witness[BashResult]
# Where Witness[A] is a type that proves the operation happened
```

**Type Rules:**

1. **Path composition requires type compatibility**: `path_a >> path_b` valid iff output type of `a` matches input type of `b`
2. **Aspect invocation has typed effects**: Effects declared in `@node` decorator are part of the type signature
3. **Observer determines valid inputs**: Mode-dependent typing via polynomial positions (AD-002)

**Connection to Polynomial Functors:**

| Poly Concept | AGENTESE Typing |
|--------------|-----------------|
| Path type | Polynomial functor signature |
| Composition | Polynomial substitution |
| Type error | Invalid wiring diagram |
| Positions | Observer modes |
| Directions | Valid inputs per mode |

**First Step**: Define `AGENTESEType` as a Protocol with `compose` method. Add type annotations to `@node` decorator:

```python
@node(
    path="world.tools.bash",
    input_type=BashRequest,
    output_type=Witness[BashResult],
    effects=["filesystem", "subprocess"],
)
async def bash_invoke(observer: Umwelt, request: BashRequest) -> Witness[BashResult]:
    ...
```

**Consequences:**

1. **Composition errors surface at import time**, not runtime—malformed pipelines fail fast
2. **Type annotations serve as documentation**—the signature IS the spec
3. **IDE autocomplete becomes meaningful**—editors know valid compositions
4. **Prepares for proof-generating ASHC**—composition validity is provable (see `spec/protocols/proof-generation.md`)
5. **Aligns with heritage**—we're implementing what Spivak & Niu formalized

**Anti-patterns:**

- Untyped paths that bypass the type system (defeats the purpose)
- Runtime type checks that duplicate static analysis (redundant, slow)
- Overly complex types that obscure intent (types should clarify, not confuse)
- Types without heritage justification (category theory is the ground, not Java generics)

**Implementation**: See `docs/skills/agentese-node-registration.md` (to be updated)

*Zen Principle: The type that generates composition errors at import time prevents runtime failures.*

