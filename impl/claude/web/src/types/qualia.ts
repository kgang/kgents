/**
 * Qualia Space - Unified Synesthetic Design System
 *
 * Philosophy:
 *   "The barrier between colors and qualia is zero here."
 *
 * All sensory modalities project from a unified 7-dimensional qualia space.
 * The same coordinates produce consistent cross-modal experiences:
 *   - Warm qualia → amber color + slow motion + rounded shapes
 *   - Cool qualia → cyan color + crisp motion + angular shapes
 *
 * This is not mere mapping—it IS the aesthetic. The projection IS the experience.
 *
 * @see docs/creative/emergence-principles.md
 * @see impl/claude/agents/i/theme/qualia.py (Python isomorphism)
 */

// =============================================================================
// Qualia Coordinates - The 7-Dimensional Space
// =============================================================================

/**
 * 7-dimensional qualia coordinates, all in range [-1, 1].
 *
 * These coordinates represent a point in qualia space from which
 * all sensory modalities can be projected. The coordinates are
 * observer-independent; the projections are observer-dependent.
 *
 * @example
 * const coords: QualiaCoords = { warmth: 0.7, weight: -0.3, tempo: -0.5 };
 * const color = toColor(coords);  // Amber-ish
 * const motion = toMotion(coords);  // Slow, bouncy
 */
export interface QualiaCoords {
  /** cool (-1) ↔ warm (+1) */
  warmth: number;
  /** light (-1) ↔ heavy (+1) */
  weight: number;
  /** slow (-1) ↔ fast (+1) */
  tempo: number;
  /** smooth (-1) ↔ rough (+1) */
  texture: number;
  /** dark (-1) ↔ bright (+1) */
  brightness: number;
  /** muted (-1) ↔ vivid (+1) */
  saturation: number;
  /** simple (-1) ↔ complex (+1) */
  complexity: number;
}

/**
 * Default neutral qualia coordinates.
 */
export const NEUTRAL_QUALIA: QualiaCoords = {
  warmth: 0,
  weight: 0,
  tempo: 0,
  texture: 0,
  brightness: 0,
  saturation: 0,
  complexity: 0,
};

// =============================================================================
// Circadian Aesthetics
// =============================================================================

/**
 * The four phases of the circadian aesthetic cycle.
 */
export type CircadianPhase = 'dawn' | 'noon' | 'dusk' | 'midnight';

/**
 * Modifier to apply to base qualia coords.
 * Values are additive for warmth/tempo/texture, multiplicative for brightness.
 */
export interface QualiaModifier {
  warmth?: number;
  /** Multiplicative (default 1.0) */
  brightness?: number;
  tempo?: number;
  texture?: number;
}

/**
 * Circadian modifiers for each phase.
 * The UI breathes differently at different times.
 */
export const CIRCADIAN_MODIFIERS: Record<CircadianPhase, QualiaModifier> = {
  dawn: {
    warmth: -0.3, // Cooler
    brightness: 0.8, // Brightening
    tempo: 0.3, // Quickening
    texture: -0.2, // Smoother
  },
  noon: {
    warmth: 0, // Neutral
    brightness: 1.0, // Full brightness
    tempo: 0.5, // Active
    texture: 0, // Balanced
  },
  dusk: {
    warmth: 0.4, // Warming
    brightness: 0.6, // Dimming
    tempo: -0.2, // Slowing
    texture: 0.2, // Textured
  },
  midnight: {
    warmth: -0.1, // Cool
    brightness: 0.3, // Dim
    tempo: -0.5, // Slow
    texture: -0.3, // Smooth
  },
};

// =============================================================================
// Projection Outputs
// =============================================================================

/**
 * Color parameters in HSL space.
 */
export interface ColorParams {
  /** 0-360 */
  hue: number;
  /** 0-100 */
  saturation: number;
  /** 0-100 */
  lightness: number;
}

/**
 * Motion parameters derived from qualia.
 */
export interface MotionParams {
  /** Animation duration in milliseconds */
  durationMs: number;
  /** Easing function name */
  easing: 'linear' | 'ease_in' | 'ease_out' | 'ease_in_out' | 'bounce' | 'elastic';
  /** Motion amplitude (0-1) */
  amplitude: number;
  /** Optional delay in milliseconds */
  delayMs?: number;
}

/**
 * Shape parameters derived from qualia.
 */
