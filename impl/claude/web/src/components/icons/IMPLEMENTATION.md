# KGENTS ICON/GLYPH SYSTEM IMPLEMENTATION

**Created**: 2025-12-24
**Status**: Complete, Production-Ready
**Philosophy**: Mathematical notation meets ancient glyphs. Stillness, then life.

---

## What Was Built

A holistic icon/glyph system to replace emojis with authentic, whimsical glyphs that embody the STARK BIOME aesthetic.

### Files Created

```
src/components/icons/
├── glyphs.ts                 # Glyph constant definitions + helper functions
├── Glyph.tsx                 # React component for rendering glyphs
├── glyph.css                 # STARK BIOME styling + breathing animation
├── LucideAllowlist.tsx       # Curated subset of Lucide icons
├── GlyphShowcase.tsx         # Visual demo component
├── glyph-showcase.css        # Showcase styling
├── index.ts                  # Unified exports
├── README.md                 # Comprehensive documentation
└── IMPLEMENTATION.md         # This file
```

---

## Design Philosophy (FROM CLAUDE.md)

This implementation rigorously follows the STARK BIOME philosophy:

### Core Principles

1. **90% Steel, 10% Life**
   - Steel foundation (monochrome, precision)
   - Life emerges through interaction (earned glow)

2. **Mathematical Notation + Ancient Glyphs**
   - NOT emojis, NOT decorative icons
   - Proof-engine operations: `⊢` (witness), `⊨` (decide), `∘` (compose)
   - Categorical precision: `◇` (entity), `◈` (morphism)

3. **Stillness, Then Life**
   - No animation by default
   - Breathing animation uses 4-7-8 asymmetric timing (6.75s cycle)
   - Movement is earned, not given

4. **Flat Geometric Precision**
   - NO 3D effects, glassmorphism, gradients, Y2K metallic
   - YES steel surfaces, monochrome + single accent, bare edges

---

## Glyph Categories (7)

### 1. Status (`status`)
Geometric state indicators:
- `healthy` → `●` (filled circle)
- `degraded` → `◐` (half-filled)
- `dormant` → `○` (hollow)
- `error` → `◆` (solid diamond)
- `warning` → `◇` (hollow diamond)
- `pending` → `◎` (double circle)

### 2. AGENTESE Contexts (`contexts`)
The five-fold ontology:
- `world` → `∴` (therefore — external causality)
- `self` → `∵` (because — internal causality)
- `concept` → `⟨⟩` (angle brackets — abstraction)
- `void` → `∅` (empty set — the accursed share)
- `time` → `⟳` (temporal flow)

### 3. Actions (`actions`)
Proof-engine operations:
- `witness` → `⊢` (turnstile)
- `decide` → `⊨` (double turnstile)
- `compose` → `∘` (ring operator)
- `save` → `⊕` (circled plus)
- `search` → `⌕` (telephone location)
- `analyze` → `⊛` (circled asterisk)
- `edit` → `⎔` (software function)
- `delete` → `⊖` (circled minus)

### 4. Axioms (`axioms`)
The seven principles:
- `entity` → `◇`
- `morphism` → `◈`
- `mirror` → `◉` (Mirror Test)
- `tasteful` → `✧`
- `composable` → `⊛`
- `heterarchical` → `⥮`
- `generative` → `⟐`

### 5. Navigation (`navigation`)
Directional glyphs:
- `back`, `forward`, `up`, `down` → `←`, `→`, `↑`, `↓`
- `expand`, `collapse` → `⌄`, `⌃`
- `menu` → `☰`

### 6. Files (`files`)
Document types:
- `file` → `▫`
- `folder` → `▪`
- `spec` → `◈`
- `code` → `⟨⟩`

### 7. Crown Jewels (`jewels`)
Service identities:
- `brain` → `◬`
- `witness` → `⊢`
- `atelier` → `⌬`
- `liminal` → `◭`

### 8. Hypergraph Modes (`modes`)
Modal editing states:
- `normal` → `◇`
- `insert` → `◈`
- `edge` → `⟡`
- `visual` → `◉`
- `witness` → `⊢`

