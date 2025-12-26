# Constitutional Primitives

> Visualize adherence to the 7 kgents constitutional principles

## The 7 Principles

From `spec/principles.md`:

1. **Tasteful** - Each agent serves a clear, justified purpose
2. **Curated** - Intentional selection over exhaustive cataloging
3. **Ethical** - Agents augment human capability, never replace judgment
4. **Joy-Inducing** - Delight in interaction; personality matters
5. **Composable** - Agents are morphisms in a category; composition is primary
6. **Heterarchical** - Agents exist in flux, not fixed hierarchy
7. **Generative** - Spec is compression; design should generate implementation

## Components

### ConstitutionalRadar (Hero Component)

7-spoke radar chart showing all principles at once. Pure SVG, interactive, beautiful.

```tsx
import { ConstitutionalRadar } from '@/primitives/Constitutional';

<ConstitutionalRadar
  scores={{
    tasteful: 0.9,
    curated: 0.85,
    ethical: 0.95,
    joyInducing: 0.8,
    composable: 0.9,
    heterarchical: 0.75,
    generative: 0.88,
  }}
  size="md"
  showLabels={true}
  interactive={true}
  onPrincipleClick={(principle) => console.log(principle)}
/>
```

**Props:**
- `scores: ConstitutionalScores` - Principle scores (0-1 range)
- `size?: 'sm' | 'md' | 'lg'` - Size variant (default: 'md')
- `showLabels?: boolean` - Show principle labels around perimeter (default: true)
- `interactive?: boolean` - Enable hover effects and breathing animation (default: false)
- `onPrincipleClick?: (principle) => void` - Click handler for vertices

**Design:**
- Heptagonal (7-sided) radar chart
- Color-coded vertices: green (>0.8), yellow (0.5-0.8), red (<0.5)
- Concentric grid lines at 0.2, 0.4, 0.6, 0.8, 1.0
- Axis lines from center to each vertex
- Subtle glow on hover (interactive mode)
- Breathing animation for high scores (>0.8)

---

### PrincipleScore

Single principle badge/pill for inline display.

```tsx
import { PrincipleScore } from '@/primitives/Constitutional';

<PrincipleScore
  principle="composable"
  score={0.92}
  showLabel={true}
  size="md"
  onClick={(principle) => console.log(principle)}
/>
```

**Props:**
- `principle: PrincipleKey` - Which principle to display
- `score: number` - Score value (0-1)
- `showLabel?: boolean` - Show principle label (default: true)
- `size?: 'sm' | 'md' | 'lg'` - Size variant
- `onClick?: (principle) => void` - Click handler

**Design:**
- Pill-shaped badge with color-coded dot
- Short label ("Taste", "Joy", "Compose", etc.)
- Percentage value with tier color
- Hover effects if clickable

---

### AllPrincipleScores

Grid of all 7 principle badges.

```tsx
import { AllPrincipleScores } from '@/primitives/Constitutional';

<AllPrincipleScores
  scores={{
    tasteful: 0.9,
    curated: 0.85,
    // ... all 7 scores
  }}
  showLabels={true}
  size="md"
  layout="grid"
  onPrincipleClick={(principle) => console.log(principle)}
/>
```

**Props:**
- `scores: ConstitutionalScores` - All principle scores
- `showLabels?: boolean` - Show labels (default: true)
- `size?: 'sm' | 'md' | 'lg'` - Size variant
- `layout?: 'row' | 'grid'` - Layout variant
- `onPrincipleClick?: (principle) => void` - Click handler

**Design:**
- Auto-fit grid (responsive)
- Falls back to row layout on small screens
- Consistent spacing and alignment

---

### ConstitutionalSummary

Overall constitutional score with optional breakdown.

```tsx
import { ConstitutionalSummary } from '@/primitives/Constitutional';

// Compact variant (badge only)
<ConstitutionalSummary
  scores={{ /* all 7 scores */ }}
  variant="compact"
  size="md"
/>

// Expanded variant (badge + breakdown)
<ConstitutionalSummary
  scores={{ /* all 7 scores */ }}
  variant="expanded"
  showBreakdown={true}
  size="md"
/>
```

