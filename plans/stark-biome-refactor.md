# Stark Biome Refactor Plan

> *"The frame is humble. The content glows. The austerity makes the warmth more precious."*

**Created**: 2025-12-22
**Status**: Planning
**Scope**: Subtle but radical transformation of webapp styling

---

## Philosophy

The "Stark Biome" aesthetic is a **refinement, not a replacement**. We keep the organic life—it just emerges from industrial stillness instead of warm chaos. The 90/10 rule:

- **90% Steel**: Cool grays, sharp edges, static silence
- **10% Life**: Organic greens/ambers that bloom where it matters

---

## Phase 1: Foundation (Token System)

### 1.1 Update Tailwind Config

**File**: `impl/claude/web/tailwind.config.js`

```javascript
// REPLACE jewelColors with starkColors
const starkColors = {
  // Steel Foundation (backgrounds, frames)
  'steel-obsidian': '#0A0A0C',
  'steel-carbon': '#141418',
  'steel-slate': '#1C1C22',
  'steel-gunmetal': '#28282F',
  'steel-zinc': '#3A3A44',

  // Soil Undertones (warm secondary surfaces)
  'soil-loam': '#1A1512',
  'soil-humus': '#2D221A',
  'soil-peat': '#3D3028',
  'soil-earth': '#524436',
  'soil-clay': '#685844',

  // Living Accent (success, growth, life)
  'life-moss': '#1A2E1A',
  'life-fern': '#2E4A2E',
  'life-sage': '#4A6B4A',
  'life-mint': '#6B8B6B',
  'life-sprout': '#8BAB8B',

  // Bioluminescent (highlights, focus, precious)
  'glow-spore': '#C4A77D',
  'glow-amber': '#D4B88C',
  'glow-light': '#E5C99D',
  'glow-lichen': '#8BA98B',
  'glow-bloom': '#9CBDA0',

  // Semantic (constrained to 4)
  'state-healthy': '#4A6B4A',
  'state-pending': '#C4A77D',
  'state-alert': '#A65D4A',
  'state-dormant': '#3A3A44',

  // Jewel Identities (muted)
  'jewel-brain': '#4A6B6B',
  'jewel-witness': '#6B6B4A',
  'jewel-atelier': '#8B7355',
  'jewel-liminal': '#5A5A6B',
};
```

### 1.2 Update CSS Custom Properties

**File**: `impl/claude/web/src/styles/globals.css`

```css
:root {
  /* Steel Foundation */
  --background: 10 10 12;           /* obsidian */
  --surface: 20 20 24;              /* carbon */
  --surface-elevated: 28 28 34;     /* slate */
  --border: 58 58 68;               /* zinc */

  /* Text hierarchy */
  --foreground: 138 138 148;        /* muted body */
  --foreground-strong: 180 180 190; /* emphasized */
  --foreground-whisper: 90 90 100;  /* de-emphasized */

  /* Life accents */
  --accent-life: 74 107 74;         /* sage */
  --accent-glow: 196 167 125;       /* spore */

  /* Remove warm earth tones from defaults */
  /* Remove accent: 233 69 96 (was town-highlight) */
}
```

### 1.3 Animation Token Changes

**Changes to make**:
- Remove `--ease-spring` (bounce is banned)
- Change `breathe` keyframe amplitude from 30% → 2%
- Add `--duration-emergence: 250ms`
- Remove/deprecate vine-flow continuous animation

---

## Phase 2: Component Audit

### 2.1 High-Impact Components (Touch First)

| Component | Current State | Stark Biome Change |
|-----------|--------------|-------------------|
| `Layout.tsx` | Warm background | → `steel-obsidian` bg |
| `ElasticCard.tsx` | Rounded, shadow | → `rounded-bare`, minimal shadow |
| `Breathe.tsx` | Continuous breathing | → Only for living elements, amplitude ↓ |
| `Pop.tsx` | Spring bounce | → Simple fade emergence |
| `UnfurlPanel.tsx` | Organic unfurl | → Mechanical slide |
| `OrganicToast.tsx` | Warm styling | → Cool steel frame, life-colored content |

### 2.2 Color Usage Audit

Run grep to find all color usages:
```bash
grep -r "town-" impl/claude/web/src/         # Legacy warm colors
grep -r "jewel-" impl/claude/web/src/        # Jewel colors (keep but mute)
grep -r "bg-\[" impl/claude/web/src/         # Arbitrary colors
grep -r "text-\[" impl/claude/web/src/       # Arbitrary text colors
```

### 2.3 Animation Audit

Find and assess all animations:
```bash
grep -r "animate-" impl/claude/web/src/
grep -r "@keyframes" impl/claude/web/src/
grep -r "transition" impl/claude/web/src/
```

---

## Phase 3: Surgical Changes (Minimal Diff)

### 3.1 Background Shift

**Before**: `bg-gray-900` / `bg-town-bg`
**After**: `bg-steel-obsidian`

This single change transforms the entire feel.

### 3.2 Card Treatment

