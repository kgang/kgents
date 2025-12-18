# Elastic UI Patterns

> *"Density is not screen size. Density is the capacity to receive."*

## When to Use

- Building responsive React pages with multi-pane layouts
- Widgets that must adapt to available space (card content degradation)
- Touch-friendly mobile experiences with drawer patterns
- Pages that need consistent behavior from 320px to 4K

**Spec Reference**: See `spec/protocols/projection.md` for categorical theory (AD-008 Density-Content Isomorphism).

---

## The Three-Mode Pattern

| Mode | Breakpoint | Characteristics |
|------|------------|-----------------|
| **Compact** | <768px (mobile) | Drawer-based, touch-friendly, minimal chrome |
| **Comfortable** | 768-1023px (tablet) | Hybrid, collapsible panels, balanced |
| **Spacious** | ≥1024px (desktop) | Full panels, draggable dividers, maximum info |

> **Canonical Source**: `spec/protocols/projection.md` defines these breakpoints. Both Python (`agents/design/types.py`) and TypeScript (`useDesignPolynomial.ts`) must align.

```tsx
import { useWindowLayout } from '@/hooks/useLayoutContext';

const { density, isMobile, isTablet, isDesktop } = useWindowLayout();
// density: 'compact' | 'comfortable' | 'spacious'
```

---

## Density-Aware Constants

**GOOD: Parameterized by density**
```tsx
const NODE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 } as const;
const size = NODE_SIZE[density];  // Morphism: Density → Value
```

**BAD: Scattered conditionals**
```tsx
const nodeSize = isMobile ? 0.2 : isTablet ? 0.25 : 0.3;
```

---

## Component Primitives

| Primitive | Use Case | Density Behavior |
|-----------|----------|------------------|
| `ElasticSplit` | Two-pane layouts | Collapse below threshold |
| `ElasticContainer` | Self-arranging grids | Auto-fit columns |
| `BottomDrawer` | Mobile panels | Slides from bottom |
| `FloatingActions` | Mobile FABs | Touch-friendly cluster |
| `FloatingSidebar` | Overlay navigation | Float over content |
| `FixedBottomPanel` | Terminals/REPL | Fixed at bottom |
| `FixedTopPanel` | Status bars | Fixed at top |

### ElasticSplit

```tsx
<ElasticSplit
  defaultRatio={0.75}
  collapseAt={768}
  collapsePriority="secondary"
  resizable={isDesktop}
  primary={<MainCanvas />}
  secondary={<SidePanel />}
/>
```

### BottomDrawer

```tsx
<BottomDrawer isOpen={isOpen} onClose={onClose} title="Controls">
  <ControlPanel density={density} isDrawer />
</BottomDrawer>
```

### FloatingActions

```tsx
<div className="absolute bottom-4 right-4 flex flex-col gap-2">
  <button className="w-12 h-12 bg-green-600 rounded-full">🔄</button>
</div>
```

---

## Content Degradation

Cards adapt based on container width:

| Level | Width | Displays |
|-------|-------|----------|
| `icon` | <60px | Icon only |
| `title` | <150px | Icon + name |
| `summary` | <280px | Icon + name + phase |
| `full` | ≥400px | Full content |

```tsx
function getContentLevel(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}
```

**Design System Types**: See `agents/design/types.py` for `ContentLevel` enum.

---

## Mobile Layout Pattern

```tsx
function MyPage() {
  const { isMobile, density } = useWindowLayout();

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col">
        <header className="flex-shrink-0 px-3 py-2">
          <CompactHeader />
        </header>
        <div className="flex-1 relative">
          <Canvas density={density} />
          <FloatingActions onToggle={handleToggle} />
        </div>
        <BottomDrawer isOpen={panelOpen} onClose={closePanel}>
          <ControlPanel density={density} isDrawer />
        </BottomDrawer>
      </div>
    );
  }

  return (
    <ElasticSplit
      resizable={isDesktop}
      primary={<Canvas density={density} />}
      secondary={<ControlPanel density={density} />}
    />
  );
}
```

---

## CSS Custom Properties

```css
:root {
  --elastic-gap-xs: 4px;
  --elastic-gap-sm: 8px;
  --elastic-gap-md: 16px;
  --elastic-gap-lg: 24px;
  --elastic-transition-smooth: 300ms ease-in-out;
  --elastic-bp-sm: 640px;
  --elastic-bp-md: 768px;
  --elastic-bp-lg: 1024px;
}
```

---

## Floating Overlay Pattern

Navigation panels work better as **floating overlays** than document-flow elements.

**Decision**: Overlay wins because:
1. Full content width when panels closed
2. Smoother animation (transform vs reflow)
3. Users rarely need nav and content simultaneously

