# Continuation: Wave 4 - SSAO for Cinematic Quality

> *"Depth is not just shadows—it's the subtle darkening where surfaces meet."*

## Context

**Previous Session Completed Waves 0-3:**
- `src/constants/lighting.ts` - Quality lookup tables
- `src/hooks/useIlluminationQuality.ts` - Device capability detection
- `src/hooks/useSceneContext.ts` - Unified scene context
- `src/components/three/SceneLighting.tsx` - Canonical lighting rig
- `src/utils/three/calculateShadowBounds.ts` - Shadow frustum calculation
- BrainTopology + Gestalt migrated to use SceneLighting

**The lighting system works.** Shadows are quality-adaptive. But for `high` and `cinematic` quality levels, we're leaving visual fidelity on the table.

---

## The Mission: SSAO for Cinematic Quality

**Screen-Space Ambient Occlusion** adds the subtle darkening where surfaces approach each other—the soft shadows in crevices, the contact darkness between objects. This is the difference between "good 3D" and "wow, this feels real."

### Why SSAO Matters for Crown Jewels

1. **BrainTopology**: Crystal clusters should feel dense where nodes cluster together
2. **Gestalt**: Module spheres near each other should show spatial relationship
3. **Future 3D Jewels**: Any graph visualization benefits from depth cues

### Quality-Gated Implementation

SSAO is expensive. Only enable for capable devices:

```typescript
// In constants/lighting.ts, add:
export const SSAO_ENABLED: Record<IlluminationQuality, boolean> = {
  minimal: false,
  standard: false,
  high: true,      // Optional SSAO
  cinematic: true, // Full SSAO
};

export const SSAO_SAMPLES: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 16,
  cinematic: 32,
};

export const SSAO_RADIUS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.5,
  cinematic: 0.8,
};
```

---

## Technical Approach

### Option A: @react-three/postprocessing (Recommended)

The `@react-three/postprocessing` library wraps pmndrs/postprocessing with React bindings:

```bash
npm install @react-three/postprocessing postprocessing
```

```tsx
import { EffectComposer, SSAO } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';

function SceneEffects({ quality }: { quality: IlluminationQuality }) {
  const ssaoEnabled = SSAO_ENABLED[quality];
  const samples = SSAO_SAMPLES[quality];
  const radius = SSAO_RADIUS[quality];

  if (!ssaoEnabled) return null;

  return (
    <EffectComposer>
      <SSAO
        blendFunction={BlendFunction.MULTIPLY}
        samples={samples}
        radius={radius}
        intensity={20}
        luminanceInfluence={0.5}
        color="#1a1a2e"  // Soft blue-gray to match shadow color
      />
    </EffectComposer>
  );
}
```

### Option B: drei's built-in effects

```tsx
import { Effects } from '@react-three/drei';
import { SSAOPass } from 'three-stdlib';

// Less recommended - SSAOPass is older algorithm
```

### Integration with SceneLighting

Create a new component or extend SceneLighting:

```tsx
// Option 1: Separate component
<Canvas shadows>
  <SceneLighting quality={quality} bounds={bounds} />
  <SceneEffects quality={quality} />
  {/* ... nodes ... */}
</Canvas>

// Option 2: SceneLighting returns effects too (via portal or fragment)
```

---

## Deliverables

### 1. Update constants/lighting.ts
Add SSAO-related quality constants.

### 2. Create components/three/SceneEffects.tsx
```typescript
interface SceneEffectsProps {
  quality: IlluminationQuality;
  /** Disable effects for performance testing */
  disabled?: boolean;
}
```

### 3. Integrate into BrainTopology and Gestalt
Add `<SceneEffects quality={illuminationQuality} />` inside Canvas.

### 4. Add quality override UI (optional but nice)
Let users manually select quality level if auto-detection is wrong:
```tsx
<select onChange={(e) => overrideQuality(e.target.value)}>
  <option value="">Auto ({autoQuality})</option>
  <option value="minimal">Minimal (no shadows)</option>
  <option value="standard">Standard</option>
  <option value="high">High (+ SSAO)</option>
  <option value="cinematic">Cinematic (full SSAO)</option>
</select>
```

---

## Success Criteria

1. **Visual**: Nodes in BrainTopology/Gestalt show subtle contact shadows where they cluster
2. **Performance**: 60 FPS maintained at `high` quality on M1 MacBook
3. **Graceful Degradation**: SSAO auto-disables on standard/minimal quality
4. **Joy Factor**: Looking at the visualization should feel "premium"

---

## Testing Checklist

- [x] SSAO visible on `high` and `cinematic` quality
- [x] SSAO disabled on `standard` and `minimal` (no performance impact)
- [x] BrainTopology clusters show depth enhancement
- [x] Gestalt module groups show spatial relationships
- [ ] No visual artifacts (halos, banding) - needs visual verification
- [x] Quality override persists to localStorage

## Implementation Status: COMPLETE (2025-12-16)

All deliverables implemented:

1. **constants/lighting.ts** - Added SSAO constants (SSAO_ENABLED, SSAO_SAMPLES, SSAO_RADIUS, SSAO_INTENSITY, SSAO_COLOR)
2. **components/three/SceneEffects.tsx** - New component with quality-gated SSAO
3. **components/three/QualitySelector.tsx** - UI for quality override
4. **BrainTopology.tsx** - Integrated SceneEffects + QualitySelector
5. **Gestalt.tsx** - Integrated SceneEffects + QualitySelector

### Dependencies Installed
- `@react-three/postprocessing@2.19.1`
- `postprocessing@6`

### SSAO Parameters
| Quality | Enabled | Samples | Radius | Intensity |
|---------|---------|---------|--------|-----------|
| minimal | false | 0 | 0 | 0 |
| standard | false | 0 | 0 | 0 |
| high | true | 16 | 0.5 | 15 |
| cinematic | true | 32 | 0.8 | 20 |

### Next Steps (Optional)
- Visual verification on actual hardware
- Fine-tune SSAO parameters based on user feedback
- Consider adding Bloom for emissive elements (future wave)

---

## Reference Files

| File | Purpose |
|------|---------|
| `src/constants/lighting.ts` | Add SSAO constants here |
| `src/components/three/SceneLighting.tsx` | Existing lighting rig |
| `src/hooks/useIlluminationQuality.ts` | Quality detection + override |
| `src/components/BrainTopology.tsx` | First integration target |
| `src/pages/Gestalt.tsx` | Second integration target |
| `plans/3d-visual-clarity.md` | Original plan |

---

## Notes on Tuning

SSAO parameters are subjective. Start conservative and increase:

- `radius`: How far to sample (0.3-1.0 typical)
- `intensity`: Strength of darkening (10-30 typical)
- `samples`: Quality/performance tradeoff (16-64)
- `color`: Should match shadow color for consistency (`#1a1a2e`)

The goal is **subtle enhancement**, not obvious darkening. If users notice "there's SSAO," it's probably too strong.

---

*"The best visual effects are the ones you don't consciously see—you just feel that something is right."*

---

## Quick Start

```bash
# Install dependencies
cd impl/claude/web
npm install @react-three/postprocessing postprocessing

# Run dev server to test
npm run dev
```

Then implement SceneEffects and integrate into BrainTopology first (smaller/simpler).
