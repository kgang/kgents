# Continuation: Wave 5 - Bloom for Emissive Elements ✅ COMPLETE

> *"Light doesn't just illuminate—it bleeds, glows, and breathes."*

**Status**: COMPLETE (2025-12-16)

## Summary

Wave 5 implemented bloom post-processing for emissive elements:

1. **constants/lighting.ts**: Added `BLOOM_ENABLED`, `BLOOM_INTENSITY`, `BLOOM_THRESHOLD`, `BLOOM_SMOOTHING` constants
2. **SceneEffects.tsx**: Extended with Bloom effect alongside SSAO, both quality-gated
3. **BrainTopology.tsx**: Increased emissive intensities (1.2-2.0) for hot/hub/selected nodes
4. **Gestalt.tsx**: Increased emissive intensities (0.6-2.0) for selected/hovered modules
5. **QualitySelector.tsx**: Added "Bloom" indicator badge for high/cinematic quality

All changes are quality-gated—bloom only activates on `high` and `cinematic` quality levels.

---

## Context

**Previous Session Completed Wave 4:**
- `src/components/three/SceneEffects.tsx` - Post-processing with SSAO
- `src/components/three/QualitySelector.tsx` - Quality override UI
- SSAO integration in BrainTopology and Gestalt
- Quality-gated effects (high/cinematic only)

**The depth is there.** SSAO adds subtle contact shadows. But emissive elements (selected nodes, hot crystals, hub rings) still feel flat. They emit light but the light doesn't *bloom*.

---

## The Mission: Bloom for Emissive Elements

**Bloom** creates the cinematic glow around bright objects—the soft halo that makes lights feel real. In photography, this happens naturally when bright areas bleed into surrounding pixels. In 3D, we simulate it.

### Why Bloom Matters for Crown Jewels

1. **BrainTopology**: Hot crystals should *glow* with warmth. Hub rings should pulse with visible light halos
2. **Gestalt**: Selected modules should stand out with radiant emphasis
3. **Emotional Impact**: Bloom is the difference between "that's bright" and "that's *luminous*"

### Quality-Gated Implementation

Bloom is moderately expensive. Enable appropriately:

```typescript
// In constants/lighting.ts, add:
export const BLOOM_ENABLED: Record<IlluminationQuality, boolean> = {
  minimal: false,
  standard: false,
  high: true,       // Subtle bloom
  cinematic: true,  // Full bloom
};

export const BLOOM_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.3,        // Subtle glow
  cinematic: 0.5,   // Pronounced glow
};

export const BLOOM_THRESHOLD: Record<IlluminationQuality, number> = {
  minimal: 1,
  standard: 1,
  high: 0.8,        // Only very bright areas bloom
  cinematic: 0.6,   // More generous bloom
};

export const BLOOM_SMOOTHING: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.3,
  cinematic: 0.5,
};
```

---

## Technical Approach

### Extend SceneEffects.tsx

```tsx
import { EffectComposer, SSAO, Bloom } from '@react-three/postprocessing';
import { BlendFunction, KernelSize } from 'postprocessing';

function SceneEffects({ quality, disabled }: SceneEffectsProps) {
  const ssaoConfig = useMemo(() => /* existing */, [quality]);
  const bloomConfig = useMemo(() => ({
    enabled: BLOOM_ENABLED[quality],
    intensity: BLOOM_INTENSITY[quality],
    threshold: BLOOM_THRESHOLD[quality],
    smoothing: BLOOM_SMOOTHING[quality],
  }), [quality]);

  if (disabled || (!ssaoConfig.enabled && !bloomConfig.enabled)) {
    return null;
  }

  return (
    <EffectComposer>
      {ssaoConfig.enabled && <SSAO {...ssaoProps} />}
      {bloomConfig.enabled && (
        <Bloom
          blendFunction={BlendFunction.ADD}
          intensity={bloomConfig.intensity}
          luminanceThreshold={bloomConfig.threshold}
          luminanceSmoothing={bloomConfig.smoothing}
          kernelSize={KernelSize.MEDIUM}
          mipmapBlur
        />
      )}
    </EffectComposer>
  );
}
```

### Enhance Emissive Materials

For bloom to work well, emissive materials need appropriate intensity:

```tsx
// In BrainTopology CrystalNode
<meshStandardMaterial
  color={color}
  emissive={isHub || isSelected ? color : undefined}
  emissiveIntensity={isHub ? 1.5 : isSelected ? 2.0 : 0}  // Increased for bloom
/>

// Hub ring glow
<meshBasicMaterial
  color="#ffa500"
  transparent
  opacity={0.6}  // Increased from 0.3
/>
```

