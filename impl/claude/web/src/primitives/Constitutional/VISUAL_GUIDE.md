# Constitutional Primitives - Visual Guide

> A visual walkthrough of the Constitutional primitives

## Quick Reference

```
ConstitutionalRadar    →  Hero radar chart (7-spoke heptagon)
PrincipleScore         →  Single principle badge
AllPrincipleScores     →  Grid of 7 badges
ConstitutionalSummary  →  Overall score card
```

---

## 1. ConstitutionalRadar (The Hero)

**Purpose**: Visualize all 7 principles at once in a beautiful radar chart.

```tsx
<ConstitutionalRadar
  scores={{
    tasteful: 0.92,
    curated: 0.88,
    ethical: 0.95,
    joyInducing: 0.82,
    composable: 0.90,
    heterarchical: 0.75,
    generative: 0.85,
  }}
  size="md"
  showLabels={true}
  interactive={true}
/>
```

**Visual Structure**:
```
         Tasteful
            ●
          /   \
    Generative Curated
         ●       ●
        /         \
  Hetero-    ○——○  Ethical
  archical
         \       /
          ●     ●
      Composable Joy
```

**Features**:
- 7-sided polygon (heptagon)
- Concentric grid lines (20%, 40%, 60%, 80%, 100%)
- Axis lines from center to vertices
- Color-coded vertices: 🟢 high (>80%), 🟡 medium (50-80%), 🔴 low (<50%)
- Subtle glow on hover
- Breathing animation for high scores (when interactive=true)

**When to use**: Dashboards, analysis panels, full constitutional assessments

---

## 2. PrincipleScore (The Badge)

**Purpose**: Show a single principle score inline.

```tsx
<PrincipleScore
  principle="composable"
  score={0.92}
  showLabel={true}
  size="md"
/>
```

**Visual Structure**:
```
┌──────────────────────┐
│ ● Compose      92%   │  ← Green dot (>0.8)
└──────────────────────┘

┌──────────────────────┐
│ ● Ethics       65%   │  ← Yellow dot (0.5-0.8)
└──────────────────────┘

┌──────────────────────┐
│ ● Joy          42%   │  ← Red dot (<0.5)
└──────────────────────┘
```

**Features**:
- Pill-shaped badge
- Color-coded indicator dot
- Short label (Compose, Joy, Ethics, etc.)
- Percentage value in tier color
- Hover effect if clickable

**When to use**: Inline in cards, headers, lists

---

## 3. AllPrincipleScores (The Grid)

**Purpose**: Show all 7 principle badges in a compact grid.

```tsx
<AllPrincipleScores
  scores={scores}
  layout="grid"
  size="md"
  showLabels={true}
/>
```

**Visual Structure**:
```
┌─────────────────────────────────────┐
│  ● Taste 92%    ● Curate 88%        │
│  ● Ethics 95%   ● Joy 82%           │
│  ● Compose 90%  ● Hetero 75%        │
│  ● Generate 85%                     │
└─────────────────────────────────────┘
```

**Features**:
- Auto-fit grid (responsive to container width)
- Falls back to 2-column on mobile
- Consistent spacing
- Optional click handlers per badge

**When to use**: Breakdown sections, expanded summaries

---

## 4. ConstitutionalSummary (The Overview)

**Purpose**: Overall score with optional breakdown.

### Compact Variant

```tsx
<ConstitutionalSummary
  scores={scores}
  variant="compact"
  size="md"
/>
```

**Visual Structure**:
```
┌───────────────────────────────────┐
│ Constitutional            87%     │ ← Green left border (>80%)
└───────────────────────────────────┘
```

### Expanded Variant

```tsx
<ConstitutionalSummary
  scores={scores}
  variant="expanded"
  showBreakdown={true}
  size="md"
/>
```

**Visual Structure**:
```
┌───────────────────────────────────┐
│ Constitutional Score              │
│ High Adherence            87%     │ ← Green left border
├───────────────────────────────────┤
│  ● Taste 92%    ● Curate 88%      │
│  ● Ethics 95%   ● Joy 82%         │
│  ● Compose 90%  ● Hetero 75%      │
│  ● Generate 85%                   │
└───────────────────────────────────┘
```

**Features**:
- Overall score = average of 7 principles
- Tier label ("High/Moderate/Low Adherence")
- Color-coded left border
- Optional breakdown grid
- Responsive layout

**When to use**: Dashboard widgets, agent cards, summary panels

---

## Color Coding System

All components use the same tier-based color system:

| Score Range | Tier | Color | Visual | Health Var |
|-------------|------|-------|--------|------------|
| > 0.8 | High | Green | 🟢 | `--health-healthy` |
| 0.5 - 0.8 | Medium | Yellow | 🟡 | `--health-degraded` |
| < 0.5 | Low | Red | 🔴 | `--health-critical` |

---

## Layout Patterns

### Dashboard Widget

```tsx
<div className="dashboard-widget">
  <h3>K-gent Health</h3>
  <ConstitutionalSummary
    scores={kgentScores}
    variant="compact"
    size="sm"
  />
</div>
```

### Full Analysis Panel

