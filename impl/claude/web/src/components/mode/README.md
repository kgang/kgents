# Mode System

Six-mode editing system for hypergraph editing (vim-inspired modal editing).

## Modes

| Mode | Trigger | Color | Purpose |
|------|---------|-------|---------|
| **NORMAL** | `Escape` | Steel | Navigate, select, invoke commands (default) |
| **INSERT** | `i` | Moss | Create new K-Blocks (nodes) |
| **EDGE** | `e` | Amber | Create relationships (edges) between nodes |
| **VISUAL** | `v` | Sage | Multi-select for batch operations |
| **COMMAND** | `:` | Rust | Execute slash commands |
| **WITNESS** | `w` | Gold | Commit changes with witness marks |

## Usage

### 1. Wrap app with ModeProvider

```tsx
// In App.tsx or AppShell.tsx
import { ModeProvider } from '@/context/ModeContext';

function App() {
  return (
    <ModeProvider>
      <YourApp />
    </ModeProvider>
  );
}
```

### 2. Add ModeIndicator

```tsx
// In AppShell or HypergraphEditor
import { ModeIndicator } from '@/components/mode';

function AppShell() {
  return (
    <div>
      {/* Your content */}
      <ModeIndicator />
    </div>
  );
}
```

### 3. Use mode in components

```tsx
import { useMode } from '@/hooks';

function KBlockEditor() {
  const { mode, isInsert, toNormal } = useMode();

  if (!isInsert) {
    return null; // Only render in INSERT mode
  }

  return (
    <div>
      <h2>Create K-Block</h2>
      <button onClick={toNormal}>Cancel (Esc)</button>
    </div>
  );
}
```

## Keyboard Bindings

From **NORMAL** mode:
- `i` → INSERT mode
- `e` → EDGE mode
- `v` → VISUAL mode
- `:` → COMMAND mode
- `w` → WITNESS mode

From **any** mode:
- `Escape` → NORMAL mode (always)

## Mode-Specific Behavior

### INSERT Mode
- Captures keyboard input
- Create K-Blocks (nodes in hypergraph)
- Escape to cancel and return to NORMAL

### EDGE Mode
- Click two nodes to create edge
- Visual feedback during edge creation
- Escape to cancel

### VISUAL Mode
- Multi-select nodes
- Batch operations (delete, tag, export)
- Escape to deselect and return to NORMAL

### COMMAND Mode
- Captures keyboard input
- Slash commands (`:save`, `:export`, etc.)
- Escape to cancel

### WITNESS Mode
- Captures keyboard input
- Commit changes with witness marks
- Blocks navigation until committed
- Escape to cancel

## Examples

### Modal component that respects mode

```tsx
function EdgeCreator() {
  const { isEdge, toNormal, color } = useMode();

  if (!isEdge) return null;

  return (
    <div style={{ borderColor: color }}>
      <p>Click two nodes to create edge</p>
      <button onClick={toNormal}>Cancel</button>
    </div>
  );
}
```

### Disable keyboard shortcuts in input mode

```tsx
function MyComponent() {
  const { capturesInput } = useMode();

  useKeyboardShortcuts({
    enabled: !capturesInput, // Disable when mode captures input
    shortcuts: [...],
  });
}
```

### History tracking

```tsx
function ModeHistory() {
  const { history } = useMode();

  return (
    <ul>
      {history.map((t, i) => (
        <li key={i}>
          {t.from} → {t.to} ({t.reason})
        </li>
      ))}
    </ul>
  );
}
```

## Architecture

```
types/mode.ts              # Mode types, definitions, utilities
  ↓
context/ModeContext.tsx    # React context + provider + keyboard handling
  ↓
hooks/useMode.ts           # Convenient hook with shortcuts
  ↓
components/mode/ModeIndicator.tsx  # Visual indicator
```

## Integration with Hypergraph Editor

The mode system should be integrated at the HypergraphEditor level:

```tsx
// In HypergraphEditor.tsx
import { ModeProvider } from '@/context/ModeContext';
import { ModeIndicator } from '@/components/mode';
import { useMode } from '@/hooks';

export function HypergraphEditor() {
  return (
    <ModeProvider initialMode="NORMAL">
      <HypergraphCanvas />
      <ModeIndicator />
    </ModeProvider>
  );
}

function HypergraphCanvas() {
  const { mode, isInsert, isEdge, isVisual } = useMode();

  // Render different UI based on mode
  return (
    <div>
      {isInsert && <KBlockCreator />}
      {isEdge && <EdgeCreator />}
      {isVisual && <MultiSelector />}
      {/* ... */}
    </div>
  );
}
```

## N-03 Compliance

**N-03: Escape ALWAYS returns to NORMAL**

This is enforced at the ModeContext level:
- Escape key handler is registered globally
- Always transitions to NORMAL, regardless of current mode
- No mode can override or prevent Escape behavior
- Implemented in `ModeProvider` effect hook

See: `context/ModeContext.tsx` line 85-90