---

## Breathing Animation (4-7-8 Asymmetric)

The breathing animation follows the STARK BIOME asymmetric pattern:

```
Timing: 6.75s cycle
Opacity range: 0.985 → 1.0 → 0.985

Phase Breakdown:
- Rest (0-15%):        0.985 opacity — stillness before inhale
- Gentle Rise (15-40%): 0.985 → 1.0 — soft inhale
- Brief Hold (40-50%):  1.0 — moment of fullness
- Slow Release (50-95%): 1.0 → 0.985 — long, calming exhale
- Return (95-100%):     0.985 — back to rest
```

**When to use breathing**:
- Health indicators (active, healthy state)
- User presence markers
- Active connections
- Living elements (explicitly marked as "alive")

**When NOT to use**:
- Navigation
- Buttons (until hover)
- Text
- Static content
- Inactive elements

---

## API Surface

### Component Usage

```tsx
import { Glyph } from '@/components/icons';

// Basic
<Glyph name="status.healthy" />

// With size
<Glyph name="actions.witness" size="lg" />

// With breathing animation
<Glyph name="jewels.brain" breathing />

// With custom color
<Glyph name="contexts.world" color="var(--life-sage)" />

// With CSS class
<Glyph name="status.healthy" className="glyph--healthy" />
```

### Helper Functions

```tsx
import { getGlyph, getGlyphCategory, GLYPH_CATEGORIES } from '@/components/icons';

// Get glyph by path
const glyph = getGlyph('status.healthy'); // '●'

// Get all glyphs in category
const statusGlyphs = getGlyphCategory('status');

// Iterate categories
GLYPH_CATEGORIES.forEach(category => {
  console.log(category, getGlyphCategory(category));
});
```

### Lucide Allowlist

```tsx
import { ArrowLeft, Check, Folder } from '@/components/icons';

<ArrowLeft size={16} />
<Check size={14} />
<Folder size={18} />
```

---

## Size Variants

| Size | Font Size | Use Case |
|------|-----------|----------|
| `xs` | 10px | Inline text, compact UI |
| `sm` | 12px | Default inline size |
| `md` | 14px | Standard glyph size (default) |
| `lg` | 18px | Prominent glyphs, headers |

---

## Color Utilities

CSS classes for semantic coloring:

| Class | Color | Use Case |
|-------|-------|----------|
| `glyph--steel` | `--steel-300` | Muted, inactive |
| `glyph--life` | `--life-sage` | Organic accent |
| `glyph--glow` | `--glow-spore` | Earned moment |
| `glyph--healthy` | `--health-healthy` | Success, operational |
| `glyph--degraded` | `--health-degraded` | Partial function |
| `glyph--warning` | `--health-warning` | Caution |
| `glyph--critical` | `--health-critical` | Error, attention |
| `glyph--hover-glow` | (transition) | Earned glow on hover |

---

## Design Tokens Used

All glyphs integrate with the existing STARK BIOME design system:

### From `design-system.css` / `globals.css`:

```css
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;
--steel-300: #a0a0a0;   /* Muted text */
--steel-400: #888;      /* Secondary text */
--life-sage: #4a6b4a;   /* Primary living accent */
--glow-spore: #c4a77d;  /* Warm accent */
--health-healthy: #22c55e;
--health-degraded: #facc15;
--health-warning: #f97316;
--health-critical: #ef4444;
```

### Typography:
- Font family: `var(--font-mono)` for geometric precision
- Letter spacing: `0.02em` for subtle readability
- Line height: `1` for tight vertical alignment

---

## Accessibility

### ARIA Labels
All glyphs include proper ARIA labels for screen readers:

```tsx
// Default: uses glyph name
<Glyph name="status.healthy" />
// aria-label="status healthy"

// Custom label
<Glyph name="status.healthy" aria-label="Service is operational" />
```

### Reduced Motion Support

Built-in support for `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  .glyph--breathing {
    animation: none !important;
  }
}
```

