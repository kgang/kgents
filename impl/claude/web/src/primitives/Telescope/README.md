# Telescope Primitive

> "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."

A universal viewer with focal distance, aperture, and filter controls. Replaces GaloisTelescope (1,200 LOC) + TelescopeNavigator (800 LOC) + supporting components (2,582 LOC) = **4,582 LOC → 952 LOC** (79% reduction).

## Architecture

The Telescope is a composable primitive with five clean components:

```
Telescope/
├── types.ts              (116 LOC) — Pure types, no logic
├── utils.ts              (246 LOC) — Pure functions for positioning, coloring, navigation
├── useTelescopeNavigation.ts (70 LOC) — React hook for loss-guided navigation
├── Telescope.tsx         (324 LOC) — Main component with SVG rendering
├── Telescope.css         (165 LOC) — STARK BIOME styling
└── index.ts              (31 LOC)  — Barrel exports
```

**Total: 952 LOC** (776 LOC excluding comments/blanks)

## Philosophy

### The Telescope Metaphor

- **Focal Distance** (0-1): Ground level (L7) → Cosmic (L1)
  - `0.0`: Ground (L7 only - Representations)
  - `0.5`: Mid-range (L4-L7 - Specs through Representations)
  - `1.0`: Cosmic (L1-L7 - All layers including Axioms)

- **Loss as Landscape**: Nodes colored by semantic stability
  - Purple (`#440154`): Low loss, stable, well-grounded
  - Blue-green (`#31688e`): Mid loss, moderate drift
  - Yellow (`#fde724`): High loss, semantic drift, needs attention

- **Gradients as Guide**: Arrows point toward lower loss (stability)
  - Green: Stable gradient (magnitude < 0.4)
  - Orange: Warning gradient (magnitude 0.4-0.7)
  - Red: Critical gradient (magnitude > 0.7)

## Usage

### Basic Example

```tsx
import { Telescope } from '@/primitives/Telescope';

function ZeroSeedView() {
  const nodes: NodeProjection[] = [
    {
      node_id: 'axiom-1',
      layer: 1,
      position: { x: 400, y: 100 },
      scale: 1.0,
      opacity: 1.0,
      is_focal: false,
      color: '#440154',
      loss: 0.2,
    },
    // ... more nodes
  ];

  const gradients = new Map([
    ['axiom-1', { x: 0.5, y: 0.3, magnitude: 0.6 }],
    // ... more gradients
  ]);

  return (
    <Telescope
      nodes={nodes}
      gradients={gradients}
      onNodeClick={(nodeId) => console.log('Clicked:', nodeId)}
      onNavigate={(nodeId, direction) =>
        console.log(`Navigated to ${nodeId} via ${direction}`)
      }
      keyboardEnabled
    />
  );
}
```

### Navigation Hook

```tsx
import { useTelescopeNavigation } from '@/primitives/Telescope';

function CustomNavigator({ nodes, gradients }) {
  const { goLowestLoss, goHighestLoss, followGradientFrom } =
    useTelescopeNavigation({
      nodes,
      gradients,
      onNavigate: (nodeId, direction) => {
        console.log(`Navigated to ${nodeId} via ${direction}`);
      },
    });

  return (
    <div>
      <button onClick={goLowestLoss}>Find Stability</button>
      <button onClick={goHighestLoss}>Find Drift</button>
      <button onClick={() => followGradientFrom('current-node')}>
        Follow Gradient
      </button>
    </div>
  );
}
```

### Utility Functions

