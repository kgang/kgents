# Phase 5: Zustand Removal and V2 Rename - Continuation Prompt

## Context

**Previous Phases Complete:**
- Phase 1: Foundation (76 tests) - `types.ts`, `useWidgetState.ts`, `WidgetRenderer.tsx`, `context.tsx`
- Phase 2: Widget Components (109 tests) - `/widgets/` directory with primitives/, layout/, cards/, dashboards/
- Phase 3: SSE Integration (19 + 25 tests) - `live.state` event emission, `useTownStreamWidget` hook
- Phase 4: Migration (38 tests) - `TownV2.tsx`, `MesaV2.tsx`, `CitizenPanelV2.tsx` running in parallel

**Current State:**
- TownV2 (`/town-v2/:townId`) uses widget-based architecture with `useTownStreamWidget`
- Town (`/town/:townId`) uses legacy Zustand-based architecture
- Both routes work in parallel for A/B testing

**Goal:** Remove all legacy Zustand-based Town code and rename V2 files to become the primary implementation.

---

## Pre-Flight Checklist

Before starting, verify TownV2 is stable:

```bash
cd impl/claude/web

# 1. Run all widget/reactive tests
npm test -- --run tests/unit/reactive tests/unit/widgets tests/unit/pages/TownV2.test.tsx tests/unit/components/MesaV2.test.tsx tests/unit/components/CitizenPanelV2.test.tsx

# 2. TypeScript check
npm run typecheck

# 3. Manual smoke test (requires backend running)
npm run dev
# Visit http://localhost:3000/town-v2/demo
# Verify: citizens render, events stream, citizen selection works
```

All tests must pass and manual verification complete before proceeding.

---

## Implementation Tasks

### Task 5.1: Remove Legacy Town Files

Delete the old Zustand-based implementations:

```bash
cd impl/claude/web

# Remove old page
rm src/pages/Town.tsx

# Remove old components
rm src/components/town/Mesa.tsx
rm src/components/town/CitizenPanel.tsx

# Remove old hook
rm src/hooks/useTownStream.ts

# Remove old tests
rm tests/unit/components/Mesa.test.tsx
rm tests/unit/components/CitizenPanel.test.tsx
```

### Task 5.2: Rename V2 Files to Primary

```bash
cd impl/claude/web

# Rename page
mv src/pages/TownV2.tsx src/pages/Town.tsx

# Rename components
mv src/components/town/MesaV2.tsx src/components/town/Mesa.tsx
mv src/components/town/CitizenPanelV2.tsx src/components/town/CitizenPanel.tsx

# Rename tests
mv tests/unit/pages/TownV2.test.tsx tests/unit/pages/Town.test.tsx
mv tests/unit/components/MesaV2.test.tsx tests/unit/components/Mesa.test.tsx
mv tests/unit/components/CitizenPanelV2.test.tsx tests/unit/components/CitizenPanel.test.tsx
```

### Task 5.3: Update Imports in Renamed Files

**File:** `src/pages/Town.tsx` (was TownV2.tsx)

```typescript
// Update component imports
import { Mesa } from '@/components/town/Mesa';           // was MesaV2
import { CitizenPanel } from '@/components/town/CitizenPanel';  // was CitizenPanelV2

// Update export name
export default function Town() {  // was TownV2
```

**File:** `src/components/town/Mesa.tsx` (was MesaV2.tsx)

```typescript
// Update export
export function Mesa({...}) {  // was MesaV2
export default Mesa;           // was MesaV2
```

**File:** `src/components/town/CitizenPanel.tsx` (was CitizenPanelV2.tsx)

```typescript
// Update export
export function CitizenPanel({...}) {  // was CitizenPanelV2
export default CitizenPanel;           // was CitizenPanelV2
```

### Task 5.4: Update App.tsx Routes

**File:** `src/App.tsx`

```typescript
// Remove TownV2 import
const Town = lazy(() => import('./pages/Town'));
// DELETE: const TownV2 = lazy(() => import('./pages/TownV2'));

// Update routes - remove /town-v2 route
<Route element={<Layout />}>
  <Route path="/town/:townId" element={<Town />} />
  {/* DELETE: <Route path="/town-v2/:townId" element={<TownV2 />} /> */}
  <Route path="/town/:townId/inhabit/:citizenId" element={<Inhabit />} />
  ...
</Route>
```

### Task 5.5: Update Test File Imports

**File:** `tests/unit/pages/Town.test.tsx` (was TownV2.test.tsx)

```typescript
// Update imports
import Town from '@/pages/Town';  // was TownV2

// Update describe block
describe('Town', () => {  // was TownV2
```

**File:** `tests/unit/components/Mesa.test.tsx` (was MesaV2.test.tsx)

```typescript
import { Mesa } from '@/components/town/Mesa';  // was MesaV2

describe('Mesa', () => {  // was MesaV2
```

**File:** `tests/unit/components/CitizenPanel.test.tsx` (was CitizenPanelV2.test.tsx)

```typescript
import { CitizenPanel } from '@/components/town/CitizenPanel';  // was CitizenPanelV2

describe('CitizenPanel', () => {  // was CitizenPanelV2
```

### Task 5.6: Remove Zustand Town Store

**File:** `src/stores/townStore.ts`

Delete entirely:
```bash
rm src/stores/townStore.ts
```

### Task 5.7: Check for Remaining townStore References

```bash
# Search for any remaining useTownStore references
grep -r "useTownStore" src/ --include="*.ts" --include="*.tsx"
grep -r "townStore" src/ --include="*.ts" --include="*.tsx"

# Should only find:
# - Nothing (ideal)
# - Or comments/documentation mentioning the old pattern
```

