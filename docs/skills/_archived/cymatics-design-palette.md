# Cymatics Design Palette

The official visual language for kgents, based on cymatics (sound-made-visible) patterns.

## Philosophy

> "The eye finds what it likes faster than the mind predicts."

These patterns represent the intersection of physics, mathematics, and aesthetics. Each pattern family has specific use cases within the kgents ecosystem.

## Pattern Families

### 1. Chladni (Standing Waves)
**Use cases:** Loading states, phase transitions

Classic Chladni plate patterns showing standing wave nodes. Physics-inspired, mathematical beauty.

| Preset | Description | Speed |
|--------|-------------|-------|
| `chladni-4-5` | Cyan, balanced symmetry | 0.7 |
| `chladni-3-7` | Orange, asymmetric tension | 0.42 |
| `chladni-6-6` | Purple, inverted, complex | 0.56 |

### 2. Interference (Ripples)
**Use cases:** Connection visualization, network activity

Multiple circular waves from point sources creating interference patterns. Water-like, organic.

| Preset | Description | Speed |
|--------|-------------|-------|
| `interference-4` | Cyan, 4 sources | 1.4 |
| `interference-6` | Red/pink, 6 sources | 1.12 |

### 3. Mandala (Sacred Geometry)
**Use cases:** Soul/consciousness states, meditation mode

Radial symmetry with angular harmonics. Spiritual, centering.

| Preset | Description | Speed |
|--------|-------------|-------|
| `mandala-6` | Purple, 6-fold symmetry | 0.7 |
| `mandala-8` | Cyan, 8-fold symmetry | 0.42 |

### 4. Flow (Organic Noise)
**Use cases:** Ambient backgrounds, idle states

Layered simplex noise creating organic, natural movement.

| Preset | Description | Speed |
|--------|-------------|-------|
| `flow-calm` | Cyan, gentle | 0.42 |
| `flow-turbulent` | Orange, energetic | 0.84 |

### 5. Reaction (Turing Patterns)
**Use cases:** Agent evolution, emergence visualization

Reaction-diffusion inspired patterns. Biological, emergent.

| Preset | Description | Speed |
|--------|-------------|-------|
| `reaction-spots` | Teal, leopard-like | 0.56 |
| `reaction-stripes` | Neutral, zebra-like | 0.42 |

### 6. Spiral (Logarithmic)
**Use cases:** Brain topology, memory crystallization

Golden ratio spirals. Mathematical harmony, meditative.

| Preset | Description | Speed | Note |
|--------|-------------|-------|------|
| `spiral-3` | Purple, 3 arms | 0.5 | **Original speed preserved** |
| `spiral-5` | Cyan, 5 arms | 0.4 | **Original speed preserved** |

> **Design Decision:** Spiral patterns maintain their original slower speeds to preserve their meditative quality. All other patterns are 40% faster.

### 7. Voronoi (Cellular)
**Use cases:** Memory crystals, data clustering

Cellular/crystalline structures based on nearest-neighbor distance.

| Preset | Description | Speed |
|--------|-------------|-------|
| `voronoi-sparse` | Cyan, large cells | 0.7 |
| `voronoi-dense` | Orange/inverted, small cells | 0.42 |

### 8. Moiré (Optical Interference)
**Use cases:** Subtle backgrounds, layered UI depth

Overlapping linear patterns creating optical illusions.

| Preset | Description | Speed |
|--------|-------------|-------|
| `moiré-subtle` | Neutral, barely visible | 0.28 |
| `moiré-bold` | Cyan, pronounced | 0.42 |

### 9. Fractal (Self-Similar)
**Use cases:** Infinite zoom, complexity visualization

Julia set variations with animated constants.

| Preset | Description | Speed |
|--------|-------------|-------|
| `fractal-julia` | Purple, classic | 0.7 |
| `fractal-deep` | Orange/inverted, high iteration | 0.42 |

## Color Families

| Hue Range | Color | Usage |
|-----------|-------|-------|
| ~0.55 | **Cyan** | Primary brand, brain/memory |
| ~0.75-0.85 | **Purple** | Soul/spiritual, K-gent |
| ~0.08 | **Orange** | Energy/action, alerts |
| ~0.0 (low sat) | **Neutral** | Subtle backgrounds |

## Usage in Code

```tsx
import { PatternTile, PATTERN_PRESETS, CURATED_PRESETS } from '@/components/three/CymaticsSampler';

// Use a specific preset
<PatternTile config={PATTERN_PRESETS['spiral-5']} size={2} />

// Iterate curated presets
{CURATED_PRESETS.map(name => (
  <PatternTile key={name} config={PATTERN_PRESETS[name]} />
))}
```

## Animation Speed Guidelines

- **Default patterns:** 40% faster than original for better responsiveness
- **Spiral patterns:** Original speed preserved for meditative quality
- **Speed values:** Multiplied into shader's `uTime * uSpeed * [family_factor]`

## Version History

- **v1.0** (2025-12-16): Initial palette with 19 curated presets
  - Fixed spiral horizontal line artifact
  - Increased animation speeds by 40% (except spirals)
  - Formalized color families and use cases
