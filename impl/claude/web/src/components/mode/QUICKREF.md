# Mode System Quick Reference

One-page cheat sheet for the six-mode editing system.

## Keyboard Bindings

| Key | From Mode | To Mode | Purpose |
|-----|-----------|---------|---------|
| `Esc` | Any | NORMAL | Return to NORMAL (ALWAYS) |
| `i` | NORMAL | INSERT | Create K-Blocks |
| `e` | NORMAL | EDGE | Create edges |
| `v` | NORMAL | VISUAL | Multi-select |
| `:` | NORMAL | COMMAND | Slash commands |
| `w` | NORMAL | WITNESS | Commit changes |

## Mode Properties

| Mode | Color | capturesInput | blocksNavigation |
|------|-------|---------------|------------------|
| NORMAL | Steel | ❌ | ❌ |
| INSERT | Moss | ✅ | ❌ |
| EDGE | Amber | ❌ | ❌ |
| VISUAL | Sage | ❌ | ❌ |
| COMMAND | Rust | ✅ | ❌ |
| WITNESS | Gold | ✅ | ✅ |

## Hook API

```tsx
import { useMode } from '@/hooks';

const {
  // Current state
  mode,              // 'NORMAL' | 'INSERT' | ...
  color,             // Mode color (hex string)
  label,             // 'NORMAL', 'INSERT', etc.
  description,       // Mode description
  capturesInput,     // boolean
  blocksNavigation,  // boolean

  // Mode checkers
  isNormal,          // boolean
  isInsert,          // boolean
  isEdge,            // boolean
  isVisual,          // boolean
  isCommand,         // boolean
  isWitness,         // boolean

  // Transitions
  setMode,           // (mode: Mode, reason?: string) => void
  toNormal,          // () => void
  toInsert,          // () => void
  toEdge,            // () => void
  toVisual,          // () => void
  toCommand,         // () => void
  toWitness,         // () => void

  // History
  history,           // Array<{from, to, timestamp, reason}>
} = useMode();
```

## Common Patterns

### Conditional Rendering
```tsx
if (!isInsert) return null;
```

### Mode-Specific Styles
```tsx
<div style={{ borderColor: color }}>
```

### Disable Shortcuts
```tsx
useKeyboardShortcuts({
  enabled: !capturesInput,
  // ...
});
```

### Cancel Handler
```tsx
<button onClick={toNormal}>Cancel (Esc)</button>
```

### Mode Transition with Reason
```tsx
setMode('INSERT', 'toolbar-button');
```

## Component Examples

### Setup (App-Level)
```tsx
import { ModeProvider } from '@/context/ModeContext';
import { ModeIndicator } from '@/components/mode';

<ModeProvider>
  <App />
  <ModeIndicator />
</ModeProvider>
```

### Mode-Aware Component
```tsx
function KBlockCreator() {
  const { isInsert, toNormal } = useMode();
  if (!isInsert) return null;
  return <Form onCancel={toNormal} />;
}
```

### Toolbar with Mode Triggers
```tsx
function Toolbar() {
  const { mode, toInsert, toEdge } = useMode();
  return (
    <div>
      <button onClick={toInsert} disabled={mode !== 'NORMAL'}>
        Create Node (i)
      </button>
      <button onClick={toEdge} disabled={mode !== 'NORMAL'}>
        Create Edge (e)
      </button>
    </div>
  );
}
```

## Files

| File | Purpose |
|------|---------|
| `types/mode.ts` | Type definitions |
| `context/ModeContext.tsx` | Context provider |
| `hooks/useMode.ts` | Hook for components |
| `components/mode/ModeIndicator.tsx` | Visual indicator |
| `components/mode/ModeIndicator.css` | Styles |

## Import Paths

```tsx
// Types
import type { Mode } from '@/types/mode';

// Context
import { ModeProvider } from '@/context/ModeContext';

// Hook
import { useMode } from '@/hooks';

// Component
import { ModeIndicator } from '@/components/mode';
```

## Colors (Living Earth)

```tsx
const MODE_COLORS = {
  NORMAL: '#475569',   // Steel (slate-600)
  INSERT: '#2E4A2E',   // Moss (fern)
  EDGE: '#D4A574',     // Amber
  VISUAL: '#4A6B4A',   // Sage
  COMMAND: '#8B5A2B',  // Rust (bronze)
  WITNESS: '#E8C4A0',  // Gold (honey)
};
```

## Testing

```tsx
import { renderHook, act } from '@testing-library/react';
import { ModeProvider } from '@/context/ModeContext';
import { useMode } from '@/hooks';

const wrapper = ({ children }) => (
  <ModeProvider>{children}</ModeProvider>
);

const { result } = renderHook(() => useMode(), { wrapper });

act(() => {
  result.current.toInsert();
});

expect(result.current.isInsert).toBe(true);
```

## N-03 Compliance

**Rule**: Escape ALWAYS returns to NORMAL

**Enforcement**: Global keyboard handler in `ModeProvider` (cannot be overridden)

**Test**:
```tsx
// From any mode
act(() => result.current.toNormal() );
expect(result.current.mode).toBe('NORMAL');
```

## Tips

1. **Always check mode before rendering**: `if (!isInsert) return null;`
2. **Provide cancel affordance**: `<button onClick={toNormal}>Cancel</button>`
3. **Respect capturesInput**: Disable global shortcuts when `capturesInput === true`
4. **Use mode color**: Visual consistency via `color` property
5. **Track history**: Debug with `history` array
6. **Fire onModeChange**: Analytics via callback in `ModeProvider`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Escape not working | Check ModeProvider wraps component tree |
| Mode not updating | Verify component inside ModeProvider |
| Shortcuts interfering | Disable when `capturesInput === true` |
| Colors not showing | Import `ModeIndicator.css` |
| Type errors | Import types from `@/types/mode` |

## Performance

- **Context updates**: Only when mode changes
- **Keyboard handlers**: Single global listener
- **History**: Capped at 10 entries
- **Re-renders**: Minimized via `useMemo`

## Accessibility

- **Keyboard-first**: All modes accessible via keyboard
- **Escape key**: Universal exit (muscle memory)
- **Visual feedback**: Color-coded indicator
- **Screen readers**: Add ARIA labels as needed

---

**Quick Start**: Wrap with `<ModeProvider>`, add `<ModeIndicator />`, use `useMode()` hook.
