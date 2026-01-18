# Frontend Evergreen Execution Plan

> *"The fundamental thing to avoid is the suppression and atrophy of human creativity."*
> *"There is no shipping. Only evolution."*

**Status:** Active Execution
**Created:** 2026-01-17
**Grounded In:** 10-evergreen-vision.md, 05-severe-stark-spec.md, 06-kent-feedback.md

---

## Executive Summary

This plan transforms the kgents frontend from a minimal skeleton (5 files, post-88% deletion) into an **anti-sloppification machine** grounded in 8 discovered axioms. The result is not a product but a **practice** — a garden that grows with every session.

### Current State (Post-Deletion)

```
src/
├── main.tsx                 # Entry (14 lines)
├── App.tsx                  # Shell (19 lines)
├── router/
│   └── AgenteseRouter.tsx   # Routes (66 lines)
├── pages/
│   └── WorkspacePage.tsx    # THE page (68 lines — TODO skeleton)
├── components/error/
│   └── ErrorBoundary.tsx    # Error handling
├── hooks/
│   └── useLayoutContext.ts  # Density hook (161 lines)
├── styles/
│   └── globals.css          # Tailwind + legacy tokens (1124 lines)
└── design/
    └── tokens.css           # Design tokens (495 lines)
```

### Target State

A fully-realized **Evergreen Workspace** with:
1. **SEVERE STARK aesthetic** — Yahoo Japan density, earned glow only
2. **Three Containers** — Human/Collaboration/AI with visible provenance
3. **Collapsing Functions** — TypeScript, Tests, Constitution, Galois visible
4. **Garden Lifecycle** — SEED → SPROUT → BLOOM → WITHER → COMPOST
5. **Anti-Sloppification** — Every AI touch visible, every decision witnessed

---

## Phase 1: Foundation — SEVERE STARK Design System

**Duration:** 2 hours
**Agent:** Implementation (opus)

### 1.1 Create Severe Tokens

Replace bloated tokens.css with SEVERE STARK spec:

```css
/* src/design/severe-tokens.css */

:root {
  /* Typography — WCAG AA Dense */
  --text-xs: 10px;   /* Timestamps, metadata */
  --text-sm: 11px;   /* Secondary labels */
  --text-base: 12px; /* Body text, DEFAULT */
  --text-md: 13px;   /* Important body */
  --text-lg: 14px;   /* Section headers */
  --text-xl: 15px;   /* Page titles */

  --leading-tight: 1.2;  /* Body text, DEFAULT */
  --leading-snug: 1.3;   /* Multi-paragraph */

  /* Spacing — 50% Reduction */
  --gap-1: 2px;   /* Micro */
  --gap-2: 4px;   /* Default */
  --gap-3: 6px;   /* Between groups */
  --gap-4: 8px;   /* Section */
  --gap-5: 12px;  /* Major sections */
  --gap-6: 16px;  /* Page-level only */

  /* Backgrounds — Steel Scale */
  --bg-void: #0a0a0c;
  --bg-surface: #0f0f12;
  --bg-elevated: #141418;
  --bg-highlight: #1c1c22;

  /* Foregrounds — Gray Scale */
  --fg-muted: #3a3a44;
  --fg-secondary: #5a5a64;
  --fg-primary: #8a8a94;
  --fg-strong: #b0b0b8;
  --fg-intense: #e0e0e8;

  /* Borders */
  --border-subtle: #1c1c22;
  --border-default: #28282f;
  --border-strong: #3a3a44;

  /* Earned Glow (ONLY for significant moments) */
  --glow-earned: #c4a77d;
  --glow-bright: #d4b88c;

  /* Semantic */
  --error: #8b4a4a;
  --warning: #8b6b4a;
  --success: #4a6b4a;

  /* Motion — Almost None */
  --transition-instant: 0ms;
  --transition-micro: 50ms linear;

  /* Fonts */
  --font-data: 'JetBrains Mono', 'SF Mono', monospace;
  --font-prose: 'Inter', -apple-system, sans-serif;
}
```

### 1.2 Create Base CSS Reset

