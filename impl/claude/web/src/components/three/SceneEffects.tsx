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
import { EffectComposer, SSAO, Bloom } from '@react-three/postprocessing';
import { BlendFunction } from 'postprocessing';
import * as THREE from 'three';
import {
  type IlluminationQuality,
  SSAO_ENABLED,
  SSAO_SAMPLES,
  SSAO_RADIUS,
  SSAO_INTENSITY,
  SSAO_COLOR,
  BLOOM_ENABLED,
  BLOOM_INTENSITY,
  BLOOM_THRESHOLD,
  BLOOM_SMOOTHING,
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

  /**
   * Override bloom intensity (for fine-tuning per scene).
   * Uses quality-based default if not specified.
   */
  bloomIntensityOverride?: number;

  /**
   * Override bloom threshold (for fine-tuning per scene).
   * Uses quality-based default if not specified.
   */
  bloomThresholdOverride?: number;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * Post-processing effects for 3D scenes.
 *
 * Currently includes:
 * - SSAO (Screen-Space Ambient Occlusion) for depth enhancement
 * - Bloom for emissive glow effects
 *
 * Future possibilities:
 * - Chromatic aberration for style
 * - Vignette for focus
 */
export function SceneEffects({
  quality = 'standard',
  disabled = false,
  ssaoIntensityOverride,
  ssaoRadiusOverride,
  bloomIntensityOverride,
  bloomThresholdOverride,
}: SceneEffectsProps) {
  // Get quality-based SSAO configuration
  const ssaoConfig = useMemo(() => {
    const enabled = SSAO_ENABLED[quality];
    const samples = SSAO_SAMPLES[quality];
    const radius = ssaoRadiusOverride ?? SSAO_RADIUS[quality];
    const intensity = ssaoIntensityOverride ?? SSAO_INTENSITY[quality];
    // Convert color string to THREE.Color for postprocessing
    const color = new THREE.Color(SSAO_COLOR);

    return { enabled, samples, radius, intensity, color };
  }, [quality, ssaoIntensityOverride, ssaoRadiusOverride]);

  // Get quality-based Bloom configuration
  const bloomConfig = useMemo(() => {
    const enabled = BLOOM_ENABLED[quality];
    const intensity = bloomIntensityOverride ?? BLOOM_INTENSITY[quality];
    const threshold = bloomThresholdOverride ?? BLOOM_THRESHOLD[quality];
    const smoothing = BLOOM_SMOOTHING[quality];

    return { enabled, intensity, threshold, smoothing };
  }, [quality, bloomIntensityOverride, bloomThresholdOverride]);

  // Don't render anything if disabled or no effects needed
  const hasAnyEffect = ssaoConfig.enabled || bloomConfig.enabled;
  if (disabled || !hasAnyEffect) {
    return null;
  }

  // EffectComposer has strict typing - render based on which effects are enabled
  // Both SSAO and Bloom enabled
  if (ssaoConfig.enabled && bloomConfig.enabled) {
    return (
      <EffectComposer>
        <SSAO
          blendFunction={BlendFunction.MULTIPLY}
          samples={ssaoConfig.samples}
          radius={ssaoConfig.radius}
          intensity={ssaoConfig.intensity}
          luminanceInfluence={0.5}
          color={ssaoConfig.color}
          distanceScaling={true}
          depthAwareUpsampling={true}
          worldDistanceThreshold={1.0}
          worldDistanceFalloff={0.1}
          worldProximityThreshold={0.3}
          worldProximityFalloff={0.3}
        />
        <Bloom
          intensity={bloomConfig.intensity}
          luminanceThreshold={bloomConfig.threshold}
          luminanceSmoothing={bloomConfig.smoothing}
          mipmapBlur={true}
        />
      </EffectComposer>
    );
  }

  // Only SSAO enabled
  if (ssaoConfig.enabled) {
    return (
      <EffectComposer>
        <SSAO
          blendFunction={BlendFunction.MULTIPLY}
          samples={ssaoConfig.samples}
          radius={ssaoConfig.radius}
          intensity={ssaoConfig.intensity}
          luminanceInfluence={0.5}
          color={ssaoConfig.color}
          distanceScaling={true}
          depthAwareUpsampling={true}
          worldDistanceThreshold={1.0}
          worldDistanceFalloff={0.1}
          worldProximityThreshold={0.3}
          worldProximityFalloff={0.3}
        />
      </EffectComposer>
    );
  }

  // Only Bloom enabled
  return (
    <EffectComposer>
      <Bloom
        intensity={bloomConfig.intensity}
        luminanceThreshold={bloomConfig.threshold}
        luminanceSmoothing={bloomConfig.smoothing}
        mipmapBlur={true}
      />
    </EffectComposer>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SceneEffects;
