# UX Flow: Workspace

> *"The K-Block is not where you edit a document. It's where you edit a possible world."*

**Status**: Active Plan
**Date**: 2026-01-17
**Specs**: k-block.md, severe-stark.md, layout-sheaf.md
**Principles**: Composable, Tasteful, Joy-Inducing

---

## The Problem We're Solving

Traditional document editors:
- Single view (prose OR code, not both)
- Immediate save (no transactional isolation)
- No derivation visibility
- No connection to system of meaning

**The Workspace provides hyperdimensional editing of K-Blocks in a Constitutional Graph.**

---

## The Workspace Philosophy

| Traditional | kgents Workspace |
|-------------|------------------|
| File browser | Constitutional Navigator |
| Single pane | K-Block + Views + Graph |
| Auto-save | Monadic isolation → explicit commit |
| Orphan edits | Every edit witnessed |
| Flat structure | Derivation trails visible |

---

## The Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: logo │ contexts │ ──────────────── │ user │ density │ garden%          │
├──────┬───────────────────────────────────────────────────────────────────┬──────┤
│      │                                                                   │      │
│ NAV  │                        K-BLOCK                                    │ META │
│      │                                                                   │      │
│ ─────│                                                                   │ ─────│
│      │  ┌─────────────────────────────────────────────────────────────┐  │      │
│ TREE │  │                                                             │  │COLL- │
│      │  │   Prose / Graph / Code / Diff                               │  │APSE  │
│      │  │                                                             │  │      │
│      │  │                                                             │  │ ─────│
│      │  │                                                             │  │      │
│      │  │                                                             │  │GARDEN│
│      │  │                                                             │  │      │
│      │  └─────────────────────────────────────────────────────────────┘  │      │
│      │                                                                   │      │
├──────┴───────────────────────────────────────────────────────────────────┴──────┤
│ STATUS: path │ mode │ isolation │ garden% │ slop │ connection │ hints          │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Panel Descriptions

| Panel | Purpose | Key Features |
|-------|---------|--------------|
| **HEADER** | Global context | Contexts (world/self/concept/void/time), density toggle, garden health |
| **NAV** | Constitutional navigation | Tree of K-Blocks, layer filters, search |
| **K-BLOCK** | Primary editing area | Content with view tabs (Prose/Graph/Code/Diff) |
| **META** | Collapse state + garden | TypeScript/Tests/Constitution scores, garden lifecycle |
| **STATUS** | System state | Path, mode, isolation state, connection, keyboard hints |

---

## Navigation Flow