```css
/* src/styles/severe-base.css */

/* Kill all animations except permitted */
*, *::before, *::after {
  transition: none !important;
  animation: none !important;
}

/* Permitted: panel open/close */
.panel-transition {
  transition: transform 50ms linear !important;
}

/* Earned glow animation */
@keyframes glow-fade {
  0% { text-shadow: 0 0 12px var(--glow-earned); }
  100% { text-shadow: none; }
}

.glow-moment {
  animation: glow-fade 2s ease-out forwards !important;
}

/* Typography defaults */
body {
  font-family: var(--font-prose);
  font-size: var(--text-base);
  line-height: var(--leading-tight);
  background: var(--bg-void);
  color: var(--fg-primary);
}

/* Data contexts — monospace */
code, pre, .kblock, .path, .id, .number {
  font-family: var(--font-data);
}

/* Links — no color change on hover */
a {
  color: inherit;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}

/* Selection — inverse video */
::selection {
  background: var(--fg-primary);
  color: var(--bg-void);
}

/* Focus — thin, visible */
:focus-visible {
  outline: 1px solid var(--fg-intense);
  outline-offset: 1px;
}
```

### 1.3 Deliverables

- [ ] `src/design/severe-tokens.css` — New token system
- [ ] `src/styles/severe-base.css` — Base reset
- [ ] Update `globals.css` to import severe tokens
- [ ] Remove deprecated elastic-* tokens
- [ ] Remove all breathing/spring animations

---

## Phase 2: Core Infrastructure — TypeScript Types

**Duration:** 1.5 hours
**Agent:** Implementation (opus)

### 2.1 Provenance System Types

```typescript
// src/types/provenance.ts

export type Author = 'kent' | 'claude' | 'fusion';

export interface Provenance {
  author: Author;
  confidence: number;        // 0-1
  reviewed: boolean;         // Has human reviewed AI content?
  sloppification_risk: number; // 0-1
  evidence: string[];        // Why do we believe this assessment?
  created_at: string;        // ISO timestamp
  reviewed_at?: string;      // When was it reviewed?
}

export interface ProvenanceRange {
  start: number;  // Line start
  end: number;    // Line end
  provenance: Provenance;
}

// Visual encoding
export const PROVENANCE_INTENSITY: Record<Author, string> = {
  kent: 'var(--fg-intense)',     // Full intensity
  fusion: 'var(--fg-intense)',   // Full intensity + marker
  claude: 'var(--fg-secondary)', // Low intensity
};

export const PROVENANCE_INDICATORS: Record<string, string> = {
  fusion: '⚡',      // Fusion mark
  reviewed: '◇',    // Reviewed AI
  unreviewed: '◆',  // Needs review (amber border)
};
```

### 2.2 Garden Lifecycle Types

```typescript
// src/types/lifecycle.ts

export type LifecycleStage = 'seed' | 'sprout' | 'bloom' | 'wither' | 'compost';

export interface LifecycleState {
  stage: LifecycleStage;
  planted: string;         // ISO timestamp
  lastTended: string;      // ISO timestamp
  health: number;          // 0-1
  dependents: string[];    // What relies on this?
  daysSinceActivity: number;
}

export const LIFECYCLE_COLORS: Record<LifecycleStage, string> = {
  seed: '#3a5a7a',     // Blue-gray (potential)
  sprout: '#5a7a5a',   // Green-gray (growing)
  bloom: 'var(--fg-intense)', // Full intensity
  wither: 'var(--fg-secondary)', // Fading
  compost: 'var(--fg-muted)',    // Nearly gone
};

export const LIFECYCLE_ICONS: Record<LifecycleStage, string> = {
  seed: '●',
  sprout: '╱│╲',
  bloom: '✿',
  wither: '╱',
  compost: '░',
};
```

### 2.3 Collapsing Functions Types

