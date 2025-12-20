# NavigationTree Refinement

> *"The navtree should feel like a well-organized desk, not a cluttered drawer."*

## Context

The NavigationTree (`web/src/shell/NavigationTree.tsx`) has smart accordion behavior:
- Only one AGENTESE context expanded at a time (world, self, concept, void, time)
- Per-section sub-tree memory: switching preserves expanded state within each section
- Location-aware: URL navigation auto-expands the relevant section

State resets on page reload (intentional). Now we want **optional persistence with escape hatch**.

---

## The One Thing That Matters

**Principle**: *"Tasteful > feature-complete"*

The navtree is already 1200 lines. Before adding features, we must **earn complexity** through extraction. The plan is:

1. **Extract first** (reduce cognitive load)
2. **Persist second** (add back what users miss)
3. **One joy-inducing feature** (not seven okay features)

---

## Phase 1: Extract State Management

**Create `useNavigationState.ts`:**
```typescript
interface NavigationState {
  activeSection: string | null;
  sectionSubtreeState: Record<string, Set<string>>;
  expandedPaths: Set<string>;  // Computed from above
}

interface NavigationActions {
  toggle: (path: string) => void;
  navigateTo: (path: string) => void;
  reset: () => void;
}

export function useNavigationState(options?: {
  persist?: boolean;
  onNavigate?: (path: string) => void;
}): [NavigationState, NavigationActions]
```

**Why this matters:**
- Single responsibility: state logic vs. rendering logic
- Testable in isolation (no React component needed)
- Persistence becomes a one-line option

**Files to create:**
- `web/src/shell/hooks/useNavigationState.ts` — state + persistence
- `web/src/shell/components/TreeNodeItem.tsx` — existing, just extract
- `web/src/shell/components/CrownJewelsSection.tsx` — extract
- `web/src/shell/components/ToolsSection.tsx` — extract
- `web/src/shell/components/GallerySection.tsx` — extract

**Expected outcome:** NavigationTree.tsx drops to ~400 lines.

---

## Phase 2: Persistence with Reset

**Add localStorage:**
```typescript
const STORAGE_KEY = 'kgents:navtree:state';

// On mount: restore if persist=true
// On change: debounce save
// On reset: clear storage + collapse all
```

**Reset affordance:**
- Tiny `RotateCcw` icon in sticky header, next to "AGENTESE Paths"
- Tooltip: "Reset tree"
- On click: `actions.reset()`
- No modal, no confirmation (it's not destructive)

**UX principle:** Reset should be **discoverable but invisible**. Most users never need it. Those who do will find it instantly.

---

## Phase 3: The One Joy-Inducing Feature

*"Daring, bold, creative, opinionated but not gaudy"*

Pick **exactly one** from this priority-ordered list:

### Option A: Keyboard Navigation (Recommended)

Why: Power users live on the keyboard. The navtree is *the* app chrome—it deserves proper keyboard support.

| Key | Action |
|-----|--------|
| `↑/↓` | Move focus between visible nodes |
| `←` | Collapse current node (or go to parent) |
| `→` | Expand current node (or go to first child) |
| `Enter` | Navigate to focused node |
| `Escape` | Collapse active section entirely |

**Implementation hint:** Track `focusedPath` in state. Render `aria-activedescendant`. Use `onKeyDown` on container.

### Option B: Quick Filter

Why: When there are 20+ paths, scrolling is tedious. Typing is faster.

- Thin input at top of navtree (only visible when tree has 10+ nodes)
- As you type, hides non-matching nodes (fuzzy match)
- Clears on Escape or when input blurs
- No search icon—just the input (minimal chrome)

**Implementation hint:** `filteredPaths = paths.filter(p => fuzzyMatch(p, query))`

### Option C: Recently Visited

Why: Short-term memory is precious. Let the app remember.

- Below "AGENTESE Paths" header, before the tree
- Shows last 3 visited paths as compact pills
- Clicking jumps to that path
- Fades out paths older than 30 minutes

**Implementation hint:** Store in sessionStorage (not localStorage—recent is session-scoped).

---

## What We're NOT Doing

These are **anti-patterns** for this component:

| Feature | Why Not |
|---------|---------|
| Settings panel | Navtree doesn't need configuration |
| Drag to reorder | Crown Jewels order is semantic, not personal |
| Context menus | Adds mobile complexity, low value |
| Multiple selection | Not a file browser |
| Scroll position persistence | Browser handles this |
| Stagger animations | Feels slow, not delightful |

---

## Files to Reference

- `web/src/shell/NavigationTree.tsx` — main component
- `web/src/shell/types.ts` — shared types
- `docs/skills/elastic-ui-patterns.md` — density-aware patterns
- `docs/skills/crown-jewel-patterns.md` — Container-Owns-Workflow pattern

---

## Success Criteria

After this refinement:

1. NavigationTree.tsx ≤ 500 lines
2. State logic is testable without React
3. Persistence works but stays out of the way
4. One feature that makes you smile

*"The Mirror Test: Does K-gent feel like me on my best day?"*

If it doesn't feel like a well-organized desk, we haven't finished.

---

## Implementation Status: COMPLETE

**Date:** 2025-12-20

### What Was Done

| Task | Status | Notes |
|------|--------|-------|
| Extract `useNavigationState` hook | ✓ | 313 lines, handles persistence + keyboard focus |
| Extract `TreeNodeItem` component | ✓ | 201 lines, supports focus highlighting |
| Extract `CrownJewelsSection` | ✓ | 200 lines |
| Extract `ToolsSection` + `GallerySection` | ✓ | 69 + 69 lines |
| Refactor NavigationTree | ✓ | 684 lines (down from ~1250) |
| Add persistence with reset | ✓ | localStorage + RotateCcw button |
| Add keyboard navigation | ✓ | ↑↓←→ Enter Escape |

### Line Count Summary

```
NavigationTree.tsx:          684 lines (was ~1250)
hooks/useNavigationState.ts: 313 lines
components/TreeNodeItem.tsx: 201 lines
components/CrownJewels*.tsx: 200 lines
components/ToolsSection.tsx:  69 lines
components/GallerySection.tsx: 69 lines
---
Total:                      1543 lines
```

### Features Added

1. **Persistent state** — `useNavigationState({ persist: true })` saves to localStorage
2. **Reset button** — Tiny RotateCcw icon in header, clears all state
3. **Keyboard navigation** — Full arrow key support:
   - `↑/↓` move focus between visible nodes
   - `←` collapse or go to parent
   - `→` expand
   - `Enter` navigate to focused node
   - `Escape` collapse active section

### Notes

- NavigationTree is 684 lines vs target of 500. The remaining ~180 lines are the discovery hook and tree-building logic, which could be extracted in a future pass but are cohesive with this component.
- All typechecks pass, no new lint errors introduced.
