/**
 * useGrowing - Organic growth animation hook
 *
 * Implements "Growing" from Crown Jewels Genesis Moodboard.
 * Provides seed → sprout → bloom → full growth transitions for entering elements.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see constants/town.ts - GROWING_ANIMATION constants
 */

import { useState, useCallback, useRef, useMemo, useEffect } from 'react';
import { GROWING_ANIMATION } from '@/constants';

// =============================================================================
// Types
// =============================================================================

export type GrowthStage = 'seed' | 'sprout' | 'bloom' | 'full';

export interface GrowingOptions {
  /**
   * Enable/disable growing animation.
   */
  enabled?: boolean;

  /**
   * Duration of growth transition in ms (default: 400)
   */
  duration?: number;

  /**
   * Custom easing function (default: spring overshoot)
   */
  easing?: string;

  /**
   * Start at full state immediately (for already-visible elements)
   */
  startFull?: boolean;

  /**
   * Respect prefers-reduced-motion media query.
   * Default: true
   */
  respectReducedMotion?: boolean;

  /**
   * Callback when growth completes
   */
  onComplete?: () => void;
}

export interface GrowingState {
  /** Current scale value (0 - 1.03 with spring overshoot) */
  scale: number;

  /** Current opacity value (0 - 1) */
  opacity: number;

  /** Current growth stage */
  stage: GrowthStage;

  /** Whether animation is currently running */
  isGrowing: boolean;

  /** Trigger growth animation from seed */
  trigger: () => void;

  /** Reset to seed state */
  reset: () => void;

  /** Immediately jump to full state */
  complete: () => void;

  /** CSS transform string */
  transform: string;

  /** CSS style object for easy application */
  style: React.CSSProperties;
}

// =============================================================================
// Stage Configuration
// =============================================================================

const STAGE_CONFIG: Record<GrowthStage, { scale: number; opacity: number; progress: number }> = {
  seed: { scale: 0, opacity: 0, progress: 0 },
  sprout: { scale: 0.5, opacity: 0.5, progress: 0.4 },
  bloom: { scale: 0.95, opacity: 0.95, progress: 0.8 },
  full: { scale: 1, opacity: 1, progress: 1 },
};

// Spring overshoot peak (3% above target at ~80% progress)
const SPRING_OVERSHOOT = 0.03;
const SPRING_PEAK_PROGRESS = 0.8;

// =============================================================================
// Hook Implementation
// =============================================================================

/**
 * useGrowing
 *
 * Returns animation state for organic growth transitions.
 *
 * @example
 * ```tsx
 * function GrowingCard({ isVisible }) {
 *   const { style, trigger } = useGrowing();
 *
 *   useEffect(() => {
 *     if (isVisible) trigger();
 *   }, [isVisible, trigger]);
 *
 *   return (
 *     <div className="card" style={style}>
 *       Content
 *     </div>
 *   );
 * }
 * ```
 *
 * @example Auto-grow on mount:
 * ```tsx
 * function NewItem() {
 *   const { style, trigger } = useGrowing();
 *
 *   useEffect(() => { trigger(); }, []);
 *
 *   return <div style={style}>New!</div>;
 * }
 * ```
 */