### Constitutional Tree

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ NAV                                                                          │
│ ─────────────────────────────────────────────────────────────────────────────│
│                                                                              │
│ 🔍 Search K-Blocks...                                                        │
│                                                                              │
│ ┌─ L0: ZERO SEED ────────────────────────────────────────────────────────┐   │
│ │  ◉ A1: Entity                                                          │   │
│ │  ◉ A2: Morphism                                                        │   │
│ │  ◉ A3: Mirror                                                          │   │
│ │  ◉ G: Galois                                                           │   │
│ └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─ L1: KERNEL ───────────────────────────────────────────────────────────┐   │
│ │  ├─ Compose                                                            │   │
│ │  ├─ Judge                                                              │   │
│ │  ├─ Ground                                                             │   │
│ │  ├─ Id                                                                 │   │
│ │  ├─ Contradict                                                         │   │
│ │  ├─ Sublate                                                            │   │
│ │  └─ Fix                                                                │   │
│ └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─ L2: PRINCIPLES ───────────────────────────────────────────────────────┐   │
│ │  ├─ TASTEFUL          ◀── selected                                     │   │
│ │  ├─ CURATED                                                            │   │
│ │  ├─ ETHICAL                                                            │   │
│ │  ├─ JOY_INDUCING                                                       │   │
│ │  ├─ COMPOSABLE                                                         │   │
│ │  ├─ HETERARCHICAL                                                      │   │
│ │  └─ GENERATIVE                                                         │   │
│ └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─ L3: ARCHITECTURE ─────────────────────────────────────────────────────┐   │
│ │  ...                                                                   │   │
│ └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│ ┌─ MY GRAPH ─────────────────────────────────────────────────────────────┐   │
│ │  ├─ specs/                                                             │   │
│ │  │  └─ witness.md (14 K-Blocks)                                        │   │
│ │  └─ ideas/                                                             │   │
│ │     └─ alive-software (1 K-Block)                                      │   │
│ └────────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Navigation Modes**:
- **hjkl/arrows**: Move selection
- **Enter**: Open K-Block in editor
- **Space**: Expand/collapse section
- **/**: Focus search
- **gL**: Go to layer (g0 = L0, g1 = L1, etc.)

### Derivation Trail

When viewing a K-Block, its derivation trail is always visible:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ DERIVATION TRAIL                                                             │
│ ─────────────────────────────────────────────────────────────────────────────│
│                                                                              │
│ A2:Morphism → Compose → COMPOSABLE → ▶ TASTEFUL                              │
│       ↑                                   ↑                                  │
│   [L0]                               [selected]                              │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Click any node in the trail → navigate to that K-Block.

---

## K-Block Editing Flow

### View Tabs

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Prose] [Graph] [Code] [Diff]                          L = 0.08 │ CATEGORICAL│
│ ─────────────────────────────────────────────────────────────────────────────│
```

| View | Description | Editable |
|------|-------------|----------|
| **Prose** | Markdown rendering | Yes |
| **Graph** | Concept DAG with edges | Yes (structure) |
| **Code** | TypeSpec / implementation | Yes |
| **Diff** | Delta from base | No |

**Bidirectional Sync**: Edit in any view → all views update.

### Isolation States

The K-Block has isolation states visible in status line:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ STATUS: self.constitution.tasteful │ EDIT │ 🔒 ISOLATED │ 🌱 85% │ ● Online    │
└──────────────────────────────────────────────────────────────────────────────┘
```

| State | Icon | Meaning |
|-------|------|---------|
| PRISTINE | ✓ | No local changes |
| ISOLATED | 🔒 | Has uncommitted changes (safe) |
| STALE | ⚠ | Upstream changed |
| CONFLICTING | ⚡ | Both local and upstream changes |
| ENTANGLED | 🔗 | Linked to another K-Block |

### Harness Operations

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ HARNESS: [💾 Save] [✗ Discard] [⎇ Fork] [📍 Checkpoint] [↺ Rewind]           │
└──────────────────────────────────────────────────────────────────────────────┘
```

| Operation | Shortcut | Description |
|-----------|----------|-------------|
| Save | `Cmd+S` | Commit to cosmos (triggers effects) |
| Discard | `Cmd+D` | Abandon without saving |
| Fork | `Cmd+F` | Create parallel editing universe |
| Checkpoint | `Cmd+P` | Create named restore point |
| Rewind | `Cmd+R` | Restore to checkpoint |

---

## Collapse Panel

Shows K-Block health metrics:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ COLLAPSE                                                                     │
│ ─────────────────────────────────────────────────────────────────────────────│
│                                                                              │
│ TypeScript    ✓ pass                                                         │
│ Tests         ✓ pass (12/12)                                                 │
│ Constitution  6.5/7                                                          │
│   TASTEFUL ─────────▓▓▓▓▓▓▓▓▓░ 0.9                                           │
│   CURATED  ─────────▓▓▓▓▓▓▓░░░ 0.7                                           │
│   ETHICAL  ─────────▓▓▓▓▓▓▓▓▓▓ 1.0                                           │
│   JOY      ─────────▓▓▓▓▓▓▓▓░░ 0.8                                           │
│   COMPOSE  ─────────▓▓▓▓▓▓▓▓▓▓ 1.0                                           │
│   HETERAR  ─────────▓▓▓▓▓▓▓▓░░ 0.8                                           │
│   GENERAT  ─────────▓▓▓▓▓▓▓▓▓░ 0.9                                           │
│                                                                              │
│ Galois       L = 0.08 │ CATEGORICAL                                          │
│                                                                              │
│ Slop Risk    LOW                                                             │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Garden Panel

Shows K-Block lifecycle:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ GARDEN                                                                 85%   │
│ ─────────────────────────────────────────────────────────────────────────────│
│                                                                              │
│ NEEDS TENDING (3)                                                            │
│ ├─ 🥀 witness.md             12 days stale                    [Tend]         │
│ ├─ 🌿 k-block.md             5 days since activity            [Tend]         │
│ └─ 🌱 ideas/alive            just planted                     [Tend]         │
│                                                                              │
│ THRIVING (22)                                                                │
│ └─ Constitutional Graph (all nodes healthy)                                  │
│                                                                              │
│ READY TO COMPOST (1)                                                         │
│ └─ 💀 old-spec.md            90 days stale                    [Compost]      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Garden States**:
| State | Icon | Days Since Activity |
|-------|------|---------------------|
| Seed | 🌱 | 0-3 |
| Sprout | 🌿 | 3-7 |
| Bloom | 🌸 | Active |
| Wilt | 🥀 | 7-30 |
| Compost | 💀 | 30+ |

---

## Modes

The workspace has three modes:

| Mode | Purpose | Indicators |
|------|---------|------------|
| **NAVIGATE** | Move through graph | hjkl moves selection |
| **EDIT** | Modify K-Block content | Insert mode, cursor in editor |
| **COMMAND** | Execute operations | `:` prefix, command palette |

Mode visible in status line:

```
│ STATUS: path │ ▶ NAVIGATE │ ...
│ STATUS: path │ ✎ EDIT │ ...
│ STATUS: path │ : COMMAND │ ...
```

**Mode Transitions**:
- `i` in NAVIGATE → EDIT
- `Esc` in EDIT → NAVIGATE
- `:` in NAVIGATE → COMMAND
- `Enter/Esc` in COMMAND → NAVIGATE

---

## Implementation Notes

### Component Structure

```tsx
// pages/WorkspacePage.tsx
export function WorkspacePage() {
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [mode, setMode] = useState<'navigate' | 'edit' | 'command'>('navigate');
  const { kblock, isolation, harness } = useKBlock(selectedPath);

  return (
    <div className="workspace-page">
      <WorkspaceHeader />

      <main className="workspace-main">
        <NavigationPanel
          selectedPath={selectedPath}
          onSelect={setSelectedPath}
        />

        <KBlockPanel
          kblock={kblock}
          isolation={isolation}
          mode={mode}
          onModeChange={setMode}
          harness={harness}
        />

        <MetaPanel kblock={kblock} />
      </main>

      <StatusLine
        path={selectedPath}
        mode={mode}
        isolation={isolation}
      />
    </div>
  );
}
```

### Keyboard Handler

```tsx
// hooks/useWorkspaceKeys.ts
export function useWorkspaceKeys(mode: Mode, handlers: Handlers) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (mode === 'navigate') {
        switch (e.key) {
          case 'h': handlers.moveLeft(); break;
          case 'j': handlers.moveDown(); break;
          case 'k': handlers.moveUp(); break;
          case 'l': handlers.moveRight(); break;
          case 'Enter': handlers.openSelected(); break;
          case 'i': handlers.enterEdit(); break;
          case ':': handlers.enterCommand(); break;
        }
      } else if (mode === 'edit') {
        if (e.key === 'Escape') handlers.exitEdit();
      } else if (mode === 'command') {
        if (e.key === 'Enter') handlers.executeCommand();
        if (e.key === 'Escape') handlers.exitCommand();
      }
    };

    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [mode, handlers]);
}
```

---

## Witnessing

Every workspace action is witnessed:

| Action | Mark Tag |
|--------|----------|
| Navigate to K-Block | `workspace.navigate` |
| Edit K-Block | `workspace.edit` |
| Save K-Block | `workspace.save` |
| Discard K-Block | `workspace.discard` |
| Fork K-Block | `workspace.fork` |
| Checkpoint | `workspace.checkpoint` |
| View switch | `workspace.view` |

---

## Success Criteria

| Metric | Target |
|--------|--------|
| Time to navigate to any K-Block | < 3 clicks |
| Time to switch views | < 100ms |
| Edit → Save latency | < 500ms |
| Mode switch latency | < 50ms |

---

*"The K-Block is not where you edit a document. It's where you edit a possible world."*