```tsx
<div className="analysis-panel">
  <div className="panel-header">
    <h2>Constitutional Analysis</h2>
    <ConstitutionalSummary
      scores={scores}
      variant="compact"
      size="md"
    />
  </div>

  <ConstitutionalRadar
    scores={scores}
    size="lg"
    interactive={true}
    onPrincipleClick={(p) => navigate(`/principles/${p}`)}
  />

  <div className="breakdown-section">
    <h3>Individual Principles</h3>
    <AllPrincipleScores
      scores={scores}
      layout="grid"
      size="md"
      onPrincipleClick={(p) => navigate(`/principles/${p}`)}
    />
  </div>
</div>
```

### Agent Card

```tsx
<div className="agent-card">
  <div className="card-header">
    <h3>K-gent</h3>
    <PrincipleScore
      principle="composable"
      score={0.92}
      size="sm"
    />
  </div>
  <p>LLM dialogue, hypnagogia, gatekeeper</p>
  <AllPrincipleScores
    scores={scores}
    layout="row"
    size="sm"
    showLabels={false}
  />
</div>
```

---

## Size Guide

Each component supports 3 sizes:

| Size | Use Case | Dimensions |
|------|----------|------------|
| `sm` | Inline, tight spaces | ConstitutionalRadar: 160px, badges compact |
| `md` | Default, most uses | ConstitutionalRadar: 240px, badges standard |
| `lg` | Hero sections, focus | ConstitutionalRadar: 320px, badges spacious |

---

## Accessibility Features

- ✅ Semantic HTML with ARIA labels
- ✅ Keyboard navigation (`Tab`, `Enter`)
- ✅ Focus indicators (2px outline)
- ✅ Respects `prefers-reduced-motion` (disables animations)
- ✅ Respects `prefers-contrast: high` (thicker borders)
- ✅ Screen reader friendly (descriptive labels)
- ✅ Color + shape encoding (not just color)

---

## Interaction Patterns

### Click-to-Navigate

```tsx
<ConstitutionalRadar
  scores={scores}
  interactive={true}
  onPrincipleClick={(principle) => {
    navigate(`/principles/${principle}`);
  }}
/>
```

### Click-to-Filter

```tsx
<AllPrincipleScores
  scores={scores}
  onPrincipleClick={(principle) => {
    setFilter({ principle, minScore: 0.8 });
  }}
/>
```

### Hover-to-Inspect

```tsx
<PrincipleScore
  principle="composable"
  score={0.92}
  onClick={(principle) => {
    showTooltip(PRINCIPLES[principle].description);
  }}
/>
```

---

## Performance Notes

- ✅ All components are memoized (`React.memo`)
- ✅ Geometry calculated in `useMemo` hooks
- ✅ Pure SVG (no canvas, no heavy libraries)
- ✅ CSS transitions (GPU-accelerated)
- ✅ No layout thrashing
- ✅ Sub-16ms render time (60fps)

---

## Design Tokens Used

From `src/design/tokens.css`:

```css
/* Colors */
--health-healthy: #22c55e;      /* Green (>80%) */
--health-degraded: #facc15;     /* Yellow (50-80%) */
--health-critical: #ef4444;     /* Red (<50%) */

/* Surfaces */
--surface-0: var(--color-steel-obsidian);  /* Deep background */
--surface-1: var(--color-steel-carbon);    /* Card background */
--surface-3: var(--color-steel-gunmetal);  /* Borders */

/* Text */
--text-primary: #e5e7eb;        /* Bright text */
--text-secondary: #8a8a94;      /* Muted text */
--text-muted: #5a5a64;          /* Whisper text */

/* Spacing */
--space-xs: 0.2rem;
--space-sm: 0.4rem;
--space-md: 0.85rem;
--space-lg: 1.25rem;

/* Radius */
--radius-bare: 2px;             /* Cards, containers */
--radius-pill: 9999px;          /* Badges, pills */

/* Transitions */
--transition-fast: 120ms ease-out-expo;
--transition-normal: 200ms ease-in-out-cubic;
```

---

## Example Scores

### Excellent Agent (High Adherence)

```tsx
const excellentScores = {
  tasteful: 0.95,
  curated: 0.90,
  ethical: 0.95,
  joyInducing: 0.88,
  composable: 0.92,
  heterarchical: 0.85,
  generative: 0.90,
};
// Overall: 90% (High Adherence)
```

### Moderate Agent (Medium Adherence)

```tsx
const moderateScores = {
  tasteful: 0.75,
  curated: 0.70,
  ethical: 0.80,
  joyInducing: 0.65,
  composable: 0.72,
  heterarchical: 0.68,
  generative: 0.70,
};
// Overall: 71% (Moderate Adherence)
```

### Struggling Agent (Low Adherence)

```tsx
const strugglingScores = {
  tasteful: 0.45,
  curated: 0.40,
  ethical: 0.55,
  joyInducing: 0.35,
  composable: 0.48,
  heterarchical: 0.42,
  generative: 0.38,
};
// Overall: 43% (Low Adherence)
```

---

## Related Files

- **Components**: `src/primitives/Constitutional/`
- **Types**: `src/primitives/Constitutional/types.ts`
- **Design tokens**: `src/design/tokens.css`
- **Spec**: `spec/principles.md`

---

*"Daring, bold, creative, opinionated but not gaudy"*
