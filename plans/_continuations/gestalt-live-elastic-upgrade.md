# Continuation Prompt: GestaltLive Elastic + Illumination Upgrade

> Apply the Layout Projection Functor and Illumination System to GestaltLive, making responsive patterns automatic and mandatory.

---

## Context

**GestaltLive** (`impl/claude/web/src/pages/GestaltLive.tsx`) is a real-time 3D infrastructure visualizer that currently lacks:

1. **Layout Projection Functor patterns** - Uses inline panel handling instead of `BottomDrawer`/`FloatingActions`
2. **Illumination system** - No `SceneLighting`, `ShadowPlane`, or `SceneEffects`
3. **Density-parameterized constants** - Hardcoded values instead of `DensityMap`

**Gestalt.tsx** is the gold standard that GestaltLive should follow.

---

## The Problem: Patterns Not Used Automatically

Current elastic components exist but are optional. AI agents and developers often:
- Write inline mobile handling instead of using `BottomDrawer`
- Create manual `isMobile ? X : Y` logic instead of `DensityMap`
- Skip touch target enforcement
- Forget lighting/shadow setup in 3D scenes

**Solution**: Create higher-level abstractions that make correct usage the path of least resistance.

---

## The Prompt

```
Upgrade GestaltLive.tsx to use the Layout Projection Functor and Illumination System.

## Current State Analysis

GestaltLive is missing (compared to Gestalt.tsx):

### Missing Layout Patterns
1. No import of `BottomDrawer`, `FloatingActions` from elastic/
2. No `DensityMap` for constants - uses hardcoded values
3. Manual `isMobile` checks scattered throughout
4. EntityDetailPanel is inline (280px hardcoded width)
5. Events panel toggle is manual (`showEvents` state)

### Missing Illumination Patterns
1. No `SceneLighting` component (key light, fill light, rim light)
2. No `ShadowPlane` for ground shadows
3. No `SceneEffects` (bloom, ambient occlusion)
4. No `QualitySelector` for user performance preference
5. No `useIlluminationQuality` hook

### Missing Physical Constraints
1. EntityDetailPanel close button is `text-xl` (not 48px enforced)
2. Toggle buttons don't enforce minimum touch targets
3. No `PHYSICAL_CONSTRAINTS` import

## Implementation Steps

### Step 1: Add Density-Parameterized Constants

Replace hardcoded values with DensityMap pattern:

```tsx
import { type DensityMap, fromDensity, PHYSICAL_CONSTRAINTS } from '@/components/elastic';

// Replace hardcoded values
const PULSE_SPEED: DensityMap<number> = {
  compact: 0.004,
  comfortable: 0.005,
  spacious: 0.005,
};

const MAX_VISIBLE_EVENTS: DensityMap<number> = {
  compact: 20,
  comfortable: 30,
  spacious: 50,
};

const ENTITY_PANEL_WIDTH: DensityMap<number> = {
  compact: 0,    // Uses BottomDrawer on compact
  comfortable: 260,
  spacious: 280,
};
```

### Step 2: Import Elastic Components

```tsx
import {
  ElasticSplit,
  BottomDrawer,
  FloatingActions,
  useWindowLayout,
  PHYSICAL_CONSTRAINTS,
  type FloatingAction,
  type Density,
  type DensityMap,
  fromDensity,
} from '@/components/elastic';
```

### Step 3: Add Panel State Pattern

```tsx
interface PanelState {
  events: boolean;
  details: boolean;
}

const [panelState, setPanelState] = useState<PanelState>({
  events: false,
  details: false,
});
```

### Step 4: Convert to ElasticSplit Layout

```tsx
// Mobile: Full canvas + FAB + Drawers
// Desktop: Canvas | Sidebar

<ElasticSplit
  direction="horizontal"
  defaultRatio={0.75}
  collapseAt={768}
  collapsePriority="secondary"
  primary={<InfraCanvas topology={topology} ... />}
  secondary={<SidebarContent ... />}
/>
```

### Step 5: Add FloatingActions for Mobile

```tsx
// Only show on mobile when panels are collapsed
{isMobile && (
  <FloatingActions
    actions={[
      {
        id: 'events',
        icon: '📋',
        label: 'Events',
        onClick: () => setPanelState(s => ({ ...s, events: true })),
        isActive: panelState.events,
      },
      {
        id: 'refresh',
        icon: '🔄',
        label: 'Refresh',
        onClick: handleRetry,
        variant: 'primary',
      },
    ]}
    position="bottom-right"
  />
)}
```

### Step 6: Add BottomDrawer for Mobile Panels

```tsx
{/* Events drawer (mobile) */}
<BottomDrawer
  isOpen={panelState.events && isMobile}
  onClose={() => setPanelState(s => ({ ...s, events: false }))}
  title="Events"
>
  <EventFeed events={events} />
</BottomDrawer>

{/* Entity details drawer (mobile) */}
<BottomDrawer
  isOpen={!!selectedEntity && isMobile}
  onClose={() => setSelectedEntity(null)}
  title={selectedEntity?.name || 'Details'}
>
  {selectedEntity && <EntityDetails entity={selectedEntity} />}
</BottomDrawer>
```

### Step 7: Add Illumination System

```tsx
import { SceneLighting, ShadowPlane } from '@/components/three/SceneLighting';
import { SceneEffects } from '@/components/three/SceneEffects';
import { QualitySelector } from '@/components/three/QualitySelector';
import { useIlluminationQuality } from '@/hooks/useIlluminationQuality';

// In component:
const [quality, setQuality] = useIlluminationQuality();

