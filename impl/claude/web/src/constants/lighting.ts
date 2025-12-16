/**
 * Lighting Constants - Canonical 3D Illumination Parameters
 *
 * @see plans/3d-visual-clarity.md
 * @see plans/_continuations/wave5-bloom-emissive.md (COMPLETE)
 * @see docs/skills/3d-lighting-patterns.md
 *
 * Core Insight: Illumination quality is a simplifying isomorphism.
 * Just as `density` unifies device layout checks, `illuminationQuality`
 * unifies device capability checks for 3D rendering:
 *
 *   Device Capability ≅ Illumination Quality ≅ Shadow Fidelity ≅ Rendering Budget
 */

// =============================================================================
// Types
// =============================================================================

/**
 * Illumination quality levels, from low-power mobile to cinematic desktop.
 *
 * - `minimal`: No shadows, higher ambient (mobile battery saving)
 * - `standard`: Basic shadows (most devices)
 * - `high`: Detailed shadows (powerful devices)
 * - `cinematic`: Maximum quality (high-end desktop)
 */
export type IlluminationQuality = 'minimal' | 'standard' | 'high' | 'cinematic';

/**
 * Shadow frustum bounds for directional light.
 * Tighter bounds = higher shadow quality for same map size.
 */
export interface ShadowBounds {
  left: number;
  right: number;
  top: number;
  bottom: number;
  near: number;
  far: number;
}

// =============================================================================
// Quality-Parameterized Constants
// =============================================================================

/**
 * Shadow map resolution (pixels).
 * Larger = sharper shadows but more VRAM.
 */
export const SHADOW_MAP_SIZE: Record<IlluminationQuality, number> = {
  minimal: 0,      // Shadows disabled
  standard: 1024,
  high: 2048,
  cinematic: 4096,
};

/**
 * Ambient light intensity.
 * Higher ambient compensates for missing shadows on low-end devices.
 */
export const AMBIENT_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0.6,
  standard: 0.35,
  high: 0.3,
  cinematic: 0.25,
};

/**
 * Main directional light (sun/key light) intensity.
 */
export const SUN_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 1.0,
  standard: 1.2,
  high: 1.3,
  cinematic: 1.4,
};

/**
 * Fill light intensity (secondary point lights).
 */
export const FILL_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0.4,
  standard: 0.5,
  high: 0.6,
  cinematic: 0.7,
};

/**
 * Shadow bias to prevent acne/peter-panning artifacts.
 * More negative = less acne but more peter-panning.
 */
export const SHADOW_BIAS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: -0.0001,
  high: -0.00005,
  cinematic: -0.00001,
};

/**
 * Shadow normal bias for additional artifact prevention.
 */
export const SHADOW_NORMAL_BIAS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0.01,
  high: 0.005,
  cinematic: 0.002,
};

/**
 * Shadow radius (blur) for soft shadow edges.
 */
export const SHADOW_RADIUS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 2,
  high: 3,
  cinematic: 4,
};

// =============================================================================
// SSAO (Screen-Space Ambient Occlusion) Constants
// =============================================================================

/**
 * Whether SSAO is enabled for a given quality level.
 * SSAO adds subtle darkening where surfaces approach each other—
 * the soft shadows in crevices, the contact darkness between objects.
 *
 * Only enabled on high-end devices due to performance cost.
 */
export const SSAO_ENABLED: Record<IlluminationQuality, boolean> = {
  minimal: false,
  standard: false,
  high: true,      // Optional SSAO for powerful devices
  cinematic: true, // Full SSAO for high-end desktop
};

/**
 * SSAO sample count. Higher = better quality but more expensive.
 * - 16 samples: Good quality/performance tradeoff
 * - 32 samples: Maximum quality for cinematic mode
 */
export const SSAO_SAMPLES: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 16,
  cinematic: 32,
};

/**
 * SSAO sampling radius. How far to sample for occlusion.
 * Larger radius = more global occlusion but can miss fine details.
 */
export const SSAO_RADIUS: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.5,
  cinematic: 0.8,
};

/**
 * SSAO intensity. Strength of the darkening effect.
 * Should be subtle—if users notice "there's SSAO," it's too strong.
 */
export const SSAO_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 15,
  cinematic: 20,
};

/**
 * SSAO color. Should match shadow color for visual consistency.
 * Using the same soft blue-gray as shadows.
 */
export const SSAO_COLOR = '#1a1a2e';

// =============================================================================
// Bloom (Emissive Glow) Constants
// =============================================================================

/**
 * Whether bloom is enabled for a given quality level.
 * Bloom creates the cinematic glow around bright/emissive objects—
 * the soft halo that makes lights feel real.
 *
 * Moderately expensive, so only enabled on high-end devices.
 */
