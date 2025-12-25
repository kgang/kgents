# Design Token Consolidation

**Date**: 2025-12-24
**Status**: Complete
**Location**: `/impl/claude/web/src/design/tokens.css`

## Overview

This document explains the consolidation of design tokens from three separate CSS files into a single source of truth.

## Previous State (Fragmented)

### 1. `src/styles/globals.css` (773 lines of tokens)
- **Spacing**: `--elastic-gap-xs` through `--elastic-gap-xl`
- **Radius**: `--radius-none`, `--radius-bare`, `--radius-subtle`, `--radius-soft`, `--radius-pill` (Bare Edge system)
- **Steel colors**: Full palette with semantic names (obsidian, carbon, slate, gunmetal, zinc)
- **Z-index**: `--elastic-z-base`, `--elastic-z-sticky`, `--elastic-z-dropdown`, etc.
- **Transitions**: `--elastic-transition-fast`, `--elastic-transition-smooth`, `--elastic-transition-spring`

### 2. `src/hypergraph/design-system.css` (657 lines of tokens)
- **Spacing**: `--space-xs` through `--space-2xl` (simpler names)
- **Radius**: `--radius-sm: 2px`, `--radius-md: 4px`, `--radius-lg: 6px`, `--radius-xl: 8px`, `--radius-pill: 12px` (t-shirt sizing)
- **Steel colors**: DUPLICATED from globals (same values, intentional for standalone component usage)
- **Z-index**: Hypergraph-specific layers (`--z-sidebar`, `--z-panel`, `--z-overlay`, `--z-modal`)
- **Transitions**: `--transition-fast`, `--transition-normal`, `--transition-slow` (duration + easing combined)
- **Accent gold**: `#ffd700` (bright) vs globals `#d4b88c` (muted)

### 3. `src/styles/brutalist.css` (442 lines)
- **Spacing**: Inline values (4px, 6px, 8px, 12px)
- **Radius**: All `0` (no curves in brutalism)
- **Colors**: Pure black/white palette (`--brutalist-bg`, `--brutalist-text`, `--brutalist-accent`)
- **Transitions**: None (instant interactions)
- **Shadows**: None (flat design)

## Identified Conflicts

### 1. Spacing Scale Naming
- **globals.css**: `--elastic-gap-md: 8px`
- **design-system.css**: `--space-md: 0.85rem` (13.6px)
- **Conflict**: Different naming conventions AND different values!

**Resolution**: Use `--space-*` as canonical (more intuitive), deprecate `--elastic-gap-*`

### 2. Border Radius Philosophy Clash
- **globals.css**: `--radius-bare: 2px` (Bare Edge system — semantic naming)
- **design-system.css**: `--radius-sm: 2px`, `--radius-md: 4px` (t-shirt sizing)
- **Conflict**: Two naming conventions for same concept

**Resolution**: Use Bare Edge system (`--radius-bare`, `--radius-subtle`, `--radius-soft`) as canonical, keep hypergraph sizes as aliases

### 3. Accent Gold Brightness
- **globals.css**: `--accent-gold: #d4b88c` (muted glow-amber)
- **design-system.css**: `--accent-gold: #ffd700` (bright gold for selection)
- **Conflict**: Same token name, different use cases

**Resolution**:
- `--accent-gold: #d4b88c` (canonical — muted for general accents)
- `--accent-gold-bright: #ffd700` (new — for high-visibility selection/focus)

### 4. Z-Index Duplication
- **globals.css**: `--elastic-z-dropdown: 200`
- **design-system.css**: `--z-dropdown: 200` (implied from component context)
- **Conflict**: Different naming convention

**Resolution**: Use `--z-*` as canonical, deprecate `--elastic-z-*`

### 5. Transition Naming
- **globals.css**: `--elastic-transition-fast: var(--duration-fast) var(--ease-out-expo)`
- **design-system.css**: `--transition-fast: 0.12s ease`
- **Conflict**: Different naming, different composition

**Resolution**: Use `--transition-*` as canonical (simpler), keep `--elastic-transition-*` as aliases

## New Canonical Structure

```css
/* tokens.css — Single Source of Truth */

/* COLORS */
--color-steel-obsidian, --color-steel-carbon, ... (named palette)
--color-steel-950, --color-steel-900, ... (numbered scale)
--surface-0, --surface-1, --surface-2, --surface-3 (semantic surfaces)
--text-primary, --text-secondary, --text-muted (text hierarchy)
--accent-gold (muted), --accent-gold-bright (high visibility)
--status-normal, --status-insert, --status-edge, ... (mode colors)
--health-healthy, --health-degraded, ... (confidence indicators)

/* SPACING */
--space-xs, --space-sm, --space-md, --space-lg, --space-xl, --space-2xl
DEPRECATED: --elastic-gap-*

/* BORDER RADIUS */
--radius-none, --radius-bare, --radius-subtle, --radius-soft, --radius-pill
DEPRECATED: Hypergraph numeric sizes (kept as aliases)

/* TYPOGRAPHY */
--font-sans, --font-mono
--font-size-xs, --font-size-sm, --font-size-md, --font-size-base, --font-size-lg, ...
--line-height-tight, --line-height-normal, --line-height-relaxed
--font-weight-normal, --font-weight-medium, --font-weight-semibold, --font-weight-bold

/* Z-INDEX */
--z-base, --z-sticky, --z-dropdown, --z-modal, --z-toast, --z-tooltip
--z-sidebar, --z-panel, --z-overlay (hypergraph-specific)
DEPRECATED: --elastic-z-*

/* TRANSITIONS */
--duration-instant, --duration-fast, --duration-normal, --duration-slow
--ease-linear, --ease-out, --ease-spring, --ease-spring-gentle, ...
--transition-instant, --transition-fast, --transition-normal, --transition-slow
DEPRECATED: --elastic-transition-*

/* SHADOWS */
--shadow-none, --shadow-sm, --shadow-md, --shadow-lg, --shadow-xl, --shadow-2xl

/* BRUTALIST VARIANT */
.brutalist { /* Overrides all tokens with flat, high-contrast values */ }
```