---

## Deliverables

### 1. Update constants/lighting.ts
Add bloom-related quality constants.

### 2. Extend SceneEffects.tsx
Add Bloom effect alongside SSAO, both quality-gated.

### 3. Tune Emissive Intensities
Ensure emissive materials are bright enough to trigger bloom:
- BrainTopology: Hub rings, hot crystals, selection rings
- Gestalt: Selected module glow, violation edges (optional red glow)

### 4. Update QualitySelector
Show bloom indicator alongside SSAO:
```tsx
{ssaoEnabled(currentQuality) && <span>SSAO</span>}
{bloomEnabled(currentQuality) && <span>Bloom</span>}
```

---

## Success Criteria

1. **Visual**: Hot crystals and selected nodes emit visible glow halos
2. **Performance**: 60 FPS maintained at `high` quality on M1 MacBook
3. **Subtlety**: Bloom enhances without overwhelming—it should feel natural
4. **Joy Factor**: The visualization should feel "alive" and "luminous"

---

## Testing Checklist

- [x] Bloom visible on `high` and `cinematic` quality
- [x] Bloom disabled on `standard` and `minimal`
- [x] Hot crystals in BrainTopology show warm glow (emissiveIntensity: 1.2)
- [x] Selected nodes have visible light halo (emissiveIntensity: 2.0)
- [x] Hub rings pulse with soft bloom (opacity: 0.6)
- [ ] No blown-out areas or excessive glow (manual verification needed)
- [ ] Performance acceptable (manual verification needed)

---

## Reference Files

| File | Purpose |
|------|---------|
| `src/constants/lighting.ts` | Add bloom constants |
| `src/components/three/SceneEffects.tsx` | Add Bloom effect |
| `src/components/three/QualitySelector.tsx` | Add bloom indicator |
| `src/components/BrainTopology.tsx` | Tune emissive intensities |
| `src/pages/Gestalt.tsx` | Tune emissive intensities |

---

## Notes on Tuning

Bloom parameters are subjective and scene-dependent:

- `intensity`: Overall glow strength (0.1-1.0 typical)
- `luminanceThreshold`: How bright before bloom kicks in (0.5-0.9)
- `luminanceSmoothing`: Falloff around threshold (0.1-0.5)
- `kernelSize`: Blur radius (SMALL, MEDIUM, LARGE, HUGE)
- `mipmapBlur`: Enable for smoother, more natural bloom

Start subtle. Bloom should feel like *natural light behavior*, not a filter effect.

---

## Optional Enhancements

### Selective Bloom (Advanced)
Use layers to bloom only specific objects:
```tsx
// Objects that should bloom go on layer 1
mesh.layers.enable(1);

// SelectiveBloom only affects layer 1
<SelectiveBloom selection={[...bloomObjects]} />
```

### Animated Bloom
Pulse bloom intensity for "breathing" effect:
```tsx
useFrame(({ clock }) => {
  bloomRef.current.intensity = 0.4 + Math.sin(clock.elapsedTime) * 0.1;
});
```

---

*"The best glow is the one that makes you lean in closer—not squint away."*

---

## Quick Start

```bash
cd impl/claude/web
npm run dev
# Visit http://localhost:3000
# Navigate to Brain page
# Set quality to "cinematic"
# Click on crystals and observe the glow
```

---

## Next Session: Wave 6 (Optional Enhancements)

If bloom feels too subtle or too strong, consider:

### Fine-Tuning Bloom Parameters

```typescript
// In constants/lighting.ts, adjust:
BLOOM_INTENSITY: { high: 0.3, cinematic: 0.5 }  // Increase for stronger glow
BLOOM_THRESHOLD: { high: 0.8, cinematic: 0.6 }  // Lower to bloom more elements
```

### Animated Bloom (Breathing Effect)

```tsx
// In BrainTopology or Gestalt Scene component:
useFrame(({ clock }) => {
  if (bloomRef.current) {
    bloomRef.current.intensity = 0.4 + Math.sin(clock.elapsedTime) * 0.1;
  }
});
```

### Selective Bloom (Layer-Based)

For more control, use layers to bloom only specific objects:
```tsx
// Objects that should bloom go on layer 1
mesh.layers.enable(1);

// SelectiveBloom only affects layer 1
<SelectiveBloom selection={[...bloomObjects]} />
```

---

*Last updated: 2025-12-16*
