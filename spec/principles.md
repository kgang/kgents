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
| **Transparent Infrastructure** | Does infrastructure communicate what's happening? |

A "no" on any principle is a signal to reconsider.
