/**
 * UmweltRipple - Spectrum shift ripple animation
 *
 * When the observer changes, a subtle ring emanates from the picker,
 * visually communicating "reality is shifting."
 *
 * Follows "The Spectrum" design from the plan:
 * - A tick perceives: butyric acid → warmth → blood
 * - A human perceives: colors, sounds, concepts
 * - Same world. Different realities.
 *
 * The ripple IS that perceptual shift made visible.
 *
 * @see plans/umwelt-visualization.md
 */

import { motion, AnimatePresence } from 'framer-motion';
import { useMotionPreferences } from '@/components/joy/useMotionPreferences';
import { UMWELT_MOTION } from './umwelt.types';

// =============================================================================
// Types
// =============================================================================

export interface UmweltRippleProps {
  /** Whether the ripple should be visible */
  isVisible: boolean;

  /** The color of the ripple (observer archetype color) */
  color: string;

  /** Optional additional className */
  className?: string;
}

// =============================================================================
// Component
// =============================================================================

/**
 * UmweltRipple
 *
 * A radial gradient ring that expands outward when observer changes.
 * Position this absolutely relative to the ObserverPicker.
 *
 * @example
 * ```tsx
 * <div className="relative">
 *   <ObserverPicker ... />
 *   <UmweltRipple isVisible={showRipple} color={observerColor} />
 * </div>
 * ```
 */
export function UmweltRipple({ isVisible, color, className = '' }: UmweltRippleProps) {
  const { shouldAnimate } = useMotionPreferences();

  // Skip animation if reduced motion preferred
  if (!shouldAnimate) {
    return null;
  }

  // Convert hex opacity to hex string (0.15 → "26")
  const opacityHex = Math.round(UMWELT_MOTION.rippleOpacity * 255)
    .toString(16)
    .padStart(2, '0');

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className={`absolute inset-0 rounded-full pointer-events-none ${className}`}
          style={{
            background: `radial-gradient(circle, ${color}${opacityHex} 0%, transparent 70%)`,
          }}
          initial={{ scale: 0.8, opacity: 0.6 }}
          animate={{ scale: UMWELT_MOTION.rippleScale, opacity: 0 }}
          exit={{ opacity: 0 }}
          transition={{
            duration: UMWELT_MOTION.quick / 1000,
            ease: UMWELT_MOTION.enter,
          }}
        />
      )}
    </AnimatePresence>
  );
}

// =============================================================================
// Accent Ripple (Smaller, for buttons)
// =============================================================================

export interface AccentRippleProps {
  /** Whether the ripple should trigger */
  trigger: boolean;

  /** The color of the ripple */
  color: string;

  /** Size of the ripple origin (matches button size) */
  size?: 'sm' | 'md' | 'lg';
}

/**
 * AccentRipple
 *
 * A smaller ripple for inline elements like aspect buttons.
 * Triggers on the `trigger` prop changing to true.
 */
export function AccentRipple({ trigger, color, size = 'md' }: AccentRippleProps) {
  const { shouldAnimate } = useMotionPreferences();

  if (!shouldAnimate || !trigger) {
    return null;
  }

  const sizeMap = {
    sm: 'w-6 h-6',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  // Subtle opacity
  const opacityHex = Math.round(UMWELT_MOTION.rippleOpacity * 255)
    .toString(16)
    .padStart(2, '0');

  return (
    <motion.div
      className={`absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full pointer-events-none ${sizeMap[size]}`}
      style={{
        background: `radial-gradient(circle, ${color}${opacityHex} 0%, transparent 60%)`,
      }}
      initial={{ scale: 0.7, opacity: 0.5 }}
      animate={{ scale: 1.8, opacity: 0 }}
      transition={{
        duration: UMWELT_MOTION.quick / 1000,
        ease: UMWELT_MOTION.enter,
      }}
    />
  );
}

export default UmweltRipple;
