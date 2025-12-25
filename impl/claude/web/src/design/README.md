# kgents Design System

**Single Source of Truth**: `/impl/claude/web/src/design/tokens.css`

## Philosophy

> "Daring, bold, creative, opinionated but not gaudy"

### STARK BIOME (Default)
- **90% Steel**: Cool industrial frames (backgrounds, borders, containers)
- **10% Earned Glow**: Organic accents that celebrate moments (success, focus, special states)
- **Bare Edge**: Sharp corners (2px) make warm elements pop against austerity
- **Breathing Motion**: Subtle 3-4 second animation cycles, never frantic
- **High Information Density**: Tight spacing, purposeful whitespace

### Brutalist Variant (`.brutalist`)
- **Pure Black/White**: No grays unless functional
- **No Decoration**: No shadows, gradients, or rounded corners
- **Instant Feedback**: No transitions, immediate state changes
- **Typography as Structure**: Weight and size create hierarchy
- **Information-Rich**: Minimal padding, maximal content

## Files

```
src/design/
├── tokens.css                  # 🎯 Single source of truth (import this)
├── TOKEN_CONSOLIDATION.md      # Full consolidation documentation
├── QUICK_REF.md                # Copy-paste cheat sheet
└── README.md                   # This file
```

## Quick Start

### 1. Import Tokens
```css
/* In your main CSS file (e.g., globals.css) */
@import '../design/tokens.css';
```

### 2. Use in Components
```css
.my-component {
  background: var(--surface-1);
  padding: var(--space-md);
  border-radius: var(--radius-bare);
  color: var(--text-primary);
}
```

### 3. Apply Brutalist Variant (Optional)
```jsx
<div className="brutalist">
  {/* High-contrast, flat, instant design */}
</div>
```

## Token Categories

### Colors
- **Surfaces**: `--surface-0` through `--surface-3`
- **Text**: `--text-primary`, `--text-secondary`, `--text-muted`
- **Accents**: `--accent-gold`, `--accent-gold-bright`, `--accent-success`, `--accent-error`
- **Status**: `--status-normal`, `--status-insert`, `--status-error`, etc.
- **Health**: `--health-healthy`, `--health-degraded`, `--health-warning`, `--health-critical`

### Spacing
- **Scale**: `--space-xs`, `--space-sm`, `--space-md`, `--space-lg`, `--space-xl`, `--space-2xl`
- **Philosophy**: Tight frame, breathing content

### Border Radius (Bare Edge)
- `--radius-none` (0px) — Panels, canvas
- `--radius-bare` (2px) — Cards, containers (most common)
- `--radius-subtle` (3px) — Interactive surfaces
- `--radius-soft` (4px) — Accent elements
- `--radius-pill` (9999px) — Badges, tags

### Typography
- **Families**: `--font-sans`, `--font-mono`
- **Sizes**: `--font-size-xs` through `--font-size-2xl`
- **Weights**: `--font-weight-normal`, `--font-weight-medium`, `--font-weight-semibold`, `--font-weight-bold`
- **Line Heights**: `--line-height-tight`, `--line-height-normal`, `--line-height-relaxed`

### Z-Index
- `--z-base` (0)
- `--z-sticky` (100)
- `--z-dropdown` (200)
- `--z-modal` (300)
- `--z-toast` (400)

### Transitions
- **Durations**: `--duration-instant`, `--duration-fast`, `--duration-normal`, `--duration-slow`
- **Easings**: `--ease-linear`, `--ease-out`, `--ease-spring`, `--ease-spring-gentle`
- **Composite**: `--transition-instant`, `--transition-fast`, `--transition-normal`, `--transition-slow`

### Shadows
- `--shadow-none`
- `--shadow-sm` (subtle elevation)
- `--shadow-md` (card hover)
- `--shadow-lg` (modal/panel)
- `--shadow-xl` (dramatic elevation)

## Visual Comparison: Before & After

### Before (Fragmented)

**globals.css** (773 lines):
```css
--elastic-gap-md: 8px;
--radius-bare: 2px;
--accent-gold: #d4b88c;
--elastic-z-modal: 300;
--elastic-transition-fast: var(--duration-fast) var(--ease-out-expo);
```

**design-system.css** (657 lines):
```css
--space-md: 0.85rem;  /* 13.6px — CONFLICT! */
--radius-sm: 2px;     /* Same value, different name */
--accent-gold: #ffd700; /* CONFLICT! Different color */
--z-modal: 1000;      /* CONFLICT! Different value */
--transition-fast: 0.12s ease;
```

**brutalist.css** (442 lines):
```css
/* Inline values everywhere */
padding: 6px 12px;
border-radius: 0;
background: #0a0a0a;
```

**Result**: Confusion, duplicates, conflicts, no clear canonical choice.

### After (Consolidated)

