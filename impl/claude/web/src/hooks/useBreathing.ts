/**
 * useBreathing - Zero Seed Genesis 4-7-8 Breathing Animation Hook
 *
 * Implements Motion Law M-01: Asymmetric breathing uses 4-7-8 timing.
 * Provides organic, calming scale/opacity animations for earned motion.
 *
 * 4-7-8 Pattern (19s total):
 * - 4s inhale (21%): Gentle rise
 * - 7s hold (37%): Moment of fullness
 * - 8s exhale (42%): Long, calming release
 *
 * M-02: Default is still, animation is earned (only use when appropriate)
 * M-04: Respects prefers-reduced-motion
 *
 * @see plans/zero-seed-creative-strategy.md - Motion Laws (M-01 through M-05)
 * @see styles/breathing.css - CSS keyframes implementation
 */

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';

// =============================================================================
// Constants - 4-7-8 Breathing Timing
// =============================================================================

/**
 * BREATHING_4_7_8 - Core timing constants
 *
 * Total cycle: 19 seconds (4 + 7 + 8)
 * Amplitude: 1.5% scale variation (subtle, not mechanical)
 */
export const BREATHING_4_7_8 = {
  /** Total cycle duration in ms (4s + 7s + 8s = 19s) */
  period: 19000,

  /** Inhale duration (4s = 21% of cycle) */
  inhaleDuration: 4000,

  /** Hold duration (7s = 37% of cycle) */
  holdDuration: 7000,

  /** Exhale duration (8s = 42% of cycle) */
  exhaleDuration: 8000,

  /** Scale amplitude - subtle (1.5% variation) */
  amplitude: 0.015,

  /** Opacity amplitude - very subtle (5% variation) */
  opacityAmplitude: 0.05,
} as const;

// =============================================================================
// Types
// =============================================================================

export interface BreathingOptions {
  /**
   * Enable/disable breathing animation.
   * M-02: Default should be FALSE (stillness is default, animation is earned)
   */
  enabled?: boolean;

  /**
   * Custom period in ms (default: 19000 for 4-7-8 timing)
   */
  period?: number;

  /**
   * Custom amplitude (default: 0.015 = 1.5%)
   */
  amplitude?: number;

  /**
   * Phase offset (0-1) for staggered animation.
   * Allows multiple elements to breathe out of sync.
   */
  phaseOffset?: number;

  /**
   * Respect prefers-reduced-motion media query.
   * M-04: Default: true (always respect accessibility)
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
    period = BREATHING_4_7_8.period,
    amplitude = BREATHING_4_7_8.amplitude,
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

  // Calculate 4-7-8 breath value at given cycle position (0-1)
  // Pattern: 4s inhale (21%) → 7s hold (37%) → 8s exhale (42%)
  const get478BreathValue = useCallback((cyclePosition: number): number => {
    // Inhale phase (0-21%): 4 seconds - gentle rise
    if (cyclePosition <= 0.2105) {
      const progress = cyclePosition / 0.2105;
      // Ease-in curve for gentle start
      return Math.sin((progress * Math.PI) / 2);
    }
    // Hold phase (21-58%): 7 seconds - stay at peak
    else if (cyclePosition <= 0.5789) {
      return 1;
    }
    // Exhale phase (58-100%): 8 seconds - long, calming release
    else {
      const progress = (cyclePosition - 0.5789) / 0.4211;
      // Ease-out curve for gentle landing
      return Math.cos((progress * Math.PI) / 2);
    }
  }, []);

  // Calculate scale at given time (4-7-8 pattern)
  const calculateScale = useCallback(
    (timeMs: number): number => {
      const offsetMs = phaseOffset * period;
      const adjustedTime = timeMs + offsetMs;
      const cyclePosition = (adjustedTime % period) / period;

      const breathValue = get478BreathValue(cyclePosition);
      return 1 + breathValue * amplitude;
    },
    [period, amplitude, phaseOffset, get478BreathValue]
  );

  // Calculate opacity (same 4-7-8 curve, subtler amplitude)
  const calculateOpacity = useCallback(
    (timeMs: number): number => {
      const offsetMs = phaseOffset * period;
      const adjustedTime = timeMs + offsetMs;
      const cyclePosition = (adjustedTime % period) / period;

      const breathValue = get478BreathValue(cyclePosition);
      // Opacity ranges from 0.95 to 1.0 (5% variation)
      return 0.95 + breathValue * 0.05;
    },
    [period, phaseOffset, get478BreathValue]
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
 * Generate a CSS keyframes animation string for 4-7-8 breathing effect.
 * 4s inhale (21%) → 7s hold (37%) → 8s exhale (42%)
 * Use with linear timing function.
 */
export function getBreathingKeyframes(amplitude: number = BREATHING_4_7_8.amplitude): string {
  // 4-7-8 breath pattern:
  // 0-21%: inhale (4 seconds)
  // 21-58%: hold (7 seconds)
  // 58-100%: exhale (8 seconds)
  const keyframes = Array.from({ length: 21 }, (_, i) => {
    const pct = i * 5;
    const cyclePosition = pct / 100;
    let value: number;

    if (cyclePosition <= 0.2105) {
      // Inhale phase: gentle rise
      const progress = cyclePosition / 0.2105;
      value = Math.sin((progress * Math.PI) / 2);
    } else if (cyclePosition <= 0.5789) {
      // Hold phase: stay at peak
      value = 1;
    } else {
      // Exhale phase: long release
      const progress = (cyclePosition - 0.5789) / 0.4211;
      value = Math.cos((progress * Math.PI) / 2);
    }

    const scale = 1 + value * amplitude;
    const opacity = 0.95 + value * 0.05;
    return `${pct}% { transform: scale(${scale.toFixed(4)}); opacity: ${opacity.toFixed(3)}; }`;
  });

  return `
    @keyframes breathing-4-7-8 {
      ${keyframes.join('\n      ')}
    }
  `;
}

// =============================================================================
// Default export
// =============================================================================

export default useBreathing;
