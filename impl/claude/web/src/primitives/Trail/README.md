# Trail

Derivation breadcrumb with PolicyTrace compression ratios.

## Overview

Trail displays navigation paths as horizontal breadcrumbs with:
- **Semantic journey** through derivation steps
- **PolicyTrace compression** metrics (0-1)
- **Principle indicators** at each step (optional)
- **Intelligent collapsing** for long paths

Pure React implementation. Total LOC: 247 (component) + 183 (styles) = 430.

## Philosophy

> "The proof IS the decision. The mark IS the witness."

Trail shows the epistemic trajectory, not file paths. Each step represents a semantic decision point in the derivation chain, optionally annotated with constitutional principle scores.

## Replaces

This primitive consolidates three existing components:
1. **DerivationTrail.tsx** - Breadcrumb aspect
2. **FocalDistanceRuler.tsx** - Principle indicators
3. **BranchTree.tsx** - Path navigation breadcrumbs

## Usage

### Basic Breadcrumb

```tsx
import { Trail } from '@/primitives/Trail';

const path = ['axioms', 'values', 'goals', 'specs', 'actions'];

<Trail path={path} />
```

### With Compression Ratio

Shows PolicyTrace compression from Zero Seed analysis:

```tsx
<Trail
  path={path}
  compressionRatio={0.42} // 42% compressed
/>
```

### With Principle Scores

Display constitutional adherence at each step:

```tsx
import type { ConstitutionScores } from '@/types/theory';

const principleScores: ConstitutionScores[] = [
  { tasteful: 0.9, curated: 0.8, ethical: 0.85, ... }, // Step 0
  { tasteful: 0.85, curated: 0.9, ethical: 0.88, ... }, // Step 1
  // ... one per step
];

<Trail
  path={path}
  showPrinciples
  principleScores={principleScores}
/>
```

### Interactive Navigation

Click steps to navigate back:

```tsx
<Trail
  path={path}
  currentIndex={3} // Highlight step 3
  onStepClick={(stepIndex, stepId) => {
    console.log(`Navigate to step ${stepIndex}: ${stepId}`);
  }}
/>
```

### Long Paths (Intelligent Collapsing)

Automatically collapses middle steps:

```tsx
const longPath = [
  'root', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'current'
];

<Trail
  path={longPath}
  maxVisible={7} // Shows: root, a, ..., i, current
/>
```

### Compact Mode

Minimal single-line version:

```tsx
<Trail path={path} compact />
```

## Props

```typescript
interface TrailProps {
  /** Navigation path as array of step IDs or names */
  path: string[];

  /** Compression ratio from PolicyTrace (0-1) */
  compressionRatio?: number;

  /** Show principle scores at each step */
  showPrinciples?: boolean;

  /** Principle scores per step (if showPrinciples=true) */
  principleScores?: ConstitutionScores[];

  /** Click handler for path steps */
  onStepClick?: (stepIndex: number, stepId: string) => void;

  /** Maximum visible steps before collapsing */
  maxVisible?: number; // Default: 7

  /** Compact mode (single line, minimal labels) */
  compact?: boolean;

  /** Current step index (highlights as active) */
  currentIndex?: number;
}
```

## Styling

