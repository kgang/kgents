# Graph Primitive Wiring Summary

**Date**: 2025-12-24
**Status**: COMPLETE

## What Was Done

Wired the existing Hypergraph editor into the new primitives structure by creating a clean re-export layer at `primitives/Graph/`.

## Files Created

```
impl/claude/web/src/primitives/Graph/
├── index.ts          (183 lines - re-exports from hypergraph/)
└── README.md         (357 lines - comprehensive documentation)
```

## Key Decisions

### 1. Re-Export Strategy (Not Move)

**Decision**: Re-export from existing `hypergraph/` directory rather than moving files.

**Reasoning**:
- Hypergraph code is already excellent and well-organized
- Moving would risk breaking existing imports
- Would lose git history
- Would disrupt ongoing development

**Implementation**:
```typescript
// primitives/Graph/index.ts
export { HypergraphEditor } from '../../hypergraph/HypergraphEditor';
export { useNavigation } from '../../hypergraph/useNavigation';
// ... etc
```

### 2. What Gets Exported

**Core exports**:
- `HypergraphEditor` - Main component
- `useNavigation` - State management
- `useKeyHandler` - Vim-like keybindings
- `useKBlock` - Isolation layer
- `useCommandRegistry` - Cmd+K palette
- `useGraphNode` - API bridge

**Types**:
- `EditorMode`, `GraphNode`, `Edge`, `NavigationState`
- `Command` (from useCommandRegistry, not state/types to avoid duplication)

**UI Components** (optional):
- `StatusLine`, `CommandLine`, `CommandPalette`, `FileExplorer`
- `ProofPanel`, `ProofStatusBadge` (Zero Seed integration)

### 3. Documentation Strategy

Created comprehensive `README.md` that:
- Documents the 6-mode modal editing system
- Explains graph navigation patterns
- Describes K-Block isolation
- Lists reusable patterns for potential extraction
- Shows usage examples
- Explains why we re-export rather than move

## Reusable Patterns Identified

These patterns could be extracted for use elsewhere:

1. **Declarative Keybinding System** (`useKeyHandler`)
   - Registry-based (not scattered event handlers)
   - Mode-specific filtering
   - Sequence handling (g-prefix, z-prefix)
   - Could power any modal interface

2. **K-Block Isolation Pattern** (`useKBlock`)
   - Edit → Crystallize → Commit workflow
   - Could be used for "draft mode" in other features
   - Already supports file and dialogue modes

3. **Command Palette System** (`useCommandRegistry`)
   - Cmd+K universal command search
   - Recency tracking with localStorage
   - Could be app-wide (not just graph-specific)

## Verification

### Type Safety
- No TypeScript errors specific to Graph primitive
- Duplicate `Command` type export resolved (kept from useCommandRegistry)
- All re-exports compile successfully

### Backward Compatibility
- Existing imports from `hypergraph/` still work
- No breaking changes to `HypergraphEditorPage.tsx` or other consumers
- Git history preserved in original files

### Structure
```
primitives/Graph/
  index.ts       - 183 lines (clean re-export layer)
  README.md      - 357 lines (comprehensive docs)

hypergraph/       - Original files untouched
  HypergraphEditor.tsx
  useNavigation.ts
  useKeyHandler.ts
  useKBlock.ts
  ... etc
```

## Usage

### Before (still works)
```typescript
import { HypergraphEditor } from '../hypergraph';
```

### After (new primitive API)
```typescript
import { HypergraphEditor } from '@/primitives/Graph';
```

Both import paths work - no migration required for existing code.

## Next Steps (Optional)

1. **Extract useKeyHandler** to `primitives/Modal/useKeyHandler.ts`
   - Make it generic (not graph-specific)
   - Could power chat command mode, global shortcuts, etc.

2. **Extract useCommandRegistry** to `primitives/Command/useCommandRegistry.ts`
   - Make it app-wide
   - Extend with categories for different domains

3. **Extract K-Block pattern** to `primitives/Isolation/useIsolation.ts`
   - Generalize beyond files/dialogue
   - Could be used for any "possible world" editing

4. **Migrate existing imports** (when ready)
   - Update `HypergraphEditorPage.tsx` to use `primitives/Graph`
   - Update other consumers
   - Keep both import paths working during migration

## Files Modified

- Created: `impl/claude/web/src/primitives/Graph/index.ts`
- Created: `impl/claude/web/src/primitives/Graph/README.md`
- Created: `impl/claude/web/GRAPH_PRIMITIVE_WIRING.md` (this file)

## No Breaking Changes

- All existing code continues to work
- Original hypergraph/ files untouched
- No files moved or deleted
- Purely additive change

---

**Tasteful > feature-complete**: This is minimal, intentional work that creates a clean entry point without disrupting the excellent code that already exists.
