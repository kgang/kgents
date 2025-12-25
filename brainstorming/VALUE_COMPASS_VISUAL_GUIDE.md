# ValueCompass Visual Guide

```
                                Tasteful (0°)
                                     │
                                     ●
                                   ╱   ╲
                                 ╱       ╲
                               ╱           ╲
                             ╱               ╲
                           ╱                   ╲
         Generative ●────●                       ●──── Curated
          (308.57°)    ╱   ╲                   ╱        (51.43°)
                     ╱       ╲               ╱
                   ╱           ╲           ╱
                 ╱               ╲       ╱
               ╱                   ╲   ╱
             ╱                       ●
           ●                         │                    ●
  Heterarchical                 [CENTER]             Ethical
   (257.14°)                        │                 (102.86°)
             ╲                       ●
               ╲                   ╱   ╲
                 ╲               ╱       ╲
                   ╲           ╱           ╲
                     ╲       ╱               ╲
                       ╲   ╱                   ╲
                         ●                       ●
                    Composable              Joy-Inducing
                    (205.71°)                (154.29°)
```

## Components

### 1. Grid Circles (25%, 50%, 75%, 100%)
```
Subtle steel rings at quartile distances
Color: var(--surface-3)
Opacity: 0.15 (inner), 0.3 (outer)
```

### 2. Axes
```
Dashed lines from center to each principle
Color: var(--surface-3)
Style: stroke-dasharray: 2 2
```

### 3. Current Scores (Filled Polygon)
```
Fill: rgba(196, 167, 125, 0.2) — Glow spore at 20%
Stroke: var(--accent-primary) — Glow spore
Shadow: 0 0 12px rgba(196, 167, 125, 0.4)
```

### 4. Trajectory (Historical Positions)
```
Faint trails showing previous scores
Fill: rgba(196, 167, 125, 0.05)
Stroke: var(--accent-primary)
Opacity: 0.2 + (index / total) * 0.3 (fade in over time)
```

### 5. Attractor Basin (Optional)
```
Dashed outline showing personality range
Fill: rgba(139, 169, 139, 0.05) — Glow lichen at 5%
Stroke: var(--accent-secondary) — Glow lichen
Style: stroke-dasharray: 4 4
```

### 6. Attractor Coordinates (Optional)
```
Dashed polygon showing target personality
Fill: rgba(139, 169, 139, 0.1)
Stroke: var(--accent-secondary)
Style: stroke-dasharray: 6 3
Shadow: 0 0 8px rgba(139, 169, 139, 0.3)
```

### 7. Score Vertices
```
Circles at each principle intersection
Fill: var(--accent-primary)
Stroke: var(--surface-0) (2px)
Radius: 4px (compact: 3px)
Hover: grows to 6px with glow
```

### 8. Principle Labels
```
Text around perimeter
Font: monospace, 12px (compact: 10px)
Color: var(--text-secondary)
Hover: var(--accent-primary-bright)
```

## Layer Order (Bottom to Top)

1. Grid circles
2. Axes
3. Attractor basin (if present)
4. Attractor coordinates (if present)
5. Trajectory (if present)
6. Current scores (filled polygon)
7. Score vertices
8. Principle labels

## Colors (STARK BIOME)

### Steel (90% — The Frame)
- `--surface-0`: #0a0a0c (deepest background)
- `--surface-1`: #141418 (card background)
- `--surface-2`: #1c1c22 (elevated)
- `--surface-3`: #28282f (borders, grid)
- `--text-secondary`: #8a8a94 (labels)
- `--text-muted`: #5a5a64 (hints)

### Glow (10% — The Content)
- `--accent-primary`: #c4a77d (glow spore — main)
- `--accent-primary-bright`: #d4b88c (glow amber — hover)
- `--accent-secondary`: #8ba98b (glow lichen — attractor)
- `--color-glow-amber`: #d4b88c (earned glow on hover)

## Animations

### Breathing (Container)
```css
@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.02); opacity: 0.95; }
}
```
Duration: 3s ease-in-out infinite
Trigger: hover on container

### Glow (Vertices)
```css
.score-vertex:hover {
  fill: var(--accent-primary-bright);
  r: 6;
  filter: drop-shadow(0 0 8px rgba(196, 167, 125, 0.8));
}
```
Duration: 0.3s ease
Trigger: hover on vertex

### Earned Glow (Specific Principles)
```css
tasteful, joyInducing, generative:
  fill: var(--color-glow-amber);
  text-shadow: 0 0 10px rgba(212, 184, 140, 0.6);
```

## Example States

### Kent's Personality (High Scores)
```typescript
{
  tasteful: 0.95,      // Very high — "Tasteful > feature-complete"
  curated: 0.85,       // High — Intentional selection
  ethical: 0.80,       // High — Augment, never replace
  joyInducing: 0.90,   // Very high — "Joy-inducing > merely functional"
  composable: 0.75,    // Above average — Category theory
  heterarchical: 0.70, // Above average — Flux, not fixed
  generative: 0.92,    // Very high — "The persona is a garden"
}
```

### Early Agent (Learning)
```typescript
{
  tasteful: 0.50,      // Neutral
  curated: 0.50,       // Neutral
  ethical: 0.70,       // Good default
  joyInducing: 0.40,   // Low (generic responses)
  composable: 0.60,    // Moderate
  heterarchical: 0.50, // Neutral
  generative: 0.50,    // Neutral
}
```

### Convergence Path
```
Initial → Learning → Converged
  0.50      0.70       0.95    (tasteful)
  0.40      0.65       0.90    (joyInducing)
  0.50      0.70       0.92    (generative)
```

## Responsive Behavior

### Full Size (default)
- Container: max-width 400px
- Labels: full text ("Joy-Inducing")
- Vertices: 4px radius
- Grid: 4 circles

### Compact Mode
- Container: max-width 250px
- Labels: 3-char abbreviation ("Joy")
- Vertices: 3px radius
- Grid: 4 circles (same)

### Mobile (< 640px)
- Container: 100% width
- Labels: 10px font
- Rest: same as full size

## Integration Example

```tsx
// In DirectorDashboard
import { ValueCompass } from '@/primitives/ValueCompass';

function DirectorDashboard() {
  const [scores, setScores] = useState<ConstitutionScores>(...);
  
  return (
    <div className="dashboard">
      <section className="principles-section">
        <h2>Constitutional Alignment</h2>
        <ValueCompass 
          scores={scores}
          trajectory={historicalScores}
          attractor={kentAttractor}
        />
      </section>
    </div>
  );
}
```

