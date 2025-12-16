/**
 * Pop Animation Component
 *
 * Selection/activation feedback - a quick scale bounce.
 * Use when user selects an item or triggers an action.
 *
 * Foundation 5: Personality & Joy - Animation Primitives
 *
 * @example
 * ```tsx
 * const [selected, setSelected] = useState(false);
 *
 * <Pop trigger={selected}>
 *   <Card onClick={() => setSelected(true)} />
 * </Pop>
 * ```
 */

import { motion, type Variants } from 'framer-motion';
import type { ReactNode, CSSProperties } from 'react';
import { useState, useEffect } from 'react';
import { useMotionPreferences } from './useMotionPreferences';

export interface PopProps {
  /** Content to animate */
  children: ReactNode;
  /** Trigger the pop animation when this becomes true */
  trigger?: boolean;
  /** Peak scale during pop. Default: 1.1 */
  scale?: number;
  /** Animation duration in ms. Default: 200 */
  duration?: number;
  /** Disable animation regardless of motion preferences */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * Pop animation wrapper - quick scale bounce on trigger.
 *
 * Perfect for:
 * - Selection feedback
 * - Button press response
 * - Toast appearance
 * - Notification arrival
 */
export function Pop({
  children,
  trigger = false,
  scale = 1.1,
  duration = 200,
  disabled = false,
  className = '',
  style,
}: PopProps) {
  const { shouldAnimate } = useMotionPreferences();
  const [isPopping, setIsPopping] = useState(false);

  // Watch for trigger changes
  useEffect(() => {
    if (trigger && shouldAnimate && !disabled) {
      setIsPopping(true);
      // Reset after animation completes
      const timer = setTimeout(() => setIsPopping(false), duration);
      return () => clearTimeout(timer);
    }
  }, [trigger, shouldAnimate, disabled, duration]);

  // Skip animation if disabled or user prefers reduced motion
  if (disabled || !shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  const popVariants: Variants = {
    idle: {
      scale: 1,
    },
    pop: {
      scale: [1, scale, 1],
      transition: {
        duration: duration / 1000,
        times: [0, 0.5, 1],
        ease: [0.25, 0.46, 0.45, 0.94], // easeOutQuad
      },
    },
  };

  return (
    <motion.div
      className={className}
      style={{ display: 'inline-flex', ...style }}
      variants={popVariants}
      animate={isPopping ? 'pop' : 'idle'}
    >
      {children}
    </motion.div>
  );
}

/**
 * PopOnMount - Pops once when mounted (e.g., for toasts)
 */
export function PopOnMount({
  children,
  scale = 1.05,
  duration = 300,
  delay = 0,
  className = '',
  style,
}: Omit<PopProps, 'trigger'> & { delay?: number }) {
  const { shouldAnimate } = useMotionPreferences();

  if (!shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  // Use scale for initial transform (not final - final is always 1)
  const initialScale = 1 - (scale - 1); // If scale is 1.05, initial is 0.95

  return (
    <motion.div
      className={className}
      style={{ display: 'inline-flex', ...style }}
      initial={{ scale: initialScale, opacity: 0 }}
      animate={{
        scale: 1,
        opacity: 1,
        transition: {
          delay: delay / 1000,
          duration: duration / 1000,
          ease: [0.34, 1.56, 0.64, 1], // spring-like overshoot
        },
      }}
    >
      {children}
    </motion.div>
  );
}

export default Pop;
