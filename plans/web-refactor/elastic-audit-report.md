# Elastic UI Audit Report

> *"The same structure appears everywhere because it IS everywhere. Find it once, use it forever."*

**Audit Date**: 2025-12-16
**Auditor**: Claude Code (Elastic UI Agent)
**Reference Implementation**: `src/pages/Gestalt.tsx`

---

## Executive Summary

| Page | Status | Critical Issues | Major Issues | Minor Issues |
|------|--------|----------------|--------------|--------------|
| **Gestalt.tsx** | GOLD STANDARD | 0 | 0 | 0 |
| **Brain.tsx** | REFACTORED | 0 | 0 | 0 |
| **Town.tsx** | REFACTORED | 0 | 0 | 0 |
| **Workshop.tsx** | REFACTORED | 0 | 0 | 0 |
| **Inhabit.tsx** | REFACTORED | 0 | 0 | 0 |
| **App.tsx** | OK | 0 | 0 | 0 |

**Overall Assessment**: All pages have been refactored to match Gestalt elastic patterns.

### Refactoring Completed (Session 8)

**Brain.tsx** - Major refactor:
- Added `useWindowLayout()` for density context
- Added dedicated mobile layout with `BottomDrawer` and `FloatingActions`
- Replaced raw flex with `ElasticSplit`
- Added density-parameterized constants (`MAX_GHOST_RESULTS`, `DEFAULT_SHOW_LABELS`)
- All components now receive and adapt to density

**Town.tsx** - Moderate refactor:
- Added `useWindowLayout()` for density context
- Added dedicated mobile layout with `FloatingActions` and `BottomDrawer`
- Added `ControlsPanel` component for mobile drawer
- Made header density-aware
- Made event feed density-aware
- ElasticSplit now uses `resizable={isDesktop}`

**Workshop.tsx** - Minor refactor:
- Now properly uses `useWindowLayout()` values
- Added density-parameterized constants (`MAX_ARTIFACTS`, `MIN_GRID_ITEM_WIDTH`)
- All components now receive and adapt to density
- ElasticSplit now uses `resizable={isDesktop}`

**Inhabit.tsx** - Minor refactor:
- Added full density context (not just `isMobile`)
- All components now receive and adapt to density
- ElasticSplit now uses `resizable={isDesktop}`

---

## Detailed Audit

### 1. Gestalt.tsx - GOLD STANDARD (Reference)

**Status**: Fully compliant with elastic principles

**Patterns to emulate**:
1. **Density-parameterized constants** (lines 44-62):
   ```tsx
   const NODE_BASE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 } as const;
   const LABEL_FONT_SIZE = { compact: 0.14, comfortable: 0.18, spacious: 0.22 } as const;
   const MAX_VISIBLE_LABELS = { compact: 15, comfortable: 30, spacious: 50 } as const;
   ```

2. **Proper useWindowLayout usage** (line 835):
   ```tsx
   const { width, density, isMobile, isTablet, isDesktop } = useWindowLayout();
   ```

3. **Dedicated mobile layout** (lines 984-1080):
   - Full canvas with `FloatingActions`
   - `BottomDrawer` for panels
   - Compact header
   - Smart defaults (`showLabels` off on mobile)

4. **Components receive density, adapt internally**:
   - `ModuleDetailPanel` accepts `density` prop
   - `ControlPanel` accepts `density` prop
   - Both adapt their styling based on density

5. **Touch targets ≥48px** (lines 724-755):
   - FloatingActions use `w-12 h-12` (48px)

6. **ElasticSplit for desktop/tablet** (lines 1198-1214):
   - `resizable={isDesktop}` - only draggable on desktop
   - `collapseAt={PANEL_COLLAPSE_BREAKPOINT}` (768px)

---

### 2. Brain.tsx - NEEDS REFACTOR

**Status**: Does not follow elastic patterns

**Checklist Assessment**:
- [ ] Uses `useWindowLayout()` - **MISSING**
- [ ] Passes `density` to child components - **MISSING**
- [ ] No scattered `isMobile` conditionals - N/A (no responsive code)
- [ ] Uses `ElasticSplit` - **MISSING** (uses raw flex)
- [ ] Has dedicated mobile layout - **MISSING**
- [ ] Uses `BottomDrawer` for mobile - **MISSING**
- [ ] Uses `FloatingActions` for mobile - **MISSING**
- [ ] Touch targets ≥48px - **NOT CHECKED**
- [ ] Density-aware constants - **MISSING**
- [ ] Loading/error states density-aware - **PARTIAL**

#### Critical Issues