export interface ShapeParams {
  /** 0 (angular) to 1 (rounded) */
  roundness: number;
  /** 0 (sparse) to 1 (dense) */
  density: number;
  /** 0 (simple) to 1 (fractal) */
  complexity: number;
}

// =============================================================================
// Presets
// =============================================================================

/**
 * Common qualia presets for quick usage.
 */
export const QUALIA_PRESETS = {
  warmActive: {
    warmth: 0.7,
    weight: 0,
    tempo: 0.3,
    texture: 0,
    brightness: 0.5,
    saturation: 0.6,
    complexity: 0,
  } as QualiaCoords,

  coolCalm: {
    warmth: -0.6,
    weight: 0,
    tempo: -0.4,
    texture: 0,
    brightness: 0.3,
    saturation: 0.4,
    complexity: 0,
  } as QualiaCoords,

  heavySerious: {
    warmth: 0,
    weight: 0.7,
    tempo: 0,
    texture: 0,
    brightness: -0.3,
    saturation: 0.5,
    complexity: 0.3,
  } as QualiaCoords,

  lightPlayful: {
    warmth: 0,
    weight: -0.6,
    tempo: 0.5,
    texture: 0,
    brightness: 0.4,
    saturation: 0.7,
    complexity: 0,
  } as QualiaCoords,
} as const;

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Clamp a value to [-1, 1] range.
 */
function clamp(value: number, min = -1, max = 1): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * Get circadian phase from hour (0-23).
 */
export function getCircadianPhase(hour: number): CircadianPhase {
  if (hour >= 6 && hour < 10) return 'dawn';
  if (hour >= 10 && hour < 16) return 'noon';
  if (hour >= 16 && hour < 20) return 'dusk';
  return 'midnight';
}

/**
 * Apply circadian phase modulation to base coordinates.
 */
export function applyCircadian(base: QualiaCoords, hour: number): QualiaCoords {
  const phase = getCircadianPhase(hour);
  const modifier = CIRCADIAN_MODIFIERS[phase];

  return {
    warmth: clamp(base.warmth + (modifier.warmth ?? 0)),
    weight: base.weight,
    tempo: clamp(base.tempo + (modifier.tempo ?? 0)),
    texture: clamp(base.texture + (modifier.texture ?? 0)),
    brightness: clamp(base.brightness * (modifier.brightness ?? 1)),
    saturation: base.saturation,
    complexity: base.complexity,
  };
}

/**
 * Inject accursed share (controlled chaos) into coordinates.
 *
 * The accursed share is the 10% of emergence that is chaos.
 * This is sacred—it prevents the system from becoming sterile.
 *
 * @param coords Base coordinates
 * @param budget Maximum deviation per dimension (default 0.1 = 10%)
 */
export function injectEntropy(coords: QualiaCoords, budget = 0.1): QualiaCoords {
  const noise = () => (Math.random() - 0.5) * 2 * budget;

  return {
    warmth: clamp(coords.warmth + noise()),
    weight: clamp(coords.weight + noise()),
    tempo: clamp(coords.tempo + noise()),
    texture: clamp(coords.texture + noise()),
    brightness: clamp(coords.brightness + noise()),
    saturation: clamp(coords.saturation + noise()),
    complexity: clamp(coords.complexity + noise()),
  };
}

/**
 * Linear interpolation between two qualia coordinates.
 */
export function lerpQualia(a: QualiaCoords, b: QualiaCoords, t: number): QualiaCoords {
  const lerp = (v1: number, v2: number) => v1 + (v2 - v1) * t;
  return {
    warmth: lerp(a.warmth, b.warmth),
    weight: lerp(a.weight, b.weight),
    tempo: lerp(a.tempo, b.tempo),
    texture: lerp(a.texture, b.texture),
    brightness: lerp(a.brightness, b.brightness),
    saturation: lerp(a.saturation, b.saturation),
    complexity: lerp(a.complexity, b.complexity),
  };
}

/**
 * Euclidean distance between two points in qualia space.
 */
export function qualiaDistance(a: QualiaCoords, b: QualiaCoords): number {
  return Math.sqrt(
    (a.warmth - b.warmth) ** 2 +
      (a.weight - b.weight) ** 2 +
      (a.tempo - b.tempo) ** 2 +
      (a.texture - b.texture) ** 2 +
      (a.brightness - b.brightness) ** 2 +
      (a.saturation - b.saturation) ** 2 +
      (a.complexity - b.complexity) ** 2
  );
}

