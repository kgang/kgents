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

  // Calculate calming breath value at given cycle position (0-1)
  // Pattern: rest → gentle rise → hold → slow release
  const getCalmingBreathValue = useCallback((cyclePosition: number): number => {
    if (cyclePosition <= 0.15) {
      // Rest phase (0-15%): stillness with tiny drift
      return (cyclePosition / 0.15) * 0.05;
    } else if (cyclePosition <= 0.4) {
      // Rise phase (15-40%): gentle curve up
      const progress = (cyclePosition - 0.15) / 0.25;
      return 0.05 + Math.sin((progress * Math.PI) / 2) * 0.95;
    } else if (cyclePosition <= 0.5) {
      // Hold phase (40-50%): stay at peak
      return 1;
    } else if (cyclePosition <= 0.95) {
      // Release phase (50-95%): slow descent
      const progress = (cyclePosition - 0.5) / 0.45;
      return Math.cos((progress * Math.PI) / 2);
    }
    // Return to rest (95-100%)
    return 0;
  }, []);

  // Calculate scale at given time
  const calculateScale = useCallback(
    (timeMs: number): number => {
      const offsetMs = phaseOffset * period;
      const adjustedTime = timeMs + offsetMs;
      const cyclePosition = (adjustedTime % period) / period;

      const breathValue = getCalmingBreathValue(cyclePosition);
      return 1 + breathValue * amplitude;
    },
    [period, amplitude, phaseOffset, getCalmingBreathValue]
  );

  // Calculate opacity (same calming curve, subtler amplitude)
  const calculateOpacity = useCallback(
    (timeMs: number): number => {
      const offsetMs = phaseOffset * period;
      const adjustedTime = timeMs + offsetMs;
      const cyclePosition = (adjustedTime % period) / period;

      const breathValue = getCalmingBreathValue(cyclePosition);
      // Opacity ranges from 0.985 to 1.0 (1.5% variation)
      return 0.985 + breathValue * 0.015;
    },
    [period, phaseOffset, getCalmingBreathValue]
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
 * Calming asymmetric pattern: rest → gentle rise → hold → slow release
 * Use with linear timing.
 */
export function getBreathingKeyframes(amplitude: number = BREATHING_ANIMATION.amplitude): string {
  // Calming breath pattern:
  // 0-15%: rest (stillness)
  // 15-40%: gentle rise (inhale)
  // 40-50%: brief hold (fullness)
  // 50-95%: slow release (exhale)
  // 95-100%: return to rest
  const keyframes = Array.from({ length: 21 }, (_, i) => {
    const pct = i * 5;
    let value: number;

    if (pct <= 15) {
      // Rest phase: stay at baseline with tiny drift
      value = (pct / 15) * 0.05; // 0 → 0.05
    } else if (pct <= 40) {
      // Rise phase: gentle curve up
      const progress = (pct - 15) / 25;
      value = 0.05 + Math.sin((progress * Math.PI) / 2) * 0.95; // 0.05 → 1
    } else if (pct <= 50) {
      // Hold phase: stay at peak
      value = 1;
    } else if (pct <= 95) {
      // Release phase: slow descent (longer than rise)
      const progress = (pct - 50) / 45;
      value = Math.cos((progress * Math.PI) / 2); // 1 → 0
    } else {
      // Return to rest
      value = 0;
    }

    const scale = 1 + value * amplitude;
    return `${pct}% { transform: scale(${scale.toFixed(4)}); }`;
  });

  return `
    @keyframes breathing {
      ${keyframes.join('\n      ')}
    }
  `;
}

// =============================================================================
// Default export
// =============================================================================

export default useBreathing;
