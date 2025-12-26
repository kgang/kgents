# Constitutional Primitives - Quick Reference

## Import

```tsx
import {
  ConstitutionalRadar,
  PrincipleScore,
  AllPrincipleScores,
  ConstitutionalSummary,
  type ConstitutionalScores,
  type PrincipleKey,
} from '@/primitives/Constitutional';
```

---

## Components at a Glance

| Component | Purpose | When to Use |
|-----------|---------|-------------|
| `ConstitutionalRadar` | 7-spoke radar chart | Dashboards, full analysis |
| `PrincipleScore` | Single principle badge | Inline, headers, cards |
| `AllPrincipleScores` | Grid of 7 badges | Breakdown sections |
| `ConstitutionalSummary` | Overall score card | Widgets, summaries |

---

## Quick Examples

### Radar Chart

```tsx
<ConstitutionalRadar
  scores={scores}
  size="md"
  interactive={true}
  onPrincipleClick={(p) => navigate(`/principles/${p}`)}
/>
```

### Single Badge

```tsx
<PrincipleScore
  principle="composable"
  score={0.92}
  size="sm"
/>
```

### All Badges

```tsx
<AllPrincipleScores
  scores={scores}
  layout="grid"
  size="md"
/>
```

### Summary Card

```tsx
<ConstitutionalSummary
  scores={scores}
  variant="expanded"
  showBreakdown={true}
/>
```

---

## The 7 Principles

```tsx
type PrincipleKey =
  | 'tasteful'      // Clear, justified purpose
  | 'curated'       // Intentional selection
  | 'ethical'       // Augments human capability
  | 'joyInducing'   // Delight in interaction
  | 'composable'    // Morphisms in a category
  | 'heterarchical' // Flux, not hierarchy
  | 'generative';   // Spec is compression
```

---

## Score Object

```tsx
const scores: ConstitutionalScores = {
  tasteful: 0.92,      // 0-1 range
  curated: 0.88,
  ethical: 0.95,
  joyInducing: 0.82,
  composable: 0.90,
  heterarchical: 0.75,
  generative: 0.85,
};
```

---

## Color Tiers

| Range | Tier | Color |
|-------|------|-------|
| > 0.8 | High | 🟢 Green |
| 0.5-0.8 | Medium | 🟡 Yellow |
| < 0.5 | Low | 🔴 Red |

---

## Sizes

| Size | Use Case |
|------|----------|
| `sm` | Compact, tight spaces |
| `md` | Default, most uses |
| `lg` | Hero sections, focus |

---

## Utilities

```tsx
import {
  calculateOverallScore,
  getScoreTier,
  getScoreColor,
  formatScore,
} from '@/primitives/Constitutional';

const overall = calculateOverallScore(scores); // 0.872
const tier = getScoreTier(0.85);               // 'high'
const color = getScoreColor(0.85);             // 'var(--health-healthy)'
const formatted = formatScore(0.8567);         // "86%"
```

---

## Common Patterns

### Dashboard Widget

```tsx
<div className="widget">
  <h3>Agent Health</h3>
  <ConstitutionalSummary scores={scores} variant="compact" size="sm" />
</div>
```

### Full Panel

```tsx
<div className="panel">
  <ConstitutionalRadar scores={scores} size="lg" interactive={true} />
  <AllPrincipleScores scores={scores} layout="grid" />
</div>
```

### Inline Badge

```tsx
<div className="header">
  <h2>K-gent</h2>
  <PrincipleScore principle="composable" score={0.92} size="sm" />
</div>
```

---

## Files

```
Constitutional/
├── index.ts                     # Exports
├── types.ts                     # Shared types
├── ConstitutionalRadar.tsx      # Radar chart
├── PrincipleScore.tsx           # Badge
├── ConstitutionalSummary.tsx    # Summary
├── README.md                    # Full docs
├── VISUAL_GUIDE.md              # Visual examples
├── QUICK_REF.md                 # This file
└── SHOWCASE.tsx                 # Live demo
```

---

*For full documentation, see `README.md` and `VISUAL_GUIDE.md`*
