# Hook Consolidation Report - Phase 4

**Date:** 2025-12-23
**Session:** Phase 4 - Consolidate Duplicate Hooks

---

## Executive Summary

Audited all hooks in `src/hooks/` and `src/hypergraph/` for duplicates. Found ONE duplicate (`useKBlock`), deleted the orphaned version, and documented the canonical locations for all hooks.

---

## Findings

### 1. useKBlock - DUPLICATE (RESOLVED)

**Three versions existed:**

1. **`src/hooks/useKBlock.ts`** (17KB, 625 lines) - DELETED (this session)
   - Exported: `useKBlock()` (dialogue), `useFileKBlock()` (file)
   - Two separate function implementations
   - **NOT imported anywhere** - completely orphaned

2. **`src/membrane/useKBlock.ts`** - DELETED (previous session)
   - Already removed in earlier cleanup
   - Was being re-exported through `src/membrane/index.ts`

3. **`src/hypergraph/useKBlock.ts`** (28KB, 966 lines) - CANONICAL
   - Exported: `useKBlock()` (unified), `useFileKBlock()`, `useDialogueKBlock()`
   - Single unified implementation with backward-compatible wrappers
   - Feature-complete:
     - AbortController for race condition prevention
     - Checkpoint/rewind support (file K-Blocks)
     - Analysis status tracking (Sovereign integration)
     - Unified dialogue + file K-Block handling
   - Imported by:
     - `src/membrane/index.ts` (re-exported)
     - `src/hypergraph/HypergraphEditor.tsx` (direct use)

**Resolution:**
- Deleted `src/hooks/useKBlock.ts` (orphaned version, this session)
- `src/membrane/useKBlock.ts` was already deleted in a previous session

---

### 2. useGraphNode - NO DUPLICATE

**Single version:**
- **Location:** `src/hypergraph/useGraphNode.ts`
- **Purpose:** Bridge between WitnessedGraph API and Hypergraph types
- **Features:**
  - Witnessed edges (linked to marks via mark_id)
  - Evidence-based navigation (confidence, context, line numbers)
  - Origin tracking (which source contributed edge)
  - Update polling (5-second interval)
- **Exported via:**
  - `src/hypergraph/index.ts`
  - `src/membrane/index.ts` (backward compatibility)
- **Used by:**
  - `src/pages/HypergraphEditorPage.tsx`

**Canonical location:** `src/hypergraph/useGraphNode.ts`

---

### 3. useSpecNavigation - DUPLICATE (RESOLVED)

**Two versions existed:**

1. **`src/membrane/useSpecNavigation.ts`** - DELETED (previous session)
   - Already removed in earlier cleanup
   - Was being re-exported through `src/membrane/index.ts`

2. **`src/hypergraph/useSpecNavigation.ts`** - CANONICAL
   - **Purpose:** Navigate the SpecGraph hypergraph via AGENTESE `concept.specgraph.*`
   - **Exports multiple hooks:**
     - `useSpecGraph()` - Discovery and manifest
     - `useSpecQuery()` - Query individual specs
     - `useSpecEdges()` - Fetch edges for a spec
     - `useSpecNavigate()` - Navigate via edges (extends, implements, tests)
   - **Exported via:**
     - `src/hypergraph/index.ts`
     - `src/membrane/index.ts` (backward compatibility)
   - **Used by:**
     - Internal use within hypergraph components

**Resolution:** `src/membrane/useSpecNavigation.ts` was already deleted in a previous session

**Canonical location:** `src/hypergraph/useSpecNavigation.ts`

---

## Hook Taxonomy

### Hooks in `src/hooks/`

**Purpose:** Generic, reusable infrastructure hooks (NOT domain-specific).

**Categories:**
- **Async state:** `useAsyncState`
- **Streaming:** `useProjectedStream`, `useWitnessStream`
- **Performance:** `useBatchedEvents`
- **Layout:** `useLayoutContext`, `useWindowLayout`, `useLayoutMeasure`
- **Input:** `useKeyboardShortcuts`, `useTouchGestures`, `usePinchZoom`, `useLongPress`, `useSwipe`
- **Animation:** `useBreathing`, `useGrowing`, `useUnfurling`, `useFlowing`, `useSpringTilt`, `useTitleScatter`, `useVitalityOperad`
- **UI:** `useSimpleToast`, `useOnlineStatus`, `useQuoteRotation`
- **State machine:** `useDesignPolynomial`, `useAnimationCoordination`
- **Domain-specific:** `useTerrarium` (Brain page)

**Exports:** `src/hooks/index.ts` (barrel file)

---

### Hooks in `src/hypergraph/`

**Purpose:** Hypergraph-specific hooks (graph navigation, K-Block editing).

**Hooks:**
- `useKBlock` - K-Block lifecycle (dialogue + file editing)
- `useGraphNode` - WitnessedGraph API bridge
- `useSpecNavigation` - SpecGraph navigation (4 sub-hooks)
- `useNavigation` - Graph navigation state machine
- `useKeyHandler` - Vim-style modal key handling

**Exports:** `src/hypergraph/index.ts` (barrel file)

---

## Import Conventions

### For consumers importing hooks:

1. **Generic infrastructure hooks:**
   ```typescript
   import { useAsyncState, useBreathing, useWitnessStream } from '@/hooks';
   ```

