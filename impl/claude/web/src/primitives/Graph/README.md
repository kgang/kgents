# Graph Primitive

> "The file is a lie. There is only the graph."

## Overview

The Graph primitive provides a **modal hypergraph editor** with K-Block isolation. It's keeper code - already battle-tested and well-architected. This primitive re-exports from the existing `hypergraph/` directory rather than moving files, to preserve git history and minimize disruption.

## Core Capabilities

### 1. Six-Mode Modal Editing

| Mode | Purpose | Key Bindings |
|------|---------|-------------|
| **NORMAL** | Navigate the graph | `h/j/k/l` scroll, `gh/gl/gj/gk` graph nav, `?` help |
| **INSERT** | Edit content | Esc to exit, full CodeMirror editing |
| **EDGE** | Create/modify edges | `d` defines, `e` extends, `i` implements, `r` references |
| **VISUAL** | Select multiple nodes | (Future: multi-node operations) |
| **COMMAND** | Execute AGENTESE | `:` prefix, ex-style commands |
| **WITNESS** | Mark moments | `w` to enter, quick capture |

### 2. Graph Navigation

Navigation is **edge traversal**, not file paths:

```
gh - Go to parent (incoming edge or trail back)
gl - Go to child (outgoing edge, prompted if multiple)
gj - Go to next sibling
gk - Go to previous sibling
gd - Go to definition
gr - Go to references
gt - Go to tests
```

**Trail System**: Breadcrumb history persists navigation context.

**Portal Operations**: Fold/unfold subgraphs for focus:

```
zo - Open portal (unfold)
zc - Close portal (fold)
zO - Open all portals
zC - Close all portals
```

### 3. K-Block Isolation

> "You're never editing the 'real' thing. You're editing a possible world."

Every edit happens in **isolated K-Block workspace**:

1. **Enter INSERT mode** → Creates K-Block (if not exists)
2. **Edit freely** → Changes stay isolated
3. **Crystallize/Save** → Commits to cosmos (escapes isolation)
4. **Discard** → Abandons changes (no cosmic effects)

**Supports two modes**:
- **File K-Blocks**: Edit files in isolation
- **Dialogue K-Blocks**: Accumulate thoughts before crystallization

### 4. Declarative Keybindings

**Registry-based** system (not scattered event handlers):

```typescript
const BINDINGS: KeyBinding[] = [
  { key: 'j', mode: 'NORMAL', action: 'SCROLL_DOWN' },
  { key: 'k', mode: 'NORMAL', action: 'SCROLL_UP' },
  { key: 'gh', mode: 'NORMAL', action: 'GO_PARENT', isSequence: true },
  // ...
];
```

**Benefits**:
- Single source of truth
- Mode-specific filtering
- Sequence handling (g-prefix, z-prefix)
- Easy to audit and extend

## Architecture

```
HypergraphEditor (Main Component)
  ├── useNavigation       // State: current node, trail, mode
  ├── useKeyHandler       // Modal keybindings
  ├── useKBlock           // Isolation layer
  ├── useCommandRegistry  // Cmd+K palette
  └── Panes
      ├── Header          // Parent/child edge counts
      ├── TrailBar        // Breadcrumb navigation
      ├── ContentPane     // Node content (CodeMirror)
      └── EdgeGutters     // Left/right edge lists
```

### State Management

**NavigationState** (managed by `useNavigation`):

```typescript
interface NavigationState {
  currentNode: GraphNode | null;
  trail: Trail;
  cursor: Position;
  mode: EditorMode;
  kblock: KBlockState | null;
  // ...
}
```

**Actions** dispatch to reducer for predictable state transitions.

### K-Block Lifecycle

```
1. ENTER_INSERT → dispatch({ type: 'START_KBLOCK', path })
2. Edit content → kblock.content mutates
3. Crystallize  → POST /api/kblock/:id/crystallize
4. Discard      → DELETE /api/kblock/:id
```

## File Organization

```
impl/claude/web/src/hypergraph/
├── HypergraphEditor.tsx      // Main component
├── state/
│   ├── types.ts              // NavigationState, EditorMode, GraphNode
│   ├── reducer.ts            // State transitions
│   └── useEditorState.ts     // Derived state
├── useNavigation.ts          // State + convenience methods
├── useKeyHandler.ts          // Declarative keybindings
├── useKBlock.ts              // Isolation layer
├── useCommandRegistry.ts     // Cmd+K palette
├── useGraphNode.ts           // API bridge (load nodes)
├── panes/
│   ├── Header.tsx            // Edge counts, title
│   ├── TrailBar.tsx          // Breadcrumbs
│   ├── ContentPane.tsx       // CodeMirror wrapper
│   └── EdgeGutter.tsx        // Edge navigation
├── StatusLine.tsx            // Mode, position, path
├── CommandLine.tsx           // Ex-style command input
├── CommandPalette.tsx        // Cmd+K palette (cmdk)
├── FileExplorer.tsx          // File tree sidebar
├── ProofPanel.tsx            // Zero Seed integration
└── index.ts                  // Public exports
```

**Core files** (essential to understanding):
- `HypergraphEditor.tsx` - Main orchestration
- `state/types.ts` - Data model
- `state/reducer.ts` - State transitions
- `useNavigation.ts` - Primary hook
- `useKeyHandler.ts` - Keybinding system

