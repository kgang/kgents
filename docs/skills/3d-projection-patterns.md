# 3D Projection Patterns

> *"The same categorical structure underlies everything. Three.js scenes are no exception."*

This skill covers 3D visualization patterns using the unified primitive system.

---

## The Core Abstraction

```
P[3D] : State x Theme x Quality -> Three.js Scene
```

All 3D visualizations in kgents follow this functor pattern:
- **State**: Domain data (nodes, edges, metrics)
- **Theme**: Visual identity (crystal, forest)
- **Quality**: Device capability (minimal -> cinematic)

The result is a composed Three.js scene with consistent behavior.

---

## When to Use What

| Scenario | Use This | Why |
|----------|----------|-----|
| Building new 3D visualization | `TopologyNode3D`, `TopologyEdge3D` | Full control, theme-agnostic |
| Memory/Brain features | `OrganicCrystal`, `CrystalVine` | Pre-configured with crystal theme |
| Codebase/Gestalt features | `OrganicNode`, `VineEdge` | Pre-configured with forest theme |
| Custom domain visualization | Create thin wrapper | Encapsulates tier/size logic |

**Rule**: Domain wrappers are thin. All logic lives in primitives.

---

## Using Primitives Directly

### TopologyNode3D

```tsx
import { TopologyNode3D, CRYSTAL_THEME } from '@/components/three/primitives';

function MyNode({ data, isSelected, density }: Props) {
  // Domain-specific tier calculation
  const getTier = (d: MyData) => {
    if (d.importance > 0.9) return 'hot';
    if (d.importance > 0.7) return 'vivid';
    return 'familiar';
  };

  // Domain-specific size calculation
  const getSize = (d: MyData, density: Density) => {
    const baseSize = { compact: 0.2, comfortable: 0.3, spacious: 0.4 }[density];
    return baseSize * (1 + d.importance * 0.5);
  };

  return (
    <TopologyNode3D
      position={[data.x, data.y, data.z]}
      theme={CRYSTAL_THEME}
      data={data}
      getTier={getTier}
      getSize={getSize}
      isSelected={isSelected}
      density={density}
      onClick={() => selectNode(data.id)}
    />
  );
}
```

### TopologyEdge3D

```tsx
import { TopologyEdge3D, FOREST_THEME } from '@/components/three/primitives';

function MyEdge({ source, target, strength, isActive }: Props) {
  return (
    <TopologyEdge3D
      source={source.position}
      target={target.position}
      theme={FOREST_THEME}
      strength={strength}
      isActive={isActive}
      showFlowParticles={isActive}
      curveIntensity={0.3}
    />
  );
}
```

### SmartTopologyEdge3D

For edges that need to look up node positions:

```tsx
import { SmartTopologyEdge3D, CRYSTAL_THEME } from '@/components/three/primitives';

function MySmartEdge({ edge, nodePositions }: Props) {
  return (
    <SmartTopologyEdge3D
      sourceId={edge.source}
      targetId={edge.target}
      nodePositions={nodePositions}  // Map<string, [x,y,z]>
      theme={CRYSTAL_THEME}
      strength={edge.weight}
    />
  );
}
```

---

## Creating Domain Wrappers

Domain wrappers should be thin and only contain:
1. Domain-specific tier calculation
2. Domain-specific size calculation
3. Theme selection

### Pattern

```tsx
// components/mydomain/MyDomainNode.tsx

import { TopologyNode3D, MY_THEME } from '@/components/three/primitives';
import type { MyDomainData } from './types';

// Domain-specific tier calculation
function getMyDomainTier(data: MyDomainData): string {
  if (data.score >= 0.9) return 'excellent';
  if (data.score >= 0.7) return 'good';
  if (data.score >= 0.5) return 'moderate';
  return 'needs_attention';
}

// Domain-specific size calculation
function getMyDomainSize(data: MyDomainData, density: Density): number {
  const bases = { compact: 0.2, comfortable: 0.3, spacious: 0.4 };
  return bases[density] * Math.sqrt(data.weight);
}

// Thin wrapper - just wires up domain logic
export function MyDomainNode(props: MyDomainNodeProps) {
  return (
    <TopologyNode3D
      {...props}
      theme={MY_THEME}
      getTier={getMyDomainTier}
      getSize={getMyDomainSize}
    />
  );
}
```