```typescript
// src/types/collapse.ts

export type CollapseStatus = 'pass' | 'partial' | 'fail' | 'pending';

export interface CollapseResult {
  status: CollapseStatus;
  score?: number;        // For partial results (e.g., 16/20 tests)
  total?: number;
  message?: string;
  timestamp: string;
}

export interface CollapseState {
  typescript: CollapseResult;
  tests: CollapseResult;
  constitution: {
    score: number;       // 0-7
    principles: Record<string, number>; // Per-principle scores
  };
  galois: {
    loss: number;        // 0-1
    tier: 'CATEGORICAL' | 'EMPIRICAL' | 'AESTHETIC' | 'SOMATIC' | 'CHAOTIC';
  };
  overallSlop: 'low' | 'medium' | 'high';
}

export const COLLAPSE_COLORS: Record<CollapseStatus, string> = {
  pass: 'var(--success)',
  partial: 'var(--warning)',
  fail: 'var(--error)',
  pending: 'var(--fg-muted)',
};
```

### 2.4 Three Containers Types

```typescript
// src/types/containers.ts

export type ContainerType = 'human' | 'collaboration' | 'ai';

export interface ContainerContext {
  type: ContainerType;
  authority: 'full' | 'shared' | 'delegated';
  sloppificationVisible: boolean;
  requiresReview: boolean;
}

export const CONTAINER_DESCRIPTIONS: Record<ContainerType, string> = {
  human: 'Full authority, no AI mediation',
  collaboration: 'Dialectic visible, fusion tracked',
  ai: 'Low intensity, requires review',
};
```

### 2.5 Deliverables

- [ ] `src/types/provenance.ts`
- [ ] `src/types/lifecycle.ts`
- [ ] `src/types/collapse.ts`
- [ ] `src/types/containers.ts`
- [ ] `src/types/index.ts` — Re-exports

---

## Phase 3: Provenance System Components

**Duration:** 3 hours
**Agent:** Implementation (opus)

### 3.1 ProvenanceIndicator Component

```typescript
// src/components/provenance/ProvenanceIndicator.tsx

interface ProvenanceIndicatorProps {
  provenance: Provenance;
  inline?: boolean;  // For per-line indicators
}

// Shows: author badge, review status, slop risk
```

### 3.2 ProvenanceLine Component

```typescript
// src/components/provenance/ProvenanceLine.tsx

interface ProvenanceLineProps {
  content: string;
  provenance: Provenance;
  lineNumber: number;
}

// Renders a single line with provenance gutter
```

### 3.3 ProvenanceBlock Component

```typescript
// src/components/provenance/ProvenanceBlock.tsx

interface ProvenanceBlockProps {
  content: string;
  provenanceMap: Map<Range, Provenance>;
}

// Renders content with per-line provenance
```

### 3.4 useProvenance Hook

```typescript
// src/hooks/useProvenance.ts

// Fetches/manages provenance data for a K-Block
// Integrates with backend provenance API
```

### 3.5 Deliverables

- [ ] `src/components/provenance/ProvenanceIndicator.tsx`
- [ ] `src/components/provenance/ProvenanceLine.tsx`
- [ ] `src/components/provenance/ProvenanceBlock.tsx`
- [ ] `src/components/provenance/index.ts`
- [ ] `src/hooks/useProvenance.ts`

---

## Phase 4: Collapsing Functions Panel

**Duration:** 2.5 hours
**Agent:** Implementation (opus)

### 4.1 CollapseBar Component

```typescript
// src/components/collapse/CollapseBar.tsx

interface CollapseBarProps {
  label: string;
  status: CollapseStatus;
  progress?: number;  // 0-1 for partial
  detail?: string;
}

// Horizontal bar showing pass/fail/partial
```

### 4.2 CollapsePanel Component

```typescript
// src/components/collapse/CollapsePanel.tsx

interface CollapsePanelProps {
  state: CollapseState;
  provenance: Provenance;
  witness: WitnessSummary;
}

// Full panel with all four collapsing functions
// Plus sloppification assessment and witness summary
```

### 4.3 GaloisIndicator Component

```typescript
// src/components/collapse/GaloisIndicator.tsx

interface GaloisIndicatorProps {
  loss: number;
  tier: string;
}

// Specialized display for Galois loss
// Shows tier badge and loss value
```

### 4.4 Deliverables

- [ ] `src/components/collapse/CollapseBar.tsx`
- [ ] `src/components/collapse/CollapsePanel.tsx`
- [ ] `src/components/collapse/GaloisIndicator.tsx`
- [ ] `src/components/collapse/index.ts`
- [ ] `src/hooks/useCollapse.ts`

