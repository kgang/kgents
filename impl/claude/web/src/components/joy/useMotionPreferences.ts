/**
 * Motion Preferences Hook
 *
 * Respects user's system preference for reduced motion.
 * All joy animations should use this to gracefully disable animations
 * for users who prefer reduced motion.
 *
 * @see https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
 */

import { useState, useEffect } from 'react';

export interface MotionPreferences {
  /** True if user prefers reduced motion */
  prefersReducedMotion: boolean;
  /** True if we should animate (inverse of prefersReducedMotion for convenience) */
  shouldAnimate: boolean;
}

/**
 * Hook to detect and respond to user's motion preferences.
 *
 * @example
 * ```tsx
 * const { shouldAnimate } = useMotionPreferences();
 *
 * return (
 *   <div style={{ animation: shouldAnimate ? 'pulse 2s infinite' : 'none' }}>
 *     Content
 *   </div>
 * );
 * ```
 */
export function useMotionPreferences(): MotionPreferences {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(() => {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') return false;

    // Get initial value
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  });

  useEffect(() => {
    // Skip if not in browser
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Update state when preference changes
    const handler = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };

    // Modern browsers
    mediaQuery.addEventListener('change', handler);

    return () => {
      mediaQuery.removeEventListener('change', handler);
    };
  }, []);

  return {
    prefersReducedMotion,
    shouldAnimate: !prefersReducedMotion,
  };
}

/**
 * Get current motion preferences without reactivity.
 * Useful for one-time checks (e.g., in celebrate()).
 */
export function getMotionPreferences(): MotionPreferences {
  if (typeof window === 'undefined') {
    return { prefersReducedMotion: false, shouldAnimate: true };
  }

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return {
    prefersReducedMotion,
    shouldAnimate: !prefersReducedMotion,
  };
}

export default useMotionPreferences;
