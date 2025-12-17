# Skill: 3D Lighting and Visual Clarity Patterns

> *"Shadows are not merely absence of light—they are presence of depth."*

This skill documents the principled approach to 3D lighting, shadows, and visual clarity in kgents visualizations. The core insight: **lighting quality** is a projection dimension, just as **density** is for 2D layout.

---

## The Illumination Quality Isomorphism

Just as AD-008 (Simplifying Isomorphisms) identifies `density` as the single dimension underlying `isMobile/isTablet/isDesktop`, we identify **illumination quality** as the dimension underlying performance vs. fidelity tradeoffs in 3D:

```
Device Capability ≅ Illumination Quality ≅ Shadow Fidelity ≅ Rendering Budget
```

| Quality Level | Shadows | Shadow Map | Light Count | Use Case |
|--------------|---------|------------|-------------|----------|
| `minimal` | None | N/A | 2 (ambient + directional) | Low-end mobile, battery saving |
| `standard` | Soft shadows | 1024px | 3 | Most devices |
| `high` | PCF soft shadows | 2048px | 4 | Desktop, high-end mobile |
| `cinematic` | VSM/CSM | 4096px | 5+ | Presentation, screenshots |

This is **not** a user preference—it is detected from device capability, just as density is detected from viewport size.

---

## The Canonical Lighting Rig

Every kgents 3D scene uses the same **Canonical Lighting Rig**. This ensures visual consistency across all visualizations (BrainTopology, Gestalt, future jewels).

### The Sun Pattern

The primary light source is a **DirectionalLight** positioned to simulate sunlight:

```typescript
// The Canonical Sun - same in ALL kgents 3D scenes
const CANONICAL_SUN = {
  position: [15, 20, 15] as const,  // Upper-right-front quadrant
  intensity: 1.2,
  color: '#ffffff',
  castShadow: true,
  shadow: {
    mapSize: { width: 1024, height: 1024 },  // Parameterized by quality
    camera: {
      near: 0.5,
      far: 50,
      left: -15,
      right: 15,
      top: 15,
      bottom: -15,
    },
    bias: -0.0001,
    normalBias: 0.02,
  },
};
```

**Why this position?** Cognitive science shows humans assume light comes from above-left (the "light from above" prior). Position [15, 20, 15] creates shadows that fall to the lower-right, matching this expectation.

### The Three-Light Minimum

Every scene includes at minimum:

```typescript
// 1. Ambient Fill - prevents pure black shadows
<ambientLight intensity={0.35} />

// 2. Key Light (Sun) - primary shadow caster
<directionalLight
  position={[15, 20, 15]}
  intensity={1.2}
  castShadow
  shadow-mapSize-width={shadowMapSize}
  shadow-mapSize-height={shadowMapSize}
  shadow-camera-near={0.5}
  shadow-camera-far={50}
  shadow-camera-left={-15}
  shadow-camera-right={15}
  shadow-camera-top={15}
  shadow-camera-bottom={-15}
  shadow-bias={-0.0001}
  shadow-normalBias={0.02}
/>

// 3. Fill Light - softens shadows, adds dimension
<pointLight
  position={[-10, -5, -10]}
  intensity={0.4}
  color="#6366f1"  // Cool fill color for depth
/>
```

### Quality-Parameterized Constants

Following the AD-008 pattern, lighting parameters are lookup tables, not scattered conditionals:

```typescript
// Illumination Quality Constants
const SHADOW_MAP_SIZE = {
  minimal: 0,       // Shadows disabled
  standard: 1024,
  high: 2048,
  cinematic: 4096,
} as const;

const AMBIENT_INTENSITY = {
  minimal: 0.6,     // Higher ambient compensates for no shadows
  standard: 0.35,
  high: 0.3,
  cinematic: 0.25,
} as const;

const SUN_INTENSITY = {
  minimal: 1.0,
  standard: 1.2,
  high: 1.3,
  cinematic: 1.4,
} as const;

const SHADOW_BIAS = {
  minimal: 0,
  standard: -0.0001,
  high: -0.00005,
  cinematic: -0.00001,
} as const;

type IlluminationQuality = 'minimal' | 'standard' | 'high' | 'cinematic';
```

---

## Shadow Optimization Best Practices

### 1. Selective Shadow Casting

**Only enable shadows on objects that benefit from them:**