**tokens.css** (ONE file):
```css
/* CANONICAL */
--space-md: 0.85rem;         /* Spacing */
--radius-bare: 2px;          /* Border radius (Bare Edge) */
--accent-gold: #d4b88c;      /* Muted gold (general) */
--accent-gold-bright: #ffd700; /* Bright gold (selection/focus) */
--z-modal: 300;              /* Z-index */
--transition-fast: 120ms cubic-bezier(0.19, 1, 0.22, 1);

/* DEPRECATED (aliases for backward compatibility) */
--elastic-gap-md: var(--space-md);
--elastic-z-modal: var(--z-modal);
--elastic-transition-fast: var(--transition-fast);
```

**Result**: Clear canonical tokens, deprecation path, no breaking changes.

## Migration Path

### Phase 1: Immediate (✅ Complete)
- Created unified `tokens.css`
- All deprecated tokens aliased (no breakage)
- Documentation written

### Phase 2: Migration (Next Sprint)
- Update components to use canonical tokens
- Search/replace:
  - `--elastic-gap-` → `--space-`
  - `--elastic-z-` → `--z-`
  - `--elastic-transition-` → `--transition-`

### Phase 3: Cleanup (Future)
- Remove deprecated aliases
- Delete old CSS files
- Import only `tokens.css`

## Common Recipes

### Card with Hover
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
}

.input:focus {
  border-color: var(--accent-gold);
  outline: none;
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

.button-primary {
  background: var(--accent-success);
  color: var(--surface-0);
}
```

### Modal
```css
.modal {
  background: var(--surface-1);
  border-radius: var(--radius-soft);
  padding: var(--space-xl);
  box-shadow: var(--shadow-xl);
  z-index: var(--z-modal);
}

.modal-backdrop {
  background: var(--backdrop-overlay-medium);
  backdrop-filter: var(--backdrop-blur-light);
}
```

## When to Use What

### Spacing
- `--space-xs` — Micro gaps (icon + text)
- `--space-sm` — Tight groupings (form fields)
- `--space-md` — Standard gaps (most common)
- `--space-lg` — Comfortable sections (between cards)
- `--space-xl` — Spacious areas (page margins)

### Radius
- `--radius-none` — Full bleed panels
- `--radius-bare` — Most components (cards, buttons)
- `--radius-subtle` — Interactive elements (inputs, links)
- `--radius-soft` — Special accents (highlights, selections)
- `--radius-pill` — Badges, tags, status indicators

### Transitions
- `--transition-instant` — Immediate feedback (click states)
- `--transition-fast` — Most interactions (hover, focus)
- `--transition-normal` — Smooth changes (expand/collapse)
- `--transition-slow` — Dramatic effects (modal open, page transitions)

### Shadows
- `--shadow-sm` — Subtle elevation (cards at rest)
- `--shadow-md` — Clear elevation (card hover, dropdowns)
- `--shadow-lg` — Strong elevation (modals, panels)
- `--shadow-xl` — Dramatic separation (full-screen overlays)

## Design Principles

1. **Tasteful > Feature-Complete**: Fewer tokens, well-chosen
2. **Depth over Breadth**: Rich semantic meaning, not exhaustive scales
3. **The Mirror Test**: Does this token feel like kgents on its best day?
4. **Daring, Bold, Creative**: Opinionated choices (Bare Edge over generic t-shirt sizes)
5. **Not Gaudy**: Earned glow (10%), humble frame (90%)
6. **Joy-Inducing**: Subtle spring animations, breathing scrollbars
7. **Composable**: Tokens combine to create experiences

## Resources

- **Full Documentation**: `TOKEN_CONSOLIDATION.md`
- **Quick Reference**: `QUICK_REF.md`
- **Elastic UI Patterns**: `docs/skills/elastic-ui-patterns.md`
- **STARK BIOME**: See globals.css lines 19-88

## FAQs

**Q: Why two gold colors?**
A: `--accent-gold` is muted (#d4b88c) for general warmth. `--accent-gold-bright` is high-visibility (#ffd700) for selection/focus where you need to catch the eye.

**Q: When do I use brutalist variant?**
A: When you need ultra-minimal, information-dense UI. Apply `.brutalist` class to container.

**Q: What happened to `--elastic-gap-*`?**
A: Deprecated. Use `--space-*` instead (simpler, more intuitive).

**Q: Can I still use hypergraph's `--radius-sm`?**
A: Yes, it's aliased to `--radius-bare`. But prefer the semantic name.

**Q: Why "Bare Edge" instead of t-shirt sizes?**
A: More opinionated, more meaningful. "Bare" tells you *why* (just enough to not cut), not *what* (small).

## Contributing

When adding new tokens:
1. Check if existing token fits your use case
2. If not, add to appropriate category in `tokens.css`
3. Use semantic names (`--radius-whisper`, not `--radius-1px`)
4. Document use case in comments
5. Add to `QUICK_REF.md`
