---
path: plans/web-refactor/elastic-primitives
status: active
progress: 40
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables: [web-refactor/interaction-patterns, web-refactor/user-flows]
parent: plans/web-refactor/webapp-refactor-master
session_notes: |
  Elastic primitives are the foundation. If agents can chaotically modify state,
  the UI must gracefully adapt. This is the Projection Protocol applied to layout.
  2025-12-15: Phase 1 foundation complete - CSS vars, ElasticContainer, ElasticCard,
  ElasticPlaceholder, ElasticSplit, WidgetLayoutHints, useLayoutContext hook.
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: in_progress
  STRATEGIZE: touched
  IMPLEMENT: in_progress
  QA: pending
  TEST: pending
entropy:
  planned: 0.08
  spent: 0.0
  returned: 0.0
---

# Elastic Primitives

> *"Developers design state, not rendering. Layout is a projection."*

## Problem Statement

Current widgets render without layout awareness. When an agent adds/removes citizens or changes state chaotically, the UI can:
- Leave awkward gaps
- Overflow containers
- Break responsive breakpoints
- Show jarring reflows

We need primitives that **self-arrange** within constraints.

---

## Design Goals

1. **Self-Arranging**: Widgets negotiate space with siblings
2. **Graceful Degradation**: Missing data → meaningful placeholder, not broken layout
3. **Responsive by Default**: Works from 320px mobile to 4K desktop
4. **Animatable**: State changes trigger smooth transitions
5. **Composable**: Primitives combine via `>>` (sequence) and `//` (parallel)

---

## Core Primitives

### 1. ElasticContainer

The fundamental building block. Replaces raw `div` wrappers.

```typescript
interface ElasticContainerProps {
  /** Layout strategy */
  layout: 'flow' | 'grid' | 'masonry' | 'stack';

  /** How to handle overflow */
  overflow: 'scroll' | 'wrap' | 'collapse' | 'truncate';

  /** Gap between children (CSS value or responsive object) */
  gap: string | { sm?: string; md?: string; lg?: string };

  /** Padding (CSS value or responsive object) */
  padding: string | { sm?: string; md?: string; lg?: string };

  /** What to show when empty */
  emptyState?: React.ReactNode;

  /** Animation config */
  transition?: 'none' | 'fast' | 'smooth' | 'spring';

  children: React.ReactNode;
}
```

**Behaviors**:
- `flow`: Children wrap naturally (like flexbox wrap)
- `grid`: CSS Grid with auto-fit columns
- `masonry`: Pinterest-style variable-height grid
- `stack`: Vertical or horizontal stack with uniform spacing

### 2. ElasticCard

Self-sizing card with priority hints.

```typescript
interface ElasticCardProps {
  /** Content priority (higher = survives truncation) */
  priority: number;

  /** Minimum content to show */
  minContent: 'icon' | 'title' | 'summary' | 'full';

  /** How card responds to tight space */
  shrinkBehavior: 'truncate' | 'collapse' | 'stack' | 'hide';

  /** Enable drag handle */
  draggable?: boolean;

  children: React.ReactNode;
}
```

**Behaviors**:
- In tight space, shows `minContent`
- When space allows, expands to `full`
- Animates between states

### 3. ElasticSplit

Two-pane layout that collapses gracefully.

```typescript
interface ElasticSplitProps {
  /** Split direction */
  direction: 'horizontal' | 'vertical';

  /** Initial split ratio (0-1) */
  defaultRatio: number;

  /** Below this width, stack instead of split */
  collapseAt: number;

  /** Which pane collapses first */
  collapsePriority: 'primary' | 'secondary';

  primary: React.ReactNode;
  secondary: React.ReactNode;
}
```

### 4. ElasticPlaceholder

Intelligent placeholder when data is missing/loading.

```typescript
interface ElasticPlaceholderProps {
  /** What's being loaded */
  for: 'agent' | 'metric' | 'chart' | 'list' | 'custom';

  /** Loading state */
  state: 'loading' | 'empty' | 'error';

  /** For error state */
  error?: string;

  /** Retry action */
  onRetry?: () => void;

  /** Match dimensions of expected content */
  expectedSize?: { width: string; height: string };
}
```

---

## Widget Layout Hints

Extend `WidgetJSON` with layout metadata:

```typescript
interface WidgetLayoutHints {
  /** Flex grow factor (how eagerly to take space) */
  flex?: number;

  /** Minimum width before collapsing */
  minWidth?: number;

  /** Maximum comfortable width */
  maxWidth?: number;

  /** Render priority (for truncation/hiding) */
  priority?: number;

  /** Preferred aspect ratio */
  aspectRatio?: number;

  /** Can this widget be hidden to save space? */
  collapsible?: boolean;

  /** Collapse threshold (viewport width) */
  collapseAt?: number;
}

// Extended widget types
interface CitizenCardJSON {
  type: 'citizen_card';
  // ... existing fields
  layout?: WidgetLayoutHints;
}
```

---

## Layout Context

