# Frontend Design Audit: Index

> *"The fundamental thing to avoid is the suppression and atrophy of human creativity."*
> *"There is no such thing as shipping. Only continuous iteration and evolution."*

**Status:** Living Index
**Updated:** 2026-01-17

---

## Canonical Documents

| Document | Purpose | Status |
|----------|---------|--------|
| **`10-evergreen-vision.md`** | THE VISION — Axiom-grounded transformative design | CANONICAL |
| **`05-severe-stark-spec.md`** | Aesthetic specification (SEVERE STARK) | CANONICAL |
| **`06-kent-feedback.md`** | Kent's voice anchors and design decisions | REFERENCE |
| **`13-kent-design-decisions.md`** | **Kent's 15 definitive design decisions** | **CANONICAL** |

### Execution Documents

| Document | Purpose | Status |
|----------|---------|--------|
| **`11-execution-plan.md`** | Phase-by-phase implementation plan | ACTIVE |
| **`12-backend-integration-plan.md`** | Backend API integration | ACTIVE |

---

## The Evergreen Vision Summary

The kgents frontend is an **anti-sloppification machine** grounded in 8 discovered axioms:

### Foundational Axioms

| ID | Axiom | Frontend Implication |
|----|-------|---------------------|
| A0 | Ethical floor | No dark patterns, errors guide |
| A1 | Creativity preservation | Amplify, never replace |
| A2 | Sloppification visibility | AI-touch always visible |
| A3 | Evolutionary epistemology | Everything falsifiable |
| A4 | No-shipping | Garden, not product |
| A5 | Delusion/creativity boundary | Show evidence, not claims |
| A6 | Authority with Kent | UI presents, never persuades |
| A7 | Disgust prevention | Always show state, support deletion |
| A8 | Understandability priority | Simple elements that compose |

### Three Containers

```
HUMAN CONTAINER     — Full intensity, no AI mediation
COLLABORATION       — Dialectic visible, fusion tracked
AI CONTAINER        — Low intensity, requires review
```

### Collapsing Functions

```
TypeScript    → Binary (compiles?)
Tests         → Binary (passes?)
Constitution  → Score (0-7)
Galois        → Loss (0-1)
```

### Garden Lifecycle

```
SEED → SPROUT → BLOOM → WITHER → COMPOST
idea   draft   mature  deprecated  deleted
```

---

## Kent's 15 Decisions (Summary)

See **`13-kent-design-decisions.md`** for full details.

| # | Category | Decision |
|---|----------|----------|
| 1 | Mobile | **Adapt for touch** — 44px min targets |
| 2 | Glow | **Milestones only** — commit, crystal, resolve |
| 3 | Motion | **Slow earned, fast default** |
| 4 | Nav | **Bottom tab bar** (iOS-style) |
| 5 | Onboarding | **External docs only** |
| 6 | Keys | **Single-letter** — m/w/t/f/d/s |
| 7 | K-Block | **Reference, not contain** (graph) |
| 8 | Entangle | **Spec dependencies** |
| 9 | Persist | **Event sourced** (HEAD-FIRST) |
| 10 | Users | **Everyone is architect** |
| 11 | Jewels | **Ship all 6** |
| 12 | ASHC | **Gutter annotations** |
| 13 | Query | **Fuzzy search only** (fzf-style) |
| 14 | Layout | **CSS constraint system** |
| 15 | A11y | **Strict WCAG AA** (4.5:1) |

---

## Implementation Status (Phase 0 Complete)

### ✅ Completed Today (2026-01-17)

1. **Accessibility** — Fixed all contrast ratios in `tokens.css`
2. **Event Sourcing** — Implemented HEAD-FIRST design in `services/k_block/core/events.py`
3. **CSS Constraints** — Created `src/styles/layout-constraints.css`

### ⏳ Phase 1 (Next)

1. WorkspacePage with 5-panel grid
2. Navigation (AGENTESE paths, fuzzy search)
3. K-Block list (graph visualization)
4. Editor (markdown, gutter annotations)
5. Metadata panel (edges, constitutional)
6. Status line (mode, path, density)

---

## Deleted Documents (Historical)

These documents were deleted as obsolete or superseded:

| Document | Reason |
|----------|--------|
| 01-component-taxonomy.md | Referenced deleted components |
| 02-consolidation-plan.md | Superseded by radical deletion |
| 03-design-questions.md | Questions answered in 13-kent-design-decisions.md |
| 04-multi-stage-plan.md | Obsolete timeline |
| 07-radical-deletion.md | Executed, historical only |
| 08-protocol-integration.md | Absorbed into 10-evergreen-vision |
| 09-metaphysical-container.md | Superseded by 10-evergreen-vision |

Git history preserves all.

---

## Current State

The frontend was radically deleted (581→13 files) and Phase 0 is complete.

```
src/
├── main.tsx                     # Entry
├── App.tsx                      # Shell (imports CSS)
├── router/
│   ├── AgenteseRouter.tsx       # Routes
│   └── AgentesePath.ts          # Path parsing
├── pages/
│   └── WorkspacePage.tsx        # THE page
├── components/
│   └── error/
│       └── ErrorBoundary.tsx
├── hooks/
│   └── useLayoutContext.ts      # Density hook
├── styles/
│   ├── globals.css              # Base styles
│   ├── severe-base.css          # SEVERE STARK reset
│   └── layout-constraints.css   # ✅ NEW: CSS constraint system
└── design/
    ├── tokens.css               # ✅ FIXED: WCAG AA compliant
    └── severe-tokens.css        # SEVERE STARK tokens
```

---

## Next Session

Continue with Phase 1:
1. Implement WorkspacePage with `workspace-grid` class
2. Build Navigation component with fuzzy search
3. Create K-Block list as graph visualization
4. Wire up keyboard shortcuts (m/w/t/f/d/s)

---

*"The persona is a garden, not a museum."*
