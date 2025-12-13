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

This principle comes from [C-gents](c-gents/) but applies to all agents.

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
- `spec/c-gents/functor-catalog.md` §13 — Flux functor
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

**Implementation**: See `plans/architecture/alethic-algebra-tactics.md`

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

**Implementation**: See `plans/skills/polynomial-agent.md`, `impl/claude/agents/poly/`

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
