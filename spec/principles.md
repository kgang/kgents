# Design Principles

These six principles guide all kgents design decisions.

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

### Anti-patterns
- Monolithic agents that can't be broken apart
- Agents with hidden state that prevents composition
- "God agents" that must be used alone

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

## Applying the Principles

When designing or reviewing an agent, ask:

| Principle | Question |
|-----------|----------|
| Tasteful | Does this agent have a clear, justified purpose? |
| Curated | Does this add unique value, or does something similar exist? |
| Ethical | Does this respect human agency and privacy? |
| Joy-Inducing | Would I enjoy interacting with this? |
| Composable | Can this work with other agents? |
| Heterarchical | Can this agent both lead and follow? Does it avoid fixed hierarchy? |

A "no" on any principle is a signal to reconsider.