Widgets receive layout context from parent containers:

```typescript
interface LayoutContext {
  /** Available width in pixels */
  availableWidth: number;

  /** Available height in pixels */
  availableHeight: number;

  /** Nesting depth (affects default sizing) */
  depth: number;

  /** Parent's layout strategy */
  parentLayout: 'flow' | 'grid' | 'masonry' | 'stack';

  /** Is the viewport constrained? */
  isConstrained: boolean;

  /** Preferred density */
  density: 'compact' | 'comfortable' | 'spacious';
}
```

---

## Graceful Degradation Matrix

| Scenario | Behavior |
|----------|----------|
| Widget data missing | ElasticPlaceholder with `state='empty'` |
| Widget data loading | ElasticPlaceholder with skeleton animation |
| Widget errors | ElasticPlaceholder with retry button |
| Too many widgets | Virtualization kicks in |
| Narrow viewport | Collapse to minContent |
| Very narrow viewport | Hide collapsible widgets |
| API timeout | Cached data with "stale" indicator |

---

## CSS Custom Properties

Global design tokens that widgets inherit:

```css
:root {
  /* Spacing scale */
  --elastic-gap-xs: 4px;
  --elastic-gap-sm: 8px;
  --elastic-gap-md: 16px;
  --elastic-gap-lg: 24px;
  --elastic-gap-xl: 32px;

  /* Transitions */
  --elastic-transition-fast: 150ms ease-out;
  --elastic-transition-smooth: 300ms ease-in-out;
  --elastic-transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);

  /* Breakpoints */
  --elastic-bp-sm: 640px;
  --elastic-bp-md: 768px;
  --elastic-bp-lg: 1024px;
  --elastic-bp-xl: 1280px;

  /* Z-indices */
  --elastic-z-base: 0;
  --elastic-z-sticky: 100;
  --elastic-z-dropdown: 200;
  --elastic-z-modal: 300;
  --elastic-z-toast: 400;
}
```

---

## Grid System

Named grid areas for common layouts:

```css
/* Town Layout */
.town-grid {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar mesa   details"
    "footer footer footer";
  grid-template-columns: minmax(0, 280px) 1fr minmax(0, 320px);
  grid-template-rows: auto 1fr auto;
  gap: var(--elastic-gap-md);
  height: 100%;
}

/* Collapse sidebar on medium screens */
@media (max-width: 1024px) {
  .town-grid {
    grid-template-areas:
      "header header"
      "mesa   details"
      "footer footer";
    grid-template-columns: 1fr minmax(0, 280px);
  }
}

/* Stack on small screens */
@media (max-width: 768px) {
  .town-grid {
    grid-template-areas:
      "header"
      "mesa"
      "details"
      "footer";
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto auto;
  }
}
```

---

## Implementation Tasks

### Phase 1: Foundation
- [x] Create `ElasticContainer` component → `src/components/elastic/ElasticContainer.tsx`
- [x] Create `ElasticCard` component → `src/components/elastic/ElasticCard.tsx`
- [x] Create `ElasticPlaceholder` component → `src/components/elastic/ElasticPlaceholder.tsx`
- [x] Create `ElasticSplit` component → `src/components/elastic/ElasticSplit.tsx`
- [x] Define CSS custom properties in `globals.css`
- [x] Create `useLayoutContext` hook → `src/hooks/useLayoutContext.ts`
- [x] Add `WidgetLayoutHints` to `reactive/types.ts`

### Phase 2: Widget Integration
- [ ] Add `layout` field to all WidgetJSON types
- [ ] Update `WidgetRenderer` to pass LayoutContext
- [ ] Migrate `CitizenCard` to use elastic primitives
- [ ] Migrate `ColonyDashboard` to use elastic grid

### Phase 3: Page Layouts
- [ ] Refactor `Town.tsx` to use elastic grid
- [ ] Refactor `Workshop.tsx` to use elastic grid
- [ ] Refactor `Inhabit.tsx` to use elastic primitives
- [ ] Add responsive collapse behaviors

### Phase 4: Testing
- [ ] Visual regression tests for breakpoints
- [ ] Chaos test: random widget show/hide
- [ ] Performance test: 100 widgets rendering

---

## Success Metrics

1. **No Layout Breaks**: Zero visual regressions when widgets change
2. **Responsive Coverage**: Works on 320px-2560px viewports
3. **Transition Smoothness**: All layout changes animate
4. **Placeholder Coverage**: 100% of loading states have placeholders

---

## Connection to Projection Protocol

The elastic primitives ARE the web projection layer:

```typescript
// Python backend
widget.to_json()  // → WidgetJSON with layout hints

// React frontend
<WidgetRenderer
  widget={json}
  context={layoutContext}  // ← NEW: layout awareness
/>
```

The `LayoutContext` is the web-specific projection target, analogous to:
- CLI: terminal width/height
- marimo: notebook cell constraints
- JSON: none (lossless)

---

*"The projection is not the territory. But a good projection makes the territory navigable."*