**Support files** (can skim):
- Pane components (presentational)
- API hooks (data fetching)
- UI widgets (modals, panels)

## Reusable Patterns

These patterns could be extracted for use elsewhere:

### 1. Declarative Keybinding System

**Pattern**: `useKeyHandler` + `BINDINGS` registry

```typescript
const BINDINGS: KeyBinding[] = [
  { key: 'j', mode: 'NORMAL', action: 'SCROLL_DOWN' },
  { key: 'gh', mode: 'NORMAL', action: 'GO_PARENT', isSequence: true },
];

const actions = {
  SCROLL_DOWN: () => contentPaneRef.current?.scrollDown(),
  GO_PARENT: () => navigation.goParent(),
};

const keyHandler = useKeyHandler({
  mode: state.mode,
  bindings: BINDINGS,
  actions,
});
```

**Could power**:
- Any modal interface (e.g., chat with command mode)
- Global app shortcuts
- Context-sensitive keybindings

### 2. K-Block Isolation Pattern

**Pattern**: Edit → Crystallize → Commit

```typescript
const kblock = useKBlock({
  path: 'spec/protocols/witness.md',
  onCrystallize: (content) => saveToFile(content),
});

// Edit in isolation
kblock.setContent('...');

// Commit to cosmos
await kblock.crystallize();
```

**Could be used for**:
- Draft mode in chat (accumulate thoughts before sending)
- "Try it out" mode in any editor
- Speculative execution (roll back if fails)

### 3. Command Palette System

**Pattern**: `useCommandRegistry` + recency tracking

```typescript
const commands = [
  {
    id: 'nav:parent',
    label: 'Go to parent',
    category: 'navigation',
    execute: () => navigation.goParent(),
  },
  // ...
];

const registry = useCommandRegistry({ commands });
```

**Could be app-wide**:
- Not just graph-specific
- Global Cmd+K for all features
- Unified search/execute interface

## Usage

### Basic Example

```typescript
import { HypergraphEditor } from '@/primitives/Graph';

function HypergraphPage() {
  return (
    <HypergraphEditor
      initialPath="spec/protocols/witness.md"
      onNodeFocus={(node) => console.log('Focused:', node)}
      onNavigate={(path) => updateUrl(path)}
    />
  );
}
```

### Custom Layout (using panes directly)

```typescript
import {
  useNavigation,
  useKeyHandler,
  useKBlock,
  Header,
  ContentPane,
  StatusLine,
} from '@/primitives/Graph';

function CustomGraphView() {
  const navigation = useNavigation();
  const keyHandler = useKeyHandler({ /* ... */ });
  const kblock = useKBlock({ /* ... */ });

  return (
    <div>
      <Header node={navigation.state.currentNode} />
      <ContentPane node={navigation.state.currentNode} />
      <StatusLine mode={navigation.state.mode} />
    </div>
  );
}
```

### Integrating with Zero Seed

```typescript
import { HypergraphEditor } from '@/primitives/Graph';

function SpecEditor() {
  const navigateToZeroSeed = (tab?: string) => {
    // Navigate to Zero Seed page with optional tab
    router.push(`/zero-seed${tab ? `?tab=${tab}` : ''}`);
  };

  return (
    <HypergraphEditor
      initialPath="spec/protocols/zero-seed.md"
      onZeroSeed={navigateToZeroSeed}
    />
  );
}
```

## Why Re-Export (Not Move)?

The hypergraph code is **already excellent**. Moving it would:

1. **Risk breaking existing imports** - Many files import from `hypergraph/`
2. **Lose git history** - Harder to trace evolution of the code
3. **Disrupt ongoing development** - Active work depends on current structure

Instead, this primitive:

1. **Creates a clean entry point** - `primitives/Graph` is the public API
2. **Documents intent** - This README clarifies purpose and patterns
3. **Identifies reusable patterns** - Highlights what could be extracted
4. **Preserves flexibility** - Original files stay where they are

## Future Extractions

As the primitive library matures, consider extracting:

1. **`useKeyRegistry`** → `primitives/Modal/useKeyRegistry.ts`
   - Declarative keybinding system
   - Usable for any modal interface

2. **`useKBlock`** → `primitives/Isolation/useKBlock.ts`
   - Generalized isolation pattern
   - Already supports file and dialogue modes

3. **`useCommandRegistry`** → `primitives/Command/useCommandRegistry.ts`
   - App-wide command palette
   - Not specific to graph editing

## Testing

The hypergraph editor has existing tests in `hypergraph/__tests__/`. Key test categories:

1. **State transitions** - Reducer tests for all actions
2. **Keybinding resolution** - Mode-specific binding tests
3. **K-Block lifecycle** - Isolation/crystallization tests
4. **Graph navigation** - Edge traversal tests

Run tests:

```bash
cd impl/claude/web
npm run test -- hypergraph
```

## Related Documentation

- **Skill**: `docs/skills/hypergraph-editor.md` - Full implementation guide
- **Spec**: `spec/protocols/interactive-text.md` - Conceptual foundation
- **Examples**: `impl/claude/web/src/pages/HypergraphEditorPage.tsx` - Usage in app

---

*This is keeper code. Minimal changes, maximal preservation.*