---

## Phase 5: Garden Lifecycle System

**Duration:** 2.5 hours
**Agent:** Implementation (opus)

### 5.1 GardenSummary Component

```typescript
// src/components/garden/GardenSummary.tsx

interface GardenSummaryProps {
  state: GardenState;
  onSelect?: (item: GardenItem) => void;
}

// Shows: Seeds: 12 | Sprouts: 8 | Blooms: 47 | Withering: 3 | Health: 0.82
```

### 5.2 GardenItem Component

```typescript
// src/components/garden/GardenItem.tsx

interface GardenItemProps {
  item: GardenItem;
  onAction?: (action: 'tend' | 'compost') => void;
}

// Individual item with lifecycle badge
```

### 5.3 AttentionNeeded Component

```typescript
// src/components/garden/AttentionNeeded.tsx

interface AttentionNeededProps {
  items: GardenItem[];
  maxItems?: number;
}

// Prioritized list of items needing attention
// Sorted by: wither > sprout > seed
```

### 5.4 useGarden Hook

```typescript
// src/hooks/useGarden.ts

interface GardenState {
  seeds: number;
  sprouts: number;
  blooms: number;
  withering: number;
  composted_today: number;
  health: number;
  attention: GardenItem[];
}

// Fetches garden state from backend
// Updates on file changes
```

### 5.5 Deliverables

- [ ] `src/components/garden/GardenSummary.tsx`
- [ ] `src/components/garden/GardenItem.tsx`
- [ ] `src/components/garden/AttentionNeeded.tsx`
- [ ] `src/components/garden/index.ts`
- [ ] `src/hooks/useGarden.ts`
- [ ] `src/types/garden.ts`

---

## Phase 6: Three Containers Architecture

**Duration:** 2 hours
**Agent:** Implementation (opus)

### 6.1 ContainerProvider Component

```typescript
// src/components/containers/ContainerProvider.tsx

interface ContainerProviderProps {
  type: ContainerType;
  children: React.ReactNode;
}

// Context provider for container type
// Applies appropriate styling/restrictions
```

### 6.2 HumanContainer Component

```typescript
// src/components/containers/HumanContainer.tsx

// Full intensity, no AI mediation
// Direct manipulation only
```

### 6.3 CollaborationContainer Component

```typescript
// src/components/containers/CollaborationContainer.tsx

// Dialectic visible
// Sloppification indicators
// Witness marks mandatory
```

### 6.4 AIContainer Component

```typescript
// src/components/containers/AIContainer.tsx

// Low intensity rendering
// Prominent "AI generated" indicator
// Requires review before elevation
// Amber border until reviewed
```

### 6.5 Deliverables

- [ ] `src/components/containers/ContainerProvider.tsx`
- [ ] `src/components/containers/HumanContainer.tsx`
- [ ] `src/components/containers/CollaborationContainer.tsx`
- [ ] `src/components/containers/AIContainer.tsx`
- [ ] `src/components/containers/index.ts`
- [ ] `src/context/ContainerContext.tsx`

---

## Phase 7: Unified Workspace Layout

**Duration:** 4 hours
**Agent:** Implementation (opus)

### 7.1 WorkspaceHeader Component

```typescript
// src/components/workspace/WorkspaceHeader.tsx

// Dense navigation: [world] [self] [concept] [void] [time]
// Status: KENT | density:max | garden:healthy
// 50+ links visible (Yahoo Japan density)
```

### 7.2 NavigationPanel Component

```typescript
// src/components/workspace/NavigationPanel.tsx

// 15% width
// Garden state tree
// Current path
// Aspect shortcuts
```

### 7.3 KBlockPanel Component

```typescript
// src/components/workspace/KBlockPanel.tsx

// 60% width (main editor)
// Provenance gutter
// Lifecycle badge
// Container awareness
```

### 7.4 MetadataPanel Component

```typescript
// src/components/workspace/MetadataPanel.tsx

// 25% width
// Collapse panel
// Provenance summary
// Witness summary
```

### 7.5 StatusLine Component

