# The Membrane — Co-Thinking Surface

> *"Stop documenting agents. Become the agent."*

**Status**: Draft
**Tier**: Crown Jewel
**Decision**: `fuse-ccad81de` (2025-12-22)

---

## Overview

The Membrane is a **single morphing surface** where Kent and K-gent think together. It replaces the traditional dashboard/navigation paradigm with context-aware rendering.

### Core Insight

Traditional agent UIs are *about* agents — browse paths, see diagrams, explore trails. The Membrane IS the agent — a co-pilot surface that morphs based on what you're working on.

---

## Generating Equations

```
Membrane = Focus × Witness × Dialogue
         : Context → Surface

Focus    : WorkingContext → Content
         | file f    → CodeView(f)
         | spec s    → SpecView(s)
         | concept c → ConceptView(c)
         | void      → Welcome

Witness  : Stream[Mark | Decision | Fusion]
         → Timeline of what's been witnessed

Dialogue : (History, Input) → Response
         → Where co-thinking happens
```

---

## State Machine

```
┌─────────────┐
│   Compact   │ ←── Focus only, deep work
└──────┬──────┘
       │ expand
       ▼
┌─────────────┐
│ Comfortable │ ←── Focus + Witness, normal
└──────┬──────┘
       │ expand
       ▼
┌─────────────┐
│  Spacious   │ ←── Full membrane, active co-thinking
└─────────────┘
```

Transitions:
- `expand`: More surface area for context
- `contract`: Focus down for deep work
- `context_change`: May trigger mode shift

---

## Surfaces

### Focus Pane

The Focus Pane shows **what you're working on**. Content is context-dependent:

| Context | Content |
|---------|---------|
| File open | Syntax-highlighted code with K-gent's understanding |
| Spec active | Rendered specification with derivation confidence |
| Concept | Conceptual explanation with related entities |
| Nothing | Welcome state, recent activity |

**Key Principle**: The focus is never empty. There's always something to look at.

### Witness Stream

Real-time stream of:
- **Marks** — `km "Completed X"`
- **Decisions** — `kg decide` fusions
- **Crystallizations** — Moments captured for memory

The stream shows **you're being heard**. Every action leaves a trace.

### Dialogue Pane

Where Kent and K-gent talk. Not a chatbot — a **co-thinking space**:
- History of exchanges
- Input for new thoughts
- Crystallize button to capture decisions

---

## No Navigation

The Membrane has **no routes, no pages, no navigation tree**.

Instead:
- Context determines what's shown
- Dialogue drives exploration
- Focus morphs based on conversation

Example flow:
```
Kent: "Show me the witness service"
→ Focus morphs to: services/witness/core.py
→ Witness shows: Related decisions about witness
→ Dialogue shows: K-gent's understanding of the code
```

---

## Elastic Behavior

The Membrane itself is elastic:

| Mode | Layout | Trigger |
|------|--------|---------|
| **Compact** | Focus only | Deep work, explicit request |
| **Comfortable** | Focus + Witness | Default state |
| **Spacious** | Focus + Witness + expanded Dialogue | Active conversation |

Mode responds to:
- Viewport size (responsive)
- Activity level (adaptive)
- Explicit toggle (user control)

---

## AGENTESE Integration

### Required Nodes

```
self.membrane.focus     → Get/set current focus context
self.membrane.mode      → Get/set elastic mode
self.witness.stream     → SSE stream of marks/decisions
self.context.current    → Current working context
self.dialogue.exchange  → Send message, receive response
```

### Observer Umwelt

The Membrane renders differently based on observer:
- **Developer** → Code-heavy focus, technical witness
- **Designer** → Aesthetic focus, visual witness
- **Philosopher** → Concept-heavy, dialectical witness

---

## Implementation Notes

### Foundation Primitives (Already Built)

| Primitive | Use |
|-----------|-----|
| `elastic/` | Three-mode responsive patterns |
| `joy/Fizz` | Subtle animation for witness stream |
| `joy/Hum` | Ambient background for dialogue |
| `useDesignPolynomial` | Temporal coherence across modes |

### New Components Needed

| Component | Purpose |
|-----------|---------|
| `Membrane.tsx` | Root component, single surface |
| `FocusPane.tsx` | Context-aware content |
| `WitnessStream.tsx` | Real-time mark/decision display |
| `DialoguePane.tsx` | Co-thinking interface |
| `useMembrane.ts` | State machine hook |
| `useWorkingContext.ts` | Context detection |

---

## Success Criteria

1. **One component** renders the entire app
2. **No react-router** — context, not routes
3. **Dialogue-first** — conversation drives interaction
4. **Witness visible** — decisions stream in real-time
5. **Joy-inducing** — feels like collaboration, not tool use

---

## Philosophical Grounding

The Membrane embodies:
- **Symmetric Agency** (Article I) — Kent and K-gent as peers
- **Fusion as Goal** (Article VI) — Co-thinking, not command/response
- **Joy-Inducing** (Principle 4) — Delight in interaction

*"The persona is a garden, not a museum."*

---

## References

- Plan: `plans/_membrane.md`
- Decision: `fuse-ccad81de`
- Foundation: `docs/skills/elastic-ui-patterns.md`

---

*Filed: 2025-12-22*
*Author: Kent + Claude (fusion)*
