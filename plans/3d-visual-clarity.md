# Plan: 3D Visual Clarity System

> *"Let there be light—and let it be principled."*

## Summary

Implement a canonical lighting and shadow system for all kgents 3D visualizations. This system treats **illumination quality** as a projection dimension parallel to density, enabling automatic device-appropriate rendering while ensuring visual consistency across all 3D crown jewels.

---

## The Problem

Current 3D visualizations (BrainTopology, Gestalt) use:
- **Inconsistent lighting**: Each component defines its own light positions/intensities
- **No shadows**: Spheres appear to float ambiguously in space
- **No depth cues**: Users struggle to perceive 3D relationships
- **No quality adaptation**: Same rendering on high-end desktop and low-end mobile

This violates:
- **Principle 1 (Tasteful)**: Arbitrary per-component lighting choices
- **Principle 4 (Joy-Inducing)**: Flat visualizations lack life
- **AD-008 (Simplifying Isomorphisms)**: Scattered quality conditionals

---

## The Solution

### Core Insight

**Illumination quality is a simplifying isomorphism.**

Just as `density` unifies `isMobile/isTablet/isDesktop` for layout, `illuminationQuality` unifies device capability checks for 3D rendering:

```
Device Capability ≅ Illumination Quality ≅ Shadow Fidelity ≅ Rendering Budget
```

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PROJECTION LAYER                                 │
│                                                                          │
│   ┌──────────────────┐      ┌──────────────────┐                        │
│   │   Density        │      │ Illumination     │                        │
│   │   (2D Layout)    │      │ Quality (3D)     │                        │
│   └────────┬─────────┘      └────────┬─────────┘                        │
│            │                         │                                   │
│            └─────────────┬───────────┘                                   │
│                          │                                               │
│                          ▼                                               │
│            ┌─────────────────────────┐                                   │
│            │   useSceneContext()     │                                   │
│            │   { density, quality }  │                                   │
│            └─────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPONENT LAYER                                  │
│                                                                          │
│   ┌─────────────────────────────────────────────────────────┐           │
│   │              SceneLighting                               │           │
│   │                                                          │           │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │           │
│   │   │ Ambient     │  │ Sun (Key)   │  │ Fill Lights │    │           │
│   │   │ Light       │  │ DirectionalL│  │ PointLights │    │           │
│   │   └─────────────┘  └─────────────┘  └─────────────┘    │           │
│   │                                                          │           │
│   │   All parameters from QUALITY_CONSTANTS[quality]         │           │
│   └─────────────────────────────────────────────────────────┘           │
│                                                                          │
│   Used by: BrainTopology | Gestalt | Future 3D Jewels                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Waves

### Wave 0: Foundation Infrastructure

**Goal**: Create the quality detection and context system.

**Deliverables**:

1. **`hooks/useIlluminationQuality.ts`**
   - Detect device WebGL capabilities
   - Check battery status (low power → minimal quality)
   - Return `IlluminationQuality` type
   - Memoize detection (run once per session)

2. **`hooks/useSceneContext.ts`**
   - Combine `useWindowLayout()` (density) with `useIlluminationQuality()`
   - Provide unified context for 3D scenes
   - Type: `{ density, illuminationQuality, shadowsEnabled }`

3. **`constants/lighting.ts`**
   - Quality-parameterized constants as lookup tables
   - `SHADOW_MAP_SIZE`, `AMBIENT_INTENSITY`, `SUN_INTENSITY`, etc.
   - No magic numbers anywhere in components

**Tests**:
- Unit test quality detection with mock WebGL contexts
- Test battery API fallback behavior

---

### Wave 1: SceneLighting Component

**Goal**: Create the canonical lighting rig as a reusable component.

**Deliverables**:

1. **`components/three/SceneLighting.tsx`**
   ```typescript
   interface SceneLightingProps {
     quality?: IlluminationQuality;
     bounds?: ShadowBounds;
     atmosphericFill?: boolean;
     sunPosition?: [number, number, number];
   }
   ```
   - Implements the three-light minimum (ambient + key + fill)
   - All parameters from quality constants
   - Dynamic shadow frustum from bounds prop

2. **`components/three/ShadowPlane.tsx`** (optional)
   - Invisible ground plane that receives shadows
   - For graph visualizations without explicit ground

3. **`utils/three/calculateShadowBounds.ts`**
   - Calculate tight shadow frustum from node positions
   - Returns `ShadowBounds` type

**Tests**:
- Render test with different quality levels
- Verify shadow map sizes match constants
- Performance test: measure FPS at each quality

---

### Wave 2: Migrate BrainTopology

**Goal**: Replace BrainTopology's ad-hoc lighting with SceneLighting.

**Changes**:

```diff
// BrainTopology.tsx Scene component

- <ambientLight intensity={0.4} />
- <pointLight position={[10, 10, 10]} intensity={1} />
- <pointLight position={[-10, -10, -10]} intensity={0.5} color="#4a90d9" />
+ <SceneLighting
+   quality={illuminationQuality}
+   bounds={calculateShadowBounds(topology.nodes)}
+   atmosphericFill
+ />

// Add castShadow to CrystalNode mesh
- <mesh ref={meshRef} ...>
+ <mesh ref={meshRef} castShadow ...>
```

**Additional work**:
- Update Canvas to enable shadows: `shadows={{ type: 'soft' }}`
- Add shadow-receiving floor (optional, for enhanced depth)

**Tests**:
- Visual regression test
- Performance comparison (before/after shadows)
- Mobile/desktop quality detection verification

---

### Wave 3: Migrate Gestalt

**Goal**: Replace Gestalt's ad-hoc lighting with SceneLighting.

**Changes**:

```diff
// Gestalt.tsx Scene component

- <ambientLight intensity={0.5} />
- <pointLight position={[15, 15, 15]} intensity={1.2} />
- <pointLight position={[-15, -10, -15]} intensity={0.6} color="#6366f1" />
- <pointLight position={[0, -20, 0]} intensity={0.3} color="#22c55e" />
+ <SceneLighting
+   quality={illuminationQuality}
+   bounds={calculateShadowBounds(filteredNodes)}
+   atmosphericFill
+ />

// Add castShadow to ModuleNode mesh
- <mesh ref={meshRef} ...>
+ <mesh ref={meshRef} castShadow ...>
```

**Tests**:
- Visual regression test
- Verify layer rings don't cast shadows (they shouldn't)
- Performance test with full topology

---

### Wave 4: Polish and Documentation

**Goal**: Ensure joy-inducing quality and complete documentation.

**Deliverables**:

1. **Shadow color tuning**
   - Soft blue-gray shadows, not harsh black
   - `shadow-color="#1a1a2e"`

2. **Ambient occlusion consideration** (optional enhancement)
   - Screen-space ambient occlusion (SSAO) for `high`/`cinematic`
   - Only if performance allows

3. **Documentation updates**
   - Update `docs/skills/3d-lighting-patterns.md` with learnings
   - Add screenshots showing before/after
   - Performance benchmarks

4. **Gallery integration** (if Projection Gallery supports 3D)
   - Add 3D widget pilots with different quality levels

---

## Quality Constants Reference

```typescript
// constants/lighting.ts

export type IlluminationQuality = 'minimal' | 'standard' | 'high' | 'cinematic';

export const SHADOW_MAP_SIZE: Record<IlluminationQuality, number> = {
  minimal: 0,       // Shadows disabled
  standard: 1024,
  high: 2048,
  cinematic: 4096,
};

export const AMBIENT_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0.6,     // Higher ambient compensates for no shadows
  standard: 0.35,
  high: 0.3,
  cinematic: 0.25,
};

export const SUN_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 1.0,
  standard: 1.2,
  high: 1.3,
  cinematic: 1.4,
};

export const SHADOW_BIAS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: -0.0001,
  high: -0.00005,
  cinematic: -0.00001,
};

export const CANONICAL_SUN_POSITION: [number, number, number] = [15, 20, 15];

export const DEFAULT_SHADOW_BOUNDS: ShadowBounds = {
  left: -15,
  right: 15,
  top: 15,
  bottom: -15,
  near: 0.5,
  far: 50,
};
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| **Performance regression** | Quality detection ensures low-end devices get `minimal` |
| **Visual inconsistency** | Single SceneLighting component enforces consistency |
| **Shadow artifacts (peter-panning, acne)** | Pre-tuned bias values in constants |
| **Mobile battery drain** | Battery API detection → `minimal` quality |
| **Breaking existing appearance** | Wave 2-3 are opt-in; test thoroughly |

---

## Success Criteria

1. **Visual**: Users can clearly perceive depth relationships between nodes
2. **Performance**: 60 FPS maintained on target devices per quality level
3. **Consistency**: All 3D scenes use identical lighting rig
4. **Adaptability**: Quality auto-detects based on device capability
5. **Maintainability**: New 3D scenes get lighting for free via SceneLighting

---

## Estimated Effort

| Wave | Effort | Dependencies |
|------|--------|--------------|
| Wave 0 | 2h | None |
| Wave 1 | 2h | Wave 0 |
| Wave 2 | 1h | Wave 1 |
| Wave 3 | 1h | Wave 1 |
| Wave 4 | 2h | Wave 2, 3 |

**Total**: ~8 hours of focused work

---

## Connection to Crown Jewels

This plan supports the Enlightened Crown strategy:

- **Brain (Holographic)**: BrainTopology gets depth-rich crystal visualization
- **Gestalt (Visualizer)**: Architecture graphs become spatially comprehensible
- **Future Jewels**: Any 3D visualization inherits the lighting rig

The "wow moment" for 3D visualizations requires depth perception. Without shadows, spheres are circles.

---

*"The sun that lights one jewel lights them all."*
