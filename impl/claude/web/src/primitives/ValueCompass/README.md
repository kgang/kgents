# ValueCompass

Constitutional principle visualization for kgents value system.

## Overview

ValueCompass displays the 7 constitutional principles as a radar/compass chart with:
- **Current scores** (0-1 for each principle)
- **Decision trajectory** over time (optional)
- **Personality attractor** basin and coordinates (optional)

Pure CSS implementation - no D3 dependency. Total LOC: 389 (component) + 48 (types) = 437.

## The 7 Principles

1. **Tasteful** - Each agent serves a clear, justified purpose
2. **Curated** - Intentional selection over exhaustive cataloging
3. **Ethical** - Agents augment human capability, never replace judgment
4. **Joy-Inducing** - Delight in interaction
5. **Composable** - Agents are morphisms in a category
6. **Heterarchical** - Agents exist in flux, not fixed hierarchy
7. **Generative** - Spec is compression

## Usage

```tsx
import { ValueCompass } from '@/primitives/ValueCompass';
import type { ConstitutionScores } from '@/types/theory';

const scores: ConstitutionScores = {
  tasteful: 0.9,
  curated: 0.8,
  ethical: 0.85,
  joyInducing: 0.95,
  composable: 0.7,
  heterarchical: 0.75,
  generative: 0.9,
};

<ValueCompass scores={scores} />
```

## With Trajectory

Shows historical decision evolution:

```tsx
const trajectory: ConstitutionScores[] = [
  { tasteful: 0.5, curated: 0.5, ... }, // Earlier
  { tasteful: 0.7, curated: 0.6, ... }, // Middle
  { tasteful: 0.9, curated: 0.8, ... }, // Recent
];

<ValueCompass scores={scores} trajectory={trajectory} />
```

## With Personality Attractor

Shows target personality basin:

```tsx
const attractor: PersonalityAttractor = {
  coordinates: { tasteful: 0.95, curated: 0.85, ... },
  basin: [
    { tasteful: 0.90, curated: 0.80, ... },
    { tasteful: 0.92, curated: 0.88, ... },
  ],
  stability: 0.85,
};

<ValueCompass 
  scores={scores} 
  trajectory={trajectory}
  attractor={attractor}
/>
```

## Compact Mode

```tsx
<ValueCompass scores={scores} compact />
```

## Styling

Uses STARK BIOME design system:
- **90% steel** - Cool industrial grays
- **10% earned glow** - Warm amber accents
- **Breathing animation** on hover
- **Earned glow** on principle highlights

Colors from `globals.css`:
- `--surface-0/1/2/3` - Background layers
- `--accent-primary` - Glow spore (#c4a77d)
- `--accent-secondary` - Glow lichen (#8ba98b)

## Theory Integration

This primitive validates the theory system by:
1. **ConstitutionScores** - Quantifying adherence to principles
2. **PolicyTrace** - Tracking decision evolution
3. **PersonalityAttractor** - Modeling stable personality basins

See `/Users/kentgang/git/kgents/impl/claude/web/src/types/theory.ts` for full type definitions.

## Example

See `ValueCompassExample.tsx` for a live demo with:
- Animated convergence toward attractor
- Trajectory visualization
- Toggle for attractor display
- Compact mode comparison

## Architecture

```
primitives/ValueCompass/
├── ValueCompass.tsx         # Main component (231 LOC)
├── ValueCompass.css         # STARK styling (209 LOC)
├── ValueCompassExample.tsx  # Demo (141 LOC)
├── index.ts                 # Exports (8 LOC)
└── README.md                # This file
```

Theory types at:
```
types/theory.ts              # 48 LOC
```

## Integration Points

Can be integrated into:
- **Director dashboard** - Show constitutional alignment
- **Decision panels** - Visualize principle trade-offs
- **Agent profiles** - Display personality attractors
- **Audit views** - Track principle drift over time

## Performance

- Pure CSS transforms (no SVG rendering overhead for shapes)
- SVG used only for paths and text labels
- Memoized path computation
- Lightweight transitions (< 300ms)

## Accessibility

- `aria-label` on SVG
- High contrast steel/glow palette
- Keyboard navigable (hover states)
- Text labels for screen readers