## Deprecation Schedule

### Phase 1: Immediate (2025-12-24)
1. Create unified `tokens.css` with all canonical tokens
2. Add deprecated tokens as aliases (no breakage)
3. Document migration paths in comments

### Phase 2: Migration (Next Sprint)
1. Update all components to use canonical tokens
2. Search/replace deprecated tokens across codebase:
   - `--elastic-gap-` → `--space-`
   - `--elastic-z-` → `--z-`
   - `--elastic-transition-` → `--transition-`
   - `--elastic-bp-` → `--breakpoint-`
3. Update hypergraph components to use Bare Edge radius system

### Phase 3: Cleanup (Future)
1. Remove deprecated token aliases from `tokens.css`
2. Remove old CSS files (globals.css, design-system.css, brutalist.css)
3. Import only `tokens.css` in main entry point

## Migration Examples

### Spacing
```css
/* BEFORE */
gap: var(--elastic-gap-md);
padding: var(--space-md);

/* AFTER (canonical) */
gap: var(--space-md);
padding: var(--space-md);
```

### Border Radius
```css
/* BEFORE (hypergraph style) */
border-radius: var(--radius-sm); /* 2px as number */

/* AFTER (Bare Edge canonical) */
border-radius: var(--radius-bare); /* 2px, semantic name */
```

### Accent Gold
```css
/* BEFORE (ambiguous) */
color: var(--accent-gold); /* Which gold? Muted or bright? */

/* AFTER (explicit) */
color: var(--accent-gold);        /* Muted gold for general accents */
caret-color: var(--accent-gold-bright); /* Bright gold for high-visibility */
```

### Z-Index
```css
/* BEFORE */
z-index: var(--elastic-z-modal);

/* AFTER (canonical) */
z-index: var(--z-modal);
```

### Transitions
```css
/* BEFORE */
transition: all var(--elastic-transition-fast);

/* AFTER (canonical) */
transition: all var(--transition-fast);
```

## Philosophy Alignment

### STARK BIOME (Default)
- 90% steel (cool industrial frames)
- 10% earned glow (organic accents)
- Muted gold (`--accent-gold: #d4b88c`) for warmth
- Bright gold (`--accent-gold-bright: #ffd700`) for special moments (selection, focus)
- Subtle curves (`--radius-bare: 2px`) — "just enough to not cut"
- Breathing animations (3-4 second cycles)

### Brutalist Variant (`.brutalist` class)
- Pure black/white, no grays unless functional
- No decoration (shadows, gradients, curves)
- No transitions (instant feedback)
- Typography creates hierarchy (weight + size)
- High information density

## Benefits of Consolidation

1. **Single Source of Truth**: No more guessing which token to use
2. **Clear Deprecation Path**: Old tokens work, but have clear replacements
3. **Consistent Naming**: `--space-*`, `--z-*`, `--transition-*` (no prefixes)
4. **Semantic Clarity**: Bare Edge system (`--radius-bare`) > numeric (`--radius-sm: 2px`)
5. **Variant Support**: Brutalist aesthetic as a layer, not a separate system
6. **Smaller Footprint**: One file instead of three
7. **Easier Onboarding**: New developers learn one system, not three

## Usage

### Import in Main CSS
```css
/* src/styles/globals.css */
@import '../design/tokens.css';
```

### Apply Brutalist Variant
```jsx
<div className="brutalist">
  {/* All tokens override to flat, high-contrast values */}
</div>
```

### Use Canonical Tokens
```css
.my-component {
  gap: var(--space-md);               /* Spacing */
  border-radius: var(--radius-bare);  /* Radius */
  color: var(--accent-gold);          /* Muted gold */
  caret-color: var(--accent-gold-bright); /* Bright gold */
  z-index: var(--z-modal);            /* Z-index */
  transition: all var(--transition-fast); /* Transitions */
  box-shadow: var(--shadow-md);       /* Shadow */
}
```

## Testing Checklist

- [ ] Verify all components still render correctly
- [ ] Check that brutalist variant applies properly
- [ ] Confirm hypergraph editor visuals unchanged
- [ ] Test responsive breakpoints
- [ ] Validate accessibility (focus rings, contrast)
- [ ] Check scrollbar theming across jewels
- [ ] Verify animation timing feels correct
- [ ] Test reduced motion support

## References

- STARK BIOME: `docs/skills/elastic-ui-patterns.md`
- Bare Edge System: `impl/claude/web/src/styles/globals.css` (lines 162-170)
- Hypergraph Design: `impl/claude/web/src/hypergraph/design-system.css`
- Brutalist Aesthetic: `impl/claude/web/src/styles/brutalist.css`