Uses STARK BIOME design system:
- **90% steel** - Cool industrial grays (#141418, #28282f)
- **10% earned glow** - Warm amber accents (#c4a77d)
- **Breathing animation** on current step
- **Subtle hover glow** on clickable steps

Colors from `globals.css`:
- `--color-steel-carbon` - Background (#141418)
- `--color-steel-slate` - Elevated surfaces (#1c1c22)
- `--color-glow-spore` - Primary accent (#c4a77d)
- `--accent-primary` - Highlights (#c4a77d)

## Principle Color Mapping

Each constitutional principle has a unique color:

| Principle | Color | Hex |
|-----------|-------|-----|
| Tasteful | Glow Lichen | #8ba98b |
| Curated | Glow Spore | #c4a77d |
| Ethical | Life Sage | #4a6b4a |
| Joy-Inducing | Glow Amber | #d4b88c |
| Composable | Life Mint | #6b8b6b |
| Heterarchical | Life Sprout | #8bab8b |
| Generative | Glow Light | #e5c99d |

## Path Collapsing Logic

When `path.length > maxVisible`:
1. Show first 2 steps
2. Insert `...` ellipsis
3. Show last 2 steps

Example:
```
Before: A → B → C → D → E → F → G → H
After:  A → B → ... → G → H
```

## Integration Points

Use Trail in:
- **Hypergraph Editor** - Show node derivation chain
- **Zero Seed Telescope** - Navigate focal distance layers
- **Director Dashboard** - Display document ancestry
- **Chat Interface** - Show conversation fork paths
- **Witness UI** - Trace mark provenance

## Theory Integration

Trail validates the theory system by:
1. **PolicyTrace compression** - Quantify derivation efficiency
2. **ConstitutionScores** - Show principle adherence per step
3. **Semantic paths** - Navigate epistemic structure, not filesystem

See `/Users/kentgang/git/kgents/impl/claude/web/src/types/theory.ts` for type definitions.

## Architecture

```
primitives/Trail/
├── Trail.tsx         # Main component (247 LOC)
├── Trail.css         # STARK styling (183 LOC)
├── index.ts          # Exports (4 LOC)
└── README.md         # This file
```

Theory types at:
```
types/theory.ts       # ConstitutionScores, PolicyTrace
```

## Performance

- **Memoized rendering** - Only re-renders on path/scores change
- **Lightweight DOM** - Minimal wrapper elements
- **CSS animations** - Hardware-accelerated transforms
- **Smart collapsing** - O(1) path computation

## Accessibility

- `aria-label` on navigation
- `aria-current="location"` on current step
- `title` tooltips with full step IDs
- Keyboard navigable buttons
- High contrast steel/glow palette
- Screen reader friendly labels

## Example: Zero Seed Navigation

```tsx
import { Trail } from '@/primitives/Trail';
import { useTelescope } from '@/hooks/useTelescopeState';

function ZeroSeedBreadcrumb() {
  const { state } = useTelescope();

  // Convert focal history to path
  const path = state.focalHistory.map(item => item.nodeId);
  if (state.focalPoint) {
    path.push(state.focalPoint);
  }

  return (
    <Trail
      path={path}
      currentIndex={path.length - 1}
      onStepClick={(idx, nodeId) => {
        // Navigate back in telescope
        const historyItem = state.focalHistory[idx];
        if (historyItem) {
          dispatch({
            type: 'SET_FOCAL_POINT',
            nodeId: historyItem.nodeId,
            layer: historyItem.layer
          });
        }
      }}
    />
  );
}
```

## Example: PolicyTrace Compression

```tsx
import { Trail } from '@/primitives/Trail';
import type { PolicyTrace } from '@/types/theory';

function PolicyTrailView({ trace }: { trace: PolicyTrace }) {
  const path = trace.decisions.map(d => d.action);

  return (
    <Trail
      path={path}
      compressionRatio={trace.compressionRatio}
      showPrinciples
      principleScores={trace.trajectory}
    />
  );
}
```

## Future Enhancements

Potential additions (not yet implemented):
- **Loss gradients** - Color-code steps by loss value
- **Branching indicators** - Show fork points in path
- **Diff highlighting** - Compare two trails side-by-side
- **Minimap** - Bird's-eye view of entire path

## Related Primitives

- **ValueCompass** - Visualize principle scores as radar chart
- **Telescope** - Navigate focal distance layers
- **Witness** - Display mark provenance chains
- **Graph** - Show hypergraph structure

## Testing

The component is designed for:
- **Unit tests** - Path collapsing logic
- **Visual tests** - CSS animations and hover states
- **Integration tests** - Navigation callbacks
- **Accessibility tests** - Screen reader compatibility