**Props:**
- `scores: ConstitutionalScores` - All principle scores
- `variant?: 'compact' | 'expanded'` - Display variant (default: 'compact')
- `showBreakdown?: boolean` - Show individual principles (expanded only, default: true)
- `size?: 'sm' | 'md' | 'lg'` - Size variant

**Design:**
- Overall score = average of all 7 principles
- Tier-based left border (green/yellow/red)
- Compact: Just badge with score
- Expanded: Header + AllPrincipleScores grid

---

## Types

### ConstitutionalScores

```typescript
interface ConstitutionalScores {
  tasteful: number;      // 0-1
  curated: number;       // 0-1
  ethical: number;       // 0-1
  joyInducing: number;   // 0-1
  composable: number;    // 0-1
  heterarchical: number; // 0-1
  generative: number;    // 0-1
}
```

### PrincipleKey

```typescript
type PrincipleKey =
  | 'tasteful'
  | 'curated'
  | 'ethical'
  | 'joyInducing'
  | 'composable'
  | 'heterarchical'
  | 'generative';
```

---

## Utilities

### calculateOverallScore

```typescript
import { calculateOverallScore } from '@/primitives/Constitutional';

const overall = calculateOverallScore(scores); // 0-1 (average)
```

### getScoreTier

```typescript
import { getScoreTier } from '@/primitives/Constitutional';

const tier = getScoreTier(0.85); // 'high' | 'medium' | 'low'
```

### getScoreColor

```typescript
import { getScoreColor } from '@/primitives/Constitutional';

const color = getScoreColor(0.85); // CSS var (--health-healthy, etc.)
```

### formatScore

```typescript
import { formatScore } from '@/primitives/Constitutional';

const formatted = formatScore(0.8567); // "86%"
```

---

## Color Coding

Scores are color-coded by tier:

| Tier | Range | Color | CSS Variable |
|------|-------|-------|--------------|
| High | >0.8 | Green | `--health-healthy` |
| Medium | 0.5-0.8 | Yellow | `--health-degraded` |
| Low | <0.5 | Red | `--health-critical` |

---

## Design Philosophy

**STARK Biome**: "The frame is humble. The content glows."

- **90% Steel**: Background surfaces, borders, frames (cool industrial)
- **10% Life**: Earned glow for high scores (organic accents)
- **Brutalist foundations**: No decoration, pure function
- **Breathing UI**: Subtle pulse on high scores (prefers-reduced-motion safe)
- **Tier-based signaling**: Green = good, yellow = attention, red = concern

---

## Accessibility

- Semantic HTML with ARIA labels
- Keyboard navigation support
- Focus indicators for interactive elements
- Respects `prefers-reduced-motion`
- Respects `prefers-contrast: high`
- Screen reader friendly

---

## Example Usage

### Dashboard Widget

```tsx
<ConstitutionalSummary
  scores={scores}
  variant="compact"
  size="sm"
/>
```

### Analysis Panel

```tsx
<div className="analysis-panel">
  <ConstitutionalRadar
    scores={scores}
    size="lg"
    interactive={true}
    onPrincipleClick={(p) => navigate(`/principles/${p}`)}
  />
  <ConstitutionalSummary
    scores={scores}
    variant="expanded"
    showBreakdown={true}
  />
</div>
```

### Inline Indicators

```tsx
<div className="agent-card">
  <h3>K-gent</h3>
  <AllPrincipleScores
    scores={scores}
    layout="row"
    size="sm"
    showLabels={false}
  />
</div>
```

---

## File Structure

```
Constitutional/
├── README.md                    (this file)
├── index.ts                     (exports)
├── types.ts                     (shared types and utilities)
├── ConstitutionalRadar.tsx      (hero component)
├── ConstitutionalRadar.css
├── PrincipleScore.tsx           (badge component)
├── PrincipleScore.css
├── ConstitutionalSummary.tsx    (summary component)
└── ConstitutionalSummary.css
```

---

## Related

- **Spec**: `spec/principles.md` - The 7 constitutional principles
- **Design tokens**: `src/design/tokens.css` - STARK biome colors
- **Patterns**: `docs/skills/elastic-ui-patterns.md` - Responsive patterns

---

*"Daring, bold, creative, opinionated but not gaudy"*