**Before**:
```jsx
<div className="rounded-lg bg-town-surface shadow-lg">
```

**After**:
```jsx
<div className="rounded-bare bg-steel-carbon border border-steel-zinc/20">
```

Key changes:
- Rounded → `rounded-bare` (2px)
- Remove shadow → add subtle border
- Warm surface → cool steel

### 3.3 Text Hierarchy

**Before**: White text on dark
**After**: Muted gray text, with rare bright moments

```jsx
// Headings: cool, reserved
<h1 className="text-steel-zinc uppercase tracking-wide">

// Body: muted, doesn't compete
<p className="text-[#8A8A94]">

// Accent: earned, rare
<span className="text-glow-spore">
```

### 3.4 Interactive States

**Before**: Warm highlight on hover
**After**: Subtle glow emergence

```jsx
// Before
className="hover:bg-town-highlight"

// After
className="hover:bg-steel-gunmetal hover:border-life-sage/30"
```

### 3.5 Animation Restraint

**Remove from**: Idle cards, backgrounds, decorative elements
**Keep for**: Active agents, live data, user presence indicators

```jsx
// Before: Everything breathes
<div className="animate-breathe">

// After: Only living things breathe
{isAlive && <div className="animate-breathe-subtle">}
```

---

## Phase 4: Component-by-Component

### 4.1 Layout Shell

**File**: `impl/claude/web/src/components/layout/Layout.tsx`

```diff
- <div className="min-h-screen bg-gray-900 text-white">
+ <div className="min-h-screen bg-steel-obsidian text-[#8A8A94]">
```

### 4.2 Navigation

**File**: Sidebar/Nav components

- Remove warm accent colors
- Use `steel-zinc` for inactive, `glow-spore` for active
- Uppercase labels with tracking

### 4.3 Cards

**File**: `impl/claude/web/src/components/elastic/ElasticCard.tsx`

```diff
- className="rounded-lg bg-town-surface shadow-lg hover:shadow-xl"
+ className="rounded-bare bg-steel-carbon border border-steel-zinc/10
+            hover:border-steel-zinc/30 transition-colors duration-200"
```

### 4.4 Buttons

Primary button: life-sage bg, minimal
Secondary button: transparent, border only
Ghost button: just text, glow on hover

### 4.5 Joy Components

**Transform**:
- `Breathe.tsx` → Reduce amplitude, longer period
- `Pop.tsx` → Remove spring, use fade-in
- `Shake.tsx` → Keep (rare error feedback)
- `Shimmer.tsx` → Keep for loading only

**Remove/Deprecate**:
- Continuous vine animations
- Particle effects
- Decorative parallax

---

## Phase 5: Validation

### 5.1 Visual Regression

- Screenshot key pages before/after
- Ensure the 90/10 ratio feels right
- Check that "alive" elements still feel alive

### 5.2 Accessibility Check

- Contrast ratios still pass WCAG
- Focus states visible (use `glow-spore` ring)
- Motion respectful of `prefers-reduced-motion`

### 5.3 Performance

- Fewer animations = better perf
- Measure FPS on older devices

---

## Migration Checklist

### Tokens
- [ ] Update `tailwind.config.js` with stark colors
- [ ] Update `globals.css` custom properties
- [ ] Update `animations.css` (remove bounce, add emergence)
- [ ] Create `stark-biome.css` theme file

### Components (Priority Order)
1. [ ] `Layout.tsx` - background shift
2. [ ] `ElasticCard.tsx` - card treatment
3. [ ] `ElasticContainer.tsx` - surface colors
4. [ ] Navigation components - text hierarchy
5. [ ] Button variants - interaction states
6. [ ] `Breathe.tsx` - amplitude reduction
7. [ ] `Pop.tsx` - remove spring
8. [ ] `UnfurlPanel.tsx` - mechanical slide
9. [ ] `OrganicToast.tsx` - cool frame

### Pages
- [ ] Brain dashboard
- [ ] Witness dashboard
- [ ] Trail explorer
- [ ] AGENTESE docs
- [ ] Landing/home

### Cleanup
- [ ] Remove unused warm color tokens
- [ ] Deprecate continuous animation classes
- [ ] Update component docs

---

## Risk Mitigation

**Risk**: Too stark, loses personality
**Mitigation**: The 10% life is crucial. Test that glow moments feel earned.

**Risk**: Accessibility regression
**Mitigation**: Check contrast ratios for all text on new backgrounds

**Risk**: Large diff, hard to review
**Mitigation**: Phase approach. Each phase is a reviewable PR.

---

## Success Criteria

1. **90/10 Rule Visible**: Screenshots show mostly steel with rare life moments
2. **Stillness Default**: No continuous animations on non-living elements
3. **Earned Glow**: Active/interactive states use bioluminescent accents
4. **Typography Hierarchy**: Clear steel-voice vs organic-voice distinction
5. **Performance**: Equal or better than before (fewer animations)

---

*"Don't decorate. Let the rare color moments feel earned."*
