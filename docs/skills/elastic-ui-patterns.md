# Elastic UI Patterns

> *"Density is not screen size. Density is the capacity to receive."*

## When to Use

- Building responsive React pages with multi-pane layouts
- Widgets that must adapt to available space (card content degradation)
- Touch-friendly mobile experiences with drawer patterns
- Pages that need consistent behavior from 320px to 4K

---

## The Density-Content Isomorphism

The core insight: **Screen density and content detail level are isomorphic**. This is not a metaphor—it's a categorical equivalence that can be exploited:

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

| Domain | Concept | Isomorphic To |
|--------|---------|---------------|
| **AGENTESE** | Observer-dependent perception | Density-aware rendering |
| **Projection Protocol** | CLI/Web/marimo targets | Mobile/Tablet/Desktop modes |
| **Polynomial Agents** | State-dependent input types | Layout-dependent content |
| **Sheaf Theory** | Local-to-global consistency | Component-to-page coherence |

**The algorithm**: When you find yourself writing `if (isMobile)` multiple times, you've discovered an isomorphism. Extract it once, apply it everywhere.

---

## The Three-Mode Pattern

Every kgents UI should support three density modes:

| Mode | Breakpoint | Characteristics |
|------|------------|-----------------|
| **Compact** | <640px (mobile) | Drawer-based, touch-friendly, minimal chrome |
| **Comfortable** | 640-1024px (tablet) | Hybrid, collapsible panels, balanced |
| **Spacious** | >1024px (desktop) | Full panels, draggable dividers, maximum information |

### Mode Detection

```tsx
import { useWindowLayout } from '@/hooks/useLayoutContext';

function MyComponent() {
  const { density, isMobile, isTablet, isDesktop } = useWindowLayout();

  // density: 'compact' | 'comfortable' | 'spacious'
  // Use density for parameterized constants
  // Use isMobile/isTablet/isDesktop for structural differences
}
```

---

## Density-Aware Constants Pattern

**BAD: Ad-hoc conditionals**
```tsx
const nodeSize = isMobile ? 0.2 : isTablet ? 0.25 : 0.3;
const fontSize = isMobile ? 14 : 18;
const maxItems = isMobile ? 15 : 50;
```

**GOOD: Parameterized by density**
```tsx
const NODE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 } as const;
const LABEL_FONT_SIZE = { compact: 0.14, comfortable: 0.18, spacious: 0.22 } as const;
const MAX_VISIBLE_LABELS = { compact: 15, comfortable: 30, spacious: 50 } as const;

// Usage
const size = NODE_SIZE[density];
const fontSize = LABEL_FONT_SIZE[density];
const maxLabels = MAX_VISIBLE_LABELS[density];
```

**Why this matters**: The constant lookup is now a morphism from Density → Value. The shape of your conditionals matches the shape of your domain.

---

## Smart Defaults by Density

Each mode has sensible defaults that reduce cognitive load:

### Compact (Mobile)
- Labels/chrome **off** by default (toggle on)
- Fewer items rendered (performance)
- Touch targets minimum 48px
- Floating actions instead of toolbars
- Bottom drawers for panels

### Comfortable (Tablet)
- Balanced information density
- Collapsible panels (toggle)
- Moderate chrome
- Hybrid touch/mouse interaction

### Spacious (Desktop)
- Full information display
- Persistent panels
- Draggable dividers
- Rich legends and annotations

```tsx
// Example: Default labels based on density
const [showLabels, setShowLabels] = useState(!isMobile);

// Example: Default max nodes based on density
const [maxNodes, setMaxNodes] = useState(
  isMobile ? 100 : isTablet ? 125 : 150
);
```

---

## Component Patterns

### ElasticSplit: Two-Pane Responsive Layout

```tsx
<ElasticSplit
  direction="horizontal"
  defaultRatio={0.75}
  collapseAt={768}           // Stack vertically below this width
  collapsePriority="secondary" // What collapses first
  minPaneSize={280}
  resizable={isDesktop}      // Only draggable on desktop
  primary={<MainCanvas />}
  secondary={<SidePanel />}
/>
```

**Key Props:**
- `collapseAt`: Breakpoint for vertical stacking
- `collapsePriority`: Which pane collapses first ('primary' | 'secondary')
- `resizable`: Enable draggable divider (typically desktop-only)

### BottomDrawer: Mobile Slide-Up Panels

For mobile, replace side panels with bottom drawers:

```tsx
function BottomDrawer({ isOpen, onClose, title, children }) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />

      {/* Drawer */}
      <div className="fixed bottom-0 left-0 right-0 z-50 max-h-[70vh]
                      bg-gray-800 rounded-t-xl shadow-2xl">
        {/* Drag handle */}
        <div className="flex justify-center py-2">
          <div className="w-10 h-1 bg-gray-600 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex justify-between items-center px-4 pb-2
                        border-b border-gray-700">
          <h3 className="text-sm font-semibold">{title}</h3>
          <button onClick={onClose}>×</button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(70vh-60px)]">
          {children}
        </div>
      </div>
    </>
  );
}
```

### FloatingActions: Mobile Action Buttons

Replace toolbars with floating action buttons on mobile:

```tsx
function FloatingActions({ onScan, onToggleControls, onToggleDetails }) {
  return (
    <div className="absolute bottom-4 right-4 flex flex-col gap-2">
      <button
        onClick={onScan}
        className="w-12 h-12 bg-green-600 rounded-full shadow-lg
                   flex items-center justify-center text-xl"
      >
        🔄
      </button>
      <button
        onClick={onToggleControls}
        className="w-12 h-12 bg-gray-700 rounded-full shadow-lg
                   flex items-center justify-center text-xl"
      >
        ⚙️
      </button>
    </div>
  );
}
```

### ElasticContainer: Self-Arranging Grids

```tsx
<ElasticContainer
  layout="grid"              // 'flow' | 'grid' | 'stack'
  minItemWidth={200}         // Grid auto-fit column min
  gap="var(--elastic-gap-md)"
  transition="smooth"
  emptyState={<Placeholder />}
>
  {items.map(item => <Card key={item.id} {...item} />)}
</ElasticContainer>
```

---

## Responsive Content Degradation

Cards should adapt content based on available width:

```tsx
type ContentLevel = 'icon' | 'title' | 'summary' | 'full';

function getContentLevel(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}

function CitizenCard({ width, citizen }) {
  const level = getContentLevel(width);

  return (
    <div>
      {/* Icon always visible */}
      <span>{citizen.icon}</span>

      {/* Title at 150px+ */}
      {level !== 'icon' && <span>{citizen.name}</span>}

      {/* Summary at 280px+ */}
      {level === 'summary' || level === 'full' && (
        <span>{citizen.phase}</span>
      )}

      {/* Full at 400px+ */}
      {level === 'full' && <FullDetails citizen={citizen} />}
    </div>
  );
}
```

**Content Level Thresholds:**

| Level | Width | Displays |
|-------|-------|----------|
| `icon` | <60px | Icon only |
| `title` | <150px | Icon + name |
| `summary` | <280px | Icon + name + phase |
| `full` | ≥400px | Full card content |

---

## Mobile Layout Pattern

For complex pages, use a dedicated mobile layout:

```tsx
function MyPage() {
  const { isMobile, density } = useWindowLayout();
  const [panelState, setPanelState] = useState({ controls: false, details: false });

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col">
        {/* Compact header */}
        <header className="flex-shrink-0 px-3 py-2">
          <CompactHeader />
        </header>

        {/* Main content (full canvas) */}
        <div className="flex-1 relative">
          <Canvas density={density} />
          <FloatingActions
            onToggleControls={() => setPanelState(s => ({ ...s, controls: !s.controls }))}
          />
        </div>

        {/* Bottom drawers */}
        <BottomDrawer
          isOpen={panelState.controls}
          onClose={() => setPanelState(s => ({ ...s, controls: false }))}
          title="Controls"
        >
          <ControlPanel density={density} isDrawer />
        </BottomDrawer>
      </div>
    );
  }

  // Desktop/tablet: ElasticSplit layout
  return (
    <div className="h-screen flex flex-col">
      <header><FullHeader /></header>
      <div className="flex-1 overflow-hidden">
        <ElasticSplit
          defaultRatio={0.75}
          collapseAt={768}
          primary={<Canvas density={density} />}
          secondary={<ControlPanel density={density} />}
        />
      </div>
    </div>
  );
}
```

---

## CSS Custom Properties

