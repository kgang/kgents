# Continuation Prompt: Layout Projection Functor - STRATEGIZE Phase

> Use this prompt to continue implementing the Layout Projection Functor from STRATEGIZE through IMPLEMENT.

---

## Context

The Layout Projection Functor RESEARCH and DEVELOP phases are **complete**. The canonical types, components, and composition law tests are in place.

**Plan**: `plans/web-refactor/layout-projection-functor.md` (35% complete)
**Spec**: `spec/protocols/projection.md` (lines 213-424)

---

## What's Done

### DEVELOP Phase Deliverables (2025-12-16)

| File | Description |
|------|-------------|
| `elastic/types.ts` | Canonical types: `Density`, `LayoutHints`, `DensityMap`, `LAYOUT_PRIMITIVES`, `PHYSICAL_CONSTRAINTS` |
| `elastic/BottomDrawer.tsx` | Mobile panel projection with 48px touch targets |
| `elastic/FloatingActions.tsx` | Mobile actions projection with 48px buttons |
| `elastic/index.ts` | Barrel exports for all new types and components |
| `hooks/useLayoutContext.ts` | Breakpoints aligned to spec (sm: 768, lg: 1024) |
| `tests/unit/elastic/composition.test.tsx` | 22 composition law tests (all passing) |

### Key APIs Established

```typescript
// Import from elastic/
import {
  type Density,
  type LayoutHints,
  type DensityMap,
  DENSITY_BREAKPOINTS,
  PHYSICAL_CONSTRAINTS,
  LAYOUT_PRIMITIVES,
  getDensityFromWidth,
  fromDensity,
  createDensityMap,
  getPrimitiveBehavior,
  BottomDrawer,
  FloatingActions,
} from '@/components/elastic';

// Density-parameterized constants (canonical pattern)
const NODE_SIZE: DensityMap<number> = { compact: 0.2, comfortable: 0.25, spacious: 0.3 };
const size = fromDensity(NODE_SIZE, density);

// Layout primitive behavior lookup
const panelBehavior = getPrimitiveBehavior('panel', 'compact'); // → 'bottom_drawer'
```

### Composition Laws Verified

1. **Vertical Preservation**: `Layout[D](A // B) = Layout[D](A) // Layout[D](B)` ✓
2. **Horizontal Transformation**: `>>` → overlay in compact mode ✓
3. **Physical Invariance**: `TouchTarget >= 48px` ∀D ✓
4. **Structural Isomorphism**: Information preserved across layouts ✓

---

## The Prompt

```
Layout Projection Functor RESEARCH and DEVELOP phases are complete.

## Current State

- 22 composition law tests passing
- 39 elastic tests passing (total)
- Types, BottomDrawer, FloatingActions implemented
- Breakpoints aligned to spec (768/1024)

## Your Task: STRATEGIZE + CROSS-SYNERGIZE + IMPLEMENT

### STRATEGIZE Phase

Plan the remaining implementation work:

1. **Gallery Pilots** (Phase 4 from plan)
   - Design 8 layout projection pilots for the Projection Gallery
   - Pilots should demonstrate: sidebar↔drawer, toolbar↔FAB, isomorphism

2. **Gestalt Refactor**
   - Plan how to refactor Gestalt.tsx to use extracted BottomDrawer/FloatingActions
   - Currently has inline implementations (~50 lines to remove)

3. **AGENTESE Integration** (Phase 5 from plan)
   - Design layout-aware `manifest` for umwelt capacity
   - Plan paths: `world.panel.manifest` → density-appropriate projection

### CROSS-SYNERGIZE Phase

Look for patterns from other crown jewels:

1. **Brain** - How does holographic brain handle density?
2. **Atelier** - Bidding UI adapts to mobile?
3. **Coalition Forge** - Any layout projection patterns?

Document reusable patterns in session_notes.

### IMPLEMENT Phase (if time permits)

1. Refactor Gestalt.tsx to use BottomDrawer/FloatingActions from elastic/
2. Add a simple gallery pilot demonstrating sidebar↔drawer isomorphism
3. Wire up basic AGENTESE path for layout-aware manifest

## Key Files to Reference

1. `impl/claude/web/src/components/elastic/types.ts` - The canonical types
2. `impl/claude/web/src/components/elastic/BottomDrawer.tsx` - Panel primitive
3. `impl/claude/web/src/components/elastic/FloatingActions.tsx` - Actions primitive
4. `impl/claude/web/src/pages/Gestalt.tsx` - Gold standard, needs refactor
5. `spec/protocols/projection.md` (lines 369-388) - AGENTESE connection

## Success Criteria

- [ ] STRATEGIZE: Clear plan for gallery pilots documented
- [ ] STRATEGIZE: Gestalt refactor steps identified
- [ ] STRATEGIZE: AGENTESE integration design written
- [ ] CROSS-SYNERGIZE: Patterns from other jewels documented
- [ ] IMPLEMENT: Gestalt uses extracted BottomDrawer/FloatingActions
- [ ] IMPLEMENT: At least 1 gallery pilot working

## Important Patterns

### Density-Parameterized Constants

```typescript
// Anti-pattern: scattered conditionals
const size = isMobile ? 0.2 : isTablet ? 0.25 : 0.3;