1. **No responsive layout at all** (line 258-374)
   - Sidebar is fixed at `w-80` (320px)
   - No collapse behavior on mobile
   - Side panel never becomes a drawer
   ```tsx
   // Current: Fixed 2-column layout
   <div className="flex h-[calc(100vh-80px)]">
     <div className="flex-1 relative">...</div>
     <div className="w-80 border-l border-gray-800 p-4 overflow-y-auto">...</div>
   </div>
   ```

2. **No useWindowLayout hook usage**
   - Page doesn't import or use `useWindowLayout`
   - No density context passed to components
   - No responsive behavior at all

3. **No mobile layout**
   - Mobile users see squished desktop layout
   - Side panel unusable on narrow screens
   - No floating actions for mobile interactions

#### Major Issues

4. **No density-aware constants**
   - Magic numbers throughout (e.g., `w-80`, `p-4`, `text-sm`)
   - Should use parameterized constants like Gestalt

5. **Fixed sidebar doesn't collapse**
   - Should use ElasticSplit with `collapseAt`
   - Should become BottomDrawer on mobile

6. **3D canvas not responsive**
   - No camera distance adjustment for mobile
   - Labels may be too small/large on different densities

7. **Header not responsive**
   - Same padding/sizing on all screens
   - View mode toggle may be cramped on mobile

#### Minor Issues

8. **No smart defaults by density**
   - `showLabels` defaults to `true` on all screens
   - Should be `false` on mobile like Gestalt

9. **Loading/error states not density-aware**
   - Same presentation on all screen sizes
   - Could be more compact on mobile

---

### 3. Town.tsx - PARTIAL COMPLIANCE

**Status**: Uses ElasticSplit but lacks density context

**Checklist Assessment**:
- [ ] Uses `useWindowLayout()` - **MISSING**
- [ ] Passes `density` to child components - **MISSING**
- [ ] Uses `ElasticSplit` - **YES** (line 178)
- [ ] Has dedicated mobile layout - **NO** (uses ElasticSplit collapse only)
- [ ] Uses `BottomDrawer` for mobile - **NO**
- [ ] Uses `FloatingActions` for mobile - **NO**
- [ ] Touch targets ≥48px - **PARTIAL**
- [ ] Density-aware constants - **NO**

#### Critical Issue

1. **No useWindowLayout or density context**
   - Components don't receive density
   - No density-aware styling

#### Major Issues

2. **No FloatingActions on mobile**
   - When ElasticSplit collapses, play/pause controls are in header
   - Would benefit from FloatingActions pattern

3. **Header not responsive** (lines 260-314)
   - Fixed sizing regardless of screen
   - Could be more compact on mobile

4. **Event feed doesn't adapt to density**
   - Same presentation on all screens
   - Should show fewer events on mobile

#### Minor Issues

5. **Touch targets in header** (lines 294-308)
   - `px-3 py-1` may be too small for touch
   - Should be at least 44px height

6. **No smart defaults**
   - Same initial state on all screen sizes

---

### 4. Workshop.tsx - PARTIAL COMPLIANCE

**Status**: Good elastic component usage but no density context

**Checklist Assessment**:
- [ ] Uses `useWindowLayout()` - **YES** (but unused, line 45)
- [ ] Passes `density` to child components - **NO**
- [ ] Uses `ElasticSplit` - **YES** (line 66)
- [ ] Uses `ElasticContainer` - **YES**
- [ ] Uses `ElasticCard` - **YES**
- [ ] Uses `ElasticPlaceholder` - **YES**
- [ ] Has dedicated mobile layout - **NO**
- [ ] Uses `FloatingActions` for mobile - **NO**
- [ ] Density-aware constants - **NO**

#### Major Issues

1. **useWindowLayout called but not used** (line 45)
   ```tsx
   useWindowLayout(); // Called but destructured values unused
   ```

2. **No density passed to components**
   - ElasticCard doesn't receive density
   - Panels don't adapt to density

#### Minor Issues

3. **Header not density-aware** (lines 144-178)
   - Same sizing on all screens

4. **Grid minItemWidth is fixed** (line 204)
   - Should be density-parameterized

5. **No FloatingActions on mobile**
   - "Create Task" button is in empty state, not floating

---

### 5. Inhabit.tsx - PARTIAL COMPLIANCE

**Status**: Good elastic usage with minor gaps

**Checklist Assessment**:
- [ ] Uses `useWindowLayout()` - **YES** (line 35)
- [ ] Passes `density` to child components - **NO** (only uses `isMobile`)
- [ ] Uses `ElasticSplit` - **YES** (line 82)
- [ ] Uses `ElasticContainer` - **YES**
- [ ] Uses `ElasticCard` - **YES**
- [ ] Uses `ElasticPlaceholder` - **YES**
- [ ] `resizable={!isMobile}` - **YES** (line 88)
- [ ] Has dedicated mobile layout - **NO**
- [ ] Uses `FloatingActions` for mobile - **NO**

