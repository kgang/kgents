/**
 * SceneEffects - Post-processing effects for 3D scenes
 *
 * @see plans/_continuations/wave4-ssao-cinematic.md
 * @see plans/3d-visual-clarity.md
 *
 * This component adds screen-space ambient occlusion (SSAO) and other
 * post-processing effects to enhance visual depth and realism.
 *
 * SSAO adds subtle darkening where surfaces approach each other—
 * the soft shadows in crevices, the contact darkness between objects.
 * This is the difference between "good 3D" and "wow, this feels real."
 *
 * Quality-gated: Effects are only enabled on high/cinematic quality
 * to preserve performance on lower-end devices.
 *
 * Usage:
 * ```tsx
 * import { SceneEffects } from '../components/three/SceneEffects';
 *
 * function My3DScene() {
 *   const { illuminationQuality } = useSceneContext();
 *
 *   return (
 *     <Canvas shadows>
 *       <SceneLighting quality={illuminationQuality} bounds={bounds} />
 *       <SceneEffects quality={illuminationQuality} />
 *       {/* Your scene content *\/}
 *     </Canvas>
 *   );
 * }
 * ```
 */

import { useMemo } from 'react';
import { EffectComposer, SSAO } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';
import {
  type IlluminationQuality,
  SSAO_ENABLED,
  SSAO_SAMPLES,
  SSAO_RADIUS,
  SSAO_INTENSITY,
  SSAO_COLOR,
} from '../../constants/lighting';

// =============================================================================
// Types
// =============================================================================

export interface SceneEffectsProps {
  /**
   * Illumination quality level. Determines which effects are enabled.
   * @default 'standard'
   */
  quality?: IlluminationQuality;

  /**
   * Force-disable all effects (for performance testing or preference).
   * @default false
   */
  disabled?: boolean;

  /**
   * Override SSAO intensity (for fine-tuning per scene).
   * Uses quality-based default if not specified.
   */
  ssaoIntensityOverride?: number;

  /**
   * Override SSAO radius (for fine-tuning per scene).
   * Uses quality-based default if not specified.
   */
  ssaoRadiusOverride?: number;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Post-processing effects for 3D scenes.
 *
 * Currently includes:
 * - SSAO (Screen-Space Ambient Occlusion) for depth enhancement
 *
 * Future possibilities:
 * - Bloom for emissive elements
 * - Chromatic aberration for style
 * - Vignette for focus
 */
export function SceneEffects({
  quality = 'standard',
  disabled = false,
  ssaoIntensityOverride,
  ssaoRadiusOverride,
}: SceneEffectsProps) {
  // Get quality-based configuration
  const ssaoConfig = useMemo(() => {
    const enabled = SSAO_ENABLED[quality];
    const samples = SSAO_SAMPLES[quality];
    const radius = ssaoRadiusOverride ?? SSAO_RADIUS[quality];
    const intensity = ssaoIntensityOverride ?? SSAO_INTENSITY[quality];
    // Convert color string to THREE.Color for postprocessing
    const color = new THREE.Color(SSAO_COLOR);

    return { enabled, samples, radius, intensity, color };
  }, [quality, ssaoIntensityOverride, ssaoRadiusOverride]);

  // Don't render anything if disabled or no effects needed
  if (disabled || !ssaoConfig.enabled) {
    return null;
  }

  return (
    <EffectComposer>
      <SSAO
        blendFunction={BlendFunction.MULTIPLY}
        samples={ssaoConfig.samples}
        radius={ssaoConfig.radius}
        intensity={ssaoConfig.intensity}
        luminanceInfluence={0.5}
        color={ssaoConfig.color}
        // Additional tuning parameters
        distanceScaling={true}
        depthAwareUpsampling={true}
        // World-space distance parameters (reasonable defaults)
        worldDistanceThreshold={1.0}
        worldDistanceFalloff={0.1}
        worldProximityThreshold={0.3}
        worldProximityFalloff={0.3}
      />
    </EffectComposer>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SceneEffects;