If any files still import `useTownStore`, update them to use local state or `useTownStreamWidget`.

### Task 5.8: Remove Zustand/Immer Dependencies (Optional)

Only if `userStore.ts` and `uiStore.ts` can also be migrated:

```bash
# Check what still uses zustand
grep -r "from 'zustand'" src/ --include="*.ts" --include="*.tsx"
grep -r "from 'immer'" src/ --include="*.ts" --include="*.tsx"
```

If only `userStore.ts` and `uiStore.ts` remain:
- Keep zustand for now (auth state benefits from persistence)
- OR migrate them to React Context + local storage

If nothing uses zustand:
```bash
npm uninstall zustand immer
```

And remove from `main.tsx`:
```typescript
// DELETE these lines if zustand removed
import { enableMapSet } from 'immer';
enableMapSet();
```

### Task 5.9: Update README

**File:** `README.md`

Remove migration status section, update architecture:

```markdown
## Architecture

### Widget-Based Rendering

The Agent Town frontend uses a widget-based architecture:

1. **Backend emits widget JSON** via SSE (`live.state` events)
2. **`useTownStreamWidget` hook** consumes the JSON stream
3. **Widget components** render from JSON (type-discriminated union)

### Key Files

| File | Purpose |
|------|---------|
| `src/hooks/useTownStreamWidget.ts` | Widget SSE streaming hook |
| `src/reactive/types.ts` | Widget JSON type definitions |
| `src/reactive/WidgetRenderer.tsx` | Type-discriminated dispatcher |
| `src/widgets/` | Widget component implementations |
| `src/pages/Town.tsx` | Widget-based Town page |
| `src/components/town/Mesa.tsx` | Props-based Mesa canvas |
| `src/components/town/CitizenPanel.tsx` | Props-based citizen panel |
```

---

## Verification Commands

```bash
cd impl/claude/web

# 1. Run all tests
npm test -- --run

# 2. TypeScript check (should have 0 errors in our files)
npm run typecheck

# 3. Verify no zustand in Town-related code
grep -r "useTownStore" src/ --include="*.ts" --include="*.tsx"
# Should return empty

# 4. Verify imports are correct
grep -r "MesaV2\|CitizenPanelV2\|TownV2" src/ --include="*.ts" --include="*.tsx"
# Should return empty

# 5. Build check
npm run build

# 6. Dev server test
npm run dev
# Visit http://localhost:3000/town/demo
# Verify everything works as before
```

---

## Acceptance Criteria

1. **No V2 suffixes remain**: All files renamed, no `TownV2`, `MesaV2`, `CitizenPanelV2` references
2. **No legacy files**: Old `Town.tsx`, `Mesa.tsx`, `CitizenPanel.tsx`, `useTownStream.ts` deleted
3. **No townStore.ts**: File deleted, no `useTownStore` imports anywhere
4. **Single route**: Only `/town/:townId` exists, no `/town-v2/:townId`
5. **All tests pass**: Including renamed test files
6. **TypeScript passes**: No errors in modified files
7. **Build succeeds**: `npm run build` completes without errors
8. **README updated**: Reflects final architecture without migration notes

---

## Files to Delete

| File | Reason |
|------|--------|
| `src/pages/Town.tsx` | Replaced by TownV2 (after rename) |
| `src/components/town/Mesa.tsx` | Replaced by MesaV2 (after rename) |
| `src/components/town/CitizenPanel.tsx` | Replaced by CitizenPanelV2 (after rename) |
| `src/hooks/useTownStream.ts` | Replaced by useTownStreamWidget |
| `src/stores/townStore.ts` | No longer needed |
| `tests/unit/components/Mesa.test.tsx` | Old tests |
| `tests/unit/components/CitizenPanel.test.tsx` | Old tests |

## Files to Rename

| From | To |
|------|-----|
| `src/pages/TownV2.tsx` | `src/pages/Town.tsx` |
| `src/components/town/MesaV2.tsx` | `src/components/town/Mesa.tsx` |
| `src/components/town/CitizenPanelV2.tsx` | `src/components/town/CitizenPanel.tsx` |
| `tests/unit/pages/TownV2.test.tsx` | `tests/unit/pages/Town.test.tsx` |
| `tests/unit/components/MesaV2.test.tsx` | `tests/unit/components/Mesa.test.tsx` |
| `tests/unit/components/CitizenPanelV2.test.tsx` | `tests/unit/components/CitizenPanel.test.tsx` |

## Files to Modify

| File | Changes |
|------|---------|
| `src/App.tsx` | Remove TownV2 import and route |
| `src/pages/Town.tsx` | Update imports and export name |
| `src/components/town/Mesa.tsx` | Update export name |
| `src/components/town/CitizenPanel.tsx` | Update export name |
| `tests/unit/pages/Town.test.tsx` | Update imports and describe blocks |
| `tests/unit/components/Mesa.test.tsx` | Update imports and describe blocks |
| `tests/unit/components/CitizenPanel.test.tsx` | Update imports and describe blocks |
| `README.md` | Remove migration notes, finalize architecture docs |

---

## Notes

- **Inhabit page**: Still uses `useTownStore` for some state - may need separate migration
- **userStore.ts**: Keep for auth/tier state (useful with zustand persistence)
- **uiStore.ts**: Keep for modal/notification state
- **Zustand removal**: Only remove if ALL stores can be migrated; partial removal breaks immer plugin

---

## Dependencies

- Phase 4 complete (TownV2, MesaV2, CitizenPanelV2 exist and tests pass)
- TownV2 manually verified working with real backend
- No blockers from other features depending on old Town implementation