// =============================================================================
// Projection Functions
// =============================================================================

/**
 * Project qualia to color parameters.
 *
 * Cross-modal mapping:
 * - warmth → hue (180=cyan → 30=amber)
 * - saturation → saturation (muted → vivid)
 * - brightness → lightness (dark → bright)
 */
export function toColor(coords: QualiaCoords): ColorParams {
  // Hue: cool (cyan=180) to warm (amber=30)
  // warmth -1 → 180, warmth +1 → 30
  let hue = 105 - coords.warmth * 75;
  if (hue < 0) hue += 360;
  if (hue > 360) hue -= 360;

  // Saturation: muted (20%) to vivid (90%)
  const saturation = 55 + coords.saturation * 35;

  // Lightness: dark (25%) to bright (75%)
  const lightness = 50 + coords.brightness * 25;

  return { hue, saturation, lightness };
}

/**
 * Project qualia to motion parameters.
 *
 * Cross-modal mapping:
 * - tempo → duration (slow=1000ms → fast=100ms)
 * - weight → easing (light=bouncy → heavy=dampened)
 * - brightness → amplitude (dim=subtle → bright=large)
 */
export function toMotion(coords: QualiaCoords): MotionParams {
  // Duration: slow (1000ms) to fast (100ms)
  const durationMs = 550 - coords.tempo * 450;

  // Easing based on weight
  let easing: MotionParams['easing'];
  if (coords.weight < -0.3) {
    easing = 'bounce';
  } else if (coords.weight < 0) {
    easing = 'ease_out';
  } else if (coords.weight < 0.3) {
    easing = 'ease_in_out';
  } else if (coords.weight < 0.6) {
    easing = 'ease_in';
  } else {
    easing = 'linear';
  }

  // Amplitude: dim (0.2) to bright (1.0)
  const amplitude = 0.6 + coords.brightness * 0.4;

  return { durationMs, easing, amplitude };
}

/**
 * Project qualia to shape parameters.
 *
 * Cross-modal mapping:
 * - warmth → roundness (cool=angular → warm=rounded)
 * - weight → density (light=sparse → heavy=dense)
 * - complexity → complexity (simple=primitive → complex=fractal)
 */
export function toShape(coords: QualiaCoords): ShapeParams {
  // Roundness: cool (0.1) to warm (0.9)
  const roundness = 0.5 + coords.warmth * 0.4;

  // Density: light (0.2) to heavy (0.9)
  const density = 0.55 + coords.weight * 0.35;

  // Complexity maps directly
  const complexity = 0.5 + coords.complexity * 0.5;

  return { roundness, density, complexity };
}

// =============================================================================
// Color Utilities
// =============================================================================

/**
 * Convert HSL to RGB.
 */
export function hslToRgb(h: number, s: number, l: number): [number, number, number] {
  const hue = h / 360;
  const sat = s / 100;
  const light = l / 100;

  if (sat === 0) {
    const gray = Math.round(light * 255);
    return [gray, gray, gray];
  }

  const hueToRgb = (p: number, q: number, t: number): number => {
    let tt = t;
    if (tt < 0) tt += 1;
    if (tt > 1) tt -= 1;
    if (tt < 1 / 6) return p + (q - p) * 6 * tt;
    if (tt < 1 / 2) return q;
    if (tt < 2 / 3) return p + (q - p) * (2 / 3 - tt) * 6;
    return p;
  };

  const q = light < 0.5 ? light * (1 + sat) : light + sat - light * sat;
  const p = 2 * light - q;

  return [
    Math.round(hueToRgb(p, q, hue + 1 / 3) * 255),
    Math.round(hueToRgb(p, q, hue) * 255),
    Math.round(hueToRgb(p, q, hue - 1 / 3) * 255),
  ];
}

/**
 * Convert ColorParams to hex string.
 */
export function colorToHex(color: ColorParams): string {
  const [r, g, b] = hslToRgb(color.hue, color.saturation, color.lightness);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Convert ColorParams to CSS hsl() string.
 */
export function colorToHsl(color: ColorParams): string {
  return `hsl(${Math.round(color.hue)}, ${Math.round(color.saturation)}%, ${Math.round(color.lightness)}%)`;
}
