# Design Token Quick Reference

**Location**: `/impl/claude/web/src/design/tokens.css`

## Most Used Tokens (Copy-Paste Ready)

### Colors
```css
/* Surfaces */
--surface-0                 /* Deepest background */
--surface-1                 /* Card backgrounds */
--surface-2                 /* Elevated surfaces */
--surface-3                 /* Borders, dividers */

/* Text */
--text-primary              /* Bright text */
--text-secondary            /* Muted body text */
--text-muted                /* Hints, timestamps */

/* Accents */
--accent-gold               /* Muted gold (#d4b88c) */
--accent-gold-bright        /* Bright gold (#ffd700) for selection/focus */
--accent-success            /* Life-sage green */
--accent-error              /* Muted rust */

/* Status */
--status-normal             /* Blue — normal mode */
--status-insert             /* Green — edit mode */
--status-error              /* Red — error state */
```

### Spacing
```css
--space-xs                  /* 3.2px — micro gaps */
--space-sm                  /* 6.4px — tight groupings */
--space-md                  /* 13.6px — standard gaps */
--space-lg                  /* 20px — comfortable sections */
--space-xl                  /* 28px — spacious areas */
```

### Border Radius (Bare Edge System)
```css
--radius-none               /* 0px — panels, canvas */
--radius-bare               /* 2px — cards, containers */
--radius-subtle             /* 3px — interactive surfaces */
--radius-soft               /* 4px — accent elements */
--radius-pill               /* 9999px — badges, tags */
```

### Z-Index
```css
--z-base                    /* 0 */
--z-sticky                  /* 100 */
--z-dropdown                /* 200 */
--z-modal                   /* 300 */
--z-toast                   /* 400 */
```

### Transitions
```css
--transition-instant        /* 100ms */
--transition-fast           /* 120ms */
--transition-normal         /* 200ms */
--transition-slow           /* 320ms (spring) */
```

### Shadows
```css
--shadow-sm                 /* Subtle elevation */
--shadow-md                 /* Card hover */
--shadow-lg                 /* Modal/panel */
```

## Common Patterns

### Card Component
```css
.card {
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-bare);
  padding: var(--space-md);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
```

### Input Field
```css
.input {
  background: var(--surface-0);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-subtle);
  color: var(--text-primary);
  caret-color: var(--accent-gold-bright);
  padding: var(--space-sm) var(--space-md);
  transition: border-color var(--transition-fast);
}

.input:focus {
  border-color: var(--accent-gold);
  outline: none;
}

.input::placeholder {
  color: var(--text-muted);
}
```

### Button
```css
.button {
  background: var(--surface-2);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-subtle);
  color: var(--text-primary);
  padding: var(--space-sm) var(--space-lg);
  transition: all var(--transition-fast);
}

.button:hover {
  background: var(--surface-3);
  border-color: var(--accent-gold);
  box-shadow: var(--shadow-sm);
}

.button-primary {
  background: var(--accent-success);
  color: var(--surface-0);
  border-color: var(--accent-success);
}
```

### Modal
```css
.modal {
  background: var(--surface-1);
  border: 1px solid var(--surface-3);
  border-radius: var(--radius-soft);
  padding: var(--space-xl);
  box-shadow: var(--shadow-xl);
  z-index: var(--z-modal);
}

.modal-backdrop {
  background: var(--backdrop-overlay-medium);
  backdrop-filter: var(--backdrop-blur-light);
  z-index: calc(var(--z-modal) - 1);
}
```

### Stack Layout
```css
.stack {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
```

### Grid Layout
```css
.grid {
  display: grid;
  gap: var(--space-md);
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}
```

## Brutalist Variant

Apply `.brutalist` class to container for flat, high-contrast design:

```jsx
<div className="brutalist">
  {/* All tokens override to pure black/white, no curves, no transitions */}
</div>
```

## Deprecated Tokens (Don't Use)

```css
/* OLD → NEW */
--elastic-gap-md        → --space-md
--elastic-z-modal       → --z-modal
--elastic-transition-fast → --transition-fast
--elastic-bp-lg         → --breakpoint-lg
--radius-sm: 2px        → --radius-bare (semantic name)
```

## Steel Color Scale (When You Need Granular Control)

```css
--color-steel-950       /* #0d0d0d — deepest */
--color-steel-900       /* #1a1a1a */
--color-steel-850       /* #1f1f1f */
--color-steel-800       /* #252525 */
--color-steel-700       /* #333 */
--color-steel-600       /* #444 */
--color-steel-500       /* #666 */
--color-steel-400       /* #888 */
--color-steel-300       /* #a0a0a0 */
--color-steel-200       /* #ccc */
--color-steel-100       /* #e0e0e0 — lightest */
```

## Health/Confidence Indicators

```css
--health-healthy        /* >= 80% — green */
--health-degraded       /* 60-80% — yellow */
--health-warning        /* 40-60% — orange */
--health-critical       /* < 40% — red */
```

## When to Use Bright vs Muted Gold

```css
/* MUTED GOLD (--accent-gold: #d4b88c) */
- General accents
- Hover states
- Borders
- Icons

/* BRIGHT GOLD (--accent-gold-bright: #ffd700) */
- Text selection
- Focus indicators
- Carets
- Active states
- Anything that needs HIGH visibility
```

## Responsive Breakpoints (Use in JS)

```js
const breakpoints = {
  sm: 640,   // Mobile
  md: 768,   // Tablet
  lg: 1024,  // Desktop
  xl: 1280,  // Wide
  '2xl': 1536 // Ultra-wide
};

// Or access from CSS custom properties
const smBreakpoint = getComputedStyle(document.documentElement)
  .getPropertyValue('--breakpoint-sm'); // "640px"
```

## Typography Scale

```css
--font-size-xs          /* 10px */
--font-size-sm          /* 12px */
--font-size-md          /* 14px */
--font-size-base        /* 16px */
--font-size-lg          /* 20px */
--font-size-xl          /* 24px */
--font-size-2xl         /* 32px */

--font-mono             /* 'JetBrains Mono', 'Fira Code', monospace */
--font-sans             /* 'Inter', -apple-system, BlinkMacSystemFont, sans-serif */
```

## Animation Easings

```css
--ease-linear           /* Linear timing */
--ease-out              /* Deceleration */
--ease-spring           /* Bouncy spring (1.56 bounce) */
--ease-spring-gentle    /* Subtle spring (1.2 bounce) */
--ease-out-expo         /* Exponential deceleration */
```

## Pro Tips

1. **Always use semantic surface tokens** (`--surface-0` through `--surface-3`) instead of raw steel colors
2. **Bare Edge philosophy**: Most things get `--radius-bare` (2px), special things get `--radius-soft` (4px)
3. **Spacing consistency**: Use `--space-md` for standard gaps, `--space-sm` for tight groupings
4. **Z-index layering**: Always use the scale, never arbitrary numbers
5. **Transitions**: Use `--transition-fast` for most interactions, `--transition-slow` for dramatic effects
6. **Brutalist override**: When you need ultra-minimal, just add `.brutalist` class

## Import in Your Component

```tsx
// Component-scoped CSS
import '../design/tokens.css';

function MyComponent() {
  return (
    <div style={{
      background: 'var(--surface-1)',
      padding: 'var(--space-md)',
      borderRadius: 'var(--radius-bare)',
    }}>
      Content
    </div>
  );
}
```