---

## Testing & Validation

### TypeScript Compilation
All files pass strict TypeScript checks:
```bash
cd impl/claude/web && npm run typecheck
# ✓ No errors
```

### Type Safety
- Glyph paths validated via helper functions
- Props typed with `GlyphProps` interface
- Category keys type-checked via `keyof typeof GLYPHS`

---

## Migration Path (Emoji → Glyph)

**Before**:
```tsx
<span>🟢</span> Healthy
<span>⚠️</span> Warning
<span>❌</span> Error
<span>🧠</span> Brain
```

**After**:
```tsx
<Glyph name="status.healthy" className="glyph--healthy" /> Healthy
<Glyph name="status.warning" className="glyph--warning" /> Warning
<Glyph name="status.error" className="glyph--critical" /> Error
<Glyph name="jewels.brain" breathing className="glyph--life" /> Brain
```

---

## Connection to Principles

| Principle | How System Embodies It |
|-----------|------------------------|
| **Tasteful** | Mathematical precision, not decorative |
| **Curated** | 8 categories, ~50 glyphs total (necessary & sufficient) |
| **Ethical** | Accessible (ARIA, reduced motion) |
| **Joy-Inducing** | Breathing animation, earned glow moments |
| **Composable** | Type-safe helpers, consistent API |
| **Heterarchical** | No fixed hierarchy, context determines use |
| **Generative** | Categories generate consistent patterns |

---

## Next Steps (Optional Enhancements)

### Immediate Opportunities
1. **Replace emoji usage** across existing components
2. **Add glyphs to DirectorStatusBadge** (replace colored dots)
3. **Use in navigation** (replace Lucide arrows with glyph navigation)
4. **Hypergraph mode indicators** (replace text with mode glyphs)

### Future Enhancements
1. **Glyph editor** for custom user glyphs
2. **Animation variants** (different breathing speeds)
3. **Context-aware coloring** (auto-color by jewel context)
4. **Glyph combinations** (compose multiple glyphs)

---

## Files to Update (Emoji Replacement)

High-impact files using emojis that could benefit from glyphs:

```bash
# Find emoji usage
grep -r "[\u{1F300}-\u{1F9FF}]" src/ --include="*.tsx" --include="*.ts"
```

Candidates:
- `src/components/director/DirectorStatusBadge.tsx` (status dots)
- `src/components/layout/WitnessFooter.tsx` (witness indicators)
- `src/pages/WelcomePage.tsx` (feature icons)
- Any status indicators, health badges, mode displays

---

## Performance Characteristics

### Bundle Size
- **glyphs.ts**: ~4.7KB (constant definitions)
- **Glyph.tsx**: ~1.9KB (component logic)
- **glyph.css**: ~3.2KB (styles + animation)
- **Total**: ~10KB uncompressed

All glyphs are Unicode characters (no SVG overhead).

### Runtime Performance
- Zero-cost abstraction (direct Unicode rendering)
- GPU-accelerated breathing animation (opacity only)
- Type-safe lookups with constant-time access

---

## Verification Checklist

- [x] TypeScript compilation passes
- [x] All 8 glyph categories defined
- [x] Breathing animation uses 4-7-8 timing (6.75s)
- [x] STARK BIOME color tokens integrated
- [x] Accessibility (ARIA labels, reduced motion)
- [x] Size variants (xs, sm, md, lg)
- [x] Helper functions (getGlyph, getGlyphCategory)
- [x] Lucide allowlist (curated subset)
- [x] Documentation (README.md, IMPLEMENTATION.md)
- [x] Showcase component (GlyphShowcase.tsx)
- [x] No 3D effects, gradients, or glassmorphism
- [x] Monospace font for geometric precision
- [x] Color inherits by default, overridable

---

*"The glyph is notation. The breath is life. The steel is humble. The glow is earned."*

**Implementation complete**: 2025-12-24
**Files created**: 9
**Total lines**: ~750 (excluding docs)
**Status**: Production-ready, awaiting integration
