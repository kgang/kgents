/**
 * useBreathing - Ghibli-inspired breathing animation hook
 *
 * Implements "Everything Breathes" from Crown Jewels Genesis Moodboard.
 * Provides organic, subtle scale animations for elements.
 *
 * @see plans/town-visualizer-renaissance.md - Phase 5: Animation
 * @see constants/town.ts - BREATHING_ANIMATION constants
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { BREATHING_ANIMATION } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export interface BreathingOptions {
  /**
   * Enable/disable breathing animation.
   * Useful for pause during interactions.
   */
  enabled?: boolean;

  /**
   * Custom period in ms (default: 3500)
   */
  period?: number;

  /**
   * Custom amplitude (default: 0.03 = 3%)
   */
  amplitude?: number;

  /**
   * Phase offset (0-1) for staggered animation.
   * Allows multiple elements to breathe out of sync.
   */
  phaseOffset?: number;

  /**
   * Respect prefers-reduced-motion media query.
   * Default: true
   */
  respectReducedMotion?: boolean;
}

export interface BreathingState {
  /** Current scale value (0.97 - 1.03) */
  scale: number;

  /** Current opacity value (0.95 - 1.0) */
  opacity: number;

  /** Whether animation is currently running */
  isBreathing: boolean;

  /** Pause the animation */
  pause: () => void;

  /** Resume the animation */
  resume: () => void;

  /** CSS transform string */
  transform: string;

  /** CSS style object for easy application */
  style: React.CSSProperties;
}

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useBreathing
 *
 * Returns continuously animating scale/opacity values for breathing effect.
 *
 * @example
 * ```tsx
 * function BreathingCircle() {
 *   const { style, isBreathing } = useBreathing();
 *
 *   return (
 *     <div
 *       className="w-8 h-8 rounded-full bg-amber-500"
 *       style={style}
 *     />
 *   );
 * }
 * ```
 *
 * @example With phase offset for staggered animation:
 * ```tsx
 * citizens.map((citizen, i) => (
 *   <CitizenNode
 *     key={citizen.id}
 *     breathing={useBreathing({ phaseOffset: i * 0.1 })}
 *   />
 * ))
 * ```
 */
export function useBreathing(options: BreathingOptions = {}): BreathingState {
  const {
    enabled = true,
    period = BREATHING_ANIMATION.period,
    amplitude = BREATHING_ANIMATION.amplitude,
    phaseOffset = 0,
    respectReducedMotion = true,
  } = options;

  // State
  const [scale, setScale] = useState(1);
  const [opacity, setOpacity] = useState(1);
  const [isPaused, setIsPaused] = useState(false);

  // Refs for animation frame
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (!respectReducedMotion) return false;
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, [respectReducedMotion]);

  // Calculate scale at given time
  const calculateScale = useCallback(
    (timeMs: number): number => {
      // Apply phase offset (0-1 maps to one full cycle)
      const offsetMs = phaseOffset * period;
      const adjustedTime = timeMs + offsetMs;

      // Cycle position (0-1)
      const cyclePosition = (adjustedTime % period) / period;

      // Sinusoidal breathing: smooth wave
      const breathFactor = Math.sin(cyclePosition * Math.PI * 2);

      // Scale between (1 - amplitude) and (1 + amplitude)
      return 1 + breathFactor * amplitude;
    },
    [period, amplitude, phaseOffset]
  );

  // Calculate opacity (slightly out of phase with scale)
  const calculateOpacity = useCallback(
    (timeMs: number): number => {
      // Opacity variation is subtler (half the amplitude)
      const offsetMs = (phaseOffset + 0.25) * period; // Quarter phase offset from scale
      const adjustedTime = timeMs + offsetMs;

      const cyclePosition = (adjustedTime % period) / period;
      const breathFactor = Math.sin(cyclePosition * Math.PI * 2);

      // Opacity ranges from 0.95 to 1.0
      return 0.975 + breathFactor * 0.025;
    },
    [period, phaseOffset]
  );

  // Animation loop
  useEffect(() => {
    // Don't animate if disabled, paused, or reduced motion preferred
    if (!enabled || isPaused || prefersReducedMotion) {
      setScale(1);
      setOpacity(1);
      return;
    }

    let lastTime = 0;

    const animate = (timestamp: number) => {
      if (startTimeRef.current === 0) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;

      // Only update if enough time has passed (throttle to ~60fps)
      if (timestamp - lastTime >= 16) {
        setScale(calculateScale(elapsed));
        setOpacity(calculateOpacity(elapsed));
        lastTime = timestamp;
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }
    };
  }, [enabled, isPaused, prefersReducedMotion, calculateScale, calculateOpacity]);

  // Pause/resume functions
  const pause = useCallback(() => setIsPaused(true), []);
  const resume = useCallback(() => setIsPaused(false), []);

  // Derived values
  const isBreathing = enabled && !isPaused && !prefersReducedMotion;
  const transform = `scale(${scale.toFixed(4)})`;
  const style: React.CSSProperties = {
    transform,
    opacity,
    transition: isBreathing ? 'none' : 'transform 0.3s ease-out, opacity 0.3s ease-out',
  };

  return {
    scale,
    opacity,
    isBreathing,
    pause,
    resume,
    transform,
    style,
  };
}

// =============================================================================
// Utility: Staggered breathing for lists
// =============================================================================

/**
 * Calculate phase offset for staggered breathing in lists.
 *
 * @param index Item index in list
 * @param total Total items (optional, for normalization)
 * @param variance How much to spread the phases (0-1)
 * @returns Phase offset for useBreathing
 *
 * @example
 * ```tsx
 * citizens.map((citizen, i) => {
 *   const { style } = useBreathing({
 *     phaseOffset: getStaggeredPhaseOffset(i, citizens.length, 0.8)
 *   });
 *   return <CitizenNode key={citizen.id} style={style} />;
 * })
 * ```
 */
export function getStaggeredPhaseOffset(
  index: number,
  total: number = 10,
  variance: number = 0.5
): number {
  // Use golden ratio for visually pleasing distribution
  const goldenRatio = 0.618033988749895;
  const normalizedIndex = index / total;

  // Spread across variance * cycle using golden ratio
  return (normalizedIndex * goldenRatio * variance) % 1;
}

// =============================================================================
// Utility: Breathing CSS class generator
// =============================================================================

/**
 * Generate a CSS keyframes animation string for breathing effect.
 * Useful for pure CSS fallback.
 */
export function getBreathingKeyframes(
  amplitude: number = BREATHING_ANIMATION.amplitude
): string {
  const min = 1 - amplitude;
  const max = 1 + amplitude;

  return `
    @keyframes breathing {
      0%, 100% { transform: scale(1); }
      25% { transform: scale(${max}); }
      50% { transform: scale(1); }
      75% { transform: scale(${min}); }
    }
  `;
}

// =============================================================================
// Default export
// =============================================================================

export default useBreathing;
