# Loss Primitives — Visual Guide

Visual reference for all Loss primitive components.

## Color Scale

Loss represents coherence drift from axioms. The color scale uses STARK BIOME palette:

```
0.00 ────────── 0.20 ────────── 0.50 ────────── 0.80 ────────── 1.00
GREEN           YELLOW          ORANGE          RED             DARK RED
Axiom           Warning         Alert           Critical        Nonsense
Coherent        Some drift      Significant     Maximum         Incoherent
#22c55e         #facc15         #f97316         #ef4444         #ef4444
```

## LossIndicator

Single loss value display with multiple variants.

### Basic (Dot Only)
```
Loss: 0.42  ●
            ^
            Color-coded dot
```

### With Label
```
Loss: 0.42  ●
^           ^
Label       Dot
```

### With Gradient Bar
```
Loss: 0.42  [████████──────────────]  ●
            ^                         ^
            Full gradient             Marker at position
            Green → Yellow → Red
```

### Interactive
```
Loss: 0.42  [████████──────────────]  ●  [↓] [↑]
                                         ^   ^
                                    Lower  Higher
                                    Navigation buttons
```

### Size Variants

```
Small:  Loss: 0.42  ●      (8px dot)
Medium: Loss: 0.42  ●      (12px dot)
Large:  Loss: 0.42  ●      (16px dot)
```

## LossGradient

Clickable gradient bar for navigation by loss.

```
┌────────────────────────────────────────────────────────────┐
│  [█████████████████████████████████████████████████████]  │
│   Green────────Yellow────────Orange────────Red             │
│               ▲                                            │
│               │                                            │
│          Current position (0.42)                           │
│                                                            │
│  0.00    0.25         0.50         0.75         1.00       │
│   ▼       ▼           ▼            ▼            ▼          │
└────────────────────────────────────────────────────────────┘
     ^       ^           ^            ^            ^
     Tick marks with labels

Click anywhere on the bar to navigate to that loss value.
```

## LossHeatmap

Multiple items colored by loss.

### Grid Layout (4 columns)

```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Axiom    │ │ Value    │ │ Capabil. │ │ Domain   │
│ 0.05  ●  │ │ 0.15  ●  │ │ 0.35  ●  │ │ 0.55  ●  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
   Green       Lt Green      Yellow       Orange

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Service  │ │ Constr.  │ │ Impl     │ │ Deprec.  │
│ 0.65  ●  │ │ 0.75  ●  │ │ 0.85  ●  │ │ 0.95  ●  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
   Orange      Lt Red        Red          Dark Red

Background color intensity increases with loss.
Border color indicates loss threshold.
Dot in top-right corner shows status at a glance.
```

### List Layout

```
┌────────────────────────────────────────────────────┐
│ Axiom Layer                              0.05  ●   │
└────────────────────────────────────────────────────┘
   Subtle green background, green border

┌────────────────────────────────────────────────────┐
│ Value Layer                              0.25  ●   │
└────────────────────────────────────────────────────┘
   Light yellow background, yellow border

┌────────────────────────────────────────────────────┐
│ Domain Layer                             0.65  ●   │
└────────────────────────────────────────────────────┘
   Orange background, orange border
```

## WithLoss

Wrapper that adds loss indicator overlay to any component.

### Position Variants

```
Top-Left Position:
┌─────────────────────────────────┐
│ ● Loss: 0.42                    │
│                                 │
│   Sample K-Block                │
│                                 │
│   This is a sample component    │
│   wrapped with loss indicator.  │
│                                 │
└─────────────────────────────────┘

Top-Right Position (default):
┌─────────────────────────────────┐
│                    ● Loss: 0.42 │
│                                 │
│   Sample K-Block                │
│                                 │
│   This is a sample component    │
│   wrapped with loss indicator.  │
│                                 │
└─────────────────────────────────┘

Bottom-Left Position:
┌─────────────────────────────────┐
│                                 │
│   Sample K-Block                │
│                                 │
│   This is a sample component    │
│   wrapped with loss indicator.  │
│                                 │
│ ● Loss: 0.42                    │
└─────────────────────────────────┘

Bottom-Right Position:
┌─────────────────────────────────┐
│                                 │
│   Sample K-Block                │
│                                 │
│   This is a sample component    │
│   wrapped with loss indicator.  │
│                                 │
│                    ● Loss: 0.42 │
└─────────────────────────────────┘
```

## Integration Examples

### Feed Item with Loss

```
┌───────────────────────────────────────────────────────┐
│ L1  Axiom Title                    Loss: 0.05  ●  2h │
│ ──────────────────────────────────────────────────────│
│ Author | 3 edges | axiom, coherent, foundational     │
│                                                       │
│ Preview text appears here...                          │
│                                                       │
│ [Edit]  [View]  [Dismiss]                             │
└───────────────────────────────────────────────────────┘
```

### K-Block Card with Loss Header

```
┌───────────────────────────────────────────┐
│  K-Block Title          Loss: 0.42  ●     │
│  ─────────────────────────────────────────│
│                                           │
│  Content goes here...                     │
│                                           │
│  Tags: value, draft, needs-review         │
│                                           │
└───────────────────────────────────────────┘
```

### Layer Navigation Dashboard

```
Coherence Dashboard
─────────────────────────────────────────────────────

Current Loss: 0.42

Navigate by Loss:
[████████████████──────────────────────────]
Green──────Yellow──────Orange──────Red
  ▲
  Current position

0.00    0.25      0.50      0.75      1.00


Layer Breakdown:
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Axiom    │ │ Value    │ │ Capabil. │ │ Domain   │
│ 0.05  ●  │ │ 0.15  ●  │ │ 0.35  ●  │ │ 0.55  ●  │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐
│ Service  │ │ Constr.  │ │ Impl     │
│ 0.65  ●  │ │ 0.75  ●  │ │ 0.85  ●  │
└──────────┘ └──────────┘ └──────────┘
```

## Design Principles

1. **Universal Color Language**: Green = coherent, Red = incoherent
2. **Progressive Disclosure**: Start with dot, add label/gradient as needed
3. **Contextual Integration**: Works as overlay, inline, or standalone
4. **STARK BIOME Aesthetic**: Muted colors, earned glow, no decoration
5. **Composable**: Mix and match primitives for different use cases
6. **Density-Aware**: Adapts to compact/comfortable/spacious modes

## Accessibility

- Color is not the only indicator (labels, values, positions)
- ARIA labels for screen readers
- Keyboard navigation for interactive elements
- High contrast mode support
- Reduced motion support