Elastic primitives use these CSS variables (defined in `globals.css`):

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
}
```

---

## UI Building Algorithm

1. **IDENTIFY THE DIMENSIONS**
   - What varies? (screen size, user role, data state)
   - Name each dimension explicitly (density, tier, mode)

2. **DEFINE THE PROJECTION SPACE**
   - What are the valid combinations?
   - Which combinations are isomorphic? (`mobile + viewer ≅ compact`)

3. **BUILD ATOMIC PRIMITIVES**
   - Components that accept dimension values
   - Internal adaptation, not external conditionals

4. **COMPOSE WITH ELASTIC CONTAINERS**
   - `ElasticSplit` for pane layouts
   - `ElasticContainer` for collections
   - `BottomDrawer` for mobile panels

5. **PROVIDE CONTEXT AT THE RIGHT LEVEL**
   - Window-level: `useWindowLayout()` (density, breakpoints)
   - Page-level: page-specific state (selected item)
   - Component-level: `useLayoutMeasure()` (container size)

6. **SMART DEFAULTS BY DENSITY**
   - Compact: minimal, touch-friendly, progressive disclosure
   - Comfortable: balanced, collapsible, moderate chrome
   - Spacious: full information, draggable, persistent panels

7. **VALIDATE THE ISOMORPHISMS**
   - Does mobile behave like "compact web"?
   - Can you describe behavior without mentioning screen size?

---

## Anti-Patterns

### Scattered Conditionals
```tsx
// BAD: isMobile checks everywhere
{isMobile ? <CompactThing /> : <FullThing />}
{isMobile ? 'Short' : 'A much longer label'}
{isMobile && <MobileOnlyWidget />}
```

```tsx
// GOOD: Pass density, let components decide
<Thing density={density} />
<Label density={density} />
<Widget density={density} />
```

### Mode-Specific Components
```tsx
// BAD: Separate components per mode
<MobileControlPanel />
<TabletControlPanel />
<DesktopControlPanel />
```

```tsx
// GOOD: One component, density-aware
<ControlPanel density={density} isDrawer={isMobile} />
```

### Forgetting Touch Targets
```tsx
// BAD: 24px buttons on mobile
<button className="p-1">×</button>

// GOOD: 48px minimum touch targets
<button className="w-12 h-12 p-3">×</button>
```

### Calling Hooks Without Using Values
```tsx
// BAD: Hook called but values unused (found in Workshop.tsx)
export default function MyPage() {
  useWindowLayout(); // Called but not destructured
  // ...
}

// GOOD: Destructure and use the values
export default function MyPage() {
  const { density, isMobile, isDesktop } = useWindowLayout();
  // Now actually USE density in the component
}
```

### Using Only isMobile, Ignoring Density
```tsx
// BAD: Only using isMobile for binary decisions (found in Inhabit.tsx)
const { isMobile } = useWindowLayout();
// Loses the three-mode nuance

// GOOD: Use full density context
const { density, isMobile, isDesktop } = useWindowLayout();
// Pass density to components, use isMobile only for structural layout decisions
```

---

## Refactoring Guide

How to refactor an existing page to elastic patterns (derived from Brain.tsx and Town.tsx refactors):

### Step 1: Audit Current State

Run through this checklist:
- [ ] Uses `useWindowLayout()`?
- [ ] Passes `density` to child components?
- [ ] Has dedicated mobile layout?
- [ ] Uses `ElasticSplit` for two-pane layouts?
- [ ] Uses `BottomDrawer` for mobile panels?
- [ ] Uses `FloatingActions` for mobile?
- [ ] Touch targets ≥48px?
- [ ] Has density-parameterized constants?

### Step 2: Add Layout Context

```tsx
// Add to top of component
const { density, isMobile, isTablet, isDesktop } = useWindowLayout();
```

### Step 3: Extract Constants

Find all magic numbers and extract to density lookup:

```tsx
// Before (scattered in component)
const maxItems = isMobile ? 5 : 10;
const fontSize = isMobile ? 12 : 14;

// After (constants at module level)
const MAX_ITEMS = { compact: 3, comfortable: 5, spacious: 10 } as const;
const FONT_SIZE = { compact: 12, comfortable: 13, spacious: 14 } as const;

// In component
const maxItems = MAX_ITEMS[density];
const fontSize = FONT_SIZE[density];
```

### Step 4: Add Mobile Layout Branch

```tsx
// After state and effects, before main return
if (isMobile) {
  return (
    <div className="h-screen flex flex-col">
      {/* Compact header */}
      <header className="flex-shrink-0 px-3 py-2">...</header>

      {/* Main content */}
      <div className="flex-1 relative">
        {mainContent}
        <FloatingActions onToggle={...} />
      </div>

      {/* Bottom drawers */}
      <BottomDrawer isOpen={state.panel} onClose={...}>
        <Panel density={density} isDrawer />
      </BottomDrawer>
    </div>
  );
}

