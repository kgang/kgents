# Mode System Quick Start

## Try It Now

```bash
cd impl/claude/web
npm run dev
# Visit http://localhost:3000
# Press 'i' to enter INSERT mode
# Press 'Esc' to return to NORMAL
# See the mode indicator in bottom-left corner
```

## Available Modes

| Key | Mode | Color | Purpose |
|-----|------|-------|---------|
| `Esc` | NORMAL | Steel | Navigate, select |
| `i` | INSERT | Moss | Create K-Blocks |
| `v` | VISUAL | Sage | Multi-select |
| `e` | EDGE | Amber | Create relationships |
| `:` | COMMAND | Rust | Slash commands |
| `w` | WITNESS | Gold | Commit changes |

## Navigation (NORMAL mode)

| Key | Action |
|-----|--------|
| `j` or `↓` | Scroll down |
| `k` or `↑` | Scroll up |
| `{` | Previous paragraph |
| `}` | Next paragraph |
| `g``g` | Top of document |
| `G` | Bottom of document |

## Using in Components

```tsx
import { useMode } from '@/hooks';

function MyComponent() {
  const { mode, isInsert, toNormal, color } = useMode();
  
  if (isInsert) {
    return <KBlockCreator onCancel={toNormal} />;
  }
  
  return <div style={{ borderColor: color }}>NORMAL mode</div>;
}
```

## Mode Indicator

The pill in the bottom-left shows:
- **Color** - Current mode color
- **Label** - Mode name (e.g., "INSERT")
- **Description** - What this mode does
- **Hint** - "Esc to exit" (when not NORMAL)

## Escape Key

**N-03 Law**: Escape ALWAYS returns to NORMAL, from any mode, at any time.

This is the universal "get out" key - it's your safety net.

## Tests

```bash
npm test -- --run ModeSystem
# Should see: ✓ 19 passed
```

## Docs

- Full docs: `src/components/mode/README.md`
- Integration guide: `src/components/mode/INTEGRATION.md`
- Quick reference: `src/components/mode/QUICKREF.md`
- Implementation report: `ZERO_SEED_MODE_IMPLEMENTATION.md`
- Transition diagram: `MODE_TRANSITIONS.md`