```typescript
// Spheres (nodes): CAST shadows, DON'T receive
<mesh castShadow>
  <sphereGeometry />
  <meshStandardMaterial />
</mesh>

// Ground plane (if present): RECEIVE shadows, DON'T cast
<mesh receiveShadow>
  <planeGeometry />
  <meshStandardMaterial />
</mesh>

// Lines/Edges: NEVER cast or receive shadows
<Line points={points} />  // No shadow props
```

**Performance rule:** Graph edges and text labels should never cast shadows.

### 2. Tight Shadow Frustum

The shadow camera frustum should be as small as possible:

```typescript
// Calculate scene bounds dynamically
function calculateShadowBounds(nodes: TopologyNode[]) {
  if (nodes.length === 0) return DEFAULT_BOUNDS;

  let minX = Infinity, maxX = -Infinity;
  let minY = Infinity, maxY = -Infinity;
  let minZ = Infinity, maxZ = -Infinity;

  for (const node of nodes) {
    minX = Math.min(minX, node.x);
    maxX = Math.max(maxX, node.x);
    minY = Math.min(minY, node.y);
    maxY = Math.max(maxY, node.y);
    minZ = Math.min(minZ, node.z);
    maxZ = Math.max(maxZ, node.z);
  }

  const padding = 2; // Small buffer
  return {
    left: minX - padding,
    right: maxX + padding,
    top: maxY + padding,
    bottom: minY - padding,
    near: 0.5,
    far: Math.max(maxZ - minZ, 20) + padding * 2,
  };
}
```

### 3. Shadow Map Update Strategy

For static or slowly-changing graphs, shadows don't need per-frame updates:

```typescript
// Update shadow map only when topology changes
const shadowNeedsUpdate = useRef(true);

useEffect(() => {
  shadowNeedsUpdate.current = true;
}, [topology.nodes.length, topology.edges.length]);

useFrame(() => {
  if (directionalLightRef.current && shadowNeedsUpdate.current) {
    directionalLightRef.current.shadow.needsUpdate = true;
    shadowNeedsUpdate.current = false;
  }
});
```

---

## Semiotic Principles for 3D Visualization

### Depth Cues Hierarchy

The human visual system uses these depth cues, in order of perceptual strength:

| Cue | Description | Implementation |
|-----|-------------|----------------|
| **Occlusion** | Objects blocking others | Automatic (WebGL z-buffer) |
| **Shadows** | Cast shadows indicate depth | DirectionalLight + shadow map |
| **Size Gradient** | Distant objects appear smaller | Perspective camera (default) |
| **Aerial Perspective** | Distant objects are hazier | Fog (optional, for large scenes) |
| **Motion Parallax** | Closer objects move faster | OrbitControls (interactive) |
| **Shading** | Light/dark sides of objects | meshStandardMaterial |

**Shadows are the second-most-powerful depth cue after occlusion.** Without shadows, spheres appear to float ambiguously in space.

### The Shadow Stereopsis Effect

Research shows shadows provide stereoscopic depth information even in 2D displays:

> *"Objects might appear flat without shadow information but were perceived to be volumetric objects in the presence of cast shadows."*
> — Medina Puerta, "Shadow Stereopsis"

This is why adding a simple ground-contact shadow dramatically improves perceived depth.

### Pre-Attentive Processing

Shadows are processed **pre-attentively**—before conscious attention. This means:

1. Shadows should be **consistent** (same direction everywhere)
2. Shadows should be **subtle** (not overwhelming the data)
3. Shadow color should be **cool** (blue-ish gray, not black)

```typescript
// Soft, cool shadow color for readability
shadow-color="#1a1a2e"  // Dark blue-gray, not pure black
```

---

## The SceneLighting Component Pattern

Extract lighting into a reusable component that all 3D scenes use:

```typescript
// components/three/SceneLighting.tsx

interface SceneLightingProps {
  quality?: IlluminationQuality;
  /** Dynamic bounds from scene content */
  bounds?: ShadowBounds;
  /** Enable colored fill lights for atmosphere */
  atmosphericFill?: boolean;
  /** Custom sun position override */
  sunPosition?: [number, number, number];
}

export function SceneLighting({
  quality = 'standard',
  bounds = DEFAULT_BOUNDS,
  atmosphericFill = true,
  sunPosition = [15, 20, 15],
}: SceneLightingProps) {
  const shadowsEnabled = quality !== 'minimal';
  const shadowMapSize = SHADOW_MAP_SIZE[quality];

  return (
    <>
      {/* Ambient Fill */}
      <ambientLight intensity={AMBIENT_INTENSITY[quality]} />

      {/* Key Light (Sun) */}
      <directionalLight
        position={sunPosition}
        intensity={SUN_INTENSITY[quality]}
        castShadow={shadowsEnabled}
        shadow-mapSize-width={shadowMapSize}
        shadow-mapSize-height={shadowMapSize}
        shadow-camera-left={bounds.left}
        shadow-camera-right={bounds.right}
        shadow-camera-top={bounds.top}
        shadow-camera-bottom={bounds.bottom}
        shadow-camera-near={bounds.near}
        shadow-camera-far={bounds.far}
        shadow-bias={SHADOW_BIAS[quality]}
        shadow-normalBias={0.02}
      />

      {/* Fill Lights */}
      {atmosphericFill && (
        <>
          <pointLight
            position={[-10, -5, -10]}
            intensity={0.4}
            color="#6366f1"  // Cool indigo
          />
          <pointLight
            position={[0, -15, 0]}
            intensity={0.2}
            color="#22c55e"  // Ground bounce (subtle green)
          />
        </>
      )}
    </>
  );
}
```

---

## Integration with Projection Protocol

### WebGL Target Extension

The SceneLighting component implements the Projection Protocol's WebGL target with **illumination quality as a density-orthogonal dimension**:

```
Projection[WebGL] = (Density × IlluminationQuality) → 3D Scene
```

| Density | Illumination | Result |
|---------|--------------|--------|
| compact | minimal | Mobile 3D - no shadows, simpler geometry |
| compact | standard | Tablet 3D - soft shadows, full geometry |
| spacious | high | Desktop 3D - crisp shadows, full detail |
| spacious | cinematic | Presentation - maximum fidelity |

### Quality Detection

Illumination quality should be detected, not configured:

```typescript
function detectIlluminationQuality(): IlluminationQuality {
  // Check for low-power mode
  if (navigator.getBattery) {
    const battery = await navigator.getBattery();
    if (battery.charging === false && battery.level < 0.2) {
      return 'minimal';
    }
  }

  // Check WebGL capabilities
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

  if (!gl) return 'minimal';

  const maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
  const renderer = gl.getParameter(gl.RENDERER);

  // Heuristics for quality detection
  if (maxTextureSize >= 16384 && !renderer.includes('Intel')) {
    return 'high';
  }

  if (maxTextureSize >= 8192) {
    return 'standard';
  }

  return 'minimal';
}
```

---

## Geometry Defensive Patterns

### The Silent NaN Catastrophe

**Critical Learning**: Three.js geometry with NaN values renders as **invisible**—no error, no warning, just nothing.

When `sphereGeometry` or any geometry receives NaN for radius/dimensions, it:
1. Creates a geometry with NaN in the position buffer
2. Computes `boundingSphere.radius = NaN`
3. Renders **nothing** (silent failure)

The only hint is a console warning:
```
THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN.
The "position" attribute is likely to have NaN values.
```

**Root cause**: API data with undefined/null values passed to size calculations.

```typescript
// WRONG: Trusts API data blindly
function calculateSize(accessCount: number, resolution: number): number {
  return 0.5 * Math.log10(accessCount + 1) * resolution;
  // If accessCount is undefined: Math.log10(undefined + 1) = NaN
  // If resolution is undefined: 0.5 * X * undefined = NaN
}

// RIGHT: Defensive validation
function calculateSize(accessCount: number, resolution: number): number {
  const safeCount = typeof accessCount === 'number' && !isNaN(accessCount) ? accessCount : 1;
  const safeRes = typeof resolution === 'number' && !isNaN(resolution) ? resolution : 0.5;
  return 0.5 * Math.log10(safeCount + 1) * safeRes;
}
```

### The Defensive Geometry Pattern

Always validate numeric inputs before passing to Three.js geometry:

```typescript
// Defensive wrapper for geometry props
function safeNumber(value: number, fallback: number): number {
  return typeof value === 'number' && !isNaN(value) && isFinite(value)
    ? value
    : fallback;
}

// Usage in component
const size = useMemo(() => {
  const rawSize = calculateSize(node.access_count, node.resolution);
  return safeNumber(rawSize, 0.5); // Fallback to 0.5 if NaN
}, [node.access_count, node.resolution]);

// Now safe to use
<sphereGeometry args={[size, 32, 32]} />
```

### Debug Pattern for Invisible Geometry

When 3D objects don't render, add debug logging:

```typescript
// DEBUG: Log raw values to catch undefined/NaN
console.log(`[Component] ${id}: pos=(${x}, ${y}, ${z}), size=${size}`);
// Look for: "pos=(undefined, NaN, 5.2)" or "size=NaN"
```

**Remember**: The browser console warning about NaN boundingSphere is your friend—always check for it when debugging invisible geometry.

---

## Anti-Patterns

### 1. Per-Component Lighting

**Wrong:**
```typescript
// BrainTopology.tsx
<ambientLight intensity={0.4} />
<pointLight position={[10, 10, 10]} intensity={1} />

// Gestalt.tsx
<ambientLight intensity={0.5} />  // Different!
<pointLight position={[15, 15, 15]} intensity={1.2} />  // Different!
```

**Right:**
```typescript
// Both use the same SceneLighting
<SceneLighting quality={illuminationQuality} bounds={sceneBounds} />
```

### 2. All Objects Cast Shadows

**Wrong:**
```typescript
{nodes.map(node => (
  <mesh castShadow receiveShadow>...</mesh>
))}
{edges.map(edge => (
  <Line castShadow>...</Line>  // Lines don't cast useful shadows
))}
```

**Right:**
```typescript
{nodes.map(node => (
  <mesh castShadow>...</mesh>  // Nodes cast shadows
))}
{edges.map(edge => (
  <Line>...</Line>  // No shadow props on edges
))}
```

### 3. Hardcoded Shadow Quality

**Wrong:**
```typescript
shadow-mapSize-width={2048}  // Always 2048
```

**Right:**
```typescript
shadow-mapSize-width={SHADOW_MAP_SIZE[quality]}  // Quality-parameterized
```

---

## Performance Metrics

Target frame rates by quality level:

| Quality | Target FPS | Max Nodes | Shadow Updates |
|---------|-----------|-----------|----------------|
| minimal | 60 | 500+ | None |
| standard | 60 | 300 | On change |
| high | 60 | 200 | On change |
| cinematic | 30 | 150 | Continuous |

Monitor with:

```typescript
import { useFrame } from '@react-three/fiber';
import Stats from 'three/examples/jsm/libs/stats.module';

function PerformanceMonitor() {
  const stats = useMemo(() => new Stats(), []);

  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      document.body.appendChild(stats.dom);
      return () => document.body.removeChild(stats.dom);
    }
  }, [stats]);

  useFrame(() => stats.update());
  return null;
}
```

---

## Connection to kgents Principles

| Principle | Manifestation |
|-----------|---------------|
| **Tasteful** | One canonical lighting rig, not arbitrary per-scene choices |
| **Joy-Inducing** | Shadows add depth, making visualizations feel alive |
| **Composable** | SceneLighting component composes with any scene content |
| **Generative** | Quality levels are generated from device capability |
| **Observer-Dependent** | Illumination quality is observer's device capability |

---

## Sources

- [Three.js Shadow Optimization (Three.js Forum)](https://discourse.threejs.org/t/how-to-optimize-shadow-rendering-in-three-js-for-better-performance/64681)
- [Three.js Performance Guide (GitHub Gist)](https://gist.github.com/iErcann/2a9dfa51ed9fc44854375796c8c24d92)
- [Directional Light Shadow Tutorial (sbcode.net)](https://sbcode.net/threejs/directional-light-shadow/)
- [Depth Cues in Human Visual Perception (ResearchGate)](https://www.researchgate.net/publication/215478670_Depth_cues_in_human_visual_perception_and_their_realization_in_3D_displays)
- [Perception, Cognition and Reasoning about Shadows (Taylor & Francis)](https://www.tandfonline.com/doi/full/10.1080/13875868.2017.1377204)
- [GPU Work Graphs for Procedural Generation (ACM)](https://dl.acm.org/doi/10.1145/3675376)

---

*"The difference between a good visualization and a great one is often just the shadows."*