// Desktop/tablet layout continues below...
```

### Step 5: Update ElasticSplit Props

```tsx
<ElasticSplit
  defaultRatio={0.75}
  collapseAt={768}
  collapsePriority="secondary"
  minPaneSize={isMobile ? 200 : 280}  // Smaller on mobile
  resizable={isDesktop}                // Only draggable on desktop
  primary={...}
  secondary={...}
/>
```

### Step 6: Update Child Components

Add density prop to each sub-component:

```tsx
// Before
interface PanelProps {
  data: Data;
  onAction: () => void;
}

// After
interface PanelProps {
  data: Data;
  onAction: () => void;
  density: Density;
  isDrawer?: boolean;  // Optional: behave differently in drawer
}

function Panel({ data, onAction, density, isDrawer }: PanelProps) {
  const isCompact = density === 'compact';

  return (
    <div className={isCompact ? 'p-3' : 'p-4'}>
      {/* Component adapts internally based on density */}
    </div>
  );
}
```

### Step 7: Validate

Test at these widths:
- 375px (iPhone SE)
- 768px (iPad portrait)
- 1024px (iPad landscape)
- 1440px (Desktop)

Verify:
- Mobile has full-screen canvas + floating actions + drawers
- Tablet has collapsible panels
- Desktop has draggable dividers
- All transitions are smooth (no jarring layout shifts)

---

## Real-World Examples

### Brain.tsx Refactor Summary

**Before**: Fixed 2-column layout with `w-80` sidebar
```tsx
<div className="flex h-[calc(100vh-80px)]">
  <div className="flex-1 relative">...</div>
  <div className="w-80 border-l">...</div>
</div>
```

**After**: Full elastic layout
```tsx
// Mobile: Full canvas + floating actions + drawers
if (isMobile) {
  return (
    <div className="h-screen flex flex-col">
      <CompactHeader />
      <div className="flex-1 relative">
        {canvas3D}
        <FloatingActions onToggle={...} />
      </div>
      <BottomDrawer isOpen={panelState.controls}>
        <ControlPanel density={density} isDrawer />
      </BottomDrawer>
    </div>
  );
}

// Desktop: ElasticSplit with resizable divider
return (
  <ElasticSplit
    resizable={isDesktop}
    primary={canvas3D}
    secondary={<ControlPanel density={density} />}
  />
);
```

### Town.tsx Refactor Summary

**Before**: ElasticSplit but no mobile awareness
```tsx
<ElasticSplit
  resizable={true}  // Always resizable
  primary={<Mesa />}
  secondary={<Sidebar />}
/>
```

**After**: Dedicated mobile layout with floating actions
```tsx
if (isMobile) {
  return (
    <div className="h-[calc(100vh-64px)] flex flex-col">
      <CompactHeader />
      <div className="flex-1 relative">
        <Mesa />
        <FloatingActions
          isPlaying={isPlaying}
          onTogglePlay={handleToggle}
          onOpenControls={() => setControlsDrawerOpen(true)}
        />
      </div>
      <BottomDrawer isOpen={controlsDrawerOpen}>
        <ControlsPanel density={density} />
      </BottomDrawer>
    </div>
  );
}

// Desktop/tablet with proper resizable prop
<ElasticSplit
  resizable={isDesktop}  // Only on desktop
  primary={<Mesa />}
  secondary={<Sidebar />}
/>
```

---

## The Categorical Stack

How category theory applies to elastic UI:

| Concept | UI Application |
|---------|----------------|
| **Functor** | Layout strategy: `data → rendered elements` |
| **Natural Transformation** | Responsive adaptation: `desktop → mobile` |
| **Isomorphism** | Density equivalence: `mobile ≅ compact ≅ minimal` |
| **Sheaf** | Local components glue to global page layout |
| **Polynomial** | State-dependent UI: `mode → available interactions` |

---

## Related

- `docs/skills/ui-isomorphism-detection.md` — Finding these patterns
- `spec/protocols/projection.md` — Projection Protocol + Density
- `spec/principles.md` — AD-008 Simplifying Isomorphisms
- `plans/web-refactor/elastic-primitives.md` — Original implementation plan

---

*"The projection is not the territory. But understanding the isomorphism between projections reveals the territory's true shape."*
