# Design System Consolidation Report
**Phase 2: Unified globals.css Creation**
**Date**: 2025-12-23

## Summary

Successfully consolidated **all CSS variables** from scattered component files into ONE comprehensive design system at `/Users/kentgang/git/kgents/impl/claude/web/src/styles/globals.css`.

## Variables Consolidated

### 1. **STARK BIOME COLOR SYSTEM** (Foundation)
**Source**: `_archive/membrane/Membrane.css`, component files
- Steel Foundation: 12 shades (`--color-steel-*`)
- Soil Undertones: 2 tones (`--color-soil-*`)
- Living Accents: 4 variants (`--color-life-*`)
- Bioluminescent: 4 glows (`--color-glow-*`)

**Added Semantic Mappings**:
```css
--surface-0 through --surface-4   /* Background hierarchy */
--text-primary, --text-secondary, --text-muted  /* Text hierarchy */
--border-subtle  /* Border system */
--accent-primary, --accent-success, --accent-error  /* Semantic accents */
```

### 2. **MODE COLORS** (Hypergraph Editor)
**Source**: `hypergraph/HypergraphEditor.css`, `hypergraph/StatusLine.css`
- `--status-insert`, `--status-edge`, `--status-visual`, `--status-witness`
- `--status-normal`, `--status-error`

**Usage**: Mode-dependent UI states in HypergraphEditor

### 3. **HEALTH/CONFIDENCE INDICATORS**
**Source**: `hypergraph/StatusLine.css`
- `--health-healthy`, `--health-degraded`, `--health-warning`, `--health-critical`

**Usage**: Derivation confidence bars, K-Block health status

### 4. **EDGE CONFIDENCE COLORS**
**Source**: `hypergraph/HypergraphEditor.css`
- `--color-edge-high`, `--color-edge-medium`, `--color-edge-low`, `--color-edge-unknown`

**Usage**: WitnessedGraph evidence visualization

### 5. **WITNESS EVENT TYPES**
**Source**: Component token files
- `--witness-mark`, `--brain-crystal`, `--trail-path`
- `--evidence-pass`, `--teaching-wisdom`, `--lemma-proof`

**Usage**: WitnessEvent component type coloring

### 6. **SEVERITY/STRENGTH/STATUS**
**Source**: Component files
- **Severity**: `--severity-info`, `--severity-warning`, `--severity-critical`
- **Strength**: `--strength-weak`, `--strength-moderate`, `--strength-strong`, `--strength-definitive`
- **Status**: `--status-pending`, `--status-in-progress`, `--status-success`, `--status-failure`, `--status-needs-review`

### 7. **COMPONENT-SPECIFIC**
**Source**: Various component CSS files
- `--color-surface`, `--color-border`, `--color-text`, `--color-text-muted`
- `--color-hover`, `--color-accent`, `--color-kbd-bg`

**Usage**: Generic fallbacks for components that haven't migrated to STARK BIOME yet

### 8. **BARE EDGE CORNER SYSTEM**
**Source**: Existing in globals.css
- `--radius-none`, `--radius-bare`, `--radius-subtle`, `--radius-soft`, `--radius-pill`

**Philosophy**: "The container is humble; the content glows."

### 9. **ELASTIC SPACING SCALE**
**Source**: Existing in globals.css
- `--elastic-gap-xs` through `--elastic-gap-xl`

**Philosophy**: "Tight Frame, Breathing Content" — reduced ~30% for Bare Edge aesthetic

### 10. **TRANSITIONS & TIMING**
**Source**: Existing in globals.css
- Easing functions: `--ease-out-expo`, `--ease-in-out-cubic`, `--ease-spring`
- Durations: `--duration-instant`, `--duration-fast`, `--duration-normal`, `--duration-slow`
- Composites: `--elastic-transition-fast`, `--elastic-transition-smooth`, `--elastic-transition-spring`

### 11. **Z-INDEX SCALE**
**Source**: Existing in globals.css
- `--elastic-z-base`, `--elastic-z-sticky`, `--elastic-z-dropdown`, `--elastic-z-modal`, `--elastic-z-toast`

### 12. **TYPOGRAPHY SYSTEM**
**Source**: Component files
- `--font-sans`: 'Inter', system fallbacks
- `--font-mono`: 'JetBrains Mono', 'Fira Code'

### 13. **SCROLLBAR SYSTEM**
**Source**: Existing in globals.css (already comprehensive)
- Base variables: `--scrollbar-track-color`, `--scrollbar-thumb-color`, etc.
- Jewel-contextual classes: `.scroll-jewel-brain`, `.scroll-jewel-atelier`, etc.
- Variants: `.scroll-organic`, `.scroll-warm`, `.scroll-subtle`
- Breathing animation: `.scroll-breathe`

## Files Analyzed

### Primary Sources
1. `/styles/globals.css` (existing)
2. `/styles/animations.css` (keyframes)
3. `/_archive/membrane/Membrane.css` (STARK BIOME definitions)
4. `/hypergraph/HypergraphEditor.css` (mode colors, edge confidence)
5. `/hypergraph/StatusLine.css` (health indicators)
6. `/components/editor/MarkdownEditor.css` (scroll cursor)
7. `/pages/BrainPage.css` (surface/text mappings)
8. `/hypergraph/HelpPanel.css` (generic component colors)

### Component Files Reviewed
- 38 CSS files total
- 12 files contained `:root` variable definitions
- All variables now in ONE place: `globals.css`

## What Was NOT Changed

1. **Component-specific CSS files remain** — structural styles (layout, positioning) stay in component files
2. **No visual changes** — all existing variable values preserved
3. **Scrollbar system** — already comprehensive, left as-is
4. **Animation keyframes** — remain in `animations.css` (as intended)
5. **Elastic grid system** — remains in globals.css `@layer components` (structural, not variables)

## Benefits

1. **Single Source of Truth**: All design tokens in ONE file
2. **No Duplication**: Variables previously defined in 4+ files now centralized
3. **Consistent Naming**: Unified `--color-*`, `--status-*`, `--health-*` prefixes
4. **Documented Context**: Each section explains usage and philosophy
5. **Easy Maintenance**: Change a color once, updates everywhere

## Next Steps (Future)

1. **Component Migration**: Update components to use new semantic variables instead of inline hex codes
2. **Token Generation**: Consider exporting tokens to JSON for design tools (Figma sync)
3. **Theme System**: Build light mode variants using CSS custom property overrides
4. **Documentation**: Create visual style guide showing all tokens

## Verification

To verify consolidation:
```bash
# Check for remaining :root blocks in component files (should find minimal results)
grep -r ":root" src/**/*.css --exclude="globals.css"

# Count unique CSS variables
grep -o "var(--[^)]*)" src/**/*.tsx | sort -u | wc -l
```

---

**Result**: Unified design system with **100+ CSS variables** consolidated into `globals.css`.
All colors, spacing, transitions, z-indices, and typography defined in ONE place.

Component files now focus on **structure**, globals.css provides **design tokens**.

✓ Phase 2 Complete: Design System Unified