```tsx
<FloatingSidebar
  isExpanded={navExpanded}
  onToggle={() => setNavExpanded(!navExpanded)}
  bottomOffset={terminalExpanded ? '200px' : '48px'}
>
  <NavTree />
</FloatingSidebar>
```

### Fixed Panel Coordination (Sheaf Condition)

Multiple fixed panels must coordinate via shared context:

```
observer.bottom = nav.top        // Nav respects observer drawer
terminal.top = nav.bottom        // Nav respects terminal
main.paddingTop = observer.height
main.paddingBottom = terminal.height
```

```tsx
import { TOP_PANEL_HEIGHTS, BOTTOM_PANEL_HEIGHTS } from '@/components/elastic';

const getTopOffset = () =>
  observerExpanded ? `${TOP_PANEL_HEIGHTS.expanded}px` : `${TOP_PANEL_HEIGHTS.collapsed}px`;
```

---

## Anti-Patterns

### Scattered Conditionals
```tsx
// BAD
{isMobile ? <CompactThing /> : <FullThing />}

// GOOD
<Thing density={density} />
```

### Mode-Specific Components
```tsx
// BAD
<MobileControlPanel />
<DesktopControlPanel />

// GOOD
<ControlPanel density={density} isDrawer={isMobile} />
```

### Ignoring Touch Targets
```tsx
// BAD: 24px buttons on mobile
<button className="p-1">×</button>

// GOOD: 48px minimum
<button className="w-12 h-12">×</button>
```

---

## Refactoring Checklist

- [ ] Uses `useWindowLayout()`?
- [ ] Passes `density` to child components?
- [ ] Has dedicated mobile layout?
- [ ] Uses `ElasticSplit` for two-pane?
- [ ] Uses `BottomDrawer` for mobile panels?
- [ ] Uses `FloatingActions` for mobile?
- [ ] Touch targets ≥48px?
- [ ] Has density-parameterized constants?

Test widths: 375px, 768px, 1024px, 1440px

---

## AGENTESE Gateway Integration

The design system is a **full vertical slice** from polynomial state machine to AGENTESE gateway to React projection.

### Backend Layers

```
agents/design/types.py      → Types (Density, ContentLevel, MotionType)
agents/design/polynomial.py → DESIGN_POLYNOMIAL (144 states: 3×4×6×2)
agents/design/operad.py     → LAYOUT_OPERAD, CONTENT_OPERAD, MOTION_OPERAD, DESIGN_OPERAD
agents/design/sheaf.py      → DesignSheaf (temporal coherence)
protocols/agentese/contexts/design.py → @node("concept.design.*")
```

### AGENTESE Paths

| Path | Purpose |
|------|---------|
| `concept.design.manifest` | Design system overview |
| `concept.design.layout.manifest` | Layout operad state |
| `concept.design.layout.verify` | Verify layout laws |
| `concept.design.content.manifest` | Content operad state |
| `concept.design.motion.manifest` | Motion operad state |
| `concept.design.operad.verify` | Verify all design laws |

### useDesignGateway Hook

Bridges local state (responsive) with gateway data (authoritative):

```tsx
import { useDesignGateway } from '@/hooks';

function MyComponent() {
  const {
    // Local state (instant, viewport-responsive)
    localState,      // { density, contentLevel, motion, shouldAnimate }
    send,            // State machine input

    // Gateway data (fetched from AGENTESE)
    layoutOperad,    // { name, operations, lawCount }
    verification,    // { all_passed, results[] }

    // Actions
    verifyLaws,      // () => Promise<OperadVerifyResponse>
    refreshOperads,  // () => Promise<void>
  } = useDesignGateway({ autoFetch: true });

  return (
    <div>
      <p>Density: {localState.density}</p>
      <button onClick={verifyLaws}>Verify Laws</button>
      {verification?.all_passed && <span>✓ All laws pass</span>}
    </div>
  );
}
```

### Key Insight: Local + Gateway

- **Local polynomial** (`useDesignPolynomial`): Runs in browser, instant response to viewport/container changes
- **Gateway** (`designApi`): Authoritative law verification, operad metadata from Python backend
- **useDesignGateway**: Combines both—responsive local state + authoritative gateway data

---

## Related

- `spec/protocols/projection.md` — Projection Protocol + Density (AD-008)
- `spec/principles.md` — AD-008 Simplifying Isomorphisms
- `agents/design/` — Design operads (LAYOUT, CONTENT, MOTION)
- `impl/claude/web/src/components/elastic/` — Implementation
- `impl/claude/web/src/hooks/useDesignGateway.ts` — Gateway hook
- `impl/claude/web/src/hooks/useDesignPolynomial.ts` — Local polynomial
- `impl/claude/web/src/pages/LayoutGallery.tsx` — Live demo

---

*Lines: ~300*
