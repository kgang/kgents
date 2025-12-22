# The Membrane — Radical Frontend Transformation

> *"Stop documenting agents. Become the agent."*

**Status**: ACTIVE
**Decision**: `fuse-ccad81de` (2025-12-22)
**Supersedes**: Timeline Explorer + Swarm Lab plan

---

## The Synthesis

| Position | View | Reasoning |
|----------|------|-----------|
| **Kent** | Timeline Explorer + Swarm Lab | Git history visualization, multi-agent outline refinement |
| **Claude** | Membrane — single morphing surface | Kill dashboard paradigm, become the co-pilot |
| **Fusion** | **Build the Membrane** | Radical transformation means the frontend IS the agent, not a window into it |

---

## Vision

The old frontend was a **documentation shell** — browse AGENTESE paths, see polynomial diagrams, explore trails. It was *about* agents.

**The Membrane is different**: One surface that morphs based on context. Not navigation, not routes, not pages. A **co-thinking surface** where Kent and K-gent work together.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  THE MEMBRANE                                                           │
│  ═══════════════════════════════════════════════════════════════════════│
│                                                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │      FOCUS PANE             │  │       WITNESS STREAM            │  │
│  │                             │  │                                 │  │
│  │  [Current working context]  │  │  • Kent committed burn          │  │
│  │  - What you're building     │  │  • Claude proposed vision       │  │
│  │  - Live code/spec view      │  │  • Fusion: membrane metaphor    │  │
│  │  - K-gent's understanding   │  │  • Decision: proceed            │  │
│  │                             │  │                                 │  │
│  └─────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  DIALOGUE                                                          │  │
│  │  ─────────────────────────────────────────────────────────────────│  │
│  │  Kent: "Aim for radical transformation"                           │  │
│  │  K-gent: "Not documentation. Membrane. Co-thinking surface."      │  │
│  │                                                                   │  │
│  │  [Input: What's next?]                          [Crystallize ⬡]  │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Three Surfaces, One Membrane

| Surface | What It Does | Foundation Primitive |
|---------|--------------|---------------------|
| **Focus** | Shows what you're working on — live file, spec, or concept | `elastic/` responsive |
| **Witness** | Real-time stream of decisions, fusions, crystallizations | `joy/Fizz` + streaming |
| **Dialogue** | Where Kent and K-gent think together | `joy/Hum` ambient |

---

## Elastic Modes (Membrane-Level)

| Mode | Layout | When |
|------|--------|------|
| `Compact` | Focus only, dialogue minimal | Deep work, reading code |
| `Comfortable` | Focus + Witness side-by-side | Normal interaction |
| `Spacious` | Full membrane with expanded dialogue | Active co-thinking |

---

## What Makes This Radical

1. **No Navigation Tree** — The membrane morphs; you don't navigate
2. **No Routes** — Context determines what's shown, not URL
3. **No Pages** — One surface, infinite configurations
4. **Dialogue-First** — Everything happens through conversation
5. **Witness as Memory** — Decisions stream, you see you're being heard

---

## Implementation Phases

### Phase 1: Membrane Foundation
- [ ] `Membrane.tsx` — The single root component
- [ ] `FocusPane.tsx` — Context-aware content display
- [ ] `WitnessStream.tsx` — Real-time decision/mark stream
- [ ] `DialoguePane.tsx` — Input + history
- [ ] `useMembrane.ts` — State machine for membrane modes

### Phase 2: Context Sensing
- [ ] `useWorkingContext.ts` — What file/spec/concept is active?
- [ ] `useFocusContent.ts` — Render appropriate content for context
- [ ] Wire to backend: `self.witness.stream`, `self.context.current`

### Phase 3: Crystallization
- [ ] Crystallize button → witness mark
- [ ] Decisions flow into stream
- [ ] Focus updates to reflect decisions

### Phase 4: Polish
- [ ] Elastic three-mode at membrane level
- [ ] Joy primitives: Fizz for stream, Hum for ambient
- [ ] Keyboard shortcuts for mode switching

---

## Preserved Foundation (From Burn)

- `elastic/` — Three-mode responsive patterns
- `joy/` — Shake, EmpathyError, PersonalityLoading, Fizz, Hum
- `genesis/` — Foundation components
- `useDesignPolynomial` — Temporal coherence
- `useAnimationCoordination` — Animation orchestration

---

## Backend Requirements

New AGENTESE nodes (or adapt existing):
- `self.witness.stream` — SSE stream of marks/decisions
- `self.context.current` — What's the current working context?
- `self.membrane.focus` — Set/get focus content

---

## Success Criteria

- [ ] One component renders the entire app
- [ ] No `react-router` navigation
- [ ] Dialogue is the primary interaction mode
- [ ] Witness stream shows decisions in real-time
- [ ] Feels like co-thinking, not browsing

---

*"The persona is a garden, not a museum."*
*"The proof IS the decision."*

Filed: 2025-12-22
Author: Kent + Claude (fusion)
