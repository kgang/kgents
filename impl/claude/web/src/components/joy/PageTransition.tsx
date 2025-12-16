/**
 * Page Transition Component
 *
 * Smooth transitions between pages for React Router.
 * Uses fade + subtle scale for elegant route changes.
 *
 * Foundation 5: Personality & Joy - Motion Language
 *
 * @example
 * ```tsx
 * // In App.tsx with AnimatePresence
 * <AnimatePresence mode="wait">
 *   <Routes location={location} key={location.pathname}>
 *     <Route element={<PageTransition><Layout /></PageTransition>}>
 *       ...routes
 *     </Route>
 *   </Routes>
 * </AnimatePresence>
 * ```
 */

import { motion } from 'framer-motion';
import type { ReactNode, CSSProperties } from 'react';
import { useMotionPreferences } from './useMotionPreferences';
import { TIMING } from '../../constants';

export interface PageTransitionProps {
  /** Page content */
  children: ReactNode;
  /** Transition style variant */
  variant?: 'fade' | 'slide' | 'scale';
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

// Animation variants for different transition styles
const variants = {
  fade: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
  },
  slide: {
    initial: { opacity: 0, y: 8 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -8 },
  },
  scale: {
    initial: { opacity: 0, scale: 0.98 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.98 },
  },
};

/**
 * Page transition wrapper for smooth route changes.
 *
 * Respects user's motion preferences (reduced motion = instant).
 */
export function PageTransition({
  children,
  variant = 'fade',
  className = '',
  style,
}: PageTransitionProps) {
  const { shouldAnimate } = useMotionPreferences();

  // No animation if user prefers reduced motion
  if (!shouldAnimate) {
    return (
      <div className={className} style={style}>
        {children}
      </div>
    );
  }

  const transitionVariant = variants[variant];

  return (
    <motion.div
      className={className}
      style={style}
      initial={transitionVariant.initial}
      animate={transitionVariant.animate}
      exit={transitionVariant.exit}
      transition={{
        duration: TIMING.quick / 1000, // Convert ms to seconds
        ease: [0, 0, 0.2, 1], // enter easing
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * Pre-configured fade transition.
 */
export function PageFade({ children, ...props }: Omit<PageTransitionProps, 'variant'>) {
  return (
    <PageTransition variant="fade" {...props}>
      {children}
    </PageTransition>
  );
}

/**
 * Pre-configured slide transition.
 */
export function PageSlide({ children, ...props }: Omit<PageTransitionProps, 'variant'>) {
  return (
    <PageTransition variant="slide" {...props}>
      {children}
    </PageTransition>
  );
}

/**
 * Pre-configured scale transition.
 */
export function PageScale({ children, ...props }: Omit<PageTransitionProps, 'variant'>) {
  return (
    <PageTransition variant="scale" {...props}>
      {children}
    </PageTransition>
  );
}

export default PageTransition;
