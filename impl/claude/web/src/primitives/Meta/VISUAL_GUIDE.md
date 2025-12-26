# CoherenceTimeline Visual Guide

## Overview

The CoherenceTimeline component visualizes coherence score evolution over time with breakthrough detection and layer distribution analysis.

## Visual Anatomy

```
┌─────────────────────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ [Timeline] [Distribution]              [Export MD] [Export SVG] │   │  Header
│ └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  100% ┤                                                                 │
│       │                                              🏆                 │
│       │                                            ●                    │
│   75% ┤                                    ●     ●                      │  Y-axis (Score)
│       │                            ●     ●                              │
│   50% ┤                    ●     ●                                      │
│       │            ●     ●                                              │
│   25% ┤    ●     ●                                                      │
│       │  ●                                                              │
│    0% └─────────────────────────────────────────────────────────────   │
│       Dec 1                                                  Dec 30    │  X-axis (Time)
│                                                                         │
│ ┌──────────────────────────────────────────────────────────────────┐   │
│ │ [Tooltip]                                                        │   │  Hover tooltip
│ │ 82.3%                                                            │   │
│ │ Dec 15, 2:30 PM                                                  │   │
│ │ def456a                                                          │   │
│ │ 🏆 Breakthrough                                                  │   │
│ └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Color Palette (STARK BIOME)

### Timeline View

| Element | Color | CSS Variable | Usage |
|---------|-------|--------------|-------|
| Line | Moss/Sage Green | `--color-life-sage` | Main timeline path |
| Normal Points | Sage | `--color-life-sage` | Regular data points (5px radius) |
| Breakthrough Points | Amber | `--color-glow-amber` | Significant jumps (8px radius) |
| Breakthrough Badge | - | - | 🏆 emoji, 16px above point |
| Grid Lines | Steel | `--surface-3` | Horizontal score reference lines |
| Tooltip Background | Steel | `--surface-2` | Hover tooltip surface |
| Tooltip Border | Spore | `--color-glow-spore` | Earned glow on tooltip |

### Distribution View

| Layer | Color | CSS Variable |
|-------|-------|--------------|
| 0 | Steel | `--color-steel-300` |
| 1 | Sage | `--color-life-sage` |
| 2 | Lichen | `--color-glow-lichen` |
| 3 | Spore | `--color-glow-spore` |
| 4+ | Amber | `--color-glow-amber` |

## Interaction States

### Hover (Timeline)
- Point grows slightly
- Drop shadow appears: `drop-shadow(0 0 8px var(--color-life-sage))`
- Tooltip appears above point (centered, translated -50% X)
- Transition: `--transition-fast` (120ms)

### Hover (Distribution Arc)
- Opacity: 0.8
- Brightness: 1.2
- Cursor: pointer

### Active Tab
- Background: `--color-life-moss`
- Border: `--color-life-sage`
- Text: `--color-life-mint`

### Inactive Tab
- Background: `--surface-2`
- Border: `--surface-3`
- Text: `--text-secondary`

## Animations

### Breakthrough Badge Pulse
```css
@keyframes breakthrough-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}
```
- Duration: 2s (4-7-8 breathing pattern inspiration)
- Easing: ease-in-out
- Infinite loop

### Tooltip Appear
```css
@keyframes tooltip-appear {
  from { opacity: 0; transform: translateX(-50%) translateY(4px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
```
- Duration: 120ms (`--transition-fast`)
- Easing: `--ease-out`

## Typography

| Element | Font Family | Size | Weight | Color |
|---------|-------------|------|--------|-------|
| Tab Label | `--font-mono` | `--font-size-sm` | medium | Varies by state |
| Action Button | `--font-mono` | `--font-size-xs` | normal | `--text-secondary` |
| Tooltip Score | `--font-mono` | `--font-size-lg` | bold | `--color-life-sage` |
| Tooltip Date | `--font-mono` | `--font-size-xs` | normal | `--text-muted` |
| Tooltip Commit | `--font-mono` | `--font-size-xs` | normal | `--text-secondary` |
| Axis Labels | `--font-mono` | 12px | normal | `--text-muted` |

## Layout

### Spacing
- Container padding: `--space-lg` (20px)
- Header gap: `--space-md` (13.6px)
- Tab gap: `--space-xs` (3.2px)
- Distribution legend gap: `--space-sm` (6.4px)

### Border Radius
- Container: `--radius-bare` (2px) — Bare Edge philosophy
- Tabs/Buttons: `--radius-subtle` (3px)
- Tooltip: `--radius-subtle` (3px)
- Legend color box: `--radius-bare` (2px)

### Z-Index
- Tooltip: `--z-dropdown` (200)
- SVG: default (stacking context within container)

## Responsive Breakpoints

### Desktop (>768px)
```
┌─────────────────────────────────────────────┐
│ [Timeline] [Distribution]  [Export buttons] │
│                                             │
│ [Full-width timeline graph]                 │
│                                             │
│ [Pie chart] [Legend →]                      │
└─────────────────────────────────────────────┘
```

### Tablet (640-768px)
```
┌────────────────────────────┐
│ [Timeline] [Distribution]  │
│ [Export buttons]           │
│                            │
│ [Full-width timeline]      │
│                            │
│ [Pie chart]                │
│ [Legend ↓]                 │
└────────────────────────────┘
```

### Mobile (<640px)
```
┌──────────────────┐
│ [Timeline]       │
│ [Distribution]   │
│ [Export buttons] │
│                  │
│ [Scrollable SVG] │
│                  │
│ [Pie chart]      │
│ [Legend]         │
└──────────────────┘
```

## Data Flow

1. **Input**: Array of `CoherencePoint[]`
2. **Sort**: By timestamp (ascending)
3. **Enrich**: Calculate breakthrough flags (delta > 2x avg)
4. **Scale**: Map timestamps → X pixels, scores → Y pixels
5. **Render**: SVG path + circles + labels
6. **Aggregate**: Sum layer distributions across all points
7. **Export**: Markdown summary or SVG snapshot

## Breakthrough Detection Algorithm

```typescript
// Calculate average delta between consecutive points
const deltas = points.slice(1).map((p, i) => p.score - points[i].score);
const avgDelta = deltas.reduce((sum, d) => sum + Math.abs(d), 0) / deltas.length;

// Threshold: 2x average = breakthrough
const threshold = avgDelta * 2;

// Mark breakthroughs
points.forEach((point, i) => {
  if (i === 0) return;
  const delta = point.score - points[i - 1].score;
  point.breakthrough = delta > threshold;
});
```

## Export Formats

### Markdown
```markdown
# Coherence Timeline

## Summary
- Total Points: 30
- Current Score: 82.3%
- Breakthroughs: 3

## Timeline
- Dec 1, 10:00 AM: 65.0% (abc123f)
- 🏆 Dec 15, 2:30 PM: 82.3% (def456a)
- ...

## Layer Distribution
- Layer 0: 240
- Layer 1: 180
- Layer 2: 90
- Layer 3: 30
```

### SVG
Complete SVG export with:
- Grid lines
- Path
- Points
- Labels
- Breakthrough badges

Suitable for importing into Figma, Illustrator, or embedding in documentation.

## Accessibility

- All interactive elements are keyboard accessible
- Hover states provide visual feedback
- Color is not the only indicator (size, labels, badges)
- Monospace fonts for numerical data (easy to scan)

## Performance

- All calculations memoized with `useMemo`
- SVG rendering native browser performance
- No external chart library dependency
- Tooltip only renders when hovering (conditional)
- Scales well up to ~1000 points

## Future Enhancements

- Zoom/pan for long timelines
- Brush selection for time range
- Animated path drawing on mount
- Click point → navigate to commit
- Stacked area chart mode for layers
- Comparison view (two timelines)