```typescript
// src/components/workspace/StatusLine.tsx

// Fixed bottom
// MODE | path | line | slop | garden | EVERGREEN
```

### 7.6 Rebuild WorkspacePage

```typescript
// src/pages/WorkspacePage.tsx

// Assemble all components
// 5-column dense grid
// All axioms embodied
```

### 7.7 Deliverables

- [ ] `src/components/workspace/WorkspaceHeader.tsx`
- [ ] `src/components/workspace/NavigationPanel.tsx`
- [ ] `src/components/workspace/KBlockPanel.tsx`
- [ ] `src/components/workspace/MetadataPanel.tsx`
- [ ] `src/components/workspace/StatusLine.tsx`
- [ ] `src/components/workspace/index.ts`
- [ ] Update `src/pages/WorkspacePage.tsx`

---

## Phase 8: Integration & Polish

**Duration:** 2 hours
**Agent:** Implementation (opus)

### 8.1 Backend Integration

- [ ] Wire useProvenance to provenance API
- [ ] Wire useGarden to garden state API
- [ ] Wire useCollapse to collapse functions API
- [ ] Add SSE for real-time updates

### 8.2 Accessibility Audit

- [ ] Verify WCAG AA compliance (12px minimum)
- [ ] Test keyboard navigation
- [ ] Test screen reader announcements
- [ ] Verify focus indicators

### 8.3 Performance Validation

- [ ] Bundle size audit (<100KB JS)
- [ ] First paint <1s
- [ ] No layout shifts
- [ ] 60fps scroll

### 8.4 Final Checklist

- [ ] All TODO comments resolved
- [ ] TypeScript strict mode passes
- [ ] No ESLint warnings
- [ ] Storybook stories for all components
- [ ] E2E tests for critical paths

---

## Execution Schedule

| Phase | Duration | Dependencies | Parallel? |
|-------|----------|--------------|-----------|
| 1. Design System | 2h | None | No |
| 2. TypeScript Types | 1.5h | Phase 1 | No |
| 3. Provenance | 3h | Phase 2 | Yes |
| 4. Collapse Panel | 2.5h | Phase 2 | Yes |
| 5. Garden Lifecycle | 2.5h | Phase 2 | Yes |
| 6. Three Containers | 2h | Phase 3 | No |
| 7. Workspace Layout | 4h | Phases 3-6 | No |
| 8. Integration | 2h | Phase 7 | No |

**Total:** ~19.5 hours (can parallelize phases 3-5)

**Parallel Execution:** Phases 3, 4, 5 can run simultaneously after Phase 2.

---

## Success Criteria

### Axiom Validation

| Axiom | Validation |
|-------|------------|
| A0 (Ethical) | No dark patterns, errors guide |
| A1 (Creativity) | Kent rates creative amplification ≥ 7/10 |
| A2 (Sloppification) | AI-touch visually distinct in all contexts |
| A3 (Evolution) | All elements deletable, derivation visible |
| A4 (No-Shipping) | No "complete" labels, garden metaphor pervasive |
| A5 (Delusion) | Evidence shown, not claims |
| A6 (Authority) | No "recommended" badges, options presented equally |
| A7 (Disgust) | State always visible, "where am I?" answered |
| A8 (Understandability) | Each component ≤50 lines, composable |

### Technical Validation

- [ ] TypeScript strict mode: 0 errors
- [ ] ESLint: 0 warnings
- [ ] Bundle size: <100KB
- [ ] First paint: <1s
- [ ] Accessibility: WCAG AA

### Kent's Mirror Test

> "Does K-gent feel like me on my best day?"

Target: ≥ 7/10

---

## Notes

### Voice Anchors (Preserve These)

- "Daring, bold, creative, opinionated but not gaudy"
- "Tasteful > feature-complete"
- "The persona is a garden, not a museum"
- "Depth over breadth"

### Anti-Patterns (Avoid These)

- Animations beyond cursor blink and scroll
- Hover shadows or transforms
- "Recommended" badges from AI
- Progressive disclosure (show everything)
- Decorative whitespace
- Colors beyond monochrome + earned glow

---

*"This is not software. It is a garden."*
