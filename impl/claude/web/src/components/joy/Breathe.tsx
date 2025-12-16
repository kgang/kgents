/**
 * Breathe Animation Component
 *
 * Subtle pulsing animation for healthy/living elements.
 * Conveys vitality and wellness - use for health grades, status indicators.
 *
 * Foundation 5: Personality & Joy - Animation Primitives
 *
 * @example
 * ```tsx
 * <Breathe intensity={0.5}>
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

// Duration in seconds for each speed
const SPEED_DURATION: Record<BreatheSpeed, number> = {
  slow: 4,
  normal: 3,
  fast: 2,
};

// Scale factor based on intensity
function getScaleRange(intensity: number): [number, number] {
  const clampedIntensity = Math.max(0, Math.min(1, intensity));
  const maxScale = 1 + clampedIntensity * 0.05; // Max 1.05 at full intensity
  return [1, maxScale];
}

// Opacity range based on intensity
function getOpacityRange(intensity: number): [number, number] {
  const clampedIntensity = Math.max(0, Math.min(1, intensity));
  const minOpacity = 1 - clampedIntensity * 0.15; // Min 0.85 at full intensity
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

  const breatheVariants: Variants = {
    animate: {
      scale: [minScale, maxScale, minScale],
      opacity: [maxOpacity, minOpacity, maxOpacity],
      transition: {
        duration,
        repeat: Infinity,
        ease: 'easeInOut',
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
