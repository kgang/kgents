/**
 * Breathe Animation Component — STARK BIOME Edition
 *
 * Calming breath animation for healthy/living elements.
 * Uses 4-7-8 asymmetric timing for organic, non-mechanical feel.
 *
 * STARK BIOME: "Stillness, then life."
 * Only living elements should breathe. Most things stay still.
 *
 * 4-7-8 Timing Pattern:
 * - 15% rest (stillness before inhale)
 * - 25% gentle rise (soft inhale)
 * - 10% brief hold (moment of fullness)
 * - 50% slow release (long, calming exhale)
 *
 * @see docs/creative/stark-biome-moodboard.md
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
  /** Disable animation regardless of motion preferences */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * STARK BIOME: Calming breath durations
 * Based on 4-7-8 breathing pattern — asymmetric, organic timing
 */
const SPEED_DURATION: Record<BreatheSpeed, number> = {
  slow: 8.1, // Full calming cycle — ambient elements
  normal: 6.75, // Standard living breath — active elements
  fast: 5.4, // Quicker but still calming — attention needed
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

  const duration = SPEED_DURATION[speed];
  const [minScale, maxScale] = getScaleRange(intensity);
  const [maxOpacity, minOpacity] = getOpacityRange(intensity);

  /**
   * STARK BIOME: 4-7-8 Asymmetric Calming Breath
   *
   * Timeline breakdown:
   * - 0-15% (0-1.01s): Rest — stillness before inhale
   * - 15-40% (1.01-2.7s): Gentle rise — soft inhale
   * - 40-50% (2.7-3.375s): Brief hold — moment of fullness
   * - 50-100% (3.375-6.75s): Slow release — long, calming exhale
   *
   * This creates a natural breathing feel, not mechanical oscillation.
   */
  const breatheVariants: Variants = {
    animate: {
      // 4-7-8 timing: rest → rise → hold → slow release
      scale: [
        minScale, // 0% - rest
        minScale, // 15% - still resting
        maxScale, // 40% - peak of inhale
        maxScale, // 50% - hold
        minScale, // 100% - end of exhale
      ],
      opacity: [
        minOpacity, // 0% - rest (dim)
        minOpacity, // 15% - still dim
        maxOpacity, // 40% - peak brightness
        maxOpacity, // 50% - hold brightness
        minOpacity, // 100% - back to dim
      ],
      transition: {
        duration,
        repeat: Infinity,
        // Custom timing to match 4-7-8 pattern
        times: [0, 0.15, 0.4, 0.5, 1.0],
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