#### Major Issues

1. **Only uses `isMobile`, not full density context**
   - Should pass `density` to components
   - Components should adapt based on density, not just mobile boolean

2. **No FloatingActions on mobile**
   - Action buttons in side panel, not floating

#### Minor Issues

3. **No density-aware styling**
   - Padding/gaps are fixed
   - EigenvectorGrid could be more compact on mobile

4. **Header not density-aware** (lines 176-208)
   - Same layout on all screens

---

### 6. App.tsx - OK

**Status**: Just routing, not relevant to elastic patterns

App.tsx handles routing only. No layout patterns to audit.

---

## Recommended Fixes

### Priority 1: Brain.tsx (Critical)

1. Import and use `useWindowLayout`:
   ```tsx
   const { width, density, isMobile, isTablet, isDesktop } = useWindowLayout();
   ```

2. Add dedicated mobile layout with:
   - `BottomDrawer` for side panel
   - `FloatingActions` for capture/ghost surfacing
   - Compact header

3. Replace raw flex with `ElasticSplit`:
   ```tsx
   <ElasticSplit
     direction="horizontal"
     defaultRatio={0.75}
     collapseAt={768}
     collapsePriority="secondary"
     resizable={isDesktop}
     primary={<Topology3D density={density} />}
     secondary={<ControlPanel density={density} />}
   />
   ```

4. Add density-parameterized constants for node sizes, labels, etc.

### Priority 2: Town.tsx (Major)

1. Import and use `useWindowLayout`
2. Pass `density` to all components
3. Add `FloatingActions` for mobile
4. Make header responsive

### Priority 3: Workshop.tsx (Moderate)

1. Actually use the `useWindowLayout` values
2. Pass `density` to components
3. Add density-parameterized constants

### Priority 4: Inhabit.tsx (Moderate)

1. Use full density context, not just `isMobile`
2. Pass `density` to components
3. Add density-aware styling

---

## User Flow Validation

### Flow 1: Mobile User Explores Town

**Status**: PARTIAL

**Issues**:
- No FloatingActions - controls only accessible in sidebar
- Header controls may be cramped
- Event feed takes same space on mobile

**Recommendation**: Add FloatingActions for play/pause/speed

### Flow 2: Tablet User Analyzes Architecture (Gestalt)

**Status**: PASS

Gestalt handles this flow excellently with:
- ElasticSplit with resizable divider
- Appropriate collapse behavior
- Density-aware panels

### Flow 3: Desktop User Deep-Dives Brain

**Status**: FAIL

**Issues**:
- No ElasticSplit, fixed sidebar width
- No density context
- Side panel always same size

**Recommendation**: Full refactor to match Gestalt patterns

### Flow 4: User Switches Between Pages

**Status**: FAIL - INCONSISTENT

**Issues**:
- Gestalt: Full mobile support with drawers and floating actions
- Brain: No mobile support at all
- Town: ElasticSplit only, no floating actions
- Workshop: Similar to Town
- Inhabit: Similar to Town

**Recommendation**: All pages should follow Gestalt's pattern for consistency

---

## Anti-Patterns Found

### 1. Missing useWindowLayout

**Brain.tsx** doesn't use `useWindowLayout` at all.

### 2. Unused useWindowLayout

**Workshop.tsx** calls `useWindowLayout()` but doesn't use the returned values.

### 3. Using Only isMobile

**Inhabit.tsx** extracts only `isMobile` when full density context should be used.

### 4. Fixed Widths

**Brain.tsx** uses `w-80` fixed width instead of responsive patterns.

### 5. No Mobile Layout

**Brain.tsx** has no dedicated mobile layout - just squished desktop.

### 6. No FloatingActions

**Town.tsx**, **Workshop.tsx**, **Inhabit.tsx** don't use FloatingActions on mobile.

---

## Summary

The kgents web UI has one exemplary page (Gestalt) that demonstrates all elastic patterns correctly. Other pages range from "needs minor fixes" (Inhabit) to "needs full refactor" (Brain).

**Key Actions**:
1. **Refactor Brain.tsx** to match Gestalt patterns (CRITICAL)
2. **Add useWindowLayout** to all pages (HIGH)
3. **Pass density** to all components (HIGH)
4. **Add FloatingActions** to Town, Workshop, Inhabit (MEDIUM)
5. **Create shared mobile patterns** for consistency (MEDIUM)

---

*"The projection is not the territory. But understanding the isomorphism between projections reveals the territory's true shape."*
