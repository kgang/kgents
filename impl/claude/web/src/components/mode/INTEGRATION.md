# Mode System Integration Guide

How to integrate the six-mode editing system into the Hypergraph Editor.

## Step 1: Wrap the Editor with ModeProvider

```tsx
// In HypergraphEditor.tsx or similar
import { ModeProvider } from '@/context/ModeContext';
import { ModeIndicator } from '@/components/mode';

export function HypergraphEditor() {
  return (
    <ModeProvider
      initialMode="NORMAL"
      enableKeyboard={true}
      onModeChange={(transition) => {
        console.info(`Mode: ${transition.from} → ${transition.to}`);
      }}
    >
      <HypergraphCanvas />
      <ModeIndicator position="bottom-left" />
    </ModeProvider>
  );
}
```

## Step 2: Mode-Aware Canvas

```tsx
// In HypergraphCanvas.tsx
import { useMode } from '@/hooks';

function HypergraphCanvas() {
  const { mode, isNormal, isEdge, capturesInput } = useMode();

  // Different cursor styles based on mode
  const cursorStyle = {
    NORMAL: 'default',
    INSERT: 'crosshair',
    EDGE: 'pointer',
    VISUAL: 'cell',
    COMMAND: 'text',
    WITNESS: 'wait',
  }[mode];

  return (
    <div
      className="hypergraph-canvas"
      style={{ cursor: cursorStyle }}
    >
      {/* Render graph */}
      <GraphRenderer />

      {/* Mode-specific overlays */}
      <ModeOverlays />
    </div>
  );
}
```

## Step 3: Mode-Specific Components

### INSERT Mode: K-Block Creator

```tsx
function KBlockCreator() {
  const { isInsert, toNormal } = useMode();
  const [position, setPosition] = useState<{x: number, y: number} | null>(null);

  useEffect(() => {
    if (!isInsert) return;

    const handleClick = (e: MouseEvent) => {
      setPosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('click', handleClick);
    return () => window.removeEventListener('click', handleClick);
  }, [isInsert]);

  if (!isInsert || !position) return null;

  return (
    <KBlockForm
      position={position}
      onSave={(block) => {
        createKBlock(block);
        toNormal();
      }}
      onCancel={toNormal}
    />
  );
}
```

### EDGE Mode: Edge Creator

```tsx
function EdgeCreator() {
  const { isEdge, toNormal } = useMode();
  const [sourceNode, setSourceNode] = useState<string | null>(null);
  const [targetNode, setTargetNode] = useState<string | null>(null);

  const handleNodeClick = (nodeId: string) => {
    if (!isEdge) return;

    if (!sourceNode) {
      setSourceNode(nodeId);
    } else if (sourceNode !== nodeId) {
      setTargetNode(nodeId);
      createEdge(sourceNode, nodeId);
      setSourceNode(null);
      setTargetNode(null);
      toNormal();
    }
  };

  if (!isEdge) return null;

  return (
    <EdgePreview
      sourceId={sourceNode}
      targetId={targetNode}
      onCancel={() => {
        setSourceNode(null);
        setTargetNode(null);
        toNormal();
      }}
    />
  );
}
```

### VISUAL Mode: Multi-Selector

```tsx
function MultiSelector() {
  const { isVisual, toNormal } = useMode();
  const [selectedNodes, setSelectedNodes] = useState<Set<string>>(new Set());

  const toggleNode = (nodeId: string) => {
    setSelectedNodes(prev => {
      const next = new Set(prev);
      if (next.has(nodeId)) {
        next.delete(nodeId);
      } else {
        next.add(nodeId);
      }
      return next;
    });
  };

  if (!isVisual) return null;

  return (
    <div className="multi-selector">
      <div className="selection-count">
        {selectedNodes.size} nodes selected
      </div>
      <button onClick={() => deleteNodes(Array.from(selectedNodes))}>
        Delete Selected
      </button>
      <button onClick={() => {
        setSelectedNodes(new Set());
        toNormal();
      }}>
        Clear Selection
      </button>
    </div>
  );
}
```

### COMMAND Mode: Command Palette

```tsx
function CommandPalette() {
  const { isCommand, toNormal } = useMode();
  const [input, setInput] = useState('');

  const handleSubmit = () => {
    executeCommand(input);
    setInput('');
    toNormal();
  };

  if (!isCommand) return null;

  return (
    <div className="command-palette">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') handleSubmit();
          // Note: Escape is handled globally by ModeProvider
        }}
        placeholder="Enter command..."
        autoFocus
      />
      <CommandSuggestions input={input} />
    </div>
  );
}
```

### WITNESS Mode: Commit Dialog