---

## Creating Custom Themes

### Theme Interface

```typescript
import type { ThemePalette } from '@/components/three/primitives/themes';

export const MY_THEME: ThemePalette = {
  name: 'my-theme',
  description: 'Theme for my domain',

  // Node colors by tier (domain-specific tier names)
  nodeTiers: {
    excellent: { core: '#22C55E', glow: '#4ADE80', ring: '#166534' },
    good: { core: '#3B82F6', glow: '#60A5FA', ring: '#1E40AF' },
    moderate: { core: '#F59E0B', glow: '#FBBF24', ring: '#B45309' },
    needs_attention: { core: '#EF4444', glow: '#F87171', ring: '#B91C1C' },
  },

  // Edge colors
  edgeColors: {
    base: '#6B7280',
    highlight: '#3B82F6',
    glow: '#60A5FA',
    violation: '#EF4444',
  },

  // Particle colors for flow animations
  particleColors: {
    normal: '#3B82F6',
    active: '#60A5FA',
  },

  // Selection/hover indicators
  selectionColor: '#FBBF24',
  hoverColor: '#FCD34D',

  // Labels
  labelColor: '#F9FAFB',
  labelOutlineColor: '#1F2937',

  // Optional atmosphere
  atmosphere: {
    fog: { color: '#0F172A', near: 10, far: 50 },
    background: '#0F172A',
    ambientTint: '#1E3A5F',
  },
};
```

### Validation

```typescript
import { validateThemeTiers } from '@/components/three/primitives/themes';

// Ensure theme has all tiers your domain uses
const missing = validateThemeTiers(MY_THEME, ['excellent', 'good', 'moderate', 'needs_attention']);
if (missing.length > 0) {
  console.warn(`Theme missing tiers: ${missing.join(', ')}`);
}
```

---

## Quality Adaptation

### Using Quality Hook

```tsx
import { useIlluminationQuality } from '@/hooks/useIlluminationQuality';
import { ANIMATION_PRESETS, PERFORMANCE_TIERS } from '@/components/three/primitives';

function My3DScene() {
  const { quality, setQuality } = useIlluminationQuality();
  const perfTier = PERFORMANCE_TIERS[quality];

  return (
    <Canvas>
      {/* Scene lighting adapts to quality */}
      <SceneLighting quality={quality} />

      {/* Effects adapt to quality */}
      <SceneEffects quality={quality} />

      {/* Conditionally render expensive features */}
      {perfTier.particleCount > 0 && (
        <FlowParticles count={perfTier.particleCount} />
      )}

      {/* LOD-aware rendering */}
      <MyNodes lodBias={perfTier.lodBias} />
    </Canvas>
  );
}
```

### Quality Levels

| Level | Shadows | SSAO | Bloom | Particles | Use Case |
|-------|---------|------|-------|-----------|----------|
| `minimal` | No | No | No | 0 | Low-end devices, battery saving |
| `standard` | Yes | No | Yes | 4 | Default, good balance |
| `high` | Yes | Yes | Yes | 6 | Desktop with GPU |
| `cinematic` | Yes | Yes | Yes | 8 | Demos, screenshots |

---

## Performance Patterns

### LOD for Large Graphs (100+ nodes)

Use the built-in `useLOD` hook for automatic level-of-detail management:

```tsx
import { useLOD, LODAwareNode, getEdgeLOD } from '@/components/three/primitives';

function LargeGraph({ nodes, edges }: Props) {
  // useLOD handles frustum culling and distance-based detail reduction
  const { getLOD, getLODBatch, getStats } = useLOD(nodes.length);

  // Calculate LOD for all nodes in batch
  const nodeLODs = getLODBatch(nodes.map(n => [n.x, n.y, n.z]));

  // Debug stats
  const stats = getStats(nodeLODs);
  console.log(`Visible: ${stats.full + stats.reduced + stats.minimal}, Culled: ${stats.culled}`);

  return (
    <>
      {nodes.map((node, i) => {
        const lod = nodeLODs[i];
        if (lod.level === 'culled') return null;

        return (
          <LODAwareNode key={node.id} position={[node.x, node.y, node.z]} lod={lod}>
            {({ segments, showLabel, animationSpeed }) => (
              <TopologyNode3D
                {...node}
                segments={segments}           // Auto-reduced at distance
                showLabel={showLabel}         // Hidden at distance
                animationSpeed={animationSpeed} // Disabled at distance
              />
            )}
          </LODAwareNode>
        );
      })}

      {edges.map((edge, i) => {
        const sourceLOD = nodeLODs[nodes.findIndex(n => n.id === edge.sourceId)];
        const targetLOD = nodeLODs[nodes.findIndex(n => n.id === edge.targetId)];
        const edgeLOD = getEdgeLOD(sourceLOD, targetLOD);

        if (!edgeLOD.visible) return null;

        return (
          <TopologyEdge3D
            key={edge.id}
            {...edge}
            curveSegments={edgeLOD.curveSegments}
            showFlowParticles={edgeLOD.showFlowParticles}
          />
        );
      })}
    </>
  );
}
```

#### LOD Settings

```tsx
// Custom LOD settings for dense graphs
const { getLOD } = useLOD(nodes.length, {
  settings: {
    distances: {
      full: 3,      // Closer = full detail
      reduced: 10,
      minimal: 25,
    },
    budgetThresholds: {
      medium: 30,   // Earlier transition to aggressive LOD
      large: 75,
    },
  },
  updateInterval: 50, // More frequent updates for dynamic scenes
});
```

### Touch Responsiveness (Mobile)

Use the touch hooks for mobile accessibility (WCAG 2.1 compliant):

```tsx
import { useTouchDevice, TopologyNode3D } from '@/components/three/primitives';

function My3DScene({ nodes }: Props) {
  const { isTouchDevice, isHybrid } = useTouchDevice();

  return (
    <>
      {nodes.map(n => (
        <TopologyNode3D
          key={n.id}
          {...n}
          isTouchDevice={isTouchDevice}       // Enables larger hit area
          touchTargetMultiplier={1.5}         // 1.5x node size for touch
        />
      ))}
    </>
  );
}
```

For custom gesture handling:

```tsx
import { useGesture } from '@/components/three/primitives';

function TouchableNode({ onSelect, onDetails }: Props) {
  const { onPointerDown, onPointerMove, onPointerUp } = useGesture({
    onTap: onSelect,        // Quick touch
    onLongPress: onDetails, // Press and hold
    onDrag: (dx, dy) => console.log('Dragging', dx, dy),
  });

  return (
    <mesh
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={onPointerUp}
    >
      ...
    </mesh>
  );
}
```

### Animation Throttling

```tsx
import { ANIMATION_PRESETS } from '@/components/three/primitives';

function OptimizedNode({ quality, ...props }: Props) {
  // Reduce animation speed on low quality
  const animationSpeed = quality === 'minimal'
    ? 0  // Disable animation
    : ANIMATION_PRESETS.breathing.speed;

  return (
    <TopologyNode3D
      {...props}
      animationSpeed={animationSpeed}
    />
  );
}
```

---

## AGENTESE Integration

### Available Paths

