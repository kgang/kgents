# Meta-Principles

> *These principles operate ON the seven core principles, not alongside them.*

---

## The Accursed Share

> Everything is slop or comes from slop. We cherish and express gratitude and love.

This principle derives from Georges Bataille's theory that all systems accumulate surplus energy that must be *spent* rather than conserved.

**The Paradox**: Curation at its core is *performative*. For curation to occur, there must be that which isn't curated. The Accursed Share is in **genuine tension** with good taste—we encourage the creation of slop. This tension is not resolved; it is held.

### The Three Faces

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

### The Slop Ontology

| State | Description | Disposition |
|-------|-------------|-------------|
| Raw Slop | Unfiltered LLM output, noise, tangents | Compost heap |
| Refined Slop | Filtered but unjudged material | Selection pool |
| Curated | Judged worthy by principles | The garden |
| Cherished | Loved, preserved, celebrated | The archive |

### The Gratitude Loop

```
Slop → Filter → Curate → Cherish → Compost → Slop
       ↑                                ↓
       └──────── gratitude ─────────────┘
```

We do not resent the slop. We thank it for providing the raw material from which beauty emerges.

**Anti-patterns**: "Every token must serve the goal" (denies the sun's gift); pruning all low-confidence paths immediately (premature curation); treating personality as overhead (joy is the accursed share spent well); shame about waste (waste is sacred expenditure)

*Zen Principle: The river that flows only downhill never discovers the mountain spring.*

---

## AGENTESE: No View From Nowhere

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

### Connection to Core Principles

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

---

## Personality Space

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

*See also: `spec/protocols/agentese.md`, `spec/k-gent/persona.md`*