```tsx
function WitnessCommit() {
  const { isWitness, toNormal } = useMode();
  const [message, setMessage] = useState('');

  const handleCommit = async () => {
    await commitChanges(message);
    setMessage('');
    toNormal();
  };

  if (!isWitness) return null;

  return (
    <div className="witness-commit">
      <h3>Commit Changes</h3>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Describe your changes..."
        autoFocus
      />
      <div className="actions">
        <button onClick={handleCommit} disabled={!message.trim()}>
          Commit with Witness
        </button>
        <button onClick={toNormal}>Cancel</button>
      </div>
    </div>
  );
}
```

## Step 4: Keyboard Shortcuts

```tsx
function HypergraphKeyboardShortcuts() {
  const { mode, capturesInput } = useMode();

  useKeyboardShortcuts({
    // Only enable graph navigation when mode doesn't capture input
    enabled: !capturesInput,
    shortcuts: [
      {
        key: 'ArrowUp',
        handler: () => navigateUp(),
        contexts: ['global'],
        description: 'Navigate up',
      },
      {
        key: 'ArrowDown',
        handler: () => navigateDown(),
        contexts: ['global'],
        description: 'Navigate down',
      },
      {
        key: 'Delete',
        handler: () => deleteSelected(),
        contexts: ['global'],
        description: 'Delete selected node',
      },
    ],
  });

  return null;
}
```

## Step 5: Complete Integration

```tsx
// HypergraphEditor.tsx - Complete example
import { ModeProvider } from '@/context/ModeContext';
import { ModeIndicator } from '@/components/mode';

export function HypergraphEditor() {
  return (
    <ModeProvider initialMode="NORMAL">
      <div className="hypergraph-editor">
        {/* Main canvas */}
        <HypergraphCanvas />

        {/* Mode-specific UI overlays */}
        <KBlockCreator />
        <EdgeCreator />
        <MultiSelector />
        <CommandPalette />
        <WitnessCommit />

        {/* Keyboard shortcuts */}
        <HypergraphKeyboardShortcuts />

        {/* Mode indicator (always visible) */}
        <ModeIndicator />
      </div>
    </ModeProvider>
  );
}
```

## Best Practices

### 1. Conditional Rendering

Always check mode before rendering mode-specific UI:

```tsx
if (!isInsert) return null;
```

### 2. Return to NORMAL

Always provide a way to return to NORMAL:

```tsx
<button onClick={toNormal}>Cancel</button>
```

### 3. Respect capturesInput

Disable global shortcuts when mode captures input:

```tsx
useKeyboardShortcuts({
  enabled: !capturesInput,
  // ...
});
```

### 4. Visual Feedback

Use mode color for visual consistency:

```tsx
const { color } = useMode();
<div style={{ borderColor: color }}>...</div>
```

### 5. Mode Transitions

Provide clear affordances for mode transitions:

```tsx
// In NORMAL mode
<button onClick={toInsert}>Create Node (i)</button>
<button onClick={toEdge}>Create Edge (e)</button>
```

## Testing

```tsx
import { renderHook } from '@testing-library/react';
import { ModeProvider } from '@/context/ModeContext';
import { useMode } from '@/hooks';

test('INSERT mode enables K-Block creation', () => {
  const wrapper = ({ children }) => (
    <ModeProvider>{children}</ModeProvider>
  );

  const { result } = renderHook(() => useMode(), { wrapper });

  act(() => {
    result.current.toInsert();
  });

  expect(result.current.isInsert).toBe(true);
  expect(result.current.capturesInput).toBe(true);
});
```

## Architecture Diagram

```
┌────────────────────────────────────────────┐
│         ModeProvider (Context)             │
│  • Global keyboard handling (Escape, etc)  │
│  • Mode state management                   │
│  • Transition history                      │
└────────────────────────────────────────────┘
                    ↓
        ┌───────────────────────┐
        │  useMode() Hook       │
        │  • Shortcuts          │
        │  • Metadata           │
        │  • Checkers           │
        └───────────────────────┘
                    ↓
    ┌───────────────────────────────┐
    │  Mode-Specific Components     │
    │  • KBlockCreator (INSERT)     │
    │  • EdgeCreator (EDGE)         │
    │  • MultiSelector (VISUAL)     │
    │  • CommandPalette (COMMAND)   │
    │  • WitnessCommit (WITNESS)    │
    └───────────────────────────────┘
                    ↓
         ┌─────────────────────┐
         │  ModeIndicator      │
         │  (Visual Feedback)  │
         └─────────────────────┘
```

## Next Steps

1. Implement HypergraphEditor integration
2. Add mode-specific cursors and visual feedback
3. Implement undo/redo for mode-aware operations
4. Add mode-specific help tooltips
5. Create mode-aware context menus