```tsx
import {
  focalDistanceToLayers,
  calculateNodePosition,
  getLossColor,
  findLowestLossNode,
} from '@/primitives/Telescope';

// Map focal distance to visible layers
const layers = focalDistanceToLayers(0.5); // [4, 5, 6, 7]

// Calculate node position
const pos = calculateNodePosition(
  { layer: 4, id: 'spec-1' },
  allNodes,
  0.5, // focal distance
  800, // width
  600  // height
);

// Get loss color
const color = getLossColor(0.7); // '#fde724' (yellow - high loss)

// Find most stable node
const mostStable = findLowestLossNode(nodes);
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `l` | Navigate to lowest loss (most stable) |
| `h` | Navigate to highest loss (needs attention) |
| `Shift+G` | Follow gradient toward stability |
| `+` / `-` | Zoom in / out (adjust focal distance) |

## Comparison to Previous Implementation

### Before (4,582 LOC)

```
GaloisTelescope.tsx       1,200 LOC
TelescopeNavigator.tsx      800 LOC
types.ts                    250 LOC
LossNode.tsx                180 LOC
GradientField.tsx           220 LOC
LossLegend.tsx              150 LOC
useTelescopeNavigation.ts   280 LOC
GaloisTelescope.css         200 LOC
ZeroSeed.css                150 LOC
Supporting utilities      1,152 LOC
--------------------------------
TOTAL                     4,582 LOC
```

### After (952 LOC)

```
Telescope.tsx             324 LOC  (unified component)
utils.ts                  246 LOC  (pure functions)
types.ts                  116 LOC  (clean types)
Telescope.css             165 LOC  (STARK BIOME)
useTelescopeNavigation.ts  70 LOC  (focused hook)
index.ts                   31 LOC  (exports)
--------------------------------
TOTAL                     952 LOC
```

**Reduction: 3,630 LOC (79%)**

## Design Principles

1. **Composable**: Pure functions + React hook + SVG component
2. **Tasteful**: STARK BIOME styling (90% steel, 10% earned glow)
3. **Testable**: All logic in pure functions (utils.ts)
4. **Typed**: Full TypeScript coverage
5. **Performant**: Memoized calculations, minimal re-renders
6. **Accessible**: Keyboard navigation, semantic colors

## What Was Removed

- **Eliminated Abstractions**: LossNode, GradientField, LossLegend components folded into Telescope.tsx
- **Simplified Types**: Removed intermediate types (GaloisTelescopeState → TelescopeState)
- **Unified Styling**: Single CSS file vs. 3 separate stylesheets
- **Streamlined Navigation**: Single hook vs. complex state machine
- **Direct SVG**: No intermediate rendering layers

## What Was Preserved

- **Loss-guided navigation**: All navigation modes (lowest, highest, gradient)
- **Focal distance metaphor**: Layer visibility based on zoom
- **Gradient visualization**: Arrows pointing toward stability
- **Keyboard controls**: Same keybindings (l, h, Shift+G, +/-)
- **STARK BIOME aesthetics**: Steel foundation with earned glow
- **Viridis colormap**: Purple (stable) → Yellow (drift)

## Testing

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Telescope } from '@/primitives/Telescope';

test('renders nodes and handles clicks', () => {
  const nodes = [/* ... */];
  const handleClick = jest.fn();

  render(
    <Telescope
      nodes={nodes}
      gradients={new Map()}
      onNodeClick={handleClick}
    />
  );

  // Click a node
  const node = screen.getByTestId('node-axiom-1');
  fireEvent.click(node);
  expect(handleClick).toHaveBeenCalledWith('axiom-1');
});

test('navigates to lowest loss on "l" key', () => {
  const nodes = [
    { node_id: 'a', loss: 0.8 },
    { node_id: 'b', loss: 0.2 },
  ];
  const handleNavigate = jest.fn();

  render(
    <Telescope
      nodes={nodes}
      gradients={new Map()}
      onNavigate={handleNavigate}
      keyboardEnabled
    />
  );

  fireEvent.keyDown(window, { key: 'l' });
  expect(handleNavigate).toHaveBeenCalledWith('b', 'lowest');
});
```

## Future Enhancements

- [ ] Layer shape variation (circle, diamond, star, etc.)
- [ ] Edge rendering (show connections between nodes)
- [ ] Minimap (overview of entire graph)
- [ ] Touch/mobile navigation
- [ ] Export to SVG/PNG
- [ ] Animation on navigation
- [ ] Search/filter nodes by content

## License

Part of kgents. See root LICENSE.
