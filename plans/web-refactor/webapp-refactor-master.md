---
path: plans/web-refactor/webapp-refactor-master
status: active
progress: 10
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: [monetization/grand-initiative-monetization, reactive-substrate-unification]
session_notes: |
  Created from /hydrate session. Aligns with KENT's WISHES:
  - COMPOSITIONAL GENERATIVE UI
  - Create a shockingly delightful consumer, prosumer, and professional experience
  - Builder Workshop (chefs/gardeners/kids metaphors)
  2025-12-15: Phase 1 elastic foundation implemented (40% of elastic-primitives chunk).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: in_progress
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: in_progress
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.0
  returned: 0.0
---

# Web Application Refactor — Master Plan

> *"The noun is a lie. There is only the rate of change."*

## Vision Statement

Transform the Agent Town web frontend from a page-centric application to an **elastic, compositional UI** where agents chaotically modify the canvas yet **reasonably aesthetic pages always emerge**. The UI should feel like a garden that grows and adapts—never broken, always alive.

---

## Four Pillars

### 1. Elastic Context-Aware Primitives

> *If agents chaotically change things, a reasonably aesthetic page must always be generated.*

**Current State**: Widget-based rendering exists (`WidgetRenderer`, discriminated union types) but composition is manual.

**Target State**: Every UI element derives from elastic primitives that:
- Self-arrange when neighbors change
- Degrade gracefully when data is partial
- Animate transitions smoothly
- Respect a grid/flow system that guarantees aesthetics

**Key Insight**: The Projection Protocol already defines `to_cli()`, `to_marimo()`, `to_json()`—extend this to include **layout-aware projections** where the target includes viewport constraints.

### 2. Coherent Interaction Patterns

> *A base impulse is to move agents around and add them to build pipelines.*

**Current State**: Citizens are displayed on Mesa, but interaction is limited to click-to-select.

**Target State**:
- **Drag & Drop** agents into pipeline slots
- **Connect** agents with visible wires/edges
- **Pipeline Preview** showing data flow before execution
- **Historical Simulations** allow rewind/replay with read-only semantics
- **Live Mode** grants full interactivity

**Key Insight**: The Operad defines composition grammar. The UI should visualize this directly—operations become draggable nodes, composition rules become valid drop targets.

### 3. Better User Flows

> *Creating, chatting, viewing details, orchestrating—these must feel natural.*

**Four Core Flows**:

| Flow | Current | Target |
|------|---------|--------|
| **Create Agent** | API only | Visual agent builder with archetype palette |
| **Chat with Agent** | INHABIT mode | Seamless chat panel, always accessible |
| **View Details** | CitizenPanel sidebar | Expandable cards, drill-down modals |
| **Orchestrate** | Implicit via town phases | Visual pipeline canvas, drag-to-compose |

**Flow Design Principle**: Every flow should be completable in ≤3 clicks from any page.

### 4. Optimized Performance

**Targets**:
- **First Contentful Paint**: <1.5s
- **SSE Event Processing**: <10ms per event
- **Widget Render**: <16ms (60fps capable)
- **Bundle Size**: <300KB gzipped

**Strategies**:
- Virtualized lists for citizens >50
- Lazy load detail components
- Memoization of pure widget renders
- SSE message batching with debounce

---

## Sub-Plans (Chunks)

This plan decomposes into five focused chunks:

| Chunk | Focus | Dependencies |
|-------|-------|--------------|
| `elastic-primitives.md` | Grid system, auto-layout, graceful degradation | None |
| `interaction-patterns.md` | Drag-drop, pipelines, historical replay | elastic-primitives |
| `user-flows.md` | Agent creation, chat, details, orchestration | elastic-primitives, interaction-patterns |
| `performance.md` | Bundle splitting, virtualization, memoization | None (parallel) |
| `polish-and-delight.md` | Animations, transitions, micro-interactions | All above |

---

## Architectural Decisions

### AD-W01: Elastic Grid System

Use CSS Grid with named areas that adapt to content:

```css
.dashboard {
  display: grid;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  grid-template-columns: minmax(200px, 320px) 1fr;
  grid-template-rows: auto 1fr auto;
}

/* Empty sidebar? Main takes full width */
.dashboard:has(.sidebar:empty) {
  grid-template-columns: 1fr;
}
```

### AD-W02: Widget as Graph Node

Every widget exposes:
- `inputs: Port[]` — what it accepts
- `outputs: Port[]` — what it produces
- `render(context: LayoutContext): ReactNode` — projection

This enables the pipeline canvas to treat widgets uniformly.

### AD-W03: Projection-Aware Composition

Extend the `WidgetJSON` discriminated union with layout hints:

```typescript
interface WidgetJSON {
  type: string;
  // ... existing fields
  layout?: {
    flex?: number;      // flex-grow hint
    minWidth?: number;  // minimum viable width
    maxWidth?: number;  // maximum comfortable width
    priority?: number;  // render priority (for truncation)
  };
}
```

### AD-W04: Historical vs Live Mode

```typescript
type SimulationMode =
  | { type: 'live'; permissions: 'full' }
  | { type: 'historical'; tick: number; permissions: 'readonly' };
```

Historical mode:
- Scrubber to navigate time
- All interactions disabled except viewing
- Visual differentiation (sepia overlay? timeline UI)

---

## Connection to Existing Systems

### Widget Stack
- `src/reactive/types.ts` — extend with layout hints
- `src/reactive/WidgetRenderer.tsx` — add layout context
- `src/widgets/*` — audit for elasticity

### AGENTESE Integration
- Pipeline compositions map to AGENTESE paths
- `world.pipeline.manifest` → visual pipeline
- User-built pipelines → stored as AGENTESE compositions

### Town/Workshop Alignment
- Town uses `ColonyDashboardJSON`
- Workshop uses similar builder-centric structure
- Unified component library serves both

---

## Success Criteria

1. **Chaos Resilience Test**: Randomly hide/show 50% of widgets, page remains usable
2. **3-Click Flow Test**: All four core flows completable in ≤3 interactions
3. **Performance Budget**: All targets met on 3G throttled connection
4. **Visual Regression**: No broken layouts when backend sends partial data
5. **Joy Test**: 5 users describe the UI as "delightful" in user testing

---

## Implementation Order

```
Phase 1: Elastic Primitives (Week 1)
├── Grid system foundation
├── Widget layout hints
└── Graceful degradation patterns

Phase 2: Interaction Patterns (Week 2)
├── Drag-drop infrastructure
├── Pipeline canvas MVP
└── Historical mode

Phase 3: User Flows (Week 3)
├── Agent creation wizard
├── Chat panel integration
├── Details drill-down

Phase 4: Performance (Parallel)
├── Bundle analysis
├── Virtualization
└── Memoization audit

Phase 5: Polish (Week 4)
├── Transitions & animations
├── Loading states
└── Error boundaries with personality
```

---

## Open Questions

1. **Pipeline Persistence**: Store user-built pipelines server-side or client-side?
2. **Historical Data**: How far back do we store simulation history?
3. **Accessibility**: Screen reader strategy for drag-drop pipelines?
4. **Mobile**: Progressive enhancement or separate mobile experience?

---

*"The form that generates forms is itself a form."* — AD-006