// In Canvas:
<Canvas shadows={quality !== 'low'} ...>
  <SceneLighting
    quality={quality}
    keyIntensity={1.5}
    fillIntensity={0.4}
    rimEnabled={quality !== 'low'}
  />
  <ShadowPlane
    enabled={quality !== 'low'}
    size={40}
    opacity={0.3}
  />
  {/* Scene content */}
  <SceneEffects
    enabled={quality === 'high'}
    bloom={true}
    ambientOcclusion={quality === 'high'}
  />
</Canvas>
```

### Step 8: Add Quality Selector to Header

```tsx
<div className="flex items-center gap-2">
  <QualitySelector value={quality} onChange={setQuality} />
  <ConnectionStatus status={streamStatus} />
  {/* ... other controls */}
</div>
```

### Step 9: Enforce Physical Constraints

All buttons/touch targets must use PHYSICAL_CONSTRAINTS:

```tsx
<button
  onClick={onClose}
  style={{
    minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,
    minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget,
  }}
  ...
>
```

## Structural Isomorphism Verification

After refactoring, verify:

| Content | Desktop (Spacious) | Mobile (Compact) |
|---------|-------------------|------------------|
| Events panel | Fixed sidebar (280px) | Bottom drawer |
| Entity details | Fixed sidebar (280px) | Bottom drawer |
| Refresh action | Button in header | FAB |
| Events toggle | Button in header | FAB |
| Quality selector | Visible | Hidden (auto-low) |

Same information accessible in both layouts, different structures.

## Testing Requirements

1. **Layout tests**: Verify drawer opens on mobile, sidebar on desktop
2. **Touch target tests**: All interactive elements >= 48px
3. **Illumination tests**: Quality selector changes shadow/bloom behavior
4. **Density tests**: Constants change based on viewport width

## Success Criteria

- [ ] No manual `isMobile ? X : Y` conditionals (use DensityMap)
- [ ] All panels use BottomDrawer on mobile
- [ ] FloatingActions for mobile controls
- [ ] SceneLighting + ShadowPlane in 3D scene
- [ ] QualitySelector in header
- [ ] All touch targets >= 48px
- [ ] 15+ new tests
```

---

## Phase 2: Create Elastic3DPage Higher-Order Component

To prevent future pages from missing these patterns, create an HOC:

```tsx
// src/components/elastic/Elastic3DPage.tsx

interface Elastic3DPageProps {
  /** 3D canvas content */
  scene: React.ReactNode;
  /** Sidebar content (becomes drawer on mobile) */
  sidebar?: React.ReactNode;
  /** Header content */
  header?: React.ReactNode;
  /** Mobile floating actions */
  mobileActions?: FloatingAction[];
  /** Enable illumination system */
  illumination?: boolean;
  /** Enable shadows */
  shadows?: boolean;
}

export function Elastic3DPage({
  scene,
  sidebar,
  header,
  mobileActions = [],
  illumination = true,
  shadows = true,
}: Elastic3DPageProps) {
  const { density, isMobile } = useWindowLayout();
  const [quality, setQuality] = useIlluminationQuality();
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="h-screen flex flex-col">
      {/* Header with quality selector */}
      <header className="...">
        {header}
        {illumination && <QualitySelector value={quality} onChange={setQuality} />}
      </header>

      {/* Main content */}
      <div className="flex-1">
        <ElasticSplit
          collapseAt={768}
          primary={
            <Canvas shadows={shadows && quality !== 'low'}>
              {illumination && <SceneLighting quality={quality} />}
              {shadows && quality !== 'low' && <ShadowPlane />}
              {scene}
              {illumination && quality === 'high' && <SceneEffects />}
            </Canvas>
          }
          secondary={sidebar}
        />
      </div>

      {/* Mobile FAB */}
      {isMobile && mobileActions.length > 0 && (
        <FloatingActions
          actions={[
            ...mobileActions,
            sidebar && {
              id: 'sidebar',
              icon: '📋',
              label: 'Menu',
              onClick: () => setDrawerOpen(true),
            },
          ].filter(Boolean)}
        />
      )}

      {/* Mobile drawer */}
      {sidebar && (
        <BottomDrawer
          isOpen={drawerOpen && isMobile}
          onClose={() => setDrawerOpen(false)}
          title="Menu"
        >
          {sidebar}
        </BottomDrawer>
      )}
    </div>
  );
}
```

This makes the correct pattern the DEFAULT. Using `Elastic3DPage` automatically gives you:
- Responsive layout
- Mobile drawers
- FAB actions
- Illumination system
- Quality selector
- Physical constraints

---

## Exit Criteria

The upgrade is complete when:

- [ ] GestaltLive uses BottomDrawer for mobile panels
- [ ] GestaltLive uses FloatingActions for mobile controls
- [ ] GestaltLive uses DensityMap for all constants
- [ ] GestaltLive has SceneLighting + ShadowPlane
- [ ] GestaltLive has QualitySelector
- [ ] Elastic3DPage HOC created and documented
- [ ] 20+ tests added
- [ ] No hardcoded `isMobile` conditionals remain

---

## References

- **Gold Standard**: `impl/claude/web/src/pages/Gestalt.tsx`
- **Elastic Components**: `impl/claude/web/src/components/elastic/`
- **Illumination**: `impl/claude/web/src/components/three/SceneLighting.tsx`
- **Layout Projection Spec**: `spec/protocols/projection.md`
- **Plan**: `plans/web-refactor/layout-projection-functor.md`
- **Skills**: `docs/skills/elastic-ui-patterns.md`, `docs/skills/3d-lighting-patterns.md`
