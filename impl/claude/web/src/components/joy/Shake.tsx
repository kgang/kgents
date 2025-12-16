/**
 * Shake Animation Component
 *
 * Error/warning feedback - a horizontal shake.
 * Use when validation fails or user makes an error.
 *
 * Foundation 5: Personality & Joy - Animation Primitives
 *
 * @example
 * ```tsx
 * const [hasError, setHasError] = useState(false);
 *
 * <Shake trigger={hasError} intensity="normal">
 *   <input className={hasError ? 'border-red-500' : ''} />
 * </Shake>
 * ```
 */

import { motion, type Variants } from 'framer-motion';
import type { ReactNode, CSSProperties } from 'react';
import { useState, useEffect } from 'react';
import { useMotionPreferences } from './useMotionPreferences';

export type ShakeIntensity = 'gentle' | 'normal' | 'urgent';

export interface ShakeProps {
  /** Content to animate */
  children: ReactNode;
  /** Trigger the shake animation when this becomes true */
  trigger?: boolean;
  /** Shake intensity. Default: 'normal' */
  intensity?: ShakeIntensity;
  /** Number of shakes. Default: 3 */
  shakes?: number;
  /** Disable animation regardless of motion preferences */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

// Pixel offset for each intensity level
const INTENSITY_OFFSET: Record<ShakeIntensity, number> = {
  gentle: 4,
  normal: 8,
  urgent: 12,
};

// Duration per shake cycle (in seconds)
const SHAKE_DURATION: Record<ShakeIntensity, number> = {
  gentle: 0.08,
  normal: 0.06,
  urgent: 0.05,
};

/**
 * Shake animation wrapper - horizontal shake on trigger.
 *
 * Perfect for:
 * - Form validation errors
 * - Permission denied feedback
 * - Invalid action attempts
 * - Wrong password shake
 */
export function Shake({
  children,
  trigger = false,
  intensity = 'normal',
  shakes = 3,
  disabled = false,
  className = '',
  style,
}: ShakeProps) {
  const { shouldAnimate } = useMotionPreferences();
  const [isShaking, setIsShaking] = useState(false);

  // Watch for trigger changes (rising edge only)
  useEffect(() => {
    if (trigger && shouldAnimate && !disabled) {
      setIsShaking(true);
      const duration = SHAKE_DURATION[intensity] * shakes * 2 * 1000;
      const timer = setTimeout(() => setIsShaking(false), duration);
      return () => clearTimeout(timer);
    }
  }, [trigger, shouldAnimate, disabled, intensity, shakes]);

  // Skip animation if disabled or user prefers reduced motion
  if (disabled || !shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  const offset = INTENSITY_OFFSET[intensity];
  const duration = SHAKE_DURATION[intensity];

  // Build keyframes for shakes
  const xKeyframes: number[] = [0];
  for (let i = 0; i < shakes; i++) {
    xKeyframes.push(-offset, offset);
  }
  xKeyframes.push(0);

  const shakeVariants: Variants = {
    idle: { x: 0 },
    shake: {
      x: xKeyframes,
      transition: {
        duration: duration * xKeyframes.length,
        ease: 'linear',
      },
    },
  };

  return (
    <motion.div
      className={className}
      style={{ ...style }}
      variants={shakeVariants}
      animate={isShaking ? 'shake' : 'idle'}
    >
      {children}
    </motion.div>
  );
}

export default Shake;