export function useGrowing(options: GrowingOptions = {}): GrowingState {
  const {
    enabled = true,
    duration = GROWING_ANIMATION.duration,
    easing = GROWING_ANIMATION.easing,
    startFull = false,
    respectReducedMotion = true,
    onComplete,
  } = options;

  // State
  const [scale, setScale] = useState(startFull ? 1 : 0);
  const [opacity, setOpacity] = useState(startFull ? 1 : 0);
  const [stage, setStage] = useState<GrowthStage>(startFull ? 'full' : 'seed');
  const [isGrowing, setIsGrowing] = useState(false);

  // Refs
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number>(0);
  const onCompleteRef = useRef(onComplete);

  // Keep onComplete ref updated
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  // Check for reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (!respectReducedMotion) return false;
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, [respectReducedMotion]);

  // Calculate stage from progress
  const getStageFromProgress = useCallback((progress: number): GrowthStage => {
    if (progress >= 1) return 'full';
    if (progress >= STAGE_CONFIG.bloom.progress) return 'bloom';
    if (progress >= STAGE_CONFIG.sprout.progress) return 'sprout';
    return 'seed';
  }, []);

  // Calculate scale with spring overshoot
  const calculateScale = useCallback((progress: number): number => {
    if (progress >= 1) return 1;

    // Base linear interpolation
    let targetScale = progress;

    // Add spring overshoot near peak
    if (progress >= SPRING_PEAK_PROGRESS && progress < 1) {
      // Quadratic overshoot that peaks and returns to 1
      const overshootProgress = (progress - SPRING_PEAK_PROGRESS) / (1 - SPRING_PEAK_PROGRESS);
      // Parabola: peak at 0.5 of overshoot range
      const overshootFactor = 4 * overshootProgress * (1 - overshootProgress);
      targetScale = 1 + SPRING_OVERSHOOT * overshootFactor;
    }

    return Math.max(0, Math.min(1 + SPRING_OVERSHOOT, targetScale));
  }, []);

  // Calculate opacity (linear, no overshoot)
  const calculateOpacity = useCallback((progress: number): number => {
    return Math.max(0, Math.min(1, progress));
  }, []);

  // Animation loop
  const animate = useCallback(
    (timestamp: number) => {
      if (startTimeRef.current === 0) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(1, elapsed / duration);

      setScale(calculateScale(progress));
      setOpacity(calculateOpacity(progress));
      setStage(getStageFromProgress(progress));

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        // Animation complete
        setIsGrowing(false);
        setStage('full');
        setScale(1);
        setOpacity(1);
        onCompleteRef.current?.();
      }
    },
    [duration, calculateScale, calculateOpacity, getStageFromProgress]
  );

  // Trigger growth
  const trigger = useCallback(() => {
    if (!enabled) return;

    // Cancel any existing animation
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    // Handle reduced motion
    if (prefersReducedMotion) {
      setScale(1);
      setOpacity(1);
      setStage('full');
      setIsGrowing(false);
      onCompleteRef.current?.();
      return;
    }

    // Start animation
    startTimeRef.current = 0;
    setIsGrowing(true);
    animationRef.current = requestAnimationFrame(animate);
  }, [enabled, prefersReducedMotion, animate]);

  // Reset to seed
  const reset = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    setScale(0);
    setOpacity(0);
    setStage('seed');
    setIsGrowing(false);
    startTimeRef.current = 0;
  }, []);

  // Complete immediately
  const complete = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
    setScale(1);
    setOpacity(1);
    setStage('full');
    setIsGrowing(false);
    onCompleteRef.current?.();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // Derived values
  const transform = `scale(${scale.toFixed(4)})`;
  const style: React.CSSProperties = {
    transform,
    opacity,
    transformOrigin: 'center center',
    // Use CSS transition when not actively animating (for reset smoothness)
    transition: isGrowing ? 'none' : `transform 0.15s ${easing}, opacity 0.15s ${easing}`,
  };

  return {
    scale,
    opacity,
    stage,
    isGrowing,
    trigger,
    reset,
    complete,
    transform,
    style,
  };
}

// =============================================================================
// Utility: Staggered growth for lists
// =============================================================================

/**
 * Calculate delay for staggered growth in lists.
 *
 * @param index Item index in list
 * @param baseDelay Base delay between items in ms (default: 50)
 * @param maxDelay Maximum cumulative delay in ms (default: 500)
 * @returns Delay in ms before triggering growth
 *
 * @example
 * ```tsx
 * items.map((item, i) => {
 *   const { trigger } = useGrowing();
 *   const delay = getStaggeredGrowthDelay(i);
 *
 *   useEffect(() => {
 *     const timeout = setTimeout(trigger, delay);
 *     return () => clearTimeout(timeout);
 *   }, []);
 *
 *   return <ItemCard key={item.id} />;
 * })
 * ```
 */
export function getStaggeredGrowthDelay(
  index: number,
  baseDelay: number = 50,
  maxDelay: number = 500
): number {
  // Logarithmic decay for visual rhythm (earlier items appear faster apart)
  const rawDelay = baseDelay * Math.log2(index + 2);
  return Math.min(rawDelay, maxDelay);
}

/**
 * Create a growing trigger with delay for list items.
 *
 * @param trigger The trigger function from useGrowing
 * @param delay Delay in ms before triggering
 * @returns Cleanup function
 */
export function triggerWithDelay(trigger: () => void, delay: number): () => void {
  const timeout = setTimeout(trigger, delay);
  return () => clearTimeout(timeout);
}

// =============================================================================
// CSS Keyframes Generator
// =============================================================================

/**
 * Generate CSS keyframes for growth animation.
 * Useful for pure CSS fallback or server-rendered content.
 */
export function getGrowingKeyframes(): string {
  return `
    @keyframes growing {
      0% {
        transform: scale(0);
        opacity: 0;
      }
      40% {
        transform: scale(0.5);
        opacity: 0.5;
      }
      80% {
        transform: scale(1.03);
        opacity: 0.95;
      }
      100% {
        transform: scale(1);
        opacity: 1;
      }
    }
  `;
}

/**
 * Get CSS animation property string for growing effect.
 */
export function getGrowingAnimation(duration: number = GROWING_ANIMATION.duration): string {
  return `growing ${duration}ms ${GROWING_ANIMATION.easing} forwards`;
}

// =============================================================================
// Default export
// =============================================================================

export default useGrowing;