2. **Hypergraph hooks:**
   ```typescript
   import { useKBlock, useGraphNode, useNavigation } from '@/hypergraph';
   ```

3. **Backward compatibility (membrane):**
   ```typescript
   // Still works, redirects to canonical location
   import { useKBlock, useWitnessStream } from '@/membrane';
   ```

---

## Consolidation Actions Taken

### This Session (2025-12-23):
1. **Deleted:** `src/hooks/useKBlock.ts` (orphaned, not imported anywhere)
2. **Kept canonical version:** `src/hypergraph/useKBlock.ts` (unified, feature-complete)

### Previous Session (already completed):
1. **Deleted:** `src/membrane/useKBlock.ts` (duplicate)
2. **Deleted:** `src/membrane/useSpecNavigation.ts` (duplicate)
3. **Deleted:** `src/membrane/useWitnessStream.ts` (moved to `src/hooks/`)

All deleted `membrane/` hooks are now re-exported through `src/membrane/index.ts` from their canonical locations.

---

## useGraphApi Hook - NOT CREATED

**Recommendation from original request:** Create `useGraphApi` to consolidate graph-related API calls.

**Assessment:** NOT NEEDED.

**Rationale:**
- `useGraphNode` already provides a clean API for graph operations:
  - `loadNode(path)` - Load node by path
  - `loadSiblings(node)` - Load siblings
  - Update polling and cache invalidation
- `useSpecNavigation` provides spec-specific navigation:
  - `useSpecGraph()` - Discovery and stats
  - `useSpecQuery()` - Query individual specs
  - `useSpecEdges()` - Fetch edges
  - `useSpecNavigate()` - Navigate via edges

**Conclusion:** Creating `useGraphApi` would introduce unnecessary abstraction. The existing hooks are well-scoped and composable.

---

## Verification

### Typecheck Status (Post-Consolidation)

```bash
npm run typecheck
```

**Result:** No new errors introduced by hook consolidation.

**Pre-existing errors:** Type errors in `src/hypergraph/*` files related to missing `./types` module (unrelated to this consolidation).

---

## Canonical Hook Locations (Reference)

| Hook | Canonical Location | Purpose |
|------|-------------------|---------|
| `useKBlock` | `src/hypergraph/useKBlock.ts` | K-Block lifecycle (dialogue + file) |
| `useFileKBlock` | `src/hypergraph/useKBlock.ts` | File K-Block (backward compat wrapper) |
| `useDialogueKBlock` | `src/hypergraph/useKBlock.ts` | Dialogue K-Block (backward compat wrapper) |
| `useGraphNode` | `src/hypergraph/useGraphNode.ts` | WitnessedGraph API bridge |
| `useSpecGraph` | `src/hypergraph/useSpecNavigation.ts` | SpecGraph discovery/manifest |
| `useSpecQuery` | `src/hypergraph/useSpecNavigation.ts` | Query individual specs |
| `useSpecEdges` | `src/hypergraph/useSpecNavigation.ts` | Fetch spec edges |
| `useSpecNavigate` | `src/hypergraph/useSpecNavigation.ts` | Navigate via edges |
| `useNavigation` | `src/hypergraph/useNavigation.ts` | Graph navigation state machine |
| `useKeyHandler` | `src/hypergraph/useKeyHandler.ts` | Vim-style modal key handling |
| `useWitnessStream` | `src/hooks/useWitnessStream.ts` | Witness event SSE streaming |
| `useAsyncState` | `src/hooks/useAsyncState.ts` | Async state management |
| `useDesignPolynomial` | `src/hooks/useDesignPolynomial.ts` | Design state machine |
| `useBreathing` | `src/hooks/useBreathing.ts` | Breathing animation primitive |
| All others | `src/hooks/` | Generic infrastructure |

---

## Recommendations

### 1. Update Exports (Low Priority)

The `src/membrane/index.ts` barrel file currently re-exports hooks for backward compatibility. This is acceptable but could be simplified in a future refactor:

- **Option A (Keep):** Maintain `membrane/` as a convenience barrel for commonly-used hooks.
- **Option B (Remove):** Force consumers to import directly from `hooks/` or `hypergraph/`.

**Current approach (Option A) is fine.** No action needed.

### 2. Fix Type Errors (Separate Task)

The typecheck reveals errors related to missing `./types` module in `src/hypergraph/`. This is a separate issue unrelated to hook consolidation.

**Next step:** Fix hypergraph type errors in a separate session.

---

## Summary

- **Duplicates found (this session):** 1 (`useKBlock` in `src/hooks/`)
- **Duplicates removed (this session):** 1 (`src/hooks/useKBlock.ts`)
- **Previously removed:** 3 (`src/membrane/useKBlock.ts`, `src/membrane/useSpecNavigation.ts`, `src/membrane/useWitnessStream.ts`)
- **Total duplicates eliminated:** 4 hooks across 2 sessions
- **Canonical versions:** All hooks now have a single, well-documented canonical location
- **Import paths:** Standardized via barrel files (`src/hooks/index.ts`, `src/hypergraph/index.ts`)
- **Backward compatibility:** Maintained via `src/membrane/index.ts`

**Status:** COMPLETE. No further consolidation needed.