export const BLOOM_ENABLED: Record<IlluminationQuality, boolean> = {
  minimal: false,
  standard: false,
  high: true,       // Subtle bloom for powerful devices
  cinematic: true,  // Full bloom for high-end desktop
};

/**
 * Bloom intensity. Overall glow strength.
 * Should be subtle—bloom that's noticeable as "bloom" is too strong.
 */
export const BLOOM_INTENSITY: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.3,        // Subtle glow
  cinematic: 0.5,   // Pronounced glow
};

/**
 * Bloom luminance threshold. How bright before bloom kicks in.
 * Lower = more elements bloom, higher = only very bright elements.
 */
export const BLOOM_THRESHOLD: Record<IlluminationQuality, number> = {
  minimal: 1,
  standard: 1,
  high: 0.8,        // Only very bright areas bloom
  cinematic: 0.6,   // More generous bloom
};

/**
 * Bloom luminance smoothing. Falloff around the threshold.
 * Higher values create a softer transition between blooming and non-blooming.
 */
export const BLOOM_SMOOTHING: Record<IlluminationQuality, number> = {
  minimal: 0,
  standard: 0,
  high: 0.3,
  cinematic: 0.5,
};

// =============================================================================
// Canonical Positions & Bounds
// =============================================================================

/**
 * Default sun position - elevated, slightly behind camera.
 * This creates a natural "key light from above-right" look.
 */
export const CANONICAL_SUN_POSITION: [number, number, number] = [15, 20, 15];

/**
 * Fill light positions for atmospheric/jewel-specific mood.
 * Array of [position, color, intensityMultiplier].
 */
export const FILL_LIGHT_POSITIONS: Array<{
  position: [number, number, number];
  color: string;
  intensityMultiplier: number;
}> = [
  { position: [-10, 5, -10], color: '#4a90d9', intensityMultiplier: 0.5 },  // Cool blue fill
  { position: [0, -15, 5], color: '#22c55e', intensityMultiplier: 0.3 },    // Warm green rim
];

/**
 * Default shadow frustum bounds.
 * Sized for typical 3D graph visualizations (-15 to +15 units).
 */
export const DEFAULT_SHADOW_BOUNDS: ShadowBounds = {
  left: -20,
  right: 20,
  top: 20,
  bottom: -20,
  near: 0.5,
  far: 60,
};

// =============================================================================
// Derived Helpers
// =============================================================================

/**
 * Whether shadows are enabled for a given quality level.
 */
export function shadowsEnabled(quality: IlluminationQuality): boolean {
  return SHADOW_MAP_SIZE[quality] > 0;
}

/**
 * Whether bloom is enabled for a given quality level.
 */
export function bloomEnabled(quality: IlluminationQuality): boolean {
  return BLOOM_ENABLED[quality];
}

/**
 * Get complete lighting configuration for a quality level.
 */
export function getLightingConfig(quality: IlluminationQuality) {
  return {
    quality,
    shadowMapSize: SHADOW_MAP_SIZE[quality],
    shadowsEnabled: shadowsEnabled(quality),
    ambientIntensity: AMBIENT_INTENSITY[quality],
    sunIntensity: SUN_INTENSITY[quality],
    fillIntensity: FILL_INTENSITY[quality],
    shadowBias: SHADOW_BIAS[quality],
    shadowNormalBias: SHADOW_NORMAL_BIAS[quality],
    shadowRadius: SHADOW_RADIUS[quality],
    sunPosition: CANONICAL_SUN_POSITION,
    fillLights: FILL_LIGHT_POSITIONS,
    // SSAO parameters
    ssaoEnabled: SSAO_ENABLED[quality],
    ssaoSamples: SSAO_SAMPLES[quality],
    ssaoRadius: SSAO_RADIUS[quality],
    ssaoIntensity: SSAO_INTENSITY[quality],
    ssaoColor: SSAO_COLOR,
    // Bloom parameters
    bloomEnabled: BLOOM_ENABLED[quality],
    bloomIntensity: BLOOM_INTENSITY[quality],
    bloomThreshold: BLOOM_THRESHOLD[quality],
    bloomSmoothing: BLOOM_SMOOTHING[quality],
  };
}

/**
 * Whether SSAO is enabled for a given quality level.
 */
export function ssaoEnabled(quality: IlluminationQuality): boolean {
  return SSAO_ENABLED[quality];
}

/**
 * Quality level descriptions for UI display.
 */
export const QUALITY_DESCRIPTIONS: Record<IlluminationQuality, string> = {
  minimal: 'Battery saver - no shadows',
  standard: 'Balanced quality and performance',
  high: 'Detailed shadows + SSAO + bloom',
  cinematic: 'Maximum visual fidelity - full effects',
};
