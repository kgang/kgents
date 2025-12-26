# Loss Primitives

Universal coherence thermometer components for displaying loss values throughout the kgents system.

## Philosophy

Loss represents coherence drift from axioms:
- **0.00**: Axiom — perfect coherence, bright green
- **0.50**: Uncertain — yellow
- **1.00**: Nonsense — incoherent, red

STARK BIOME aesthetic: Green (life-sage) → Yellow (degraded) → Orange (warning) → Red (critical)

## Components

### LossIndicator

Single loss value display with optional label and gradient bar.

```tsx
import { LossIndicator } from '@/primitives/Loss';

// Basic usage
<LossIndicator loss={0.42} />

// With label
<LossIndicator loss={0.42} showLabel />

// With gradient bar
<LossIndicator loss={0.42} showGradient />

// Interactive with navigation
<LossIndicator
  loss={0.42}
  interactive
  onNavigate={(direction) => console.log(`Navigate ${direction}`)}
/>

// Size variants
<LossIndicator loss={0.42} size="sm" />
<LossIndicator loss={0.42} size="md" />
<LossIndicator loss={0.42} size="lg" />
```

### LossGradient

Navigation by loss — clickable gradient bar showing the full loss spectrum.

```tsx
import { LossGradient } from '@/primitives/Loss';

// Basic usage
<LossGradient
  currentLoss={0.42}
  onNavigate={(targetLoss) => console.log(`Navigate to ${targetLoss}`)}
/>

// Without tick marks
<LossGradient currentLoss={0.42} showTicks={false} />

// Custom dimensions
<LossGradient
  currentLoss={0.42}
  width="200px"
  height="24px"
/>
```

### LossHeatmap

Multiple items colored by loss — grid or list view with loss-based coloring.

```tsx
import { LossHeatmap } from '@/primitives/Loss';

const items = [
  { id: '1', label: 'Axiom Layer', loss: 0.05, onClick: () => {} },
  { id: '2', label: 'Value Layer', loss: 0.25, onClick: () => {} },
  { id: '3', label: 'Domain Layer', loss: 0.65, onClick: () => {} },
  { id: '4', label: 'Impl Layer', loss: 0.85, onClick: () => {} },
];

// Grid layout (default)
<LossHeatmap items={items} />

// List layout
<LossHeatmap items={items} layout="list" />

// Custom grid columns
<LossHeatmap items={items} columns={3} />

// Without loss values
<LossHeatmap items={items} showValue={false} />
```

### WithLoss

HOC/wrapper that adds a loss indicator overlay to any component.

```tsx
import { WithLoss } from '@/primitives/Loss';

// Wrap any component
<WithLoss loss={0.42}>
  <YourComponent />
</WithLoss>

// With label
<WithLoss loss={0.42} showLabel>
  <YourComponent />
</WithLoss>

// Position variants
<WithLoss loss={0.42} position="top-left">
  <YourComponent />
</WithLoss>

<WithLoss loss={0.42} position="bottom-right">
  <YourComponent />
</WithLoss>

// With gradient
<WithLoss loss={0.42} showGradient>
  <YourComponent />
</WithLoss>
```

## Design Tokens

All components use STARK BIOME color tokens from `src/design/tokens.css`:

```css
--health-healthy: #22c55e;   /* 0.00-0.20: Green */
--health-degraded: #facc15;  /* 0.20-0.50: Yellow */
--health-warning: #f97316;   /* 0.50-0.80: Orange */
--health-critical: #ef4444;  /* 0.80-1.00: Red */
```

## Integration Examples

### Feed Items

```tsx
import { FeedItem } from '@/primitives/Feed';
import { WithLoss } from '@/primitives/Loss';

<WithLoss loss={kblock.loss} position="top-right">
  <FeedItem kblock={kblock} {...props} />
</WithLoss>
```

### K-Block Cards

```tsx
import { LossIndicator } from '@/primitives/Loss';

<div className="kblock-card">
  <div className="kblock-card__header">
    <h3>{kblock.title}</h3>
    <LossIndicator loss={kblock.loss} showLabel />
  </div>
  {/* ... */}
</div>
```

### Layer Navigation

```tsx
import { LossGradient } from '@/primitives/Loss';

<LossGradient
  currentLoss={currentLayer.loss}
  onNavigate={(targetLoss) => {
    // Find layer closest to target loss
    const layer = findLayerByLoss(targetLoss);
    navigateToLayer(layer);
  }}
/>
```

### Coherence Dashboard

```tsx
import { LossHeatmap } from '@/primitives/Loss';

const layers = [
  { id: '1', label: 'Axiom', loss: 0.05, onClick: () => navigateToLayer(1) },
  { id: '2', label: 'Value', loss: 0.15, onClick: () => navigateToLayer(2) },
  { id: '3', label: 'Capability', loss: 0.35, onClick: () => navigateToLayer(3) },
  { id: '4', label: 'Domain', loss: 0.55, onClick: () => navigateToLayer(4) },
  { id: '5', label: 'Service', loss: 0.65, onClick: () => navigateToLayer(5) },
  { id: '6', label: 'Construction', loss: 0.75, onClick: () => navigateToLayer(6) },
  { id: '7', label: 'Implementation', loss: 0.85, onClick: () => navigateToLayer(7) },
];

<LossHeatmap items={layers} columns={4} />
```

## Accessibility

All components include:
- ARIA labels for screen readers
- Keyboard navigation support (where interactive)
- High contrast mode support
- Reduced motion support

## Performance

All components are memoized using `React.memo` for optimal performance.