// Pattern: density map lookup
const NODE_SIZE: DensityMap<number> = { compact: 0.2, comfortable: 0.25, spacious: 0.3 };
const size = fromDensity(NODE_SIZE, density);
```

### Layout Primitive Selection

```typescript
// Get behavior for current density
const panelBehavior = getPrimitiveBehavior('panel', density);

switch (panelBehavior) {
  case 'bottom_drawer':
    return <BottomDrawer {...props} />;
  case 'collapsible_panel':
    return <CollapsiblePanel {...props} />;
  case 'fixed_sidebar':
    return <FixedSidebar {...props} />;
}
```

### Physical Constraints (Invariant)

```typescript
// These do NOT change with density
const buttonStyle = {
  minWidth: PHYSICAL_CONSTRAINTS.minTouchTarget,  // 48px
  minHeight: PHYSICAL_CONSTRAINTS.minTouchTarget, // 48px
};
```

## Update Plan File

When done, update `plans/web-refactor/layout-projection-functor.md`:
- Add session_notes for STRATEGIZE findings
- Mark phases complete in phase_ledger
- Update progress percentage (target: 60% after IMPLEMENT)
```

---

## Expected Outputs

### After STRATEGIZE Phase

```yaml
session_notes: |
  STRATEGIZE Complete (2025-12-XX):

  ## Gallery Pilots Design
  1. panel_sidebar - Panel in spacious mode (fixed sidebar)
  2. panel_drawer - Same panel in compact mode (bottom drawer)
  3. panel_isomorphism - Split view showing both
  4. actions_toolbar - Actions as full toolbar (spacious)
  5. actions_fab - Same actions as FAB cluster (compact)
  6. split_resizable - ElasticSplit with drag handle
  7. split_collapsed - Same split in stacked mode
  8. touch_targets - 48px minimum demonstration

  ## Gestalt Refactor Plan
  1. Import BottomDrawer, FloatingActions from elastic/
  2. Remove inline BottomDrawer (lines 644-675)
  3. Remove inline FloatingActions (lines 588-631)
  4. Update FloatingActionsProps to use FloatingAction[]
  5. Verify mobile layout still works

  ## AGENTESE Integration Design
  - Add Capacity.density to Umwelt
  - world.panel.manifest(umwelt) returns layout-appropriate JSON
  - Observer modality: 'touch' | 'pointer' determines affordances
```

### After IMPLEMENT Phase

```yaml
session_notes: |
  IMPLEMENT Complete (2025-12-XX):

  ## Gestalt Refactor
  - Removed 87 lines of inline implementations
  - Now uses elastic/BottomDrawer and elastic/FloatingActions
  - Mobile layout verified working

  ## Gallery Pilot: panel_isomorphism
  - File: protocols/projection/gallery/layout_pilots.py
  - Shows sidebar in spacious, drawer in compact
  - Demonstrates structural isomorphism

  ## Test Count: 61 elastic tests (was 39)
```

---

## Phase Handoff

| Phase | Input | Output |
|-------|-------|--------|
| STRATEGIZE | Completed types + tests | Design docs for gallery, refactor, AGENTESE |
| CROSS-SYNERGIZE | Other crown jewel patterns | Reusable patterns documented |
| IMPLEMENT | Design docs | Working code: refactored Gestalt, 1+ pilots |
| QA | Working code | Property-based tests for edge cases |
| TEST | QA-hardened code | Full test suite (target: 80+ elastic tests) |

---

*"The functor that preserves structure is the functor that enables composition."*