```python
# Node primitive configuration
await logos.invoke("concept.projection.three.node.manifest", umwelt)
await logos.invoke("concept.projection.three.node.config", umwelt)

# Edge primitive configuration
await logos.invoke("concept.projection.three.edge.manifest", umwelt)
await logos.invoke("concept.projection.three.edge.config", umwelt)

# Theme operations
await logos.invoke("concept.projection.three.theme.list", umwelt)
await logos.invoke("concept.projection.three.theme.get", umwelt, name="crystal")
await logos.invoke("concept.projection.three.theme.palette", umwelt, name="forest")

# Quality adaptation
await logos.invoke("concept.projection.three.quality.adapt", umwelt, level="high")
await logos.invoke("concept.projection.three.quality.config", umwelt)
```

### Python Usage

```python
from protocols.agentese.contexts.three import (
    THEME_REGISTRY,
    QUALITY_CONFIGS,
    Quality,
    create_three_resolver,
)

# Get theme info
crystal = THEME_REGISTRY["crystal"]
print(f"Crystal tiers: {crystal['nodeTiers']}")

# Get quality config
high_config = QUALITY_CONFIGS[Quality.HIGH]
print(f"High quality: {high_config['description']}")
```

---

## File Locations

| Component | Location |
|-----------|----------|
| **Primitives** | `web/src/components/three/primitives/` |
| **Themes** | `web/src/components/three/primitives/themes/` |
| **Theme Harmony** | `web/src/components/three/primitives/themes/harmony.ts` |
| **Animation** | `web/src/components/three/primitives/animation.ts` |
| **LOD System** | `web/src/components/three/primitives/useLOD.tsx` |
| **Touch Hooks** | `web/src/components/three/primitives/useTouch.ts` |
| **Brain wrappers** | `web/src/components/brain/` |
| **Gestalt wrappers** | `web/src/components/gestalt/` |
| **Quality hook** | `web/src/hooks/useIlluminationQuality.ts` |
| **Lighting constants** | `web/src/constants/lighting.ts` |
| **AGENTESE context** | `protocols/agentese/contexts/three.py` |

---

## Common Mistakes

### 1. Duplicating Logic in Wrappers

**Bad:**
```tsx
// Reimplementing breathing animation in wrapper
function OrganicCrystal(props) {
  const [scale, setScale] = useState(1);
  useFrame((_, delta) => {
    setScale(1 + Math.sin(Date.now() * 0.001) * 0.03);
  });
  return <mesh scale={scale}>...</mesh>;
}
```

**Good:**
```tsx
// Let primitive handle animation
function OrganicCrystal(props) {
  return <TopologyNode3D {...props} theme={CRYSTAL_THEME} />;
}
```

### 2. Mixing Themes in Same Scene

If you need cross-jewel scenes, check theme harmony first:

```tsx
import { checkThemeHarmony, CRYSTAL_THEME, FOREST_THEME } from '@/components/three/primitives';

// Check compatibility
const harmony = checkThemeHarmony(CRYSTAL_THEME, FOREST_THEME);
if (!harmony.harmonious) {
  console.warn('Theme issues:', harmony.issues);
  console.log('Recommendations:', harmony.recommendations);
}

// Use blend color for transition zones
const blendBg = getThemeBlendColor(CRYSTAL_THEME, FOREST_THEME);
```

For single-theme scenes (preferred):

```tsx
// One theme per scene
const theme = domain === 'brain' ? CRYSTAL_THEME : FOREST_THEME;
<>
  {nodes.map(n => <TopologyNode3D key={n.id} theme={theme} {...n} />)}
</>
```

### 3. Ignoring Quality Adaptation

**Bad:**
```tsx
// Always rendering at max quality
<SceneEffects bloom ssao />
```

**Good:**
```tsx
// Adapt to device capability
<SceneEffects quality={quality} />
```

---

## Related Skills

- `elastic-ui-patterns.md` — Density-responsive 2D layout
- `projection-target.md` — Multi-target projection (CLI/TUI/JSON)
- `metaphysical-fullstack.md` — Full stack pattern (7 layers)

---

*Last updated: 2025-12-18*
