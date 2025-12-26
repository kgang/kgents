/**
 * Breathe Animation Component — Zero Seed Genesis Edition
 *
 * Implements Motion Law M-01: Asymmetric breathing uses 4-7-8 timing.
 * Calming breath animation for healthy/living elements that have earned motion.
 *
 * Motion Laws Applied:
 * - M-01: Asymmetric breathing (4s inhale, 7s hold, 8s exhale = 19s total)
 * - M-02: Stillness is default, animation is earned (only use on active elements)
 * - M-03: Mechanical precision for structure, organic life for content
 * - M-04: Respects prefers-reduced-motion
 * - M-05: Animation has semantic reason (shows life/health/activity)
 *
 * STARK BIOME: "Stillness, then life."
 * Only living elements should breathe. Most things stay still.
 *
 * 4-7-8 Timing Pattern (19s total cycle):
 * - 21% inhale (4 seconds): Gentle rise
 * - 37% hold (7 seconds): Moment of fullness at peak
 * - 42% exhale (8 seconds): Long, calming release
 *
 * @see plans/zero-seed-creative-strategy.md - Motion Laws
 * @see styles/breathing.css - CSS keyframes implementation
 *
 * @example
 * ```tsx
 * <Breathe intensity={0.3}>
 *   <HealthGrade grade="A+" />
 * </Breathe>
 * ```
 */

import { motion, type Variants } from 'framer-motion';
import type { ReactNode, CSSProperties } from 'react';
import { useMotionPreferences } from './useMotionPreferences';

export type BreatheSpeed = 'slow' | 'normal' | 'fast';

export interface BreatheProps {
  /** Content to animate */
  children: ReactNode;
  /** Animation intensity (0.0-1.0). Higher = more pronounced. Default: 0.3 */
  intensity?: number;
  /** Animation speed. Default: 'normal' */
  speed?: BreatheSpeed;
  /**
   * Global entropy level (0.0-1.0). When provided, modulates intensity and speed.
   * - Entropy < 0.3: slow speed, reduced intensity
   * - Entropy 0.3-0.7: normal speed, base intensity
   * - Entropy > 0.7: fast speed, amplified intensity
   *
   * Used by the Terrarium to make all creatures respond to global chaos level.
   */
  entropy?: number;
  /** Disable animation regardless of motion preferences */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * Zero Seed Genesis: 4-7-8 Breathing Durations
 * Motion Law M-01: 4s inhale + 7s hold + 8s exhale = 19s total cycle
 */
const SPEED_DURATION: Record<BreatheSpeed, number> = {
  slow: 25.3, // 33% slower than standard (19s * 1.33) — ambient, gentle
  normal: 19, // Standard 4-7-8 cycle — active elements
  fast: 14.25, // 25% faster than standard (19s * 0.75) — attention needed
};

/**
 * STARK BIOME: Subtle scale range
 * Scale is barely perceptible — organic, not mechanical
 */
function getScaleRange(intensity: number): [number, number] {
  const clampedIntensity = Math.max(0, Math.min(1, intensity));
  // Max scale 1.015 at full intensity — very subtle
  const maxScale = 1 + clampedIntensity * 0.015;
  return [1, maxScale];
}

/**
 * STARK BIOME: Opacity range based on intensity
 * - Whisper (low intensity): 0.985 ↔ 1.0 (1.5% variation)
 * - Living (high intensity): 0.94 ↔ 1.0 (6% variation)
 */
function getOpacityRange(intensity: number): [number, number] {
  const clampedIntensity = Math.max(0, Math.min(1, intensity));
  // Min 0.94 at full intensity, 0.985 at low intensity
  const minOpacity = 1 - clampedIntensity * 0.06;
  return [1, minOpacity];
}

/**
 * Breathe animation wrapper - makes children pulse gently.
 *
 * Perfect for:
 * - Health grade badges (A+, B, etc.)
 * - Status indicators showing "healthy" state
 * - Elements that should feel alive
 */
export function Breathe({
  children,
  intensity = 0.3,
  speed = 'normal',
  entropy,
  disabled = false,
  className = '',
  style,
}: BreatheProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Skip animation if disabled or user prefers reduced motion
  if (disabled || !shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  // When entropy is provided, modulate intensity and speed
  // This allows the Terrarium to control all creatures with a single slider
  let effectiveIntensity = intensity;
  let effectiveSpeed = speed;

  if (entropy !== undefined) {
    // Intensity scales with entropy: half base at 0, full at 0.5, 1.5x at 1.0
    effectiveIntensity = intensity * (0.5 + entropy);
    // Speed maps to entropy thresholds
    effectiveSpeed = entropy > 0.7 ? 'fast' : entropy > 0.3 ? 'normal' : 'slow';
  }

  const duration = SPEED_DURATION[effectiveSpeed];
  const [minScale, maxScale] = getScaleRange(effectiveIntensity);
  const [maxOpacity, minOpacity] = getOpacityRange(effectiveIntensity);

  /**
   * Motion Law M-01: 4-7-8 Asymmetric Calming Breath
   *
   * Timeline breakdown (19s total cycle):
   * - 0-21% (0-4s): Inhale — gentle rise
   * - 21-58% (4-11s): Hold — moment of fullness (7 seconds)
   * - 58-100% (11-19s): Exhale — long, calming release (8 seconds)
   *
   * This creates a natural breathing feel, not mechanical oscillation.
   */
  const breatheVariants: Variants = {
    animate: {
      // 4-7-8 timing: inhale (21%) → hold (37%) → exhale (42%)
      scale: [
        minScale,    // 0% - start
        maxScale,    // 21% - peak of inhale (4 seconds)
        maxScale,    // 58% - end of hold (11 seconds total)
        minScale,    // 100% - end of exhale (19 seconds total)
      ],
      opacity: [
        minOpacity,  // 0% - start (dim)
        maxOpacity,  // 21% - peak brightness (4 seconds)
        maxOpacity,  // 58% - end of hold brightness (11 seconds total)
        minOpacity,  // 100% - end of exhale (19 seconds total)
      ],
      transition: {
        duration,
        repeat: Infinity,
        // 4-7-8 pattern: inhale (0-21%), hold (21-58%), exhale (58-100%)
        times: [0, 0.2105, 0.5789, 1.0],
        ease: 'linear', // Easing baked into keyframe placement
      },
    },
  };

  return (
    <motion.div
      className={className}
      style={{ display: 'inline-flex', ...style }}
      variants={breatheVariants}
      animate="animate"
    >
      {children}
    </motion.div>
  );
}

export default Breathe;
