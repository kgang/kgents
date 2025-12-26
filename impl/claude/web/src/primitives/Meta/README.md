# Meta Primitives

**Journey 5: Meta — Watching Yourself Grow**

Components for meta-cognitive visualization, helping users see their coherence journey over time.

## Components

### CoherenceTimeline

Line graph showing coherence score evolution with breakthrough detection.

**Features**:
- SVG-based timeline visualization (no external chart library)
- Hover tooltips with commit details
- Breakthrough badges (🏆) at significant score jumps
- Layer distribution pie chart view
- Export to markdown + SVG

**Usage**:
```tsx
import { CoherenceTimeline } from '@/primitives/Meta';

const points: CoherencePoint[] = [
  {
    timestamp: new Date('2024-12-01T10:00:00Z'),
    score: 0.65,
    commitId: 'abc123f',
    layerDistribution: { 0: 10, 1: 5, 2: 2 },
  },
  {
    timestamp: new Date('2024-12-02T14:30:00Z'),
    score: 0.82,
    commitId: 'def456a',
    layerDistribution: { 0: 8, 1: 7, 2: 3, 3: 1 },
  },
  // ... more points
];

<CoherenceTimeline
  points={points}
  width={800}
  height={400}
/>
```

**Props**:
```typescript
interface CoherencePoint {
  timestamp: Date;
  score: number;              // 0-1 coherence score
  commitId?: string;          // Git commit hash
  breakthrough?: boolean;     // Auto-detected or manually set
  layerDistribution: Record<number, number>; // Layer → count
}

interface CoherenceTimelineProps {
  points: CoherencePoint[];
  width?: number;             // Default: 800
  height?: number;            // Default: 400
  className?: string;
}
```

**Breakthrough Detection**:
Breakthroughs are automatically detected as score jumps >2x the average delta between consecutive points. You can also manually set `breakthrough: true` on any point.

**Views**:
1. **Timeline**: Line graph with points, breakthroughs marked with 🏆
2. **Distribution**: Pie chart showing aggregate layer distribution across all points

**Exports**:
- **Export MD**: Generates markdown report with summary, timeline, and distribution
- **Export SVG**: Downloads the current timeline view as SVG

## Design Tokens

Uses STARK BIOME aesthetic (90% steel, 10% earned glow):

| Element | Color |
|---------|-------|
| Line | `--color-life-sage` (moss/sage green) |
| Normal points | `--color-life-sage` |
| Breakthrough points | `--color-glow-amber` (amber glow) |
| Grid lines | `--surface-3` |
| Tooltip | `--surface-2` with `--color-glow-spore` border |

## Animation

- Breakthrough badges pulse with 4-7-8 breathing pattern (2s cycle)
- Hover states use `--transition-fast` (120ms)
- Tooltip appears with gentle ease-out animation

## Responsive

Works at all densities:
- **Desktop** (>768px): Full layout with side-by-side distribution
- **Tablet** (640-768px): Stacked header, vertical distribution
- **Mobile** (<640px): Compact padding, smaller text, scrollable SVG

## Layer Colors

| Layer | Color | CSS Variable |
|-------|-------|--------------|
| 0 | Steel | `--color-steel-300` |
| 1 | Sage | `--color-life-sage` |
| 2 | Lichen | `--color-glow-lichen` |
| 3 | Spore | `--color-glow-spore` |
| 4+ | Amber | `--color-glow-amber` |

## Implementation Notes

- Pure SVG rendering (no D3, recharts, or other chart library)
- All calculations done in useMemo for performance
- Tooltip positioning uses transform-based centering
- Pie chart uses SVG path arcs (polarToCartesian + describeArc helpers)
- Export functions use Blob API for client-side file generation

## Future Enhancements

- [ ] Zoom/pan support for long timelines
- [ ] Brush selection for time range filtering
- [ ] Animated transitions between data points
- [ ] Click point to navigate to commit
- [ ] Layer distribution stacked area chart mode
- [ ] Comparison mode (two timelines side-by-side)

## Related

- `/primitives/Crystal` - Crystallized insights (input to coherence)
- `/primitives/Witness` - Witnessed marks (source data)
- `/services/witness` - Backend witness service
